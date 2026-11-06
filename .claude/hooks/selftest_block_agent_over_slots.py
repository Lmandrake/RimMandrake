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


def run(seat="BENCH", stdin=None, cwd=None, session=False, reserve="0"):
    env = dict(os.environ, RM_SPAWN_RESERVE_S=reserve, RM_SLOT_PROJECTS=str(projects), RM_STREAMS_DIR=str(streams), RM_ACCOUNT_USAGE_DIR=str(au),
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


alloc({"BENCH": 3, "RELENTLESS": 1})
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
alloc({"BENCH": 0, "RELENTLESS": 3})
rc, dec, why = run("BENCH")
check("... the exemption is the Conductor window only: a role run on BENCH (N=0) is still gated",
      dec == "deny" and "N=0" in why, (dec, why[:200]))
alloc({"BENCH": 3, "RELENTLESS": 1})
alloc({"BENCH": 4, "RELENTLESS": 1})
rc, dec, why = run()
check("3 running against N=4 -> allow", dec is None and rc == 0, (dec, why[:200]))
alloc({"BENCH": 3, "RELENTLESS": 0})
rc, dec, why = run("RELENTLESS")
check("the builder key RELENTLESS has no head window (no transcript project), so the hook does not gate it even at "
      "N=0: its places are the supervisor's (relentless_rules staffing)", dec is None and "RELENTLESS" not in SA.SEAT_PROJECT,
      (dec, why[:200]))
alloc({"BENCH": 3, "RELENTLESS": 1})
rc, dec, why = run("STEVE")
check("a seat outside enforce_seats is not gated", dec is None, dec)
rc, dec, why = run("", cwd="/home/mandrake/rm/bench")
check("no AGENT_SEAT: the seat comes from the cwd (rm/bench -> BENCH, denied)", dec == "deny", (dec, why[:200]))
rc, dec, why = run(stdin="not json")
check("broken input fails open", rc == 0 and dec is None, (rc, dec))
alloc({"BENCH": 3, "RELENTLESS": 1}, age=3 * H)
rc, dec, why = run()
check("a stale allocation.json is recomputed live (v3: he is absent -> CONDUCTOR 0, 3 running -> deny)",
      dec == "deny" and "N=0" in why and "computed now" in why, (dec, why[:300]))
alloc({"BENCH": 3, "RELENTLESS": 1})
time.sleep(0.05)
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "run nine", "until": iso(now + H), "n": 9}))
rc, dec, why = run()
check("his word newer than the allocation is honoured at once (N 9 -> allow)", dec is None, (dec, why[:300]))
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "just two", "until": iso(now + H), "n": 2}))
rc, dec, why = run()
check("his word can lower it too (N 2 -> deny, quoting him)", dec == "deny" and "just two" in why, (dec, why[:300]))

# ---- v3: the Dispatcher's published budget comes first (HELPER_BUDGET_MIGRATE_INTO_DISPATCHER)
(streams / "slot_override.json").unlink()
alloc({"BENCH": 3, "RELENTLESS": 1})


def budget(seats, age=30):
    (disp / "helper_budget.json").write_text(json.dumps({"t": now - age, "at": iso(now - age), "by": "dispatcher",
                                                         "seats": seats, "mode": "CRUISE", "why": "budget why: v3"}))


budget({"CONDUCTOR": 5, "RELENTLESS": 0})
rc, dec, why = run()
check("a fresh Dispatcher budget beats allocation.json (CONDUCTOR 5, 3 running -> allow)", dec is None, (dec, why[:300]))
alloc({"BENCH": 3, "RELENTLESS": 1})
budget({"CONDUCTOR": 0, "RELENTLESS": 5})
rc, dec, why = run()
check("BENCH reads its budget under CONDUCTOR, never the builder's RELENTLESS (CONDUCTOR 0 -> deny, citing the Dispatcher)",
      dec == "deny" and "N=0" in why and "Dispatcher budget" in why and "budget why" in why, (dec, why[:300]))
