#!/usr/bin/env python3
"""surprise_book.py -- the Test Pilot's SURPRISE BOOK: what it has learned is boring, and where.

Owner, 2026-11-04: "when it finds what seems surprising (omg there are mushrooms everywhere) it then has a chance to
prove it's not surprising (oh, this is the rot biome, that makes sense) or (oh this is the... desert? That's not
right!) might require building some kind of context about what is surprising. If it keeps thinking boring things are
surprising we will need to retire some surprise. ... This can be the agent learning."  (SURPRISE_BOOK_BUILD_RETIRE_THE_BORING)

WHERE. infrastructure/state/testpilot/surprise_book.jsonl, committed. It is shared state that tools write and every
later sitting on any seat or host reads (CLAUDE.md "What is where": anyone-later -> the repo), not a cache: nothing
can rebuild it, it is the record of what each sitting saw and how each filing ended. Append-only JSONL, one event per
line, so two clones' additions merge as a union. RM_SURPRISE_BOOK overrides the path (selftests).

EVENTS. {"id", "ts", "event", "kind", "context", "sitting", ...}; "id" is unique per line, so a union merge's
duplicates collapse by id and order is (ts, outcome before its audit line, id), never file position.
  outcome  "outcome": explained | not_a_bug | sample_ok | real_bug | co_occurred | filed | superseded | abandoned,
           "evidence", "item"; a real_bug carries "cause" (below); a settled line carries "settles": <the filed id>
  sitting  `start` declares the sitting's context once: its sample is picked from that context, no narrower one
  retire   the key is now scored EXPECTED in that context; "for" = the outcome line that tipped it, "evidence" = the
           outcome lines that retired it
  revive   the key is surprising again at once; "for" = the real bug's outcome line, "evidence" = it and its cause
The per-key ENTRY (fold()) is a projection: kind, context, verdict expected|surprising, evidence, count, last_seen,
outcomes. Retired-ness comes from the outcome lines alone under surprise_rules.json, so `replay --rules` can ask what
other numbers would have done; retire/revive lines are the audit trail record() writes in the same locked write as
the outcome that changed the fold, and `check` fails when the two disagree.

THE RULE (numbers in surprise_rules.json, UNMEASURED until replayed). A (kind, context) RETIRES after `retire_after`
non-bug outcomes in a row (explained, not_a_bug, sample_ok) spread over at least `retire_min_sittings` sittings.
A real_bug outcome REVIVES it at once and resets the run; a key that has ever had a real bug needs
`retire_again_after_revive` to retire. A real bug counts against a key only when it is CAUSALLY LINKED to the
observation (owner 2026-11-04: "The item should only come back if it is correlated with a real bug and is shown to be
a direct result or cause of the bug, not just 'a mushroom was nearby'"): its "cause" is "<link>: <evidence>" with
<link> one of the rules' cause_links -- fix_commit (the bug's fix commit, its sha cited, names the observation's def
or mechanism), pilot_cause (the Test Pilot's recorded cause names it), gone_after_fix (the observation disappears
once the bug is fixed). A real_bug recorded without one is written as co_occurred ("co-occurred, not linked"): kept
against the entry, neutral, and a retired entry stays retired. filed, superseded, abandoned and co_occurred are
neutral. `settle` turns each filed line
into one settled outcome from its item's ledger state: done -> co_occurred (a fixed item is not yet a causal link:
record real_bug --cause to make it one), superseded -> superseded, dropped ->
not_a_bug, unless the drop reason is administrative (`abandoned_drop_reason`: duplicate, deferred, obsolete, ...),
which is abandoned -- a drop for no time says nothing about whether it was a bug.
Guards against normalising a real defect: a context is never empty, so retirement is always context-scoped
(kind=mushrooms_everywhere retired under biome=RM_TheRot says nothing about biome=RM_BlueDesert); a real bug in any
COMPATIBLE entry (no condition disagrees, e.g. biome=RM_TheRot;test=fire for a query biome=RM_TheRot) beats a
retirement; a def seen OFF the biome's roster contradicts a retirement; and each sitting re-checks
`sample_per_sitting` retired entries in its context (pick_sample: the one checked longest ago), recording sample_ok,
real_bug --cause or co_occurred, so silence is itself tested. Sitting ids are <ITEM>@<YYYY-MM-DDTHHMM> (its start, UTC): two sittings on one
day are two sittings. Timestamps are each host's UTC clock to the microsecond; skew between hosts can reorder two
sittings' lines, which is why a sitting's own lines carry its id.

EXPLAIN-AWAY (explain()). Before filing an ODD or ALARMING observation the pilot gets one attempt to prove it
unsurprising from context: the book (a retired key in this context), and, for the roster kinds in the rules
(creature_unexpected, plant_off_roster, mushrooms_everywhere, ...), the biome's real roster -- BiomeDef wildAnimals /
wildPlants read as XML elements PLUS the patch-added cast (UtinniPatches/Patches/WildAnimals_<Biome>.xml,
WildPlants_<Biome>.xml) via biome_group_sizes.rosters. Roster LIMITS: it is derived from src/, not from the running
game (a live state read beats it); a def named by an entry-level patch xpath (.../wildPlants/RM_X), carrying a zero
weight, or added under a PatchOperationFindMod naming a mod not under src/ is UNCERTAIN in that biome and never
explains; inheritance from a patched parent and the game's patch order are not modelled. The test's purpose and recent letters (jawa/vitals) are facts
only the pilot holds: it cites them with `record --outcome explained --evidence "<source>: <fact>"`. Otherwise the
observation STANDS and is filed (`record --outcome filed --item <ID>`).

    surprise_book.py start   --context biome=RM_TheRot --sitting <ITEM>@<YYYY-MM-DDTHHMM>   read at sitting start;
                             writes the sitting's one `sitting` line (its context: the sample is picked from it)
    surprise_book.py roster  --biome RM_TheRot
    surprise_book.py lookup  --kind K --context biome=X
    surprise_book.py explain --kind K --context biome=X --sitting S [--def RM_Agaripod ...]
    surprise_book.py record  --kind K --context biome=X --sitting S --outcome O --evidence TEXT [--item ID] [--sample]
    surprise_book.py settle                         filed lines whose item has ended -> their settled outcome
    surprise_book.py summary --sitting S            "explained <n>, retired <keys>" for the TESTPILOT_SAT note
    surprise_book.py check | replay [--rules FILE]
"""
import argparse
import contextlib
import datetime
import json
import os
import re
import sys
import uuid

