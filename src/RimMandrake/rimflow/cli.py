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
import calendar
import json
import os
import re
import subprocess
import sys
import time

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
            # ⚠️ NEVER CLOBBER an override the caller already stamped. `cmd_bridge`
            # sets one for an owner handover or a forced take; a permission bypass
            # found here is a SECOND fact about the same event, and dropping either
            # is exactly the silent-loss this field exists to prevent.
            prior = ev.get("override")
            ev["override"] = ("%s; %s" % (prior, model.OVERRIDE_NOTICES[0])
                              if prior else model.OVERRIDE_NOTICES[0])
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
    # Render-on-write (owner, 2026-08-27): every mutation rewrites the queue views in
    # the same command, so a view can never be staler than the ledger. This replaced
    # the 60 s queue_publisher.sh loop and everything that existed to detect its
    # death. ~160 ms per event; best-effort — a render failure must never eat the
    # append that already happened, so it warns and moves on.
    try:
        try:
            from . import render as _render
        except ImportError:
            from rimflow import render as _render       # script invocation
        # 🔴 render.QUEUE/DERIVED/PREVIEW bind at import from model.STATE and
        # `_bind_paths()` never touches them — only model.EVENTS/model.ITEMS.
        # Without passing events_path/queue_root explicitly, a redirected
        # RIMFLOW_LEDGER (selftest_cli.py's whole point: "runs end-to-end
        # with no risk to the real one") still renders the REAL queue/*.md
        # from the synthetic test ledger. STATE root is derived the same way
        # model.write_bridge_file derives its own mirror target, and it
        # matches both the real layout (STATE/ledger/events.jsonl) and the
        # throwaway layout selftest_render.py builds by hand.
        state_root = os.path.dirname(os.path.dirname(model.EVENTS))
        s = _render.render(events_path=model.EVENTS, overwrite_queues=True,
                           queue_root=os.path.join(state_root, "queue"),
                           out_dir=os.path.join(state_root, "derived", "queue_preview"),
                           quiet=True)
        # quiet=True means render() never prints its own refusal (the census
        # guard against overwriting the queues from a shorter ledger) — _emit
        # ignoring the return value meant that refusal, which render.py's own
        # comments call "the whole safety property of this module", could
        # fire silently: every subsequent write would stop publishing the
        # queue views with nothing said, and both windows would keep reading
        # a frozen file.
        if s.get("refused"):
            sys.stderr.write("🔴 " + s["refused"] + "\n")
    except Exception as e:                                    # noqa: BLE001
        sys.stderr.write("⚠️  queue views not re-rendered (%s) — run "
                         "render.py --overwrite-queues by hand\n" % e)
    return ev


