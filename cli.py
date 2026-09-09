"""
MooveGate CLI - Command Line Tool for Moove Agentic Payments & Fair Exchange
"""

import argparse
import sys
import os
import json
import time

from core.moove_client import MooveClient, MooveAPIError
from core.fair_exchange_state_machine import FairExchangeContract
from core.benchmark import run_benchmark
from simulation.run_autonomous_economy import run_simulation


def main():
    parser = argparse.ArgumentParser(
        prog="moovegate",
        description="MooveGate CLI - The Autonomous Agent Commerce & Fair-Exchange Tool for Moove Rails",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: create-link
    link_parser = subparsers.add_parser("create-link", help="Create a hosted Moove payment link")
    link_parser.add_argument("--amount", required=True, type=str, help="Amount in USDC decimal string (e.g. '25.00')")
    link_parser.add_argument("--desc", default="CLI-INVOICE", help="Reference identifier for accounting")
    link_parser.add_argument("--max-usage", default=1, type=int, help="Usage cap (default 1)")
    link_parser.add_argument("--live", action="store_true", help="Call live https://api.moove.xyz instead of sandbox")

    # Command: status
    status_parser = subparsers.add_parser("status", help="Inspect payment link settlement status")
    status_parser.add_argument("link_id", type=str, help="Payment link ID (e.g. pl_mock_xxx)")
    status_parser.add_argument("--live", action="store_true", help="Call live Moove API")

    # Command: simulate-a2a
    subparsers.add_parser("simulate-a2a", help="Run live autonomous multi-agent fair exchange simulation")

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run cryptographic & state machine performance benchmark")
    bench_parser.add_argument("--iterations", default=1000, type=int, help="Number of benchmark iterations")

    # Command: mcp
    subparsers.add_parser("mcp", help="Start Model Context Protocol (MCP) JSON-RPC stdio server")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "create-link":
        client = MooveClient(sandbox=not args.live)
        link = client.create_payment_link(amount=args.amount, description=args.desc, max_usage=args.max_usage)
        print(json.dumps({
            "success": True,
            "id": link.id,
            "url": link.url,
            "status": link.status.value,
            "toAmount": link.toAmount,
            "description": link.description,
        }, indent=2))

    elif args.command == "status":
        client = MooveClient(sandbox=not args.live)
        link = client.get_payment_link(args.link_id)
        print(json.dumps({
            "id": link.id,
            "status": link.status.value,
            "toAmount": link.toAmount,
            "receivedAmount": link.receivedAmount,
            "description": link.description,
        }, indent=2))

    elif args.command == "simulate-a2a":
        run_simulation()

    elif args.command == "benchmark":
        run_benchmark(args.iterations)

    elif args.command == "mcp":
        from mcp_server.server import MooveMCPServer
        server = MooveMCPServer()
        server.run_stdio()


if __name__ == "__main__":
    main()
