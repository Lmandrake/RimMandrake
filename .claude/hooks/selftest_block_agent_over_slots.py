#!/usr/bin/env python3
"""selftest for block_agent_over_slots.py (SLOT_CAP_ENFORCE_HOOK_REFUSES_OVER_N).

Runs the hook as Claude Code does (JSON on stdin) against fixture transcripts, a fixture allocation.json and a fixture
meter under a temp dir. No real transcript or allocation is read.

    python3 .claude/hooks/selftest_block_agent_over_slots.py
    HOOK=<path> python3 ...   run against another hook file (a no-op stub shows the red-before)
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HOOK = Path(os.environ.get("HOOK") or HERE / "block_agent_over_slots.py")
sys.path.insert(0, str(ROOT / "src" / "RimMandrake" / "Utils"))
import slot_allocator as SA  # noqa: E402

FAILS = []
H = 3600.0


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        FAILS.append(name)


now = time.time()
tmp = Path(tempfile.mkdtemp(prefix="slothook_"))
projects = tmp / "projects"
sub = projects / "-home-mandrake-rm-bench" / "s1" / "subagents"
sub.mkdir(parents=True)
(projects / "-home-mandrake-rm-foundry").mkdir()
A = lambda stop: {"type": "assistant", "timestamp": SA.iso_z(now - 600),  # noqa: E731
                  "message": {"role": "assistant", "stop_reason": stop, "content": [{"type": "text", "text": "x"}]}}
U = {"type": "user", "timestamp": SA.iso_z(now - 700), "message": {"role": "user", "content": "go"}}
for name, recs, age in (("run1", [U, A("tool_use")], 20), ("run2", [U, A("tool_use")], 300), ("run3", [U], 100),
                        ("ended", [U, A("end_turn")], 400), ("dead", [U, A("tool_use")], 3000)):
    p = sub / f"agent-{name}.jsonl"
    p.write_text("".join(json.dumps(x) + "\n" for x in recs))
    os.utime(p, (now - age, now - age))
streams = tmp / "streams"
streams.mkdir()
au = tmp / "au"
au.mkdir()
iso = SA.iso_local
(au / "latest.json").write_text(json.dumps({"schema": 1, "updated": iso(now), "accounts": {
    "system": {"account": "system", "machine": "testhost", "source": "MEASURED", "ts": iso(now), "measured_at": iso(now - 60),
               "week_pct_used": 60.0, "week_resets_at": iso(now + 48 * H), "session_pct_used": 18.0,
               "session_resets_at": iso(now + 3 * H)}}}))
(au / "series.jsonl").write_text("")


def alloc(seats, age=60, mode="CRUISE"):
    (streams / "allocation.json").write_text(json.dumps({"t": now - age, "at": iso(now - age), "mode": mode, "seats": seats,
                                                          "why": "fixture why: fits 4.1"}))
    os.utime(streams / "allocation.json", (now - age, now - age))


def run(seat="BENCH", stdin=None, cwd=None):
    env = dict(os.environ, RM_SLOT_PROJECTS=str(projects), RM_STREAMS_DIR=str(streams), RM_ACCOUNT_USAGE_DIR=str(au),
               RM_SLOT_MACHINE="testhost", RM_SLOT_OWNER_LEDGER=str(tmp / "none.jsonl"), AGENT_SEAT=seat,
               CLAUDE_PROJECT_DIR=str(ROOT))
    body = stdin if stdin is not None else json.dumps({"tool_name": "Agent", "cwd": cwd or "/x",
                                                       "tool_input": {"prompt": "p", "model": "sonnet"}})
    p = subprocess.run([sys.executable, str(HOOK)], input=body, env=env, capture_output=True, text=True, timeout=60)
    try:
        out = json.loads(p.stdout) if p.stdout.strip() else {}
    except ValueError:
        out = {"_raw": p.stdout}
    h = out.get("hookSpecificOutput") or {}
    return p.returncode, h.get("permissionDecision"), h.get("permissionDecisionReason") or ""


alloc({"BENCH": 3, "FOUNDRY": 1})
rc, dec, why = run()
check("3 running (one between calls, one not yet answered) against N=3 -> deny", dec == "deny", (rc, dec, why[:200]))
check("the refusal names N, the mode and the why", "N=3" in why and "CRUISE" in why and "fits 4.1" in why, why[:400])
check("the refusal points at the override flag and says not to cancel",
      "--owner-said" in why and "slot_allocator.py set --seat BENCH" in why and "Do not cancel" in why, why[:600])
alloc({"BENCH": 4, "FOUNDRY": 1})
rc, dec, why = run()
check("3 running against N=4 -> allow", dec is None and rc == 0, (dec, why[:200]))
alloc({"BENCH": 3, "FOUNDRY": 1})
rc, dec, why = run("FOUNDRY")
check("FOUNDRY counts its own seat: 0 running against N=1 -> allow", dec is None, (dec, why[:200]))
alloc({"BENCH": 3, "FOUNDRY": 0})
rc, dec, why = run("FOUNDRY")
check("FOUNDRY N=0 (ALMOST_OUT) refuses even the first helper", dec == "deny" and "N=0" in why, (dec, why[:200]))
alloc({"BENCH": 3, "FOUNDRY": 1})
rc, dec, why = run("STEVE")
check("a seat outside enforce_seats is not gated", dec is None, dec)
rc, dec, why = run("", cwd="/home/mandrake/rm/bench")
check("no AGENT_SEAT: the seat comes from the cwd (rm/bench -> BENCH, denied)", dec == "deny", (dec, why[:200]))
rc, dec, why = run(stdin="not json")
check("broken input fails open", rc == 0 and dec is None, (rc, dec))
alloc({"BENCH": 3, "FOUNDRY": 1}, age=3 * H)
rc, dec, why = run()
check("a stale allocation.json is recomputed live (CRUISE 6 total -> BENCH 5, 3 running -> allow)",
      dec is None, (dec, why[:300]))
alloc({"BENCH": 3, "FOUNDRY": 1})
time.sleep(0.05)
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "run nine", "until": iso(now + H), "n": 9}))
rc, dec, why = run()
check("his word newer than the allocation is honoured at once (N 9 -> allow)", dec is None, (dec, why[:300]))
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "just two", "until": iso(now + H), "n": 2}))
rc, dec, why = run()
check("his word can lower it too (N 2 -> deny, quoting him)", dec == "deny" and "just two" in why, (dec, why[:300]))

print(f"\n{'GREEN' if not FAILS else 'RED'}: {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
