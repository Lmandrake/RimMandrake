# Desert family review sheet build — 2026-09-20

## Status: STARTING

## Scope — REVISED by coordinator mid-task
- RUT_ExtremeDesert (3,969 tiles)
- RUT_Desert (2,390 tiles)
- RUT_AridShrubland (628 tiles)  <- swapped in for RUT_BlueDesert
- DROPPED: RUT_BlueDesert — CORRECTED reason (coordinator's first reason was
  WRONG and retracted): NOT "deliberately sterile/by design". Its empty
  wildAnimals/absent wildPlants is because the biome's intended life
  (Swallowers, Burners, Pickers fauna; transparent fractal flora) was
  COMMISSIONED in the_blue_desert.md and NEVER AUTHORED — density fields were
  zeroed only because "nothing to scale until [those defs] exist" (the def's
  own comment). A verdict sheet reviews roster entries that already exist;
  this biome has none yet. Needs AUTHORING, not verdicts — coordinator is
  filing its own item. Never call it sterile or by-design in the sheet/report.
- Adjacent, NOT pulled in: RUT_Wasteland

## Coordinator-supplied numbers (use, don't re-derive) — CONFIRMED by parent
- RUT_Desert: 1 ours, 54 third-party, 7 unguarded (top donors: SWAnimalCollection 39,
  AlphaAnimals 7, DroidDepot 7)
- RUT_AridShrubland: 2 ours, 51 third-party, 11 unguarded (SWAnimalCollection 38,
  DroidDepot 7, AlphaAnimals 4)
- RUT_ExtremeDesert: 0 ours, 22 third-party, 3 unguarded (SWAnimalCollection 10,
  DroidDepot 7, AlphaAnimals 4)

## Origin rule (per coordinator correction)
Origin column shows the REAL packageId from the entry's own MayRequire attribute,
never inferred from defName prefix — SWAnimalCollection ships BARE defNames
(Bantha, Kreetle, Scavrat, Shyrack, Gorg, Gutkurr, Jamel, Rat-lookalikes) that a
prefix rule would misread as vanilla; it's actually the single largest donor
(160 entries planet-wide).

## Unguarded entries to flag (no MayRequire, not our own def) — visible marker,
## do NOT add MayRequire, do NOT "fix"
- RUT_Desert wildPlants: AB_HardyGrass, Plant_Chakroot_Wild, Plant_HubbaGourd_Wild, AB_Aaklac, AB_DessertTree
- RUT_Desert wildAnimals: JOE_Landopus (ours — comment says so), Rat
- RUT_ExtremeDesert wildPlants: Plant_Bloddle, AB_GiantStikehr
- RUT_ExtremeDesert wildAnimals: Rat
- RUT_AridShrubland wildPlants: Plant_ShrubLow, RG_Plant_AridGrass, Plant_Brambles, Plant_Bush, Plant_Ripthorn, Plant_HealrootWild, Plant_Nysyllin_Wild, RG_Plant_CreepStern, RG_Plant_CrimsonCushion, RG_Plant_Dervish
- RUT_AridShrubland wildAnimals: Rat

## Progress log — DONE
- [x] Read review-sheets skill
- [x] Read Rot generator (build_review_sheet.py) — confirmed hand-literal ROWS
      table (830 lines), too specific to Rot's 40+10 species to generalize
- [x] Read Deeps generator (build_species_sheet.py) — same hand-literal shape
- [x] Decision: write a NEW, fully DATA-DRIVEN generator instead of
      generalizing either (documented in the new script's own docstring) —
      the desert family's raw roster (151 entries across 3 biomes) spans 9+
      donor mods and is squarely in "hand-transcribed table drifts and gets
      it wrong" territory this project already paid for once (RotSporeKit
      visualSizeRange, see that script's header note)
- [x] Located the three desert BiomeDef XML files
- [x] Parsed wildPlants/wildAnimals per biome (ElementTree, direct-child
      shape confirmed for all three files; <li> shape also handled in the
      parser defensively though not needed here)
- [x] SCOPE CORRECTION mid-build: RUT_BlueDesert dropped, RUT_AridShrubland
      added (coordinator, then coordinator's own correction on WHY)
- [x] Origin resolved from each entry's own MayRequire attribute, never
      defName prefix, per coordinator correction
- [x] 19 unguarded entries independently resolved via scoped greps (never a
      blind full-Workshop scan — one timed out past 120s when tried) against
      specific candidate mod roots
- [x] Resolved thumbnails: SWAnimalCollection ships AssetBundle-only art (no
      loose PNGs at all) — UnityPy unavailable on this machine's python3, so
      thumbnails for it and Droid Depot/ReGrowth/Horrors came from this
      repo's own pre-extracted observed/inventory/bundle_textures cache,
      matched by trailing container-path segments (not the stale index.csv,
      which only covers 5 of the ~10 needed sourceKeys — walked the cache
      folders directly instead)
- [x] Fixed 3 real bugs found via dry runs: (1) thumb path had no directory
      prefix (check_sheet.py FAILed on it), (2) wild-variant plant ThingDefs
      (Plant_Chakroot_Wild etc.) inherit description/graphicData/
      visualSizeRange from a ParentName parent, not on the leaf def — added
      chain-walking, (3) letter-INFIX Graphic_Random form (Grass_Leafless ->
      GrassA_Leafless) was missing from the suffix ladder
- [x] Determined sizes: fauna = adult (LAST) lifeStage bodyGraphicData.drawSize
      (never li[0]); flora = drawSize × visualSizeRange.max, chain-walked
- [x] Built src/RimUtinni/UtinniPatches/build_desert_review_sheet.py
- [x] Generated HTML (109 rows) + 105 thumbs + decisions.json seed
- [x] check_sheet.py: 0 FAIL, 1 WARN (expected — fresh unreviewed decisions
      file), exit 0
- [ ] Commit + push (next)

## Final tallies (CONFIRMED, parsed 2026-09-20)
- 109 unique species rows (17 flora, 92 fauna) across the 3 biomes
- Origin: OURS=4 (3 SWBestiary + 1 UtinniPatches/JOE_Landopus),
  DONOR=99, VANILLA/DLC=6
- Top donors: Star Wars Animal Collection 68, Alpha Animals 14,
  Outer Rim Droid Depot 7, Alpha Biomes 4, ReGrowth 2 4, VFE Insectoids 2 1,
  Horrors 1
- 19 unique unguarded rows (no MayRequire on that entry) — every one
  independently resolved to a real owning mod, not left ambiguous
- Thumbnails: 105/109 resolved (96.3%). 4 unresolved, all ReGrowth 2 plants
  in RUT_AridShrubland (RG_Plant_AridGrass/CreepStern/CrimsonCushion/
  Dervish) — their texPaths have no loose PNG anywhere in the owning mod's
  own tree (scoped search) and no entry in our bundle_textures cache;
  reported as UNRESOLVED with reason, not guessed.
- Raw per-biome parse counts (pre-dedup, cross-check against coordinator's
  numbers): RUT_ExtremeDesert 23 animals + 2 plants; RUT_Desert 57 animals +
  5 plants; RUT_AridShrubland 54 animals + 10 plants. Per-biome UNGUARDED
  counts MATCH the coordinator's exactly (3 / 7 / 11). Per-biome OURS counts
  differ slightly (mine: 0/2/2 vs coordinator's 0/1/2 for Extreme/Desert/
  Arid) — mine additionally counts RSW_Jellypot (RUT_Desert,
  mandrake.rsw.swbestiary) as OURS, consistent with how the Rot sheet
  classified RSW_ SWBestiary defs. Flagging rather than silently overriding.
