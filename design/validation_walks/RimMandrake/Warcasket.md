# RimMandrake: Warcasket — validation walk
subject: src/RimMandrake/Warcasket  (packageId `mandrake.rm.warcasket`)
deps: mandrake.rm.biomes (composed mod folder, not a src folder) (carries the folded EnvironmentalHazards assembly: `HazardTargeting`) + Odyssey (vacuum) + Biotech (pollution, toxic resistance) <!-- walklint-ok: mandrake.rm.biomes is the COMPOSED mod, it has no src folder of its own -->
list: `warcasket` tier (modset_builder.py --list; all five DLCs)
status-hint: WARCASKET_SUIT_CLASS_1 — a cross-cutting heavy survival suit (extreme temperature, vacuum, toxins) that is very slow and fails under compound threats; plus the Junker sarcophagus variant, the half-extracted core, the lead-lined cask bay, and a general deep-water terrain hazard that any apparel carrying `RM_HazardousTerrainProtection` defuses

Script: `src/RimMandrake/Warcasket/validation.py` (modcheck Suite), plan `src/RimMandrake/Warcasket/northstar_plan.py`. Every line below ends with the component that covers it, or `UNCOVERED` with the reason.

## must be true
- Every shipped def loads and resolves in the running game: `RM_Warcasket`, `RM_WarcasketJunker`, `RM_CaskBay`, `RM_HalfExtractedCore`, `RM_HazardousTerrainProtection`, `RM_WarcasketBreach`, `RM_TerrainImmersionHazard`, `RM_CrackSarcophagus`, `RM_HazardCasks`; the suit carries `RM_CompProperties_WarcasketIntegrity`, the Junker `RM_CompProperties_SarcophagusSeal` + `RM_JunkerSarcophagusExtension`, the bay `RM_CompProperties_CaskShielding`, the core `RM_CompProperties_CoreDose` (a mistyped `Class` silently discards the comp); the log carries no Warcasket error. → defs_and_load.defs_resolve, defs_and_load.absent_def_is_refused, defs_and_load.comps_wired, defs_and_load.no_warcasket_log_errors
- The suit is "very resistant to extreme temps": wearing it raises the wearer's `ComfyTemperatureMax` by about the declared `Insulation_Heat` 100 and lowers `ComfyTemperatureMin` by about `Insulation_Cold` 140. → suit_stats.thermal_cover
- The suit is resistant to vacuum: the wearer's `VacuumResistance` reaches the declared +0.85. → suit_stats.vacuum_cover
- The suit is resistant to toxins: the wearer's `ToxicEnvironmentResistance` reaches the declared 0.9 (and so cuts the half-extracted core's dose, which scales by it). → suit_stats.toxin_cover, core_and_cask_bay.warcasket_wearer_resists_core_dose
- The suit is "very slow, bulky": the wearer's `MoveSpeed` drops by about 1.8 and `WorkSpeedGlobal` by about 0.25. → suit_stats.slow_and_bulky
- The suit carries `RM_HazardousTerrainProtection` 0.9 as a worn-apparel stat. → suit_stats.terrain_protection_stat
- `RM_WarcasketJunker` is still a full suit (inherits the base suit's cover). → suit_stats.junker_variant_is_still_a_suit
- Compound failure is real: with TWO hazards active at once (extreme heat + polluted ground) a sample of wearers suffers breaches (`RM_WarcasketBreach` on the wearer, suit HP down). → compound_failure.compound_failure_fires
- One hazard alone never fails the suit. → compound_failure.single_hazard_never_fails
- Mod Settings `compoundFailureEnabled` OFF: the suit never fails, stats unchanged. → compound_failure.compound_failure_off
- Mod Settings `masterEnabled` OFF: none of the mod's mechanics run. → compound_failure.master_off, terrain_immersion.master_off_terrain, core_and_cask_bay.master_off_core
- Compound failure with VACUUM as one of the two hazards. → UNCOVERED: no bridge tool creates vacuum on a room (needs a `jawa/room_vacuum` tool; heat + pollution already exercise the same `hazards >= 2` branch)
- A pawn on deep (non-walkable) water without protection accrues `RM_TerrainImmersionHazard`. → terrain_immersion.unprotected_on_deep_water_accrues
- A warcasket wearer on the same water accrues at about a tenth of that rate (the clock is slowed by the protection stat, floored at 5%). → terrain_immersion.protected_wearer_barely_accrues
- A shallow ford (walkable water) is never the hazard. → terrain_immersion.ford_is_safe
- Mod Settings `terrainImmersionEnabled` OFF: deep water is ordinary terrain, no hediff accrues. → terrain_immersion.terrain_immersion_off
- The terrain hazard grants no dive verb, no portal, no sea-floor access (ship-only rule, owner 2026-09-26). → UNCOVERED: a negative over every verb and every portal is unbounded; source guard is that the mod ships no `MapPortal`/`FloatMenuOptionProvider` for diving (`RM_Sarcophagus.cs`'s provider only offers the crack-open job on a corpse)
- A dead wearer's `RM_WarcasketJunker` is sealed onto the body; a colonist cracks it open (`RM_CrackSarcophagus`) and recovers the suit, the welded tooling (Steel 25, ComponentIndustrial 2) and `RM_HalfExtractedCore`. → sarcophagus.crack_open_yields_salvage
- Only the Junker variant is a sarcophagus: the same job on an ordinary warcasket corpse yields nothing. → sarcophagus.plain_suit_corpse_yields_nothing
- Mod Settings `sarcophagiEnabled`: a dead wearer's suit is not sealed when it is OFF. → sarcophagus.sarcophagi_setting_flips (write + read-back only) · UNCOVERED for the behaviour: no bridge tool reads a corpse's apparel lock or strips a corpse (needs `jawa/corpse_strip`)
- A loose `RM_HalfExtractedCore` doses pawns within 4 cells (vanilla toxic buildup) and nobody beyond. → core_and_cask_bay.loose_core_doses_nearby
- Mod Settings `coreDoseEnabled` OFF: the core is inert cargo. → core_and_cask_bay.core_dose_off
- The cask bay admits only cask cargo (Wastepack, the core, `RM_HazardCasks`). → core_and_cask_bay.cask_bay_storage_filter
- A core on a cask-bay cell gives no dose, and the inspect pane says the bay is shielding. → core_and_cask_bay.cask_bay_silences_core, core_and_cask_bay.inspect_reports_shielding
- Mod Settings `caskBayShieldingEnabled` OFF: the bay is ordinary cask storage (core reads unshielded, bay reads "Shielding disabled"). → core_and_cask_bay.cask_bay_shielding_off
- A stored toxic wastepack never dissolves while shielding is on. → UNCOVERED: `CompDissolution.dissolveTicks` is private and no tool reads a comp field (needs `jawa/comp_field`); the bay's own inspect line is the only proxy and is covered above
- The cask bay is buildable only on gravship substructure and so flies with the ship. → UNCOVERED: needs a live gravship (`jawa/gravship_launch`) and the Odyssey build UI; the def's `terrainAffordanceNeeded Substructure` is the only evidence, read in `defs_resolve` only as presence
- Art reads as a heavy riveted tank, bay as a lead-lined hold, core as a half-cut reactor. → UNCOVERED: `visual` — owner has not reviewed the generated icons (judge pass)

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.warcasket" and no XML error naming `RM_Warcasket.xml`/`RM_CaskBay.xml`/`RM_HalfExtractedCore.xml`/`RM_WarcasketHediffs.xml`/`RM_WarcasketStats.xml`/`RM_CrackSarcophagus.xml`   # load-time
2. [D] def read-back: every def in the first `must be true` line resolves (`jawa/get_defs`, `foundCount` 9, `notFound` empty)
3. [B] `jawa/pawn_gear` wear `RM_Warcasket` on a colonist; `jawa/pawn_stats` before/after → comfy range, `VacuumResistance`, `ToxicEnvironmentResistance`, `MoveSpeed`, `WorkSpeedGlobal` move as declared
4. [B] twenty wearers in a heated (80 C) polluted room for 6000 ticks → at least one `RM_WarcasketBreach`; the same in a heat-only room → none; both settings OFF → none
5. [B] naked / suited / ford pawns on deep or shallow water for 1000 ticks → `RM_TerrainImmersionHazard` ~0.48 / ~0.05 / absent
6. [B] kill a Junker-suited colonist, `jawa/ordered_job` `RM_CrackSarcophagus` by a second colonist → suit, Steel, ComponentIndustrial, `RM_HalfExtractedCore` on the ground
7. [B] core beside a naked pawn → `ToxicBuildup`; core on a `RM_CaskBay` cell → none; inspect strings flip with the settings

## [S]
Whether the warcasket, junker variant, cask bay and half-extracted core icons read as intended is a human-pass concern (generated art, owner has not reviewed; the paperdoll reuses the vanilla Vacsuit).

## anti-guessing notes
- Every def, field and comp named above is read from `src/RimMandrake/Warcasket/Defs/*.xml` and `Source/*.cs`; every bridge call is a declared `[Tool]` parameter (checked by `northstar_driver/lint_calls.py`).
- MOD DEFECT FIXED OFFLINE, unmeasured live: the suit declared `ToxicEnvironmentResistance` 0.9 in `statBases`; every vanilla source (Core and Biotech gas/tox masks) uses `equippedStatOffsets`, which is what the pawn stat reads. Moved. `toxin_cover` and `warcasket_wearer_resists_core_dose` read the pawn and go red if the line regresses.
- MOD DEFECT FOUND AND FIXED OFFLINE (RimSage, decompiled `Thing.DoTick`): `RM_Warcasket` had no `tickerType`, apparel defaults to `Never`, and `Pawn_ApparelTracker.ApparelTrackerTickRare` only does wear-out, so `RM_CompWarcasketIntegrity.CompTickRare` never ran and compound failure never fired. Def now carries `<tickerType>Rare</tickerType>`. `compound_failure_fires` is the guard: it goes red if the line is ever lost. Never seen red live; if the first live run is green, that is the fix working. `checkIntervalTicks` in the XML is never read (the cadence is the engine's 250-tick rare tick).
- RULED OUT (by source): `HazardousTerrainImmersion` heals protected pawns only when `driveFactor <= 0`, which `max(0.05, ...)` makes unreachable; a protected wearer therefore never heals while standing in deep water. Not a check, noted so nobody "fixes" the missing heal.
- The failure roll is random: 20 wearers x 24 rare ticks x 0.015 = ~7 expected failures in the 6000-tick ON arm (zero by chance ~0.1%), ~4.8 in each 4000-tick OFF arm (~0.8%). A red `compound_failure_fires` that is not a mod bug is possible once in ~1000 runs; rerun before filing.
- The break/absent cases that prove each check can fail: `absent_def_is_refused` is the def-resolution control; `single_hazard_never_fails` and `plain_suit_corpse_yields_nothing` are the negative controls; the toggle arms are the OFF controls; the naked baselines in `suit_stats` are the stat controls (a suit that applied nothing reads a zero delta).

## north star
state: DRAFT
validated-hash:

No owner-validated bars exist for this mod; nothing here binds until he validates a section by his own word. The functional script above is agent-approved (debug_process.md section 6).
