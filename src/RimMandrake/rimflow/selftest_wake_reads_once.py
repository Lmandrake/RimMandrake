#!/usr/bin/env python3
"""Selftest: a Conductor window's first turn prints the Conductor log tail, the owed list, the old window's last reply
and the top of his words ONCE (RIMMANDRAKE_SLIM_RUN_END_WAKES_WINDOW_HIT_400K_IN_TWO_HOURS).

Measured 2026-11-26 over the Conductor window c95f9ab4: `seat_restart.py wake` printed the 12.9k-character log tail, the
owed list and the last reply, then `handoff.py --wake` (it runs `seat_restart.py last-reply`) printed the last reply and
the top lines again, and the Start of turn steps printed the owed list and the log tail again.

All in a temp dir: a throwaway clone, dispatcher state and ~/.claude. No window is read, killed or launched.
Exit 0 all pass, 1 a promise broke.

    python3 src/RimMandrake/rimflow/selftest_wake_reads_once.py
"""
import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_wake_reads_once_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(TMP, "claude")
os.environ["AGENT_SEAT"] = "BENCH"
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import doorbell  # noqa: E402
import owed  # noqa: E402
import seat_restart as SR  # noqa: E402
import wake_words as WW  # noqa: E402

RESULTS = []
LOG = os.path.join(TMP, "conductor_log.md")
CLONE = os.path.join(TMP, "clone")
OLD_TX = os.path.join(TMP, "old.jsonl")
LAST = "LAST_REPLY_MARK the old window said this"
OWED = "OWED_MARK an owed act"
TAIL = "LOG_TAIL_MARK a log line"


def check(ok, what, got=None):
    RESULTS.append((bool(ok), what, got))


def fixture():
    os.makedirs(os.path.join(CLONE, WW.SHARDS), exist_ok=True)
    for shard in ("OWNER", "BENCH"):
        open(os.path.join(CLONE, WW.SHARDS, shard + ".jsonl"), "w").close()
    with open(LOG, "w") as f:
        f.write("an old line\n" + TAIL + "\n")
    with open(OLD_TX, "w") as f:
        f.write(json.dumps({"type": "user", "timestamp": "2026-11-26T02:00:00Z", "message": {"content": "hi"}}) + "\n")
    os.makedirs(SR.restart_dir(), exist_ok=True)


@contextlib.contextmanager
def window(session):
    """This process is the Conductor window `session`; every reader outside the wake's own text is a fixture."""
    sch = {"seat_restart": {"enabled": True, "seats": {"BENCH": {"kind": "conductor", "seat_log": LOG}}},
           "seats": {"BENCH": {"session_name": "CONDUCTOR", "clone": CLONE}}}
    saved = {}

    def put(mod, name, val):
        saved[(mod, name)] = getattr(mod, name)
        setattr(mod, name, val)
    put(SR, "_schedule", lambda: sch)
    put(doorbell, "claude_ancestor", lambda *a, **k: 4242)
    put(SR, "session_file", lambda pid: {"sessionId": session, "name": "CONDUCTOR", "entrypoint": "cli"})
    put(SR, "transcript_for", lambda me, cfg: os.path.join(TMP, session + ".jsonl"))
    put(SR, "last_dead_window", lambda cfg, me=None: (OLD_TX, LAST))
    put(SR, "last_assistant_text", lambda *a, **k: LAST)
    put(SR, "hard_stop_reason", lambda: None)
    put(owed, "wake_lines", lambda repo, *a, **k: ["", owed.WAKE_HEAD, OWED])
    put(WW, "read_holds", lambda: ({}, None))
    for quiet in ("_wake_conductor", "_wake_helpers", "_wake_receipts", "_wake_designer_turns"):
        put(SR, quiet, lambda *a, **k: None)
    try:
        yield
    finally:
        for (mod, name), val in saved.items():
            setattr(mod, name, val)


def run(fn, **ns):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        fn(argparse.Namespace(**ns))
    return out.getvalue()


