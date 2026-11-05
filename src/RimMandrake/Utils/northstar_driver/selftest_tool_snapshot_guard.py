#!/usr/bin/env python3
"""Class guard for NIGHTLY_COP_FIX_RED_LMTEZQ_YAXX: a companion [Tool] cannot be committed without its snapshot entry.

    python3 src/RimMandrake/Utils/northstar_driver/selftest_tool_snapshot_guard.py
    python3 ... selftest_tool_snapshot_guard.py --instance "<cs_dir> <snapshot.json>"   one real pair; red if any is missing

No args: fixtures, then a throwaway git repo committing through the REAL infrastructure/githooks/pre-commit: a staged
[Tool] the staged snapshot lacks is refused, the same commit with the snapshot entry passes, an unrelated commit passes.
Offline; no bridge.
"""
import json
import os
import shutil
import subprocess as SP
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import tool_snapshot_guard as G  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


CS = '''namespace X {
public static class T {
    [Tool("jawa/new_thing", Description = "d")]
    public static object NewThing(string defName, int count = 1) { return null; }
}}
'''

if len(sys.argv) == 3 and sys.argv[1] == "--instance":
    cs_dir, snap = sys.argv[2].split()
    found = G.pair(cs_dir, snap)
    check("instance: every [Tool] in %s is in %s" % (cs_dir, snap), not found, "missing: %s" % [n for n, _ in found])
    print("FAILED: %s" % FAILS if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)

# --- the pure check
check("fixture: absent tool is found", G.missing({"a.cs": CS}, set()) == [("jawa/new_thing", "a.cs")])
check("fixture: present tool passes", G.missing({"a.cs": CS}, {"jawa/new_thing"}) == [])
check("fixture: a file with no [Tool] passes", G.missing({"b.cs": "class Y {}"}, set()) == [])

# --- the real hook, in a throwaway repo
tmp = tempfile.mkdtemp(prefix="tsguard_")
try:
    def git(*a, env=None):
        return SP.run(["git", "-C", tmp] + list(a), capture_output=True, text=True, env=env)
    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t"); git("config", "user.name", "t")
    hooks = os.path.join(tmp, "hooks")
    os.makedirs(hooks)
    shutil.copy(os.path.join(ROOT, "infrastructure", "githooks", "pre-commit"), hooks)
    nd = os.path.join(tmp, "src", "RimMandrake", "Utils", "northstar_driver")
    os.makedirs(nd)
    for fn in ("tool_snapshot_guard.py", "tool_schemas.py"):
        shutil.copy(os.path.join(HERE, fn), nd)
    cs_dir = os.path.join(tmp, G.CS_DIR)
    os.makedirs(cs_dir)
    snap_path = os.path.join(tmp, G.SNAP)
    json.dump({"_source": "t", "tools": {}}, open(snap_path, "w"))
    open(os.path.join(tmp, "README"), "w").write("x\n")
    git("add", "-A")
    env = dict(os.environ, RUNNER_AI_COMMIT_OK="1")
    r = git("-c", "core.hooksPath=" + hooks, "commit", "-qm", "base", env=env)
    check("base commit (no [Tool]) passes the hook", r.returncode == 0, r.stderr[-200:])

    open(os.path.join(cs_dir, "NewTool.cs"), "w").write(CS)
    git("add", G.CS_DIR + "NewTool.cs")
    r = git("-c", "core.hooksPath=" + hooks, "commit", "-qm", "add tool", env=env)
    check("THE INSTANCE: a staged [Tool] without its snapshot entry is refused by pre-commit",
          r.returncode != 0 and "jawa/new_thing" in r.stderr, "(exit %d) %s" % (r.returncode, r.stderr[-200:]))

    json.dump({"_source": "t", "tools": {"jawa/new_thing": {"parameters": [], "required": []}}}, open(snap_path, "w"))
    open(os.path.join(tmp, "README"), "w").write("y\n")
    git("add", G.SNAP)
    r = git("-c", "core.hooksPath=" + hooks, "commit", "-qm", "add tool + snapshot", env=env)
    check("the same commit with the snapshot entry staged passes", r.returncode == 0, r.stderr[-200:])

    git("add", "README")
    r = git("-c", "core.hooksPath=" + hooks, "commit", "-qm", "readme", env=env)
    check("a commit touching no companion .cs passes", r.returncode == 0, r.stderr[-200:])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# --- the live tree: every [Tool] in source is in the committed snapshot (the nightly red's own clause, run here too)
found = G.pair(os.path.join(ROOT, G.CS_DIR), os.path.join(ROOT, G.SNAP))
check("repo: every companion [Tool] is in tool_schemas.json", not found, "missing: %s" % [n for n, _ in found][:8])

print("FAILED: %s" % FAILS if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
