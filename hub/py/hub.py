#!/usr/bin/env python3
import socket, threading, os, sys, traceback
from .utils import to_json_line, parse_json_line, safe_print, ts_iso
from . import dashboard as dash

HOST = "127.0.0.1"
PORT = 5051

class Hub:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_sock = None
        self.clients = {}  # conn -> info dict
        self.devices = {}  # device_id -> state dict
        self.subscribers = {"telemetry": set(), "commands": set()}
        self.lock = threading.Lock()
        banner_path = os.path.join(os.path.dirname(__file__), "../../config/ascii_banner.txt")
        try:
            with open(os.path.abspath(banner_path), "r", encoding="utf-8") as f:
                self.banner = f.read()
        except Exception:
            self.banner = ""
        # Ensure data dir exists for logs
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
        os.makedirs(data_dir, exist_ok=True)
        self.events_log_path = os.path.join(data_dir, "events.log")

    def print_devices(self):
        with self.lock:
            for dev_id, st in self.devices.items():
                safe_print(f"{dev_id}  type={st.get('type')} last_seen={st.get('last_seen')} payload={st.get('payload')}")

    def start(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(64)
        safe_print(f"Hub listening on {self.host}:{self.port}")
        threading.Thread(target=self.accept_loop, daemon=True).start()
        # Dashboard + input threads
        hub_state = {"banner": self.banner, "devices": self.devices, "lock": self.lock}
        threading.Thread(target=dash.dashboard_loop, args=(hub_state,), daemon=True).start()
        threading.Thread(target=dash.input_loop, args=(self,), daemon=True).start()
        # Keep main thread alive
        try:
            while True:
                threading.Event().wait(3600)
        except KeyboardInterrupt:
            safe_print("\nHub shutting down...")

    def accept_loop(self):
        while True:
            try:
                conn, addr = self.server_sock.accept()
                threading.Thread(target=self.client_loop, args=(conn, addr), daemon=True).start()
            except Exception:
                traceback.print_exc()

    def log_event(self, obj):
        try:
            with open(self.events_log_path, "a", encoding="utf-8") as f:
                f.write(str(obj) + "\n")
        except Exception:
            pass

    def client_loop(self, conn, addr):
        f = conn.makefile("rwb", buffering=0)
        info = {"role": "unknown", "device_id": None, "addr": addr}
        with self.lock:
            self.clients[conn] = info
        try:
            # Expect hello first
            hello = f.readline()
            obj = parse_json_line(hello)
            if obj.get("action") != "hello":
                conn.write(to_json_line({"action":"error","error":"expected hello"}))
                conn.close()
                return
            info["role"] = obj.get("role","unknown")
            info["device_id"] = obj.get("device_id")
            info["device_type"] = obj.get("device_type")
            conn.write(to_json_line({"action":"ack","msg":"hello"}))
            with self.lock:
                if info["role"] == "device" and info["device_id"]:
                    self.devices[info["device_id"]] = {
                        "type": info.get("device_type","?"),
                        "last_seen": ts_iso(),
                        "payload": {}
                    }
            # Main loop
            while True:
                line = f.readline()
                if not line: break
                msg = parse_json_line(line)
                self.handle_message(msg, conn)
        except Exception:
            traceback.print_exc()
        finally:
            with self.lock:
                # If device disconnects, keep its last state
                self.clients.pop(conn, None)
            try:
                conn.close()
            except Exception:
                pass

    def handle_message(self, msg, conn):
        action = msg.get("action")
        if action == "subscribe":
            topics = msg.get("topics", [])
            with self.lock:
                for t in topics:
                    if t in self.subscribers:
                        self.subscribers[t].add(conn)
            return
        if action == "telemetry":
            dev_id = msg.get("device_id")
            payload = msg.get("payload", {})
            with self.lock:
                if dev_id not in self.devices:
                    self.devices[dev_id] = {"type":"?", "last_seen": ts_iso(), "payload": payload}
                else:
                    self.devices[dev_id]["last_seen"] = ts_iso()
                    self.devices[dev_id]["payload"] = payload
                subs = list(self.subscribers.get("telemetry", []))
            # Mirror telemetry to subscribers
            for s in subs:
                try:
                    s.sendall(to_json_line(msg))
                except Exception:
                    pass
            self.log_event(msg)
            return
        if action == "command":
            # Broadcast to target devices (or all)
            self.broadcast_command(msg)
            return
        # Unknown actions ignored

    def broadcast_command(self, cmd):
        # Send to all device-role connections matching target
        target = cmd.get("target")
        with self.lock:
            sinks = []
            for c, info in self.clients.items():
                if info.get("role") != "device": continue
                if target in ("all", None) or info.get("device_id") == target:
                    sinks.append(c)
            cmd_subs = list(self.subscribers.get("commands", []))
        for s in sinks + cmd_subs:
            try:
                s.sendall(to_json_line(cmd))
            except Exception:
                pass
        safe_print(f"[hub] command sent -> target={target}: {cmd}")
        self.log_event(cmd)

if __name__ == "__main__":
    Hub().start()
