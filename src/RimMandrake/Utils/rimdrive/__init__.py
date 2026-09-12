"""rimdrive -- the reusable Python bridge library.

L1 (`rimdrive.session`) + L2 (`rimdrive.verify`) per
design/RimMandrake/bridge_library_design.md (owner-ruled 2026-09-12).
L3 domain verbs (things/pawns/map/world/events/camera/time) and L4
consumers (modcheck, content-injection kits) land as separate packages,
verb-by-verb, per that design's rollout section -- this package does not
grow them preemptively.

    from rimdrive import Session, mutate, Unchanged, Indeterminate, UNVERIFIED

    with Session() as s:
        tid = s.call("rimworld/spawn_thing", defName="...", x=1, z=1)["thingId"]
        s.track("thing", tid, x=1, z=1)          # torn down by sweep() on exit
"""
from .session import Session, SessionError, ToolCensusError
from .verify import Unchanged, Indeterminate, Reconnected, UNVERIFIED, mutate

__all__ = [
    "Session", "SessionError", "ToolCensusError",
    "Unchanged", "Indeterminate", "Reconnected", "UNVERIFIED", "mutate",
]