def git(*args):
    try:
        return subprocess.check_output(("git",) + args, cwd=model.ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except (subprocess.CalledProcessError, OSError):
        return ""


def head_sha():
    return git("rev-parse", "--short", "HEAD") or None


def _undocumented_work_warning(item_id):
    """-> a one-line warning, or None, for QUEUE_ITEM_FILES_DECAY_1's own gap:
    a commit that finishes an item's work is not required to touch
    items/<ID>.md, so the prose `show` just printed can read as "nothing
    happened here" while real, committed work already exists. Measured
    2026-09-02: BUILDING_THEFT_HAULER_1 and SETTLEMENT_VERBS_WAVE_1 were both
    fully built and committed the night before, then both nearly re-built
    from scratch by a later FOUNDRY pass (and a dedicated triage fork) that
    had no way to tell "done" from "unstarted" except `git log` by hand.

    Heuristic, not a structured item->source-path map (none exists): this
    repo's commit messages near-universally open with "ID: what happened"
    (checked against every commit cited by this session), so a substring
    search for "<item_id>:" across full commit messages finds them without
    needing to know WHERE an item's code lives. A commit body that happens to
    mention a different item this way is the rare false positive this
    advisory accepts — it never blocks anything, only tells `show`'s caller
    to look before assuming.
    """
    out = git("log", "-F", "--grep=%s:" % item_id, "--name-only", "--format=%x01%H")
    if not out:
        return None
    item_file = os.path.relpath(os.path.join(model.ITEMS, "%s.md" % item_id), model.ROOT)
    hits = []
    for rec in out.split("\x01")[1:]:
        lines = [ln for ln in rec.splitlines() if ln.strip()]
        if not lines:
            continue
        sha, files = lines[0], lines[1:]
        hits.append((sha, item_file in files))
    if hits and not any(touched for _, touched in hits):
        shas = ", ".join(sha[:8] for sha, _ in hits[:3])
        more = "" if len(hits) <= 3 else ", +%d more" % (len(hits) - 3)
        return ("%d commit(s) cite %s (%s%s) but NONE touch %s — the prose below "
                "may be stale. `git log --oneline -F --grep=\"%s:\"` before assuming "
                "unstarted." % (len(hits), item_id, shas, more, item_file, item_id))
    return None


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


def _ctx(args):
    return {"mode": (getattr(args, "mode", None) or os.environ.get("RIMFLOW_MODE")
                     or _mode_file()),
            "harvest_pending": bool(os.environ.get("RIMFLOW_HARVEST_PENDING"))}


# ---------------------------------------------------------------------------
# next — the command that matters
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# `next --bench` — TRIAGE AS A QUERY, not a fifth agent.
#
# 🔴 THE FIFTH "MANAGER" SEAT WAS REJECTED AND THE REASON IS ON FILE
# (`TRIM_VALIDATION_LAYERS_1`): it could not tell any seat what it took — messaging is
# off and hook-blocked — it only helped while the owner sat in its window, which is what
# BENCH already covers, and it was a fifth doctrine set to keep in sync. The valuable
# half was always the query. This is the query.
#
# ⚠️ SUPERSEDES ITS OWN SPEC. That item asked for "thrashing items (2+ reassignments)".
# Six hours later `facts/distress_signals.md` MEASURED that population and refuted the
# framing: reassignment COUNT is misleading — its top hit had **11 reassignments and
# closed in 1.0 h** — while DIRECTION is the whole signal. Upstream-reassigned items live
# 10.5 h against 1.5 h and close 26.9% against 72.9%. So this implements the measured
# coarse index, not the count.
#
# ⛔ REP AND THE OWNER ONLY, and that is not seniority. Every other thing rimflow prints
# measures the world; this one measures actions seats CHOOSE, so it is the one number
# that can be gamed — and penalising upstream reassignment would teach a seat to absorb
# mis-scoped work rather than hand it back, which is worse and invisible. A seat gets the
# underlying fact ("claimed 33 h, no commit"); it never gets a score to optimise.

BENCH_SEATS = ("BENCH", "OWNER")

# Upstream = a seat saying "this is not what I thought it was". Downstream is the
# conveyor working (0.55× — protective), so only these pairs count.
_UPSTREAM = {("CHECK", "BUILD"), ("CHECK", "DECIDE"), ("BUILD", "DECIDE")}


def _p90_by_kind(w, evs):
    """-> {kind: p90 hours} computed from items that CLOSED, at run time.

    🔑 `distress_signals.md` is explicit that these must NOT be hard-coded: they vary 7×
    across kinds (a ruling at 20 h is in trouble; a check at 40 h is normal) and
    hard-coding "guarantees they are wrong within a fortnight".
    """
    from collections import defaultdict
    lives = defaultdict(list)
    for it in w.items.values():
        if it.state != "done" or not it.created_at or not it.history:
            continue
        last = evs[it.history[-1]].get("ts")
        if not last:
            continue
        # ⚠️ Either stamp being unreadable poisons the p90 for a whole KIND, which then
        # scores every item of that kind. `_epoch`'s 0.0 is 1970: an unreadable
        # `created_at` alone yields a ~495,000 h "life" that sails past the `h >= 0`
        # guard and lands in the percentile.
        e_last, e_made = _epoch(last), _epoch(it.created_at)
        if not e_last or not e_made:
            continue
        h = (e_last - e_made) / 3600.0
        if h >= 0:
            lives[it.kind or "task"].append(h)
    out = {}
    for kind, xs in lives.items():
        xs.sort()
        out[kind] = xs[min(len(xs) - 1, int(round(0.9 * (len(xs) - 1))))]
    return out


def _epoch(ts):
    import calendar, time
    try:
        return calendar.timegm(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
    except (ValueError, TypeError):
        return 0.0


def _age_hours(ts, now):
    """Hours between `ts` and `now`, or None if the stamp is unreadable.

    🔴 NEVER SUBTRACT `_epoch` DIRECTLY IN A SCORE. Its failure value is 0.0, which is
    1970, so one malformed `ts` anywhere in the ledger became an age of ~495,000 h and
    forced a distress score onto whichever item owned it — silently reordering the
    queue with nothing on screen to say why. Every age used for scoring goes through
    here, and callers treat None as "no evidence", exactly as `_idle_seconds` does.
    """
    e = _epoch(ts)
    if not e:
        return None
    return (now - e) / 3600.0


def _distress(it, evs, p90, now):
    """-> (score, [reasons]) on the measured coarse index. ≥3 is the believe-it line."""
    score, why = 0, []

    if it.blocked:
        age = _age_hours(_last_ts(it, evs, "block"), now)
        if age is not None and age > 24:
            score += 3
            why.append("blocked %.0f h, unresolved" % age)
        else:
            score += 1
            why.append("blocked")

    if it.needs == "owner":
        score += 2
        why.append("needs the owner (4.26×)")
    elif it.needs in ("game-up", "bridge", "harvest", "deploy"):
        score += 1
        why.append("needs %s" % it.needs)

    up = 0
    prev = None
    for i in it.history:
        ev = evs[i]
        if ev.get("verb") == "reassign" or ev.get("event") == "reassign":
            to_ = ev.get("to") or ev.get("for")
            # ⚠️ `reassign` records no `from` — 0 of 73, and the fact file names this as
            # the one line that would sharpen the whole index. Until it does, direction
            # is INFERRED from the previous owner, and an item whose first event is a
            # reassign has no previous owner to infer from.
            if prev and (prev, to_) in _UPSTREAM:
                up += 1
            prev = to_ or prev
        elif ev.get("for") or ev.get("seat"):
            prev = ev.get("for") or prev
    if up:
        score += 2 * up
        why.append("%d upstream reassign%s (2.28×)" % (up, "" if up == 1 else "es"))

    if it.created_at:
        age = _age_hours(it.created_at, now)
        line = p90.get(it.kind or "task")
        if line and age is not None and age > line:
            score += 2
            why.append("%.0f h old, p90 for a %s is %.0f h" % (age, it.kind or "task", line))

    notes = commits = 0
    for i in it.history:
        ev = evs[i]
        if ev.get("event") == "note" or ev.get("verb") == "note":
            notes += 1
        if ev.get("sha"):
            notes, commits = 0, commits + 1
    if notes >= 2:
        score += 2
        why.append("%d notes since the last commit — talk without work (3.20×)" % notes)

    if it.state == "doing":
        claimed = _last_ts(it, evs, "claim", "start")
        if claimed and not commits:
            age = _age_hours(claimed, now)
            if age is not None and age > 24:
                score += 2
                why.append("claimed %.0f h ago, no commit since" % age)

    if any(evs[i].get("ownerSaid") or evs[i].get("override") for i in it.history):
        score += 1
        why.append("the owner had to intervene")

    return score, why


def _last_ts(it, evs, *verbs):
    for i in reversed(it.history):
        ev = evs[i]
        if (ev.get("verb") in verbs) or (ev.get("event") in verbs):
            return ev.get("ts")
    return it.created_at


def cmd_bench(args, seat):
    """The BENCH scan as a query. Both halves, always — he should never have to
    remember which phrase gets which."""
    if seat not in BENCH_SEATS:
        die("`next --bench` is BENCH's and the owner's, and that is not seniority.\n"
            "  It scores actions SEATS CHOOSE, so it is the one metric that can be\n"
            "  gamed — penalising upstream reassignment would teach a seat to absorb\n"
            "  mis-scoped work rather than hand it back. You get the underlying fact\n"
            "  (`rimflow why <ID>`), never the score. facts/distress_signals.md.")
    evs, w = load()
    import time
    now = time.time()
    p90 = _p90_by_kind(w, evs)
    open_ = [i for i in w.open_items() if not args.target or i.target == args.target]

    print("(game %s, bridge %s)  %d open" % (w.game, w.bridge_holder or "free", len(open_)))

    per = {}
    for it in open_:
        per.setdefault(it.owner or "unassigned", []).append(it)
    print("")
    for who in sorted(per):
        rows = per[who]
        game = sum(1 for i in rows if i.needs in ("game-up", "bridge", "harvest", "deploy"))
        him = sum(1 for i in rows if i.needs == "owner")
        print("%-11s %2d open   %2d need the game   %2d need him"
              % (who, len(rows), game, him))

    ripe = [i for i in open_
            if not i.blocked and i.needs == "offline" and i.state in ("proposed", "ready")]
    print("\nRIPE — unblocked, offline, would move the moment someone took it: %d" % len(ripe))
    for it in ripe[:10]:
        print("  %-44s %-9s %s" % (it.id[:44], it.owner or "unassigned", (it.title or "")[:60]))
    if len(ripe) > 10:
        print("  ... +%d more" % (len(ripe) - 10))

    scored = []
    for it in open_:
        sc, why = _distress(it, evs, p90, now)
        if sc >= 3:
            scored.append((sc, it, why))
    scored.sort(key=lambda r: -r[0])
    # ⛔ Never more than five, ranked. A longer list is a dump, and a dump is what the
    # briefing exists instead of.
    print("\nIN TROUBLE — coarse index ≥3 (31% recall, 42.9% precision, 5.22× lift).")
    print("🔑 When it fires, believe it. When it does not, that is NOT safety.")
    for sc, it, why in scored[:5]:
        print("  [%d] %-40s %s" % (sc, it.id[:40], (it.title or "")[:52]))
        print("      %s" % "; ".join(why))
    if not scored:
        print("  nothing scores ≥3.")

    needs_him = [i for i in open_ if i.needs == "owner"]
    print("\nNEEDS HIM — %d" % len(needs_him))
    for it in needs_him[:8]:
        print("  %-44s %s" % (it.id[:44], (it.title or "")[:60]))
    if len(needs_him) > 8:
        print("  ... +%d more" % (len(needs_him) - 8))
    print("\n⚠️  Every item above gets TWO clauses when you relay it — DO: and DON'T:.")
    print("    The DON'T clause is the half that decides, and the half easy to leave out.")
    return 0


def cmd_next(args, seat):
    if getattr(args, "bench", False):
        return cmd_bench(args, seat)
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
    # 🔑 A bridge item is now offered while the lock is FREE, so the offer has to say
    # how to take it. Without this the seat is handed live work and no way to start it,
    # which is the same stranding in a friendlier costume.
    if it.needs == "bridge" and not w.bridge_holder:
        print("⚠️  this item needs the bridge and nobody holds it — take it first:")
        print("      rimflow bridge take        (and `rimflow bridge release` after)")
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
                "criteria": "(nobody said what a correct outcome looks like)"}[m]))
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
    if not it.closed_sha:
        undoc = _undocumented_work_warning(it.id)
        if undoc:
            print("⚠️  %s" % undoc)

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
    # 🔴 REGULAR HUMAN PLAY IS THE DEFAULT VALIDATION — owner, 2026-08-27. BUILD produces
    # NOTHING for CHECK automatically: not on finishing, not on deploying, not "so it gets
    # looked at". One thing earns a live check — a NEW or significantly changed MECHANISM
    # that has never once been observed running.
    # ⚠️ A PROMPT, NOT A GATE, and that is the ruling's own shape: the same conversation
    # DROPPED the proposal to enforce this in `file`, because the item it belongs to exists
    # to REDUCE gates. A refusal here would also be wrong on the merits — the exception is
    # real and only the filer can tell whether it applies.
    if args.needs in ("bridge", "game-up"):
        print("")
        print("🔴 A live check is owed only to a mechanism never once observed running —")
        print("   the owner playing is the default validation. Answer in one line, in the")
        print("   item: which NEW mechanism has never been seen? ⚠️ The MECHANISM, not this")
        print("   instance — a 49th pawnkind built like the other 48 has been observed. A")
        print("   roster, a stat, a texPath, what a patch matched: offline, close it yourself.")
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
        # `drop` and `supersede` end an item just as `close` does, and anything waiting on
        # it is just as stranded — more so, since a dropped blocker will never deliver.
        if verb in ("drop", "supersede"):
            _announce_unblocks(args.id)
        return 0
    return run


