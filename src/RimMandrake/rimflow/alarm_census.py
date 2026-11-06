#!/usr/bin/env python3
"""alarm_census.py -- every alarm kind the source can raise, read from the syntax tree (RO4).

An alarm site is a call with do= and kind=..., a dict with "do": "alarm" and "kind": ..., a kind-bearing dict appended
to `alarms`, any road straight onto the told ledger (incident.signal, a dict handed to alarm_signal or on_alarm, a told
row with "metric" and "told_at"), or a point an ops_watch collector builds (a key given an M/U/E point, ranged or not:
a target or ranges row added later needs its route to be there). A kind may be a literal, a concatenation, a % format, an f-string, an if-expression, a variable
assigned in the function or module, a sibling module's constant (`mod.NAME`), an `a or b`, or a parameter (read at
the function's call sites in that module); a None branch of an if/or is no kind. A dynamic part
inside a kind reads as "x", the same as a route's * sees it. A kind with no literal left in it is UNRESOLVED: a census
that shrugs at a form is the blindness this replaced (selftest_incident fails on any unresolved site).
Built names slipped past before: queues.<name>.* and relentless_attention_<key> (ALARM_CENSUS_EXTEND_BUILT_NAMES_SLIP_PAST).

recurring() is the census of what came back: an alarm kind crossed twice or more (ops_watch's alarms_log.jsonl), or an item
whose fix died (model.guard_owed: deaths, a first sighting is none), with no class guard test on record (design idea 5, `rimflow guard`).

    python3 src/RimMandrake/rimflow/alarm_census.py recurring     one line per recurring kind with no guard; exit 1 if any
"""
import ast
import fnmatch
import json
import os
import re

WILD = "x"
SIGNAL_MODULE = "incident"
SIGNAL_CALLEES = ("alarm_signal", "on_alarm")
FORWARDERS = {"signal_alarm": 2, "told": 0}     # pass on a kind (argument index) a site elsewhere names; a literal is still read
POINT_MODULES = ("ops_watch.py",)
POINT_MAKERS = ("M", "U", "E", "soft_point", "tt_point", "untriaged_reading")
POINT_FAMILY_OF = {"red_groups": "testing.red_x"}       # the key is data made by known_reds.py; rules target testing.red_*
POINT_REPLAYS = ("andon", "run", "carry_family")  # re-issue the keys of an earlier pass; every one was built above


class Unresolved(Exception):
    pass


def _lit(node, key):
    return isinstance(node, ast.Constant) and node.value == key


def _functions(tree):
    """Parent links, and {function name: [def nodes]}."""
    fns = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            c.parent = n
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fns.setdefault(n.name, []).append(n)
    return fns


def _scopes(node):
    while hasattr(node, "parent"):
        node = node.parent
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.Module)):
            yield node


def _own_nodes(scope):
    """The nodes of a scope, not those of a function inside it: another function's local is not this name."""
    todo = list(ast.iter_child_nodes(scope))
    while todo:
        n = todo.pop()
        yield n
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            todo += ast.iter_child_nodes(n)


def _assigned(scope, name):
    for n in _own_nodes(scope):
        if not isinstance(n, ast.Assign):
            continue
        for t in n.targets:
            if isinstance(t, ast.Name) and t.id == name:
                yield n.value
            elif isinstance(t, ast.Tuple) and isinstance(n.value, ast.Tuple) and len(t.elts) == len(n.value.elts):
                yield from (v for e, v in zip(t.elts, n.value.elts) if isinstance(e, ast.Name) and e.id == name)


def _params(fn):
    a = fn.args
    return [p.arg for p in a.posonlyargs + a.args + a.kwonlyargs]


def _arg_values(tree, fn, name, fns, seen):
    pos = _params(fn).index(name)
    out = []
    for c in ast.walk(tree):
        if isinstance(c, ast.Call) and getattr(c.func, "id", getattr(c.func, "attr", None)) == fn.name:
            kw = [k.value for k in c.keywords if k.arg == name]
            arg = kw[0] if kw else (c.args[pos] if pos < len(c.args) else None)
            if arg is not None:
                out += values(arg, tree, fns, seen)
    return out


