#!/usr/bin/env python3
"""selftest_helper_checkpoint.py — the checkpoint order and its bounded wait (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

All on SIMULATED transcripts in a temp dir; no window, no rimflow write (the note runner is faked).
  order      `checkpoint` lists every live helper with its agentId and item, records one deadline, prints the ORDER
  items      the item is the id after `Item`; a ruling the brief cites is not taken for it
  once       re-running before the deadline never extends it
  done       --wait returns DONE as soon as every checkpointed helper has ended its turn
  lost       past the deadline a still-live helper is LOST: notes on its item, helpers_of retires it (the drain
             exemption: the kill no longer waits on it), the wake lists it
  no record  without a checkpoint nothing changes: a live helper stays alive (helpers_of untouched)
  cap        one --wait call returns WAITING at its cap, before the deadline
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_helper_checkpoint_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
sys.path.insert(0, HERE)
import helper_checkpoint as HC  # noqa: E402
import seat_restart as SR  # noqa: E402

FAILS = []
T0 = 1_800_000_000.0
KNOWN = {"SOME_ITEM_TO_BUILD", "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM", "OTHER_THING_FIXED_HERE"}


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def rec(kind, text=None):
    if kind == "prompt":
        return {"type": "user", "message": {"role": "user", "content": text}}
    if kind == "end":
        return {"type": "assistant", "message": {"stop_reason": "end_turn", "content": [{"type": "text", "text": "ok"}]}}
    return {"type": "assistant", "message": {"stop_reason": "tool_use",
                                             "content": [{"type": "tool_use", "name": "Bash", "input": {}}]}}


def window(sid, helpers):
    """helpers: {agentId: (prompt, ended?)} -> transcript path."""
    proj = os.path.join(TMP, "proj")
    os.makedirs(os.path.join(proj, sid, "subagents"), exist_ok=True)
    tx = os.path.join(proj, sid + ".jsonl")
    with open(tx, "w") as f:
        f.write(json.dumps(rec("prompt", "hi")) + "\n")
    for aid, (prompt, ended) in helpers.items():
        write_helper(tx, aid, prompt, ended)
    return tx


def write_helper(tx, aid, prompt, ended):
    base = os.path.join(tx[:-len(".jsonl")], "subagents", "agent-" + aid)
    with open(base + ".jsonl", "w") as f:
        f.write(json.dumps(rec("prompt", prompt)) + "\n")
        f.write(json.dumps(rec("end" if ended else "tool")) + "\n")
    with open(base + ".meta.json", "w") as f:
        json.dump({"description": "helper " + aid}, f)
    os.utime(base + ".jsonl", (T0, T0))


def test_order_items_once():
    tx = window("sid-a", {"a111": ("BENCH helper (--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). Item "
                                   "SOME_ITEM_TO_BUILD (read its notes).", False),
                          "a222": ("Fix OTHER_THING_FIXED_HERE and mention NOT_A_LEDGER_ID_AT_ALL.", False),
                          "a333": ("Item SOME_ITEM_TO_BUILD done already", True)})
    r, text = HC.start("BENCH", tx, "sid-a", wait_s=600, now=T0 + 10, known=KNOWN)
    ids = [h["agent_id"] for h in r["helpers"]]
    check(ids == ["a111", "a222"], "order: only the live helpers are listed (%s)" % ids)
    check("to=a111" in text and HC.ORDER in text, "order: the agentId and the standard ORDER are printed")
    check(r["helpers"][0]["items"] == ["SOME_ITEM_TO_BUILD"], "items: the id after `Item`, not the cited ruling (%s)"
          % r["helpers"][0]["items"])
    check(r["helpers"][1]["items"] == ["OTHER_THING_FIXED_HERE"], "items: no `Item` -> the ledger ids the brief names")
    r2, _ = HC.start("BENCH", tx, "sid-a", wait_s=9999, now=T0 + 100, known=KNOWN)
    check(r2["deadline"] == T0 + 610, "once: a re-run before the deadline keeps it (%s)" % (r2["deadline"] - T0))
    return tx


def test_no_record_changes_nothing():
    tx = window("sid-z", {"a999": ("Item SOME_ITEM_TO_BUILD", False)})
    hs = SR.helpers_of(tx, T0 + 5000, 10**9)
    check(hs and hs[0]["alive"] and "retired" not in hs[0], "no record: a live helper stays alive")


def test_done():
    tx = window("sid-d", {"ad1": ("Item SOME_ITEM_TO_BUILD", False)})
    HC.start("BENCH", tx, "sid-d", wait_s=600, now=T0, known=KNOWN)
    clock = [T0 + 1]

    def sleep(s):
        clock[0] += s
        write_helper(tx, "ad1", "Item SOME_ITEM_TO_BUILD", True)   # it obeys the order and ends its turn

    rc, text = HC.wait("BENCH", tx, "sid-d", cap_s=500, now_fn=lambda: clock[0], sleep=sleep,
                       runner=lambda *a, **k: None)
    check(rc == 0 and "DONE" in text, "done: --wait returns DONE once the helper ended (%s)" % text[:60])


def test_cap():
    tx = window("sid-c", {"ac1": ("Item SOME_ITEM_TO_BUILD", False)})
    HC.start("BENCH", tx, "sid-c", wait_s=600, now=T0, known=KNOWN)
    clock = [T0 + 1]
    rc, text = HC.wait("BENCH", tx, "sid-c", cap_s=100, now_fn=lambda: clock[0],
                       sleep=lambda s: clock.__setitem__(0, clock[0] + s), runner=lambda *a, **k: None)
    check(rc == 3 and "WAITING" in text, "cap: one call stops at its cap before the deadline (%s)" % text[:40])


class R:
    returncode = 0


def test_lost(tx):
    notes = []

    def runner(argv, **kw):
        notes.append(argv)
        return R()

    clock = [T0 + 20]
    hs = SR.helpers_of(tx, clock[0], 10**9)
    check(all(h["alive"] for h in hs if h["id"] != "agent-a333"), "lost: before the deadline both helpers hold")
    rc, text = HC.wait("BENCH", tx, "sid-a", cap_s=10**6, now_fn=lambda: clock[0],
                       sleep=lambda s: clock.__setitem__(0, clock[0] + s), runner=runner)
    check(rc == 1 and "LOST" in text and "a111" in text and "SOME_ITEM_TO_BUILD" in text,
          "lost: the deadline names each helper and its item (%s)" % text[:90])
    items = sorted(a[a.index("note") + 1] for a in notes)
    check(items == ["OTHER_THING_FIXED_HERE", "SOME_ITEM_TO_BUILD"], "lost: one note per item (%s)" % items)
    check(all("--text" in a and "--seat" in a for a in notes), "lost: notes use rimflow note --text --seat")
    hs = SR.helpers_of(tx, clock[0], 10**9)
    live = [h["id"] for h in hs if h["alive"]]
    check(live == [] and all("LOST" in (h.get("retired") or "LOST") for h in hs),
          "drain exemption: past the deadline helpers_of retires the lost helpers (live %s)" % live)
    rc2, _ = HC.wait("BENCH", tx, "sid-a", cap_s=10, now_fn=lambda: clock[0], sleep=lambda s: None, runner=runner)
    check(len(notes) == 2 and rc2 == 1, "lost: a second --wait repeats LOST and writes no second note (rc %s)" % rc2)
    w = HC.wake_lines("sid-a")
    check(len(w) == 2 and "SOME_ITEM_TO_BUILD" in "".join(w), "wake: the fresh window is told what was lost")


def main():
    tx = test_order_items_once()
    test_no_record_changes_nothing()
    test_done()
    test_cap()
    test_lost(tx)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
