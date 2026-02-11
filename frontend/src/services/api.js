/**
 * API service layer for InsuranceHub.
 * Centralizes all backend API calls with error handling.
 */
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Dashboard
export const fetchDashboardStats = () => api.get('/dashboard/stats').then(r => r.data);

// Insurers
export const fetchInsurers = () => api.get('/insurers').then(r => r.data);
export const fetchInsurer = (id) => api.get(`/insurers/${id}`).then(r => r.data);
export const triggerSync = (id) => api.post(`/insurers/${id}/sync`).then(r => r.data);

// Products
export const fetchProducts = (params) => api.get('/products', { params }).then(r => r.data);
export const fetchProduct = (id) => api.get(`/products/${id}`).then(r => r.data);
export const fetchProductTypes = () => api.get('/products/types').then(r => r.data);
export const importProducts = (formData) =>
  api.post('/products/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);

// Policies
export const fetchPolicies = (params) => api.get('/policies', { params }).then(r => r.data);
export const fetchPolicy = (id) => api.get(`/policies/${id}`).then(r => r.data);
export const createPolicy = (data) => api.post('/policies', data).then(r => r.data);
export const calculatePremium = (data) => api.post('/policies/calculate', data).then(r => r.data);

// Reports
export const fetchPremiumReport = (params) => api.get('/reports/premiums', { params }).then(r => r.data);
export const fetchClaimsReport = () => api.get('/reports/claims').then(r => r.data);
export const fetchProductsReport = () => api.get('/reports/products').then(r => r.data);
export const exportReport = (data) =>
  api.post('/reports/export', data, { responseType: 'blob' }).then(r => r.data);

// Sync
export const fetchSyncStatus = () => api.get('/sync/status').then(r => r.data);
export const fetchSyncLogs = () => api.get('/sync/logs').then(r => r.data);

export default api;
