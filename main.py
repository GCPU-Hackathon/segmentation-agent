from fastapi import FastAPI, BackgroundTasks, HTTPException
from schemas import SegmentationRequest, TaskResponse, TaskStatus
from typing import Optional
import uuid
from pathlib import Path
import asyncio
import traceback
from datetime import datetime
import os
from dotenv import load_dotenv

from storage import (
    store_task_data,
    get_task_data,
    task_exists,
    delete_task_data,
    redis_client,
)

load_dotenv()

app = FastAPI(title="BraTS Segmentation API")

from controllers.segmentation_controller import (
    create_segmentation_task as controller_create_segmentation_task,
    get_task_status_controller,
    delete_task_controller,
    health_check_controller,
)


@app.post("/segment", response_model=TaskResponse, status_code=202)
async def create_segmentation_task(request: SegmentationRequest, background_tasks: BackgroundTasks):
    return await controller_create_segmentation_task(request, background_tasks)


@app.get("/task/{task_id}/status", response_model=TaskStatus)
async def get_task_status(task_id: str):
    return await get_task_status_controller(task_id)


@app.delete("/task/{task_id}")
async def delete_task(task_id: str):
    return await delete_task_controller(task_id)


@app.get("/health")
async def health_check():
    return await health_check_controller()


@app.on_event("startup")
async def startup_event():
    if redis_client:
        try:
            await redis_client.ping()
            print("✓ Redis connection established")
        except Exception as e:
            print(f"✗ Redis connection failed: {e}")
    else:
        print("✓ Using in-memory storage")


@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        await redis_client.close()
        print("Redis connection closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )