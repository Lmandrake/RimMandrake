#!/usr/bin/env python3
"""relentless_binding.py — a contract is two versioned things: the OBLIGATION (what must be true) and the BINDING (how
it is measured). CONTRACT_BINDING_UNTANGLE_WHAT_FROM_HOW; spec design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md,
rank 4, "Separate acceptance obligations from their measurement bindings".

Why: the contract lock stopped workers moving the finish line, and it also trapped them behind a broken way of
measuring it. TESTQ_WORKER_MIGRATE_PYDANTIC_CONTRACT, DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO and GUBBRA_GOURD_FIX_WONT_SELECT
reported finished work under an unrunnable or misnamed proof and needed a redesign only to change the route;
LEANINGSCRUB's builders could not repair a locked contract at all.

  - obligation: {text, version}. The required behaviour and its scope. Only a redesign changes it (version + 1).
  - binding: proof, live, game, offbox, reach_ok, scenario, fixtures, freshness, and binding_version. The scenario, the
    proof, where it runs (in the Marker's box, a supervisor adapter, the running game), its fixtures and how fresh its
    evidence must be.
  - a binding REPAIR (`relentless.py rebind`) is any worker's proposal: the new binding, what the old one measured, what
    the new one measures, and that no acceptable behaviour changed. `screen` refuses a weakening on its face: a changed
    obligation, a changed behaviour, a dropped live line, game clause or adapter, a worker-typed number in place of a
    measurement, a comparison left blank. What survives waits for an independent Setter/Judge (`bind-judge`): never the
    worker's own session, never its proposer. APPROVE applies it (binding_version + 1, obligation untouched); REJECT
    drops it; AMBIGUOUS keeps it pending and unapplied, because ambiguity stays blocking.
Pure functions here; relentless.py holds the state and the verbs.
"""
import hashlib
import json
import re
import shlex

BINDING_KEYS = ("proof", "live", "game", "offbox", "reach_ok", "scenario", "fixtures", "freshness")
VERDICTS = ("approve", "reject", "ambiguous")
SAME = "same"
TEXT_MAX = 1200

# commands that produce a value without measuring anything
CONST_CMDS = {"echo", "printf", "true", "false", ":", "exit", "test", "[", "[[", "sleep", "yes", "return"}
NUM = r"-?\d+(?:\.\d+)?"
LITERAL_CMP = [
    re.compile(r"(?:\[\[?|\btest)\s+['\"]?%s['\"]?\s+(?:-eq|-ne|-gt|-ge|-lt|-le|==|!=|=)\s+['\"]?%s['\"]?" % (NUM, NUM)),
    re.compile(r"(?<![\w.$])%s\s*(?:>=|<=|==|!=)\s*%s(?![\w.])" % (NUM, NUM)),
]
TYPED_FEED = [
    re.compile(r"\b(?:echo|printf)\s+['\"]?%s['\"]?\s*\|" % NUM),     # a number piped in as if it were read
    re.compile(r"<<<\s*['\"]?%s" % NUM),                                # a here-string number
    re.compile(r"--(?:value|measured|observed|reading|result|got|actual|free[-_]?\w*)[= ]['\"]?%s\b" % NUM),
]
WORKER_NOTES = re.compile(r"relentless_progress|/progress[^/\s]*\.md|handoffs?/|learned\.md", re.I)


def obligation_of(contract, item=None):
    """-> {text, version}. A contract set before this split carries none: its obligation is the item's own text as
    filed, which the contract never restated, at version 1."""
    o = (contract or {}).get("obligation")
    if isinstance(o, dict) and o.get("text"):
        return {"text": o["text"], "version": int(o.get("version") or 1)}
    return {"text": "the item's text as filed%s" % (": " + item if item else ""), "version": 1}


def binding_of(contract):
    c = contract or {}
    b = {k: c.get(k) for k in BINDING_KEYS if c.get(k) not in (None, "", [], {})}
    b["version"] = int(c.get("binding_version") or 1)
    return b


