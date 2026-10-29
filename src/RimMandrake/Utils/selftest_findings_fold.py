#!/usr/bin/env python3
"""selftest_findings_fold.py - the no-AI findings sorter (findings_fold.py, FINDINGS_FOLD_BUILD_QUARRY_SAID_IT_23X).

One group per guarantee of the simplified design (coordinator ruling after blind review 2,
v3_review/blind/findings/review2.md). Every group fails against the pre-simplification module (5ee3ccc7d8):
  G1 exact merge: failures differing only in job ids, timestamps and durations share a signature; count, first/last
     seen and every raw text are kept;
  G2 no over-merge: error codes, numbered file names, hex values, rows, chains and mods keep failures apart (F1);
  G3 evidence, never judgment: passes after the last failure are counted per distinct job and reported, nothing is
     retired or reopened, a decision shows the failures since it, an empty-detail FAIL is pinned on no bug (F4-F8);
  G4 contradictions: an item's own latest verdict of a row, a pass under another item's build clears nothing (F9);
  G5 health routing is case-insensitive (F13);
  G6 fails closed: structurally wrong records, findings, decisions, a reused finding name or a job in two done files
     exit 2 and change no output (F3, F5, F10);
  G7 one writer: a held queue lock or clone lock exits 2 and writes nothing (F11, F14);
  G8 publication: an interruption between the two renames is repaired by the next run; an unchanged rerun rewrites
     neither file (F12, F14); the run writes no ledger line.
"""
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "testq"))
import findings_fold as FF  # noqa: E402

FAILS = []
RULES = FF.load_rules()


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def ts(day, hh, mm=0):
    return "2026-10-%02dT%02d:%02d:00Z" % (day, hh, mm)


def fev(name, item, row, text, at, chain="c1"):
    """A ledger finding line, as ingest.py files it."""
    return {"seat": "RUNNER", "event": "finding", "id": item, "type": "UNTRIAGED", "severity": "medium",
            "name": name, "from": "%s/run-1@steve-targeted" % item,
            "why": "%s/%s FAIL on SteveDesktop: %s" % (chain, row, text[:160]), "ts": at}


def rec(job, mod, at, rows, findings=(), item="X"):
    """rows: (chain, row, verdict, detail)."""
    return {"job": {"id": job, "mod": mod, "item": item},
            "result": {"outcome": "DONE", "finished": at, "attempt": job + ".a1",
                       "rows": [{"chain": c, "row": r, "verdict": v, "detail": d} for c, r, v, d in rows]},
            "ingested": {"run": "%s/run-1@steve-targeted" % item, "findings": list(findings), "at": at}}


def fold(evs, states, recs, decisions=()):
    finds = {e["name"]: {k: e.get(k) for k in ("id", "why", "ts", "from")} for e in evs}
    return FF.fold(finds, [], states, recs, list(decisions), RULES, ts(29, 20))


def one(evs, recs, states=None, decisions=()):
    """-> (table, {finding: sig})."""
    t = fold(evs, states or {}, recs, decisions)
    return t, {n: f["sig"] for n, f in t["raw"].items()}


def pair(text_a, text_b, row_b="r1", chain_b="c1", mod_b="FlowWorks"):
    evs = [fev("A_1", "IT_A", "r1", text_a, ts(27, 1)), fev("B_1", "IT_A", row_b, text_b, ts(27, 2), chain_b)]
    recs = [rec("JA", "FlowWorks", ts(27, 1), [("c1", "r1", "FAIL", text_a)], ["A_1"], "IT_A"),
            rec("JB", mod_b, ts(27, 2), [(chain_b, row_b, "FAIL", text_b)], ["B_1"], "IT_A")]
    _, s = one(evs, recs)
    return s["A_1"] == s["B_1"]


# ------------------------------------------------------------------ G1 exact merge on volatile fields only
T1 = ("ExpectationFailed: dig never finished (dig_result_2026102%dT1%d0000.json, job J2026102%dT101010Z-a1b2c%d.a2, "
      "at 2026-10-2%dT0%d:11:12Z, took %d s, pawn Human476708)")
