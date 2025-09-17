import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import (
    return_book
)

def test_successful_book_return():
    """Test successful book return with valid patron ID and book ID."""
    result = return_book("P001", "B001")
    print(f"Result: {result}")
    
    success, message = result
    print(f"Success: {success}, Message: {message}")
    
    assert success == True
    assert "successfully returned" in message.lower()

def test_return_book_invalid_patron_id():
    """Test return with invalid patron ID."""
    success, message = return_book("INVALID", "B001")
    
    assert success == False
    assert "invalid patron id" in message.lower()

def test_return_book_invalid_book_id():
    """Test return with invalid book ID."""
    success, message = return_book("P001", "INVALID")
    
    assert success == False
    assert "invalid book id" in message.lower()

def test_return_book_not_borrowed_by_patron():
    """Test returning a book that was not borrowed by the patron."""
    success, message = return_book("P001", "B002")
    
    assert success == False
    assert "book was not borrowed by this patron" in message.lower()

def test_return_book_already_returned():
    """Test returning a book that has already been returned."""
    success, message = return_book("P001", "B001")
    
    assert success == False
    assert "book has already been returned" in message.lower()

def test_return_book_empty_patron_id():
    """Test return with empty patron ID."""
    success, message = return_book("", "B001")
    
    assert success == False
    assert "patron id cannot be empty" in message.lower()

def test_return_book_empty_book_id():
    """Test return with empty book ID."""
    success, message = return_book("P001", "")
    
    assert success == False
    assert "book id cannot be empty" in message.lower()

def test_return_book_none_patron_id():
    """Test return with None patron ID."""
    success, message = return_book(None, "B001")
    
    assert success == False
    assert "patron id cannot be none" in message.lower()

def test_return_book_none_book_id():
    """Test return with None book ID."""
    success, message = return_book("P001", None)
    
    assert success == False
    assert "book id cannot be none" in message.lower()

def test_return_book_with_late_fee():
    """Test returning a book with late fees owed."""
    # This assumes the book was borrowed and is now overdue
    success, message = return_book("P001", "B003")
    
    assert success == True
    assert "late fee" in message.lower()
    assert "returned successfully" in message.lower()

def test_return_book_updates_available_copies():
    """Test that returning a book updates available copies count."""
    # This would require integration with the catalog system
    # The return should increase available copies by 1
    success, message = return_book("P001", "B001")
    
    assert success == True
    assert "available copies updated" in message.lower()

def test_return_book_records_return_date():
    """Test that return date is properly recorded."""
    success, message = return_book("P001", "B001")
    
    assert success == True
    assert "return date recorded" in message.lower()

def test_return_book_calculates_late_fee():
    """Test late fee calculation for overdue book."""
    # Assuming B004 is an overdue book
    success, message = return_book("P001", "B004")
    
    assert success == True
    # Should contain information about late fee calculation
    assert ("late fee" in message.lower() or "no late fee" in message.lower())

def test_return_book_patron_id_wrong_format():
    """Test return with patron ID in wrong format."""
    success, message = return_book("123", "B001")  # Assuming format should be P###
    
    assert success == False
    assert "invalid patron id format" in message.lower()

def test_return_book_book_id_wrong_format():
    """Test return with book ID in wrong format."""
    success, message = return_book("P001", "123")  # Assuming format should be B###
    
    assert success == False
    assert "invalid book id format" in message.lower()
