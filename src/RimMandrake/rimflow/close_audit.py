#!/usr/bin/env python3
"""close_audit.py - AU4, unearned dones (rimflow_v3_responsibilities_2026-10-26.md; RO3 of
operating_requirements_2026-11-01.md): items reaching done with no level-tagged pass on the sha they reached it at, or a newer fail.

Every transition to done counts, whichever verb made it: `close`, the last criterion's `verify`, an `implemented` owing
nothing. The fold is model.replay's own, so a reopened item that closes again counts twice. The window is
close_gate_rules.json `since`, when the gate covered all three; the 2026-10-19 window, the baseline's, is printed beside
it. A --no-code close has no code to check, so it is counted apart, under its own limit.
Exit 0 in range, 1 out of range, 2 UNMEASURED: fewer dones in the window than `min_sample`, whose share would say nothing.

    python3 src/RimMandrake/rimflow/close_audit.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                                       # noqa: E402

RULES = os.path.join(HERE, "close_gate_rules.json")
VERBS = ("close", "verify", "implemented")      # `kept` only restores a done already counted when it was reached


def dones(events):
    """Pure. -> [{id, ts, via, sha, noCode, earned}], one per transition to done, in ledger order."""
    state, out = {}, []

    def see(ev, world, ok):
        iid = ev.get("id")
        it = world.items.get(iid)
        if it is None:
            return
        was, state[iid] = state.get(iid), it.state
        if ok and it.state == "done" and was != "done" and ev.get("event") in VERBS:
            sha = it.closed_sha
            out.append({"id": iid, "ts": ev["ts"], "via": ev["event"], "sha": sha, "noCode": ev.get("noCode"),
                        "earned": not model.run_refusals(it, sha)})

    model.replay(events, observe=see)
    return out


def audit(rows, since):
    """Pure. -> (dones in the window, the unearned of those, --no-code ones excepted, the code ones, the --no-code ones)."""
    window = [d for d in rows if d["ts"] >= since]
    code = [d for d in window if not d["noCode"]]
    return window, [d for d in code if not d["earned"]], code


def main():
    with open(RULES, encoding="utf-8") as f:
        r = json.load(f)
    events = model.read()
    rows = dones(events)
    print("ledger: %d events, %d transitions to done" % (len(events), len(rows)))
    base, base_bad, base_code = audit(rows, "2026-10-19")
    print("AU4 since 2026-10-19 (the baseline's window): %d of %d code dones unearned" % (len(base_bad), len(base_code)))
    window, bad, code = audit(rows, r["since"])
    vias = {v: sum(d["via"] == v for d in window) for v in VERBS}
    print("AU4 since the gate landed (%s): %d of %d code dones unearned; --no-code %d of %d; by verb %s" % (
        r["since"], len(bad), len(code), len(window) - len(code), len(window), vias))
    for d in bad[:10]:
        print("  unearned: %s by %s at %s" % (d["id"], d["via"], d["sha"]))
    if len(window) < r["min_sample"]:
        print("UNMEASURED: %d dones in the window, fewer than min_sample %d" % (len(window), r["min_sample"]))
        return 2
    high = [bool(code) and len(bad) / len(code) > r["code_unverified_max_share"],
            (len(window) - len(code)) / len(window) > r["no_code_max_share"]]
    print("AU4 %s (code unearned <= %.2f, --no-code <= %.2f of dones)" % (
        "OUT OF RANGE" if any(high) else "IN RANGE", r["code_unverified_max_share"], r["no_code_max_share"]))
    return 1 if any(high) else 0


if __name__ == "__main__":
    sys.exit(main())
