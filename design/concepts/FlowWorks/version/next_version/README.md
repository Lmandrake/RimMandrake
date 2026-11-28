# FlowWorks: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

*No open judge gap was sorted here.* The entries below are here by his word:

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

## RIMMANDRAKE_FIND_STAR_WARS_JUMP_PACK_ELSE_MAKE_ONE_BLACKSTAR_WEARS: raiders are dressed from jump gear by capability (FlowWorks 0.2.0)

- **Decided:** owner, 2026-11-24 about 11:15 PM PST (ledger note on `RIMMANDRAKE_RULE_RAIDER_JUMP_PACKS_THE_SHIP_LIST_CUTS`): *"The jump pack should NOT be cut for FlowWorks, it was a RimStarWars decision/setting specific decision."* *"Raiders having a jump gene could also of course cross that way."* FlowWorks keeps raider jump packs and stays setting-free. The brief of the item names this a 0.2.0 change; it moves no 0.1.0 bar.
- **What is already by capability (no change):** the crossing itself. `RM_RaiderTrench.TryGetJump` takes any worn apparel with a usable `Verb_Jump` and any castable `Verb_CastAbilityJump` ability (the longjump-legs gene and its kin).
- **What changes:** the dressing patch `RM_Patch_Raid_JumpPacks` (`Source/Superdeep/RM_RaiderTrench.cs`) reads one def, `GetNamedSilentFail("Apparel_PackJump")`. The ship cut list cuts that def, so on the Star Wars setting no raider is dressed, though three Star Wars jetpacks with `Verb_Jump` load from `mandrake.rsw.armoury` (`guy762_Jetpack_light`, `guy762_Jetpack_heavy`, `guy762_Jetpack_missile`; measured in the def capture of 2026-11-24T15:48Z). The patch is to build its candidates once from `DefDatabase<ThingDef>` (apparel whose verbs hold `Verb_Jump` or a subclass; a cut def is not in the database), dress nobody when the list is empty, pick per raider with a pure `RM_RaiderTrenchMath.PickJumpGear(id, n)`, and skip a pick that the raider cannot wear without dropping something. A choice for the 0.2.0 Designer: prefer gear at or under the raiding faction's tech level.
- **Why not now:** FlowWorks 0.1.0 is in Stage 6 (in-game acceptance); a Divergent change enters the next version at Stage 1 (`design/specs/2026-11-13-maturation-pipeline.md`). The raider bars are in 0.2.0 already (the raid proof entry above).
- **Acceptance test:** `python3 src/RimMandrake/FlowWorks/owed_0_2_0_raider_jump_gear.py --dotnet`: exit 0 (the build that makes it green renames it `selftest_flowworks_raider_jump_gear.py`, so the selftest run finds it). RED today (exit 1: A1 a def named by literal, A2 no candidates from the loaded defs, A3 no empty-list return, A4 no pure pick; B owes 3 or more SelfTest cases `RaiderTrench_jump_gear_*`). Seen GREEN on a planted patch, offline, 2026-11-24. Live, UNRUN while raid tests are paused: on the FlowWorks small list plus `mandrake.rsw.armoury`, with `Apparel_PackJump` cut, a raid of an industrial-or-better faction on a map with a dug trench arrives with some raiders in a Star Wars jetpack.