V1 = {"Q_A": (7, 1, 7, 1, 7, 1, 12), "Q_B": (8, 2, 8, 2, 8, 2, 340), "Q_C": (9, 3, 9, 3, 9, 3, 7)}
evs1 = [fev(n, "IT_Q", "cut", T1 % V1[n], ts(27 + k, k + 1)) for k, n in enumerate(sorted(V1))]
recs1 = [rec("JQ%d" % k, "FlowWorks", ts(27 + k, k + 1), [("c1", "cut", "FAIL", T1 % V1[n])], [n], "IT_Q")
         for k, n in enumerate(sorted(V1))]
t, s = one(evs1, recs1)
check(len(set(s.values())) == 1, "G1 three runs apart only in timestamps, job ids and a duration share one signature")
row = t["signatures"].get(s["Q_A"], {})
check(row.get("count") == 3 and row.get("first_seen") == ts(27, 1) and row.get("last_seen") == ts(29, 3),
      "G1 the merged row counts 3 with first and last seen")
check(sorted(row.get("findings") or []) == ["Q_A", "Q_B", "Q_C"] and t["raw"]["Q_B"]["text"] == T1 % V1["Q_B"],
      "G1 every finding name is listed and every raw text kept verbatim")
check(t["counts"]["findings"] == 3 and t["counts"]["distinct"] == 1, "G1 counts: 3 findings, 1 distinct")

# ------------------------------------------------------------------ G2 nothing else merges
check(not pair("assert failed: CODE1234", "assert failed: CODE5678"), "G2 error codes CODE1234/CODE5678 stay apart")
check(not pair("missing result1234.json", "missing result5678.json"), "G2 numbered file names stay apart")
check(not pair("expected flags 0xdeadbeef1 got 0xdeadbeef2", "expected flags 0xdeadbeef1 got 0xcafebabe2"),
      "G2 hex values stay apart")
check(not pair("Human476708 never drank", "Human118501 never drank"), "G2 a pawn id is not stripped")
check(not pair("got 0.117750995", "got 0.117750996"), "G2 measured values stay apart")
check(not pair("x", "x", row_b="r2") and not pair("x", "x", chain_b="c2") and not pair("x", "x", mod_b="Thirst"),
      "G2 same text on another row, chain or mod stays apart")
check(pair("took 12 s at 2026-10-27T01:02:03Z", "took 340 s at 2026-10-28T09:08:07Z"),
      "G2 sanity: the same pair with only volatile fields apart DOES merge")
# a finding no done record explains merges with nothing, not even its own twin text
evs = [fev("U_1", "IT_A", "r1", "boom", ts(27, 1)), fev("U_2", "IT_A", "r1", "boom", ts(27, 2))]
_, s = one(evs, [])
check(s["U_1"] != s["U_2"], "G2 two record-less findings with one text stay two rows")

# ------------------------------------------------------------------ G3 evidence only
TA = "thirst never rose"
evs3 = [fev("A_1", "IT_T", "r1", TA, ts(27, 1))]
recs3 = [rec("J0", "FlowWorks", ts(27, 1), [("c1", "r1", "FAIL", TA)], ["A_1"], "IT_T")] + \
    [rec("J%d" % k, "FlowWorks", ts(27, 2 + k), [("c1", "r1", "PASS", "")], [], "IT_T") for k in (1, 2, 3)]
t, s = one(evs3, recs3, {"IT_T": "doing"})
row = t["signatures"][s["A_1"]]
check(row.get("passes_since") == 3, "G3 three later passes are counted (got %s)" % row.get("passes_since"))
check(row.get("status") == "NEW", "G3 and nothing is retired: the row stays NEW (got %s)" % row.get("status"))
check((row.get("row_latest") or {}).get("verdict") == "PASS", "G3 the row's latest verdict is reported")
md = FF.render_md(t, "x")
check("passed 3 later run(s)" in md, "G3 curation says 'passed 3 later run(s)'")
# an empty-detail FAIL after the passes is the row's latest verdict but is pinned on no signature
recs3b = recs3 + [rec("J9", "FlowWorks", ts(28, 1), [("c1", "r1", "FAIL", "")], [], "IT_T")]
t, s = one(evs3, recs3b, {"IT_T": "doing"})
row = t["signatures"][s["A_1"]]
check(row.get("last_fail") == ts(27, 1) and row.get("passes_since") == 3 and row.get("status") == "NEW",
      "G3 an empty-detail FAIL changes no signature's last failure (F7)")
