import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { ReviewTask, ReviewTaskCreate, ReviewTaskUpdate, TaskProgress, TaskStatus } from '../types'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<ReviewTask[]>([])
  const isLoading = ref(false)
  const filterDocumentId = ref<string | null>(null)
  const filterAssignee = ref<string | null>(null)
  const filterStatus = ref<TaskStatus | null>(null)

  const progress = computed<TaskProgress>(() => {
    const filtered = filterDocumentId.value
      ? tasks.value.filter(t => t.documentId === filterDocumentId.value)
      : tasks.value
    return {
      total: filtered.length,
      pending: filtered.filter(t => t.status === 'pending').length,
      assigned: filtered.filter(t => t.status === 'assigned').length,
      inProgress: filtered.filter(t => t.status === 'in_progress').length,
      completed: filtered.filter(t => t.status === 'completed').length,
    }
  })

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
        tasks.value = data.map((t: any) => ({
          id: t.id,
          title: t.title,
          documentId: t.document_id,
          chapter: t.chapter,
          resultIds: t.result_ids,
          assignee: t.assignee,
          status: t.status,
          createdAt: t.created_at,
          completedAt: t.completed_at,
        }))
      }
    } catch {
      loadMockTasks()
    } finally {
      isLoading.value = false
    }
  }

  async function createTask(data: ReviewTaskCreate) {
    isLoading.value = true
    try {
      const resp = await fetch('/api/review-tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: data.title,
          document_id: data.documentId,
          chapter: data.chapter,
          result_ids: data.resultIds,
          assignee: data.assignee,
        }),
      })
      if (resp.ok) {
        const t = await resp.json()
        const task: ReviewTask = {
          id: t.id,
          title: t.title,
          documentId: t.document_id,
          chapter: t.chapter,
          resultIds: t.result_ids,
          assignee: t.assignee,
          status: t.status,
          createdAt: t.created_at,
          completedAt: t.completed_at,
        }
        tasks.value.push(task)
        return task
      }
    } finally {
      isLoading.value = false
    }
    return null
  }

  async function updateTask(taskId: string, data: ReviewTaskUpdate) {
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
        const idx = tasks.value.findIndex(task => task.id === taskId)
        if (idx !== -1) {
          tasks.value[idx] = {
            id: t.id,
            title: t.title,
            documentId: t.document_id,
            chapter: t.chapter,
            resultIds: t.result_ids,
            assignee: t.assignee,
            status: t.status,
            createdAt: t.created_at,
            completedAt: t.completed_at,
          }
        }
        return tasks.value[idx]
      }
    } finally {
      isLoading.value = false
    }
    return null
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

  async function deleteTask(taskId: string) {
    isLoading.value = true
    try {
      const resp = await fetch(`/api/review-tasks/${taskId}`, { method: 'DELETE' })
      if (resp.ok) {
        tasks.value = tasks.value.filter(t => t.id !== taskId)
        return true
      }
    } finally {
      isLoading.value = false
    }
    return false
  }

  function loadMockTasks() {
    tasks.value = [
      {
        id: 't1',
        title: '论语·学而篇 第1-3章校对',
        documentId: '1',
        chapter: '第1-3章',
        resultIds: ['r1', 'r2', 'r3'],
        assignee: '张三',
        status: 'in_progress',
        createdAt: '2025-01-16T09:00:00',
      },
      {
        id: 't2',
        title: '论语·学而篇 第4-7章校对',
        documentId: '1',
        chapter: '第4-7章',
        resultIds: ['r4', 'r5', 'r6', 'r7'],
        assignee: '李四',
        status: 'assigned',
        createdAt: '2025-01-16T09:30:00',
      },
      {
        id: 't3',
        title: '论语·学而篇 整体复核',
        documentId: '1',
        resultIds: [],
        status: 'pending',
        createdAt: '2025-01-16T10:00:00',
      },
    ]
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
    setDocumentFilter,
    setAssigneeFilter,
    setStatusFilter,
  }
})
