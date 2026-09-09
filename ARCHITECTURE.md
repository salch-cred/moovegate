# MooveGate Architecture & Threat Model

```
+---------------------------------------------------------------------------------+
|                           AUTONOMOUS AGENT ECOSYSTEM                            |
|                                                                                 |
|   +-----------------------+                    +----------------------------+   |
|   |   CLIENT AGENT (A)    |                    |     SUPPLIER AGENT (B)     |   |
|   | (Claude / Cursor IDE) |                    |   (Auditor / Prover Bot)   |   |
|   +-----------+-----------+                    +--------------+-------------+   |
|               |                                               |                 |
|               |  1. Request Task (e.g. Audit, Compute)        |                 |
|               +---------------------------------------------->|                 |
|               |                                               |                 |
|               |                                       [Compute Deliverable D]   |
|               |                                       [Derive Ephemeral Key K]  |
|               |                                       [Seal Envelope C]         |
|               |                                       [Calculate Hash h=SHA256] |
|               |                                               |                 |
|               |  2. Deliver Sealed Envelope (C, h, URL)       |                 |
|               |<----------------------------------------------+                 |
|               |                                               |                 |
|   +-----------v-----------------------------------------------v-------------+   |
|   |                           MOOVEGATE PROTOCOL LAYER                      |   |
|   |                                                                         |   |
|   |   +---------------------+   +---------------------+   +-------------+   |   |
|   |   |   HLDM COMMITMENT   |   |   STATE MACHINE     |   | MCP SERVER  |   |   |
|   |   |   (SHA-256 Engine)  |   |   (AAFX Protocol)   |   | (JSON-RPC)  |   |   |
|   |   +----------+----------+   +----------+----------+   +------+------+   |   |
|   +--------------|-------------------------|---------------------|----------+   |
|                  |                         |                     |              |
|                  |  3. POST /v1/payment-link                     |              |
|                  |     toAmount: "50.00"                         |              |
|                  |     description: "AFX_Task_h[:12]"            |              |
|                  v                                               v              |
|   +-------------------------------------------------------------------------+   |
|   |                     MOOVE AGENTIC PAYMENTS PLATFORM                     |   |
|   |                                                                         |   |
|   |   [Cross-Chain Clearing across 30+ Blockchains & 16,000+ Tokens]        |   |
|   |   [USDC Direct Disbursement to Supplier's Moove Profile Handle]         |   |
|   +------------------------------------+------------------------------------+   |
|                                        |                                        |
|                                        | 4. On-Chain Settlement Finality        |
|                                        |    GET /v1/payment-link/{id}           |
|                                        v                                        |
|                       +---------------------------------+                       |
|                       |   ATOMIC KEY RELEASE & VERIFY   |                       |
|                       |   Decryption Key K Released     |                       |
|                       |   Pre-image h' == h Confirmed   |                       |
|                       +---------------------------------+                       |
+---------------------------------------------------------------------------------+
```

## Security Guarantees

1. **Safety**: No participant can be forced into counterparty exposure. The deliverable is mathematically tied to the Moove invoice before the transaction occurs.
2. **Liveness**: If either party terminates early or network partitions occur, unverified payment links simply expire (`inactive`) without economic loss.
3. **Sybil Resistance**: Invoicing costs a real verifiable computation and on-chain settlement fee, preventing spam attacks on autonomous agent discovery registries.
