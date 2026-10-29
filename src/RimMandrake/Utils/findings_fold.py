#!/usr/bin/env python3
"""findings_fold.py - the no-AI findings sorter (FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X).

Design: design/RimMandrake/findings_curation_design_2026-10-29.md option B, chosen by the owner by card 2026-10-29
("Program folds, FOUNDRY judges"), simplified after two blind reviews (v3_review/blind/findings/review.md, review2.md)
by the coordinator's ruling: the program groups and reports, it never judges. Runs after every testq ingest (the
testq-tick unit's last ExecStart, testq.py UNITS); output folder and rules: findings_fold_rules.json.

    findings_fold.py run [--out DIR]                                       fold, write findings_fold.md
    findings_fold.py decide SIG --as KIND [--into X] --why "..." --seat SEAT     FOUNDRY records a judgment

What it does, with no AI and no ledger writes:
  * signs every finding of the folded types (UNTRIAGED: what ingest.py files) by mod, chain, row and the failure
    text with ONLY job ids, timestamps and durations removed (rules `normalise`, a short tested list). The text is
    the done record's full detail when exactly one record names the finding, else the ledger's line, and then the
    finding is signed with its own name too, so it merges with nothing (a paused-lane finding, which names no test
    row, always is). Rows are grouped by that whole tuple; the signature shown is its full sha256. One row of the
    table: count, first and last seen, items, every finding name and raw text. A doubtful pair stays two rows;
  * reports evidence, decides nothing: for each signature, how many distinct later runs passed its row after its
    last failure (`passes_since`) and the row's latest measured verdict. There is no automatic retirement, reopening
    or merge into a decision: FOUNDRY (or a human) records a decision with `decide` and the report shows it, plus any
    failure of that signature since it;
  * a CONTRADICTION is an item in a `contradiction_states` state (done, validated) whose own latest measured verdict
    of a row (the newest PASS/FAIL among the done records whose rows ingest maps to that item) is FAIL;
  * a machine-health failure (rules machine_health_patterns, case-insensitive) or a paused-lane finding is labelled
    HEALTH, for Operations' lane item; its identity is not changed by that label.
Fails CLOSED: an unreadable or structurally wrong ledger finding, done record, decisions line or previous table, or a
finding name reused with different content, exits 2 with UNMEASURED and changes no output. One writer: the run holds
the queue's ingest.lock and this clone's ingest.repo_lock (the locks ingest.py takes while it writes records and the
ledger) from the rules read to the rename, and `decide` takes them too. ONE file is published, by one rename:
findings_fold.md, the report with the whole table embedded as its last block. An existing one that cannot be read or
holds no whole table of this schema makes the run UNMEASURED (move it aside); a rerun that would render the same table
writes nothing, one whose markdown was edited is re-rendered.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(REPO, "src", "RimMandrake", "rimflow")
TESTQ = os.path.join(HERE, "testq")
RULES_PATH = os.path.join(HERE, "findings_fold_rules.json")
SCHEMA = "findings_fold/3"
KINDS = ("work", "merge", "memory", "route", "retire", "undo")
NEEDS_INTO = ("work", "merge", "memory", "route")
VERDICTS = ("PASS", "FAIL", "UNMEASURED", "NOT_RUN")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SIG_RE = re.compile(r"^S[0-9a-f]{64}$")
WHY_RE = re.compile(r"^(?P<chain>[^/ ]*)/(?P<row>\S+) FAIL on (?P<host>\S+): (?P<detail>.*)$", re.S)
REPORT = "findings_fold.md"
TABLE_FENCE, TABLE_END = "\n\n```json findings_fold table\n", "\n```\n"
TABLE_KEYS = {"schema", "generated", "counts", "signatures", "contradictions", "raw"}


class Unmeasured(Exception):
    """An input could not be read: the run stops, changes nothing, and says so."""


def utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_rules(path=None):
    path = path or os.environ.get("FINDINGS_FOLD_RULES") or RULES_PATH     # the env override: selftests only
    try:
        with open(path, encoding="utf-8") as f:
            rules = json.load(f)
        for k in ("finding_types", "lane_item", "machine_health_patterns", "contradiction_states",
                  "decisions_file", "normalise", "memory_roots"):
            rules[k]
        rules["_mh"] = [re.compile(p, re.I) for p in rules["machine_health_patterns"]]
        rules["_norm"] = [(re.compile(p), r) for p, r in rules["normalise"]]
        return rules
    except (OSError, ValueError, KeyError, TypeError, re.error) as e:
        raise Unmeasured("rules %s unreadable: %s: %s" % (path, type(e).__name__, e))


def normalise(text, rules):
    t = text or ""
    for rx, rep in rules["_norm"]:
        t = rx.sub(rep, t)
    return t


def row_key(mod, chain, row, text, rules, name=None):
    """The identity of a failure: the whole tuple. name: given only for a finding no done record explains."""
    return (mod, chain, row, normalise(text, rules), name)


def signature(key):
    """Its full sha256 over an unambiguous encoding: a label for the tuple, which is what rows are grouped by."""
    return "S" + hashlib.sha256(json.dumps(list(key)).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ inputs (each fails closed)
def _strs(x):
    return isinstance(x, list) and all(isinstance(s, str) and s for s in x)


def record_fault(r):
    """-> why a done record cannot be folded, or None. Every field the fold reads is checked, nested ones too."""
    if not isinstance(r, dict):
        return "not an object"
    job, res, ing = r.get("job"), r.get("result"), r.get("ingested")
    if not isinstance(job, dict) or not all(isinstance(job.get(k), str) and job.get(k) for k in ("id", "mod")):
        return "no job with an id and a mod"
    if job.get("item") is not None and not isinstance(job["item"], str):
        return "job.item is not a string"
    ri = job.get("row_items")
    if ri is not None and not (isinstance(ri, dict) and all(isinstance(v, str) for v in ri.values())):
        return "job.row_items is not {row: item}"
    if not isinstance(res, dict) or not isinstance(res.get("outcome"), str) or not res["outcome"]:
        return "no result with an outcome"
    if not ISO_RE.match(str(res.get("finished"))):
        return "no finish time (got %r)" % res.get("finished")
    rows = res.get("rows")
    if res["outcome"] == "DONE" and not isinstance(rows, list):
        return "a DONE result whose rows are not a list"
    seen = set()
    for k, x in enumerate(rows if isinstance(rows, list) else []):
        if not isinstance(x, dict) or not isinstance(x.get("row"), str) or not x["row"] \
                or x.get("verdict") not in VERDICTS:
            return "row %d is not {row, verdict}" % k
        for f in ("chain", "detail"):
            if x.get(f) is not None and not isinstance(x[f], str):
                return "row %d %s is not a string" % (k, f)
        rid = (x.get("chain") or "", x["row"])          # the fold's own identity of a row (row_runs, locate)
        if rid in seen:
            return "row %s/%s appears twice" % rid
        seen.add(rid)
    if ing is not None:
        if not isinstance(ing, dict):
            return "ingested is not an object"
        groups = ing.get("groups", {})
        if not isinstance(groups, dict) or not all(isinstance(g, dict) for g in groups.values()):
            return "ingested.groups is not {item: group}"
        for g in [ing] + list(groups.values()):
            if "findings" in g and not (g["findings"] == [] or _strs(g["findings"])):
                return "ingested findings is not a list of names"
        if ing.get("lane_finding") is not None and not isinstance(ing["lane_finding"], str):
            return "ingested.lane_finding is not a string"
    return None


def queue_dir():
    sys.path.insert(0, TESTQ)
    import testq as T
    return os.environ.get("TESTQ_QUEUE") or T.QHOME


def read_done(qdir):
    d = os.path.join(qdir, "done")
    try:
        names = sorted(n for n in os.listdir(d) if n.endswith(".json"))
    except OSError as e:
        raise Unmeasured("done records unreadable: %s" % e)
    recs, ids = [], set()
    for n in names:
        try:
            with open(os.path.join(d, n), encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError) as e:
            raise Unmeasured("done record %s unreadable: %s" % (n, e))
        why = record_fault(r) or ("job %s is in two done files" % r["job"]["id"] if r["job"]["id"] in ids else None)
        if why:
            raise Unmeasured("done record %s unreadable: %s" % (n, why))
        ids.add(r["job"]["id"])
        recs.append(r)
    return recs


def read_ledger(rules):
    """-> (findings by name, spawn events, item states). A folded finding missing a field, or a name reused with
    different content, is UNMEASURED (an exact duplicate line, as a git union merge can leave, is one finding)."""
    sys.path.insert(0, RIMFLOW)
    try:
        import model
        if os.environ.get("RIMFLOW_LEDGER"):          # the selftest redirect, as ingest.recorded_run binds it
            model.EVENTS = os.environ["RIMFLOW_LEDGER"]
        events = model.read()
        states = {i: it.state for i, it in model.replay(events).items.items()}
    except Exception as e:  # noqa: BLE001 - every ledger failure is UNMEASURED
        raise Unmeasured("ledger unreadable: %s: %s" % (type(e).__name__, str(e)[:200]))
    finds = {}
    for e in events:
        if e.get("event") != "finding" or e.get("type") not in rules["finding_types"]:
            continue
        if not all(isinstance(e.get(k), str) and e.get(k) for k in ("name", "id", "why")) \
                or not ISO_RE.match(str(e.get("ts"))):
            raise Unmeasured("ledger finding %r lacks a name, item, text or time" % e.get("name"))
        core = {k: e.get(k) for k in ("id", "why", "ts", "from")}
        if e["name"] in finds and finds[e["name"]] != core:
            raise Unmeasured("finding name %s is used by two different findings" % e["name"])
        finds[e["name"]] = core
    spawns = [e for e in events if e.get("event") == "spawn" and isinstance(e.get("from"), str)]
    return finds, spawns, states


def decisions_path(rules):
    return os.environ.get("FINDINGS_FOLD_DECISIONS") or os.path.join(REPO, rules["decisions_file"])


def decision_fault(d):
    if not isinstance(d, dict) or d.get("as") not in KINDS or not SIG_RE.match(str(d.get("sig"))):
        return "not {sig, as}"
    if not ISO_RE.match(str(d.get("ts"))) or not all(isinstance(d.get(k), str) and d[k].strip() for k in ("by", "why")):
        return "no ts, by or why"
    if d["as"] in NEEDS_INTO and not (isinstance(d.get("into"), str) and d["into"]):
        return "a %s decision with no --into" % d["as"]
    return None


def read_decisions(path):
    if not os.path.exists(path):
        return []                                   # legitimately absent until FOUNDRY's first decision
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for k, line in enumerate(f, 1):
                if line.strip():
                    d = json.loads(line)
                    if decision_fault(d):
                        raise ValueError("line %d: %s" % (k, decision_fault(d)))
                    out.append(d)
    except (OSError, ValueError) as e:
        raise Unmeasured("decisions %s unreadable: %s" % (path, e))
    return out


# ------------------------------------------------------------------ the fold
def index_records(recs):
    """finding name -> its done record. A name in two records is ambiguous: neither is used."""
    idx, dup = {}, set()
    for r in recs:
        ing = r.get("ingested") or {}
        groups = [ing] + list((ing.get("groups") or {}).values())
        names = [n for g in groups for n in (g.get("findings") or [])] + \
            ([ing["lane_finding"]] if ing.get("lane_finding") else [])
        for n in names:
            if n in idx and idx[n] is not r:
                dup.add(n)
            idx[n] = r
    for n in dup:
        idx.pop(n)
    return idx


def locate(name, ev, rec):
    """-> (mod, chain, row, text, time, resolved): from the record's one FAIL row of that chain/row, else the ledger."""
    m = WHY_RE.match(ev["why"])
    chain, row, detail = (m.group("chain"), m.group("row"), m.group("detail")) if m else ("", "", ev["why"])
    if rec is not None:
        pick = [x for x in rec["result"].get("rows") or [] if x["verdict"] == "FAIL" and x["row"] == row
                and (x.get("chain") or "") == chain]
        if len(pick) == 1:
            return rec["job"]["mod"], chain, row, pick[0].get("detail") or detail, rec["result"]["finished"], True
    return "?", chain, row, detail, ev["ts"], False


