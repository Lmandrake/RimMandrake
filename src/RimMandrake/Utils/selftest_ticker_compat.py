#!/usr/bin/env python3
"""selftest for lint_ticker_compat.py (MOD_TICKER_COMPAT_LINT_1): synthetic fixtures must each be flagged or passed correctly,
and the repo scan must look at real defs and real ticking comps (a lint that looked at nothing reports UNMEASURED, exit 2)."""
import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
lint = os.path.join(here, "lint_ticker_compat.py")
r = subprocess.run([sys.executable, lint, "--selftest"], capture_output=True, text=True)
sys.stdout.write(r.stdout + r.stderr)
if r.returncode:
    sys.exit(1)
sys.path.insert(0, here)
import lint_ticker_compat as L  # noqa: E402
cs, xml, patches = L.load_repo()
findings, c = L.lint(cs, xml, patches)
if c["defs"] < 1000 or c["ticking_comps"] < 50 or c["patched_comps"] < 20 or c["pawn_heat_pushers"] < 3:
    print("selftest_ticker_compat: repo scan saw too little (%r): UNMEASURED" % (c,))
    sys.exit(1)
# HEATPUSHER_FIX_PAWN_DOUBLE_PUSH: a pawn heat pusher that doubles its heat fails this test outright.
double = [f for f in findings if f[0] == "PAWN_DOUBLE_PUSH"]
if double:
    print("selftest_ticker_compat: FAIL\n  " + "\n  ".join("%s: %s" % (os.path.relpath(p, L.REPO), m) for _, p, m in double))
    sys.exit(1)
# TICKERLINT_BUILDINGBASE_WIDEN_VANILLA_NEVER: the repo lint is green, so any NEVER_TICKER / NEVER_TICKS is a regression
# (SHIELDGENERATOR_TICKER_REPAIR_NEVER_TICKS, PIPESEGMENT_TICKER_REPAIR_NEVER_RUPTURES, RM_SolarStill 578c02318e).
if findings:
    print("selftest_ticker_compat: FAIL\n  " + "\n  ".join("%s %s: %s" % (k, os.path.relpath(p, L.REPO), m) for k, p, m in findings))
    sys.exit(1)
# The repaired defs must resolve to a ticker that calls their comps, not merely escape judgement.
want = {"RUT_ShieldGenerator": "Normal", "RUT_PipeSegment": "Normal", "RM_SolarStill": None}
seen = {d["name"]: d["ticker"] for d in L.resolve(L.parse_defs(xml)) if d["name"] in want}
bad = [(n, seen.get(n)) for n, t in want.items() if n not in seen or (t and seen[n] != t) or seen[n] in (None, "Never")]
if bad:
    print("selftest_ticker_compat: repaired defs not resolving to a ticking tickerType: %r" % (bad,))
    sys.exit(1)
print("selftest_ticker_compat: OK (repo scan: %d defs, %d ticking comps judged, %d pawn heat pushers checked, %d with unresolved ticker; "
      "0 findings)" % (c["defs"], c["ticking_comps"], c["pawn_heat_pushers"], c["unresolved_ticker"]))
