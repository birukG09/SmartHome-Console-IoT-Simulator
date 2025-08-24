# SmartHome NDJSON Protocol (v0.1)

**Transport**: TCP. **Encoding**: UTF-8. **Framing**: NDJSON (one JSON object per line).

## Message Types

### `hello`
Sent first by all clients.
```json
{"action":"hello","role":"device|recorder|dashboard","device_id":"<id>","device_type":"<type>","capabilities":["..."]}
```

### `telemetry`
Sent by devices to the hub.
```json
{"action":"telemetry","device_id":"<id>","payload":{"k":"v"}}
```

### `subscribe`
Recorder/observer indicates topics it wants to mirror.
```json
{"action":"subscribe","topics":["telemetry","commands"]}
```

### `command`
Sent by hub (or typed via dashboard) to devices.
```json
{"action":"command","target":"<id>|all","name":"<verb>","params":{"k":"v"}}
```
