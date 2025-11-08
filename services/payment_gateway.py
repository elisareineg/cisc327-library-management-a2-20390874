"""
Payment Gateway Interface
This module defines the PaymentGateway class that serves as an interface
for external payment processing services.
"""

from typing import Tuple
from abc import ABC, abstractmethod


class PaymentGateway(ABC):
    """
    Abstract base class for payment gateway implementations.
    This interface defines the contract for payment processing services.
    """
    
    @abstractmethod
    def process_payment(self, patron_id: str, amount: float, description: str) -> Tuple[bool, str, str]:
        """
        Process a payment through the payment gateway.
        
        Args:
            patron_id: The patron's library card ID
            amount: The amount to charge (must be positive)
            description: Description of the payment
            
        Returns:
            tuple: (success: bool, transaction_id: str, message: str)
        """
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: float) -> Tuple[bool, str]:
        """
        Process a refund through the payment gateway.
        
        Args:
            transaction_id: The original transaction ID to refund
            amount: The amount to refund (must be positive)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        pass


class PaymentServiceGateway(PaymentGateway):
    """
    Concrete implementation of PaymentGateway using the payment_service module.
    This wraps the PaymentGateway class from payment_service.
    """
    
    def __init__(self, api_key: str = "test_key_12345"):
        """Initialize with the PaymentGateway from payment_service."""
        from .payment_service import PaymentGateway as ServicePaymentGateway
        self._gateway = ServicePaymentGateway(api_key)
    
    def process_payment(self, patron_id: str, amount: float, description: str) -> Tuple[bool, str, str]:
        """Process payment using the payment_service PaymentGateway."""
        return self._gateway.process_payment(patron_id, amount, description)
    
    def refund_payment(self, transaction_id: str, amount: float) -> Tuple[bool, str]:
        """Process refund using the payment_service PaymentGateway."""
        return self._gateway.refund_payment(transaction_id, amount)

