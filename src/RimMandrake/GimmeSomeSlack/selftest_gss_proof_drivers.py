"""Offline guards for the GSS proof-driver review fixes (GSS_PROOF_DRIVERS_FIX_FALSE_PASS, review rows 9.1-9.5, 9.7, 9.8).

Each case is the finding's false-pass scenario fed to the pure verdict it named; it failed before the fix (the helper did not
exist) and passes after. No bridge, no game.
  9.1 validation_style.s9_before_state: S9e's baseline is the read taken just before the save, not the older s10 read
  9.2 validation.m9_bad_log_lines: Player.log error lines naming the mod fail M9
  9.3 validation.m5_verdict: a build that failed, or a far run that did not change, is not "local invalidation"
  9.4 validation_aerial.theft_phase_gap: a --theft phase that wrote no row is owed an UNMEASURED row and a non-zero exit
  9.5 validation_aerial.m19m_status: a tap scene whose conduits are not one net is UNMEASURED SITE
  9.7 Utils/selftest_gimmesomeslack.selftest_cwd: not the read-only mirror
  9.8 validation.clear_off_site: the stub scene outside SITE is destroyed by the suite's finally
GSS_SWITCHES_PROVE_LAST_FOUR_STANDING (the last four switches' pure verdicts):
  M12  validation.plug_tip / slide_under_verdict: slideUnder's plug fraction 0.18/0.82 ON, 0.25/0.5/0.75 OFF
  M21a/b validation_aerial.owner_change_verdict: cutWiresOnOwnerChange kept OFF / gone ON, no span is UNMEASURED
  M21c/d validation_aerial.drip_expected_points / drip_verdict: dripLoops point counts against a port of the C# loops
Run: python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_proof_drivers.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "Utils")))
FAILS = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAILS.append(name)


def has(mod, name):
    ok = hasattr(mod, name)
    check("%s exposes %s" % (mod.__name__, name), ok)
    return ok


def t_91():
    import validation_style as S
    if not has(S, "s9_before_state"):
        return
    old, new = {"st": {"members": [1]}}, {"members": [1, 2]}
    check("9.1 the pre-save read wins over s10's", S.s9_before_state({}, old, new) == new)
    check("9.1 without a pre-save read it falls back to s10, then s9",
          S.s9_before_state({"st": {"a": 1}}, old) == old["st"] and S.s9_before_state({"st": {"a": 1}}, {}) == {"a": 1})
    src = open(os.path.join(HERE, "validation_style.py"), encoding="utf-8").read()
    check("9.1 the save branch passes the pre-save read", "s9_after_load(B, rows, s9, s10, pre_save)" in src)


def t_92_93_98():
    import validation as V
    if has(V, "m9_bad_log_lines"):
        check("9.2 an error line naming the mod fails", V.m9_bad_log_lines(["RimMandrake.GimmeSomeSlack: Exception in Tick"]) != [])
        check("9.2 an info line naming the mod passes", V.m9_bad_log_lines(["[RimMandrake GSS] loaded 3 defs"]) == [])
    if has(V, "m5_verdict"):
        ok_b = {"success": True}
        check("9.3 far run changed + build ok passes", V.m5_verdict(["9,1"], [], ["9,1"], 1, ok_b) is True)
        check("9.3 far run never changed fails", V.m5_verdict([], [], [], 0, ok_b) is False)
        check("9.3 a failed build fails", V.m5_verdict(["9,1"], [], ["9,1"], 1, {"success": False}) is False)
        check("9.3 a change outside the far run fails", V.m5_verdict(["9,1", "2,2"], [], ["9,1"], 1, ok_b) is False)
    if has(V, "clear_off_site"):
        V.OFF_SITE_RECTS[:] = ["5,5,8,6"]
        calls = []
        done = V.clear_off_site(lambda *a, **k: calls.append((a, k)))
        check("9.8 the off-SITE stub rect is destroyed", done == ["5,5,8,6"] and calls and calls[0][1].get("rects") == "5,5,8,6")
        check("9.8 the registry is empty after", V.OFF_SITE_RECTS == [])
        V.OFF_SITE_RECTS[:] = ["1,1,1,1"]
        V.clear_off_site(lambda *a, **k: (_ for _ in ()).throw(RuntimeError("bridge")))
        check("9.8 a throwing destroy does not stop the teardown", V.OFF_SITE_RECTS == [])


def t_94_95():
    import validation_aerial as A
    if has(A, "theft_phase_gap"):
        check("9.4 an unfinished day phase owes its row", A.theft_phase_gap("day", [{"id": "PT_A2_letter"}]) == "PT_A3_goodwill_day")
        check("9.4 a finished day phase owes nothing", A.theft_phase_gap("day", [{"id": "PT_A3_goodwill_day"}]) is None)
    if has(A, "m19m_status"):
        check("9.5 not a mixed net is UNMEASURED SITE", A.m19m_status(False, True) == ("UNMEASURED", "SITE"))
        check("9.5 mixed and connected passes", A.m19m_status(True, True) == ("PASS", "MOD"))
        check("9.5 mixed and not connected fails", A.m19m_status(True, False) == ("FAIL", "MOD"))


def t_97():
    import selftest_gimmesomeslack as G
    if has(G, "selftest_cwd"):
        d = G.selftest_cwd()
        check("9.7 cwd is not the read-only mirror and exists", not d.startswith("/mnt/d/Luke") and os.path.isdir(d), d)
        check("9.7 the run uses it", "cwd=selftest_cwd()" in open(G.__file__, encoding="utf-8").read())


def _ts_count(ln, drip, depth=0.12, reach=0.45, step=0.5):
    """An independent port of AerialMath.SpanCurve / SpanCurveDrip's sample loops (counts the t list they build)."""
    import math
    if not drip or ln < 1e-6:
        return max(4, int(math.ceil(ln / step))) + 1
    reach = min(reach, ln / 4)
    tr = reach / ln
    ts = [tr * k / 6 for k in range(6)]
    n = max(2, int(math.ceil((1 - 2 * tr) * ln / step)))
    ts += [tr + (1 - 2 * tr) * k / n for k in range(n + 1)]
    ts += [1 - tr * k / 6 for k in range(5, -1, -1)]
    return len(ts)


