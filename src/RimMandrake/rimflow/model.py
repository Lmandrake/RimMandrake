#!/usr/bin/env python3
"""rimflow/model.py — the event ledger, and the only thing allowed to interpret it.

WHAT THIS REPLACES AND WHY
==========================
Six hand-edited markdown queues, 827 KB across 167 items, four seats sharing one
working tree. Measured 2026-08-20: 68 of 142 items carried a `state:` no tool could
parse, `state: done` had been written three times in the project's history while 116
items had actually closed, and the board reported 0 done and 0 blocked. Items did not
get closed, they got deleted — so the numerator could never rise while the denominator
shrank.

None of that was carelessness. It is what a **shared editable file** does when several
writers each hold a partial view: every edit is a read-modify-write over someone else's
state, and the last writer silently wins.

So the truth moves to an **append-only event log**, and every view is derived from it.

    THE LEDGER IS THE TRUTH. Everything else — queue/<SEAT>.md, the board, this
    module's own `Item` objects — is a projection that can be thrown away and rebuilt.

🔴 WHY APPENDING NEEDS A LOCK HERE, AND THE PLAN'S ARGUMENT WAS WRONG
====================================================================
The design's stated safety argument was: on Linux a `write()` to a file opened
`O_APPEND` is atomic below `PIPE_BUF` (4096 bytes), so four seats can append at once
with no coordination. That is true — **on a local filesystem.**

⛔ **This repo is not on one.** `/mnt/d` is a **9p / DrvFs** mount (WSL2 talking to a
Windows drive), and 9p does not serialise concurrent writes. Measured 2026-08-20,
12 processes × 250 events of ~160 bytes each, run twice:

    filesystem            lines written   distinct events   torn lines
    /tmp   (tmpfs)          3000 / 3000      3000 / 3000          0
    /mnt/d (the repo, 9p)    857 / 3000       502 / 3000        355
                             657 / 3000       496 / 3000        161

**Five of every six events vanished, and hundreds of lines were torn in half** — in
the one file that is supposed to be the truth, on the filesystem the repo actually
lives on. The PIPE_BUF argument was quoted from POSIX and never run here.

✅ **`flock` fixes it completely**: 3000/3000, zero torn, twice, at ~2 ms per event.
Isolated further — flock alone is sufficient and re-seeking under the lock changes
nothing, so the failure is that 9p does not serialise the *writes*, not that it
mishandles the append offset.

⚠️ **`flock` is ADVISORY.** It only protects against writers that also take it, which
means `append()` below is the ONLY sanctioned way to write this file. A shell `>>`,
an editor, or any other appender bypasses the lock and can still tear a line.

🔑 The PIPE_BUF ceiling is KEPT anyway, and not as superstition: it bounds an event to
one plausible write, keeps prose out of the ledger, and preserves the no-lock
guarantee for anyone who later moves this to ext4. Prose belongs in `items/<ID>.md`.

⚠️ If the repo ever moves to a native Linux filesystem, or to NFS/SMB, re-run
`selftest_concurrency.py` **in the repo** before trusting anything here. That test's
first version defaulted to `tempfile.mkdtemp()`, which is `/tmp`, and passed 3600/3600
while the real filesystem was losing 83% of writes — a green test measuring the wrong
disk.

NO FIELD EXISTS TWICE
=====================
`items/<ID>.md` holds **prose only** — spec, verify, criteria, notes — and no
front-matter, no `state:`, no title. Every scalar lives in the ledger. A field cannot
drift out of sync with itself if it exists in exactly one place, and drift between two
copies of one field is the single failure this whole design is aimed at.

Stdlib only, and no daemon. Everything is a file in git.
"""
import copy
import fcntl
import json
import os
import re
import time

# 🔴 EVERY PATH BELOW IS RESOLVED AT CALL TIME, NEVER BOUND AS A DEFAULT ARGUMENT.
# `def read(path=EVENTS)` binds the production ledger at import, so reassigning
# `model.EVENTS` — which is exactly what a test does — silently leaves read() and
# append() pointed at the real, append-only file. Worse, `check()` calls `read()` with
# no argument, so a redirected test would have replayed production state and, on any
# write path, appended to it. There is no undo for that file. Found 2026-08-20 by the
# CLI's selftest, which had to rebind `read.__defaults__` to work around it.
# ⛔ Do not "simplify" these back to default arguments.
PIPE_BUF = 4096
ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STATE = os.path.join(ROOT, "infrastructure", "state")
LEDGER = os.path.join(STATE, "ledger")
EVENTS = os.path.join(LEDGER, "events.jsonl")
ITEMS = os.path.join(STATE, "items")

# BENCH and FOUNDRY are the live windows (redesign #4, 2026-08-27). The four retired
# seats stay listed so the ledger's history replays and legacy items keep their owners.
SEATS = ("BENCH", "FOUNDRY", "OWNER", "DECIDE", "BUILD", "CHECK", "REP")

# Item lifecycle. `proposed` means "filed, not yet taken". 🔴 It is NO LONGER a
# completeness gate — the owner removed that on 2026-08-21 (see `start`). An item may be
# claimed and started with no spec, verify or criteria at all.
STATES = ("proposed", "ready", "doing", "done", "dropped", "superseded")

# ⚠️ `blocked` is NOT a state. It is a flag, because an item can be blocked while
# proposed, ready or doing, and collapsing it into the state enum is what made the old
# queues unable to say "ready, but waiting on an answer". Same for `needs`.
NEEDS = ("offline", "deploy", "game-up", "bridge", "harvest", "owner")

# 🔑 `needs` is the coupling between the game and the queue, and it is a DIFFERENT
# axis from `blocked`. blocked means something is WRONG. needs means the WINDOW IS
# CLOSED. The old queues wrote both into one prose field, so the board could read
# neither, and "waiting for the game to come up" was indistinguishable from "broken".
# 🔴 FIVE STATES, NOT FOUR. `GOING_DOWN` was missing until 2026-08-20, which meant the
# OWNER COULD NOT ANNOUNCE A STATE HIS OWN DOCTRINE REQUIRES — `rimflow game GOING_DOWN`
# was refused outright, against `infrastructure/GAME_STATE_WORKFLOW.md`, which is a
# permanent doctrine file every seat is bound by.
#
# ⚠️ It is not a synonym for DOWN and collapsing them loses the only thing it says: the
# game is STILL UP and the window is closing. CHECK drops postponable offline work and
# runs live items only. In DOWN the game is gone and everyone is offline.
GAME_STATES = ("DOWN", "DEPLOYING", "LOADING", "UP", "GOING_DOWN")

# The item-ID grammar, and the ONLY place it is written down. It admits the
# THREE_DESCRIPTIVE_WORDS_# form (underscores, digits) and the legacy B58 / D5 form,
# which is why legacy items still close under their own number.
# 🔑 It is also the `Closes:` trailer grammar: `importer.py` walks those trailers out of
# git, and a name this regex rejects is a trailer nothing will ever match.
# ⛔ Do not restate this in a doctrine file. POLICY.md and CLAUDE.md both once named
# `derive_matrix.py` as the authority here; its CLI is superseded for the generated
# queues, and prose kept saying otherwise for days after the code moved.
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
# A run is the ONE exception to "no opaque IDs", and it is never seen alone.
RUN_RE = re.compile(r"^(?P<item>[A-Za-z][A-Za-z0-9._-]*)/run-(?P<n>\d+)@(?P<config>[\w.-]+)$")


class LedgerError(Exception):
    """Base for every refusal. These are REFUSALS, not crashes: each one names a rule."""


class EventTooLargeError(LedgerError):
    pass


class SchemaError(LedgerError):
    pass


class PermissionError_(LedgerError):
    pass


