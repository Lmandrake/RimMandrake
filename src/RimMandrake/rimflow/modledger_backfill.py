#!/usr/bin/env python3
"""modledger_backfill.py — import one mod's state from today's stores into its mod ledger, in SHADOW mode.

Spec design/specs/2026-11-15-holder-pipeline-fusion.md §3.8 steps 2-3; plan step 3. Every event is written by the
`BACKFILL` writer and cites the old file (and the row or line) it came from. Nothing old is redirected, archived or
deleted: the views are generated beside the old files, and `compare` prints where the old files disagree with each
other or with the ledger.

    python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod ExplosiveKnockback        # writes the ledger
    python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod ExplosiveKnockback --dry  # counts only
    python3 src/RimMandrake/rimflow/modledger_backfill.py compare --mod ExplosiveKnockback    # shadow disagreements

Stores read (each optional; a missing one is said, never guessed): version/VERSION.json, version/stage_record.json,
version/locked_bars.json, version/test_table.json, version/in_game/visit_*/rows.jsonl,
version/blind_challenge/cycle_*/lane2/faults.json, version/criterion_repairs/*/, version/run_spend.jsonl,
journal.md ("His words on this mod"), the live rimflow items naming the mod, and the OWNER ledger shards' events naming
the mod that carry his words (ownerSaid) or a card (byCard). Run twice, it writes nothing new (idempotent keys).
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402
import modledger_reader as R                                     # noqa: E402

W = "BACKFILL"


def _rel(root, p):
    return os.path.relpath(p, root)


def _load(p):
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _jsonl(p):
    out = []
    try:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def _last(rec):
    """A red or green record is one dict or a list of them (one per commit it ran on): the last is the one that counts."""
    if isinstance(rec, list):
        rec = rec[-1] if rec else {}
    return rec if isinstance(rec, dict) else {}


SHA_RE = re.compile(r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{7,40}\b")
PATH_RE = re.compile(r"(?<![\w/.-])((?:src|design|infrastructure|skills)/[\w./-]*\w\.[A-Za-z]{1,5})\b")
# a sentence that STATES a refutation ('False theory: X', 'D7 refuted', 'was refuted', 'refuted by'), never the
# adjective ('a refuted cause')
REFUTED_RE = re.compile(r"(?i:false theor(?:y|ies)\s*:)|\b(?i:is|was|were|are|been|now)\s+(?i:refuted)\b|"
                        r"\b[A-Z][A-Za-z0-9_]*\)?\s+refuted\b|\b(?i:refuted)\s*(?:by|at|on|:)")
NOT_REFUTED_RE = re.compile(r"\b(?:not|never|un)[- ]?refuted\b|\b(?:not|never|can't|cannot|can not|couldn't|could "
                            r"not) (?:yet )?(?:be )?ruled out\b|^\W*-{3}|\bcriterion:", re.I)


TOOLING_RE = re.compile(r"\bmod ledger\b", re.I)

# ruled-out causes and traps under ANY of the wordings tickets use (the judges' rule 2); a cause needs a sha to pin it,
# else it is mined as the trap it is for the next reader ('X looks like the cause; it was ruled out')
CAUSE_RE = re.compile(r"\bruled out\b|\bnot (?:the|a) (?:cause|culprit)\b|\bwas not (?:the|a) (?:cause|bug|defect)\b|"
                      r"\bno [\w-]+(?: [\w-]+)? (?:bug|defect) in\b|\bfault was in\b|\bexplained\b|\bred herring\b|"
                      r"\bnot (?:caused by|due to)\b|\brather than (?:the |a )?(?:mod|[A-Z][A-Za-z]+(?:Knockback|Slack|Works))\b",
                      re.I)
TRAP_RE = re.compile(r"\bCorrection:|\bturned out\b|\bgreen because\b|\bis green\b[^.]{0,80}\bbecause\b|"
                     r"\bexits? \d+ for both\b|\bgreen for the wrong\b|\bfalse pass\b|\bno longer resolves\b", re.I)
WHERE_RE = re.compile(r"`([^`]{2,160})`|((?:src|design|infrastructure|skills)/[\w./-]*\w)|\b([\w-]+\.(?:py|cs|xml|json|"
                      r"jsonl|md))\b|\b(T_[A-Z0-9_]{2,})\b")
# owner words ride on these events as authority for the act, never as a statement about the mod (the judges' rule 3)
OWNER_WORD_EVENTS = ("note", "file", "close", "drop", "supersede")
FLEET_WIDE_IDS = 3                     # the same words on this many tickets are a fleet-wide order, not about one mod
BULK_STAMP_IDS = 3                     # one OWNER sha stamped `implemented` on this many tickets is a bulk re-stamp
PROVENANCE_RE = re.compile(r"(?i)^\W*(?:found[- ]by\b|found by\b|verdict:|written by the producer|producer\b|"
                           r"status at filing|step \d+ of\b|detached run\b[:,]?|relentless:)")
LEAD_NOISE_RE = re.compile(r"(?i)^(?:detached run(?: ended \w+)?|closed?(?: at [0-9a-f]+)?(?: by \w+)?)\s*[:;,.-]\s*")
CAUSE_LINE_RE = re.compile(r"(?i)\b(?:root )?cause(?: \[[^\]]*\])?\s*:\s*(.+)")


def _closed_like(state):
    return state in ("done", "dropped", "superseded")


_STATES = {}


def _fold(evs):
    """A minimal fold of a ticket's rimflow verbs, for a root that is not this checkout (a fixture): close -> done,
    drop -> dropped, supersede -> superseded, reopen -> ready, implemented -> built unless done."""
    st = "proposed"
    for t in evs:
        k = t[2].get("event")
        if k == "close":
            st = "done"
        elif k == "drop":
            st = "dropped"
        elif k == "supersede":
            st = "superseded"
        elif k == "reopen":
            st = "ready"
        elif k == "implemented" and st not in ("done", "dropped", "superseded"):
            st = "built"
    return st


def rimflow_states(root, names, tev):
    """-> {ticket: its FINAL rimflow state} (the judges' rule 1). On this checkout it is rimflow's own fold
    (`model.replay` over every shard and the frozen ledger: a refused or bulk event moves nothing there either); on
    any other root (a fixture) the minimal fold of its events."""
    try:
        import model
        here = os.path.realpath(model.ROOT) == os.path.realpath(root)
    except ImportError:
        here = False
    if here:
        if root not in _STATES:
            w = model.replay(model.read())
            _STATES[root] = {i: getattr(it, "state", None) for i, it in w.items.items()}
        return {n: _STATES[root].get(n) for n in names}
    return {n: _fold(tev.get(n, [])) for n in names}


def bulk_shas(root):
    """-> the shas an OWNER `implemented` event stamped on BULK_STAMP_IDS or more tickets (a bulk re-stamp such as
    2026-11-06's c29007b6b66e): never the fix a ticket's claim names while its own builder's sha lands."""
    ids = {}
    for sp in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "*.jsonl"))):
        with open(sp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"implemented"' not in line or '"OWNER"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("event") == "implemented" and e.get("seat") == "OWNER" and isinstance(e.get("sha"), str):
                    ids.setdefault(e["sha"][:12], set()).add(e.get("id"))
    return {sha for sha, v in ids.items() if len(v) >= BULK_STAMP_IDS}


def fleet_words(root):
    """-> the owner words (ownerSaid or byCard) attached to FLEET_WIDE_IDS or more tickets: fleet-wide orders."""
    ids = {}
    for sp_ in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER*.jsonl"))):
        for e in _jsonl(sp_):
            for k in ("ownerSaid", "byCard"):
                if e.get(k):
                    ids.setdefault(str(e[k]), set()).add(e.get("id"))
    return {k for k, v in ids.items() if len(v) >= FLEET_WIDE_IDS}


def clean_lead(text):
    """A close reason or note without its run-history lead ('detached run: ', 'Closed at X by Y: ')."""
    t = " ".join(str(text or "").split())
    for _ in range(3):
        t2 = LEAD_NOISE_RE.sub("", t)
        if t2 == t:
            break
        t = t2
    return t


def where_of(sentence, fallback):
    m = WHERE_RE.search(sentence)
    return fit(next(g for g in m.groups() if g), 160) if m else fallback


def split_bars(bar, locked):
    """A fault's `bar` may list several ('no_hose, no_hose_in_gss'): -> the locked ids among them, in order."""
    out = []
    for b in re.split(r"[,;/]|\band\b", str(bar or "")):
        b = b.strip().strip("()` ")
        if b in locked and b not in out:
            out.append(b)
    return out


def defect_paras(prose):
    """A ticket's paragraphs with headings and provenance (found-by, Producer re-plan, 'Step N of') left out."""
    return [x.strip() for x in prose.split("\n\n") if x.strip() and not x.lstrip().startswith("#")
            and not PROVENANCE_RE.match(x.strip().lstrip("-* "))]


def fix_line(texts):
    """The ticket's own 'Fix:' line, from its prose or notes: -> the words after it, or None."""
    for t in texts:
        m = re.search(r"(?im)^\W*(?:\*\*)?(?:proposed )?fix(?:\*\*)?\s*:\s*(.+)", str(t or ""))
        if m and len(m.group(1).strip()) >= 12:
            return words_of(m.group(1)).strip()
    return None


def accept_line(texts):
    """The acceptance test the ticket filed: an 'Acceptance test:' line in its prose, its filing or its notes."""
    for t in texts:
        m = re.search(r"Acceptance test:\s*(.+)", str(t or ""))
        if m and words_of(m.group(1)).strip():
            return words_of(m.group(1)).strip()
    return None




def _closed_in_ledger(evs):
    """A ticket with no prose file is closed when its last close, drop or supersede has no reopen after it."""
    state = False
    for t in evs:
        k = t[2].get("event")
        if k in ("close", "drop", "supersede"):
            state = True
        elif k == "reopen":
            state = False
    return state


def ticket_events(root, names):
    """-> {ticket id: [(shard path, line number, event)]} for the rimflow ledger events on those tickets, in tsn order."""
    out = {}
    for sp in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "*.jsonl"))):
        with open(sp, encoding="utf-8", errors="replace") as fh:
            for ln, line in enumerate(fh, 1):
                m = re.search(r'"id": ?"([A-Z0-9_]+)"', line)
                if not m or m.group(1) not in names:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("id") in names:
                    out.setdefault(e["id"], []).append((sp, ln, e))
    for v in out.values():
        v.sort(key=lambda t: t[2].get("tsn") or 0)
    return out


