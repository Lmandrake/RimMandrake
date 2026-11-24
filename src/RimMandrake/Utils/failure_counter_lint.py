#!/usr/bin/env python3
"""failure_counter_lint.py - a counter of bad outcomes asks failure_class whether an outcome counts against the work.

Item RIMMANDRAKE_SHARE_ONE_FAILURE_CLASSIFIER_EVERY_COUNTER_ROLLED_ITS_OWN; page
design/specs/2026-11-23-one-failure-classifier/boundary.md (the-lint-refuses-a-new-counter). Runs at ./publish
(pipeline_tests.json, through selftest_failure_counter_lint.py).

By AST, over pipeline machinery (ROOTS, and every pipeline_files path of pipeline_tests.json): a comparison of a counted
bad outcome with a limit (`fails >= 2`, `len(dead) >= LIMIT`, `rec["tries"] < MAX_TRIES`), and a retry loop
(`for attempt in range(TRIES)`). Its enclosing function must call failure_class (an `FC.` or `failure_class.` name), or
the counter sits in failure_counter_list.json with its reason: what it counts, and why no outcome of the work is spent.
An entry is keyed by file, function and the comparison's own text, with a count, so a moved line is no change. An entry
that matches nothing is stale and refused.

    python3 src/RimMandrake/Utils/failure_counter_lint.py [--list]      exit 0 green, 1 refused (each named), 2 could not look
"""
import ast
import collections
import fnmatch
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIST = os.path.join(HERE, "failure_counter_list.json")
ROOTS = ("src/RimMandrake/rimflow/*.py", "src/RimMandrake/Utils/testq/*.py", "src/RimMandrake/Utils/maturation*.py",
         "src/RimMandrake/Utils/artpipe/*.py", "src/RimMandrake/Utils/art_eval/*.py", "src/RimMandrake/Utils/publish.py",
         "src/RimMandrake/Utils/art/facing_regen_batch.py", "src/RimMandrake/Utils/nightly_catchup.py",
         "src/RimMandrake/Utils/deadman_check.py", "infrastructure/stevedesktop/*.py")
WORD = re.compile(r"(?i)(fail|tries\b|attempt|streak|strike|refus|retr(?:y|ies)|\bdied|\bdead\b|deaths|\bfaults?\b|fault_|_fault|"
                  r"outage|relaunch|never|resume_n\b|reruns?\b|rerun_|invalid|crash|reopens|bounce|trial|redispatch|give_?up|"
                  r"spoiled|non_?pass|unmeasured|cycles?\b|cycled|voids?\b|CYCLE_|RESUME_MAX|RUNS_MAX|_TO_STOP|MAX_PER_DAY|max_never|"
                  r"max_runs|\bdry)")
TIME = re.compile(r"\bnow\b|time\.|deadline|clock\(|_at\b|\bage\b|_age|since|_s\b|getsize|getmtime|\bt0\b")
LIMIT = re.compile(r"^(?:\d+|[A-Z][A-Z0-9_.]*|lim\w*|most|cap|n|need|per|max_\w+|int\(.*\)|.*\b[A-Z][A-Z0-9_]{3,}\b.*|"
                   r".*(?:_limit|_max|max_|_most|_tries|limit\().*)$", re.S)
OPS = (ast.GtE, ast.Gt, ast.Lt, ast.LtE)


def files(repo=REPO):
    with open(os.path.join(repo, "src/RimMandrake/Utils/pipeline_tests.json"), encoding="utf-8") as f:
        pats = list(ROOTS) + [p for p in json.load(f)["pipeline_files"] if p.endswith(".py")]
    out = set()
    for d in sorted({os.path.dirname(p) for p in pats}):
        if not os.path.isdir(os.path.join(repo, d)):
            continue
        for fn in os.listdir(os.path.join(repo, d)):
            rel = d + "/" + fn
            if fn.endswith(".py") and not re.match(r"selftest|test_", fn) and "mutant" not in fn \
                    and any(fnmatch.fnmatch(rel, p) for p in pats):
                out.add(rel)
    return sorted(out)


