#!/usr/bin/env python3
"""selftest_lock_commit_is_landed: the promises of design/specs/2026-11-27-lock-commit-is-landed/boundary.md, one test
per promise, each named as the promise is. The failure, 2026-11-27 4:16 AM PST: the tick locked Wrecked Machines 0.1.0
and wrote `locked_from_commit` b53e34d705, the HEAD of the dispatch clone. That HEAD was a ledger commit that never
reached origin/main under that sha, so `maturation.py lock-bars` in the steward's clone refused with "tree.json at
b53e34d705... cannot be read" and the mod stood at the Designer.

Each test builds its own git repos in a temp folder (a bare origin and one clone). No network, no game, no real landing.

    python3 src/RimMandrake/rimflow/selftest_lock_commit_is_landed.py      # "selftest_lock_commit_is_landed: PASS"
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="lock_commit_landed_")
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "_state")
os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
import maturation as M  # noqa: E402
import maturation_autonomy as AUT  # noqa: E402

FAILS = []
MOD = "LMod"
NOW = 1795781760.0
TREE = {"leaves": [{"id": "bar_one"}, {"id": "bar_two"}]}


def check(ok, name, got=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def git(root, *a):
    p = subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                        "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false"] + list(a),
                       capture_output=True, text=True, timeout=1800)  # budget: class=call
    if p.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), p.stderr.strip()))
    return p.stdout.strip()


def put(root, relpath, text):
    p = os.path.join(root, relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def clone_with_landed_concept(name):
    """A bare origin and a clone whose concept files are landed on origin/main. -> (root, the landed sha)."""
    origin, root = os.path.join(TMP, name + ".git"), os.path.join(TMP, name)
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True, timeout=1800)  # budget: class=call
    subprocess.run(["git", "clone", "-q", origin, root], check=True, capture_output=True,
                   timeout=1800)  # budget: class=call
    git(root, "checkout", "-q", "-B", "main")
    put(root, M.rel(MOD, "tree.json"), json.dumps(TREE))
    put(root, M.rel(MOD, "stage.json"), json.dumps({"status": "locked", "budget": {"spent": 5}}))
    put(root, M.rel(MOD, "sheet.md"), "# the sheet\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "the concept, landed")
    git(root, "push", "-q", "origin", "main")
    return root, git(root, "rev-parse", "HEAD")


def unlanded_commit(root, relpath, text, subject):
    put(root, relpath, text)
    git(root, "add", "--", relpath)
    git(root, "commit", "-q", "-m", subject)
    return git(root, "rev-parse", "HEAD")


def lock(root):
    """Run the pipeline's lock with a fake landing. -> (VERSION.json or None, the paths handed to the landing, error)."""
    landed = []
    try:
        AUT.autolock_and_land(root, MOD, now=NOW, land=lambda subj, paths: landed.append(paths) or "PUBLISHED x")
        err = None
    except Exception as e:  # noqa: BLE001
        err = e
    v, _ = M.read_json(root, MOD, "version/VERSION.json")
    return v, landed, err


def t_the_pipeline_lock_names_a_commit_on_origin_main():
    # the failure of 2026-11-27: HEAD is a local ledger commit that origin/main does not hold
    root, landed_sha = clone_with_landed_concept("ledger_ahead")
    head = unlanded_commit(root, "infrastructure/state/ledger/events/DISPATCHER.jsonl", "{}\n",
                           "ledger: DISPATCHER notes (2)")
    v, landed, err = lock(root)
    c = (v or {}).get("locked_from_commit")
    check(err is None and landed, "an unlanded ledger commit at HEAD does not stop the lock", (err, landed))
    check(c == landed_sha and c != head, "an unlanded ledger commit at HEAD: the lock names the landed commit under it",
          (c, landed_sha, head))
    fresh = os.path.join(TMP, "ledger_ahead_fresh")       # the steward's clone: it holds origin/main only
    subprocess.run(["git", "clone", "-q", os.path.join(TMP, "ledger_ahead.git"), fresh], check=True,
                   capture_output=True, timeout=1800)  # budget: class=call
    shutil.copytree(os.path.join(M.mod_dir(root, MOD), "version"), os.path.join(M.mod_dir(fresh, MOD), "version"))
    r = M.lock_bars(fresh, MOD, "BENCH", "the steward records the bars")
    check(r.get("ok") and r.get("ids") == ["bar_one", "bar_two"],
          "a fresh clone of origin/main records the bars of that lock", r)
    # HEAD on origin/main: the lock names HEAD, as before
    root2, landed2 = clone_with_landed_concept("level")
    v2, _, err2 = lock(root2)
    check(err2 is None and (v2 or {}).get("locked_from_commit") == landed2, "a HEAD on origin/main is the lock commit",
          (err2, (v2 or {}).get("locked_from_commit"), landed2))


