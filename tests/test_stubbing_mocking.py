"""
Task 2.1: Stubbing and Mocking Tests
Comprehensive unit tests for pay_late_fees and refund_late_fee_payment
using both stubbing and mocking techniques.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

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
    
    def test_pay_late_fees_no_fee_info(self, mocker):
        """
        Test pay_late_fees when calculate_late_fee_for_book returns None or invalid.
        Stubs: calculate_late_fee_for_book (returns None)
        Mocks: payment_gateway.process_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Stub calculate_late_fee_for_book to return None
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value=None
        )
        
        # Call the function
        success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Unable to calculate late fees" in message
        assert transaction_id is None
        
        # Verify mock was NOT called
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_missing_fee_amount_key(self, mocker):
        """
        Test pay_late_fees when fee_info doesn't have 'fee_amount' key.
        Stubs: calculate_late_fee_for_book (returns dict without fee_amount)
        Mocks: payment_gateway.process_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Stub calculate_late_fee_for_book to return dict without fee_amount
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={'days_overdue': 5, 'status': 'Overdue'}
        )
        
        # Call the function
        success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Unable to calculate late fees" in message
        assert transaction_id is None
        
        # Verify mock was NOT called
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_book_not_found(self, mocker):
        """
        Test pay_late_fees when book is not found.
        Stubs: calculate_late_fee_for_book, get_book_by_id (returns None)
        Mocks: payment_gateway.process_payment (should not be called)
        """
        # Create a mock payment gateway
        mock_gateway = Mock(spec=PaymentGateway)
        
        # Stub calculate_late_fee_for_book
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={
                'fee_amount': 5.50,
                'days_overdue': 3,
                'status': 'Overdue'
            }
        )
        
        # Stub get_book_by_id to return None
        mocker.patch(
            'services.library_service.get_book_by_id',
            return_value=None
        )
        
        # Call the function
        success, message, transaction_id = pay_late_fees("123456", 999, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Book not found" in message
        assert transaction_id is None
        
        # Verify mock was NOT called
        mock_gateway.process_payment.assert_not_called()
    
    def test_pay_late_fees_default_gateway_creation(self, mocker):
        """
        Test pay_late_fees creates default PaymentGateway when None is provided.
        Stubs: calculate_late_fee_for_book, get_book_by_id
        Mocks: PaymentGateway initialization
        """
        # Stub calculate_late_fee_for_book
        mocker.patch(
            'services.library_service.calculate_late_fee_for_book',
            return_value={
                'fee_amount': 5.50,
                'days_overdue': 3,
                'status': 'Overdue'
            }
        )
        
        # Stub get_book_by_id
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
        
        # Mock PaymentGateway class
        mock_gateway_instance = Mock()
        mock_gateway_instance.process_payment.return_value = (True, "txn_123", "Success")
        mocker.patch('services.library_service.PaymentGateway', return_value=mock_gateway_instance)
        
        # Call the function without providing gateway
        success, message, transaction_id = pay_late_fees("123456", 1, None)
        
        # Assertions
        assert success is True
        assert transaction_id == "txn_123"


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
    
    def test_refund_late_fee_payment_default_gateway_creation(self, mocker):
        """
        Test refund_late_fee_payment creates default PaymentGateway when None is provided.
        Mocks: PaymentGateway initialization
        """
        # Mock PaymentGateway class
        mock_gateway_instance = Mock()
        mock_gateway_instance.refund_payment.return_value = (True, "Refund successful")
        mocker.patch('services.library_service.PaymentGateway', return_value=mock_gateway_instance)
        
        # Call the function without providing gateway
        success, message = refund_late_fee_payment("txn_123456_001", 5.50, None)
        
        # Assertions
        assert success is True
        assert "Refund successful" in message
    
    def test_refund_late_fee_payment_exception_handling(self, mocker):
        """
        Test refund_late_fee_payment handles exceptions from gateway.
        Mocks: payment_gateway.refund_payment (raises exception)
        """
        # Create a mock payment gateway that raises an exception
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.side_effect = ConnectionError("Network error")
        
        # Call the function
        success, message = refund_late_fee_payment("txn_123456_001", 5.50, mock_gateway)
        
        # Assertions
        assert success is False
        assert "Refund processing error" in message
        assert "Network error" in message


class TestPaymentGateway:
    """Test suite for PaymentGateway class from payment_service.py."""
    
    def test_init_default_api_key(self):
        """Test PaymentGateway initialization with default API key."""
        gateway = PaymentGateway()
        assert gateway.api_key == "test_key_12345"
        assert gateway.base_url == "https://api.payment-gateway.example.com"
    
    def test_init_custom_api_key(self):
        """Test PaymentGateway initialization with custom API key."""
        gateway = PaymentGateway(api_key="custom_key_123")
        assert gateway.api_key == "custom_key_123"
    
    @patch('services.payment_service.time.sleep')
    def test_process_payment_success(self, mock_sleep):
        """Test successful payment processing."""
        gateway = PaymentGateway()
        success, transaction_id, message = gateway.process_payment("123456", 10.50, "Late fees")
        
        assert success is True
        assert transaction_id.startswith("txn_123456_")
        assert "Payment of $10.50 processed successfully" in message
        mock_sleep.assert_called_once_with(0.5)
    
    @patch('services.payment_service.time.sleep')
    def test_process_payment_zero_amount(self, mock_sleep):
        """Test payment with zero amount."""
        gateway = PaymentGateway()
        success, transaction_id, message = gateway.process_payment("123456", 0, "Late fees")
        
        assert success is False
        assert transaction_id == ""
        assert "Invalid amount: must be greater than 0" in message
    
    @patch('services.payment_service.time.sleep')
    def test_process_payment_negative_amount(self, mock_sleep):
        """Test payment with negative amount."""
        gateway = PaymentGateway()
        success, transaction_id, message = gateway.process_payment("123456", -10.50, "Late fees")
        
        assert success is False
        assert transaction_id == ""
        assert "Invalid amount: must be greater than 0" in message
    
    @patch('services.payment_service.time.sleep')
    def test_process_payment_amount_exceeds_limit(self, mock_sleep):
        """Test payment with amount exceeding $1000 limit."""
        gateway = PaymentGateway()
        success, transaction_id, message = gateway.process_payment("123456", 1001.00, "Late fees")
        
        assert success is False
        assert transaction_id == ""
        assert "Payment declined: amount exceeds limit" in message
    
    @patch('services.payment_service.time.sleep')
    def test_process_payment_invalid_patron_id_short(self, mock_sleep):
        """Test payment with invalid patron ID (too short)."""
        gateway = PaymentGateway()
        success, transaction_id, message = gateway.process_payment("12345", 10.50, "Late fees")
        
        assert success is False
        assert transaction_id == ""
        assert "Invalid patron ID format" in message
    
    @patch('services.payment_service.time.sleep')
    def test_process_payment_invalid_patron_id_long(self, mock_sleep):
        """Test payment with invalid patron ID (too long)."""
        gateway = PaymentGateway()
        success, transaction_id, message = gateway.process_payment("1234567", 10.50, "Late fees")
        
        assert success is False
        assert transaction_id == ""
        assert "Invalid patron ID format" in message
    
    @patch('services.payment_service.time.sleep')
    def test_process_payment_empty_description(self, mock_sleep):
        """Test payment with empty description."""
        gateway = PaymentGateway()
        success, transaction_id, message = gateway.process_payment("123456", 10.50, "")
        
        assert success is True
        assert transaction_id.startswith("txn_123456_")
    
    @patch('services.payment_service.time.sleep')
    def test_refund_payment_success(self, mock_sleep):
        """Test successful refund processing."""
        gateway = PaymentGateway()
        success, message = gateway.refund_payment("txn_123456_001", 10.50)
        
        assert success is True
        assert "Refund of $10.50 processed successfully" in message
        assert "Refund ID: refund_txn_123456_001_" in message
        mock_sleep.assert_called_once_with(0.5)
    
    @patch('services.payment_service.time.sleep')
    def test_refund_payment_invalid_transaction_id_empty(self, mock_sleep):
        """Test refund with empty transaction ID."""
        gateway = PaymentGateway()
        success, message = gateway.refund_payment("", 10.50)
        
        assert success is False
        assert "Invalid transaction ID" in message
    
    @patch('services.payment_service.time.sleep')
    def test_refund_payment_invalid_transaction_id_format(self, mock_sleep):
        """Test refund with invalid transaction ID format."""
        gateway = PaymentGateway()
        success, message = gateway.refund_payment("INVALID_123", 10.50)
        
        assert success is False
        assert "Invalid transaction ID" in message
    
    @patch('services.payment_service.time.sleep')
    def test_refund_payment_zero_amount(self, mock_sleep):
        """Test refund with zero amount."""
        gateway = PaymentGateway()
        success, message = gateway.refund_payment("txn_123456_001", 0)
        
        assert success is False
        assert "Invalid refund amount" in message
    
    @patch('services.payment_service.time.sleep')
    def test_refund_payment_negative_amount(self, mock_sleep):
        """Test refund with negative amount."""
        gateway = PaymentGateway()
        success, message = gateway.refund_payment("txn_123456_001", -10.50)
        
        assert success is False
        assert "Invalid refund amount" in message
    
    @patch('services.payment_service.time.sleep')
    def test_verify_payment_status_success(self, mock_sleep):
        """Test successful payment status verification."""
        gateway = PaymentGateway()
        result = gateway.verify_payment_status("txn_123456_001")
        
        assert isinstance(result, dict)
        assert result["status"] == "completed"
        assert result["transaction_id"] == "txn_123456_001"
        assert "amount" in result
        assert "timestamp" in result
        mock_sleep.assert_called_once_with(0.3)
    
    @patch('services.payment_service.time.sleep')
    def test_verify_payment_status_invalid_transaction_id(self, mock_sleep):
        """Test payment status verification with invalid transaction ID."""
        gateway = PaymentGateway()
        result = gateway.verify_payment_status("INVALID_123")
        
        assert isinstance(result, dict)
        assert result["status"] == "not_found"
        assert "Transaction not found" in result["message"]
    
    @patch('services.payment_service.time.sleep')
    def test_verify_payment_status_empty_transaction_id(self, mock_sleep):
        """Test payment status verification with empty transaction ID."""
        gateway = PaymentGateway()
        result = gateway.verify_payment_status("")
        
        assert isinstance(result, dict)
        assert result["status"] == "not_found"
        assert "Transaction not found" in result["message"]

