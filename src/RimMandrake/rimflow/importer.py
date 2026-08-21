#!/usr/bin/env python3
"""rimflow/importer.py — the one-way door: six hand-edited queues -> ledger + prose.

    python3 src/RimMandrake/rimflow/importer.py                 # DRY RUN, writes nothing
    python3 src/RimMandrake/rimflow/importer.py --apply         # writes for real
    python3 src/RimMandrake/rimflow/importer.py --apply --force  # over a non-empty ledger

🔴 THIS IS THE IRREVERSIBLE STEP IN THE WHOLE PLAN, SO IT IS DRY-RUN BY DEFAULT.
The dry run is not a summary of what would happen — it is a **full rehearsal**: every
item file is rendered, every event is built, the whole thing is written into a
throwaway directory and replayed through `model.replay(strict=False)`. If the report
says the replay is clean, `--apply` is the same code writing to a different directory.

⛔ IT NEVER TOUCHES `infrastructure/state/queue/*.md`. Not with `--apply`, not with
`--force`. Those files become generated views only after a HUMAN has compared this
import against them, and that is someone else's step and someone else's commit.
Deleting the source before anyone has checked the copy is the one mistake here that
cannot be undone.

WHAT IT READS, AND WHAT AN "ITEM" IS
====================================
Items are `## <ID> <title>` headings; the ID is the first whitespace-delimited token
and must match `model.ID_RE`. That alone is not enough — the queues also carry prose
headings (`## 🔴 OWNER RULINGS…`, `## 📌 SESSION HANDOFF…`, `## Q (CHECK, 2026-08-15)…`)
whose first token is sometimes a bare word like `Q` or `The`. Measured 2026-08-20:

    169 `## ` headings total
    145 of those carry a `state:` field OR are shaped UPPER_SNAKE_#   <- the items
     24 prose headings, skipped and LISTED in the report so a human can check them
    144 distinct IDs (B53 is filed in BOTH queue/BUILD.md and queue/CHECK.md)

⚠️ Those numbers move. Four seats share this working tree and the queues gain items
while you are reading them — this run started at 168/144 and finished at 169/145
because DECIDE committed one mid-run. **The report's `in == out` assertion is the
guarantee, not the count**; re-read the report, never a number written in a doc.

So the test is: an ID-shaped first token AND (a `state:` field OR a name that already
obeys the THREE_DESCRIPTIVE_WORDS_# rule). The two items that reach here on their name
alone — `MORNING_BRIEF_CHECK_1`, `LOADS_ARE_BLOCKED_NEEDS_YOU_1` in `queue/HUMAN.md` —
have no fields at all and are reported **uncertain** rather than dropped.

⛔ NOTHING IS EVER SILENTLY DROPPED. An item that cannot be parsed is still filed, with
a `note` event carrying the reason, and is listed individually in the report. `items in`
must equal `items accounted for`, and the report asserts it.

`state:` IS PROSE, NOT AN ENUM — AND THAT PROBLEM IS ALREADY SOLVED
==================================================================
Of the items with a `state:`, only about half begin with a bare canonical keyword; 58 lead with
an emoji and many carry a qualifier (`done (2026-08-14)`, `blocked — needs a human
answer`). `Utils/derive_matrix.py` already reads that vocabulary correctly, so this
module **loads its `state_of`, `WORD` and `EMOJI` rather than reinventing them** — one
reader, one vocabulary. If they ever disagree, the board and the ledger disagree, which
is the drift this whole design exists to end.

What this adds on top is a CONFIDENCE, because a silent wrong guess becomes the
permanent record:

    certain    the leading word IS a canonical state, and any leading emoji agrees
    inferred   the state came from a synonym (`closed`, `built`, `v2`) or from an emoji
    uncertain  guessed: no `state:` at all, an unrecognised coinage, a duplicate ID,
               an emoji that CONTRADICTS the word, or a transition we could not complete

⚠️ `⛔ v2` is **dropped, targeted v2** — not done. The emoji and the word agree on
`dropped`, and the word `v2` additionally sets `target: v2`. An import that read that
red circle as "finished" would silently mark ~21 deferred items complete.

WHERE EACH PIECE OF THE SOURCE LANDS, AND WHY NOTHING LANDS TWICE
=================================================================
    row:  target:              -> the ledger, as `file` fields
    state:                     -> the ledger, as the events it implies
    spec: verify: criteria:    -> items/<ID>.md, sections of the same name
    every other field, and any
    prose before the fields    -> items/<ID>.md `## notes`

🔑 The one judgement call: `state:` is frequently a paragraph, not a word (`B55`'s runs
to 30 lines of measured argument). The ENUM goes to the ledger; a `block`/`drop` reason
is truncated to a scalar; and the **raw text is preserved verbatim under `## notes`**,
introduced by a provenance line saying it came from the import. That is not the field
existing twice — the live field is the ledger's, and the note is a dated quotation of
what the queue said on the day it was converted. Throwing it away would lose the
majority of the argument in the queues, which is the part nobody can reconstruct.

Stdlib only.
"""
import argparse
import copy
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                                            # noqa: E402

