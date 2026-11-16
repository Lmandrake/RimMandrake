#!/usr/bin/env python3
"""Offline test of validation.py's walk_storeroom_raid leaf (scene sc_walk_raid) against a fake bridge
(RIMMANDRAKE_GIVE_WALK_RAID_LIVE_MODE_STATIC_EXITS_ZERO). The fake is a tiny world: goods in a storeroom, a shelf and a
closed locker, a covered pit cell, a vent-gas cloud; a blast requests and moves every good in its radius, a lit cloud
bursts one cell a tick outward from the lit cell, saves and loads copy the world. Each planted break must flip ITS row:
  W0  a sound world: every row PASS, FRAME_BUDGET included (RM_KnockbackProof.Frame answers a p99 under 50 ms), so exit 0
      (RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED: before it the row was UNMEASURED by construction)
  W1  --live with no game (time_perf refused) refuses with exit 2, never STATIC: PASS exit 0
  W2  the release DLL ("Type not found") exits 3
  W3  no closed container in the storeroom: W_PRECONDITIONS INVALID, every other row UNMEASURED
  W4  a reload duplicates a good: A_RELOAD_NO_DUP_LOST FAIL
  W5  the gas bursts all on one tick: A_ and B_GAS_CLUMP_BY_CLUMP FAIL
  W6  a request with no outcome line: A_ and B_REQUESTS_MATCH_PLAN FAIL
  W7  the mod-off control still throws: C_OFF_IMPACTS_NO_THROWS FAIL
  W8  the grenade leaves the cover: A_ and B_COVER_BROKEN_ONE_DESCENT FAIL
  W9  a good inside a shell's radius gets no journal line: A_REACHED_ACCOUNTED FAIL
  W10 `validation.py --live` (no leaf) and `--live walk_storeroom_raid` under WSL python3 both exit non-zero
  W11 a sound save whose load runs one tick (PauseOnLoad) while the shell's wave still destroys stacks: A_RELOAD_NO_DUP_LOST
      PASS (run 2 of visit 2 read "11 before, 7 after" from two different ticks; RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES)
  W12 nobody on the cover when the grenade goes off: A_ and B_COVER_BROKEN_ONE_DESCENT UNMEASURED (a SITE miss), not FAIL
  W13 the grenade kills the rider: COVER rows UNMEASURED, and the rider's request answered by its corpse's line keeps
      A_ and B_REQUESTS_MATCH_PLAN PASS
  W14 a living rider, the cover gone, no descent: A_ and B_COVER_BROKEN_ONE_DESCENT FAIL (the mod's row still bites)
  W15 a storeroom shell breaks the cover (live run 3, 2026-11-16: the first shell broke it, the rider fell then, and the
      grenade thrown after met no cover): the grenade is thrown first in each order, so the COVER rows still PASS
  W17 a thing born after the mid-air save takes its id from the game's counter, which a load advances (live 2026-11-16:
      42837 live, 43837 in both loads): A_RELOAD_NO_DUP_LOST still PASSes; ids are compared only for things the save holds
  W18 a thing born after the save is placed with the RNG, whose state a load changes (live 2026-11-16: a WoodLog leaving at
      101,42 live, 102,42 in both loads): born things are counted by def, not by cell, and the row still PASSes
  W19 the frame probe reads a 99th-percentile frame of 75 ms in the real-time window: FRAME_BUDGET FAIL
  W20 the frame probe saw no frame (Frame stop answers NONE): FRAME_BUDGET UNMEASURED, never PASS
  W16 the cover already gone when the grenade comes: COVER rows UNMEASURED naming it, never a mod FAIL read off an empty
      journal

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_walk_raid.py
"""
import copy
import io
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

ARGS = ["--storeroom", "10,10,7,7", "--cover", "13,19", "--gas", "26,13", "--lit", "24,13", "--raid-points", "300",
        "--out", os.devnull, "--stamp", "T"]