def t_a_lock_over_unlanded_locked_files_is_refused():
    root, _ = clone_with_landed_concept("tree_ahead")
    unlanded_commit(root, M.rel(MOD, "tree.json"), json.dumps({"leaves": [{"id": "bar_other"}]}),
                    "a tree that never landed")
    v, landed, err = lock(root)
    check(err is not None and not landed, "an unlanded change of a locked file refuses the lock and lands nothing",
          (err, landed))
    check("tree.json" in str(err) and "land" in str(err).lower(),
          "the refusal names the locked file and the act that clears it (land it)", str(err))
    check(not (isinstance(v, dict) and str(v.get("state") or "").startswith("locked")),
          "the refused lock leaves no locked VERSION.json", v)
    # each locked file, not tree.json alone: record.json's inventory also feeds the bars that lock_bars derives
    missed = []
    for f in M.LOCK_PINNED:
        if f == "tree.json":
            continue
        r_f, _ = clone_with_landed_concept("ahead_" + f.replace(".", "_"))
        unlanded_commit(r_f, M.rel(MOD, f), "{}\n", "an unlanded %s" % f)
        v_f, landed_f, err_f = lock(r_f)
        if err_f is None or landed_f or f not in str(err_f):
            missed.append(f)
    check(not missed, "an unlanded change of each other locked file refuses the lock and names that file", missed)


def t_lock_bars_says_when_the_lock_commit_is_not_in_the_clone():
    root, landed_sha = clone_with_landed_concept("reader")
    gone = "b53e34d70527cdd6ab1d8c37c74716851708ddc1"
    put(root, M.rel(MOD, "version/VERSION.json"),
        json.dumps({"mod": MOD, "version": "0.1.0", "state": "locked", "locked_from_commit": gone}))
    r = M.lock_bars(root, MOD, "BENCH", "w")
    why = str(r.get("why"))
    check(not r.get("ok") and gone in why and "is not a commit in this clone" in why
          and "locked_from_commit" in why and "origin/main" in why,
          "a lock commit that the clone lacks: the refusal says so and names the repair", r)
    check(not os.path.exists(os.path.join(M.mod_dir(root, MOD), M.LOCKED_BARS)),
          "a lock commit that the clone lacks: no locked_bars.json is written", r)
    # another cause, another answer: the commit is there, its tree.json is not
    empty = git(root, "commit-tree", "-m", "empty", git(root, "hash-object", "-t", "tree", "/dev/null"))
    put(root, M.rel(MOD, "version/VERSION.json"),
        json.dumps({"mod": MOD, "version": "0.1.0", "state": "locked", "locked_from_commit": empty}))
    r2 = M.lock_bars(root, MOD, "BENCH", "w")
    check(not r2.get("ok") and "is not a commit in this clone" not in str(r2.get("why"))
          and "tree.json at %s cannot be read" % empty in str(r2.get("why")),
          "a lock commit that is there with no tree.json keeps its own refusal", r2)
    del landed_sha


def main():
    try:
        for t in (t_the_pipeline_lock_names_a_commit_on_origin_main, t_a_lock_over_unlanded_locked_files_is_refused,
                  t_lock_bars_says_when_the_lock_commit_is_not_in_the_clone):
            try:
                t()
            except Exception as e:  # noqa: BLE001  a crash is a FAIL of that test, the others still run
                import traceback
                check(False, "%s raised" % t.__name__, "%s: %s %s" % (type(e).__name__, e,
                                                                      traceback.format_exc()[-600:]))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_lock_commit_is_landed: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