ROOT = model.ROOT
QUEUE = os.path.join(model.STATE, "queue")
CLOSED_LEDGER = os.path.join(model.STATE, "closed_ledger.json")

# 🔑 REUSED, NOT REIMPLEMENTED. derive_matrix.py's state_of()/WORD/EMOJI are the
# measured vocabulary of what seats have actually written. Loading the file directly
# avoids needing Utils to be an importable package, and it is stdlib.
_dm_path = os.path.join(ROOT, "src", "RimMandrake", "Utils", "derive_matrix.py")
_spec = importlib.util.spec_from_file_location("_derive_matrix", _dm_path)
derive_matrix = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(derive_matrix)
state_of, WORD, EMOJI = derive_matrix.state_of, derive_matrix.WORD, derive_matrix.EMOJI

CANON = ("ready", "doing", "done", "blocked", "dropped")

# Which seat owns the items in each file, and what kind of thing they are. Both are
# properties of the FILE, which is why they are not guessed per item.
SOURCES = [
    ("BUILD.md",          "BUILD",  "task"),
    ("CHECK.md",          "CHECK",  "check"),
    ("CHECK_CLOSED.md",   "CHECK",  "check"),
    ("DECIDE.md",         "DECIDE", "decision"),
    ("DECIDE_ARCHIVE.md", "DECIDE", "decision"),
    ("HUMAN.md",          "OWNER",  "question"),
]

PROSE_FIELDS = ("spec", "verify", "criteria")
SCALAR_FIELDS = ("row", "target", "needs", "state")

# An UPPER_SNAKE_# name is self-evidently an item even with no fields at all.
NAMED_ID = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*_\d+$")
FIELD = re.compile(r"^([a-z][a-z_]*):[ \t]*(.*)$")
LEAD_WORD = re.compile(r"[^A-Za-z]*([A-Za-z][A-Za-z0-9]*)")
SHA_RE = re.compile(r"\b([0-9a-f]{7,40})\b")
# "folded into `X`", "superseded by X", "supersedes X" — the successor is always named.
SUCCESSOR = re.compile(
    r"(?:folded into|superseded by|replaced by|supersedes)\s+`?([A-Za-z][A-Za-z0-9._-]{2,})`?",
    re.I)

TITLE_MAX = 180
REASON_MAX = 280


# ---------------------------------------------------------------------------
# PARSING
# ---------------------------------------------------------------------------
class Parsed(object):
    __slots__ = ("id", "title", "source", "owner", "kind", "fields", "preamble",
                 "order", "raw_lines")

    def __init__(self, iid, title, source, owner, kind):
        self.id, self.title = iid, title
        self.source, self.owner, self.kind = source, owner, kind
        self.fields = {}        # name -> text (dedented, may be multi-line)
        self.order = []         # field names in source order
        self.preamble = ""      # prose between the heading and the first field
        self.raw_lines = []


