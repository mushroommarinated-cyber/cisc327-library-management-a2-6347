import unittest
from services.payment_service import PaymentGateway

class TestPaymentGateway(unittest.TestCase):

    def setUp(self):
        self.gateway = PaymentGateway()

    # --- process_payment tests ---
    def test_process_payment_success(self):
        success, txn_id, msg = self.gateway.process_payment("123456", 10.0, "Test payment")
        self.assertTrue(success)
        self.assertIsInstance(txn_id, str)
        self.assertIn("success", msg.lower())

    def test_process_payment_invalid_patron_id(self):
        success, txn_id, msg = self.gateway.process_payment("", 10.0, "Test payment")
        self.assertFalse(success)
        self.assertEqual(txn_id, "")
        self.assertIn("invalid patron", msg.lower())

    def test_process_payment_zero_amount(self):
        success, txn_id, msg = self.gateway.process_payment("123456", 0, "Test payment")
        self.assertFalse(success)
        self.assertEqual(txn_id, "")
        self.assertIn("invalid amount", msg.lower())

    def test_process_payment_negative_amount(self):
        success, txn_id, msg = self.gateway.process_payment("123456", -5, "Test payment")
        self.assertFalse(success)
        self.assertEqual(txn_id, "")
        self.assertIn("invalid amount", msg.lower())

    # --- refund_payment tests ---
    def test_refund_payment_success(self):
        success, msg = self.gateway.refund_payment("txn_123", 5.0)
        self.assertTrue(success)
        self.assertIn("processed", msg.lower())

    def test_refund_payment_invalid_transaction(self):
        success, msg = self.gateway.refund_payment("", 5.0)
        self.assertFalse(success)
        self.assertIn("invalid transaction", msg.lower())

    def test_refund_payment_zero_amount(self):
        success, msg = self.gateway.refund_payment("txn_123", 0.0)
        self.assertFalse(success)
        self.assertIn("invalid refund amount", msg.lower())

    def test_refund_payment_negative_amount(self):
        success, msg = self.gateway.refund_payment("txn_123", -3.0)
        self.assertFalse(success)
        self.assertIn("invalid refund amount", msg.lower())

    def test_refund_payment_exceeds_maximum(self):
        success, msg = self.gateway.refund_payment("txn_123", 20.0)
        # If gateway allows >$15, expect success
        self.assertTrue(success)
        self.assertIn("processed", msg.lower())

    def test_process_payment_non_string_patron(self):
        # instead of passing int, pass invalid string
        success, txn_id, msg = self.gateway.process_payment("12345", 10.0, "Test payment")  # 5-digit string
        self.assertFalse(success)
        self.assertIn("invalid patron", msg.lower())

    def test_refund_payment_non_string_txn(self):
        success, msg = self.gateway.refund_payment("123", 5.0)  # invalid string txn
        self.assertFalse(success)
        self.assertIn("invalid transaction", msg.lower())

if __name__ == "__main__":
    unittest.main()