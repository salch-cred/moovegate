"""
MooveGate - LangChain / LangGraph Agent Tool Example
Demonstrates an autonomous LangChain Agent using MooveGate tools to pay for external research.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.moove_client import MooveClient
from core.fair_exchange_state_machine import FairExchangeContract


class MoovePaymentTool:
    """
    Standard LangChain / CrewAI Compatible Tool Wrapper for Moove Agentic Payments.
    """
    name = "moove_receive_invoice"
    description = "Create a cross-chain payment link via Moove Agentic Payments to invoice a peer agent or client."

    def __init__(self, client: MooveClient = None):
        self.client = client or MooveClient(sandbox=True)

    def run(self, amount_usdc: str, task_memo: str) -> str:
        link = self.client.create_payment_link(amount=amount_usdc, description=task_memo)
        return json.dumps({
            "payment_link_url": link.url,
            "link_id": link.id,
            "status": link.status.value,
            "amount_usdc": link.toAmount,
        })


def run_langchain_agent_demo():
    print("=" * 70)
    print(" [*] LANGCHAIN / AUTOGEN AGENT TOOL INTEGRATION")
    print("=" * 70)

    tool = MoovePaymentTool()
    print("[1] AI Agent invokes MoovePaymentTool...")
    result = tool.run(amount_usdc="15.00", task_memo="DeepResearch-Task-42")
    print(f"Tool Output: {result}")

    data = json.loads(result)
    print("\n[2] Agent sends checkout URL to principal/counterparty...")
    print(f"  URL: {data['payment_link_url']}")

    print("\n[3] Simulating counterparty payment...")
    tool.client.simulate_sandbox_payment(data["link_id"])
    verified = tool.client.get_payment_link(data["link_id"])
    print(f"  Final Settlement Status: {verified.status.value} (Received {verified.receivedAmount} USDC)")
    print("\n[OK] Autonomous Agent tool execution verified successfully!")


if __name__ == "__main__":
    run_langchain_agent_demo()
