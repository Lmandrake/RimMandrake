"""Is the burn line's 'burning' count after a reload a cache the next watch rebuilds, or lost state? Load pyre_walk_mid bare
(no ticks), probe, then 60 / 120 / 600 ticks."""
import sys, os, json, time
sys.path.insert(0, os.path.abspath(r"src\RimMandrake\Pyrelands")); sys.path.insert(0, os.path.abspath(r"src\RimMandrake\Utils"))
import northstar_site as NS
from northstar_driver.session import FastSession
BL = "RimMandrake.Pyrelands.MapComponent_BurnLine"; out = []
s = FastSession(strict=False)
with s:
    c = lambda tool, **kw: s.call(tool, **kw) or {}
    if NS._ui_state(s).get("programState") == "Playing":
        c("rimworld/go_to_main_menu"); NS._wait_state(s, "Entry", 300)
    c("rimworld/load_game", saveName="pyre_walk_mid"); NS._wait_state(s, "Playing", 480)
    t = time.time()
    while time.time() - t < 480:
        try:
            if c("jawa/map_info").get("tile") is not None: break
        except Exception: pass
        time.sleep(2)
    c("jawa/set_current_map", mapId=NS.find_site_map(s, 5))
    for step in (0, 60, 60, 480):
        if step: c("jawa/safe_advance", ticks=step, timeException=False)
        h = c("jawa/static_call", type=BL, method="ProbeBurnHistory", args="0").get("result")
        f = c("jawa/list_things", defName="Fire", limit=1).get("countMatched")
        out.append({"after": step, "fires": f, "hist": str(h)[:200]}); print(out[-1])
json.dump(out, open(r"Transient\pv1\walk_reload_probe.json", "w"), indent=1)
