#!/usr/bin/env python3
"""ingest.py - finished test-queue jobs become RUNNER ledger events (STEVEDESKTOP_RUNNER_WIRE_OWN_LEDGER_SEAT).

Plan: design/RimMandrake/test_orchestration_two_machines_2026-10-25.md item #5. The testq-tick service runs it after
every tick, from the dispatch clone (~/rm/dispatch), so the only writer of the RUNNER shard is that clone.

For each done/<job>.json not yet ingested, whose job names a rimflow item:
  outcome DONE      -> `rimflow verify ITEM --result pass|fail|partial --config steve-<profile>` (archmagi-<profile> from the backfill) as seat RUNNER
                       (fail: any FAIL row; pass: every row PASS; partial: otherwise), --sha the runner's commit,
                       --evidence the sheet on SteveDesktop plus the attempt id; then ONE finding per FAIL row,
                       --from that run, type UNTRIAGED (a human or seat decides MOD/SITE/HARNESS).
  any other outcome -> a note on the item (INVALID/REFUSED/INTERRUPTED measured nothing about the mod), once per
                       attempt; a refused note (item not on origin yet) is an error, retried like a verify.
  no item           -> nothing on the ledger, unless job.row_items (submit --row-item ROW_OR_CHAIN=ITEM) maps rows to
                       items or TESTQ_HOST_ITEM names a standing host: then each item is verified from ITS rows only.
A lane-pausing outcome (testq.PAUSE_ON: a red canary, a refused runner pull) is also, item or not, a failed run of
the lane (verify STEVE_LANE_MONITOR_PAUSE_FINDINGS --config steve-lane) plus one finding from it,
STEVE_LANE_<CANARY_RED|SYNC_REFUSED>_<JOBHEX6> (design section 6: pause the lane, file a finding).
The done record gets "ingested" either way, except after an error (typically an item filed in a seat clone that
has not reached origin yet): that record is retried every TESTQ_INGEST_RETRY_S (600) and marked ingested with the
error only after TESTQ_INGEST_MAX_TRIES (6) tries. Idempotent: a verify already in the RUNNER shard for that attempt is
reused, never written twice. Then the shard is committed and pushed (TESTQ_INGEST_PUSH=0 skips the git step); a
pull --rebase that fails is aborted and stops that publication with the commit kept local, never pushed half-rebased;
any later ingest publishes RUNNER lines left uncommitted or commits left unpushed, even with nothing new to ingest.
"""
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import testq as T  # noqa: E402

REPO = T.REPO
CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
SHARD_REL = os.path.join("infrastructure", "state", "ledger", "events", "RUNNER.jsonl")
RETRY_S = int(os.environ.get("TESTQ_INGEST_RETRY_S", "600"))
MAX_TRIES = int(os.environ.get("TESTQ_INGEST_MAX_TRIES", "6"))


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
    # the attempt must stand whole in the evidence: JOB.a1 is not JOB.a10
    pat = re.escape(attempt) + r"(?![\w.])"
    code = ("import os, re, sys; sys.path.insert(0, %r); import model\n"
            "model.EVENTS = os.environ.get('RIMFLOW_LEDGER') or model.EVENTS\n"
            "it = model.replay(model.read()).items.get(%r)\n"
            "print(next((r.name for r in (it.runs if it else []) if re.search(%r, r.evidence or '')), ''))"
            % (os.path.dirname(CLI), item, pat))
    r = subprocess.run([sys.executable, "-c", code], env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO),
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:     # a failed lookup is not "no run": verifying anyway would record the attempt twice
        raise RuntimeError("replay for %s failed (exit %d): %s" % (item, r.returncode, (r.stderr or "").strip()[-160:]))
    return r.stdout.strip() or None


def filed(name, run):
    """True when the shard already holds finding NAME from RUN (an ingest that died before marking its record). Only
    the same run counts: a name is not unique, and another item's finding must never pass for this one's."""
    try:
        with open(shard_path(), encoding="utf-8") as f:
            for line in f:
                if '"%s"' % name in line:
                    try:
                        e = json.loads(line)
                    except ValueError:
                        continue
                    if e.get("event") == "finding" and e.get("name") == name and e.get("from") == run:
                        return True
    except OSError:
        pass
    return False


