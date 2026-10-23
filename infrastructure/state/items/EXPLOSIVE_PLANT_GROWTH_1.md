# EXPLOSIVE_PLANT_GROWTH_1 — visible plant growth as a world mechanic

Born in the Cracked Lands enrichment (`biomes/the_cracked_lands.md` §10b): water-soaked
plants grow VISIBLY — the player watches them get bigger, not animal-motion but growth —
and it should feel intimidating. The jungles should visibly grow. **Scope is Baroque
Biomes' own biomes** (owner 2026-10-16: *"It should only natively apply to plants within
the Baroque Biomes, though option settings could allow it to apply to other plants from
other mods or vanilla basegame (irrelevant in Utinni)."*); an unsupported option extends it.

**Where the design lives now:** the rules are
`design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md` (every OQ ruled on
`EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS`) and `design/RimMandrake/tree_burst_design_2026-10-17.md`;
the background, numbers history and owner quotes are
`design/RimMandrake/explosive_growth_consensus_2026-10-16.md` and
`design/Jawa/worldbuilding/explosive_plant_growth_design.md`. This sprint's acceptance lines are
X1-X5 in `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md` §1.4 (approved by card, S0-4).
`FLOOD_WITNESS_EVENT_1` is the plot's guaranteed showcase.

## State (2026-10-22)

- Code: `src/RimMandrake/ExplosiveGrowth/`, a composed ENGINE member of Baroque Biomes
  (`mandrake.rm.biomes`, `src/RimMandrake/Biomes.compose.json`); the standalone
  `mandrake.rm.explosivegrowth` and `mandrake.rut.plantgrowth` are retired
  (`EXPLOSIVE_GROWTH_MERGE_COMES_HOME`, `PLANT_GROWTH_MERGE_NEVER_MEANT_APART`). Campaign roster:
  `src/RimUtinni/UtinniPatches/Defs/ExplosiveGrowth/`.
- Script: `src/RimMandrake/ExplosiveGrowth/validation.py`, walk
  `design/validation_walks/RimMandrake/ExplosiveGrowth.md`, preflight `preflight_explosivegrowth.py`.
- Live so far: the charge clock climbs and fires a real Churn (2026-09-27, solo tier);
  `scope_native_only` PASS on the solo list (2026-10-17).
- **X4 built offline 2026-10-22:** cutting a charged wild plant forfeits the jackpot, harvesting
  keeps it. `RM_Patch_Plant_YieldNow_Jackpot.CuttingNow` reads the plant's reserver: a pawn whose
  driver is `JobDriver_PlantCut` (vanilla reads `YieldNow` inside the work toil, before
  `PlantCollected`, after reserving the target). Row `probe_jackpot_cut_forfeits`.
- **S0-7 (agreed by card 2026-10-16) enacted 2026-10-22:** `RM_Cauldron` and `RUT_Cauldron` are
  stalled (terminator) biomes — `src/RimMandrake/Cauldron/Defs/ExplosiveGrowth/RM_Cauldron_ExplosiveGrowthStalled.xml`
  and the RUT roster; `RUT_ExtremeDesert` stays held by `noSoakBiomes`. Salted-ground refusal is
  CUT; the dynamic-draw close-up layer and Fever Wood's inside-the-giant view are DEFERRED (not
  sprint biomes); the invented roster defaults are KEPT.

## Owed (all live; nothing offline remains on this item)

1. Deploy (`deploy_custom_mods.py --compose biomes --apply` + UtinniPatches) and refresh
   `src/RimMandrake/Utils/modcheck/required_checks.json` (`required_checks.py`) at the same landing.
2. **X2** perf gate: TPS at speed 3 with soaked plants ≥ 90% of soak-off (S0-6, by card).
3. **X3** every soak route live (crack flood, dug FlowWorks water cell, Miasma axis fresh side,
   wet-native rate in Greentide/Miasma/Fever Wood).
4. **X4** live: a real pawn's CutPlant job on a charged wild plant drops the plain yield; a
   HarvestPlant job pays about ×(1 + charge).
5. **X5** Greentide grazing hook and dry-air blower writing the suppression grid, seen in the
   Greentide review (`suppression_on` row).
6. The stalled Cauldron: on a Cauldron map our plants run `stuntedMultiplier` and never cycle.
7. Open soak routes with no system yet: `red_water` (Contagion rain), `scald_melt`, Greentide
   extract (engine side ready: `ExplosiveGrowthAPI.Soak`, roster `soakWeathers`).
