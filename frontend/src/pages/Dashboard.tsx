import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { leadsApi, integrationsApi } from '../services/api';
import type { Lead, IntegrationsStatus } from '../types';
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  PhoneIcon,
  EnvelopeIcon,
  MapPinIcon,
  PencilSquareIcon,
} from '@heroicons/react/24/outline';

export default function Dashboard() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [integrations, setIntegrations] = useState<IntegrationsStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [leadsResponse, integrationsResponse] = await Promise.all([
        leadsApi.getAll({ limit: 10 }),
        integrationsApi.getStatus(),
      ]);

      setLeads(leadsResponse.data);
      setIntegrations(integrationsResponse.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      name: 'Total Leads',
      value: leads.length,
      icon: UserGroupIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'New',
      value: leads.filter((l) => l.status === 'new').length,
      icon: BuildingOfficeIcon,
      color: 'bg-green-500',
    },
    {
      name: 'In Progress',
      value: leads.filter((l) => l.status === 'in_progress').length,
      icon: PhoneIcon,
      color: 'bg-yellow-500',
    },
    {
      name: 'Contacted',
      value: leads.filter((l) => l.status === 'contacted').length,
      icon: EnvelopeIcon,
      color: 'bg-purple-500',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to LeadGen - Your automated sales lead generation tool
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stat.value}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/manual"
            className="flex items-center p-4 border-2 border-green-500 bg-green-50 rounded-lg hover:border-green-600 hover:bg-green-100 transition-colors"
          >
            <PencilSquareIcon className="h-8 w-8 text-green-600 mr-3" />
            <div>
              <h3 className="font-semibold text-gray-900">Manual Entry</h3>
              <p className="text-sm text-green-700">No API required!</p>
            </div>
          </Link>

          <Link
            to="/search"
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <MapPinIcon className="h-8 w-8 text-primary-600 mr-3" />
            <div>
              <h3 className="font-semibold text-gray-900">Search Jobs</h3>
              <p className="text-sm text-gray-600">Find new opportunities</p>
            </div>
          </Link>

          <Link
            to="/leads"
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <UserGroupIcon className="h-8 w-8 text-primary-600 mr-3" />
            <div>
              <h3 className="font-semibold text-gray-900">View Leads</h3>
              <p className="text-sm text-gray-600">Manage your pipeline</p>
            </div>
          </Link>

          <Link
            to="/companies"
            className="flex items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <BuildingOfficeIcon className="h-8 w-8 text-primary-600 mr-3" />
            <div>
              <h3 className="font-semibold text-gray-900">Companies</h3>
              <p className="text-sm text-gray-600">Browse organizations</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Leads */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Recent Leads</h2>
          <Link to="/leads" className="text-primary-600 hover:text-primary-700 font-medium">
            View All →
          </Link>
        </div>

        {leads.length === 0 ? (
          <p className="text-gray-600 text-center py-8">
            No leads yet. Start by{' '}
            <Link to="/search" className="text-primary-600 hover:underline">
              searching for jobs
            </Link>
            .
          </p>
        ) : (
          <div className="space-y-4">
            {leads.slice(0, 5).map((lead) => (
              <Link
                key={lead.id}
                to={`/leads/${lead.id}`}
                className="block p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {lead.company?.name || 'Unknown Company'}
                    </h3>
                    {lead.job_posting && (
                      <p className="text-sm text-gray-600 mt-1">
                        {lead.job_posting.title}
                      </p>
                    )}
                    {lead.contact && (
                      <p className="text-sm text-gray-500 mt-1">
                        Contact: {lead.contact.full_name}
                      </p>
                    )}
                  </div>
                  <span className={`badge badge-${lead.status}`}>
                    {lead.status.replace('_', ' ')}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Integration Status */}
      {integrations && (
        <div className="card mt-8">
          <h2 className="text-xl font-semibold mb-4">Integration Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(integrations).map(([name, status]) => (
              <div
                key={name}
                className="flex items-center p-3 bg-gray-50 rounded-lg"
              >
                <div
                  className={`w-3 h-3 rounded-full mr-3 ${
                    status.configured ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                />
                <div>
                  <p className="text-sm font-medium text-gray-900 capitalize">
                    {name.replace('_', ' ')}
                  </p>
                  <p className="text-xs text-gray-500">
                    {status.configured ? 'Connected' : 'Not configured'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
