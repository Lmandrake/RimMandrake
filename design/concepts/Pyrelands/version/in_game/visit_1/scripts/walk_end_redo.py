"""sc_walk's switch + log clause, redone on pyre_walk_end with a SENTINEL log window (the count window was blind at the
1000-line cap). Then a canary window with one deliberate Log.Error proves the filter sees an error."""
import sys, os, json, time
sys.path.insert(0, os.path.abspath(r"src\RimMandrake\Pyrelands")); sys.path.insert(0, os.path.abspath(r"src\RimMandrake\Utils"))
import northstar_site as NS
from northstar_driver.session import FastSession
S = "RimMandrake.Pyrelands.RM_PyrelandsSettings"; out = {}
s = FastSession(strict=False)
with s:
    c = lambda tool, **kw: s.call(tool, **kw) or {}
    if NS._ui_state(s).get("programState") == "Playing":
        c("rimworld/go_to_main_menu"); NS._wait_state(s, "Entry", 300)
    c("rimworld/load_game", saveName="pyre_walk_end"); NS._wait_state(s, "Playing", 480)
    t = time.time()
    while time.time() - t < 480:
        try:
            if c("jawa/map_info").get("tile") is not None: break
        except Exception: pass
        time.sleep(2)
    c("jawa/set_current_map", mapId=NS.find_site_map(s, 5))
    c("jawa/static_call", type="Verse.Log", method="Clear")      # validation_core.log_revive: reset the 10,000-message cap
    def window(do):
        tok = "pyre log mark %d" % int(time.time() * 1000)
        c("jawa/static_call", type="Verse.Log", method="Warning", args=tok)
        do()
        msgs = c("jawa/drain_log", limit=1000).get("messages") or []
        at = [i for i, m in enumerate(msgs) if tok in str(m.get("text", ""))]
        if not at: return None
        return msgs[at[-1] + 1:]
    out["fruit_end"] = c("jawa/list_things", defName="RM_FE_Plant_ScorchFruit", limit=1).get("countMatched")
    def switch():
        prior = c("jawa/mod_settings_field", typeName=S, action="get", field="pyrelandsEnabled").get("value")
        c("jawa/mod_settings_field", typeName=S, action="set", field="pyrelandsEnabled", value="False")
        c("jawa/map_fire", action="extinguish", rect="0,0,250,250")
        c("jawa/safe_advance", ticks=2500, timeException=False)
        out["fires_off"] = c("jawa/list_things", defName="Fire", limit=1).get("countMatched")
        c("jawa/mod_settings_field", typeName=S, action="set", field="pyrelandsEnabled", value=str(prior))
        c("jawa/safe_advance", ticks=2500, timeException=False)
    w = window(switch)
    out["window_lines"] = None if w is None else len(w)
    out["errors"] = None if w is None else [m.get("text", "")[:200] for m in w if str(m.get("type", "")).lower() in ("error", "exception")]
    out["warnings"] = None if w is None else [m.get("text", "")[:160] for m in w if str(m.get("type", "")).lower() == "warning"][:5]
    cw = window(lambda: c("jawa/static_call", type="Verse.Log", method="Error", args="visit1 canary error"))
    out["canary_errors"] = None if cw is None else [m.get("text", "")[:80] for m in cw if str(m.get("type", "")).lower() == "error"]
    print(json.dumps(out)[:1500])
json.dump(out, open(r"Transient\pv1\walk_end_redo.json", "w"), indent=1)
