#!/usr/bin/env python3
"""Selftest for check_doc_links.py — run after ANY change to it.

⚠️ THIS TEST EXISTS BECAUSE THE LIVE RUN CANNOT PROVE THE TOOL WORKS. On 2026-08-20
the repo contained exactly one dead document and zero links into it, so the checker
reported a clean pass — the same output it would print if the rule were never
evaluated at all. A green run on a corpus with no violations is not evidence.

So this builds a throwaway `design/` tree with violations in it and checks that each
is caught, and that each legal shape is not.

    python3 src/RimMandrake/Utils/selftest_check_doc_links.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "check_doc_links.py")

FILES = {
    "design/dead_one.md":
        "<!-- status: dead ; 2026-08-18 ; the owner banned offline save writing -->\n"
        "# Dead\nSee [live](live_one.md).\n",
    "design/gone.md":
        "<!-- status: superseded-by: design/live_one.md ; 2026-08-19 ; moved -->\n"
        "# Superseded\n",
    "design/aspirational_one.md": "<!-- status: aspirational -->\n# Someday\n",
    "design/live_one.md": "<!-- status: live -->\n# Live\nNothing to see.\n",
}

# (name, extra file, its body, expect a violation)
CASES = [
    ("live doc links INTO a dead doc", "design/offender.md",
     "<!-- status: live -->\n# X\nRead [the pipeline](dead_one.md) first.\n", True),

    ("a backtick path counts as a link too", "design/offender.md",
     "<!-- status: live -->\n# X\nSee `design/dead_one.md`.\n", True),

    ("an UNMARKED doc linking into a dead one still violates", "design/offender.md",
     "# X\nRead [the pipeline](dead_one.md) first.\n", True),

    # Citing a dead doc AS dead is the correct way to write a supersession note.
    # If this ever fails, every good correction in the repo becomes an error.
    ("citing it as dead is legal — strikethrough", "design/offender.md",
     "<!-- status: live -->\n# X\n~~[the pipeline](dead_one.md)~~ is dead.\n", False),
    ("citing it as dead is legal — the word 'superseded'", "design/offender.md",
     "<!-- status: live -->\n# X\nsuperseded by nothing: [old](dead_one.md).\n", False),
    ("citing it as dead is legal — inside a table cell", "design/offender.md",
     "<!-- status: live -->\n# X\n| ⛔ dead | [old](dead_one.md) | gone |\n", False),

    ("a DEAD doc may link anywhere — it is dead", "design/another_dead.md",
     "<!-- status: dead ; 2026-08-01 ; x -->\n# D\n[live](live_one.md) [d](dead_one.md)\n",
     False),

    ("superseded is a forwarding address, not a grave", "design/offender.md",
     "<!-- status: live -->\n# X\nSee [gone](gone.md).\n", False),

    ("a link inside a code fence is not a link", "design/offender.md",
     "<!-- status: live -->\n# X\n```\n[p](dead_one.md)\n```\n", False),

    ("no link at all", "design/offender.md", "<!-- status: live -->\n# X\nnothing.\n",
     False),
]


def run(extra_path, extra_body, args=()):
    root = tempfile.mkdtemp(prefix="selftest_cdl_")
    try:
        for rel, body in list(FILES.items()) + [(extra_path, extra_body)]:
            full = os.path.join(root, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(body)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
        p = subprocess.run([sys.executable, TOOL, *args], capture_output=True,
                           text=True, env=env, cwd=root, timeout=30)
        return p.returncode, p.stdout + p.stderr
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    fails = 0
    for name, path, body, expect in CASES:
        code, out = run(path, body)
        ok = (code == 1) == expect
        print("%-5s %s" % ("ok" if ok else "FAIL", name))
        if not ok:
            fails += 1
            print("        exit=%s expected_violation=%s\n        %s"
                  % (code, expect, out.strip().replace("\n", "\n        ")[:500]))

    # --require-status turns "nobody has said" into a failure. Until W3(a) has run
    # everywhere it would fail on 117 docs, which is why it is opt-in and not default.
    code, out = run("design/unmarked.md", "# No header here\n", ("--require-status",))
    ok = code == 1 and "no status header" in out
    print("%-5s %s" % ("ok" if ok else "FAIL", "--require-status fails on an unmarked doc"))
    if not ok:
        fails += 1
        print("        exit=%s\n        %s" % (code, out[:400]))
    code, _ = run("design/unmarked.md", "# No header here\n")
    ok = code == 0
    print("%-5s %s" % ("ok" if ok else "FAIL", "…and without the flag it does not"))
    if not ok:
        fails += 1

    total = len(CASES) + 2
    print("\n%d/%d passed" % (total - fails, total))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
