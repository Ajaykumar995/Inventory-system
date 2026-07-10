import api from './api';
export const purchaseService = {
    listSuppliers: (params) => api.get('/purchases/suppliers', { params }),
    createSupplier: (data) => api.post('/purchases/suppliers', data),
    supplierPerformance: (id) => api.get(`/purchases/suppliers/${id}/performance`),
    listOrders: (params) => api.get('/purchases/orders', { params }),
    createOrder: (data) => api.post('/purchases/orders', data),
    receiveOrder: (poId, items) => api.post(`/purchases/orders/${poId}/receive`, { items }),
    cancelOrder: (poId) => api.post(`/purchases/orders/${poId}/cancel`),
};