def row_runs(recs):
    """(mod, chain, row) -> [(finished, job, verdict, detail, item)], oldest first, DONE records only."""
    sys.path.insert(0, TESTQ)
    import ingest as I
    out = {}
    for r in recs:
        res = r["result"]
        if res["outcome"] != "DONE":
            continue
        item_of = {id(x): it for it, xs in I.groups_of(r["job"], res).items() for x in xs}
        for x in res["rows"]:
            out.setdefault((r["job"]["mod"], x.get("chain") or "", x["row"]), []).append(
                (res["finished"], r["job"]["id"], x["verdict"], x.get("detail") or "", item_of.get(id(x))))
    for v in out.values():
        v.sort()
    return out


def latest_decision(sig, names, spawns, lines):
    """The newest of: a decisions-file line on sig, a `rimflow spawn --from <one of its findings>` (work). undo -> None."""
    ds = [dict(d, src="decisions") for d in lines if d["sig"] == sig] + \
        [{"as": "work", "into": e.get("name"), "by": e.get("seat"), "ts": e.get("ts") or "",
          "why": "spawned from %s" % e["from"], "src": "ledger"} for e in spawns if e["from"] in names]
    last = max(ds, key=lambda d: d["ts"]) if ds else None
    return None if not last or last["as"] == "undo" else last


