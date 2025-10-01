# Value Adders Multi-Agent Automation Playbook

This document captures the end-to-end process for standing up the Value Adders multi-agent cluster so it can operate autonomously, generate deliverables, and carry context forward without manual prompting. Follow these instructions to replicate the solution for new teams or paying clients.

---

## System Architecture Overview

| Component | Responsibility |
|-----------|----------------|
| **Specialist Agents** (`agents/*.py`) | Domain-specific Autogen AgentChat assistants (CEO, Developer, Marketing, etc.) enriched with a shared `web_fetch` research tool. |
| **OrchestratorAgent** (`agents/orchestrator_agent.py`) | Coordinates tasks, enforces human-review guardrails, writes updates to Notion, saves deliverables, and optionally notifies Slack. |
| **Notion database** | Primary state store. Each sprint run logs a page with agent alias, task, status, and summary. Summaries are used to generate the next sprint’s instructions. |
| **Deliverable Writer** (`outputs/deliverable_writer.py`) | Persists Markdown deliverables per agent and timestamp. Keeps a human-auditable trail of progress. |
| **Automation Playbook** (`automation/playbook.py`) | Merges weekly default prompts, optional overrides, and Notion summaries to produce follow-up tasks. |
| **Scheduler** (`automation/scheduled_runner.py` & `automation/run_sprint.ps1`) | Runs the orchestration loop on a cadence (daily by default). |
| **Notion Task Loader** (`integrations/notion_task_loader.py`) | Queries Notion for latest “Summary”/“Status” per agent and feeds context into the next run. |
| **Slack Notifier** (optional) | Sends completion or failure alerts when a webhook is configured. |

---

## Prerequisites

1. **Python 3.13** (recommended to match current environment).
2. **OpenAI API key** with access to `gpt-4o` (or equivalent model).
3. **Notion workspace** where you can create integrations and databases.
4. (Optional) **Slack incoming webhook** for notifications.
5. Project dependencies installed: `pip install -r requirements.txt` from the repo root.

---

## Initial Setup (one-time)

1. **Clone the repository**
   ```bash
   git clone https://github.com/ValueaddersWorld/value-adders-agents.git
   cd value-adders-agents
   ```

2. **Create & activate a virtual environment** (optional but recommended)
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Notion**
   - Create a database (Table view) titled e.g. **Value Adders Orchestration Log**.
   - Add the following properties (types in parentheses):
     - `Name` (Title) – auto-created by Notion.
     - `Status` (Status).
     - `Agent` (Text).
     - `Task` (Text).
     - `Summary` (Text) – **newly added** to persist follow-up context.
   - Generate an **Internal Integration Secret** (Notion Settings ➜ Integrations).
   - Share the database with that integration so it has read/write access.

5. **Populate `.env`**
   - Copy `.env.example` to `.env`.
   - Fill in at minimum:
     ```env
     OPENAI_API_KEY=sk-...
     OPENAI_MODEL=gpt-4o
     NOTION_API_KEY=ntn-...
     NOTION_DATABASE_ID=<your database id>
     ```
   - Optional toggles:
     - `REVIEW_REQUIRED_ALIASES` – comma-separated aliases that require human approval before execution (defaults to `developer,ceo`).
     - `AUTO_EXECUTE` – set to `false` to log assignments without auto-running them.
     - `WRITE_DELIVERABLES` – set to `false` to skip Markdown output.
     - `SLACK_WEBHOOK_URL` – when set, success/failure notifications are sent.

6. **Test a single run**
   ```bash
   python orchestration_auto_demo.py
   ```
   Verify:
   - Notion now has new pages with status, task, and summary.
   - Markdown files appear under `outputs/<agent>/timestamp.md` (if enabled).

---

## Daily Automation Loop

1. **Playbook generation**
   - `automation/playbook.py` builds daily tasks from:
     - Weekly defaults (`_WEEKLY_PLAYBOOK`).
     - Optional manual overrides (via `PLAYBOOK_OVERRIDE` file).
     - Latest Notion summaries using `NotionTaskLoader`.
   - “Needs Review” items produce pause instructions; completed tasks generate follow-up prompts based on prior summaries.

