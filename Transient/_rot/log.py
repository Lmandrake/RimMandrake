import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/drain_log",{})
    msgs=r.get("messages") or r.get("entries") or []
    print("count", len(msgs), r.get("message"))
    for m in msgs[-40:]:
        t=(m.get("text") or m.get("message") or str(m))
        print(m.get("type") or m.get("level"), "|", t[:180].replace("\n"," "))
