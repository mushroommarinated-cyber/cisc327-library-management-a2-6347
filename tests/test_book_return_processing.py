from library_service import *
from database import *

def test_return_book_valid():
    """Test returning a book that was borrowed."""
    success, message = return_book_by_patron("123456", 1)
    assert success is True
    assert "success" in message.lower()

def test_return_book_invalid_patron():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("abc", 1)
    assert success is False
    assert "patron" in message.lower()

def test_return_book_not_found():
    """Test returning a book that doesn't exist."""
    success, message = return_book_by_patron("123456", 9999)
    assert success is False
    assert "book" in message.lower()

def test_return_book_not_borrowed_by_patron():
    """Test returning a book the patron didn't borrow."""
    success, message = return_book_by_patron("123456", 3)  # book 3 is returned
    assert success is False
    assert "borrowed" in message.lower()