def _calls_class(node):
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in ("FC", "failure_class"):
            return True
    return False


def _counter(n):
    """-> the counter's text, or None."""
    if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.ops[0], OPS):
        a, b = ast.unparse(n.left), ast.unparse(n.comparators[0])
        if TIME.search(a) or TIME.search(b):
            return None
        if b == "0" and isinstance(n.ops[0], (ast.Gt, ast.LtE)):      # `fails > 0` is "any", no count to a limit
            return None
        if WORD.search(a + " " + b) and (LIMIT.match(a) or LIMIT.match(b)):
            return " ".join(ast.unparse(n).split())
    if isinstance(n, (ast.For, ast.AsyncFor)) and isinstance(n.iter, ast.Call) and getattr(n.iter.func, "id", "") == "range":
        s = ast.unparse(n.iter)
        if WORD.search(s) or WORD.search(ast.unparse(n.target)):
            return "for %s in %s" % (ast.unparse(n.target), " ".join(s.split()))
    return None


def scan_text(text, rel):
    """-> [(key, line)] of the counters of one file whose enclosing function does not call failure_class."""
    out = []

    def walk(node, fn, ok):
        for c in ast.iter_child_nodes(node):
            f2, ok2 = fn, ok
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                f2, ok2 = c.name, ok or _calls_class(c)
            t = _counter(c)
            if t and not ok2:
                out.append(("%s::%s::%s" % (rel, f2, t), c.lineno))
            walk(c, f2, ok2)
    walk(ast.parse(text), "<module>", False)
    return out


def load_list(path=LIST):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    out = {}
    for k, v in doc["counters"].items():
        if not str(v.get("why") or "").strip():
            raise ValueError("%s: %s has no why" % (path, k))
        out[k] = int(v.get("n", 1))
    return out


def check(repo=REPO, listed=None, extra=None, only=None):
    """-> ([problem], counters seen). extra: {rel: text} read in place of (or beside) the tree's files. only: read these
    files alone (the list is then not checked for stale entries)."""
    listed = load_list(os.path.join(repo, os.path.relpath(LIST, REPO))) if listed is None else listed
    seen, where = collections.Counter(), {}
    rels = sorted(only if only is not None else set(files(repo)) | set(extra or ()))
    for rel in rels:
        if extra and rel in extra:
            text = extra[rel]
        else:
            with open(os.path.join(repo, rel), encoding="utf-8", errors="replace") as f:
                text = f.read()
        for k, line in scan_text(text, rel):
            seen[k] += 1
            where.setdefault(k, []).append(line)
    bad = []
    for k, n in sorted(seen.items()):
        if n > listed.get(k, 0):
            rel, fn, t = k.split("::", 2)
            bad.append("%s:%s: in %s, the counter `%s` does not ask failure_class whether an outcome counts. Call "
                       "failure_class there, or list it with its reason in src/RimMandrake/Utils/failure_counter_list.json"
                       % (rel, ",".join(map(str, where[k])), fn, t))
    for k, n in sorted(listed.items() if only is None else ()):
        if seen.get(k, 0) < n:
            bad.append("stale entry of failure_counter_list.json (%d listed, %d in the tree): %s" % (n, seen.get(k, 0), k))
    return bad, sum(seen.values())


def main(argv=None):
    if "--list" in (argv or sys.argv[1:]):
        for rel in files():
            with open(os.path.join(REPO, rel), encoding="utf-8", errors="replace") as f:
                for k, line in scan_text(f.read(), rel):
                    print("%s\t%d" % (k, line))
        return 0
    try:
        bad, n = check()
    except (OSError, ValueError, KeyError, SyntaxError) as e:
        print("failure_counter_lint: COULD NOT LOOK: %s: %s" % (type(e).__name__, e))
        return 2
    for b in bad:
        print("FAIL " + b)
    print("failure_counter_lint: %d listed counter(s), %s" % (n, "REFUSED %d" % len(bad) if bad else "OK"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