try:
    import fcntl                # POSIX (WSL, Mac); on native Windows the book is written unlocked
except ImportError:
    fcntl = None

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BOOK = os.path.join(ROOT, "infrastructure", "state", "testpilot", "surprise_book.jsonl")
RULES = os.path.join(HERE, "surprise_rules.json")
KIND_RE = re.compile(r"^[a-z][a-z0-9_]{2,60}$")
COND_RE = re.compile(r"^([a-z][a-z_]*)=([A-Za-z0-9_.:-]+)$")
SITTING_RE = re.compile(r"^[A-Z][A-Z0-9_]*@\d{4}-\d{2}-\d{2}T\d{4}$")
OUTCOMES = ("explained", "not_a_bug", "sample_ok", "real_bug", "co_occurred", "filed", "superseded", "abandoned")
SAMPLE_ENDS = ("sample_ok", "real_bug", "co_occurred")


def linked(ev, rules):
    """The outcome this line folds as: a real bug with no causal link to the observation only co-occurred."""
    o = ev["outcome"]
    return "co_occurred" if o in rules["bug_outcomes"] and not ev.get("cause") else o


def check_cause(cause, rules):
    """'<link>: <evidence>' -> cause, or BookError."""
    m = re.match(r"^\s*([a-z_]+)\s*:\s*(.+)$", cause or "", re.S)
    links = rules["cause_links"]
    if not m or m.group(1) not in links or len(m.group(2).strip()) < 12:
        raise BookError("--cause %r: '<link>: <evidence>', link one of %s, evidence naming the observation's def or "
                        "mechanism" % (cause, ", ".join(links)))
    if m.group(1) == "fix_commit" and not re.search(r"\b[0-9a-f]{7,40}\b", m.group(2)):
        raise BookError("--cause fix_commit: cite the fix commit's sha")
    return cause.strip()
ROSTERS = ("wildAnimals", "wildPlants")


class BookError(ValueError):
    pass


def book_path():
    return os.path.abspath(os.environ.get("RM_SURPRISE_BOOK") or BOOK)


def load_rules(path=None):
    with open(path or RULES) as f:
        return json.load(f)


def parse_context(conds):
    """['biome=RM_TheRot', 'test=fire'] or 'biome=RM_TheRot;test=fire' -> {'biome': 'RM_TheRot', ...}. Never empty."""
    if isinstance(conds, dict):
        items = list(conds.items())
    else:
        parts = [p for c in ([conds] if isinstance(conds, str) else conds) for p in c.split(";") if p.strip()]
        items = []
        for p in parts:
            m = COND_RE.match(p.strip())
            if not m:
                raise BookError("context condition %r is not key=value" % p)
            items.append((m.group(1), m.group(2)))
    ctx = {}
    for k, v in items:
        if k in ctx and ctx[k] != v:
            raise BookError("context gives %s twice" % k)
        ctx[k] = v
    if not ctx:
        raise BookError("a context is never empty: retirement is always context-scoped (give biome=<defName>)")
    return ctx


def context_key(ctx):
    return ";".join("%s=%s" % kv for kv in sorted(ctx.items()))


def check_kind(kind):
    if not KIND_RE.match(kind or ""):
        raise BookError("kind %r: lowercase slug, e.g. mushrooms_everywhere, creature_off_roster" % kind)
    return kind


