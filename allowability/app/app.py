"""
Simple Flask application for Allowability project.
Provides health check endpoint and basic info.
"""

import logging
import os
from datetime import datetime
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Application metadata
APP_NAME = "allowability"
APP_VERSION = "1.0.0"
START_TIME = datetime.utcnow()


@app.route('/')
def index():
    """Root endpoint with basic application info."""
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    
    response = {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "uptime_seconds": uptime,
        "environment": os.environ.get("ENVIRONMENT", "unknown"),
        "endpoints": {
            "health": "/health",
            "info": "/"
        }
    }
    
    logger.info(f"Index endpoint accessed - uptime: {uptime:.2f}s")
    return jsonify(response), 200


@app.route('/health')
def health():
    """Health check endpoint for ALB target group."""
    response = {
        "status": "ok",
        "message": "Hello world!",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return jsonify(response), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {error}")
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    # This is only used for local development
    # In production, gunicorn is used as the WSGI server
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
