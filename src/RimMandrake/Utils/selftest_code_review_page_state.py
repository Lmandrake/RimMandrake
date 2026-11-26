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


# ---- a mod's locked bars are its page (version 0.3.0) ----

sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rimflow"))
import judge_certificate as JC  # noqa: E402  the build identity a mod test's recorded run is bound to

MOD_SRC = "src/RimMandrake/Mod"
MOD_FILES = ("%s/Source/a.cs" % MOD_SRC, "%s/Source/b.cs" % MOD_SRC, "%s/validation.py" % MOD_SRC)
MOD_A = MOD_FILES[0]
VDIR = "design/concepts/Mod/version"


def offline(tid, reads="a"):
    return {"id": tid, "kind": "offline", "file": "%s/selftest_%s.py" % (MOD_SRC, tid.lower()),
            "reads": ["%s/Source/%s.cs" % (MOD_SRC, reads)], "command": "python3 %s/selftest_%s.py" % (MOD_SRC, tid.lower())}


def stamp(r, t, rc=0, result=None, build=None, command=None):
    t["runs_today"] = {"ran": True, "rc": rc, "result": result or ("PASS" if rc == 0 else "FAIL"),
                       "build": build or JC.test_build(r, t), "command": command or t["command"], "last": "x"}
    return t


def mod_root(name, edit=None, version=None, locked=None, table=True):
    """A repo root with one locked mod, `Mod`, of two bars, each decided by one offline test that ran green on this
    build. `edit(r, tt)` changes the table before it is written; version/locked override VERSION.json/locked_bars.json
    (a string is written as the file's raw text; None as the default; False leaves the file out)."""
    r = root(name, {})
    for f in MOD_FILES:
        write(r, f, "// %s\n" % f)
    tt = {"mod": "Mod", "version": "0.1.0", "bars": [{"id": "bar_one", "decides": ["T_ONE"]},
                                                    {"id": "bar_two", "decides": ["T_TWO"]}],
          "tests": {"T_ONE": offline("T_ONE", "a"), "T_TWO": offline("T_TWO", "b")}}
    for t in tt["tests"].values():
        write(r, t["file"], "pass\n")
        stamp(r, t)
    if edit:
        edit(r, tt)
    import json
    for rel, default, given in (("VERSION.json", {"mod": "Mod", "version": "0.1.0", "state": "locked"}, version),
                                ("locked_bars.json", {"mod": "Mod", "version": "0.1.0", "ids": ["bar_one", "bar_two"]},
                                 locked),
                                ("test_table.json", tt, None if table is True else table)):
        if given is False:
            continue
        write(r, "%s/%s" % (VDIR, rel), given if isinstance(given, str) else json.dumps(given if given else default))
    return r


def line(rows, rel):
    return rows.get(rel, ("", ""))[1]


def t_a_mod_file_reads_its_locked_bars():
    mod_root("modclean")
    rc, rows = check(*MOD_FILES)
    eq(rc, 0, "mod clean: exit")
    for rel in MOD_FILES:
        eq(state(rows, rel), "CLEAN", "mod clean: %s (a file no bar touches reads by its mod's bars)" % rel)
    eq("bars green 2 of 2" in line(rows, MOD_A), True, "mod clean: detail counts the bars (%s)" % line(rows, MOD_A))
    eq("Mod 0.1.0" in line(rows, MOD_A), True, "mod clean: detail names the mod and its version")

    def extra(r, tt):   # a table bar that is not locked is no promise
        tt["bars"].append({"id": "bar_not_locked", "decides": ["T_GONE"]})
    mod_root("modextra", extra)
    eq(check(MOD_A)[0], 0, "a table bar that is not locked changes nothing")
    mod_root("modpassed", version={"mod": "Mod", "version": "0.1.0", "state": "passed 2026-11-19"})
    eq(check(MOD_A)[0], 0, "a passed version's locked bars stay the page")
    mod_root("modrecord", lambda r, tt: tt["tests"]["T_ONE"].update(kind="record"))
    eq(check(MOD_A)[0], 0, "a record test with a green run on this build is green")


