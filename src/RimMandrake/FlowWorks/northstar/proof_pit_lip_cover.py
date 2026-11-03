#!/usr/bin/env python3
"""Live proof of the near-lip pit cover on br1f's s8 scene (PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES).

The GPT art review read s8_pitlip_close.png (2026-10-23 21:00 PDT) as a cover that "runs past the pit's west edge and ghosts
a pawn standing partly outside the pit" plus an occupant "more than half hidden with no window". That frame predates
PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM (76779c19e6, the same night): the "partly outside" pawn is the muffalo IN the pit's SW
corner, whose 3-cell sprite overhangs the west rim. This script restages s8 (a 4x4 pit dug to D4, a muffalo on its SW
corner, a colonist on its SE corner, a muffalo on the ground beyond the SE corner), pauses, frames the camera on it and
reads what the cover drew in the last frame through jawa/static_call RM_PitLipOcclusion.LastFrameCovers. Clauses:

  A1  no cover piece drawn over a pawn shallower than the one it hides (the outside muffalo is never ghosted);
  A2  the cover stays with what the pit hides: every piece lies inside its sunk pawn's drawn rect, and the in-pit muffalo's
      west overhang is covered above the lip by a side-bank piece (no hard seam at the lip row in the overhang column);
  A3  occupant window: with the sink clamp OFF the lip hides more than half of the colonist and the window opens (cut=1,
      the near-lip pieces leave [x-w/2, x+w/2] bare); with the clamp ON (shipped) it stays shut, as PIT_LIP_FIX_BOAR_HANGS_OUT
      ruled (2026-10-16: the window opens only when the lip would hide MORE than half).

    python.exe proof_pit_lip_cover.py --clause A1|A2|A3|all [--origin 120,180] [--no-shots]

Exit 0 when every asked clause holds, 1 when one fails, 2 when it could not measure. Settings it touches are restored.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

OCC = "RimMandrake.FlowWorks.RM_PitLipOcclusion"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
# the bridge is Windows loopback only, so this runs under python.exe (live_proofs line); /mnt/d is WSL spelling
OUT = (("D:/" if os.name == "nt" else "/mnt/d/") + "ClaudeWork/rimmandrake/scratch/pitlip_occluder/live")
EPS = 1e-3
# s8, relative to the origin: pit (1..4, 1..4) dug 4 notches; the in-pit muffalo on its SW corner, the colonist on its SE
# corner, the outside muffalo one cell south and two east of the SE corner (br1f: 132,114 / 135,114 / 137,113 on 131,113)
PIT = (1, 1, 4, 4)
DEPTH = 4
MUFF_IN, COLONIST, MUFF_OUT = (1, 1), (4, 1), (6, 0)
SETTINGS = {"pitLipOcclusionEnabled": True, "pitDepthDrawOffsetEnabled": True, "pitLipOccupantCutEnabled": True,
            "pitLipOccupantCutWidth": 1.0}


# ============================================================================ pure (selftest_pit_lip_cover.py)
def parse_report(txt):
    """LastFrameCovers' text -> {"head": {k: v}, "sunk": {id: rec}, "pieces": [rec], "pawns": {id: rec}}."""
    rep = {"head": {}, "sunk": {}, "pieces": [], "pawns": {}}
    for line in (txt or "").splitlines():
        f = line.split()
        if not f:
            continue
        if f[0] == "frame":
            rep["head"] = {f[i]: f[i + 1] for i in range(0, len(f) - 1, 2)}
        elif f[0] == "sunk" and len(f) == 8:
            rep["sunk"][f[1]] = {"id": f[1], "d": int(f[2]), "l": float(f[3]), "r": float(f[4]), "bot": float(f[5]),
                                 "top": float(f[6]), "cut": f[7] == "1"}
        elif f[0] == "piece" and len(f) == 7:
            rep["pieces"].append({"id": f[1], "kind": f[2], "l": float(f[3]), "r": float(f[4]), "a": float(f[5]),
                                  "b": float(f[6])})
        elif f[0] == "pawn" and len(f) == 7:
            rep["pawns"][f[1]] = {"id": f[1], "d": int(f[2]), "l": float(f[3]), "r": float(f[4]), "bot": float(f[5]),
                                  "top": float(f[6])}
    return rep


def _overlap(p, q):
    return p["r"] > q["l"] + EPS and p["l"] < q["r"] - EPS and p["b"] > q["bot"] + EPS and p["a"] < q["top"] - EPS


def drawn(rep):
    return [p for p in rep["pieces"] if p["kind"] in ("N", "S")]


