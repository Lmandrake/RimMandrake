"""Acceptance test for RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START.

Runs every live command of the Pyrelands test table exactly as judge_certificate.red_seen does (shell=True, repo root,
no game needed) for a few seconds, and fails when any dies before its test can run: a shell syntax error, an import
error, or a missing file. A command that reaches the bridge (and is refused there, game down) counts as started.
Exit 0 = every command starts; 1 = at least one never starts (the count is printed)."""
import json, os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 7))
T = json.load(open(os.path.join(ROOT, "design/concepts/Pyrelands/version/test_table.json")))["tests"]
DEAD = ("Syntax error", "ModuleNotFoundError", "No such file", "can't open file", "not found")
bad = []
for k, t in sorted(T.items()):
    if not str(t.get("kind", "")).startswith("live") or not t.get("command"):
        continue
    try:
        r = subprocess.run(t["command"], shell=True, cwd=ROOT, capture_output=True, text=True, timeout=20)
        err = (r.stderr or "") + (r.stdout or "")
    except subprocess.TimeoutExpired:
        continue                        # still running after 20 s: it started
    if any(d in err for d in DEAD):
        bad.append((k, err.strip().splitlines()[-1][:120] if err.strip() else "rc %s" % r.returncode))
print("%d live command(s) never start" % len(bad))
for k, why in bad[:8]:
    print("  %s: %s" % (k, why))
sys.exit(1 if bad else 0)
