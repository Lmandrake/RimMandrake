# WORLDMAP_FINAL_REVIEW_1 — measured audit report (night pass, 2026-09-12)

Instruments: fresh live-bridge dumps (world loaded from CANONICAL_ASHKARR_2026-09-09,
ticksGame 114896; features/landmarks/settlements/mutators/links, all read to
exhaustion, no row-cap truncation) joined against the frozen CSV (region column
completed tonight — CSV_REGION_SYNC_1 CLOSED, all 809 mismatches resolved).
Lane files in this directory: audit_mutators.md · audit_landmarks_settlements.md ·
audit_names_rivers.md. Everything below is MEASURED unless marked.

## Clean (verified tonight)
- **Features ↔ regions: 0 mismatches** — all 71 live WorldFeatures match the CSV's
  region column 1:1, per-feature tile counts agree exactly (Abandoned Mines 34,
  Ashfall Range 324 both ways).
- **Steam terminator rule: 0 violations** — the 21-tile violation is FIXED on the
  live world (33 geysers remain, max arc 73.98). Inferred VAPOR_TERMINATOR_GEYSER_FIX_1
  executed; FOUNDRY's close will confirm.
- **Faction roster reconciles**: 12 settlement-holding factions + Mechanoid = the
  13-faction canon roster; the world's 21 total = campaign 8 RUT_ + system factions.
- **Rivers reconciled, three-way**: live adjacency 335 tiles / 326 edges; frozen-CSV
  river_flow-nonzero 298 (= canon's rivers_tiles, same definition); the old "217
  origin tiles" figure is method-unrecoverable — treat as dead.
- RUT_GapingDoom placed; landmark art-patch coverage complete; rotstink gas 0/16 clean.

## Findings (ranked)
1. 🔴 **Ancient*Vent family: 283 of 417 placements violate the ruin-only rule**
   (ruled 2026-09-12). This is VAPOR_PLACEMENT_CLEANUP_1's main workload, now
   quantified. Examples in audit_mutators.md.
2. 🔴 **Sarlacc landmarks: 6 live sw_Sarlacc (expected 1) and 7 sw_DeadSarlacc
   (expected 4); the tile-2920 one still on the Weeping Stones oasis.** Counts
   contradict sarlacc_spec's ×1/×4 register. Possibly FOUNDRY's in-progress build
   placing cisterns before the relocate item ran — SARLACC_WORLDMAP_RELOCATE_1 must
   reconcile to the ruled 2–4 total and vacate 2920; if 6 predates tonight, the
   spec's counts were stale and the accepted draft's fork-2 ruling governs.
3. **Settlements: 96 live vs canon.yml's stale 120** (canon's settlements block is
   pre-freeze lineage; per-faction distribution also differs). Candidate for the
   next canon sitting — same treatment the planet census got. +1 settlement on an
   ice biome (details in lane file).
4. **Magma vents 5/13 out-of-lock; swamp/ruin gases 11 misplaced** (7 toxic,
   4 deadlife) — both inside VAPOR_PLACEMENT_CLEANUP_1's scope. PoisonForest
   green-gas def not present in the dump — coverage gap, UNMEASURED.
5. **Name register, 5 findings** — worst: [MEDIUM] the Ascendant Helix settlement
   names ("Specimen Hall", "The Revision", "The Fair Copy", "Cold Archive")
   thematically echo the reveal-gated splice secret; owner to confirm intentional.
   [LOW] near-duplicate roots (Fall Line/Fall Line Barrens, Scald/Scald Spine);
   [LOW] settlement "Colony" is register-breaking generic.
6. **Representation caveat**: 34 "road on water" hits are all AB_PropaneLakes,
   which this data represents as land (water flag 0) — both readings recorded,
   not collapsed.

## UNMEASURED / open
- Helixien rule audit: 0 placements exist (rule governs future placement); "the
  Rot" not identifiable in the CSV (RUT_TheRot unpainted or pending swap).
- Whether RUT_BlueDesert/Wasteland count as "dead-machine ruin" biomes for the
  gas rule — needs a biome-def read.
- The STARE: planet captures pending (Transient/worldreview/shots/ when the
  current cold load completes); the verdict itself is the owner's sitting with
  BENCH — this report is its evidence pack, not the verdict.
