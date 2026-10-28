#!/usr/bin/env python3
"""selftest_blind_harden.py — one red-first check per finding of gpt_review_blind_2026-10-27.md
(BLINDVIEW_HARDEN_SIX_LEAKS_STILL_OPEN). Each check names its finding (F1..F17). Deterministic, offline, stdlib +
pydantic. The structural rules it pins:

  F1  identifiers: kinds are a closed enum, rows a 1-2 digit number, subjects and evidence file names a strict
      letters-only name grammar (no figure, no key), else dropped and counted
  F2  account names: matched on the squashed canonical form (case, separators, camel) against a registry that is
      re-read when its files change and RAISES when a file cannot be read (fail closed)
  F3  every sha shown resolves to a real commit (an injected resolver; none = refused); notes give no sha of their own
      text; art ledger digests are never shown
  F4  no arbitrary prefix: a closed note category only
  F5  identity unavailable (ids None) withholds every record with a reference; a hidden id in any field withholds
  F6  a blind note never carries the unit name; render_note runs the page guard
  F7  a model made or changed outside a projection never renders (copy, base model_construct, _CTX, __dict__)
  F8-F14 delegated_digest state, dry run, error log, headline
  F15 a commit line's pick reaches the closed decision fields
  F17 a refused sha is counted as a withheld field
  R1-* gpt_review_blind_harden_r1: registry-issued names, short/dotted accounts, a private render snapshot, an
       unlistable verdict directory, complete state validation, unresolved note shas counted
  R2-H gpt_review_blind_harden_r2: a registry key is never exempt as a model name; a null account map raises
  R3-H gpt_review_blind_harden_r3: the evidence path is account-checked as displayed (native root included)
"""
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(SRC, "rimflow"))
from contracts import blind as BL, blind_core as C  # noqa: E402

FAILS = []
T0 = dt.datetime(2026, 10, 27, 6, 0, tzinfo=dt.timezone.utc)
SHA_A = "abcdef0123456789abcdef0123456789abcdef01"