def _dedent(first, rest):
    """`first` is the text after `spec:` on the field line; `rest` are its continuation
    lines, which are aligned past the widest label (`criteria: `).

    ⚠️ The common indent must be measured over the CONTINUATIONS ONLY. Measuring it
    over all the lines includes the field line's own value, whose indent is zero, so
    nothing is stripped and every multi-line field arrives in items/<ID>.md as a
    ten-space markdown code block — which is how the first version of this rendered
    all 143 files before anyone looked at one.
    """
    body = [l for l in rest if l.strip()]
    indent = min((len(l) - len(l.lstrip()) for l in body), default=0)
    out = [first] + [l[indent:] if l.strip() else "" for l in rest]
    return "\n".join(out).strip("\n")


def parse_file(path, source, owner, kind):
    """-> ([Parsed], skipped_headings). Field lines are at COLUMN 0 only.

    ⚠️ derive_matrix.py's parser matches `\\s*state:` and so can pick a `state:` out of
    an indented prose continuation. Here a field must start at column 0, because the
    body of `spec:` legitimately contains lines like `  result: pass` quoted from a
    tool's output, and reading one of those as the item's own field would silently
    rewrite the item.
    """
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    heads = [i for i, l in enumerate(lines) if l.startswith("## ")] + [len(lines)]
    items, skipped = [], []
    for a, b in zip(heads, heads[1:]):
        tok = lines[a][3:].split()
        tok = tok[0] if tok else ""
        body = lines[a + 1:b]
        if not model.ID_RE.match(tok):
            skipped.append(lines[a])
            continue
        has_state = any(FIELD.match(l) and FIELD.match(l).group(1) == "state"
                        for l in body)
        if not (has_state or NAMED_ID.match(tok)):
            skipped.append(lines[a])
            continue
        it = Parsed(tok, lines[a][3:][len(tok):].strip(), os.path.basename(path),
                    owner, kind)
        it.raw_lines = body
        cur, buf, pre = None, [], []
        for l in body:
            m = FIELD.match(l)
            if m:
                if cur:
                    it.fields[cur] = _dedent(buf[0], buf[1:])
                cur, buf = m.group(1), [m.group(2)]
                if cur not in it.order:
                    it.order.append(cur)
            elif cur is None:
                pre.append(l)
            else:
                buf.append(l)
        if cur:
            it.fields[cur] = _dedent(buf[0], buf[1:])
        it.preamble = "\n".join(pre).strip("\n")
        items.append(it)
    return items, skipped


# ---------------------------------------------------------------------------
# STATE -> (canonical state, confidence, explanation)
# ---------------------------------------------------------------------------
def classify(raw):
    """-> (state, confidence, why). `raw` is the verbatim `state:` text, or ''.

    The canonical answer is delegated to derive_matrix.state_of so the board and the
    ledger cannot disagree. Everything here is about HOW it was reached, which is the
    part a human has to be able to audit before this becomes the permanent record.
    """
    raw = (raw or "").strip()
    if not raw:
        return "ready", "uncertain", "no `state:` field at all; defaulted to ready (open)"
    final = state_of({"state": raw})      # derive_matrix takes the ITEM dict
    emoji = EMOJI.get(raw[0])
    m = LEAD_WORD.match(raw)
    word = m.group(1).lower() if m else None
    mapped = WORD.get(word) if word else None

    if mapped and emoji and emoji != mapped:
        return final, "uncertain", (
            "the leading emoji %r says %r but the word %r says %r; took the word"
            % (raw[0], emoji, word, mapped))
    if mapped and word in CANON:
        return final, "certain", "canonical keyword %r" % word
    if mapped:
        return final, "inferred", "synonym %r -> %r" % (word, mapped)
    if emoji:
        return final, "inferred", "emoji %r -> %r" % (raw[0], emoji)
    return final, "uncertain", (
        "no known keyword or emoji in %r; derive_matrix's catch-all made it %r "
        "(open work, never done)" % (raw.splitlines()[0][:60], final))


