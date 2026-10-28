#!/usr/bin/env python3
"""selftest_blind_allowlist.py — the allowlist renderer (BLINDVIEW_HARDEN_SIX_LEAKS_STILL_OPEN).

Four review rounds each found a new KIND of leak route through per-field deny checks. The renderer now emits only
typed tokens (template words, code enum labels, ledger item ids, registered names, numbers of declared measures,
formatted times, opaque handles) and a whole-page gate refuses any page carrying a token it did not emit. This test
proves the gate refuses each class of foreign token, and a Hypothesis property: an account name and a figure
injected into EVERY input field of every page kind never reach the page (the render either refuses or is clean), and
no raw sha or path ever prints.

Run: python3 src/RimMandrake/contracts/selftest_blind_allowlist.py
"""
import datetime as dt
import hashlib
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(SRC, "rimflow"))
from contracts import blind as BL, blind_core as C  # noqa: E402

from hypothesis import HealthCheck, given, settings, strategies as st  # noqa: E402

FAILS = []
T0 = dt.datetime(2026, 10, 27, 6, 0, tzinfo=dt.timezone.utc)
SHA_A = "abcdef0123456789abcdef0123456789abcdef01"
KNOWN = ("PIPE_ELBOW_FIX_SEAM_JOGS", "BIOME_DECIDE_TWO_ROUTES", "RM_X_ITEM")
STATUS = {s: {"state": "measured", "fault": "none", "malformed": 0, "all_time": 1} for s in BL.SOURCES}


def check(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:  # noqa: BLE001 - a crash is a failure of the check, shown
        ok, detail = False, "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:200] if str(e) else "")
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  [%s]" % str(detail)[:400]))
    if not ok:
        FAILS.append(name)


def refuses(fn):
    try:
        fn()
    except (C.PageRefused, ValueError, TypeError):
        return True
    return False


def ids(known=KNOWN):
    return BL.Identity(known=frozenset(known), hidden=frozenset())


def resolver(cands):
    return {c: SHA_A for c in cands if isinstance(c, str) and len(c) >= 7 and SHA_A.startswith(c.lower())}


def page(**kw):
    kw.setdefault("vocab", {"row", "sha"})
    kw.setdefault("enums", (("ready", "done"),))
    return C.Page(**kw)


# ------------------------------------------------------------------------------------------ the gate -----
def g_lit_data():
    return refuses(lambda: page().lit("row swordfish")), "lit of a non-template word"


def g_vocab_digit():
    return refuses(lambda: C.Page({"row", "tok45000"})), "a vocab word with a digit"


def g_enum_domain():
    p = page()
    return (refuses(lambda: p.enum("ready", ("ready", "done", "swordfish")))
            and refuses(lambda: p.enum("swordfish", ("ready", "done")))), "unregistered domain / value"


def g_measure():
    p = page()
    return (refuses(lambda: p.num(45000, "tokens")) and refuses(lambda: p.num(-1, "row"))
            and refuses(lambda: p.num(True, "row")) and refuses(lambda: p.num(1.5, "row"))
            and refuses(lambda: p.num(C.COUNT_MAX + 1, "row"))), "undeclared measure / bad number"


def gated(text, allowed):
    """page_gate's verdict as a bool: True when the page is refused."""
    import collections
    return C.page_gate(text, collections.Counter(allowed)) is not None


def g_unicode():
    return (gated("row \u0441ost", {"row": 1}) and gated("row\u200b", {"row": 1})
            and not gated("row", {"row": 1})), "non-ascii / zero-width"


def g_foreign_token():
    return gated("row 45000", {"row": 1}), "a token outside the allowlist"


def g_appended():
    p = page()
    p.lit("row ")
    p.num(3, "row")
    t = p.text()
    return gated(t + " swordfish", {"row": 1, "3": 1}) and str(t) == "row 3", t


def g_multiset():
    # a token emitted once may not appear twice: the gate counts, not just membership
    return gated("row row", {"row": 1}) and not gated("row row", {"row": 2}), "duplicated token"


def g_item_name():
    p = page(item_ok=lambda i: i in KNOWN, name_ok=lambda n: n == "RM_Chittik")
    q = page(item_ok=lambda i: i in KNOWN)
    q.item(KNOWN[0])
    return (refuses(lambda: p.item("RM_NOT_KNOWN")) and refuses(lambda: p.name("swordfish"))
            and refuses(lambda: page().item(KNOWN[0])) and str(q.text()) == KNOWN[0]), "item/name predicates"


def g_handles():
    p = page()
    p.lit("sha ")
    p.handle("sha", SHA_A)
    p.lit(" sha ")
    p.handle("sha", SHA_A)
    t = p.text()
    with tempfile.TemporaryDirectory() as tmp:
        C.store_handles(t, t.handles, tmp)
        fn = os.path.join(tmp, hashlib.sha256(str(t).encode()).hexdigest()[:16] + ".json")
        stored = json.load(open(fn))["handles"]
    return (str(t) == "sha E1 sha E1" and SHA_A not in t and stored["E1"]["value"] == SHA_A
            and refuses(lambda: page().handle("account", "x"))), t


def g_registry_outage():
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "slot_rules.json")
        open(f, "w").write("{not json")
        old = C.RULE_FILES
        C.RULE_FILES = (f,)
        try:
            p = page()
            p.lit("row ")
            p.num(3, "row")
            r = refuses(p.text)
        finally:
            C.RULE_FILES = old
    return r, "an unreadable registry refuses the page"


