#!/usr/bin/env python3
"""selftest_ruling_search.py: the promises of design/specs/2026-11-27-ruling-search/boundary.md (each t_ function is one
promise, by name). Offline: a temp tree with the five rule trees. Written before ruling_search.py; seen failing on the
base (the module absent).

    python3 src/RimMandrake/rimflow/selftest_ruling_search.py
"""
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE,):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True

RULING = "No faction work starts until the owner says so"
FILLER = "Textures are 64 pixels square and the art folder holds one file per def.\n"
# one planted line per tree: it holds the ruling's content words and says the opposite
PLANTS = {
    "CLAUDE.md": "CLAUDE.md",
    "standing_rulings": "design/RimMandrake/standing_rulings.md",
    "roles": "src/RimMandrake/rimflow/roles/builder.md",
    "skills": "skills/demo/SKILL.md",
    "boundary": "design/specs/2026-11-27-demo/boundary.md",
}
PLANT_LINE = "Faction work starts at once; the owner need not say so.\n"


def tree(planted=True, skip=()):
    root = tempfile.mkdtemp(prefix="rsearch_")
    for name, rel in PLANTS.items():
        if name in skip:
            continue
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write("# Heading\n\n" + FILLER + (PLANT_LINE if planted else FILLER) + FILLER)
    return root


def S():
    import ruling_search
    return ruling_search


def run(root, *extra):
    buf = io.StringIO()
    code = S().main(["--root", root] + list(extra) + [RULING], out=buf)
    return code, buf.getvalue()


def section(text, name):
    """The block of output that belongs to one tree: from its '== name' line to the next '== ' line."""
    out, on = [], False
    for ln in text.splitlines():
        if ln.startswith("SUMMARY"):
            on = False
        if ln.startswith("== "):
            on = ln.startswith("== " + name + ":")
        if on:
            out.append(ln)
    return "\n".join(out)


def t_finds_a_planted_opposite_line_in_each_tree():
    root = tree()
    code, text = run(root)
    assert code == 0, (code, text)
    for name, rel in PLANTS.items():
        sec = section(text, name)
        assert sec, "no block for tree %s in:\n%s" % (name, text)
        assert os.path.basename(rel) + ":4" in sec, "tree %s: planted line (line 4) not listed:\n%s" % (name, sec)
    assert "none (looked)" not in text, text


def t_prints_file_line_and_the_negation_words():
    root = tree()
    p = os.path.join(root, "CLAUDE.md")
    with open(p, "w") as f:
        f.write("# H\n\nDo not park it.\nFaction work: never start it; the owner has not said so.\nplain\n")
    code, text = run(root)
    sec = section(text, "CLAUDE.md")
    assert "CLAUDE.md:4" in sec, sec
    line = [ln for ln in sec.splitlines() if "CLAUDE.md:4" in ln][0]
    assert "never" in line and "not" in line, "negation words of the line itself not printed: " + line
    assert "do not" in line.lower() or "near" in line.lower(), "the negation on the neighbour line is not shown: " + line
    assert "terms" in line, "the term count is not printed: " + line


def t_no_hit_reads_none_looked():
    root = tree(planted=False)
    code, text = run(root)
    assert code == 1, (code, text)
    for name in PLANTS:
        sec = section(text, name)
        assert "none (looked)" in sec, "tree %s did not read 'none (looked)':\n%s" % (name, text)
        assert "line" in sec and "file" in sec, "what was searched is not said:\n" + sec
    assert not any(ln.strip() == "" for ln in text.splitlines()[:1]), "output starts blank"


def t_an_unreadable_tree_reads_could_not_look():
    root = tree(skip=("skills",))                       # the skills root is missing
    code, text = run(root)
    assert code == 3, (code, text)
    sec = section(text, "skills")
    assert "COULD NOT LOOK" in sec and os.path.join(root, "skills") in sec, sec
    assert "FAULT" not in text and "Traceback" not in text, text
    assert "CLAUDE.md:4" in text, "the trees that could be read are still printed"
    # a file that cannot be decoded: the tree says so and names the file; the rest of the tree is still read
    root = tree()
    os.makedirs(os.path.join(root, "design/specs/2026-11-27-bad"))
    with open(os.path.join(root, "design/specs/2026-11-27-bad/boundary.md"), "wb") as f:
        f.write(b"\xff\xfe\xfa not utf8 \x80\x81\n")
    code3, text3 = run(root)
    assert "boundary.md:4" in section(text3, "boundary"), "the readable part of the tree is not printed:\n" + text3
    assert code3 == 3 and "COULD NOT LOOK" in section(text3, "boundary") and "2026-11-27-bad" in section(text3, "boundary"), text3


def main():
    failed = 0
    tests = [t_finds_a_planted_opposite_line_in_each_tree, t_prints_file_line_and_the_negation_words,
             t_no_hit_reads_none_looked, t_an_unreadable_tree_reads_could_not_look]
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except BaseException as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
