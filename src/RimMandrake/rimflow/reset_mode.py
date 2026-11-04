"""The Conductor window's reset switch (CONDUCTOR_RESET_FIX_KILLED_MID_READ). Owner 2026-11-03: "I wish there were a switch
I could click on Conductor that said "hold for user interaction" or "ready to reset as soon as possible" or "auto"".

  auto   today's rule: 110k idle and quiet, 200k at the next ended turn plus 20 s of quiet (seat_restart).
  hold   no context-backstop restart while he reads or types, up to a safety ceiling (seat_restart._hold_stands).
  ready  restart at the next ended turn, whatever the context size.

A goodbye and a HANDOFF READY are the window's own request and outrank all three. The switch is his WHOLE message, the
way goodbye is (.claude/hooks/conductor_goodbye.py), and it shows on the window's status line (statusline.py).
A mode belongs to ONE window: the file names its session, and any other window reads auto. That is what stops `ready`
restarting every fresh window for ever, and a forgotten hold from outliving the window it was meant for.

Shared by the hook, the status line and seat_restart, so it imports nothing heavy.
"""
import json
import os
import time

AUTO, HOLD, READY = "auto", "hold", "ready"
MODES = (AUTO, HOLD, READY)
# normalized as goodbye_phrase.norm does: casefold, no apostrophes, non-word runs as one space
WORDS = {"hold": HOLD, "hold for user interaction": HOLD, "reset hold": HOLD,
         "ready": READY, "ready to reset": READY, "ready to reset as soon as possible": READY, "reset ready": READY,
         "auto": AUTO, "reset auto": AUTO}
SAID = {HOLD: "Reset switch: HOLD. No context restart while you read or type (safety ceiling {tokens} tokens, or {hours} h "
              "without a message from you). Say auto or ready to change it; goodbye still fires at once.",
        READY: "Reset switch: READY. This window restarts as soon as this turn ends; my last reply is shown again in the "
               "fresh window.",
        AUTO: "Reset switch: AUTO. The ordinary context limits apply again."}


def mode_of_words(normalized):
    """-> the mode his whole (already normalized) message names, or None."""
    return WORDS.get(normalized)


def path(seat, root):
    return os.path.join(root, "restart", "%s.mode.json" % seat)


def read(seat, session_id, root):
    """-> {"mode", "at"} for this window. No file, an unreadable one or another window's: auto, today's rule."""
    try:
        with open(path(seat, root), encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {"mode": AUTO, "at": None}
    if not isinstance(d, dict) or d.get("mode") not in MODES or not session_id or d.get("session_id") != session_id:
        return {"mode": AUTO, "at": None}
    return {"mode": d["mode"], "at": d.get("at")}


def write(seat, mode, session_id, root, by="", now=None):
    """Atomic: the Dispatcher reads this between its ticks. -> the path. Raises ValueError on a mode or window it cannot name."""
    if mode not in MODES or not session_id:
        raise ValueError("reset mode %r for session %r" % (mode, session_id))
    p = path(seat, root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = "%s.%d.tmp" % (p, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"seat": seat, "mode": mode, "session_id": session_id, "at": time.time() if now is None else now,
                   "by": by}, f)
    os.replace(tmp, p)
    return p


def said(mode, cfg=None):
    cfg = cfg or {}
    return SAID[mode].format(tokens=cfg.get("hold_ceiling_tokens", "?"), hours=round((cfg.get("hold_max_s") or 0) / 3600, 1))


def badge(mode, past_ceiling=False):
    """The status line's word: AUTO stays quiet, the two he chose stand out."""
    if mode == HOLD:
        return "\033[1;33mreset HOLD%s\033[0m" % (" past its ceiling" if past_ceiling else "")
    if mode == READY:
        return "\033[1;31mreset READY\033[0m"
    return "\033[2mreset auto\033[0m"
