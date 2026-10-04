"""selftest_lorestages_bars.py -- LORESTAGES_COVERAGE_GAPS_1's offline_mechanism bars are clean on the shipped
source and redden on each break they exist to catch (edited copies in memory / fake runners, never shipped files)."""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def main():
    spec = importlib.util.spec_from_file_location("ls_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    check("shipped: toggle-off and scribe paths wired", v.mechanism_static_problems() == [], v.mechanism_static_problems())

    def reader(edits):
        def r(name):
            s = v._read(name)
            for f, a, b in edits:
                if f == name:
                    assert a in s, (name, a)
                    s = s.replace(a, b, 1)
            return s
        return r

    gc = "GameComponent_LoreStage.cs"
    for label, edit, want in (
        ("toggle no longer zeroes", (gc, "? GetStage(ladderId) : 0;", "? GetStage(ladderId) : GetStage(ladderId);"), "EffectiveStage"),
        ("apply bypasses the toggle", (gc, "tables,\n                EffectiveStage,", "tables,\n                GetStage,"), "ResetAndApply"),
        ("stages not scribed", (gc, '"loreStages"', '"loreStagez"'), "not Scribed"),
        ("FinalizeInit stops applying", (gc, "base.FinalizeInit();\n            Apply();", "base.FinalizeInit();"), "FinalizeInit"),
        ("checkbox stops reapplying", ("RM_LoreStagesMod.cs", "Reapply()", "Nothing()"), "Reapply"),
    ):
        got = v.mechanism_static_problems(reader([edit]))
        check("break: " + label, len(got) == 1 and want in got[0], got)

    tmp = tempfile.mkdtemp()
    try:
        def fake(body, rc):
            p = os.path.join(tmp, "r%d.py" % len(os.listdir(tmp)))
            open(p, "w").write("import sys\nprint(%r)\nsys.exit(%d)\n" % (body, rc))
            return p
        good = "\n".join("ok    " + c for c in v.SELFTEST_REQUIRED) + "\n\n18/18 passed"
        check("fake clean run -> clean", v.offline_selftest_proof(fake(good, 0)) == [])
        got = v.offline_selftest_proof(fake(good.replace("18/18", "17/18"), 1))
        check("break: a failing case -> red", any("not clean" in g for g in got), got)
        got = v.offline_selftest_proof(fake(good.replace("ok    RESET: stage 0", "FAIL  RESET: stage 0"), 0))
        check("break: required case missing -> red", any("RESET: stage 0" in g for g in got), got)
        check("no dotnet -> None (UNMEASURED), never clean",
              v.offline_selftest_proof(fake("dotnet.exe not found", 1)) is None)
    finally:
        import shutil
        shutil.rmtree(tmp)
    print("selftest_lorestages_bars: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
