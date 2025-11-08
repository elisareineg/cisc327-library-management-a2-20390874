# Assignment 2 - Function Implementation Report

https://github.com/elisareineg/cisc327-library-management-a2-20390874

## Implementation Changes Summary

### R1 - Add Book to Catalog

**Status**: Minor fix applied to make fully complete
**Changes**: Fixed ISBN validation to check for digits only - now properly rejects invalid ISBNs like "123456789abcd"

### R2 - Book Catalog Display

**Status**: No changes made
**Reason**: Already complete and fully functional

### R3 - Borrow Book by Patron

**Status**: Minor fix applied to make fully complete
**Changes**: Added duplicate borrowing check and fixed maximum borrowing limit validation

### R4 - Return Book by Patron

**Status**: Completely rewritten from scratch
**Changes**: Implemented complete return book functionality with validation, database updates, and late fee integration
**Additional Test Cases**: Fixed patron ID format from "P001" to "123456", book ID format from "B001" to integer IDs, updated error message assertions

### R5 - Calculate Late Fee for Book

**Status**: Implemented from scratch
**Changes**: Implemented late fee calculation with tiered pricing ($0.50/day first 7 days, $1.00/day after, $15.00 max cap)

### R6 - Search Books in Catalog

**Status**: Implemented from scratch
**Changes**: Implemented search functionality with title/author partial matching and ISBN exact matching

### R7 - Get Patron Status Report

**Status**: Implemented from scratch
**Changes**: Implemented comprehensive patron status reporting with borrowed books tracking, overdue detection, and total fines calculation

## Implementation Experience

The implementation process was successful and all functions (R1-R7) are now fully functional. The main tasks were implementing the four missing functions (R4, R5, R6, R7) from scratch, plus making minor fixes to R1 and R3 to address their partial completion issues. The most challenging aspects were ensuring proper database integration and implementing the complex late fee calculation logic with the tiered pricing structure. All functions include comprehensive input validation, error handling, and proper integration with the existing database schema. The web application runs successfully and all functionality is accessible through the user interface.

## AI-Assisted Test Generation

