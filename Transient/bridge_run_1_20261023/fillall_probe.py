"""fillall_probe.py -- TANK_DEBUG A1 FillAll route: run the debug action, then look for its FloatMenu in the UI layout and click a liquid."""
import sys, json, re
sys.path.insert(0, "src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
B = chr(92); TANKS = "RM_LiquidTank,RM_LiquidTankTall,RM_UniversalCargoTank,RM_UniversalCargoTankXTall"
def find(o, pred, out):
    if isinstance(o, dict):
        if pred(o): out.append(o)
        for v in o.values(): find(v, pred, out)
    elif isinstance(o, list):
        for v in o: find(v, pred, out)
    return out
with RimBridge(*resolve_endpoint()) as rb:
    c = lambda t, p=None: rb.call(t, p or {})
    c("jawa/clear_ui"); c("rimworld/pause_game"); c("rimworld/set_god_mode", {"enabled": True})
    tanks = lambda: {t["id"]: t["inspect"][0] for t in c("jawa/inspect_string", {"defName": TANKS, "limit": 100})["things"]}
    r = c("rimworld/execute_debug_action", {"path": "Actions" + B + "Tanks: fill ALL on map to max (pick liquid)"})
    print("act", json.dumps({k: v for k, v in r.items() if k not in ("operation", "state")})[:500])
    lay = c("rimworld/get_ui_layout")
    print("surfaces", [s.get("type") for s in lay.get("surfaces", [])])
    labs = find(lay, lambda o: o.get("targetId") and o.get("label"), [])
    brine = [o for o in labs if "brine" in o["label"].lower()]
    print("labels", [o["label"] for o in labs][:40])
    m = c("rimworld/get_context_menu_options"); print("menu", m.get("optionCount"), [x["label"] for x in m.get("options", [])][:5])
    pick = None
    if m.get("options"):
        pick = [x["label"] for x in m["options"] if "brine" in x["label"].lower()][0]
        print("exec", json.dumps(c("rimworld/execute_context_menu_option", {"label": pick}))[:200])
    elif brine:
        pick = brine[0]["label"]; print("click", json.dumps(c("rimworld/click_ui_target", {"targetId": brine[0]["targetId"]}))[:200])
    f = tanks(); full = [k for k, v in f.items() if (m_ := re.match(r"Holding: (.+) \((\S+) kL / (\S+) kL\)", v)) and m_.group(2) == m_.group(3) and "brine" in m_.group(1).lower()]
    print("RESULT pick=%r full_of_brine=%d/%d sample=%r" % (pick, len(full), len(f), list(f.values())[:2]))
    c("rimworld/execute_debug_action", {"path": "Actions" + B + "Tanks: empty ALL on map"})
    e = tanks(); print("EMPTY", sum(v == "Empty" for v in e.values()), len(e))
    c("jawa/clear_ui"); c("rimworld/set_god_mode", {"enabled": False}); c("rimworld/pause_game")
