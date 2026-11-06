#!/usr/bin/env python3
"""selftest_entrypoint_inventory.py - the inventory sees every kind of entry point, and the retired modules stay retired.

    python3 src/RimMandrake/rimflow/selftest_entrypoint_inventory.py

Each entry-point kind is planted alone in a throwaway repo and must fail the check by name; history and prose must not.
The real tree must pass with its probes seeing known entry points; a revert bundle is judged good and four ways bad.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import entrypoint_inventory as E  # noqa: E402

FAILS = []
NONE = ({}, [])
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.hooksPath=/dev/null",
       "-c", "commit.gpgsign=false"]


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def git(root, *args):
    return subprocess.run(GIT + ["-C", root] + list(args), capture_output=True, text=True, check=True).stdout.strip()


def repo(files):
    root = tempfile.mkdtemp(prefix="selftest_entrypoint_")
    git(root, "init", "--quiet", "-b", "main")
    for rel, text in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)
    git(root, "add", "-A")
    git(root, "commit", "--quiet", "-m", "fixture")
    return root


def verdict(files, installed=NONE):
    root = repo(files)
    try:
        return E.check_retired(root, retired={"deadmod": "x"}, kept={}, probes=False, installed=installed)
    finally:
        shutil.rmtree(root, ignore_errors=True)


PY = "tool/caller.py"
REACH = {
    "import": {PY: "import deadmod\n"},
    "from-import": {PY: "from rimflow import deadmod\n"},
    "dotted import": {PY: "import rimflow.deadmod as d\n"},
    "from dotted module": {PY: "from rimflow.deadmod import thing\n"},
    "importlib literal": {PY: "import importlib\nimportlib.import_module('rimflow.deadmod')\n"},
    "__import__ literal": {PY: "__import__('deadmod')\n"},
    "spec_from_file_location": {PY: "import importlib.util as u\nu.spec_from_file_location('h', 'a/deadmod.py')\n"},
    "computed import handed the name": {PY: "def _mod(n):\n    return n\n_mod('deadmod')\n"},
    "path join": {PY: "import os\nos.path.join('a', 'deadmod.py')\n"},
    "python -m in argv": {PY: "cmd = ['python3', '-m', 'rimflow.deadmod']\n"},
    "python -m in a shell string": {PY: "cmd = 'cd x; python3 -m deadmod --go'\n"},
    "unit ExecStart": {"src/RimMandrake/Utils/systemd/rm-x.service": "[Service]\nExecStart=/usr/bin/python3 a/deadmod.py\n"},
    "shell script": {"tools/run.sh": "python3 a/deadmod.py\n"},
    "powershell": {"tools/run.ps1": "python.exe a\\deadmod.py\n"},
    "githook": {"infrastructure/githooks/pre-push": "python3 a/deadmod.py\n"},
    "repo-root tool": {"publish": "python3 a/deadmod.py\n"},
    "settings hook": {".claude/settings.json": '{"hooks": "python3 a/deadmod.py"}\n'},
    "schedule json": {"src/x/dispatcher_schedule.json": '["python3", "a/deadmod.py"]\n'},
    "role instructions": {"src/RimMandrake/rimflow/roles/r.md": "Run `python3 a/deadmod.py`.\n"},
    "lesson": {"infrastructure/state/lessons/l.md": "Before filing, run a/deadmod.py.\n"},
    "skill": {"skills/s/SKILL.md": "python3 a/deadmod.py\n"},
    "agent definition": {".claude/agents/a.md": "python3 a/deadmod.py\n"},
    "unparsable python": {PY: "def (:\n  'a/deadmod.py'\n"},
}
for what, files in REACH.items():
    code, lines = verdict(files)
    check(code == 1 and any(next(iter(files)) in l for l in lines), "reached through %s: %s" % (what, lines[:1]))

NOT = {
    "docstring": {PY: '"""deadmod.py used to run here."""\n'},
    "function docstring": {PY: 'def f():\n    "run deadmod.py by hand"\n'},
    "comment": {PY: "# python3 deadmod.py\n"},
    "longer name": {PY: "x = 'not_deadmod.py and deadmod_two.py'\nimport deadmod_two\n"},
    "dated design prose": {"design/old.md": "python3 deadmod.py\n"},
    "ledger": {"infrastructure/state/ledger/events/X.jsonl": '{"why":"deadmod.py"}\n'},
    "conversation": {"conversations/c.md": "python3 deadmod.py\n"},
    "handoff": {"infrastructure/state/handoffs/h.md": "deadmod.py\n"},
    "a state directory of that name": {"tools/run.sh": "cat infrastructure/state/deadmod/record.json\n"},
}
for what, files in NOT.items():
    code, lines = verdict(files)
    check(code == 0, "not an entry point: %s (%s)" % (what, lines[:1]))

code, lines = verdict({PY: "x = 1\n"}, installed=({"installed:rm-x.service": "ExecStart=python3 /a/deadmod.py\n"}, []))
check(code == 1 and "installed:rm-x.service" in lines[-1], "an installed unit the repo does not hold counts")
code, lines = verdict({PY: "x = 1\n"}, installed=({"installed:crontab": "0 3 * * * python3 -m rimflow.deadmod\n"}, []))
check(code == 1 and "installed:crontab" in lines[-1], "a crontab line counts")
code, lines = verdict({E.RIMFLOW + "/deadmod.py": "x = 1\n"})
check(code == 1 and "still exists" in lines[-1], "the file itself still there fails")
code, lines = verdict({PY: "x = 1\n"}, installed=({}, ["~/.config/systemd/user"]))
check(code == 0 and "unread" in lines[0], "an unreadable installed source is said, not hidden")

root = repo({E.RIMFLOW + "/deadmod.py": "import deadmod\nprint('deadmod.py')\n", E.RIMFLOW + "/caller.py": "x = 1\n"})
inv, _ = E.inventory(root, ["deadmod"], NONE)
check(inv["deadmod"] == [], "a module naming itself is not its own entry point")
shutil.rmtree(root, ignore_errors=True)

root = repo({PY: "x = 1\n"})
code, lines = E.check_retired(root, retired={}, kept={"gone": "why"}, probes=False, installed=NONE)
check(code == 1 and "is kept" in lines[-1], "a kept module that vanished fails")
code, lines = E.check_retired(root, retired={}, kept={}, probes=True, installed=NONE)
check(code == 2 and lines[-1].startswith("UNMEASURED"), "a tree where the probes cannot see exits 2, not green")
shutil.rmtree(root, ignore_errors=True)

# The real tree.
code, lines = E.check_retired()
check(code == 0, "the real tree: every retired module absent and unreached, kept ones present: %s" % lines[-1:])
check(not set(E.RETIRED) & set(E.KEPT), "no module is both retired and kept")
check(E.classify("src/RimMandrake/Utils/hook_latency_corpus.json") is None, "recorded prompts in the latency corpus start nothing")
inv, _ = E.inventory(E.ROOT, ["regrade"])
check(any(k == "doc" and f.endswith("findings_judge_prompt.md") for k, f, _l in inv["regrade"]),
      "regrade's daily caller, the findings judge prompt, is read as an entry point")
check(os.path.exists(os.path.join(E.ROOT, E.RIMFLOW, "close_audit.py")), "close_audit stays (redesign_final.md G20)")
inv, _ = E.inventory(E.ROOT, ["audit_prescreen"])
check(any(k == "import" and f.endswith("role_launch.py") for k, f, _l in inv["audit_prescreen"]),
      "the instrument sees role_launch's import of audit_prescreen, the one the importer-grep table called dead")


def bundle_case(retired, doctor=None, ancestor=True):
    """-> check_revert's verdict over a fixture: P, D deletes the module (and adds a file), R undoes it."""
    mod = E.RIMFLOW + "/deadmod.py"
    root = repo({mod: "x = 1\n", "other.py": "y = 1\n"})
    git(root, "rm", "--quiet", mod)
    with open(os.path.join(root, "added.py"), "w") as f:
        f.write("z = 1\n")
    git(root, "add", "added.py")
    git(root, "commit", "--quiet", "-m", "deletion")
    deletion = git(root, "rev-parse", "HEAD")
    parent = git(root, "rev-parse", "HEAD^")
    tree = (doctor or (lambda r, p: p + "^{tree}"))(root, parent)
    rev = git(root, "commit-tree", tree, "-p", deletion, "-m", "revert")
    git(root, "update-ref", "refs/heads/revert_it", rev)
    path = os.path.join(root, "..", os.path.basename(root) + ".bundle")
    git(root, "bundle", "create", "--quiet", path, "refs/heads/revert_it", "^" + deletion)
    if not ancestor:
        git(root, "update-ref", "refs/heads/main", parent)
        git(root, "symbolic-ref", "HEAD", "refs/heads/main")
    try:
        return E.check_revert(path, root, retired=retired)
    finally:
        shutil.rmtree(root, ignore_errors=True)
        os.path.exists(path) and os.remove(path)


