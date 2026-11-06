#!/usr/bin/env python3
"""row_verdict.py -- read ONE modcheck run's results JSON and say whether named rows hold (ACC_BIOMES_FIXES_LIVE_RERUN_1).

    python3 src/RimMandrake/Utils/modcheck/live_queue/row_verdict.py --mod Miasma --max-age-min 30 \
        --row returning_a_young_wins_her_tolerance --unmeasured-ok "no warden mother and no water cell"

It only READS the newest Transient/modcheck/<Mod>_<stamp>.json (runner.write_sheet); the live half is the
`modcheck/cli.py run <Mod> --chains ...` call before it on the same live-proof line.

  --row NAME          a component that must read verdict PASS (repeatable). `~TEXT` matches the one component whose
                      name contains TEXT (exactly one, or it is a FAIL of the reader: an ambiguous row is never a pass).
  --unmeasured-ok RX  an UNMEASURED row whose detail matches RX counts as holding (a site fact the criterion allows).
  --max-age-min N     the newest run must be younger than N minutes (a stale run is not this sitting's evidence).

Exit 0 = every row holds; 1 = a row is missing, FAIL, UNMEASURED (not allowed) or NOT_RUN;
2 = UNMEASURED: modcheck REFUSED the run (summary.refused, e.g. stale_load with chains []), or the run is stale/absent
(PROOF_CRASH_FIX_READ_AS_MOD_FAILURE): nothing ran, so it is neither PASS nor FAIL (MODCHECK_READERS_FIX_REFUSAL_READ_AS_FAIL).
judge() is pure; `--selftest` exercises it offline.
"""
import argparse
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
SHEET_DIR = os.path.join(ROOT, "Transient", "modcheck")


def components(data):
    return [c for ch in ((data or {}).get("summary") or {}).get("chains") or [] for c in ch.get("components") or []]


def refused(data):
    """modcheck's own refusal of the run ('' when it ran): summary.refused; its kind (e.g. stale_load) is
    summary.unmeasured. A refused run's chains are [], so a reader of chains alone would score it FAIL."""
    summ = (data or {}).get("summary") or {}
    return str(summ.get("refused") or "").strip()


def refusal_line(data, path):
    return "UNMEASURED  modcheck refused the run (%s): %s  [%s]" % (
        ((data or {}).get("summary") or {}).get("unmeasured") or "refused", refused(data)[:300], path)


def find(comps, row):
    if row.startswith("~"):
        hits = [c for c in comps if row[1:] in str(c.get("name", ""))]
    else:
        hits = [c for c in comps if c.get("name") == row]
    return hits


def judge(data, rows, unmeasured_ok=None):
    """-> (ok, [one line per row])."""
    comps = components(data)
    ok, lines = True, []
    for row in rows:
        hits = find(comps, row)
        if len(hits) != 1:
            ok = False
            lines.append("%s: %d matching rows (want exactly 1)" % (row, len(hits)))
            continue
        c = hits[0]
        v, detail = str(c.get("verdict")), str(c.get("detail") or "")
        held = v == "PASS" or (v == "UNMEASURED" and unmeasured_ok and re.search(unmeasured_ok, detail))
        ok = ok and bool(held)
        lines.append("%s: %s%s%s" % (c.get("name"), v, " (allowed)" if held and v != "PASS" else "",
                                     (" -- " + detail[:200]) if detail else ""))
    return ok, lines


def newest(sheet_dir, mod):
    runs = sorted(glob.glob(os.path.join(sheet_dir, "%s_*.json" % mod)), key=os.path.getmtime)
    return runs[-1] if runs else None


