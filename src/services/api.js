// src/services/api.js - Centralized API service

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: 'http://localhost:5001/api', // Updated to port 5001
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request interceptor to add JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    login: (credentials) => api.post('/auth/login', credentials),
    register: (userData) => api.post('/auth/register', userData),
    logout: () => api.post('/auth/logout'),
    getProfile: () => api.get('/auth/profile'),
};

// User API
export const userAPI = {
    getDashboard: () => api.get('/user/dashboard'),
    getProfile: () => api.get('/user/profile'),
    getSubjects: () => api.get('/user/subjects'),
    getQuizzesBySubject: (subjectId) => api.get(`/user/subjects/${subjectId}/quizzes`),
    startQuiz: (quizId) => api.get(`/user/quiz/${quizId}/take`),
    submitQuiz: (quizId, answers) => api.post(`/user/quiz/${quizId}/submit`, answers),
    getScores: () => api.get('/user/scores'),
    getQuizSummary: (quizId) => api.get(`/user/quiz-summary/${quizId}`),
    getQuizResults: (quizId) => api.get(`/user/quiz/${quizId}/results`),
    getScoreSummary: () => api.get('/user/score-summary'),
    exportCSV: () => api.post('/user/export/csv'),
    getStats: () => api.get('/user/stats'),
};

// Admin API
export const adminAPI = {
    // Subjects
    getSubjects: () => api.get('/admin/subjects'),
    createSubject: (subjectData) => api.post('/admin/subjects', subjectData),
    updateSubject: (subjectId, subjectData) => api.put(`/admin/subjects/${subjectId}`, subjectData),
    deleteSubject: (subjectId) => api.delete(`/admin/subjects/${subjectId}`),
    
    // Chapters
    getChapters: () => api.get('/admin/chapters'),
    getChaptersBySubject: (subjectId) => api.get(`/admin/subjects/${subjectId}/chapters`),
    createChapter: (chapterData) => api.post('/admin/chapters', chapterData),
    updateChapter: (chapterId, chapterData) => api.put(`/admin/chapters/${chapterId}`, chapterData),
    deleteChapter: (chapterId) => api.delete(`/admin/chapters/${chapterId}`),
    
    // Quizzes
    getQuizzes: () => api.get('/admin/quizzes'),
    getQuizzesByChapter: (chapterId) => api.get(`/admin/chapters/${chapterId}/quizzes`),
    createQuiz: (quizData) => api.post('/admin/quizzes', quizData),
    updateQuiz: (quizId, quizData) => api.put(`/admin/quizzes/${quizId}`, quizData),
    deleteQuiz: (quizId) => api.delete(`/admin/quizzes/${quizId}`),
    
    // Questions
    getQuestions: () => api.get('/admin/questions'),
    getQuestionsByQuiz: (quizId) => api.get(`/admin/quizzes/${quizId}/questions`),
    createQuestion: (questionData) => api.post('/admin/questions', questionData),
    updateQuestion: (questionId, questionData) => api.put(`/admin/questions/${questionId}`, questionData),
    deleteQuestion: (questionId) => api.delete(`/admin/questions/${questionId}`),
    
    // Users
    getUsers: () => api.get('/admin/users'),
    searchUsers: (query) => api.get(`/admin/search/users?q=${query}`),
    
    // Search
    search: (query, type = 'all') => api.get(`/admin/search?q=${query}&type=${type}`),
    
    // Export
    exportCSV: () => api.post('/admin/export/csv'),
    
    // Stats
    getStats: () => api.get('/admin/stats'),
    getDashboardStats: () => api.get('/admin/dashboard/stats'),
    
    // Celery
    getCeleryStatus: () => api.get('/admin/celery/status'),
    getCeleryTasks: () => api.get('/admin/celery/tasks'),
    triggerExpireCheck: () => api.post('/admin/quiz/expire-check'),
    triggerExpireQuiz: (quizId) => api.post(`/admin/quiz/expire/${quizId}`),
    getTaskStatus: (taskId) => api.get(`/admin/task/${taskId}/status`),
    
    // Celery Task Management
    triggerCeleryTasks: (taskType) => api.post('/admin/celery/trigger-tasks', { task_type: taskType }),
    getTaskStatusById: (taskId) => api.get(`/admin/celery/task-status/${taskId}`),
    getActiveTasks: () => api.get('/admin/celery/active-tasks'),
    getWorkerStatus: () => api.get('/admin/celery/worker-status'),
};

// Helper functions
export const apiHelpers = {
    handleError: (error) => {
        console.error('API Error:', error);
        if (error.response && error.response.data && error.response.data.error) {
            return error.response.data.error;
        }
        return 'An unexpected error occurred';
    },
    
    formatDate: (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },
    
    formatDuration: (minutes) => {
        if (!minutes) return '0 min';
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
    },
    
    calculateScore: (correct, total) => {
        if (total === 0) return 0;
        return Math.round((correct / total) * 100);
    }
};

export default api; 