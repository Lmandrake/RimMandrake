#!/usr/bin/env python3
"""Selftest: a mod's review and proof scripts never write relative to the caller's cwd (NORTHSTAR_PROCESS_RETRO_1).

GimmeSomeSlack/human_review.py crashed anywhere but the repo root because `--log` defaulted to "Transient/...". That was
the only live case, so the guard is this scan and not a run_from_root() helper. A default path built from REPO or HERE
passes; a bare "Transient/..." or os.path.join("Transient", ...) default fails.
"""
import ast
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROOTS = ("Transient", "infrastructure", "design", "src")
# In a hashed mod folder: fixing it would stale that mod's recorded run for a dev-only --out flag.
KNOWN = {"src/RimMandrake/GimmeSomeSlack/shader_sway_look.py"}
FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def relative_default(node):
    """True for a default that is a cwd-relative repo path, as a literal or an os.path.join of literals."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.replace("\\", "/").split("/")[0] in ROOTS and "/" in node.value.replace("\\", "/")
    if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "join" and node.args:
        first = node.args[0]
        return isinstance(first, ast.Constant) and first.value in ROOTS
    return False


def offenders(source):
    out = []
    for n in ast.walk(ast.parse(source)):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "add_argument":
            for k in n.keywords:
                if k.arg == "default" and relative_default(k.value):
                    out.append(n.lineno)
    return out


def t_detector():
    ok(offenders('ap.add_argument("--log", default=os.path.join("Transient", "x.md"))'), "catches os.path.join")
    ok(offenders('ap.add_argument("--log", default="Transient/x.md")'), "catches a literal")
    ok(not offenders('ap.add_argument("--log", default=os.path.join(REPO, "Transient", "x.md"))'), "passes REPO joins")
    ok(not offenders('ap.add_argument("--mode", default="design")'), "passes a plain word")


def t_tree():
    paths = []
    for pat in ("*/human_review.py", "*/validation*.py", "*/save_review_map.py", "*/review_map.py", "*/shader_sway_look.py",
                "*/northstar/*.py"):
        paths += glob.glob(os.path.join(REPO, "src", "RimMandrake", pat))
    ok(len(paths) >= 20, "the scan sees the tree (%d files)" % len(paths))
    found = {}
    for p in paths:
        with open(p, encoding="utf-8") as f:
            hits = offenders(f.read())
        if hits:
            found[os.path.relpath(p, REPO).replace(os.sep, "/")] = hits
    ok(set(found) <= KNOWN, "no new cwd-relative default: %s" % sorted(set(found) - KNOWN))
    ok(found.keys() >= KNOWN or not KNOWN, "the KNOWN list is not stale: %s" % sorted(KNOWN - set(found)))


if __name__ == "__main__":
    t_detector()
    t_tree()
    print("%d FAIL" % len(FAILS))
    sys.exit(1 if FAILS else 0)