def check(sheet_dir, mod, rows, max_age_min, unmeasured_ok=None):
    path = newest(sheet_dir, mod)
    # PROOF_CRASH_FIX_READ_AS_MOD_FAILURE: no run, or only an old one, means this proof's run never wrote its JSON (a
    # modcheck crash before it, STILLSAND 2026-11-05): nothing was measured, so UNMEASURED, never the mod's FAIL
    if not path:
        return 2, ["UNMEASURED  no %s run JSON in %s" % (mod, sheet_dir)]
    age = (time.time() - os.path.getmtime(path)) / 60.0
    if age > max_age_min:
        return 2, ["UNMEASURED  newest run %s is %.0f min old (> %d): rerun the live half" % (path, age, max_age_min)]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if data.get("mod") != mod:
        return 1, ["%s names mod %r, not %r" % (path, data.get("mod"), mod)]
    if refused(data):
        return 2, [refusal_line(data, path)]
    ok, lines = judge(data, rows, unmeasured_ok)
    return (0 if ok else 1), ["run %s" % path] + lines


def selftest():
    def d(*comps):
        return {"mod": "M", "summary": {"chains": [{"name": "c", "components": list(comps)}]}}
    P = {"name": "a_round_trips", "verdict": "PASS"}
    F = {"name": "b", "verdict": "FAIL", "detail": "x"}
    U = {"name": "u", "verdict": "UNMEASURED", "detail": "ERROR no warden mother and no water cell on map"}
    U2 = {"name": "u", "verdict": "UNMEASURED", "detail": "bridge timed out"}
    cases = [
        (d(P), ["a_round_trips"], None, True),
        (d(P), ["missing"], None, False),
        (d(F), ["b"], None, False),
        (d(U), ["u"], None, False),                                  # UNMEASURED is not PASS by default
        (d(U), ["u"], "no warden mother and no water cell", True),
        (d(U2), ["u"], "no warden mother and no water cell", False),  # an UNMEASURED of another cause is not allowed
        (d(P, F), ["a_round_trips", "b"], None, False),
        (d(P), ["~round_trips"], None, True),
        (d(P, dict(P, name="z_round_trips")), ["~round_trips"], None, False),   # ambiguous substring
        (d({"name": "n", "verdict": "NOT_RUN"}), ["n"], None, False),
        ({}, ["a"], None, False),
    ]
    bad = 0
    for i, (data, rows, um, want) in enumerate(cases):
        got, lines = judge(data, rows, um)
        if got != want:
            bad += 1
            print("case %d: want %s got %s %s" % (i, want, got, lines))
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, "M_20261105T234400Z.json"), "w", encoding="utf-8") as f:
            json.dump({"mod": "M", "summary": {"chains": [], "refused": "UNMEASURED: the running load is not the "
                       "composed list", "unmeasured": "stale_load"}}, f)
        code, lines = check(td, "M", ["a_round_trips"], 60)
        if code != 2:
            bad += 1
            print("refused run: want exit 2 got %d %s" % (code, lines))
        os.utime(os.path.join(td, "M_20261105T234400Z.json"), (time.time() - 7200, time.time() - 7200))
        code, lines = check(td, "M", ["a_round_trips"], 60)
        if code != 2:
            bad += 1
            print("stale run: want exit 2 got %d %s" % (code, lines))
        code, lines = check(td, "Absent", ["a_round_trips"], 60)
        if code != 2:
            bad += 1
            print("absent run: want exit 2 got %d %s" % (code, lines))
    print("row_verdict selftest: %s (%d cases)" % ("PASS" if not bad else "FAIL", len(cases) + 3))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod")
    ap.add_argument("--row", action="append", default=[])
    ap.add_argument("--unmeasured-ok")
    ap.add_argument("--max-age-min", type=int, default=30)
    ap.add_argument("--dir", default=SHEET_DIR)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.mod or not a.row:
        ap.error("--mod and at least one --row are required")
    code, lines = check(a.dir, a.mod, a.row, a.max_age_min, a.unmeasured_ok)
    print({0: "PASS ", 2: "UNMEASURED "}.get(code, "FAIL ") + a.mod)
    for line in lines:
        print("  " + line)
    return code


if __name__ == "__main__":
    sys.exit(main())
