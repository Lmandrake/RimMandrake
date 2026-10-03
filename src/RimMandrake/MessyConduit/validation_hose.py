"""validation_hose.py -- Messy Conduit L6 (fire hoses) functional script, beside validation.py / validation_aerial.py.

Design: design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 3 (3.12 northstar angle).
Owner, 2026-10-02: "The flexible water hoses should be much thicker and stiffer than the wires, much like the fire
hoses they use. And they SHOULD "plump up" when water is flowing through them and "collapse down" when it's not."
Offline half: the Verse-free Source/Hose/HoseMath.cs is checked by the C# SelfTest (HoseSelfTest.cs, run by
validation.py's O3 row: widths, the state machine + hysteresis + a no-hysteresis negative control, wobble, lay
bend radius incl. round a wall, install validity, the pump rule, tints). State is read through
RimMandrake.MessyConduit.Hose.HoseProbe (jawa/mod_settings_field), never from screenshots.

    python.exe validation_hose.py --live                   # on the current map (after validation.py --live)
    python.exe validation_hose.py --save-load NAME         # H10: hose, its end and its state survive save/load
    python.exe validation_hose.py --removal-check NAME     # H11: a save WITH a laid hose on a tier WITHOUT the mod

The flow signal here is the DEBUG provider (HoseProbe "flow:"): FlowWorks has no pump yet, so its adapter
(FlowWorksPumpFlow, design 3.3 fields lastMovedUnits/lastMovedTick read by reflection) answers null and H5 asserts
the provider that decided was "debug" -- the day a pump exists beside a reel, that row says so.

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
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

HPROBE = "RimMandrake.MessyConduit.Hose.HoseProbe"
HX0, HZ0 = 40, 60
SITE = (HX0 - 2, HZ0 - 2, 36, 20)
R1, F1 = (HX0 + 2, HZ0 + 6), (HX0 + 26, HZ0 + 6)        # main hose, 24 cells, across a wall
WALL = [(HX0 + 13, z) for z in range(HZ0 + 2, HZ0 + 9)]  # the hose must go round its north end
R2, F2 = (HX0 + 2, HZ0 + 14), (HX0 + 20, HZ0 + 14)       # flicker hose, open floor
SHOT = (HX0, HZ0 + 1, 30, 16)
SHOTS = os.path.join(V.REPO, "Transient", "messy_conduit_live_20261002")
WIRE_RATIO_MIN = 4.0


class H(V.Bridge):
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

    def hose(self, reel):
        c = self.hp("census")
        for h in c.get("hoses") or []:
            if tuple(h["reel"]) == tuple(reel):
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
    res = {"mod": V.MOD, "mode": "live", "script": "validation_hose.py", "tier": V.TIER,
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
    V.row(rows, "H0_probe_channel", "PASS", "HARNESS", "defaults applied")

    # ---------------------------------------------------------------- scene
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % SITE)
    bw = B.call("jawa/build_batch", ops=V.ops("Wall", WALL), stuff="Steel", faction="player")
    br = B.call("jawa/build_batch", ops=V.ops("RM_HoseReel", [R1, R2]), faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(2)
    h1, c = B.hose(R1)
    h2, _ = B.hose(R2)
    V.row(rows, "H1_reels_built", "PASS" if h1 and h2 else "FAIL", "MOD" if br.get("success") else "SITE",
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
    V.row(rows, "H3_width_ge_4x_wire", "PASS" if (h1.get("widthOverWire") or 0) >= WIRE_RATIO_MIN else "FAIL", "MOD",
          _pick(h1, "visibleWidth", "widthOverWire", "meshWidthFlat", "meshWidthPlump") | {"wireVisibleWidth": c.get("wireVisibleWidth")})
    mb = c.get("minBendSetting") or 1.2
    ok4 = (h1.get("minBendFlat") or 0) >= 0.95 * mb and (h1.get("minBendPlump") or 0) >= 0.95 * mb and (h2.get("minBendFlat") or 0) >= 0.95 * mb
    V.row(rows, "H4_bend_radius_ge_hose_min", "PASS" if ok4 else "FAIL", "MOD",
          {"setting": mb, "hose1": _pick(h1, "minBendFlat", "minBendPlump"), "hose2": _pick(h2, "minBendFlat", "minBendPlump"), "wallInPath": True})

    # ---------------------------------------------------------------- flat while nothing flows
    B.ticks(300)
    h1, _ = B.hose(R1)
    ok5 = h1.get("state") == "Flat" and h1.get("transitions") == 0 and h1.get("blend") == 0 and h1.get("provider") == "debug"
    V.row(rows, "H5_flat_when_not_flowing", "PASS" if ok5 else "FAIL", "MOD", _pick(h1, "state", "blend", "transitions", "provider", "signal"))
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
    V.row(rows, "H9_stiffness_setting", "PASS" if (hs.get("minBendFlat") or 0) >= 1.9 and hs.get("geometryHash") != hd.get("geometryHash") else "FAIL", "MOD",
          {"minBend2": hs.get("minBendFlat"), "hash2": hs.get("geometryHash"), "hashDefault": hd.get("geometryHash")})

    # ---------------------------------------------------------------- log budget
    lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > log_base]
    errs_all = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
    # the scene clear's own destroy_batch over a map geyser logs "Tried to destroy non-destroyable thing": harness, not the mod
    site = [e for e in errs_all if "non-destroyable" in str(e.get("Message", ""))]
    errs = [e for e in errs_all if e not in site]
    V.row(rows, "HZ_log_budget", "PASS" if not errs else "FAIL", "MOD",
          {"errors": [str(e.get("Message", ""))[:240] for e in errs[:8]], "newWarnings": len(new), "siteClearErrors": len(site)})
    # leave hose 1 plump for the save-load mode (state must survive)
    B.hp("flow:%d,%d=on" % R1)
    B.ticks(tt + 5)
    res["log"] = log
    return res


# ============================================================================ H10 / H11
def _hose_set(c):
    return sorted((tuple(h["reel"]), tuple(h["far"]), h.get("end"), h.get("state"), h.get("laid"), h.get("debugFlowing"),
                   h.get("geometryHash"), h.get("transitions")) for h in c.get("hoses") or [])


def run_save_load(args):
    B = H()
    rows = []
    res = {"mod": V.MOD, "mode": "save-load", "script": "validation_hose.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
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
    time.sleep(3.0)
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
    hits = {k: blob.count(k.encode()) for k in ("RM_MapComponent_Hoses", "RimMandrake.MessyConduit.Hose", "rmHoseState")}
    V.row(rows, "H10b_save_names_no_class", "PASS" if hits["RM_MapComponent_Hoses"] == 0 and hits["RimMandrake.MessyConduit.Hose"] == 0
          and hits["rmHoseState"] >= 1 else "FAIL", "MOD", hits)
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


def run_removal_check(args):
    """H11: a save holding a laid hose, loaded on a tier WITHOUT the mod: vanilla's missing-def errors may name
    RM_HoseReel; nothing may name one of our C# classes."""
    B = H()
    rows = []
    res = {"mod": V.MOD, "mode": "removal-check", "script": "validation_hose.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    rm = B.call("jawa/running_mods", details=False)
    running = [p.lower() for p in rm.get("packageIds") or []]
    if not running or V.PKG in running:
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
    class_hits = [e[:240] for e in errs if "RimMandrake.MessyConduit" in e]
    def_hits = [e[:200] for e in errs if "RM_HoseReel" in e]
    V.row(rows, "H11_remove_mod_with_hose", "PASS" if not class_hits else "FAIL", "MOD",
          {"loadSeconds": waited, "errorsNamingOurClasses": class_hits[:6], "errorsNamingOurDefs(expected)": len(def_hits),
           "firstDefErrors": def_hits[:3]})
    return res


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--save-load", default=None, metavar="NAME")
    ap.add_argument("--removal-check", default=None, metavar="NAME")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.save_load:
        res = run_save_load(a)
    elif a.removal_check:
        res = run_removal_check(a)
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