def wants_v2(raw, fields):
    """`⛔ v2 —` is dropped AND targeted v2. The two are different axes and the queues
    wrote both into one word."""
    if fields.get("target", "").strip().lower().startswith("v2"):
        return True
    m = LEAD_WORD.match(raw or "")
    return bool(m and m.group(1).lower() == "v2")


def find_successor(raw, body=""):
    """-> (successor_id, where) or (None, None).

    The `state:` line is asked first. Many supersessions announce the successor in the
    prose ABOVE the fields instead ("⛔ **Folded into `BLACKSTAR_NEVER_GENERATES_1`**"),
    so the body is asked second — and a successor found there is reported as a guess,
    because prose is not a field and the sentence may be describing something else.
    """
    for text, where in ((raw or "", "the `state:` line"), (body or "", "the body prose")):
        m = SUCCESSOR.search(text)
        if m and model.ID_RE.match(m.group(1)):
            return m.group(1), where
    return None, None


def find_sha(iid, raw, closed):
    """The sha a `close` needs. `closed_ledger.json` is the real record — it was built
    by walking every `Closes:` trailer in git — so it is consulted before the prose."""
    rec = closed.get(iid)
    if rec and rec.get("sha"):
        return rec["sha"], None
    for m in SHA_RE.finditer(raw or ""):
        # A kebab ID ends in a hex tag; only take one that is quoted as a commit.
        s = m.group(1)
        if "`%s`" % s in (raw or ""):
            return s, None
    return None, "no commit sha recorded for a closed item"


# ---------------------------------------------------------------------------
# RENDERING items/<ID>.md
# ---------------------------------------------------------------------------
def render_item(parsed, extra_notes=()):
    """`## spec`, `## verify`, `## criteria`, `## notes` — and nothing else.

    No front-matter, no title, no `state:`. Every scalar lives in the ledger.
    """
    out = []
    for name in PROSE_FIELDS:
        out.append("## %s\n%s\n" % (name, parsed.fields.get(name, "").strip()
                                    or "_not recorded in the source queue_"))
    notes = []
    if parsed.preamble.strip():
        notes.append(parsed.preamble.strip())
    for name in parsed.order:
        if name in PROSE_FIELDS or name in ("row", "target", "needs"):
            continue
        val = parsed.fields.get(name, "").strip()
        if name == "state":
            notes.append("**Imported from `queue/%s`. Its `state:` read, verbatim:**\n\n%s"
                         % (parsed.source, val))
        elif val:
            notes.append("**%s:** %s" % (name, val))
    notes.extend(extra_notes)
    out.append("## notes\n%s\n" % ("\n\n".join(notes).strip()
                                   or "_nothing beyond the fields above._"))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# BUILDING THE EVENTS
# ---------------------------------------------------------------------------
def trunc(s, n):
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[:n - 1] + "…"


class Conv(object):
    """One item's conversion: the events, the file body, and how sure we are."""

    __slots__ = ("parsed", "events", "body", "confidence", "why", "state")

    def __init__(self, parsed):
        self.parsed = parsed
        self.events, self.why = [], []
        self.body, self.confidence, self.state = "", "certain", "ready"

    def demote(self, level, why):
        rank = {"certain": 0, "inferred": 1, "uncertain": 2}
        if rank[level] > rank[self.confidence]:
            self.confidence = level
        self.why.append(why)


