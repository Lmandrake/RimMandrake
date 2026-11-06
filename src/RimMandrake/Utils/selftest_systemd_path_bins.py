#!/usr/bin/env python3
"""selftest_systemd_path_bins.py -- no tracked script runs a ~/.local/bin command by bare name (OPS_TIMER_REPAIR_PRXC).

A systemd user unit, and every `systemd-run --user` one-shot, starts with the manager's bare PATH, which lacks
~/.local/bin, where `claude`, `claude-account`, `gh`, `rimflow`, `modcheck` and friends live. A bare
`subprocess.run(["claude", ...])` works from a shell and dies FileNotFoundError under a timer, which is a failed
unit and a TIMER_FAILED alarm: rm-agent-improve 2026-11-03 (5f5406e957), account_handover 2026-11-05 (f8a59e9df7).
So the rule is on the call: an argv whose first word is a ~/.local/bin name must be a resolved path
(`shutil.which(name) or os.path.expanduser("~/.local/bin/" + name)`), never the bare literal.

    python3 selftest_systemd_path_bins.py               scan every tracked .py (selftests and arena excluded)
    python3 selftest_systemd_path_bins.py FILE ...      scan only these files (replaying an instance)
"""
import ast
import os
import subprocess
import sys
import warnings

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
# Commands that live only in ~/.local/bin on Archmagi (`ls ~/.local/bin`, 2026-11-06), not on systemd's default PATH.
LOCAL_BIN_ONLY = {"claude", "claude-account", "claude-account-switch", "rimflow", "modcheck", "gh", "jj", "restic",
                  "node", "npm", "npx", "nemo", "playwright"}
RUNNERS = {"run", "Popen", "check_output", "check_call", "call", "sh", "_sh", "_run", "execvp", "execv"}
SKIP_DIRS = ()


def _name(func):
    return func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")


def _bare(node):
    """-> the ~/.local/bin name this argv node starts with as a bare literal, or None."""
    if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
        node = node.elts[0]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        word = node.value.split(" ")[0]
        return word if word in LOCAL_BIN_ONLY else None
    return None


def bare_calls(text):
    """-> [(line, name)] for every argv in `text` that starts with a bare ~/.local/bin command."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tree = ast.parse(text)
    hits = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _name(n.func) in RUNNERS and n.args:
            w = _bare(n.args[0])
            if w:
                hits.append((n.lineno, w))
        elif isinstance(n, ast.Assign) and isinstance(n.value, ast.List) and _bare(n.value):   # a tuple is a label set, not an argv
            hits.append((n.lineno, _bare(n.value)))
    return sorted(set(hits))


def tracked():
    out = subprocess.run(["git", "ls-files", "src", "infrastructure", "skills"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.split()
    return [f for f in out if f.endswith(".py") and not os.path.basename(f).startswith("selftest")
            and not f.startswith(SKIP_DIRS)]


def scan(paths):
    bad = []
    for p in paths:
        full = p if os.path.isabs(p) else os.path.join(ROOT, p)
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
            hits = bare_calls(text)
        except (OSError, SyntaxError):
            continue
        bad += ["%s:%d runs %r by bare name" % (p, line, w) for line, w in hits]
    return bad


def self_check():
    """The instrument sees: the account_handover call that failed, and passes a resolved one."""
    assert bare_calls('sh("claude-account", "--json", "status")') == [(1, "claude-account")]
    assert bare_calls('subprocess.run(["claude", "-p", x])') == [(1, "claude")]
    assert bare_calls('cmd = ["gh", "api", k]') == [(1, "gh")]
    assert bare_calls('subprocess.run([CLAUDE, "-p", x])') == []
    assert bare_calls('subprocess.run(["python3", "x.py"])') == []
    assert bare_calls('d = {"claude": 1}; s.pawns["rescue"] = 2') == []
    assert bare_calls('KIND_ORDER = ("claude", "codex")') == []


def main(argv):
    self_check()
    files = argv or tracked()
    if not argv:
        assert len(files) > 200, "only %d tracked .py files: git ls-files is not seeing the repo" % len(files)
    bad = scan(files)
    for b in bad:
        print("FAIL " + b)
    if bad:
        print("FAIL %d bare ~/.local/bin call(s): systemd's PATH lacks ~/.local/bin; resolve the path" % len(bad))
        return 1
    print("PASS %d files, no bare ~/.local/bin command" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
