Elisa Goncalves
20390874
Nov 24, 2025
https://github.com/elisareineg/cisc327-library-management-a2-20390874

### Part 1:

#### E2E Testing Approach (tool used, tested features, assertions)

For end-to-end testing, I used **Playwright (Python)** with the `pytest-playwright` plugin to automate browser-based testing of the Flask application. The E2E tests cover user flows including: (1) adding a new book to the catalog with form validation and verification that the book appears in the catalog table, (2) borrowing a book from the catalog using a patron ID and verifying flash messages and availability updates, (3) a complete end-to-end flow that adds a book and then borrows it, and (4) homepage navigation and redirect functionality. Assertions are performed using Playwright's web-first assertion API (`expect()`) which automatically retries until conditions are met. The tests verify UI elements such as page headings, form submissions, flash success/error messages with proper CSS class selectors (`.flash-success`, `.flash-error`), table content including book details (title, author, ISBN), and availability changes after borrowing operations. Each test uses a `flask_app_server` fixture that automatically starts a Flask server on a dynamically assigned port in a separate thread, ensuring test isolation with fresh database instances. The tests can run in both headless mode (default, faster for CI/CD) and headed mode (`--headed` flag, for debugging).
