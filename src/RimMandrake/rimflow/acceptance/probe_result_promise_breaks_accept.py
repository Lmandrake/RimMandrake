#!/usr/bin/env python3
"""Each promise on design/specs/2026-11-19-probe-result/boundary.md has a test of its name that turns red when the code
breaks that promise (RIMMANDRAKE_SHARE_PROBE_RESULT_TYPE_NINE_FILES_ROLL_OWN; built like
control_promise_breaks_accept.py). One deliberately broken stand-in per promise is made in a private copy of
probe_result.py, could_not_look_lint.py and their selftest (temp dir); the real files are never edited. First the
unbroken copy must pass every named test, else a test that always fails would read as a catch.

  exit 0  PASS: every break rejected by its named test
  exit 1  FAIL: a break slipped past (its named test passed), each named
  exit 3  COULD NOT LOOK: a break no longer matches its file exactly once, or the unbroken copy fails a named test
          (cause named); not a verdict about the tests

`--only <promise> ...` runs those promises alone."""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
PAGE = os.path.join(REPO, "design", "specs", "2026-11-19-probe-result", "boundary.md")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import boundary_check as B  # noqa: E402

COPY = ("src/RimMandrake/rimflow/probe_result.py", "src/RimMandrake/rimflow/selftest_probe_result.py",
        "src/RimMandrake/Utils/could_not_look_lint.py", "src/RimMandrake/Utils/publish_tree_checks.json")
TYPE, LINT = COPY[0], COPY[2]
BREAKS = {}     # promise -> (the break in one line, file, [(text, its replacement)])


def brk(promise, what, path, *edits):
    BREAKS[promise] = (what, path, list(edits))


brk("probe-never-lies", "__bool__ reads the raw content, so `blind or []` is []", TYPE,
    ("    def __bool__(self):\n        return bool(self.value)", "    def __bool__(self):\n        return bool(self._v)"))
brk("blind-answers-keep-their-cause", "a blind answer drops its cause", TYPE,
    ("return Answer(kind, cause=str(cause))", "return Answer(kind, cause='')"))
brk("looked-answers-read-plainly", "indexing a value always reads its first item", TYPE,
    ("        return self.value[i]", "        return self.value[0]"))
brk("four-answers-never-blur", "value() of a blind answer passes it through", TYPE,
    ("        x.value     # noqa: B018  raises NotAnswered on a blind answer\n", ""))
brk("lint-sees-both-shapes", "the except shape is never looked for", LINT,
    ("            if isinstance(n, ast.ExceptHandler):", "            if False:"))
brk("lint-allowlist-is-counted", "any allowance, however small, covers every hit under its key", LINT,
    ("        if seen[k] > allowed.get(k, 0):", "        if not allowed.get(k, 0):"))
brk("lint-shadow-refuses-nothing", "--shadow still exits 1 on a red", LINT,
    ('    return 0 if shadow else rc', '    return rc'))


def one(tree, promise):
    """-> (exit code, last line) of the promise's named test in `tree`."""
    r = subprocess.run([sys.executable, os.path.join(tree, COPY[1]), "--only", B.test_name(promise)], cwd=tree,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, ((r.stdout + r.stderr).strip().splitlines() or ["(no output)"])[-1]


def fresh_tree():
    d = tempfile.mkdtemp(prefix="probe_breaks_")
    for rel in COPY:
        if not os.path.isfile(os.path.join(REPO, rel)):
            continue    # a break aimed at it then matches 0 times: COULD NOT LOOK, never a catch
        os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), os.path.join(d, rel))
    return d


def main(argv):
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    names = [p for p in B.promises(PAGE) if only is None or p in only]
    missing = [p for p in names if p not in BREAKS]
    if missing:
        print("COULD NOT LOOK: no break written for promise(s) %s" % ", ".join(missing))
        return 3
    base = fresh_tree()
    try:
        for p in names:
            rc, last = one(base, p)
            if rc != 0:
                print("COULD NOT LOOK: the unbroken copy fails %s (%s): %s" % (B.test_name(p), p, last))
                return 3
    finally:
        shutil.rmtree(base, ignore_errors=True)
    slipped = []
    for p in names:
        what, rel, edits = BREAKS[p]
        tree = fresh_tree()
        try:
            path = os.path.join(tree, rel)
            text = open(path, encoding="utf-8").read() if os.path.isfile(path) else ""
            for old, new in edits:
                if text.count(old) != 1:
                    print("COULD NOT LOOK: break for %s matches %s %d times, not once: %r" % (p, rel, text.count(old),
                                                                                             old[:60]))
                    return 3
                text = text.replace(old, new)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            rc, last = one(tree, p)
        finally:
            shutil.rmtree(tree, ignore_errors=True)
        print("%s %s: %s  (%s)" % ("caught " if rc != 0 else "SLIPPED", p, what, last[:100]))
        if rc == 0:
            slipped.append(p)
    if slipped:
        print("FAIL probe_result_promise_breaks: %d of %d breaks slipped past: %s" % (len(slipped), len(names),
                                                                                   ", ".join(slipped)))
        return 1
    print("PASS probe_result_promise_breaks: %d of %d breaks rejected by their named test" % (len(names), len(names)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
