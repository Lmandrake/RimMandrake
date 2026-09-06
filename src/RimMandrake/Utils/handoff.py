#!/usr/bin/env python3
"""
Prepare a seat reboot handoff — the mechanical half, so the agent writes only the
half that needs judgment.

Owner, 2026-09-06: *"Is there a way for an agent to automatically prepare for
agent reboot when it finishes a big wave and it thinks it's a good time to hand
off? Then it could just say HANDOFF READY at the end and I could reboot myself
while keeping things in cache."*

So: at the end of a wave the agent runs

    python3 src/RimMandrake/Utils/handoff.py

which GATES first (refusing if the seat is not actually safe to reboot), then
writes `infrastructure/state/items/<SEAT>_REBOOT_HANDOFF_<stamp>.md` with every
fact a script can establish — items closed and filed since the last handoff,
the commits, game and bridge state, the live mod count, what is uncommitted —
and prints the headings the agent must fill in itself.

🔑 THE DIVISION OF LABOUR IS THE POINT. A script can list what closed; it cannot
say which finding the owner needs to see, or which trap cost two hours. Those
sections are left as explicit TODO markers and `--check` refuses to call the
handoff ready while any survives — a handoff that is only a changelog is the
failure this is meant to prevent, and an unfilled marker is louder than a
missing section nobody notices.

⛔ IT NEVER SAYS "HANDOFF READY" ITSELF. Only the agent does, after filling the
judgment sections, and only when `--check` passes. That phrase is the owner's
signal to reboot; a script that could emit it would eventually emit it wrongly.

    handoff.py                write the skeleton (gates first, --force to skip)
    handoff.py --check        gates + TODO scan only; exit 1 if not ready
    handoff.py --since <sha>  window start override (default: the last handoff)
"""

import argparse
import datetime
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEDGER = os.path.join(ROOT, "infrastructure", "state", "ledger", "events.jsonl")
ITEMS = os.path.join(ROOT, "infrastructure", "state", "items")
BRIDGE = os.path.join(ROOT, "infrastructure", "state", "BRIDGE")

TODO = "<<< WRITE THIS >>>"

# The sections a script cannot produce. Each is a real question the next seat
# will ask on wake, in the order they will ask it.
JUDGEMENT_SECTIONS = [
    ("The one thing to carry forward",
     "The single most important thing learned. Not a list — the thing that would "
     "cost the next seat hours if it had to rediscover it. If nothing qualifies, "
     "write 'nothing this wave' and mean it."),
    ("What the owner should see",
     "Findings that need HIS eye or HIS decision: a number nobody ruled on, a "
     "mod that vanished from his list, a change he can veto. Say what you shipped "
     "deliberately with a flag raised. Empty is a legitimate answer."),
    ("What is half-done, and where it stops",
     "Anything left mid-flight, and the exact next action. An item in `doing` "
     "with no line here is a trap for the next seat."),
    ("Traps learned",
     "Instruments that lied, silent failures, commands that ate their own input. "
     "Also file these to LESSONS_INBOX.md."),
]


def sh(*args, **kw):
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                              timeout=kw.get("timeout", 60)).stdout.strip()
    except Exception as e:
        return "<could not run %s: %s>" % (args[0], e)


def seat():
    for v in (os.environ.get("RIMFLOW_SEAT"), os.environ.get("AGENT_SEAT")):
        if v:
            return v.strip().upper()
    out = sh("python3", os.path.join(ROOT, "src", "RimMandrake", "rimflow", "cli.py"),
             "seat", "ready")
    m = re.match(r"^([A-Z]+) is ready", out or "")
    return m.group(1) if m else "FOUNDRY"


