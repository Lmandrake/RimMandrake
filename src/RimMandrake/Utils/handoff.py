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
writes `infrastructure/state/handoffs/<SEAT>_REBOOT_HANDOFF_<stamp>.md` with every
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
signal to reboot, read by .claude/hooks/handoff_restart.py on a seat with a restart;
a script that could emit it would eventually emit it wrongly.

    handoff.py                write the skeleton (gates first, --force to skip)
    handoff.py --check        gates + content scan; exit 1 if not ready
    handoff.py --wake         the READ side: latest handoff + live pointer status + the one-screen
                              ledger state file it regenerates (ledger_state.py)
    handoff.py --harvest      lesson sections since the last drain -> Transient/
    handoff.py --cull [--apply]  handoffs a newer one from the same window replaced 7+ days
                              ago, lessons filed; could-not-tell ones are listed and kept
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
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridge_holder  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEDGER = os.path.join(ROOT, "infrastructure", "state", "ledger", "events.jsonl")
# 🔑 Handoffs are NOT queue items and never were — no ledger entry, no seat
# ownership, nothing greps them for queue state. They lived in items/ only by
# habit, where 82 of them (1.9 MB) sat in the directory doctrine tells agents to
# grep for "what else this settled". Moved out 2026-09-19 on the owner's word.
HANDOFFS = os.path.join(ROOT, "infrastructure", "state", "handoffs")
RIMFLOW = os.path.join(ROOT, "src", "RimMandrake", "rimflow")

