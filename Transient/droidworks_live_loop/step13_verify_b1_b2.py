import sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    rb.call("jawa/clear_ui", {})
    # B2: spawn a few KotOR kinds, check apparel
    print("=== B2: module absorb — spawn KotOR kinds, check apparel ===")
    for i, kind in enumerate(["RSW_DW_KotORDroidBad_KM1HMD", "RSW_DW_KotORDroidBad_ADMkI", "RSW_DW_KotORDroidColonist_KM1MD"]):
        r = rb.call("rimworld/execute_debug_action", {
            "path": f"Actions\\Spawn Pawn...\\{kind}", "x": 100 + i * 3, "z": 100})
        print("spawn", kind, r.get("success"), r.get("message"))
    time.sleep(1)
    lp = rb.call("jawa/list_pawns", {})
    kinds_wanted = {"RSW_DW_KotORDroidBad_KM1HMD", "RSW_DW_KotORDroidBad_ADMkI", "RSW_DW_KotORDroidColonist_KM1MD"}
    ids = [p["id"] for p in lp.get("pawns", []) if p.get("kind") in kinds_wanted]
    print("ids:", ids)
    for pid in ids:
        g = rb.call("jawa/pawn_get", {"pawn": pid})
        p = g.get("pawns", [{}])[0]
        apparel = p.get("apparel", [])
        module_apparel = [a for a in apparel if "RSW_DW_Module" in str(a)]
        print(pid, p.get("kindDef"), "apparel:", json.dumps(apparel)[:600])
        print("  RSW_DW_Module_* worn:", module_apparel)

    # B1: format tier — set hediff at different severities, read needs back
    print("=== B1: format tiers — need gating by stage ===")
    r = rb.call("rimworld/execute_debug_action", {
        "path": "Actions\\Spawn Pawn...\\RSW_DW_KotORDroidColonist_ADMkI", "x": 115, "z": 100})
    print("spawn format-test subject", r.get("success"))
    time.sleep(0.5)
    lp2 = rb.call("jawa/list_pawns", {})
    ftid = sorted([p["id"] for p in lp2.get("pawns", []) if p.get("kind") == "RSW_DW_KotORDroidColonist_ADMkI"],
                  key=lambda i: int(''.join(filter(str.isdigit, i))))[-1]
    print("format test pawn:", ftid)

    g0 = rb.call("jawa/pawn_get", {"pawn": ftid})
    print("default needs:", [n.get("def") for n in g0.get("pawns", [{}])[0].get("needs", [])])
    print("default hediffs:", g0.get("pawns", [{}])[0].get("hediffs"))

    for severity, label in [(0.9, "blank/mindless (low)"), (2.0, "programmable"), (3.5, "sapient")]:
        rb.call("jawa/pawn_health", {"pawn": ftid, "action": "remove", "hediff": "RSW_DW_FormatTier"})
        r = rb.call("jawa/pawn_health", {"pawn": ftid, "action": "add", "hediff": "RSW_DW_FormatTier", "severity": severity})
        print(f"--- severity {severity} ({label}) ---", r.get("success"), r.get("didWhat"))
        g = rb.call("jawa/pawn_get", {"pawn": ftid})
        p = g.get("pawns", [{}])[0]
        needs = [n.get("def") for n in p.get("needs", [])]
        print("  needs present:", needs)
        print("  hediffs:", p.get("hediffs"))
