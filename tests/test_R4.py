import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import (
    return_book_by_patron
)

def test_successful_book_return():
    """Test successful book return with valid patron ID and book ID."""
    result = return_book_by_patron("123457", 1)
    print(f"Result: {result}")
    
    success, message = result
    print(f"Success: {success}, Message: {message}")
    
    assert success == True
    assert "successfully returned" in message.lower()

def test_invalid_patron_id():
    """Test return with invalid patron ID."""
    success, message = return_book_by_patron("INVALID", "B001")
    
    assert success == False
    assert "invalid patron id" in message.lower()

def test_invalid_book_id():
    """Test return with invalid book ID."""
    success, message = return_book_by_patron("123456", 999)
    
    assert success == False
    assert "book not found" in message.lower()

def test_book_not_borrowed_by_patron():
    """Test returning a book that was not borrowed by the patron."""
    # Use a different patron who hasn't borrowed book 1
    success, message = return_book_by_patron("999999", 1)
    
    assert success == False
    assert "not borrowed" in message.lower()

def test_empty_or_none_inputs():
    """Test return with empty or None inputs."""
    # Test empty patron ID
    success, message = return_book_by_patron("", 1)
    assert success == False
    assert "invalid patron id" in message.lower()
    
    # Test None patron ID
    success, message = return_book_by_patron(None, 1)
    assert success == False
    assert "invalid patron id" in message.lower()

def test_book_with_late_fee():
    """Test returning an overdue book that incurs late fees."""
    success, message = return_book_by_patron("123456", 3)
    
    assert success == True
    assert "late fee" in message.lower()
    assert "returned" in message.lower()

def test_already_returned_book():
    """Test returning a book that has already been returned."""
    # First return the book
    return_book_by_patron("123456", 3)
    
    # Try to return it again
    success, message = return_book_by_patron("123456", 3)
    
    assert success == False
    assert "not borrowed" in message.lower()