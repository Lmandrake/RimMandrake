#!/usr/bin/env python3
"""evidence_gate.py - the one evidence-record close predicate, run in SHADOW beside today's close gate
(RIMFLOW_BUILD_ONE_EVIDENCE_RECORD step 09b; redesign_final.md WP-09 / section 3.4, redesign.md section 2).

The question redesign.md section 2.2 says a Relentless close should ask: is there a green evidence record for this exact
sha whose exam is the frozen exam? `green()` answers it from one record (evidence.py, 09a). Green, as far as today's
record can carry it (section 2.1; breaks, hunks and holdouts have no entry kind yet, so they are not judged here):
    - the record verifies (an edited, cut or forged record is no evidence)
    - its newest box run (kind `run`) is green, exit 0, against the frozen exam (exam_hash = the contract's hash)
    - its newest Marker verdict is PASS: WEAK, FAIL and UNMEASURED do not close ("a WEAK verdict cannot close"), and
      a WEAK the live narrow rule reads as PASS (relentless_wall.acted_weak) is still WEAK here
    - an empty-diff close (--no-code) closes only on a `no_code` exam (G15: empty-diff Judge closes are false closes)
    - an exam that declares a live clause closes done only with a live attestation (today: the close's `--live` line,
      which cli._live_gate checks right after); without one the item is `built`, not done

SHADOW ONLY: cli.py `_close_gate` calls `shadow()` for every close of an item the Relentless store holds, before it
refuses or passes. It never refuses, never raises and never waits long (git calls time out at GIT_TIMEOUT_S); it
appends one row per close to <store>/evidence_shadow.jsonl - the gate's word, the predicate's word, `disagree`.
09c deletes the replaced guards one at a time once the corpus and SAMPLE closes of this log agree; until then nothing
here decides anything.

    python3 src/RimMandrake/rimflow/evidence_gate.py report [--json]      the disagreement count toward the sample
    python3 src/RimMandrake/rimflow/evidence_gate.py corpus check          the false/valid close corpus, exit 1 on a miss
    python3 src/RimMandrake/rimflow/evidence_gate.py corpus build          rebuild it from the ledger + store (writes)

The corpus (evidence_gate_corpus.json) is built from REAL past Relentless closes. No evidence record existed before
09a, so each close's record is reconstructed from what the store kept for it: the Marker's verdict (check.verdict, or
the close audit's), the contract (exam hash, live clause), the close event (--no-code, --live). The box run is taken
as green because finish accepted it. False closes: every close whose deciding Marker word was WEAK (the store's done
WEAK items and close_audits.jsonl's narrow_weak draws) and every empty-diff `--no-code` Relentless close. Valid
closes: every code close whose Marker said PASS.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import evidence                                                 # noqa: E402

DEFAULT_ROOT = "/home/mandrake/rm/relentless"       # relentless.DEFAULT_ROOT, not imported: cli.py must stay light
SHADOW = "evidence_shadow.jsonl"
SAMPLE = 30                 # redesign_final.md: the shadow ends on a sample count, not on days
GIT_TIMEOUT_S = 5
CORPUS = os.path.join(HERE, "evidence_gate_corpus.json")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
AUDITS = os.path.join(REPO, "infrastructure", "state", "close_audits.jsonl")
RELENTLESS_WHY = "relentless"       # relentless.py closes with --why "relentless: blind check passed"


def store_dir():
    return os.path.join(os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT, "store")


def exam_of(contract):
    """-> the exam as the predicate reads it: {hash, live, no_code}. hash is relentless_boxrun.contract_hash."""
    c = contract or {}
    return {"hash": hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest(),
            "live": bool(c.get("live")), "no_code": bool(c.get("no_code"))}


def green(entries, exam, no_code=False, live=None, tampered=()):
    """Pure. entries: one record's entries in order (evidence.read). exam: exam_of(...) or None (not known: hash and
    clauses unchecked). no_code: the close names no work commit. live: the live attestation the close carries (a checked
    line) or None. tampered: evidence.verify's problems. -> (accepted, [reason]); every failing rule gives a reason."""
    why = []
    if tampered:
        why.append("tampered: the record does not verify (%s)" % "; ".join(tampered)[:200])
    runs = [e for e in entries if e.get("kind") == "run"]
    marks = [e for e in entries if e.get("kind") == "marker"]
    if not entries:
        why.append("no record: no evidence record at this sha")
    if not runs:
        why.append("no run: no box run on record")
    else:
        r = runs[-1]
        if r.get("verdict") != "green" or r.get("exit") != 0:
            why.append("run not green: newest box run is %s, exit %s" % (r.get("verdict"), r.get("exit")))
        if exam and r.get("exam_hash") != exam.get("hash"):
            why.append("exam drift: the run's exam %s is not the frozen exam %s"
                       % (str(r.get("exam_hash"))[:12], str(exam.get("hash"))[:12]))
    if not marks:
        why.append("no marker: no Marker verdict on record")
    elif marks[-1].get("verdict") != "PASS":
        why.append("marker %s: a %s verdict cannot close" % (marks[-1].get("verdict"), marks[-1].get("verdict")))
    if no_code and not (exam or {}).get("no_code"):
        why.append("empty diff: a --no-code close, and the exam is not a no_code exam")
    if (exam or {}).get("live") and not live:
        why.append("live owed: the exam declares a live clause and no attestation holds: built, not done")
    return (not why), why