TODO = "<<< WRITE THIS >>>"
WHOSE = "<<< WHOSE? >>>"
# Owner, by card 2026-11-18 (RIMMASTER_SETTLE_HANDOFF_CULL_AGE_TWO_RULINGS_DISAGREE): "7 days after replaced
# (Recommended)". Replaces the 2026-09-18 rule (30 days of the handoff's own age).
CULL_DAYS = 7

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
     "`doing` with no line here is a trap for the next seat. The Conductor's "
     "pointers each cite an open owed id too: file the act first (`rimflow file "
     "<ID> --for BENCH --kind owed --caused-by <item>`), then cite it on the line; "
     "--check runs `owed.py check-pointers`."),
    ("Traps learned",
     "Instruments that lied, silent failures, commands that ate their own input. "
     "ONE line each, ending with where it now lives -- file it with "
     "`lessons.py add` the moment it is learned, then cite `(filed: "
     "lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is "
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


def own_hold(who, me):
    """Does this `rimflow bridge who` reading name `me`'s own hold? The holder is compared whole, under the name this
    process holds as: a Relentless process holds as RELENTLESS, and a BENCH hold is the Conductor's."""
    return bridge_holder.held_by(who) == bridge_holder.identity(me)


def _seat_restart():
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake"))
    from rimflow import seat_restart
    return seat_restart


def bridge_lines():
    """-> one line per game of this machine, ArchBig first: who drives it, read from its driver lock (game_lock.query_all,
    the one record), as `game_lock.py query all` prints it. A lock that cannot be read is its game's COULD NOT LOOK line;
    a reader that cannot run is one COULD NOT LOOK line. Never a blank, and never FREE for either."""
    try:
        if RIMFLOW not in sys.path:
            sys.path.insert(0, RIMFLOW)
        import game_lock
        rows = game_lock.query_all()
    except Exception as e:  # noqa: BLE001  (a reader that cannot run is an instrument that cannot see)
        return ["COULD NOT LOOK at the game locks: %s: %s" % (type(e).__name__, e)]
    return [r["line"] for r in rows] or ["COULD NOT LOOK at the game locks: no game on this machine"]


def read_bridge(me):
    """Game a's lock and this shell's driver lock, read as the restart gate reads them (seat_restart.bridge_reading)."""
    return _seat_restart().bridge_reading(me)


def ppid_of(pid):
    return _seat_restart()._proc_ppid(pid)


def window_pid():
    """The Claude window this process runs under: the nearest ancestor with a ~/.claude/sessions/<pid>.json, else None
    (then a holder cannot be placed against the window and the gate refuses, UNMEASURED)."""
    sr, p = _seat_restart(), os.getpid()
    for _ in range(64):
        if p is None or p <= 1:
            return None
        if sr.session_file(p):
            return p
        p = ppid_of(p)
    return None


def bridge_gate(who, me):
    """-> the refusal for a bridge or driver lock held by this seat's WINDOW, or None. Judged by the holder's process
    (seat_restart.bridge_hold, the one copy): a detached run's lock survives the reboot and is no reason to refuse."""
    hold = _seat_restart().bridge_hold(me, read_bridge(me) or {}, window_pid(), ppid_of)
    if not hold:
        return None
    return "BRIDGE still held by %s — release it before rebooting:\n      %s\n      (%s)" % (
        me, who.splitlines()[0] if who else "?", hold)


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
        if v:       # folded as rimflow folds it: RIMFLOW_SEAT=Conductor is BENCH, or every per-seat query reads empty
            return _canonical(v.strip().upper())
    out = sh("python3", os.path.join(ROOT, "src", "RimMandrake", "rimflow", "cli.py"),
             "seat", "ready")
    seat = seat_from_ready(out)
    if seat:
        return seat
    raise SystemExit(
        "REFUSED: handoff.py cannot tell which seat is rebooting, and it will not\n"
        "guess. A wrong seat files one seat's reboot under another seat's name, and\n"
        "hands it that seat's unfinished items.\n\n"
        "Fix it with ONE of:\n"
        "    RIMFLOW_SEAT=MACBENCH python3 src/RimMandrake/Utils/handoff.py\n"
        "    export AGENT_SEAT=MACBENCH\n"
        "    ./src/RimMandrake/Utils/set_agent_window.sh MACBENCH   (then reopen the tab)")


def require_worker_seat(s, env=None):
    """Codex helpers never write the Conductor's handoff, even with --force."""
    env = os.environ if env is None else env
    codex = any(env.get(k) for k in ("CODEX_THREAD_ID", "CODEX_SESSION_ID", "CODEX_CI"))
    codex = codex or (env.get("RIMFLOW_BRIDGE_SEAT") or "").startswith(("CODEX_", "CLAUDE_"))   # a worker loop, Codex or Claude
    if codex and s in ("BENCH", "CONDUCTOR"):
        raise SystemExit("REFUSED: a Codex worker cannot write a BENCH/CONDUCTOR handoff; "
                         "export RIMFLOW_SEAT=CODEX_<MACHINE>_<LANE> using a registered seat.")


def seat_from_ready(out):
    """-> the ledger seat KEY named by `rimflow seat ready`'s first line, or None.

    The Conductor prints by display name with its key in brackets ("CONDUCTOR is ready [seat BENCH]",
    CONDUCTOR_NAME_RENAME_BENCH_STEPS_ASIDE); other seats print "FOUNDRY is ready". The key is what goes into
    the handoff's filename and queries, so the bracket wins, and a bare display name maps back to its key."""
    m = re.match(r"^([A-Z0-9_]+) is ready(?: \[seat ([A-Z0-9_]+)\])?", out or "")
    if not m:
        return None
    return m.group(2) or {"CONDUCTOR": "BENCH"}.get(m.group(1), m.group(1))


def _seat_keys(ev):
    """Fold the on-disk names CONDUCTOR/RELENTLESS back to the seat key BENCH, exactly as `rimflow.model.from_disk`
    (SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP step 2); a `bridge` event's RELENTLESS is the distinct holder."""
    if not isinstance(ev, dict):
        return ev
    verb = ev.get("event")
    fields = ("seat",) + {"file": ("for",), "spawn": ("for",), "reassign": ("to",)}.get(verb, ())
    for f in fields:
        v = ev.get(f)
        if v == "CONDUCTOR" or (v == "RELENTLESS" and not (f == "seat" and verb == "bridge")):
            ev[f] = "BENCH"
    return ev


def events():
    """-> every ledger event, ordered by `ts`.

    🔴 THE LEDGER IS SEVERAL FILES since 2026-09-23: `events.jsonl` is frozen history
    and each seat appends to its own `ledger/events/<SEAT>.jsonl` shard, so two windows
    can never conflict in one git-tracked file (`rimflow.model.SHARD_DIR` is the
    authority). Reading the head alone would hand every handoff a seat's in-flight
    items as they stood at the cutover — stale in exactly the way this script exists to
    prevent.
    """
    shards = os.path.join(os.path.dirname(LEDGER), "events")
    paths = [LEDGER]
    try:
        paths += [os.path.join(shards, n) for n in sorted(os.listdir(shards))
                  if n.endswith(".jsonl")]
    except OSError:
        pass
    out = []
    for p in paths:
        if not os.path.isfile(p):
            continue
        with io.open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(_seat_keys(json.loads(line)))
                    except ValueError:
                        pass
    # Stable sort, so each file's own append order survives a same-second tie.
    out.sort(key=lambda e: str(e.get("ts") or ""))
    return out


def handoff_files(all_seats=False):
    """Handoffs on disk, unordered — ordering is never by name here.

    `all_seats` serves --harvest and --cull, which sweep the whole corpus and
    must not require a resolvable seat."""
    if not os.path.isdir(HANDOFFS):
        return []
    # Both spellings: the Lodestar `handoff` skill writes <SEAT>_HANDOFF_<stamp>,
    # this tool <SEAT>_REBOOT_HANDOFF_<stamp>. Matching only one made --wake
    # print a day-old handoff while a newer one sat beside it (2026-10-07).
    names = [fn for fn in os.listdir(HANDOFFS)
             if _HANDOFF_RE.match(fn) and fn.endswith(".md")]
    if all_seats:
        return names
    s = _canonical(seat())
    return [fn for fn in names if _canonical(_HANDOFF_RE.match(fn).group(1)) == s]


def _canonical(name):
    """The ledger seat key: the handoff skill writes CONDUCTOR_HANDOFF_*, this tool BENCH_REBOOT_HANDOFF_*, and both are
    one seat (model.SEAT_ALIAS). Matching the raw name hid CONDUCTOR_HANDOFF_202611110123 from a BENCH wake (review,
    2026-11-11)."""
    try:
        import ledger_state
        return ledger_state.model.canonical(name)
    except Exception:       # noqa: BLE001  the alias table unreadable: the one alias it holds today
        return {"CONDUCTOR": "BENCH"}.get(name, name)


_HANDOFF_RE = re.compile(r"^(.+?)_(?:REBOOT_)?HANDOFF_\d")


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


def _replay():
    """The ledger's own state machine over the ledger in use (model.replay): the only reader of an item's state."""
    import ledger_state
    ledger_state.ledger_head()
    return ledger_state.model.replay(ledger_state.model.read())


def open_this_window(since_ts, world=None):
    """Items this seat started in the window that are still `doing`, unblocked, now.

    ⚠️ "Still doing" is model.replay's answer, never the id's last lifecycle verb. An id blocked back in August and
    unblocked-and-restarted this window is open now; an id finished by `implemented` + `verify --result pass` has no
    `close` and is done; one unblocked with no fresh `start` is doing again. The last-verb reader listed 63 done items
    of 146 in a BENCH window since 2026-11-01 as still open (review, 2026-11-11).
    """
    s = seat()
    started = {e.get("id") for e in events()
               if e.get("event") == "start" and e.get("seat") == s and (since_ts is None or (e.get("ts") or "") > since_ts)}
    items = (world if world is not None else _replay()).items
    return sorted(i for i in started if i in items and items[i].state == "doing" and not items[i].blocked)


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

    # `git cherry` marks a commit `-` when origin already holds a patch-equivalent
    # (a rebase rewrites shas), so only `+` is truly unpushed.
    # A failed `git cherry` (no upstream, git error) used to read as "nothing unpushed".
    try:
        ch = subprocess.run(["git", "cherry", "@{u}", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True, timeout=60)
        ch_ok, ch_out, ch_err = ch.returncode == 0, ch.stdout.strip(), ch.stderr.strip()
    except Exception as e:
        ch_ok, ch_out, ch_err = False, "", str(e)
    if not ch_ok:
        bad.append("CANNOT TELL what is unpushed (git cherry failed: %s) — no upstream "
                   "is not the same as nothing unpushed" % (ch_err.splitlines()[-1] if ch_err else "?"))
    unpushed = "\n".join(
        sh("git", "log", "--oneline", "-1", ln[2:].strip())
        for ln in ch_out.splitlines()
        if ln.startswith("+"))
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
    refusal = bridge_gate(who, seat())
    if refusal:
        bad.append(refusal)

    open_doing = open_this_window(since_ts)

    # Being named in the handoff DISCHARGES the obligation. The rule is "close it,
    # block it, or account for it" — not "close it": some work is legitimately
    # left mid-flight, and a gate that cannot be satisfied by writing the truth
    # teaches the seat to pass --force instead, which is worse than no gate.
    # Only its own half-done pointer with a NEXT: discharges it: a mention anywhere (the auto-listed queue, a longer id)
    # did, and let a deleted pointer pass (Codex, 2026-11-18; RIMMANDRAKE_HARDEN_HANDOFF_CHECK_FOUR_HOLES_CODEX_FOUND).
    if open_doing and handoff_path and os.path.isfile(handoff_path):
        named = accounted_ids(io.open(handoff_path, encoding="utf-8").read())
        open_doing = [i for i in open_doing if i not in named]

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
             and e.get("event") in ("close", "file", "block", "drop", "supersede", "implemented", "verify")]
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


_EXACT_ID = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]+(?![A-Za-z0-9_])")


