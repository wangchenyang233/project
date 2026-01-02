<template>
  <div class="activity-monitor-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>持续监控</h2>
    </div>

    <!-- 配置区域 -->
    <el-card class="config-card">
      <el-form :model="monitorConfig" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用户地址">
              <el-input
                v-model="monitorConfig.user_address"
                placeholder="请输入用户地址"
                clearable
              ></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="轮询间隔">
              <el-select
                v-model="monitorConfig.interval"
                placeholder="选择轮询间隔"
              >
                <el-option label="5秒" value="5"></el-option>
                <el-option label="10秒" value="10"></el-option>
                <el-option label="30秒" value="30"></el-option>
                <el-option label="1分钟" value="60"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleStartMonitor"
            :disabled="isMonitoring"
          >
            <el-icon><VideoPlay /></el-icon>
            启动监控
          </el-button>
          <el-button
            type="danger"
            @click="handleStopMonitor"
            :disabled="!isMonitoring"
          >
            <el-icon><VideoPause /></el-icon>
            停止监控
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 日志表格 -->
    <el-card class="table-card">
      <div class="monitor-status">
        <el-tag :type="isMonitoring ? 'success' : 'warning'" size="medium">
          {{ isMonitoring ? '监控中' : '未监控' }}
        </el-tag>
        <span v-if="isMonitoring" class="monitor-info">
          轮询间隔: {{ monitorConfig.interval }}秒
        </span>
      </div>

      <el-table
        v-loading="loading"
        :data="monitorLogs"
        style="width: 100%"
        stripe
        :max-height="500"
      >
        <el-table-column prop="timestamp" label="时间" min-width="180">
          <template #default="scope">
            {{ formatTimestamp(scope.row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" min-width="100">
          <template #default="scope">
            <el-tag
              :type="
                scope.row.level === 'info' ? 'info' :
                scope.row.level === 'warning' ? 'warning' :
                scope.row.level === 'error' ? 'danger' : 'success'
              "
            >
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="日志信息" min-width="400">
          <template #default="scope">
            <div class="log-message">
              {{ scope.row.message }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="user_address" label="用户地址" min-width="200">
          <template #default="scope">
            <el-tooltip :content="scope.row.user_address" placement="top">
              <span class="truncate-text">{{ scope.row.user_address }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <!-- 清空日志按钮 -->
      <div class="clear-logs">
        <el-button type="warning" size="small" @click="handleClearLogs">
          <el-icon><Delete /></el-icon>
          清空日志
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { VideoPlay, VideoPause, Delete } from '@element-plus/icons-vue';
import request from '../utils/request';

// 加载状态
const loading = ref(false);
// 监控状态
const isMonitoring = ref(false);
// 定时器
let monitorTimer = null;
// 监控日志
const monitorLogs = ref([]);

// 监控配置
const monitorConfig = reactive({
  user_address: '',
  interval: '10', // 默认10秒
  task_id: '' // 任务ID
});

// 页面卸载时清除定时器
onUnmounted(() => {
  if (monitorTimer) {
    clearInterval(monitorTimer);
    monitorTimer = null;
  }
});

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000);
  return date.toLocaleString();
};

// 启动监控
const handleStartMonitor = async () => {
  if (!monitorConfig.user_address) {
    ElMessage.warning('请输入用户地址');
    return;
  }

  try {
    loading.value = true;
    // 调用后端启动监控API
    const res = await request.post('/api/v1/monitor/start', {
      user: monitorConfig.user_address,
      poll_seconds: parseInt(monitorConfig.interval)
    });
    
    // 保存任务ID
    monitorConfig.task_id = res.data.task_id;
    isMonitoring.value = true;
    ElMessage.success('监控已启动');
    
    // 立即获取一次日志
    fetchLogs();
    
    // 设置定时器
    monitorTimer = setInterval(() => {
      fetchLogs();
    }, monitorConfig.interval * 1000);
  } catch (error) {
    console.error('启动监控失败:', error);
    ElMessage.error('启动监控失败');
  } finally {
    loading.value = false;
  }
};

// 停止监控
const handleStopMonitor = async () => {
  if (!monitorConfig.task_id) {
    isMonitoring.value = false;
    return;
  }

  try {
    loading.value = true;
    // 调用后端停止监控API
    await request.post('/api/v1/monitor/stop', {
      task_id: monitorConfig.task_id
    });
    
    isMonitoring.value = false;
    monitorConfig.task_id = '';
    ElMessage.success('监控已停止');
    
    // 清除定时器
    if (monitorTimer) {
      clearInterval(monitorTimer);
      monitorTimer = null;
    }
  } catch (error) {
    console.error('停止监控失败:', error);
    ElMessage.error('停止监控失败');
  } finally {
    loading.value = false;
  }
};

// 获取日志
const fetchLogs = async () => {
  if (!monitorConfig.task_id) {
    return;
  }

  try {
    loading.value = true;
    const res = await request.get('/api/v1/monitor/logs', {
      params: { task_id: monitorConfig.task_id }
    });
    monitorLogs.value = res.data.logs || [];
  } catch (error) {
    console.error('获取日志失败:', error);
    ElMessage.error('获取日志失败');
  } finally {
    loading.value = false;
  }
};

// 清空日志
const handleClearLogs = () => {
  monitorLogs.value = [];
  ElMessage.success('日志已清空');
};
</script>

<style scoped>
.activity-monitor-container {
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

.table-card {
  margin-bottom: 20px;
}

.monitor-status {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.monitor-info {
  margin-left: 10px;
  color: #606266;
  font-size: 14px;
}

.log-message {
  word-break: break-all;
  white-space: pre-wrap;
}

.truncate-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.clear-logs {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

:deep(.el-button) {
  margin-right: 8px;
}
</style>