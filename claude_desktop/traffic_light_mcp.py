#!/usr/bin/env python3
"""Local MCP server that controls the ESP8266 traffic light for Claude Desktop."""

import os
import socket
from typing import Literal

from mcp.server.fastmcp import FastMCP


LIGHT_IPS = tuple(
    address.strip()
    for address in os.getenv(
        "ESP8266_LIGHT_IPS", "192.168.0.200,192.168.31.200"
    ).split(",")
    if address.strip()
)
UDP_PORT = 4210

mcp = FastMCP("ESP8266 Traffic Light")


def send_light_command(command: str) -> str:
    """Send a command to both saved networks; the inactive network is ignored."""
    sent_to = []
    for address in LIGHT_IPS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(command.encode("ascii"), (address, UDP_PORT))
            sent_to.append(address)
        except OSError:
            pass
    return f"Sent {command} to {', '.join(sent_to) or 'no reachable address'} on UDP {UDP_PORT}."


@mcp.tool()
def set_light(color: Literal["yellow", "blue", "red", "off"]) -> str:
    """Set the physical traffic light colour. Use off when the task is complete."""
    commands = {"yellow": "Y", "blue": "B", "red": "R", "off": "O"}
    return send_light_command(commands[color])


@mcp.tool()
def light_yellow() -> str:
    """Set the physical traffic light to yellow for attention or a new prompt."""
    return send_light_command("Y")


@mcp.tool()
def light_blue() -> str:
    """Set the physical traffic light to blue while work is in progress."""
    return send_light_command("B")


@mcp.tool()
def light_red() -> str:
    """Set the physical traffic light to red for a warning or blocked task."""
    return send_light_command("R")


@mcp.tool()
def light_off() -> str:
    """Turn all physical traffic-light LEDs off."""
    return send_light_command("O")


@mcp.tool()
def light_test() -> str:
    """Send a yellow test command to verify the current Wi-Fi connection."""
    return send_light_command("Y")


if __name__ == "__main__":
    mcp.run(transport="stdio")
