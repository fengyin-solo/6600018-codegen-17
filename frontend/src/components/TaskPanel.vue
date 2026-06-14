<template>
  <div class="flex h-full">
    <div class="w-80 bg-gray-900 p-4 flex flex-col gap-3 border-r border-gray-800">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-bold text-amber-400">复核任务管理</h2>
        <button @click="showCreate = true" class="bg-amber-500 text-black px-3 py-1 rounded text-sm font-medium hover:bg-amber-400">
          + 新建任务
        </button>
      </div>

      <div class="space-y-2">
        <select v-model="filterStatus" @change="applyFilters" class="w-full bg-gray-800 rounded px-3 py-2 text-sm">
          <option value="">全部状态</option>
          <option value="pending">待分配</option>
          <option value="assigned">已分配</option>
          <option value="in_progress">进行中</option>
          <option value="completed">已完成</option>
        </select>
        <input v-model="filterAssignee" @input="applyFilters" placeholder="按分配人筛选..." class="w-full bg-gray-800 rounded px-3 py-2 text-sm" />
      </div>

      <div class="bg-gray-800 rounded p-3 space-y-2">
        <div class="text-sm font-medium text-gray-300">进度统计</div>
        <div class="grid grid-cols-5 gap-1 text-center text-xs">
          <div>
            <div class="text-lg font-bold text-gray-300">{{ taskStore.progress.total }}</div>
            <div class="text-gray-500">总计</div>
          </div>
          <div>
            <div class="text-lg font-bold text-gray-400">{{ taskStore.progress.pending }}</div>
            <div class="text-gray-500">待分配</div>
          </div>
          <div>
            <div class="text-lg font-bold text-blue-400">{{ taskStore.progress.assigned }}</div>
            <div class="text-gray-500">已分配</div>
          </div>
          <div>
            <div class="text-lg font-bold text-yellow-400">{{ taskStore.progress.inProgress }}</div>
            <div class="text-gray-500">进行中</div>
          </div>
          <div>
            <div class="text-lg font-bold text-green-400">{{ taskStore.progress.completed }}</div>
            <div class="text-gray-500">已完成</div>
          </div>
        </div>
        <div class="w-full bg-gray-700 rounded-full h-2 overflow-hidden flex">
          <div v-if="taskStore.progress.total > 0" class="bg-gray-400" :style="{ width: (taskStore.progress.pending / taskStore.progress.total * 100) + '%' }"></div>
          <div v-if="taskStore.progress.total > 0" class="bg-blue-500" :style="{ width: (taskStore.progress.assigned / taskStore.progress.total * 100) + '%' }"></div>
          <div v-if="taskStore.progress.total > 0" class="bg-yellow-500" :style="{ width: (taskStore.progress.inProgress / taskStore.progress.total * 100) + '%' }"></div>
          <div v-if="taskStore.progress.total > 0" class="bg-green-500" :style="{ width: (taskStore.progress.completed / taskStore.progress.total * 100) + '%' }"></div>
        </div>
        <div v-if="taskStore.progress.totalResults > 0" class="text-xs text-gray-400 flex justify-between">
          <span>记录进度</span>
          <span class="text-green-400">{{ taskStore.progress.completedResults }} / {{ taskStore.progress.totalResults }} 条</span>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto space-y-2">
        <div v-for="task in displayedTasks" :key="task.id" @click="selectTask(task.id)"
          class="bg-gray-800 rounded p-3 cursor-pointer text-sm transition-all"
          :class="taskStore.selectedTaskId === task.id ? 'ring-1 ring-amber-500 bg-gray-750' : 'hover:bg-gray-750'">
          <div class="flex justify-between items-start">
            <span class="font-medium text-white">{{ task.title }}</span>
            <span class="text-xs px-2 py-0.5 rounded" :class="statusClass(task.status)">
              {{ statusLabel(task.status) }}
            </span>
          </div>
          <div class="text-xs text-gray-400 mt-1 flex items-center gap-2">
            <span :class="scopeTypeClass(task.scopeType) + ' px-1.5 py-0.5 rounded'">{{ scopeTypeLabel(task.scopeType) }}</span>
            <span v-if="task.chapter">· {{ task.chapter }}</span>
          </div>
          <div class="text-xs text-gray-500 mt-1 flex justify-between">
            <span>{{ getResultCount(task) }} 条记录</span>
            <span>{{ task.assignee || '未分配' }}</span>
          </div>
        </div>
        <div v-if="!displayedTasks.length" class="text-gray-500 text-sm text-center py-8">
          暂无任务
        </div>
      </div>
    </div>

    <div class="flex-1 bg-gray-950 p-6 overflow-y-auto">
      <div v-if="taskStore.selectedTask" class="max-w-2xl mx-auto space-y-6">
        <div class="bg-gray-900 rounded-lg p-6">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="text-xl font-bold text-white">{{ taskStore.selectedTask.title }}</h2>
              <div class="mt-2 flex items-center gap-2 text-sm">
                <span :class="scopeTypeClass(taskStore.selectedTask.scopeType) + ' px-2 py-0.5 rounded'">
                  {{ scopeTypeLabel(taskStore.selectedTask.scopeType) }}
                </span>
                <span v-if="taskStore.selectedTask.chapter" class="text-gray-400">
                  章节: {{ taskStore.selectedTask.chapter }}
                </span>
              </div>
            </div>
            <span class="text-sm px-3 py-1 rounded" :class="statusClass(taskStore.selectedTask.status)">
              {{ statusLabel(taskStore.selectedTask.status) }}
            </span>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-500">文档:</span>
              <span class="text-gray-300 ml-2">{{ getDocName(taskStore.selectedTask.documentId) }}</span>
            </div>
            <div>
              <span class="text-gray-500">范围:</span>
              <span class="text-gray-300 ml-2">{{ scopeTypeLabel(taskStore.selectedTask.scopeType) }}</span>
            </div>
            <div>
              <span class="text-gray-500">记录数:</span>
              <span class="text-gray-300 ml-2">{{ getResultCount(taskStore.selectedTask) }} 条</span>
            </div>
            <div>
              <span class="text-gray-500">分配给:</span>
              <span class="text-gray-300 ml-2">{{ taskStore.selectedTask.assignee || '未分配' }}</span>
            </div>
            <div>
              <span class="text-gray-500">创建时间:</span>
              <span class="text-gray-300 ml-2">{{ formatDate(taskStore.selectedTask.createdAt) }}</span>
            </div>
            <div v-if="taskStore.selectedTask.completedAt">
              <span class="text-gray-500">完成时间:</span>
              <span class="text-gray-300 ml-2">{{ formatDate(taskStore.selectedTask.completedAt) }}</span>
            </div>
          </div>
        </div>

        <div class="bg-gray-900 rounded-lg p-6">
          <h3 class="text-amber-300 font-bold mb-4">任务操作</h3>
          <div class="flex flex-wrap gap-3">
            <button v-if="taskStore.selectedTask.status === 'pending'" @click="doAssign" class="bg-blue-600 px-4 py-2 rounded text-sm hover:bg-blue-500 transition-colors">
              分配任务
            </button>
            <button v-if="taskStore.selectedTask.status === 'assigned'" @click="doStart" class="bg-yellow-600 px-4 py-2 rounded text-sm hover:bg-yellow-500 transition-colors">
              开始处理
            </button>
            <button v-if="taskStore.selectedTask.status === 'in_progress'" @click="doComplete" class="bg-green-600 px-4 py-2 rounded text-sm hover:bg-green-500 transition-colors">
              标记完成
            </button>
            <button @click="showAssignDialog = true" class="bg-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-600 transition-colors">
              重新分配
            </button>
            <button @click="doDelete" class="bg-red-700 px-4 py-2 rounded text-sm hover:bg-red-600 transition-colors">
              删除任务
            </button>
          </div>
        </div>

        <div class="bg-gray-900 rounded-lg p-6">
          <h3 class="text-amber-300 font-bold mb-4">待校对内容 ({{ taskResults.length }} 条)</h3>
          <div v-if="taskResults.length" class="space-y-2">
            <div v-for="r in taskResults" :key="r.id" class="bg-gray-800 rounded p-3 text-sm">
              <div class="flex justify-between">
                <span class="text-white">{{ r.text }}</span>
                <span class="text-xs px-2 py-0.5 rounded"
                  :class="r.confidence > 0.9 ? 'bg-green-900 text-green-400' : 'bg-yellow-900 text-yellow-400'">
                  {{ (r.confidence * 100).toFixed(0) }}%
                </span>
              </div>
              <div class="text-xs text-gray-400 mt-1">
                简体: {{ convertVariant(r.text) }}
              </div>
              <div v-if="r.corrected" class="text-xs text-green-400 mt-1">
                已校正: {{ r.corrected }}
              </div>
            </div>
          </div>
          <div v-else class="text-gray-500 text-sm">
            暂无待校对内容
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center h-full text-gray-600">
        请选择一个任务查看详情
      </div>
    </div>

    <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCreate = false">
      <div class="bg-gray-900 rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-amber-400 mb-4">新建复核任务</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-300 mb-1">任务标题</label>
            <input v-model="newTask.title" class="w-full bg-gray-800 rounded px-3 py-2 text-sm" placeholder="请输入任务标题" />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">关联文档</label>
            <select v-model="newTask.documentId" class="w-full bg-gray-800 rounded px-3 py-2 text-sm">
              <option v-for="d in ocrStore.documents" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">任务范围</label>
            <div class="space-y-2">
              <label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-800 p-2 rounded">
                <input type="radio" v-model="newTask.scopeType" value="document" class="accent-amber-500" />
                <span>整文档</span>
                <span class="text-gray-500 text-xs">({{ getDocResultCount(newTask.documentId) }} 条记录)</span>
              </label>
              <label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-800 p-2 rounded">
                <input type="radio" v-model="newTask.scopeType" value="chapter" class="accent-amber-500" />
                <span>按章节</span>
              </label>
              <label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-800 p-2 rounded">
                <input type="radio" v-model="newTask.scopeType" value="results" class="accent-amber-500" />
                <span>指定记录</span>
              </label>
            </div>
          </div>
          <div v-if="newTask.scopeType === 'chapter'">
            <label class="block text-sm text-gray-300 mb-1">章节名称</label>
            <input v-model="newTask.chapter" class="w-full bg-gray-800 rounded px-3 py-2 text-sm" placeholder="如：第1-3章" />
          </div>
          <div v-if="newTask.scopeType === 'results'">
            <label class="block text-sm text-gray-300 mb-1">选择 OCR 记录</label>
            <div class="bg-gray-800 rounded p-2 max-h-48 overflow-y-auto space-y-1">
              <label v-for="r in getDocResults(newTask.documentId)" :key="r.id"
                class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-700 p-1 rounded">
                <input type="checkbox" :value="r.id" v-model="newTask.resultIds" class="accent-amber-500" />
                <span class="flex-1">{{ r.text }}</span>
                <span class="text-xs text-gray-500">{{ (r.confidence * 100).toFixed(0) }}%</span>
              </label>
            </div>
            <div class="text-xs text-gray-500 mt-1">已选 {{ newTask.resultIds.length }} 条</div>
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">分配给 (可选)</label>
            <input v-model="newTask.assignee" class="w-full bg-gray-800 rounded px-3 py-2 text-sm" placeholder="请输入负责人姓名" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button @click="showCreate = false" class="px-4 py-2 rounded text-sm bg-gray-700 hover:bg-gray-600 transition-colors">取消</button>
          <button @click="submitCreate" :disabled="!canCreate"
            class="px-4 py-2 rounded text-sm bg-amber-500 text-black hover:bg-amber-400 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            创建
          </button>
        </div>
      </div>
    </div>

    <div v-if="showAssignDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showAssignDialog = false">
      <div class="bg-gray-900 rounded-lg p-6 w-full max-w-sm mx-4">
        <h3 class="text-lg font-bold text-amber-400 mb-4">分配任务</h3>
        <div>
          <label class="block text-sm text-gray-300 mb-1">分配给</label>
          <input v-model="assignName" class="w-full bg-gray-800 rounded px-3 py-2 text-sm" placeholder="请输入负责人姓名" />
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button @click="showAssignDialog = false" class="px-4 py-2 rounded text-sm bg-gray-700 hover:bg-gray-600 transition-colors">取消</button>
          <button @click="submitAssign" :disabled="!assignName.trim()"
            class="px-4 py-2 rounded text-sm bg-amber-500 text-black hover:bg-amber-400 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useTaskStore } from '../store/task'