def check(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:  # noqa: BLE001 - a crash is a failure of the check, shown
        ok, detail = False, "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:200] if str(e) else "")
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  [%s]" % detail))
    if not ok:
        FAILS.append(name)


def resolver(known_full=(SHA_A,)):
    def res(cands):
        out = {}
        for c in cands:
            hit = [f for f in known_full if f.startswith(str(c).lower())]
            if len(hit) == 1 and len(str(c)) >= 7:
                out[c] = hit[0]
        return out
    return res


def handled(page, label, prefix):
    """The page shows `<label> E<n>` and that handle maps (in the page's handle map, never on the page) to a value
    starting with prefix."""
    hs = re.findall(r"\b%s (E\d+)\b" % label, page)
    return any(page.handles.get(h, {}).get("value", "").startswith(prefix) for h in hs)


def ids(known=(), hidden=()):
    return BL.Identity(known=frozenset(known), hidden=frozenset(hidden))


def item(**kw):
    d = {"id": "PIPE_ELBOW_FIX_SEAM_JOGS", "state": "ready", "blocked": False, "kind": "task", "needs": "offline",
         "row": "3", "title": "fine", "owner": "BENCH", "closed_sha": None, "superseded_by": None, "open": True,
         "history": []}
    d.update(kw)
    return types.SimpleNamespace(**d)


STATUS = {s: {"state": "measured", "fault": "none", "malformed": 0, "all_time": 1} for s in BL.SOURCES}
KNOWN = ("PIPE_ELBOW_FIX_SEAM_JOGS", "BIOME_DECIDE_TWO_ROUTES", "RM_X_ITEM")


def digest(raw, status=STATUS, ident="default", resolve="default"):
    ident = ids(KNOWN) if ident == "default" else ident
    resolve = resolver() if resolve == "default" else resolve
    page = BL.project_digest("2026-10-27", None, T0 + dt.timedelta(hours=1), raw, status, ids=ident, resolve=resolve)
    return page, BL.render_digest(page)


def verdict(**kw):
    d = {"source": "verdict", "t": T0, "rel": "infrastructure/state/delegated/2026-10-27/RM_Chittik__r1.json",
         "item": "RM_X_ITEM", "subject": "RM_Chittik_n", "class": "art", "decision": "ACCEPT",
         "judge_keys": ("opus",), "art": True}
    d.update(kw)
    return d


# ---------------------------------------------------------------------------------------------- F1 ------
def f1_names():
    bad = ["cost_9", "price_1.5", "9500", "abcdefghijkmnpqrstuvwxyz2345", "RM_cost_9", "tok_45000"]
    got = {b: C.name_problem(b) for b in bad}
    good = ["RM_Chittik_n", "RM_AlienTree__AB_OcularTreeA", "RM_HoseFreeEnd_Mouth__R1b", "live_round2_visuals"]
    okg = {g: C.name_problem(g) for g in good}
    return all(got.values()) and not any(okg.values()), "bad %s good %s" % (got, okg)


def f1_queue_kind_row():
    q = BL.project_queue("BENCH", [("NEXT", [item(kind="cost_9", row="9500"), item(id="BIOME_DECIDE_TWO_ROUTES",
                                                                                   kind="bug", row="12")])],
                         ids(KNOWN))
    page = BL.render_queue(q)
    return ("cost_9" not in page and "9500" not in page and "kind bug" in page and "row 12" in page
            and "kind other" in page and q.fields_withheld == 1), page


def f1_digest_subject_path():
    _p, page = digest([verdict(subject="cost_9", rel="infrastructure/state/delegated/2026-10-27/price_1.5.json")])
    return "cost_9" not in page and "price_1" not in page and "2026-10-27" in page, page


# ---------------------------------------------------------------------------------------------- F2 ------
def f2_case():
    return all(C.ident_problem(s) for s in ("sTeVeN", "SteVen_x", "LUKASREPORT")), "case/segmentation"


def f2_registry():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "slot_rules.json")
        json.dump({"accounts": {"jane_smith": {}}}, open(p, "w"))
        old = C.RULE_FILES
        C.RULE_FILES = (p,)
        try:
            a = C.ident_problem("jane_smith_report") and C.ident_problem("JaneSmith")
            json.dump({"accounts": {"jane_smith": {}, "bertrand": {}}}, open(p, "w"))
            os.utime(p, (1, 2_000_000_000))
            b = bool(C.ident_problem("bertrand"))
            open(p, "w").write("{not json")
            os.utime(p, (1, 2_000_000_100))
            try:
                C.account_names()
                c = False
            except C.RegistryUnavailable:
                c = True
        finally:
            C.RULE_FILES = old
    return bool(a) and b and c, "multi-part %s refresh %s fail-closed %s" % (bool(a), b, c)


# ---------------------------------------------------------------------------------------------- F3 ------
def f3_note_sha():
    notes = [{"event": "note", "seat": "BENCH", "ts": "2026-10-27T05:00:00Z",
              "text": "key ab12cd34ef56ab78 and real abcdef0123 and 1234567890123456789012345678901234567890"}]
    page = BL.render_item(BL.project_item(item(), notes, [], ids(KNOWN), resolve=resolver()))
    # allowlist renderer: a resolved sha shows as its handle, never raw; the handle map (Operations') holds it
    return ("ab12cd34ef56" not in page and "123456789012" not in page and "abcdef0123" not in page
            and handled(page, "sha", "abcdef012345")), page


def f3_digest_shas():
    raw = [{"source": "ledger", "t": T0, "why": "delegated: scope", "id": "PIPE_ELBOW_FIX_SEAM_JOGS",
            "event": "close", "seat": "BENCH", "sha": "1" * 40},
           {"source": "marks", "t": T0, "type": "live", "reason": "archive", "id": "ab12" * 5, "sha": "cd" * 32,
            "rel": "Mods/X/Textures/a.png"},
           {"source": "commit", "t": T0, "sha": SHA_A, "class": "scope"}]
    _p, page = digest(raw)
    return ("111111111111" not in page and "cdcdcdcdcdcd" not in page and "ab12ab12" not in page
            and "abcdef012345" not in page and handled(page, "git", "abcdef012345")
            and not any(h["value"][:12] in ("111111111111", "cdcdcdcdcdcd") for h in page.handles.values())), page


