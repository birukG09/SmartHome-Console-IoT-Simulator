# SmartHome-Console-IoT-Simulator

A cross-language, console-first IoT smart‑home simulator. It uses a lightweight,
newline-delimited JSON (NDJSON) protocol over TCP so devices written in different
languages (Python, Go, Node.js, Java) can talk to a central **Hub**.

- **Focus**: simple console UX + ASCII dashboard, zero external deps.
- **IPC**: plain TCP on `127.0.0.1:5051` with NDJSON messages.
- **Devices**: Python Sensor, Go Thermostat, Node.js Lightbulb, Java Door  Lock.
- **Recorder**: Python client that subscribes to telemetry and writes CSV logs.
- **Exactly 20 files**: project kept lean for clarity and portability.

## Quick Start

### Linux/macOS (Bash)
```bash
cd SmartHome-Console-IoT-Simulator
bash scripts/run_all.sh
# The hub starts first with a dashboard.
# Devices will connect and send telemetry every ~2–3s.
# Type `help` in the hub console for commands.
```

### Windows (PowerShell)
```powershell
cd SmartHome-Console-IoT-Simulator
./scripts/run_all.ps1
```

> Requirements: Python 3.9+, Go 1.20+, Node.js 18+, Java 11+.
> No extra libraries are needed; everything uses standard libraries.

## Architecture

```
+---------------------+           TCP:5051 NDJSON           +------------------------+
|  devices/python     |  --->  [ Hub (Python) ]  <---  |  devices/js (Node)       |
|  env sensor         |          - registry               |  lightbulb              |
|                     |          - router (commands)      |                         |
+---------------------+          - telemetry mirror        +------------------------+
         ^                        - ASCII dashboard                 ^
         |                                                       +--+--+
         |                                                       |     |
         |                                                devices/go  devices/java
         |                                                thermostat   door lock
         v
 +--------------------+
 | tools/recorder     |  (subscribes to telemetry and writes CSV)
 +--------------------+
```

### Protocol (NDJSON over TCP)
Each message is one JSON object per line (`\n` terminated). UTF-8 text. Minimal schema:

- **Hello** (first message from any client):
```json
{"action":"hello","role":"device|recorder|dashboard","device_id":"id-1","device_type":"lightbulb","capabilities":["on","brightness"]}
```
- **Telemetry** (from devices to hub):
```json
{"action":"telemetry","device_id":"id-1","payload":{"on":true,"brightness":80}}
```
- **Subscribe** (recorder asks hub to mirror telemetry):
```json
{"action":"subscribe","topics":["telemetry"]}
```
- **Command** (sent by hub to devices or by a dashboard user typing `cmd <json>`):
```json
{"action":"command","target":"id-1","name":"set_brightness","params":{"value":30}}
```
Targets may also be `"all"`.

## Files (20 total)
```
1  README.md
2  LICENSE
3  .gitignore
4  config/devices.yaml
5  config/ascii_banner.txt
6  protocol.md
7  hub/py/hub.py
8  hub/py/dashboard.py
9  hub/py/utils.py
10 devices/go/thermostat/main.go
11 devices/js/lightbulb.js
12 devices/java/LockDevice.java
13 tools/recorder.py
14 tools/plot_history.py
15 scripts/run_all.sh
16 scripts/run_all.ps1
17 hub/py/requirements.txt
18 data/sample_commands.jsonl
19 tests/protocol_test.py
20 devices/python/sensor.py
```

## Running commands
Inside the hub console, type:
- `help` — show help
- `list` — list devices
- `cmd {"action":"command","target":"all","name":"ping"}` — broadcast JSON command

## Notes
- The hub logs telemetry to stdout and mirrors it to any client subscribed to `telemetry` (e.g., `tools/recorder.py`).
- The dashboard auto-refreshes every second and renders an ASCII table of registered devices and latest readings.
- Everything is pure standard library code across languages.
