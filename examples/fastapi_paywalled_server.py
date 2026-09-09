"""
MooveGate - FastAPI Monetized Service Example
Demonstrates how to monetize an AI inference / data endpoint with HTTP 402 challenge.
"""

import sys
import os
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.moove_client import MooveClient
from core.schemas import PaymentStatus

app = FastAPI(
    title="MooveGate Monetized AI Inference API",
    description="Example API protected by Moove Agentic Payments. Returns HTTP 402 if unpaid.",
    version="1.0.0",
)

client = MooveClient(sandbox=True)


class AuditRequest(BaseModel):
    contract_address: str
    deep_scan: bool = True


@app.post("/api/v1/smart-contract-audit")
async def audit_endpoint(
    req: AuditRequest,
    x_moove_link_id: str = Header(None, description="The Moove payment link ID that settled this invoice"),
):
    """
    Protected AI Security Scan: Costs 25.00 USDC.
    If unpaid, raises HTTP 402 with Moove hosted payment link.
    """
    required_price = "25.00"

    # If caller provided link ID, verify settlement on Moove rails
    if x_moove_link_id:
        link = client.get_payment_link(x_moove_link_id)
        if link.status == PaymentStatus.COMPLETED:
            return {
                "success": True,
                "status": "COMPLETED",
                "contract": req.contract_address,
                "vulnerabilities_found": 0,
                "reentrancy_safe": True,
                "paid_amount_usdc": link.receivedAmount,
                "auditor": "@sentinel_auditor",
            }
        else:
            raise HTTPException(status_code=402, detail=f"Payment link {x_moove_link_id} status is '{link.status.value}'. Payment not settled.")

    # No link provided or unpaid: Mint fresh Moove payment link
    new_link = client.create_payment_link(
        amount=required_price,
        description=f"AUDIT_{req.contract_address[:8]}",
        max_usage=1,
    )

    raise HTTPException(
        status_code=402,
        detail={
            "error": "Payment Required",
            "message": "This AI audit requires settlement via Moove Agentic Payments.",
            "payment_url": new_link.url,
            "payment_link_id": new_link.id,
            "amount_usdc": required_price,
            "instructions": "Pay via Moove checkout URL, then re-send request with 'X-Moove-Link-Id' header.",
        },
    )


if __name__ == "__main__":
    print("[*] Starting MooveGate Monetized FastAPI server on http://127.0.0.1:8000")
    print("[*] Documentation available at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
