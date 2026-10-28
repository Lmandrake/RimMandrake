"""contracts.blind -- BlindView: the CLOSED type every token-blind page is built from (BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF).

Owner ruling 2026-10-27: only Operations is token-aware; every other role is token-blind. Free-text redaction (the old
blind_view.redact) can never be complete, so a blind page carries no free text at all:

  * every model is extra="forbid", strict and frozen;
  * classes, sources, decisions, actions, outcomes, states, seats and needs are closed sets (Literal);
  * an identifier (item id, subject, kind, file name) is admitted only by contracts.blind_core: the rimflow id grammar,
    and no part that is an account name, a token/quota/cap/spend word, a unit figure or a long number;
  * an evidence path is admitted only under an allowed root (blind_core.EVIDENCE_ROOTS), segment by segment;
  * a reason is an enum, never prose: titles, notes, block reasons, summaries, commit subjects, `why` details and an
    unban's quoted words are DROPPED, never redacted.

The projection functions (project_digest, project_queue, project_item, project_note) are the ONLY way to make one: a
model validated without this module's private token refuses, model_construct / model_copy / copy refuse, and every
renderer takes only a model a projection ISSUED, unchanged since (a fingerprint of its content is kept at issue: a
model built by a base-class constructor or edited through __dict__ never renders). A value that fails its check is
never mangled: the record is withheld (an item id) or the field dropped (anything else), and both are COUNTED.

Hidden by SOURCE, not by word list (review blind 2026-10-27):
  * item ids come from an Identity(known, hidden): an id shows only when the ledger knows it and it is not hidden;
    Identity None (the ledger did not read) withholds every record that names an item and drops every name;
  * a kind is a closed enum, a row a 1-2 digit number; a subject or file name passes blind_core.name_problem (no
    figure, no key, no account) and names no hidden id;
  * every sha shown is one the injected resolver (blind_core.git_resolver) proved is a commit; no resolver, no sha;
    art-ledger digests and event ids are never shown;
  * a note filter is a closed category (NOTE_CATEGORIES), never free text;
  * the dispatcher's note never carries the unit name.
The renderers write from fixed templates and run a final page guard (page_problem) that fails closed.

Imports pydantic (~50 ms): never import this from the dispatcher's tick; it uses blind_core's stdlib twins.
"""
import datetime as dt
import hashlib
import re
from collections import namedtuple
from typing import Annotated, Literal, Optional

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

try:
    from contracts import blind_core as C
except ImportError:  # run as a file next to blind_core
    import blind_core as C  # type: ignore

SCHEMA = "rimflow.blind-digest/1"
_TOKEN = object()                      # the projection's private key: only this module holds it
_ISSUED = {}                           # id(model) -> (model, fingerprint, private snapshot) per issued page

Identity = namedtuple("Identity", "known hidden")   # ledger ids that exist; ids withheld (about accounts)


def _identity(ids):
    """ids is an Identity or None (unavailable); anything else (an old bare hidden set) is a programming error."""
    if ids is not None and not isinstance(ids, Identity):
        raise TypeError("ids must be blind.Identity or None, not %s" % type(ids).__name__)
    return ids
NOTE_CATEGORIES = ("REPLAN REQUEST", "CUT LIST", "CUT DECISION", "CUT APPLIED", "CUT")


class ProjectionOnly(TypeError):
    """A BlindView model was made outside a projection function."""


