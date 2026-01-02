<template>
  <div class="app-container">
    <!-- 路由出口 -->
    <router-view />
  </div>
</template>

<script setup>
// 导入必要的依赖
import { onMounted } from 'vue';
import { useUserStore } from './stores/modules/user';

// 初始化用户状态
const userStore = useUserStore();
onMounted(() => {
  // 如果有令牌，自动获取用户信息
  if (userStore.token) {
    userStore.getCurrentUserAction();
  }
});
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
  color: #303133;
}

.app-container {
  width: 100%;
  height: 100vh;
}
</style>
