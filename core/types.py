"""
MooveGate - Core Data Models & Schemas
Conforms strictly to Moove Agentic Payments OpenAPI specification.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class PaymentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    INACTIVE = "inactive"


class PaymentLinkCreate(BaseModel):
    toAmount: str = Field(
        ...,
        description="Decimal string representation of payment amount (e.g. '10.00'). Never floating point.",
    )
    description: Optional[str] = Field(
        None,
        description="Unique reference identifier (order ID, job ID, invoice number).",
    )
    maxUsage: Optional[int] = Field(
        1,
        description="Maximum number of times the link can be paid. Defaults to 1 for one-off payments.",
    )
    expirationDate: Optional[str] = Field(
        None,
        description="ISO-8601 UTC timestamp for link expiry. Null/None means never expires.",
    )

    @validator("toAmount")
    def validate_amount_string(cls, v: str) -> str:
        try:
            val = float(v)
            if val <= 0:
                raise ValueError("Amount must be greater than 0")
        except ValueError:
            raise ValueError(f"toAmount must be a valid positive decimal string, got: {v}")
        return v


class PaymentLink(BaseModel):
    id: str
    url: str
    status: PaymentStatus
    toAmount: str
    receivedAmount: Optional[str] = None
    description: Optional[str] = None
    createdAt: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaywallChallenge(BaseModel):
    status_code: int = 402
    error: str = "Payment Required"
    message: str = "This service requires settlement via Moove Agentic Payments."
    payment_link_id: str
    payment_url: str
    amount_usdc: str
    reference_id: str
    instructions: str = (
        "Complete payment using the Moove hosted payment link. "
        "Upon cross-chain settlement, re-query this endpoint with header 'X-Moove-Link-Id: <id>'."
    )
