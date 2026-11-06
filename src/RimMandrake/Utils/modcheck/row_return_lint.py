#!/usr/bin/env python3
"""Find `return` statements that cut a validation chain short (VALIDATION_ROWRETURN_AUDIT_CHAINS_CUT_SHORT).

A chain function records one row per `with t.component(...)` (or a mod's `_comp(...)` wrapper) block. A `return`
inside a row leaves the whole FUNCTION, not the row: every later row is never recorded, live or in the offline
`components_declared()` probe that builds required_checks.json. A PASS-path return silently drops independent rows
(TrophyCraft's crafting chain, TROPHYCRAFT_VALIDATION_FIX_SKIPPED_ROWS).

A finding is a `return` that sits inside a row block (directly, not inside a nested def/lambda/class) when the same
function still has a row after it: a row block that starts later in the source, or the row itself sits in a loop.
The fix is to move the row's body into its own function, so its `return` ends that row only.

    python3 src/RimMandrake/Utils/modcheck/row_return_lint.py            # every validation.py under src/, exit 1 on any
    python3 src/RimMandrake/Utils/modcheck/row_return_lint.py <file>...  # just these
    --count                                                               # per-file counts only
"""
import ast
import os
import sys

ROW_CALLS = {"component", "_comp"}
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
_LOOPS = (ast.For, ast.AsyncFor, ast.While)


def _row_name(withnode):
    for item in withnode.items:
        c = item.context_expr
        if isinstance(c, ast.Call):
            f = c.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if name in ROW_CALLS:
                return name
    return None


def _walk_scope(node):
    """Every node under `node` that belongs to the same function scope (stops at nested defs/lambdas/classes)."""
    for child in ast.iter_child_nodes(node):
        yield child
        if not isinstance(child, _SCOPES):
            for sub in _walk_scope(child):
                yield sub


def _rows_with_loop_flag(fn):
    """(withnode, in_loop) for every row block in fn's own scope."""
    out = []

    def visit(node, in_loop):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, _SCOPES):
                continue
            here = in_loop or isinstance(node, _LOOPS)
            if isinstance(child, (ast.With, ast.AsyncWith)) and _row_name(child):
                out.append((child, here))
            visit(child, here)
    visit(fn, False)
    return out


def findings(path):
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        rows = _rows_with_loop_flag(fn)
        if not rows:
            continue
        starts = sorted(w.lineno for w, _ in rows)
        seen = set()
        for w, in_loop in rows:
            end = getattr(w, "end_lineno", w.lineno)
            later = any(s > end for s in starts) or in_loop
            if not later:
                continue
            for node in _walk_scope(w):
                if isinstance(node, ast.Return) and node.lineno not in seen:
                    seen.add(node.lineno)
                    out.append((node.lineno, fn.name))
    return sorted(set(out))


def validation_files(root=None):
    root = root or os.path.join(REPO, "src")
    found = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", "Source", "obj", "bin", "__pycache__")]
        if "validation.py" in files:
            found.append(os.path.join(d, "validation.py"))
    return sorted(found)


def main(argv):
    count = "--count" in argv
    paths = [a for a in argv if not a.startswith("--")] or validation_files()
    total, files = 0, 0
    for p in paths:
        f = findings(p)
        if not f:
            continue
        files += 1
        total += len(f)
        rel = os.path.relpath(p, REPO)
        if count:
            print("%4d  %s" % (len(f), rel))
        else:
            for line, fn in f:
                print("%s:%d: return inside a non-final row of %s() ends the chain" % (rel, line, fn))
    print("row_return_lint: %d finding(s) in %d file(s) of %d scanned" % (total, files, len(paths)))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
