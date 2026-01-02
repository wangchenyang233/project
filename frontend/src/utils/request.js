import axios from 'axios';
import { ElMessage } from 'element-plus';
import { getToken, removeToken } from './token';
import { useUserStore } from '../stores/modules/user';
import router from '../router';

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '', // API基础URL
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 添加JWT令牌
    const token = getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    // 处理请求错误
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data;
    
    // 统一处理响应格式
    if (res.code !== 200) {
      // 错误提示
      ElMessage({
        message: res.msg || '请求失败',
        type: 'error',
        duration: 3000
      });
      
      // 处理特定错误码
      switch (res.code) {
        case 401:
          // 登录失效，清除token并跳转登录页
          ElMessage({
            message: '登录已失效，请重新登录',
            type: 'warning',
            duration: 3000
          });
          const userStore = useUserStore();
          userStore.logoutAction();
          router.push('/login');
          break;
        case 403:
          // 权限不足
          ElMessage({
            message: '权限不足，无法访问该资源',
            type: 'warning',
            duration: 3000
          });
          break;
        default:
          break;
      }
      
      return Promise.reject(new Error(res.msg || 'Error'));
    }
    
    return res;
  },
  error => {
    // 处理响应错误
    console.error('Response error:', error);
    
    // 网络错误处理
    if (!error.response) {
      ElMessage({
        message: '网络错误，请检查网络连接',
        type: 'error',
        duration: 3000
      });
      return Promise.reject(error);
    }
    
    // HTTP状态码处理
    const status = error.response.status;
    switch (status) {
      case 401:
        // 登录失效
        ElMessage({
          message: '登录已失效，请重新登录',
          type: 'warning',
          duration: 3000
        });
        const userStore = useUserStore();
        userStore.logoutAction();
        router.push('/login');
        break;
      case 403:
        // 权限不足
        ElMessage({
          message: '权限不足，无法访问该资源',
          type: 'warning',
          duration: 3000
        });
        break;
      case 404:
        // 资源不存在
        ElMessage({
          message: '请求的资源不存在',
          type: 'error',
          duration: 3000
        });
        break;
      case 500:
        // 服务器错误
        ElMessage({
          message: '服务器错误，请稍后重试',
          type: 'error',
          duration: 3000
        });
        break;
      default:
        ElMessage({
          message: `请求失败 (${status})`,
          type: 'error',
          duration: 3000
        });
        break;
    }
    
    return Promise.reject(error);
  }
);

export default request;