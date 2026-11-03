#!/usr/bin/env python3
"""Selftest for block_orphan_item_prose.py, through real `git push`es into a bare remote via the real pre-push script.

    python3 .claude/hooks/selftest_block_orphan_item_prose.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
HOOK = os.path.join(HERE, "block_orphan_item_prose.py")
PRE_PUSH = os.path.join(REPO, "infrastructure", "githooks", "pre-push")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
ITEMS = "infrastructure/state/items"
SHARD = "infrastructure/state/ledger/events/BENCH.jsonl"
# 6489a12285 is the commit that turned the nightly red; its parent is the base it was pushed onto
INCIDENT = "6489a12285"
INCIDENT_ITEMS = {"STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF", "TITAN_WALL_CRUSH_DIAGNOSE_WOOD_WALL_SHRUGS"}
FAILS = []


def expect(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


def git(work, *a, check=True):
    r = subprocess.run(["git", "-C", work] + list(a), capture_output=True, text=True, env=ENV)
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (a, r.stderr))
    return r


class Fixture:
    """A clone whose hooks are the real pre-push and guard; rimflow is the real one, by an untracked symlink."""

    def __init__(self, tmp):
        self.work, bare = os.path.join(tmp, "work"), os.path.join(tmp, "bare.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True, env=ENV)
        os.makedirs(self.work)
        git(self.work, "init", "-q", "-b", "main")
        git(self.work, "remote", "add", "origin", bare)
        os.symlink(os.path.join(REPO, "src"), os.path.join(self.work, "src"))
        self.write("infrastructure/githooks/pre-push", open(PRE_PUSH).read())
        os.chmod(os.path.join(self.work, "infrastructure/githooks/pre-push"), 0o755)
        self.write(".claude/hooks/block_orphan_item_prose.py", open(HOOK).read())
        git(self.work, "config", "core.hooksPath", "infrastructure/githooks")
        self.tsn = 1000
        self.row("BASE_ITEM_LIVE", "file")
        self.commit("infrastructure", ".claude", msg="base")

    def write(self, rel, text, mode="w"):
        p = os.path.join(self.work, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, mode, encoding="utf-8") as f:
            f.write(text)

    def row(self, iid, event, **extra):
        self.tsn += 1
        ev = dict(seat="BENCH", event=event, id=iid, ts="2026-11-03T00:00:00Z", tsn=self.tsn, **extra)
        if event == "file":
            ev.update(title="t", kind="bug", target="v1", **{"for": "BENCH"})
        self.write(SHARD, json.dumps(ev) + "\n", "a")

    def prose(self, stem):
        self.write("%s/%s.md" % (ITEMS, stem), "## spec\nx\n")

    def commit(self, *paths, msg="c"):
        git(self.work, "add", "--", *paths)
        git(self.work, "commit", "-q", "--no-verify", "-m", msg)

    def push(self):
        return git(self.work, "push", "-q", "origin", "main", check=False)


def scenarios(fx):
    r = fx.push()
    expect(r.returncode == 0, "a base push with no new prose passes: %s" % r.stderr[-200:])

    fx.prose("ORPHAN_NO_ROW")
    fx.commit(ITEMS)
    r = fx.push()
    expect(r.returncode == 1 and "REFUSED" in r.stderr and "ORPHAN_NO_ROW" in r.stderr,
           "prose with no ledger row is REFUSED by name: rc=%d" % r.returncode)

    fx.row("ORPHAN_NO_ROW", "file")              # the row exists only uncommitted: origin would still drift
    r = fx.push()
    expect(r.returncode == 1 and "ORPHAN_NO_ROW" in r.stderr, "a row left uncommitted in the shard does not count")

    fx.commit(SHARD)                             # the fix the refusal names; a later commit in the same push
    r = fx.push()
    expect(r.returncode == 0, "filing and committing the shard in the same push passes: %s" % r.stderr[-300:])

    fx.prose("BASE_ITEM_LIVE.names")
    fx.commit(ITEMS)
    r = fx.push()
    expect(r.returncode == 0, "a companion file of a live item passes: %s" % r.stderr[-300:])

    fx.write("%s/closed/CLOSED_NO_ROW.md" % ITEMS, "x\n")
    fx.commit(ITEMS)
    r = fx.push()
    expect(r.returncode == 0, "items/closed/ is outside the live glob: %s" % r.stderr[-200:])

    fx.prose("ORPHAN_NO_ROW.names")
    fx.row("DONE_ITEM", "file")
    fx.row("DONE_ITEM", "drop", reason="x")
    fx.prose("DONE_ITEM")
    fx.commit(ITEMS, SHARD)
    r = fx.push()
    expect(r.returncode == 1 and "DONE_ITEM" in r.stderr and "terminal" in r.stderr,
           "prose added for a terminal item is REFUSED: rc=%d %s" % (r.returncode, r.stderr[-200:]))
    expect("ORPHAN_NO_ROW.names" not in r.stderr, "a companion of a live item is not named beside it")


def tool_use(fx, cmd):
    """-> what the PreToolUse mode prints for this Bash command in the fixture clone."""
    payload = json.dumps({"tool_input": {"command": cmd}, "cwd": fx.work})
    r = subprocess.run([sys.executable, os.path.join(fx.work, ".claude/hooks/block_orphan_item_prose.py")], input=payload,
                       capture_output=True, text=True, env=ENV)
    return r.stdout + r.stderr


def pre_tool_use_scenarios(fx):
    """Runs after scenarios(): the terminal item's commit is still waiting in the clone."""
    for cmd in ("git push origin main", "./publish", "git -C %s push" % fx.work, "cd %s && ./publish -m x a" % fx.work,
                "python3 src/RimMandrake/Utils/publish.py"):
        said = tool_use(fx, cmd)
        expect('"deny"' in said and "DONE_ITEM" in said, "PreToolUse denies %r with the waiting orphan: %s" % (cmd, said[-200:] if '"deny"' not in said else ""))
    for cmd in ("git status", "grep publish notes.txt", "echo git push"):
        expect(tool_use(fx, cmd) == "", "PreToolUse leaves %r alone" % cmd)
    git(fx.work, "fetch", "-q", "origin")
    git(fx.work, "checkout", "-q", "-B", "clean", "origin/main")
    expect(tool_use(fx, "git push origin main") == "", "PreToolUse lets a clone with no orphan waiting push")


