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
    handoff.py --check        gates + content scan; exit 1 if not ready
    handoff.py --wake         the READ side: latest handoff + live pointer status
    handoff.py --harvest      lesson sections since the last drain -> Transient/
    handoff.py --cull [--apply]  superseded+harvested handoffs older than 30 days
    handoff.py --since <sha>  window start override (default: the last handoff)

The content checks and the wake/harvest/cull modes are audit-driven (2026-09-17,
three-arm audit in `Transient/handoff_audit/`): measured pointer pickup was ~25%
overall and near-100% for pointers with a concrete `NEXT:` action; 7 of 11 recent
handoffs shipped an unattributed dirty-tree dump `--check` could not see; and 43
of 171 lesson-claims were stranded in handoffs no durable doc ever received.
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
WHOSE = "<<< WHOSE? >>>"
CULL_DAYS = 30  # owner ruling 2026-09-18: superseded + harvest-covered + older

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
     "Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one "
     "imperative action>`. A pointer without a ledger item id does not survive a "
     "seat change, and a pointer without a NEXT: measured ~0% pickup. An item in "
     "`doing` with no line here is a trap for the next seat."),
    ("Traps learned",
     "Instruments that lied, silent failures, commands that ate their own input. "
     "ONE line each, ending with where it now lives -- file it to "
     "LESSONS_INBOX.md the moment it is learned, then cite `(filed: "
     "LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is "
     "already recorded somewhere durable."),
]

# --check verifies these headings exist (prefix match; the mechanical ones carry
# counts in their titles). A hand-written handoff with its own headers used to
# pass --check trivially because it contained no TODO marker (measured
# 2026-09-17, BENCH_REBOOT_HANDOFF_202609132330.md): the template is the contract.
CANONICAL_HEADINGS = [t for t, _ in JUDGEMENT_SECTIONS] + [
    "Closed since the last handoff",
    "Filed and still open",
    "Commits",
    "Game / bridge / tree state at wrap",
]


def sh(*args, **kw):
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                              timeout=kw.get("timeout", 60)).stdout.strip()
    except Exception as e:
        return "<could not run %s: %s>" % (args[0], e)


def seat():
    """Which seat is rebooting. REFUSES rather than guessing.

    🔴 Fixed 2026-09-16, observed live from a MACBENCH session: this used to
    `return "FOUNDRY"` whenever nothing identified the seat. On a machine with no
    Windows Terminal seat profile (the Mac laptop) `AGENT_SEAT` is unset AND
    `rimflow seat ready` REFUSES, so the regex never matched and **every handoff
    written there was filed as FOUNDRY's** — this window's reboot produced a
    `FOUNDRY_REBOOT_HANDOFF_*` listing FOUNDRY's six in-flight items as its own
    unfinished work, and told the next FOUNDRY window the handoff was about it.

    The seat is written into the handoff's filename, its `follows` link, its
    unclosed-items query and its bridge check, so guessing it wrong is worse than
    writing nothing. This now follows `rimflow`'s own stance verbatim: it cannot
    tell, so it will not guess.
    """
    for v in (os.environ.get("RIMFLOW_SEAT"), os.environ.get("AGENT_SEAT")):
        if v:
            return v.strip().upper()
    out = sh("python3", os.path.join(ROOT, "src", "RimMandrake", "rimflow", "cli.py"),
             "seat", "ready")
    m = re.match(r"^([A-Z]+) is ready", out or "")
    if m:
        return m.group(1)
    raise SystemExit(
        "REFUSED: handoff.py cannot tell which seat is rebooting, and it will not\n"
        "guess. A wrong seat files one seat's reboot under another seat's name, and\n"
        "hands it that seat's unfinished items.\n\n"
        "Fix it with ONE of:\n"
        "    RIMFLOW_SEAT=MACBENCH python3 src/RimMandrake/Utils/handoff.py\n"
        "    export AGENT_SEAT=MACBENCH\n"
        "    ./src/RimMandrake/Utils/set_agent_window.sh MACBENCH   (then reopen the tab)")


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