def f3_no_resolver():
    _p, page = digest([{"source": "commit", "t": T0, "sha": SHA_A, "class": "scope"}], resolve=None)
    return "abcdef012345" not in page and not page.handles, page


# ---------------------------------------------------------------------------------------------- F4 ------
def f4_prefix():
    notes = [{"event": "note", "seat": "BENCH", "ts": "2026-10-27T05:00:00Z", "text": "quota 93% left"}]
    try:
        BL.project_item(item(), notes, [], ids(KNOWN), category="quota 93", resolve=resolver())
        refused = False
    except ValueError:
        refused = True
    notes.append({"event": "note", "seat": "BENCH", "ts": "2026-10-27T05:00:00Z", "text": "REPLAN REQUEST: x"})
    p = BL.project_item(item(), notes, [], ids(KNOWN), category="REPLAN REQUEST", resolve=resolver())
    return refused and p.notes_matching == 1, "refused %s matching %s" % (refused, p.notes_matching)


# ---------------------------------------------------------------------------------------------- F5 ------
def f5_unavailable():
    raw = [{"source": "ledger", "t": T0, "why": "delegated: scope", "id": "PIPE_ELBOW_FIX_SEAM_JOGS",
            "event": "close", "seat": "BENCH"}, verdict()]
    p, page = digest(raw, ident=None)
    held = sum(s.withheld for s in p.sources)
    return "PIPE_ELBOW" not in page and "RM_Chittik" not in page and held == 2, page


def f5_hidden_everywhere():
    raw = [verdict(item=None, subject="SAFE_LOOKING_HIDDEN"),
           verdict(item=None, subject="RM_Ok", rel="infrastructure/state/delegated/2026-10-27/SAFE_LOOKING_HIDDEN.json")]
    _p, page = digest(raw, ident=ids(KNOWN, {"SAFE_LOOKING_HIDDEN"}))
    return "SAFE_LOOKING_HIDDEN" not in page, page


def f5_digest_load():
    import delegated_digest as D
    from rimflow import model
    orig = model.read
    model.read = lambda *a, **k: (_ for _ in ()).throw(OSError("no ledger"))
    try:
        r = D._load_ledger()
    finally:
        model.read = orig
    return r[0] is None and r[1] is None, repr(r)[:80]


# ---------------------------------------------------------------------------------------------- F6 ------
def f6_note():
    b = {"role": "Conductor", "outcome": "completed", "mode": "quick", "unit": "rm-role-conductor-123456789012"}
    t = C.note_text(b)
    m = BL.project_note(b)
    forged = "dispatcher: Conductor quick run rm-role-conductor-123456789012: completed"
    return (t is not None and "rm-role" not in t and "123456789012" not in t and BL.render_note(m) == t
            and not C.is_note_text(forged)), t


# ---------------------------------------------------------------------------------------------- F7 ------
def f7_closed():
    import pydantic
    q = BL.project_queue("BENCH", [("NEXT", [item()])], ids(KNOWN))
    tries = []
    for how, mk in (("copy", lambda: q.copy(update={"withheld": 45000})),
                    ("base construct", lambda: pydantic.BaseModel.model_construct.__func__(
                        BL.BlindQueue, seat="BENCH", withheld=45000, fields_withheld=0, sections=())),
                    ("ctx", lambda: BL.BlindQueue.model_validate(dict(q.model_dump(), withheld=45000),
                                                                 context=dict(BL._CTX)) if hasattr(BL, "_CTX")
                     else None)):
        try:
            m = mk()
            if m is None:
                tries.append((how, True))
                continue
            BL.render_queue(m)
            tries.append((how, False))
        except Exception:  # noqa: BLE001
            tries.append((how, True))
    q2 = BL.project_queue("BENCH", [("NEXT", [item()])], ids(KNOWN))
    q2.__dict__["withheld"] = 45000
    try:
        BL.render_queue(q2)
        tries.append(("dict", False))
    except Exception:  # noqa: BLE001
        tries.append(("dict", True))
    return all(ok for _h, ok in tries), tries