def wired():
    """The pre-push loop and settings.json must both call the guard; the deadman reads only the second."""
    expect("block_orphan_item_prose.py" in open(PRE_PUSH).read(), "infrastructure/githooks/pre-push calls the guard")
    settings = json.dumps(json.load(open(os.path.join(REPO, ".claude", "settings.json")))["hooks"]["PreToolUse"])
    expect("block_orphan_item_prose.py" in settings, ".claude/settings.json wires the guard as PreToolUse")


def incident():
    """The commit that made the alarm, read from this clone's real history."""
    if git(REPO, "cat-file", "-e", INCIDENT + "^{commit}", check=False).returncode:
        print("SKIP  incident commit %s is not in this clone" % INCIDENT)
        return
    sys.path.insert(0, HERE)
    import block_orphan_item_prose as guard
    bad = {stem for stem, _ in guard.orphans(REPO, INCIDENT + "^", INCIDENT)}
    expect(bad == INCIDENT_ITEMS, "the incident commit is refused, naming exactly its two files: %s" % sorted(bad))


def main():
    tmp = tempfile.mkdtemp(prefix="orphan_prose_selftest_")
    try:
        fx = Fixture(tmp)
        scenarios(fx)
        pre_tool_use_scenarios(fx)
        wired()
        incident()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print()
    print("%d FAILED" % len(FAILS) if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
