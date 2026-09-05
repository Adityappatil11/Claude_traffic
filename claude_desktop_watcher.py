#!/usr/bin/env python3
"""Experimental Claude Desktop log watcher for the hardware traffic light.

Claude Desktop does not expose Claude Code lifecycle hooks. This program tails
the app's local Windows logs and maps recognizable activity to the same UDP
commands used by hw_light.py.
"""

from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path
import sys
import time

from hw_light import send_udp


POLL_SECONDS = 0.25
DEFAULT_IDLE_SECONDS = 4.0

# Log wording has changed between Claude Desktop releases. Keep these patterns
# deliberately broad and print unmatched lines in --verbose mode for tuning.
ERROR_MARKERS = (
    "[error]",
    "request failed",
    "network error",
    "err_connection_",
    "failed all attempts",
)
START_MARKERS = (
    "completion request",
    "stream started",
    "starting stream",
    "message submitted",
    "prompt submitted",
    "tool_use",
    "tool use",
)
STOP_MARKERS = (
    "stream completed",
    "stream finished",
    "completion finished",
    "response completed",
    "message completed",
)
PROMPT_MARKERS = ("message submitted", "prompt submitted", "user message")


def candidate_log_dirs() -> list[Path]:
    """Return existing Claude Desktop log directories on Windows."""
    found: list[Path] = []
    appdata = os.getenv("APPDATA")
    localappdata = os.getenv("LOCALAPPDATA")

    if appdata:
        found.extend(
            [
                Path(appdata) / "Claude" / "logs",
                Path(appdata) / "Claude-3p" / "logs",
            ]
        )

    if localappdata:
        package_pattern = str(Path(localappdata) / "Packages" / "Claude_*")
        for package in glob.glob(package_pattern):
            root = Path(package) / "LocalCache" / "Roaming"
            found.extend([root / "Claude" / "logs", root / "Claude-3p" / "logs"])

    # Resolve duplicates without requiring paths to exist.
    unique: list[Path] = []
    seen: set[str] = set()
    for path in found:
        key = str(path).casefold()
        if path.is_dir() and key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def discover_log_files() -> list[Path]:
    files: list[Path] = []
    for directory in candidate_log_dirs():
        files.extend(path for path in directory.glob("*.log") if path.is_file())
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def classify_line(line: str) -> str | None:
    """Map a log line to Y/B/R/O, or return None if it is unrelated."""
    text = line.casefold()
    if any(marker in text for marker in ERROR_MARKERS):
        return "R"
    if any(marker in text for marker in PROMPT_MARKERS):
        return "Y"
    if any(marker in text for marker in STOP_MARKERS):
        return "O"
    if any(marker in text for marker in START_MARKERS):
        return "B"
    return None


def emit(signal: str, dry_run: bool, last_signal: str | None) -> str:
    if signal == last_signal:
        return last_signal
    names = {"Y": "YELLOW", "B": "BLUE", "R": "RED", "O": "OFF"}
    print(f"[{time.strftime('%H:%M:%S')}] {names[signal]}", flush=True)
    if not dry_run:
        send_udp(signal)
    return signal


def watch(
    paths: list[Path], dry_run: bool, verbose: bool, idle_seconds: float
) -> None:
    positions: dict[Path, int] = {}
    for path in paths:
        try:
            positions[path] = path.stat().st_size
        except OSError:
            positions[path] = 0

    last_signal: str | None = None
    last_activity = 0.0
    print("Watching Claude Desktop logs. Press Ctrl+C to stop.", flush=True)
    for path in paths:
        print(f"  {path}", flush=True)

    while True:
        for path in list(positions):
            try:
                size = path.stat().st_size
                if size < positions[path]:
                    positions[path] = 0  # Log rotation/truncation.
                if size == positions[path]:
                    continue

                with path.open("r", encoding="utf-8", errors="replace") as handle:
                    handle.seek(positions[path])
                    lines = handle.readlines()
                    positions[path] = handle.tell()

                for line in lines:
                    signal = classify_line(line)
                    if signal:
                        last_signal = emit(signal, dry_run, last_signal)
                        last_activity = time.monotonic()
                    elif verbose and line.strip():
                        print(f"[{path.name}] {line.rstrip()}", flush=True)
            except (OSError, PermissionError):
                continue

        # Some versions log a start but no reliable completion marker.
        if (
            last_signal in {"Y", "B"}
            and last_activity
            and time.monotonic() - last_activity >= idle_seconds
        ):
            last_signal = emit("O", dry_run, last_signal)
            last_activity = 0.0

        time.sleep(POLL_SECONDS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-file",
        action="append",
        type=Path,
        help="Log to tail; repeat for multiple files. Auto-discovers when omitted.",
    )
    parser.add_argument(
        "--discover", action="store_true", help="List detected logs and exit."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print colours without sending UDP."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print unmatched new log lines."
    )
    parser.add_argument(
        "--idle-seconds",
        type=float,
        default=DEFAULT_IDLE_SECONDS,
        help="Turn off after this many seconds without activity (default: 4).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = args.log_file or discover_log_files()
    paths = [path.expanduser().resolve() for path in paths if path.is_file()]

    if args.discover:
        if paths:
            print("\n".join(str(path) for path in paths))
            return 0
        print("No Claude Desktop .log files were found.", file=sys.stderr)
        return 1

    if not paths:
        print(
            "No Claude Desktop logs found. Open Claude Desktop once, then run "
            "with --discover. You can also pass --log-file PATH.",
            file=sys.stderr,
        )
        return 1

    if args.idle_seconds <= 0:
        print("--idle-seconds must be greater than zero.", file=sys.stderr)
        return 2

    try:
        watch(paths, args.dry_run, args.verbose, args.idle_seconds)
    except KeyboardInterrupt:
        if not args.dry_run:
            send_udp("O")
        print("\nWatcher stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
