#!/usr/bin/env python3
"""relentless_explain.py — a live or checker failure is EXPLAINED, not labelled (LIVE_FAILURES_EXPLAIN_MORE_THAN_A_LABEL).

Owner, 2026-11-04: "Make sure the Test Pilot's job is to EXPLAIN the failure, not just try to execute a test. That's the
major problem with Relentless: it needs to write a coherent explanation of failures, not just indicate them. Then there
needs to be follow-up work to address them."

Before this, a DIAGNOSE ending (relentless.DIAGNOSE_ENDS) was settled by one `learn "CLASSIFY: MOD|SITE|..."` line and a
diagnostician's `attribute` by a target and one evidence line: a label. Now both carry one explanation record:

    expected    what the proof expected to read
    observed    what the game (or the checker) actually did
    mechanism   how the one led to the other: the causal link, not a restated symptom
    steps       one or more "claim :: evidence" pairs: every step of the mechanism with the log line, path or reading
                that shows it
    ruled_out   one or more "theory :: why it is not that": the other explanations considered and the reading that
                killed each
    cause       the follow-up item that addresses the cause: OPEN, filed in the ledger. Several items whose failures
                share a cause name the same one (the cause book, explain_causes.json, lists every open cause with its
                mechanism so a second explainer joins it rather than filing a twin). A closed item is never reopened
                here (rimflow refuses: terminal means terminal): file a NEW one with --caused-by the old.

The record is kept on the item (the store's items/<ID>/explanations.jsonl and an attempt line), reaches every later
brief whole, and is noted on the cause item's ledger history, so the follow-up work starts from the explanation.
"""
import json
import os
import re
import time

ID_RX = re.compile(r"^[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+$")
SEP = "::"
MIN = 12                     # a field shorter than this is a label, not an explanation
TEXT = ("expected", "observed", "mechanism")
LISTS = ("steps", "ruled_out")
# a worker's own reading (`relentless.py explain`); the diagnostician's targets are relentless_attrib.TARGETS
CLASSES = ("MOD", "SITE", "HARNESS", "CONTRACT")
# a cause outside the item: the work cannot be fixed on the item itself, so the cause must be a different item
OUTSIDE = ("SITE", "HARNESS", "CHECKER", "DEPENDENCY")
TERMINAL = ("done", "dropped", "superseded")
BOOK = "explain_causes.json"
# a brief's template pasted back (<the log line>, <how the one led to the other>): three or more plain words in angle
# brackets. Code in an explanation (List<Thing>, Dictionary<string, int>) is not one.
PLACEHOLDER = re.compile(r"<[a-z][a-z']*(?: [a-z']+){2,}>")


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def _text(name, v):
    v = (v or "").strip()
    if len(v) < MIN or PLACEHOLDER.search(v):
        raise ValueError("--%s must say it in words (%d+ characters, no <placeholder>): got %r"
                         % (name.replace("_", "-"), MIN, v[:80]))
    return v


def _pairs(name, vals, what):
    out = []
    for v in vals or []:
        if SEP not in (v or ""):
            raise ValueError("--%s takes \"%s %s %s\": got %r" % (name.replace("_", "-"), what[0], SEP, what[1], (v or "")[:80]))
        a, b = (x.strip() for x in v.split(SEP, 1))
        if len(a) < 4 or len(b) < 4 or PLACEHOLDER.search(a + b):
            raise ValueError("--%s: both sides of %r must be said (no <placeholder>): got %r" % (name.replace("_", "-"), SEP, v[:80]))
        out.append({what[0]: a, what[1]: b})
    if not out:
        raise ValueError("give at least one --%s \"%s %s %s\"" % (name.replace("_", "-"), what[0], SEP, what[1]))
    return out


def validate(a, kinds, item, cause=None):
    """CLI args (a dict: expected, observed, mechanism, step|steps, ruled_out) -> the explanation fields, or ValueError
    naming what is missing. `kinds`: the classes or targets it explains; `cause`: the follow-up item id."""
    rec = {k: _text(k, a.get(k)) for k in TEXT}
    rec["steps"] = _pairs("step", a.get("step") or a.get("steps"), ("claim", "evidence"))
    rec["ruled_out"] = _pairs("ruled_out", a.get("ruled_out"), ("theory", "why_not"))
    cause = (cause or "").strip()
    if cause != item and not ID_RX.match(cause):        # the item itself is its own follow-up whatever its id's shape
        raise ValueError("--cause must name the follow-up item that addresses the cause (a filed id): got %r" % cause)
    if cause == item and any(k in OUTSIDE for k in kinds):
        raise ValueError("%s is a cause outside this item: name the repair item (`rimflow namecheck`, `rimflow file <NAME> "
                         "--for BENCH`, or the open one in the cause book), not %s itself" % ("/".join(kinds), item))
    rec["cause"] = cause
    rec["kinds"] = list(kinds)
    return rec


def check_cause(cause, state_of):
    """`state_of(id)` -> the ledger state, None when never filed (or None for no ledger: skipped). Raises on a cause that
    cannot carry the follow-up work."""
    if state_of is None:
        return
    s = state_of(cause)
    if s is None:
        raise ValueError("--cause %s has never been filed: `rimflow namecheck`, then `rimflow file <NAME> --for BENCH`, or "
                         "reuse an open cause from `relentless.py causes`" % cause)
    if s in TERMINAL:
        raise ValueError("--cause %s is %s and a closed item is never reopened: file a NEW follow-up item with "
                         "`--caused-by %s` (or reuse an open one from `relentless.py causes`) and name it" % (cause, s, cause))


