import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/drain_log",{})   # clear
    rb.call("jawa/spawn_batch",{"ops":"RUT_RegenerantVeil:120,138,1;RUT_AgelessCap:122,138,1;RUT_FalseFruit:124,138,1"})
    t=rb.call("jawa/list_things",{"rect":"119,137,8,3"})
    print("spawned:", [(q["id"],q.get("className")) for q in t.get("things",[])])
    r=rb.call("jawa/drain_log",{})
    msgs=r.get("messages") or r.get("entries") or []
    print("NEW LOG LINES:", len(msgs))
    for m in msgs:
        print(" ", m.get("type"), "|", (m.get("text") or "")[:200].replace("\n"," "))
