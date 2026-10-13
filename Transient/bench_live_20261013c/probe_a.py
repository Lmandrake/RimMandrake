"""Probe A (BENCH 2026-10-13c): vitals across a load (TESTENV_VITALS_REPAIR_TICKSABS_SECOND_SOURCE,
TESTENV_VITALS_HARDEN_LOADS_ARE_NOT_JUMPS), then the off-site colony + toxic source on fixture p8a
(PYRE_SITE_VITALS_REPAIR_HALF_THE_COLONY, TESTENV_TOXIC_HARDEN_SITE_POISONS_ITS_GUESTS). Short: no wait > 2000 ticks."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(HERE, "src", "RimMandrake", "Pyrelands"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
FIX = "NS_Pyrelands_site_1_417df172fdb5_p8a"
TILE = 5
OUT = {}


def J(r):
    if isinstance(r, dict) and r.get("content"):
        try:
            return json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


def log_lines():
    with open(LOG, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def wait_playing(rb, budget=420):
    t0 = time.time()
    while time.time() - t0 < budget:
        try:
            if J(rb.call("rimworld/get_ui_state")).get("programState") == "Playing":
                return round(time.time() - t0)
        except Exception:
            pass
        time.sleep(3)
    raise SystemExit("not Playing after %ds" % budget)


def toxic(rb):
    rows = J(rb.call("jawa/list_pawns", {"includeHealth": True, "limit": 200})).get("pawns") or []
    out = {}
    for p in rows:
        if p.get("faction") is None and not p.get("isColonist"):
            pass
        hd = ((p.get("health") or {}).get("hediffs")) or []
        tox = [h.get("severity") for h in hd if (h.get("def") or h.get("defName")) == "ToxicBuildup"]
        if p.get("faction") or tox:
            out[str(p.get("name") or p.get("id"))] = {"faction": p.get("faction"), "tox": tox[0] if tox else 0.0,
                                                      "dead": p.get("dead"), "def": p.get("kind") or p.get("def")}
    return out


with RimBridge(*resolve_endpoint(), timeout=600.0) as rb:
    step = sys.argv[1] if len(sys.argv) > 1 else "a"
    if step == "a":
        # 1. a fresh quicktest game, armed, then a save loaded from inside it: the exact window of both vitals defects
        n0 = len(log_lines())
        print("menu", J(rb.call("rimworld/go_to_main_menu")).get("success"))
        print("qt", J(rb.call("rimworld/start_debug_game_ready", {"readiness": "mapData", "pauseIfNeeded": True,
                                                                     "timeoutMs": 280000})).get("success"))
        print("playing after", wait_playing(rb))
        arm = J(rb.call("jawa/vitals", {"action": "arm", "ttlMin": 60, "row": "probe_a", "why": "BENCH 13c load probe"}))
        print("arm", arm.get("success"), arm.get("message"))
        rb.call("rimworld/step_game_ticks", {"ticks": 120, "pauseFirst": True})
        seq0 = (J(rb.call("jawa/vitals")).get("latched") or {}).get("seq") or 0
        print("load", J(rb.call("rimworld/load_game", {"saveName": FIX})).get("success"))
        time.sleep(5)
        print("playing after", wait_playing(rb))
        rb.call("rimworld/step_game_ticks", {"ticks": 120, "pauseFirst": True})
        ev = J(rb.call("jawa/vitals", {"action": "events", "sinceSeq": 0, "limit": 500}))
        trig = ev.get("triggers") or []
        clock = [t for t in trig if t.get("kind") == "clock_discontinuity"]
        cov = [t for t in trig if t.get("kind") == "coverage"]
        lines = log_lines()[n0:]
        abserr = [l for l in lines if "gameStartAbsTick is not set" in l]
        errs = [l for l in lines if l.startswith("Exception") or "Error" in l[:40]]
        st = J(rb.call("jawa/vitals"))
        OUT["a"] = {"armed": st.get("armed"), "clockTriggers": clock, "coverage": [t.get("detail") for t in cov],
                    "ticksAbsErrors": abserr, "logLinesNew": len(lines), "clock": st.get("clock"), "faults": st.get("counters")}
        print(json.dumps(OUT["a"], indent=1)[:3000])
    elif step == "b":
        # 2. on the loaded p8a: what is map 0 and what poisons it
        maps = []
        for mid in range(0, 4):
            r = J(rb.call("jawa/set_current_map", {"mapId": mid}))
            if not r.get("success"):
                continue
            mi = J(rb.call("jawa/map_info"))
            w = J(rb.call("jawa/weather_get"))
            maps.append({"mapId": mid, "tile": mi.get("tile"), "biome": mi.get("mapBiome"),
                         "conditions": mi.get("gameConditions") or mi.get("conditions") or w.get("conditions") or w.get("activeConditions"),
                         "weather": w.get("weather") or w.get("current"), "outdoor": mi.get("outdoorTempNow"),
                         "pollutionKeys": [k for k in mi if "pollut" in k.lower()], "toxic": toxic(rb),
                         "mapInfoKeys": sorted(mi.keys())[:60], "weatherKeys": sorted(w.keys())[:40]})
        cols_all = J(rb.call("rimworld/list_colonists", {"currentMapOnly": False}))
        OUT["b"] = {"maps": maps, "colonistsAll": len(cols_all.get("colonists") or [])}
        print(json.dumps(OUT["b"], indent=1, default=str)[:6000])
    with open(os.path.join(HERE, "probe_%s.json" % step), "w") as f:
        json.dump(OUT, f, indent=1, default=str)
