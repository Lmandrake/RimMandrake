#!/usr/bin/env python3
r"""Selftest: rmpaths.py is the one data root, and no code names the old D:\Luke\dev\_<dir> layout.

Owner, 2026-10-19: *"stop putting things in Luke\dev\_(filename) directories ... dev is my special
directory for Lodestar-managed projects"*. The dirs moved to the data root on 2026-10-20; this keeps
a new hard-wired `/mnt/d/Luke/dev/_rmscratch` (or any sibling) from growing back.

    python3 src/RimMandrake/Utils/selftest_rmpaths.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import rmpaths  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("ok    " if cond else "FAIL  ") + name + ("" if cond else "\n        " + detail))
    if not cond:
        FAILS.append(name)


def resolve(env, lodestar=""):
    rmpaths._resolve.cache_clear()
    return rmpaths._resolve(env, lodestar)


check("env wins", resolve("/x/data") == "/x/data")
try:
    resolve("/mnt/d/Luke/dev/_rmscratch")
    check("a root inside Luke/dev is refused", False, "accepted")
except rmpaths.RmDataRootUnset:
    check("a root inside Luke/dev is refused", True)
check("windows translation", rmpaths.to_win("/mnt/d/ClaudeWork/rimmandrake/scratch/a") ==
      "D:\\ClaudeWork\\rimmandrake\\scratch\\a")
try:
    rmpaths.rm_path("_rmscratch")
    check("old-style _name refused", False, "accepted")
except ValueError:
    check("old-style _name refused", True)
rmpaths._resolve.cache_clear()
if os.path.isfile(rmpaths.AGENT_STORAGE) or os.environ.get(rmpaths.ENV_VAR):
    r = str(rmpaths.rm_data_root())
    check("live root resolves outside dev", "luke/dev" not in r.replace("\\", "/").lower(), r)

# A Windows-form root under POSIX python (live 2026-11-26: AGENT_STORAGE_ROOT='D:\\ClaudeWork' in a WSL shell made the
# root the RELATIVE path 'D:\\ClaudeWork/rimmandrake'; game_lock then wrote an ArchSmall claim into that folder inside the
# clone, a lock no other process reads). POSIX translates a drive path to /mnt/<d>/...; a relative root is refused.
if not rmpaths.IS_WIN:
    check("posix: a drive-form env root becomes /mnt/<d>",
          resolve("D:\\ClaudeWork\\rimmandrake") == "/mnt/d/ClaudeWork/rimmandrake", resolve("D:\\ClaudeWork\\rimmandrake"))
    check("posix: a drive-form helper answer becomes /mnt/<d>",
          rmpaths._check("D:\\ClaudeWork/rimmandrake") == "/mnt/d/ClaudeWork/rimmandrake")
    try:
        resolve("scratch/rimmandrake")
        check("posix: a relative root is refused", False, "accepted")
    except rmpaths.RmDataRootUnset:
        check("posix: a relative root is refused", True)
    if os.path.isfile(rmpaths.AGENT_STORAGE):
        # the live shape: Lodestar's helper abspaths the raw value against cwd, so the env goes in translated
        _keep = {k: os.environ.get(k) for k in (rmpaths.CACHE_ENV, rmpaths.LODESTAR_ENV)}
        os.environ[rmpaths.CACHE_ENV] = ""
        os.environ[rmpaths.LODESTAR_ENV] = "D:\\ClaudeWork"
        try:
            got = resolve("", "D:\\ClaudeWork")
        except rmpaths.RmDataRootUnset as e:
            got = "refused: %s" % e
        finally:
            for k, v in _keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        check("posix: a drive-form AGENT_STORAGE_ROOT reaches the helper as /mnt/<d>",
              got == "/mnt/d/ClaudeWork/rimmandrake", got)
rmpaths._resolve.cache_clear()

DEV = "/mnt/d/Luke/dev"
if os.path.isdir(DEV):
    left = sorted(n for n in os.listdir(DEV) if n.startswith("_"))
    check("no D:\\Luke\\dev\\_* dir is left", not left, ", ".join(left))

pat = r"Luke[/\\]+dev[/\\]+_(artpipe|artstore|obs|rmbuild|rmdashboard|rmscratch)"
out = subprocess.run(["git", "-C", ROOT, "grep", "-nIE", pat, "--", "src", "skills", "CLAUDE.md",
                      ":!*.md", ":!*.json", ":!*.jsonl", ":!*.log", ":!**/selftest_rmpaths.py"],
                     capture_output=True, text=True).stdout.strip()
check("no code names D:\\Luke\\dev\\_<dir>", not out, out[:800])
# a skill's references/history.md is a dated design record of its day (35334f9a85), not guidance
out = subprocess.run(["git", "-C", ROOT, "grep", "-nIE", pat, "--", "CLAUDE.md", "skills",
                      ":!skills/*/references/history.md"],
                     capture_output=True, text=True).stdout.strip()
check("CLAUDE.md and skills name no old dir", not out, out[:800])

print("OK" if not FAILS else "%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
