#!/usr/bin/env python3
"""selftest_tick_pauses.py -- the promises of design/specs/2026-11-19-tick-pauses/boundary.md, one test each, by name.

Item RIMMANDRAKE_LIFT_DESIGNER_BLOCK_NAMING_DONE_ITEM_SLIME_WAITS: GelatinousSlime's Designer stood blocked from
2026-11-16 08:55 PST on RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS, a done item, and the tick paused it with no next act.
Fixtures only (a temp concept tree, fakes for the ledger and the landing); the real ledger and repo are not touched.

    python3 src/RimMandrake/rimflow/selftest_tick_pauses.py      exit 0: every check passes
"""
import json
import os
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE))
sys.path.insert(1, str(HERE.parent / "Utils"))
import maturation_autonomy as MA  # noqa: E402

FAILS = []
NOW = 1_795_130_000.0
CFG = {"enabled": True, "advancing": [], "cap_tokens": 3_750_000, "max_live": 2, "settle_s": 180, "blind_enabled": True,
       "blind_cap_tokens": 5_000_000, "blind_auto_cycles_per_visit": 3, "ingame_enabled": True, "ingame_cap_tokens": 7_500_000,
       "ingame_auto_runs_per_visit": 1, "steward_cap_tokens": 1_250_000, "fix_cap_tokens": 2_500_000, "steward_model": "opus",
       "stalled_min": 10, "seat": "BENCH", "launch_tries": 2}
DONE = "RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS"
REASON = "%s: coverage_judge brief is UNTESTED, its verdict is advisory" % DONE
BLOCKED = {"status": "blocked", "stage": 4, "item": "CONCEPT_C", "blocked_on": REASON,
           "history": [{"at": "2026-11-16T16:55:00Z", "stage": 4, "what": "close", "why": "run r1: stage 4 blocked"}]}
it = lambda s: types.SimpleNamespace(state=s, kind="task", caused_by=None)      # noqa: E731


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def res(st, dst, items):
    """One tick's resolve on mod C, its Designer reading `dst`, the ledger `items`."""
    root = tempfile.mkdtemp(prefix="tick_pauses_")
    os.makedirs(os.path.join(root, "design", "concepts"))
    fx = {"designer_state": lambda m: dst, "version_locked": lambda m: False, "open_items": lambda ids: [],
          "version_evidence": lambda m: [], "designer_unit": lambda m: None, "designer_chain": lambda m: None,
          "blocked_tickets": lambda m, d: MA.blocked_tickets(d, items),
          "blocked_closed": lambda m, d: MA.blocked_closed(d, items), "ticket_runs": lambda i: []}
    rows = [{"mod": "C", "stage": "designer", "decision": "not_offline", "why": "decide's reading", "need": "C: design"}]
    rows, launches = MA.resolve(root, dict(CFG), st, {"C": {"version": None, "live_units": []}}, rows, [], NOW, fx)
    MA.classify(dict(CFG), st, rows, NOW)
    return rows[0], launches


def t_block_on_closed_items_lifts_once():
    st = {"mods": {}}
    r, la = res(st, BLOCKED, {DONE: it("done")})
    check(r.get("aut") == "autounblock" and la == ["C"] and r.get("klass") == "launch" and DONE in str(r.get("why")),
          "a block naming only a done item is lifted by the tick as an act, naming the item (read %s / %s, launches %s)"
          % (r.get("decision"), r.get("klass"), la))
    check(r.get("steward_key") == MA.unblock_key(BLOCKED) and r.get("unblock_items") == [DONE] and not r.get("need"),
          "the act is booked under its reason's key and owes no Needs Conductor line")
    import maturation_dispatch as MD
    check(not MD.takes_slot(r) if hasattr(MD, "takes_slot") else "autounblock" in MD.NO_SLOT_AUT,
          "the lift takes no slot")
    landed = []
    MA.execute("/nonexistent", dict(CFG), st, [r], la, NOW,
               {"known": lambda: set(), "autounblock": lambda root, mod, items, now=None:
                landed.append((mod, items)) or "PUBLISHED abc1234"})
    book = st["mods"]["C"]["steward"][MA.unblock_key(BLOCKED)]
    check(landed == [("C", [DONE])] and book.get("landed") == "PUBLISHED abc1234" and r.get("decision") == "launched",
          "execute lands the lift once and books it (read %s, %s)" % (landed, book))
    for state in ("dropped", "superseded"):
        r, _ = res({"mods": {}}, BLOCKED, {DONE: it(state)})
        check(r.get("aut") == "autounblock", "a %s item is closed too: lifted" % state)
    r, _ = res({"mods": {}}, dict(BLOCKED, blocked_on="no item named here"), {})
    check(not r.get("aut") and r.get("decision") == "designer_blocked" and r.get("klass") == "paused",
          "a reason naming no item is a plain pause, as before (read %s)" % r.get("decision"))


