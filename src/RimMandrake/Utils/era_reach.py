#!/usr/bin/env python3
"""era_reach.py -- call-graph reach from live (non-era) code into rimflow/relentless*.py: which functions, methods and
constants of the retired Relentless modules live code still reaches (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES;
results in design/RimMandrake/retired_eras_index_2026-11-18.md).

Nodes: (module, name) for top-level functions/assignments, (module, "Cls") for a class's own body and
(module, "Cls.meth") for its methods. A method is reached when its class is reached AND its name is used as an
attribute anywhere in reached code (duck-typed, so conservative). A module's import-time statements are reached
when the module is imported. In era modules a parameter named `sup` is the relentless module itself
(relentless.py passes sys.modules[__name__]).
Roots: every name a non-era file pulls from an era module (mode `live` skips tests; `selftests` counts them too).
A name reached only through getattr(obj, "x") on a non-module object, exec or a string table is NOT seen: check
undefined names after any cut. A string path run as a script (land.sh, publish.py) is not an import: grep for those.
usage: era_reach.py REPO [live|selftests] [--exclude-roots f1,f2] [--only-methods mod.Cls=m1,m2;mod.Cls2=m3]  -> JSON
--roots mod.fn,...: extra roots, for code a unit runs by script path (systemd-run ... x.py verb), which no import shows.
--only-methods: for that class, only the named methods (and what they call through self) are reached, never a method
merely used by name somewhere: the duck-typed rule over-reaches on common names (launch, measure, stop).
"""
import ast, json, os, subprocess, sys
from collections import defaultdict

REPO = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "live"
EXCL = set()
if "--exclude-roots" in sys.argv:
    EXCL = set(sys.argv[sys.argv.index("--exclude-roots") + 1].split(","))
ONLY = {}
XROOTS = []
if "--roots" in sys.argv:
    XROOTS = [tuple(x.split(".", 1)) for x in sys.argv[sys.argv.index("--roots") + 1].split(",")]
if "--only-methods" in sys.argv:
    for spec in sys.argv[sys.argv.index("--only-methods") + 1].split(";"):
        k, v = spec.split("=", 1)
        ONLY[tuple(k.rsplit(".", 1))] = set(v.split(","))
RF = "src/RimMandrake/rimflow"
SUP_NAMES = {"sup"}

files = subprocess.run(["git", "-C", REPO, "ls-files", "*.py"], capture_output=True, text=True, timeout=120,
                       check=True).stdout.split()
era_mods = {os.path.basename(f)[:-3]: f for f in files
            if os.path.dirname(f) == RF and os.path.basename(f)[:-3].split("_")[0] == "relentless"}

def is_era_file(f):
    return f in era_mods.values() or "relentless" in os.path.basename(f)

def parse(f):
    try:
        return ast.parse(open(os.path.join(REPO, f), encoding="utf-8").read(), f)
    except Exception as e:
        print(f"PARSE_FAIL {f}: {e}", file=sys.stderr)
        return None

def import_aliases(tree, era):
    mods, names = {}, {}
    if era:
        for s in SUP_NAMES:
            mods[s] = "relentless"
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                top = a.name.split(".")[-1]
                if top in era_mods:
                    mods[a.asname or a.name] = top
        elif isinstance(n, ast.ImportFrom) and n.module:
            m = n.module.split(".")[-1]
            if m in era_mods:
                for a in n.names:
                    names[a.asname or a.name] = (m, a.name)
    return mods, names

def refs_in(node, mods, names, local, here):
    out, attrs = set(), set()
    attr_bases = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr") \
                and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
            attrs.add(n.args[1].value)
            if isinstance(n.args[0], ast.Name) and n.args[0].id in mods:
                out.add((mods[n.args[0].id], n.args[1].value)); attr_bases.add(id(n.args[0]))
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute):
            attrs.add(n.attr); attr_bases.add(id(n.value))
            if isinstance(n.value, ast.Name) and n.value.id in mods:
                out.add((mods[n.value.id], n.attr))
        elif isinstance(n, ast.Name):
            if n.id in names:
                out.add(names[n.id])
            elif here and n.id in local:
                out.add((here, n.id))
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id in mods and id(n) not in attr_bases and isinstance(n.ctx, ast.Load) \
                and n.id not in SUP_NAMES:
            out.add((mods[n.id], "*"))
    return out, attrs

def is_main_block(s):
    return (isinstance(s, ast.If) and isinstance(s.test, ast.Compare) and isinstance(s.test.left, ast.Name)
            and s.test.left.id == "__name__")

