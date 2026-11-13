#!/usr/bin/env python3
"""Whole levels from the bridge's one water number (RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES).

The bridge reports water only in decilitres (excavation_rect / pulse rows `dl`, excavation_report / excavation_drive
`waterDl`) and metres (`waterM`); it has no notch count (`fill`, `f`, `fEff` are gone with FillAt). A proof that still
compares against a whole-level oracle derives the level here: floor(dL / U), what the deleted FillAt read. A reply with
no water field raises, so an old bridge DLL fails loudly instead of reading dry.
"""

U_DL = 10000        # decilitres per level per square (RM_Volume.UnitsPerLevel; 0.5 m, 1,000 L)

_RAISE = object()


def levels(r, default=_RAISE):
    """floor(water / one level) of a rect/pulse row (`dl`) or a report/drive reply (`waterDl`)."""
    if r:
        for k in ("dl", "waterDl"):
            if r.get(k) is not None:
                return int(r[k]) // U_DL
    if default is not _RAISE:
        return default
    raise KeyError("water read: no dl/waterDl in %r" % (sorted(r) if isinstance(r, dict) else r,))


def levels_of(dls):
    """A pulse vector of per-cell dL as whole levels."""
    return [int(d) // U_DL for d in dls]