check((row.get("row_latest") or {}).get("verdict") == "FAIL", "G3 but the row's latest verdict shows it")
# a later FAIL of the same exact text, with no new finding (ingest deduped it), moves last_fail
recs3c = recs3 + [rec("J8", "FlowWorks", ts(28, 2), [("c1", "r1", "FAIL", TA)], [], "IT_T")]
t, s = one(evs3, recs3c, {"IT_T": "doing"})
row = t["signatures"][s["A_1"]]
check(row.get("last_fail") == ts(28, 2) and row.get("passes_since") == 0 and row.get("status") == "NEW",
      "G3 a recurrence of the exact text resets the passes, and nothing is 'reopened' (F4, F8)")
# decisions: a retire decision retires nothing; failures since a decision are reported, a newer decision resets
sig = s["A_1"]
dec = [{"sig": sig, "as": "retire", "by": "FOUNDRY", "ts": ts(27, 10), "why": "fixed in abc"}]
t, s = one(evs3, recs3c, {"IT_T": "doing"}, dec)
row = t["signatures"][sig]
check(row.get("status") == "DECIDED" and row.get("failed_since_decision") == 1,
      "G3 a FAIL after a retire decision is reported as 1 failure since it (got %s, %s)"
      % (row.get("status"), row.get("failed_since_decision")))
dec2 = dec + [{"sig": sig, "as": "work", "into": "IT_T", "by": "FOUNDRY", "ts": ts(28, 5), "why": "back to it"}]
t, s = one(evs3, recs3c, {"IT_T": "doing"}, dec2)
row = t["signatures"][sig]
check(row.get("status") == "DECIDED" and row.get("failed_since_decision") == 0 and (row.get("decision") or {}).get("as") == "work",
      "G3 a newer decision acknowledges it (F8)")

# ------------------------------------------------------------------ G4 contradictions per item, row's own verdict
evs4 = [fev("C_1", "IT_DONE", "r1", "well dry", ts(27, 1))]
recs4 = [rec("JC1", "FlowWorks", ts(27, 1), [("c1", "r1", "FAIL", "well dry")], ["C_1"], "IT_DONE"),
         rec("JC2", "FlowWorks", ts(27, 2), [("c1", "r1", "PASS", "")], [], "IT_SWEEP")]
t, _ = one(evs4, recs4, {"IT_DONE": "done", "IT_SWEEP": "doing"})
check([c["item"] for c in t.get("contradictions") or []] == ["IT_DONE"],
      "G4 a pass under another item's build does not clear a done item's own FAIL (got %s)"
      % [c["item"] for c in t.get("contradictions") or []])
recs4b = recs4 + [rec("JC3", "FlowWorks", ts(27, 3), [("c1", "r1", "PASS", "")], [], "IT_DONE"),
                  rec("JC4", "FlowWorks", ts(27, 4), [("c1", "r1", "FAIL", "other bug")], [], "IT_SWEEP")]
t, _ = one(evs4, recs4b, {"IT_DONE": "done", "IT_SWEEP": "doing"})
check(t.get("contradictions") == [], "G4 a done item whose own latest run passed is not contradicted")
t, _ = one(evs4, recs4b, {"IT_DONE": "done", "IT_SWEEP": "validated"})
check([(c.get("item"), c.get("job")) for c in t.get("contradictions") or []] == [("IT_SWEEP", "JC4")],
      "G4 the validated item whose own latest run failed is (F9)")
evs4c = [fev("H_1", "IT_DONE", "r1", "Canary was red: no module", ts(27, 1))]
recs4c = [rec("JH1", "FlowWorks", ts(27, 1), [("c1", "r1", "FAIL", "Canary was red: no module")], ["H_1"],
              "IT_DONE")]
t, _ = one(evs4c, recs4c, {"IT_DONE": "done"})
check(len(t.get("contradictions") or []) == 1, "G4 a health-routed failure on a done item is still a contradiction")

# ------------------------------------------------------------------ G5 health, any case
for txt in ("Runner pull refused: dirty tree", "Canary was red", "NO SPACE LEFT ON DEVICE", "no module named 'PIL'"):
    evs = [fev("M_1", "IT_A", "r1", txt, ts(27, 1))]
    t, s = one(evs, [rec("JM", "FlowWorks", ts(27, 1), [("c1", "r1", "FAIL", txt)], ["M_1"], "IT_A")])
    check(t["signatures"][s["M_1"]].get("status") == "HEALTH", "G5 %r is HEALTH" % txt)

