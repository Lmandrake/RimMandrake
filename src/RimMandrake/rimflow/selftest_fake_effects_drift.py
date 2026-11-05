#!/usr/bin/env python3
"""selftest_fake_effects_drift: a selftest fake that borrows a real relentless Effects method carries what that method calls.

    python3 src/RimMandrake/rimflow/selftest_fake_effects_drift.py [selftest_file.py ...]

The class (NIGHTLY_COP_FIX_RED_HDMVNF_XJZW): selftest_priority_list's `Belt(SR.FakeWorld)` binds the real
`pool_order = R.Effects.pool_order`; pool_order grew a `self.first_touch_hold(...)` call, the fake did not, and the nightly
went red with AttributeError. Every fake that binds `<name> = <...>Effects.<method>` drifts the same way when the real
method gains a collaborator. This reads each such fake statically (its own body, `self.X = ...` in its methods, and its
base classes resolved through the file's imports) and the real method's source, and fails on any `self.<name>(...)` call
in the real method that the fake cannot answer. No args: every selftest*.py beside this file. Args: those files only
(how the guard replays the pre-fix instance).
"""
import ast
import inspect
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent / "Utils")]

import relentless as R  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(name)


def _attr_chain(node):
    """`a.b.c` -> ["a", "b", "c"], else None."""
    out = []
    while isinstance(node, ast.Attribute):
        out.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return [node.id] + out[::-1]
    return None


class Module:
    """One parsed file: its top-level classes and its import aliases."""
    cache = {}

    def __init__(self, path):
        self.path = Path(path)
        self.tree = ast.parse(self.path.read_text(encoding="utf-8"), str(self.path))
        self.classes = {}
        for n in ast.walk(self.tree):
            if isinstance(n, ast.ClassDef):
                self.classes.setdefault(n.name, n)
        self.aliases = {}       # local name -> module name
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    self.aliases[a.asname or a.name] = a.name
            elif isinstance(n, ast.ImportFrom) and n.module:
                for a in n.names:
                    self.aliases.setdefault(a.asname or a.name, "%s.%s" % (n.module, a.name))

    @classmethod
    def load(cls, path):
        key = str(Path(path).resolve())
        if key not in cls.cache:
            cls.cache[key] = cls(path)
        return cls.cache[key]

    def module_path(self, modname):
        for root in (self.path.parent, HERE, HERE.parent, HERE.parent / "Utils"):
            p = root / (modname.replace(".", "/") + ".py")
            if p.is_file():
                return p
        return None


def is_effects(chain):
    return bool(chain) and chain[-1] in ("Effects", "GameFx")


def answers(mod, cls_node, seen=None):
    """-> (names the fake class answers, or None when a base cannot be resolved; whether it inherits the real Effects)."""
    seen = seen if seen is not None else set()
    key = (str(mod.path), cls_node.name)
    if key in seen:
        return set(), False
    seen.add(key)
    names = set()
    for n in cls_node.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                for e in (t.elts if isinstance(t, ast.Tuple) else [t]):
                    if isinstance(e, ast.Name):
                        names.add(e.id)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            names.add(n.target.id)
    for n in ast.walk(cls_node):        # self.X = ... anywhere in its methods (a callable may be planted so)
        targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, (ast.AnnAssign, ast.AugAssign)) else []
        for t in targets:
            for e in (t.elts if isinstance(t, ast.Tuple) else [t]):
                if isinstance(e, ast.Attribute) and isinstance(e.value, ast.Name) and e.value.id == "self":
                    names.add(e.attr)
    for b in cls_node.bases:
        chain = _attr_chain(b)
        if chain in (["object"],):
            continue
        if is_effects(chain):
            return names, True
        if not chain:
            return None, False
        if len(chain) == 1 and chain[0] in mod.classes:
            got, eff = answers(mod, mod.classes[chain[0]], seen)
        else:
            modname = mod.aliases.get(chain[0])
            if len(chain) == 1 and modname and "." in modname:      # from x import Base
                modname, cname = modname.rsplit(".", 1)
            elif len(chain) == 2 and modname:
                cname = chain[1]
            else:
                return None, False
            p = mod.module_path(modname)
            if not p:
                return None, False
            other = Module.load(p)
            if cname not in other.classes:
                return None, False
            got, eff = answers(other, other.classes[cname], seen)
        if got is None:
            return None, False
        if eff:
            return names | got, True
        names |= got
    return names, False


