Elisa Goncalves
20390874
Nov 24, 2025
https://github.com/elisareineg/cisc327-library-management-a2-20390874

#### Part 1:

### Installation Instructions

## Step 1: Prerequisites

- Have Python 3.9 or higher
- pip (Python package manager)


### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers (required for E2E tests)
python -m playwright install chromium
``
```
### Running Tests


```bash
# Run all E2E tests (headless mode)
pytest tests/test_e2e.py or pytest tests/test_e2e.py -v

# Run E2E tests with visible browser window (headed mode)
pytest tests/test_e2e.py -v --headed

# Run specific E2E test (example)
pytest tests/test_e2e.py::test_add_book_to_catalog_and_verify -v

# Run E2E tests with visible browser (headed)
pytest tests/test_e2e.py -v --headed
```

### Expected Test Results

- `test_add_book_to_catalog_and_verify` - Tests adding a book and verifying it appears
- `test_borrow_book_from_catalog` - Tests borrowing a book from catalog
- `test_complete_add_and_borrow` - Tests complete user flow (add + borrow)
- `test_homepage_loads` - Tests homepage navigation

**Expected Output:**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.2, pytest-7.4.4, pluggy-1.0.0
collecting ... collected 4 items

tests/test_e2e.py::test_add_book_to_catalog_and_verify[chromium] PASSED
tests/test_e2e.py::test_borrow_book_from_catalog[chromium] PASSED
tests/test_e2e.py::test_complete_add_and_borrow[chromium] PASSED
tests/test_e2e.py::test_homepage_loads[chromium] PASSED

============================== 4 passed in ~8s ===============================
```

---

#### E2E Testing Approach (tool used, tested features, assertions)

For end-to-end testing, I used **Playwright (Python)** with the `pytest-playwright` plugin to automate browser-based testing of the Flask application. The E2E tests cover user flows including: (1) adding a new book to the catalog with form validation and verification that the book appears in the catalog table, (2) borrowing a book from the catalog using a patron ID and verifying flash messages and availability updates, (3) a complete end-to-end flow that adds a book and then borrows it, and (4) homepage navigation and redirect functionality. Assertions are performed using Playwright's web-first assertion API (`expect()`) which automatically retries until conditions are met. The tests verify UI elements such as page headings, form submissions, flash success/error messages with proper CSS class selectors (`.flash-success`, `.flash-error`), table content including book details (title, author, ISBN), and availability changes after borrowing operations. Each test uses a `flask_app_server` fixture that automatically starts a Flask server on a dynamically assigned port in a separate thread, ensuring test isolation with fresh database instances. The tests can run in both headless mode (default, faster for CI/CD) and headed mode (`--headed` flag, for debugging).


#### Part 2:

