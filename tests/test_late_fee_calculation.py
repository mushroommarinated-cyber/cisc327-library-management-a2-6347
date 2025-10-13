import pytest
from library_service import *

def test_late_fee_returns_dict():
    """Function returns a dictionary."""
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)

def test_late_fee_valid_keys():
    """Returned dict contains required keys."""
    result = calculate_late_fee_for_book("123456", 1)
    expected_keys = {"fee_amount", "days_overdue", "status"}
    assert expected_keys.issubset(result.keys())

def test_late_fee_value_types():
    """Returned values have correct types."""
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result["fee_amount"], float)
    assert isinstance(result["days_overdue"], int)
    assert isinstance(result["status"], str)

def test_late_fee_no_active_borrow():
    """Correctly handles a book that is not currently borrowed."""
    # Use a book/patron combination guaranteed to have no active borrow
    result = calculate_late_fee_for_book("123456", 9999)
    assert "no active borrow record" in result["status"].lower()
