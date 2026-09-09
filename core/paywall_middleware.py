"""
MooveGate - Autonomous Paywall Middleware
Provides HTTP 402 Payment Required challenges and automatic on-chain settlement release.
"""

import functools
import logging
import uuid
from typing import Callable, Optional, Dict, Any

from .moove_client import MooveClient, MooveAPIError
from .schemas import PaymentStatus, PaywallChallenge

logger = logging.getLogger("moovegate.paywall")


class MoovePaymentRequired(Exception):
    """Exception raised when an endpoint requires Moove settlement."""
    def __init__(self, challenge: PaywallChallenge):
        super().__init__(challenge.message)
        self.challenge = challenge


def moove_paywall(
    price: str,
    memo: Optional[str] = None,
    client: Optional[MooveClient] = None,
):
    """
    Decorator for Python functions / API routes that require Moove Agentic Payments settlement.
    
    Usage:
        @moove_paywall(price="2.50", memo="DeepResearch-Report")
        def generate_report(topic: str, moove_link_id: Optional[str] = None):
            return {"report": f"Confidential analysis on {topic}"}
    """
    _client = client or MooveClient()

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check for link id in kwargs or custom header parameter
            link_id = kwargs.get("moove_link_id") or kwargs.get("x_moove_link_id")

            if link_id:
                try:
                    link = _client.get_payment_link(link_id)
                    if link.status == PaymentStatus.COMPLETED:
                        logger.info(f"Payment verified for link {link_id}. Unlocking resource.")
                        return func(*args, **kwargs)
                    else:
                        logger.warning(f"Link {link_id} provided but status is {link.status}")
                except Exception as e:
                    logger.error(f"Error validating payment link {link_id}: {e}")

            # If not paid or no valid link, issue a fresh payment link
            ref_id = f"{memo or func.__name__}_{uuid.uuid4().hex[:8]}"
            new_link = _client.create_payment_link(
                amount=str(price),
                description=ref_id,
                max_usage=1,
            )

            challenge = PaywallChallenge(
                payment_link_id=new_link.id,
                payment_url=new_link.url,
                amount_usdc=str(price),
                reference_id=ref_id,
            )
            logger.info(f"Issuing HTTP 402 Paywall Challenge: Link {new_link.id} for {price} USDC")
            raise MoovePaymentRequired(challenge)

        return wrapper
    return decorator


class FastAPIMooveMiddleware:
    """
    FastAPI / Starlette Middleware for autonomous HTTP 402 Paywall handling.
    """
    def __init__(self, app, routes_pricing: Dict[str, str], client: Optional[MooveClient] = None):
        self.app = app
        self.routes_pricing = routes_pricing  # e.g. {"/api/generate": "5.00"}
        self.client = client or MooveClient()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in self.routes_pricing:
            price = self.routes_pricing[path]
            headers = dict(scope.get("headers", []))
            link_id = headers.get(b"x-moove-link-id", b"").decode("utf-8")

            if link_id:
                try:
                    link = self.client.get_payment_link(link_id)
                    if link.status == PaymentStatus.COMPLETED:
                        # Payment verified, allow request to proceed
                        await self.app(scope, receive, send)
                        return
                except Exception as e:
                    logger.error(f"Middleware validation error for link {link_id}: {e}")

            # Not paid: Return 402 Payment Required JSON
            ref = f"REQ_{path.strip('/').replace('/', '_')}_{uuid.uuid4().hex[:6]}"
            new_link = self.client.create_payment_link(amount=price, description=ref)
            
            challenge = PaywallChallenge(
                payment_link_id=new_link.id,
                payment_url=new_link.url,
                amount_usdc=price,
                reference_id=ref,
            )
            response_body = challenge.json().encode("utf-8")

            await send({
                "type": "http.response.start",
                "status": 402,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"x-moove-payment-url", new_link.url.encode("utf-8")),
                    (b"x-moove-link-id", new_link.id.encode("utf-8")),
                ],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })
            return

        await self.app(scope, receive, send)
