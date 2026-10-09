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
cs, xml = L.load_repo()
findings, c = L.lint(cs, xml)
if c["defs"] < 1000 or c["ticking_comps"] < 50:
    print("selftest_ticker_compat: repo scan saw too little (%r): UNMEASURED" % (c,))
    sys.exit(1)
print("selftest_ticker_compat: OK (repo scan: %d defs, %d ticking comps judged; %d known findings tracked by TICKER_NEVER_FIRES_FIX_1)"
      % (c["defs"], c["ticking_comps"], len(findings)))
