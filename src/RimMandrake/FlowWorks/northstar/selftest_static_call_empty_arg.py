"""Offline selftest: no northstar driver sends jawa/static_call an EMPTY args to a method that only takes parameters.

jawa/static_call reads args="" as ZERO parameters and answers "No public static <M> with 0 params." when the C# method is
`M(string arg)` (live 2026-10-21 reach_map/lines; 2026-10-23 suspension_settings_live ProofButtons -> a row went
UNMEASURED/HARNESS). Item SUSPENSION_PROOF_FIX_EMPTY_ARG_NO_METHOD. The convention is a placeholder arg ("-") the method ignores.

Reads every `public static <T> Name(...)` under src/**/*.cs, then every static_call in the drivers: direct calls
(`B.call("jawa/static_call", method="M", args="")`, args absent counts as empty) and calls through a local wrapper
(`def proof(m, arg): B.call("jawa/static_call", method=m, args=arg)` called as `proof("M", "")`). A wrapper that
sanitises its arg (`args=args or "-"`) is safe. Flags only a name with NO zero-parameter overload anywhere in src (so a
name shared with a 0-param method elsewhere is never a false alarm). Can fail: CASES below must be caught.
"""
import ast
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DRIVERS = tuple(sorted(
    os.path.relpath(f, HERE) for f in glob.glob(os.path.join(HERE, "*.py")) + glob.glob(os.path.join(HERE, "live_probes", "*.py"))
    if not os.path.basename(f).startswith("selftest_") and "jawa/static_call" in open(f, encoding="utf-8").read()))


def cs_param_counts():
    """name -> set of parameter counts over every public static method of that name in src/."""
    counts = {}
    for f in glob.glob(os.path.join(ROOT, "src", "**", "*.cs"), recursive=True):
        if os.sep + "obj" + os.sep in f:
            continue
        txt = open(f, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r'public static (?:[\w<>\[\],.? ]+?) (\w+)\s*\(([^)]*)\)', txt):
            p = m.group(2).strip()
            counts.setdefault(m.group(1), set()).add(0 if not p else p.count(",") + 1)
    return counts


def _const(n):
    return n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None


def _is_static_call(n):
    return (isinstance(n, ast.Call) and n.args and _const(n.args[0]) == "jawa/static_call")


def _kw(call, name):
    for k in call.keywords:
        if k.arg == name:
            return k.value
    return None


def wrappers(tree):
    """fname -> (method param index, args param index or None, args default or None) for local static_call wrappers
    that pass their own params straight through (a BoolOp/other expression on args = sanitised, not a wrapper here)."""
    out = {}
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        params = [a.arg for a in fn.args.args]
        defaults = dict(zip(params[len(params) - len(fn.args.defaults):], fn.args.defaults))
        for c in ast.walk(fn):
            if not _is_static_call(c):
                continue
            mv, av = _kw(c, "method"), _kw(c, "args")
            if not (isinstance(mv, ast.Name) and mv.id in params):
                continue
            if av is None:
                out[fn.name] = (params.index(mv.id), None, "")
            elif isinstance(av, ast.Name) and av.id in params:
                d = defaults.get(av.id)
                out[fn.name] = (params.index(mv.id), params.index(av.id), _const(d) if d is not None else None)
    return out


def check_source(src, counts, name="<src>"):
    out = []
    tree = ast.parse(src)
    wr = wrappers(tree)

    def flag(line, meth, how):
        c = counts.get(meth)
        if c and 0 not in c:
            out.append("%s:%d %s gets an empty args (%s) but every %s overload takes %s param(s)" % (
                name, line, meth, how, meth, sorted(c)))

    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        if _is_static_call(n):
            meth, av = _const(_kw(n, "method")), _kw(n, "args")
            if meth and (av is None or _const(av) == ""):
                flag(n.lineno, meth, "direct, args absent" if av is None else 'direct, args=""')
            continue
        fname = n.func.id if isinstance(n.func, ast.Name) else (n.func.attr if isinstance(n.func, ast.Attribute) else "")
        if fname not in wr:
            continue
        mi, ai, default = wr[fname]
        pos = list(n.args)
        if isinstance(n.func, ast.Attribute) and mi > 0 and len(pos) == mi:   # bound method: self is implicit
            mi, ai = mi - 1, (ai - 1 if ai is not None else None)
        meth = _const(pos[mi]) if mi < len(pos) else None
        if not meth:
            continue
        if ai is None:
            flag(n.lineno, meth, "via %s, which sends no args" % fname)
        elif ai < len(pos):
            if _const(pos[ai]) == "":
                flag(n.lineno, meth, 'via %s("%s", "")' % (fname, meth))
        elif default == "":
            flag(n.lineno, meth, "via %s, args left at its empty default" % fname)
    return out


FAILS = []


def check(label, ok, why=""):
    print("%s  %s %s" % ("ok  " if ok else "FAIL", label, "" if ok else why))
    if not ok:
        FAILS.append(label)


counts = cs_param_counts()
WRAP = 'def proof(m, arg):\n    return B.call("jawa/static_call", type="T", method=m, args=arg)\n'
SAFE = 'def proof(m, arg=""):\n    return B.call("jawa/static_call", type="T", method=m, args=arg or "-")\n'
check("the C# index sees ProofButtons(string arg) as 1-param and RM_WakeMath.Render() as 0-param",
      counts.get("ProofButtons") == {1} and 0 in counts.get("Render", set()), (counts.get("ProofButtons"), counts.get("Render")))
check("can-fail: the 2026-10-23 bug, proof(\"ProofButtons\", \"\") through a wrapper, is caught",
      check_source(WRAP + 'proof("ProofButtons", "")\n', counts) != [])
check("can-fail: a direct static_call with args=\"\" on a 1-param method is caught",
      check_source('B.call("jawa/static_call", type="T", method="ProofButtons", args="")\n', counts) != [])
check("can-fail: a wrapper call leaving args at an empty default is caught",
      check_source(WRAP.replace("(m, arg)", '(m, arg="")') + 'proof("ProofButtons")\n', counts) != [])
check("control: a placeholder arg passes", check_source(WRAP + 'proof("ProofButtons", "-")\n', counts) == [])
check("control: a sanitising wrapper passes", check_source(SAFE + 'proof("ProofButtons")\n', counts) == [])
check("control: a 0-param method with args=\"\" passes",
      check_source('B.call("jawa/static_call", type="T", method="Render", args="")\n', counts) == [])
check("the driver glob found the drivers (not an empty loop)", len(DRIVERS) >= 10, DRIVERS)
for d in DRIVERS:
    probs = check_source(open(os.path.join(HERE, d), encoding="utf-8").read(), counts, d)
    check("%s: no static_call sends an empty args to a parameterised method" % d, not probs, probs)
print("selftest_static_call_empty_arg: %s" % ("FAIL" if FAILS else "ok"))
sys.exit(1 if FAILS else 0)
