#!/usr/bin/env python3
r"""Selftest: exactly one place in this repo knows where RimWorld's files are.

⭐ WHY THIS IS A TEST AND NOT A RULE IN A DOC. CLAUDE.md already says it —
*"Single-source only what a GENERATOR can enforce. Where only discipline
enforces it, expect decay and write the pointer instead."* Discipline had been
enforcing this since 2026-08-13 and it decayed anyway: by 2026-08-21 **21 files**
resolved the def dump themselves, `refresh.py` had grown a whole SECOND seam off
its own literals, and three of the new literals were `/mnt/c`-only — the exact
breakage `game_paths.py` was written to fix, grown back in three new files.

🔑 **The restructure this guards.** The owner called a work stop on 2026-08-21 to
change how dump files are stored. A layout change is cheap only if there is ONE
place that says where they are. This test is what keeps that true after the
change lands, not before it.

    python3 src/RimMandrake/Utils/selftest_one_path_seam.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

PASS, FAIL = [], []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))


# ⛔ THE EXEMPTIONS, AND WHY EACH ONE IS A GUARD RATHER THAN A GAP.
# Every entry here must name a reason a reader can check. "It was like that" is
# not one — an unexplained exemption is how this list becomes the new problem.
EXEMPT = {
    "src/RimMandrake/Utils/game_paths.py":
        "IS the seam. The literals live here by definition.",
    ".claude/hooks/block_blind_scan.py":
        "a PreToolUse hook that must FAIL OPEN, always. It runs as its own "
        "process before any tool call; importing from src/ would give a guard a "
        "new way to die, and a dead guard is worse than a duplicated locator.",
    ".claude/hooks/selftest_block_blind_scan.py":
        "exercises the hook with FIXTURE paths that only look real.",
    "src/RimMandrake/Utils/rimbridge_client.py":
        "its WSL fallback GLOBS `/mnt/c/Users/*` on purpose — a BROADER search "
        "than the seam, not a narrower one, and it names no user. Added 2026-08-12 "
        "after a bad Player.log path cost a seat the hunt twice: the point is that "
        "the error you get is the true one (connection refused) rather than "
        "'is RimWorld up?'.",
    "skills/rimworld-start-prep/scripts/sync_mod_state.py":
        "a skill script, packaged and run on machines with no checkout of this "
        "repo. It cannot import from src/ because src/ may not be there.",
}

# Disposed-of code and vendored trees are not maintained and are not in scope.
#
# ⭐ `Transient/` is in this list for the same reason as `observed/`: CLAUDE.md
# defines it as output a human reads once and then bins, untracked and swept at
# ~14 days. A throwaway script that names a capture folder by hand is doing the
# right thing — it is a note about ONE capture, not code anyone maintains — and
# holding it to the seam would either delete honest scratch work or teach the
# next seat to add exemptions, which is how this list becomes the new problem.
SKIP_DIRS = (".git", "infrastructure/disposing", "node_modules", "__pycache__",
             "observed", "Transient", "src/RimMandrake/bridgetools/obj",
             "src/RimMandrake/bridgetools/bin")

LITERAL = re.compile(r"""(?xi)
    (?: [A-Za-z]:\\+Users | /mnt/[a-z]/Users )   # C:\Users…  or  /mnt/c/Users…
    .{0,120}? LocalLow
""")


def _files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT).replace("\\", "/")
        if any(rel_dir == d or rel_dir.startswith(d + "/") for d in SKIP_DIRS):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for fn in filenames:
            if fn.endswith(".py"):
                yield os.path.join(dirpath, fn)


def t_no_new_localslow_literal_outside_the_seam():
    """🔴 The one that decays. A new script hardcodes the path, it works on the
    author's machine, and the next dump move misses it."""
    offenders = []
    for path in _files():
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        if rel in EXEMPT:
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in LITERAL.finditer(text):
            line = text[:m.start()].count("\n") + 1
            offenders.append("%s:%d" % (rel, line))
    assert not offenders, (
        "%d LocalLow path literal(s) outside the seam:\n          %s\n"
        "        Import it instead:  from game_paths import DEF_DUMP, LOCALLOW, "
        "MODS_CONFIG, PLAYER_LOG\n"
        "        If the file genuinely must stand alone, add it to EXEMPT in "
        "this test WITH the reason."
        % (len(offenders), "\n          ".join(sorted(offenders))))


def t_every_exemption_still_exists():
    """An exemption for a deleted file is a hole nobody is watching."""
    gone = [p for p in EXEMPT if not os.path.exists(os.path.join(ROOT, p))]
    assert not gone, ("EXEMPT names files that no longer exist: %s — drop them, "
                      "or the next file at that path inherits a pass it never "
                      "earned." % ", ".join(sorted(gone)))


def t_every_exemption_carries_a_reason():
    thin = [p for p, why in EXEMPT.items() if len(why) < 40]
    assert not thin, ("these exemptions do not explain themselves: %s"
                      % ", ".join(sorted(thin)))


def t_refresh_does_not_run_a_second_seam():
    """`refresh.py` re-exports `D_DUMP`/`D_CONFIG` to other scripts, so if it
    resolves them itself the repo has two seams and the second has no test."""
    sys.path.insert(0, HERE)
    import game_paths
    import refresh
    assert refresh.D_DUMP == game_paths.DEF_DUMP, (
        "refresh.D_DUMP (%s) is not the seam's DEF_DUMP (%s)"
        % (refresh.D_DUMP, game_paths.DEF_DUMP))
    assert refresh.D_CONFIG == game_paths.MODS_CONFIG, (
        "refresh.D_CONFIG is not the seam's MODS_CONFIG")


def t_the_skill_locator_is_not_duplicated_inside_src():
    """`dump_manifest.skill_scripts()` promises in its own docstring that a
    moving skill changes ONE file. `refresh._measure_scripts` was a verbatim
    copy, which made that promise false."""
    sys.path.insert(0, HERE)
    import dump_manifest
    import refresh
    assert refresh._measure_scripts() == dump_manifest.skill_scripts(), (
        "refresh._measure_scripts() and dump_manifest.skill_scripts() disagree — "
        "they are supposed to be the same function, called not copied")
    src = open(os.path.join(HERE, "refresh.py"), encoding="utf-8").read()
    assert "MEASURE_SKILL_HOME" not in src, (
        "refresh.py has grown its own copy of the skill locator again; call "
        "dump_manifest.skill_scripts() instead")


def t_the_seam_resolves_everything_it_claims():
    sys.path.insert(0, HERE)
    import game_paths
    missing = [n for n in game_paths.__all__
               if n.isupper() and not os.path.exists(getattr(game_paths, n))]
    # Not a failure on a machine without the game — but it must be SAID.
    if missing:
        print("      note: not present on this machine: %s" % ", ".join(missing))


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.startswith("t_"):
            case(k[2:], v)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
