#!/usr/bin/env python3
"""selftest_modset_cameraplus_tier.py -- CAMERAPLUS_TIER_BUILD_EVERY_LIST_ADDS_RIVAL.

resolve_tier adds ray1203.simplecamerasetting (SCS) to every tier that does not set `no_zoom`, so before this item no
load existed where ART_RESOLUTION_MEASURE_AT_MAX_ZOOM A1's precondition (Camera+ at defaults, SCS absent) held, and a
`live-mods:` line cannot say "absent". What must hold, offline, on a fake installed map holding BOTH camera mods:
  - tier cameraplus_nozoom sets no_zoom and resolves to Camera+, the bridge, all five DLC, and never SCS; nothing refused;
  - a dependency that drags SCS back is refused (forbid), never a quieter list;
  - a tier without no_zoom still gets SCS (the owner's 2026-10-04 policy is untouched);
  - write_config does not add SCS to a list holding Camera+;
  - the live-proof file binds A1 to this tier through relentless_live_round.clause_tier, with no live-mods line.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import modset_builder as MB           # noqa: E402
import relentless_live_round as LR    # noqa: E402

TIER = "cameraplus_nozoom"
CAM = "brrainz.cameraplus"
FAILS = []


def ok(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def rec(pid, deps=()):
    return {"packageId": pid, "name": pid, "deps": list(deps), "after": [], "before": [], "dir": "/x/" + pid}


def installed(extra=()):
    ids = [MB.CORE, MB.HARMONY, MB.BRIDGE, MB.ZOOM, CAM, "mandrake.rm.gimmesomeslack"] + list(MB.DLC_IDS)
    m = {p: rec(p) for p in ids}
    for r in extra:
        m[r["packageId"]] = r
    return m


t = MB.TIERS.get(TIER)
ok(t is not None, "tier %s exists" % TIER)
ok(bool(t and t.get("no_zoom")), "tier sets no_zoom")
pids, missing, refusals = MB.resolve_tier(TIER, installed())
ok(CAM in pids, "resolved list holds Camera+")
ok(MB.ZOOM not in pids, "resolved list lacks SimpleCameraSetting")
ok(MB.BRIDGE in pids, "resolved list holds the bridge")
ok(all(d in pids for d in MB.DLC_IDS), "resolved list holds all five DLC")
ok(not missing and not refusals, "nothing missing or refused (%s, %s)" % (missing, refusals))

# a dependency dragging SCS back is a refusal
inst = installed()
inst[CAM] = rec(CAM, deps=[MB.ZOOM])
_, _, ref2 = MB.resolve_tier(TIER, inst)
ok(any(MB.ZOOM in r for r in ref2), "SCS dragged back by a dependency is refused (%s)" % ref2)

# the policy elsewhere is untouched
p_bridge, _, _ = MB.resolve_tier("bridge", installed())
ok(MB.ZOOM in p_bridge, "a tier without no_zoom still gets SCS")

# write_config leaves a Camera+ list without SCS
with tempfile.TemporaryDirectory() as d:
    src = os.path.join(d, "src.xml")
    with open(src, "w") as f:
        f.write("<ModsConfigData>\n  <version>1.6</version>\n  <activeMods>\n  </activeMods>\n</ModsConfigData>\n")
    live = os.path.join(d, "live.xml")
    old = MB.CONFIG
    MB.CONFIG = live
    try:
        MB.write_config(pids, src)
        import xml.etree.ElementTree as ET
        got = [li.text for li in ET.parse(live).getroot().find("activeMods")]
    finally:
        MB.CONFIG = old
    ok(CAM in got and MB.ZOOM not in got, "write_config adds no SCS to the Camera+ list")

# the live-proof binding
lp = os.path.join(REPO, "infrastructure", "state", "live_proofs", "ART_RESOLUTION_MEASURE_AT_MAX_ZOOM.txt")
text = open(lp).read()
ok(LR.clause_tier(text, "A1") == TIER, "A1 binds to %s (got %r)" % (TIER, LR.clause_tier(text, "A1")))
ok(not any(line.lstrip().startswith("live-mods") for line in text.splitlines()), "no live-mods line remains")

print("selftest_modset_cameraplus_tier: %s" % ("FAIL " + "; ".join(FAILS) if FAILS else "OK"))
sys.exit(1 if FAILS else 0)
