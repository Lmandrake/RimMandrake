#!/usr/bin/env python3
"""PreToolUse/SendMessage hook — hold a cross-session message to a window that is being restarted.

Owner 2026-11-02: a window that says it is ready for a reboot must be restarted "before some nonsense message messes
with it" (RESTART_NOW_BUILD_WINDOW_SAYS_READY). No hook fires on RECEIVING a peer message (broadcast.py), so the hold
sits on the sender: a send whose `to` names a seat window with a restart request on disk, a `--now` stamp, or a restart
pending or under way is refused, with where to resend. Anything unreadable lets the message through (fail open).

    python3 src/RimMandrake/rimflow/selftest_restart_now.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(HERE))
RIMFLOW = os.path.join(ROOT, "src", "RimMandrake", "rimflow")

REASON = (
    "Held: {name} is being restarted ({why}). A message now would reopen the turn it just ended, or die with the old "
    "window. Resend it to the fresh window once it has woken: `python3 src/RimMandrake/rimflow/seat_restart.py status` "
    "shows `verified` when it has."
)


def restarting(to, now=None, sr=None):
    """-> (seat, why) if `to` names a seat window being restarted, else None."""
    if sr is None:
        sys.path.insert(0, RIMFLOW)
        import seat_restart as sr  # noqa: PLC0415
    import session_match as sm  # noqa: PLC0415 - sits beside seat_restart
    now = time.time() if now is None else now
    cfgs = sr.config(sr._schedule())
    st = sr._read_json(os.path.join(sr.doorbell.state_dir(), "state.json")) or {}
    for seat, cfg in cfgs.items():
        names = sm.names_of(cfg)
        if not (sm.name_matches(to.strip(), names) or to.strip().upper() in [seat] + [n.upper() for n in names]):
            continue
        rs = (st.get("seat_restart") or {}).get(seat) or {}
        if rs.get("state") in ("pending", "claimed", "killed"):
            return seat, "restart %s" % rs["state"]
        stamp = sr._read_json(sr.now_stamp_path(seat)) or {}
        req = sr._read_json(sr.request_path(seat)) or {}
        for rec, label in ((stamp, "said ready (--now)"), (req, "restart requested")):
            ts = rec.get("req_ts", rec.get("ts"))
            if ts is not None and ts != rs.get("req_ts") and 0 <= now - float(ts) < cfg["request_max_age_s"]:
                return seat, label
    return None


def main():
    try:
        data = json.load(sys.stdin)
        to = str((data.get("tool_input") or {}).get("to") or "")
        hit = restarting(to) if to else None
    except Exception:  # noqa: BLE001 - a broken reading never strands a message
        return 0
    if hit:
        print(REASON.format(name=to, why=hit[1]), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
