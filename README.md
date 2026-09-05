# Claude Code Hardware Traffic Light Indicator 🚥

A physical status indicator with LED states and audio buzzer alerts for [Claude Code](https://docs.anthropic.com/claude/docs/claude-code) and CLI coding agents powered by an ESP8266 / NodeMCU.

---

## 🌟 Visual & Audio Signals

| State | LED Color | Buzzer Pattern | Trigger |
| :--- | :--- | :--- | :--- |
| **Prompt Dispatched / Action Needed** | 🟡 Yellow | 1 Short Beep (120ms) | `UserPromptSubmit`, `PermissionRequest`, `Notification` |
| **Tool Execution** | 🔵 Blue | Silent | `PreToolUse`, `PostToolUse` (Edit, Bash, Read) |
| **Idle / Ready** | ⚫ Off | Silent | `Stop` |
| **Context Limit / Out of Tokens** | 🔴 Red | 1 Long Alarm (800ms) | Context window $\ge 95\%$ or `stop_reason == "max_tokens"` |

---

## 🛠️ Hardware Wiring

| Component | NodeMCU Pin | GPIO Pin | Notes |
| :--- | :--- | :--- | :--- |
| **🔴 Red LED** | `D1` | GPIO 5 | 220Ω–330Ω to Anode (+), Cathode to GND |
| **🟡 Yellow LED** | `D2` | GPIO 4 | 220Ω–330Ω to Anode (+), Cathode to GND |
| **🔵 Blue LED** | `D5` | GPIO 14 | 220Ω–330Ω to Anode (+), Cathode to GND |
| **🔔 Buzzer** | `D6` | GPIO 12 | Positive (+) to D6, Negative (-) to GND |

---

## 🚀 Quick Start

### 1. Prerequisites & Toolchain Setup

Install `arduino-cli`, `esptool`, and the ESP8266 board core:

```bash
# Install arduino-cli
curl -fsSL [https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh](https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh) | BINDIR=~/.local/bin sh
export PATH=$PATH:~/.local/bin

# Initialize config & add ESP8266 core
arduino-cli config init
arduino-cli config add board_manager.additional_urls [http://arduino.esp8266.com/stable/package_esp8266com_index.json](http://arduino.esp8266.com/stable/package_esp8266com_index.json)
arduino-cli core update-index
arduino-cli core install esp8266:esp8266

# Install esptool & serial tools
pip install esptool pyserial

```

---

### 2. Identify the Port & Fix Permissions

Plug your NodeMCU board into your computer and find the active serial port:

#### Linux

```bash
# List connected serial devices
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

# Or view kernel hardware detection logs
dmesg | grep -i tty

```

> **Important Linux Fixes:**
> 1. **Permission Denied:** Add your user to the `dialout` group or grant read/write permissions:
> ```bash
> sudo usermod -a -G dialout $USER
> sudo chmod 666 /dev/ttyUSB0
> 
> ```
> 
> 
> 2. **Device Auto-Disconnecting (`brltty` Conflict):** If `/dev/ttyUSB0` disappears immediately after plugging in:
> ```bash
> sudo apt remove --purge -y brltty
> 
> ```
> 
> 
> 
> 

#### Windows (PowerShell)

```powershell
# List available COM ports
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Description

```

*(Look for `Silicon Labs CP210x` or `USB-SERIAL CH340` $\rightarrow$ e.g., `COM3`).*

---

### 3. Configure, Compile & Flash the Firmware

1. Open `firmware/firmware.ino` and enter the two 2.4 GHz Wi-Fi profiles:
```cpp
WifiCredential wifiCredentials[] = {
  {"Vishwa", "YOUR_PASSWORD", IPAddress(192, 168, 0, 200), IPAddress(192, 168, 0, 1)},
  {"Gramle_Jio", "YOUR_PASSWORD", IPAddress(192, 168, 31, 200), IPAddress(192, 168, 31, 1)}
};

```

The ESP8266 tries the profiles in order. It uses `192.168.0.200` on Vishwa and `192.168.31.200` on Gramle_Jio.


2. Compile the binary:
```bash
arduino-cli compile --fqbn esp8266:esp8266:nodemcuv2 --output-dir ./build firmware/

```


3. **Put the board into Bootloader Mode:**
* Press and hold the physical **`FLASH`** (or `BOOT`) button.
* Tap the physical **`RST`** button once.
* Release the **`FLASH`** button.


4. Flash the binary:
```bash
# Linux / macOS
python3 -m esptool --port /dev/ttyUSB0 --baud 115200 --no-stub --before no-reset --after no-reset write-flash 0x0 ./build/firmware.ino.bin

# Windows (replace COM3 with your port)
python -m esptool --port COM3 --baud 115200 --no-stub --before no-reset --after no-reset write-flash 0x0 ./build/firmware.ino.bin

```



---

### 4. Monitor Serial Output

1. **Press the `RST` button** on your NodeMCU once to start the firmware.
2. Open the serial monitor:
```bash
# Linux / macOS
python3 -m serial.tools.miniterm /dev/ttyUSB0 115200

# Windows
python -m serial.tools.miniterm COM3 115200

```


3. Watch the terminal for your Wi-Fi confirmation:
```text
WiFi Connected!
Connected SSID: Vishwa
NodeMCU Fixed IP Address: 192.168.0.200

```


4. Press `Ctrl + ]` to exit the monitor.

---

### 5. Configure the Light Sender and Hooks

`hw_light.py` sends every light command to both saved ESP8266 addresses. No per-PC IP edit is needed.

| Wi-Fi | ESP8266 address |
| :--- | :--- |
| Vishwa | `192.168.0.200` |
| Gramle_Jio | `192.168.31.200` |

The computer only needs to be connected to either Wi-Fi network.

#### Linux

```bash
chmod +x /path/to/Claude_traffic/hw_light.py

# Claude Code: only copies when no settings file exists
mkdir -p ~/.claude
test -e ~/.claude/settings.json || cp settings.json.example ~/.claude/settings.json

# Codex: only copies when no hooks file exists
mkdir -p ~/.codex
test -e ~/.codex/hooks.json || cp codex-hooks.json.example ~/.codex/hooks.json
```

Replace `/media/aditya/STUDY/projects/Claude_traffic` in the example JSON if your project is in a different folder. Use `.claude/settings.json` or `.codex/hooks.json` in a repository instead when hooks should only apply to that repository. Restart Claude Code or Codex after changing its settings.

#### Windows (PowerShell)

1. Install Python 3 and check that the launcher works:

```powershell
py -3 --version
```

2. Copy this project to a stable path, such as `C:\Users\YOUR_NAME\Claude_traffic`.

3. Replace every `YOUR_NAME` in [settings.windows.json.example](settings.windows.json.example), then merge it into:

```text
C:\Users\YOUR_NAME\.claude\settings.json
```

4. Replace every `YOUR_NAME` in [codex-hooks.windows.json.example](codex-hooks.windows.json.example), then copy it to:

```text
C:\Users\YOUR_NAME\.codex\hooks.json
```

Restart Claude Code or Codex after saving. Codex may ask you to trust the hook the first time it runs.

---

### 6. Manual Testing

These tests do not require Claude Code or Codex. They send the same UDP commands that the hooks send.

### Claude Desktop on Windows (experimental)

Claude Desktop does not expose Claude Code lifecycle hooks. The included log
watcher can infer activity from local Desktop logs, but log wording can change
between Claude releases.

```powershell
# Show the Claude Desktop logs detected on this PC
py -3 .\claude_desktop_watcher.py --discover

# First test without sending anything to the hardware. Send a Claude message
# while this is running and inspect the detected colour events/log wording.
py -3 .\claude_desktop_watcher.py --dry-run --verbose

# Run the traffic-light watcher
py -3 .\claude_desktop_watcher.py
```

The watcher checks both the classic `%APPDATA%\Claude\logs` location and the
Microsoft Store/MSIX package location. If automatic discovery misses the active
log, pass it explicitly with `--log-file "C:\path\to\claude.ai-web.log"`.

#### Linux

Run these from the project directory:

```bash
# Yellow: prompt / attention needed
python3 hw_light.py UserPromptSubmit

# Blue: tool running
python3 hw_light.py PreToolUse

# Red: interrupt / context warning
python3 hw_light.py Interrupt

# Off: session complete
python3 hw_light.py Stop

# Guided sequence: Yellow -> Blue -> Off, plus manual colour selection
python3 simulate_claude.py
```

#### Windows (PowerShell)

Open PowerShell in the project directory:

```powershell
# Yellow: prompt / attention needed
py -3 .\hw_light.py UserPromptSubmit

# Blue: tool running
py -3 .\hw_light.py PreToolUse

# Red: interrupt / context warning
py -3 .\hw_light.py Interrupt

# Off: session complete
py -3 .\hw_light.py Stop

# Guided sequence: Yellow -> Blue -> Off, plus manual colour selection
py -3 .\simulate_claude.py
```

If the light does not change, confirm the PC is connected to the same Wi-Fi as the board, then ping the active address:

```bash
# Linux: use 192.168.31.200 when connected to Gramle_Jio
ping -c 1 192.168.0.200
```

```powershell
# Windows: use 192.168.31.200 when connected to Gramle_Jio
ping 192.168.0.200
```

---

### 7. Claude Desktop Setup (Manual MCP Light Controls)

Claude Desktop does not provide Claude Code lifecycle hooks. Instead, this project includes a local MCP server that gives Claude Desktop tools to control the light on request:

| Tool | Action |
| :--- | :--- |
| `light_test` | Sends yellow as a quick connectivity test |
| `light_yellow` | Turns on yellow |
| `light_blue` | Turns on blue |
| `light_red` | Turns on red |
| `light_off` | Turns all LEDs off |
| `set_light` | Accepts `yellow`, `blue`, `red`, or `off` |

You do **not** need an `.mcpb` file for this manual setup. The `.mcpb` file is only needed when using Claude Desktop's **Settings -> Extensions -> Advanced settings -> Install Extension...** flow.

The MCP server sends every command to both ESP8266 addresses:

```text
192.168.0.200
192.168.31.200
```

That means the same Claude Desktop config can work whether the computer is connected to the Vishwa Wi-Fi or the Gramle_Jio Wi-Fi.

#### Windows

1. Open PowerShell and go to the project directory:

```powershell
cd C:\Users\graml\Downloads\Claude_traffic
```

If you keep the project somewhere else, use that folder instead.

2. Install the MCP dependency:

```powershell
py -3 -m pip install -r .\claude_desktop\requirements.txt
```

3. Confirm the MCP server can start:

```powershell
py -3 .\claude_desktop\traffic_light_mcp.py
```

The command may wait silently because Claude Desktop normally talks to it over standard input/output. Press `Ctrl+C` to stop it after confirming there is no startup error.

4. Open the Claude Desktop config file:

```powershell
notepad "$env:APPDATA\Claude\claude_desktop_config.json"
```

If the file does not exist, create it.

5. Add or merge this config. If the file already has other MCP servers, only add the `esp8266-traffic-light` entry inside `mcpServers`.

```json
{
  "mcpServers": {
    "esp8266-traffic-light": {
      "command": "py",
      "args": [
        "-3",
        "C:\\Users\\graml\\Downloads\\Claude_traffic\\claude_desktop\\traffic_light_mcp.py"
      ],
      "env": {
        "ESP8266_LIGHT_IPS": "192.168.0.200,192.168.31.200"
      }
    }
  }
}
```

6. Fully quit Claude Desktop and reopen it.

7. Start a chat and ask:

```text
Use the esp8266 traffic light tool and run light_test.
```

The yellow light should turn on. Claude Desktop may ask you to approve the tool the first time.

#### macOS

1. Copy the project to your Mac and install the MCP dependency:

```bash
cd /Users/YOUR_NAME/Claude_traffic
python3 -m pip install -r claude_desktop/requirements.txt
```

2. Open or create Claude Desktop's config file:

```bash
open "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

If `open` does not create the file, make the folder and file manually:

```bash
mkdir -p "$HOME/Library/Application Support/Claude"
touch "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

3. Add or merge this config. Replace `YOUR_NAME` with your macOS user name:

```json
{
  "mcpServers": {
    "esp8266-traffic-light": {
      "command": "python3",
      "args": [
        "/Users/YOUR_NAME/Claude_traffic/claude_desktop/traffic_light_mcp.py"
      ],
      "env": {
        "ESP8266_LIGHT_IPS": "192.168.0.200,192.168.31.200"
      }
    }
  }
}
```

4. Fully quit Claude Desktop and reopen it.

5. In a chat, ask:

```text
Use the esp8266 traffic light tool and run light_test.
```

#### Linux Testing

Claude Desktop support on Linux depends on the installation channel/version. You can still test the MCP server itself from this repository:

```bash
cd /media/aditya/STUDY/projects/Claude_traffic
python3 -m pip install -r claude_desktop/requirements.txt
python3 claude_desktop/traffic_light_mcp.py
```

Press `Ctrl+C` after confirming the server starts.

Use this config shape if your Claude Desktop build exposes a local MCP config file:

```json
{
  "mcpServers": {
    "esp8266-traffic-light": {
      "command": "python3",
      "args": [
        "/media/aditya/STUDY/projects/Claude_traffic/claude_desktop/traffic_light_mcp.py"
      ],
      "env": {
        "ESP8266_LIGHT_IPS": "192.168.0.200,192.168.31.200"
      }
    }
  }
}
```

The ready-made examples are also included here:

| Platform | Example file |
| :--- | :--- |
| macOS | [claude_desktop_config.macos.example.json](claude_desktop/claude_desktop_config.macos.example.json) |
| Windows | [claude_desktop_config.windows.example.json](claude_desktop/claude_desktop_config.windows.example.json) |

#### Troubleshooting

If Claude Desktop does not show the tool, check these first:

1. Restart Claude Desktop after changing `claude_desktop_config.json`.
2. Confirm Python works from the same terminal: `py -3 --version` on Windows or `python3 --version` on macOS/Linux.
3. Confirm the MCP package is installed: `py -3 -m pip show mcp` or `python3 -m pip show mcp`.
4. Confirm the path in `args` points to the real `traffic_light_mcp.py` location.
5. Confirm the ESP8266 is on either `192.168.0.200` or `192.168.31.200`.

For automatic Claude Desktop activity detection on Windows, you can also try the experimental log watcher:

```powershell
py -3 .\claude_desktop_watcher.py --discover
py -3 .\claude_desktop_watcher.py --dry-run --verbose
py -3 .\claude_desktop_watcher.py
```