class TransitionError(LedgerError):
    pass


# ---------------------------------------------------------------------------
# THE VOCABULARY — 18 verbs, deliberately small.
#
# ⚠️ The plan says "16 verbs" and lists 18. Its table pairs `claim · start`,
# `block · unblock` and `drop · supersede` on shared rows, and the count was taken off
# the rows. Corrected here rather than by cutting two verbs to match a number: all
# eighteen are read by the board, the priority engine or the causal graph.
#
# ⛔ Adding a verb is a design change, not a convenience. Every verb here is one the
# board, the priority engine or the causal graph actually reads; a verb nothing reads
# is a note, and `note` already exists for that.
#
# `who`: which seat may emit it.
#   "any"   — any seat
#   "owner" — the seat that OWNS the item (not the human owner; see OWNER below)
#   a tuple — exactly those seats. "OWNER" in a tuple means the human.
# ---------------------------------------------------------------------------
VERBS = {
    "file":      {"who": "any",   "req": ("for", "title", "kind"),
                  "opt": ("row", "target", "needs", "spec", "from")},
    "claim":     {"who": "owner", "req": (), "opt": ()},
    "start":     {"who": "owner", "req": (), "opt": ()},
    "block":     {"who": "owner", "req": ("reason",), "opt": ("on",)},
    "unblock":   {"who": "owner", "req": (), "opt": ("reason",)},
    "verify":    {"who": "owner", "req": ("result", "config"), "opt": ("evidence", "sha")},
    "finding":   {"who": "any",   "req": ("from", "type", "severity", "name"), "opt": ()},
    # ⚠️ `spawn` carries no `id`. Its cause is `from` — a finding name, a run name, or
    # an item id — and its product is `name`. Requiring an `id` too forced the caller to
    # nominate some existing HOST item, which is not what §4 describes
    # (`spawn --from BLACKSTAR_SPAWNS_VESSELLESS_1 --for BUILD --name …`) and made the
    # documented command impossible. Found 2026-08-20 by the renderer, which tried it.
    "spawn":     {"who": "any",   "req": ("from", "for", "name"),
                  "opt": ("kind", "needs", "this_deployment", "spec", "title")},
    # ⚠️ `reason` moved from `req` to `opt` on these three — owner's ruling, 2026-08-22.
    # Nothing reads them: no renderer, no `priority.rank()` branch, no `derive_matrix`
    # case. They were a required justification that only a human ever reads, which is
    # what `note` is for — and a required field with nothing to put in it is answered
    # with filler, which is worse than silence because it looks like a reason.
    # 🔑 `drop`, `block` and `admin` KEEP theirs: there the reason is the ONLY record of
    # the decision, and the Tribal Furniture reversal was lost precisely because it lived
    # in a drop reason nobody propagated. Those are load-bearing; these three are not.
    "retarget":  {"who": ("BENCH", "DECIDE", "owner"), "req": ("to",), "opt": ("from", "reason")},
    # 🔴 `needs` had NO setter until 2026-08-21, and that broke the axis POLICY.md added
    # precisely so "waiting for the game" stops looking like "ready". Only `file` and
    # `spawn` accepted it, so every migrated item rendered at the filing default: 38 of
    # CHECK's 38 read `offline` while several of them wanted 100 in-game days or a
    # 21,872-tile bridge import, and his WAITING ON A WINDOW section was empty.
    # ⚠️ It is `("DECIDE", "owner")` like `retarget`, not owner-only: a mis-stamped
    # `needs` is exactly the kind of thing a seat notices about ANOTHER seat's item, and
    # the item's owner may be the one seat that cannot see the problem.
    "needs":     {"who": ("BENCH", "DECIDE", "owner"), "req": ("to",), "opt": ("reason",)},
    "reassign":  {"who": ("BENCH", "DECIDE"), "req": ("to",), "opt": ("reason",)},
    "close":     {"who": "owner", "req": ("sha",), "opt": ()},
    "drop":      {"who": "owner", "req": ("reason",), "opt": ()},
    "supersede": {"who": "owner", "req": ("by",), "opt": ("reason",)},
    "note":      {"who": "any",   "req": ("text",), "opt": ()},
    # ⚠️ `note` is the HANDOFF and POLICY.md's 90% ritual instructs it by name:
    # `rimflow seat idle --reason context-exhausted --note "<where I stopped>"`.
    # It was missing from this table, so the documented command errored out — a rule
    # nobody could follow. Found 2026-08-20 by the first seat that tried to follow it.
    "seat":      {"who": "self",  "req": ("state",), "opt": ("reason", "item", "note")},
    # Either live window may drive; one at a time is enforced by cmd_bridge's holder
    # guard (redesign #4, 2026-08-27 — CHECK's monopoly retired with the seat).
    # `purpose` is what `--for` lands in: one line saying what the holder is driving
    # it FOR, mirrored into infrastructure/state/BRIDGE so the other window can judge
    # whether to wait or go offline. Optional — a take without one is still a take.
    "bridge":    {"who": ("BENCH", "FOUNDRY", "CHECK"), "req": ("state",), "opt": ("purpose",)},
    # 🔑 `text` is what --note lands in, and it was MISSING here until
    # 2026-08-23: cmd_game has always set ev["text"], so every `rimflow game
    # --note` and every `./game up "note"` raised SchemaError instead. The flag
    # was advertised in --help and dead on arrival - it is GAME_STATE_HAS_NO_STAMPER_1's
    # second half, the prose game.json used to carry, and it had nowhere to go.
    # ⭐ `ranBy` records whose HANDS ran the command when the authority is the
    # owner's - an agent relaying his spoken words through `./game --said`. It was
    # added to cmd_game on 2026-08-25 and NOT added here, so every agent relay
    # broadcast to all four windows and then failed schema on the stamp: the seats
    # heard the new state and the ledger kept the old one, which is the exact
    # split-brain `./game` exists to prevent. Caught 2026-08-25 on a real `down`.
    "game":      {"who": ("OWNER",), "req": ("state",),
                  "opt": ("measured", "evidence", "text", "ranBy")},
    # `admin` (an OWNER-only audited correction) was removed 2026-08-27: defined
    # 2026-08-20, fired zero times ever. Git holds it if the need materialises.
}

# Events that do not name an item. Everything else must carry an `id`.
# Events that do not name an EXISTING item. `spawn` is here because it CREATES one —
# it is about its `from` (the cause) and its `name` (the product), never about a host.
ITEMLESS = ("seat", "bridge", "game", "spawn")


# THREE_DESCRIPTIVE_WORDS_# — the naming rule since 2026-08-20. Legacy IDs (B58, D55,
# C40) do not match it and are never renamed, which is why this is one half of a test
# and not the whole of it.
NAMED_ID = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+_\d+$")


def is_item_heading(token, body_lines):
    """Is `## <token> …` a filed ITEM, or a prose section that merely starts with a word?

    🔴 ONE DEFINITION, USED BY BOTH THE IMPORTER AND THE OVERWRITE GUARD. They disagreed
    on 2026-08-20 and it nearly cost the migration: the guard counted any heading whose
    first token was a legal ID, so `## A (DECIDE, 2026-08-14) to BUILD's B6 question`
    counted `A` as an item, and `## FYI …`, `## The …`, `## Four …`, `## Q …` likewise.
    The ledger held 144 items and the guard insisted the queues held 149, so it refused
    to let the overwrite proceed — correctly refusing, for a wrong reason.

    ⚠️ That is the dangerous shape of a bad guard: it does not fail open, it cries wolf.
    A guard that miscounts is one people learn to `--force` past, and forcing past this
    particular guard is how 853 lines of owner briefings would have died.

    The discriminator is that a real item carries a `state:` field at column 0, or is
    named in the THREE_DESCRIPTIVE_WORDS_# form. Prose sections have neither.
    """
    if not ID_RE.match(token or ""):
        return False
    if NAMED_ID.match(token):
        return True
    return any(re.match(r"state\s*:", l) for l in body_lines)


