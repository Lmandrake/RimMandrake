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
                        ("ended", [U, A("end_turn")], 400), ("justended", [U, A("end_turn")], 10), ("dead", [U, A("tool_use")], 3000)):
    p = sub / f"agent-{name}.jsonl"
    p.write_text("".join(json.dumps(x) + "\n" for x in recs))
    os.utime(p, (now - age, now - age))
streams = tmp / "streams"
streams.mkdir()
disp = tmp / "dispatcher"
disp.mkdir()
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


def run(seat="BENCH", stdin=None, cwd=None, session=False):
    env = dict(os.environ, RM_SLOT_PROJECTS=str(projects), RM_STREAMS_DIR=str(streams), RM_ACCOUNT_USAGE_DIR=str(au),
               RM_SLOT_MACHINE="testhost", RM_SLOT_OWNER_LEDGER=str(tmp / "none.jsonl"), AGENT_SEAT=seat,
               RM_DISPATCHER_STATE=str(disp),
               CLAUDE_PROJECT_DIR=str(ROOT))
    env.pop("RM_ROLE_UNIT", None)
    if not session:
        env["RM_ROLE_UNIT"] = "rm-role-fixture"   # a Dispatcher role launch; session=True is the owner's own window
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
      "--owner-said" in why and "slot_allocator.py set --seat CONDUCTOR" in why and "Do not cancel" in why, why[:600])
# ---- the Conductor window's open policy: unlimited only within conductor_window.open_min of his last typed message
def transcript(name, minutes_ago, origin="human", extra=()):
    p = tmp / f"{name}.jsonl"
    recs = [{"type": "user", "timestamp": SA.iso_z(now - minutes_ago * 60), "origin": {"kind": origin},
             "message": {"role": "user", "content": "please"}}] + list(extra)
    p.write_text("".join(json.dumps(x) + "\n" for x in recs))
    return str(p)


def sess_run(tp):
    body = json.dumps({"tool_name": "Agent", "cwd": "/x", "transcript_path": tp,
                       "tool_input": {"prompt": "p", "model": "sonnet"}})
    return run(session=True, stdin=body)


rc, dec, why = sess_run(transcript("t5", 5))
check("owner typed 5 min ago: no limit, 3 running against N=3 -> allow (ruling 2026-10-29)", dec is None, (dec, why[:200]))
rc, dec, why = sess_run(transcript("t19", 19))
check("owner typed 19 min ago: still open -> allow", dec is None, (dec, why[:200]))
rc, dec, why = sess_run(transcript("t25", 25))
check("owner typed 25 min ago: capped at 2, 3 running -> deny, N=2", dec == "deny" and "N=2" in why, (dec, why[:300]))
rc, dec, why = sess_run(transcript("t90", 90))
check("... the cap names the lapsed open policy", dec == "deny" and "open policy lapsed" in why, why[:300])
ring = tmp / "ring.jsonl"
ring.write_text(json.dumps({"type": "user", "timestamp": SA.iso_z(now - 60), "origin": {"kind": "task-notification"},
                            "message": {"role": "user", "content": "[RimFlow ring]"}}) + "\n"
                + json.dumps({"type": "user", "timestamp": SA.iso_z(now - 30 * 60), "origin": {"kind": "human"},
                              "message": {"role": "user", "content": "old"}}) + "\n")
rc, dec, why = sess_run(str(ring))
check("a fresh ring/task-notification is not the owner typing: 30 min since he did -> capped", dec == "deny", (dec, why[:200]))
rc, dec, why = sess_run(str(tmp / "nonexistent.jsonl"))
check("unreadable transcript -> capped at 2 (fail closed)", dec == "deny" and "N=2" in why, (dec, why[:200]))
rc, dec, why = run(session=True)
check("no transcript_path in the payload -> capped (fail closed)", dec == "deny", (dec, why[:200]))
alloc({"BENCH": 3, "FOUNDRY": 0})
rc, dec, why = run("FOUNDRY", session=True)
check("... the exemption is the Conductor window only: FOUNDRY (N=0) is still gated", dec == "deny", (dec, why[:200]))
alloc({"BENCH": 3, "FOUNDRY": 1})
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
check("a stale allocation.json is recomputed live (v3: he is absent -> CONDUCTOR 0, 3 running -> deny)",
      dec == "deny" and "N=0" in why and "computed now" in why, (dec, why[:300]))
rc, dec, why = run("FOUNDRY")
check("... and FOUNDRY, computed live, gets the machine total (CRUISE 6 -> allow)", dec is None, (dec, why[:300]))
alloc({"BENCH": 3, "FOUNDRY": 1})
time.sleep(0.05)
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "run nine", "until": iso(now + H), "n": 9}))
rc, dec, why = run()
check("his word newer than the allocation is honoured at once (N 9 -> allow)", dec is None, (dec, why[:300]))
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "just two", "until": iso(now + H), "n": 2}))
rc, dec, why = run()
check("his word can lower it too (N 2 -> deny, quoting him)", dec == "deny" and "just two" in why, (dec, why[:300]))

# ---- v3: the Dispatcher's published budget comes first (HELPER_BUDGET_MIGRATE_INTO_DISPATCHER)
(streams / "slot_override.json").unlink()
alloc({"BENCH": 3, "FOUNDRY": 1})


def budget(seats, age=30):
    (disp / "helper_budget.json").write_text(json.dumps({"t": now - age, "at": iso(now - age), "by": "dispatcher",
                                                         "seats": seats, "mode": "CRUISE", "why": "budget why: v3"}))


budget({"CONDUCTOR": 5, "FOUNDRY": 0})
rc, dec, why = run()
check("a fresh Dispatcher budget beats allocation.json (CONDUCTOR 5, 3 running -> allow)", dec is None, (dec, why[:300]))
rc, dec, why = run("FOUNDRY")
check("FOUNDRY reads its budget under its own name (FOUNDRY 0 -> deny, citing the Dispatcher)",
      dec == "deny" and "N=0" in why and "Dispatcher budget" in why and "budget why" in why, (dec, why[:300]))
budget({"CONDUCTOR": 2, "FOUNDRY": 4})
rc, dec, why = run()
check("the window seat BENCH reads the CONDUCTOR budget and is refused under the Conductor's name",
      dec == "deny" and "N=2" in why and "CONDUCTOR" in why, (dec, why[:300]))
budget({"CONDUCTOR": 9, "FOUNDRY": 4}, age=3 * H)
rc, dec, why = run()
check("a stale Dispatcher budget is ignored (falls back to allocation.json N=3 -> deny)",
      dec == "deny" and "allocation.json" in why, (dec, why[:300]))
budget({"CONDUCTOR": 9, "FOUNDRY": 4})
time.sleep(0.05)
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "just one", "until": iso(now + H), "n": 1}))
rc, dec, why = run()
check("his word newer than the budget still acts at once (N 1 -> deny, quoting him)",
      dec == "deny" and "just one" in why, (dec, why[:300]))
(disp / "helper_budget.json").write_text("{torn")
(streams / "slot_override.json").unlink()
rc, dec, why = run()
check("a torn budget file falls back, never fails the spawn open by accident (allocation.json N=3 -> deny)",
      dec == "deny" and "allocation.json" in why, (dec, why[:300]))

ids = sorted(x["id"] for x in SA.running_helpers([projects / "-home-mandrake-rm-bench"], now, SA.load_rules()))
check("a helper whose last record is an end_turn report is finished at once, not counted for minutes",
      "justended" not in ids and "ended" not in ids and ids == ["run1", "run2", "run3"], ids)

print(f"\n{'GREEN' if not FAILS else 'RED'}: {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