def fold(finds, spawns, states, recs, decision_lines, rules, now):
    idx, runs = index_records(recs), row_runs(recs)
    raw = {}
    for name, ev in sorted(finds.items()):
        mod, chain, row, text, at, ok = locate(name, ev, idx.get(name))
        key = row_key(mod, chain, row, text, rules, None if ok else name)
        raw[name] = {"key": key, "sig": signature(key), "item": ev["id"], "mod": mod, "chain": chain, "row": row,
                     "text": text, "at": at, "from": ev.get("from"), "resolved": ok}
    groups = {}
    for name, f in sorted(raw.items(), key=lambda kv: (kv[1]["at"], kv[0])):
        s = groups.setdefault(f.pop("key"), {k: f[k] for k in ("sig", "mod", "chain", "row", "text")} |
                              {"findings": [], "items": [], "first_seen": f["at"], "count": 0})
        s["findings"].append(name)
        s["count"] += 1
        s["last_seen"] = f["at"]
        if f["item"] not in s["items"]:
            s["items"].append(f["item"])
    sigs = {s.pop("sig"): s for s in groups.values()}
    if len(sigs) != len(groups):
        raise Unmeasured("two different failures share one signature")
    for (key, s), sig in zip(groups.items(), sigs):
        tl = runs.get((s["mod"], s["chain"], s["row"]), [])
        last_fail = max([s["last_seen"]] + [at for at, _, v, d, _ in tl if v == "FAIL" and
                                            row_key(s["mod"], s["chain"], s["row"], d, rules) == key])
        measured = [x for x in tl if x[2] in ("PASS", "FAIL")]
        s["last_fail"] = last_fail
        s["passes_since"] = len({j for at, j, v, _, _ in tl if v == "PASS" and at > last_fail})
        s["row_latest"] = {"verdict": measured[-1][2], "at": measured[-1][0], "job": measured[-1][1]} \
            if measured else None
        s["health"] = any(n.startswith("STEVE_LANE_") for n in s["findings"]) or \
            any(rx.search(s["text"]) for rx in rules["_mh"])
        d = latest_decision(sig, set(s["findings"]), spawns, decision_lines)
        s["decision"] = d
        s["failed_since_decision"] = sum(1 for n in s["findings"] if d and raw[n]["at"] > d["ts"]) + \
            sum(1 for at, _, v, dt, _ in tl if d and v == "FAIL" and at > d["ts"] and
                row_key(s["mod"], s["chain"], s["row"], dt, rules) == key and
                not any(raw[n]["at"] == at for n in s["findings"]))
        s["status"] = "HEALTH" if s["health"] else "DECIDED" if d else "NEW"
    contra = []
    for (mod, chain, row), tl in sorted(runs.items()):
        latest = {}
        for at, job, v, _, it in tl:
            if it and v in ("PASS", "FAIL"):
                latest[it] = (at, job, v)
        for it, (at, job, v) in sorted(latest.items()):
            if v == "FAIL" and states.get(it) in rules["contradiction_states"]:
                contra.append({"item": it, "state": states[it], "mod": mod, "chain": chain, "row": row, "at": at,
                               "job": job, "sigs": sorted(s_ for s_, s in sigs.items() if it in s["items"] and
                                                          (s["mod"], s["chain"], s["row"]) == (mod, chain, row))})
    by = {}
    for s in sigs.values():
        by[s["status"]] = by.get(s["status"], 0) + 1
    counts = {"findings": len(raw), "distinct": len(sigs), "by_status": by, "contradictions": len(contra),
              "unresolved": sum(1 for f in raw.values() if not f["resolved"]), "records": len(recs)}
    if sum(s["count"] for s in sigs.values()) != len(raw):
        raise Unmeasured("conservation broken: %d findings, %d counted" % (len(raw), sum(s["count"] for s in
                                                                                          sigs.values())))
    return {"schema": SCHEMA, "generated": now, "counts": counts, "signatures": sigs, "contradictions": contra,
            "raw": raw}


