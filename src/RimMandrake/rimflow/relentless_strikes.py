#!/usr/bin/env python3
"""relentless_strikes.py — two strikes change tack, and an item that has had its approaches goes up with a summary
(RELENTLESS_STRIKES_HARDEN_CHANGE_TACK).

Measured (relentless_vs_foundry_2026-11-02.md fix 4): items at gen 6 and above took 35% of Relentless spend for 11
closes; CLOSE_GATE_ENFORCE_DONE_IS_EARNED reached gen 20 for 6.2M. The ladder already existed in relentless.fail
(build -> redesign -> pilot -> redesign ... at `same_failure_limit` of one class) but it never ended and waited three
strikes. Now: `same_failure_limit` 2, and after `max_approach_changes` changes the next trigger HOLDS the item for the
Conductor instead of turning again. The per-item token cap is `item_spend_limit` (spend_holds); its hold carries the
same summary, so whoever reads the hold sees what was tried without opening the store.
"""

SUMMARY_MAX = 380       # the hold reaches the ledger through `rimflow needs --reason`, cut at relentless.NOTE_MAX (400)


def summary(st):
    """-> one line: generations, spend, the endings by class, the approach, the last ending."""
    ends = ", ".join("%s x%d" % (k, n) for k, n in sorted((st.get("failures") or {}).items(), key=lambda kv: -kv[1]) if n)
    last = st.get("last_fail") or {}
    line = "gen %d, %.1fM weighted tokens, %d returns (%s), approach %s after %d change(s); last: %s: %s" % (
        st.get("gen", 0), (st.get("spent") or 0) / 1e6, st.get("total_failures", 0), ends or "none open",
        st.get("approach"), st.get("approach_changes", 0), last.get("class", "-"), (last.get("detail") or "")[:160])
    return line[:SUMMARY_MAX]


def out_of_tacks(st, r):
    """True when the approach has already changed `max_approach_changes` times: the next change is a person's."""
    cap = r.get("max_approach_changes")
    return cap is not None and st.get("approach_changes", 0) >= cap


def hold(st, why, kind, now):
    st["hold"] = {"why": ("%s. %s" % (why, summary(st)))[:SUMMARY_MAX + 120], "kind": kind, "delivered": False,
                  "at": now}
