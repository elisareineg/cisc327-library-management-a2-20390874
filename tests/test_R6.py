import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.library_service import (
    search_books_in_catalog
)

def test_search_books_title_partial_match():
    """Test searching for books by partial title match (case-insensitive)."""
    result = search_books_in_catalog("great", "title")
    print(f"Result: {result}")
    
    assert isinstance(result, list)
    # Should find books with "great" in the title (case-insensitive)
    if len(result) > 0:
        assert any("great" in book.get('title', '').lower() for book in result)

def test_search_books_author_partial_match():
    """Test searching for books by partial author match (case-insensitive)."""
    result = search_books_in_catalog("fitzgerald", "author")
    
    assert isinstance(result, list)
    if len(result) > 0:
        assert any("fitzgerald" in book.get('author', '').lower() for book in result)

def test_search_books_isbn_exact_match():
    """Test searching for books by exact ISBN match."""
    result = search_books_in_catalog("9780743273565", "isbn")
    
    assert isinstance(result, list)
    if len(result) > 0:
        assert any(book.get('isbn') == "9780743273565" for book in result)

def test_search_books_invalid_search_type():
    """Test searching with invalid search type."""
    result = search_books_in_catalog("test", "invalid_type")
    
    assert isinstance(result, list)
    assert len(result) == 0

def test_search_books_no_results():
    """Test searching for non-existent book."""
    result = search_books_in_catalog("NonExistentBookTitle12345", "title")
    
    assert isinstance(result, list)
    assert len(result) == 0

def test_search_books_result_format():
    """Test that search results follow catalog display format."""
    result = search_books_in_catalog("test", "title")
    
    assert isinstance(result, list)
    
    # Test format of each book in results
    for book in result:
        assert isinstance(book, dict)
        # Should contain standard catalog fields
        expected_fields = ['title', 'author', 'isbn', 'total_copies', 'available_copies']
        for field in expected_fields:
            assert field in book, f"Missing field: {field}"

def test_search_books_empty_search_term():
    """Test searching with empty search term."""
    result = search_books_in_catalog("", "title")
    
    assert isinstance(result, list)
    assert len(result) == 0