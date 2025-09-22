import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from library_service import (
    calculate_late_fee_for_book
)

def test_calculate_late_fee_not_overdue():
    """Test late fee calculation for book not yet due (within 14 days)."""
    result = calculate_late_fee_for_book("P001", 1)
    print(f"Result: {result}")
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert 'status' in result

def test_calculate_late_fee_1_day_overdue():
    """Test late fee calculation for 1 day overdue ($0.50)."""
    result = calculate_late_fee_for_book("P001", 2)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 0.50
    assert result['days_overdue'] == 1
    assert 'status' in result

def test_calculate_late_fee_7_days_overdue():
    """Test late fee calculation for 7 days overdue ($3.50)."""
    result = calculate_late_fee_for_book("P001", 3)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 3.50  # 7 * $0.50
    assert result['days_overdue'] == 7
    assert 'status' in result

def test_calculate_late_fee_8_days_overdue():
    """Test late fee calculation for 8 days overdue (7 * $0.50 + 1 * $1.00 = $4.50)."""
    result = calculate_late_fee_for_book("P001", 4)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 4.50  # 7 * $0.50 + 1 * $1.00
    assert result['days_overdue'] == 8
    assert 'status' in result

def test_calculate_late_fee_maximum_cap():
    """Test late fee calculation hits maximum cap of $15.00."""
    result = calculate_late_fee_for_book("P001", 6)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 15.00  # Maximum cap
    assert result['days_overdue'] >= 21  # Would need 21+ days to hit $15 cap
    assert 'status' in result


def test_calculate_late_fee_invalid_patron_id():
    """Test late fee calculation with invalid patron ID."""
    result = calculate_late_fee_for_book("INVALID", 1)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert 'error' in result['status'].lower() or 'invalid' in result['status'].lower()

def test_calculate_late_fee_invalid_book_id():
    """Test late fee calculation with invalid book ID."""
    result = calculate_late_fee_for_book("P001", 999)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert 'error' in result['status'].lower() or 'invalid' in result['status'].lower()


def test_calculate_late_fee_book_not_borrowed():
    """Test late fee calculation for book not borrowed by patron."""
    result = calculate_late_fee_for_book("P001", 8)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert 'not borrowed' in result['status'].lower()


def test_calculate_late_fee_precision():
    """Test that fee amounts are calculated with proper precision (2 decimal places)."""
    result = calculate_late_fee_for_book("P001", 2)
    
    assert isinstance(result, dict)
    # Ensure fee_amount is rounded to 2 decimal places
    assert round(result['fee_amount'], 2) == result['fee_amount']

