// TypeScript type definitions

export interface Company {
  id: number;
  name: string;
  domain?: string;
  industry?: string;
  size?: string;
  description?: string;
  website?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country: string;
  latitude?: number;
  longitude?: number;
  linkedin_url?: string;
  employee_count?: number;
  annual_revenue?: string;
  created_at: string;
  updated_at?: string;
}

export interface Contact {
  id: number;
  company_id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  title?: string;
  department?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  source?: string;
  confidence_score?: number;
  created_at: string;
}

export interface JobPosting {
  id: number;
  company_id: number;
  title: string;
  description?: string;
  requirements?: string;
  salary_range?: string;
  employment_type?: string;
  location?: string;
  city?: string;
  state?: string;
  is_remote: boolean;
  source: string;
  external_id: string;
  external_url?: string;
  posted_date?: string;
  created_at: string;
}

export type LeadStatus = 'new' | 'in_progress' | 'contacted' | 'qualified' | 'converted' | 'closed_lost';
export type ContactMethod = 'call' | 'visit' | 'email';

export interface Lead {
  id: number;
  company_id: number;
  contact_id?: number;
  job_posting_id?: number;
  status: LeadStatus;
  score?: number;
  selected_methods?: ContactMethod[];
  call_script?: string;
  email_subject?: string;
  email_body?: string;
  notes?: string;
  tags?: string[];
  created_at: string;
  updated_at?: string;
  company?: Company;
  contact?: Contact;
  job_posting?: JobPosting;
}

export interface LeadActivity {
  id: number;
  lead_id: number;
  activity_type: string;
  description?: string;
  created_at: string;
}

export interface SearchCriteria {
  id?: number;
  name: string;
  keywords?: string[];
  job_titles?: string[];
  industries?: string[];
  zip_code?: string;
  radius_miles?: number;
  cities?: string[];
  states?: string[];
  employment_type?: string[];
  experience_level?: string[];
  posted_within_days?: number;
  search_indeed: boolean;
  search_ziprecruiter: boolean;
}

export interface RouteStop {
  lead_id: number;
  company_name: string;
  address: string;
  order: number;
  estimated_arrival?: string;
  distance_from_previous?: number;
}

export interface RoutePlan {
  total_distance: number;
  estimated_duration: number;
  stops: RouteStop[];
  map_url?: string;
}

export interface IntegrationStatus {
  enabled: boolean;
  configured: boolean;
}

export interface IntegrationsStatus {
  openai: IntegrationStatus;
  indeed: IntegrationStatus;
  ziprecruiter: IntegrationStatus;
  linkedin: IntegrationStatus;
  zoominfo: IntegrationStatus;
  apollo: IntegrationStatus;
  google_maps: IntegrationStatus;
}
