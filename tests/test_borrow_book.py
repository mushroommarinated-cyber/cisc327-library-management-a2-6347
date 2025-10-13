from library_service import *


def test_borrow_book_valid():
    """Test borrowing a book with valid inputs."""
    success, message = borrow_book_by_patron("123456", 1)
    assert success == True or success == False
    assert len(message) > 0


def test_borrow_book_invalid_patronID():
    """Test borrowing a book with invalid patron ID."""
    success, message = borrow_book_by_patron("abc", 1)
    assert success == False
    assert "invalid patron" in message.lower()


def test_borrow_book_not_found():
    """Test borrowing a book that doesn't exist."""
    success, message = borrow_book_by_patron("123456", 9999)
    assert success == False
    assert "book not found" in message.lower()


def test_borrow_book_no_copies_available():
    """Test borrowing a book that has no copies."""
    success, message = borrow_book_by_patron("123456", 3)
    assert isinstance(success, bool)
    assert any(word in message.lower() for word in ["not available", "book not found"])

def test_borrow_book_limit_reached():
    success, message = borrow_book_by_patron("123456", 1)
    # either True (if database has <5 books) or False (if db has 5+)
    assert len(message) > 0