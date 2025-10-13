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
    
    if len(isbn) != 13:
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
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
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
    
    TODO: Implement R4 as per requirements
    """
    return False, "Book return functionality is not yet implemented."

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    Args:
        patron_id: The patron's ID
        book_id: The book's ID
        
    Returns:
        Dict with fee_amount, days_overdue, and status
    """
    try:
        # Validate inputs
        if not patron_id or not isinstance(patron_id, str):
            return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid patron ID'}
        
        if not isinstance(book_id, int) or book_id <= 0:
            return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid book ID'}
        
        # Check if book was borrowed by this patron
        borrowed_books = get_patron_borrowed_books(patron_id)
        book_borrowed = None
        
        for borrowed_book in borrowed_books:
            if borrowed_book['book_id'] == book_id:
                book_borrowed = borrowed_book
                break
        
        if not book_borrowed:
            return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Book not borrowed by this patron'}
        
        # Calculate days overdue
        due_date = datetime.strptime(book_borrowed['due_date'], '%Y-%m-%d').date()
        today = datetime.now().date()
        days_overdue = max(0, (today - due_date).days)
        
        # Calculate late fee
        if days_overdue == 0:
            fee_amount = 0.00
        elif days_overdue <= 7:
            fee_amount = days_overdue * 0.50
        else:
            fee_amount = (7 * 0.50) + ((days_overdue - 7) * 1.00)
        
        # Cap at $15.00
        fee_amount = min(fee_amount, 15.00)
        
        return {
            'fee_amount': round(fee_amount, 2),
            'days_overdue': days_overdue,
            'status': 'success'
        }
        
    except Exception as e:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': f'Error: {str(e)}'}

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    
    return []

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    Args:
        patron_id: The patron's ID
        
    Returns:
        Dict with patron information, borrowed books, and overdue status
    """
    try:
        # Validate input
        if not patron_id or not isinstance(patron_id, str):
            return {'success': False, 'error': 'Invalid patron ID'}
        
        # Get patron's borrowed books
        borrowed_books = get_patron_borrowed_books(patron_id)
        
        # Calculate overdue books and total fines
        overdue_books = []
        total_fines = 0.00
        
        for book in borrowed_books:
            due_date = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            days_overdue = max(0, (today - due_date).days)
            
            if days_overdue > 0:
                # Calculate late fee for this book
                if days_overdue <= 7:
                    late_fee = days_overdue * 0.50
                else:
                    late_fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)
                
                late_fee = min(late_fee, 15.00)  # Cap at $15.00
                total_fines += late_fee
                
                overdue_books.append({
                    'book_id': book['book_id'],
                    'title': book.get('title', 'Unknown'),
                    'due_date': book['due_date'],
                    'days_overdue': days_overdue,
                    'late_fee': round(late_fee, 2)
                })
        
        return {
            'success': True,
            'patron_id': patron_id,
            'name': f'Patron {patron_id}',  # Placeholder name
            'books_borrowed': len(borrowed_books),
            'books_overdue': len(overdue_books),
            'total_fines': round(total_fines, 2),
            'overdue_books': overdue_books,
            'borrowed_books': borrowed_books
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Error generating report: {str(e)}'}