## RIMMANDRAKE_DEEPEN_FLOWWORKS_PIT_LOOK_HE_SUSPECTS_READS_SHALLOW: a pit looks as deep as it is (FlowWorks 0.2.0, owner 2026-11-24)
- **Decided:** owner, 2026-11-24 (ledger note on the item, his approval of the stepped-pit and `RM_PIT_DEPTH_LADDER_AFTER` looks for 0.1.0): *"please file a ticket for the NEXT version that we need to make pits look as deep as they are... they read way too shallow compared to their actual look (I suspect). But for now both of these looks pass."* Divergent; it moves no 0.1.0 bar.
- **Measured (2026-11-25, `design/specs/2026-11-25-pit-reads-as-deep/`):** his suspicion holds. For 3x3 pits of 2 to 16 m, no drawn cue shows more than about 1.7 m: the north face is shorter than a colonist beside it at every depth (a 16 m face reads as 0.9 m), the cast shadow is 5 to 9 times shorter than the sun's, and 77 to 88% of the floor stays in view where the colonist's own scale hides it past about 4 m. The scale rests on one capture and an assumed 1.75 m person.
- **What:** design and build a pit look that reads its depth, and keeps a trapped pawn and liquid on the floor in sight. Directions in the spec's README: a true cast shadow (depth / tan of sun elevation, his Direct Sun principle) and less sky at the bottom are recommended; a taller, banded north face is the third. The art judge picks among mocks; he judges the result.
- **Proposed bar (the Designer adopts or rewrites it at Stage 1):** at default zoom by day, a player who sees a dug pit beside a standing colonist puts its depth in the right band without reading a number (shallower than the colonist, a few colonists deep, or a deep shaft), and a pawn or liquid on its floor stays in sight.
- **Acceptance test:** none, a look he judges at his walk (as filed). The instrument for before and after: `python3 design/specs/2026-11-25-pit-reads-as-deep/measure.py` (its `--check` exits 1 when the offline twin drifts from the C# build, so a changed look must update the twin to be measured).

## Caller scenario tests from the mined live bugs: fw_melee_across_lip, fw_raid_stall_reach

- **What:** two offline scenario tests of the pit melee caller `RM_PitReach` (`src/RimMandrake/FlowWorks/Source/Superdeep/RM_Patch_PitLipMelee.cs`). The scenarios run on real game types, after the pattern in `design/RimMandrake/2026-11-07-pocock-design/pilot_realtypes/`. The live record holds both as caller bugs (`design/RimMandrake/2026-11-07-pocock-design/06-mined-live-bugs.md`). The scenarios follow the owner's rule of 2026-11-23, `RIMMANDRAKE_ENACT_PIT_MELEE_REACH_EQUALS_CLIMB_SIZE_DECIDES`: melee across a pit's edge works exactly when the attacker's body could take that step.
  - `fw_melee_across_lip` (`RM_PitReach.Strikes`): a man-sized raider on a pit floor deeper than his climb limit cannot strike a pawn on the lip, and a body that could take the step can.
  - `fw_raid_stall_reach` (`RM_PitReach.WorthAttacking`): a melee raider whose only colonist is across a pit that he cannot strike across picks a reachable target or none, so the raid does not stall.
  - Dropped as stale: `fw_trapped_target_pick` (drafted archers held their fire on a pit raider until his first real attack). The 2026-11-23 reach rule replaced that behaviour. Today's code has no such gate.
- **Who, when, why not now:** the owner adopted the scenario policy by card 2026-11-08 ("Policy plus real-types pilot"; item `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL`, `design/RimMandrake/2026-11-07-pocock-design/06-mined-live-bugs.md` §Seed set). The seed is a live-found caller bug: its fix is on the build, and no offline test reads the caller. It moves no bar of the current version. It adds a cheaper regression check beside the live scene that decides the bar today. The Conductor decides at filing whether it stays here (recommended: next version).
- **Acceptance test:** both scenarios run offline from the mod's tests. `maturation.py red-seen FlowWorks <test id>` records each one red on a planted fault in `RM_PitReach` (the depth comparison inverted), and green on the build.

## Build where the water already stands, and swim out to the work (from BRIDGES_DIG_DESIGN_THREE_WAYS_EACH)

- **What:** let a player place and build where water already stands (deep water has no vanilla affordance, so this needs our own placement rule). Builders reach such a site by swimming or from footing beside it, and the job does not thrash or drown them.
- **Who, when:** his words 2026-10-25 (BENCH ledger, BRIDGES_DIG_DESIGN_THREE_WAYS_EACH): *"Gotta think about building where it's already underwater too: we should just let that happen, it needs to happen. But need to think about people swimming out to worksites to make sure it doesn't break anything."* Ground analysis of that day: `D:\ClaudeWork\rimmandrake\design_bridges_dig_20261024\GROUND_TYPES_ANALYSIS.md` (swim risk: job thrash and drowned builders; recommends building from footing).
- **Why not 0.1.0:** no 0.1.0 bar names building in standing water. The other three areas of that design ticket were built and closed (SUSPENSION_ISLANDS_BUILD_TOWERS_COST_PLENTY, DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY, PIT_DIG_FIX_SAND_SLIDES_BACK_IN, the one-drag drawbridge); this part was carried by nothing (searched 2026-11-26). It extends the vision (Divergent). The Conductor decides at filing whether it stays here (recommended: next version).
- **Proposed bar (the Designer adopts or rewrites it):** a player can order a structure built on a square of standing water; a colonist reaches it, builds it and comes back without drowning or abandoning the job.
- **Acceptance test:** none yet, design not argued (the Designer writes it with the bar).

## Ledger tickets held for 0.2.0 (Work Bundle WB-mod-FlowWorks-20261126-113858, 2026-11-26)

- **What:** each ticket below stays open in the rimflow ledger, with its own spec and history (`rimflow show <ID>`); this list is where a 0.2.0 Designer pass finds them. None moves a 0.1.0 bar.
- **Why not 0.1.0:** the FlowWorks ticket sweep of 2026-11-22 (`design/concepts/FlowWorks/ticket_sweep_2026-11-22.md`) classed each KEEP_NEXT, or the owner's own words put it in v2 (target v2 on the ledger).
  - `DIG_RIG_BUILD_BUCKET_OVER_THE_PIT`, `FOUNTAIN_SCULPTURES_DESIGN_WATER_MEETS_ART` and `SIEGE_RAID_BUILD_SHELLS_OVER_THE_PIT` no longer stay open: the three tickets are pure v2 ideas, and each is closed with its whole text in the section "Three v2 ideas moved from tickets" below (2026-11-26)
  - `DROWNING_ESCAPE_FIX_READS_DECK_ABOVE`, `INDUSTRIAL_RUINS_FIX_HIDDEN_EH_DEPENDENCY`, `REFUSED_HANDOVER_DRAIN_FIX_PUDDLE_OVERSTAYS`, `RIMMANDRAKE_REFUSE_PITS_IN_LOOSE_GROUND_EVEN_BY_BRIDGE`, `RIMMANDRAKE_SHORT_DROWNED_ELECTRONICS_LIKE_RAIN_DOES`, `WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS`, `RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE` (sweep KEEP_NEXT)
- **Acceptance test:** each ticket's own.
- Also held for 0.2.0 (same bundle, 2026-11-26): `RIMMANDRAKE_ANIMATE_POUR_SPILL_SHEET_ARRIVES_ALL_AT_ONCE`. The dev pour's overflow still lays its whole spill in one call (`RM_SheetMath.ResolveSpills` fills each lip square to the sheet cap, nearest first). His walk of 2026-11-25, station 75, put how liquid sheets on the ground look and flow in the next version: "NEXT VERSION we need to do a LOT of work on what all the differnt fluids look like as thin sheets on the ground, how they flow, etc." (`RIMMANDRAKE_DESIGN_FLUID_THIN_SHEETS_TAR_SHOWED_MISTY_GREY`). A spill that grows ring by ring over time belongs to that design.
- Also held for 0.2.0 (same bundle, 2026-11-26): `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP`. Its owed criterion A3 (raiders breach a 4 m trench by fill; FAILED as MOD on 2026-10-24, r52.json, never re-run) is raider AI under a real raid: the raid proof moved to 0.2.0 by his words of 2026-11-23 (section above), and the raid pause stops its test.

## Three v2 ideas moved from tickets (FlowWorks 0.2.0, moved 2026-11-26)

Each of these three ledger tickets held only an idea: nothing built, no failure, no test. Each ticket was closed with the reason that this section keeps it, so the text of each ticket is whole here. All three are Divergent additions for FlowWorks 0.2.0. The table of the move: `design/pre_design_concepts/moved_2026-11-26.md`.

### DIG_RIG_BUILD_BUCKET_OVER_THE_PIT (v2, owner 2026-10-22)
- **Title (ledger):** "v2: a buildable dig rig (winch-and-bucket frame over a pit, operated by a colonist) that digs past the 2 m colonist cap; design start: design/RimMandrake/machine_dig_2026-10-21.md".
- **His words** (OWNER `file` event, 2026-10-22T06:06:58Z, kind build, filed target v1, for FOUNDRY): "v2 has the buildable dig rig, for Utinni it's droids and labour mechs".
- **Retarget** (OWNER, 2026-10-23T11:34:27Z, per ruling `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL`): to v2, with the reason "owner 2026-10-22 (DEEP_DIG note tsn 1792649216327168525): 'v2 has the buildable dig rig, for Utinni it's droids and labour mechs'; the item's own title says v2 but it was filed target=v1".
- **Prose of the ticket:** the spec line is the title above. "What is left: proposed: nothing recorded as owed beyond the title." (The item file was restored 2026-11-12 from the ledger, by `RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE`.)
- **Owner of the ticket:** BENCH from 2026-10-23: "Please redirect those FlowWorks actions back to Bench. I want Bench owning all Flowworks from now on to prevent mutual waiting." (OWNER, 2026-10-23).
- **Sweep:** CONDUCTOR, 2026-11-23T00:46:37Z, "FlowWorks ticket sweep 2026-11-22: KEEP, FlowWorks 0.2.0 (next version; moves no 0.1.0 bar). Reading: Divergent addition, retargeted v2 by his note of 2026-10-22; not in 0.1.0 vision". Home `mod:FlowWorks`, group `pits-and-trenches` (2026-11-24).
- **Design start:** `design/RimMandrake/machine_dig_2026-10-21.md`. Related: `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` (for Utinni, droids and labour mechs).
- **Acceptance test:** none, an idea (no test was filed with the ticket).

### FOUNTAIN_SCULPTURES_DESIGN_WATER_MEETS_ART (v2 brainstorm, owner 2026-10-23)
- **Title (ledger):** "v2 brainstorm: artistic fountain sculptures (water spewing, counterpart to fire and glow sculptures) built on overspill".
- **His words** (OWNER `file` event, 2026-10-23T12:46:56Z, whole): "Now that we're building the ability for water to flow over the ground (overspill), We can do some really neat stuff fairly cheaply! We can make fountains! Beautiful artistic sculptures with water spewing out of them, the counterpart to the fire sculptures we had already invented or the glow sculptures. That's pretty spectacular! Please document this brainstorm idea for v2 development. In the meantime, we can do a small simple version in FlowWorks itself: simple fountains that allow their water to fall out and flow over the ground. The water can be captured in a surrounding ditch then pumped back to the fountain as a proof-of-principle of the entire flow cycle as well as a neat artistic piece. Please commission that as art and as a review sheet item to watch work."
- **Retarget** (OWNER, 2026-10-23T13:12:47Z, per ruling `FOUNTAIN_SCULPTURES_DESIGN_WATER_MEETS_ART`): to v2.
- **Prose of the ticket (whole):** "spec: `design/RimMandrake/fountain_sculptures_v2_2026-10-23.md`: what exists (sheet-water overspill, FlameStatues, deepfire-lacquer glow, sprinkler spray mote, net draw, pump return), the vision and roster, mechanics, dependencies, risks and five open questions for the owner. v1 proof: `FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN`. NEXT: brainstorm documented 2026-10-23; NEXT: (retargeted to v2 2026-10-23) when v2 opens, put the doc's section 6 open questions to the owner as question cards."
- **Sweep:** home `mod:FlowWorks`, group `fountains` (2026-11-24); held for 0.2.0 by the Work Bundle note of 2026-11-26T14:22:40Z.
- **When this version opens:** put the five open questions of section 6 of `design/RimMandrake/fountain_sculptures_v2_2026-10-23.md` to him as question cards.
- **Acceptance test:** none, a brainstorm.

### SIEGE_RAID_BUILD_SHELLS_OVER_THE_PIT (v2, parked, owner 2026-10-31)
- **Title (ledger):** "Siege raids come to launch weapons over deep pits (parked, v2: not built)".
- **His words** (OWNER `file` event, 2026-10-31T18:19:13Z, kind build, target v2, filed through the Conductor per ruling `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`): "Eventually siege raids will come to launch weapons over the pits to deal with it."
- **Prose of the ticket:** none (the ticket had no prose file).
- **Sweep:** home `mod:FlowWorks`, group `pits-and-trenches` (2026-11-24). It stages a raid, so its test waits for the raid pause (`raid_pause.py show`).
- **Acceptance test:** none, parked, not built.

## RIMMANDRAKE_DESIGN_FLUID_THIN_SHEETS_TAR_SHOWED_MISTY_GREY (FlowWorks 0.2.0, his walk 2026-11-25: "NEXT VERSION")
- **What:** the look and the flow of each fluid as a thin sheet on the ground. At station 75 poured tar spread as misty grey squares (picture `D:\ClaudeWork\rimmandrake\showings\FLOWWORKS_WALK3_20261125\8.png`). Folds in RIMMANDRAKE_ANIMATE_POUR_SPILL_SHEET_ARRIVES_ALL_AT_ONCE ("I wanted to watch the water bulge and move", 2026-11-12) and the thin-film wetness ruling of 2026-11-14.
- **Design draft (2026-11-27, Designer pass of work bundle WB-mod-FlowWorks-20261127-063415):** `design/specs/2026-11-27-fluid-thin-sheets/design.md`: the measured cause of the grey tar, one look source for pit and ground, pours that arrive over several pulses, per-liquid spread speed, proposed bars with their cheapest tests, and his open questions.
- **Acceptance test:** none, a design for his look (as filed); the draft proposes the 0.2.0 bars and tests.

## RIMMANDRAKE_DESIGN_TAR_SMOKE_AND_GAS_ON_THE_WIND (FlowWorks 0.2.0, his walk 2026-11-25)
- **What:** burning tar makes choking smoke that blows with the wind; gas that flows in the air with and without wind and sealed in rooms, and its effects. His words: "That's a big area likely for the next version of FlowWorks".
- **Design draft (2026-11-27, same pass):** `design/specs/2026-11-27-tar-smoke-gas-on-wind/design.md`: a FlowWorks-owned gas field beside vanilla's gas grid, one shared wind direction, one "smoke in the lungs" condition, proposed bars with their cheapest tests, and four questions for him with recommendations.
- **Acceptance test:** none, a design for his look (as filed).

## RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY (FlowWorks next version, by the Pyrelands 0.2.0 sort of 2026-11-26)
- **What:** heavy rain (black rain included) fills an open-sky tank and a dug moat or channel. His words 2026-11-13: black rain is "a rare chance to fill your moat against the fire and fill your water tanks". Today tanks fill only over the liquid net.
- **Why here:** the Pyrelands 0.2.0 sort (`design/concepts/Pyrelands/version/next_version/README.md`, entry "Black rain fills the moat and the water tanks") ruled it a water mechanic that works by its conditions, so it is FlowWorks' design work when FlowWorks opens its next version.
- **Acceptance test:** none yet, a Designer pass owes it (how much a heavy rain fills, a Mod Setting, a live look).

## Eight ledger tickets aimed at 0.2.0, listed here by the work bundle of 2026-11-28 (WB-mod-FlowWorks-20261128-020147)
- **Why listed:** each ticket names FlowWorks 0.2.0 in its own text, by his card or by the ticket sweep of 2026-11-22
  (RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE); the 0.1.0 work bundle refused each one for
  that reason and left it open on the ledger. Each ticket's text, acceptance test and merged older tickets are on the
  ledger (`rimflow show <ID>`). None moves a 0.1.0 bar.
- `RIMMANDRAKE_ADD_LIQUID_TIDE_MARK_SURFACE_REACTION_AND_BODY_UNDER_SURFACE`: parts B, C and D of the colonist-in-liquid
  look (tide mark, surface reaction, body under the surface); his card 2026-11-23, "A now, rest next".
- `RIMMANDRAKE_BUILD_FLOWWORKS_FOUNTAIN_LOOP_ART_FOR_ZERO_TWO`: the fountain that pumps its own rain, and its art pick.
- `RIMMANDRAKE_BUILD_FLOWWORKS_THIN_FILM_WETTING_FOR_ZERO_TWO`: wetting as the thin film (the wetting entry above).
- `RIMMANDRAKE_DESIGN_FLOWWORKS_WATER_WAVES_FOR_THE_NEXT_VERSION`: waves and ripples by depth; his card 2026-11-20,
  "Colour and clarity now", waves wait for 0.2.0.
- `RIMMANDRAKE_DESIGN_PIT_FLOOR_SOILS_FOR_GROWING_RIVER_MUD_IS_RICHEST`: soil types on pit floors, so a pit can be grown in.
- `RIMMANDRAKE_PIN_FLOWWORKS_FOUR_UNWATCHED_LAWS_FOR_ZERO_TWO`: tests that pin toss range and relight, the fetch-fire
  window and key, drill power when off, and coating on colonists.
- `RIMMANDRAKE_REDRAW_FLOWWORKS_FOUR_PLACEHOLDER_ARTS_FOR_ZERO_TWO`: the gravel pile, the geyser plume bubble, the Modern
  reel tail colour, and style icons in every look menu.
- `RIMMANDRAKE_SHOW_TANK_FILL_LEVEL_AND_LIQUID_COLOUR_ON_ITS_SIDE`: every tank shows its fill and its liquid's colour on
  its side ("a must by his words").

## Two more ledger tickets aimed at 0.2.0, listed by the restart of the same work bundle (2026-11-28)
- **Why listed:** the ticket sweep of 2026-11-22 classed each one as FlowWorks 0.2.0 (next version; moves no 0.1.0 bar),
  and the 0.1.0 work bundle WB-mod-FlowWorks-20261128-020147 refused each one for that reason and left it open on the
  ledger (`rimflow show <ID>`).
- `GRAVSHIP_LOCKED_FIX_ENGINE_TURNS_THEM_ANYWAY`: a turned gravship turns 14 non-square buildings that say
  rotatable=false (8 are FlowWorks' 3x2 Desal Plant, Detox Works, Pumping Station and Tar Refinery, kludged and repaired),
  so they land in a facing the def never drew. Needs per-facing art and ports. Done when `gravship_rotation_audit.py
  --check` passes with none of them in `gravship_rotation_owed.json`.
- `RIMMANDRAKE_DESIGN_NATURAL_WATER_AS_PITS_NOT_FLAT_PONDS`: his decision of 2026-11-12, a full conversion of still
  natural water to filled pit basins with a bottom altitude map (fishing, aquatic growing and swimming kept); rivers are
  the one open point. His by-card answers on edge lakes, wet-biome lakes and drought are on the ticket. A redesign with
  him, not a 0.1.0 bar.
