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

__all__ = ["MODS_CONFIG", "DEF_DUMP", "PLAYER_LOG", "PREV_LOG", "IDEOS", "SAVES",
           "WORKSHOP", "LOCAL_MODS", "GAME_DATA", "LOCALLOW", "STEAM",
           "resolve", "describe"]


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
DEF_DUMP = resolve(os.path.join(_LOW_WIN, "DefDump"),
                   os.path.join(_LOW_WSL, "DefDump"))
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
    rows = [("ModsConfig.xml", MODS_CONFIG), ("DefDump/", DEF_DUMP),
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