def render_md(t):
    sigs, c = t["signatures"], t["counts"]
    out = ["# Findings fold %s" % t["generated"], "",
           "%d findings, %d distinct failures (%d unresolved: no done record, never merged); %s. The program groups "
           "and reports only: nothing is retired, reopened or noted on the ledger; FOUNDRY decides (`findings_fold.py "
           "decide`). The table is the last block of this file." % (c["findings"], c["distinct"], c["unresolved"],
                                                                  json.dumps(c["by_status"], sort_keys=True)), "",
           "## CONTRADICTIONS: a done or validated item whose own latest run of a row FAILED (%d)" % len(t["contradictions"])]
    for x in t["contradictions"]:
        out.append("- %s (%s): %s/%s/%s FAIL at %s in %s; signatures %s" % (
            x["item"], x["state"], x["mod"], x["chain"], x["row"], x["at"], x["job"], ",".join(x["sigs"]) or "-"))
    out.append("")

    def ev(s):
        rl = s["row_latest"]
        return "passed %s later run(s); row latest %s" % (
            "?" if s["mod"] == "?" else s["passes_since"], "%s %s" % (rl["verdict"], rl["at"]) if rl else "unmeasured")

    def dec(s):
        d = s["decision"]
        return "; decided %s into %s at %s" % (d["as"], d.get("into") or "-", d["ts"])

    def sect(title, pick, extra=lambda s: ""):
        rows = sorted(((k, s) for k, s in sigs.items() if pick(s)), key=lambda x: (-x[1]["count"], x[0]))
        out.append("## %s (%d)" % (title, len(rows)))
        for k, s in rows:
            out.append("- `%s` x%d %s..%s %s/%s/%s under %s; %s%s: %s" % (
                k, s["count"], s["first_seen"][:10], s["last_seen"][:10], s["mod"], s["chain"], s["row"],
                ",".join(s["items"]), ev(s), extra(s), json.dumps(s["text"][:200])))
        out.append("")
    sect("NEW: FOUNDRY judges (work / merge / memory / route / retire)", lambda s: s["status"] == "NEW")
    sect("DECIDED, and failed again since", lambda s: s["status"] == "DECIDED" and s["failed_since_decision"],
         lambda s: dec(s) + ", %d failure(s) since" % s["failed_since_decision"])
    sect("DECIDED", lambda s: s["status"] == "DECIDED" and not s["failed_since_decision"], dec)
    sect("HEALTH: for Operations (lane item)", lambda s: s["status"] == "HEALTH")
    return "\n".join(out)