def _book_path(store):
    return store.p(BOOK)


def book(store):
    try:
        with open(_book_path(store), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def keep(store, item, gen, rec, ending, sha, by, now):
    """Under the store lock. The explanation goes on the item (explanations.jsonl, an attempt line, learned.md) and its
    cause into the book. -> True when this item is new to that cause (the caller notes the cause item, out of the lock)."""
    full = dict(rec, item=item, gen=gen, ending=ending, sha=sha, by=by, at=iso(now))
    store._append(os.path.join(store.item_dir(item), "explanations.jsonl"), json.dumps(full, sort_keys=True))
    store.attempt(item, {"at": iso(now), "gen": gen, "explained": "+".join(rec["kinds"]), "cause": rec["cause"],
                         "ending": ending, "mechanism": rec["mechanism"]})
    store.learn(item, render(full, head="- %s gen %s EXPLAINED %s" % (iso(now), gen, ending or "the last ending")))
    if rec["cause"] == item:        # the item's own fault: its next worker carries it, nothing to share
        return False
    b = book(store)
    c = b.setdefault(rec["cause"], {"first": iso(now), "mechanism": rec["mechanism"], "items": {}})
    new = item not in c["items"]
    c["items"].setdefault(item, []).append(iso(now))
    store._write(_book_path(store), json.dumps(b, indent=1, sort_keys=True))
    return new


def explanations(store, item):
    out = []
    try:
        with open(os.path.join(store.item_dir(item), "explanations.jsonl"), encoding="utf-8") as f:
            for ln in f:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def render(e, head=None):
    """The explanation as prose lines: what the next worker reads in learned.md."""
    lines = [head or "Explanation of %s (gen %s, %s, by %s):" % (e.get("ending") or "an ending", e.get("gen"),
                                                                  "+".join(e.get("kinds") or []), e.get("by"))]
    lines += ["  expected:  %s" % e.get("expected"), "  observed:  %s" % e.get("observed"),
              "  mechanism: %s" % e.get("mechanism")]
    lines += ["  step %d: %s  [evidence: %s]" % (n + 1, s.get("claim"), s.get("evidence")) for n, s in enumerate(e.get("steps") or [])]
    lines += ["  ruled out: %s  [because: %s]" % (t.get("theory"), t.get("why_not")) for t in e.get("ruled_out") or []]
    lines.append("  follow-up: %s" % e.get("cause"))
    return "\n".join(lines)


def note_text(item, e):
    return ("relentless: %s's %s is explained with this item as its cause (%s). Expected: %s | Observed: %s | Mechanism: "
            "%s | Steps: %s" % (item, e.get("ending") or "failure", "+".join(e.get("kinds") or []), e["expected"],
                                e["observed"], e["mechanism"],
                                "; ".join("%s [%s]" % (s["claim"], s["evidence"]) for s in e["steps"][:4])))


def open_causes(store, state_of=None, limit=12):
    """-> lines for a brief: the causes on the book that are still open, newest first, so an explainer joins one."""
    rows = []
    for cause, c in book(store).items():
        try:
            closed = state_of is not None and state_of(cause) in TERMINAL
        except Exception:  # noqa: BLE001  an unreadable ledger lists the cause: a brief is never lost to it
            closed = False
        if closed:
            continue
        rows.append((max(max(v) for v in c["items"].values()) if c.get("items") else c.get("first", ""), cause, c))
    rows.sort(reverse=True)
    return ["  %s (%d item%s: %s): %s" % (cause, len(c["items"]), "" if len(c["items"]) == 1 else "s",
                                         ", ".join(sorted(c["items"])), c.get("mechanism", ""))
            for _, cause, c in rows[:limit]]


def ask(rc, item, gen):
    """The brief's instruction, one paragraph: the command and what each field must hold."""
    return ("`%s explain --item %s --gen %d --class MOD|SITE|HARNESS|CONTRACT --expected \"what the proof expected to "
            "read\" --observed \"what the game or checker actually did\" --mechanism \"how the one led to the other\" "
            "--step \"claim %s the log line, path or reading that shows it\" (repeat per step) --ruled-out \"another "
            "theory %s the reading that kills it\" (repeat) --cause <FOLLOW_UP_ITEM>`. The cause is the OPEN item that "
            "will fix it: this item itself for MOD or CONTRACT, a repair item for SITE or HARNESS (reuse one from the "
            "cause book below when it is the same cause; else `rimflow namecheck`, `rimflow file <NAME> --for BENCH`; a "
            "closed one is never reopened: file a new one `--caused-by` it)" % (rc, item, gen, SEP, SEP))


def sample():
    """A valid explanation, for the selftests and as the shape of the fields."""
    return {"expected": "A2 reads the hopper holding 10 water after 2500 ticks",
            "observed": "A2 read 0 water; the log shows the pump never ticked",
            "mechanism": "the pump comp overrides CompTick but the parent is a Plant, which only calls TickLong",
            "step": ["the pump is a Plant subclass :: Defs/RM_Pump.xml thingClass=Plant",
                     "CompTick never ran :: Player.log has no 'pump tick' line over 2500 ticks"],
            "ruled_out": ["the bridge read the wrong map :: probe printed map 0 = the quicktest map, one map loaded"]}
