# Load B live verification — 2026-09-18

Bridge UP on full 635-mod list. BENCH holds lock; this agent is the one driver.

## A. Pyrelands density read-back (PYRELANDS_DENSITY_TRIPLE_1) — PASS
Live `jawa/get_defs BiomeDef/RM_FE_Pyrelands` (game at Entry scene, defs loaded in memory):
- plantDensity = **3.0** (EXPECTED 3.0, not 1.0) PASS — enforcer confirmed live
- wildPlantRegrowDays = **9.0** (EXPECTED ~9) PASS
- animalDensity = 2.1
Def defName: RM_FE_Pyrelands, label "the Pyrelands", mod Pyrelands / mandrake.rm.pyrelands.
Read-back via bridge (not disk XML).

## B. PaleTree re-proof (ROT_PALE_TREE_1) — BLOCKED (no map loadable)
Cannot spawn RUT_PaleTree: no map exists and none can be created — see the load blocker below.
Baseline captured before attempts: Player.log 39964 lines, 2 MissingMethodException (the known
pre-fix startup pair), 0 "Could not instantiate or initialize a ThingComp". No new comp-init
errors were produced, but that is because no spawn ever ran, NOT a pass. UNVERIFIED.

## C. Vegetation screenshot (PYRELANDS_DENSITY_TRIPLE_1) — BLOCKED (no map loadable)
No Pyrelands map could be loaded or generated — see load blocker. No screenshot produced.

## D. FireHawk review save — BLOCKED (save will not load)
`rimworld/load_game PYRELANDS_REVIEW_20260918` returns success:queued, then CRASHES during load.
No screenshot produced. Save file NOT modified (only a load was attempted; no save_game called).

## LOAD BLOCKER (root cause for B/C/D) — game cannot construct a Game object
Game was found at the Entry scene (main menu): programState=Entry, hasCurrentGame=False,
mapCount=0. Bridge UP (326 companion tools, 451 total). Defs loaded in memory (A succeeded).

Every attempt to load a save OR start a quicktest throws a deterministic NRE inside `new Game()`:

  System.NullReferenceException
    at Verse.GenTypes.SameOrSubclassOf (Type baseType, Type parentType)
    at Verse.GenTypes.SameOrSubclassOf[T] (Type baseType)
    at RimWorld.ReadingPolicyDatabase.GenerateStartingPolicies () [0x0003e]
    RimWorld.ReadingPolicyDatabase..ctor()
    at Verse.Game..ctor () [0x000c2]
      (postfixes: vlvop.tormentmaster.expansion Game_Ctor_* patches)
    at Verse.GameDataSaveLoader+<>c__DisplayClass30_0.<LoadGame>g__PreLoadAct|0 ()
    at Verse.LongEventHandler.RunEventFromAnotherThread (Action action)

Evidence: 2/2 load_game attempts + 1 auto quicktest all hit the identical NRE
(Player.log lines ~40022, ~40046, ~40077, growing 39964 -> 40100). A null Type in the
reading-policy type list makes GenTypes.SameOrSubclassOf dereference null, so
`ReadingPolicyDatabase..ctor` (called by every `new Game()`) throws before any save data is read.
This blocks EVERY save load and EVERY quicktest on the current 635-mod configuration.

Notes:
- Initial load "queued" but did nothing for ~5 min because the game window was unfocused and
  not ticking (run-in-background stall). game_focus.preflight() (handle 67114) fixed the tick;
  the load then ran and revealed the NRE. So the NRE, not the stall, is the real blocker.
- A reboot would reload the same mod set and reproduce this (config-level def/type defect),
  so I did NOT reboot and did NOT touch the mod list. This needs a def/mod-side fix + restart.
- Did NOT modify any save. Did NOT call save_game. Bridge left UP; game left at Entry.

## Summary
- A: PASS — RM_FE_Pyrelands live plantDensity=3.0, wildPlantRegrowDays=9.0, animalDensity=2.1.
- B: BLOCKED (no map). C: BLOCKED (no map). D: BLOCKED (save will not load).
- Root cause: ReadingPolicyDatabase.GenerateStartingPolicies NRE in Game..ctor — no map can
  be created on this mod configuration. Not fixable from the bridge; needs a def/mod fix + reload.
