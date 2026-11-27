#!/usr/bin/env python3
"""selftest_brief_new.py: the promises of design/specs/2026-11-27-brief-new/boundary.md (each t_ function is one
promise, by name). Offline: the prose check runs its program half only (`guiding_prose.check_files` with no reader),
on every sentence of each skeleton. Written before brief_new.py; seen failing on the base (the module absent).

    python3 src/RimMandrake/rimflow/selftest_brief_new.py
"""
import ast
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
TOOL = os.path.join(HERE, "brief_new.py")
# hang guard on each run of the tool: one run takes about 0.1 s (measured 2026-11-27); 60 s is far above that
RUN_S = 60
ITEM = "RIMMANDRAKE_BUILD_BRIEF_NEW_ONE_IN_FOUR_LAUNCHES_RETURNED"   # a real ledger item: the check reads dead items
OWED_BLANKS = ("TITLE", "QUESTION", "FILES", "ENOUGH", "STOP")      # the ticket: the model writes these
NO_SPEND = re.compile(r"\b(?:spend|spent|cap|caps|budget|remainder|usd|dollars?|tokens?)\b|\$\d", re.I)  # CLAUDE.md §No limit


def B():
    import brief_new
    return brief_new


def GP():
    import guiding_prose
    return guiding_prose


def prose_faults(text):
    """-> (faults, sentences read): the program half of `guiding_prose.py brief` on every sentence of the text."""
    g = GP()
    sents = g.sentences(text)
    res = g.check_files(g.TOP, {g.BRIEF_PATH: text}, {}, "brief", reader=None, sents_by={g.BRIEF_PATH: sents})
    return res["faults"], len(sents)


def t_each_kind_skeleton_passes_the_prose_check():
    b = B()
    kinds = sorted(b.KINDS)
    assert len(kinds) >= 4, "kinds: %r" % kinds
    # the instrument can see: a planted fault in a skeleton is found (a pronoun and a `should`)
    planted, _ = prose_faults(b.skeleton(kinds[0], ITEM) + "\n\nIt should be done soon.\n")
    assert planted, "the check found nothing in a planted fault: it cannot see"
    worst, read = 0, 0
    for k in kinds:
        faults, n = prose_faults(b.skeleton(k, ITEM))
        read += n
        worst = max(worst, len(faults))
        assert n >= 15, "%s: only %d sentences read" % (k, n)
        assert not faults, "%s: %s" % (k, "; ".join("%s %r: %s" % (f["kind"], f["term"], f["sentence"][:80]) for f in faults))
    print("   prose check: worst %d faults in a kind, limit 0, %d kinds, %d sentences read" % (worst, len(kinds), read))


def t_the_question_and_the_stop_are_left_as_blanks():
    b = B()
    for k in sorted(b.KINDS):
        text = b.skeleton(k, ITEM)
        left = b.blanks(text)
        for name in OWED_BLANKS:
            assert left.count(name) == 1, "%s: blank %s appears %d times" % (k, name, left.count(name))
        assert ITEM in text.split("\n\n")[1], "%s: the header lacks the item" % k
        for key, line in b.LINES.items():
            assert "<<" not in line and ">>" not in line, "standing line %s holds a blank" % key
        # CLAUDE.md: a brief that reviews or judges states the level that is enough, when to stop, and the polish route
        assert b.LINES["polish"].split(".")[0] in text, "%s: no polish route" % k
        filled = text
        for name in set(left):
            filled = re.sub(r"<<%s:[^>]*>>" % name, "filled", filled)
        assert not b.blanks(filled), "%s: blanks() still finds %r after filling" % (k, b.blanks(filled))
    print("   blanks: %d kinds, each with %s once" % (len(b.KINDS), ", ".join(OWED_BLANKS)))