def accounted_ids(text):
    """-> {item id} named, whole, on a half-done bullet that holds a NEXT: (the only way an open `doing` item is
    accounted for)."""
    body = _section(text, "What is half-done, and where it stops") or ""
    out = set()
    for b in _bullets(body):
        if "NEXT:" in b:
            out.update(_EXACT_ID.findall(b))
    return out


# hole 2: a git status that failed is UNMEASURED, never a clean tree
TREE_UNMEASURED = ("Tree state UNMEASURED: `git status --short` failed when this was written; run it, list what is "
                   "uncommitted and whose, then delete this line.")


def tree_lines(run=subprocess.run):
    """-> the uncommitted paths (`git status --short`, untracked Transient/ apart), or None when git could not say."""
    try:
        r = run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, timeout=60)
    except Exception:  # noqa: BLE001 - could not run: UNMEASURED
        return None
    if r is None or r.returncode != 0:
        return None
    return [l for l in (r.stdout or "").splitlines() if l and not l.startswith("?? Transient/")]


def window_start(since_sha, prev_ts):
    """-> the ledger window's start: the --since commit's own time when one is given, else the previous handoff's.
    `--since` used to move only the commit range, and items started between it and the previous handoff escaped the
    doing gate. An unreadable --since commit -> None (no window: every open item answers, never fewer)."""
    if not since_sha:
        return prev_ts
    raw = sh("git", "log", "-1", "--format=%cI", since_sha)
    return _to_utc_z(raw) if raw and not raw.startswith("<could not run") else None


def handoff_out(seat_, d, stamp=None):
    """-> a skeleton path that names no file already there: a second write in the same minute replaced a filled handoff
    with a fresh skeleton (the name was minute-precision and opened with "w")."""
    stamp = stamp or datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    cands = [stamp, stamp + datetime.datetime.utcnow().strftime("%S")]
    cands += ["%s%02d" % (cands[1], k) for k in range(1, 100)]
    for st in cands:
        out = os.path.join(d, "%s_REBOOT_HANDOFF_%s.md" % (seat_, st))
        if not os.path.exists(out):
            return out
    return None


FILED_CITE = re.compile(r"\(filed:([^)]*)\)", re.I)
ITEM_SHAPE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")


def filed_citation_problems(text, items=None):
    """A `(filed: X)` whose X is shaped like an item id must name an item on the ledger: the Conductor's window cited
    ids it had never filed and --check passed them (reported 2026-11-19, RIMMANDRAKE_FIX_FOUR_SMALL_DEFECTS_FOUND_AT_
    TODAYS_WAKE). Only whole words of the citation count (`lessons`, a lesson path or `CANONICAL_SAVE.md` are not ids),
    and the ledger is read only when one is cited. `items`: a set of ids, or a callable returning one (the seam); default
    model.replay's items. A ledger that cannot be read is 'could not look', never a pass and never 'not an item'."""
    cited = []
    for m in FILED_CITE.finditer(text):
        for w in re.split(r"[\s,;]+", m.group(1)):
            w = w.strip("`*'\".")
            if ITEM_SHAPE.match(w) and w not in cited:
                cited.append(w)
    if not cited:
        return []
    try:
        known = items() if callable(items) else items if items is not None else set(_replay().items)
    except Exception as e:                       # noqa: BLE001 - said, never silent
        return ["could not look up %d `(filed: X)` id(s) on the ledger (%s: %s): %s"
                % (len(cited), type(e).__name__, e, ", ".join(cited))]
    ghosts = [c for c in cited if c not in known]
    if ghosts:
        return ["`(filed: X)` citation(s) whose X is not an item on the ledger -- file it (`rimflow file`) or cite where "
                "it really lives: " + ", ".join(ghosts)]
    return []


