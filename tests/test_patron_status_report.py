import pytest
from library_service import *
import os
import sqlite3
import pytest
from database import DATABASE


def test_patron_status_report_example_data_structure():
    """check for borrowed books data structure."""
    report = get_patron_status_report("123456")
    books = report.get("currently_borrowed_books", [])
    for book in books:
        assert "title" in book
        assert "due_date" in book

"""
def test_patron_status_report_empty_for_new_patron():
    check for empty lists and zero fees/count for new patron.
    report = get_patron_status_report("999999")  # assuming this patron has no activity
    assert report.get("currently_borrowed_books") == []
    assert report.get("borrowing_history") == []
    assert report.get("total_late_fees") == 0.0
    assert report.get("borrowed_count") == 0


def test_patron_status_report_contains_keys():
    Report dictionary should contain all required keys.
    report = get_patron_status_report("123456")
    expected_keys = ["currently_borrowed_books", "total_late_fees", "borrowed_count", "borrowing_history"]
    for key in expected_keys:
        assert key in report
"""

def test_patron_status_report_returns_dict():
    """Function should return a dictionary."""
    report = get_patron_status_report("123456")
    assert isinstance(report, dict)

def test_patron_status_report_empty_for_new_patron():
    """Check for empty lists and zero fees/count for new patron."""
    report = get_patron_status_report("999999")  # assuming this patron has no activity
    assert report.get("books_currently_borrowed") == []
    assert report.get("borrowing_history_summary") == []
    assert report.get("total_late_fees") == 0.0
    assert report.get("number_of_books_borrowed") == 0

def test_patron_status_report_contains_keys():
    """Report dictionary should contain all required keys."""
    report = get_patron_status_report("123456")
    expected_keys = ["books_currently_borrowed", "total_late_fees", "number_of_books_borrowed", "borrowing_history_summary"]
    for key in expected_keys:
        assert key in report