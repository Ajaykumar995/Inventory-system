import api from './api';
export const inventoryService = {
    dashboard: () => api.get('/inventory/dashboard'),
    listStock: (params) => api.get('/inventory/stock', { params }),
    setup: (data) => api.post('/inventory/setup', data),
    receive: (productId, data) => api.post(`/inventory/stock/${productId}/receive`, data),
    issue: (productId, data) => api.post(`/inventory/stock/${productId}/issue`, data),
    adjust: (productId, data) => api.post(`/inventory/stock/${productId}/adjust`, data),
    listMovements: (params) => api.get('/inventory/movements', { params }),
};
