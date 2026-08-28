#!/usr/bin/env python3
import os
import sys
import pty
import select
import socket

ESP32_IP = "192.168.0.5"
UDP_PORT = 4210

def send_udp(cmd_char):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.05)
        sock.sendto(cmd_char.encode('utf-8'), (ESP32_IP, UDP_PORT))
    except Exception:
        pass

def main():
    send_udp('O')

    args = sys.argv[1:]
    if not any(arg.startswith("--model") for arg in args):
        # Using Google Studio compatible Gemini model identifier
        args = ["--model", "gemini/gemini-3.6-flash"] + args

    cmd = ["aider"] + args

    # Spawn Aider in a master-slave pseudo-terminal to monitor terminal state
    master, slave = pty.openpty()
    pid = os.fork()

    if pid == 0:
        # Child process: Run Aider attached to the PTY
        os.close(master)
        os.dup2(slave, 0)
        os.dup2(slave, 1)
        os.dup2(slave, 2)
        os.close(slave)
        os.execvp("aider", cmd)
    else:
        # Parent process: Bridge input/output and update hardware light states
        os.close(slave)
        try:
            while True:
                r, _, _ = select.select([sys.stdin, master], [], [])

                # User typed something and submitted -> 🟡 Yellow + Short Beep
                if sys.stdin in r:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if not data:
                        break
                    if b'\n' in data or b'\r' in data:
                        send_udp('Y')
                    os.write(master, data)

                # Aider output received
                if master in r:
                    try:
                        data = os.read(master, 1024)
                        if not data:
                            break
                        
                        text = data.decode(errors='ignore')

                        # Prompt ready or waiting for user confirmation -> 🟡 Yellow
                        if "> " in text or "[y/n]" in text:
                            send_udp('Y')
                        # Active token generation or tool editing -> 🔵 Blue
                        elif len(data) > 0 and not ("> " in text or "[y/n]" in text):
                            send_udp('B')

                        os.write(sys.stdout.fileno(), data)
                        sys.stdout.flush()
                    except OSError:
                        break

            _, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
                send_udp('R')
            else:
                send_udp('O')

        except (KeyboardInterrupt, Exception):
            send_udp('O')
        finally:
            send_udp('O')
            try:
                os.close(master)
            except Exception:
                pass

if __name__ == "__main__":
    main()
