from library_service import *

def test_borrow_book_valid():
    """Borrow a book that is available."""
    success, message = borrow_book_by_patron("123456", 1)
    assert success is True
    assert "success" in message.lower() or "borrowed" in message.lower()

def test_borrow_book_invalid_patron():
    """Borrowing a book with invalid patron ID."""
    success, message = borrow_book_by_patron("abc", 1)
    assert success is False
    assert "invalid patron" in message.lower()

def test_borrow_book_not_found():
    """Borrowing a book that doesn't exist."""
    success, message = borrow_book_by_patron("123456", 9999)
    assert success is False
    assert "book not found" in message.lower()

def test_borrow_book_no_copies_available():
    """Borrowing a book with 0 available copies."""
    success, message = borrow_book_by_patron("123456", 3)  # Book 3 must have 0 available copies
    assert success is False
    assert "not available" in message.lower()

def test_borrow_book_limit_reached():
    """Borrowing when patron has reached the borrow limit (5 books)."""
    # Ensure patron has exactly 5 books already borrowed in test DB
    success, message = borrow_book_by_patron("123456", 2)
    assert success is False
    assert "limit" in message.lower()
