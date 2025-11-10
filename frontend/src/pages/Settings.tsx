import { useEffect, useState } from 'react';
import { integrationsApi } from '../services/api';
import type { IntegrationsStatus } from '../types';
import { toast } from 'react-toastify';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

export default function Settings() {
  const [integrations, setIntegrations] = useState<IntegrationsStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const response = await integrationsApi.getStatus();
      setIntegrations(response.data);
    } catch (error) {
      toast.error('Failed to load integration status');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const testIntegration = async (name: string) => {
    try {
      await integrationsApi.testIntegration(name);
      toast.success(`${name} connection successful!`);
    } catch (error) {
      toast.error(`Failed to connect to ${name}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading settings...</div>
      </div>
    );
  }

  const integrationsList = [
    {
      name: 'OpenAI',
      key: 'openai',
      description: 'AI-powered content generation for call scripts and emails',
      docsUrl: 'https://platform.openai.com/api-keys',
    },
    {
      name: 'Indeed',
      key: 'indeed',
      description: 'Search for job postings on Indeed',
      docsUrl: 'https://www.indeed.com/publisher',
    },
    {
      name: 'ZipRecruiter',
      key: 'ziprecruiter',
      description: 'Search for job postings on ZipRecruiter',
      docsUrl: 'https://www.ziprecruiter.com/api',
    },
    {
      name: 'LinkedIn',
      key: 'linkedin',
      description: 'Enrich company data and discover contacts',
      docsUrl: 'https://www.linkedin.com/developers/',
    },
    {
      name: 'ZoomInfo',
      key: 'zoominfo',
      description: 'B2B contact and company data enrichment',
      docsUrl: 'https://www.zoominfo.com/business/api',
    },
    {
      name: 'Apollo.io',
      key: 'apollo',
      description: 'Sales intelligence and contact discovery',
      docsUrl: 'https://apolloio.github.io/apollo-api-docs/',
    },
    {
      name: 'Google Maps',
      key: 'google_maps',
      description: 'Route planning and optimization for visits',
      docsUrl: 'https://developers.google.com/maps/documentation',
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Configure your integrations and application settings
        </p>
      </div>

      {/* API Configuration Instructions */}
      <div className="card mb-6 bg-blue-50 border border-blue-200">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">
          API Configuration
        </h2>
        <p className="text-sm text-blue-800 mb-3">
          To configure API keys, edit the <code className="bg-blue-100 px-1 py-0.5 rounded">.env</code> file in your backend directory:
        </p>
        <pre className="bg-blue-900 text-blue-50 p-3 rounded text-xs overflow-x-auto">
{`# Example .env configuration
OPENAI_API_KEY=your-openai-api-key
INDEED_API_KEY=your-indeed-api-key
ZIPRECRUITER_API_KEY=your-ziprecruiter-api-key
APOLLO_API_KEY=your-apollo-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key`}
        </pre>
        <p className="text-sm text-blue-800 mt-3">
          After updating the .env file, restart the backend server for changes to take effect.
        </p>
      </div>

      {/* Integrations Status */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-6">Integration Status</h2>

        <div className="space-y-4">
          {integrationsList.map((integration) => {
            const status = integrations?.[integration.key as keyof IntegrationsStatus];
            const isConfigured = status?.configured || false;

            return (
              <div
                key={integration.key}
                className="flex items-start justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-start space-x-4">
                  <div className="mt-1">
                    {isConfigured ? (
                      <CheckCircleIcon className="w-6 h-6 text-green-500" />
                    ) : (
                      <XCircleIcon className="w-6 h-6 text-gray-400" />
                    )}
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {integration.name}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {integration.description}
                    </p>
                    <div className="mt-2 flex gap-3">
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          isConfigured
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {isConfigured ? 'Connected' : 'Not Configured'}
                      </span>
                      <a
                        href={integration.docsUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary-600 hover:underline"
                      >
                        API Documentation →
                      </a>
                    </div>
                  </div>
                </div>

                {isConfigured && (
                  <button
                    onClick={() => testIntegration(integration.key)}
                    className="btn btn-secondary text-sm"
                  >
                    Test
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Feature Overview */}
      <div className="card mt-6">
        <h2 className="text-xl font-semibold mb-4">Feature Overview</h2>

        <div className="space-y-3 text-sm">
          <div className="flex items-start">
            <CheckCircleIcon className="w-5 h-5 text-green-500 mr-3 mt-0.5" />
            <div>
              <p className="font-medium">Automatic Lead Generation</p>
              <p className="text-gray-600">Search job boards and automatically create leads</p>
            </div>
          </div>

          <div className="flex items-start">
            <CheckCircleIcon className="w-5 h-5 text-green-500 mr-3 mt-0.5" />
            <div>
              <p className="font-medium">Company Enrichment</p>
              <p className="text-gray-600">Automatically gather company data from multiple sources</p>
            </div>
          </div>

          <div className="flex items-start">
            <CheckCircleIcon className="w-5 h-5 text-green-500 mr-3 mt-0.5" />
            <div>
              <p className="font-medium">Contact Discovery</p>
              <p className="text-gray-600">Find decision-makers and key contacts at target companies</p>
            </div>
          </div>

          <div className="flex items-start">
            <CheckCircleIcon className="w-5 h-5 text-green-500 mr-3 mt-0.5" />
            <div>
              <p className="font-medium">AI Content Generation</p>
              <p className="text-gray-600">Generate personalized call scripts and emails</p>
            </div>
          </div>

          <div className="flex items-start">
            <CheckCircleIcon className="w-5 h-5 text-green-500 mr-3 mt-0.5" />
            <div>
              <p className="font-medium">Route Planning</p>
              <p className="text-gray-600">Optimize visit routes for in-person meetings</p>
            </div>
          </div>

          <div className="flex items-start">
            <CheckCircleIcon className="w-5 h-5 text-green-500 mr-3 mt-0.5" />
            <div>
              <p className="font-medium">Deduplication</p>
              <p className="text-gray-600">Automatically prevent duplicate leads and contacts</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
