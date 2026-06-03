"""
AML Intelligence Platform — FastAPI Backend
Serves API + static frontend files.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from api.routes.alert_routes import router as alert_router
from api.routes.transaction_routes import router as transaction_router
from api.services.stream_service import start_streaming_engine

app = FastAPI(
    title="AML Intelligence API",
    version="1.0.0",
    description="Anti-Money Laundering Intelligence Platform API"
)

@app.on_event("startup")
def startup_event():
    start_streaming_engine()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(alert_router, prefix="/api", tags=["AML"])
app.include_router(transaction_router, prefix="/api", tags=["Transactions"])


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AML Intelligence API"}


# --- Serve static frontend ---
# Resolve path relative to project root (where uvicorn is run)
PROJECT_ROOT = os.getcwd()
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
CSS_DIR = os.path.join(FRONTEND_DIR, "css")
JS_DIR = os.path.join(FRONTEND_DIR, "js")
INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")

print(f"[AML] Frontend dir: {FRONTEND_DIR}")
print(f"[AML] CSS dir exists: {os.path.exists(CSS_DIR)}")
print(f"[AML] JS dir exists: {os.path.exists(JS_DIR)}")
print(f"[AML] index.html exists: {os.path.exists(INDEX_FILE)}")

if os.path.exists(CSS_DIR):
    app.mount("/css", StaticFiles(directory=CSS_DIR), name="css")

if os.path.exists(JS_DIR):
    app.mount("/js", StaticFiles(directory=JS_DIR), name="js")


@app.get("/")
def serve_frontend():
    if os.path.exists(INDEX_FILE):
        return FileResponse(INDEX_FILE)
    return {"error": "Frontend not found", "expected_path": INDEX_FILE}
