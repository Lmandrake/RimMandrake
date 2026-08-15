# LIVE.md — facts you would otherwise need a running game to learn

Published by CHECK. One line per fact. Superseded lines are replaced, not appended to.
Everything here was read out of a running game or off an artifact a running game wrote.

## The def dump

- **Current dump: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump`,
  captured `2026-08-15T15:10:11Z` (08:10 local), `mode: all`, game `1.6.4871 rev591`.**
  576 mods, 529 files under `defs/`, `animals.json` alongside. Taken during the C37
  load, so it carries `mandrake.starwarsraces` and does NOT carry the three donors
  (`btd.xenotyperemix.starwars`, `guy762.starwarsxenotypes`,
  `neronix17.outerrim.galacticdiversity`). This is the def universe `validate_patch.py --defs`
  currently checks against, and it is the current one.
- 🔴 **Read freshness from `manifest.json` → `capturedUtc`, NEVER from a folder mtime.**
  The `defs/` folder still reads 2026-08-14 01:20 because the dump overwrites files in
  place and never adds or removes one, so the directory mtime has not moved in a day.
  A stale-looking folder date sent NEXT_RELOAD §1.0 step 0 to the wrong conclusion on
  2026-08-15; the dump was fresh the whole time.
- The dump is armed by `echo all > .../DefDump/dump_request.txt` and the request is read
  **at startup only** — arming it while the game runs does nothing until the next launch.
  It costs 18.7 s of load time (`timingsMs.allDefs` 18579).

## Facial Animation

- **FA's per-xenotype opt-out is keyed by defName**, in
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_1635901197_FacialAnimationMod.xml`,
  and **FA reads it at startup only**. Currently 156 entries, 69 of them
  `Human-RimMandrake*` — verified 2026-08-15 against the 69 XenotypeDefs the races mod
  ships; the two lists match exactly, in both directions. Nothing is unprotected.
- ⚠️ **The races mod ships 69 xenotypes, not 70.** The 70 written through C37 and its
  result block is off by one. 69 is the measured count, from the deployed defs.

## Config files

- **No config file waits for anything** — not RimSort, not game close. Owner ruling
  `0460ee4`, 2026-08-15. **Assemblies are the only exception**, because the OS locks a
  loaded DLL. This retires every "check whether RimSort is open" step.
