"""
MooveGate - Autonomous Agent-to-Agent Commerce & Dynamic Paywall SDK
Built on Moove Agentic Payments infrastructure.
"""

from core.moove_client import MooveClient, MooveAPIError
from core.types import PaymentLink, PaymentLinkCreate, PaymentStatus, PaywallChallenge
from core.paywall_middleware import moove_paywall, MoovePaymentRequired, FastAPIMooveMiddleware
from core.fair_exchange_state_machine import FairExchangeContract, ExchangeState
from core.cryptography import seal_deliverable, open_deliverable, compute_sha256

__version__ = "1.0.0"
__all__ = [
    "MooveClient",
    "MooveAPIError",
    "PaymentLink",
    "PaymentLinkCreate",
    "PaymentStatus",
    "PaywallChallenge",
    "moove_paywall",
    "MoovePaymentRequired",
    "FastAPIMooveMiddleware",
    "FairExchangeContract",
    "ExchangeState",
    "seal_deliverable",
    "open_deliverable",
    "compute_sha256",
]