def t_an_unknown_kind_is_refused_by_name():
    b = B()
    d = tempfile.mkdtemp(prefix="briefnew_")
    out = os.path.join(d, "brief.md")
    r = subprocess.run([sys.executable, TOOL, "nosuchkind", ITEM, "--out", out], capture_output=True, text=True, timeout=RUN_S)
    assert r.returncode != 0, "rc %d" % r.returncode
    assert "nosuchkind" in r.stderr, r.stderr
    for k in b.KINDS:
        assert k in r.stderr, "the refusal does not name the kind %s: %s" % (k, r.stderr)
    assert not r.stdout.strip() and not os.path.exists(out), "a refused kind wrote something"
    # a known kind writes, and does not overwrite a brief that the model has filled
    r = subprocess.run([sys.executable, TOOL, sorted(b.KINDS)[0], ITEM, "--out", out], capture_output=True, text=True, timeout=RUN_S)
    assert r.returncode == 0 and os.path.isfile(out), (r.returncode, r.stderr)
    with open(out, "a", encoding="utf-8") as f:
        f.write("model text\n")
    r = subprocess.run([sys.executable, TOOL, sorted(b.KINDS)[0], ITEM, "--out", out], capture_output=True, text=True, timeout=RUN_S)
    with open(out, encoding="utf-8") as f:
        assert r.returncode != 0 and f.read().endswith("model text\n"), "an existing brief was overwritten"
    print("   refusal names all %d kinds; an existing --out is kept" % len(b.KINDS))


def t_standing_lines_come_from_one_source():
    b = B()
    import fixer_rule
    import spend_talk
    keys = [k for spec in b.KINDS.values() for _, refs in spec["sections"] for k in refs if not k.startswith("?")]
    missing = sorted(set(k for k in keys if k not in b.LINES))
    assert not missing, "kinds name lines that the source lacks: %r" % missing
    unused = sorted(set(b.LINES) - set(keys) - set(b.HEADER_KEYS))
    assert not unused, "lines that no kind uses: %r" % unused
    # no line restates another: no sentence of one standing line is in a second line
    seen = {}
    for key, line in b.LINES.items():
        for s in [x.strip() for x in re.split(r"(?<=[.!?])\s+", line) if len(x.strip()) >= 20]:
            assert s not in seen, "lines %s and %s both say: %s" % (seen[s], key, s)
            seen[s] = key
    # each kind names a line once
    for kind, spec in b.KINDS.items():
        refs = [k for _, r in spec["sections"] for k in r]
        assert len(refs) == len(set(refs)), "%s names a line twice" % kind
    # the fixer rule is fixer_rule's own text, and brief_new.py holds no copy of it
    assert b.LINES["test2"] + " " + b.LINES["evidence"] == fixer_rule.text(), "test 2 is not fixer_rule.text()"
    assert b.LINES["test2_judge"] + " " + b.LINES["evidence"] == fixer_rule.text(judge=True), "judge test 2 differs"
    with open(os.path.join(HERE, "brief_new.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    pieces = [fixer_rule.STATEMENT[:30], fixer_rule.JUDGE_STATEMENT[:30]] + [e[:30] for e in fixer_rule.EVIDENCE]
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            for p in pieces:
                assert p not in n.value, "brief_new.py restates the fixer rule: %r" % p
    # every skeleton is the source's lines, its blanks and headings: nothing else
    for kind in b.KINDS:
        rest = b.skeleton(kind, ITEM)
        for line in sorted(b.LINES.values(), key=len, reverse=True):
            rest = rest.replace(line.format(item=ITEM), "")
        rest = re.sub(r"<<[A-Z]+:[^>]*>>", "", rest)
        rest = [l for l in rest.split("\n") if l.strip() and not re.match(r"#{1,2} |# Brief: *$|[-\s]*$", l)]
        assert not rest, "%s: text from no source: %r" % (kind, rest[:3])
        for s in re.split(r"(?<=[.!?])\s+|\n", b.skeleton(kind, ITEM)):
            assert not spend_talk.is_spend(s) and not NO_SPEND.search(s), "%s states a spend: %r" % (kind, s)
    print("   one source: %d lines, %d kinds, %d references; fixer rule from fixer_rule.py" % (len(b.LINES), len(b.KINDS), len(keys)))


def main():
    failed = 0
    tests = [t_each_kind_skeleton_passes_the_prose_check, t_the_question_and_the_stop_are_left_as_blanks,
             t_an_unknown_kind_is_refused_by_name, t_standing_lines_come_from_one_source]
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
