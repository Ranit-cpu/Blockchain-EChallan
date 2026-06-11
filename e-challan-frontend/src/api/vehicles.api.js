import apiClient from './axios';
import { buildQueryString } from '@/lib/utils';

export const vehiclesApi = {
  list: (params = {}) =>
    apiClient.get(`/vehicles${buildQueryString(params)}`),
  getById: (id) => apiClient.get(`/vehicles/${id}`),
  create: (data) => apiClient.post('/vehicles', data),
  update: (id, data) => apiClient.patch(`/vehicles/${id}`, data),
  getByRegistration: (reg) =>
    apiClient.get(`/vehicles/registration/${encodeURIComponent(reg)}`),
};