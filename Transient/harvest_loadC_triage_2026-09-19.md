# Harvest Load C triage — 2026-09-19

Context: first full-list load after Biomes! Caverns OUT, Biomes! Polluted Lands OUT,
10 rut.*ArtOverride mods OUT, LanternDeeps IN (ten renamed plants).
Comparison baseline: Load B triage (`Transient/harvest_loadB_triage_2026-09-18.md`), Caverns still in.

Counts: cross-reference 221 (Load B 181), Scribe 105 (Load B 10), configerror 168 (Load B 169), patchfail 106 (Load B 16), Outer Rim 8 (unchanged).

## cross-reference

221 lines. `--show crossref` output: `Transient/_lc_crossref.txt`.

**Pre-existing, unrelated to today's cuts** (147 of 221):
- `RUT_VentForge` x109 / `RUT_VentKiln` x38 (`wanter=recipeUsers`) — both ThingDefs are on
  `src/DEPLOY_HOLD.txt` ("no art yet", 2026-09-13/14, FORGE_MECHANICS_1). Deliberately
  undeployed; every recipe that lists them as a `recipeUsers` entry dangles. Same as Load B.
- `Pawn_Squirrel_Call` SoundDef x4, `RUT_TibannaGas` x1 (also DEPLOY_HOLD), `RM_GreentideChurnmud`
  x1 — unchanged from Load B.
- 6 more DEPLOY_HOLD casualties not called out individually in the Load B triage but present
  under the same mechanism: `RUT_DeadCreep`, `RUT_FoundrySalvageCache`, `RUT_FoundryTowerEntrance`,
  `RUT_ScaldVent`, `RUT_Filth_MouseTrack` (all "no art yet" holds, 2026-09-13/14) and
  `RUT_DigShaft`'s missing `Misc13` KeyBindingDef (unrelated cosmetic hotkey gap). None of these
  are fallout from the mod cuts.

**Ongoing, separate from the Biomes! cut (deploy-lag, same root cause as Load B, now bigger):**
10 distinct `RSW_*` PawnKindDef-not-found lines (Scavrat, Scurrier, Runyip, Shaak, Shiro,
ShiroTrap, Shyrack, Skalder, Sketto, Strill) + `RSW_Qormot` BodyDef, `RSW_Leather_Ronto`/
`RSW_Ronto_Meat` ThingDef, `RSW_SW_GoldForage` Ability+Trainable, `EmptyAICore` x2 — this is the
SWBestiary deploy-lag / real `EmptyAICore` bug Load B already diagnosed, now larger because more
species have been added to `BiomeCast_Ashkarr.xml`/`cast_assignment.csv` (see recent commits,
MLIE_FAUNA_ABSORPTION_1) faster than SWBestiary redeploys. Not related to the Caverns/Polluted
Lands cut.