def todo_scan(path, items=None):
    """Everything --check demands of the handoff's CONTENT. Each check maps to a
    measured failure mode from the 2026-09-17 audit (Transient/handoff_audit/):
    unfilled markers, off-template files, unattributed dirty-tree dumps, prose
    pointers with no next action, traps re-explained instead of cited, and a
    `(filed: X)` naming an item id the ledger does not hold (`items`: the seam)."""
    if not os.path.isfile(path):
        return ["the handoff file does not exist yet — run without --check first"]
    text = io.open(path, encoding="utf-8").read()
    bad = []
    n = text.count(TODO)
    if n:
        bad.append("%d unfilled section(s) still carry %s" % (n, TODO))
    if TREE_UNMEASURED in text:
        bad.append("the tree state is UNMEASURED (git status failed when the skeleton was written): run `git status "
                   "--short`, list what is uncommitted and whose, and delete that line")
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
                       + "\n      ".join(b for b in loose[:6]))

    # Traps: one line plus where it now lives, never a re-explanation.
    body = _section(text, "Traps learned")
    if body:
        loose = [b for b in _bullets(body)
                 if not re.search(r"\((filed|see):", b)]
        if loose:
            bad.append("trap(s) with no `(filed: ...)`/`(see: ...)` citation — "
                       "file each with lessons.py add (or cite where it already "
                       "lives):\n      " + "\n      ".join(b for b in loose[:6]))
    bad += filed_citation_problems(text, items)
    return bad


def show_last_reply():
    """The Conductor's fresh window puts the dead window's last reply back on his empty screen. Here, because every wake
    prompt runs this command, including the one frozen into the Windows Terminal profile, and no other seat prints
    anything (seat_restart.py last-reply, CONDUCTOR_RESET_FIX_KILLED_MID_READ)."""
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "src", "RimMandrake", "rimflow", "seat_restart.py"),
                            "last-reply", "--seat", seat()], cwd=ROOT, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        print("\n== the old window's LAST REPLY: UNMEASURED (%r). Say so to him in one line." % e)
        return
    if r.returncode:
        print("\n== the old window's LAST REPLY: UNMEASURED (exit %d: %s). Say so to him in one line."
              % (r.returncode, (r.stderr or "").strip()))
    elif r.stdout.strip():
        print(r.stdout.rstrip() + "\n")


def owed_pointer_problems(path):
    """--check's E4 gate (RIMMANDRAKE_REFUSE_HANDOFF_POINTER_WITHOUT_OWED_ID): the Conductor's pointers each cite an open
    owed id, so a pointer whose item closes still points at a live debt. Runs `owed.py check-pointers`, a validator that
    writes nothing; only the Conductor's seat owes (show_owed). A check that could not look is a problem, never a pass."""
    if seat() != "BENCH":
        return []
    cmd = [sys.executable, os.path.join(ROOT, "src", "RimMandrake", "rimflow", "owed.py"), "check-pointers", path]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
    except Exception as e:                       # noqa: BLE001 - said, never silent
        return ["owed.py check-pointers did not run (%s: %s)" % (type(e).__name__, e)]
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        return []
    if r.returncode == 1:
        return ["pointer(s) citing no open owed id, or a closed one (owed.py check-pointers):\n      "
                + "\n      ".join(out.splitlines()[:24])]
    return ["owed.py check-pointers could not look (exit %d): %s" % (r.returncode, out[-400:] or "no output")]  # cut-ok: terminal display


def show_owed():
    """The Conductor's owed view, right after the old window's last reply: `rimflow queue CONDUCTOR --owed`
    (rimflow/owed.py; RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE). Only the Conductor's seat owes; a view that
    cannot run says so and the wake goes on."""
    if seat() != "BENCH":
        return
    try:
        sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
        import owed
        print("\n".join(owed.wake_lines(ROOT)) + "\n")
    except Exception as e:                       # noqa: BLE001 - said, never silent
        print("\n== OWED view did not run (%r): run `rimflow queue CONDUCTOR --owed` yourself\n" % e)


# A section is kept by what its heading says, not by its exact words: "## Half-done" and "## Game and bridge state" are
# real headings in the corpus that an exact-prefix match dropped (review, 2026-11-11). "Tree state" alone is git's.
WAKE_KEEP = re.compile(r"carry forward|owner should see|half-done|\bgame\b|\bbridge\b", re.I)
GAME = re.compile(r"\bgame\b|\bbridge\b", re.I)


def _sections(text):
    """[[heading, lines]] split on `## ` lines outside a ``` fence (a `## ` inside one is text); the first heading is None."""
    out, fence = [[None, []]], False
    for ln in text.splitlines():
        if ln.lstrip().startswith("```"):
            fence = not fence
        if not fence and ln.startswith("## "):
            out.append([ln, []])
        else:
            out[-1][1].append(ln)
    return out


def _wake_view(text, path):
    """What --wake prints (HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT): the title, the one thing to carry, what the owner
    should see, the pointer lines and the game/bridge state; then the file's full path and the headings left out of the
    view (traps, closed/filed lists, commits, the uncommitted list, anything else). The handoff file itself stays whole."""
    # the template's <!-- guidance --> comments are for the writer, not the reader of a wake
    text = re.sub(r"[ \t]*<!--.*?-->[ \t]*\n?", "", text, flags=re.S)
    out, left = [], []
    for head, body in _sections(text):
        if head is None:
            out.append("\n".join(body).strip())
            continue
        if not WAKE_KEEP.search(head):
            left.append(head[3:].strip())
            continue
        if GAME.search(head):       # the game section ends in the uncommitted list: git's job, not the wake's
            cut = next((k for k, ln in enumerate(body) if re.match(r"Uncommitted\b", ln)), None)
            if cut is not None:
                body = body[:cut]
                left.append("the uncommitted list")
        out.append((head + "\n" + "\n".join(body)).rstrip())
    out.append("(Left out of this view, in the full handoff %s: %s)" % (path, "; ".join(left) or "nothing"))
    return "\n\n".join(x for x in out if x) + "\n"


