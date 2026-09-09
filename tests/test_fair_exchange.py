"""
MooveGate & MooveSynapse Test Suite
Validates cryptographic commitments, Moove Receive client, and state machine integrity.
"""

import unittest
import json
import time

from core.cryptography import seal_deliverable, open_deliverable, compute_sha256
from core.moove_client import MooveClient, MooveAPIError
from core.types import PaymentStatus, PaymentLinkCreate
from core.fair_exchange_state_machine import FairExchangeContract, ExchangeState


class TestMooveGateCore(unittest.TestCase):

    def setUp(self):
        self.client = MooveClient(sandbox=True)

    def test_decimal_string_validation(self):
        """Rule: toAmount must strictly be a decimal string, never float."""
        req = PaymentLinkCreate(toAmount="29.95", description="REF-100")
        self.assertEqual(req.toAmount, "29.95")
        self.assertIsInstance(req.toAmount, str)

        with self.assertRaises(ValueError):
            PaymentLinkCreate(toAmount="-5.00")

    def test_moove_receive_agent_link_creation(self):
        """Verifies Moove Receive Agent link creation."""
        link = self.client.create_payment_link(amount="10.50", description="ORDER_8819", max_usage=1)
        self.assertTrue(link.id.startswith("pl_mock_"))
        self.assertTrue(link.url.startswith("https://pay.moove.xyz/link/"))
        self.assertEqual(link.status, PaymentStatus.ACTIVE)
        self.assertEqual(link.toAmount, "10.50")
        self.assertEqual(link.description, "ORDER_8819")

    def test_settlement_and_polling(self):
        """Verifies state transition from active to completed upon settlement."""
        link = self.client.create_payment_link(amount="100.00", description="INVOICE_99")
        self.assertEqual(link.status, PaymentStatus.ACTIVE)

        # Simulate settlement
        settled_link = self.client.simulate_sandbox_payment(link.id)
        self.assertEqual(settled_link.status, PaymentStatus.COMPLETED)
        self.assertEqual(settled_link.receivedAmount, "100.00")

        # Polling verification
        polled = self.client.poll_settlement(link.id, timeout_seconds=5)
        self.assertEqual(polled.status, PaymentStatus.COMPLETED)

    def test_cryptographic_seal_and_open(self):
        """Verifies deliverable encryption and SHA-256 pre-image commitment verification."""
        payload = {"secret_alpha": "Arbitrage opportunity on Base: USDC/WETH", "confidence": 0.98}
        commitment_hash, ciphertext_b64, key = seal_deliverable(payload)

        # Valid open
        recovered = open_deliverable(ciphertext_b64, key, commitment_hash)
        self.assertEqual(recovered["secret_alpha"], payload["secret_alpha"])
        self.assertEqual(recovered["confidence"], payload["confidence"])

        # Tampered commitment should raise ValueError
        tampered_hash = "0" * 64
        with self.assertRaises(ValueError):
            open_deliverable(ciphertext_b64, key, tampered_hash)

        # Wrong key should fail verification
        wrong_key = "1" * 64
        with self.assertRaises(Exception):
            open_deliverable(ciphertext_b64, wrong_key, commitment_hash)

    def test_full_fair_exchange_lifecycle(self):
        """Verifies complete state machine transitions."""
        contract = FairExchangeContract(
            task_id="TASK_EVAL_01",
            client_agent_id="buyer_01",
            provider_agent_id="seller_01",
            task_specification="Compute gradient descent step",
            price_usdc="15.00",
            moove_client=self.client,
        )
        self.assertEqual(contract.state, ExchangeState.INITIALIZED)

        # 1. Commit
        payload = {"weights": [0.12, 0.45, 0.99]}
        h = contract.commit_deliverable(payload)
        self.assertEqual(contract.state, ExchangeState.COMMITTED)

        # 2. Invoice on Moove
        url = contract.generate_moove_invoice()
        self.assertEqual(contract.state, ExchangeState.INVOICED)
        self.assertIn("pl_mock_", url)

        # 3. Simulate and verify settlement
        self.client.simulate_sandbox_payment(contract.payment_link_id)
        is_settled = contract.verify_and_settle()
        self.assertTrue(is_settled)
        self.assertEqual(contract.state, ExchangeState.SETTLED)

        # 4. Release deliverable
        unlocked = contract.release_key_and_decrypt()
        self.assertEqual(contract.state, ExchangeState.DELIVERED)
        self.assertEqual(unlocked["weights"], [0.12, 0.45, 0.99])


if __name__ == "__main__":
    unittest.main()
