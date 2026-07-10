import api from './api';
export const saleService = {
    create: (data) => api.post('/sales', data),
    list: (params) => api.get('/sales', { params }),
    get: (id) => api.get(`/sales/${id}`),
    getInvoice: (invoiceNumber) => api.get(`/sales/invoice/${invoiceNumber}`),
    summary: () => api.get('/sales/summary'),
    cancel: (id) => api.post(`/sales/${id}/cancel`),
};