2. **Orchestrator run**
   - `automation/scheduled_runner.py` calls `run_auto_demo()`:
     - Orchestrator logs tasks to Notion (Assigned/Needs Review/Blocked/Completed).
     - Agents execute tasks (unless marked for review).
     - Deliverables saved to Markdown for auditors.
     - Optional Slack alerts dispatched.

3. **Human-in-the-loop guardrails**
   - Review entries in Notion marked “Needs Review”.
   - Update the page summary with approved direction or adjustments; the next run uses that summary to craft the follow-up task.

4. **Progress forward**
   - Each day’s run references the latest Notion summary, ensuring agents continue where they left off instead of repeating the same instruction set.

---

## Scheduling Autonomous Runs

### Windows Task Scheduler (already scripted)

1. The repository ships with `automation/run_sprint.ps1` which:
   ```powershell
   Set-Location "C:\Users\The General\Value Adders World Agentic AI project\value-adders-agents"
   & python -m automation.scheduled_runner --once --verbose >> "sprint.log" 2>&1
   ```
2. Register the scheduled task (PowerShell as Admin):
   ```powershell
   $taskName = 'ValueAddersSprint'
   $scriptPath = 'C:\Users\...\value-adders-agents\automation\run_sprint.ps1'
   $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
   $trigger = New-ScheduledTaskTrigger -Daily -At 08:00
   Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description 'Runs Value Adders orchestrator daily'
   ```
3. Adjust the trigger time or add `Set-ScheduledTask` if needed.
4. Log output streams to `sprint.log` in the repo root.

### macOS/Linux with cron (manual)

Add something like:
```cron
0 8 * * * cd /path/to/value-adders-agents && /path/to/python -m automation.scheduled_runner --once --verbose >> sprint.log 2>&1
```

---

## Operational Playbook

1. **Morning review**
   - Check Notion for overnight updates. Approve or comment on entries flagged “Needs Review”.
   - Inspect `outputs/<agent>/` for Markdown deliverables.

2. **Midday adjustments**
   - Use the Notion `Summary` field to capture agreed next steps. This becomes the prompt seed for the next sprint.
   - If you must override tasks globally, create a simple `key=value` file and set `PLAYBOOK_OVERRIDE` in `.env`.

3. **Monitoring**
   - If `SLACK_WEBHOOK_URL` is set, success/failure notifications flow into the configured channel.
   - `sprint.log` retains command-line output for debugging.
   - Notion status values provide a full audit trail.

4. **Extensibility**
   - Add new specialist agents by following the existing constructor signature (`tools=[web_fetch]`, etc.).
   - Register new deliverable destinations (e.g., Git commits) inside the orchestrator guardrail section.
   - Expand `_WEEKLY_PLAYBOOK` for additional themed days.

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| No Notion pages created | Confirm `.env` has correct `NOTION_*` values and the integration has access to the database. |
| Agents repeat the same tasks | Ensure `Summary` values are being written, or inspect Slack/logs for API errors preventing updates. |
| Scheduled task runs with no output | Check `sprint.log` and Windows Task Scheduler history. Set `--verbose` for more detail. |
| Deliverables folder missing | `WRITE_DELIVERABLES` may be set to `false`, or the task encountered an error before writing output. |
| Slack alerts not arriving | Verify the webhook URL and check Task Scheduler for errors due to blocked outbound requests. |

---

## Replicating for Clients

1. Fork/clone the repo into the client’s environment.
2. Repeat the **Initial Setup** steps with their API keys and Notion workspace.
3. Configure domain-specific prompts by editing `_WEEKLY_PLAYBOOK` and environment overrides.
4. Run a dry sprint (`python orchestration_auto_demo.py`) to validate outputs.
5. Hand off scheduled job instructions and review process to the client.

Following this playbook, you can deliver a ready-to-run multi-agent orchestration stack that produces measurable, progressive outcomes with minimal manual upkeep.
