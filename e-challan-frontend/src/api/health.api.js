import apiClient from './axios';

export const healthApi = {
  check: () => apiClient.get('/health'),
};