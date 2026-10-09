#!/usr/bin/env python3
"""Selftest for the pulse spine's red / amber / calm classification (AWAY_DASHBOARD_BUILD_1).

Fixture session files and events only; touches no live state (RM_PULSE_STATE -> a tempdir).
Each rule is checked BOTH ways so a classifier that answers one colour everywhere fails.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ["RM_PULSE_STATE"] = tempfile.mkdtemp(prefix="pulse_selftest_")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pulse_core as pc  # noqa: E402

NOW = 1_791_500_000.0
FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


def sess(sid, name, status, upd_ago, alive=True, waiting_for=None):
    s = {"sessionId": sid, "pid": 1, "name": f"AGENT {name}", "status": status, "kind": "interactive",
         "statusUpdatedAt": (NOW - upd_ago) * 1000, "alive": alive, "_file": f"/home/x/.claude/sessions/{sid}.json"}
    if waiting_for:
        s["waitingFor"] = waiting_for
    return s


def kinds(rows):
    return {r["who"]: r["kind"] for r in rows}


# --- sessions: amber rules (owner ruling 2026-10-08) ----------------------------------
sessions = [
    sess("a", "BENCH", "waiting", 300, waiting_for="input needed"),
    sess("b", "FOUNDRY", "idle", 300),
    sess("c", "HESTIA", "idle", 300),
    sess("d", "EMERGENCY", "idle", 20),
    sess("e", "BUSY", "busy", 30),
    sess("f", "HUNG", "busy", 3000),
]
extras = {"a": {"subagents": 3, "question": "Which herd size?"}, "b": {"subagents": 0},
          "c": {"subagents": 2}, "d": {"subagents": 0}, "e": {"subagents": 1, "transcript_mtime": NOW - 10},
          "f": {"subagents": 0, "transcript_mtime": NOW - 3000}}
rows, seen, ev = pc.classify_sessions(sessions, extras, {}, {}, {}, NOW)
k = kinds(rows)
check("explicit question is amber even while subagents run", k.get("BENCH") == "amber", k)
check("question text from the pending AskUserQuestion is shown",
      any("Which herd size?" in r["text"] for r in rows if r["who"] == "BENCH"))
check("finished-and-idle with no subagents is soft amber", k.get("FOUNDRY") == "amber_soft", k)
check("finished-and-idle WITH subagents still working is NOT amber", k.get("HESTIA") == "run", k)
check("idle for under 60 s is not amber yet", k.get("EMERGENCY") == "idle", k)
check("busy with recent progress is calm run", k.get("BUSY") == "run", k)
check("busy with no progress for 50 min is dim 'stuck', not amber", k.get("HUNG") == "stuck", k)
check("live sessions are remembered as seen", set(seen) == set("abcdef"), seen.keys())

# --- sessions: red (window lost) vs neutral (clean exit) -----------------------------
seen_before = {"g": {"name": "LOST", "last_alive": NOW - 40}, "h": {"name": "EXITED", "last_alive": NOW - 40}}
rows, seen2, ev = pc.classify_sessions([sess("g", "LOST", "busy", 60, alive=False),
                                        sess("z", "RESIDUE", "busy", 99999, alive=False)],
                                       {}, seen_before, {}, {}, NOW)
k = kinds(rows)
check("a watched window whose process died is red", k.get("LOST") == "red", k)
check("an old dead file never seen alive is ignored (no false red at first start)", "RESIDUE" not in k, k)
check("a removed session file is a clean exit, not red",
      "EXITED" not in k and any(e["m"] == "session_ended_clean" for e in ev), (k, ev))
inc = next(r["incident"] for r in rows if r["who"] == "LOST")
rows, _, _ = pc.classify_sessions([sess("g", "LOST", "busy", 60, alive=False)], {}, seen_before, {},
                                  {inc: {"at": NOW}}, NOW)
check("an acked lost window stays visible but stops alarming", rows and rows[0]["acked"], rows)

# --- OOM kills -----------------------------------------------------------------------
def ts(ago):
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(NOW - ago))

mem = [{"ts": ts(90000), "kind": "oom_kill", "cgroup": "rm-harness.slice", "delta": 1},
       {"ts": ts(600), "kind": "oom_kill", "cgroup": "rm-harness.slice", "delta": 1, "snapshot": {"current_gb": 6.0}},
       {"ts": ts(300), "kind": "oom_kill", "cgroup": "rm-harness.slice", "delta": 1},
       {"ts": ts(200), "kind": "max", "cgroup": "claude-seats.slice/claude-seat-BENCH-1.scope", "delta": 40},
       {"ts": ts(100), "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-1.scope",
        "seat": "BENCH", "delta": 1, "toast": True},
       {"ts": ts(100), "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-1.scope/claude-code-bash",
        "seat": "BENCH", "delta": 1, "toast": True}]
reds = pc.classify_oom(mem, {}, NOW)
by = {r["who"]: r for r in reds}
check("harness OOM kills alarm red (memwatch never toasts them)", by.get("HARNESS", {}).get("kind") == "red", reds)
check("harness burst is ONE line counting the 24 h kills only",
      len([r for r in reds if r["who"] == "HARNESS"]) == 1 and by["HARNESS"]["count"] == 2, by.get("HARNESS"))
check("a seat kill and its tool child are one incident", len([r for r in reds if r["who"] == "BENCH"]) == 1, reds)
check("memory 'max' ticks are not red", len(reds) == 2, reds)
check("seat kill already toasted by memwatch is not toasted twice", by["BENCH"]["toasted_elsewhere"] is True)
check("harness kill is toasted by the widget", by["HARNESS"]["toasted_elsewhere"] is False)
acked = pc.classify_oom(mem, {"oom:rm-harness.slice": {"at": NOW - 450}}, NOW)
acked2 = pc.classify_oom(mem, {"oom:rm-harness.slice": {"at": NOW - 250}}, NOW)
check("ack after the last kill silences it", next(r for r in acked2 if r["who"] == "HARNESS")["acked"] is True)
check("a NEW kill after the ack re-raises it", next(r for r in acked if r["who"] == "HARNESS")["acked"] is False)

# --- subagent running signal ---------------------------------------------------------
end = {"type": "assistant", "message": {"stop_reason": "end_turn"}}
mid = {"type": "user", "message": {"content": [{"type": "tool_result"}]}}
check("subagent whose last record is end_turn is finished", not pc.subagent_running(end, NOW - 5, NOW))
check("subagent mid-tool and recent is running", pc.subagent_running(mid, NOW - 5, NOW))
check("subagent silent past the watchdog is not running", not pc.subagent_running(mid, NOW - 3600, NOW))

# --- session file reader: liveness via procStart (PID reuse) -------------------------
with tempfile.TemporaryDirectory() as d:
    me = os.getpid()
    good = pc.proc_start(me)
    for name, ps in (("live", good), ("reused", "1")):
        Path(d, f"{name}.json").write_text(json.dumps({"pid": me, "procStart": ps, "sessionId": name,
                                                       "kind": "interactive", "status": "busy"}))
    Path(d, "printmode.json").write_text(json.dumps({"pid": me, "procStart": good, "sessionId": "p", "kind": "print"}))
    got = {s["sessionId"]: s["alive"] for s in pc.read_sessions(Path(d))}
    check("pid alive with matching procStart reads alive", got.get("live") is True, got)
    check("pid alive with a different procStart (PID reuse) reads dead", got.get("reused") is False, got)
    check("non-interactive (claude -p) sessions are ignored", "p" not in got, got)

# --- ledger: done rows with typed links, review rows ---------------------------------
def le(ev, iid, ago, **kw):
    return {"event": ev, "id": iid, "seat": "FOUNDRY", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW - ago)),
            "tsn": int((NOW - ago) * 1e9), **kw}

ledger = [le("file", "X_ONE_1", 5000, title="Do the thing"), le("start", "X_ONE_1", 4000),
          le("verify", "X_ONE_1", 3000, result="pass", criterion="A1", evidence="Transient/modcheck/x.json", sha="abc123def"),
          le("implemented", "X_ONE_1", 2000, sha="ff172269a0"),
          le("needs", "R_TWO_1", 1000, to="OWNER", reason="sheet ready"),
          le("needs", "R_THREE_1", 1000, to="OWNER", reason="sheet ready"), le("close", "R_THREE_1", 500, sha="1"),
          le("file", "OLD_1", 90000, title="old")]
lrows, counts = pc.classify_ledger(ledger, NOW - 12 * 3600, NOW)
lk = {r["key"]: r for r in lrows}
check("one line per thing: verify then implemented collapse to one done row",
      lk.get("item:X_ONE_1", {}).get("kind") == "done" and "implemented" in lk["item:X_ONE_1"]["text"], lk.get("item:X_ONE_1"))
check("commit links are GitHub URLs", (lk["item:X_ONE_1"]["link"] or {}).get("value", "").startswith(pc.GITHUB_COMMIT))
check("evidence paths become native Windows paths",
      pc.link_for(ledger[2])["value"] == "D:\\Luke\\dev\\RimMandrake\\Transient\\modcheck\\x.json", pc.link_for(ledger[2]))
check("needs->OWNER is a calm review row", lk.get("needs:R_TWO_1", {}).get("kind") == "review", lk.keys())
check("a closed review item drops off", "needs:R_THREE_1" not in lk, lk.keys())
check("counts cover only the window", counts["filed"] == 1, counts)
check("current item per seat comes from start without close",
      pc.current_items(ledger[:2], NOW) == {"FOUNDRY": "X_ONE_1"} and pc.current_items(ledger[:4], NOW) == {})

# --- end to end: snapshot, strip, metric transitions ---------------------------------
raw = {"sessions": sessions, "extras": extras, "memwatch": mem, "ledger": ledger, "artpipe": {}, "probe": None,
       "bridge": None}
snap, st, ev = pc.collect_snapshot(raw, {}, NOW)
check("rows are ordered red first", snap["rows"][0]["kind"] == "red", [r["kind"] for r in snap["rows"][:3]])
check("strip carries red and amber pills", {"red", "amber", "amber_soft"} <= {p["kind"] for p in snap["strip"]}, snap["strip"])
check("alarm_open events are logged for metrics", sum(1 for e in ev if e["m"] == "alarm_open") >= 3, ev)
sessions2 = [s if s["sessionId"] != "a" else sess("a", "BENCH", "busy", 1) for s in sessions]
snap2, st2, ev2 = pc.collect_snapshot({**raw, "sessions": sessions2}, st, NOW + 60)
qa = [e for e in ev2 if e["m"] == "alarm_close" and e["kind"] == "amber"]
check("answering the question logs its age (question-age metric)", qa and qa[0]["age_s"] == 360, ev2)

print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failing")
sys.exit(1 if FAILS else 0)
