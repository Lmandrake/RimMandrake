#!/usr/bin/env python3
"""Lint: "could not look" read as "nothing there" in pipeline code (RIMMANDRAKE_SHARE_PROBE_RESULT_TYPE_NINE_FILES_ROLL_OWN).

Page: design/specs/2026-11-19-probe-result/boundary.md; design 01-design.md §5.5 part 2 (review-growth-cycle). Built like
call_deadline_lint.py. In the .py files matched by `pipeline_files` in pipeline_tests.json (selftests skipped), two
shapes are found by AST (comments and docstrings never trip them):

  or-empty               `<call> or []`, also `{}`, `()`, `0`, `None`, `""`, `list()`/`dict()`/`set()`: a read that
                         fails or finds nothing becomes the same empty answer. A `.get(...)` on the left reads a mapping
                         already in hand and is not flagged; neither is a name or an attribute.
  except-returns-empty   an `except` whose body returns one of those empty values.

A place that predates the lint sits on ALLOWLIST (could_not_look_allowlist.json), keyed by file + enclosing function +
shape, with a count, so a line moving inside its function is not a change. A hit beyond its count is RED. A count is
a list of places to read, not a count of bugs: the shared answer type for a read is probe_result.py.

    python3 src/RimMandrake/Utils/could_not_look_lint.py              exit 0 green, 1 red, 3 UNREADABLE
    ... --shadow     print the same, exit 0 always (a hand look; ./publish runs the lint refusing since
                     RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED, 2026-11-19)
    ... --census     per-file counts of every place, allowlisted or not
    ... --prune      drop allowlist slack (places fixed since), and the `reasons` entry of a place no longer allowed
    ... --seed       write every current place onto the allowlist (once, at the lint's birth)
    ... --files P... only these files; --allowlist PATH another allowlist
"""
import ast
import glob
import itertools
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PIPELINE_TESTS = os.path.join(HERE, "pipeline_tests.json")
ALLOWLIST = os.path.join(HERE, "could_not_look_allowlist.json")
EMPTY_CALLS = {"list", "dict", "set", "tuple", "str"}
DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def _empty(n):
    if isinstance(n, ast.Constant):
        v = n.value
        return v is None or v == "" or (type(v) in (int, float, bool) and v == 0)
    if isinstance(n, (ast.List, ast.Tuple, ast.Set)):
        return not n.elts
    if isinstance(n, ast.Dict):
        return not n.keys
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in EMPTY_CALLS
            and not n.args and not n.keywords)


def _read_call(n):
    """A call that may read the outside world. Not: `.get(...)` (a mapping in hand), `getattr(...)` (an object in hand),
    or a string constant's `.join(...)` (lint reads, 2026-11-19: seat_restart.bridge_hold, designer_stage.done_items)."""
    if not isinstance(n, ast.Call):
        return False
    f = n.func
    if isinstance(f, ast.Attribute):
        return not (f.attr == "get" or (f.attr == "join" and isinstance(f.value, ast.Constant)
                                        and isinstance(f.value.value, str)))
    return not (isinstance(f, ast.Name) and f.id == "getattr")


def _returns(nodes):
    """Return statements under these nodes, not inside a nested def or lambda."""
    for n in nodes:
        if isinstance(n, DEFS):
            continue
        if isinstance(n, ast.Return):
            yield n
        yield from _returns(ast.iter_child_nodes(n))


def _walk(node, scope, out):
    for n in ast.iter_child_nodes(node):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            _walk(n, scope + [n.name], out)
            continue
        where = ".".join(scope) or "<module>"
        if isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or) and _empty(n.values[-1]) \
                and any(_read_call(v) for v in n.values[:-1]):
            out.add((n.lineno, where, "or-empty"))
        if isinstance(n, ast.ExceptHandler):
            out.update((r.lineno, where, "except-returns-empty") for r in _returns(n.body)
                       if r.value is not None and _empty(r.value))
        _walk(n, scope, out)


