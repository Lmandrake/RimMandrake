"""What a hostile on a pit square is. RIMMANDRAKE_TRACE_FLOWWORKS_RAIDER_IN_OPEN_PIT_WALKED_OUT: the run t6 "stray raider" was
read as a free man in an open 4 m pit; a raider in climbing gear crosses a pit by design, 450 ticks a step, never held."""

GEAR = 'RM_ClimbingGear'


def worn(reply):
    """The apparel defs of a jawa/pawn_get reply, or None when the reply does not say."""
    pawns = (reply or {}).get('pawns') or []
    if not (reply or {}).get('success') or not pawns or pawns[0].get('apparel') is None:
        return None
    return [a.get('def') for a in pawns[0]['apparel']]


def label(trap, apparel):
    """HELD | CLIMBER (wears the gear: allowed) | ONPIT (neither: the fault) | TRAP-UNREAD | GEAR-UNREAD (could not look)."""
    if not trap.startswith('TRAP '):
        return 'TRAP-UNREAD'
    if 'held=True' in trap:
        return 'HELD'
    if apparel is None:
        return 'GEAR-UNREAD'
    return 'CLIMBER' if GEAR in apparel else 'ONPIT'
