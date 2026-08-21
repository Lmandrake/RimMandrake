#!/usr/bin/env python3
r"""game_paths.py — one place that knows where RimWorld lives.

Import this instead of hardcoding `C:\...` in a new script:

    from game_paths import MODS_CONFIG, WORKSHOP, LOCAL_MODS, GAME_DATA, DEF_DUMP

WHY THIS EXISTS
===============
Every Utils script grew its own `C:\Users\Mandrake\...` literal. Under WSL
those cannot be opened, so each script failed — and each failed by naming a
missing FILE:

    cannot read ModsConfig: [Errno 2] No such file or directory: 'C:\Users\...'
    FileNotFoundError: 'C:\...\DefDump\defs\ThingDef.json'

Nobody reads that as "wrong interpreter". They read it as "the config is gone"
and go looking for a deleted file. That single misleading message is how
"refresh.py only works under python.exe" hardened into project doctrine and
into CLAUDE.md, when the truth was two unresolved path literals. Fixed
2026-08-13; `refresh.py` and `deploy_custom_mods.py` now run identically under
both interpreters.

⚠️ **`os.path.expanduser("~")` is NOT a fix.** Under WSL it resolves to the
Linux home (`/home/<user>`), not the Windows profile, so it silently builds a
path that will never exist. `rimworld_loadset.py` had exactly this. The same
trap bit the bridge client's `DEFAULT_PLAYER_LOG`.

THE RULE
========
Windows form first, `/mnt/c` form second, whichever exists wins. If neither
exists we return the FIRST candidate rather than None, so the caller's own
error message still names a concrete path a human can go and look at — an
error saying `None` is worse than one naming a plausible file.
"""

import os
import re

__all__ = ["MODS_CONFIG", "DEF_DUMP", "DUMP_ROOT", "CAPTURES", "PLAYER_LOG",
           "PREV_LOG", "IDEOS", "SAVES", "WORKSHOP", "LOCAL_MODS", "GAME_DATA",
           "LOCALLOW", "STEAM", "resolve", "describe", "captures",
           "newest_capture", "KEEP_MARKER"]


def resolve(win, wsl):
    """First of (win, wsl) that exists; else win, so errors stay concrete."""
    for p in (win, wsl):
        if p and os.path.exists(p):
            return p
    return win


# --- the two roots everything else hangs off -----------------------------
_LOW_WIN = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios"
_LOW_WSL = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
_STEAM_WIN = r"C:\Program Files (x86)\Steam\steamapps"
_STEAM_WSL = "/mnt/c/Program Files (x86)/Steam/steamapps"

LOCALLOW = resolve(_LOW_WIN, _LOW_WSL)
STEAM = resolve(_STEAM_WIN, _STEAM_WSL)

MODS_CONFIG = resolve(os.path.join(_LOW_WIN, r"Config\ModsConfig.xml"),
                      os.path.join(_LOW_WSL, "Config/ModsConfig.xml"))
DUMP_ROOT = resolve(os.path.join(_LOW_WIN, "DefDump"),
                    os.path.join(_LOW_WSL, "DefDump"))
CAPTURES = os.path.join(DUMP_ROOT, "captures")

#: A capture directory carrying this file is never pruned. `refresh.py --freeze`
#: writes it into the capture it freezes, so the producer can enforce retention
#: without knowing anything about this repo or its registry.
KEEP_MARKER = ".keep"

#: A capture id is the ISO-8601 instant it was taken, with `:` made filesystem
#: safe — `2026-08-21T08-20-20Z`. That is the whole pointer mechanism.
_CAPTURE_ID = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$")


def captures(root=None):
    """-> [capture id] oldest first. [] when the dump is still the flat layout.

    🔑 **Sorting is lexicographic AND that is exact**, because the ids are
    ISO-8601 with fixed-width fields. No date parsing, nothing to get wrong in a
    second language — the C# producer sorts the same strings the same way.
    """
    root = root or CAPTURES
    try:
        return sorted(d for d in os.listdir(root)
                      if _CAPTURE_ID.match(d)
                      and os.path.isdir(os.path.join(root, d)))
    except OSError:
        return []


def newest_capture(root=None):
    """-> absolute path of the newest capture, or None under the flat layout."""
    ids = captures(root)
    return os.path.join(root or CAPTURES, ids[-1]) if ids else None


# 🔴 **DEF_DUMP IS THE CAPTURE, NOT THE FOLDER THAT HOLDS CAPTURES.** Every
# reader wants "the current capture's manifest.json / defs/", and that is what
# this has always meant — so it keeps meaning it across the layout change
# (`DUMP_STORAGE_LAYOUT_RULING_1`, owner 2026-08-21: *"Option (a) all the way.
# Keep last three."*).
#
# ⚠️ **The fallback is what makes the migration safe.** Before the producer is
# changed there is no `captures/`, and this resolves to the flat `DefDump/`
# exactly as before; afterwards it resolves to the newest dated capture. Both
# layouts work with one line of code and no flag day.
#
# ⛔ Do NOT "simplify" this to `CAPTURES` — a reader that points at the folder of
# captures sees a directory of directories where it expects `defs/`, and the
# failure is a confusing empty result rather than an error.
DEF_DUMP = newest_capture() or DUMP_ROOT
# ⚠️ RimWorld's OWN Player.log, not the one under Ludeon Studios/RimWorld/. The
# distinction has cost a session before: this is the file the game appends to.
PLAYER_LOG = resolve(os.path.join(_LOW_WIN, "Player.log"),
                     os.path.join(_LOW_WSL, "Player.log"))
# Where the game keeps saved ideoligions (.rid) and savegames (.rws).
# Unity rotates Player.log -> Player-prev.log at launch, PRESERVING the old
# file's mtime, which makes it the anchor for "which run is this".
PREV_LOG = resolve(os.path.join(_LOW_WIN, "Player-prev.log"),
                   os.path.join(_LOW_WSL, "Player-prev.log"))
IDEOS = resolve(os.path.join(_LOW_WIN, "Ideos"),
                os.path.join(_LOW_WSL, "Ideos"))
SAVES = resolve(os.path.join(_LOW_WIN, "Saves"),
                os.path.join(_LOW_WSL, "Saves"))
WORKSHOP = resolve(os.path.join(_STEAM_WIN, r"workshop\content\294100"),
                   os.path.join(_STEAM_WSL, "workshop/content/294100"))
LOCAL_MODS = resolve(os.path.join(_STEAM_WIN, r"common\RimWorld\Mods"),
                     os.path.join(_STEAM_WSL, "common/RimWorld/Mods"))
GAME_DATA = resolve(os.path.join(_STEAM_WIN, r"common\RimWorld\Data"),
                    os.path.join(_STEAM_WSL, "common/RimWorld/Data"))


def describe():
    """Print what resolved to what, and flag anything missing. Run this first
    when a script says a game file does not exist."""
    rows = [("ModsConfig.xml", MODS_CONFIG), ("DefDump root", DUMP_ROOT),
            ("current capture", DEF_DUMP),
            ("Player.log", PLAYER_LOG), ("Ideos/", IDEOS),
            ("Saves/", SAVES),
            ("workshop/294100", WORKSHOP), ("Mods/", LOCAL_MODS),
            ("Data/", GAME_DATA)]
    width = max(len(n) for n, _ in rows)
    for name, path in rows:
        print("  %-*s  %-7s %s" % (width, name,
                                   "ok" if os.path.exists(path) else "MISSING",
                                   path))


if __name__ == "__main__":
    print("resolved game paths (%s):"
          % ("WSL/Linux" if os.sep == "/" else "Windows"))
    describe()
