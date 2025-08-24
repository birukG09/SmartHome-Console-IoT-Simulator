#!/usr/bin/env python3
# Optional: visualize telemetry history from telemetry.csv using matplotlib.
# Not required for the simulator to run.
import csv, json, sys
from collections import defaultdict
import matplotlib.pyplot as plt

def load(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            row["ts"] = int(row["ts"])
            row["payload"] = json.loads(row["payload_json"])
            rows.append(row)
    return rows

def main():
    path = sys.argv[1] if len(sys.argv)>1 else "data/telemetry.csv"
    rows = load(path)
    series = defaultdict(list)  # (device_id, key) -> [(ts, value)]
    for r in rows:
        dev = r["device_id"]
        for k, v in r["payload"].items():
            if isinstance(v, (int, float)):
                series[(dev, k)].append((r["ts"], float(v)))

    for (dev, key), pts in series.items():
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        plt.figure()
        plt.plot(xs, ys)
        plt.title(f"{dev} — {key}")
        plt.xlabel("ts (ms)")
        plt.ylabel(key)
    plt.show()

if __name__ == "__main__":
    main()