def wrong_tree(root, parent):
    """The pre-deletion tree with other.py changed: a revert that is not byte for byte."""
    blob = subprocess.run(GIT + ["-C", root, "hash-object", "-w", "--stdin"], input="y = 2\n", capture_output=True,
                          text=True, check=True).stdout.strip()
    idx = os.path.join(root, ".git", "tmp_index")
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    subprocess.run(GIT + ["-C", root, "read-tree", parent], env=env, check=True)
    subprocess.run(GIT + ["-C", root, "update-index", "--add", "--cacheinfo", "100644," + blob + ",other.py"], env=env, check=True)
    return subprocess.run(GIT + ["-C", root, "write-tree"], env=env, capture_output=True, text=True, check=True).stdout.strip()


code, lines = bundle_case({"deadmod": "x"})
check(code == 0 and lines[0].startswith("OK revert commit"), "a true revert passes: %s" % lines[:1])
code, lines = bundle_case({"deadmod": "x", "never_deleted": "x"})
check(code == 1 and "does not delete" in lines[0], "a deletion that missed a retired module fails: %s" % lines[:1])
code, lines = bundle_case(({"retired_later": "x"}, {"deadmod": "x"}))
check(code == 0, "a bundle checks against its own batch when another retirement has joined: %s" % lines[:1])
code, lines = bundle_case(({"retired_later": "x"}, {"deadmod": "x", "never_deleted": "x"}))
check(code == 1 and "does not delete" in lines[0], "no batch fully deleted fails: %s" % lines[:1])
code, lines = bundle_case({"deadmod": "x"}, doctor=wrong_tree)
check(code == 1 and "differs" in lines[0], "a revert that is not byte for byte fails: %s" % lines[:1])
code, lines = bundle_case({"deadmod": "x"}, ancestor=False)
check(code == 1 and "not in the history" in lines[0], "a deletion outside our history fails: %s" % lines[:1])
fd, junk = tempfile.mkstemp()
os.write(fd, b"not a bundle\n")
os.close(fd)
code, lines = E.check_revert(junk, E.ROOT, retired={"deadmod": "x"})
check(code == 1 and "not a git bundle" in lines[0], "a file that is no bundle fails")
os.remove(junk)
code, lines = E.check_revert(junk, E.ROOT, retired={"deadmod": "x"})
check(code == 1 and "no bundle" in lines[0], "a missing bundle fails")

print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d" % len(FAILS)))
sys.exit(1 if FAILS else 0)
