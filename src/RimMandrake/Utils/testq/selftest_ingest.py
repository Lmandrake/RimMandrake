#!/usr/bin/env python3
"""selftest_ingest.py - finished testq jobs become RUNNER verify/finding/note events (ingest.py), once.

A temp queue holds hand-made done/ records; rimflow writes a temp ledger (RIMFLOW_LEDGER / RIMFLOW_ITEMS), and the
git step is off (TESTQ_INGEST_PUSH=0). Proves: DONE with FAIL rows -> verify fail plus one finding per FAIL;
all PASS -> pass; PASS + UNMEASURED -> partial; INVALID -> a note; a lane-pausing outcome (red canary) -> one
finding item for BENCH even with no job item; no item -> nothing; an unknown item -> retried,
not marked, no crash; a second ingest writes nothing; an ingest that died before marking the record reuses its
run and findings instead of writing them twice; an item filed late is verified on the retry; an item never filed is
marked with its error after the last try; a non-DONE note refused for an item not filed yet is retried and lands
once. publish() in a sandbox (bare origin + clone): a pull --rebase that
conflicts is aborted and stops publication with the commit kept local on its branch (the old code pushed origin's
own tip and reported "pushed"); origin moving on another file is rebased over and pushed; shard lines a publish
left uncommitted make the next ingest publish though it has nothing new (the old ahead-only check never retried).
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
LANE = "STEVE_LANE_MONITOR_PAUSE_FINDINGS"
LATE = "LATE_ITEM_FIX_AFTER"
MANY_A, MANY_B = "MANY_ROWS_FIX_ALPHA", "MANY_ROWS_FIX_BETA"
NOTE_LATE = "LATE_NOTE_FIX_AFTER"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def done_rec(item, outcome="DONE", cause=None, rows=(("r1", "PASS"), ("r2", "FAIL"), ("r3", "FAIL")), row_items=None):
    job = S.make_job("Mock", {"rows": [r for r, _ in rows]}, "fix", "BENCH", "abc1234", item=item,
                     row_items=row_items or {})
    rws = [{"chain": "c1", "row": r, "verdict": v, "detail": "d"} for r, v in rows]
    res = {"schema": S.RESULT_SCHEMA, "job": job["id"], "attempt": job["id"] + ".a1", "outcome": outcome,
           "cause": cause, "rows": rws if outcome == "DONE" else [], "counts": S.count_verdicts(rws),
           "runner_sha": "def5678", "artifacts": [{"path": "/x/Mock_1.json"}, {"path": "/x/Mock_1.html"}],
           "note": "why"}
    return {"job": job, "result": res, "attempts": [res["attempt"]], "finished": S.utcnow()}


LINT_CLEAN = 'print("ledger_lint: 0 findings over 1 commit")\n'
LINT_REFUSE = 'import sys\nprint("NOT_APPEND events/RUNNER.jsonl")\nprint("ledger_lint: 1 finding over 1 commit")\nsys.exit(1)\n'


def publish_sandbox(conflict, lint=LINT_CLEAN):
    """Bare origin + a dispatch clone + a rival clone that pushes first. Returns (publish result, dispatch dir, sh)."""
    import ingest as I
    root = tempfile.mkdtemp(prefix="rf_pub_")
    bare, disp, rival = (os.path.join(root, n) for n in ("origin.git", "dispatch", "rival"))

    def sh(*a, cwd=None):
        return subprocess.run(["git"] + list(a), cwd=cwd, capture_output=True, text=True, timeout=60)
    ident = ["-c", "user.email=st@x", "-c", "user.name=st"]
    sh("init", "-q", "--bare", "-b", "main", bare)
    sh("clone", "-q", bare, rival)
    shard = I.SHARD_REL
    os.makedirs(os.path.join(rival, os.path.dirname(shard)))
    with open(os.path.join(rival, shard), "w") as f:
        f.write('{"a":1}\n')
    sh("add", shard, cwd=rival)
    sh(*ident, "commit", "-qm", "init", cwd=rival)
    sh("push", "-q", "origin", "HEAD:main", cwd=rival)
    sh("clone", "-q", bare, disp)
    for d in (disp, rival):
        sh("config", "user.email", "st@x", cwd=d)
        sh("config", "user.name", "st", cwd=d)
    with open(os.path.join(disp, shard), "a") as f:
        f.write('{"runner":"ingest"}\n')
    target = shard if conflict else "other.txt"   # no .gitattributes here: a same-shard append conflicts
    with open(os.path.join(rival, target), "a") as f:
        f.write('{"rival":"line"}\n')
    sh("add", target, cwd=rival)
    sh("commit", "-qm", "rival", cwd=rival)
    sh("push", "-q", "origin", "HEAD:main", cwd=rival)
    lint_py = os.path.join(disp, "src", "RimMandrake", "Utils", "ledger_lint.py")   # untracked: a stand-in lint
    os.makedirs(os.path.dirname(lint_py))
    with open(lint_py, "w") as f:
        f.write(lint)
    old = I.REPO
    I.REPO = disp
    try:
        out = I.publish(1)
    finally:
        I.REPO = old
    return out, root, disp, sh


def leftover_checks():
    import time
    """Review S F2/F3: a rebase left half done is aborted and a stale index.lock cleared before publish adds."""
    import ingest as I
    d = tempfile.mkdtemp(prefix="rf_left_")
    try:
        def sh(*a):
            return subprocess.run(["git", "-C", d, "-c", "user.email=a@b", "-c", "user.name=t"] + list(a),
                                  capture_output=True, text=True, timeout=60)
        sh("init", "-q", "-b", "main")
        f = os.path.join(d, "f.txt")
        for br, txt in (("main", "base\n"), ("x", "x\n"), ("main", "m\n")):
            if br == "x":
                sh("checkout", "-qb", "x")
            elif txt == "m\n":
                sh("checkout", "-q", "main")
            with open(f, "w") as fh:
                fh.write(txt)
            sh("add", "f.txt")
            sh("commit", "-qm", txt.strip())
        sh("checkout", "-q", "x")
        sh("rebase", "main")                       # conflicts: leaves .git/rebase-merge, detached HEAD
        gdir = os.path.join(d, ".git")
        check(os.path.isdir(os.path.join(gdir, "rebase-merge")), "setup: an interrupted rebase exists")
        lock = os.path.join(gdir, "index.lock")
        open(lock, "w").close()
        old = I.REPO
        I.REPO = d
        try:
            g = lambda *a: subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True, timeout=60)
            young = I.clear_leftovers(g, procs=lambda: [])
            check(young and young.startswith("publish stopped") and os.path.exists(lock),
                  "a young index.lock is left alone and stops the publish: %r" % young)
            later = time.time() + I.STALE_LOCK_S + 60
            held = I.clear_leftovers(g, now=later, procs=lambda: [4242])
            check(held.startswith("publish stopped") and "4242" in held and os.path.exists(lock),
                  "a stale lock with a live git process is NOT deleted: %r" % held)
            done = I.clear_leftovers(g, now=later, procs=lambda: [])
            check(not os.path.exists(lock) and "removed stale index.lock" in done, "a stale lock with no git is removed and logged: %r" % done)
            check("aborted a leftover rebase" in done and not os.path.isdir(os.path.join(gdir, "rebase-merge")),
                  "the leftover rebase is aborted before add: %r" % done)
            check(sh("symbolic-ref", "-q", "--short", "HEAD").stdout.strip() == "x", "back on a branch, not detached")
        finally:
            I.REPO = old
    finally:
        shutil.rmtree(d, ignore_errors=True)


def publish_checks():
    out, root, disp, sh = publish_sandbox(conflict=False, lint=LINT_REFUSE)
    try:
        sh("fetch", "-q", "origin", cwd=disp)
        ahead = sh("rev-list", "--count", "origin/main..HEAD", cwd=disp).stdout.strip()
        check(out.startswith("publish stopped: ledger_lint") and "NOT_APPEND" in out and ahead == "1",
              "ledger_lint refusing HEAD withholds the push, the commit stays local (%r ahead=%s)" % (out, ahead))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    out, root, disp, sh = publish_sandbox(conflict=False, lint="import sys\nsys.exit(2)\n")
    try:
        check(out.startswith("publish stopped: ledger_lint") and "exit 2" in out,
              "a lint that cannot finish also withholds the push (unattended pusher): %r" % out)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    out, root, disp, sh = publish_sandbox(conflict=True)
    try:
        rebasing = any(os.path.isdir(os.path.join(disp, ".git", d)) for d in ("rebase-merge", "rebase-apply"))
        branch = sh("symbolic-ref", "-q", "--short", "HEAD", cwd=disp).stdout.strip()
        sh("fetch", "-q", "origin", cwd=disp)
        ahead = sh("rev-list", "--count", "origin/main..HEAD", cwd=disp).stdout.strip()
        tip = sh("log", "-1", "--format=%s", "origin/main", cwd=disp).stdout.strip()
        check(out.startswith("publish stopped"), "a conflicting pull --rebase stops publication: %r" % out)
        check(not rebasing and branch == "main", "the rebase is aborted, back on main (rebasing=%s branch=%r)"
              % (rebasing, branch))
        check(ahead == "1" and tip == "rival", "the RUNNER commit stays local, origin untouched (ahead=%s tip=%r)"
              % (ahead, tip))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    out, root, disp, sh = publish_sandbox(conflict=False)
    try:
        import ingest as I
        with open(os.path.join(disp, I.SHARD_REL), "a") as f:   # a publish that died before its commit
            f.write('{"runner":"stranded"}\n')
        old, I.REPO = I.REPO, disp
        try:
            stranded = I.unpublished()
            I.publish(0)
            left = I.unpublished()
        finally:
            I.REPO = old
        check(stranded and not left, "RUNNER lines left uncommitted count as unpublished and the next publish "
              "ships them (before=%s after=%s)" % (stranded, left))
        sh("fetch", "-q", "origin", cwd=disp)
        ahead = sh("rev-list", "--count", "origin/main..HEAD", cwd=disp).stdout.strip()
        check(out == "pushed" and ahead == "0", "origin moved on another file: rebased and pushed (%r ahead=%s)"
              % (out, ahead))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def crash_checks():
    """A record whose ingest raises (a rimflow call timing out) is retried and counted like a returned error; it
    neither stops the records after it nor crashes ingest.py - a crash there failed the unit every tick, so no record
    ever reached its last try and the fill line after it never ran (the rig idled)."""
    import ingest as I
    tmp = tempfile.mkdtemp(prefix="rf_ingest_crash_")
    saved = (I.T.QHOME, I.ingest_one, os.environ.get("TESTQ_INGEST_PUSH"))
    try:
        os.makedirs(os.path.join(tmp, "done"))
        boom, fine = done_rec(ITEM), done_rec(None)
        boom["job"]["id"], fine["job"]["id"] = "A_boom", "B_fine"
        for rec in (boom, fine):
            S.dump(rec, os.path.join(tmp, "done", rec["job"]["id"] + ".json"))

        def fake(rec):
            if rec["job"]["id"] == "A_boom":
                raise subprocess.TimeoutExpired("rimflow", 120)
            return {"skipped": "no item"}
        I.T.QHOME, I.ingest_one = tmp, fake
        os.environ["TESTQ_INGEST_PUSH"] = "0"
        try:
            rc = I.main()
        except Exception as ex:     # noqa: BLE001 - the bug under test
            rc = "raised %s" % type(ex).__name__
        a = json.load(open(os.path.join(tmp, "done", "A_boom.json")))
        b = json.load(open(os.path.join(tmp, "done", "B_fine.json")))
        check(rc == 0, "an ingest_one that raises does not crash ingest.py: %s" % rc)
        check("crash: TimeoutExpired" in (a.get("ingest_pending") or {}).get("error", ""),
              "the raising record is pending a retry with its crash counted: %s" % a.get("ingest_pending"))
        check("ingested" in b, "the record after it is still ingested")
    finally:
        I.T.QHOME, I.ingest_one = saved[0], saved[1]
        if saved[2] is None:
            os.environ.pop("TESTQ_INGEST_PUSH", None)
        else:
            os.environ["TESTQ_INGEST_PUSH"] = saved[2]
        shutil.rmtree(tmp, ignore_errors=True)


def review_r1_checks():
    """Full-file review r1 (consult-20261028-003834-4019862) r2 (consult-20261028-005025-4040039), r3 (consult-20261028-005356-4044166): a finding rimflow refused is retried, never marked done
    without it (row and lane finding); one item not on origin yet blocks no other item's verdict; a replay that fails
    is not "no run recorded" (that verified the attempt twice); two rows of one job never share a finding name; a rebase
    left by a killed publish is cleared BEFORE ingesting (its abort threw away the lines ingested into it)."""
    import ingest as I
    tmp = tempfile.mkdtemp(prefix="rf_ingest_r1_")
    saved = (I.rimflow, I.recorded_run, I.shard_path, I.CLI, I.clear_leftovers, I.ingest_one, I.T.QHOME, I.publish,
             I.unpublished, I.REPO, os.environ.get("TESTQ_INGEST_PUSH"))
    calls = []

    def fake_rimflow(*a):
        calls.append(a)
        if a[0] == "verify":
            return (1, "refused: no item") if a[1].startswith("A_") else (0, "%s/run-1@x recorded" % a[1])
        return (1, "finding refused") if a[0] == "finding" else (0, "ok")
    try:
        I.rimflow, I.recorded_run = fake_rimflow, lambda item, att: None
        I.shard_path = lambda: os.path.join(tmp, "none.jsonl")
        rec = done_rec(ITEM)
        try:
            r = I.ingest_group(rec["job"], rec["result"], ITEM, rec["result"], rec["result"]["attempt"])
        except Exception as ex:     # noqa: BLE001
            r = {"raised": repr(ex)}
        check("error" in r, "a FAIL row's finding that rimflow refuses is an error (retried), not done: %s" % r)
        can = done_rec(None, "INVALID", "CANARY")
        try:
            r = I.ingest_one(can)
        except Exception as ex:     # noqa: BLE001
            r = {"raised": repr(ex)}
        check("error" in r, "a lane finding that rimflow refuses is an error (retried), not done: %s" % r)
        del calls[:]
        many = done_rec(None, rows=(("m1", "PASS"), ("m2", "PASS")), row_items={"m1": "A_FIRST", "m2": "B_SECOND"})
        try:
            r = I.ingest_one(many)
        except Exception as ex:     # noqa: BLE001
            r = {"raised": repr(ex)}
        vs = [c[1] for c in calls if c[0] == "verify"]
        check("error" in r and vs == ["A_FIRST", "B_SECOND"],
              "an item not on origin yet does not stop the next item's verify: verifies %s, %s" % (vs, r))
        I.rimflow, I.recorded_run = saved[0], saved[1]
        fake = os.path.join(tmp, "cli")
        os.makedirs(fake)
        open(os.path.join(fake, "model.py"), "w").write("raise SystemExit('replay broke')\n")
        open(os.path.join(tmp, "shard.jsonl"), "w").write('{"evidence": "ATT.a1"}\n')
        I.CLI, I.shard_path = os.path.join(fake, "cli.py"), lambda: os.path.join(tmp, "shard.jsonl")
        try:
            got = "returned %r" % (I.recorded_run("SOME_ITEM", "ATT.a1"),)
        except Exception as ex:     # noqa: BLE001
            got = "raised " + type(ex).__name__
        check(got.startswith("raised"), "a replay that fails is not 'no run recorded': %s" % got)
        open(os.path.join(fake, "model.py"), "w").write(
            "import types\nEVENTS = None\ndef read():\n    return []\n"
            "def replay(_):\n    run = types.SimpleNamespace(name='R10', evidence='h:/x.html (testq ATT.a10)')\n"
            "    return types.SimpleNamespace(items={'SOME_ITEM': types.SimpleNamespace(runs=[run])})\n")
        open(os.path.join(tmp, "shard.jsonl"), "w").write('{"evidence": "h:/x.html (testq ATT.a10)"}\n')
        got = (I.recorded_run("SOME_ITEM", "ATT.a1"), I.recorded_run("SOME_ITEM", "ATT.a10"))
        check(got == (None, "R10"), "attempt a1 does not reuse attempt a10's run: %s" % (got,))
        I.CLI, I.shard_path = saved[3], saved[2]
        I.rimflow = lambda *a: calls.append(a) or (0, "B_CASE/run-1@x recorded" if a[0] == "verify" else "ok")
        I.recorded_run, I.shard_path = (lambda item, att: None), (lambda: os.path.join(tmp, "none.jsonl"))
        del calls[:]
        cr = done_rec("B_CASE", rows=(("foo", "FAIL"), ("FOO", "FAIL")))
        I.ingest_group(cr["job"], cr["result"], "B_CASE", cr["result"], cr["result"]["attempt"])
        fn = [c[c.index("--name") + 1] for c in calls if c[0] == "finding"]
        check(len(fn) == 2 and len(set(fn)) == 2, "rows only case apart get two findings, two names: %s" % fn)
        del calls[:]                           # review ing_r4: one row id FAILing in two chains is two findings
        cr = done_rec("B_CASE", rows=(("r1", "FAIL"), ("r1", "FAIL")))
        cr["result"]["rows"][1]["chain"] = "c2"
        I.ingest_group(cr["job"], cr["result"], "B_CASE", cr["result"], cr["result"]["attempt"])
        fn = [c[c.index("--name") + 1] for c in calls if c[0] == "finding"]
        check(len(fn) == 2 and len(set(fn)) == 2, "one row id failing in two chains gets two findings: %s" % fn)
        del calls[:]                           # review r5: a disambiguated name may itself collide -> still distinct
        real_fn = I.finding_name
        I.finding_name = lambda mod, row, jid, salt=False, chain=None: (
            "SAME_FAILS_X" if (not salt or "#" not in str(chain)) and row.lower() != "bar" else real_fn(mod, row, jid, salt, chain))
        try:
            cr = done_rec("B_CASE", rows=(("foo", "FAIL"), ("FOO", "FAIL")))
            I.ingest_group(cr["job"], cr["result"], "B_CASE", cr["result"], cr["result"]["attempt"])
        finally:
            I.finding_name = real_fn
        fn = [c[c.index("--name") + 1] for c in calls if c[0] == "finding"]
        check(len(fn) == 2 and len(set(fn)) == 2, "a salted name that collides again is re-salted: %s" % fn)
        root = "/srv/clone"                    # review r6: a git run from elsewhere but aimed at this repo holds its lock
        hit = lambda argv, env, cwd: I.git_targets_repo(argv, env, cwd, root)
        check(hit(["git", "--git-dir=/srv/clone/.git", "update-index"], {}, "/tmp"), "--git-dir=X from elsewhere is ours")
        check(hit(["git", "--git-dir", "/srv/clone/.git", "x"], {}, "/tmp"), "--git-dir X (two args) is ours")
        check(hit(["git", "--work-tree=/srv/clone", "x"], {}, "/tmp"), "--work-tree is ours")
        check(hit(["git", "x"], {"GIT_DIR": "/srv/clone/.git"}, "/tmp"), "GIT_DIR in the environment is ours")
        check(hit(["git", "--git-dir=.git", "x"], {}, "/srv/clone"), "a relative --git-dir resolves against its cwd")
        check(hit(["git", "-C", "/srv/clone", "x"], {}, "/tmp"), "-C into the repo is ours")
        check(hit(["git", "-c", "user.name=Runner", "-C", "/srv/clone", "commit"], {}, "/tmp"), "-c K=V does not end option parsing")
        check(hit(["git", "-C", "/srv", "--git-dir=clone/.git", "--work-tree=clone", "commit"], {}, "/tmp"),
              "a relative --git-dir resolves against the -C before it")
        check(not hit(["git", "--git-dir=/srv/other/.git", "x"], {"GIT_DIR": "/srv/clone2/.git"}, "/tmp"),
              "another repo (even one sharing a name prefix) is not ours")
        I.rimflow, I.recorded_run, I.shard_path = saved[0], saved[1], saved[2]
        names = {I.finding_name("Mock", r, "job_abcdef") for r in ("foo-bar", "foo_bar", "x" * 50 + "1", "x" * 50 + "2")}
        check(len(names) == 4, "two rows of one job never share a finding name: %s" % sorted(names))
        check(I.finding_name("Mock", "r2", "job_abcdef") == "MOCK_R2_FAILS_ABCDEF", "a plain row keeps its old name")
        names = {I.finding_name("Mock", "x" * 50 + r, "job_abcdef") for r in ("270", "554")}
        check(len(names) == 2, "rows whose 4-hex suffixes collide get distinct names: %s" % sorted(names))
        open(os.path.join(tmp, "own.jsonl"), "w").write(json.dumps(
            {"event": "finding", "name": "MOCK_R2_FAILS_ABCDEF", "from": "OTHER_ITEM/run-1@x"}) + "\n")
        I.shard_path = lambda: os.path.join(tmp, "own.jsonl")
        check(not I.filed("MOCK_R2_FAILS_ABCDEF", "SOME_ITEM/run-1@x") and
              I.filed("MOCK_R2_FAILS_ABCDEF", "OTHER_ITEM/run-1@x"),
              "a finding of the same name from another item's run does not pass for this run's")
        I.shard_path = saved[2]
        order = []
        os.makedirs(os.path.join(tmp, "q", "done"))
        S.dump(done_rec(ITEM), os.path.join(tmp, "q", "done", "x.json"))
        repo = os.path.join(tmp, "repo")
        subprocess.run(["git", "init", "-q", repo], check=True, timeout=60)
        os.makedirs(os.path.join(repo, ".git", "rebase-merge"))
        I.REPO, I.T.QHOME = repo, os.path.join(tmp, "q")
        I.clear_leftovers = lambda git, *a, **k: order.append("clear") or "publish stopped: leftover rebase stuck"
        I.ingest_one = lambda rec: order.append("ingest") or {"skipped": "t"}
        I.publish, I.unpublished = (lambda n, *a, **k: order.append("publish") or "pushed"), (lambda *a: False)
        os.environ["TESTQ_INGEST_PUSH"] = "1"
        I.main()
        check(order[:1] == ["clear"] and "ingest" not in order,
              "a leftover rebase is cleared before ingesting, and while it stays nothing is ingested: %s" % order)
        import fcntl
        order.clear()
        shutil.rmtree(os.path.join(repo, ".git", "rebase-merge"))
        S.dump(done_rec(ITEM), os.path.join(tmp, "q", "done", "x.json"))   # review r8: a held clone lock (second queue / Dispatcher) stops ingest
        I.REPO = os.path.join(tmp, "repo")
        os.environ["TESTQ_INGEST_PUSH"] = "0"
        with open(I.repo_lock_path(), "w") as other:
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
            I.main()
            check("ingest" not in order, "ingest skips while another caller holds this clone's lock: %s" % order)
        os.environ["TESTQ_INGEST_PUSH"] = "0"
        I.main()
        check("ingest" in order, "setup: without the lock held, the same ingest runs: %s" % order)
        order.clear()
        os.makedirs(os.path.join(repo, ".git", "rebase-merge"), exist_ok=True)
        order.clear()
        os.environ["TESTQ_INGEST_PUSH"] = "0"      # review r5: publication off must not ingest into a rebase tree either
        I.main()
        check("ingest" not in order and "clear" not in order,
              "with publication off a rebase in progress still stops ingestion (and nothing is cleared): %s" % order)
    finally:
        (I.rimflow, I.recorded_run, I.shard_path, I.CLI, I.clear_leftovers, I.ingest_one, I.T.QHOME, I.publish,
         I.unpublished, I.REPO) = saved[:10]
        if saved[10] is None:
            os.environ.pop("TESTQ_INGEST_PUSH", None)
        else:
            os.environ["TESTQ_INGEST_PUSH"] = saved[10]
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    crash_checks()
    review_r1_checks()
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
        r = subprocess.run([sys.executable, CLI, "file", LANE, "--for", "BENCH", "--title", "t", "--seat", "BENCH"],
                           env=env, capture_output=True, text=True, timeout=120)
        check(r.returncode == 0, "the lane host item is filed in the temp ledger: %s" % r.stderr[-200:])
        for it in (MANY_A, MANY_B):
            subprocess.run([sys.executable, CLI, "file", it, "--for", "BENCH", "--title", "t", "--seat", "BENCH"],
                           env=env, capture_output=True, text=True, timeout=120)
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
                "unknown": done_rec("NO_SUCH_ITEM_HERE"), "late": done_rec(LATE),
                "canary": done_rec(None, "INVALID", "CANARY"),
                # TESTQ_INGEST_FIX_ONE_ITEM_MANY_ROWS: one sheet, two items; ITEM's own row PASSes, MANY's rows FAIL
                "many": done_rec(None, rows=(("m1", "PASS"), ("m2", "FAIL"), ("m3", "PASS")),
                                 row_items={"m1": MANY_A, "m2": MANY_B, "m3": MANY_B})}
        for k, rec in recs.items():
            S.dump(rec, os.path.join(queue, "done", rec["job"]["id"] + ".json"))
        r = ingest()
        check(r.returncode == 0, "ingest runs: %s" % r.stderr[-300:])
        evs = events()
        mv = {e["id"]: e["result"] for e in evs if e["event"] == "verify" and e.get("id") in (MANY_A, MANY_B)}
        check(mv == {MANY_A: "pass", MANY_B: "fail"},
              "one sheet, two items: each verdict comes from that item's own rows only: %s" % mv)
        mf = [e for e in evs if e["event"] == "finding" and e["from"].startswith(MANY_B + "/run-")]
        check(len(mf) == 1 and not [e for e in evs if e["event"] == "finding" and e["from"].startswith(MANY_A)],
              "the FAIL row's finding hangs off its own item's run")
        verifies = [e for e in evs if e["event"] == "verify" and e.get("id") not in (LANE, MANY_A, MANY_B)]
        check(sorted(e["result"] for e in verifies) == ["fail", "partial", "pass"],
              "one verify per DONE job, results fail/pass/partial: %s" % [e["result"] for e in verifies])
        check(all(e["seat"] == "RUNNER" and e["config"] == "steve-targeted" and e["sha"] == "def5678" and
                  "Mock_1.html" in e["evidence"] for e in verifies), "verifies carry seat, config, sha and the sheet")
        fnd = [e for e in evs if e["event"] == "finding" and e.get("id") != LANE and not e["from"].startswith("MANY_ROWS")]
        check(len(fnd) == 2 and all(e["from"].startswith(ITEM + "/run-") and e["type"] == "UNTRIAGED" for e in fnd),
              "one finding per FAIL row, from its run: %s" % [e["name"] for e in fnd])
        notes = [e for e in evs if e["event"] == "note"]
        check(len(notes) == 1 and "INVALID/HANG" in notes[0]["text"], "a non-DONE run is a note, not a verify")
        def rec_of(k):
            return json.load(open(os.path.join(queue, "done", recs[k]["job"]["id"] + ".json")))

        cid = "STEVE_LANE_CANARY_RED_" + recs["canary"]["job"]["id"][-6:].upper()
        lv = [e for e in evs if e["event"] == "verify" and e.get("id") == LANE]
        lf = [e for e in evs if e["event"] == "finding" and e.get("name") == cid]
        check(len(lv) == 1 and lv[0]["result"] == "fail" and lv[0]["config"] == "steve-lane" and len(lf) == 1
              and "paused" in lf[0].get("why", ""),
              "a red canary records one failed lane run on %s and one finding naming the pause, with no job item: %s"
              % (LANE, rec_of("canary").get("ingested")))

        check("skipped" in rec_of("noitem")["ingested"], "no item -> skipped")
        check(all("ingested" not in rec_of(k) and rec_of(k)["ingest_pending"]["tries"] == 1 for k in ("unknown", "late")),
              "an unknown item -> pending a retry, not marked: %s" % rec_of("unknown").get("ingest_pending"))
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
        r = subprocess.run([sys.executable, CLI, "file", LATE, "--for", "BENCH", "--title", "t", "--seat", "BENCH"],
                           env=env, capture_output=True, text=True, timeout=120)
        check(r.returncode == 0, "the late item is filed: %s" % r.stderr[-200:])
        r = subprocess.run([sys.executable, os.path.join(HERE, "ingest.py")], env=dict(env, TESTQ_INGEST_RETRY_S="0"),
                           capture_output=True, text=True, timeout=300)
        late = [e for e in events() if e.get("id") == LATE]
        check(rec_of("late").get("ingested", {}).get("result") == "fail" and len(late) == 3,
              "an item filed late is verified on the retry, with its findings: %d events, %s %s"
              % (len(late), rec_of("late").get("ingest_pending"), r.stderr[-300:]))
        check(rec_of("unknown")["ingest_pending"]["tries"] == 2, "a never-filed item counts its tries")
        subprocess.run([sys.executable, os.path.join(HERE, "ingest.py")],
                       env=dict(env, TESTQ_INGEST_RETRY_S="0", TESTQ_INGEST_MAX_TRIES="3"),
                       capture_output=True, text=True, timeout=300)
        u = rec_of("unknown")
        check("error" in u.get("ingested", {}) and "ingest_pending" not in u, "the last try marks it with the error")
        # a standing host (TESTQ_HOST_ITEM) hosts only item-less jobs: a job that names its own item is not noted there
        hr = done_rec(ITEM, "INVALID", "HANG")
        S.dump(hr, os.path.join(queue, "done", hr["job"]["id"] + ".json"))
        subprocess.run([sys.executable, os.path.join(HERE, "ingest.py")], env=dict(env, TESTQ_HOST_ITEM=MANY_A),
                       capture_output=True, text=True, timeout=300)
        hn = [e for e in events() if e["event"] == "note" and hr["result"]["attempt"] in e.get("text", "")]
        check([e["id"] for e in hn] == [ITEM], "a non-DONE job with an item notes that item only, not the host: %s"
              % [e["id"] for e in hn])
        # a non-DONE job whose item is not on the ledger yet: the refused note is retried, not lost, and written once
        nl = done_rec(NOTE_LATE, "INVALID", "HANG")
        nlp = os.path.join(queue, "done", nl["job"]["id"] + ".json")
        S.dump(nl, nlp)
        ingest()
        check("ingested" not in json.load(open(nlp)) and json.load(open(nlp))["ingest_pending"]["tries"] == 1,
              "a non-DONE note refused for an unfiled item is pending a retry, not marked: %s"
              % json.load(open(nlp)).get("ingested"))
        subprocess.run([sys.executable, CLI, "file", NOTE_LATE, "--for", "BENCH", "--title", "t", "--seat", "BENCH"],
                       env=env, capture_output=True, text=True, timeout=120)
        for _ in range(2):
            subprocess.run([sys.executable, os.path.join(HERE, "ingest.py")], env=dict(env, TESTQ_INGEST_RETRY_S="0"),
                           capture_output=True, text=True, timeout=300)
            p2 = json.load(open(nlp))
            p2.pop("ingested", None)
            S.dump(p2, nlp)                     # unmark: a re-run must not note twice
        nn = [e for e in events() if e["event"] == "note" and e.get("id") == NOTE_LATE]
        check(len(nn) == 1, "the retried note lands once on the late item: %d notes" % len(nn))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    publish_checks()
    leftover_checks()
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
