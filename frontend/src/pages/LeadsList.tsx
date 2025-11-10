import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { leadsApi, contentApi, routesApi } from '../services/api';
import type { Lead } from '../types';
import { toast } from 'react-toastify';
import {
  PhoneIcon,
  EnvelopeIcon,
  MapPinIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

export default function LeadsList() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedLeads, setSelectedLeads] = useState<Set<number>>(new Set());
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
  }, [filterStatus]);

  const loadLeads = async () => {
    try {
      setLoading(true);
      const params = filterStatus !== 'all' ? { status: filterStatus } : {};
      const response = await leadsApi.getAll(params);
      setLeads(response.data);
    } catch (error) {
      toast.error('Failed to load leads');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const toggleLead = (id: number) => {
    const newSelected = new Set(selectedLeads);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedLeads(newSelected);
  };

  const selectAll = () => {
    if (selectedLeads.size === leads.length) {
      setSelectedLeads(new Set());
    } else {
      setSelectedLeads(new Set(leads.map((l) => l.id)));
    }
  };

  const generateBatchCallScripts = async () => {
    if (selectedLeads.size === 0) {
      toast.warning('Please select at least one lead');
      return;
    }

    try {
      toast.info('Generating call scripts...');
      await contentApi.generateBatchCallScripts(Array.from(selectedLeads));
      toast.success('Call scripts generated!');
      loadLeads();
    } catch (error) {
      toast.error('Failed to generate call scripts');
    }
  };

  const generateBatchEmails = async () => {
    if (selectedLeads.size === 0) {
      toast.warning('Please select at least one lead');
      return;
    }

    try {
      toast.info('Generating emails...');
      await contentApi.generateBatchEmails(Array.from(selectedLeads));
      toast.success('Emails generated!');
      loadLeads();
    } catch (error) {
      toast.error('Failed to generate emails');
    }
  };

  const planRoute = async () => {
    if (selectedLeads.size === 0) {
      toast.warning('Please select at least one lead');
      return;
    }

    try {
      toast.info('Planning route...');
      const response = await routesApi.planRoute(Array.from(selectedLeads));
      toast.success(`Route planned: ${response.data.total_distance} miles, ${response.data.estimated_duration} minutes`);

      if (response.data.map_url) {
        window.open(response.data.map_url, '_blank');
      }
    } catch (error) {
      toast.error('Failed to plan route');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading leads...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Leads</h1>
          <p className="mt-2 text-gray-600">
            Manage your sales pipeline and contact prospects
          </p>
        </div>
        <Link to="/search" className="btn btn-primary">
          + Search Jobs
        </Link>
      </div>

      {/* Filters and Bulk Actions */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input w-48"
            >
              <option value="all">All Status</option>
              <option value="new">New</option>
              <option value="in_progress">In Progress</option>
              <option value="contacted">Contacted</option>
              <option value="qualified">Qualified</option>
              <option value="converted">Converted</option>
              <option value="closed_lost">Closed Lost</option>
            </select>
          </div>

          {selectedLeads.size > 0 && (
            <div className="flex gap-2">
              <button
                onClick={generateBatchCallScripts}
                className="btn btn-secondary flex items-center"
              >
                <PhoneIcon className="w-4 h-4 mr-2" />
                Generate Scripts ({selectedLeads.size})
              </button>
              <button
                onClick={generateBatchEmails}
                className="btn btn-secondary flex items-center"
              >
                <EnvelopeIcon className="w-4 h-4 mr-2" />
                Generate Emails ({selectedLeads.size})
              </button>
              <button
                onClick={planRoute}
                className="btn btn-secondary flex items-center"
              >
                <MapPinIcon className="w-4 h-4 mr-2" />
                Plan Route ({selectedLeads.size})
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Leads List */}
      <div className="card">
        {leads.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">No leads found.</p>
            <Link to="/search" className="btn btn-primary">
              Start Searching for Jobs
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedLeads.size === leads.length}
                      onChange={selectAll}
                      className="rounded"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Job Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedLeads.has(lead.id)}
                        onChange={() => toggleLead(lead.id)}
                        className="rounded"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-medium text-gray-900">
                          {lead.company?.name || 'Unknown'}
                        </div>
                        {lead.company?.city && lead.company?.state && (
                          <div className="text-sm text-gray-500">
                            {lead.company.city}, {lead.company.state}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {lead.contact ? (
                        <div>
                          <div className="text-sm text-gray-900">
                            {lead.contact.full_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {lead.contact.title || lead.contact.email}
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">No contact</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {lead.job_posting ? (
                        <div className="text-sm text-gray-900">
                          {lead.job_posting.title}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">No job</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`badge badge-${lead.status}`}>
                        {lead.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <Link
                        to={`/leads/${lead.id}`}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        View Details →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
