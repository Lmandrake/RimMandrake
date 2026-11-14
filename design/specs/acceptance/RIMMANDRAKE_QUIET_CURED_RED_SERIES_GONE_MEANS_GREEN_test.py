#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_QUIET_CURED_RED_SERIES_GONE_MEANS_GREEN.

A per-red series testing.red_<group> stops being reported when its nightly red goes green or its test is deleted;
the andon silent rule flagged each one "no longer reported by its collector" (36 flags, 11-14). While the nightly
collector itself still reports, a gone red series is the instrument saying "not red", never a blind instrument.

Checks: (1) gone testing.red_<x>, collector alive -> no silent flag; (2) the collector's own aggregate gone -> still
silent; (3) a red series still reported but UNMEASURED past its limit -> still silent; (4) a non-red testing series
gone -> still silent.
    python3 design/specs/acceptance/RIMMANDRAKE_QUIET_CURED_RED_SERIES_GONE_MEANS_GREEN_test.py   (expect 5 PASS)
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
os.environ["RM_OPS_WATCH_DIR"] = tempfile.mkdtemp(prefix="accept_cured_red_")
import ops_watch as ow  # noqa: E402

FAILS = []
NOW, HOUR = 1_800_000_000.0, 3600


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


R = ow.load_rules()
AGG, OTHER = "testing.nightly_news", "testing.nothing_h_7d"
cured, cured2, still = "testing.red_aaaaaa", "testing.red_bbbbbb", "testing.red_cccccc"
lm = {k: NOW - 30 * HOUR for k in (AGG, OTHER, cured, cured2, still)}
alive = {AGG: ow.M(0, "entries"), OTHER: ow.M(3.0, "h"), still: ow.M(1, "red")}


def silent(points):
    return {f["key"] for f in ow.andon(points, {}, lm, R, NOW) if f["rule"] == "silent"}


s1 = silent(alive)
ok(cured not in s1 and cured2 not in s1, "1: gone red series, collector alive: no silent flag", sorted(s1))
ok(still not in s1, "1: a red still reported MEASURED is not silent", sorted(s1))
s2 = silent({k: p for k, p in alive.items() if k != AGG})
ok(AGG in s2, "2: the collector's aggregate gone is still silent", sorted(s2))
s3 = silent(dict(alive, **{still: ow.U("collector could not read it", "red")}))
ok(still in s3, "3: a red series reported UNMEASURED past its limit is still silent", sorted(s3))
s4 = silent({k: p for k, p in alive.items() if k != OTHER})
ok(OTHER in s4, "4: a non-red testing series gone is still silent", sorted(s4))
print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
