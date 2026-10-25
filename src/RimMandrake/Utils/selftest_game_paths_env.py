#!/usr/bin/env python3
r"""Selftest: game_paths.py honours the per-machine env vars (GAME_PATHS_REWIRE_ONE_ENV_PER_MACHINE).

SteveDesktop's RimWorld lives on D:\SteamLibrary under Windows user sjlewis and its test runs use
their own -savedatafolder. Without the overrides every tool there resolves Archmagi's C:\ paths and
fails by naming a missing file. Each case imports game_paths in a fresh interpreter, because the
module resolves at import time.

    python3 src/RimMandrake/Utils/selftest_game_paths_env.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PASS, FAIL = [], []


def probe(env):
    e = {k: v for k, v in os.environ.items() if not k.startswith("RM_GAME_") and k != "RM_STEAMAPPS"}
    e.update(env)
    code = ("import json, game_paths as g; print(json.dumps({k: getattr(g, k) for k in "
            "('STEAM', 'GAME_DIR', 'LOCAL_MODS', 'MODS_CONFIG', 'SAVES', 'PLAYER_LOG', 'PREV_LOG', 'DUMP_ROOT')}))")
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=e, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as ex:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, ex))


def no_env_is_archmagi():
    d = probe({})
    assert "Program Files (x86)" in d["STEAM"], d["STEAM"]
    assert "Mandrake" in d["MODS_CONFIG"], d["MODS_CONFIG"]


def steamapps_win_form():
    d = probe({"RM_STEAMAPPS": r"Q:\NoSuchLib\steamapps"})
    for k in ("STEAM", "GAME_DIR", "LOCAL_MODS"):
        assert "NoSuchLib" in d[k], (k, d[k])
    assert "Program Files" not in d["GAME_DIR"], d["GAME_DIR"]


def userdata_moves_config_not_log():
    d = probe({"RM_GAME_USERDATA": "/mnt/q/rmtest/userdata"})
    for k in ("MODS_CONFIG", "SAVES", "DUMP_ROOT"):
        assert "rmtest" in d[k], (k, d[k])
    # Unity writes Player.log to the Windows user's LocalLow regardless of -savedatafolder.
    assert "rmtest" not in d["PLAYER_LOG"] and "rmtest" not in d["PREV_LOG"], d["PLAYER_LOG"]


def logdir_moves_log():
    d = probe({"RM_GAME_LOGDIR": r"Q:\Users\sjlewis\rwlogs"})
    assert "sjlewis" in d["PLAYER_LOG"] and "sjlewis" in d["PREV_LOG"], d["PLAYER_LOG"]
    assert "sjlewis" not in d["MODS_CONFIG"], d["MODS_CONFIG"]


def path_forms_round_trip():
    sys.path.insert(0, HERE)
    import game_paths as g
    assert g.win_to_wsl(r"D:\SteamLibrary\steamapps") == "/mnt/d/SteamLibrary/steamapps"
    assert g.wsl_to_win("/mnt/d/SteamLibrary/steamapps") == r"D:\SteamLibrary\steamapps"
    assert g.wsl_to_win("/mnt/d") == "D:\\"
    assert g.win_to_wsl("/already/posix") == "/already/posix"
    assert g.wsl_to_win("/home/x") == "/home/x"


for n, f in [("no env -> Archmagi literals", no_env_is_archmagi),
             ("RM_STEAMAPPS (Windows form) moves Steam, game dir, Mods", steamapps_win_form),
             ("RM_GAME_USERDATA (WSL form) moves Config/Saves/DefDump, not Player.log", userdata_moves_config_not_log),
             ("RM_GAME_LOGDIR moves Player.log + prev only", logdir_moves_log),
             ("win_to_wsl / wsl_to_win", path_forms_round_trip)]:
    case(n, f)
print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
sys.exit(1 if FAIL else 0)
