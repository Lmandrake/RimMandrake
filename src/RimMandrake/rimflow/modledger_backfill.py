#!/usr/bin/env python3
"""modledger_backfill.py — import one mod's state from today's stores into its mod ledger, in SHADOW mode.

Spec design/specs/2026-11-15-holder-pipeline-fusion.md §3.8 steps 2-3; plan step 3. Every event is written by the
`BACKFILL` writer and cites the old file (and the row or line) it came from. Nothing old is redirected, archived or
deleted: the views are generated beside the old files, and `compare` prints where the old files disagree with each
other or with the ledger.

    python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod ExplosiveKnockback        # writes the ledger
    python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod ExplosiveKnockback --dry  # counts only
    python3 src/RimMandrake/rimflow/modledger_backfill.py compare --mod ExplosiveKnockback    # shadow disagreements
    python3 src/RimMandrake/rimflow/modledger_backfill.py bars --mod ExplosiveKnockback       # bars = locked_bars.json

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
import math
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
# --- the round-2 judge's rules (RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY, verdicts
# D:\ClaudeWork\rimmandrake\conductor\mining_samples\<Mod>_round2.judge.json) ---
# rule 1: a sentence carrying a status word is a status line, false the day it changes, never a trap ('wave was still
# spreading' is a past reading, not a status, and stays)
STATUS_RE = re.compile(r"(?i)(?<!was )(?<!were )\bstill\b|\bun-?run\b|\bowed\b|\bnot yet\b|\bis not closed\b|"
                       r"\bnot closed until\b|\bnever (?:been )?run\b|\bwas not run\b|\bnot done\b|\bunwritten\b|"
                       r"\bremains? (?:unverified|open|owed)\b")
UNRUN_RE = re.compile(r"(?i)\bun-?run\b")
PRONOUN_RE = re.compile(r"^(?:It|This|That|They|These|Those|Its|Both)\b")
# a doc correction already made is history (git has it), and a trap never restates his ruling without his authority
HISTORY_RE = re.compile(r"(?i)\b(?:text|line|claim|sentence|wording|doc)\b[^.;]{0,40}\b(?:was|were|is|has been)\s+"
                        r"(?:false and\s+)?(?:removed|corrected|deleted|rewritten)\b")
OWNER_RESTATE_RE = re.compile(r"(?i)(?<!not )\b(?:the |if the )?owner (?:has |had |then )?(?:chose|ruled|decided|picked|said|"
                              r"wants|asked|kept)\b|\bby card\b")
# a past reading of a result ('earlier passes were swims', 'the earlier PASS rows came from harness fixes') stays true
# after the fix, so it is never dropped as the ticket's own defect
PAST_READING_RE = re.compile(r"(?i)\b(?:earlier|previous|prior|older)\b[^.;]{0,60}\b(?:pass|passes|fail|fails|rows?|"
                             r"runs?|reads?|readings?)\b")
# rule 2: a ruled-out cause is mined only from a sentence that rules it out; 'later resolved' / 'passed later' is a
# state change, never a refutation
RULED_OUT_RE = re.compile(r"(?i)\bruled out\b|\bnot (?:the|a) (?:cause|culprit|bug|defect)\b|\b(?:was|were|is|are)"
                          r"(?:n't| not)\b|\bno (?:[\w-]+ )?(?:bug|defect|fault)\b|\brefut|\bfalse theor|\bexplained\b|"
                          r"\bturned out\b|\brather than\b|\binstead\b|\bred herring\b|\b(?:did|does|do)(?:n't| not)\b|"
                          r"\bharness\b|\bnot (?:caused|due)\b|\bcorrection\b|\bdisprov|\bexclud|\bcleared\b|"
                          r"\binnocent\b|\bnever\b|\bunrelated\b|\bnot responsible\b|\bmatched\b|\bcorrect(?:ly)?\b|"
                          r"\bfault was in\b|\b(?:checker|harness|proof|test|site|instrument)\b[^.;]{0,30}\bfault\b|"
                          r"\b(?:CHECKER|HARNESS|PROOF|SITE)\b|\bwrong\b|^\W*(?:not|no)\b|\balready\b|\btheory\b|\bhypothes[ie]s\b|"
                          r"\brejected\b|\bre-read\b|\bnot reproduced\b")
STATE_CHANGE_RE = re.compile(r"(?i)\blater (?:resolved|passed|fixed)\b|\bwas (?:later )?resolved\b|\bresolved later\b|"
                             r"\bpassed later\b|\bsince (?:passed|fixed)\b")
# a cause the ticket FOUND (the defect's mechanism) is no refuted cause
FOUND_CAUSE_RE = re.compile(r"(?i)\b(?:was|is|were|are) caused by\b|\bthe (?:root )?cause (?:is|was)\b|\bsettled as\b|"
                            r"\ba real\b[^.;]{0,40}\b(?:bug|defect)\b")
# the reader's list form: 'the hypothesis: what refuted it'
HYPOTHESIS_RE = re.compile(r"^[^:]{3,140}:\s+\S")
EXPLICIT_REFUTED_RE = re.compile(r"(?i)\bnot (?:the|a) (?:cause|culprit)\b|\bruled out\b|\brefut|\bfalse theor")
# rule 3: a done ticket whose record says nothing needed changing, closed on passing rows, is withdrawn after a test
NO_CHANGE_RE = re.compile(r"(?i)\bno code change\b|\bdid not occur\b|\bno (?:code )?fix (?:was )?needed\b|"
                          r"\bnothing to fix\b|\bno defect (?:remains|found)\b")
# rule 4: a fix text that is boilerplate (lifecycle, 'the record does not say how') is replaced by the landed commit's
# subject; a bookkeeping commit (lesson, ledger) names no fix
BOILER_RE = re.compile(r"(?i)record (?:does not|doesn't) (?:say|describe)|names no change|beyond its title|"
                       r"^relentless:|^published[;,]|^selftest green\.?$|^the fault's smallest_fix, shipped|"
                       r"^(?:fixed|built|landed|done) (?:in|at|as) [0-9a-f]{7,40}\.?$")
BOOKKEEP_RE = re.compile(r"(?i)^(?:ledger|lessons?|modledger|handoff|notes?|chore|journal)\b[:(]")
# work orders: a pipeline ticket that takes the mod through a stage or a blind cycle names nothing wrong with the mod
# the round-4 judge (mining_samples/<Mod>_round4.judge.json): a trap stating that a named thing is missing (EK 65),
# a trap about pipeline code (FW 661: maturation.py), a note on how a fix's red was re-shown (EK 139), a sentence a
# walk by the owner verified (GSS 341), the paths that say which mod a ticket's code and art are (GSS 0)
ABSENT_RE = re.compile(r"(?i)\b(?:has no|have no|had no|lacks?|is missing|are missing|there is no|there are no)\s+"
                       r"(?:an? |the |any )?`?([A-Za-z][\w.]*[A-Za-z0-9])")
IDENT_RE = re.compile(r"`([^`\s]{3,80})`|\b([\w-]+\.(?:cs|py|json|xml|md))\b|"
                      r"\b([A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]*[A-Za-z0-9])\b|\b([A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+)\b")
CODE_EXT = (".cs", ".py", ".json", ".xml")
TODAY_EXT = CODE_EXT + (".md", ".txt")
REDEMO_RE = re.compile(r"(?i)\bre-?demonstrat\w*|\boriginal red command\b")
OWNER_WALK_RE = re.compile(r"(?i)\bwalked\b.{0,160}\bverified\b|\bverified (?:it |them )?in game\b")
MODDIR_RE = re.compile(r"(?:\bsrc|\bTextures)[/\\]RimMandrake[/\\]([A-Z][A-Za-z]+)[/\\]|"
                       r"\bdesign[/\\]concepts[/\\]([A-Z][A-Za-z]+)[/\\]")
NOT_A_MOD = {"Utils"}
ARTIFACT_RE = re.compile(r"(?i)(?:[A-Z]:\\|/mnt/[a-z]/|\b(?:src|design|infrastructure|Transient)/)[^\s()\"',;]+"
                         r"\.(?:png|jpe?g|webp|gif|bmp|mp4|svg|pdf)\b")
# danger: a FlowWorks trap shares two words with hundreds of later FlowWorks commits, and an unbounded list makes one
# ticket's question longer than a reader batch (modledger_reader.BATCH_CHARS); the best lines by shared words go
CURRENT_LATER = 6           # later work lines per question
CURRENT_TODAY = 4           # today's lines per question
WORK_ORDER_RE = re.compile(r"(?i)^maturation pipeline: take\b|\bblind (?:offline )?challenge cycle \d+\b")
# --- the round-3 judge's rules (verdicts D:\ClaudeWork\rimmandrake\conductor\mining_samples\<Mod>_round3.judge.json):
# every WRONG entry was a trap later work overtook, so a trap is mined only while it is still true today ---
RELENTLESS_STORE = None     # the relentless store (run_store.store_dir()); the selftest stands a fixture in here
STORE_MIN = 150             # a ledger text this long may be the cut copy of a text the relentless store holds whole
# rule 4: a ticket whose every spec path is pipeline code belongs to no mod (a mod's own selftest under Utils/ does)
PIPE_PATH_RE = re.compile(r"^src/RimMandrake/(?:rimflow|Utils)/")
# rule 2: a limit that later work can lift ('cannot be staged', 'until it is reworded', 'no X exists')
CONDITIONAL_RE = re.compile(r"(?i)\bcan(?:not|'t| not)\b|\bcould not be\b|\buntil\b|\bno [\w-]+(?: [\w-]+){0,2} "
                            r"(?:exists?|is available)\b|\bdoes(?:n't| not) exist\b|\bnot (?:possible|stageable|"
                            r"supported)\b|\bimpossible\b|\bunable to\b|\bblocked (?:by|on)\b|\bwaits? (?:for|on)\b")
# the words a limit waits on, quoted ('until the bar is reworded to "thrown a short way"'): in the mod's files = done
UNTIL_QUOTE_RE = re.compile(r"(?i)\b(?:until|reworded|renamed|changes?|changed)\b[^.;]*?['\"‘“]([^'\"’”]{6,80})['\"’”]")
OVERTAKE_SHARE = 0.4        # a later close or commit holding this share of a limit's words (and OVERTAKE_MIN) did it
OVERTAKE_MIN = 3
GROUND_MIN = 0.5            # a reading's trap sentence needs this share of its words in the ticket's own record
# a verdict on a result ('the pass is weaker than it reads'): mined only when the record itself says it (GSS 119)
JUDGEMENT_RE = re.compile(r"(?i)\b(weaker|stronger|unreliable|untrustworthy|meaningless|hollow|degraded)\b|"
                          r"\b(?:reads|claims|proves|says) (less|more) than\b")
FIX_SHA_RE = re.compile(r"(?i)\bfix(?:ed|es)?\b")
PASS_ROW_RE = re.compile(r"\bPASS\b")
_STOP = set("this that with from have been were what when then than they them their there which while into onto over "
            "under also only once does done each every same some more most much such very will would could should "
            "about after before because being both here just like make made many must never none other ours read "
            "reads says said shall since still these those through until upon whose where".split())


def _store_dir():
    if RELENTLESS_STORE:
        return RELENTLESS_STORE
    try:
        import run_store
        return run_store.store_dir()
    except Exception:                    # no relentless on this host: nothing is read whole
        return None


_STORE_TEXTS = {}


def store_texts(name):
    """-> the long texts the relentless item store holds for a ticket (its blind check's reasons, its candidate's
    evidence, its receipts): the whole of what the ledger copies cut at ~300 chars (the round-3 judge, GSS 119)."""
    if name in _STORE_TEXTS:
        return _STORE_TEXTS[name]
    out = []
    d = os.path.join(_store_dir() or "/nonexistent", "items", name)
    if os.path.isdir(d):
        def walk(o):
            if isinstance(o, dict):
                for x in o.values():
                    walk(x)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
            elif isinstance(o, str) and len(o) >= STORE_MIN:
                out.append(" ".join(o.split()))
        for p in [os.path.join(d, "state.json")] + sorted(glob.glob(os.path.join(d, "receipts", "*.json"))):
            walk(_load(p))
    _STORE_TEXTS[name] = out
    return out


def whole(name, text):
    """A ledger text the relentless store holds whole (its tail a cut prefix of a store text): -> its lead and the
    store's whole text; else the text as it is."""
    t = " ".join(str(text or "").split())
    if len(t) < STORE_MIN:
        return text
    full = store_texts(name)
    if not full:
        return text
    for i in [0] + [m.end() for m in re.finditer(r" ", t[:240])]:  # cut-ok: search the lead for possible text starts
        body = t[i:]
        if len(body) < 80:
            break
        for f in full:
            if len(f) > len(body) + 10 and f.startswith(body):
                return t[:i] + f
    return text


