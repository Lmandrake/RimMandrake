# FEVERWOOD_ANT_THEFT_RAIDBACK_1 — the kurreth carry thornbugs off alive, and the column can be tracked and raided back

Caused by `FEVERWOOD_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.feverwood` (content) and
`mandrake.rm.environmentalhazards` (the generic haul kit). Design: `feverwood_bedazzle_review_2026-10-02.md`
§1 ("The ants do not steal"), §4 row 0, §8; sheet `the_fever_wood.md` §4: *"Ant raids haul thornbugs away
ALIVE: theft, not slaughter… so every loss is a recoverable quest: track the column, raid it back."*
Ruling: **build first: land the decided work plus the giant's story** (decision taken by question card
2026-10-02 11:12 PDT). Wave-1 scope already named *"lord wiring, raid-back quest"* (2026-09-24 card,
`FEVERWOOD_RM_MOD_BUILD_1`, closed without it).

## What exists (read before building)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_HaulVictimAIUtility.cs`: the victim-finder (a
  `KidnapAIUtility.TryFindGoodKidnapVictim` generalised with a caller predicate; requires the victim already
  Downed). Its header: *"NOT done here: the LordJob/LordToil that would actually call this … and the
  'unclamp stun' attack job"*.
- `RM_JobDriver_StunVictim.cs` (the unclamp stun) and `RUT_HaulPawnAndExit.cs` (`JobDriver_TakeAndExitMap`
  with `JobDriver_Kidnap`'s FailOn).
- The lure raid: `RM_MapComponent_TwoFrontLure.cs` l.203 runs
  `LordJob_AssaultColony(faction, canKidnap: false, canTimeoutOrFlee: false, canSteal: false)`.
- The hive: `RM_GenStep_AntHiveDungeon`, `RM_MapComponent_AntHive` (`FEVERWOOD_ANT_HIVE_DUNGEON_1`).

## spec

1. **A theft LordJob** `RM_LordJob_KurrethTheft` (crib `LordToil_KidnapCover`'s shape): toils assault →
   stun (`RM_JobDriver_StunVictim` on a target from `RM_HaulVictimAIUtility` with a predicate for thornbugs
   first, then any tamed sap-sucker: `RM_Thornbug`, the vaulm, ollareth, drommath) → haul off alive
   (`RUT_HaulPawnAndExit`) → the rest exit. The victim is never killed by the theft itself (stun damage
   only; a victim that would die is dropped instead). Every kurreth raid uses it, including the lure's first
   front: change l.203's call (or its successor) so the kurreth raid steals. The lure's skreth front stays a
   plain assault (the brood kills; the ants steal: the sheet's contrast).
2. **No silent vanishing** (the 2026-09-29/30 rule: no animal or pawn ever vanishes without a readable sign):
   a letter naming each animal taken and the direction the column left; a ground track (filth or a
   designator-visible trail, existing defs first) from the exit cell.
3. **The raid-back:** when a stolen animal leaves the map, a site appears on the world map (a
   `QuestScriptDef` `RM_Quest_KurrethColumn`, read the `rimworld-quests` skill first): a column camp within a
   few tiles, holding the stolen animals alive (downed-and-bound or penned), guarded by kurreth. Recover them
   by raiding the camp; ignored for a fixed time, the column reaches its hive and the animals are carried into
   the nearest hive dungeon (`RM_MapComponent_AntHive`), still recoverable there and gone only if the hive is
   left for a long while (letter when that happens). All timers `// INVENTED` and in Mod Settings.
4. **Mod Settings:** `antTheftEnabled` (off = today's plain assault), the column timers, the hive hold time.
   Every field read by the code it claims to gate.

Depends on: `FEVERWOOD_ANT_HIVE_DUNGEON_1` (soft: the hive leg of the raid-back; the camp leg stands alone).
Tested beside `FEVERWOOD_RM_CAST_COMPLETION_1` (the lure's two fronts). Tier note: `RUT_HaulPawnAndExit` is a
`RUT_` name in a free mod, listed on `BIOME_TIER_CLEANUP_1` (c); rename it there, not here.

## criteria

Deterministic, scriptable, recorded as cases in `FEVER_WOOD_FIRST_SCRIPT_1`'s `validation.py`:
- `jawa/get_defs` `QuestScriptDef/RM_Quest_KurrethColumn`: `foundCount` 1 (reading `success`/`foundCount`).
- Source read: no `LordJob_AssaultColony(` call for the kurreth faction remains with `canKidnap: false,
  canSteal: false` as its only route; `RM_LordJob_KurrethTheft` exists and calls `RM_HaulVictimAIUtility`.
- Live, on a quicktest map with 3 tamed `RM_Thornbug`: a debug kurreth raid using the theft LordJob; after the
  raid ends, (a) the count of `RM_Thornbug` pawns with `Dead` = true is 0, (b) at least one thornbug is not on
  the home map and is held by the quest's site (world object read: its `Map`'s pawns include that thornbug's
  `thingIDNumber`, or the quest's `QuestPart` lists it), (c) a letter of the theft letter def was received
  (`Find.LetterStack` read).
- Raiding the site and returning: the thornbug with the same `thingIDNumber` is back on a player map, alive.
- With `antTheftEnabled` off, the same raid kills or ignores but never removes a thornbug from the map.
