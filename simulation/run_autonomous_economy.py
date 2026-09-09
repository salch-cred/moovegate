"""
MooveSynapse - Autonomous Multi-Agent Economy Simulation
Simulates end-to-end bilateral agent commerce using Moove Agentic Payments and Fair-Exchange.
"""

import sys
import os
import time
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.moove_client import MooveClient
from core.fair_exchange_state_machine import FairExchangeContract, ExchangeState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MooveEconomySim")


def run_simulation():
    print("=" * 75)
    print(" [*] MOOVESYNAPSE: AUTONOMOUS AGENT-TO-AGENT COMMERCE SIMULATION")
    print(" Powered by Moove Agentic Payments (moove.xyz)")
    print("=" * 75)

    # Initialize client in sandbox mode for deterministic testing
    client = MooveClient(sandbox=True)

    client_agent_id = "agent_venture_capitalist_01"
    provider_agent_id = "agent_auditor_sentinel_09"

    print(f"\n[1] AGENT DISCOVERY & TASK NEGOTIATION")
    print(f"  - Client:   {client_agent_id} (Autonomous Portfolio Manager)")
    print(f"  - Provider: {provider_agent_id} (Formal Verification & Audit Agent)")
    print(f"  - Task:     Formal Security Audit of Decentralized Orderbook Contract")
    print(f"  - Price:    50.00 USDC")

    # Step 1: Initialize Contract
    contract = FairExchangeContract(
        task_id="TASK_AUDIT_2026_9941",
        client_agent_id=client_agent_id,
        provider_agent_id=provider_agent_id,
        task_specification="Zero-Knowledge & Reentrancy Audit of Vault.sol",
        price_usdc="50.00",
        moove_client=client,
    )

    # Step 2: Provider computes deliverable and locks it under hash commitment
    print(f"\n[2] PROVIDER GENERATES DELIVERABLE & CRYPTOGRAPHIC COMMITMENT")
    deliverable = {
        "report_id": "REP_SEC_2026_09",
        "target_contract": "Vault.sol (v2.4.1)",
        "vulnerabilities_found": 0,
        "invariant_tests_passed": 1420,
        "formal_verification_cert": "QmW2WQi7j6c7ugJTarActp7tCMikN4F1Fh5Z7L5uT6",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    commitment_hash = contract.commit_deliverable(deliverable)
    print(f"  [+] Deliverable encrypted under ephemeral 256-bit key.")
    print(f"  [+] Hash Commitment (SHA-256): {commitment_hash}")
    print(f"  [+] State: {contract.state.value}")

    # Step 3: Provider mints Moove Payment Link via Receive Agent
    print(f"\n[3] MOOVE AGENTIC PAYMENTS INVOICE ISSUANCE")
    invoice_url = contract.generate_moove_invoice()
    print(f"  [+] Moove Payment Link created: {invoice_url}")
    print(f"  [+] Payment Link ID:           {contract.payment_link_id}")
    print(f"  [+] Amount:                    {contract.price_usdc} USDC")
    print(f"  [+] Reconcile Description:     AFX_{contract.task_id[:8]}_{commitment_hash[:12]}")
    print(f"  [+] State:                     {contract.state.value}")

    # Step 4: Client receives invoice, inspects hash commitment, and settles cross-chain
    print(f"\n[4] CLIENT VERIFIES COMMITMENT & SETTLES VIA MOOVE")
    print(f"  - Client validates link parameters and triggers cross-chain settlement...")
    time.sleep(0.5)
    
    # Simulate on-chain confirmation (e.g. payer paid via Arbitrum/Solana/Ethereum)
    client.simulate_sandbox_payment(contract.payment_link_id)
    print(f"  [+] Moove cross-chain settlement confirmed on-chain!")

    # Step 5: Verify settlement via Moove API
    print(f"\n[5] AUTOMATIC SETTLEMENT VERIFICATION")
    is_settled = contract.verify_and_settle()
    print(f"  [+] Settlement Verified: {is_settled}")
    print(f"  [+] State:               {contract.state.value}")

    # Step 6: Atomic Key Release & Decryption Verification
    print(f"\n[6] ATOMIC KEY RELEASE & DELIVERABLE VERIFICATION")
    decrypted_payload = contract.release_key_and_decrypt()
    print(f"  [+] Ephemeral key transferred to buyer.")
    print(f"  [+] Cryptographic commitment mathematically verified against pre-image.")
    print(f"  [+] State: {contract.state.value}")
    print(f"\n[7] UNLOCKED CONFIDENTIAL DELIVERABLE:")
    print(json.dumps(decrypted_payload, indent=4))

    print("\n" + "=" * 75)
    print(" [OK] FAIR-EXCHANGE SIMULATION COMPLETED WITH ZERO HUMAN INTERVENTION")
    print("      Value moved seamlessly over Moove Agentic Payments!")
    print("=" * 75)


if __name__ == "__main__":
    run_simulation()