def check_sitting(sitting):
    if not SITTING_RE.match(sitting or ""):
        raise BookError("sitting %r: <ITEM>@<YYYY-MM-DDTHHMM>, the sitting's start in UTC" % sitting)
    return sitting


RANK = {"sitting": 0, "outcome": 1, "retire": 2, "revive": 2}


def _order(events):
    return sorted(events, key=lambda ev: (str(ev.get("ts")), RANK.get(ev.get("event"), 3), str(ev.get("id"))))


def read(path=None):
    """-> the book's events, duplicates collapsed (by id; by content for a line without one) and ordered by
    (ts, outcome before its audit line, id): the committed file merges as a union across clones, so duplicates and
    interleaving are expected and file position means nothing."""
    path = path or book_path()
    if not os.path.exists(path):
        return []
    out, seen = [], set()
    with open(path) as f:
        for n, line in enumerate(f, 1):
            if line.strip():
                try:
                    ev = json.loads(line)
                except ValueError:
                    raise BookError("%s:%d is not JSON" % (path, n))
                key = ev.get("id") or json.dumps(ev, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    out.append(ev)
    return _order(out)


@contextlib.contextmanager
def _locked(path):
    """Hold an exclusive lock on the book for a read-fold-append, so two writers cannot both fold the same old state."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        if fcntl:
            fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield f
        finally:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_UN)


def _write(f, lines):
    f.write("".join(json.dumps(w, sort_keys=True) + "\n" for w in lines))
    f.flush()


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _id():
    return uuid.uuid4().hex[:16]


def _step(e, ev, rules):
    """Fold one outcome line into its entry; -> the verdict it moved to, or None."""
    was = e["verdict"]
    e["count"] += 1
    e["last_seen"] = ev["ts"]
    o = linked(ev, rules)
    e["outcomes"][o] = e["outcomes"].get(o, 0) + 1
    if ev.get("evidence"):
        e["evidence"] = (e["evidence"] + [ev["evidence"]])[-3:]
    if o in SAMPLE_ENDS:
        e["last_checked"] = ev["ts"]
    if o in rules["bug_outcomes"]:
        if e["verdict"] == "expected":
            e["revived"] += 1
        e["verdict"], e["run"], e["last_bug"], e["retired_by"] = "surprising", [], ev, None
    elif o in rules["not_bug_outcomes"]:
        e["run"].append(ev)
        need = rules["retire_again_after_revive"] if e["last_bug"] else rules["retire_after"]
        if (e["verdict"] == "surprising" and len(e["run"]) >= need
                and len({r["sitting"] for r in e["run"]}) >= rules["retire_min_sittings"]):
            e["verdict"], e["retired_by"] = "expected", list(e["run"])
    return e["verdict"] if e["verdict"] != was else None


def fold(events, rules, observe=None):
    """-> {(kind, context_key): entry}. Pure: retired-ness from the outcome lines alone, in read() order.
    observe(ev, entry, moved_to) is called after each outcome line (check() uses it)."""
    out, settled = {}, set()
    for ev in events:
        if ev.get("event") != "outcome":
            continue
        if ev.get("settles"):
            if ev["settles"] in settled:      # two clones settled the same filing: it is one outcome, not two
                continue
            settled.add(ev["settles"])
        key = (ev["kind"], ev["context"])
        e = out.setdefault(key, {"kind": ev["kind"], "context": ev["context"], "verdict": "surprising",
                                 "evidence": [], "count": 0, "last_seen": None, "outcomes": {}, "run": [],
                                 "revived": 0, "last_bug": None, "retired_by": None, "last_checked": None})
        moved = _step(e, ev, rules)
        if observe:
            observe(ev, e, moved)
    return out


def _conds(entry):
    return parse_context(entry["context"]).items()


def matching(entries, kind, ctx):
    """Entries for `kind` whose context is a subset of `ctx` (an entry under biome=X also covers biome=X;test=Y)."""
    have = set(ctx.items())
    return [e for (k, c), e in sorted(entries.items()) if k == kind and set(_conds(e)) <= have]


def compatible(entries, kind, ctx):
    """Entries for `kind` with no condition that disagrees with `ctx`: the same situation, maybe described wider or
    narrower. A real bug in any of them beats a retirement."""
    return [e for (k, c), e in sorted(entries.items())
            if k == kind and all(ctx.get(ck, cv) == cv for ck, cv in _conds(e))]


def lookup(kind, ctx, events=None, rules=None):
    """-> {"verdict": EXPECTED|SURPRISING|NEW, "entry", "why"}. A real bug in any compatible entry beats a retirement."""
    rules = rules or load_rules()
    ctx = parse_context(ctx)
    ents = fold(read() if events is None else events, rules)
    bugs = [e for e in compatible(ents, check_kind(kind), ctx) if e["verdict"] == "surprising" and e["last_bug"]]
    if bugs:
        b = bugs[0]
        return {"verdict": "SURPRISING", "entry": b, "why": "real bug under %s: %s" % (
            b["context"], b["last_bug"].get("evidence") or b["last_bug"].get("item"))}
    hits = matching(ents, kind, ctx)
    retired = [e for e in hits if e["verdict"] == "expected"]
    if retired:
        r = retired[0]
        return {"verdict": "EXPECTED", "entry": r, "why": "retired under %s after %d non-bug outcomes: %s" % (
            r["context"], len(r["retired_by"]), "; ".join(x.get("evidence") or "" for x in r["retired_by"][-2:]))}
    if hits:
        return {"verdict": "SURPRISING", "entry": hits[0], "why": "known, not retired (run %d)" % len(hits[0]["run"])}
    return {"verdict": "NEW", "entry": None, "why": "the book has no %s under %s" % (kind, context_key(ctx))}


def pick_sample(ctx, sitting, events=None, rules=None):
    """-> the retired entries this sitting must re-check (the ones checked longest ago, key order on ties), or []
    once the sitting has recorded its sample_per_sitting sample outcomes. Deterministic."""
    rules = rules or load_rules()
    events = read() if events is None else events
    done = sum(1 for ev in events if ev.get("event") == "outcome" and ev.get("sitting") == sitting
               and ev.get("sample"))
    left = rules["sample_per_sitting"] - done
    if left <= 0:
        return []
    have = set(parse_context(ctx).items())
    retired = [e for e in fold(events, rules).values() if e["verdict"] == "expected" and set(_conds(e)) <= have]
    retired.sort(key=lambda e: (e["last_checked"] or e["retired_by"][-1]["ts"], e["kind"], e["context"]))
    return retired[:left]


def sitting_context(events, sitting):
    """-> the context the sitting declared at `start` (its earliest sitting line), or None."""
    for ev in events:
        if ev.get("event") == "sitting" and ev.get("sitting") == sitting:
            return ev["context"]
    return None


def begin(ctx, sitting, path=None, ts=None):
    """Write the sitting's one `sitting` line (its declared context), so its sample is picked from that context and
    no narrower one. -> the sitting's context (the first one declared wins)."""
    ckey = context_key(parse_context(ctx))
    path = path or book_path()
    with _locked(path) as f:
        events = read(path)
        lines = _heal(events, load_rules())
        have = sitting_context(events, sitting)
        if not have:
            lines.append({"id": _id(), "ts": ts or _now(), "event": "sitting", "sitting": sitting, "context": ckey})
        _write(f, lines)
    return have or ckey


_ROSTERS, _UNCERTAIN = {}, {}


def _bgs():
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
    import biome_group_sizes as bgs
    return bgs


def rosters(roster):
    """{biome: [defName]} for wildAnimals or wildPlants: inline BiomeDef elements plus patch-added rows, our live
    biomes only (biome_group_sizes.rosters; a vanilla biome is not under src/ and reads as unknown)."""
    if roster not in _ROSTERS:
        bgs = _bgs()
        defs, named, ops = bgs.collect(roster=roster)
        _ROSTERS[roster] = bgs.rosters(defs, ops, named, roster)
    return _ROSTERS[roster]


def _weight_le_zero(el):
    try:
        return float((el.text or "").strip()) <= 0
    except ValueError:
        return False


_OURS = []


def our_mod_names():
    """The <name> of every mod under src/ (About/About.xml): a FindMod naming only these runs (every mod of ours and
    every DLC is assumed loaded), any other name is a gate this reading cannot evaluate."""
    if not _OURS:
        import xml.etree.ElementTree as ET
        for dirpath, dirs, files in os.walk(os.path.join(ROOT, "src")):
            if os.path.basename(dirpath) == "About" and "About.xml" in files:
                try:
                    n = ET.parse(os.path.join(dirpath, "About.xml")).getroot().findtext("name")
                except ET.ParseError:
                    continue
                if n:
                    _OURS.append(n.strip())
    return set(_OURS)


BIOME_IN_XPATH = re.compile(r'BiomeDef\[defName\s*=\s*["\']([^"\']+)["\']\]')


def uncertain(roster):
    """{(biome, def)} whose place on `roster` the src/ reading cannot vouch for ("*" = any biome): named by an
    entry-level patch xpath (.../wildPlants/RM_X: a remove or edit biome_group_sizes does not model), carrying a
    weight <= 0, or added under a PatchOperationFindMod naming a mod not under src/ or in a FindMod's nomatch branch
    (our mods are assumed loaded, so it never runs; biome_group_sizes does not evaluate FindMod). Such a def never
    explains."""
    if roster not in _UNCERTAIN:
        bgs = _bgs()
        entry = re.compile(r"/%s/([A-Za-z_][A-Za-z0-9_]*)" % roster)
        ours = our_mod_names()
        out = set()
        for path in bgs.xml_files():
            top = bgs.parse(path)
            if top is None:
                continue
            if top.tag == "Defs":
                for el in top:
                    rows = el.find(roster) if el.tag == "BiomeDef" else None
                    biome = (el.findtext("defName") or "*").strip()
                    out |= {(biome, c.tag) for c in (rows if rows is not None else []) if isinstance(c.tag, str)
                            and _weight_le_zero(c)}
                continue
            if top.tag != "Patch":
                continue
            parents = {c: p for p in top.iter() for c in p}
            for op in top.iter():
                xp = (op.findtext("xpath") or "").strip()
                m = BIOME_IN_XPATH.search(xp)
                biome = m.group(1) if m else "*"
                out |= {(biome, d) for d in entry.findall(xp)}
                if not bgs.ROSTER_XPATHS[roster].search(xp):
                    continue
                val = op.find("value")
                rows = [c for c in (val.iter() if val is not None else []) if c is not val and isinstance(c.tag, str)
                        and c.tag != roster]
                out |= {(biome, c.tag) for c in rows if _weight_le_zero(c)}
                node, gated = op, False
                while node in parents:
                    prev, node = node, parents[node]
                    if node.get("Class", "") == "PatchOperationFindMod":
                        named = {(li.text or "").strip() for li in node.findall("mods/li")}
                        gated |= not named or not named <= ours or prev.tag == "nomatch"
                if gated:
                    out |= {(biome, c.tag) for c in rows}
        _UNCERTAIN[roster] = out
    return _UNCERTAIN[roster]


def roster(biome):
    """-> {"wildAnimals": [...] or None, "wildPlants": [...] or None}; None = this biome's roster is not readable here."""
    return {r: rosters(r).get(biome) for r in ROSTERS}


def _roster_facts(biome, defs, roster_of, uncertain_of):
    """-> (facts, on, off, doubtful) for `defs` against `biome`'s cast; on/off/doubtful are lists of defNames."""
    cast = roster_of(biome)
    if all(cast.get(r) is None for r in ROSTERS):
        return (["roster: %s is not one of our biomes under src/; its roster is unknown here" % biome], [], [], [])
    facts, on, off, doubt = [], [], [], []
    for d in defs:
        where = [r for r in ROSTERS if cast.get(r) and d in cast[r]]
        if any({(biome, d), ("*", d)} & uncertain_of(r) for r in ROSTERS):
            doubt.append(d)
            facts.append("roster: %s is UNCERTAIN on %s (entry-level patch, zero weight or gated on a mod not "
                         "under src/): a live state read decides, not the roster" % (d, biome))
        elif where:
            on.append(d)
            facts.append("roster: %s is on %s's %s (BiomeDef + patch-added)" % (d, biome, "/".join(where)))
        else:
            off.append(d)
            facts.append("roster: %s is NOT on %s's wildAnimals or wildPlants" % (d, biome))
    return facts, on, off, doubt


def explain(kind, ctx, sitting, defs=(), events=None, rules=None, roster_of=roster, uncertain_of=uncertain):
    """One attempt to prove an observation unsurprising from context. -> {"outcome": EXPLAINED|STANDS, "facts"}.
    Nothing is written: the pilot records what it decides."""
    rules = rules or load_rules()
    events = read() if events is None else events
    ctx = parse_context(ctx)
    seen = lookup(kind, ctx, events, rules)
    if seen["verdict"] == "SURPRISING" and seen["entry"] and seen["entry"]["last_bug"]:
        return {"outcome": "STANDS", "facts": ["book: " + seen["why"]]}
    sample = [e for e in pick_sample(sitting_context(events, sitting) or ctx, sitting, events, rules)
              if e["kind"] == kind]
    biome = ctx.get("biome")
    rfacts, on, off, doubt = _roster_facts(biome, defs, roster_of, uncertain_of) if biome and defs else ([], [], [], [])
    if seen["verdict"] == "EXPECTED" and not sample:
        if off or doubt:
            return {"outcome": "STANDS", "facts": ["book: " + seen["why"], "roster contradicts the retirement: %s" % (
                ", ".join(off + doubt))] + rfacts}
        return {"outcome": "EXPLAINED", "facts": ["book: " + seen["why"]] + rfacts}
    facts = []
    if sample:
        facts.append("book: retired, but it is this sitting's SAMPLE: re-check it by state read and record "
                     "--sample --outcome sample_ok|co_occurred, or real_bug --cause")
    facts += rfacts
    if rfacts and kind not in rules["roster_kinds"]:
        facts.append("roster: %s is not a roster kind (%s): roster membership does not explain it" % (
            kind, ", ".join(rules["roster_kinds"])))
    elif on and not off and not doubt and not sample:
        return {"outcome": "EXPLAINED", "facts": facts}
    if not sample:
        facts.append("no book or roster fact explains it: cite the test's purpose or a jawa/vitals letter with "
                     "record --outcome explained, else file it and record --outcome filed --item <ID>")
    return {"outcome": "STANDS", "facts": facts}


def _audit(ev, entry, moved):
    retire = moved == "expected"
    return {"id": _id(), "ts": ev["ts"], "event": "retire" if retire else "revive", "for": ev["id"],
            "kind": ev["kind"], "context": ev["context"], "sitting": ev["sitting"],
            "evidence": ([{"id": r["id"], "ts": r["ts"], "outcome": r["outcome"], "evidence": r.get("evidence"),
                           "sitting": r["sitting"]} for r in entry["retired_by"]] if retire else
                         [{"id": ev["id"], "ts": ev["ts"], "outcome": ev["outcome"], "evidence": ev.get("evidence"),
                           "item": ev.get("item"), "cause": ev.get("cause")}])}


def _outcome(events, kind, ckey, sitting, outcome, evidence, item, sample, rules, ts, settles, cause=None):
    """Build one outcome line and its audit line (if it moves the fold), against `events`. Writes nothing.
    A real_bug with no cause is written as co_occurred: it counts against nothing."""
    check_kind(kind)
    if outcome not in OUTCOMES:
        raise BookError("outcome %r: one of %s" % (outcome, ", ".join(OUTCOMES)))
    if cause and outcome not in rules["bug_outcomes"]:
        raise BookError("--cause belongs to a real_bug")
    if cause:
        cause = check_cause(cause, rules)
    elif outcome in rules["bug_outcomes"]:
        outcome, evidence = "co_occurred", "co-occurred, not linked: " + (evidence or "")
    if outcome in ("explained", "not_a_bug", "real_bug", "sample_ok", "co_occurred") and len(
            (evidence or "").replace("co-occurred, not linked:", "").strip()) < 8:
        raise BookError("%s needs --evidence: the context fact or state read it rests on" % outcome)
    if outcome == "filed" and not item:
        raise BookError("filed needs --item <ID>")
    if sample and outcome not in SAMPLE_ENDS:
        raise BookError("a sample re-check ends sample_ok, real_bug --cause or co_occurred")
    if outcome == "sample_ok" and not sample:
        raise BookError("sample_ok is only for a sampled retired entry (--sample)")
    if not sitting:
        raise BookError("--sitting <ITEM>@<YYYY-MM-DDTHHMM> is required")
    if sample:
        sctx = sitting_context(events, sitting)
        if not sctx:
            raise BookError("--sample: sitting %s never ran `start`, so it has no pick" % sitting)
        if not any((e["kind"], e["context"]) == (kind, ckey) for e in pick_sample(sctx, sitting, events, rules)):
            raise BookError("--sample: %s@%s is not this sitting's pick under %s (`start` names it; the quota may be "
                            "spent)" % (kind, ckey, sctx))
    ev = {"id": _id(), "ts": ts or _now(), "event": "outcome", "kind": kind, "context": ckey, "sitting": sitting,
          "outcome": outcome, "evidence": evidence}
    last = max([str(e.get("ts")) for e in events if (e.get("kind"), e.get("context")) == (kind, ckey)] or [""])
    if ev["ts"] < last:
        raise BookError("%s@%s already has a line at %s, later than %s: the book is not written backwards (a clock "
                        "behind another host's?)" % (kind, ckey, last, ev["ts"]))
    if item:
        ev["item"] = item
    if sample:
        ev["sample"] = True
    if settles:
        ev["settles"] = settles
    if cause:
        ev["cause"] = cause
    moved = []
    fold(_order(events + [ev]), rules, observe=lambda o, e, m: moved.append(_audit(o, e, m)) if (o is ev and m) else None)
    return [ev] + moved


def record(kind, ctx, sitting, outcome, evidence="", item=None, sample=False, path=None, rules=None, ts=None,
           settles=None, cause=None):
    """Append one outcome line and, if it changes the key's verdict, its retire or revive line, in one locked write.
    -> the lines written."""
    rules = rules or load_rules()
    ckey = context_key(parse_context(ctx))
    path = path or book_path()
    with _locked(path) as f:
        lines = _outcome(read(path), kind, ckey, sitting, outcome, evidence, item, sample, rules, ts, settles, cause)
        _write(f, lines)
    return lines


def drop_reasons(ledger_events):
    """{item: the reason of its last drop} from raw ledger events."""
    out = {}
    for ev in ledger_events:
        if ev.get("event") == "drop":
            out[ev.get("id")] = ev.get("reason") or ""
    return out


def settle(world, path=None, rules=None, ts=None, reasons=None):
    """Each filed line whose item has ended and is not yet settled -> one settled outcome line linked to it by id.
    dropped -> not_a_bug, or abandoned when the drop reason (reasons: {item: text}) is administrative."""
    rules = rules or load_rules()
    reasons = reasons or {}
    admin = re.compile(rules["abandoned_drop_reason"])
    path = path or book_path()
    out = []
    with _locked(path) as f:
        events = read(path)
        settled = {ev.get("settles") for ev in events if ev.get("event") == "outcome" and ev.get("settles")}
        out += _heal(events, rules)
        for ev in [e for e in events if e.get("event") == "outcome" and e["outcome"] == "filed"]:
            if ev.get("id") in settled:
                continue
            it = world.items.get(ev.get("item"))
            to = rules["settle_states"].get(it.state) if it else None
            if not to:
                continue
            why = "item %s ended %s" % (ev["item"], it.state)
            if to == "co_occurred":
                why += "; no causal link to this observation is recorded (record real_bug --cause to make one)"
            if it.state == "dropped" and admin.search(reasons.get(ev["item"], "")):
                to, why = "abandoned", why + " for an administrative reason: " + reasons[ev["item"]][:120]
            elif it.state == "dropped":
                why += ": " + (reasons.get(ev["item"]) or "no reason read")[:120]
            lines = _outcome(events, ev["kind"], ev["context"], ev["sitting"], to, why, ev["item"], False, rules,
                             ts, ev.get("id") or "legacy")
            settled.add(ev.get("id"))
            events = _order(events + lines)
            out += lines
        _write(f, out)
    return out


def summary(sitting, events=None):
    """-> 'explained <n>, retired <keys>, revived <keys>' for the TESTPILOT_SAT note."""
    events = read() if events is None else events
    mine = [ev for ev in events if ev.get("sitting") == sitting]
    n = sum(1 for ev in mine if ev.get("event") == "outcome" and ev["outcome"] == "explained")
    ret = ["%s@%s" % (ev["kind"], ev["context"]) for ev in mine if ev.get("event") == "retire"]
    rev = ["%s@%s" % (ev["kind"], ev["context"]) for ev in mine if ev.get("event") == "revive"]
    return "explained %d, retired %s, revived %s" % (n, ",".join(ret) or "none", ",".join(rev) or "none")


def _audits(events, rules):
    """-> (problems with audit lines, [audit line owed]) -- see check()."""
    pos, trans = {}, {}
    def note(ev, e, moved):
        pos[ev.get("id")] = (len(pos), (ev["kind"], ev["context"]))
        if moved:
            trans.setdefault((ev["kind"], ev["context"]), []).append(
                [pos[ev.get("id")][0], "retire" if moved == "expected" else "revive", False, _audit(ev, e, moved)])
    fold(events, rules, observe=note)
    # An audit whose outcome the fold now passes over changes nothing and proves nothing: a second clone's settlement
    # of a filing already settled (whatever it settled to), or a real_bug with no causal link (one written before
    # the 2026-11-04 cause rule had its revive line). Such an audit is inert: neither a problem nor a record.
    inert, first = set(), set()
    for ev in events:
        if ev.get("event") != "outcome":
            continue
        if ev.get("settles"):
            if ev["settles"] in first:
                inert.add(ev.get("id"))
            first.add(ev["settles"])
        if linked(ev, rules) != ev["outcome"]:
            inert.add(ev.get("id"))
    problems = []
    for ev in events:
        if ev.get("event") in ("retire", "revive") and ev.get("for") in inert:
            continue
        if ev.get("event") in ("retire", "revive"):
            key = (ev.get("kind"), ev.get("context"))
            at = pos.get(ev.get("for"))
            opened = [t for t in trans.get(key, []) if at and at[1] == key and t[0] <= at[0]]
            if not opened or opened[-1][1] != ev["event"]:
                problems.append("%s %s@%s at %s: no outcome line makes that change (for=%s)" % (
                    ev["event"], key[0], key[1], ev.get("ts"), ev.get("for")))
            else:
                opened[-1][2] = True
        elif ev.get("event") not in ("outcome", "sitting"):
            problems.append("unknown event %r at %s" % (ev.get("event"), ev.get("ts")))
    owed = [t[3] for key, ts in sorted(trans.items()) for t in ts if not t[2]]
    return problems, owed


def _heal(events, rules):
    """-> the audit lines a union merge left owed (each clone's lines were valid alone, their union crosses the
    threshold): written by the next start or settle, under the lock, so the trail catches up with the fold."""
    return _audits(events, rules)[1]


def heal(path=None, rules=None):
    rules = rules or load_rules()
    path = path or book_path()
    with _locked(path) as f:
        owed = _heal(read(path), rules)
        _write(f, owed)
    return owed


def check(events=None, rules=None):
    """-> problems. Every verdict change the fold makes on a key must have an audit line, and every audit line must
    name ("for") an outcome of that key that lies in a stretch the fold opened with the same change. The stretch,
    not the exact outcome: two clones that each retired a key on their own third outcome merge into one retirement
    at the earlier one, and the later clone's audit then sits inside that stretch -- redundant, not forged. A change
    with no audit (two clones' lines crossing the threshold only together) is owed; `start` and `settle` heal it."""
    rules = rules or load_rules()
    problems, owed = _audits(read() if events is None else events, rules)
    return problems + ["%s %s@%s: the fold makes this change at outcome %s but no audit line records it (heal: run "
                       "start or settle)" % (w["event"], w["kind"], w["context"], w["for"]) for w in owed]


def _ctx_arg(p):
    p.add_argument("--context", action="append", required=True, help="key=value, e.g. biome=RM_TheRot (repeatable)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); _ctx_arg(s); s.add_argument("--sitting", required=True)
    s = sub.add_parser("roster"); s.add_argument("--biome", required=True)
    s = sub.add_parser("lookup"); s.add_argument("--kind", required=True); _ctx_arg(s)
    s = sub.add_parser("explain"); s.add_argument("--kind", required=True); _ctx_arg(s)
    s.add_argument("--sitting", required=True); s.add_argument("--def", dest="defs", action="append", default=[])
    s = sub.add_parser("record"); s.add_argument("--kind", required=True); _ctx_arg(s)
    s.add_argument("--sitting", required=True); s.add_argument("--outcome", required=True, choices=OUTCOMES)
    s.add_argument("--evidence", default=""); s.add_argument("--item"); s.add_argument("--sample", action="store_true")
    s.add_argument("--cause", help="real_bug only: '<link>: <evidence>' (fix_commit | pilot_cause | gone_after_fix); "
                                   "without it a real_bug is recorded as co_occurred and revives nothing")
    sub.add_parser("settle")
    s = sub.add_parser("summary"); s.add_argument("--sitting", required=True)
    sub.add_parser("check")
    s = sub.add_parser("replay"); s.add_argument("--rules")
    a = ap.parse_args(argv)
    try:
        if getattr(a, "sitting", None):
            check_sitting(a.sitting)
        if a.cmd == "start":
            ctx = parse_context(begin(a.context, a.sitting))
            rules = load_rules()
            events = read()
            ents = fold(events, rules)
            mine = [e for e in ents.values() if all(ctx.get(k, v) == v for k, v in _conds(e))]
            print("SURPRISE BOOK %s, sitting %s, context %s: %d entries apply (rules %s)" % (
                book_path(), a.sitting, context_key(ctx), len(mine), rules["_status"].split(":")[0]))
            for e in sorted(mine, key=lambda e: (e["verdict"], e["kind"], e["context"])):
                v = lookup(e["kind"], ctx, events, rules)
                tag = ("SURPRISING (real bug)" if e["last_bug"] and e["verdict"] == "surprising" else
                       "EXPECTED (retired)" if e["verdict"] == "expected" and v["verdict"] == "EXPECTED" else
                       "retired, overruled" if e["verdict"] == "expected" else "surprising, run %d" % len(e["run"]))
                print("  %-22s %s @ %s, %d seen, last %s" % (tag, e["kind"], e["context"], e["count"], e["last_seen"]))
            for e in pick_sample(ctx, a.sitting, rules=rules):
                print("SAMPLE this sitting: re-check %s @ %s by state read; record --sample --outcome "
                      "sample_ok|co_occurred, or real_bug --cause" % (e["kind"], e["context"]))
            if "biome" in ctx:
                r = roster(ctx["biome"])
                print("ROSTER %s: %s" % (ctx["biome"], ", ".join(
                    "%s %s" % (k, "unknown" if v is None else len(v)) for k, v in r.items())))
            kinds = sorted({e["kind"] for e in ents.values()})
            print("KINDS in the book (reuse one when it fits): %s" % (", ".join(kinds) or "none yet"))
        elif a.cmd == "roster":
            print(json.dumps(roster(a.biome), indent=1))
        elif a.cmd == "lookup":
            v = lookup(a.kind, a.context)
            print("%s: %s" % (v["verdict"], v["why"]))
        elif a.cmd == "explain":
            v = explain(a.kind, a.context, a.sitting, a.defs)
            print(v["outcome"])
            for f in v["facts"]:
                print("  " + f)
        elif a.cmd == "record":
            for w in record(a.kind, a.context, a.sitting, a.outcome, a.evidence, a.item, a.sample, cause=a.cause):
                print("%s %s@%s%s" % (w["event"].upper(), w["kind"], w["context"],
                                      " " + w["outcome"] if w["event"] == "outcome" else ""))
        elif a.cmd == "settle":
            sys.path.insert(0, os.path.dirname(HERE))
            from rimflow import model
            evs = model.read()
            for w in settle(model.replay(evs), reasons=drop_reasons(evs)):
                print("%s %s@%s %s" % (w["event"].upper(), w["kind"], w["context"], w.get("outcome", "")))
        elif a.cmd == "summary":
            print(summary(a.sitting))
        elif a.cmd == "check":
            probs = check()
            for p in probs:
                print("PROBLEM " + p)
            print("surprise book: %d events, %d problems" % (len(read()), len(probs)))
            return 1 if probs else 0
        elif a.cmd == "replay":
            rules = load_rules(a.rules)
            ents = fold(read(), rules)
            for (k, c), e in sorted(ents.items()):
                print("%-10s %s@%s outcomes %s revived %d" % (e["verdict"], k, c, e["outcomes"], e["revived"]))
    except (BookError, OSError) as e:
        print("surprise_book: " + str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
