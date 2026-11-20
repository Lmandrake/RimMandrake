#!/usr/bin/env python3
"""selftest_code_review_page_state.py — `code_review_status.py check` reads CLEAN only against a page of promises.

    python3 src/RimMandrake/Utils/selftest_code_review_page_state.py

Each test carries the name of a promise on `design/specs/2026-11-19-clean-means-promises-tested/boundary.md`. The
tests build throwaway repo roots in a temp folder (CODE_REVIEW_STATUS_ROOT, and `CRS.ROOT` / `CRS.PAGES` set per
root), so they never read this repo's pages, tests or review records.
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

TMP = tempfile.mkdtemp(prefix="crs_page_selftest_")
os.environ["CODE_REVIEW_STATUS_ROOT"] = TMP
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import code_review_status as CRS  # noqa: E402  (after the env var)

FAILS = []


def eq(got, want, what):
    if got != want:
        FAILS.append("%s: got %r, want %r" % (what, got, want))


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


TESTS_OK = """import os, sys
def t_does_one_thing():
    pass
def t_does_another_thing():
    pass
def main():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs.log"), "a") as f:
        f.write("run\\n")
    t_does_one_thing()
    t_does_another_thing()
    return %d
if __name__ == "__main__":
    sys.exit(main())
"""

PAGE = """# BOUNDARY: a thing

Code: `src/pkg/one.py` (`f`), `two.py` and `pkg/three.py`. Item: `X`. Not code: `src/pkg/later.py`.

## PROMISES

