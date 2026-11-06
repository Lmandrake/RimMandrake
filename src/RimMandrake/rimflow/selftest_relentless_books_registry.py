#!/usr/bin/env python3
"""BOOKS_REGISTRY_UNSTICK_MOVED_FILE: a proof run in the books clone leaves the modcheck registry (and Transient/, a
validation_triplet_ report) dirty there; when origin moved the same file, `reset --keep` refused and the engine froze on
old code with a journal line that said only "books cannot level". The rows below, the put-back row aside (a guard on
the new set-aside, which the old code never made), are red on the code before the fix:

- origin moving the registry while books holds a run's entries levels the clone, books' entries merged over origin's
  by key (the later `ts` winning a key both changed), books' bytes kept in books_dirt, the carry journalled by path;
- a moved Transient/ or validation_triplet_ file levels too, origin's copy standing and books' kept;
- a level that stops after the set-aside puts every set-aside file back as the run left it;
- a reset git refuses names the file it would not overwrite;
- flush publishes a registry dirty in books, even with no ledger shard to land, but never from books behind origin
  (publish would replay the whole file as text over origin's and could strand the commit)."""
import glob
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
import relentless_books_left as L  # noqa: E402

FAILS = []
REG = L.REGISTRY
TRANS = "Transient/n.json"
TRIP = "src/RimMandrake/GimmeSomeSlack/northstar/validation_triplet_x.json"


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def g(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True,
                          text=True, check=True, stdin=subprocess.DEVNULL).stdout


def put(root, p, text):
    os.makedirs(os.path.dirname(os.path.join(root, p)) or root, exist_ok=True)
    with open(os.path.join(root, p), "w") as f:
        f.write(text)


def read(root, p):
    with open(os.path.join(root, p)) as f:
        return f.read()


def reg(d):
    return json.dumps(d, indent=2, sort_keys=True) + "\n"


class Fix:
    def __init__(self):
        self.d = tempfile.mkdtemp(prefix="rlbreg-")
        self.origin, self.up, self.books = (os.path.join(self.d, n) for n in ("o.git", "up", "books"))
        g(self.d, "init", "-q", "--bare", "-b", "main", self.origin)
        g(self.d, "clone", "-q", self.origin, self.up)
        g(self.up, "checkout", "-q", "-B", "main")
        self.base = {"A": {"status": "GREEN", "ts": 100}, "B": {"status": "RED", "ts": 100},
                     "C": {"status": "RED", "ts": 100}, "D": {"status": "GREEN", "ts": 100}}
        put(self.up, REG, reg(self.base))
        for p in (TRANS, TRIP, "code.py"):
            put(self.up, p, "one\n")
        g(self.up, "add", "--", REG, TRANS, TRIP, "code.py")
        g(self.up, "commit", "-qm", "one")
        g(self.up, "push", "-q", "origin", "main")
        g(self.d, "clone", "-q", self.origin, self.books)
        self.fx = R.Effects.__new__(R.Effects)
        self.fx.books, self.fx.store = self.books, R.Store(os.path.join(self.d, "store"))
        os.makedirs(self.fx.store.dir, exist_ok=True)

    def advance(self, files):
        for p, text in files.items():
            put(self.up, p, text)
        g(self.up, "add", "--", *files)
        g(self.up, "commit", "-qm", "move")
        g(self.up, "push", "-q", "origin", "main")
        g(self.books, "fetch", "-q", "origin")

    def journal(self):
        p = self.fx.store.p("journal.jsonl")
        if not os.path.isfile(p):
            return []
        with open(p) as f:
            return [json.loads(x) for x in f if x.strip()]

    def kept(self, p):
        got = glob.glob(os.path.join(self.fx.store.p("books_dirt"), "*", p))
        return read(os.path.dirname(got[0]), os.path.basename(p)) if got else None

    def behind(self):
        return g(self.books, "rev-list", "--count", "HEAD..origin/main").strip()

    def done(self):
        shutil.rmtree(self.d, ignore_errors=True)