def v_no_ghost(rep, outside_id):
    """A1: no drawn piece overlaps a pawn shallower than the sunk pawn it hides. Can-see: the outside pawn is in view at
    depth 0, and at least one piece was drawn."""
    if outside_id not in rep["pawns"]:
        return "UNMEASURED", {"why": "outside pawn not in the frame's pawn list", "pawns": sorted(rep["pawns"])}
    if not drawn(rep):
        return "UNMEASURED", {"why": "no cover piece drawn: the instrument cannot see the cover"}
    bad = []
    for p in drawn(rep):
        d = (rep["sunk"].get(p["id"]) or {}).get("d", 0)
        for q in rep["pawns"].values():
            if q["id"] != p["id"] and q["d"] < d and _overlap(p, q):
                bad.append((p, q["id"]))
    return ("FAIL" if bad else "PASS"), {"ghosted": bad[:6], "pieces": len(drawn(rep)),
                                         "skipped": sum(1 for p in rep["pieces"] if p["kind"] == "X")}


def v_cover_with_pit(rep, muff_id, west_col, lip_z):
    """A2: every drawn piece lies inside its sunk pawn's drawn rect; the in-pit muffalo's overhang column (west of the
    pit) carries a side-bank piece above the lip, so the flank reads as one body under the bank, not a seam at the lip."""
    if muff_id not in rep["sunk"]:
        return "UNMEASURED", {"why": "the in-pit muffalo was not covered this frame", "sunk": sorted(rep["sunk"])}
    out = []
    for p in drawn(rep):
        s = rep["sunk"].get(p["id"])
        if s is None or p["l"] < s["l"] - EPS or p["r"] > s["r"] + EPS or p["a"] < s["bot"] - EPS or p["b"] > s["top"] + EPS:
            out.append(p)
    s = rep["sunk"][muff_id]
    if s["l"] >= west_col + 1 - EPS:
        return "UNMEASURED", {"why": "the muffalo sprite does not overhang the west rim", "sunk": s}
    side = [p for p in drawn(rep) if p["id"] == muff_id and p["kind"] == "S" and p["l"] < west_col + 1 - EPS
            and p["b"] > lip_z + EPS]
    ok = not out and bool(side)
    return ("PASS" if ok else "FAIL"), {"outsideOwnRect": out[:6], "westSidePieces": side[:4], "sunk": s}


def v_window(rep, col_id, clamp_on, cut_width=1.0):
    """A3: clamp off -> the colonist's cut is open and no near-lip piece covers [x-w/2, x+w/2]; clamp on -> cut shut."""
    s = rep["sunk"].get(col_id)
    if s is None:
        return "UNMEASURED", {"why": "the colonist was not covered this frame", "sunk": sorted(rep["sunk"])}
    hidden = None
    x = 0.5 * (s["l"] + s["r"])
    lips = [p["b"] for p in rep["pieces"] if p["id"] == col_id and p["kind"] in ("N", "X")]
    if lips:
        hidden = (max(lips) - s["bot"]) / max(EPS, s["top"] - s["bot"])
    det = {"cut": s["cut"], "hiddenShare": hidden, "sunk": s}
    if clamp_on:
        return ("PASS" if not s["cut"] else "FAIL"), det
    if not s["cut"]:
        return "FAIL", det
    lo, hi = x - 0.5 * cut_width, x + 0.5 * cut_width
    inside = [p for p in drawn(rep) if p["id"] == col_id and p["kind"] == "N" and p["r"] > lo + EPS and p["l"] < hi - EPS]
    det["coveredInWindow"] = inside[:4]
    return ("PASS" if not inside else "FAIL"), det


