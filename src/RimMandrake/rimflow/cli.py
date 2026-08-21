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
import subprocess
import sys

try:                                                    # python3 -m rimflow.cli
    from . import model, priority
except ImportError:                                     # python3 .../rimflow/cli.py
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimflow import model, priority                 # noqa: F401

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


def _ctx(args):
    return {"mode": getattr(args, "mode", None) or os.environ.get("RIMFLOW_MODE"),
            "harvest_pending": bool(os.environ.get("RIMFLOW_HARVEST_PENDING"))}


# ---------------------------------------------------------------------------
# next — the command that matters
# ---------------------------------------------------------------------------
def cmd_next(args, seat):
    _, w = load()
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
        print("⚠️  %d spec-complete item%s ALSO waiting for %s to claim: %s%s"
              % (len(also), "" if len(also) == 1 else "s", seat,
                 ", ".join(i.id for i in also[:4]),
                 "" if len(also) <= 4 else ", +%d" % (len(also) - 4)))
        print("    filed for you by another seat. `rimflow claim <ID>` to take one.")
    return 0


def _claimable(w, seat, target="v1"):
    """-> [Item] this seat owns that are `proposed`, spec-complete and unblocked.

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
    out = [i for i in w.items.values()
           if i.owner == seat and i.state == "proposed" and not i.blocked
           and i.target in (None, target) and model._complete(i)]
    out.sort(key=lambda i: (not i.this_deployment, i.created_at or "", i.id))
    return out


def _offer_claimable(items, seat):
    it = items[0]
    print("nothing is CLAIMED, but %d spec-complete item%s waiting for %s to claim."
          % (len(items), "" if len(items) == 1 else "s", seat))
    print("")
    print("%s   %s" % (it.id, _scalars(it)))
    print(it.title or "(no title)")
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
        print("⚠️  %d proposed item(s) cannot be claimed because items/<ID>.md is "
              "missing sections:" % len(incomplete))
        for i in incomplete[:6]:
            print("      %-44s missing %s"
                  % (i.id, ", ".join("## " + m for m in model._missing(i))))
        print("    Whoever filed them owes the prose; until then nobody can work them.")
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
def cmd_file(args, seat):
    _, w = load()
    ev = {"seat": seat, "event": "file", "id": args.id, "title": args.title,
          "kind": args.kind, "row": args.row, "target": args.target_field,
          "needs": args.needs, "spec": args.spec, "caused_by": args.caused_by}
    ev["for"] = args.for_
    _emit(ev, w, quiet=True)
    print("%s filed for %s, state proposed." % (args.id, args.for_))
    miss = [s for s in ("spec", "verify", "criteria")
            if s not in {n.lower() for n, _ in read_prose(args.id)}]
    if miss:
        print("items/%s.md has no %s yet — worth adding, but it can be claimed and "
              "started as it is." % (args.id, " or ".join("## " + m for m in miss)))
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
        die("`close` requires --sha and git could not supply one. The sha is what makes "
            "a close checkable a year later; a close with no commit behind it is a claim.")
    _emit({"seat": seat, "event": "close", "id": args.id, "sha": sha}, w, quiet=True)
    print("%s closed at %s." % (args.id, sha))
    return 0


def cmd_verify(args, seat):
    _, w = load()
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


def cmd_game(args, seat):
    _, w = load()
    _emit({"seat": seat, "event": "game", "state": args.state}, w, quiet=True)
    print("game is %s" % args.state)
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
    s.add_argument("--reason", required=True)

    s = add("retarget", "move it between v1 and v2 — a planning move", cmd_retarget)
    s.add_argument("id")
    s.add_argument("to", help="v1|v2")
    s.add_argument("--reason", required=True)

    s = add("reassign", "hand an item to another seat (DECIDE only)",
            _simple("reassign", (("to", "to"), ("reason", "reason"))))
    s.add_argument("id")
    s.add_argument("--to", required=True)
    s.add_argument("--reason", required=True)

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
    s.add_argument("state", choices=model.GAME_STATES)

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
    return args.fn(args, seat) or 0


if __name__ == "__main__":
    sys.exit(main())
