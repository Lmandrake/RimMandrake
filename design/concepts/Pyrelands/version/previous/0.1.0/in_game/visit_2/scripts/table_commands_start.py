"""Acceptance test for RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START.

Runs every live command of the Pyrelands test table, and every command of in_game/unrun.jsonl, exactly as judge_certificate.red_seen does (shell=True, repo root,
no game needed) for a few seconds, and fails when any dies before its test can run: a shell syntax error, an import
error, or a missing file. A command that reaches the bridge (and is refused there, game down) counts as started.
Exit 0 = every command starts; 1 = at least one never starts (the count is printed).

Every command is pointed at a bridge port where no game listens (GABP_SERVER_PORT, carried to python.exe by WSLENV),
so the test never drives a live game: Windows python passes host_guard.crossing, and game a may be held by another
seat's run (measured 2026-11-21 4:10 AM PST: GimmeSomeSlack's visit held it). "Started" = it got as far as the
bridge and was refused there, or it was still running after 20 s."""
import json, os, subprocess, sys
DEAD_PORT = "5999"                      # no game instance uses it (game_instance.py: a 5174, b 5175)
ENV = dict(os.environ, GABP_SERVER_PORT=DEAD_PORT, RM_GAME_INSTANCE="",
           WSLENV=":".join(x for x in (os.environ.get("WSLENV"), "GABP_SERVER_PORT") if x))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 7))
T = json.load(open(os.path.join(ROOT, "design/concepts/Pyrelands/version/test_table.json")))["tests"]
# the road back's UNRUN rows: the Stage 6 brief tells its driver to run each row's own command (maturation.unrun_lines)
UNRUN = os.path.join(ROOT, "design/concepts/Pyrelands/version/in_game/unrun.jsonl")
for i, line in enumerate(open(UNRUN, encoding="utf-8") if os.path.isfile(UNRUN) else []):
    if line.strip():
        r = json.loads(line)
        T["unrun#%d:%s" % (i, r.get("check"))] = {"kind": "live_unrun", "command": r.get("command")}
DEAD = ("Syntax error", "ModuleNotFoundError", "No such file", "can't open file", "not found")
bad, n = [], 0
for k, t in sorted(T.items()):
    if not str(t.get("kind", "")).startswith("live") or not t.get("command"):
        continue
    n += 1
    try:
        r = subprocess.run(t["command"], shell=True, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=20)
        err = (r.stderr or "") + (r.stdout or "")
    except subprocess.TimeoutExpired:
        continue                        # still running after 20 s: it started
    if any(d in err for d in DEAD):
        bad.append((k, err.strip().splitlines()[-1][:120] if err.strip() else "rc %s" % r.returncode))
print("%d live command(s) never start, of %d run" % (len(bad), n))
for k, why in bad[:8]:
    print("  %s: %s" % (k, why))
sys.exit(1 if bad else 0)
