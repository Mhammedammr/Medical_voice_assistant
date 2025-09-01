from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Optional
import os
import uvicorn
import json
import asyncio
from datetime import datetime

from src.core.config import Config
from src.model.pipeline_graph import stream_pipeline  # <-- use the graph runner

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Audio Processing API - Test Version")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Initializing test application")
    logger.info("Application started successfully")

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"message": "Audio Processing API - Test Version", "status": "running", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze")
async def Analyze(
    audio: UploadFile = File(...),
    language: str = Form("ar"),
    features: Optional[str] = Form(None)  # optional override of DEFAULT_FEATURES
):
    """Handle file uploads and stream processing results."""
    logger.info(f"Received upload request")
    logger.info(f"File: {audio.filename}, Content Type: {audio.content_type}")
    logger.info(f"Parameters: language={language}")

    logger.info(f"Upload parameters: language={language}")

    # Save the uploaded file
    try:
        contents = await audio.read()
        file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"File saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    async def sse_generator():
        """
        Stream graph results as SSE lines: {"step": <name>, "data": <payload>}
        """
        try:
            # Iterate the LangGraph stream
            for step_name, payload in stream_pipeline(
                file_path=file_path,
                language=language,
                api_key=Config.FIREWORKS_API_KEY,
                features=features
            ):
                yield json.dumps({"step": step_name, "data": payload}) + "\n"
                await asyncio.sleep(0.01)  # tiny pause to flush to client

        except Exception as e:
            logger.exception("Unexpected error in pipeline stream")
            yield json.dumps({"step": "error", "data": f"Unexpected error: {str(e)}"}) + "\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@app.post("/test-form")
async def test_form_data(
    text_field: str = Form(...),
    number_field: int = Form(...),
    optional_field: Optional[str] = Form(None)
):
    """Test endpoint for form data without file upload"""
    return {
        "message": "Form data received successfully",
        "data": {
            "text_field": text_field,
            "number_field": number_field,
            "optional_field": optional_field
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting FastAPI test server on port 8587")
    uvicorn.run("__main__:app", host="0.0.0.0", port=8586, reload=True)
