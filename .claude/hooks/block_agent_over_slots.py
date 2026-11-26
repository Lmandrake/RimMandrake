#!/usr/bin/env python3
"""PreToolUse/Agent hook: refuse a spawn when this seat already runs its allocated N helpers (SLOT_CAP_ENFORCE_HOOK_REFUSES_OVER_N).

Owner, 2026-10-26: "Let's drop to 5 max subagents for Bench at a time (complete all current work entirely, don't
cancel) to preserve. We should make this a semi-automated process going forward, so I don't have to stare at it and
guess." Then at 13:05: "...please use it to determine the number of Foundry and Bench agents yourself. My 5 was a guess."

So N is not fixed here. v3 (HELPER_BUDGET_MIGRATE_INTO_DISPATCHER): the Dispatcher is the source. It publishes the
per-seat budget every tick (src/RimMandrake/rimflow/helper_budget.py -> <dispatcher state>/helper_budget.json, seats
CONDUCTOR and MATURATION); the window seat AGENT_SEAT=BENCH reads the CONDUCTOR budget. When that file is missing, stale
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
(human origin only); unreadable means capped. See session_exempt(). His own word (slot_override.json) is read first
and caps the window at his N even while he types (SPAWN_HOOK_FIX_TYPING_BEATS_OWNER_CAP).

Count and spawn are serialised: the last check runs under an flock on <streams>/spawn_gate.lock, and each allowed spawn
writes a reservation (<streams>/spawn_reservations.json) that counts as a running helper until a helper transcript
started after it appears or helpers.reserve_s (default 90 s) passes, so two concurrent spawns cannot both take the
last slot.

Role runs with their own allowance (RIMMANDRAKE_BUDGET_DESIGNER_EXAM_HELPERS_FIVE_READERS_ZERO_SLOTS): a role run whose
RM_ROLE_UNIT starts with a prefix in slot_rules.json `role_runs` (the Designer, rm-role-designer-*) is a Maturation
Pipeline run, already counted in the pipeline's own slots; its helpers (the exam's Examiner, Challenger, two Readers and
Control) are capped at that prefix's N, counted on that run's OWN session only, never against the Conductor's budget nor
the window's helpers. Measured 2026-11-15: CONDUCTOR N=0 once he left the window, so Contagion's exam could never run.
His word (slot_override.json) still caps it. A full allowance is refused with reason `slots_full`: the run waits.

Fails open: a broken guard must not stop all spawning.

    python3 .claude/hooks/selftest_block_agent_over_slots.py
"""
import glob
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
UTILS = ROOT / "src" / "RimMandrake" / "Utils"
RIMFLOW = ROOT / "src" / "RimMandrake" / "rimflow"
FRESH_S = 40 * 60
RESERVE_S = 90          # an allowed spawn holds its slot this long, or until its helper transcript appears
START_SLACK_S = 2       # a helper transcript may stamp its first record a moment before the hook wrote its reservation
LOCK_WAIT_S = 5         # past this the gate fails open rather than stall every spawn


def seat_of(payload):
    s = (os.environ.get("AGENT_SEAT") or "").strip().upper()
    if s:
        return s
    cwd = str(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).rstrip("/")
    if cwd.endswith("/rm/bench") or "/rm/bench/" in cwd:
        return "BENCH"
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


def draining(seat, payload, now):
    """Why this window is draining, or None. Its own failure must leave the slot logic standing, so it is caught here."""
    try:
        if str(RIMFLOW) not in sys.path:
            sys.path.insert(0, str(RIMFLOW))
        import seat_restart as SR
        return SR.drain_of(seat, payload.get("session_id"), now=now)
    except Exception:  # noqa: BLE001
        return None


def session_exempt(seat, payload, rules, now):
    """True when the helper cap does not apply: the interactive Conductor window (seat BENCH, no RM_ROLE_UNIT: a
    scheduled or Dispatcher role run always carries it) while the owner typed within conductor_window.open_min.
    Role runs keep their own limits or use the allocator's Conductor budget."""
    if seat != "BENCH" or (os.environ.get("RM_ROLE_UNIT") or "").strip():
        return False
    open_min, _ = conductor_window(rules)
    t = last_typed(payload)
    return t is not None and 0 <= now - t < open_min * 60


def role_allowance(rules):
    """(N, prefix) when this is a role run with its own allowance (slot_rules.json role_runs, keyed by RM_ROLE_UNIT
    prefix), else None. A non-integer N is ignored (the Conductor budget then applies, as before)."""
    unit = (os.environ.get("RM_ROLE_UNIT") or "").strip()
    rr = rules.get("role_runs") or {}
    # the longest matching prefix wins: `rm-detached-` gives every detached run its own allowance, and a named kind
    # (the rewrite batch's one reader) keeps its own number
    for prefix, n in sorted(rr.items(), key=lambda kv: -len(kv[0])):
        if unit and not prefix.startswith("_") and unit.startswith(prefix) and isinstance(n, int) \
                and not isinstance(n, bool) and n >= 0:
            return n, prefix
    return None


