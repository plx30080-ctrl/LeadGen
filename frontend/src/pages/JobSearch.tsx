import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchApi } from '../services/api';
import type { SearchCriteria } from '../types';
import { toast } from 'react-toastify';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

export default function JobSearch() {
  const navigate = useNavigate();
  const [savedSearches, setSavedSearches] = useState<SearchCriteria[]>([]);
  const [searchName, setSearchName] = useState('');
  const [keywords, setKeywords] = useState('');
  const [jobTitles, setJobTitles] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [radiusMiles, setRadiusMiles] = useState(25);
  const [cities, setCities] = useState('');
  const [states, setStates] = useState('');
  const [postedWithinDays, setPostedWithinDays] = useState(30);
  const [searchIndeed, setSearchIndeed] = useState(true);
  const [searchZipRecruiter, setSearchZipRecruiter] = useState(true);

  useEffect(() => {
    loadSavedSearches();
  }, []);

  const loadSavedSearches = async () => {
    try {
      const response = await searchApi.getCriteria();
      setSavedSearches(response.data);
    } catch (error) {
      console.error('Failed to load saved searches:', error);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    const searchData = {
      keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
      job_titles: jobTitles.split(',').map(t => t.trim()).filter(t => t),
      zip_code: zipCode || undefined,
      radius_miles: radiusMiles,
      cities: cities.split(',').map(c => c.trim()).filter(c => c),
      states: states.split(',').map(s => s.trim()).filter(s => s),
      posted_within_days: postedWithinDays,
      search_indeed: searchIndeed,
      search_ziprecruiter: searchZipRecruiter,
    };

    try {
      toast.info('Searching for jobs...');
      const response = await searchApi.searchJobs(searchData);
      toast.success('Job search started! Check back in a few moments.');
      setTimeout(() => navigate('/leads'), 2000);
    } catch (error) {
      toast.error('Failed to start job search');
      console.error(error);
    }
  };

  const saveSearch = async () => {
    if (!searchName.trim()) {
      toast.warning('Please enter a name for this search');
      return;
    }

    const criteria: SearchCriteria = {
      name: searchName,
      keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
      job_titles: jobTitles.split(',').map(t => t.trim()).filter(t => t),
      zip_code: zipCode || undefined,
      radius_miles: radiusMiles,
      cities: cities.split(',').map(c => c.trim()).filter(c => c),
      states: states.split(',').map(s => s.trim()).filter(s => s),
      posted_within_days: postedWithinDays,
      search_indeed: searchIndeed,
      search_ziprecruiter: searchZipRecruiter,
    };

    try {
      await searchApi.saveCriteria(criteria);
      toast.success('Search criteria saved!');
      loadSavedSearches();
      setSearchName('');
    } catch (error) {
      toast.error('Failed to save search criteria');
    }
  };

  const runSavedSearch = async (id: number) => {
    try {
      toast.info('Running saved search...');
      await searchApi.runSavedSearch(id);
      toast.success('Job search started!');
      setTimeout(() => navigate('/leads'), 2000);
    } catch (error) {
      toast.error('Failed to run search');
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Job Search</h1>
        <p className="mt-2 text-gray-600">
          Search Indeed and ZipRecruiter for relevant job openings
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSearch} className="card space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Keywords
              </label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="e.g., sales, marketing, healthcare (comma-separated)"
                className="input"
              />
              <p className="mt-1 text-sm text-gray-500">
                Separate multiple keywords with commas
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Titles
              </label>
              <input
                type="text"
                value={jobTitles}
                onChange={(e) => setJobTitles(e.target.value)}
                placeholder="e.g., Sales Manager, Business Development (comma-separated)"
                className="input"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Zip Code
                </label>
                <input
                  type="text"
                  value={zipCode}
                  onChange={(e) => setZipCode(e.target.value)}
                  placeholder="e.g., 94102"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Radius (miles)
                </label>
                <input
                  type="number"
                  value={radiusMiles}
                  onChange={(e) => setRadiusMiles(parseInt(e.target.value))}
                  min="0"
                  max="100"
                  className="input"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cities
                </label>
                <input
                  type="text"
                  value={cities}
                  onChange={(e) => setCities(e.target.value)}
                  placeholder="e.g., San Francisco, Los Angeles"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  States
                </label>
                <input
                  type="text"
                  value={states}
                  onChange={(e) => setStates(e.target.value)}
                  placeholder="e.g., CA, NY, TX"
                  className="input"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Posted Within (days)
              </label>
              <select
                value={postedWithinDays}
                onChange={(e) => setPostedWithinDays(parseInt(e.target.value))}
                className="input"
              >
                <option value={1}>Last 24 hours</option>
                <option value={7}>Last week</option>
                <option value={14}>Last 2 weeks</option>
                <option value={30}>Last 30 days</option>
                <option value={60}>Last 60 days</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Boards
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={searchIndeed}
                    onChange={(e) => setSearchIndeed(e.target.checked)}
                    className="rounded mr-2"
                  />
                  <span>Indeed</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={searchZipRecruiter}
                    onChange={(e) => setSearchZipRecruiter(e.target.checked)}
                    className="rounded mr-2"
                  />
                  <span>ZipRecruiter</span>
                </label>
              </div>
            </div>

            <div className="flex gap-3">
              <button type="submit" className="btn btn-primary flex-1">
                <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
                Search Jobs
              </button>
            </div>
          </form>

          {/* Save Search */}
          <div className="card mt-6">
            <h3 className="text-lg font-semibold mb-4">Save This Search</h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                placeholder="Search name (e.g., Bay Area Sales)"
                className="input flex-1"
              />
              <button onClick={saveSearch} className="btn btn-secondary">
                Save
              </button>
            </div>
          </div>
        </div>

        {/* Saved Searches */}
        <div className="card h-fit">
          <h2 className="text-xl font-semibold mb-4">Saved Searches</h2>

          {savedSearches.length === 0 ? (
            <p className="text-gray-600 text-sm">No saved searches yet</p>
          ) : (
            <div className="space-y-3">
              {savedSearches.map((search) => (
                <div
                  key={search.id}
                  className="p-3 border border-gray-200 rounded-lg hover:border-primary-500 transition-colors"
                >
                  <h3 className="font-medium text-gray-900">{search.name}</h3>
                  <div className="mt-2 space-y-1 text-sm text-gray-600">
                    {search.keywords && search.keywords.length > 0 && (
                      <p>Keywords: {search.keywords.join(', ')}</p>
                    )}
                    {search.zip_code && (
                      <p>Location: {search.zip_code} ({search.radius_miles} mi)</p>
                    )}
                  </div>
                  <button
                    onClick={() => runSavedSearch(search.id!)}
                    className="mt-3 text-primary-600 hover:text-primary-700 text-sm font-medium"
                  >
                    Run Search →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
