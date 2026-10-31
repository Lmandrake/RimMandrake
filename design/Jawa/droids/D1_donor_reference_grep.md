# Droid Donor Reference Audit — D1_donor_reference_grep
**Re-grepped:** 2026-10-31 (Opus, full re-grep; replaces the 2026-09-06 sweep)
**Scope:** every `.xml` and `.cs` in three places, whatever the active list says:
- `src/` (git-tracked files in the bench clone: 5,708 files read);
- game Mods, `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods` (100 folders; `.xml .cs .txt`);
- Workshop, `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100` (1,270 folders).

**Instrument:** `findstr /s /i` over both mod roots, then a line classifier on the 353 + 3,242 files it listed. Scripts and rows: `D:\ClaudeWork\rimmandrake\scratch\d1_donor_regrep` (`scan.py`, `rows.json`, `deps.txt`). Probe: the donors' own folders hit (Depot 282 files, Asimov 110), so a zero below is a measured zero. Case-insensitive, because `src` and the donors spell the same id differently (`neronix17.asimov` / `Neronix17.Asimov`).

**State of the donors.** `ModsConfig.xml` (next load, 321 active, parsed) lists none of the four, and not `Killathon.ArtificialBeings.SynCore` either. They are retired; this file is the record of what still names them.

| Donor | packageId | Workshop | Name |
|---|---|---|---|
| KotOR Droids | `guy762.KotORDroids` | 3047371944 | Star Wars KotOR Droids |
| ABF | `Killathon.ArtificialBeings` | 3284097810 | ABF: Artificial Beings Framework |
| Asimov | `Neronix17.Asimov` | 3096481956 | Asimov |
| Droid Depot | `Neronix17.OuterRim.DroidDepot` | 3096501398 | Outer Rim - Droid Depot |

`Killathon.ArtificialBeings.SynCore` (3288463094, ABF: Synstructs Core) is a separate mod and is counted separately.

---

## Reference counts, by occurrence

`src` / game Mods / Workshop. "Gate" is `MayRequire` on the same line. "Load order" is `loadAfter`, `loadBefore` and the `force` and `ByVersion` forms.

| Donor | Comment | Gate | Load order | modDependencies | Other live |
|---|---|---|---|---|---|
| `guy762.kotordroids` | 17 / 17 / 63 | 6 / 6 / 643 | 1 / 1 / 5 | 0 / 0 / 1 | 0 / 1 / 6 |
| `killathon.artificialbeings` (bare) | 2 / 1 / 6 | 0 / 0 / 163 | 2 / 2 / 8 | 0 / 0 / 2 | 0 / 0 / 2 |
| `...artificialbeings.syncore` | 2 / 2 / 9 | 2 / 2 / 82 | 3 / 3 / 6 | 0 / 0 / 1 | 1 / 1 / 4 |
| `neronix17.asimov` | 1 / 0 / 0 | 0 / 0 / 104 | 2 / 2 / 4 | 0 / 0 / 2 | 0 / 0 / 2 |
| `neronix17.outerrim.droiddepot` | 7 / 5 / 13 | 14 / 14 / 39 | 7 / 7 / 2 | 1 / 1 / 0 | 0 / 0 / 3 |

