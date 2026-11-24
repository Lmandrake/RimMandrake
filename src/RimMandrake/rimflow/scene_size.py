#!/usr/bin/env python3
"""THE SCENE SIZE CHECK: an oversized live scene carries its evidence that no cheaper test decides its bar. No AI.

Owner, 2026-11-24, of Pyrelands' sc_walk (39 runs of Stage 6, one live scene of two game weeks, his full list and about ten
claims): "WHAT is being actually tested here? Should it even be tested? And if so, what's the MINIMUM test necessary to show
it?" The rule it checks: design/RimMandrake/standing_rulings.md §The cheapest test that decides the bar. Page:
design/specs/2026-11-24-scene-size/boundary.md.

A stage-6 live test of a test table is OVERSIZED when one of these is measured:
  span     it plays more than SPAN_DAYS game days (`game_days` of the entry, else the waits its entry reaches in its .py file)
  list     it runs on the full list (kind live_full, or `why_full_list`)
  claims   it holds more than one claim: `claims`, a list on the entry. An entry that declares none is read from the clauses of
           its `observes` (split at ';', a "log clean" clause left out), and CLAUSES or more of them read as several claims
A test on the full list is refused, whatever its evidence (owner, 2026-11-24: retired until the integration phase).
Any other oversized test owes `cheaper_why` on its entry: why a cheaper, faster, simpler test cannot decide the same bar. A span that
cannot be read is UNMEASURED, never small and never oversized.

  scene_size.py check [--mod M ...] [--table FILE] [--all]   one line per finding; --all lists the known ones too
  exit 0 no new finding; 1 a new oversized test with no cheaper_why; 2 a table could not be read (could not look)
KNOWN (scene_size_known.json) lists the tests found oversized on the day the check was made, each with the measures found; one
that grows past them is new. RIMMANDRAKE_SHRINK_OVERSIZED_SCENES_IN_EVERY_MOD_AFTER_PYRE empties the list. Nothing adds to it.
"""
import argparse
import ast
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KNOWN = os.path.join(HERE, "scene_size_known.json")
# LIMIT. Danger: past a day the colony sleeps, eats and drinks, wild animals hunt and arrivals come, and any of them spoils the
# scene. Evidence: Pyrelands sc_walk spoiled in visits 2, 5 and 8 (run 1) (2026-11-21 to 2026-11-24); in visit 8 fresh_burn_bonus
# was spoiled on day 1 and burn_line on day 4 by wild predators. Stage 6 of Pyrelands ran 39 times; visit 8 alone took six hours.
SPAN_DAYS = 1.0
# LIMIT. Danger: a scene that decides many things at once loses all of them when one is spoiled. Evidence: sc_walk, 7 clauses,
# every part UNMEASURED in visits 2 and 8 run 1. Below this many clauses several usually state one claim (a rise and its control),
# so a clause count is a proxy only where the entry declares no `claims`.
CLAUSES = 5
DAY = 60000
# Owner, 2026-11-24 ("go"): full-list testing is retired until the integration phase. No evidence buys a full-list test now.
# FULL_LEFT names each test that still stands on it, with why; nothing else may. Empty since Pyrelands visit 9 ended.
FULL_LEFT = {}
FULL_REPAIR = ("run the same scene on the mod's small list (kind live_minimal, its tier in small_list.json), or take it out of the table "
               "and write its claim on design/RimMandrake/integration_phase_list.md (design/RimMandrake/standing_rulings.md "
               "§Mod development runs on small lists)")
WAITS = ("_wait", "wait_ticks", "_wait_raw", "_r6_tick_on", "wait", "advance_ticks")
REPAIR = ("write the cheaper scene (one claim, the least list, the shortest advance), or say in `cheaper_why` of its test-table "
          "entry why a cheaper, faster, simpler test cannot decide the same bar (design/RimMandrake/standing_rulings.md §The "
          "cheapest test that decides the bar)")


def _txt(v):
    return isinstance(v, str) and bool(v.strip())


# ---- the span, read from the script -----------------------------------------------------------------------------------

