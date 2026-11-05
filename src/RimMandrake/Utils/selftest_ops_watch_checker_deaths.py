#!/usr/bin/env python3
"""selftest_ops_watch_checker_deaths.py — CHECKER_DEATHS_MONITOR_29_NOBODY_NOTICED: a run of dead checkers alarms.

On 2026-11-03 every blind checker died at launch (EACCES) for 2.5 h, none gave a verdict, none wrote output; each item
saw only its own checker_lost and no alarm said so. The reading is relentless.checker_deaths_run
(ops_watch.rl_checker_deaths_run): the different items in the run of checker deaths that ends now, across items, with
no verdict between and every death empty. This test:
  - replays the REAL journal of that afternoon (selftest_fixtures/relentless_checker_deaths_2026-11-03.jsonl: the
    check_started, checker_lost, verdict and done acts of 2026-11-03T17:00..22:33Z, cut from the live store's
    journal.jsonl) through a real ops_watch pass on the REAL ops_watch_rules.json: the alarm fires at 20:15Z, and the
    run reaches 30 deaths at 22:30Z; at 19:30Z, before the incident, it does not;
  - a verdict breaks the run: the same deaths with a blind_fail (or a check_passed) between leave only the tail, and
    no alarm;
  - empty output is in the condition: the same deaths each with out_bytes > 0 (a checker that started and wrote)
    raise none; out_bytes 0 counts as empty, None/absent as unknown (still in the run);
  - a done act (an item closed off the checker) does not break it: one landed mid-incident on 2026-11-03;
  - deaths older than checker_run_window_h raise none; an unreadable journal is UNMEASURED.
Fixtures only: a temp store, a temp RM_OPS_WATCH_DIR, a fake filer.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []
KEY = "relentless.checker_deaths_run"
REAL = HERE / "selftest_fixtures" / "relentless_checker_deaths_2026-11-03.jsonl"


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def main():
    import ops_watch as ow
    tmp = Path(tempfile.mkdtemp(prefix="ow_checker_run_"))
    store = tmp / "store"
    store.mkdir()
    rules = ow.load_rules()
    cfg = rules["relentless"]
    tg = [t for t in rules["targets"] if t["key"] == KEY]
    ok(len(tg) == 1 and tg[0].get("alarm") is True and tg[0]["op"] == ">" and tg[0]["value"] == 2
       and tg[0]["name"] == "OPS_CHECKER_RUN_DIAGNOSE_NO_VERDICT",
       "the real rules hold one alarm target on it, above 2 items", tg)
    alarm = "%s:%s" % (tg[0]["tag"], KEY) if tg else None
    real = REAL.read_text()

    def journal(text):
        (store / "journal.jsonl").write_text(text)

    def rows(*rs):
        return "".join(json.dumps(r) + "\n" for r in rs)

    def tick(t, *acts):
        return {"at": ow.iso(t), "do": "tick", "acts": list(acts)}

    def death(item, out=0):
        a = {"do": "checker_lost", "item": item, "err_tail": "Permission denied (EACCES) at launch"}
        if out != "absent":
            a["out_bytes"] = out
        return a

    def point(text, now):
        journal(text)
        return ow.rl_checker_deaths_run(store, now, cfg)

    saved = os.environ.get("RM_OPS_WATCH_DIR")
    coll = ow.COLLECTORS["relentless"]
    passes = []

    def one_pass(text, now):
        journal(text)
        passes.append(1)
        os.environ["RM_OPS_WATCH_DIR"] = str(tmp / ("ops%d" % len(passes)))
        ow.COLLECTORS["relentless"] = lambda n, r, c: {KEY: ow.rl_checker_deaths_run(store, n, r["relentless"]),
                                                       "relentless.blind": ow.M(0, "sources not seen", cause="none")}
        rr = ow.load_rules()        # the real targets; only their Conductor log is a temp file
        for t in rr["targets"]:
            if t.get("conductor_log"):
                t["conductor_log"] = str(tmp / "conductor_log.md")
        return ow.run(now=now, rules=rr, filer=lambda todo, conf: {a["name"]: None for a in todo},
                      families=["relentless"])["alarms"]

    try:
        # the real afternoon
        e = ow.epoch
        p = point(real, e("2026-11-03T22:30:00Z"))
        ok(p["m"] == "MEASURED" and p["v"] == 17 and p["x"]["deaths"] == 30,
           "the real journal at 22:30Z: 30 checkers in a row on 17 items with no verdict", p)
        ok(p["x"]["unknown"] == 30 and p["x"]["empty"] == 0,
           "acts from before run_output carry no out_bytes: unknown, still in the run", p["x"])
        ok("done" not in p["x"]["broken_by"] and p["x"]["since"] == "2026-11-03T19:57:37Z",
           "the done that landed mid-incident (22:08Z) did not break the run; it runs from 19:57Z", p["x"])
        ok(alarm in one_pass(real, e("2026-11-03T20:15:00Z")), "a real pass on the real journal alarms at 20:15Z")
        ok(alarm in one_pass(real, e("2026-11-03T22:30:00Z")), "and still at 22:30Z")
        ok(alarm not in one_pass(real, e("2026-11-03T19:30:00Z")), "and not at 19:30Z, before the incident")

        # a verdict breaks the run
        now = e("2026-11-05T12:00:00Z")
        run = [tick(now - 3000 + 200 * n, death("ITEM_%d" % n)) for n in range(8)]
        ok(point(rows(*run), now)["v"] == 8, "8 empty deaths on 8 items in a row read 8")
        ok(alarm in one_pass(rows(*run), now), "and alarm")
        for verdict in ("blind_fail", "check_passed", "game_entered", "proof_weak", "unmeasured"):
            broken = run[:6] + [tick(now - 3000 + 200 * 6 - 50, {"do": verdict, "item": "OTHER"})] + run[6:]
            q = point(rows(*broken), now)
            ok(q["v"] == 2 and verdict in q["x"]["broken_by"], "a %s between breaks the run: 2 left" % verdict, q)
        broken = run[:6] + [tick(now - 3000 + 200 * 6 - 50, {"do": "blind_fail", "item": "OTHER"})] + run[6:]
        ok(alarm not in one_pass(rows(*broken), now), "and a pass on the broken run raises none")
        interleaved = [r for n, x in enumerate(run) for r in (x, tick(now - 3000 + 200 * n + 100,
                                                                      {"do": "blind_fail", "item": "ITEM_%d" % n}))]
        ok(alarm not in one_pass(rows(*interleaved), now), "deaths each followed by a verdict raise none")
        q = point(rows(*(run[:6] + [tick(now - 3000 + 200 * 6 - 50, {"do": "live_broken", "item": "OTHER", "after_check": True})] + run[6:])), now)
        ok(q["v"] == 2, "a live_broken read after a checker's PASS breaks it", q)
        q = point(rows(*(run[:6] + [tick(now - 3000 + 200 * 6 - 50, {"do": "live_broken", "item": "OTHER"})] + run[6:])), now)
        ok(q["v"] == 8, "a closing retry's live_broken (no checker) does not", q)
        done = run[:6] + [tick(now - 3000 + 200 * 6 - 50, {"do": "done", "item": "OTHER"})] + run[6:]
        ok(point(rows(*done), now)["v"] == 8, "a done between does not break it")

        # empty output is in the condition
        wrote = [tick(now - 3000 + 200 * n, death("ITEM_%d" % n, out=300)) for n in range(8)]
        q = point(rows(*wrote), now)
        ok(q["v"] == 0, "8 deaths that each wrote output read 0", q)
        ok(alarm not in one_pass(rows(*wrote), now), "and raise none")
        mid = run[:5] + [tick(now - 3000 + 200 * 5 - 50, death("MID", out=4096))] + run[5:]
        ok(point(rows(*mid), now)["v"] == 3, "one death that wrote output breaks the run: 3 left")
        q = point(rows(*run), now)
        ok(q["x"]["empty"] == 8 and q["x"]["unknown"] == 0 and "EACCES" in q["x"]["err"],
           "out_bytes 0 counts empty, with the err tail", q["x"])
        mixed = [tick(now - 3000 + 200 * n, death("I%d" % n, out=(0, None, "absent")[n % 3])) for n in range(6)]
        q = point(rows(*mixed), now)
        ok(q["v"] == 6 and q["x"]["empty"] == 2 and q["x"]["unknown"] == 4, "None and absent are unknown, kept", q["x"])
        launch = [tick(now - 600 + 100 * n, {"do": "check_launch_fail", "item": "L%d" % n, "why": "EACCES"})
                  for n in range(3)]
        q = point(rows(*launch), now)
        ok(q["v"] == 3 and q["x"]["empty"] == 3, "check_launch_fail is an empty death", q["x"])

        # across items, window, blindness
        same = [tick(now - 3000 + 200 * n, death("ONE")) for n in range(8)]
        ok(alarm not in one_pass(rows(*same), now), "one item's checker dying 8 times is 1 item: none")
        old = [tick(now - 4 * 3600 + 60 * n, death("OLD_%d" % n)) for n in range(8)]
        ok(point(rows(*old), now)["v"] == 0, "deaths outside the window read 0")
        (store / "journal.jsonl").unlink()
        q = ow.rl_checker_deaths_run(store, now, cfg)
        ok(q["m"] == "UNMEASURED", "no journal is UNMEASURED, never 0", q)
    finally:
        ow.COLLECTORS["relentless"] = coll
        if saved is None:
            os.environ.pop("RM_OPS_WATCH_DIR", None)
        else:
            os.environ["RM_OPS_WATCH_DIR"] = saved
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
