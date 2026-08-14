#!/usr/bin/env python3
"""board.py — the one screen the owner reads instead of five scrolling tabs.

    python3 src/RimMandrake/Utils/board.py            # render once
    python3 src/RimMandrake/Utils/board.py --watch    # redraw every 5s, never scrolls
    python3 src/RimMandrake/Utils/board.py say "L4 droid double-spawn"   # set my line

WHAT IT JOINS
=============
Three sources, deliberately, because no single one can be trusted alone:

  the ROSTER   `infrastructure/state/BOARD.md`   what we said we would do
  the STAMPS   `infrastructure/state/status/`    that a seat is breathing (hook)
  the REGISTRY `~/.claude/sessions/<pid>.json`   who is actually launched (peers)

⚠️ **The roster is hand-maintained and therefore the part that can lie.** Every
other field on screen is measured. So the board prints the roster's own age next
to it: if BOARD.md has not been touched in hours while five seats are busy, that
is the tell, and it is on screen rather than buried.

WHY NOT PARSE NEXT_RELOAD.md DIRECTLY
=====================================
It is 636 lines of prose that five seats rewrite continuously. A regex over it
would mis-parse silently, and a board that is quietly wrong is worse than none —
that is the failure this whole exercise exists to end. BOARD.md is short, flat
and pipe-delimited so that parsing it cannot be ambiguous.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ROSTER = os.path.join(ROOT, "infrastructure/state/BOARD.md")
STATUS_DIR = os.path.join(ROOT, "infrastructure/state/status")
SEATS = ["BRIDGE", "OPS", "CREATE", "VISION", "PROJECT"]
# A seat cannot usefully raise an alarm about itself: it is "blocked" for
# the duration of the very tool call that renders this board.
SELF = (os.environ.get("AGENT_SEAT") or "").upper()

AMBER_AFTER = 15 * 60          # a seat silent this long is flagged, never hidden
W = 74                         # box width

MARK = {"done": "[x]", "open": "[ ]", "wip": "[~]",
        "held": "[-]", "blocked": "[!]"}
DOT = {"busy": "*", "idle": "o", "waiting": "!", "blocked": "!"}
# Higher = more urgent. Drives both the alarm band and dedup above.
RANK = {"idle": 1, "busy": 2, "waiting": 9, "blocked": 9}
NEEDS_HUMAN = ("waiting", "blocked")


# ---------------------------------------------------------------- roster ----
def read_roster():
    """Parse BOARD.md into {section: [fields]}. Unknown sections are kept, so
    adding one to the file needs no change here."""
    out, sec = {}, None
    if not os.path.exists(ROSTER):
        return out
    with open(ROSTER, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("## "):
                sec = line[3:].strip()
                out[sec] = []
            elif sec and "|" in line and not line.startswith(("#", "_", "**")):
                out[sec].append([c.strip() for c in line.split("|")])
    return out


def kv(rows, key, default=""):
    for r in rows:
        if r and r[0] == key:
            return r[1] if len(r) > 1 else default
    return default


# ---------------------------------------------------------------- status ----
def read_status():
    """Per-seat stamps. Absent file = seat never ran, which is itself a finding."""
    out = {}
    for seat in SEATS:
        p = os.path.join(STATUS_DIR, "%s.json" % seat)
        try:
            with open(p) as fh:
                out[seat] = json.load(fh)
        except Exception:
            out[seat] = {}
    return out


def live_seats():
    """Seat -> state, from `claude agents --json`.

    ⚠️ **This replaced a hand-rolled join over the session registry.** The CLI is
    the SUPPORTED surface, it already reports interactive sessions (not only
    background ones), and — the reason that matters — it distinguishes
    `blocked` / `waiting` from `busy`. **That distinction is the whole point:**
    on 2026-08-14 BRIDGE sat waiting on the owner's word at the main menu while
    the owner believed work was in flight, because nothing on any screen
    separated "thinking hard" from "stopped, needs a human".

    ⚠️ **Deliberately shells out to `claude`, never to `git`.** A status pane
    that runs `git status` on a timer grabs `.git/index.lock` and loses a
    seat's commit — a documented failure in shared-tree fleets. The roster age
    below is read with `os.path.getmtime`, not a git subprocess, for the same
    reason. **Never add a git call to this file.**
    """
    try:
        out = subprocess.run(["claude", "agents", "--json"],
                             capture_output=True, text=True, timeout=15)
        rows = json.loads(out.stdout)
    except Exception:
        return {}
    seats = {}
    for r in rows:
        name = (r.get("name") or "").upper()
        if not name.startswith("AGENT "):
            continue
        seat = name[6:].strip()
        st = r.get("status") or r.get("state") or "?"
        # A seat with several rows (a dead PID beside a live one) resolves to
        # the one that needs a human: blocked beats busy beats idle.
        if seat in seats and RANK.get(seats[seat], 0) >= RANK.get(st, 0):
            continue
        seats[seat] = st
    return seats


def ago(ts):
    if not ts:
        return "  never"
    d = int(time.time()) - int(ts)
    if d < 90:
        return "%5ds" % d
    if d < 5400:
        return "%5dm" % (d // 60)
    return "%5dh" % (d // 3600)


# ----------------------------------------------------------------- render ---
def bar(title=""):
    if not title:
        return "+" + "-" * (W - 2) + "+"
    return "+-- " + title + " " + "-" * (W - 6 - len(title)) + "+"


def row(text):
    text = text[:W - 4]
    return "| " + text.ljust(W - 4) + " |"


def render():
    r = read_roster()
    st = read_status()
    live = live_seats()
    L = []

    game = kv(r.get("GAME", []), "state", "?").upper()
    bridge = kv(r.get("GAME", []), "bridge", "--") or "--"
    head = " FLEET   game: %s   bridge: %s " % (game, bridge)
    L.append("+" + head.ljust(W - 2, "-") + "+")

    note = kv(r.get("GAME", []), "note")
    if note:
        L.append(row(note))

    # --- THE ALARM BAND ------------------------------------------------------
    # Rendered FIRST, and only when it has something to say. The research is
    # unanimous that the fix for a silently-stalled agent is PUSH, not poll:
    # a human scanning five panes for a seat that has quietly stopped is the
    # documented failure, not the remedy. A band that is usually absent is one
    # you actually read when it appears — a permanent "0 blocked" line is
    # wallpaper within a day.
    stalled = [(seat, live[seat]) for seat in SEATS
               if live.get(seat) in NEEDS_HUMAN and seat != SELF]
    owner_rows = [f for f in r.get("OWNER", []) if len(f) >= 3]
    if stalled or owner_rows:
        L.append(bar("NEEDS YOU"))
        for seat, stv in stalled:
            item = (st.get(seat, {}).get("item") or "").strip() or "(no line set)"
            L.append(row(">> %-7s %-8s STOPPED - %s" % (seat, stv, item[:40])))
        for f in owner_rows:
            tag = "" if f[0] == "--" else "#%s " % f[0]
            L.append(row(">> %s%s" % (tag, f[1][:66])))

    # --- v1, two per line: it is a goal tracker, not a task list -------------
    L.append(bar("V1"))
    v1 = r.get("V1", [])
    cells = []
    for f in v1:
        if len(f) < 4:
            continue
        cells.append("%s %s %s" % (MARK.get(f[3], "[?]"), f[0], f[1][:24]))
    for i in range(0, len(cells), 2):
        L.append(row(cells[i].ljust(35) + (cells[i + 1] if i + 1 < len(cells) else "")))

    # --- seats: the only measured band --------------------------------------
    L.append(bar("SEATS"))
    for seat in SEATS:
        s = st.get(seat, {})
        state = live.get(seat, "--")
        dot = DOT.get(state, "-")
        item = (s.get("item") or "").strip() or "(no line set)"
        age = ago(s.get("updated"))
        flag = ""
        if s.get("updated") and int(time.time()) - int(s["updated"]) > AMBER_AFTER:
            flag = " !"
        L.append(row("%s %-7s %-8s %-36s %s%s"
                     % (dot, seat, state[:8], item[:36], age, flag)))

    # --- the checklist ------------------------------------------------------
    for sec, label in (("LOAD", "THIS LOAD"), ("SHUTDOWN", "NEXT SHUTDOWN")):
        items = [f for f in r.get(sec, []) if len(f) >= 4]
        if not items:
            continue
        openn = sum(1 for f in items if f[3] not in ("done",))
        L.append(bar("%s   %d open / %d" % (label, openn, len(items))))
        for f in items:
            L.append(row("%s %-4s %-46s %s"
                         % (MARK.get(f[3], "[?]"), f[0], f[1][:46], f[2][:9])))

    # --- what is blocked on the owner --------------------------------------
    # --- the roster's own honesty line -------------------------------------
    try:
        rage = ago(int(os.path.getmtime(ROSTER)))
    except Exception:
        rage = "  ?"
    L.append(bar())
    L.append(row("roster edited %s ago   (hand-maintained: the one part that can lie)"
                 % rage.strip()))
    L.append(bar())
    return "\n".join(L)


# -------------------------------------------------------------------- say ---
def say(text):
    """A seat sets its own one-line 'what I am doing'. Merges into the stamp
    file so the hook's liveness fields survive."""
    seat = (os.environ.get("AGENT_SEAT") or "").upper()
    if not seat:
        print("no AGENT_SEAT in env — run this from a fleet seat", file=sys.stderr)
        return 1
    p = os.path.join(STATUS_DIR, "%s.json" % seat)
    os.makedirs(STATUS_DIR, exist_ok=True)
    cur = {}
    if os.path.exists(p):
        try:
            with open(p) as fh:
                cur = json.load(fh)
        except Exception:
            pass
    cur["seat"] = seat
    cur["item"] = text
    cur.setdefault("updated", int(time.time()))
    tmp = p + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(cur, fh)
    os.replace(tmp, p)
    return 0


def main():
    a = sys.argv[1:]
    if a and a[0] == "say":
        return say(" ".join(a[1:]))
    if a and a[0] in ("--watch", "-w"):
        try:
            while True:
                # \033[H homes the cursor instead of scrolling; \033[J clears
                # to end of screen. Together they redraw in place, which is the
                # entire point — this pane must never produce scrollback.
                sys.stdout.write("\033[H\033[J" + render() + "\n")
                sys.stdout.flush()
                time.sleep(5)
        except KeyboardInterrupt:
            return 0
    print(render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