def handoff_files(all_seats=False):
    """Handoffs on disk, unordered — ordering is never by name here.

    `all_seats` serves --harvest and --cull, which sweep the whole corpus and
    must not require a resolvable seat."""
    if not os.path.isdir(ITEMS):
        return []
    if all_seats:
        return [fn for fn in os.listdir(ITEMS)
                if "_REBOOT_HANDOFF_" in fn and fn.endswith(".md")]
    s = seat()
    return [fn for fn in os.listdir(ITEMS)
            if fn.startswith(s + "_REBOOT_HANDOFF_") and fn.endswith(".md")]


def _to_utc_z(iso_ts):
    """A `%cI`-format git timestamp (local offset, e.g. '...-07:00') rewritten
    to match the ledger's own 'Z'-suffixed UTC format.

    ⚠️ Without this, `since_ts` (sourced from git) and every ledger `ts` it
    gets compared against are two DIFFERENT ISO-8601 representations of a
    moment, and a bare string `>` does not know that '13:07:06Z' (13:07 UTC)
    is actually EARLIER than '06:19:54-07:00' (13:19:54 UTC) - it only sees
    '13' > '06'. Measured live 2026-09-08: this silently pulled
    DROID_ORACLE_VOICE_DESIGN_1 (genuinely started in a PRIOR window, ~13
    minutes before the cutoff) into "started this window", passing the
    doing-gate on a false premise.
    """
    try:
        dt = datetime.datetime.fromisoformat(iso_ts)
    except ValueError:
        return iso_ts
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
    times = _corpus_commit_times()
    for fn in handoff_files():
        ts = times.get(fn)
        if ts and (best[1] is None or ts > best[1]):
            best = (fn, ts)
    return best


def open_this_window(since_ts):
    """Items this seat started in the window and has not closed since.

    ⚠️ "has not closed" means since the item's OWN most recent start, not
    ever. An id blocked back in August and unblocked-and-restarted this
    window is open now — a close/block/drop/supersede from a PRIOR spell
    must not suppress it. Determined from the id's latest lifecycle event
    (start/close/block/drop/supersede) in chronological order, not from
    "does a terminal event exist anywhere in this id's history."
    """
    s = seat()
    last_lifecycle: dict[str, tuple[str, str, str]] = {}
    for e in sorted(events(), key=lambda x: x.get("ts") or ""):
        kind = e.get("event")
        if kind in ("start", "close", "block", "drop", "supersede"):
            last_lifecycle[e.get("id")] = (kind, e.get("ts") or "", e.get("seat"))
    return sorted(id_ for id_, (kind, ts, start_seat) in last_lifecycle.items()
                  if kind == "start" and start_seat == s
                  and (since_ts is None or ts > since_ts))


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
    # 🔴 Exact holder match, not `seat() in who`. `cli.py`'s `_bridge_who` prints
    # "bridge held by <holder> since ...", and a bare substring test means a seat
    # whose name is a substring of another live seat's name (BENCH inside a
    # MACBENCH-held bridge — MACBENCH is a real seat per `seat()`'s own docstring,
    # even though `bridge give` only offers BENCH/FOUNDRY; `bridge take` gates on
    # no such list) would have this seat wrongly told IT holds the bridge and
    # must release something it never took.
    m = re.match(r"^bridge held by (\S+)", who or "")
    if m and m.group(1) == seat():
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


def _section(text, title):
    """Body of `## <title>...` up to the next `## ` heading, or None."""
    m = re.search(r"^## %s.*?$(.*?)(?=^## |\Z)" % re.escape(title), text,
                  re.M | re.S)
    return m.group(1) if m else None


