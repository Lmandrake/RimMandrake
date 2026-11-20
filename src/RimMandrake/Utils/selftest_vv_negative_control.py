#!/usr/bin/env python3
# selftest-timeout: 900   (stage + build + 2 x 2000 control seeds: 51 s warm; the stage data layer is 9 min cold on D: once per stage folder, measured 2026-11-19)
"""The shipped-settings matrix's negative control, built and run for real (dotnet.exe, offline, no game).

Page: design/specs/2026-11-19-vv-negative-control/boundary.md (each promise has a test of its name here).
Item: RIMMANDRAKE_INSTALL_VV_MATRIX_CLOCK_WRITTEN_NOT_RUNNING. On 2026-11-19 the rm-vv-matrix clock ran 36 min and then
died at its last step: the control (the pre-fix kernel CONTROL_REV compiled with today's ShippedMatrixProbe.cs) no
longer compiled (18 errors: the law plants and trace read k.water / RM_LevelSolve / Notch, which that kernel lacks).
Nothing offline built the control, so the drift was found only by a full run. This test builds it from this tree with
vv_shipped_matrix.stage_flowworks(control=True) (the same function the clock runs, into its own `_selftest` folder so it
never shares a stage with a running clock) and runs vv_shipped_matrix.negative_control on it: red at SHIPPED, 0 at
AUTHORED, the pre-declared criterion (3).
"""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vv_shipped_matrix as M  # noqa: E402

M.STAGE = M.STAGE + "_selftest"   # never the clock's own stage folder
FAILS = []
_BUILT = {}


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + str(detail)) if detail else ""))
    if not ok:
        FAILS.append(name)


def _control_dll():
    """-> (dll path or None, why). Built once per run."""
    if "dll" not in _BUILT:
        try:
            dll = M.stage_flowworks(control=True)
            _BUILT["dll"], _BUILT["why"] = (dll, "") if os.path.isfile(dll) else (None, "no dll at " + dll)
        except SystemExit as e:
            _BUILT["dll"], _BUILT["why"] = None, str(e)
    return _BUILT["dll"], _BUILT["why"]


def t_the_control_builds():
    dll, why = _control_dll()
    check("the-control-builds (pre-fix kernel %s + today's probe compile)" % M.CONTROL_REV, dll is not None, why or dll)


def t_the_control_goes_red():
    dll, why = _control_dll()
    if dll is None:
        check("the-control-goes-red", False, "UNMEASURED: the control did not build (%s)" % why)
        return
    with tempfile.TemporaryDirectory() as td:
        cout = os.path.join(td, "control.jsonl")
        cs, ca, ok = M.negative_control(dll, cout, 1200)
    # worst values, limits, cases read (the bar: SHIPPED failures > 0, AUTHORED failures == 0, both measured)
    check("the-control-goes-red", ok, "SHIPPED %s/%s (limit > 0, unmeasured=%s); AUTHORED %s/%s (limit == 0, exceptions=%s, timed_out=%s)" % (
        cs.get("failures"), cs.get("completed"), cs.get("unmeasured"), ca.get("failures"), ca.get("completed"),
        ca.get("exceptions"), ca.get("timed_out")))


def t_a_plant_or_trace_is_refused_in_the_control():
    dll, why = _control_dll()
    if dll is None:
        check("a-plant-or-trace-is-refused-in-the-control", False, "UNMEASURED: the control did not build (%s)" % why)
        return
    want = "not compiled into the negative-control build"
    with tempfile.TemporaryDirectory() as td:
        out = M.winbuild.win(os.path.join(td, "p.jsonl"))
        runs = {"--plant volume": ["rates", "--config", "X", "--families", "fills_from_limitless", "--n", "3", "--out", out, "--plant", "volume"],
                "trace": ["trace", "--pulses", "2"]}
        got = {k: M._run(dll, a, timeout=300)[:2] for k, a in runs.items()}
    for k, (rc, so) in got.items():
        check("a-plant-or-trace-is-refused-in-the-control (%s)" % k, rc == 2 and want in so, (rc, so.strip()[-160:]))


def t_the_control_is_built_before_the_long_runs():
    """The matrix's main() with every build and run stubbed: a control that does not build stops it before any suite or
    rates run starts."""
    calls = []
    keep = (M.stage_flowworks, M.suite, M.rates, M.stage_ep, M.STAGE)

    def fake_stage(control=False, source_plants=(), tag=""):
        calls.append("stage control" if control else "stage")
        if control:
            sys.exit("VV: build failed for VVControl.csproj (planted)")
        return "probe.dll"

    with tempfile.TemporaryDirectory() as td:
        M.stage_flowworks, M.STAGE = fake_stage, os.path.join(td, "stage")
        M.suite = lambda *a, **k: calls.append("suite") or {}
        M.rates = lambda *a, **k: calls.append("rates")
        M.stage_ep = lambda: calls.append("stage ep") or "ep.dll"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                M.main([])
            stopped = False
        except SystemExit:
            stopped = True
        except Exception as e:   # a stub fed to a run that should never have started (the order is the finding)
            stopped = False
            calls.append("crashed in main: %s %s" % (type(e).__name__, e))
        finally:
            M.stage_flowworks, M.suite, M.rates, M.stage_ep, M.STAGE = keep
    check("the-control-is-built-before-the-long-runs", stopped and "suite" not in calls and "rates" not in calls, calls)