def convert(parsed, closed, dup_of=None):
    c = Conv(parsed)
    raw = parsed.fields.get("state", "")
    state, conf, why = classify(raw)
    c.state = state
    c.demote(conf, why)
    seat = parsed.owner

    if dup_of:
        c.demote("uncertain", "ID %s is filed in BOTH queue/%s and queue/%s; the second "
                              "was merged into the first as a note, not filed again"
                              % (parsed.id, dup_of, parsed.source))
        c.body = None
        c.events = [{"seat": seat, "event": "note", "id": parsed.id,
                     "text": trunc("duplicate heading in queue/%s: %s"
                                   % (parsed.source, parsed.title), REASON_MAX)}]
        return c

    target = "v2" if wants_v2(raw, parsed.fields) else \
        (parsed.fields.get("target", "").strip() or "v1")
    ev = {"seat": seat, "event": "file", "id": parsed.id,
          "for": seat, "kind": parsed.kind,
          "title": trunc(parsed.title, TITLE_MAX) or parsed.id,
          "target": target}
    row = parsed.fields.get("row", "").strip()
    if row:
        ev["row"] = trunc(row, 40)
    needs = parsed.fields.get("needs", "").strip()
    if needs in model.NEEDS:
        ev["needs"] = needs
    elif seat == "OWNER":
        ev["needs"] = "owner"
    c.events.append(ev)

    if not parsed.fields:
        c.demote("uncertain", "no `row:`/`state:`/`spec:` fields at all — the whole "
                              "body is prose and went to `## notes`")
        c.events.append({"seat": seat, "event": "note", "id": parsed.id,
                         "text": "imported from queue/%s with no parseable fields; "
                                 "state and prose are unverified" % parsed.source})

    if state == "dropped":
        word = (LEAD_WORD.match(raw).group(1).lower() if LEAD_WORD.match(raw) else "")
        looks_superseded = word in ("superseded", "supersedes") or \
            "supersed" in raw.lower()[:120] or "folded into" in raw.lower()[:120]
        by, where = find_successor(raw, parsed.preamble) if looks_superseded else (None, None)
        if by:
            if where != "the `state:` line":
                c.demote("uncertain",
                         "recorded as superseded by %s, but the successor was read out of "
                         "%s rather than a field" % (by, where))
            c.events.append({"seat": seat, "event": "supersede", "id": parsed.id,
                             "by": by, "reason": trunc(raw, REASON_MAX)})
        else:
            if looks_superseded:
                c.demote("uncertain", "reads as superseded but names no successor; "
                                      "recorded as `drop` rather than inventing a `by`")
            c.events.append({"seat": seat, "event": "drop", "id": parsed.id,
                             "reason": trunc(raw, REASON_MAX) or "dropped in the queue"})
        return c

    c.events.append({"seat": seat, "event": "claim", "id": parsed.id})

    if state == "done":
        sha, problem = find_sha(parsed.id, raw, closed)
        if problem:
            c.demote("uncertain", problem + "; closed with sha `unrecorded`")
            sha = "unrecorded"
        c.events.append({"seat": seat, "event": "close", "id": parsed.id, "sha": sha})
    elif state == "doing":
        c.events.append({"seat": seat, "event": "start", "id": parsed.id})
    elif state == "blocked":
        c.events.append({"seat": seat, "event": "block", "id": parsed.id,
                         "reason": trunc(raw, REASON_MAX) or "blocked in the queue"})
    return c


# ---------------------------------------------------------------------------
# THE RUN
# ---------------------------------------------------------------------------
def collect():
    """-> ([Parsed], skipped, seen_headings)."""
    items, skipped, heads = [], [], 0
    for fname, owner, kind in SOURCES:
        path = os.path.join(QUEUE, fname)
        got, skip = parse_file(path, fname, owner, kind)
        items.extend(got)
        skipped.extend(skip)
        heads += len(got) + len(skip)
    return items, skipped, heads


def build(items):
    closed = {}
    try:
        with open(CLOSED_LEDGER, encoding="utf-8") as fh:
            closed = json.load(fh).get("items", {})
    except (OSError, ValueError):
        pass
    convs, first = [], {}
    for p in items:
        dup = first.get(p.id)
        c = convert(p, closed, dup_of=dup)
        if dup is None:
            first[p.id] = p.source
            c.body = render_item(p)
        convs.append(c)
    # A duplicate's prose is appended to the survivor rather than thrown away.
    for c in convs:
        if c.body is None:
            host = next(x for x in convs if x.parsed.id == c.parsed.id and x.body)
            host.body = host.body.rstrip() + (
                "\n\n**A second heading for this ID was filed in `queue/%s`. Its body, "
                "verbatim:**\n\n%s\n" % (c.parsed.source,
                                         "\n".join(c.parsed.raw_lines).strip()))
    return convs