def _sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.;])\s+(?=[A-Z(])", " ".join(str(text or "").split())) if x.strip()]


def _words(mod):
    """CamelCase -> the spaced name ('ExplosiveKnockback' -> 'Explosive Knockback') and the item-name word."""
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", mod)
    return spaced, spaced.split()[-1].upper()


def fit(text, cap):
    """One paragraph of at most `cap` chars: a longer text keeps its leading whole sentences (or, when the first
    sentence alone is longer, its leading whole clauses), never a '[…]' marker (the judges' rule 6: a cut that hides
    the fact behind a marker reads as the fact). The event cites the old file that holds the whole (standard rule 3)."""
    t = " ".join(str(text or "").split())
    if len(t) <= cap:
        return t
    head = t[:cap + 1]   # cut-ok: whole sentences or clauses only; the event cites the old file holding the whole
    stop = max(head.rfind(". "), head.rfind("; "), head.rfind("? "), head.rfind("! "))
    if stop >= 40:
        return head[:stop + 1].rstrip(" ;")
    stop = max(head.rfind(", "), head.rfind(" — "), head.rfind(": "), head.rfind(" ("))
    if stop >= 40:
        return head[:stop].rstrip(" ,;:—")
    return head[:head.rfind(" ")].rstrip(" ,;:") if " " in head else head[:cap]


def words_of(text):
    """The words of a ticket section: code fences unwrapped (a fenced command is words), cut at the first pasted
    stack or traceback (the standard refuses one; the event cites the ticket that holds it)."""
    t = str(text or "").replace("```", " ")
    m = M.STACK_RE.search(t)
    t = " ".join((t[:m.start()] if m else t).split())
    m = M.STACK_RE.search(t)                 # a traceback wrapped across lines matches only once joined
    return t[:m.start()] if m else t


def slug(text, words=6):
    return "-".join(re.findall(r"[a-z0-9]+", str(text or "").lower())[:words]) or "untitled"


QUOTE_RE = re.compile(r"[\"“]([^\"”]{2,})[\"”]")


def _said(text):
    """His words from a line that quotes them: the quoted parts, verbatim, joined by ' · ' (the journal's own
    separator); the line itself when it quotes nothing."""
    q = QUOTE_RE.findall(text or "")
    return " · ".join(x.strip() for x in q) if q else " ".join(str(text or "").split())


def _tags(prose):
    p = prose.lower()
    out = [t for t, words in (("live", ("live", "in-game", "in game", "bridge")), ("test", ("selftest", "proof", "test")),
                              ("settings", ("setting",)), ("perf", ("perf", "tick budget")),
                              ("art", ("sprite", "texture", " art ")), ("other-mod", ("flowworks", "cauldron")))
           if any(w in p for w in words)]
    return out or ["code"]


def item_titles(root):
    """-> {item id: the one-line title its filer wrote}: rimflow's `file` events (a title is the filer's own statement
    of the item; an item's first paragraph is often shared boilerplate, e.g. 'Step N of plan.md (...)')."""
    out = {}
    for sp in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "*.jsonl"))):
        with open(sp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"file"' not in line or '"title"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("event") == "file" and isinstance(e.get("id"), str) and isinstance(e.get("title"), str):
                    out[e["id"]] = e["title"]
    return out


def other_mod_words(root, mod):
    """The item-name words that name ANOTHER concept mod (its squashed name, its last CamelCase word when it is 5+
    letters): an item named for another mod is that mod's, even when it cites this one as a precedent."""
    out = set()
    for m in os.listdir(os.path.join(root, "design", "concepts")) if os.path.isdir(
            os.path.join(root, "design", "concepts")) else []:
        if m == mod or not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", m):
            continue
        out.add(m.upper().replace("_", ""))
        last = _words(m)[1]
        if len(last) >= 5:
            out.add(last)
    return out


def _mine_finding(add, name, prose, titles, locked, S, src, texts=(), reading=None):
    """One ticket's finding.open: its defect (the filer's title, else its first paragraph that is not provenance), its
    own 'Fix:' line or its spec as the proposed fix, the acceptance test it filed (prose, filing or notes; else its
    criteria; else its verify section). `texts` are the ticket's rimflow event texts; `reading` (a per-ticket reading,
    see read_tickets) replaces a field only where it holds one."""
    reading = reading or {}
    paras = defect_paras(prose)
    m = re.search(r"^## spec\s*\n(.*?)(?=^## |\Z)", prose, re.S | re.M)
    spec = " ".join(x for x in defect_paras(m.group(1)) if not x.startswith("Acceptance test:")) if m else ""
    fix = (fix_line([prose] + list(texts)) or words_of(spec).strip() or
           "not written by its filer: read item:%s" % name)
    crit = re.search(r"^## criteria\s*\n(.*?)(?=^## |\Z)", prose, re.S | re.M)
    crit = " ".join(defect_paras(crit.group(1))).lstrip("-* ") if crit else ""
    ver = re.search(r"^## verify\s*\n(.*?)(?=^## |\Z)", prose, re.S | re.M)
    acc = accept_line([prose] + list(texts)) or words_of(crit).strip() or (words_of(ver.group(1)).strip() if ver else
                                                                           "") or "none, not written at filing"
    named_bars = [b for b in locked if re.search(r"\b%s\b" % re.escape(b), prose)][:3]
    bars = [b for b in reading.get("bars") or [] if b in locked] or named_bars
    text = titles.get(name) or (words_of(paras[0]).strip() if paras else "") or name
    cls = ("polish" if re.search(r"\bpolish\b", prose, re.I) and not re.search(r"\bproblem\b", prose, re.I)
           else "problem")
    add("finding.open", "finding:" + name, {
        "class": reading.get("class") if reading.get("class") in ("problem", "polish") else cls,
        "bars": bars, "tags": [] if bars else _tags(prose),
        "text": fit(reading.get("defect") or text, S["text"]),
        "proposed_fix": fit(reading.get("proposed_fix") or fix, S["proposed_fix"]),
        "accept": fit(reading.get("accept") or acc, S["accept"])},
        src)           # the old file first: evidence[0] is what the backfill came from


def changed_text(evs, sha):
    """What a fix changed, from the ticket's own words: its close reason and the 'Cause:' line of its notes, each
    without run history; -> the text, or a plain pointer when the record names no change."""
    parts = []
    for t in evs:
        e = t[2]
        for k in ("text", "reason", "why"):
            m = CAUSE_LINE_RE.search(str(e.get(k) or "")) if e.get("event") in ("note", "implemented", "close") else None
            if m:
                c = _sentences(m.group(1))[0] if _sentences(m.group(1)) else m.group(1)
                if c not in parts:
                    parts.insert(0, "cause: " + c)
    close = next((t[2] for t in reversed(evs) if t[2].get("event") in ("close", "implemented") and
                  (t[2].get("reason") or t[2].get("why"))), None)
    if close:
        r = clean_lead(close.get("reason") or close.get("why"))
        if r and not re.match(r"(?i)^(detached run|re-pointed|re-recorded)\b", r):
            parts.insert(0, r)
    return "; ".join(parts) if parts else "Fixed at %s; the record names no change beyond its title" % sha


def _final_state(name, evs, S, state=None, landed=None, bulk=(), reading=None):
    """-> (kind, body, sha, ledger ref pattern) for a ticket's FINAL rimflow state (the judges' rule 1), or None.
    `state` is rimflow's fold of the ticket: proposed / ready / doing (reopened included) state no fix; dropped and
    superseded nothing. done with noCode -> finding.withdrawn; done, built or validated with a verify pass ->
    finding.verified; else finding.claimed_fixed. The sha is the last one its own builders stamped that lands on
    origin/main; a bulk OWNER re-stamp (`bulk`) only when nothing else lands. A verify is read, never mined."""
    landed = landed or (lambda x: x)
    reading = reading or {}
    if state is None:
        state = _fold(evs)
    if state not in ("done", "built", "validated"):
        return None
    term = [t for t in evs if t[2].get("event") in ("close", "implemented") and isinstance(t[2].get("sha"), str) and
            re.match(r"^[0-9a-f]{7,40}$", t[2]["sha"])]
    verify = [t[2] for t in evs if t[2].get("event") == "verify" and t[2].get("result") == "pass"]
    close = next((t for t in reversed(evs) if t[2].get("event") == "close"), None)
    if state == "done" and close and close[2].get("noCode"):
        nc = str(close[2]["noCode"])
        sha = close[2].get("sha") if isinstance(close[2].get("sha"), str) else None
        if not sha:
            return None
        how = "reading+test" if re.search(r"\b(selftest|test)\b", nc, re.I) else "reading"
        return ("finding.withdrawn", {"text": fit("No defect at %s: %s" % (sha, nc), S["text"]), "how_checked": how},
                sha, "ledger:%%s:%d" % close[1])
    pick = None
    for t in reversed(term):
        if t[2]["sha"][:12] not in bulk and landed(t[2]["sha"]):
            pick = t
            break
    if pick is None:
        pick = next((t for t in reversed(term) if landed(t[2]["sha"])), term[-1] if term else None)
    if pick is None:
        return None
    sha = pick[2]["sha"]
    ref = "ledger:%%s:%d" % pick[1]
    did = reading.get("changed") or changed_text(evs, sha)
    impl = next((t[2] for t in reversed(evs) if t[2].get("event") == "implemented" and t[2].get("criteria")), {})
    crit = "; ".join("%s %s" % (c.get("id"), c.get("text")) for c in impl.get("criteria") or [] if isinstance(c, dict))
    if verify:
        v = verify[-1]
        return ("finding.verified", {"text": fit("%s; verified: %s" % (did, clean_lead(v.get("config")) or
                                                                       "a verify pass"), S["text"])},
                sha, ref)
    test = crit or "none recorded at %s (live: %s)" % ("close" if state == "done" else "build",
                                                       (close[2].get("live") if close else None) or "-")
    return ("finding.claimed_fixed", {"text": fit(did, S["text"]), "test": fit(test, S["test"])}, sha, ref)


def readings_path(root, mod):
    """The committed per-ticket readings of one mod (read_tickets writes them; every clone's re-mine reads them, so a
    re-run without --read keeps what the reading found instead of deleting it)."""
    return os.path.join(root, "src", "RimMandrake", "rimflow", "modledger_readings", "%s.json" % mod)


def load_readings(root, mod):
    d = _load(readings_path(root, mod))
    return d.get("tickets", {}) if isinstance(d, dict) else {}


RECORDS_OWNER = {}  # {mod: {ticket: his words numbered}}: what the owner reader is handed
RECORDS = {}        # {mod: {ticket: record text}}: what plan() would hand the reader (modledger_reader.record_text)
NARRATION_RE = re.compile(r"(?i)^(?:I |We |Now |Started|Began|Working on|Looking at|Continuing)")


def valid_reading(rd, root, locked):
    """A reading's words, checked: strings only, no narration or provenance lead, caps by fit, bars from the locked
    ids, depends_on paths that exist. Anything else is dropped (the deterministic field stands in)."""
    if not isinstance(rd, dict):
        return {}
    out = {}
    for k in ("defect", "proposed_fix", "accept", "changed"):
        v = rd.get(k)
        if isinstance(v, str) and v.strip() and not NARRATION_RE.match(v.strip()) and not PROVENANCE_RE.match(v):
            out[k] = " ".join(v.split())
    if rd.get("class") in ("problem", "polish"):
        out["class"] = rd["class"]
    out["bars"] = [b for b in rd.get("bars") or [] if isinstance(b, str) and b in locked]
    for k, extra in (("causes_refuted", "depends_on"), ("traps", "where")):
        lst = []
        for c in rd.get(k) or []:
            if not isinstance(c, dict) or not isinstance(c.get("text"), str) or not c["text"].strip() or \
                    NARRATION_RE.match(c["text"].strip()):
                continue
            c2 = {"text": " ".join(c["text"].split())}
            if extra == "depends_on":
                c2["depends_on"] = [x for x in c.get("depends_on") or [] if isinstance(x, str) and
                                    os.path.exists(os.path.join(root, re.sub(r"[#:].*$", "", x)))]
            elif isinstance(c.get("where"), str) and c["where"].strip():
                c2["where"] = " ".join(c["where"].split())
            lst.append(c2)
        out[k] = lst
    return out


_BASE = {}


def _base(root):
    """-> ({7-char prefix: [full sha]}, {(author date, subject): [full sha]}) of origin/main, one `git log` per root."""
    if root not in _BASE:
        r = subprocess.run(["git", "-C", root, "log", "origin/main", "--format=%H%x09%aI%x09%s"], capture_output=True,
                           text=True, timeout=120)
        idx, twin = {}, {}
        for line in r.stdout.split("\n"):
            parts = line.split("\t", 2)
            if len(parts) == 3:
                idx.setdefault(parts[0][:7], []).append(parts[0])
                twin.setdefault((parts[1], parts[2]), []).append(parts[0])
        _BASE[root] = (idx, twin)
    return _BASE[root]


def landed_sha(root, sha):
    """-> the 12-char origin/main sha for `sha` (the standard's lint rule for every code_sha): itself when it is on
    origin/main; else its landed twin, the one origin/main commit with the same author date and subject (`./publish`
    rebases, so a close often records the pre-landing sha); else None. One `git log` per root, then lookups."""
    if not re.match(r"^[0-9a-f]{7,40}$", sha or ""):
        return None
    if not os.path.exists(os.path.join(root, ".git")):
        return sha                  # not a git checkout (a fixture): taken as written
    idx, twin = _base(root)
    hit = [f for f in idx.get(sha[:7], ()) if f.startswith(sha)]
    if len(hit) == 1:
        return hit[0][:12]
    r = subprocess.run(["git", "-C", root, "log", "--no-walk", "--format=%aI%x09%s", sha, "--"], capture_output=True,
                       text=True, timeout=30)
    parts = r.stdout.strip().split("\t", 1) if r.returncode == 0 else []
    t = twin.get(tuple(parts)) if len(parts) == 2 else None
    return t[0][:12] if t and len(t) == 1 else None


def ref_path(state, tev, name):
    """The shard path of the event a final state came from (the pattern carries its line)."""
    line = int(state[3].rsplit(":", 1)[1])
    return next(t[0] for t in tev.get(name, []) if t[1] == line)


def plan(root, mod):
    """-> ([(kind, subject, body, evidence, authority, code_sha)], notes). A pure read of the old stores, mined under
    the entry standard (design/specs/2026-11-15-mod-ledger-entry-standard.md): facts, not history; one fact per entry;
    every text fitted to its cap with the old file cited for the whole; subjects from the classes; lifecycle never.
    Left out on purpose, and counted in the notes: the derived per-bar test summaries (no command, no sha), a
    checkpoint whose `next` the stores never recorded, fault status notes, live rows that decide no locked bar, his
    words already quoted under another source, and an item that only repeats a blind fault of the same name."""
    cdir = os.path.join(root, "design", "concepts", mod)
    vdir = os.path.join(cdir, "version")
    S = M.config()["standard"]["caps"]
    ev, notes, said_seen = [], [], []
    raw_readings = load_readings(root, mod)
    RECORDS[mod] = {}
    titles = item_titles(root)

    def add(kind, subject, body, evidence, authority=None, code_sha=None):
        ev.append((kind, subject, body, [e for e in evidence if e][:6], authority, code_sha))

    def his(said):
        n = " ".join(re.findall(r"[a-z0-9]+", said.lower()))
        if any(n in o or o in n for o in said_seen):
            return False
        said_seen.append(n)
        return True

    def P(path, row=None):
        rel = _rel(root, path)
        return "path:%s%s" % (rel, ("#%s" % row) if row is not None else "")

    vj = _load(os.path.join(vdir, "VERSION.json"))
    vjp = os.path.join(vdir, "VERSION.json")
    if vj:
        add("version.open", "version", {"version": vj.get("version"), "text": fit(
            "Design Version %s, %s on %s by %s; %s of %s bars met at the lock" % (
                vj.get("version"), vj.get("state"), vj.get("locked_on"), vj.get("locked_by"), vj.get("bars_met"),
                vj.get("bars_total")), S["text"])}, [P(vjp)])
        if vj.get("owner_words"):
            said = fit(_said(vj["owner_words"]), S["said"])
            his(said)
            add("decision", "version", {"said": said}, [P(vjp)], {"owner_said": said})
        if vj.get("tokens_spent"):
            add("spend", "spend", {"tokens": vj["tokens_spent"], "run": "designer and judging, to the lock"}, [P(vjp)])
    else:
        notes.append("version/VERSION.json absent")
    srp = os.path.join(vdir, "stage_record.json")
    sr = _load(srp)
    if sr:
        for i, mv in enumerate(sr.get("moves") or []):
            add("stage.accepted", "stage", {"from": mv.get("from"), "to": mv.get("to"), "by": mv.get("by"),
                                            "text": fit("%s -> %s: %s" % (mv.get("from"), mv.get("to"),
                                                                          mv.get("why") or ""), S["text"]),
                                            "as_of": mv.get("at")}, [P(srp, "moves[%d]" % i)])
        add("stage.enter", "stage", {"stage": sr.get("stage"), "text": fit("%s since %s (%s)" % (
            sr.get("stage_label"), sr.get("since"), sr.get("since_from")), S["text"]), "as_of": sr.get("since")},
            [P(srp)])
        notes.append("left out: the checkpoint (the stores never recorded a next step)")
    else:
        notes.append("version/stage_record.json absent")
    ttp = os.path.join(vdir, "test_table.json")
    tt = _load(ttp) or {}
    lbp = os.path.join(vdir, "locked_bars.json")
    lb = _load(lbp) or {}
    bars = {b["id"]: b for b in tt.get("bars") or [] if isinstance(b, dict) and b.get("id")}
    locked = list(lb.get("ids") or sorted(bars))
    readings = {k: valid_reading(v.get("reading"), root, locked) for k, v in raw_readings.items()}
    decider = {}
    for bid in locked:
        b = bars.get(bid, {})
        for d in b.get("decides") or []:
            decider.setdefault(d, bid)
        add("bar.locked", "bar:" + bid, {"text": fit("%s bar from %s, proves at stage %s" % (
            b.get("kind"), b.get("source"), b.get("proves_at")), S["text"]),
            "decides": fit("; ".join(b.get("decides") or []), S["decides"])}, [P(lbp), P(ttp, "bars.%s" % bid)])
    if not lb:
        notes.append("version/locked_bars.json absent")
    if bars:
        notes.append("left out: %d derived per-bar test summaries (no command, no sha; test_table.json is the artifact)"
                     % len(locked))
    # live results: the last row per scene per visit, on the first locked bar the scene decides
    no_bar = no_sha = 0
    for vp in sorted(glob.glob(os.path.join(vdir, "in_game", "visit_*", "rows.jsonl"))):
        visit = os.path.basename(os.path.dirname(vp))
        last = {}
        for i, row in enumerate(_jsonl(vp), 1):
            if row.get("test"):
                last[row["test"]] = (i, row)
        for test, (i, row) in sorted(last.items()):
            bid = decider.get(test)
            if not bid:
                no_bar += 1
                continue
            res = row.get("verdict") if row.get("verdict") in ("PASS", "FAIL", "UNMEASURED", "UNRUN") else "UNMEASURED"
            sha = (row.get("mod_sha") or "")[:12] or None
            if not sha and res != "UNRUN":
                no_sha += 1
                continue
            add("live.run", "bar:" + bid, {"result": res, "bar": bid,
                                           "command": fit("%s · scene %s" % (row.get("command") or "?", test),
                                                          S["command"]),
                                           "text": fit("%s %s %s (runner %s)" % (visit, test, row.get("verdict"),
                                                                                row.get("runner_verdict")), S["text"])},
                [P(vp, i)], None, sha)
    if no_sha:
        notes.append("left out: %d live rows that record no mod sha (a result without the code it ran on)" % no_sha)
    if no_bar:
        notes.append("left out: %d live rows whose scene decides no locked bar (the visit rows keep them)" % no_bar)
    # blind challenge faults: the finder's smallest_fix IS the proposed fix; its criterion is the acceptance
    fault_ids, noted, fault_raw = set(), 0, {}
    for fp in sorted(glob.glob(os.path.join(vdir, "blind_challenge", "cycle_*", "lane2", "faults.json"))):
        d = _load(fp)
        faults = d if isinstance(d, list) else (d or {}).get("faults") or []
        fxp = os.path.join(os.path.dirname(fp), "fixes.jsonl")
        fixes = {x.get("fault"): x for x in _jsonl(fxp)}
        for i, f in enumerate(faults):
            if not isinstance(f, dict) or not f.get("id"):
                continue
            src = [P(fp, i), "item:%s" % f["id"]]
            fault_raw[f["id"]] = (f, fixes.get(f["id"]), _rel(root, fp))
            fix = f.get("smallest_fix") or "not written by its finder; read the fault record"
            if not isinstance(fix, str):
                fix = json.dumps(fix, ensure_ascii=False)
            if len(fix.strip()) < M.config()["proposed_fix_min_chars"]:
                fix = "%s (the finder's smallest_fix as written, a pointer rather than a fix; read the fault record)" % fix
            evl = f.get("evidence") if isinstance(f.get("evidence"), list) else [f.get("evidence") or ""]
            evl = [str(x) for x in evl if x]
            cause = next((CAUSE_LINE_RE.search(x).group(1) for x in evl if CAUSE_LINE_RE.match(x.strip())), None)
            # the defect line: the fault's own 'cause:' evidence, else its filer's title, else its first evidence
            seen = cause or titles.get(f["id"]) or (evl[0] if evl else None)
            rd = readings.get(f["id"]) or {}
            fbars = [b for b in rd.get("bars") or [] if b in locked] or split_bars(f.get("bar"), locked)
            add("finding.open", "finding:" + f["id"], {
                "class": "polish" if str(f.get("class") or f.get("cls")).lower() == "polish" else "problem",
                "bars": fbars, "tags": [] if fbars else (["instrument"] if "instrument" in str(f.get("bar")) else
                                                         _tags(json.dumps(f))),
                "text": fit(rd.get("defect") or seen or f.get("criterion") or f["id"], S["text"]),
                "proposed_fix": fit(rd.get("proposed_fix") or fix, S["proposed_fix"]),
                "accept": fit(rd.get("accept") or f.get("would_pass") or f.get("criterion") or
                              "none, the fault record names no criterion", S["accept"])}, src)
            fault_ids.add(f["id"])
            st = f.get("status") or ""
            if st.startswith("FIXED"):
                sha = (st.split() + [None])[1]
                x = fixes.get(f["id"]) or {}
                red, green = _last(x.get("red")), _last(x.get("green"))
                test = "red rc %s, green rc %s: %s" % (red.get("rc"), green.get("rc"), red.get("command") or
                                                       red.get("cmd") or green.get("command") or "see fixes.jsonl")
                did = rd.get("changed") or "; ".join(x for x in (
                    f.get("fix_as_shipped") or f.get("smallest_fix") if isinstance(
                        f.get("fix_as_shipped") or f.get("smallest_fix"), str) else None,
                    ("cause: " + cause) if cause else None) if x) or "the fault's smallest_fix, shipped at %s" % sha
                add("finding.claimed_fixed", "finding:" + f["id"], {
                    "text": fit(did, S["text"]),
                    "test": fit(test, S["test"])}, [P(fxp) if os.path.exists(fxp) else P(fp, i), "item:%s" % f["id"],
                                                    "sha:%s" % sha if sha else None], None, sha)
            elif st.startswith("NOTED"):
                noted += 1
    if noted:
        notes.append("left out: %d fault status notes (NOTED_*: the finding.open carries the fact)" % noted)
    # criterion repairs: a decision on the bar whose scene was repaired
    for cp in sorted(glob.glob(os.path.join(vdir, "criterion_repairs", "*"))):
        if not os.path.isdir(cp):
            continue
        txt = ""
        for name in ("RECERTIFY.md", "FINDINGS.md"):
            q = os.path.join(cp, name)
            if os.path.exists(q):
                with open(q, encoding="utf-8") as fh:
                    paras = [x.strip() for x in fh.read().split("\n\n") if x.strip() and not x.startswith("#")]
                txt = paras[0] if paras else ""
                break
        scene = re.sub(r"_\d{4}-\d\d-\d\d$", "", os.path.basename(cp))
        bid = decider.get(scene) or next((b for b in locked if b == scene), None)
        add("decision", "bar:" + bid if bid else "q:criterion-repair-" + slug(scene, 8),
            {"text": fit(txt or "criterion repair of %s (files: %s)" % (scene, ", ".join(sorted(os.listdir(cp)))),
                         S["text"])}, [P(cp)], {"why": "backfill: a criterion repair recorded in its folder"})
    # spend
    sp = os.path.join(vdir, "run_spend.jsonl")
    for i, row in enumerate(_jsonl(sp), 1):
        usd = row.get("usd") if isinstance(row.get("usd"), (int, float)) else None
        add("spend", "spend", {"usd": usd, "tokens": row.get("tokens"), "stage": row.get("stage"),
                               "run": str(row.get("unit") or i)}, [P(sp, i)])
    # his words, as the journal lists them
    jp = os.path.join(cdir, "journal.md")
    if os.path.exists(jp):
        with open(jp, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        start = next((i for i, l in enumerate(lines) if l.startswith("### His words")), None)
        bullets, cur, at = [], [], None
        if start is not None:
            for i in range(start + 1, len(lines)):
                l = lines[i]
                if l.startswith("#"):
                    break
                if l.startswith("- "):
                    if cur:
                        bullets.append((at, " ".join(cur)))
                    cur, at = [l[2:].strip()], i + 1
                elif cur and l.strip():
                    cur.append(l.strip())
            if cur:
                bullets.append((at, " ".join(cur)))
            for at, b in bullets:
                said = fit(_said(b), S["said"])
                if his(said):
                    add("decision", "q:" + slug(said), {"said": said}, ["path:%s:%d" % (_rel(root, jp), at)],
                        {"owner_said": said})
        else:
            notes.append("journal.md has no 'His words' section")
        ostart = next((i for i, l in enumerate(lines) if l.startswith("### Oddities")), None)
        odd, cur = [], None
        for i in range(ostart + 1, len(lines)) if ostart is not None else []:
            l = lines[i]
            if l.startswith("#"):
                break
            mo = re.match(r"^\d+\.\s+(.*)", l)
            if mo:
                cur = [i + 1, mo.group(1).strip()]
                odd.append(cur)
            elif cur and l.strip():
                cur[1] += " " + l.strip()
        for at, b in odd:
            head = re.match(r"\*\*(.+?)\*\*", b)
            where = re.search(r"`([^`]{2,160})`", b)
            add("trap.noted", "trap:" + slug(head.group(1) if head else b, 8),
                {"text": fit(b.replace("**", ""), S["text"]), "where": where.group(1) if where else
                 "%s:%d" % (_rel(root, jp), at), "tags": ["instrument"]}, ["path:%s:%d" % (_rel(root, jp), at)])
    # live items naming the mod: each mines to at most one finding.open (standard rule 10)
    spaced, word = _words(mod)
    words = M.config().get("backfill_item_words", {}).get(mod, [])
    items, dup_fault, elsewhere = [], 0, 0
    others = other_mod_words(root, mod) - set(words) - {word, mod.upper()}
    idir = os.path.join(root, "infrastructure", "state", "items")
    cands = [(p, False) for p in sorted(glob.glob(os.path.join(idir, "*.md")))] + \
        [(p, True) for p in sorted(glob.glob(os.path.join(idir, "closed", "*.md")))]
    cfg = M.config()
    lead = re.compile(r"^(?:polish\W*)?(?:%s)\b" % "|".join(
        re.escape(n) for n in [mod, spaced] + cfg.get("backfill_title_names", {}).get(mod, [])), re.I)
    include = set(cfg.get("backfill_item_include", {}).get(mod, []))
    exclude = set(cfg.get("backfill_item_exclude", {}).get(mod, []))

    def id_or_title_names(name):
        """A closed or prose-less ticket is the mod's only when its id or its filer's title leads with the mod (a
        closed pipeline ticket that cites the mod in passing is the pipeline's)."""
        return name in include or mod.upper() in name or bool(set(name.split("_")) & set(words)) or bool(
            lead.search(titles.get(name) or ""))

    # most tickets have no prose file: their rimflow events (title, notes, close) are the whole record
    have = {os.path.basename(p)[:-3] for p, _ in cands}
    cands += [(None, n) for n in sorted(titles) if n not in have and id_or_title_names(n)]
    tev = ticket_events(root, have | {n for p, n in cands if p is None} | fault_ids)
    states = rimflow_states(root, sorted(tev), tev)
    bulk = bulk_shas(root)
    sha_ok = {}

    def landed(sha):
        """A sha cited must resolve on origin/main: -> it, or its landed twin (./publish rewrites a pre-landing sha),
        or None (landed_sha)."""
        if sha not in sha_ok:
            sha_ok[sha] = landed_sha(root, sha)
        return sha_ok[sha]

    rebased = 0
    claimed = {s for k, s, *_ in ev if k == "finding.claimed_fixed"}
    closed_unstated, sha_dead, refuted_no_sha, causes_seen = [], 0, 0, set()
    for ip, is_closed in cands:
        if ip is None:
            name, prose, ip = is_closed, titles[is_closed], None
            is_closed = _closed_in_ledger(tev.get(name, []))
        else:
            name = os.path.basename(ip)[:-3]
            with open(ip, encoding="utf-8") as fh:
                prose = fh.read()
        if name in exclude or TOOLING_RE.search(titles.get(name) or ""):
            continue                       # the mod ledger's own machinery stays a rimflow ticket (fusion spec 3.2)
        if (is_closed or ip is None) and not id_or_title_names(name):
            continue
        head = "\n".join(prose.split("\n")[:6])
        named = mod.upper() in name or mod in head or spaced in head or id_or_title_names(name)
        # a short word (KNOCKBACK, SLACK) alone is too wide (SLACK also names SlackMaster work): it counts only when the
        # mod's configured item words list it, or the mod is named somewhere in the prose
        if not named and not (set(name.split("_")) & set(words) or
                              (word in name.split("_") and (mod in prose or spaced in prose))):
            continue
        if set(name.split("_")) & set(M.config().get("backfill_item_skip_words", [])):
            continue
        if set(name.split("_")) & others and not (mod.upper() in name or set(name.split("_")) & (set(words) | {word})):
            elsewhere += 1
            continue
        rd = readings.get(name) or {}
        fr = fault_raw.get(name) or (None, None, None)
        RECORDS[mod][name] = R.record_text(name, titles.get(name), states.get(name), prose if ip else None,
                                           tev.get(name, []), fr[0], fr[1], _rel(root, ip) if ip else fr[2])
        state = _final_state(name, tev.get(name, []), S, states.get(name), landed, bulk, rd)
        if state and state[2]:
            tw = landed(state[2])
            if not tw:
                sha_dead += 1
                state = None
            elif not (tw.startswith(state[2][:12]) or state[2].startswith(tw)):
                rebased += 1
                kind_, body_, said_, ref_ = state
                t_ = body_["text"]
                t_ = (t_.replace(said_, "%s (pre-landing; landed as %s)" % (said_, tw), 1) if said_ in t_ else
                      "%s (recorded on pre-landing %s; landed as %s)" % (t_, said_[:12], tw))
                state = (kind_, dict(body_, text=fit(t_, S["text"])), tw, ref_)
        if is_closed and not state:
            closed_unstated.append(name)
            continue
        items.append(name)
        fe = next((t for t in tev.get(name, []) if t[2].get("event") == "file"), None)
        src = [P(ip) if ip else "path:%s:%d" % (_rel(root, fe[0]), fe[1]), "item:" + name]
        etexts = [str(t[2].get(k) or "") for t in tev.get(name, []) for k in ("text", "why", "reason", "title")
                  if t[2].get("event") in ("file", "note", "close", "implemented")]
        if name in fault_ids:
            dup_fault += 1
        else:
            _mine_finding(add, name, prose, titles, locked, S, src, etexts, rd)
        if state and "finding:" + name not in claimed:
            kind, body, sha, ref = state
            add(kind, "finding:" + name, body, src + ["sha:" + sha, ref % _rel(root, ref_path(state, tev, name))],
                None, sha)
        # ruled-out causes and traps, under any wording, from the ticket's prose and its notes (the judges' rule 2): a
        # cause pinned to a sha that lands is cause.refuted; one with no sha, and every 'reader would get it wrong'
        # line, is trap.noted. A per-ticket reading's causes and traps come first; the sentences add what it lacks.
        texts = [(None, prose)] + [(t, e.get("text") or e.get("reason") or e.get("why") or e.get("noCode") or "")
                                   for t in tev.get(name, []) for e in [t[2]] if e.get("event") in
                                   ("note", "close", "drop", "implemented", "verify") and
                                   str(e.get("sha") or "")[:12] not in bulk]
        found = [("cause", c.get("text"), c.get("depends_on") or [], None) for c in rd.get("causes_refuted") or []
                 if isinstance(c, dict) and c.get("text")] + \
                [("trap", c.get("text"), [], c.get("where")) for c in rd.get("traps") or []
                 if isinstance(c, dict) and c.get("text")]
        for t, txt in texts:
            for sen in _sentences(words_of(txt)):
                is_cause = (CAUSE_RE.search(sen) or REFUTED_RE.search(sen)) and not NOT_REFUTED_RE.search(sen)
                if not (is_cause or TRAP_RE.search(sen)):
                    continue
                if rd and not (REFUTED_RE.search(sen) and is_cause):
                    continue              # the reading read these lines with judgement; only an explicit 'X refuted'
                    #                       or 'False theory:' sentence is added beside its list
                found.append(("cause" if is_cause else "trap", sen, PATH_RE.findall(sen), None, t, txt))
        for f_ in found:
            kind_, sen, deps, where = f_[:4]
            t, txt = (f_[4], f_[5]) if len(f_) > 4 else (None, sen)
            key = " ".join(re.findall(r"[a-z0-9]+", str(sen).lower()))
            if key in causes_seen:
                continue
            causes_seen.add(key)
            lref = ["ledger:%s:%d" % (_rel(root, t[0]), t[1])] if t else []
            shas = [landed(x) for x in SHA_RE.findall(txt) if landed(x)] or ([state[2]] if state else [])
            subj = slug(re.sub(r"(?i)^.*?(?:false theor(?:y|ies)|correction|ruled out[^:]*):\s*", "", sen), 8)
            if kind_ == "cause" and shas:
                paths = deps or PATH_RE.findall(txt) or [
                    _rel(root, d) for d in [os.path.join(root, "src", "RimMandrake", mod)] if os.path.isdir(d)] or [
                    re.sub(r":\d+$", "", src[0][5:])]
                add("cause.refuted", "cause:" + subj,
                    {"text": fit(sen, S["text"]), "finding": "finding:" + name, "depends_on": paths[:4]},
                    src + lref, None, shas[0])
            else:
                refuted_no_sha += kind_ == "cause"
                add("trap.noted", "trap:" + subj, {"text": fit(sen, S["text"]), "where": fit(
                    where or where_of(sen, "item:" + name), S["where"]), "tags": ["instrument"] if re.search(
                        r"(?i)\b(test|proof|gate|check|scan|wrapper|census|verify|green|harness|instrument)\b", sen)
                        else ["code"]}, src + lref)
    for fid, (f, fx, fpr) in fault_raw.items():
        if fid not in RECORDS[mod]:
            RECORDS[mod][fid] = R.record_text(fid, titles.get(fid), None, None, tev.get(fid, []), f, fx, fpr)
    if dup_fault:
        notes.append("left out: %d items that only repeat the blind fault of the same name" % dup_fault)
    if closed_unstated:
        notes.append("left out: %d closed tickets whose closing the ledger does not state with a sha on origin/main "
                     "(a drop, a supersede, or no close event; no sha to withdraw on), so none is left looking open"
                     % len(closed_unstated))
    if rebased:
        notes.append("%d ticket final states recorded a pre-landing sha: each is claimed on its landed twin (the one "
                     "origin/main commit with its author date and subject), both named" % rebased)
    if sha_dead:
        notes.append("left out: %d ticket final states whose sha does not resolve on origin/main" % sha_dead)
    nofile = [n for n in items if not os.path.exists(os.path.join(idir, n + ".md")) and
              not os.path.exists(os.path.join(idir, "closed", n + ".md"))]
    notes.append("tickets mined: %d, %d of them with no item file (their rimflow events are the whole record)"
                 % (len(items), len(nofile)))
    if refuted_no_sha:
        notes.append("%d ruled-out causes with no sha to pin them to are mined as traps" % refuted_no_sha)
    if elsewhere:
        notes.append("left out: %d items named for another mod that cite this one" % elsewhere)
    # his words and cards in the OWNER ledger shards, on the finding they bear on when it is one of ours
    mined = {s for k, s, *_ in ev if k == "finding.open"}
    mined_items = set(items)
    fleet = fleet_words(root)
    lifecycle_words = off_mod = not_ruling = 0
    squash = lambda t: re.sub(r"[^a-z0-9]", "", str(t).lower())
    name_re = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(w) for w in set(
        words + cfg.get("backfill_title_names", {}).get(mod, []) + [word])), re.I)
    cand = []
    for sp_ in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER*.jsonl"))):
        for i, e in enumerate(_jsonl(sp_), 1):
            blob = json.dumps(e, ensure_ascii=False)
            if mod not in blob and spaced not in blob and e.get("id") not in mined_items:
                continue
            said, card = e.get("ownerSaid"), e.get("byCard")
            if not (said or card):
                continue
            # rule 3: words riding a lifecycle event (needs, reassign, raise, block, a FROZEN STOP note) or the same
            # words on many tickets (a fleet-wide order) authorise an act; they say nothing about the mod
            if (e.get("event") not in OWNER_WORD_EVENTS or str(said or card) in fleet or
                    re.match(r"\s*(?:FROZEN|STOP\b|PARK|UNPARK|PAUSE)", str(e.get("text") or ""))):
                lifecycle_words += 1
                continue
            card = card if isinstance(card, str) or card is None else json.dumps(card, ensure_ascii=False)
            iid = e.get("id") if isinstance(e.get("id"), str) else None
            # on a ticket that is not one of this mod's, his words count only when they name the mod themselves
            if iid not in mined_items and not (squash(mod) in squash(said or card) or name_re.search(said or card)):
                off_mod += 1
                continue
            cand.append((sp_, i, said, card, iid))
    by_ticket = {}
    for c_ in cand:
        if c_[4] in mined_items:
            by_ticket.setdefault(c_[4], []).append(c_[2] or c_[3])
    RECORDS_OWNER[mod] = {t: R.owner_text(t, titles.get(t), mod, ws) for t, ws in by_ticket.items()}
    for sp_, i, said, card, iid in cand:
        # on a ticket the owner reader read, only the words it marked as a ruling about the mod
        orr = raw_readings.get(iid) or {}
        if iid in by_ticket and isinstance(orr.get("owner"), list):
            n_ = by_ticket[iid].index(said or card) + 1
            if n_ not in orr["owner"]:
                not_ruling += 1
                continue
        words_ = fit(said, S["said"]) if said else fit(card, S["text"])
        if not his(words_):
            continue
        subj = ("finding:" + iid) if iid and "finding:" + iid in mined else "q:" + slug(iid or words_, 12)
        auth = {"owner_said": words_} if said else {"by_card": words_}
        add("decision", subj, {"said": words_} if said else {"text": words_},
            ["path:%s:%d" % (_rel(root, sp_), i), ("item:" + iid) if iid else None], auth)
    if off_mod or not_ruling:
        notes.append("left out: %d owner words on other tickets that do not name the mod, %d the owner reader found "
                     "no ruling about it" % (off_mod, not_ruling))
    if lifecycle_words:
        notes.append("left out: %d owner words riding lifecycle or fleet-wide events (authority for an act, not a "
                     "statement about the mod)" % lifecycle_words)
    return ev, notes


