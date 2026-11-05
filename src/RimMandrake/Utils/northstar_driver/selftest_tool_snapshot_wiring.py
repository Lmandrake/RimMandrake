#!/usr/bin/env python3
"""Live-wiring proof for NIGHTLY_COP_FIX_RED_LMTEZQ_YAXX: the tool-snapshot pre-commit guard is a GIT hook, so it is
alive only if every clone the project makes points core.hooksPath at infrastructure/githooks, the hook file is
executable (git silently skips a non-executable hook), and the hook runs tool_snapshot_guard.py --staged and passes its
refusal on. selftest_tool_snapshot_guard.py proves the hook's behaviour; this proves the wiring a Claude settings.json
`hook=` live line cannot see.

    python3 src/RimMandrake/Utils/northstar_driver/selftest_tool_snapshot_wiring.py [--root <repo>]

Each check is also run on a broken copy of its input (mutant) and must go red there. Offline; no git history.
"""
import os
import re
import stat
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FAILS = []

CLONE_MAKERS = ["src/RimMandrake/Utils/scratch_clone.py", "src/RimMandrake/Utils/ledger_sync.py"]
HOOK = "infrastructure/githooks/pre-commit"
SET_HOOKS = re.compile(r"""git\([^)]*["']config["']\s*,\s*["']core\.hooksPath["']\s*,\s*["']infrastructure/githooks["']""")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def sets_hooks_path(text):
    """True when the source sets core.hooksPath=infrastructure/githooks on the clone it makes (not in a comment)."""
    code = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    return bool(SET_HOOKS.search(code))


def hook_runs_guard(text):
    """True when the hook runs tool_snapshot_guard.py --staged and exits non-zero on its refusal (exit 1)."""
    lines = [l for l in text.splitlines() if not l.lstrip().startswith("#")]
    body = "\n".join(lines)
    names = re.search(r'^\s*t="\$root/src/RimMandrake/Utils/northstar_driver/tool_snapshot_guard\.py"\s*$', body, re.M)
    runs = re.search(r'^\s*python3 "\$t" --staged "\$root"\s*$', body, re.M)
    passes_on = re.search(r'^\s*\[ "\$r" -ne 0 \] && exit \$r\s*$', body, re.M)
    return bool(names and runs and passes_on)


def is_executable(mode):
    return bool(mode & stat.S_IXUSR)


def main(argv):
    root = ROOT
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    for rel in CLONE_MAKERS:
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            text = f.read()
        check("%s sets core.hooksPath=infrastructure/githooks" % rel, sets_hooks_path(text))
        mutant = text.replace('"infrastructure/githooks"', '"infrastructure/githooks_x"')
        check("  mutant (wrong hooks dir) of %s goes red" % rel, not sets_hooks_path(mutant))
        commented = "\n".join(("# " + l) if SET_HOOKS.search(l) else l for l in text.splitlines())
        check("  mutant (setter commented out) of %s goes red" % rel, not sets_hooks_path(commented))
    hook = os.path.join(root, HOOK)
    with open(hook, encoding="utf-8") as f:
        text = f.read()
    check("%s runs tool_snapshot_guard.py --staged and exits on its refusal" % HOOK, hook_runs_guard(text))
    check("  mutant (guard call removed) goes red",
          not hook_runs_guard(text.replace('python3 "$t" --staged "$root"', 'true')))
    check("  mutant (refusal swallowed) goes red",
          not hook_runs_guard(text.replace('[ "$r" -ne 0 ] && exit $r', '[ "$r" -ne 0 ] && r=0')))
    check("  mutant (guard path renamed) goes red",
          not hook_runs_guard(text.replace("tool_snapshot_guard.py", "tool_snapshot_guardX.py")))
    mode = os.stat(hook).st_mode
    check("%s is executable (git skips a non-executable hook silently)" % HOOK, is_executable(mode), oct(mode))
    check("  mutant (exec bit cleared) goes red", not is_executable(mode & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)))
    check("guard script exists", os.path.isfile(os.path.join(root, "src/RimMandrake/Utils/northstar_driver/tool_snapshot_guard.py")))
    print("FAILED: %s" % FAILS if FAILS else "RESULT: PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
