#!/usr/bin/env python3
"""selftest_blind_contract.py — property tests of the closed blind type (contracts/blind.py, contracts/blind_core.py;
BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF, DIGEST_BLIND_HARDEN_REASONS_SLIP_THROUGH).

  digest   a secret (an account id, an account name, a token figure, a cap, a cost, a key-shaped word, quota phrasing)
           wrapped in arbitrary text and placed in ANY raw field of ANY digest source never reaches the rendered page,
           the page renders (no fail-closed raise), and the page guard passes it. One exception, by construction: a
           32/64-hex key placed in an art ledger sha/id field is indistinguishable from the image sha256 the art
           ledger writes there with hashlib, so hex keys are not planted in those two program-written fields.
  queue    the same secrets in an item's title, block reason, summary, kind, row or id never reach the blind queue;
           every row of the input is listed or counted as withheld
  item     the same secrets in note text and item fields never reach the blind item page
  closed   every model refuses direct construction, model_construct, model_copy and an extra field
  notes    blind_core.note_text (the stdlib twin), project_note + render_note and is_note_text agree on every record,
           closed or not; a forged text is never is_note_text
  guard    page_problem refuses any page carrying a secret word, and passes every page the renderers produce
Account names come from blind_core.account_names() (the repo's rule files), never from this file.
Deterministic (derandomize, no example database). Needs hypothesis and pydantic; without hypothesis: UNMEASURED.
"""
import datetime as dt
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from contracts import blind as BL, blind_core as C  # noqa: E402
try:
    from hypothesis import given, settings, strategies as st, HealthCheck  # noqa: E402
except ImportError:                    # pinned in infrastructure/stevedesktop/mutation_requirements.txt
    print("hypothesis is not installed: UNMEASURED, not a pass or a fail")
    sys.exit(0)

SET = settings(max_examples=400, derandomize=True, database=None, deadline=None,
               suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much])
FAILS = []
T0 = dt.datetime(2026, 10, 27, 6, 0, tzinfo=dt.timezone.utc)
NAMES = sorted(n for n in C.account_names() if n not in C.MODEL_NAMES and len(n) >= 4)
FULL_L, FULL_C = "abcdef1234567" + "8" * 27, "ab" * 20      # the only commits the test resolver knows
KNOWN = frozenset({"PIPE_ELBOW_FIX_SEAM_JOGS", "RM_X_ITEM", "BIOME_DECIDE_TWO_ROUTES"})
HIDDEN = ("STEADY_RIVER_FIX_BANKS", "RM_Quietfern", "LOW_TIDE_BUILD_WEIRS")   # safe-looking, withheld by the ledger
IDS = BL.Identity(KNOWN, frozenset(HIDDEN))


def RESOLVE(cands):
    return {c: f for c in cands for f in (FULL_L, FULL_C) if f.startswith(c)}


