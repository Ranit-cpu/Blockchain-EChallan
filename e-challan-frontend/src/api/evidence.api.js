import apiClient from './axios';
import { buildQueryString } from '@/lib/utils';

export const evidenceApi = {
  list: (params = {}) => apiClient.get(`/evidence${buildQueryString(params)}`),
  getById: (id) => apiClient.get(`/evidence/${id}`),
  upload: (formData, onProgress) =>
    apiClient.post('/evidence/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (onProgress && event.total) {
          onProgress(Math.round((event.loaded * 100) / event.total));
        }
      },
    }),
  delete: (id) => apiClient.delete(`/evidence/${id}`),
  getByChallan: (challanId) => apiClient.get(`/evidence/challan/${challanId}`),
};
