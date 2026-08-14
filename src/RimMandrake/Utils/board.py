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
LAST_STALLED = []              # set by render(), consumed by push() and the title


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


DWELL_FILE = os.path.join(STATUS_DIR, ".dwell.json")
DWELL_BEFORE_ALARM = 90        # seconds a seat must be stopped before it alarms


def dwell(live):
    """How long each seat has held its CURRENT state.

    ⚠️ **Without this the alarm band flaps and dies.** `blocked` is the normal,
    momentary state of any seat sitting on a permission prompt or mid-tool-call
    — a board that shouts on every one of those is the "rainbow dilution" and
    "all-green normalisation" failure in one: the band is always lit, so it
    stops being read, and the one time a seat is genuinely stuck it looks
    exactly like the ninety times it was not.

    Alert practice is explicit that a rule needs a minimum duration for which
    it must hold before firing. 90 s is chosen because a real permission prompt
    is answered in seconds, while a seat waiting on a human decision waits
    minutes. **Tune this number, do not delete the gate.**
    """
    now = int(time.time())
    prev = {}
    try:
        with open(DWELL_FILE) as fh:
            prev = json.load(fh)
    except Exception:
        pass
    out = {}
    for seat, state in live.items():
        p = prev.get(seat) or {}
        since = p.get("since", now) if p.get("state") == state else now
        out[seat] = {"state": state, "since": since}
    try:
        os.makedirs(STATUS_DIR, exist_ok=True)
        tmp = DWELL_FILE + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(out, fh)
        os.replace(tmp, DWELL_FILE)
    except Exception:
        pass
    return {k: now - v["since"] for k, v in out.items()}


TOASTED_FILE = os.path.join(STATUS_DIR, ".toasted.json")


