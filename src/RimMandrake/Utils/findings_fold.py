#!/usr/bin/env python3
"""findings_fold.py - the no-AI findings sorter (FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X).

Design: design/RimMandrake/findings_curation_design_2026-10-29.md option B, chosen by the owner by card 2026-10-29
("Program folds, FOUNDRY judges"). Runs after every testq ingest: the testq-tick unit's last ExecStart (testq.py UNITS),
output folder and rules: findings_fold_rules.json.

    findings_fold.py run [--no-notes] [--out DIR]     fold, write standing.json + curation.md, note the ledger
    findings_fold.py decide SIG --as KIND [--into X] --why "..." --seat SEAT     FOUNDRY records a judgment

What it does, with no AI:
  * signs every finding of the folded types (UNTRIAGED: what ingest.py files) by mod, chain, test row and the failure
    text with run numbers, timestamps, job ids and file names removed (the full done-record detail when the record is
    found, else the ledger's line); identical signatures fold into one row of the standing-failures table with count,
    first seen, last seen, the items it was filed under and every raw text (kept forever: a raw text whose done record
    is gone survives from the previous table);
  * a repeat of a DECIDED signature (a `rimflow spawn --from <finding>`, or a line FOUNDRY appended with `decide`) is
    MERGED into that decision: one RUNNER note on the decision item with the count, first and last seen;
  * a red canary, a refused pull or a machine-health row (rules machine_health_patterns) is ROUTED: a note on
    Operations' lane item;
  * a row that passed `retire_after_passes` (3) runs in a row after its last FAIL is RETIRED, the runs as proof; a FAIL
    after that REOPENS it (back to FOUNDRY);
  * a signature still failing under an item in a `contradiction_states` state (done, validated) is a CONTRADICTION:
    a note on that item, and the first section of curation.md;
  * everything else is NEW: FOUNDRY's daily judgment (curation.md), with the contradictions, the reopened and the stuck.
Merges and retirements are advisory until a non-maker has reviewed this program (design section 8): they change no
item state, they only add notes, and curation.md lists them for FOUNDRY and the Auditor's weekly sample.

Fails CLOSED: an unreadable ledger, done directory, done record, previous table or decisions line exits 2 with
UNMEASURED and writes nothing (the previous table, which holds raw texts, is never overwritten by a blind run).
Ledger notes go through ingest.py's note_once (idempotent by needle, seat RUNNER) and publish (the dispatch clone's
RUNNER publisher, under its clone lock).
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(REPO, "src", "RimMandrake", "rimflow")
TESTQ = os.path.join(HERE, "testq")
RULES_PATH = os.path.join(HERE, "findings_fold_rules.json")
SCHEMA = "findings_fold/1"
KINDS = ("work", "merge", "memory", "route", "retire", "undo")
WHY_RE = re.compile(r"^(?P<chain>[^/ ]*)/(?P<row>\S+) FAIL on (?P<host>\S+): (?P<detail>.*)$", re.S)
LANE_NAME_RE = re.compile(r"^STEVE_LANE_(?P<twist>.+)_[0-9A-F]{6}$")


class Unmeasured(Exception):
    """An input could not be read: the run stops, writes nothing, and says so."""


def utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def epoch(iso):
    try:
        return time.mktime(time.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    except (TypeError, ValueError):
        return None


def load_rules(path=RULES_PATH):
    try:
        with open(path, encoding="utf-8") as f:
            rules = json.load(f)
        for k in ("finding_types", "lane_item", "machine_health_patterns", "retire_after_passes",
                  "contradiction_states", "stuck_after_days", "decisions_file", "normalise", "memory_roots"):
            rules[k]
        rules["_mh"] = [re.compile(p) for p in rules["machine_health_patterns"]]
        rules["_norm"] = [(re.compile(p), r) for p, r in rules["normalise"]]
        return rules
    except (OSError, ValueError, KeyError, re.error) as e:
        raise Unmeasured("rules %s unreadable: %s: %s" % (path, type(e).__name__, e))


def normalise(text, rules):
    t = text or ""
    for rx, rep in rules["_norm"]:
        t = rx.sub(rep, t)
    return t.strip()


def signature(mod, chain, row, text, rules):
    key = "\0".join([mod or "?", chain or "", row or "", normalise(text, rules)])
    return "S" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]


# ------------------------------------------------------------------ joining findings to done records
def index_records(recs):
    """finding name -> (record, its ingest group's run). A name in two records is ambiguous: neither is used."""
    idx, dup = {}, set()
    for r in recs:
        ing = r.get("ingested") or {}
        groups = [ing] + [g for g in (ing.get("groups") or {}).values() if isinstance(g, dict)]
        names = [n for g in groups for n in (g.get("findings") or [])]
        if ing.get("lane_finding"):
            names.append(ing["lane_finding"])
        for n in names:
            if n in idx and idx[n] is not r:
                dup.add(n)
            idx[n] = r
    for n in dup:
        idx.pop(n, None)
    return idx


def locate(ev, rec):
    """-> (mod, chain, row, raw text) for one finding event, using its done record when the FAIL row is found."""
    if (ev.get("name") or "").startswith("STEVE_LANE_"):
        m = LANE_NAME_RE.match(ev["name"])
        return "LANE", "", m.group("twist") if m else "PAUSED", ev.get("why") or ""
    m = WHY_RE.match(ev.get("why") or "")
    chain, row, detail = (m.group("chain"), m.group("row"), m.group("detail")) if m else ("", "", ev.get("why") or "")
    if rec is not None:
        res = rec.get("result") or {}
        cands = [r for r in res.get("rows") or [] if isinstance(r, dict) and r.get("verdict") == "FAIL"
                 and r.get("row") == row]
        pick = [r for r in cands if str(r.get("chain")) == chain] or cands
        if len(pick) == 1:
            r = pick[0]
            return (rec.get("job") or {}).get("mod") or "?", str(r.get("chain") or ""), row, r.get("detail") or detail
    return "?", chain, row, detail


def row_timelines(recs):
    """(mod, chain, row) -> [(finished, verdict, job)] over every DONE record, oldest first."""
    tl = {}
    for r in recs:
        res = r.get("result") or {}
        if res.get("outcome") != "DONE":
            continue
        at = res.get("finished") or r.get("finished") or ""
        mod = (r.get("job") or {}).get("mod") or "?"
        job = (r.get("job") or {}).get("id") or res.get("job") or "?"
        for row in res.get("rows") or []:
            if isinstance(row, dict) and row.get("row"):
                tl.setdefault((mod, str(row.get("chain") or ""), row["row"]), []).append(
                    (at, row.get("verdict"), job))
    for v in tl.values():
        v.sort()
    return tl


def walk(timeline, need):
    """Retire/reopen state of one row from its timeline. A streak counts PASSes after a FAIL; anything else that is not
    a PASS (UNMEASURED, ...) breaks it; a FAIL after a retirement reopens."""
    st = {"pass_streak": 0, "retired_at": None, "retire_proof": [], "reopened": 0, "reopened_at": None,
          "last_verdict": None}
    proof, seen_fail, retired = [], False, False
    for at, v, job in timeline:
        if v == "FAIL":
            if retired:
                st["reopened"] += 1
                st["reopened_at"] = at
            retired, seen_fail, proof = False, True, []
            st["retired_at"], st["retire_proof"] = None, []
        elif v == "PASS":
            proof.append({"job": job, "at": at})
            if seen_fail and len(proof) >= need and not retired:
                retired = True
                st["retired_at"], st["retire_proof"] = at, proof[-need:]
        else:
            proof = []
        if v in ("PASS", "FAIL"):
            st["last_verdict"] = v
        st["pass_streak"] = len(proof)
    st["retired"] = retired
    return st


# ------------------------------------------------------------------ decisions
def decisions_of(names_by_sig, events, lines):
    """sig -> the latest decision {as, into, by, ts, why, src}: a spawn whose `from` is one of the signature's findings
    (as work, into the spawned item), or a decisions-file line. `undo` cancels what came before it."""
    owner = {n: s for s, ns in names_by_sig.items() for n in ns}
    cand = {}
    for e in events:
        if e.get("event") == "spawn" and e.get("from") in owner:
            cand.setdefault(owner[e["from"]], []).append(
                {"as": "work", "into": e.get("name"), "by": e.get("seat"), "ts": e.get("ts") or "",
                 "why": "spawned from %s" % e["from"], "src": "ledger"})
    for d in lines:
        if d.get("sig") in names_by_sig:
            cand.setdefault(d["sig"], []).append(dict(d, src="decisions"))
    out = {}
    for s, ds in cand.items():
        last = sorted(ds, key=lambda d: d.get("ts") or "")[-1]
        if last.get("as") != "undo":
            out[s] = last
    return out


# ------------------------------------------------------------------ the fold
def fold(events, item_states, recs, decision_lines, prev, rules, now):
    """Pure. events: the ledger (dicts); item_states: id -> state; recs: testq done records; decision_lines: the
    decisions file; prev: the previous standing table or None. -> the new table, with `actions` (ledger notes)."""
    types = set(rules["finding_types"])
    idx = index_records(recs)
    raw, seen = {}, set()
    for e in events:
        if e.get("event") != "finding" or e.get("type") not in types or not e.get("name") or e["name"] in seen:
            continue
        seen.add(e["name"])
        mod, chain, row, text = locate(e, idx.get(e["name"]))
        raw[e["name"]] = {"sig": signature(mod, chain, row, text, rules), "mod": mod, "chain": chain, "row": row,
                          "text": text, "why": e.get("why") or "", "item": e.get("id"), "ts": e.get("ts") or "",
                          "from": e.get("from")}
    in_scope = len(raw)
    for n, r in ((prev or {}).get("raw") or {}).items():
        if n not in raw:                       # never lose a raw text: its record or event may be gone
            raw[n] = dict(r, carried=True)
    by_sig = {}
    for n, r in raw.items():
        if not r.get("carried"):
            by_sig.setdefault(r["sig"], []).append(n)
    decided = decisions_of(by_sig, events, decision_lines)
    tls = row_timelines(recs)
    need = int(rules["retire_after_passes"])
    lane = rules["lane_item"]
    bad_states = set(rules["contradiction_states"])
    stuck_s = float(rules["stuck_after_days"]) * 86400
    sigs, actions = {}, []
    for s, names in sorted(by_sig.items()):
        rs = sorted((raw[n] for n in names), key=lambda r: r["ts"])
        names = [n for n in sorted(names, key=lambda n: raw[n]["ts"])]
        first = rs[0]
        items = sorted({r["item"] for r in rs if r["item"]})
        row = {"mod": first["mod"], "chain": first["chain"], "row": first["row"],
               "text": normalise(first["text"], rules), "count": len(rs), "first_seen": rs[0]["ts"],
               "last_seen": rs[-1]["ts"], "findings": names, "items": items}
        key = (first["mod"], first["chain"], first["row"])
        st = walk(tls.get(key, []), need) if first["mod"] != "?" and key in tls else None
        row.update({"pass_streak": st["pass_streak"] if st else 0, "retired_at": st["retired_at"] if st else None,
                    "retire_proof": st["retire_proof"] if st else [], "reopened": st["reopened"] if st else 0,
                    "timeline_runs": len(tls.get(key, [])) if st else 0})
        dec = decided.get(s)
        row["decision"] = dec
        texts = " ".join(r["text"] + " " + r["why"] for r in rs)
        still_failing = not st or st["last_verdict"] != "PASS"
        reopened_here = bool(st and st["reopened"] and not st["retired"] and st["reopened_at"]
                             and row["last_seen"] >= st["reopened_at"][:len(row["last_seen"])])
        hosts = items + ([dec["into"]] if dec and dec.get("into") in item_states else [])
        contra = sorted({i for i in hosts if item_states.get(i) in bad_states})
        if lane in items or any(rx.search(texts) for rx in rules["_mh"]) or (dec and dec.get("as") == "route"):
            status = "ROUTED"
        elif st and st["retired"]:
            status = "RETIRED"
        elif dec and dec.get("as") == "retire" and row["last_seen"] <= (dec.get("ts") or ""):
            status = "RETIRED"
        elif contra and still_failing:
            status = "CONTRADICTION"
        elif reopened_here or (dec and dec.get("as") == "retire"):
            status = "REOPENED"
        elif dec:
            status = "MERGED"
        else:
            status = "NEW"
        row["status"] = status
        row["contradicts"] = contra if status == "CONTRADICTION" else []
        since = [n for n in names if dec and raw[n]["ts"] > (dec.get("ts") or "")]
        a, b = epoch(dec.get("ts")) if dec else None, epoch(row["last_seen"])
        row["stuck"] = bool(status == "MERGED" and since and a is not None and b is not None and b - a >= stuck_s)
        tag = "findings_fold %s" % s
        summary = "count %d (first %s, last %s)" % (row["count"], row["first_seen"], row["last_seen"])
        what = "%s/%s/%s: %s" % (row["mod"], row["chain"], row["row"], row["text"][:140])
        if status == "ROUTED":
            actions.append({"kind": "route", "item": lane, "needle": "%s route through %s" % (tag, names[-1]),
                            "text": "%s route through %s: lane or machine health, %s; %s" % (
                                tag, names[-1], summary, what)})
        elif status == "RETIRED" and row["retired_at"]:
            for it in items:
                actions.append({"kind": "retire", "item": it, "needle": "%s retire at %s" % (tag, row["retired_at"]),
                                "text": "%s retire at %s: %d passes in a row after the last FAIL (%s); %s; %s" % (
                                    tag, row["retired_at"], need,
                                    ", ".join(p["job"] for p in row["retire_proof"]), summary, what)})
        elif status == "CONTRADICTION":
            for it in contra:
                actions.append({"kind": "contradiction", "item": it,
                                "needle": "%s CONTRADICTION on %s %s" % (tag, it, item_states.get(it)),
                                "text": "%s CONTRADICTION on %s %s: this row still fails (%s, %d pass(es) on "
                                        "record since); %s" % (tag, it, item_states.get(it), summary,
                                                               row["pass_streak"], what)})
        elif status == "REOPENED":
            for it in items:
                actions.append({"kind": "reopen", "item": it, "needle": "%s reopen by %s" % (tag, names[-1]),
                                "text": "%s reopen by %s: a retired row failed again; %s; %s" % (
                                    tag, names[-1], summary, what)})
        elif status == "MERGED" and since and dec.get("into") in item_states:
            actions.append({"kind": "merge", "item": dec["into"],
                            "needle": "%s merge through %s" % (tag, since[-1]),
                            "text": "%s merge through %s: %d repeat(s) since the decision of %s, %s; %s" % (
                                tag, since[-1], len(since), dec.get("ts"), summary, what)})
        sigs[s] = row
    by_status = {}
    for r in sigs.values():
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    counts = {"findings": in_scope, "distinct": len(sigs), "by_status": by_status,
              "contradictions": by_status.get("CONTRADICTION", 0), "routed": by_status.get("ROUTED", 0),
              "residue": sum(1 for r in sigs.values() if r["status"] in ("NEW", "REOPENED", "CONTRADICTION")
                             or r["stuck"]),
              "raw_carried": sum(1 for r in raw.values() if r.get("carried")),
              "joined_to_records": sum(1 for r in raw.values() if not r.get("carried") and r["mod"] not in ("?", "LANE"))}
    if sum(r["count"] for r in sigs.values()) != in_scope:   # conservation: one signature per finding, exactly
        raise Unmeasured("conservation broken: %d findings, %d in signatures"
                         % (in_scope, sum(r["count"] for r in sigs.values())))
    return {"schema": SCHEMA, "generated": now, "counts": counts, "signatures": sigs, "raw": raw, "actions": actions}


# ------------------------------------------------------------------ curation.md (FOUNDRY reads it)
def render_md(t):
    sigs, c = t["signatures"], t["counts"]
    out = ["# Findings fold %s" % t["generated"], "",
           "%d findings, %d distinct failures; by status %s. Program merges and retirements are advisory (design "
           "section 8). Table: standing.json." % (c["findings"], c["distinct"], json.dumps(c["by_status"],
                                                                                          sort_keys=True)), ""]

    def sect(title, pick, extra=lambda r: ""):
        rows = sorted(((s, r) for s, r in sigs.items() if pick(r)), key=lambda x: (-x[1]["count"], x[0]))
        out.append("## %s (%d)" % (title, len(rows)))
        for s, r in rows:
            out.append("- `%s` x%d %s..%s %s/%s/%s under %s%s: %s" % (
                s, r["count"], r["first_seen"][:10], r["last_seen"][:10], r["mod"], r["chain"], r["row"],
                ",".join(r["items"]) or "-", extra(r), r["text"][:200]))
        out.append("")
    sect("CONTRADICTIONS: done or validated, still failing", lambda r: r["status"] == "CONTRADICTION",
         lambda r: " CONTRADICTS %s" % ",".join(r["contradicts"]))
    sect("NEW: FOUNDRY judges (work / merge / memory / route / retire)", lambda r: r["status"] == "NEW")
    sect("REOPENED: retired or decided retired, failed again", lambda r: r["status"] == "REOPENED")
    sect("STUCK: decided, still failing %s+ days later" % "3", lambda r: r["stuck"],
         lambda r: " decided %s into %s" % ((r["decision"] or {}).get("as"), (r["decision"] or {}).get("into")))
    sect("MERGED by the program (advisory: Auditor samples)", lambda r: r["status"] == "MERGED",
         lambda r: " -> %s %s" % ((r["decision"] or {}).get("as"), (r["decision"] or {}).get("into")))
    sect("RETIRED (advisory: Auditor samples)", lambda r: r["status"] == "RETIRED",
         lambda r: " retired %s" % (r["retired_at"] or (r["decision"] or {}).get("ts")))
    sect("ROUTED to Operations", lambda r: r["status"] == "ROUTED")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ inputs (each fails closed)
def read_ledger():
    sys.path.insert(0, RIMFLOW)
    try:
        import model
        if os.environ.get("RIMFLOW_LEDGER"):          # the selftest redirect, as ingest.recorded_run binds it
            model.EVENTS = os.environ["RIMFLOW_LEDGER"]
        events = model.read()
        world = model.replay(events)
    except Exception as e:  # noqa: BLE001 - every ledger failure is UNMEASURED
        raise Unmeasured("ledger unreadable: %s: %s" % (type(e).__name__, str(e)[:200]))
    return events, {i: it.state for i, it in world.items.items()}


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
    recs = []
    for n in names:
        try:
            with open(os.path.join(d, n), encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError) as e:
            raise Unmeasured("done record %s unreadable: %s" % (n, e))
        if not isinstance(r, dict):
            raise Unmeasured("done record %s is not an object" % n)
        recs.append(r)
    return recs


def decisions_path(rules):
    return os.environ.get("FINDINGS_FOLD_DECISIONS") or os.path.join(REPO, rules["decisions_file"])


def read_decisions(path):
    if not os.path.exists(path):
        return []                                   # legitimately absent until FOUNDRY's first decision
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for k, line in enumerate(f, 1):
                if line.strip():
                    d = json.loads(line)
                    if not isinstance(d, dict) or d.get("as") not in KINDS or not d.get("sig"):
                        raise ValueError("line %d is not a decision" % k)
                    out.append(d)
    except (OSError, ValueError) as e:
        raise Unmeasured("decisions %s unreadable: %s" % (path, e))
    return out


def out_dir(override=None):
    if override or os.environ.get("FINDINGS_FOLD_OUT"):
        return override or os.environ["FINDINGS_FOLD_OUT"]
    sys.path.insert(0, HERE)
    from game_paths import win_to_wsl
    return win_to_wsl(load_rules()["out"])


def read_prev(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            t = json.load(f)
        if t.get("schema") != SCHEMA or not isinstance(t.get("raw"), dict):
            raise ValueError("schema %r" % t.get("schema"))
        return t
    except (OSError, ValueError, AttributeError) as e:
        raise Unmeasured("previous table %s unreadable (it holds raw texts: not overwritten): %s" % (path, e))


def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


# ------------------------------------------------------------------ ledger notes
def apply_notes(actions, push):
    """Each action is one RUNNER note, written once (ingest.note_once greps the shard for its needle). Under the
    clone lock; then the RUNNER publisher. -> (written, errors, publish result)."""
    sys.path.insert(0, TESTQ)
    import ingest as I
    with I.repo_lock(120) as got:
        if not got:
            return 0, ["clone busy: another ingest/publish holds it (retried next run)"], None
        if I.rebase_left(clear=push):
            return 0, ["a rebase is in progress in the clone (retried next run)"], None
        n, errs = 0, []
        for a in actions:
            before = os.path.getsize(I.shard_path()) if os.path.exists(I.shard_path()) else 0
            if not I.note_once(a["item"], a["needle"], a["text"]):
                errs.append("note refused on %s: %s" % (a["item"], a["needle"]))
            elif (os.path.getsize(I.shard_path()) if os.path.exists(I.shard_path()) else 0) != before:
                n += 1
        pub = I.publish(n, message="ledger: findings fold, %d note(s)" % n) if push and (n or I.unpublished()) \
            else None
    return n, errs, pub


def cmd_run(a):
    rules = load_rules()
    od = out_dir(a.out)
    os.makedirs(od, exist_ok=True)
    std = os.path.join(od, "standing.json")
    prev = read_prev(std)
    events, states = read_ledger()
    recs = read_done(queue_dir())
    decs = read_decisions(decisions_path(rules))
    t = fold(events, states, recs, decs, prev, rules, utcnow())
    if not a.no_notes and t["actions"]:
        n, errs, pub = apply_notes(t["actions"], os.environ.get("FINDINGS_FOLD_PUSH", "1") != "0")
        t["notes"] = {"written": n, "errors": errs, "publish": pub}
    write_atomic(std, json.dumps(t, indent=1, sort_keys=True))
    write_atomic(os.path.join(od, "curation.md"), render_md(t))
    print("findings_fold: %s -> %s" % (json.dumps(t["counts"], sort_keys=True), od))
    if t.get("notes"):
        print("notes: %s" % json.dumps(t["notes"])[:600])
    return 1 if (t.get("notes") or {}).get("errors") else 0


def cmd_decide(a):
    rules = load_rules()
    seat = a.seat or os.environ.get("RIMFLOW_SEAT")
    if not seat:
        print("REFUSED: --seat (or RIMFLOW_SEAT) names who decided")
        return 2
    t = read_prev(os.path.join(out_dir(a.out), "standing.json"))
    if not t or a.sig not in t.get("signatures", {}):
        print("REFUSED: %s is not in the standing table (run `findings_fold.py run` first)" % a.sig)
        return 2
    into = a.into
    if a.as_ in ("work", "merge"):
        _, states = read_ledger()
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
    if not (a.why or "").strip():
        print("REFUSED: --why is required")
        return 2
    path = decisions_path(rules)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = {"sig": a.sig, "as": a.as_, "into": into, "by": seat, "ts": utcnow(), "why": a.why.strip()}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, sort_keys=True) + "\n")
    print("decided %s as %s -> %s. Commit %s by explicit path." % (a.sig, a.as_, into, os.path.relpath(path, REPO)))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--no-notes", action="store_true", help="fold and write the table only; no ledger notes")
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