# ------------------------------------------------------------------------------------------ property -----
class Registry:
    """A temporary account registry (C.RULE_FILES), rewritten per example with a fresh stamp."""
    n = 0

    def __init__(self, tmp):
        self.p = os.path.join(tmp, "slot_rules.json")

    def set(self, names):
        json.dump({"accounts": {n: {} for n in names}}, open(self.p, "w"))
        Registry.n += 1
        os.utime(self.p, (1, 2_000_000_000 + Registry.n * 10))


ACCT = st.from_regex(r"zq[a-z]{3,8}", fullmatch=True)          # "zq" occurs in no template word
FIG = st.integers(min_value=100_000, max_value=10**12)          # >5 digits: no date, time or count has that run


def forms(a, f):
    return ["%s" % a, "%s %d" % (a, f), "%s_%d" % (a, f), "%s used %d tokens" % (a.upper(), f), "%d" % f,
            "%s/%d.json" % (a, f), "%.1fk" % (f / 1000), "$%d" % f, "RM_%s_%d" % (a, f)]


def inputs(a, f, i):
    """Every input field of every page kind, carrying the account a / figure f in form i."""
    x = forms(a, f)[i % 9]
    sha = SHA_A[:12]
    raw = [
        {"source": "ledger", "t": T0, "id": x, "why": "delegated: " + x, "event": x, "seat": x, "ranBy": x,
         "sha": x},
        {"source": "ledger", "t": T0, "id": "RM_X_ITEM", "why": x, "event": "close", "seat": "BENCH", "sha": sha},
        {"source": "verdict", "t": T0, "rel": "infrastructure/state/delegated/2026-10-27/%s.json" % x, "item": x,
         "subject": x, "class": x, "decision": x, "judge_keys": (x,), "art": True},
        {"source": "commit", "t": T0, "class": x, "sha": sha},
        {"source": "marks", "t": T0, "type": x, "reason": x, "rel": "a/%s.png" % x},
        {"source": "art_install", "t": T0, "why": x, "seat": x, "rel": "b/%s.png" % x},
        {"source": "leftovers", "t": T0, "kind": x, "archive": "c/%s.zip" % x},
    ]
    # status is the digest's own measurement (code-computed counts), not record text: it stays a small count
    status = {s: {"state": "measured", "fault": "none", "malformed": 0, "all_time": 7} for s in BL.SOURCES}
    # `it`: a valid rimflow Item (state / needs are model-validated literals) whose free fields carry x;
    # `bad`: every field carries x (the row is refused or withheld whole)
    it = types.SimpleNamespace(id=KNOWN[0], state="ready", blocked=False, kind=x, needs="offline", row=x, title=x,
                               owner=x, closed_sha=sha, superseded_by=x, open=True, history=[])
    bad = types.SimpleNamespace(id=x, state=x, blocked=False, kind=x, needs=x, row=str(f), title=x, owner=x,
                                closed_sha=x, superseded_by=x, open=True, history=[])
    notes = [{"event": "note", "seat": x, "ts": "2026-10-27T05:00:00Z", "text": "%s %s %s" % (x, sha, KNOWN[1])},
             {"event": "note", "seat": "BENCH", "ts": x, "text": x}]
    note = {"role": x, "outcome": x, "mode": x, "unit": x}
    note2 = {"role": "Conductor", "outcome": "completed", "mode": "quick", "unit": "rm-role-conductor-%d" % f}
    return raw, status, it, bad, notes, note, note2


