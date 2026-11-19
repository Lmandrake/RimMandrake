#!/usr/bin/env python3
"""Offline selftest of probe_result.py and could_not_look_lint.py: one test per promise on
design/specs/2026-11-19-probe-result/boundary.md, each named after it (boundary_check.py reads that).

    python3 src/RimMandrake/rimflow/selftest_probe_result.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_probe_result.py --only t_x ...  those alone (the promise-breaks check)
"""
import json
import operator
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LINT = os.path.join(HERE, "..", "Utils", "could_not_look_lint.py")
TMP = tempfile.mkdtemp(prefix="selftest_probe_result_")
FAILS = []


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def refuses(fn):
    """True when fn() raises NotAnswered (any other outcome, another exception included, is False)."""
    import probe_result as P
    try:
        fn()
    except P.NotAnswered:
        return True
    except Exception:       # noqa: BLE001  a TypeError is not the promise: the raise must name the cause
        return False
    return False


def lint(text, *args, name="fixture.py"):
    """-> (exit code, output) of the lint on one fixture file holding `text`."""
    p = os.path.join(TMP, name)
    with open(p, "w") as f:
        f.write(text)
    r = subprocess.run([sys.executable, LINT, "--files", p] + list(args), capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


def flagged(out, name="fixture.py"):
    """-> the line numbers the lint named in `name`."""
    words = [os.path.basename(w) for ln in out.splitlines() for w in ln.split()]
    return sorted(int(w.split(":")[1]) for w in words if w.startswith(name + ":") and w.split(":")[1].isdigit())


def t_probe_never_lies():
    """A could-not-look or failed answer raises at once as a truth value, a list or a number."""
    import probe_result as P
    for b in (P.could_not_look("systemctl show failed (rc 1)"), P.failed("store raised OSError")):
        uses = {"bool": lambda: bool(b), "x or []": lambda: b or [], "list": lambda: list(b), "len": lambda: len(b),
                "for": lambda: [x for x in b], "index": lambda: b[0], "in": lambda: 1 in b, "int": lambda: int(b),
                "float": lambda: float(b), "operator.index": lambda: operator.index(b), ".value": lambda: b.value,
                "if": lambda: 1 if b else 0}
        slipped = [k for k, fn in uses.items() if not refuses(fn)]
        check(not slipped, "%s raises NotAnswered on every use as an answer" % b.kind, slipped)
    try:
        bool(P.could_not_look("cgroup.procs unreadable"))
        said = ""
    except P.NotAnswered as e:
        said = str(e)
    check("cgroup.procs unreadable" in said, "the raise names the cause", said)


def t_blind_answers_keep_their_cause():
    """Each blind answer keeps its cause; str() names the kind and the cause; a blank cause is refused."""
    import probe_result as P
    c, f = P.could_not_look("systemctl timed out"), P.failed("boom")
    check(c.cause == "systemctl timed out" and f.cause == "boom", "the cause is kept", (c.cause, f.cause))
    check("could not look" in str(c).lower() and "systemctl timed out" in str(c), "str() of could-not-look", str(c))
    check("failed" in str(f).lower() and "boom" in str(f), "str() of failed", str(f))
    check("boom" in repr(f) and "%s" % f, "repr() and %-formatting never raise", repr(f))
    blank = []
    for mk in (P.could_not_look, P.failed):
        for cause in ("", "   ", None):
            try:
                mk(cause)
                blank.append((mk.__name__, cause))
            except ValueError:
                pass
    check(not blank, "a blank cause is refused", blank)


def t_looked_answers_read_plainly():
    """value(x) reads as x; empty() reads as an empty list and is false."""
    import probe_result as P
    v = P.value([4, 5])
    check(list(v) == [4, 5] and len(v) == 2 and v[1] == 5 and 4 in v and bool(v) and v.value == [4, 5],
          "value([4, 5]) reads as the list", v)
    check((P.value([]) or ["x"]) == ["x"] and not P.value(0) and int(P.value(3)) == 3 and P.value(None).value is None,
          "a measured [] / 0 / None reads as itself")
    e = P.empty()
    check(list(e) == [] and len(e) == 0 and not e and (e or [9]) == [9] and e.value == [] and 7 not in e,
          "empty() reads as an empty list and is false")


def t_four_answers_never_blur():
    """kind is one of four; ok is true for value and empty only; value() of a blind answer raises."""
    import probe_result as P
    ans = [P.value(1), P.empty(), P.could_not_look("c"), P.failed("f")]
    check([a.kind for a in ans] == ["value", "empty", "could_not_look", "failed"] and tuple(P.KINDS) == (
        "value", "empty", "could_not_look", "failed"), "the four kinds", [a.kind for a in ans])
    check([a.ok for a in ans] == [True, True, False, False], "ok is true for value and empty only", [a.ok for a in ans])
    check([a.cause for a in ans[:2]] == [None, None], "a looked answer has no cause")
    check(refuses(lambda: P.value(P.could_not_look("c"))) and refuses(lambda: P.value(P.failed("f"))),
          "value() of a blind answer raises")
    check(P.value(P.value(2)).value == 2 and P.value(P.empty()).kind == "empty", "value() of a looked answer is it")


SHAPES = """\
def a(cg):
    return (_procs(cg) or [])
def b():
    x = load() or {}
    y = m.read() or ""
    return x, y
def c():
    try:
        return read()
    except OSError:
        return []
def d():
    try:
        return read()
    except OSError:
        return None
def e(d, r, n):
    k = d.get("k") or []
    s = r.stdout or ""
    t = n or 0
    try:
        return read()
    except OSError as e:
        raise Unreadable(str(e))
def f():
    return (g() or ())
def h():
    return len(x) or 0
"""


def t_lint_sees_both_shapes():
    """`<call> or <empty>` and an except returning an empty are named file:line; .get / a name / an attribute is not."""
    rc, out = lint(SHAPES)
    check(rc == 1 and flagged(out) == [2, 4, 5, 11, 16, 26, 28], "the lint names exactly the shaped lines", (rc, out))
    rc, out = lint("def f():\n    r = _procs(cg)\n    if r is None:\n        raise RuntimeError('blind')\n    return r\n")
    check(rc == 0 and not flagged(out), "a read that says could-not-look is green", (rc, out))


def t_lint_allowlist_is_counted():
    """Two hits in one function: an allowance of 1 is red, 2 green; a moved line changes nothing; --prune drops
    slack."""
    two = "def a():\n    x = f() or []\n    y = g() or []\n    return x, y\n"
    al = os.path.join(TMP, "allow.json")

    def allow(n):
        with open(al, "w") as fh:
            json.dump({"places": {"%s::a::or-empty" % os.path.join(TMP, "count.py"): n}}, fh)
    allow(1)
    rc, out = lint(two, "--allowlist", al, name="count.py")
    check(rc == 1 and flagged(out, "count.py") == [3], "a hit beyond its count is red", (rc, out))
    allow(2)
    rc, out = lint(two, "--allowlist", al, name="count.py")
    check(rc == 0, "within its count it is green", (rc, out))
    rc, out = lint("# a line above\n\n" + two, "--allowlist", al, name="count.py")
    check(rc == 0, "a line moving inside its function changes nothing", (rc, out))
    allow(5)
    rc, out = lint(two, "--allowlist", al, "--prune", name="count.py")
    with open(al) as fh:
        left = json.load(fh)["places"]
    check(rc == 0 and list(left.values()) == [2], "--prune leaves the count that is still open", (rc, left))


def t_lint_shadow_refuses_nothing():
    """--shadow prints the count and each new hit and exits 0, an unreadable file included; ./publish runs it so."""
    rc, out = lint(SHAPES, "--shadow")
    check(rc == 0 and flagged(out) == [2, 4, 5, 11, 16, 26, 28] and "SHADOW" in out, "shadow prints and exits 0",
          (rc, out[-300:]))
    rc, out = lint("def f(:\n", name="broken.py")
    check(rc == 3 and "UNREADABLE" in out, "an unparsable file is UNREADABLE, exit 3", (rc, out))
    rc, out = lint("def f(:\n", "--shadow", name="broken.py")
    check(rc == 0 and "UNREADABLE" in out, "and under --shadow it is said and refuses nothing", (rc, out))
    cfg = os.path.join(HERE, "..", "Utils", "publish_tree_checks.json")
    with open(cfg, encoding="utf-8") as fh:
        rows = [c for c in json.load(fh)["checks"] if c["test"].endswith("could_not_look_lint.py")]
    check(len(rows) == 1 and rows[0].get("shadow") is True and "--shadow" in rows[0].get("args", []),
          "./publish runs the lint as a shadow check", rows)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_probe_never_lies, t_blind_answers_keep_their_cause, t_looked_answers_read_plainly,
              t_four_answers_never_blur, t_lint_sees_both_shapes, t_lint_allowlist_is_counted,
              t_lint_shadow_refuses_nothing):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_probe_result")
    return 0


if __name__ == "__main__":
    sys.exit(main())
