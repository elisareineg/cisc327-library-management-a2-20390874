"""
Library Service Module - Business Logic Functions

Contains all the core business logic for the Library Management System

"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books
)
from services.payment_service import PaymentGateway


def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."


def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check if patron already borrowed this book
    borrowed_books = get_patron_borrowed_books(patron_id)
    for borrowed in borrowed_books:
        if borrowed['book_id'] == book_id:
            return False, "You have already borrowed this book."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'


def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4 as per requirements
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not isinstance(patron_id, str) or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Validate book ID
    if not isinstance(book_id, int) or book_id <= 0:
        return False, "Invalid book ID."
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    # Check if book is currently borrowed by this patron
    borrowed_books = get_patron_borrowed_books(patron_id)
    book_borrowed = None
    for borrowed in borrowed_books:
        if borrowed['book_id'] == book_id:
            book_borrowed = borrowed
            break
    
    if not book_borrowed:
        return False, "This book is not borrowed by this patron."
    
    # Calculate late fee if overdue
    return_date = datetime.now()
    due_date = book_borrowed['due_date']
    days_overdue = 0
    late_fee = 0.0
    
    if return_date > due_date:
        days_overdue = (return_date - due_date).days
        # Calculate late fee: $0.50 per day for first 7 days, $1.00 per day after
        if days_overdue <= 7:
            late_fee = days_overdue * 0.50
        else:
            late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
        # Maximum cap of $15.00
        late_fee = min(late_fee, 15.00)
    
    # Update borrow record with return date
    return_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not return_success:
        return False, "Database error occurred while processing return."
    
    # Update book availability
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    # Build success message
    if late_fee > 0:
        return True, f'Book "{book["title"]}" has been successfully returned. Late fee: ${late_fee:.2f} ({days_overdue} days overdue).'
    else:
        return True, f'Book "{book["title"]}" has been successfully returned.'


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5 as per requirements
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book
        
    Returns:
        dict: Contains 'fee_amount', 'days_overdue', and 'status'
    """
    # Validate patron ID
    if not patron_id or not isinstance(patron_id, str) or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Error: Invalid patron ID format'
        }
    
    # Validate book ID
    if not isinstance(book_id, int) or book_id <= 0:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Error: Invalid book ID'
        }
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not found'
        }
    
    # Check if book is currently borrowed by this patron
    borrowed_books = get_patron_borrowed_books(patron_id)
    book_borrowed = None
    for borrowed in borrowed_books:
        if borrowed['book_id'] == book_id:
            book_borrowed = borrowed
            break
    
    if not book_borrowed:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not found or not borrowed by this patron'
        }
    
    # Calculate days overdue
    due_date = book_borrowed['due_date']
    current_date = datetime.now()
    
    if current_date <= due_date:
        # Not overdue
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Not overdue'
        }
    
    days_overdue = (current_date - due_date).days
    
    # Calculate late fee: $0.50 per day for first 7 days, $1.00 per day after
    if days_overdue <= 7:
        fee_amount = days_overdue * 0.50
    else:
        fee_amount = (7 * 0.50) + ((days_overdue - 7) * 1.00)
    
    # Maximum cap of $15.00
    fee_amount = min(fee_amount, 15.00)
    fee_amount = round(fee_amount, 2)
    
    return {
        'fee_amount': fee_amount,
        'days_overdue': days_overdue,
        'status': 'Overdue'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6 as per requirements
    
    Args:
        search_term: The term to search for
        search_type: Type of search ('title', 'author', or 'isbn')
        
    Returns:
        list: List of book dictionaries matching the search criteria
    """
    # Validate search term
    if not search_term or not search_term.strip():
        return []
    
    # Get all books
    all_books = get_all_books()
    
    # Normalize search term
    search_term_lower = search_term.strip().lower()
    
    # Filter based on search type
    results = []
    for book in all_books:
        if search_type == 'title':
            if search_term_lower in book.get('title', '').lower():
                results.append(book)
        elif search_type == 'author':
            if search_term_lower in book.get('author', '').lower():
                results.append(book)
        elif search_type == 'isbn':
            if book.get('isbn', '') == search_term.strip():
                results.append(book)
        # Invalid search type returns empty list
    
    return results


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7 as per requirements
    
    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        dict: Status report with patron information, borrowed books, overdue books, and fines
    """
    # Validate patron ID
    if not patron_id or not isinstance(patron_id, str):
        return {
            'success': False,
            'message': 'Invalid patron ID'
        }
    
    if not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'success': False,
            'message': 'Invalid patron ID. Must be exactly 6 digits.'
        }
    
    # Get all borrowed books for this patron
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    # Separate into current and overdue
    books_borrowed = []
    books_overdue = []
    total_fines = 0.0
    current_date = datetime.now()
    
    for book in borrowed_books:
        book_info = {
            'book_id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'borrow_date': book['borrow_date'].strftime('%Y-%m-%d'),
            'due_date': book['due_date'].strftime('%Y-%m-%d')
        }
        
        if book['is_overdue']:
            days_overdue = (current_date - book['due_date']).days
            # Calculate late fee
            if days_overdue <= 7:
                late_fee = days_overdue * 0.50
            else:
                late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
            late_fee = min(late_fee, 15.00)
            late_fee = round(late_fee, 2)
            
            book_info['days_overdue'] = days_overdue
            book_info['late_fee'] = late_fee
            total_fines += late_fee
            books_overdue.append(book_info)
        else:
            books_borrowed.append(book_info)
    
    total_fines = round(total_fines, 2)
    
    return {
        'success': True,
        'patron_id': patron_id,
        'books_borrowed': books_borrowed,
        'books_overdue': books_overdue,
        'total_fines': total_fines,
        'total_books_borrowed': len(books_borrowed) + len(books_overdue),
        'total_overdue': len(books_overdue)
    }


