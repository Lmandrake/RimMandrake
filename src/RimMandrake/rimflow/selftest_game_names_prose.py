#!/usr/bin/env python3
"""selftest_game_names_prose.py - rule text and role files name the games ArchBig, ArchSmall, Steve1, Steve2.

The owner, by card 2026-11-22: "A and b lower case are very hard to read and recognize." · "Let's go with ArchBig,
ArchSmall, Steve1 & Steve2." (item RIMMANDRAKE_RENAME_GAMES_ARCHBIG_ARCHSMALL_STEVE1_STEVE2_LETTERS_UNREADABLE).
Covered, on files only (nothing launched, nothing written):
  prose   CLAUDE.md, infrastructure/agents/*.md, rimflow/roles/*.md, standing_rulings.md, every skills/*/SKILL.md, the
          SteveDesktop RUNBOOK and the game pages never call a game "game a", "game b" or game:a outside a `code span`
          (a code span may name the old key as an alias) or an owner quote (*"..."*).
  probe   a planted bad line is caught and a good one passes (the instrument can see).
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FAILS = []

# "game a", "Game b's", "games a and b", "game:a" as a game's name; not "game a run" (English: "the first game a run
# may take") and not a hyphenated promise name (a-full-list-on-game-b-beside-game-a is a test's name, not prose).
BAD = re.compile(r"(?<!-)\b[Gg]ames? [ab]\b(?!-)(?! (?:live )?run\b)|(?<!-)\bgame:[ab]\b")
CODE = re.compile(r"`[^`\n]*`")
QUOTE = re.compile(r'\*"[^"]*"\*')


def check(ok, what, detail=""):
    print(("ok   " if ok else "FAIL ") + what + ("" if ok else "  " + str(detail)[:1500]))
    if not ok:
        FAILS.append(what)


def bad_lines(text):
    """-> [(line number, line)] that name a game by its old letter in prose."""
    out = []
    for n, ln in enumerate(text.splitlines(), 1):
        if BAD.search(QUOTE.sub(" ", CODE.sub(" ", ln))):
            out.append((n, ln.strip()))
    return out


def prose_files():
    pats = ["CLAUDE.md", "infrastructure/agents/*.md", "src/RimMandrake/rimflow/roles/*.md",
            "design/RimMandrake/standing_rulings.md", "skills/*/SKILL.md", "infrastructure/stevedesktop/RUNBOOK.md",
            "design/specs/2026-11-20-per-game-hold-own-install/boundary.md",
            "design/specs/2026-11-21-one-game-lock/boundary.md", "design/specs/2026-11-22-game-names/boundary.md"]
    out = []
    for p in pats:
        out += sorted(glob.glob(os.path.join(ROOT, p)))
    return out


def t_rule_text_and_role_files_name_games_by_name():
    files = prose_files()
    check(len(files) >= 10 and any(f.endswith("CLAUDE.md") for f in files),
          "the instrument finds the rule files (%d)" % len(files), files[:3])
    hits = []
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as fh:
            hits += ["%s:%d: %s" % (os.path.relpath(f, ROOT), n, ln[:160]) for n, ln in bad_lines(fh.read())]
    check(not hits, "no rule or role file calls a game 'game a' / 'game b' (%d lines)" % len(hits), "\n" + "\n".join(hits))


def t_the_check_can_see():
    bad = ["If game a is busy, use game b.", "His walk holds game:a only.", "Game b's own install.",
           "games a and b run beside each other"]
    good = ["If ArchBig is busy, use ArchSmall; `game:a` and `archmagi.b` still work.",
            "the first game a run may take", "a-full-list-on-game-b-beside-game-a", '*"game a is his"* he said']
    check(all(bad_lines(x) for x in bad), "a planted 'game a' line is caught", [x for x in bad if not bad_lines(x)])
    check(not any(bad_lines(x) for x in good), "a good line passes", [x for x in good if bad_lines(x)])


def main():
    t_the_check_can_see()
    t_rule_text_and_role_files_name_games_by_name()
    print("selftest_game_names_prose: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
