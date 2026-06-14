from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime


class OCRResult(BaseModel):
    id: str
    text: str
    bbox: List[float]
    confidence: float
    corrected: Optional[str] = None


class Document(BaseModel):
    id: str
    name: str
    image_url: str
    results: List[OCRResult]
    created_at: str


class Annotation(BaseModel):
    id: str
    type: str
    bbox: List[float]
    label: str
    content: str


class TaskStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"


class TaskScopeType(str, Enum):
    whole_document = "whole_document"
    chapter = "chapter"
    selected_results = "selected_results"


class ReviewTaskCreate(BaseModel):
    title: str
    document_id: str
    scope_type: TaskScopeType = TaskScopeType.whole_document
    chapter: Optional[str] = None
    result_ids: List[str] = []
    assignee: Optional[str] = None


class ReviewTask(BaseModel):
    id: str
    title: str
    document_id: str
    scope_type: TaskScopeType = TaskScopeType.whole_document
    chapter: Optional[str] = None
    result_ids: List[str] = []
    result_count: int = 0
    assignee: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    created_at: str
    completed_at: Optional[str] = None


class ReviewTaskUpdate(BaseModel):
    assignee: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskProgress(BaseModel):
    total: int
    pending: int
    assigned: int
    in_progress: int
    completed: int
    total_results: int
    completed_results: int
