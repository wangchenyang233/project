<template>
  <aside class="sidebar">
    <!-- 菜单列表 -->
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical-demo"
      background-color="#001529"
      text-color="#fff"
      active-text-color="#ffd04b"
      router
    >
      <!-- 仪表盘 -->
      <el-menu-item index="/dashboard">
        <template #title>
          <el-icon><Histogram /></el-icon>
          <span>仪表盘</span>
        </template>
      </el-menu-item>

      <!-- 活动查询 -->
      <el-menu-item
        v-if="hasPermission('activity_query')"
        index="/activity-query"
      >
        <template #title>
          <el-icon><Search /></el-icon>
          <span>活动查询</span>
        </template>
      </el-menu-item>

      <!-- 持续监控 -->
      <el-menu-item
        v-if="hasPermission('activity_monitor')"
        index="/activity-monitor"
      >
        <template #title>
          <el-icon><VideoPlay /></el-icon>
          <span>持续监控</span>
        </template>
      </el-menu-item>

      <!-- 自动跟单 -->
      <el-menu-item
        v-if="hasPermission('copy_trade')"
        index="/copy-trade"
      >
        <template #title>
          <el-icon><Operation /></el-icon>
          <span>自动跟单</span>
        </template>
      </el-menu-item>

      <!-- 用户管理（超级管理员专属） -->
      <el-menu-item
        v-if="isSuperAdmin"
        index="/user-manage"
      >
        <template #title>
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </template>
      </el-menu-item>
    </el-menu>
  </aside>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '../../stores/modules/user';
import { Histogram, Search, VideoPlay, Operation, User } from '@element-plus/icons-vue';

// 路由实例
const route = useRoute();
// 用户状态
const userStore = useUserStore();

// 计算属性
const activeMenu = computed(() => {
  return route.path;
});

// 检查是否为超级管理员
const isSuperAdmin = computed(() => {
  return userStore.role === 'super_admin';
});

// 检查是否有模块权限
const hasPermission = (module) => {
  // 超级管理员拥有所有权限
  if (isSuperAdmin.value) {
    return true;
  }
  // 检查用户是否拥有该模块权限
  return userStore.permissions?.[module] || false;
};
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  background-color: #001529;
  color: #fff;
  overflow-y: auto;
  flex-shrink: 0;
}

.el-menu {
  border-right: none;
  background-color: transparent;
}

.el-menu-item {
  height: 60px;
  line-height: 60px;
  font-size: 16px;
  margin: 10px 0;
  border-radius: 0 20px 20px 0;
  transition: all 0.3s;
}

.el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.el-menu-item.is-active {
  background-color: rgba(24, 144, 255, 0.2);
  border-bottom: 2px solid #1890ff;
}

.el-icon {
  margin-right: 10px;
  font-size: 18px;
}
</style>
