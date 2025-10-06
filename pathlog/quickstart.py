"""Minimal CLI walkthrough for PathLog prototype."""

from __future__ import annotations

import json
from pathlib import Path

from .service import PathLogService


def main() -> None:
    service = PathLogService()

    print("[1] Provision vault and generate key...")
    consent = service.register_user(
        email="pilot@pathlog.local",
        accept_terms=True,
        passphrase="demo-pass",
        alias="pilot",
    )
    user_id = consent["user_id"]
    print(f"    user_id = {user_id}")
    print(f"    key stored at = {consent['key_file_path']}")

    print("[2] Connect ChatGPT and Claude hooks...")
    service.connect_tool(user_id, "ChatGPT")
    service.connect_tool(user_id, "Claude")

    print("[3] Capture an interaction event...")
    capture = service.capture_event(
        user_id=user_id,
        tool_name="ChatGPT",
        prompt="How do I launch PathLog?",
        response="Start with encrypted capture, build recall surfaces, rotate keys regularly.",
        metadata={"channel": "web"},
        passphrase="demo-pass",
    )
    print(f"    stored event {capture['event_id']} at {capture['stored_at']}")

    print("[4] Review timeline entries...")
    timeline = service.fetch_timeline(user_id, "demo-pass")
    print(json.dumps(timeline, indent=2))

    print("[5] Stats snapshot...")
    stats = service.stats(user_id, "demo-pass")
    print(json.dumps(stats, indent=2))

    print("[6] Export encrypted bundle...")
    bundle = service.export_bundle(user_id)
    export_path = Path("pathlog_quickstart_export.json")
    export_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print(f"    export saved to {export_path.resolve()}")

    print("[7] Rotate key and re-encrypt history...")
    rotated = service.rotate_key(user_id, "demo-pass")
    print(json.dumps(rotated, indent=2))

    print("PathLog quickstart complete.")


if __name__ == "__main__":  # pragma: no cover
    main()
