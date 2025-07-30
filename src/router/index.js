import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '../store';

import SubjectManager from '../components/Admin/SubjectManager.vue';
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import UserDashboard from '../views/UserDashboard.vue'
import SubjectQuizzes from '../views/SubjectQuizzes.vue'
import QuizTaking from '../views/QuizTaking.vue'
import QuizSummary from '../views/QuizSummary.vue'
import ScoresPage from '../views/ScoresPage.vue'

Vue.use(VueRouter);

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login, meta: { guest: true } },
    { path: '/register', component: Register, meta: { guest: true } },
    { path: '/dashboard', component: UserDashboard, meta: { requiresAuth: true } },
    { path: '/user/subjects/:subjectId/quizzes', component: SubjectQuizzes, meta: { requiresAuth: true } },
    { path: '/user/quiz/:quizId/take', component: QuizTaking, meta: { requiresAuth: true } },
    { path: '/quiz-summary/:quizId', component: QuizSummary, meta: { requiresAuth: true } },
    { path: '/scores', component: ScoresPage, meta: { requiresAuth: true } },
    { path: '/admin/subjects', component: SubjectManager, meta: { requiresAuth: true, requiresAdmin: true } },
    { path: '/admin/chapters', component: () => import('../components/Admin/ChapterList.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
    { path: '/admin/quizzes', component: () => import('../components/Admin/QuizList.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
    { path: '/admin/questions', component: () => import('../components/Admin/QuestionList.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
    { path: '/admin/users', component: () => import('../components/Admin/UserList.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
    { path: '/admin', component: AdminDashboard, meta: { requiresAuth: true, requiresAdmin: true } },
];

// Define the router instance
const router = new VueRouter({
  mode: 'history',
  routes,
});

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  const isAdmin = store.getters['auth/isAdmin'];
  
  // If route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next('/login');
      return;
    }
    
    // If route requires admin access
    if (to.matched.some(record => record.meta.requiresAdmin)) {
      if (!isAdmin) {
        next('/dashboard');
        return;
      }
    }
  }
  
  // If route is for guests only (login/register)
  if (to.matched.some(record => record.meta.guest)) {
    if (isAuthenticated) {
      // Redirect to appropriate dashboard
      if (isAdmin) {
        next('/admin');
      } else {
        next('/dashboard');
      }
      return;
    }
  }
  
  next();
});

export default router;