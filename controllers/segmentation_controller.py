from fastapi import BackgroundTasks, HTTPException
from schemas import SegmentationRequest, TaskResponse, TaskStatus
from storage import (
    store_task_data,
    get_task_data,
    task_exists,
    delete_task_data,
    redis_client,
)
from pathlib import Path
import uuid
import asyncio
import traceback
from datetime import datetime


async def run_segmentation(task_id: str, request: SegmentationRequest):
    """Background task that runs the BraTS segmentation"""
    try:
        # Update status to processing
        await store_task_data(task_id, {
            "status": "processing",
            "started_at": datetime.utcnow().isoformat(),
            "progress": "Starting segmentation..."
        })

        # Import BraTS here to avoid loading at startup
        from brats import AdultGliomaPreAndPostTreatmentSegmenter
        from brats.constants import AdultGliomaPreAndPostTreatmentAlgorithms

        await store_task_data(task_id, {"progress": "Initializing BraTS model..."})

        # Run in thread pool to not block async event loop
        loop = asyncio.get_event_loop()

        def _run_inference():
            """Blocking function to run in executor"""
            # Initialize segmenter
            segmenter = AdultGliomaPreAndPostTreatmentSegmenter(
                algorithm=AdultGliomaPreAndPostTreatmentAlgorithms.BraTS25_1,
                cuda_devices="0"
            )

            # Determine output path
            output_file = request.output_path
            if not output_file:
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_file = str(output_dir / f"segmentation_{task_id}.nii.gz")

            # Run inference (this is the long-running operation)
            segmenter.infer_single(
                t1c=request.t1c_path,
                t1n=request.t1n_path,
                t2f=request.t2f_path,
                t2w=request.t2w_path,
                output_file=output_file,
            )

            return output_file

        # Execute blocking inference in thread pool
        print(f"[Task {task_id}] Starting inference...")
        output_file = await loop.run_in_executor(None, _run_inference)
        print(f"[Task {task_id}] Inference completed!")

        # Success - store result
        result = {
            "output_file": output_file,
            "input_files": {
                "t1c": request.t1c_path,
                "t1n": request.t1n_path,
                "t2f": request.t2f_path,
                "t2w": request.t2w_path,
            }
        }

        await store_task_data(task_id, {
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "result": result,
            "progress": "Segmentation complete!"
        })

        # Set expiry for Redis
        if redis_client:
            await redis_client.expire(f"task:{task_id}", 86400)

        print(f"[Task {task_id}] Result stored")

    except Exception as e:
        # Capture full error trace
        error_trace = traceback.format_exc()
        print(f"[Task {task_id}] ERROR: {error_trace}")

        # Store error
        await store_task_data(task_id, {
            "status": "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "error": str(e),
            "error_trace": error_trace
        })

        if redis_client:
            await redis_client.expire(f"task:{task_id}", 86400)


async def create_segmentation_task(request: SegmentationRequest, background_tasks: BackgroundTasks) -> TaskResponse:
    """Create task, store initial state and schedule background processing"""
    task_id = str(uuid.uuid4())
    print(f"[Task {task_id}] New segmentation request received")

    # Store initial task status
    await store_task_data(task_id, {
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "request": request.model_dump()
    })

    # Start background processing
    background_tasks.add_task(run_segmentation, task_id, request)

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Segmentation task created. Poll /task/{task_id}/status for updates."
    )


async def get_task_status_controller(task_id: str) -> TaskStatus:
    """Return TaskStatus for given id or raise 404"""
    if not await task_exists(task_id):
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task_data = await get_task_data(task_id)

    return TaskStatus(
        task_id=task_id,
        status=task_data.get("status", "unknown"),
        created_at=task_data.get("created_at", ""),
        started_at=task_data.get("started_at"),
        completed_at=task_data.get("completed_at"),
        result=task_data.get("result"),
        error=task_data.get("error"),
        progress=task_data.get("progress")
    )


async def delete_task_controller(task_id: str):
    """Delete a task or raise 404"""
    if not await task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    await delete_task_data(task_id)
    print(f"[Task {task_id}] Deleted")

    return {"message": f"Task {task_id} deleted successfully"}


async def health_check_controller():
    """Return health info about storage"""
    storage = "redis" if redis_client else "memory"
    redis_status = "disconnected"

    if redis_client:
        try:
            await redis_client.ping()
            redis_status = "connected"
        except Exception as e:
            redis_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "storage": storage,
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }
