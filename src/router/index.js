import Vue from 'vue';
import VueRouter from 'vue-router';

import SubjectManager from '../views/SubjectManager.vue'
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
    {path : '/', redirect: '/login'},
    {path : '/login', component: Login},
    {path : '/register', component: Register},
    {path: '/dashboard', component: UserDashboard},
    {path: '/user/subject/:subjectId/quizzes', component: SubjectQuizzes},
    {path: '/quiz/:quizId', component: QuizTaking},
    {path: '/quiz-summary/:quizId', component: QuizSummary},
    {path: '/scores', component: ScoresPage},
    {path: '/admin/subjects', component: SubjectManager},
    {path: '/admin/chapters', component: () => import('../components/Admin/ChapterList.vue')},
    {path: '/admin/quizzes', component: () => import('../components/Admin/QuizList.vue')},
    {path: '/admin/questions', component: () => import('../components/Admin/QuestionList.vue')},
    {path: '/admin/users', component: () => import('../components/Admin/UserList.vue')},
    {path: '/admin', component: AdminDashboard}
]

// Define the router instance
const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;