def finding_name(mod, row, job_id, salt=False, chain=None):
    """MOD_ROW_FAILS_JOBHEX6. When folding the row to A-Z0-9_ loses anything (a cut at 44, `foo-bar` vs `foo_bar`),
    6 hex of the raw mod/row keep two rows of one job from sharing a name (one would pass for the other's finding).
    `chain` (given only when one row id FAILs in two chains) joins the hashed text, so those two differ as well."""
    raw = "%s_%s" % (mod, row)
    full = re.sub(r"[^A-Z0-9]+", "_", raw.upper()).strip("_")
    base = full[:44]
    if salt or base != raw.upper():
        key = raw if chain is None else "%s\0%s" % (raw, chain)
        base = "%s_%s" % (base[:37].rstrip("_"), hashlib.sha1(key.encode("utf-8")).hexdigest()[:6].upper())
    return "%s_FAILS_%s" % (base, job_id[-6:].upper())


LANE_ITEM = os.environ.get("TESTQ_LANE_ITEM", "STEVE_LANE_MONITOR_PAUSE_FINDINGS")
LANE_TWIST = {("INVALID", "CANARY"): "CANARY_RED", ("REFUSED", "SYNC"): "SYNC_REFUSED"}


def lane_finding(job, res):
    """An outcome that paused the lane is a failed run of the lane itself: RUNNER may only verify/finding/note, so it
    records `verify LANE_ITEM --result fail --config steve-lane` and one finding from that run. Idempotent: the run
    is reused by attempt (recorded_run) and the finding by grepping the shard for its name."""
    key = (res["outcome"], res.get("cause"))
    if key not in T.PAUSE_ON:
        return None
    att = res["attempt"]
    name = "STEVE_LANE_%s_%s" % (LANE_TWIST.get(key, "PAUSED"), job["id"][-6:].upper())
    run = recorded_run(LANE_ITEM, att)
    if not run:
        rc, out = rimflow("verify", LANE_ITEM, "--result", "fail", "--config", "steve-lane",
                          "--evidence", "stevedesktop: testq %s %s/%s" % (att, key[0], key[1]),
                          "--sha", res.get("runner_sha") or job["source_sha"])
        m = re.search(r"(\S+/run-\d+@\S+) recorded", out)
        if rc != 0 or not m:
            return "lane run not recorded: " + out[-160:]
        run = m.group(1)
    if filed(name, run):
        return name
    rc, out = rimflow("finding", "--from", run, "--name", name, "--type", "UNTRIAGED", "--severity", "high",
                      "--why", "SteveDesktop lane paused: %s (testq %s: %s); it admits nothing until "
                      "`testq.py resume --reason`" % (T.PAUSE_ON[key], att, (res.get("note") or "")[:160]))
    return name if rc == 0 else "lane finding not recorded: %s: %s" % (name, out[-160:])


def note_once(item, needle, text):
    """Note ITEM unless the shard already holds a note on it whose text contains NEEDLE (an earlier try of this
    record) -> True when the note is on the ledger. A refused note (the item not on origin yet) is retried like a
    verify instead of being lost when the record is marked."""
    try:
        with open(shard_path(), encoding="utf-8") as f:
            for line in f:
                if needle in line:
                    e = json.loads(line)
                    if e.get("event") == "note" and e.get("id") == item and needle in (e.get("text") or ""):
                        return True
    except (OSError, ValueError):
        pass
    return rimflow("note", item, "--text", text)[0] == 0


def ingest_one(rec):
    job, res = rec["job"], rec["result"]
    item, att = job.get("item"), res["attempt"]
    lane = lane_finding(job, res)
    if lane and lane.startswith("lane "):  # run or finding not recorded (host item not on origin yet): retried
        return {"error": lane}
    if not item and not job.get("row_items") and not os.environ.get("TESTQ_HOST_ITEM"):
        return dict({"skipped": "the job names no item"}, **({"lane_finding": lane} if lane else {}))
    # the standing host stands in only for a job with no item of its own (as in groups_of)
    host = None if item else os.environ.get("TESTQ_HOST_ITEM")
    items = sorted({i for i in [item, host] + list((job.get("row_items") or {}).values()) if i})
    failed = []
    if lane:
        for it in items:
            needle = "testq %s paused the SteveDesktop lane" % att
            if not note_once(it, needle, "%s; finding %s" % (needle, lane)):
                failed.append(it)
    if res["outcome"] != "DONE":
        for it in items:
            needle = "testq %s on SteveDesktop:" % att
            if not note_once(it, needle, "%s %s/%s, no verdict recorded (%s)"
                             % (needle, res["outcome"], res.get("cause"), (res.get("note") or "")[:160])):
                failed.append(it)
        if failed:
            return {"error": "note refused on %s" % ",".join(sorted(set(failed)))}
        return {"note": True}
    if failed:
        return {"error": "lane note refused on %s" % ",".join(sorted(set(failed)))}
    return ingest_done(job, res, item)