class _Closed(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def _only_by_projection(cls, data, info):
        if not (info.context and info.context.get("blind_projection") is _TOKEN):
            raise ValueError("a BlindView is made only by a contracts.blind projection function")
        return data

    @classmethod
    def model_construct(cls, *a, **k):  # noqa: D102 - closes the validation bypass
        raise ProjectionOnly("model_construct bypasses the checks; use a projection function")

    def model_copy(self, *a, **k):  # noqa: D102
        raise ProjectionOnly("model_copy can set unchecked fields; use a projection function")

    def copy(self, *a, **k):  # noqa: D102 - pydantic v1's copy(update=) sets unchecked fields too
        raise ProjectionOnly("copy can set unchecked fields; use a projection function")


def _fp(m):
    return hashlib.sha256(BaseModel.model_dump_json(m, by_alias=True).encode("utf-8")).hexdigest()


def _issue(cls, data):
    """Validate the projection's data and keep a PRIVATE snapshot, re-validated from its JSON (fresh nested objects,
    nothing shared with the model handed out). Renderers render the snapshot, never the caller's object, so no
    mutation, shadowed method or swapped nested model of the handed-out object can reach a page."""
    m = cls.model_validate(data, context={"blind_projection": _TOKEN})
    js = BaseModel.model_dump_json(m, by_alias=True)
    snap = cls.model_validate_json(js, strict=False, context={"blind_projection": _TOKEN})
    _ISSUED[id(m)] = (m, hashlib.sha256(js.encode("utf-8")).hexdigest(), snap)
    return m


def _issued(m, cls):
    """-> the private snapshot of an issued page. Refuses anything a projection did not issue, or that changed since
    (object.__setattr__, __dict__ edits): a tampered object is an error, never silently rendered as issued."""
    e = _ISSUED.get(id(m))
    try:
        same = e is not None and e[0] is m and type(m) is cls and _fp(m) == e[1]
    except Exception:  # noqa: BLE001 - a tampered object that cannot even serialise is refused
        same = False
    if not same:
        raise ProjectionOnly("%s renders only a %s a projection issued, unchanged" % (cls.__name__, cls.__name__))
    return e[2]


def _check(fn, *args):
    def run(v):
        r = fn(v, *args)
        if r:
            raise ValueError("refused: %s" % r)
        return v
    return AfterValidator(run)


def _utc(v):
    if v.tzinfo is None or v.utcoffset() != dt.timedelta(0):
        raise ValueError("refused: a time on a blind page is aware UTC")
    return v


ItemId = Annotated[str, _check(C.item_id_problem)]
Ident = Annotated[str, _check(C.ident_problem, 120)]
Short = Annotated[str, _check(C.ident_problem, 40)]
Evidence = Annotated[str, _check(C.evidence_problem)]
Sha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]       # a resolved commit (the full sha a resolver returned)
Name = Annotated[str, _check(C.name_problem)]
Row = Annotated[str, Field(pattern=r"^[0-9]{1,2}$")]
Time = Annotated[dt.datetime, AfterValidator(_utc)]
Date = Annotated[str, Field(pattern=r"^20\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")]
Count = Annotated[int, Field(ge=0)]

Seat = Literal["BENCH", "FOUNDRY", "OWNER", "DECIDE", "BUILD", "CHECK", "REP", "RUNNER", "DISPATCHER"]
State = Literal["proposed", "ready", "doing", "built", "validated", "done", "dropped", "superseded"]
Needs = Literal["offline", "deploy", "game-up", "bridge", "harvest", "owner"]
DigestClass = Literal["technical", "scope", "design", "art", "cosmetic", "art geometric correction", "art marks",
                      "bridge idle", "leftovers", "unclassified"]
POLICY_CLASSES = tuple(sorted(DigestClass.__args__[:-1], key=len, reverse=True))   # longest first: `art marks` > `art`
Source = Literal["ledger", "verdict", "commit", "marks", "art_install", "leftovers"]
SOURCES = Source.__args__
Decision = Literal["ACCEPT", "REGEN", "ESCALATE", "HOLD_ERROR", "HOLD_INPUT", "REDO", "KEEP", "REJECT", "PASS",
                   "FAIL", "PICK", "OTHER"]
Pick = Literal["A", "B", "C", "D", "E", "F", "G", "H"]
JudgeFamily = Literal["opus", "sonnet", "haiku", "gpt", "gemini", "nemotron", "human"]
By = Literal["BENCH", "FOUNDRY", "OWNER", "DECIDE", "BUILD", "CHECK", "REP", "RUNNER", "DISPATCHER", "git",
             "art_enact", "art_pipeline", "leftovers"]
MarkAction = Literal["archived", "restored", "installed_over_keep", "x_removed", "banned", "unbanned", "ban_hit",
                     "installed"]
LeftKind = Literal["save", "setting", "clone", "other"]
SourceState = Literal["measured", "unmeasured"]
SourceFault = Literal["none", "absent", "unreadable", "git_failed", "import_failed", "error"]
SectionTitle = Literal["NEXT", "IN PROGRESS", "BLOCKED", "WAITING ON A WINDOW", "NOT THIS TARGET", "BUILT", "PROPOSED",
                       "OTHER"]   # a section queue grows later reads OTHER: never silently dropped
NoteRole = Literal["Conductor", "Arbiter", "Auditor", "Operations", "Producer", "Innovator"]
NoteMode = Literal["quick", "run", "weekly", "economy", "event", "alarm"]
NoteOutcome = Literal[tuple(C.NOTE_OUTCOMES)]
LedgerVerb = Short                     # a rimflow verb; projections map anything outside model.VERBS to "other"
Kind = Literal["task", "bug", "build", "decision", "design", "check", "fix", "defect", "art", "feature", "finding",
               "code", "verify", "trial", "investigate", "chore", "ruling", "improvement", "question", "card",
               "continuity", "review", "perf", "harness", "decide", "mechanism", "engine", "tooling", "test", "repair",
               "other"]                # anything else reads "other" (a closed set, never the text)
