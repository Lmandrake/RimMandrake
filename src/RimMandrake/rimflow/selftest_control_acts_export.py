#!/usr/bin/env python3
"""Selftest of control_acts_export.py, the control store's acts copied to git by rm-control-acts-export.timer (item
RIMMANDRAKE_EXPORT_CONTROL_ACTS_BELT_SPLIT_FROM_SLICE_FOUR; page design/specs/2026-11-19-control-acts-export/boundary.md).
One test per promise, each named for it. Temp stores, a temp bare origin and temp clones only: never the live store,
never GitHub."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []
TMP = tempfile.mkdtemp(prefix="selftest-acts-export-")
os.environ["RM_CONTROL_DB"] = os.path.join(TMP, "unused.db")
os.environ["RM_CONTROL_MODS"] = "Graffiti,Cauldron,Pyrelands"
os.environ["RM_CONTROL_TICK_UNIT"] = ""
import control as C  # noqa: E402
import control_acts_export as X  # noqa: E402


def subject(argv):
    """`--subject <rev>`: test control_acts_export.py as it stood at that git revision (the repeat guard replays the
    instance: `rimflow guard ... --instance "--subject <the fix>^"`). -> the module."""
    if "--subject" not in argv:
        return X
    import importlib.util
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    import time_budget
    rev = argv[argv.index("--subject") + 1]
    repo = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    src = subprocess.run(["git", "-C", repo, "show", "%s:src/RimMandrake/rimflow/control_acts_export.py" % rev],
                         capture_output=True, text=True, timeout=time_budget.CALL_S, check=True).stdout
    path = os.path.join(TMP, "control_acts_export_at_%s.py" % rev.replace("^", "p").replace("~", "t"))
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    spec = importlib.util.spec_from_file_location("control_acts_export", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

PATH = X.PATH
N = [0]


def check(ok, msg, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", msg, "" if ok or got is None else "  (got %r)" % (got,)))
    if not ok:
        FAILS.append(msg)


def git(repo, *a, check_=True):
    r = subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True, timeout=60)
    if check_ and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()))
    return r.stdout.strip()


def world():
    """-> (store, origin, work, peer, reading): a fresh store with two acts, a bare origin with one commit, and two
    clones of it."""
    N[0] += 1
    d = os.path.join(TMP, "w%d" % N[0])
    os.makedirs(d)
    store = os.path.join(d, "c.db")
    C.init(store)
    C.switch("mod:Graffiti", True, "first act", p=store)
    C.switch("mod:Graffiti", False, "second act", p=store)
    origin = os.path.join(d, "origin.git")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
    clones = []
    for name in ("work", "peer"):
        c = os.path.join(d, name)
        subprocess.run(["git", "clone", "-q", origin, c], check=True, capture_output=True)
        git(c, "config", "user.name", "Selftest")
        git(c, "config", "user.email", "selftest@example.invalid")
        clones.append(c)
    with open(os.path.join(clones[0], "README"), "w") as f:
        f.write("x\n")
    git(clones[0], "add", "README")
    git(clones[0], "commit", "-q", "-m", "base")
    git(clones[0], "push", "-q", "origin", "HEAD:main")
    git(clones[1], "pull", "-q", "origin", "main")
    return store, origin, clones[0], clones[1], os.path.join(d, "reading.json")


def published(origin):
    r = subprocess.run(["git", "-C", origin, "show", "main:" + PATH], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def run(store, work, reading, **kw):
    return X.run(repo=work, store=store, reading=reading, **kw)


def peer_commit(peer, name):
    git(peer, "pull", "-q", "--rebase", "origin", "main")
    with open(os.path.join(peer, name), "w") as f:
        f.write(name + "\n")
    git(peer, "add", name)
    git(peer, "commit", "-q", "-m", name)
    git(peer, "push", "-q", "origin", "HEAD:main")


def t_export_holds_every_act():
    store, origin, work, _peer, reading = world()
    code, lines = run(store, work, reading)
    got = published(origin)
    want = [r["id"] for r in C._q("SELECT id FROM acts ORDER BY rev", p=store)]
    ids = [json.loads(x)["id"] for x in (got or "").splitlines()]
    check(code == 0 and lines[-1].startswith("PUBLISHED ") and ids == want and len(want) == 2,
          "a run pushes every act, in revision order, to origin/main and prints PUBLISHED", (code, lines, ids, want))
    C.switch("mod:Cauldron", True, "third act", p=store)
    code, lines = run(store, work, reading)
    ids = [json.loads(x)["id"] for x in (published(origin) or "").splitlines()]
    check(code == 0 and len(ids) == 3, "a new act is pushed by the next run", (code, lines, ids))


def t_unchanged_store_makes_no_commit():
    store, origin, work, _peer, reading = world()
    run(store, work, reading)
    tip = git(origin, "rev-parse", "main")
    code, lines = run(store, work, reading)
    check(code == 0 and git(origin, "rev-parse", "main") == tip and "unchanged" in lines[-1],
          "a run whose file equals origin's pushes nothing and says unchanged", (code, lines))


def t_touches_no_working_tree():
    store, origin, work, _peer, reading = world()
    with open(os.path.join(work, "dirty.txt"), "w") as f:
        f.write("a peer's edit\n")
    with open(os.path.join(work, "README"), "a") as f:
        f.write("staged edit\n")
    git(work, "add", "README")
    os.makedirs(os.path.join(work, os.path.dirname(PATH)), exist_ok=True)
    with open(os.path.join(work, PATH), "w") as f:
        f.write("a hand export left in the tree\n")
    before = (git(work, "rev-parse", "HEAD"), git(work, "status", "--porcelain=v1", "--untracked-files=all"),
              git(work, "ls-files", "-s"))
    base = git(origin, "rev-parse", "main")
    code, lines = run(store, work, reading)
    after = (git(work, "rev-parse", "HEAD"), git(work, "status", "--porcelain=v1", "--untracked-files=all"),
             git(work, "ls-files", "-s"))
    changed = git(origin, "diff-tree", "--no-commit-id", "--name-only", "-r", base, "main").splitlines()
    with open(os.path.join(work, PATH)) as f:
        left = f.read()
    check(code == 0 and before == after and left == "a hand export left in the tree\n",
          "the clone's HEAD, index and working tree are untouched", (code, lines, before, after))
    check(changed == [PATH], "the commit changes the one path only", changed)


def t_never_loses_a_published_act():
    store, origin, work, _peer, reading = world()
    run(store, work, reading)
    kept = published(origin)
    other = os.path.join(os.path.dirname(store), "reset.db")
    C.init(other)
    C.switch("mod:Graffiti", True, "a store set up again", p=other)
    code, lines = run(other, work, reading)
    check(code == 2 and published(origin) == kept and "ct_000001" in lines[-1],
          "a store set up again (an act the published file holds is gone) is refused, exit 2, naming it",
          (code, lines))
    C.switch("mod:Cauldron", True, "a later act", p=store)
    with C.txn(store) as c:
        c.execute("UPDATE acts SET why='rewritten' WHERE id='ct_000001'")
    code, lines = run(store, work, reading)
    check(code == 2 and published(origin) == kept, "a rewritten act line is refused too; origin's file is kept",
          (code, lines))


def t_could_not_look_publishes_nothing():
    store, origin, work, _peer, reading = world()
    tip = git(origin, "rev-parse", "main")
    code, lines = run(os.path.join(TMP, "no-such-dir", "c.db"), work, reading)
    check(code == 3 and git(origin, "rev-parse", "main") == tip and published(origin) is None,
          "a missing store: exit 3 with the cause, nothing pushed", (code, lines))
    bad = os.path.join(os.path.dirname(store), "corrupt.db")
    with open(bad, "wb") as f:
        f.write(b"this is not a sqlite database" * 100)
    code, lines = run(bad, work, reading)
    check(code == 3 and published(origin) is None and lines and "COULD NOT LOOK" in lines[-1],
          "a corrupt store: exit 3, COULD NOT LOOK, never an empty file pushed", (code, lines))


def t_reading_only_on_success():
    store, origin, work, _peer, reading = world()
    code, _ = run(os.path.join(TMP, "absent.db"), work, reading)
    check(code == 3 and not os.path.exists(reading), "a could-not-look run writes no reading", code)
    code, lines = run(store, work, reading)
    with open(reading) as f:
        r1 = json.load(f)
    check(code == 0 and r1.get("verdict") == "published" and r1.get("acts") == 2 and r1.get("sha"),
          "a pushing run writes the reading with its verdict, count and sha", r1)
    t1 = os.path.getmtime(reading)
    time.sleep(0.05)
    code, _ = run(store, work, reading)
    with open(reading) as f:
        r2 = json.load(f)
    check(code == 0 and r2.get("verdict") == "unchanged" and os.path.getmtime(reading) > t1,
          "an unchanged run freshens the reading too", r2)
    t2 = os.path.getmtime(reading)
    other = os.path.join(os.path.dirname(store), "reset2.db")
    C.init(other)
    C.switch("mod:Graffiti", True, "reset", p=other)
    code, _ = run(other, work, reading)
    check(code == 2 and os.path.getmtime(reading) == t2, "a refused run leaves the reading to age", code)
    git(work, "remote", "set-url", "origin", os.path.join(TMP, "no-such-origin.git"))
    code, lines = run(store, work, reading)
    check(code == 4 and os.path.getmtime(reading) == t2, "a run that cannot reach origin: exit 4, reading left",
          (code, lines))


def t_push_race_rebuilds():
    store, origin, work, peer, reading = world()
    moved = []

    def once():
        if not moved:
            moved.append(1)
            peer_commit(peer, "race1")
    code, lines = run(store, work, reading, before_push=once)
    tree = git(origin, "ls-tree", "--name-only", "main")
    check(code == 0 and "race1" in tree.split() and published(origin),
          "a push refused because origin moved is rebuilt on the new tip and lands", (code, lines, tree))
    C.switch("mod:Cauldron", True, "another act", p=store)
    count = []

    def always():
        count.append(1)
        peer_commit(peer, "race%d" % (len(count) + 1))
    code, lines = run(store, work, reading, before_push=always)
    check(code == 4 and len(count) == X.TRIES and "push" in lines[-1],
          "origin moving on every try: %d tries, then exit 4 naming the push" % X.TRIES, (code, len(count), lines))


def t_fetch_race_retries():
    """A peer's fetch in the same clone can win the ref update: git then says "incorrect old value provided" (seen
    in rm-control-acts-export three times on 2026-11-26). That fetch is tried again; any other fetch error is not."""
    store, origin, work, _peer, reading = world()
    real = X._git
    lost = []

    def racing(repo, *args, **kw):
        if args and args[0] == "fetch" and len(lost) < 2:
            lost.append(1)
            raise X.GitFailed("git fetch exited 1: error: fetching ref refs/remotes/origin/main failed: incorrect old "
                              "value provided")
        return real(repo, *args, **kw)
    X._git = racing
    try:
        code, lines = run(store, work, reading)
    finally:
        X._git = real
    check(code == 0 and len(lost) == 2 and published(origin),
          "a fetch that loses the ref update to a peer's fetch is tried again and the run lands", (code, lines))
    other = []

    def broken(repo, *args, **kw):
        if args and args[0] == "fetch":
            other.append(1)
            raise X.GitFailed("git fetch exited 128: fatal: 'origin' does not appear to be a git repository")
        return real(repo, *args, **kw)
    C.switch("mod:Cauldron", True, "another act", p=store)
    X._git = broken
    try:
        code, lines = run(store, work, reading)
    finally:
        X._git = real
    check(code == 4 and len(other) == 1 and "fetch" in lines[-1],
          "any other fetch error is not tried again: exit 4 at once, naming the fetch", (code, len(other), lines))


def main():
    global X
    X = subject(sys.argv)
    for t in (t_export_holds_every_act, t_unchanged_store_makes_no_commit, t_touches_no_working_tree,
              t_never_loses_a_published_act, t_could_not_look_publishes_nothing, t_reading_only_on_success,
              t_push_race_rebuilds, t_fetch_race_retries):
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_control_acts_export")
    return 0


if __name__ == "__main__":
    sys.exit(main())