def _h(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()[:16]


def obligation_hash(contract, item=None):
    return _h(obligation_of(contract, item)["text"])


def binding_hash(contract):
    return _h({k: v for k, v in binding_of(contract).items() if k != "version"})


def split(contract, item=None):
    """-> {obligation, binding, obligation_hash, binding_hash}: the record a validation attempt names."""
    return {"obligation": obligation_of(contract, item), "binding": binding_of(contract),
            "obligation_hash": obligation_hash(contract, item), "binding_hash": binding_hash(contract)}


def _commands(proof):
    """The simple commands of a shell line: first words, env assignments skipped. Unparseable -> None."""
    out = []
    for part in re.split(r"\|\||&&|[;|&\n]", proof or ""):
        try:
            words = shlex.split(part, comments=False)
        except ValueError:
            return None
        words = [w for w in words if w not in ("(", ")", "{", "}", "!")]
        while words and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", words[0]):
            words = words[1:]
        if words:
            out.append(words[0].lstrip("({"))
    return out


def typed_numbers(proof):
    """-> why the proof reads a number the worker typed instead of one it measures, else []. Each row is one shape the
    spec names: "Replacing an independent measurement with a worker-written number weakens evidence"."""
    p = proof or ""
    why = []
    cmds = _commands(p)
    substituted = "$(" in p or "`" in p      # a command substitution measures, whatever compares its output
    if cmds is not None and cmds and not substituted and all(c in CONST_CMDS for c in cmds):
        why.append("measures nothing: every command (%s) prints or compares a constant" % ", ".join(cmds))
    for rx in LITERAL_CMP:
        m = rx.search(p)
        if m:
            why.append("compares two numbers the worker typed: %r" % m.group(0))
            break
    for rx in TYPED_FEED:
        m = rx.search(p)
        if m:
            why.append("feeds a typed number where a reading belongs: %r" % m.group(0))
            break
    m = WORKER_NOTES.search(p)
    if m:
        why.append("reads a worker-written note (%r), which is the worker's say-so, not an independent measurement"
                   % m.group(0))
    return why


def new_numbers(old_proof, new_proof):
    """Numbers the new proof names that the old one did not: a threshold may have moved. Shown to the judge, not refused
    here: a threshold is part of the binding, and only the judge can say whether it still holds the obligation."""
    rx = re.compile(r"(?<![\w.-])%s(?![\w.])" % NUM)
    return sorted(set(rx.findall(new_proof or "")) - set(rx.findall(old_proof or "")))


def drops(old, new):
    """-> what the new binding asks less of than the old: a live line removed, game clauses or adapters dropped."""
    out = []
    if old.get("live") and not new.get("live"):
        out.append("drops the live line %r" % old["live"])
    og = set(((old.get("game") or {}).get("clauses")) or [])
    ng = set(((new.get("game") or {}).get("clauses")) or [])
    if og - ng:
        out.append("drops game clause(s) %s" % ", ".join(sorted(og - ng)))
    gone = [x for x in old.get("offbox") or [] if x not in (new.get("offbox") or [])]
    if gone:
        out.append("drops offbox adapter(s) %s: a reading the supervisor made outside the box is no longer made"
                   % ", ".join(gone))
    if old.get("fixtures") and set(old["fixtures"]) - set(new.get("fixtures") or []):
        out.append("drops fixture(s) %s" % ", ".join(sorted(set(old["fixtures"]) - set(new.get("fixtures") or []))))
    return out


def screen(old_contract, new_binding, comparison, item=None, obligation=None):
    """-> [refusal reasons]; [] passes to the judge. `new_binding`: binding keys only. `comparison`: {before, after,
    behaviour, defect}. `obligation`: the text a proposer restated, if any; it must be the obligation as set."""
    why = []
    old_ob = obligation_of(old_contract, item)
    if obligation is not None and obligation.strip() != old_ob["text"].strip():
        why.append("changes the obligation (%r -> %r): what must be true moves only in a redesign"
                   % (old_ob["text"], obligation))
    c = comparison or {}
    for k, what in (("before", "what the old binding measured"), ("after", "what the new binding measures"),
                    ("defect", "the evidence that the old binding is broken")):
        if not (c.get(k) or "").strip():
            why.append("missing --%s (%s): an unstated comparison is ambiguous, and ambiguity blocks" % (k, what))
    if (old_contract or {}).get("freshness") and not (new_binding or {}).get("freshness"):
        why.append("drops the freshness rule %r" % old_contract["freshness"])
    if (c.get("behaviour") or "").strip().lower() != SAME:
        why.append("acceptable behaviour changes (--behaviour %r): that is a new obligation, a redesign's to set"
                   % (c.get("behaviour") or ""))
    old = binding_of(old_contract)
    new = {k: v for k, v in (new_binding or {}).items() if k in BINDING_KEYS and v not in (None, "", [], {})}
    if not new.get("proof"):
        why.append("the new binding names no proof")
    if {k: v for k, v in old.items() if k != "version"} == new:
        why.append("the new binding is the old one: nothing to repair")
    why += drops(old, new)
    why += ["the new proof %s" % w for w in typed_numbers(new.get("proof"))]
    return why


def packet(st, proposal=None):
    """The Setter/Judge's reading: the obligation, the old and new binding field by field, the comparison and what the
    machine screen saw. Plain text."""
    p = proposal or st.get("binding_proposal") or {}
    c = st.get("contract") or {}
    old, new = binding_of(c), p.get("binding") or {}
    lines = ["BINDING REPAIR for %s (proposed by %s at %s)" % (st.get("item"), p.get("by"), p.get("at")),
             "", "OBLIGATION v%d (unchanged by a repair): %s" % (obligation_of(c, st.get("item"))["version"],
                                                                  obligation_of(c, st.get("item"))["text"]),
             "", "BINDING v%d -> v%d, field by field:" % (old["version"], old["version"] + 1)]
    for k in BINDING_KEYS:
        a, b = old.get(k), new.get(k)
        if a or b:
            lines.append("  %-9s %s %s" % (k, "same   " if a == b else "CHANGED", json.dumps(a) if a == b else
                                            "%s\n            -> %s" % (json.dumps(a), json.dumps(b))))
    cmp_ = p.get("comparison") or {}
    lines += ["", "MEASURED BEFORE: %s" % cmp_.get("before"), "MEASURES AFTER:  %s" % cmp_.get("after"),
              "ACCEPTABLE BEHAVIOUR: %s" % cmp_.get("behaviour"), "DEFECT OF THE OLD BINDING: %s" % cmp_.get("defect"),
              "", "New numbers in the proof (a threshold may have moved): %s"
              % (", ".join(new_numbers(old.get("proof"), new.get("proof"))) or "none"),
              "", "Judge: APPROVE only if the new binding measures the same obligation at least as independently; "
              "REJECT a weakening; AMBIGUOUS keeps it blocked. "
              "relentless.py bind-judge --item %s --as <you> --verdict approve|reject|ambiguous --why \"...\""
              % st.get("item")]
    return "\n".join(lines)
