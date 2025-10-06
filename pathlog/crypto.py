"""Cryptographic utilities for the local PathLog prototype."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
from dataclasses import dataclass
from typing import Any

try:
    from cryptography.fernet import Fernet
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise RuntimeError(
        "cryptography package is required for PathLog encryption.\n"
        "Install with `pip install cryptography`."
    ) from exc


@dataclass(slots=True)
class PassphraseRecord:
    """Persisted passphrase verification data."""

    salt_b64: str
    hash_b64: str

    def verify(self, candidate: str) -> bool:
        return self.hash_b64 == hash_passphrase(candidate, base64.urlsafe_b64decode(self.salt_b64.encode()))


def generate_master_key() -> bytes:
    """Return a new Fernet-compatible master key."""
    return Fernet.generate_key()


def derive_fernet_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a Fernet key from a passphrase and salt using scrypt."""
    derived = hashlib.scrypt(
        passphrase.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return base64.urlsafe_b64encode(derived)


def hash_passphrase(passphrase: str, salt: bytes) -> str:
    """Hash a passphrase for verification (separate from key derivation)."""
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        passphrase.encode("utf-8"),
        salt,
        200_000,
    )
    return base64.urlsafe_b64encode(digest).decode("utf-8")


def create_passphrase_record(passphrase: str) -> PassphraseRecord:
    salt = secrets.token_bytes(16)
    return PassphraseRecord(
        salt_b64=base64.urlsafe_b64encode(salt).decode("utf-8"),
        hash_b64=hash_passphrase(passphrase, salt),
    )


def wrap_master_key(master_key: bytes, passphrase: str | None = None) -> dict[str, Any]:
    """Encrypt or encode the master key according to passphrase policy."""
    salt = secrets.token_bytes(16)
    if passphrase:
        derived_key = derive_fernet_key(passphrase, salt)
        token = Fernet(derived_key).encrypt(master_key)
        wrapped = token.decode("utf-8")
        requires_passphrase = True
    else:
        wrapped = master_key.decode("utf-8")
        requires_passphrase = False

    return {
        "wrapped_key": wrapped,
        "salt": base64.urlsafe_b64encode(salt).decode("utf-8"),
        "requires_passphrase": requires_passphrase,
    }


def unwrap_master_key(
    wrapped_key: str,
    *,
    salt_b64: str,
    requires_passphrase: bool,
    passphrase: str | None,
) -> bytes:
    """Recover the master key using the stored wrapping metadata."""
    salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
    if requires_passphrase:
        if not passphrase:
            raise ValueError("Passphrase required to unwrap master key.")
        derived_key = derive_fernet_key(passphrase, salt)
        return Fernet(derived_key).decrypt(wrapped_key.encode("utf-8"))
    return wrapped_key.encode("utf-8")


def encrypt_payload(master_key: bytes, payload: dict[str, Any]) -> str:
    """Encrypt a payload dictionary with the master key."""
    serialised = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return Fernet(master_key).encrypt(serialised).decode("utf-8")


def decrypt_payload(master_key: bytes, token: str) -> dict[str, Any]:
    """Decrypt an encrypted payload token."""
    decoded = Fernet(master_key).decrypt(token.encode("utf-8"))
    return json.loads(decoded.decode("utf-8"))


__all__ = [
    "PassphraseRecord",
    "generate_master_key",
    "create_passphrase_record",
    "wrap_master_key",
    "unwrap_master_key",
    "encrypt_payload",
    "decrypt_payload",
]