def events():
    if not os.path.isfile(LEDGER):
        return []
    out = []
    with io.open(LEDGER, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def handoff_files():
    """Every handoff for this seat, unordered — ordering is never by name here."""
    s = seat()
    if not os.path.isdir(ITEMS):
        return []
    return [fn for fn in os.listdir(ITEMS)
            if fn.startswith(s + "_REBOOT_HANDOFF_") and fn.endswith(".md")]


def previous_handoff():
    """(path, iso-timestamp) of the newest handoff for this seat, or (None, None).

    Timestamp comes from git, not the filesystem: a shared worktree gets touched
    by other seats and mtime is not evidence about when this was written.
    """
    # ⚠️ Newest by COMMIT TIME, not by filename and not by mtime.
    #   * Not the newest on disk: the handoff being written right now is
    #     uncommitted and would select itself, making the window start "now" —
    #     which silently disabled the doing-scope and listed 47 stale items.
    #   * Not alphabetical: this repo has BOTH naming schemes in flight,
    #     `..._20260906C` and `..._202609062326`, and digits sort before letters,
    #     so the newest file sorted THIRD. Filenames are not a clock.
    best = (None, None)
    for fn in handoff_files():
        rel = os.path.join("infrastructure", "state", "items", fn)
        ts = sh("git", "log", "-1", "--format=%cI", "--", rel)
        if ts and (best[1] is None or ts > best[1]):
            best = (fn, ts)
    return best


def open_this_window(since_ts):
    """Items this seat started in the window and has not closed."""
    ev = events()
    closed = {e.get("id") for e in ev
              if e.get("event") in ("close", "block", "drop", "supersede")}
    return sorted({e["id"] for e in ev
                   if e.get("event") == "start" and e.get("seat") == seat()
                   and (since_ts is None or (e.get("ts") or "") > since_ts)
                   and e.get("id") not in closed})


def gates(since_ts=None, handoff_path=None, doing_is_fatal=True):
    """Everything that must be true before a reboot is safe. Returns [problems].

    ⚠️ `since_ts` scopes the `doing` check to THIS window, and that scoping is
    load-bearing. Without it the check named all 47 items this seat has ever
    started and not closed — standing loops, parked builds, work three sessions
    old — which is a gate that fires every time and is therefore ignored every
    time. A handoff is answerable for what IT left half-done, not for the whole
    backlog; the previous handoff already owns the rest.
    """
    bad = []

    unpushed = sh("git", "log", "--oneline", "@{u}..HEAD")
    if unpushed:
        bad.append("UNPUSHED commits — committed-but-unpushed survives exactly one "
                   "disk:\n      " + unpushed.replace("\n", "\n      "))

    who = sh("python3", os.path.join(ROOT, "src", "RimMandrake", "rimflow", "cli.py"),
             "bridge", "who")
    if seat() in who and "FREE" not in who.upper():
        bad.append("BRIDGE still held by %s — release it before rebooting:\n      %s"
                   % (seat(), who.splitlines()[0] if who else "?"))

    open_doing = open_this_window(since_ts)

    # Being named in the handoff DISCHARGES the obligation. The rule is "close it,
    # block it, or account for it" — not "close it": some work is legitimately
    # left mid-flight, and a gate that cannot be satisfied by writing the truth
    # teaches the seat to pass --force instead, which is worse than no gate.
    if open_doing and handoff_path and os.path.isfile(handoff_path):
        text = io.open(handoff_path, encoding="utf-8").read()
        open_doing = [i for i in open_doing if i not in text]

    # ⚠️ In WRITE mode this must not refuse. The only way to discharge it is to
    # write the item into 'What is half-done' — in a file that does not exist yet.
    # A gate that blocks you from creating the thing that satisfies it teaches you
    # to reach for --force, so write mode pre-fills the list into that section
    # instead and only --check treats it as fatal.
    if open_doing and doing_is_fatal:
        bad.append("started THIS window and still open — close, block, or write each "
                   "into 'What is half-done':\n      %s" % ", ".join(open_doing))

    return bad


def window_is_empty(since_sha, since_ts):
    """True when NOTHING has happened since the last committed handoff.

    Owner, 2026-09-06: *"...and then NOT do so again unless new work does come
    in."* Saying HANDOFF READY is a signal, and a signal repeated on every idle
    turn stops being one. So the steady state after a handoff is silence: this
    returns True when there are no closes, no filings and no commits in the
    window, and both modes then refuse to write a second handoff saying the same
    nothing.

    Deliberately counts WORK, not turns. A seat that spent an hour reading and
    concluded correctly has still added nothing a next seat must be told.
    """
    if since_ts is None:
        return False
    ev = events()
    moved = [e for e in ev
             if (e.get("ts") or "") > since_ts
             and e.get("event") in ("close", "file", "block", "drop", "supersede")]
    commits = sh("git", "log", "--oneline", "%s..HEAD" % since_sha) if since_sha else ""
    return not moved and not commits


def todo_scan(path):
    if not os.path.isfile(path):
        return ["the handoff file does not exist yet — run without --check first"]
    text = io.open(path, encoding="utf-8").read()
    n = text.count(TODO)
    return ["%d unfilled section(s) still carry %s" % (n, TODO)] if n else []


def build(since_sha, since_ts, prev_name):
    ev = events()
    s = seat()

    def after(e):
        return since_ts is None or (e.get("ts") or "") > since_ts

    closes = [e for e in ev if e.get("event") == "close" and e.get("seat") == s and after(e)]
    files_ = [e for e in ev if e.get("event") == "file" and after(e)
              and (e.get("for") == s or e.get("seat") == s)]
    still_open = {e.get("id") for e in ev if e.get("event") == "file"} - \
                 {e.get("id") for e in ev
                  if e.get("event") in ("close", "drop", "supersede")}

    rng = ("%s..HEAD" % since_sha) if since_sha else "-30"
    commits = sh("git", "log", "--oneline", "--format=%h %s", rng)

    dirty = [l for l in sh("git", "status", "--short").splitlines()
             if l and not l.startswith("?? Transient/")]

    game = sh(os.path.join(ROOT, "game"))
    bridge = ""
    if os.path.isfile(BRIDGE):
        bridge = [l for l in io.open(BRIDGE, encoding="utf-8").read().splitlines()
                  if l and not l.startswith("#")]
        bridge = bridge[-1] if bridge else ""

    stamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    out = os.path.join(ITEMS, "%s_REBOOT_HANDOFF_%s.md" % (s, stamp))

    L = []
    L.append("# %s_REBOOT_HANDOFF_%s — READ FIRST on wake" % (s, stamp))
    L.append("")
    if prev_name:
        L.append("Follows `%s`. Everything below is committed and pushed unless a"
                 % prev_name[:-3])
        L.append("line says otherwise. **Game and bridge state is the last section —"
                 " read it")
        L.append("before touching the game.**")
    else:
        L.append("First handoff for this seat. Everything below is committed and pushed.")
    L.append("")

    open_doing = open_this_window(since_ts)
    for title, prompt in JUDGEMENT_SECTIONS:
        L.append("## %s" % title)
        L.append("")
        L.append("<!-- %s -->" % prompt)
        if title.startswith("What is half-done") and open_doing:
            L.append("<!-- These are the items you started this window and did not")
            L.append("     close. Say what state each is in and the exact next action,")
            L.append("     or close/block it. --check refuses while any is unaccounted")
            L.append("     for, so deleting a line here is not a way past it. -->")
            for i in open_doing:
                L.append("- `%s` — %s" % (i, TODO))
            L.append("")
        else:
            L.append(TODO)
            L.append("")

    L.append("## Closed since the last handoff (%d)" % len(closes))
    L.append("")
    if closes:
        for e in closes:
            L.append("- `%s` — %s" % (e.get("id"), e.get("sha") or "no sha"))
    else:
        L.append("Nothing closed in this window.")
    L.append("")

    ready = [e for e in files_ if e.get("id") in still_open]
    L.append("## Filed and still open (%d) — the next seat's queue" % len(ready))
    L.append("")
    if ready:
        for e in ready:
            L.append("- `%s` — %s" % (e.get("id"), (e.get("title") or "")[:150]))
    else:
        L.append("Nothing filed in this window.")
    L.append("")

    L.append("## Commits")
    L.append("")
    L.append("```")
    L.append(commits or "(none)")
    L.append("```")
    L.append("")

    L.append("## Game / bridge / tree state at wrap")
    L.append("")
    for line in (game or "").splitlines():
        L.append("- %s" % line.strip())
    L.append("- Bridge: %s" % (bridge or "unknown"))
    L.append("")
    if dirty:
        L.append("Uncommitted (say for each whether it is yours or another seat's):")
        L.append("")
        L.append("```")
        L.extend(dirty)
        L.append("```")
    else:
        L.append("Working tree clean apart from untracked `Transient/`.")
    L.append("")

    io.open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--check", action="store_true",
                    help="gates + unfilled-section scan only; exit 1 if not ready")
    ap.add_argument("--since", help="commit to measure the window from")
    ap.add_argument("--force", action="store_true",
                    help="write the skeleton even if a gate fails")
    a = ap.parse_args()

    s = seat()
    prev_name, prev_ts = previous_handoff()
    since_sha = a.since
    if not since_sha and prev_name:
        p = os.path.join("infrastructure", "state", "items", prev_name)
        since_sha = sh("git", "log", "-1", "--format=%h", "--", p) or None

    # --check validates the handoff THIS session wrote, which is the most recently
    # touched one — again not the alphabetically last, for the same reason.
    cands = [os.path.join(ITEMS, fn) for fn in handoff_files()]
    newest = max(cands, key=os.path.getmtime) if cands else None

    if prev_name and window_is_empty(since_sha, prev_ts) and not a.force:
        print("ALREADY HANDED OFF — nothing has closed, been filed or been "
              "committed since\n  %s"
              % os.path.join("infrastructure", "state", "items", prev_name))
        print("\nThat handoff still stands. Do NOT write another and do NOT say "
              "HANDOFF READY again;\nsay it once, then stay quiet until real work "
              "comes in. --force overrides.")
        return 0

    problems = gates(prev_ts, newest if a.check else None,
                     doing_is_fatal=a.check)

    if a.check:
        problems += todo_scan(newest) if newest else ["no handoff file written yet"]
        if problems:
            print("NOT READY — %d thing(s) to fix:" % len(problems))
            for p in problems:
                print("  * %s" % p)
            print("\nFix these, then say HANDOFF READY yourself. This script never "
                  "says it for you.")
            return 1
        print("gates pass and no unfilled sections remain in\n  %s" % newest)
        print("\nThe judgement is yours: if this wave really is a clean stopping "
              "point, say HANDOFF READY.")
        return 0

    if problems and not a.force:
        print("REFUSED — the seat is not safe to reboot yet:")
        for p in problems:
            print("  * %s" % p)
        print("\n--force writes the skeleton anyway (and records these as open).")
        return 1

    out = build(since_sha, prev_ts, prev_name)
    print("wrote %s" % os.path.relpath(out, ROOT))
    print("\nFill these in — a script cannot:")
    for title, prompt in JUDGEMENT_SECTIONS:
        print("  %-38s %s" % (title, prompt.split(".")[0] + "."))
    print("\nThen: handoff.py --check, commit, push, and say HANDOFF READY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