# ---------------------------------------------------------------------------------------------- F8-14 ---
def _dd():
    import delegated_digest as D
    return D


def _rec(iid, h):
    t = T0 + dt.timedelta(hours=h)
    return {"seat": "BENCH", "event": "close", "id": iid, "why": "delegated: scope", "ts": D_iso(t)}


def D_iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _src(D, evs, known):
    reads = D.gather(evs, "/nonexistent", "/nonexistent/d", "/nonexistent/x.jsonl", added={}, commits=[],
                     art_events=[])
    return reads, ids(known), resolver()


def _args(tmp, date, *extra, cut=None):
    a = ["--date", date, "--state", os.path.join(tmp, "state.json"), "--out-dir", os.path.join(tmp, "out"),
         "--errors", os.path.join(tmp, "ops", "errors.log")]
    return a + (["--cut", cut] if cut else []) + list(extra)


def f8_reconcile_all():
    D = _dd()
    with tempfile.TemporaryDirectory() as tmp:
        ev = [_rec("A_ONE", 1)]
        D.main(_args(tmp, "2026-10-27", cut=D_iso(T0 + dt.timedelta(hours=2))), sources=_src(D, ev, ["A_ONE", "B_TWO"]))
        st = json.load(open(os.path.join(tmp, "state.json")))
        st["digests"]["2026-10-27"]["complete"] = False            # died after the page, before completion
        json.dump(st, open(os.path.join(tmp, "state.json"), "w"))
        ev2 = ev + [_rec("B_TWO", 30)]
        D.main(_args(tmp, "2026-10-28", cut=D_iso(T0 + dt.timedelta(hours=40))),
               sources=_src(D, ev2, ["A_ONE", "B_TWO"]))
        p = open(os.path.join(tmp, "out", "delegated_digest_2026-10-28.md")).read()
        return "A_ONE" not in p and "B_TWO" in p, p[-300:]


def f9_force_incomplete():
    D = _dd()
    with tempfile.TemporaryDirectory() as tmp:
        ev = [_rec("A_ONE", 1)]
        cut = D_iso(T0 + dt.timedelta(hours=2))
        D.main(_args(tmp, "2026-10-27", cut=cut), sources=_src(D, ev, ["A_ONE"]))
        before = open(os.path.join(tmp, "out", "delegated_digest_2026-10-27.md")).read()
        reads, i, r = _src(D, None, ["A_ONE"])                     # the ledger does not read now
        try:
            D.main(_args(tmp, "2026-10-27", "--force", cut=cut), sources=(reads, i, r))
        except Exception:  # noqa: BLE001 - a refusal is the fix
            pass
        after = open(os.path.join(tmp, "out", "delegated_digest_2026-10-27.md")).read()
        st = json.load(open(os.path.join(tmp, "state.json")))
        return after == before and st["digests"]["2026-10-27"]["seen"]["ledger"], "page/seen replaced"


def f10_dry_fail():
    D = _dd()
    with tempfile.TemporaryDirectory() as tmp:
        prod, dry = os.path.join(tmp, "prod"), os.path.join(tmp, "dry")
        o = (D.OUT_DIR, D.DRY_DIR)
        D.OUT_DIR, D.DRY_DIR = prod, dry
        try:
            D.main(["--pre-launch", "--dry-run", "--since", "invalid", "--date", "2026-10-27", "--state",
                    os.path.join(tmp, "s.json"), "--errors", os.path.join(tmp, "e.log")], sources=({}, None, None))
            D.main(["--pre-launch", "--dry-run", "--out-dir", prod, "--date", "2026-10-27", "--state",
                    os.path.join(tmp, "s.json"), "--errors", os.path.join(tmp, "e.log")], sources=({}, None, None))
        finally:
            D.OUT_DIR, D.DRY_DIR = o
        return not os.path.exists(os.path.join(prod, "delegated_digest_2026-10-27.FAILED.md")), "prod marker"


