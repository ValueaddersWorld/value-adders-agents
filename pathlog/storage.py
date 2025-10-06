"""File-system storage helpers for the PathLog prototype."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

BASE_DIR = Path(__file__).resolve().parent.parent / "pathlog_data"
PROFILE_FILENAME = "profile.json"
EVENTS_FILENAME = "events.jsonl"
KEYS_DIRNAME = "keys"


def _ensure_base_dir() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)


def _user_dir(user_id: str) -> Path:
    _ensure_base_dir()
    return BASE_DIR / user_id


def ensure_user_dirs(user_id: str) -> Path:
    """Create the user directory structure if it does not already exist."""
    user_dir = _user_dir(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / KEYS_DIRNAME).mkdir(parents=True, exist_ok=True)
    (user_dir / EVENTS_FILENAME).touch(exist_ok=True)
    return user_dir


def profile_path(user_id: str) -> Path:
    return ensure_user_dirs(user_id) / PROFILE_FILENAME


def key_path(user_id: str, key_id: str) -> Path:
    return ensure_user_dirs(user_id) / KEYS_DIRNAME / f"{key_id}.json"


def events_path(user_id: str) -> Path:
    return ensure_user_dirs(user_id) / EVENTS_FILENAME


def save_profile(user_id: str, profile: dict[str, Any]) -> None:
    path = profile_path(user_id)
    path.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")


def load_profile(user_id: str) -> dict[str, Any]:
    path = profile_path(user_id)
    if not path.exists():
        raise FileNotFoundError(f"No PathLog profile found for user {user_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_key_file(user_id: str, key_id: str, data: dict[str, Any]) -> Path:
    path = key_path(user_id, key_id)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_events(user_id: str, entries: Iterable[dict[str, Any]]) -> None:
    path = events_path(user_id)
    with path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, separators=(",", ":")))
            handle.write("\n")


def append_event(user_id: str, entry: dict[str, Any]) -> None:
    entry = dict(entry)
    entry.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    path = events_path(user_id)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, separators=(",", ":")))
        handle.write("\n")


def iter_event_entries(user_id: str) -> Iterable[dict[str, Any]]:
    path = events_path(user_id)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def export_bundle(user_id: str) -> dict[str, Any]:
    profile = load_profile(user_id)
    events = list(iter_event_entries(user_id))
    keys_dir = ensure_user_dirs(user_id) / KEYS_DIRNAME
    key_files = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in keys_dir.glob("*.json")
    }
    return {
        "version": "1.0",
        "profile": profile,
        "events": events,
        "keys": key_files,
    }


def import_bundle(bundle: dict[str, Any], target_user_id: str) -> None:
    profile = bundle.get("profile") or {}
    events = bundle.get("events") or []
    keys = bundle.get("keys") or {}

    save_profile(target_user_id, profile)
    for key_id, data in keys.items():
        write_key_file(target_user_id, key_id, data)
    write_events(target_user_id, events)


__all__ = [
    "BASE_DIR",
    "save_profile",
    "load_profile",
    "write_key_file",
    "write_events",
    "append_event",
    "iter_event_entries",
    "export_bundle",
    "import_bundle",
]
