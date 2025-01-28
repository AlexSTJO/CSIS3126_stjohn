import { createRouter, createWebHistory } from 'vue-router';
import HubPage from '../components/HubPage.vue';
import LoginPage from '../components/LoginPage.vue';
import RegisterPage from '../components/RegisterPage.vue';
import LinkPage from '../components/LinkPage.vue'

const routes = [
  { path: '/', component: HubPage },
  { path: '/login', component:LoginPage },
  { path: '/register', component:RegisterPage},
  { path: '/link', component:LinkPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