def f11_complete_shortcut():
    D = _dd()
    with tempfile.TemporaryDirectory() as tmp:
        ev = [_rec("A_ONE", 1)]
        cut = D_iso(T0 + dt.timedelta(hours=2))
        D.main(_args(tmp, "2026-10-27", cut=cut), sources=_src(D, ev, ["A_ONE"]))
        page = os.path.join(tmp, "out", "delegated_digest_2026-10-27.md")
        os.remove(page)
        failed = os.path.join(tmp, "out", "delegated_digest_2026-10-27.FAILED.md")
        open(failed, "w").write("stale")
        D.main(_args(tmp, "2026-10-27", cut=cut), sources=_src(D, ev, ["A_ONE"]))
        return os.path.exists(page) and not os.path.exists(failed), "page %s failed %s" % (
            os.path.exists(page), os.path.exists(failed))


def f12_errors_dest():
    D = _dd()
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "out", "delegated_digest_2026-10-26.md")
        os.makedirs(os.path.dirname(target))
        open(target, "w").write("page\n")
        D.main(["--pre-launch", "--date", "steven", "--errors", target, "--state", os.path.join(tmp, "s.json"),
                "--out-dir", os.path.join(tmp, "out")], sources=({}, None, None))
        return open(target).read() == "page\n", "the error log was written into a page"


def f13_state():
    D = _dd()
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, s in enumerate(({"schema": "other/9", "digests": {}}, {"schema": D.STATE_SCHEMA, "floor": "garbage",
                                                                      "digests": {}},
                               {"last_cut": "not a time"}, {"schema": D.STATE_SCHEMA, "floor": None, "digests": []})):
            p = os.path.join(tmp, "s%d.json" % i)
            json.dump(s, open(p, "w"))
            try:
                D.load_state(p)
                bad.append(i)
            except ValueError:
                pass
    return not bad, "accepted %s" % bad


def f14_unmeasured():
    status = {s: {"state": "unmeasured", "fault": "unreadable", "malformed": 0} for s in BL.SOURCES}
    _p, page = digest([], status=status)
    return "No delegated record in this window" not in page and "UNMEASURED" in page.split("|")[0], page[:600]


# ---------------------------------------------------------------------------------------------- F15/17 --
def f15_pick():
    p, _page = digest([{"source": "commit", "t": T0, "sha": SHA_A, "class": "scope — choose route B"}])
    r = p.records[0]
    return r.decision == "PICK" and r.pick == "B" and r.cls == "scope", (r.decision, r.pick, r.cls)


def f17_counted():
    raw = [{"source": "ledger", "t": T0, "why": "delegated: scope", "id": "PIPE_ELBOW_FIX_SEAM_JOGS",
            "event": "close", "seat": "BENCH", "sha": "1" * 40}]
    p, _ = digest(raw)
    led = [s for s in p.sources if s.source == "ledger"][0]
    pi = BL.project_item(item(closed_sha="ff" * 20), [], [], ids(KNOWN), resolve=resolver())
    return led.fields_withheld == 1 and pi.fields_withheld == 1, (led.fields_withheld, pi.fields_withheld)


# ---------------------------------------------------------------------------------------------- round 2 -
# gpt_review_blind_harden_r1_2026-10-27.md: three HIGH and three MED findings, one check each.
def r1_registry_names():
    vs = [verdict(subject="cost_nine", rel="infrastructure/state/delegated/2026-10-27/cost_nine.json"),
          verdict(subject="swordfish", rel="infrastructure/state/delegated/2026-10-27/swordfish.json"),
          verdict(subject="RM_Chittik_cost_nine", rel="infrastructure/state/delegated/2026-10-27/"
                                                      "RM_Chittik__cost_nine.json"),
          verdict(subject="RM_Chittik_n", rel="infrastructure/state/delegated/2026-10-27/RM_Chittik__r2.json")]
    _p, page = digest(vs)
    vals = " ".join(h["value"] for h in page.handles.values())      # the path now rides in the handle map only
    return ("cost" not in page and "nine" not in page and "swordfish" not in page and "RM_Chittik_n" not in page
            and "RM_Chittik__r2" not in page and "RM_Chittik__r2.json" in vals and "cost" not in vals
            and "swordfish" not in vals and "RM_Chittik" in page), page


