#!/usr/bin/env python3
"""A per-machine line for ./publish's door checks: at most SLOTS run their full checkout and checks at once, the rest
wait first come first served, and a dead holder frees its slot at once (a slot is a flock held by a live process).

    with Gate(root) as g:      # one publish
        g.take("tree checks")  # waits for a slot (no-op when held already, or inside a held slot); prints while it waits
        ...                    # the slot is dropped when the with block ends

Page: design/specs/2026-11-24-treecheck-slots/boundary.md (LIMITS names the danger and the measurement of SLOTS).
Layout of `root`: slot.<i> (flocked by its holder; holds "pid argv"), queue/<time_ns>-<pid> (a waiter's ticket,
flocked by the waiter; one with no lock is a dead waiter's and is removed).
"""
import fcntl
import os
import sys
import time

# budget: danger=six door checks at once saturated SteveDesktop's disk (2026-11-24 5:49-9:41 PM PST: 100% busy, load 47, a
# budget: publish starved 148 min, hang guards fired on healthy git); evidence=Archmagi 2026-11-24: one run 50 s alone, 44 s
# budget: each at 2, 82 at 4, 133 at 6, 179 at 8: throughput flat from 2 up, so more only adds wait and load
SLOTS = 2
SLOTS_ENV = "RM_TREECHECK_SLOTS"
HELD_ENV = "RM_TREECHECK_SLOT_HELD"     # set while a slot is held: a child of a holder passes the gate at once
SAY_S = 30.0        # budget: ends no work: the waiting line repeats this often; the wait goes on
POLL_S = 0.2        # budget: ends no work: how often a waiter looks at the line


def slots_n():
    v = os.environ.get(SLOTS_ENV, "").strip()
    try:
        return max(1, int(v)) if v else SLOTS
    except ValueError:
        print("treecheck_slots: %s=%r is not a number; using %d" % (SLOTS_ENV, v, SLOTS), file=sys.stderr, flush=True)
        return SLOTS


HELD, FREE = -2, -1      # _try_lock's two answers that are not a kept fd


def _try_lock(path, keep):
    """-> an fd holding path's flock (keep=True), FREE (keep=False: it was free; probed and released at once), or HELD
    (a live process holds it). An OSError (the file or its folder cannot be opened) is raised: could not look."""
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return HELD
    if keep:
        return fd
    os.close(fd)
    return FREE


class Gate:
    def __init__(self, root, n=None, say_s=SAY_S, poll_s=POLL_S, out=None):
        self.root, self.n = root, n if n is not None else slots_n()
        self.say_s, self.poll_s, self.out = say_s, poll_s, out or sys.stderr
        self.fd, self.ours = None, False

    def say(self, text):
        print("publish: " + text, file=self.out, flush=True)

    def _slot_paths(self):
        return [os.path.join(self.root, "slot.%d" % i) for i in range(self.n)]

    def _live_tickets(self, qdir, mine):
        """-> the sorted names of live waiters' tickets; a ticket with no lock on it is a dead waiter's: removed."""
        live = []
        for name in sorted(os.listdir(qdir)):
            if name.startswith("."):
                continue
            p = os.path.join(qdir, name)
            if name != mine:
                try:
                    free = _try_lock(p, keep=False) == FREE
                except FileNotFoundError:                 # it left the line between the listing and the look
                    continue
                if free:                                  # nobody holds it: its waiter died
                    try:
                        os.unlink(p)
                    except FileNotFoundError:
                        pass
                    continue
            live.append(name)
        return live

    def _holders(self):
        out = []
        for p in self._slot_paths():
            try:
                held = _try_lock(p, keep=False) == HELD
            except OSError:
                held = False
            if held:
                try:
                    out.append(open(p).read().strip().split(" ")[0] or "?")
                except OSError:
                    out.append("?")
        return out

    def take(self, what="tree checks"):
        if self.fd is not None or os.environ.get(HELD_ENV):
            return
        qdir = os.path.join(self.root, "queue")
        try:
            os.makedirs(qdir, exist_ok=True)
            tmp = os.path.join(qdir, ".new-%d-%d" % (os.getpid(), time.time_ns()))
            tfd = os.open(tmp, os.O_CREAT | os.O_RDWR, 0o644)
            fcntl.flock(tfd, fcntl.LOCK_EX)              # locked before it is visible, so no live ticket reads as dead
            mine = "%020d-%d" % (time.time_ns(), os.getpid())
            os.rename(tmp, os.path.join(qdir, mine))
        except OSError as e:
            self.say("could not open the tree-check line %s (%s); running the %s without it" % (self.root, e, what))
            return
        began, said = time.monotonic(), None
        try:
            while self.fd is None:
                live = self._live_tickets(qdir, mine)
                ahead = live.index(mine) if mine in live else 0
                if ahead == 0:
                    for p in self._slot_paths():
                        fd = _try_lock(p, keep=True)
                        if fd != HELD:
                            self.fd = fd
                            try:
                                os.ftruncate(fd, 0)
                                os.write(fd, ("%d %s\n" % (os.getpid(), " ".join(sys.argv)[:200])).encode())
                            except OSError:
                                pass
                            break
                if self.fd is not None:
                    break
                now = time.monotonic() - began
                if said is None or now >= said + self.say_s:
                    said = now if said is None else said + self.say_s
                    h = self._holders()
                    self.say("waiting %d s for a tree-check slot, %d ahead, %d running (%s); the %s start when one frees"
                             % (now, ahead, len(h), ", ".join("pid " + x for x in h) or "none", what))
                time.sleep(self.poll_s)
        except OSError as e:                             # the line could not be read: could not look, not a refusal
            self.say("could not read the tree-check line %s (%s); running the %s without it" % (self.root, e, what))
        finally:
            try:
                os.unlink(os.path.join(qdir, mine))
            except FileNotFoundError:
                pass
            os.close(tfd)
        if self.fd is None:
            return
        os.environ[HELD_ENV] = str(os.getpid())
        self.ours = True
        if said is not None:
            self.say("took a tree-check slot after %d s" % (time.monotonic() - began))

    def drop(self):
        if self.fd is not None:
            os.close(self.fd)                            # closing releases the flock
            self.fd = None
        if self.ours:
            os.environ.pop(HELD_ENV, None)
            self.ours = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.drop()
        return False
