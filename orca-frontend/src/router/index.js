import { createRouter, createWebHistory } from 'vue-router';
import MainMenu from '../components/MainMenu.vue';
import LoginPage from '../components/LoginPage.vue';
import RegisterPage from '../components/RegisterPage.vue'
import MainProcesses from '@/components/MainProcesses.vue';

const routes = [
  { path: '/', component: MainMenu },
  { path: '/login', component:LoginPage },
  { path: '/register', component:RegisterPage},
  { path: '/processes', component:MainProcesses}
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