def materialise(convs, items_dir, events_path):
    """Write item files FIRST, then the ledger.

    🔑 The order is load-bearing: `start` refuses an item whose items/<ID>.md is
    missing spec/verify/criteria, so the prose has to be on disk before the events
    that depend on it are appended.
    """
    os.makedirs(items_dir, exist_ok=True)
    # ⚠️ model's completeness gate reads model.ITEMS, not the path we were handed. If
    # they differ (they do under --items, and under the dry run's throwaway dir) every
    # `start` is refused for a missing spec that is sitting right there.
    saved, model.ITEMS = model.ITEMS, items_dir
    for c in convs:
        if c.body:
            with open(os.path.join(items_dir, "%s.md" % c.parsed.id), "w",
                      encoding="utf-8") as fh:
                fh.write(c.body)
    refused = []
    try:
        for c in convs:
            for ev in c.events:
                try:
                    model.append(copy.deepcopy(ev), events_path)
                except model.LedgerError as e:
                    refused.append((c.parsed.id, ev.get("event"), str(e)))
    finally:
        model.ITEMS = saved
    return refused


def report(convs, skipped, heads, refused, world, out=None):
    # ⚠️ NOT a default of sys.stdout: that binds the stream at import time, so a
    # caller that redirects stdout (the selftest does) never sees the report.
    w = (out or sys.stdout).write
    n_in = len(convs)
    filed = sum(1 for c in convs if c.body)
    merged = n_in - filed
    w("=" * 78 + "\n")
    w("QUEUE IMPORT — %s\n" % ("APPLIED" if APPLIED else "DRY RUN, nothing written"))
    w("=" * 78 + "\n\n")
    w("SOURCES\n")
    for fname, owner, kind in SOURCES:
        n = sum(1 for c in convs if c.parsed.source == fname)
        w("  %-20s -> %-6s %-9s %3d items\n" % (fname, owner, kind, n))
    w("  %-20s    %-6s %-9s %3d prose headings skipped (not items)\n"
      % ("", "", "", len(skipped)))
    w("\nCOUNTS — these must balance or the import is losing work\n")
    w("  `## ` headings seen ................. %d\n" % heads)
    w("  prose headings skipped .............. %d\n" % len(skipped))
    w("  ITEMS IN ............................ %d\n" % n_in)
    w("  items/<ID>.md written ............... %d\n" % filed)
    w("  merged into an existing ID .......... %d\n" % merged)
    w("  ITEMS ACCOUNTED FOR ................. %d\n" % (filed + merged))
    ok = (filed + merged) == n_in and heads == n_in + len(skipped)
    w("  %s in == out: %d == %d\n" % ("OK  " if ok else "MISMATCH", n_in, filed + merged))
    w("\nEVENTS\n")
    verbs = {}
    for c in convs:
        for ev in c.events:
            verbs[ev["event"]] = verbs.get(ev["event"], 0) + 1
    for k in sorted(verbs):
        w("  %-10s %4d\n" % (k, verbs[k]))
    w("  %-10s %4d total\n" % ("", sum(verbs.values())))
    w("\nSTATES\n")
    st = {}
    for c in convs:
        if c.body:
            st[c.state] = st.get(c.state, 0) + 1
    for k in sorted(st):
        w("  %-10s %4d\n" % (k, st[k]))
    w("\nCONFIDENCE\n")
    for level in ("certain", "inferred", "uncertain"):
        w("  %-10s %4d\n" % (level, sum(1 for c in convs if c.confidence == level)))

    w("\nINFERRED — the state came from an emoji or a synonym\n")
    for c in convs:
        if c.confidence == "inferred":
            w("  %-58s %-8s %s\n" % (c.parsed.id, c.state, c.why[0]))

    w("\n" + "!" * 78 + "\nUNCERTAIN — every one of these is a GUESS and becomes the "
      "permanent record.\nRead the raw source line before running --apply.\n"
      + "!" * 78 + "\n")
    for c in convs:
        if c.confidence != "uncertain":
            continue
        raw = (c.parsed.fields.get("state", "") or "").splitlines()
        w("\n  %s  [queue/%s]  -> %s\n" % (c.parsed.id, c.parsed.source, c.state))
        for why in c.why:
            w("      why: %s\n" % why)
        w("      raw: %s\n" % (raw[0].strip() if raw else "<no state: line in the source>"))

    w("\nREPLAY\n")
    if refused:
        w("  %d event(s) REFUSED by model.append — fix the event, never the model:\n"
          % len(refused))
        for iid, verb, msg in refused:
            w("    %-40s %-10s %s\n" % (iid, verb, msg.replace("\n", " ")[:150]))
    else:
        w("  every event was accepted by model.append().\n")
    if world is not None:
        w("  replay: %d items, %d refusals collected\n"
          % (len(world.items), len(world.errors)))
        for i, verb, msg in world.errors[:20]:
            w("    line %d %-10s %s\n" % (i, verb, msg.replace("\n", " ")[:150]))
    w("\nSKIPPED HEADINGS (prose, not items — check none of these is work)\n")
    for s in skipped:
        w("  %s\n" % s[:100])
    w("\n")
    return ok and not refused