def _bullets(body):
    """Top-level `- ` bullets with their continuation lines folded in — a
    pointer check that only reads a bullet's first line misses a marker that
    wrapped (the line-2-vs-line-3 subject bug, CLAUDE.md 2026-09-17)."""
    out, cur = [], None
    for l in body.splitlines():
        if l.startswith("- "):
            if cur is not None:
                out.append(cur)
            cur = l
        elif cur is not None and l.strip():
            cur += " " + l.strip()
        elif not l.strip():
            # A blank line ends the bullet: trailing prose is not part of it,
            # so a paragraph after the list cannot lend its (filed:)/NEXT:
            # marker to the last bullet (caught by Lodestar's port, 2026-09-18).
            if cur is not None:
                out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    return out


def todo_scan(path):
    """Everything --check demands of the handoff's CONTENT. Each check maps to a
    measured failure mode from the 2026-09-17 audit (Transient/handoff_audit/):
    unfilled markers, off-template files, unattributed dirty-tree dumps, prose
    pointers with no next action, traps re-explained instead of cited."""
    if not os.path.isfile(path):
        return ["the handoff file does not exist yet — run without --check first"]
    text = io.open(path, encoding="utf-8").read()
    bad = []
    n = text.count(TODO)
    if n:
        bad.append("%d unfilled section(s) still carry %s" % (n, TODO))
    n = text.count(WHOSE)
    if n:
        bad.append("%d uncommitted-file line(s) still carry %s — say whose each "
                   "one is" % (n, WHOSE))
    missing = [h for h in CANONICAL_HEADINGS
               if not re.search(r"^## %s" % re.escape(h), text, re.M)]
    if missing:
        bad.append("canonical heading(s) missing — the template is the contract: "
                   + ", ".join(missing))

    # Half-done: a pointer without a concrete next action dies unread —
    # measured ~25% pickup overall, near-100% with a NEXT:.
    body = _section(text, "What is half-done, and where it stops")
    if body:
        loose = [b for b in _bullets(body) if "NEXT:" not in b]
        if loose:
            bad.append("half-done pointer(s) without a `NEXT:` action:\n      "
                       + "\n      ".join(b[:120] for b in loose[:6]))

    # Traps: one line plus where it now lives, never a re-explanation.
    body = _section(text, "Traps learned")
    if body:
        loose = [b for b in _bullets(body)
                 if not re.search(r"\((filed|see):", b)]
        if loose:
            bad.append("trap(s) with no `(filed: ...)`/`(see: ...)` citation — "
                       "file each to LESSONS_INBOX.md (or cite where it already "
                       "lives):\n      " + "\n      ".join(b[:120] for b in loose[:6]))
    return bad


def wake():
    """The READ side of the ritual: print this seat's latest committed handoff
    with each pointer's CURRENT ledger state. Consumption audit 2026-09-17:
    46 of 76 pointers were never consumed — a handoff nobody is obliged to
    read is write-only by construction. Run on the first turn after a reboot."""
    prev_name, _ = previous_handoff()
    if not prev_name:
        print("no committed handoff for %s — nothing to wake from" % seat())
        return 0
    text = io.open(os.path.join(ITEMS, prev_name), encoding="utf-8").read()
    print(text)
    ids = re.findall(r"^- `([A-Z][A-Z0-9_]+)`", text, re.M)
    if ids:
        last = {}
        for e in sorted(events(), key=lambda x: x.get("ts") or ""):
            if e.get("event") in ("file", "start", "close", "block", "drop",
                                  "supersede"):
                last[e.get("id")] = e.get("event")
        print("=" * 66)
        print("POINTER STATUS (ledger, re-derived now — the handoff above is a")
        print("snapshot and may be stale):")
        open_ids = []
        for i in dict.fromkeys(ids):
            st = last.get(i, "not in ledger")
            print("  %-48s %s" % (i, st))
            if st in ("file", "start", "block", "not in ledger"):
                open_ids.append(i)
        print("open pointers: %d — pick each up, close it, or say in your first"
              % len(open_ids))
        print("reply why not. Silence is how 60% of pointers died.")
    return 0


