<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <Sidebar />
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部导航 -->
      <header class="top-header">
        <div class="header-left">
          <h1 class="system-title">业务管理系统</h1>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" :src="userAvatar"></el-avatar>
              <span>{{ userName }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- 内容区域 -->
      <main class="content-wrapper">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/modules/user';
import { ElMessage } from 'element-plus';
import Sidebar from './components/Sidebar.vue';
import { SwitchButton } from '@element-plus/icons-vue';

// 路由实例
const router = useRouter();
// 用户状态
const userStore = useUserStore();

// 计算属性
const userName = computed(() => userStore.username || '未知用户');
const userAvatar = computed(() => {
  // 简单生成用户头像
  const name = userName.value;
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=409EFF&color=fff&size=32`;
});

// 退出登录
const handleLogout = async () => {
  try {
    await userStore.logoutAction();
    router.push('/login');
    ElMessage.success('退出登录成功');
  } catch (error) {
    console.error('Logout failed:', error);
    ElMessage.error('退出登录失败');
  }
};
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 250px;
  background-color: #001529;
  color: #fff;
  overflow-y: auto;
  flex-shrink: 0;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航 */
.top-header {
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  flex-shrink: 0;
}

.system-title {
  font-size: 1.5rem;
  color: #1890ff;
  margin: 0;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f0f2f5;
}

.user-info span {
  margin-left: 10px;
  font-size: 14px;
  color: #303133;
}

/* 内容区域 */
.content-wrapper {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
}
</style>
