# MooveGate (MooveSynapse) ⚡

> **The Universal Autonomous Agent-to-Agent (A2A) Micro-Commerce Gateway & Model Context Protocol (MCP) Server for Moove Agentic Payments.**

[![Moove Developer Program](https://img.shields.io/badge/Moove_Developer_Fund-$100k_Grant_Candidate-FFCE31?style=for-the-badge&logo=crypto)](https://www.moove.xyz/blog/everything-you-need-to-know-about-moove-developer-program)
[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-10B981?style=for-the-badge&logo=github)](https://salch-cred.github.io/moovegate/)
[![CI Status](https://github.com/salch-cred/moovegate/actions/workflows/ci.yml/badge.svg)](https://github.com/salch-cred/moovegate/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)

🔗 **Live Website**: [https://salch-cred.github.io/moovegate/](https://salch-cred.github.io/moovegate/)  
📊 **Interactive Studio**: [https://salch-cred.github.io/moovegate/dashboard/](https://salch-cred.github.io/moovegate/dashboard/)  
🎯 **Executive Pitch Deck**: [https://salch-cred.github.io/moovegate/pitch/](https://salch-cred.github.io/moovegate/pitch/)  

---

## 🌟 The Vision

AI agents are transitioning from passive conversational assistants into autonomous economic actors that negotiate, barter, and settle compute, real-time datasets, and fine-tuned inferences.

However, existing payment mechanisms fail autonomous agents:
1. **Legacy Rails (Stripe, Cards, Banks)**: Require human KYC, cards, 3D Secure / 2FA prompts, and high minimum fees ($0.30 + 3%) that destroy micro-transactions.
2. **The Distributed Fair-Exchange Dilemma (Cleve, 1986)**: If Agent A pays Agent B upfront, Agent B may defect or hallucinate. If Agent B delivers the work upfront, Agent A has zero incentive to pay.

**MooveGate** solves this fundamental bottleneck by pairing **Cryptographic Hash Commitments (SHA-256)** with **Moove Agentic Payments' cross-chain Receive Agent**.

---

## 🚀 Key Innovations

### 1. Zero-Custody Cryptographic Fair-Exchange
- **Hash-Locked Deliverable Mechanism (HLDM)**: The supplying agent locks its deliverable under an ephemeral 256-bit symmetric key and publishes an immutable SHA-256 digest.
- **Moove Receive Agent Binding**: An official Moove payment link (`POST /v1/payment-link`) is generated with the hash commitment encoded in the `description` field for 100% accounting transparency.
- **On-Chain Settlement Verification**: Settlement across 30+ chains and 16,000+ cryptocurrencies is verified via `GET /v1/payment-link/{id}` before releasing the decryption key.
- **Zero Custody**: MooveGate **never moves money and never holds private keys**. Funds settle directly to the developer's verified Moove Handle.

### 2. First Moove Model Context Protocol (MCP) Server
Enables any AI agent running in **Anthropic Claude Desktop, Cursor IDE, Windsurf, LangGraph, or AutoGen** to natively invoice and receive payments in USDC.

### 3. Drop-in HTTP 402 Paywall Middleware
Turn any Python FastAPI or Node.js endpoint into an autonomous crypto-monetized pay-per-call service in 3 lines of code:

```python
@moove_paywall(price="5.00", memo="AuditReport")
def audit_smart_contract(repo_url: str):
    return {"status": "verified", "vulnerabilities": 0}
```

---

## 📂 Project Architecture

```
moovegate/
├── WHITE_PAPER.md                      # Formal 50-year scientific research whitepaper
├── GRANT_APPLICATION.md                # $10,000 Moove Developer Fund proposal
├── core/                               # Core protocol engine
│   ├── cryptography.py                 # SHA-256 commitment & AES-GCM envelope engine
│   ├── moove_client.py                 # Moove API client (RFC decimal strings, polite polling)
│   ├── fair_exchange_state_machine.py  # Formal AAFX state machine
│   ├── paywall_middleware.py           # HTTP 402 autonomous paywall middleware
│   └── types.py                        # Pydantic models matching Moove OpenAPI spec
├── mcp_server/                         # Model Context Protocol Server
│   └── server.py                       # JSON-RPC stdio MCP server for Claude/Cursor
├── sdk/
│   ├── python/moovegate.py             # Python developer SDK
│   └── typescript/moovegate.ts         # TypeScript developer SDK
├── dashboard/
│   └── index.html                      # Interactive UI & Live A2A Simulation Studio
├── simulation/
│   └── run_autonomous_economy.py       # Live multi-agent autonomous commerce simulation
└── tests/
    └── test_fair_exchange.py           # Comprehensive unit & cryptographic test suite
```

---

## ⚡ Quickstart

### 1. Run Autonomous Multi-Agent Simulation
Simulate end-to-end bilateral agent commerce with live cryptographic commitments and Moove settlement verification:

```bash
python simulation/run_autonomous_economy.py
```

### 2. Run Test Suite
```bash
python -m unittest tests/test_fair_exchange.py
```

### 3. Launch Interactive Web Dashboard
Open `dashboard/index.html` in any modern web browser or preview via your local server:
- Experience the live 4-step A2A negotiation simulator.
- Generate and test live or sandbox Moove payment links.
- Monitor real-time merchant analytics and settlement latency.

---

## 🔌 Using with Claude Desktop or Cursor (MCP)

Add the following to your `claude_desktop_config.json` or Cursor MCP configuration:

```json
{
  "mcpServers": {
    "moovegate": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "MOOVE_API_KEY": "mk_live_your_key_here",
        "MOOVE_API_BASE_URL": "https://api.moove.xyz"
      }
    }
  }
}
```

Available Tools:
- `moove_create_payment_link`: Create hosted payment link for an invoice.
- `moove_check_payment_status`: Inspect whether a link has been settled on-chain.
- `moove_poll_settlement`: Politely poll until settlement confirmation.
- `moove_fair_exchange_initiate`: Lock deliverable under hash commitment and issue Moove invoice.
- `moove_list_settled_links`: Reconcile completed payments.

---

## 🏆 Moove Developer Program Alignment

MooveGate directly targets the **$100,000 Moove Developer Fund** (claiming up to $10,000 in USDC across 4 milestone tranches):
- **Category**: AI Agent Builders & Developer Infrastructure.
- **Why Moove Appreciates This**: Rather than waiting for humans to manually click checkout buttons, MooveGate enables autonomous agents to settle millions of micro-transactions continuously on Moove rails.
- See [`GRANT_APPLICATION.md`](./GRANT_APPLICATION.md) for the complete submission package.
- See [`WHITE_PAPER.md`](./WHITE_PAPER.md) for mathematical safety and game-theoretic proofs.

---

## 📜 License
MIT © 2026 MooveGate Contributors. Built on [moove.xyz](https://www.moove.xyz).