budget({"CONDUCTOR": 2, "RELENTLESS": 4})
rc, dec, why = run()
check("the window seat BENCH reads the CONDUCTOR budget and is refused under the Conductor's name",
      dec == "deny" and "N=2" in why and "CONDUCTOR" in why, (dec, why[:300]))
budget({"CONDUCTOR": 9, "RELENTLESS": 4}, age=3 * H)
rc, dec, why = run()
check("a stale Dispatcher budget is ignored (falls back to allocation.json N=3 -> deny)",
      dec == "deny" and "allocation.json" in why, (dec, why[:300]))
budget({"CONDUCTOR": 9, "RELENTLESS": 4})
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

rc, dec, why = run(session=True)
check("his window with the owner silent stays capped at two (3 running -> deny)",
      dec == "deny" and "CONDUCTOR_WINDOW" in why, (dec, why[:300]))
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "run nine", "until": iso(time.time() + H),
                                                        "seats": {"BENCH": 9}}))
rc, dec, why = run(session=True)
check("his word for BENCH lifts the window cap", dec is None, (dec, why[:300]))
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "run nine", "until": iso(time.time() + H),
                                                        "seats": {"RELENTLESS": 9}}))
rc, dec, why = run(session=True)
check("his word for RELENTLESS alone leaves the window cap on", dec == "deny", (dec, why[:300]))
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "run nine", "until": iso(time.time() - H),
                                                        "seats": {"BENCH": 9}}))
rc, dec, why = run(session=True)
check("a lapsed word no longer lifts it", dec == "deny", (dec, why[:300]))
(streams / "slot_override.json").unlink()

# ---- CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE: a window draining for its restart spawns nothing, the owner's open policy
# included; the drain binds to one session, so no other window and no stale record is touched
state_f = disp / "state.json"
keep_state = state_f.read_text() if state_f.exists() else None
# his word raises N to 9, so a refusal below can only be the drain's
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "run nine", "until": iso(time.time() + H),
                                                        "seats": {"BENCH": 9}}))
body = lambda sid: json.dumps({"tool_name": "Agent", "cwd": "/x", "session_id": sid,
                               "tool_input": {"prompt": "p", "model": "sonnet"}})
state_f.write_text(json.dumps({"seat_restart": {"BENCH": {"state": "pending", "session_id": "sid-drain", "hard": True,
                                                          "reason": "hard context limit: 400000 tokens"}}}))
rc, dec, why = run(stdin=body("sid-drain"), session=True)
check("the draining window is refused, with the reason", dec == "deny" and "draining" in why and "hard context" in why, (dec, why[:300]))
rc, dec, why = run(stdin=body("sid-other"), session=True)
check("another session of the seat is not", dec != "deny", (dec, why[:300]))
state_f.write_text("{torn")
rc, dec, why = run(stdin=body("sid-drain"), session=True)
check("an unreadable state leaves the slot logic standing", dec != "deny", (dec, why[:300]))
(streams / "slot_override.json").unlink()
if keep_state is None:
    state_f.unlink()
else:
    state_f.write_text(keep_state)

# ---- SPAWN_HOOK_FIX_TYPING_BEATS_OWNER_CAP: (a) his explicit N caps the window even while he types
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "just three", "until": iso(time.time() + H),
                                                        "seats": {"BENCH": 3}}))
rc, dec, why = sess_run(transcript("t5b", 5))
check("owner typed 5 min ago but his word says N=3, 3 running -> deny, quoting him",
      dec == "deny" and "N=3" in why and "just three" in why, (dec, why[:300]))
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "run nine", "until": iso(time.time() + H),
                                                        "seats": {"BENCH": 9}}))
rc, dec, why = sess_run(transcript("t5c", 5))
check("... and his larger N while typing still allows (3 < 9)", dec is None, (dec, why[:300]))