def _fold(n, env):
    """A constant expression's number, or None."""
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        return n.value
    if isinstance(n, ast.Name):
        return env.get(n.id)
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        v = _fold(n.operand, env)
        return None if v is None else -v
    if isinstance(n, ast.BinOp):
        a, b = _fold(n.left, env), _fold(n.right, env)
        if a is None or b is None:
            return None
        op = type(n.op)
        if op in (ast.Div, ast.FloorDiv):
            return None if not b else a / b if op is ast.Div else a // b
        return a + b if op is ast.Add else a - b if op is ast.Sub else a * b if op is ast.Mult else None
    return None


def _loops(it, env):
    """How often a `for` runs when that is a constant, else None."""
    if isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id == "range" and 1 <= len(it.args) <= 2:
        v = [_fold(a, env) for a in it.args]
        return None if None in v else max(0, int(v[-1] - (v[0] if len(v) == 2 else 0)))
    if isinstance(it, (ast.Tuple, ast.List)) and not any(isinstance(e, ast.Starred) for e in it.elts):
        return len(it.elts)
    return None


def _name(call):
    f = call.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None


def script(text):
    """A script read once: (its constants, its functions, what is already counted)."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tree = ast.parse(text)
    env, defs = {}, {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            v = _fold(n.value, env)
            if v is not None:
                env[n.targets[0].id] = v
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            defs.setdefault(n.name, n)
    return env, defs, {}


def span_ticks(text, entry, read=None):
    """-> (ticks the entry plays at least, waits it could not read), or None when the file has no such function. A wait whose
    length or loop is no constant counts one pass or nothing, and is counted as unread; so the number is a floor."""
    env, defs, memo = read or script(text)
    if entry not in defs:
        return None

    def fn(name, stack):
        if name in stack:
            return 0, 0
        if name not in memo:
            memo[name] = body(defs[name].body, stack | {name})
        return memo[name]

    def body(nodes, stack):
        t = u = 0
        for n in nodes:
            a, b = visit(n, stack)
            t, u = t + a, u + b
        return t, u

    def visit(n, stack):
        if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Lambda)):
            return 0, 0
        if isinstance(n, ast.For):
            k = _loops(n.iter, env)
            t, u = body(n.body, stack)
            return (t * k, u) if k is not None else (t, u + (1 if t else 0))
        if isinstance(n, ast.While):
            t, u = body(n.body, stack)
            return t, u + (1 if t else 0)
        if isinstance(n, ast.If):
            x, y = body(n.body, stack), body(n.orelse, stack)
            return max(x, y)
        t = u = 0
        if isinstance(n, ast.Call):
            name = _name(n)
            if name in WAITS:
                v = [x for x in (_fold(a, env) for a in n.args) if x is not None]
                t, u = (v[-1], 0) if v else (0, 1)
                return t, u
            if name in defs and isinstance(n.func, ast.Name):
                t, u = fn(name, stack)
        a, b = body(list(ast.iter_child_nodes(n)), stack)
        return t + a, u + b
    return fn(entry, frozenset())


def claims_of(spec):
    """-> how many claims a test holds: its `claims` list, else 1, or the clause count of `observes` from CLAUSES up."""
    c = spec.get("claims")
    if isinstance(c, list):
        return len([x for x in c if _txt(x)])
    n = len([x for x in str(spec.get("observes") or "").split(";") if x.strip() and not re.match(r"^log clean\W*$", x.strip())])
    return n if n >= CLAUSES else 1


def measure(spec, root=REPO, _files=None):
    """-> {"days": number or None, "unread": waits not read or None, "full": bool, "claims": n}."""
    days, unread = spec.get("game_days"), 0
    if isinstance(days, bool) or not isinstance(days, (int, float)):
        days, unread = None, None
        f, e = spec.get("file"), spec.get("entry")
        if _txt(f) and f.endswith(".py") and _txt(e):
            files = {} if _files is None else _files
            try:
                if f not in files:
                    with open(os.path.join(root, f), encoding="utf-8") as h:
                        files[f] = script(h.read())
                r = span_ticks(None, e, files[f]) if files[f] else None
            except (OSError, SyntaxError, ValueError):
                r = files[f] = None
            if r is not None:
                days, unread = round(r[0] / float(DAY), 3), r[1]
    return {"days": days, "unread": unread, "full": spec.get("kind") == "live_full" or _txt(spec.get("why_full_list")),
            "claims": claims_of(spec)}


def over(m):
    """-> the measures that make a test oversized, in words ([] is not oversized)."""
    out = []
    if m["days"] is not None and m["days"] > SPAN_DAYS:
        out.append("plays %s%.1f game days (limit %g)" % ("at least " if m["unread"] else "", m["days"], SPAN_DAYS))
    if m["full"]:
        out.append("runs on the full list")
    if m["claims"] > 1:
        out.append("holds %d claims" % m["claims"])
    return out


def live_tests(tt):
    ts = (tt or {}).get("tests") if isinstance(tt, dict) else None
    return dict((k, v) for k, v in (ts or {}).items() if isinstance(v, dict) and str(v.get("kind") or "").startswith("live")
                and str(v.get("stage")) == "6") if isinstance(ts, dict) else {}


def owed(tt, root=REPO):
    """-> {test id: (measures, [words])} of the oversized tests with no `cheaper_why`."""
    files, out = {}, {}
    for k, v in live_tests(tt).items():
        if _txt(v.get("cheaper_why")):
            continue
        m = measure(v, root, files)
        w = over(m)
        if w:
            out[k] = (m, w)
    return out


def grown(m, known):
    """True when a known oversized test is larger now than the day it was listed."""
    k = known or {}
    return bool((m["full"] and not k.get("full")) or m["claims"] > (k.get("claims") or 0)
                or (m["days"] or 0) > (k.get("days") or 0) + 0.05)


def load_known(path=KNOWN):
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("tests") or {}


def check(tables, root=REPO, known=None, left=None):
    """tables: {mod: parsed table}. -> (new, old): lines [(mod, test, words)]. A test on the full list is always new, whatever its
    evidence, unless `left` (FULL_LEFT) names it."""
    known = load_known() if known is None else known
    left = FULL_LEFT if left is None else left
    new, old = [], []
    for mod, tt in sorted(tables.items()):
        for t, v in sorted(live_tests(tt).items()):
            if (v.get("kind") == "live_full" or _txt(v.get("why_full_list"))) and (mod, t) not in left:
                new.append((mod, t, ["asks for the full list, which is retired: %s" % FULL_REPAIR]))
        asked = {t for m_, t, _w in new if m_ == mod}
        for t, (m, w) in sorted(owed(tt, root).items()):
            if t in asked:
                continue
            k = (known.get(mod) or {}).get(t)
            (new if k is None or grown(m, k) else old).append((mod, t, w))
    return new, old


def brief_lines(root, mod, tt):
    """The in-game brief's section: each oversized check of this mod that owes its evidence. [] when none."""
    return ["- `%s` %s: %s" % (t, "; ".join(w), REPAIR) for t, (_m, w) in sorted(owed(tt, root).items())]


