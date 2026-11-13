#!/usr/bin/env python3
"""findings_fold_vet_notes.py - re-derive the RUNNER findings_fold notes of 2026-10-29T20:4xZ with the reviewed fold
(FINDINGS_FOLD_VET_NOTES_BEAT_THE_REVIEW).

Those notes (retire / reopen / route / CONTRADICTION) were written live by the first findings_fold.py (4c0b13067d),
before three blind reviews found its merges inexact (it normalised every number, hex id, file name and run of spaces
away, and walked retirement over the whole row). This re-derives each one with the reviewed program, as of the time
the notes were written (ledger events, done records and decisions stamped no later than the earliest note):

  * the note's old group is rebuilt with the first program's signature (its normalise rules are frozen below as
    OLD_NORMALISE, its join of a finding to its done record as old_locate), so the findings the note spoke for are known;
  * each of them is placed in the reviewed program's exact signature (findings_fold.fold);
  * a claim HOLDS when the old group is one exact signature and the reviewed evidence agrees with the claim:
      retire         every passes_since >= 3 (the first program's retire_after_passes) and the row's latest verdict PASS
      reopen         the reopening finding's exact failure had been seen before and the row then passed >= 3 distinct
                     runs before it failed again (else it is a NEW failure, not that one back)
      route          the reviewed fold labels the signature HEALTH (machine or lane health, Operations' lane item)
      CONTRADICTION  the reviewed fold lists that item and row as a contradiction
    otherwise it is a CORRECTION, with its reasons; a claim that holds for every exact signature of a group the
    reviewed fold splits, or whose count or pass count it does not reproduce, is INEXACT. Both get a correction note.

    findings_fold_vet_notes.py [--done DIR]            print the verdicts
    findings_fold_vet_notes.py --write [--done DIR]    write VERDICTS (committed)
    findings_fold_vet_notes.py --check [--done DIR]    exit 0 only if VERDICTS equals the re-derivation and every
                                                       non-HOLDS verdict has its correction note on that item in the ledger
The correction notes are posted with `rimflow note <item>`; their text starts with NOTE_PREFIX, the old tag and kind.
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import findings_fold as FF  # noqa: E402

ITEM = "FINDINGS_FOLD_VET_NOTES_BEAT_THE_REVIEW"
NOTE_PREFIX = ITEM + " correction"
VERDICTS = os.path.join(REPO, "infrastructure", "state", "findings", "fold_notes_vet_2026-10-29.json")
DONE = "/mnt/d/ClaudeWork/rimmandrake/testq/done"
RETIRE_AFTER = 3                                    # the first program's retire_after_passes
NOTE_RE = re.compile(r"^findings_fold (?P<tag>S[0-9a-f]{10}) (?P<kind>retire|reopen|route|CONTRADICTION)\b")
REOPEN_RE = re.compile(r"^findings_fold S[0-9a-f]{10} reopen by (?P<name>\S+):")
ROUTE_RE = re.compile(r"^findings_fold S[0-9a-f]{10} route through (?P<name>\S+):")
CONTRA_RE = re.compile(r"^findings_fold S[0-9a-f]{10} CONTRADICTION on (?P<item>\S+) (?P<state>\S+):")
CLAIM_RE = re.compile(r"count (?P<count>\d+) \(first ")
SINCE_RE = re.compile(r"\), (?P<n>\d+) pass\(es\) on record since\)")
PROOF_RE = re.compile(r"passes in a row after the last FAIL \((?P<jobs>[^)]*)\)")
WINDOW = ("2026-10-29T20:40:00Z", "2026-10-29T20:50:00Z")   # the one live run of 4c0b13067d

# the first program's normalise rules (4c0b13067d findings_fold_rules.json), frozen: they define the old groups
OLD_NORMALISE = [(re.compile(p), r) for p, r in [
    [r"J\d{8}T\d{6}Z-[0-9a-fA-F]{6}(?:\.a\d+)?", "<job>"],
    [r"\d{8}T\d{6}Z?", "<ts>"],
    [r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?Z?", "<ts>"],
    [r"[\w.\\/:-]*[\w-]\.(?:json|jsonl|html|png|log|xml|txt|rws|py|csv)\b", "<file>"],
    [r"\b(?=[0-9a-fA-F]*\d)[0-9a-fA-F]{7,40}\b", "<hex>"],
    [r"\d+(?:\.\d+)?", "#"],
    [r"\s+", " "]]]
OLD_LANE_RE = re.compile(r"^STEVE_LANE_(?P<twist>.+)_[0-9A-F]{6}$")


def old_sig(mod, chain, row, text):
    t = text or ""
    for rx, rep in OLD_NORMALISE:
        t = rx.sub(rep, t)
    return "S" + hashlib.sha1("\0".join([mod or "?", chain or "", row or "", t.strip()]).encode("utf-8")).hexdigest()[:10]


def old_index(recs):
    idx, dup = {}, set()
    for r in recs:
        ing = r.get("ingested") or {}
        groups = [ing] + [g for g in (ing.get("groups") or {}).values() if isinstance(g, dict)]
        names = [n for g in groups for n in (g.get("findings") or [])] + \
            ([ing["lane_finding"]] if ing.get("lane_finding") else [])
        for n in names:
            if n in idx and idx[n] is not r:
                dup.add(n)
            idx[n] = r
    for n in dup:
        idx.pop(n, None)
    return idx


def old_locate(ev, rec):
    if (ev.get("name") or "").startswith("STEVE_LANE_"):
        m = OLD_LANE_RE.match(ev["name"])
        return "LANE", "", m.group("twist") if m else "PAUSED", ev.get("why") or ""
    m = FF.WHY_RE.match(ev.get("why") or "")
    chain, row, detail = (m.group("chain"), m.group("row"), m.group("detail")) if m else ("", "", ev.get("why") or "")
    if rec is not None:
        res = rec.get("result") or {}
        cands = [x for x in res.get("rows") or [] if isinstance(x, dict) and x.get("verdict") == "FAIL"
                 and x.get("row") == row]
        pick = [x for x in cands if str(x.get("chain")) == chain] or cands
        if len(pick) == 1:
            return (rec.get("job") or {}).get("mod") or "?", str(pick[0].get("chain") or ""), row, \
                pick[0].get("detail") or detail
    return "?", chain, row, detail


# ------------------------------------------------------------------ inputs as of the cutoff
def ledger_events():
    sys.path.insert(0, FF.RIMFLOW)
    import model
    if os.environ.get("RIMFLOW_LEDGER"):              # the redirect FF.read_ledger honours, applied to every read here
        model.EVENTS = os.environ["RIMFLOW_LEDGER"]
    return model.read()


def decisions_as_of(path, cutoff):
    """FF.read_decisions, but a line stamped after the cutoff is skipped before it is judged: a later line, even a
    malformed one, cannot change (or break) this historical derivation."""
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for k, line in enumerate(f, 1):
                if not line.strip():
                    continue
                d = json.loads(line)
                if isinstance(d, dict) and isinstance(d.get("ts"), str) and FF.ISO_RE.match(d["ts"]) \
                        and d["ts"] > cutoff:
                    continue
                if FF.decision_fault(d):
                    raise ValueError("line %d: %s" % (k, FF.decision_fault(d)))
                out.append(d)
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as e:
        raise FF.Unmeasured("decisions %s unreadable: %s" % (path, e))
    return out


def must(rx, text):
    m = rx.match(text)
    if not m:
        raise FF.Unmeasured("a findings_fold note this vet cannot parse: %r" % text)
    return m


def old_notes(events):
    out = []
    for e in events:
        t = e.get("text") or ""
        if e.get("seat") == "RUNNER" and e.get("event") == "note" and t.startswith("findings_fold ") and \
                WINDOW[0] <= str(e.get("ts")) <= WINDOW[1]:
            m = NOTE_RE.match(t)
            if not m:
                raise FF.Unmeasured("a findings_fold note this vet cannot parse: %r" % t)
            out.append({"tsn": e.get("tsn"), "ts": e["ts"], "item": e["id"], "tag": m.group("tag"),
                        "kind": m.group("kind"), "text": t})
    return out


def done_as_of(ddir, cutoff):
    recs, ids = [], set()
    for n in sorted(os.listdir(ddir)):
        if not n.endswith(".json"):
            continue
        with open(os.path.join(ddir, n), encoding="utf-8") as f:
            r = json.load(f)
        fin = ((r.get("result") or {}).get("finished")) if isinstance(r, dict) and \
            isinstance(r.get("result"), dict) else None
        if isinstance(fin, str) and FF.ISO_RE.match(fin) and fin > cutoff:
            continue                                # finished after the notes were written: not their input
        # an undated record is judged (and refused) like any other: it cannot be skipped as "later"
        # no ingest lock is taken: every input kept is stamped no later than the cutoff, which ingest only appends past,
        # and the checker reads the queue folder read-only
        why = FF.record_fault(r) or ("job %s is in two done files" % r["job"]["id"] if r["job"]["id"] in ids else None)
        if why:
            raise FF.Unmeasured("done record %s unreadable: %s" % (n, why))
        ids.add(r["job"]["id"])
        recs.append(r)
    return recs


def reviewed_fold(events, recs, cutoff, rules):
    sys.path.insert(0, FF.RIMFLOW)
    import model
    early = [e for e in events if str(e.get("ts") or "") <= cutoff]
    real = model.read
    model.read = lambda *a, **k: early
    try:
        finds, spawns, states, timeline = FF.read_ledger(rules)
    finally:
        model.read = real
    lines = decisions_as_of(FF.decisions_path(rules), cutoff)
    t = FF.fold(finds, spawns, states, recs, lines, rules, cutoff, timeline)
    return t, early


# ------------------------------------------------------------------ the vet
def derive(ddir):
    rules = FF.load_rules()
    events = ledger_events()
    notes = old_notes(events)
    if not notes:
        raise FF.Unmeasured("no findings_fold notes in the 2026-10-29T20:4x window: the instrument sees nothing")
    cutoff = min(n["ts"] for n in notes)
    recs = done_as_of(ddir, cutoff)
    t, early = reviewed_fold(events, recs, cutoff, rules)
    sig_of = {n: r["sig"] for n, r in t["raw"].items()}
    old_idx, seen, old_groups = old_index(recs), set(), {}
    for e in early:
        if e.get("event") != "finding" or e.get("type") not in rules["finding_types"] or not e.get("name") \
                or e["name"] in seen:
            continue
        seen.add(e["name"])
        mod, chain, row, text = old_locate(e, old_idx.get(e["name"]))
        old_groups.setdefault(old_sig(mod, chain, row, text), []).append(e["name"])
    runs = FF.row_runs(recs)
    out = []
    for n in sorted(notes, key=lambda n: (n["ts"], n["tsn"] or 0)):
        names = old_groups.get(n["tag"], [])
        v = {"note_ts": n["ts"], "note_tsn": n["tsn"], "item": n["item"], "tag": n["tag"], "kind": n["kind"],
             "claim": n["text"], "old_findings": sorted(names), "reasons": [], "inexact": []}
        sigs = sorted({sig_of[x] for x in names if x in sig_of})
        v["reviewed"] = [{"sig": s[:13], "count": t["signatures"][s]["count"],
                          "first_seen": t["signatures"][s]["first_seen"], "last_seen": t["signatures"][s]["last_seen"],
                          "passes_since": t["signatures"][s]["passes_since"],
                          "row_latest": (t["signatures"][s]["row_latest"] or {}).get("verdict"),
                          "status": t["signatures"][s]["status"], "items": t["signatures"][s]["items"],
                          "findings": t["signatures"][s]["findings"]} for s in sigs]
        if not names:
            v["reasons"].append("the old group %s cannot be rebuilt from the ledger and done records as of %s"
                                % (n["tag"], cutoff))
        elif n["kind"] in ("retire", "reopen") and not any(t["raw"][x]["item"] == n["item"] for x in names
                                                            if x in t["raw"]):
            # retire and reopen went to each item of the group; route went to the lane item, CONTRADICTION to the
            # contradicted item (judged against the reviewed contradictions below)
            v["reasons"].append("no finding of the old group is on %s" % n["item"])
        if len(sigs) > 1:
            v["inexact"].append("inexact merge: the old group's %d findings are %d different failures (exact "
                                "signatures %s)" % (len(names), len(sigs), ", ".join(s[:13] for s in sigs)))
        elif len(sigs) == 1:
            s = t["signatures"][sigs[0]]
            # the count only: the old note stamped first/last with the ledger event's time, the reviewed fold with
            # the done record's finish, so those two differ by the ingest delay on every row and say nothing
            c = CLAIM_RE.search(n["text"])
            if c and int(c.group("count")) != s["count"]:
                v["inexact"].append("the note says count %s; the exact signature has count %d"
                                    % (c.group("count"), s["count"]))
        mine = [t["signatures"][s] for s in sigs]
        if n["kind"] == "retire":
            proof = PROOF_RE.search(n["text"])
            for job in (proof.group("jobs").split(", ") if proof else []):
                if not any(j == job and v_ == "PASS" for r in mine for _, j, v_, _, _ in
                           runs.get((r["mod"], r["chain"], r["row"]), [])):
                    v["reasons"].append("proof run %s is not a PASS of this row in the done records" % job)
            for s, r in zip(sigs, mine):
                if r["passes_since"] < RETIRE_AFTER or (r["row_latest"] or {}).get("verdict") != "PASS":
                    v["reasons"].append("retire does not hold for %s: %d distinct passing run(s) after its last "
                                        "failure, row latest %s" % (s[:13], r["passes_since"],
                                                                     (r["row_latest"] or {}).get("verdict")))
        elif n["kind"] == "reopen":
            name = must(REOPEN_RE, n["text"]).group("name")
            v["reasons"] += reopen_reasons(name, t, runs, rules)
        elif n["kind"] == "route":
            name = must(ROUTE_RE, n["text"]).group("name")
            if name not in t["raw"]:
                v["reasons"].append("%s is not a folded finding as of %s" % (name, cutoff))
            for s, r in zip(sigs, mine):                # every failure the note routed, not only the one it named
                if not r["health"]:
                    v["reasons"].append("the reviewed fold does not label %s (%s) machine or lane health"
                                        % (s[:13], ", ".join(r["findings"])))
        elif n["kind"] == "CONTRADICTION":
            m = must(CONTRA_RE, n["text"])
            rowname = n["text"].split(" on record since); ", 1)[1].split(": ", 1)[0] \
                if " on record since); " in n["text"] else ""
            hit = [c for c in t["contradictions"] if c["item"] == m.group("item") and
                   "%s/%s/%s" % (c["mod"], c["chain"], c["row"]) == rowname]   # the whole mod/chain/row, exactly
            said = SINCE_RE.search(n["text"])
            for r in mine:
                if said and int(said.group("n")) != r["passes_since"]:
                    v["inexact"].append("the note says %s pass(es) on record since; the reviewed fold counts %d distinct "
                                        "passing run(s) of the row after this failure (another item's runs)"
                                        % (said.group("n"), r["passes_since"]))
            if not hit:
                v["reasons"].append("the reviewed fold finds no contradiction of %s on %s: that item's own latest "
                                    "measured verdict of the row is not FAIL" % (m.group("item"), rowname or "?"))
        # CORRECTION: the claim itself does not hold; INEXACT: it holds for every exact signature, but the
        # note spoke for a group the reviewed fold splits, or gave a count it does not reproduce
        v["verdict"] = "CORRECTION" if v["reasons"] else "INEXACT" if v["inexact"] else "HOLDS"
        out.append(v)
    return {"schema": "findings_fold_vet/1", "cutoff": cutoff, "program": "findings_fold.py (reviewed: exact "
            "signature, 981787da49 rules and later fixes)", "records": len(recs),
            "counts": {k: sum(1 for v in out if v["verdict"] == k) for k in ("HOLDS", "INEXACT", "CORRECTION")},
            "by_kind": {k: sum(1 for v in out if v["kind"] == k) for k in sorted({v["kind"] for v in out})},
            "notes": out}


def reopen_reasons(name, t, runs, rules):
    if name not in t["raw"]:
        return ["%s is not a folded finding as of the notes" % name]
    f = t["raw"][name]
    s = t["signatures"][f["sig"]]
    key = FF.row_key(s["mod"], s["chain"], s["row"], s["text"], rules, None if f["resolved"] else name)
    tl = runs.get((s["mod"], s["chain"], s["row"]), [])
    earlier = [t["raw"][x]["at"] for x in s["findings"] if t["raw"][x]["at"] < f["at"]] + \
        [at for at, j, v, d, _ in tl if v == "FAIL" and at < f["at"] and
         FF.row_key(s["mod"], s["chain"], s["row"], d, rules) == key]
    if not earlier:
        return ["%s is a NEW failure (its exact signature %s was never seen before it), not a retired one back"
                % (name, f["sig"][:13])]
    last = max(earlier)
    passes = len({j for at, j, v, _, _ in tl if v == "PASS" and last < at < f["at"]})
    if passes < RETIRE_AFTER:
        return ["%s's exact failure was last seen %s with only %d distinct passing run(s) before it came back: "
                "never retired" % (name, last, passes)]
    return []


def ledger_corrections(events):
    have = set()
    for e in events:
        t = e.get("text") or ""
        if e.get("event") == "note" and t.startswith(NOTE_PREFIX + " "):
            parts = t[len(NOTE_PREFIX) + 1:].split(" ", 2)
            if len(parts) >= 2:
                have.add((e.get("id"), parts[0], parts[1].rstrip(":")))
    return have


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--done", default=DONE, help="testq done records (default %(default)s)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    try:
        d = derive(a.done)
    except (FF.Unmeasured, OSError, ValueError) as e:
        print("UNMEASURED: %s" % e)
        return 2
    print("vet: %d notes (%s) as of %s over %d done records: %s" % (
        len(d["notes"]), d["by_kind"], d["cutoff"], d["records"], d["counts"]))
    for v in d["notes"]:
        if v["verdict"] != "HOLDS":
            print("  %s %s %s on %s: %s" % (v["verdict"], v["tag"], v["kind"], v["item"],
                                            " | ".join(v["reasons"] + v["inexact"])))
    if a.write:
        with open(VERDICTS, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1, sort_keys=True)
            f.write("\n")
        print("wrote %s" % VERDICTS)
        return 0
    if a.check:
        bad = []
        try:
            with open(VERDICTS, encoding="utf-8") as f:
                if json.load(f) != d:
                    bad.append("%s differs from the re-derivation" % VERDICTS)
        except (OSError, ValueError) as e:
            bad.append("%s unreadable: %s" % (VERDICTS, e))
        have = ledger_corrections(ledger_events())
        for v in d["notes"]:
            if v["verdict"] != "HOLDS" and (v["item"], v["tag"], v["kind"]) not in have:
                bad.append("no correction note on %s for %s %s" % (v["item"], v["tag"], v["kind"]))
        for b in bad:
            print("FAIL: " + b)
        print("CHECK %s" % ("FAIL" if bad else "PASS: every CORRECTION and INEXACT has its note"))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