- **does-one-thing.** One.
- **does-another-thing.** Two.
"""


def root(name, pages, tests_rc=0, page_text=PAGE):
    """A fresh repo root with src/pkg/{one,two,three,later,four}.py and one page per entry of `pages`."""
    r = os.path.join(TMP, name)
    shutil.rmtree(r, ignore_errors=True)
    for f in ("one", "two", "three", "later", "four"):
        write(r, "src/pkg/%s.py" % f, "x = 1\n")
    reg = {}
    for page, tests in pages.items():
        write(r, page, page_text)
        if tests:
            write(r, tests, TESTS_OK % tests_rc)
            reg[page] = tests
    CRS.ROOT = r
    CRS.PAGES = reg
    os.chdir(r)  # relative paths resolve from the cwd, as on the command line
    return r


def check(*paths, record=False):
    """-> (exit code, {rel: (state, line)}) of `check` run as main() runs it."""
    argv = ["code_review_status.py", "check"] + (["--record"] if record else []) + list(paths)
    old, sys.argv = sys.argv, argv
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            try:
                CRS.main()
                rc = 0
            except SystemExit as e:
                rc = e.code or 0
    except Exception as e:  # a crash is a failed promise, not a crashed selftest
        rc = "crash %s: %s" % (type(e).__name__, e)
    finally:
        sys.argv = old
    rows = {}
    for ln in buf.getvalue().splitlines():
        for state in ("NO PAGE", "UNREADABLE", "UNREVIEWABLE", "CLEAN", "DIRTY"):
            if ln.startswith(state + "  "):
                rows[ln[len(state) + 2:].split("  ")[0]] = (state, ln)
    return rc, rows


def state(rows, rel):
    return rows.get(rel, ("absent", ""))[0]


def t_clean_needs_a_page_and_passing_tests():
    root("clean", {"design/specs/p/boundary.md": "tests/t_p.py"})
    rc, rows = check("src/pkg/one.py", "src/pkg/two.py", "src/pkg/three.py")
    eq(rc, 0, "clean: exit")
    for rel in ("src/pkg/one.py", "src/pkg/two.py", "src/pkg/three.py"):
        eq(state(rows, rel), "CLEAN", "clean: %s (full, bare and partial names on the Code sentence)" % rel)
    eq("promises covered 2 of 2" in rows.get("src/pkg/one.py", ("", ""))[1], True, "clean: detail names the count")
    eq("design/specs/p/boundary.md" in rows.get("src/pkg/one.py", ("", ""))[1], True, "clean: detail names the page")


def t_a_promise_without_a_test_is_dirty():
    root("missing", {"design/specs/p/boundary.md": "tests/t_p.py"},
         page_text=PAGE + "- **does-a-third-thing.** Three.\n")
    rc, rows = check("src/pkg/one.py")
    eq(rc, 1, "missing test: exit")
    eq(state(rows, "src/pkg/one.py"), "DIRTY", "missing test: state")
    line = rows.get("src/pkg/one.py", ("", ""))[1]
    eq("does-a-third-thing" in line and "t_does_a_third_thing" in line, True, "missing test: detail names it")


def t_a_red_tests_file_is_dirty():
    root("red", {"design/specs/p/boundary.md": "tests/t_p.py"}, tests_rc=1)
    rc, rows = check("src/pkg/one.py")
    eq(rc, 1, "red tests: exit")
    eq(state(rows, "src/pkg/one.py"), "DIRTY", "red tests: state")
    line = rows.get("src/pkg/one.py", ("", ""))[1]
    eq("tests/t_p.py" in line and "exit 1" in line, True, "red tests: detail names the file and exit")


def t_no_page_is_its_own_answer():
    root("nopage", {"design/specs/p/boundary.md": "tests/t_p.py"})
    rc, rows = check("src/pkg/four.py")
    eq(rc, 4, "no page: exit")
    eq(state(rows, "src/pkg/four.py"), "NO PAGE", "no page: state")
    rc, rows = check("src/pkg/later.py")
    eq(state(rows, "src/pkg/later.py"), "NO PAGE", "a file named after the Code sentence is not named")


def t_could_not_look_is_its_own_answer():
    r = root("unreg", {"design/specs/p/boundary.md": None})
    rc, rows = check("src/pkg/one.py")
    eq((rc, state(rows, "src/pkg/one.py")), (3, "UNREADABLE"), "an unregistered page that names the file")
    root("notests", {"design/specs/p/boundary.md": "tests/t_p.py"})
    os.remove(os.path.join(CRS.ROOT, "tests/t_p.py"))
    rc, rows = check("src/pkg/one.py")
    eq((rc, state(rows, "src/pkg/one.py")), (3, "UNREADABLE"), "a registered tests file that is gone")
    r = root("nocode", {"design/specs/p/boundary.md": "tests/t_p.py"})
    write(r, "design/specs/q/boundary.md", "# BOUNDARY\n\n## PROMISES\n\n- **x.** y.\n")
    CRS.PAGES["design/specs/q/boundary.md"] = "tests/t_p.py"
    rc, rows = check("src/pkg/four.py")
    eq((rc, state(rows, "src/pkg/four.py")), (3, "UNREADABLE"), "a page with no Code line: naming is unknown")
    r = root("slow", {"design/specs/p/boundary.md": "tests/t_p.py"})
    write(r, "tests/t_p.py", TESTS_OK.replace("    return %d", "    import time; time.sleep(5)\n    return 0"))
    old, CRS.TESTS_TIMEOUT_S = CRS.TESTS_TIMEOUT_S, 1
    try:
        rc, rows = check("src/pkg/one.py")
    finally:
        CRS.TESTS_TIMEOUT_S = old
    eq((rc, state(rows, "src/pkg/one.py")), (3, "UNREADABLE"), "a tests file past TESTS_TIMEOUT_S")


def t_a_review_record_cleans_nothing():
    r = root("record", {})
    subprocess.run(["git", "init", "-q"], cwd=r, capture_output=True)
    rel = "src/pkg/four.py"
    CRS.append_records([CRS._record(rel, {"hash": CRS.file_hash(rel), "sha": "abc", "date": "2026-11-19",
                                          "cleanCount": 1}, "SELFTEST", CRS._ts())])
    eq(CRS.clean_state(rel, CRS.load().get(rel))[0], "CLEAN", "setup: the review record itself reads clean")
    rc, rows = check(rel)
    eq((rc, state(rows, rel)), (4, "NO PAGE"), "a matching review record without a page")


def t_the_worst_answer_sets_the_exit():
    root("worst", {"design/specs/p/boundary.md": "tests/t_p.py"})
    eq(check("src/pkg/one.py", "src/pkg/four.py")[0], 4, "CLEAN + NO PAGE")
    eq(check("src/pkg/one.py", "src/pkg/four.py", "no/such/file.py")[0], 3, "+ UNREVIEWABLE")
    root("worst2", {"design/specs/p/boundary.md": "tests/t_p.py"}, tests_rc=1)
    eq(check("src/pkg/one.py", "src/pkg/four.py", "no/such/file.py")[0], 1, "+ DIRTY")


def t_each_tests_file_runs_once():
    r = root("once", {"design/specs/p/boundary.md": "tests/t_p.py"})
    check("src/pkg/one.py", "src/pkg/two.py", "src/pkg/three.py")
    try:
        with open(os.path.join(r, "tests", "runs.log")) as f:
            runs = f.read().count("run")
    except OSError:
        runs = 0
    eq(runs, 1, "tests file starts for three named paths")


def t_record_mode_keeps_the_review_record():
    r = root("recmode", {"design/specs/p/boundary.md": "tests/t_p.py"})
    rel = "src/pkg/four.py"
    CRS.append_records([CRS._record(rel, {"hash": CRS.file_hash(rel), "sha": "abc", "date": "2026-11-19",
                                          "cleanCount": 1}, "SELFTEST", CRS._ts())])
    rc, rows = check(rel, record=True)
    eq((rc, state(rows, rel)), (0, "CLEAN"), "record mode, matching hash")
    write(r, rel, "x = 2\n")
    rc, rows = check(rel, record=True)
    eq((rc, state(rows, rel)), (1, "DIRTY"), "record mode, bytes changed")


def run(*argv):
    """-> (exit code, stdout, stderr) of `code_review_status.py <argv>` run as main() runs it."""
    old, sys.argv = sys.argv, ["code_review_status.py"] + list(argv)
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                CRS.main()
                rc = 0
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else (0 if e.code is None else "exit %r" % (e.code,))
    except Exception as e:  # a crash is a failed promise, not a crashed selftest
        rc = "crash %s: %s" % (type(e).__name__, e)
    finally:
        sys.argv = old
    return rc, out.getvalue(), err.getvalue()


def flag_shards(r):
    d = os.path.join(r, "infrastructure", "state", "code_review", "flags")
    return sorted(os.listdir(d)) if os.path.isdir(d) else []


def flagged_rows(stdout):
    return [ln for ln in stdout.splitlines() if ln.startswith("FLAGGED  ")]


def t_flag_records_why_and_sticks():
    r = root("flag", {})
    rel = "src/pkg/four.py"
    rc, _, _ = run("flag", rel, "--why", "the blind reread found and fixed a second significant finding")
    eq(rc, 0, "flag: exit")
    eq(len(flag_shards(r)), 1, "flag: one shard under code_review/flags/")
    write(r, rel, "x = 2\n")
    rc, out, _ = run("list", "--flagged")
    rows = flagged_rows(out)
    eq(len(rows) == 1 and rel in rows[0] and "second significant finding" in rows[0], True,
       "flag: still FLAGGED with its why after the bytes change")
    r = root("flag_refused", {})
    rc, _, _ = run("flag", "src/pkg/four.py")
    eq(rc, 2, "flag with no --why: refused")
    rc, _, _ = run("flag", "src/pkg/nosuch.py", "--why", "x")
    eq(rc, 2, "flag of a path that is not a file: refused")
    eq(flag_shards(r), [], "a refused flag writes nothing")


def t_list_flagged_names_each_flag():
    r = root("listflag", {})
    rc, out, _ = run("list", "--flagged")
    eq((rc, flagged_rows(out), "no file is flagged" in out), (0, [], True), "no flag: exit 0, says none")
    run("flag", "src/pkg/one.py", "--why", "why one")
    run("flag", "src/pkg/two.py", "--why", "why two")
    rc, out, _ = run("list", "--flagged")
    rows = flagged_rows(out)
    eq(rc, 0, "two flags: exit")
    eq([("src/pkg/one.py" in x and "why one" in x, "src/pkg/two.py" in x and "why two" in x) for x in rows],
       [(True, False), (False, True)], "two flags: one line each, path and why")
    d = os.path.join(r, "infrastructure", "state", "code_review", "flags")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "BAD.jsonl"), "w") as f:
        f.write("{not json\n")
    rc, out, err = run("list", "--flagged")
    eq((rc, flagged_rows(out)), (3, []), "an unreadable flag shard: exit 3 and no FLAGGED line")
    eq("UNREADABLE" in out + err, True, "an unreadable flag shard is named UNREADABLE")


def t_a_flagged_file_is_not_picked_for_review():
    r = root("notpicked", {})
    subprocess.run(["git", "init", "-q"], cwd=r, capture_output=True)
    subprocess.run(["git", "add", "src"], cwd=r, capture_output=True)
    rel, never = "src/pkg/one.py", "src/pkg/two.py"
    CRS.append_records([CRS._record(rel, {"hash": "0" * 64, "sha": "abc", "date": "2026-11-19", "cleanCount": 1},
                                    "SELFTEST", CRS._ts())])
    old_dir = CRS.UNTRACKED_SCAN_DIR
    CRS.UNTRACKED_SCAN_DIR = "src"
    try:
        rc, out, _ = run("list", "--show-untracked")
        eq("DIRTY" in out and rel in out and never in out, True, "setup: the file reads DIRTY, the other NEVER ENTERED")
        run("flag", rel, "--why", "x")
        run("flag", never, "--why", "y")
        rc, out, _ = run("list", "--show-untracked")
    finally:
        CRS.UNTRACKED_SCAN_DIR = old_dir
    lines = out.splitlines()
    eq([ln for ln in lines if rel in ln and ln.startswith("DIRTY")], [], "list: a flagged file is not DIRTY")
    eq([ln for ln in lines if ln.strip() == never], [], "list: a flagged file is not NEVER ENTERED")
    eq(any(ln.startswith("FLAGGED") and rel in ln for ln in lines), True, "list: the file reads FLAGGED")
    tally = [ln for ln in lines if ln.startswith("TALLY")]
    eq(bool(tally) and "DIRTY 0" in tally[0] and "FLAGGED 2" in tally[0], True, "list: tally %r" % tally)
    before = len(CRS.read_records())
    rc, _, err = run("mark-clean", rel)
    eq(rc, 2, "mark-clean of a flagged file: refused")
    eq("unflag" in err, True, "the refusal names unflag")
    eq(len(CRS.read_records()), before, "a refused mark-clean writes no record")


def t_unflag_ends_the_flag():
    root("unflag", {})
    rel = "src/pkg/four.py"
    run("flag", rel, "--why", "x")
    rc, _, _ = run("unflag", rel, "--why", "weekly examination: the definition of significant was too wide")
    eq(rc, 0, "unflag: exit")
    rc, out, _ = run("list", "--flagged")
    eq(flagged_rows(out), [], "unflag: no longer FLAGGED")
    rc, _, _ = run("unflag", rel, "--why", "again")
    eq(rc, 2, "unflag of a file that is not flagged: refused")
    run("flag", rel, "--why", "x")
    rc, _, _ = run("unflag", rel)
    eq(rc, 2, "unflag with no --why: refused")


def t_a_flag_changes_no_page_state():
    root("flagpage", {"design/specs/p/boundary.md": "tests/t_p.py"})
    run("flag", "src/pkg/one.py", "--why", "x")
    rc, rows = check("src/pkg/one.py", "src/pkg/four.py")
    eq((rc, state(rows, "src/pkg/one.py"), state(rows, "src/pkg/four.py")), (4, "CLEAN", "NO PAGE"),
       "check on a flagged file: the page states and exit are unchanged")
    rc, rows = check("src/pkg/one.py", record=True)
    eq((rc, state(rows, "src/pkg/one.py")), (1, "DIRTY"), "check --record on a flagged file with no record")


def main():
    t_clean_needs_a_page_and_passing_tests()
    t_a_promise_without_a_test_is_dirty()
    t_a_red_tests_file_is_dirty()
    t_no_page_is_its_own_answer()
    t_could_not_look_is_its_own_answer()
    t_a_review_record_cleans_nothing()
    t_the_worst_answer_sets_the_exit()
    t_each_tests_file_runs_once()
    t_record_mode_keeps_the_review_record()
    t_flag_records_why_and_sticks()
    t_list_flagged_names_each_flag()
    t_a_flagged_file_is_not_picked_for_review()
    t_unflag_ends_the_flag()
    t_a_flag_changes_no_page_state()
    os.chdir(HERE)
    shutil.rmtree(TMP, ignore_errors=True)
    for f in FAILS:
        print("FAIL " + f)
    print("selftest_code_review_page_state: %d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
