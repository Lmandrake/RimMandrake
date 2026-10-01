"""One bridge call from the shell: python.exe Transient\\live_verify_batch_2026-09-30\\bcall.py <tool> '<json params>'
Run from the repo root under Windows python.exe. Prints the decoded result JSON."""
import json
import sys

sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb

tool = sys.argv[1]
params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()
r = S.call(tool, params) or {}
if isinstance(r, dict) and r.get("content"):
    try:
        r = json.loads(r["content"][0]["text"])
    except Exception:
        pass
print(json.dumps(r, indent=1)[: int(sys.argv[3]) if len(sys.argv) > 3 else 6000])