# (b) the last slot: concurrent spawns are serialised, the winner's reservation holds the slot
(streams / "slot_override.json").write_text(json.dumps({"ownerSaid": "just four", "until": iso(time.time() + H),
                                                        "seats": {"BENCH": 4}}))
resf = streams / "spawn_reservations.json"
if resf.exists():
    resf.unlink()
rc, dec, why = run(reserve="90")
check("one slot left (3 running, N=4): the first spawn is allowed and reserves", dec is None and resf.exists(), (dec, why[:300]))
rc, dec, why = run(reserve="90")
check("... a second spawn before its transcript appears is refused (the reservation counts)",
      dec == "deny" and "reserved-" in why, (dec, why[:300]))
nt = sub / "agent-newborn.jsonl"
nt.write_text(json.dumps({"type": "user", "timestamp": SA.iso_z(time.time() + 1), "message": {"role": "user", "content": "go"}})
              + "\n" + json.dumps({"type": "assistant", "timestamp": SA.iso_z(time.time() + 1),
                                   "message": {"role": "assistant", "stop_reason": "end_turn",
                                               "content": [{"type": "text", "text": "done"}]}}) + "\n")
rc, dec, why = run(reserve="90")
check("... once the reserved helper's transcript shows (it ended), the reservation is spent: allow",
      dec is None, (dec, why[:300]))
nt.unlink()
resf.unlink(missing_ok=True)
env = dict(os.environ, RM_SPAWN_RESERVE_S="90", RM_SLOT_PROJECTS=str(projects), RM_STREAMS_DIR=str(streams),
           RM_ACCOUNT_USAGE_DIR=str(au), RM_SLOT_MACHINE="testhost", RM_SLOT_OWNER_LEDGER=str(tmp / "none.jsonl"),
           AGENT_SEAT="BENCH", RM_DISPATCHER_STATE=str(disp), CLAUDE_PROJECT_DIR=str(ROOT), RM_ROLE_UNIT="rm-role-fixture")
body = json.dumps({"tool_name": "Agent", "cwd": "/x", "tool_input": {"prompt": "p", "model": "sonnet"}})


def race(hook, n=6):
    """Truly concurrent: every hook gets its stdin (and EOF) before any output is read."""
    resf.unlink(missing_ok=True)
    procs = [subprocess.Popen([sys.executable, str(hook)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env,
                              text=True) for _ in range(n)]
    for p in procs:
        p.stdin.write(body)
        p.stdin.close()
    outs = [p.stdout.read() for p in procs]
    for p in procs:
        p.wait(timeout=60)
    return sum(1 for o in outs if '"deny"' not in o)


# sanity probe: the race instrument can see a race (the 2026-11-06 checker: a sequential version stayed green with
# the flock taken out). Two copies of the hook hold the critical section open 0.6 s (between read and write), so six spawns surely overlap:
# without the flock several must pass; with it exactly one, even though each caller's `now` is read before it waited.
src = HOOK.read_text()
LOCK, CRIT = "fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)", "        if n is not None and len(running) + len(pend) >= n:"
assert LOCK in src and CRIT in src
slow = src.replace(CRIT, "        time.sleep(0.6)  # between reading the reservations and writing ours\n" + CRIT)
wide, nolock = tmp / "hook_wide.py", tmp / "hook_wide_nolock.py"
wide.write_text(slow)
nolock.write_text(slow.replace(LOCK, "pass"))
raw = [race(nolock) for _ in range(3)]
check("sanity: without the flock, concurrent spawns pass the last slot together", min(raw) > 1, raw)
gw = [race(wide) for _ in range(3)]
check("with the flock and a wide critical section, exactly one of six passes each round", all(a == 1 for a in gw), gw)
got = [race(HOOK) for _ in range(8)]
check("six truly concurrent spawns against the last slot (shipped hook), 8 rounds: exactly one passes each round",
      all(a == 1 for a in got), got)
resf.unlink(missing_ok=True)
(streams / "slot_override.json").unlink()

print(f"\n{'GREEN' if not FAILS else 'RED'}: {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
