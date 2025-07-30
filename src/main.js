import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';

Vue.config.productionTip = false;

// Initialize authentication state
store.dispatch('auth/initAuth');

new Vue({
  router,
  store,
  render: h => h(App),
}).$mount('#app');