# ------------------------------------------------------------------ G6-G8 run() on temp inputs
tmp = tempfile.mkdtemp(prefix="ffold_")
try:
    qd, out, led = (os.path.join(tmp, n) for n in ("q", "out", "ledger"))
    os.makedirs(os.path.join(qd, "done"))
    os.makedirs(os.path.join(led, "events"))
    events_file = os.path.join(led, "events.jsonl")
    open(events_file, "w").close()
    shard = os.path.join(led, "events", "RUNNER.jsonl")

    def write_shard(evs):
        with open(shard, "w") as f:
            for e in evs:
                f.write(json.dumps(e) + "\n")

    def write_recs(recs):
        for n in os.listdir(os.path.join(qd, "done")):
            os.remove(os.path.join(qd, "done", n))
        for r_ in recs:
            with open(os.path.join(qd, "done", r_["job"]["id"] + ".json"), "w") as f:
                json.dump(r_, f)
    write_shard(evs1)
    write_recs(recs1)
    decf = os.path.join(tmp, "decisions.jsonl")
    lockdir = os.path.join(tmp, "locks")         # ingest.repo_lock lives in the temp dir: a private one, so this
    os.makedirs(lockdir)                         # test never holds the real clone lock against ingest's selftest
    tempfile.tempdir = lockdir
    env = dict(os.environ, TESTQ_QUEUE=qd, FINDINGS_FOLD_OUT=out, RIMFLOW_LEDGER=events_file,
               FINDINGS_FOLD_DECISIONS=decf, FINDINGS_FOLD_LOCK_WAIT_S="1", TMPDIR=lockdir)
    env.pop("FINDINGS_FOLD_RULES", None)
    std, cur = os.path.join(out, "standing.json"), os.path.join(out, "curation.md")

    def run():
        return subprocess.run([sys.executable, os.path.join(HERE, "findings_fold.py"), "run"], env=env,
                              capture_output=True, text=True, timeout=120)

    def same_table(s_):
        return FF.semantic(json.loads(snap()[0])) == FF.semantic(json.loads(s_[0]))

    def snap():
        return tuple(open(p, "rb").read() if os.path.exists(p) else None for p in (std, cur))
    r = run()
    check(r.returncode == 0 and os.path.isfile(std) and os.path.isfile(cur),
          "G6 a clean run exits 0 and writes both files (%d: %s)" % (r.returncode, (r.stderr or r.stdout)[-300:]))
    good = snap()
    ledger_bytes = open(shard, "rb").read()

    def closed(label, setup, undo):
        setup()
        try:
            r_ = run()
            check(r_.returncode == 2 and "UNMEASURED" in r_.stdout and snap() == good,
                  "%s: exit 2, UNMEASURED, no output change (got %d: %s)" % (label, r_.returncode, r_.stdout[-160:]))
        finally:
            undo()

    def bad_rec(mut):
        def setup():
            r_ = json.loads(json.dumps(recs1[0]))
            mut(r_)
            write_recs([r_] + recs1[1:])
        return setup

    restore = (lambda: write_recs(recs1))
    closed("G6 ingested.findings is a string (F10)", bad_rec(lambda r_: r_["ingested"].update(findings="Q_A")), restore)
    closed("G6 a row verdict that is no verdict", bad_rec(lambda r_: r_["result"]["rows"][0].update(verdict="MEH")),
           restore)
    closed("G6 one row twice in a record (F5)",
           bad_rec(lambda r_: r_["result"]["rows"].append(dict(r_["result"]["rows"][0], verdict="PASS"))), restore)
    closed("G6 a DONE result with rows null (F6)", bad_rec(lambda r_: r_["result"].update(rows=None)), restore)
    closed("G6 job.row_items not a mapping", bad_rec(lambda r_: r_["job"].update(row_items=["c1"])), restore)
    closed("G6 no finish time", bad_rec(lambda r_: r_["result"].pop("finished")), restore)

    def dup_job():
        write_recs(recs1)
        with open(os.path.join(qd, "done", "copy.json"), "w") as f:
            json.dump(recs1[0], f)
    closed("G6 one job in two done files (F5)", dup_job, restore)
    closed("G6 a finding name reused with another text (F3)",
           lambda: write_shard(evs1 + [dict(evs1[0], why="c1/cut FAIL on SteveDesktop: a different bug")]),
           lambda: write_shard(evs1))
    closed("G6 a finding with no time", lambda: write_shard(evs1 + [dict(fev("Z_1", "IT_Q", "cut", "z", ""))]),
           lambda: write_shard(evs1))
    write_shard(evs1 + [evs1[0]])
    r = run()
    check(r.returncode == 0 and snap() == good, "G6 an exact duplicate finding line is one finding")
    write_shard(evs1)
    sig = json.loads(good[0])["raw"]["Q_A"]["sig"]
    for label, line in (("no ts or into (F10)", {"sig": sig, "as": "work", "by": "F", "why": "w"}),
                        ("work with no into", {"sig": sig, "as": "work", "by": "F", "ts": ts(28, 1), "why": "w"}),
                        ("no why", {"sig": sig, "as": "retire", "by": "F", "ts": ts(28, 1), "why": " "}),
                        ("a malformed sig", {"sig": "nope", "as": "retire", "by": "F", "ts": ts(28, 1), "why": "w"})):
        closed("G6 a decision with %s" % label, lambda line=line: open(decf, "w").write(json.dumps(line) + "\n"),
               lambda: os.remove(decf))

    # G7 one writer
    sys.path.insert(0, os.path.join(HERE, "testq"))
    import ingest as I

    def hold_queue_lock():
        fh = open(os.path.join(qd, "ingest.lock"), "a")
        fcntl.flock(fh, fcntl.LOCK_EX)
        return fh
    write_shard(evs1 + [fev("NEW_1", "IT_Q", "other", "new bug", ts(29, 5))])   # a run would change the output
    fh = hold_queue_lock()
    try:
        r = run()
        check(r.returncode == 2 and snap() == good, "G7 while ingest holds the queue lock: exit 2, nothing written "
                                                     "(got %d)" % r.returncode)
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()
    with I.repo_lock(0) as got:
        check(got and I.repo_lock_path().startswith(lockdir), "G7 sanity: the test holds the (private) repo lock")
        r = run()
        check(r.returncode == 2 and snap() == good, "G7 while the clone lock is held: exit 2, nothing written "
                                                     "(got %d)" % r.returncode)
    r = run()
    check(r.returncode == 0 and snap() != good, "G7 sanity: with both locks free the same input does change it")
    write_shard(evs1)
    r = run()
    check(r.returncode == 0 and same_table(good), "G7 and back")

    # G8 publication
    os.utime(std, (1, 1))
    os.utime(cur, (1, 1))
    r = run()
    check(r.returncode == 0 and os.stat(std).st_mtime == 1 and os.stat(cur).st_mtime == 1,
          "G8 an unchanged rerun rewrites neither file (F14)")
    stale = good[1].decode().replace("# Findings fold", "# Findings fold STALE", 1)
    with open(cur, "w") as f:
        f.write(stale)                           # as a crash between the two renames leaves it
    r = run()
    check(r.returncode == 0 and snap()[1] != stale.encode() and b"STALE" not in snap()[1],
          "G8 a curation.md that disagrees with standing.json is rewritten (F12)")
    newer = snap()
    write_shard(evs1 + [fev("NEW_2", "IT_Q", "other", "new bug", ts(29, 6))])
    r = run()
    check(r.returncode == 0 and not same_table(newer), "G8 sanity: a new finding changes the table")
    with open(std, "wb") as f:
        f.write(newer[0])                        # a crash after curation.md, before standing.json
    r = run()
    check(r.returncode == 0 and b"NEW_2" in snap()[0], "G8 a standing.json older than curation.md is rewritten")
    write_shard(evs1)
    os.remove(cur)
    r = run()
    check(r.returncode == 0 and os.path.isfile(cur), "G8 a missing curation.md is rewritten")
    check(open(shard, "rb").read() == ledger_bytes and os.path.getsize(events_file) == 0,
          "G8 the run wrote no ledger line")
    check(not [n for n in os.listdir(out) if n.endswith(".tmp")], "G8 no temp file left behind")
finally:
    tempfile.tempdir = None
    shutil.rmtree(tmp, ignore_errors=True)

print("\n%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
