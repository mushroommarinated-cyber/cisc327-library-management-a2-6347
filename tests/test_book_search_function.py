import pytest
from library_service import *

def test_search_books_returns_list():
    """Function should return a list."""
    results = search_books_in_catalog("Harry Potter", "title")
    assert isinstance(results, list)

def test_search_books_invalid_type_returns_empty():
    """Invalid search type should return empty list."""
    results = search_books_in_catalog("Harry Potter", "invalid_type")
    assert results == []

def test_search_partial_author_match():
    """Partial author match (case-insensitive) returns results with 'author' keys."""
    results = search_books_in_catalog("Rowling", "author")
    assert isinstance(results, list)
    for book in results:
        assert "author" in book
        assert "rowling" in book["author"].lower()

def test_search_isbn_exact_match():
    """Exact ISBN match returns correct book."""
    results = search_books_in_catalog("1234567890123", "isbn")
    assert isinstance(results, list)
    for book in results:
        assert "isbn" in book
        assert book["isbn"] == "1234567890123"

def test_search_partial_title_match():
    """Partial title match (case-insensitive) returns results with 'title' keys."""
    results = search_books_in_catalog("harry", "title")
    assert isinstance(results, list)
    for book in results:
        assert "title" in book
        assert "harry" in book["title"].lower()
