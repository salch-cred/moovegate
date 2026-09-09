"""
MooveSynapse Cryptographic Fair-Exchange Module
Implements Hash-Commitment & Sealed Envelope Protocol for Autonomous Agent Commerce.
"""

import hashlib
import hmac
import secrets
import base64
import json
from typing import Tuple, Dict, Any, Optional


def compute_sha256(data: bytes) -> str:
    """Computes SHA-256 hexadecimal digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def generate_escrow_key() -> str:
    """Generates a cryptographically secure 256-bit ephemeral symmetric key (hex)."""
    return secrets.token_hex(32)


def seal_deliverable(payload: Dict[str, Any], key_hex: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Seals an agent's computed deliverable into a cryptographic envelope.
    
    Returns:
        commitment_hash: SHA-256 digest of original plaintext JSON bytes.
        ciphertext_b64: XOR/ChaCha/Stream ciphertext base64 (zero external dependencies).
        key_hex: The 256-bit symmetric key required to open the envelope.
    """
    key = key_hex or generate_escrow_key()
    raw_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    commitment_hash = compute_sha256(raw_bytes)

    # Derive deterministic keystream using HMAC-SHA256 counter mode for zero external dependency compatibility
    key_bytes = bytes.fromhex(key)
    keystream = bytearray()
    counter = 0
    while len(keystream) < len(raw_bytes):
        block = hmac.new(key_bytes, counter.to_bytes(8, byteorder="big"), hashlib.sha256).digest()
        keystream.extend(block)
        counter += 1

    cipher_bytes = bytes([b ^ k for b, k in zip(raw_bytes, keystream[:len(raw_bytes)])])
    ciphertext_b64 = base64.b64encode(cipher_bytes).decode("ascii")

    return commitment_hash, ciphertext_b64, key


def open_deliverable(ciphertext_b64: str, key_hex: str, expected_commitment: str) -> Dict[str, Any]:
    """
    Opens a sealed envelope and verifies the hash commitment against the original pre-image.
    
    Raises:
        ValueError: If commitment verification fails or data is corrupted.
    """
    cipher_bytes = base64.b64decode(ciphertext_b64.encode("ascii"))
    key_bytes = bytes.fromhex(key_hex)

    keystream = bytearray()
    counter = 0
    while len(keystream) < len(cipher_bytes):
        block = hmac.new(key_bytes, counter.to_bytes(8, byteorder="big"), hashlib.sha256).digest()
        keystream.extend(block)
        counter += 1

    plain_bytes = bytes([b ^ k for b, k in zip(cipher_bytes, keystream[:len(cipher_bytes)])])
    computed_hash = compute_sha256(plain_bytes)

    if not hmac.compare_digest(computed_hash, expected_commitment):
        raise ValueError(
            f"Cryptographic commitment verification failed! "
            f"Expected {expected_commitment}, calculated {computed_hash}"
        )

    return json.loads(plain_bytes.decode("utf-8"))
