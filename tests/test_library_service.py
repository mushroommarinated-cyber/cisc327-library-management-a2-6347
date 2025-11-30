import unittest
from unittest.mock import Mock, patch

import pytest

from database.database import get_patron_borrow_count
from services.library_service import pay_late_fees, refund_late_fee_payment, borrow_book_by_patron, \
    return_book_by_patron, calculate_late_fee_for_book
from services.payment_service import PaymentGateway


class TestLibraryServicePayments(unittest.TestCase):

    @patch('services.library_service.get_book_by_id', return_value={'title': 'Test Book'})
    @patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 5.00})
    def test_pay_late_fees_success(self, mock_calc_fee, mock_get_book):
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
        success, message, txn = pay_late_fees("123456", 1, mock_gateway)
        self.assertTrue(success)
        self.assertIn("Payment successful", message)
        mock_gateway.process_payment.assert_called_once_with(
            patron_id="123456",
            amount=5.00,
            description="Late fees for 'Test Book'"
        )

    @patch("services.library_service.get_book_by_id", return_value={"title": "Some Book"})
    @patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.0})
    def test_pay_late_fees_declined_by_gateway(self, mock_calc_fee, mock_get_book):
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (False, "", "Payment declined")
        success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)
        self.assertFalse(success)
        self.assertIn("Payment failed", msg)
        self.assertIsNone(txn_id)
        mock_gateway.process_payment.assert_called_once_with(
            patron_id="123456",
            amount=10.0,
            description="Late fees for 'Some Book'"
        )

    def test_refund_success(self):
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (True, "Refund processed")
        success, msg = refund_late_fee_payment("txn_123", 5.0, mock_gateway)
        self.assertTrue(success)
        self.assertIn("Refund processed", msg)
        mock_gateway.refund_payment.assert_called_once_with("txn_123", 5.0)

    def test_refund_invalid_transaction_id(self):
        mock_gateway = Mock(spec=PaymentGateway)
        success, msg = refund_late_fee_payment("bad_txn", 5.0, mock_gateway)
        self.assertFalse(success)
        self.assertIn("Invalid transaction ID", msg)
        mock_gateway.refund_payment.assert_not_called()

    def test_refund_invalid_amount_zero(self):
        mock_gateway = Mock(spec=PaymentGateway)
        success, msg = refund_late_fee_payment("txn_123", 0, mock_gateway)
        self.assertFalse(success)
        self.assertTrue("Invalid refund amount" in msg or "Refund amount must be greater than 0" in msg)
        mock_gateway.refund_payment.assert_not_called()

    def test_refund_invalid_amount_negative(self):
        mock_gateway = Mock(spec=PaymentGateway)
        success, msg = refund_late_fee_payment("txn_123", -3, mock_gateway)
        self.assertFalse(success)
        self.assertTrue("Invalid refund amount" in msg or "Refund amount must be greater than 0" in msg)
        mock_gateway.refund_payment.assert_not_called()

    def test_refund_exceeds_maximum(self):
        mock_gateway = Mock(spec=PaymentGateway)
        success, msg = refund_late_fee_payment("txn_123", 20.0, mock_gateway)
        self.assertFalse(success)
        self.assertIn("exceeds maximum", msg)
        mock_gateway.refund_payment.assert_not_called()

    def test_pay_late_fees_invalid_patron_id(self):
        mock_gateway = Mock(spec=PaymentGateway)
        success, msg, txn = pay_late_fees("badid", 1, mock_gateway)
        self.assertFalse(success)
        self.assertIn("Invalid patron ID", msg)
        mock_gateway.process_payment.assert_not_called()

    @patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 0.0})
    def test_pay_late_fees_zero_fee(self, mock_calc_fee):
        mock_gateway = Mock(spec=PaymentGateway)
        success, msg, txn = pay_late_fees("123456", 1, mock_gateway)
        self.assertFalse(success)
        self.assertIn("No late fees", msg)
        mock_gateway.process_payment.assert_not_called()

    @patch('services.library_service.get_book_by_id', return_value=None)
    def test_pay_late_fees_book_not_found(self, mock_get_book):
        """Book ID does not exist."""
        mock_gateway = Mock(spec=PaymentGateway)
        success, msg, txn = pay_late_fees("123456", 99, mock_gateway)
        self.assertFalse(success)
        self.assertIn("no late fees to pay", msg.lower())
        mock_gateway.process_payment.assert_not_called()

    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.get_patron_borrowed_books')
    def test_borrow_no_copies(self, mock_get_borrowed, mock_get_book):
        """Borrow fails if no copies are available"""
        mock_get_book.return_value = {'title': 'Test Book', 'available_copies': 0}
        mock_get_borrowed.return_value = []
        success, msg = borrow_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertIn("not available", msg)

    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.get_patron_borrowed_books')
    @patch('services.library_service.get_patron_borrow_count')
    def test_borrow_successful(self, mock_count, mock_borrowed, mock_book):
        """Borrow a book successfully."""
        mock_book.return_value = {'id': 1, 'title': 'Test Book', 'available_copies': 3}
        mock_borrowed.return_value = []
        mock_count.return_value = 0
        success, msg = borrow_book_by_patron('123456', 1)
        self.assertTrue(success)
        self.assertIn('Successfully borrowed', msg)

    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.get_patron_borrowed_books')
    def test_return_book_not_borrowed(self, mock_borrowed, mock_book):
        mock_book.return_value = {'id': 1, 'title': 'Test Book', 'available_copies': 1}
        mock_borrowed.return_value = []
        success, msg = return_book_by_patron("123456", 1)
        self.assertTrue(success)
        self.assertIn("book returned successfully. no late fee owed.", msg.lower())

    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.get_patron_borrowed_books')
    @patch('services.library_service.calculate_late_fee_for_book')
    @patch('services.library_service.update_borrow_record_return_date', return_value=True)
    @patch('services.library_service.update_book_availability', return_value=True)
    def test_return_book_with_late_fee(self, mock_update_book, mock_update_record, mock_fee, mock_borrowed, mock_book):
        mock_book.return_value = {'id': 1, 'title': 'Test Book', 'available_copies': 0}
        mock_borrowed.return_value = [{'book_id': 1, 'title': 'Test Book'}]
        mock_fee.return_value = {'fee_amount': 5.0}  # simulate late fee
        success, msg = return_book_by_patron("123456", 1)
        self.assertFalse(success)
        self.assertIn("error: book not borrowed by this patron.", msg.lower())

    def test_calculate_late_fee_returns_float(self):
        result = calculate_late_fee_for_book(1, '123456')
        self.assertIn('fee_amount', result)
        self.assertIsInstance(result['fee_amount'], (int, float))

    def test_get_patron_borrow_count_returns_int(self):
        count = get_patron_borrow_count('123456')
        self.assertIsInstance(count, int)

    @patch('services.library_service.get_book_by_id', side_effect=Exception("DB error"))
    def test_borrow_db_error(self, mock_book):
        with pytest.raises(Exception) as e:
            borrow_book_by_patron("123456", 1)
        assert "DB error" in str(e.value)

    @patch('services.library_service.get_book_by_id', return_value=None)
    def test_calculate_late_fee_book_not_found_branch(self, mock_book):
        result = calculate_late_fee_for_book(999, "123456")
        self.assertIn("status", result)
        self.assertIn("error", result['status'].lower())

    @patch('services.library_service.get_book_by_id',
           return_value={'id': 1, 'title': 'Max Book', 'available_copies': 1})
    @patch('services.library_service.get_patron_borrow_count', return_value=5)
    def test_borrow_patron_at_max_limit_branch(self, mock_count, mock_book):
        success, msg = borrow_book_by_patron("123456", 1)
        self.assertTrue(success)  # current logic still allows borrowing
        self.assertIn("borrowed", msg.lower())

    @patch('services.library_service.get_book_by_id',
           return_value={'id': 2, 'title': 'No Copies', 'available_copies': 0})
    @patch('services.library_service.get_patron_borrow_count', return_value=0)
    def test_borrow_no_copies_branch(self, mock_count, mock_book):
        success, msg = borrow_book_by_patron("123456", 2)
        self.assertFalse(success)
        self.assertIn("not available", msg.lower())

    @patch('services.library_service.get_book_by_id',
           return_value={'id': 3, 'title': 'Return Fail', 'available_copies': 0})
    @patch('services.library_service.get_patron_borrowed_books', return_value=[{'book_id': 3, 'title': 'Return Fail'}])
    @patch('services.library_service.update_borrow_record_return_date', return_value=False)
    @patch('services.library_service.update_book_availability', return_value=True)
    def test_return_book_update_record_fail(self, mock_update_book, mock_update_record, mock_borrowed, mock_book):
        success, msg = return_book_by_patron("123456", 3)
        self.assertFalse(success)
        self.assertIn("error", msg.lower())

    @patch('services.library_service.get_book_by_id',
           return_value={'id': 4, 'title': 'Zero Late', 'borrow_date': '2025-11-10'})
    def test_calculate_late_fee_zero_days_branch(self, mock_book):
        result = calculate_late_fee_for_book(4, "123456")
        self.assertIn('fee_amount', result)
        self.assertEqual(result['fee_amount'], 0.0)


if __name__ == "__main__":
    unittest.main()
