#!/usr/bin/env python3
"""handoff_restart.py — a `Stop` hook. A seat's handoff ends in its restart, by program.

Owner, 2026-11-01: "20 seconds, build it now and implement." (HANDOFF_FIX_RESTART_TWENTY_SECONDS). A seat that said
HANDOFF READY used to sit: nothing read those words. Keyed on the words, not on a script, because the seat may run this
repo's handoff.py or Lodestar's, and an agent can forget a last step but not the sentence its handoff ends in.

On the turn that says it (seat_restart.says_handoff_ready):
  handoff.py --check fails     -> block with its problems; the window fixes them and says it again.
                                  With helpers alive the check waits: they hold the shard and the doing items.
  seat_restart.py request      -> --ticket HANDOFF --fresh: the Dispatcher kills after grace_s of quiet, 20 s for FOUNDRY.
    refused (shard unpublished) -> block with the refusal.
On any turn end during a deferred handoff (its helpers ran out): the same check, plus the shard; then ticks, so the wait
is 20 s and not the 120 s timer.

Every block is written to restart/<SEAT>.refused.json, and at most MAX_BLOCKS stop one session: past that the turn ends
and the file stands, so the Dispatcher alarms (restart:<SEAT>:handoff_refused). Hence loud, and never a stuck window.
The Conductor is out of scope: its goodbye is instant and has its own hook. A seat not on restarts passes.
"""
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
MAX_BLOCKS = 3
TAIL = 1500


def run(args, seat, timeout=100):
    """-> (rc, output tail). A check that cannot run reads as a failed one."""
    try:
        r = subprocess.run([sys.executable] + args, cwd=REPO, capture_output=True, text=True, timeout=timeout,
                           env=dict(os.environ, RIMFLOW_SEAT=seat))
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[-TAIL:]
    except (OSError, subprocess.SubprocessError) as e:
        return 1, "could not run %s: %r" % (os.path.basename(args[0]), e)


def check(seat):
    return run([os.path.join(REPO, "src", "RimMandrake", "Utils", "handoff.py"), "--check"], seat)


def request(seat):
    return run([os.path.join(REPO, "src", "RimMandrake", "rimflow", "seat_restart.py"), "request", "--seat", seat,
                "--ticket", "HANDOFF", "--reason", "handoff", "--fresh",
                "--note", "The window said HANDOFF READY; its restart was requested by the Stop hook."], seat)


def refuse(SR, seat, sid, why, out=None):
    """Record the refusal; -> 0 after writing the block (or, past the cap, nothing: the alarm has it)."""
    p = SR.refused_path(seat)
    old = SR._read_json(p) or {}
    n = (old.get("n") or 0) + 1 if old.get("session_id") == sid else 1
    SR._write_json(p, {"seat": seat, "session_id": sid, "why": why, "n": n,
                       "ts": old["ts"] if old.get("session_id") == sid else time.time()})
    if n <= MAX_BLOCKS:
        json.dump({"decision": "block", "reason": "HANDOFF RESTART REFUSED (%d/%d): %s\nFix it, then end your message with "
                   "HANDOFF READY again. Past %d the Conductor is alarmed." % (n, MAX_BLOCKS, why, MAX_BLOCKS)},
                  out or sys.stdout)
    return 0


def cleared(SR, seat):
    try:
        os.remove(SR.refused_path(seat))
    except OSError:
        pass


def live_helpers(SR, cfg, path):
    """None (unreadable) counts as alive, as cmd_request's deferral does."""
    hs = SR.helpers_of(path, time.time(), cfg.get("helper_stale_s"))
    return True if hs is None else any(h.get("alive") for h in hs)


def on_stop(hook, seat, SR, out=None):
    """-> what was done: one word, for the selftest."""
    cfg = SR.config(SR._schedule()).get(seat)
    if not cfg or cfg.get("kind") == "conductor":
        return "skip"
    sid, path = hook.get("session_id"), hook.get("transcript_path")
    if SR.handoff_drain(seat, sid):
        if live_helpers(SR, cfg, path):
            return "draining"
        unpub = SR.unpublished_shard(seat, REPO)
        rc, txt = (1, "%s. Commit it by explicit path and ./publish." % unpub) if unpub else check(seat)
        if rc:
            refuse(SR, seat, sid, txt, out)
            return "refused"
        cleared(SR, seat)
        SR.kick_handoff(cfg)
        return "kicked"
    if not SR.says_handoff_ready(hook.get("last_assistant_message") or SR.last_assistant_text(path)):
        return "no"
    if not live_helpers(SR, cfg, path):
        rc, txt = check(seat)
        if rc:
            refuse(SR, seat, sid, txt, out)
            return "refused"
    rc, txt = request(seat)
    if rc or not SR.handoff_drain(seat, sid):   # rc 0 with no request recorded is a refusal too (a seat off restarts)
        refuse(SR, seat, sid, txt or "no request was recorded", out)
        return "refused"
    cleared(SR, seat)
    return "requested"


def main():
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        return 0
    import doorbell
    import seat_restart as SR
    seat = doorbell.seat_name()
    if seat:
        on_stop(hook, seat.upper(), SR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
