#!/usr/bin/env python3
"""selftest_ingest.py - finished testq jobs become RUNNER verify/finding/note events (ingest.py), once.

A temp queue holds hand-made done/ records; rimflow writes a temp ledger (RIMFLOW_LEDGER / RIMFLOW_ITEMS), and the
git step is off (TESTQ_INGEST_PUSH=0). Proves: DONE with FAIL rows -> verify fail plus one finding per FAIL;
all PASS -> pass; PASS + UNMEASURED -> partial; INVALID -> a note; no item -> nothing; an unknown item -> an error
on the record, no crash; a second ingest writes nothing; an ingest that died before marking the record reuses its
run and findings instead of writing them twice.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
sys.path.insert(0, HERE)
import schema as S  # noqa: E402

FAILS = []
ITEM = "SOME_ITEM_FIX_IT"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def done_rec(item, outcome="DONE", cause=None, rows=(("r1", "PASS"), ("r2", "FAIL"), ("r3", "FAIL"))):
    job = S.make_job("Mock", {"rows": [r for r, _ in rows]}, "fix", "BENCH", "abc1234", item=item)
    rws = [{"chain": "c1", "row": r, "verdict": v, "detail": "d"} for r, v in rows]
    res = {"schema": S.RESULT_SCHEMA, "job": job["id"], "attempt": job["id"] + ".a1", "outcome": outcome,
           "cause": cause, "rows": rws if outcome == "DONE" else [], "counts": S.count_verdicts(rws),
           "runner_sha": "def5678", "artifacts": [{"path": "/x/Mock_1.json"}, {"path": "/x/Mock_1.html"}],
           "note": "why"}
    return {"job": job, "result": res, "attempts": [res["attempt"]], "finished": S.utcnow()}


def main():
    tmp = tempfile.mkdtemp(prefix="rf_ingest_")
    try:
        queue, items = os.path.join(tmp, "queue"), os.path.join(tmp, "items")
        led = os.path.join(tmp, "ledger", "events.jsonl")
        for d in (os.path.join(queue, "done"), items, os.path.dirname(led)):
            os.makedirs(d)
        open(led, "w").close()
        env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "CLAUDE_PROJECT_DIR")}
        env.update(TESTQ_QUEUE=queue, RIMFLOW_LEDGER=led, RIMFLOW_ITEMS=items, TESTQ_INGEST_PUSH="0")
        r = subprocess.run([sys.executable, CLI, "file", ITEM, "--for", "BENCH", "--title", "t", "--seat", "BENCH"],
                           env=env, capture_output=True, text=True, timeout=120)
        check(r.returncode == 0, "the test item is filed in the temp ledger: %s" % r.stderr[-200:])
        shard = os.path.join(tmp, "ledger", "events", "RUNNER.jsonl")

        def events():
            try:
                return [json.loads(x) for x in open(shard)]
            except OSError:
                return []

        def ingest():
            return subprocess.run([sys.executable, os.path.join(HERE, "ingest.py")], env=env, capture_output=True,
                                  text=True, timeout=300)

        recs = {"fail": done_rec(ITEM), "pass": done_rec(ITEM, rows=(("r1", "PASS"),)),
                "partial": done_rec(ITEM, rows=(("r1", "PASS"), ("r4", "UNMEASURED"))),
                "invalid": done_rec(ITEM, "INVALID", "HANG"), "noitem": done_rec(None),
                "unknown": done_rec("NO_SUCH_ITEM_HERE")}
        for k, rec in recs.items():
            S.dump(rec, os.path.join(queue, "done", rec["job"]["id"] + ".json"))
        r = ingest()
        check(r.returncode == 0, "ingest runs: %s" % r.stderr[-300:])
        evs = events()
        verifies = [e for e in evs if e["event"] == "verify"]
        check(sorted(e["result"] for e in verifies) == ["fail", "partial", "pass"],
              "one verify per DONE job, results fail/pass/partial: %s" % [e["result"] for e in verifies])
        check(all(e["seat"] == "RUNNER" and e["config"] == "steve-targeted" and e["sha"] == "def5678" and
                  "Mock_1.html" in e["evidence"] for e in verifies), "verifies carry seat, config, sha and the sheet")
        fnd = [e for e in evs if e["event"] == "finding"]
        check(len(fnd) == 2 and all(e["from"].startswith(ITEM + "/run-") and e["type"] == "UNTRIAGED" for e in fnd),
              "one finding per FAIL row, from its run: %s" % [e["name"] for e in fnd])
        notes = [e for e in evs if e["event"] == "note"]
        check(len(notes) == 1 and "INVALID/HANG" in notes[0]["text"], "a non-DONE run is a note, not a verify")
        got = {k: json.load(open(os.path.join(queue, "done", rec["job"]["id"] + ".json")))["ingested"]
               for k, rec in recs.items()}
        check("skipped" in got["noitem"] and "error" in got["unknown"], "no item -> skipped; unknown item -> error")
        n = len(evs)
        ingest()
        check(len(events()) == n, "a second ingest writes nothing")
        p = os.path.join(queue, "done", recs["fail"]["job"]["id"] + ".json")
        rec = json.load(open(p))
        run = rec["ingested"]["run"]
        del rec["ingested"]
        S.dump(rec, p)
        ingest()
        again = json.load(open(p))["ingested"]
        check(len(events()) == n and again.get("run") == run and len(again.get("findings", [])) == 2,
              "an ingest that died before marking reuses its run and findings: %s" % again)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
