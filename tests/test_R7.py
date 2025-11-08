import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.library_service import (
    get_patron_status_report
)

def test_get_patron_status_report_valid():
    """Test getting patron status report with valid patron ID."""
    # Use the patron from sample data who has borrowed book 3
    result = get_patron_status_report("123456")
    print(f"Result: {result}")
    
    assert isinstance(result, dict)
    assert result["success"] == True
    assert "patron_id" in result
    assert "books_borrowed" in result
    assert "books_overdue" in result
    assert "total_fines" in result
    assert "total_books_borrowed" in result
    assert "total_overdue" in result

def test_get_patron_status_report_invalid_patron_id():
    """Test getting status report with invalid patron ID format."""
    result = get_patron_status_report("INVALID")
    
    assert isinstance(result, dict)
    assert result["success"] == False
    assert "invalid patron id" in result.get("message", "").lower()

def test_get_patron_status_report_wrong_length():
    """Test getting status report with wrong length patron ID."""
    result = get_patron_status_report("12345")
    
    assert isinstance(result, dict)
    assert result["success"] == False
    assert "exactly 6 digits" in result.get("message", "").lower()

def test_get_patron_status_report_empty_patron_id():
    """Test getting status report with empty patron ID."""
    result = get_patron_status_report("")
    
    assert isinstance(result, dict)
    assert result["success"] == False
    assert "invalid patron id" in result.get("message", "").lower()

def test_get_patron_status_report_none_patron_id():
    """Test getting status report with None patron ID."""
    result = get_patron_status_report(None)
    
    assert isinstance(result, dict)
    assert result["success"] == False
    assert "invalid patron id" in result.get("message", "").lower()

def test_get_patron_status_report_with_borrowed_books():
    """Test patron status report for patron with borrowed books."""
    # Sample data has patron 123456 with book 3 borrowed
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    assert result["success"] == True
    assert isinstance(result["books_borrowed"], list)
    assert isinstance(result["books_overdue"], list)
    
    # Total borrowed should include both current and overdue
    total_books = len(result["books_borrowed"]) + len(result["books_overdue"])
    assert total_books > 0
    
    # Check structure of book entries
    all_books = result["books_borrowed"] + result["books_overdue"]
    for book in all_books:
        assert "book_id" in book
        assert "title" in book
        assert "author" in book
        assert "borrow_date" in book
        assert "due_date" in book

def test_get_patron_status_report_with_overdue_books():
    """Test patron status report for patron with overdue books."""
    # Sample data has patron 123456 with book 3 overdue
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    assert result["success"] == True
    assert isinstance(result["books_overdue"], list)
    
    if len(result["books_overdue"]) > 0:
        # Check structure of overdue book entries
        for book in result["books_overdue"]:
            assert "book_id" in book
            assert "title" in book
            assert "author" in book
            assert "due_date" in book
            assert "days_overdue" in book
            assert "late_fee" in book
            assert book["days_overdue"] > 0
            assert book["late_fee"] > 0

def test_get_patron_status_report_no_books():
    """Test patron status report for patron with no borrowed books."""
    result = get_patron_status_report("999999")
    
    assert isinstance(result, dict)
    assert result["success"] == True
    assert result["total_books_borrowed"] == 0
    assert result["total_overdue"] == 0
    assert result["total_fines"] == 0.00
    assert len(result["books_borrowed"]) == 0
    assert len(result["books_overdue"]) == 0

def test_get_patron_status_report_total_fines_calculation():
    """Test that total fines are calculated correctly."""
    # Sample data patron 123456 has overdue book
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    if result["success"] and len(result["books_overdue"]) > 0:
        # Calculate sum of individual late fees
        calculated_total = sum(book["late_fee"] for book in result["books_overdue"])
        assert result["total_fines"] == calculated_total

def test_get_patron_status_report_counts_match():
    """Test that count fields match the actual list lengths."""
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    if result["success"]:
        total_borrowed = len(result["books_borrowed"]) + len(result["books_overdue"])
        assert result["total_books_borrowed"] == total_borrowed
        assert result["total_overdue"] == len(result["books_overdue"])

def test_get_patron_status_report_data_types():
    """Test that all fields have correct data types."""
    result = get_patron_status_report("123456")
    
    assert isinstance(result, dict)
    if result["success"]:
        assert isinstance(result["patron_id"], str)
        assert isinstance(result["books_borrowed"], list)
        assert isinstance(result["books_overdue"], list)
        assert isinstance(result["total_fines"], (int, float))
        assert isinstance(result["total_books_borrowed"], int)
        assert isinstance(result["total_overdue"], int)