"""Offline selftest for prove_roof_cover.py, the A2 live proof of STILLSAND_ROOF_COVER_EXPOSURE_1.

The live line exits 0 only when modcheck's own results JSON for THIS run holds sun_roof_cover_above_55deg as PASS.
Here modcheck is faked (subprocess.call writes a results JSON the way runner.write_sheet does) so the verdict
reading is proven without the game: PASS -> 0; FAIL, UNMEASURED, a missing row -> 1; no JSON from this run, or only
a stale JSON from an earlier run -> 2. It also pins that the proof asks modcheck for exactly that row on Stillsand.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("prove_roof_cover", os.path.join(HERE, "prove_roof_cover.py"))
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

ROW = "sun_roof_cover_above_55deg"


def _summary(verdict, row=ROW):
    comps = [{"name": "sun_pinned_elevation", "verdict": "PASS", "detail": "61 deg"}]
    if verdict is not None:
        comps.append({"name": row, "verdict": verdict, "detail": "roofed 0.35 open 1.00"})
    return {"chains": [{"name": "sun", "components": comps}]}


def run_case(verdict, row=ROW, write=True, stale=False):
    """-> (exit code, argv modcheck was called with)."""
    root = tempfile.mkdtemp(prefix="prove_roof_cover_")
    out = os.path.join(root, "Transient", "modcheck")
    os.makedirs(out)
    seen = {}

    def write_json(name, when=None):
        p = os.path.join(out, name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"mod": "Stillsand", "stamp": "x", "summary": _summary(verdict, row)}, f)
        if when is not None:
            os.utime(p, (when, when))

    if stale:                                   # an earlier run's PASS must not count for this one
        write_json("Stillsand_old.json", when=time.time() - 3600)

    def fake_call(argv, **kw):
        seen["argv"] = argv
        if write:
            write_json("Stillsand_new.json")
        return 0

    old_root, old_call = P.ROOT, P.subprocess.call
    P.ROOT, P.subprocess.call = root, fake_call
    try:
        return P.main(), seen.get("argv")
    finally:
        P.ROOT, P.subprocess.call = old_root, old_call
        shutil.rmtree(root, ignore_errors=True)


def main():
    fails = []

    def expect(label, got, want):
        ok = got == want
        print("%-4s %-34s exit %s (want %s)" % ("ok" if ok else "FAIL", label, got, want))
        if not ok:
            fails.append(label)

    rc, argv = run_case("PASS")
    expect("row PASS", rc, 0)
    pinned = bool(argv) and "Stillsand" in argv and "--rows" in argv and argv[argv.index("--rows") + 1] == ROW
    expect("asks modcheck for the row", pinned, True)
    expect("row FAIL", run_case("FAIL")[0], 1)
    expect("row UNMEASURED", run_case("UNMEASURED")[0], 1)
    expect("row missing", run_case(None)[0], 1)
    expect("other row PASS, ours absent", run_case("PASS", row="sun_open_sand_full_exposure")[0], 1)
    expect("no results JSON", run_case("PASS", write=False)[0], 2)
    expect("only a stale PASS JSON", run_case("PASS", write=False, stale=True)[0], 2)
    print("RESULT: %s" % ("FAIL " + ", ".join(fails) if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