def r1_short_dotted_accounts():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "slot_rules.json")
        json.dump({"accounts": {"amy": {}, "jane.smith": {}}}, open(p, "w"))
        old = C.RULE_FILES
        C.RULE_FILES = (p,)
        try:
            hit = {s: bool(C.ident_problem(s)) for s in ("a_m_y", "AMy", "x_amy_report", "Jane_Smith", "JANESMITH")}
            miss = {s: bool(C.ident_problem(s)) for s in ("dreamy", "RM_Chittik")}
            raised = []
            for i, bad in enumerate(({"accounts": ["amy"]}, {"lent_accounts": "amy"}, {"accounts": {"..": {}}})):
                json.dump(bad, open(p, "w"))
                os.utime(p, (1, 2_000_000_000 + i * 10))
                try:
                    C.account_names()
                except C.RegistryUnavailable:
                    raised.append(i)
        finally:
            C.RULE_FILES = old
    return all(hit.values()) and not any(miss.values()) and raised == [0, 1, 2], (hit, miss, raised)


def r1_shadowed_dump():
    p = BL.project_item(item(), [], [], ids(KNOWN), resolve=resolver())
    saved = p.model_dump_json(by_alias=True)
    p.__dict__["model_dump_json"] = lambda **kw: saved
    p.__dict__["id"] = "cost_9"
    try:
        page = BL.render_item(p)
    except Exception:  # noqa: BLE001 - refusing is also a pass
        return True, "refused"
    return "cost_9" not in page and "PIPE_ELBOW_FIX_SEAM_JOGS" in page, page[:300]


def r1_unlistable_verdicts():
    D = _dd()
    with tempfile.TemporaryDirectory() as tmp:
        dd = os.path.join(tmp, "delegated")
        sub = os.path.join(dd, "2026-10-27")
        os.makedirs(sub)
        json.dump({"subject": "RM_Chittik"}, open(os.path.join(sub, "RM_Chittik__r1.json"), "w"))
        ok_read = D.verdict_read(root=tmp, ddir=dd, added={})
        os.chmod(sub, 0)
        try:
            if os.access(sub, os.R_OK):          # running as root: the instrument cannot make it unlistable
                return False, "instrument: chmod 0 did not block listing (root?)"
            r = D.verdict_read(root=tmp, ddir=dd, added={})
        finally:
            os.chmod(sub, 0o755)
    return (ok_read["state"] == "measured" and len(ok_read["items"]) == 1 and r["state"] == "unmeasured"
            and not r["items"]), (ok_read["state"], len(ok_read["items"]), r["state"])


def r1_state_complete():
    D = _dd()
    good = {"floor": None, "cut": "2026-10-27T06:00:00Z", "complete": True, "page_sha256": "a" * 64,
            "seen": {"ledger": ["Lx"]}, "sources": {s: "measured" for s in D.SOURCES},
            "out": "/tmp/delegated_digest_2026-10-27.md"}
    bad = [dict(good, seen={"ledger": [{}]}), {k: v for k, v in good.items() if k != "sources"},
           dict(good, sources=dict(good["sources"], ledger="zero")), dict(good, out=7),
           dict(good, page_sha256="xyz"), dict(good, seen={"nonsense": []}), dict(good, extra=1)]
    accepted = []
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "s.json")
        json.dump({"schema": D.STATE_SCHEMA, "floor": None, "digests": {"2026-10-27": good}}, open(p, "w"))
        D.load_state(p)
        for i, e in enumerate(bad):
            json.dump({"schema": D.STATE_SCHEMA, "floor": None, "digests": {"2026-10-27": e}}, open(p, "w"))
            try:
                D.load_state(p)
                accepted.append(i)
            except ValueError:
                pass
    return not accepted, "accepted %s" % accepted