def self_calls(func):
    """-> the `self.<name>(...)` calls in a real method's source."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) \
                and n.func.value.id == "self":
            out.add(n.func.attr)
    return out


def bindings(mod):
    """-> [(class node, bound name, real Effects method name)] for `<name> = <...>Effects.<method>` in a class body."""
    out = []
    for cls_node in mod.classes.values():
        for n in cls_node.body:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                chain = _attr_chain(n.value)
                if chain and len(chain) >= 2 and chain[-2] == "Effects":
                    out.append((cls_node, n.targets[0].id, chain[-1]))
    return out


def audit(paths):
    """-> (problems, bindings seen, classes skipped as unresolvable)."""
    problems, seen, skipped = [], 0, []
    for p in paths:
        mod = Module.load(p)
        for cls_node, bound, meth in bindings(mod):
            seen += 1
            real = getattr(R.Effects, meth, None)
            if real is None or not callable(real):
                problems.append("%s:%s binds Effects.%s, which the real Effects no longer has" % (Path(p).name, cls_node.name, meth))
                continue
            have, eff = answers(mod, cls_node)
            if have is None:
                skipped.append("%s:%s" % (Path(p).name, cls_node.name))
                continue
            if eff:
                continue
            missing = sorted(c for c in self_calls(real) if c not in have and not hasattr(object, c))
            if missing:
                problems.append("%s:%s binds Effects.%s, which calls self.%s; the fake answers none of them"
                                % (Path(p).name, cls_node.name, meth, ", self.".join(missing)))
    return problems, seen, skipped


def probe():
    """The instrument can see: a planted fake missing a collaborator is caught, and the same fake with it is not."""
    import tempfile
    d = Path(tempfile.mkdtemp(prefix="selftest_fake_effects_drift_"))
    called = sorted(self_calls(R.Effects.pool_order))
    body = "".join("    def %s(self, *a, **k):\n        return None\n" % c for c in called)
    bad = d / "selftest_planted_bad.py"
    bad.write_text("import relentless as R\n\nclass Fake:\n    pool_order = R.Effects.pool_order\n" + body.replace(
        "    def %s(" % called[0], "    def _gone_%s(" % called[0]), encoding="utf-8")
    good = d / "selftest_planted_good.py"
    good.write_text("import relentless as R\n\nclass Fake:\n    pool_order = R.Effects.pool_order\n" + body, encoding="utf-8")
    pb, nb, _ = audit([bad])
    pg, ng, _ = audit([good])
    check("probe: pool_order calls collaborators (the real source is read)", len(called) >= 3, called)
    check("probe: a fake missing self.%s is caught" % called[0], nb == 1 and len(pb) == 1 and called[0] in pb[0], pb)
    check("probe: the fake that has every collaborator passes", ng == 1 and not pg, pg)


def main(argv):
    probe()
    paths = [Path(a) for a in argv] if argv else sorted(p for p in HERE.glob("selftest*.py") if p.name != Path(__file__).name)
    problems, seen, skipped = audit(paths)
    check("the scan sees fakes that bind a real Effects method (%d bindings over %d files)" % (seen, len(paths)), seen > 0, seen)
    for p in problems:
        check("fake drift", False, p)
    if not problems:
        check("every fake binding a real Effects method answers each self-call it makes", True)
    if skipped:
        print("note: %d fake(s) with a base this reader cannot resolve, not judged: %s" % (len(skipped), ", ".join(skipped)))
    print("selftest_fake_effects_drift: %s (%d fails)" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
