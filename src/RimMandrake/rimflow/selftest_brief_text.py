#!/usr/bin/env python3
"""selftest_brief_text.py - the promises of design/specs/2026-11-24-brief-text-hash/boundary.md: a docstring or a comment
is not brief text, so its edit does not reset a judge's calibration; a prompt or code edit does. No model, no network."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402

FAILS = []
SRC = '''#!/usr/bin/env python3
"""module doc: one"""
import argparse

# a comment
RULE = "hash # mark is prompt text"   # a trailing comment
PROMPT = """judge the bar

and say why"""


def ask(n):
    """function doc: one"""
    return f"""look {n}

and {n!r} # not a comment"""


class Judge:
    """class doc: one"""
    LIMIT = 3


def main():
    print(__doc__)
    argparse.ArgumentParser(description=__doc__.split("\\n")[0])
'''


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def h(text, name="b.py"):
    with tempfile.TemporaryDirectory() as root:
        with open(os.path.join(root, name), "w", encoding="utf-8") as f:
            f.write(text)
        return RC.brief_hash([name], root)


def sub(src, *pairs):
    for a, b in pairs:
        assert a in src, a
        src = src.replace(a, b, 1)
    return src


def same(name, src, *edits):
    moved = [e for e in edits if h(sub(src, e)) != h(src)]
    check(name, not moved, moved)


def moves(name, src, *edits):
    kept = [e for e in edits if h(sub(src, e)) == h(src)]
    check(name, not kept, kept)


def t_a_docstring_edit_keeps_the_hash():
    same("a-docstring-edit-keeps-the-hash", SRC, ("module doc: one", "module doc: two\n\nmore lines # and a hash"),
         ("function doc: one", "two"), ("class doc: one", "two"), ('    """class doc: one"""\n', ""),
         ("def main():\n", 'def main():\n    """a new doc\n\n    of lines"""\n'))


def t_a_comment_or_blank_line_edit_keeps_the_hash():
    same("a-comment-or-blank-line-edit-keeps-the-hash", SRC, ("# a comment", "# another"), ("# a comment\n", ""),
         ("# a trailing comment", "# é, changed"), ("   # a trailing comment", ""), ("import argparse\n", "import argparse\n\n\n"))


def t_a_prompt_string_edit_moves_the_hash():
    moves("a-prompt-string-edit-moves-the-hash", SRC, ("# mark is", "# sign is"), ("judge the bar\n\n", "judge the bar\n"),
          ("judge the bar", "judge each bar"), ("look {n}\n\n", "look {n}\n"), ("# not a comment", "# a comment"),
          ("look {n}\n", "look {n}\n# a planted line\n"))


def t_a_code_edit_moves_the_hash():
    moves("a-code-edit-moves-the-hash", SRC, ("LIMIT = 3", "LIMIT = 4"), ("def ask(n)", "def ask(n, m=1)"),
          ("    LIMIT = 3\n", ""))


def t_a_docstring_the_program_reads_counts():
    for reads in ("PROMPT2 = __doc__", "PROMPT2 = ask.__doc__", "import inspect; PROMPT2 = inspect.getdoc(ask)",
                  "import inspect; PROMPT2 = inspect.getsource(ask)", "PROMPT2 = globals()['__doc__']"):
        moves("a-docstring-the-program-reads-counts: %s" % reads, SRC + reads + "\n", ("module doc: one", "two"))


def t_a_file_that_does_not_parse_counts_whole():
    moves("a-file-that-does-not-parse-counts-whole", SRC + "def (:\n", ("module doc: one", "two"), ("# a comment", "# b"))


def t_a_non_python_brief_counts_whole():
    for name in ("b.md", "b.json"):
        check("a-non-python-brief-counts-whole: %s" % name, h(SRC, name) != h(sub(SRC, ("# a comment", "# b")), name)
              and h(SRC, name) != h(sub(SRC, ("module doc: one", "two")), name))


def t_the_docstring_commit_of_2026_11_24_keeps_the_hash():
    # the real edit of 6cfd21b97c, on today's file
    with open(os.path.join(HERE, "coverage_judge.py"), encoding="utf-8") as f:
        cj = f.read()
    new, old = "and only his\nword or the Conductor's act on the item lifts it.", "and only his own\nword on the item lifts it."
    flips = cj.replace(new, old, 1) if new in cj else cj.replace('"""', '"""planted words ', 1)
    check("the-docstring-commit-of-2026-11-24-keeps-the-hash", flips != cj and h(flips) == h(cj))
    check("the-docstring-commit-of-2026-11-24-keeps-the-hash: a prompt edit moves it",
          h(sub(cj, ("You are the coverage judge", "You are a coverage judge"))) != h(cj))


def t_an_edited_docstring_leaves_the_row_calibrated():
    with tempfile.TemporaryDirectory() as root:
        path, reg = os.path.join(root, "b.py"), os.path.join(root, "cal.json")

        def put(text):
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return RC.status("fam")
        put(SRC)
        with open(reg, "w", encoding="utf-8") as f:
            json.dump({"families": {"fam": {"brief": ["b.py"], "hash": RC.brief_hash(["b.py"], root),
                                            "status": "CALIBRATED", "cases": {}}}}, f)
        keep = {k: os.environ.get(k) for k in ("RM_JUDGE_CALIBRATION", "RM_CALIBRATION_ROOT")}
        os.environ.update(RM_JUDGE_CALIBRATION=reg, RM_CALIBRATION_ROOT=root)
        try:
            got = (put(SRC), put(sub(SRC, ("module doc: one", "two"))), put(sub(SRC, ("judge the bar", "judge no bar"))))
        finally:
            for k, v in keep.items():
                os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        check("an-edited-docstring-leaves-the-row-calibrated", got == ("CALIBRATED", "CALIBRATED", "UNTESTED"), got)


def main():
    t_a_docstring_edit_keeps_the_hash()
    t_a_comment_or_blank_line_edit_keeps_the_hash()
    t_a_prompt_string_edit_moves_the_hash()
    t_a_code_edit_moves_the_hash()
    t_a_docstring_the_program_reads_counts()
    t_a_file_that_does_not_parse_counts_whole()
    t_a_non_python_brief_counts_whole()
    t_the_docstring_commit_of_2026_11_24_keeps_the_hash()
    t_an_edited_docstring_leaves_the_row_calibrated()
    print("ALL PASS" if not FAILS else "%d FAILED: %s" % (len(FAILS), ", ".join(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
