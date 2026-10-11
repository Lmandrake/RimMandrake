# Retirement wave 1 - offline lint, hard deps, reduced-tree refs (2026-10-10)

Source: origin/main FULL.LATEST (551). Everything offline; mirror cwd `D:\Luke\dev\RimMandrake` (== origin/main for effective_def_lint.py and costlist_resolve_check.py, cmp-verified).

## 1. Lists built
- `infrastructure/state/modlists/ModsConfig.WAVE1_CANDIDATE.xml`: 551 -> **514** (37 removed, all 37 present in FULL incl. vlvop.tormentmaster.expansion; it is in the list but NOT installed, so only its list entry drops). det.epochspyrinth -> mandrake.rm.pyrinth at the same position (index 130 in FULL; 119 after removals before it - assert passed).
- `ModsConfig.WAVE1_CANDIDATE_PLUS_SHELLS.xml`: **510** (+ xmb.ancienturbanruins.mo, meteores.ancienturbanruinsalldeconstructible.aurad, meteores.ancienturbanruinsvanillaloot.aurvl, redmattis.bigsmall).
- version / knownExpansions unchanged. Files re-serialised through ElementTree (2-space indent, quote style of the xml declaration differs trivially).
- mandrake.rm.pyrinth DEPLOYED: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Pyrinth\About\About.xml` (packageId mandrake.rm.pyrinth).

## 2. Hard-dependency check (About.xml of every remaining active mod, both roots)
- **modDependencies on a removed id: NONE** in either candidate.
- loadAfter / loadBefore / incompatibleWith naming removed ids (harmless, ordering only): vanillaexpanded.skills (petetimessix.researchreinvented loadBefore); sarg.alphamechs (frozensnowfox.complexjobs); vanillaquestsexpanded.ancients (mandrake.rut.doctrine, mandrake.rut.patches); mandrake.rsw.armoury -> aoba.warcasket, clown.dedicatedturrets, hmc.wall.furniture, milkwater.destinymod, sarg.alphamechs, vanillaexpanded.vwe; mandrake.rsw.patches -> vanillaexpanded.vwe; mandrake.rut.patches -> armoredampharos.fancyrats; mandrake.rm.biomes loadAfter det.epochspyrinth; mandrake.rm.pyrinth incompatibleWith det.epochspyrinth (intended).
- SHELLS only, extra: danzinagri.facialanimationcompatabilityproject loadAfter redmattis.bigsmall; mandrake.rsw.armoury / rsw.patches / rut.patches loadAfter xmb.ancienturbanruins.mo.

## 3. effective_def_lint diff vs FULL baseline
Baseline FULL: VERDICT FAIL on failed_ops only (3 findings, all pre-existing: AncientsAreRakata.xml Sequence+FindMod, VQEPatients_AreRakata.xml FindMod). 0 crash anywhere. costlist/recipe_refs/stuff_refs/removed_refs/drug_comp/pawnkind_race/biome_worker/li_custom_loader/plant_purpose/faction_name: 0 findings in all three runs.
Both candidates: **crash 0**.

| check | base | CANDIDATE | +SHELLS |
|---|---|---|---|
| failed_ops | 3 | 8 (+6, -1) | 8 (+7, -2) |
| op_mayrequire (warn) | 24 | 21 (-3, gone with removed mods) | 21 |
| unsupported_patch_ops (warn) | 81 | 106 (+27 frozensnowfox.complexjobs Optional/SafeAddOrReplace, -2) | 106 |

NEW error-class findings (all `failed_ops`, our files, each logs an error, no crash):
- `src/RimStarWars/StarWarsPatches/Patches/WeaponTags_Renormalise.xml`: 6 PatchOperationConditional on AM_BeamGraserCannon, AM_Gun_GoliathChargeBlaster, AM_Gun_SuperHeavyChargeBlaster, AM_Gun_TacticalShotgun, AM_MechanoidGunRotaryNeedle, AM_StarfireTurret (matches expected +6; sarg.alphamechs removal). Both candidates.
- SHELLS only: `src/RimUtinni/UtinniPatches/Patches/AncientArsenal_Ashkarr.xml` - Conditional on `PawnKindDef[AncientSoldierBoss]/weaponTags/li[IndustrialGunAdvanced]` with nomatch PatchOperationAdd on a now-absent PawnKindDef (**NOT in the deepdive's expected list**).
Gone: `VQEPatients_AreRakata.xml` FindMod (both); SHELLS also drops the `AncientsAreRakata.xml` FindMod (Sequence entry remains).
Warn-only complexjobs noise: its XmlExtensions Optional patches read differently once alphamechs is gone - not a load error.

costlist_resolve_check on CANDIDATE: 1 miss = Meat_Human in CannibalPlatter (Ideology; identical to baseline, implied def).

Command lines (cwd `D:\Luke\dev\RimMandrake`, i.e. /mnt/d/Luke/dev/RimMandrake, python.exe; lists copied to `D:\Luke\dev\_rmscratch\rw1\`):
`python.exe src/RimMandrake/Utils/effective_def_lint.py 'D:\Luke\dev\_rmscratch\rw1\ModsConfig.<NAME>.xml' --json 'D:\Luke\dev\_rmscratch\rw1\lint_<NAME>.json'` (NAME = FULL.LATEST | WAVE1_CANDIDATE | WAVE1_CANDIDATE_PLUS_SHELLS; a cold candidate run is ~5 min). JSONs copied to `/home/mandrake/.seat-tmp/rw1/lint/lint_*.json`; diff script `/home/mandrake/.seat-tmp/rw1/lint/diff.py <NAME>`. Append `packageId=C:\folder` for overrides.

## 4. Reduced-tree surviving references (wave_scan.py: effective patched tree of candidate; removed = FULL minus candidate, incl. det.epochspyrinth)
Script `/home/mandrake/.seat-tmp/rw1/lint/wave_scan.py`; outputs `scan_<NAME>.json`. Sanity probe Steel/Gun_Revolver/Muffalo all present. CANDIDATE: 70 refs, SHELLS: 69. Kinds seen: text-node refs only (0 class_ref, 0 tag). None are MayRequire-guarded (a guarded one pointing at an absent mod is stripped before the scan).
**Caveat: most hits are FALSE POSITIVES from generic words** (a removed mod defines a def named Major/Minor/Butcher/Surgeon/Candles/Foreman and the survivors use the same word as an enum or label). The scan cannot see C# references.

### Ours (mandrake.*), unguarded
| our def | src path | text | verdict |
|---|---|---|---|
| RM_GraffitiPaintingSpreeBreak | src/RimMandrake/Graffiti/Defs/MentalStateDefs_Graffiti.xml | intensity `Major` | false positive (MentalBreakIntensity enum) |
| RM_Witness_ButcherBolt | src/RimMandrake/RustCathedral/Defs/ThingDefs_Races/RM_HullBolt.xml | kind `Butcher` | false positive (own enum) |
| RUT_Jawa_RakataTakenChild, RUT_Jawa_RakataFleshShaped | src/RimUtinni/PawnFlavor/Defs/Backstories_Rakata_Sleepers.xml | spawnCategories `VQE_Experiment` | real but harmless: category string from vanillaquestsexpanded.ancients, these backstories just stop being picked by VQE |
Ours patch ops naming removed names/mods: 76 guarded and fine; 6 unmatched = the WeaponTags_Renormalise AM_ rows (guarded Conditionals, still log an error). SHELLS adds AncientArsenal_Ashkarr.xml (above). Patch-op sites in our src (all guarded: FindMod/Conditional): mandrake.rsw.armoury (Armour_*.xml, Armoury_RangedDamage.xml, Turrets_*.xml, Absorbed kotorweapons patch), rsw.patches WeaponTags_Renormalise.xml, rut.patches (BiomeCastEvictions_WildBiomes.xml 22, AnimalBiomeDuplicates_Fix.xml, AnimalTolerances_Ashkarr.xml, GalacticEmpire.xml, HomesteadDefenseLeague.xml, VQEPatients_AreRakata.xml, VQEQuestText_AreForsaken.xml, VREArchon_MortisRename.xml, XenotypeCut_SpawnSets.xml), rut.doctrine MegafaunaYield.xml, rut.researchretag (RUT_ResearchRetag.xml / RUT_ResearchTabAssign.xml), rm.biomes LanternDeeps RM_LanternDeepGatePyrinth.xml, rsw.jawavoice JawaVoice_Interactions.xml, rm.pyrinth Absorbed_EpochsPyrinth patches.

### Third party, unguarded (68)
- sarg.alphamechs (22): iforgotmysocks.caravanadventures CompatibilityDef `mechanoidBountyToAdd/raceDefName` x21 (AM_* races) - custom def class, unsupported by the offline engine: runtime risk not proven; kilokio.rimai.core ResearchProjectDef RimAI_Subspace_Gravitic_Penetration prerequisites -> AM_Cryptoharmonization (a dead research prerequisite: check live log).
- vanillaexpanded.vwe (3): andromeda.niceresearchtab FineTune defs (research/thing names) - custom def, low risk.
- mlie.beastsoftherim (2): vanillaexpanded.vgeneticse RecipeDef Corpse_Penguin - false positive (Penguin race is defined by a surviving mod; the scan's implied-corpse list is not shadow-aware).
- van.dacrypts (1): dizzy.candlesandmeditation label `Candles` - false positive.
- vanillaexpanded.skills (38): Major/Minor intensity enums, complexjobs/vanillabackstoriesexpanded labels (Butcher, Surgeon, Driller, Trainer, Foreman) - false positives. 
- loadAfter: see section 2. string-only: none beyond the above.

## 5. Verdict
**crash-class: 0** (no crash finding in any of the three lint runs; hard-dep check clean; no verified crash path in the reduced-tree scan, which cannot see C#).
Error-class to fix before/with the wave: WeaponTags_Renormalise.xml (6 AM_ rows, guard them with FindMod/def-exists), and for SHELLS AncientArsenal_Ashkarr.xml AncientSoldierBoss add.

## 6. Final re-run (FOUNDRY, after the fixes landed; supersedes the PLUS_SHELLS numbers above)

- `ModsConfig.WAVE1_CANDIDATE_PLUS_SHELLS.xml` was rebuilt with **3** shells (511 active): the census found
  `xmb.ancienturbanruins.mo` not save-safe, so it stays; the `AncientArsenal_Ashkarr.xml` finding above disappears with it.
- Both candidates re-linted with overrides `mandrake.rsw.patches`, `mandrake.rut.researchretag`, `mandrake.rut.patches`,
  `mandrake.rut.doctrine`, `mandrake.rut.greentideraidant`, `mandrake.rsw.armoury`, `mandrake.rm.luminouspigment` =
  their `D:\Luke\dev\RimMandrake\src\...` folders: **crash 0**; `failed_ops` = only the 2 pre-existing
  `AncientsAreRakata.xml` rows; the six AM_ rows are gone. Logs: `/home/mandrake/.seat-tmp/rw1/final_WAVE1.log`, `final_SHELLS3.log`.
- Trap hit on the way: `echo` in zsh interprets backslash escapes, so an override list saved with `echo` lost
  `\U...` path parts and one run silently dropped UtinniPatches (372 fewer files, a false crash finding). Save
  Windows paths with `printf '%s\n'`.
