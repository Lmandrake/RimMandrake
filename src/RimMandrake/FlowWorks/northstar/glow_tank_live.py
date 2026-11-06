"""GLOW TANK WATER live check (GLOW_TANK_LIQUID_FEED_1 A2 + A3, LuminousPigment LP-2 on a FlowWorks tank; BENCH belt
2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/glow_tank_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N] [--max-seconds S]

Three identical scenes 10 squares apart: an RM_GlowTank (2x2) powered by a charged Battery over a PowerConduit, seeded
(jawa/thing_refuel 1 = the crowncarpet culture), RM_CrowncarpetCultured planted in its four squares at growth 0.10, and an
RM_LiquidTank touching it holding 10 draws of SALT water (scene S), FRESH water (scene F) or BRINE (scene B).
Rows:
  GLOWTANK_SALT_DRAWN_ONE_UNIT   EXPECT within 500 ticks S's tank lost exactly one draw (200 L = 2000 dL) and the glow tank
                                 reads "Ocean water: ... (salt water)"; F's and B's tanks lost nothing and read "Dry".
  GLOWTANK_SALT_CROP_GROWS       EXPECT over --ticks (default 60000, one whole day) S's crop grew more than F's (F is parched:
                                 growth paused).
  GLOWTANK_SETTING_OFF_NO_LINE   EXPECT with LuminousPigmentSettings.tankNeedsWater off the inspect has no water line
                                 (restored after).
SITE  GLOWTANK_CROP_FIX_FROZEN_FRESH_MAP: a fresh quicktest map is often out of growing season, and the engine's
      PlantUtility.GrowthSeasonNow(cell) reads the CELL temperature (> minGrowthTemperature 0), which no tool can raise
      outdoors. So every scene stands in a walled room (jawa/make_empty_room) whose roof is lifted over the glow tank's 2x2
      only: 4 open of 32 interior cells is under Room.UsesOutdoorTemperature's 25%, so the room keeps its own temperature
      while the crop still sees daylight; jawa/room_heat sets it to PIN_C before every stepped chunk (equalization drags
      it back toward ambient). The clock is only ever stepped, never set. A glow tank that still reads "Cannot grow" after
      the window is a SITE miss (UNMEASURED), never a crop FAIL.
      The window is a whole day because Plant.Resting stops growth outside day 0.25-0.8, and the read is the plant
      inspect's integer "N% grown" line (growDays 12: about 4% a day), never a "Growth" prefix (lesson 20261029T080817Z).
LIES  an unpowered tank grows nothing either (the battery is read charged and the inspect shows no 'needs power'); a plant
      that never spawned reads growth None -> UNMEASURED.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
LPS = "RimMandrake.LuminousPigment.LuminousPigmentSettings"
ITEM = "GLOW_TANK_LIQUID_FEED_1"
LIQ = {"S": "RM_Liquid_SaltWater", "F": "RM_Liquid_FreshWater", "B": "RM_Liquid_Brine"}
DRAW = 2000
PIN_C = 22.0          # inside crowncarpet's optimal band (default PlantProperties 6-42 C)
CHUNK = 1000          # ticks between pins: a 32-cell room with 4 open drifts ~18% of the way to ambient per chunk
MIN_GROW_C = 0.0      # crowncarpet's minGrowthTemperature (PlantProperties default): a pin found at or under it is a SITE miss
GROWN = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*%\s*grown\b", re.I)
NO_SEASON = "cannot grow"


def grown_fraction(lines):
    """The plant inspect's 'N% grown' lines as fractions; 'Growth rate: 71%' and the rest are not growth."""
    out = []
    for ln in lines or []:
        m = GROWN.match(ln or "")
        if m:
            out.append(float(m.group(1)) / 100.0)
    return out


