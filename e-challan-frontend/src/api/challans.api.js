import apiClient from './axios';
import { buildQueryString } from '@/lib/utils';

const multipart = { headers: { 'Content-Type': 'multipart/form-data' } };

export const challansApi = {
  // Violations
  listViolations: () => apiClient.get('/challans/violations'),
  createViolation: (data) => apiClient.post('/challans/violations', data),

  // Challans
  list: (params = {}) => apiClient.get(`/challans${buildQueryString(params)}`),
  getById: (id) => apiClient.get(`/challans/${id}`),
  getByNumber: (num) =>
    apiClient.get(`/challans/number/${encodeURIComponent(num)}`),
  create: (formData) => apiClient.post('/challans', formData, multipart),
  update: (id, data) => apiClient.patch(`/challans/${id}`, data),
  getStats: () => apiClient.get('/challans/stats'),
  verify: (challanNumber) =>
    apiClient.get(`/challans/verify/${encodeURIComponent(challanNumber)}`),

  // Evidence
  uploadEvidence: (challanId, formData, onProgress) =>
    apiClient.post(`/challans/${challanId}/evidence`, formData, {
      ...multipart,
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      },
    }),

  // Payments
  processPayment: (data) => apiClient.post('/challans/payments', data),
};