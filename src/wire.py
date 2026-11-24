"""Optional wire log: set WIRE_DIR and every model request and MCP message is appended there.
Off by default. The lecture's wire figures are read from these files."""
import json, os, threading

_lock = threading.Lock()


def log(channel, record):
    folder = os.environ.get("WIRE_DIR")
    if not folder:
        return
    os.makedirs(folder, exist_ok=True)
    with _lock, open(os.path.join(folder, f"{channel}.jsonl"), "a") as f:
        f.write(json.dumps(record) + "\n")
