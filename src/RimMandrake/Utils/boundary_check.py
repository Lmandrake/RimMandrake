#!/usr/bin/env python3
"""boundary_check.py — every promise on a boundary page has a test of the same name.

Owner by card 2026-11-18 (`design/RimMandrake/standing_rulings.md` §A boundary page before pipeline code; design
`design/specs/2026-11-18-review-growth-cycle/01-design.md` §5.2). A page's `## PROMISES` and `## SURVIVES` sections list
entries `- **some-name.** ...`; each is owed a module-level test `t_some_name` (a def, or a name bound to one) in the
page's tests file, which that file's `main()` runs (names it, or the def it is bound to). `## DOES NOT SURVIVE`,
`## ACCEPTS` and `## LIFE CYCLES` entries are not promises.

  boundary_check.py <boundary.md> --tests <selftest.py>    one page
  boundary_check.py                                        every design/specs/*/boundary.md (what ./publish runs on a
                                                           change to one, pipeline_tests.json); each must have its
                                                           row in boundary_pages.json, the page list beside this file

Exit 0: `promises covered N of N`. 1: a promise has no test, or one `main()` never runs (each named; `promises covered
N of M`). 3: UNREADABLE, the page or tests file could not be read or parsed, its `main()` is absent or a promised
test runs only with a runtime CLI option (`runtime_optional_test_counted`), its test selection is dynamic, a page has
no row in boundary_pages.json, or that file cannot be read (cause named, no count printed). 4: NO PROMISES, the page
lists none.
"""
import argparse
import ast
import glob
import json
import os
import re
import sys

TOP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PAGES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boundary_pages.json")


SECTIONS = ("PROMISES", "SURVIVES")
HEAD_RX = re.compile(r"^##\s+(\S+)")
ENTRY_RX = re.compile(r"^- \*\*(.+?)[.:]?\*\*")


class Unreadable(Exception):
    pass


def load_pages(path):
    """-> {page: tests file}, repo-relative, from the data file at `path` (a JSON object; a key that starts with `_` is
    prose). Raises Unreadable, the cause named, when the file cannot be read or parsed, is not an object, names a page
    twice, or gives a tests file that is not a non-empty string."""
    def no_twins(pairs):
        seen = {}
        for k, v in pairs:
            if k in seen:
                raise Unreadable("%s: page %s is named twice" % (path, k))
            seen[k] = v
        return seen
    try:
        with open(path, encoding="utf-8") as f:
            rows = json.load(f, object_pairs_hook=no_twins)
    except (OSError, ValueError) as e:
        raise Unreadable("%s: %s" % (path, e))
    if not isinstance(rows, dict):
        raise Unreadable("%s: not a JSON object of page -> tests file" % path)
    pages = {}
    for k, v in rows.items():
        if k.startswith("_"):
            continue
        if not isinstance(v, str) or not v:
            raise Unreadable("%s: page %s has no tests file (got %r)" % (path, k, v))
        pages[k] = v
    return pages


# page -> its tests file, repo-relative, from PAGES_FILE. A new boundary page adds its row there, not here.
# PAGES_UNREADABLE holds the cause when the data file cannot be read; main() then answers UNREADABLE (exit 3).
try:
    PAGES, PAGES_UNREADABLE = load_pages(PAGES_FILE), None
except Unreadable as _e:
    PAGES, PAGES_UNREADABLE = {}, str(_e)