def t_moved_registry_merges():
    fx = Fix()
    mine = dict(fx.base, A={"status": "RED", "ts": 300}, C={"status": "GREEN", "ts": 50}, NEW={"status": "GREEN", "ts": 300})
    del mine["D"]           # books' run forgot a key (forget_key)
    put(fx.books, REG, reg(mine))
    theirs = dict(fx.base, B={"status": "GREEN", "ts": 200}, C={"status": "RED", "ts": 200}, O={"status": "RED", "ts": 200})
    fx.advance({REG: reg(theirs), "code.py": "two\n"})
    why = fx.fx.level_books()
    ok(why is None, "registry moved by origin: the books level (%s)" % why)
    ok(fx.behind() == "0" and read(fx.books, "code.py") == "two\n", "registry: the clone is on origin's code")
    got = json.loads(read(fx.books, REG))
    ok(got.get("A") == mine["A"], "registry: books' new run of A stands over HEAD")
    ok(got.get("B") == theirs["B"] and got.get("O") == theirs["O"], "registry: origin's own entries stand")
    ok(got.get("C") == theirs["C"], "registry: a key both changed takes the later run (origin ts 200 > books ts 50)")
    ok(got.get("NEW") == mine["NEW"] and "D" not in got, "registry: books' added key carried, removed key removed")
    ok(fx.kept(REG) == reg(mine), "registry: books' bytes kept in books_dirt")
    j = [x for x in fx.journal() if x.get("do") == "books_registry_carried"]
    ok(j and j[-1]["path"] == REG and set(j[-1]["keys"]) == {"A", "D", "NEW"},
       "registry: the carry is journalled by path and key: %s" % (j[-1] if j else None))
    fx.done()


def t_deleted_registry_takes_origins():
    fx = Fix()
    os.remove(os.path.join(fx.books, REG))
    theirs = dict(fx.base, O={"status": "RED", "ts": 200})
    fx.advance({REG: reg(theirs)})
    why = fx.fx.level_books()
    ok(why is None and json.loads(read(fx.books, REG)) == theirs,
       "a registry deleted in books levels to origin's, no key of it removed (%s)" % why)
    fx.done()


def t_moved_left_files_level():
    fx = Fix()
    put(fx.books, TRANS, "from a run\n")
    put(fx.books, TRIP, "from a run\n")
    fx.advance({TRANS: "origin's\n", TRIP: "origin's\n", "code.py": "two\n"})
    why = fx.fx.level_books()
    ok(why is None and fx.behind() == "0", "left files moved by origin: the books level (%s)" % why)
    ok(read(fx.books, TRANS) == "origin's\n" and read(fx.books, TRIP) == "origin's\n", "left files: origin's copy stands")
    ok(fx.kept(TRANS) == "from a run\n" and fx.kept(TRIP) == "from a run\n", "left files: books' copies kept")
    paths = {x["path"] for x in fx.journal() if x.get("do") == "books_left_file_replaced"}
    ok(paths == {TRANS, TRIP}, "left files: each replacement journalled by path")
    fx.done()


def t_stopped_level_puts_back():
    fx = Fix()
    put(fx.books, REG, reg(dict(fx.base, A={"status": "RED", "ts": 300})))
    put(fx.books, TRANS, "from a run\n")
    before = (read(fx.books, REG), read(fx.books, TRANS))
    fx.advance({REG: reg(dict(fx.base, B={"status": "GREEN", "ts": 200})), TRANS: "origin's\n"})
    fx.fx._level_rows = lambda *a: "stopped for the test"
    why = fx.fx.level_books()
    ok(why == "stopped for the test" and fx.behind() != "0", "stopped level: the refusal comes back")
    ok((read(fx.books, REG), read(fx.books, TRANS)) == before, "stopped level: both set-aside files are as the run left them")
    fx.done()


def t_reset_refusal_names_file():
    fx = Fix()
    fx.advance({"code.py": "two\n"})
    g(fx.books, "update-index", "-q", "--refresh")
    calls = []
    real = fx.fx.git

    def git(cwd, *a, **k):      # the reset alone, as if git refused it: what does the books' reason say?
        calls.append(a[0])
        if a[0] == "reset":
            return subprocess.CompletedProcess(a, 128, "", "error: Entry 'code.py' not uptodate. Cannot merge.\n")
        return real(cwd, *a, **k)
    fx.fx.git = git
    why = fx.fx.level_books()
    ok("reset" in calls and why and "code.py" in why and "reset --keep refused" in why,
       "a refused reset names its file: %s" % why)
    fx.done()