def push(stalled):
    """One OS notification per stall, never per render.

    ⚠️ **The edge, not the level.** A toast every 5 s while a seat is stuck
    trains the owner to dismiss toasts, and the next real one is dismissed too.
    So we fire when a seat CROSSES into stalled and stay silent until it
    recovers — the same discipline an on-call system uses to keep its own
    channel worth reading.

    Failure here is always silent: a board that dies because a notifier failed
    is worse than a board with no notifications.
    """
    try:
        with open(TOASTED_FILE) as fh:
            already = set(json.load(fh))
    except Exception:
        already = set()
    now_stalled = {x[0] for x in stalled}
    fresh = now_stalled - already
    for seat, state, secs in stalled:
        if seat not in fresh:
            continue
        try:
            subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                 "-File", os.path.join(ROOT, "src/RimMandrake/Utils/fleet_toast.ps1"),
                 "-Title", "FLEET - %s NEEDS YOU" % seat,
                 "-Msg", ("%s for %dm - check its tab" % (state, secs // 60))[:120]],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    if fresh or (already - now_stalled):
        try:
            os.makedirs(STATUS_DIR, exist_ok=True)
            with open(TOASTED_FILE, "w") as fh:
                json.dump(sorted(now_stalled), fh)
        except Exception:
            pass


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

    # Game state is MEASURED and STAMPED, never declared (gamestate.py). The
    # roster no longer carries it: a fact you can measure must not also be a
    # sentence someone has to remember to write.
    g = {}
    try:
        with open(os.path.join(STATUS_DIR, "game.json")) as fh:
            g = json.load(fh)
    except Exception:
        pass
    gstate = g.get("state", "UNSTAMPED")
    gage = int(time.time()) - int(g.get("at", 0)) if g.get("at") else None
    ls = g.get("lease") or {}
    lidle = int(time.time()) - int(ls.get("renewed", 0)) if ls.get("renewed") else None
    holder = ls.get("seat") if (lidle is not None and lidle < 600) else None

    head = " FLEET   game: %s%s   instrument: %s " % (
        gstate,
        "" if gage is None else " (%s %s)" % (g.get("by", "?"), ago(int(time.time()) - gage).strip()),
        ("%s %s idle" % (holder, ago(int(time.time()) - lidle).strip())) if holder else "FREE")
    L.append("+" + head.ljust(W - 2, "-") + "+")

    if g.get("note"):
        L.append(row(g["note"]))
    # A stamp nobody has refreshed is the failure this replaced. Say its age
    # loudly rather than letting a stale value read as current fact.
    if gage is not None and gage > 900:
        L.append(row("!! game state stamped %s ago — nobody has measured since"
                     % ago(int(time.time()) - gage).strip()))

    # --- THE ALARM BAND ------------------------------------------------------
    # Rendered FIRST, and only when it has something to say. The research is
    # unanimous that the fix for a silently-stalled agent is PUSH, not poll:
    # a human scanning five panes for a seat that has quietly stopped is the
    # documented failure, not the remedy. A band that is usually absent is one
    # you actually read when it appears — a permanent "0 blocked" line is
    # wallpaper within a day.
    global LAST_STALLED
    held = dwell(live)
    stalled = [(seat, live[seat], held.get(seat, 0)) for seat in SEATS
               if live.get(seat) in NEEDS_HUMAN and seat != SELF
               and held.get(seat, 0) >= DWELL_BEFORE_ALARM]
    owner_rows = [f for f in r.get("OWNER", []) if len(f) >= 3]
    LAST_STALLED = stalled
    # Two bands, not one — they have very different hit rates and mixing them
    # destroys the good one.
    #
    # An owner decision is ALWAYS real: a human wrote it down because a human
    # must answer it. Hit rate 1.0.
    # A seat that looks stopped is a GUESS from a process state. Sometimes it
    # is genuinely stuck; sometimes it is between tasks or on a prompt it is
    # about to clear.
    #
    # The alarm literature is blunt about why this matters: people
    # probability-match their response rate to an alarm's observed reliability,
    # so a band that is right half the time gets obeyed about half the time —
    # and it drags whatever is next to it down with it. Keeping the certain
    # items in their own band, listed first, protects the one signal that is
    # always worth acting on.
    if owner_rows:
        n = len(owner_rows)
        L.append(bar("DECIDE   %d%s" % (
            n, "   << YOU ARE THE BOTTLENECK" if n > 3 else "")))
        for f in owner_rows:
            tag = "" if f[0] == "--" else "#%s " % f[0]
            L.append(row(">> %s%s" % (tag, f[1][:66])))
    if stalled:
        # Graded, not binary. A row carries WHY it is flagged, because showing
        # the agent's reasoning is measured to raise both performance and trust
        # at no cost in workload or response time — transparency is free here,
        # and a bare flag is the thing that gets ignored.
        L.append(bar("MAYBE STUCK   %d   (a guess — check the tab)" % len(stalled)))
        for seat, stv, secs in stalled:
            item = (st.get(seat, {}).get("item") or "").strip()
            why = item if item else "no status line set — may never have started"
            L.append(row(">> %-7s %-8s %s - %s"
                         % (seat, stv, ago(int(time.time()) - secs).strip(), why[:34])))

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
    # --- v1 LAST, deliberately: it is the scoreboard, not the work ----------
    # Band order is needs-me -> in-flight -> will-be-done -> done. That order is
    # near-universal across incident, CI and agent consoles, and it is the
    # opposite of how a status doc is usually written (goals at the top).
    # The goal band is the part that changes least, so it earns the least
    # valuable screen position. ⚠️ Keep the DONE rows visible: hiding passing
    # work is measured to induce "five failures and twenty-five failures look
    # the same" blindness. Green stays on screen as ratio, not as detail.
    L.append(bar("V1"))
    v1 = r.get("V1", [])
    cells = []
    for f in v1:
        if len(f) < 4:
            continue
        cells.append("%s %s %s" % (MARK.get(f[3], "[?]"), f[0], f[1][:24]))
    for i in range(0, len(cells), 2):
        L.append(row(cells[i].ljust(35) + (cells[i + 1] if i + 1 < len(cells) else "")))

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
                out = render()
                push(LAST_STALLED)
                # OSC 0: the tab title carries the count, so the fleet is
                # legible from the taskbar with no pane visible at all.
                title = ("%d NEEDS YOU - fleet" % len(LAST_STALLED)) if LAST_STALLED else "fleet - all running"
                sys.stdout.write("\033]0;%s\007" % title)
                sys.stdout.write("\033[H\033[J" + out + "\n")
                sys.stdout.flush()
                time.sleep(5)
        except KeyboardInterrupt:
            return 0
    print(render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
