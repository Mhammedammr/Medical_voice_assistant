from flask import Flask, request, jsonify, Response, stream_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
import os
import json
import asyncio
from datetime import datetime
from src.core.config import Config
from src.model.pipeline_graph import stream_pipeline

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Add CORS support
CORS(app, origins=["*"], supports_credentials=True)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Application startup initialization
@app.before_request
def startup_event():
    """Initialize application on startup"""
    logger.info("Initializing test application")
    logger.info("Application started successfully")

@app.route("/", methods=["GET"])
def root():
    """Root endpoint for health check"""
    return jsonify({
        "message": "Audio Processing API - Test Version", 
        "status": "running", 
        "timestamp": datetime.now().isoformat()
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat()
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    """Handle file uploads and stream processing results."""
    logger.info("Received upload request")
    
    # Check if file is present
    if 'audio' not in request.files:
        logger.error("No audio file provided")
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    logger.info(f"audio_file: {audio_file}" )
    if audio_file.filename == '':
        logger.error("No file selected")
        return jsonify({"error": "No file selected"}), 400
    
    # Get form parameters
    language = request.form.get('language', 'ar')
    features = request.form.get('features', None)
    
    logger.info(f"File_org:, {request.files['audio']} File: {audio_file.filename}, Content Type: {audio_file.content_type}")
    logger.info(f"Parameters: language={language}")
    
    # Save the uploaded file
    try:
        filename = secure_filename(audio_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        audio_file.save(file_path)
        logger.info(f"File saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return jsonify({"error": f"Error saving file: {str(e)}"}), 500
    
    def sse_generator():
        """
        Stream graph results as SSE lines: {"step": <name>, "data": <payload>}
        """
        try:
            # Iterate the LangGraph stream
            for step_name, payload in stream_pipeline(
                file_path=file_path,
                language=language,
                features=features
            ):
                yield f"data: {json.dumps({'step': step_name, 'data': payload})}\n\n"
        except Exception as e:
            logger.exception("Unexpected error in pipeline stream")
            yield f"data: {json.dumps({'step': 'error', 'data': f'Unexpected error: {str(e)}'})}\n\n"
    
    return Response(
        sse_generator(), 
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
        }
    )

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting Flask test server on port 8586")
    app.run(host="0.0.0.0", port=8888, debug=True)