import { createApp } from 'vue';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import App from './App.vue';
import router from './router';
import request from './utils/request';

// 创建Vue应用
const app = createApp(App);

// 挂载Pinia状态管理
const pinia = createPinia();
app.use(pinia);

// 挂载ElementPlus组件库
app.use(ElementPlus);

// 挂载路由
app.use(router);

// 全局注册axios请求实例
app.config.globalProperties.$http = request;

// 挂载应用
app.mount('#app');
