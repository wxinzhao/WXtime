<template>
  <div class="tasks">
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">定时任务管理</h2>
        <div class="header-actions">
          <button class="btn btn-primary" @click="showDialog = true">
            <span class="btn-icon">+</span>
            新建任务
          </button>
          <button 
            class="btn btn-danger" 
            @click="deleteSelectedTasks" 
            :disabled="selectedTasks.length === 0"
          >
            <span class="btn-icon">✕</span>
            删除选中 ({{ selectedTasks.length }})
          </button>
        </div>
      </div>
      
      <div class="card-body">
        <div v-if="tasks.length === 0" class="empty-state">
          <div class="empty-icon">⏰</div>
          <h3>暂无定时任务</h3>
          <p>点击上方"新建任务"按钮创建您的第一个定时任务</p>
        </div>
        
        <table v-else class="task-table">
          <thead>
            <tr>
              <th width="40">
                <input 
                  type="checkbox" 
                  v-model="selectAllFlag" 
                  @change="toggleSelectAll"
                />
              </th>
              <th>任务名称</th>
              <th>接收人</th>
              <th>消息内容</th>
              <th>执行时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in tasks" :key="task.id" class="task-row">
              <td>
                <input 
                  type="checkbox" 
                  :checked="selectedTasks.includes(task.id)" 
                  @change="toggleSelect(task.id)"
                />
              </td>
              <td class="task-name">{{ task.name }}</td>
              <td>{{ task.receiver }}</td>
              <td class="task-content">{{ task.content }}</td>
              <td class="task-cron">{{ formatCron(task.cron) }}</td>
              <td>
                <button 
                  :class="['status-btn', task.enabled ? 'status-active' : 'status-inactive']"
                  @click="toggleTaskStatus(task)"
                >
                  <span class="status-icon">{{ task.enabled ? '✓' : '✕' }}</span>
                  {{ task.enabled ? '启用' : '禁用' }}
                </button>
              </td>
              <td class="task-actions">
                <button class="btn btn-secondary btn-sm" @click="editTask(task)">编辑</button>
                <button class="btn btn-danger btn-sm" @click="deleteTask(task.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新建/编辑任务对话框 -->
    <div v-if="showDialog" class="dialog-overlay">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑任务' : '新建任务' }}</h3>
          <button class="btn btn-close" @click="showDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label for="task-name">任务名称</label>
              <input 
                type="text" 
                id="task-name"
                v-model="form.name" 
                placeholder="请输入任务名称" 
                class="form-input"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="task-receiver">接收人</label>
              <input 
                type="text" 
                id="task-receiver"
                v-model="form.receiver" 
                placeholder="微信昵称或备注" 
                class="form-input"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="task-content">消息内容</label>
              <textarea 
                id="task-content"
                v-model="form.content" 
                placeholder="请输入消息内容" 
                rows="4" 
                class="form-textarea"
                required
              ></textarea>
            </div>
            
            <div class="form-group">
              <label>执行时间</label>
              <div class="time-selector">
                <div class="time-type">
                  <label for="time-type">执行类型</label>
                  <select 
                    id="time-type"
                    v-model="timeType" 
                    class="form-select"
                    @change="onTimeTypeChange"
                  >
                    <option value="daily">每天</option>
                    <option value="weekly">每周</option>
                    <option value="monthly">每月</option>
                    <option value="custom">自定义</option>
                  </select>
                </div>
                
                <!-- 每天 -->
                <div v-if="timeType === 'daily'" class="time-setting">
                  <label for="daily-time">时间</label>
                  <input 
                    type="time" 
                    id="daily-time"
                    v-model="timeSettings.daily" 
                    class="form-input"
                  />
                </div>
                
                <!-- 每周 -->
                <div v-if="timeType === 'weekly'" class="time-setting">
                  <div class="weekday-select">
                    <label>星期</label>
                    <div class="weekday-buttons">
                      <button 
                        v-for="day in weekdays" 
                        :key="day.value"
                        :class="['weekday-btn', timeSettings.weekly.days.includes(day.value) ? 'active' : '']"
                        @click="toggleWeekday(day.value)"
                      >
                        {{ day.label }}
                      </button>
                    </div>
                  </div>
                  <div class="time-input">
                    <label for="weekly-time">时间</label>
                    <input 
                      type="time" 
                      id="weekly-time"
                      v-model="timeSettings.weekly.time" 
                      class="form-input"
                    />
                  </div>
                </div>
                
                <!-- 每月 -->
                <div v-if="timeType === 'monthly'" class="time-setting">
                  <div class="day-input">
                    <label for="monthly-day">日期</label>
                    <input 
                      type="number" 
                      id="monthly-day"
                      v-model="timeSettings.monthly.day" 
                      class="form-input"
                      min="1" 
                      max="31"
                    />
                  </div>
                  <div class="time-input">
                    <label for="monthly-time">时间</label>
                    <input 
                      type="time" 
                      id="monthly-time"
                      v-model="timeSettings.monthly.time" 
                      class="form-input"
                    />
                  </div>
                </div>
                
                <!-- 自定义 -->
                <div v-if="timeType === 'custom'" class="time-setting">
                  <label for="custom-cron">Cron表达式</label>
                  <input 
                    type="text" 
                    id="custom-cron"
                    v-model="form.cron" 
                    placeholder="秒 分 时 日 月 周 (例: 0 0 9 * * 1-5)" 
                    class="form-input"
                    required
                  />
                  <div class="cron-hint">
                    <span class="hint-text">格式: 秒 分 时 日 月 周</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-group form-checkbox">
              <input 
                type="checkbox" 
                id="task-enabled"
                v-model="form.enabled" 
                class="checkbox-input"
              />
              <label for="task-enabled">启用任务</label>
            </div>
            
            <div class="button-group">
              <button type="submit" class="btn btn-primary">保存</button>
              <button type="button" @click="showDialog = false" class="btn btn-secondary">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { taskApi } from '../api'

