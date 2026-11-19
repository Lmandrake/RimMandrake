#!/usr/bin/env python3
"""era_history_mark: head every record file that names a retired era with the HISTORY line, so a reader of it sees at
its top that the Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 machinery it names no longer runs
(RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS).

The owner, 2026-11-18: "I do not want to lose the wisdom, just remove all future confusion please." A record file is a
design doc, a skill reference, a lesson or a fact (rimflow/era_text.py `MARKABLE`); a file every agent is handed
(`LIVE_ALWAYS`: CLAUDE.md, agent definitions, roles, SKILL.md files, the standing rulings) is never marked here: it is
corrected line by line, and the era gate (rimflow/selftest_retired_era_gone.py, at ./publish) refuses it until it is.
Only files with at least one era line that does not say it is past are marked; the rule is era_text.era_lines.

    python3 src/RimMandrake/Utils/era_history_mark.py            dry run: list what would be marked, by kind
    python3 src/RimMandrake/Utils/era_history_mark.py --apply    write the heads

Exit: 0 = looked and nothing left to mark (or --apply marked them all); 1 = dry run found files to mark;
2 = could not look (git unreadable, or no file in scope was read).
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import era_text  # noqa: E402


def kind(p):
    if p.startswith("infrastructure/state/lessons/"):
        return "lesson"
    if p.startswith("skills/"):
        return "skill reference"
    if p.startswith("infrastructure/state/facts/"):
        return "fact"
    return "design doc"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="write the HISTORY heads (default: list them)")
    a = ap.parse_args(argv)
    try:
        raw = subprocess.run(["git", "-C", REPO, "ls-files", "-z"], capture_output=True, check=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError) as e:
        print("COULD NOT LOOK: git ls-files failed: %s" % e)
        return 2
    paths = [os.fsdecode(x) for x in raw.split(b"\0") if x]
    todo, read = [], 0
    for p in paths:
        if era_text.text_scope(p) != "mark":
            continue
        try:
            with open(os.path.join(REPO, p), encoding="utf-8", newline="") as f:
                text = f.read()
        except FileNotFoundError:
            continue
        except (OSError, UnicodeError) as e:
            print("UNREADABLE %s: %s" % (p, e))
            continue
        read += 1
        if era_text.check_text(p, text):
            todo.append((p, text))
    if read == 0:
        print("COULD NOT LOOK: no record file in scope was read")
        return 2
    counts = {}
    for p, text in todo:
        counts[kind(p)] = counts.get(kind(p), 0) + 1
        if a.apply:
            new = era_text.mark_text(p, text)
            if new is None:
                print("NOT MARKABLE %s" % p)
                continue
            with open(os.path.join(REPO, p), "w", encoding="utf-8", newline="") as f:
                f.write(new)
        else:
            print("would mark %s" % p)
    summary = ", ".join("%d %s(s)" % (n, k) for k, n in sorted(counts.items())) or "none"
    if a.apply:
        print("MARKED %d of %d record files read: %s" % (len(todo), read, summary))
        return 0
    print("%s: %d of %d record files read need the HISTORY head: %s" % ("TO MARK" if todo else "NONE", len(todo), read,
                                                                          summary))
    return 1 if todo else 0


if __name__ == "__main__":
    sys.exit(main())
