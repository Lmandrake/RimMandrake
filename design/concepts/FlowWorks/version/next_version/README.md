# FlowWorks: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

*No open judge gap was sorted here.* Four entries are here by his word:

## RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION (FlowWorks 0.2.0, owner by card 2026-11-13)
- **Decided:** owner by card 2026-11-13, 10:12 PM PST, asked where the dig interface redesign belongs: *"All in the next version"* (OWNER:1794636834064875208). The whole redesign, the 40-entry depth menu included, is Divergent; it moves no 0.1.0 bar.
- **What:** design the dig interface and consolidate the controls for dig, repair, fill in and the rest; input `design/specs/2026-11-13-flowworks-dig-interface-census.md`. The dig-speed target ("it's slow") is a question inside this design.
- **Acceptance test:** none yet, design with him (as filed).

## RIMMANDRAKE_DESIGN_MELEE_SHOVE_INTO_PIT_CONTEST_FLOWWORKS (FlowWorks 0.2.0, owner by card 2026-11-14)
- **Decided:** owner by card 2026-11-14, about 2:10 PM PST, asked when the melee shove into a pit should be designed: *"Next FlowWorks version"* (OWNER:1794694163670985006). Divergent, FlowWorks 0.2.0; it moves no 0.1.0 bar.
- **What:** one pawn shoves another into an open pit, a contest of both masses and both melee skills or dodge.
- **Who, when:** his words 2026-11-13 09:55 PST, on Explosive Knockback's card: *"Melee shove is a great idea, but it belongs in FlowWorks, not here."* Filed to the ledger that day (target v1).
- **Why not 0.1.0:** the 0.1.0 vision has no pawn-on-pawn shove; adding it extends the vision (Divergent). It was filed before versions existed; he answered now-or-next by card 2026-11-14 (next).
- **Acceptance test:** none, design not yet argued (as filed).

