"""modcheck.vacuity -- find validation components that cannot fail: they never read anything back.

CODE FIRST (the Jev rule: if a parser answers exactly, a model can only make it worse). A component whose
body contains no `t.expect_*` call, no `raise ExpectationFailed` and no `assert`
asserts nothing: its PASS is a statement that setup did not throw. `check_surroundings`, `checkpoint` and `expect` read
nothing back, so they earn no credit; a call to `_unmeasured` (or setting `upstream_failed`) earns it: that row can never
go green. Code a component only DEFINES, and `if False:` branches, never run and earn nothing. This is the cheap, exact half of the GPT
review's "vacuous-test lint"; components that DO assert go on to jev_triage.lint_vacuous_test (shadow) to
judge whether the assertion reads back the claimed behaviour.

    python3 vacuity.py <validation.py>...        # table of components and what they assert
    python3 vacuity.py --repo                    # every component under src/, minus vacuity_baseline.json

`selftest_northstar_adversarial_round.py` runs --repo, so a NEW component that asserts nothing fails the suite (it was a lint nobody ran:
two rows it could already name sat PASS for weeks, NORTHSTAR_ADVERSARIAL_REVIEW_1 round 1).
"""
import ast
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
BASELINE = os.path.join(HERE, "vacuity_baseline.json")

ASSERT_CALLS = ("expect_pawn_despawned", "expect_log_contains", "expect_in_cell_of", "expect_not_in_cell_of",
                "expect_reached_past")
NO_CREDIT = ("check_surroundings", "checkpoint", "expect")   # named like asserts; none can fail a component


def live_nodes(node):
    """ast.walk minus what never runs: nested def/lambda bodies (helpers earn credit when CALLED) and `if False:`."""
    todo = [node]
    while todo:
        n = todo.pop()
        yield n
        for c in ast.iter_child_nodes(n):
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            if isinstance(c, ast.If) and isinstance(c.test, ast.Constant) and not c.test.value:
                todo.extend(c.orelse)
                continue
            todo.append(c)


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
        # a computed name (`"%s_flips" % f`) is still a row: skipping it hid a tenth of the components
        return a.value if isinstance(a, ast.Constant) else ast.unparse(a)
    return None


def _is_assert_node(n, helpers):
    if isinstance(n, ast.Call):
        nm = _name(n.func)
        if nm in NO_CREDIT:
            return False
        return bool(nm in ASSERT_CALLS or nm == "set_setting" or nm in helpers
                    or (nm and "unmeasured" in nm.lower())
                    or (nm and nm.lstrip("_").startswith(("expect", "assert", "check", "verify", "require"))))
    if isinstance(n, ast.Raise):
        return isinstance(n.exc, ast.Call) and _name(n.exc.func) == "ExpectationFailed"
    if isinstance(n, ast.Assign):
        return any(isinstance(x, ast.Attribute) and x.attr == "upstream_failed" for x in n.targets) \
            and isinstance(n.value, ast.Constant) and n.value.value is True
    return isinstance(n, ast.Assert)


def asserting_helpers(tree):
    """Names of module-level functions whose body (transitively, through other such helpers) asserts.
    Without this a component that delegates to `_harmony_owner_present(...)` looked vacuous (MEASURED:
    first pass flagged 48/280, 28 of them helpers)."""
    funcs = dict((f.name, f) for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)
                 and not any(isinstance(d, ast.Call) and _name(d.func) == "chain" for d in f.decorator_list))
    helpers = set()
    changed = True
    while changed:
        changed = False
        for name, f in funcs.items():
            if name not in helpers and any(_is_assert_node(n, helpers) for n in live_nodes(f)):
                helpers.add(name)
                changed = True
    return helpers


def analyse(path):
    """-> list of {"chain","component","asserts":[...],"verbs":[...],"intent":str} for every component."""
    with open(path, encoding="utf-8", errors="replace") as f:
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
                for n in live_nodes(w):
                    if isinstance(n, ast.Yield):
                        asserts.append("yield (wrapper: the caller's body is the row)")
                    if isinstance(n, ast.Assign) and _is_assert_node(n, helpers):
                        asserts.append("upstream_failed")
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


def scan_repo(root=REPO):
    """Every chain component under src/, as `path|chain|component` -> line, for rows that assert nothing."""
    bad, total = {}, 0
    for p in sorted(glob.glob(os.path.join(root, "src", "**", "*.py"), recursive=True)):
        with open(p, encoding="utf-8", errors="replace") as f:
            text = f.read()
        if ".component(" not in text or os.path.basename(p).startswith("selftest") or ".chain(" not in text:
            continue
        try:
            rows = analyse(p)
        except SyntaxError:
            continue
        total += len(rows)
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        for r in rows:
            if not r["asserts"]:
                bad["%s|%s|%s" % (rel, r["chain"], r["component"])] = r["line"]
    return bad, total


def new_vacuous(root=REPO):
    """-> (rows not in the baseline, baseline rows that no longer exist, components scanned)."""
    bad, total = scan_repo(root)
    with open(BASELINE, encoding="utf-8") as f:
        base = json.load(f)["rows"]
    return sorted(set(bad) - set(base)), sorted(set(base) - set(bad)), total


def main(paths):
    if paths == ["--repo"]:
        new, gone, total = new_vacuous()
        for r in new:
            print("VACUOUS " + r)
        for r in gone:
            print("BASELINE-STALE " + r)
        print("%d component(s) scanned, %d new, %d stale baseline" % (total, len(new), len(gone)))
        return 1 if new or gone else 0
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