const tasks = ref<any[]>([])
const showDialog = ref(false)
const isEdit = ref(false)
const currentId = ref(0)
const selectedTasks = ref<number[]>([])

const selectAllFlag = computed({
  get: () => tasks.value.length > 0 && selectedTasks.value.length === tasks.value.length,
  set: (value) => toggleSelectAll({ target: { checked: value } })
})

const form = ref({
  name: '',
  receiver: '',
  content: '',
  cron: '0 0 9 * * *',
  enabled: true
})

// 时间类型
const timeType = ref('daily')

// 时间设置
const timeSettings = ref({
  daily: '09:00',
  weekly: {
    days: ['1'], // 默认周一
    time: '09:00'
  },
  monthly: {
    day: 1,
    time: '09:00'
  }
})

// 星期选项
const weekdays = [
  { label: '周一', value: '1' },
  { label: '周二', value: '2' },
  { label: '周三', value: '3' },
  { label: '周四', value: '4' },
  { label: '周五', value: '5' },
  { label: '周六', value: '6' },
  { label: '周日', value: '0' }
]

const fetchTasks = async () => {
  try {
    const res = await taskApi.list()
    console.log('任务列表API响应:', res)
    // 直接使用 res.data，因为后端返回的是数组
    tasks.value = res.data || []
    console.log('任务列表:', tasks.value)
    // 清空选中状态
    selectedTasks.value = []
  } catch (error) {
    console.error('获取任务列表失败', error)
  }
}

