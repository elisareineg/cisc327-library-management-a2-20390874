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
    
    # Check if patron has already borrowed this book
    borrowed_books = get_patron_borrowed_books(patron_id)
    for borrowed_book in borrowed_books:
        if borrowed_book['book_id'] == book_id:
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
    Implements R4: Book Return Functionality
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    # Check if patron has borrowed this book
    borrowed_books = get_patron_borrowed_books(patron_id)
    book_borrowed = False
    for borrowed_book in borrowed_books:
        if borrowed_book['book_id'] == book_id:
            book_borrowed = True
            break
    
    if not book_borrowed:
        return False, "You have not borrowed this book."
    
    # Update return date
    return_date = datetime.now()
    success_update_return = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not success_update_return:
        return False, "Database error occurred while updating return date."
    
    # Update book availability
    success_update_availability = update_book_availability(book_id, 1)
    if not success_update_availability:
        return False, "Database error occurred while updating book availability."
    
    # Calculate late fees
    late_fee_info = calculate_late_fee_for_book(patron_id, book_id)
    
    if late_fee_info['fee_amount'] > 0:
        return True, f'Book "{book["title"]}" has been successfully returned. Late fee: ${late_fee_info["fee_amount"]:.2f} for {late_fee_info["days_overdue"]} days overdue.'
    else:
        return True, f'Book "{book["title"]}" has been successfully returned. No late fees.'


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5: Late Fee Calculation
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book
        
    Returns:
        dict: {'fee_amount': float, 'days_overdue': int, 'status': str}
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Invalid patron ID'
        }
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not found'
        }
    
    # Get patron's borrowed books to find the specific book
    borrowed_books = get_patron_borrowed_books(patron_id)
    target_book = None
    for borrowed_book in borrowed_books:
        if borrowed_book['book_id'] == book_id:
            target_book = borrowed_book
            break
    
    if not target_book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not borrowed by this patron'
        }
    
    # Calculate days overdue
    due_date = target_book['due_date']
    current_date = datetime.now()
    days_overdue = (current_date - due_date).days
    
    if days_overdue <= 0:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Not overdue'
        }
    
    # Calculate late fee based on the fee structure
    # First 7 days: $0.50 per day
    # After 7 days: $1.00 per day
    # Maximum cap: $15.00
    
    if days_overdue <= 7:
        fee_amount = days_overdue * 0.50
    else:
        # First 7 days at $0.50, remaining days at $1.00
        fee_amount = (7 * 0.50) + ((days_overdue - 7) * 1.00)
    
    # Apply maximum cap
    fee_amount = min(fee_amount, 15.00)
    
    return {
        'fee_amount': round(fee_amount, 2),
        'days_overdue': days_overdue,
        'status': 'Overdue'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6: Book Search Functionality
    
    Args:
        search_term: The term to search for
        search_type: Type of search ('title', 'author', 'isbn')
        
    Returns:
        list: List of matching books
    """
    if not search_term or not search_term.strip():
        return []
    
    # Get all books from the catalog
    all_books = get_all_books()
    search_term_lower = search_term.strip().lower()
    matching_books = []
    
    for book in all_books:
        if search_type == 'title':
            if search_term_lower in book['title'].lower():
                matching_books.append(book)
        elif search_type == 'author':
            if search_term_lower in book['author'].lower():
                matching_books.append(book)
        elif search_type == 'isbn':
            if search_term.strip() == book['isbn']:
                matching_books.append(book)
        else:
            # Invalid search type, return empty list
            return []
    
    return matching_books

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7: Patron Status Report
    
    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        dict: Patron status information
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'success': False,
            'message': 'Invalid patron ID. Must be exactly 6 digits.'
        }
    
    # Get patron's borrowed books
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    # Separate current and overdue books
    current_books = []
    overdue_books = []
    total_fines = 0.0
    
    for book in borrowed_books:
        book_info = {
            'book_id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'borrow_date': book['borrow_date'].strftime('%Y-%m-%d'),
            'due_date': book['due_date'].strftime('%Y-%m-%d')
        }
        
        if book['is_overdue']:
            # Calculate late fee for this book
            late_fee_info = calculate_late_fee_for_book(patron_id, book['book_id'])
            book_info['days_overdue'] = late_fee_info['days_overdue']
            book_info['late_fee'] = late_fee_info['fee_amount']
            total_fines += late_fee_info['fee_amount']
            overdue_books.append(book_info)
        else:
            current_books.append(book_info)
    
    return {
        'success': True,
        'patron_id': patron_id,
        'books_borrowed': current_books,
        'books_overdue': overdue_books,
        'total_fines': round(total_fines, 2),
        'total_books_borrowed': len(borrowed_books),
        'total_overdue': len(overdue_books)
    }