def r1_note_sha_counted():
    notes = [{"event": "note", "seat": "BENCH", "ts": "2026-10-27T05:00:00Z",
              "text": "see deadbeef1234 and abcdef0123 and deadbeef1234 again"}]
    pi = BL.project_item(item(), notes, [], ids(KNOWN), resolve=resolver())
    return pi.fields_withheld == 1 and pi.notes[0].shas == (SHA_A,), (pi.fields_withheld, pi.notes[0].shas)


def r2_registry_model_and_null():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "slot_rules.json")
        json.dump({"accounts": {"opus": {}}}, open(p, "w"))
        old = C.RULE_FILES
        C.RULE_FILES = (p,)
        try:
            ident = bool(C.ident_problem("OPUS_REVIEW")) and bool(C.name_problem("OPUS_REVIEW"))
            try:
                _pg, page = digest([verdict(item=None, subject="OPUS_REVIEW", rel=None)],
                                   ident=ids(KNOWN + ("OPUS_REVIEW",)))
                shown = "OPUS_REVIEW" in page
            except Exception:  # noqa: BLE001 - refusing the page is also a pass
                shown = False
            raised = []
            for i, bad in enumerate(({"accounts": None}, {"lent_accounts": None})):
                json.dump(bad, open(p, "w"))
                os.utime(p, (1, 2_000_000_500 + i * 10))
                try:
                    C.account_names()
                except C.RegistryUnavailable:
                    raised.append(i)
        finally:
            C.RULE_FILES = old
    plain = not C.ident_problem("judge_opus_pass")      # with no such registry key, a model name alone is legal
    return ident and not shown and raised == [0, 1] and plain, (ident, shown, raised, plain)


def r3_evidence_root_account():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "slot_rules.json")
        json.dump({"accounts": {"luke": {}}}, open(p, "w"))
        old = C.RULE_FILES
        C.RULE_FILES = (p,)
        try:
            prob = C.evidence_problem("infrastructure/state/delegated/2026-10-27/")
            try:
                pg, page = digest([verdict(item=None, subject=None, judge_keys=(),
                                           rel="infrastructure/state/delegated/2026-10-27/")])
                shown, counted = "luke" in page.lower(), pg.fields_withheld if hasattr(pg, "fields_withheld") else \
                    sum(s.fields_withheld for s in pg.sources)
            except Exception:  # noqa: BLE001 - refusing the page is also a pass
                shown, counted = False, 1
        finally:
            C.RULE_FILES = old
    base = C.evidence_problem("infrastructure/state/delegated/2026-10-27/")   # the real registry: shows
    return prob == "account_name" and not shown and counted >= 1 and base is None, (prob, shown, counted, base)


class _Registry:
    """A temporary account registry for one check (restores RULE_FILES on exit)."""
    def __init__(self, accounts):
        self.accounts = accounts

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        p = os.path.join(self.tmp.name, "slot_rules.json")
        with open(p, "w") as f:
            json.dump({"accounts": self.accounts}, f)
        self.old, C.RULE_FILES = C.RULE_FILES, (p,)
        return self

    def __exit__(self, *a):
        C.RULE_FILES = self.old
        self.tmp.cleanup()


def r4_sha_account():
    """GPT r4 H1: a resolved sha whose shown prefix is a registry account key never shows; the drop is counted;
    the final guard refuses a labelled sha that names an account."""
    with _Registry({SHA_A[:12]: {}}):
        try:
            pg, page = digest([{"source": "commit", "t": T0, "sha": SHA_A, "class": "scope"}])
            shown = SHA_A[:12] in page
            counted = sum(s.fields_withheld for s in pg.sources) if hasattr(pg, "sources") else pg.fields_withheld
        except Exception:  # noqa: BLE001 - refusing the page is also a pass
            shown, counted = False, 1
        guard = BL.page_problem("git %s" % SHA_A[:12])
    _p, base = digest([{"source": "commit", "t": T0, "sha": SHA_A, "class": "scope"}])
    # base (real registry): the commit shows as a handle, its sha never raw (allowlist renderer)
    return (not shown and counted >= 1 and guard is not None and SHA_A[:12] not in base
            and handled(base, "git", SHA_A[:12])), repr((shown, counted, guard))


