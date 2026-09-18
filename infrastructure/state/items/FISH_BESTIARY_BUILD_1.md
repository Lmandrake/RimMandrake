## spec
Full spec: `design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md`
(the ratified proposal — 32 new `RUT_` species across 8 registers on 7
waters, 4 prize items, 6 rare-catch tables, the 4 owed defs: Scald
thermophile shoal, Cathedral coolant eel, Wasteland brine-battery, Twilight
shoal). That doc's `## 6. Questions for the owner` is now fully ruled (see
its own `### Rulings (owner, 2026-09-18)` block) — read it before starting,
it settles every open call this build would otherwise have to guess at.

## verify
- Every fished water has its proposed table (buckets, weights, rare
  catches) built and validated.
- `RUT_MeeCatch`/`FaaCatch`/`LaaCatch` exist as our own items with our own
  art (not Mlie's `swfish_Faa`/`swfish_Laa`) — the ruling was OURS, not a
  MayRequire fallback pairing.
- `GREENTIDE_FISH_ITEMS_FIX_1`'s engine bug (BiomeFishTypes_Greentide.xml
  wires race defs, not item defs, into `fishTypes` — a net makes a bare
  `Pawn`) is fixed as PART of this build, not left to its own item.
- The bladderboil catch (Scald, uncommon 0.5, per the hydrocarbon
  commission's own spec) ships with THIS mod, not that commission's.
- `swfish_` four (Burra/Daggert/Nyork/See) retired once the six Weeping
  Stones RUT species land — don't retire early, don't ship both.
- `validate_patch.py` clean; live-quicktest a fishing pass on at least the
  Weeping Stones and Greentide waters (the two that changed mechanism, not
  just roster) before calling this done.

## criteria
A correct v1: all 32 species + 4 owed defs exist, wired into the correct
per-biome mod (see Watch out), every catch table resolves to a real item on
a live fishing pass, and the Greentide creature-instead-of-item bug is gone.

## Watch out
- **Mod shape is per-biome, not one shared fish mod.** The owner ruled
  "Biomes" then clarified "per-biome mods" when asked — each water's fish
  defs belong alongside that water's OWN existing biome mod (Pyrelands-style
  precedent), not a new `AshkarrWaters` mod and not folded wholesale into
  `UtinniPatches`. If a water has no dedicated biome mod yet, that's a real
  open question this build has to answer per-water, not by inventing one
  shared home to dodge it.
- **Names are final as shipped nicknames** — *coolant eel*, *the silver*,
  *the owner*, *the sailor* for the 4 owed defs. No rename pass owed; don't
  hold the build waiting on "real" names that were explicitly declined.
- The BMT pair (Cracked Lands) is now PERMANENT — don't build any
  retirement/placeholder-swap logic for it.
- `RUT_LungerFry` ships now, ahead of the Lunger creature existing in the
  roster — its parent-creature link is a forward reference, not a bug.
- Both optional hediffs (veen coolant load, drazz raw shock) ship in v1 —
  don't defer them as a "v2 polish" item.

## 2026-09-18 wave 1 (FOUNDRY, belt mode, subagent)

**Two big findings before any new code:**

1. **`GREENTIDE_FISH_ITEMS_FIX_1` was already done** by another window before
   this wave started. `src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/
   RSW_ScalefishCatch_Items.xml` (RSW_MeeCatch/FaaCatch/LaaCatch, our own
   items, own mockup art — ruling 7) and `src/RimUtinni/UtinniPatches/
   Patches/BiomeFishTypes_Greentide.xml` (wiring those items, not the race
   defs, into `BiomeCypreJungle.fishTypes`) both already exist on disk,
   headers dated 2026-09-10/citing this exact item. Verified by reading both
   files in full, not inferred from a filename. Nothing to build here.
2. **The Cathedral coolant eel (owed def §4.2) was already built**, under
   `RUT_CoolantEel` (not `RUT_Veen`), in `src/RimUtinni/RustCathedralHum/`
   (`RUST_CATHEDRAL_MECHANICS_1`, predates the fish commission). Its shipped
   label is literally "coolant eel" — which already satisfies owner ruling 5
   (nicknames are the shipped names) with zero rename needed. Full mechanism
   already wired: `RUT_RustCathedral_Fishing.xml` (fishTypes/
   maxFishPopulation), `RUT_NegativeFishingOutcomes.xml` (the electrical-burn
   outcome), `RM_CathedralFishing.cs` (hum/goodwill Harmony hooks). Only the
   optional coolant-load hediff was missing (see below) — did not otherwise
   touch or rebuild this mod.

**Built this wave (all `validate_patch.py` clean, 0 errors — see Verify):**

- **The 3 remaining owed defs** (§4 of the spec): `RUT_Eesh` (Scald
  thermophile shoal), `RUT_Drazz` (Wasteland brine-battery), `RUT_Niim`
  (Twilight shoal) — full stats/description per each spec block.
