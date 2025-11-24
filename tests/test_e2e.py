from playwright.sync_api import Page, expect


def test_add_book_to_catalog_and_verify(page: Page, flask_app_server):
    """
    E2E Test: Add a new book to the catalog and verify it appears.
    """
    # Navigate to catalog page
    page.goto("http://localhost:5000/catalog")
    
    # Verify we're on the catalog page
    expect(page.locator("h2")).to_have_text("📖 Book Catalog")
    
    # Click "Add New Book" button
    page.click("text=➕ Add New Book")
    
    # Verify we're on the add book page
    expect(page.locator("h2")).to_have_text("➕ Add New Book")
    
    # Fill in the form
    test_title = "The Great Gatsby"
    test_author = "F. Scott Fitzgerald"
    test_isbn = "9780743273565"
    test_copies = "3"
    
    page.fill('input[name="title"]', test_title)
    page.fill('input[name="author"]', test_author)
    page.fill('input[name="isbn"]', test_isbn)
    page.fill('input[name="total_copies"]', test_copies)
    
    # Submit the form
    page.click('button:has-text("Add Book to Catalog")')
    
    # Wait for redirect to catalog page
    page.wait_for_url("**/catalog")
    
    # Verify success message appears
    success_message = page.locator(".flash-success")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("successfully added")
    
    # Verify the book appears in the catalog table
    expect(page.locator("table")).to_be_visible()
    
    # Check that the book title appears in the table
    book_row = page.locator(f"table tbody tr:has-text('{test_title}')")
    expect(book_row).to_be_visible()
    
    # Verify book details in the table
    expect(book_row.locator("td").nth(1)).to_have_text(test_title)  # Title column
    expect(book_row.locator("td").nth(2)).to_have_text(test_author)  # Author column
    expect(book_row.locator("td").nth(3)).to_have_text(test_isbn)  # ISBN column


def test_borrow_book_from_catalog(page: Page, flask_app_server):
    """
    E2E Test: Borrow a book from the catalog using a patron ID.
    """
    # Navigate to catalog page
    page.goto("http://localhost:5000/catalog")
    
    # Verify we're on the catalog page
    expect(page.locator("h2")).to_have_text("📖 Book Catalog")
    
    # Wait for the table to load
    expect(page.locator("table")).to_be_visible()
    
    # Find the first available book row (one with a borrow form)
    first_borrow_form = page.locator('form[action*="borrow"]').first
    expect(first_borrow_form).to_be_visible()
    
    # Get the book row (parent tr of the form)
    book_row = first_borrow_form.locator("xpath=ancestor::tr")
    
    # Get the book title for verification
    book_title = book_row.locator("td").nth(1).inner_text()
    
    # Get initial availability
    availability_before = book_row.locator("td").nth(4).inner_text()
    
    # Enter patron ID (6 digits)
    patron_id = "123456"
    first_borrow_form.locator('input[name="patron_id"]').fill(patron_id)
    
    # Click the Borrow button
    first_borrow_form.locator('button:has-text("Borrow")').click()
    
    # Wait for redirect back to catalog
    page.wait_for_url("**/catalog")
    
    # Verify success message appears
    success_message = page.locator(".flash-success")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Successfully borrowed")
    expect(success_message).to_contain_text(book_title)
    
    # Verify the book's availability has decreased
    book_row_after = page.locator(f"table tbody tr:has-text('{book_title}')")
    availability_after = book_row_after.locator("td").nth(4).inner_text()
    
    # The availability should have decreased by 1
    # Format is "X/Y Available" where X is available_copies
    available_before = int(availability_before.split("/")[0])
    available_after = int(availability_after.split("/")[0])
    
    assert available_after == available_before - 1, \
        f"Availability should decrease from {available_before} to {available_before - 1}, but got {available_after}"


def test_complete_add_and_borrow(page: Page, flask_app_server):
    """
    E2E Test: Complete user flow - Add a book, then borrow it.
    """
    # Step 1: Navigate to catalog
    page.goto("http://localhost:5000/catalog")
    expect(page.locator("h2")).to_have_text("📖 Book Catalog")
    
    # Step 2: Add a new book
    page.click("text=➕ Add New Book")
    expect(page.locator("h2")).to_have_text("➕ Add New Book")
    
    # Fill form with unique ISBN to avoid conflicts
    import time
    unique_isbn = f"978{int(time.time()) % 10000000000:010d}"
    
    page.fill('input[name="title"]', "E2E Test Book")
    page.fill('input[name="author"]', "Test Author")
    page.fill('input[name="isbn"]', unique_isbn)
    page.fill('input[name="total_copies"]', "5")
    
    page.click('button:has-text("Add Book to Catalog")')
    page.wait_for_url("**/catalog")
    
    # Step 3: Verify book appears
    expect(page.locator(".flash-success")).to_be_visible()
    book_row = page.locator("table tbody tr:has-text('E2E Test Book')")
    expect(book_row).to_be_visible()
    expect(book_row.locator("td").nth(1)).to_have_text("E2E Test Book")
    
    # Step 4: Borrow the book
    borrow_form = book_row.locator('form[action*="borrow"]')
    expect(borrow_form).to_be_visible()
    
    borrow_form.locator('input[name="patron_id"]').fill("999999")
    borrow_form.locator('button:has-text("Borrow")').click()
    
    # Step 5: Verify borrow confirmation
    page.wait_for_url("**/catalog")
    expect(page.locator(".flash-success")).to_be_visible()
    expect(page.locator(".flash-success")).to_contain_text("Successfully borrowed")
    expect(page.locator(".flash-success")).to_contain_text("E2E Test Book")


def test_homepage_loads(page: Page, flask_app_server):
    """
    E2E Test: Verify homepage loads and redirects correctly.
    """
    # Navigate to homepage
    page.goto("http://localhost:5000/")
    
    # Homepage should redirect to catalog
    page.wait_for_url("**/catalog")
    
    # Verify catalog page elements
    expect(page.locator("h2")).to_have_text("📖 Book Catalog")
    expect(page.locator("table, .content")).to_be_visible()  # Either table or empty state