def now():
    """UTC, second resolution, sortable. Seconds are enough: ordering inside the file
    is what matters and appends are serialised by the kernel, not by the clock."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# WRITING
# ---------------------------------------------------------------------------
# 🔑 THE CHECKS ARE SEPARATE FUNCTIONS SO EACH CAN BE TESTED ON ITS OWN, and
# `validate` below is the ORDER they run in. The order is not incidental: the message
# a caller sees is the FIRST refusal its event trips, and several are pinned by name in
# the selftests. Add a check by adding a function AND a line in `validate`.
UNIVERSAL_FIELDS = ("ts", "seat", "event", "id", "caused_by", "override", "ownerSaid")


def _check_verb(ev):
    """-> the verb's spec. Refuses a verb the vocabulary does not contain."""
    verb = ev.get("event")
    spec = VERBS.get(verb)
    if not spec:
        raise SchemaError("unknown verb %r. The vocabulary is %d verbs and adding one "
                          "is a design change: %s"
                          % (verb, len(VERBS), ", ".join(sorted(VERBS))))
    return spec


def _check_seat(ev):
    seat = ev.get("seat")
    if seat not in SEATS:
        raise SchemaError("seat %r is not one of %s" % (seat, ", ".join(SEATS)))


def _check_stamp(ev):
    """Every event carries a `ts`, and a missing one must REFUSE rather than crash.

    🔴 WITHOUT THIS THE REFUSAL WAS A KeyError. `_apply` reads `ev["ts"]`
    unconditionally — `world.last_seen`, `item.created_at`, every `Run` — so one line
    missing the stamp raised KeyError, which is NOT a `LedgerError`, so
    `replay(strict=False)` could not collect it and EVERY tool that reads the ledger
    died on that one line. That is precisely the one-bad-line-breaks-everything
    failure non-strict replay exists to prevent, and an append-only file cannot have
    the bad line taken back out. `append()` and `check()` both stamp BEFORE
    validating, so nothing written through this module ever reaches this refusal; a
    line that does was written by something that bypassed the lock.
    """
    ts = ev.get("ts")
    if not ts or not isinstance(ts, str):
        raise SchemaError(
            "every event needs a `ts` string and this one has %r. `append()` and "
            "`check()` stamp it for you — a line without one was written by something "
            "that bypassed them, and the whole projection reads it." % (ts,))


def _check_item_reference(ev):
    """An itemless verb must NOT name an item; every other verb MUST name a legal one."""
    verb = ev["event"]
    if verb in ITEMLESS:
        if ev.get("id"):
            raise SchemaError(
                "`%s` is not about an existing item; drop the id.%s" % (
                    verb,
                    " Its cause is `from` and its product is `name`."
                    if verb == "spawn" else ""))
        return
    iid = ev.get("id")
    if not iid or not ID_RE.match(str(iid)):
        raise SchemaError(
            "`%s` needs an id matching THREE_DESCRIPTIVE_WORDS_# (got %r). "
            "Legacy IDs like B58 still resolve and are never renamed." % (verb, iid))


def _check_required(ev, spec):
    verb = ev["event"]
    for f in spec["req"]:
        if ev.get(f) in (None, ""):
            raise SchemaError(
                "`%s` requires --%s. Every field this verb needs:\n"
                "    required  %s\n"
                "    optional  %s\n"
                "\u2705 python3 src/RimMandrake/rimflow/cli.py %s <ID> %s"
                % (verb, str(f).replace("_", "-"),
                   ", ".join("--" + x.replace("_", "-") for x in spec["req"]) or "(none)",
                   ", ".join("--" + x.replace("_", "-") for x in spec["opt"]) or "(none)",
                   verb,
                   " ".join("--%s <%s>" % (x.replace("_", "-"), x) for x in spec["req"])))


def _check_no_unknown_fields(ev, spec):
    # ⚠️ `override` is legal on EVERY verb because the OWNER may override every verb.
    # It holds the rule that was crossed, so the bypass is in the record rather than
    # being invisible — see `_may`. No seat passes it on a command line: `_emit`
    # stamps it from `OVERRIDE_NOTICES`, and `cmd_bridge` stamps it for the two
    # bridge crossings `_may` cannot see (an OWNER `give`, which is emitted under the
    # target window's seat, and a `--force`/stale take across a live holder).
    known = set(spec["req"]) | set(spec["opt"]) | set(UNIVERSAL_FIELDS)
    for f in ev:
        if f not in known:
            raise SchemaError(
                "`%s` has no field %r. Prose belongs in items/<ID>.md, not in the "
                "ledger — a scalar that exists in two places drifts."
                % (ev["event"], f))


def _check_enums(ev):
    """The closed vocabularies.

    ⚠️ RUNS AFTER `_check_required`, and that is what makes the direct `ev[...]` reads
    below safe: every field named here is in its verb's `req`, so a missing one has
    already been refused with a message naming the flag. `spawn`'s name-shape check
    used to run BEFORE that, reading `ev["name"]` directly — so `spawn` with no
    `--name` raised KeyError rather than the refusal, and KeyError is not a
    LedgerError, so non-strict replay could not collect it either.
    """
    verb = ev["event"]
    if verb == "seat" and ev["state"] not in ("ready", "busy", "idle"):
        raise SchemaError("seat state must be ready|busy|idle")
    if verb == "bridge" and ev["state"] not in ("taken", "released"):
        raise SchemaError("bridge state must be taken|released")
    if verb == "game" and ev["state"] not in GAME_STATES:
        raise SchemaError("game state must be one of %s" % ", ".join(GAME_STATES))
    if verb in ("file", "spawn") and ev["for"] not in SEATS:
        raise SchemaError("%s --for must name a seat" % verb)
    if verb == "spawn" and not ID_RE.match(str(ev["name"])):
        raise SchemaError("spawn --name must be THREE_DESCRIPTIVE_WORDS_# "
                          "(got %r)" % ev["name"])
    # Without this, `rimflow spawn --for FOUNRDY ...` or `rimflow reassign X
    # --to BULID` succeeded and wrote an item owned by a seat that does not
    # exist: priority.rank() filters on item.owner, so no seat is ever
    # offered it and `next` never mentions it — the item goes silently
    # unofferable until someone notices and reassigns it back by hand.
    if verb == "reassign" and ev["to"] not in SEATS:
        raise SchemaError("reassign --to must name a seat")
    if verb == "verify" and ev["result"] not in ("pass", "fail", "partial"):
        raise SchemaError("verify result must be pass|fail|partial")


def _check_caused_by(ev):
    cb = ev.get("caused_by")
    if cb is not None and not (ID_RE.match(str(cb)) or RUN_RE.match(str(cb))):
        raise SchemaError(
            "caused_by must NAME the cause — an item id, a finding name, or a run like "
            "C40/run-3@full-578 — not a line number. Line numbers do not survive the "
            "monthly roll of events.jsonl. Got %r" % (cb,))


def _check_needs(ev):
    n = ev.get("needs")
    if n and n not in NEEDS:
        raise SchemaError("needs must be one of %s" % ", ".join(NEEDS))
    # The `needs` VERB carries its value in `to`, the same shape `retarget` uses. Without
    # this, `rimflow needs <ID> --to offlien` would append a typo that renders as a needs
    # nothing satisfies, and the item would simply stop being offered with no error.
    if ev.get("event") == "needs" and ev.get("to") not in NEEDS:
        raise SchemaError(
            "needs --to must be one of %s (got %r)" % (", ".join(NEEDS), ev.get("to")))