def _fit_line(body, auth, measured):
    """A line over the byte cap, refused: shorten its longest text (his `said` and its authority copy together) by the
    overflow, the leading sentences kept and the cut marked; the event cites the old file holding the whole (rule 8).
    -> True when something was shortened."""
    m = re.match(r"(\d+) bytes > (\d+)", measured or "")
    if not m:
        return False
    over = int(m.group(1)) - int(m.group(2))
    field = max((f for f in ("said", "text") if isinstance(body.get(f), str)), key=lambda f: len(body[f]), default=None)
    if not field:
        return False
    old = body[field]
    copies = [k for k, v in (auth or {}).items() if v == old]
    cut = over // (1 + len(copies)) + 16
    if len(old) - cut < 40:
        return False
    body[field] = fit(old, len(old) - cut)
    for k in copies:
        auth[k] = body[field]
    return True


def run(root, mod, dry=False, read=False, budget_usd=None, log=print):
    """Write the plan through `modledger.append` (the standard's refusals included). An event the standard still
    refuses is left out and counted, never forced. A BACKFILL line already in the shard that the plan no longer holds
    is deleted after the appends (delete on sight: it failed the standard, or the old stores no longer say it); a line
    the plan still holds is kept as it is (same key, same id). A line over the byte cap has its longest text fitted
    (`_fit_line`) and is held under the fitted key."""
    ev, notes = plan(root, mod)
    reader = None
    if read:
        cfg = M.config().get("backfill_reader", {})
        bud = budget_usd if budget_usd is not None else cfg.get("budget_usd", 5)
        locked = sorted(s[4:] for k, s, *_ in ev if k == "bar.locked")
        reader = R.read_tickets(readings_path(root, mod), RECORDS.get(mod, {}), locked, bud,
                                cfg.get("model", "sonnet"), cfg.get("workers", 4), log)
        notes.append("reader: %d of %d tickets read in %d batches, $%.2f spent (bound $%.2f), %d failed, %d skipped "
                     "for the bound" % (reader["read"], reader["asked"], reader["batches"], reader["spent_usd"], bud,
                                        len(reader["failed"]), reader["skipped_for_budget"]))
        ev, notes2 = plan(root, mod)
        owr = R.read_tickets(readings_path(root, mod), RECORDS_OWNER.get(mod, {}), [], max(0.0, bud - reader[
            "spent_usd"]), cfg.get("model", "sonnet"), cfg.get("workers", 4), log, field="owner",
            system=R.OWNER_SYSTEM)
        ev, notes2 = plan(root, mod)
        notes = notes2 + notes[-1:] + ["owner reader: %d of %d tickets read in %d batches, $%.2f spent, %d failed, "
                                       "%d skipped for the bound" % (owr["read"], owr["asked"], owr["batches"],
                                                                     owr["spent_usd"], len(owr["failed"]),
                                                                     owr["skipped_for_budget"])]
    have_r = load_readings(root, mod)
    stale = sum(1 for n, t in RECORDS.get(mod, {}).items() if (have_r.get(n) or {}).get("hash") not in (None, R.rec_hash(t)))
    unread = sum(1 for n in RECORDS.get(mod, {}) if n not in have_r)
    notes.append("readings: %d tickets unread (mined by the sentence rules), %d read from an older record (re-read "
                 "with --read)" % (unread, stale))
    if dry:
        return {"planned": len(ev), "written": 0, "already": 0, "deleted": 0, "refused": [], "near_duplicates": [],
                "notes": notes}
    version = next((b.get("version") for k, s, b, *_ in ev if k == "version.open"), None)
    written = already = 0
    refused, near, held, seq = [], [], set(), {}
    for idx, (kind, subject, body, evidence, auth, sha) in enumerate(ev):
        apart = fit("a separate source record (%s); listed in the backfill report" % (
            evidence[0] if evidence else "?"), 160)
        try:
            for _try in range(3):
                try:
                    eid, created = M.append(root, mod, W, kind, subject, body=body, version=version, evidence=evidence,
                                          authority=auth, code_sha=sha, views=False)
                    break
                except M.Refusal as r:
                    if r.field != "line" or _try == 2 or not _fit_line(body, auth, r.measured):
                        raise
        except M.Refusal as r:
            # a near-duplicate subject is kept with --new-subject; on a re-run the plain append restates that kept line,
            # so the same --new-subject append finds it by key and holds it (else the run deletes it, the next rewrites)
            again = r.field == "text" and "restates" in r.measured
            if (r.field == "subject" and "looks like" in r.measured) or again:
                if not again:
                    near.append((subject, r.measured))
                try:
                    eid, created = M.append(root, mod, W, kind, subject, body=body, version=version, evidence=evidence,
                                          authority=auth, code_sha=sha, views=False, new_subject=apart)
                except M.Refusal as r2:
                    same = re.search(r"restates (BACKFILL:[0-9a-f]+)", str(r2))
                    if same:                # an older mine holds the same fact under other evidence: keep that line
                        held.add(same.group(1))
                        already += 1
                        continue
                    refused.append((kind, subject, str(r2)))
                    continue
            else:
                refused.append((kind, subject, str(r)))
                continue
        held.add(eid)
        seq.setdefault(subject, []).append((idx, eid, created, body, auth))
        written += created
        already += not created
    # a subject's events must stay in plan order (the reducer reads the last): a line kept from an earlier run that the
    # plan puts AFTER a line written now (a re-read finding text before its kept claim) is re-appended after it
    redo = []
    for subject, xs in seq.items():
        first = next((i for i, x in enumerate(xs) if x[2]), None)
        if first is not None:
            redo += [x for x in xs[first + 1:] if not x[2]]
    if redo:
        M.delete(root, mod, [x[1] for x in redo])
        for idx, eid, _c, body, auth in sorted(redo, key=lambda x: x[0]):
            kind, subject, _b, evidence, _a, sha = ev[idx]
            apart = fit("a separate source record (%s); listed in the backfill report" % (
                evidence[0] if evidence else "?"), 160)
            # a fresh key: the same id re-appended reads as a line changed in place (lint EDITED_IN_PLACE); a later
            # run's plain append of this fact is refused as 'restates' and holds this line
            rkey = hashlib.sha256(("%s\0reordered after\0%s" % (eid, seq[subject][0][1])).encode()).hexdigest()[:16]
            for ns in (None, apart):
                try:
                    M.append(root, mod, W, kind, subject, body=body, version=version, evidence=evidence,
                             authority=auth, code_sha=sha, views=False, new_subject=ns, key=rkey)
                    held.add(M.derive_id(W, rkey))
                    break
                except M.Refusal as r:
                    if ns or not (r.field in ("subject", "text")):
                        refused.append((kind, subject, str(r)))
                        held.discard(eid)
                        break
            written += 1
            already -= 1
    # after the appends (a line fitted to the byte cap is held under its fitted key): a BACKFILL line the plan no
    # longer holds is deleted
    old = [e for e in M.read(root, mod) if e.get("_shard") == W and e.get("id") not in held]
    if old:
        M.delete(root, mod, [e["id"] for e in old])
        # a subject whose old first line just left was written without the mint check (the subject existed then):
        # its lines are re-appended in order, the first kept apart by --new-subject, each under a fresh key
        bad = {d.split(" looks like ")[0].split("REFUSED subject: ", 1)[1] for c, pth, ln, d in M.lint(root, mod, None)[0]
               if c == "STANDARD" and pth.endswith("/BACKFILL.jsonl") and "REFUSED subject: " in d and " looks like " in d}
        for subject in sorted(bad):
            lines = [e for e in M.read(root, mod) if e.get("_shard") == W and e["subject"] == subject]
            M.delete(root, mod, [e["id"] for e in lines])
            for i, e in enumerate(lines):
                rkey = hashlib.sha256(("%s\0minted apart" % e["id"]).encode()).hexdigest()[:16]
                body = {k: v for k, v in e["body"].items() if k not in ("by", "ts", "new_subject_why")}
                apart = fit("a separate source record (%s); listed in the backfill report" % (
                    e["evidence"][0] if e.get("evidence") else "?"), 160)
                try:
                    M.append(root, mod, W, e["kind"], subject, body=body, version=e.get("version"),
                             evidence=e.get("evidence") or [], authority=e.get("authority"), code_sha=e.get("code_sha"),
                             views=False, new_subject=apart if i == 0 else None, key=rkey)
                except M.Refusal as r:
                    refused.append((e["kind"], subject, str(r)))
            near.append((subject, "re-minted apart after its old first line was deleted"))
    M.write_views(root, mod)
    return {"planned": len(ev), "written": written, "already": already, "deleted": len(old), "refused": refused,
            "near_duplicates": near, "notes": notes}


