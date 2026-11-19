#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_REFUSE_STAGE_THREE_BAR_READS_NO_BUILT_FILE (DESIGN DECISION 2026-11-18 on
RIMMANDRAKE_GATE_STAGE_THREE_ON_UNBUILT_BEHAVIOUR_FROZEN_RECORD). The live signal for "this bar's behaviour is built" is
the test table the Stage 3 exit already reads: a bar is built only when at least one of its DECIDING tests `reads` a
built file, read from disk when the gate runs. A built file: exists under <root>/src/RimMandrake/, is a regular file,
is not a .py, and is not the test's own `file` (a `path:line` suffix is ignored). record.json is not read.
  maturation.bars_reading_no_built_file(root, tt) -> sorted bar ids that read none; None when the table cannot be read
  (not a dict, or no `bars` list): "could not look" is not "every bar is built".
  The Stage 3 exit carries it as clause `every_bar_reads_built_code`, listed in maturation.BUILD_CLAUSES.
Red on 69a05807c1 (watched)."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


def ask(root, tt):
    fn = getattr(M, "bars_reading_no_built_file", None)
    if not callable(fn):
        return "no bars_reading_no_built_file"
    try:
        return fn(root, tt)
    except Exception as e:
        return "CRASH %s: %s" % (type(e).__name__, e)


def main():
    tmp = tempfile.mkdtemp(prefix="stage3_built_")
    try:
        src = os.path.join(tmp, "src", "RimMandrake", "Foo")
        os.makedirs(os.path.join(src, "Source", "ADir"))
        os.makedirs(os.path.join(tmp, "design"))
        for rel in ("Source/Climb.cs", "validation.py"):
            with open(os.path.join(src, rel), "w") as f:
                f.write("x\n")
        with open(os.path.join(tmp, "design", "notes.md"), "w") as f:
            f.write("x\n")
        cs, py = "src/RimMandrake/Foo/Source/Climb.cs", "src/RimMandrake/Foo/validation.py"

        def table(reads, decides=("t1",), file=py):
            return {"tests": {"t1": {"id": "t1", "file": file, "reads": reads}},
                    "bars": [{"id": "b1", "decides": list(decides)}]}
        two = {"t1": {"id": "t1", "file": py, "reads": [py]}, "t2": {"id": "t2", "file": py, "reads": [cs]}}
        cases = [
            ("a decider reading a shipped source file is built", table([py, cs]), []),
            ("a path with a :line suffix counts", table([cs + ":42"]), []),
            ("a decider reading only its own test file is not built", table([py]), ["b1"]),
            ("a decider reading only a .py is not built", table(["src/RimMandrake/Foo/other.py", py]), ["b1"]),
            ("a file that does not exist is not built", table(["src/RimMandrake/Foo/Source/Gone.cs"]), ["b1"]),
            ("a directory is not a built file", table(["src/RimMandrake/Foo/Source/ADir"]), ["b1"]),
            ("a file outside src/RimMandrake is not built", table(["design/notes.md"]), ["b1"]),
            ("a path that climbs out of src/RimMandrake is not built",
             table(["src/RimMandrake/../../design/notes.md"]), ["b1"]),
            ("the test's own file is not built even when it is not a .py", table([cs], file=cs), ["b1"]),
            ("no reads is not built", table([]), ["b1"]),
            ("reads that is not a list is not built", table(cs), ["b1"]),
            ("a reads entry that is not text is skipped", table([7, None, cs]), []),
            ("a bar with no deciders is not built", table([cs], decides=()), ["b1"]),
            ("a decider the table does not hold is not built", table([cs], decides=("t9",)), ["b1"]),
            ("a supporting test's reads do not count",
             {"tests": two, "bars": [{"id": "b1", "decides": ["t1"], "supports": ["t2"]}]}, ["b1"]),
            ("one built decider among several is enough",
             {"tests": two, "bars": [{"id": "b1", "decides": ["t1", "t2"]}]}, []),
            ("no bars at all is an empty answer, not an unread one", {"tests": {}, "bars": []}, []),
            ("several bars come back sorted",
             {"tests": two, "bars": [{"id": "zz", "decides": ["t1"]}, {"id": "aa", "decides": ["t1"]}]}, ["aa", "zz"]),
        ]
        for name, tt, want in cases:
            got = ask(tmp, tt)
            check(name, got == want, got)
        for name, tt in (("a table that is None", None), ("a table that is a list", []),
                         ("a table with no bars list", {"tests": {}}), ("a table whose bars is not a list", {"bars": {}})):
            got = ask(tmp, tt)
            check("%s is None (could not look), never []" % name, got is None, got)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # the real tables: four mods whose bars all read built code stay clean; Graffiti's unbuilt bar is named
    for mod, want_clean in (("ExplosiveKnockback", True), ("FlowWorks", True), ("GimmeSomeSlack", True),
                            ("Pyrelands", True), ("Graffiti", False)):
        p = os.path.join(ROOT, "design", "concepts", mod, "version", "test_table.json")
        try:
            with open(p) as f:
                tt = json.load(f)
        except (OSError, ValueError) as e:
            print("UNMEASURED %s: %s" % (mod, e))
            FAILS.append("%s table unread" % mod)
            continue
        got = ask(ROOT, tt)
        if want_clean:
            check("%s: every bar reads built code today" % mod, got == [], str(got)[:200])
        else:
            check("Graffiti: the unbuilt bar inv_raider_future_marks is named",
                  isinstance(got, list) and "inv_raider_future_marks" in got, str(got)[:200])
    check("every_bar_reads_built_code is a clause a builder can work off (BUILD_CLAUSES)",
          "every_bar_reads_built_code" in getattr(M, "BUILD_CLAUSES", ()), getattr(M, "BUILD_CLAUSES", None))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
