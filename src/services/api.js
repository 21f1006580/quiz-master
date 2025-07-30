import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
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

// Authentication API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  adminLogin: (credentials) => api.post('/auth/admin-login', credentials),
  getProfile: () => api.get('/auth/profile'),
  changePassword: (passwords) => api.post('/auth/change-password', passwords),
};

// User API
export const userAPI = {
  getDashboard: () => api.get('/user/dashboard'),
  getProfile: () => api.get('/user/profile'),
  getQuizzesBySubject: (subjectId) => api.get(`/user/subjects/${subjectId}/quizzes`),
  getQuizStatus: (quizId) => api.get(`/user/quiz/${quizId}/status`),
  startQuiz: (quizId) => api.get(`/user/quiz/${quizId}/take`),
  submitQuiz: (quizId, answers) => api.post(`/user/quiz/${quizId}/submit`, answers),
  getScores: () => api.get('/user/scores'),
  getQuizSummary: (quizId) => api.get(`/user/quiz-summary/${quizId}`),
  getQuizResults: (quizId) => api.get(`/user/quiz/${quizId}/results`),
  getScoreSummary: () => api.get('/user/score-summary'),
  checkAnswer: (questionId, selectedOption) => 
    api.post(`/user/question/${questionId}/check`, { selected_option: selectedOption }),
};

// Admin API
export const adminAPI = {
  getDashboardStats: () => api.get('/admin/dashboard/stats'),
  
  // Subjects
  getSubjects: (params = {}) => api.get('/admin/subjects', { params }),
  createSubject: (subjectData) => api.post('/admin/subjects', subjectData),
  updateSubject: (subjectId, subjectData) => api.put(`/admin/subjects/${subjectId}`, subjectData),
  deleteSubject: (subjectId) => api.delete(`/admin/subjects/${subjectId}`),
  
  // Chapters
  getChapters: (subjectId) => api.get(`/admin/subjects/${subjectId}/chapters`),
  getAllChapters: (params = {}) => api.get('/admin/chapters', { params }),
  createChapter: (chapterData) => api.post('/admin/chapters', chapterData),
  getChapter: (chapterId) => api.get(`/admin/chapters/${chapterId}`),
  updateChapter: (chapterId, chapterData) => api.put(`/admin/chapters/${chapterId}`, chapterData),
  deleteChapter: (chapterId) => api.delete(`/admin/chapters/${chapterId}`),
  
  // Quizzes
  getQuizzes: (chapterId) => api.get(`/admin/chapters/${chapterId}/quizzes`),
  createQuiz: (quizData) => api.post('/admin/quizzes', quizData),
  updateQuiz: (quizId, quizData) => api.put(`/admin/quizzes/${quizId}`, quizData),
  deleteQuiz: (quizId) => api.delete(`/admin/quizzes/${quizId}`),
  
  // Questions
  getQuestions: (quizId) => api.get(`/admin/quizzes/${quizId}/questions`),
  getQuestionsByChapter: (chapterId) => api.get(`/admin/chapters/${chapterId}/questions`),
  createQuestion: (questionData) => api.post('/admin/questions', questionData),
  getQuestion: (questionId) => api.get(`/admin/questions/${questionId}`),
  updateQuestion: (questionId, questionData) => api.put(`/admin/questions/${questionId}`, questionData),
  deleteQuestion: (questionId) => api.delete(`/admin/questions/${questionId}`),
  
  // Users
  getUsers: (params = {}) => api.get('/admin/users', { params }),
  
  // Quiz Management
  manualExpireCheck: () => api.post('/admin/quiz/expire-check'),
  manualExpireQuiz: (quizId) => api.post(`/admin/quiz/expire/${quizId}`),
  bulkQuizStatusUpdate: () => api.post('/admin/quizzes/status-check'),
  
  // Celery Management
  getCeleryStatus: () => api.get('/admin/celery/status'),
  getCeleryTasks: () => api.get('/admin/celery/tasks'),
  getTaskStatus: (taskId) => api.get(`/admin/task/${taskId}/status`),
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
  
  setAuthToken: (token) => {
    localStorage.setItem('access_token', token);
  },
  
  getAuthToken: () => {
    return localStorage.getItem('access_token');
  },
  
  removeAuthToken: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
  
  isAdmin: () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user.is_admin === true;
  },
};

export default api; 