def stems(text):
    """A text's content words, each with a plural or verb ending taken off ('doors' -> 'door', 'staged' -> 'stag')."""
    out = set()
    for w in content_words(text):
        for suf in ("ing", "ed", "es", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 4:
                w = w[:-len(suf)]
                break
        out.add(w)
    return out


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
                    for k in ("reason", "why", "text", "config"):
                        if isinstance(e.get(k), str) and len(e[k]) >= STORE_MIN:
                            e[k] = whole(e["id"], e[k])     # rule 1: a cut copy is read whole from the store
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


SAID_KEY1_RE = re.compile(r"(?i)\bmajor fix\b|\bplease ensure\b|\bmust\b|\bnever\b|\balways\b|\bdo not\b|\bdon't\b")
SAID_KEY2_RE = re.compile(r"(?i)\bfix\b|\bshould\b")


def fit_said(text, cap):
    """His words past the cap: his deciding sentences ('major fix', 'please ensure', must/never/always first, then 'fix'
    and 'should'), verbatim and in his order, joined by ' · ' (the journal's own separator), never a leading prefix cut
    with a marker (the round-2 judge, FlowWorks index 13); a text with no such sentence is fitted as any other."""
    t = " ".join(str(text or "").split())
    if len(t) <= cap:
        return t
    sents = [s for s in re.split(r"(?<=[.!?])\s+", t) if s]
    pick = set()
    for rx in (SAID_KEY1_RE, SAID_KEY2_RE):
        for i, s in enumerate(sents):
            if i in pick or not rx.search(s):
                continue
            trial = pick | {i}
            if len(" · ".join(sents[j] for j in sorted(trial))) <= cap:
                pick = trial
    if not pick:
        return fit(t, cap)
    return " · ".join(sents[j] for j in sorted(pick))


def content_words(text):
    return {w for w in re.findall(r"[a-z0-9_]{4,}", str(text or "").lower()) if w not in _STOP}


def coverage(a, b):
    """The share of a's content words that b holds (0 when a has fewer than 3)."""
    ca = content_words(a)
    return len(ca & content_words(b)) / len(ca) if len(ca) >= 3 else 0.0


def _label(text):
    """A hypothesis label a ticket names its causes by ('A6 refuted', 'D7 (…) refuted'): -> the label or None."""
    m = re.match(r"\W*([A-Z]{1,3}\d{1,3}[a-z]?)\b", str(text or ""))
    return m.group(1) if m else None


def filter_trap(text, decisions=(), defects=(), fixed=False):
    """-> (kept text or None, [(reason, sentence)] dropped, [UNRUN sentences]). A trap's sentences are kept unless one
    is a status line (rule 1; a following 'It …' sentence about it leaves with it), a doc correction already made, a
    restatement of his ruling on the same ticket, or, on a ticket closed by a fix, the ticket's own defect (the
    round-2 judge's GSS 257, EK 53/54/82/133, FlowWorks 386/690), or a note on how a fix's red was re-shown (the
    round-4 judge's rule 6, EK 139). A sentence after a dropped one that leans on it (leans()) leaves with it."""
    kept, dropped, unrun, prev = [], [], [], False
    for s in _sentences(text):
        why = None
        if dropped and leans(s):
            why = "leans on a dropped sentence"
        elif REDEMO_RE.search(s):
            why = "how a fix's red was re-shown"
        elif STATUS_RE.search(s):
            why = "status"
            if UNRUN_RE.search(s):
                unrun.append(s)
        elif HISTORY_RE.search(s):
            why = "history"
        elif OWNER_RESTATE_RE.search(s) or any(coverage(s, d) >= 0.6 for d in decisions):
            why = "restates a decision"
        elif fixed and not PAST_READING_RE.search(s) and any(coverage(s, d) >= OWN_DEFECT_COVER for d in defects):
            why = "the ticket's own defect, fixed"
        prev = bool(why)
        if why:
            dropped.append((why, s))
        else:
            kept.append(s)
    out = " ".join(kept).strip()
    out = re.sub(r";$", ".", out)
    return (out if len(out) >= 25 else None), dropped, unrun


LEAN_WORDS = 5     # a sentence with fewer content words than this says nothing without the one before it (FW 72: 3)


def leans(sentence):
    """True when a sentence cannot stand without the one before it: it opens on a pronoun ('It runs only under ...'),
    or it has fewer than LEAN_WORDS content words ('The caveat is filed as X.', FW 72; 'Stage 3 done does not mean the
    scenes pass.', GSS 245; the round-4 judge's rule 2). 'The run4 probe ran with sticky back ON, so it reflects the
    later setting.' stands (the round-2 judge, FW 690)."""
    return bool(PRONOUN_RE.match(sentence)) or len(stems(sentence)) < LEAN_WORDS


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


def fix_shas(evs, landed):
    """-> [(sha on origin/main, event)] for each sha a ticket's notes or close name in a sentence that says it fixed
    something ('D1 fixed at bb6825c7e2', 'BENCH 9b208fdf70: D8 fixed'), in event order."""
    out = []
    for t in evs:
        if t[2].get("event") not in ("note", "close", "implemented"):
            continue
        for k in ("text", "reason", "why"):
            for sen in _sentences(t[2].get(k)):
                if not FIX_SHA_RE.search(sen):
                    continue
                for x in SHA_RE.findall(sen):
                    tw = landed(x)
                    if tw and tw not in [o[0] for o in out]:
                        out.append((tw, t))
    return out


def pass_rows(reason):
    """The clauses of a close reason that name PASS rows, and its evidence clause: the test the close ran (the
    round-3 judge's rule 5, GSS 246), or None."""
    parts = [x for x in re.split(r"(?<=[.;])\s+", clean_lead(reason)) if PASS_ROW_RE.search(x) or
             re.match(r"(?i)\W*evidence\b", x)]
    return " ".join(parts) if any(PASS_ROW_RE.search(x) for x in parts) else None


def _final_state(name, evs, S, state=None, landed=None, bulk=(), reading=None, subject_of=None, date_of=None,
                 title="", mod_re=None, files_of=None):
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
    # rule 3: done, no builder's fix, a note or the close says nothing needed changing, and the close reads PASS
    if state == "done" and close and isinstance(close[2].get("sha"), str) and not [
            t for t in evs if t[2].get("event") == "implemented" and str(t[2].get("sha") or "")[:12] not in bulk]:
        said_ = [str(t[2].get(k) or "") for t in evs if t[2].get("event") in ("note", "close") for k in
                 ("text", "reason", "why")]
        why_ = clean_lead(close[2].get("reason") or close[2].get("why") or "")
        if any(NO_CHANGE_RE.search(x) for x in said_) and re.search(r"\bPASS\b", why_) and \
                not re.search(r"\bFAIL\b", why_):
            return ("finding.withdrawn", {"text": fit("No defect, no code change: %s" % why_, S["text"]),
                                          "how_checked": "test"}, close[2]["sha"], "ledger:%%s:%d" % close[1])
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
    # rule 5: a close on a sha whose commit names nothing of the ticket (the HEAD deployed at a live pass) gives way
    # to the last fix sha the ticket's text names; so does any build or close sha whose commit is bookkeeping (the
    # round-4 judge, FW 94: a 'ledger:' commit). A close commit that names the mod is the ticket's work (GSS 341: 'Owner
    # verified the GSS walkthrough in game'), never an older sha a note names
    subj0 = subject_of(sha) if subject_of else None
    off = subj0 is not None and name not in subj0 and (BOOKKEEP_RE.match(subj0) or (
        pick is close and len(stems(subj0) & stems(title)) < 2 and not (mod_re and mod_re.search(subj0))))
    if off:
        named = [x for x in fix_shas(evs, landed) if not landed(sha) or not x[0].startswith(landed(sha)[:12])]
        if named:
            best = max(named, key=lambda x: ((date_of(x[0]) if date_of else None) or "", named.index(x)))
            sha, ref = best[0], "ledger:%%s:%d" % best[1][1]
    did = reading.get("changed") or changed_text(evs, sha)
    fails = [t[2] for t in evs if t[2].get("event") == "verify" and t[2].get("result") == "fail" and
             (t[2].get("tsn") or 0) > (pick[2].get("tsn") or 0)]
    if BOILER_RE.search(did):
        # rule 4: the landed commit's subject says what changed; a bookkeeping commit or none says nothing, so the
        # text states the build and what its live verifies read after it
        subj = subject_of(sha) if subject_of else None
        if subj and not BOOKKEEP_RE.match(subj):
            did = subject_clause(subj, title)
        else:
            did = "%s at %s; no change named by its record or commit" % (
                "Fixed" if state == "done" else "Built", sha)
            if fails:
                did = "%s at %s; its live verify read FAIL %d time%s after it (%s)" % (
                    "Fixed" if state == "done" else "Built", sha, len(fails), "" if len(fails) == 1 else "s",
                    clean_lead(fails[-1].get("config")) or "a verify")
    impl = next((t[2] for t in reversed(evs) if t[2].get("event") == "implemented" and t[2].get("criteria")), {})
    crit = "; ".join("%s %s" % (c.get("id"), c.get("text")) for c in impl.get("criteria") or [] if isinstance(c, dict))
    if verify:
        v = verify[-1]
        how = " ".join(str(v.get(k)) for k in ("criterion", "level") if v.get(k))
        cfg = clean_lead(v.get("config")) or "a verify pass"
        # a ticket built and verified on some of its criteria names the ones still unverified (the round-3 judge,
        # FlowWorks 1043: the owner-look criterion it waits on)
        seen_c = {str(x.get("criterion")) for x in verify if x.get("criterion")}
        owed = ["%s %s" % (c.get("id"), c.get("text")) for c in impl.get("criteria") or [] if isinstance(c, dict) and
                c.get("id") and str(c.get("id")) not in seen_c] if seen_c and state != "done" else []
        tail = ("; unverified: " + "; ".join(owed)) if owed else ""
        tail = tail if len(tail) <= S["text"] // 2 else fit(tail, S["text"] // 2)
        return ("finding.verified", {"text": fit("%s; verified: %s" % (did, ("%s PASS (%s)" % (how, cfg)) if how else
                                                                       cfg), S["text"] - len(tail)) + tail},
                sha, ref)
    rows = pass_rows(close[2].get("reason") or close[2].get("why")) if close and state == "done" else None
    if fails:       # the command its live verify ran, and what it read, is the test (never the criterion prose)
        test = "%s: FAIL x%d" % (clean_lead(fails[-1].get("config")), len(fails))
    elif rows:      # rule 5: the PASS rows the close names are the test it ran
        test = rows
    else:
        # the round-4 judge, GSS 341 and FW 756: the owner's walk that verified it in game, else the SelfTest files
        # the fix commit touched, is the test before 'none recorded'
        walk = next((clean_lead(t[2].get("text")) for t in reversed(evs) if t[2].get("event") == "note" and
                     OWNER_WALK_RE.search(str(t[2].get("text") or ""))), None)
        tests_ = [os.path.basename(f) for f in (files_of(sha) if files_of else None) or () if
                  re.search(r"(?i)/SelfTest/|/selftest_[^/]*$", f)]
        test = crit or (walk and "in game: " + walk) or (
            tests_ and "the fix commit %s's checks: %s" % (sha, ", ".join(tests_[:4]))) or \
            "none recorded at %s (live: %s)" % ("close" if state == "done" else "build",
                                                (close[2].get("live") if close else None) or "-")
    return ("finding.claimed_fixed", {"text": fit(did, S["text"]), "test": fit(test, S["test"])}, sha, ref)


_TICKET_TEXT = {}


def other_mods_code(root, name, mod):
    """True when a ticket's item file and ledger events name code or art paths of other mods only
    (src/RimMandrake/<Mod>/, Textures/RimMandrake/<Mod>/, design/concepts/<Mod>/), none of `mod`'s."""
    if name not in _TICKET_TEXT:
        parts = []
        for p_ in (os.path.join(root, "infrastructure", "state", "items", name + ".md"),
                   os.path.join(root, "infrastructure", "state", "items", "closed", name + ".md")):
            if os.path.exists(p_):
                with open(p_, encoding="utf-8", errors="replace") as fh:
                    parts.append(fh.read())
        parts += [json.dumps(t[2], ensure_ascii=False) for t in ticket_events(root, {name}).get(name, [])]
        _TICKET_TEXT[name] = {a or b for a, b in MODDIR_RE.findall("\n".join(parts))} - NOT_A_MOD
    dirs = _TICKET_TEXT[name]
    return bool(dirs) and mod not in dirs


def subject_clause(subj, title):
    """The clause of a commit subject ('A: x; y; z') that shares most words with the ticket's title, else the whole
    subject (the round-4 judge, FW 756: a three-mod commit whose 'late deep-swim toggle recomputes' is the fix)."""
    parts = [p_.strip() for p_ in re.split(r";\s+", subj) if p_.strip()]
    if len(parts) < 2:
        return subj
    parts[0] = re.sub(r"^[^:]{1,60}:\s+", "", parts[0])
    tw = stems(title)
    best = max(parts, key=lambda p_: len(stems(p_) & tw))
    return best if len(stems(best) & tw) >= 2 else subj


def readings_path(root, mod):
    """The committed per-ticket readings of one mod (read_tickets writes them; every clone's re-mine reads them, so a
    re-run without --read keeps what the reading found instead of deleting it)."""
    return os.path.join(root, "src", "RimMandrake", "rimflow", "modledger_readings", "%s.json" % mod)


def load_readings(root, mod):
    d = _load(readings_path(root, mod))
    return d.get("tickets", {}) if isinstance(d, dict) else {}


RECORDS_OWNER = {}  # {mod: {ticket: his words numbered}}: what the owner reader is handed
RECORDS_KEEP = {}   # {mod: {ticket: its candidate traps and causes numbered}}: what the keep reader is handed
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
    if len(out.get("proposed_fix") or "x" * 99) < M.config()["proposed_fix_min_chars"]:
        out.pop("proposed_fix")              # a pointer, not a fix: the ticket's own words stand in
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
        idx, twin, subj, commits, dates = {}, {}, {}, [], {}
        for line in r.stdout.split("\n"):
            parts = line.split("\t", 2)
            if len(parts) == 3:
                idx.setdefault(parts[0][:7], []).append(parts[0])
                twin.setdefault((parts[1], parts[2]), []).append(parts[0])
                subj[parts[0][:12]] = parts[2]
                commits.append((parts[1], parts[0][:12], parts[2]))
                dates[parts[0][:12]] = parts[1]
        commits.reverse()
        _BASE[root] = (idx, twin, subj, commits, dates)
    return _BASE[root]


def commit_subject(root, sha):
    """-> the subject of `sha`'s landed commit on origin/main (rule 4's fallback for a boilerplate fix text), or None."""
    tw = landed_sha(root, sha)
    if not tw or not os.path.exists(os.path.join(root, ".git")):
        return None
    return _base(root)[2].get(tw[:12])


SUBJECT_OF = commit_subject      # the selftest stands a fake in here (its fixture root is no git checkout)


def landed_sha(root, sha):
    """-> the 12-char origin/main sha for `sha` (the standard's lint rule for every code_sha): itself when it is on
    origin/main; else its landed twin, the one origin/main commit with the same author date and subject (`./publish`
    rebases, so a close often records the pre-landing sha); else None. One `git log` per root, then lookups."""
    if not re.match(r"^[0-9a-f]{7,40}$", sha or ""):
        return None
    if not os.path.exists(os.path.join(root, ".git")):
        return sha                  # not a git checkout (a fixture): taken as written
    idx, twin = _base(root)[:2]
    hit = [f for f in idx.get(sha[:7], ()) if f.startswith(sha)]
    if len(hit) == 1:
        return hit[0][:12]
    r = subprocess.run(["git", "-C", root, "log", "--no-walk", "--format=%aI%x09%s", sha, "--"], capture_output=True,
                       text=True, timeout=60)  # budget: danger=a hung git read (a stuck drvfs read) holds its caller; longest=3.8s (210 local git calls sampled at load 20 to 52, 2026-11-24)
    parts = r.stdout.strip().split("\t", 1) if r.returncode == 0 else []
    t = twin.get(tuple(parts)) if len(parts) == 2 else None
    return t[0][:12] if t and len(t) == 1 else None


def ref_path(state, tev, name):
    """The shard path of the event a final state came from (the pattern carries its line)."""
    line = int(state[3].rsplit(":", 1)[1])
    return next(t[0] for t in tev.get(name, []) if t[1] == line)


def pipeline_only(prose, mod, words, leads=False):
    """A ticket whose spec (its '## spec' section, else its whole prose) names paths, every one pipeline code under
    src/RimMandrake/rimflow/ or Utils/ and none the mod's own (a selftest_<mod>.py): it belongs to no mod (the round-3
    judge's rule 4, GSS 361: a rimflow selftest naming the mod in a case title). A ticket whose title leads with the
    mod, or whose spec names C# or XML (the mod's code), stays the mod's."""
    m = re.search(r"^## spec\s*\n(.*?)(?=^## |\Z)", prose or "", re.S | re.M | re.I)
    spec = m.group(1) if m else prose or ""
    paths = PATH_RE.findall(spec)
    keys = {mod.lower()} | {w.lower() for w in words if len(w) >= 3}
    if leads or re.search(r"(?i)\b[\w-]+\.(?:cs|xml|dll)\b", spec):
        return False
    return bool(paths) and all(PIPE_PATH_RE.match(p) and not any(k in os.path.basename(p).lower() for k in keys)
                               for p in paths)


def judged_in(sentence, record):
    """False when the sentence passes a verdict on a result ('weaker', 'degraded', 'reads less than') that the record
    never states (GSS 119: the reader drew 'the pass is weaker than it reads' from a cut fragment)."""
    low = str(record).lower()
    return all((m.group(1) or m.group(0)).lower() in low for m in JUDGEMENT_RE.finditer(sentence))


def grounded_in(text, record):
    """A text the record states: GROUND_MIN of its content words (endings off) are in it (a short one always)."""
    w = stems(text)
    return len(w) < 3 or len(w & stems(record)) / len(w) >= GROUND_MIN


def _commits(root):
    """-> [(author date, 12-char sha, subject)] of origin/main, oldest first (one `git log` per root)."""
    _base(root)
    return _BASE[root][3]


COMMITS = _commits            # the selftest stands a fake in here (its fixture root is no git checkout)


def commit_date(root, sha):
    tw = landed_sha(root, sha)
    if not tw or not os.path.exists(os.path.join(root, ".git")):
        return None
    return _base(root)[4].get(tw[:12])


COMMIT_DATE = commit_date


def _commit_info(root):
    """-> {12-char sha: (message body, [paths touched])} of origin/main since 2026-08-01 (one `git log` per root):
    what a later commit changed, for the currency check (the round-4 judge: the commits that overtook its four WRONG
    traps named the files and scenes the traps name, never the trap's ticket or, often, the mod)."""
    if root not in _INFO:
        out = {}
        if os.path.exists(os.path.join(root, ".git")):
            r = subprocess.run(["git", "-C", root, "log", "origin/main", "--since=2026-08-01", "--name-only",
                                "--format=%x1e%H%x1f%b%x1f"], capture_output=True, text=True, timeout=300)
            for rec in r.stdout.split("\x1e")[1:]:
                parts = rec.split("\x1f")
                if len(parts) == 3:
                    out[parts[0][:12]] = (" ".join(parts[1].split()),
                                          [x.strip() for x in parts[2].split("\n") if x.strip()])
        _INFO[root] = out
    return _INFO[root]


_INFO = {}
COMMIT_INFO = _commit_info    # the selftest stands a fake in here (its fixture root is no git checkout)
_TODAY = {}
# records of past runs and judgings say what WAS (a cycle's faults, a visit's rows, a repair's calibration): never
# what the mod's files say today
TODAY_SKIP_DIRS = {"ledger", "views", ".git", "bin", "obj", "Textures", "Assemblies", "blind_challenge",
                   "criterion_repairs", "in_game", "evidence", "pilot_throwaway", "next_version", "art_source", "review",
                   "live_probes", "fix_demos"}
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def today_index(root, mod):
    """-> ([(repo path, line number, line)], {token: [row]}) of the mod's own design and source files as they are
    today (code, scenes, tables, sheets; never its journal, log, ledger, views or readings, which quote words that may
    not have landed). The token map finds the lines that hold a name without a scan per question."""
    if (root, mod) not in _TODAY:
        rows, tok = [], {}
        for base in (os.path.join(root, "design", "concepts", mod), os.path.join(root, "src", "RimMandrake", mod)):
            for d, dirs, fs in os.walk(base):
                dirs[:] = sorted(x for x in dirs if x not in TODAY_SKIP_DIRS and not x.startswith("rescue_"))
                for f in sorted(fs):
                    if f in ("journal.md", "log.md") or not f.endswith(TODAY_EXT) or f.endswith(".judge.json"):
                        continue
                    p = os.path.join(d, f)
                    try:
                        if os.path.getsize(p) > 2_000_000:
                            continue
                        with open(p, encoding="utf-8", errors="replace") as fh:
                            for n, line in enumerate(fh, 1):
                                if line.strip():
                                    for t in set(TOKEN_RE.findall(line)):
                                        tok.setdefault(t, []).append(len(rows))
                                    rows.append((_rel(root, p), n, line.strip()))
                    except OSError:
                        pass
        _TODAY[(root, mod)] = (rows, tok)
    return _TODAY[(root, mod)]


def idents(text):
    """The names a sentence or a `where` points at: backticked words, snake_case and CamelCase names, file names."""
    out = []
    for m in IDENT_RE.finditer(str(text or "")):
        x = next(g for g in m.groups() if g).strip(".")
        if x not in out and len(x) >= 3:
            out.append(x)
    return out


_STOP3 = set("the and for not was are but its has had any all one two can may did why how who new now out off own per "
             "via yet got let see set use too run ran end".split())


def _parts(text):
    """Stems of a text with its snake_case and dotted names split ('sc_storeroom_mortar' -> storeroom, mortar), and
    its three-letter words too ('sink cap': FW 451's overtaking commit is 'sink cap to 4 m')."""
    t = re.sub(r"[_.]", " ", str(text or ""))
    return stems(t) | {w for w in re.findall(r"\b[a-z]{3}\b", t.lower()) if w not in _STOP3}


PHRASE_WEIGHT = 8          # a two-word phrase shared word for word outranks several loose words (FW 451: 'sink cap')


def phrases(sentence):
    """The sentence's two-word phrases of content words, lowercased ('sink cap', 'oracle scenes')."""
    ws = re.findall(r"[a-z][a-z0-9]+", str(sentence or "").lower())
    return {"%s %s" % (a, b) for a, b in zip(ws, ws[1:]) if len(a) >= 3 and len(b) >= 3 and
            a not in _STOP | _STOP3 and b not in _STOP | _STOP3}


def _rows_with(root, mod, name):
    """-> the rows of today_index that hold `name` whole (each of its tokens, in order)."""
    rows, tok = today_index(root, mod)
    ts = TOKEN_RE.findall(name)
    if not ts:
        return []
    cand = set(tok.get(ts[0], ()))
    for t in ts[1:]:
        cand &= set(tok.get(t, ()))
    rx = re.compile(r"(?<![\w])%s(?![\w])" % re.escape(name))
    return [i for i in sorted(cand) if rx.search(rows[i][2])]


def today_lines(root, mod, sentence, where, skip=()):
    """-> ['path:line: text'] of the mod's files today that hold a name the sentence or its `where` points at: lines
    in a file the sentence names first, then those holding most of its names and words, at most CURRENT_TODAY (the
    round-4 judge, EK 125: the scene's criterion today says a whole-cell band; FW 451: the known-red entry today drops
    itself once the cap is 8)."""
    names = [x for x in idents(sentence) + idents(where) if x not in skip]
    files = [x for x in names if re.search(r"\.(?:cs|py|json|xml|md)$", x)]
    keys = [x for x in names if x not in files]
    if not keys:
        return []
    rows = today_index(root, mod)[0]
    sw = _parts(sentence)
    score = {}
    for k in keys:
        for i in _rows_with(root, mod, k):
            score[i] = score.get(i, 0) + 1
    ranked = sorted(score, key=lambda i: (-any(rows[i][0].endswith("/" + f) for f in files), -score[i],
                                          -len(sw & _parts(rows[i][2])), rows[i][0], rows[i][1]))
    return ["%s:%d: %s" % (rows[i][0], rows[i][1], fit(rows[i][2], 220)) for i in ranked[:CURRENT_TODAY]]


def present_today(root, mod, name):
    """True when a code file of the mod (C#, Python, JSON, XML) holds `name` as a whole word today."""
    rows = today_index(root, mod)[0]
    return any(rows[i][0].endswith(CODE_EXT) for i in _rows_with(root, mod, name))


_MOD_TEXT = {}


def mod_text(root, mod):
    """The lowercased text of the mod's own design and source files (its scenes, tree, sheets, defs), never its
    journal, log, ledger or readings (they quote words that may not have landed)."""
    if (root, mod) not in _MOD_TEXT:
        parts = []
        for base in (os.path.join(root, "design", "concepts", mod), os.path.join(root, "src", "RimMandrake", mod)):
            for d, dirs, fs in os.walk(base):
                dirs[:] = [x for x in dirs if x not in ("ledger", "views", ".git", "bin", "obj")]
                for f in fs:
                    if f in ("journal.md", "log.md") or not f.endswith((".json", ".md", ".xml", ".txt", ".py")) or \
                            f.endswith(".judge.json"):
                        continue
                    p = os.path.join(d, f)
                    try:
                        if os.path.getsize(p) <= 2_000_000:
                            with open(p, encoding="utf-8", errors="replace") as fh:
                                parts.append(fh.read().lower())
                    except OSError:
                        pass
        _MOD_TEXT[(root, mod)] = "\n".join(parts)
    return _MOD_TEXT[(root, mod)]


def _iso(ts):
    """An ISO time (Z or an offset) as a comparable UTC string 'YYYY-MM-DDTHH:MM:SS', or ''."""
    import datetime
    try:
        d = datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return ""
    if d.tzinfo:
        d = d.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return d.strftime("%Y-%m-%dT%H:%M:%S")


def drop_overtaken(root, mod, ev, tev, titles, states, mod_words, notes, raw_readings=None):
    """The round-3 judge's class fix: a trap is mined only while it is still true today, sentence by sentence (all
    three round-3 WRONG entries were traps later work overtook: EK 51, EK 119, GSS 119). A sentence stating a limit
    ('cannot be staged', 'until it is reworded to X', 'no X exists') leaves when the words it waits on are in the mod's
    own files, when a ticket it names closed after it, or when another of the mod's tickets FILED about that limit (its
    title holds the limit's words, and its close speaks to them) was closed after it. Any other sentence that later
    work may have made false (a later close, verify or note on one of the mod's tickets, its own included, or a later
    origin/main commit naming the mod, sharing its words) is a question for the currency reader (`claude -p`,
    modledger_reader.CURRENT_SYSTEM): its committed answer drops the sentences it found no longer true; an unread one
    stays. A sentence's date is the ticket event that states it, else the ticket's filing. -> the plan with those
    sentences out (an entry left under 25 chars leaves whole), counted in `notes`; the questions go to
    RECORDS_CURRENT[mod]."""
    raw_readings = raw_readings or {}
    drop_w = {w for x in mod_words for w in stems(x)} | stems(re.sub(r"(?<=[a-z])(?=[A-Z])", " ", mod)) | \
        stems(mod.lower())
    name_re = re.compile(r"(?i)\b(?:%s)\b" % "|".join(re.escape(x) for x in sorted(
        set(mod_words) | {mod, re.sub(r"(?<=[a-z])(?=[A-Z])", " ", mod)}) if x))
    later = []           # (ts, ticket, words, is a close of a fix): what happened on the mod's tickets
    for n in states:
        for t in tev.get(n, []):
            e = t[2]
            k = e.get("event")
            if k in ("close", "implemented", "note") or (k == "verify" and e.get("result") == "pass"):
                txt = clean_lead(e.get("reason") or e.get("why") or e.get("text") or e.get("config") or "")
                if txt and not R.QUARANTINE_RE.search(txt):
                    later.append((_iso(e.get("ts")), n, txt, k in ("close", "implemented") and
                                  states.get(n) in ("done", "built", "validated")))
    traps = [i for i, e in enumerate(ev) if e[0] == "trap.noted"]
    named = {x for i in traps for x in re.findall(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b", ev[i][2].get("text") or "")}
    nev = ticket_events(root, named) if named else {}
    nstate = rimflow_states(root, sorted(nev), nev) if nev else {}
    low = mod_text(root, mod)
    commits = COMMITS(root) if traps else []
    # the round-4 judge's class fix: what later commits of ANY ticket did to the files a trap names or to the mod's own
    # files, and the trap ticket's own fix commits with their message body (GSS 170, EK 65, EK 125, FW 451)
    info = COMMIT_INFO(root) if traps else {}
    cmeta = {csha: (_iso(ts), subj) for ts, csha, subj in commits}
    by_base, mod_shas = {}, []
    prefixes = ("design/concepts/%s/" % mod, "src/RimMandrake/%s/" % mod)
    for csha, (_body, files) in info.items():
        if csha not in cmeta:
            continue
        for f in files:
            by_base.setdefault(os.path.basename(f), []).append(csha)
        if any(f.startswith(prefixes) for f in files):
            mod_shas.append(csha)

    words_of_c = {c_: _parts(cmeta[c_][1] + " " + (info.get(c_) or ("", []))[0]) for c_ in info if c_ in cmeta}
    df = {}
    for ws_ in words_of_c.values():
        for x in ws_:
            df[x] = df.get(x, 0) + 1
    n_c = max(1, len(words_of_c))

    def idf(ws_):
        return sum(math.log(n_c / df.get(x, 1)) for x in ws_)

    def own_shas(evs_):
        """Every sha the trap's ticket stamps or names (newest last): its own fix commits (GSS 170: 'gss_four at
        0416599c69' named the fix in a note with no 'fixed' beside the sha)."""
        out_s = []
        for t in evs_:
            x = t[2].get("sha") if t[2].get("event") in ("close", "implemented") else None
            if isinstance(x, str) and re.match(r"^[0-9a-f]{7,40}$", x):
                out_s.append(x)
            if t[2].get("event") in ("note", "close", "implemented"):
                for k_ in ("text", "reason", "why"):
                    out_s += SHA_RE.findall(str(t[2].get(k_) or ""))
        res_ = []
        for x in out_s:
            tw = landed_sha(root, x) or x
            tw = next((c_ for c_ in cmeta if c_.startswith(tw[:12]) or tw.startswith(c_)), None)
            if tw and tw not in res_:
                res_.append(tw)
        return res_

    def commit_line(csha, own=False):
        body_ = (info.get(csha) or ("", []))[0]
        return "%s %s %s: %s%s" % ("fix commit" if own else "commit", csha, cmeta[csha][0][:10], cmeta[csha][1],
                                   (" | " + fit(body_, 300)) if body_ else "")
    cut, gone, asks = {}, {}, {}

    def out_(i, k, why):
        cut.setdefault(i, set()).add(k)
        gone[why[0]] = gone.get(why[0], 0) + 1
        tick_ = next((r[5:] for r in ev[i][3] if r and r.startswith("item:")), None)
        DROPPED_OVERTAKEN[mod].append((tick_, _sentences(ev[i][2]["text"])[k], "%s (%s)" % why))
    for i in traps:
        kind, subject, body, evidence, auth, sha = ev[i]
        tick = next((r[5:] for r in evidence if r and r.startswith("item:")), None)
        evs = tev.get(tick, [])
        for k, sen in enumerate(_sentences(body.get("text") or "")):
            tw = stems(sen) - drop_w
            if len(tw) < OVERTAKE_MIN:
                continue
            src = next((t for t in evs if any(len(tw & stems(t[2].get(f))) / len(tw) >= 0.5 for f in (
                "text", "reason", "why", "byCard", "title", "spec"))), None) or next(
                (t for t in evs if t[2].get("event") == "file"), None)
            t0 = _iso(src[2].get("ts")) if src else ""
            gone_ = next((x for x in ABSENT_RE.findall(sen) if x.lower() != mod.lower() and
                          re.search(r"_|[a-z][A-Z]|\d", x) and present_today(root, mod, x)), None)
            if gone_:
                out_(i, k, ("the thing it says is missing is in the mod's code today", gone_))
                continue
            if CONDITIONAL_RE.search(sen):
                why = next((("the words it waits on are in the mod's files", q) for q in UNTIL_QUOTE_RE.findall(sen)
                            if q.lower() in low), None)
                for x in sorted(named & set(re.findall(r"\b[A-Z][A-Z0-9_]+\b", sen))) if not why else ():
                    if x != tick and nstate.get(x) == "done" and [t for t in nev.get(x, []) if t[2].get("event") in (
                            "close", "implemented") and _iso(t[2].get("ts")) > t0]:
                        why = ("a ticket it names was closed after it", x)
                        break
                for ts, n, txt, fixed in later if not why and t0 else ():
                    sh = tw & stems(titles.get(n))
                    # its close must speak to the limit too: a title that quotes the limit beside another defect
                    # (GSS_SLICE_FIX_LONE_REBUILD_HITS_140MS: 'maxSliceMs is a lifetime max') closed on that defect
                    if fixed and n != tick and ts > t0 and len(sh) >= OVERTAKE_MIN + 1 and \
                            len(sh) / len(tw) >= OVERTAKE_SHARE and len(tw & stems(txt)) >= 2:
                        why = ("a ticket filed about that limit was closed after it", n)
                        break
                if why:
                    out_(i, k, why)
                    continue
            if not t0:
                continue
            cand = [(len(tw & stems(subj)), "commit %s %s: %s" % (csha, str(ts)[:10], subj)) for ts, csha, subj in
                    commits if _iso(ts) > t0 and name_re.search(subj) and len(tw & stems(subj)) >= OVERTAKE_MIN]
            cand += [(len(tw & stems(txt)), "%s %s %s: %s" % ("close of" if fixed else "note on", n, ts[:10],
                                                              fit(txt, 300)))
                     for ts, n, txt, fixed in later if ts > t0 and
                     len(tw & stems(txt)) >= OVERTAKE_MIN + (0 if n == tick else 1)]
            sw = _parts(sen) - drop_w
            pairs = phrases(sen)
            named_f = {os.path.basename(x) for x in idents(sen) + idents(body.get("where")) if
                       re.search(r"\.(?:cs|py|json|xml|md)$", x)}
            seen_c = {c_.split(" ", 2)[1] for _n, c_ in cand if c_.startswith("commit ")}
            # the ticket's own commits stated after it, newest first (the reader sees each with its date)
            own = sorted((x for x in own_shas(evs) if cmeta[x][0] > t0), key=lambda x: cmeta[x][0], reverse=True)[:3]
            more = {}
            for csha in {x for b in named_f for x in by_base.get(b, ())} | set(mod_shas):
                if csha in seen_c or csha in own or cmeta[csha][0] <= t0:
                    continue
                sh = sw & words_of_c.get(csha, set())
                touched = named_f & {os.path.basename(f) for f in info[csha][1]}
                if len(sh) >= (1 if touched else 2):
                    low_c = (cmeta[csha][1] + " " + (info.get(csha) or ("", []))[0]).lower()
                    more[csha] = idf(sh) + (5 if touched else 0) + PHRASE_WEIGHT * sum(1 for x in pairs if x in low_c)
            cand = [(n_ * 10, c_) for n_, c_ in cand] + [(n_, commit_line(x)) for x, n_ in more.items()]
            today = today_lines(root, mod, sen, body.get("where"), skip={mod})
            lines_ = [commit_line(x, own=True) for x in own] + [c_ for _n, c_ in sorted(
                cand, key=lambda x: (-x[0], x[1]))][:max(0, CURRENT_LATER - len(own))]
            if lines_ or today:
                asks.setdefault(tick, []).append((i, k, t0, sen, lines_, today))
    RECORDS_CURRENT[mod] = {}
    unread = 0
    for tick, qs in asks.items():
        rtext = R.current_text(tick, titles.get(tick), [(t0, sen, cs, td) for _i, _k, t0, sen, cs, td in qs])
        RECORDS_CURRENT[mod][tick] = rtext
        rr = raw_readings.get(tick) or {}
        if not (isinstance(rr.get("current"), list) and rr.get("current_hash") == R.rec_hash(rtext, "current")):
            unread += 1
            continue
        for n_, (i, k, _t0, _sen, cs, td) in enumerate(qs, 1):
            if n_ in rr["current"]:
                out_(i, k, ("the currency reader found later work made it false", (cs or td)[0]))
    out = []
    for i, e in enumerate(ev):
        if i not in cut:
            out.append(e)
            continue
        kind, subject, body, evidence, auth, sha = e
        # the round-4 judge's rule 2 (GSS 245, FW 72): a sentence after a dropped one that leans on it leaves too
        sents = _sentences(body["text"])
        for k in range(min(cut[i]) + 1, len(sents)):
            if k not in cut[i] and leans(sents[k]):
                cut[i].add(k)
        kept = " ".join(x for k, x in enumerate(sents) if k not in cut[i])
        if len(kept) >= 25:
            out.append((kind, "trap:" + slug(kept, 8), dict(body, text=kept), evidence, auth, sha))
    if gone:
        notes.append("left out: trap sentences later work made false (round-3 judge): " + "; ".join(
            "%d %s" % (n, w) for w, n in sorted(gone.items())))
    if unread:
        notes.append("currency: %d tickets with trap sentences later work may have made false are unread (kept; "
                     "read with --read)" % unread)
    return out


RECORDS_CURRENT = {}        # {mod: {ticket: its limit traps and the later work that may have lifted them}}
DROPPED_OVERTAKEN = {}      # {mod: [(ticket, trap text, why)]}: what drop_overtaken left out, for the report


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
    DROPPED_OVERTAKEN[mod] = []
    raw_readings = load_readings(root, mod)
    RECORDS[mod] = {}
    RECORDS_KEEP[mod] = {}
    dropped_keep = 0
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
            said = fit_said(_said(vj["owner_words"]), S["said"])
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
    fault_ids, noted, fault_raw, pipe_faults = set(), 0, {}, 0
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
            # the round-4 judge's rule 4 (EK 8): a fault on no bar of the mod ('(record format)'), noted for the
            # Conductor, is a defect of the pipeline's own recorder: no finding of the mod
            if not fbars and str(f.get("status") or "").upper() == "NOTED_FOR_CONDUCTOR" and \
                    re.match(r"^\s*\(", str(f.get("bar") or "")) and "instrument" not in str(f.get("bar")):
                fault_ids.add(f["id"])
                pipe_faults += 1
                continue
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
    if pipe_faults:
        notes.append("left out: %d blind faults on no bar of the mod, noted for the Conductor (the pipeline's own "
                     "recorder, the round-4 judge's rule 4)" % pipe_faults)
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
                said = fit_said(_said(b), S["said"])
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

    mod_re = re.compile(r"(?i)\b(?:%s)\b" % "|".join(re.escape(x) for x in sorted(
        {mod, spaced, word} | set(words) | set(cfg.get("backfill_title_names", {}).get(mod, []))) if x))
    rebased = work_orders = pipeline_tickets = ungrounded = 0
    ticket_ctx = {}
    claimed = {s for k, s, *_ in ev if k == "finding.claimed_fixed"}
    closed_unstated, sha_dead, refuted_no_sha, causes_seen = [], 0, 0, set()
    for ip, is_closed in cands:
        if ip is None:
            name, prose, ip = is_closed, titles[is_closed], None
            is_closed = _closed_in_ledger(tev.get(name, []))
            fspec = next((t[2]["spec"] for t in tev.get(name, []) if t[2].get("event") == "file" and
                          isinstance(t[2].get("spec"), str) and t[2]["spec"].strip()), None)
            if fspec:           # a ledger-only ticket's filed spec is its spec (the round-3 judge's rule 6)
                prose = "%s\n\n## spec\n\n%s\n" % (prose, fspec)
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
        if pipeline_only(prose, mod, words, bool(lead.search(titles.get(name) or ""))):
            pipeline_tickets += 1
            continue
        rd = readings.get(name) or {}
        fr = fault_raw.get(name) or (None, None, None)
        RECORDS[mod][name] = R.record_text(name, titles.get(name), states.get(name), prose if ip else None,
                                           tev.get(name, []), fr[0], fr[1], _rel(root, ip) if ip else fr[2])
        wo = bool(WORK_ORDER_RE.search(titles.get(name) or ""))
        state = None if wo else _final_state(name, tev.get(name, []), S, states.get(name), landed, bulk, rd,
                                             lambda x: SUBJECT_OF(root, x), lambda x: COMMIT_DATE(root, x),
                                             titles.get(name) or "", mod_re,
                                             lambda x: (COMMIT_INFO(root).get((landed(x) or x)[:12]) or ("", []))[1])
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
        if is_closed and not state and not wo:
            closed_unstated.append(name)
            continue
        if wo:
            work_orders += 1
        items.append(name)
        ticket_ctx[name] = {"fixed": bool(state) and state[0] in ("finding.claimed_fixed", "finding.verified"),
                            "defects": [titles.get(name) or "", rd.get("defect") or ""] + [
                                str(t[2].get(k) or "") for t in tev.get(name, []) if t[2].get("event") == "file"
                                for k in ("why", "reason", "title")]}
        fe = next((t for t in tev.get(name, []) if t[2].get("event") == "file"), None)
        src = [P(ip) if ip else "path:%s:%d" % (_rel(root, fe[0]), fe[1]), "item:" + name]
        etexts = [str(t[2].get(k) or "") for t in tev.get(name, []) for k in ("text", "why", "reason", "title")
                  if t[2].get("event") in ("file", "note", "close", "implemented")]
        if name in fault_ids:
            dup_fault += 1
        elif not wo:           # a work order names nothing wrong with the mod: its facts are its traps
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
                                   str(e.get("sha") or "")[:12] not in bulk and
                                   not R.QUARANTINE_RE.search(str(e.get("text") or ""))]
        found = [("cause", c.get("text"), c.get("depends_on") or [], None) for c in rd.get("causes_refuted") or []
                 if isinstance(c, dict) and c.get("text")] + \
                [("trap", c.get("text"), [], c.get("where")) for c in rd.get("traps") or []
                 if isinstance(c, dict) and c.get("text")]
        # rule 1: a reading's sentence stating what the ticket's record does not ('the pass is weaker than it reads')
        # is left out; the rest of the entry stays
        grounded = []
        for f_ in found:
            sents = _sentences(f_[1])
            kept_ = " ".join(x for x in sents if judged_in(x, RECORDS[mod][name]))
            if len(kept_) >= 25 and grounded_in(kept_, RECORDS[mod][name]):
                grounded.append((f_[0], kept_) + tuple(f_[2:]))
                ungrounded += len(kept_) < len(" ".join(sents))      # a verdict sentence left out
            else:
                ungrounded += 1
        found = grounded
        for t, txt in texts:
            for sen in _sentences(words_of(txt)):
                is_cause = (CAUSE_RE.search(sen) or REFUTED_RE.search(sen)) and not NOT_REFUTED_RE.search(sen)
                if not (is_cause or TRAP_RE.search(sen)):
                    continue
                if rd and not (REFUTED_RE.search(sen) and is_cause):
                    continue              # the reading read these lines with judgement; only an explicit 'X refuted'
                    #                       or 'False theory:' sentence is added beside its list
                found.append(("cause" if is_cause else "trap", sen, PATH_RE.findall(sen), None, t, txt))
        # the keep pass: a reader that sees the ticket's candidates together keeps only those that would change what
        # a holder does to the mod (process trivia, status lines and restatements leave)
        if found:
            ktext = R.keep_text(name, titles.get(name), rd.get("defect"), [
                ("C" if f_[0] == "cause" else "T", f_[1], f_[3]) for f_ in found])
            RECORDS_KEEP[mod][name] = ktext
            kr = raw_readings.get(name) or {}
            if isinstance(kr.get("keep"), list) and kr.get("keep_hash") == R.rec_hash(ktext, "keep"):
                dropped_keep += len(found) - len([f_ for i_, f_ in enumerate(found) if i_ + 1 in kr["keep"]])
                found = [f_ for i_, f_ in enumerate(found) if i_ + 1 in kr["keep"]]
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
            if kind_ == "cause" and shas and not wo:
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
            # on a ticket that is not one of this mod's, his words count only when they name the mod themselves, and
            # the ticket's code and art are not another mod's (the round-4 judge's rule 4, GSS 0: a FlowWorks tank
            # ticket in the four GSS looks)
            if iid not in mined_items and not (squash(mod) in squash(said or card) or name_re.search(said or card)):
                off_mod += 1
                continue
            if iid not in mined_items and iid and other_mods_code(root, iid, mod):
                off_mod += 1
                continue
            cand.append((sp_, i, said, card, iid, e.get("text") if isinstance(e.get("text"), str) else ""))
    by_ticket = {}
    for c_ in cand:
        if c_[4]:
            by_ticket.setdefault(c_[4], []).append(c_[2] or c_[3])
    RECORDS_OWNER[mod] = {t: R.owner_text(t, titles.get(t), mod, ws) for t, ws in by_ticket.items()}
    for sp_, i, said, card, iid, etext in cand:
        # on a ticket the owner reader read, only the words it marked as a ruling about the mod
        orr = raw_readings.get(iid) or {}
        if iid in by_ticket and isinstance(orr.get("owner"), list) and orr.get("owner_hash") == R.rec_hash(
                RECORDS_OWNER[mod][iid], "owner"):
            n_ = by_ticket[iid].index(said or card) + 1
            if n_ not in orr["owner"]:
                not_ruling += 1
                continue
        words_ = fit_said(said, S["said"]) if said else fit(card, S["text"])
        if not his(words_):
            continue
        subj = ("finding:" + iid) if iid and "finding:" + iid in mined else "q:" + slug(iid or words_, 12)
        auth = {"owner_said": words_} if said else {"by_card": words_}
        body_ = {"said": words_} if said else {"text": words_}
        # the round-4 judge's rule 5 (GSS 378): words that point at a photo or file the event names cite it, with
        # the event's own reading of it
        art = ARTIFACT_RE.findall(etext or "")
        if said and art:
            body_["text"] = fit(etext, S["text"])
        add("decision", subj, body_, ["path:%s:%d" % (_rel(root, sp_), i), ("item:" + iid) if iid else None] +
            ["ext:" + a_ for a_ in art[:2] if len(a_) + 4 <= M.std()["evidence_ref_chars"]], auth)  # longer paths remain in the cited event
    ev = apply_judge_rules(ev, ticket_ctx, decider, tt.get("tests") if isinstance(tt.get("tests"), dict) else {}, S,
                           notes)
    ev = drop_overtaken(root, mod, ev, tev, titles, {n: states.get(n) or _fold(tev.get(n, [])) for n in items},
                        set(words) | {word}, notes, raw_readings)
    if pipeline_tickets:
        notes.append("left out: %d tickets whose every spec path is pipeline code (rimflow/, Utils/): no mod's"
                     % pipeline_tickets)
    if ungrounded:
        notes.append("left out: %d reading traps and causes (or their verdict sentences) the ticket's record does not "
                     "state" % ungrounded)
    if work_orders:
        notes.append("%d pipeline work-order tickets (a stage take, a blind cycle) mine no finding: their traps stand"
                     % work_orders)
    if dropped_keep:
        notes.append("left out: %d traps and ruled-out causes the keep reader found would change nothing a holder "
                     "does" % dropped_keep)
    if off_mod or not_ruling:
        notes.append("left out: %d owner words on other tickets that do not name the mod, %d the owner reader found "
                     "no ruling about it" % (off_mod, not_ruling))
    if lifecycle_words:
        notes.append("left out: %d owner words riding lifecycle or fleet-wide events (authority for an act, not a "
                     "statement about the mod)" % lifecycle_words)
    return ev, notes


OWN_DEFECT_COVER = 0.6      # a trap sentence this much of whose words are the fixed ticket's own defect restates it
TWIN_COVER = 0.7            # two lines of one kind on one ticket this much alike are one fact


def apply_judge_rules(ev, ctx, decider, tests, S, notes):
    """The round-2 judge's rules over a whole plan, after the keep pass (so no reading's hash moves): a trap keeps only
    its sentences that are no status line, doc history, restated ruling or (on a ticket closed by a fix) its own
    defect (rule 1); a status sentence naming an UNRUN scene of a bar with no live row becomes that bar's live.run
    UNRUN; a cause.refuted needs a sentence that rules it out (rule 2); a later twin of a line on the same ticket leaves
    (rule 5: the re-mine's leftovers, e.g. a regex 'A6 refuted' beside the reading's A6). `ctx` is {ticket: {"fixed":
    bool, "defects": [texts]}}. -> the new plan; what left is counted in `notes`."""
    dec = {}
    for kind, subject, body, evidence, auth, sha in ev:
        if kind == "decision":
            for r in evidence:
                if r and r.startswith("item:"):
                    dec.setdefault(r[5:], []).append(body.get("said") or body.get("text") or "")
    live_bars = {s for k, s, *_ in ev if k == "live.run"}
    out, counts, unrun_rows, seen = [], {}, [], {}

    def count(why):
        counts[why] = counts.get(why, 0) + 1

    for e in ev:
        kind, subject, body, evidence, auth, sha = e
        tick = next((r[5:] for r in evidence if r and r.startswith("item:")), None)
        if tick is None or kind not in ("trap.noted", "cause.refuted"):
            out.append(e)
            continue
        c = ctx.get(tick) or {}
        text = body.get("text") or ""
        if kind == "cause.refuted":
            if STATE_CHANGE_RE.search(text) or (FOUND_CAUSE_RE.search(text) and not EXPLICIT_REFUTED_RE.search(text)) \
                    or not (RULED_OUT_RE.search(text) or HYPOTHESIS_RE.match(text)):
                count("cause.refuted with no sentence ruling it out")
                continue
        elif R.QUARANTINE_RE.search(text):
            count("trap: a test-queue quarantine note (lifecycle, the round-3 judge's rule 3)")
            continue
        elif pipe_trap(text, body.get("where")):
            count("trap about pipeline code under src/RimMandrake/rimflow/ (the round-4 judge's rule 4)")
            continue
        else:
            kept, dropped, unrun = filter_trap(text, dec.get(tick, ()), c.get("defects", ()), c.get("fixed"))
            for why, _s in dropped:
                count("trap sentence: " + why)
            unrun_rows += [(s_, evidence) for s_ in unrun]
            if not kept:
                continue
            if kept != text:
                body = dict(body, text=fit(kept, S["text"]))
                subject = "trap:" + slug(kept, 8)
        twins = seen.setdefault((tick, kind), [])
        t2 = body["text"]
        if any((_label(p) and _label(p) == _label(t2)) or coverage(t2, p) >= TWIN_COVER or coverage(p, t2) >= TWIN_COVER
               for p in twins):
            count("%s twin of an earlier line on its ticket" % kind)
            continue
        twins.append(t2)
        out.append((kind, subject, body, evidence, auth, sha))
    for s_, evd in unrun_rows:
        for scene, bid in sorted(decider.items()):
            if re.search(r"(?<![\w])%s(?![\w])" % re.escape(scene), s_) and "bar:" + bid not in live_bars:
                live_bars.add("bar:" + bid)
                cmd = (tests.get(scene) or {}).get("command") if isinstance(tests.get(scene), dict) else None
                out.append(("live.run", "bar:" + bid, {
                    "result": "UNRUN", "bar": bid, "command": fit("%s · scene %s" % (cmd or "?", scene), S["command"]),
                    "text": fit("%s UNRUN, as its ticket records it" % scene, S["text"])}, evd, None, None))
                count("UNRUN scene named by a ticket made its bar's live.run UNRUN")
    if counts:
        notes.append("judge rules (round 2): " + "; ".join("%d %s" % (n, w) for w, n in sorted(counts.items())))
    return out


_PIPE_FILES = None


def pipe_trap(text, where):
    """True when a trap names a pipeline file (a module of src/RimMandrake/rimflow/, or that folder) in its text or
    its `where`: a defect of the pipeline's own reader, not of the mod (the round-4 judge, FW 661: 'Fixed in
    maturation.py')."""
    global _PIPE_FILES
    if _PIPE_FILES is None:
        _PIPE_FILES = {f for f in os.listdir(HERE) if f.endswith(".py") and not f.startswith(("selftest_", "__"))}
    blob = "%s %s" % (text or "", where or "")
    return "rimflow/" in blob or any(os.path.basename(m) in _PIPE_FILES for m in re.findall(r"[\w./-]+\.py\b", blob))


def _bare(body):
    """A body as its facts: without the writer's own stamps."""
    return {k: v for k, v in (body or {}).items() if k not in ("by", "ts", "new_subject_why")}


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
        kpr = R.read_tickets(readings_path(root, mod), RECORDS_KEEP.get(mod, {}), [], max(0.0, bud - reader[
            "spent_usd"] - owr["spent_usd"]), cfg.get("model", "sonnet"), cfg.get("workers", 4), log, field="keep",
            system=R.KEEP_SYSTEM)
        ev, notes2 = plan(root, mod)
        cur = R.read_tickets(readings_path(root, mod), RECORDS_CURRENT.get(mod, {}), [], max(0.0, bud - reader[
            "spent_usd"] - owr["spent_usd"] - kpr["spent_usd"]), cfg.get("model", "sonnet"), cfg.get("workers", 4), log,
            field="current", system=R.CURRENT_SYSTEM)
        ev, notes2 = plan(root, mod)
        notes = notes2 + notes[-1:] + ["currency reader: %d of %d tickets read in %d batches, $%.2f spent, %d failed, "
                                       "%d skipped for the bound" % (cur["read"], cur["asked"], cur["batches"],
                                                                     cur["spent_usd"], len(cur["failed"]),
                                                                     cur["skipped_for_budget"])] + ["keep reader: %d of %d tickets read in %d batches, $%.2f spent, %d failed, "
                                       "%d skipped for the bound" % (kpr["read"], kpr["asked"], kpr["batches"],
                                                                     kpr["spent_usd"], len(kpr["failed"]),
                                                                     kpr["skipped_for_budget"])] + ["owner reader: %d of %d tickets read in %d batches, $%.2f spent, %d failed, "
                                       "%d skipped for the bound" % (owr["read"], owr["asked"], owr["batches"],
                                                                     owr["spent_usd"], len(owr["failed"]),
                                                                     owr["skipped_for_budget"])]
    have_r = load_readings(root, mod)
    stale = sum(1 for n, t in RECORDS.get(mod, {}).items() if (have_r.get(n) or {}).get("hash") not in (None,
                                                                                         R.rec_hash(t)))
    unread = sum(1 for n in RECORDS.get(mod, {}) if n not in have_r)
    notes.append("readings: %d tickets unread (mined by the sentence rules), %d read from an older record (re-read "
                 "with --read)" % (unread, stale))
    if dry:
        return {"planned": len(ev), "written": 0, "already": 0, "deleted": 0, "refused": [], "near_duplicates": [],
                "notes": notes}
    version = next((b.get("version") for k, s, b, *_ in ev if k == "version.open"), None)
    written = already = 0
    refused, near, held, seq = [], [], set(), {}
    replaced = 0
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
                    olde = next((e for e in M.read(root, mod) if e.get("id") == same.group(1)), None) if same else None
                    if same and olde is not None and _bare(olde.get("body")) != _bare(body):
                        # rule 5: an earlier mining's line whose words this re-mine changed (a '[…]' cut, a
                        # boilerplate text) is replaced, never held beside the fact it restates
                        M.delete(root, mod, [olde["id"]])
                        try:
                            eid, created = M.append(root, mod, W, kind, subject, body=body, version=version,
                                                    evidence=evidence, authority=auth, code_sha=sha, views=False)
                            replaced += 1
                        except M.Refusal as r3:
                            refused.append((kind, subject, str(r3)))
                            continue
                    elif same:              # an older mine holds the same fact under other evidence: keep that line
                        held.add(same.group(1))           # (and keep it in its subject's plan order below)
                        seq.setdefault(subject, []).append((idx, same.group(1), False, body, auth))
                        already += 1
                        continue
                    else:
                        refused.append((kind, subject, str(r2)))
                        continue
            else:
                refused.append((kind, subject, str(r)))
                continue
        held.add(eid)
        seq.setdefault(subject, []).append((idx, eid, created, body, auth))
        written += created
        already += not created
    # a subject's events must stay in plan order (the reducer reads the last): from the first line that sits in the
    # shard after a line the plan puts later (a kept line behind one written now, or a kept pair an earlier run left
    # out of order), every line of the subject is re-appended in plan order, written-now ones included (else a line
    # written now stays in front of the kept lines re-appended after it: ExplosiveKnockback's stage read
    # offline_build over its stage.enter in_game, 2026-11-16)
    pos = {e.get("id"): i for i, e in enumerate(M.read(root, mod)) if e.get("_shard") == W}
    redo = []
    for subject, xs in seq.items():
        p = [pos.get(x[1], -1) for x in xs]
        j = next((i for i in range(len(p)) if any(q < p[i] for q in p[i + 1:])), None)
        if j is not None:
            redo += xs[j:]
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
            if not _c:
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
    # a kept cause whose finding line was just re-written now sits before its finding (lint REFUSED finding): it is
    # re-appended after it under a fresh key (Gimme Some Slack, 2026-11-16)
    orphan = [ln for c, pth, ln, d in M.lint(root, mod, None)[0] if c == "STANDARD" and
              pth.endswith("/%s.jsonl" % W) and "REFUSED finding: " in d]
    if orphan:
        with open(M.shard_path(root, mod, W), encoding="utf-8") as fh:
            raw = fh.read().split("\n")
        ids = {json.loads(raw[ln - 1]).get("id") for ln in orphan if 0 < ln <= len(raw) and raw[ln - 1].strip()}
        shard = [e for e in M.read(root, mod) if e.get("_shard") == W]
        # each orphan moves with every later line of its subject, so the subject keeps its order
        first = {}
        for i, e in enumerate(shard):
            if e.get("id") in ids:
                first.setdefault(e["subject"], i)
        lines = [e for i, e in enumerate(shard) if e["subject"] in first and i >= first[e["subject"]]]
        M.delete(root, mod, [e["id"] for e in lines])
        for e in lines:
            rkey = hashlib.sha256(("%s\0after its finding" % e["id"]).encode()).hexdigest()[:16]
            body = {k: v for k, v in e["body"].items() if k not in ("by", "ts", "new_subject_why")}
            try:
                M.append(root, mod, W, e["kind"], e["subject"], body=body, version=e.get("version"),
                         evidence=e.get("evidence") or [], authority=e.get("authority"), code_sha=e.get("code_sha"),
                         views=False, key=rkey)
            except M.Refusal as r:
                refused.append((e["kind"], e["subject"], str(r)))
    M.write_views(root, mod)
    if replaced:
        notes.append("%d lines of an earlier mining restating a fact in other words were replaced by the re-mine's"
                     % replaced)
    return {"planned": len(ev), "written": written, "already": already, "deleted": len(old), "refused": refused,
            "near_duplicates": near, "notes": notes, "replaced": replaced}


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


def sync_bars(root, mod, views=True):
    """Bring the mod ledger's bars level with version/locked_bars.json, the record `maturation.py lock-bars` writes
    (RIMMANDRAKE_REPAIR_KNOCKBACK_LEDGER_READINESS_STOPS_TICK_HOLDER: Explosive Knockback 0.2.0's lock recorded 73 ids
    and its ledger still read 0.1.0's 59). A BACKFILL bar.locked for each locked id the ledger lacks, a bar.deferred
    for each ledger bar the record does not lock; each cites locked_bars.json and names the record it came from.
    -> None for a mod with no ledger; {"ok": False, "why"} with nothing written when locked_bars.json cannot be read
    or records another version than the ledger's; else {"ok", "version", "locked": [ids], "deferred": [ids], "why"},
    ok False when the ledger is still not level after the writes (said, never assumed)."""
    evs = M.read(root, mod)
    if not evs:
        return None
    vdir = os.path.join(root, "design", "concepts", mod, "version")
    lbp = os.path.join(vdir, "locked_bars.json")
    rel = _rel(root, lbp)
    lb = _load(lbp)
    if not isinstance(lb, dict) or not isinstance(lb.get("ids"), list):
        return {"ok": False, "why": "%s could not be read as a lock record (no ids list): the ledger's bars are left "
                "as they are" % rel}
    st = M.reduce(evs)
    if lb.get("version") != st["version"]:
        return {"ok": False, "why": "%s records version %r and the mod ledger reads %r: nothing written (a lock of "
                "another version is no record of this one's bars)" % (rel, lb.get("version"), st["version"])}
    ids = list(dict.fromkeys(i for i in lb["ids"] if isinstance(i, str) and i))
    hist = [h for h in lb.get("history") or [] if isinstance(h, dict)]
    rec = "record %d%s" % (len(hist), " of %s" % hist[-1]["at"] if hist and hist[-1].get("at") else "")
    tt = _load(os.path.join(vdir, "test_table.json"))
    unread = [] if isinstance(tt, dict) else ["version/test_table.json unread: bars locked without the table's words"]
    table = {b["id"]: b for b in (tt.get("bars") if unread == [] and isinstance(tt.get("bars"), list) else [])
             if isinstance(b, dict) and b.get("id")}     # the record locks a bar; the table only words its event
    S = M.std()["caps"]
    have = {b.partition(":")[2] for b in st["bars"]}
    locked, deferred = [], []
    try:
        _sync_write(root, mod, st, ids, rel, rec, table, S, have, locked, deferred)
    finally:    # views follow every event written, also when an append refused partway
        if (locked or deferred) and views:
            M.write_views(root, mod)
    now = {b.partition(":")[2] for b in M.reduce(M.read(root, mod))["bars"]}
    level = now == set(ids)
    return {"ok": level, "version": st["version"], "locked": locked, "deferred": deferred, "notes": unread,
            "why": ("the ledger's %d bars equal %s" % (len(now), rel)) if level else (
                "the ledger still differs from %s: lacks %s, holds %s" % (
                    rel, sorted(set(ids) - now), sorted(now - set(ids))))}


def _sync_write(root, mod, st, ids, rel, rec, table, S, have, locked, deferred):
    """sync_bars' appends; appends each id it wrote to `locked` / `deferred` as it goes."""
    for bid in ids:
        if bid in have:
            continue
        b = table.get(bid, {})
        what = ", ".join(x for x in ("%s bar" % b["kind"] if b.get("kind") else "", "from %s" % b["source"]
                                     if b.get("source") else "", "proves at stage %s" % b["proves_at"]
                                     if b.get("proves_at") else "") if x)
        body = {"text": fit("locked for %s in version/locked_bars.json (%s)%s" % (
            st["version"], rec, ": " + what if what else ""), S["text"])}
        if b.get("decides"):
            body["decides"] = fit("; ".join(b["decides"]), S["decides"])
        _, created = M.append(root, mod, W, "bar.locked", "bar:" + bid, body=body, version=st["version"],
                              evidence=["path:" + rel], env_writer=None, views=False)
        if created:
            locked.append(bid)
    for sb in sorted(st["bars"]):
        bid = sb.partition(":")[2]
        if bid in ids:
            continue
        body = {"text": fit("not among the %d bars version/locked_bars.json records for %s (%s): out of this "
                            "version" % (len(ids), st["version"], rec), S["text"])}
        _, created = M.append(root, mod, W, "bar.deferred", sb, body=body, version=st["version"],
                              evidence=["path:" + rel], env_writer=None, views=False)
        if created:
            deferred.append(bid)


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
    sb = sub.add_parser("bars", help="bring the ledger's bars level with version/locked_bars.json (sync_bars)")
    sb.add_argument("--mod", required=True)
    o = ap.parse_args(argv)
    root = o.root or M.default_root()
    if o.verb == "bars":
        try:
            r = sync_bars(root, o.mod)
        except (M.ModLedgerError, M.Refusal) as e:
            print("bars %s: the mod ledger refused an event (%s: %s); views follow what was written"
                  % (o.mod, type(e).__name__, e))
            return 1
        if r is None:
            print("bars %s: no mod ledger" % o.mod)
            return 2
        print("bars %s: %s; locked %s; deferred %s" % (o.mod, r["why"], r.get("locked") or "none",
                                                        r.get("deferred") or "none"))
        return 0 if r["ok"] else 1
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
