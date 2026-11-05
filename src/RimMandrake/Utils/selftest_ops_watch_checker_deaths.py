#!/usr/bin/env python3
"""selftest_ops_watch_checker_deaths.py — CHECKER_DEATHS_MONITOR_29_NOBODY_NOTICED: the 2026-11-03 run alarms.

On 2026-11-03 29 of 29 blind checkers died at launch (EACCES) for 2.5 h; each item saw only its own checker_lost and
no alarm said so. The reading is relentless.checks_lost_items (ops_watch.rl_checks_lost, from the twin item
CHECKER_DEATHS_ALARM_BUILD_29_WENT_UNHEARD); this replays the incident's shape, with the empty output the supervisor
now records (relentless.run_output), through a real ops_watch pass on the REAL ops_watch_rules.json:
  - an hour of the incident (12 deaths on 8 items, no output, EACCES) raises RELENTLESS_CHECKERS_DYING, and its
    point says how many wrote no output and the err;
  - the journal's normal worst (2 items lost a checker) raises none;
  - deaths older than the window raise none.
Fixtures only: a temp store, a temp RM_OPS_WATCH_DIR, a fake filer.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []
KEY = "relentless.checks_lost_items"


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def lost(item):
    return {"do": "checker_lost", "item": item, "out_bytes": 0, "err_tail": "Permission denied (EACCES) at launch"}


def main():
    import ops_watch as ow
    now = time.time()
    tmp = Path(tempfile.mkdtemp(prefix="ow_checker_deaths_"))
    store = tmp / "store"
    store.mkdir()
    rules = ow.load_rules()
    tg = [t for t in rules["targets"] if t["key"] == KEY]
    ok(len(tg) == 1 and tg[0].get("alarm") is True and tg[0]["op"] == ">" and tg[0]["value"] == 2,
       "the real rules hold one alarm target on it, above 2 items", tg)
    alarm = "%s:%s" % (tg[0]["tag"], KEY) if tg else None

    def journal(rows):
        (store / "journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))

    def tick(t, *acts):
        return {"at": ow.iso(t), "do": "tick", "acts": list(acts)}

    incident = [tick(now - 3300 + 270 * n, lost("ITEM_%d" % (n % 8)), {"do": "check_started", "item": "ITEM_%d" % n},
                     {"do": "lease", "item": "W%d" % n}) for n in range(12)]
    journal(incident)
    p = ow.rl_checks_lost(store, now, rules["relentless"])
    ok(p["m"] == "MEASURED" and p["v"] == 8 and p["x"]["lost"] == 12 and p["x"]["verdicts"] == 0,
       "the incident hour reads 8 items, 12 lost, 0 verdicts", p)
    ok(p["x"].get("empty") == 12 and "EACCES" in p["x"].get("err", ""), "and says all 12 wrote no output, with the err",
       p["x"])

    saved = {k: os.environ.get(k) for k in ("RM_OPS_WATCH_DIR",)}
    coll = ow.COLLECTORS["relentless"]
    passes = []

    def one_pass(rows):
        journal(rows)
        passes.append(1)
        os.environ["RM_OPS_WATCH_DIR"] = str(tmp / ("ops%d" % len(passes)))
        ow.COLLECTORS["relentless"] = lambda n, r, c: {KEY: ow.rl_checks_lost(store, n, r["relentless"]),
                                                       "relentless.blind": ow.M(0, "sources not seen", cause="none")}
        return ow.run(now=now, rules=ow.load_rules(), filer=lambda todo, conf: {a["name"]: None for a in todo},
                      families=["relentless"])["alarms"]
    try:
        ok(alarm in one_pass(incident), "a real pass raises the alarm on the incident")
        ok(alarm not in one_pass([tick(now - 900, lost("A")), tick(now - 600, lost("B")), tick(now - 300, lost("A"))]),
           "the normal worst (2 items) raises none")
        ok(alarm not in one_pass([tick(now - 3 * 3600 + n, lost("OLD_%d" % n)) for n in range(6)]),
           "deaths outside the window raise none")
    finally:
        ow.COLLECTORS["relentless"] = coll
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
