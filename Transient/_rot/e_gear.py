import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
BARE=["Human36838","Human36841","Human36844"]; ROOF=["Human36847","Human36850","Human36853"]
HELM=["Human36856","Human36859","Human36862"]; SYM=["Human36865","Human36868","Human36871"]
with RimBridge(host, port, token) as rb:
    for p in BARE+ROOF+HELM+SYM:
        rb.call("jawa/pawn_gear", {"pawn":p,"action":"clear","clearWhat":"apparel"})
    for p in HELM:
        r = rb.call("jawa/pawn_gear", {"pawn":p,"action":"wear","def":"RUT_Apparel_ChitinSpiderHelmet"})
        print("wear", p, r.get("success"), str(r.get("message"))[:160])
    for p in SYM:
        r = rb.call("jawa/pawn_health", {"pawn":p,"action":"add","hediff":"RUT_SheenSymbiosis"})
        print("sym", p, r.get("success"), str(r.get("message"))[:160])
    # read back protection stat
    for p in BARE[:1]+HELM+SYM[:1]:
        s = rb.call("jawa/pawn_stats", {"pawn":p,"stats":"RUT_SheenProtection"})
        print("stat", p, json.dumps(s.get("stats") or s.get("rows"))[:250])
