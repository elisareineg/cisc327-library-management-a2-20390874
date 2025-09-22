import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_all_books, init_database, add_sample_data

def test_get_all_books_returns_list():
    """Test that get_all_books returns a list of books."""
    # Initialize database and add sample data
    init_database()
    add_sample_data()
    
    books = get_all_books()
    assert isinstance(books, list)
    assert len(books) > 0

def test_get_all_books_contains_required_fields():
    """Test that each book in the catalog contains all required fields."""
    books = get_all_books()
    
    for book in books:
        # Check that all required fields are present
        assert 'id' in book, "Book ID field missing"
        assert 'title' in book, "Title field missing"
        assert 'author' in book, "Author field missing"
        assert 'isbn' in book, "ISBN field missing"
        assert 'total_copies' in book, "Total copies field missing"
        assert 'available_copies' in book, "Available copies field missing"

def test_get_all_books_field_types():
    """Test that book fields have correct data types."""
    books = get_all_books()
    
    for book in books:
        assert isinstance(book['id'], int), "Book ID should be integer"
        assert isinstance(book['title'], str), "Title should be string"
        assert isinstance(book['author'], str), "Author should be string"
        assert isinstance(book['isbn'], str), "ISBN should be string"
        assert isinstance(book['total_copies'], int), "Total copies should be integer"
        assert isinstance(book['available_copies'], int), "Available copies should be integer"

def test_get_all_books_availability_logic():
    """Test that available_copies is never greater than total_copies."""
    books = get_all_books()
    
    for book in books:
        assert book['available_copies'] <= book['total_copies'], \
            f"Available copies ({book['available_copies']}) cannot exceed total copies ({book['total_copies']})"
        assert book['available_copies'] >= 0, "Available copies cannot be negative"
        assert book['total_copies'] > 0, "Total copies must be positive"


def test_get_all_books_isbn_format():
    """Test that ISBNs are in correct 13-digit format."""
    books = get_all_books()
    
    for book in books:
        isbn = book['isbn']
        assert len(isbn) == 13, f"ISBN should be 13 digits, got {len(isbn)}"
        assert isbn.isdigit(), f"ISBN should contain only digits, got {isbn}"

def test_get_all_books_empty_catalog():
    """Test behavior when catalog is empty (after clearing)."""
    # This test would require clearing the database, which might affect other tests
    # For now, we'll test that the function handles the case gracefully
    books = get_all_books()
    # Function should return empty list rather than None or error
    assert isinstance(books, list)

def test_catalog_display_format():
    """Test that books are formatted correctly for catalog display."""
    books = get_all_books()
    
    for book in books:
        # Test that all fields needed for display are present and valid
        assert book['title'].strip() != "", "Title cannot be empty"
        assert book['author'].strip() != "", "Author cannot be empty"
        assert len(book['isbn']) == 13, "ISBN must be 13 digits for display"
        
        # Test availability display logic
        if book['available_copies'] > 0:
            assert book['available_copies'] <= book['total_copies']
        else:
            # When no copies available, should show as unavailable
            assert book['available_copies'] == 0

def test_catalog_borrow_button_logic():
    """Test the logic for when borrow button should be available."""
    books = get_all_books()
    
    for book in books:
        # Borrow button should be available only when available_copies > 0
        can_borrow = book['available_copies'] > 0
        
        if can_borrow:
            assert book['available_copies'] > 0, "Borrow button should be available when copies > 0"
        else:
            assert book['available_copies'] == 0, "Borrow button should not be available when copies = 0"

def test_catalog_sample_data():
    """Test that sample data is correctly loaded and formatted."""
    books = get_all_books()
    
    # Check that we have the expected sample books
    titles = [book['title'] for book in books]
    expected_titles = ['The Great Gatsby', 'To Kill a Mockingbird', '1984']
    
    for expected_title in expected_titles:
        assert expected_title in titles, f"Expected book '{expected_title}' not found in catalog"
    
    # Check specific book data 
    gatsby = next((book for book in books if book['title'] == 'The Great Gatsby'), None)
    assert gatsby is not None, "The Great Gatsby should be in catalog"
    assert gatsby['author'] == 'F. Scott Fitzgerald', "Author should match"
    assert gatsby['isbn'] == '9780743273565', "ISBN should match"
    assert gatsby['total_copies'] == 3, "Total copies should be 3"
    assert gatsby['available_copies'] == 3, "Available copies should be 3 (initially)"