def _into_art(tip, c, slide_dia=None):
    """A strand end as CordBuilder.IntoArt lays it: the routed run up to the plug tip, then (slide) a 0.3 diagonal
    carry in 6 samples, then 0.05 steps to the centroid."""
    pts = [(tip[0], tip[1] - 1.0), (tip[0], tip[1] - 0.5), tip]
    cur = tip
    if slide_dia:
        mid = (tip[0] + slide_dia[0] * 0.3, tip[1] + slide_dia[1] * 0.3)
        pts += [(tip[0] + (mid[0] - tip[0]) * i / 6, tip[1] + (mid[1] - tip[1]) * i / 6) for i in range(1, 7)]
        cur = mid
    d = ((c[0] - cur[0]) ** 2 + (c[1] - cur[1]) ** 2) ** 0.5
    k = max(1, int(d / 0.05 + 0.999))
    pts += [(cur[0] + (c[0] - cur[0]) * i / k, cur[1] + (c[1] - cur[1]) * i / k) for i in range(1, k + 1)]
    return [[round(x, 3), round(z, 3)] for x, z in pts]


def t_m12():
    import validation as V
    if not (has(V, "plug_tip") and has(V, "slide_under_verdict")):
        return
    fp, c = (10, 20, 1, 1), (10.5, 20.5)
    off = V.plug_tip(_into_art((10.5, 19.92), c), fp)
    check("M12 OFF plug tip found 0.08 below a south side, fraction 0.5", off and abs(off[3] - 0.5) < 1e-6 and off[2] == "z", off)
    r = 0.5 ** 0.5
    on = V.plug_tip(_into_art((10.18, 19.92), c, (r, r)), fp)
    check("M12 ON plug tip found past the 0.045 carry sample, fraction 0.18", on and abs(on[3] - 0.18) < 1e-6, on)
    rev = V.plug_tip(list(reversed(_into_art((10.18, 19.92), c, (r, r)))), fp)
    check("M12 a strand laid machine-first reads the same tip", rev == on, rev)
    side = V.plug_tip(_into_art((9.92, 20.25), c), fp)
    check("M12 an x-side plug reads its z fraction", side and side[2] == "x" and abs(side[3] - 0.25) < 1e-6, side)
    check("M12 a strand with no end on the centroid is no tip", V.plug_tip([[0, 0], [1, 1]], fp) is None)
    check("M12 ON fractions pass ON", V.slide_under_verdict([on], True) == ("PASS", "MOD"))
    check("M12 ON fractions fail OFF (a switch that did nothing)", V.slide_under_verdict([on], False) == ("FAIL", "MOD"))
    check("M12 OFF fractions fail ON", V.slide_under_verdict([off, side], True) == ("FAIL", "MOD"))
    check("M12 OFF fractions pass OFF", V.slide_under_verdict([off, side], False) == ("PASS", "MOD"))
    check("M12 no tip is UNMEASURED SITE", V.slide_under_verdict([], True) == ("UNMEASURED", "SITE"))


