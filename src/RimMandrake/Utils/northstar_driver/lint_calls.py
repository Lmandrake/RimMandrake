#!/usr/bin/env python3
"""Offline static lint of bridge calls against the declared tool schemas (LINT_CALLS_1).

    python3 lint_calls.py [--snapshot tool_schemas.json] [--summary] PATH...
    (PATH = .py files or directories; directories are searched for validation.py,
     northstar_plan.py, northstar_site.py, preflight_*.py)

Recognised call shapes, with a LITERAL tool name:
    X.bridge_call("tool", k=v...)    X.call("tool", k=v...)    X.session.call(...)
    _call(s, "tool", k=v...)
    X.call("tool", {"k": v})  /  X.call("tool", params={"k": v})   (literal-key dict)
Output: `file:line  tool  KIND  detail`, KIND in
    UNKNOWN_TOOL | UNDECLARED_PARAM | MISSING_REQUIRED | UNCHECKED
Anything the lint cannot see through (**kwargs, non-literal tool name, non-literal
params dict, dict with non-literal keys) is UNCHECKED, never silently passed.
Exit 0 only if there are no problems of ANY kind (UNCHECKED counts: it is unproven).
`check=` is the transport's own flag and is not treated as a tool parameter unless the
tool declares one. Does not touch the bridge.
"""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = os.path.join(HERE, "tool_schemas.json")
TARGET_NAMES = ("validation.py", "northstar_plan.py", "northstar_site.py")
TRANSPORT_KW = {"check"}
STATS = {"calls": 0}


def load_tools(path=None):
    with open(path or SNAPSHOT, encoding="utf-8") as f:
        return json.load(f)["tools"]


def _is_call_func(node):
    """Return 'attr' (x.bridge_call / x.call), 'under' (_call(s, ...)) or None."""
    f = node.func
    if isinstance(f, ast.Attribute) and f.attr in ("bridge_call", "call"):
        return "attr"
    if isinstance(f, ast.Name) and f.id == "_call":
        return "under"
    return None


def _str(n):
    return n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None


def lint_source(src, fname, tools):
    out = []  # (line, tool, kind, detail)
    try:
        tree = ast.parse(src, fname)
    except SyntaxError as e:
        return [(e.lineno or 0, "-", "UNCHECKED", "file does not parse: %s" % e.msg)]
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        shape = _is_call_func(node)
        if not shape:
            continue
        pos = node.args
        idx = 0 if shape == "attr" else 1
        if len(pos) <= idx:
            # `x.call(...)` with no tool arg: not a bridge call shape; a bare
            # `_call(s)` neither.  Only flag if it starved for a tool name via kw.
            continue
        if any(isinstance(a, ast.Starred) for a in pos[: idx + 1]):
            out.append((node.lineno, "?", "UNCHECKED", "starred positional args"))
            continue
        tool = _str(pos[idx])
        if tool is None:
            # x.call(variable) is overwhelmingly not a bridge call (e.g. subprocess helpers);
            # report only when the name is a clear bridge-call attr or _call.
            out.append((node.lineno, "?", "UNCHECKED", "non-literal tool name"))
            continue
        if "/" not in tool:
            continue  # x.call("foo") - not a namespaced bridge tool
        given = {}
        unchecked = []
        for kw in node.keywords:
            if kw.arg is None:
                unchecked.append("**kwargs")
            elif kw.arg == "params":
                d = kw.value
                if isinstance(d, ast.Dict) and all(_str(k) for k in d.keys):
                    for k in d.keys:
                        given[_str(k)] = True
                else:
                    unchecked.append("non-literal params=")
            else:
                given[kw.arg] = True
        extra = pos[idx + 1:]
        for d in extra[:1]:
            if isinstance(d, ast.Dict) and all(k is not None and _str(k) for k in d.keys):
                for k in d.keys:
                    given[_str(k)] = True
            else:
                unchecked.append("non-literal params dict")
        STATS["calls"] += 1
        spec = tools.get(tool)
        if spec is None:
            out.append((node.lineno, tool, "UNKNOWN_TOOL", "not in snapshot"))
            continue
        declared = set(spec["parameters"])
        for k in sorted(given):
            if k not in declared and not (k in TRANSPORT_KW and k not in declared):
                out.append((node.lineno, tool, "UNDECLARED_PARAM",
                            "%s (declared: %s)" % (k, ",".join(sorted(declared)) or "none")))
        if not unchecked:
            for k in spec["required"]:
                if k not in given:
                    out.append((node.lineno, tool, "MISSING_REQUIRED", k))
        for u in unchecked:
            out.append((node.lineno, tool, "UNCHECKED", u))
    return sorted(out)


def gather(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, names in os.walk(p):
                dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "worktrees")]
                for n in names:
                    if n in TARGET_NAMES or (n.startswith("preflight_") and n.endswith(".py")):
                        files.append(os.path.join(root, n))
        else:
            files.append(p)
    return sorted(files)


def lint_paths(paths, tools):
    rows = []
    for f in gather(paths):
        with open(f, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        for line, tool, kind, detail in lint_source(src, f, tools):
            rows.append((f, line, tool, kind, detail))
    return rows


def main(argv):
    snap = None
    summary = False
    args = argv[1:]
    while args and args[0].startswith("--"):
        a = args.pop(0)
        if a == "--snapshot":
            snap = args.pop(0)
        elif a == "--summary":
            summary = True
        else:
            print(__doc__)
            return 2
    if not args:
        print(__doc__)
        return 2
    rows = lint_paths(args, load_tools(snap))
    for f, line, tool, kind, detail in rows:
        print("%s:%d  %s  %s  %s" % (f, line, tool, kind, detail))
    counts = {}
    for r in rows:
        counts[r[3]] = counts.get(r[3], 0) + 1
    if summary or rows:
        print("TOTAL %d problems over %d literal-named calls: %s" % (len(rows), STATS["calls"], counts))
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
