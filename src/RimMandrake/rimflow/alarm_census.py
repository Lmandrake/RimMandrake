#!/usr/bin/env python3
"""alarm_census.py -- every alarm kind the source can raise, read from the syntax tree (RO4).

An alarm site is a call with do= and kind=..., a dict with "do": "alarm" and "kind": ..., or a kind-bearing dict
appended to `alarms`. A kind may be a literal, a concatenation, a % format, an f-string, an if-expression, a variable
assigned in the function or module, or a parameter (read at the function's call sites in that module). A dynamic part
inside a kind reads as "x", the same as a route's * sees it. A kind with no literal left in it is UNRESOLVED: a census
that shrugs at a form is the blindness this replaced (selftest_incident fails on any unresolved site).
"""
import ast
import os
import re

WILD = "x"


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


def _assigned(scope, name):
    for n in ast.walk(scope):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            yield n.value


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
        return values(node.body, tree, fns, seen) + values(node.orelse, tree, fns, seen)
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


def of_source(src, where="<source>"):
    """-> (kinds, [unresolved "where:line what"])."""
    tree = ast.parse(src)
    fns = _functions(tree)
    kinds, bad = set(), []
    for node in sites(tree):
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
    return kinds, bad


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
                k, b = of_source(src, os.path.relpath(p, root))
            except SyntaxError:
                continue            # not a live module (a template or a py2 donor): nothing runs it
            kinds |= k
            bad += b
            files += [p] if k or b else []
    return kinds, bad, files