def pointer_states(world):
    """{item id: (state, blocked)} as the ledger's own state machine has it (model.replay), never a last-verb guess: a
    `live --result broken` or failed `verify` after a close reopens an item, `implemented` plus a `verify` pass ends one
    with no close, and `unblock` lifts a block. A last-verb reader called 132 open items CLOSED and 744 done ones open on
    the live ledger (review, 2026-11-11)."""
    return dict(world.items)


def _successor(items, it):
    """'; work its successor X' for a superseded item, following the chain to its end: A -> B -> C with C open is C (one
    link said "B is SUPERSEDED too, do NOT act" over live work, review 2026-11-11). '' when it has no successor."""
    chain, cur = [], it
    while cur is not None and cur.superseded_by and cur.superseded_by not in chain and len(chain) < 20:
        chain.append(cur.superseded_by)
        cur = items.get(cur.superseded_by)
    if not chain:
        return ""
    end, via = chain[-1], (" (via %s)" % ", ".join(chain[:-1]) if len(chain) > 1 else "")
    if cur is None:
        return "; its successor %s%s is not in the ledger" % (end, via)
    if cur.state in TERMINAL:
        return "; its successor %s%s is %s too" % (end, via, cur.state.upper())
    return "; work its successor %s%s" % (end, via)


def pointer_ids(text):
    """Item ids a handoff points at: `- `ID`` (backticked) or `- ID -- state` / `- ID — state` (the template's own
    form, `- ITEM_ID -- state; NEXT:`). The backtick-only reader missed five of six pointers on 2026-11-11."""
    ids = re.findall(r"^- `([A-Z][A-Z0-9_]+)`", text, re.M)
    ids += re.findall(r"^- ([A-Z][A-Z0-9_]+) (?:--|\u2014|\u2013) ", text, re.M)
    return list(dict.fromkeys(ids))


def wake():
    """The READ side of the ritual: print this seat's latest committed handoff
    with each pointer's CURRENT ledger state. Consumption audit 2026-09-17:
    46 of 76 pointers were never consumed — a handoff nobody is obliged to
    read is write-only by construction. Run on the first turn after a reboot."""
    from account_stop_notice import hard_stop_reason
    reason = hard_stop_reason()
    if reason:
        print("Account status: " + reason)
    show_last_reply()
    show_owed()
    prev_name, prev_ts = previous_handoff()
    if not prev_name:
        print("no committed handoff for %s — nothing to wake from" % seat())
        print(ledger_state_line(pointers=False))
        return 0
    text = io.open(os.path.join(HANDOFFS, prev_name), encoding="utf-8").read()
    view = _wake_view(text, os.path.join(HANDOFFS, prev_name))
    print(view)
    # pointers are the ids in what was printed: the hidden closed and filed lists made every filed item, another seat's
    # included, an "open pointer — pick each up" that the reader could not see (review, 2026-11-11)
    ids = pointer_ids(view)
    if ids:
        print("=" * 66)
        try:
            import ledger_state
            ledger_state.ledger_head()
            last = pointer_states(ledger_state.model.replay(ledger_state.model.read()))
            evs = events()
        except Exception as e:      # noqa: BLE001  a wake must still print; an unread ledger says so
            print("POINTER STATUS: UNMEASURED (%s). Read each with rimflow show <ID>: %s" % (e, ", ".join(ids)))
            print(ledger_state_line())
            return 0
        print("POINTER STATUS (ledger, re-derived now — the handoff above is a")
        print("snapshot and may be stale; %s):" % handoff_age(prev_ts))
        open_ids, me = [], _canonical(seat())
        for i in dict.fromkeys(ids):
            it = last.get(i)
            if it is not None and it.state in TERMINAL:
                after = _successor(last, it)
                print("  %-48s %s  *** CLOSED -- do NOT act on this pointer%s ***" % (i, it.state.upper(), after))
                continue
            whose = "" if it is None or _canonical(it.owner or me) == me else ", %s's" % it.owner
            print("  %-48s %s" % (i, "not in ledger" if it is None else
                                  "open (%s%s%s)" % (it.state, ", BLOCKED" if it.blocked else "", whose)))
            moved = since_handoff(evs, i, prev_ts)
            if moved:
                print("      " + moved)
            open_ids.append(i)
        print("open pointers: %d — pick each up, close it, or say in your first"
              % len(open_ids))
        print("reply why not. Silence is how 60% of pointers died.")
    print(ledger_state_line())
    return 0


TERMINAL = ("done", "dropped", "superseded")     # model.TERMINAL; a pointer at one of these is not work
QUIET = ("lease", "renew", "claim", "start")    # keep a claim alive; they say nothing new about the work


def handoff_age(ts):
    """'written <Pacific time>, <N> h before this wake' from the handoff's commit stamp; its NEXTs age with it."""
    try:
        import ledger_state
        e = ledger_state.model.epoch(ts)
        return "written %s, %.1f h before this wake" % (ledger_state.local(ts), (time.time() - e) / 3600.0)
    except Exception:       # noqa: BLE001
        return "written at an UNMEASURED time"


