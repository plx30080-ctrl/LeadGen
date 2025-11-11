import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import {
  PlusCircleIcon,
  DocumentArrowUpIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ManualEntry() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'single' | 'csv'>('single');

  // Single entry form
  const [companyName, setCompanyName] = useState('');
  const [companyWebsite, setCompanyWebsite] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [location, setLocation] = useState('');
  const [contactName, setContactName] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [notes, setNotes] = useState('');

  // Email suggestions
  const [emailSuggestions, setEmailSuggestions] = useState<string[]>([]);

  // CSV upload
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!companyName || !jobTitle) {
      toast.error('Company name and job title are required');
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/api/import/job/manual`, null, {
        params: {
          company_name: companyName,
          company_website: companyWebsite,
          job_title: jobTitle,
          job_description: jobDescription,
          location: location,
          contact_name: contactName,
          contact_email: contactEmail,
          contact_phone: contactPhone,
          notes: notes,
        },
      });

      toast.success('Lead created successfully!');

      // Reset form
      setCompanyName('');
      setCompanyWebsite('');
      setJobTitle('');
      setJobDescription('');
      setLocation('');
      setContactName('');
      setContactEmail('');
      setContactPhone('');
      setNotes('');

      // Navigate to the new lead
      setTimeout(() => navigate(`/leads/${response.data.lead_id}`), 1000);
    } catch (error) {
      toast.error('Failed to create lead');
      console.error(error);
    }
  };

  const suggestEmails = async () => {
    if (!contactName || !companyWebsite) {
      toast.warning('Enter contact name and company website first');
      return;
    }

    const names = contactName.split(' ');
    if (names.length < 2) {
      toast.warning('Please enter full name (First Last)');
      return;
    }

    try {
      const domain = companyWebsite.replace('http://', '').replace('https://', '').split('/')[0];
      const firstName = names[0];
      const lastName = names[names.length - 1];

      const response = await axios.post(`${API_URL}/api/import/contact/suggest-emails`, null, {
        params: {
          company_id: 0, // We'll generate based on domain
          first_name: firstName,
          last_name: lastName,
        },
      });

      // Generate patterns locally
      const patterns = [
        `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${domain}`,
        `${firstName.toLowerCase()}${lastName.toLowerCase()}@${domain}`,
        `${firstName[0].toLowerCase()}${lastName.toLowerCase()}@${domain}`,
        `${firstName.toLowerCase()}@${domain}`,
        `${firstName.toLowerCase()}${lastName[0].toLowerCase()}@${domain}`,
        `${firstName[0].toLowerCase()}.${lastName.toLowerCase()}@${domain}`,
      ];

      setEmailSuggestions(patterns);
    } catch (error) {
      console.error(error);
    }
  };

  const handleCsvUpload = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!csvFile) {
      toast.error('Please select a CSV file');
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', csvFile);

      const response = await axios.post(`${API_URL}/api/import/jobs/csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success(`${response.data.leads_created} leads created!`);

      if (response.data.errors.length > 0) {
        console.warn('Errors:', response.data.errors);
        toast.warning(`${response.data.errors.length} rows had errors (check console)`);
      }

      setCsvFile(null);
      setTimeout(() => navigate('/leads'), 1500);
    } catch (error) {
      toast.error('Failed to upload CSV');
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const downloadCsvTemplate = () => {
    const csv = `company_name,company_website,job_title,job_description,location,contact_name,contact_email,contact_phone
TechCorp Inc,https://techcorp.com,Sales Manager,Looking for experienced sales manager...,San Francisco CA,John Smith,john.smith@techcorp.com,555-1234
`;

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'leadgen_template.csv';
    a.click();
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Manual Lead Entry</h1>
        <p className="mt-2 text-gray-600">
          Add leads manually without requiring API integrations
        </p>
      </div>

      {/* Info Banner */}
      <div className="card mb-6 bg-green-50 border border-green-200">
        <div className="flex items-start">
          <SparklesIcon className="w-6 h-6 text-green-600 mr-3 mt-1" />
          <div>
            <h3 className="font-semibold text-green-900 mb-2">No API Keys Required!</h3>
            <p className="text-sm text-green-800 mb-2">
              This method lets you manually enter job opportunities and companies you've found.
              Perfect for when you don't have access to job board APIs.
            </p>
            <ul className="text-sm text-green-700 list-disc list-inside space-y-1">
              <li>Browse job boards manually and copy/paste information</li>
              <li>Import multiple leads at once via CSV</li>
              <li>Free company enrichment using public data</li>
              <li>Email pattern suggestions for contacts</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card mb-6">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('single')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'single'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <PlusCircleIcon className="w-5 h-5 inline mr-2" />
            Single Entry
          </button>
          <button
            onClick={() => setActiveTab('csv')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'csv'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <DocumentArrowUpIcon className="w-5 h-5 inline mr-2" />
            CSV Upload
          </button>
        </div>

        {/* Single Entry Form */}
        {activeTab === 'single' && (
          <form onSubmit={handleSubmit} className="mt-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Company Info */}
              <div className="md:col-span-2">
                <h3 className="text-lg font-semibold mb-4">Company Information</h3>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  required
                  className="input"
                  placeholder="e.g., TechCorp Inc"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Website
                </label>
                <input
                  type="url"
                  value={companyWebsite}
                  onChange={(e) => setCompanyWebsite(e.target.value)}
                  className="input"
                  placeholder="https://example.com"
                />
              </div>

              {/* Job Info */}
              <div className="md:col-span-2 pt-4">
                <h3 className="text-lg font-semibold mb-4">Job Opening</h3>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Title *
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  required
                  className="input"
                  placeholder="e.g., Sales Manager"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="input"
                  placeholder="e.g., San Francisco, CA"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="input min-h-32"
                  placeholder="Paste the job description here..."
                />
              </div>

              {/* Contact Info */}
              <div className="md:col-span-2 pt-4">
                <h3 className="text-lg font-semibold mb-4">Contact Information (Optional)</h3>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Name
                </label>
                <input
                  type="text"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  className="input"
                  placeholder="First Last"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Phone
                </label>
                <input
                  type="tel"
                  value={contactPhone}
                  onChange={(e) => setContactPhone(e.target.value)}
                  className="input"
                  placeholder="(555) 123-4567"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Email
                </label>
                <div className="flex gap-2">
                  <input
                    type="email"
                    value={contactEmail}
                    onChange={(e) => setContactEmail(e.target.value)}
                    className="input flex-1"
                    placeholder="contact@example.com"
                  />
                  <button
                    type="button"
                    onClick={suggestEmails}
                    className="btn btn-secondary whitespace-nowrap"
                  >
                    Suggest Emails
                  </button>
                </div>

                {emailSuggestions.length > 0 && (
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs font-medium text-gray-700 mb-2">
                      Common email patterns (verify before use):
                    </p>
                    <div className="space-y-1">
                      {emailSuggestions.map((email, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setContactEmail(email)}
                          className="block text-sm text-primary-600 hover:underline"
                        >
                          {email}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Notes */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="input min-h-24"
                  placeholder="Any additional notes about this lead..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button type="button" onClick={() => navigate('/leads')} className="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                <PlusCircleIcon className="w-5 h-5 mr-2" />
                Create Lead
              </button>
            </div>
          </form>
        )}

        {/* CSV Upload */}
        {activeTab === 'csv' && (
          <div className="mt-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">CSV Format</h3>
              <p className="text-sm text-gray-600 mb-4">
                Upload a CSV file with the following columns:
              </p>
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <code className="text-sm">
                  company_name, company_website, job_title, job_description, location, contact_name, contact_email, contact_phone
                </code>
              </div>
              <button onClick={downloadCsvTemplate} className="btn btn-secondary text-sm">
                Download Template CSV
              </button>
            </div>

            <form onSubmit={handleCsvUpload}>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select CSV File
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-lg file:border-0
                    file:text-sm file:font-semibold
                    file:bg-primary-50 file:text-primary-700
                    hover:file:bg-primary-100"
                />
              </div>

              {csvFile && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm font-medium text-blue-900">
                    Selected: {csvFile.name}
                  </p>
                  <p className="text-xs text-blue-700 mt-1">
                    Size: {(csvFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              )}

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setCsvFile(null);
                    navigate('/leads');
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!csvFile || uploading}
                  className="btn btn-primary"
                >
                  <DocumentArrowUpIcon className="w-5 h-5 mr-2" />
                  {uploading ? 'Uploading...' : 'Upload CSV'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Usage Tips */}
      <div className="card bg-blue-50 border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-3">💡 Tips for Finding Leads</h3>
        <ul className="text-sm text-blue-800 space-y-2">
          <li>• Browse Indeed, LinkedIn, or ZipRecruiter manually and copy job details</li>
          <li>• Look for "Contact" or "About" pages on company websites for emails</li>
          <li>• Search LinkedIn for employees with titles like "VP Sales" or "Director"</li>
          <li>• Use the email suggestion feature to guess common patterns</li>
          <li>• Verify contact information before reaching out</li>
          <li>• You can always enrich company data later using the free enrichment button</li>
        </ul>
      </div>
    </div>
  );
}
