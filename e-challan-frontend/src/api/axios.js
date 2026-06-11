import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const API_URL =
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,

  withCredentials: true,

  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },

  timeout: 30000,
});

apiClient.interceptors.request.use(
  (config) => {
    const { user } = useAuthStore.getState();

    if (user?.id) {
      config.headers['X-User-Id'] = user.id;
    }

    return config;
  },

  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    const status = error.response?.status;

    if (
      status === 401 &&
      !originalRequest?._retry
    ) {
      originalRequest._retry = true;

      const {
        clearAuth,
        setAuthChecked,
      } = useAuthStore.getState();

      clearAuth();

      setAuthChecked(true);

      if (
        !window.location.pathname.includes('/login')
      ) {
        window.location.href = '/login';
      }
    }

    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';

    return Promise.reject({
      status,

      message:
        typeof message === 'string'
          ? message
          : JSON.stringify(message),

      data: error.response?.data,

      originalError: error,
    });
  }
);

export default apiClient;