NoteCategory = Literal[NOTE_CATEGORIES]


def _kind(v):
    k = str(v or "").strip().lower()
    return k if k in Kind.__args__ else "other"


# ------------------------------------------------------------------------------------------- digest -------
class DigestRecord(_Closed):
    source: Source
    cls: DigestClass
    t: Time
    item: Optional[ItemId] = None
    subject: Optional[Name] = None
    verb: Optional[LedgerVerb] = None
    decision: Optional[Decision] = None
    pick: Optional[Pick] = None
    action: Optional[MarkAction] = None
    judge: tuple[JudgeFamily, ...] = ()
    by: Optional[By] = None
    sha: Optional[Sha] = None
    kind: Optional[LeftKind] = None
    evidence: tuple[Evidence, ...] = Field(default=(), max_length=4)


class DigestSource(_Closed):
    source: Source
    state: SourceState
    fault: SourceFault
    records: Count
    malformed: Count
    withheld: Count
    fields_withheld: Count
    all_time: Optional[Count] = None
    newest: Optional[Time] = None


class DigestPage(_Closed):
    schema_: Literal["rimflow.blind-digest/1"] = Field(alias="schema")
    date: Date
    floor: Optional[Time]
    cut: Time
    records: tuple[DigestRecord, ...]
    sources: tuple[DigestSource, ...]


# raw fields a reader may hand the projection, per source (the allow-list: nothing else of a record is looked at)
RAW_FIELDS = {
    "ledger": ("t", "why", "id", "event", "seat", "ranBy", "sha"),
    "verdict": ("t", "rel", "item", "subject", "class", "decision", "judge_keys", "art"),
    "commit": ("t", "sha", "class"),
    "marks": ("t", "type", "reason", "rel"),             # art-ledger digests and event ids: never read, never shown
    "art_install": ("t", "why", "seat", "rel"),
    "leftovers": ("t", "kind", "archive"),
}


def class_of(why):
    """`delegated: art facing judge 2026-10-26, …` -> the policy class it starts with, else "unclassified". Reads the
    label, never copies it: the page shows only the closed class."""
    rest = str(why or "").strip()
    while rest.lower().startswith("delegated:"):
        rest = rest[len("delegated:"):].strip()
    label = re.split(r"\s+[—–-]\s+|--|[—–;,(:\[]|\.\s|\s+per\s+|\s+\d{4}-\d{2}-\d{2}", rest,
                     maxsplit=1)[0].strip().rstrip(".").lower()
    for c in POLICY_CLASSES:
        if label == c or re.match(re.escape(c) + r"[\s/\-]", label):
            return c
    return "unclassified"


def decision_of(v):
    """A verdict's decision text -> (Decision, Pick|None). Prose and anything unknown -> OTHER (never copied)."""
    s = str(v or "").strip().upper()
    if s in Decision.__args__ and s not in ("PICK", "OTHER"):
        return s, None
    if s in Pick.__args__:
        return "PICK", s
    return "OTHER", None


def judges_of(keys):
    out = []
    for k in keys or ():
        fam = next((f for f in JudgeFamily.__args__ if str(k).lower().startswith(f)), None)
        if fam and fam not in out:
            out.append(fam)
    return tuple(out)


def _verbs():
    try:
        from rimflow import model
        return frozenset(model.VERBS)
    except Exception:  # noqa: BLE001 - without the verb list every verb reads "other"
        return frozenset()


def _resolve(resolve, cands):
    """-> {candidate: full sha} from the injected resolver; no resolver, or one that fails, proves nothing."""
    cs = [c for c in dict.fromkeys(str(x).strip().lower() for x in cands if x) if C.CAND_RE.match(c)]
    if not resolve or not cs:
        return {}
    try:
        got = resolve(cs) or {}
    except Exception:  # noqa: BLE001 - an unavailable resolver refuses every sha
        return {}
    # a commit that resolves proves provenance, not that its shown prefix names no account (GPT r4 H1): such a sha
    # is treated as unresolved, so the caller drops and counts it
    return {c: f for c, f in got.items() if c in cs and isinstance(f, str) and re.fullmatch(r"[0-9a-f]{40}", f)
            and f.startswith(c) and not C.account_in(f[:12]) and not C.account_in(f) and not C.account_in(c)}


