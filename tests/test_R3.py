import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import (
    add_book_to_catalog
)

def test_book_borrow():
    """Test borrowing a book with valid input."""
    result = add_book_to_catalog("Test Title", "Test Author", "1234567890124", 5)
    print(f"Result: {result}")  
    
    success, message = result
    print(f"Success: {success}, Message: {message}")  
    
    assert success == True
    assert "successfully added" in message.lower()