def groups_of(job, res):
    """-> {item: [rows]}: each row goes to the item its row id (else its chain) maps to in job["row_items"], else to the
    job's item, else to TESTQ_HOST_ITEM (a standing host for item-less sweeps/filler; unset: such rows are dropped).
    A sheet's verdict is never recorded on an item whose rows it does not hold (TESTQ_INGEST_FIX_ONE_ITEM_MANY_ROWS)."""
    ri = job.get("row_items") or {}
    default = job.get("item") or os.environ.get("TESTQ_HOST_ITEM") or None
    out = {}
    for row in res.get("rows") or []:
        it = ri.get(row.get("row")) or ri.get(row.get("chain")) or default
        if it:
            out.setdefault(it, []).append(row)
    return out


def ingest_done(job, res, item):
    att = res["attempt"]
    groups = groups_of(job, res)
    if item and item not in groups and not job.get("row_items"):
        groups[item] = []                      # unchanged: a job for an item with no rows still gets its verdict
    if not groups:
        return {"skipped": "no row maps to an item"}
    out, errs = {}, []
    for it, rows in sorted(groups.items()):     # every group is tried: one item not on origin yet blocks no other
        r = ingest_group(job, res, it, dict(res, rows=rows, counts=T.S.count_verdicts(rows)), att)
        if "error" in r:
            errs.append("%s: %s" % (it, r["error"]) if len(groups) > 1 else r["error"])
        else:
            out[it] = r
    if errs:                                    # retried; the groups recorded here are reused (recorded_run)
        return dict({"error": " | ".join(errs)}, **({"groups": out} if out else {}))
    if len(out) == 1:
        return next(iter(out.values()))
    return {"groups": out, "result": ",".join("%s=%s" % (i, o["result"]) for i, o in out.items())}


def ingest_group(job, res, item, gres, att):
    host = res.get("host") or "stevedesktop"         # the archmagi backfill runs the same worker (host "archmagi")
    config = "%s-%s" % ("steve" if host == "stevedesktop" else host, job.get("profile", "targeted"))
    run = recorded_run(item, att)
    if not run:
        rc, out = rimflow("verify", item, "--result", verdict(gres), "--config", config,
                          "--evidence", "%s:%s (testq %s)" % (host, sheet_of(res), att),
                          "--sha", res.get("runner_sha") or job["source_sha"])
        m = re.search(r"(\S+/run-\d+@\S+) recorded", out)
        if rc != 0 or not m:
            return {"error": out[-300:]}
        run = m.group(1)
    found = []
    fails = [row for row in gres.get("rows") or [] if row["verdict"] == "FAIL"]
    plain = [finding_name(job["mod"], row["row"], job["id"]) for row in fails]
    taken = set()
    for row, name in zip(fails, plain):
        if plain.count(name) > 1:              # rows only case apart (foo / FOO): each gets its own hash
            twin = sum(1 for r in fails if r["row"] == row["row"]) > 1    # one row id in two chains: chain joins it
            chain = str(row.get("chain")) if twin else None
            name = finding_name(job["mod"], row["row"], job["id"], salt=True, chain=chain)
        k = 0
        while name in taken:                   # a salted name can hit another row's name: re-salt until distinct
            k += 1
            name = finding_name(job["mod"], row["row"], job["id"], salt=True,
                                chain="%s#%d" % (row.get("chain"), k))
        taken.add(name)
        if filed(name, run):                   # filed by an ingest that died before marking the record
            found.append(name)
            continue
        rc, out = rimflow("finding", "--from", run, "--name", name, "--type", "UNTRIAGED", "--severity", "medium",
                          "--why", "%s/%s FAIL on %s: %s" % (row.get("chain"), row["row"],
                                                           "SteveDesktop" if host == "stevedesktop" else host,
                                                           (row.get("detail") or "")[:160]))
        if rc != 0:     # retried: the run is reused, findings already filed are found in the shard
            return {"error": "finding %s not recorded: %s" % (name, out[-120:])}
        found.append(name)
    return {"run": run, "result": verdict(gres), "findings": found}