def since_handoff(evs, iid, ts):
    """One line: what the ledger recorded on an open pointer after the handoff was committed (its newest note first),
    or "" when nothing did. An open pointer whose work a later note reports done read as live work to a fresh
    window: COMPARE_ARTISAN_WHITTLE's "spawn a helper" NEXT, with "Comparison written" landed after it."""
    later = [e for e in evs if (e.get("id") or e.get("name")) == iid and str(e.get("ts") or "") > str(ts or "")
             and e.get("event") not in QUIET]
    if not later:
        return ""
    notes = [e for e in later if e.get("event") == "note"]
    out = "since the handoff: %d ledger event%s" % (len(later), "" if len(later) == 1 else "s")
    if notes:
        n = notes[-1]
        try:
            import ledger_state
            when, said = ledger_state.local(n.get("ts"))[5:16], ledger_state.clip(n.get("text"), 90)
        except Exception:       # noqa: BLE001  the note still shows, in the ledger's own UTC stamp
            when, said = str(n.get("ts") or "?") + " UTC", " ".join(str(n.get("text") or "").split())[:90]
        out += '; newest note %s (%s): "%s"' % (when, n.get("seat") or "?", said)
    return out + " (rimflow show for the rest)"


def ledger_state_line(pointers=True):
    """Regenerate this seat's one-screen ledger state file and name it (HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT, half 2):
    open items, owner-pending, live helpers and NEXT lines as the ledger has them now, not as the handoff narrated them.
    Every wake writes it, so it is never older than the wake that points at it."""
    try:
        import ledger_state
        path = ledger_state.write(seat())
    except Exception as e:      # noqa: BLE001  a wake must still print; an unwritten file says so instead
        return "LEDGER STATE NOW: UNMEASURED (%s). Regenerate: python3 src/RimMandrake/Utils/ledger_state.py" % e
    try:
        with io.open(path, encoding="utf-8") as fh:
            now = fh.read().splitlines()[1]
    except (OSError, IndexError):
        now = "UNMEASURED"
    return ("LEDGER STATE NOW (regenerated by this wake: open items, owner-pending, live helpers, NEXT lines;\n"
            "read it %s): %s\n  now: %s%s" % ("before acting on any pointer above" if pointers else "first", path, now,
                                         " (a game/bridge section above is as at the handoff)" if pointers else ""))


def _corpus_commit_times():
    """{handoff filename: newest commit ts, ledger format} for ALL seats, in
    ONE git call — a per-file `git log` across this 67-file corpus on the
    drvfs mount measures in minutes, not seconds (hit live 2026-09-18)."""
    # ⚠️ BOTH paths AND --diff-filter=AM, deliberately. Handoffs moved out of items/
    # on 2026-09-19;
    # keys here are BASENAMES, and the log is newest-first with first-sighting-wins,
    # so including the historical items/ path keeps every pre-move handoff's ORIGINAL
    # commit time. Query only the new path and all 82 collapse to the move commit's
    # timestamp — `previous_handoff()` picks "newest by commit time", so it would then
    # pick an arbitrary one and wake the seat on the wrong predecessor. AM then drops
    # the move commit itself, which is a pure rename (R) touching all 82 at once and
    # would otherwise become every file's "newest" time — the same collapse by another
    # route. Each handoff keeps the time of the commit that actually WROTE it.
    out = sh("git", "log", "--format=@@%cI", "--name-only", "--diff-filter=AM", "--",
             "infrastructure/state/handoffs/*_HANDOFF_*.md",
             "infrastructure/state/items/*_HANDOFF_*.md")
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
    """Commit time (ledger-format UTC) of the last lessons drain — the newest
    commit in which the inbox SHRANK (a file's deletions > additions, via one
    `--numstat` walk). Filing only adds; only a curation drain removes lines or
    lesson files. Walks both the one-file-per-lesson dir and the old
    LESSONS_INBOX.md history; a commit whose subject carries `[no-drain]` (the
    2026-10-02 split into lessons/) is not a drain. None if none on record."""
    out = sh("git", "log", "--format=@@%cI %s", "--numstat", "--",
             "infrastructure/state/lessons", "infrastructure/state/LESSONS_INBOX.md")
    ts, skip = "", False
    for line in out.splitlines():
        if line.startswith("@@"):
            head = line[2:].strip()
            ts, _, subject = head.partition(" ")
            skip = "[no-drain]" in subject
        elif line.strip() and not skip:
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
        text = io.open(os.path.join(HANDOFFS, fn), encoding="utf-8").read()
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


LESSON_SECTIONS = ("The one thing to carry forward", "Traps learned")
CITATION = re.compile(r"\((?:filed|see):([^)]*)\)", re.I)
EMPTY_LESSON = re.compile(r"^(nothing( new)?( this wave)?|none( new)?( this wave)?|n/?a|-+)\.?$", re.I)
_STAMP_RE = re.compile(r"_HANDOFF_(\d{12})\.md$")


