<template>
  <div class="activity-query-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>活动查询</h2>
    </div>

    <!-- 输入参数区域 -->
    <el-card class="input-card">
      <el-form :model="queryParams" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用户地址">
              <el-input
                v-model="queryParams.user_address"
                placeholder="请输入用户地址"
                clearable
              ></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Limit">
              <el-input-number
                v-model="queryParams.limit"
                :min="1"
                :max="1000"
                :step="1"
                placeholder="数量限制"
              ></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Offset">
              <el-input-number
                v-model="queryParams.offset"
                :min="0"
                :step="1"
                placeholder="偏移量"
              ></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 输出字段勾选 -->
        <el-form-item label="输出字段">
          <el-checkbox-group v-model="queryParams.fields">
            <el-checkbox label="block_number">区块号</el-checkbox>
            <el-checkbox label="transaction_hash">交易哈希</el-checkbox>
            <el-checkbox label="user_address">用户地址</el-checkbox>
            <el-checkbox label="size">交易金额</el-checkbox>
            <el-checkbox label="price">价格</el-checkbox>
            <el-checkbox label="side">交易方向</el-checkbox>
            <el-checkbox label="asset">资产ID</el-checkbox>
            <el-checkbox label="timestamp">时间戳</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshRight /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="activityData"
        style="width: 100%"
        stripe
      >
        <el-table-column type="index" label="序号" width="80"></el-table-column>
        <el-table-column prop="block_number" label="区块号" v-if="queryParams.fields.includes('block_number')"></el-table-column>
        <el-table-column prop="transaction_hash" label="交易哈希" v-if="queryParams.fields.includes('transaction_hash')">
          <template #default="scope">
            <el-tooltip :content="scope.row.transaction_hash" placement="top">
              <span class="truncate-text">{{ scope.row.transaction_hash }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="user_address" label="用户地址" v-if="queryParams.fields.includes('user_address')">
          <template #default="scope">
            <el-tooltip :content="scope.row.user_address" placement="top">
              <span class="truncate-text">{{ scope.row.user_address }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="交易金额" v-if="queryParams.fields.includes('size')"></el-table-column>
        <el-table-column prop="price" label="价格" v-if="queryParams.fields.includes('price')"></el-table-column>
        <el-table-column prop="side" label="交易方向" v-if="queryParams.fields.includes('side')">
          <template #default="scope">
            <el-tag :type="scope.row.side === 'BUY' ? 'success' : 'danger'">
              {{ scope.row.side }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="asset" label="资产ID" v-if="queryParams.fields.includes('asset')">
          <template #default="scope">
            <el-tooltip :content="scope.row.asset" placement="top">
              <span class="truncate-text">{{ scope.row.asset }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间戳" v-if="queryParams.fields.includes('timestamp')">
          <template #default="scope">
            {{ formatTimestamp(scope.row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { Search, RefreshRight } from '@element-plus/icons-vue';
import request from '../utils/request';

// 加载状态
const loading = ref(false);
// 分页信息
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
// 活动数据
const activityData = ref([]);

// 查询参数
const queryParams = reactive({
  user_address: '',
  limit: 20,
  offset: 0,
  fields: ['block_number', 'transaction_hash', 'user_address', 'size', 'timestamp', 'price', 'side', 'asset']
});

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000);
  return date.toLocaleString();
};

// 查询数据
const handleQuery = async () => {
  try {
    loading.value = true;
    // 计算offset
    queryParams.offset = (currentPage.value - 1) * pageSize.value;
    queryParams.limit = pageSize.value;
    
    const res = await request.get('/api/v1/activity/query', { params: queryParams });
    activityData.value = res.data;
    total.value = res.total;
  } catch (error) {
    console.error('查询活动数据失败:', error);
    ElMessage.error('查询活动数据失败');
    activityData.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

// 重置查询参数
const handleReset = () => {
  queryParams.user_address = '';
  queryParams.limit = 20;
  queryParams.offset = 0;
  queryParams.fields = ['block_number', 'transaction_hash', 'user_address', 'size', 'timestamp', 'price', 'side', 'asset'];
  currentPage.value = 1;
  pageSize.value = 20;
};

// 分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size;
  handleQuery();
};

// 当前页变化
const handleCurrentChange = (current) => {
  currentPage.value = current;
  handleQuery();
};
</script>

<style scoped>
.activity-query-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #303133;
}

.input-card {
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

.truncate-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-checkbox) {
  margin-right: 20px;
  margin-bottom: 10px;
}

:deep(.el-row) {
  margin-bottom: 15px;
}
</style>