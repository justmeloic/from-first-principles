"""
Entry point for the application.

This script creates a Flask application using a custom middleware creation function
and starts the development server.
"""

from appfactory import create_middleware_app  # Assuming appfactory.py exists

from flask import Flask  # Optional import for type hinting

# Create the Flask application with middleware
app: Flask = create_middleware_app()  # Type hint if `create_middleware_app` returns a Flask app

def run_server():
    app.run(debug=True, port=8080)

if __name__ == "__main__":
    # Run the development server
    run_server()