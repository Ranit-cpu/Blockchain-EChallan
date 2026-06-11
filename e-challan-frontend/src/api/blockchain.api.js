import apiClient from './axios';

export const blockchainApi = {
  verify: (txHash) => apiClient.get(`/blockchain/verify/${txHash}`),
  verifyChallan: (challanNumber) =>
    apiClient.get(`/blockchain/challan/${encodeURIComponent(challanNumber)}`),
  getTransaction: (txHash) => apiClient.get(`/blockchain/transaction/${txHash}`),
  getNetworkStatus: () => apiClient.get('/blockchain/status'),
  anchorChallan: (challanId) => apiClient.post(`/blockchain/anchor/${challanId}`),
};
