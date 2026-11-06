#!/usr/bin/env python3
"""Offline proof of glow_tank_live.py's crop row on a FROZEN fresh map (GLOWTANK_CROP_FIX_FROZEN_FRESH_MAP).

    python3 src/RimMandrake/FlowWorks/northstar/selftest_glow_tank_live.py

A fake bridge models the engine rules the harness leans on (RimWorld 1.6 decompile):
  * PlantUtility.GrowthSeasonNow(cell): the CELL temperature must exceed minGrowthTemperature (0 C); the outdoors here is
    -15 C and no tool can heat it (room_heat set refuses a cell with no room);
  * Room.UsesOutdoorTemperature: a walled room whose open-roof cells are >= 25% of its interior is outdoors;
  * a set room temperature drifts back toward ambient between pins;
  * Plant.Resting: no growth outside day 0.25-0.8; growth 1/(60000*growDays) a tick, growDays 12, applied per TickLong;
  * the plant inspect reads 'N% grown' (integer) and 'Growth rate: N%'; a parched (dry) glow tank does not grow.
Checks: the crop row PASSes with salt growing and fresh not; the clock is never set; every stepped chunk is preceded by a
pin; each room leaves exactly the glow tank's 4 cells open (under 25%); a pin that cannot hold is UNMEASURED SITE; an
inspect without 'N% grown' is UNMEASURED HARNESS; a salt tank that never drinks is a FAIL; the default window is a day.
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glow_tank_live as G  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  " + str(detail)[:400]))
    if not ok:
        FAILS.append(name)


class Fake:
    AMBIENT = -15.0

    def __init__(self, room_ok=True, inspect_style="grown", salt_drinks=True, start_tick=50000, ambient=-15.0, leak=0.0002):
        self.AMBIENT, self.leak = ambient, leak
        self.calls = []
        self.tick = start_tick
        self.rooms = []          # dict(rect, open:set, temp)
        self.things = {}         # id -> dict
        self.tanks = {}          # (x,z) -> [liquid, units]
        self.n = 0
        self.room_ok, self.style, self.salt_drinks = room_ok, inspect_style, salt_drinks
        self.reserve = {}        # glow id -> ticks of water

    # -- geometry
    def room_at(self, x, z):
        for r in self.rooms:
            rx, rz, w, h = r["rect"]
            if rx < x < rx + w - 1 and rz < z < rz + h - 1:
                inner = (w - 2) * (h - 2)
                return None if len(r["open"]) >= -(-inner // 4) else r
        return None

    def temp_at(self, x, z):
        r = self.room_at(x, z)
        return r["temp"] if r else self.AMBIENT

    def season(self, gt):
        return self.temp_at(*gt) > 0.0

    def new(self, d, x, z, **kw):
        self.n += 1
        tid = "%s%d" % (d, self.n)
        self.things[tid] = dict(d=d, x=x, z=z, **kw)
        return tid

    def glow_of(self, x, z):
        for tid, t in self.things.items():
            if t["d"] == "RM_GlowTank" and t["x"] <= x <= t["x"] + 1 and t["z"] <= z <= t["z"] + 1:
                return tid
        return None

    def parched(self, gid):
        return self.reserve.get(gid, 0) <= 0

    # -- the clock
    def advance(self, n):
        for _ in range(n):
            self.tick += 1
            for r in self.rooms:
                r["temp"] += (self.AMBIENT - r["temp"]) * self.leak
            if self.tick % 250 == 0:
                for gid, g in self.things.items():
                    if g["d"] != "RM_GlowTank":
                        continue
                    self.reserve[gid] = max(0, self.reserve.get(gid, 0) - 250)
                    if self.reserve[gid] <= 0:
                        t = self.tanks.get((g["x"] + 2, g["z"]))
                        if t and t[0] == "RM_Liquid_SaltWater" and t[1] >= G.DRAW and self.salt_drinks:
                            t[1] -= G.DRAW
                            self.reserve[gid] = 60000
                            g["drawn"] = True
            if self.tick % 2000 == 0:
                day = (self.tick % 60000) / 60000.0
                if 0.25 <= day <= 0.8:
                    for t in self.things.values():
                        if t["d"] != "RM_CrowncarpetCultured":
                            continue
                        gid = self.glow_of(t["x"], t["z"])
                        if gid and self.season((t["x"], t["z"])) and not self.parched(gid):
                            t["growth"] = min(1.0, t["growth"] + 2000.0 / (60000 * 12))

    # -- the bridge
    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "rimworld/step_game_ticks":
            self.advance(int(kw["ticks"]))
            return {"success": True}
        if tool == "jawa/make_empty_room":
            x, z, w, h = (int(v) for v in kw["rect"].split(","))
            self.rooms.append({"rect": (x, z, w, h), "open": set(), "temp": self.AMBIENT})
            return {"success": True}
        if tool == "jawa/set_roof_batch":
            d, r = kw["ops"].split(":")
            x, z, w, h = (int(v) for v in r.split(","))
            for room in self.rooms:
                for cx in range(x, x + w):
                    for cz in range(z, z + h):
                        rx, rz, rw, rh = room["rect"]
                        if rx < cx < rx + rw - 1 and rz < cz < rz + rh - 1:
                            room["open"].add((cx, cz))
            return {"success": True}
        if tool == "jawa/room_heat":
            r = self.room_at(kw["x"], kw["z"]) if self.room_ok else None
            if r is None:
                return {"success": False, "message": "no room at that cell"}
            b, r["temp"] = r["temp"], float(kw["value"])
            return {"success": True, "temperatureBefore": b, "temperatureAfter": r["temp"]}
        if tool == "jawa/build_batch":
            for op in kw["ops"].split(";"):
                d, c = op.split(":")
                x, z = (int(v) for v in c.split(","))
                self.new(d, x, z)
            return {"success": True}
        if tool == "jawa/list_things":
            x, z, w, h = (int(v) for v in kw["rect"].split(","))
            got = [{"id": tid} for tid, t in self.things.items()
                   if t["d"] == kw["defName"] and x <= t["x"] < x + w and z <= t["z"] < z + h]
            return {"success": True, "things": got[:kw.get("limit", 50)]}
        if tool == "jawa/set_plants":
            d, r = kw["ops"].split(":")
            x, z, w, h = (int(v) for v in r.split(","))
            for cx in range(x, x + w):
                for cz in range(z, z + h):
                    self.new(d, cx, cz, growth=float(kw["growth"]))
            return {"success": True, "planted": w * h}
        if tool == "jawa/inspect_string":
            out = []
            for tid in kw["thingIds"].split(","):
                t = self.things[tid]
                if t["d"] == "RM_GlowTank":
                    ln = ["Power needed: 180 W",
                          "Growing season here now." if self.season((t["x"], t["z"])) else "Cannot grow (bad seasonal temperature)."]
                    if G_SETTING["tankNeedsWater"]:
                        ln.append("Dry: growth paused." if self.parched(tid) else "Ocean water: 5.9 h in reserve (salt water).")
                else:
                    pct = int((t["growth"] + 0.0001) * 100)
                    ln = (["%d%% grown" % pct] if self.style == "grown" else ["Growth: %d%%" % pct]) + ["Growth rate: 71%"]
                out.append({"id": tid, "inspect": ln})
            return {"success": True, "things": out}
        if tool == "jawa/mod_settings_field":
            if kw["action"] == "get":
                return {"success": True, "value": str(G_SETTING["tankNeedsWater"])}
            G_SETTING["tankNeedsWater"] = kw["value"] == "True"
            return {"success": True}
        if tool == "jawa/time_set_ticks":
            raise AssertionError("the harness set the clock")
        return {"success": True}

    def hp(self, s):
        if s.startswith("filltank:"):
            c, rest = s[len("filltank:"):].split("=")
            liq, n = rest.split(",")
            self.tanks[tuple(int(v) for v in c.split(","))] = [liq, int(n)]
            return {"success": True}
        if s.startswith("tank:"):
            t = self.tanks.get(tuple(int(v) for v in s[len("tank:"):].split(",")))
            return {"units": t[1] if t else None}
        return {}


G_SETTING = {"tankNeedsWater": True}


def run(fake, args=()):
    G_SETTING["tankNeedsWater"] = True
    V = types.SimpleNamespace(_wait_playing=lambda B, leave_s=0: (True, None), site_calm=lambda B: {"ok": True},
                              prepare_site=lambda B, rect, rows, name: rows.append({"status": "PASS"}))
    sys.modules["proof_hose"] = types.SimpleNamespace(V=V, PB=lambda: fake)
    out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "selftest_glow_tank_%d.json" % os.getpid())
    argv = sys.argv
    sys.argv = ["glow_tank_live.py", out] + list(args)
    try:
        rc = G.main()
    finally:
        sys.argv = argv
    import json
    with open(out, encoding="utf-8") as f:
        res = json.load(f)
    os.remove(out)
    return rc, {r["id"]: r for r in res["rows"]}, res


def main():
    check("grown_fraction reads 'N% grown' and skips 'Growth rate'",
          G.grown_fraction(["12% grown", "Growth rate: 71%", "Growth: 30%"]) == [0.12])
    import argparse  # noqa: F401
    check("default window is a whole day", "default=60000" in open(G.__file__, encoding="utf-8").read())
    # GLOWTANK_PROOF_FIX_GROWTH_PARSER_BLIND: the giants go before the site prep (prepare_site does it for every caller)
    import inspect as _insp
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
    import validation_core as _VC
    swept = _insp.getsource(_VC._prepare_site_swept)
    check("prepare_site clears huge plants before the site prep",
          "clear_huge_plants(B)" in swept and swept.index("clear_huge_plants(B)") < swept.index("return _prepare_site("))
    x, z, w, h = G.room_rect(60, 152)
    inner = (w - 2) * (h - 2)
    check("4 open of the room's interior stays under Room.UsesOutdoorTemperature's 25%", 4 < -(-inner // 4), inner)
    check("the room's interior holds battery, glow tank and liquid tank",
          x < 61 and 60 + 7 < x + w - 1 and z < 152 and 153 < z + h - 1, (x, z, w, h))

    f = Fake()
    rc, rows, res = run(f)
    crop = rows.get("GLOWTANK_SALT_CROP_GROWS", {})
    check("frozen fresh map, pinned rooms: crop row PASS", crop.get("status") == "PASS", crop)
    d = crop.get("detail", {})
    check("salt grew and fresh did not", d.get("saltGrowth", [0, 0])[1] > d.get("saltGrowth", [0, 0])[0]
          and d.get("freshGrowth", [0, 1])[1] == d.get("freshGrowth", [0, 1])[0], d)
    check("drawn-one-unit row still PASS", rows.get("GLOWTANK_SALT_DRAWN_ONE_UNIT", {}).get("status") == "PASS",
          rows.get("GLOWTANK_SALT_DRAWN_ONE_UNIT"))
    tools = [c[0] for c in f.calls]
    check("the clock is never set", "jawa/time_set_ticks" not in tools)
    steps = [i for i, t in enumerate(tools) if t == "rimworld/step_game_ticks"]
    unpinned = [i for i in steps[1:] if "jawa/room_heat" not in tools[max(0, i - 8):i]]
    check("every stepped chunk after setup follows a pin", not unpinned and len(steps) >= 1 + 60000 // G.CHUNK, (len(steps), unpinned[:3]))
    check("no step longer than a chunk", all(int(c[1]["ticks"]) <= G.CHUNK for c in f.calls if c[0] == "rimworld/step_game_ticks"))
    check("each room opens exactly the glow tank's 4 cells", [len(r["open"]) for r in f.rooms] == [4, 4, 4], [len(r["open"]) for r in f.rooms])
    check("rooms are built before the scene", tools.index("jawa/make_empty_room") < tools.index("jawa/build_batch"))

    rc, rows, _ = run(Fake(room_ok=False))
    crop = rows.get("GLOWTANK_SALT_CROP_GROWS", {})
    check("a pin that cannot hold (no room) is UNMEASURED SITE, not FAIL",
          crop.get("status") == "UNMEASURED" and crop.get("class") == "SITE", crop)

    # a bitter, leaky map: the room loses ~45% of its lead per 1000-tick chunk and drops out of season between pins;
    # the row must say SITE, never a crop FAIL
    rc, rows, _ = run(Fake(ambient=-90.0, leak=0.0006))
    crop = rows.get("GLOWTANK_SALT_CROP_GROWS", {})
    check("a room that cools out of season between pins is UNMEASURED SITE, not FAIL",
          crop.get("status") == "UNMEASURED" and crop.get("class") == "SITE" and crop["detail"]["pins"].get("cold"), crop)
    rc, rows, _ = run(Fake(ambient=-40.0, leak=0.0002))
    check("a -40 C map at the same leak still holds the season and PASSes",
          rows.get("GLOWTANK_SALT_CROP_GROWS", {}).get("status") == "PASS", rows.get("GLOWTANK_SALT_CROP_GROWS"))

    rc, rows, _ = run(Fake(inspect_style="growth"))
    crop = rows.get("GLOWTANK_SALT_CROP_GROWS", {})
    check("an inspect without 'N% grown' is UNMEASURED HARNESS", crop.get("status") == "UNMEASURED" and crop.get("class") == "HARNESS", crop)

    rc, rows, _ = run(Fake(salt_drinks=False))
    crop = rows.get("GLOWTANK_SALT_CROP_GROWS", {})
    check("a salt tank that never feeds the crop is a crop FAIL", crop.get("status") == "FAIL", crop)

    for start in (0, 20000, 47000):
        rc, rows, _ = run(Fake(start_tick=start))
        check("any start hour: crop row PASS (start tick %d)" % start,
              rows.get("GLOWTANK_SALT_CROP_GROWS", {}).get("status") == "PASS", rows.get("GLOWTANK_SALT_CROP_GROWS"))

    # GAMEENV_FIX_HARNESS_EEE35FD9_ITEMS_WAIT: the day needs ~1000 s, the lane kills at 600 s unless the proof line carries
    # --max-seconds; the run then stops itself at its own wall and reads UNMEASURED (exit 2), never a kill or a FAIL
    real_time = G.time
    clock = [0.0]

    def fake_time():
        clock[0] += 5.0          # every clock read costs 5 s: the 60-chunk day takes far longer than a 100 s wall
        return clock[0]
    G.time = types.SimpleNamespace(time=fake_time, strftime=real_time.strftime)
    try:
        f = Fake()
        rc, rows, res = run(f, ["--max-seconds", "100"])
    finally:
        G.time = real_time
    crop = rows.get("GLOWTANK_SALT_CROP_GROWS", {})
    check("a day that outruns --max-seconds is UNMEASURED HARNESS with its reason, exit 2",
          rc == 2 and crop.get("status") == "UNMEASURED" and crop.get("class") == "HARNESS"
          and "UNMEASURED: the day outran --max-seconds 100" in crop["detail"]["why"] and res.get("stoppedEarly"), (rc, crop))
    n_steps = sum(1 for c in f.calls if c[0] == "rimworld/step_game_ticks")
    check("the wall stops the stepping short", n_steps < 1 + 60000 // G.CHUNK, n_steps)
    rc, rows, _ = run(Fake(), ["--max-seconds", "100000"])
    check("a wall the day fits inside changes nothing: exit 0, crop PASS",
          rc == 0 and rows.get("GLOWTANK_SALT_CROP_GROWS", {}).get("status") == "PASS", (rc, rows.get("GLOWTANK_SALT_CROP_GROWS")))
    check("verdict: all PASS 0, a FAIL 1, UNMEASURED without FAIL 2",
          (G.verdict([{"status": "PASS"}]), G.verdict([{"status": "PASS"}, {"status": "FAIL"}, {"status": "UNMEASURED"}]),
           G.verdict([{"status": "PASS"}, {"status": "UNMEASURED"}])) == (0, 1, 2))
    # the live proof line must carry a wall the lane honours (proof_budget = max-seconds + 120 over the 600 s default)
    root = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
    sys.path.insert(0, os.path.join(root, "src", "RimMandrake", "rimflow"))
    import re
    import relentless_live as RL
    lp = os.path.join(root, "infrastructure", "state", "live_proofs", "GLOWTANK_CROP_FIX_FROZEN_FRESH_MAP.txt")
    lines = [ln for ln in open(lp, encoding="utf-8") if ln.startswith("live-proof ") and "glow_tank_live.py" in ln]
    walls = [int(m.group(1)) for ln in lines for m in [re.search(r"--max-seconds (\d+)", ln)] if m]
    check("the GLOWTANK live proof carries --max-seconds >= 1500 and the lane allows it + 120 s",
          lines and len(walls) == len(lines) and all(w >= 1500 and RL.proof_budget(ln, 600) == w + 120
                                                     for w, ln in zip(walls, lines)), (walls, lines[:1]))

    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
