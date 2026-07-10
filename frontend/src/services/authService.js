import api from './api';
export const authService = {
    login: (data) => api.post('/auth/login', data),
    register: (data) => api.post('/auth/register', data),
    me: () => api.get('/auth/me'),
    updateMe: (data) => api.put('/auth/me', data),
    listUsers: (params) => api.get('/auth/users', { params }),
    listRoles: () => api.get('/auth/roles'),
    createUser: (data) => api.post('/auth/users', data),
    updateUser: (id, data) => api.put(`/auth/users/${id}`, data),
    logout: () => { localStorage.clear(); },
};