Workshop self-declarations (`<packageId>` in the donor's own About.xml) are left out. The "other live" rows are all explained:
- game Mods `kotordroids` 1 is `Droidworks\Defs\Absorbed_KotorDroidModules\Absorbed_KotorDroidModules_EXCLUDED_manifest.txt`, prose;
- `syncore` 1 is `Absorbed_Kotorcore_ATC_Patch_DroidIngestibleBlacklist.xml`, a `PatchOperationFindMod` whose gate is its `<mods><li>ABF: Synstructs Core</li></mods>`;
- Workshop `IfModActive` / `IfModNotActive` rows are `LoadFolders.xml` entries in `2919248699`, `2938932438`, `3254370945`, conditional by construction. The remaining Workshop rows were counted, not read line by line.

## `src`, by file

**guy762.kotordroids (24).** Gated, 6: `Absorbed_KotorWeapons_OrbitalTrader_Baragwin.xml` 3, `Absorbed_KotorWeapons_BaseTrader_Baragwin.xml` 3. Load order: `RimStarWars/Armoury/About/About.xml`. Comments, 17: `DroidDonor_ABFGate.xml` 8, `BTD_DistressCall_Repoint.xml` 5, and one each in `Absorbed_KotorDroidModules_Tech.xml`, `WeaponTags_Renormalise.xml`, `DroidsAreMachines.xml`, `PawnFlavorPhase2_Xenotype.xml`.

**killathon.artificialbeings, bare (4).** Load order: `Armoury/About/About.xml`, `StarWarsPatches/About/About.xml`. Comments: `DamageWorker_Ionize.cs`, `DroidDonor_ABFGate.xml`.

**killathon.artificialbeings.syncore (8).** Gated: `Absorbed_KotorCore__BASE_SWKotORApparel.xml` 2. Load order: `Armoury`, `PawnFlavor`, `ResearchRetag` About.xml. Comments: `Doctrine/About/About.xml`, `DroidDonor_ABFGate.xml`. Plus the ATC FindMod above.

**neronix17.asimov (3).** Load order: `Doctrine/About/About.xml`, `ResearchRetag/About/About.xml`. Comment: `BoltCorePatches.cs`.

**neronix17.outerrim.droiddepot (29).** Gated, 14: `JawaFreeDroidEnclaves.xml` 10, `JawaFactionRoster.xml` 4. Load order: `Armoury`, `StarWarsPatches`, `Doctrine`, `PawnFlavor`, `ResearchRetag`, `UtinniPatches` (2) About.xml. Comments: `StockGenerator_DWDroids.cs`, `DroidFemaleTexture_Fix.xml`, `WeaponTags_Renormalise.xml`, `GoodwillSituationWorker_RestrainingBolts.cs`, `JawaFreeDroidEnclaves.xml`, `RUT_TradeMootDroids.xml`, `FreeDroidEnclaves_LeaderFallback.xml`.

**The one hard reference:** `src/RimStarWars/MSEDroidFix/About/About.xml` has a `modDependencies` entry on Depot. The mod is inactive but still sits in game Mods. Filed: `MSEDROIDFIX_RETIRE_DEPOT_DEPENDENCY_GONE`.

## DefName references

Donor defNames read from the donors' own XML (`donor_defs.json`: Depot 234, Asimov 62, ABF 31, SynCore 335, KotOR Droids 407).

`OuterRim_*Droid*` not preceded by `RSW_DW_`, in `src`: 416 occurrences (comment 31, `MayRequire` 4, About.xml 1, live 380). No live name is defined in `src`, so all 380 are donor names:

| Where | Count | Why it cannot bite |
|---|---|---|
| `RimUtinni/ResearchRetag/Patches` | 326 | `RUT_ResearchRetag.xml`, `RUT_ResearchTabAssign.xml` and `RUT_TechprintGating.xml` test the target with `PatchOperationConditional` |
| `RimStarWars/StarWarsPatches/Patches` | 26 | `DroidFemaleTexture_Fix.xml` uses `PatchOperationConditional`; `WeaponTags_Renormalise.xml` under FindMod |
| `RimUtinni/Doctrine/Patches` | 5 | `PatchOperationFindMod` |
| `RimUtinni/UtinniPatches/Patches` | 4 | `FactionSlate/OnlyOurFactions.xml`, xpath on the absent FactionDef |
| `Droidworks/Defs/Races_OuterRim.xml` | 19 | `<description>` prose ("Absorbed from OuterRimDroidDepot (OuterRim_...)"), not references |

The `RSW_DW_*OuterRim_*` names (142 in `src`) are ours and do not reference the donor. `JawaFreeDroidEnclaves.xml` holds the 4 gated real Depot kinds.

`ABF_*` and `ArtificialBeings.*` in `src`, live: 1,011. Patches, 1,009: `PawnFlavorPhase2_ThoughtDef.xml` 847, `RUT_TechprintGating.xml` 52, `RUT_ResearchRetag.xml` 48, `RUT_ResearchTabAssign.xml` 24, `DroidDonor_ABFGate.xml` 18, `PawnFlavorPhase2_MentalBreak.xml` 18, the ATC blacklist 2. All sit in FindMod or Conditional operations. The other 2 are the C# below.

`Asimov_*` in `src`, live: 19, all Patches: `Asimov_WirelessCharging` 16 (ResearchRetag), `Asimov_Automaton` 3 (`DroidsAreMachines.xml`, FindMod on `Asimov`).

**C# reference to a donor type:** `src/RimStarWars/Armoury/Source/guy762_IonizationABF/DamageWorker_Ionize.cs` has `using ArtificialBeings;` and calls `ABF_Utils.IsArtificial` twice, in `DamageWorker_Ionize` and `DamageWorker_AllDroids`. `JawaArmoury.csproj` compiles it against ABF's DLL in the Workshop folder, and its comment says SynCore stays active, which is no longer true. No Def in `src` names either class: the ion DamageDefs use `guy762_Ionization.*`, and the namespace `guy762_IonizationABF` appears in one XML comment only. Filed: `ARMOURY_IONIZE_RETIRE_ABF_REFERENCE_DEAD`.

## Workshop: who else names a donor

17 Workshop folders. `modDependencies` on a donor, all inactive: KotOR Droids (on ABF and SynCore), Droid Depot (on Asimov), SynCore (on ABF), KotOR Factions (on KotOR Droids), Rim-Effect Renegade: Core (on Asimov).

Three active Workshop mods name a donor, none by hard dependency: `frozensnowfox.complexjobs` (242 gated, 3 load order), `neronix17.outerrim.core` (32 gated, 12 comments), `neronix17.outerrim.galacticempire` (4 gated, 1 comment, 3 `LoadFolders.xml`).

Limits: `findstr` skipped 40 UTF-16 files, all `Languages` translations, and could not open 36 non-ASCII filenames (`2710382569` 33, `3533512691` 1, `3545374124` 2). Those 36 were read directly: 0 donor hits, and 34 of them are visibly patch XML, so the read worked.

## How each gate works

1. `MayRequire` on a `<li>` or on a def-list element: skipped when the mod is absent.
2. `PatchOperationFindMod` with `<mods>`: the `<mods>` list is matched against mod **names**, and `<match>` / `<nomatch>` are the branches. `DroidDonor_ABFGate.xml` is 9 such operations on `nomatch`, removing `ArtificialBeings.*` modExtensions when ABF is gone.
3. `PatchOperationConditional`: an xpath test on the target. `DroidFemaleTexture_Fix.xml` is gated this way.
4. `loadAfter` / `forceLoadAfter`: load order only, and inert for an absent mod.

`MayRequire` on a top-level `<Operation>` is ignored by the engine, so it is not a gate. No donor reference relies on it (0 in `src`).

## Conclusion

No active mod and no `src` Def depends on a donor at load. Two leftovers, both filed: MSEDroidFix's `modDependencies`, and the `DamageWorker_Ionize` dead code. A save can still hold donor state no mod grep sees: check the save directly before calling a retirement safe (`rimworld-savegame`).
