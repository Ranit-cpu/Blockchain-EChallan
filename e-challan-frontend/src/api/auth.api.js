import apiClient from './axios';

export const authApi = {
  login: (credentials) =>
    apiClient.post('/auth/login', credentials),

  logout: () =>
    apiClient.post('/auth/logout'),

  me: () =>
    apiClient.get('/auth/me'),
};
