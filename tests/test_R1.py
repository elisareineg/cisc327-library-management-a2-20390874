import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import (
    add_book_to_catalog
)

def test_add_book_to_catalog():
    """Test adding a book with valid input."""
    result = add_book_to_catalog("Test Title", "Test Author", "1234567890124", 5)
    print(f"Result: {result}")  
    
    success, message = result
    print(f"Success: {success}, Message: {message}")  
    
    assert success == True
    assert "successfully added" in message.lower()

def test_title():
    """Test title exceeds maximum length."""
    long_title = "a" * 201  # 201 characters
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890123", 5)

    assert success == False
    assert "Title too long" in message.lower()

def test_author():
    "Test if author length exceeds 100 characters"
    long_author = "a" * 101  # 101 characters
    success, message = add_book_to_catalog("Test Book", long_author, "1234567890123", 5)
    assert success == False
    assert "Author name too long" in message.lower()

def test_isbn_length():
    """Test ISBN not being 13 digits."""
    isbn_length = 13
    success, message = add_book_to_catalog("Test Book", "Test Author", "1" * (isbn_length - 1), 5)
    assert success == False
    assert "not 13 digits" in message

def test_isbn_non_numeric():
    """Test ISBN contains non-numeric characters."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789abcd", '$')
    
    assert success == False
    assert "isbn must be a 13-digit number" in message.lower()


def test_copies():
    """Test copies being negative."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -5)
    assert success == False
    assert "cannot be negative" in message.lower()

def test_add_book_zero_copies():
    """Test total copies is zero."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    
    assert success == False
    assert "total copies must be a positive integer" in message.lower()


def test_add_book_non_integer_copies():
    """Test total copies is not an integer."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", "five")
    
    assert success == False
    assert "total copies must be a positive integer" in message.lower()
