import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { leadsApi, contentApi, integrationsApi } from '../services/api';
import type { Lead, LeadActivity, ContactMethod } from '../types';
import { toast } from 'react-toastify';
import {
  PhoneIcon,
  EnvelopeIcon,
  MapPinIcon,
  SparklesIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

export default function LeadDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<Lead | null>(null);
  const [activities, setActivities] = useState<LeadActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notes, setNotes] = useState('');
  const [newActivity, setNewActivity] = useState('');

  useEffect(() => {
    if (id) {
      loadLead(parseInt(id));
    }
  }, [id]);

  const loadLead = async (leadId: number) => {
    try {
      setLoading(true);
      const [leadResponse, activitiesResponse] = await Promise.all([
        leadsApi.getOne(leadId),
        leadsApi.getActivities(leadId),
      ]);

      setLead(leadResponse.data);
      setActivities(activitiesResponse.data);
      setNotes(leadResponse.data.notes || '');
    } catch (error) {
      toast.error('Failed to load lead');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const updateLead = async (updates: Partial<Lead>) => {
    if (!lead) return;

    try {
      await leadsApi.update(lead.id, updates);
      setLead({ ...lead, ...updates });
      toast.success('Lead updated');
    } catch (error) {
      toast.error('Failed to update lead');
    }
  };

  const saveNotes = async () => {
    await updateLead({ notes });
    setEditingNotes(false);
  };

  const toggleContactMethod = async (method: ContactMethod) => {
    if (!lead) return;

    const methods = lead.selected_methods || [];
    const newMethods = methods.includes(method)
      ? methods.filter((m) => m !== method)
      : [...methods, method];

    await updateLead({ selected_methods: newMethods });
  };

  const generateCallScript = async () => {
    if (!lead) return;

    try {
      toast.info('Generating call script...');
      const response = await contentApi.generateCallScript(lead.id);
      setLead({ ...lead, call_script: response.data.call_script });
      toast.success('Call script generated!');
    } catch (error) {
      toast.error('Failed to generate call script');
    }
  };

  const generateEmail = async () => {
    if (!lead) return;

    try {
      toast.info('Generating email...');
      const response = await contentApi.generateEmail(lead.id);
      setLead({
        ...lead,
        email_subject: response.data.subject,
        email_body: response.data.body,
      });
      toast.success('Email generated!');
    } catch (error) {
      toast.error('Failed to generate email');
    }
  };

  const enrichCompany = async () => {
    if (!lead?.company) return;

    try {
      toast.info('Enriching company data...');
      await integrationsApi.enrichCompany(lead.company.id);
      toast.success('Company data enriched!');
      loadLead(lead.id);
    } catch (error) {
      toast.error('Failed to enrich company');
    }
  };

  const discoverContacts = async () => {
    if (!lead?.company) return;

    try {
      toast.info('Discovering contacts...');
      const response = await integrationsApi.discoverContacts(lead.company.id);
      toast.success(`Found ${response.data.contacts_found} contacts!`);
      loadLead(lead.id);
    } catch (error) {
      toast.error('Failed to discover contacts');
    }
  };

  const addActivity = async () => {
    if (!lead || !newActivity.trim()) return;

    try {
      await leadsApi.addActivity(lead.id, {
        lead_id: lead.id,
        activity_type: 'note',
        description: newActivity,
      });

      setNewActivity('');
      const response = await leadsApi.getActivities(lead.id);
      setActivities(response.data);
      toast.success('Activity added');
    } catch (error) {
      toast.error('Failed to add activity');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading lead...</div>
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Lead not found</p>
        <button onClick={() => navigate('/leads')} className="btn btn-primary mt-4">
          Back to Leads
        </button>
      </div>
    );
  }

  const selectedMethods = lead.selected_methods || [];

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/leads')}
          className="text-primary-600 hover:text-primary-700 mb-4"
        >
          ← Back to Leads
        </button>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {lead.company?.name || 'Unknown Company'}
            </h1>
            <p className="mt-2 text-gray-600">
              {lead.job_posting?.title || 'No job title'}
            </p>
          </div>
          <select
            value={lead.status}
            onChange={(e) => updateLead({ status: e.target.value as any })}
            className={`badge badge-${lead.status} text-base px-4 py-2 cursor-pointer`}
          >
            <option value="new">New</option>
            <option value="in_progress">In Progress</option>
            <option value="contacted">Contacted</option>
            <option value="qualified">Qualified</option>
            <option value="converted">Converted</option>
            <option value="closed_lost">Closed Lost</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Company Info */}
          <div className="card">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-semibold">Company Information</h2>
              <button onClick={enrichCompany} className="btn btn-secondary text-sm">
                <SparklesIcon className="w-4 h-4 mr-1" />
                Enrich
              </button>
            </div>
            {lead.company && (
              <div className="space-y-2">
                {lead.company.industry && (
                  <p><span className="font-medium">Industry:</span> {lead.company.industry}</p>
                )}
                {lead.company.website && (
                  <p>
                    <span className="font-medium">Website:</span>{' '}
                    <a href={lead.company.website} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                      {lead.company.website}
                    </a>
                  </p>
                )}
                {lead.company.phone && (
                  <p><span className="font-medium">Phone:</span> {lead.company.phone}</p>
                )}
                {lead.company.address && (
                  <p>
                    <span className="font-medium">Address:</span>{' '}
                    {lead.company.address}, {lead.company.city}, {lead.company.state} {lead.company.zip_code}
                  </p>
                )}
                {lead.company.description && (
                  <p className="mt-4">{lead.company.description}</p>
                )}
              </div>
            )}
          </div>

          {/* Contact Info */}
          <div className="card">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-semibold">Contact Information</h2>
              <button onClick={discoverContacts} className="btn btn-secondary text-sm">
                <SparklesIcon className="w-4 h-4 mr-1" />
                Discover
              </button>
            </div>
            {lead.contact ? (
              <div className="space-y-2">
                <p><span className="font-medium">Name:</span> {lead.contact.full_name}</p>
                {lead.contact.title && (
                  <p><span className="font-medium">Title:</span> {lead.contact.title}</p>
                )}
                {lead.contact.email && (
                  <p><span className="font-medium">Email:</span> {lead.contact.email}</p>
                )}
                {lead.contact.phone && (
                  <p><span className="font-medium">Phone:</span> {lead.contact.phone}</p>
                )}
              </div>
            ) : (
              <p className="text-gray-600">No contact information available</p>
            )}
          </div>

          {/* Job Posting */}
          {lead.job_posting && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Job Posting</h2>
              <div className="space-y-2">
                <p><span className="font-medium">Title:</span> {lead.job_posting.title}</p>
                {lead.job_posting.location && (
                  <p><span className="font-medium">Location:</span> {lead.job_posting.location}</p>
                )}
                {lead.job_posting.employment_type && (
                  <p><span className="font-medium">Type:</span> {lead.job_posting.employment_type}</p>
                )}
                {lead.job_posting.salary_range && (
                  <p><span className="font-medium">Salary:</span> {lead.job_posting.salary_range}</p>
                )}
                {lead.job_posting.description && (
                  <div className="mt-4">
                    <p className="font-medium mb-2">Description:</p>
                    <p className="text-gray-700 whitespace-pre-wrap">{lead.job_posting.description}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="card">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-semibold">Notes</h2>
              {!editingNotes ? (
                <button onClick={() => setEditingNotes(true)} className="btn btn-secondary text-sm">
                  <PencilIcon className="w-4 h-4 mr-1" />
                  Edit
                </button>
              ) : (
                <div className="flex gap-2">
                  <button onClick={saveNotes} className="btn btn-success text-sm">
                    <CheckIcon className="w-4 h-4" />
                  </button>
                  <button onClick={() => { setEditingNotes(false); setNotes(lead.notes || ''); }} className="btn btn-secondary text-sm">
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
            {editingNotes ? (
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="input min-h-32"
                placeholder="Add notes about this lead..."
              />
            ) : (
              <p className="text-gray-700 whitespace-pre-wrap">
                {lead.notes || 'No notes yet'}
              </p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Contact Methods */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Contact Methods</h2>
            <div className="space-y-3">
              <button
                onClick={() => toggleContactMethod('call')}
                className={`w-full flex items-center justify-between p-3 rounded-lg border-2 ${
                  selectedMethods.includes('call')
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-center">
                  <PhoneIcon className="w-5 h-5 mr-2" />
                  <span>Call</span>
                </div>
                {selectedMethods.includes('call') && (
                  <CheckIcon className="w-5 h-5 text-primary-600" />
                )}
              </button>

              <button
                onClick={() => toggleContactMethod('visit')}
                className={`w-full flex items-center justify-between p-3 rounded-lg border-2 ${
                  selectedMethods.includes('visit')
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-center">
                  <MapPinIcon className="w-5 h-5 mr-2" />
                  <span>Visit</span>
                </div>
                {selectedMethods.includes('visit') && (
                  <CheckIcon className="w-5 h-5 text-primary-600" />
                )}
              </button>

              <button
                onClick={() => toggleContactMethod('email')}
                className={`w-full flex items-center justify-between p-3 rounded-lg border-2 ${
                  selectedMethods.includes('email')
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-center">
                  <EnvelopeIcon className="w-5 h-5 mr-2" />
                  <span>Email</span>
                </div>
                {selectedMethods.includes('email') && (
                  <CheckIcon className="w-5 h-5 text-primary-600" />
                )}
              </button>
            </div>
          </div>

          {/* AI Actions */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">AI Actions</h2>
            <div className="space-y-2">
              <button onClick={generateCallScript} className="btn btn-primary w-full">
                <SparklesIcon className="w-4 h-4 mr-2" />
                Generate Call Script
              </button>
              <button onClick={generateEmail} className="btn btn-primary w-full">
                <SparklesIcon className="w-4 h-4 mr-2" />
                Generate Email
              </button>
            </div>

            {lead.call_script && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-900 mb-2">Call Script:</p>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{lead.call_script}</p>
              </div>
            )}

            {lead.email_subject && lead.email_body && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium text-gray-900 mb-2">Email Draft:</p>
                <p className="text-sm font-semibold text-gray-900">Subject: {lead.email_subject}</p>
                <p className="text-sm text-gray-700 mt-2 whitespace-pre-wrap">{lead.email_body}</p>
              </div>
            )}
          </div>

          {/* Activity Log */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Activity Log</h2>
            <div className="space-y-3 mb-4">
              {activities.slice(0, 5).map((activity) => (
                <div key={activity.id} className="text-sm">
                  <p className="font-medium text-gray-900">{activity.activity_type}</p>
                  {activity.description && (
                    <p className="text-gray-600">{activity.description}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(activity.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={newActivity}
                onChange={(e) => setNewActivity(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addActivity()}
                placeholder="Add activity..."
                className="input flex-1"
              />
              <button onClick={addActivity} className="btn btn-primary">
                Add
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