def _corpus_commit_times():
    """{handoff filename: newest commit ts, ledger format} for ALL seats, in
    ONE git call — a per-file `git log` across this 67-file corpus on the
    drvfs mount measures in minutes, not seconds (hit live 2026-09-18)."""
    out = sh("git", "log", "--format=@@%cI", "--name-only", "--",
             "infrastructure/state/items/*_REBOOT_HANDOFF_*.md")
    times, ts = {}, ""
    for line in out.splitlines():
        if line.startswith("@@"):
            ts = _to_utc_z(line[2:].strip())
        elif line.strip():
            fn = os.path.basename(line.strip())
            if fn not in times:  # log is newest-first; first sighting wins
                times[fn] = ts
    return times


def last_drain_ts():
    """Commit time (ledger-format UTC) of the last LESSONS_INBOX drain — the
    newest commit in which the inbox SHRANK (deletions > additions, via one
    `--numstat` walk). Ordinary filing only appends; only a curation drain
    removes lines. None if no drain is on record."""
    out = sh("git", "log", "--format=@@%cI", "--numstat", "--",
             "infrastructure/state/LESSONS_INBOX.md")
    ts = ""
    for line in out.splitlines():
        if line.startswith("@@"):
            ts = line[2:].strip()
        elif line.strip():
            parts = line.split("\t")
            if (len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit()
                    and int(parts[1]) > int(parts[0])):
                return _to_utc_z(ts)
    return None


def harvest(since_ts):
    """Extract every filled 'The one thing to carry forward' + 'Traps learned'
    section from ALL seats' handoffs committed after since_ts into one
    Transient/ file — the pre-chewed input for the curation sitting. The
    2026-09-17 audit found 43 of 171 lesson-claims stranded in handoffs no
    durable doc ever received; this makes the drain a read, not an excavation."""
    if since_ts is None:
        since_ts = last_drain_ts()
    times = _corpus_commit_times()
    rows = []
    for fn in sorted(handoff_files(all_seats=True)):
        ts = times.get(fn, "")
        if since_ts and ts and ts <= since_ts:
            continue
        text = io.open(os.path.join(ITEMS, fn), encoding="utf-8").read()
        secs = []
        for title in ("The one thing to carry forward", "Traps learned"):
            body = _section(text, title)
            if body and TODO not in body and body.strip():
                secs.append("### %s\n\n%s" % (title, body.strip()))
        if secs:
            rows.append("## %s (%s)\n\n%s"
                        % (fn[:-3], ts or "uncommitted", "\n\n".join(secs)))
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d")
    out = os.path.join(ROOT, "Transient", "handoff_harvest_%s.md" % stamp)
    hdr = ("# Handoff harvest %s — lesson sections since %s\n\n"
           "Input for the curation sitting: promote what deserves it into "
           "skills / CLAUDE.md / facts, then this file is disposable "
           "(Transient).\n\n" % (stamp, since_ts or "the beginning"))
    io.open(out, "w", encoding="utf-8").write(hdr + "\n\n".join(rows) + "\n")
    print("wrote %s — %d handoff(s) with lesson content since %s"
          % (os.path.relpath(out, ROOT), len(rows), since_ts or "ever"))
    return 0


