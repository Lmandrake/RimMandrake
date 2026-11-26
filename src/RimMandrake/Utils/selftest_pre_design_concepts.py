#!/usr/bin/env python3
"""selftest_pre_design_concepts.py: the Pre-Design Concepts store (design/pre_design_concepts/), its program
pre_design_concepts.py, and its line on MATURATION_NOW. Promises: design/specs/2026-11-26-pre-design-concepts/boundary.md.
Item RIMMANDRAKE_BUILD_IDEAS_LIST_AT_INTAKE_TWO_IDEAS_SAT_UNPLACED.

    python3 src/RimMandrake/Utils/selftest_pre_design_concepts.py

Each check first proves that it can see (a planted fault inside the test is caught), then reads the real store and the
real page. Offline: no ledger, no network (the page runs with --no-live).
"""
import datetime as DT
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STORE = os.path.join(REPO, "design", "pre_design_concepts")
PROG = os.path.join(HERE, "pre_design_concepts.py")
PAGE = os.path.join(HERE, "maturation_now.py")
sys.path.insert(0, HERE)
# hang guard on one child run; the longest measured run is about 3 s (2026-11-26)
CHILD_TIMEOUT_S = 600


def lib():
    import pre_design_concepts as P  # noqa: E402  imported late: a missing module is this test's red, named
    return P


def run(argv):
    r = subprocess.run([sys.executable] + argv, capture_output=True, text=True, timeout=CHILD_TIMEOUT_S)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def concept(name, added, offered="never", answer="none yet", kind="new mod", went=""):
    return ("# %s\n\n- **Name:** %s\n- **Kind:** %s\n- **Gets:** the player gets a planted thing.\n- **Added:** %s\n"
            "- **From ticket:** `PLANTED_TICKET_NAME_ONLY`\n- **Code:** none, planted.\n- **Last offered:** %s\n"
            "- **His answer:** %s\n%s\n## Everything known\n\nPlanted.\n"
            % (name, name, kind, added, offered, answer, ("- **Went to:** %s\n" % went) if went else ""))


def tmp_root(copy_real=True):
    """-> a temp root whose design/pre_design_concepts holds a copy of the real store (or nothing)."""
    t = tempfile.mkdtemp(prefix="pre_design_concepts_st_")
    d = os.path.join(t, "design", "pre_design_concepts")
    if copy_real:
        shutil.copytree(STORE, d)
    else:
        os.makedirs(d)
    return t, d


def page(root):
    rc, out = run([PAGE, "--root", root, "--no-live", "--no-phone", "--print", "--print-detail"])
    assert rc == 0, "maturation_now.py could not build the page: rc=%d %s" % (rc, out[-400:])
    return out


def page_line(text):
    line = next((x for x in text.splitlines() if x.startswith("Pre-design concepts: ")), None)
    assert line, "the page has no 'Pre-design concepts:' line"
    m = re.match(r"Pre-design concepts: (\S+?)(?:\.| · (.*?))(?: \(`|$)", line)
    assert m, "the page line has no count: %s" % line[:200]
    return m.group(1), (m.group(2) or ""), line


def t_check_passes_on_the_real_store():
    """`check` exits 0 on the real store; a concept file that lacks a field fails by the file's name and the field."""
    P = lib()
    t, d = tmp_root()
    try:
        files = sorted(f for f in os.listdir(d) if f.endswith(".md") and f != "README.md")
        assert files, "the real store holds no concept file"
        p = os.path.join(d, files[0])
        text = open(p, encoding="utf-8").read()
        broken = re.sub(r"(?m)^- \*\*Kind:\*\*.*\n", "", text, count=1)
        assert broken != text, "the plant did not change %s" % files[0]
        open(p, "w", encoding="utf-8").write(broken)
        rc, out = run([PROG, "check", "--store", d])
        assert rc == 1 and files[0] in out and "Kind" in out, "a file with no Kind was not named: rc=%d %s" % (rc, out)
    finally:
        shutil.rmtree(t)
    rc, out = run([PROG, "check"])
    assert rc == 0, "check fails on the real store: %s" % out[-600:]
    r = P.read_store(STORE)
    assert r["count"] != P.UNM and not r["faults"], (r["why"], r["faults"])
    for c in r["concepts"]:
        assert re.search(r'"[^"]{8,}"', c["body"]), "%s: the body quotes no owner words" % c["file"]


