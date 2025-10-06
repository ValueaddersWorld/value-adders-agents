# Value Adders Agents

Autonomous multi-agent orchestration for the Value Adders World initiative. This repo wires a full Autogen AgentChat cluster (CEO, Product, Developer, etc.) into a daily sprint loop backed by Notion, Markdown deliverables, and optional Slack alerts.

- [Automation Playbook](docs/automation_playbook.md) - detailed setup and operations guide.
- [PathLog Blueprint](docs/pathlog_blueprint.md) - encrypted memory architecture and rollout plan.
- `orchestration_auto_demo.py` - run the full team with Notion + deliverables.
- `automation/scheduled_runner.py` - daily scheduler (used by Task Scheduler or cron).
- [PathLog Bridge Extension](pathlog/browser_extension/README.md) - Chrome context menu to send selections to the vault.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in OpenAI + Notion credentials
python orchestration_auto_demo.py
```

This logs tasks to Notion, writes Markdown deliverables under `outputs/`, and generates follow-up context for the next automated run.

## PathLog Prototype (Local Vault)

```bash
pip install fastapi uvicorn cryptography pydantic
python -m pathlog.quickstart          # walkthrough without API
uvicorn pathlog.api:app --reload --port 8002
```

Endpoints:
- `POST /consent` - capture consent, generate AES-256 key, write key file.
- `POST /connect` - register ChatGPT, Claude, or custom agents to the vault.
- `POST /capture` - log prompts/responses (encrypted at rest).
- `GET /timeline/{user_id}` - decrypt sessions with the supplied passphrase.
- `GET /stats/{user_id}` - growth metrics by tool.
- `POST /export` & `/import` - backup and restore bundles.
- `POST /rotate-key` - rotate master key and re-encrypt history.

API docs are available at `http://localhost:8002/docs` once the server is running.

### Chrome Extension Quickstart

1. Run the PathLog API locally (`uvicorn pathlog.api:app --host 127.0.0.1 --port 8002`).
2. Open `chrome://extensions`, enable Developer Mode, and **Load unpacked** from `pathlog/browser_extension`.
3. Configure the extension options with your PathLog base URL, user ID, and optional passphrase.
4. Highlight any chat text and either right-click to choose **Send selection to PathLog** or press **Alt+Shift+L** to push the selection into the vault.

## Build PDF Manual

To build the automation manual locally:

```bash
make pdf
```

The generated file will be in `docs/value-adders-automation-manual.pdf` and is also produced automatically by GitHub Actions when relevant files change.

## Daily Automation

To run daily, use the provided PowerShell helper:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File automation\run_sprint.ps1
```

The [automation playbook](docs/automation_playbook.md) explains how to schedule this in Windows Task Scheduler and how to adapt the prompts for other domains or clients.

