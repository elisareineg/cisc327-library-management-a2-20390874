"""
Task 2.1: Stubbing and Mocking Tests
Comprehensive unit tests for pay_late_fees and refund_late_fee_payment
using both stubbing and mocking techniques.
"""

import pytest
import sys
import os
from unittest.mock import Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway


class TestPayLateFees:
    """Test suite for pay_late_fees function using stubbing and mocking."""
    
    def test_successful_payment(self, mocker):
        """
        Test successful payment processing.
        Stubs: calculate_late_fee_for_book, get_book_by_id
        Mocks: payment_gateway.process_payment
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_123456_001", "Payment of $5.50 processed successfully")
        
        # Stub calculate_late_fee_for_book to return a fee
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={
                'fee_amount': 5.50,
                'days_overdue': 3,
                'status': 'Overdue'
            }
        )
        
        # Stub get_book_by_id to return book info
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value={
                'id': 1,
                'title': 'Test Book',
                'author': 'Test Author',
                'isbn': '1234567890123',
                'total_copies': 5,
                'available_copies': 3
            }
        )
        
        # Call the function
        success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
        
        # Assertions
        assert success is True
        assert "Payment successful" in message
        assert transaction_id == "txn_123456_001"
        
        # Verify mock was called correctly
        mock_gateway.process_payment.assert_called_once_with(
            patron_id="123456",
            amount=5.50,
            description="Late fees for 'Test Book'"
        )
    
    def test_payment_declined_by_gateway(self, mocker):
        """
        Test payment declined by gateway.
        Stubs: calculate_late_fee_for_book, get_book_by_id
        Mocks: payment_gateway.process_payment (returns failure)
        """
        # mock payment gateway that declines payment
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (False, "", "Payment declined by gateway")
        
        # Stub calculate_late_fee_for_book
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={
                'fee_amount': 10.00,
                'days_overdue': 10,
                'status': 'Overdue'
            }
        )
        
        # Stub get_book_by_id
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value={
                'id': 2,
                'title': 'Another Book',
                'author': 'Another Author',
                'isbn': '9876543210987',
                'total_copies': 3,
                'available_copies': 1
            }
        )
        
        # Call 
        success, message, transaction_id = pay_late_fees("123456", 2, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Payment failed" in message
        assert transaction_id is None
        
        # Verify mock was called
        mock_gateway.process_payment.assert_called_once()
    
    def test_invalid_patron_id_mock_not_called(self, mocker):
        """
        Test invalid patron ID - verify mock NOT called.
        Stubs: Not needed (early return)
        Mocks: payment_gateway.process_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Call with invalid patron ID
        success, message, transaction_id = pay_late_fees("12345", 1, mock_gateway)  # Only 5 digits
        
        # Assertions
        assert success is False
        assert "Invalid patron ID" in message
        assert transaction_id is None
        
        # Verify mock was NOT called
        mock_gateway.process_payment.assert_not_called()
    
    def test_zero_late_fees_mock_not_called(self, mocker):
        """
        Test zero late fees - verify mock NOT called.
        Stubs: calculate_late_fee_for_book (returns zero fee)
        Mocks: payment_gateway.process_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Stub calculate_late_fee_for_book to return zero fee
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={
                'fee_amount': 0.00,
                'days_overdue': 0,
                'status': 'Not overdue'
            }
        )
        
        # Call the function
        success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
        
        # Assertions
        assert success is False
        assert "No late fees to pay" in message
        assert transaction_id is None
        
        # Verify mock was NOT called
        mock_gateway.process_payment.assert_not_called()
    
    def test_network_error_exception_handling(self, mocker):
        """
        Test network error exception handling.
        Stubs: calculate_late_fee_for_book, get_book_by_id
        Mocks: payment_gateway.process_payment (raises exception)
        """
        # Create a mock payment gateway that raises an exception
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.side_effect = ConnectionError("Network connection failed")
        
        # Stub calculate_late_fee_for_book
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={
                'fee_amount': 7.50,
                'days_overdue': 5,
                'status': 'Overdue'
            }
        )
        
        # Stub get_book_by_id
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value={
                'id': 3,
                'title': 'Network Test Book',
                'author': 'Test Author',
                'isbn': '1111111111111',
                'total_copies': 2,
                'available_copies': 1
            }
        )
        
        # Call the function
        success, message, transaction_id = pay_late_fees("123456", 3, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Payment processing error" in message or "error" in message.lower()
        assert transaction_id is None
        
        # Verify mock was called
        mock_gateway.process_payment.assert_called_once()


class TestRefundLateFeePayment:
    """Test suite for refund_late_fee_payment function using stubbing and mocking."""
    
    def test_successful_refund(self, mocker):
        """
        Test successful refund processing.
        Mocks: payment_gateway.refund_payment
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (True, "Refund processed successfully")
        
        # Call the function
        success, message = refund_late_fee_payment("txn_123456_001", 5.50, mock_gateway)
        
        # Assertions
        assert success is True
        assert "Refund" in message or "successfully" in message.lower()
        
        # Verify mock was called correctly (positional arguments)
        mock_gateway.refund_payment.assert_called_once_with("txn_123456_001", 5.50)
    
    def test_invalid_transaction_id_rejection(self, mocker):
        """
        Test invalid transaction ID rejection.
        Mocks: payment_gateway.refund_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Call with empty transaction ID
        success, message = refund_late_fee_payment("", 5.50, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Invalid transaction ID" in message
        
        # Verify mock was NOT called
        mock_gateway.refund_payment.assert_not_called()
        
        # Test with whitespace-only transaction ID (should fail validation)
        success2, message2 = refund_late_fee_payment("   ", 5.50, mock_gateway)
        assert success2 is False
        assert "Invalid transaction ID" in message2
        assert mock_gateway.refund_payment.call_count == 0
    
    def test_negative_refund_amount(self, mocker):
        """
        Test invalid refund amount - negative amount.
        Mocks: payment_gateway.refund_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Call with negative amount
        success, message = refund_late_fee_payment("txn_123456_001", -5.50, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Refund amount must be greater than 0" in message
        
        # Verify mock was NOT called
        mock_gateway.refund_payment.assert_not_called()
    
    def test_zero_refund_amount(self, mocker):
        """
        Test invalid refund amount - zero amount.
        Mocks: payment_gateway.refund_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Call with zero amount
        success, message = refund_late_fee_payment("txn_123456_001", 0, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Refund amount must be greater than 0" in message
        
        # Verify mock was NOT called
        mock_gateway.refund_payment.assert_not_called()
    
    def test_refund_amount_exceeds_maximum(self, mocker):
        """
        Test invalid refund amount - exceeds $15 maximum.
        Mocks: payment_gateway.refund_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Call with amount exceeding $15.00
        success, message = refund_late_fee_payment("txn_123456_001", 20.00, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Refund amount exceeds maximum late fee" in message
        
        # Verify mock was NOT called
        mock_gateway.refund_payment.assert_not_called()
        
        # Test with exactly $15.01
        success2, message2 = refund_late_fee_payment("txn_123456_001", 15.01, mock_gateway)
        assert success2 is False
        assert "Refund amount exceeds maximum late fee" in message2
        assert mock_gateway.refund_payment.call_count == 0
    
    def test_refund_at_maximum_amount(self, mocker):
        """
        Test successful refund at maximum amount ($15.00).
        Mocks: payment_gateway.refund_payment
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (True, "Refund processed successfully")
        
        # Call with maximum amount
        success, message = refund_late_fee_payment("txn_123456_001", 15.00, mock_gateway)
        
        # Assertions
        assert success is True
        assert "Refund" in message or "successfully" in message.lower()
        
        # Verify mock was called with correct amount (positional arguments)
        mock_gateway.refund_payment.assert_called_once_with("txn_123456_001", 15.00)
    
    def test_refund_gateway_failure(self, mocker):
        """
        Test refund when gateway returns failure.
        Mocks: payment_gateway.refund_payment (returns failure)
        """
        # Create a mock payment gateway that fails
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (False, "Transaction not found")
        
        # Call the function
        success, message = refund_late_fee_payment("txn_invalid_001", 5.50, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Refund failed" in message or "error" in message.lower()
        
        # Verify mock was called (positional arguments)
        mock_gateway.refund_payment.assert_called_once_with("txn_invalid_001", 5.50)

