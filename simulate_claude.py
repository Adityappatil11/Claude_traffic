#!/usr/bin/env python3
import subprocess
import json
import time
import sys

def run_hook(event_name, payload):
    try:
        proc = subprocess.Popen(
            [sys.executable, "hw_light.py", event_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        proc.communicate(input=json.dumps(payload))
    except Exception as e:
        print(f"Hook dispatch error: {e}")

def simulate_turn():
    print("\n[User Prompt]: 'Refactor authentication module'")
    print(" -> YELLOW (Waiting for Claude response...)")
    run_hook("UserPromptSubmit", {"prompt": "Refactor auth"})
    time.sleep(2.5)

    print(" -> BLUE (Claude running tools/editing files...)")
    run_hook("PreToolUse", {"tool_name": "Edit", "file": "auth.py"})
    time.sleep(3.5)

    print(" -> OFF (Turn complete)\n")
    run_hook("Stop", {})

def simulate_tokens_exhausted():
    print("\n[Out of Tokens Simulation]")
    print(" -> RED (Context limit reached: stop_reason = max_tokens)\n")
    run_hook("Stop", {
        "stop_reason": "max_tokens",
        "context_window": {"used_percentage": 98}
    })

def main():
    while True:
        print("==========================================")
        print("  CLAUDE TRAFFIC LIGHT TESTER")
        print("==========================================")
        print("1. Test standard run (Yellow -> Blue -> Off)")
        print("2. Test Out of Tokens error (Red)")
        print("3. Manual send (Y, B, R, O)")
        print("q. Exit")
        
        choice = input("\nSelect [1-3, q]: ").strip()
        if choice == "1":
            simulate_turn()
        elif choice == "2":
            simulate_tokens_exhausted()
        elif choice == "3":
            val = input("Enter signal (Y/B/R/O): ").strip().upper()
            if val in ['Y', 'B', 'R', 'O']:
                from hw_light import send_udp
                send_udp(val)
                print(f"Sent: {val}")
        elif choice.lower() == "q":
            break

if __name__ == "__main__":
    main()