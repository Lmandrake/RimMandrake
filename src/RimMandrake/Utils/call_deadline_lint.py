#!/usr/bin/env python3
"""Lint: every blocking subprocess call carries a deadline; robocopy is bounded (CALL_DEADLINES_ENFORCE_130_OPEN_ENDED).

Design: design/RimMandrake/build_system_practices_2026-11-03.md, top-5 #2. A hung robocopy left on its
default /R:1000000 /W:30 held a seat for 4 h (2026-11-02); hangs never announce themselves.

Two rules, both by AST (comments and docstrings never trip them):

1. DEADLINE. Under SCAN_ROOTS (non-selftest .py), every subprocess.run / check_output / check_call / call
   passes `timeout=` (a `**kwargs` splat counts: the caller may pass it). Aliases are followed
   (`import subprocess as sp`, `from subprocess import run`). Calls that predate the lint sit on
   ALLOWLIST (call_deadline_allowlist.json), keyed by file + enclosing function + callee, with a count, so a
   line shift is not a change. A call beyond its allowance is RED. An EXTERNAL call (crosses into Windows or
   the network: git push/fetch/pull/clone, *.exe, powershell, cmd, robocopy, codex, claude, curl, ssh, gh,
   rsync, tailscale) may never be allowlisted. Every allowlist entry dies on the file's `burn_down_by`
   date: after it the lint is RED until the entry is fixed or removed.
2. ROBOCOPY. In every tracked .py, a subprocess call (Popen included) whose literal args name robocopy must
   pass /R:n with n<=5 and /W:n with n<=30, and run under `timeout=` (a retry bound alone does not bound
   the copy). Popen is refused for robocopy outright: nothing static proves its wait is bounded. In
   .ps1/.psm1/.sh/.cmd/.bat, a non-comment line invoking robocopy needs the same /R /W bounds, and a .sh
   line needs a `timeout N` prefix.

    python3 src/RimMandrake/Utils/call_deadline_lint.py            # report; exit 0 green, 1 red
    python3 src/RimMandrake/Utils/call_deadline_lint.py --prune    # drop allowlist slack (fixed calls)
    python3 src/RimMandrake/Utils/call_deadline_lint.py --census   # per-file counts of open calls
"""
import ast
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCAN_ROOTS = ("src/RimMandrake/rimflow", "src/RimMandrake/Utils")
ALLOWLIST = os.path.join(HERE, "call_deadline_allowlist.json")
BLOCKING = {"run", "check_output", "check_call", "call"}
SHELL_EXT = (".ps1", ".psm1", ".sh", ".cmd", ".bat")
R_MAX, W_MAX = 5, 30

EXTERNAL_WORDS = re.compile(
    r"(?:^|[\s/\\\"'])(?:powershell|pwsh|cmd|robocopy|codex|claude|curl|wget|ssh|scp|gh|rsync|tailscale|"
    r"wsl|winget|steamcmd)(?:\.exe)?(?=$|[\s\"'])|\.exe(?=$|[\s\"'])", re.I)
GIT_NET = {"push", "fetch", "pull", "clone", "ls-remote"}
ROBO_R = re.compile(r"/R:(\d+)", re.I)
ROBO_W = re.compile(r"/W:(\d+)", re.I)
ROBO_WORD = re.compile(r"\brobocopy(?:\.exe)?\b", re.I)


def _is_selftest(path):
    return os.path.basename(path).startswith("selftest")