**NEW, directly caused by the two Biomes! cuts (23 distinct BMT_ plant names, ~28 lines):**
`BMT_Arpeau, BleedingTooth, Brightbells, CrimsonCap, Dewshrooms(x2), FireLavender,
FlakespireFungus, FruitingBodies, GiantLeaf(x2), GreyLady, HeatsinkFungus, MortalMorelPlant,
Nogtyl, Nuitae, Pusmelon, RustPuff, Sagecrust(x2), Shinecap, Skulltop, VioletWimple, Wrinklecap`
— all `RimWorld.BiomePlantRecord` references. Traced `BMT_GiantLeaf` to OUR own biome content:
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FeverWood.xml`, `RUT_Greentide.xml`, and
`src/RimUtinni/UtinniPatches/Patches/BiomeFlora_Ashkarr.xml` — these still list Biomes!
Caverns/Polluted Lands plant defNames in their plant rosters. **OURS.** The fauna-side purge
already underway (`design/Jawa/fauna/BiomeCast_Ashkarr.xml`, `cast_assignment.csv` — both
modified in this session's git status) has NOT yet reached the flora side
(`design/Jawa/mods/biome_flora.py`, `plant_pool.csv` — untouched).

No LanternDeeps defName (`RUT_Deep*`, `RUT_Lantern*`, `RUT_Thrakk*`, `RUT_Ossk*`, `RUT_Vellok*`,
`RUT_Prenna*`, `RUT_Nurrik*`, `RUT_Quorr*`, `RUT_Zivvit*`, `RUT_Kuvra*`, `RUT_Brellik*`,
`RUT_TwitchingPuffer`, `RUT_PufferTendrils`) appears anywhere in crossref, scribe, configerror
or patchfail — grepped all four raw dumps, zero hits.

## scribe

105 lines (Load B: 10). `--show scribe`: `Transient/_lc_scribe.txt`.

**All 105 come from ONE file**: `Config/Mod_3532608331_DeepStorageMod.xml` (Deep Storage's mod
settings, `<ModSettings Class="LWM.DeepStorage.Settings">`), read at
`/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/`.
Grepped it directly: 96 distinct `BMT_*`/`TYR_*` defName `<li>` entries in a stored things-list
field, including the exact compound names the log reports dead (`Meat_BMT_Maxolotl`,
`Meat_TYR_HotfootRat`, `Corpse_BMT_*`, `BMT_Egg*Fertilized/Unfertilized`, etc.). 5 `TYR_` names
(the same 10 Meat+Corpse lines unchanged since Load B) plus ~95 new `BMT_` lines match the
Biomes! Caverns/Polluted Lands cut exactly. `pokean.xtp` (the OTHER file implicated in the
2026-08-22 cleanup per CLAUDE.md) has **zero** `BMT_`/`TYR_` hits this time — not involved.

**A one-time settings clean (strip the dead `BMT_`/`TYR_` `<li>` entries from that one XML,
same as the 2026-08-22 cleanup) would fix all 105 lines.** This is a live Windows Config file,
not a repo file — not edited here (read-only investigation; the fix is a live-game action for
whoever owns Deep Storage's mod settings).

## configerror

168 lines / ~125 distinct-vs-stale-baseline (`check_config_errors.py` against the 2026-09-06
baseline: `Transient/_lc_checkconfig.txt`). Raw dump: `Transient/_lc_configerror.txt`.

**Bulk, not a defect (~50 lines):** `RM_LiquidProperties does nothing beyond documenting
viscosity...` on ~26 distinct TerrainDefs x2 — FlowWorks' own authoring check, ruled canon
2026-09-13. Same as Load B.

**Carried over from Load B, unchanged, OURS (still open, not urgent):** `RSW_*Juv` (Mee/Faa/Laa/
Yobshrimp/SiltLamprey/RustNipper/OpeeSeaKiller) lifeStages ordering; `Utinni
Shellmandrake.rut.menushell` malformed defName; `RUT_BrineDeposit_{Tekk,Drazz,BrinePlate}`
compressible-claimable; `RUT_BrinePlate` null graphicClass; `RUT_TwinkleSpikeTestPlant` (leftover
test content); `RUT_Slough_GelatinousBreach`/`RUT_ComplexStructures` landmark mutator gaps;
`RSW_Orray` Teeth; `RSW_KilnClay` food-serve warden bug risk; `RSW_ToxinDependence` null
needClass.

**Third-party, unrelated:** ModernFixtures/RR_Furniture + AdvancedShowers/VCE_StewCooking
research-tab collisions, RR_LateralThinking/RR_Organization researchView, AM_AncientLogisticsSystem
+ 4x guy762_* Hyperweave tradeability, TargetedInsultingSpree label chars, Techprint_RR_lighting
trailing whitespace, Eclipse/Aurora/SolarFlare "world-targeting incident has a biome restriction
list" (cosmetic, third-party incident defs).

**NEW since Load B, worth flagging:** the NullReferenceException-in-`ConfigErrors()` cluster grew
from 3 biomes (AridShrubland, Desert, ExtremeDesert — already flagged, unresolved) to 5:
**+`AB_MiasmicMangrove`, +`BiomeCypreJungle`**. Same unexplained NRE, now spreading to more biome
defs — still no stack trace in the harvested lines to root-cause; plausibly the same
FlowWorks/plant-roster wiring the crossref section's BMT_ cluster points at (a biome's
`ConfigErrors()` walking a plant/animal roster that now contains a dangling BMT_ reference).
Not confirmed — needs the full exception text.

## patchfail

106 lines (Load B: 16). `--show patchfail`: `Transient/_lc_patchfail.txt`.

**Pre-existing (≈16, same as Load B):** Torment Master→HAR FindMod, Vanilla Mining Outpost
Patch→Gemstones FindMod, Intimacy x3 Remove, RimStarWars Patches→ABF FindMod x5 +
`OuterRim_DroidWeapon_*` weaponTags Conditional x4 (see `outerrim` note below — `harvest_log.py`
has no separate `outerrim` key; those 4 lines live inside `patchfail`), Jawa Pawn Flavor→KotOR
Resources FindMod. Biomes! Caverns' own PlaceWorker-Replace baseline entry is simply GONE now
(the mod itself is uninstalled, so it can't log a failure any more).

**NEW, ~90 lines, ALL OURS, ALL the same shape** (`PatchOperationConditional` on a `BMT_*`
defName's xpath, no match because Caverns/Polluted Lands are gone — this class of op no-ops
harmlessly per the repo's own "Conditional/FindMod return true on no match" rule, but still logs
"failed" and is pure noise from here on):
- `src/RimStarWars/Armoury/Patches/Absorbed_AdditionalMods/kotorweapons/BiomesCaverns/
  Absorbed_Kotorweapons_BiomesCaverns_Patch_KotORCrystalFormationInjector.xml` — 1 line,
  `PatchOperationAdd` on `GenStepDef[defName="BMT_CrystalsGenerator"]`, shown under mod name
  "Jawa Armoury Rebalance". This is donor-absorbed content (WEAPONS_DONOR_RETIREMENT_1) that
  targeted Caverns' own genstep; now permanently dead since Caverns is out. Candidate for
  deletion or a `PatchOperationFindMod("Biomes! Caverns")` guard.
- `src/RimStarWars/SWBestiary/Patches/SeasWaterline/Waterline_Lane1.xml` — 5 lines, `/race/
  wildBiomes` Conditional on `BMT_MucklurkerCatfish`, `BMT_TaintedTurtle`,
  `BMT_MutatingTumorfishSpawn/Fry/Adult`, shown as "RimMandrake: SW − Bestiary".
- `src/RimStarWars/StarWarsPatches/Patches/WeaponTags_Renormalise.xml` — 10 lines, `weaponTags`
  Conditional on `BMT_BlastSpore/BunkerClaw/CaveSpiderHead/CrystalMantisClaw/FungalMantisClaw/
  PustuleHornetStinger/ResourceBlueCrystal/RoyalRhinoHorn/ThrumbungusShroom/Toxwood`.
- `src/RimUtinni/UtinniPatches/Patches/AnimalTolerances_Ashkarr.xml` — **the big one**, ~74 lines
  + 1 `PatchOperationSequence` failure (`BMT_Thrumbungus` lifeStages), all `statBases`
  temperature-band Conditionals. This file is **GENERATED** (header: "GENERATED by
  design/Jawa/fauna/animal_tolerances.py - do not hand-edit") and still carries 592
  `defName="BMT_...` entries across the whole file (most of the file, not just the failing
  lines) from before the Caverns/Polluted Lands cast members were dropped.
  ⛔ **Do not hand-edit this file.** Fix = regenerate it (`animal_tolerances.py`) once
  `cast_assignment.csv`/`BiomeCast_Ashkarr.xml`'s already-in-progress purge of the cut species is
  complete and redeploy.