class Fake:
    def __init__(self, **brk):
        self.brk = brk
        self.saves = {}
        self.w = {"tick": 0, "enabled": True, "cover": True, "goods": {}, "carriers": [], "journal": [], "gas": None,
                  "burn": [], "wave": [], "pawns": {} if brk.get("no_rider") else {"Human900": {"pos": [13, 19], "dead": False}}}
        n = 100
        for x in range(11, 16):
            for z in (11, 13, 15):
                self.w["goods"][str(n)] = [x, z]
                n += 1
        self.w["goods"][str(n)] = [26, 14]       # in the gas cloud
        self.w["goods"][str(n + 1)] = [27, 13]
        self.next_exp = 1

    # journal helpers
    def rec(self, **kw):
        kw.setdefault("tick", self.w["tick"])
        self.w["journal"].append(kw)

    def blast(self, at, radius, source="shell"):
        exp = self.next_exp
        self.next_exp += 1
        if at != (13, 19) and self.brk.get("cover_broken_early") and self.w["cover"]:
            # a shell (or a raider's blast) breaks the cover before the scripted grenade: the rider falls in then
            self.w["cover"] = False
            if self.w["pawns"].get("Human900"):
                self.rec(type="descent", exp=0, thing="Human900", at=[13, 19], **{"def": "Human"})
        if at == (13, 19):
            rider = self.w["pawns"].get("Human900")
            if rider and not rider["dead"]:
                self.rec(type="request", exp=exp, thing="Human900", centre=list(at), radius=radius, **{"def": "Human"})
                if self.brk.get("rider_killed"):
                    rider["dead"] = True
            if not self.brk.get("cover_stays"):
                had, self.w["cover"] = self.w["cover"], False
                if had and rider and not rider["dead"] and not self.brk.get("no_descent"):     # no lid, no fall
                    self.rec(type="descent", exp=0, thing="Human900", at=[13, 19], **{"def": "Human"})
            if rider and rider["dead"]:
                self.rec(type="skip", exp=exp, thing="Corpse_Human901", reason="in_pit", **{"def": "Corpse_Human"})
            elif rider:
                self.rec(type="skip", exp=exp, thing="Human900", reason="in_pit", **{"def": "Human"})
            return
        if not self.w["enabled"] and not self.brk.get("off_throws"):
            return
        for gid, (x, z) in sorted(self.w["goods"].items()):
            d = math.hypot(x - at[0], z - at[1])
            if d > radius:
                continue
            if self.brk.get("unjournalled") and gid == "112":
                continue
            th = "Steel" + gid
            self.rec(type="request", exp=exp, thing=th, centre=list(at), radius=radius)
            if self.brk.get("orphan") and gid == "106":
                continue
            if self.brk.get("wave_destroys") and d > radius - 1:
                self.w["wave"].append(gid)          # the wave's outer ring is reached a tick later, and it burns
                self.rec(type="skip", exp=exp, thing=th, reason="destroyed")
                continue
            dx = (x > at[0]) - (x < at[0]) or 1
            dest = [x + dx, z]
            self.rec(type="item_move", exp=exp, thing=th, kind="Item", **{"from": [x, z]}, to=dest, planned=1, cells=1,
                     stop="None", kernelCells=1, wildCells=1, flying=True)
            self.w["goods"].pop(gid)
            self.w["carriers"].append({"inner": gid, "dest": dest, "left": 15})   # live: 13 left at the mid-air save

    def tick(self):
        self.w["tick"] += 1
        if self.brk.get("reid_after_save") and self.w.get("savedAt") is not None and self.w["tick"] == self.w["savedAt"] + 3:
            # a leaving born after the save (the shell's wave breaks a shelf): its id comes from the game's counter, which a
            # load advances (live 2026-11-16: 42837 live, 43837 after both loads)
            self.w["goods"][str(self.w.get("nextId", 5000))] = [14, 14] if self.w.get("loaded") and self.brk.get(
                "born_cell_differs") else [14, 13]   # a leaving is placed with the RNG, whose state a load changes
            self.w["nextId"] = self.w.get("nextId", 5000) + 1
        if self.w["wave"]:
            self.w["goods"].pop(self.w["wave"].pop(0), None)
        for c in list(self.w["carriers"]):
            c["left"] -= 1
            if c["left"] <= 0:
                self.w["carriers"].remove(c)
                self.w["goods"][c["inner"]] = c["dest"]
        if self.w["burn"]:
            batch = self.w["burn"] if self.brk.get("gas_at_once") else self.w["burn"][:1]
            for cell in batch:
                exp = self.next_exp
                self.rec(type="gas_burst", exp=exp, at=list(cell), source="vent", radius=1.5, queued=1)
                self.next_exp += 1
                for gid, (x, z) in sorted(self.w["goods"].items()):
                    if abs(x - cell[0]) <= 1 and abs(z - cell[1]) <= 1:
                        th = "Steel" + gid
                        self.rec(type="request", exp=exp, thing=th, centre=list(cell), radius=1.5)
                        self.rec(type="item_move", exp=exp, thing=th, kind="Item", **{"from": [x, z]}, to=[x + 1, z],
                                 planned=1, cells=1, stop="None", kernelCells=1, wildCells=1, flying=False)
                        self.w["goods"][gid] = [x + 1, z]
            self.w["burn"] = [] if self.brk.get("gas_at_once") else self.w["burn"][1:]

    # the bridge
    def call(self, tool, _answer=False, **kw):
        w = self.w
        if tool == "jawa/time_clock":
            return {"success": True, "ticksGame": w["tick"]}
        if tool == "jawa/list_pawns":
            x, z, ww, hh = (int(v) for v in kw["rect"].split(","))
            return {"success": True, "pawns": [{"id": i, "def": "Human", "x": p["pos"][0], "z": p["pos"][1], "dead": p["dead"],
                                                "spawned": not p["dead"]} for i, p in sorted(w["pawns"].items())
                                               if x <= p["pos"][0] < x + ww and z <= p["pos"][1] < z + hh
                                               and (kw.get("includeCorpses") or not p["dead"])]}
        if tool == "jawa/time_perf":
            return {"success": False, "error": "No game loaded."} if self.brk.get("no_game") else {"success": True, "meanTickTime": 2.5}
        if tool == "jawa/static_call":
            m, a = kw["method"], kw.get("args", "")
            if self.brk.get("release") and kw["type"] == V.PROOF:
                return {"success": False, "error": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackProof"}
            r = {"Names": "calibration,wall_stop flowworks=True hoses=True", "Clear": "CLEARED",
                 "Plant": "PLANT %s gasreg=True" % a, "SeedCloud": "seeded 13 cells", "ClearOf": "cleared"}.get(m)
            if m == "Clear":
                w["journal"] = []
            elif m == "Journal":
                r = "\n".join(json.dumps(x) for x in w["journal"])
            elif m == "IsClosed":
                r = ("CLOSED " if a == "LWM_WeaponsLocker" else "OPEN ") + a
            elif m == "Flights":
                r = "\n".join("Flyer%d inner=Steel x10 innerId=Steel%s at=0,0 dest=%d,%d left=%d bounces=0"
                              % (i, c["inner"], c["dest"][0], c["dest"][1], c["left"]) for i, c in enumerate(w["carriers"])) or "NONE"
            elif m == "Settings":
                if a == "reset":
                    w["enabled"] = True
                elif a.startswith("enabled="):
                    w["enabled"] = a.split("=")[1] == "True"
                r = "SET " + a
            elif m == "SeedCloud":
                w["gas"] = a
            elif m == "Frame":
                if a == "begin":
                    w["probe"], w["probe_speed"] = True, []
                    r = "BEGUN"
                elif not w.pop("probe", False) or self.brk.get("probe_blind") or 1 not in w.get("probe_speed", []):
                    r = "NONE no probe running, or it saw no frame"
                else:
                    p99 = 75.0 if self.brk.get("slow_frames") else 24.0
                    r = ("FRAME frames=480 probeRows=480 paused=12 wall=8.00s worstMs=%.1f meanMs=16.7 maxInAir=12 window=0.5-8s "
                         "windowRows=450 windowP99Ms=%.1f path=C:/x/RM_FrameProbe_1.csv" % (p99 + 9, p99))
            return {"success": True, "result": r or "OK"}
        if tool == "jawa/list_things":
            x, z, ww, hh = (int(v) for v in kw["rect"].split(","))
            inr = lambda p: x <= p[0] < x + ww and z <= p[1] < z + hh  # noqa: E731
            if kw.get("group") == "BuildingArtificial":
                b = [{"id": "Shelf1", "def": "Shelf", "position": {"x": 11, "z": 11}}]
                if not self.brk.get("no_closed"):
                    b.append({"id": "Locker1", "def": "LWM_WeaponsLocker", "position": {"x": 15, "z": 15}})
                return {"success": True, "things": [t for t in b if inr((t["position"]["x"], t["position"]["z"]))]}
            if kw.get("group") == "HaulableEver":
                return {"success": True, "things": [{"id": "Steel" + g, "def": "Steel", "position": {"x": p[0], "z": p[1]}}
                                                    for g, p in sorted(w["goods"].items()) if inr(p)]}
            if w["cover"] and inr((13, 19)):
                return {"success": True, "things": [{"id": "Cover1", "def": "RM_PitCover_WovenFrame", "position": {"x": 13, "z": 19}}]}
            return {"success": True, "things": []}
        if tool == "jawa/explosion_at":
            self.blast(tuple(int(v) for v in kw["at"].split(",")), kw["radius"])
            return {"success": True}
        if tool == "jawa/map_fire":
            lx, lz = (int(v) for v in kw["rect"].split(",")[:2])
            gx, gz = 26, 13
            cells = sorted(((gx + dx, gz + dz) for dx in range(-2, 3) for dz in range(-2, 3) if dx * dx + dz * dz <= 4),
                           key=lambda c: math.hypot(c[0] - lx, c[1] - lz))
            w["burn"] = cells
            return {"success": True, "firesStarted": 1}
        if tool == "rimworld/step_game_ticks":
            for _ in range(kw["ticks"]):
                self.tick()
            return {"success": True}
        if tool == "rimworld/save_game":
            w["savedAt"] = w["tick"]
            self.saves[kw["saveName"]] = copy.deepcopy({k: v for k, v in w.items() if k != "journal"})
            return {"success": True}
        if tool == "rimworld/load_game":
            j = w["journal"]                        # the journal is a static class: a load keeps it
            self.w = copy.deepcopy(self.saves[kw["saveName"]])
            self.w["journal"] = j
            if self.brk.get("dup_on_reload") and self.w["carriers"]:
                self.w["goods"][self.w["carriers"][0]["inner"]] = [12, 12]   # a spawned twin of a good still in its carrier
            if self.brk.get("reid_after_save"):
                self.w["nextId"] = self.w.get("nextId", 5000) + 1000
                self.w["loaded"] = True
            if self.brk.get("load_tick"):
                self.tick()                         # Prefs.PauseOnLoad: Game.LoadGame runs one DoSingleTick
            return {"success": True}
        if tool == "rimworld/set_time_speed":
            if w.get("probe"):
                w.setdefault("probe_speed", []).append(kw.get("speed"))
            return {"success": True}
        if tool == "jawa/mod_settings_field":
            return {"success": True, "value": "True"}
        if tool == "jawa/fire_raid":
            if self.brk.get("cover_gone_at_raid"):
                w["cover"] = False                  # the raid broke the cover before any act of the walk
            return {"success": True, "executed": True, "pawnsArrivedTotal": 4}
        return {"success": True}


def run(**brk):
    V.active_mods = lambda path=None: list(V.MODS_NEEDED) + ["m%d" % i for i in range(300)]
    f = Fake(**brk)
    V.TRIPLET_SEAMS = {"saves_stat": lambda: dict((n + ".rws", (1, 1)) for n in f.saves), "wait_saved": lambda name: True}
    V.SLEEP = lambda s: None                # the frame act's real-time wait
    out = io.StringIO()
    code = V.walk_storeroom_raid(list(ARGS), bridge=f, wait=lambda B: (True, 0), out=out)
    rows = {}
    for line in out.getvalue().splitlines():
        p = line.split(None, 2)
        if len(p) >= 2 and p[0] in V.WALK_ROWS:
            rows[p[0]] = p[1]
    return code, rows, out.getvalue()


def main():
    fails = []

    def check(cid, ok, what):
        print("%s %-4s %s" % ("PASS" if ok else "FAIL", cid, what))
        if not ok:
            fails.append(cid)

    code, rows, txt = run()
    not_pass = sorted(r for r in V.WALK_ROWS if rows.get(r) != "PASS")
    check("W0", code == 0 and not_pass == [],
          "a sound world passes every row, FRAME_BUDGET included (code %s, not PASS: %s)" % (code, not_pass))
    if not_pass:
        print(txt)
    code, rows, _ = run(no_game=True)
    check("W1", code == 2, "no game refuses with exit 2 (got %s)" % code)
    code, rows, _ = run(release=True)
    check("W2", code == 3, "the release DLL exits 3 (got %s)" % code)
    code, rows, _ = run(no_closed=True)
    check("W3", code == 1 and rows.get("W_PRECONDITIONS") == "INVALID"
          and all(rows.get(r) == "UNMEASURED" for r in V.WALK_ROWS if r != "W_PRECONDITIONS"),
          "no closed container: preconditions INVALID, the rest UNMEASURED (%s)" % rows.get("W_PRECONDITIONS"))
    for cid, brk, want in (("W4", "dup_on_reload", ["A_RELOAD_NO_DUP_LOST"]),
                           ("W5", "gas_at_once", ["A_GAS_CLUMP_BY_CLUMP", "B_GAS_CLUMP_BY_CLUMP"]),
                           ("W6", "orphan", ["A_REQUESTS_MATCH_PLAN", "B_REQUESTS_MATCH_PLAN"]),
                           ("W7", "off_throws", ["C_OFF_IMPACTS_NO_THROWS"]),
                           ("W8", "cover_stays", ["A_COVER_BROKEN_ONE_DESCENT", "B_COVER_BROKEN_ONE_DESCENT"]),
                           ("W9", "unjournalled", ["A_REACHED_ACCOUNTED"])):
        code, rows, _ = run(**{brk: True})
        got = [rows.get(r) for r in want]
        check(cid, code == 1 and all(g == "FAIL" for g in got), "%s flips %s to FAIL (got %s)" % (brk, want, got))
    code, rows, txt = run(load_tick=True, wave_destroys=True)
    check("W11", rows.get("A_RELOAD_NO_DUP_LOST") == "PASS",
          "a load one tick late in a moving wave is still a sound save (got %s)" % rows.get("A_RELOAD_NO_DUP_LOST"))
    cover = ["A_COVER_BROKEN_ONE_DESCENT", "B_COVER_BROKEN_ONE_DESCENT"]
    code, rows, _ = run(no_rider=True)
    check("W12", [rows.get(r) for r in cover] == ["UNMEASURED"] * 2, "no rider: %s" % [rows.get(r) for r in cover])
    code, rows, _ = run(rider_killed=True)
    plan = ["A_REQUESTS_MATCH_PLAN", "B_REQUESTS_MATCH_PLAN"]
    check("W13", [rows.get(r) for r in cover] == ["UNMEASURED"] * 2 and [rows.get(r) for r in plan] == ["PASS"] * 2,
          "rider killed: cover %s, plan %s" % ([rows.get(r) for r in cover], [rows.get(r) for r in plan]))
    code, rows, _ = run(no_descent=True)
    check("W14", code == 1 and [rows.get(r) for r in cover] == ["FAIL"] * 2, "living rider, no descent: %s" % [rows.get(r) for r in cover])
    code, rows, txt = run(cover_broken_early=True)
    check("W15", [rows.get(r) for r in cover] == ["PASS"] * 2,
          "a storeroom shell that breaks the cover cannot pre-empt the grenade, thrown first (live 2026-11-16): %s"
          % [rows.get(r) for r in cover])
    code, rows, txt = run(cover_gone_at_raid=True)
    check("W16", [rows.get(r) for r in cover] == ["UNMEASURED"] * 2 and txt.count("already gone") >= 2,
          "the cover already gone when the grenade comes: UNMEASURED naming it, not FAIL: %s" % [rows.get(r) for r in cover])
    code, rows, txt = run(reid_after_save=True)
    check("W17", rows.get("A_RELOAD_NO_DUP_LOST") == "PASS",
          "a thing born after the save, re-numbered by the load, is neither lost nor new (live 2026-11-16): %s"
          % rows.get("A_RELOAD_NO_DUP_LOST"))
    code, rows, txt = run(reid_after_save=True, born_cell_differs=True)
    check("W18", rows.get("A_RELOAD_NO_DUP_LOST") == "PASS",
          "a thing born after the save lands on another cell after a load (the RNG; live 2026-11-16: WoodLog 101,42 live,"
          " 102,42 loaded): still PASS: %s" % rows.get("A_RELOAD_NO_DUP_LOST"))
    code, rows, txt = run(slow_frames=True)
    check("W19", code == 1 and rows.get("FRAME_BUDGET") == "FAIL",
          "a 75 ms 99th-percentile frame in the real-time window fails FRAME_BUDGET (code %s, got %s)" % (code, rows.get("FRAME_BUDGET")))
    code, rows, txt = run(probe_blind=True)
    check("W20", code == 1 and rows.get("FRAME_BUDGET") == "UNMEASURED",
          "a probe that saw no frame leaves FRAME_BUDGET UNMEASURED (code %s, got %s)" % (code, rows.get("FRAME_BUDGET")))
    script = os.path.join(HERE, "validation.py")
    r1 = subprocess.run([sys.executable, script, "--live"], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, script, "--live", "walk_storeroom_raid"] + ARGS[:6], capture_output=True, text=True,
                        env=dict(os.environ, RIMBRIDGE_HOST="127.0.0.1", GABP_SERVER_PORT="1"))
    check("W10", r1.returncode != 0 and r2.returncode != 0 and "STATIC: PASS" not in r1.stdout + r2.stdout,
          "--live without a leaf (%d) and with no reachable game (%d) refuse" % (r1.returncode, r2.returncode))
    print("%s walk_storeroom_raid leaf: %d failed" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
