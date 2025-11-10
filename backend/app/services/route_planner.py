"""Route planning and optimization service"""
from typing import List, Optional, Dict, Tuple
from app.models.lead import Lead
from app.schemas.lead import RoutePlanResponse, RouteStop
from app.core.config import settings
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import httpx
from loguru import logger


class RoutePlannerService:
    """Service for planning optimized visit routes"""

    def __init__(self):
        self.geocoder = Nominatim(user_agent="leadgen_app")

    async def plan_route(
        self,
        leads: List[Lead],
        start_location: Optional[str] = None,
        optimize: bool = True
    ) -> RoutePlanResponse:
        """
        Plan an optimized route for visiting multiple leads
        """
        # Geocode all addresses if not already geocoded
        await self._geocode_companies(leads)

        # Get coordinates for all stops
        stops = []
        for lead in leads:
            if lead.company.latitude and lead.company.longitude:
                stops.append({
                    'lead': lead,
                    'coords': (lead.company.latitude, lead.company.longitude)
                })

        if not stops:
            return RoutePlanResponse(
                total_distance=0.0,
                estimated_duration=0,
                stops=[]
            )

        # Get start coordinates
        start_coords = None
        if start_location:
            start_coords = await self._geocode_address(start_location)

        # Optimize route order
        if optimize:
            ordered_stops = self._optimize_route(stops, start_coords)
        else:
            ordered_stops = stops

        # Calculate distances and build response
        route_stops = []
        total_distance = 0.0
        previous_coords = start_coords or ordered_stops[0]['coords']

        for idx, stop in enumerate(ordered_stops):
            lead = stop['lead']
            company = lead.company

            # Calculate distance from previous stop
            distance = geodesic(previous_coords, stop['coords']).miles
            total_distance += distance

            route_stop = RouteStop(
                lead_id=lead.id,
                company_name=company.name,
                address=f"{company.address}, {company.city}, {company.state} {company.zip_code}",
                order=idx + 1,
                distance_from_previous=round(distance, 2)
            )
            route_stops.append(route_stop)

            previous_coords = stop['coords']

        # Estimate duration (assuming 30 mph average + 30 min per stop)
        estimated_duration = int((total_distance / 30) * 60) + (len(stops) * 30)

        # Generate map URL if Google Maps API is available
        map_url = None
        if settings.GOOGLE_MAPS_API_KEY:
            map_url = self._generate_map_url(ordered_stops, start_location)

        return RoutePlanResponse(
            total_distance=round(total_distance, 2),
            estimated_duration=estimated_duration,
            stops=route_stops,
            map_url=map_url
        )

    async def _geocode_companies(self, leads: List[Lead]):
        """Geocode company addresses that don't have coordinates"""
        for lead in leads:
            company = lead.company

            # Skip if already geocoded
            if company.latitude and company.longitude:
                continue

            # Build address string
            if not company.address or not company.city:
                continue

            address = f"{company.address}, {company.city}, {company.state} {company.zip_code}"

            try:
                coords = await self._geocode_address(address)
                if coords:
                    company.latitude, company.longitude = coords
                    logger.info(f"Geocoded {company.name}: {coords}")

            except Exception as e:
                logger.error(f"Error geocoding {company.name}: {e}")

    async def _geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode an address to coordinates"""
        try:
            location = self.geocoder.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            logger.error(f"Error geocoding address {address}: {e}")

        return None

    def _optimize_route(
        self,
        stops: List[Dict],
        start_coords: Optional[Tuple[float, float]] = None
    ) -> List[Dict]:
        """
        Optimize route using nearest neighbor algorithm
        For production, consider using:
        - Google Maps Directions API with waypoint optimization
        - OSRM (Open Source Routing Machine)
        - GraphHopper
        - OR-Tools for more complex optimization
        """
        if not stops:
            return []

        # Simple nearest neighbor algorithm
        ordered = []
        remaining = stops.copy()

        # Start from specified location or first stop
        current_coords = start_coords or remaining[0]['coords']

        # If we have a start location that's not in the stops, use it
        if start_coords and start_coords != remaining[0]['coords']:
            # Find nearest to start
            nearest_idx = self._find_nearest(current_coords, remaining)
            current_stop = remaining.pop(nearest_idx)
        else:
            current_stop = remaining.pop(0)

        ordered.append(current_stop)
        current_coords = current_stop['coords']

        # Greedily select nearest remaining stop
        while remaining:
            nearest_idx = self._find_nearest(current_coords, remaining)
            current_stop = remaining.pop(nearest_idx)
            ordered.append(current_stop)
            current_coords = current_stop['coords']

        return ordered

    def _find_nearest(
        self,
        coords: Tuple[float, float],
        stops: List[Dict]
    ) -> int:
        """Find index of nearest stop to given coordinates"""
        min_distance = float('inf')
        nearest_idx = 0

        for idx, stop in enumerate(stops):
            distance = geodesic(coords, stop['coords']).miles
            if distance < min_distance:
                min_distance = distance
                nearest_idx = idx

        return nearest_idx

    def _generate_map_url(
        self,
        stops: List[Dict],
        start_location: Optional[str] = None
    ) -> str:
        """
        Generate a Google Maps URL with all waypoints
        """
        # Build waypoints string
        waypoints = []
        for stop in stops:
            company = stop['lead'].company
            waypoints.append(f"{company.city}, {company.state}")

        origin = start_location or waypoints[0]
        destination = waypoints[-1]
        waypoints_str = "|".join(waypoints[:-1])

        # Google Maps URL format
        base_url = "https://www.google.com/maps/dir/"
        url = f"{base_url}?api=1&origin={origin}&destination={destination}"

        if waypoints_str:
            url += f"&waypoints={waypoints_str}"

        return url