def counts(text):
    return {"log tail": text.count(TAIL), "owed list": text.count(OWED), "last reply": text.count(LAST)}


def t_a_restart_wake_then_handoff_prints_once():
    """The measured first turn: `seat_restart.py wake`, then `handoff.py --wake`'s last-reply read, in one window."""
    with window("W-restart"):
        first = run(SR.cmd_wake, seat="BENCH", lines=40, gen=None)
        again = run(SR.cmd_last_reply, seat="BENCH", again=False, lines=40)
    total = counts(first + again)
    check(all(n == 1 for n in total.values()),
          "restart-wake-then-handoff-prints-once: the log tail, owed list and last reply print once in the window "
          "(%s)" % total, again)
    check("seat_restart.py last-reply --seat BENCH --again" in again,
          "restart-wake-then-handoff-prints-once: the second read names the command that prints them again", again)
    with window("W-restart"):
        forced = run(SR.cmd_last_reply, seat="BENCH", again=True, lines=40)
    check(all(n == 1 for n in counts(forced).values()),
          "restart-wake-then-handoff-prints-once: --again prints them whole", forced)


def t_handoff_first_then_restart_wake_prints_once():
    """The restart prompt names both reads and no order: `handoff.py --wake` first, then `seat_restart.py wake`."""
    with window("W-reverse"):
        first = run(SR.cmd_last_reply, seat="BENCH", again=False, lines=40)
        again = run(SR.cmd_wake, seat="BENCH", lines=40, gen=None, again=False)
    total = counts(first + again)
    check(all(n == 1 for n in total.values()) and "--again" in again,
          "handoff-first-then-restart-wake-prints-once: the second read prints one line in their place (%s)" % total,
          again)


def t_a_fleet_launch_reads_everything_once():
    """A window no restart made runs only `handoff.py --wake`: its last-reply read carries the log tail and the owed
    list, so the Start of turn needs no second tail or owed run."""
    with window("W-fleet"):
        first = run(SR.cmd_last_reply, seat="BENCH", again=False, lines=40)
    check(all(n == 1 for n in counts(first).values()),
          "fleet-launch-reads-everything-once: last-reply prints the log tail, owed list and last reply (%s)"
          % counts(first), first)


def t_handoff_prints_no_second_owed():
    """handoff.py --wake prints its own owed list only when the last-reply read did not."""
    import handoff
    calls = []
    saved = (handoff.subprocess.run, handoff.show_owed, handoff.previous_handoff, handoff.ledger_state_line)
    for said in ("\n" + owed.WAKE_HEAD + "\n" + OWED, SR.READ_ONCE % ("7:00:00 PM PST", "BENCH"), ""):
        calls.clear()
        handoff.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 0, said, "")
        handoff.show_owed = lambda: calls.append(1)
        handoff.previous_handoff = lambda: (None, None)
        handoff.ledger_state_line = lambda pointers=True: ""
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                handoff.wake()
        finally:
            handoff.subprocess.run, handoff.show_owed, handoff.previous_handoff, handoff.ledger_state_line = saved
        want = 0 if said else 1
        check(len(calls) == want, "handoff-prints-no-second-owed: handoff.py --wake ran its owed view %d time(s), "
              "want %d, after a last-reply read of %d characters" % (len(calls), want, len(said)))




def guarded(t):
    try:
        t()
    except Exception as e:  # noqa: BLE001 - a test that raises is a failed promise, named
        check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))


def main():
    fixture()
    guarded(t_a_restart_wake_then_handoff_prints_once)
    guarded(t_handoff_first_then_restart_wake_prints_once)
    guarded(t_a_fleet_launch_reads_everything_once)
    guarded(t_handoff_prints_no_second_owed)
    for ok, what, got in RESULTS:
        print(("PASS " if ok else "FAIL ") + what)
        if not ok and got is not None:
            print("   got: %s" % str(got)[:1500])
    bad = sum(1 for ok, _, _ in RESULTS if not ok)
    print("%s: %d of %d failed" % ("FAIL" if bad else "ALL PASS", bad, len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