- **The Scald's full table** (§2E): `RUT_Muddal`, `RUT_Karrash`, `RUT_Saal`,
  plus `RUT_BladderboilCatch` (the hydrocarbon commission's §10c fifth line —
  ruling 8, this mod owns it; the `RUT_Bladderboil` wildAnimals pawn is
  explicitly NOT built here, that's the hydrocarbon commission's own
  creature-roster scope). `RUT_RareScaldCatches` ThingSetMakerDef — ONE
  option only (karrash x2); the pigment-scrap option is omitted per the
  doc's own instruction, since `the_scald.json`'s welcome-blanket pigment
  product def does not exist yet. **Wired directly into `RUT_TheScald.xml`**
  (fishTypes + maxFishPopulation 30 + rareCatchesSetMaker), since this mod
  (UtinniPatches) already owns that BiomeDef outright — same convention its
  own `wildAnimals` block already used, no separate patch file needed.
  🔴 **MEASURED, resolving the doc's own "UNMEASURED" flag**: the Scald's
  actual wired water terrains (`RUT_ScaldWaterDeep`/`Shallow`/
  `MovingShallow`/`MovingChestDeep`) inherit `waterBodyType Freshwater` from
  Core's `WaterDeepBase`/`WaterShallowBase`/`WaterChestDeepBase` (RimSage
  direct read) — so this is `freshwater_Common`/`freshwater_Uncommon`, not
  ambiguous.
- **The Wasteland's `RUT_Tekk`** (crustacean) alongside `RUT_Drazz`, plus
  `RUT_BrinePlate` (the §2G.rare prize resource) — all built as real
  ThingDefs. **🔴 NOT wired into the `Wasteland` BiomeDef's `fishTypes` or
  `rareCatchesSetMaker`** — see the finding below; that wiring would be dead
  on arrival.
- **Both optional hediffs, ruling 4**: `RUT_BrineShock` (drazz, raw
  ingestion only, fast-decaying stun-like jolt) and `RUT_CoolantLoad` (veen —
  added to the pre-existing `RUT_CoolantEel`, additive-only XML change, no
  C#, no other change to that mod).

**🔴 New engine finding this wave (supersedes the doc's "⚑ UNMEASURED" on the
Wasteland pool terrain): fishing on the Wasteland brine pools is
ENGINE-DEAD, independent of any `fishTypes` content.** The donor `Wasteland`
BiomeDef (Mlie.AdvancedBiomes) wires both its fresh and salt water fields to
Odyssey's `ToxicWater*` terrain family, and EVERY `ToxicWater*` terrain sets
`waterBodyType Other` (Core's `ToxicWaterDeepBase`/`ToxicWaterShallowBase`/
`ToxicWaterChestDeepBase`, read via RimSage). `Verse.WaterBody.SetFishTypes()`
(read directly, `read_csharp_symbol`) switches ONLY on `Freshwater` and
`Saltwater` — `Other` falls through and does nothing, so `HasFish` can never
become true and `Zone_Fishing`/`FishingUtility` can never produce a catch on
this biome's water, full stop. This is on top of (and independent of) the
donor's own `maxFishPopulation 0`. **Open question for wave 2 or the owner**:
the brine-battery archetype needs a delivery mechanism OTHER than
rod-fishing (mining the pool floor, a GenStep scatter, a caravan/quest
reward) if `RUT_Tekk`/`RUT_Drazz`/`RUT_BrinePlate` are meant to reach the
player at all. Not decided here — the items exist and are ready for
whichever mechanism gets chosen.

**Deferred to wave 2+** (not started, no partial/broken state left behind):

- **Weeping Stones** (6 new species + `swfish_` retirement) — untouched.
  Per the brief's own sequencing rule, `swfish_Burra/Daggert/Nyork/See`
  are NOT retired since the six RUT species were not built this wave.
- **Cracked Lands** (`RUT_Tubbik`/`RUT_Zhurr`/`RUT_Hurrok`/`RUT_Vhessa` + the
  `RSW_RareSandCatches` rare-table addition) — untouched; the BMT pair and
  `RSW_DuneCrawler` stand exactly as already shipped.
- **Greentide's remaining 7 new species** (`zeev`/`uvva`/`karrun`/`dubbol`/
  `lozh`/`saava`/`tuun`), `RUT_RareGreentideCatches`, and `RUT_LungerFry` —
  untouched. The brief's item 6 (ship the fry now) was conditional on
  reaching the Greentide table this wave; since the fry's own home is that
  table's rare-catch set (not yet built), it's deferred with the rest rather
  than built as an orphan.
- **Twilight's remaining 7 species** (`pallu`/`tikkarr`/`nuudal`/`kellu`/
  `murrol`/`hollu`/`oobo`) and `RUT_RareTwilightCatches` — untouched. `niim`
  lands alone this wave, still correctly HELD (no `fishTypes` binding, same
  reason the design doc gives: `RUT_TwilightSea` is one shared surface+deep
  BiomeDef).
- Per-biome mod homes for Weeping Stones/Cracked Lands (`ZBiome_DesertOasis`/
  `ZBiome_Badlands`) remain an open question per the ruling's own "Watch out"
  text: no dedicated mod exists for either water beyond `UtinniPatches`
  (which already carries their existing fish patches, predating this
  ruling). Not resolved or changed this wave — flagged, not silently decided.

**Verify — this wave's files only:**
`validate_patch.py` run twice on the 8 touched/new files: static (0 errors,
1 warning), then again with `--defs` against RimWorld's Data + the full
workshop content folder + the deployed Mods folder — **635/635 active mods
found on disk, 8,854 def files, 0 errors, 1 warning** (the same pre-existing
`RUT_CoolantEel` placeholder-texPath advisory, not introduced this wave;
every `ParentName` — `FishBase`/`ResourceBase`/`RareFishingCatchesBase` —
resolved clean against the real load set). No live bridge fishing quicktest
this wave — bridge time went to the engine-mechanism research above instead
(the Wasteland finding); a live Scald-water fishing pass is owed before
calling that table done.

**Git**: see the commit this section ships with.
