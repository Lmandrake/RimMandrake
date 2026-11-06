"""shotsettle.py - a screenshot that shows where pawns ARE after bulk tick stepping, at zero ticks.

SHOTSETTLE_BUILD_PAUSED_BARRIER (design/RimMandrake/tickburst_2026-11-06/final.md L-e, GPT review 12).

After many ticks in one frame (safe_advance, step_game_ticks) each pawn's sim position has moved and
its PawnTweener-drawn position has not: the tweener eases per real frame, scaled by a tick-rate
multiplier that reads 0 while paused. The old cure, "play a few frames at Normal", advances the
simulation. This helper is the paused barrier instead:

    pause -> read ticksGame -> clear_ui -> jawa/settle_tweens -> take_screenshot -> read ticksGame

and it REFUSES (ShotSettleError) when the two ticksGame reads differ, so a picture never silently
cost ticks. `call` is any `call(tool, **params) -> dict` (rimdrive/rimbench Session.call); wrap a
rimbridge_client with `lambda t, **p: rb.call(t, p)`.
"""


class ShotSettleError(RuntimeError):
    """The shot could not be proved tick-free, or a step of it failed."""


def _ticks(call):
    r = call("rimworld/get_game_info") or {}
    t = r.get("ticksGame")
    if isinstance(t, bool) or not isinstance(t, int):
        raise ShotSettleError("UNMEASURED: get_game_info gave no integer ticksGame: %r" % (t,))
    return t


def settled_shot(call, file_name, clear_ui=True):
    """Pause, settle tweened pawn positions, capture, and prove no tick passed.

    Leaves the game PAUSED (the barrier's point; nothing here resumes it).
    Returns {path, ticksBefore, ticksAfter, settled, maxShiftCells}."""
    p = call("rimworld/pause_game", pause=True) or {}
    if p.get("success") is False:
        raise ShotSettleError("pause_game failed: %s" % p.get("message"))
    t0 = _ticks(call)
    if clear_ui:
        u = call("jawa/clear_ui") or {}
        if u.get("success") is False:
            raise ShotSettleError("clear_ui failed: %s" % u.get("message"))
    s = call("jawa/settle_tweens") or {}
    if not s.get("success"):
        raise ShotSettleError("settle_tweens refused: %s" % (s.get("message") or s))
    if s.get("ticksBefore") != t0 or s.get("ticksAfter") != t0:
        raise ShotSettleError("settle_tweens saw ticks %r..%r, expected %d"
                              % (s.get("ticksBefore"), s.get("ticksAfter"), t0))
    r = call("rimworld/take_screenshot", fileName=file_name, suppressMessage=True) or {}
    if r.get("success") is False or not r.get("path"):
        raise ShotSettleError("take_screenshot failed: %s" % (r.get("message") or r))
    t1 = _ticks(call)
    if t1 != t0:
        raise ShotSettleError("the shot advanced the game %d ticks (%d -> %d)" % (t1 - t0, t0, t1))
    return {"path": r.get("path"), "ticksBefore": t0, "ticksAfter": t1,
            "settled": s.get("settled"), "noTweener": s.get("noTweener"),
            "maxShiftCells": s.get("maxShiftCells")}