def t_a_mod_without_locked_bars_has_no_page():
    for name, kw in (("nover", {"version": False}), ("drafting", {"version": {"mod": "Mod", "version": "0.2.0",
                                                                             "state": "drafting"}}),
                     ("nolocked", {"locked": False})):
        mod_root("mod" + name, **kw)
        rc, rows = check(MOD_A)
        eq((rc, state(rows, MOD_A)), (4, "NO PAGE"), "mod no page: %s" % name)
        eq("Mod" in line(rows, MOD_A) and "locked" in line(rows, MOD_A), True,
           "mod no page: %s: the detail says why (%s)" % (name, line(rows, MOD_A)))
    r = mod_root("modnoconcept")
    write(r, "src/RimMandrake/Other/x.cs", "//\n")
    rc, rows = check("src/RimMandrake/Other/x.cs")
    eq((rc, state(rows, "src/RimMandrake/Other/x.cs")), (4, "NO PAGE"), "a folder with no concept reads as before")
    eq("boundary.md" in line(rows, "src/RimMandrake/Other/x.cs"), True, "no concept: the old detail")


def t_a_bar_without_a_green_test_is_dirty():
    cases = (
        ("notinta", lambda r, tt: tt["bars"].pop(1), "bar_two"),
        ("nodecider", lambda r, tt: tt["bars"][1].update(decides=[]), "bar_two"),
        ("noentry", lambda r, tt: tt["tests"].pop("T_TWO"), "T_TWO"),
        ("nocommand", lambda r, tt: tt["tests"]["T_TWO"].update(command=""), "T_TWO"),
        ("red", lambda r, tt: stamp(r, tt["tests"]["T_TWO"], rc=1), "T_TWO"),
        ("redresult", lambda r, tt: stamp(r, tt["tests"]["T_TWO"], rc=0, result="FAIL"), "T_TWO"),
        ("knownred", lambda r, tt: tt["tests"]["T_TWO"].update(known_red="SOME_ITEM"), "T_TWO"),
        ("redandunrun", lambda r, tt: (stamp(r, tt["tests"]["T_TWO"], rc=1),
                                       tt["tests"]["T_ONE"].pop("runs_today")), "T_TWO"),
    )
    for name, edit, names in cases:
        mod_root("moddirty" + name, edit)
        rc, rows = check(MOD_A)
        eq((rc, state(rows, MOD_A)), (1, "DIRTY"), "mod dirty: %s" % name)
        eq(names in line(rows, MOD_A), True, "mod dirty: %s: the detail names %s (%s)" % (name, names, line(rows, MOD_A)))
    mod_root("moddirtynotable", table=False)
    rc, rows = check(MOD_A)
    eq((rc, state(rows, MOD_A)), (1, "DIRTY"), "mod dirty: no test table, so no bar has a test")


def t_an_unrun_or_stale_mod_test_is_unreadable():
    def edited_after(r, tt):
        write(r, "%s/Source/b.cs" % MOD_SRC, "// changed after the run\n")
    cases = (
        ("norun", lambda r, tt: tt["tests"]["T_TWO"].pop("runs_today"), "UNRUN"),
        ("notran", lambda r, tt: tt["tests"]["T_TWO"]["runs_today"].update(ran=False), "UNRUN"),
        ("nobuild", lambda r, tt: tt["tests"]["T_TWO"]["runs_today"].pop("build"), "STALE"),
        ("stale", edited_after, "STALE"),
        ("command", lambda r, tt: tt["tests"]["T_TWO"].update(command="python3 other.py"), "STALE"),
        ("ingame", lambda r, tt: tt["tests"]["T_TWO"].update(kind="live_minimal"), "UNRUN"),
        ("look", lambda r, tt: tt["tests"]["T_TWO"].update(kind="look"), "UNRUN"),
        ("lookcommandless", lambda r, tt: tt["tests"]["T_TWO"].update(kind="look", command=None), "UNRUN"),
    )
    for name, edit, word in cases:
        mod_root("modunrun" + name, edit)
        rc, rows = check(MOD_A)
        eq((rc, state(rows, MOD_A)), (3, "UNREADABLE"), "mod unrun: %s" % name)
        eq(word in line(rows, MOD_A) and "bar_two" in line(rows, MOD_A), True,
           "mod unrun: %s: the detail says %s and names the bar (%s)" % (name, word, line(rows, MOD_A)))


