from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
import os
from datetime import datetime

from src.model.pipeline_graph import (
    transcribe_node,
    refine_node,
    translate_node,
    extract_node,
    PipelineState,
)
from src.core.config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------
# Helper to save file
# -------------------
def save_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return file_path

# -------------------
# Endpoints
# -------------------

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_path = save_file(audio_file)
    language = request.form.get("language", "ar")
    api_key = Config.FIREWORKS_API_KEY

    state: PipelineState = {"file_path": file_path, "language": language, "api_key": api_key}
    result = transcribe_node(state)
    return jsonify({"transcription": result.get("raw_text", "")})


@app.route("/refine", methods=["POST"])
def refine():
    data = request.json
    raw_text = data.get("text", "")
    language = data.get("language", "ar")

    state: PipelineState = {"raw_text": raw_text, "language": language}
    result = refine_node(state)
    return jsonify({"refinement": result.get("refined_text", "")})


@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    refined_text = data.get("text", "")

    state: PipelineState = {"refined_text": refined_text}
    result = translate_node(state)
    return jsonify({"translation": result.get("translated_text", "")})


@app.route("/extract", methods=["POST"])
def extract():
    data = request.json
    text = data.get("text", "")
    language = data.get("language", "ar")
    features = data.get("features")

    # if Arabic, expect translation was provided
    state: PipelineState = {"refined_text": text, "language": language}
    if language == "ar":
        state["translated_text"] = text
    if features:
        state["features"] = features

    result = extract_node(state)
    return jsonify({
        "json_data": result.get("json_data", {}),
        "reasoning": result.get("reasoning", "")
    })

if __name__ == "__main__":
    logger.info("Starting Flask test server on port 8586")
    app.run(host="0.0.0.0", port=8888, debug=True)