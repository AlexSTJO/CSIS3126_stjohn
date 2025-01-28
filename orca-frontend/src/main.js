import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import "url-search-params-polyfill";

const app = createApp(App);
app.use(router); 
app.mount('#app');
