<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <div class="login-header">
        <h1 class="login-title">业务管理系统</h1>
        <p class="login-subtitle">请登录您的账户</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            autocomplete="off"
          ></el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            autocomplete="off"
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/modules/user';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';

// 路由实例
const router = useRouter();
// 用户状态
const userStore = useUserStore();
// 表单引用
const loginFormRef = ref(null);
// 加载状态
const loading = ref(false);

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
});

// 表单规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度在 6 到 30 个字符', trigger: 'blur' }
  ]
};

// 登录处理
const handleLogin = async () => {
  try {
    // 表单校验
    await loginFormRef.value.validate();
    loading.value = true;
    
    // 调用登录接口
    const success = await userStore.loginAction(loginForm);
    
    if (success) {
      ElMessage.success('登录成功');
      // 跳转到仪表盘
      router.push('/dashboard');
    } else {
      ElMessage.error('登录失败，请检查用户名和密码');
    }
  } catch (error) {
    console.error('Login failed:', error);
    if (error !== false) {
      ElMessage.error('登录失败，请稍后重试');
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form-wrapper {
  width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  font-size: 2rem;
  color: #1890ff;
  margin: 0 0 10px;
  font-weight: 600;
}

.login-subtitle {
  font-size: 1rem;
  color: #606266;
  margin: 0;
}

.login-form {
  width: 100%;
}

.login-button {
  width: 100%;
  font-size: 1rem;
  padding: 10px;
  background-color: #1890ff;
  border-color: #1890ff;
  border-radius: 6px;
}

.login-button:hover {
  background-color: #40a9ff;
  border-color: #40a9ff;
}

.login-button:active {
  background-color: #096dd9;
  border-color: #096dd9;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-input__inner) {
  font-size: 1rem;
  padding: 12px 15px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>
