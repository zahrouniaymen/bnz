import axios from 'axios';

// Use empty base URL to make requests relative - Vite proxy will handle routing to backend
const API_BASE_URL = '';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// ============= Authentication API =============

export const authAPI = {
    login: (username, password) => {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
        return api.post('/auth/login', params, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
    },

    register: (userData) => api.post('/auth/register', userData),

    getCurrentUser: () => api.get('/auth/me'),
};

// ============= Users API =============

export const usersAPI = {
    getAll: (skip = 0, limit = 100) =>
        api.get(`/users/?skip=${skip}&limit=${limit}`),

    getById: (id) => api.get(`/users/${id}`),

    update: (id, userData) => api.put(`/users/${id}`, userData),
};

// ============= Clients API =============

export const clientsAPI = {
    create: (clientData) => api.post('/clients/', clientData),

    getAll: (skip = 0, limit = 100) =>
        api.get(`/clients/?skip=${skip}&limit=${limit}`),

    getById: (id) => api.get(`/clients/${id}`),

    update: (id, clientData) => api.put(`/clients/${id}`, clientData),
    delete: (id) => api.delete(`/clients/${id}`),
};

// ============= Offers API =============

export const offersAPI = {
    create: (offerData) => api.post('/offers/', offerData),

    getAll: (params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.skip !== undefined) queryParams.append('skip', params.skip);
        if (params.limit !== undefined) queryParams.append('limit', params.limit);
        if (params.status) queryParams.append('status', params.status);
        if (params.priority) queryParams.append('priority', params.priority);
        if (params.client_id) queryParams.append('client_id', params.client_id);
        if (params.managed_by_id) queryParams.append('managed_by_id', params.managed_by_id);

        return api.get(`/offers/?${queryParams.toString()}`);
    },

    getMyOffers: (skip = 0, limit = 100) =>
        api.get(`/offers/my-offers?skip=${skip}&limit=${limit}`),

    getById: (id) => api.get(`/offers/${id}`),

    update: (id, offerData) => api.put(`/offers/${id}`, offerData),
};

// ============= Workflow API =============

export const workflowAPI = {
    create: (offerId, workflowData) =>
        api.post(`/offers/${offerId}/workflow`, workflowData),

    getSteps: (offerId) => api.get(`/offers/${offerId}/workflow`),

    updateStep: (stepId, stepData) => api.put(`/workflow/${stepId}`, stepData),
};

// ============= Files API =============

export const filesAPI = {
    upload: (offerId, file, fileType = 'attachment') => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('file_type', fileType);

        return api.post(`/offers/${offerId}/files`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },

    getAll: (offerId) => api.get(`/offers/${offerId}/files`),
};

// ============= Messages API =============

export const messagesAPI = {
    create: (offerId, messageData) =>
        api.post(`/offers/${offerId}/messages`, messageData),

    getAll: (offerId, skip = 0, limit = 100) =>
        api.get(`/offers/${offerId}/messages?skip=${skip}&limit=${limit}`),
};

// ============= Notes API =============

export const notesAPI = {
    create: (offerId, noteData) =>
        api.post(`/offers/${offerId}/notes`, noteData),

    getAll: (offerId, department = null) => {
        const url = department
            ? `/offers/${offerId}/notes?department=${department}`
            : `/offers/${offerId}/notes`;
        return api.get(url);
    },

    update: (noteId, noteData) => api.put(`/notes/${noteId}`, noteData),
};

// ============= Analytics API =============
export const analyticsAPI = {
    getMonthlyEvolution: (year) => api.get(`/analytics/monthly-evolution/${year}`),
    getReasons: (year) => api.get(`/analytics/reasons/${year}`),
    getComparison: (years = "2024,2025") => api.get(`/analytics/comparison?years=${years}`),
    getClientRanking: (year) => api.get(`/analytics/client-ranking/${year}`),
    getSectorDistribution: (year) => api.get(`/analytics/sector-distribution/${year}`),
    getItemMix: (year) => api.get(`/analytics/item-mix/${year}`),
};

// ============= Dashboard API =============

export const dashboardAPI = {
    getStats: (year = null) => {
        const url = year ? `/dashboard/stats?year=${year}` : '/dashboard/stats';
        return api.get(url);
    },
};

export default api;
