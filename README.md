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

### 3. Compile & Flash the Firmware

1. Open `firmware/firmware.ino` and enter your 2.4 GHz Wi-Fi credentials:
```cpp
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

```


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

### 4. Monitor Serial Output & Get Board IP

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
NodeMCU IP Address: 192.168.0.5

```


4. Press `Ctrl + ]` to exit the monitor.

---

### 5. Configure Claude Code Hooks

1. Open `hw_light.py` and set your NodeMCU's assigned IP:
```python
ESP32_IP = "192.168.0.5"

```


2. Make the hook script executable:
```bash
chmod +x hw_light.py

```


3. Copy the example configuration to your Claude settings:
```bash
mkdir -p ~/.claude
cp settings.json.example ~/.claude/settings.json

```


*(Update `/path/to/Claude_traffic/hw_light.py` inside `~/.claude/settings.json` with the absolute path to your script).*

---

### 6. Testing

* **Hardware Testbench (No Claude required):**
```bash
python3 simulate_claude.py

```


* **With Aider (Open Source coding assistant):**
```bash
./aider_light.py
