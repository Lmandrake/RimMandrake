#!/usr/bin/env python3
"""Selftest: a run-end wake prints the state rows that changed since the window's last wake, and the rest as one
counted line (RIMMANDRAKE_SLIM_RUN_END_WAKES_WINDOW_HIT_400K_IN_TWO_HOURS). One test per promise of
design/specs/2026-11-23-wake-carries-result/boundary.md §Changes only.

Measured 2026-11-26 over the Conductor window c95f9ab4: 19 wakes, 73,415 of their 129,090 characters were the state
block, and most of its 29 rows were the same at each wake. All in a temp dir; no window is read or woken.
Exit 0 all pass, 1 a promise broke.

    python3 src/RimMandrake/rimflow/selftest_run_end_wake_slim.py
"""
import inspect
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_run_end_wake_slim_")
STATE = os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(TMP, "cfg")
sys.path.insert(0, HERE)
import run_end_wake as RW  # noqa: E402

RESULTS = []
N = [0]
HELD = ["Cauldron           designer        HELD BY OWNER: And stop the new biome mo tick: owner_hold",
        "Contagion          designer        HELD BY OWNER: And stop the new biome mo tick: owner_hold",
        "FeverWood          designer        HELD BY OWNER: And stop the new biome mo tick: owner_hold",
        "Graffiti           blind_challenge HELD BY OWNER: Stop that Graffiti work.  tick: owner_hold"]


def check(ok, what, got=None):
    RESULTS.append((bool(ok), what, got))


def readers(minutes=24, hours="163.3", pipe_extra=(), held=HELD, flowworks="his_walk"):
    """The three readers as the wake has them; the lock's age and the accounts' reset hours move at every wake."""
    return {"locks": lambda: "ArchBig: HELD by BENCH since 19:16 PST (%d min), for: a walk map rebuild" % minutes,
            "pipe": lambda: "\n".join(["control rev 208: ALL ON",
                                       "FlowWorks          %-15s ON tick: owner" % flowworks] + list(held)
                                      + list(pipe_extra)),
            "accounts": lambda: "lukas    MEASURED   week 100%% left, resets in %s h session ?" % hours}


def tx(path, ctx):
    """A transcript whose last assistant turn read ctx tokens of context."""
    with open(path, "a") as f:
        f.write(json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": 2, "cache_read_input_tokens": ctx,
                                                                         "cache_creation_input_tokens": 0}}}) + "\n")
    return path


def one_wake(session, rd, tx_path=None):
    """Post one run end to an armed window and take the wake's text."""
    N[0] += 1
    p = os.path.join(TMP, "u%d.out.json" % N[0])
    with open(p, "w") as f:
        json.dump({"type": "result", "result": "run %d said this" % N[0], "is_error": False}, f)
    os.makedirs(RW.wake_dir(STATE), exist_ok=True)
    with open(RW.armed_path(STATE), "w") as f:
        json.dump({"pid": 99, "window_pid": 4242, "session_id": session}, f)
    RW.post("u%d" % N[0], "success (exited 0)", p, "ITEM_%d" % N[0], root=STATE, alive=lambda pid: True)
    kw = {"tx_path": tx_path} if "tx_path" in inspect.signature(RW.wait).parameters else {}   # red on the parent by
    code, text = RW.wait(session, 4242, root=STATE, me=99, alive=lambda pid: True, max_wait=5,  # budget: fixture
                         sleep=lambda s: None, state=lambda: RW.state_block(rd, now=1795660857), **kw)  # TypeError
    return text


def state_part(text):
    k = text.find("== STATE")
    return text[k:] if k >= 0 else ""


def t_unchanged_rows_print_once():
    t = tx(os.path.join(TMP, "w1.jsonl"), 120000)
    first = state_part(one_wake("W1", readers(), t))
    second = state_part(one_wake("W1", readers(minutes=31, hours="163.1"), tx(t, 130000)))
    held_twice = [h for h in HELD if h.split()[0] in second]
    check(all(h.split()[0] in first for h in HELD) and not held_twice and "FlowWorks" not in second
          and "control rev 208" not in second,
          "unchanged-rows-print-once: two wakes in a row with the same state print each unchanged row once", second)
    check("unchanged since" in second and "8 rows" in second,
          "unchanged-rows-print-once: the second wake names how many rows stood still, in one line", second)
    check(len(second) * 2 < len(first), "unchanged-rows-print-once: the second state block is under half the first "
          "(%d vs %d characters)" % (len(second), len(first)), second)


def t_a_change_is_printed():
    t = tx(os.path.join(TMP, "w2.jsonl"), 120000)
    one_wake("W2", readers(), t)
    second = state_part(one_wake("W2", readers(flowworks="passed", held=HELD[1:]), tx(t, 125000)))
    check("FlowWorks          passed" in second, "a-change-is-printed: a row that changed is printed whole", second)
    check("GONE" in second and "Cauldron" in second,
          "a-change-is-printed: a row that is gone since the last wake is named as gone", second)
    check("Contagion" not in second, "a-change-is-printed: the rows that did not change are not printed", second)


def t_a_fresh_window_reads_it_whole():
    t = tx(os.path.join(TMP, "w3.jsonl"), 120000)
    one_wake("W3", readers(), t)
    other = state_part(one_wake("W3b", readers(), tx(os.path.join(TMP, "w3b.jsonl"), 30000)))
    check(all(h.split()[0] in other for h in HELD) and "unchanged since" not in other,
          "a-fresh-window-reads-it-whole: another window's first wake prints every row", other)


def t_a_compacted_window_reads_it_whole():
    t = tx(os.path.join(TMP, "w4.jsonl"), 300000)
    one_wake("W4", readers(), t)
    after = state_part(one_wake("W4", readers(), tx(t, 40000)))
    check(all(h.split()[0] in after for h in HELD) and "unchanged since" not in after,
          "a-compacted-window-reads-it-whole: a window whose context fell since its last wake prints every row", after)
    blind = state_part(one_wake("W5", readers(), None))
    again = state_part(one_wake("W5", readers(), None))
    check(all(h.split()[0] in again for h in HELD) and all(h.split()[0] in blind for h in HELD),
          "a-compacted-window-reads-it-whole: with no transcript to read, every wake prints every row", again)


def t_a_could_not_look_row_always_prints():
    t = tx(os.path.join(TMP, "w6.jsonl"), 120000)
    bad = dict(readers(), accounts=lambda: (_ for _ in ()).throw(RuntimeError("exit 2: no reading")))
    one_wake("W6", bad, t)
    second = state_part(one_wake("W6", bad, tx(t, 121000)))
    check("COULD NOT LOOK" in second, "a-could-not-look-row-always-prints: a reader that failed is said at each wake",
          second)




def guarded(t):
    try:
        t()
    except Exception as e:  # noqa: BLE001 - a test that raises is a failed promise, named
        check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))


def main():
    guarded(t_unchanged_rows_print_once)
    guarded(t_a_change_is_printed)
    guarded(t_a_fresh_window_reads_it_whole)
    guarded(t_a_compacted_window_reads_it_whole)
    guarded(t_a_could_not_look_row_always_prints)
    for ok, what, got in RESULTS:
        print(("PASS " if ok else "FAIL ") + what)
        if not ok and got is not None:
            print("   got: %s" % str(got)[:1500])
    bad = sum(1 for ok, _, _ in RESULTS if not ok)
    print("%s: %d of %d failed" % ("FAIL" if bad else "ALL PASS", bad, len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
