#!/usr/bin/env python3
import socket, json, csv, time, os, sys

HOST, PORT = "127.0.0.1", 5051

def main():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/telemetry.csv"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = open(path, "a", newline="", encoding="utf-8")
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow(["ts","device_id","payload_json"])

    conn = socket.create_connection((HOST, PORT))
    sock = conn.makefile("rwb", buffering=0)
    hello = {"action":"hello","role":"recorder","device_id":"rec-1","device_type":"recorder"}
    sock.write((json.dumps(hello)+"\n").encode("utf-8"))
    sock.flush()
    sock.readline()  # ack
    sub = {"action":"subscribe","topics":["telemetry"]}
    sock.write((json.dumps(sub)+"\n").encode("utf-8"))
    sock.flush()

    print("[recorder] writing to", path)
    try:
        while True:
            line = sock.readline()
            if not line: break
            try:
                obj = json.loads(line.decode("utf-8").strip())
                if obj.get("action") == "telemetry":
                    writer.writerow([int(time.time()*1000), obj.get("device_id"), json.dumps(obj.get("payload",{}), separators=(",",":"))])
                    f.flush()
            except Exception:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        f.close()

if __name__ == "__main__":
    main()
