#!/usr/bin/env python3
"""era_split.py -- move the live top-level nodes of one era module into a new module, verbatim
(RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES; plan in design/RimMandrake/retired_eras_index_2026-11-18.md).

    era_split.py REACH.json OLD.py NEW.py "docstring line"     # writes NEW.py, rewrites OLD.py

The new module gets the shared header (imports, path setup, import-time statements) and every live node from
REACH.json (era_reach.py output). The old module keeps its dead nodes and imports the live names back from the new
module, so dead code that still calls them runs unchanged until it is deleted. A class whose methods are split stays
whole in the new module minus its dead methods; the old module gets `class X(new.X)` holding the dead ones.
"""
import ast
import json
import os
import sys

reach, old_p, new_p, doc = sys.argv[1:5]
WHOLE_CLASSES = "--trim-classes" not in sys.argv   # default: a live class moves whole (dead code may hold its instances)
mod = os.path.basename(old_p)[:-3]
new_mod = os.path.basename(new_p)[:-3]
R = json.load(open(reach))["modules"][mod]
LIVE = set(R["live"]) | set(R["live_consts"])
src = open(old_p, encoding="utf-8").read()
lines = src.splitlines(keepends=True)
t = ast.parse(src)


def is_main(s):
    return isinstance(s, ast.If) and isinstance(s.test, ast.Compare) and isinstance(s.test.left, ast.Name) \
        and s.test.left.id == "__name__"


def start(s):
    a = min([s.lineno] + [d.lineno for d in getattr(s, "decorator_list", [])])
    return a


def targets(s):
    tg = s.targets if isinstance(s, ast.Assign) else [s.target]
    out = set()
    for x in tg:
        for n in ast.walk(x):
            if isinstance(n, ast.Name):
                out.add(n.id)
    return out


# span of each top-level stmt including the comment/blank block right above it
body = t.body
spans = []
prev_end = 0
for i, s in enumerate(body):
    a = start(s)
    # attach comment lines directly above (no blank line between)
    j = a
    while j - 1 > prev_end and lines[j - 2].lstrip().startswith("#"):
        j -= 1
    spans.append((j, s.end_lineno))
    prev_end = s.end_lineno

kind = []   # header | live | dead | main | doc
for i, s in enumerate(body):
    if i == 0 and isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant):
        kind.append("doc")
    elif is_main(s):
        kind.append("main")
    elif isinstance(s, (ast.Import, ast.ImportFrom)):
        kind.append("header")
    elif isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        kind.append("live" if s.name in LIVE else "dead")
    elif isinstance(s, (ast.Assign, ast.AnnAssign)):
        tg = targets(s)
        kind.append("live" if tg & LIVE else "dead")
    else:
        kind.append("header")   # import-time statements (sys.path, try/except imports) run in both

text = lambda a, b: "".join(lines[a - 1:b])
new_parts, old_parts, moved = [], [], []
subclassed = set()
first_def = next(i for i, k in enumerate(kind) if k in ("live", "dead"))
for i, (s, k) in enumerate(zip(body, kind)):
    a, b = spans[i]
    chunk = text(a, b)
    gap = text(spans[i - 1][1] + 1, a - 1) if i else text(1, a - 1)
    if k == "doc":
        new_parts.append(gap + '"""%s\n\nMoved verbatim from rimflow/%s.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):\n'
                         'only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).\n"""\n'
                         % (doc, mod))
        old_parts.append(gap + chunk)
        continue
    if k == "header":
        new_parts.append(gap + chunk); old_parts.append(gap + chunk)
        if i + 1 == first_def or (i + 1 < len(kind) and kind[i + 1] in ("live", "dead") and
                                  all(kk not in ("live", "dead") for kk in kind[:i + 1])):
            old_parts.append("\nfrom %s import *  # noqa: F401,F403  the live part moved there\nfrom %s import (  # noqa: E402,F401\n    %%MOVED%%)\n" % (new_mod, new_mod))
        continue
    if k == "main":
        old_parts.append(gap + chunk)
        continue
    if k == "dead":
        old_parts.append(gap + chunk)
        continue
    # live
    if isinstance(s, ast.ClassDef):
        dead_m = [] if WHOLE_CLASSES else [m for m in s.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and "%s.%s" % (s.name, m.name) not in LIVE]
        keep = chunk
        dead_src = []
        for m in sorted(dead_m, key=lambda m: -m.lineno):
            ma = min([m.lineno] + [d.lineno for d in m.decorator_list])
            j = ma
            while j - 1 > s.lineno and lines[j - 2].lstrip().startswith("#"):
                j -= 1
            seg = text(j, m.end_lineno)
            dead_src.insert(0, seg)
            rel_a, rel_b = j - a, m.end_lineno - a + 1
            kl = keep.splitlines(keepends=True)
            keep = "".join(kl[:rel_a] + kl[rel_b:])
        new_parts.append(gap + keep)
        moved.append(s.name)
        if dead_src:
            subclassed.add(s.name)
            old_parts.append(gap + "class %s(%s.%s):  # the dead methods; the live class moved to %s.py\n"
                             % (s.name, new_mod, s.name, new_mod) + "\n".join(x.rstrip("\n") + "\n" for x in dead_src))
    else:
        new_parts.append(gap + chunk)
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
            moved.append(s.name)
        else:
            moved.extend(sorted(targets(s) & LIVE) or sorted(targets(s)))
tail = text(spans[-1][1] + 1, len(lines))
new_src = "".join(new_parts) + tail
old_src = "".join(old_parts) + tail
needs_mod = "class " in old_src and ("(%s." % new_mod) in old_src
mv = ", ".join(sorted(set(moved)))
# wrap the moved-names list
out, line = [], ""
for nm in sorted(set(moved) - subclassed):
    if len(line) + len(nm) + 2 > 110:
        out.append(line); line = ""
    line += nm + ", "
out.append(line)
old_src = old_src.replace("%MOVED%", "\n    ".join(x.rstrip() for x in out))
old_src = old_src.replace("from %s import *  # noqa: F401,F403  the live part moved there\n" % new_mod,
                          ("import %s  # noqa: E402  the live part moved there\n" % new_mod) if needs_mod else "")
import re as _re
import subprocess as _sp
open(new_p, "w", encoding="utf-8").write(new_src)
pf = os.environ.get("PYFLAKES_PYTHON") or sys.exit("era_split: set PYFLAKES_PYTHON to a python with pyflakes "
                                                     "(python3 -m venv V && V/bin/pip install pyflakes)")
r = _sp.run([pf, "-m", "pyflakes", new_p], capture_output=True, text=True, timeout=120)
nl = new_src.splitlines(keepends=True)
drop = set()
for ln in r.stdout.splitlines():
    m = _re.match(r".*?:(\d+):\d+:? '([\w.]+)' imported but unused", ln)
    if m and _re.fullmatch(r"import %s\s*" % _re.escape(m.group(2)), nl[int(m.group(1)) - 1].strip() + "\n"):
        drop.add(int(m.group(1)) - 1)
new_src = "".join(x for i, x in enumerate(nl) if i not in drop)
open(new_p, "w", encoding="utf-8").write(new_src)
open(old_p, "w", encoding="utf-8").write(old_src)
print(json.dumps({"moved": sorted(set(moved)), "new_lines": new_src.count("\n"), "old_lines": old_src.count("\n")}))