def session_scope(payload):
    """(reservation key, this session's subagents folder) for a role run's own count. The folder is the transcript's
    sibling <session id>/subagents; None when the payload names no transcript or session (only reservations count)."""
    unit = (os.environ.get("RM_ROLE_UNIT") or "").strip()
    tp, sid = payload.get("transcript_path"), payload.get("session_id")
    if not sid and tp:
        sid = Path(tp).stem
    sub = str(Path(tp).parent / sid / "subagents") if tp and sid else None
    return "role:" + unit, sub


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


def unbounded_refuses(payload):
    """True when block_unbounded_agent.py (the other PreToolUse Agent hook) refuses this spawn. Both hooks run, so a
    reservation written for such a spawn held a slot for reserve_s with no helper behind it: three sightings, lesson
    20261112T084018Z-BENCH-refused-spawn-holds-slot. Unreadable: False (the slot gate stays as it was)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import block_unbounded_agent as U
        if os.environ.get("RM_ALLOW_UNBOUNDED_AGENT") == "1":
            return False
        return U.refused_type(payload.get("tool_input") or {}) is not None   # "" (an omitted type) is refused too
    except Exception:  # noqa: BLE001
        return False


def decide(payload, now=None):
    """None to allow, or the refusal text."""
    now = now or time.time()
    if unbounded_refuses(payload):
        return None     # the other hook refuses it; reserve nothing
    seat = seat_of(payload)
    if str(UTILS) not in sys.path:
        sys.path.insert(0, str(UTILS))
    import slot_allocator as SA
    rules = SA.load_rules(os.environ.get("RM_SLOT_RULES") or UTILS / "slot_rules.json")
    if seat not in (rules.get("enforce_seats") or []) or seat not in SA.SEAT_PROJECT:
        return None
    drain = draining(seat, payload, now)
    # Owner, 2026-11-02: "This is unacceptable. You've essentially frozen me out of new subagents for Conductor for an
    # arbitrary amount of time." While he is typing to the Conductor window, a pending restart never blocks a spawn.
    if drain and seat == "BENCH" and session_exempt(seat, payload, rules, now):
        drain = None
    if drain:
        return (
            f"Blocked: this {SA.seat_label(seat)} window is draining for its restart ({drain}). Running helpers finish; "
            "no new one starts, because the kill waits on every helper alive. Run the work OUTSIDE this window "
            "instead; it survives the restart: `python3 src/RimMandrake/rimflow/detached_helper.py launch --seat "
            f"{SA.seat_label(seat)} --item <ID> --brief-file <F> --model sonnet|opus --budget-usd <cap for this job>`. Or file it in the "
            "ledger: the fresh window picks it up. (CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE)"
        )
    ov = SA._override_live(SA.read_json(SA.streams_dir() / "slot_override.json"), now) or {}
    his_n = (ov.get("seats") or {}).get(seat, ov.get("n"))
    own = role_allowance(rules)
    if own is not None:
        rn, prefix = own
        rwhy = f"slot_rules.json role_runs[{prefix!r}]: this role run's own allowance, counted on its own session"
        if his_n is not None and int(his_n) < rn:
            rn, rwhy = int(his_n), f"his word: \"{ov.get('ownerSaid')}\" (slot_override.json) caps the role run"
        unit = os.environ.get("RM_ROLE_UNIT", "").strip()

        def refuse_own(running):
            ids = ", ".join(x["id"][:10] for x in running[:8])
            return (
                f"slots_full: this role run ({unit}) already has {len(running)} helper(s) running and its own "
                f"allowance is N={rn}.\n\nWhy N={rn}: {rwhy}\n\nRunning: {ids}\n\n"
                "Wait for one of your helpers to finish, then spawn (the exam's steps run in order; two Readers and "
                "the Control may overlap). Do not cancel a running helper, and do not end the run blocked on this: a "
                "full allowance is a wait, not a defect.")
        return _gate(seat, rules, now, rn, refuse_own, scope=session_scope(payload))
    # SPAWN_HOOK_FIX_TYPING_BEATS_OWNER_CAP: his word is read BEFORE the typing exemption, so an explicit N of his caps
    # the window even while he types; the open policy only lifts the window's default cap.
    if his_n is None and session_exempt(seat, payload, rules, now):
        return _gate(seat, rules, now, None, lambda r: None)
    n, mode, why, src = allowed_n(SA, rules, seat, now)
    if seat == "BENCH" and his_n is not None:  # his word outranks the window cap, as the refusal text promises
        n, mode, src = int(his_n), "OWNER_WORD", "slot_override.json"
        why = f"his word: \"{ov['ownerSaid']}\""
    elif seat == "BENCH" and not (os.environ.get("RM_ROLE_UNIT") or "").strip():
        open_min, cap_n = conductor_window(rules)
        n, mode, src = cap_n, "CONDUCTOR_WINDOW", f"owner silent {open_min:g}+ min or unreadable (slot_rules.json conductor_window)"
        why = "the open policy lapsed (owner, 2026-10-29): two helpers until he types to this window again"
    label = SA.seat_label(seat)

    def refuse(running):
        ids = ", ".join(x["id"][:10] for x in running[:8])
        return (
            f"Blocked: {label} already has {len(running)} helper(s) running and the allocator allows N={n} now "
            f"(mode {mode}, {src}).\n\nWhy N={n}: {why}\n\nRunning: {ids}\n\n"
            "Do not cancel a running helper to make room. Wait for one to finish, then spawn. The Dispatcher republishes the "
            "budget every tick; `python3 src/RimMandrake/rimflow/helper_budget.py show` shows it.\n"
            "His word or the Conductor's decision raises N (owner 2026-11-19: only five acts stay his):\n"
            f"    python3 src/RimMandrake/Utils/slot_allocator.py set --seat {label} --n <N> --owner-said \"<his exact words>\"\n"
            f"    python3 src/RimMandrake/Utils/slot_allocator.py set --seat {label} --n <N> --per-ruling "
            "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM --why \"<the Conductor's decision>\"\n"
            "(it holds until the burn account's weekly reset; `slot_allocator.py clear` drops it)."
            )
    return _gate(seat, rules, now, n, refuse)


def reserve_s(rules):
    v = os.environ.get("RM_SPAWN_RESERVE_S")
    if v is not None and v.strip():
        return float(v)
    return float((rules.get("helpers") or {}).get("reserve_s", RESERVE_S))


def _pending(res, starts, now, hold_s):
    """Reservations not yet matched by a helper transcript that started at or after them (greedy, oldest first).
    A reservation stamped AFTER this caller's `now` is live too: `now` is read before the lock, so a spawn that waited
    on the lock sees the winner's later stamp, and dropping it would let both pass and overwrite the winner's."""
    live = sorted(float(t) for t in res if abs(now - float(t)) < hold_s)
    left = list(live)
    for st in sorted(starts):
        for i, t in enumerate(left):
            if t <= st + START_SLACK_S:
                del left[i]
                break
    return left


def _gate(seat, rules, now, n, refuse, scope=None):
    """SPAWN_HOOK_FIX_TYPING_BEATS_OWNER_CAP: count and reserve under one lock, so two concurrent spawns cannot both pass
    the last slot. An allowed spawn leaves a reservation that counts as a running helper until a helper transcript
    started after it appears (or reserve_s passes). n None = uncapped (the open policy): reserve only. Fails open when
    the lock or the reservation file cannot be had (a broken guard must not stop all spawning)."""
    import slot_allocator as SA
    hold_s = reserve_s(rules)
    proj = SA.projects_dir() / SA.SEAT_PROJECT[seat]
    key, pattern = seat, os.path.join(str(proj), "*", "subagents", "agent-*.jsonl")
    if scope is not None:   # a role run's own allowance: its own session's helpers and reservations only
        key, sub = scope
        pattern = os.path.join(sub, "agent-*.jsonl") if sub else None
    d = SA.streams_dir()
    try:
        import fcntl
        fd = os.open(str(d / "spawn_gate.lock"), os.O_CREAT | os.O_RDWR, 0o644)
    except Exception:  # noqa: BLE001
        fd = None
    try:
        if fd is not None:
            deadline = time.time() + LOCK_WAIT_S
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.time() > deadline:
                        os.close(fd)
                        fd = None
                        break
                    time.sleep(0.05)
        rf = d / "spawn_reservations.json"
        allr = SA.read_json(rf)
        allr = allr if isinstance(allr, dict) else {}
        mine = [t for t in (allr.get(key) or []) if isinstance(t, (int, float))]
        if n is None:
            running = []
        elif scope is None:
            running = SA.running_helpers([proj], now, rules)
        else:
            running = [x for x in SA.running_helpers([Path(scope[1]).parent.parent], now, rules)
                       if Path(x["path"]).parent == Path(scope[1])] if scope[1] else []
        starts = []
        if mine and hold_s > 0 and pattern:
            lo = min(mine) - START_SLACK_S
            for p in glob.glob(pattern):
                try:
                    if os.path.getmtime(p) < lo:
                        continue
                except OSError:
                    continue
                st = SA._first_ts(p)
                if st is not None and st >= lo:
                    starts.append(st)
        pend = _pending(mine, starts, now, hold_s) if hold_s > 0 else []
        if n is not None and len(running) + len(pend) >= n:
            held = running + [{"id": "reserved-" + time.strftime("%H%M%S", time.localtime(t))} for t in pend]
            return refuse(held)
        if hold_s > 0:
            allr[key] = sorted(pend + [max([now] + pend)])
            tmpf = rf.with_name(rf.name + f".{os.getpid()}.tmp")
            tmpf.write_text(json.dumps(allr))
            os.replace(tmpf, rf)
        return None
    except Exception:  # noqa: BLE001  fail open
        return None
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass


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