## Wetting, four bars moved out of 0.1.0 (FlowWorks 0.2.0, owner by card 2026-11-14)
- **Decided:** owner by card 2026-11-14, about 9:43 PM PST, asked what 0.1.0 does about wetting: *"Move wetting to 0.2.0: the wetting bars leave 0.1.0 by his word and arrive in 0.2.0 with the thin film"* (OWNER:1794721673433243094). A change to a locked version by his card; journal, Conductor interventions, 2026-11-14 10:30 PM PST.
- **Why:** his ruling of 2026-11-14 12:01 PM PST, *"ALL game wetness should now migrate to a thin film"* (held row 2026-11-14#10f, `RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE`). A separate wetted state built for 0.1.0 would be work the film removes.
- **The bars, as they stood in 0.1.0** (full objects, with their tests, in `wetting_from_0.1.0.json` beside this file):
  - `inv_irrigation` (record.json inventory): ground within two squares of a filled canal is wetted (Stillsand's spilled-water technique); plants there have water and use it up; plants also drink standing flood water.
  - `canal_wets_two_squares` (tree leaf, experience): ground within two squares of a filled canal reads wetted and crops there have water; fast growth uses it up until the canal reapplies it; plants under a flood drink it down.
  - `wetting_is_not_flood` (tree leaf, experience): wetted ground is never drawn or behaving as standing water.
  - `wetness_probe` (tree leaf, instrument): a per-cell read of wetting level, cause and the water a plant drew.
  - Not moved: `d_wetting` (his words, a decision in `record.json`) and `exam.json`'s two wetting scenarios (a record of the exam taken at the lock).
- **The 0.2.0 Designer pass owes:** reconcile these bars with the thin film. `wetting_is_not_flood` ("never standing water") and a film may disagree; that is the pass's question, not settled here.
- **Build items now aimed at 0.2.0:** `FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP`, `FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST` (ledger notes 2026-11-14 10:30 PM PST); both follow the design pass `RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE`.
- **Acceptance test (written for 0.1.0's wording, red as intended):** `python3 src/RimMandrake/FlowWorks/selftest_stage3_owed.py --only wetting` and `--only wetness_probe`; live `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_wetting --out <json>`, UNRUN. The 0.2.0 pass rewrites them to the film.

## RIMMANDRAKE_REBUILD_SWALE_AS_SOAKING_FLOOR_NOT_FURNITURE (FlowWorks 0.2.0, owner by card 2026-11-14)
- **Decided:** owner by card 2026-11-14, about 9:47 PM PST, asked which version the swale rebuild belongs to: *"Next version, 0.2.0; 0.1.0's bars do not move"* (OWNER:1794721683744408896). Divergent; it moves no 0.1.0 bar.
- **What:** `RM_Swale` rebuilt as a floor tile that soaks water fast and turns nearby ground to fertile soil, not a Building (his look 2026-11-14, row 4: *"The Swale should be a floor-tile type that encourages rapid water absorption and transforms nearby terrain to fertile soil, not a weird metal slide-looking piece of furniture."*).
- **Why not 0.1.0:** no 0.1.0 bar names the swale; its soaking is wetness, which his thin-film ruling moves to 0.2.0.
- **Acceptance test:** on the item (offline: `RM_Swale` is a TerrainDef with a designation category and no Building ThingDef of that name; nothing references the old ThingDef; a selftest shows a swale cell soaking faster than plain soil and upgrading adjacent sand).

## The raid proof, moved out of 0.1.0 (FlowWorks 0.2.0, owner, typed 2026-11-23)
- **Decided:** owner, about 11:05 PM PST: *"Can we move the raid item in Flowworks into the next version and handle it then, so FlowWorks can pass otherwise now?"* (OWNER:1795504867390195471). The Conductor answered yes. Earlier that night he paused raid tests until better tools exist, and said of FlowWorks that testing raiders on ladders and moats *"is a real need"*.
- **lost:** FlowWorks 0.1.0 passes with no real raid ever assaulting a moat, trench, island or pit; the walker scenes show that pawns path, cross and climb, not that raider AI chooses to.
- **undo:** move the listed bars and scenes back from next_version into the 0.1.0 locked bars and test table and re-pin.
- **Bars moved** (full objects, as they stood, with their scenes, tests and file lists, in `raid_from_0.1.0.json`):
  - `moat_raid_sequence` (leaf): raiders swim the moat, are held when it drains, are taken from the rim, and the moat burns round them. The part that needs no raider stays in 0.1.0 as `moat_drains_and_burns` (`sc_moat_walkers`, `sc_hole_prison`, `sc_sluice`, `sc_toss_flame`).
  - `raiders_fetch_their_fallen` (leaf) and `inv_raider_fetch_fallen` (inventory): the rest chop a ladder and go down for their fallen, and leave them when driven off. The code is built and ships in 0.1.0; its offline test `T_FETCH_FALLEN_OFFLINE` stays in the 0.1.0 table as support of `inv_pit_access`.
  - `raiders_shelter_only_where_they_can_climb_out` (the raider clause of `trench_gives_cover` and `inv_trench_cover`): raiders shelter only in trenches they can climb out of, never in a cage-like pit. The cover stays in 0.1.0 (`sc_trench_cover_pawns`).
  - `raiders_break_a_winch_and_escape` (the raider clause of `island_bridges_trap_and_fail`): raiders trapped on the span go for a winch, break it and escape; the defence still counts. The trap, the dropped leaf and the way off stay in 0.1.0 (`sc_islands_walker`).
- **Scenes moved:** `sc_moat_raid`, `sc_trench_cover`, `sc_islands`, `sc_pit_trap_raid`, `sc_fetch_fallen`, and the showcase `pit_trap`. Their staging code and offline selftests stay in `src/RimMandrake/FlowWorks/northstar/`.
- **Open fault that comes with them:** `RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT` (visit 9, seen in 1 of 3 valid runs of `sc_moat_raid`; its cause is unknown). A held pawn that climbs out of a drained moat would also break the 0.1.0 bar `ways_in_and_out`; no scene of 0.1.0 has shown it.
- **Waits for:** the test tools that can hold a raid still (`design/specs/2026-11-23-bridge-v2/`); `raid_pause.py lift`.
- **Acceptance test:** `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_moat_raid --out <json>`, and the same with `scene_trench_cover`, `scene_islands`, `scene_pit_trap_raid` and `scene_fetch_fallen`: every row PASS. While raid tests are paused each reads PAUSED.

## The test hooks go into FlowWorks (rimflow `RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION`)

- **Proposed by:** the Bridge v2 build order (`design/specs/2026-11-23-bridge-v2/06_build_order.md`, "first use in Explosive Knockback and FlowWorks when each next advances"), filed 2026-11-24 6:41 PM PST by the ticket that built the hooks.
- **What:** compile `src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs` into `src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj` (its RELEASE build too); an `[RMReset]` and an `[RMDigest]` hook over the per-scene state that the mod keeps (the builder lists each static cache, counter and pending callback first); `RMTrace.Emit` at the branches that a scene must tell apart, first in `sc_moat_raid` and the ordered rescue. Contract and rules: `design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md`.
- **Why not now:** a mod converts its scenes when it next advances, as a planned change of its next version; no current bar moves. The hooks are test apparatus: they add no bar and no player-facing behaviour. A helper's recommendation: the version in which this mod's scenes move onto the scene library. The Conductor decides the version at filing.
- **Acceptance test:** live, `jawa/mod_hooks action=list` lists the mod with build `RELEASE`, `trace` yes, a reset hook, a digest hook and no problem; `action=prove step=clean`, one scene act that dirties the state, `step=dirty` reads `digestProven` true; `action=reset` then reads `verified`. Offline: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_test_hooks.py` stays green. Red at filing: the mod's csproj does not compile `RMTestHooks.cs`.
