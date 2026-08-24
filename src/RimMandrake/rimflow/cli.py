#!/usr/bin/env python3
"""rimflow/cli.py — the command surface a seat actually types.

    python3 src/RimMandrake/rimflow/cli.py next --seat BUILD
    python3 -m rimflow.cli next --seat BUILD

WHAT THIS FILE IS AND IS NOT
============================
It is a **thin shell over `model.py` and `priority.py` and nothing else.** Every rule
lives there; every refusal message is written there. This file's whole job is to turn
words a human types into one event dict, hand it to `model.check()`, and — only if that
returns — hand it to `model.append()`.

⛔ **No rule may be re-implemented here.** A permission check written twice is a
permission check that will disagree with itself, and the ledger's own docstring says
why that is the failure this design exists to end. If a refusal is missing, it is
missing from `model.py`.

🔑 **`check()` BEFORE `append()`, always.** `validate()` alone cannot know that an item
is already closed, because that fact lives in the replay and not in the event. `check()`
replays the candidate against current state. `_emit()` below is the only writer, and it
does both, in that order, every time.

🔑 **A refusal is printed VERBATIM and exits non-zero.** Those messages were written to
tell someone what to do instead — "an item that closed cannot be reopened. File a NEW
item and link it with caused_by" — and paraphrasing them into "error: refused" throws
away the only part that helps.

🔴 WHICH SEAT AM I — AND WHY THIS REFUSES RATHER THAN GUESSES
============================================================
`seat` is on every event, it is what every permission check reads, and the ledger is
append-only: an event attributed to the wrong seat is a **permanent lie in a file with
no delete**. So the resolution order is explicit and it ends in a refusal, never in a
default:

    1. RIMFLOW_SEAT          an explicit override, for scripts and tests
    2. --seat SEAT           what the human typed, which beats ambient state
    3. AGENT_SEAT            exported by the Windows Terminal seat profiles
    4. .claude/session_roles/$CLAUDE_SESSION_ID   what set_agent_window.sh recorded
    5. REFUSE

⚠️ Step 4 is deliberately narrow: it consults the role file for **this** session id and
no other. There are ~60 role files in that directory from past sessions, and picking
the newest — the obvious cheap heuristic — would silently sign this seat's events with
whichever window was opened last. A wrong seat is worse than no seat.

WHAT IS NOT MINE
================
⛔ `render` and `reindex` belong to `render.py`, which another agent owns. They are
wired here as thin subcommands that import it if it exists and say so plainly if it
does not. This file must never grow its own renderer — two renderers is two answers.

⚠️ `sweep --transient` LISTS. It never deletes. A heuristic calling someone's working
notes stale is not grounds for destroying them, and the listing is the whole product.
"""
import argparse
import os
import re
import subprocess
import sys

try:                                                    # python3 -m rimflow.cli
    from . import model, priority, probe
except ImportError:                                     # python3 .../rimflow/cli.py
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimflow import model, priority, probe          # noqa: F401

PROSE_BUDGET = 2400          # chars of items/<ID>.md that `next` will print, ~600 tokens


# ---------------------------------------------------------------------------
# PATHS
#
# `RIMFLOW_LEDGER` and `RIMFLOW_ITEMS` redirect the whole tool at a throwaway ledger,
# which is how `selftest_cli.py` runs end-to-end with no risk to the real one.
#
# ⚠️ This used to also rebind `model.read.__defaults__` / `model.append.__defaults__`,
# because those functions took `path=EVENTS` as a DEFAULT ARGUMENT — evaluated at
# import, so reassigning `model.EVENTS` redirected nothing and a test that only set the
# global appended to the REAL, append-only ledger. `model.py` now resolves the path at
# call time (2026-08-20), so the rebinding is gone. ⛔ If you ever find yourself
# reaching for `__defaults__` again, the bug is in the callee.
# ---------------------------------------------------------------------------
def _bind_paths():
    led = os.environ.get("RIMFLOW_LEDGER")
    its = os.environ.get("RIMFLOW_ITEMS")
    if led:
        model.EVENTS = led
    if its:
        model.ITEMS = its


def die(msg, code=2):
    sys.stderr.write(msg.rstrip() + "\n")
    raise SystemExit(code)


# ---------------------------------------------------------------------------
# SEAT
# ---------------------------------------------------------------------------
def _role_file_seat():
    sid = os.environ.get("CLAUDE_SESSION_ID")
    if not sid:
        return None
    path = os.path.join(model.ROOT, ".claude", "session_roles", sid)
    try:
        with open(path, encoding="utf-8") as fh:
            words = fh.read().replace("-", " ").split()
    except OSError:
        return None
    for w in words:                      # the file reads "AGENT BUILD"
        if w.upper() in model.SEATS:
            return w.upper()
    return None


def resolve_seat(explicit):
    for src, val in (("RIMFLOW_SEAT", os.environ.get("RIMFLOW_SEAT")),
                     ("--seat", explicit),
                     ("AGENT_SEAT", os.environ.get("AGENT_SEAT")),
                     ("session role file", _role_file_seat())):
        if not val:
            continue
        val = val.strip().upper()
        if val not in model.SEATS:
            die("%s says the seat is %r, which is not one of %s."
                % (src, val, ", ".join(model.SEATS)))
        return val
    die("REFUSED: I cannot tell which seat I am, and I will not guess.\n"
        "  `seat` is on every event, every permission check reads it, and the ledger "
        "is append-only —\n"
        "  a wrong seat is a permanent lie in a file with no delete.\n"
        "  Fix it with ONE of:\n"
        "    rimflow <verb> --seat BUILD\n"
        "    export RIMFLOW_SEAT=BUILD\n"
        "    ./src/RimMandrake/Utils/set_agent_window.sh BUILD   (then reopen the tab)")


# ---------------------------------------------------------------------------
# LEDGER ACCESS
# ---------------------------------------------------------------------------
def load():
    """-> (events, world). Read once; every command needs both."""
    try:
        evs = model.read(model.EVENTS)
    except model.LedgerError as e:
        die(str(e))
    w = model.replay(evs)               # non-strict: mistakes already in the file stand
    return evs, w


def _emit(ev, world=None, quiet=False):
    """check() then append(). The ONLY writer in this file."""
    ev = {k: v for k, v in ev.items() if v not in (None, "", False)}
    try:
        model.check(ev, world)
        # 🔴 The OWNER overrode a seat rule (2026-08-22 ruling — see `model._may`).
        # STAMP it before appending and WARN on stderr: he asked to be able to
        # override, and to be told when he did. Silent power is the failure mode here,
        # not the override itself. `check()` deep-copies the event, so the notice comes
        # back on the module, not on `ev`.
        said = getattr(model, "OWNER_SAID", "")
        if said:
            ev["ownerSaid"] = said
            sys.stderr.write(
                "\u2705 Acting as OWNER on his instruction, recorded on the event:\n"
                "     \u201c%s\u201d\n" % said)
        if model.OVERRIDE_NOTICES:
            ev["override"] = model.OVERRIDE_NOTICES[0]
            sys.stderr.write(
                "⚠️  OWNER OVERRIDE — the rule bypassed was: %s\n"
                "    Allowed because you are the OWNER, and recorded on the event as "
                "`override` so the ledger shows you crossed a seat boundary on purpose.\n"
                % model.OVERRIDE_NOTICES[0])
        model.append(ev, model.EVENTS)
    except model.LedgerError as e:
        die(str(e))                     # verbatim, non-zero — see the module docstring
    if not quiet:
        print("%s %s%s" % (ev["event"], ev.get("id", ""),
                           "" if ev.get("id") else "(" + str(ev.get("state", "")) + ")"))
    return ev


