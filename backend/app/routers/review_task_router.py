from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas import ReviewTask, ReviewTaskCreate, ReviewTaskUpdate, TaskStatus, TaskProgress
from app.services import task_service

router = APIRouter(prefix="/review-tasks", tags=["复核任务"])


@router.post("", response_model=ReviewTask)
def create_task(data: ReviewTaskCreate):
    """创建复核任务"""
    return task_service.create_task(data)


@router.get("", response_model=List[ReviewTask])
def list_tasks(
    document_id: Optional[str] = Query(None, description="按文档过滤"),
    assignee: Optional[str] = Query(None, description="按分配人过滤"),
    status: Optional[TaskStatus] = Query(None, description="按状态过滤"),
):
    """查询复核任务列表"""
    return task_service.list_tasks(document_id=document_id, assignee=assignee, status=status)


@router.get("/progress", response_model=TaskProgress)
def get_progress(
    document_id: Optional[str] = Query(None, description="按文档过滤"),
):
    """获取任务进度统计"""
    return task_service.get_progress(document_id=document_id)


@router.get("/{task_id}", response_model=ReviewTask)
def get_task(task_id: str):
    """获取单个复核任务详情"""
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.patch("/{task_id}", response_model=ReviewTask)
def update_task(task_id: str, data: ReviewTaskUpdate):
    """更新复核任务（分配、改状态等）"""
    task = task_service.update_task(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: str):
    """删除复核任务"""
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "删除成功"}


@router.post("/{task_id}/assign", response_model=ReviewTask)
def assign_task(task_id: str, assignee: str = Query(..., description="分配人")):
    """分配任务给指定人员"""
    task = task_service.update_task(task_id, ReviewTaskUpdate(assignee=assignee))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/{task_id}/start", response_model=ReviewTask)
def start_task(task_id: str):
    """开始处理任务"""
    task = task_service.update_task(task_id, ReviewTaskUpdate(status=TaskStatus.in_progress))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/{task_id}/complete", response_model=ReviewTask)
def complete_task(task_id: str):
    """完成任务"""
    task = task_service.update_task(task_id, ReviewTaskUpdate(status=TaskStatus.completed))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