def validate(ev):
    """Refuse a malformed event BEFORE it reaches the file.

    🔑 There is no repair path for a bad line: the ledger is append-only, so a wrong
    event can only be corrected by a later `admin` event, never removed. Validation
    is therefore the last point at which a mistake is cheap.

    ⛔ EVERY REFUSAL RAISED FROM HERE IS A `LedgerError`, and nothing below may raise a
    KeyError, an AttributeError or a TypeError on a hand-written line. `replay()`
    catches only `LedgerError`; anything else takes down every tool that reads the
    ledger instead of being collected into `world.errors`.
    """
    spec = _check_verb(ev)
    _check_seat(ev)
    _check_stamp(ev)
    _check_item_reference(ev)
    _check_required(ev, spec)
    _check_no_unknown_fields(ev, spec)
    _check_enums(ev)
    _check_caused_by(ev)
    _check_needs(ev)
    return ev


BRIDGE_FILE = os.path.join(STATE, "BRIDGE")

# How long a holder may be silent before another window may simply take the bridge.
# 🔑 The number exists to prevent MUTUAL LOCKOUT, which is the failure mode the owner
# named (2026-09-02): a window that crashed, was closed, or ran out of context holds
# the lock forever, and the other window sits idle waiting for a release that is never
# coming. Staleness is measured against the holder's LAST LEDGER EVENT of any kind, so
# a window that is working is never stolen from, and a window that is gone is never
# in the way.
BRIDGE_STALE_SECONDS = 45 * 60


# The five comment lines every mirror opens with. ⚠️ Their COUNT is asserted by
# `selftest_bridge_file_concurrency.py`, which proves the final file is one writer's
# complete body by checking exactly where the status line lands.
BRIDGE_HEADER = (
    "# WHO IS DRIVING THE LIVE RIMWORLD BRIDGE.\n"
    "# Mirror of the rimflow ledger. Written by `rimflow bridge`, never by hand.\n"
    "#   free?  ->  rimflow bridge take --for \"<what for>\"\n"
    "#   held?  ->  do offline work. Nobody will come and tell you it freed; look again.\n"
    "#   wrong? ->  rimflow bridge who   (re-derives this from the ledger)\n")


def bridge_mirror_path():
    """Where the mirror goes for the LEDGER IN USE.

    ⚠️ Derived from the ledger in use, not from the module constant. `RIMFLOW_LEDGER`
    points the whole tool at a throwaway ledger for the selftests, and a mirror bound
    to the module constant wrote a synthetic test holder ("HELD CHECK") over the real
    file on the first run — the tests would have kept lying to two live windows.
    """
    led = os.environ.get("RIMFLOW_LEDGER")
    # `or "."` because `dirname("events.jsonl")` is "", and `makedirs("")` raises
    # FileNotFoundError — which is not a LedgerError, so it takes the tool down
    # instead of naming a rule. A bare filename in RIMFLOW_LEDGER is a legal thing
    # for a test or a one-off to set.
    return os.path.join(os.path.dirname(led) or ".", "BRIDGE") if led else BRIDGE_FILE


def bridge_body(holder, actor, purpose=None, since=None, note=None):
    """The exact bytes the mirror should hold. Pure, so it is testable without a disk."""
    if holder:
        line = "HELD    %s    since %s" % (holder, since or now())
        if purpose:
            line += "\nfor     %s" % purpose
    else:
        line = "FREE    since %s" % (since or now())
        if actor:
            line += "    (released by %s)" % actor
    if note:
        line += "\nnote    %s" % note
    return BRIDGE_HEADER + line + "\n"


def _write_atomically(target, body):
    """Replace `target` with `body` in one rename, leaving no litter behind on failure.

    🔴 THE TEMP NAME MUST BE PER-CALL UNIQUE, NOT A FIXED "<target>.tmp".
    A shared tmp path means O_TRUNC (which fires at open(), BEFORE flock is even
    requested) truncates whatever a concurrent writer already wrote to the SAME
    inode — both fds name the same file, truncation is not fd-local. Two windows
    calling this within the same instant (exactly the BENCH/FOUNDRY scenario this
    file exists for) could interleave into a torn write, or have the second
    os.replace() raise FileNotFoundError chasing a tmp the first replace already
    renamed away. Found by code review, 2026-09-02, never actually hit live — but
    this is the same class of 9p write-tearing `append()`'s own docstring measures.

    ⚠️ AND THE TEMP FILE IS UNLINKED IF ANYTHING FAILS. A unique name fixes the race
    and creates a second problem: every failed write left a `BRIDGE.tmp.<pid>.<ns>`
    behind, in a directory that is IN GIT, where the next `git status` shows it as
    untracked state nobody can attribute. Found by code review, 2026-09-03.
    """
    tmp = "%s.tmp.%d.%d" % (target, os.getpid(), time.time_ns())
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                blob = body.encode("utf-8")
                written = os.write(fd, blob)
                if written != len(blob):
                    raise LedgerError(
                        "short write to %s: %d of %d bytes; the mirror was NOT "
                        "replaced." % (target, written, len(blob)))
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return body


def write_bridge_file(holder, actor, purpose=None, since=None, note=None):
    """Mirror the bridge lock into one glanceable line at infrastructure/state/BRIDGE.

    🔑 A MIRROR, NOT A SECOND TRUTH. The ledger stays the only record; this file exists
    because the two windows cannot message each other and should not have to replay a
    ledger to answer "is the bridge free yet". `rimflow bridge who` re-derives it, so a
    stale mirror is always one command from being corrected rather than something to
    believe. Written here rather than in cli.py because every write in this system goes
    through the module that owns the 9p lock discipline.
    """
    target = bridge_mirror_path()
    body = bridge_body(holder, actor, purpose, since, note)
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    return _write_atomically(target, body)


def append(ev, path=None):
    """Validate, then write ONE line under an exclusive lock. Returns the byte offset.

    🔴 IT RETURNS A BYTE OFFSET, NOT A LINE INDEX, AND `caused_by` IS A NAME.
    The plan specified `caused_by` as "the index of the event that caused this one".
    That cannot work here for two independent reasons, both found while building it:

    1. **Computing the index means counting the whole file on every append** — O(n²)
       over the ledger's life, and under 12 concurrent writers on 9p the re-read
       itself failed with ENODATA. The offset comes free from the lock we already hold.
    2. 🔑 **Line indices do not survive the monthly roll.** The design rolls
       `events.jsonl` into `events/2026-08.jsonl` past ~5 MB, at which point every
       index restarts at zero and every stored `caused_by` silently points at a
       different event. A causal graph that quietly relabels itself is worse than none.

    So `caused_by` carries a **name** — an item id, a finding name, or a run name like
    `C40/run-3@full-578`. Those are already unique, already what §4's commands pass
    (`--from C40/run-3@full-578`), and they survive any amount of rolling.

    The returned offset is a convenience for the CURRENT file only. Do not store it.
    """
    # 🔑 STAMP FIRST, THEN VALIDATE. `validate` now REFUSES an event with no `ts`
    # (see `_check_stamp`: a stamp-less line made `_apply` raise KeyError, which
    # non-strict replay cannot collect), and callers legitimately hand this function
    # an unstamped dict. Validating before stamping would refuse every one of them.
    ev.setdefault("ts", now())
    validate(ev)
    path = path or EVENTS
    line = json.dumps(ev, separators=(",", ":"), ensure_ascii=False) + "\n"
    blob = line.encode("utf-8")
    if len(blob) >= PIPE_BUF:
        raise EventTooLargeError(
            "event is %d bytes; O_APPEND is only atomic below %d, and a torn line "
            "corrupts the ledger irrecoverably. Move the prose into items/%s.md."
            % (len(blob), PIPE_BUF, ev.get("id", "<ID>")))
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)   # see bridge_mirror_path
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        # ⛔ DO NOT REMOVE THE LOCK "because O_APPEND is atomic". It is, on ext4 and
        # tmpfs. This repo is on 9p, where it is not, and without this lock five of
        # every six events are lost — measured, not theorised. See the module
        # docstring for the numbers and `selftest_concurrency.py` to re-run them.
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            offset = os.lseek(fd, 0, os.SEEK_END)
            written = os.write(fd, blob)
            # A short write means a torn line, which is the one thing that cannot be
            # tolerated in an append-only file. Silence would be the worst response.
            if written != len(blob):
                raise LedgerError(
                    "short write: %d of %d bytes. The ledger may be torn at the tail "
                    "— inspect it before writing again." % (written, len(blob)))
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)
    return offset


