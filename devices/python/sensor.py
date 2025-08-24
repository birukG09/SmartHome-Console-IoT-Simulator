#!/usr/bin/env python3
import socket, json, time, random, os, sys

HOST, PORT = "127.0.0.1", 5051
DEVICE_ID = "py-env-1"

def send(sock, obj):
    sock.write((json.dumps(obj, separators=(",",":"))+"\n").encode("utf-8"))
    sock.flush()

def main():
    conn = socket.create_connection((HOST, PORT))
    sock = conn.makefile("rwb", buffering=0)
    hello = {"action":"hello","role":"device","device_id":DEVICE_ID,"device_type":"env-sensor","capabilities":["temperature","humidity","battery"]}
    send(sock, hello)
    sock.readline()  # ack
    temp = 23.5
    hum = 42.0
    battery = 100
    last = 0
    while True:
        time.sleep(0.5)
        temp += (random.random()-0.5)*0.1
        hum += (random.random()-0.5)*0.3
        battery = max(0, battery - (0.01 if random.random()<0.2 else 0))
        now = time.time()
        if now - last > 2.0:
            payload = {"temperature": round(temp,1), "humidity": round(hum,1), "battery": round(battery,1)}
            tel = {"action":"telemetry","device_id":DEVICE_ID,"payload":payload}
            send(sock, tel)
            last = now

if __name__ == "__main__":
    main()
