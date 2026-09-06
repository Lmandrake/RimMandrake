"""
Retired donor mods — the one list, read by every generator that eats a dump.

A frozen `observed/<date>/` dump is a photograph of a mod set that no longer
exists. Nothing in it knows the owner has since retired four donors, so a
generator re-run against it happily re-emits patches for mods the game will
never load again: that is exactly how bbf66830's hand cleanup of
Armour_Leather.xml became a change the generator would silently undo
(ARMOURY_LEATHER_GEN_DESYNC_1).

So the exclusion lives in ONE place —
`infrastructure/state/facts/retired_mods.json` — and generators call in here
rather than each carrying its own copy of the four names.

    from retired_mods import is_retired, filter_rows

    if is_retired(mod_name):            # display name or packageId
        continue
    rows = filter_rows(rows)            # drops rows whose modName/packageId is retired
"""

import io
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
FACT = os.path.join(_ROOT, "infrastructure", "state", "facts",
                    "retired_mods.json")

_cache = None


def _load():
    global _cache
    if _cache is None:
        with io.open(FACT, encoding="utf-8") as fh:
            entries = json.load(fh)["retired"]
        names, pids = set(), set()
        for e in entries:
            pid = (e.get("packageId") or "").strip()
            if pid:
                pids.add(pid.lower())
            for n in e.get("modNames") or []:
                if n.strip():
                    names.add(n.strip().lower())
        _cache = (entries, names, pids)
    return _cache


def entries():
    """The raw fact rows, for reporting."""
    return list(_load()[0])


def is_retired(value):
    """True if `value` is a retired mod's display name OR its packageId.

    One argument on purpose: callers hold either form and rarely both, and a
    name-vs-packageId mixup is the failure this is meant to prevent.
    """
    if not value:
        return False
    v = str(value).strip().lower()
    _, names, pids = _load()
    return v in names or v in pids


def filter_rows(rows, name_key="modName", pid_key="packageId"):
    """Drop dump rows contributed by a retired mod.

    Checks packageId first (stable) and falls back to the display name, so a
    dump that carries only one of the two columns is still filtered.
    """
    out = []
    for r in rows:
        pid = (r.get(pid_key) or "").strip() if pid_key else ""
        name = (r.get(name_key) or "").strip() if name_key else ""
        if is_retired(pid) or is_retired(name):
            continue
        out.append(r)
    return out
