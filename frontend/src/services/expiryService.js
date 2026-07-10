import api from './api';
export const expiryService = {
    summary: (days) => api.get('/expiry/summary', { params: { days } }),
    listBatches: (params) => api.get('/expiry/batches', { params }),
    addBatch: (data) => api.post('/expiry/batches', data),
    dispose: (batchId, reason) => api.post(`/expiry/batches/${batchId}/dispose`, { reason }),
    syncNotifications: () => api.post('/expiry/notifications/sync'),
    listNotifications: (params) => api.get('/expiry/notifications', { params }),
    markRead: (id) => api.put(`/expiry/notifications/${id}/read`),
};
