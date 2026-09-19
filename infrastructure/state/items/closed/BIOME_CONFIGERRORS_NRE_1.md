# BIOME_CONFIGERRORS_NRE_1

## Mechanism (found via RimSage, no fresh log needed)

`RimWorld.BiomeDef.ConfigErrors()` (`RimWorld/BiomeDef.cs` lines 507-545) gates its
whole body on `Prefs.DevMode`, then walks `wildAnimals` (and, with Biotech/Odyssey,
`pollutionWildAnimals`/`coastalWildAnimals`) doing:

```csharp
foreach (BiomeAnimalRecord wa in wildAnimals) {
    if (wildAnimals.Count(a => a.animal == wa.animal) > 1)
        yield return "Duplicate animal record: " + wa.animal.defName;
}
```

If **two or more** entries in the same list have an unresolved (null)
`BiomeAnimalRecord.animal` cross-reference, `null == null` makes the LINQ
`Count` see them as "duplicates" (>1), and the yield line then dereferences
`wa.animal.defName` on a null `wa.animal` -> the reported `NullReferenceException`.
One unresolved entry alone does not crash (`Count` == 1); it takes at least two
in the same biome's list.

## Root cause is NOT a dangling BMT_ reference

The filer's leading hypothesis (a dangling `BMT_` plant/animal ref) does not fit:
the ConfigErrors() loop above only ever walks **wildAnimals** lists — never
`wildPlants` (`BiomePlantRecord`), so the harvest's 23-name `BMT_*` plant
crossref cluster (traced to `RUT_FeverWood.xml`/`RUT_Greentide.xml`/
`BiomeFlora_Ashkarr.xml`) cannot be the trigger for this specific NRE at all.

The actual match: `Transient/_lc_crossref.txt` (Load C harvest) has ~30 lines of
`Could not resolve cross-reference: No Verse.PawnKindDef named RSW_<X> found to
give to RimWorld.BiomeAnimalRecord` for `RSW_Scavrat/Sketto/Strill/Skalder/
Shiro/ShiroTrap/Shyrack/Scurrier/Shaak/Runyip` — already noted in the harvest
doc as "the SWBestiary deploy-lag / real EmptyAICore bug Load B already
diagnosed", explicitly called out there as unrelated to the Caverns/Polluted
Lands cut. Mapping `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`'s
line ranges to each biome's `<xpath>` block confirms every one of the 5 crashing
biomes has >=2 of these RSW_ PawnKindDef refs added to its own `wildAnimals`:
Desert (6: Scavrat/Shyrack/Sketto/Skalder/Shaak/Runyip), AridShrubland (5:
Scurrier/Sketto/Scavrat/Strill/Skalder), ExtremeDesert (2: Scavrat/Scurrier),
AB_MiasmicMangrove (2: Runyip/Shiro), BiomeCypreJungle (2: Shiro/ShiroTrap) —
which is exactly why Mangrove/CypreJungle only joined the crash cluster once
`BiomeCast_Ashkarr.xml`'s fauna-wave additions (MLIE_FAUNA_ABSORPTION_1) gave
each of them a second RSW_ entry.

The RSW_ PawnKindDefs themselves are real and correctly authored in
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_*.xml` (each file defines
both the `ThingDef` and a `PawnKindDef` of the same name) — this was a
deploy-lag artifact, not a dead/renamed defName.

## Current live session: does NOT reproduce (checked, not fabricated)

Player.log at `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by
Ludeon Studios/Player.log` (this BELT session's live game, full 620-mod list,
DevMode confirmed on — see below) shows:
- Zero `Exception in ConfigErrors() of <Desert|AridShrubland|ExtremeDesert|
  AB_MiasmicMangrove|BiomeCypreJungle>` lines (the exact format `DefDatabase.cs`
  line 204 emits). Only 2 NRE-in-ConfigErrors lines total, both unrelated
  `FactionDef`s (`CannibalPirate`, `PirateYttakin`).
- Zero `Could not resolve cross-reference ... PawnKindDef named RSW_*` lines
  (185 crossref failures total, none of them RSW_ PawnKindDefs). `RSW_Scavrat`
  appears 20x as `Added RSW_Scavrat to <biome> with commonality ...` — i.e. it
  resolves and is being distributed successfully.
- `AB_MiasmicMangrove`'s `ConfigErrors()` visibly completed without crashing:
  it logged `Config error in AB_MiasmicMangrove: Duplicate animal record:
  RSW_Yobshrimp` twice — proving (a) DevMode is on this session (that whole
  code path is DevMode-gated) and (b) the loop ran to completion for this
  biome with a genuine, unrelated duplicate (RSW_Yobshrimp listed twice in its
  wildAnimals — a separate, non-crashing authoring nit, not investigated
  further here).

Conclusion: the specific null-crossref condition that produced the Load C
crash appears to have been resolved by the time of this live session (SWBestiary
drift check via `deploy_custom_mods.py --mod SWBestiary` shows no drift on any
`ThingDefs_Races/RSW_*.xml` file today — only unrelated art/DLL/Livestock
drift). This is evidence from one already-running session's log, not a
from-scratch reproduction attempt, so it narrows rather than closes the item:
**a fresh full-list cold load, harvested for the exact
`Exception in ConfigErrors() of <biome>` line and full stack trace, is still
the way to confirm this is actually gone** rather than merely absent from one
session's timing/order. No repo file was edited — there was nothing dangling
to fix; the previous condition was live-deploy state, not a defect in any
committed def.

## Next steps if it reproduces again

Pull the full stack trace's line number is moot (the source above already
pins the exact line: the `wa.animal.defName` yield in `BiomeDef.ConfigErrors()`)
— on a repro, just re-run the crossref harvest and confirm which RSW_/BMT_/etc.
PawnKindDef names are unresolved in the affected biome's `wildAnimals`/
`pollutionWildAnimals`/`coastalWildAnimals` at that moment, then fix the actual
dangling name or redeploy whichever mod owns it. No engine-side fix is
available to us (vanilla `BiomeDef.ConfigErrors()`); the durable fix is never
letting two simultaneously-unresolved entries sit in the same biome's animal
list, i.e. keeping mod deploys in step with `BiomeCast_Ashkarr.xml` edits.
