#!/usr/bin/env python3
"""selftest_liveround_stale_build.py -- LIVEROUND_STALE_BUILD_SILENCE_RETRIES: a build whose game files changed since it
was built is refused once and stays refused for that sha; it is never retried (the 6 h unmeasured_retry_s is gone: PACING_PRUNE_LLMS_SLOW_ENOUGH_ALONE).

First seen: EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS A2, round 2026-11-02T04:14:51Z, RUT_ExplosiveGrowthRoster.xml changed
at 5afbec097e. The rule lives in relentless_live_round.decides/due; this file proves only that rule, so an unrelated red
check elsewhere (selftest_relentless_live_round.py) cannot hide or fake it. No game, no bridge, no ledger.

    python3 src/RimMandrake/rimflow/selftest_liveround_stale_build.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_live_round as R      # noqa: E402

FAILS = []
NOW = 1_800_000_000
RETRY = 6 * 3600        # the 6 h unmeasured_retry_s the item names, now gone: ages around it still never run a stale row
CRON = 1                # the supervisor's own round (candidates/due's cron flag); 0 is a game phase's round
NO_GAME = "no game can measure this build"


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def stale_row(age_s, sha="5afbec097e"):
    # the exact shape relentless_live.stale_build writes ("%s, so the game cannot run %s: %s" % (STALE, sha, ...))
    why = "%s, so the game cannot run %s: %s" % (
        R.L.STALE, sha, "src/RimUtinni/X/Defs/RUT_ExplosiveGrowthRoster.xml (beefcafe01)")
    return {"item": "EGROSTER_X", "criterion": "A2", "sha": sha, "outcome": "UNMEASURED",
            "at": R.L.iso(NOW - age_s), "why": why}


def item(sha):
    return {"id": "EGROSTER_X", "state": "built", "built_sha": sha, "title": "t",
            "criteria": [{"id": "A2", "level": "L1", "text": "x"}], "outstanding": ["A2"]}


PROSE = "live-proof A2: python3 live_log_check.py --absent RUT_A\n"


def t_instrument_sees():
    """Sanity probe: an ordinary UNMEASURED row on the same sha DOES come due (no game to key on, no timer), so a
    refusal below is the stale rule, not an instrument that refuses everything."""
    plain = dict(stale_row(60), why="the proof exited 2: x")
    check("probe: an ordinary UNMEASURED a minute old comes due (no nap)", R.due(plain, plain["sha"], NOW, CRON) is None,
          R.due(plain, plain["sha"], NOW, CRON))
    check("probe: an ordinary UNMEASURED does not decide", not R.decides(plain))


def t_stale_is_terminal_for_its_sha():
    for age in (0, RETRY - 1, RETRY + 1, 7 * 3600, 30 * 86400):
        row = stale_row(age)
        got = R.due(row, row["sha"], NOW, CRON)
        check("stale: refused at age %ds (never a 6 h retry)" % age, got == NO_GAME, got)
        for game, per_game in (("G1", True), ("G2", False)):
            got = R.due(row, row["sha"], NOW, 0, game, per_game=per_game)
            check("stale: refused at age %ds, game %s, retry 0" % (age, game), got == NO_GAME, got)
    check("stale: the row decides its build", R.decides(stale_row(30 * 86400)))


def t_new_sha_runs_again():
    row = stale_row(60)
    check("stale: a new sha runs again", R.due(row, "0123abcd99", NOW, CRON) is None,
          R.due(row, "0123abcd99", NOW, CRON))


def t_history_and_candidates():
    old = stale_row(7 * 3600)
    later = dict(old, at=R.L.iso(NOW - 60), why="the proof exited 2: x")
    hist = R.history([old, later])
    check("history: the stale row outlives a later plain row on its sha",
          hist[("EGROSTER_X", "A2", old["sha"])]["why"].startswith(R.L.STALE))
    todo, counts = R.candidates([item(old["sha"])], lambda i: PROSE, R.history([old]), NOW, CRON)
    check("round: the stale build is not a candidate after 7 h", todo == [] and counts.get(NO_GAME) == 1,
          (todo, counts))
    todo, counts = R.candidates([item("0123abcd99")], lambda i: PROSE, R.history([old]), NOW, CRON)
    check("round: a rebuilt sha is a candidate", len(todo) == 1, (todo, counts))


def main():
    for t in (t_instrument_sees, t_stale_is_terminal_for_its_sha, t_new_sha_runs_again, t_history_and_candidates):
        t()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
