import json, time, sys, threading, os

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CLEAR = "\033[2J\033[H"

def now_ms() -> int:
    return int(time.time() * 1000)

def ts_iso() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def to_json_line(obj: dict) -> bytes:
    return (json.dumps(obj, separators=(",", ":")) + "\n").encode("utf-8")

def parse_json_line(line: bytes):
    try:
        return json.loads(line.decode("utf-8").strip())
    except Exception as e:
        return {"action":"error","error":str(e)}

def safe_print(*args, **kwargs):
    # Single-threaded stdout write
    text = " ".join(str(a) for a in args)
    sys.stdout.write(text + ("" if text.endswith("\n") else "\n"))
    sys.stdout.flush()
