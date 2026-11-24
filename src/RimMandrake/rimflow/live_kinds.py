#!/usr/bin/env python3
"""live_kinds.py -- what the kind of a live scene and the outcomes of its runs mean at the Stage 6 exit (owner, 2026-11-23,
design/RimMandrake/standing_rulings.md §Live tests have three kinds). Pure: it reads rows and one test of the table, and
touches no file. Page: design/specs/2026-11-23-live-kinds-exit-reader/boundary.md. Tests: selftest_live_kinds.py.

A check with no tag whose rows carry no `outcome` and no `forbidden` has no reading here (`reading` -> None): the exit
reads it by its verdict and class, as it did before the kinds."""
import re

SUCCESS, MOD_FAILURE, RANDOM_MISS = "SUCCESS", "MOD FAILURE", "RANDOM MISS"
ENVIRONMENT, APPARATUS, UNRESOLVED, NO_LOOK = "ENVIRONMENT FAULT", "APPARATUS FAULT", "UNRESOLVED", "COULD NOT LOOK"
OUTCOMES = (SUCCESS, MOD_FAILURE, RANDOM_MISS, ENVIRONMENT, APPARATUS, UNRESOLVED, NO_LOOK)
REFUSED = "REFUSED"         # not an outcome: the row's words cannot be read, and the exit names them
SPOILING = (ENVIRONMENT, APPARATUS, NO_LOOK)
NO_BUDGET = (APPARATUS, NO_LOOK)    # our own fault or no reading spends no trial (standing_rulings, No trial is spent)
WRONG = ("HARNESS", "SITE")
NOTHING = ("NONE", "NO", "N/A", "NOTHING")      # a `forbidden` entry that says nothing was seen
WHY_WORDS = 6               # the word floor of `classed.why`; its danger and evidence: the page, LIMITS
NEEDED, GUESS = CALLS = ("needed", "guess")     # the Conductor's call on a scene short of its X of Y
HOLDS = ("spoiled", "inconclusive", "unresolved", "refused", "tag")    # the line counts that only this module gives

STEWARD_RULE = (
    "- The kinds and outcomes (owner, 2026-11-23; standing_rulings.md §Live tests have three kinds): a line that reads "
    "`spoiled` (every run was spoiled), `inconclusive` (a kind B budget spent with no SUCCESS) or `unresolved` (a run "
    "nobody has classed) sends the mod to no earlier stage and gets no mod item. A `spoiled` scene runs again in the "
    "next visit (--to in_game). For an INCONCLUSIVE scene with no X of Y, the scene runs again with a budget that the "
    "Conductor sets, or the Conductor decides: head the line in your note `FOR THE CONDUCTOR:`. A scene that ended short "
    "of its X of Y waits for the Conductor's call: the tick has asked, so open no visit only for that scene, and never "
    "edit its `x_of_y` (the Conductor's command is `shortfall.py call`). When the call is that the mod needs X of Y, the "
    "line reads MOD FAILURE: route it as any mod wrong line. An UNRESOLVED run is classed by whoever reads "
    "its evidence: add to that row `classed`: `{\"outcome\": <one of the other six>, \"why\": <six words at least>, "
    "\"by\": <your unit>}` (and `spoiled_by` for an ENVIRONMENT FAULT); class it only on evidence. A `refused` or `tag` "
    "line is a fault of form in the row or the table: repair the words, never the reading.\n"
    "- A raid scene that reads PAUSED (`paused_raids` of the exit) is no line: file nothing for it and send nothing back for it. "
    "Its open bars go in the walk brief and hold only the version's pass (standing_rulings.md §The cheapest test that decides "
    "the bar).")


def norm(word):
    """-> the word as the rule writes it: upper case, one space for each run of spaces, `_` or `-`."""
    return re.sub(r"[\s_-]+", " ", str(word if word is not None else "")).strip().upper()


def _text(v):
    return bool(str(v).strip()) if v not in (None, False, [], {}) else False


def kind(spec):
    """-> "A", "B", "C", or the table's own unknown word. Absent is A."""
    return norm((spec or {}).get("test_kind")) or "A"


def x_of_y(spec):
    """-> (X, Y) for a kind B scene that is random by design and says so usably, else None."""
    v = (spec or {}).get("x_of_y")
    if kind(spec) != "B" or not isinstance(v, (list, tuple)) or len(v) != 2:
        return None
    if any(isinstance(i, bool) or not isinstance(i, int) for i in v) or not 1 <= v[0] <= v[1]:
        return None
    return v[0], v[1]


