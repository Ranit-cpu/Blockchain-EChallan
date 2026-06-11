import apiClient from './axios';
import { buildQueryString } from '@/lib/utils';

export const ownersApi = {
  list: (params = {}) =>
    apiClient.get(`/vehicles/owners${buildQueryString(params)}`),
  getById: (id) => apiClient.get(`/vehicles/owners/${id}`),
  create: (data) => apiClient.post('/vehicles/owners', data),
  update: (id, data) => apiClient.patch(`/vehicles/owners/${id}`, data),
  getVehicles: (ownerId) =>
    apiClient.get(`/vehicles/owners/${ownerId}/vehicles`),
};