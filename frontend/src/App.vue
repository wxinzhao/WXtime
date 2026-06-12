<template>
  <div class="app">
    <div class="header">微信定时消息管理系统</div>
    <div class="nav">
      <div class="nav-menu">
        <a :class="{ active: currentRoute === '/' }" href="/">首页</a>
        <a :class="{ active: currentRoute === '/tasks' }" href="/tasks">定时任务</a>
        <a :class="{ active: currentRoute === '/messages' }" href="/messages">消息管理</a>
      </div>
    </div>
    <div class="container">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => route.path)
</script>

<style scoped>
.app {
  min-height: 100vh;
  font-family: Arial, sans-serif;
}

.header {
  background: #1890ff;
  color: white;
  padding: 16px 24px;
  font-size: 18px;
  font-weight: 600;
}

.nav {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 24px;
}

.nav-menu {
  display: flex;
  gap: 24px;
  padding: 12px 0;
}

.nav-menu a {
  color: #333;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
}

.nav-menu a:hover {
  background: #f0f0f0;
}

.nav-menu a.active {
  background: #1890ff;
  color: white;
}

.container {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-item {
  margin-bottom: 16px;
}

.button-group {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.status-item {
  background: #fafafa;
  padding: 16px;
  border-radius: 4px;
  text-align: center;
}

.status-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.status-value {
  font-size: 20px;
  font-weight: 600;
}

.status-online { color: #52c41a; }
.status-offline { color: #ff4d4f; }
.status-warning { color: #faad14; }

.empty {
  text-align: center;
  padding: 48px;
  color: #999;
}

input, textarea, button {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

input:focus, textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

button {
  cursor: pointer;
  background: #1890ff;
  color: white;
  border: none;
}

button:hover {
  background: #40a9ff;
}

button:active {
  background: #096dd9;
}

textarea {
  resize: vertical;
  min-height: 100px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}
</style>