def promises(page):
    """-> the page's promise and SURVIVES entry names, in order. Raises Unreadable."""
    try:
        with open(page, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable("%s: %s" % (page, e))
    out, cur, seen = [], None, False
    for ln in lines:
        h = HEAD_RX.match(ln)
        if h:
            cur = h.group(1).upper()
            seen = seen or cur == "PROMISES"
            continue
        m = ENTRY_RX.match(ln) if cur in SECTIONS else None
        if m:
            out.append(m.group(1).strip())
    if not seen:
        raise Unreadable("%s: no `## PROMISES` section, so it is not a boundary page this tool can read" % page)
    return out


def test_name(promise):
    return "t_" + re.sub(r"[^a-z0-9]+", "_", promise.lower().replace("'", "")).strip("_")


def _offline_names(main):
    """Names referenced by main() with no explicit CLI option, for direct flag guards."""
    argv = {arg.arg for arg in main.args.posonlyargs + main.args.args + main.args.kwonlyargs}
    parsed = {t.id for n in ast.walk(main) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
              and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "parse_args"
              for t in n.targets if isinstance(t, ast.Name)}

    def default(test):
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            value = default(test.operand)
            return None if value is None else not value
        if isinstance(test, ast.Attribute) and isinstance(test.value, ast.Name) and test.value.id in parsed:
            return False
        if isinstance(test, ast.Compare) and len(test.ops) == 1:
            parts = list(ast.walk(test))
            if (any(isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith("--") for n in parts)
                    and any((isinstance(n, ast.Name) and n.id in argv) or
                            (isinstance(n, ast.Attribute) and n.attr == "argv") for n in parts)):
                if isinstance(test.ops[0], (ast.In, ast.Eq)):
                    return False
                if isinstance(test.ops[0], (ast.NotIn, ast.NotEq)):
                    return True
        return None

    def names(node):
        if isinstance(node, ast.Name):
            yield node.id
        if isinstance(node, ast.If):
            value = default(node.test)
            if value is not None:
                yield from names(node.test)
                for child in node.body if value else node.orelse:
                    yield from names(child)
                return
        for child in ast.iter_child_nodes(node):
            yield from names(child)

    return set(names(main))


def tests_in(path, promised=()):
    """-> (module-level names bound to a function: `def t_x` or `t_x = t_y`, the subset `main()` runs). Raises
    Unreadable when there is no `main()`, it picks its tests at run time, or a name in `promised` is CLI-only."""
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), path)
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as e:
        raise Unreadable("%s: %s" % (path, e))
    defs = {n.name: n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Name) and n.value.id in defs:
            defs.update((t.id, defs[n.value.id]) for t in n.targets if isinstance(t, ast.Name))
    main = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"]
    if not main:
        raise Unreadable("%s: no main(), so which tests it runs cannot be read" % path)
    used = {x.id for x in ast.walk(main[-1]) if isinstance(x, ast.Name)}
    dynamic = used & {"globals", "locals", "vars", "getattr"}
    if dynamic:
        raise Unreadable("%s: main() picks its tests at run time (%s), so which run cannot be read"
                         % (path, ", ".join(sorted(dynamic))))
    ran = {defs[u] for u in _offline_names(main[-1]) if u in defs}
    optional = {defs[u] for u in used if u in defs} - ran
    guarded = sorted(n for n in promised if defs.get(n) in optional)
    if guarded:
        raise Unreadable("%s: main() selects %s at run time through a CLI option" % (path, ", ".join(guarded)))
    return set(defs), {n for n, d in defs.items() if d in ran}


def check(page, tests):
    """-> exit code, printing the verdict for one page."""
    try:
        names = promises(page)
        have, run = tests_in(tests, map(test_name, names))
    except Unreadable as e:
        print("UNREADABLE %s" % e)
        return 3
    if not names:
        print("NO PROMISES on %s: its PROMISES section lists no `- **name.**` entry" % page)
        return 4
    missing = [p for p in names if test_name(p) not in run]
    for p in missing:
        print("FAIL promise %s: %s %s in %s" % (p, "main() never runs test" if test_name(p) in have else "no test",
                                                test_name(p), tests))
    print("promises covered %d of %d  (%s)" % (len(names) - len(missing), len(names), page))
    return 1 if missing else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("page", nargs="?")
    ap.add_argument("--tests")
    a = ap.parse_args(argv)
    if a.page and a.tests:
        return check(a.page, a.tests)
    if a.page or a.tests:
        ap.error("give both a page and --tests, or neither")
    if PAGES_UNREADABLE:
        print("UNREADABLE %s: the page list cannot be read, so no page is checked" % PAGES_UNREADABLE)
        return 3
    rcs = [check(os.path.join(TOP, p), os.path.join(TOP, t)) for p, t in PAGES.items()]
    for p in sorted(glob.glob(os.path.join(TOP, "design", "specs", "*", "boundary.md"))):
        if os.path.relpath(p, TOP).replace(os.sep, "/") not in PAGES:
            print("UNREADABLE %s: no tests file registered for it in boundary_pages.json" % p)
            rcs.append(3)
    return max(rcs)


if __name__ == "__main__":
    sys.exit(main())
