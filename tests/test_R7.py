import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import (
    get_patron_status_report
)

def test_get_patron_status_report_valid():
    """Test getting patron status report with valid patron ID."""
    result = get_patron_status_report("123456")
    print(f"Result: {result}")
    
    # Assuming the function returns a dict with success status and data
    assert isinstance(result, dict)
    assert "success" in result
    assert "patron_id" in result
    assert "name" in result
    assert "books_borrowed" in result
    assert "books_overdue" in result
    assert "total_fines" in result

def test_get_patron_status_report_nonexistent_patron():
    """Test getting status report for non-existent patron."""
    result = get_patron_status_report("NONEXISTENT")
    
    assert isinstance(result, dict)
    assert result["success"] == False
    assert "patron not found" in result.get("message", "").lower()

def test_get_patron_status_report_empty_patron_id():
    """Test getting status report with empty patron ID."""
    result = get_patron_status_report("")
    
    assert isinstance(result, dict)
    assert result["success"] == False
    assert "patron id cannot be empty" in result.get("message", "").lower()

def test_get_patron_status_report_none_patron_id():
    """Test getting status report with None patron ID."""
    result = get_patron_status_report(None)
    
    assert isinstance(result, dict)
    assert result["success"] == False
    assert "invalid patron id" in result.get("message", "").lower()

def test_get_patron_status_report_with_borrowed_books():
    """Test patron status report for patron with borrowed books."""
    result = get_patron_status_report("P002")
    
    assert isinstance(result, dict)
    if result.get("success", False):
        assert isinstance(result["books_borrowed"], list)
        assert len(result["books_borrowed"]) > 0
        for book in result["books_borrowed"]:
            assert "isbn" in book
            assert "title" in book
            assert "due_date" in book

def test_get_patron_status_report_with_overdue_books():
    """Test patron status report for patron with overdue books."""
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    if result.get("success", False):
        assert isinstance(result["books_overdue"], list)
        if len(result["books_overdue"]) > 0:
            # Check structure of overdue book entries
            for book in result["books_overdue"]:
                assert "isbn" in book
                assert "title" in book
                assert "due_date" in book
                assert "days_overdue" in book

def test_get_patron_status_report_invalid_patron_id_format():
    """Test getting status report with invalid patron ID format."""
    result = get_patron_status_report("INVALID123")
    
    assert isinstance(result, dict)
    assert result["success"] == False
    assert ("invalid patron id format" in result.get("message", "").lower() or 
            "patron not found" in result.get("message", "").lower())