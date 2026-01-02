import { defineStore } from 'pinia';
import request from '../../utils/request';
import { setToken, getToken, removeToken } from '../../utils/token';
import { ElMessage } from 'element-plus';

export const useUserStore = defineStore('user', {
  state: () => ({
    username: '',
    role: '',
    permissions: {
      activity_query: false,
      activity_monitor: false,
      copy_trade: false
    },
    isLogin: false,
    token: getToken() || ''
  }),
  
  getters: {
    /**
     * 判断是否为超级管理员
     */
    isSuperAdmin: (state) => {
      return state.role === 'super_admin';
    },
    
    /**
     * 判断是否拥有指定模块权限
     */
    hasModulePermission: (state) => (module) => {
      if (state.isSuperAdmin) return true;
      return state.permissions[module] || false;
    }
  },
  
  actions: {
    /**
     * 用户登录
     * @param {Object} loginInfo - 登录信息
     * @param {string} loginInfo.username - 用户名
     * @param {string} loginInfo.password - 密码
     */
    async loginAction(loginInfo) {
      try {
        const response = await request.post('/api/v1/auth/login', loginInfo);
        
        if (response.code === 200) {
          // 保存令牌
          const { access_token, refresh_token } = response.data;
          setToken(access_token, refresh_token);
          
          // 更新状态
          this.token = access_token;
          this.isLogin = true;
          
          // 获取用户信息
          await this.getCurrentUserAction();
          
          ElMessage({
            message: '登录成功',
            type: 'success',
            duration: 2000
          });
          
          return true;
        }
        
        return false;
      } catch (error) {
        console.error('Login failed:', error);
        ElMessage({
          message: '登录失败，请检查用户名和密码',
          type: 'error',
          duration: 3000
        });
        return false;
      }
    },
    
    /**
     * 获取当前用户信息
     */
    async getCurrentUserAction() {
      try {
        const response = await request.get('/api/v1/auth/current-user');
        
        if (response.code === 200) {
          const userInfo = response.data;
          
          // 更新用户信息
          this.username = userInfo.username;
          this.role = userInfo.is_super_admin ? 'super_admin' : 'user';
          this.permissions = {
            activity_query: userInfo.activity_query,
            activity_monitor: userInfo.activity_monitor,
            copy_trade: userInfo.copy_trade
          };
          this.isLogin = true;
          
          return true;
        }
        
        return false;
      } catch (error) {
        console.error('Get current user failed:', error);
        // 如果获取用户信息失败，可能是token失效
        this.logoutAction();
        return false;
      }
    },
    
    /**
     * 用户退出登录
     */
    logoutAction() {
      // 清除令牌
      removeToken();
      
      // 重置状态
      this.username = '';
      this.role = '';
      this.permissions = {
        activity_query: false,
        activity_monitor: false,
        copy_trade: false
      };
      this.isLogin = false;
      this.token = '';
      
      ElMessage({
        message: '已退出登录',
        type: 'info',
        duration: 2000
      });
    },
    
    /**
     * 初始化用户状态
     */
    async initUserStatus() {
      if (getToken()) {
        this.token = getToken();
        await this.getCurrentUserAction();
      }
    }
  }
});