def t_m21():
    import validation_aerial as A
    if has(A, "owner_change_verdict"):
        a = {"id": 1, "links": [{"other": 2, "state": "Up"}]}
        b = {"id": 2, "links": [{"other": 1, "state": "Up"}]}
        a0, b0 = {"id": 1, "links": []}, {"id": 2, "links": []}
        check("M21a OFF link kept passes", A.owner_change_verdict(False, True, a, b, 1, 2) == ("PASS", "MOD"))
        check("M21a OFF link cut fails", A.owner_change_verdict(False, True, a0, b0, 1, 2) == ("FAIL", "MOD"))
        check("M21a OFF a one-sided link fails", A.owner_change_verdict(False, True, a, b0, 1, 2) == ("FAIL", "MOD"))
        check("M21b ON link gone passes", A.owner_change_verdict(True, True, a0, b0, 1, 2) == ("PASS", "MOD"))
        check("M21b ON link kept fails", A.owner_change_verdict(True, True, a, b, 1, 2) == ("FAIL", "MOD"))
        check("M21b ON half-cut fails", A.owner_change_verdict(True, True, a0, b, 1, 2) == ("FAIL", "MOD"))
        check("M21 a span that never stood is UNMEASURED SITE", A.owner_change_verdict(True, False, a0, b0, 1, 2) == ("UNMEASURED", "SITE"))
        check("M21 an anchor gone from census is UNMEASURED SITE", A.owner_change_verdict(True, True, None, b0, 1, 2) == ("UNMEASURED", "SITE"))
    if has(A, "drip_expected_points") and has(A, "drip_verdict"):
        for ln in (0.9, 1.8, 3.0, 7.25, 11.6, 12.0, 15.3):
            for drip in (False, True):
                got, want = A.drip_expected_points(0, 0, ln, 0, drip), _ts_count(ln, drip)
                check("M21c/d point count len %.2f drip %s matches the C# loop port" % (ln, drip), got == want, (got, want))
        check("M21c 12-cell span OFF is 25 points", A.drip_expected_points(0, 0, 12, 0, False) == 25)
        check("M21d 12-cell span ON is 36 points", A.drip_expected_points(0, 0, 12, 0, True) == 36)
        ends = [[0.0, 0.0, 12.0, 0.0], [0.0, 0.3, 12.0, 0.3]]
        sp_on = [{"kind": "Power", "strandPts": [36, 36], "strandEnds": ends, "verts": 144}]
        sp_off = [{"kind": "Power", "strandPts": [25, 25], "strandEnds": ends, "verts": 100}]
        check("M21d ON counts pass ON", A.drip_verdict(sp_on, True)[:2] == ("PASS", "MOD"))
        check("M21c OFF counts pass OFF", A.drip_verdict(sp_off, False)[:2] == ("PASS", "MOD"))
        check("M21d OFF counts fail ON (the switch did nothing)", A.drip_verdict(sp_off, True)[:2] == ("FAIL", "MOD"))
        check("M21c ON counts fail OFF", A.drip_verdict(sp_on, False)[:2] == ("FAIL", "MOD"))
        check("M21 verts not 2x points fails", A.drip_verdict([dict(sp_on[0], verts=10)], True)[:2] == ("FAIL", "MOD"))
        check("M21 an old build without strandPts is UNMEASURED HARNESS",
              A.drip_verdict([{"kind": "Power", "verts": 144}], True)[:2] == ("UNMEASURED", "HARNESS"))
        check("M21 no Power span is UNMEASURED HARNESS", A.drip_verdict([], True)[:2] == ("UNMEASURED", "HARNESS"))
        check("M21 only undecidable strands is UNMEASURED SITE",
              A.drip_verdict([{"kind": "Power", "strandPts": [5], "strandEnds": [[0, 0, 0, 0]], "verts": 10}], True)[:2]
              == ("UNMEASURED", "SITE"))
        for rid in ("M21a_cut_wires_on_owner_change_off_keeps_link", "M21c_drip_loops_off_plain_curve",
                    "M21e_keep_wires_on_gravship_off_setting_state"):
            check("M21 row id %s is in the aerial source" % rid, rid in open(A.__file__, encoding="utf-8").read())


for t in (t_91, t_92_93_98, t_94_95, t_97, t_m12, t_m21):
    try:
        t()
    except Exception as e:      # noqa: BLE001 - an import failure is a red test
        check(t.__name__ + " ran", False, "%s: %s" % (type(e).__name__, e))
print("FAIL: %s" % FAILS if FAILS else "gss proof drivers: all ok")
sys.exit(1 if FAILS else 0)
