#!/usr/bin/env python3
"""findings_fold.py - the no-AI findings sorter (FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X).

Design: design/RimMandrake/findings_curation_design_2026-10-29.md option B, chosen by the owner by card 2026-10-29
("Program folds, FOUNDRY judges"). Runs after every testq ingest: the testq-tick unit's last ExecStart (testq.py UNITS),
output folder and rules: findings_fold_rules.json.

    findings_fold.py run [--no-notes] [--out DIR]     fold, write standing.json + curation.md, note the ledger
    findings_fold.py decide SIG --as KIND [--into X] --why "..." --seat SEAT     FOUNDRY records a judgment

What it does, with no AI:
  * signs every finding of the folded types (UNTRIAGED: what ingest.py files) by mod, chain, test row and the failure
    text with only explicitly volatile identifiers removed (job ids, UUIDs, timestamps, hex ids, thing ids, run
    numbers: rules `normalise`; error codes, values and file names stay). The text is the full done-record detail
    when the record is found, else the previous table's detail for that finding, else the ledger's line, and then the
    mod is unresolved and the finding is signed with its own name so it merges with nothing. Identical signatures
    fold into one row of the standing-failures table with count, first seen, last seen, the items it was filed under
    and every raw text. A finding is kept forever: one whose ledger event is gone is carried from the previous table
    and still stands in its signature;
  * a repeat of a DECIDED signature (a `rimflow spawn --from <finding>`, or a line FOUNDRY appended with `decide`) is
    MERGED into that decision: one RUNNER note on the decision item with the count, first and last seen;
  * a red canary, a refused pull or a machine-health row (rules machine_health_patterns) is ROUTED: a note on
    Operations' lane item;
  * a signature whose row passed `retire_after_passes` (3) runs in a row after the signature's own last FAIL is
    RETIRED, the runs as proof (a run that measured nothing, or another signature's FAIL, breaks the streak); a FAIL
    of that signature after it REOPENS it (back to FOUNDRY). A `retire` decision alone never retires: it waits for
    the proof (AWAITING_PROOF);
  * a signature still failing under an item in a `contradiction_states` state (done, validated) is a CONTRADICTION:
    a note on that item, and the first section of curation.md, even when it is also routed or decided;
  * everything else is NEW: FOUNDRY's daily judgment (curation.md), with the contradictions, the reopened and the stuck.
Merges and retirements are advisory until a non-maker has reviewed this program (design section 8): they change no
item state, they only add notes, and curation.md lists them for FOUNDRY and the Auditor's weekly sample.

Fails CLOSED: an unreadable ledger, done directory, done record (any field the fold reads of the wrong type),
previous table or decisions line exits 2 with UNMEASURED and writes nothing (the previous table, which holds raw
texts, is never overwritten by a blind run). One run at a time per output folder (a lock over read .. write); a run
that changes nothing writes nothing. While rules `live_notes` is false (or --no-notes) no ledger note is written.
Ledger notes go through ingest.py's note_once (idempotent by needle, seat RUNNER) and publish (the dispatch clone's
RUNNER publisher, under its clone lock).
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


def load_rules(path=None):
    path = path or os.environ.get("FINDINGS_FOLD_RULES") or RULES_PATH     # the env override: selftests only
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


def signature(mod, chain, row, text, rules, name=None):
    """A finding whose mod is unresolved ("?": no done record, no previous detail) is signed with its own NAME, so it
    never merges with another (two mods' failures could read alike under "?"; review finding 2)."""
    key = "\0".join([mod or "?", chain or "", row or "", normalise(text, rules)] +
                     (["unresolved:" + (name or "")] if (mod or "?") == "?" else []))
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
    """-> (mod, chain, row, raw text, provenance) for one finding event: "record" when its done record holds the FAIL
    row, "lane" for a paused-lane finding, else "ledger" (the ledger's line, mod unresolved)."""
    if (ev.get("name") or "").startswith("STEVE_LANE_"):
        m = LANE_NAME_RE.match(ev["name"])
        return "LANE", "", m.group("twist") if m else "PAUSED", ev.get("why") or "", "lane"
    m = WHY_RE.match(ev.get("why") or "")
    chain, row, detail = (m.group("chain"), m.group("row"), m.group("detail")) if m else ("", "", ev.get("why") or "")
    if rec is not None:
        res = rec.get("result") or {}
        cands = [r for r in res.get("rows") or [] if isinstance(r, dict) and r.get("verdict") == "FAIL"
                 and r.get("row") == row]
        pick = [r for r in cands if str(r.get("chain")) == chain] or cands
        if len(pick) == 1:
            r = pick[0]
            return (rec.get("job") or {}).get("mod") or "?", str(r.get("chain") or ""), row, \
                r.get("detail") or detail, "record"
    return "?", chain, row, detail, "ledger"


def rec_at(r):
    return (r.get("result") or {}).get("finished") or r.get("finished") or ""


def row_timelines(recs, rules):
    """(mod, chain, row) -> [(finished, verdict, job, fail signature or None)], oldest first. DONE records give their
    rows' verdicts (a FAIL carries the signature of its detail, None when it has none). A record that is not DONE
    (INVALID, INTERRUPTED, REFUSED: no measurement) puts an UNMEASURED on every row it holds AND every known row its
    selector covers (the job's chains, or all of the mod's rows for `full`, narrowed by `rows` prefixes), so a blind
    run breaks a pass streak (review finding 9)."""
    tl, blind = {}, []
    for r in recs:
        res = r.get("result") or {}
        at, job = rec_at(r), (r.get("job") or {}).get("id") or res.get("job") or "?"
        mod = (r.get("job") or {}).get("mod") or "?"
        done = res.get("outcome") == "DONE"
        for row in res.get("rows") or []:
            if not (isinstance(row, dict) and row.get("row")):
                continue
            key = (mod, str(row.get("chain") or ""), row["row"])
            if done:
                v = row.get("verdict")
                fs = signature(mod, key[1], key[2], row.get("detail"), rules) if v == "FAIL" and row.get("detail") \
                    else None
                tl.setdefault(key, []).append((at, v, job, fs))
            else:
                tl.setdefault(key, []).append((at, "UNMEASURED", job, None))
        if not done:
            blind.append((mod, (r.get("job") or {}).get("selector") or {}, at, job))
    for mod, sel, at, job in blind:
        chains = None if sel.get("full") else set(sel.get("chains") or [])
        pref = sel.get("rows") or None
        for key, v in tl.items():
            if key[0] != mod or (chains is not None and key[1] not in chains):
                continue
            if pref and not any(key[2] == p or key[2].startswith(p + "_") for p in pref):
                continue
            if not any(e[0] == at and e[2] == job for e in v):
                v.append((at, "UNMEASURED", job, None))
    for v in tl.values():
        v.sort(key=lambda e: (e[0], e[2]))
    return tl


def walk(timeline, need, sig, own_ts=()):
    """Retire/reopen state of ONE signature on its row (review finding 4). A PASS of the row is proof for every
    signature on it; a FAIL of THIS signature (or a FAIL whose detail is unknown) resets the streak and, after a
    retirement, reopens; a FAIL of ANOTHER signature, an UNMEASURED or a NOT_RUN breaks the streak and reopens nothing.
    own_ts: the signature's finding times, used as its FAILs only when no FAIL in the timeline carries it (the done
    record that held its row is gone)."""
    tl = list(timeline)
    if own_ts and not any(e[1] == "FAIL" and e[3] in (sig, None) for e in tl):
        tl = sorted(tl + [(t_, "FAIL", "finding", sig) for t_ in own_ts], key=lambda e: (e[0], e[2]))
    st = {"pass_streak": 0, "retired_at": None, "retire_proof": [], "reopened": 0, "reopened_at": None,
          "last_verdict": None}
    proof, seen_fail, retired = [], False, False
    for at, v, job, fs in tl:
        if v == "FAIL" and fs in (sig, None):
            if retired:
                st["reopened"] += 1
                st["reopened_at"] = at
            retired, seen_fail, proof = False, True, []
            st["retired_at"], st["retire_proof"] = None, []
            st["last_verdict"] = "FAIL"
        elif v == "PASS":
            proof.append({"job": job, "at": at})
            if seen_fail and len(proof) >= need and not retired:
                retired = True
                st["retired_at"], st["retire_proof"] = at, proof[-need:]
            st["last_verdict"] = "PASS"
        else:
            proof = []
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
    prev_raw = (prev or {}).get("raw") or {}
    raw, seen = {}, set()
    for e in events:
        if e.get("event") != "finding" or e.get("type") not in types or not e.get("name") or e["name"] in seen:
            continue
        seen.add(e["name"])
        mod, chain, row, text, prov = locate(e, idx.get(e["name"]))
        old = prev_raw.get(e["name"]) or {}
        if prov == "ledger" and old.get("mod") not in (None, "", "?"):
            # its done record is gone: the previous table's full detail and provenance stand (review finding 2)
            mod, chain, row, text, prov = old["mod"], old.get("chain") or "", old.get("row") or "", \
                old.get("text") or text, "prev"
        raw[e["name"]] = {"mod": mod, "chain": chain, "row": row, "text": text, "provenance": prov,
                          "why": e.get("why") or "", "item": e.get("id"), "ts": e.get("ts") or "",
                          "from": e.get("from")}
    in_ledger = len(raw)
    for n, r in prev_raw.items():
        if n not in raw:     # never lose a finding: its ledger event is gone, it still stands (review finding 3)
            raw[n] = dict(r, carried=True)
    by_sig = {}
    for n, r in raw.items():
        r["sig"] = signature(r.get("mod"), r.get("chain"), r.get("row"), r.get("text"), rules, name=n)
        by_sig.setdefault(r["sig"], []).append(n)
    decided = decisions_of(by_sig, events, decision_lines)
    tls = row_timelines(recs, rules)
    need = int(rules["retire_after_passes"])
    lane = rules["lane_item"]
    bad_states = set(rules["contradiction_states"])
    stuck_s = float(rules["stuck_after_days"]) * 86400
    sigs, actions = {}, []
    for s, names in sorted(by_sig.items()):
        names = sorted(names, key=lambda n: (raw[n].get("ts") or "", n))
        rs = [raw[n] for n in names]
        first = rs[0]
        items = sorted({r["item"] for r in rs if r.get("item")})
        row = {"mod": first.get("mod") or "?", "chain": first.get("chain") or "", "row": first.get("row") or "",
               "text": normalise(first.get("text"), rules), "count": len(rs), "first_seen": rs[0].get("ts") or "",
               "last_seen": rs[-1].get("ts") or "", "findings": names, "items": items,
               "carried": sum(1 for r in rs if r.get("carried"))}
        key = (row["mod"], row["chain"], row["row"])
        st = walk(tls[key], need, s, [r.get("ts") for r in rs if r.get("ts")]) \
            if row["mod"] != "?" and key in tls else None
        row.update({"pass_streak": st["pass_streak"] if st else 0, "retired_at": st["retired_at"] if st else None,
                    "retire_proof": st["retire_proof"] if st else [], "reopened": st["reopened"] if st else 0,
                    "timeline_runs": len(tls.get(key, [])) if st else 0})
        dec = decided.get(s)
        row["decision"] = dec
        texts = " ".join((r.get("text") or "") + " " + (r.get("why") or "") for r in rs)
        still_failing = not st or st["last_verdict"] != "PASS"
        reopened_here = bool(st and st["reopened"] and not st["retired"] and st["reopened_at"]
                             and row["last_seen"] >= st["reopened_at"][:len(row["last_seen"])])
        since = [n for n in names if dec and (raw[n].get("ts") or "") > (dec.get("ts") or "")]
        hosts = items + ([dec["into"]] if dec and dec.get("into") in item_states else [])
        # contradictions stand on their own: routing or a decision never hides one (review finding 6)
        contra = sorted({i for i in hosts if item_states.get(i) in bad_states}) if still_failing else []
        if lane in items or any(rx.search(texts) for rx in rules["_mh"]) or (dec and dec.get("as") == "route"):
            status = "ROUTED"
        elif st and st["retired"]:
            status = "RETIRED"           # only ever on passing proof (review finding 5)
        elif contra:
            status = "CONTRADICTION"
        elif reopened_here or (dec and dec.get("as") == "retire" and since):
            status = "REOPENED"
        elif dec and dec.get("as") == "retire":
            status = "AWAITING_PROOF"    # FOUNDRY judged it fixed; it retires when the row has passed `need` runs
        elif dec:
            status = "MERGED"
        else:
            status = "NEW"
        row["status"] = status
        row["contradicts"] = contra
        a_, b_ = epoch(dec.get("ts")) if dec else None, epoch(row["last_seen"])
        row["stuck"] = bool(status == "MERGED" and since and a_ is not None and b_ is not None and b_ - a_ >= stuck_s)
        tag = "findings_fold %s" % s
        summary = "count %d (first %s, last %s)" % (row["count"], row["first_seen"], row["last_seen"])
        what = "%s/%s/%s: %s" % (row["mod"], row["chain"], row["row"], row["text"][:140])
        for it in contra:
            actions.append({"kind": "contradiction", "item": it,
                            "needle": "%s CONTRADICTION on %s %s" % (tag, it, item_states.get(it)),
                            "text": "%s CONTRADICTION on %s %s: this row still fails (%s, %d pass(es) on "
                                    "record since); %s" % (tag, it, item_states.get(it), summary,
                                                           row["pass_streak"], what)})
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
    counts = {"findings": len(raw), "in_ledger": in_ledger, "distinct": len(sigs), "by_status": by_status,
              "contradictions": sum(1 for r in sigs.values() if r["contradicts"]), "routed": by_status.get("ROUTED", 0),
              "residue": sum(1 for r in sigs.values() if r["status"] in ("NEW", "REOPENED", "CONTRADICTION")
                             or r["contradicts"] or r["stuck"]),
              "raw_carried": sum(1 for r in raw.values() if r.get("carried")),
              "joined_to_records": sum(1 for r in raw.values() if r.get("provenance") in ("record", "prev")),
              "unresolved": sum(1 for r in raw.values() if (r.get("mod") or "?") == "?")}
    if sum(r["count"] for r in sigs.values()) != len(raw):   # conservation: one signature per finding, exactly
        raise Unmeasured("conservation broken: %d findings, %d in signatures"
                         % (len(raw), sum(r["count"] for r in sigs.values())))
    return {"schema": SCHEMA, "generated": now, "counts": counts, "signatures": sigs, "raw": raw, "actions": actions,
            "policy": {"retire_after_passes": need, "stuck_after_days": rules["stuck_after_days"]}}


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
    sect("CONTRADICTIONS: done or validated, still failing", lambda r: bool(r["contradicts"]),
         lambda r: " CONTRADICTS %s%s" % (",".join(r["contradicts"]),
                                          " (also routed)" if r["status"] == "ROUTED" else ""))
    sect("NEW: FOUNDRY judges (work / merge / memory / route / retire)", lambda r: r["status"] == "NEW")
    sect("REOPENED: retired or decided retired, failed again", lambda r: r["status"] == "REOPENED")
    pol = t.get("policy") or {}
    sect("STUCK: decided, still failing %s+ days later" % pol.get("stuck_after_days", "?"), lambda r: r["stuck"],
         lambda r: " decided %s into %s" % ((r["decision"] or {}).get("as"), (r["decision"] or {}).get("into")))
    sect("MERGED by the program (advisory: Auditor samples)", lambda r: r["status"] == "MERGED",
         lambda r: " -> %s %s" % ((r["decision"] or {}).get("as"), (r["decision"] or {}).get("into")))
    sect("RETIRED on passing proof (advisory: Auditor samples)", lambda r: r["status"] == "RETIRED",
         lambda r: " retired %s" % r["retired_at"])
    sect("AWAITING PROOF: decided retired, not yet %s passes" % pol.get("retire_after_passes", "?"), lambda r: r["status"] == "AWAITING_PROOF",
         lambda r: " decided %s, %d pass(es) so far" % ((r["decision"] or {}).get("ts"), r["pass_streak"]))
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
        why = record_fault(r)
        if why:
            raise Unmeasured("done record %s unreadable: %s" % (n, why))
        recs.append(r)
    return recs


VERDICTS = ("PASS", "FAIL", "UNMEASURED", "NOT_RUN")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def record_fault(r):
    """-> why a done record cannot be folded, or None (review finding 12: `{}` is not a record). Every field the fold
    reads is checked for its type: a job with a string id and mod, a result with a string outcome, a finish time,
    rows of {row, verdict in VERDICTS, chain/detail strings or absent}, a selector object, an ingested object."""
    if not isinstance(r, dict):
        return "not an object"
    job, res = r.get("job"), r.get("result")
    if not isinstance(job, dict) or not isinstance(job.get("id"), str) or not job.get("id") \
            or not isinstance(job.get("mod"), str) or not job.get("mod"):
        return "no job with an id and a mod"
    if not isinstance(job.get("selector", {}), dict):
        return "the job's selector is not an object"
    if not isinstance(res, dict) or not isinstance(res.get("outcome"), str) or not res.get("outcome"):
        return "no result with an outcome"
    if not ISO_RE.match(str(rec_at(r))) or epoch(rec_at(r)) is None:
        return "no finish time (got %r)" % rec_at(r)
    rows = res.get("rows", [])
    if rows is None:
        rows = []
    if not isinstance(rows, list):
        return "rows is not a list"
    if res["outcome"] == "DONE" and "rows" not in res:
        return "a DONE result with no rows"
    for k, x in enumerate(rows):
        if not isinstance(x, dict) or not isinstance(x.get("row"), str) or not x.get("row") \
                or x.get("verdict") not in VERDICTS:
            return "row %d is not {row, verdict}" % k
        for f in ("chain", "detail"):
            if x.get(f) is not None and not isinstance(x[f], str):
                return "row %d %s is not a string" % (k, f)
    if not isinstance(r.get("ingested") or {}, dict):
        return "ingested is not an object"
    return None


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
    """A unique temp file in the same folder, then one rename (review finding 7: two runs never share a temp)."""
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
def out_lock(od, wait_s):
    """One fold at a time per output folder, held over the whole read-previous .. write-new (review finding 7)."""
    with open(os.path.join(od, ".findings_fold.lock"), "a") as fh:
        end = time.time() + wait_s
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() >= end:
                    raise Unmeasured("another findings_fold run holds %s after %d s" % (od, wait_s))
                time.sleep(0.2)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def semantic(t):
    """The table without its run time: two runs that agree on this wrote the same thing (review finding 10)."""
    return json.dumps({k: v for k, v in (t or {}).items() if k != "generated"}, sort_keys=True)


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


def fold_and_note(rules, prev, recs, decs, push):
    """Live: the ledger is read, folded and noted under ONE hold of the clone lock (ingest.repo_lock, re-entrant),
    the lock every writer of this clone's ledger takes (ingest, the RUNNER publisher's pull/rebase), so no item can
    turn done between the snapshot the notes were chosen from and the notes (review finding 8). -> (table, notes)."""
    sys.path.insert(0, TESTQ)
    import ingest as I
    with I.repo_lock(120) as got:
        events, states = read_ledger()
        t = fold(events, states, recs, decs, prev, rules, utcnow())
        if not got:
            return t, {"written": 0, "errors": ["clone busy: no notes this run (retried next run)"], "publish": None}
        if not t["actions"]:
            return t, None
        n, errs, pub = apply_notes(t["actions"], push)
        return t, {"written": n, "errors": errs, "publish": pub}


def cmd_run(a):
    rules = load_rules()
    od = out_dir(a.out)
    os.makedirs(od, exist_ok=True)
    std, cur = os.path.join(od, "standing.json"), os.path.join(od, "curation.md")
    dry = bool(a.no_notes or not rules.get("live_notes", False))
    with out_lock(od, float(os.environ.get("FINDINGS_FOLD_LOCK_WAIT_S", "300"))):
        prev = read_prev(std)
        recs = read_done(queue_dir())
        decs = read_decisions(decisions_path(rules))
        if dry:
            events, states = read_ledger()
            t, notes = fold(events, states, recs, decs, prev, rules, utcnow()), None
            print("findings_fold: DRY (rules live_notes false or --no-notes): %d note(s) computed, none written"
                  % len(t["actions"]))
        else:
            t, notes = fold_and_note(rules, prev, recs, decs, os.environ.get("FINDINGS_FOLD_PUSH", "1") != "0")
        t["dry"] = dry
        if prev is not None and semantic(prev) == semantic(t) and os.path.isfile(cur):
            print("findings_fold: unchanged since %s: nothing written" % prev.get("generated"))
        else:
            write_atomic(std, json.dumps(t, indent=1, sort_keys=True))
            write_atomic(cur, render_md(t))
            print("findings_fold: %s -> %s" % (json.dumps(t["counts"], sort_keys=True), od))
    if notes:   # run telemetry: stdout (the journal), never the table, so a repeat run compares equal
        print("notes: %s" % json.dumps(notes)[:600])
    return 1 if (notes or {}).get("errors") else 0


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
