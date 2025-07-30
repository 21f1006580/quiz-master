import Vue from 'vue';
import Vuex from 'vuex';
import auth from './auth';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    auth
  },
  
  // Global state
  state: {
    appLoading: false,
    globalError: null
  },
  
  mutations: {
    SET_APP_LOADING(state, loading) {
      state.appLoading = loading;
    },
    
    SET_GLOBAL_ERROR(state, error) {
      state.globalError = error;
    },
    
    CLEAR_GLOBAL_ERROR(state) {
      state.globalError = null;
    }
  },
  
  actions: {
    setAppLoading({ commit }, loading) {
      commit('SET_APP_LOADING', loading);
    },
    
    setGlobalError({ commit }, error) {
      commit('SET_GLOBAL_ERROR', error);
    },
    
    clearGlobalError({ commit }) {
      commit('CLEAR_GLOBAL_ERROR');
    }
  },
  
  getters: {
    appLoading: state => state.appLoading,
    globalError: state => state.globalError
  }
}); 