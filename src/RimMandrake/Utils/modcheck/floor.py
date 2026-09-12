"""modcheck.floor -- the Mod Settings toggle FLOOR.

Owner ruling 2026-09-12: a mod's Mod Settings toggles are the floor -- every
toggle has at least one covering component -- and the builder adds
components for complex functions beyond any toggle. The ceiling is open;
this module has no opinion on it, and enforces only the floor.

KNOWN GAP, recorded rather than papered over: as of 2026-09-12 most mods
(the pilot, `RimMandrake Pits`, included) have no Mod Settings at all yet --
that is `MOD_OPTIONS_RETROFIT_1`'s job, not this module's. Zero toggles is
not a floor violation here; it means every component in that mod's suite is
necessarily `beyond_toggle=True` until settings exist to cover.
"""


def uncovered(toggles, components):
    """`toggles`: iterable of Mod Settings toggle field names.
    `components`: iterable of {"toggle": name_or_None, "beyond_toggle": bool}
    dicts, one per registered component across every chain in a `Suite`.

    Returns the sorted list of toggle names with zero covering component.
    Empty means the floor is met. Never raises -- callers (a CLI, a runner)
    decide whether an uncovered toggle is fatal to a run.
    """
    covered = {c["toggle"] for c in components if c.get("toggle")}
    return sorted(set(toggles) - covered)
