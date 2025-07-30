import { authAPI, apiHelpers } from '../services/api';

const state = {
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('access_token') || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
  error: null
};

const mutations = {
  SET_USER(state, user) {
    state.user = user;
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  },
  
  SET_TOKEN(state, token) {
    state.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
    state.isAuthenticated = !!token;
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  
  SET_ERROR(state, error) {
    state.error = error;
  },
  
  CLEAR_ERROR(state) {
    state.error = null;
  },
  
  LOGOUT(state) {
    state.user = null;
    state.token = null;
    state.isAuthenticated = false;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }
};

const actions = {
  async login({ commit }, credentials) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await authAPI.login(credentials);
      const { access_token, user } = response.data;
      
      commit('SET_TOKEN', access_token);
      commit('SET_USER', user);
      
      return { success: true, user };
    } catch (error) {
      const errorMessage = apiHelpers.handleError(error);
      commit('SET_ERROR', errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async adminLogin({ commit }, credentials) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await authAPI.adminLogin(credentials);
      const { access_token, user } = response.data;
      
      commit('SET_TOKEN', access_token);
      commit('SET_USER', user);
      
      return { success: true, user };
    } catch (error) {
      const errorMessage = apiHelpers.handleError(error);
      commit('SET_ERROR', errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async register({ commit }, userData) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await authAPI.register(userData);
      const { access_token, user } = response.data;
      
      commit('SET_TOKEN', access_token);
      commit('SET_USER', user);
      
      return { success: true, user };
    } catch (error) {
      const errorMessage = apiHelpers.handleError(error);
      commit('SET_ERROR', errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async getProfile({ commit }) {
    try {
      const response = await authAPI.getProfile();
      const user = response.data.user;
      commit('SET_USER', user);
      return { success: true, user };
    } catch (error) {
      const errorMessage = apiHelpers.handleError(error);
      commit('SET_ERROR', errorMessage);
      return { success: false, error: errorMessage };
    }
  },
  
  async changePassword({ commit }, passwords) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      await authAPI.changePassword(passwords);
      return { success: true };
    } catch (error) {
      const errorMessage = apiHelpers.handleError(error);
      commit('SET_ERROR', errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  logout({ commit }) {
    commit('LOGOUT');
  },
  
  clearError({ commit }) {
    commit('CLEAR_ERROR');
  },
  
  initAuth({ commit }) {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    
    if (token && user) {
      commit('SET_TOKEN', token);
      commit('SET_USER', user);
    }
  }
};

const getters = {
  isAuthenticated: state => state.isAuthenticated,
  isAdmin: state => state.user && state.user.is_admin === true,
  user: state => state.user,
  token: state => state.token,
  loading: state => state.loading,
  error: state => state.error,
  userFullName: state => state.user && state.user.full_name || 'User',
  userEmail: state => state.user && state.user.user_name || ''
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}; 