import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
want = sys.argv[1].split(",")
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        if t["name"] in want:
            print("="*70); print(t["name"]); print(t.get("description","")[:1400])
            print("-- params:", json.dumps(t.get("inputSchema") or t.get("input_schema") or {})[:2200])
