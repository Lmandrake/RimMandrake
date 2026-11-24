#!/usr/bin/env python3
"""A hang guard on progress: end a child that shows no sign of life, never one that is slow and alive.

The sign of life is growth of the child's output, or of the CPU time of its process tree (waitalive.tree_cpu, the same
reading that a long wait uses). A wall-clock deadline cannot tell a hang from a loaded machine: at load 28 to 52 the
pipeline tests took 7 to 12 times their run alone, and the 180 s deadline of ./publish ended 207 live checks in 14 days.

    communicate(p, silence_s, cap_s) -> (out, err)      raises Hung; the caller kills (a Hung child is still running)
    run(argv, silence_s, cap_s, **kw) -> CompletedProcess    kills the child's whole session, then raises Hung

Page: design/specs/2026-11-24-progress-guard/boundary.md (LIMITS names the danger of each number).
"""
import os
import selectors
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import waitalive  # noqa: E402

# budget: danger=a hung child holds its caller with no end; evidence=INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT 2026-11-03 (a
# budget: WSL interop launch that never answered; new on 2026-11-24); never reached in the 14 days to 2026-11-24; no record of
# budget: its run
SILENCE_S = 1800
POLL_S = 2.0
# budget: danger=a process that a finished child left behind holds its pipe open with no end (run_selftests audit 7);
# budget: ends no work: the child has exited and its result is returned
LEFT_OPEN_S = 15


class Hung(subprocess.TimeoutExpired):
    """A child ended by a guard. `why` says which guard; it is never a verdict on what the child was measuring."""

    def __init__(self, cmd, timeout, why):
        super().__init__(cmd, timeout)
        self.why = why

    def __str__(self):
        return self.why


def communicate(p, silence_s=SILENCE_S, cap_s=None, poll_s=POLL_S, cpu=waitalive.tree_cpu, clock=time.monotonic):
    """p: a Popen with stdout and stderr pipes (binary or text). -> (out, err) as bytes or text, as `p` was opened.
    Raises Hung when nothing grew for silence_s, or past cap_s (the backstop for a child that spins). None: no backstop."""
    start = last = clock()
    got = {f: [] for f in (p.stdout, p.stderr) if f is not None}
    seen_cpu, next_cpu = None, 0.0
    sel = selectors.DefaultSelector()
    for f in got:
        sel.register(f, selectors.EVENT_READ)
    try:
        while True:
            ended = p.poll() is not None
            grew = False
            for key, _ in (sel.select(timeout=poll_s) if sel.get_map() else []):
                data = os.read(key.fd, 65536)
                if data:
                    got[key.fileobj].append(data)
                    grew = True
                else:
                    sel.unregister(key.fileobj)
            if ended and (not sel.get_map() or (not grew and clock() - last >= LEFT_OPEN_S)):
                break       # whole; or a process it left behind holds the pipe, and the child's own result is in
            if not sel.get_map():
                try:
                    p.wait(timeout=poll_s)
                except subprocess.TimeoutExpired:
                    pass
            now = clock()
            if now >= next_cpu:
                next_cpu = now + poll_s
                try:
                    c = cpu(p.pid)
                    grew = grew or c != seen_cpu
                    seen_cpu = c
                except (waitalive.CouldNotLook, OSError):
                    grew = True     # the instrument could not look: no evidence of a hang
            if grew:
                last = now
            elif now - last >= silence_s:
                raise Hung(p.args, silence_s, "hung: no output and no CPU time in its process tree for %d s" % silence_s)
            if cap_s is not None and now - start >= cap_s:
                raise Hung(p.args, cap_s, "past its %d s backstop (it was still using CPU time or writing)" % cap_s)
    finally:
        sel.close()

    def whole(f):
        if f is None:
            return None
        data = b"".join(got[f])
        enc = getattr(f, "encoding", None)
        return data.decode(enc, "replace") if enc else data
    return whole(p.stdout), whole(p.stderr)


def kill_session(p):
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError:
        pass
    try:
        # budget: danger=a killed child in uninterruptible IO never reaps; its reach leaves no record; no record of its run
        p.wait(timeout=15)
    except subprocess.TimeoutExpired:
        pass
    for f in (p.stdout, p.stderr):
        if f is not None:
            try:
                f.close()
            except OSError:
                pass


def run(argv, silence_s=SILENCE_S, cap_s=None, text=True, **kw):
    """subprocess.run(argv, capture_output=True) with a guard on progress in place of a wall-clock timeout."""
    kw.setdefault("stdin", subprocess.DEVNULL)
    with_session = dict(kw, start_new_session=True)
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text, **with_session)
    try:
        out, err = communicate(p, silence_s, cap_s)
    except BaseException:
        kill_session(p)
        raise
    return subprocess.CompletedProcess(argv, p.returncode, out, err)
