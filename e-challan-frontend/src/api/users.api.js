import apiClient from './axios';
import { buildQueryString } from '@/lib/utils';

export const usersApi = {
  create: (data) => apiClient.post('/users', data),
  list: (params) => apiClient.get(`/users${buildQueryString(params)}`),
  getById: (id) => apiClient.get(`/users/${id}`),
  update: (id, data) => apiClient.patch(`/users/${id}`, data),
  deactivate: (id) => apiClient.delete(`/users/${id}`),
  changePassword: (id, data) =>
    apiClient.post(`/users/${id}/change-password`, data),
};