def call_of(spec):
    """-> the Conductor's standing call that the mod needs this scene's X of Y (shortfall.py writes it), or None. The last
    usable entry on the scene's present [X, Y] speaks."""
    xy, v = x_of_y(spec), (spec or {}).get("x_of_y_calls")
    mine = [c for c in v if isinstance(c, dict) and xy and list(c.get("x_of_y") or []) == list(xy)
            and c.get("call") in CALLS and len(str(c.get("why") or "").split()) >= WHY_WORDS and _text(c.get("by"))
            ] if isinstance(v, list) else []
    return mine[-1] if mine and mine[-1]["call"] == NEEDED else None


def budget(spec):
    """-> the budgeted runs of a kind B scene, or None when the table gives no usable number (x_of_y's Y stands in only
    for a budget that is not there)."""
    b = (spec or {}).get("budget")
    if b is None and x_of_y(spec):
        return x_of_y(spec)[1]
    return b if isinstance(b, int) and not isinstance(b, bool) and b >= 1 else None


def tag_flaws(spec):
    """-> [why] the tag of one test cannot be used; [] when it can."""
    k = kind(spec)
    if k not in ("A", "B", "C"):
        return ["its tag test_kind %r is none of A, B, C" % (spec or {}).get("test_kind")]
    out = []
    if k != "A" and not _text((spec or {}).get("tag_evidence")):
        out.append("its tag %s carries no tag_evidence (%s)" % (k, "what spoils the run, what was tried to control each "
                   "thing, and why that was not enough" if k == "B" else "the symptom, how often it was seen in how many "
                   "opportunities, and the trace"))
    if (spec or {}).get("x_of_y") is not None and x_of_y(spec) is None:
        out.append("its tag's x_of_y %r is not [X, Y] with 1 <= X <= Y on a kind B scene" % ((spec or {}).get("x_of_y"),))
    if k == "B" and budget(spec) is None:
        out.append("its tag B carries no usable budget (a whole number of runs, written before the first run)")
    return out


def _in_game(t):
    return isinstance(t, dict) and str(t.get("kind", "")).startswith("live") and str(t.get("stage")) == "6"


def table_flaws(tt):
    """-> {check id or bar id: [why]}: the tags of the table's stage-6 in-game checks that cannot be used, and the bars
    that a kind C tag would take out of the exit."""
    tests = (tt or {}).get("tests") or {}
    live = {t: x for t, x in tests.items() if _in_game(x)}
    out = {t: f for t, f in ((t, tag_flaws(x)) for t, x in live.items()) if f}
    hunts = {t for t, x in live.items() if kind(x) == "C"}
    for b in (tt or {}).get("bars") or []:
        mine = [t for t in (b.get("decides") or []) if t in live] if isinstance(b, dict) else []
        if mine and all(t in hunts for t in mine):
            out["bar %s" % b.get("id")] = ["its only in-game decider(s) %s are tagged kind C, and a hunt is never part of "
                                           "the exit: a tag does not take a bar out of it" % ", ".join(mine)]
    return out


def _forbidden(r):
    """-> (effects seen, why unreadable or None)."""
    v = r.get("forbidden")
    if v is None or v == "":
        return [], None
    if isinstance(v, str):
        return [v] if norm(v) and norm(v) not in NOTHING else [], None
    if isinstance(v, (list, tuple)):
        return [str(x) for x in v if _text(x) and norm(x) not in NOTHING], None
    return [], "its `forbidden` %r is no list of the effects seen" % (v,)


def outcome(r, spec=None):
    """-> (word, why): what one row says. word None is an old row (no outcome, no forbidden effect): its verdict and class
    speak. REFUSED: the words cannot be read, why says which. UNRESOLVED carries why when the row did not say it itself."""
    if not isinstance(r, dict):
        return None, None
    seen, bad = _forbidden(r)
    if seen:
        return MOD_FAILURE, "forbidden effect: %s" % "; ".join(seen)
    raw = norm(r.get("outcome"))
    if bad:
        return REFUSED, bad
    if not raw:
        return None, None
    word, why = _word(raw, r, spec, r)
    cl = r.get("classed")
    if word == UNRESOLVED and isinstance(cl, dict):
        if norm(cl.get("outcome")) != UNRESOLVED and len(str(cl.get("why") or "").split()) >= WHY_WORDS and _text(
                cl.get("by")):
            return _word(norm(cl.get("outcome")), r, spec, dict(r, **{k: v for k, v in cl.items() if k == "spoiled_by"}))
        why = "its `classed` needs an outcome of the other six, a why of %d words at least, and a by" % WHY_WORDS
    return word, why


