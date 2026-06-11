import apiClient from './axios';
import { buildQueryString } from '@/lib/utils';

export const auditApi = {
  list: (params = {}) => apiClient.get(`/audit${buildQueryString(params)}`),
};