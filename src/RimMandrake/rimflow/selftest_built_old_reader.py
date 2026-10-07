#!/usr/bin/env python3
"""Selftest: what a clone running PRE-step-2 rimflow sees in a ledger written by step 2.

    python3 src/RimMandrake/rimflow/selftest_built_old_reader.py

🔑 WHY. The ledger shards are read by every clone, and a clone can be running older code
than the window that wrote an event. Step 2 adds a verb (`implemented`) and two fields on
an existing verb (`verify --level --criterion`). This test does not reason about the old
reader — it RUNS it: the rimflow package as committed at OLD_REF (577d72d2f, step 1, the
last commit before step 2) is extracted with `git show` into a temp dir, and both its
model and its CLI are pointed at a ledger the NEW CLI just wrote.

What it pins (the measured answer, printed at the end):
  * the old reader never crashes — replay, `next --peek`, `show`, `queue`, `why` exit 0;
  * `implemented` is an unknown verb there -> one entry in `world.errors`, nothing applied:
    the item keeps its pre-implemented state (`ready`) and `needs` (`offline`), so an old
    `next` still OFFERS it as build work (the step-1 reconcile guard is the only thing
    that can stop that, and only when git names the item);
  * a `verify` carrying `level`/`criterion` is refused WHOLE there (unknown field) -> one
    more error, and the run does not appear in its `show`;
  * an item `implemented` straight to `done` is still OPEN on the old reader;
  * the NEW reader replays the same ledger with zero errors.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD_REF = "577d72d2f"
PKG = "src/RimMandrake/rimflow"
sys.path.insert(0, os.path.dirname(HERE))

from rimflow import model                                         # noqa: E402

PASS, FAIL = [], []
CTX = {}

BUILT = "OLD_READER_BUILT_1"        # implemented with L1+L4 owed, then A1 passed
DONE = "OLD_READER_DONE_1"          # implemented with nothing owed -> done
PLAIN = "OLD_READER_PLAIN_1"        # untouched ready item, the control


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))
    except Exception as e:                                       # noqa: BLE001
        FAIL.append(name)
        print("FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e))


def env(seat="FOUNDRY"):
    e = {k: v for k, v in os.environ.items()
         if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    e["RIMFLOW_LEDGER"] = os.path.join(CTX["led"], "events.jsonl")
    e["RIMFLOW_ITEMS"] = os.path.join(CTX["led"], "items")
    e["RIMFLOW_PROBE"] = "no-reading"
    e["RIMFLOW_SEAT"] = seat
    e["RIMFLOW_GITINDEX"] = CTX["fixture"]
    return e


def run(cli, *args, **kw):
    p = subprocess.run([sys.executable, cli] + list(args), capture_output=True,
                       cwd=REPO, env=env(kw.get("seat", "FOUNDRY")))
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def new_ok(*args, **kw):
    rc, out, err = run(CLI, *args, **kw)
    assert rc == 0, "NEW `%s` exited %d: %s %s" % (" ".join(args), rc, out[-400:], err[-400:])
    return out


def old(*args, **kw):
    rc, out, err = run(CTX["old_cli"], *args, **kw)
    assert rc == 0, "OLD `%s` exited %d — an old clone would be broken:\n%s\n%s" % (
        " ".join(args), rc, out[-600:], err[-600:])
    return out


def extract_old_package(dest):
    """The rimflow package exactly as committed at OLD_REF."""
    names = subprocess.check_output(("git", "ls-tree", "--name-only", OLD_REF, PKG + "/"),
                                    cwd=REPO).decode().split()
    pkg = os.path.join(dest, "rimflow")
    os.makedirs(pkg)
    for n in names:
        if not n.endswith(".py"):
            continue
        blob = subprocess.check_output(("git", "show", "%s:%s" % (OLD_REF, n)), cwd=REPO)
        with open(os.path.join(pkg, os.path.basename(n)), "wb") as fh:
            fh.write(blob)
    assert os.path.exists(os.path.join(pkg, "model.py")), "no model.py at %s" % OLD_REF
    return pkg


def setup():
    root = tempfile.mkdtemp(prefix="rimflow_old_reader_")
    CTX["root"] = root
    CTX["old_cli"] = os.path.join(extract_old_package(os.path.join(root, "old")), "cli.py")
    CTX["led"] = os.path.join(root, "ledger")
    os.makedirs(os.path.join(CTX["led"], "items"))
    sha = "c0ffee1" + "0" * 33
    CTX["sha"] = sha
    CTX["fixture"] = os.path.join(root, "fx.json")
    with open(CTX["fixture"], "w") as fh:
        json.dump({"ref": "origin/main", "head": "f" * 40, "commits": [
            {"sha": sha, "ts": "2099-01-01T00:00:00Z", "subject": "unrelated",
             "body": "", "files": ["src/X.xml"]}]}, fh)
    crit = os.path.join(root, "crit.txt")
    with open(crit, "w") as fh:
        fh.write("O1 L0: compiles\nA1 L1: defs resolve\nA4 L4: owner plays it\n")
    # Written by the NEW cli, so the events are exactly what step 2 puts on the ledger.
    for iid in (BUILT, DONE, PLAIN):
        new_ok("file", iid, "--for", "FOUNDRY", "--title", "old reader " + iid)
        # step 3: `claim` leases and STARTS the item; `reclaim` returns it to plain `ready`,
        # the pre-implemented state this test was written against. The lease `take` it
        # leaves is an unknown verb to this old reader (selftest_lease.py covers leases).
        new_ok("claim", iid)
        new_ok("reclaim", iid)
    new_ok("implemented", BUILT, "--sha", sha[:9], "--criteria-file", crit)
    new_ok("verify", BUILT, "--criterion", "A1", "--result", "pass", "--config", "min-13")
    new_ok("implemented", DONE, "--sha", sha[:9], "--none-owed")


def old_replay():
    """The OLD model, in its own interpreter, over the shard the new CLI wrote."""
    code = (
        "import json,sys; sys.path.insert(0, %r)\n"
        "from rimflow import model, priority\n"
        "model.EVENTS = %r\n"
        "w = model.replay(model.read())\n"
        "print(json.dumps({'items': {k: [v.state, v.needs, len(v.runs)] for k, v in "
        "w.items.items()}, 'errors': [[e[1], e[2][:120]] for e in w.errors], "
        "'rank': [i.id for i in priority.rank(w, 'FOUNDRY')]}))\n"
        % (os.path.dirname(os.path.dirname(CTX["old_cli"])),
           os.path.join(CTX["led"], "events.jsonl")))
    p = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert p.returncode == 0, "the OLD model raised on the new ledger:\n%s" % p.stderr.decode()
    return json.loads(p.stdout.decode())


# ---------------------------------------------------------------------------
def t_old_model_replays_without_crashing():
    r = old_replay()
    CTX["old"] = r
    verbs = sorted(e[0] for e in r["errors"] if e[0] != "lease")
    assert verbs == ["implemented", "implemented", "verify"], r["errors"]
    assert sum(1 for e in r["errors"] if e[0] == "lease") == 3, r["errors"]
    assert any("unknown verb 'implemented'" in e[1] for e in r["errors"]), r["errors"]
    assert any("no field" in e[1] for e in r["errors"] if e[0] == "verify"), r["errors"]


def t_old_model_sees_built_and_done_items_as_still_ready_offline():
    r = CTX.get("old") or old_replay()
    assert r["items"][BUILT] == ["ready", "offline", 0], r["items"][BUILT]
    assert r["items"][DONE] == ["ready", "offline", 0], r["items"][DONE]
    assert set(r["rank"]) == {BUILT, DONE, PLAIN}, \
        "old rank no longer offers built items — update the report: %r" % r["rank"]


def t_old_cli_read_verbs_exit_zero():
    out = old("next", "--peek")
    assert "rimflow start" in out, out
    show = old("show", BUILT)
    assert "--- runs" not in show, "the old reader showed a run it should have dropped:\n" + show
    q = old("queue", "FOUNDRY")
    assert BUILT in q and DONE in q, q
    old("why", DONE)


def t_new_reader_has_no_errors_on_the_same_ledger():
    model.EVENTS = os.path.join(CTX["led"], "events.jsonl")
    w = model.replay(model.read())
    assert not w.errors and not w.tolerated, (w.errors, w.tolerated)
    assert w.items[BUILT].state == "validated" and w.items[DONE].state == "done"
    assert w.items[PLAIN].state == "ready"


def report():
    r = CTX.get("old")
    if not r:
        return
    print("\nOLD CLONE (%s) on a step-2 ledger:" % OLD_REF)
    for iid in (BUILT, DONE, PLAIN):
        st, nd, runs = r["items"][iid]
        print("  %-20s state %-9s needs %-8s runs %d" % (iid, st, nd, runs))
    print("  world.errors: %d (%s)" % (len(r["errors"]),
                                       ", ".join(e[0] for e in r["errors"])))
    print("  offered by old `next`/rank: %s" % ", ".join(r["rank"]))


if __name__ == "__main__":
    try:
        setup()
        for fn in (t_old_model_replays_without_crashing,
                   t_old_model_sees_built_and_done_items_as_still_ready_offline,
                   t_old_cli_read_verbs_exit_zero,
                   t_new_reader_has_no_errors_on_the_same_ledger):
            case(fn.__name__, fn)
        report()
    finally:
        shutil.rmtree(CTX.get("root", "/nonexistent-rimflow-old-reader"), ignore_errors=True)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
