"""selftest_rustcathedral_wornbit.py -- RUSTCATHEDRAL_WORN_BIT_ARC_1, offline: validation.wornbit_problems is clean on the
shipped mod and reddens on each break it exists to catch (planted in a temp copy), and the arc kernel passes its criteria
under dotnet through the Attitude selftest project (--fuzz-only wornbit)."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _sub(path, old, new):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    assert old in text, (path, old)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new, 1))


def main():
    spec = importlib.util.spec_from_file_location("rc_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    bad, unmeasured = v.wornbit_problems()
    check("shipped: arc clean", bad == [], bad)
    check("shipped: campaign files seen", unmeasured == [], unmeasured)

    def planted(label, rel, old, new, expect):
        tmp = tempfile.mkdtemp()
        try:
            for d in ("Defs", "Patches", "Source"):
                shutil.copytree(os.path.join(HERE, d), os.path.join(tmp, d), ignore=shutil.ignore_patterns("obj", "bin", "__pycache__"))
            _sub(os.path.join(tmp, rel), old, new)
            got, _u = v.wornbit_problems(mod_root=tmp)
            check(label, any(expect in g for g in got), got)
        finally:
            shutil.rmtree(tmp)

    heads = os.path.join("Defs", "ThingDefs_Items", "RM_WornBitDrillHeads.xml")
    misc = os.path.join("Defs", "Misc", "RM_WornBit.xml")
    races = os.path.join("Defs", "ThingDefs_Races", "RM_Borehulk.xml")
    planted("light head reddens", heads, "<Mass>250</Mass>", "<Mass>25</Mass>", "mass")
    planted("lost job reddens", os.path.join("Defs", "JobDefs", "RM_WornBitJobs.xml"), "<defName>RM_Job_RestoreBorehulk</defName>",
            "<defName>RM_Job_RestoreBorehulkX</defName>", "RM_Job_RestoreBorehulk")
    planted("a dropped part reddens", misc, "<PowerfocusChip>1</PowerfocusChip>", "", "restoration parts")
    planted("a short count reddens", misc, "<RM_DeadSmartsteel>12<", "<RM_DeadSmartsteel>2<", "RM_DeadSmartsteel")
    planted("inherited overseer reddens", races, '<comps Inherit="False">', "<comps>", "mechanitor")
    planted("no dig job reddens", os.path.join("Defs", "ThinkTreeDefs", "RM_ThinkTree_Borehulk.xml"),
            '<li Class="RimMandrake.RustCathedral.RM_JobGiver_BorehulkWork" />', "", "dig job")
    planted("no refurbisher reddens", os.path.join("Patches", "RM_WornBit.xml"), 'FactionDef[defName="Pirate"]', 'FactionDef[defName="Nobody"]', "Pirate")
    planted("a buff reddens", os.path.join("Source", "RustCathedral", "RM_WornBitDig.cs"), "comp.cellsMined++;",
            "comp.cellsMined++; pawn.health.AddHediff(null);", "buff")
    tmp = tempfile.mkdtemp()
    try:
        bad_patch = os.path.join(tmp, "p.xml")
        with open(bad_patch, "w", encoding="utf-8") as fh:
            fh.write('<Patch><Operation MayRequire="x" Class="PatchOperationAdd" /></Patch>')
        got, _u = v.wornbit_problems(rut_patch=bad_patch)
        check("a thin campaign patch reddens", any("campaign patch lacks" in g for g in got), got)
        check("a guarded top-level MayRequire reddens", any("MayRequire" in g for g in got), got)
    finally:
        shutil.rmtree(tmp)
    check("no campaign patch says UNMEASURED", any("campaign patch" in u for u in v.wornbit_problems(rut_patch="/nonexistent")[1]))

    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    fuzz = os.path.join(REPO, "src", "RimMandrake", "Utils", "selftest_rustcathedral_attitude_fuzz.py")
    r = subprocess.run([sys.executable, fuzz, "--fuzz-only", "wornbit"], capture_output=True, text=True, timeout=400)
    print("\n".join(x for x in r.stdout.splitlines() if x.startswith(("FAIL", "WORNBIT"))))
    check("arc kernel passes under dotnet", r.returncode == 0 and "WORNBIT PASS" in r.stdout, (r.stdout + r.stderr)[-600:])
    print("%s (%d failures)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