def cull(apply_):
    """Handoffs that have served both consumers — superseded by a newer one for
    the same seat AND committed before the last lessons drain — and are older
    than CULL_DAYS. Owner ruling 2026-09-18: delete at 30 days, git is the
    archive. Without --apply this only lists."""
    drain = last_drain_ts()
    now = datetime.datetime.now(datetime.timezone.utc)
    times = _corpus_commit_times()
    newest, info = {}, []
    for fn in handoff_files(all_seats=True):
        ts = times.get(fn, "")
        st = fn.split("_REBOOT_HANDOFF_")[0]
        info.append((fn, st, ts))
        if ts and (st not in newest or ts > newest[st][1]):
            newest[st] = (fn, ts)
    cands = []
    for fn, st, ts in info:
        if not ts or newest.get(st, (None,))[0] == fn:
            continue  # uncommitted, or a seat's latest — never culled
        age = (now - datetime.datetime.fromisoformat(
            ts.replace("Z", "+00:00"))).days
        if age < CULL_DAYS or drain is None or ts >= drain:
            continue  # too young, or not harvest-covered yet
        cands.append((fn, ts, age))
    if not cands:
        print("nothing to cull: no handoff is superseded + harvest-covered + "
              "older than %d days" % CULL_DAYS)
        return 0
    for fn, ts, age in sorted(cands):
        print("%s  (%s, %dd)" % (fn, ts, age))
    if apply_:
        for fn, _, _ in cands:
            os.remove(os.path.join(ITEMS, fn))
        print("deleted %d — commit the deletions with explicit paths; git is "
              "the archive." % len(cands))
    else:
        print("%d candidate(s). `--cull --apply` deletes them." % len(cands))
    return 0


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
            L.append("     close. Say what state each is in and ONE imperative NEXT:")
            L.append("     action, or close/block it. --check refuses while any is")
            L.append("     unaccounted for or lacks a NEXT:, so deleting a line here")
            L.append("     is not a way past it. -->")
            for i in open_doing:
                L.append("- `%s` — %s; NEXT: %s" % (i, TODO, TODO))
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
    # Git is the provenance: past 20 lines a dump stops being read and starts
    # being scrolled (one audited handoff carried 556 commit lines, mostly
    # other seats'). The range pointer reproduces the rest in one command.
    clines = (commits or "(none)").splitlines()
    if len(clines) > 20:
        L.extend(clines[:20])
        L.append("... %d more: git log --oneline %s" % (len(clines) - 20, rng))
    else:
        L.extend(clines)
    L.append("```")
    L.append("")

    L.append("## Game / bridge / tree state at wrap")
    L.append("")
    for line in (game or "").splitlines():
        L.append("- %s" % line.strip())
    L.append("- Bridge: %s" % (bridge or "unknown"))
    L.append("")
    if dirty:
        L.append("Uncommitted (replace each %s with whose it is —" % WHOSE)
        L.append("yours, the other seat's, a subagent's):")
        L.append("")
        L.append("```")
        L.extend("%s   %s" % (l, WHOSE) for l in dirty)
        L.append("```")
    else:
        L.append("Working tree clean apart from untracked `Transient/`.")
    L.append("")

    io.open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--check", action="store_true",
                    help="gates + content scan only; exit 1 if not ready")
    ap.add_argument("--wake", action="store_true",
                    help="print the seat's latest handoff + live pointer status "
                         "— run on the first turn after a reboot")
    ap.add_argument("--harvest", action="store_true",
                    help="extract lesson sections since the last LESSONS_INBOX "
                         "drain into Transient/ for the curation sitting")
    ap.add_argument("--cull", action="store_true",
                    help="list handoffs superseded + harvest-covered + older "
                         "than %d days" % CULL_DAYS)
    ap.add_argument("--apply", action="store_true",
                    help="with --cull: actually delete the candidates")
    ap.add_argument("--since", help="commit to measure the window from")
    ap.add_argument("--force", action="store_true",
                    help="write the skeleton even if a gate fails")
    a = ap.parse_args()

    # Corpus modes first: they sweep all seats and must not demand a
    # resolvable seat identity.
    if a.harvest:
        since_ts = None
        if a.since:
            raw = sh("git", "log", "-1", "--format=%cI", a.since)
            since_ts = _to_utc_z(raw) if raw else a.since
        return harvest(since_ts)
    if a.cull:
        return cull(a.apply)
    if a.wake:
        return wake()

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