const handleSubmit = async () => {
  // 生成Cron表达式
  generateCronExpression()
  
  if (!form.value.name) {
    alert('请填写任务名称')
    return
  }
  if (!form.value.receiver) {
    alert('请填写接收人')
    return
  }
  if (!form.value.content) {
    alert('请填写消息内容')
    return
  }
  if (!form.value.cron) {
    alert('请设置执行时间')
    return
  }
  
  try {
    if (isEdit.value) {
      await taskApi.update(currentId.value, form.value)
      alert('任务更新成功')
    } else {
      await taskApi.create(form.value)
      alert('任务创建成功')
    }
    showDialog.value = false
    fetchTasks()
    resetForm()
  } catch (error) {
    console.error('操作失败', error)
    alert('操作失败，请重试')
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    receiver: '',
    content: '',
    cron: '0 0 9 * * *',
    enabled: true
  }
  timeType.value = 'daily'
  timeSettings.value = {
    daily: '09:00',
    weekly: {
      days: ['1'],
      time: '09:00'
    },
    monthly: {
      day: 1,
      time: '09:00'
    }
  }
  isEdit.value = false
  currentId.value = 0
}

const editTask = (row: any) => {
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    name: row.name,
    receiver: row.receiver,
    content: row.content,
    cron: row.cron,
    enabled: row.enabled
  }
  
  // 解析Cron表达式到时间设置
  parseCronExpression(row.cron)
  showDialog.value = true
}

const deleteTask = async (id: number) => {
  if (!confirm('确定删除此任务？')) return
  try {
    await taskApi.delete(id)
    alert('删除成功')
    fetchTasks()
  } catch (error) {
    alert('删除失败')
  }
}

const deleteSelectedTasks = async () => {
  if (selectedTasks.value.length === 0) return
  
  if (!confirm(`确定删除选中的 ${selectedTasks.value.length} 个任务？`)) return
  
  try {
    for (const id of selectedTasks.value) {
      await taskApi.delete(id)
    }
    alert('删除成功')
    fetchTasks()
  } catch (error) {
    alert('删除失败')
  }
}

const toggleTaskStatus = async (task: any) => {
  try {
    await taskApi.update(task.id, { ...task, enabled: !task.enabled })
    alert('状态更新成功')
    fetchTasks()
  } catch (error) {
    alert('状态更新失败')
  }
}

const toggleSelect = (id: number) => {
  const index = selectedTasks.value.indexOf(id)
  if (index > -1) {
    selectedTasks.value.splice(index, 1)
  } else {
    selectedTasks.value.push(id)
  }
}

const toggleSelectAll = (event: any) => {
  const checked = event.target.checked
  if (checked) {
    selectedTasks.value = tasks.value.map(task => task.id)
  } else {
    selectedTasks.value = []
  }
}

const toggleWeekday = (day: string) => {
  const index = timeSettings.value.weekly.days.indexOf(day)
  if (index > -1) {
    timeSettings.value.weekly.days.splice(index, 1)
  } else {
    timeSettings.value.weekly.days.push(day)
  }
}

const onTimeTypeChange = () => {
  // 根据时间类型生成Cron表达式
  generateCronExpression()
}

const generateCronExpression = () => {
  switch (timeType.value) {
    case 'daily': {
      const [hour, minute] = timeSettings.value.daily.split(':')
      form.value.cron = `0 ${minute} ${hour} * * *`
      break
    }
    case 'weekly': {
      const [hour, minute] = timeSettings.value.weekly.time.split(':')
      const days = timeSettings.value.weekly.days.sort().join(',')
      form.value.cron = `0 ${minute} ${hour} * * ${days}`
      break
    }
    case 'monthly': {
      const [hour, minute] = timeSettings.value.monthly.time.split(':')
      const day = timeSettings.value.monthly.day
      form.value.cron = `0 ${minute} ${hour} ${day} * *`
      break
    }
    // custom 类型保持用户输入
  }
}