def _read_lines(path):
    # Shared lock, so a reader cannot observe a write mid-flight — append()
    # takes LOCK_EX for the duration of its write, and this is the reader's
    # half of that same discipline. Advisory locks only bind other callers
    # that also take one, which every writer in this module does.
    fd = os.open(path, os.O_RDONLY)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_SH)
        except OSError:
            pass  # DrvFs/9p may refuse advisory locks; best-effort.
        try:
            with os.fdopen(os.dup(fd), encoding="utf-8") as fh:
                return fh.readlines()
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
    finally:
        os.close(fd)


def read(path=None):
    """-> [event]. A malformed line is REPORTED, never skipped silently.

    ⚠️ Skipping a bad line would make the ledger quietly lie, which is precisely the
    failure mode the ledger exists to end. A torn tail is recoverable by a human; a
    silently ignored one is not, because nobody learns it happened.
    """
    out = []
    path = path or EVENTS
    if not os.path.exists(path):
        return out
    lines = _read_lines(path)
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError as e:
            # The shared lock above rules out a write caught mid-flight for
            # every OTHER writer in this module, but it cannot see one that
            # bypassed the lock (a lock refused by the filesystem, or a
            # future writer that forgets to take it) — and only the LAST
            # line can ever be a genuinely in-flight append, since this file
            # is append-only. So: re-read once, but only for a failure on
            # the tail; a bad line earlier in the file is real corruption,
            # not a race, and retrying would just hide it behind a random
            # chance of catching the writer between flock calls.
            if i == len(lines) - 1:
                retry = _read_lines(path)
                if len(retry) > i:
                    retried = retry[i].strip()
                    if retried:
                        try:
                            out.append(json.loads(retried))
                            continue
                        except ValueError:
                            pass
            raise LedgerError(
                "%s line %d is not valid JSON (%s). The ledger is append-only, so "
                "this is almost certainly a torn write — do NOT edit around it; "
                "look at the tail and repair it deliberately." % (path, i + 1, e))
    return out


# ---------------------------------------------------------------------------
# READING — the projection
#
# 🔑 Everything below is DERIVED. Delete every file but events.jsonl and `reindex`
# rebuilds all of it. That is the test of whether the ledger really is the truth, and
# it is worth running for real rather than believing.
# ---------------------------------------------------------------------------
class Run(object):
    """One verification attempt. IMMUTABLE, forever, including the failures.

    ⭐ A failed run is not a defect in the record — it IS the record. The old queues
    reopened an item when its check failed, which erased the fact that it had ever
    failed and made "how many times did we try this" unanswerable. Here a `fail`
    stands permanently and the follow-up is a NEW item, linked by `caused_by`.
    """

    __slots__ = ("item", "n", "config", "result", "evidence", "sha", "ts", "index")

    def __init__(self, item, n, config, result, evidence, sha, ts, index):
        self.item, self.n, self.config = item, n, config
        self.result, self.evidence, self.sha = result, evidence, sha
        self.ts, self.index = ts, index

    @property
    def name(self):
        return "%s/run-%d@%s" % (self.item, self.n, self.config)

    def __repr__(self):
        return "<Run %s %s>" % (self.name, self.result)


class Item(object):
    """The projection of one item. Rebuilt from the ledger every time; never stored."""

    __slots__ = ("id", "title", "kind", "owner", "row", "target", "needs", "state",
                 "blocked", "blocked_reason", "blocked_on", "this_deployment",
                 "created_at", "created_index", "closed_sha", "superseded_by",
                 "runs", "findings", "history", "caused_by")

    def __init__(self, iid, index):
        self.id, self.created_index = iid, index
        self.title = self.kind = self.owner = None
        self.row = self.target = None
        self.needs = "offline"
        self.state = "proposed"
        self.blocked = False
        self.blocked_reason = self.blocked_on = None
        self.this_deployment = False
        self.created_at = None
        self.closed_sha = self.superseded_by = self.caused_by = None
        self.runs, self.findings, self.history = [], [], []

    @property
    def open(self):
        return self.state in ("proposed", "ready", "doing")

    def __repr__(self):
        return "<Item %s %s%s>" % (self.id, self.state,
                                   " BLOCKED" if self.blocked else "")


class World(object):
    """Everything the ledger says, at one moment: items, seats, bridge, game state."""

    def __init__(self):
        self.items = {}
        self.seats = {}                 # seat -> {"state":…, "reason":…, "item":…}
        self.bridge_holder = None
        self.bridge_since = None        # ts of the take/release that set the line above
        self.bridge_purpose = None      # what the holder said they were driving it FOR
        self.last_seen = {}             # seat -> ts of its most recent event of any kind
        self.game = "DOWN"
        self.findings = {}              # name -> {"from":…, "type":…, "severity":…}
        self.errors = []                # refusals a replay found ALREADY IN the file

    def open_items(self):
        return [i for i in self.items.values() if i.open]


# 🔴 TERMINAL MEANS TERMINAL. Nothing leaves these states, ever.
#
# ⚠️ This general rule is here because enumerating the forbidden PAIRS was not enough
# and the selftest caught it: `claim` on a closed item computed `done -> proposed`,
# which was not in the table, so a closed item could be quietly reopened through a
# state nobody thought to forbid. A blocklist of pairs fails open on the pair you did
# not think of; a terminal set fails closed. Prefer the second wherever the states are
# few and the consequence is losing the record.
TERMINAL = ("done", "dropped", "superseded")

# The named refusals. Their value is the MESSAGE — the terminal rule above already
# stops all of them, and each entry here replaces "refused" with a sentence saying
# what to do instead. ⛔ Every one of these happened in the markdown queues.
FORBIDDEN = {
    ("done", "ready"): "an item that closed cannot be reopened. File a NEW item and "
                       "link it with caused_by — the record of the close stands.",
    ("done", "doing"): "an item that closed cannot be restarted. File a new one.",
    ("done", "blocked"): "an item that closed cannot be blocked.",
    ("dropped", "ready"): "a dropped item cannot be revived. File a new one, and say "
                          "in its notes why the drop was wrong.",
    ("dropped", "doing"): "a dropped item cannot be started.",
    ("superseded", "ready"): "a superseded item cannot be revived; work its successor.",
}


# Filled by `_may` when the OWNER overrides a seat restriction, drained by the CLI so
# the override is WARNED about as well as recorded. Cleared at the top of `check()`.
OVERRIDE_NOTICES = []

# The OWNER's verbatim instruction, when a seat is acting on his spoken word rather than
# from his own shell. Set by the CLI's `--owner-said`, stamped onto the event as
# `ownerSaid`. 🔑 It is the authorization AND the record — see the flag's own comment.
OWNER_SAID = ""