**AI Tool Used:** LibreChat (Queen's University AI Application)
**Access URL:** https://librechat.queensu.ca

**Prompt Used:**
"Generate comprehensive test cases for a library management system with the following functionalities:

- R1: Add book to catalog with ISBN validation (13-digit numeric only)
- R2: Display book catalog (already implemented)
- R3: Borrow book by patron with duplicate checking and 5-book limit
- R4: Return book by patron with late fee calculation
- R5: Calculate late fees with tiered pricing ($0.50/day first 7 days, $1.00/day after, $15.00 max)
- R6: Search books by title, author, or ISBN
- R7: Get patron status report with borrowed books and fines
  Generate test cases that are comprehensive but use different naming conventions and test scenarios than typical library tests."

**Follow up Prompts:**

1. "Add edge cases for boundary conditions and error handling"
2. "Include test cases for data validation and user input"
3. "Generate negative test cases for invalid inputs/error cases"

**Generated Test Cases:**

### R1 - Add Book to Catalog (AI Generated)

```python
def test_add_book_valid_isbn_thirteen_digits():
    """Test adding book with valid 13-digit ISBN."""
    result = add_book_to_catalog("Machine Learning Guide", "Dr. Sarah Johnson", "9780123456789", 5)
    assert result[0] == True
    assert "successfully added" in result[1].lower()

def test_add_book_isbn_with_letters():
    """Test adding book with ISBN containing letters."""
    result = add_book_to_catalog("Data Science", "Prof. Mike Chen", "978012345678a", 3)
    assert result[0] == False
    assert "invalid isbn" in result[1].lower()

def test_add_book_isbn_too_short():
    """Test adding book with ISBN less than 13 digits."""
    result = add_book_to_catalog("Python Basics", "Jane Smith", "123456789", 2)
    assert result[0] == False
    assert "invalid isbn" in result[1].lower()

def test_add_book_duplicate_isbn():
    """Test adding book with existing ISBN."""
    result = add_book_to_catalog("Advanced Python", "Dr. Alex Brown", "9780123456789", 4)
    assert result[0] == False
    assert "already exists" in result[1].lower()
```

### R2 - Book Catalog Display (AI Generated)

```python
def test_catalog_display_all_books():
    """Test that catalog displays all available books."""
    result = get_all_books()
    assert isinstance(result, list)
    assert len(result) > 0
    for book in result:
        assert 'title' in book
        assert 'author' in book
        assert 'isbn' in book
        assert 'total_copies' in book
        assert 'available_copies' in book

def test_catalog_display_book_format():
    """Test that each book in catalog has proper format."""
    result = get_all_books()
    for book in result:
        assert isinstance(book['title'], str)
        assert isinstance(book['author'], str)
        assert isinstance(book['isbn'], str)
        assert isinstance(book['total_copies'], int)
        assert isinstance(book['available_copies'], int)
        assert book['available_copies'] <= book['total_copies']

def test_catalog_display_availability_status():
    """Test that availability status is correctly calculated."""
    result = get_all_books()
    for book in result:
        if book['available_copies'] > 0:
            assert book['available_copies'] > 0
        else:
            assert book['available_copies'] == 0

def test_catalog_display_empty_database():
    """Test catalog display when database is empty."""
    # This would require clearing the database first
    # result = get_all_books()
    # assert isinstance(result, list)
    # assert len(result) == 0
    pass  # Skipped as it would affect other tests
```

### R3 - Borrow Book by Patron (AI Generated)

```python
def test_borrow_book_duplicate_attempt():
    """Test attempting to borrow same book twice."""
    borrow_book_by_patron("123456", 1)
    result = borrow_book_by_patron("123456", 1)
    assert result[0] == False
    assert "already borrowed" in result[1].lower()

def test_borrow_book_maximum_limit_reached():
    """Test borrowing when patron has reached 5-book limit."""
    result = borrow_book_by_patron("123456", 2)
    assert result[0] == False
    assert "maximum limit" in result[1].lower()

def test_borrow_book_unavailable_copy():
    """Test borrowing when no copies are available."""
    result = borrow_book_by_patron("123456", 3)
    assert result[0] == False
    assert "not available" in result[1].lower()
```

### R4 - Return Book by Patron (AI Generated)

```python
def test_return_book_successful_with_fee():
    """Test successful return of overdue book with late fee."""
    result = return_book_by_patron("123456", 4)
    assert result[0] == True
    assert "late fee" in result[1].lower()
    assert "returned successfully" in result[1].lower()

def test_return_book_not_borrowed_by_patron():
    """Test returning book not borrowed by the patron."""
    result = return_book_by_patron("123456", 5)
    assert result[0] == False
    assert "not borrowed" in result[1].lower()

def test_return_book_invalid_patron_format():
    """Test return with invalid patron ID format."""
    result = return_book_by_patron("ABC123", 1)
    assert result[0] == False
    assert "invalid patron id" in result[1].lower()
```

### R5 - Calculate Late Fee (AI Generated)

```python
def test_calculate_fee_exactly_seven_days():
    """Test fee calculation for exactly 7 days overdue."""
    result = calculate_late_fee_for_book("123456", 6)
    assert result['fee_amount'] == 3.50  # 7 * $0.50
    assert result['days_overdue'] == 7

def test_calculate_fee_fifteen_days_overdue():
    """Test fee calculation for 15 days overdue."""
    result = calculate_late_fee_for_book("123456", 7)
    expected_fee = (7 * 0.50) + (8 * 1.00)  # $11.50
    assert result['fee_amount'] == expected_fee
    assert result['days_overdue'] == 15

def test_calculate_fee_maximum_cap_reached():
    """Test fee calculation hitting $15.00 maximum cap."""
    result = calculate_late_fee_for_book("123456", 8)
    assert result['fee_amount'] == 15.00
    assert result['days_overdue'] >= 21
```

### R6 - Search Books (AI Generated)

```python
def test_search_by_title_case_insensitive():
    """Test search by title with mixed case."""
    result = search_books_in_catalog("GREAT GATSBY", "title")
    assert len(result) > 0
    assert any("great gatsby" in book['title'].lower() for book in result)

def test_search_by_author_partial_match():
    """Test search by partial author name."""
    result = search_books_in_catalog("Fitz", "author")
    assert len(result) > 0
    assert any("fitzgerald" in book['author'].lower() for book in result)

def test_search_by_isbn_exact_match():
    """Test search by exact ISBN match."""
    result = search_books_in_catalog("9780743273565", "isbn")
    assert len(result) == 1
    assert result[0]['isbn'] == "9780743273565"

def test_search_no_results_found():
    """Test search with no matching results."""
    result = search_books_in_catalog("NonExistentBook12345", "title")
    assert len(result) == 0
```

### R7 - Patron Status Report (AI Generated)

```python
def test_patron_status_with_multiple_books():
    """Test status report for patron with multiple borrowed books."""
    result = get_patron_status_report("123456")
    assert result['success'] == True
    assert len(result['books_borrowed']) > 1
    assert result['total_fines'] >= 0

def test_patron_status_with_overdue_books():
    """Test status report for patron with overdue books."""
    result = get_patron_status_report("123456")
    assert result['success'] == True
    if len(result['books_overdue']) > 0:
        for book in result['books_overdue']:
            assert 'days_overdue' in book
            assert book['days_overdue'] > 0

def test_patron_status_nonexistent_patron():
    """Test status report for non-existent patron."""
    result = get_patron_status_report("999999")
    assert result['success'] == False
    assert "not found" in result['message'].lower()

def test_patron_status_invalid_id_format():
    """Test status report with invalid patron ID format."""
    result = get_patron_status_report("INVALID")
    assert result['success'] == False
    assert "invalid" in result['message'].lower()
```

## Test-Case Comparison

This section compares the AI-generated test cases with my existing manually test cases to evaluate test quality, coverage, and effectiveness.

### R1 - Add Book to Catalog

**Existing Test Cases (8 tests):**

- `test_add_book_to_catalog` - Basic successful addition
- `test_add_book_invalid_title` - Empty title validation
- `test_add_book_invalid_author` - Empty author validation
- `test_add_book_invalid_isbn` - Invalid ISBN format
- `test_add_book_invalid_copies` - Invalid copy count
- `test_add_book_duplicate_isbn` - Duplicate ISBN handling
- `test_add_book_boundary_copies` - Boundary copy values (0, 1, 100)
- `test_add_book_special_characters` - Special characters in title/author

**AI-Generated Test Cases (4 tests):**

- `test_add_book_valid_isbn_thirteen_digits` - Valid 13-digit ISBN
- `test_add_book_isbn_with_letters` - ISBN with letters
- `test_add_book_isbn_too_short` - Short ISBN
- `test_add_book_duplicate_isbn` - Duplicate ISBN

**Comparison Analysis:** Existing tests provide more comprehensive coverage (8 vs 4 tests) with better edge case testing. AI tests focus on ISBN validation but miss title/author validation, copy count validation, and boundary testing. Both sets overlap in core functionality but use different naming conventions.

### R2 - Book Catalog Display

**Existing Test Cases (7 tests):**

- `test_get_all_books` - Basic functionality
- `test_get_all_books_format` - Data format validation
- `test_get_all_books_isbn_format` - ISBN format in results
- `test_get_all_books_availability` - Availability calculation
- `test_get_all_books_empty_database` - Empty database handling
- `test_get_all_books_large_dataset` - Performance with large datasets
- `test_get_all_books_consistency` - Data consistency

**AI-Generated Test Cases (4 tests):**

- `test_catalog_display_all_books` - Basic functionality
- `test_catalog_display_book_format` - Data format validation
- `test_catalog_display_availability_status` - Availability status
- `test_catalog_display_empty_database` - Empty database (commented out)

**Comparison Analysis:** Existing tests provide more comprehensive coverage (7 vs 4 tests) with more thorough functionality testing. AI tests have high overlap with existing tests but miss performance testing and data consistency validation.

### R3 - Borrow Book by Patron

**Existing Test Cases (6 tests):**

- `test_book_borrow` - Basic borrowing functionality
- `test_book_availability` - Availability checking
- `test_borrowing_record` - Database record creation
- `test_maximum_borrowing_limit` - 5-book limit enforcement
- `test_invalid_patron_id` - Invalid patron ID handling
- `test_invalid_book_id` - Invalid book ID handling

**AI-Generated Test Cases (3 tests):**

- `test_borrow_book_duplicate_attempt` - Duplicate borrowing
- `test_borrow_book_maximum_limit_reached` - Maximum limit
- `test_borrow_book_unavailable_copy` - Unavailable copies

**Comparison Analysis:** Existing tests provide more comprehensive coverage (6 vs 3 tests) with better validation testing. AI tests have moderate overlap in limit testing and availability checking but miss basic functionality testing and input validation.

### R4 - Return Book by Patron

**Existing Test Cases (7 tests):**

- `test_successful_book_return` - Basic return functionality
- `test_invalid_patron_id` - Invalid patron ID
- `test_invalid_book_id` - Invalid book ID
- `test_book_not_borrowed_by_patron` - Not borrowed by patron
- `test_empty_or_none_inputs` - Empty/None inputs
- `test_book_with_late_fee` - Late fee calculation
- `test_already_returned_book` - Already returned book

**AI-Generated Test Cases (3 tests):**

- `test_return_book_successful_with_fee` - Return with late fee
- `test_return_book_not_borrowed_by_patron` - Not borrowed by patron
- `test_return_book_invalid_patron_format` - Invalid patron format

**Comparison Analysis:** Existing tests provide more comprehensive coverage (7 vs 3 tests) with more thorough scenario testing. AI tests have high overlap in core functionality testing but miss basic return functionality and input validation.

### R5 - Calculate Late Fee

**Existing Test Cases (9 tests):**

- `test_calculate_late_fee_not_overdue` - Not overdue
- `test_calculate_late_fee_1_day_overdue` - 1 day overdue
- `test_calculate_late_fee_7_days_overdue` - 7 days overdue
- `test_calculate_late_fee_8_days_overdue` - 8 days overdue
- `test_calculate_late_fee_maximum_cap` - Maximum cap
- `test_calculate_late_fee_invalid_patron_id` - Invalid patron
- `test_calculate_late_fee_invalid_book_id` - Invalid book
- `test_calculate_late_fee_book_not_borrowed` - Not borrowed
- `test_calculate_late_fee_precision` - Precision testing

**AI-Generated Test Cases (3 tests):**

- `test_calculate_fee_exactly_seven_days` - 7 days overdue
- `test_calculate_fee_fifteen_days_overdue` - 15 days overdue
- `test_calculate_fee_maximum_cap_reached` - Maximum cap

**Comparison Analysis:** Existing tests provide significantly more comprehensive coverage (9 vs 3 tests) with better edge case testing. AI tests have moderate overlap in boundary condition testing but miss input validation, precision testing, and error handling.

### R6 - Search Books

**Existing Test Cases (7 tests):**

- `test_search_books_title_partial_match` - Title partial match
- `test_search_books_author_partial_match` - Author partial match
- `test_search_books_isbn_exact_match` - ISBN exact match
- `test_search_books_invalid_search_type` - Invalid search type
- `test_search_books_no_results` - No results
- `test_search_books_result_format` - Result format
- `test_search_books_empty_search_term` - Empty search term

**AI-Generated Test Cases (4 tests):**

- `test_search_by_title_case_insensitive` - Case-insensitive title search
- `test_search_by_author_partial_match` - Author partial match
- `test_search_by_isbn_exact_match` - ISBN exact match
- `test_search_no_results_found` - No results

**Comparison Analysis:** Existing tests provide more comprehensive coverage (7 vs 4 tests) with better validation testing. AI tests have high overlap in search functionality testing but miss search type validation and result format testing.

### R7 - Patron Status Report

**Existing Test Cases (7 tests):**

- `test_get_patron_status_report_valid` - Valid patron
- `test_get_patron_status_report_nonexistent_patron` - Non-existent patron
- `test_get_patron_status_report_empty_patron_id` - Empty patron ID
- `test_get_patron_status_report_none_patron_id` - None patron ID
- `test_get_patron_status_report_with_borrowed_books` - With borrowed books
- `test_get_patron_status_report_with_overdue_books` - With overdue books
- `test_get_patron_status_report_invalid_patron_id_format` - Invalid format

**AI-Generated Test Cases (4 tests):**

- `test_patron_status_with_multiple_books` - Multiple books
- `test_patron_status_with_overdue_books` - Overdue books
- `test_patron_status_nonexistent_patron` - Non-existent patron
- `test_patron_status_invalid_id_format` - Invalid format

**Comparison Analysis:** Existing tests provide more comprehensive coverage (7 vs 4 tests) with better input validation testing. AI tests have high overlap in core functionality testing but miss basic functionality testing and input validation.

### Overall 

Existing tests (51 cases) provide 2x better coverage than AI tests (25 cases). Existing tests excel at input validation, error handling, and edge cases, while AI tests focus on core functionality with clear naming. AI tests miss comprehensive edge case testing and error handling, but existing tests have some redundancy. AI tests are good complements but can't replace the existing comprehensive test suite. This however, is also due to me having access to all the files within the directory, while the AI doesn't have access to the all the same files-something I wanted to make a note of.
