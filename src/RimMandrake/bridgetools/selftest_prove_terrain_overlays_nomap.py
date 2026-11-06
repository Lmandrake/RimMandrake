#!/usr/bin/env python3
"""selftest_prove_terrain_overlays_nomap.py (GAMEENV_FIX_PROOFSITE_1C77350A_ITEMS_WAIT): HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK
A1 met a game with no map (map_info "No current map ... map-scoped"). Its live_proofs file must name the lane's
`live_site.py --game` site step for A1 (which starts a quicktest only when no map is up), the lane must accept that command,
and the proof itself, against a fake bridge with no map, must still say NO VERDICT and exit 2 without a single write.
No game, no bridge."""
import contextlib
import io
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
FAILS = []


def check(label, ok):
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        FAILS.append(label)


LP = os.path.join(ROOT, "infrastructure", "state", "live_proofs", "HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK.txt")
prose = open(LP, encoding="utf-8").read() if os.path.exists(LP) else ""
import relentless_live  # noqa: E402
import relentless_live_round as R  # noqa: E402
sites = R.proof_lines(prose, R.SITE_LINE)
proofs = R.proof_lines(prose)
SITE = "python.exe src/RimMandrake/Utils/live_site.py --game"
check("A1 has a live-site line: %r" % sites.get("A1"), sites.get("A1") == SITE)
check("A1's proof line is still there", "prove_terrain_overlays_cleared.py" in proofs.get("A1", ""))
check("A2 has no site line (proof_hose makes its own map)", "A2" not in sites)
check("the lane accepts the site command", relentless_live.refused_site(SITE) is None)

# the proof against a no-map bridge: exit 2, NO VERDICT, nothing but map_info called
NOMAP = {"success": False, "message": "No current map. These tools are map-scoped; use the planet-scoped world tool family instead."}
calls = []


class FakeBridge:
    def __init__(self, **kw):
        pass

    def connect(self):
        pass

    def call(self, tool, args=None, check=True):
        calls.append(tool)
        return NOMAP if tool == "jawa/map_info" else {"success": True}


rb = types.ModuleType("rimbridge_client")
rb.resolve_endpoint = lambda: ("127.0.0.1", 1, "t")
rb.RimBridge = FakeBridge
sys.modules["rimbridge_client"] = rb
import prove_terrain_overlays_cleared as P  # noqa: E402
out = io.StringIO()
with contextlib.redirect_stdout(out):
    rc = P.main([])
check("no map -> exit 2 'NO VERDICT: no map', only map_info called (got %r, %r)" % (rc, calls),
      rc == 2 and out.getvalue().startswith("NO VERDICT: no map") and calls == ["jawa/map_info"])

print("SELFTEST " + ("FAIL: %s" % FAILS if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
