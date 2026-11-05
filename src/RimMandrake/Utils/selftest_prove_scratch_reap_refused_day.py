#!/usr/bin/env python3
"""selftest_prove_scratch_reap_refused_day.py -- the day-long refused proof goes red on every way the Done-when breaks.

Builds synthetic reaper state dirs (runs.jsonl, runs.jsonl.1, sanity.json) in a temp dir; never reads the real one."""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["PROVE_REFUSED_DAY_SELFTEST"] = "1"
import prove_scratch_reap_refused_day as P  # noqa: E402

FAILS = []
NOW = "2026-11-06T04:00:00Z"
T = P.parse_ts(NOW)


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def run(ts, refuse, apply=True, young=5):
    rows = [{"verdict": "REFUSE", "path": f"/x/{i}"} for i in range(refuse)]
    rows += [{"verdict": "YOUNG", "path": f"/y/{i}"} for i in range(young)]
    return {"ts": P.fmt(ts), "apply": apply, "rows": rows}


def build(td, runs, rotated=(), sanity_refused=31, sanity_age_h=0.5, limits_line=60):
    sd = Path(tempfile.mkdtemp(dir=td))
    (sd / "runs.jsonl").write_text("".join(json.dumps(r) + "\n" for r in runs))
    if rotated:
        (sd / "runs.jsonl.1").write_text("".join(json.dumps(r) + "\n" for r in rotated))
    if sanity_refused is not None:
        (sd / "sanity.json").write_text(json.dumps({"end": {"at": T - sanity_age_h * 3600,
                                                            "measures": {"refused": sanity_refused}}}))
    lim = sd / "limits.json"
    lim.write_text(json.dumps({"end": {"refused": limits_line}}))
    return sd, lim


def verdict(sd, lim):
    ok, out = P.prove(sd, lim, T, 24.0, 2.0, 3.0)
    return ok, out


def hourly(refuse=31, hours=25):
    return [run(T - h * 3600 + 120, refuse) for h in range(hours, 0, -1)]


def main():
    td = tempfile.mkdtemp(prefix="selftest_prove_refused_day_")
    try:
        base = hourly()
        ok, out = verdict(*build(td, base))
        check(ok, "a day of hourly runs at 31 with a fresh sanity end at 31 is green")
        ok, _ = verdict(*build(td, base[:-1] + [run(T - 600, 60)]))
        check(ok, "a run exactly at the line (60) is not over it, as judge_sanity reads it")
        # the checker's gap: one post-fix spike inside the day must turn it red
        spiked = list(base)
        spiked[12] = run(P.parse_ts(spiked[12]["ts"]), 63)
        ok, out = verdict(*build(td, spiked))
        check(not ok and any("refused 63 over 60" in l for l in out), "one run at 63 inside the day is red")
        dry = list(base)
        dry.insert(5, run(P.parse_ts(base[5]["ts"]) + 600, 61, apply=False))
        ok, _ = verdict(*build(td, dry))
        check(not ok, "a hand dry run over the line counts too")
        # a spike older than the day is outside it
        old = [run(T - 30 * 3600, 1072)] + base
        ok, _ = verdict(*build(td, old))
        check(ok, "a 1072 run 30 h ago is outside the day")
        # rotated file is read: a spike there inside the window is red
        ok, _ = verdict(*build(td, base[10:], rotated=[dict(r) for r in base[:9]] + [run(P.parse_ts(base[9]["ts"]), 81)]))
        check(not ok, "a spike in runs.jsonl.1 inside the day is red")
        ok, _ = verdict(*build(td, base[10:], rotated=base[:10]))
        check(ok, "a clean day split across runs.jsonl.1 and runs.jsonl is green")
        # coverage: under a day of records is not a day
        ok, out = verdict(*build(td, hourly(hours=20)))
        check(not ok and any("not covered" in l for l in out), "20 h of runs is not a day")
        holed = base[:8] + base[13:]
        ok, out = verdict(*build(td, holed))
        check(not ok and any("gap" in l for l in out), "a 5 h hole with no run is red")
        ok, out = verdict(*build(td, base[:-3]))
        check(not ok and any("newest run" in l for l in out), "no run in the last 3 h is red")
        ok, out = verdict(*build(td, []))
        check(not ok, "an empty runs.jsonl is red")
        # sanity.json end
        ok, _ = verdict(*build(td, base, sanity_refused=81))
        check(not ok, "sanity.json end refused 81 is red")
        ok, _ = verdict(*build(td, base, sanity_age_h=5))
        check(not ok, "a stale sanity.json end is red")
        ok, _ = verdict(*build(td, base, sanity_refused=None))
        check(not ok, "a missing sanity.json is red")
        sd, lim = build(td, base)
        (sd / "sanity.json").write_text(json.dumps({"end": {"at": T, "measures": {"refused": None}}}))
        check(not verdict(sd, lim)[0], "sanity.json end refused with no reading is red")
        # unreadable records
        sd, lim = build(td, base)
        with open(sd / "runs.jsonl", "a") as f:
            f.write("{not json\n")
        check(not verdict(sd, lim)[0], "an unparseable run line is red")
        sd, lim = build(td, base)
        lines = (sd / "runs.jsonl").read_text().splitlines()
        r = json.loads(lines[-1])
        del r["rows"]
        lines[-1] = json.dumps(r)
        (sd / "runs.jsonl").write_text("\n".join(lines) + "\n")
        check(not verdict(sd, lim)[0], "a run in the day with no rows is red")
        sd, lim = build(td, base)
        os.remove(sd / "runs.jsonl")
        check(not verdict(sd, lim)[0], "a missing runs.jsonl is red")
        sd, lim = build(td, base)
        lim.write_text("{}")
        check(not verdict(sd, lim)[0], "an unreadable end line is red")
        # the line is read from the limits file, not hard-wired
        ok, _ = verdict(*build(td, base, limits_line=30))
        check(not ok, "with the end line at 30, runs at 31 are red")
        # the shipped limits file carries the 60 the item names
        line = json.loads((HERE / "scratch_reap_sanity.json").read_text())["end"]["refused"]
        check(line == 60, f"shipped end.refused line is 60 (read {line})")
        # CLI: a window under a day is refused outside the selftest
        os.environ.pop("PROVE_REFUSED_DAY_SELFTEST")
        check(P.main(["--hours", "3", "--state-dir", td]) == 2, "--hours under 24 is refused")
        os.environ["PROVE_REFUSED_DAY_SELFTEST"] = "1"
        sd, lim = build(td, base)
        check(P.main(["--state-dir", str(sd), "--limits", str(lim), "--now", NOW]) == 0, "CLI exits 0 on a green day")
        sd, lim = build(td, spiked)
        check(P.main(["--state-dir", str(sd), "--limits", str(lim), "--now", NOW]) == 1, "CLI exits 1 on a spiked day")
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print(f"selftest_prove_scratch_reap_refused_day: {'FAIL' if FAILS else 'PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
