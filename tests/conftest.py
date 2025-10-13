"""
Pytest configuration file for Library Management System tests.
Handles database setup and teardown for test isolation.
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database, add_sample_data, DATABASE

@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """
    Setup a fresh database for each test function.
    This ensures test isolation and prevents tests from interfering with each other.
    """
    # Remove existing database if it exists
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    # Initialize fresh database with schema
    init_database()
    
    # Add sample data
    add_sample_data()
    
    yield
    
    # Cleanup after test
    if os.path.exists(DATABASE):
        os.remove(DATABASE)