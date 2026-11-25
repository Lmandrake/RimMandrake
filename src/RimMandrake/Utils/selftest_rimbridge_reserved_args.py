#!/usr/bin/env python3
"""selftest_rimbridge_reserved_args.py - rimbridge_client lets the companion's reserved expect* arguments through.

The companion reads expectGameEpoch / expectMapId / expectCurrentMapId from the RAW argument dictionary at the binder
(JawaBenchCompanionSafety.CheckReserved), on every tool, so no tool declares them. check_params refused them as
undeclared (2026-11-25, Steve1 lane job J20261125T203006Z-f50231: "jawa/map_info does not declare expectCurrentMapId,
expectGameEpoch"), so no Python caller could use the stale-target guard. A truly undeclared key is still refused."""
import os
import sys

os.environ.setdefault("RIMBRIDGE_SESSION_LOG", "")
os.environ.setdefault("RIMBRIDGE_EVIDENCE_LOG", "")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as RC  # noqa: E402

FAILS = []
b = RC.RimBridge.__new__(RC.RimBridge)
b._param_index = {"jawa/map_info": {"mapId"}}
try:
    r = b.check_params("jawa/map_info", {"expectGameEpoch": 3, "expectMapId": 1, "expectCurrentMapId": 1})
    print("ok   reserved expect* arguments pass (%s)" % r)
except RC.UnknownParameterError as e:
    print("FAIL reserved expect* arguments refused: %s" % str(e)[:160])
    FAILS.append("reserved")
try:
    b.check_params("jawa/map_info", {"expectGameEpoch": 3, "dryRun": True})
    print("FAIL an undeclared key passed with a reserved one")
    FAILS.append("undeclared")
except RC.UnknownParameterError:
    print("ok   an undeclared key is still refused")
print("RESULT: %s" % ("FAIL %s" % FAILS if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
