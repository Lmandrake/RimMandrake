#!/usr/bin/env python3
"""exam_retake.py -- after a coverage-judge refusal is repaired, re-run only the Cold Reader exam scenarios the repair
touched (item RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE; his card 2026-11-18 4:29 PM PST,
"Retake only what changed"). The order of the gates does not move: the exam runs first, and the coverage judge still
skips a tree whose exam does not pass (coverage_judge.plan, maturation_autonomy.exam_gate).

  record <dir>             write exam_reads.json, the read map of the exam that passes on the current tree
  plan   <dir> [--scenarios F]   what a retake re-runs now; writes exam_retake_plan.json
  carry  <dir> --fresh F   write the new exam.json: the fresh answers for the retaken scenarios, the rest carried

THE MAP. A Reader is shown sheet.md, tree.json and the scenario text (designer_exam.md step 4), so what a scenario
can have read is cut into units: one per leaf (the leaf's object in tree.json and every sheet line tagged with its id,
with the section it sits in) and one shared unit (the tree's own fields, coverage aside as tree_hash leaves it and the
floor's hash pin aside, since it pins concept_floor.json, a file no Reader is shown; the
leaves' order, and every untagged sheet line: his words, open, delegated, pruning). The order of the sheet's lines is
recorded beside them: a line added to, removed from or moved within one leaf's own lines is that leaf's change, and any
other reorder is read by every scenario. A scenario's reads are its expect_source leaf and
every leaf either Reader said it relied on, taken from the Readers' own answers when the exam passed, never from a
hand-kept list. Each unit's hash at that moment is recorded, so a later change is found by comparing hashes, not by
reading a diff or the old tree.

THE OUTCOMES, kept apart in every return value and every line printed:
  partial       some scenarios retaken, the rest carried forward (A1, A5)
  none_touched  looked: nothing any scenario read changed, so zero are re-run (A4)
  whole         the map could not tell, so the whole exam is retaken by designer_exam.md in full: no map, an
                unreadable map, a map of another exam, a leaf added or removed, a change to the shared unit or to
                a leaf every scenario reads, a changed leaf no scenario's reads cover, sheet lines reordered beyond
                the touched leaves' own lines (A2, A3). A partial retake is never guessed.
  cannot_run    the retake cannot run at all: the current tree.json or sheet.md cannot be read

A carried answer keeps, in exam.json `carried`, the exam it was answered in and the hashes it was answered against;
designer_stage.exam_errors refuses one whose scenario or any unit it read has changed since, so the gate checks the
carry instead of trusting it.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT          # noqa: E402

READS_FILE = "exam_reads.json"
PLAN_FILE = "exam_retake_plan.json"
SCHEMA = 3         # 2: the sheet's line order left the shared hash for its own record, sheet_order
#                    3: the floor's hash pin left the shared hash (PINS); a schema-2 map is still read (plan)
READ_SCHEMAS = (2, 3)
# fields of the tree that pin a file no Reader is shown (designer_exam.md step 4: sheet.md, tree.json and the scenario
# text): a re-pin changes nothing a scenario read. The floor's `ref` and `off` stay in the shared unit.
PINS = (("floor", "hash"),)
PARTIAL, NONE_TOUCHED, WHOLE, CANNOT_RUN = "partial", "none_touched", "whole", "cannot_run"
SCENARIO_KEYS = ("id", "text", "expect", "expect_source", "by")
TAGGED = re.compile(CT.BULLET + r"\s*\[(?:leaf|core):([A-Za-z0-9_]+)\]")


class Refused(Exception):
    pass


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _write(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, p)


def scenario_hash(s):
    """What a carried answer was given and scored against: the situation, its expectation and its source."""
    return CT.sha({k: s.get(k) for k in SCENARIO_KEYS}) if isinstance(s, dict) else None


def _leaf_id(name):
    n = CT.txt(name)
    return n[len("leaf:"):] if n.startswith("leaf:") else n


def units(d):
    """-> ({leaf id: hash}, shared hash, sheet order) of the current tree.json and sheet.md; the order is one
    [section, leaf id or None] per sheet line. OSError/ValueError when either cannot be read (the caller's
    cannot_run)."""
    return units_of(CT.load(d), d)


def legacy_shared(d, tree=None):
    """The schema-2 shared hash (the floor's hash pin inside it) of `tree` (default the current tree.json) and the
    current sheet.md: what a schema-2 map or a carried answer written before schema 3 recorded."""
    return units_of(CT.load(d) if tree is None else tree, d, legacy=True)[1]


def _unpinned(rest):
    out = dict(rest)
    for key, field in PINS:
        if isinstance(out.get(key), dict) and field in out[key]:
            out[key] = {k: v for k, v in out[key].items() if k != field}
    return out


def units_of(tree, d, legacy=False):
    """units() of a given tree object and d's sheet.md; `legacy` keeps the PINS in the shared hash (schema 2)."""
    if not isinstance(tree, dict) or not isinstance(tree.get("leaves"), list):
        raise ValueError("tree.json has no leaves list")
    leaves = {}
    for x in tree["leaves"]:
        if isinstance(x, dict) and isinstance(x.get("id"), str):
            if x["id"] in leaves:
                raise ValueError("tree.json names leaf %r twice" % x["id"])
            leaves[x["id"]] = x
    p = os.path.join(d, "sheet.md")
    if not os.path.isfile(p):
        raise OSError("no sheet.md")
    tagged, untagged, order = {k: [] for k in leaves}, [], []
    for section, lines in CT.parse_sheet(p).items():
        for ln in lines:
            m = TAGGED.match(ln)
            if m and m.group(1) in leaves:
                tagged[m.group(1)].append([section, ln.rstrip()])
                order.append([section, m.group(1)])
            else:
                untagged.append([section, ln.rstrip()])
                order.append([section, None])
    rest = {k: v for k, v in tree.items() if k not in ("leaves", "coverage")}
    if not legacy:
        rest = _unpinned(rest)
    # the order of the leaves and of the sheet's lines is read by every scenario (a rule may say "the earlier line
    # wins"): the leaves' order is in the shared unit, the sheet's is returned for order_moved
    return ({k: CT.sha({"leaf": leaves[k], "sheet": tagged[k]}) for k in leaves},
            CT.sha({"tree": rest, "sheet": untagged,
                    "leaf_order": [x.get("id") if isinstance(x, dict) else None for x in tree["leaves"]],
                    "other_entries": [x for x in tree["leaves"]
                                      if not (isinstance(x, dict) and isinstance(x.get("id"), str))]}),
            order)


def is_order(o):
    return isinstance(o, list) and all(isinstance(e, list) and len(e) == 2 and isinstance(e[0], str)
                                       and (e[1] is None or isinstance(e[1], str)) for e in o)


def order_moved(old, new, touched):
    """True when the sheet's lines moved relative to each other beyond the touched leaves' own lines: with every line of
    a touched leaf dropped, the two orders must be equal. A line added to or removed from a touched leaf is that leaf's
    change; a reorder of lines whose text did not change touches no leaf, so it is a change every scenario reads."""
    def keep(o):
        return [list(e) for e in o if e[1] not in touched]
    return keep(old) != keep(new)


def _answers(v, d, repo):
    """One Reader's answers in any shape the exams on disk use: a list of {id, verdict, leaf}, a dict {sid: {verdict,
    leaf}}, or a path to a JSON file holding {"verdicts": [...]}. -> {sid: (verdict, [leaf ids])}."""
    if isinstance(v, str):
        for base in (repo, d):
            p = os.path.join(base, v)
            if os.path.isfile(p):
                v = _read(p)
                break
        else:
            raise ValueError("answer file %r is not on disk" % v)
        v = v.get("verdicts") if isinstance(v, dict) else v
    rows = v.items() if isinstance(v, dict) else ((x.get("id") if isinstance(x, dict) else None, x) for x in
                                                   (v if isinstance(v, list) else []))
    out = {}
    for sid, a in rows:
        if not isinstance(a, dict):
            raise ValueError("an answer to %r is not an object with its verdict and leaf" % sid)
        lf = []
        for f in (a.get("leaf"), a.get("leaves")):
            lf += [x.strip() for x in f.split(",")] if isinstance(f, str) else f if isinstance(f, list) else []
        if any(not isinstance(x, str) for x in lf):
            raise ValueError("an answer to %r names a leaf that is not a string" % sid)
        if CT.txt(sid) in out:
            raise ValueError("one Reader answered %r twice; which answer it relied on cannot be told" % sid)
        out[CT.txt(sid)] = (CT.txt(a.get("verdict")).lower(), [_leaf_id(x) for x in lf if CT.txt(x)])
    return out


def _right(s, verdicts):
    want = CT.txt(s.get("expect")).split(":")[0].strip().lower()
    return bool(verdicts) and want in ("accept", "reject") and all(v == want for v in verdicts.values())


def _fresh_reads(ex, sids, leaf_ids, d, repo):
    """-> {sid: {"reads": [...], "verdicts": {reader: verdict}}} for `sids` from exam.json's reader_verdicts, or
    ValueError naming what is missing. Every named Reader answers every scenario, each answer names a leaf of the tree."""
    rv = ex.get("reader_verdicts")
    readers = [r for r in (ex.get("readers") or []) if CT.txt(r)]
    if not isinstance(rv, dict) or len(readers) < 2:
        raise ValueError("exam.json has no reader_verdicts from its two named Readers")
    import designer_stage as DS
    by = {}
    for r in readers:
        # keyed by the Reader's own string or by the agent id it names; a positional key ("reader1") is not guessed at
        keys = [k for k in rv if k == r or set(DS.agent_ids(k)) & set(DS.agent_ids(r))]
        if len(keys) != 1:
            raise ValueError("Reader %s has %s in reader_verdicts (matched by its agent id)" % (
                r, "no answers" if not keys else "%d answer sets" % len(keys)))
        by[r] = _answers(rv[keys[0]], d, repo)
    sc = {CT.txt(s.get("id")): s for s in ex.get("scenarios") or [] if isinstance(s, dict)}
    out = {}
    for sid in sids:
        reads, verdicts = set(), {}
        src = CT.txt(sc[sid].get("expect_source"))
        if not src.startswith("OWNER:"):          # his words sit in the shared unit, which every scenario reads
            reads.add(_leaf_id(src))
        for r in readers:
            if sid not in by[r]:
                raise ValueError("Reader %s gave no answer to %s" % (r, sid))
            verdict, lf = by[r][sid]
            if not lf:
                raise ValueError("Reader %s named no leaf it relied on for %s" % (r, sid))
            bad = [x for x in lf if x not in leaf_ids]
            if bad:
                raise ValueError("Reader %s relied on %s for %s, which is no leaf of the tree" % (r, bad, sid))
            reads.update(lf)
            verdicts[r] = verdict
        out[sid] = {"reads": sorted(reads), "verdicts": verdicts}
    return out


def record(d, repo=None):
    """Write READS_FILE for the exam on disk, which must pass its gate on the current tree and sheet. -> the record,
    or {"error": why} (and no file written) when it cannot be made."""
    import designer_stage as DS
    repo = repo or DS.clone_of(d) or DS.REPO
    try:
        tree = CT.load(d)
        if isinstance(tree, dict) and tree.get("exam_waived"):
            return {"error": "the exam is waived in his words: there are no answers to map"}
        ex = _read(os.path.join(d, "exam.json"))
        st = DS.read_json(os.path.join(d, "stage.json"), {}) or {}
        errs = DS.exam_errors(ex, d, st, repo)
        if errs:
            return {"error": "the exam does not pass on the current tree, so no map is recorded: %s" % "; ".join(errs[:3])}
        cur, shared, order = units(d)
        rows = _map_rows(ex, set(cur), d, repo)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, DS.Refused) as e:
        return {"error": "no map recorded: %s" % e}
    rec = {"schema": SCHEMA, "by": "exam_retake.py record", "at": _now(),
           "exam": {"tree": ex["inputs"]["tree"], "sheet": ex["inputs"]["sheet"],
                    "scenarios_hash": ex["scenarios_hash"]},
           "units": cur, "shared": shared, "sheet_order": order, "scenarios": rows}
    _write(os.path.join(d, READS_FILE), rec)
    return rec