def t_an_unreadable_mod_store_is_unreadable():
    cases = (
        ("version", {"version": "{not json"}),
        ("locked", {"locked": "{not json"}),
        ("lockedother", {"locked": {"version": "0.0.9", "ids": ["bar_one", "bar_two"]}}),
        ("lockednoids", {"locked": {"version": "0.1.0", "ids": "bar_one"}}),
        ("lockeddup", {"locked": {"version": "0.1.0", "ids": ["bar_one", "bar_one"]}}),
        ("table", {"table": "{not json"}),
        ("tableother", {"table": {"version": "0.0.9", "bars": [], "tests": {}}}),
        ("tablebars", {"table": {"version": "0.1.0", "bars": "x", "tests": {}}}),
    )
    for name, kw in cases:
        mod_root("modunread" + name, **kw)
        rc, rows = check(MOD_A)
        eq((rc, state(rows, MOD_A)), (3, "UNREADABLE"), "mod store unreadable: %s (%s)" % (name, line(rows, MOD_A)))


def t_a_mod_file_on_a_page_takes_the_worse():
    page = PAGE.replace("`src/pkg/one.py` (`f`)", "`%s`, `src/pkg/one.py` (`f`)" % MOD_A)
    r = mod_root("modpage", lambda r, tt: stamp(r, tt["tests"]["T_TWO"], rc=1))
    write(r, "design/specs/p/boundary.md", page)
    write(r, "tests/t_p.py", TESTS_OK % 0)
    CRS.PAGES = {"design/specs/p/boundary.md": "tests/t_p.py"}
    rc, rows = check(MOD_A)
    eq((rc, state(rows, MOD_A)), (1, "DIRTY"), "clean page + red mod bar")
    eq("design/specs/p/boundary.md" in line(rows, MOD_A) and "T_TWO" in line(rows, MOD_A), True,
       "the detail names both (%s)" % line(rows, MOD_A))
    r = mod_root("modpage2")
    write(r, "design/specs/p/boundary.md", page)
    write(r, "tests/t_p.py", TESTS_OK % 1)
    CRS.PAGES = {"design/specs/p/boundary.md": "tests/t_p.py"}
    rc, rows = check(MOD_A)
    eq((rc, state(rows, MOD_A)), (1, "DIRTY"), "red page + clean mod")
    write(r, "tests/t_p.py", TESTS_OK % 0)
    eq(check(MOD_A)[0], 0, "clean page + clean mod")


def t_each_mod_store_is_read_once():
    mod_root("modonce")
    calls = {"build": 0}
    real = JC.test_build

    def counting(root_, t):
        calls["build"] += 1
        return real(root_, t)
    JC.test_build = counting
    try:
        reads = []
        real_open = open
        import builtins

        def spy(f, *a, **k):
            if str(f).endswith("test_table.json"):
                reads.append(f)
            return real_open(f, *a, **k)
        builtins.open = spy
        try:
            rc, _rows = check(*MOD_FILES)
        finally:
            builtins.open = real_open
    finally:
        JC.test_build = real
    eq(rc, 0, "read once: exit")
    eq(calls["build"], 2, "test builds computed for three files of a mod with two tests")
    eq(len(reads), 1, "test table opened for three files of one mod")