def pay_late_fees(patron_id: str, book_id: int, payment_gateway: PaymentGateway = None) -> Tuple[bool, str, Optional[str]]:
    """
    Process payment for late fees using external payment gateway.
    
    NEW FEATURE FOR ASSIGNMENT 3: Demonstrates need for mocking/stubbing
    This function depends on an external payment service that should be mocked in tests.
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book with late fees
        payment_gateway: Payment gateway instance (injectable for testing)
        
    Returns:
        tuple: (success: bool, message: str, transaction_id: Optional[str])
        
    Example for you to mock:
        # In tests, mock the payment gateway:
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
        success, msg, txn = pay_late_fees("123456", 1, mock_gateway)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits.", None
    
    # Calculate late fee first
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    
    # Check if there's a fee to pay
    if not fee_info or 'fee_amount' not in fee_info:
        return False, "Unable to calculate late fees.", None
    
    fee_amount = fee_info.get('fee_amount', 0.0)
    
    if fee_amount <= 0:
        return False, "No late fees to pay for this book.", None
    
    # Get book details for payment description
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found.", None
    
    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()
    
    # Process payment through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN THEIR TESTS!
    try:
        success, transaction_id, message = payment_gateway.process_payment(
            patron_id=patron_id,
            amount=fee_amount,
            description=f"Late fees for '{book['title']}'"
        )
        
        if success:
            return True, f"Payment successful! {message}", transaction_id
        else:
            return False, f"Payment failed: {message}", None
            
    except Exception as e:
        # Handle payment gateway errors
        return False, f"Payment processing error: {str(e)}", None


def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway: PaymentGateway = None) -> Tuple[bool, str]:
    """
    Refund a late fee payment (e.g., if book was returned on time but fees were charged in error).
    
    NEW FEATURE FOR ASSIGNMENT 3: Another function requiring mocking
    
    Args:
        transaction_id: Original transaction ID to refund
        amount: Amount to refund
        payment_gateway: Payment gateway instance (injectable for testing)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate inputs
    if not transaction_id or not transaction_id.startswith("txn_"):
        return False, "Invalid transaction ID."
    
    if amount <= 0:
        return False, "Refund amount must be greater than 0."
    
    if amount > 15.00:  # Maximum late fee per book
        return False, "Refund amount exceeds maximum late fee."
    
    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()
    
    # Process refund through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN YOUR TESTS!
    try:
        success, message = payment_gateway.refund_payment(transaction_id, amount)
        
        if success:
            return True, message
        else:
            return False, f"Refund failed: {message}"
            
    except Exception as e:
        return False, f"Refund processing error: {str(e)}"
