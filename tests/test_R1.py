import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import add_book_to_catalog
from database import init_database, get_db_connection

# Setup for clean test environment
@pytest.fixture(autouse=True)
def setup_database():
    """Setup clean database for each test."""
    init_database()
    yield
    # Cleanup after test
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE isbn NOT IN ("9780743273565", "9780061120084", "9780451524935")')
    conn.commit()
    conn.close()

def test_add_book_to_catalog():
    """Test adding a book with valid input."""
    result = add_book_to_catalog("Test Title", "Test Author", "1234567890124", 5)
    print(f"Result: {result}")  
    
    success, message = result
    print(f"Success: {success}, Message: {message}")  
    
    assert success == True
    assert "successfully added" in message.lower()

def test_title_exceeds_max_length():
    """Test title exceeds maximum length."""
    long_title = "a" * 201  # 201 characters
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890123", 5)

    assert success == False
    assert "less than 200 characters" in message.lower()

def test_title_empty():
    """Test empty title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "title is required" in message.lower()

def test_title_whitespace_only():
    """Test title with only whitespace."""
    success, message = add_book_to_catalog("   ", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "title is required" in message.lower()

def test_author_exceeds_max_length():
    """Test if author length exceeds 100 characters"""
    long_author = "a" * 101  # 101 characters
    success, message = add_book_to_catalog("Test Book", long_author, "1234567890123", 5)
    
    assert success == False
    assert "less than 100 characters" in message.lower()

def test_author_empty():
    """Test empty author."""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)
    
    assert success == False
    assert "author is required" in message.lower()

def test_author_whitespace_only():
    """Test author with only whitespace."""
    success, message = add_book_to_catalog("Test Book", "   ", "1234567890123", 5)
    
    assert success == False
    assert "author is required" in message.lower()

def test_isbn_length_too_short():
    """Test ISBN not being 13 digits."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789012", 5)
    
    assert success == False
    assert "exactly 13 digits" in message.lower()

def test_isbn_length_too_long():
    """Test ISBN being too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901234", 5)
    
    assert success == False
    assert "exactly 13 digits" in message.lower()

def test_isbn_non_numeric():
    """Test ISBN contains non-numeric characters."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789abcd", 5)
    
    assert success == False
    assert "exactly 13 digits" in message.lower()

def test_isbn_duplicate():
    """Test adding book with duplicate ISBN."""
    # Add first book
    add_book_to_catalog("First Book", "First Author", "9999999999999", 5)
    
    # Try to add book with same ISBN
    success, message = add_book_to_catalog("Second Book", "Second Author", "9999999999999", 3)
    
    assert success == False
    assert "already exists" in message.lower()

def test_copies_negative():
    """Test copies being negative."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -5)
    
    assert success == False
    assert "positive integer" in message.lower()

def test_add_book_zero_copies():
    """Test total copies is zero."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    
    assert success == False
    assert "positive integer" in message.lower()

def test_add_book_non_integer_copies():
    """Test total copies is not an integer."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", "five")
    
    assert success == False
    assert "positive integer" in message.lower()

def test_add_book_float_copies():
    """Test total copies is a float."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5.5)
    
    assert success == False
    assert "positive integer" in message.lower()
