#!/usr/bin/env python3
"""selftest_modset_swap_books_per_game.py -- each game keeps its own swap marker and before-copy.

Found 2026-11-24 (item RIMMANDRAKE_STAGE_SLACK_WALK_SMALL_LIST_ARCHSMALL_NO_FULL_LIST): a swap marker written on one
game (ArchBig, 2026-11-12) sat in the clone's one deployed/config folder and refused a swap on ArchSmall twelve days
later ("the live ModsConfig is neither its tier list nor its before-copy"), because ArchSmall's ModsConfig is another
file. What must hold: modset_builder.BACKUPS for game a stays deployed/config (old markers keep working), and for any
other game it is a folder of its own under it, named by the game.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FAILS = []


def ok(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def backups(inst):
    env = dict(os.environ)
    env.pop("RM_GAME_INSTANCE", None)
    if inst:
        env["RM_GAME_INSTANCE"] = inst
    r = subprocess.run([sys.executable, "-c", "import modset_builder as M; print(M.BACKUPS)"], cwd=HERE, env=env,
                       capture_output=True, text=True, timeout=120)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "ERR " + r.stderr[-300:]


base = os.path.join(REPO, "deployed", "config")
a = backups(None)
a2 = backups("a")
b = backups("b")
ok(os.path.normpath(a) == os.path.normpath(base), "game a keeps deployed/config (%s)" % a)
ok(os.path.normpath(a2) == os.path.normpath(base), "RM_GAME_INSTANCE=a keeps deployed/config (%s)" % a2)
ok(os.path.normpath(b) != os.path.normpath(base), "game b does not share game a's swap books (%s)" % b)
ok(os.path.normpath(os.path.dirname(b)) == os.path.normpath(base), "game b's books sit under deployed/config (%s)" % b)

print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