def _map_rows(ex, leaf_ids, d, repo):
    """-> {sid: {hash, reads, verdicts, right, from}} for every scenario of `ex`: a carried answer's from its carried
    record, a fresh one's from the Readers' answers. ValueError when any cannot be told."""
    sc = {CT.txt(s.get("id")): s for s in ex["scenarios"] if isinstance(s, dict)}
    carried = ex.get("carried") if isinstance(ex.get("carried"), dict) else {}
    bad = [c for c in carried if c not in sc or carried_shape(carried[c])]
    if bad:
        raise ValueError("carried answer %s is malformed or no scenario" % ", ".join(sorted(bad)))
    fresh = _fresh_reads(ex, [x for x in sc if x not in carried], leaf_ids, d, repo)
    rows = {}
    for sid, s in sc.items():
        src = carried[sid] if sid in carried else fresh[sid]
        rows[sid] = {"hash": scenario_hash(s), "reads": sorted(src["reads"]), "verdicts": src["verdicts"],
                     "right": _right(s, src["verdicts"]), "from": src["from"] if sid in carried else _origin(ex)}
    return rows


def carried_shape(c):
    """-> why a carried record is malformed, or None."""
    if not isinstance(c, dict) or not isinstance(c.get("from"), dict) or not CT.txt(c["from"].get("tree")):
        return "names no exam it came from"
    if not (isinstance(c.get("reads"), list) and c["reads"] and all(isinstance(u, str) and u for u in c["reads"])):
        return "has no list of the leaves it read"
    if not isinstance(c.get("verdicts"), dict) or not isinstance(c.get("unit_hashes"), dict):
        return "has no verdicts or unit hashes"
    return None


