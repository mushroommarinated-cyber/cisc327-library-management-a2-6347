import pytest
import sqlite3
import os
from library_service import *

@pytest.fixture(autouse=True)
def reset_test_db():
    db_path = os.environ.get("DATABASE", "library_test.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE isbn = '2235567890223'")
    conn.commit()
    conn.close()

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Harry Plotter", "LOL Rowling", "2235567890223", 5)

    #assert success == True
    assert "successfully added" in message.lower()

"""def test_add_book_valid_input():
    #Test adding a book with valid input
    success, message = add_book_to_catalog("Harry Potter", "JK Rowling", "1234567890123", 5)
    assert success == False
    assert "book" in message.lower() or "not yet" in message.lower()"""

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Harry Potter", "JK Rowling", "123456789", 5)

    assert success == False
    assert "13 digits" in message.lower()


# for me to remember:
# make test cases where there are negative copies, empty title, long author name
def test_add_book_negative_copies():
    """Test adding a book with negative copies."""
    success, message = add_book_to_catalog("Harry Potter", "JK Rowling", "1234567890123", -5)

    assert success == False
    assert "positive integer" in message.lower()


def test_add_book_empty_title():
    """Test adding a book with an empty title."""
    success, message = add_book_to_catalog("", "JK Rowling", "1234567890123", 4)

    assert success == False
    assert "title is required" in message.lower()


def test_add_book_long_author_name():
    """Test adding a book with a long author name."""
    success, message = add_book_to_catalog("Harry Potter",
                                           "Pneumonoultramicroscopicsilicovolcanoconiosisantidisestablishmentarianismhippopotomonstrosesquippedaliophobia",
                                           "1234567890123", 4)

    assert success == False
    assert "100 characters" in message.lower()
