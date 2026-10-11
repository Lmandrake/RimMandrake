# Removal consequence analysis: the five C15 "old why" mods

Owner order, typed 2026-10-10: *"I would like to remove them all. But please evaluate the consequences deeply
so we don't get bitten."* This is the evaluation. Nothing has been removed from any list; no game code was
edited. Offline only (no bridge, no game). Card: `mod_audit/OWNER_CARDS.md` C15; records `records/batch_07.md`,
`batch_09.md`, `batch_11.md`.

| mod | packageId | workshop folder (294100) | list position (FULL.LATEST, 551) |
|---|---|---|---|
| Vanilla Weapons Expanded | `vanillaexpanded.vwe` | `1814383360` | 357 |
| Vanilla Quests Expanded - Ancients | `vanillaquestsexpanded.ancients` | `3618306875` | 347 |
| Alpha Mechs | `sarg.alphamechs` | `2973169158` | 52 |
| Destiny Exotic Weapons | `milkwater.destinymod` | `3496200631` | 109 |
| WarCasket Expanded (the card's "three extra suits"; it ships four) | `aoba.warcasket` | `2733135485` | 471 |

Each resolves to exactly one root, under `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\`; none
has a copy under `...\common\RimWorld\Mods` (`facts/mod_facts.jsonl` `all_roots`, re-read by the scan below).

## 0. Method and instruments

Every number below comes from a parser, never a text count. Scripts are throwaway, kept outside git under
`/home/mandrake/.seat-tmp/oldwhy/`; their outputs are untracked `Transient/.oldwhy_*` files (a program reads them).

| instrument | what it does | sanity probe |
|---|---|---|
| `oldwhy_scan.py` | inventories each removed mod's Defs/Patches/Textures/DLLs with the FULL list's LoadFolders, then builds the **effective patched def tree of the 546-mod list without them** (the engine of `effective_def_lint.py`: combine Defs, apply every patch op in load order, drop MayRequire-unsatisfied defs and list children) and lists every surviving reference to a removed defName (text node or shorthand tag), implied def (`Corpse_`/`Meat_`/`Blueprint_`/`Frame_`/`Minified`/`Techprint_`) or removed C# namespace, plus every patch op that names one | `Steel`, `Gun_Revolver`, `Muffalo` all found in the reduced tree |
| `effective_def_lint.py` (repo) | the preflight load-killer lint, run on FULL.LATEST (baseline), on the 546 list, and on five 550 lists (each mod alone) | its own probes (`Steel`, `Beer`...) |
| `oldwhy_tree.py` | builds FULL and REMOVE5 effective trees and extracts weapon/apparel tag supply, pawnkind kits, faction group kinds, biome rosters, research prerequisites, recipe products | see section 4 |
| `oldwhy_save.py` | streaming `iterparse` of the canonical save, every element text/tag equal to a removed defName, every `Class=` from a removed namespace, the meta modIds | `Steel` 917, `Human` 864, `WoodLog` 15 hits |
| our-source census | tokenises every `src/**/*.xml` (comments stripped, About excluded) against the removed defNames | `Steel` 733 tokens |
| RimSage | decompiled 1.6 for what a dangling reference does at load and at save load | n/a |

Engine facts used (RimSage, decompiled 1.6, read 2026-10-10):

- **A list cross-reference that does not resolve is logged as an error and the entry is simply not added**
  (`DirectXmlCrossRefLoader.WantedRefForList<T>.TryResolve`). No null enters the list. A single-field ref stays
  null (error). `costList`/`ThingDefCountClass` is the null-dereference crash class (already linted).
- **`PatchOperationConditional` with a `<nomatch>` whose own xpath targets the missing def FAILS** (it returns
  `nomatch.Apply`); with only `<match>` it returns true silently.
- **Save load:** `DrugPolicy` drops entries whose drug is null (one error), `AutoSlaughterManager` drops null-animal
  configs (warning), `Ideo` drops precepts whose **PreceptDef** is null, but **an `IdeoRelic` precept whose relic
  ThingDef is null is NOT dropped** (`Ideo.ExposeData` only checks `x.def`). A Scribe def reference to a missing def
  logs `Could not load reference to ...` (`ScribeExtractor`).

The deployed copies of our mods are what the lint reads (it indexes the game's Mods folder and the workshop), so
everything here is about what the game would load, not the repo.

## 1. Per-mod contribution and our references

### 1a. What each mod contributes (parsed, concrete defs only; abstract/nameless excluded)

| mod | defs | biggest types | patch files / top-level ops | textures | DLL (own types) |
|---|---|---|---|---|---|
| VWE | 233 (1 abstract) | ThingDef 125, WeaponTraitDef 52, SoundDef 19, WeaponCategoryDef 12, HediffDef 8, ResearchProjectDef 3 | 5 / 13 (Core 20 + Odyssey 23 xpath refs) | 345 | none (XML only) |
| VQE Ancients | 473 (7) | ThingDef 119, KCSG.SymbolDef 107, KCSG.StructureLayoutDef 65, GeneDef 33, BackstoryDef 27, HediffDef 16, StructureSetDef 14, QuestScriptDef 6, SitePartDef 6, PawnKindDef 6, also a FactionDef, a BiomeDef, 2 ScenarioDefs, 3 TerrainDefs | 10 / 12 | 390 | `VanillaQuestsExpandedAncients.dll` (Harmony, 8 static ctors, 41 own types named in its XML: quest roots, vault GenSteps, wonderdoc, archogen injector, containment caskets, pneumatic tube port) |
| Alpha Mechs | 242 (15) | ThingDef 92, PawnKindDef 27, RecipeDef 26, SoundDef 17, BodyPartDef 13, HediffDef 11, BodyDef 10, ResearchProjectDef 8, BossDef 3, BossgroupDef 3 | 13 / 21 (Biotech 11, Core 2, Odyssey 2, Royalty 2) | 662 | `AlphaMechs.dll` (Harmony, settings, comp ticks; 20 own types) |
| Destiny | 59 (3) | ThingDef 25 (9 exotics + projectiles/engram), SoundDef 15, FleckDef 9, HediffDef 8, StatDef 1, WorkGiverDef 1 | 0 / 0 | 31 | `DestinyMod.dll` (MapComponent; 33 own types) |
| WarCasket Expanded | 14 | VFEPirates.WarcasketDef 12 = **four** frames, not three (Sentinel, Guardian X, Tyrant, Centurion; helmet + shoulders + body each), ThingDef 2 (EMP and smoke launcher projectiles) | 0 / 0 | 68 | none (types are VFE Pirates') |

Implied defs that also vanish: 232 (`Corpse_`, `Meat_`, `Blueprint_`, `Frame_`, `Minified`, `Techprint_`).
Three removed names are **shadowed** by a surviving def of the same name and type, so nothing dangles for them:
`VWE_TrenchWarfare` (ResearchProjectDef), `VanillaExpanded` (ResearchTabDef, the shared VE tab), `AM_AcidSpit`
(DamageDef).

### 1b. Our references (src census, comments stripped)

| removed mod | our files | refs / distinct names | files and guards |
|---|---|---|---|
| VQE Ancients | 5 | 64 / 11 | `src\RimUtinni\UtinniPatches\Patches\AnimalTolerances_Ashkarr.xml` 27 (Conditional) · `src\RimUtinni\Doctrine\Patches\MegafaunaYield.xml` 18 (FindMod) · `src\RimUtinni\UtinniPatches\Patches\VQEPatients_AreRakata.xml` 10 (FindMod) · `src\RimUtinni\UtinniPatches\Patches\VQEQuestText_AreForsaken.xml` 7 (FindMod) · `src\RimUtinni\PawnFlavor\Defs\Backstories_Rakata_Sleepers.xml` 2 (**unguarded**, but a string field) |
| Alpha Mechs | 4 | 79 / 13 | `src\RimUtinni\ResearchRetag\Patches\RUT_ResearchRetag.xml` 42 (Conditional) · `src\RimStarWars\StarWarsPatches\Patches\WeaponTags_Renormalise.xml` 18 (Conditional **with nomatch**, unguarded: see 2) · `src\RimUtinni\ResearchRetag\Patches\RUT_ResearchTabAssign.xml` 16 (Conditional) · `src\RimStarWars\Armoury\Patches\Armoury_RangedDamage.xml` 3 (FindMod, generated) |
| VWE | 6 | 26 / 5 | `RUT_ResearchRetag.xml` 11 · `RUT_ResearchTabAssign.xml` 8 (Conditional) · `WeaponTags_Renormalise.xml` 3 (FindMod) · `src\RimStarWars\Armoury\Patches\Armour_Penetration.xml` 1 (FindMod) · 2 hits on the shared `VanillaExpanded` tab (shadowed, harmless) |
| WarCasket Expanded | 1 | 8 / 6 | `src\RimStarWars\Armoury\Patches\Armour_Ratings.xml` 8 (FindMod "WarCasket Expanded", generated) · `src\RimStarWars\Armoury\Patches\Warcasket_BuildPathCut.xml` names it in a comment table only |
| Destiny | 0 | 0 | none beyond an optional `loadAfter` |

`loadAfter` lines (harmless when absent): `src\RimStarWars\Armoury\About\About.xml` (aoba.warcasket, destinymod,
alphamechs, vwe), `src\RimStarWars\StarWarsPatches\About\About.xml` (VWE), `src\RimUtinni\Doctrine\About\About.xml`
and `src\RimUtinni\UtinniPatches\About\About.xml` (Ancients), `src\RimUtinni\ResearchRetag\About\About.xml`
(alphamechs, vwe). The ideoligion files `src\Jawa\ideoligion\The Salvation.rid` and `MandrakeJawa.xtp` list all
five in their mod-id/mod-name metadata but reference **no** def of theirs.

The card's "about 60 of our patches use its creatures" (Ancients) is **64 references in 5 files naming 11 defs**,
and all but two sit behind FindMod or Conditional. Nothing of ours inherits from any of the five (no ParentName
into them); no Armoury kit, faction, pawnkind, biome roster, scenario or quest of ours names a removed def.

Third-party dependants (facts `dependants_detail`, then checked in the reduced tree): Alpha Memes (233 VWE refs),
VE Memes (45), Show Me Your Hands (38), Biomes! Fossils, VFE Tribals, Fortress Industrial, Complex Jobs, Better
Prerequisites, Turret Pipeline, VFE Core, Alpha Genes, VSR Examined, Regrowth: every one of their references is
FindMod-, MayRequire- or Conditional-guarded **except** the four listed in section 2.

## 2. Load-time unresolved refs (simulated removal on the 551 list)

`effective_def_lint.py` was run on `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (551, baseline) and on
six reduced lists (all five removed = 546; each mod alone = 550; untracked `Transient/.oldwhy_*.xml`). Baseline is
FAIL on 3 pre-existing `failed_ops`; every other check PASSes. The diff against baseline:

| list | costlist | recipe/stuff refs | pawnkind_race | drug_comp | failed_ops | other checks |
|---|---|---|---|---|---|---|
| minus VWE | 0 new | 0 | 0 | 0 | 0 new | 0 |
| minus Ancients | 0 | 0 | 0 | 0 | **-1** (a baseline failure in `VQEPatients_AreRakata.xml` disappears, because its FindMod no longer fires) | 0 |
| minus Alpha Mechs | 0 | 0 | 0 | 0 | **+6** | 0 |
| minus Destiny | 0 | 0 | 0 | 0 | 0 | 0 |
| minus WarCasket Expanded | 0 | 0 | 0 | 0 | 0 | 0 |
| all five (546) | 0 | 0 | 0 | 0 | +6 / -1 | 0 |

**No crash-class finding** (no costList/recipe/stuff/pawnkind-race/drug null). The per-mod deltas are disjoint and
sum to the combined delta, so the five removals do not interact with each other.

The +6 are real red errors: `src\RimStarWars\StarWarsPatches\Patches\WeaponTags_Renormalise.xml` has six
`PatchOperationConditional` ops on `AM_BeamGraserCannon`, `AM_Gun_GoliathChargeBlaster`,
`AM_Gun_SuperHeavyChargeBlaster`, `AM_Gun_TacticalShotgun`, `AM_MechanoidGunRotaryNeedle`, `AM_StarfireTurret`, each
with a `<nomatch>` PatchOperationAdd whose xpath is the absent def, so the op returns false and logs
`Patch operation ... failed`. They are not inside a FindMod (the VWE rows of the same file are).

The reduced-tree reference scan (`oldwhy_scan.py`, 1,061 removed or implied names that no surviving def shadows)
finds **27 surviving references**, none of them ours except two string fields:

| who | what | effect at load |
|---|---|---|
| `kilokio.rimai.core` `ResearchProjectDef RimAI_Subspace_Gravitic_Penetration` | `prerequisites/li` = `AM_Cryptoharmonization` | one `Could not resolve cross-reference` error; the entry is dropped, so that project loses a prerequisite (gets easier) |
| `iforgotmysocks.caravanadventures` `CompatibilityDef CACompatDef` | 21 `mechanoidBountyToAdd/li/raceDefName` = AM mechs | raw strings; 31 of its 66 names are ALREADY absent today and the mod logged 0 errors in the 550-mod session, so it tolerates missing names (MEASURED by the baseline, mechanism INFERRED) |
| `andromeda.niceresearchtab` `FineTune` | 3 VWE names (`VWE_HeavyWeapons`, `VWE_LaserTargetingSystems`, `VWE_MeleeWeapon_Shovel`) | strings in a third-party rule set; 0 errors from it today; INFERRED harmless |
| `mandrake.rut.pawnflavor` `RUT_Jawa_RakataTakenChild`, `RUT_Jawa_RakataFleshShaped` (`src\RimUtinni\PawnFlavor\Defs\Backstories_Rakata_Sleepers.xml`) | `spawnCategories/li` = `VQE_Experiment` | a string category, no error; but both backstories exist only for VQE's patient/experiment kinds, so they become **unreachable content** |

80 patch ops anywhere in the list name a removed def or mod; 74 are FindMod/Conditional-guarded and return true
silently (Alpha Memes 25, Complex Jobs 11, ResearchRetag 13, our Armoury 2, Doctrine 1, UtinniPatches 5, VFE
Tribals 2, VFE Core 3 with `success Always`, and others). Only the six above fail.

What the lint cannot see (stated, not passed): 236 custom-class patch ops (`OptionalPatch`, `PatchOperationModOption`
and similar) are not simulated; donor C# (Harmony patches, def generators) is not read. Two removed DLLs carry
Harmony (`AlphaMechs.dll`, `VanillaQuestsExpandedAncients.dll`); removing a Harmony mod removes its behaviour
changes too, which no offline lint models. None of OUR C# references a type in any of the three removed assemblies
(source grep of `*.cs`/`*.csproj`).

## 3. The canonical save


`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws`
(canon.yml `planet.start_savegame`; 17,483,421 bytes, written 2026-10-09 06:11). All five packageIds are in its
meta `modIds`. Streaming parse, every hit classified by context:

| removed mod | names / occurrences | where | what loading without the mod does |
|---|---|---|---|
| VWE | 128 / 205 | storage/caravan/trade **filters** (packUp, goods, journey) 155; price-history 27; **5 `IdeoRelic` precepts** (relic = `VWE_Gun_ChargeLMG_Unique` x3, `VWE_Gun_MarksmanRifle` x2) in five ideoligions (relic/ideo name pairs as read: Hexlink/Astropolitan, Loccorpus/the Contract, Strong Rifle/the Ascendant Genome, Rifle of Self/the Balance, Animal Blaster/the Green Oath); 2 research-progress keys | filters/price/research: `Could not load reference` errors, entries dropped. **Relic precepts survive with a null relic ThingDef** (see engine facts) |
| Alpha Mechs | 100 / 189 | filters 135; price history 28; 4 research-progress keys (`AM_MechanoidBeamcasting`, `AM_VoidLinkConnectivity`, `AM_QuantumPulseMessaging`, `AM_Cryptoharmonization`); 2 Big and Small `BS_scribedCache` originals (`AM_Daggersnout`, `AM_Siegebreaker`) | errors, entries dropped; the Big and Small cache rows are third-party code with a null def (UNMEASURED behaviour) |
| VQE Ancients | 97 / 259 | price history 155 (KCSG symbols are ThingDef names); 63 work-priority rows (`li/Priorities/li/Workgiver`); filters 25; 4 auto-slaughter configs (`VQEA_Spliceling`, `Splicehulk`, `Splicefiend`, `Splicetoot`); **1 VEF quest-chain `futureQuests` entry with `questDef` `VQE_AncientLabComplex`**; 1 `ignoredFactions` row (`VQE_NewVaultPlayerFaction`) | auto-slaughter: warning, dropped. **The future-quest entry is VEF (kept) code holding a null QuestScriptDef** (UNMEASURED: may NRE when VEF tries to fire it) |
| Destiny | 26 / 71 | filters 38; price history 13; 9 work priorities; **`m_Arc_Injector` in all four drug policies**; the map component `DestinyMod.MapComponent_ExoticsManager` (1) | drug policies: one error, entries removed (engine-verified). The map component's class is gone: logged, component skipped |
| WarCasket Expanded | 14 / 23 | filters 22; **one worn `Warcasket_Tyrant`** on a DEAD world pawn (`Human668808`, Maria Rodriguez, kind `RUT_Jawa_Junkers_Grunt`, `Faction_1`) with a VFE Pirates shoulder piece | the Tyrant body fails to load and is dropped from a corpse-less dead pawn: harmless. **But it proves our Junkers raid kit already draws these suits** (section 4) |

No placed Thing (`things/thing/def`) of any of the five exists on any map in the save, no VQEA site or world
object, and no living pawn carries one of their weapons. Terrain grids are shortHash-encoded and were NOT decoded
(needs a def dump of the same mod set); VQEA's three TerrainDefs are only generated inside its vault sites, and the
save holds no such site, so the risk is low but formally UNMEASURED.


**First load of the save without the five: expect about 740 `Could not load reference to ... named ...` errors**
(one per surviving occurrence above; `ScribeExtractor.DefFromNode` logs each unless BackCompatibility knows the def
was removed, and it does not), plus `Some DrugPolicyEntries were null after loading.`, the auto-slaughter warning,
`Could not find class DestinyMod.MapComponent_ExoticsManager`, and RimWorld's **mod-mismatch dialog**
(`Dialog_ModMismatch`, the save's meta lists all five). The flood is far below the 10,000-message stop
(`Log.StopLoggingAtMessageCount`), and one re-save clears it. It is noise, but noise that a launch gate or a log
harvester will read as a regression unless told in advance.

## 4. Raid/faction power, balance, replacement content

Measured from the FULL and REMOVE5 effective trees (`oldwhy_tree.py`; probe: 738 vs 646 weapons, 1,971 vs 1,937
pawnkinds), with the **live Cherry Picker cuts applied** (`Config\Mod_3521312241_Mod_CherryPicker.xml`, 2,088
entries), because that is what pawn generation actually draws from.

**No pawnkind loses its last weapon or apparel source.** No weapon or apparel tag used by any surviving pawnkind
goes from non-zero to zero.

| mod | what enemies lose | our kits affected (supply before -> after, CP applied) |
|---|---|---|
| VWE | 61 weapon defs, of which Cherry Picker already cuts 40; **21 live** (13 spacer, 4 industrial, 3 medieval, 1 neolithic). Biggest cuts: `SniperRifle` 12 -> 4 raw, `SpacerGun` 61 -> 39 raw (with Destiny), `Gun` 36 -> 21 raw | `RUT_Jawa_Homestead_Specialist` 9 -> 7 (charge sniper pair); `RUT_Jawa_Tribal_Elder` 16 -> 13 (battle axe, combat knife, halberd); `RUT_Jawa_Tribal_Slinger` 6 -> 5 (throwing knives) |
| Destiny | 9 exotics (7 live after CP): Riskrunner, Polaris Lance, Gjallarhorn, Wardcliff Coil, Eriana's Vow, Xenophage, Graviton Lance. They carry the generic `Gun`/`SpacerGun` tags, so **any of 44 `Gun` pawnkinds (Core 9, Biotech 6, Ancient Urban Ruins 5, Ideology 4, Caravan Adventures 4, ...) can roll one today** | none of ours |
| Alpha Mechs | **7 of 23 kinds in the Mechanoid faction's group makers** (`AM_Aura`, `Daggersnout`, `Demolisher`, `Fireworm`, `Goliath`, `Phalanx`, `Siegebreaker`; 23 -> 16, the rest Core 7, Biotech 8, Odyssey 1); 3 boss groups (Infernus, War Empress, Apoptosis); 21 mech weapons; 17 apparel incl. 3 VFEP MechController warcasket parts | every Jawa kit that draws `SimpleGun`/`AssaultRifle` loses `AM_Gun_GoliathChargeBlaster` and `AM_Gun_SuperHeavyChargeBlaster` (59-72 -> 57-70), **because our own `WeaponTags_Renormalise.xml` gave those Goliath-scale mech guns grunt tags**; Junkers casket kits lose the 3 MechController parts |
| WarCasket Expanded | 12 suit parts (Sentinel, Guardian X, Tyrant, Centurion) | `RUT_Jawa_Junkers_Grunt/Heavy/Specialist/Leader` draw `WarcasketAll`: 51 -> 36 (with the 3 AM parts). The save proves the draw happens: a dead Junkers grunt wore a `Warcasket_Tyrant` |
| VQE Ancients | 6 pawnkinds (patients, experiments, 4 splice creatures), none in any faction's group makers, none in any biome roster (both trees: 0 roster rows change) | none; the Rakata-patient reskin and quest-text patches go quiet |

Power: removal **lowers** the enemy ceiling (Destiny exotics and charge-spacer guns out of generic raids, Goliath
guns out of Jawa grunts' hands) and **narrows mechanoid raids** by about 30% of their kinds. The second is the real
flavour hole; the owner's 2026-08-15 *"We are keeping the mechanoids"* (`design\Jawa\droid_ruling.md`,
`design\Jawa\worldbuilding\cherrypick_inbox.md`) is about the mechanoid faction existing, which survives on Core +
Biotech + Odyssey kinds; the mod audit had read it as protecting Alpha Mechs specifically. Removal does not violate
it, but the registry's KEEP reason for Alpha Mechs must be rewritten.

Replacement content, what must exist first:

| mod | must exist before removal | effort | licence/source |
|---|---|---|---|
| VWE | nothing; Star Wars sets keep every kit supplied | S | not needed |
| Destiny | nothing | S | not needed |
| WarCasket Expanded | nothing (VFE Pirates' own frames remain; `mandrake.rm.warcasket` is the long-term class) | S | not needed |
| VQE Ancients | nothing for load safety. Flavour: the Rakata-vault quest line (`VQEQuestText_AreForsaken.xml`, `VQEPatients_AreRakata.xml`, `design\Jawa\worldbuilding\ANCIENTS_AS_RAKATA_SPEC.md`) disappears with it; replacing it is our own quest work, not a port | L if wanted | steam-only, no licence found (facts `source_kind steam-only`): port nothing, write our own |
| Alpha Mechs | nothing for load safety. Flavour: mech-raid variety; replace with our own droid/mech threats per `droid_ruling.md` if the owner wants 23 kinds back | M-L | a GitHub name-match `Smxrez/Alpha-Mechs-ReExamined` exists, identity UNVERIFIED; do not port art |

## 5. Safe removal order

Every step is verified offline before the one cold load (~21 min on the full list) that it feeds. The removals are
independent (section 2), so they can share ONE cold load; the order below is the order of offline work, and also
the bisection order if that one load surprises.

| step | do | offline test that must pass first |
|---|---|---|
| 0 | Back up `ModsConfig.xml`, `infrastructure\state\modlists\ModsConfig.FULL.LATEST.xml`, `manifest.FULL.json`, the Cherry Picker config and the canonical save; stat the Saves folder | backups exist, sizes recorded |
| 1 | Wrap the six Alpha Mechs rows of `WeaponTags_Renormalise.xml` in `PatchOperationFindMod` "Alpha Mechs" (the VWE rows already are). Deploy StarWarsPatches | `effective_def_lint.py` on the minus-Alpha-Mechs list: `failed_ops` back to the 3 baseline rows; on FULL: unchanged |
| 2 | Add a FindMod-nomatch patch (ResearchRetag is the natural home) removing `AM_Cryptoharmonization` from `RimAI_Subspace_Gravitic_Penetration` when Alpha Mechs is absent | rerun `oldwhy_scan.py`: 0 references outside string-only third-party defs |
| 3 | Decide the two save repairs (owner, card): the 5 `IdeoRelic` precepts with VWE relics, and the VEF `futureQuests` row `VQE_AncientLabComplex`. Either edit a COPY of the save (relic `thingDef` -> a surviving gun, futureQuests row removed) or accept them | `oldwhy_save.py` on the copy: 0 relic / futureQuests hits; size delta matches; never edit in place |
| 4 | Retarget or retire the two Rakata backstories; leave the FindMod/Conditional patches in place (they are inert without their target and cost nothing) | lint unchanged |
| 5 | Write the 546 list (remove the five ids; nothing else) as the live ModsConfig, with the expected-log list from section 3 in hand | `effective_def_lint.py` on it: only the 3 baseline failed_ops; `modset_builder`/manifest identical apart from the five |
| 6 | ONE cold load; load the canonical (or repaired) save; read the FIRST exception, not the loudest | expected: no exception; the ~740 `Could not load reference` errors, the drug-policy and auto-slaughter lines, the mod-mismatch dialog. Anything else is new |
| 7 | Re-save, then prune Cherry Picker of its 66 dead entries (VWE 41, AM 13, Ancients 10, Destiny 2); update registry rows, FULL.LATEST, `manifest.FULL.json`; optionally re-run the Armoury generators (their FindMod blocks for absent mods drop out) | second load of the re-saved game: 0 `Could not load reference` lines for these mods |

Fallback bisection if step 6 shows an unexplained error: restore and remove Destiny + WarCasket Expanded first
(zero lint delta), then VWE, then Ancients, then Alpha Mechs (the Harmony-heavy, most-referenced one).

## 6. What would bite (ranked)

1. **Five ideoligions keep a relic precept whose relic is a VWE gun.** The engine drops a precept only when its
   PreceptDef is null; an `IdeoRelic` with a null relic ThingDef survives load (`Ideo.ExposeData`, RimSage). Every
   UI and quest path that draws or spawns that relic then holds a null. INFERRED NRE, MEASURED presence (5).
   Fix before or at removal (step 3).
2. **A Vanilla Expanded Framework quest-chain entry holds `questDef VQE_AncientLabComplex`.** VEF stays loaded and
   will read a null QuestScriptDef when the chain tries to fire it. Behaviour UNMEASURED (third-party code); scrub
   the row in a copy of the save or verify VEF null-guards it.
3. **Six red patch failures** from our own `WeaponTags_Renormalise.xml` the moment Alpha Mechs goes (step 1). Small,
   but they would land in a log being judged "clean" and cost a diagnosis round.
4. **~740 load errors and a mod-mismatch dialog on the first save load.** Expected and harmless, but a bridge
   `load_game_ready` behind a modal, or a launch gate that counts errors, will read it as a failure.
5. **Mechanoid raids lose 7 of 23 kinds and three bosses.** Not a crash; a flavour hole the owner should see named
   before he loses it. The audit's KEEP verdict for Alpha Mechs rested on reading the 2026-08-15 ruling as
   protecting this mod.
6. **Third-party code holding removed names in caches:** Big and Small's `BS_scribedCache` (2 AM originals in the
   save), Caravan Adventures' bounty list (tolerated today), RimAI's research prerequisite (one error). UNMEASURED
   beyond the log baseline.
7. **The Rakata patient backstories go dark** (two backstories, `Backstories_Rakata_Sleepers.xml`), and the
   Rakata-vault quest flavour disappears with VQE Ancients. Content loss, not a fault.
8. **Generators and records drift.** `gen_armoury_patch.py`/`gen_armour_patch.py` read the live list, so a re-run
   silently drops the Alpha Mechs/WarCasket blocks (correct, but a diff to explain); `cherrypick_build.py` names
   `VWE_Throwing_Rocks`; the audit registry, FULL.LATEST, `manifest.FULL.json` and the ideoligion files'
   mod lists all still name the five.

## 7. Tickets (names pass `rimflow namecheck`; NOT filed)

| name | what |
|---|---|
| `OLDWHY_MODS_RETIRE_IN_FIVE_STEPS` | the umbrella: steps 0-7 above, one cold load |
| `WEAPONTAGS_RENORMALISE_HARDEN_AM_ROWS` | wrap the six AM rows in FindMod (step 1) |
| `RIMAI_PREREQ_SILENCE_MISSING_AM` | drop `AM_Cryptoharmonization` from RimAI's prerequisite when AM is absent (step 2) |
| `SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS` | the five VWE relic precepts (step 3; owner decides relic replacement or removal) |
| `VEF_FUTUREQUEST_PROBE_NULL_QUESTDEF` | prove or scrub the `VQE_AncientLabComplex` future-quest row (step 3) |
| `RAKATA_BACKSTORIES_REWIRE_WITHOUT_VQEA` | the two orphaned Rakata backstories (step 4) |
| `CHERRYPICKER_ENTRIES_PRUNE_DEAD_DEFS` | 66 dead Cherry Picker entries (step 7) |
| `MODLIST_RECORDS_SYNC_AFTER_OLDWHY` | FULL.LATEST, manifest, registry rows, About loadAfter tidy (step 7) |
| `MECHANOID_ROSTER_FILL_AFTER_ALPHAMECHS` | owner's call: replace the 7 lost mech kinds with our own, or accept 16 |
| `MECH_GUNS_AUDIT_IN_JAWA_KITS` | independent of removal: our renormalise patch hands Goliath-class mech guns to Jawa grunts today |
| `BIGSMALL_CACHE_PROBE_DEAD_AM_ORIGINALS` | check Big and Small tolerates its two cached AM originals |

## 8. Review disposition
(pending)