import { useOcrStore } from '../store/ocr'
import type { TaskStatus, TaskScopeType, ReviewTask, OCRResult } from '../types'

const taskStore = useTaskStore()
const ocrStore = useOcrStore()

const showCreate = ref(false)
const showAssignDialog = ref(false)
const assignName = ref('')
const filterStatus = ref('')
const filterAssignee = ref('')

const newTask = ref({
  title: '',
  documentId: '',
  scopeType: 'document' as TaskScopeType,
  chapter: '',
  resultIds: [] as string[],
  assignee: '',
})

const canCreate = computed(() => {
  if (!newTask.value.title.trim()) return false
  if (!newTask.value.documentId) return false
  if (newTask.value.scopeType === 'chapter' && !newTask.value.chapter.trim()) return false
  if (newTask.value.scopeType === 'results' && newTask.value.resultIds.length === 0) return false
  return true
})

const displayedTasks = computed(() => {
  let tasks = taskStore.tasks
  if (filterStatus.value) {
    tasks = tasks.filter(t => t.status === filterStatus.value)
  }
  if (filterAssignee.value) {
    tasks = tasks.filter(t => t.assignee?.includes(filterAssignee.value))
  }
  return tasks
})

const taskResults = computed<OCRResult[]>(() => {
  if (!taskStore.selectedTask) return []
  const doc = ocrStore.documents.find(d => d.id === taskStore.selectedTask?.documentId)
  if (!doc) return []

  const resultIds = taskStore.selectedTask.resultIds
  if (resultIds && resultIds.length > 0) {
    const idSet = new Set(resultIds)
    return doc.results.filter(r => idSet.has(r.id))
  }

  return []
})

