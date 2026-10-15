"""r8 cheap read: what releases the hostiles at the calm's unfog? fresh quicktest, NO tick advance, no sweep before the unfog.
before: RectTrigger cells, hostiles listed, every Thing in a 21x21 around each trigger. unfog (jawa/set_fog unfogAll).
after: hostiles, pawn_origin (same epoch, before any save), thing_explain of one, Things in a 7x7 around each hostile."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
out = {}
def things(rb, rect):
    r = rb.call("jawa/list_things", {"rect": rect, "limit": 400})
    return {"scanned": r.get("scanned"), "matched": r.get("countMatched"),
            "things": [(x.get("def"), x.get("id"), x.get("x"), x.get("z"), x.get("faction")) for x in (r.get("things") or [])]}
def hostiles(rb):
    r = rb.call("jawa/list_pawns", {"faction": "hostile", "limit": 200})
    return [{k: x.get(k) for k in ("id", "def", "kind", "faction", "x", "z", "spawned", "dead")} for x in (r.get("pawns") or []) if not x.get("dead")]
with RimBridge(h, p, t) as rb:
    rb.call("rimworld/go_to_main_menu", {})
    rb.call("rimworld/start_debug_game_ready", {"readiness": "mapData", "pauseIfNeeded": True, "timeoutMs": 280000})
    for _ in range(480):
        if rb.call("rimworld/get_ui_state", {}).get("programState") == "Playing" and rb.call("jawa/map_info", {}).get("success"):
            break
        time.sleep(0.5)
    mi = rb.call("jawa/map_info", {})
    out["map"] = {k: mi.get(k) for k in ("tile", "mapId", "sizeX", "sizeZ", "biome")}
    out["tick0"] = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    trig = rb.call("jawa/list_things", {"defName": "RectTrigger,SignalAction_Letter,SignalAction_Ambush", "limit": 50})
    out["triggers"] = [(x.get("def"), x.get("id"), x.get("x"), x.get("z")) for x in (trig.get("things") or [])]
    out["hostiles_before"] = hostiles(rb)
    ap = rb.call("jawa/list_pawns", {"limit": 1000})
    out["all_before"] = [{k: x.get(k) for k in ("id", "def", "faction", "x", "z", "spawned", "dead")} for x in (ap.get("pawns") or [])]
    out["near_trigger_before"] = {}
    for d, i, x, z in out["triggers"]:
        if x is not None:
            out["near_trigger_before"][i] = things(rb, "%d,%d,21,21" % (x - 10, z - 10))
    fog = rb.call("jawa/set_fog", {"action": "unfogAll"})
    out["unfog"] = {k: fog.get(k) for k in ("success", "foggedBefore", "foggedNow", "changed", "error")}
    out["tick_after"] = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    hs = hostiles(rb)
    out["hostiles_after"] = hs
    ids_after = {str(x["id"]) for x in hs}
    out["hostiles_after_seen_before_as"] = [x for x in out["all_before"] if str(x["id"]) in ids_after]
    ids = ",".join(str(x["id"]) for x in hs)
    out["origin"] = rb.call("jawa/pawn_origin", {"ids": ids}) if ids else None
    out["explain"] = rb.call("jawa/thing_explain", {"id": str(hs[0]["id"])}) if hs else None
    out["near_hostiles_after"] = {}
    for x in hs[:6]:
        if x.get("x") is not None:
            out["near_hostiles_after"][str(x["id"])] = things(rb, "%d,%d,7,7" % (x["x"] - 3, x["z"] - 3))
    out["journal"] = (rb.call("jawa/incident_journal", {}).get("rows") or [])[-10:]
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print("seen before as", out["hostiles_after_seen_before_as"], "all_before n", len(out["all_before"]))
print("map", out["map"], "triggers", out["triggers"], "hostiles before", len(out["hostiles_before"]), "after", len(out["hostiles_after"]), "unfog", out["unfog"])
for x in out["hostiles_after"]: print("  ", x)
