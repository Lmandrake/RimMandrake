#!/usr/bin/env python3
"""ask.py - the whole `testq.py submit` line for one item, after the host's facts (RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS).

plan(item, facts, stale, live_proofs, table, tiers, mod=None, sha="origin/main", companion=None)
  -> {"verdict": "ASK"|"CANNOT"|"COULD NOT LOOK"|"HOLD", "argv": [...], "why": [...]}
Order: stale or missing facts first (COULD NOT LOOK, nothing sent); then a chain with no driver (CANNOT); then what the host lacks
(CANNOT, named); a missing companion alone is HOLD (the job waits until it is staged). It judges nothing about what to test.
"""
import host_facts as HF


def plan(item, facts, stale, live_proofs, table, tiers, mod=None, sha="origin/main", companion=None):
    if stale or not isinstance(facts, dict):
        return {"verdict": "COULD NOT LOOK", "argv": [], "why": ["host facts are stale or missing: refresh them (host_facts.py refresh)"]}
    why = []
    for row, t in sorted((table or {}).items()):
        if isinstance(t, dict) and t.get("live_check_owed"):
            why.append("%s: live check owed, the lane has no driver for it" % row)
    if not live_proofs:
        why.append("%s has no live-proof line, so the lane has nothing to run" % item)
    if why:
        return {"verdict": "CANNOT", "argv": [], "why": why}
    need = {"mods": sorted({m for ms in (tiers or {}).values() for m in ms})}
    gone = HF.lacks(need, facts, False)
    if gone:
        return {"verdict": "CANNOT", "argv": [], "why": ["%s %s is %s on the host" % (k, n, w) for k, n, w in gone]}
    argv = ["submit", mod or item, "--for-item", item, "--sha", sha, "--proofs", ",".join(sorted(live_proofs))]
    if tiers:
        argv += ["--profile", "tier:" + sorted(tiers)[0]]
    held = HF.lacks({"companion": companion}, facts, False) if companion else []
    return {"verdict": "HOLD" if held else "ASK", "argv": argv, "why": ["companion %s is not staged yet" % companion] if held else []}
