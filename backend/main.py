"""
FastAPI Backend for Grant Evaluator
Supports file upload, grant evaluation pipeline, and MongoDB Atlas storage
"""

import asyncio

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
import os
import sys
import tempfile
from datetime import datetime, timezone
from bson import ObjectId

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import EvaluationResponse, SettingsModel, EvaluationCreate
from database import get_database
import database
from evaluation_pipeline import run_full_evaluation
from src.agents.pdf_generator import generate_evaluation_report_pdf
from src.agents.domain_selection import get_all_domains
from websocket_manager import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    from database import connect_to_mongo
    try:
        await connect_to_mongo()
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ CRITICAL ERROR: MongoDB connection failed!")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"\n💡 Solution: Check QUICKFIX_MONGODB.md for instructions")
        print(f"{'='*60}\n")
    
    yield
    
    # Shutdown
    from database import close_mongo_connection
    await close_mongo_connection()


app = FastAPI(
    title="Grant Evaluator API",
    description="AI-powered grant proposal evaluation system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
# Configure CORS origins via environment variable `ALLOWED_ORIGINS`.
# If not set, fall back to local dev origins.
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    if allowed_origins_env.strip() == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allow_origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    from database import client, database
    
    mongo_status = "disconnected"
    if client is not None:
        try:
            await client.admin.command('ping')
            mongo_status = "connected"
        except:
            mongo_status = "error"
    
    return {
        "status": "healthy" if mongo_status == "connected" else "degraded",
        "service": "Grant Evaluator API",
        "version": "1.0.0",
        "mongodb": mongo_status,
        "database": database.name if database is not None else None
    }


@app.get("/api/domains")
async def get_domains():
    """Get list of all available domains for dropdown selection"""
    return {"domains": get_all_domains()}


@app.get("/api/health")
async def health_check():
    """Detailed health check to verify backend is responsive"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
        "memory_percent": round(process.memory_percent(), 2),
        "cpu_percent": round(process.cpu_percent(interval=0.1), 2),
        "message": "Backend is alive and responding"
    }


@app.websocket("/ws/evaluation/{session_id}")
async def evaluation_status_socket(websocket: WebSocket, session_id: str):
    """Stream live evaluation status updates to connected clients."""

    await websocket_manager.connect(session_id, websocket)
    try:
        await websocket.send_json({
            "event": "connected",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        while True:
            # Keep the connection alive; we do not expect client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(session_id, websocket)
    except Exception:
        await websocket_manager.disconnect(session_id, websocket)


@app.post("/api/evaluations", response_model=EvaluationResponse)
async def create_evaluation(
    file: UploadFile = File(...),
    domain: Optional[str] = Form(None),
    check_plagiarism: bool = Form(False),
    session_id: Optional[str] = Form(None),
    db=Depends(get_database)
):
    """
    Upload and evaluate a grant proposal (PDF or DOCX)
    Returns comprehensive evaluation with scores, critique, and budget analysis
    
    Args:
        file: Grant proposal file (PDF or DOCX)
        domain: Optional user-specified domain (overrides auto-detection)
        check_plagiarism: Whether to run plagiarism detection
    """
    print("="*80)
    print(f"[INFO] NEW EVALUATION REQUEST RECEIVED")
    print(f"[INFO] File: {file.filename}, Domain: {domain}, Plagiarism: {check_plagiarism}")
    print(f"[INFO] Session ID: {session_id}")
    print("="*80)
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Get settings for max_budget
    settings = await database.settings_collection.find_one()
    max_budget = settings.get('max_budget', 50000) if settings else 50000
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    loop = asyncio.get_running_loop()

    def _consume_future(fut: asyncio.Future) -> None:
        try:
            fut.result()
        except Exception:
            pass

    def queue_status(payload: Dict[str, Any]) -> None:
        if not session_id:
            return
        future = asyncio.run_coroutine_threadsafe(
            websocket_manager.send(session_id, payload),
            loop
        )
        future.add_done_callback(_consume_future)

    if session_id:
        await websocket_manager.send(session_id, {
            "event": "status",
            "stage_index": -1,
            "stage_key": "queued",
            "label": "Preparing evaluation",
            "status": "queued",
            "progress": 0,
            "message": "Preparing evaluation pipeline...",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    try:
        def run_pipeline() -> Dict[str, Any]:
            return run_full_evaluation(
                file_path=tmp_file_path,
                max_budget=max_budget,
                override_domain=domain,
                check_plagiarism=check_plagiarism,
                status_callback=queue_status if session_id else None,
            )

        evaluation_result = await loop.run_in_executor(None, run_pipeline)
    
    except Exception as e:
        # Check for API quota errors
        error_message = str(e)
        if "429" in error_message or "quota" in error_message.lower() or "ResourceExhausted" in str(type(e).__name__):
            print(f"[ERROR] API quota exceeded: {error_message}")
            if session_id:
                await websocket_manager.send(session_id, {
                    "event": "error",
                    "message": "AI API quota exceeded. Please wait a few minutes and try again, or check your API key billing.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            raise HTTPException(
                status_code=429,
                detail="AI API quota exceeded. Please wait a few minutes and try again, or upgrade your API plan."
            )
        
        # Re-raise other errors to be caught by outer exception handler
        raise
    
    try:

        # Prepare document for MongoDB
        evaluation_doc = {
            "file_name": file.filename,
            "file_size": len(content),
            "decision": evaluation_result["decision"],
            "overall_score": evaluation_result["overall_score"],
            "domain": evaluation_result.get("domain", "Unknown"),
            "scores": evaluation_result["scores"],
            "critique_domains": evaluation_result.get("critique_domains", []),
            "section_scores": evaluation_result["section_scores"],
            "full_critique": evaluation_result["full_critique"],
            "budget_analysis": evaluation_result["budget_analysis"],
            "summary": evaluation_result.get("summary", {}),
            "plagiarism_check": evaluation_result.get("plagiarism_check"),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        # Insert into MongoDB
        result = await database.evaluations_collection.insert_one(evaluation_doc)
        evaluation_doc["id"] = str(result.inserted_id)
        evaluation_doc["_id"] = str(result.inserted_id)

        # Convert datetime to ISO string for JSON response
        evaluation_doc["created_at"] = evaluation_doc["created_at"].isoformat()
        evaluation_doc["updated_at"] = evaluation_doc["updated_at"].isoformat()

        if session_id:
            await websocket_manager.send(session_id, {
                "event": "complete",
                "evaluation_id": evaluation_doc["id"],
                "decision": evaluation_doc["decision"],
                "progress": 100,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        return evaluation_doc

    except Exception as e:
        import traceback
        print("[ERROR] Exception in /api/evaluations:", str(e))
        traceback.print_exc()
        if session_id:
            await websocket_manager.send(session_id, {
                "event": "error",
                "message": f"Evaluation failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@app.get("/api/evaluations", response_model=List[EvaluationResponse])
async def get_evaluations(db=Depends(get_database)):
    """Get all evaluations, sorted by creation date (newest first)"""
    
    cursor = database.evaluations_collection.find().sort("created_at", -1)
    evaluations = []
    
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc["created_at"] = doc["created_at"].isoformat()
        doc["updated_at"] = doc["updated_at"].isoformat()
        evaluations.append(doc)
    
    return evaluations


@app.get("/api/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation_by_id(evaluation_id: str, db=Depends(get_database)):
    """Get a specific evaluation by ID"""
    
    try:
        obj_id = ObjectId(evaluation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid evaluation ID format")
    
    doc = await database.evaluations_collection.find_one({"_id": obj_id})
    
    if not doc:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    doc["id"] = str(doc["_id"])
    doc["created_at"] = doc["created_at"].isoformat()
    doc["updated_at"] = doc["updated_at"].isoformat()
    
    return doc


@app.get("/api/evaluations/{evaluation_id}/download")
async def download_evaluation_pdf(evaluation_id: str, db=Depends(get_database)):
    """Download evaluation as PDF report"""
    
    try:
        obj_id = ObjectId(evaluation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid evaluation ID format")
    
    doc = await database.evaluations_collection.find_one({"_id": obj_id})
    
    if not doc:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    # Prepare data for PDF generation
    doc["id"] = str(doc["_id"])
    doc["created_at"] = doc["created_at"].isoformat()
    doc["updated_at"] = doc["updated_at"].isoformat()
    
    try:
        # Generate PDF
        pdf_buffer = generate_evaluation_report_pdf(doc)
        
        # Create filename
        filename = f"grant_evaluation_{doc.get('file_name', 'report').replace('.pdf', '').replace('.docx', '')}_{evaluation_id[:8]}.pdf"
        
        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/api/settings", response_model=SettingsModel)
async def get_settings(db=Depends(get_database)):
    """Get application settings"""
    
    settings = await database.settings_collection.find_one()
    
    if not settings:
        # Return default settings if none exist
        return {
            "max_budget": 50000,
            "chunk_size": 1000,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    settings["id"] = str(settings["_id"])
    settings["created_at"] = settings.get("created_at", datetime.now(timezone.utc)).isoformat()
    settings["updated_at"] = settings.get("updated_at", datetime.now(timezone.utc)).isoformat()
    
    return settings


@app.put("/api/settings", response_model=SettingsModel)
async def update_settings(settings: SettingsModel, db=Depends(get_database)):
    """Update application settings"""
    
    existing = await database.settings_collection.find_one()
    
    settings_dict = {
        "max_budget": settings.max_budget,
        "chunk_size": settings.chunk_size,
        "updated_at": datetime.now(timezone.utc)
    }
    
    if existing:
        # Update existing settings
        await database.settings_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": settings_dict}
        )
        settings_dict["id"] = str(existing["_id"])
        settings_dict["created_at"] = existing.get("created_at", datetime.now(timezone.utc))
    else:
        # Create new settings
        settings_dict["created_at"] = datetime.now(timezone.utc)
        result = await database.settings_collection.insert_one(settings_dict)
        settings_dict["id"] = str(result.inserted_id)
    
    settings_dict["created_at"] = settings_dict["created_at"].isoformat()
    settings_dict["updated_at"] = settings_dict["updated_at"].isoformat()
    
    return settings_dict


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
