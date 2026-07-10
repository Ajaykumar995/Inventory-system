import api from './api';
export const catalogService = {
    listCategories: (params) => api.get('/catalog/categories', { params }),
    createCategory: (data) => api.post('/catalog/categories', data),
    updateCategory: (id, data) => api.put(`/catalog/categories/${id}`, data),
    deleteCategory: (id) => api.delete(`/catalog/categories/${id}`),
    listProducts: (params) => api.get('/catalog/products', { params }),
    createProduct: (data) => api.post('/catalog/products', data),
    updateProduct: (id, data) => api.put(`/catalog/products/${id}`, data),
    deleteProduct: (id) => api.delete(`/catalog/products/${id}`),
    uploadProductImage: (productId, file) => {
        const form = new FormData();
        form.append('file', file);
        return api.post(`/catalog/products/${productId}/image`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
};
