
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.library_service import borrow_book_by_patron
from database import get_db_connection

def test_book_borrow_success():
    """Test borrowing a book with valid input."""
    result = borrow_book_by_patron("123458", 1)  # The Great Gatsby - use a new patron
    print(f"Result: {result}")
    
    success, message = result
    print(f"Success: {success}, Message: {message}")
    
    assert success == True
    assert "successfully borrowed" in message.lower()

def test_patron_id_length_too_short():
    """Test patron ID not being 6 digits (too short)."""
    success, message = borrow_book_by_patron("12345", 1)
    print(f"Result: {message}")
    
    assert success == False
    assert "exactly 6 digits" in message.lower()

def test_patron_id_length_too_long():
    """Test patron ID being too long."""
    success, message = borrow_book_by_patron("1234567", 1)
    print(f"Result: {message}")
    
    assert success == False
    assert "exactly 6 digits" in message.lower()

def test_patron_id_non_numeric():
    """Test patron ID contains non-numeric characters."""
    success, message = borrow_book_by_patron("1234a6", 1)
    print(f"Result: {message}")
    
    assert success == False
    assert "exactly 6 digits" in message.lower()

def test_patron_id_empty():
    """Test empty patron ID."""
    success, message = borrow_book_by_patron("", 1)
    print(f"Result: {message}")
    
    assert success == False
    assert "invalid patron id" in message.lower()

def test_book_not_available():
    """Test borrowing a book that is not available."""
    # Book 3 (1984) is already borrowed in sample data
    success, message = borrow_book_by_patron("123458", 3)
    print(f"Result: {message}")
    
    assert success == False
    assert "not available" in message.lower()

def test_book_not_found():
    """Test borrowing a book that doesn't exist."""
    success, message = borrow_book_by_patron("123458", 9999)
    print(f"Result: {message}")
    
    assert success == False
    assert "not found" in message.lower()

def test_already_borrowed_same_book():
    """Test borrowing a book that the patron has already borrowed."""
    patron_id = "123459"
    
    # First borrow - use book 2 which has available copies
    borrow_book_by_patron(patron_id, 2)
    
    # Try to borrow again
    success, message = borrow_book_by_patron(patron_id, 2)
    print(f"Result: {message}")
    
    assert success == False
    assert "already borrowed" in message.lower()

def test_maximum_borrowing_limit():
    """Test that patron cannot borrow more than 5 books."""
    patron_id = "123460"
    
    # Borrow 5 books (all available books from sample data and create more if needed)
    borrow_book_by_patron(patron_id, 1)  # The Great Gatsby
    borrow_book_by_patron(patron_id, 2)  # To Kill a Mockingbird
    
    # Add more books to database for this test
    conn = get_db_connection()
    for i in range(10, 14):  # Add books with IDs 10-13
        conn.execute('''
            INSERT INTO books (id, title, author, isbn, total_copies, available_copies)
            VALUES (?, ?, ?, ?, 1, 1)
        ''', (i, f"Test Book {i}", f"Author {i}", f"{i:013d}"))
    conn.commit()
    conn.close()
    
    borrow_book_by_patron(patron_id, 10)
    borrow_book_by_patron(patron_id, 11)
    borrow_book_by_patron(patron_id, 12)
    
    # Now try to borrow a 6th book (should fail)
    success, message = borrow_book_by_patron(patron_id, 13)
    print(f"Result: {message}")
    
    assert success == False
    assert "maximum borrowing limit" in message.lower()

def test_borrow_decrements_available_copies():
    """Test that borrowing a book decrements available copies."""
    conn = get_db_connection()
    book = conn.execute('SELECT available_copies FROM books WHERE id = 2').fetchone()
    initial_copies = book['available_copies']
    conn.close()
    
    # Borrow the book
    borrow_book_by_patron("111111", 2)
    
    # Check available copies decreased
    conn = get_db_connection()
    book = conn.execute('SELECT available_copies FROM books WHERE id = 2').fetchone()
    final_copies = book['available_copies']
    conn.close()
    
    assert final_copies == initial_copies - 1

    
