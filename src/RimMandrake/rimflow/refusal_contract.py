#!/usr/bin/env python3
"""refusal_contract.py - the refusal contract for judges and gates (spec
design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md; item RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS).

A refusal that names no way to pass, or that repeats on the same evidence, is a loop that spends and fixes nothing: the
ExplosiveKnockback coverage judge said not_covered nine times in three hours (~90M tokens against a 4M cap), with 15 of its
50 gap ids first named after round 1. This module holds the contract's one alarm:

  REFUSAL_NOTHING_COULD_EVER_PASS   one fixed id, routed to the Conductor (alarm_routes.json). One row per subject (an
                                    item, a concept, a judge family) in alarms.json; a repeat trip updates that row and
                                    tells nobody again; a release closes it, and the next trip after a release tells again.
                                    Never a new queue item per trip.

and the contract's record (spec section 1). A verdict is one JSON object:

  {"item": ID, "family": <judge brief or gate clause set>, "sha": SHA,
   "given": {"inputs": [ref, ...] or {ref: text}, "criteria": {clause_id: clause_text}, "root": dir?},
   "passed": [{"clause": id, "evidence": [ref, ...]}, ...],
   "refusals": [{"clause", "criterion_hash", "evidence": [ref[:line[-line]], ...], "observed", "would_pass",
                 "smallest_fix": {"what", "attainable": yes|no, "cost": edit|rerun|new instrument|owner},
                 "criterion_verdict": sound|flawed|unattainable, "criterion_why", "new_since"}, ...]}

`given` is written by the launcher, never the judge (it may also come from --given). `check` refuses a malformed verdict;
it never counts against the item. `submit` checks, stores every record whole (refusals.jsonl, a pointer per repeat key),
answers a repeat (same item, clause, criterion hash, evidence content and sha) from the cache uncounted, and counts:

  the 3rd refusal of one clause on one item      -> repair_due (the neutral fixer, T5) and the item's alarm row
  the 4th refused verdict on one item            -> the item's alarm row; may_judge(item) reads False until it is cleared
                                                    (no production caller asks may_judge: the alarm TELLS, it blocks
                                                    nothing; maturation_advance is pinned alarm-only, FAMILY_TUNING)
  a 2nd malformed verdict from one brief         -> the family's alarm row (brief FAILED)
  a family refusing >70% of its last 20, or all of its last 8 across >=3 items -> the family's alarm row

    python3 src/RimMandrake/rimflow/refusal_contract.py check <verdict.json> [--given <given.json>]   errors, exit 1
    python3 src/RimMandrake/rimflow/refusal_contract.py submit <verdict.json> [--given <given.json>]  the result JSON
                                    (a judge's file whose verdict is its `contract` block is read as that block)
    python3 src/RimMandrake/rimflow/refusal_contract.py counters [<item>]                            the counts
    python3 src/RimMandrake/rimflow/refusal_contract.py alarms          the open alarm rows, one line each
    python3 src/RimMandrake/rimflow/refusal_contract.py diffguard <old.json> <new.json> [--bars a,b] [--card R]
                                    [--second-read R]   classify a criteria change {clause: text}; exit 1 if refused
    python3 src/RimMandrake/rimflow/refusal_contract.py calibrate [--no-run | --model <family>]   the judge calibration
                                    registry (infrastructure/state/judge_calibration.json): an edited brief resets to
                                    UNTESTED (a .py docstring or comment is not brief text: brief_text.py),
                                    free deterministic checks run (--model runs a family's model_check, which
                                    spends); a check must show every planted case ran and came out as planted, both
                                    ways (a row's `tolerate` and `abstain`, each set by a named ruling, bend this:
                                    judge_cases). Only a CALIBRATED brief's verdict, either way, has a consequence.
                                    --no-run is a read-only status (writes nothing) and flags signatures made under an unproven brief
    python3 src/RimMandrake/rimflow/refusal_contract.py repair <case.json>   the neutral fixer (roles/criteria_fixer.md,
                                    one fresh Opus run), guarded by diffguard, recorded whole; exit 1 if refused

The rows live in RM_REFUSAL_DIR, default /mnt/d/ClaudeWork/rimmandrake/refusal_contract (a program reads them: scratch,
not the repo). The told row goes through incident.signal when dispatcher_schedule.json has the incident ledger on.
"""
import effort as EF  # the one effort table (RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM)
import fcntl
import hashlib
import json
import os
import re
import sys
import time
from contextlib import contextmanager

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brief_text  # noqa: E402

ALARM_ID = "REFUSAL_NOTHING_COULD_EVER_PASS"
REAL_DIR = "/mnt/d/ClaudeWork/rimmandrake/refusal_contract"
SCHEDULE = os.path.join(HERE, "dispatcher_schedule.json")


def state_dir():
    return os.environ.get("RM_REFUSAL_DIR") or REAL_DIR


def alarms_path():
    return os.path.join(state_dir(), "alarms.json")


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict):
        raise ValueError("%s is not a JSON object" % path)
    return data


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def _told(why, now):
    """-> None when told (or the incident ledger is off), else why the told row could not be written."""
    try:
        import incident
        with open(SCHEDULE, encoding="utf-8") as f:
            sch = json.load(f)
        # A process that moved the rows (a selftest) moves their told row too, unless it named its own ops folder:
        # selftest_control set RM_REFUSAL_DIR alone and paged the Conductor from a temp dir (refusals-20261119145232).
        moved = state_dir() != REAL_DIR and not os.environ.get("RM_OPS_WATCH_DIR")
        if moved:
            os.makedirs(state_dir(), exist_ok=True)
        incident.signal(sch, ALARM_ID, why, now, path=os.path.join(state_dir(), "told.jsonl") if moved else None)
        return None
    except Exception as e:  # noqa: BLE001 - the row on disk stands; the failure to tell is written into it
        return "%s: %s" % (type(e).__name__, str(e))