def _norm(text):
    """Lowercased, markup-free, whitespace-collapsed: a lesson filed with other emphasis or wrapping still matches."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"[`*_>#]", "", text.lower())
    return " ".join(text.split())


def lesson_units(text):
    """The lesson-bearing units of a handoff (carry-forward + Traps): each bullet with its indented continuation, each
    prose paragraph as one unit. Comments, fences, unfilled markers and 'nothing this wave' are skipped. None when the
    handoff has NEITHER heading: a free-form handoff's lessons cannot be found, so it is "could not tell", never
    "no lessons"."""
    lines = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S).splitlines()
    units, seen = [], False
    for title in LESSON_SECTIONS:
        i = next((n for n, l in enumerate(lines) if l.startswith("## " + title)), None)
        if i is None:
            continue
        seen, cur, bullet = True, None, False
        for line in lines[i + 1:]:
            if line.startswith("## "):
                break
            if TODO in line or line.strip().startswith("```"):
                continue
            starts = re.match(r"^\s?(?:[-*+]|\d+\.)\s", line)
            if starts or not line.strip() or (bullet and not line[:1].isspace()):
                if cur is not None:     # a bullet, a blank, or unindented prose after a bullet ends the unit
                    units.append(cur)
                cur, bullet = (line, bool(starts)) if line.strip() else (None, False)
            else:                       # a bullet's indented continuation, or the next line of a paragraph
                cur = line if cur is None else cur + " " + line.strip()
        if cur is not None:
            units.append(cur)
    if not seen:
        return None
    out = []
    for u in units:
        bare = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", u).strip()
        if len(bare) >= 12 and not EMPTY_LESSON.match(_norm(bare)):
            out.append(u)
    return out


def _filed(unit, corpus):
    """A unit is filed when it cites a durable home -- `(filed: X)` / `(see: X)` where X is not a handoff -- or its
    text is in the lessons corpus. A citation of "this handoff" or of another handoff file points at a file the cull
    deletes, so it is not a filing."""
    for m in CITATION.finditer(unit):
        target = m.group(1).strip()
        if target and not re.search(r"\b(?:this|the) handoff\b|_HANDOFF_\d", target, re.I):
            return True
    return bool(corpus) and _norm(unit) in corpus


def lessons_corpus():
    """Normalized text of everything ever filed as a lesson: every line any commit added to the lessons dir or the old
    inbox (a lesson filed and later folded still counts), plus the working tree."""
    rels = ("infrastructure/state/lessons", "infrastructure/state/LESSONS_INBOX.md")
    added = [l[1:] for l in sh("git", "log", "-p", "--format=", "--no-color", "--", *rels).splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    for rel in rels:
        p = os.path.join(ROOT, rel)
        for f in ([os.path.join(p, n) for n in os.listdir(p)] if os.path.isdir(p) else [p]):
            try:
                added.append(io.open(f, encoding="utf-8", errors="replace").read())
            except (IOError, OSError):
                pass
    return _norm("\n".join(added))


def _when(fn, times):
    """A handoff's date, ledger-format UTC: its filename stamp (UTC, written by the tool), else its commit time, else
    None. The stamp outranks git: a later edit or a batch commit moves the commit time (CONDUCTOR_HANDOFF_202611180743
    was committed AFTER the 17:27 handoff that replaced it, measured 2026-11-19)."""
    m = _STAMP_RE.search(fn)
    if m:
        try:
            return datetime.datetime.strptime(m.group(1), "%Y%m%d%H%M").strftime("%Y-%m-%dT%H:%M:00Z")
        except ValueError:
            pass
    return times.get(fn) or None


def cull_plan(now=None, corpus=None):
    """-> (candidates, stays). A candidate is a committed handoff that a newer handoff from the same window replaced
    CULL_DAYS or more ago and whose lessons are all filed. Everything else stays, with its reason; "could not tell"
    (unreadable, no date, no lesson headings) is its own reason and is never a candidate. The newest dated handoff of
    each window always stays."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    times = _corpus_commit_times()
    windows, stays = {}, []
    for fn in sorted(handoff_files(all_seats=True)):
        when = _when(fn, times)
        if not when:
            stays.append((fn, "could not tell: no date (no filename stamp, no commit)"))
            continue
        windows.setdefault(_canonical(_HANDOFF_RE.match(fn).group(1)), []).append((when, fn))
    cands = []
    for rows in windows.values():
        rows.sort()
        stays.append((rows[-1][1], "newest of its window"))
        for (_, fn), (sup_ts, sup_fn) in zip(rows, rows[1:]):
            days = (now - datetime.datetime.fromisoformat(sup_ts.replace("Z", "+00:00"))).total_seconds() / 86400.0
            if fn not in times:
                stays.append((fn, "uncommitted"))
                continue
            if days < CULL_DAYS:
                stays.append((fn, "replaced %.1f d ago by %s (< %d)" % (days, sup_fn, CULL_DAYS)))
                continue
            try:
                text = io.open(os.path.join(HANDOFFS, fn), encoding="utf-8").read()
            except (IOError, OSError, UnicodeDecodeError) as e:
                stays.append((fn, "could not tell: unreadable (%s)" % e.__class__.__name__))
                continue
            units = lesson_units(text)
            if units is None:
                stays.append((fn, "could not tell: no lesson headings"))
                continue
            if corpus is None and units:
                corpus = lessons_corpus()
            loose = [u for u in units if not _filed(u, corpus)]
            if loose:
                stays.append((fn, "%d unfiled lesson line(s), first: %s" % (len(loose), " ".join(loose[0].split())[:90])))
                continue
            cands.append((fn, sup_fn, days))
    return cands, stays


def cull(apply_):
    """List (or with --apply delete) the handoffs `cull_plan` marks; every handoff that stays is counted by reason, and
    every could-not-tell one is named. Git is the archive. A missing handoff folder is could-not-look (exit 2), never
    "nothing to cull"."""
    if not os.path.isdir(HANDOFFS):
        print("COULD NOT LOOK: no handoff folder at %s" % HANDOFFS)
        return 2
    cands, stays = cull_plan()
    for fn, sup_fn, days in sorted(cands):
        print("%s  (replaced by %s %.1f d ago; lessons filed)" % (fn, sup_fn, days))
    kinds = {}
    for fn, why in stays:
        k = ("could not tell" if why.startswith("could not tell") else "with unfiled lessons" if "unfiled" in why
             else "replaced < %d d ago" % CULL_DAYS if why.startswith("replaced") else why)
        kinds[k] = kinds.get(k, 0) + 1
    for fn, why in sorted(stays):
        if why.startswith("could not tell") or "unfiled" in why:
            print("STAYS %s  (%s)" % (fn, why))
    print("stay: %s" % ("; ".join("%d %s" % (n, k) for k, n in sorted(kinds.items())) or "none"))
    if not cands:
        print("nothing to cull: no handoff was replaced %d+ days ago with its lessons filed" % CULL_DAYS)
        return 0
    if apply_:
        for fn, _, _ in cands:
            os.remove(os.path.join(HANDOFFS, fn))
        print("deleted %d — commit the deletions with explicit paths; git is the archive." % len(cands))
    else:
        print("%d candidate(s). `--cull --apply` deletes them." % len(cands))
    return 0


