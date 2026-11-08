"""g8_kit.py -- batch B of the pass-8 gallery: wall ladders, portable ladders, the suspension bridge and climbing gear,
on RM_FW_Gallery8.

  python.exe ralph/live/g8_kit.py [--save RM_FW_Gallery8] [--no-load] [--parts ladders,portables,bridge,gear]
                                  [--treatments 0,1,2] [--settle-ms 500] [--tag t]

parts (default all):
  ladders    B1 (5x5 pit, 2 m): a colonist on the floor; all four RM_Ladder lowered (ProofLadder lower, the gizmo's own
             writer) -> shots at 7.2 and 20 + reachability out; all four raised -> shots + reachability out.
  portables  B2: a colonist in each 3x3 pit (portable on N, E, S, W at 2 m; the too-deep control with a portable on every
             wall; a bare 2 m pit with none). Per pit: Reaches() of each portable, ProofReach to a cell outside,
             ProofClimb held/trapped; shots at 7.2 (two frames) and 20.
  bridge     B3 (hole 5 x 9, 2 m, timber suspension bridge east-west over its middle row): for each treatment
             (RM_SuspensionHang.SetTreatment, skipped with UNMEASURED when the build lacks it) shots at 7.2 and 20;
             then a colonist on the hole floor walks north -> under the deck -> south: BEFORE, MID, AFTER at 7.2 with the
             camera fixed, its reach/underpath read before the walk.
  gear       B4: RM_ClimbingGear on the ground beside a vanilla jump pack, and the site's wearer: 7.2 and 20, then the
             wearer facing east, north and west at 7.2.

Reachability: RM_SuspensionProofs.ProofReach("pawnId;x,z") is Reachability.CanReach with the pawn's TraverseParms plus
the A* path (reach=, found=); RM_NorthstarProofs.ProofClimb("pawn:<id>") says held/trapped; RM_LadderUtility.Reaches(ladder)
says whether a portable spans its wall. Output: Transient/ralph_fw/g8/kit_<tag>_<HHMMSS>/.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g8_common as C  # noqa: E402
from g8_common import j, scall  # noqa: E402


def reach_out(B, R, pid, outside, name, expect=None, **extra):
    st, txt = scall(B, C.SUSP, "ProofReach", "%s;%d,%d" % (pid, outside[0], outside[1]))
    st2, txt2 = scall(B, C.NSP, "ProofClimb", "pawn:%s" % pid)
    d = C.kv(txt) if st == "OK" else {}
    reach = d.get("reach")
    v = {"reach": reach, "found": d.get("found"), "veto": d.get("veto"), "climb": txt2[:160] if st2 == "OK" else st2,
         "raw": txt[:200]}
    v.update(extra)
    if st != "OK" or reach is None:
        R.result(name, v, expected=expect, ok="UNMEASURED", source="ProofReach")
    elif expect is None:
        R.result(name, v, ok=None, source="ProofReach+ProofClimb")
    else:
        R.result(name, v, expected="reach=%s" % expect, ok=(reach == str(expect)), source="ProofReach+ProofClimb")
    return reach


def things_at(B, defname, cell):
    r = B.call("jawa/list_things", defName=defname, rect="%d,%d,1,1" % tuple(cell), limit=10) or {}
    return r.get("things") or r.get("rows") or []


def ladders(B, R, L, a):
    b1 = L["B1"]
    pid = C.subject(B, R, b1["subject"], "B1 floor")
    for state in ("lower", "raise"):
        reads = {}
        for rot, c in sorted(b1["ladders"].items()):
            st, txt = scall(B, C.PROMO, "ProofLadder", "%d,%d,%s" % (c[0], c[1], state))
            d = C.kv(txt)
            reads["NESW"[rot]] = {"present": d.get("present"), "raised": d.get("raised"), "inspect": d.get("inspect"),
                                  "status": st}
        C.redraw(B, R)
        C.settle(B, a.settle_ms)
        want = "False" if state == "lower" else "True"
        good = all(v.get("raised") == want for v in reads.values()) and len(reads) == 4
        R.result("B1_ladders_%s" % state, reads, expected="4 present, raised=%s" % want, ok=good, source="ProofLadder")
        if pid:
            reach_out(B, R, pid, b1["outside"], "B1_reach_out_%s" % state, expect=(state == "lower"))
        tag = "lowered" if state == "lower" else "raised"
        C.shot(B, R, "B1_%s" % tag, b1["rect"], C.ROOT_PLAY)
        C.shot(B, R, "B1_%s" % tag, b1["rect"], C.ROOT_WIDE)


def portables(B, R, L, a):
    pids = {}
    for p in L["B2"]:
        pids[p["tag"]] = C.subject(B, R, p["subject"], "B2 %s" % p["tag"])
    C.settle(B, a.settle_ms)
    for p in L["B2"]:
        spans = {}
        for rot, c in sorted(p["portables"].items()):
            th = things_at(B, "RM_LadderPortable", c)
            if not th:
                spans["NESW"[rot]] = "absent"
                continue
            tid = th[0].get("id") or th[0].get("thingId")
            st, txt = scall(B, C.LADU, "Reaches", tid)
            spans["NESW"[rot]] = txt if st == "OK" else st
        deep = p["tag"] == "deep"
        if p["portables"]:
            want = "False" if deep else "True"
            good = all(v == want for v in spans.values())
            R.result("B2_%s_portable_spans" % p["tag"], spans, expected="Reaches=%s" % want, ok=good,
                     source="RM_LadderUtility.Reaches", levels=p.get("levels") or C.depth_at(B, p["subject"]))
        pid = pids.get(p["tag"])
        if pid:
            reach_out(B, R, pid, p["outside"], "B2_%s_reach_out" % p["tag"], expect=(p["tag"] not in ("deep", "bare")),
                      levels=C.depth_at(B, p["subject"]))
    C.shot(B, R, "B2_N_E_S_W_deep_bare", L["B2_rects"]["all"], C.ROOT_PLAY)
    C.shot(B, R, "B2_N_E_S_W_deep_bare", L["B2_rects"]["all"], C.ROOT_WIDE)


def bridge(B, R, L, a):
    b3 = L["B3"]
    st, txt = scall(B, C.SUSP, "ProofSpan", "%d,%d" % (b3["x0"] + 2, b3["deck_z"]))
    R.result("B3_span", txt[:240], ok=None if st == "OK" else "UNMEASURED", source="ProofSpan")
    treats = [int(t) for t in a.treatments.split(",")] if a.treatments else []
    have = None
    for t in treats:
        st, txt = scall(B, C.T_HANG, C.M_TREAT, t)
        if st == "MISSING":
            have = False
            R.result("B3_treatment_%d" % t, txt[:160], expected="SetTreatment(%d)" % t, ok="UNMEASURED",
                     source="RM_SuspensionHang.SetTreatment")
            break
        have = True
        R.result("B3_treatment_%d" % t, txt[:200], ok=None if st == "OK" else "UNMEASURED",
                 source="RM_SuspensionHang.SetTreatment")
        C.redraw(B, R)
        C.settle(B, 300)
        C.shot(B, R, "B3_t%d" % t, b3["rect"], C.ROOT_PLAY)
        C.shot(B, R, "B3_t%d" % t, b3["rect"], C.ROOT_WIDE)
    if not have:
        C.settle(B, 300)
        C.shot(B, R, "B3_asbuilt", b3["rect"], C.ROOT_PLAY)
        C.shot(B, R, "B3_asbuilt", b3["rect"], C.ROOT_WIDE)
    elif treats and treats[-1] != 0:
        scall(B, C.T_HANG, C.M_TREAT, 0)   # the walk under the default look (suspension)
        C.redraw(B, R)
    start, mid, end = b3["walk"]
    pid = C.subject(B, R, start, "B3 walker", face=None)
    if not pid:
        return
    st, txt = scall(B, C.SUSP, "ProofUnderPath", "%s;%d,%d" % (pid, end[0], end[1]))
    R.result("B3_underpath", txt[:200], ok=None if st == "OK" else "UNMEASURED", source="ProofUnderPath")
    reach_out(B, R, pid, end, "B3_reach_end", expect=True)
    C.settle(B, a.settle_ms)
    C.shot(B, R, "B3_walk_BEFORE", b3["rect"], C.ROOT_PLAY, frame=True, wait=1.5)
    for name, cell in (("MID", mid), ("AFTER", end)):
        arrived, at = C.walk_to(B, R, pid, cell, wait_ticks=120)
        C.settle(B, a.settle_ms)
        rd = C.read_pawn(B, R, pid, "B3 " + name)
        R.result("B3_walk_%s" % name, {"at": at, "want": cell, "arrived": arrived, "depth": C.depth_at(B, at or cell),
                                       "sink": rd["sink"], "src": rd["src"]},
                 expected="on the hole floor at %s" % (cell,), ok=arrived, source="pawn_census")
        C.shot(B, R, "B3_walk_%s" % name, b3["rect"], C.ROOT_PLAY, frame=False)


def gear(B, R, L, a):
    b4 = L["B4"]
    wearer = None
    for p in C.colonists(B):
        if (p.get("x"), p.get("z")) == tuple(b4["wearer"]):
            wearer = p.get("id")
    if not wearer:
        R.harness_error("no wearer on %s: spawning one" % (b4["wearer"],))
        wearer = C.subject(B, R, b4["wearer"], "B4 wearer")
        if wearer:
            B.call("jawa/pawn_gear", pawn=wearer, action="wear", **{"def": "RM_ClimbingGear"})
    R.result("B4_ground", {"gear": len(things_at(B, "RM_ClimbingGear", b4["gear"])),
                           "vanilla": len(things_at(B, b4["vanillaDef"], b4["vanilla"]))},
             expected={"gear": 1, "vanilla": 1}, ok=None, source="list_things")
    if wearer:
        B.call("jawa/set_pawn_rotation", pawnId=wearer, dir="south", lockRotation=True)
    C.settle(B, a.settle_ms)
    C.shot(B, R, "B4_ground_and_worn_S", b4["rect"], C.ROOT_PLAY)
    C.shot(B, R, "B4_ground_and_worn_S", b4["rect"], C.ROOT_WIDE)
    if wearer:
        for d in ("east", "north", "west"):
            B.call("jawa/set_pawn_rotation", pawnId=wearer, dir=d, lockRotation=True)
            C.settle(B, 0)
            C.shot(B, R, "B4_worn_%s" % d[0].upper(), b4["rect"], C.ROOT_PLAY, frame=(d == "east"))
        B.call("jawa/set_pawn_rotation", pawnId=wearer, dir="south", lockRotation=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", default=C.SAVE)
    ap.add_argument("--no-load", action="store_true")
    ap.add_argument("--origin", default=None)
    ap.add_argument("--parts", default="ladders,portables,bridge,gear")
    ap.add_argument("--treatments", default="0,1,2")
    ap.add_argument("--settle-ms", type=int, default=500)
    ap.add_argument("--tag", default="b")
    a = ap.parse_args()
    parts = a.parts.split(",")
    L = C.layout(tuple(int(v) for v in a.origin.split(",")) if a.origin else None)
    B = C.bridge()
    R = C.Run("kit", a.tag)
    try:
        if not a.no_load and not C.load_gallery(B, R, a.save):
            return
        C.pause(B, R)
        C.draft_all(B, R)
        R.result("build_reads", {"SetTreatment": C.scall(B, C.T_HANG, C.M_TREAT, "-1")[0],
                                 "portableReach": C.setting(B, "portableLadderMaxLevels"),
                                 "B1": C.depth_at(B, L["B1"]["subject"]),
                                 "B2": {p["tag"]: C.depth_at(B, p["subject"]) for p in L["B2"]},
                                 "B3": C.depth_at(B, L["B3"]["walk"][0])},
                 source="static_call probe + excavation")
        for name, fn in (("ladders", ladders), ("portables", portables), ("bridge", bridge), ("gear", gear)):
            if name in parts:
                R.log("== part", name)
                fn(B, R, L, a)
        C.finish_shots(R)
    except Exception as e:  # noqa: BLE001
        import traceback
        R.harness_error("UNCAUGHT %s: %s | %s" % (type(e).__name__, e, traceback.format_exc()[-900:]))
    finally:
        try:
            C.pause(B)
        except Exception:  # noqa: BLE001
            pass
        R.close()


if __name__ == "__main__":
    main()
