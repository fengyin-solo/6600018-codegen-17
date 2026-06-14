import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { ReviewTask, ReviewTaskCreate, ReviewTaskUpdate, TaskProgress, TaskStatus, TaskScopeType } from '../types'

const SCOPE_TYPE_MAP: Record<string, TaskScopeType> = {
  'whole_document': 'document',
  'chapter': 'chapter',
  'selected_results': 'results',
}

const SCOPE_TYPE_TO_BACKEND: Record<TaskScopeType, string> = {
  'document': 'whole_document',
  'chapter': 'chapter',
  'results': 'selected_results',
}

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<ReviewTask[]>([])
  const isLoading = ref(false)
  const filterDocumentId = ref<string | null>(null)
  const filterAssignee = ref<string | null>(null)
  const filterStatus = ref<TaskStatus | null>(null)
  const selectedTaskId = ref<string | null>(null)

  const selectedTask = computed<ReviewTask | null>(() => {
    if (!selectedTaskId.value) return null
    return tasks.value.find(t => t.id === selectedTaskId.value) || null
  })

  const progress = computed<TaskProgress>(() => {
    const filtered = filterDocumentId.value
      ? tasks.value.filter(t => t.documentId === filterDocumentId.value)
      : tasks.value
    const totalResults = filtered.reduce((sum, t) => sum + t.resultCount, 0)
    const completedResults = filtered
      .filter(t => t.status === 'completed')
      .reduce((sum, t) => sum + t.resultCount, 0)
    return {
      total: filtered.length,
      pending: filtered.filter(t => t.status === 'pending').length,
      assigned: filtered.filter(t => t.status === 'assigned').length,
      inProgress: filtered.filter(t => t.status === 'in_progress').length,
      completed: filtered.filter(t => t.status === 'completed').length,
      totalResults,
      completedResults,
    }
  })

  function convertTask(t: any): ReviewTask {
    const scopeType = SCOPE_TYPE_MAP[t.scope_type] || 'document'
    return {
      id: t.id,
      title: t.title,
      documentId: t.document_id,
      scopeType,
      chapter: t.chapter,
      resultIds: t.result_ids || [],
      resultCount: t.result_count ?? (t.result_ids?.length || 0),
      assignee: t.assignee,
      status: t.status,
      createdAt: t.created_at,
      completedAt: t.completed_at,
    }
  }

  function toBackendTask(task: ReviewTaskCreate): any {
    return {
      title: task.title,
      document_id: task.documentId,
      scope_type: SCOPE_TYPE_TO_BACKEND[task.scopeType],
      chapter: task.chapter,
      result_ids: task.resultIds,
      assignee: task.assignee,
    }
  }

  function generateId(): string {
    return 't' + Date.now() + Math.random().toString(36).substring(2, 6)
  }

  function resolveResultCount(documentId: string, scopeType: TaskScopeType, resultIds: string[]): number {
    if (resultIds && resultIds.length > 0) {
      return resultIds.length
    }
    return 0
  }

  async function fetchTasks() {
    isLoading.value = true
    try {
      const params = new URLSearchParams()
      if (filterDocumentId.value) params.set('document_id', filterDocumentId.value)
      if (filterAssignee.value) params.set('assignee', filterAssignee.value)
      if (filterStatus.value) params.set('status', filterStatus.value)
      const resp = await fetch(`/api/review-tasks?${params.toString()}`)
      if (resp.ok) {
        const data = await resp.json()
        tasks.value = data.map(convertTask)
        return
      }
    } catch {
      // Fallback to local mock data
    } finally {
      isLoading.value = false
    }
  }

  async function createTask(data: ReviewTaskCreate): Promise<ReviewTask | null> {
    isLoading.value = true
    try {
      const resp = await fetch('/api/review-tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(toBackendTask(data)),
      })
      if (resp.ok) {
        const t = await resp.json()
        const task = convertTask(t)
        tasks.value.push(task)
        return task
      }
    } catch {
      // Fallback: create locally
    } finally {
      isLoading.value = false
    }

    const resultCount = resolveResultCount(data.documentId, data.scopeType, data.resultIds)
    const task: ReviewTask = {
      id: generateId(),
      title: data.title,
      documentId: data.documentId,
      scopeType: data.scopeType,
      chapter: data.chapter,
      resultIds: data.resultIds,
      resultCount,
      assignee: data.assignee,
      status: data.assignee ? 'assigned' : 'pending',
      createdAt: new Date().toISOString(),
    }
    tasks.value.push(task)
    return task
  }

  async function updateTask(taskId: string, data: ReviewTaskUpdate): Promise<ReviewTask | null> {
    isLoading.value = true
    try {
      const resp = await fetch(`/api/review-tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assignee: data.assignee,
          status: data.status,
        }),
      })
      if (resp.ok) {
        const t = await resp.json()
        const updatedTask = convertTask(t)
        const idx = tasks.value.findIndex(task => task.id === taskId)
        if (idx !== -1) {
          tasks.value[idx] = updatedTask
        }
        return updatedTask
      }
    } catch {
      // Fallback: update locally
    } finally {
      isLoading.value = false
    }

    const idx = tasks.value.findIndex(task => task.id === taskId)
    if (idx === -1) return null

    const updated = { ...tasks.value[idx] }
    if (data.assignee !== undefined) {
      updated.assignee = data.assignee
      if (updated.status === 'pending') {
        updated.status = 'assigned'
      }
    }
    if (data.status !== undefined) {
      updated.status = data.status
      if (data.status === 'completed' && !updated.completedAt) {
        updated.completedAt = new Date().toISOString()
      }
      if (data.status !== 'completed') {
        updated.completedAt = undefined
      }
    }
    tasks.value[idx] = updated
    return updated
  }

  async function assignTask(taskId: string, assignee: string) {
    return updateTask(taskId, { assignee })
  }

  async function startTask(taskId: string) {
    return updateTask(taskId, { status: 'in_progress' })
  }

  async function completeTask(taskId: string) {
    return updateTask(taskId, { status: 'completed' })
  }

  async function deleteTask(taskId: string): Promise<boolean> {
    isLoading.value = true
    try {
      const resp = await fetch(`/api/review-tasks/${taskId}`, { method: 'DELETE' })
      if (resp.ok) {
        tasks.value = tasks.value.filter(t => t.id !== taskId)
        if (selectedTaskId.value === taskId) {
          selectedTaskId.value = null
        }
        return true
      }
    } catch {
      // Fallback: delete locally
    } finally {
      isLoading.value = false
    }

    tasks.value = tasks.value.filter(t => t.id !== taskId)
    if (selectedTaskId.value === taskId) {
      selectedTaskId.value = null
    }
    return true
  }

  function loadMockTasks() {
    tasks.value = [
      {
        id: 't1',
        title: '论语·学而篇 整体复核',
        documentId: '1',
        scopeType: 'document',
        resultIds: ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7'],
        resultCount: 7,
        assignee: undefined,
        status: 'pending',
        createdAt: '2025-01-16T10:00:00',
      },
      {
        id: 't2',
        title: '论语·学而篇 上篇章节校对',
        documentId: '1',
        scopeType: 'chapter',
        chapter: '第1-3章',
        resultIds: ['r1', 'r2', 'r3'],
        resultCount: 3,
        assignee: '张三',
        status: 'in_progress',
        createdAt: '2025-01-16T09:00:00',
      },
      {
        id: 't3',
        title: '论语·学而篇 下篇章节校对',
        documentId: '1',
        scopeType: 'chapter',
        chapter: '第4-7章',
        resultIds: ['r4', 'r5', 'r6', 'r7'],
        resultCount: 4,
        assignee: '李四',
        status: 'assigned',
        createdAt: '2025-01-16T09:30:00',
      },
      {
        id: 't4',
        title: '精选条目精校',
        documentId: '1',
        scopeType: 'results',
        resultIds: ['r1', 'r4', 'r7'],
        resultCount: 3,
        assignee: '王五',
        status: 'completed',
        createdAt: '2025-01-15T14:00:00',
        completedAt: '2025-01-15T16:30:00',
      },
    ]
  }

  function selectTask(taskId: string | null) {
    selectedTaskId.value = taskId
  }

  function setDocumentFilter(docId: string | null) {
    filterDocumentId.value = docId
  }

  function setAssigneeFilter(assignee: string | null) {
    filterAssignee.value = assignee
  }

  function setStatusFilter(status: TaskStatus | null) {
    filterStatus.value = status
  }

  return {
    tasks,
    isLoading,
    progress,
    selectedTaskId,
    selectedTask,
    filterDocumentId,
    filterAssignee,
    filterStatus,
    fetchTasks,
    createTask,
    updateTask,
    assignTask,
    startTask,
    completeTask,
    deleteTask,
    loadMockTasks,
    selectTask,
    setDocumentFilter,
    setAssigneeFilter,
    setStatusFilter,
  }
})
