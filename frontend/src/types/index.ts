export interface OCRResult {
  id: string
  text: string
  bbox: [number, number, number, number]  // x, y, w, h
  confidence: number
  corrected?: string
}

export interface Document {
  id: string
  name: string
  imageUrl: string
  results: OCRResult[]
  annotations: Annotation[]
  createdAt: string
}

export interface Annotation {
  id: string
  type: 'region' | 'character' | 'note'
  bbox: [number, number, number, number]
  label: string
  content: string
}

export interface VariantChar {
  ancient: string
  modern: string
  frequency: number
}

export type TaskStatus = 'pending' | 'assigned' | 'in_progress' | 'completed'

export type TaskScopeType = 'document' | 'chapter' | 'results'

export interface ReviewTask {
  id: string
  title: string
  documentId: string
  scopeType: TaskScopeType
  chapter?: string
  resultIds: string[]
  resultCount: number
  assignee?: string
  status: TaskStatus
  createdAt: string
  completedAt?: string
}

export interface ReviewTaskCreate {
  title: string
  documentId: string
  scopeType: TaskScopeType
  chapter?: string
  resultIds: string[]
  assignee?: string
}

export interface ReviewTaskUpdate {
  assignee?: string
  status?: TaskStatus
}

export interface TaskProgress {
  total: number
  pending: number
  assigned: number
  inProgress: number
  completed: number
  totalResults: number
  completedResults: number
}