def _announce_unblocks(target):
    """Name the items whose live block waits on `target`, now that `target` is terminal.

    🔴 A BLOCK NEVER LIFTS ITSELF. `block --on X` records the dependency and nothing ever
    reads it backwards, so an item can wait on a blocker that finished days ago and no
    signal is produced. Measured 2026-08-24: `WEAPON_MONEY_ROLL_NOT_CEILING_1` sat blocked
    43 h on `BARE_HANDS_REMEASURE_AFTER_LOAD_1`, which had been `done` for 15 of them. The
    dependency was in the ledger the whole time; nobody was ever told.

    ⛔ Deliberately does NOT auto-unblock. The blocker closing is EVIDENCE that the block
    may be stale, never proof — a blocker can close `dropped`, or close without delivering
    what the blocked item was actually waiting for. The seat still confirms. This only
    makes the information arrive at the one moment it is free.
    """
    try:
        st = model.replay(model.read(model.EVENTS))
    except Exception:
        return
    waiting = [it for it in st.items.values()
               if getattr(it, "blocked", False)
               and getattr(it, "blocked_on", None) == target
               and it.id != target]
    if not waiting:
        return
    print("")
    print("🔑 %d item(s) are BLOCKED ON %s, which just went terminal:"
          % (len(waiting), target))
    for it in waiting:
        print("   %s  (%s)" % (it.id, it.state))
        print("     %s" % (it.blocked_reason or "")[:140])
    print("   If %s delivered what they were waiting for, lift it — they will not lift"
          % target)
    print("   themselves, and nothing else will ever tell you:")
    for it in waiting:
        print("     python3 src/RimMandrake/rimflow/cli.py unblock %s --reason \"%s "
              "closed\"" % (it.id, target))


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
    _announce_unblocks(args.id)
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


