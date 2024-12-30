"""
This module defines a Flask Blueprint for handling chat interactions using a Gemini language model. 
It provides an endpoint for receiving user messages and generating responses using the configured model.
"""

import os
from typing import Dict, Any

from flask import Blueprint, request, jsonify, Response
from werkzeug.exceptions import BadRequest


from models.chat_model import get_model  # Assuming this module exists

# Initialize model outside the request context for efficiency
try:
    _GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
except KeyError:
    raise ValueError("GEMINI_API_KEY environment variable must be set.")

_model = get_model(api_key=_GEMINI_API_KEY)

if _model is None:
    raise RuntimeError("Failed to initialize the Gemini model. Check API Key and model availability")

_model.start_chat()

# Define Blueprint
chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat() -> Response:
    """
    Endpoint for handling chat requests.
    ... (rest of your docstring)
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data: Dict[str, Any] = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' in request body"}), 400

        user_message: str = data["message"]

        response = _model.generate_content(f"{user_message}")
        return jsonify({"response": response.text})

    except BadRequest:
        return jsonify({"error": "Request must be JSON"}), 400

    except Exception as e:  # Catch potential model errors
        print(f"Error during model processing: {e}") # Log the error for debugging
        return jsonify({"error": "An error occurred during processing."}), 500