graph = {}
methods = defaultdict(dict)
tops, spans = {}, {}
for m, f in era_mods.items():
    t = parse(f)
    mods, names = import_aliases(t, True)
    local = {}
    for s in t.body:
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            local[s.name] = s
        elif isinstance(s, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            tg = s.targets if isinstance(s, ast.Assign) else [s.target]
            for x in tg:
                for nn in ast.walk(x):
                    if isinstance(nn, ast.Name):
                        local.setdefault(nn.id, s)
        elif isinstance(s, (ast.Try, ast.If)) and not is_main_block(s):
            for nn in ast.walk(s):
                if isinstance(nn, (ast.FunctionDef, ast.ClassDef)):
                    local.setdefault(nn.name, nn)
                elif isinstance(nn, ast.Name) and isinstance(nn.ctx, ast.Store):
                    local.setdefault(nn.id, s)
    tops[m] = local
    for k, v in local.items():
        if isinstance(v, ast.ClassDef):
            r, a = set(), set()
            for b in [b for b in v.body if not isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))] \
                    + v.bases + v.decorator_list:
                rr, aa = refs_in(b, mods, names, local, m); r |= rr; a |= aa
            graph[(m, k)] = (r - {(m, k)}, a)
            for b in v.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    graph[(m, f"{k}.{b.name}")] = refs_in(b, mods, names, local, m)
                    methods[(m, k)][b.name] = b
                    spans[(m, f"{k}.{b.name}")] = (b.lineno, b.end_lineno)
            spans[(m, k)] = (v.lineno, v.end_lineno)
        else:
            rr, aa = refs_in(v, mods, names, local, m)
            graph[(m, k)] = (rr - {(m, k)}, aa)
            if isinstance(v, (ast.FunctionDef, ast.AsyncFunctionDef)):
                spans[(m, k)] = (v.lineno, v.end_lineno)
    it, ia, imported = set(), set(), set()
    for s in t.body:
        if is_main_block(s):
            graph[(m, "<main>")] = refs_in(s, mods, names, local, m)
            continue
        if isinstance(s, ast.Import):
            imported |= {a.name.split(".")[-1] for a in s.names if a.name.split(".")[-1] in era_mods}
            continue
        if isinstance(s, ast.ImportFrom):
            if s.module and s.module.split(".")[-1] in era_mods:
                imported.add(s.module.split(".")[-1])
            continue
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for d in s.decorator_list:
                it |= refs_in(d, mods, names, local, m)[0]
            continue
        for c in ast.walk(s):
            if isinstance(c, ast.Call):
                rr, aa = refs_in(c, mods, names, local, m); it |= rr; ia |= aa
        if not isinstance(s, (ast.Assign, ast.AnnAssign)):
            rr, aa = refs_in(s, mods, names, local, m); it |= rr; ia |= aa
    graph[(m, "<import>")] = (it | {(x, "<import>") for x in imported}, ia)

roots = defaultdict(set)
live_attrs = set()
for f in files:
    if is_era_file(f) or f in EXCL or os.path.basename(f) in EXCL:
        continue
    b = os.path.basename(f)
    if MODE == "live" and (b.startswith("selftest_") or b.startswith("test_") or "/testdata/" in f
                           or "selftest_fixtures" in f or "time_ledger_replay" in f):
        continue
    t = parse(f)
    if t is None:
        continue
    mods, names = import_aliases(t, False)
    if not mods and not names:
        continue
    rr, aa = refs_in(t, mods, names, {}, None)
    for r in rr:
        roots[r].add(f)
    for m in set(mods.values()) | {v[0] for v in names.values()}:
        roots[(m, "<import>")].add(f)
    live_attrs |= aa

for r in XROOTS:
    roots[r].add("--roots")
reached, parent = set(), {}
stack = [(r, None) for r in roots]
classes_reached = set()
while True:
    while stack:
        node, par = stack.pop()
        if node in reached:
            continue
        reached.add(node); parent[node] = par
        m, n = node
        if m not in era_mods:
            continue
        if n == "*":
            nxt = [k for k in graph if k[0] == m and "." not in k[1] and k[1] != "<main>"]
        else:
            refs, attrs = graph.get(node, (set(), set()))
            live_attrs |= attrs
            nxt = list(refs) + [(m, "<import>")]
            if (m, n) in methods:
                classes_reached.add((m, n))
            if "." in n:
                nxt.append((m, n.split(".")[0]))
        stack.extend((x, node) for x in nxt)
    added = False
    self_used = defaultdict(set)
    for c in ONLY:
        for meth, b in methods.get(c, {}).items():
            if (c[0], f"{c[1]}.{meth}") in reached:
                self_used[c] |= {a.attr for a in ast.walk(b) if isinstance(a, ast.Attribute)
                                 and isinstance(a.value, ast.Name) and a.value.id == "self"}
    for c in list(classes_reached):
        for meth in methods[c]:
            node = (c[0], f"{c[1]}.{meth}")
            ok = (meth in ONLY[c] or meth in self_used.get(c, ())) if c in ONLY else \
                (meth in live_attrs or (meth.startswith("__") and meth.endswith("__")))
            if node not in reached and ok:
                stack.append((node, c)); added = True
    if not added:
        break

def path(k):
    p = []
    while k:
        p.append(f"{k[0]}.{k[1]}"); k = parent.get(k)
    return p

out = {"mode": MODE, "excluded_roots": sorted(EXCL), "modules": {}}
for m in sorted(era_mods):
    fns = [k for k in spans if k[0] == m]
    whole = (m, "*") in reached
    live = {k for k in fns if k in reached or (whole and "." not in k[1])}
    out["modules"][m] = {
        "imported": (m, "<import>") in reached, "wholesale": whole,
        "fns": len(fns), "live_fns": len(live),
        "live": sorted(k[1] for k in live), "dead": sorted(k[1] for k in fns if k not in live),
        "dead_lines": sum(spans[k][1] - spans[k][0] + 1 for k in fns if k not in live
                          and ("." not in k[1] or (m, k[1].split(".")[0]) in live)),
        "all_lines": sum(spans[k][1] - spans[k][0] + 1 for k in fns if "." not in k[1]),
        "live_consts": sorted(n for (mm, n) in reached if mm == m and n in tops[m]
                              and not isinstance(tops[m][n], (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))),
    }
out["why_wholesale"] = {m: path((m, "*")) for m in era_mods if (m, "*") in reached}
out["path"] = {f"{k[0]}.{k[1]}": path(k) for k in reached if k[0] in era_mods}
out["roots"] = {f"{m}.{n}": sorted(v) for (m, n), v in sorted(roots.items())}
json.dump(out, sys.stdout, indent=1)
