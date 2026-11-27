#!/usr/bin/env python3
"""selftest_ops_watch_removed_key.py — a series taken out of a collector on purpose is not silent.

f933849106 (RIMMANDRAKE_REMOVE_GRANT_EXPIRY_CHECKS_ONCE_FOUR_COMPANIONS_REDEPLOYED) took companion.grant_hours_left
out of c_companion. last_measured.json keeps its last MEASURED time for good, so the andon silent rule flagged it
"no longer reported by its collector" on every pass from 2026-11-25 (seen 47.7 h at the 2026-11-27 03:31Z digest):
a blind instrument in the digest that is no instrument. REMOVED_FAMILIES retires a whole family; REMOVED_KEYS
retires one key of a family that still runs.

Checks: (1) a REMOVED_KEYS key gone past its limit raises no silent flag; (2) a sibling key of the same family gone
past its limit still does; (3) ops_memory.retired_key says the removed key is retired.

    python3 src/RimMandrake/Utils/selftest_ops_watch_removed_key.py
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["RM_OPS_WATCH_DIR"] = tempfile.mkdtemp(prefix="selftest_ops_watch_removed_key_")
import ops_watch as ow  # noqa: E402
import ops_memory as om  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0
HOUR = 3600


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


R = ow.load_rules()
GONE = "companion.grant_hours_left"
SIB = "companion.grant_visible"
ok(GONE in getattr(ow, "REMOVED_KEYS", ()), "0: %s is in ops_watch.REMOVED_KEYS" % GONE, getattr(ow, "REMOVED_KEYS", None))
lm = {GONE: NOW - 48 * HOUR, SIB: NOW - 48 * HOUR, "companion.grant_test": NOW - 60}
points = {"companion.grant_test": ow.M(1, "")}      # the family still reports; both keys are absent from this pass
silent = {f["key"] for f in ow.andon(points, {}, lm, R, NOW) if f["rule"] == "silent"}
ok(GONE not in silent, "1: %s, taken out of its collector, raises no silent flag" % GONE, sorted(silent))
ok(SIB in silent, "2: %s, gone from a family that still runs, is still silent" % SIB, sorted(silent))
ok(om.retired_key(GONE, R), "3: ops_memory.retired_key(%s) is True" % GONE)
ok(not om.retired_key(SIB, R), "3: ops_memory.retired_key(%s) is False" % SIB)

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
