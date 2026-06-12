<template>
  <div class="home">
    <div class="card">
      <div class="card-title">系统状态</div>
      <div class="status-grid">
        <div class="status-item">
          <div class="status-label">微信连接</div>
          <div class="status-value" :class="status.wx_connected ? 'status-online' : 'status-offline'">
            {{ status.wx_connected ? '在线' : '离线' }}
          </div>
        </div>
        <div class="status-item">
          <div class="status-label">今日已发</div>
          <div class="status-value">{{ status.today_sent || 0 }} / {{ status.hourly_limit || 50 }}</div>
        </div>
        <div class="status-item">
          <div class="status-label">当前时段</div>
          <div class="status-value" :class="status.is_active_time ? 'status-online' : 'status-warning'">
            {{ status.is_active_time ? '活跃' : '休息中' }}
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">快速发送</div>
      <form @submit.prevent="handleSend" class="send-form">
        <div class="form-group">
          <label for="receiver">接收人</label>
          <input 
            type="text" 
            id="receiver" 
            v-model="form.receiver" 
            placeholder="微信昵称或备注" 
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label for="content">消息内容</label>
          <textarea 
            id="content" 
            v-model="form.content" 
            placeholder="请输入消息内容..." 
            rows="4" 
            class="form-textarea"
          ></textarea>
        </div>
        <div class="button-group">
          <button type="submit" class="btn btn-primary">发送</button>
          <button type="button" @click="form = { receiver: '', content: '' }" class="btn btn-secondary">重置</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { messageApi, statusApi } from '../api'

const form = ref({ receiver: '', content: '' })
const status = ref<any>({})

const handleSend = async () => {
  if (!form.value.receiver || !form.value.content) {
    alert('请填写完整信息')
    return
  }
  try {
    const res = await messageApi.send(form.value.receiver, form.value.content)
    if (res.data.status === 'success') {
      alert('发送成功')
      form.value = { receiver: '', content: '' }
    } else {
      alert('发送失败: ' + res.data.error)
    }
  } catch (error: any) {
    alert('发送失败: ' + (error.message || '未知错误'))
  }
}

const fetchStatus = async () => {
  try {
    const res = await statusApi.get()
    status.value = res.data
  } catch (error) {
    console.error('获取状态失败', error)
  }
}

onMounted(() => {
  fetchStatus()
  setInterval(fetchStatus, 10000)
})
</script>

<style scoped>
.send-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-textarea {
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  min-height: 120px;
  transition: all 0.3s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.btn-primary:active {
  background: #096dd9;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
  border: 1px solid #d9d9d9;
}

.btn-secondary:hover {
  background: #e6e6e6;
  border-color: #1890ff;
}

.btn-secondary:active {
  background: #d9d9d9;
}
</style>