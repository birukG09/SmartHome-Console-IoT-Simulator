from .utils import CLEAR, BOLD, RESET, safe_print, ts_iso
import threading, time, json, sys

def render_table(rows):
    # rows: list of dicts with keys: id, type, last_seen, summary
    cols = ["ID","TYPE","LAST SEEN","SUMMARY"]
    widths = [20,14,19,40]
    def fmt_cell(s, w):
        t = str(s)
        return (t[:w-1] + "…") if len(t) > w else t.ljust(w)
    header = " ".join(fmt_cell(c, w) for c,w in zip(cols, widths))
    sep = "-"*len(header)
    lines = [header, sep]
    for r in rows:
        line = " ".join([
            fmt_cell(r.get("id",""), widths[0]),
            fmt_cell(r.get("type",""), widths[1]),
            fmt_cell(r.get("last_seen",""), widths[2]),
            fmt_cell(r.get("summary",""), widths[3]),
        ])
        lines.append(line)
    return "\n".join(lines)

def summarize_payload(payload):
    if not isinstance(payload, dict): return ""
    # Make a short "k=v" string
    parts = []
    for k, v in list(payload.items())[:6]:
        parts.append(f"{k}={v}")
    return ", ".join(parts)

def dashboard_loop(hub_state):
    # hub_state provides: banner, devices (dict), lock (threading.Lock)
    banner = hub_state["banner"]
    devices = hub_state["devices"]
    lock = hub_state["lock"]
    while True:
        time.sleep(1.0)
        with lock:
            rows = []
            for dev_id, state in devices.items():
                rows.append({
                    "id": dev_id,
                    "type": state.get("type","?"),
                    "last_seen": state.get("last_seen","?"),
                    "summary": summarize_payload(state.get("payload",{}))
                })
        safe_print(CLEAR + banner)
        safe_print(f"{BOLD}SmartHome Hub — {ts_iso()}{RESET}")
        safe_print(render_table(sorted(rows, key=lambda r: r["id"])))
        safe_print("\nCommands: 'help', 'list', or 'cmd <JSON>' e.g. cmd {\"action\":\"command\",\"target\":\"all\",\"name\":\"ping\"}")

def input_loop(hub):
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line: continue
        if line == "help":
            print("Type: list | cmd <json>")
        elif line == "list":
            hub.print_devices()
        elif line.startswith("cmd "):
            raw = line[4:].strip()
            try:
                obj = json.loads(raw)
                if obj.get("action") != "command":
                    print("JSON must contain action=command")
                else:
                    hub.broadcast_command(obj)
            except Exception as e:
                print("Invalid JSON:", e)
        else:
            print("Unknown command. Try 'help'.")
