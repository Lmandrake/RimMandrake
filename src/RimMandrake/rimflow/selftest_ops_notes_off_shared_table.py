#!/usr/bin/env python3
"""Guard for OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE (review U N2), run against the REAL
dispatcher_schedule.json and ops_watch_rules.json, not a fixture: the token-aware Operations role's launch, done and
economy notes, and every dispatcher note bound for the shared V3 roles item that token-blind roles read, land on
Operations' own item; only a closed-type blind note may reach the shared item.

A fixture test cannot catch the schedule drifting (Operations' row pointed back at the shared item, its token_aware
flag dropped, token_notes_item renamed to a blind item); this one reads the shipped data."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import dispatcher as D  # noqa: E402
import role_launch as RL  # noqa: E402

OPS_ITEM = "OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE"
SHARED = "V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE"
FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    sch = D.load_schedule()
    roles = {r.get("name"): r for r in sch.get("roles") or [] if isinstance(r, dict)}
    ops = roles.get("Operations") or {}
    check(ops.get("ledger_item") == OPS_ITEM, "Operations' ledger_item is its own item: %r" % ops.get("ledger_item"))
    check(ops.get("token_aware") is True, "Operations is token_aware")
    check(sch.get("token_notes_item") == OPS_ITEM, "token_notes_item is Operations' item: %r" % sch.get("token_notes_item"))
    blind = D.blind_items(sch)
    check(SHARED in blind, "the shared V3 roles item is read by a token-blind role (so it is guarded)")
    check(OPS_ITEM not in blind, "no token-blind role reads Operations' item")
    readers = sorted(n for n, r in roles.items() if r.get("ledger_item") == OPS_ITEM)
    check(readers == ["Operations"], "only Operations reads its item: %r" % readers)

    rx = D.token_rx()  # the shipped token_talk word list
    check(bool(rx.pattern) and rx.search("budget 450000 weighted tokens") is not None,
          "the shipped token_talk list is non-empty and sees a budget line")

    # Operations' own launch/done notes stay on its item, figures and all
    for text in ("dispatcher role_launch BENCH: Operations slot 07:30 local, band GREEN, budget 550000",
                 "dispatcher role_done Operations: 372782 weighted tokens of a 550000 budget"):
        check(D.route_note(sch, OPS_ITEM, text) == (OPS_ITEM, text), "Operations note stays home: %s" % text[:40])

    # anything with figures bound for the shared item is diverted, naming where it was meant to go
    for text in ("dispatcher alarm : Arbiter run used 1020596 weighted tokens (raw 5451557), budget 500000",
                 "usage limit reached on account steven",   # a phrasing the word list may lack: still diverted
                 "plain text with no figure"):               # not a closed-type blind note: diverted too
        to, out = D.route_note(sch, SHARED, text)
        check(to == OPS_ITEM and SHARED in out and out.startswith(text), "diverted off the shared item: %s" % text[:40])

    # a figure-bearing string passed AS blind_text is refused (closed type, not the word list, is the gate)
    to, _ = D.route_note(sch, SHARED, "x", blind_text="Operations run: budget 550000")
    check(to == OPS_ITEM, "a forged blind_text is refused")

    # a real closed-type blind note may reach the shared item, and carries no unit digits
    bn = RL.blind_note(RL.blind("Conductor", "launched", "quick", "rm-role-conductor-1793241004"))
    check(bool(bn) and D.route_note(sch, SHARED, "why with budget 1", blind_text=bn) == (SHARED, bn),
          "a closed-type blind note reaches the shared item: %r" % bn)
    check(bool(bn) and "1793241004" not in bn and not rx.search(bn), "the blind note carries no unit digits or token term")

    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
