"""Utility for running orchestrator sprints on a schedule."""

from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime

from integrations.slack_notifier import SlackNotifier
from orchestration_auto_demo import run_auto_demo

LOGGER = logging.getLogger(__name__)


def _configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_sprint_once(notifier: SlackNotifier | None = None) -> None:
    LOGGER.info("Starting sprint orchestration run")
    try:
        run_auto_demo()
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Sprint orchestration failed: %s", exc)
        if notifier and notifier.is_configured:
            notifier.send(f"Sprint orchestration failed: {exc}")
        raise
    else:
        LOGGER.info("Sprint orchestration completed successfully")
        if notifier and notifier.is_configured:
            notifier.send("Sprint orchestration completed successfully.")


def run_loop(
    interval_minutes: float, max_runs: int | None = None, notifier: SlackNotifier | None = None
) -> None:
    run_count = 0
    while True:
        run_count += 1
        LOGGER.info("Run %s kickoff", run_count)
        try:
            run_sprint_once(notifier=notifier)
        except Exception:
            LOGGER.info("Run %s ended with errors", run_count)
        finally:
            if max_runs is not None and run_count >= max_runs:
                LOGGER.info("Reached requested run count (%s); exiting", max_runs)
                return
        LOGGER.info("Run %s finished", run_count)
        LOGGER.info("Sleeping for %.2f minutes", interval_minutes)
        time.sleep(max(0.0, interval_minutes * 60))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scheduled runner for Value Adders orchestrator")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run the orchestration one time and exit (default behaviour)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=60.0,
        help="Interval in minutes between runs when not using --once (default: 60)",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Optional limit on number of runs when looping",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Increase logging verbosity",
    )
    args = parser.parse_args()

    _configure_logging(verbose=args.verbose)
    LOGGER.info("Scheduled orchestrator starting at %s", datetime.utcnow().isoformat())
    notifier = SlackNotifier()

    if args.once:
        run_sprint_once(notifier=notifier)
    else:
        run_loop(interval_minutes=args.interval, max_runs=args.max_runs, notifier=notifier)


if __name__ == "__main__":
    main()
