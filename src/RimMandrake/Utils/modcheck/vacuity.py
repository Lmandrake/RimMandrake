"""modcheck.vacuity -- find validation components that cannot fail: they never read anything back.

CODE FIRST (the Jev rule: if a parser answers exactly, a model can only make it worse). A component whose
body contains no `t.expect_*` call, no `raise ExpectationFailed`, no `assert`, and no `check_surroundings`
asserts nothing: its PASS is a statement that setup did not throw. This is the cheap, exact half of the GPT
review's "vacuous-test lint"; components that DO assert go on to jev_triage.lint_vacuous_test (shadow) to
judge whether the assertion reads back the claimed behaviour.

    python3 vacuity.py <validation.py>...        # table of components and what they assert
"""
import ast
import os
import sys

ASSERT_CALLS = ("expect_pawn_despawned", "expect_log_contains", "expect_in_cell_of", "expect_not_in_cell_of",
                "expect_reached_past", "check_surroundings")


def _name(node):
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def _component_name(item):
    call = item.context_expr
    if isinstance(call, ast.Call) and _name(call.func) == "component" and call.args:
        a = call.args[0]
        if isinstance(a, ast.Constant):
            return a.value
    return None


def _is_assert_node(n, helpers):
    if isinstance(n, ast.Call):
        nm = _name(n.func)
        return bool(nm in ASSERT_CALLS or nm == "set_setting" or nm in helpers
                    or (nm and nm.lstrip("_").startswith(("expect", "assert", "check", "verify", "require"))))
    if isinstance(n, ast.Raise):
        return isinstance(n.exc, ast.Call) and _name(n.exc.func) == "ExpectationFailed"
    return isinstance(n, ast.Assert)


def asserting_helpers(tree):
    """Names of module-level functions whose body (transitively, through other such helpers) asserts.
    Without this a component that delegates to `_harmony_owner_present(...)` looked vacuous (MEASURED:
    first pass flagged 48/280, 28 of them helpers)."""
    funcs = dict((f.name, f) for f in tree.body if isinstance(f, ast.FunctionDef)
                 and not any(isinstance(d, ast.Call) and _name(d.func) == "chain" for d in f.decorator_list))
    helpers = set()
    changed = True
    while changed:
        changed = False
        for name, f in funcs.items():
            if name not in helpers and any(_is_assert_node(n, helpers) for n in ast.walk(f)):
                helpers.add(name)
                changed = True
    return helpers


def analyse(path):
    """-> list of {"chain","component","asserts":[...],"verbs":[...],"intent":str} for every component."""
    with open(path) as f:
        tree = ast.parse(f.read(), path)
    helpers = asserting_helpers(tree)
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        if not any(isinstance(d, ast.Call) and _name(d.func) == "chain" for d in fn.decorator_list):
            continue
        intent = (ast.get_docstring(fn) or "").strip().split("\n\n")[0].replace("\n", " ")[:300]
        for w in ast.walk(fn):
            if not isinstance(w, ast.With):
                continue
            for item in w.items:
                cname = _component_name(item)
                if cname is None:
                    continue
                asserts, verbs = [], []
                for n in ast.walk(w):
                    if isinstance(n, ast.Call):
                        nm = _name(n.func)
                        # a local helper named expect*/_expect*/assert*/_check* (PawnFlavor's `_expect_field`) or
                        # set_setting (it reads the field back and raises, suite.py) asserts too
                        if _is_assert_node(n, helpers):
                            asserts.append(nm)
                        elif nm in ("spawn", "spawn_pawn", "bridge_call", "wait_ticks", "walk_over", "order_to",
                                    "set_setting", "ensure_faction", "clear_area"):
                            verbs.append(nm)
                    elif isinstance(n, ast.Raise):
                        ex = n.exc
                        if isinstance(ex, ast.Call) and _name(ex.func) == "ExpectationFailed":
                            asserts.append("raise ExpectationFailed")
                    elif isinstance(n, ast.Assert):
                        asserts.append("assert")
                out.append({"chain": fn.name, "component": cname, "asserts": asserts, "verbs": verbs,
                            "intent": intent, "line": w.lineno})
    return out


def main(paths):
    total = vac = 0
    for p in paths:
        rows = analyse(p)
        bad = [r for r in rows if not r["asserts"]]
        total += len(rows)
        vac += len(bad)
        for r in bad:
            print("VACUOUS %s:%d  %s / %s  (verbs: %s)" % (p, r["line"], r["chain"], r["component"], ",".join(r["verbs"]) or "none"))
    print("%d component(s) scanned, %d assert nothing" % (total, vac))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
