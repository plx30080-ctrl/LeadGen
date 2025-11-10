// API service for backend communication
import axios from 'axios';
import type {
  Lead, Company, Contact, JobPosting, SearchCriteria,
  LeadActivity, RoutePlan, IntegrationsStatus
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Leads API
export const leadsApi = {
  getAll: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get<Lead[]>('/api/leads', { params }),

  getOne: (id: number) =>
    api.get<Lead>(`/api/leads/${id}`),

  create: (data: Partial<Lead>) =>
    api.post<Lead>('/api/leads', data),

  update: (id: number, data: Partial<Lead>) =>
    api.patch<Lead>(`/api/leads/${id}`, data),

  delete: (id: number) =>
    api.delete(`/api/leads/${id}`),

  getActivities: (id: number) =>
    api.get<LeadActivity[]>(`/api/leads/${id}/activities`),

  addActivity: (id: number, data: Omit<LeadActivity, 'id' | 'created_at'>) =>
    api.post<LeadActivity>(`/api/leads/${id}/activities`, data),
};

// Companies API
export const companiesApi = {
  getAll: (params?: { skip?: number; limit?: number; search?: string; city?: string; state?: string }) =>
    api.get<Company[]>('/api/companies', { params }),

  getOne: (id: number) =>
    api.get<Company>(`/api/companies/${id}`),

  create: (data: Partial<Company>) =>
    api.post<Company>('/api/companies', data),

  update: (id: number, data: Partial<Company>) =>
    api.patch<Company>(`/api/companies/${id}`, data),

  delete: (id: number) =>
    api.delete(`/api/companies/${id}`),
};

// Contacts API
export const contactsApi = {
  getAll: (params?: { skip?: number; limit?: number; company_id?: number }) =>
    api.get<Contact[]>('/api/contacts', { params }),

  getOne: (id: number) =>
    api.get<Contact>(`/api/contacts/${id}`),

  create: (data: Partial<Contact>) =>
    api.post<Contact>('/api/contacts', data),

  update: (id: number, data: Partial<Contact>) =>
    api.patch<Contact>(`/api/contacts/${id}`, data),

  delete: (id: number) =>
    api.delete(`/api/contacts/${id}`),
};

// Jobs API
export const jobsApi = {
  getAll: (params?: any) =>
    api.get<JobPosting[]>('/api/jobs', { params }),

  getOne: (id: number) =>
    api.get<JobPosting>(`/api/jobs/${id}`),
};

// Search API
export const searchApi = {
  searchJobs: (data: any) =>
    api.post('/api/search/jobs', data),

  getSearchStatus: (taskId: string) =>
    api.get(`/api/search/jobs/status/${taskId}`),

  saveCriteria: (data: SearchCriteria) =>
    api.post<SearchCriteria>('/api/search/criteria', data),

  getCriteria: () =>
    api.get<SearchCriteria[]>('/api/search/criteria'),

  runSavedSearch: (id: number) =>
    api.post(`/api/search/criteria/${id}/run`),
};

// Content Generation API
export const contentApi = {
  generateCallScript: (leadId: number) =>
    api.post('/api/content/call-script', { lead_id: leadId }),

  generateEmail: (leadId: number, tone: string = 'professional') =>
    api.post('/api/content/email', { lead_id: leadId, tone }),

  generateBatchCallScripts: (leadIds: number[]) =>
    api.post('/api/content/batch/call-scripts', leadIds),

  generateBatchEmails: (leadIds: number[], tone: string = 'professional') =>
    api.post('/api/content/batch/emails', leadIds, { params: { tone } }),
};

// Route Planning API
export const routesApi = {
  planRoute: (leadIds: number[], startLocation?: string, optimize: boolean = true) =>
    api.post<RoutePlan>('/api/routes/plan', {
      lead_ids: leadIds,
      start_location: startLocation,
      optimize,
    }),
};

// Integrations API
export const integrationsApi = {
  getStatus: () =>
    api.get<IntegrationsStatus>('/api/integrations/status'),

  enrichCompany: (companyId: number) =>
    api.post(`/api/integrations/enrich/company/${companyId}`),

  discoverContacts: (companyId: number) =>
    api.post(`/api/integrations/discover/contacts/${companyId}`),

  testIntegration: (name: string) =>
    api.post(`/api/integrations/test/${name}`),
};

export default api;