def check(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


# ---------------------------------------------------------------------------------------------- secrets ---
# a secret is (the text planted, the needles that must not appear on the page)
_hex = st.text("0123456789abcdef", min_size=6, max_size=8).filter(lambda s: re.search(r"[a-f]", s))
_alnum = st.text("abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789", min_size=10, max_size=20)
_lower = st.text("abcdefghijkmnpqrstuvwxyz23456789", min_size=20, max_size=32)


def _hexn(lo, hi):
    return st.integers(lo, hi).flatmap(lambda n: st.text("0123456789abcdef", min_size=n, max_size=n))


def _camel(name):
    return st.lists(st.booleans(), min_size=len(name), max_size=len(name)).map(
        lambda bs: "".join(c.upper() if b else c for c, b in zip(name, bs)))


def _fig(n):
    return "{:,}".format(n)


# (text, needles, as_id): as_id=False for a secret whose meaning an id cannot carry ($0.01 -> 0_01) or whose words
# are ordinary game words in an id by design (RATE_LIMIT, RUNWAY, BURN: blind_view.WITHHELD_KIND_PARTS' comment)
SECRETS = st.one_of(
    _hex.map(lambda h: ("acct-" + h, ["acct-" + h, h], True)),
    st.integers(1000, 9_999_999).map(lambda n: ("%s tokens" % _fig(n), [_fig(n), str(n)], True)),
    st.integers(11, 99).map(lambda n: ("%d%% of the week" % n, ["%d%%" % n, "%dpct" % n], False)),
    st.integers(11, 999).map(lambda n: ("%dk" % n, ["%dk" % n], True)),
    st.integers(1, 99).map(lambda n: ("$0.%02d" % n, ["$0.%02d" % n, "0.%02d" % n], False)),
    _alnum.map(lambda k: ("sk-live-" + k, ["sk-live", k], True)),
    st.text("0123456789abcdef", min_size=32, max_size=32).map(lambda k: (k, [k[:7]], True)),
    # every hex length a sha field once accepted, and its truncated fragment ("~": substring, no word boundary)
    _hexn(7, 16).map(lambda k: (k, [k, "~" + k[:7]], True)),
    _hexn(40, 40).map(lambda k: (k, [k, "~" + k[:10]], True)),
    _lower.map(lambda k: (k, [k, "~" + k[:10]], True)),                     # an unprefixed lowercase key
    st.sampled_from(NAMES or ["acct"]).flatmap(_camel).map(lambda n: (n, [n], True)),   # sTeVeN
    st.sampled_from(["cost_9", "price_1.5", "spend_3", "budget_12"]).map(lambda c: (c, [c], True)),
    st.integers(30000, 99999).map(lambda n: (str(n), [str(n)], True)),      # a bare figure
    st.sampled_from(["weekly quota", "usage limit", "cost_usd", "quota left"]).map(
        lambda p: (p, [p, p.replace(" ", "_")], True)),
    st.sampled_from(["rate limit hit", "session budget left", "runway at", "burn rate"]).map(
        lambda p: (p, [p, p.replace(" ", "_")], False)),
    st.sampled_from(NAMES or ["acct"]).map(lambda n: (n, [n], True)),
)
JUNK = st.text(st.characters(codec="utf-8", exclude_categories=("Cs",)), max_size=12)


@st.composite
def wrapped(draw):
    secret, needles, as_id = draw(SECRETS)
    pre, post = draw(JUNK), draw(JUNK)
    shape = draw(st.sampled_from(["plain", "id", "path", "why"] if as_id else ["plain", "path", "why"]))
    if shape == "id":
        text = "%s_%s" % (re.sub(r"[^A-Za-z0-9]+", "_", secret).strip("_").upper() or "X", "THING")
        needles = needles + [text]
    elif shape == "path":
        text = "infrastructure/state/delegated/2026-10-27/%s.json" % secret
    elif shape == "why":
        text = "delegated: scope — " + secret
    else:
        text = pre + secret + post
    return text, needles


def leaked(page, needles):
    low = page.lower()
    for n in needles:
        n = str(n).lower()
        if n.startswith("~"):                        # a fragment a renderer could cut a secret down to
            if n[1:] in low:
                return n
            continue
        if len(n) >= 3 and re.search(r"(?<![0-9a-z])" + re.escape(n) + r"(?![0-9a-z])", low):
            return n
    return None


# ------------------------------------------------------------------------------------------------ digest --
BASE = {
    "ledger": {"t": T0, "why": "delegated: scope", "id": "PIPE_ELBOW_FIX_SEAM_JOGS", "event": "close",
               "seat": "BENCH", "ranBy": "BENCH", "sha": "abcdef1234567"},   # resolves to FULL_L
    "verdict": {"t": T0, "rel": "infrastructure/state/delegated/2026-10-27/RM_X__r1.json", "item": "RM_X_ITEM",
                "subject": "RM_Chittik_n", "class": "art", "decision": "ACCEPT", "judge_keys": ("opus", "gpt"),
                "art": True},
    "commit": {"t": T0, "sha": FULL_C, "class": "scope"},
    "marks": {"t": T0, "type": "live", "reason": "archive", "id": "ab12" * 5, "sha": "cd" * 32, "prev": "ef" * 32,
              "rel": "Mods/X/Textures/RM_Bloodlurk_south.png"},
    "art_install": {"t": T0, "why": "delegated: art", "seat": "BENCH", "sha": "12ab" * 16,
                    "rel": "Mods/X/Textures/RM_Tikkit.png"},
    "leftovers": {"t": T0, "kind": "save", "archive": "/mnt/d/ClaudeWork/backups/leftovers/a.zip"},
}
STATUS = {s: {"state": "measured", "fault": "none", "malformed": 0, "all_time": 1} for s in BL.SOURCES}
FIELDS = [(s, f) for s in BL.SOURCES for f in BL.RAW_FIELDS[s] if f != "t"]


def digest_page(raw, status=STATUS, ids=IDS):
    page = BL.project_digest("2026-10-27", None, T0 + dt.timedelta(hours=1), raw, status, ids, RESOLVE)
    return BL.render_digest(page)


@SET
@given(st.sampled_from(FIELDS), wrapped(), st.booleans())
def prop_digest(field, plant, every_source):
    src, key = field
    text, needles = plant
    raw = []
    for s in (BL.SOURCES if every_source else (src,)):
        r = dict(BASE[s], source=s)
        for k in BL.RAW_FIELDS[s]:
            if k != "t" and (k == key or every_source):
                r[k] = text
        raw.append(r)
    page = digest_page(raw)
    hit = leaked(page, needles)
    assert hit is None, "digest %s.%s leaked %r from %r" % (src, key, hit, text)
    assert BL.page_problem(page) is None


# ------------------------------------------------------------------------------------------------ queue ---
def item(**kw):
    d = {"id": "PIPE_ELBOW_FIX_SEAM_JOGS", "state": "ready", "blocked": False, "kind": "task", "needs": "offline",
         "row": "3", "title": "fine", "block_reason": None, "summary": None, "owner": "BENCH", "closed_sha": None,
         "superseded_by": None, "open": True, "history": []}
    d.update(kw)
    return types.SimpleNamespace(**d)


@SET
@given(st.sampled_from(["id", "title", "block_reason", "summary", "kind", "row"]), wrapped(),
       st.sampled_from(["NEXT", "BLOCKED — on a window", "PROPOSED", "something new"]))
def prop_queue(field, plant, section):
    text, needles = plant
    bad = item(**{field: text, "blocked": field == "block_reason"})
    good = item(id="BIOME_DECIDE_TWO_ROUTES")
    q = BL.project_queue("BENCH", [(section, [bad, good])], IDS)
    page = BL.render_queue(q)
    hit = leaked(page, needles)
    assert hit is None, "queue %s leaked %r from %r" % (field, hit, text)
    assert BL.page_problem(page) is None
    listed = sum(len(s.items) for s in q.sections)
    assert listed + q.withheld == 2 and "BIOME_DECIDE_TWO_ROUTES" in page


CATS = st.one_of(st.none(), st.sampled_from(BL.NOTE_CATEGORIES))


def item_page(it, notes, category):
    return BL.render_item(BL.project_item(it, notes, [{"event": "file", "seat": "BENCH", "ts": "x"}], IDS, 10,
                                          category, RESOLVE))


@SET
@given(st.lists(wrapped(), min_size=1, max_size=4), st.sampled_from(["kind", "closed_sha", "superseded_by", "id"]),
       CATS, st.booleans())
def prop_item(plants, field, category, lead):
    head = (category + ": ") if category and lead else ""
    notes = [{"event": "note", "seat": "BENCH", "ts": "2026-10-27T05:00:00Z",
              "text": head + "see BIOME_DECIDE_TWO_ROUTES at abc1234 " + t} for t, _n in plants]
    it = item(**{field: plants[0][0]})
    page = item_page(it, notes, category)
    for _t, needles in plants:
        hit = leaked(page, needles)
        assert hit is None, "item page leaked %r from %r" % (hit, [t for t, _n in plants])
    assert BL.page_problem(page) is None


@SET
@given(wrapped(), wrapped(), CATS)
def prop_no_oracle(a, b, category):
    """Differential: two notes that differ only in their secret give the same page under every closed filter, so no
    sequence of filtered queries can recover the text (the free-text prefix oracle)."""
    def page(secret):
        text = (category + ": " if category else "") + secret
        return item_page(item(), [{"event": "note", "seat": "BENCH", "ts": "2026-10-27T05:00:00Z", "text": text}],
                         category)
    # the one sanctioned channel: the withheld-field count (an unresolved sha candidate is counted, r1 MED 17)
    assert _uncounted(page(a[0])) == _uncounted(page(b[0])), "the page depends on the note text: %r vs %r" % (
        a[0], b[0])


def _uncounted(page):
    return re.sub(r"^\d+ field\(s\) withheld\n", "", page, flags=re.M)


@SET
@given(st.sampled_from(HIDDEN), st.sampled_from(FIELDS), st.sampled_from(["plain", "path"]))
def prop_hidden(hid, field, shape):
    """A withheld id, however safe it looks, appears in no field of any page."""
    src, key = field
    text = "infrastructure/state/delegated/2026-10-27/%s.json" % hid if shape == "path" else hid
    page = digest_page([dict(BASE[src], source=src, **{key: text})])
    assert leaked(page, [hid]) is None, "digest %s.%s showed hidden %s" % (src, key, hid)
    q = BL.render_queue(BL.project_queue("BENCH", [("NEXT", [item(id=hid), item(id="RM_X_ITEM", title=hid,
                                                                                 kind=hid)])], IDS))
    assert leaked(q, [hid]) is None, "queue showed hidden %s" % hid
    ip = item_page(item(superseded_by=hid), [{"event": "note", "seat": "BENCH", "ts": "2026-10-27T05:00:00Z",
                                             "text": "see " + hid}], None)
    assert leaked(ip, [hid]) is None, "item page showed hidden %s" % hid
    assert "withheld" in item_page(item(id=hid), [], None).lower()


@SET
@given(st.lists(st.sampled_from(["measured", "unmeasured"]), min_size=len(BL.SOURCES), max_size=len(BL.SOURCES)),
       st.booleans(), st.booleans())
def prop_unmeasured(states, with_records, ident):
    """An unreadable source or identity never reads as a measured zero, and its records never show."""
    status = {s: {"state": st_, "fault": "none" if st_ == "measured" else "unreadable", "malformed": 0}
              for s, st_ in zip(BL.SOURCES, states)}
    raw = [dict(BASE[s], source=s) for s in BL.SOURCES if with_records and status[s]["state"] == "measured"]
    page = digest_page(raw, status, IDS if ident else None)
    head = page.split("|")[0]
    assert BL.page_problem(page) is None
    if "unmeasured" in states:
        assert "UNMEASURED" in head, head
    if all(x == "unmeasured" for x in states):
        assert "No delegated record in this window" not in page and "not empty" in page
    if not ident:
        assert "PIPE_ELBOW_FIX_SEAM_JOGS" not in page and "RM_X_ITEM" not in page


# ------------------------------------------------------------------------------------------------ notes ---
NOTE = st.fixed_dictionaries({"role": st.one_of(st.sampled_from(C.NOTE_ROLES), st.text(max_size=8)),
                              "outcome": st.one_of(st.sampled_from(sorted(C.NOTE_OUTCOMES)), st.text(max_size=8))},
                             optional={"mode": st.one_of(st.sampled_from(C.NOTE_MODES), st.text(max_size=6)),
                                       "unit": st.one_of(st.integers(0, 10 ** 12).map(str),
                                                         st.text(max_size=20)),
                                       "extra": st.text(max_size=5)})


@SET
@given(NOTE, st.booleans())
def prop_note(b, unit_for_role):
    if unit_for_role and isinstance(b.get("role"), str) and "unit" in b:
        b = dict(b, unit="rm-role-%s-%s" % (b["role"].lower(), re.sub(r"\D", "", b["unit"])[:12] or "1"))
    twin = C.note_text(b)
    m = BL.project_note(b)
    assert (twin is None) == (m is None) == bool(C.note_problem(b))
    if twin is not None:
        assert BL.render_note(m) == twin
        assert C.is_note_text(twin)
        assert BL.page_problem(twin) is None


@SET
@given(st.text(max_size=60), wrapped())
def prop_forged(prefix, plant):
    forged = "dispatcher: Conductor quick run: " + prefix + plant[0]
    if C.is_note_text(forged):
        # only a text note_text could have rendered passes; it can then hold no secret
        assert leaked(forged, plant[1]) is None


# ------------------------------------------------------------------------------------------------ closed --
def closed_checks():
    models = [BL.DigestRecord, BL.DigestSource, BL.DigestPage, BL.QueueItem, BL.QueueSection, BL.BlindQueue,
              BL.NoteRef, BL.ItemEvent, BL.BlindItemPage, BL.BlindNote]
    for M in models:
        for how, fn in (("direct", lambda: M()), ("model_validate", lambda: M.model_validate({})),
                        ("model_construct", lambda: M.model_construct())):
            try:
                fn()
                ok = False
            except Exception:  # noqa: BLE001 - ProjectionOnly or ValidationError: refused either way
                ok = True
            check(ok, "closed: %s refuses %s" % (M.__name__, how))
    import pydantic
    check(not hasattr(BL, "_CTX"), "closed: no exported construction context")
    q = BL.project_queue("BENCH", [("NEXT", [item()])], IDS)

    def mutated():
        q2 = BL.project_queue("BENCH", [("NEXT", [item()])], IDS)
        q2.__dict__["withheld"] = 45000
        return BL.render_queue(q2)
    for how, fn in (("model_copy", lambda: q.model_copy(update={"seat": "OWNER"})),
                    ("copy", lambda: BL.render_queue(q.copy(update={"withheld": 45000}))),
                    ("base model_construct", lambda: BL.render_queue(pydantic.BaseModel.model_construct.__func__(
                        BL.BlindQueue, seat="BENCH", withheld=45000, fields_withheld=0, sections=()))),
                    ("model_validate of a dump", lambda: BL.render_queue(
                        BL.BlindQueue.model_validate(dict(q.model_dump(), withheld=45000)))),
                    ("__dict__ mutation", mutated),
                    ("setattr", lambda: setattr(q, "seat", "OWNER"))):
        try:
            fn()
            ok = False
        except Exception:  # noqa: BLE001
            ok = True
        check(ok, "closed: a projected BlindQueue refuses %s" % how)
    for fn, arg in ((BL.render_queue, {"seat": "BENCH"}), (BL.render_item, {}), (BL.render_digest, {}),
                    (BL.render_note, {"role": "Conductor", "outcome": "completed"})):
        try:
            fn(arg)
            ok = False
        except BL.ProjectionOnly:
            ok = True
        check(ok, "closed: %s takes only its model" % fn.__name__)


def guard_checks():
    # a bare count of up to 6 digits passes the guard on purpose (the program prints counts); the models keep bare
    # numbers out of every field, the guard is the net behind them
    for n in ["acct-7f3e9", "45,000", "93%", "80k", "$0.34", "sk-live-zz9abc", "quota", "cost_usd", "1234567"] + NAMES[:3]:
        check(BL.page_problem("- 10-27 ledger %s by BENCH\n" % n) is not None, "guard: refuses a page with %r" % n)
    check(BL.page_problem("- 10-27 06:00Z ledger **PIPE_ELBOW_FIX_SEAM_JOGS** close by BENCH sha 121212121212\n")
          is None, "guard: passes a labelled all-digit sha")


def review_r2_checks():
    """Review night r2: a reference at the end of a sentence ("... X.") is still that item; references past the
    12 shown are counted withheld, like shas past 6."""
    note = {"event": "note", "seat": "BENCH", "ts": "2026-10-27T06:00:00Z", "text": "See BIOME_DECIDE_TWO_ROUTES."}
    page = item_page(item(), [note], None)
    check("BIOME_DECIDE_TWO_ROUTES" in page, "refs: a trailing full stop does not lose the reference")
    many = ["PIPE_ELBOW_FIX_SEAM_" + c for c in "ABCDEFGHIJKLM"]
    ids = BL.Identity(frozenset(many) | KNOWN, frozenset(HIDDEN))
    note = dict(note, text="see " + " ".join(many))
    pg = BL.project_item(item(), [note], [{"event": "file", "seat": "BENCH", "ts": "x"}], ids, 10, None, RESOLVE)
    check(pg.fields_withheld >= 1, "refs: the 13th reference (past 12 shown) is counted withheld (%d)"
          % pg.fields_withheld)
    note = dict(note, text="see 0BIOME_DECIDE_TWO_ROUTES")
    check("BIOME_DECIDE_TWO_ROUTES" not in item_page(item(), [note], None),
          "refs: an id inside a larger token (0X) is not a reference (review r3)")


def main():
    check(bool(NAMES), "instrument: blind_core.account_names() yields account names to plant (%d)" % len(NAMES))
    base = digest_page([dict(BASE[s], source=s) for s in BL.SOURCES])
    vals = [h["value"] for h in getattr(base, "handles", {}).values()]   # shas ride in the handle map, never raw
    check(all(x in base for x in ("PIPE_ELBOW_FIX_SEAM_JOGS", "RM_Chittik", "sha E", "git E",
                                  "marks RM_Bloodlurk archived", "art_install RM_Tikkit installed"))
          and any(v.startswith("abcdef123456") for v in vals) and any(v.startswith("abababababab") for v in vals)
          and "abcdef123456" not in base and "abababababab" not in base,
          "instrument: the clean base records render their closed fields (the planted fields are visible slots)")
    for name, prop in (("digest: a secret in any field of any source", prop_digest),
                       ("queue: a secret in any item field", prop_queue),
                       ("item: a secret in notes or item fields", prop_item),
                       ("item: no note-text count oracle under any closed filter", prop_no_oracle),
                       ("hidden: a withheld id reaches no page field", prop_hidden),
                       ("unmeasured: an unreadable source or identity is never a measured zero", prop_unmeasured),
                       ("notes: the stdlib twin, the model and is_note_text agree", prop_note),
                       ("notes: a forged text holding a secret is never a note", prop_forged)):
        try:
            prop()
            check(True, name)
        except Exception as e:  # noqa: BLE001
            check(False, "%s: %s" % (name, str(e).splitlines()[0][:300]))
    closed_checks()
    guard_checks()
    review_r2_checks()
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
