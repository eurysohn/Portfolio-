import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent.engine import run_agent
from config import settings
import os

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    api_key: Optional[str] = None

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

# Serve static files from the "dist" directory
# This directory will be created by the frontend build process
dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend-ts", "dist")

@app.get("/")
async def serve_index():
    index_file = os.path.join(dist_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend build not found. Run 'npm run build' in frontend-ts directory."}

if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="static")

@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.ENV
    }

@app.post("/query")
async def query_agent(request: QueryRequest):
    result = run_agent(request.query, top_k=request.top_k, api_key=request.api_key)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
