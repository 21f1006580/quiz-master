import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import api from './services/api';

Vue.config.productionTip = false;

// Make API available globally
Vue.prototype.$api = api;

// Initialize authentication state
store.dispatch('auth/initAuth');

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app');