def _word(raw, r, spec, rec):
    if raw not in OUTCOMES:
        return REFUSED, "its outcome %r is none of the seven (%s)" % (raw, ", ".join(OUTCOMES))
    if raw in SPOILING and norm(r.get("class")) == "MOD":
        return UNRESOLVED, "outcome %s beside class MOD: if the mod could have spoiled the run, it is UNRESOLVED" % raw
    if raw == ENVIRONMENT and not _text(rec.get("spoiled_by")):
        return UNRESOLVED, "ENVIRONMENT FAULT with no `spoiled_by` (what spoiled the run, and the record that shows it)"
    if raw == RANDOM_MISS and not x_of_y(spec):
        return REFUSED, "outcome RANDOM MISS on a scene that is not random by design (a kind B tag with x_of_y)"
    if raw == SUCCESS and norm(r.get("verdict")) != "PASS":
        return REFUSED, "outcome SUCCESS beside verdict %s: the row contradicts itself" % (r.get("verdict") or "none")
    return raw, None


def spoiled(r):
    """True when the run speaks for nobody. An APPARATUS FAULT or COULD NOT LOOK row that says the check itself is wrong
    (class HARNESS or SITE, `repair`, `unrepaired`) is read as an old row is. A row voided as a system failure
    (`void_system`) is no reading, whatever its class."""
    if isinstance(r, dict) and r.get("void_system") is True:
        return True
    w = outcome(r)[0]
    if w == ENVIRONMENT:
        return True
    return w in SPOILING and norm(r.get("class")) not in WRONG and "repair" not in r and "unrepaired" not in r


def no_verdict(r):
    """True for a row that is no verdict about the mod: a spoiled run or a random miss (maturation_rescue.py)."""
    return spoiled(r) or (norm(r.get("outcome")) == RANDOM_MISS and not _forbidden(r)[0])


def later(old, new):
    """-> the deciding row of the two: the later one, except that a spoiled row never replaces one that is not."""
    return old if old is not None and spoiled(new) and not spoiled(old) else new


def as_old(r):
    """-> the row as the verdict-and-class reader must see it: a MOD FAILURE is a FAIL with class MOD."""
    return dict(r, verdict="FAIL", **{"class": "MOD"}) if outcome(r)[0] == MOD_FAILURE else r


def earlier_fail(r, spec=None):
    """-> True when a FAIL word on this row counts as a FAIL that a later PASS does not hide. A spoiled run, an allowed
    miss, and a row held by its own reading (UNRESOLVED, REFUSED) do not."""
    return not spoiled(r) and outcome(r, spec)[0] not in (RANDOM_MISS, UNRESOLVED, REFUSED)


def same_build(a, b):
    """True when two rows name one mod_sha (a short hash agrees with a long one it starts); two rows with none agree."""
    x, y = str((a or {}).get("mod_sha") or ""), str((b or {}).get("mod_sha") or "")
    return x.startswith(y) or y.startswith(x) if x and y else x == y


def _as_outcome(r, spec):
    """A row's outcome, an old row's read from its verdict and class (kind B only)."""
    w = outcome(r, spec)[0]
    if w is not None:
        return w
    v, c = norm(r.get("verdict")), norm(r.get("class"))
    return SUCCESS if v == "PASS" else MOD_FAILURE if c == "MOD" and v == "FAIL" else NO_LOOK


def reading(spec, runs):
    """runs: [(visit, row)], every row of one check up to the visit, in order. -> None (kind A, old rows only: the exit
    reads them as before), or {count: None | one of HOLDS | "pass" (kind B), why: [...], rows: the word for the exit's
    rows or None, use: the row that decides, mod: True when an earlier run of the same build is a MOD FAILURE, passes:
    the scene passes on its runs (holds aside), claim_free: the block's claim is not held against it, short: what ended
    short of the scene's X of Y, or None}."""
    runs = [(v, r) for v, r in runs or [] if isinstance(r, dict)]
    k = kind(spec)
    if not runs or (k == "A" and all(outcome(r, spec)[0] is None for _, r in runs)):
        return None
    pool = build_runs(runs, runs[-1][1]) if k == "B" and not tag_flaws(spec) else None
    deciding_rows = pool if pool is not None else [r for _, r in runs]
    d = None
    for r in deciding_rows:
        d = later(d, r)
    at = max(i for i, r in enumerate(deciding_rows) if r is d)
    word = _as_outcome if k == "B" else (lambda r, s: outcome(r, s)[0])
    out = {"count": None, "why": [], "rows": None, "use": d, "short": None, "claim_free": runs[-1][1] is not d or k == "B",
           "mod": any(i != at and word(r, spec) == MOD_FAILURE and same_build(r, d) for i, r in enumerate(deciding_rows)),
           "passes": norm(d.get("verdict")) == "PASS" and outcome(d, spec)[0] in (None, SUCCESS)}
    if pool is not None:
        _kind_b(spec, pool, out)
    elif spoiled(d):
        w = outcome(d, spec)[0]
        out.update(count="spoiled", rows="SPOILED", passes=False)
        out["why"].append("its last run was spoiled (%s%s) and no valid run stands: run that scene again" % (
            w, ": %s" % str(d.get("spoiled_by")) if w == ENVIRONMENT else ""))
    # a run that nobody classed, or whose words cannot be read, holds the scene under any later PASS, whatever its visit
    for word, cnt in ((UNRESOLVED, "unresolved"), (REFUSED, "refused")):
        for v, r in runs:
            w, why = outcome(r, spec)
            if w == word:
                out["count"], out["rows"] = cnt, word
                out["why"].append("a run of visit %s reads %s%s%s" % (
                    v, word, " (%s)" % why if why else "", ": it holds the pass until someone classes it (`classed`)"
                    if word == UNRESOLVED else ": repair the row's words"))
    if tag_flaws(spec):
        out["count"], out["rows"] = "tag", None       # the table's flaw is said once, by table_flaws
    return out


