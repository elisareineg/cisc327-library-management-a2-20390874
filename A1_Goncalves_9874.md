| Function Name | Implementation Status |                                                                                   Missing |
| :------------ | :-------------------: | ----------------------------------------------------------------------------------------: |
| R1            |  Partially Complete   | ISBN digit validation only checks length but not if it's solely numeric (accepts letters) |
| R2            |       Complete        |                                                                                      None |
| R3            |       Complete        |                                                                                      None |
| R4            |    Not Implemented    |                             Return book functionality, validation logic, database updates |
| R5            |    Not Implemented    |                                  Late fee calculation logic, date handling, fee structure |
| R6            |    Not Implemented    |                                 Search functionality, catalog querying, result formatting |
| R7            |    Not Implemented    |                              Patron status reporting, data aggregation, report generation |

# Summary of Test Cases

## R1

- **Valid Book Addition**: Tests successful addition of a book with valid title, author, ISBN, and copies
- **Title Length Validation**: Tests that titles exceeding 200 characters are rejected with "Title too long" error
- **Author Length Validation**: Tests that author names exceeding 100 characters are rejected with "Author name too long" error
- **ISBN Length Validation**: Tests that ISBNs not exactly 13 digits are rejected with "not 13 digits" error
- **ISBN Format Validation**: Tests that ISBNs containing non-numeric characters are rejected with "isbn must be a 13-digit number" error
- **Copies Validation**: Tests that negative copies, zero copies, and non-integer copies are rejected with appropriate error messages

\_Note: R1 is partially complete. The core functionality works, but there are minor issues: ISBN validation only checks length (13 characters) but doesn't validate that all characters are digits - it would accept invalid ISBNs like "123456789abcd" or "123456789-123".

## R2

### Test Cases for Book Catalog Display Function

- **Returns Book List**: Tests that get_all_books returns a list of books from the database
- **Required Fields Present**: Tests that each book contains all required fields (ID, title, author, ISBN, total_copies, available_copies)
- **Field Data Types**: Tests that book fields have correct data types (ID as int, title/author/ISBN as strings, copies as integers)
- **Availability Logic**: Tests that available_copies never exceeds total_copies and is never negative
- **ISBN Format Validation**: Tests that ISBNs are in correct 13-digit numeric format
- **Empty Catalog Handling**: Tests graceful handling when catalog is empty
- **Display Format Validation**: Tests that books are formatted correctly for catalog display
- **Borrow Button Logic**: Tests the logic for when borrow button should be available (available_copies > 0)
- **Sample Data Validation**: Tests that sample data is correctly loaded with expected book information

## R3

- **Valid Book Borrowing**: Tests successful borrowing of a book with valid patron ID and book ID
- **Patron ID Length Validation**: Tests that patron IDs not exactly 6 digits are rejected with "exactly 6 digits" error
- **Patron ID Format Validation**: Tests that patron IDs containing non-numeric characters are rejected with "exactly 6 digits" error
- **Book Availability Check**: Tests that borrowing unavailable books is rejected with "not available" error
- **Duplicate Borrowing Prevention**: Tests that patrons cannot borrow the same book twice, showing "already borrowed" error

## R4

_Note: The return book functionality has not been implemented, but comprehensive test cases have been created to define expected behavior when the function is developed._

- **Successful Book Return**: Tests successful return of a book with valid patron ID and book ID, expecting "successfully returned" message
- **Invalid Patron ID**: Tests return with invalid patron ID, expecting "invalid patron id" error
- **Invalid Book ID**: Tests return with invalid book ID, expecting "invalid book id" error
- **Book Not Borrowed by Patron**: Tests returning a book that wasn't borrowed by the patron, expecting "book was not borrowed by this patron" error
- **Empty or None Inputs**: Tests return with empty or None patron ID inputs, expecting appropriate error messages
- **Book with Late Fee**: Tests returning an overdue book that incurs late fees, verifying late fee information is included
- **Already Returned Book**: Tests returning a book that has already been returned, expecting "book has already been returned" error

## R5

_Note: The late fee calculation functionality has not been implemented, but comprehensive test cases have been created to define expected behavior when the function is developed._

- **Not Overdue**: Tests late fee calculation for books within 14-day borrowing period (fee = $0.00)
- **1 Day Overdue**: Tests late fee calculation for 1 day overdue (fee = $0.50)
- **7 Days Overdue**: Tests late fee calculation for 7 days overdue (fee = $3.50)
- **8 Days Overdue**: Tests late fee calculation for 8 days overdue (fee = $4.50, using tiered pricing)
- **Maximum Cap**: Tests that late fees are capped at $15.00 maximum
- **Invalid Patron ID**: Tests late fee calculation with invalid patron ID, expecting error status
- **Invalid Book ID**: Tests late fee calculation with invalid book ID, expecting error status
- **Book Not Borrowed**: Tests late fee calculation for books not borrowed by the patron
- **Fee Precision**: Tests that fee amounts are calculated with proper precision (2 decimal places)

## R6

_Note: The search books functionality has not been implemented, but comprehensive test cases have been created to define expected behavior when the function is developed._

- **Title Partial Match**: Tests searching for books by partial title match (case-insensitive)
- **Author Partial Match**: Tests searching for books by partial author match (case-insensitive)
- **ISBN Exact Match**: Tests searching for books by exact ISBN match
- **Invalid Search Type**: Tests searching with invalid search type, expecting empty results
- **No Results**: Tests searching for non-existent books, expecting empty results
- **Result Format**: Tests that search results follow proper catalog display format with required fields
- **Empty Search Term**: Tests searching with empty search term, expecting empty results

## R7

_Note: The patron status report functionality has not been implemented, but comprehensive test cases have been created to define expected behavior when the function is developed._

- **Valid Patron Report**: Tests getting status report with valid patron ID, verifying all required fields
- **Non-existent Patron**: Tests getting status report for non-existent patron, expecting "patron not found" error
- **Empty Patron ID**: Tests getting status report with empty patron ID, expecting "patron id cannot be empty" error
- **None Patron ID**: Tests getting status report with None patron ID, expecting "invalid patron id" error
- **Patron with Borrowed Books**: Tests status report for patron with borrowed books, verifying book details structure
- **Patron with Overdue Books**: Tests status report for patron with overdue books, verifying overdue book details
- **Invalid Patron ID Format**: Tests getting status report with invalid patron ID format, expecting format error