function getDocName(docId: string): string {
  const doc = ocrStore.documents.find(d => d.id === docId)
  return doc?.name || docId
}

function getDocResultCount(docId: string): number {
  const doc = ocrStore.documents.find(d => d.id === docId)
  return doc?.results.length || 0
}

function getDocResults(docId: string): OCRResult[] {
  const doc = ocrStore.documents.find(d => d.id === docId)
  return doc?.results || []
}

function getResultCount(task: ReviewTask): number {
  if (task.resultCount && task.resultCount > 0) {
    return task.resultCount
  }
  if (task.resultIds && task.resultIds.length > 0) {
    return task.resultIds.length
  }
  const doc = ocrStore.documents.find(d => d.id === task.documentId)
  if (doc && task.scopeType === 'document') {
    return doc.results.length
  }
  return 0
}

function statusClass(status: TaskStatus): string {
  switch (status) {
    case 'pending': return 'bg-gray-700 text-gray-300'
    case 'assigned': return 'bg-blue-900 text-blue-300'
    case 'in_progress': return 'bg-yellow-900 text-yellow-300'
    case 'completed': return 'bg-green-900 text-green-300'
    default: return 'bg-gray-700 text-gray-300'
  }
}

function statusLabel(status: TaskStatus): string {
  switch (status) {
    case 'pending': return '待分配'
    case 'assigned': return '已分配'
    case 'in_progress': return '进行中'
    case 'completed': return '已完成'
    default: return status
  }
}