def t_an_ingame_pass_that_stands_counts_green():
    """The reader is planted (CRS.ingame_standing): a fixture root has no visit rows and no git history. The real reader,
    maturation.ingame_to_run, is the Stage 6 reader and has its own tests."""
    def live(r, tt):
        tt["tests"]["T_TWO"].update(kind="live_minimal", stage=6)
        tt["tests"]["T_TWO"].pop("runs_today")
    real = CRS.ingame_standing
    calls = []
    try:
        CRS.ingame_standing = lambda mod, tt: (calls.append(mod), {"T_TWO"})[1]
        mod_root("modingamepass", live)
        rc, rows = check(*MOD_FILES)
        eq((rc, state(rows, MOD_A)), (0, "CLEAN"), "an in-game PASS that stands: the bar is green")
        eq("bars green 2 of 2" in line(rows, MOD_A), True, "in-game PASS: the detail counts it (%s)" % line(rows, MOD_A))
        eq(calls, ["Mod"], "the in-game runs are read once for three files of one mod")
        CRS.ingame_standing = lambda mod, tt: set()
        mod_root("modingamenone", live)
        rc, rows = check(MOD_A)
        eq((rc, state(rows, MOD_A)), (3, "UNREADABLE"), "no in-game PASS stands: the bar is not green")
        eq("UNRUN" in line(rows, MOD_A) and "bar_two" in line(rows, MOD_A), True,
           "no in-game PASS: the detail says UNRUN and names the bar (%s)" % line(rows, MOD_A))

        def blind(mod, tt):
            raise ValueError("visit_2/rows.jsonl line 3 is not JSON")
        CRS.ingame_standing = blind
        mod_root("modingameblind", live)
        rc, rows = check(MOD_A)
        eq((rc, state(rows, MOD_A)), (3, "UNREADABLE"), "in-game runs that cannot be read: never green")
        eq("rows.jsonl line 3" in line(rows, MOD_A), True, "unreadable in-game runs: the cause (%s)" % line(rows, MOD_A))
        CRS.ingame_standing = lambda mod, tt: (calls.append(mod), {"T_TWO"})[1]
        del calls[:]
        mod_root("modingamelook", lambda r, tt: (tt["tests"]["T_TWO"].update(kind="look"),
                                                  tt["tests"]["T_TWO"].pop("runs_today")))
        rc, rows = check(MOD_A)
        eq((rc, state(rows, MOD_A)), (3, "UNREADABLE"), "his walk (kind look) is no in-game visit: it stays UNRUN")
        mod_root("modingameabsent")
        check(MOD_A)
        eq(calls, [], "a mod with no in-game decider reads no in-game run")
    finally:
        CRS.ingame_standing = real
    import maturation as M
    seen = {}
    old = M.visit_numbers, M.ingame_to_run
    try:
        M.visit_numbers = lambda root_, mod: [1, 2]
        M.ingame_to_run = lambda root_, mod, n, tt: (seen.update(root=root_, mod=mod, n=n), (["T_ONE"], ["T_TWO"]))[1]
        got = CRS.ingame_standing("Mod", {"tests": {}})
    finally:
        M.visit_numbers, M.ingame_to_run = old
    eq(got, {"T_TWO"}, "the real reader returns the checks the Stage 6 reader counts")
    eq(seen, {"root": CRS.ROOT, "mod": "Mod", "n": 3}, "the real reader asks the Stage 6 reader as visit 3 would")


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
    t_a_mod_file_reads_its_locked_bars()
    t_a_mod_without_locked_bars_has_no_page()
    t_a_bar_without_a_green_test_is_dirty()
    t_an_unrun_or_stale_mod_test_is_unreadable()
    t_an_unreadable_mod_store_is_unreadable()
    t_a_mod_file_on_a_page_takes_the_worse()
    t_each_mod_store_is_read_once()
    t_an_ingame_pass_that_stands_counts_green()
    os.chdir(HERE)
    shutil.rmtree(TMP, ignore_errors=True)
    for f in FAILS:
        print("FAIL " + f)
    print("selftest_code_review_page_state: %d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
