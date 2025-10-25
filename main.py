from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "service healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)