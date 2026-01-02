<template>
  <div class="user-list-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="handleAddUser">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" size="small">
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
          ></el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="searchForm.role"
            placeholder="请选择角色"
            clearable
          >
            <el-option label="超级管理员" value="super_admin"></el-option>
            <el-option label="普通用户" value="user"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshRight /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="userList"
        style="width: 100%"
        stripe
      >
        <el-table-column type="index" label="序号" width="80"></el-table-column>
        <el-table-column prop="username" label="用户名" min-width="150"></el-table-column>
        <el-table-column prop="role" label="角色" min-width="100">
          <template #default="scope">
            <el-tag
              :type="scope.row.role === 'super_admin' ? 'success' : 'info'"
            >
              {{ scope.row.role === 'super_admin' ? '超级管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180"></el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="180"></el-table-column>
        <el-table-column label="操作" min-width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleEditUser(scope.row)"
              v-if="scope.row.role !== 'super_admin'"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleSetPermission(scope.row)"
              v-if="scope.row.role !== 'super_admin'"
            >
              <el-icon><Lock /></el-icon>
              配置权限
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDeleteUser(scope.row)"
              v-if="scope.row.role !== 'super_admin'"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Search, RefreshRight, Edit, Lock, Delete } from '@element-plus/icons-vue';
import request from '../../utils/request';

// 路由实例
const router = useRouter();

// 加载状态
const loading = ref(false);

// 搜索表单
const searchForm = reactive({
  username: '',
  role: ''
});

// 分页信息
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
});

// 用户列表数据
const userList = ref([]);

// 页面加载时获取用户列表
onMounted(() => {
  fetchUserList();
});

// 获取用户列表
const fetchUserList = async () => {
  try {
    loading.value = true;
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize,
      ...searchForm
    };
    const res = await request.get('/api/v1/user-manage/list', { params });
    userList.value = res.data.users;
    pagination.total = res.data.total;
  } catch (error) {
    console.error('获取用户列表失败:', error);
    ElMessage.error('获取用户列表失败');
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.currentPage = 1;
  fetchUserList();
};

// 重置搜索
const handleReset = () => {
  searchForm.username = '';
  searchForm.role = '';
  pagination.currentPage = 1;
  fetchUserList();
};

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size;
  fetchUserList();
};

// 当前页变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current;
  fetchUserList();
};

// 新增用户
const handleAddUser = () => {
  router.push('/user-manage/add');
};

// 编辑用户
const handleEditUser = (user) => {
  router.push(`/user-manage/add?id=${user.id}`);
};

// 配置权限
const handleSetPermission = (user) => {
  router.push(`/user-manage/set-permission?id=${user.id}`);
};

// 删除用户
const handleDeleteUser = (user) => {
  ElMessageBox.confirm(`确定要删除用户 "${user.username}" 吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/api/v1/user-manage/delete?user_id=${user.id}`);
      ElMessage.success('删除用户成功');
      fetchUserList();
    } catch (error) {
      console.error('删除用户失败:', error);
      ElMessage.error('删除用户失败');
    }
  }).catch(() => {
    // 取消删除操作
  });
};
</script>

<style scoped>
.user-list-container {
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

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

:deep(.el-button) {
  margin-right: 8px;
}
</style>