def places_in(path):
    """-> sorted [(line, scope, shape)] in one file. Raises SyntaxError/OSError/ValueError when it cannot be read."""
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    out = set()
    _walk(tree, [], out)
    return sorted(out)


def pipeline_py(repo=REPO):
    """-> the repo-relative non-selftest .py files pipeline_files names. Raises OSError/ValueError/KeyError."""
    with open(os.path.join(repo, os.path.relpath(PIPELINE_TESTS, REPO)), encoding="utf-8") as fh:
        globs = json.load(fh)["pipeline_files"]
    files = {os.path.relpath(p, repo).replace(os.sep, "/") for g in globs for p in glob.glob(os.path.join(repo, g))}
    return sorted(f for f in files if f.endswith(".py") and not os.path.basename(f).startswith("selftest"))


def _rel(path):
    a = os.path.abspath(path)
    return os.path.relpath(a, REPO).replace(os.sep, "/") if a.startswith(REPO + os.sep) else a


def load_allowlist(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:   # no allowlist written yet: nothing is allowed, which is an answer
        return {"places": {}}


def main(argv):
    shadow = "--shadow" in argv
    al_path = argv[argv.index("--allowlist") + 1] if "--allowlist" in argv else ALLOWLIST
    if "--files" in argv:
        files = [_rel(f) for f in itertools.takewhile(lambda a: not a.startswith("--"),
                                                       argv[argv.index("--files") + 1:])]
    else:
        try:
            files = pipeline_py()
        except (OSError, ValueError, KeyError) as e:
            print("UNREADABLE %s: %s" % (PIPELINE_TESTS, e))
            print("RESULT%s: UNREADABLE, nothing linted" % (" (SHADOW, refuses nothing)" if shadow else ""))
            return 0 if shadow else 3
    found, unreadable = {}, []
    for rel in files:
        try:
            found[rel] = places_in(rel if os.path.isabs(rel) else os.path.join(REPO, rel))
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as e:
            unreadable.append((rel, e))
    allow = load_allowlist(al_path)
    allowed = allow.setdefault("places", {})
    seen, reds = Counter(), []
    for rel, ps in found.items():
        for line, scope, shape in ps:
            k = "%s::%s::%s" % (rel, scope, shape)
            seen[k] += 1
            if seen[k] > allowed.get(k, 0):
                reds.append("NEW %s:%d %s in %s" % (rel, line, shape, scope))
    if "--census" in argv:
        for rel, ps in sorted(found.items(), key=lambda x: (-len(x[1]), x[0])):
            if ps:
                print("%4d  %s" % (len(ps), rel))
    if "--seed" in argv or "--prune" in argv:
        mine = {k for k in allowed if k.split("::")[0] in found}
        for k in mine | set(seen):
            n = seen.get(k, 0) if "--seed" in argv else min(allowed.get(k, 0), seen.get(k, 0))
            if n:
                allowed[k] = n
            else:
                allowed.pop(k, None)
        allow["places"] = dict(sorted(allowed.items()))
        if "reasons" in allow:      # a place no longer allowed takes its reason with it
            allow["reasons"] = {k: v for k, v in sorted(allow["reasons"].items()) if k in allowed}
        with open(al_path, "w", encoding="utf-8") as fh:
            json.dump(allow, fh, indent=1)
            fh.write("\n")
        reds = [] if "--seed" in argv else reds
    for rel, e in unreadable:
        print("UNREADABLE %s: %s" % (rel, e))
    for r in reds:
        print(r)
    total = sum(seen.values())
    rc = 3 if unreadable else (1 if reds else 0)
    print("RESULT%s: %s; %d places in %d of %d files, %d beyond the allowlist (%d allowed)"
          % (" (SHADOW, refuses nothing)" if shadow else "", {0: "GREEN", 1: "RED", 3: "UNREADABLE"}[rc], total,
             sum(1 for ps in found.values() if ps), len(files), len(reds), sum(allowed.values())))
    return 0 if shadow else rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
