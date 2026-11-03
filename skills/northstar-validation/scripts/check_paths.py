#!/usr/bin/env python3
"""Every repo path this skill cites must exist (exit 0), else list the dead ones (exit 1).

    python3 skills/northstar-validation/scripts/check_paths.py

A path is a backticked token starting with src/ design/ infrastructure/ skills/ (trailing `:`, `/` and a
following ` --flag` are not part of it). A bare module name such as `watch.py` is resolved against
src/RimMandrake/Utils/modcheck/, its live_queue/ subfolder and src/RimMandrake/Utils/, where the skill
says they live. A token that cannot be resolved there is reported, so a renamed or deleted module turns this red. Zero paths found is
itself a failure: an instrument that saw nothing has not proved anything.
"""
import pathlib
import re
import sys

SKILL = pathlib.Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[1]
UTILS = ROOT / "src" / "RimMandrake" / "Utils"
MODCHECK = UTILS / "modcheck"
BARE_DIRS = (MODCHECK, MODCHECK / "live_queue", UTILS)
REPO_PREFIX = re.compile(r"^(src|design|infrastructure|skills)/")


def tokens(text):
    for tok in re.findall(r"`([^`\n]+)`", text):
        yield tok.split()[0].rstrip(":,") if tok.split() else tok


def main():
    checked, dead = 0, []
    for md in sorted(SKILL.rglob("*.md")):
        for tok in tokens(md.read_text(encoding="utf-8")):
            if "<" in tok or "*" in tok:
                continue                                   # a template (<Mod>) or glob, not a path
            if REPO_PREFIX.match(tok):
                checked += 1
                if not (ROOT / tok.rstrip("/")).exists():
                    dead.append("%s: %s" % (md.relative_to(ROOT), tok))
            elif re.fullmatch(r"[A-Za-z_]+\.py", tok):
                checked += 1
                if not any((d / tok).exists() for d in BARE_DIRS):
                    dead.append("%s: %s (not in Utils/, modcheck/ or modcheck/live_queue/)" % (md.relative_to(ROOT), tok))
    print("checked %d cited paths, %d dead" % (checked, len(dead)))
    for d in dead:
        print("  DEAD " + d)
    if checked == 0:
        print("  no paths found: the instrument saw nothing")
        return 1
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
