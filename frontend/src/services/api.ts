import axios from 'axios';

const API_BASE = '/api/v1';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth
export const login = async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await axios.post(`${API_BASE}/auth/token`, formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
};

export const register = async (data: { username: string; password: string; email?: string }) => {
    const response = await api.post('/auth/register', data);
    return response.data;
};

// Institutions
export const getInstitutions = async () => {
    const response = await api.get('/institutions');
    return response.data;
};

export const createInstitution = async (data: any) => {
    const response = await api.post('/institutions', data);
    return response.data;
};

export const getInstitutionStats = async (id: number) => {
    const response = await api.get(`/institutions/${id}/stats`);
    return response.data;
};

// Analytics
export const getAnalyticsOverview = async (days = 30) => {
    const response = await api.get(`/analytics/overview?days=${days}`);
    return response.data;
};

export const getDailyStats = async (days = 7) => {
    const response = await api.get(`/analytics/daily?days=${days}`);
    return response.data;
};

export const getCourseStats = async () => {
    const response = await api.get('/analytics/courses');
    return response.data;
};

export const getLowAttendanceStudents = async (threshold = 70) => {
    const response = await api.get(`/analytics/students/low-attendance?threshold=${threshold}`);
    return response.data;
};

// Students
export const getStudents = async () => {
    const response = await api.get('/students');
    return response.data;
};

// Sessions
export const getSessions = async () => {
    const response = await api.get('/sessions');
    return response.data;
};

export default api;