_PICK_IN = re.compile(r"\b(?i:route|option|pick|choice|chose|choose|chosen)\s+([A-H])\b")


def commit_decision(text):
    """A Delegated: commit line -> (Decision, Pick|None): `... route B` -> PICK B; exactly one Decision word in capitals
    (ACCEPT, KEEP ...) -> that word; else OTHER. The line itself is never copied."""
    t = str(text or "")
    m = _PICK_IN.search(t)
    if m:
        return "PICK", m.group(1)
    words = set(re.findall(r"\b[A-Z][A-Z_]{2,}\b", t)) & (set(Decision.__args__) - {"PICK", "OTHER"})
    return (words.pop(), None) if len(words) == 1 else ("OTHER", None)


def _by(v):
    return v if v in By.__args__ else None


def _names_hidden(s, hidden):
    q = C.squash(s)
    return any(C.squash(h) and C.squash(h) in q for h in hidden or ())


def _record(src, raw, verbs, ids, resolved):
    """-> (fields, withheld_record, dropped_fields). An item id shows only when ids knows it and does not hide it
    (ids None: identity unavailable, the record is withheld); any other unsafe or unproven value drops that field.
    Values are mapped to closed sets here, never copied as text."""
    r = {k: raw.get(k) for k in RAW_FIELDS[src] if k in raw}
    f, dropped = {"source": src, "t": r.get("t")}, 0
    hidden = ids.hidden if ids is not None else ()

    def sha(v):
        nonlocal dropped
        if v in (None, ""):
            return
        full = resolved.get(str(v).strip().lower())
        if full:
            f["sha"] = full
        else:
            dropped += 1

    def name(key, v):
        nonlocal dropped
        if v in (None, ""):
            return
        root, trimmed = (None, True) if ids is None or not isinstance(v, str) else C.registered_name(v, ids.known)
        if root is None or _names_hidden(v, hidden):
            dropped += 1
        else:
            f[key] = root               # the registry's name, never the source's text; a dropped suffix counts
            dropped += int(trimmed)

    def ev(paths):
        nonlocal dropped
        ok = []
        for p in paths:
            shown, refused = C.evidence_view(p, hidden) if p else (None, False)
            if shown and ids is None and not shown.endswith("/"):
                shown, refused = shown.rsplit("/", 1)[0] + "/", True
            if shown and C.evidence_problem(shown):        # e.g. an account in the displayed root: dropped, counted
                shown, refused = None, True
            dropped += int(refused)
            if shown and len(ok) < 4:
                ok.append(shown)
        if ok:
            f["evidence"] = tuple(ok)

    def stem(rel):
        b = str(rel or "").replace("\\", "/").rsplit("/", 1)[-1]
        return b.rsplit(".", 1)[0] if "." in b else b

    iid = r.get("id") if src == "ledger" else r.get("item") if src == "verdict" else None
    if iid not in (None, ""):
        if (ids is None or not isinstance(iid, str) or iid not in ids.known or iid in hidden
                or C.item_id_problem(iid)):
            return None, True, 0
        f["item"] = iid
    if src == "ledger":
        f["cls"] = class_of(r.get("why"))
        verb = r.get("event")
        f["verb"] = verb if isinstance(verb, str) and verb in verbs else "other"
        f["by"] = _by(r.get("ranBy")) or _by(r.get("seat"))
        sha(r.get("sha"))
    elif src == "verdict":
        art = bool(r.get("art"))
        f["cls"] = "art" if art else class_of("delegated: " + str(r.get("class") or ""))
        name("subject", r.get("subject"))
        f["decision"], pick = decision_of(r.get("decision"))
        if pick:
            f["pick"] = pick
        f["judge"] = judges_of(r.get("judge_keys"))
        ev([r.get("rel")])
    elif src == "commit":
        line = str(r.get("class") or "")
        f["cls"] = class_of("delegated: " + line)
        f["decision"], pick = commit_decision(line)
        if pick:
            f["pick"] = pick
        f["by"] = "git"
        sha(r.get("sha"))
    elif src == "marks":
        f["cls"] = "art marks"
        typ, reason = r.get("type"), r.get("reason")
        f["action"] = {"ban": "banned", "unban": "unbanned", "ban_hit": "ban_hit"}.get(typ) or (
            {"archive": "archived", "restore-archive": "restored", "x-delete": "x_removed"}.get(reason,
                                                                                                "installed_over_keep"))
        f["by"] = "art_pipeline" if typ == "ban_hit" else "art_enact"
        name("subject", stem(r.get("rel")) or None)
    elif src == "art_install":
        f["cls"] = class_of(r.get("why"))
        f["action"] = "installed"
        f["by"] = _by(r.get("seat"))
        name("subject", stem(r.get("rel")) or None)
    elif src == "leftovers":
        f["cls"] = "leftovers"
        k = r.get("kind")
        f["kind"] = k if k in LeftKind.__args__ else "other"
        f["by"] = "leftovers"
        ev([r.get("archive")])
    return {k: v for k, v in f.items() if v is not None}, False, dropped


