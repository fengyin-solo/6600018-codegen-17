import uuid
from datetime import datetime
from typing import List, Optional, Dict
from app.models.schemas import ReviewTask, ReviewTaskCreate, ReviewTaskUpdate, TaskStatus, TaskProgress

_tasks: Dict[str, ReviewTask] = {}


def create_task(data: ReviewTaskCreate) -> ReviewTask:
    task = ReviewTask(
        id=str(uuid.uuid4()),
        title=data.title,
        document_id=data.document_id,
        chapter=data.chapter,
        result_ids=data.result_ids,
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
        if data.status == TaskStatus.completed:
            task.completed_at = datetime.now().isoformat()
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
    return TaskProgress(
        total=len(tasks),
        pending=sum(1 for t in tasks if t.status == TaskStatus.pending),
        assigned=sum(1 for t in tasks if t.status == TaskStatus.assigned),
        in_progress=sum(1 for t in tasks if t.status == TaskStatus.in_progress),
        completed=sum(1 for t in tasks if t.status == TaskStatus.completed),
    )
