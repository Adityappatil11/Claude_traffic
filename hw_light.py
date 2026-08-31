#!/usr/bin/env python3
import sys
import json
import socket
import os

# Put the IP printed in your Serial Monitor here:
ESP32_IP = os.getenv("CLAUDE_LIGHT_IP", "192.168.0.16")
UDP_PORT = 4210

def send_udp(cmd_char):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.05)
        sock.sendto(cmd_char.encode('utf-8'), (ESP32_IP, UDP_PORT))
    except Exception:
        pass

def main():
    if len(sys.argv) < 2:
        return

    event_type = sys.argv[1]

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    pct_used = payload.get("context_window", {}).get("used_percentage", 0)
    stop_reason = payload.get("stop_reason", "")
    if pct_used >= 95 or stop_reason in ["max_tokens", "token_limit_exceeded"]:
        send_udp('R')  # Red
        return

    if event_type == "UserPromptSubmit":
        send_udp('Y')  # Yellow
    elif event_type in ["PreToolUse", "PostToolUse"]:
        send_udp('B')  # Blue
    elif event_type == "Stop":
        send_udp('O')  # Off
    elif event_type == "Notification":
        send_udp('Y')  # Yellow

if __name__ == "__main__":
    main()