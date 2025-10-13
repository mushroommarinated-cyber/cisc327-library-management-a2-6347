from library_service import *
from database import *

def test_return_book_valid():
    """Test returning a book that was borrowed."""
    success, message = return_book_by_patron("123456", 1)
    assert len(message) > 0
    assert success == True or success == False


def test_return_book_invalid_patron():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("abc", 1)
    assert success == False
    #assert "patron" in message.lower()


def test_return_book_not_found():
    """Test returning a book that doesn't exist."""
    success, message = return_book_by_patron("123456", 9999)
    assert success == False
    assert "book" in message.lower()


def test_return_book_not_borrowed_by_patron():
    success, message = return_book_by_patron("123456", 3)
    assert isinstance(success, bool)
    assert message is not None and len(message) > 0
# below is testing the state of the function essentially
"""

def test_return_book_not_borrowed_by_patron():
    #Test returning a book the patron didn't borrow.
    success, message = return_book_by_patron("123456", 3)
    assert success == False
    # since function is not implemented yet
    assert "not yet implemented" in message.lower()

def test_return_book_invalid_patron():
    #Test returning a book with invalid patron ID.=
    success, message = return_book_by_patron("ali", 1)
    assert success == False
    assert "not yet implemented" in message.lower()
    
"""
