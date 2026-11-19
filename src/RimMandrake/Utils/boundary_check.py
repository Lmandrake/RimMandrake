#!/usr/bin/env python3
"""boundary_check.py — every promise on a boundary page has a test of the same name.

Owner by card 2026-11-18 (`design/RimMandrake/standing_rulings.md` §A boundary page before pipeline code; design
`design/specs/2026-11-18-review-growth-cycle/01-design.md` §5.2). A page's `## PROMISES` and `## SURVIVES` sections list
entries `- **some-name.** ...`; each is owed a module-level test `t_some_name` (a def, or a name bound to one) in the
page's tests file, which that file's `main()` runs (names it, or the def it is bound to). `## DOES NOT SURVIVE`,
`## ACCEPTS` and `## LIFE CYCLES` entries are not promises.

  boundary_check.py <boundary.md> --tests <selftest.py>    one page
  boundary_check.py                                        every design/specs/*/boundary.md (what ./publish runs on a
                                                           change to one, pipeline_tests.json); each must be in PAGES

Exit 0: `promises covered N of N`. 1: a promise has no test, or one `main()` never runs (each named; `promises covered
N of M`). 3: UNREADABLE, the page or tests file could not be read or parsed, its `main()` is absent or picks tests at
run time, or a page is not in PAGES (cause named, no count printed). 4: NO PROMISES, the page lists none.
"""
import argparse
import ast
import glob
import os
import re
import sys

TOP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
# page -> its tests file, repo-relative. A new boundary page is added here.
PAGES = {
    "design/specs/2026-11-18-pipeline-control-surface/boundary.md": "src/RimMandrake/rimflow/selftest_control.py",
    "design/specs/2026-11-19-probe-result/boundary.md": "src/RimMandrake/rimflow/selftest_probe_result.py",
    "design/specs/2026-11-19-stage-ceiling/boundary.md": "src/RimMandrake/rimflow/selftest_stage_ceiling_arrival.py",
    "design/specs/2026-11-19-asks-on-empty-game/boundary.md": "src/RimMandrake/rimflow/selftest_asks_on_empty_game.py",
    "design/specs/2026-11-19-control-acts-export/boundary.md": "src/RimMandrake/rimflow/selftest_control_acts_export.py",
}
SECTIONS = ("PROMISES", "SURVIVES")
HEAD_RX = re.compile(r"^##\s+(\S+)")
ENTRY_RX = re.compile(r"^- \*\*(.+?)[.:]?\*\*")


class Unreadable(Exception):
    pass


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


def tests_in(path):
    """-> (module-level names bound to a function: `def t_x` or `t_x = t_y`, the subset `main()` runs). Raises
    Unreadable when there is no `main()` or it picks its tests at run time."""
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
    ran = {defs[u] for u in used if u in defs}
    return set(defs), {n for n, d in defs.items() if d in ran}


def check(page, tests):
    """-> exit code, printing the verdict for one page."""
    try:
        names = promises(page)
        have, run = tests_in(tests)
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
    rcs = [check(os.path.join(TOP, p), os.path.join(TOP, t)) for p, t in PAGES.items()]
    for p in sorted(glob.glob(os.path.join(TOP, "design", "specs", "*", "boundary.md"))):
        if os.path.relpath(p, TOP).replace(os.sep, "/") not in PAGES:
            print("UNREADABLE %s: no tests file registered for it in boundary_check.py PAGES" % p)
            rcs.append(3)
    return max(rcs)


if __name__ == "__main__":
    sys.exit(main())