def r4_note_account():
    """GPT r4 H2: a stdlib note whose text names a registry account renders nothing, and is_note_text refuses it;
    an unavailable registry fails closed."""
    b = {"role": "Conductor", "outcome": "completed"}
    with _Registry({"conductor": {}}):
        t, ok = C.note_text(b), C.is_note_text("dispatcher: Conductor: completed")
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "slot_rules.json")
        with open(p, "w") as f:
            f.write("{not json")
        old, C.RULE_FILES = C.RULE_FILES, (p,)
        try:
            u = C.note_text(b)
        except C.RegistryUnavailable:
            u = None
        finally:
            C.RULE_FILES = old
    base = C.note_text(b)
    return t is None and not ok and u is None and base == "dispatcher: Conductor: completed", repr((t, ok, u, base))


CHECKS = [("F1 a figure or key in a name is refused by the strict name grammar", f1_names),
          ("F1 queue kind is a closed enum and row a 1-2 digit number", f1_queue_kind_row),
          ("F1 digest subject and evidence file name pass the strict grammar or drop", f1_digest_subject_path),
          ("F2 account names match across case and camel segmentation", f2_case),
          ("F2 registry: multi-part names, refreshed on change, fail closed when unreadable", f2_registry),
          ("F3 a note's sha shows only when it resolves to a real commit", f3_note_sha),
          ("F3 digest: an unresolved or art-ledger sha never shows", f3_digest_shas),
          ("F3 no resolver: no sha shows", f3_no_resolver),
          ("F4 an arbitrary prefix is refused; a closed category counts", f4_prefix),
          ("F5 identity unavailable withholds every record with a reference", f5_unavailable),
          ("F5 a hidden id in subject or path is withheld", f5_hidden_everywhere),
          ("F5 the digest's ledger failure reports identity unavailable", f5_digest_load),
          ("F6 a blind note never carries the unit; is_note_text refuses it", f6_note),
          ("F7 a model made or changed outside a projection never renders", f7_closed),
          ("F8 every pending entry is reconciled before the window", f8_reconcile_all),
          ("F9 a force rebuild never replaces a page with an incomplete one", f9_force_incomplete),
          ("F10 a failed dry run never writes a production FAILED marker", f10_dry_fail),
          ("F11 a completed date whose page is gone is rebuilt; a stale marker goes", f11_complete_shortcut),
          ("F12 the error log never lands in a page", f12_errors_dest),
          ("F13 damaged state is refused, never a first run", f13_state),
          ("F14 all sources unmeasured never reads as a measured zero", f14_unmeasured),
          ("F15 a commit line's pick reaches the closed fields", f15_pick),
          ("F17 a refused sha is counted as a withheld field", f17_counted),
          ("R1-H1 a subject or file stem shows only as a registered defName or known id", r1_registry_names),
          ("R4-H1 a resolved sha naming an account never shows; the guard refuses it", r4_sha_account),
          ("R4-H2 a stdlib note naming an account renders nothing; is_note_text refuses it", r4_note_account),
          ("R1-H2 short, split and dotted account names are refused; a malformed registry raises",
           r1_short_dotted_accounts),
          ("R1-H3 a shadowed model_dump_json plus a __dict__ edit never renders", r1_shadowed_dump),
          ("R1-M an unlistable verdict directory reads UNMEASURED, never zero", r1_unlistable_verdicts),
          ("R1-M a state entry is validated completely", r1_state_complete),
          ("R1-M an unresolved note sha is counted once per distinct candidate", r1_note_sha_counted),
          ("R2-H a registry account named like a model is still an account; a null map raises",
           r2_registry_model_and_null),
          ("R3-H an account in the displayed evidence root drops the path, counted", r3_evidence_root_account)]


def main():
    for name, fn in CHECKS:
        check(name, fn)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
