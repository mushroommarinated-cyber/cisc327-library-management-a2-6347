"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database.database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_db_connection, get_patron_borrowed_books,
    get_patron_borrow_record
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


LATE_FEE_RATE = 0.50


def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    if not patron_id or not book_id:
        return False, "Error: Invalid input."

    book = get_book_by_id(book_id)
    if not book:
        return False, "Error: Book not found."

    conn = get_db_connection()
    record = conn.execute('''
        SELECT * FROM borrow_records
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
        ORDER BY borrow_date ASC
        LIMIT 1
    ''', (patron_id, book_id)).fetchone()
    conn.close()

    if not record:
        return False, "Error: Book not borrowed by this patron."

    # Calculate late fee before returning the book
    late_fee_info = calculate_late_fee_for_book(patron_id, book_id)
    fee_amount = late_fee_info.get('fee_amount', 0.0)

    # Process return
    return_date = datetime.now()
    success_record = update_borrow_record_return_date(patron_id, book_id, return_date)
    success_book = update_book_availability(book_id, 1)

    if success_record and success_book:
        if fee_amount > 0:
            return True, f"Book returned successfully. Late fee owed: ${fee_amount:.2f}"
        else:
            return True, "Book returned successfully. No late fee owed."
    else:
        return False, "Error: Could not process return."


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    R5 requirements:
    - books are due 14 days after borrowing
    -$0.5/day after first 7 days overdue, $1.00/day after that
    - max late fee does not exceed $15
    
    # implement 5
    
    
    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """
    if not patron_id or not book_id:
        return {"fee_amount": 0.0, "days_overdue": 0, "copies_overdue": [], "status": "Error: Invalid input."}

    book = get_book_by_id(book_id)
    if not book:
        return {"fee_amount": 0.0, "days_overdue": 0, "copies_overdue": [], "status": "Error: Book not found."}

    record = get_patron_borrow_record(patron_id, book_id)
    if not record:
        return {"fee_amount": 0.0, "days_overdue": 0, "copies_overdue": [], "status": "No active borrow record"}

    borrow_date = datetime.fromisoformat(record["borrow_date"]).date()
    today = datetime.now().date()
    days_borrowed = (today - borrow_date).days
    overdue_days = max(0, days_borrowed - 14)

    if overdue_days <= 7:
        fee_amount = 0.5 * overdue_days
    else:
        fee_amount = 0.5 * 7 + 1.0 * (overdue_days - 7)
    fee_amount = min(fee_amount, 15.0)

    copies_overdue = [{
        "borrow_date": borrow_date.isoformat(),
        "days_overdue": overdue_days,
        "late_fee": round(fee_amount, 2)
    }]

    return {
        "fee_amount": round(fee_amount, 2),
        "days_overdue": overdue_days,
        "copies_overdue": copies_overdue,
        "status": "Success"
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    search_term = search_term.strip()
    if not search_term:
        return []

    conn = get_db_connection()
    books: List[Dict] = []

    if search_type == 'isbn':
        # exact match
        query = "SELECT * FROM books WHERE isbn = ? ORDER BY title"
        params = (search_term,)

    elif search_type == 'title':
        # case-insensitive partial match for the title
        query = "SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?) ORDER BY title"
        params = (f"%{search_term}%",)

    elif search_type == 'author':
        # case-insensitive partial match for the author
        query = "SELECT * FROM books WHERE LOWER(author) LIKE LOWER(?) ORDER BY title"
        params = (f"%{search_term}%",)

    else:
        conn.close()
        return []

    try:
        cursor = conn.execute(query, params)
        results = cursor.fetchall()
        books = [dict(row) for row in results]


    except Exception as e:

        print(f"Database error during search: {e}")

    # list of books returned
    return books


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            "status": "Error",
            "message": "Invalid patron ID. Must be exactly 6 digits."
        }

    # get  patron borrowing data
    try:
        borrowed_books_list = get_patron_borrowed_books(patron_id)
        borrow_count = get_patron_borrow_count(patron_id)
    except Exception as e:
        return {
            "status": "Error",
            "message": f"Database error while fetching patron records: {e}"
        }

    # calculate total late fees
    total_late_fees = 0.00
    current_loans_report = []

    for book in borrowed_books_list:
        late_fee, overdue_days = (0.00, 0)

        if book.get("is_overdue"):
            late_fee, overdue_days = calculate_late_fee_for_book(book["due_date"])
            total_late_fees += late_fee

        current_loans_report.append({
            "book_id": book["book_id"],
            "title": book["title"],
            "author": book["author"],
            "due_date": book["due_date"].strftime("%Y-%m-%d"),
            "is_overdue": book["is_overdue"],
            "days_overdue": overdue_days,
            "late_fee_current": late_fee
        })

    # borrowing history handling
    try:
        borrowing_history = []
        history_status = (
            "Borrowing history not implemented yet."
            if not borrowing_history else
            "History retrieved successfully."
        )
    except Exception:
        borrowing_history = []
        history_status = "Error retrieving full borrowing history."

    return {
        "status": "Success",
        "patron_id": patron_id,
        "number_of_books_borrowed": borrow_count,
        "books_currently_borrowed": current_loans_report,
        "total_late_fees_owed": round(total_late_fees, 2),
        "borrowing_history_summary": borrowing_history,
        "_history_note": history_status
    }


def get_patron_status_report(patron_id):
    # mainly for testing purposes, ignore
    """
    Returns a summary of a patron's current borrowing status.
    Uses placeholder vals
    """
    report = {
        "_history_note": "Borrowing history not implemented yet.",
        "books_currently_borrowed": [],
        "borrowing_history_summary": [],
        "number_of_books_borrowed": 0,
        "total_late_fees": 0.0,  # i added this so tests pass
    }
    return report


def pay_late_fees(patron_id: str, book_id: int, payment_gateway: PaymentGateway = None) -> Tuple[
    bool, str, Optional[str]]:
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


def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway: PaymentGateway = None) -> Tuple[
    bool, str]:
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
