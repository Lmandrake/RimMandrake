import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
ftid = "RSW_DW_Race_guy762_DroidRace_ADMkI53446"
with RimBridge(host, port, token) as rb:
    for severity, label in [(0.5, "blank"), (1.5, "mindless"), (2.5, "programmable"), (3.9, "sapient")]:
        rb.call("jawa/pawn_health", {"pawn": ftid, "action": "remove", "hediff": "RSW_DW_FormatTier"})
        r = rb.call("jawa/pawn_health", {"pawn": ftid, "action": "add", "hediff": "RSW_DW_FormatTier", "severity": severity})
        g = rb.call("jawa/pawn_get", {"pawn": ftid})
        p = g.get("pawns", [{}])[0]
        needs = [n.get("need") for n in p.get("needs", [])]
        hd = [h for h in p.get("hediffs", []) if h["def"] == "RSW_DW_FormatTier"]
        print(f"severity {severity} ({label}): hediff={hd} needs={needs}")
