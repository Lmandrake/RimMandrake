"""validation_hose.py -- FlowWorks flexible hoses (moved from Gimme Some Slack L6 at the hose port, 2026-10-11): functional script.

Design: design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 3 (3.12 northstar angle).
Owner, 2026-10-02: "The flexible water hoses should be much thicker and stiffer than the wires, much like the fire
hoses they use. And they SHOULD "plump up" when water is flowing through them and "collapse down" when it's not."
Offline half: the Verse-free Source/Hose/HoseMath.cs is checked by the C# SelfTest (HoseSelfTest.cs, run by
validation.py's O3 row: widths, the state machine + hysteresis + a no-hysteresis negative control, wobble, lay
bend radius incl. round a wall, install validity, the pump rule, tints). State is read through
RimMandrake.FlowWorks.Hose.HoseProbe (jawa/mod_settings_field), never from screenshots. The bridge plumbing is the
mod-neutral src/RimMandrake/Utils/validation_core.py (no Gimme Some Slack import); the C# SelfTest is FlowWorks'
(python3 src/RimMandrake/Utils/selftest_flowworks_stock.py, the "hose:" suites).

    python.exe validation_hose.py --live                   # on the current map (after validation.py --live)
    python.exe validation_hose.py --save-load NAME         # H10: hose, its end and its state survive save/load
    python.exe validation_hose.py --removal-check NAME     # H11: a save WITH a laid hose on a tier WITHOUT the mod
    python.exe validation_hose.py --maze                   # M1-M6 + P1-P2: path solving in a spiral maze, reel ports
    python.exe validation_hose.py --relay                  # RL1-RL9 (round 6): a chain of relay reels past one hose's reach
    python.exe validation_hose.py --carry                  # CR1-CR7 (carry S3/S5): a real colonist deploys, drops, resumes, retracts

The maze walk (owner, round 2, 2026-10-04: "make the hose solve a complex path (like a spiral through a simple maze
with two options, then 'build' a wall to block the obvious solution so we can see if it changes to go the other way...
or what happens)"). One scene, six rows, each a state read; the SAME maze is solved offline by HoseSelfTest.Maze
(MAZE below must stay identical to HoseSelfTest.MazeRows). Predictions from the code, to be confirmed or killed live:
  * M2: walling the gap re-plans from scratch at the reel's next 250-tick corridor check -> the 3/4 spiral, ~2x longer.
  * M3: the length cap is enforced on a re-plan too (HOSE_BLOCKED_REROUTE_RETRACT_1): an obstacle change across a laid hose
    whose remaining route is longer than the cap RETRACTS it (laid false, retractReason "route too long"). The cap itself
    changing does not move the corridor hash, so M3b adds a harmless filler wall inside the corridor box to trigger the check.
  * M4: no route left -> the hose is RETRACTED (laid false, retractReason "no route"), never a laid-but-invisible ghost.
  * M5: the hose was reeled in, so it is laid again first; with the walls removed it takes the short route.
The reel is 2x2 (round 3): Position = its south-west cell, footprint x..x+1 / z..z+1, the hose leaves its centre. Every
reel below is placed so that footprint holds no wall, pipe, tank, other reel or free end.

The flow signal in these rows is the DEBUG provider (HoseProbe "flow:"), so they test the hose's look and timing alone.
Real flow (hose port step 6) is the "net" provider: a lease every successful transfer through the hose extends; the census
reports it per hose (flowUntil, tintLiquid, credits, netLink). The real-flow bars (NS_hose_*) run in northstar/proof_hose.py.

LEARNED (seed; each line is a check below):
  * A hose wrapped round an obstacle corner bends at about its clearance from the corner (SelfTest measured 1.03
    at clearance 0.10); the scene puts a wall across the hose so H4 measures the bend radius where it is hardest.
  * Hysteresis is asserted both ways: a toggle every 40 ticks for 1200 ticks never drains (H7), AND a plump hose
    still reads Plump 400 ticks after flow stops (H8a), then Flat after the release window (H8b).
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS_DIR = os.path.join(os.path.dirname(HERE), "Utils")
for _p in (HERE, UTILS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import validation_core as V  # noqa: E402

MOD = "FlowWorks"
PKG = "mandrake.rm.flowworks"
TIER = "flowworks"
HPROBE = "RimMandrake.FlowWorks.Hose.HoseProbe"
HX0, HZ0 = 40, 60
# 2026-10-10: 10 cells west of the reels, not 4: staged West, their hoses left the west nozzle straight and U-turned east
# (owner card 2026-10-06); H9 sets the minimum bend to 2 (lead-out 5.6 + a 4-cell-wide turn), which ran onto unprepared
# ground. The reels face East (their ends) since VALIDATION_HOSE_REELS_FIX_STILL_WEST; the margin is kept.
SITE = (HX0 - 10, HZ0 - 2, 44, 20)
R1, F1 = (HX0 + 2, HZ0 + 6), (HX0 + 26, HZ0 + 6)        # main hose, 24 cells, across a wall
WALL = [(HX0 + 13, z) for z in range(HZ0 + 2, HZ0 + 9)]  # the hose must go round its north end
R2, F2 = (HX0 + 2, HZ0 + 14), (HX0 + 20, HZ0 + 14)       # flicker hose, open floor
SHOT = (HX0, HZ0 + 1, 30, 16)
SHOTS = os.path.join(V.REPO, "Transient", "messy_conduit_live_20261002")
WIRE_RATIO_MIN = 4.0


class H(V.Bridge):
    probe_type = HPROBE

    def hp(self, cmd, wait_s=20.0):
        before = self.call("jawa/mod_settings_field", typeName=HPROBE, action="get", field="serial").get("value")
        s = self.call("jawa/mod_settings_field", typeName=HPROBE, action="set", field="request", value=cmd)
        if not s.get("success"):
            return {"success": False, "error": "hose probe set failed", "raw": s}
        t0 = time.time()
        while time.time() - t0 < wait_s:
            now = self.call("jawa/mod_settings_field", typeName=HPROBE, action="get", field="serial").get("value")
            if now != before:
                res = self.call("jawa/mod_settings_field", typeName=HPROBE, action="get", field="result").get("value")
                try:
                    return json.loads(res)
                except Exception:  # noqa: BLE001
                    return {"success": False, "raw": res}
            time.sleep(0.25)
        return {"success": False, "error": "hose probe timed out (no frame serviced it)"}

    def shot_rect(self, name, rect):
        global SHOT
        keep, SHOT = SHOT, rect
        try:
            return self.shot(name)
        finally:
            SHOT = keep

    def hose(self, reel):
        c = self.hp("census")
        for h in c.get("hoses") or []:
            if V.reel_at(h["reel"], reel):
                return h, c
        return {}, c

    def shot(self, name):
        self.call("jawa/clear_ui", all=True)
        self.call("rimworld/frame_cell_rect", x=SHOT[0], z=SHOT[1], width=SHOT[2], height=SHOT[3], paddingCells=1)
        time.sleep(2.0)
        r = self.call("jawa/take_screenshot", fileName=name)
        src = r.get("filePath")
        for _ in range(10):
            if src and os.path.exists(src):
                break
            time.sleep(0.5)
        try:
            os.makedirs(SHOTS, exist_ok=True)
            dst = os.path.join(SHOTS, name + ".png")
            shutil.copyfile(src, dst)
            return dst
        except Exception as ex:  # noqa: BLE001
            return "copy failed: %s (%s)" % (ex, src)


def _pick(h, *keys):
    return {k: h.get(k) for k in keys}


def run_live(args):
    B = H()
    rows, log = [], []
    res = {"mod": MOD, "mode": "live", "script": "validation_hose.py", "tier": TIER,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "screenshots": []}
    try:
        sys.path.insert(0, os.path.join(V.UTILS, "modcheck"))
        import status as _mc  # noqa: E402
        res["mod_hash"] = _mc.mod_hash(HERE)
    except Exception as ex:  # noqa: BLE001
        res["mod_hash"] = None
        log.append("mod_hash unavailable: %s" % ex)
    lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    log_base = max([x.get("Sequence", 0) for x in lg0.get("logs") or []] or [0])
    d = B.hp("defaults")
    if not d.get("success"):
        V.row(rows, "H0_probe_channel", "FAIL", "HARNESS", d)
        res["aborted"] = "hose probe dead"
        return res
    V.hrow(rows, "H0_probe_channel", "PASS", "HARNESS", "defaults applied")

    # ---------------------------------------------------------------- scene
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % SITE)
    bw = B.call("jawa/build_batch", ops=V.ops("Wall", WALL), stuff="Steel", faction="player")
    # VALIDATION_HOSE_REELS_FIX_STILL_WEST: each reel faces its hose's free end (East), as the proofs do since 3fa1dc487d
    br = B.call("jawa/build_batch", ops=";".join([V.reel_toward(R1, F1), V.reel_toward(R2, F2)]), faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(2)
    h1, c = B.hose(R1)
    h2, _ = B.hose(R2)
    V.hrow(rows, "H1_reels_built", "PASS" if h1 and h2 else "FAIL", "MOD" if br.get("success") else "SITE",
          {"reels": len(c.get("hoses") or []), "build": br.get("success"), "walls": bw.get("success"), "textures": c.get("texturesInstalled")})
    if not (h1 and h2):
        res["aborted"] = "reels missing"
        res["log"] = log
        return res

    # install validity (refusals are state reads, no hose laid)
    far = B.hp("check:%d,%d,%d,%d" % (R1 + (R1[0] + 60, R1[1])))
    blk = B.hp("check:%d,%d,%d,%d" % (R1 + WALL[2]))
    okc = B.hp("check:%d,%d,%d,%d" % (R1 + F1))
    V.row(rows, "H1b_install_validity", "PASS" if far.get("reason") in ("too far", "out of bounds") and blk.get("reason") == "target blocked"
          and okc.get("reason") is None else "FAIL", "MOD", {"far": far.get("reason"), "wall": blk.get("reason"), "ok": okc.get("reason")})

    l1 = B.hp("lay:%d,%d,%d,%d" % (R1 + F1))
    l2 = B.hp("lay:%d,%d,%d,%d" % (R2 + F2))
    B.ticks(2)
    h1, c = B.hose(R1)
    h2, _ = B.hose(R2)
    ok2 = l1.get("success") and l2.get("success") and h1.get("kind") == "Hose" and h1.get("layOk") and h2.get("layOk") \
        and h1.get("unwalkablePoints") == 0 and not h1.get("selfIntersects") and (h1.get("couplings") or 0) >= 2
    V.row(rows, "H2_hose_laid_as_hose_cord", "PASS" if ok2 else "FAIL", "MOD",
          dict(_pick(h1, "kind", "layOk", "pathLen", "flatLen", "plumpLen", "straight", "points", "couplings", "fellBack",
                     "unwalkablePoints", "selfIntersects", "geometryHash"), lay1=l1.get("reason"), lay2=l2.get("reason"),
               lastLayMs=c.get("lastLayMs")))
    # H3 (width >= 4x wire) and H4 (bend radius >= 0.95 x setting) are CUT (consolidation doc section 2 "Matrix hose 9"):
    # every MX_H00-H08 scene asserts the same predicates (run_live.hose_compare width_over_wire_ge / min_bend_radius_ge) on
    # a superset of shapes (straight / corner round a wall / water, 6/14/24 cells, flat / plump / filling).

    # ---------------------------------------------------------------- flat while nothing flows
    # H5 (flat while nothing flows) is CUT: MX_H Flat scenes assert state Flat + blend 0 on three shapes (doc section 2).
    # The 300 settle ticks stay: H6 reads "plump is wider and shorter than flat" against this flat pose.
    B.ticks(300)
    h1, _ = B.hose(R1)
    res["screenshots"].append(B.shot("hose_01_flat"))
    flat_ratio = h1.get("widthOverWire")
    flat_len = h1.get("poseLen")

    # ---------------------------------------------------------------- plump after the provider says flowing
    B.hp("flow:%d,%d=on" % R1)
    tt = c.get("transitionTicks") or 30
    B.ticks(max(1, tt // 2))
    hm, _ = B.hose(R1)
    B.ticks(tt)
    h1, _ = B.hose(R1)
    ok6 = hm.get("state") == "Filling" and 0.2 < (hm.get("blend") or 0) < 0.8 and h1.get("state") == "Plump" and h1.get("blend") == 1 \
        and (h1.get("widthOverWire") or 0) > (flat_ratio or 99) and (h1.get("poseLen") or 99) < (flat_len or 0)
    V.row(rows, "H6_plump_within_transition", "PASS" if ok6 else "FAIL", "MOD",
          {"mid": _pick(hm, "state", "blend", "wobbling"), "after": _pick(h1, "state", "blend", "widthOverWire", "poseLen", "history"),
           "flat": {"widthOverWire": flat_ratio, "poseLen": flat_len}, "transitionTicks": tt})
    res["screenshots"].append(B.shot("hose_02_plump"))

    # ---------------------------------------------------------------- no flicker when the signal toggles fast
    B.hp("clearhist:%d,%d" % R2)
    on = False
    for _ in range(30):
        on = not on
        B.hp("flow:%d,%d=%s" % (R2 + ("on" if on else "off",)))
        B.ticks(40)
    h2, _ = B.hose(R2)
    states = [s for _, s in h2.get("history") or []]
    ok7 = h2.get("state") == "Plump" and states == ["Filling", "Plump"] and "Draining" not in states
    V.row(rows, "H7_no_flicker_fast_toggle", "PASS" if ok7 else "FAIL", "MOD",
          {"toggles": 30, "every": 40, "history": h2.get("history"), "state": h2.get("state"), "transitions": h2.get("transitions")})
    B.hp("flow:%d,%d=off" % R2)

    # ---------------------------------------------------------------- release only after the hysteresis window
    B.hp("flow:%d,%d=off" % R1)
    B.ticks(400)
    ha, _ = B.hose(R1)
    B.ticks(800)
    hb, _ = B.hose(R1)
    V.row(rows, "H8_collapse_after_release", "PASS" if ha.get("state") == "Plump" and hb.get("state") == "Flat" else "FAIL", "MOD",
          {"after400": _pick(ha, "state", "blend"), "after1200": _pick(hb, "state", "blend", "history"),
           "releaseTicks": c.get("releaseTicks"), "minPlumpDwell": c.get("minPlumpDwell")})

    # ---------------------------------------------------------------- stiffness setting re-lays
    B.hp("set:minBendRadius=2")
    B.ticks(1)
    hs, _ = B.hose(R2)
    B.hp("defaults")
    B.ticks(1)
    hd, _ = B.hose(R2)
    # both hashes must be READ: a failed default-pose read (None) is not "the shape moved"
    V.row(rows, "H9_stiffness_setting", "PASS" if (hs.get("minBendFlat") or 0) >= 1.9 and None not in (hs.get("geometryHash"), hd.get("geometryHash"))
          and hs.get("geometryHash") != hd.get("geometryHash") else "FAIL", "MOD",
          {"minBend2": hs.get("minBendFlat"), "hash2": hs.get("geometryHash"), "hashDefault": hd.get("geometryHash")})

    # ---------------------------------------------------------------- log budget
    lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > log_base]
    errs_all = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
    # the scene clear's own destroy_batch over a map geyser logs "Tried to destroy non-destroyable thing": harness, not the mod
    site = [e for e in errs_all if "non-destroyable" in str(e.get("Message", ""))]
    errs = [e for e in errs_all if e not in site]
    if not V.SHARED:                 # SHARED: proof_all's one run-end Z (doc section 2 "Log budget")
        # an unreadable log (no "logs" list) is ignorance, never a clean budget
        V.row(rows, "HZ_log_budget", "UNMEASURED" if not isinstance(lg.get("logs"), list) else "PASS" if not errs else "FAIL", "MOD",
              {"errors": [str(e.get("Message", ""))[:240] for e in errs[:8]], "newWarnings": len(new), "siteClearErrors": len(site)})
    # leave hose 1 plump for the save-load mode (state must survive)
    B.hp("flow:%d,%d=on" % R1)
    B.ticks(tt + 5)
    res["log"] = log
    return res


# ============================================================================ M / P: maze path solving and reel ports
# Rows from high z to low z; R reel, T free end, g the short route's gap, b a cell on the long spiral route.
# Redrawn 2026-10-10 (GSS_HOSE_LAY_DIAGNOSE_FIFTEEN_NEW_REDS): the owner's straight lead-out ruling (question card
# 2026-10-06: a 2x2 reel's hose leaves its WEST nozzle dead straight, refused rather than laid without it, never bending under
# the 1.2 minimum radius) made the old maze unlayable -- its reel sat 3 cells from the west wall in a 3-row chamber, so the
# short route needed a 2.5-cell-wide U-turn and the spiral a 1.26-radius turn into a 1-cell corridor. Now the reel faces a
# 9-cell straight run west and BOTH options leave that way: straight on through the gap g to T (~12), or up the b corridor,
# west along the top and down to T (~23, the spiral). Same two-option walk, same rows.
MAZE = [
    "#######             ",
    "#.....#             ",
    "#.###b#             ",
    "#.###.#             ",
    "#.###.##############",
    "#.###..............#",
    "#.Tg..........R....#",
    "#####..............#",
    "    ################",
]
MX0, MZ0 = 40, 84
MSITE = (MX0 - 3, MZ0 - 3, 26, 22)
# 2x2 reel at PREEL (cells x..x+1, z..z+1) and a 2x2 tank at PTANK: PTANK = PREEL + (2, 0) shares the reel's EAST edge (two cells).
# PLONE is a second 2x2 reel 10 cells from the tank, touching nothing. The maze reel R (marker 'R') is a 2x2 at its marker
# cell + (0..1, 0..1): (MX0+14..15, MZ0+2..3) lies wholly on '.' chamber cells (rows MZ0+2 and MZ0+3, x 14 and 15).
PREEL, PTANK, PLONE = (MX0 + 2, MZ0 + 12), (MX0 + 4, MZ0 + 12), (MX0 + 12, MZ0 + 12)
FILLER = (MX0 + 9, MZ0 + 1)   # a chamber cell (bottom row) clear of both routes (M3b obstacle change that triggers the 250-tick check)
MAZE_LEN = 40                 # hose length used for M1/M2/M4/M5: the spiral is ~23 taut (x1.05 margin ~24), well inside
RELAY_TICKS = 300  # > the 250-tick corridor check


def maze_cells():
    walls, mark = [], {}
    for i, rowtxt in enumerate(MAZE):
        z = MZ0 + len(MAZE) - 1 - i
        for x, ch in enumerate(rowtxt):
            c = (MX0 + x, z)
            if ch == "#":
                walls.append(c)
            elif ch in "RTgb":
                mark[ch] = c
    return walls, mark


def _via(h, cell):
    return list(cell) in (h.get("centreCells") or [])


def run_maze(args):
    B = H()
    rows, log = [], []
    res = {"mod": MOD, "mode": "maze", "script": "validation_hose.py", "tier": TIER,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "screenshots": []}
    d = B.hp("defaults")
    if not d.get("success"):
        V.row(rows, "M0_probe_channel", "FAIL", "HARNESS", d)
        res["aborted"] = "hose probe dead"
        return res
    B.hp("set:maxLength=%d" % MAZE_LEN)
    walls, m = maze_cells()
    R, T, g, b = m["R"], m["T"], m["g"], m["b"]
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % MSITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % MSITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % MSITE)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % MSITE)
    bw = B.call("jawa/build_batch", ops=V.ops("Wall", walls), stuff="Steel", faction="player")
    # VALIDATION_HOSE_REELS_FIX_STILL_WEST: R faces its free end T (West, as before); PREEL and PLONE lay no hose (port rows only)
    # and keep West, PREEL's back (East) edge on the tank
    br = B.call("jawa/build_batch", ops=";".join([V.reel_toward(R, T), V.reel_toward(PREEL, None), V.reel_toward(PLONE, None)]),
                faction="player", wipeExisting=False)
    bt = B.call("jawa/build_batch", ops=V.ops("RM_LiquidTank", [PTANK]), faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(2)

    # M1: both routes open -> the obvious one, through the gap
    l1 = B.hp("lay:%d,%d,%d,%d" % (R + T))
    B.ticks(2)
    h1, c = B.hose(R)
    ok1 = l1.get("success") and h1.get("layOk") and _via(h1, g) and (h1.get("unwalkablePoints") == 0)
    V.row(rows, "M1_open_maze_short_route", "PASS" if ok1 else "FAIL", "MOD" if bw.get("success") and br.get("success") else "SITE",
          dict(_pick(h1, "layOk", "pathLen", "bbox", "fellBack", "minBendFlat", "unwalkablePoints"), lay=l1.get("reason"), viaGap=_via(h1, g)))
    res["screenshots"].append(B.shot_rect("maze_01_open", MSITE))

    # M2: wall the gap -> does it go the other way?
    B.call("jawa/build_batch", ops=V.ops("Wall", [g]), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(RELAY_TICKS)
    h2, c2 = B.hose(R)
    top = MZ0 + len(MAZE) - 2
    rerouted = h2.get("layOk") and not _via(h2, g) and (h2.get("bbox") or [0, 0, 0, 0])[3] >= top
    V.row(rows, "M2_gap_walled_reroutes", "PASS" if rerouted and (h2.get("pathLen") or 0) > 1.6 * (h1.get("pathLen") or 99) else "FAIL", "MOD",
          dict(_pick(h2, "laid", "layOk", "pathLen", "bbox", "fellBack", "minBendFlat", "unwalkablePoints", "selfIntersects"),
               relays=(c2.get("relays") or 0) - (c.get("relays") or 0), before=h1.get("pathLen")))
    res["screenshots"].append(B.shot_rect("maze_02_gap_walled", MSITE))

    # M3: length cap. Install refuses the spiral for a 20-cell hose; a filler wall inside the corridor box then makes the
    # reel re-check the laid hose (the corridor hash moved, the route is unchanged but now over the cap) -> it retracts
    B.hp("set:maxLength=20")
    chk = B.hp("check:%d,%d,%d,%d" % (R + T))
    B.call("jawa/build_batch", ops=V.ops("Wall", [FILLER]), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(RELAY_TICKS)
    h3, c3 = B.hose(R)
    V.row(rows, "M3_length_cap_install", "PASS" if chk.get("reason") == "route too long" else "FAIL", "MOD",
          {"reason": chk.get("reason"), "maxLength": h3.get("maxLength")})
    V.row(rows, "M3b_laid_hose_over_cap_retracts", "PASS" if h3.get("laid") is False and h3.get("retractReason") == "route too long" else "FAIL", "MOD",
          dict(_pick(h3, "laid", "layOk", "pathLen", "maxLength", "retractReason", "retractTick"), retracts=c3.get("retracts"),
               note="HOSE_BLOCKED_REROUTE_RETRACT_1: a re-plan enforces the cap; expected reeled in, reason 'route too long'"))
    B.hp("set:maxLength=%d" % MAZE_LEN)
    lr = B.hp("lay:%d,%d,%d,%d" % (R + T))      # M3b reeled it in: lay it again (the spiral, gap still walled)
    B.ticks(2)

    # M4: wall the spiral too -> unreachable -> the hose is reeled in with a reason (no ghost hose)
    B.call("jawa/build_batch", ops=V.ops("Wall", [b]), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(RELAY_TICKS)
    h4, c4 = B.hose(R)
    chk4 = B.hp("check:%d,%d,%d,%d" % (R + T))
    V.row(rows, "M4_unreachable_retracts", "PASS" if lr.get("success") and h4.get("laid") is False and h4.get("retractReason") == "no route"
          and chk4.get("reason") == "no route" else "FAIL", "MOD",
          dict(_pick(h4, "laid", "layOk", "state", "reelGraphic", "retractReason", "retractTick"), check=chk4.get("reason"),
               relay=lr.get("reason"), retracts=c4.get("retracts"),
               note="expected: reeled in at the next 250-tick check, retractReason 'no route'"))
    res["screenshots"].append(B.shot_rect("maze_04_unreachable", MSITE))

    # M5: walls removed -> lay it again; it takes the short route
    for cell in (g, b, FILLER):
        # "Building" (ThingCategory): "Buildings" is refused ("Not a ThingCategory") and removed nothing (live 2026-10-04)
        B.call("jawa/destroy_batch", rects="%d,%d,1,1" % cell, categories="Building")
    B.call("jawa/map_commit")
    # one tick: RM_MapComponent_Hoses.World() is cached per tick, and M4's check built it THIS tick with the walls standing
    B.ticks(2)
    l5 = B.hp("lay:%d,%d,%d,%d" % (R + T))
    B.ticks(RELAY_TICKS)
    h5, _ = B.hose(R)
    V.row(rows, "M5_walls_removed_recovers", "PASS" if l5.get("success") and h5.get("laid") and h5.get("layOk") and _via(h5, g) else "FAIL", "MOD",
          dict(_pick(h5, "laid", "layOk", "pathLen", "bbox"), lay=l5.get("reason")))

    # P1/P2: reel ports (owner, round 2: "the Hose Reel can also connect to ... pipe-friendly buildings (like tanks)")
    hp_, _ = B.hose(PREEL)
    hl, _ = B.hose(PLONE)
    # 2026-10-10: the feed-draw count is read NOW, not from M1's census: CompHoseReel.Port() caches its port for 60 ticks
    # (CompHoseReel.cs, `port`), and M1's census came 4 ticks after the tank was built in a later batch than the reels, so
    # it read the cached "no port" (P1 red 2026-10-10, first run with FlowWorks loaded). Hundreds of ticks have passed here.
    cp = B.hp("census")
    # build_batch answers success with placed 0 for an unknown def (FlowWorks absent on this tier, live 2026-10-04)
    if not bt.get("success") or not bt.get("placed"):
        V.row(rows, "P1_reel_couples_to_tank", "SKIP", "SITE", {"tankBuild": bt, "note": "RM_LiquidTank not buildable here (FlowWorks not loaded?)"})
    else:
        V.row(rows, "P1_reel_couples_to_tank", "PASS" if hp_.get("port") == "RM_LiquidTank" and hp_.get("portKind") == "Tank"
              and hp_.get("portSide") == [1, 0] and (cp.get("feedDraws") or 0) >= 1 else "FAIL", "MOD",
              dict(_pick(hp_, "port", "portKind", "portSide"), feedDraws=cp.get("feedDraws"), feedDrawsAtM1=c.get("feedDraws")))
    V.row(rows, "P2_lone_reel_not_coupled", "PASS" if hl and hl.get("port") is None else "FAIL", "MOD", _pick(hl, "port", "portKind"))
    res["screenshots"].append(B.shot_rect("ports_01_reel_tank", (PREEL[0] - 2, PREEL[1] - 2, 10, 6)))
    B.hp("defaults")
    res["log"] = log
    return res


# ============================================================================ H10 / H11
def _hose_set(c):
    return sorted((tuple(h["reel"]), tuple(h["far"]), h.get("end"), h.get("state"), h.get("laid"), h.get("debugFlowing"),
                   h.get("geometryHash"), h.get("transitions")) for h in c.get("hoses") or [])


def run_save_load(args):
    B = H()
    rows = []
    res = {"mod": MOD, "mode": "save-load", "script": "validation_hose.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    name = args.save_load
    B.call("rimworld/frame_cell_rect", x=SHOT[0], z=SHOT[1], width=SHOT[2], height=SHOT[3], paddingCells=1)
    B.ticks(2)
    ca = B.hp("census")
    if not any(h.get("laid") for h in ca.get("hoses") or []):
        V.row(rows, "H10_save_load_hose", "FAIL", "SITE", "no laid hose on the current map")
        return res
    before = V._saves_stat()
    if name + ".rws" in before:
        V.row(rows, "H10_save_load_hose", "FAIL", "HARNESS", "%s.rws exists" % name)
        return res
    B.call("rimworld/save_game", saveName=name)
    V._wait_saved(name)
    after = V._saves_stat()
    new = sorted(set(after) - set(before))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    ok_save = new == [name + ".rws"] and not changed
    V.row(rows, "H10a_save_landed_new_file_only", "PASS" if ok_save else "FAIL", "HARNESS", {"new": new, "changed": changed})
    if not ok_save:
        res["aborted"] = "save did not land as a new file only"
        return res
    with open(os.path.join(V.SAVES, name + ".rws"), "rb") as f:
        blob = f.read()
    hits = save_class_hits(blob)
    V.row(rows, "H10b_save_names_no_class", "PASS" if not hits["offending"] and hits["rmHoseState"] >= 1 else "FAIL", "MOD", hits)
    B.call("rimworld/load_game", saveName=name)
    ok, waited = V._wait_playing(B)
    if not ok:
        V.row(rows, "H10_save_load_hose", "FAIL", "SITE", {"state": waited})
        return res
    B.call("rimworld/frame_cell_rect", x=SHOT[0], z=SHOT[1], width=SHOT[2], height=SHOT[3], paddingCells=1)
    time.sleep(1.0)
    cb = B.hp("census")
    sa, sb = _hose_set(ca), _hose_set(cb)
    V.row(rows, "H10_save_load_hose", "PASS" if sa == sb and any(s[3] == "Plump" for s in sa) else "FAIL", "MOD",
          {"before": sa, "after": sb, "loadSeconds": waited})
    res["screenshots"] = [B.shot("hose_03_after_save_load")]
    return res


# ---------------------------------------------------------------------------------------------------- save hygiene (FINAL §3.9)
# The ONE helper H10b, proof_hose.py's SL2 and H11 use. A save may name a hose class in exactly one place: a colonist saved
# mid-carry / mid-wind has vanilla deep-save his job driver as <curDriver Class="RimMandrake.FlowWorks.Hose.Jobs.JobDriver_X">
# (X = CarryHoseEnd or RetractHose). Every other occurrence of a hose namespace -- FlowWorks', or the old Gimme Some Slack /
# MessyConduit one -- is a fault (the map component written into a save; an un-aliased old name).
HOSE_NAMESPACES = ("RimMandrake.FlowWorks.Hose", "RimMandrake.GimmeSomeSlack.Hose", "RimMandrake.MessyConduit.Hose")
DRIVER_WHITELIST = ("RimMandrake.FlowWorks.Hose.Jobs.JobDriver_CarryHoseEnd", "RimMandrake.FlowWorks.Hose.Jobs.JobDriver_RetractHose")


def save_class_hits(blob):
    """{"drivers": n whitelisted curDriver values, "offending": [context...], "RM_MapComponent_Hoses": n, "rmHoseState": n}."""
    import re as _re
    if isinstance(blob, str):
        blob = blob.encode("utf-8")
    drivers, offending = 0, []
    allowed = set()
    for m in _re.finditer(rb'<curDriver\s+Class="([^"]+)"', blob):
        if m.group(1).decode("utf-8", "replace") in DRIVER_WHITELIST:
            drivers += 1
            allowed.add(m.start(1))
    for ns in HOSE_NAMESPACES:
        for m in _re.finditer(_re.escape(ns.encode()), blob):
            if m.start() in allowed and ns == "RimMandrake.FlowWorks.Hose":
                continue
            offending.append(blob[max(0, m.start() - 80):m.end() + 40].decode("utf-8", "replace"))
    mc = blob.count(b"RM_MapComponent_Hoses")
    if mc:
        offending.append("RM_MapComponent_Hoses x%d" % mc)
    return {"drivers": drivers, "offending": offending[:6], "RM_MapComponent_Hoses": mc, "rmHoseState": blob.count(b"rmHoseState")}


def names_hose_class(err_text):
    """H11: a load error that names one of our hose classes, old (GSS / MessyConduit) or new (FlowWorks)."""
    return any(ns in err_text for ns in HOSE_NAMESPACES)


def run_removal_check(args):
    """H11: a save holding a laid hose, loaded on a tier WITHOUT the mod: vanilla's missing-def errors may name
    RM_HoseReel; nothing may name one of our C# classes."""
    B = H()
    rows = []
    res = {"mod": MOD, "mode": "removal-check", "script": "validation_hose.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    rm = B.call("jawa/running_mods", details=False)
    running = [p.lower() for p in rm.get("packageIds") or []]
    if not running or PKG in running:
        V.row(rows, "H11_remove_mod_with_hose", "UNMEASURED", "SITE", "mod list unreadable or the mod still running")
        return res
    lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    base = max([x.get("Sequence", 0) for x in lg0.get("logs") or []] or [0])
    B.call("rimworld/load_game", saveName=args.removal_check, ignoreModCompatibility=True)
    ok, waited = V._wait_playing(B)
    if not ok:
        V.row(rows, "H11_remove_mod_with_hose", "FAIL", "MOD", {"state": waited})
        return res
    B.ticks(60)
    time.sleep(1.0)
    lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > base]
    errs = [str(e.get("Message", "")) + " " + str(e.get("StackTrace", "")) for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
    class_hits = [e[:240] for e in errs if names_hose_class(e)]
    def_hits = [e[:200] for e in errs if "RM_HoseReel" in e]
    V.row(rows, "H11_remove_mod_with_hose", "UNMEASURED" if not isinstance(lg.get("logs"), list) else "PASS" if not class_hits else "FAIL", "MOD",
          {"loadSeconds": waited, "errorsNamingOurClasses": class_hits[:6], "errorsNamingOurDefs(expected)": len(def_hits),
           "firstDefErrors": def_hits[:3]})
    return res


# ---------------------------------------------------------------------------------------------------- round 6: relays
# Owner 2026-10-04: "So if the hose can only reach 30 cells, how does the player go farther? Maybe they place another reel
# out there to connect to? If so we should show that working." Three 2x2 reels in a row (A, B 24 east, C 32 further); A's hose
# is laid ONTO B's footprint, B's onto C's. Predictions from the code (HoseRelay, ReviewRound6Checks), to be confirmed live:
#   * RL2: one 40-cell hose cannot reach C from A ("too far"); RL3/RL4: aimed at a reel, the hose ends on that reel's
#     intake (relayTo = that reel, far = an intake cell), each hose under its own cap, and (round 7) the DRAWN end meets
#     the reel: lay end == endPoint, within 0.35 cell of the intake-side edge, straight into it, on the west brass inlet.
#   * RL5: closing the ring (C onto A) is refused. RL6 (hose port G5.6, split): the DEBUG flag on A propagates down the
#     chain -- B plumps through the "debug" provider (RL6_debug_flow_propagates); real flow through a chain is the bar
#     NS_relay_chain_carries (proof_hose.py). RL7: A's flow off -> B drains after the release window (no latch).
#   * RL9: the draw-order fix is live: span material queue == overhead queue > hose queue.
# Here "working" = connection accepted, both hoses laid and plump, chain shown connected (the liquid half is NS_relay_chain_carries).
RX0, RZ0 = 20, 100
# 2026-10-10 (West staging): 8 cells west of RA, not 2. RA is the one relay reel with no feeder, so its hose left the west nozzle straight
# and U-turns back east (owner card 2026-10-06, straight lead-out: OutletLead 4.0 + a 1.2-radius turn); a 2-cell margin put
# that lead-out on unprepared map ground, which refused the lay (RL3/RL6/RL8 red 2026-10-10). Same cure as the hose
# matrix's 6-cell soil margin (8b0c5b0e3).
SITE_R = (RX0 - 8, RZ0 - 3, 88, 10)
# 2026-10-10: A-B is 24, not 32. A's hose U-turns out of its west nozzle (the straight lead-out, owner card 2026-10-06), which
# adds ~12 cells; at 32 the laid hose was ~44 > 40 and was refused "route too long (the laid hose, lead-out included...)".
# B is fed, so its hose keeps the plain start and B-C stays 32. A-C = 56 is still past one 40-cell hose (RL2, RL8).
RA, RB, RC = (RX0, RZ0), (RX0 + 24, RZ0), (RX0 + 56, RZ0)
# VALIDATION_HOSE_REELS_FIX_STILL_WEST: each relay reel faces the reel its hose goes to (A and B East; C West, toward A, the
# ring RL5 refuses). The margins above date from the West staging and are kept.
RELAY_TARGET = {RA: RB, RB: RC, RC: RA}


def run_relay(args):
    B = H()
    rows = []
    res = {"mod": MOD, "mode": "relay", "script": "validation_hose.py", "tier": TIER,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    d = B.hp("defaults")
    if not d.get("success"):
        V.row(rows, "RL0_probe_channel", "FAIL", "HARNESS", d)
        res["aborted"] = "hose probe dead"
        return res
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE_R, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE_R)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE_R)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % SITE_R)
    br = B.call("jawa/build_batch", ops=";".join(V.reel_toward(r, RELAY_TARGET[r]) for r in (RA, RB, RC)), faction="player",
                wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(2)
    a, c = B.hose(RA)
    b, _ = B.hose(RB)
    cc, _ = B.hose(RC)
    V.hrow(rows, "RL1_reels_built", "PASS" if a and b and cc else "FAIL", "SITE", {"build": br.get("success"), "maxLength": a.get("maxLength")})
    if not (a and b and cc):
        res["aborted"] = "reels missing"
        return res
    one = B.hp("check:%d,%d,%d,%d" % (RA + (RC[0] - 1, RC[1])))
    V.row(rows, "RL2_one_hose_cannot_reach", "PASS" if one.get("reason") in ("too far", "route too long") else "FAIL", "MOD",
          {"reason": one.get("reason"), "maxLength": a.get("maxLength")})

    def laid_into(src, dst, name):
        lay = B.hp("lay:%d,%d,%d,%d" % (src + dst))          # aimed at the relay's own south-west footprint cell
        B.ticks(2)
        h, _ = B.hose(src)
        rel = h.get("relayTo")
        far = h.get("far") or [0, 0]
        ep = h.get("endPoint") or [0, 0]
        intake = far[0] in (dst[0] - 1, dst[0] + 2) and dst[1] <= far[1] <= dst[1] + 1 or \
            far[1] in (dst[1] - 1, dst[1] + 2) and dst[0] <= far[0] <= dst[0] + 1
        # round 7 (owner, station 42: "pipe does NOT hook up properly to the next reel station"): what is DRAWN must meet
        # the relay -- the lay's last point IS the end point, it lies within the tolerance (0.35 cell) of the footprint
        # edge on the intake side and inside that edge, and the last 0.5 cell runs along the intake axis (< 3 deg). From
        # the west (this station) the end is the art's brass inlet: its height (relay centre z +-0.15), face outside the edge.
        re_ = h.get("relayEnd") or {}
        de = re_.get("drawnEnd") or [0, 0]
        tol = re_.get("tolerance") or 0.35
        inward = re_.get("inward") or [0, 0]
        on_edge = bool(re_) and abs(de[0] - ep[0]) < 1e-3 and abs(de[1] - ep[1]) < 1e-3 and \
            abs(re_.get("edgeOffset") if re_.get("edgeOffset") is not None else 99) <= tol and re_.get("withinEdge") is True and \
            (re_.get("tailAngleDeg") if re_.get("tailAngleDeg") is not None else 99) < 3
        # the brass inlet is on the PICTURE's west, i.e. the relay's facing side (HoseRelay.DrawnEnd, art frame): it is checked
        # only when the hose comes in on that side (C, facing A); a hose into a relay's back (B, facing C) meets the drawn
        # outline (on_edge). VALIDATION_HOSE_REELS_FIX_STILL_WEST: before, every relay faced West and this was always checked.
        brass = inward == [1, 0] and V.reel_facing(dst, RELAY_TARGET[dst]) == 3
        west_inlet = not brass or (abs(de[1] - (dst[1] + 1)) < 0.15 and dst[0] - tol < de[0] < dst[0])
        # HARNESS (BENCH belt 2026-10-22): a reel's Position moves with its facing while the footprint stays dst..dst+1
        # (V.reel_pos): the relay is matched by V.reel_at, not equality
        ok = lay.get("success") and h.get("layOk") and V.reel_at(rel, dst) and intake and on_edge and west_inlet and \
            (h.get("pathLen") or 99) <= (h.get("maxLength") or 0)
        V.row(rows, name, "PASS" if ok else "FAIL", "MOD",
              dict(_pick(h, "relayTo", "far", "endPoint", "pathLen", "flatLen", "maxLength", "layOk"), reason=lay.get("reason"), intake=intake,
                   onEdge=on_edge, brassSide=brass, westInlet=west_inlet, relayEnd=re_))
        return h

    ha = laid_into(RA, RB, "RL3_hose_onto_relay_B")
    hb = laid_into(RB, RC, "RL4_relay_B_onward_to_C")
    loop = B.hp("check:%d,%d,%d,%d" % (RC + RA))
    lay_loop = B.hp("lay:%d,%d,%d,%d" % (RC + RA))
    V.row(rows, "RL5_ring_refused", "PASS" if not lay_loop.get("success") and "loop" in (lay_loop.get("reason") or "") else "FAIL", "MOD",
          {"lay": lay_loop.get("reason"), "check": loop.get("reason")})
    B.hp("flow:%d,%d=on" % RA)
    B.ticks(120)
    a, c = B.hose(RA)
    b, _ = B.hose(RB)
    V.row(rows, "RL6_debug_flow_propagates", "PASS" if a.get("state") == "Plump" and b.get("state") == "Plump" and b.get("provider") == "debug"
          and (c.get("relayCouplings") or 0) >= 2 and len(b.get("fedBy") or []) == 1 and V.reel_at(b["fedBy"][0], RA) else "FAIL", "MOD",
          {"A": _pick(a, "state", "provider", "signal"), "B": _pick(b, "state", "provider", "signal", "fedBy"), "relayCouplings": c.get("relayCouplings")})
    B.hp("flow:%d,%d=off" % RA)
    B.ticks((c.get("releaseTicks") or 500) + (c.get("minPlumpDwell") or 600) + 200)
    a, _ = B.hose(RA)
    b, _ = B.hose(RB)
    V.row(rows, "RL7_no_latch", "PASS" if a.get("state") == "Flat" and b.get("state") == "Flat" else "FAIL", "MOD",
          {"A": _pick(a, "state", "provider"), "B": _pick(b, "state", "provider")})
    span = RC[0] - RA[0]
    V.row(rows, "RL8_chain_beyond_one_hose", "PASS" if span > (a.get("maxLength") or 0) and ha.get("layOk") and hb.get("layOk") else "FAIL", "MOD",
          {"span": span, "maxLength": a.get("maxLength"), "pathA": ha.get("pathLen"), "pathB": hb.get("pathLen")})
    # RL9 (cross-mod, both mods active): the hose queue is FlowWorks' (HoseProbe), the overhead queues Gimme Some Slack's
    # (AerialProbe census): each mod reports its own (hose port M3); without GSS there is no overhead line to draw over
    q = dict((c.get("queues") or {}))
    aq = (B.probe_of("RimMandrake.GimmeSomeSlack.Aerial.AerialProbe", "census").get("queues") or {})
    q.update({"overhead": aq.get("overhead"), "spanMat": aq.get("spanMat")})
    if aq.get("overhead") is None:
        V.row(rows, "RL9_overhead_drawn_over_hose", "UNMEASURED", "SITE", dict(q, why="Gimme Some Slack's AerialProbe did not answer (GSS not active?)"))
    else:
        V.row(rows, "RL9_overhead_drawn_over_hose", "PASS" if q["overhead"] > q.get("hose", 1e9) and q.get("spanMat") == q["overhead"] else "FAIL",
              "MOD", q)
    return res


# ============================================================================ CR1-CR6: the colonist-carried hose (S3)
# hose_carry_design_2026-10-04.md section 13. One scene, one REAL colonist, real jobs (RM_CarryHoseEnd / RM_RetractHose
# given through WorkGiver_HoseOrders.JobFor by the probe's startjob verb), every row a state read through HoseProbe.
# Predictions from the code, to be confirmed or killed live:
#   * CR1: the forced job walks to the reel, waits 45 ticks (grab), then the reel reads Carrying with this pawn as carrier.
#   * CR2: jogging ~13 ticks/cell, 60 ticks add ~4 cells; the trail's last cell is the pawn's cell (or the one he just left).
#   * CR3: drafting ends the job InterruptForced (vanilla Drafted setter) -> finish action -> Dropped at his cell, order KEPT.
#   * CR4: a save while Dropped round-trips exactly; a save while Carrying comes back Carrying (driver resumed at its toil)
#     or Dropped (holder check), never Laid-without-trail.
#   * CR5: undrafted, the UNFORCED WorkGiver path takes the kept order: back to the dropped end, carry on, Laid at the target.
#     Plump with the DEV flow on. endKind (Water etc.) is S4's: that row is SKIP until the census carries it.
#   * CR6: a Retract order: walk back to the reel, Retracting, Stored within length/3 s + 300 ticks of winding.
CX0, CZ0 = 80, 60
CSITE = (CX0 - 8, CZ0 - 2, 42, 20)   # 2026-10-10: room west of the reel for the West-staged lead-out + U-turn; kept (it faces East now)
CREEL = (CX0 + 2, CZ0 + 8)
CTARGET = (CX0 + 26, CZ0 + 8)        # 24 cells out, open floor
CSTAND = (CX0 + 5, CZ0 + 8)          # where the colonist is staged, beside the reel


def _near(a, b, d=1):
    return a is not None and b is not None and max(abs(a[0] - b[0]), abs(a[1] - b[1])) <= d


def _carry_view(h):
    t = h.get("trail") or {}
    return {"carry": h.get("carry"), "carrier": (h.get("carrier") or {}).get("id"), "far": h.get("far"),
            "trailCount": t.get("count"), "trailLast": t.get("last"), "pulled": t.get("pulled"),
            "pending": h.get("pending"), "pendingAt": h.get("pendingAt"), "wound": h.get("wound"), "state": h.get("state")}


def _poll(B, pred, max_ticks, step=30):
    """Step the game `step` ticks at a time until pred(hose) holds; returns (hose, ticks waited, seen carry states)."""
    waited, seen, h = 0, [], {}
    while True:
        h, _ = B.hose(CREEL)
        if h.get("carry") not in seen:
            seen.append(h.get("carry"))
        if pred(h) or waited >= max_ticks:
            return h, waited, seen
        B.ticks(step)
        waited += step


def _walk_a_little(B, reel, more=2, max_ticks=60, step=2):
    """2026-10-10 (full 550-mod list): step until the carried trail has grown by `more` cells, never a fixed 60 ticks.
    There an out-of-combat speed mod ("Out of Combat ReBoost") walks a colonist ~2 ticks/cell, not ~13 (MoveSpeed reads 4.6
    unchanged), so 60 ticks carried him all 16 remaining cells and "mid-walk" rows saw him already Laid at the target."""
    h0 = B.hose(reel)[0]
    n0 = (h0.get("trail") or {}).get("count") or 0
    waited, h = 0, h0
    while waited < max_ticks:
        B.ticks(step)
        waited += step
        h = B.hose(reel)[0]
        if h.get("carry") != "Carrying" or ((h.get("trail") or {}).get("count") or 0) >= n0 + more:
            break
    return h, waited


def _save_reload(B, name):
    before = V._saves_stat()
    if name + ".rws" in before:
        return False, {"error": "%s.rws exists" % name}
    B.call("rimworld/save_game", saveName=name)
    V._wait_saved(name)
    after = V._saves_stat()
    new = sorted(set(after) - set(before))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    if new != [name + ".rws"] or changed:
        return False, {"new": new, "changed": changed}
    B.call("rimworld/load_game", saveName=name)
    ok, waited = V._wait_playing(B)
    if not ok:
        return False, {"state": waited}
    B.call("rimworld/frame_cell_rect", x=CSITE[0], z=CSITE[1], width=CSITE[2], height=CSITE[3], paddingCells=1)
    time.sleep(1.0)
    return True, {"saved": name + ".rws", "loadSeconds": waited}


def run_carry(args):
    B = H()
    rows = []
    res = {"mod": MOD, "mode": "carry", "script": "validation_hose.py", "tier": TIER,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    stamp = time.strftime("%Y%m%d%H%M%S")
    d = B.hp("defaults")
    if not d.get("success"):
        V.row(rows, "CR0_probe_channel", "FAIL", "HARNESS", d)
        res["aborted"] = "hose probe dead"
        return res
    # ---------------------------------------------------------------- scene: a reel and one real colonist beside it
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % CSITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % CSITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % CSITE)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % CSITE)
    br = B.call("jawa/build_batch", ops=V.reel_toward(CREEL, CTARGET), faction="player", wipeExisting=False)   # East, at its target
    B.call("jawa/map_commit")
    B.call("rimworld/frame_cell_rect", x=CSITE[0], z=CSITE[1], width=CSITE[2], height=CSITE[3], paddingCells=1)
    B.ticks(2)
    h0, _ = B.hose(CREEL)
    col = B.hp("colonists")
    pawns = [p for p in col.get("pawns") or [] if not p.get("downed")]
    if not h0 or not pawns:
        V.row(rows, "CR0_scene", "FAIL", "SITE", {"reel": bool(h0), "build": br, "colonists": col})
        res["aborted"] = "no reel or no colonist"
        return res
    pid = pawns[0]["id"]
    if pawns[0].get("drafted"):
        B.hp("pawn:%d=undraft" % pid)
    # 2026-10-10 (550-mod list): idle colonists take a dropped hose's KEPT order through the WorkGiver; the rows follow ONE
    # colonist, so the others are drafted for the block and released at its end
    others = [p["id"] for p in pawns[1:]]
    for o_ in others:
        B.hp("pawn:%d=draft" % o_)
    tp = B.hp("pawn:%d=tp:%d,%d" % ((pid,) + CSTAND))
    V.hrow(rows, "CR0_scene", "PASS" if tp.get("success") else "FAIL", "HARNESS", {"pawn": tp.get("pawn"), "reel": CREEL})

    # ---------------------------------------------------------------- CR1: order Deploy -> a real colonist carries it
    o = B.hp("order:%d,%d=deploy:%d,%d" % (CREEL + CTARGET))
    sj = B.hp("startjob:%d,%d=forced;%d" % (CREEL + (pid,)))
    h, waited, seen = _poll(B, lambda x: x.get("carry") == "Carrying", 600, step=3)
    V.row(rows, "CR1_deploy_carrying", "PASS" if h.get("carry") == "Carrying" and (h.get("carrier") or {}).get("id") == pid else "FAIL",
          "MOD", {"order": o, "startjob": sj, "ticks": waited, "seen": seen, "hose": _carry_view(h)})

    # ---------------------------------------------------------------- CR2: the trail grows behind him
    a = h
    b, _ = _walk_a_little(B, CREEL)
    ta, tb = (a.get("trail") or {}), (b.get("trail") or {})
    ppos = (b.get("carrier") or {}).get("pos")
    V.row(rows, "CR2_trail_follows_walk", "PASS" if (tb.get("count") or 0) > (ta.get("count") or 0) and _near(tb.get("last"), ppos)
          and b.get("layOk") else "FAIL", "MOD", {"before": _carry_view(a), "after": _carry_view(b), "pawnPos": ppos})

    # ---------------------------------------------------------------- CR3: draft him mid-walk -> dropped at his cell, order kept
    dr = B.hp("pawn:%d=draft" % pid)
    B.ticks(35)   # past one 30-tick holder check, should the finish action not have fired
    c, _ = B.hose(CREEL)
    pc = B.hp("colonists")
    me = next((p for p in pc.get("pawns") or [] if p["id"] == pid), {})
    V.row(rows, "CR3_draft_drops_end", "PASS" if c.get("carry") == "Dropped" and _near(c.get("far"), me.get("pos"))
          and c.get("pending") == "Deploy" and c.get("carrier") is None else "FAIL", "MOD",
          {"draft": (dr.get("pawn") or {}).get("drafted"), "pawn": me, "hose": _carry_view(c)})

    # ---------------------------------------------------------------- CR4a: save/load while Dropped
    # SHARED (proof_all): CR4a/CR4b are the session's ONE save (SL4, consolidation doc section 2 "Save/load"), staged by
    # proof_all.stage_carry_for_save: a Dropped reel and a Carrying reel in the same save, the carrying one resumed after load.
    if not V.SHARED:
        keys = ("carry", "far", "trailCount", "trailLast", "pending", "pendingAt")
        va = {k: _carry_view(c)[k] for k in keys}
        ok, det = _save_reload(B, "RM_hosecarry_%s_dropped" % stamp)
        c2, _ = B.hose(CREEL) if ok else ({}, None)
        vb = {k: _carry_view(c2)[k] for k in keys} if ok else None
        V.row(rows, "CR4a_save_load_dropped", "PASS" if ok and va == vb else "FAIL", "MOD", {"io": det, "before": va, "after": vb})
        if not ok:
            res["aborted"] = "save/load failed"
            return res

    # ---------------------------------------------------------------- CR5: undraft -> the WorkGiver path resumes, Laid at the target
    B.hp("pawn:%d=undraft" % pid)
    sj = B.hp("startjob:%d,%d=work;%d" % (CREEL + (pid,)))
    how = "work"
    if not sj.get("success"):
        sj2 = B.hp("startjob:%d,%d=forced;%d" % (CREEL + (pid,)))
        how = {"work": sj, "forced": sj2}
    h, waited, seen = _poll(B, lambda x: x.get("carry") == "Carrying", 600, step=3)
    resumed = h.get("carry") == "Carrying"
    # CR4b: save/load while Carrying (taken here, mid-resume) -- SHARED: SL4 (see CR4a)
    if not V.SHARED:
        vc = _carry_view(h)
        ok, det = _save_reload(B, "RM_hosecarry_%s_carrying" % stamp)
        hl, _ = B.hose(CREEL) if ok else ({}, None)
        vl = _carry_view(hl)
        good = ok and resumed and vl["carry"] in ("Carrying", "Dropped") and (vl["trailCount"] or 0) > 0 and vl["pending"] == "Deploy"
        V.row(rows, "CR4b_save_load_carrying", "PASS" if good else "FAIL", "MOD", {"io": det, "before": vc, "after": vl})
        if ok and hl.get("carry") == "Dropped":
            B.hp("startjob:%d,%d=work;%d" % (CREEL + (pid,)))
    h, waited2, seen2 = _poll(B, lambda x: x.get("carry") == "Laid", 1200)
    V.row(rows, "CR5_resume_laid_at_target", "PASS" if resumed and h.get("carry") == "Laid" and tuple(h.get("far") or ()) == CTARGET
          and h.get("pending") == "None" and h.get("layOk") else "FAIL", "MOD",
          {"startjob": how, "resumeTicks": waited, "layTicks": waited2, "seen": seen + seen2, "hose": _carry_view(h)})
    B.hp("flow:%d,%d=on" % CREEL)
    B.ticks(120)
    hp_, _ = B.hose(CREEL)
    V.row(rows, "CR5b_laid_hose_plumps", "PASS" if hp_.get("state") == "Plump" else "FAIL", "MOD", _pick(hp_, "state", "provider", "signal"))
    B.hp("flow:%d,%d=off" % CREEL)
    V.row(rows, "CR5c_end_kind", "PASS" if hp_.get("endKind") == "Free" else ("SKIP" if "endKind" not in hp_ else "FAIL"), "MOD",
          {"endKind": hp_.get("endKind"), "note": "endKind is stage S4"})

    # ---------------------------------------------------------------- CR6: Retract -> Retracting -> Stored
    length = (h.get("trail") or {}).get("pulled") or 24
    o = B.hp("order:%d,%d=retract" % CREEL)
    sj = B.hp("startjob:%d,%d=forced;%d" % (CREEL + (pid,)))
    budget = int(length / 3.0 * 60 + 300 + 30 * length)   # winding + the walk back to the reel
    h, waited, seen = _poll(B, lambda x: x.get("carry") == "Stored", budget)
    V.row(rows, "CR6_retract_stored", "PASS" if "Retracting" in seen and h.get("carry") == "Stored" and h.get("pending") == "None"
          else "FAIL", "MOD", {"order": o, "startjob": sj, "ticks": waited, "budget": budget, "seen": seen, "hose": _carry_view(h)})
    # ---------------------------------------------------------------- CR7: no instant Lay / Reel in without dev mode
    # (owner ruling: the instant gizmos are DEV-ONLY with NO setting that restores them). Read the gizmo labels with dev mode
    # forced off, then forced on (control: the DEV: gizmos must exist then, or the off-reading proves nothing), then restore.
    was = B.hp("devmode:%d,%d=read" % CREEL).get("devMode")
    B.hp("devmode:%d,%d=off" % CREEL)
    off = B.hp("gizmos:%d,%d" % CREEL)
    B.hp("devmode:%d,%d=on" % CREEL)
    on = B.hp("gizmos:%d,%d" % CREEL)
    B.hp("devmode:%d,%d=%s" % (CREEL + ("on" if was else "off",)))
    lo = [str(x) for x in (off.get("labels") or [])]
    lon = [str(x) for x in (on.get("labels") or [])]
    bad = [x for x in lo if "lay hose" in x.lower() or "reel in" in x.lower()]
    control = [x for x in lon if "lay hose" in x.lower() or "reel in" in x.lower()]
    V.row(rows, "CR7_no_instant_gizmos_without_devmode",
          "PASS" if off.get("success") and off.get("devMode") is False and lo and not bad and control else "FAIL", "MOD",
          {"devModeOff_labels": lo, "offending": bad, "devModeOn_labels": lon, "control_found_in_devmode": control,
           "devModeBefore": was})
    for o_ in others:
        B.hp("pawn:%d=undraft" % o_)
    res["saves"] = [] if V.SHARED else ["RM_hosecarry_%s_dropped.rws" % stamp, "RM_hosecarry_%s_carrying.rws" % stamp]
    res["pawn"] = pid
    return res


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--save-load", default=None, metavar="NAME")
    ap.add_argument("--removal-check", default=None, metavar="NAME")
    ap.add_argument("--maze", action="store_true")
    ap.add_argument("--relay", action="store_true")
    ap.add_argument("--carry", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.save_load:
        res = run_save_load(a)
    elif a.removal_check:
        res = run_removal_check(a)
    elif a.maze:
        res = run_maze(a)
    elif a.relay:
        res = run_relay(a)
    elif a.carry:
        res = run_carry(a)
    elif a.live:
        res = run_live(a)
    else:
        ap.print_help()
        return 2
    os.makedirs(os.path.join(HERE, "northstar"), exist_ok=True)
    out = a.out or os.path.join(HERE, "northstar", "validation_hose_%s_%s.json" % (res["mode"], time.strftime("%Y%m%dT%H%M%S")))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    t = {}
    for r in res["rows"]:
        t[r["status"]] = t.get(r["status"], 0) + 1
    print("hose %s: %s -> %s" % (res["mode"], t, out))
    return 0 if not res.get("aborted") and not t.get("FAIL") and not t.get("UNMEASURED") else 1


if __name__ == "__main__":
    sys.exit(main())