def main(argv=None):
    p = argparse.ArgumentParser(description="an oversized live scene carries its evidence (cheaper_why)")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--mod", action="append", default=[])
    c.add_argument("--table", help="read this test table instead (with --mod, its name)")
    c.add_argument("--all", action="store_true", help="list the known ones too")
    a = p.parse_args(argv)
    paths = [a.table] if a.table else sorted(glob.glob(os.path.join(REPO, "design", "concepts", "*", "version", "test_table.json")))
    tables, bad = {}, []
    for f in paths:
        mod = a.mod[0] if a.table and a.mod else os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(f))))
        if a.mod and mod not in a.mod:
            continue
        try:
            with open(f, encoding="utf-8") as h:
                tables[mod] = json.load(h)
        except (OSError, ValueError) as e:
            bad.append("%s: %s" % (f, e))
    for x in bad:
        print("COULD NOT LOOK %s" % x)
    if not tables and not bad:
        print("COULD NOT LOOK: no test table%s" % (" of %s" % ", ".join(a.mod) if a.mod else ""))
        return 2
    try:
        known = load_known()
    except (OSError, ValueError) as e:
        print("COULD NOT LOOK scene_size_known.json: %s" % e)
        return 2
    new, old = check(tables, REPO, known)
    for mod, t, w in new:
        print("NEW   %s %s: %s%s" % (mod, t, "; ".join(w), "" if FULL_REPAIR in w[0] else ". " + REPAIR))
    if a.all:
        for mod, t, w in old:
            print("known %s %s: %s" % (mod, t, "; ".join(w)))
    print("scene size: %d table(s), %d new oversized, %d known" % (len(tables), len(new), len(old)))
    return 2 if bad else 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