def _origin(ex):
    """The exam a fresh answer was given in: its frozen inputs and scenario set, and its Readers."""
    return {"tree": (ex.get("inputs") or {}).get("tree"), "sheet": (ex.get("inputs") or {}).get("sheet"),
            "scenarios_hash": ex.get("scenarios_hash"), "readers": list(ex.get("readers") or [])}


def _out(outcome, why, retake=(), carry=(), changed=(), against=None):
    return {"outcome": outcome, "why": why, "retake": list(retake), "carry": list(carry), "changed": list(changed),
            "against": against}


def plan(d, scenarios=None, repo=None):
    """-> {"outcome", "why", "retake", "carry", "changed", "against"}: what a retake of the exam re-runs now.
    `scenarios` is the set the retake will freeze (default: the last exam's); a scenario whose text, expectation or
    source differs from the one answered is re-run, as is one the map never saw."""
    try:
        cur, shared, order = units(d)
    except (OSError, ValueError) as e:
        return _out(CANNOT_RUN, "the retake cannot run: tree.json or sheet.md cannot be read (%s)" % e)
    p = os.path.join(d, READS_FILE)
    if not os.path.isfile(p):
        return _out(WHOLE, "no read map recorded for the last exam (%s): the map cannot tell, retake the whole exam"
                    % READS_FILE)
    try:
        rec = _read(p)
        if not isinstance(rec, dict) or rec.get("schema") not in READ_SCHEMAS:
            raise ValueError("schema %r, not one of %s" % (rec.get("schema") if isinstance(rec, dict) else rec,
                                                           READ_SCHEMAS))
        units0, rows, shared0, order0 = rec["units"], rec["scenarios"], rec.get("shared"), rec["sheet_order"]
        if not (isinstance(units0, dict) and isinstance(rows, dict) and rows):
            raise ValueError("no units or no scenarios")
        if not is_order(order0):
            raise ValueError("sheet_order is not a list of [section, leaf id or null]")
        for sid, r in rows.items():
            if not (isinstance(r, dict) and isinstance(r.get("reads"), list) and r["reads"] and CT.txt(r.get("hash"))
                    and isinstance(r.get("verdicts"), dict) and isinstance(r.get("right"), bool)):
                raise ValueError("scenario %r has no reads, hash, verdicts or right" % sid)
            if any(u not in units0 for u in r["reads"]):
                raise ValueError("scenario %r reads a unit the map never hashed" % sid)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        return _out(WHOLE, "the read map %s cannot be read (%s): retake the whole exam" % (READS_FILE, e))
    try:
        ex = _read(os.path.join(d, "exam.json"))
        mine = {"tree": ex["inputs"]["tree"], "sheet": ex["inputs"]["sheet"], "scenarios_hash": ex["scenarios_hash"]}
        sc0 = ex["scenarios"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        return _out(WHOLE, "the last exam.json cannot be read (%s): retake the whole exam" % e)
    if not isinstance(rec.get("exam"), dict) or rec["exam"] != mine:
        return _out(WHOLE, "the read map is of another exam than exam.json (map %s, exam %s): retake the whole exam"
                    % (str(rec["exam"].get("tree") if isinstance(rec.get("exam"), dict) else rec.get("exam"))[:12],
                       str(mine["tree"])[:12]))
    against = dict(mine, at=rec.get("at"))
    # the map is re-derived from the exam's own answers: a map that drops or adds a read is not trusted
    try:
        import designer_stage as DS
        derived = _map_rows(ex, set(units0), d, repo or DS.clone_of(d) or DS.REPO)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        return _out(WHOLE, "the exam's own answers cannot confirm the read map (%s): retake the whole exam" % e,
                    against=against)
    if {k: (v["reads"], v["hash"], v["verdicts"]) for k, v in derived.items()} != {
            k: (sorted(v["reads"]), v["hash"], v["verdicts"]) for k, v in rows.items()}:
        return _out(WHOLE, "the read map disagrees with the exam's own answers: retake the whole exam",
                    against=against)
    new = sorted(set(cur) - set(units0))
    if new:
        return _out(WHOLE, "leaf %s is new: no scenario's read record covers it, so the map cannot tell: retake the "
                    "whole exam" % ", ".join(new), against=against)
    gone = sorted(set(units0) - set(cur))
    if gone:
        return _out(WHOLE, "leaf %s was removed: the leaves every scenario reads are not the ones it was answered on, "
                    "so the map cannot tell: retake the whole exam" % ", ".join(gone), changed=gone, against=against)
    if rec["schema"] == 2 and shared != shared0:
        shared0, why2 = _schema2_shared(d, rec, shared0)
        if shared0 is None:
            return _out(WHOLE, "the read map is schema 2, whose shared hash holds the floor's hash pin, and %s: the "
                        "map cannot tell, retake the whole exam" % why2, against=against)
    if shared != shared0:
        return _out(WHOLE, "the shared part every scenario reads changed (his words, an untagged sheet line or the "
                    "tree's own fields): retake the whole exam", against=against)
    changed = sorted(u for u in units0 if cur.get(u) != units0[u])
    if order_moved(order0, order, set(changed)):
        return _out(WHOLE, "the sheet's lines were reordered beyond the touched leaves' own lines (every scenario reads "
                    "the order): retake the whole exam", changed=changed, against=against)
    for u in changed:
        readers_of = [s for s, r in rows.items() if u in r["reads"]]
        if not readers_of:
            return _out(WHOLE, "leaf %s changed and no scenario's read record covers it: retake the whole exam" % u,
                        changed=changed, against=against)
        if len(readers_of) == len(rows):
            return _out(WHOLE, "leaf %s changed and every scenario reads it: retake the whole exam" % u,
                        changed=changed, against=against)
    sc = sc0 if scenarios is None else scenarios
    if not isinstance(sc, list) or not all(isinstance(s, dict) and CT.txt(s.get("id")) for s in sc):
        return _out(CANNOT_RUN, "the retake cannot run: the scenario set is not a list of scenarios with ids",
                    changed=changed, against=against)
    retake, carry, notes = [], [], []
    for s in sc:
        sid = CT.txt(s["id"])
        r = rows.get(sid)
        if r is None:
            retake.append(sid)
            notes.append("%s is new" % sid)
        elif r["hash"] != scenario_hash(s):
            retake.append(sid)
            notes.append("%s's text changed" % sid)
        elif set(r["reads"]) & set(changed):
            retake.append(sid)
        else:
            carry.append(sid)
    if not retake:
        return _out(NONE_TOUCHED, "looked: nothing any of the %d scenarios read changed (tree and sheet as examined "
                    "for every scenario's units): zero re-run, %d answers stand; run `exam_retake.py carry <dir> --fresh <file>` "
                    "on a file holding {} to restamp the exam's inputs (a sheet edit no scenario reads still moves the "
                    "hash the gate checks)" % (len(sc), len(carry)),
                    carry=carry, changed=changed, against=against)
    return _out(PARTIAL, "re-run %d of %d (%s%s); carry %d answers forward" % (
        len(retake), len(sc), "changed leaves %s" % ", ".join(changed) if changed else "no leaf changed",
        "; " + "; ".join(notes) if notes else "", len(carry)), retake, carry, changed, against)


def _exam_tree_from_git(d, want):
    """-> the tree.json object whose tree_hash is `want`, from git history of d's tree.json, or None (no git, no such
    commit). Every commit that touched tree.json is read: the danger of a cap is a wrong whole exam, and a read is
    about 10 ms."""
    import subprocess
    try:
        log = subprocess.run(["git", "-C", d, "log", "--format=%H", "--", "tree.json"], capture_output=True,
                             text=True, check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return None
    for h in log:
        try:
            out = subprocess.run(["git", "-C", d, "show", "%s:./tree.json" % h], capture_output=True, text=True,
                                 check=True).stdout
            t = json.loads(out)
        except (OSError, subprocess.CalledProcessError, ValueError):
            continue
        if isinstance(t, dict) and CT.tree_hash(t) == want:
            return t
    return None


def _schema2_shared(d, rec, shared0):
    """A schema-2 map's shared hash holds the floor's hash pin. -> (the schema-3 shared hash of the tree the exam was
    taken on, None) when that tree is found in git history and proven to be the one the map hashed (its schema-2 shared
    hash with the current sheet equals the map's, so the untagged sheet lines did not change either), else
    (None, why)."""
    if legacy_shared(d) == shared0:
        return units(d)[1], None
    old = _exam_tree_from_git(d, rec["exam"].get("tree"))
    if old is None:
        return None, "the tree the exam was taken on (%s) is not in git history" % str(rec["exam"].get("tree"))[:12]
    try:
        if legacy_shared(d, old) != shared0:
            return None, "the exam's tree from git history with the current sheet does not give the map's shared hash"
        return units_of(old, d)[1], None
    except (OSError, ValueError) as e:
        return None, "the exam's tree from git history cannot be read (%s)" % e


def write_plan(d, p):
    """Record the plan on disk, so "looked, none touched" is a written result and never inferred from silence."""
    rec = dict(p, by="exam_retake.py plan", at=_now())
    _write(os.path.join(d, PLAN_FILE), rec)
    return rec


def carry(d, fresh_path, repo=None):
    """Write the new exam.json from the last one: the fresh Readers' answers for the scenarios plan() retakes, every
    other answer carried forward and marked with the exam it came from. Refused (Refused) when the plan is whole or
    cannot_run, and when the fresh answers do not cover what is retaken (then the plan on disk reads cannot_run, with
    why). -> the plan applied."""
    import designer_stage as DS
    repo = repo or DS.clone_of(d) or DS.REPO

    def cannot(p, why):
        write_plan(d, dict(p, outcome=CANNOT_RUN, why="the retake could not run: %s" % why, retake=[], carry=[]))
        raise Refused("the retake could not run: %s" % why)

    try:
        fresh = _read(fresh_path)
    except (OSError, ValueError) as e:
        cannot(_out(CANNOT_RUN, ""), "the fresh answers cannot be read (%s)" % e)
    if not isinstance(fresh, dict):
        cannot(_out(CANNOT_RUN, ""), "the fresh answers are not an object")
    sc = fresh.get("scenarios")
    if sc is None:
        try:
            sc = _read(os.path.join(d, "exam.json")).get("scenarios")
        except (OSError, ValueError, AttributeError):
            sc = None
    # the plan first, and on disk, so a missing or broken map is recorded as whole before anything else is read
    p = plan(d, scenarios=sc, repo=repo)
    write_plan(d, p)
    if p["outcome"] in (WHOLE, CANNOT_RUN):
        raise Refused("no partial retake: the plan is %s (%s)" % (p["outcome"], p["why"]))
    prior = _read(os.path.join(d, "exam.json"))       # plan() has read both and found them sound
    rec = _read(os.path.join(d, READS_FILE))
    st = DS.read_json(os.path.join(d, "stage.json"), {}) or {}
    now_in = {k: DS.inputs(d, st, repo)[k] for k in ("tree", "sheet")}
    readers = fresh.get("readers")
    if p["retake"]:
        # the tree moved, so the old control Reader's miss and the old count of core false accepts say nothing of it:
        # a retake that re-ran scenarios brings both, never inherits them, and says which inputs its Readers were shown
        if not isinstance(fresh.get("control"), dict):
            cannot(p, "the fresh answers bring no control (a control Reader on a fresh `designer_stage.py "
                      "exam-control` copy of the current tree)")
        if type(fresh.get("accept_where_reject_core")) is not int:
            cannot(p, "the fresh answers bring no accept_where_reject_core count")
        if fresh.get("inputs") != now_in:
            cannot(p, "the fresh answers were given on inputs %r, not the current tree and sheet %r" % (
                fresh.get("inputs"), now_in))
        if fresh.get("scenarios_hash") != CT.sha(sc):
            cannot(p, "the fresh answers' scenarios_hash is not the hash of the scenario set frozen for the retake")
        if not (isinstance(readers, list) and all(isinstance(r, str) for r in readers)):
            cannot(p, "the fresh answers name no list of Readers")
    new = dict(prior, scenarios=sc, scenarios_hash=CT.sha(sc))
    if p["retake"]:
        new.update(readers=readers, reader_verdicts=fresh.get("reader_verdicts"))
        try:
            cur, shared, order = units(d)
            got = _fresh_reads(new, p["retake"], set(cur), d, repo)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
            cannot(p, "the fresh answers %s" % e)
    else:
        cur, shared, order = units(d)
        got = {}
        _restamp_control(d, prior, lambda why: cannot(p, why))
    car = {}
    for sid in p["carry"]:
        r = rec["scenarios"][sid]
        car[sid] = {"from": r.get("from") or _origin(prior), "reads": r["reads"], "verdicts": r["verdicts"],
                    "right": r["right"], "hash": r["hash"], "shared": shared,
                    "unit_hashes": {u: cur[u] for u in r["reads"]}}
    by_id = {CT.txt(s.get("id")): s for s in sc}
    right = sum(1 for sid in p["carry"] if car[sid]["right"]) + sum(
        1 for sid, g in got.items() if _right(by_id[sid], g["verdicts"]))
    new.update(inputs=now_in, carried=car, score={"right": right, "total": len(sc)},
               retake={"outcome": p["outcome"], "retaken": p["retake"], "carried": p["carry"],
                       "changed": p["changed"], "against": p["against"], "units": cur, "sheet_order": order,
                       "by": "exam_retake.py carry", "at": _now()})
    # a Challenger miss stands for a carried scenario; a retaken one's old miss says nothing of the new answers
    new["challenger_misses"] = [m for m in (prior.get("challenger_misses") or []) if isinstance(m, dict)
                                and CT.txt(m.get("id")) in car] + [
        m for m in (fresh.get("challenger_misses") or []) if isinstance(m, dict) and CT.txt(m.get("id")) in got]
    for k in ("accept_where_reject_core", "control"):
        if k in fresh:
            new[k] = fresh[k]
    _write(os.path.join(d, "exam.json"), new)
    return p


def _restamp_control(d, prior, cannot):
    """No scenario retaken: the control Reader's answers stand, but the control copy names the tree it was made from
    (copy.json base_tree), so a tree change no Reader reads (a PINS re-pin) leaves the gate refusing it. Remake the copy
    from the current tree with the same leaf and strip phrases, and keep it only when it reads exactly as the copy the
    control Reader was shown (every unit and the sheet order equal, PINS aside); else put the old copy back and refuse."""
    import designer_stage as DS
    cdir = os.path.join(d, DS.CONTROL_DIR)
    try:
        rec = _read(os.path.join(cdir, "copy.json"))
        if not isinstance(rec, dict) or rec.get("base_tree") == DS.input_hash(d, "tree"):
            return
        before = units(cdir)
        keep = {}
        for n in ("tree.json", "sheet.md", "copy.json"):
            with open(os.path.join(cdir, n), encoding="utf-8") as f:
                keep[n] = f.read()
    except (OSError, ValueError, TypeError, DS.Refused):
        return          # no readable copy to remake: the gate names what is missing
    leaf = (prior.get("control") or {}).get("broken_leaf") if isinstance(prior.get("control"), dict) else None
    try:
        DS.exam_control(d, leaf or rec.get("leaf"), strip=rec.get("strip") or [])
        after = units(cdir)
    except (OSError, ValueError, DS.Refused) as e:
        after = "unreadable (%s)" % e
    if after != before:
        for n, text in keep.items():
            with open(os.path.join(cdir, n), "w", encoding="utf-8") as f:
                f.write(text)
        cannot("the control copy made from the current tree does not read as the one the control Reader was shown: "
               "rerun the control Reader on a fresh `designer_stage.py exam-control` copy")


def carry_errors(ex, d):
    """designer_stage.exam_errors' check of a carried answer: its scenario, the shared unit and every leaf unit it read
    are as they were when it was answered, and the sheet's lines are not reordered beyond the leaves changed since the
    carry (retake.units and retake.sheet_order, written by carry). -> errors ([] when exam.json carries nothing)."""
    car = ex.get("carried")
    if car is None:
        return []
    if not isinstance(car, dict):
        return ["exam: carried is not a map of scenario id to its carried answer"]
    try:
        cur, shared, order = units(d)
    except (OSError, ValueError) as e:
        return ["exam: carried answers cannot be checked: %s" % e]
    legacy = legacy_shared(d)
    by_id = {CT.txt(s.get("id")): s for s in ex.get("scenarios") or [] if isinstance(s, dict)}
    errs = []
    if car:
        rt = ex.get("retake") if isinstance(ex.get("retake"), dict) else {}
        u0, o0 = rt.get("units"), rt.get("sheet_order")
        if not (isinstance(u0, dict) and is_order(o0)):
            errs.append("exam: carried answers cannot be checked: retake records no units and sheet_order of the carry; "
                        "retake it (exam_retake.py plan)")
        elif order_moved(o0, order, {u for u in set(u0) | set(cur) if u0.get(u) != cur.get(u)}):
            errs.append("exam: carried answers are stale: the sheet's lines were reordered since the carry; retake it "
                        "(exam_retake.py plan)")
    for sid, c in sorted(car.items()):
        how = "retake it (exam_retake.py plan)"
        bad = carried_shape(c)
        if bad:
            errs.append("exam: carried answer %s %s; %s" % (sid, bad, how))
            continue
        if sid not in by_id:
            errs.append("exam: carried answer %s is no scenario of this exam" % sid)
        elif c.get("hash") != scenario_hash(by_id[sid]):
            errs.append("exam: carried answer %s is stale: its scenario changed since it was answered; %s" % (sid, how))
        if c.get("shared") != shared and c.get("shared") != legacy:     # legacy: carried before schema 3
            errs.append("exam: carried answer %s is stale: the shared part of the tree or sheet changed; %s" % (sid, how))
        uh = c.get("unit_hashes") if isinstance(c.get("unit_hashes"), dict) else {}
        moved = sorted(u for u in (c.get("reads") or []) if uh.get(u) is None or cur.get(u) != uh.get(u))
        if not c.get("reads") or moved:
            errs.append("exam: carried answer %s is stale: leaf %s it read changed since it was answered; %s" % (
                sid, ", ".join(moved) or "(none recorded)", how))
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("record", "plan", "carry"):
        x = sub.add_parser(name)
        x.add_argument("dir")
        if name == "plan":
            x.add_argument("--scenarios", help="a JSON file holding the scenario list the retake will freeze")
        if name == "carry":
            x.add_argument("--fresh", required=True, help="readers, reader_verdicts for the retaken scenarios, the "
                           "new control, accept_where_reject_core, and optionally the scenario list")
    a = ap.parse_args(argv)
    if a.cmd == "record":
        rec = record(a.dir)
        if "error" in rec:
            print("NO MAP: %s" % rec["error"])
            return 1
        print("MAP RECORDED: %d scenarios over %d leaves -> %s" % (len(rec["scenarios"]), len(rec["units"]),
                                                                   os.path.join(a.dir, READS_FILE)))
        return 0
    if a.cmd == "plan":
        sc = None
        if a.scenarios:
            try:
                sc = _read(a.scenarios)
            except (OSError, ValueError) as e:
                print("CANNOT_RUN: the scenario file cannot be read (%s)" % e)
                return 3
            sc = sc.get("scenarios") if isinstance(sc, dict) else sc
        p = write_plan(a.dir, plan(a.dir, scenarios=sc))
        print("%s: %s" % (p["outcome"].upper(), p["why"]))
        if p["outcome"] in (PARTIAL, NONE_TOUCHED):
            print("  retake: %s\n  carry:  %s" % (" ".join(p["retake"]) or "(none)", " ".join(p["carry"]) or "(none)"))
        return {PARTIAL: 0, NONE_TOUCHED: 0, WHOLE: 2, CANNOT_RUN: 3}[p["outcome"]]
    try:
        p = carry(a.dir, a.fresh)
    except Refused as e:
        print("REFUSED: %s" % e)
        return 2
    print("CARRIED: %s, retook %s, carried %d; now run `designer_stage.py check` (the gate re-checks every carry)" % (
        p["outcome"], " ".join(p["retake"]) or "nothing", len(p["carry"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
