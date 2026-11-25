#!/usr/bin/env python3
"""Selftest: the owner's "positive steps" text has one source (item RIMMANDRAKE_SHARE_POSITIVE_STEPS_TEXT_FOUR_COPIES_DRIFTED).

.claude/rm_positive_steps.md holds his words; every carrier below must contain each line of it, whitespace collapsed.
Promises (design/specs/2026-11-19-positive-steps-one-source/boundary.md), each with a test of its name:
an-edited-copy-is-refused, a-missing-copy-is-refused, an-edited-source-refuses-every-carrier,
a-missing-or-empty-source-is-refused, the-real-tree-is-clean.

    python3 src/RimMandrake/Utils/selftest_positive_steps_one_source.py
"""
import os, re, shutil, sys, tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SOURCE = os.path.join(".claude", "rm_positive_steps.md")
FILES = [os.path.join("src", "RimMandrake", "rimflow", "roles", "builder.md"),     # the one builder role
         os.path.join(".claude", "agents", "rm-builder.md"),
         os.path.join(".claude", "agents", "rm-fixer.md")]
PY = [("maturation.HOW_A_BAR_HOLDS", "maturation", "HOW_A_BAR_HOLDS"),
      ("testpilot_route.HOLDS_LINES", "testpilot_route", "HOLDS_LINES")]
FAILS = []


def flat(s):
    return re.sub(r"\s+", " ", s).strip()


def source_lines(root):
    """-> (lines, problem). Two or more non-empty lines, else a problem (never an empty pass)."""
    p = os.path.join(root, SOURCE)
    if not os.path.isfile(p):
        return [], "%s is missing" % SOURCE
    with open(p, encoding="utf-8") as fh:
        lines = [flat(x) for x in fh.read().splitlines() if x.strip()]
    if len(lines) < 2:
        return [], "%s holds %d line(s), not his text" % (SOURCE, len(lines))
    return lines, None


def carrier_texts(root):
    """-> {name: text or None when it could not be read}. Python carriers are imported from `root`'s rimflow."""
    out = {}
    for rel in FILES:
        p = os.path.join(root, rel)
        out[rel] = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
    sys.path.insert(0, os.path.join(root, "src", "RimMandrake", "rimflow"))
    try:
        for name, mod, attr in PY:
            sys.modules.pop(mod, None)
            try:
                v = getattr(__import__(mod), attr)
                out[name] = v if isinstance(v, str) else "\n".join(v)
            except Exception as e:  # could not look, named, never a pass
                out[name] = None
                print("could not load %s: %s" % (name, e))
    finally:
        sys.path.pop(0)
    return out


def problems(root, texts=None):
    lines, bad = source_lines(root)
    if bad:
        return [bad]
    out = []
    for name, text in (texts if texts is not None else carrier_texts(root)).items():
        if text is None:
            out.append("%s: could not be read" % name)
            continue
        t = flat(text)
        out += ["%s: lacks his line %r" % (name, l[:40] + "...") for l in lines if l not in t]
    return out


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def planted(fault):
    tmp = tempfile.mkdtemp(prefix="selftest_positive_steps_")
    for rel in FILES + [SOURCE]:
        os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
        shutil.copy(os.path.join(REPO, rel), os.path.join(tmp, rel))
    fault(tmp)
    return tmp


def edit(root, rel, old, new):
    p = os.path.join(root, rel)
    t = open(p, encoding="utf-8").read()
    assert old in t, (rel, old)
    open(p, "w", encoding="utf-8").write(t.replace(old, new, 1))


def file_problems(root):
    """The four file carriers only (the Python carriers are read from the real tree, in the real-tree test)."""
    return problems(root, {r: (open(os.path.join(root, r), encoding="utf-8").read()
                               if os.path.isfile(os.path.join(root, r)) else None) for r in FILES})


def t_an_edited_copy_is_refused():
    t = planted(lambda r: edit(r, FILES[2], "Create instruments to prove", "Create instrument to prove"))
    p = file_problems(t)
    check(len(p) == 1 and FILES[2] in p[0], "an-edited-copy-is-refused (one word, only that file)")
    shutil.rmtree(t, ignore_errors=True)
    t = planted(lambda r: edit(r, FILES[0], "Get inventive.", "Be inventive."))
    check(any(FILES[0] in x for x in file_problems(t)), "an-edited-copy-is-refused (the builder role)")
    shutil.rmtree(t, ignore_errors=True)


def t_a_missing_copy_is_refused():
    t = planted(lambda r: os.remove(os.path.join(r, FILES[1])))
    check(any(FILES[1] in x and "could not be read" in x for x in file_problems(t)), "a-missing-copy-is-refused (file gone)")
    shutil.rmtree(t, ignore_errors=True)
    t = planted(lambda r: edit(r, FILES[0], "Hunt parameter regimes and regions, not examples.", ""))
    check(any(FILES[0] in x for x in file_problems(t)), "a-missing-copy-is-refused (line gone)")
    shutil.rmtree(t, ignore_errors=True)


def t_an_edited_source_refuses_every_carrier():
    t = planted(lambda r: edit(r, SOURCE, "Think outside the box", "Think inside the box"))
    check(len(file_problems(t)) == len(FILES), "an-edited-source-refuses-every-carrier")
    shutil.rmtree(t, ignore_errors=True)


def t_a_missing_or_empty_source_is_refused():
    t = planted(lambda r: os.remove(os.path.join(r, SOURCE)))
    check(file_problems(t) == ["%s is missing" % SOURCE], "a-missing-or-empty-source-is-refused (missing)")
    shutil.rmtree(t, ignore_errors=True)
    t = planted(lambda r: open(os.path.join(r, SOURCE), "w").close())
    check(len(file_problems(t)) == 1, "a-missing-or-empty-source-is-refused (empty)")
    shutil.rmtree(t, ignore_errors=True)


def t_the_real_tree_is_clean():
    bad = problems(REPO)
    check(not bad, "the-real-tree-is-clean%s" % ("" if not bad else ": " + "; ".join(bad)))


def main():
    t_an_edited_copy_is_refused()
    t_a_missing_copy_is_refused()
    t_an_edited_source_refuses_every_carrier()
    t_a_missing_or_empty_source_is_refused()
    t_the_real_tree_is_clean()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
