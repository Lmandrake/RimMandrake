#!/usr/bin/env python3
"""selftest_ops_watch_tokentalk_retired.py — a retired tokentalk series is not silent
(TOKENTALK_SILENT_RETIRE_GHOST_SERIES).

BENCH and the conductor role left the token-talk measure on purpose (owner 2026-10-31) and the Arbiter role was
deleted (2026-11-05); their tokentalk.<group>.share keys stop being reported, and the andon silent rule flagged each
as "no longer reported by its collector" — noise, not an outage. A hand-kept silent.skip list held the first three
and missed the Arbiter. ops_watch.tt_retired derives retirement from token_talk's own seats/roles, so a group that
leaves the config retires its series with it.

Checks: (1) on the LIVE rules, every gone series of an unconfigured group (BENCH, commits.BENCH, role.conductor,
role.arbiter) raises no silent flag; (2) a configured group's series that goes UNMEASURED past its limit still does;
(3) the live silent.skip list holds no hand-written tokentalk key (the derived rule replaced it).

    python3 src/RimMandrake/Utils/selftest_ops_watch_tokentalk_retired.py
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["RM_OPS_WATCH_DIR"] = tempfile.mkdtemp(prefix="selftest_ops_watch_tokentalk_retired_")
import ops_watch as ow  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0
HOUR = 3600


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


R = ow.load_rules()
groups = ow.tt_groups(R)
ok("BENCH" not in groups and "role.conductor" not in groups and "role.arbiter" not in groups,
   "live token_talk measures neither BENCH, the conductor role nor the deleted arbiter", groups)

ghosts = ["tokentalk.BENCH.share", "tokentalk.commits.BENCH.share", "tokentalk.role.conductor.share",
          "tokentalk.role.arbiter.share"]
live = ["tokentalk.%s.share" % g for g in groups]
lm = {k: NOW - 30 * HOUR for k in ghosts + live}    # all last MEASURED 30 h ago, well past tokentalk's 6 h limit

# (1) the ghosts are gone from this pass (not reported); the collector itself still runs and reports its live groups
points = {k: ow.M(3.0, "% of reports") for k in live}
silent = {f["key"] for f in ow.andon(points, {}, lm, R, NOW) if f["rule"] == "silent"}
for k in ghosts:
    ok(k not in silent, "1: %s, retired with its group, raises no silent flag" % k, sorted(silent))

# (2) a configured group's series gone blind still raises one, reported UNMEASURED or not reported at all
blind = live[0]
pts2 = dict(points, **{blind: ow.U("3 report(s) in the window, under min_reports 5", "% of reports")})
silent2 = {f["key"] for f in ow.andon(pts2, {}, lm, R, NOW) if f["rule"] == "silent"}
ok(blind in silent2, "2: %s (configured) UNMEASURED past its limit is still silent" % blind, sorted(silent2))
pts3 = {k: p for k, p in points.items() if k != blind}
silent3 = {f["key"] for f in ow.andon(pts3, {}, lm, R, NOW) if f["rule"] == "silent"}
ok(blind in silent3, "2: %s (configured) no longer reported is still silent" % blind, sorted(silent3))

# (3) no hand-kept per-key skip left to rot
skip = R["silent"]["skip"]
ok(not [s for s in skip if s.startswith("tokentalk.")], "3: silent.skip names no tokentalk key by hand", skip)

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
