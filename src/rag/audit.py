import json
from pathlib import Path

LOG_FILE = Path("audit_logs.jsonl")

def audit_node(state):
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(state.__dict__) + "\n")
    return state
