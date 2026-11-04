#!/usr/bin/env python3
"""One real `relentless.py tick`, as the timer runs it, on a scratch root: a crash on a rarely-taken branch fails here,
before it lands, not on rm-relentless every tick (RELENTLESS_TICK_PROVE_FIRST_SHUFFLE_BIT; OPS_TIMER_REPAIR_PRXC, three
outages: c5a80db360 made level_books call self.journal, which Effects has not; fixed f4133dd996).

The tick is a subprocess of the books' own copy of the code, exactly as the unit starts it, so main(), the real Effects
and the timer's import path all run. The books are a scratch clone of a scratch origin holding THIS working tree's
rimflow (uncommitted edits included) and an empty ledger, and they are seeded so the tick's sync must take level_books'
set-equal reorder branch: a code_review shard reordered here while origin moved it, which a fast-forward cannot take.

Sealed: the real rules name host paths (walls.marker.box_root, ops_watch_dir) and a bare scratch RELENTLESS_ROOT tick
reaped a real box and told the real ops ledger an alarm (2026-11-04). The test writes its own rules file that points
every one of them into the scratch dir and staffs nothing, and checks the real told ledger heard nothing and no real box was reaped.

Then the 2026-11-02 mutant: the same tick on a copy with `self.store.journal` turned back into `self.journal` in
level_books must fail. A test that passes on the defect proves nothing.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SHARD = "infrastructure/state/code_review/B.jsonl"
FAILS = []


def ok(cond, what):
    print("  %s %s" % ("ok  " if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *a],
                          cwd=cwd, check=True, capture_output=True, text=True, timeout=120,
                          stdin=subprocess.DEVNULL).stdout


def put(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def sealed_rules(d):
    """The real rules with every host path moved into `d` and nothing to staff, launch or prove."""
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        r = json.load(f)
    r["enabled"] = True
    r["ops_watch_dir"] = os.path.join(d, "ops_watch")
    for prof in (r.get("walls") or {}).values():
        if isinstance(prof, dict) and "box_root" in prof:
            prof["box_root"] = os.path.join(d, "walled")
    r["max_workers"] = 0
    r["max_queued"] = 0
    r["enrol_per_tick"] = 0
    r["warm_clones"] = 0
    r["pool_seats"] = []
    r["pool_needs"] = []
    r["pool_targets"] = []
    r["game"] = dict(r.get("game") or {}, enabled=False)
    r["live"] = dict(r.get("live") or {}, auto=False)
    st = dict(r.get("staffing") or {})
    for k in [k for k in st if "launch_per_tick" in k and not k.startswith("_")]:
        st[k] = 0
    r["staffing"] = st
    os.makedirs(os.path.join(d, "walled"), exist_ok=True)
    os.makedirs(os.path.join(d, "ops_watch"), exist_ok=True)
    path = os.path.join(d, "rules.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1)
    return path, r


def build(d, mutate=False):
    """-> books. Origin holds this tree's rimflow and an empty ledger; the books hold a set-equal reorder of SHARD that
    origin has since moved, so only level_books can bring them level."""
    up, origin, books = os.path.join(d, "up"), os.path.join(d, "o.git"), os.path.join(d, "root", "books")
    rim = os.path.join(up, "src", "RimMandrake", "rimflow")
    shutil.copytree(HERE, rim, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # the engine imports across src/RimMandrake (Utils/rmpaths, contracts, ...): every tracked .py there, as this working
    # tree has it, and the Utils' config
    repo = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    names = subprocess.run(["git", "-C", repo, "ls-files", "-z", "--", ".gitignore", "src/RimMandrake/*.py", "src/RimMandrake/Utils/*.json"],
                           check=True, capture_output=True, text=True, timeout=60).stdout.split("\0")
    ok(len(names) > 100, "sanity: the engine's sources are listed (%d)" % len(names))
    for n in filter(None, names):
        if n.startswith("src/RimMandrake/rimflow/") or not os.path.isfile(os.path.join(repo, n)):
            continue
        os.makedirs(os.path.dirname(os.path.join(up, n)), exist_ok=True)
        shutil.copy2(os.path.join(repo, n), os.path.join(up, n))
    if mutate:
        p = os.path.join(rim, "relentless.py")
        with open(p, encoding="utf-8") as f:
            src = f.read()
        fixed = 'self.store.journal({"at": iso(time.time()), "do": "books_reorder_restored"'
        ok(src.count(fixed) == 1, "mutant: the restore journal call is where the mutant expects it")
        with open(p, "w", encoding="utf-8") as f:
            f.write(src.replace(fixed, fixed.replace("self.store.journal", "self.journal")))
    put(up, "infrastructure/state/ledger/events/.keep", "")
    put(up, "infrastructure/state/items/.keep", "")
    put(up, SHARD, "a\nb\nc\n")
    git(d, "init", "-q", "--bare", "-b", "main", origin)
    git(up, "init", "-q", "-b", "main")
    git(up, "remote", "add", "origin", origin)
    git(up, "add", "-A", ".")
    git(up, "commit", "-qm", "base")
    git(up, "push", "-q", "origin", "main")
    os.makedirs(os.path.dirname(books), exist_ok=True)
    git(d, "clone", "-q", origin, books)
    put(books, SHARD, "c\na\nb\n")          # the union-merge landing order: same lines, another order
    put(up, SHARD, "a\nb\nc\nd\n")          # origin moves the shard too, so the fast-forward refuses
    git(up, "commit", "-qam", "up")
    git(up, "push", "-q", "origin", "main")
    return books


def run_tick(d, books, rules_path):
    env = dict(os.environ, RELENTLESS_ROOT=os.path.join(d, "root"), RELENTLESS_RULES=rules_path,
               RM_OPS_WATCH_DIR=os.path.join(d, "ops_watch"), RM_RUN_TMP_ROOT=os.path.join(d, "runtmp"),
               CLAUDE_PROJECT_DIR=books, GIT_CONFIG_GLOBAL=os.path.join(d, "gitconfig"))
    for k in ("RIMFLOW_SEAT", "AGENT_SEAT", "RELENTLESS_SUPERVISOR"):
        env.pop(k, None)
    with open(env["GIT_CONFIG_GLOBAL"], "w", encoding="utf-8") as f:
        f.write("[user]\n\tname = t\n\temail = t@t\n[commit]\n\tgpgsign = false\n")
    os.makedirs(env["RM_RUN_TMP_ROOT"], exist_ok=True)
    return subprocess.run([sys.executable, os.path.join(books, "src/RimMandrake/rimflow/relentless.py"), "tick"],
                          cwd=books, env=env, capture_output=True, text=True, timeout=420, stdin=subprocess.DEVNULL)


def journal(d):
    p = os.path.join(d, "root", "store", "journal.jsonl")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def told_since(path, at):
    """-> the told-ledger text appended after byte `at`: other writers append there too, so only lines naming this run's
    scratch dir are this run's."""
    try:
        with open(path, "rb") as f:
            f.seek(at)
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def t_tick_once():
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        real = json.load(f)
    told = os.path.join(real["ops_watch_dir"], "told.jsonl")
    host = [real["ops_watch_dir"]] + \
        [prof["box_root"] for prof in (real.get("walls") or {}).values() if isinstance(prof, dict) and prof.get("box_root")]
    d = tempfile.mkdtemp(prefix="rltickonce-")
    try:
        rules_path, r = sealed_rules(d)
        ok(not any(h in json.dumps(r) for h in host), "sanity: the sealed rules name no real host path: %s" % host)
        books = build(d)
        at = os.path.getsize(told) if os.path.exists(told) else 0
        got = run_tick(d, books, rules_path)
        with open(os.path.join(d, "tick.out"), "w", encoding="utf-8") as f:
            f.write(got.stdout + "\n--- stderr ---\n" + got.stderr)
        ok(got.returncode == 0 and "Traceback" not in got.stderr,
           "one real tick exits 0 with no traceback (exit %d): %s" % (got.returncode, got.stderr[-1500:]))
        try:
            acts = json.loads(got.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            acts = None
        ok(isinstance(acts, list), "the tick prints its acts as one JSON list: %r" % got.stdout[-300:])
        errs = [a for a in (acts or []) if a.get("do") == "error"]
        ok(not errs, "no act is an error: %s" % errs[:3])
        js = journal(d)
        ok(any(x.get("do") == "tick" for x in js), "sanity: the tick journalled itself, so the instrument can see")
        ok(any(x.get("do") == "books_reorder_restored" and SHARD in (x.get("paths") or []) for x in js),
           "the tick took level_books' set-equal reorder branch and journalled the restore")
        ok(git(books, "rev-parse", "HEAD") == git(books, "rev-parse", "origin/main"), "the books are level with origin")
        with open(os.path.join(books, SHARD), encoding="utf-8") as f:
            ok(f.read() == "a\nb\nc\nd\n", "and the shard holds origin's bytes")
        launched = [x for x in js if "launch" in str(x.get("do", ""))]
        ok(not launched, "sealed: the tick launched nothing: %s" % launched[:3])
        ok(d not in told_since(told, at), "sealed: the real told ledger heard nothing from this run")
        reaped = [b for x in js if x.get("do") == "boxes_reaped" for b in x.get("boxes") or []]
        ok(all(str(b).startswith(d) or not str(b).startswith("/") for b in reaped) and
           not any(str(b).startswith(h) for b in reaped for h in host), "sealed: no real box was reaped: %s" % reaped)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_mutant_fails():
    """The defect of c5a80db360 put back: the same tick must now fail, or this test cannot see what it is for."""
    d = tempfile.mkdtemp(prefix="rltickmut-")
    try:
        rules_path, _r = sealed_rules(d)
        books = build(d, mutate=True)
        got = run_tick(d, books, rules_path)
        ok(got.returncode != 0 and "'Effects' object has no attribute 'journal'" in got.stderr,
           "the self.journal mutant crashes the tick (exit %d): %s" % (got.returncode, got.stderr[-300:]))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    for t in (t_tick_once, t_mutant_fails):
        print("--", t.__name__)
        t()
    print("selftest_relentless_tick_once: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
