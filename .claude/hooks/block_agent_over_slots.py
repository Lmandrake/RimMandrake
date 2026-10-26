#!/usr/bin/env python3
"""PreToolUse/Agent hook: refuse a spawn when this seat already runs its allocated N helpers (SLOT_CAP_ENFORCE_HOOK_REFUSES_OVER_N).

Owner, 2026-10-26: "Let's drop to 5 max subagents for Bench at a time (complete all current work entirely, don't
cancel) to preserve. We should make this a semi-automated process going forward, so I don't have to stare at it and
guess." Then at 13:05: "...please use it to determine the number of Foundry and Bench agents yourself. My 5 was a guess."

So N is not fixed here. It is the allocator's per-seat N (src/RimMandrake/Utils/slot_allocator.py, rules in
slot_rules.json), read from allocation.json when that is under 40 min old and newer than his last word, computed
live otherwise, and the rules file's fallback_n if neither works. Running helpers are counted from this seat's
subagent transcripts (slot_allocator.running_helpers: written in the last 15 min and not cleanly ended; when in doubt
a helper counts as running). Nothing here cancels a helper: the refusal only says to wait.

Fails open: a broken guard must not stop all spawning.

    python3 .claude/hooks/selftest_block_agent_over_slots.py
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
UTILS = ROOT / "src" / "RimMandrake" / "Utils"
FRESH_S = 40 * 60


def seat_of(payload):
    s = (os.environ.get("AGENT_SEAT") or "").strip().upper()
    if s:
        return s
    cwd = str(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).rstrip("/")
    for name in ("bench", "foundry"):
        if cwd.endswith("/rm/" + name) or ("/rm/" + name + "/") in cwd:
            return name.upper()
    return ""


def allowed_n(SA, rules, seat, now):
    """(N, mode, why, source) for this seat."""
    d = SA.streams_dir()
    al = SA.read_json(d / "allocation.json")
    try:
        ov_m = os.path.getmtime(d / "slot_override.json")
    except OSError:
        ov_m = 0
    if isinstance(al, dict) and now - float(al.get("t") or 0) < FRESH_S and ov_m <= float(al.get("t") or 0) \
            and seat in (al.get("seats") or {}):
        return int(al["seats"][seat]), al.get("mode"), al.get("why", ""), f"allocation.json of {al.get('at')}"
    try:
        dec = SA.compute(now, rules, seat)
        return int(dec["seats"][seat]), dec["mode"], dec["why"], "computed now"
    except Exception as e:  # noqa: BLE001
        fb = rules.get("fallback_n") or {}
        if seat in fb:
            return int(fb[seat]), "FALLBACK", f"allocator failed ({type(e).__name__}); rules fallback_n", "fallback"
        raise


def decide(payload, now=None):
    """None to allow, or the refusal text."""
    now = now or time.time()
    seat = seat_of(payload)
    if str(UTILS) not in sys.path:
        sys.path.insert(0, str(UTILS))
    import slot_allocator as SA
    rules = SA.load_rules(os.environ.get("RM_SLOT_RULES") or UTILS / "slot_rules.json")
    if seat not in (rules.get("enforce_seats") or []) or seat not in SA.SEAT_PROJECT:
        return None
    n, mode, why, src = allowed_n(SA, rules, seat, now)
    running = SA.running_helpers([SA.projects_dir() / SA.SEAT_PROJECT[seat]], now, rules)
    if len(running) < n:
        return None
    ids = ", ".join(x["id"][:10] for x in running[:8])
    return (
        f"Blocked: {seat} already has {len(running)} helper(s) running and the allocator allows N={n} now "
        f"(mode {mode}, {src}).\n\nWhy N={n}: {why}\n\nRunning: {ids}\n\n"
        "Do not cancel a running helper to make room. Wait for one to finish, then spawn. The allocator re-checks every "
        "15 min (RimPulse, rm-pulse-streams.timer); `python3 src/RimMandrake/Utils/slot_allocator.py now` shows it.\n"
        "Only the owner's word raises N (the override flag):\n"
        f"    python3 src/RimMandrake/Utils/slot_allocator.py set --seat {seat} --n <N> --owner-said \"<his exact words>\"\n"
        "(it holds until the burn account's weekly reset; `slot_allocator.py clear` drops it)."
    )


def main():
    try:
        payload = json.load(sys.stdin)
        reason = decide(payload if isinstance(payload, dict) else {})
    except Exception:
        return 0
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