def t_a_second_block_on_the_same_reason_names_what_is_owed():
    st = {"mods": {"C": {"steward": {MA.unblock_key(BLOCKED): {"at": NOW - 3600, "failed": None, "tries": 1,
                                                               "landed": "PUBLISHED abc1234"}}}}}
    r, la = res(st, BLOCKED, {DONE: it("done")})
    need = str(r.get("need"))
    check(la == [] and not r.get("aut") and r.get("klass") == "paused", "the same block after one lift is not lifted "
          "again (read %s / %s, launches %s)" % (r.get("decision"), r.get("klass"), la))
    check(DONE in need and "re-blocked" in need and "designer_stage.py unblock" in need and "UNTESTED" in need,
          "its need names the closed item, the earlier lift, the reason still owed and the hand command (%s)" % need)
    r, la = res(st, dict(BLOCKED, blocked_on=REASON + "; and the signature is missing"), {DONE: it("done")})
    check(r.get("aut") == "autounblock", "a new reason is a new block, with its own one lift")


def t_an_open_or_unknown_item_is_no_lift():
    r, la = res({"mods": {}}, BLOCKED, {DONE: it("doing")})
    check(r.get("aut") == "fixer" and r.get("fix_item") == DONE, "an open item gets its fixer run, not a lift (read "
          "%s)" % r.get("aut"))
    r, la = res({"mods": {}}, dict(BLOCKED, blocked_on=REASON + " and RIMMANDRAKE_NEVER_FILED_ANYWHERE_AT_ALL"),
                {DONE: it("done")})
    check(not r.get("aut") and la == [] and r.get("klass") == "paused", "an id the ledger does not hold is no lift "
          "(read %s)" % r.get("aut"))
    check(MA.blocked_closed(BLOCKED, {}) == [] and MA.blocked_closed(None, {DONE: it("done")}) == [] and
          MA.blocked_closed({"blocked_on": None}, {}) == [], "blocked_closed: an empty ledger, no state, no reason")
    r, la = res({"mods": {}}, dict(BLOCKED, blocked_on="OWNER HOLD: %s" % DONE), {DONE: it("done")})
    check(r.get("decision") == "owner" and not r.get("aut"), "an OWNER HOLD naming a done item stays his")


def t_a_failed_lift_puts_stage_json_back():
    root = tempfile.mkdtemp(prefix="tick_pauses_land_")
    d = os.path.join(root, "design", "concepts", "C")
    os.makedirs(d)
    p = os.path.join(d, "stage.json")
    with open(p, "w") as f:
        json.dump(BLOCKED, f)
    with open(p, "rb") as f:
        was = f.read()
    seen = []

    def land(subject, paths):
        with open(p) as f:
            seen.append(json.load(f).get("status"))
        raise RuntimeError("land.sh exited 1: push refused")
    try:
        MA.unblock_and_land(root, "C", [DONE], land=land)
        raised = None
    except RuntimeError as e:
        raised = e
    with open(p, "rb") as f:
        now = f.read()
    check(seen == ["ready"] and raised is not None and now == was,
          "the lift writes ready, and a landing that raises puts stage.json back byte for byte (saw %s)" % seen)
    out = MA.unblock_and_land(root, "C", [DONE], land=lambda s, ps: "PUBLISHED def5678")
    with open(p) as f:
        after = json.load(f)
    check(out == "PUBLISHED def5678" and after.get("status") == "ready" and "blocked_on" not in after
          and any(h.get("what") == "unblock" and DONE in str(h.get("why")) for h in after.get("history") or []),
          "a landed lift leaves the concept ready, its reason in history")
    st = {"mods": {"C": {}}}
    row = {"mod": "C", "aut": "autounblock", "decision": "autounblock", "steward_key": MA.unblock_key(BLOCKED),
           "unblock_items": [DONE]}

    def boom(root, mod, items, now=None):
        raise RuntimeError("land.sh exited 1: push refused")
    MA.execute(root, dict(CFG), st, [row], ["C"], NOW, {"known": lambda: set(), "autounblock": boom})
    check(row.get("decision") == "launch_failed" and "push refused" in str(row.get("why"))
          and st["mods"]["C"]["steward"][MA.unblock_key(BLOCKED)].get("failed"),
          "a failed lift reads launch_failed with the error, booked as a failed try (read %s)" % row.get("why"))


def main():
    t_block_on_closed_items_lifts_once()
    t_a_second_block_on_the_same_reason_names_what_is_owed()
    t_an_open_or_unknown_item_is_no_lift()
    t_a_failed_lift_puts_stage_json_back()
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
