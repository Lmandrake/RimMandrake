#!/usr/bin/env python3
"""selftest_wrapup_live_clone.py — RIMMANDRAKE_SPARE_LIVE_CLONE_FROM_DEBRIS_FIFTH_RUN_SAME: a filed clone row stops
standing while a live process works in that clone.

The incident (unrouted-20261102214722) relapsed on wrapup.debris_standing 4: four wrap-ups of earlier detached runs of
one item had filed its .det clone, and the fifth run of that item was working in the same clone. Work in flight is not
debris; once nothing runs there, dirt left behind stands again.

  L1  a dirty filed clone with a live process inside it does not stand
  L2  the same clone with nothing running inside it stands
  L3  clone_in_use unmeasurable (raises): the row stands (never clear on ignorance)
  L4  World.clone_in_use sees a real process whose cwd is inside the clone, and not after it exits

OPS_WRAPUP_SKIP_CLONES_OF_LIVE_FLEET_RUN extends it to the clone a live cleanse MOD owns. The cwd test cannot see a
designer_cleanse fleet: its unit runs with WorkingDirectory=ROOT (designer_cleanse.fleet_unit_argv), it gives its
author and reviewer subprocesses cwd=clone only inside a phase, and the blind sort runs in a tempfile.mkdtemp, so
between phases NO process has its cwd in the clone while the mod's run still owns it and will commit there again. The
ownership IS recorded, elsewhere: designer_cleanse.mod_lock holds an exclusive flock on the clone's dot-sibling
`<pool>/clones/.cleanse-<Mod>.lock`, held across `one()` for the whole of that mod's run and dropped by the kernel the
moment the holder exits or dies.

The window is the MOD's run, not the fleet's life, and that is deliberate [measured, 2026-11-17]: the alarming row on
`cleanse-Greentide` was filed 09:39:11Z and read at 09:51Z, while Greentide's own phases ran 09:03:50Z (5424d9190a,
proposal) to 09:23:00Z (b7d516bd34, review). Its lock was already released; that alarm was a TRUE positive about a
stray root draft nobody was coming back to (Effects.release kept the clone because `changed()` was non-empty), and
this check leaves it standing. Suppressing it for the fleet's whole 8-hour life over 23 mods would hide real debris.

  L5  ACCEPTANCE: a dirty filed clone whose dot-sibling lock a live process holds does not stand, though no process
      has its cwd inside it (the phase-gap regime)
  L6  the same clone once that run ended (the lock file is there, unheld) stands again
  L7  no lock file beside the clone at all — a measured empty set, not a failure — and nothing running: it stands
  L8  "could not look" is not "nothing holds it": either reading unmeasurable leaves the row standing, and the why
      says `unmeasured` by name
  L9  wrapup.lock_holder over MEASURED /proc/locks text: the holder's pid, never a `-> ` blocked waiter, no match on
      another inode, device or an empty file
  L10 wrapup.clone_lock_path IS the path designer_cleanse.mod_lock locks (read from designer_cleanse, not guessed)
  L11 (needs /proc/locks) World.clone_owner on a real flock: none -> free -> live while a child holds it with its cwd
      OUTSIDE the clone -> free again once that child is killed
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest_wrapup_live_")
os.environ["RM_WRAPUP_DIR"] = os.path.join(TMP, "state")
os.environ["RIMFLOW_SHARED_BRIDGE"] = ""
os.environ["RM_WRAPUP_PREV_LOG"] = ""

import wrapup  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


class Fake(wrapup.World):
    def __init__(self, in_use=False, raises=False, owner=("none", "no lock file"), owner_raises=False,
                 real_owner=False):
        self.in_use, self.raises = in_use, raises
        self.owner, self.owner_raises, self.real_owner = owner, owner_raises, real_owner

    def shared_bridge(self):
        return None

    def clone_in_use(self, clone):
        if self.raises:
            raise OSError("proc unreadable")
        return self.in_use

    def clone_owner(self, clone):
        if self.owner_raises:
            raise OSError("owner unreadable")
        return wrapup.World.clone_owner(self, clone) if self.real_owner else self.owner


clone = os.path.join(TMP, "ITEM.det")
os.makedirs(clone)
subprocess.run(["git", "init", "-q", clone], check=True)
with open(os.path.join(clone, "work.txt"), "w") as f:
    f.write("in flight\n")
rec = {"at": wrapup._iso(time.time()), "kind": "unit", "key": "u1", "seat": "BENCH", "clones": [clone],
       "rows": [{"kind": "clone", "what": clone, "act": "filed", "why": "1 uncommitted path"}]}
wrapup._write_json(wrapup._p("open", "unit-u1.json"), rec)


def n_standing(world):
    return sum(len(rs) for _, _, rs in wrapup.standing(world))


check(n_standing(Fake(in_use=True)) == 0, "L1 a dirty clone a live process works in does not stand")
check(n_standing(Fake(in_use=False)) == 1, "L2 the dirty clone with nothing running inside stands")
check(n_standing(Fake(raises=True)) == 1, "L3 an unmeasurable clone_in_use leaves the row standing")

# OPS_WRAPUP_SKIP_CLONES_OF_LIVE_FLEET_RUN -----------------------------------------------------------------------
# Every case below has NO process with its cwd in the clone (in_use=False): that is the incident, where the cwd test
# read "nothing here" about a clone a live fleet owned.
check(n_standing(Fake(in_use=False, owner=("live", "held by pid 2245702"))) == 0,
      "L5 a dirty clone whose lock a live cleanse run holds does not stand, though nothing has its cwd inside")
check(n_standing(Fake(in_use=False, owner=("free", "lock file held by nobody"))) == 1,
      "L6 the clone of a run that has ended (its lock unheld) stands again, even while the fleet lives on")
check(n_standing(Fake(in_use=False, owner=("none", "no lock file beside the clone"))) == 1,
      "L7 no lock file beside the clone (a measured empty set) and nothing running: the row stands")

rows8 = [r for _, _, rs in wrapup.standing(Fake(in_use=False, owner_raises=True)) for r in rs]
check(len(rows8) == 1 and "unmeasured" in (wrapup.clone_owner_state(Fake(owner_raises=True), clone)[1]),
      "L8 an unmeasurable clone_owner leaves the row standing and says unmeasured by name: %r" % (
          wrapup.clone_owner_state(Fake(owner_raises=True), clone),))
check(wrapup.clone_owner_state(Fake(owner_raises=True), clone)[0] == "unmeasured"
      and wrapup.clone_owner_state(Fake(owner=("free", "x")), clone)[0] == "free"
      and wrapup.clone_owner_state(Fake(owner=("none", "x")), clone)[0] == "none"
      and wrapup.clone_owner_state(Fake(owner=("live", "x")), clone)[0] == "live",
      "L8 could-not-look, nothing-holds-it, no-such-lock and held are four different answers")

# L9: the parser, over /proc/locks text MEASURED on linux 6.x (docker python:3.12-slim, 2026-11-17). Field 5 is
# maj:min:ino as %02x:%02x:%d; a line whose second token is `->` is a process BLOCKED waiting, not the holder.
LOCKS = ("10: FLOCK  ADVISORY  WRITE 1 00:2a:2637126 0 EOF\n"
         "10: -> FLOCK  ADVISORY  WRITE 7 00:2a:2637126 0 EOF\n"
         "3: POSIX  ADVISORY  WRITE 44 00:2a:999 0 EOF\n")
WAITER_ONLY = "10: -> FLOCK  ADVISORY  WRITE 7 00:2a:2637126 0 EOF\n"
check(wrapup.lock_holder(LOCKS, 0x2a, 2637126) == 1
      and wrapup.lock_holder(LOCKS, 0x2a, 999) == 44                      # a POSIX lock holds it too
      and wrapup.lock_holder(WAITER_ONLY, 0x2a, 2637126) is None          # a blocked waiter is not a holder
      and wrapup.lock_holder(LOCKS, 0x2a, 123456) is None                 # another inode on the same device
      and wrapup.lock_holder(LOCKS, 0x99, 2637126) is None                # the same inode on another device
      and wrapup.lock_holder("", 0x2a, 2637126) is None,                  # an empty file = nothing holds anything
      "L9 lock_holder reads the holder's pid off measured /proc/locks, never a blocked waiter or another dev/inode")

# L10: the path, read from designer_cleanse rather than guessed.
sys.path.insert(0, HERE)
import designer_cleanse as DC  # noqa: E402

POOL = os.path.join(TMP, "pool")
os.environ["RM_DETACHED_POOL"] = POOL
os.makedirs(os.path.join(POOL, "clones"), exist_ok=True)
cleanse_clone = os.path.join(POOL, "clones", "cleanse-Greentide")
with DC.mod_lock("Greentide"):
    locked_now = sorted(os.listdir(os.path.join(POOL, "clones")))
check(locked_now == [".cleanse-Greentide.lock"]
      and os.path.realpath(wrapup.clone_lock_path(cleanse_clone)) == os.path.realpath(
          os.path.join(POOL, "clones", ".cleanse-Greentide.lock")),
      "L10 clone_lock_path names the very file designer_cleanse.mod_lock locks (%r vs %r)" % (
          wrapup.clone_lock_path(cleanse_clone), locked_now))

# L11: the real reading, against a real flock. The holder's cwd is deliberately OUTSIDE the clone: that is the whole
# point of the incident. No /proc/locks (darwin, a sandbox) is reported as unmeasured, never as a pass.
if not os.path.exists("/proc/locks"):
    print("SKIP L11 unmeasured on this platform: no /proc/locks (run it on linux; the suite's host has it)")
else:
    w11 = wrapup.World()
    # Its OWN clone name: L10's mod_lock opened `.cleanse-Greentide.lock` with "a" and the kernel keeps the file after
    # releasing the lock, so that name can never read "none" again [measured: L11a read ("free", ...) against the
    # Greentide name]. Hence "free" is the state of every clone a fleet has EVER locked, and "none" only of one no
    # fleet ever touched. Both leave the row standing, which is why neither may be the clearing answer.
    fresh = os.path.join(POOL, "clones", "cleanse-Neverlocked")
    check(w11.clone_owner(fresh)[0] == "none",
          "L11a no lock file beside the clone reads none: %r" % (w11.clone_owner(fresh),))
    check(w11.clone_owner(cleanse_clone)[0] == "free",
          "L11b the lock file L10's mod_lock left behind, now held by nobody, reads free: %r" % (
              w11.clone_owner(cleanse_clone),))
    lk11 = wrapup.clone_lock_path(cleanse_clone)
    holder = subprocess.Popen([sys.executable, "-c", "import fcntl,sys,time\nfh=open(sys.argv[1],'a')\n"
                               "fcntl.flock(fh,fcntl.LOCK_EX)\nsys.stdout.write('got\\n')\nsys.stdout.flush()\n"
                               "time.sleep(60)", lk11], cwd=TMP, stdout=subprocess.PIPE, text=True)
    try:
        holder.stdout.readline()                    # it has the lock (no sleep-and-hope)
        got = w11.clone_owner(cleanse_clone)
    finally:
        holder.kill()
        holder.wait()
    for _ in range(50):                             # the kernel drops the lock as the holder dies
        after = w11.clone_owner(cleanse_clone)
        if after[0] != "live":
            break
        time.sleep(0.1)
    check(got[0] == "live" and str(holder.pid) in got[1] and after[0] == "free",
          "L11c a live flock holder with its cwd outside the clone reads live (%r), free once it dies (%r)" % (
              got, after))

w = wrapup.World()
p = subprocess.Popen(["sleep", "30"], cwd=os.path.join(clone))
try:
    time.sleep(0.2)
    seen = w.clone_in_use(clone)
finally:
    p.kill()
    p.wait()
check(seen is True and w.clone_in_use(clone) is False and w.clone_in_use(os.path.join(TMP, "ITEM")) is False,
      "L4 World.clone_in_use sees a process with its cwd in the clone, not after it exits, not a prefix sibling")

print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
