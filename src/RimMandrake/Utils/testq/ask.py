#!/usr/bin/env python3
"""ask.py - the whole `testq.py submit` line for one item, after the host's facts (RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS).

tiers_of(text, pid_of) -> ({tier: [clause, ...]}, why not): each live-proof clause's own list, read by proof_lines.py.

plan(item, facts, stale, live_proofs, table, tiers, mod=None, sha="origin/main", companion=None)
  -> {"verdict": "ASK"|"CANNOT"|"COULD NOT LOOK"|"HOLD", "argv": [...], "why": [...]}
Order: stale or missing facts first (COULD NOT LOOK, nothing sent); then a chain with no driver (CANNOT); then what the host lacks
(CANNOT, named); a missing companion alone is HOLD: the job is queued and the lane's admission holds it until the companion is
staged (testq.companion_unready). It judges nothing about what to test.
"""
import os
import sys

import host_facts as HF

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "rimflow"))


def tiers_of(text, pid_of):
    """-> ({tier: [clauses]}, None), or (None, why no lane job can run this file). pid_of(name) -> a packageId or None."""
    import proof_lines as PL
    proofs = PL.proof_lines(text)
    if not proofs:
        return {}, None
    try:
        if PL.live_menu(text) or PL.live_toggle(text):
            return None, "its proofs want the main menu or a pair of loads; the lane stages neither"
        named = PL.live_tiers(text)
        default = None
        if any(not PL.clause_tier(text, c, named) for c in proofs):
            pids = []
            for m in PL.live_mods(text):
                pid = pid_of(m)
                if not pid:
                    return None, "live-mods names %s, which is no mod of the repo and no packageId" % m
                pids.append(pid)
            default, why = PL.mods_tier(pids)
            if why:
                return None, why
        out = {}
        for c in sorted(proofs):
            out.setdefault(PL.clause_tier(text, c, named) or default, []).append(c)
        return out, None
    except ValueError as e:
        return None, str(e)


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
