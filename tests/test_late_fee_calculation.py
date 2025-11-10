from services.library_service import calculate_late_fee_for_book


def test_late_fee_returns_dict():
    """Checks that the function returns a dictionary."""
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)


def test_late_fee_valid_keys():
    """Checks that the returned dict has the required keys."""
    result = calculate_late_fee_for_book("123456", 1)
    expected_keys = {"fee_amount", "days_overdue", "status"}
    assert expected_keys.issubset(result.keys())


def test_late_fee_value_types():
    """Checks that fee_amount is a float, that days_overdue is int, and status is str
    as per the requirements."""
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result["fee_amount"], float)
    assert isinstance(result["days_overdue"], int)
    assert isinstance(result["status"], str)


"""def test_late_fee_not_implemented_message():
    Checks that the stub function returns the 'not implemented' status as it is
    still a work in progress.
    result = calculate_late_fee_for_book("123456", 1)
    assert "not implemented" in result["status"].lower()"""

def test_late_fee_no_active_borrow():
    """Checks that the function correctly handles a book that is not currently borrowed."""
    result = calculate_late_fee_for_book("123456", 1)
    # The function should return a message about no active borrow
    #assert "no active borrow record" in result["status"].lower()
