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


def uncovered_shows(must_show_ids, components):
    """The VISUAL floor -- owner ruling 2026-09-15, north_star_validation_spec.md
    section 3. Mirror of `uncovered` above: uncovered EXPERIENCE is as fatal as
    an uncovered settings toggle.

    `must_show_ids`: iterable of must-show ids from the mod's walk `## north
    star` section -- pass ONLY the ids of a VALIDATED section. A DRAFT section
    contributes nothing: it cannot fail a mod and cannot green one.
    `components`: the same component dicts, each optionally carrying "shows".

    Returns the sorted list of must-show ids no component claims. Empty means
    the visual floor is met. Never raises; the caller decides fatality.
    """
    claimed = set()
    for c in components:
        claimed.update(c.get("shows") or ())
    return sorted(set(must_show_ids) - claimed)


def orphan_shows(must_show_ids, components):
    """The reverse check: ids a component CLAIMS that the validated checklist
    does not define. A lint error, never a silent pass -- claiming to show
    something nobody asked for is the same defect class as a patch that matches
    nothing (CLAUDE.md, 'A patch that matches nothing logs nothing').

    Commonly means a must-show id was renamed and a `shows=` was left behind.
    Returns the sorted list of orphaned ids.
    """
    claimed = set()
    for c in components:
        claimed.update(c.get("shows") or ())
    return sorted(claimed - set(must_show_ids))