def alarm(subject, why, now=None, family=None, detail=None):
    """Raise or update the one alarm for `subject`. -> the row. The first trip of an open row tells the Conductor;
    a repeat only updates trips, last_at and why."""
    now = time.time() if now is None else now
    path = alarms_path()
    rows = _read(path)
    row = rows.get(subject)
    fresh = not (isinstance(row, dict) and row.get("open"))
    if fresh:
        was = row if isinstance(row, dict) else {}      # a released row keeps its trips and releases
        row = {"id": ALARM_ID, "subject": subject, "first_at": iso(now), "trips": int(was.get("trips") or 0), "open": True}
        if was.get("releases"):
            row["releases"] = was["releases"]
    row.update(last_at=iso(now), why=str(why), trips=int(row.get("trips") or 0) + 1)
    if family:
        row["family"] = family
    if detail is not None:
        row["detail"] = detail
    if fresh:
        err = _told("%s: %s" % (subject, why), now)
        row["told_at"] = iso(now)
        if err:
            row["told_error"] = err
        else:
            row.pop("told_error", None)
    rows[subject] = row
    _write(path, rows)
    return row


def clear(subject, why, now=None, by=None):
    """A release: the row closes (kept, with its history), so the next trip tells again. -> the row or None."""
    now = time.time() if now is None else now
    path = alarms_path()
    rows = _read(path)
    row = rows.get(subject)
    if not isinstance(row, dict):
        return None
    row.update(open=False)
    rel = {"at": iso(now), "why": str(why)}
    if by:
        rel["by"] = str(by)
    row.setdefault("releases", []).append(rel)
    rows[subject] = row
    _write(path, rows)
    return row


def open_alarms():
    return [r for r in _read(alarms_path()).values() if isinstance(r, dict) and r.get("open")]


# ---- the record (spec section 1) ------------------------------------------------------------------------------

FIELDS = ("clause", "criterion_hash", "evidence", "observed", "would_pass", "smallest_fix", "criterion_verdict",
          "criterion_why")
VERDICTS = ("sound", "flawed", "unattainable")
COSTS = ("edit", "rerun", "new instrument", "owner")
NEW_SINCE = ("unfixed", "changed", "regression")       # each as "<tag>:<what>"; or the bare "late"
# Phrases that say a thing failed without saying what would pass. A would_pass/smallest_fix left with fewer than
# MIN_WORDS content words once these and the stopwords are struck is empty.
EMPTY = ("does not pass", "doesn't pass", "not passing", "insufficient", "needs more work", "needs work", "weak",
         "not convincing", "unconvincing", "not good enough", "inadequate", "make it better", "improve it", "fix it",
         "do better", "try again", "unclear", "not sufficient", "more detail", "more evidence", "be more")
STOP = set("a an the it this that these those is are be been was were to of in on for with and or as at by from so "
           "its it's should must needs need more better do does not no yes".split())
MIN_WORDS = 3
CLAUSE_REPAIR_AT = 3        # the 3rd refusal of one clause on one item (spec section 3)
ITEM_ALARM_AT = 4           # the 4th refused verdict on one item
MALFORMED_ALARM_AT = 2      # a 2nd malformed verdict from one brief on one item
FAMILY_WINDOW, FAMILY_RATE = 20, 0.70
FAMILY_ALL_WINDOW, FAMILY_ALL_ITEMS = 8, 3
FAMILY_KEEP = 50
# RIMMANDRAKE_TUNE_ADVANCE_REFUSAL_ALARM_BLOCKS_NOTHING_AS_CODED (owner 2026-11-18: "If we just implemented 'a change I
# can veto' where it would be stopping currently known needed work, then the rule we just implemented isn't useful.
# Please assess how it should actually be tuned given what we know"): a family here counts its item and clause alarms
# within a rolling window, not for the item's life, and never counts a clause whose fix is a hand step waiting on a
# person. The family limits are unchanged. maturation_advance is ALARM-ONLY: maturation.py advance never asks
# may_judge, so a trip tells the Conductor and stops no advance.
FAMILY_TUNING = {"maturation_advance": {"window_s": 86400,
                                        "uncounted": ("owner_said", "steward_confirms", "conductor_decision")}}
LINE_RE = re.compile(r"^(?P<ref>.+?):(?P<a>\d+)(?:-(?P<b>\d+))?$")
WORD_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.'-]*")


def criterion_hash(text):
    return hashlib.sha256(" ".join(str(text).split()).encode("utf-8")).hexdigest()[:16]


def _words(text):
    return [w.lower().strip(".'-") for w in WORD_RE.findall(str(text or ""))]


def _content(text):
    t = " %s " % " ".join(_words(text))
    for p in sorted(EMPTY, key=len, reverse=True):
        t = t.replace(" %s " % p, " ")
    return [w for w in t.split() if w and w not in STOP]


def _inputs(given):
    """-> {ref: text or None} from given.inputs (a list of refs or a {ref: text} map)."""
    inp = (given or {}).get("inputs") or {}
    if isinstance(inp, list):
        return {str(r): None for r in inp}
    return {str(k): v for k, v in inp.items()}


def _split(ev):
    """'path:12-14' -> ('path', 12, 14); 'path' -> ('path', None, None)."""
    m = LINE_RE.match(ev)
    if not m:
        return ev, None, None
    a = int(m.group("a"))
    return m.group("ref"), a, int(m.group("b") or a)


def _text_of(ref, given):
    """The text of a given input: its value in given.inputs, else the file under given.root. None if neither."""
    txt = _inputs(given).get(ref)
    if txt is not None:
        return str(txt)
    path = ref if os.path.isabs(ref) else os.path.join((given or {}).get("root") or os.getcwd(), ref)
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError:
        return None
    if b"\0" in raw[:8192]:   # cut-ok: sample bytes to detect binary evidence, which is checked by ref alone
        return None           # (RIMMANDRAKE_TEACH_CONTRACT_CHECK_PICTURES_ARE_NOT_TEXT)
    return raw.decode("utf-8", errors="replace")


def _evidence(rec):
    ev = rec.get("evidence")
    if isinstance(ev, str):
        return [ev]
    return [str(e) for e in ev] if isinstance(ev, list) else []


def _passed(verdict):
    out = []
    for p in verdict.get("passed") or []:
        out.append({"clause": str(p), "evidence": []} if isinstance(p, str) else
                   {"clause": str(p.get("clause")), "evidence": _evidence(p)})
    return out


OBSERVED_SHARED = 2   # observed must share this many distinct content words (3+ letters) with its evidence lines


