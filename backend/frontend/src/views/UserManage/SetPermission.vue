<template>
  <div class="set-permission-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>配置用户权限</h2>
      <el-button @click="handleBack">
        <el-icon><Back /></el-icon>
        返回列表
      </el-button>
    </div>

    <!-- 权限配置表单 -->
    <el-card class="form-card">
      <div class="user-info">
        <h3>用户：{{ userInfo.username }}</h3>
        <el-tag :type="userInfo.role === 'super_admin' ? 'success' : 'info'">
          {{ userInfo.role === 'super_admin' ? '超级管理员' : '普通用户' }}
        </el-tag>
      </div>

      <el-form ref="permissionFormRef" :model="permissionForm">
        <el-form-item label="模块权限">
          <el-checkbox-group v-model="permissionForm.permissions">
            <el-checkbox label="activity_query">活动查询</el-checkbox>
            <el-checkbox label="activity_monitor">持续监控</el-checkbox>
            <el-checkbox label="copy_trade">自动跟单</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit">保存权限</el-button>
          <el-button @click="handleBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Back } from '@element-plus/icons-vue';
import request from '../../utils/request';

// 路由实例
const router = useRouter();
const route = useRoute();

// 表单引用
const permissionFormRef = ref(null);

// 用户信息
const userInfo = reactive({
  id: '',
  username: '',
  role: ''
});

// 权限表单
const permissionForm = reactive({
  permissions: []
});

// 页面加载时获取用户信息和当前权限
onMounted(() => {
  fetchUserData();
});

// 获取用户数据和权限
const fetchUserData = async () => {
  try {
    const userId = route.query.id;
    if (!userId) {
      ElMessage.error('用户ID不能为空');
      router.push('/user-manage');
      return;
    }

    // 从用户列表接口获取并过滤当前用户信息
    const res = await request.get(`/api/v1/user-manage/list`, { 
      params: { page: 1, per_page: 100 } 
    });
    const user = res.data.users.find(u => u.id == userId);
    if (user) {
      userInfo.id = user.id;
      userInfo.username = user.username;
      userInfo.role = user.is_super_admin ? 'super_admin' : 'user';
      
      // 从用户对象中获取权限信息
      permissionForm.permissions = [];
      if (user.activity_query) permissionForm.permissions.push('activity_query');
      if (user.activity_monitor) permissionForm.permissions.push('activity_monitor');
      if (user.copy_trade) permissionForm.permissions.push('copy_trade');
    } else {
      throw new Error('用户不存在');
    }
  } catch (error) {
    console.error('获取用户数据失败:', error);
    ElMessage.error('获取用户数据失败');
    router.push('/user-manage');
  }
};

// 提交权限配置
const handleSubmit = async () => {
  try {
    // 构建权限对象
    const permissions = {
      user_id: userInfo.id,
      activity_query: permissionForm.permissions.includes('activity_query'),
      activity_monitor: permissionForm.permissions.includes('activity_monitor'),
      copy_trade: permissionForm.permissions.includes('copy_trade')
    };

    // 调用权限配置接口
    await request.put('/api/v1/user-manage/set-permission', permissions);
    ElMessage.success('权限配置保存成功');
    router.push('/user-manage');
  } catch (error) {
    console.error('保存权限配置失败:', error);
    ElMessage.error('保存权限配置失败');
  }
};

// 返回列表
const handleBack = () => {
  router.push('/user-manage');
};
</script>

<style scoped>
.set-permission-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #303133;
}

.form-card {
  max-width: 600px;
}

.user-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 6px;
  display: flex;
  align-items: center;
}

.user-info h3 {
  margin: 0 15px 0 0;
  font-size: 1.2rem;
  color: #303133;
}

:deep(.el-checkbox) {
  margin-right: 20px;
  margin-bottom: 10px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>