def t_page_count_equals_store_count():
    """The page's count of concepts that wait, and each plain name, equal the store's; a concept added moves both."""
    P = lib()
    r = P.read_store(STORE)
    t, d = tmp_root()
    try:
        n, names, _ = page_line(page(t))
        assert n == str(r["count"]), "the page says %s concepts, the store holds %s" % (n, r["count"])
        for nm in r["names"]:
            assert nm in names, "the page does not name %r: %r" % (nm, names)
        open(os.path.join(d, "planted_one.md"), "w", encoding="utf-8").write(concept("Planted one", "2026-01-01"))
        open(os.path.join(d, "planted_gone.md"), "w", encoding="utf-8").write(
            concept("Planted gone", "2026-01-01", went="a mod at the intake"))
        n2, names2, _ = page_line(page(t))
        assert n2 == str(r["count"] + 1) and "Planted one" in names2 and "Planted gone" not in names2, (n2, names2)
    finally:
        shutil.rmtree(t)


def t_unreadable_store_reads_unmeasured():
    """A store that cannot be read gives UNMEASURED with its cause on the page, never 0: a missing folder, a file in
    the folder's place, a concept file that cannot be read. An empty store reads 0, a measured zero."""
    cases = []
    t, d = tmp_root(copy_real=False)
    shutil.rmtree(d)
    cases.append((t, "missing"))
    t, d = tmp_root(copy_real=False)
    os.rmdir(d)
    open(d, "w").write("not a folder")
    cases.append((t, "NotADirectoryError"))
    t, d = tmp_root(copy_real=False)
    os.makedirs(os.path.join(d, "a_folder.md"))
    cases.append((t, "a_folder.md"))
    for t, cause in cases:
        try:
            n, _, line = page_line(page(t))
        finally:
            shutil.rmtree(t)
        assert n == "UNMEASURED", "an unreadable store (%s) gave %r on the page" % (cause, n)
        assert cause in line, "the UNMEASURED line does not name %r: %s" % (cause, line[:300])
    t, d = tmp_root(copy_real=False)
    try:
        n, _, _ = page_line(page(t))
    finally:
        shutil.rmtree(t)
    assert n == "0", "an empty store did not read a measured 0: %r" % n


def t_due_puts_never_offered_first():
    """`due` lists the concepts never offered first, oldest added first, then the ones offered longest ago; at most
    four; never a concept that went. `offered` writes the date and his answer, and moves the concept back."""
    t, d = tmp_root(copy_real=False)
    try:
        for fn, args in (("old_offer.md", ("Old offer", "2026-01-01", "2026-02-01", "let it sleep")),
                         ("new_offer.md", ("New offer", "2026-01-01", "2026-03-01", "let it sleep")),
                         ("never_late.md", ("Never late", "2026-05-01")),
                         ("never_early.md", ("Never early", "2026-04-01")),
                         ("gone.md", ("Gone", "2025-01-01", "never", "none yet", "new mod", "a ticket")),
                         ("fifth.md", ("Fifth", "2026-01-01", "2026-04-01", "let it sleep"))):
            open(os.path.join(d, fn), "w", encoding="utf-8").write(concept(*args))
        rc, out = run([PROG, "due", "--store", d])
        got = [ln.split(" · ")[0].strip() for ln in out.splitlines() if ln.strip()]
        assert rc == 0 and got == ["Never early", "Never late", "Old offer", "New offer"], (rc, out)
        rc, out = run([PROG, "offered", "never early", "--answer", "a planted answer", "--store", d])
        assert rc == 0, out
        text = open(os.path.join(d, "never_early.md"), encoding="utf-8").read()
        today = DT.date.today().isoformat()
        assert "- **Last offered:** %s" % today in text and "a planted answer" in text, text[:600]
        rc, out = run([PROG, "due", "--store", d])
        got = [ln.split(" · ")[0].strip() for ln in out.splitlines() if ln.strip()]
        assert got == ["Never late", "Old offer", "New offer", "Fifth"], got
        rc, out = run([PROG, "offered", "no such concept", "--answer", "x", "--store", d])
        assert rc != 0 and "no such concept" in out, "an unknown name was not refused by name: %s" % out
    finally:
        shutil.rmtree(t)


def main():
    tests = [t_check_passes_on_the_real_store, t_page_count_equals_store_count, t_unreadable_store_reads_unmeasured,
             t_due_puts_never_offered_first]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001  each test's own red, named
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (e.__class__.__name__, str(e)[:500]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL %d PASS" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
