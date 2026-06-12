<template>
  <div class="messages">
    <div class="card">
      <div class="card-title">
        <span>消息记录</span>
        <div class="card-actions">
          <button 
            class="btn btn-danger" 
            @click="deleteSelected" 
            :disabled="selectedMessages.length === 0"
          >
            删除选中 ({{ selectedMessages.length }})
          </button>
          <button class="btn btn-secondary" @click="selectAll">
            {{ isAllSelected ? '取消全选' : '全选' }}
          </button>
        </div>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th width="40">
              <input 
                type="checkbox" 
                v-model="isAllSelected" 
                @change="toggleSelectAll"
              />
            </th>
            <th>ID</th>
            <th>接收人</th>
            <th>内容</th>
            <th>状态</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="msg in messages" :key="msg.id" :class="{ selected: selectedMessages.includes(msg.id) }">
            <td>
              <input 
                type="checkbox" 
                :checked="selectedMessages.includes(msg.id)" 
                @change="toggleSelect(msg.id)"
              />
            </td>
            <td>{{ msg.id }}</td>
            <td>{{ msg.receiver }}</td>
            <td>{{ msg.content }}</td>
            <td><span :class="'status-' + msg.status">{{ msg.status }}</span></td>
            <td>{{ new Date(msg.created_at).toLocaleString() }}</td>
            <td>
              <button class="btn btn-danger btn-sm" @click="deleteMessage(msg.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="messages.length === 0" class="empty">暂无消息记录</div>
      <div v-else class="count">共 {{ messages.length }} 条消息</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { messageApi } from '../api'

const messages = ref<any[]>([])
const selectedMessages = ref<number[]>([])

const isAllSelected = computed({
  get: () => messages.value.length > 0 && selectedMessages.value.length === messages.value.length,
  set: (value) => toggleSelectAll({ target: { checked: value } })
})

const fetchMessages = async () => {
  try {
    console.log('开始获取消息列表...')
    const res = await messageApi.list()
    console.log('API 响应:', res)
    console.log('响应数据:', res.data)
    // 直接使用 res.data，因为 API 返回的是数组
    messages.value = res.data || []
    console.log('消息列表:', messages.value)
    // 清空选中状态
    selectedMessages.value = []
  } catch (error) {
    console.error('获取消息列表失败', error)
  }
}

const deleteMessage = async (id: number) => {
  if (confirm('确定要删除这条消息吗？')) {
    try {
      await messageApi.delete(id)
      alert('删除成功')
      fetchMessages()
    } catch (error) {
      console.error('删除失败', error)
      alert('删除失败')
    }
  }
}

const toggleSelect = (id: number) => {
  const index = selectedMessages.value.indexOf(id)
  if (index > -1) {
    selectedMessages.value.splice(index, 1)
  } else {
    selectedMessages.value.push(id)
  }
}

const toggleSelectAll = (event: any) => {
  const checked = event.target.checked
  if (checked) {
    selectedMessages.value = messages.value.map(msg => msg.id)
  } else {
    selectedMessages.value = []
  }
}

const selectAll = () => {
  if (isAllSelected.value) {
    selectedMessages.value = []
  } else {
    selectedMessages.value = messages.value.map(msg => msg.id)
  }
}

const deleteSelected = async () => {
  if (selectedMessages.value.length === 0) return
  
  if (confirm(`确定要删除选中的 ${selectedMessages.value.length} 条消息吗？`)) {
    try {
      // 逐个删除消息
      for (const id of selectedMessages.value) {
        await messageApi.delete(id)
      }
      alert('删除成功')
      fetchMessages()
    } catch (error) {
      console.error('删除失败', error)
      alert('删除失败')
    }
  }
}

onMounted(() => {
  fetchMessages()
  setInterval(fetchMessages, 30000)
})
</script>

<style scoped>
.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.table th,
.table td {
  padding: 12px;
  border: 1px solid #e8e8e8;
  text-align: left;
}

.table th {
  background: #fafafa;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
}

.table tr:hover {
  background: #f5f5f5;
}

.table tr.selected {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
}

.status-success { color: #52c41a; font-weight: 500; }
.status-failed { color: #ff4d4f; font-weight: 500; }
.status-pending { color: #1890ff; font-weight: 500; }

.empty {
  text-align: center;
  padding: 48px;
  color: #999;
  background: #fafafa;
  border-radius: 4px;
  margin-top: 16px;
}

.count {
  text-align: right;
  margin-top: 12px;
  color: #666;
  font-size: 14px;
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
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

.btn-danger {
  background: #ff4d4f;
  color: white;
}

.btn-danger:hover {
  background: #ff7875;
  box-shadow: 0 2px 8px rgba(255, 77, 79, 0.3);
}

.btn-danger:disabled {
  background: #ffccc7;
  cursor: not-allowed;
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

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
}
</style>