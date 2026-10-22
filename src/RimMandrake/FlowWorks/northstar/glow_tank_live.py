"""GLOW TANK WATER live check (GLOW_TANK_LIQUID_FEED_1 A2 + A3, LuminousPigment LP-2 on a FlowWorks tank; BENCH belt
2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/glow_tank_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N]

Three identical scenes 10 squares apart: an RM_GlowTank (2x2) powered by a charged Battery over a PowerConduit, seeded
(jawa/thing_refuel 1 = the crowncarpet culture), RM_CrowncarpetCultured planted in its four squares at growth 0.10, and an
RM_LiquidTank touching it holding 10 draws of SALT water (scene S), FRESH water (scene F) or BRINE (scene B).
Rows:
  GLOWTANK_SALT_DRAWN_ONE_UNIT   EXPECT within 500 ticks S's tank lost exactly one draw (200 L = 2000 dL) and the glow tank
                                 reads "Ocean water: ... (salt water)"; F's and B's tanks lost nothing and read "Dry".
  GLOWTANK_SALT_CROP_GROWS       EXPECT over --ticks (default 6000) S's crop grew more than F's (F is parched: growth paused).
  GLOWTANK_SETTING_OFF_NO_LINE   EXPECT with LuminousPigmentSettings.tankNeedsWater off the inspect has no water line
                                 (restored after).
LIES  an unpowered tank grows nothing either (the battery is read charged and the inspect shows no 'needs power'); a plant
      that never spawned reads growth None -> UNMEASURED.
"""
import argparse
import json
import os
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="60,150")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=6000)
    a = ap.parse_args()
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
        bb = B.call("jawa/build_batch", ops="RM_GlowTank:%d,%d;Battery:%d,%d;PowerConduit:%d,%d;PowerConduit:%d,%d;RM_LiquidTank:%d,%d"
                    % (gt + bat + cond + (ox + 3, z) + tank), faction="player", wipeExisting=False) or {}
        sc[name] = dict(gt=gt, bat=bat, tank=tank, build=str(bb)[:200])
    step(2)
    for name, s in sc.items():
        lt = (B.call("jawa/list_things", defName="RM_GlowTank", rect="%d,%d,3,3" % (s["gt"][0] - 1, s["gt"][1] - 1), limit=2) or {}).get("things") or []
        s["gid"] = lt[0]["id"] if lt else None
        bt = (B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % s["bat"], limit=2) or {}).get("things") or [{}]
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
        vals = []
        for t in ins.get("things") or []:
            for ln in t.get("inspect") or []:
                if ln.lower().startswith("growth"):
                    try:
                        vals.append(float(ln.split(":")[1].strip().rstrip("%")) / 100.0)
                    except (IndexError, ValueError):
                        pass
        return (sum(vals) / len(vals)) if vals else None
    step(500)
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
    step(a.ticks)
    for name, s in sc.items():
        s["growth2"] = growth(s)
        s["units2"] = B.hp("tank:%d,%d" % s["tank"]).get("units")
    gS = (S["growth2"] or 0) - (S["growth1"] or 0) if S["growth1"] is not None and S["growth2"] is not None else None
    gF = (F["growth2"] or 0) - (F["growth1"] or 0) if F["growth1"] is not None and F["growth2"] is not None else None
    if gS is None or gF is None:
        row("GLOWTANK_SALT_CROP_GROWS", "UNMEASURED", "SITE", {"why": "crop growth unreadable", "S": [S.get("growth1"), S.get("growth2")],
                                                              "F": [F.get("growth1"), F.get("growth2")], "plant": S.get("plant")})
    else:
        row("GLOWTANK_SALT_CROP_GROWS", "PASS" if gS > gF and gS > 0 else "FAIL", "MOD",
            {"saltGrowth": [S["growth1"], S["growth2"]], "freshGrowth": [F["growth1"], F["growth2"]], "saltUnits": [S["units0"], S["units1"], S["units2"]]})
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
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