def build_runs(runs, last):
    """-> the rows of runs on the build of `last`, the scene's latest run. A kind B scene is judged on the build it last
    ran on: its deciding row, MOD FAILURE check and budget use this pool (rule: "on the same claim and build")."""
    return [r for _, r in runs if same_build(r, last)]


def _kind_b(spec, pool, out):
    """Fill out for a kind B scene from pool, its runs on one build."""
    words = [_as_outcome(r, spec) for r in pool]
    good = [r for r, w in zip(pool, words) if w == SUCCESS]
    d = out["use"]
    if outcome(d, spec)[0] == MOD_FAILURE or (not spoiled(d) and norm(d.get("class")) in WRONG
                                              and norm(d.get("verdict")) != "PASS"):
        return      # the mod failed, or the check is said wrong: the verdict and class speak
    spent, b = sum(w not in NO_BUDGET for w in words), budget(spec)
    xy = x_of_y(spec)
    if xy:
        valid = [w for w in words if w in (SUCCESS, RANDOM_MISS)][:xy[1]]
        got = valid.count(SUCCESS)
        ok, done = got >= xy[0], len(valid) >= xy[1] or spent >= b
        said = "%d success(es) in %d valid opportunity(ies), %d in %d needed" % (got, len(valid), xy[0], xy[1])
    else:
        ok, done = bool(good), spent >= b
        said = "no SUCCESS in %d of %d budgeted run(s)" % (spent, b)
    if ok:
        out.update(count="pass", use=good[-1], passes=True)
    elif done and xy:
        _short(spec, pool, out, {"x_of_y": list(xy), "got": got, "valid": len(valid), "spent": spent, "budget": b,
                                 "mod_sha": pool[-1].get("mod_sha"), "tag_evidence": (spec or {}).get("tag_evidence")}, said)
    elif done:
        out.update(count="inconclusive", rows="INCONCLUSIVE", passes=False)
        out["why"].append("INCONCLUSIVE (%s; %d of %d budgeted run(s) spent): never PASS and never FAIL; the scene runs "
                          "again with a budget the Conductor sets, or the Conductor decides" % (said, spent, b))
    else:
        out.update(count="spoiled", rows="SPOILED", passes=False)
        out["why"].append("kind B, %s: run that scene again (%d of %d budgeted run(s) left)" % (said, b - spent, b))


def _short(spec, pool, out, short, said):
    """The scene ended short of its X of Y: held for the Conductor's call, or MOD FAILURE when the call is that the mod
    needs X of Y (owner, 2026-11-23). A call that X was a guess changed x_of_y itself, so it is not seen here."""
    out["short"], c = short, call_of(spec)
    if c:
        d = out["use"] if any(r is out["use"] for r in pool) else pool[-1]
        out.update(use=dict(d, outcome=MOD_FAILURE, verdict="FAIL", **{"class": "MOD"}), passes=False)
        out["why"].append("MOD FAILURE: it ended short of its X of Y (%s), and the Conductor's call is that the mod needs X "
                          "of Y: %s" % (said, c["why"]))
        return
    out.update(count="inconclusive", rows="INCONCLUSIVE", passes=False)
    out["why"].append("INCONCLUSIVE (%s; %d of %d budgeted run(s) spent): never PASS and never FAIL; escalated, and held "
                      "until the Conductor's call is recorded: does the mod's function need X of Y, or was X a guess "
                      "(shortfall.py call)" % (said, short["spent"], short["budget"]))