def _idle_seconds(ts):
    """Seconds since an ISO ledger timestamp, or None if there is no readable one.

    ⚠️ Parses through `_epoch` — ONE parser for one timestamp format. This used to
    carry its own `strptime` with a stricter pattern (a trailing `Z` required) and a
    different failure value, so a change to the ledger's stamp format could silently
    move staleness behaviour with nothing to see near the edit. `_epoch` answers 0.0
    for an unreadable stamp, which is 1970 rather than an idle time; that becomes
    None here, which is what every caller already reads as "no evidence the holder
    is alive" — so the failure semantics are unchanged, only the parser is shared.
    """
    if not ts:
        return None
    e = _epoch(ts)
    if not e:
        return None
    return max(0, int(time.time() - e))


def _mirror_from_ledger(actor, note=None):
    """Rewrite the BRIDGE mirror from a FRESH replay, and answer who the ledger says holds it.

    🔴 THE MIRROR IS WRITTEN FROM THE LEDGER, NEVER FROM INTENT. Every branch below used
    to mirror the holder it had just decided on — so a take that lost a race appended
    its event (harmless: the ledger's last event wins) and then wrote ITS OWN name into
    the file, leaving the one glanceable line naming a different window than the ledger.
    `bridge who` re-derived correctly, but only for someone already doubting the answer,
    and a mirror nobody can believe at a glance is the whole point thrown away.

    🔑 This is a mirror fix, not a lock: it never refuses a take, in keeping with the
    ruling that this system errs toward ALLOWING (owner, 2026-09-02). The loser of a
    race is told who won; it is not told no.
    """
    _, w3 = load()
    model.write_bridge_file(w3.bridge_holder, actor, w3.bridge_purpose,
                            w3.bridge_since, note=note)
    return w3.bridge_holder