function scopeTypeClass(scopeType: TaskScopeType): string {
  switch (scopeType) {
    case 'document': return 'text-purple-400 bg-purple-900/40'
    case 'chapter': return 'text-cyan-400 bg-cyan-900/40'
    case 'results': return 'text-pink-400 bg-pink-900/40'
    default: return 'text-gray-400 bg-gray-800'
  }
}

function scopeTypeLabel(scopeType: TaskScopeType): string {
  switch (scopeType) {
    case 'document': return '整文档'
    case 'chapter': return '按章节'
    case 'results': return '指定记录'
    default: return scopeType
  }
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

function convertVariant(text: string): string {
  return ocrStore.convertVariant(text)
}

function selectTask(taskId: string) {
  taskStore.selectTask(taskId)
}

function applyFilters() {
  // Client-side filtering, no need to fetch
}

async function submitCreate() {
  if (!canCreate.value) return
  const task = await taskStore.createTask({
    title: newTask.value.title,
    documentId: newTask.value.documentId,
    scopeType: newTask.value.scopeType,
    chapter: newTask.value.scopeType === 'chapter' ? newTask.value.chapter : undefined,
    resultIds: newTask.value.scopeType === 'results' ? newTask.value.resultIds : [],
    assignee: newTask.value.assignee || undefined,
  })
  if (task) {
    taskStore.selectTask(task.id)
  }
  showCreate.value = false
  newTask.value = {
    title: '',
    documentId: '',
    scopeType: 'document',
    chapter: '',
    resultIds: [],
    assignee: '',
  }
}

function doAssign() {
  showAssignDialog.value = true
}

async function submitAssign() {
  if (!taskStore.selectedTaskId || !assignName.value.trim()) return
  await taskStore.assignTask(taskStore.selectedTaskId, assignName.value.trim())
  showAssignDialog.value = false
  assignName.value = ''
}

async function doStart() {
  if (!taskStore.selectedTaskId) return
  await taskStore.startTask(taskStore.selectedTaskId)
}

async function doComplete() {
  if (!taskStore.selectedTaskId) return
  await taskStore.completeTask(taskStore.selectedTaskId)
}

async function doDelete() {
  if (!taskStore.selectedTaskId) return
  if (confirm('确定要删除这个任务吗？')) {
    await taskStore.deleteTask(taskStore.selectedTaskId)
  }
}

onMounted(() => {
  if (ocrStore.documents.length === 0) {
    ocrStore.loadMockDocument()
  }
  if (taskStore.tasks.length === 0) {
    taskStore.loadMockTasks()
  }
  if (ocrStore.documents.length > 0 && !newTask.value.documentId) {
    newTask.value.documentId = ocrStore.documents[0].id
  }
})

watch(
  () => ocrStore.documents,
  (docs) => {
    if (docs.length > 0 && !newTask.value.documentId) {
      newTask.value.documentId = docs[0].id
    }
  },
  { immediate: false }
)
</script>