def project_digest(date, floor, cut, raw, status, ids=None, resolve=None):
    """THE way to make a DigestPage. raw: [{"source": <Source>, <RAW_FIELDS of it>...}] (readers extract these from
    the records); status: {source: {"state", "fault", "malformed", "all_time"?, "newest"?}}; ids: Identity, or None
    when the ledger could not be read (every record naming an item is then withheld: fail closed); resolve: the sha
    resolver (blind_core.git_resolver), None = no sha is shown. Withheld records and dropped fields are counted per
    source. Raises ValueError only on a programming error (a bad time or source)."""
    verbs = _verbs()
    ids = _identity(ids)
    per = {s: {"records": 0, "withheld": 0, "fields_withheld": 0} for s in SOURCES}
    for r in raw:
        if r.get("source") not in per:
            raise ValueError("unknown source %r" % (r.get("source"),))
    resolved = _resolve(resolve, [r.get("sha") for r in raw if r.get("source") in ("ledger", "commit")])
    recs = []
    for r in raw:
        src = r["source"]
        fields, held, dropped = _record(src, r, verbs, ids, resolved)
        if held:
            per[src]["withheld"] += 1
            continue
        per[src]["fields_withheld"] += dropped
        per[src]["records"] += 1
        recs.append(fields)
    recs.sort(key=lambda d: d["t"], reverse=True)
    sources = []
    for s in SOURCES:
        st = status.get(s) or {"state": "unmeasured", "fault": "error", "malformed": 0}
        d = dict(per[s], source=s, state=st["state"], fault=st["fault"], malformed=st.get("malformed", 0))
        for k in ("all_time", "newest"):
            if st.get(k) is not None:
                d[k] = st[k]
        sources.append(d)
    return _issue(DigestPage, {"schema": SCHEMA, "date": date, "floor": floor, "cut": cut, "records": tuple(recs),
                               "sources": tuple(sources)})


# -------------------------------------------------------------------------------------- queue / item ------
class QueueItem(_Closed):
    id: ItemId
    state: State
    blocked: bool
    kind: Optional[Kind] = None
    needs: Needs
    row: Optional[Row] = None


class QueueSection(_Closed):
    title: SectionTitle
    items: tuple[QueueItem, ...]


class BlindQueue(_Closed):
    seat: Seat
    withheld: Count
    fields_withheld: Count
    sections: tuple[QueueSection, ...]


class NoteRef(_Closed):
    t: Optional[Time] = None
    seat: Optional[Seat] = None
    refs: tuple[ItemId, ...] = ()
    shas: tuple[Sha, ...] = ()


class ItemEvent(_Closed):
    t: Optional[Time] = None
    verb: LedgerVerb
    seat: Optional[Seat] = None


class BlindItemPage(_Closed):
    id: Optional[ItemId] = None
    withheld: bool = False
    state: Optional[State] = None
    blocked: bool = False
    kind: Optional[Kind] = None
    owner: Optional[Seat] = None
    needs: Optional[Needs] = None
    closed_sha: Optional[Sha] = None
    superseded_by: Optional[ItemId] = None
    superseded_withheld: bool = False
    fields_withheld: Count = 0
    notes_total: Count = 0
    category: Optional[NoteCategory] = None
    notes_matching: Optional[Count] = None
    notes: tuple[NoteRef, ...] = ()
    events_total: Count = 0
    events: tuple[ItemEvent, ...] = ()


def _section_title(t):
    t = str(t or "").split(" — ")[0].strip()
    return t if t in SectionTitle.__args__ else "OTHER"


def _time(ts):
    try:
        d = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if d.tzinfo is None:
        return None
    return d.astimezone(dt.timezone.utc)


def _id_ok(iid, ids):
    ids = _identity(ids)
    return (ids is not None and isinstance(iid, str) and iid in ids.known and iid not in ids.hidden
            and not C.item_id_problem(iid))


