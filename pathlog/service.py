"""High-level service orchestration for PathLog."""

from __future__ import annotations

import base64
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from . import storage
from .crypto import (
    PassphraseRecord,
    create_passphrase_record,
    decrypt_payload,
    encrypt_payload,
    generate_master_key,
    hash_passphrase,
    unwrap_master_key,
    wrap_master_key,
)


class PathLogService:
    """Provide user-level operations for the PathLog prototype."""

    encryption_policy: Dict[str, Any] = {
        "algorithm": "AES-256-GCM via Fernet",
        "rotation": "Per-request manual rotation supported",
        "root_key": "Passphrase-wrapped optional",
        "notes": "Prototype implementation for local testing",
    }

    def register_user(
        self,
        *,
        email: str,
        accept_terms: bool,
        passphrase: str | None = None,
        alias: str | None = None,
    ) -> dict[str, Any]:
        if not accept_terms:
            raise ValueError("User must accept encryption policy and consent statement.")

        user_id = str(uuid.uuid4())
        master_key = generate_master_key()
        key_id = str(uuid.uuid4())
        passphrase_record: PassphraseRecord | None = None
        if passphrase:
            passphrase_record = create_passphrase_record(passphrase)

        wrapped_key = wrap_master_key(master_key, passphrase if passphrase_record else None)
        key_record = {
            "key_id": key_id,
            "wrapped_key": wrapped_key["wrapped_key"],
            "salt": wrapped_key["salt"],
            "requires_passphrase": wrapped_key["requires_passphrase"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        profile: Dict[str, Any] = {
            "user_id": user_id,
            "email": email,
            "alias": alias,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "encryption_policy": self.encryption_policy,
            "current_key_id": key_id,
            "keys": {key_id: key_record},
            "connected_tools": [],
        }
        if passphrase_record:
            profile["passphrase"] = {
                "salt": passphrase_record.salt_b64,
                "hash": passphrase_record.hash_b64,
            }

        storage.save_profile(user_id, profile)
        key_file = {
            "user_id": user_id,
            "key_id": key_id,
            "created_at": key_record["created_at"],
            "encryption_policy": self.encryption_policy,
            "wrapped_key": key_record["wrapped_key"],
            "salt": key_record["salt"],
            "requires_passphrase": key_record["requires_passphrase"],
        }
        key_file_path = storage.write_key_file(user_id, key_id, key_file)

        return {
            "user_id": user_id,
            "key_id": key_id,
            "key_file_path": str(key_file_path),
        }

    # ---------------------------------------------------------------------
    def connect_tool(self, user_id: str, tool_name: str) -> List[str]:
        profile = storage.load_profile(user_id)
        tools: List[str] = list(profile.get("connected_tools", []))
        if tool_name not in tools:
            tools.append(tool_name)
        profile["connected_tools"] = tools
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        storage.save_profile(user_id, profile)
        return tools

    # ---------------------------------------------------------------------
    def capture_event(
        self,
        *,
        user_id: str,
        tool_name: str,
        prompt: str,
        response: str,
        metadata: Dict[str, Any],
        passphrase: str | None,
    ) -> dict[str, Any]:
        profile = storage.load_profile(user_id)
        self._validate_passphrase(profile, passphrase)
        current_key_id = profile["current_key_id"]
        key_record = profile["keys"][current_key_id]
        master_key = self._unwrap_key_record(key_record, passphrase)

        event_id = str(uuid.uuid4())
        payload = {
            "event_id": event_id,
            "tool_name": tool_name,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        ciphertext = encrypt_payload(master_key, payload)
        storage.append_event(
            user_id,
            {
                "event_id": event_id,
                "key_id": current_key_id,
                "ciphertext": ciphertext,
            },
        )
        return {
            "event_id": event_id,
            "stored_at": payload["timestamp"],
        }

    # ---------------------------------------------------------------------
    def fetch_timeline(self, user_id: str, passphrase: str | None) -> List[dict[str, Any]]:
        profile = storage.load_profile(user_id)
        self._validate_passphrase(profile, passphrase)
        key_cache: Dict[str, bytes] = {}
        events: List[dict[str, Any]] = []
        for entry in storage.iter_event_entries(user_id):
            key_id = entry.get("key_id")
            key_record = profile["keys"].get(key_id)
            if not key_record:
                continue
            if key_id not in key_cache:
                key_cache[key_id] = self._unwrap_key_record(
                    key_record,
                    passphrase if key_record.get("requires_passphrase") else None,
                )
            payload = decrypt_payload(key_cache[key_id], entry["ciphertext"])
            events.append(payload)
        events.sort(key=lambda item: item.get("timestamp", ""))
        return events

    # ---------------------------------------------------------------------
    def stats(self, user_id: str, passphrase: str | None) -> dict[str, Any]:
        events = self.fetch_timeline(user_id, passphrase)
        counter = Counter(event.get("tool_name", "unknown") for event in events)
        return {
            "user_id": user_id,
            "total_events": len(events),
            "by_tool": dict(counter),
        }

    # ---------------------------------------------------------------------
    def export_bundle(self, user_id: str) -> dict[str, Any]:
        bundle = storage.export_bundle(user_id)
        return {**bundle, "exported_at": datetime.now(timezone.utc).isoformat()}

    # ---------------------------------------------------------------------
    def import_bundle(self, bundle: dict[str, Any], target_user_id: str | None = None) -> dict[str, Any]:
        profile = bundle.get("profile") or {}
        source_user_id = profile.get("user_id")
        user_id = target_user_id or source_user_id or str(uuid.uuid4())
        if source_user_id and target_user_id and source_user_id != target_user_id:
            profile["user_id"] = user_id
        elif not source_user_id:
            profile["user_id"] = user_id
        bundle["profile"] = profile
        storage.import_bundle(bundle, user_id)
        events = bundle.get("events") or []
        return {
            "user_id": user_id,
            "imported_events": len(events),
        }

    # ---------------------------------------------------------------------
    def rotate_key(self, user_id: str, passphrase: str | None) -> dict[str, Any]:
        profile = storage.load_profile(user_id)
        self._validate_passphrase(profile, passphrase)
        current_key_id = profile["current_key_id"]
        original_keys = dict(profile.get("keys", {}))
        current_key_record = original_keys[current_key_id]
        current_master = self._unwrap_key_record(current_key_record, passphrase)

        new_master = generate_master_key()
        new_key_id = str(uuid.uuid4())
        wrapped = wrap_master_key(new_master, passphrase if profile.get("passphrase") else None)
        new_key_record = {
            "key_id": new_key_id,
            "wrapped_key": wrapped["wrapped_key"],
            "salt": wrapped["salt"],
            "requires_passphrase": wrapped["requires_passphrase"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        profile.setdefault("keys", {})[new_key_id] = new_key_record
        profile["current_key_id"] = new_key_id
        profile.setdefault("key_history", []).append(
            {"key_id": new_key_id, "created_at": new_key_record["created_at"]}
        )

        # Re-encrypt existing events with the new key
        key_cache: Dict[str, bytes] = {current_key_id: current_master}
        new_events = []
        for entry in storage.iter_event_entries(user_id):
            key_id = entry.get("key_id", current_key_id)
            key_record = original_keys.get(key_id)
            if not key_record:
                continue
            if key_id not in key_cache:
                key_cache[key_id] = self._unwrap_key_record(
                    key_record,
                    passphrase if key_record.get("requires_passphrase") else None,
                )
            payload = decrypt_payload(key_cache[key_id], entry["ciphertext"])
            ciphertext = encrypt_payload(new_master, payload)
            new_entry = dict(entry)
            new_entry["ciphertext"] = ciphertext
            new_entry["key_id"] = new_key_id
            new_events.append(new_entry)
        storage.write_events(user_id, new_events)
        storage.save_profile(user_id, profile)
        storage.write_key_file(
            user_id,
            new_key_id,
            {
                "user_id": user_id,
                "key_id": new_key_id,
                "created_at": new_key_record["created_at"],
                "encryption_policy": self.encryption_policy,
                "wrapped_key": new_key_record["wrapped_key"],
                "salt": new_key_record["salt"],
                "requires_passphrase": new_key_record["requires_passphrase"],
            },
        )

        return {
            "user_id": user_id,
            "key_id": new_key_id,
            "message": "Master key rotated and existing events re-encrypted.",
        }

    # ------------------------------------------------------------------
    def _validate_passphrase(self, profile: Dict[str, Any], passphrase: str | None) -> None:
        record = profile.get("passphrase")
        if not record:
            return
        if not passphrase:
            raise ValueError("Passphrase is required for this vault.")
        salt = base64.urlsafe_b64decode(record["salt"].encode("utf-8"))
        if record["hash"] != hash_passphrase(passphrase, salt):
            raise ValueError("Invalid passphrase provided.")

    def _unwrap_key_record(self, key_record: Dict[str, Any], passphrase: str | None) -> bytes:
        return unwrap_master_key(
            key_record["wrapped_key"],
            salt_b64=key_record["salt"],
            requires_passphrase=key_record.get("requires_passphrase", False),
            passphrase=passphrase,
        )


__all__ = ["PathLogService"]
