#!/usr/bin/env python3
"""PreToolUse/Agent hook: refuse a spawn when this seat already runs its allocated N helpers (SLOT_CAP_ENFORCE_HOOK_REFUSES_OVER_N).

Owner, 2026-10-26: "Let's drop to 5 max subagents for Bench at a time (complete all current work entirely, don't
cancel) to preserve. We should make this a semi-automated process going forward, so I don't have to stare at it and
guess." Then at 13:05: "...please use it to determine the number of Foundry and Bench agents yourself. My 5 was a guess."

So N is not fixed here. v3 (HELPER_BUDGET_MIGRATE_INTO_DISPATCHER): the Dispatcher is the source. It publishes the
per-seat budget every tick (src/RimMandrake/rimflow/helper_budget.py -> <dispatcher state>/helper_budget.json, seats
CONDUCTOR and FOUNDRY); the window seat AGENT_SEAT=BENCH reads the CONDUCTOR budget. When that file is missing, stale
(10 min) or older than his last word, the hook falls back to the allocator's per-seat N
(src/RimMandrake/Utils/slot_allocator.py, rules in slot_rules.json): allocation.json when that is under 40 min old
and newer than his last word, computed live otherwise, and the rules file's fallback_n if neither works. Running helpers are counted from this seat's
subagent transcripts (slot_allocator.running_helpers: written in the last 15 min and not cleanly ended; when in doubt
a helper counts as running). Nothing here cancels a helper: the refusal only says to wait.

Open policy (owner, 2026-10-29: "The worker opennpolicy for conductor should only be for work started within 20 mins
of the last time the user typed to conductor. After that it should relax to two subagents only."): the interactive
Conductor window (seat BENCH without RM_ROLE_UNIT) has no helper limit while the owner's last typed message in THIS
window is under conductor_window.open_min (slot_rules.json, 20) old; after that it is capped at conductor_window.cap_n
(2) concurrent helpers. The typed time is seat_restart.tx_summary(...)["last_user_at"] over this session's transcript
(human origin only); unreadable means capped. See session_exempt().

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
RIMFLOW = ROOT / "src" / "RimMandrake" / "rimflow"
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


def conductor_window(rules):
    cw = rules.get("conductor_window") or {}
    return float(cw.get("open_min", 20)), int(cw.get("cap_n", 2))


def last_typed(payload):
    """Epoch of the owner's last real typed message in this session's transcript, or None (unreadable: fail closed).
    Reuses seat_restart.tx_summary, which tells human input from rings/task-notifications by transcript origin."""
    try:
        path = payload.get("transcript_path")
        if not path:
            return None
        if str(RIMFLOW) not in sys.path:
            sys.path.insert(0, str(RIMFLOW))
        import seat_restart as SR
        s = SR.tx_summary(path)
        return (s or {}).get("last_user_at")
    except Exception:  # noqa: BLE001
        return None


def session_exempt(seat, payload, rules, now):
    """True when the helper cap does not apply: the interactive Conductor window (seat BENCH, no RM_ROLE_UNIT: a
    scheduled or Dispatcher role run always carries it) while the owner typed within conductor_window.open_min.
    FOUNDRY and every role run keep the allocator's limits."""
    if seat != "BENCH" or (os.environ.get("RM_ROLE_UNIT") or "").strip():
        return False
    open_min, _ = conductor_window(rules)
    t = last_typed(payload)
    return t is not None and 0 <= now - t < open_min * 60


def allowed_n(SA, rules, seat, now):
    """(N, mode, why, source) for this seat (the allocator's key: BENCH is the Conductor's window)."""
    try:
        if str(RIMFLOW) not in sys.path:
            sys.path.insert(0, str(RIMFLOW))
        import helper_budget as HB
        bud = HB.read(now=now)
        name = HB.budget_seat(SA.seat_label(seat))
        if bud and name in bud["seats"]:
            return int(bud["seats"][name]), bud.get("mode"), bud.get("why", ""), f"Dispatcher budget of {bud.get('at')}"
    except Exception:  # noqa: BLE001  the budget is one source; the allocator below is the fallback
        pass
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
    if session_exempt(seat, payload, rules, now):
        return None
    n, mode, why, src = allowed_n(SA, rules, seat, now)
    ov = SA._override_live(SA.read_json(SA.streams_dir() / "slot_override.json"), now) or {}
    his_n = (ov.get("seats") or {}).get(seat, ov.get("n"))
    if seat == "BENCH" and his_n is not None:  # his word outranks the window cap, as the refusal text promises
        n, mode, src = int(his_n), "OWNER_WORD", "slot_override.json"
        why = f"his word: \"{ov['ownerSaid']}\""
    elif seat == "BENCH" and not (os.environ.get("RM_ROLE_UNIT") or "").strip():
        open_min, cap_n = conductor_window(rules)
        n, mode, src = cap_n, "CONDUCTOR_WINDOW", f"owner silent {open_min:g}+ min or unreadable (slot_rules.json conductor_window)"
        why = "the open policy lapsed (owner, 2026-10-29): two helpers until he types to this window again"
    label = SA.seat_label(seat)
    running = SA.running_helpers([SA.projects_dir() / SA.SEAT_PROJECT[seat]], now, rules)
    if len(running) < n:
        return None
    ids = ", ".join(x["id"][:10] for x in running[:8])
    return (
        f"Blocked: {label} already has {len(running)} helper(s) running and the allocator allows N={n} now "
        f"(mode {mode}, {src}).\n\nWhy N={n}: {why}\n\nRunning: {ids}\n\n"
        "Do not cancel a running helper to make room. Wait for one to finish, then spawn. The Dispatcher republishes the "
        "budget every tick; `python3 src/RimMandrake/rimflow/helper_budget.py show` shows it.\n"
        "Only the owner's word raises N (the override flag):\n"
        f"    python3 src/RimMandrake/Utils/slot_allocator.py set --seat {label} --n <N> --owner-said \"<his exact words>\"\n"
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