def project_queue(seat, groups, ids, withheld=()):
    """groups: [(section title, [rimflow Item])] in the queue's order; ids: Identity (None: identity unavailable,
    every row is withheld); withheld: ids of the seat's open withheld items the caller knows of. The page counts the
    union of those and every row met in groups that is not shown (each once). The kind is a closed enum (else
    "other"), the row a 1-2 digit number (else dropped and counted). Titles, reasons and summaries are never read."""
    sections, held, dropped = [], set(), 0
    for title, items in groups:
        tt = _section_title(title)
        rows = []
        for it in items:
            if not _id_ok(it.id, ids):
                held.add(str(it.id))
                continue
            row = {"id": it.id, "state": it.state, "blocked": bool(it.blocked), "needs": it.needs}
            if it.kind not in (None, ""):
                row["kind"] = _kind(it.kind)
            if it.row not in (None, ""):
                if re.fullmatch(r"[0-9]{1,2}", str(it.row)):
                    row["row"] = str(it.row)
                else:
                    dropped += 1
            rows.append(row)
        if rows and tt:
            sections.append({"title": tt, "items": tuple(rows)})
    return _issue(BlindQueue, {"seat": seat, "withheld": len(held | {str(i) for i in withheld}),
                               "fields_withheld": dropped, "sections": tuple(sections)})


_REF_RE = re.compile(r"[A-Za-z][A-Za-z0-9._-]{2,}")
_SHA_IN = re.compile(r"(?<![\w-])[0-9a-f]{10,40}(?![\w-])")   # a candidate only: shown ONLY when it resolves to a commit


def category_match(text, category):
    """Does a note start with the closed category, at a word boundary ("CUT" matches "CUT LIST: ...", not "CUTTER")?"""
    t = str(text or "").lstrip()
    return t.startswith(category) and (len(t) == len(category) or not (t[len(category)].isalnum()
                                                                        or t[len(category)] == "_"))


def project_item(it, notes, others, ids, last=10, category=None, resolve=None):
    """One item page. notes / others: its ledger events (dicts) in order; ids: Identity (None: the page is withheld);
    category: one of NOTE_CATEGORIES or None (any other value raises: no free-text filter, no count oracle); resolve:
    the sha resolver (None: no sha shown). A note's TEXT never reaches the page: only its time, seat, the known
    non-withheld item ids it names and the commits its shas resolve to."""
    if category is not None and category not in NOTE_CATEGORIES:
        raise ValueError("a blind note filter is one of NOTE_CATEGORIES")
    if not _id_ok(it.id, ids):
        return _issue(BlindItemPage, {"withheld": True})
    d = {"id": it.id, "state": it.state, "blocked": bool(it.blocked), "needs": it.needs, "fields_withheld": 0}
    if it.owner in Seat.__args__:
        d["owner"] = it.owner
    if it.kind:
        d["kind"] = _kind(it.kind)
    d["notes_total"] = len(notes)
    match = [n for n in notes if category_match(n.get("text"), category)] if category else notes
    if category:
        d["category"], d["notes_matching"] = category, len(match)
    shown = match[-last:] if last else match
    cands = [it.closed_sha] + [m for n in shown for m in _SHA_IN.findall(str(n.get("text") or ""))]
    resolved = _resolve(resolve, cands)
    if it.closed_sha:
        full = resolved.get(str(it.closed_sha).strip().lower())
        if full:
            d["closed_sha"] = full
        else:
            d["fields_withheld"] += 1
    if it.superseded_by:
        if _id_ok(it.superseded_by, ids):
            d["superseded_by"] = it.superseded_by
        else:
            d["superseded_withheld"] = True
    refs = []
    for n in shown:
        text = str(n.get("text") or "")
        rid = []
        for w in _REF_RE.findall(text):
            if w != it.id and w not in rid and _id_ok(w, ids):
                rid.append(w)
        found = list(dict.fromkeys(_SHA_IN.findall(text)))      # distinct candidates per note (the count policy)
        shas = tuple(dict.fromkeys(resolved[m] for m in found if m in resolved))
        d["fields_withheld"] += sum(m not in resolved for m in found) + max(0, len(shas) - 6)
        shas = shas[:6]
        ref = {"refs": tuple(rid[:12]), "shas": shas}
        t = _time(n.get("ts"))
        if t:
            ref["t"] = t
        if n.get("seat") in Seat.__args__:
            ref["seat"] = n["seat"]
        refs.append(ref)
    d["notes"] = tuple(refs)
    verbs = _verbs()
    d["events_total"] = len(others)
    evs = []
    for e in (others[-last:] if last else others):
        v = e.get("event")
        x = {"verb": v if isinstance(v, str) and v in verbs else "other"}
        t = _time(e.get("ts"))
        if t:
            x["t"] = t
        if e.get("seat") in Seat.__args__:
            x["seat"] = e["seat"]
        evs.append(x)
    d["events"] = tuple(evs)
    return _issue(BlindItemPage, d)


