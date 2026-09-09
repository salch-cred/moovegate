"""
MooveSynapse - Formal Fair-Exchange State Machine
Governs deterministic transition of bilateral agent micro-contracts settled via Moove Agentic Payments.
"""

import time
import uuid
import logging
from enum import Enum
from typing import Dict, Any, Optional

from .cryptography import seal_deliverable, open_deliverable
from .moove_client import MooveClient, MooveAPIError
from .schemas import PaymentStatus

logger = logging.getLogger("moovegate.fair_exchange")


class ExchangeState(str, Enum):
    INITIALIZED = "INITIALIZED"
    COMMITTED = "COMMITTED"
    INVOICED = "INVOICED"
    SETTLED = "SETTLED"
    DELIVERED = "DELIVERED"
    EXPIRED = "EXPIRED"


class FairExchangeContract:
    """
    State machine for a single bilateral agent fair-exchange contract.
    Solves the Fair Exchange Problem without custodial smart contract overhead
    by tying deliverable hash commitments to Moove's cross-chain settlement verification.
    """

    def __init__(
        self,
        task_id: str,
        client_agent_id: str,
        provider_agent_id: str,
        task_specification: str,
        price_usdc: str,
        moove_client: MooveClient,
        timeout_seconds: int = 300,
    ):
        self.task_id = task_id
        self.client_agent_id = client_agent_id
        self.provider_agent_id = provider_agent_id
        self.task_specification = task_specification
        self.price_usdc = price_usdc
        self.moove_client = moove_client
        self.timeout_seconds = timeout_seconds
        
        self.created_at = time.time()
        self.state = ExchangeState.INITIALIZED
        
        # Cryptographic fields
        self.commitment_hash: Optional[str] = None
        self.sealed_ciphertext: Optional[str] = None
        self._escrow_key: Optional[str] = None
        
        # Moove settlement fields
        self.payment_link_id: Optional[str] = None
        self.payment_link_url: Optional[str] = None
        self.settlement_timestamp: Optional[float] = None
        self.unlocked_deliverable: Optional[Dict[str, Any]] = None

    def commit_deliverable(self, deliverable_payload: Dict[str, Any]) -> str:
        """
        Step 1 (Provider): Seals deliverable into cryptographic envelope and binds commitment.
        """
        if self.state != ExchangeState.INITIALIZED:
            raise ValueError(f"Cannot commit deliverable in state {self.state}")

        h, c, k = seal_deliverable(deliverable_payload)
        self.commitment_hash = h
        self.sealed_ciphertext = c
        self._escrow_key = k
        self.state = ExchangeState.COMMITTED
        
        logger.info(f"Contract [{self.task_id}] COMMITTED. SHA-256: {h[:16]}...")
        return h

    def generate_moove_invoice(self) -> str:
        """
        Step 2 (Provider/Gateway): Issues official Moove Receive Agent payment link.
        Description strictly embeds contract reference and cryptographic commitment.
        """
        if self.state != ExchangeState.COMMITTED:
            raise ValueError(f"Cannot invoice contract in state {self.state}")

        # Unique reference embedding task and cryptographic commitment prefix
        ref_description = f"AFX_{self.task_id[:8]}_{self.commitment_hash[:12]}"
        
        link = self.moove_client.create_payment_link(
            amount=self.price_usdc,
            description=ref_description,
            max_usage=1,
        )
        self.payment_link_id = link.id
        self.payment_link_url = link.url
        self.state = ExchangeState.INVOICED
        
        logger.info(f"Contract [{self.task_id}] INVOICED on Moove: {link.url} (Ref: {ref_description})")
        return link.url

    def verify_and_settle(self) -> bool:
        """
        Step 3 (Observer/Client): Polls Moove Receive Agent to verify on-chain finality.
        """
        if self.state != ExchangeState.INVOICED:
            raise ValueError(f"Cannot verify settlement in state {self.state}")

        if time.time() - self.created_at > self.timeout_seconds:
            self.state = ExchangeState.EXPIRED
            logger.warning(f"Contract [{self.task_id}] EXPIRED waiting for payment.")
            return False

        link = self.moove_client.get_payment_link(self.payment_link_id)
        if link.status == PaymentStatus.COMPLETED:
            self.settlement_timestamp = time.time()
            self.state = ExchangeState.SETTLED
            logger.info(f"Contract [{self.task_id}] SETTLED via Moove! Status: {link.status}")
            return True

        return False

    def release_key_and_decrypt(self) -> Dict[str, Any]:
        """
        Step 4 (Client): Once settlement is verified, releases the symmetric key
        and decrypts the deliverable with mathematical verification of pre-image commitment.
        """
        if self.state != ExchangeState.SETTLED:
            raise ValueError(f"Cannot release deliverable in state {self.state}. Settlement required.")

        # In a decentralized or dual-agent setting, the escrow key is transmitted upon settlement verification
        payload = open_deliverable(
            ciphertext_b64=self.sealed_ciphertext,
            key_hex=self._escrow_key,
            expected_commitment=self.commitment_hash,
        )
        self.unlocked_deliverable = payload
        self.state = ExchangeState.DELIVERED
        logger.info(f"Contract [{self.task_id}] DELIVERED and cryptographically verified.")
        return payload

    def export_summary(self) -> Dict[str, Any]:
        """Exports public audit summary of the fair-exchange transaction."""
        return {
            "task_id": self.task_id,
            "state": self.state.value,
            "client_agent_id": self.client_agent_id,
            "provider_agent_id": self.provider_agent_id,
            "specification": self.task_specification,
            "price_usdc": self.price_usdc,
            "commitment_sha256": self.commitment_hash,
            "moove_link_id": self.payment_link_id,
            "moove_link_url": self.payment_link_url,
            "settled": self.state in (ExchangeState.SETTLED, ExchangeState.DELIVERED),
            "settlement_timestamp": self.settlement_timestamp,
        }
