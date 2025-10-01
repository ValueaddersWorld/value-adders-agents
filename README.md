# Value Adders Agents

Autonomous multi-agent orchestration for the Value Adders World initiative. This repo wires a full Autogen AgentChat cluster (CEO, Product, Developer, etc.) into a daily sprint loop backed by Notion, Markdown deliverables, and optional Slack alerts.

- [Automation Playbook](docs/automation_playbook.md) – detailed setup and operations guide.
- `orchestration_auto_demo.py` – run the full team with Notion + deliverables.
- `automation/scheduled_runner.py` – daily scheduler (used by Task Scheduler or cron).

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in OpenAI + Notion credentials
python orchestration_auto_demo.py
```

This logs tasks to Notion, writes Markdown deliverables under `outputs/`, and generates follow-up context for the next automated run.

## Automation

To build the PDF manual locally:
```bash
make pdf
```
The generated file will be in `docs/value-adders-automation-manual.pdf` and is also produced automatically by GitHub Actions when relevant files change.

## Automation

To run daily, use the provided PowerShell helper:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File automation\run_sprint.ps1
```

The [automation playbook](docs/automation_playbook.md) explains how to schedule this in Windows Task Scheduler and how to adapt the prompts for other domains or clients.