def _who_refusal(ev, item):
    """The refusal `who` would produce, or None if this seat may emit the event.

    Split out of `_may` so the OWNER override has ONE thing to bypass and ONE sentence
    to quote back. Keeping the checks inline meant every new verb had to remember to
    exempt him, and `reassign` did not — see `_may`.
    """
    verb, seat = ev["event"], ev["seat"]
    who = VERBS[verb]["who"]
    if who in ("any", "self"):
        return None                             # a seat may only speak for itself
    if who == "owner":
        if item is None:
            # ⛔ NOT overridable, and it is in this function only because that is where
            # the lookup lands. "This id does not exist" is not a seat boundary — it is
            # a typo, and letting the OWNER override it would file events against
            # nothing. Raised, not returned, so `_may` never offers it to him.
            raise PermissionError_("`%s` names an item that does not exist" % verb)
        if item.owner and item.owner != seat:
            return ("%s may not `%s` %s — it belongs to %s. Filing work FOR another "
                    "seat is normal; changing another seat's item is refused."
                    % (seat, verb, item.id, item.owner))
        return None
    # ⚠️ `who` may MIX seat names with the sentinel "owner" — `retarget` is
    # ("DECIDE", "owner"), meaning DECIDE may retarget anything and a seat may
    # retarget its own. Treating the tuple as a literal seat list made the sentinel
    # match nothing, so no seat could ever retarget its own item. Found 2026-08-20 by
    # the CLI's selftest, which tried it; the model's own tests had only ever
    # exercised the pure-tuple case.
    if "owner" in who and (seat == "OWNER" or (item is not None and
                                               item.owner in (None, seat))):
        return None                             # the rule admits him; not an override
    if seat in who:
        return None
    if verb == "bridge":
        return ("only a live window (BENCH, FOUNDRY) takes the bridge, one at a time. "
                "This is not a formality: two seats driving one live game produce "
                "results neither can attribute.")
    if verb == "game":
        # \U0001f534 OWNER, 2026-08-22: the MEASUREMENT wins, silently. A seat that RAN
        # the probe is not guessing on anyone's behalf - it looked. Those events carry
        # `measured: true` and are admitted from any seat, because the alternative is
        # what he was tired of: a seat that can SEE the game is down, is forbidden to
        # say so, and writes a paragraph about the disagreement instead.
        # \u26d4 An INFERRED state is still refused. `measured` is set by probe.py and
        # nowhere else; writing it by hand to bypass this is the one thing it cannot
        # survive, and it would put a guess in the one place that is supposed to be true.
        if ev.get("measured"):
            return None
        return ("only the OWNER announces game state \u2014 unless you MEASURED it.\n\n"
                "\u2705 To read and correct it from the machine, which any seat may do:\n"
                "    python3 src/RimMandrake/rimflow/cli.py game\n\n"
                "A seat that INFERS 'the game is up' and tells everyone is still "
                "guessing on other people's behalf.\n\n"
                "\u2705 But if he SAID it, quoting him is not inferring — stamp it now:\n"
                "    python3 src/RimMandrake/rimflow/cli.py game <STATE> "
                "--owner-said \"<his words>\"\n"
                "\u26a0\ufe0f  That stamps the LEDGER only. Waking the other windows is "
                "still his, and\n    `./game up` does both in one word.")
    # 🔴 A REFUSAL THAT DOES NOT NAME THE ROUTE THROUGH IT STOPS THE WRONG PERSON.
    # Owner, 2026-08-24 01:3x, after REP was refused `needs` on work HE had just ordered,
    # reported the refusal back to him and stopped — while `--owner-said` was sitting right
    # there and REP had used it a dozen times the same night. The rule was never the
    # problem; the message was. Every other refusal in this file teaches the way through,
    # and this one — the generic seat rule, the one hit most often — did not.
    # ⛔ Do not shorten this back to one line. ⛔ And do not widen the rule instead: the seat
    # boundary is real and the override is supposed to be RECORDED, which is exactly what
    # `--owner-said` does.
    return ("only %s may `%s` (seat is %s)\n\n"
            "\u2705 If the OWNER told you to do this, that is not a refusal — quote him and "
            "it lands,\n   with his words recorded on the event as the authorization:\n"
            "    python3 src/RimMandrake/rimflow/cli.py %s %s \u2026 --owner-said "
            "\"<his words, verbatim>\"\n\n"
            "\u26a0\ufe0f  Pass what he ACTUALLY said. Bare assent (\"yes\", \"ok\", "
            "\"go ahead\") is refused on\n    purpose — that is him agreeing to something "
            "YOU said, and the ledger would record\n    your words as his. A short "
            "instruction is fine.\n\n"
            "\u26d4 If he did NOT tell you to, the rule stands. Route it to %s instead."
            % (" or ".join("the owning seat" if w == "owner" else w for w in who),
               verb, seat, verb, ev.get("id") or "<ID>",
               " or ".join("its owning seat" if w == "owner" else w for w in who)))


def _may(ev, item, world):
    """Who may emit this. Raises PermissionError_ naming the rule, never a bare False.

    🔴 THE OWNER IS NEVER REFUSED BY A SEAT RULE — owner's ruling, 2026-08-22.
    He was told `reassign` was DECIDE-only and that *"OWNER is not exempt for that
    verb, so even you can't do it"*. His answer: *"That's bullshit. OWNER absolutely
    can and should be able to override and shift items between agents if necessary.
    A warning may be appropriate, but I have to be able to override."*

    Every `who` rule here exists to stop one SEAT from reaching into another seat's
    work. The owner is not a seat — he is the human the seats work for, and he is the
    only one who can correct a seat that has wedged itself. A rule that refuses him is
    not protecting anything; it is a tool telling its owner no.

    ⚠️ **The override is recorded and warned about, never silent.** The event carries
    `override: "<the rule bypassed>"`, so a year later the ledger says he crossed a
    seat boundary deliberately rather than the boundary appearing not to have existed.

    ⛔ **What this does NOT unlock, deliberately.** `_may` governs WHO. It is not the
    state machine: `TERMINAL` and `FORBIDDEN` are checked elsewhere and still refuse
    him, so he cannot reopen a closed item by being the owner. Reviving a decision is
    a new item, for him as for everyone — that record is the one thing nobody edits.
    """
    reason = _who_refusal(ev, item)
    if reason is None:
        return
    if ev["seat"] == "OWNER":
        OVERRIDE_NOTICES.append(reason)
        return
    raise PermissionError_(reason)


def _transition(item, state):
    """The lifecycle gate, and the ONLY thing that assigns `item.state`.

    Lifted out of `_apply` (2026-09-03) so the state machine can be exercised on a bare
    `Item` without building a world and a ledger around it.

    🔴 A SECOND `close`/`drop`/`supersede` IS REFUSED, and it used to be a silent
    success. The `state == item.state` short-circuit below sat ABOVE the terminal
    check, so `done -> done` returned early and `_apply_item_verb` carried straight on
    to `item.closed_sha = ev["sha"]` — the projection quietly adopted the SECOND sha
    (and `supersede` the second `by`, and `close` cleared a `blocked` flag) while the
    ledger held both events. `rimflow close X` on an item closed days ago by another
    seat exited 0 and printed "X closed at <sha>", so the seat had no way to learn it
    had closed nothing. Fired FOUR times in the live ledger (two `close`, one `drop`,
    one `supersede`), measured 2026-09-03; those four now surface in `world.errors`,
    which is what that list is for — refusals found ALREADY IN an append-only file.
    ⛔ Do not "fix" them by loosening this back: the first record is the one that
    stands, and the terminal rule is only worth anything if it also refuses the pair
    nobody thought of — see the comment over `TERMINAL`.
    """
    if item.state in TERMINAL and state == item.state:
        raise TransitionError(
            "%s is already `%s`, and this would be a SECOND one. The first record "
            "stands — a repeat cannot be told apart from the original in any view, "
            "but it would silently replace the sha, the reason or the successor the "
            "projection reports. If something more happened, file a NEW item and link "
            "it with caused_by." % (item.id, item.state))
    if state == item.state:
        return
    pair = (item.state, state)
    if pair in FORBIDDEN:
        raise TransitionError("%s: %s -> %s refused. %s"
                              % (item.id, item.state, state, FORBIDDEN[pair]))
    if item.state in TERMINAL:
        raise TransitionError(
            "%s: %s -> %s refused. `%s` is terminal and cannot be reopened, "
            "revived or restarted — the record of it standing IS the deliverable. "
            "File a NEW item and link it with caused_by."
            % (item.id, item.state, state, item.state))
    item.state = state


