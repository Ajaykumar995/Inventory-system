import api from './api';
export const predictionService = {
    dashboard: (days, limit) => api.get('/prediction/dashboard', { params: { days, limit } }),
    fastMoving: (days) => api.get('/prediction/fast-moving', { params: { days } }),
    slowMoving: (days) => api.get('/prediction/slow-moving', { params: { days } }),
    reorder: (days) => api.get('/prediction/reorder', { params: { days } }),
    nextMonth: (days) => api.get('/prediction/next-month', { params: { days } }),
};
