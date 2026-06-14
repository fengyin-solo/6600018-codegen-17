from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas import ReviewTask, ReviewTaskCreate, ReviewTaskUpdate, TaskStatus, TaskProgress, TaskScopeType, OCRResult
from app.services import task_service
from app.services.ocr_service import MOCK_RESULTS

router = APIRouter(prefix="/review-tasks", tags=["复核任务"])

_mock_initialized = False


def _ensure_mock_tasks():
    global _mock_initialized
    if _mock_initialized:
        return
    mock_tasks = [
        ReviewTaskCreate(
            title="论语·学而篇 第1-3章校对",
            document_id="1",
            scope_type=TaskScopeType.chapter,
            chapter="第1-3章",
            result_ids=[],
            assignee="张三",
        ),
        ReviewTaskCreate(
            title="论语·学而篇 第4-7章校对",
            document_id="1",
            scope_type=TaskScopeType.chapter,
            chapter="第4-7章",
            result_ids=[],
            assignee="李四",
        ),
        ReviewTaskCreate(
            title="论语·学而篇 整体复核",
            document_id="1",
            scope_type=TaskScopeType.whole_document,
            result_ids=[],
        ),
        ReviewTaskCreate(
            title="低置信度记录专项校对",
            document_id="1",
            scope_type=TaskScopeType.selected_results,
            result_ids=["r4", "r6"],
        ),
    ]
    for mt in mock_tasks:
        task_service.create_task(mt)
    tasks = task_service.list_tasks()
    for i, t in enumerate(tasks):
        if i == 0:
            task_service.update_task(t.id, ReviewTaskUpdate(status=TaskStatus.in_progress))
        elif i == 2:
            task_service.update_task(t.id, ReviewTaskUpdate(status=TaskStatus.completed))
    _mock_initialized = True


_ensure_mock_tasks()


@router.post("", response_model=ReviewTask)
def create_task(data: ReviewTaskCreate):
    return task_service.create_task(data)


@router.get("", response_model=List[ReviewTask])
def list_tasks(
    document_id: Optional[str] = Query(None, description="按文档过滤"),
    assignee: Optional[str] = Query(None, description="按分配人过滤"),
    status: Optional[TaskStatus] = Query(None, description="按状态过滤"),
):
    return task_service.list_tasks(document_id=document_id, assignee=assignee, status=status)


@router.get("/progress", response_model=TaskProgress)
def get_progress(
    document_id: Optional[str] = Query(None, description="按文档过滤"),
):
    return task_service.get_progress(document_id=document_id)


@router.get("/{task_id}", response_model=ReviewTask)
def get_task(task_id: str):
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.get("/{task_id}/results", response_model=List[OCRResult])
def get_task_results(task_id: str):
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if not task.result_ids:
        return []
    results_map = {r["id"]: r for r in MOCK_RESULTS}
    results: List[OCRResult] = []
    for rid in task.result_ids:
        if rid in results_map:
            r = results_map[rid]
            results.append(OCRResult(
                id=r["id"],
                text=r["text"],
                bbox=r["bbox"],
                confidence=r["confidence"],
            ))
        else:
            mock_map = {
                "r1": {"text": "子曰", "confidence": 0.95},
                "r2": {"text": "学而", "confidence": 0.88},
                "r3": {"text": "时习之", "confidence": 0.91},
                "r4": {"text": "不亦说乎", "confidence": 0.87},
                "r5": {"text": "有朋", "confidence": 0.93},
                "r6": {"text": "自远方来", "confidence": 0.85},
                "r7": {"text": "不亦乐乎", "confidence": 0.92},
            }
            if rid in mock_map:
                m = mock_map[rid]
                results.append(OCRResult(
                    id=rid,
                    text=m["text"],
                    bbox=[50.0, 30.0, 80.0, 40.0],
                    confidence=m["confidence"],
                ))
    return results


@router.patch("/{task_id}", response_model=ReviewTask)
def update_task(task_id: str, data: ReviewTaskUpdate):
    task = task_service.update_task(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: str):
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "删除成功"}


@router.post("/{task_id}/assign", response_model=ReviewTask)
def assign_task(task_id: str, assignee: str = Query(..., description="分配人")):
    task = task_service.update_task(task_id, ReviewTaskUpdate(assignee=assignee))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/{task_id}/start", response_model=ReviewTask)
def start_task(task_id: str):
    task = task_service.update_task(task_id, ReviewTaskUpdate(status=TaskStatus.in_progress))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/{task_id}/complete", response_model=ReviewTask)
def complete_task(task_id: str):
    task = task_service.update_task(task_id, ReviewTaskUpdate(status=TaskStatus.completed))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
