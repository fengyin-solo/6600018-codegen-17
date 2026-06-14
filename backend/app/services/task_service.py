import uuid
from datetime import datetime
from typing import List, Optional, Dict
from app.models.schemas import ReviewTask, ReviewTaskCreate, ReviewTaskUpdate, TaskStatus, TaskProgress, TaskScopeType

_tasks: Dict[str, ReviewTask] = {}

_documents: Dict[str, Dict] = {
    "1": {
        "id": "1",
        "name": "论语·学而篇",
        "total_results": 7,
        "chapters": {
            "第1-3章": ["r1", "r2", "r3"],
            "第4-7章": ["r4", "r5", "r6", "r7"],
            "第一章": ["r1"],
            "第二章": ["r2"],
            "第三章": ["r3"],
            "第四章": ["r4"],
            "第五章": ["r5", "r6"],
            "第六章": ["r7"],
        }
    }
}


def _resolve_result_count(document_id: str, scope_type: TaskScopeType, chapter: Optional[str], result_ids: List[str]) -> int:
    doc = _documents.get(document_id)
    if scope_type == TaskScopeType.whole_document:
        if doc:
            return doc["total_results"]
        return 0
    if scope_type == TaskScopeType.chapter:
        if doc and chapter:
            ch_results = doc["chapters"].get(chapter, [])
            return len(ch_results)
        return 0
    if scope_type == TaskScopeType.selected_results:
        return len(result_ids)
    return 0


def _resolve_result_ids(document_id: str, scope_type: TaskScopeType, chapter: Optional[str], result_ids: List[str]) -> List[str]:
    doc = _documents.get(document_id)
    if scope_type == TaskScopeType.whole_document:
        if doc:
            all_ids: List[str] = []
            for ch_ids in doc["chapters"].values():
                all_ids.extend(ch_ids)
            return list(set(all_ids))
        return []
    if scope_type == TaskScopeType.chapter:
        if doc and chapter:
            return list(doc["chapters"].get(chapter, []))
        return []
    if scope_type == TaskScopeType.selected_results:
        return result_ids
    return []


def register_document(doc_id: str, name: str, total_results: int, chapters: Optional[Dict[str, List[str]]] = None):
    _documents[doc_id] = {
        "id": doc_id,
        "name": name,
        "total_results": total_results,
        "chapters": chapters or {},
    }


def create_task(data: ReviewTaskCreate) -> ReviewTask:
    resolved_ids = _resolve_result_ids(data.document_id, data.scope_type, data.chapter, data.result_ids)
    resolved_count = _resolve_result_count(data.document_id, data.scope_type, data.chapter, resolved_ids)
    task = ReviewTask(
        id=str(uuid.uuid4()),
        title=data.title,
        document_id=data.document_id,
        scope_type=data.scope_type,
        chapter=data.chapter,
        result_ids=resolved_ids,
        result_count=resolved_count,
        assignee=data.assignee,
        status=TaskStatus.assigned if data.assignee else TaskStatus.pending,
        created_at=datetime.now().isoformat(),
    )
    _tasks[task.id] = task
    return task


def get_task(task_id: str) -> Optional[ReviewTask]:
    return _tasks.get(task_id)


def list_tasks(document_id: Optional[str] = None, assignee: Optional[str] = None, status: Optional[TaskStatus] = None) -> List[ReviewTask]:
    tasks = list(_tasks.values())
    if document_id:
        tasks = [t for t in tasks if t.document_id == document_id]
    if assignee:
        tasks = [t for t in tasks if t.assignee == assignee]
    if status:
        tasks = [t for t in tasks if t.status == status]
    return tasks


def update_task(task_id: str, data: ReviewTaskUpdate) -> Optional[ReviewTask]:
    task = _tasks.get(task_id)
    if not task:
        return None
    if data.assignee is not None:
        task.assignee = data.assignee
        if task.status == TaskStatus.pending:
            task.status = TaskStatus.assigned
    if data.status is not None:
        task.status = data.status
        if data.status == TaskStatus.completed and task.completed_at is None:
            task.completed_at = datetime.now().isoformat()
        if data.status != TaskStatus.completed:
            task.completed_at = None
    _tasks[task.id] = task
    return task


def delete_task(task_id: str) -> bool:
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def get_progress(document_id: Optional[str] = None) -> TaskProgress:
    tasks = list(_tasks.values())
    if document_id:
        tasks = [t for t in tasks if t.document_id == document_id]
    total_results = sum(t.result_count for t in tasks)
    completed_results = sum(t.result_count for t in tasks if t.status == TaskStatus.completed)
    return TaskProgress(
        total=len(tasks),
        pending=sum(1 for t in tasks if t.status == TaskStatus.pending),
        assigned=sum(1 for t in tasks if t.status == TaskStatus.assigned),
        in_progress=sum(1 for t in tasks if t.status == TaskStatus.in_progress),
        completed=sum(1 for t in tasks if t.status == TaskStatus.completed),
        total_results=total_results,
        completed_results=completed_results,
    )
