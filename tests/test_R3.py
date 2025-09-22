import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import (
    borrow_book_by_patron
)

def test_book_borrow():
    """Test borrowing a book with valid input."""
    result = borrow_book_by_patron("123457", 8)
    print(f"Result: {result}")  
    
    success, message = result
    print(f"Success: {success}, Message: {message}")  
    
    assert success == True
    assert "successfully borrowed" in message.lower()
    

def test_patron_id_length():
    """Test patron ID not being 6 digits."""
    success, message = borrow_book_by_patron("12345", 7)
    print(f"Result: {message}")
    
    assert success == False
    assert "exactly 6 digits" in message.lower()

def test_patron_id_non_numeric():
    """Test patron ID contains non-numeric characters."""
    success, message = borrow_book_by_patron("1234a6", 7)
    print(f"Result: {message}")
    
    assert success == False
    assert "exactly 6 digits" in message.lower()

def test_book_availability():
    """Test borrowing a book that is not available."""
    success, message = borrow_book_by_patron("123458", 5)
    print(f"Result: {message}")
    
    assert success == False
    assert "not available" in message.lower()

def test_borrowing_record():
    """Test borrowing a book that the patron has already borrowed."""
    success, message = borrow_book_by_patron("123459", 8)
    print(f"Result: {message}")
    
    assert success == False
    assert "already borrowed" in message.lower()

def test_maximum_borrowing_limit():
    """Test that patron cannot borrow more than 5 books."""
    # Assuming patron 123460 has already borrowed 5 books
    success, message = borrow_book_by_patron("123460", 9)
    print(f"Result: {message}")
    
    assert success == False
    assert "maximum borrowing limit" in message.lower()

    
