"""Acceptance: a second steward run launched on a mod whose road back is already open must not orphan the first
steward's filings. maturation_autonomy._execute_one sets road_back = {"caused_by": <new steward item>} on every
exit_not_met/exit_met steward launch, so the items the first steward filed (caused_by its own item) are no longer what
the road back asks the ledger for. GimmeSomeSlack, 2026-11-15: RIMMANDRAKE_PAIR_GSS_TWIN_LEADS_ACROSS_PIECES_SIX_LEFT,
caused by ..._FAILURES_BACK, dropped out of the road back when ..._FAILURES_BACK_RUN_TWO launched.
rc 1 on the base ab86199dfe; rc 0 on a fix (the road back still names the first steward's item, in any shape)."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import maturation_autonomy as A


def names(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for x in v.values():
            yield from names(x)
    elif isinstance(v, (list, tuple)):
        for x in v:
            yield from names(x)


fails = []
for kind in ("exit_not_met", "exit_met"):
    st = {"mods": {"M": {"road_back": {"caused_by": "OLD_STEWARD", "at": 1.0, "from": "blind_challenge"}}}}
    row = {"mod": "M", "stage": "blind_challenge", "aut": "steward", "steward_kind": kind, "steward_key": "k2",
           "cycle": 1, "cap": 8, "why": "test"}
    A._execute_one(ROOT, {}, st, row, 2.0,
                   lambda item, title, why: (True, "filed"),
                   lambda item, brief, model, cap, seat: (0, "DETACHED unit-x", "unit-x"),
                   {"OLD_STEWARD"})
    rb = st["mods"]["M"].get("road_back") or {}
    got = set(names(rb))
    if "OLD_STEWARD" not in got:
        fails.append("%s: road_back after the second steward launch is %s; the first steward's items are orphaned"
                     % (kind, rb))
for f in fails:
    print("FAIL", f)
print("PASS" if not fails else "%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