const parseCronExpression = (cron: string) => {
  const parts = cron.split(' ')
  if (parts.length < 6) return
  
  const [second, minute, hour, dayOfMonth, month, dayOfWeek] = parts
  
  // 尝试解析为不同类型
  if (dayOfWeek === '*' && dayOfMonth === '*') {
    // 每天
    timeType.value = 'daily'
    timeSettings.value.daily = `${hour}:${minute}`
  } else if (dayOfMonth === '*') {
    // 每周
    timeType.value = 'weekly'
    timeSettings.value.weekly.time = `${hour}:${minute}`
    timeSettings.value.weekly.days = dayOfWeek.split(',').filter(d => d)
  } else if (dayOfWeek === '*') {
    // 每月
    timeType.value = 'monthly'
    timeSettings.value.monthly.day = parseInt(dayOfMonth)
    timeSettings.value.monthly.time = `${hour}:${minute}`
  } else {
    // 自定义
    timeType.value = 'custom'
  }
}

const formatCron = (cron: string): string => {
  const parts = cron.split(' ')
  if (parts.length >= 6) {
    const [second, minute, hour, dayOfMonth, month, dayOfWeek] = parts
    
    if (dayOfWeek === '*' && dayOfMonth === '*') {
      return `每天 ${hour}:${minute.padStart(2, '0')}`
    } else if (dayOfMonth === '*') {
      const days = dayOfWeek.split(',').map(d => {
        const dayMap: any = {
          '0': '周日',
          '1': '周一',
          '2': '周二',
          '3': '周三',
          '4': '周四',
          '5': '周五',
          '6': '周六'
        }
        return dayMap[d] || d
      })
      return `${days.join('、')} ${hour}:${minute.padStart(2, '0')}`
    } else if (dayOfWeek === '*') {
      return `每月${dayOfMonth}日 ${hour}:${minute.padStart(2, '0')}`
    }
  }
  return cron
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.tasks {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  color: white;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.card-body {
  padding: 24px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
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

.btn-danger {
  background: #ff4d4f;
  color: white;
}

.btn-danger:hover {
  background: #ff7875;
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);
}

.btn-danger:disabled {
  background: #ffccc7;
  cursor: not-allowed;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  margin-right: 8px;
}

.btn-icon {
  font-size: 16px;
  font-weight: bold;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #666;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.task-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.task-table th,
.task-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.task-table th {
  background: #fafafa;
  font-weight: 600;
  font-size: 14px;
  color: #666;
  position: sticky;
  top: 0;
  z-index: 10;
}

.task-row:hover {
  background: #f9f9f9;
}

.task-name {
  font-weight: 500;
  color: #333;
}

.task-content {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #666;
}

.task-cron {
  color: #1890ff;
  font-family: monospace;
}

.status-btn {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-icon {
  font-size: 10px;
  font-weight: bold;
  display: inline-block;
  width: 12px;
  height: 12px;
  line-height: 12px;
  text-align: center;
  border-radius: 50%;
}

.status-active {
  background: #f6ffed;
  color: #52c41a;
  border-color: #b7eb8f;
}

.status-active:hover {
  background: #d9f7be;
}

.status-inactive {
  background: #fff1f0;
  color: #ff4d4f;
  border-color: #ffccc7;
}

.status-inactive:hover {
  background: #ffccc7;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.dialog {
  background: white;
  border-radius: 12px;
  width: 550px;
  max-width: 90%;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: dialogFadeIn 0.3s ease;
}

@keyframes dialogFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.btn-close:hover {
  background: #f0f0f0;
  color: #333;
}

.dialog-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  min-height: 120px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.checkbox-input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.time-selector {
  margin-top: 12px;
}

.time-type {
  margin-bottom: 16px;
}

.time-setting {
  margin-top: 16px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.weekday-select {
  margin-bottom: 16px;
}

.weekday-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.weekday-btn {
  background: #f0f0f0;
  border: 1px solid #d9d9d9;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.weekday-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.weekday-btn.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.time-input,
.day-input {
  margin-top: 12px;
}

.cron-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f6f6f6;
  border-radius: 4px;
  font-size: 12px;
  color: #999;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .task-table {
    font-size: 12px;
  }
  
  .task-table th,
  .task-table td {
    padding: 12px;
  }
  
  .weekday-buttons {
    flex-direction: column;
  }
  
  .weekday-btn {
    width: 100%;
    text-align: center;
  }
}
</style>