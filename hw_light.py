#!/usr/bin/env python3
import sys
import json
import socket
import os

# The ESP8266 uses a different fixed address on each saved Wi-Fi network.
# Send to both: only the address on the currently connected LAN can receive it.
# Set ESP8266_LIGHT_IPS to a comma-separated list to override these defaults.
ESP8266_IPS = [
    address.strip()
    for address in os.getenv(
        "ESP8266_LIGHT_IPS",
        "192.168.0.200,192.168.31.200",
    ).split(",")
    if address.strip()
]
UDP_PORT = 4210

def send_udp(cmd_char):
    for esp8266_ip in ESP8266_IPS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.05)
            sock.sendto(cmd_char.encode('utf-8'), (esp8266_ip, UDP_PORT))
            sock.close()
        except OSError:
            # A packet for the inactive Wi-Fi subnet may be unroutable.
            # The address on the active subnet still receives its packet.
            pass

def read_payload():
    # Hook runners pipe a JSON payload through stdin. When manually testing in
    # a terminal, stdin is interactive and reading it would wait for Ctrl-D.
    if sys.stdin.isatty():
        return {}

    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def main():
    payload = read_payload()
    # Claude Code passes the event in the command line. Codex passes it in the
    # JSON hook payload, so the script accepts both formats.
    event_type = sys.argv[1] if len(sys.argv) >= 2 else (
        payload.get("hook_event_name")
        or payload.get("event_name")
        or payload.get("event")
        or payload.get("hookEventName")
        or ""
    )

    pct_used = payload.get("context_window", {}).get("used_percentage", 0)
    stop_reason = payload.get("stop_reason", "")
    if pct_used >= 95 or stop_reason in ["max_tokens", "token_limit_exceeded"]:
        send_udp('R')  # Red
        return

    if event_type in ["UserPromptSubmit", "PermissionRequest", "Notification"]:
        send_udp('Y')  # Yellow
    elif event_type in ["PreToolUse", "PostToolUse", "SessionStart", "SubagentStart"]:
        send_udp('B')  # Blue
    elif event_type in ["Stop", "SessionEnd", "SubagentStop"]:
        send_udp('O')  # Off
    elif event_type in ["Interrupt", "PreCompact", "PostCompact"]:
        send_udp('R')  # Red

if __name__ == "__main__":
    main()
