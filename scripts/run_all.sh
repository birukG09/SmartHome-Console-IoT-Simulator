#!/usr/bin/env bash
set -euo pipefail

# Start Hub
( cd hub/py && python3 hub.py ) &
HUB_PID=$!
sleep 1

# Start Recorder
( python3 tools/recorder.py ) &

# Start Python Sensor
( python3 devices/python/sensor.py ) &

# Start Go Thermostat
( go run devices/go/thermostat/main.go ) &

# Start Node Lightbulb
( node devices/js/lightbulb.js ) &

# Compile + Start Java LockDevice
( cd devices/java && javac LockDevice.java && java LockDevice ) &

echo "All processes started. Hub PID=$HUB_PID"
echo "Type commands in the Hub console window. Press Ctrl+C to stop."
wait