def _ev_texts(where, evs, inputs, given, errs, seen_ev):
    """Check each evidence ref (an input, its lines inside the file) -> the cited texts. Refusals and passes alike."""
    texts = []
    for ev in evs:
        ref, a, b = _split(ev)
        if ref not in inputs and ev in inputs:
            ref, a, b = ev, None, None
        if ref not in inputs:
            errs.append("%s: evidence %r is not one of the inputs the judge was given" % (where, ev))
            continue
        seen_ev.add(ref)
        txt = _text_of(ref, given)
        if txt is None:
            continue
        if a is not None:
            lines = txt.splitlines()
            if not 1 <= a <= b <= len(lines):
                errs.append("%s: evidence %r names lines outside %s (%d lines)" % (where, ev, ref, len(lines)))
                continue
            txt = "\n".join(lines[a - 1:b])
        texts.append(txt)
    return texts


def check(verdict, given=None, prior=0):
    """-> the list of reasons `verdict` is malformed (empty = well formed). Pure: reads only the given inputs.
    `prior` is the item's earlier counted refusals: after the first, every refusal must say what is new since."""
    if not isinstance(verdict, dict):
        return ["the verdict is not a JSON object"]
    given = given if given is not None else verdict.get("given")
    errs = []
    for k in ("item", "family", "sha"):
        if not str(verdict.get(k) or "").strip():
            errs.append("verdict: no %s" % k)
    if not isinstance(given, dict) or not given.get("criteria") or not given.get("inputs"):
        return errs + ["verdict: no given criteria and inputs to check it against (the launcher writes `given`)"]
    if str(given.get("sha") or "").strip() and str(verdict.get("sha") or "") != str(given["sha"]):
        # RIMMANDRAKE_CHECK_PASSED_CONTRACT_EVIDENCE: the verdict judges the sha the launcher gave, no other
        errs.append("verdict: sha %r is not the given sha %r" % (verdict.get("sha"), given["sha"]))
    crit = {str(k): v for k, v in given["criteria"].items()}
    inputs = _inputs(given)
    refs = verdict.get("refusals")
    if not isinstance(refs, list):
        return errs + ["verdict: refusals is not a list"]
    seen_ev, clauses = set(), {}
    for i, rec in enumerate(refs):
        where = "refusal %d" % i
        if not isinstance(rec, dict):
            errs.append("%s: not an object" % where)
            continue
        c = str(rec.get("clause") or "")
        where = "refusal %d (%s)" % (i, c or "no clause")
        for f in FIELDS:
            v = rec.get(f)
            if v is None or (isinstance(v, (str, list, dict)) and not (v.strip() if isinstance(v, str) else v)):
                errs.append("%s: %s is missing or empty" % (where, f))
        if c:
            clauses[c] = clauses.get(c, 0) + 1
            if c not in crit:
                errs.append("%s: clause is not in the criterion set" % where)
            elif rec.get("criterion_hash") and rec["criterion_hash"] != criterion_hash(crit[c]):
                errs.append("%s: criterion_hash %s is not the hash of the clause's text (%s)"
                            % (where, rec["criterion_hash"], criterion_hash(crit[c])))
        texts = _ev_texts(where, _evidence(rec), inputs, given, errs, seen_ev)
        if texts and rec.get("observed"):
            have = set(_words(" ".join(texts)))
            shared = {w for w in _words(rec["observed"]) if len(w) >= 3 and w not in STOP and w in have}
            if len(shared) < OBSERVED_SHARED:
                errs.append("%s: observed quotes %s of its evidence (%d distinct words shared, %d needed)" % (
                    where, "no token" if not shared else "too little", len(shared), OBSERVED_SHARED))
        if rec.get("would_pass") and len(_content(rec["would_pass"])) < MIN_WORDS:
            errs.append("%s: would_pass says nothing checkable (%r)" % (where, rec["would_pass"]))
        elif c in crit and rec.get("would_pass"):
            extra = set(_content(rec["would_pass"])) - set(_content(crit[c]))
            if not extra:
                errs.append("%s: would_pass restates the clause" % where)
        fix = rec.get("smallest_fix")
        if fix is not None and not isinstance(fix, dict):
            errs.append("%s: smallest_fix is not an object {what, attainable, cost}" % where)
        elif isinstance(fix, dict):
            if len(_content(fix.get("what"))) < MIN_WORDS:
                errs.append("%s: smallest_fix.what names no change (%r)" % (where, fix.get("what")))
            if fix.get("attainable") not in ("yes", "no"):
                errs.append("%s: smallest_fix.attainable is not yes/no" % where)
            if fix.get("cost") not in COSTS:
                errs.append("%s: smallest_fix.cost is not one of %s" % (where, "/".join(COSTS)))
        if rec.get("criterion_verdict") and rec["criterion_verdict"] not in VERDICTS:
            errs.append("%s: criterion_verdict is not one of %s" % (where, "/".join(VERDICTS)))
        if rec.get("criterion_why") and len(_words(rec["criterion_why"])) < 4:
            errs.append("%s: criterion_why is not a sentence" % where)
        ns = str(rec.get("new_since") or "")
        if prior and not ns:
            errs.append("%s: new_since is required after the item's first refusal" % where)
        elif prior and ns == "first":
            errs.append("%s: new_since 'first' after the item's first refusal (%d counted before)" % (where, prior))
        elif ns and ns not in ("first", "late") and not (ns.split(":", 1)[0] in NEW_SINCE and ns.split(":", 1)[1:]
                                                         and ns.split(":", 1)[1].strip()):
            errs.append("%s: new_since %r is not unfixed:<clause>, changed:<input>, regression:<clause> or late"
                        % (where, ns))
    passed = _passed(verdict)
    for p in passed:
        if p["clause"] not in crit:
            errs.append("passed: %r is not in the criterion set" % p["clause"])
        # RIMMANDRAKE_CHECK_PASSED_CONTRACT_EVIDENCE: a pass's evidence is checked as a refusal's is (lines in bounds)
        _ev_texts("passed %s" % p["clause"], p["evidence"], inputs, given, errs, seen_ev)
    both = sorted(set(clauses) & {p["clause"] for p in passed})
    if both:
        errs.append("clauses both passed and refused: %s" % ", ".join(both))
    dup = sorted(c for c, n in clauses.items() if n > 1)
    if dup:
        errs.append("one record per clause; repeated: %s" % ", ".join(dup))
    unjudged = sorted(set(crit) - set(clauses) - {p["clause"] for p in passed})
    if unjudged:
        errs.append("coverage: clauses neither passed nor refused: %s" % ", ".join(unjudged))
    unread = sorted(set(inputs) - seen_ev)
    if unread:
        errs.append("coverage: given inputs in no passed or refused evidence: %s" % ", ".join(unread))
    return errs