# ------------------------------------------------------------------------------------------- note ---------
class BlindNote(_Closed):
    role: NoteRole
    outcome: NoteOutcome
    mode: Optional[NoteMode] = None
    run: bool = False                  # the record named a unit: rendered as the word "run", never the unit name


def project_note(b):
    """The dispatcher's blind note as the closed model (its stdlib twin is blind_core.note_text, which the 2-minute
    tick uses). -> BlindNote, or None when the record is not closed. The unit is checked, never kept."""
    if C.note_problem(b):
        return None
    d = {k: b[k] for k in ("role", "outcome", "mode") if b.get(k) is not None}
    d["run"] = b.get("unit") is not None
    return _issue(BlindNote, d)


def render_note(n):
    n = _issued(n, BlindNote)
    b = {k: v for k, v in (("role", n.role), ("outcome", n.outcome), ("mode", n.mode)) if v is not None}
    if n.run:
        b["unit"] = "rm-role-%s-1" % n.role.lower()      # note_text never renders the unit; it only says "run"
    return _guard(C.note_text(b))


# ------------------------------------------------------------------------------------------ render -------
def _hm(t):
    return t.strftime("%m-%d %H:%MZ") if t else "-"


def _iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _ev(p):
    return "`%s`" % C.evidence_native(p)


_SPLIT = re.compile(r"[\s|*()\[\],:;·—→+=#/×'\"!?<>]+")


_GUARD_SHA = re.compile(r"^(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{7,40}$")   # a rendered sha (hex, mixed)
_GUARD_SHA_AT = re.compile(r"\b(sha|git) [0-9a-f]{12}\b")             # a rendered (resolved) sha, by its label
_GUARD_GROUPED = re.compile(r"\d,\d{3}(?!\d)")                                    # 45,000: never a count we print
_GUARD_COUNT = re.compile(r"^[0-9]{1,6}$")                                          # a count the program computed


def page_problem(text):
    """The final guard, independent of the models: every word of a rendered page passes blind_core.ident_problem
    (backticked evidence paths pass evidence_problem instead). -> None, or the first refused word's closed reason
    (never the word). A renderer that trips this raises instead of returning a page: it fails closed."""
    for p in re.findall(r"`([^`]*)`", text):
        if C.evidence_problem(p):
            return "evidence path"
    if _GUARD_GROUPED.search(text):
        return "word: number"
    body = re.sub(r"`[^`]*`", " ", text)
    if any(C.account_in(m.group(0).split(" ")[1]) for m in _GUARD_SHA_AT.finditer(body)):
        return "word: account_name"        # a labelled sha is exempt from the word grammar, never from accounts (r4 H1)
    body = _GUARD_SHA_AT.sub(r"\1", body)   # a sha the renderer printed after its label may be all digits (0.4% of shas)
    for w in _SPLIT.split(body):
        w = w.strip(".-")
        if not w or _GUARD_SHA.match(w) or _GUARD_COUNT.match(w):
            if w and C.account_in(w):
                return "word: account_name"
            continue
        r = C.ident_problem(w, 140)
        if r:
            return "word: %s" % r
    return None


def _guard(text):
    r = page_problem(text)
    if r:
        raise ValueError("blind page guard refused the page (%s)" % r)
    return text


_SRC_LABEL = {"ledger": "ledger events", "verdict": "judge verdict files", "commit": "Delegated commits",
              "marks": "art mark acts", "art_install": "delegated art installs", "leftovers": "leftover deletions"}


def _rec_line(r):
    bits = [_hm(r.t), r.source]
    if r.item:
        bits.append("**%s**" % r.item)
    if r.subject:
        bits.append(r.subject)
    if r.verb:
        bits.append(r.verb)
    if r.decision:
        bits.append(r.decision + ((" " + r.pick) if r.pick else ""))
    if r.action:
        bits.append(r.action)
    if r.kind:
        bits.append(r.kind)
    if r.judge:
        bits.append("judge " + "+".join(r.judge))
    if r.by:
        bits.append("by " + r.by)
    if r.sha:
        bits.append("git " + r.sha[:12] if r.source == "commit" else "sha " + r.sha[:12])
    line = "- " + " ".join(bits)
    if r.evidence:
        line += " evidence " + " ".join(_ev(p) for p in r.evidence)
    return line


