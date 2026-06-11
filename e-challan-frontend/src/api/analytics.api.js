import apiClient from './axios';
import { buildQueryString } from '@/lib/utils';

export const analyticsApi = {
  getDashboard: (params = {}) =>
    apiClient.get(`/analytics/dashboard${buildQueryString(params)}`),
  getChallanTrends: (params = {}) =>
    apiClient.get(`/analytics/challans/trends${buildQueryString(params)}`),
  getRevenue: (params = {}) =>
    apiClient.get(`/analytics/revenue${buildQueryString(params)}`),
  getViolationBreakdown: (params = {}) =>
    apiClient.get(`/analytics/violations${buildQueryString(params)}`),
  getOfficerPerformance: (params = {}) =>
    apiClient.get(`/analytics/officers${buildQueryString(params)}`),
};
