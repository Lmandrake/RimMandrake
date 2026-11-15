"""sc_walk, resumable: the walk_season chain's own steps on the FULL list (save pre, WALK_DAYS, save mid, digest, reload mid,
digest, reload pre, digest, reload mid; WALK_DAYS more; fruit; mechanics off -> extinguish -> 2500 -> fires; on -> 2500;
errors logged in that window; save end), split across foreground calls of <= BUDGET_S. State: Transient/pv1/walk_state.json.
Heat guard + food top-up every 6000 ticks (the suite's own guard). Reloads go through the main menu (northstar_site)."""
import sys, os, json, time
HERE = os.path.abspath(r"src\RimMandrake\Pyrelands"); sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(r"src\RimMandrake\Utils"))
import northstar_site as NS
from northstar_driver.session import FastSession
from game_paths import SAVES
ST = r"Transient\pv1\walk_state.json"; BUDGET_S = 420; DAY = 60000; WALK_DAYS = 7
S = "RimMandrake.Pyrelands.RM_PyrelandsSettings"; ASH_FIELD = "RimMandrake.Pyrelands.MapComponent_PyrelandsAshField"
BURN_LINE = "RimMandrake.Pyrelands.MapComponent_BurnLine"; FRUIT = "RM_FE_Plant_ScorchFruit"; W = "pyre_walk"
st = json.load(open(ST)) if os.path.exists(ST) else {"phase": "pre"}
t0 = time.time()
def save(st): json.dump(st, open(ST, "w"), indent=1)
s = FastSession(strict=False)
with s:
    c = lambda tool, **kw: s.call(tool, **kw) or {}
    def ticks(): return int(c("jawa/weather_get").get("ticksGame"))
    def count(d): return c("jawa/list_things", defName=d, limit=1).get("countMatched")
    def digest():
        d = {k: count(k) for k in ("Fire", FRUIT, "RM_FE_ScorchFruitYield", "RM_FurnaceBeast", "RM_Ullai")}
        d["regrowth"] = str(c("jawa/static_call", type=ASH_FIELD, method="ProbeRegrowth").get("result", ""))[:400]
        d["burnHistory"] = str(c("jawa/static_call", type=BURN_LINE, method="ProbeBurnHistory", args="0").get("result", ""))[:400]
        return d
    def guard():
        r = c("jawa/list_pawns", faction="player", includeHealth=True, limit=100)
        alive = 0
        for q in r.get("pawns") or []:
            if q.get("dead") or q.get("intelligence") not in (None, "Humanlike"): continue
            alive += 1
            if any(h.get("def") == "Heatstroke" for h in (q.get("health") or {}).get("hediffs") or []):
                c("jawa/pawn_health", pawn=q["id"], action="remove", hediff="Heatstroke")
            c("jawa/pawn_need", pawn=q["id"], action="need", need="Food", level=1.0)
        return alive
    def adv_to(target):
        while True:
            left = target - ticks()
            if left <= 0: return True
            r = c("jawa/safe_advance", ticks=min(6000, left), timeException=False, timeoutMs=600000)
            if r.get("state") != "done": st.setdefault("stops", []).append(str(r.get("stopBy") or r.get("state"))[:160])
            st["colonists"] = guard()
            if st["colonists"] == 0: st["dead_colony"] = True; return False
            if int(r.get("executed") or 0) == 0: st.setdefault("stalls", []).append(ticks())
            if len(st.get("stalls", [])) > 5: raise SystemExit("advance stalls: %r" % r)
            if time.time() - t0 > BUDGET_S: return False
    def saved(name):
        before = {f: os.stat(os.path.join(SAVES, f)).st_mtime for f in os.listdir(SAVES)}
        c("rimworld/save_game", saveName=name); time.sleep(3)
        after = {f: os.stat(os.path.join(SAVES, f)).st_mtime for f in os.listdir(SAVES)}
        new = [f for f in after if f not in before]; ch = [f for f in before if after.get(f) != before[f]]
        if new + ch != [name + ".rws"]: raise SystemExit("save %s touched %r / %r" % (name, new, ch))
        return name
    def load_bare(name):   # main menu -> load -> a map answers -> the site current; NO ticks (the digest compares)
        if NS._ui_state(s).get("programState") == "Playing":
            try: c("rimworld/go_to_main_menu")
            except Exception: pass
            NS._wait_state(s, "Entry", 300)
        try: c("rimworld/load_game", saveName=name)
        except Exception as e: print("load raised", type(e).__name__)
        NS._wait_state(s, "Playing", 480)
        t = time.time()
        while time.time() - t < 480:
            try:
                if c("jawa/map_info").get("tile") is not None: break
            except Exception: pass
            time.sleep(2)
        c("jawa/set_current_map", mapId=NS.find_site_map(s, st["tile"]))
        mi = c("jawa/map_info"); assert mi.get("mapBiome") == "RM_Pyrelands", mi
    ph = st["phase"]; print("phase", ph, "colonists", st.get("colonists"))
    if ph == "pre":
        st["tile"] = c("jawa/map_info").get("tile"); st["pre"] = saved(W + "_pre"); st["t1"] = ticks(); st["phase"] = ph = "half1"; save(st)
    if ph == "half1":
        if adv_to(st["t1"] + WALK_DAYS * DAY): st["phase"] = ph = "mid"
        save(st)
    if ph == "mid" and time.time() - t0 < BUDGET_S:
        saved(W + "_mid"); st["d_mid"] = digest(); st["phase"] = ph = "reload_mid"; save(st)
    if ph == "reload_mid" and time.time() - t0 < BUDGET_S:
        load_bare(W + "_mid"); st["d_mid_reloaded"] = digest(); st["phase"] = ph = "reload_pre"; save(st)
    if ph == "reload_pre" and time.time() - t0 < BUDGET_S:
        load_bare(W + "_pre"); st["d_pre"] = digest(); st["phase"] = ph = "back_to_mid"; save(st)
    if ph == "back_to_mid" and time.time() - t0 < BUDGET_S:
        NS.reload_fixture(s, W + "_mid", st["tile"]); st["t2"] = ticks(); st["phase"] = ph = "half2"; save(st)
    if ph == "half2" and time.time() - t0 < BUDGET_S:
        if adv_to(st["t2"] + WALK_DAYS * DAY): st["phase"] = ph = "end"
        save(st)
    if ph == "end" and time.time() - t0 < BUDGET_S:
        st["fruit"] = count(FRUIT) or 0
        mark = c("jawa/drain_log", limit=1).get("totalInBuffer")
        prior = c("jawa/mod_settings_field", typeName=S, action="get", field="pyrelandsEnabled").get("value")
        c("jawa/mod_settings_field", typeName=S, action="set", field="pyrelandsEnabled", value="False")
        c("jawa/map_fire", action="extinguish", rect="0,0,250,250")
        c("jawa/safe_advance", ticks=2500, timeException=False); st["fires_off"] = count("Fire") or 0
        c("jawa/mod_settings_field", typeName=S, action="set", field="pyrelandsEnabled", value=str(prior))
        c("jawa/safe_advance", ticks=2500, timeException=False)
        r = c("jawa/drain_log", limit=500); total = r.get("totalInBuffer"); msgs = r.get("messages") or []
        win = msgs[len(msgs) - (total - mark):] if (total is not None and mark is not None and total > mark) else []
        st["log_window"] = {"mark": mark, "total": total, "read": len(win)}
        st["errors"] = [m.get("text", "")[:200] for m in win if str(m.get("type", "")).lower() in ("error", "exception")]
        saved(W + "_end")
        keys = set(st["d_mid"]) & set(st["d_mid_reloaded"])
        st["reload_equal"] = bool(keys) and all(st["d_mid"][k] == st["d_mid_reloaded"][k] for k in keys)
        st["pre_differs"] = any(st["d_pre"].get(k) != st["d_mid"].get(k) for k in keys)
        st["verdict"] = "PASS" if (st["reload_equal"] and st["pre_differs"] and st["fruit"] > 0 and st["fires_off"] == 0 and not st["errors"]) else "FAIL"
        st["phase"] = "done"; save(st)
    print({k: st.get(k) for k in ("phase", "t1", "t2", "colonists", "verdict", "reload_equal", "pre_differs", "fruit", "fires_off", "errors", "dead_colony")}, "now", ticks(), "wall", int(time.time() - t0))
save(st)
