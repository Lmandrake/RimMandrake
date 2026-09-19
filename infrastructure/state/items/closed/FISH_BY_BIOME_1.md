# FISH_BY_BIOME_1 — think about FISH in every biome where relevant

Owner, 2026-09-06: *"need to think about FISH in every biome where relevant! Good lord..."*

## spec
- Odyssey's fishing is live in the stack (donor biome defs carry `fishTypes` blocks —
  Alpha Biomes assigns e.g. `VCEF_DuskySprat`/`VCEF_ForsakenAnglerfish` to the crags,
  `VCEF_Jellyfungus` to the Rot; vanilla `IceSheet` carries salmon/cod/frostfish). Inventory
  every fish def in the stack (MEASURED from the dump) and every biome's current
  `fishTypes`.
- Per biome with water (the four liquid biomes, the Cracked Lands' 27 open-water tiles,
  the Slime's slime-rain floods, the Rot's milk ponds, the propane sea's exotics, the
  Contagion's red pools): what lives in it, what a fisher catches, what the fliers dip for
  — all under the recognizability rule (no salmon; analogs and aliens) and each sheet's
  water chemistry (`WATER_KINDS_TAXONOMY_1`: fishing in milk, propane, red water, brine
  are different acts).
- Output as DATA: biome × water kind × fish defs × rare catches, fed into the freeze
  review's per-biome table.
- Ties: `SAND_SWIMMERS_MOD_1` (sand fishing), the fliers (`the_cracked_lands.md` §4).

## verify
Every water-bearing biome has a ruled fish list or an explicit "no fish, because…"; the
dump resolves each def.

## 2026-09-09 progress (BENCH, assignment pass)
- Per-biome fish RULINGS are data now: every roster in
  `design/Jawa/worldbuilding/biomes/rosters/*.json` carries a `fish` field (mostly
  ruled no-fish with the chemistry cited).
- Candidates for the ruled-yes waters: `rosters/_fish_candidates.json` (`f18fb5de`) —
  87 fish ThingDefs MEASURED in the live dump; binding is `BiomeDef.fishTypes`
  (fresh/salt Common/Uncommon buckets) — fish placement is BIOME work, no def edits;
  the campaign water-kinds chemistry has no engine hook, it is flavor over the
  fresh/salt axis. Weeping Stones and Cracked Lands have confident donors; greentide
  already assigned (RSW_Mee/Faa/Laa); twilight sub-roof shoal = the one new-def gap,
  non-blocking (diving mods unbuilt).
- ⚠️ RECONCILE BEFORE CLOSING: another window is concurrently authoring sand-fishing
  content (`src/RimUtinni/UtinniPatches/Patches/SandFishing_CrackedLands.xml`,
  `src/RimStarWars/SWBestiary/.../RSW_SandStalker.xml`, `ManyWaters/Defs/` — untracked
  in their tree as of this note). Their custom-def approach and this census's donor
  candidates for the Cracked Lands must merge into ONE fishTypes ruling per water.

## 2026-09-09 progress (Fable, buildable-half pass)
- **Written**: `src/RimUtinni/UtinniPatches/Patches/BiomeFishTypes_Ashkarr.xml` +
  generator `design/Jawa/mods/gen_fish_types.py`, reading `_fish_candidates.json`.
  Sets `ZBiome_DesertOasis` (weeping_stones) `fishTypes` — `freshwater_Common` <-
  the 4 confident swfish_ donors (Burra/Daggert/Nyork/See, MayRequire
  mlie.starwarsanimalcollection), `freshwater_Uncommon` <- the 4 secondary VCEF_
  picks (FrigidSwimmer/Slimefish/Spinyfish/OcularFish — verified these are
  actually shipped BY Alpha Biomes, ParentName="AB_RawFishBase", packageId
  sarg.alphabiomes, not a separate "Vanilla Fishing Expanded" package as the
  census's mod field implied). Replaces the donor mod's own vanilla Earth-named
  defaults (Fish_Tilapia/Fish_Piranha/Fish_Bluefish/Fish_Tuna/Fish_Flounder,
  confirmed on the live def on disk) on the freshwater buckets only; saltwater
  is untouched (no sea at this water). Each replace wrapped in
  `PatchOperationConditional` on the target bucket xpath, gated on
  `PatchOperationFindMod "More Vanilla Biomes"` + `MayRequire
  Ludeon.RimWorld.Odyssey`. Validator (`validate_patch.py`, `--live` against the
  2026-09-09T01-54-07Z dump, `--defs` against Data/Workshop/Mods): **OK, 0
  errors, 0 warnings** — both PatchOperationConditional checks and their
  PatchOperationReplace matches hit exactly 1 (`ZBiome_DesertOasis.xml`) each,
  i.e. really applied, not a silent no-op. NOT deployed (per instruction).
- **Left to the other window**: `the_cracked_lands` / `ZBiome_Badlands`. Read
  their uncommitted `SandFishing_CrackedLands.xml` (read-only, per instruction —
  not edited, moved or committed here): it already
  `PatchOperationReplace`s both `freshwater_Common` (RSW_DuneCrawler) and
  `freshwater_Uncommon` (deliberately empty) plus `rareCatchesSetMaker`
  (RSW_RareSandCatches) and `maxFishPopulation` on this exact def, gated the
  same way (PatchOperationFindMod "More Vanilla Biomes"). Fully covered —
  nothing added here, no conflict to merge.
- **Real gap found, not fixed here**: `the_greentide` / `BiomeCypreJungle`'s
  roster claim that RSW_Mee/Faa/Laa are "already assigned" does **not** hold.
  Checked the live def (`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml`
  — no `fishTypes` block at all) and the donor XML
  (`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`): RSW_Mee/Faa/Laa
  (commonality 0.4/0.3/0.3, matching the roster's numbers exactly) are wired into
  a `wildAnimals` bucket on a **different** biome — `AB_MiasmicMangrove` /
  `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml` (the_miasma) — not
  into `BiomeCypreJungle`'s/`RUT_Greentide`'s `fishTypes`. Likely a copy-paste
  mix-up in the roster's own `_fish_candidates.json` `the_greentide.assigned`
  block, or the RSW_Mee/Faa/Laa assignment was planned for the greentide and
  landed on the miasma instead. Out of this pass's instructed scope to fix
  (task said verify-and-do-nothing-if-present; it is not present) — whoever
  picks this item back up should decide whether the_greentide gets its own
  `fishTypes` patch (its own roster ruling — graded shoal fish on the living
  reach only — never actually got written), and whether the_miasma's
  RSW_Mee/Faa/Laa wildAnimals placement is itself correct or should move.
  Also unresolved, separately noted by that def's own second grimterra.biomesmod-
  gated `BiomeCypreJungle` xpath block in `BiomeCast_Ashkarr.xml`: two live defs
  (`BiomeCypreJungle` from grimterra.biomesmod, active; and `RUT_Greentide`, this
  repo's own) carry near-duplicate wildAnimals content — which one is actually
  the world-tile-assigned "the Greentide" biome was not resolved here.
- **What remains**: the_greentide's own fishTypes patch (never written, per
  above); the twilight sub-roof shoal new-def (`twilight sea`, deferred to
  diving mods per the census, non-blocking); confirming which of
  `BiomeCypreJungle`/`RUT_Greentide` is the live greentide def before anyone
  writes that patch.
