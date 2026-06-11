import apiClient from './axios';

export const paymentsApi = {
  process: (data) => apiClient.post('/challans/payments', data),
};