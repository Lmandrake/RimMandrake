"""Visit 2: the opening front's old-save read (P_opening_front / opening_front_old_save_inert) on a save made BEFORE the
opening front shipped (05033a3f7, 2026-10-22). The visit-2 site was born after it, so its own read is UNMEASURED (SITE).
python.exe, bridge held. Main menu, load NS_Pyrelands_site_1_417df172fdb5_calm (2026-10-15), await map_ready, read
MapComponent_BurnLine.ProbeOpeningFront, advance one opening window (2500 ticks), read again. Both readings go to
evidence/old_save_read.json; validation.old_save_opening_verdict judges them offline (python3)."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
from await_lifecycle import await_lifecycle
SAVE = sys.argv[1] if len(sys.argv) > 1 else "NS_Pyrelands_site_1_417df172fdb5_calm"
BURN_LINE = "RimMandrake.Pyrelands.MapComponent_BurnLine"
h, p, tk = resolve_endpoint()
out = {"save": SAVE}
with RimBridge(h, p, tk) as rb:
    call = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    try:
        call("rimworld/go_to_main_menu")
    except Exception as e:  # noqa: BLE001 - the menu wait judges it
        out["menu_err"] = str(e)[:200]
    out["menu"] = bool(await_lifecycle(call, "menu", 180.0))
    out["load"] = {k: v for k, v in (call("rimworld/load_game", saveName=SAVE) or {}).items() if k in ("success", "message")}
    if out["load"].get("success") is False:   # e.g. the save names mods this list lacks: no map will come
        print(json.dumps(out, indent=1, default=str)); print("UNMEASURED: the load was refused")
        json.dump(out, open(r"design\concepts\Pyrelands\version\in_game\visit_2\evidence\old_save_read.json", "w"), indent=1, default=str)
        sys.exit(2)
    out["ready"] = bool(await_lifecycle(call, "map_ready", 1800.0))
    call("rimworld/set_time_speed", speed=0)
    mi = call("jawa/map_info")
    out["map"] = {k: mi.get(k) for k in ("tile", "biome", "mapBiome", "ticksGame", "mapId") if k in mi}
    out["before"] = call("jawa/static_call", type=BURN_LINE, method="ProbeOpeningFront").get("result")
    left = 2600
    while left > 0:
        r = call("jawa/safe_advance", ticks=min(left, 1300), timeException=False)
        left -= int(r.get("executed") or 0) or 1300
        if r.get("state") == "stopped":
            out["advance_stopped"] = json.dumps(r)[:300]; break
    out["after"] = call("jawa/static_call", type=BURN_LINE, method="ProbeOpeningFront").get("result")
    f = call("jawa/list_things", defName="Fire", limit=1)
    out["fires"] = {"countMatched": f.get("countMatched"), "scanned": f.get("scanned")}
print(json.dumps(out, indent=1, default=str)[:3000])
json.dump(out, open(r"design\concepts\Pyrelands\version\in_game\visit_2\evidence\old_save_read.json", "w"), indent=1, default=str)
