import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://medical-redis:6379")
redis_client = None

try:
    import redis.asyncio as redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    print(f"✓ Redis configured: {REDIS_URL}")
except ImportError:
    print("⚠ Redis not available, using in-memory storage")
    redis_client = None

# In-memory fallback
TASKS = {}


async def store_task_data(task_id: str, data: dict):
    """Store task data in Redis or memory"""
    if redis_client:
        await redis_client.hset(
            f"task:{task_id}",
            mapping={
                k: json.dumps(v) if isinstance(v, dict) else str(v)
                for k, v in data.items()
            },
        )
    else:
        if task_id not in TASKS:
            TASKS[task_id] = {}
        TASKS[task_id].update(data)


async def get_task_data(task_id: str) -> dict:
    """Get task data from Redis or memory"""
    if redis_client:
        data = await redis_client.hgetall(f"task:{task_id}")
        # Parse JSON strings back to dicts
        for key in ["result", "request"]:
            if key in data and data[key]:
                try:
                    data[key] = json.loads(data[key])
                except Exception:
                    pass
        return data
    else:
        return TASKS.get(task_id, {})


async def task_exists(task_id: str) -> bool:
    """Check if task exists"""
    if redis_client:
        return (await redis_client.exists(f"task:{task_id}")) > 0
    else:
        return task_id in TASKS


async def delete_task_data(task_id: str):
    """Delete task data"""
    if redis_client:
        await redis_client.delete(f"task:{task_id}")
    else:
        TASKS.pop(task_id, None)