APPLIED = False


def main(argv=None):
    global APPLIED
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true",
                    help="write for real. Without it NOTHING is written.")
    ap.add_argument("--force", action="store_true",
                    help="allow --apply over a non-empty events.jsonl")
    ap.add_argument("--events", default=model.EVENTS)
    ap.add_argument("--items", default=model.ITEMS)
    a = ap.parse_args(argv)

    items, skipped, heads = collect()
    convs = build(items)

    if a.apply:
        if os.path.exists(a.events) and os.path.getsize(a.events) > 0:
            if not a.force:
                sys.stderr.write(
                    "REFUSED: %s already exists and holds %d bytes.\n"
                    "The ledger is APPEND-ONLY — importing again would file every one "
                    "of these %d items a second time, and `file` on an existing id is "
                    "refused by the model, so the run would half-land and leave a "
                    "ledger nobody can read backwards to a clean state.\n"
                    "If you genuinely mean to import on top of an existing ledger, "
                    "pass --force. If you meant to start over, move the old ledger "
                    "aside first: it cannot be deleted from inside this tool.\n"
                    % (a.events, os.path.getsize(a.events), len(convs)))
                return 2
            sys.stderr.write("--force: appending on top of an existing %d-byte ledger.\n"
                             % os.path.getsize(a.events))
        APPLIED = True
        refused = materialise(convs, a.items, a.events)
        saved, model.ITEMS = model.ITEMS, a.items
        try:
            world = model.replay(model.read(a.events))
        finally:
            model.ITEMS = saved
        ok = report(convs, skipped, heads, refused, world)
        return 0 if ok else 1

    # DRY RUN — a full rehearsal into a throwaway directory, then a real replay.
    tmp = tempfile.mkdtemp(prefix="rimflow_import_dry_")
    try:
        items_dir = os.path.join(tmp, "items")
        events = os.path.join(tmp, "events.jsonl")
        refused = materialise(convs, items_dir, events)
        saved, model.ITEMS = model.ITEMS, items_dir
        try:
            world = model.replay(model.read(events))
        finally:
            model.ITEMS = saved
        ok = report(convs, skipped, heads, refused, world)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("DRY RUN. Nothing was written. Re-run with --apply to commit this.")
    print("queue/*.md was not opened for writing and never will be by this tool.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