def _subprocess_names(tree):
    """Names bound to the subprocess module, and bare names bound to its functions."""
    mods, funcs = {"subprocess"}, {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "subprocess":
                    mods.add(a.asname or a.name)
        elif isinstance(n, ast.ImportFrom) and n.module == "subprocess":
            for a in n.names:
                funcs[a.asname or a.name] = a.name
    return mods, funcs


def _callee(node, mods, funcs):
    f = node.func
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in mods:
        return f.attr
    if isinstance(f, ast.Name) and f.id in funcs:
        return funcs[f.id]
    return None


def _strings(node):
    """Every string literal inside an argument expression, in order."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return out


def _bounded(node):
    for k in node.keywords:
        if k.arg is None or k.arg == "timeout":
            return True
    return False


def _external(node):
    if not node.args:
        return False
    s = _strings(node.args[0])
    if not s:
        return False
    text = " ".join(s)
    if EXTERNAL_WORDS.search(text):
        return True
    words = text.split()
    if "git" in [os.path.basename(w) for w in words[:1]] or (s and s[0] == "git"):
        return any(w in GIT_NET for w in words[1:6])
    return False


class _Visitor(ast.NodeVisitor):
    def __init__(self, mods, funcs):
        self.mods, self.funcs, self.stack, self.calls = mods, funcs, [], []

    def _scope(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _scope

    def visit_Call(self, node):
        name = _callee(node, self.mods, self.funcs)
        if name:
            self.calls.append((".".join(self.stack) or "<module>", name, node))
        self.generic_visit(node)


def calls_in(path):
    """[(scope, callee, ast.Call)] for every subprocess call in one file; None if it does not parse."""
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src, filename=path)
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
        return None
    mods, funcs = _subprocess_names(tree)
    v = _Visitor(mods, funcs)
    v.visit(tree)
    return v.calls


def scan_deadlines(repo=REPO, roots=SCAN_ROOTS):
    """-> (total_blocking, open_calls[(rel, scope, callee, line, external)], unparsed[rel])."""
    total, opened, unparsed = 0, [], []
    for root in roots:
        for dp, dns, fns in os.walk(os.path.join(repo, root)):
            dns[:] = sorted(d for d in dns if d not in ("__pycache__", ".git"))
            for fn in sorted(fns):
                if not fn.endswith(".py") or _is_selftest(fn):
                    continue
                p = os.path.join(dp, fn)
                rel = os.path.relpath(p, repo).replace(os.sep, "/")
                calls = calls_in(p)
                if calls is None:
                    unparsed.append(rel)
                    continue
                for scope, callee, node in calls:
                    if callee not in BLOCKING:
                        continue
                    total += 1
                    if not _bounded(node):
                        opened.append((rel, scope, callee, node.lineno, _external(node)))
    return total, opened, unparsed


def _key(rel, scope, callee):
    return "%s::%s::%s" % (rel, scope, callee)


def load_allowlist(path=ALLOWLIST):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {"burn_down_by": None, "calls": {}}


def check_deadlines(opened, allow, today=None):
    """-> list of red messages."""
    today = today or _dt.date.today()
    reds = []
    allowed = allow.get("calls", {})
    burn = allow.get("burn_down_by")
    if allowed and burn and today > _dt.date.fromisoformat(burn):
        reds.append("burn-down date %s passed with %d allowlisted call(s) still open"
                    % (burn, sum(allowed.values())))
    seen = Counter()
    for rel, scope, callee, line, ext in opened:
        k = _key(rel, scope, callee)
        seen[k] += 1
        if ext:
            reds.append("%s:%d %s() crosses into Windows/network with no timeout= (never allowlisted)"
                        % (rel, line, callee))
        elif seen[k] > allowed.get(k, 0):
            reds.append("%s:%d %s() in %s has no timeout= (new call: pass timeout=)" % (rel, line, callee, scope))
    return reds


def slack(opened, allow):
    """Allowlist entries larger than what is still open (calls fixed since)."""
    seen = Counter(_key(r, s, c) for r, s, c, _l, ext in opened if not ext)
    return {k: (v, seen.get(k, 0)) for k, v in allow.get("calls", {}).items() if seen.get(k, 0) < v}


def _robo_bounds(text):
    r, w = ROBO_R.search(text), ROBO_W.search(text)
    errs = []
    if not r or int(r.group(1)) > R_MAX:
        errs.append("/R:<=%d" % R_MAX)
    if not w or int(w.group(1)) > W_MAX:
        errs.append("/W:<=%d" % W_MAX)
    return errs


def robocopy_py(path, rel):
    reds = []
    for scope, callee, node in calls_in(path) or []:
        text = " ".join(s for a in node.args + [k.value for k in node.keywords] for s in _strings(a))
        if not ROBO_WORD.search(text):
            continue
        need = _robo_bounds(text)
        if callee == "Popen":
            need.append("subprocess.run(..., timeout=) instead of Popen")
        elif not _bounded(node):
            need.append("timeout=")
        if need:
            reds.append("%s:%d robocopy needs %s" % (rel, node.lineno, ", ".join(need)))
    return reds


def robocopy_shell(path, rel):
    reds = []
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return reds
    for i, line in enumerate(lines, 1):
        code = line.strip()
        if not code or code.startswith(("#", "REM ", "rem ", "::")) or not ROBO_WORD.search(code):
            continue
        need = _robo_bounds(code)
        if rel.endswith(".sh") and not re.search(r"\btimeout\s+(-\S+\s+)*\d", code):
            need.append("a `timeout N` prefix")
        if need:
            reds.append("%s:%d robocopy needs %s" % (rel, i, ", ".join(need)))
    return reds


def tracked_files(repo=REPO):
    out = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        return None
    return [f for f in out.stdout.split("\0") if f]


def scan_robocopy(repo=REPO, files=None):
    files = tracked_files(repo) if files is None else files
    if files is None:
        return None
    reds = []
    for rel in files:
        p = os.path.join(repo, rel)
        if rel.endswith(".py"):
            try:
                if "robocopy" not in open(p, encoding="utf-8", errors="replace").read().lower():
                    continue
            except OSError:
                continue
            reds += robocopy_py(p, rel)
        elif rel.lower().endswith(SHELL_EXT):
            reds += robocopy_shell(p, rel)
    return reds


def main(argv):
    total, opened, unparsed = scan_deadlines()
    if total == 0:
        print("UNMEASURED: no subprocess call found under %s (the scan is blind)" % ", ".join(SCAN_ROOTS))
        return 2
    allow = load_allowlist()
    if "--census" in argv:
        by = Counter(r for r, *_ in opened)
        for rel, n in by.most_common():
            print("%4d  %s" % (n, rel))
    if "--prune" in argv:
        calls = allow.get("calls", {})
        for k, (_was, now) in slack(opened, allow).items():
            if now:
                calls[k] = now
            else:
                calls.pop(k)
        allow["calls"] = dict(sorted(calls.items()))
        with open(ALLOWLIST, "w", encoding="utf-8") as fh:
            json.dump(allow, fh, indent=1)
            fh.write("\n")
    reds = check_deadlines(opened, allow)
    robo = scan_robocopy()
    if robo is None:
        reds.append("UNMEASURED robocopy scan: git ls-files failed")
    else:
        reds += robo
    ext = sum(1 for o in opened if o[4])
    print("deadline lint: %d blocking subprocess calls, %d without timeout= (%d external), %d allowlisted, "
          "burn-down %s" % (total, len(opened), ext, sum(allow.get("calls", {}).values()), allow.get("burn_down_by")))
    for u in unparsed:
        print("  note: did not parse %s" % u)
    for r in reds:
        print("RED " + r)
    print("RESULT: %s" % ("RED %d" % len(reds) if reds else "GREEN"))
    return 1 if reds else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
