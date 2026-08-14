#!/usr/bin/env python3
"""gamestate.py — the game's state is MEASURED and STAMPED. Nobody declares it.

    python3 src/RimMandrake/Utils/gamestate.py                      # show
    python3 src/RimMandrake/Utils/gamestate.py stamp PLAYABLE "32 pawns, map drivable"
    python3 src/RimMandrake/Utils/gamestate.py take                 # take the instrument
    python3 src/RimMandrake/Utils/gamestate.py renew                # I am still using it
    python3 src/RimMandrake/Utils/gamestate.py release "left 1 hostile droid at 0,0"

WHY THIS REPLACED RULES 1a AND 1b
=================================
Owner's ruling, 2026-08-14, after a stall that cost most of a load window.

The old pair said PROJECT *declares* game state and that "live" means a map
exists as *measured by BRIDGE*. Both halves were defensible and together they
produced a deadlock: the owner said "the game is live" meaning **the game is up,
go**; BRIDGE heard **a map exists**, measured that one did not, and used a
measurement rule to refuse; PROJECT believed BRIDGE had to say it; BRIDGE
believed PROJECT had to; OPS waited to be told it was its turn. Everyone was
correct about a different noun and nothing moved.

Three faults, and this file exists to make each one impossible:

  1. ONE WORD, THREE STATES. "Live" meant the process is up, and a map exists,
     and the seats may touch the instrument. Those are now separate fields with
     separate names, and "live" is not one of them.
  2. A MEASUREMENT BECAME A VETO. Measuring is good; refusing to work because
     of what you measured is not. **A stamp labels reality. It never gates
     anyone.** Nothing in this file can block a seat.
  3. NOBODY OWNED CLOSING THE GAP. A map was one call and ~90 s away and its
     absence was reported instead of ended. See the standing rule below.

🔴 **THE STANDING RULE THIS ENCODES: never report a precondition you can
satisfy.** If you can close the gap yourself, close it and say so afterwards.
"There is no map" is not a status update when you own `start_debug_game_ready`.

🔴 **AND: the owner's word is a GO, not a claim to fact-check.** "The game is
live" means *begin*. The correct reply is "no map yet — making one, ~90 s",
never "no it isn't". Reconcile reality to the instruction; do not argue the
noun. ⚠️ Reads are always safe; **mutations still wait for a measured map and
the ~40 s settle** — that is physics, not permission.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STATE_FILE = os.path.join(ROOT, "infrastructure/state/status/game.json")

# The ladder. Each is a measurable fact, not an opinion.
STATES = {
    "DOWN":     "no RimWorld process",
    "LOADING":  "process up, mod stack still loading",
    "MENU":     "stack loaded and the bridge answers, but there is NO map",
    "PLAYABLE": "a map exists and is drivable",
}

# A lease is released by NOT being renewed. That is the whole point: today's
# failure was a TAKEN with no RELEASED, which marks the bridge occupied forever
# — the exact collision the announcement existed to prevent. A crashed seat
# cannot forget to renew.
LEASE_IDLE = 10 * 60


def load():
    try:
        with open(STATE_FILE) as fh:
            return json.load(fh)
    except Exception:
        return {}


def save(d):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(d, fh)
    os.replace(tmp, STATE_FILE)


def seat():
    return (os.environ.get("AGENT_SEAT") or "?").upper()


def lease_holder(d):
    """Returns (seat, held_secs, idle_secs) or None if free/expired."""
    ls = d.get("lease") or {}
    if not ls.get("seat"):
        return None
    idle = int(time.time()) - int(ls.get("renewed", 0))
    if idle > LEASE_IDLE:
        return None                       # expired: free, no action needed
    return ls["seat"], int(time.time()) - int(ls.get("taken", 0)), idle


def measure_process():
    """DOWN is the one state any seat can measure with no bridge at all."""
    try:
        out = subprocess.run(["tasklist.exe"], capture_output=True, text=True,
                             timeout=20).stdout.lower()
        return "rimworld" in out
    except Exception:
        return None


TICKER = os.path.join(os.path.dirname(STATE_FILE), "ticker.log")


def announce(line):
    """Make the event IMPOSSIBLE to miss — because recording it was not enough.

    🔴 **Owner's ruling 2026-08-14, and it is a correction to this file's own
    first design.** Releasing the instrument used to be a stamp: correct,
    atomic, and **silent**. The board read `FREE`, the release had genuinely
    happened, and the owner still had to ask who held the bridge — then point
    out that it should have been freed. It already had been. Nobody was told.

    **The old TAKEN/RELEASED pair failed LOUDLY — a dangling TAKEN is visible.
    The lease failed QUIETLY. We swapped an obvious failure for an invisible
    one and called it an improvement.** A timeout is not something a human can
    watch.

    So a release now pushes on every channel this script can reach by itself:
    a toast to the owner, and a ticker line the board renders. The one channel
    it cannot reach is the peers — a shell script cannot call SendMessage — so
    it prints the exact line and says so, rather than pretending it sent it.
    """
    try:
        with open(TICKER, "a") as fh:
            fh.write("%d %s\n" % (int(time.time()), line))
    except Exception:
        pass
    try:
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", os.path.join(ROOT, "src/RimMandrake/Utils/fleet_toast.ps1"),
             "-Title", "FLEET", "-Msg", line[:120]],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def show():
    d = load()
    st = d.get("state", "?")
    age = int(time.time()) - int(d.get("at", 0)) if d.get("at") else None
    who = d.get("by", "?")
    line = "game: %-9s" % st
    if age is None:
        line += "  (never stamped)"
    else:
        line += "  (%s, %s ago)" % (who, human(age))
    if d.get("note"):
        line += "  — %s" % d["note"]
    print(line)
    h = lease_holder(d)
    if h:
        print("instrument: held by %s, %s   idle %s   (auto-free at %s idle)"
              % (h[0], human(h[1]), human(h[2]), human(LEASE_IDLE)))
    else:
        print("instrument: FREE — take it, do not ask")
    # A stamp older than the process reality is the failure this file prevents;
    # say so rather than letting a stale value read as current.
    proc = measure_process()
    if proc is False and st != "DOWN":
        print("⚠️  no RimWorld process, but the stamp says %s — RESTAMP" % st)
    if proc is True and st == "DOWN":
        print("⚠️  a RimWorld process exists but the stamp says DOWN — RESTAMP")
    return 0


def human(s):
    s = int(s)
    if s < 90:
        return "%ds" % s
    if s < 5400:
        return "%dm" % (s // 60)
    return "%dh" % (s // 3600)


def main():
    a = sys.argv[1:]
    if not a or a[0] == "show":
        return show()
    d = load()
    cmd = a[0]

    if cmd == "stamp":
        if len(a) < 2 or a[1].upper() not in STATES:
            print("stamp <%s> [note]" % "|".join(STATES), file=sys.stderr)
            return 2
        d["state"] = a[1].upper()
        d["by"] = seat()
        d["at"] = int(time.time())
        d["note"] = " ".join(a[2:]) if len(a) > 2 else ""
        save(d)
        return show()

    if cmd == "take":
        h = lease_holder(d)
        if h and h[0] != seat():
            # Reported, never enforced — this tool cannot block anyone. A seat
            # that decides it needs the instrument anyway is making a judgment
            # call, which is exactly what a seat is for.
            print("instrument held by %s (%s, idle %s). Coordinate or wait."
                  % (h[0], human(h[1]), human(h[2])))
            return 1
        now = int(time.time())
        if not h:
            announce("BRIDGE TAKEN — %s" % seat())
        d["lease"] = {"seat": seat(),
                      "taken": (d.get("lease") or {}).get("taken", now)
                      if h else now,
                      "renewed": now}
        save(d)
        return show()

    if cmd == "renew":
        ls = d.get("lease") or {}
        if ls.get("seat") != seat():
            print("you do not hold it", file=sys.stderr)
            return 1
        ls["renewed"] = int(time.time())
        d["lease"] = ls
        save(d)
        return 0

    if cmd == "release":
        who = seat()
        left = " ".join(a[1:]) if len(a) > 1 else "nothing noted"
        d["lease"] = {}
        d["left"] = left
        save(d)
        line = "BRIDGE RELEASED — %s — %s" % (who, left)
        announce(line)
        print(line)
        print("")
        print("🔴 SEND THAT LINE TO EVERY SEAT NOW. One line, no ceremony.")
        print("   The owner has already been told (toast + board). Your peers")
        print("   have NOT — this script cannot call SendMessage.")
        return 0

    print(__doc__.split("WHY")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