def _apply_file(ev, index, world):
    """`file` — the ordinary way an item comes into existence."""
    iid = ev["id"]
    existing = world.items.get(iid)
    if existing is not None:
        raise SchemaError("%s already exists (filed at line %d)"
                          % (iid, existing.created_index + 1))
    item = Item(iid, index)
    item.title, item.kind, item.owner = ev["title"], ev["kind"], ev["for"]
    # ⚠️ `or`, not a get() default. A key that is PRESENT AND NULL — which `append()`
    # accepts and only `cli._emit`'s strip happens to prevent — makes `get(k, default)`
    # hand back None, and a `needs` of None matches nothing in `priority.BY_GAME`: the
    # item fails open into UNKNOWN_NEEDS and is offered with no window check at all,
    # reported as an unrecognised `needs` nobody can grep for. The default belongs to
    # the projection, not to the presence of a key.
    item.row, item.target = ev.get("row"), ev.get("target") or "v1"
    item.needs = ev.get("needs") or "offline"
    item.created_at = ev["ts"]
    item.caused_by = ev.get("caused_by")
    # 🔑 THE FILING IS THE ITEM'S FIRST HISTORY ENTRY — the same reason `spawn` records
    # its own, and it was missing here until 2026-09-03. Three live items rendered
    # "history (0 events)" while plainly existing, which reads as a gap in the record
    # rather than as its beginning. It also cost `cli._distress`'s reassign-direction
    # heuristic outright: that loop seeds the previous owner from an event carrying a
    # `for`, and for a FILED item the only such event was the one not in the list — so
    # `prev` stayed None and an upstream reassign could never be counted.
    item.history.append(index)
    world.items[iid] = item
    return item


def _apply_spawn(ev, index, world):
    """`spawn` — an item born from a finding, a run or another item."""
    name = ev["name"]
    clash = world.items.get(name)
    if clash is not None:
        # 🔴 SPAWN USED TO OVERWRITE. `world.items[name] = new` replaced whatever was
        # already there, so `spawn --name <a live item>` silently discarded that item's
        # state, history, runs and findings from every derived view while the ledger
        # still held both halves — the projection quietly disagreeing with the truth,
        # which is the single failure this whole design exists to end. `file` has always
        # refused this; `spawn` did not. Never hit live (checked across all 4217 events,
        # 2026-09-03); found by code review the same day.
        raise SchemaError(
            "%s already exists (created at line %d). `spawn` CREATES an item — "
            "spawning onto a live one would replace its state, history, runs and "
            "findings in every view while the ledger still holds both. Give the new "
            "item its own name, or `note` the existing one."
            % (name, clash.created_index + 1))
    new = Item(name, index)
    new.title = ev.get("title") or name
    new.kind = ev.get("kind") or "task"          # `or`, not a get() default — see _apply_file
    new.owner = ev["for"]
    new.needs = ev.get("needs") or "offline"
    new.this_deployment = bool(ev.get("this_deployment"))
    new.created_at, new.caused_by = ev["ts"], ev["from"]
    # The spawn IS the new item's first history entry. Without this the item
    # renders with "history (0 events)" while plainly existing, which reads as a
    # gap in the record rather than as its beginning.
    new.history.append(index)
    world.items[name] = new
    return new


def _apply_itemless(ev, seat, world):
    """`seat`, `bridge`, `game` — the three verbs that describe the WORLD, not an item."""
    verb = ev["event"]
    if verb == "seat":
        world.seats[seat] = {"state": ev["state"], "reason": ev.get("reason"),
                             "item": ev.get("item"), "note": ev.get("note"),
                             "at": ev["ts"]}
        return
    if verb == "bridge":
        taken = ev["state"] == "taken"
        world.bridge_holder = seat if taken else None
        world.bridge_since = ev["ts"]
        world.bridge_purpose = ev.get("purpose") if taken else None
        return
    if verb == "game":
        world.game = ev["state"]
        # 🔑 `--this-deployment` is cleared on entering DOWN — and ONLY on DOWN.
        # ⚠️ This used to fire on any state that was not UP, which cleared the flag at
        # GOING_DOWN: exactly the moment the flag is most load-bearing, because
        # GOING_DOWN is when CHECK drops everything postponable and works the
        # this-deployment list before the window shuts. The doctrine file says "cleared
        # on entering DOWN" and the doctrine file is right.
        # The flag means "do this before the window closes"; carrying it PAST the close
        # would turn it into false urgency nobody could trace to a cause.
        if ev["state"] == "DOWN":
            for it in world.items.values():
                it.this_deployment = False
        return