def cmd_bridge(args, seat):
    _, w = load()
    holder, since, purpose = w.bridge_holder, w.bridge_since, w.bridge_purpose

    # ⛔ `to` is a `give`-only positional that argparse accepts for every action.
    # `rimflow bridge take BOGUS --for x` used to exit 0 and print success with the
    # word silently discarded. A target nobody reads is a typo that looks like it
    # worked, so refuse it here — argparse cannot make one positional conditional on
    # another without a subparser per action.
    if args.to and args.action != "give":
        die("`bridge %s` takes no target, and %r was about to be ignored.\n"
            "  a target is for `bridge give`:  rimflow bridge give BENCH|FOUNDRY|free\n"
            "  what you probably meant:        rimflow bridge %s --for \"<what for>\""
            % (args.action, args.to, args.action))

    if args.action == "who":
        # Re-derived from the ledger, so this answer is true even when the mirror is not.
        model.write_bridge_file(holder, None, purpose, since)
        if not holder:
            print("bridge FREE — take it:  rimflow bridge take --for \"<what for>\"")
        else:
            idle = _idle_seconds(w.last_seen.get(holder))
            print("bridge held by %s since %s%s%s"
                  % (holder, since or "?",
                     ("  for: " + purpose) if purpose else "",
                     ("  (idle %d min)" % (idle // 60)) if idle is not None else ""))
        return 0

    if args.action == "give":
        # 🔴 THE OWNER'S OWN SWITCH. He is not a seat and does not queue behind one:
        # `bridge give FOUNDRY` moves it, `bridge give free` clears it, and both
        # windows see the answer in the same file they already read.
        #
        # 🔑 THE EVENT CARRIES WHO DID IT, not just the mirror. A `give` is emitted
        # under the TARGET window's seat, because `_apply` reads `seat` as the new
        # holder and the owner is not a window — which made an owner handover
        # byte-identical to that window taking the bridge itself, with the real story
        # only in `write_bridge_file(note=)`, a file the next bridge call overwrites.
        # `override` is the field this system already uses for "a rule was crossed on
        # purpose, and here is which one" (see `_emit` and `model._may`), so it is the
        # field used here too rather than a third shape. `--owner-said` still stamps
        # `ownerSaid` alongside it, from `_emit`, unchanged.
        # 🔴 THE OWNER GATE. `give` emits under the TARGET window's seat so `_apply`
        # records the right holder — which means `model._may` sees BENCH/FOUNDRY, never
        # OWNER, and never fires. So this branch had NO permission check at all: any
        # window could run `bridge give` and write "the OWNER handed the bridge to X"
        # into an append-only ledger, bypassing staleness and `--force` on the way.
        # ⚠️ Stamping `override` here (2026-09-02) is what made that forgery DURABLE —
        # it put a false claim in the one field this system treats as evidence of a
        # deliberate crossing. Caught in review the same day. The gate is the fix; the
        # stamp is only honest behind it.
        if seat != "OWNER":
            die("`bridge give` is the OWNER's switch, and you are %s.\n\n"
                "It writes his name onto a permanent ledger event, so a window may not "
                "run it —\nnot even to hand the bridge over politely.\n\n"
                "  take it yourself   rimflow bridge take --for \"<what for>\"\n"
                "  holder still awake rimflow bridge take --force --for \"<what for>\"\n"
                "  release your own   rimflow bridge release\n\n"
                "If HE told you to move it, quote him and it is recorded as his:\n"
                "  rimflow bridge give <seat> --owner-said \"<his verbatim words>\""
                % seat)
        to = (args.to or "").upper()
        if to in ("FREE", "NOBODY", "NONE"):
            _emit({"seat": holder or seat, "event": "bridge", "state": "released",
                   "override": "the OWNER cleared the bridge%s"
                               % (" off %s" % holder if holder else "")}, w, quiet=True)
            _mirror_from_ledger("OWNER", note="cleared by the owner")
            print("bridge FREE — the owner cleared it")
            return 0
        if to not in ("BENCH", "FOUNDRY"):
            die("give it to BENCH, FOUNDRY, or `free`. Got %r." % args.to)
        ev = {"seat": to, "event": "bridge", "state": "taken",
              "override": "the OWNER handed the bridge to %s%s"
                          % (to, " from %s" % holder if holder and holder != to else "")}
        if args.purpose:
            ev["purpose"] = args.purpose
        _emit(ev, w, quiet=True)
        _mirror_from_ledger("OWNER", note="handed over by the owner")
        print("bridge -> %s (the owner said so)" % to)
        return 0

    if args.action == "release":
        # ⚠️ `_apply` clears the holder for ANY `released` event, whoever sent it — so a
        # window can free a lock it does not hold. That stays ALLOWED, deliberately:
        # this system errs toward freeing a wedged bridge, never toward mutual lockout.
        # What was wrong is that it happened UNRECORDED. Stamp it, like every other
        # crossing (review finding, 2026-09-02).
        ev = {"seat": seat, "event": "bridge", "state": "released"}
        if holder and holder != seat:
            ev["override"] = "released the bridge out from under %s" % holder
        _emit(ev, w, quiet=True)
        _mirror_from_ledger(seat)
        if holder and holder != seat:
            print("bridge released by %s — it was held by %s, and that is on the event"
                  % (seat, holder))
        else:
            print("bridge released by %s — it is now FREE for the other window" % seat)
        return 0

    # take. 🔑 ERR ON THE SIDE OF ALLOWING (owner, 2026-09-02). One driver at a time is
    # about attributability, not about ownership, and the expensive failure here has
    # never been two drivers — it is MUTUAL LOCKOUT: a window that crashed or ran out
    # of context holds the lock forever and the other sits idle. So a take is refused
    # ONLY while the holder is demonstrably alive (an event inside the staleness
    # window), and even then the refusal hands over `--force` rather than a dead end.
    if holder in (None, seat):
        granted, why = True, None
    else:
        idle = _idle_seconds(w.last_seen.get(holder))
        if args.force:
            granted, why = True, "forced"
        elif idle is None or idle >= model.BRIDGE_STALE_SECONDS:
            granted, why = True, "%s went quiet%s" % (
                holder, (" for %d min" % (idle // 60)) if idle is not None else "")
        else:
            die("bridge is held by %s and they are still working (last event %d min "
                "ago%s).\n"
                "  wait      — check again with: rimflow bridge who\n"
                "  or take it — rimflow bridge take --force --for \"<what for>\"\n"
                "It frees on its own after %d min of silence, and a wedged bridge is "
                "stuck, not crashed."
                % (holder, idle // 60,
                   ("; for: " + purpose) if purpose else "",
                   model.BRIDGE_STALE_SECONDS // 60))
    ev = {"seat": seat, "event": "bridge", "state": "taken"}
    if args.purpose:
        ev["purpose"] = args.purpose
    # 🔑 A take that CROSSED SOMEONE goes on the event, not only into the mirror.
    # Without this, `--force` while the holder was still working produced a ledger
    # line indistinguishable from an ordinary uncontested take, and `events.jsonl` —
    # this module's sole source of truth — could never answer "did that take cut
    # across a live window". Same field as the owner override above, deliberately.
    if why:
        ev["override"] = (
            "took the bridge with --force while %s still held it" % holder
            if args.force else "took the bridge: %s" % why)
    # 🔴 RE-DERIVE THE HOLDER RIGHT BEFORE WRITING. `granted` above was decided
    # against the world `load()` read at the TOP of this function, and nothing
    # holds a lock across that decision — two windows racing `bridge take` at
    # the same instant could both see `holder is None`, both compute
    # `granted=True`, and both append a "taken" event, the exact double-driver
    # failure this whole mechanism exists to prevent. This does not make the
    # check-then-write atomic (that needs a lock held across the full decision,
    # which is a larger change than this review pass should make to the core
    # ledger primitives) — but it collapses the race window from "the time
    # between two windows' load() calls" down to "the time between this
    # re-check and _emit's own write", which is what actually matters: the
    # loser of the original race now sees the winner's already-recorded event
    # here and backs off with a clear message, rather than silently colliding.
    if not args.force:
        _, w2 = load()
        fresh_holder = w2.bridge_holder
        if fresh_holder not in (None, seat) and fresh_holder != holder:
            die("bridge was just taken by %s (a moment ago) — someone else won this race.\n"
                "  check again    rimflow bridge who\n"
                "  cut across it  rimflow bridge take --force --for \"<what for>\""
                % fresh_holder)
    _emit(ev, w, quiet=True)
    won = _mirror_from_ledger(
        seat, note=("taken from %s: %s" % (holder, why)) if why else None)
    if won != seat:
        # A take landed between our re-check above and our own append. Both events are
        # in the ledger, the later one holds, and the mirror now says so.
        print("bridge is held by %s — they took it in the same instant you did.\n"
              "  your take IS on the ledger; theirs landed after it, so it stands.\n"
              "  cut across it  rimflow bridge take --force --for \"<what for>\"" % won)
        return 0
    print("bridge taken by %s%s" % (seat, ("  (%s)" % why) if why else ""))
    if not args.purpose:
        print("  tip: --for \"<what for>\" tells the other window whether to wait.")
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
    # \u2b50 `seat` here is OWNER whenever broadcast.py is the caller, because it forces
    # RIMFLOW_SEAT — the event says WHOSE authority the state change carries, which is
    # always his. `ranBy` says whose HANDS were on it, which is a different question and
    # the one nobody could answer on 2026-08-25. Absent when the owner ran it himself.
    ran_by = (os.environ.get("RIMFLOW_RAN_BY") or "").strip().upper()
    if ran_by and ran_by != seat:
        ev["ranBy"] = ran_by
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
    # Transient/ is where transient output lives as of 2026-08-27. The directory is
    # gitignored, so `git ls-files` can no longer find any of it — walk the disk.
    # README.md is the convention itself and is never swept.
    tdir = os.path.join(model.ROOT, "Transient")
    if os.path.isdir(tdir):
        for n in os.listdir(tdir):
            if n != "README.md" and not n.startswith("."):
                names.add(os.path.join("Transient", n))
    # Legacy: root-level TRANSIENT_* from before the move. Kept so a stray one is
    # still reported rather than becoming invisible.
    for line in git("ls-files", "TRANSIENT_*").splitlines():
        names.add(line)
    for n in os.listdir(model.ROOT):
        if n.startswith("TRANSIENT_"):
            names.add(n)
    if not names:
        print("no transient files.")
        return 0
    print("%d transient file(s). ⚠️ THIS LISTS ONLY — nothing here is deleted, ever."
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
    common.add_argument("--seat", help="BENCH|FOUNDRY|OWNER (legacy seats replay only). "
                                       "Beaten by RIMFLOW_SEAT; refused if unresolvable.")
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

    s = add("next", "the one item to work now", cmd_next)
    s.add_argument("--bench", action="store_true",
                   help="REP/OWNER only: the whole board triaged — per-seat "
                        "counts, RIPE, IN TROUBLE, and what needs him")

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

    s = add("reassign", "hand an item to the other window (BENCH, or OWNER overriding)",
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

    s = add("bridge", "one driver at a time — two windows driving one game is unattributable",
            cmd_bridge)
    s.add_argument("action", choices=("take", "release", "who", "give"))
    s.add_argument("to", nargs="?",
                   help="give only: BENCH | FOUNDRY | free")
    s.add_argument("--for", dest="purpose",
                   help="one line: what you are driving it FOR. The other window reads "
                        "this to judge whether to wait or go do something else.")
    s.add_argument("--force", action="store_true",
                   help="take it even though another window holds it and is awake. "
                        "Records that you did.")

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

    s = add("render", "rebuild queue/*.md (owned by render.py)",
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
