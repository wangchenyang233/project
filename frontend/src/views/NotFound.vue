<template>
  <div class="not-found-container">
    <h1>404</h1>
    <h2>页面不存在</h2>
    <p>抱歉，您访问的页面不存在或已被删除。</p>
    <el-button type="primary" @click="$router.push('/dashboard')">返回仪表盘</el-button>
  </div>
</template>

<script setup>
// 404页面组件的逻辑将在此处实现
</script>

<style scoped>
.not-found-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  text-align: center;
}

h1 {
  font-size: 10rem;
  color: #409eff;
  margin: 0;
}

h2 {
  font-size: 2rem;
  color: #606266;
  margin: 1rem 0;
}

p {
  font-size: 1rem;
  color: #909399;
  margin: 1rem 0 2rem;
}
</style>
