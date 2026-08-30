# Star Wars mod ownership survey — measured facts only

Generated 2026-08-30. Read-only census across the live mod stack for the owner's
per-mod ABSORB-vs-keep-upstream decision. **No trades or recommendations are
written here** — that layer belongs to the parent session. Every number below
carries its source; anything not measured is marked UNCERTAIN rather than guessed.

## Method

- Active mods: `activeMods` in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` (590 `<li>` entries), joined case-insensitively against every workshop folder's `About/About.xml` `<packageId>` under `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\` (1255 folders scanned, 620 packageId matches — some active packageIds resolve to more than one workshop folder because Steam still holds stale copies; the folder used per mod below is the one actually referenced by its own dependents/LoadFolders).
- SW-flavored candidates: keyword scan (name/description/packageId) for Star Wars/KotOR/Outer Rim/lightsaber/droid/Jawa/Mandalorian/Hutt/Jedi/Sith/blaster/etc., then hand-checked. **Six keyword hits were confirmed false positives from substring collisions** and are excluded (see below): `fuu.bloodanimations`, `mlie.realistichumansounds`, `vanillaexpanded.vfecore` all matched "droid" inside "**droid**s" spelled inside "VEAn**droid**s" or "An**droid** Tiers" (Android Tiers mod family, not Star Wars droids); `sk.gravshipraids`, `zal.spaceports`, `trouperton.trystantravellersshuttleschematics` all matched "hutt" inside the substring "s**hutt**le". None of the six ship any Star Wars content.
- 1.6 loaded folders: each mod's own `LoadFolders.xml` `<v1.6>` list (with `IfModActive`/`IfModNotActive` gates evaluated against the real active-mod set), or — where no `LoadFolders.xml` exists — RimWorld's default of root `/` plus a top-level `1.6/` folder if one exists. Stated per mod.
- Def counts: direct children of each Defs XML file's `<Defs>` root only (no nested elements), tallied with `xml.etree`.
- "Our-touch": grep of `src/Jawa`, `src/RimMandrake`, `design/Jawa` for the mod's defName prefix/packageId, plus a check of `infrastructure/state/canon.yml` and the turret-canon review artifacts under `design/Jawa/worldbuilding/review/`.
- CherryPicker keys: counted in the **live** config `Mod_3521312241_Mod_CherryPicker.xml` (1505-1513 total keys depending on the read), matched by the mod's real defName prefix where one exists.
- World-save presence: `MEASURE_ALLOW_SCAN=1 grep -c "<prefix>"` against `world/WORLDMAP_V1_original.rws` (21.8 MB plain XML). **Scan-grade only** — a substring hit count, not a verified cross-reference count.
- Reverse dependencies: substring match of each target packageId against every active mod's `About.xml` text — scan-grade, case-insensitive, not distinguishing hard `modDependencies` from `loadAfter`/prose mentions unless noted.

## Mods found

**20 core SW-flavored mods** (all confirmed genuinely Star-Wars-content, not just vocabulary):
`guy762.kotorweapons`, `guy762.kotordroids`, `guy762.mm.kotorcore`, `lee.theforce.lightsaber`, `neronix17.outerrim.core`, `neronix17.outerrim.droiddepot`, `neronix17.outerrim.furnitureanddecor`, `neronix17.outerrim.galacticempire`, `neronix17.outerrim.rebelalliance`, `m3.continued.jangodsoul.starwars.bti`, `m3.continued.jangodsoul.starwars.tsda`, `maincrep.eweb`, `sov.sith`, `btd.gbp.shippack.kotor.vge`, `lumi.doorsexpanded`, `lumi.swlights`, `mlie.starwarsanimalcollection`, `starwars.themedsounds`, `leutiankane.mineablesor`, `leutiankane.mines2patchouterrim`.

**3 borderline mods, measured but each independently determined NOT genuinely SW-themed** (flagged by the keyword scan on vocabulary alone — "blaster", "lightsaber" as an example — but their actual content is generic sci-fi/framework, not Star Wars branded): `jecrell.jecstools` (general C# framework), `vanillaexpanded.vfesecurity` (generic sci-fi turret pack), `rpgwanderer.opturret` (RimWorld's own archotech lore). Kept in this survey because the owner explicitly asked to check the Archotech Blaster Turret mod, and because two of the three already have content absorbed into Jawa canon.

**Notes on named members from the task brief:**
- `maincrep.eweb` is the only active E-Web mod; its `<author>` field reads "Maincrep," not "RN2" — but its internal defNames/filenames (`RN2SWGun_EWeb_MG`, `BaseDef_Bullets_RN2.xml`) are RN2-branded, consistent with the owner's "RN2's E-Web" memory even though credited authorship differs. Not silently corrected.
- `btd.gbp.shippack.kotor.vge` has an unresolved discrepancy between the two measurement passes over whether its `IfModActive="guy762.KotORDroids"` gated subfolder should count as loaded — see its card.

## Summary table

| mod | defs | C# depth | art (loose+bundled) | rev-deps | our-touch | blockers |
|---|---|---|---|---|---|---|
| guy762.kotorweapons | 679 | DLL-less in loaded set, no Source | 60.66 MB + ~17 MB bundle | 3 | 24 files touch "kotor" | world-save 7/673 defNames present; shared `guy762_` prefix not separable |
| guy762.kotordroids | 239 | none | 2.70 MB | 3 | overlaps kotor grep | world-save 0/237 present |
| guy762.mm.kotorcore | 1235 | 29 DLLs, no Source (size only) | 51.34 MB loose (no bundle) | 2 | **KotORBandolierNorthFix hard-depends on this mod's apparel defs** (retirement blocker) | world-save 4/1142 present |
| lee.theforce.lightsaber | 335 | Lightsaber.dll 273 KB, no Source | 2.98 MB + 0.37 MB bundle | 2 | 16 files | world-save 3/311 defNames, 68 total occurrences (highest live signal in the KotOR cluster) |
| neronix17.outerrim.core | 446 | Source, 22 classes; DLL 28 KB | 1.1 MB + 36.5 MB bundle | 6 | 129 files; hard framework dep of every addon | world-save `OuterRim_`=3156 (shared, not separable) |
| neronix17.outerrim.droiddepot | 306 | Source, ~31 classes; DLL 41 KB | 0 + 1.5 MB bundle | 1 | "ADOPTED FUNCTIONAL" | UNCERTAIN (shared prefix) |
| neronix17.outerrim.furnitureanddecor | 298 | none (empty Source/Assemblies) | 0.016 MB + 19.4 MB bundle | 0 | "cosmetic, pillar-neutral," no patches | UNCERTAIN (shared prefix) |
| neronix17.outerrim.galacticempire | 107 | Source, 4 classes incl. a Harmony patch INTO Core's settings (real class coupling) | 0 + 3.5 MB bundle | 0 | ADOPTED; faction struck from records but `OuterRim_Imp*` pawnkind MayRequire dependency stands | FactionDef present=1 (unused, consistent); `OuterRim_Imp`=129 |
| neronix17.outerrim.rebelalliance | 47 | none | 0 + 1.4 MB bundle | 0 | ADOPTED, then suppressed via patch (kept, not deleted — Scenario_Rebel.xml references it) | FactionDef present=1 (suppressed, consistent) |
| m3...bti (JDS Armory) | 74 | none | 0.35 MB | 1 | `JDSA_` defs in array-review only, not ratified turret roster | world-save `JDSA_`=163 |
| m3...tsda (JDS Sep. Droid Army) | 59 | none | 1.16 MB | 0 | none found | world-save `JDSCIS_`=17 |
| maincrep.eweb | 8 | none | 0.08 MB | 0 | **already ruled on** — in ratified 56-def turret roster, damage/label patched | world-save `RN2SWGun_EWeb`=6 |
| sov.sith | 8 | none | 0.21 MB | 0 | none found | world-save `PureBlood`=0 |
| btd.gbp.shippack.kotor.vge | 0 (UNCERTAIN — see card) | none | 4.77 MB | 0 (uncertain) | none found | world-save packageId string=1 (uncertain) |
| lumi.doorsexpanded | 41 | none | ~0.7 MB tex + ~0.3 MB audio | 0 | **BlastDoorFrameAsyncFix hard-depends on this mod** (retirement blocker) | `SW_DoorJail`=6; other prefixes disputed between runs |
| lumi.swlights | 3 | none | 0.036 MB | 0 | none (mod-list snapshot only) | `SwLightA`+`SwLightB`=10 |
| mlie.starwarsanimalcollection | 1581 | none | 0.036 MB loose + ~33 MB bundle | 0 | **ADOPTED**, resolves Bantha/Sarlacc, 3 of our patch files fix its art, fauna census tooling depends on it | no consistent prefix; species-name hits high (Bantha=210, Rancor=114, Reek=92...) |
| starwars.themedsounds | 0 native (SoundDef-retarget patch only) | none | 0.02 MB tex + 0.40 MB audio | 0 | none found | not applicable — no defNames of its own |
| leutiankane.mineablesor | 4 (+13 patch ops) | none | 0 | 0 | owner ruling KEPT 2026-08-12 ("something on the map to find and leave behind") | **unguarded hard cross-ref** to `OuterRim_*` ThingDefs — breaks if Core retired |
| leutiankane.mines2patchouterrim | 0 native (9 patch ops) | none | 0 | 0 | owner override "Mines 2.0 IS LIVE" 2026-08-12 | **unguarded hard cross-ref** to `OuterRim_*` + Mines 2.0's C# class — breaks if Core retired |
| *(borderline)* jecrell.jecstools | 27 | Source, 549 files, ~163 classes; 18 DLLs | 8 KB | 3, all **soft** (`loadAfter` only, no SW mod hard-depends on it) | none load-bearing found | framework; runtime use by lightsaber/oversized-weapon graphics UNCERTAIN without a live test |
| *(borderline)* vanillaexpanded.vfesecurity | 86 | VFESecurity.dll 79.9 KB, no Source | 6.4 MB | 3 (unverified) | **7 defs already kept** in the ratified turret roster (tesla+railgun→Helix, flamer→Wildsteam); 17 other defs cut via CherryPicker | world-save `VFES_`=371 (real, live content) |
| *(borderline)* rpgwanderer.opturret | 3 | none | 84 KB | 0 | **directly named** in the owner's turret ruling ("archotech allowed to be x4 expected") | both its defNames present on the frozen world (5, 3) |

## Per-mod cards

### guy762.kotorweapons — Star Wars KotOR Weapons and Armor
- Loaded folders (v1.6): `/`, `1.6`, `1.6/AdditionalMods/_TheForceLightsabers` (lee.theforce.lightsaber is active).
- Defs: 679 total. Top 6: ThingDef=355, ModularWeapons2.ModularPartsDef=143, AbilityDef=68, Lightsaber.HiltPartDef=46, HediffDef=20, RecipeDef=18.
- C#: no Assemblies in the loaded set (a DLL exists only under an unloaded `1.5/AdditionalMods/_NO_ForceLightsabers` folder); no Source/.
- Art: 2670 loose files, 60.66 MB; AssetBundles present, 105 files, ~17 MB.
- Declared deps (v1.6): Ludeon.RimWorld.Royalty, OskarPotocki.VanillaFactionsExpanded.Core, EBSG.Framework, kaitorisenkou.ModularWeapons2, lee.theforce.lightsaber, guy762.MM.KotORCore.
- Rev-deps: 3 → guy762.KotORDroids, guy762.MM.KotORCore, lee.theforce.lightsaber. Ecosystem link (soft, not hard): jecrell.jecstools.
- Our-touch: 24 `src/`/`design/` files match "kotor"; 16 match "lightsaber|TheForce". CherryPicker keys: 0.
- Blockers: world-save exact-defName presence 7/673 distinct defNames found (scan-grade). `guy762_` prefix scan = 4433 but is shared across all three guy762 mods, not attributable to this one alone. No dedicated src/ fix mod targets this package directly.

### guy762.kotordroids — Star Wars KotOR Droids
- Loaded folders: `/`, `1.6`.
- Defs: 239 total. Top 6: ThingDef=48, PawnKindDef=46, SoundDef=40, AlienRace.ThingDef_AlienRace=22, RecipeDef=20, HediffDef=20.
- C#: none anywhere in the mod (pure XML/art).
- Art: 139 files, 2.70 MB; no AssetBundles.
- Declared deps: Ludeon.RimWorld.Biotech, Killathon.ArtificialBeings, Killathon.ArtificialBeings.SynCore, guy762.KotORWeapons.
- Rev-deps: 3 → guy762.KotORWeapons, guy762.MM.KotORCore, btd.gbp.shippack.kotor.vge.
- Our-touch: overlaps the 24-file "kotor" hit list (not separately distinguishable). CherryPicker keys: 0.
- Blockers: world-save exact-defName presence 0/237, 0 occurrences. No src/ fix mod targets this package.

### guy762.mm.kotorcore — Star Wars KotOR Resources and Materials
- Loaded folders: `/`, `1.6`, plus three conditional `1.6/AdditionalMods/*` subfolders whose gate mods are inactive (skipped), plus `1.6/AdditionalMods/_DroidsBase` (guy762.KotORDroids is active).
- Defs: 1235 total — the largest of the four KotOR-cluster mods. Top 6: ThingDef=495, SoundDef=285, ResearchProjectDef=87, HediffDef=63, RecipeDef=35, DamageDef=34.
- C#: 29 DLLs in the loaded set (e.g. SWCP_Core.dll 162.0 KB, SWCPEnlist.dll 88.0 KB, KoltoTank.dll 29.5 KB, CompDeflector.dll 27.5 KB, plus ~25 smaller utility DLLs 4.5-21 KB each). No Source/ directory anywhere — DLL size only, no class count possible.
- Art: 2196 loose files, 51.34 MB. Confirmed no AssetBundles — this mod ships everything loose.
- Declared deps: imranfish.xmlextensions only (a much longer `loadAfter` list is load-order, not hard dependency).
- Rev-deps: 2 → guy762.KotORWeapons, guy762.KotORDroids.
- Our-touch: same 24-file "kotor" hit list; 98 files under `design/Jawa` mention kotor/lightsaber/jedi/sith (mostly generic roster/lore, not KotORCore-specific — most relevant: `force_users_build_spec.md`, `mods/armoury_keeplist.md`, `worldbuilding/ship_legacy_armoury.md`). CherryPicker keys: 0.
- **Blockers — retirement blocker found:** `src/RimMandrake/KotORBandolierNorthFix` (packageId `mandrake.kotorbandoliernorthfix`) is a compat-art mod shipping 20 PNGs (north/northm facings) for two ThingDefs in this mod's own `Apparel_SWAccessories.xml` (`bandolier_chewbacca`, `bandolier_traveler`; `wornGraphicPath`/`dataNorth` layer 65). It declares a hard `modDependencies` + `loadAfter` on `guy762.MM.KotORCore` and relies on identical loose texture paths to override the donor's missing north art. If this mod is retired/re-authored, KotORBandolierNorthFix's paths point at nothing unless the new def keeps byte-identical `texPath`/`wornGraphicPath` and load order — it does not become dead code cleanly, it needs either (a) its 20 PNGs ported into the re-authored def's own texture folder, or (b) deletion once native north art ships. World-save exact-defName presence: 4/1142 distinct defNames found. Prefix scan-counts (shared/ambiguous, UNCERTAIN attribution): `guy762_`=4433, `KotORBlaster|KotORIon|KotORStun|kotorsound|SWCP_`=21.

### lee.theforce.lightsaber — Star Wars : The Force - Lightsaber
- Loaded folders: `/`, `1.6`, `1.6/Mods/Royalty`, `1.6/Mods/Odyssey`, `1.6/Mods/Ideology`, `1.6/Mods/KoTORWeapons` (guy762.kotorweapons active).
- Defs: 335 total. Top 6: Lightsaber.HiltDef=114, Lightsaber.HiltPartDef=65, ThingDef=32, SoundDef=31, RulePackDef=12, RecipeDef=10.
- C#: Lightsaber.dll, 273.0 KB (279,552 bytes), single DLL in the loaded set, no .pdb. No Source/.
- Art: 439 loose files, 2.98 MB; AssetBundles present, 1 file, 0.37 MB.
- Declared deps: brrainz.harmony.
- Rev-deps: 2 → guy762.KotORWeapons, guy762.MM.KotORCore. Ecosystem link (soft): jecrell.jecstools.
- Our-touch: 16 `src/` files hit "lightsaber|TheForce" (Jawa_Armoury patches/README, RimMandrake bridgetools stat/character/terrain tools, `Utils/modset_builder.py`, `Utils/patch_provenance.py`). No dedicated fix-mod for this package. CherryPicker keys: 0.
- Blockers: world-save exact-defName presence 3/311 distinct defNames, but 68 total `<def>` occurrences — the highest live-presence signal of the four KotOR-cluster mods. No dedicated src/ fix-mod dependency found.
- **Cross-mod fact for the KotOR/lightsaber cluster:** the live CherryPicker config (1513 total keys) references **zero** defNames from any of these 4 mods, checked by both exact match and substring (guy762, KotOR, Force_, Lightsaber, SWCP). None of the four ship a `Source/` directory — all four are compiled-DLL-only or pure XML.

### neronix17.outerrim.core — Outer Rim - Core
- Loaded folders: `/`, `Common`, `1.6` (no live `IfModActive` gates fire).
- Defs: 446 total, 25 distinct types. Top 6: ThingDef=212, SoundDef=58, TerrainDef=50, PawnKindDef=25, ResearchProjectDef=17, DesignatorDropdownGroupDef=13.
- C#: OuterRimCore.dll, 28,160 bytes; Source/ present, 22 classes (spec grep pattern).
- Art: 73 loose files, 1.1 MB; AssetBundles `Common/AssetBundles/neronix17_outerrim_core`, 38,227,021 bytes (~36.5 MB) — art ships packed, not loose.
- Declared deps: OskarPotocki.VanillaFactionsExpanded.Core, neronix17.toolbox.
- Rev-deps: 6 → GalacticEmpire, RebelAlliance, FurnitureAndDecor, DroidDepot, Mines2patchOuterRim, MineablesOR.
- Our-touch: 129 files under `src/Jawa`/`src/RimMandrake`/`design/Jawa` match `OuterRim_`; `design/Jawa/mods/required_mods.md` logs it "ADOPTED" — a hard framework dependency of every addon module. CherryPicker keys: 3 (prefix `OuterRim_`; all 3 are `OuterRim_Stormtrooper*_Pride` apparel — i.e. GalacticEmpire-module defs, not Core's own).
- Blockers: world-save `OuterRim_`=3156 (scan-grade; all 5 Neronix17 submods share this one prefix, not separable). Core→addon coupling: the other 4 addon mods' XML has zero `class="..."` references to any of Core's 22-24 public C# class names — the only genuine class-level coupling found runs the other direction, from GalacticEmpire's own Source into Core's mod settings (see below).

### neronix17.outerrim.droiddepot — Outer Rim - Droid Depot
- Loaded folders: `/`, `Common`, `1.6`.
- Defs: 306 total, 26 distinct types. Top 6: ThingDef=76, RecipeDef=50, HediffDef=35, PawnKindDef=20, Asimov.AutomatonRecipeDef=19, ResearchProjectDef=16.
- C#: OuterRimDroids.dll, 41,472 bytes; Source/ present at 1.6 (27 classes) plus legacy 1.5/1.4 Ideology sub-source (2 each) — ~31 classes total across all found Source dirs.
- Art: 0 loose files; AssetBundles `Common/AssetBundles/neronix17_outerrim_droiddepot`, 1,584,372 bytes (~1.5 MB).
- Declared deps: Neronix17.Asimov, Neronix17.OuterRim.Core.
- Rev-deps: 1 → FrozenSnowFox.ComplexJobs.
- Our-touch: `required_mods.md` — "ADOPTED FUNCTIONAL, self-limited by build choice"; player-buildable Building_AutoCrafter kept on, 20 recipes; every droid costs `OuterRim_DroidBrain`, treated as scarce/quest-gated by design. `design/Jawa/pawn_flavor_traits_catalog.tsv` carries 10 `OuterRim_` droid trait rows pulled from this module. CherryPicker keys: UNCERTAIN — cannot isolate from the shared `OuterRim_` prefix.
- Blockers: world-save UNCERTAIN, no distinguishing prefix found (sampled defNames like `AdultHumanoidDroidStage`, `OuterRim_AstromechDroid` are not separable from other submods by substring). No `class="..."` refs to Core's classes found in this mod's own Defs/.

### neronix17.outerrim.furnitureanddecor — Outer Rim - Furniture & Decor
- Loaded folders: `/`, `Common`, `1.6` (two `IfModNotActive="Neronix17.OuterRim.Core"` gates both skipped since Core is active).
- Defs: 298 total, 8 distinct types — near-monoculture of ThingDef. Top: ThingDef=280, TabulaRasa.HologramDef=10, JobDef=2, JoyGiverDef=2, TabulaRasa.UpdateDef=1, DesignationCategoryDef=1.
- C#: Assemblies/1.6 directory exists but is empty; Source dirs exist at 1.4/1.5/1.6 but are all empty (0 files, 0 classes) — no actual C# ships in this mod.
- Art: 3 loose files, 16 KB; AssetBundles `Common/AssetBundles/neronix17_outerrim_furnitureanddecor`, 20,374,177 bytes (~19.4 MB).
- Declared deps: neronix17.toolbox (loadAfter also lists Core, not in modDependencies proper).
- Rev-deps: 0.
- Our-touch: `required_mods.md` calls it "cosmetic, pillar-neutral" — one-line mention only, no patches found. CherryPicker keys: UNCERTAIN (shared prefix).
- Blockers: world-save UNCERTAIN, no distinguishing prefix. No coupling possible — no C# ships in this mod at all.

### neronix17.outerrim.galacticempire — Outer Rim - Galactic Empire
- Loaded folders: `/`, `Common`, `1.6` (an `IfModActive="Neronix17.OuterRim.DroidDepot"` gate on `1.6/Mods/OuterRimDroidDepot` did NOT fire in this measurement — DroidDepot was not counted active for this gate check, flagged UNCERTAIN, see the general btd.gbp discrepancy note above for the same category of gate-evaluation disagreement between passes).
- Defs: 107 total, 12 distinct types. Top 6: ThingDef=61, PawnKindDef=26, RulePackDef=5, HediffDef=3, TraderKindDef=3, TabulaRasa.UpdateDef=2.
- C#: OuterRimGalacticEmpire.dll, 10,752 bytes; Source/ present, 4 classes (one is `public static class Patch_OuterRimCoreMod_Settings` — a Harmony patch directly INTO `OuterRimCoreMod`'s settings, a genuine class-level coupling into Core's own C#, unlike any of the other 3 addon mods).
- Art: 0 loose files; AssetBundles `Common/AssetBundles/neronix17_outerrim_galacticempire`, 3,621,603 bytes (~3.5 MB).
- Declared deps: Neronix17.OuterRim.Core.
- Rev-deps: 0.
- Our-touch: **independently confirms this repo's existing "GalacticEmpire is reskinned vanilla" finding.** `src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml` patches the vanilla `Empire` FactionDef (Royalty), NOT this mod's `OuterRim_GalacticEmpire` FactionDef — that faction def is "struck from the records" per the patch file's own comment (owner, 2026-08-20). BUT the dependency on this mod is not fully cut: the same patch file states it "still references `OuterRim_Imp*` PAWN KINDS under MayRequire, so the Neronix17.OuterRim.GalacticEmpire dependency stays." `required_mods.md` logs it "ADOPTED 2026-08-12, 1.6 VERIFIED ON DISK" — trooper ladder, full stormtrooper wardrobe, `Imp_OfficerUniform_Black`, ISB variants, TraderKindDefs, training hediffs; "Harmony assembly — solo-load requirement waived." CherryPicker keys: UNCERTAIN (shared prefix), but 3 `OuterRim_Stormtrooper*_Pride` keys found under the generic prefix search plausibly belong to this module.
- Blockers: world-save `OuterRim_GalacticEmpire` (the FactionDef itself) = 1 (scan-grade; consistent with the faction being struck/unused per the patch comment). `OuterRim_Imp` = 129 (scan-grade; consistent with the Imperial pawnkind/apparel MayRequire dependency the patch file says still stands). C# coupling confirmed via the Harmony patch above.

### neronix17.outerrim.rebelalliance — Outer Rim - Rebel Alliance
- Loaded folders: `/`, `Common`, `1.6` (no gates).
- Defs: 47 total, 10 distinct types. Top 6: ThingDef=20, PawnKindDef=12, RulePackDef=5, TraderKindDef=3, FactionDef=2, TabulaRasa.UpdateDef=1.
- C#: Assemblies/1.6 empty; Source dirs at 1.4/1.5/1.6 all empty (0 files) — no C# ships in this mod.
- Art: 0 loose files; AssetBundles `Common/AssetBundles/neronix17_outerrim_rebelalliance`, 1,509,590 bytes (~1.4 MB).
- Declared deps: Neronix17.OuterRim.Core.
- Rev-deps: 0.
- Our-touch: `required_mods.md` — "ADOPTED 2026-08-12, 1.6 VERIFIED ON DISK, ENABLED AND SUPPRESSED." `src/Jawa/Jawa_Patches/Patches/RebelAlliance_Suppress.xml` zeroes `settlementGenerationWeight`, `requiredCountAtGameStart`, `canMakeRandomly`, `maxConfigurableAtWorldCreation` on the `OuterRim_RebelAlliance` FactionDef (deployed 2026-08-12 18:31) to keep the faction off the world map while keeping weapon/apparel content usable (e.g. `OuterRim_A280Blaster`); the file notes it "retunes and never deletes" because `ScenarioDefs/Scenario_Rebel.xml:115` references the def by name. CherryPicker keys: UNCERTAIN (shared prefix).
- Blockers: world-save `OuterRim_RebelAlliance` (the FactionDef) = 1 (scan-grade — consistent with a name-only reference, e.g. the scenario def, and no settlement, per the suppression patch's intent). No C# coupling — no C# ships in this mod.
- **Cross-cutting fact for the Neronix17 Outer Rim suite as a whole:** all 5 submods share one `OuterRim_` defName prefix, so CherryPicker/world-save counts cannot be attributed to a single submod by substring except via the two named FactionDefs and the `OuterRim_Imp` pawnkind family. Total shared-prefix world-save hits: `OuterRim_`=3156. CherryPicker total `OuterRim_` keys=3 (all Stormtrooper `_Pride` apparel).

### m3.continued.jangodsoul.starwars.bti — [JDS] StarWars - Armory
- Loaded folders: `1.6`, `Common` (Common has no Defs, only Sounds/Textures).
- Defs: 74 total (5 files). Top 6: ThingDef=51, SoundDef=18, HediffDef=3, WorkGiverDef=1, DamageDef=1.
- C#: none anywhere — pure XML/content mod.
- Art: 44 files, 0.35 MB; no AssetBundles.
- Declared deps: none.
- Rev-deps: 1 → M3.Continued.JangoDsoul.StarWars.TSDA (its About.xml confirms both `modDependencies` and `loadAfter` list BTI).
- Our-touch: `src/Jawa/Jawa_Armoury` patches touch its `JDSA_`-prefixed weapon defs via `infrastructure/state/canon.yml`'s turret_register — `JDSA_E-60R_Missile_Launcher` appears in the array-review, **not** in the ratified `normalization_ruled: true` turret list (~canon.yml lines 1140-1194). CherryPicker keys matching `JDSA_`: 0.
- Blockers: world-save scan-grade presence `JDSA_`=163 (not a verified def-reference count).

### m3.continued.jangodsoul.starwars.tsda — [JDS] StarWars - The Separatist Droid Army
- Loaded folders: `1.6` (which also has a Patches/ folder), `Common`.
- Defs: 59 total (7 files). Top 6: ThingDef=17, PawnKindDef=17, SoundDef=16, BodyPartDef=4, BodyDef=3, ScenarioDef=1.
- C#: none anywhere.
- Art: 65 files, 1.16 MB; no AssetBundles.
- Declared deps: M3.Continued.JangoDsoul.StarWars.BTI (both `modDependencies` and `loadAfter`).
- Rev-deps: 0.
- Our-touch: none found — `JDSCIS_`/`JDSSWCIS_`/`TSDA_` prefixes appear in no canon.yml or turret-register mentions. CherryPicker keys: 0.
- Blockers: world-save `JDSCIS_`=17, `JDSSWCIS_`=0, `TSDA_`=0 (scan-grade).

### maincrep.eweb — E-Web Heavy Repeating Blaster
- Loaded folders: no LoadFolders.xml → root `/` + top-level `1.6/`; defs only exist under `1.6/Defs/`.
- Defs: 8 total (4 files). Top 6: ThingDef=5, DamageDef=1, HediffDef=1, SoundDef=1.
- C#: none anywhere.
- Art: 5 files, 0.08 MB; no AssetBundles.
- Declared deps: none.
- Rev-deps: 0.
- **Author discrepancy, confirmed not corrected:** `About.xml` `<author>` = "Maincrep" only, but the mod's own filenames/defNames are RN2-branded (`BaseDef_Bullets_RN2.xml`, `RN2SWGun_EWeb_MG`, `RN2SWGun_EWebMounted_GPMG`, `RNShotEWebMG`) — consistent with the owner's "RN2's E-Web" memory even though the credited author field differs; likely republished/derived content rather than a misremembering.
- Our-touch: **already ruled on.** `infrastructure/state/canon.yml` (~line 1165) lists `RN2SWGun_EWeb_MG` inside the ratified 56-def `normalization_ruled: true` turret roster (owner, 2026-08-29), patched by `src/Jawa/Jawa_Armoury/Patches/Turrets_DamageDoctrine.xml` (EWebShot damageAmountBase→368, damageDef→OuterRim_Blaster) and `Turrets_Renames.xml` (label→"E-Web repeating blaster"). `design/Jawa/worldbuilding/review/turret_register.json`/`.decisions.json` note "assigned Empire, not settlers" and "the E-Web stays because it is a Star Wars repeating blaster despite the MG name." CherryPicker keys: 0.
- Blockers: world-save `RN2SWGun_EWeb`=6, `EWebShot`=1 (scan-grade).

### sov.sith — Rimwars: Pureblood Xenotype
- Loaded folders: no LoadFolders.xml, no top-level `1.6/` folder → root `/` only.
- Defs: 8 total (4 files). Top: GeneDef=3, HeadTypeDef=3, RulePackDef=1, XenotypeDef=1.
- C#: none anywhere.
- Art: 15 files, 0.21 MB; no AssetBundles.
- Declared deps: none.
- Rev-deps: 0.
- **Note:** no defName actually contains "sith" — real defNames are `PureBlood`, `GS_Eyes_Yellow`/`Orange`, `Head_Bone`, `NamerPersonPureblood`. The Sith framing exists only in the packageId/description text.
- Our-touch: none found — a broad "sith|pureblood" grep produced only unrelated false positives (matched substrings inside other words like "Miraluka" and general docs), none referencing this mod's actual defNames. CherryPicker keys: 0.
- Blockers: world-save `PureBlood`=0.

### btd.gbp.shippack.kotor.vge — [BTD] Ship Pack: KotOR Ships VGE
- Loaded folders: **unresolved discrepancy between the two measurement passes.** Its `LoadFolders.xml` v1.6 list is `/`, `1.6`, and a conditional `1.6/Mods/BTD_KotOR_Droids/` gated on `IfModActive="guy762.KotORDroids"`. `guy762.KotORDroids` IS a genuinely active mod in this mod list, so the gate should fire and that subfolder (which holds the mod's only `Defs/`) should load — one pass excluded it (treating the gate as not-active) and reported 0 defs; the correct reading per the confirmed-active mod list is that the gate fires. **Def count is therefore UNCERTAIN, likely understated at 0** — treat as needing a direct re-check before any absorb/keep call, not as a genuinely empty mod.
- Defs: 0 measured under the (likely incorrect) excluded-gate reading. Under the correct reading the gated `1.6/Mods/BTD_KotOR_Droids/Defs` folder's contents were not separately counted — UNMEASURED.
- C#: none anywhere in the mod.
- Art: 2 files, 4.77 MB; no AssetBundles. Also ships 2 `.btd` gravship-blueprint files (Gravship Blueprints/KotOR/*.btd) — its actual functional content is these ship blueprints, not Defs.
- Declared deps: ludeon.rimworld.odyssey, brrainz.harmony, btd.remix.gravshipblueprints.
- Rev-deps: 0 given; a direct full read of `guy762.KotORDroids`'s `About.xml` found **no** mention of "btd", "btd.gbp", "kotor ship", or "shippack" in either direction — the earlier substring-scan hit could not be reproduced, likely a false positive.
- Our-touch: none found.
- Blockers: world-save `btd.gbp.shippack.kotor` = 1 hit (scan-grade; likely the packageId appearing once in the save's active-mod-list header rather than functional content — UNCERTAIN).

### lumi.doorsexpanded — Doors Expanded Star Wars edition
- Loaded folders: no LoadFolders.xml → root only.
- Defs: 41 total. Top: SoundDef=18, ThingDef=18, ResearchProjectDef=4, ResearchTabDef=1.
- C#: none; no Source/.
- Art: 71 files, ~0.65-0.80 MB texture (two measurement passes varied slightly); ~19 audio files, ~0.29-0.34 MB; no AssetBundles.
- Declared deps: brrainz.harmony, jecrell.doorsexpanded (both confirmed active).
- Rev-deps: 0.
- **Our-touch — retirement blocker:** `src/RimMandrake/BlastDoorFrameAsyncFix/` is our own Harmony fix whose `About.xml` declares a hard dependency on packageId `Lumi.doorsexpanded`, targeting an east split-frame door bug in this mod specifically. Retiring the mod without porting the fix (or the bug it addresses) is a live regression risk. Also present in the ideoligion mod-list snapshot (`MandrakeJawa.xtp`). A grep hit in `design/Jawa/mods/required_mods.md` was checked and is a false positive — it names a different mod ("Security Doors Expanded," workshop id 3777106218). CherryPicker keys: 0 (defNames mix `PH_`/`SW_`/`Heron*`/`Mono*`/`ProjectHeron_` prefixes, no single consistent prefix).
- Blockers: scan-grade world-save presence — two measurement runs disagreed on the `PH_` count (102 vs. 162, likely different grep patterns, UNCERTAIN which is right); `SW_DoorJail`=6 (both runs agree); `ProjectHeron_`=28 (one run only). No outerrim.core coupling.

### lumi.swlights — Star Wars Lights
- Loaded folders: no LoadFolders.xml → root only.
- Defs: 3 ThingDef (1 abstract, 2 concrete: `SwLightA`, `SwLightB`).
- C#: none; no Source/.
- Art: 8 files, 0.036 MB; no AssetBundles.
- Declared deps: none.
- Rev-deps: 0.
- Our-touch: only appears in the ideoligion mod-list snapshot (`MandrakeJawa.xtp`) — no design or code touches found. CherryPicker keys: 0.
- Blockers: world-save `SwLightA`+`SwLightB` combined = 10. No coupling.

### mlie.starwarsanimalcollection — Star Wars Animal Collection (Continued)
- Loaded folders: no LoadFolders.xml → root (About/AssetBundles/1-file Textures/Languages/News) union top-level `1.6/` (Defs/Patches).
- Defs: 1581 total, 1288 unique defNames. Top 6: SoundDef=589, ThingDef=455, PawnKindDef=160, BodyDef=102, IdeoIconDef=90, ThoughtDef=33. Also 6-17 conditional PatchOperation files (measurement runs varied on the exact op count).
- C#: none; no Source/.
- Art: root `Textures/` = 1 file, 36 KB — the real art (and audio) is packed in `AssetBundles/Mlie_StarWarsAnimalCollection`, ~32-33 MB total (2 bundle files); per-file counts inside the bundle are UNCERTAIN, not extractable by a file listing.
- Declared deps: `<modDependencies />` present but empty.
- Rev-deps: 0.
- **Our-touch — largest, most load-bearing touch found in this survey.** `design/Jawa/mods/required_mods.md` cites it as ADOPTED, resolving Bantha and Sarlacc (~150 verified SW creature ThingDefs); counted in `armoury_keeplist.md` ("Star Wars Animal Collection (10)"); referenced in `forbidden_mods.md`'s monster-roster policy; 3 of our own patch files fix its assets directly (`Jawa_Patches/Patches/BehemothArtUpres_StarWarsAnimalCollection.xml`, `AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`); `design/Jawa/fauna/*.csv` census + cast-assignment docs and `animal_contact_sheet.py`/`extract_bundle.py` tooling all depend on it. CherryPicker keys: 0 of 1288 defNames exact-match against the live 1505-key config.
- Blockers: defNames carry **no consistent mod prefix** (bare species names: `Bantha`, `Rancor`, `Nexu`, `Wampa`, `Tauntaun`, `Dewback`, `Acklay`, `Reek`, `Vulptex`, `Porg`, `KraytDragon`...). Sampled scan-grade world-save presence: `Bantha`=210, `Rancor`=114, Sarlacc-family=40, `Wampa`=17, `Nexu`=21, `Dewback`=32, `Acklay`=43, `Reek`=92, `Vulptex`=10, `Porg`=32, `Tauntaun`=10 — a full 1288-name sweep was not run (out of scan-grade scope). No outerrim.core coupling.

### starwars.themedsounds — Star Wars Themed Sounds
- Loaded folders: `LoadFolders.xml` present (lowercase filename on disk), `<v1.6><li>Common</li></v1.6>` → loaded set is `Common/` **only** (not root): unions `Common/Patches`, `Common/Sounds`, `Common/Textures`.
- Defs: 0 native — no `Defs/` folder exists at all. Its entire content is 1 patch file (`Common/Patches/SoundDefs/SWTS_Replacer.xml`): a single `PatchOperationSequence` wrapping 11 `PatchOperationReplace` sub-ops (10 unconditional + 1 `MayRequire="Ludeon.Rimworld.Biotech"`), retargeting vanilla `SoundDef` `clipPath`/`clipFolderPath` (LetterArrive*, Quest_Accepted/Succeded/Concluded/Failed, Message_PawnDeath, Explosion_Bomb/GiantBomb) to this mod's own audio clips. Defines zero of its own defNames.
- C#: none; no Source/.
- Art: 1 texture file, 24 KB (likely just the mod icon); audio (its actual content) 17 `.ogg` files, 444 KB total; no AssetBundles.
- Declared deps: none in `<modDependencies>` (About.xml has no `modDependencies` block at all, only `loadAfter` listing Ludeon.RimWorld + Royalty/Ideology/Biotech/Anomaly).
- Rev-deps: 0.
- Our-touch: no content hits in `src/Jawa`, `src/RimMandrake`, `design/Jawa` — the packageId string appears only as embedded active-mod-list metadata inside 3 ideoligion export files (`MandrakeJawa.xtp`, `The Salvation.rid`, `witness/The Salvation.2026-08-14.game.rid`), confirming it was active at export time, not a design/code dependency. No native defNames, so no CherryPicker/world-save prefix check applies.
- Blockers: not applicable — patch-only against vanilla defNames, nothing of its own to scan for. No Outer Rim Core coupling.

### leutiankane.mineablesor — LK Mineable Resources Outer Rim
- Loaded folders: no LoadFolders.xml → root only.
- Defs: 4 ThingDef (`LKDurasteel_Ore`, `LKBeskar_Ore`, `LKPureBeskar_Ore`, `LKORComponent_Ore`). Separately, `Patches/` holds 13 PatchOperations across 2 files.
- C#: none; no Source/.
- Art: 0 files, 0 MB; no AssetBundles.
- Declared deps: brrainz.harmony, Neronix17.OuterRim.Core (both confirmed active).
- Rev-deps: 0.
- Our-touch: `design/Jawa/worldbuilding/desert_world_design.md:380-390` records an owner ruling, 2026-08-12, to keep it ("something on the map to find, and then have to leave behind"), with a verified yield table; `src/RimMandrake/Utils/harvest_log.py` carries a log-error regex specifically watching for "MineablesOR" exceptions. CherryPicker keys: 0 of its 4.
- **Blockers — structural coupling, unguarded.** Its own 4 ThingDefs set `mineableThing` directly to `OuterRim_Durasteel`/`OuterRim_Beskar`/`OuterRim_PureBeskar`/`OuterRim_ComponentHypertech` — a hard cross-reference, not a patch guard. Its 13 patch ops also target `Defs/ThingDef[defName="OuterRim_*"]` (Tibanna, ComponentHypertech, Beskar, Duracrete, Durafiber, Durasteel, Permacrete, Plastcrete, PureBeskar) via `PatchOperationAddModExtension`/`Add`, plus Ideology/Odyssey-gated GenStepDef xpaths. **No `PatchOperationFindMod`/`Conditional` gate exists anywhere** — if `neronix17.outerrim.core` is retired, this mod's 4 ThingDefs get unresolved cross-references and its patch ops resolve to zero nodes and silently no-op. World-save exact-string presence (its own ThingDefs): `LKDurasteel_Ore`=1, `LKBeskar_Ore`=1, `LKPureBeskar_Ore`=1, `LKORComponent_Ore`=1.

### leutiankane.mines2patchouterrim — LK Mines 2.0 Compatability[Outer Rim Core]
- Loaded folders: no `LoadFolders.xml`, and no top-level `1.6/` folder anywhere in this mod — all content sits under an unversioned `Common/Patches/` folder. This falls outside the task's literal default-load rule (root + `1.6` only), which does not explicitly cover an unversioned `Common/`. RimWorld conventionally loads an unversioned `Common/` alongside root by default even without `LoadFolders.xml` declaring it, but this was not independently verified against engine source in this survey — **flagged rather than asserted**; if the convention does not hold for this specific mod, its single patch file never loads at all, which would itself be a notable fact about this mod's real-world functionality.
- Defs: 0 native. Content is patch-only: 9 `PatchOperationAddModExtension` operations in 1 file (`Common/Patches/Patch_Mines2.0OuterRim.xml`).
- C#: none; no Source/.
- Art: 0 files, 0 MB — no `Textures/` folder exists at all.
- Declared deps: brrainz.harmony, Cain.Mineshaft ("Mines 2.0" — confirmed active), Neronix17.OuterRim.Core (confirmed active; also duplicated in `loadAfter`).
- Rev-deps: 0.
- Our-touch: `design/Jawa/worldbuilding/desert_world_design.md:489-495` — an owner override, 2026-08-12, "Mines 2.0 IS LIVE," confirming `cain.mineshaft` + this mod + `leutiankane.mineablesor` are all enabled together (573 active mods at the time of that note); the doc explicitly flags the patch as "unguarded." `src/RimMandrake/Utils/harvest_log.py` carries a log-error regex watching for "Mines2patch" exceptions. No native defNames, so no CherryPicker/world-save prefix check applies.
- **Blockers — structural coupling, unguarded.** All 9 patch ops target `Defs/ThingDef[defName="OuterRim_*"]` (Tibanna, ComponentHypertech, Beskar, Duracrete, Durafiber, Durasteel, Permacrete, Plastcrete, PureBeskar), injecting `<li Class="MinesAutomatedExtension.MineableSettings">` — a `Cain.Mineshaft`/Mines 2.0 C# type — with `researchPrerequisites=OuterRim_HypertechFabrication`. **No `PatchOperationFindMod`/`Conditional` gate exists anywhere in the file.** If `outerrim.core`'s `OuterRim_*` ThingDefs or Mines 2.0's `MineableSettings` class become unavailable, all 9 operations either match nothing (silent no-op) or leave a dangling defName reference inside Mines 2.0's own bill list.

### *(borderline)* jecrell.jecstools — JecsTools Unofficial 1.6 BETA
- **SW-verdict: not SW-themed.** A general C# modding framework/library. Its own `About.xml` states "This mod will not change your game, but rather it lets modders do more" and lists generic components (CompAbilityUser, CompDeflector, CompSlotLoadable, CompLumbering). Its one SW-adjacent phrase — "lightsaber beam," "ATST walking effect" — is explicitly a usage EXAMPLE describing what a downstream mod *could* do with a component, not shipped content. Source filenames (`AbilityDef.cs`, `AoEProperties.cs`, `ApparelExtension.cs`, etc.) confirm zero SW-specific code.
- Loaded folders: `/` (no Defs at root) union `1.6`.
- Defs: 27 total. Top 6: JobDef=6, StatDef=6, RulePackDef=5, ThingDef=3, StatCategoryDef=2, AbilityUser.AbilityDef=1.
- C#: `Assemblies/1.6` holds 18 DLLs (0JecsTools.dll 114 KB, AbilityUser.dll 77 KB, CompSlotLoadable.dll 37 KB, PawnShields.dll 35 KB, CompDeflector.dll 28 KB, plus 13 smaller comp DLLs). `Source/` present, 549 `.cs` files, ~163 class declarations by grep count — the deepest C# of any mod in this survey.
- Art: 2 files, 8 KB (root only; `1.6/Textures` empty); no AssetBundles.
- Declared deps: brrainz.harmony.
- Rev-deps: 3 mentions (guy762.KotORWeapons, guy762.MM.KotORCore, lee.theforce.lightsaber) — **all three are soft `loadAfter` mentions only; none is a hard `modDependencies` entry** on jecstools, confirmed by reading all three mods' own `About.xml`.
- Our-touch: 5 files matched a broad grep but all are false-neutral (mod-list metadata inside the ideoligion save, `required_mods.md`, two worldbuilding docs) — no turret-canon or content ruling references jecstools. CherryPicker keys: 0.
- Blockers: since the 3 SW mods only soft-reference jecstools, retiring it would not break their declared dependency chains — but its C# (CompActivatableEffect/CompOversizedWeapon/CompSlotLoadable) is plausibly what those mods' lightsabers/oversized-weapon graphics actually use at runtime even without a formal `modDependencies` entry — **UNCERTAIN without a live game test**.

### *(borderline)* vanillaexpanded.vfesecurity — Vanilla Furniture Expanded - Security
- **SW-verdict: not SW-themed / generic sci-fi.** Description frames it as tech-tier defense progression ("Medieval... Industrial... Trench Warfare... Spacer") with "tesla blasters," "railguns," "charge turrets" as generic weapon-tech vocabulary, not Star Wars branding. However, its content is not incidental to us — see our-touch.
- Loaded folders: `/`, `1.6` (Anomaly/Biotech/VWE_NonLethal gated subfolders excluded — none of those gates are active).
- Defs: 86 total. Top 6: ThingDef=61, ResearchProjectDef=7, SoundDef=5, HediffDef=3, JobDef=2, WorkGiverDef=2.
- C#: `VFESecurity.dll`, 79,872 bytes, in `1.6/Assemblies` (older 1.4/1.5 copies exist but are not loaded); no `Source/` — compiled only.
- Art: 231 files, 6.4 MB (root `Textures/`; no separate 1.6 texture folder); no AssetBundles.
- Declared deps: brrainz.harmony, OskarPotocki.VanillaFactionsExpanded.Core.
- Rev-deps: 3 given (FrozenSnowFox.ComplexJobs, Aoba.Fortress.Industrial, toastyman.moreritualseats) — not independently re-verified.
- **Our-touch — directly touched, already partially absorbed.** `src/Jawa/Jawa_Armoury/Patches/Turrets_Renames.xml`, `Turrets_DamageDoctrine.xml`, `Armoury_RangedDamage.xml`, `src/Jawa/Jawa_Armoury/Source/gen_turret_doctrine.py`, `design/Jawa/reconciled_lore/04_factions.md`, plus the `turret_register` review artifacts under `design/Jawa/worldbuilding/review/`. `infrastructure/state/canon.yml` lines 1182-1188 keeps 7 VFES defs in the `official_roster`: `VFES_Complex_GraserCannon`, `VFES_Complex_HeavyIncineratorComplex`, `VFES_Turret_Ballista`, `VFES_Turret_ChargeRailgun`, `VFES_Turret_Flame`, `VFES_Turret_Searchlight`, `VFES_Turret_TeslaBlaster` — commit `d94fbc53`'s message states "tesla+railgun=Helix" (assigned to the Ascendant Helix faction), and canon.yml line 1209 notes "'Flamer Turret stays for the Wildsteam' (VFES_Turret_Flame)." CherryPicker keys: 17 `VFES_` ThingDef keys present in the live cut-list — a **different** set of defNames than the 7 kept in `official_roster` (i.e. 17 items already cut, 7+ already kept/absorbed).
- Blockers: `MEASURE_ALLOW_SCAN=1 grep -c "VFES_"` on `WORLDMAP_V1_original.rws` → 371 (scan-grade presence — real, live content on the frozen world).

### *(borderline)* rpgwanderer.opturret — Archotech Blaster Turret
- **SW-verdict: not SW-themed.** A single-item mod ("an archotech blaster turret using archites clouds"); "blaster" here is generic sci-fi weapon vocabulary tied explicitly to RimWorld's own archotech lore, not Star Wars.
- Loaded folders: no LoadFolders.xml, no top-level `1.6/` folder → root only.
- Defs: 3 ThingDef (`Bullet_ArchotechChargeBlasterHeavy`, `Gun_ArchotechChargeBlasterHeavyTurret`, `Turret_AutoChargeBlaster_OP`).
- C#: none; no Source/.
- Art: 84 KB total under Textures/.
- Declared deps: none.
- Rev-deps: 0.
- **Our-touch — directly named in the owner's ruling.** No design-doc references it by mod name (the earlier grep hits were the ideoligion save's embedded mod-name list, not design content), but `infrastructure/state/canon.yml`'s `official_roster` (line 1168) explicitly keeps `Turret_AutoChargeBlaster_OP`, and the ruling text (line 1205) quotes the owner: "'archotech allowed to be x4 expected' (Turret_AutoChargeBlaster_OP)." CherryPicker keys: 0.
- Blockers: `MEASURE_ALLOW_SCAN=1 grep -c "Turret_AutoChargeBlaster_OP"` on the world save → 5; `Gun_ArchotechChargeBlasterHeavyTurret` → 3. Both present on the frozen world.

## Cross-cutting facts across the whole survey

- **Zero of the 20 core SW mods' defNames appear in the live CherryPicker config**, except the 3 shared-prefix `OuterRim_Stormtrooper*_Pride` keys attributable to the Neronix17 suite and the 17 `VFES_` cut-list keys on the borderline vfesecurity mod. Nothing in this survey has been cut via CherryPicker to date.
- **Two hard retirement blockers found where our own code depends on upstream art/behavior surviving unchanged:** `src/RimMandrake/KotORBandolierNorthFix` (into `guy762.mm.kotorcore`) and `src/RimMandrake/BlastDoorFrameAsyncFix` (into `lumi.doorsexpanded`). Both declare hard `modDependencies` on the mod they patch.
- **Two mods already carry an owner ruling that specific defNames are kept/renamed/re-doctrined without a full absorb:** `maincrep.eweb` (folded into the ratified 56-def turret roster) and `rpgwanderer.opturret` (named directly in the same ruling). `vanillaexpanded.vfesecurity` has 7 defs kept the same way alongside 17 already cut.
- **Two mods (`leutiankane.mineablesor`, `leutiankane.mines2patchouterrim`) are structurally unguarded hard dependents of `neronix17.outerrim.core`** — no `PatchOperationFindMod`/`Conditional` gates their cross-references to `OuterRim_*` defNames anywhere in either mod's XML. Retiring/absorbing Core without also handling these two produces silent no-ops or dangling references, not a clean removal.
- **`neronix17.outerrim.galacticempire` is the one Neronix17 addon with a genuine C#-level coupling into Core** (a Harmony patch on `OuterRimCoreMod`'s own settings class) — the other three addons couple only through defName cross-references and declared `modDependencies`.
- **`mlie.starwarsanimalcollection` is both the largest content mod in def count (1581) and the most deeply woven into our own tooling** (fauna census CSVs, contact-sheet/bundle-extraction scripts, 3 of our own art-fix patches) of anything measured here.

---

# The trades layer (BENCH synthesis, 2026-08-30 — owner rules via cards)

**The one structural fact the droid wave didn't have:** the frozen world save
ALREADY HOLDS these mods' defNames (7 KotOR weapon defs, 163 `JDSA_`, 3,156
`OuterRim_`, 68 lightsaber occurrences). Droidworks could mint `DW_` names
because zero droids were scribed; the weapons/content waves CANNOT — they must
**preserve defNames** (our defs, their names — patch-of-theseus absorption) or
pay save surgery per wave. This is cheap to honor and changes nothing about
ownership; it just means the defs keep their old names inside OUR mod.

## Absorption tiers

**Tier 1 — the weapons/gear wave** (high value, pure-XML, armoury already owns
the numbers): kotorweapons (679 defs, NO DLL — the biggest win per effort),
kotorcore's materials/apparel (1,235 defs; kills the ABF-wiring blocker AND our
BandolierNorthFix becomes part of the absorbed art), JDS Armory (74), E-Web (8,
already roster-ruled), sov.sith (8; zero world presence — could simply cut),
opturret (3, roster-ruled). Art: ~130 MB yank (many small files; owner
regenerates over time). Retires 5-6 mods.

**Tier 2 — the C#-ownership waves**: ① lee.theforce.lightsaber STAYS
UPSTREAM (owner, 2026-08-30: peripheral to the scenario, outside the ingest
plan; compatibility-tested alongside our mods later — the behavioral inventory
at force_system_inventory.md serves that experiment). ② outerrim.core — 446 defs + SOURCE ON DISK
(22 classes; easiest C# absorption in the load) but 3,156 world-save hits and
two unguarded mines addons hang off it: defName preservation is mandatory and
the addons get re-pointed or absorbed with it. Galactic Empire / Droid Depot
addons ride Droidworks + this.

**Tier 3 — keep upstream, absorb never-or-late:** starwarsanimalcollection
(1,581 defs, zero C#, deepest tooling integration — pure content, nothing to
own), furnitureanddecor (cosmetic, zero deps), lumi doors/lights + themedsounds
(tiny), vfesecurity + jecstools (not genuinely SW; cut-managed / framework),
rebelalliance (kept-suppressed, scenario ref), btd ship pack (UNCERTAIN 0 defs
— re-check owed before any call).

**Our own fix mods**: KotORBandolierNorthFix folds into the Tier-1 absorption
(its art becomes the absorbed art); BlastDoorFrameAsyncFix stays (lumi stays).