# ============================================================================ live
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--clause", default="all", help="A1, A2, A3 or all")
    ap.add_argument("--origin", default="120,180")
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--out-dir", default=OUT)
    a = ap.parse_args(argv)
    want = {"A1", "A2", "A3"} if a.clause == "all" else {c.strip() for c in a.clause.split(",")}
    import validation_core as V
    B = V.Bridge()
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"script": "proof_pit_lip_cover.py", "clauses": sorted(want), "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "rows": {}}
    stamp = time.strftime("%Y%m%dT%H%M%S")

    def save():
        with open(os.path.join(a.out_dir, "result_%s.json" % stamp), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def sc(typ, method, arg=""):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
        txt = str(r.get("result") if r.get("result") is not None else "")
        return txt if r.get("success") and not txt.startswith("REFUSED") else None

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def frame_and_read(tag, rect):
        x, z, w, h = rect
        B.call("jawa/clear_ui", all=True)
        B.call("rimworld/jump_camera_to_cell", x=int(x + w // 2), z=int(z + h // 2))
        B.call("rimworld/set_camera_zoom", rootSize=14)
        time.sleep(1.0)                      # MapComponentUpdate runs every frame, paused or not
        txt = sc(OCC, "LastFrameCovers")
        res.setdefault("reports", {})[tag] = txt
        if not a.no_shots:
            r = B.call("jawa/take_screenshot", fileName="pitlip_%s_%s" % (tag, stamp)) or {}
            res.setdefault("shots", {})[tag] = r.get("filePath")
        save()
        return parse_report(txt) if txt else None

    ox, oz = (int(v) for v in a.origin.split(","))
    site = (ox - 1, oz - 2, 10, 8)
    saved = {}
    if (B.call("rimworld/get_ui_state") or {}).get("programState") != "Playing":
        print("UNMEASURED: the game is not Playing")
        return 2
    try:
        B.call("rimworld/pause_game", pause=True)
        B.call("jawa/kill_hostiles")
        for f, v in list(SETTINGS.items()) + [("pitSinkClampEnabled", True)]:
            saved[f] = sget(f)
            sset(f, v)
        res["settingsBefore"] = saved
        rr = sc(NSP, "ProofResetRect", "%d;%d;%d;%d" % site)
        rows = []
        if not V.prepare_site(B, site, rows, "PLC_site"):
            res["rows"]["site"] = {"status": "UNMEASURED", "why": "site not ready", "reset": rr, "site": rows[:2]}
            save()
            print("UNMEASURED: site not ready")
            return 2
        for i in range(PIT[2]):
            for j in range(PIT[3]):
                B.call("jawa/flowworks_excavation_drive", x=ox + PIT[0] + i - 1, z=oz + PIT[1] + j - 1,
                       deepenLevels=DEPTH, setFill=0)
        ids = {}
        for name, kind, faction, (dx, dz) in (("muffIn", "Muffalo", "none", MUFF_IN), ("colonist", "Colonist", "player", COLONIST),
                                              ("muffOut", "Muffalo", "none", MUFF_OUT)):
            r = B.call("jawa/spawn_pawn", kindDef=kind, x=ox + dx - 1, z=oz + dz - 1, faction=faction, count=1) or {}
            ids[name] = ((r.get("pawns") or [{}])[0]).get("id")
        res["ids"] = ids
        B.call("rimworld/pause_game", pause=True)
        if not all(ids.values()):
            res["rows"]["spawn"] = {"status": "UNMEASURED", "why": "a spawn failed", "ids": ids}
            save()
            print("UNMEASURED: spawn failed %s" % ids)
            return 2
        rect = (ox - 1, oz - 2, 9, 7)
        west_col, lip_z = ox - 1, oz          # pit columns ox..ox+3, its south row oz: the west overhang column is ox-1
        rep_on = frame_and_read("clamp_on", rect)
        if rep_on is None:
            print("UNMEASURED: LastFrameCovers refused (old DLL deployed?)")
            return 2
        verdicts = {}
        if "A1" in want:
            verdicts["A1"] = v_no_ghost(rep_on, ids["muffOut"])
        if "A2" in want:
            verdicts["A2"] = v_cover_with_pit(rep_on, ids["muffIn"], west_col, lip_z)
        if "A3" in want:
            on = v_window(rep_on, ids["colonist"], True)
            sset("pitSinkClampEnabled", False)
            rep_off = frame_and_read("clamp_off", rect)
            off = v_window(rep_off, ids["colonist"], False) if rep_off else ("UNMEASURED", {"why": "no report"})
            sts = (on[0], off[0])
            st = "PASS" if sts == ("PASS", "PASS") else ("FAIL" if "FAIL" in sts else "UNMEASURED")
            verdicts["A3"] = (st, {"clampOn": on[1], "clampOff": off[1]})
        for k, (st, det) in verdicts.items():
            res["rows"][k] = {"status": st, "detail": det}
            print("%s %s %s" % (k, st, json.dumps(det, default=str)[:400]))
        save()
        sts = [st for st, _ in verdicts.values()]
        return 0 if sts and all(s == "PASS" for s in sts) else (1 if "FAIL" in sts else 2)
    finally:
        for f, v in saved.items():
            if v is not None:
                sset(f, v)
        save()
        print("result: %s" % os.path.join(a.out_dir, "result_%s.json" % stamp))


if __name__ == "__main__":
    sys.exit(main())
