import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../stores/modules/user';
import { hasToken } from '../utils/token';
import { isSuperAdmin, isHasModulePermission } from '../utils/permission';
import { ElMessage } from 'element-plus';

// 定义路由配置
const routes = [
  // 公开路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
      requiresSuperAdmin: false
    }
  },
  
  // 根路由重定向到仪表盘
  {
    path: '/',
    redirect: '/dashboard'
  },
  
  // 需要认证的主路由（包含Layout布局）
  {
    path: '/',
    component: () => import('../layout/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      // 仪表盘
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: {
          title: '仪表盘',
          requiresSuperAdmin: false,
        }
      },
      
      // 活动查询模块
      {
        path: 'activity-query',
        name: 'ActivityQuery',
        component: () => import('../views/ActivityQuery.vue'),
        meta: {
          title: '活动查询',
          requiresSuperAdmin: false,
          module: 'activity_query'
        }
      },
      
      // 活动监控模块
      {
        path: 'activity-monitor',
        name: 'ActivityMonitor',
        component: () => import('../views/ActivityMonitor.vue'),
        meta: {
          title: '持续监控',
          requiresSuperAdmin: false,
          module: 'activity_monitor'
        }
      },
      
      // 自动跟单模块
      {
        path: 'copy-trade',
        name: 'CopyTrade',
        component: () => import('../views/CopyTrade.vue'),
        meta: {
          title: '自动跟单',
          requiresSuperAdmin: false,
          module: 'copy_trade'
        }
      },
      
      // 超级管理员专属路由 - 用户管理
      {
        path: 'user-manage',
        name: 'UserManage',
        component: () => import('../views/UserManage/UserList.vue'),
        meta: {
          title: '用户管理',
          requiresSuperAdmin: true
        }
      },
      // 新增用户
      {
        path: 'user-manage/add',
        name: 'AddUser',
        component: () => import('../views/UserManage/AddUser.vue'),
        meta: {
          title: '新增用户',
          requiresSuperAdmin: true
        }
      },
      // 配置权限
      {
        path: 'user-manage/set-permission',
        name: 'SetPermission',
        component: () => import('../views/UserManage/SetPermission.vue'),
        meta: {
          title: '配置权限',
          requiresSuperAdmin: true
        }
      }
    ]
  },
  
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: '404页面',
      requiresAuth: false
    }
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - Vue3 Frontend`;
  
  // 获取用户状态
  const userStore = useUserStore();
  const tokenExists = hasToken();
  
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    if (!tokenExists) {
      // 没有登录，跳转登录页
      ElMessage({
        message: '请先登录',
        type: 'warning',
        duration: 3000
      });
      next('/login');
      return;
    }
    
    // 检查是否为超级管理员
    if (to.meta.requiresSuperAdmin) {
      if (!userStore.isSuperAdmin && !isSuperAdmin()) {
        // 不是超级管理员，跳转仪表盘
        ElMessage({
          message: '权限不足，无法访问该页面',
          type: 'warning',
          duration: 3000
        });
        next('/dashboard');
        return;
      }
    }
    
    // 检查模块权限
    if (to.meta.module) {
      if (!isHasModulePermission(to.meta.module)) {
        // 没有模块权限，跳转仪表盘
        ElMessage({
          message: '没有该模块的访问权限',
          type: 'warning',
          duration: 3000
        });
        next('/dashboard');
        return;
      }
    }
    
    // 已登录且有权限，继续访问
    next();
  } else {
    // 不需要登录的页面
    if (to.path === '/login' && tokenExists) {
      // 已登录，跳转仪表盘
      next('/dashboard');
      return;
    }
    
    next();
  }
});

export default router;