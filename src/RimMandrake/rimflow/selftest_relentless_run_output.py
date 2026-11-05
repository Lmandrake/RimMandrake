#!/usr/bin/env python3
"""selftest_relentless_run_output.py — a lost checker says whether it wrote anything (CHECKER_DEATHS_MONITOR_29_NOBODY_NOTICED).

On 2026-11-03 29 of 29 blind checkers died at launch (EACCES) for 2.5 h. The across-items alarm is
CHECKER_DEATHS_ALARM_BUILD_29_WENT_UNHEARD's (ops_watch.rl_checks_lost, selftest_ops_checker_deaths.py); this proves the
"empty output" half: relentless.run_output reads a run's out/err (run_desc) as out_bytes and err_tail, a run it cannot
read is None (never 0), the supervisor's checker_lost act carries it, and rl_checks_lost puts the empty count and the
err in its point and alarm title. Fixtures only.
"""
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "Utils"))
FAILS = []


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def main():
    import relentless as rl
    import ops_watch as ow
    tmp = Path(tempfile.mkdtemp(prefix="rl_run_output_"))
    out, err = tmp / "c.json", tmp / "c.err"
    err.write_text("starting\nmkdir: cannot create '/tmp/rm': Permission denied\n\n")
    got = rl.run_output({"out": str(out), "err": str(err)})
    ok(got == {"out_bytes": 0, "err_tail": "mkdir: cannot create '/tmp/rm': Permission denied"},
       "no out file is out_bytes 0, with the err's last line", got)
    out.write_text('{"x": 1}')
    ok(rl.run_output({"out": str(out), "err": str(err)})["out_bytes"] == 8, "an out file reads its size")
    ok(rl.run_output({"out": str(out), "err": str(tmp / "none.err")})["err_tail"] is None, "a missing err is None")
    ok(rl.run_output(None) == {"out_bytes": None, "err_tail": None}, "no run is unread, never 0")
    src = (HERE / "relentless.py").read_text()
    ok('{"do": "checker_lost", "item": item, **run_output(chk.get("run"))}' in src,
       "the supervisor's checker_lost act carries run_output")

    now = time.time()
    store = tmp / "store"
    store.mkdir()
    rows = [{"at": ow.iso(now - 1800 + 60 * n), "do": "tick",
             "acts": [{"do": "checker_lost", "item": "I%d" % (n % 4), "out_bytes": 0 if n < 5 else 300,
                       "err_tail": "EACCES at launch"}]} for n in range(6)]
    rows.append({"at": ow.iso(now - 600), "do": "tick", "acts": [{"do": "checker_lost", "item": "OLD_ACT"}]})
    (store / "journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    p = ow.rl_checks_lost(store, now, ow.load_rules()["relentless"])
    ok(p["m"] == "MEASURED" and p["v"] == 5 and p["x"]["empty"] == 5 and p["x"]["err"] == "EACCES at launch",
       "rl_checks_lost: 7 deaths on 5 items, 5 wrote nothing (an act without out_bytes is not empty), the err kept", p)
    ok("5 wrote no output" in p["x"]["first"], "the alarm title says how many wrote no output", p["x"]["first"])
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