def publish(n, shard_rel=SHARD_REL, message=None):
    """_publish, after clearing a leftover rebase / stale index.lock (clear_leftovers); what it did leads the result."""
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=300)
    pre = clear_leftovers(git)
    if pre and pre.startswith("publish stopped"):
        return pre
    out = _publish(n, shard_rel, message)
    return "%s; %s" % (pre, out) if pre else out


def _publish(n, shard_rel=SHARD_REL, message=None):
    """Commit `shard_rel` alone, pull --rebase, lint, push. Also the RimFlow v3 Dispatcher's publisher for its
    DISPATCHER shard (rimflow/dispatcher.py passes its own shard and message)."""
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=300)
    a = git("add", "--", shard_rel)
    if a.returncode != 0:
        return "add failed (the lines stay in the working tree; the next ingest retries): " + a.stderr.strip()[-200:]
    if git("diff", "--cached", "--quiet", "--", shard_rel).returncode != 0:
        c = git("commit", "-q", "-m", message or "ledger: RUNNER ingest of %d testq job(s)" % n, "--", shard_rel)
        if c.returncode != 0:
            return "commit failed: " + c.stderr.strip()[-200:]
    p = None
    for _ in range(3):
        r = git("pull", "-q", "--rebase", "origin", "main")
        if r.returncode != 0:
            # A failed rebase leaves a detached, conflicted tree: pushing HEAD then pushes origin's own tip and
            # "succeeds" while the RUNNER commit sits unapplied (drill 2026-10-26). Abort, keep the commit local,
            # stop publication (design section 6: no reset, no stash, no game re-run).
            gd = git("rev-parse", "--git-dir").stdout.strip()
            rebasing = any(os.path.isdir(os.path.join(REPO, gd, d)) for d in ("rebase-merge", "rebase-apply"))
            if rebasing:
                git("rebase", "--abort")
            return "publish stopped: pull --rebase failed%s, the commit stays local (the next ingest retries): " % \
                (", rebase aborted" if rebasing else "") + (r.stderr or r.stdout).strip()[-200:]
        bad = lint_refusal()
        if bad:
            return "publish stopped: ledger_lint refuses HEAD, the commit stays local (the next ingest retries): " + bad
        p = git("push", "-q", "origin", "HEAD:main")
        if p.returncode == 0:
            return "pushed"
    return "push failed (the commit stays local; the next ingest retries): " + p.stderr.strip()[-200:]


STALE_LOCK_S = 300


def git_procs_in_repo():
    """pids of live git processes whose cwd is inside REPO (a /proc scan; the lock holder is one of these)."""
    found = []
    try:
        pids = [p for p in os.listdir("/proc") if p.isdigit()]
    except OSError:
        return found
    root = os.path.realpath(REPO)
    for pid in pids:
        try:
            with open("/proc/%s/cmdline" % pid, "rb") as f:
                argv0 = f.read().split(b"\0")[0].decode("utf-8", "replace")
            if os.path.basename(argv0) != "git" or int(pid) == os.getpid():
                continue
            cwd = os.path.realpath(os.readlink("/proc/%s/cwd" % pid))
        except (OSError, ValueError):
            continue
        if cwd == root or cwd.startswith(root + os.sep):
            found.append(int(pid))
    return found


def clear_leftovers(git, now=None, procs=git_procs_in_repo):
    """Before publish touches the index: (1) a rebase a killed publish left half done is aborted, or the next commit
    lands on a detached HEAD that `rebase --abort` then drops (review S, F2); (2) a stale .git/index.lock (older than
    STALE_LOCK_S, no live git process in the clone) is removed, one still held by a git process stops the publish
    (review S, F3). -> None, or a message: "publish stopped: ..." stops, anything else is a log of what was done
    (callers prefix it to their result)."""
    gd = git("rev-parse", "--git-dir").stdout.strip()
    gd = gd if os.path.isabs(gd) else os.path.join(REPO, gd)
    notes = []
    lock = os.path.join(gd, "index.lock")
    if os.path.exists(lock):
        try:
            age = (now if now is not None else time.time()) - os.path.getmtime(lock)
        except OSError:
            age = 0
        if age >= STALE_LOCK_S:
            live = procs()
            if live:
                return "publish stopped: index.lock is %d s old and git process(es) %s hold the clone" % (age, live)
            try:
                os.remove(lock)
                notes.append("removed stale index.lock (%d s old, no live git process)" % age)
            except OSError as e:
                return "publish stopped: stale index.lock (%d s old) could not be removed: %s" % (age, e)
        else:
            return "publish stopped: index.lock present (%d s old, under %d s: another git may be running)" % (
                age, STALE_LOCK_S)
    if any(os.path.isdir(os.path.join(gd, d)) for d in ("rebase-merge", "rebase-apply")):
        r = git("rebase", "--abort")
        notes.append("aborted a leftover rebase (exit %d)" % r.returncode)
        if r.returncode != 0:
            return "publish stopped: leftover rebase could not be aborted: " + (r.stderr or r.stdout).strip()[-200:]
    return "; ".join(notes) or None


