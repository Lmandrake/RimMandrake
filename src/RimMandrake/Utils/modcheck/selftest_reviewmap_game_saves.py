#!/usr/bin/env python3
"""selftest_reviewmap_game_saves.py -- reviewmap's Saves folder (and its sign sidecar folder) follow the game a process names.

Item RIMMANDRAKE_POINT_REVIEWMAP_AT_GAME_B_SAVES_KEEPER_BLIND. Measured 2026-11-20 10:16 PM PST on game b: save_keeper wrote
GSS_011_VISIT1_WALK_20261120.rws into game b's Saves and reported ok False, new [] -- it had watched game a's Saves
(SAVES was hard-wired to the profile's LocalLow), so its never-overwrite guard read the wrong folder too.

    python3 src/RimMandrake/Utils/modcheck/selftest_reviewmap_game_saves.py      # exit 0 = every case PASS
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
FAILS = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def read(env_extra):
    """-> {SAVES, SIGNS, game} as a fresh process with env_extra imports them."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("RM_GAME_", "GABP_", "RM_INSTANCES_ROOT"))}
    env.update(env_extra)
    code = ("import sys, json; sys.path.insert(0, %r); sys.path.insert(0, %r)\n"
            "import game_paths\nfrom modcheck import reviewmap as R\n"
            "print(json.dumps({'SAVES': R.SAVES, 'SIGNS': R.SIGNS, 'game': game_paths.SAVES}))") % (UTILS, os.path.dirname(UTILS))
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return {"error": r.stderr.strip()[-300:]}
    return json.loads(r.stdout.strip().splitlines()[-1])


def t_saves_follow_the_named_game():
    root = tempfile.mkdtemp(prefix="selftest_reviewmap_game_saves_")
    got = read({"RM_GAME_INSTANCE": "b", "RM_INSTANCES_ROOT": root})
    check("error" not in got, "b: reviewmap imports with game b named (%s)" % got.get("error"))
    saves = (got.get("SAVES") or "").replace("\\", "/")
    check(saves == (got.get("game") or "").replace("\\", "/"), "b: SAVES is game_paths.SAVES (%r vs %r)" % (got.get("SAVES"), got.get("game")))
    check(saves.rstrip("/").endswith("/b/Saves"), "b: SAVES is game b's own Saves folder, never game a's (%r)" % got.get("SAVES"))


def t_signs_sit_beside_the_games_saves():
    root = tempfile.mkdtemp(prefix="selftest_reviewmap_game_saves_")
    got = read({"RM_GAME_INSTANCE": "b", "RM_INSTANCES_ROOT": root})
    check(os.path.dirname((got.get("SIGNS") or "").replace("\\", "/")) == os.path.dirname((got.get("SAVES") or "").replace("\\", "/")),
          "b: the sign sidecar folder sits beside game b's Saves (%r)" % got.get("SIGNS"))


def t_game_a_keeps_its_saves():
    got = read({})
    check("error" not in got and got.get("SAVES") == got.get("game"),
          "a: with no game named SAVES is game a's, as game_paths says (%r vs %r)" % (got.get("SAVES"), got.get("game")))


def main():
    t_saves_follow_the_named_game()
    t_signs_sit_beside_the_games_saves()
    t_game_a_keeps_its_saves()
    print("%d FAIL" % len(FAILS) if FAILS else "all PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
