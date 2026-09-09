"""
MooveGate - Official Moove Agentic Payments Client
Handles payment link creation, verification, and polite settlement polling.
"""

import os
import time
import logging
import uuid
from typing import Optional, Dict, Any, List
import urllib.request
import urllib.error
import json

from .schemas import PaymentLink, PaymentLinkCreate, PaymentStatus

logger = logging.getLogger("moovegate.client")


class MooveAPIError(Exception):
    """Custom exception raised for Moove API errors."""
    def __init__(self, message: str, code: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class MooveClient:
    """
    Client for Moove Agentic Payments (Receive Agent).
    Never moves funds or touches private keys. Strictly requests payments and checks settlement.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        sandbox: bool = False,
    ):
        self.api_key = api_key or os.environ.get("MOOVE_API_KEY")
        self.base_url = (base_url or os.environ.get("MOOVE_API_BASE_URL", "https://api.moove.xyz")).rstrip("/")
        
        # Enable sandbox if explicitly requested or if no key is provided in development
        self.sandbox = sandbox or (self.api_key is None or self.api_key in ("sandbox", "mock", "test"))
        
        if self.sandbox:
            logger.info("MooveClient initialized in SANDBOX / SIMULATION mode.")
            self._mock_db: Dict[str, Dict[str, Any]] = {}
        else:
            logger.info(f"MooveClient initialized in LIVE mode against base URL: {self.base_url}")

    def _headers(self) -> Dict[str, str]:
        if not self.api_key and not self.sandbox:
            raise MooveAPIError("MOOVE_API_KEY environment variable is not set.", code="MISSING_API_KEY")
        return {
            "X-API-Key": self.api_key or "mk_sandbox_dummy",
            "Content-Type": "application/json",
            "User-Agent": "MooveGate-AgenticGateway/1.0.0",
        }

    def create_payment_link(
        self,
        amount: str,
        description: Optional[str] = None,
        max_usage: int = 1,
        expiration_date: Optional[str] = None,
    ) -> PaymentLink:
        """
        Creates a hosted payment link using Moove Receive Agent.
        
        Args:
            amount: Decimal string (e.g. '19.99', never floating point).
            description: Identifier/order reference for dashboard reconciliation.
            max_usage: Usage limit (default 1 for one-off).
            expiration_date: Optional ISO-8601 UTC timestamp.
        """
        req_model = PaymentLinkCreate(
            toAmount=str(amount),
            description=description,
            maxUsage=max_usage,
            expirationDate=expiration_date,
        )

        if self.sandbox:
            link_id = f"pl_mock_{uuid.uuid4().hex[:12]}"
            mock_data = {
                "id": link_id,
                "url": f"https://pay.moove.xyz/link/{link_id}",
                "status": PaymentStatus.ACTIVE.value,
                "toAmount": req_model.toAmount,
                "receivedAmount": None,
                "description": req_model.description,
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "metadata": {"sandbox": True},
            }
            self._mock_db[link_id] = mock_data
            logger.info(f"[SANDBOX] Created payment link {link_id} for {req_model.toAmount} USDC")
            return PaymentLink(**mock_data)

        url = f"{self.base_url}/v1/payment-link"
        payload = json.dumps(req_model.dict(exclude_none=True)).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=self._headers(), method="POST")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return PaymentLink(**data)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                code = err_json.get("code", "UNKNOWN_ERROR")
                msg = err_json.get("message", err_body)
            except Exception:
                code = "HTTP_ERROR"
                msg = err_body
            raise MooveAPIError(f"Failed to create Moove payment link: {msg}", code=code, status_code=e.code)
        except Exception as e:
            raise MooveAPIError(f"Network error connecting to Moove API: {str(e)}")

    def get_payment_link(self, link_id: str) -> PaymentLink:
        """
        Retrieves current status of a payment link.
        """
        if self.sandbox:
            if link_id not in self._mock_db:
                raise MooveAPIError(f"Payment link {link_id} not found in sandbox DB.", status_code=404)
            return PaymentLink(**self._mock_db[link_id])

        url = f"{self.base_url}/v1/payment-link/{link_id}"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return PaymentLink(**data)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise MooveAPIError(f"Error fetching payment link {link_id}: {err_body}", status_code=e.code)
        except Exception as e:
            raise MooveAPIError(f"Network error fetching payment link: {str(e)}")

    def simulate_sandbox_payment(self, link_id: str) -> PaymentLink:
        """
        Helper for testing: Simulates a customer or counterparty agent settling on-chain.
        """
        if not self.sandbox:
            raise MooveAPIError("Simulate payment is only available in sandbox mode.")
        if link_id not in self._mock_db:
            raise MooveAPIError(f"Payment link {link_id} not found.")
        
        record = self._mock_db[link_id]
        record["status"] = PaymentStatus.COMPLETED.value
        record["receivedAmount"] = record["toAmount"]
        return PaymentLink(**record)

    def poll_settlement(
        self,
        link_id: str,
        timeout_seconds: int = 120,
        initial_interval: float = 3.0,
        max_interval: float = 10.0,
    ) -> PaymentLink:
        """
        Politely polls until the link reaches 'completed' or timeout is reached.
        Uses exponential backoff to respect Moove rate limits.
        """
        start_time = time.time()
        interval = initial_interval

        while time.time() - start_time < timeout_seconds:
            link = self.get_payment_link(link_id)
            if link.status == PaymentStatus.COMPLETED:
                logger.info(f"Payment link {link_id} settled successfully!")
                return link
            elif link.status == PaymentStatus.INACTIVE:
                raise MooveAPIError(f"Payment link {link_id} became inactive/expired before settlement.")

            time.sleep(interval)
            interval = min(interval * 1.25, max_interval)

        raise TimeoutError(f"Settlement polling timed out after {timeout_seconds}s for link {link_id}")

    def list_completed_links(self, offset: int = 0) -> List[PaymentLink]:
        """
        Lists settled payment links for reconciliation.
        """
        if self.sandbox:
            completed = [PaymentLink(**item) for item in self._mock_db.values() if item["status"] == PaymentStatus.COMPLETED.value]
            return completed

        url = f"{self.base_url}/v1/payment-link?status=completed&offset={offset}"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", data) if isinstance(data, dict) else data
                return [PaymentLink(**item) for item in items]
        except Exception as e:
            raise MooveAPIError(f"Error listing completed links: {str(e)}")
