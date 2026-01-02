<template>
  <div class="add-user-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>{{ isEdit ? '编辑用户' : '新增用户' }}</h2>
      <el-button @click="handleBack">
        <el-icon><Back /></el-icon>
        返回列表
      </el-button>
    </div>

    <!-- 用户表单 -->
    <el-card class="form-card">
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="120px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
            :disabled="isEdit"
          ></el-input>
        </el-form-item>

        <el-form-item
          label="密码"
          prop="password"
          :required="!isEdit"
        >
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          ></el-input>
          <div v-if="isEdit" class="form-hint">
            不修改密码请留空
          </div>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="userForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          ></el-input>
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select
            v-model="userForm.role"
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option label="普通用户" value="user"></el-option>
            <el-option label="超级管理员" value="super_admin"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit">
            {{ isEdit ? '更新' : '提交' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage, ElForm, ElInput, ElSelect, ElOption, ElButton } from 'element-plus';
import { Back } from '@element-plus/icons-vue';
import request from '../../utils/request';

// 路由实例
const router = useRouter();
const route = useRoute();

// 表单引用
const userFormRef = ref(null);

// 计算是否为编辑模式
const isEdit = computed(() => {
  return !!route.query.id;
});

// 用户表单
const userForm = reactive({
  id: '',
  username: '',
  password: '',
  confirmPassword: '',
  role: 'user'
});

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: !isEdit.value, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度在 6 到 30 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: !isEdit.value, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== userForm.password) {
          callback(new Error('两次输入密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
};

// 监听编辑模式变化，加载用户数据
watch(isEdit, (newVal) => {
  if (newVal) {
    fetchUserData();
  }
});

// 页面加载时检查是否为编辑模式
onMounted(() => {
  if (isEdit.value) {
    fetchUserData();
  }
});

// 获取用户数据（编辑模式）
const fetchUserData = async () => {
  try {
    const userId = route.query.id;
    // 由于后端没有单个用户获取接口，我们从列表接口获取并过滤
    const res = await request.get(`/api/v1/user-manage/list`, { 
      params: { page: 1, per_page: 100 } 
    });
    const user = res.data.users.find(u => u.id == userId);
    if (user) {
      userForm.id = user.id;
      userForm.username = user.username;
      userForm.role = user.is_super_admin ? 'super_admin' : 'user';
    } else {
      throw new Error('用户不存在');
    }
  } catch (error) {
    console.error('获取用户数据失败:', error);
    ElMessage.error('获取用户数据失败');
    router.push('/user-manage');
  }
};

// 提交表单
const handleSubmit = async () => {
  try {
    await userFormRef.value.validate();
    
    // 构建请求数据
    const formData = {
      username: userForm.username,
      status: true // 默认启用状态
    };
    
    // 如果是新增用户或修改了密码，添加密码字段
    if (!isEdit.value || userForm.password) {
      formData.password = userForm.password;
    }
    
    if (isEdit.value) {
      // 编辑用户
      formData.user_id = userForm.id;
      await request.put('/api/v1/user-manage/edit', formData);
      ElMessage.success('更新用户成功');
    } else {
      // 新增用户
      await request.post('/api/v1/user-manage/add', formData);
      ElMessage.success('新增用户成功');
    }
    
    // 返回到用户列表
    router.push('/user-manage');
  } catch (error) {
    console.error('提交表单失败:', error);
    if (error instanceof Error) {
      ElMessage.error(error.message);
    } else {
      ElMessage.error('操作失败，请稍后重试');
    }
  }
};

// 重置表单
const handleReset = () => {
  userFormRef.value.resetFields();
};

// 返回列表
const handleBack = () => {
  router.push('/user-manage');
};
</script>

<style scoped>
.add-user-container {
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

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>