def compare(root, mod):
    """-> [(what, old store says, ledger says, agree?)]: the shadow check the cutover waits on."""
    cdir = os.path.join(root, "design", "concepts", mod)
    st = M.reduce(M.read(root, mod))
    out = []
    sr = _load(os.path.join(cdir, "version", "stage_record.json")) or {}
    out.append(("stage (version/stage_record.json)", sr.get("stage"), st["stage"], sr.get("stage") == st["stage"]))
    sj = _load(os.path.join(cdir, "stage.json")) or {}
    out.append(("stage.json key 'stage' (the Designer's inner step, a homonym)", sj.get("stage"), st["stage"],
                sj.get("stage") == st["stage"]))
    out.append(("stage.json blocked_on", sj.get("blocked_on") or "none", "version %s, stage %s"
                % (st["version"], st["stage"]), not sj.get("blocked_on")))
    jp = os.path.join(cdir, "journal.md")
    jt = open(jp, encoding="utf-8").read() if os.path.exists(jp) else ""
    m = re.search(r"\*\*Stage now:\*\* (.*)", jt)
    out.append(("journal.md 'Stage now'", m.group(1).strip() if m else None, st["stage"],
                bool(m) and (st["stage"] or "").replace("_", " ") in m.group(1).lower().replace("-", " ")))
    unrun = "Every in-game scene is UNRUN" in jt
    lives = [t for t in st["tests"] if t["kind"] == "live.run"]
    out.append(("journal.md stands: in-game scenes", "every scene UNRUN" if unrun else "not claimed UNRUN",
                "%d live rows backfilled from the visit records" % len(lives), not (unrun and lives)))
    wait = re.search(r"\*\*Waiting on:\*\* (.*)", jt)
    out.append(("journal.md 'Waiting on'", wait.group(1).strip() if wait else None,
                "checkpoint next: %s" % ((st["checkpoint"] or {}).get("next")),
                bool(wait) and "not yet written" not in wait.group(1)))
    vj = _load(os.path.join(cdir, "version", "VERSION.json")) or {}
    out.append(("bars_total (VERSION.json)", vj.get("bars_total"), len(st["bars"]), vj.get("bars_total") ==
                len(st["bars"])))
    fixed = set()
    for fp in glob.glob(os.path.join(cdir, "version", "blind_challenge", "cycle_*", "lane2", "faults.json")):
        d = _load(fp)
        for f in d if isinstance(d, list) else (d or {}).get("faults") or []:
            if isinstance(f, dict) and str(f.get("status") or "").startswith("FIXED"):
                fixed.add("finding:%s" % f.get("id"))
    claimed = [k for k in fixed if (st["findings"].get(k) or {}).get("status") == "claimed_fixed"]
    out.append(("blind faults marked FIXED in faults.json", len(fixed), "%d claimed_fixed, no judge verdict"
                % len(claimed), not fixed))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=None)
    sub = ap.add_subparsers(dest="verb", required=True)
    r = sub.add_parser("run")
    r.add_argument("--mod", required=True)
    r.add_argument("--dry", action="store_true")
    r.add_argument("--read", action="store_true", help="read unread or changed tickets with claude -p first")
    r.add_argument("--read-budget", type=float, default=None, help="dollar bound on --read (modledger.json "
                   "backfill_reader.budget_usd)")
    c = sub.add_parser("compare")
    c.add_argument("--mod", required=True)
    o = ap.parse_args(argv)
    root = o.root or M.default_root()
    if o.verb == "run":
        res = run(root, o.mod, o.dry, o.read, o.read_budget)
        for n in res["notes"]:
            print("note: " + n)
        for kind, subject, why in res["refused"]:
            print("refused, left out: %s %s: %s" % (kind, subject, why))
        for subject, why in res["near_duplicates"]:
            print("near-duplicate, kept with --new-subject: %s" % why)
        print("backfill %s: %d planned, %d written, %d already there, %d old lines deleted, %d refused, %d "
              "near-duplicates" % (o.mod, res["planned"], res["written"], res["already"], res["deleted"],
                                   len(res["refused"]), len(res["near_duplicates"])))
    else:
        rows = compare(root, o.mod)
        for what, old, new, ok in rows:
            print("%-6s %s\n       old: %s\n       ledger: %s" % ("agree" if ok else "DIFF", what, old, new))
        print("compare %s: %d of %d agree" % (o.mod, sum(1 for r_ in rows if r_[3]), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