def t_flush_publishes_registry():
    d = tempfile.mkdtemp(prefix="rlbregf-")
    b = os.path.join(d, "books")
    os.makedirs(b)
    subprocess.run(["git", "init", "-q", "-b", "main", b], check=True)
    put(b, REG, reg({"A": {"ts": 1}}))
    put(b, "publish", '#!/bin/sh\nprintf "%s\\n" "$@" > published.txt\n')
    os.chmod(os.path.join(b, "publish"), 0o755)
    g(b, "add", ".")
    g(b, "commit", "-qm", "base")
    g(b, "update-ref", "refs/remotes/origin/main", "HEAD")
    fx = R.Effects.__new__(R.Effects)
    fx.books, fx.r = b, {"seat": "BENCH"}
    ok(fx.flush() is None and not os.path.exists(os.path.join(b, "published.txt")), "flush: a clean registry publishes nothing")
    put(b, REG, reg({"A": {"ts": 2}}))
    ok(fx.flush() is None, "flush: runs")
    said = read(b, "published.txt").split("\n") if os.path.exists(os.path.join(b, "published.txt")) else []
    ok(REG in said, "flush: a registry a run left dirty in books is published with no shard dirty: %s" % said)
    os.remove(os.path.join(b, "published.txt"))
    put(b, "x.txt", "origin moved on\n")
    g(b, "add", "x.txt")
    g(b, "commit", "-qm", "origin")
    g(b, "update-ref", "refs/remotes/origin/main", "HEAD")
    g(b, "reset", "-q", "--soft", "HEAD~1")
    g(b, "rm", "-q", "--cached", "x.txt")
    ok(fx.flush() is None and not os.path.exists(os.path.join(b, "published.txt")),
       "flush: books behind origin does not publish the registry")
    shutil.rmtree(d, ignore_errors=True)


def t_merge_rules():
    base = {"A": {"ts": 1}, "B": {"ts": 1}}
    m, c = L.merge_registry(base, {"A": {"ts": 5}, "B": {"ts": 1}}, {"A": {"ts": 9}, "B": {"ts": 1}})
    ok(m["A"] == {"ts": 9} and c == [], "merge: origin's later run of a both-changed key stands")
    m, c = L.merge_registry(base, {"A": {"ts": 9}, "B": {"ts": 1}}, {"A": {"ts": 5}, "B": {"ts": 1}})
    ok(m["A"] == {"ts": 9} and c == ["A"], "merge: books' later run stands")
    m, c = L.merge_registry(base, base, {"A": {"ts": 1}})
    ok(m == {"A": {"ts": 1}} and c == [], "merge: books untouched, origin's removal stands")
    rv = {"said": "looks right", "ts": 150}
    t = {"A": {"status": "GREEN", "ts": 1, "owner_review": rv}, "B": {"ts": 1}}
    m, c = L.merge_registry(base, {"A": {"status": "PENDING-OWNER-REVIEW", "ts": 200, "owner_review": None},
                                   "B": {"ts": 1}}, t)
    ok(m["A"] == {"status": "GREEN", "ts": 200, "owner_review": rv} and c == ["A"],
       "merge: books' later re-run keeps the owner review origin recorded, and is GREEN as his review makes it: %s" % m["A"])
    m, c = L.merge_registry(base, {"A": {"ts": 1, "owner_review": rv}, "B": {"ts": 1}}, {"A": {"ts": 100}, "B": {"ts": 1}})
    ok(m["A"] == {"ts": 100, "owner_review": rv}, "merge: a review books recorded survives origin's earlier re-run: %s" % m["A"])


def t_raise_after_reset_hands_back():
    fx = Fix()
    mine = dict(fx.base, A={"status": "RED", "ts": 300})
    put(fx.books, REG, reg(mine))
    theirs = dict(fx.base, O={"status": "RED", "ts": 200})
    fx.advance({REG: reg(theirs), "code.py": "two\n"})
    real = fx.fx._level_rows

    def level_then_raise(*a):
        real(*a)
        raise OSError("disk full after the reset")
    fx.fx._level_rows = level_then_raise
    try:
        fx.fx.level_books()
    except OSError:
        pass
    got = json.loads(read(fx.books, REG))
    ok(fx.behind() == "0" and got.get("O") == theirs["O"] and got.get("A") == mine["A"],
       "a raise after the reset landed still merges: origin's keys are not overwritten by books' old copy")
    fx.done()


def main():
    for t in (t_merge_rules, t_moved_registry_merges, t_deleted_registry_takes_origins, t_moved_left_files_level,
              t_stopped_level_puts_back,
              t_reset_refusal_names_file, t_flush_publishes_registry, t_raise_after_reset_hands_back):
        t()
    print("selftest_relentless_books_registry: %d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