def render_report(t):
    """The one published file: the markdown, then the table as its last block."""
    return render_md(t) + TABLE_FENCE + json.dumps(t, indent=1, sort_keys=True) + TABLE_END


# ------------------------------------------------------------------ output
def out_dir(override, rules):
    if override or os.environ.get("FINDINGS_FOLD_OUT"):
        return override or os.environ["FINDINGS_FOLD_OUT"]
    sys.path.insert(0, HERE)
    from game_paths import win_to_wsl
    return win_to_wsl(rules["out"])


def semantic(t):
    """The table without its run time, as one canonical string."""
    return json.dumps({k: v for k, v in t.items() if k != "generated"}, sort_keys=True)


def read_prev(path):
    """(table, file text) of the existing report, or (None, None) when there is none. Unreadable, partial, or a
    table that is not a whole table of this schema: UNMEASURED, never 'no previous table'."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return None, None
    except (OSError, ValueError) as e:
        raise Unmeasured("existing report %s unreadable: %s" % (path, e))
    _, fence, body = text.rpartition(TABLE_FENCE)
    try:
        t = json.loads(body[:-len(TABLE_END)]) if fence and body.endswith(TABLE_END) else None
    except ValueError:
        t = None
    if not isinstance(t, dict) or set(t) != TABLE_KEYS or t["schema"] != SCHEMA:
        raise Unmeasured("existing report %s holds no whole %s table (partial, edited or another version): "
                         "move it aside to start again" % (path, SCHEMA))
    return t, text


def write_atomic(path, text):
    """A unique temp file in the same folder, then one rename."""
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


@contextlib.contextmanager
def writer_lock(qdir):
    """The queue's ingest.lock, then this clone's ingest.repo_lock (ingest.py's order): held from the first read of
    rules, records, ledger and report to the last write, so a run sees one ingest state and one writer at a time."""
    wait_s = float(os.environ.get("FINDINGS_FOLD_LOCK_WAIT_S", "300"))
    sys.path.insert(0, TESTQ)
    import ingest as I
    with open(os.path.join(qdir, "ingest.lock"), "a") as fh:
        end = time.time() + wait_s
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() >= end:
                    raise Unmeasured("the queue's ingest.lock is still held after %d s" % wait_s)
                time.sleep(0.2)
        try:
            with I.repo_lock(wait_s) as got:
                if not got:
                    raise Unmeasured("this clone's repo lock is still held after %d s" % wait_s)
                yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def cmd_run(a):
    qd = queue_dir()
    with writer_lock(qd):
        rules = load_rules()
        od = out_dir(a.out, rules)
        os.makedirs(od, exist_ok=True)
        path = os.path.join(od, REPORT)
        prev, text = read_prev(path)
        t = fold(*read_ledger(rules), read_done(qd), read_decisions(decisions_path(rules)), rules, utcnow())
        if prev is not None and semantic(prev) == semantic(t) and text == render_report(prev):
            print("findings_fold: unchanged since %s: nothing written" % prev["generated"])
            return 0
        write_atomic(path, render_report(t))
    print("findings_fold: %s -> %s" % (json.dumps(t["counts"], sort_keys=True), path))
    return 0


def cmd_decide(a):
    seat = a.seat or os.environ.get("RIMFLOW_SEAT")
    if not seat:
        print("REFUSED: --seat (or RIMFLOW_SEAT) names who decided")
        return 2
    with writer_lock(queue_dir()):
        return decide(a, seat, load_rules())


def decide(a, seat, rules):
    t = read_prev(os.path.join(out_dir(a.out, rules), REPORT))[0]
    if not t or a.sig not in t["signatures"]:
        print("REFUSED: %s is not in the report's table (run `findings_fold.py run` first)" % a.sig)
        return 2
    into = a.into
    if a.as_ in ("work", "merge"):
        _, _, states = read_ledger(rules)
        if into not in states:
            print("REFUSED: --into %r is not an item in the ledger (work: `rimflow spawn --from <finding>` first)" % into)
            return 2
    elif a.as_ == "memory":
        path, _, line = (into or "").rpartition(":")
        full = os.path.join(REPO, path)
        if not path or not line.isdigit() or not os.path.isfile(full) or \
                not any(path.startswith(r) for r in rules["memory_roots"]) or "lessons" in path.split("/"):
            print("REFUSED: memory --into must be FILE:LINE of an existing file under %s, never the lessons inbox"
                  % ", ".join(rules["memory_roots"]))
            return 2
        with open(full, encoding="utf-8", errors="replace") as f:
            if int(line) < 1 or int(line) > sum(1 for _ in f):
                print("REFUSED: %s has no line %s" % (path, line))
                return 2
    elif a.as_ == "route":
        into = into or rules["lane_item"]
    line = {"sig": a.sig, "as": a.as_, "into": into, "by": seat, "ts": utcnow(), "why": (a.why or "").strip()}
    if decision_fault(line):
        print("REFUSED: %s" % decision_fault(line))
        return 2
    path = decisions_path(rules)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, sort_keys=True) + "\n")
    print("decided %s as %s -> %s. Commit %s by explicit path." % (a.sig, a.as_, into, os.path.relpath(path, REPO)))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", help="output folder (default: the rules file's `out`)")
    d = sub.add_parser("decide")
    d.add_argument("sig")
    d.add_argument("--as", dest="as_", required=True, choices=KINDS)
    d.add_argument("--into")
    d.add_argument("--why", required=True)
    d.add_argument("--seat")
    d.add_argument("--out")
    a = p.parse_args(argv)
    try:
        return cmd_run(a) if a.cmd == "run" else cmd_decide(a)
    except Unmeasured as e:
        print("findings_fold UNMEASURED: %s (nothing written)" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
