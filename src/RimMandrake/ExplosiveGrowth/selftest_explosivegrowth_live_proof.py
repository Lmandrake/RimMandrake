#!/usr/bin/env python3
"""EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY: live_proof.py's exit code says what the game measured, and nothing else.

relentless_live.py reads a live proof's exit as 0 PASS, 1 FAIL, anything else UNMEASURED. At 0d984538 the T2 run FAILED
because python.exe never launched (WSL 'UtilAcceptVsock accept4 failed 110'): live_proof.py read "the driver wrote no
out file" as exit 1, while the same chain's T2 bar had read PASS in the T1 run 25 s earlier. This test drives
live_proof.main() with a FAKE driver (no game, no python.exe, no wslpath) and checks the whole table:

  bar PASS -> 0 · bar FAIL -> 1 · no out file / not JSON / bar absent / bar duplicated / status UNMEASURED, REFUSED,
  NOT_RUN or missing -> 2 · each clause reads ITS OWN bar (T1 tinder_leaves_fuel, T2 tinder_off_falls_back_to_churn),
  and the driver is asked for chain top_tinder with an --out naming a file of this run.

Then the same table runs on in-memory mutants of live_proof.py (no-out-file back to 1, status-blind PASS, absent bar
read as FAIL, T2 pointed at T1's bar); each must go red, so the instrument is shown to see.

    python3 src/RimMandrake/ExplosiveGrowth/selftest_explosivegrowth_live_proof.py
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(HERE, "live_proof.py")
fails = []

T1_BAR = "top_tinder.tinder_leaves_fuel"
T2_BAR = "top_tinder.tinder_off_falls_back_to_churn"


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def load(src, name="live_proof_under_test"):
    mod = types.ModuleType(name)
    mod.__file__ = SRC_PATH
    exec(compile(src, SRC_PATH, "exec"), mod.__dict__)
    return mod


def drive(mod, clause, payload, scratch):
    """Run mod.main for `clause` with a fake driver that writes `payload` (dict -> JSON, str -> raw text, None -> no
    file) to the --out it was given. -> (exit code, the argv the driver got)."""
    seen = {}

    def fake_run(argv):
        seen["argv"] = list(argv)
        out_win = argv[argv.index("--out") + 1]
        path = os.path.join(scratch, out_win.split("\\")[-1])
        if payload is None:
            return 1
        with open(path, "w") as f:
            f.write(payload if isinstance(payload, str) else json.dumps(payload))
        return 0

    mod.SCRATCH = scratch
    mod.win = lambda p: "W:" + p.replace("/", "\\")
    mod.run = fake_run
    with contextlib.redirect_stdout(io.StringIO()):     # the proof's own prints; the verdict is the rc
        rc = mod.main(["live_proof.py", clause])
    return rc, seen.get("argv", [])


def bars(*pairs):
    return {"bars": [{"id": i, "status": s, "detail": ""} for i, s in pairs]}


def table(mod, scratch):
    """-> list of (case name, expected rc, actual rc)."""
    rows = []

    def case(name, clause, payload, want):
        rc, _ = drive(mod, clause, payload, scratch)
        rows.append((name, want, rc))

    case("T1 bar PASS -> 0", "T1", bars((T1_BAR, "PASS"), (T2_BAR, "FAIL")), 0)
    case("T1 bar FAIL -> 1", "T1", bars((T1_BAR, "FAIL"), (T2_BAR, "PASS")), 1)
    case("T2 bar PASS -> 0", "T2", bars((T1_BAR, "FAIL"), (T2_BAR, "PASS")), 0)
    case("T2 bar FAIL -> 1", "T2", bars((T1_BAR, "PASS"), (T2_BAR, "FAIL")), 1)
    case("T2 no out file (driver never ran) -> 2", "T2", None, 2)
    case("T1 no out file -> 2", "T1", None, 2)
    case("T2 out file not JSON -> 2", "T2", "<3>WSL ERROR", 2)
    case("T2 out file JSON but not an object -> 2", "T2", "[1, 2]", 2)
    case("T2 bar absent -> 2", "T2", bars((T1_BAR, "PASS")), 2)
    case("T2 bar duplicated -> 2", "T2", bars((T2_BAR, "PASS"), (T2_BAR, "PASS")), 2)
    for st in ("UNMEASURED", "REFUSED", "NOT_RUN", None, "pass"):
        case("T2 bar status %r -> 2" % (st,), "T2", bars((T1_BAR, "PASS"), (T2_BAR, st)), 2)
    return rows


def table_ok(rows):
    return all(want == got for _, want, got in rows)


def main():
    src = open(SRC_PATH).read()
    scratch = tempfile.mkdtemp(prefix="eg_live_proof_")
    try:
        mod = load(src)
        for name, want, got in table(mod, scratch):
            check(name, want == got, "rc %r" % got)

        # the driver call itself: chain top_tinder for both clauses, an --out of this run's own file, the plan named
        rc, argv = drive(load(src), "T2", bars((T2_BAR, "PASS")), scratch)
        check("driver argv: python.exe ... run --mod ExplosiveGrowth", argv[:1] == ["python.exe"]
              and argv[2:5] == ["run", "--mod", "ExplosiveGrowth"], argv)
        check("driver argv: --chains top_tinder", "--chains" in argv and argv[argv.index("--chains") + 1] == "top_tinder",
              argv)
        check("driver argv: --plan northstar_plan.py", "--plan" in argv
              and argv[argv.index("--plan") + 1].endswith("northstar_plan.py"), argv)
        outs = set()
        for _ in range(3):
            _, a = drive(load(src), "T2", bars((T2_BAR, "PASS")), scratch)
            outs.add(a[a.index("--out") + 1])
        check("each run writes its own --out name (a stale file can never pass)", len(outs) == 3, outs)
        with contextlib.redirect_stdout(io.StringIO()):
            usage_rc = load(src).main(["live_proof.py", "T9"])
        check("usage error is not 0 or 1", usage_rc not in (0, 1), usage_rc)

        # controls: each mutant must turn the table red
        mutants = {
            "no out file read as FAIL (the 0d984538 bug)": (
                'print("%s UNMEASURED: the driver wrote no %s (exit %d)" % (clause, out, rc))\n        return UNMEASURED',
                'print("%s FAIL: the driver wrote no %s (exit %d)" % (clause, out, rc))\n        return 1'),
            "absent / unmeasured bar read as FAIL": (
                'print("%s UNMEASURED: %s -> %r (out %s)" % (clause, bar, r, out))\n        return UNMEASURED',
                'print("%s FAIL: %s -> %r (out %s)" % (clause, bar, r, out))\n        return 1'),
            "status-blind PASS": ('return 0 if r[0] == "PASS" else 1', 'return 0'),
            "T2 pointed at T1's bar": ('"T2": ("top_tinder", "top_tinder.tinder_off_falls_back_to_churn")',
                                       '"T2": ("top_tinder", "top_tinder.tinder_leaves_fuel")'),
            "UNMEASURED constant 1": ("UNMEASURED = 2\n", "UNMEASURED = 1\n"),
        }
        for name, (old, new) in mutants.items():
            present = src.count(old) == 1
            check("mutant site present: " + name, present, "pattern count %d" % src.count(old))
            if not present:
                continue
            try:
                red = not table_ok(table(load(src.replace(old, new), "mutant"), scratch))
            except Exception as e:     # a mutant that crashes the harness is also red
                red = True
                print("      (mutant raised %r)" % e)
            check("mutant goes red: " + name, red)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print("RESULT", "GREEN" if not fails else "RED (%d)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
