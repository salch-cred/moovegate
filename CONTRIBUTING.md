# Contributing to MooveGate

Thank you for your interest in contributing to **MooveGate** — the open-source Autonomous Agent-to-Agent (A2A) Micro-Commerce Gateway for Moove Agentic Payments.

## Development Workflow

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/salch-cred/moovegate.git
   cd moovegate
   ```

2. **Run Tests**:
   ```bash
   python -m unittest discover tests
   ```

3. **Run Performance Benchmark**:
   ```bash
   python core/benchmark.py
   ```

4. **Run Autonomous Multi-Agent Simulation**:
   ```bash
   python simulation/run_autonomous_economy.py
   ```

## Core Architectural Invariants

When contributing pull requests, please respect the core invariants:
- **Zero Custody**: MooveGate never moves money or holds private keys. All funds are paid directly to verified Moove Profile handles via Moove Receive Agent.
- **Strict Decimal Strings**: `toAmount` must always be a decimal string (e.g. `"25.00"`), never a floating point number.
- **Polite Polling**: All on-chain status checks must implement exponential backoff with rate-limit respect.