def _name(node, tree, fns, seen):
    key = (node.id, node.lineno)
    if key in seen:
        raise Unresolved(node.id)
    seen = seen | {key}
    for scope in _scopes(node):
        got = []
        for v in _assigned(scope, node.id):
            got += values(v, tree, fns, seen)
        if got:
            return got
        if not isinstance(scope, ast.Module) and node.id in (_params(scope) if not isinstance(scope, ast.Lambda) else []):
            got = _arg_values(tree, scope, node.id, fns, seen)
            if got:
                return got
            raise Unresolved(node.id)
    raise Unresolved(node.id)


def _module_constant(node, tree):
    """`mod.NAME`, where `import mod [as m]` names a sibling module whose top level assigns NAME (read through the
    sibling reader census() gives of_source; none, or no such assignment, is Unresolved)."""
    mods = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names
            if (a.asname or a.name) == node.value.id]
    src = getattr(tree, "sibling", None) and mods and tree.sibling(mods[0])
    if not src:
        raise Unresolved("Attribute")
    mtree = ast.parse(src)
    mfns = _functions(mtree)
    got = [v for a in _assigned(mtree, node.attr) for v in values(a, mtree, mfns)]     # its own tree, its own seen
    if not got:
        raise Unresolved("Attribute")
    return got


def _part(node, tree, fns, seen):
    try:
        return values(node, tree, fns, seen)
    except Unresolved:
        return [WILD]


def _product(a, b):
    return [x + y for x in a for y in b]


def values(node, tree, fns, seen=frozenset()):
    """The strings an expression can be, or Unresolved."""
    if isinstance(node, ast.Constant):
        return [str(node.value)]
    if isinstance(node, ast.IfExp):
        return [v for b in (node.body, node.orelse) if not _lit(b, None) for v in values(b, tree, fns, seen)]
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
        # `kind or "fallback"`: any operand can be the value; a None operand is no kind (an unpassed default)
        return [v for b in node.values if not _lit(b, None) for v in values(b, tree, fns, seen)]
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return _module_constant(node, tree)
    if isinstance(node, ast.Name):
        return _name(node, tree, fns, seen)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _product(_part(node.left, tree, fns, seen), _part(node.right, tree, fns, seen))
    if isinstance(node, ast.JoinedStr):
        out = [""]
        for v in node.values:
            out = _product(out, _part(v.value if isinstance(v, ast.FormattedValue) else v, tree, fns, seen))
        return out
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        args = node.right.elts if isinstance(node.right, ast.Tuple) else [node.right]
        out = []
        for fmt in values(node.left, tree, fns, seen):
            pieces = re.split(r"%[sd]", fmt)
            got = [pieces[0]]
            for i, p in enumerate(pieces[1:]):
                got = _product(_product(got, _part(args[i], tree, fns, seen) if i < len(args) else [WILD]), [p])
            out += got
        return out
    raise Unresolved(type(node).__name__)


def sites(tree):
    """The kind expression of every alarm site in a parsed module."""
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            kw = {k.arg: k.value for k in n.keywords}
            if "do" in kw and "kind" in kw:     # an act of any do: login_switch carries the kind it alarms under
                yield kw["kind"]
            if getattr(n.func, "attr", None) == "append" and getattr(n.func.value, "id", None) == "alarms" and n.args \
                    and isinstance(n.args[0], ast.Dict):
                yield from (v for k, v in zip(n.args[0].keys, n.args[0].values) if _lit(k, "kind"))
        elif isinstance(n, ast.Dict):
            d = [(k, v) for k, v in zip(n.keys, n.values) if k is not None]
            if any(_lit(k, "do") and _lit(v, "alarm") for k, v in d):
                yield from (v for k, v in d if _lit(k, "kind"))


def _enclosing(node):
    return next((s for s in _scopes(node) if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))), None)


def _callee(call):
    return getattr(call.func, "id", getattr(call.func, "attr", None))


def _signal_aliases(tree):
    return {a.asname or a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names if a.name == SIGNAL_MODULE}


def _is_signal_callee(call):
    """alarm_signal(...), x.on_alarm(...), or a name assigned getattr(x, "alarm_signal", ...) in a scope around it."""
    if _callee(call) in SIGNAL_CALLEES:
        return True
    if not isinstance(call.func, ast.Name):
        return False
    return any(isinstance(v, ast.Call) and getattr(v.func, "id", None) == "getattr" and len(v.args) > 1
               and isinstance(v.args[1], ast.Constant) and v.args[1].value in SIGNAL_CALLEES
               for s in _scopes(call) for v in _assigned(s, call.func.id))


def _forwarding(fn):
    return fn is not None and (fn.name in FORWARDERS or fn.name in SIGNAL_CALLEES or fn.name == "signal")


