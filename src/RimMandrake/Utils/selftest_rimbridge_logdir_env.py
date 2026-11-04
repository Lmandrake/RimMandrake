#!/usr/bin/env python3
r"""Selftest: rimbridge_client honours RM_GAME_LOGDIR (RIMBRIDGE_LOGDIR_FIX_ENV_VAR_IGNORED).

With RM_GAME_LOGDIR set, DEFAULT_PLAYER_LOG is game_paths.PLAYER_LOG under that folder and is the only
candidate (no glob over /mnt/c/Users/*), and discover_from_log() reads the token from it. Unset, the old
default stands. Each case imports the client in a fresh interpreter: both modules resolve at import.

    python3 src/RimMandrake/Utils/selftest_rimbridge_logdir_env.py
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PASS, FAIL = [], []
CODE = ("import json, rimbridge_client as rb; print(json.dumps({'log': rb.DEFAULT_PLAYER_LOG, "
        "'cands': list(rb._player_log_candidates()), 'disc': rb.discover_from_log()}))")


def probe(env):
    e = {k: v for k, v in os.environ.items()
         if not k.startswith("RM_GAME_") and k not in ("RM_STEAMAPPS", "GABP_TOKEN")}
    e.update(env)
    r = subprocess.run([sys.executable, "-c", CODE], cwd=HERE, env=e, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    return json.loads(r.stdout)


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as ex:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, ex))


def env_logdir_is_used():
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "Player.log"), "w") as fh:
            fh.write("[RimBridge] old on port 1111\n[RimBridge] Bridge token: deadbeef\n"
                     "[RimBridge] listening on port 5199\n[RimBridge] Bridge token: cafe1234\n")
        out = probe({"RM_GAME_LOGDIR": d})
        assert out["log"] == os.path.join(d, "Player.log"), out["log"]
        assert out["cands"] == [out["log"]], out["cands"]
        assert out["disc"][2] == "cafe1234", out["disc"]


def env_logdir_missing_log_finds_nothing():
    with tempfile.TemporaryDirectory() as d:
        out = probe({"RM_GAME_LOGDIR": d})
        assert out["cands"] == [os.path.join(d, "Player.log")], out["cands"]
        assert out["disc"][2] is None, out["disc"]


def unset_keeps_default():
    out = probe({})
    assert out["log"].endswith(os.path.join("RimWorld by Ludeon Studios", "Player.log")), out["log"]
    assert "AppData" in out["log"], out["log"]


case("RM_GAME_LOGDIR names the only Player.log and its newest token is read", env_logdir_is_used)
case("RM_GAME_LOGDIR with no log there: no fallback to another user's log", env_logdir_missing_log_finds_nothing)
case("unset: default Player.log unchanged", unset_keeps_default)
print("%d passed, %d failed" % (len(PASS), len(FAIL)))
sys.exit(1 if FAIL else 0)
