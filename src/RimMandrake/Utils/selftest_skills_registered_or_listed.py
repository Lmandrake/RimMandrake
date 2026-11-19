#!/usr/bin/env python3
"""Selftest: every folder in skills/ with a SKILL.md is either linked in .claude/skills/
or listed in the skills/README.md table "Not registered (read by path)", never neither,
never both (item RIMMANDRAKE_UNREGISTER_DORMANT_SKILLS_HE_INVOKES_BY_NAME).

Cases on throwaway trees (linked ok, listed ok, neither fails, both fails), then the real tree.
"""
import os, re, shutil, sys, tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FAILS = []


def listed_names(readme_text):
    """Backticked first cell of each row under the 'Not registered' heading."""
    m = re.search(r"^## Not registered \(read by path\)\s*$(.*?)(?=^## |\Z)", readme_text, re.S | re.M)
    if not m:
        return set()
    return set(re.findall(r"^\|\s*`([\w.-]+)`\s*\|", m.group(1), re.M))


def violations(root):
    sk = os.path.join(root, "skills")
    linked_dir = os.path.join(root, ".claude", "skills")
    readme = os.path.join(sk, "README.md")
    listed = listed_names(open(readme, encoding="utf-8").read()) if os.path.exists(readme) else set()
    bad = []
    for n in sorted(os.listdir(sk)):
        if not os.path.exists(os.path.join(sk, n, "SKILL.md")):
            continue
        linked = os.path.exists(os.path.join(linked_dir, n, "SKILL.md"))
        if linked and n in listed:
            bad.append("%s: both linked and listed" % n)
        elif not linked and n not in listed:
            bad.append("%s: neither linked nor listed" % n)
    return bad


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def tree(linked, listed):
    t = tempfile.mkdtemp(prefix="selftest_skills_reg_")
    os.makedirs(os.path.join(t, "skills", "demo"))
    open(os.path.join(t, "skills", "demo", "SKILL.md"), "w").write("---\nname: demo\n---\n")
    os.makedirs(os.path.join(t, ".claude", "skills"))
    if linked:
        os.symlink(os.path.join("..", "..", "skills", "demo"), os.path.join(t, ".claude", "skills", "demo"))
    rows = "| `demo` | path | when | undo |\n" if listed else ""
    open(os.path.join(t, "skills", "README.md"), "w").write(
        "# Skills\n\n## Not registered (read by path)\n\n| skill | p | w | u |\n|---|---|---|---|\n" + rows)
    return t


def main():
    for name, linked, listed, want_bad in [("linked only", True, False, False), ("listed only", False, True, False),
                                           ("neither", False, False, True), ("both", True, True, True)]:
        t = tree(linked, listed)
        try:
            check(bool(violations(t)) == want_bad, "case %s -> %s" % (name, "violation" if want_bad else "clean"))
        finally:
            shutil.rmtree(t)
    real = violations(REPO)
    check(not real, "real tree: every skills/ folder linked xor listed %s" % real[:5])
    print("FAILED %d" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