def signal_sites(tree):
    """The roads onto the told ledger that carry no do="alarm". A function that only forwards is no site of its own."""
    aliases = _signal_aliases(tree)
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            d = [(k, v) for k, v in zip(n.keys, n.values) if k is not None]
            if any(_lit(k, "told_at") for k, _ in d) and not _forwarding(_enclosing(n)):
                yield from (v for k, v in d if _lit(k, "metric"))
        if not isinstance(n, ast.Call):
            continue
        fn = _enclosing(n)
        forwarding = _forwarding(fn)
        if isinstance(n.func, ast.Attribute) and getattr(n.func.value, "id", None) in aliases and n.func.attr == "signal":
            kw = [k.value for k in n.keywords if k.arg == "kind"]
            kind = kw[0] if kw else (n.args[1] if len(n.args) > 1 else None)
            if kind is not None and not forwarding:
                yield kind
        elif _is_signal_callee(n) and n.args:
            arg = n.args[0]
            if isinstance(arg, ast.Dict):
                yield from (v for k, v in zip(arg.keys, arg.values) if _lit(k, "kind"))
            elif not (isinstance(arg, ast.Name) and fn is not None and arg.id in _params(fn)):     # a record passed through
                yield arg


def forwarded_literals(tree, fns):
    """What a forwarder's call sites name outright. An argument it cannot read is a record some site above already read."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _callee(n) in FORWARDERS and len(n.args) > FORWARDERS[_callee(n)]:
            try:
                out += values(n.args[FORWARDERS[_callee(n)]], tree, fns)
            except Unresolved:
                pass
    return [k for k in out if k.replace(WILD, "").strip(":")]


def of_source(src, where="<source>", sibling=None):
    """-> (kinds, [unresolved "where:line what"]). `sibling(module name)` -> that module's source or None: how a
    `mod.NAME` kind is read."""
    tree = ast.parse(src)
    tree.sibling = sibling
    fns = _functions(tree)
    kinds, bad = set(), []
    for node in list(sites(tree)) + list(signal_sites(tree)):
        try:
            got = values(node, tree, fns)
        except Unresolved as e:
            bad.append("%s:%d %s" % (where, node.lineno, e))
            continue
        for k in got:
            if k.replace(WILD, "").strip(":"):
                kinds.add(k)
            else:
                bad.append("%s:%d no literal in %r" % (where, node.lineno, k))
    return kinds | set(forwarded_literals(tree, fns)), bad


def _is_point(v):
    if isinstance(v, ast.IfExp):
        return _is_point(v.body) or _is_point(v.orelse)
    return isinstance(v, ast.Call) and _callee(v) in POINT_MAKERS


def _collection(node, tree, fns):
    """The strings in a tuple or list of names, however it is spelled; anything else is Unresolved."""
    if isinstance(node, (ast.Tuple, ast.List)):
        return [x for e in node.elts for x in values(e, tree, fns)]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _collection(node.left, tree, fns) + _collection(node.right, tree, fns)
    if isinstance(node, ast.Name):
        for scope in _scopes(node):
            got = list(_assigned(scope, node.id))
            if got:
                return [x for v in got for x in _collection(v, tree, fns)]
    raise Unresolved(type(node).__name__)


def _loop_iter(node):
    """(variable, what it iterates) of every for loop around a node."""
    while hasattr(node, "parent"):
        node = node.parent
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            yield node.target.id, node.iter


def _key_strings(node, comp, tree, fns):
    """A point key: a loop or comprehension variable reads as what it iterates, keys[0] as any of the tuple `keys`."""
    if isinstance(node, ast.Name):
        loops = [(g.target.id, g.iter) for g in comp if isinstance(g.target, ast.Name)] + list(_loop_iter(node))
        it = next((i for name, i in loops if name == node.id), None)
        if it is not None:
            return _collection(it, tree, fns)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and isinstance(node.slice, ast.Constant) \
            and isinstance(node.slice.value, int):
        return _collection(node.value, tree, fns)
    return values(node, tree, fns)


def points_of_source(src, where="<source>"):
    """Every point name a collector module can build, a dynamic part reading as x. -> (kinds, [unresolved])."""
    tree = ast.parse(src)
    fns = _functions(tree)
    kinds, bad = set(), []
    for n in ast.walk(tree):
        comp, keys = [], []
        if isinstance(n, ast.Assign) and _is_point(n.value):
            keys = [t.slice for t in n.targets if isinstance(t, ast.Subscript)]
        elif isinstance(n, ast.Dict):
            keys = [k for k, v in zip(n.keys, n.values) if k is not None and _is_point(v)]
        elif isinstance(n, ast.DictComp) and _is_point(n.value):
            comp, keys = n.generators, [n.key]
        for k in keys:
            fn = _enclosing(n)
            try:
                got = _key_strings(k, comp, tree, fns)
            except Unresolved as e:
                if fn is not None and fn.name in POINT_FAMILY_OF:
                    kinds.add(POINT_FAMILY_OF[fn.name])
                elif fn is None or fn.name not in POINT_REPLAYS:
                    bad.append("%s:%d point key %s" % (where, k.lineno, e))
                continue
            for s in got:
                if s.replace(WILD, "").strip(".:_"):
                    kinds.add(s)
                else:
                    bad.append("%s:%d no literal in point key %r" % (where, k.lineno, s))
    return kinds, bad


def _sibling_reader(d):
    def read(mod):
        p = os.path.join(d, mod + ".py")
        if not os.path.isfile(p):
            return None
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    return read


def census(root):
    """Every non-selftest .py under `root`. -> (kinds, unresolved, files with a site)."""
    kinds, bad, files = set(), [], []
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ("__pycache__", ".git")]
        for f in names:
            if not f.endswith(".py") or f.startswith("selftest") or f == "alarm_census.py":
                continue
            p = os.path.join(d, f)
            with open(p, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
            if "alarm" not in src:
                continue
            try:
                k, b = of_source(src, os.path.relpath(p, root), _sibling_reader(d))
                if f in POINT_MODULES:
                    pk, pb = points_of_source(src, os.path.relpath(p, root))
                    k, b = k | pk, b + pb
            except SyntaxError:
                continue            # not a live module (a template or a py2 donor): nothing runs it
            kinds |= k
            bad += b
            files += [p] if k or b else []
    return kinds, bad, files


def recurring(log_rows, items, exempt=(), min_seen=2):
    """-> [{kind, seen, items}] the recurring kinds no guard covers, most seen first. `log_rows`: alarms_log.jsonl's rows.
    `items`: {id: item}. An alarm kind is guarded when any item filed for it holds a guard. `exempt`: fnmatch patterns of
    kinds no test can guard (a spent account). A dropped or superseded item holds no promise."""
    seen, filed = {}, {}
    for r in log_rows:
        aid = r.get("aid")
        if not aid or any(fnmatch.fnmatch(aid, p) for p in exempt):
            continue
        seen[aid] = seen.get(aid, 0) + (r.get("event") == "crossed")
        if r.get("item"):
            filed.setdefault(aid, set()).add(r["item"])
    out = []
    claimed = set()
    for aid, n in seen.items():
        ids = filed.get(aid, set())
        claimed |= ids
        if n >= min_seen and not any(getattr(items.get(i), "guard", None) for i in ids):
            out.append({"kind": aid, "seen": n, "items": sorted(ids)})
    import model
    for iid, it in items.items():
        if model.guard_owed(it) and getattr(it, "state", None) not in ("dropped", "superseded") and iid not in claimed:
            out.append({"kind": "live:" + iid, "seen": model.deaths(it), "items": [iid]})
    return sorted(out, key=lambda r: (-r["seen"], r["kind"]))


def read_log(path):
    """alarms_log.jsonl's rows; a torn line is skipped, a missing file raises (no log is no reading, never no recurrences)."""
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            try:
                rows.append(json.loads(ln))
            except ValueError:
                continue
    return rows


def main(argv):
    import sys
    if argv[:1] != ["recurring"]:
        print(__doc__)
        return 2
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path[:0] = [here, os.path.join(os.path.dirname(here), "Utils")]
    import model
    import ops_health as H
    with open(os.path.join(os.path.dirname(here), "Utils", "ops_watch_rules.json"), encoding="utf-8") as f:
        c = H.conf(json.load(f))
    rows = recurring(read_log(str(H.ops_dir() / "alarms_log.jsonl")), model.replay(model.read()).items, c["guard_exempt_kinds"])
    for r in rows:
        print("%-55s seen %3d  %s" % (r["kind"], r["seen"], ",".join(r["items"][:3])))
    print("%d recurring kind(s) with no guard" % len(rows))
    return 1 if rows else 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
