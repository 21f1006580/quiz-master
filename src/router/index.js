import Vue from 'vue';
import VueRouter from 'vue-router';

import SubjectManager from '../views/SubjectManager.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../views/AdminDashboard.vue';

Vue.use(VueRouter);

const routes = [
    {path : '/login', component: Login},
    {path : '/register', component: Register},
    { path: '/admin/subjects', component: SubjectManager },
    {path: '/admin', component: AdminDashboard }
  // ... other routes
]




// Define the router instance
const router = new VueRouter({
  mode: 'history',
  routes,
});




export default router;