def reason_class(reason):
    """'marker WEAK: ...' -> 'marker WEAK'; the label before the colon is the class a report counts by."""
    return str(reason).split(":", 1)[0]


# ---------------------------------------------------------------- the shadow call

def _git(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, timeout=GIT_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout.strip()


def _record_for(sd, item, sha, cand, no_code, cwd):
    """-> the sha whose record speaks for this close, or None. The close's own sha; else the store's candidate (where
    the Marker ran) when the close is --no-code, is that sha, or is under it (relentless closes at the work commit)."""
    full = sha
    if sha and not evidence._SHA.match(sha):
        rc, out = _git(cwd, "rev-parse", "--verify", "-q", sha + "^{commit}")
        full = out if rc == 0 and out else sha
    if full and evidence._SHA.match(full) and os.path.exists(evidence.record_path(sd, item, full)):
        return full
    if cand and evidence._SHA.match(cand) and os.path.exists(evidence.record_path(sd, item, cand)):
        if no_code or full == cand or _git(cwd, "merge-base", "--is-ancestor", full, cand)[0] == 0:
            return cand
    return None


def judge(sd, item, sha, no_code, live=None, cwd=None):
    """-> {record, accepted, reasons} for `item` closing at `sha`, or None when the store does not hold the item (not a
    Relentless close: the predicate does not speak for it)."""
    try:
        with open(os.path.join(sd, "items", item, "state.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError):
        return None
    cand = str((st.get("candidate") or {}).get("sha") or "")
    rec = _record_for(sd, item, sha, cand, no_code, cwd or HERE)
    entries, bad = [], []
    if rec:
        bad = evidence.verify(sd, item, rec)
        entries = evidence.read(sd, item, rec, strict=False)
    ok, why = green(entries, exam_of(st.get("contract")), bool(no_code), live, bad)
    return {"record": rec, "accepted": ok, "reasons": why}


def shadow(item, sha, no_code, gate_found, live=None, cwd=None, sd=None, out=None):
    """cli._close_gate's call. Logs the predicate beside the gate's own refusals (`gate_found`, [(kind, why)]) and
    returns the row, or None. NEVER raises and never refuses: any failure is one stderr line and the close goes on."""
    t0 = time.time()
    out = out or sys.stderr      # resolved per call, so a redirected stderr is honoured
    try:
        sd = sd or store_dir()
        j = judge(sd, item, sha, no_code, live, cwd)
        if j is None:
            return None
        gate_ok = not gate_found
        row = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "item": item, "sha": sha,
               "no_code": bool(no_code), "record": j["record"], "gate": "accept" if gate_ok else "refuse",
               "gate_reasons": sorted({str(k) for k, _ in gate_found}), "predicate": "accept" if j["accepted"] else "reject",
               "reasons": j["reasons"], "disagree": gate_ok != j["accepted"], "ms": int((time.time() - t0) * 1000)}
        with open(os.path.join(sd, SHADOW), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        if row["disagree"]:
            print("close: %s: evidence shadow DISAGREES (gate %s, record %s: %s). Shadow only: this changes nothing."
                  % (item, row["gate"], row["predicate"], "; ".join(reason_class(r) for r in j["reasons"]) or "green"),
                  file=out)
        return row
    except Exception as ex:      # noqa: BLE001 - a shadow must never refuse or break a close
        try:
            print("close: %s: evidence shadow failed (%s: %s); the close is unaffected" % (item, type(ex).__name__, ex),
                  file=out)
        except Exception:        # noqa: BLE001
            pass
        return None


# ---------------------------------------------------------------- the report

def rows(sd=None):
    out = []
    try:
        with open(os.path.join(sd or store_dir(), SHADOW), encoding="utf-8") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        pass
    return out


def summary(rs):
    """Pure. -> the shadow's count, one close per (item, sha) - the last attempt stands (a refused close retried)."""
    last = {}
    for r in rs:
        last[(r.get("item"), r.get("sha"))] = r
    closes = list(last.values())
    dis = [r for r in closes if r.get("disagree")]
    by = {}
    for r in dis:
        for c in sorted({reason_class(x) for x in r.get("reasons") or []}) or ["green"]:
            k = "gate %s / record %s: %s" % (r.get("gate"), r.get("predicate"), c)
            by[k] = by.get(k, 0) + 1
    return {"closes": len(closes), "attempts": len(rs), "agree": len(closes) - len(dis), "disagree": len(dis),
            "gate_accept_record_reject": sum(r.get("gate") == "accept" and r.get("predicate") == "reject" for r in dis),
            "gate_refuse_record_accept": sum(r.get("gate") == "refuse" and r.get("predicate") == "accept" for r in dis),
            "by_class": dict(sorted(by.items(), key=lambda kv: -kv[1])), "sample": SAMPLE,
            "sample_met": len(closes) >= SAMPLE, "items": sorted({r.get("item") for r in dis})[:20]}


def report_lines(s):
    out = ["evidence shadow: %d closes (%d attempts), %d agree, %d DISAGREE - %s"
           % (s["closes"], s["attempts"], s["agree"], s["disagree"],
              "sample met (%d >= %d)" % (s["closes"], s["sample"]) if s["sample_met"]
              else "UNDER SAMPLE: %d of %d closes" % (s["closes"], s["sample"]))]
    out += ["  %4d  %s" % (n, k) for k, n in s["by_class"].items()]
    return out


# ---------------------------------------------------------------- the corpus

def corpus_entries(row):
    """A corpus row -> the record entries it stands for (see the module doc: reconstructed from the store)."""
    return [{"kind": "run", "n": 0, "verdict": "green", "exit": 0, "exam_hash": row["exam_hash"]},
            {"kind": "marker", "n": 1, "verdict": row["marker"]}]


def corpus_judge(row):
    exam = {"hash": row["exam_hash"], "live": row["live_declared"], "no_code": False}
    return green(corpus_entries(row), exam, row["no_code"], row["live"] or None)


def check_corpus(corpus):
    """-> (problems, counts). A false close the predicate accepts, or a valid close it rejects, is a problem."""
    bad, n = [], {"false": 0, "valid": 0, "false_rejected": 0, "valid_accepted": 0}
    for r in corpus["closes"]:
        ok, why = corpus_judge(r)
        n[r["class"]] += 1
        if r["class"] == "false" and not ok:
            n["false_rejected"] += 1
        elif r["class"] == "valid" and ok:
            n["valid_accepted"] += 1
        else:
            bad.append("%s close %s@%s (%s): predicate %s %s" % (r["class"], r["item"], r["sha"][:10], r["kind"],
                                                                "accepts" if ok else "rejects", "; ".join(why)))
    return bad, n


def build_corpus(events, sd, audits):
    """events: model.read(). -> the corpus dict. One row per item: its last Relentless close."""
    last = {}
    for e in events:
        if e.get("event") == "close" and RELENTLESS_WHY in str(e.get("why", "")):
            if e["id"] not in last or str(e.get("ts")) >= str(last[e["id"]].get("ts")):
                last[e["id"]] = e
    out, seen = [], set()
    for iid, e in sorted(last.items()):
        try:
            with open(os.path.join(sd, "items", iid, "state.json"), encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            continue
        cand = str((st.get("candidate") or {}).get("sha") or "")
        work = "(work at" in str(e.get("reason", ""))
        if st.get("status") != "done" or not cand or not (cand.startswith(e["sha"]) or work or e.get("noCode")):
            continue            # the store's state is no longer the one this close was decided on
        word = (st.get("check") or {}).get("verdict")
        if word not in ("PASS", "WEAK"):
            continue
        ex = exam_of(st.get("contract"))
        row = {"item": iid, "sha": e["sha"], "ts": e.get("ts"), "marker": word, "no_code": bool(e.get("noCode")),
               "live_declared": ex["live"], "live": bool(e.get("live")), "exam_hash": ex["hash"][:16]}
        if e.get("noCode"):
            row.update(cls="false", kind="empty-diff --no-code close")
        elif word == "WEAK":
            row.update(cls="false", kind="WEAK close (store)")
        else:
            row.update(cls="valid", kind="PASS code close")
        row["class"] = row.pop("cls")
        out.append(row)
        seen.add(iid)
    for a in audits:
        if a.get("kind") == "draw" and a.get("stratum") == "narrow_weak" and a.get("verdict") == "WEAK" \
                and a["item"] not in seen:
            st = {}
            try:
                with open(os.path.join(sd, "items", a["item"], "state.json"), encoding="utf-8") as f:
                    st = json.load(f)
            except (OSError, ValueError):
                pass
            ex = exam_of(st.get("contract"))
            out.append({"item": a["item"], "sha": a["sha"], "ts": a.get("closed_at"), "marker": "WEAK", "no_code": False,
                        "live_declared": ex["live"], "live": ex["live"], "exam_hash": ex["hash"][:16],
                        "class": "false", "kind": "WEAK close (close_audits narrow_weak)"})
            seen.add(a["item"])
    return {"built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "closes": out,
            "how": "evidence_gate.py corpus build: real Relentless closes, records reconstructed from the store (module doc)"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--store-dir", help="the Relentless store dir (default: $RELENTLESS_ROOT/store)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="the shadow's disagreement count toward the sample")
    r.add_argument("--json", action="store_true")
    c = sub.add_parser("corpus", help="check (default) or rebuild the false/valid close corpus")
    c.add_argument("what", nargs="?", choices=("check", "build"), default="check")
    c.add_argument("--path", default=CORPUS)
    a = ap.parse_args(argv)
    sd = a.store_dir or store_dir()
    if a.cmd == "report":
        s = summary(rows(sd))
        print(json.dumps(s, indent=1, sort_keys=True) if a.json else "\n".join(report_lines(s)))
        return 0
    if a.what == "build":
        sys.path.insert(0, os.path.dirname(HERE))
        from rimflow import model
        audits = []
        if os.path.exists(AUDITS):
            with open(AUDITS, encoding="utf-8") as f:
                audits = [json.loads(x) for x in f if x.strip()]
        corpus = build_corpus(model.read(), sd, audits)
        with open(a.path, "w", encoding="utf-8") as f:       # one close per line: a diff of a rebuild reads per close
            f.write('{"built": %s, "how": %s, "closes": [\n' % (json.dumps(corpus["built"]), json.dumps(corpus["how"])))
            f.write(",\n".join(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in corpus["closes"]))
            f.write("\n]}\n")
    with open(a.path, encoding="utf-8") as f:
        corpus = json.load(f)
    bad, n = check_corpus(corpus)
    for b in bad[:20]:
        print("MISS " + b)
    print("evidence corpus: %d false closes, %d rejected; %d valid closes, %d accepted - %s"
          % (n["false"], n["false_rejected"], n["valid"], n["valid_accepted"], "MISSES %d" % len(bad) if bad else "OK"))
    return 1 if bad or not n["false"] or not n["valid"] else 0


if __name__ == "__main__":
    sys.exit(main())
