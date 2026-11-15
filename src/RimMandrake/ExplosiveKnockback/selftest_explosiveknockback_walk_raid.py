#!/usr/bin/env python3
"""Offline test of validation.py's walk_storeroom_raid leaf (scene sc_walk_raid) against a fake bridge
(RIMMANDRAKE_GIVE_WALK_RAID_LIVE_MODE_STATIC_EXITS_ZERO). The fake is a tiny world: goods in a storeroom, a shelf and a
closed locker, a covered pit cell, a vent-gas cloud; a blast requests and moves every good in its radius, a lit cloud
bursts one cell a tick outward from the lit cell, saves and loads copy the world. Each planted break must flip ITS row:
  W0  a sound world: every row PASS but FRAME_BUDGET (UNMEASURED: no bridge read of RM_FrameProbe), so exit 1
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
                  "burn": []}
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
        if at == (13, 19):
            if not self.brk.get("cover_stays"):
                self.w["cover"] = False
                self.rec(type="descent", exp=0, thing="Steel900", at=[13, 19])
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
            dx = (x > at[0]) - (x < at[0]) or 1
            dest = [x + dx, z]
            self.rec(type="item_move", exp=exp, thing=th, kind="Item", **{"from": [x, z]}, to=dest, planned=1, cells=1,
                     stop="None", kernelCells=1, wildCells=1, flying=True)
            self.w["goods"].pop(gid)
            self.w["carriers"].append({"inner": gid, "dest": dest, "left": 5})

    def tick(self):
        self.w["tick"] += 1
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
            self.saves[kw["saveName"]] = copy.deepcopy({k: v for k, v in w.items() if k != "journal"})
            return {"success": True}
        if tool == "rimworld/load_game":
            j = w["journal"]                        # the journal is a static class: a load keeps it
            self.w = copy.deepcopy(self.saves[kw["saveName"]])
            self.w["journal"] = j
            if self.brk.get("dup_on_reload") and self.w["carriers"]:
                self.w["goods"][self.w["carriers"][0]["inner"]] = [12, 12]   # a spawned twin of a good still in its carrier
            return {"success": True}
        if tool == "jawa/mod_settings_field":
            return {"success": True, "value": "True"}
        if tool == "jawa/fire_raid":
            return {"success": True, "executed": True, "pawnsArrivedTotal": 4}
        return {"success": True}


def run(**brk):
    V.active_mods = lambda path=None: list(V.MODS_NEEDED) + ["m%d" % i for i in range(300)]
    f = Fake(**brk)
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
    check("W0", code == 1 and not_pass == ["FRAME_BUDGET"] and rows.get("FRAME_BUDGET") == "UNMEASURED",
          "a sound world passes every row but FRAME_BUDGET (code %s, not PASS: %s)" % (code, not_pass))
    if not_pass != ["FRAME_BUDGET"]:
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