def render_digest(page):
    """DigestPage -> markdown, from fixed templates only. Records grouped by class, newest first."""
    page = _issued(page, DigestPage)
    total = len(page.records)
    blind = [_SRC_LABEL[s.source] for s in page.sources if s.state != "measured"]
    out = ["# Delegated calls digest %s" % page.date, "",
           "Every call an agent took without you under delegation_policy.md from %s to %s UTC, grouped by class, "
           "newest first. Built by a program from the records; every count is measured. Ids, classes, decisions, "
           "judges, times and evidence paths only: no record text reaches this page. To overturn a line, say so in "
           "any words." % ("the beginning" if page.floor is None else _iso(page.floor), _iso(page.cut)), "",
           ("**%d delegated record(s)**" % total) if not blind else (
               "**%d delegated record(s) from the measured sources; UNMEASURED, so not counted: %s**" % (
                   total, ", ".join(blind))), "",
           "| source | state | records | malformed | withheld | fields withheld | all time |", "|---|---|---|---|---|---|---|"]
    for s in page.sources:
        state = ("measured" if s.fault == "none" else "measured, %s" % s.fault) if s.state == "measured" else (
            "UNMEASURED %s" % s.fault)
        out.append("| %s | %s | %s | %d | %d | %d | %s |" % (
            _SRC_LABEL[s.source], state, s.records if s.state == "measured" else "UNMEASURED", s.malformed,
            s.withheld, s.fields_withheld, "-" if s.all_time is None else s.all_time))
    out.append("")
    if total == 0 and len(blind) == len(page.sources):
        out += ["No source could be read: this window is UNMEASURED, not empty.", ""]
    elif total == 0:
        newest = max((s.newest for s in page.sources if s.newest), default=None)
        out += ["No delegated record in the %s. Instrument check: the measured sources see %d delegated "
                "record(s) in all time, the newest at %s." % (
                    "measured sources; the UNMEASURED ones may hold some" if blind else "window",
                    sum(s.all_time or 0 for s in page.sources if s.state == "measured"),
                    _iso(newest) if newest else "-"), ""]
    groups = {}
    for r in page.records:
        groups.setdefault(r.cls, []).append(r)
    for cls in sorted(groups, key=lambda k: (-len(groups[k]), k)):
        rs = groups[cls]
        out += ["## %s %d record(s)%s" % (cls, len(rs), " (no policy class logged)" if cls == "unclassified" else ""),
                ""]
        out += [_rec_line(r) for r in rs]
        out.append("")
    return _guard("\n".join(out) + "\n")


def render_queue(q):
    q = _issued(q, BlindQueue)
    out = ["# %s queue blind view" % q.seat, "",
           "Ids, states, kinds, needs and rows only: titles, reasons and summaries never reach this view. %d open "
           "item(s) withheld, %d field(s) withheld." % (q.withheld, q.fields_withheld), ""]
    for s in q.sections:
        out += ["## %s %d" % (s.title, len(s.items)), ""]
        for i in s.items:
            out.append("- **%s** state %s%s kind %s needs %s row %s" % (
                i.id, i.state, " BLOCKED" if i.blocked else "", i.kind or "task", i.needs, i.row or "unassigned"))
        out.append("")
    return _guard("\n".join(out) + "\n")


def render_item(p):
    p = _issued(p, BlindItemPage)
    if p.withheld:
        return _guard("withheld from the blind view: Operations alone\n")
    out = ["%s state %s%s kind %s owner %s needs %s" % (p.id, p.state, " BLOCKED" if p.blocked else "",
                                                       p.kind or "task", p.owner or "-", p.needs)]
    if p.closed_sha:
        out.append("closed at sha %s" % p.closed_sha[:12])
    if p.superseded_by or p.superseded_withheld:
        out.append("superseded by %s" % (p.superseded_by or "a withheld item"))
    if p.fields_withheld:
        out.append("%d field(s) withheld" % p.fields_withheld)
    out.append("notes %d in all%s; shown %d, as the item ids and shas each names, never its text" % (
        p.notes_total, "" if p.notes_matching is None else ", %d in category %s" % (p.notes_matching, p.category),
        len(p.notes)))
    for n in p.notes:
        out.append("- %s %s refs %s %s" % (_iso(n.t) if n.t else "-", n.seat or "-", " ".join(n.refs) or "-",
                                           " ".join("sha " + s[:12] for s in n.shas) or "no sha"))
    out.append("other events %d; shown %d as time, verb, seat" % (p.events_total, len(p.events)))
    for e in p.events:
        out.append("- %s %s %s" % (_iso(e.t) if e.t else "-", e.verb, e.seat or "-"))
    return _guard("\n".join(out) + "\n")
