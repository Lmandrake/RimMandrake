#!/usr/bin/env python3
"""selftest_relentless_finish_ledger_only.py — `relentless.py finish` refuses a commit the blind checker cannot see
(OPS_CHURN_DIAGNOSE_STALE_EDEN_EOCX).

The churn: STALE_BLOCKS_UNBLOCK_GATES_ALREADY_OPEN blind-failed twice on a8d05bca, a commit that changed only the
ledger shard. relentless_wall.make_box leaves walls.marker.tree_from_parent (the ledger, code_review) out of change.diff
and replays it from the candidate's PARENT, so the checker read an empty diff and the ledger as before the events.

1. a commit touching only tree_from_parent paths is refused, naming what is hidden;
2. the same events plus a file outside them (a lesson) is accepted;
3. a code-only commit is accepted; a root commit that is ledger-only is refused;
4. the live rules profile still replays the ledger from the parent (else this guard guards nothing);
5. main(["finish", ...]) on a ledger-only sha returns 2 and never reaches finish();
6. a MIXED commit (code + ledger events) is refused when the contract proof reads the ledger
   (OPS_CHURN_DIAGNOSE_LAPSED_VYPN_VNGX: LAPSED_LEASES_REPAIR_GHOSTS_HOLD_THE_KEYS blind-failed twice on 49ac7ca0,
   code plus 11 repair events, under `relentless_pool_why.py --leases`), and so is code + code_review under
   code_review_status; the same mixed commit under a proof reading neither is accepted; main reads the proof from the
   item's contract.

Temp git repos and a temp RELENTLESS_ROOT only; no ledger, store, clone or unit is touched.

    python3 src/RimMandrake/rimflow/selftest_relentless_finish_ledger_only.py
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import relentless as R    # noqa: E402

FAILS = []
PROF = {"tree_exclude": ["conversations"], "tree_from_parent": ["infrastructure/state/ledger", "infrastructure/state/code_review"]}


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True, check=True).stdout.strip()


def commit(repo, files, msg):
    for rel, text in files.items():
        p = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(text)
        git(repo, "add", "--", rel)
    git(repo, "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


def main():
    shard = "infrastructure/state/ledger/events/BENCH.jsonl"
    with tempfile.TemporaryDirectory() as root_repo:
        git(root_repo, "init", "-q", "-b", "main")
        root = commit(root_repo, {shard: "{}\n"}, "root ledger-only")
        ok(R.ledger_only_refusal(root, PROF, cwd=root_repo) is not None, "3b. a ledger-only ROOT commit is refused")

    with tempfile.TemporaryDirectory() as repo:
        git(repo, "init", "-q", "-b", "main")
        commit(repo, {"src/a.py": "x = 1\n"}, "base")
        led = commit(repo, {shard: '{"ev": "unblock"}\n'}, "ITEM: unblock (ledger only)")
        why = R.ledger_only_refusal(led, PROF, cwd=repo)
        ok(why is not None and "infrastructure/state/ledger" in why and "PARENT" in why,
           "1. a ledger-only commit is refused, naming the hidden path: %r" % (why or "")[:90])
        both = commit(repo, {"infrastructure/state/code_review/x.jsonl": "{}\n"}, "ITEM: review only")
        ok(R.ledger_only_refusal(both, PROF, cwd=repo) is not None, "1b. a code_review-only commit is refused too")
        mixed = commit(repo, {shard: '{"ev": "block"}\n', "infrastructure/state/lessons/l.md": "lesson\n"}, "ITEM: events + lesson")
        ok(R.ledger_only_refusal(mixed, PROF, cwd=repo) is None, "2. events plus a lesson outside the snapshot are accepted")
        code = commit(repo, {"src/a.py": "y = 2\n"}, "ITEM: code")
        ok(R.ledger_only_refusal(code, PROF, cwd=repo) is None, "3. a code-only commit is accepted")
        near = commit(repo, {"infrastructure/state/ledgerish.txt": "z\n"}, "ITEM: prefix lookalike")
        ok(R.ledger_only_refusal(near, PROF, cwd=repo) is None, "3c. a path merely PREFIXED like the ledger is not hidden")
        ok(R.ledger_only_refusal(led, {"tree_from_parent": []}, cwd=repo) is None, "3d. no tree_from_parent: nothing refused")
        ok(R.ledger_only_refusal("0" * 40, PROF, cwd=repo) is None, "3e. a git error refuses nothing")

        live = R.rules().get("walls", {}).get("marker", {})
        ok("infrastructure/state/ledger" in (live.get("tree_from_parent") or ()),
           "4. the live Marker profile replays the ledger from the parent")

        called = []
        saved = (R.finish, R.canonical_commit, R.rules)
        R.finish = lambda *a, **k: called.append(a)
        R.canonical_commit = lambda name: name
        R.rules = lambda path=None: {"walls": {"marker": PROF}}
        cwd = os.getcwd()
        err = io.StringIO()
        try:
            os.chdir(repo)
            with contextlib.redirect_stderr(err):
                rc = R.main(["finish", "--item", "X_Y_Z", "--gen", "1", "--sha", led, "--evidence", "e"])
            with contextlib.redirect_stderr(io.StringIO()):
                rc_ok = R.main(["finish", "--item", "X_Y_Z", "--gen", "1", "--sha", mixed, "--evidence", "e"])
        finally:
            os.chdir(cwd)
            R.finish, R.canonical_commit, R.rules = saved
        ok(rc == 2 and "PARENT" in err.getvalue() and len(called) == 1 and called[0][3] == mixed,
           "5. main finish refuses the ledger-only sha (rc=%s) and passes the mixed one (calls=%d)" % (rc, len(called)))

    with tempfile.TemporaryDirectory() as repo:
        git(repo, "init", "-q", "-b", "main")
        commit(repo, {"src/a.py": "x = 1\n"}, "base")
        lapsed = commit(repo, {shard: '{"ev": "release"}\n', "src/rimflow/relentless_pool_why.py": "y = 2\n"},
                        "ITEM: code + repair events")
        leases = ("python3 src/RimMandrake/Utils/run_selftests.py --only selftest_relentless_pool_why.py && "
                  "python3 src/RimMandrake/rimflow/relentless_pool_why.py --leases")
        why = R.ledger_only_refusal(lapsed, PROF, cwd=repo, proof=leases)
        ok(why is not None and "infrastructure/state/ledger" in why and "PARENT" in why and "code_review" not in why,
           "6. the LAPSED_LEASES instance: code + ledger events under a --leases proof is refused: %r" % (why or "")[:90])
        ok(R.ledger_only_refusal(lapsed, PROF, cwd=repo, proof="python3 src/RimMandrake/rimflow/cli.py show X") is not None,
           "6b. a rimflow cli.py proof reads the ledger too")
        ok(R.ledger_only_refusal(lapsed, PROF, cwd=repo,
                                 proof="python3 src/RimMandrake/Utils/run_selftests.py --only selftest_relentless.py") is None,
           "6c. the same mixed commit under a proof that reads no ledger is accepted")
        ok(R.ledger_only_refusal(lapsed, PROF, cwd=repo) is None, "6d. no proof given: a mixed commit is accepted as before")
        ok(R.ledger_only_refusal(lapsed, PROF, cwd=repo, proof="python3 src/RimMandrake/rimflow/selftest_ledger_lint.py") is None,
           "6e. 'ledger' inside a script name is not a ledger read")
        rev = commit(repo, {"infrastructure/state/code_review/x.jsonl": "{}\n", "src/b.py": "z = 3\n"}, "ITEM: code + review")
        why = R.ledger_only_refusal(rev, PROF, cwd=repo, proof="python3 src/RimMandrake/Utils/code_review_status.py check src/b.py")
        ok(why is not None and "code_review" in why and "state/ledger" not in why,
           "6f. code + code_review under a code_review_status proof is refused: %r" % (why or "")[:90])
        ok(R.ledger_only_refusal(rev, PROF, cwd=repo, proof=leases) is None,
           "6g. a ledger-reading proof on a commit writing only code_review (plus code) is accepted")

        called = []
        saved = (R.finish, R.canonical_commit, R.rules, R.Store.load)
        R.finish = lambda *a, **k: called.append(a)
        R.canonical_commit = lambda name: name
        R.rules = lambda path=None: {"walls": {"marker": PROF}}
        R.Store.load = lambda self, item: {"contract": {"proof": leases}}
        cwd = os.getcwd()
        err = io.StringIO()
        try:
            os.chdir(repo)
            with contextlib.redirect_stderr(err):
                rc = R.main(["finish", "--item", "X_Y_Z", "--gen", "1", "--sha", lapsed, "--evidence", "e"])
        finally:
            os.chdir(cwd)
            R.finish, R.canonical_commit, R.rules, R.Store.load = saved
        ok(rc == 2 and "PARENT" in err.getvalue() and not called,
           "6h. main finish reads the contract proof and refuses the mixed ledger commit (rc=%s calls=%d)" % (rc, len(called)))

    print("FAILED: %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as fake_root:     # main() builds a Store: never the real one (a walled box cannot write it)
        os.environ["RELENTLESS_ROOT"] = fake_root
        sys.exit(main())
