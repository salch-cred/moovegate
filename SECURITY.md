# Security Policy

## Reporting Security Vulnerabilities

MooveGate is built on the **Zero-Custody Principle**. The protocol does not take custody of user assets, store private keys, or execute unverified fund transfers.

If you believe you have found a security issue with MooveGate:
1. Please report it privately to `security@moovegate.io` or open a private GitHub security advisory.
2. Provide reproducible proof-of-concept code and environment details.

## Moove Security Invariants

- Never commit `MOOVE_API_KEY` into git or configuration files.
- Always retrieve API keys from environment variables.
- All payment link reconciliation relies on cryptographic SHA-256 pre-image commitments.