def lint_refusal():
    """ledger_lint on HEAD vs origin/main, as the pre-push hook runs it (the dispatch clone has no hooks:
    TESTQ_DISPATCH_PUSH_ENFORCE_LINT) -> None when clean, else why not to push. A lint that cannot run or crashes
    refuses too: this pusher is unattended, so it never pushes unlinted."""
    script = os.path.join(REPO, "src", "RimMandrake", "Utils", "ledger_lint.py")
    if not os.path.isfile(script):                   # a sparse clone without it: lint with this checkout's copy
        script = os.path.join(HERE, "..", "ledger_lint.py")
    try:
        r = subprocess.run([sys.executable, script, "--rev", "HEAD", "--root", REPO, "--base", "origin/main"],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return "ledger_lint could not run: %s" % e
    out = (r.stdout or "") + (r.stderr or "")
    finished = re.search(r"^ledger_lint: \d+ findings? over ", out, re.M)
    if r.returncode == 0 and finished:
        return None
    lines = [ln.strip() for ln in out.splitlines() if ln.strip() and not ln.startswith("note:")]
    return ("exit %d: " % r.returncode) + " | ".join(lines[-4:])[-300:]


def unpublished(shard_rel=SHARD_REL):
    """True when an earlier ingest left work behind: RUNNER lines not committed (a publish that died or failed
    before its commit; the done records are already marked, so n is 0 from then on) or commits not pushed."""
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=60).stdout.strip()
    return bool(git("status", "--porcelain", "--", shard_rel)) or git("rev-list", "--count", "origin/main..HEAD") \
        not in ("", "0")


def rebase_left(clear=True):
    """A publish killed mid-rebase leaves the shard in the rebase's tree; lines ingested into it would be thrown away by
    the `rebase --abort` publish runs, with their records already marked. So leftovers are cleared BEFORE ingesting,
    and while a rebase is still there nothing is ingested (-> True)."""
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=300)
    pre = clear_leftovers(git) if clear else None     # publication off: look, never touch
    if pre:
        T.log("ingest pre-clear: %s" % pre)
    gd = git("rev-parse", "--git-dir").stdout.strip()
    gd = gd if os.path.isabs(gd) else os.path.join(REPO, gd)
    if any(os.path.isdir(os.path.join(gd, d)) for d in ("rebase-merge", "rebase-apply")):
        T.log("ingest skipped: a rebase is still in progress in %s" % REPO)
        return True
    return False


def main():
    T.ensure_dirs()
    with open(T.q("ingest.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("ingest already running")
            return 0
        push = os.environ.get("TESTQ_INGEST_PUSH", "1") != "0"
        if rebase_left(clear=push):
            return 0
        n = 0
        for path in sorted(os.listdir(T.q("done"))):
            rec = T.read_json(T.q("done", path))
            if not rec or "ingested" in rec or not path.endswith(".json"):
                continue
            pend = rec.get("ingest_pending") or {}
            if pend and time.time() - pend.get("last", 0) < RETRY_S:
                continue
            try:
                out = ingest_one(rec)
            except Exception as ex:     # noqa: BLE001 - one bad record (a rimflow timeout) must not stop the rest
                out = {"error": "crash: %s: %s" % (type(ex).__name__, ex)}
            tries = pend.get("tries", 0) + 1
            if "error" in out and tries < MAX_TRIES:
                rec["ingest_pending"] = {"tries": tries, "last": time.time(), "error": out["error"]}
                T.S.dump(rec, T.q("done", path))
                T.log("ingest %s: try %d of %d failed, retried in %d s: %s"
                      % (rec["job"]["id"], tries, MAX_TRIES, RETRY_S, out["error"][-200:]))
                continue
            rec.pop("ingest_pending", None)
            rec["ingested"] = dict(out, at=T.S.utcnow())
            T.S.dump(rec, T.q("done", path))
            T.log("ingest %s -> %s" % (rec["job"]["id"], json.dumps(out)[:300]))
            n += 1
        if push and (n or unpublished()):
            T.log("ingest git: %s" % publish(n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
