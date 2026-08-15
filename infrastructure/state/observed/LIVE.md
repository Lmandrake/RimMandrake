# LIVE.md — facts you would otherwise need a running game to learn

Published by CHECK. One line per fact. Superseded lines are replaced, not appended to.
Everything here was read out of a running game or off an artifact a running game wrote.

## The def dump

- **Current dump: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump`,
  captured `2026-08-15T15:10:11Z` (08:10 local), `mode: all`, game `1.6.4871 rev591`.**
  576 mods, 529 files under `defs/`, `animals.json` alongside. Taken during the C37
  load, so it carries `mandrake.starwarsraces` and does NOT carry the three donors
  (`btd.xenotyperemix.starwars`, `guy762.starwarsxenotypes`,
  `neronix17.outerrim.galacticdiversity`).
- 🔴 **FRESHNESS HAS TWO AXES AND THEY DISAGREE RIGHT NOW: fresh in TIME, stale in SET.**
  The dump holds **576** mods; `ModsConfig.xml` `activeMods` holds **575**. The single
  difference is `regrowth.botr.boilingforest`, deprecated at 11:58 — *after* the 08:10
  dump. Direction matters: the dump is a **superset**. Nothing that loads is missing from
  it, so a patch onto a live def is checked correctly; but the dump still describes defs
  from a mod that **no longer loads**, so an xpath onto one of those **validates clean and
  silently no-ops in game**. `refresh.py`'s STALE verdict is right and should be believed.
  Live instance: `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\JawaWorld_BiomeMix.xml:140`
  carries `<RG_BoilingForest>` — the only BOTR reference left in `Jawa_Patches`.
  ⇒ **"The dump is from today" is not the same claim as "the dump matches what loads."**
  I asserted the second from the first on 2026-08-15 and it was wrong; REP caught it.
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

## The def dump's blind spots

- 🔴 **79 of the 529 def-type files in the dump are EMPTY** (`"count":0`), so for those
  types **"absent from the dump" says nothing about the game.** `AbilityDef` is one of
  them — zero rows — which is why all 16 ideo-role ability references in
  `The Salvation.rid` come back UNMEASURABLE rather than missing. Others in the list:
  `AbilityAIDef`, `CharacterDef`, `FactionEnlistOptionsDef`, `FaceTypeDef`, `PatchDef`,
  `PawnBioDef`, and 72 more. Full list: rerun the counter in
  `src/RimMandrake/Utils/validate_save_artifact.py --rebuild-index`.
- ⇒ **A `--defs` check against an empty def type is UNMEASURED, not passed.** Give it
  its own word and its own exit code, or it silently reads as a green tick.
- 450 non-empty types, **79,575 defs**, 62,555 distinct defNames indexed.

## ModsConfig.xml

- **The active-mod count is 575** (`activeMods`), read 2026-08-15 11:58.
- ⚠️ **Counting `<li>` across the whole file gives 580 and is WRONG.** The file has a
  second list, `knownExpansions`, holding the 5 DLC ids, and they are duplicates of ids
  already in `activeMods`. Scope the count to inside `<activeMods>…</activeMods>`, or
  take the size of the *set*. A bare `grep -c '<li>'` overcounts by exactly the DLC count.

## Saved ideo / xenotype artifacts

- **`src/Jawa/ideoligion/The Salvation.rid` is CLEAN as of 2026-08-15**: 267 def
  references, **251 resolve, 0 dangling**, 16 UNMEASURABLE (all `AbilityDef`, the dump
  blind spot above). It carries **101 precepts** — not the 82 written in earlier notes.
- **`MandrakeJawa.xtp` is CLEAN**: 36/36 references resolve.
- Both carry a `<modIds>` provenance block of 585 mods, of which **11 no longer load**.
  That is **provenance, not a dependency list** — harmless on its own, and it matters
  only if a reference also fails to resolve. Neither file has one.
- ✅ **The 19 empty `<li>` entries are NORMAL and need no live check** — retracted, I
  raised them as suspicious and they are not. Vanilla `Technocracy.rid` has the same
  shape (22 empty in `hairFrequencies`, 11 in `beardFrequencies`): Scribe writes
  `<li />` for a default-valued entry. Compared directly, game down, 2026-08-15.
  ⚠️ Also note `hairFrequencies`/`beardFrequencies` carry `<vals>` with **no `<keys>`**
  in BOTH files — that too is the normal shape, not a lost def reference.
- The tool: `python3 src/RimMandrake/Utils/validate_save_artifact.py <file>`.
  `validate_ideoligion.py` CANNOT read these — it answers `no religions found` and
  checks nothing.
- 🔴 **A clean run is necessary, not sufficient.** It proves no dangling names. It does
  NOT prove the ideo loads. Only the live dialog does that.

## Config files

- **No config file waits for anything** — not RimSort, not game close. Owner ruling
  `0460ee4`, 2026-08-15. **Assemblies are the only exception**, because the OS locks a
  loaded DLL. This retires every "check whether RimSort is open" step.