def git(*args):
    try:
        return subprocess.check_output(("git",) + args, cwd=model.ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except (subprocess.CalledProcessError, OSError):
        return ""


def head_sha():
    return git("rev-parse", "--short", "HEAD") or None


# ---------------------------------------------------------------------------
# PROSE
# ---------------------------------------------------------------------------
def read_prose(iid):
    """-> [(section, body)] from items/<ID>.md, in file order. Missing file -> []."""
    path = os.path.join(model.ITEMS, "%s.md" % iid)
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []
    out, name, buf = [], None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if name:
                out.append((name, "\n".join(buf).strip()))
            name, buf = line[3:].strip(), []
        elif name:
            buf.append(line)
    if name:
        out.append((name, "\n".join(buf).strip()))
    return out


def _scalars(it):
    bits = [it.state]
    if it.blocked:
        bits.append("BLOCKED")
    bits.append("row %s" % (it.row if it.row is not None else "-"))
    bits.append("needs %s" % it.needs)
    bits.append("target %s" % (it.target or "v1"))
    if it.this_deployment:
        bits.append("THIS DEPLOYMENT")
    return "  ".join(bits)


# The words `infrastructure/state/MODE` may hold, and what each resolves to.
#
# 🔴 The live vocabulary is BENCH · BELT · AFK (owner, 2026-08-23) and only two of the
# three belong in this file. BENCH is PER-WINDOW — it is simply whether he is talking to
# a given window right now, it is delivered per turn by `.claude/hooks/bench_mode.py`,
# and it has no global truth to write down. A `MODE` file reading `bench` is therefore a
# misunderstanding, not a setting, and is refused loudly below rather than ignored.
#
# ⚠️ `interactive` and `autonomous` are DEAD WORDS, superseded the same day (`REP.md:99`).
# They are still accepted here and normalised to `belt` because that is EXACTLY what they
# already did: neither equalled `afk`, so neither ever suppressed anything, and mapping
# them preserves behaviour byte for byte while retiring the vocabulary. ⛔ Do not "repair"
# MODE back to one of them.
_MODE_WORDS = {
    "belt": "belt",
    "afk": "afk",
    "interactive": "belt",   # legacy, behaviour-preserving
    "autonomous": "belt",    # legacy, behaviour-preserving
}


def _mode_file():
    """`infrastructure/state/MODE`, or None. 🔴 NOTHING READ THIS FILE UNTIL 2026-08-22.

    `POLICY.md > Modes` and `REP.md` both documented it as the switch between
    `interactive`, `autonomous` and `afk`, REP owns it, and the owner sets it — and the
    only readers were a `--mode` flag nobody passes and `$RIMFLOW_MODE`. So `afk`
    suppressed nothing and the documented mechanism was inert: a dead channel with
    three docs pointing at it.

    ⚠️ **Corrected 2026-08-23.** The file HAS been read since 2026-08-22 (resolved into
    the context at the bottom of this module), but it only recognised the three words
    above — so when the owner moved the vocabulary to BENCH · BELT · AFK and MODE was
    set to `belt`, the channel went inert again for a second, different reason and no
    one was told. An unrecognised word now says so on stderr instead of returning a
    silent None.
    """
    try:
        with open(os.path.join(model.ROOT, "infrastructure", "state", "MODE"),
                  encoding="utf-8") as fh:
            word = fh.read().strip().split()[0].lower()
    except (OSError, IndexError):
        return None
    if word in _MODE_WORDS:
        return _MODE_WORDS[word]
    if word == "bench":
        print("rimflow: MODE reads `bench`, which is not a global mode — BENCH is "
              "per-window and is delivered by .claude/hooks/bench_mode.py. Ignoring; "
              "write `belt` or `afk`.", file=sys.stderr)
    else:
        print("rimflow: MODE reads `%s`, which is not a mode word — ignoring. "
              "Valid: belt | afk." % word, file=sys.stderr)
    return None


def _stale_board():
    """-> a warning if `queue/*.md` have gone stale, else "".

    🔴 THE PUBLISHER IS BOUNDED AT 8 HOURS AND DIES SILENTLY, ON PURPOSE — and the cost
    lands the next morning. Measured 2026-08-22: it stopped at 00:21 and the queues sat
    frozen for 9 hours, so a seat waking would have read a view predating an entire day
    of rulings. It had already happened once before, for 2h17m, with a seat watching.

    ⚠️ `rimflow` itself reads the LEDGER, so `next` is always current — but the board and
    every `queue/*.md` reader is not, and nothing else notices. This is the one command
    every seat runs first, so the warning belongs here.
    """
    import time
    q = os.path.join(model.ROOT, "infrastructure", "state", "queue", "BUILD.md")
    try:
        age = (time.time() - os.path.getmtime(q)) / 60.0
    except OSError:
        return ""
    if age < 5:
        return ""
    return ("⚠️  THE BOARD IS %d MINUTES STALE — `queue/*.md` and http://localhost:8787 "
            "are\n    showing a view that old. What you read below is CURRENT (it comes "
            "from the\n    ledger); the published board is not. The publisher is bounded "
            "at 8h and dies\n    quietly. Restart it — REP's job, anyone's command:\n"
            "      setsid nohup ./src/RimMandrake/Utils/board_loop.sh "
            ">/dev/null 2>&1 </dev/null &\n" % age)


def _ctx(args):
    return {"mode": (getattr(args, "mode", None) or os.environ.get("RIMFLOW_MODE")
                     or _mode_file()),
            "harvest_pending": bool(os.environ.get("RIMFLOW_HARVEST_PENDING"))}


# ---------------------------------------------------------------------------
# next — the command that matters
# ---------------------------------------------------------------------------
def cmd_next(args, seat):
    warn = _stale_board()
    if warn:
        sys.stderr.write(warn)
    _, w = load()
    # 🔴 MEASURE BEFORE OFFERING. `next` decides what a seat may work on, and half of
    # that decision is the game state — so it reads it from the machine, not from what
    # somebody last typed. Owner, 2026-08-22: the measurement wins, silently. Cached for
    # 20 s in probe.py, so a seat in a loop does not shell out every call.
    sync_game_state(w, seat)
    ctx = _ctx(args)
    it = priority.next_item(w, seat, args.target, ctx)
    if it is None:
        claimable = _claimable(w, seat, args.target)
        if claimable:
            return _offer_claimable(claimable, seat)
        return _nothing(w, seat, args, ctx)

    # 🔑 ALWAYS state the world. `POLICY.md` used to open a turn with `cli.py game`,
    # which takes a required positional and errors with no arguments — so the first of
    # the three start-of-turn commands had never worked. The question it was asking is
    # cheap to answer here, and answering it here means one fewer command in the turn.
    print("(game %s, bridge %s)" % (w.game, w.bridge_holder or "free"))
    print("%s   %s" % (it.id, _scalars(it)))
    print(it.title or "(no title)")
    if it.caused_by:
        print("caused by %s" % it.caused_by)
    print("")
    prose = read_prose(it.id)
    if not prose:
        print("(items/%s.md has no sections — it should not have reached `ready`)"
              % it.id)
    budget = PROSE_BUDGET
    for name, body in prose:
        if name.lower() not in ("spec", "verify", "criteria"):
            continue
        if budget <= 0:
            print("... (rest of items/%s.md not shown; open it)" % it.id)
            break
        print("## %s" % name)
        if len(body) > budget:
            body = body[:budget] + "\n... (truncated; open items/%s.md)" % it.id
        budget -= len(body)
        print(body + "\n")
    print("-> rimflow start %s" % it.id)
    # ⭐ AND SAY WHAT IS QUEUED BEHIND IT. `_claimable` below fires only when NOTHING is
    # claimed, which fixed the empty-queue case and left the worse one open: a seat with
    # any `ready` item never learns that spec-complete work is waiting. Measured
    # 2026-08-21, AFTER that fix landed: 30 finished specs masked fleet-wide — 15 behind
    # BUILD and 15 behind CHECK. 🔴 BUILD's top item was `B-V2`, a STANDING RIGHT with no
    # completion condition, so its queue could never empty and those 15 were unreachable
    # forever, not merely delayed.
    also = _claimable(w, seat, args.target)
    if also:
        print("")
        print("⚠️  %d item%s ALSO waiting for %s to claim: %s%s"
              % (len(also), "" if len(also) == 1 else "s", seat,
                 ", ".join(i.id for i in also[:4]),
                 "" if len(also) <= 4 else ", +%d" % (len(also) - 4)))
        print("    filed for you by another seat. `rimflow claim <ID>` to take one.")
    return 0


def _claimable(w, seat, target="v1"):
    """-> [Item] this seat owns that are `proposed` and unblocked, thin ones included.

    🔴 THE HANDOFF USED TO END HERE, SILENTLY. `priority.rank()` filters
    `state == "ready"`, and an item filed FOR a seat lands in `proposed` — so work that
    another seat had specced in full was never surfaced by the only command POLICY tells
    a seat to run. Measured 2026-08-21: BUILD held 21 proposed items, **18 of them
    spec-complete**, while `next` offered 3 and the board showed no problem. Fleet-wide,
    28 finished specs were unreachable.

    ⚠️ This deliberately does NOT change `priority.rank()`. `ready` still means claimed,
    the claim is still an explicit act, and the rendered NEXT section still shows only
    claimed work. What changes is that an empty answer must now say "claim one" rather
    than "nothing".
    """
    # 🔴 NO COMPLETENESS FILTER — owner's ruling, 2026-08-22. `and model._complete(i)`
    # used to sit on the end of this list comprehension, and it was the removed gate's
    # last hiding place: the owner killed the completeness gate on 2026-08-21 at `claim`
    # and at `start`, and the removal never reached the OFFER path. So a thin item was
    # not refused, it was INVISIBLE — strictly worse, because nothing was told and the
    # blame landed on whoever filed it. Measured 2026-08-22: three of BUILD's open items
    # were starved this way. A thin item is offered, and `_offer_claimable` says what is
    # thin about it so the claiming seat knows what it is walking into.
    out = [i for i in w.items.values()
           if i.owner == seat and i.state == "proposed" and not i.blocked
           and i.target in (None, target)]
    out.sort(key=lambda i: (not i.this_deployment, i.created_at or "", i.id))
    return out


def _offer_claimable(items, seat):
    it = items[0]
    print("nothing is CLAIMED, but %d item%s waiting for %s to claim."
          % (len(items), "" if len(items) == 1 else "s", seat))
    print("")
    print("%s   %s" % (it.id, _scalars(it)))
    print(it.title or "(no title)")
    # 🔑 What is thin about the item you are being offered, said UP FRONT — never as a
    # reason you cannot have it. Owner, 2026-08-22: a missing field is not a rejection,
    # it is a signal that the filer knows something they have not written down.
    gaps = model._missing(it)
    if gaps:
        print("")
        print("⚠️  THIN ITEM — offered anyway, but you are missing:")
        for m in gaps:
            print("      ## %-9s %s" % (m, {
                "spec": "(nobody said what the world must become)",
                "verify": "(nobody said how to prove it)",
                "criteria": "(nobody said what CHECK looks for)"}[m]))
        print("   The filer may know something you do not. Ask, or decide it yourself")
        print("   and write down what you chose.")
    if len(items) > 1:
        rest = ", ".join(i.id for i in items[1:6])
        print("also: %s%s" % (rest, "" if len(items) <= 6 else ", +%d" % (len(items) - 6)))
    print("")
    print("-> rimflow claim %s     (then `start`)" % it.id)
    return 0


def _nothing(w, seat, args, ctx):
    """⭐ An empty answer must still say WHY, in one line.

    "Nothing to do" is the answer that sends a seat hunting through the queues by hand,
    which is the behaviour the ledger exists to remove. "3 ready items, all need the
    bridge and the game is DOWN" tells the seat to go and do something else instead.
    """
    mine = [i for i in w.items.values() if i.owner == seat and i.open]
    print("nothing offered for %s. (game %s, bridge %s)"
          % (seat, w.game, w.bridge_holder or "free"))
    if not mine:
        print("%s owns no open items at all. File some: rimflow file <ID> --for %s ..."
              % (seat, seat))
        return 0
    buckets = {}
    for i in mine:
        reasons = priority.why_not(w, seat, i.id, args.target, ctx)
        key = reasons[0].split(".")[0].split(":")[0].strip() if reasons else "?"
        buckets.setdefault(key, []).append(i.id)
    print("%d open item%s:" % (len(mine), "" if len(mine) == 1 else "s"))
    for key, ids in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        show = ", ".join(ids[:4]) + ("" if len(ids) <= 4 else ", +%d" % (len(ids) - 4))
        print("  %d  %s  (%s)" % (len(ids), key, show))
    incomplete = [i for i in mine
                  if i.state == "proposed" and not model._complete(i)]
    if incomplete:
        # ⚠️ INFORMATION, NOT A GATE. These items ARE offered and ARE claimable; this
        # says what you would be walking into. The old text read "cannot be claimed …
        # whoever filed them owes the prose", which was the gate the owner removed.
        print("⚠️  %d thin item(s) — offered anyway, but something was left unsaid:"
              % len(incomplete))
        for i in incomplete[:6]:
            print("      %-44s no %s"
                  % (i.id, ", ".join("## " + m for m in model._missing(i))))
        print("    Claim them as they stand. The filer may know something you do not —"
              "\n    ask, or decide it yourself and write down what you chose.")
    if getattr(priority, "UNKNOWN_NEEDS", None):
        # 🔴 An unrecognised `needs` no longer hides an item (priority.satisfiable fails
        # open since 2026-08-22). It is REPORTED, because a value nothing understands is
        # a defect somebody must fix, not a state to live in.
        print("⚠️  unrecognised `needs` value(s) in play: %s"
              % ", ".join(sorted(str(u) for u in priority.UNKNOWN_NEEDS)))
        print("    Those items ARE offered — nothing is hidden — but the value means "
              "nothing to the")
        print("    priority engine. Legal values: %s" % ", ".join(model.NEEDS))
    print("-> rimflow why <ID> for the full reason")
    return 0


# ---------------------------------------------------------------------------
# show / why — the debugging surface
# ---------------------------------------------------------------------------
def _describe(ev):
    verb = ev["event"]
    extras = [(k, v) for k, v in sorted(ev.items())
              if k not in ("ts", "seat", "event", "id")]
    tail = " ".join("%s=%s" % (k, v) for k, v in extras)
    return "%s  %-6s %-9s %s" % (ev.get("ts", "?"), ev.get("seat", "?"), verb, tail)


def cmd_show(args, seat):
    evs, w = load()
    it = w.items.get(args.id)
    if it is None:
        die("%s has never been filed. `rimflow file %s --for <SEAT> --title \"...\"` "
            "creates it." % (args.id, args.id))

    print("%s   %s" % (it.id, _scalars(it)))
    print("%s" % (it.title or "(no title)"))
    print("owner %s   kind %s   filed %s" % (it.owner, it.kind, it.created_at))
    if it.blocked:
        print("BLOCKED: %s%s" % (it.blocked_reason,
                                 " (on %s)" % it.blocked_on if it.blocked_on else ""))
    if it.closed_sha:
        print("closed at %s" % it.closed_sha)
    if it.superseded_by:
        print("superseded by %s" % it.superseded_by)

    prose = read_prose(it.id)
    print("\n--- items/%s.md ---" % it.id)
    if not prose:
        print("(absent or has no ## sections)")
    for name, body in prose:
        print("## %s\n%s\n" % (name, body))

    print("--- history (%d events) ---" % len(it.history))
    for idx in it.history:
        print("  " + _describe(evs[idx]))

    if it.runs:
        print("--- runs (immutable; a failure stands forever) ---")
        for r in it.runs:
            print("  %s  %-7s %s" % (r.name, r.result, r.evidence or ""))
    if it.findings:
        print("--- findings ---")
        for n in it.findings:
            f = w.findings.get(n, {})
            print("  %s  %s/%s" % (n, f.get("type"), f.get("severity")))

    print("--- causal chain ---")
    for line in _chain(w, it.id):
        print("  " + line)
    return 0


def _chain(w, iid, seen=None):
    """Follow caused_by up to the root, then list what this item caused.

    🔑 The chain is what makes a spawned item defensible. `run -> finding -> spawn`
    is the R&D path §4 describes, and without it a follow-up item reads as somebody's
    opinion rather than as the consequence of a run that is on the record.
    """
    out, seen = [], seen or set()
    cur, up = iid, []
    while cur and cur not in seen:
        seen.add(cur)
        it = w.items.get(cur)
        cause = it.caused_by if it else None
        if not cause:
            break
        up.append("%s  <- caused by %s" % (cur, cause))
        m = model.RUN_RE.match(str(cause))
        if m:
            up.append("%s  <- run of %s" % (cause, m.group("item")))
            cur = m.group("item")
        elif cause in w.findings:
            frm = w.findings[cause].get("from")
            up.append("%s  <- finding from %s" % (cause, frm))
            m2 = model.RUN_RE.match(str(frm))
            cur = m2.group("item") if m2 else frm
        else:
            cur = cause
    out.extend(reversed(up))
    kids = [i.id for i in w.items.values()
            if i.caused_by and (i.caused_by == iid
                                or str(i.caused_by).startswith(iid + "/run-")
                                or w.findings.get(str(i.caused_by), {}).get("from", "")
                                .startswith(iid + "/run-"))]
    for k in sorted(kids):
        out.append("%s  -> caused %s" % (iid, k))
    return out or ["(none — this item stands on its own)"]


def cmd_why(args, seat):
    _, w = load()
    for line in priority.why_not(w, seat, args.id, args.target, _ctx(args)):
        print("- " + line)
    return 0


# ---------------------------------------------------------------------------
# WRITERS — every one of these is one event
# ---------------------------------------------------------------------------
OPEN_STATES_EXCLUDED = ("done", "dropped", "superseded")


def _replaces(args, seat, w):
    """Close the parent when a successor takes its work over — or ask whether one did.

    ⚠️ NEVER auto-closes on `caused_by` alone. A parent is usually BROADER than the child:
    `B40` was rewritten out from under itself by `AUTHORED_KINDS_MUST_FIELD_1` and STILL
    owed an in-game raid-tier check. Auto-closing would have dropped that silently, which
    is the exact failure `supersede --by` exists to prevent. So this asks; it never assumes.
    """
    items = model.replay(model.read(model.EVENTS)).items
    parent = args.replaces
    if parent:
        it = items.get(parent)
        if it is None:
            print("⚠️  --replaces %s: no such item. NOTHING was superseded; %s is filed."
                  % (parent, args.id))
            return
        if it.state in OPEN_STATES_EXCLUDED:
            print("⚠️  --replaces %s: already %s. Left alone; %s is filed."
                  % (parent, it.state, args.id))
            return
        try:
            _emit({"seat": seat, "event": "supersede", "id": parent, "by": args.id,
                   "reason": "superseded by %s, which takes over its work" % args.id},
                  w, quiet=True)
            print("%s -> superseded by %s." % (parent, args.id))
        except SystemExit:
            print("⚠️  %s is filed, but %s was NOT superseded — it belongs to another seat."
                  % (args.id, parent))
            print("     python3 src/RimMandrake/rimflow/cli.py supersede %s --by %s"
                  % (parent, args.id))
            raise
        return
    # No --replaces. Ask ONLY when the shape says a parent may be dying: this item
    # descends from another that is still open. Silent otherwise — 410 filings to date,
    # and a line printed on every one of them is noise, not a prompt.
    cb = args.caused_by
    if not cb:
        return
    it = items.get(str(cb).split("/")[0])
    if it is None or it.state in OPEN_STATES_EXCLUDED:
        return
    print("")
    print("🔑 Does %s REPLACE %s, or only descend from it?" % (args.id, it.id))
    print("   %s is still open (%s)." % (it.id, it.state))
    print("   Takes over its work  -> supersede it now, so it closes naming its successor:")
    print("     python3 src/RimMandrake/rimflow/cli.py supersede %s --by %s"
          % (it.id, args.id))
    print("   Only part of it      -> leave it open. A parent is usually BROADER than")
    print("                           its child, and closing it drops the remainder.")


def cmd_file(args, seat):
    _, w = load()
    ev = {"seat": seat, "event": "file", "id": args.id, "title": args.title,
          "kind": args.kind, "row": args.row, "target": args.target_field,
          "needs": args.needs, "spec": args.spec, "caused_by": args.caused_by}
    ev["for"] = args.for_
    _emit(ev, w, quiet=True)
    print("%s filed for %s, state proposed." % (args.id, args.for_))
    _replaces(args, seat, w)
    have = {n.lower() for n, _ in read_prose(args.id)}
    miss = [s for s in ("spec", "verify", "criteria") if s not in have]
    if miss:
        print("items/%s.md has no %s yet — worth adding, but it IS offered and can be "
              "claimed and started exactly as it stands."
              % (args.id, " or ".join("## " + m for m in miss)))
    # 🔑 THE ONE SECTION NOBODY ELSE CAN SUPPLY — owner's ruling, 2026-08-22:
    # *"the submitter should include any non-obvious information that should be
    # considered for V&V because of interdependencies that the submitter may only be
    # aware of themselves."* Prompted by name, never required — the whole point of the
    # ruling is that a missing field stops being a rejection.
    # ⚠️ `needs` DEFAULTS TO `offline`, which is a claim that nothing external is
    # required — and it is the field `priority.satisfiable()` uses to decide whether the
    # item is ever offered. A wrong one either hides work or offers unrunnable work.
    # Measured 2026-08-22: CHECK hand-corrected 45 items across 44 filings, almost all
    # to `bridge`. Prompted, never required — the filer knows and the default does not.
    if not args.needs:
        print("⚠️  needs is `offline` by default — a claim that nothing external is "
              "required.")
        print("   If this wants a window, restamp it now, in this turn:")
        print("     python3 src/RimMandrake/rimflow/cli.py needs %s --to "
              "<deploy|game-up|bridge|harvest|owner>" % args.id)
    if "watch out" not in have and args.for_ != seat:
        print("")
        print("🔑 Worth adding — nobody else can supply this:")
        print("   ## Watch out")
        print("     what else reads this def, what load order affects it, what a")
        print("     passing verify would still miss. You are the only one who knows")
        print("     what you were looking at when you filed it.")
        print("   items/%s.md   (optional; the item is already claimable)" % args.id)
    return 0


def _simple(verb, extra=()):
    def run(args, seat):
        _, w = load()
        ev = {"seat": seat, "event": verb, "id": args.id}
        for field, attr in extra:
            ev[field] = getattr(args, attr, None)
        _emit(ev, w, quiet=True)
        it = model.replay(model.read(model.EVENTS)).items.get(args.id)
        print("%s %s -> %s" % (verb, args.id, it.state if it else "?"))
        return 0
    return run


def cmd_close(args, seat):
    _, w = load()
    sha = args.sha or head_sha()
    if not sha:
        die("`close` needs a sha and `git rev-parse --short HEAD` gave nothing — you are "
            "probably\nin a repo with no commits yet, or outside one.\n\n"
            "The sha is what makes a close checkable a year later; a close with no commit "
            "behind\nit is a claim. 🔑 COMMIT THE WORK FIRST — the commit IS the close:\n\n"
            "    git commit <the paths you changed> -m \"<what you did>\"\n"
            "    python3 src/RimMandrake/rimflow/cli.py close %s\n\n"
            "⚠️  Nothing is lost by the refusal — the item is untouched and still yours."
            % args.id)
    _emit({"seat": seat, "event": "close", "id": args.id, "sha": sha}, w, quiet=True)
    print("%s closed at %s." % (args.id, sha))
    return 0


_EVIDENCE_PATH_RE = re.compile(
    r"(?:observed|infrastructure|src|design|world|skills)[\w./-]*"
    r"\.(?:txt|md|json|jsonl|csv|html|log|xml|png)")


def _dead_evidence(evidence):
    """-> paths named in `evidence` that are not on disk.

    🔴 A VERIFY IS ONLY WORTH ITS EVIDENCE, and a pointer that does not resolve is not
    evidence — it is a claim. Measured 2026-08-22: nine `verify` events cite
    `observed/2026-08-21_Player.log`, which has never existed at that path (logs live in
    `observed/logs/` under a different name), and the 22:44 harvest output they were
    graded from is gone from disk entirely. Those numbers can now only be QUOTED, never
    re-counted, and nothing said so at the time.

    ⚠️ Checked HERE because this is the one moment it is cheap: the seat still has the
    file open and can save it in seconds. An hour later the log has rotated.

    🔑 ONE `observed/`, at the repo root. The former second root at
    `infrastructure/state/observed/` was merged into it on 2026-08-23. Ledger events
    written before that date cite the old prefix, so it is still accepted below and
    rewritten onto the surviving root — never re-add a second search root.
    """
    legacy = "infrastructure/state/observed/"
    out = []
    for m in sorted(set(_EVIDENCE_PATH_RE.findall(evidence or ""))):
        cands = [m, os.path.join(model.ROOT, m)]
        if m.startswith(legacy):
            cands.append(os.path.join(model.ROOT, m[len("infrastructure/state/"):]))
        if not any(os.path.exists(c) for c in cands):
            out.append(m)
    return out


def cmd_verify(args, seat):
    _, w = load()
    dead = _dead_evidence(args.evidence)
    if dead:
        sys.stderr.write(
            "\u26a0\ufe0f  EVIDENCE THAT DOES NOT RESOLVE — recorded anyway, but say so:\n"
            + "".join("      %s\n" % d for d in dead)
            + "   A pointer nobody can follow is a claim, not evidence. \U0001f511 Save "
              "the file NOW while\n   you still have it — Player.log rotates on the next "
              "launch and is then gone for\n   good. If it truly cannot be kept, put the "
              "numbers themselves in --evidence so\n   they survive without it.\n")
    _emit({"seat": seat, "event": "verify", "id": args.id, "result": args.result,
           "config": args.config, "evidence": args.evidence,
           "sha": args.sha or head_sha()}, w, quiet=True)
    it = model.replay(model.read(model.EVENTS)).items[args.id]
    r = it.runs[-1]
    print("%s recorded, result %s. IMMUTABLE — %s is not reopened."
          % (r.name, r.result, args.id))
    return 0


def _item_of(ref, w):
    """A finding or spawn names its cause; the item it hangs on is derivable from it."""
    m = model.RUN_RE.match(str(ref))
    if m:
        return m.group("item")
    f = w.findings.get(str(ref))
    if f:
        m = model.RUN_RE.match(str(f.get("from")))
        if m:
            return m.group("item")
        return f.get("from")
    return ref if ref in w.items else None


def cmd_finding(args, seat):
    _, w = load()
    iid = args.id or _item_of(args.from_, w)
    if not iid:
        die("cannot tell which item this finding hangs on. Pass --id, or make --from a "
            "run name like C40/run-3@full-578.")
    ev = {"seat": seat, "event": "finding", "id": iid, "type": args.type,
          "severity": args.severity, "name": args.name}
    ev["from"] = args.from_
    _emit(ev, w, quiet=True)
    print("%s recorded against %s (from %s)." % (args.name, iid, args.from_))
    return 0


def cmd_spawn(args, seat):
    """`spawn --from <cause> --for <SEAT> --name <NEW>` — no host item.

    ⚠️ This used to resolve a host `id`, because `model.spawn` demanded one. It no
    longer does (fixed 2026-08-20): a spawn is about its CAUSE and its PRODUCT, and
    nominating some third item as the host was an artefact of the old schema.
    ⛔ Do not reintroduce `--id` here.
    """
    _, w = load()
    known = (args.from_ in w.items or args.from_ in w.findings
             or model.RUN_RE.match(args.from_ or ""))
    if not known:
        die("--from %r names nothing in the ledger. It must be an item id, a finding "
            "name, or a run like C40/run-3@full-578 — `from` IS the causal link, and a "
            "cause that resolves to nothing is not one." % args.from_)
    ev = {"seat": seat, "event": "spawn", "name": args.name,
          "kind": args.kind, "needs": args.needs, "spec": args.spec,
          "this_deployment": args.this_deployment}
    ev["for"] = args.for_
    ev["from"] = args.from_
    _emit(ev, w, quiet=True)
    print("%s spawned for %s, state proposed, caused by %s."
          % (args.name, args.for_, args.from_))
    print("items/%s.md has no prose yet. Write it when you have something to say; "
          "it can be claimed and started either way." % args.name)
    return 0


def cmd_needs(args, seat):
    """Set `needs` on an existing item.

    🔴 Until 2026-08-21 there was no way to do this: only `file` and `spawn` accepted
    `--needs`, so every migrated item rendered at the filing default and the whole
    game-state axis was dead. 38 of CHECK's 38 items claimed to be offline work while
    several wanted 100 in-game days or a bridge import.
    """
    _, w = load()
    _emit({"seat": seat, "event": "needs", "id": args.id, "to": args.to,
           "reason": args.reason}, w, quiet=True)
    print("%s now needs %s. Lifecycle untouched — this says WHEN it can be worked, "
          "not that anything is wrong." % (args.id, args.to))
    return 0


def cmd_retarget(args, seat):
    _, w = load()
    _emit({"seat": seat, "event": "retarget", "id": args.id, "to": args.to,
           "reason": args.reason}, w, quiet=True)
    print("%s now targets %s. Lifecycle untouched — this is a planning move."
          % (args.id, args.to))
    return 0


def cmd_seat(args, seat):
    _, w = load()
    _emit({"seat": seat, "event": "seat", "state": args.state,
           "reason": args.reason, "item": args.item, "note": args.note},
          w, quiet=True)
    print("%s is %s%s" % (seat, args.state,
                          " (%s)" % args.reason if args.reason else ""))
    if args.note:
        print("  handoff: %s" % args.note)
    return 0


def cmd_bridge(args, seat):
    _, w = load()
    state = {"take": "taken", "release": "released"}[args.action]
    _emit({"seat": seat, "event": "bridge", "state": state}, w, quiet=True)
    print("bridge %s by %s" % (state, seat))
    return 0


def sync_game_state(w, seat, announce=True):
    """Measure the game, and correct the record if the machine contradicts it.

    \U0001f534 OWNER, 2026-08-22 12:47: *"there should be precisely ONE place that variable
    is recorded and no more."* That place is the ledger, and this is the only thing that
    writes to it without him. It exists so that no seat ever again reports a disagreement
    between what is recorded and what is true \u2014 there is nothing to report, because
    the reading corrects the record as it takes it.

    Returns (state, reading, corrected_from) where corrected_from is None if nothing moved.
    """
    reading = probe.measure()
    corrected = probe.contradicts(w.game, reading)
    if corrected is None:
        return w.game, reading, None
    was = w.game
    _emit({"seat": seat, "event": "game", "state": corrected, "measured": True,
           "evidence": reading["evidence"]}, w, quiet=True)
    w.game = corrected
    if announce:
        sys.stderr.write("\u2699\ufe0f  game state corrected %s \u2192 %s (measured: %s)\n"
                         % (was, corrected, reading["evidence"]))
    return corrected, reading, was


def cmd_game(args, seat):
    _, w = load()

    # No state given: MEASURE. Any seat, any time, no announcement needed.
    if not getattr(args, "state", None):
        state, reading, was = sync_game_state(w, seat, announce=False)
        print("running   : %s   (%s)"
              % ("RUNNING" if reading["running"] else
                 "NOT RUNNING" if reading["running"] is False else "UNMEASURED",
                 reading["evidence"]))
        if was is None:
            print("recorded  : %s" % state)
        else:
            print("recorded  : %s  \u2192 corrected to %s, measured now" % (was, state))
        return 0

    ev = {"seat": seat, "event": "game", "state": args.state}
    note = (getattr(args, "note", None) or "").strip()
    if note:
        ev["text"] = note
    _emit(ev, w, quiet=True)
    print("game is %s" % args.state)
    if note:
        print("  note: %s" % note)
    if args.state != "UP":
        print("every --this-deployment flag is now cleared.")
    return 0


def cmd_admin(args, seat):
    _, w = load()
    _emit({"seat": seat, "event": "admin", "id": args.id, "reason": args.reason,
           "patch": args.patch}, w, quiet=True)
    print("admin correction recorded against %s. It is in the log forever, which is "
          "the point." % args.id)
    return 0


# ---------------------------------------------------------------------------
# artifact — the one door for a new game artifact
# ---------------------------------------------------------------------------
def cmd_artifact(args, seat):
    """`rimflow artifact accept <path> --kind dump|log|save|modlist [--official]`

    ⛔ DRY RUN unless `--apply`, like the importer and for the same reason: it
    registers an artifact and files work off it, and both are easier to review than to
    undo. ⛔ And it NEVER auto-fixes a dangling reference — that is a decision, not a
    repair. See `artifact.py`.
    """
    # The same dual-import shim as `model`/`priority` at the top of this file — a bare
    # relative import fails when cli.py is run as a SCRIPT, which is how every seat
    # runs it. See the try/except beside `from . import model, priority`.
    try:
        from . import artifact as art
    except ImportError:
        from rimflow import artifact as art
    if args.action != "accept":
        die("only `accept` exists so far")
    text, dangling, provided = art.accept(
        args.path, args.kind, official=args.official, by=seat.lower(),
        write=args.apply)
    print(text if args.full else "\n".join(text.splitlines()[:44]))
    if not args.apply:
        print("\nDRY RUN — nothing registered, nothing filed, no report written.")
        print("Re-run with --apply to commit this.")
    return 0


# ---------------------------------------------------------------------------
# sweep — LISTS, NEVER DELETES
# ---------------------------------------------------------------------------
def cmd_sweep(args, seat):
    if not args.transient:
        die("`sweep` needs --transient. It is the only sweep there is.")
    import time
    names = set()
    for line in git("ls-files", "TRANSIENT_*").splitlines():
        names.add(line)
    for n in os.listdir(model.ROOT):
        if n.startswith("TRANSIENT_"):
            names.add(n)
    if not names:
        print("no TRANSIENT_* files.")
        return 0
    print("%d TRANSIENT_* file(s). ⚠️ THIS LISTS ONLY — nothing here is deleted, ever."
          % len(names))
    rows = []
    for n in sorted(names):
        p = os.path.join(model.ROOT, n)
        try:
            age = (time.time() - os.path.getmtime(p)) / 86400.0
        except OSError:
            age = -1
        last = git("log", "-1", "--format=%h %ad %an", "--date=short", "--", n)
        rows.append((age, n, last or "(untracked — never committed)"))
    for age, n, last in sorted(rows, reverse=True):
        print("  %6s  %-34s %s"
              % ("%.1fd" % age if age >= 0 else "?", n, last))
    print("Deciding one is stale is a judgement. Read it, then delete it by hand.")
    return 0


# ---------------------------------------------------------------------------
# render / reindex — NOT MINE. render.py belongs to another agent.
# ---------------------------------------------------------------------------
def _render_module():
    try:
        try:
            from . import render                                # noqa: F401
        except ImportError:
            from rimflow import render                          # noqa: F401
        return render
    except ImportError:
        try:
            from rimflow import render                          # noqa: F401
            return render
        except ImportError:
            return None


def _delegate(fnname):
    """Hand the verb to render.py and get out of the way.

    ⚠️ `main(argv)` is preferred over the bare function so that render.py's OWN
    argument handling and OWN output format apply. Calling `render()` directly would
    make this file quietly responsible for how a render is invoked and printed, which
    is how a thin wrapper becomes a second implementation.
    """
    def run(args, seat):
        mod = _render_module()
        if mod is None:
            die("`%s` lives in rimflow/render.py, which does not exist yet — it is "
                "another agent's file and this CLI deliberately does not contain a "
                "second renderer. The ledger is unaffected; %s only rebuilds derived "
                "views from it." % (args.cmd, args.cmd))
        rest = list(getattr(args, "rest", None) or [])
        main_ = getattr(mod, "main", None)
        if callable(main_):
            rc = main_([args.cmd] + rest)
        else:
            fn = getattr(mod, fnname, None)
            if fn is None:
                die("rimflow/render.py exists but exposes neither main() nor %s(). Ask "
                    "its owner for the entry point; nothing was written." % fnname)
            rc = fn()
        return rc if isinstance(rc, int) else 0
    return run


# ---------------------------------------------------------------------------
# ARGUMENTS
# ---------------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(
        prog="rimflow",
        description="One master queue, derived from an append-only ledger. "
                    "`rimflow next --seat <SEAT>` is the only command you need to "
                    "start work.")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--seat", help="DECIDE|BUILD|CHECK|REP|OWNER. Beaten by "
                                       "RIMFLOW_SEAT; refused if it cannot be resolved.")
    common.add_argument("--target", default="v1",
                        help="active version the priority engine filters on (v1)")
    common.add_argument("--mode", help="afk suppresses items whose needs is `owner`")
    # 🔴 THE OWNER'S WORD IS THE AUTHORIZATION — his ruling, 2026-08-22:
    # *"I need to be able to simply tell you things as the owner and it's understood
    # that that agent now has owner authorization. I don't want to route through weird
    # python calls."* He was pasting `! RIMFLOW_SEAT=OWNER python3 …` lines to exercise
    # his own authority, which proved nothing except that he could paste.
    # 🔑 This is STRICTLY better evidence than the paste was: the ledger now carries
    # what he actually SAID, verbatim, instead of a command anyone could have typed.
    common.add_argument("--owner-said", dest="owner_said", metavar="\"…\"",
                        help="act as OWNER on his spoken instruction. Pass his words "
                             "VERBATIM; they are recorded on the event as the "
                             "authorization. Never paraphrase, never invent.")
    sub = p.add_subparsers(dest="cmd")

    def add(name, help_, fn, parents=(common,)):
        s = sub.add_parser(name, parents=list(parents), help=help_)
        s.set_defaults(fn=fn)
        return s

    add("next", "the one item to work now", cmd_next)

    s = add("show", "everything the ledger says about one item", cmd_show)
    s.add_argument("id")

    s = add("why", "why is this item not being offered", cmd_why)
    s.add_argument("id")

    s = add("file", "create work — for any seat, including another's", cmd_file)
    s.add_argument("id", help="THREE_DESCRIPTIVE_WORDS_#")
    s.add_argument("--for", dest="for_", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--kind", default="task")
    s.add_argument("--row", help="V1 milestone row; unrowed items sort LAST")
    s.add_argument("--target-field", dest="target_field", default="v1",
                   help="v1|v2 — what this item targets (not the filter)")
    s.add_argument("--needs", choices=model.NEEDS)
    s.add_argument("--spec", help="path to a draft spec, recorded as provenance")
    s.add_argument("--caused-by", dest="caused_by")
    # 🔑 owner, 2026-08-23: "make rimflow file ask - does this replace an existing item?"
    # Nine items were closed by hand at the bench that evening; THREE of them were alive
    # only because a successor took the work over and nobody went back. `supersede` already
    # existed and was simply never reached for - filing is the verb people know. So the ask
    # lives HERE, at the moment the successor is born, not in a rule anyone must remember.
    s.add_argument("--replaces", dest="replaces", metavar="ID",
                   help="this item takes over ID's work: supersede ID in the same act, "
                        "so the parent closes and names its successor")

    add("claim", "take ownership; always reaches `ready`",
        _simple("claim")).add_argument("id")
    add("start", "begin work; never refused for missing prose",
        _simple("start")).add_argument("id")

    s = add("close", "close it against a commit", cmd_close)
    s.add_argument("id")
    s.add_argument("--sha", help="defaults to git HEAD")

    s = add("block", "something is WRONG (this is not `needs`)",
            _simple("block", (("reason", "reason"), ("on", "on"))))
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    s.add_argument("--on", help="the item this waits on")

    s = add("unblock", "the wrong thing is fixed",
            _simple("unblock", (("reason", "reason"),)))
    s.add_argument("id")
    s.add_argument("--reason")

    s = add("verify", "record a RUN. Immutable; a fail stands forever", cmd_verify)
    s.add_argument("id")
    s.add_argument("--result", required=True, choices=("pass", "fail", "partial"))
    s.add_argument("--config", required=True, help="e.g. full-578 or min-13")
    s.add_argument("--evidence", help="path to the log, dump or screenshot")
    s.add_argument("--sha", help="defaults to git HEAD")

    s = add("finding", "name what a run found", cmd_finding)
    s.add_argument("--from", dest="from_", required=True,
                   help="ITEM/run-N@config")
    s.add_argument("--name", required=True, help="THREE_DESCRIPTIVE_WORDS_#")
    s.add_argument("--type", required=True)
    s.add_argument("--severity", required=True)
    s.add_argument("--id", help="host item; derived from --from when it is a run")

    s = add("spawn", "turn a finding into work, for any seat", cmd_spawn)
    s.add_argument("--from", dest="from_", required=True, help="a finding or run name")
    s.add_argument("--for", dest="for_", required=True)
    s.add_argument("--name", required=True, help="THREE_DESCRIPTIVE_WORDS_#")
    s.add_argument("--kind", default="task")
    s.add_argument("--needs", choices=model.NEEDS)
    s.add_argument("--spec")
    s.add_argument("--this-deployment", dest="this_deployment", action="store_true",
                   help="jumps the queue; cleared automatically when the game leaves UP")
    s.add_argument("--id", help="host item; derived from --from when possible")

    s = add("needs", "set WHEN an item can be worked (offline|deploy|game-up|bridge|"
            "harvest|owner)", cmd_needs)
    s.add_argument("id")
    s.add_argument("--to", required=True,
                   help="offline|deploy|game-up|bridge|harvest|owner")
    s.add_argument("--reason")   # optional since 2026-08-22 — nothing reads it

    s = add("retarget", "move it between v1 and v2 — a planning move", cmd_retarget)
    s.add_argument("id")
    s.add_argument("to", help="v1|v2")
    s.add_argument("--reason")   # optional since 2026-08-22 — nothing reads it

    s = add("reassign", "hand an item to another seat (DECIDE, or OWNER overriding)",
            _simple("reassign", (("to", "to"), ("reason", "reason"))))
    s.add_argument("id")
    s.add_argument("--to", required=True)
    s.add_argument("--reason")   # optional since 2026-08-22 — nothing reads it

    s = add("drop", "this will not be done", _simple("drop", (("reason", "reason"),)))
    s.add_argument("id")
    s.add_argument("--reason", required=True)

    s = add("supersede", "a better item replaces it",
            _simple("supersede", (("by", "by"), ("reason", "reason"))))
    s.add_argument("id")
    s.add_argument("--by", required=True)
    s.add_argument("--reason")

    s = add("note", "a line of context. Prose belongs in items/<ID>.md",
            _simple("note", (("text", "text"),)))
    s.add_argument("id")
    s.add_argument("--text", required=True)

    s = add("seat", "announce what this seat is doing", cmd_seat)
    s.add_argument("state", choices=("ready", "busy", "idle"))
    s.add_argument("--reason")
    s.add_argument("--item")
    # 🔑 The handoff. POLICY.md's 90% ritual names this flag; a fresh seat reads it out
    # of the ledger and resumes without re-deriving anything.
    s.add_argument("--note", help="one line: where you stopped. THIS is the handoff.")

    s = add("bridge", "CHECK only — two seats driving one game is unattributable",
            cmd_bridge)
    s.add_argument("action", choices=("take", "release"))

    s = add("game", "OWNER only — announce the game state", cmd_game)
    s.add_argument("state", nargs="?", choices=model.GAME_STATES,
                   help="omit to MEASURE the game and correct the record from it")
    # 🔑 GAME_STATE_HAS_NO_STAMPER_1's second half. The prose the old game.json
    # carried - what is left to do, where the blocker is, what this load is FOR -
    # had nowhere to go once the state moved into the ledger, so it was being lost
    # at exactly the moment it was most worth keeping. It is optional: a state
    # change with nothing to say should not have to invent something.
    s.add_argument("--note", default=None,
                   help="one line of context for this state change, e.g. what "
                        "the load is for or why it went down")

    s = add("admin", "OWNER only — an audited correction", cmd_admin)
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    s.add_argument("--patch", help="JSON of what should have been recorded")

    s = add("sweep", "list stale TRANSIENT_* files. LISTS ONLY", cmd_sweep)
    s.add_argument("--transient", action="store_true")

    s = add("artifact", "accept a new game artifact. DRY RUN unless --apply",
            cmd_artifact)
    s.add_argument("action", choices=["accept"])
    s.add_argument("path")
    s.add_argument("--kind", required=True,
                   choices=["dump", "log", "save", "modlist"])
    s.add_argument("--official", action="store_true",
                   help="freeze it as the design target. Owner only.")
    s.add_argument("--apply", action="store_true",
                   help="register it, write the report, file the item")
    s.add_argument("--full", action="store_true", help="print the whole report")

    s = add("render", "rebuild queue/*.md and board.json (owned by render.py)",
            _delegate("render"))
    s.add_argument("rest", nargs=argparse.REMAINDER,
                   help="passed straight through to render.py")
    s = add("reindex", "rebuild every derived view from the ledger (owned by render.py)",
            _delegate("reindex"))
    s.add_argument("rest", nargs=argparse.REMAINDER,
                   help="passed straight through to render.py")
    return p


READ_ONLY = ("show", "why", "sweep", "render", "reindex")


# \u26d4 Bare assent is not an instruction. These are the words that mean "I agree
# with what you just said" rather than "do this" — the whole class the `--owner-said`
# guard exists to refuse. A short INSTRUCTION ("game up", "drop it") is admitted.
ASSENT_ONLY = frozenset((
    "y", "n", "ok", "okay", "yes", "yep", "yeah", "yup", "sure", "fine", "go",
    "go ahead", "do it", "please", "please do", "approved", "agreed", "correct",
    "right", "confirmed", "sounds good", "good", "great", "perfect", "no", "nope",
))


def _norm_said(said):
    """Lowercase, strip punctuation and collapse space, so 'Yes!' == 'yes'."""
    return " ".join("".join(c for c in said.lower() if c.isalnum() or c.isspace()).split())


def main(argv=None):
    _bind_paths()
    p = build_parser()
    args = p.parse_args(argv)
    if not getattr(args, "cmd", None):
        p.print_help()
        return 1
    # `show`, `why` and `sweep` never write, so they must not refuse for want of a
    # seat — debugging the queue is exactly what you do when your window is misconfigured.
    if args.cmd in READ_ONLY:
        seat = (os.environ.get("RIMFLOW_SEAT") or getattr(args, "seat", None)
                or os.environ.get("AGENT_SEAT") or _role_file_seat() or "BUILD")
        seat = seat.strip().upper()
        if seat not in model.SEATS:
            seat = "BUILD"
    else:
        seat = resolve_seat(getattr(args, "seat", None))
    said = (getattr(args, "owner_said", None) or "").strip()
    if said:
        # ⛔ A quote too short to be a quote is not authorization. This is the only
        # guard: it stops `--owner-said yes` standing in for something he never said.
        # ⛔ A QUESTION IS NOT AN INSTRUCTION. Caught within a minute of shipping this
        # flag: REP dropped an item quoting the owner ASKING what he could knock out.
        # The quote must be him telling you to do THIS, not him talking nearby.
        if said.rstrip().endswith("?"):
            die("`--owner-said` must quote an INSTRUCTION, and %r is a question.\n\n"
                "The owner asking about a thing is not the owner authorizing it. Quote "
                "the words\nwhere he told you to act; if there are none, act as your "
                "own seat and say whose\ncall it was, or ask him.\n" % said[:80])
        # \U0001f534 OWNER, 2026-08-22: the floor used to be a blunt `len < 12`, and it
        # refused HIS OWN documented phrases — "game UP" is 7 characters and "game is
        # up", the example printed in CLAUDE.md, is 10. He said *"Simply do (1) right
        # now"*. \u26d4 The guard's REAL job was never length: it was to stop
        # `--owner-said yes` standing in for an instruction he never gave. So reject
        # bare ASSENT, which is him agreeing to something said elsewhere, and let a
        # short but complete instruction through.
        if _norm_said(said) in ASSENT_ONLY:
            die("`--owner-said` must quote the INSTRUCTION, not the agreement.\n%r is "
                "him assenting to something YOU said; the ledger would record your "
                "words as his.\n\nQuote the sentence that says what to do — "
                "'game up' is fine, 'yes' is not.\n" % said)
        seat = "OWNER"
        model.OWNER_SAID = said
    return args.fn(args, seat) or 0


if __name__ == "__main__":
    sys.exit(main())