# the files the 25 AUTHORED-suite fails of 2026-11-19 19:06 could not find in the stage (authored_fails.txt of that run)
READ_0619 = ["src/RimMandrake/FlowWorks/northstar/pump_outflow_live.py",
             "src/RimMandrake/Cauldron/Defs/ThingDefs_Buildings/RM_VentGasTap.xml",
             "src/RimMandrake/FlowWorks/Languages/English/Keyed/FlowWorks_Keys.xml",
             "src/RimUtinni/UtinniPatches/Patches/ClimbingGear_JawaFactions.xml",
             "src/RimMandrake/HugeThings/Source/Titanic/WallsSlots/TrenchStrideHook.cs",
             "src/RimMandrake/Pyrelands/Source/RM_TerrainDig.cs",
             "src/RimMandrake/FlowWorks/art_source/Drawbridge/anchor_cable_art.json",
             "src/RimMandrake/GimmeSomeSlack/Defs/Aerial/RM_ConduitStyles.xml",
             "src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll",
             "src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialMath.cs",
             "src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs",
             "src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialLineProfiles.cs",
             "src/RimMandrake/BlueDesert/Defs/ThingDefs_Items/RM_BlueIce.xml",
             "src/RimMandrake/FlowWorks/About/About.xml"]


def stage_misses(dest, rels):
    """-> the rels a selftest would not find in the stage at dest."""
    return [r for r in rels if not os.path.isfile(os.path.join(dest, *r.split("/")))]


def t_the_stage_holds_what_the_suite_reads():
    """Stages into its own folder with four plants, one per regime a later run meets: a file the repo no longer tracks
    (pruned), a tracked file whose repo content changed since the last stage (its manifest key is made old: recopied), a
    staged file that went missing (recopied), and the 14 files the 19:06 fails could not find."""
    import json
    dest = M.STAGE + "_tree"
    stale = os.path.join(dest, "src", "RimMandrake", "ZZ_vv_stale", "Defs", "gone.xml")
    changed, lost = READ_0619[1], READ_0619[2]
    man = os.path.join(dest, M.MANIFEST)
    os.makedirs(os.path.dirname(stale), exist_ok=True)
    open(stale, "w").write("<Defs/>")
    if os.path.isfile(man):
        with open(man, encoding="utf-8") as f:
            had = json.load(f)
        had[changed] = "planted-old-key"
        with open(man, "w", encoding="utf-8") as f:
            json.dump(had, f)
    for rel, junk in ((changed, "planted stale content"), (lost, None)):
        path = os.path.join(dest, *rel.split("/"))
        if junk is None:
            if os.path.exists(path):
                os.remove(path)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w").write(junk)
    try:
        data = M.stage_tree(dest)
    except SystemExit as e:
        check("the-stage-holds-what-the-suite-reads", False, "staging stopped: %s" % e)
        return
    have = M.stage_files(dest, M.compiled())
    miss, extra = sorted(set(data) - have), sorted(have - set(data))
    miss19 = stage_misses(dest, READ_0619)
    same = open(os.path.join(dest, *changed.split("/")), "rb").read() == open(os.path.join(M.ROOT, *changed.split("/")), "rb").read()
    media = [r for r in data if r.lower().endswith(M.MEDIA)]
    built = stage_misses(dest, ["src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs", "src/Directory.Build.props"])
    check("the-stage-holds-what-the-suite-reads", not miss and not extra and not miss19 and same and not media and not built,
          "tracked data files missing %d of %d (limit 0; first %s); untracked files left %d (limit 0, the planted one "
          "among them: %s); 19:06 fail files missing %d of %d (limit 0; %s); changed file recopied %s; media staged %d "
          "(limit 0); compiled tree missing %s" % (
              len(miss), len(data), miss[:3], len(extra), os.path.exists(stale), len(miss19), len(READ_0619), miss19,
              same, len(media), built))


def main():
    t_the_stage_holds_what_the_suite_reads()
    t_the_control_is_built_before_the_long_runs()
    t_the_control_builds()
    t_a_plant_or_trace_is_refused_in_the_control()
    t_the_control_goes_red()
    print("vv negative control: %d failed" % len(FAILS) if FAILS else "vv negative control: all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
