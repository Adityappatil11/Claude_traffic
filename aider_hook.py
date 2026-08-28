#!/usr/bin/env python3
import socket
import sys

ESP32_IP = "192.168.X.XXX"
UDP_PORT = 4210

def send_udp(cmd_char):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.05)
        sock.sendto(cmd_char.encode('utf-8'), (ESP32_IP, UDP_PORT))
    except Exception:
        pass

if __name__ == "__main__":
    # Aider needs human input or finished the turn -> 🟡 Yellow + Short Beep
    send_udp('Y')
