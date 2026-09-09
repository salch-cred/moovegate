"""
Moove MCP Server - Model Context Protocol for Moove Agentic Payments
Exposes Moove Receive Agent and Fair-Exchange tools to LLMs (Claude, Cursor, Windsurf, AutoGen).
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List

# Ensure core package is resolvable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.moove_client import MooveClient, MooveAPIError
from core.fair_exchange_state_machine import FairExchangeContract, ExchangeState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("moove_mcp_server")


class MooveMCPServer:
    """
    Standard MCP JSON-RPC Server for Moove Agentic Payments.
    Communicates via stdin/stdout according to the Model Context Protocol specification.
    """

    def __init__(self):
        self.client = MooveClient()
        self.contracts: Dict[str, FairExchangeContract] = {}

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "moove_create_payment_link",
                "description": "Create a hosted crypto payment link via Moove Receive Agent to bill a client or agent in USDC.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount_usdc": {
                            "type": "string",
                            "description": "Decimal string representing payment amount (e.g. '15.00'). Never floating point.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Unique order reference, invoice number, or contract hash for reconciliation.",
                        },
                        "max_usage": {
                            "type": "integer",
                            "description": "Maximum usage count. Default is 1 for one-off payments.",
                            "default": 1,
                        },
                    },
                    "required": ["amount_usdc"],
                },
            },
            {
                "name": "moove_check_payment_status",
                "description": "Check whether a Moove payment link has been settled on-chain ('active', 'completed', or 'inactive').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_link_id": {
                            "type": "string",
                            "description": "The Moove payment link ID (e.g. pl_xxx).",
                        },
                    },
                    "required": ["payment_link_id"],
                },
            },
            {
                "name": "moove_poll_settlement",
                "description": "Politely poll until a payment link is marked 'completed' by Moove cross-chain settlement or timeout occurs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_link_id": {
                            "type": "string",
                            "description": "The Moove payment link ID to poll.",
                        },
                        "timeout_seconds": {
                            "type": "integer",
                            "description": "Maximum wait duration in seconds (default 60).",
                            "default": 60,
                        },
                    },
                    "required": ["payment_link_id"],
                },
            },
            {
                "name": "moove_fair_exchange_initiate",
                "description": "Initiate an atomic fair-exchange bilateral contract with another agent, generating a cryptographic commitment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Unique identifier for the task"},
                        "client_agent_id": {"type": "string", "description": "Buyer agent identifier"},
                        "provider_agent_id": {"type": "string", "description": "Seller agent identifier"},
                        "task_specification": {"type": "string", "description": "Description of work performed"},
                        "price_usdc": {"type": "string", "description": "Price in USDC decimal string (e.g. '25.00')"},
                        "deliverable_payload": {
                            "type": "object",
                            "description": "The confidential deliverable to be sealed in escrow until payment settles.",
                        },
                    },
                    "required": ["task_id", "client_agent_id", "provider_agent_id", "price_usdc", "deliverable_payload"],
                },
            },
            {
                "name": "moove_list_settled_links",
                "description": "List recently completed Moove payment links for accounting and revenue tracking.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "offset": {"type": "integer", "description": "Pagination offset", "default": 0}
                    },
                },
            },
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Executing tool: {tool_name}")
        try:
            if tool_name == "moove_create_payment_link":
                amount = str(arguments["amount_usdc"])
                desc = arguments.get("description")
                max_u = arguments.get("max_usage", 1)
                link = self.client.create_payment_link(amount=amount, description=desc, max_usage=max_u)
                return {
                    "success": True,
                    "payment_link_id": link.id,
                    "payment_url": link.url,
                    "status": link.status.value,
                    "amount_usdc": link.toAmount,
                    "description": link.description,
                }

            elif tool_name == "moove_check_payment_status":
                link_id = arguments["payment_link_id"]
                link = self.client.get_payment_link(link_id)
                return {
                    "success": True,
                    "payment_link_id": link.id,
                    "status": link.status.value,
                    "received_amount": link.receivedAmount,
                    "settled": link.status.value == "completed",
                }

            elif tool_name == "moove_poll_settlement":
                link_id = arguments["payment_link_id"]
                timeout = arguments.get("timeout_seconds", 60)
                link = self.client.poll_settlement(link_id, timeout_seconds=timeout)
                return {
                    "success": True,
                    "payment_link_id": link.id,
                    "status": link.status.value,
                    "received_amount": link.receivedAmount,
                    "settled": True,
                }

            elif tool_name == "moove_fair_exchange_initiate":
                task_id = arguments["task_id"]
                contract = FairExchangeContract(
                    task_id=task_id,
                    client_agent_id=arguments["client_agent_id"],
                    provider_agent_id=arguments["provider_agent_id"],
                    task_specification=arguments.get("task_specification", ""),
                    price_usdc=str(arguments["price_usdc"]),
                    moove_client=self.client,
                )
                # Commit and invoice
                commitment_hash = contract.commit_deliverable(arguments["deliverable_payload"])
                invoice_url = contract.generate_moove_invoice()
                self.contracts[task_id] = contract

                return {
                    "success": True,
                    "task_id": task_id,
                    "state": contract.state.value,
                    "commitment_sha256": commitment_hash,
                    "moove_link_id": contract.payment_link_id,
                    "payment_url": invoice_url,
                    "price_usdc": contract.price_usdc,
                    "instructions": "Deliver payment_url to counterparty agent. Once settled, call verify_and_settle.",
                }

            elif tool_name == "moove_list_settled_links":
                offset = arguments.get("offset", 0)
                links = self.client.list_completed_links(offset=offset)
                return {
                    "success": True,
                    "count": len(links),
                    "links": [l.dict() for l in links],
                }

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Error running tool {tool_name}: {e}")
            return {"error": str(e), "success": False}

    def run_stdio(self):
        """Standard IO JSON-RPC loop for MCP."""
        logger.info("Moove MCP Server listening on stdio...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                req_id = req.get("id")
                method = req.get("method")

                if method == "tools/list":
                    res = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": self.get_tool_definitions()}}
                elif method == "tools/call":
                    params = req.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    tool_result = self.execute_tool(tool_name, arguments)
                    res = {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(tool_result, indent=2)}]}}
                else:
                    res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_res = {"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}}
                sys.stdout.write(json.dumps(err_res) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = MooveMCPServer()
    server.run_stdio()
