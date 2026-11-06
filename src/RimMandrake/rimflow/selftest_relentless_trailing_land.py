#!/usr/bin/env python3
"""GAMELANE_LAND_FIX_SEVEN_STRANDINGS: a worker's commits must land before its item leaves its hands.

Once `finish` moves an item on (candidate, then the game lane, held or blocked), the pre-push fence refused every push
from the old lease, so a commit left in the clone waited in a bundle that only the item's NEXT clone restores; an item
that went done never got one (outages 6 and 7 of the pool breach: PIT_LIP, HORIZON_CARAVAN, MASS_VALIDATION).
Real git repos in a temp dir, the real Store, finish and hook_fence:
  (a) finish refuses while the clone holds a commit origin/main does not; a landed (or rebased-and-landed) one passes
  (b) after finish, the same generation may push a commit that touches only lessons or ledger shards
  (c) a code commit after finish is still refused, and so is any push from a superseded generation
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402

FAILS = []
ITEM = "TRAILING_LAND_TEST_ITEM"


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *a], cwd=cwd,
                          check=True, capture_output=True, text=True).stdout.strip()


def commit(cwd, path, text, msg):
    full = os.path.join(cwd, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)
    git(cwd, "add", path)
    git(cwd, "commit", "-q", "-m", msg)
    return git(cwd, "rev-parse", "HEAD")


def setup(base):
    origin, clone = os.path.join(base, "origin.git"), os.path.join(base, "clone")
    git(base, "init", "-q", "--bare", "-b", "main", origin)
    git(base, "clone", "-q", origin, clone)
    commit(clone, "src/a.py", "a\n", "base")
    git(clone, "push", "-q", "origin", "HEAD:main")
    with open(os.path.join(clone, ".git", "relentless.json"), "w") as f:
        json.dump({"item": ITEM, "gen": 2}, f)
    store = R.Store(os.path.join(base, "store"))
    st = R.new_state(ITEM, 0, "test")
    st.update(status="running", gen=2, contract={"proof": "true"})
    store.save(st)
    return clone, store


def set_status(store, status, gen=2):
    st = store.load(ITEM)
    st.update(status=status, gen=gen)
    store.save(st)


def finish_refusal(store, clone, sha):
    try:
        R.finish(store, ITEM, 2, sha, "evidence", root=clone)
    except ValueError as e:
        return str(e)
    except R.Fenced as e:
        return "fenced: %s" % e
    return None


def main():
    base = tempfile.mkdtemp(prefix="trailing_land_")
    old_gen = os.environ.pop("RELENTLESS_GEN", None)
    try:
        clone, store = setup(base)
        fix = commit(clone, "src/a.py", "fixed\n", "the fix")
        git(clone, "push", "-q", "origin", "HEAD:main")
        trailing = commit(clone, "infrastructure/state/lessons/L_one.md", "lesson\n", "lesson after landing")
        why = finish_refusal(store, clone, fix)
        ok(why and "origin/main does not" in why and trailing[:10] in why,
           "(a) finish refuses while the clone holds an unlanded commit: %s" % (why or "")[:140])
        git(clone, "push", "-q", "origin", "HEAD:main")
        why = finish_refusal(store, clone, fix)
        ok(why is None or "origin/main does not" not in why, "(a) once it is landed finish is not refused for it: %s" % why)

        # a landing that rebased: origin holds the same patch under another hash
        local = commit(clone, "infrastructure/state/lessons/L_two.md", "two\n", "lesson two")
        git(clone, "reset", "-q", "--hard", "HEAD~1")
        git(clone, "branch", "carry", local)
        other = os.path.join(base, "other")
        git(base, "clone", "-q", os.path.join(base, "origin.git"), other)
        commit(other, "README", "r\n", "someone else lands first")
        git(other, "fetch", "-q", clone, "carry")
        git(other, "cherry-pick", local)
        git(other, "push", "-q", "origin", "HEAD:main")
        git(clone, "branch", "-q", "-D", "carry")
        git(clone, "cherry-pick", local)            # this clone still has the pre-rebase hash
        git(clone, "fetch", "-q", "origin")
        ok(R.unlanded(clone) == [], "(a) a commit origin holds under a new hash counts as landed: %s" % R.unlanded(clone))
        git(clone, "reset", "-q", "--hard", "origin/main")

        # the lane move: finish is taken, the item is a candidate; then the game lane, held, done
        set_status(store, "candidate")
        ok(R.hook_fence(clone, store) is None, "nothing unpushed: the fence says nothing it must refuse")
        commit(clone, "infrastructure/state/lessons/L_three.md", "three\n", "lesson after finish")
        commit(clone, "infrastructure/state/ledger/events/BENCH.jsonl", "{}\n", "ledger line after finish")
        for status in ("candidate", R.relentless_game.GAME, "held", "blocked", "done"):
            set_status(store, status)
            why = R.hook_fence(clone, store)
            ok(why is None, "(b) %s: the finished generation may push lessons and ledger lines: %s" % (status, why))
        ok(R.fence_check(store, ITEM, 2), "(b) the plain lease check still says the lease is gone")

        set_status(store, "candidate", gen=3)
        why = R.hook_fence(clone, store)
        ok(why and "gone" in why, "(c) a superseded generation pushes nothing, not even records: %s" % why)

        set_status(store, "candidate", gen=2)
        commit(clone, "src/a.py", "late code\n", "code after finish")
        why = R.hook_fence(clone, store)
        ok(why and "gone" in why, "(c) a code commit after finish is refused: %s" % why)
        git(clone, "reset", "-q", "--hard", "HEAD~1")
        commit(clone, "infrastructure/state/lessons/L_four.md", "four\n", "mixed")
        commit(clone, "src/b.py", "b\n", "code beside the record")
        ok(R.hook_fence(clone, store), "(c) one code commit among records refuses the whole push")
        git(clone, "reset", "-q", "--hard", "HEAD~2")
        ok(R.hook_fence(clone, store) is None, "and back to records only, it passes again")
    finally:
        if old_gen is not None:
            os.environ["RELENTLESS_GEN"] = old_gen
        shutil.rmtree(base, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
