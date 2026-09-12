# VAPOR_EMITTER_PLACEMENT_1 — worldmap review of every vapor/smoke/gas emitter

Filed from the Weeping Stones (ZBiome_DesertOasis) sheet sitting, 2026-09-06. The
owner's ruling landed mid-conversation and is wider than that biome.

## The ruling (owner, verbatim on the filing event)

Steam geysers are NOT uniformly distributed. Frequency **radially decays away from
mountain ranges / overt vulcanism** and reaches **zero before the terminator** —
the deep nightside and the seam never see them. Every OTHER vent type needs the
same treatment: an inventory, then a placement rule per type.

## Scope

1. **Inventory** every vapor/smoke/gas emitter that can appear on Ash'karr —
   TileMutatorDefs, map features, terrain/building defs (SteamGeyser and kin),
   modded vents, smokers, fumaroles. Post-inheritance, against the frozen
   `official` dump; verify any live claim against the map, not raw mod XML.
2. **Placement rule per type**: which regions/biomes get it, what the decay is
   keyed to (distance to mountain/volcanic source), where it is banned.
3. **Audit the frozen map** against the rules — where do current
   geysers/vents actually sit? (`world/ASHKARR_WORLDMAP_tiles.csv` has no
   emitter column; the savegame / live world is the instrument.)
4. Fix-up pass via the bridge where the map violates the rules.

## Known couplings

- **Weeping Stones hot aberrant oases** (ruled same sitting): the ~35
  ZBiome_DesertOasis tiles on the Scald Spine/Anvil (up to 63 °C) are
  vent-steam / relic-condenser fed, not dew-fed. Their oasis water source IS a
  vapor emitter — this review decides what feeds them.
- The Contagion owns rain-receiving highs (`CONTAGION_BIOME_PLACEMENT_1`);
  volcanic steam highs are a different family — don't conflate.
- `hydrology_and_fire_ecology.md`, `the_propane_lakes.md` (nightside gas is a
  different phenomenon — cold volatiles, not vents; the ban "zero before the
  terminator" applies to STEAM sources, rule the cold-gas types separately).

## Parts 1-3 done 2026-09-12 (BENCH belt wave) — inventory + proposals + audit
`design/Jawa/worldbuilding/vapor_emitter_review_2026-09-12.md` — 17 emitter
families MEASURED against the frozen OFFICIAL-2026-08-29 dump (sha 1742630eb...,
fingerprint stated inside); world-tile audit MEASURED (28,126 mutator instances,
0 unresolved shortHashes); colony-map-level census UNMEASURED (save holds no
local maps). Findings that matter:
- RULED-RULE VIOLATION: 21/54 SteamGeysers_Increased tiles sit AT/PAST the
  terminator (arc >=90, up to 127.1) — breaks the owner's "zero before the
  terminator" directly. Fix filed: VAPOR_TERMINATOR_GEYSER_FIX_1 (FOUNDRY).
- No decay implementation exists: all 10 Ash'karr biomes carry default
  geyserCountFactor=1; VEE_SteamGeysers_Decreased used on 0 tiles.
- GeothermalVent (Odyssey) ignores biome/mutator gates entirely per source —
  needs a new gate to obey any rule.
- AB_MagmaVents: 5/10 instances on biomes outside its engine whitelist —
  likely orphaned by a biome repaint.
- Weeping Stones vent-feed PROPOSED via ZBiome_DesertOasis geyserCountFactor
  (SteamGeysers_Increased is engine-blacklisted there).
Remaining: owner rules the PROPOSED per-type rules (cards can ride
MECHANICS_CARDS_SITTING_1); then part 4 bridge fix-up per type (FOUNDRY).

## Rules RULED 2026-09-12 (owner card sitting)
All per-type rules ruled — recorded verbatim in the review doc's "Owner
rulings" section (ancient vents ruin-only; magma crater-locked; swamp/ruin
gases by biome family + PoisonForest toxic and green gas; helixien = junker
related, Poison Forest and the Rot, proposal rejected). Part-4 live cleanup
handed to FOUNDRY as VAPOR_PLACEMENT_CLEANUP_1 (+ the earlier
VAPOR_TERMINATOR_GEYSER_FIX_1). This item is done when both land.