def renders(a, f, i):
    """[(kind, page or None when refused)]"""
    raw, status, it, bad, notes, note, note2 = inputs(a, f, i)
    jobs = [
        ("digest", lambda: BL.render_digest(BL.project_digest("2026-10-27", None, T0 + dt.timedelta(hours=1), raw,
                                                               status, ids=ids(), resolve=resolver))),
        ("queue", lambda: BL.render_queue(BL.project_queue("BENCH", [("NEXT", [it, bad])], ids()))),
        ("item", lambda: BL.render_item(BL.project_item(it, notes, notes, ids(), resolve=resolver))),
        ("note", lambda: BL.render_note(BL.project_note(note))),
        ("note_unit", lambda: BL.render_note(BL.project_note(note2))),
    ]
    out = []
    for kind, fn in jobs:
        try:
            out.append((kind, fn()))
        except Exception:  # noqa: BLE001 - any refusal is closed: nothing is shown
            out.append((kind, None))
    return out


SEEN = {"pages": 0, "refused": 0, "bad": []}


def clean(pg, a, f):
    low = pg.lower()
    return (a not in low and str(f) not in pg and "%.1fk" % (f / 1000) not in pg and SHA_A[:7] not in pg
            and "/" not in pg.replace(" / ", "") and ".json" not in pg and ".png" not in pg and ".zip" not in pg)


def prop():
    with tempfile.TemporaryDirectory() as tmp:
        reg = Registry(tmp)
        old = C.RULE_FILES
        C.RULE_FILES = (reg.p,)

        @settings(max_examples=150, deadline=None, suppress_health_check=list(HealthCheck), database=None)
        @given(ACCT, FIG, st.integers(min_value=0, max_value=8))
        def run(a, f, i):
            reg.set([a])
            for kind, pg in renders(a, f, i):
                if pg is None:
                    SEEN["refused"] += 1
                    continue
                SEEN["pages"] += 1
                if not clean(pg, a, f):
                    SEEN["bad"].append((kind, a, f, i, str(pg)[:300]))
                assert clean(pg, a, f), (kind, a, f, i, str(pg)[:300])
        try:
            run()
        finally:
            C.RULE_FILES = old
    # the instrument can see: most renders produce a page (a property over all-refused renders proves nothing)
    return SEEN["pages"] > SEEN["refused"] and not SEEN["bad"], SEEN


def baseline_sees():
    """Sanity probe: the clean() predicate does catch a leak when the renderer is bypassed."""
    return not clean("records zqfoo 123456", "zqfoo", 123456) and clean("records 3", "zqfoo", 123456), "probe"


def main():
    for name, fn in [("gate: lit refuses a data word", g_lit_data), ("gate: vocab words carry no digits", g_vocab_digit),
                     ("gate: enum domain must be registered", g_enum_domain),
                     ("gate: numbers only of declared measures", g_measure), ("gate: unicode refused", g_unicode),
                     ("gate: a foreign token refuses the page", g_foreign_token),
                     ("gate: appended text refused", g_appended), ("gate: token multiset", g_multiset),
                     ("gate: item/name predicates", g_item_name), ("gate: handles opaque and stored", g_handles),
                     ("gate: registry outage fails closed", g_registry_outage),
                     ("probe: the leak predicate can see", baseline_sees),
                     ("property: injected accounts and figures never reach a page", prop)]:
        check(name, fn)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
