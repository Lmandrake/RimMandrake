# RimMandrake: Utinni - Waste Run - validation walk
subject: src/RimUtinni/WasteRun  (packageId `mandrake.rut.wasterun`)
deps: mandrake.rm.warcasket (RM_CaskBay, Wastepack, RM_HalfExtractedCore) + Royalty (Empire faction)
list: `warcasket` tier plus this mod (modset_builder.py --list)
status-hint: WARCASKET_WASTE_RUN_REMAINDER_1, WASTE_RUN_STUBS_1 - one gravship waste-run quest where the destination chosen at the cask bay is the branch: Empire, cold side, Assailants, propane lakes, Slime experiment

Script: `src/RimUtinni/WasteRun/validation.py` (modcheck Suite; `python3 validation.py` runs the offline static half).

## must be true
- Every shipped def resolves: `RUT_WasteRun`, `RUT_WasteRunOffer`, the seven `RUT_WasteRun*` history events and the seven `RUT_WasteRunMood_*` memories; `RM_CaskBay` gained `RUT_CompProperties_WasteRunPlanner`. → defs_and_load.defs_resolve, defs_and_load.absent_def_is_refused, defs_and_load.cask_bay_gained_planner_comp
- Each of the five destinations has exactly one quest branch listening on the signal the cask-bay command sends (`WasteDest_<Name>`); the quest records only defined history events; every C# file is in the csproj. → static_checks (offline)
- Every Mod Settings field (master, offer, five destinations, four consequence switches, Throat cask) writes, reads back and restores. → settings_roundtrip.*
- The run is offered only with waste in a cask bay, the master and offer toggles on, and no run active. → UNCOVERED: needs a placed cask bay holding a Wastepack and a bridge call that fires the incident through its worker (`jawa/fire_incident`); filed WASTE_RUN_SIGNAL_DEBUG_HOOK_1
- Choosing a destination at the bay destroys all cask-bay waste and ends the quest Success on that branch. → UNCOVERED: no bridge tool presses a Command_Action or sends a quest signal; WASTE_RUN_SIGNAL_DEBUG_HOOK_1
- Dropping on the Empire sets Empire goodwill to hostile. → UNCOVERED: same hook, then `jawa/faction_relations_get`
- The window lapses after 30 days with the quest Failed and the waste kept. → UNCOVERED: needs `step_game_ticks` over 1.8M ticks plus the hook
- The half-extracted core is only disposed of (no fuel, no sale). → WasteRunKernel.WasteDefNames lists it and nothing else consumes it
- Every branch runs its own effect node and every outcome has a mood memory. → static_checks (offline, consequence_checks)
- The flight gate refuses a ship away from a destination that exists, and waives one this planet lacks (a biome on 0 tiles must not lock the run). → selftest_wasterun_kernel.py (table); live: UNCOVERED, `WasteRunProof.ProofGate` reads it per destination on the bay's map
- Propane-lake branch burns the crater. → static_checks prove the reflection target; live: UNCOVERED, read `GameComponent_WarLabCrater.Triggered` after ProofPress IgnitePropaneLake with mandrake.rut.injections loaded (WAR_LAB_CRATER_HOOK_1 owes the tile proof itself)
- Slime outcomes change the world: neutralized lowers pollution around the ship, bloomed raises it and registers ToxicFallout, unknown saves one delayed answer. → kernel numbers in selftest; live: UNCOVERED, read Tile.pollution around the bay's tile after ProofPress SlimeExperiment

## the walk
1. [L] Player.log has no config error naming `RUT_WasteRun.xml`, `RUT_WasteRunOffer.xml` or the patch
2. [D] `jawa/get_defs` resolves the nine defs; the bay carries the planner comp
3. [B] fire the incident with waste in a bay, accept, read `WasteRunProof.ProofGate`, then `ProofPress` each destination (a press away from a charted destination returns committed=False). Flip `flightRequiredEnabled` off to press from anywhere.

## [S]
none; letters and goodwill are readable.

## anti-guessing notes
- RULED OUT: a runtime random roll for the Slime outcome. `QuestNode_RandomNode` runs once at quest generation, so the outcome is fixed when the quest is offered (provisional by design, and a reload cannot re-roll it).
- RULED OUT: a vanilla XML player-choice node. `<choices>` in vanilla quests is a generation-time random pick; the choice lives in the cask-bay command.
- The validator's five `unemitted-signal` warnings are expected: the `WasteDest_*` signals are sent from C# (RUT_CompWasteRunPlanner.Commit), not from any node.

## north star
state: DRAFT
validated-hash:

No owner-validated bars exist for this mod; the functional script is agent-approved (debug_process.md section 6).
