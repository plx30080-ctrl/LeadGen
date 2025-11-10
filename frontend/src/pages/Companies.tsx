import { useEffect, useState } from 'react';
import { companiesApi } from '../services/api';
import type { Company } from '../types';
import { toast } from 'react-toastify';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

export default function Companies() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async (search?: string) => {
    try {
      setLoading(true);
      const params = search ? { search } : {};
      const response = await companiesApi.getAll(params);
      setCompanies(response.data);
    } catch (error) {
      toast.error('Failed to load companies');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadCompanies(searchQuery);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading companies...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Companies</h1>
        <p className="mt-2 text-gray-600">
          Browse and manage company information
        </p>
      </div>

      {/* Search */}
      <div className="card mb-6">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search companies..."
            className="input flex-1"
          />
          <button type="submit" className="btn btn-primary">
            <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
            Search
          </button>
        </form>
      </div>

      {/* Companies Grid */}
      {companies.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600">No companies found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((company) => (
            <div key={company.id} className="card hover:shadow-lg transition-shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {company.name}
              </h3>

              {company.industry && (
                <p className="text-sm text-gray-600 mb-2">{company.industry}</p>
              )}

              {(company.city || company.state) && (
                <p className="text-sm text-gray-500 mb-3">
                  {company.city}, {company.state}
                </p>
              )}

              {company.description && (
                <p className="text-sm text-gray-700 mb-4 line-clamp-3">
                  {company.description}
                </p>
              )}

              <div className="flex gap-2 text-sm">
                {company.website && (
                  <a
                    href={company.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:underline"
                  >
                    Website
                  </a>
                )}
                {company.linkedin_url && (
                  <a
                    href={company.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:underline"
                  >
                    LinkedIn
                  </a>
                )}
              </div>

              {company.employee_count && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    Employees: {company.employee_count.toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