## outerrim

`harvest_log.py --show outerrim` is not a valid key (valid keys: dead, reflect, defdiscard,
crossref, scribe, harmonyfail, tex, configerror, patchfail, dictshape, deadnames — confirmed via
`--help`). The 8 "Outer Rim new-mod errors" the summary counts are the 4
`PatchOperationAdd(ThingDef[defName="OuterRim_DroidWeapon_*"])` xpath-not-found lines plus their
4 dependent `weaponTags` Conditional no-ops, both already counted inside `patchfail` above and
unchanged from Load B — third-party OuterRim mod version mismatch, not caused by today's cuts.

## Verdict

1. **No LanternDeeps def appears anywhere in any of the four classes** — grepped all raw dumps
   for every `RUT_Deep*/Lantern*/Thrakk*/Ossk*/Vellok*/Prenna*/Nurrik*/Quorr*/Zivvit*/Kuvra*/
   Brellik*/TwitchingPuffer/PufferTendrils` prefix, zero hits. LanternDeeps' own CAVERNS_PARITY
   work already decoupled it from `BMT_CrystalsGenerator` before this load (comment in
   `RUT_LanternDeepGenerator.xml`); it deployed clean.
2. **Single most important finding**: nearly all of the new patchfail volume (~90 of 106) and
   ALL of the new Scribe volume (95 of 105) trace to the SAME unfinished cleanup — Caverns/
   Polluted Lands (`BMT_*`) species are still listed in generated/saved data that hasn't caught
   up with the mod cut. Fix `src/RimUtinni/UtinniPatches/Patches/AnimalTolerances_Ashkarr.xml`
   by regenerating it from `design/Jawa/fauna/animal_tolerances.py` (never hand-edit — do this
   after the in-progress `cast_assignment.csv`/`BiomeCast_Ashkarr.xml` species purge lands), and
   separately purge the flora side (`design/Jawa/mods/biome_flora.py` / `plant_pool.csv`) which
   feeds `RUT_FeverWood.xml`/`RUT_Greentide.xml`/`BiomeFlora_Ashkarr.xml`'s dangling BMT_ plant
   entries.
3. Scribe's 105 lines are ALL one live-game settings file, not a repo file: `Config/
   Mod_3532608331_DeepStorageMod.xml` (Deep Storage settings) — a one-time settings clean
   removing its dead `BMT_`/`TYR_` `<li>` entries fixes all 105 in one pass, same mechanism as
   the 2026-08-22 cleanup. `pokean.xtp` is NOT implicated this time.
4. Two small OURS patch files carry real, guardable fallout: `Absorbed_Kotorweapons_
   BiomesCaverns_Patch_KotORCrystalFormationInjector.xml` (Armoury, targets Caverns' genstep
   directly — dead now, needs deletion or a FindMod guard) and `SeasWaterline/Waterline_Lane1.xml`
   + `WeaponTags_Renormalise.xml` (5 + 10 Conditional no-ops on cut BMT_ species — harmless but
   worth a FindMod("Biomes! Caverns")/("Biomes! Polluted Lands") gate to quiet the log).
5. Everything else (RUT_VentForge/Kiln DEPLOY_HOLD cluster, SWBestiary deploy-lag/EmptyAICore,
   OuterRim xpath mismatch, liquids "authoring check" configerrors) is unchanged from Load B or
   a separate, already-tracked issue — not fallout from today's two Biomes! cuts.
