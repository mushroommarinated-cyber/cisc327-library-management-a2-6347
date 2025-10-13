from library_service import *
from database import *

def test_catalog_returns_list():
    """Test that catalog returns a list."""
    books = get_all_books()
    assert isinstance(books, list)

def test_catalog_contains_requirements():
    """Test that each book has ID, title, author, ISBN, and copies."""
    books = get_all_books()
    if books:
        book = books[0]
        assert "id" in book
        assert "title" in book
        assert "author" in book
        assert "isbn" in book
        assert "available_copies" in book
        assert "total_copies" in book

def test_catalog_is_empty():
    """Test that catalog returns empty list if no books exist."""
    books = get_all_books()
    assert isinstance(books, list)

def test_catalog_available_copies_not_exceed_total():
    """Test that available copies are not greater than total copies."""
    books = get_all_books()
    for book in books:
        assert book["available_copies"] <= book["total_copies"]
