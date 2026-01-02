<template>
  <div class="copy-trade-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>自动跟单</h2>
    </div>

    <!-- 配置区域 -->
    <el-card class="config-card">
      <el-form ref="configFormRef" :model="tradeConfig" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="目标用户地址" prop="target_user">
              <el-input
                v-model="tradeConfig.target_user"
                placeholder="请输入目标用户地址"
                clearable
              ></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="钱包地址" prop="wallet_address">
              <el-input
                v-model="tradeConfig.wallet_address"
                placeholder="请输入钱包地址"
                clearable
              ></el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="私钥" prop="private_key">
              <el-input
                v-model="tradeConfig.private_key"
                type="password"
                placeholder="请输入私钥"
                clearable
              ></el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="handleSaveConfig">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
          <el-button
            type="success"
            @click="handleStartTrade"
            :disabled="isTrading"
          >
            <el-icon><Operation /></el-icon>
            启动跟单
          </el-button>
          <el-button
            type="danger"
            @click="handleStopTrade"
            :disabled="!isTrading"
          >
            <el-icon><Close /></el-icon>
            停止跟单
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计区域 -->
    <el-card class="stats-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item">
            <h4>总跟单次数</h4>
            <p class="stat-value">{{ stats.total_trades }}</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <h4>成功次数</h4>
            <p class="stat-value success">{{ stats.success_trades }}</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <h4>失败次数</h4>
            <p class="stat-value error">{{ stats.failed_trades }}</p>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 跟单据表格 -->
    <el-card class="table-card">
      <div class="trade-status">
        <el-tag :type="isTrading ? 'success' : 'warning'" size="medium">
          {{ isTrading ? '跟单中' : '未跟单' }}
        </el-tag>
      </div>

      <el-table
        v-loading="loading"
        :data="tradeRecords"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="id" label="ID" min-width="80"></el-table-column>
        <el-table-column prop="target_user" label="目标用户" min-width="200">
          <template #default="scope">
            <el-tooltip :content="scope.row.target_user" placement="top">
              <span class="truncate-text">{{ scope.row.target_user }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="side" label="方向" min-width="80">
          <template #default="scope">
            <el-tag :type="scope.row.side === 'BUY' ? 'success' : 'danger'">
              {{ scope.row.side === 'BUY' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="event_title" label="事件信息" min-width="300">
          <template #default="scope">
            <el-tooltip :content="scope.row.event_title || '无事件信息'" placement="top">
              <span class="truncate-text" style="max-width: 300px;">
                {{ scope.row.event_title || '无事件信息' }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" min-width="120"></el-table-column>
        <el-table-column prop="price" label="价格" min-width="120"></el-table-column>
        <el-table-column prop="size" label="数量" min-width="120"></el-table-column>
        <el-table-column prop="tx_hash" label="交易哈希" min-width="250">
          <template #default="scope">
            <el-tooltip :content="scope.row.tx_hash" placement="top">
              <span class="truncate-text">{{ scope.row.tx_hash }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="跟单状态" min-width="120">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间" min-width="180">
          <template #default="scope">
            {{ formatTimestamp(scope.row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Check, Operation, Close } from '@element-plus/icons-vue';
import request from '../utils/request';

// 表单引用
const configFormRef = ref(null);
// 加载状态
const loading = ref(false);
// 跟单状态
const isTrading = ref(false);
// 定时器
let statTimer = null;

// 跟单配置
const tradeConfig = reactive({
  target_user: '',
  wallet_address: '',
  private_key: ''
});

// 统计数据
const stats = reactive({
  total_trades: 0,
  success_trades: 0,
  failed_trades: 0
});

// 跟单据
const tradeRecords = ref([]);

// 页面卸载时清除定时器
onUnmounted(() => {
  if (statTimer) {
    clearInterval(statTimer);
    statTimer = null;
  }
});

// 格式化时间戳
const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
};

// 获取状态标签类型
const getStatusTagType = (status) => {
    switch (status) {
        case 'success':
        case 'matched':
            return 'success';
        case 'failed':
            return 'danger';
        case 'pending':
        case 'live':
            return 'warning';
        default:
            return 'info';
    }
};

// 获取状态文本
const getStatusText = (status) => {
    switch (status) {
        case 'success':
            return '成功';
        case 'failed':
            return '失败';
        case 'pending':
            return '待处理';
        case 'live':
            return '已挂单';
        case 'matched':
            return '已成交';
        default:
            return status;
    }
};

// 保存配置
const handleSaveConfig = async () => {
  try {
    await configFormRef.value.validate();
    await request.post('/api/v1/copy-trade/config', tradeConfig);
    ElMessage.success('配置保存成功');
  } catch (error) {
    console.error('保存配置失败:', error);
    if (error instanceof Error) {
      ElMessage.error(error.message);
    } else {
      ElMessage.error('保存配置失败');
    }
  }
};

// 启动跟单
const handleStartTrade = async () => {
  try {
    await request.post('/api/v1/copy-trade/start');
    isTrading.value = true;
    ElMessage.success('跟单已启动');
    
    // 立即获取一次统计数据
    fetchStats();
    fetchTradeRecords();
    
    // 设置定时器，每30秒更新一次数据
    statTimer = setInterval(() => {
      fetchStats();
      fetchTradeRecords();
    }, 30000);
  } catch (error) {
    console.error('启动跟单失败:', error);
    ElMessage.error('启动跟单失败');
  }
};

// 停止跟单
const handleStopTrade = async () => {
  try {
    await request.post('/api/v1/copy-trade/stop');
    isTrading.value = false;
    ElMessage.success('跟单已停止');
    
    // 清除定时器
    if (statTimer) {
      clearInterval(statTimer);
      statTimer = null;
    }
  } catch (error) {
    console.error('停止跟单失败:', error);
    ElMessage.error('停止跟单失败');
  }
};

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await request.get('/api/v1/copy-trade/stat');
    stats.total_trades = res.data.total_trades;
    stats.success_trades = res.data.success_trades;
    stats.failed_trades = res.data.failed_trades;
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

// 获取跟单据
const fetchTradeRecords = async () => {
  try {
    loading.value = true;
    const res = await request.get('/api/v1/copy-trade/records', { params: { limit: 50 } });
    tradeRecords.value = res.data.records;
  } catch (error) {
    console.error('获取跟单据失败:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.copy-trade-container {
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

.config-card {
  margin-bottom: 20px;
}

.stats-card {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.stat-item h4 {
  margin: 0 0 10px;
  font-size: 1rem;
  color: #606266;
}

.stat-value {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
  color: #303133;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.error {
  color: #f56c6c;
}

.table-card {
  margin-bottom: 20px;
}

.trade-status {
  margin-bottom: 15px;
}

.truncate-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-button) {
  margin-right: 8px;
}
</style>