# ---- the store: whole records, the repeat cache, the counters ----------------------------------------------------

def records_path():
    return os.path.join(state_dir(), "refusals.jsonl")


def counters_path():
    return os.path.join(state_dir(), "counters.json")


@contextmanager
def _locked():
    os.makedirs(state_dir(), exist_ok=True)
    with open(os.path.join(state_dir(), ".lock"), "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def evidence_hash(rec, given):
    """The hash of what the record's evidence holds now: each ref with its text (or the ref alone if it has none)."""
    h = hashlib.sha256()
    for ev in sorted(_evidence(rec)):
        ref, a, b = _split(ev)
        if ref not in _inputs(given):
            ref = ev
        txt = _text_of(ref, given)
        h.update(("%s\0%s\0" % (ev, "" if txt is None else hashlib.sha256(txt.encode("utf-8")).hexdigest()))
                 .encode("utf-8"))
    return h.hexdigest()[:16]


def repeat_key(item, rec, given, sha):
    raw = "\0".join([str(item), str(rec.get("clause")), str(rec.get("criterion_hash")), evidence_hash(rec, given),
                     str(sha)])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _store(row):
    """Append one whole row to refusals.jsonl. -> its pointer 'refusals.jsonl:<line>'."""
    path = records_path()
    n = 0
    if os.path.exists(path):
        with open(path, "rb") as f:
            n = sum(1 for _ in f)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    return "%s:%d" % (os.path.basename(path), n + 1)


def _row_at(pointer):
    name, line = pointer.rsplit(":", 1)
    with open(os.path.join(state_dir(), name), encoding="utf-8") as f:
        for i, x in enumerate(f, 1):
            if i == int(line):
                return json.loads(x)
    return None


def counters():
    c = _read(counters_path())
    for k in ("items", "families", "cache"):
        c.setdefault(k, {})
    return c


def _item(c, item):
    return c["items"].setdefault(item, {"refused": 0, "verdicts": 0, "clauses": {}, "malformed": {}})


def prejudge(item, sha, given):
    """Before a judge is spent: -> {clause: the stored refusal} for each clause already refused on this item at this
    sha whose criterion and evidence are unchanged. Those clauses are not judged again."""
    c = counters()
    crit = {str(k): v for k, v in (given.get("criteria") or {}).items()}
    out = {}
    for key, ent in c["cache"].items():
        if ent.get("item") != item or ent.get("sha") != sha or ent.get("clause") not in crit:
            continue
        rec = _row_at(ent["pointer"])["record"]
        if rec.get("criterion_hash") == criterion_hash(crit[ent["clause"]]) and \
                repeat_key(item, rec, given, sha) == key:
            out[ent["clause"]] = rec
    return out


def may_judge(item):
    row = _read(alarms_path()).get("item:%s" % item)
    return not (isinstance(row, dict) and row.get("open"))


def _family_trip(hist):
    last = hist[-FAMILY_WINDOW:]
    if len(last) >= FAMILY_WINDOW:
        share = sum(1 for h in last if h["refused"]) / float(len(last))
        if share > FAMILY_RATE:
            return "refused %d of its last %d verdicts (limit %d%%)" % (
                sum(1 for h in last if h["refused"]), len(last), int(FAMILY_RATE * 100))
    tail = hist[-FAMILY_ALL_WINDOW:]
    if len(tail) >= FAMILY_ALL_WINDOW and all(h["refused"] for h in tail) and \
            len({h["item"] for h in tail}) >= FAMILY_ALL_ITEMS:
        return "refused all of its last %d verdicts across %d items" % (len(tail), len({h["item"] for h in tail}))
    return None


def submit(verdict, given=None, now=None):
    """Check, store and count one verdict. -> {ok, errors, counted, cached, repair_due, alarms, may_judge}."""
    now = time.time() if now is None else now
    given = given if given is not None else (verdict or {}).get("given")
    item, fam = str((verdict or {}).get("item") or ""), str((verdict or {}).get("family") or "")
    res = {"ok": False, "errors": [], "counted": False, "cached": [], "repair_due": [], "alarms": []}
    res["calibration"] = status(fam)
    res["advisory"] = adv = res["calibration"] != "CALIBRATED"
    with _locked():
        c = counters()
        it = _item(c, item) if item else {"refused": 0}
        res["errors"] = check(verdict, given, prior=it["refused"])
        stored = {"at": iso(now), "item": item, "family": fam, "sha": (verdict or {}).get("sha")}
        if res["errors"]:
            stored.update(kind="malformed", errors=res["errors"], verdict=verdict)
            res["pointer"] = _store(stored)
            if item and fam:
                it["malformed"][fam] = it["malformed"].get(fam, 0) + 1
                if it["malformed"][fam] >= MALFORMED_ALARM_AT:
                    _write(counters_path(), c)
                    res["alarms"].append(alarm("family:%s" % fam, "brief FAILED: %d malformed verdicts in a row on %s"
                                               % (it["malformed"][fam], item), now, family=fam,
                                               detail={"item": item, "errors": res["errors"]}))
                _write(counters_path(), c)
            res["may_judge"] = may_judge(item) if item else False
            return res
        res["ok"] = True
        it["malformed"].pop(fam, None)
        sha, fresh = verdict["sha"], []
        for rec in verdict["refusals"]:
            key = repeat_key(item, rec, given, sha)
            if key in c["cache"]:
                res["cached"].append(rec["clause"])
                continue
            ptr = _store(dict(stored, kind="refusal", key=key, record=rec))
            c["cache"][key] = {"item": item, "clause": rec["clause"], "sha": sha, "pointer": ptr, "at": iso(now)}
            fresh.append(rec)
        if adv and fresh:
            # RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS: an uncalibrated brief's refusal is stored and shown only; it is
            # not counted, so it raises no repair and no alarm
            _write(counters_path(), c)
            res["may_judge"] = may_judge(item)
            return res
        if not verdict["refusals"]:
            res["pointer"] = _store(dict(stored, kind="pass", verdict=verdict, given=given))   # an all-pass, kept whole
        if fresh or not verdict["refusals"]:
            res["counted"] = True
            it["verdicts"] += 1
            tune = FAMILY_TUNING.get(fam)
            alarming = [r for r in fresh if not tune or r["clause"] not in tune["uncounted"]]
            refused = bool(alarming)
            if fresh:
                it["refused"] += 1      # the life count stays: tag_new_since and check read it
            for rec in fresh:
                it["clauses"][rec["clause"]] = it["clauses"].get(rec["clause"], 0) + 1
            if tune:
                hist_at = [h for h in it.get("refused_at") or [] if now - float(h.get("at") or 0) < tune["window_s"]]
                if alarming:
                    hist_at.append({"at": now, "clauses": [r["clause"] for r in alarming]})
                it["refused_at"] = hist_at
                n_refused = len(hist_at)
                n_clause = {}
                for h in hist_at:
                    for cl in h["clauses"]:
                        n_clause[cl] = n_clause.get(cl, 0) + 1
            else:
                n_refused, n_clause = it["refused"], it["clauses"]
            for rec in alarming:
                if n_clause.get(rec["clause"], 0) >= CLAUSE_REPAIR_AT:
                    res["repair_due"].append(rec["clause"])
            hist = c["families"].setdefault(fam, [])
            hist.append({"item": item, "refused": bool(fresh), "at": iso(now)})   # family limits: unchanged
            del hist[:-FAMILY_KEEP]
            _write(counters_path(), c)
            why = []
            most = ITEM_ALARM_AT
            import pipeline_control as PC      # the item's account: `pipe set|add|reset|limit <Mod> refusals ...`
            try:
                n_refused, most = PC.used(item, "refusals", n_refused), PC.limit(item, "refusals", ITEM_ALARM_AT)
            except PC.Unreadable as e:  # the alarm tells and blocks nothing: the raw count still tells, said so
                res["control"] = "UNMEASURED: the control store cannot be read (%s); the raw count was used" % e
            if refused and n_refused >= most:
                why.append("%d refused verdicts%s (limit %d)" % (
                    n_refused, " in %d h" % (tune["window_s"] // 3600) if tune else "", most))
            if res["repair_due"]:
                why.append("clause %s refused %d times: criteria repair due" % (
                    ", ".join(res["repair_due"]), CLAUSE_REPAIR_AT))
            if why:
                res["alarms"].append(alarm("item:%s" % item, "; ".join(why), now, family=fam,
                                           detail={"clauses": it["clauses"], "repair_due": res["repair_due"]}))
            trip = _family_trip(hist) if fresh else None
            if trip:
                res["alarms"].append(alarm("family:%s" % fam, trip, now, family=fam))
        _write(counters_path(), c)
    res["may_judge"] = may_judge(item)
    return res


# ---- judge calibration (T6, spec section 5) -----------------------------------------------------------------------

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CALIBRATION_REL = "infrastructure/state/judge_calibration.json"
CAL_STATUS = ("UNTESTED", "CALIBRATED", "FAILED")


def calibration_path():
    return os.environ.get("RM_JUDGE_CALIBRATION") or os.path.join(REPO, CALIBRATION_REL)


def calibration_root():
    return os.environ.get("RM_CALIBRATION_ROOT") or REPO


def load_calibration(path=None):
    try:
        with open(path or calibration_path(), encoding="utf-8") as f:
            reg = json.load(f)
    except (OSError, ValueError):
        return {"families": {}}
    return reg if isinstance(reg, dict) and isinstance(reg.get("families"), dict) else {"families": {}}


def brief_hash(files, root=None):
    """sha256 over a brief's files (repo-relative), in order; a missing file hashes as its name: the hash still moves.
    A docstring or a comment of a .py file is not brief text and does not move it (brief_text.py)."""
    h = hashlib.sha256()
    for rel in files:
        h.update(rel.encode())
        try:
            with open(os.path.join(root or calibration_root(), rel), "rb") as f:
                h.update(brief_text.rule_bytes(rel, f.read()))
        except OSError:
            h.update(b"MISSING")
    return h.hexdigest()[:16]


def status(family):
    """-> the family's calibration status now: its recorded status if its brief is unchanged since, else UNTESTED."""
    row = load_calibration()["families"].get(family)
    if not isinstance(row, dict) or row.get("status") not in CAL_STATUS:
        return "UNTESTED"
    if row.get("hash") != brief_hash(row.get("brief") or [], calibration_root()):
        return "UNTESTED"
    return row["status"]


def advisory(family):
    """Only a CALIBRATED brief's refusal has a consequence; an UNTESTED or FAILED one is stored and shown only."""
    return status(family) != "CALIBRATED"


EXPECTS = ("pass", "refuse")
RESULTS_ENV = "RM_CALIBRATION_RESULTS"   # where a check writes {"cases": [{"id", "expect", "got"}, ...]}


def judge_cases(planted, results, tolerate=0, abstain=None):
    """-> (status, why) for one check's case results against the row's planted cases (RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS).
    `planted` is a list of {id, expect} or {"count": {"pass": n, "refuse": m}} (a corpus too big to list). CALIBRATED
    only when every planted case ran and came out as planted and the cases go both ways; a case that came out the other
    way is FAILED; a case that did not run, no results, or one-way cases leave it UNTESTED. Exit 0 alone proves nothing.
    `tolerate` (a row's field, set only by a ruling that names it; RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS:
    the Conductor's "at most 3 disagreements of 25" for set_down_judge): up to that many cases may come out the other way,
    and the why names them.
    `abstain` (a row's field, set only by a ruling that names it; RIMMANDRAKE_RULE_ART_FIRST_PASS_WEAK_IS_NO_VERDICT for
    art_eval_first_pass): {"answer": <a got word>, "decided_share": {<expect>: <0..1>}}. A case whose got is that answer
    gave no verdict: it is never wrong. Each named expect must then have at least that share of its planted cases come
    out as planted, else FAILED; an abstain with no case decided at all is FAILED."""
    cases = [c for c in (results or {}).get("cases") or [] if isinstance(c, dict)]
    skip = abstain.get("answer") if isinstance(abstain, dict) and abstain.get("answer") else None
    wrong = sorted(str(c.get("id")) for c in cases if c.get("expect") in EXPECTS and c.get("got") != c.get("expect")
                   and not (skip and c.get("got") == skip))
    if isinstance(planted, dict) and isinstance(planted.get("count"), dict):
        want = {k: int(planted["count"].get(k) or 0) for k in EXPECTS}
        ran = {k: sum(1 for c in cases if c.get("expect") == k) for k in EXPECTS}
        missing = ["%d %s case(s)" % (want[k] - ran[k], k) for k in EXPECTS if ran[k] < want[k]]
    else:
        want = {k: sum(1 for c in planted or [] if isinstance(c, dict) and c.get("expect") == k) for k in EXPECTS}
        got = {str(c.get("id")): c for c in cases}
        missing = sorted(str(c.get("id")) for c in planted or [] if isinstance(c, dict) and str(c.get("id")) not in got)
        wrong = sorted(set(wrong) | {str(c.get("id")) for c in planted or [] if isinstance(c, dict)
                                     and str(c.get("id")) in got and got[str(c["id"])].get("got") != c.get("expect")
                                     and not (skip and got[str(c["id"])].get("got") == skip)})
    tolerate = int(tolerate or 0)
    if wrong and len(wrong) > tolerate:
        return "FAILED", "came out the other way: %s" % ", ".join(wrong)
    if not all(want.values()):
        return "UNTESTED", "planted cases do not go both ways (%s)" % ", ".join("%s %d" % kv for kv in sorted(want.items()))
    if missing:
        return "UNTESTED", "did not run: %s" % ", ".join(missing)
    n = len(cases) if isinstance(planted, dict) else len({str(c.get("id")) for c in planted or [] if isinstance(c, dict)})
    if skip:
        decided = {k: sum(1 for c in cases if c.get("expect") == k and c.get("got") == k) for k in EXPECTS}
        if not any(decided.values()):
            return "FAILED", "no case decided: every answer was %r" % skip
        for k, share in sorted((abstain.get("decided_share") or {}).items()):
            if k in want and decided.get(k, 0) < float(share) * want[k]:
                return "FAILED", "%d of %d %s case(s) came out %s, under the row's decided_share %s (%r is no verdict)" % (
                    decided.get(k, 0), want[k], k, k, share, skip)
        held = sum(1 for c in cases if c.get("got") == skip)
        return "CALIBRATED", "%d of %d planted case(s) came out the other way%s; %s; %d answered %r, no verdict (row's abstain)" % (
            len(wrong), n, " (%s)" % ", ".join(wrong) if wrong else "",
            ", ".join("%d of %d %s decided" % (decided[k], want[k], k) for k in EXPECTS), held, skip)
    if wrong:
        return "CALIBRATED", "%d of %d planted case(s) came out the other way (%s), within the row's tolerate of %d" % (
            len(wrong), n, ", ".join(wrong), tolerate)
    return "CALIBRATED", "%d planted case(s) ran and came out as planted" % n   # a recorded, unplanted row is not one


def judge_row(row, results):
    """-> (status, why): judge_cases with the row's own planted cases, tolerate and abstain."""
    row = row or {}
    return judge_cases(row.get("planted"), results, row.get("tolerate") or 0, row.get("abstain"))


# budget: danger=a calibration check that never ends holds the calibration; never reached in the 14 days to 2026-11-24; no
# budget: record of its run
def run_check(cmd, root, row, timeout=600):
    """Run one calibration check with RESULTS_ENV set; judge its results by the registry row. -> (status, last_run)."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        res_path = os.path.join(tmp, "results.json")
        try:
            p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=timeout,
                               env=dict(os.environ, **{RESULTS_ENV: res_path}))
            code, out = p.returncode, (p.stdout + p.stderr).strip()
        except (OSError, subprocess.SubprocessError) as e:
            code, out = None, str(e)
        try:
            with open(res_path, encoding="utf-8") as f:
                results = json.load(f)
        except (OSError, ValueError):
            results = None
    if code != 0:
        st, why = "FAILED", "exit %s" % code
    else:
        st, why = judge_row(row, results)
    run = {"exit": code, "out": out.splitlines()[-1] if out else "", "cases": why}
    if isinstance(results, dict) and isinstance(results.get("cases"), list):
        run["results"] = results["cases"] if len(results["cases"]) <= 20 else "%d case rows" % len(results["cases"])
    return st, run


def calibrate(path=None, root=None, run_free=True, now=None, model=()):
    """Re-read every row: an edited brief resets to UNTESTED; a row with a `free_check` command (deterministic, no
    model) is run; a family named in `model` has its `model_check` run (it spends: never by default). A check sets
    its status by judge_cases over the case results it writes to $RM_CALIBRATION_RESULTS, at the current hash. Writes
    the registry back. With run_free False and no model it only reports: nothing is written (`calibrate --no-run`)."""
    path, root = path or calibration_path(), root or calibration_root()
    reg = load_calibration(path)
    at = iso(time.time() if now is None else now)
    for fam, row in reg["families"].items():
        h = brief_hash(row.get("brief") or [], root)
        if row.get("hash") != h:
            row.update(status="UNTESTED", was=row.get("status"), hash=h, reset_at=at)
        cmd = row.get("model_check") if fam in model else row.get("free_check") if run_free else None
        if cmd:
            row["status"], row["last_run"] = run_check(cmd, root, row, timeout=int(row.get("timeout_s") or 600))
            row["last_run"]["at"] = at
    if run_free or model:
        _write(path, reg)
    return reg


# ---- the neutral criteria fixer and its guard (T5, spec section 2) ------------------------------------------------

FIXER_BRIEF = os.path.join(HERE, "roles", "criteria_fixer.md")
REPAIR_CLASSES = ("tighten", "clarify", "replace", "fixture", "loosen")
LOWER = ("at least", "no fewer than", "minimum", ">=")
UPPER = ("at most", "no more than", "maximum", "within", "<=")
BOUND_RE = re.compile(r"(at least|no fewer than|minimum|at most|no more than|maximum|within|>=|<=)\s*(\d+(?:\.\d+)?)",
                      re.I)
CONTROL_WORDS = ("control", "assert", "must", "never", "each", "every", "only")
# budget: danger=a fixer call that never returns holds the repair of the criterion; longest=17s (1 CRITERIA FIXER session, agent
# budget: transcripts, 14 days to 2026-11-24)
FIXER_TIMEOUT_S = 1200


def _bounds(text):
    return [("lower" if m.group(1).lower() in LOWER else "upper", float(m.group(2)))
            for m in BOUND_RE.finditer(str(text or ""))]


def _controls(text):
    w = _words(text)
    return {c: w.count(c) for c in CONTROL_WORDS}


def classify(old, new):
    """-> (class, why) for one clause's text change, read from the text alone (the fixer's own word is not trusted)."""
    if new is None:
        return "loosen", "the clause was removed"
    if old is None:
        return "tighten", "a clause was added"
    if " ".join(str(old).split()) == " ".join(str(new).split()):
        return None, "unchanged"
    ob, nb = _bounds(old), _bounds(new)
    for k in ("lower", "upper"):
        o, n = [v for kk, v in ob if kk == k], [v for kk, v in nb if kk == k]
        if len(n) < len(o):
            return "loosen", "a %s bound was removed" % k
        for a, b in zip(o, n):
            if (k == "lower" and b < a) or (k == "upper" and b > a):
                return "loosen", "a %s bound moved from %g to %g" % (k, a, b)
    oc, nc = _controls(old), _controls(new)
    dropped = [c for c in CONTROL_WORDS if nc[c] < oc[c]]
    if dropped:
        return "loosen", "a control was dropped (%s)" % ", ".join(dropped)
    if len(nb) > len(ob) or any((k == "lower" and b > a) or (k == "upper" and b < a)
                                for (k, a), (k2, b) in zip(ob, nb) if k == k2):
        return "tighten", "a bound was added or moved toward stricter"
    if set(_content(old)) <= set(_content(new)):
        return "clarify", "wording was added; the numbers and controls are unchanged"
    return "replace", "the clause was rewritten; its numbers and controls are kept"


def diffguard(old, new, owner_bars=(), card=None, second_read=None, bad_passes=None, good_passes=None):
    """Guard a criteria repair. `old`/`new` are {clause_id: text}. -> {ok, changes: [{clause, class, why}], errors}.
    Refused: an owner bar touched (it goes to the Conductor, whatever reference is given); a loosen with no card or
    second-read reference; a repair after which the known-bad case passes or the known-good case fails."""
    changes, errs = [], []
    for c in sorted(set(old) | set(new)):
        cls, why = classify(old.get(c), new.get(c))
        if cls is None:
            continue
        changes.append({"clause": c, "class": cls, "why": why})
        if c in set(owner_bars):
            errs.append("%s is an owner bar: a change to it is his word or the Conductor's recorded act, never a repair" % c)
        elif cls == "loosen" and not (str(card or "").strip() or str(second_read or "").strip()):
            errs.append("%s: loosen (%s) with no card or second-read reference" % (c, why))
    if bad_passes:
        errs.append("the known-bad calibration case passes the repaired criteria")
    if good_passes is False:
        errs.append("the known-good calibration case fails the repaired criteria")
    return {"ok": not errs, "changes": changes, "errors": errs}


def fixer_prompt(case):
    """The fixer's packet: its brief, the clause, its source line, the refusals, the evidence and the calibration cases.
    Nothing else in `case` reaches it (no builder's arguments, no stakes, no priority)."""
    with open(FIXER_BRIEF, encoding="utf-8") as f:
        brief = f.read()
    c = case["clause"]
    text = case["criteria"][c]
    return "\n".join([brief, "", "## The clause", "%s (criterion_hash %s): %s" % (c, criterion_hash(text), text), "",
                      "## The line it serves", str(case.get("source") or "(none given: say so in why)"), "",
                      "## The refusals against it", json.dumps(case.get("refusals") or [], ensure_ascii=False, indent=1),
                      "", "## The evidence they cite"] + ["- %s" % e for e in case.get("evidence") or []] +
                     ["", "## Calibration cases", json.dumps(case.get("calibration") or {}, ensure_ascii=False,
                                                             indent=1)])


FIXER_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["new_text", "class", "why"],
                "properties": {"new_text": {"type": "string"}, "class": {"enum": list(REPAIR_CLASSES)},
                               "why": {"type": "string"}, "second_read": {"type": "string"}}}


def default_fixer(prompt, timeout):
    """One fresh Opus run with the fixer's schema. -> its structured answer, or None."""
    import shutil
    import subprocess
    claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    p = subprocess.run([claude, "-p", prompt, "--model", "opus", "--output-format", "json",
                        "--json-schema", json.dumps(FIXER_SCHEMA, separators=(",", ":")),
                        "--name", "CRITERIA FIXER", "--dangerously-skip-permissions"] + EF.effort_args("opus"),
                       capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(p.stdout or "null").get("structured_output")
    except (ValueError, AttributeError):
        return None


def repair(case, runner=default_fixer, calibrate=None, now=None, timeout=FIXER_TIMEOUT_S):
    """Repair one clause by the neutral fixer. `case`: item, clause, criteria {id: text}, owner_bars, source, refusals,
    evidence, calibration, and optionally card / second_read (references the CALLER holds; the fixer's own claim of a
    second read counts for nothing). `calibrate(new_text)` -> (good_passes, bad_passes) when the caller can run it.
    -> {ok, class, errors, new_text, pointer, note, rejudge} or {ok: False, card} for an owner bar (no fixer launched)."""
    now = time.time() if now is None else now
    c, crit, bars = case["clause"], case["criteria"], case.get("owner_bars") or ()
    if c in set(bars):
        return {"ok": False, "card": "%s is an owner bar: put the clause, its refusals and the evidence that nothing "
                                     "could pass to him by card, with options" % c, "errors": ["owner bar"]}
    ans = runner(fixer_prompt(case), timeout)
    if not isinstance(ans, dict) or not str(ans.get("new_text") or "").strip():
        return {"ok": False, "class": None, "errors": ["the fixer gave no repaired text"]}
    new = dict(crit, **{c: ans["new_text"]})
    good, bad = calibrate(ans["new_text"]) if calibrate else (None, None)
    g = diffguard(crit, new, bars, card=case.get("card"), second_read=case.get("second_read"), bad_passes=bad,
                  good_passes=good)
    cls = next((x["class"] for x in g["changes"] if x["clause"] == c), None)
    res = {"ok": g["ok"], "class": cls, "fixer_said": ans.get("class"), "errors": g["errors"], "new_text": ans["new_text"]}
    with _locked():
        res["pointer"] = _store({"at": iso(now), "kind": "repair", "item": case.get("item"), "clause": c,
                                 "old": crit[c], "new": ans["new_text"], "class": cls, "fixer_said": ans.get("class"),
                                 "why": ans.get("why"), "guard": g, "calibration": {"good": good, "bad": bad}})
    res["note"] = "criteria repair %s: %s; refusal %s; calibration good=%s bad=%s%s" % (
        c, cls, res["pointer"], {True: "PASS", False: "FAIL"}.get(good, "UNMEASURED"),
        {True: "PASS", False: "FAIL"}.get(bad, "UNMEASURED"), "" if g["ok"] else "; REFUSED: " + "; ".join(g["errors"]))
    if g["ok"]:
        res["rejudge"] = "fresh instance, same brief"
    return res


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def unwrap(obj):
    """A judge's own file (art_judge_brief.md, scene_look_judge_brief.md) carries the verdict as its `contract` block."""
    if isinstance(obj, dict) and isinstance(obj.get("contract"), dict) and "refusals" not in obj:
        return obj["contract"]
    return obj


RELEASED, NOTHING_OPEN, NO_SUCH_SUBJECT, STORE_UNREADABLE, USAGE = 0, 10, 11, 12, 2


def _release_cli(args):
    """release <subject> --why "<reason>" [--by <who>]: close one open alarm row. Exit 0 released; 10 the row exists
    but is not open (nothing to release); 11 no row for that subject; 12 the alarms store could not be read; 2 usage."""
    opt = lambda k: args[args.index(k) + 1] if k in args and args.index(k) + 1 < len(args) else None  # noqa: E731
    subject, why = (args[0] if args and not args[0].startswith("--") else None), opt("--why")
    if not subject or not (why or "").strip():
        print("usage: refusal_contract.py release <subject> --why \"<reason>\" [--by <who>]  (a reason is required)")
        return USAGE
    try:
        row = _read(alarms_path()).get(subject)
    except (OSError, ValueError) as e:
        print("UNREADABLE alarms store %s: %s: %s; nothing was released" % (alarms_path(), type(e).__name__, e))
        return STORE_UNREADABLE
    if not isinstance(row, dict):
        print("NO SUCH SUBJECT %s in %s; nothing was released" % (subject, alarms_path()))
        return NO_SUCH_SUBJECT
    if not row.get("open"):
        print("NOTHING OPEN for %s (already released %d time(s)); nothing was released" % (
            subject, len(row.get("releases") or [])))
        return NOTHING_OPEN
    try:
        row = clear(subject, why, by=opt("--by") or os.environ.get("RM_SEAT") or os.environ.get("USER"))
    except (OSError, ValueError) as e:
        print("UNWRITABLE alarms store: %s: %s; nothing was released" % (type(e).__name__, e))
        return STORE_UNREADABLE
    print("RELEASED " + json.dumps(row, indent=1, sort_keys=True))
    return RELEASED


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[:1]
    if cmd in (["check"], ["submit"]) and len(argv) >= 2:
        verdict = unwrap(_load(argv[1]))
        given = _load(argv[argv.index("--given") + 1]) if "--given" in argv else None
        if cmd == ["check"]:
            item = str((verdict or {}).get("item") or "") if isinstance(verdict, dict) else ""
            prior = (counters()["items"].get(item) or {}).get("refused", 0)
            errs = check(verdict, given, prior=prior)
            for e in errs:
                print("MALFORMED " + e)
            print("%s: %d error(s)" % ("refused" if errs else "well formed", len(errs)))
            return 1 if errs else 0
        res = submit(verdict, given)
        print(json.dumps(res, indent=1, sort_keys=True))
        return 0 if res["ok"] else 1
    if cmd == ["diffguard"] and len(argv) >= 3:
        bars = argv[argv.index("--bars") + 1].split(",") if "--bars" in argv else ()
        ref = lambda k: argv[argv.index(k) + 1] if k in argv else None  # noqa: E731
        g = diffguard(_load(argv[1]), _load(argv[2]), bars, card=ref("--card"), second_read=ref("--second-read"))
        print(json.dumps(g, indent=1, sort_keys=True))
        return 0 if g["ok"] else 1
    if cmd == ["repair"] and len(argv) >= 2:
        res = repair(_load(argv[1]))
        print(json.dumps(res, indent=1, sort_keys=True))
        return 0 if res["ok"] else 1
    if cmd == ["calibrate"]:
        model = argv[argv.index("--model") + 1].split(",") if "--model" in argv else ()
        reg = calibrate(run_free="--no-run" not in argv and not model, model=model)
        for fam, row in sorted(reg["families"].items()):
            lr = row.get("last_run") or {}
            print("%-24s %-10s %s" % (fam, row["status"], lr.get("cases") or lr.get("out", "")))
        try:
            import coverage_judge
            for f in coverage_judge.unproven_signatures(calibration_root()):
                print("FLAGGED %s signed by %s at %s under an unproven brief (%s); not voided" % (
                    f["concept"], f["signed_by"], f["at"], f["why"]))
        except Exception as e:  # noqa: BLE001 - the status table stands; the scan's failure is said by name
            print("FLAGGED UNMEASURED: %s: %s" % (type(e).__name__, e))
        return 0
    if cmd == ["counters"]:
        c = counters()
        items = {k: v for k, v in c["items"].items() if len(argv) < 2 or k == argv[1]}
        print(json.dumps({"items": items, "families": {k: len(v) for k, v in c["families"].items()},
                          "cached": len(c["cache"])}, indent=1, sort_keys=True))
        return 0
    if cmd == ["release"]:
        return _release_cli(argv[1:])
    if cmd != ["alarms"]:
        print(__doc__)
        return 2
    rows = open_alarms()
    for r in rows:
        print("%s %s trips=%d since %s: %s" % (r["id"], r["subject"], r.get("trips", 0), r.get("first_at"), r.get("why")))
    print("%d open" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