def room_rect(ox, z):
    """The scene's room: walls on x ox..ox+9, z z-2..z+3; interior 8x4 = 32 cells holds battery, conduits, glow tank, tank."""
    return (ox, z - 2, 10, 6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="60,150")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=60000)
    ap.add_argument("--max-seconds", type=int, default=0,
                    help="wall-clock cap on the whole run (0 = none). The day stepped at ~60 ticks/s needs ~1000 s, past the "
                         "live lane's 600 s default; relentless_live.proof_budget reads this flag and allows S + 120 s, so a run "
                         "that outruns S stops itself and reads UNMEASURED instead of being killed mid-day "
                         "(GAMEENV_FIX_HARNESS_EEE35FD9_ITEMS_WAIT)")
    a = ap.parse_args()
    deadline = time.time() + a.max_seconds if a.max_seconds > 0 else None
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "glow_tank_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "glow_tank_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-30s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:500]), flush=True)
        save()

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    pins = []

    def pin():
        """Hold every scene's room at PIN_C; a refused set (no room), or a room found at or under MIN_GROW_C when the
        pin came (it cooled out of season between pins: temperatureBefore), is recorded and judged at the crop row."""
        rnd = len(pins) // max(1, len(sc))
        for name, s in sc.items():
            if s.get("batId"):          # a whole day at 180 W would spend much of the battery: top it up with the pin
                B.call("jawa/battery_set", thing=s["batId"], mode="setPct", value=1.0)
            r = B.call("jawa/room_heat", x=s["pinCell"][0], z=s["pinCell"][1], mode="set", value=PIN_C) or {}
            pins.append({"scene": name, "round": rnd, "ok": bool(r.get("success")), "before": r.get("temperatureBefore"),
                         "after": r.get("temperatureAfter"), "msg": None if r.get("success") else str(r)[:160]})

    def step_pinned(n):
        """-> False when the --max-seconds wall stopped the stepping short (the caller reads that as UNMEASURED)."""
        left = n
        while left > 0:
            if deadline is not None and time.time() > deadline:
                res["stoppedEarly"] = {"ticksLeft": left, "of": n, "maxSeconds": a.max_seconds}
                return False
            pin()
            k = min(CHUNK, left)
            step(k)
            left -= k
        return True

    ox, oz = (int(v) for v in a.origin.split(","))
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("GLOWTANK_SALT_DRAWN_ONE_UNIT", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    rect = (ox, oz, 12, 32)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "glowtank_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("GLOWTANK_SALT_DRAWN_ONE_UNIT", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    sc = {}
    for k, name in enumerate(("S", "F", "B")):
        z = oz + 2 + 10 * k
        gt, bat, cond, tank = (ox + 4, z), (ox + 1, z), (ox + 2, z), (ox + 6, z)
        room = B.call("jawa/make_empty_room", rect="%d,%d,%d,%d" % room_rect(ox, z), stuffDef="Steel") or {}
        sky = B.call("jawa/set_roof_batch", ops="None:%d,%d,2,2" % gt) or {}
        bb = B.call("jawa/build_batch", ops="RM_GlowTank:%d,%d;Battery:%d,%d;PowerConduit:%d,%d;PowerConduit:%d,%d;RM_LiquidTank:%d,%d"
                    % (gt + bat + cond + (ox + 3, z) + tank), faction="player", wipeExisting=False) or {}
        sc[name] = dict(gt=gt, bat=bat, tank=tank, pinCell=(ox + 2, z - 1), build=str(bb)[:200], room=str(room)[:160], sky=str(sky)[:160],
                        roomOk=bool(room.get("success")) and bool(sky.get("success")))
    step(2)
    for name, s in sc.items():
        lt = (B.call("jawa/list_things", defName="RM_GlowTank", rect="%d,%d,3,3" % (s["gt"][0] - 1, s["gt"][1] - 1), limit=2) or {}).get("things") or []
        s["gid"] = lt[0]["id"] if lt else None
        bt = (B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % s["bat"], limit=2) or {}).get("things") or [{}]
        s["batId"] = bt[0].get("id")
        if bt[0].get("id"):
            B.call("jawa/battery_set", thing=bt[0]["id"], mode="setPct", value=1.0)
        if s["gid"]:
            s["refuel"] = str(B.call("jawa/thing_refuel", thingId=s["gid"], amount=1) or {})[:160]
        B.hp("filltank:%d,%d=%s,%d" % (s["tank"] + (LIQ[name], 10 * DRAW)))
        s["units0"] = B.hp("tank:%d,%d" % s["tank"]).get("units")
    # the crop: four squares of the grower (its footprint read from the plant op on the glow tank's rect)
    for name, s in sc.items():
        g = s["gt"]
        # a 2x2 at Position covers Position..Position+(1,1)
        s["plant"] = str(B.call("jawa/set_plants", ops="RM_CrowncarpetCultured:%d,%d,2,2" % (g[0], g[1]), growth=0.10) or {})[:200]
    if not all(s.get("gid") for s in sc.values()):
        row("GLOWTANK_SALT_DRAWN_ONE_UNIT", "UNMEASURED", "SITE", {"why": "a glow tank did not stand", "scenes": sc})
        return 2
    if not all(s.get("roomOk") for s in sc.values()):
        row("GLOWTANK_SALT_DRAWN_ONE_UNIT", "UNMEASURED", "SITE", {"why": "a scene's room or its open sky did not build", "scenes": sc})
        return 2

    def inspect(s):
        ins = B.call("jawa/inspect_string", thingIds=str(s["gid"])) or {}
        return [ln for t in (ins.get("things") or []) for ln in (t.get("inspect") or [])]

    def growth(s):
        g = s["gt"]
        lt = (B.call("jawa/list_things", defName="RM_CrowncarpetCultured", rect="%d,%d,4,4" % (g[0] - 2, g[1] - 2), limit=8) or {}).get("things") or []
        ids = ",".join(t["id"] for t in lt)
        if not ids:
            return None
        ins = B.call("jawa/inspect_string", thingIds=ids) or {}
        vals = grown_fraction([ln for t in (ins.get("things") or []) for ln in (t.get("inspect") or [])])
        return (sum(vals) / len(vals)) if vals else None
    step_pinned(500)
    for name, s in sc.items():
        s["units1"] = B.hp("tank:%d,%d" % s["tank"]).get("units")
        s["inspect1"] = inspect(s)
        s["growth1"] = growth(s)
    S, F, Bb = sc["S"], sc["F"], sc["B"]
    if None in (S["units0"], S["units1"], F["units0"], F["units1"], Bb["units0"], Bb["units1"]):     # an unreadable tank is not a tank that lost nothing
        row("GLOWTANK_SALT_DRAWN_ONE_UNIT", "UNMEASURED", "HARNESS", {"why": "a tank's units were unreadable", "scenes": sc})
        return 2
    drawS = S["units0"] - S["units1"]
    salt_line = any("salt water" in ln for ln in S["inspect1"])
    dry_f = any(ln.startswith("Dry") for ln in F["inspect1"]) and F["units0"] == F["units1"]
    dry_b = any(ln.startswith("Dry") for ln in Bb["inspect1"]) and Bb["units0"] == Bb["units1"]
    row("GLOWTANK_SALT_DRAWN_ONE_UNIT", "PASS" if drawS == DRAW and salt_line and dry_f and dry_b else "FAIL", "MOD",
        {"saltDrawn": drawS, "saltInspect": S["inspect1"], "fresh": [F["units0"], F["units1"], F["inspect1"]],
         "brine": [Bb["units0"], Bb["units1"], Bb["inspect1"]]})
    day_whole = step_pinned(a.ticks)
    for name, s in sc.items():          # read BEFORE any re-pin: a pin would hide a room that cooled out of season
        s["growth2"] = growth(s)
        s["units2"] = B.hp("tank:%d,%d" % s["tank"]).get("units")
        s["inspect2"] = inspect(s)
    pin()                               # the closing pin reads how cold each room got over the last chunk
    cold = [p for p in pins if p["ok"] and p["round"] > 0 and (p["before"] is None or float(p["before"]) <= MIN_GROW_C)]
    res["pins"] = {"count": len(pins), "refused": [p for p in pins if not p["ok"]][:6], "cold": cold[:6],
                   "minBefore": min([float(p["before"]) for p in pins if p["ok"] and p["round"] > 0 and p["before"] is not None] or [None]),
                   "last": pins[-3:]}
    off_season = [n for n in ("S", "F") if any(NO_SEASON in ln.lower() for ln in sc[n]["inspect2"]) or not sc[n]["inspect2"]]
    gS = (S["growth2"] or 0) - (S["growth1"] or 0) if S["growth1"] is not None and S["growth2"] is not None else None
    gF = (F["growth2"] or 0) - (F["growth1"] or 0) if F["growth1"] is not None and F["growth2"] is not None else None
    if not day_whole:
        row("GLOWTANK_SALT_CROP_GROWS", "UNMEASURED", "HARNESS", {"why": "UNMEASURED: the day outran --max-seconds %d" % a.max_seconds,
                                                                  "stoppedEarly": res.get("stoppedEarly")})
    elif res["pins"]["refused"] or res["pins"]["cold"] or off_season:
        row("GLOWTANK_SALT_CROP_GROWS", "UNMEASURED", "SITE", {"why": "the growing-season pin did not hold", "offSeason": off_season,
                                                              "pins": res["pins"], "S": S.get("inspect2"), "F": F.get("inspect2")})
    elif gS is None or gF is None:
        row("GLOWTANK_SALT_CROP_GROWS", "UNMEASURED", "HARNESS", {"why": "crop growth unreadable", "S": [S.get("growth1"), S.get("growth2")],
                                                              "F": [F.get("growth1"), F.get("growth2")], "plant": S.get("plant")})
    else:
        row("GLOWTANK_SALT_CROP_GROWS", "PASS" if gS > gF and gS > 0 else "FAIL", "MOD",
            {"saltGrowth": [S["growth1"], S["growth2"]], "freshGrowth": [F["growth1"], F["growth2"]], "saltUnits": [S["units0"], S["units1"], S["units2"]],
             "pins": res["pins"]["count"], "pinLast": res["pins"]["last"]})
    w0 = (B.call("jawa/mod_settings_field", typeName=LPS, action="get", field="tankNeedsWater") or {}).get("value")
    B.call("jawa/mod_settings_field", typeName=LPS, action="set", field="tankNeedsWater", value="False")
    try:
        off = inspect(S)
    finally:      # `w0 or "True"` turned an original False into True
        B.call("jawa/mod_settings_field", typeName=LPS, action="set", field="tankNeedsWater", value="True" if w0 is None else str(w0))
    has_line = any(("Ocean water" in ln) or ln.startswith("Dry") for ln in off)
    row("GLOWTANK_SETTING_OFF_NO_LINE", "PASS" if not has_line else "FAIL", "MOD", {"inspectOff": off, "restoredTo": w0})
    res["scenes"] = sc
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return verdict(rows)


def verdict(rows):
    """Exit 0 = every row PASS, 1 = a FAIL, 2 = no FAIL but a row UNMEASURED (lightspeed-authoring: 2 is UNMEASURED)."""
    st = [r["status"] for r in rows]
    if st and all(x == "PASS" for x in st):
        return 0
    return 1 if "FAIL" in st else 2


if __name__ == "__main__":
    sys.exit(main())