def _apply_item_verb(ev, index, item, seat, world):
    """Every verb that MUTATES an item that already exists."""
    verb = ev["event"]
    to = lambda state: _transition(item, state)          # noqa: E731 — one short alias

    if verb == "claim":
        item.owner = seat
        to("ready")
    elif verb == "start":
        # 🔴 THE COMPLETENESS GATE IS GONE. Owner, 2026-08-21:
        #   "I need you to turn off the whole 'you can't work on something that
        #    doesn't have a valid verification or validation plan' thing. It was a
        #    BAD IDEA, and it's costing us lost knowledge when we discover errors.
        #    Remove it immediately and make everyone able to work on anything in
        #    their queue independent of the V&V plan attached right away."
        #
        # ⛔ Do not reinstate it, and do not reintroduce it in a softer form —
        # not as a warning that blocks, not as a `needs` value, not as a hook.
        # The cost it was paying for was never measured; the cost it imposed was:
        # a discovered error could not be written down and worked because the item
        # recording it had no verify section yet, so the knowledge was lost.
        #
        # ✅ `verify` and `criteria` remain GOOD PRACTICE and the sections still
        # exist. They are simply not a precondition for doing the work.
        to("doing")
    elif verb == "block":
        # 🔑 TERMINAL MEANS TERMINAL, and this guard named ONE of the three terminal
        # states. `block` does not route through `_transition` (blocked is a flag, not a
        # state), so it carried its own check — hardcoded to `done`, which left a
        # `dropped` or `superseded` item blockable. That is the exact shape the comment
        # over `TERMINAL` warns about: a list of pairs fails open on the pair nobody
        # thought of. Corrected 2026-09-03 to the terminal SET, keeping the named `done`
        # sentence, which says the useful thing.
        if item.state in TERMINAL:
            raise TransitionError(
                FORBIDDEN.get((item.state, "blocked"))
                or "%s: `%s` is terminal, and blocking says work is STUCK — this "
                   "item's record is finished. File a NEW item for whatever is stuck "
                   "and link it with caused_by." % (item.id, item.state))
        item.blocked = True
        item.blocked_reason, item.blocked_on = ev["reason"], ev.get("on")
    elif verb == "unblock":
        item.blocked = False
        item.blocked_reason = item.blocked_on = None
    elif verb == "verify":
        n = sum(1 for r in item.runs if r.config == ev["config"]) + 1
        item.runs.append(Run(item.id, n, ev["config"], ev["result"],
                             ev.get("evidence"), ev.get("sha"), ev["ts"], index))
    elif verb == "finding":
        world.findings[ev["name"]] = {"from": ev["from"], "type": ev["type"],
                                      "severity": ev["severity"], "at": ev["ts"]}
        item.findings.append(ev["name"])
    elif verb == "retarget":
        item.target = ev["to"]
    elif verb == "needs":
        item.needs = ev["to"]
    elif verb == "reassign":
        item.owner = ev["to"]
        # 🔴 A `doing` item handed to another seat was INVISIBLE to them.
        # `priority.rank()` only offers `ready`, so `rimflow next` never showed it,
        # and agents do not message each other — so nobody could tell the receiving
        # seat the id, and nothing would. Owner, 2026-08-21, shown the bug:
        # *"Capture that reassign bug and pass it to BUILD to fix! That's horrible!"*
        #
        # 🔑 Only `doing` moves, and that is deliberate. `proposed` and `ready` are
        # both already discoverable — `next` offers `ready` and names the
        # spec-complete `proposed` items waiting to be claimed — so touching them
        # would rewrite state nobody asked to change.
        #
        # ⛔ The alternative fix — making `next` surface `doing` items — was refused
        # in the item's own spec. The 2026-08-21 work stop parked nine items as
        # `doing` precisely BECAUSE `next` does not re-offer them. That behaviour is
        # load-bearing and is not for trading away.
        #
        # ⚠️ Not a `claim`: the receiving seat has not acted yet, so a `doing` item
        # returns to `ready` for them to pick up. It lands in `ready` regardless of
        # whether the prose sections exist — the completeness gate was removed by the
        # owner on 2026-08-21; see `start` above.
        if item.state == "doing":
            to("ready")
    elif verb == "close":
        to("done")
        item.closed_sha = ev["sha"]
        # ⚠️ ALL THREE, exactly as `unblock` does it. Clearing the flag and leaving the
        # reason behind left 23 live items projecting `blocked False` with a stale
        # `blocked_reason` still attached (measured 2026-09-03). Every reader gates on
        # the flag today, so nothing was displaying it — which is the definition of a
        # trap: the invariant "not blocked ⇒ no reason" held everywhere except here,
        # and the first view that reads the reason without the flag would report a
        # closed item as stuck on something that was resolved by the close.
        item.blocked = False
        item.blocked_reason = item.blocked_on = None
    elif verb == "drop":
        to("dropped")
    elif verb == "supersede":
        to("superseded")
        item.superseded_by = ev["by"]
    elif verb == "note":
        pass

    item.history.append(index)


def _apply(ev, index, world, strict=False):   # `strict` is the caller's concern
    """Fold ONE event into the world. The dispatcher; every branch is its own function.

    🔑 THE ORDER OF THE THREE GATES IS LOAD-BEARING and is why `file` sits above them:
    `file` creates the item it names, so "which has never been filed" cannot apply to
    it, and its `who` is "any", so `_may` has nothing to say. Everything else must find
    its item first (or be itemless) and pass `_may` before it touches anything.
    """
    verb, seat = ev["event"], ev["seat"]
    # Every event is a sign of life from its seat. `bridge take` reads this to tell a
    # window that is WORKING from one that is GONE, so it must count every verb, not
    # just the bridge ones.
    world.last_seen[seat] = ev["ts"]
    iid = ev.get("id")
    item = world.items.get(iid) if iid else None

    if verb == "file":
        _apply_file(ev, index, world)
        return
    if verb not in ITEMLESS and item is None:
        raise SchemaError("%s names item %s, which has never been filed" % (verb, iid))
    _may(ev, item, world)
    if verb == "spawn":
        _apply_spawn(ev, index, world)
        return
    if verb in ITEMLESS:
        _apply_itemless(ev, seat, world)
        return
    _apply_item_verb(ev, index, item, seat, world)


# 🔴 A CACHE, BECAUSE ON THIS FILESYSTEM AN open() IS 0.8 ms.
# `_sections` is called on every `claim` and every `start`, so a replay of 600 events
# over 150 items did 500 uncached opens and spent 297 of its 373 ms there — measured
# 2026-08-20. The identical loop on tmpfs takes 0.8 ms total. It is the 9p mount again:
# the same property that broke concurrent appends makes per-file syscalls expensive.
# ⚠️ Keyed on the ITEMS dir so redirecting `model.ITEMS` (which tests do) cannot serve
# a stale answer from the previous directory.
_SECTIONS_CACHE = {}


def invalidate_sections(iid=None):
    """Drop the cache. Call after writing items/<ID>.md within one process."""
    if iid is None:
        _SECTIONS_CACHE.clear()
    else:
        _SECTIONS_CACHE.pop((ITEMS, iid), None)


def _sections(iid):
    """-> set of `## ` section names present in items/<ID>.md."""
    key = (ITEMS, iid)
    hit = _SECTIONS_CACHE.get(key)
    if hit is not None:
        return hit
    path = os.path.join(ITEMS, "%s.md" % iid)
    try:
        with open(path, encoding="utf-8") as fh:
            out = {m.group(1).strip().lower()
                   for m in re.finditer(r"^##\s+(\w+)\s*$", fh.read(), re.M)}
    except OSError:
        out = set()
    _SECTIONS_CACHE[key] = out
    return out


def _missing(item):
    have = _sections(item.id)
    return [s for s in ("spec", "verify", "criteria") if s not in have]


def _complete(item):
    return not _missing(item)


def replay(events=None, strict=False, path=None):
    """Fold the whole ledger into a `World`.

    `strict=False` (the default) COLLECTS refusals into `world.errors` instead of
    raising. ⚠️ That is not leniency — a refusal found during replay describes an
    event that is ALREADY IN an append-only file and cannot be removed. Raising would
    make every downstream tool unusable until a human intervened, which is exactly the
    wrong incentive: it would push people toward editing the ledger. Collect, surface,
    and let `admin` correct it forward.

    `strict=True` is for the writing path, where the event has not landed yet and
    refusing is both possible and correct.
    """
    if events is None:
        events = read(path)
    world = World()
    for index, ev in enumerate(events):
        try:
            validate(ev)
            _apply(ev, index, world, strict)
        except LedgerError as e:
            if strict:
                raise
            world.errors.append((index, ev.get("event"), str(e)))
    return world


def check(ev, world=None, path=None):
    """Would this event be accepted? Raises the naming refusal if not.

    Call this BEFORE `append`. It replays the candidate against current state, which
    is the only way to catch a transition refusal — validate() alone cannot know that
    an item is already closed.
    """
    # 🔴 CLEAR AFTER THE REPLAY, NEVER BEFORE IT. `replay()` runs `_may` over every
    # event already in the file, so each historical OWNER override APPENDS to this same
    # module-level list — clearing first and replaying second left the candidate's own
    # notice buried behind years of them, and `_emit` reads `OVERRIDE_NOTICES[0]`. It
    # would have stamped a stale, unrelated rule onto the `override` field of a
    # permanent ledger event: the one field this system treats as evidence that a
    # boundary was crossed on purpose, carrying the wrong boundary. Not reachable
    # through today's CLI (every `_emit` passes a pre-replayed world), which is exactly
    # why it survived — found by code review 2026-09-03.
    if world is None:
        world = replay(path=path)
    del OVERRIDE_NOTICES[:]             # per-call; the CLI drains it after we return
    # Stamp before validating: `validate` refuses an event with no `ts` (see
    # `_check_stamp`) and callers hand this function unstamped dicts.
    stamped = dict(ev, ts=ev.get("ts") or now())
    validate(stamped)
    _apply(stamped, 0, copy.deepcopy(world), True)
    return True
