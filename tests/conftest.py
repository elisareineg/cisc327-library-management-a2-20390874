"""
Pytest configuration file for Library Management System tests.
Handles database setup and teardown for test isolation.
"""

import pytest
import os
import sys
import threading
import time
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database, add_sample_data, DATABASE
from app import create_app

@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """
    Setup a fresh database for each test function.
    This ensures test isolation and prevents tests from interfering with each other.
    """
    # Remove existing database if it exists
    try:
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
    except (OSError, PermissionError):
        # If file is locked, wait a moment and try again
        time.sleep(0.1)
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
    
    # Initialize fresh database with schema
    init_database()
    
    # Add sample data
    add_sample_data()
    
    yield
    
    # Cleanup after test
    try:
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
    except (OSError, PermissionError):
        # File might be locked, ignore cleanup errors
        pass


@pytest.fixture(scope="function")
def flask_app_server():
    """
    Start Flask application server in a separate thread for E2E tests.
    Uses port 5001 to avoid conflicts with AirPlay on macOS.
    """
    import socket
    
    # Find an available port
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    port = find_free_port()
    app = create_app()
    
    # Disable Flask's reloader for testing
    def run_server():
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    
    # Start server in a daemon thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to be ready
    max_attempts = 30
    base_url = f'http://localhost:{port}'
    for attempt in range(max_attempts):
        try:
            response = requests.get(base_url, timeout=1)
            if response.status_code in [200, 404, 500]:  # Any response means server is up
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(0.1)
    else:
        raise RuntimeError(f"Flask server failed to start on port {port} within 3 seconds")
    
    yield base_url
    
    # Server will be killed when thread exits (daemon thread)