def build(since_sha, since_ts, prev_name):
    ev = events()
    s = seat()

    def after(e):
        return since_ts is None or (e.get("ts") or "") > since_ts

    items = _replay().items     # what is open or done is the state machine's answer (an implemented + verify pass
                                # ends an item with no close; a fail after a close reopens it)
    closes = [e for e in ev if e.get("event") == "close" and e.get("seat") == s and after(e)]
    closed = {e.get("id") for e in closes}
    for e in ev:                # finished by verify in this window, by this seat: closed too
        i = e.get("id")
        if (e.get("event") in ("implemented", "verify") and e.get("seat") == s and after(e) and i not in closed
                and i in items and items[i].state == "done"):
            closed.add(i)
            closes.append({"id": i, "sha": "done by %s, no close" % e.get("event")})
    files_ = [e for e in ev if e.get("event") == "file" and after(e)
              and (e.get("for") == s or e.get("seat") == s)]
    still_open = {i for i, it in items.items() if it.open}

    rng = ("%s..HEAD" % since_sha) if since_sha else "-30"
    commits = sh("git", "log", "--oneline", "--format=%h %s", rng)

    dirty = tree_lines()

    game = sh(os.path.join(ROOT, "game"))
    bridge = bridge_lines()

    out = handoff_out(s, HANDOFFS)
    if out is None:
        raise SystemExit("REFUSED: every skeleton name for this minute is taken in %s; nothing written" % HANDOFFS)
    stamp = os.path.basename(out)[len("%s_REBOOT_HANDOFF_" % s):-len(".md")]

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
            L.append("- `%s` — %s" % (e.get("id"), (e.get("title") or "")[:150]))  # cut-ok: an item title in a one-line list
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
    for line in bridge:
        L.append("- Bridge: %s" % line)
    L.append("")
    if dirty is None:
        L.append(TREE_UNMEASURED)
    elif dirty:
        L.append("Uncommitted (replace the placeholder after each line below with whose it is —")
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
                    help="extract lesson sections since the last lessons "
                         "drain into Transient/ for the curation sitting")
    ap.add_argument("--cull", action="store_true",
                    help="list handoffs a newer one from the same window replaced "
                         "%d+ days ago, lessons filed (could-not-tell ones listed, kept)" % CULL_DAYS)
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
    require_worker_seat(s)
    prev_name, prev_ts = previous_handoff()
    since_sha = a.since
    if not since_sha and prev_name:
        p = os.path.join("infrastructure", "state", "handoffs", prev_name)
        since_sha = sh("git", "log", "-1", "--format=%h", "--", p) or None

    # --check validates the handoff THIS session wrote, which is the most recently
    # touched one — again not the alphabetically last, for the same reason.
    cands = [os.path.join(HANDOFFS, fn) for fn in handoff_files()]
    newest = max(cands, key=os.path.getmtime) if cands else None

    # write mode only: --check on a quiet window still checks the newest handoff (Codex, 2026-11-18: an uncommitted new
    # handoff with unowed pointers or unfilled sections read ALREADY HANDED OFF and exited 0 unchecked)
    since_ts = window_start(a.since, prev_ts)    # --since moves the ledger window too, not only the commit range
    if prev_name and window_is_empty(since_sha, since_ts) and not a.force and not a.check:
        print("ALREADY HANDED OFF — nothing has closed, been filed or been "
              "committed since\n  %s"
              % os.path.join("infrastructure", "state", "handoffs", prev_name))
        print("\nThat handoff still stands. Do NOT write another and do NOT say "
              "HANDOFF READY again;\nsay it once, then stay quiet until real work "
              "comes in. --force overrides.")
        return 0

    problems = gates(since_ts, newest if a.check else None,
                     doing_is_fatal=a.check)

    # Owner 2026-10-18 (BUILDUP_BUILD_CLONES_STOP_BREEDING Q3): "the next handoff plays catchup and takes as
    # long as it takes" -- the handoff lands every new/changed conversations/*.md record, by explicit path.
    sys.path.insert(0, HERE)
    import conversations_land
    convs = conversations_land.pending(ROOT)
    if convs and not a.check:
        rc, last = conversations_land.land(convs, ROOT)
        print("conversations/: %s" % ("landed %d record(s) %s" % (len(convs), last) if rc == 0
                                      else "REFUSED landing %d record(s) (land.sh exit %d)" % (len(convs), rc)))
        convs = conversations_land.pending(ROOT)
    if convs:
        problems.append("%d conversations/ record(s) not committed -- run "
                        "python3 src/RimMandrake/Utils/conversations_land.py --apply" % len(convs))

    if a.check:
        problems += todo_scan(newest) + owed_pointer_problems(newest) if newest else ["no handoff file written yet"]
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

    out = build(since_sha, since_ts, prev_name)
    print("wrote %s" % os.path.relpath(out, ROOT))
    print("\nFill these in — a script cannot:")
    for title, prompt in JUDGEMENT_SECTIONS:
        print("  %-38s %s" % (title, prompt.split(".")[0] + "."))
    print("\nThen: handoff.py --check, commit, push, and say HANDOFF READY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
