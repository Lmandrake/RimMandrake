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


for t in (t_91, t_92_93_98, t_94_95, t_97):
    try:
        t()
    except Exception as e:      # noqa: BLE001 - an import failure is a red test
        check(t.__name__ + " ran", False, "%s: %s" % (type(e).__name__, e))
print("FAIL: %s" % FAILS if FAILS else "gss proof drivers: all ok")
sys.exit(1 if FAILS else 0)
