#!/usr/bin/env python3
"""The check of RIMMANDRAKE_READ_STANDING_RULINGS_ONCE_WHOLE_AFTER_FIVE_REWRITES.

    whole_read_check.py table   the reader's table has one row for each `## ` section of the parent (before session one)
                                and of standing_rulings.md as it was read; a changed or lost row names its fix; every
                                owner quote of the parent is in standing_rulings.md or CLAUDE.history.md; every repo path
                                and every section pointer in the file resolves.
    whole_read_check.py tests   each test whose code (not only its docstring) names standing_rulings.md passes.
    whole_read_check.py selftest  planted faults of `table`
Exit 0 holds, 1 fails, 2 could not look."""
import ast
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FILE = "design/RimMandrake/standing_rulings.md"
PARENT = "d11bfc6623^"
TABLE = ("design/specs/2026-11-19-plain-english-rule-docs/results/"
         "RIMMANDRAKE_READ_STANDING_RULINGS_ONCE_WHOLE_AFTER_FIVE_REWRITES.md")
VERDICTS = ("kept", "changed", "lost", "new")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def at(sha):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (sha, FILE)], capture_output=True, text=True)
    if r.returncode:
        print("COULD NOT LOOK: %s" % r.stderr.strip())
        sys.exit(2)
    return r.stdout


def key(head):
    """A heading without its marks and its trailing owner and date part."""
    return re.sub(r"\s*(—|\()\s*owner.*$", "", head.lstrip("# ")).replace("🔴", "").replace("`", "").strip()


def heads(text):
    return [key(h) for h in text.splitlines() if h.startswith("## ")]


def flat(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def table_faults(table, parent, read_text, now, history):
    out, rows = [], {}
    for line in table.splitlines():
        c = [x.strip() for x in line.strip().strip("|").split(" | ")]
        if line.startswith("| ") and len(c) == 3 and c[1] in VERDICTS:
            rows[c[0].replace("`", "")] = (c[1], c[2])
    for h in dict.fromkeys(heads(parent) + heads(read_text)):
        if h not in rows:
            out.append("no row for the section %r" % h)
    for h, (v, fix) in rows.items():
        if v in ("changed", "lost") and len(fix) < 12:
            out.append("the %s row of %r names no fix" % (v, h))
    have = flat(now) + " " + flat(history)
    for m in re.finditer(r'(?<![*"])\*"(.{12,}?)"\*(?!\*)', parent, re.S):
        if flat(m.group(1)) not in have:
            out.append("his words are gone: %s" % flat(m.group(1))[:90])
    for p in sorted(set(re.findall(r"`((?:src|design|infrastructure|skills|\.claude)/[^`\s<>*…]+)`", now))):
        if not os.path.exists(os.path.join(ROOT, p.split("::")[0])):
            out.append("dead path: %s" % p)
    known = [flat(x) for x in re.findall(r"^#+ (.*)$", now, re.M)]
    for m in set(re.findall(r"\(§([A-Z][A-Za-z' ,\-]{11,60})", re.sub(r"\s+", " ", now))):
        w = flat(m.split(",")[0])[:22]
        if not any(k.startswith(w) for k in known):
            out.append("a section pointer resolves to no heading: §%s" % m)
    return out


def names_it(path):
    """The test's code holds the file's name in a string that is not a docstring."""
    tree = ast.parse(read(path))
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr)}
    return any(isinstance(n, ast.Constant) and isinstance(n.value, str) and "standing_rulings" in n.value
               and id(n) not in docs for n in ast.walk(tree))


def tests():
    ls = subprocess.run(["git", "-C", ROOT, "grep", "-l", "standing_rulings", "--", "*.py"], capture_output=True, text=True)
    cand = [p for p in ls.stdout.split() if re.search(r"selftest_|accept|/case_|/test_", p)]
    mine = [p for p in cand if names_it(p)]
    if len(mine) < 10:
        print("COULD NOT LOOK: only %d tests found" % len(mine))
        return 2

    def one(p):
        # no deadline here: list_effect.py's own 600 s hang guard covers the whole command
        r = subprocess.run([sys.executable, os.path.join(ROOT, p)], cwd=ROOT, capture_output=True, text=True)
        return p, r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:]
    bad = 0
    with ThreadPoolExecutor(4) as ex:
        for p, rc, last in ex.map(one, mine):
            print("%s %s %s" % ("ok  " if rc == 0 else "FAIL rc=%d" % rc, p, "" if rc == 0 else last))
            bad += rc != 0
    print("%d tests whose code names the file, %d fail; docstring only, not run: %s"
          % (len(mine), bad, ", ".join(sorted(set(cand) - set(mine))) or "none"))
    return 1 if bad else 0


def selftest():
    par = '## A — owner, 2026-01-01\n\n*"the words of the owner here"*\n\n## B (owner, x)\nt\n'
    now = par + "## C\n"
    tab = "| A | kept | same |\n| B | changed | restored the second line |\n| C | new | - |\n"
    cases = [("good", (tab, par, now, now, ""), 0),
             ("row missing", (tab.replace("| C | new | - |\n", ""), par, now, now, ""), 1),
             ("no fix named", (tab.replace("restored the second line", "-"), par, now, now, ""), 1),
             ("quote lost", (tab, par, now, now.replace("owner here", "agent here"), ""), 1),
             ("quote in history", (tab, par, now, "## A\n## B\n## C\n", "the words of the owner here"), 0),
             ("dead path", (tab, par, now, now + "`design/no/such_file.md`\n", ""), 1),
             ("dead pointer", (tab, par, now, now + "(§No such section at all)\n", ""), 1)]
    bad = [n for n, a, want in cases if len(table_faults(*a)) != want]
    print("selftest %s %s" % ("FAIL" if bad else "PASS", bad))
    return 1 if bad else 0


def main(argv):
    verb = argv[0] if argv else ""
    if verb == "selftest":
        return selftest()
    if verb == "tests":
        return tests()
    if verb != "table":
        print(__doc__)
        return 2
    if not os.path.isfile(os.path.join(ROOT, TABLE)):
        print("no table: %s" % TABLE)
        return 1
    table = read(TABLE)
    m = re.search(r"^Read at: `?([0-9a-f]{8,40})", table, re.M)
    if not m:
        print("the table names no `Read at:` commit")
        return 1
    faults = table_faults(table, at(PARENT), at(m.group(1)), read(FILE), read("design/RimMandrake/CLAUDE.history.md"))
    for f in faults:
        print("FAULT " + f)
    print("%d faults" % len(faults))
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
