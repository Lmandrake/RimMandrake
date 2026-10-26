#!/usr/bin/env python3
"""ingest.py - finished test-queue jobs become RUNNER ledger events (STEVEDESKTOP_RUNNER_WIRE_OWN_LEDGER_SEAT).

Plan: design/RimMandrake/test_orchestration_two_machines_2026-10-25.md item #5. The testq-tick service runs it after
every tick, from the dispatch clone (~/rm/dispatch), so the only writer of the RUNNER shard is that clone.

For each done/<job>.json not yet ingested, whose job names a rimflow item:
  outcome DONE      -> `rimflow verify ITEM --result pass|fail|partial --config steve-<profile>` as seat RUNNER
                       (fail: any FAIL row; pass: every row PASS; partial: otherwise), --sha the runner's commit,
                       --evidence the sheet on SteveDesktop plus the attempt id; then ONE finding per FAIL row,
                       --from that run, type UNTRIAGED (a human or seat decides MOD/SITE/HARNESS).
  any other outcome -> a note on the item (INVALID/REFUSED/INTERRUPTED measured nothing about the mod).
  no item           -> nothing on the ledger.
The done record gets "ingested" either way. Idempotent: a verify already in the RUNNER shard for that attempt is
reused, never written twice. Then the shard is committed and pushed (TESTQ_INGEST_PUSH=0 skips the git step).
"""
import fcntl
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import testq as T  # noqa: E402

REPO = T.REPO
CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
SHARD_REL = os.path.join("infrastructure", "state", "ledger", "events", "RUNNER.jsonl")


def shard_path():
    led = os.environ.get("RIMFLOW_LEDGER")       # rimflow's own redirect (selftests): shards sit beside it
    return os.path.join(os.path.dirname(led), "events", "RUNNER.jsonl") if led else os.path.join(REPO, SHARD_REL)


def rimflow(*args):
    env = dict(os.environ, RIMFLOW_SEAT="RUNNER", CLAUDE_PROJECT_DIR=REPO)
    r = subprocess.run([sys.executable, CLI] + list(args), env=env, capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def verdict(res):
    counts = res.get("counts") or {}
    if counts.get("FAIL"):
        return "fail"
    return "pass" if counts and set(counts) == {"PASS"} else "partial"


def sheet_of(res):
    paths = [a["path"] for a in res.get("artifacts") or []]
    return next((p for p in paths if p.endswith(".html")), paths[0] if paths else "no sheet")


def recorded_run(item, attempt):
    """The run name of a verify already on the ledger for this attempt, or None. The shard is grepped first (cheap);
    only a hit pays for a replay, which is what numbers runs."""
    try:
        with open(shard_path(), encoding="utf-8") as f:
            if attempt not in f.read():
                return None
    except OSError:
        return None
    code = ("import os, sys; sys.path.insert(0, %r); import model\n"
            "model.EVENTS = os.environ.get('RIMFLOW_LEDGER') or model.EVENTS\n"
            "it = model.replay(model.read()).items.get(%r)\n"
            "print(next((r.name for r in (it.runs if it else []) if %r in (r.evidence or '')), ''))"
            % (os.path.dirname(CLI), item, attempt))
    r = subprocess.run([sys.executable, "-c", code], env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO),
                       capture_output=True, text=True, timeout=120)
    return r.stdout.strip() or None


def finding_name(mod, row, job_id):
    base = re.sub(r"[^A-Z0-9]+", "_", ("%s_%s" % (mod, row)).upper()).strip("_")[:44]
    return "%s_FAILS_%s" % (base, job_id[-6:].upper())


def ingest_one(rec):
    job, res = rec["job"], rec["result"]
    item, att = job.get("item"), res["attempt"]
    if not item:
        return {"skipped": "the job names no item"}
    if res["outcome"] != "DONE":
        rc, out = rimflow("note", item, "--text", "testq %s on SteveDesktop: %s/%s, no verdict recorded (%s)"
                          % (att, res["outcome"], res.get("cause"), (res.get("note") or "")[:160]))
        return {"note": rc == 0, "out": out[-200:]}
    config = "steve-%s" % job.get("profile", "targeted")
    run = recorded_run(item, att)
    if not run:
        rc, out = rimflow("verify", item, "--result", verdict(res), "--config", config,
                          "--evidence", "stevedesktop:%s (testq %s)" % (sheet_of(res), att),
                          "--sha", res.get("runner_sha") or job["source_sha"])
        m = re.search(r"(\S+/run-\d+@\S+) recorded", out)
        if rc != 0 or not m:
            return {"error": out[-300:]}
        run = m.group(1)
    found = []
    try:
        with open(shard_path(), encoding="utf-8") as f:
            shard = f.read()
    except OSError:
        shard = ""
    for row in res.get("rows") or []:
        if row["verdict"] != "FAIL":
            continue
        name = finding_name(job["mod"], row["row"], job["id"])
        if '"%s"' % name in shard:             # filed by an ingest that died before marking the record
            found.append(name)
            continue
        rc, out = rimflow("finding", "--from", run, "--name", name, "--type", "UNTRIAGED", "--severity", "medium",
                          "--why", "%s/%s FAIL on SteveDesktop: %s" % (row.get("chain"), row["row"],
                                                                       (row.get("detail") or "")[:160]))
        found.append(name if rc == 0 else "%s: %s" % (name, out[-120:]))
    return {"run": run, "result": verdict(res), "findings": found}


def publish(n):
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=300)
    git("add", "--", SHARD_REL)
    if git("diff", "--cached", "--quiet", "--", SHARD_REL).returncode != 0:
        c = git("commit", "-q", "-m", "ledger: RUNNER ingest of %d testq job(s)" % n, "--", SHARD_REL)
        if c.returncode != 0:
            return "commit failed: " + c.stderr.strip()[-200:]
    p = None
    for _ in range(3):
        git("pull", "-q", "--rebase", "origin", "main")
        p = git("push", "-q", "origin", "HEAD:main")
        if p.returncode == 0:
            return "pushed"
    return "push failed (the commit stays local; the next ingest retries): " + p.stderr.strip()[-200:]


def main():
    T.ensure_dirs()
    with open(T.q("ingest.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("ingest already running")
            return 0
        n = 0
        for path in sorted(os.listdir(T.q("done"))):
            rec = T.read_json(T.q("done", path))
            if not rec or "ingested" in rec or not path.endswith(".json"):
                continue
            out = ingest_one(rec)
            rec["ingested"] = dict(out, at=T.S.utcnow())
            T.S.dump(rec, T.q("done", path))
            T.log("ingest %s -> %s" % (rec["job"]["id"], json.dumps(out)[:300]))
            n += 1
        ahead = subprocess.run(["git", "-C", REPO, "rev-list", "--count", "origin/main..HEAD"], capture_output=True,
                               text=True).stdout.strip()
        if os.environ.get("TESTQ_INGEST_PUSH", "1") != "0" and (n or ahead not in ("", "0")):
            T.log("ingest git: %s" % publish(n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
