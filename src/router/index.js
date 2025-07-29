import Vue from 'vue';
import VueRouter from 'vue-router';

import SubjectManager from '../views/SubjectManager.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../views/AdminDashboard.vue';

Vue.use(VueRouter);

const routes = [
    {path : '/', redirect: '/login'},
    {path : '/login', component: Login},
    {path : '/register', component: Register},
    { path: '/admin/subjects', component: SubjectManager },
    {path: '/admin', component: AdminDashboard },
    {path: '/dashboard', component: Login} // Temporary - will be replaced with actual dashboard
  // ... other routes
]




// Define the router instance
const router = new VueRouter({
  mode: 'history',
  routes,
});




export default router;