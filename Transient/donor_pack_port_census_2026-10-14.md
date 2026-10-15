# Donor pack port census: mlie.starwarsanimalcollection (2026-10-14, read-only)

**Bottom line.** The pack is pure XML (no DLL), MIT, 160 races + 160 PawnKindDefs, art in a 33.5 MB AssetBundle (no loose textures). 101 of 160 species already have an `RSW_` ThingDef+PawnKindDef twin with its own loose art; only 24 of those are fully off the donor in rosters. 59 species are NOT_PORTED (13 plain, 7 plain with small item/ability deps, 39 need a custom BodyDef ported). Nothing needs new C#. The three `DONOR_CODE_*` items are about Alpha Animals (`AA_*`, `VFEI2_*`), not this pack: zero species overlap.

**Corrections to what the items say.**
- The item `DONOR_DEFS_PORT_TO_OURS_1` says the pack is "vendored at `vendor/mod_sources/StarWarsAnimalCollection_src`". That directory does not exist (`ls`; `vendor/mod_sources/` holds only `SOURCES.md`). The only source is the Steam workshop copy.
- "160 entries" is the pack's race count (measured below), not today's roster row count. Today's rosters name 71 distinct species in 90 rows.
- Mynock: `RSW_Mynock` exists but is an owner-authored ship-vermin species; the donor `Mynock` is declined permanently (`mlie_wave_c_worklist.json` `declined_species`). My name-twin test counts it as a twin; treat it as DECLINED, not ported.
- The wave-C worklist (`infrastructure/state/facts/mlie_wave_c_worklist.json`, `remaining_worklist` = 0, last edit 2026-09-18) only covered species in the old Ashkarr `cast_assignment.csv`. "Wave C complete" is not "pack complete".

## 1. Donor source (measured by XML parse of `1.6/Defs`, workshop folder)

| fact | value | how |
|---|---|---|
| folder | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3497316713` | scanned both roots' `About.xml` packageIds; only this one matches |
| packageId | `Mlie.StarWarsAnimalCollection` (rosters write it lowercase; MayRequire is case-insensitive) | About.xml |
| in Steam `Mods` root | not present (only our SWBestiary, GizkaStowaway etc., which merely `loadAfter` it) | scan |
| active now | yes, in live `ModsConfig.xml` (23 activeMods at read time) | ET.parse |
| not this mod | workshop `3557220601` is `lee.theforce.standalone` | About.xml |
| C# assembly | NONE. No `Assemblies/` in the mod root or `1.6/` | `find *.dll` returned 0 |
| license | MIT (LICENSE.md, "Copyright (c) 2018 Tyler (Tgrimm92)") | read file |
| art | `AssetBundles/Mlie_StarWarsAnimalCollection` 33,571,847 bytes; loose `Textures/` is 36 KB (icon only) | `ls -la`, `du` |

Def counts, non-abstract, all `1.6/Defs/**/*.xml` (ET parse): ThingDef 454 (of which 160 have a `<race>`; the other 294 are items, plants, corpses, buildings), PawnKindDef 160, BodyDef 102, BodyPartDef 17 (+1 abstract), BodyPartGroupDef 23, SoundDef 589, IdeoIconDef 90, ThoughtDef 33, RecipeDef 20, AbilityDef 16, TrainableDef 16, HediffDef 14, TileMutatorDef 9, NegativeFishingOutcomeDef 16, others 1 to 4 each. PawnRenderTreeDef 2, ThinkTreeDef 0, ThinkNode 0. Every race has exactly one PawnKindDef (race-without-kind = []).

Classes our creatures would need: every `Class=` in the defs is a stock RimWorld class. Race comps: `CompProperties_EggLayer`/`Hatcher` x71, `Milkable` x16, `Shearable` x12, `CanBeDormant`/`WakeUpDormant` x9 (Anomaly). One vanilla render node `PawnRenderNodeProperties_BulbfreakTentacle` (Beldon). Two soft third-party extensions: `NocturnalAnimals.ExtendedRaceProperties` x15 and `PathfindingFramework.MovementExtension` x15 (both MayRequire-guarded, degrade to nothing). So NEEDS_CODE count = 0.

## 2. Roster rows naming the pack (parsed as XML elements, not grep)

63 BiomeDefs under `src/`. Rows = child elements of `<wildAnimals>` carrying `MayRequire` containing `starwarsanimalcollection`.

| BiomeDef file (`D:\Luke\dev\...` equivalents under `src\RimUtinni\UtinniPatches\Defs\BiomeDefs\`) | rows | distinct |
|---|---:|---:|
| RUT_AridShrubland.xml | 31 | 31 |
| RUT_Greentide.xml | 18 | 18 |
| RUT_Miasma.xml | 8 | 8 |
| RUT_WeepingStones.xml | 8 | 8 |
| RUT_FeverWood.xml | 6 | 6 |
| RUT_CrackedLands.xml | 5 | 5 |
| RUT_Cauldron.xml | 3 | 3 |
| RUT_TheForge.xml | 2 | 2 |
| RUT_Webwork.xml | 2 | 2 |
| RUT_Scarlands / RUT_TheRot / RUT_Wasteland | 1 each | 1 each |
| **BiomeDef total** | **86** | **68** |

Plus 4 rows injected by patches (`src\RimUtinni\UtinniPatches\Patches\` `WildAnimals_TheRot` Snoruuk, `WildAnimals_BlueDesert` Vapaad, `WildAnimals_TheForge` Tibidee, `WildAnimals_NightsideIce` Tauntaun). **Total 90 rows, 71 distinct species.** Other non-roster references: 3 faction `carriers` (Bantha x2, Dewback, in JawaHuttCartel / JawaWildsteamClan), 12 `wildPlants` rows (9 distinct donor plants, outside the fauna scope), 1 landmark mutator (`sw_DeadSarlaccCave`), 2 `specificMeatDef` in `SeaBeasts_Scalefish.xml`.

**Rows with NO MayRequire that name a donor species: 0** (checked every `<wildAnimals>` child in all of `src/`; probe: the same loop does find the 86 guarded rows, so it can see). The "19 unguarded desert rows" in the item are gone.

## 3. Twin status, all 160 species (twin = `RSW_/RM_/RUT_<Name>` race ThingDef under `src/`; name match; 101 matched, label-only matches 0)

| class | all 160 | of the 71 referenced | of the 89 unreferenced |
|---|---:|---:|---:|
| ALREADY_PORTED_AND_WIRED (twin named in a roster, no donor row left) | 24 | 0 | 24 |
| WIRED_BUT_DONOR_ROW_REMAINS (twin in one roster, donor row still in another) | 18 | 18 | 0 |
| TWIN_EXISTS_NOT_WIRED | 59 | 48 | 11 |
| NOT_PORTED | 59 | 5 | 54 |

- ALREADY_PORTED_AND_WIRED: Bolotaur, FeralGrazer, Gizka, GreaterKraytDragon, Gutkurr, Horax, Hrumph, IridonianReek, Jakobeast, Jimvu, KraytDragon, Kreetle, Krykna, Kwi, Nerf, Nuna, Shaak, TeeMuss, Uvak, Varactyl, WarWyrm, Worrt, Wraid, Zeer.
- WIRED_BUT_DONOR_ROW_REMAINS: Bantha, Clodhopper, Eopie, Falumpaset, FrilledGorg, Gorg, GraniteSlug, Iriaz, Jamel, LongtailGorg, Ronto, Runyip, Scurrier, ShiroTrap, Shyrack, Skalder, Sketto, Voorpak.
- TWIN_EXISTS_NOT_WIRED, referenced (48): the roster still names the donor name though `RSW_<X>` exists. Examples: Anooba, Beldon, Boma, Convor (4 rows), Dewback, Fambaa, Whisperbird (4 rows), Urusai, Vornskyr. Whole list is the "TWIN_EXISTS_NOT_WIRED" rows of the ledger table in the script output; includes Mynock (DECLINED, see top).
- TWIN_EXISTS_NOT_WIRED, unreferenced (11): Acklay, Blarth, Blixus, Blurrg, Bogwing, Dianoga, MarshHaunt, Orray, Scavrat, Wampa, WompRat.
- Referenced but NOT_PORTED (5): Snoruuk (TheRot), Tauntaun (NightsideIce), Tibidee (TheForge), Vapaad (BlueDesert), Wyyyschokk (Webwork).

So the real wiring job today is ~66 donor-named roster rows (48 + 18 species) to repoint to existing twins, with the 5 unported species ported first. Twin art: 100 of 101 twin PawnKindDefs have every `texPath` present as loose PNG under some `src/**/Textures` (case-insensitive prefix match, coarse); `RSW_Scurrier` has 6 of 9 paths present. Twin race ThingDefs are counted by existence only, I did not diff their stats against the donor.

## 4. Port cost of the 59 NOT_PORTED (by donor XML parse; "items" = donor ThingDefs reachable from the race with no `RSW_`/`RM_`/`RUT_` same-name def in `src/`, a name heuristic, so verify per species)

| grade | n (referenced) | species |
|---|---:|---|
| PLAIN (vanilla body, no ability, no unported items) | 13 (0) | Boarwolf, Bordok, Bursa, CorellianHound, Gualaar, Leaftail, Narglatch, Raxshir, Squall, Stintaril, Tach, Tooke, TuskCat |
| PLAIN + small item/ability deps (vanilla or already-ported body) | 7 (0) | Grazer, HarvesterBeetle, IthorianReek, KellDragon, Reek, LothWolf (SW_ForceChaosSkip unported), Maalraas (SW_ForceInvisibility unported) |
| SHARED_BODY, custom BodyDef only | 12 (1) | Aiwha, Behemoth, Devourers, FrogDog, Insectomorph, Katarn, Manka, Mawvorr, Nexu, Tibidee, Tukata, Veermok |
| SHARED_BODY plus items/abilities | 27 (4) | Akk, Brezak, ChrysalideRancor, Drexl, EnergySpider, Gullipud, Gundark, JungleRancor, Kaadu, KwazelMaw, MastiffPhalone, Mastmot, PaintedSpat, Rancor, Rikknit, Roggwart, Rycrit, Silooth, Snoruuk, Taozin, Tauntaun, TetnissCrab, Thranta, Torton, Vapaad, Warbird, Wyyyschokk |
| NEEDS_CODE | 0 | none; pack has no assembly |

Detail: body sharing among the 59 is Rancor x3 (Rancor, JungleRancor, ChrysalideRancor), Kaadu x2 (Kaadu, PaintedSpat); other bodies are one-per-species. Unported abilities still owed (pure XML, vanilla classes): SW_AcidSpew, SW_ForceChaosSkip, SW_ForceInvisibility, SW_SootheSong, SW_Spit, SW_ToxicSpew (others like SW_Calamity, SW_Leap, SW_Rampage, SW_Spur, SW_ForceFocus, SW_ForceScream already have `RSW_` copies). `MovementExtension` (Gullipud, Kaadu, KwazelMaw) is an external-mod soft extension: port as MayRequire-guarded or drop. The wild-flora, the 9 `Plant_*_Wild` donor plants and 294 non-race ThingDefs (items) are separate scope from the 160 creatures.

**Sibling items overlap: none.** `DONOR_CODE_PLAIN_PORTS_1` (Agaripawn, Agaripod, DecayDrake, MycoidColossus, Radyak, RipperHound, Thermadon), `DONOR_CODE_BURST_REBUILD_1` (AcanthamoebaGigantea*, GreenGoo, RedGoo, RedSpore, InfectedAerofleet, Thunderbeast) and `DONOR_CODE_SHAPE_REBUILD_1` (ColossalAerofleet, Mantrap, OcularJelly) are all `sarg.alphaanimals`/`AA_` creatures whose C# lives in `AlphaBehavioursAndEvents.dll`. They are the template for the later 102-row Alpha pack, not for this one. (Item titles read from `infrastructure/state/ledger/events/FOUNDRY.jsonl`; no `DONOR_CODE_*` file exists in `items/`.) The script `src/RimMandrake/Utils/donor_plain_ports_check.py` is specific to those 7 ports.

## 5. Port mechanics already in the repo

No generic "port" script exists. The closed item `infrastructure/state/items/closed/MLIE_FAUNA_ABSORPTION_1.md` (2666 lines, 25+ passes, 2026-09-02 to 2026-09-18) is the recipe, run by hand per batch of ~3 species:
1. Take the species ThingDef+PawnKindDef from the donor `Races_Animal_SW.xml`, rename `defName` flat to `RSW_<Species>`, keep `texPath` casing of the donor's own path.
2. Bring every dependency along: custom `BodyDef` (into `RSW_MlieWave*_Bodies.xml`; `BodyParts_StarWars.xml` was ported whole), `AbilityDef`/`HediffDef`/`TrainableDef` trios, resource ThingDefs (meat, leather, eggs, trophies; parent must be our `RSW_SWanimals_RawMeatBase`, not the donor's bare abstract; a Pass-8 bug), `ThoughtDef`s. Sounds were absorbed whole earlier (`extract_mlie_sounds.py`, 589 `SoundDef`s, map `infrastructure/state/facts/mlie_sound_defname_map.json`).
3. Art: `python src/RimMandrake/Utils/extract_bundle.py` (`--list`, `--find`, `--extract`; `--keep-paths` lowercases, so rename to the def's casing) against the LIVE workshop bundle. `vendor/mod_sources` bundle copy is stale (4.6 MB) and unreadable. Exclude unreferenced "Pack" variants; watch bundle typos (`FrilledGorgAA_east`).
4. Before extracting art, list `*ArtOverride` mods for the species (the item says `src/RimStarWars/*ArtOverride`; I found no `*artoverride*` folder within depth 3 under `src/` today, so re-check) so donor art does not overwrite an owner redo (Anooba, Dragonsnake regression).
5. Rename the roster row in place (previously `BiomeCast_Ashkarr.xml` x2 + `design/Jawa/fauna/cast_assignment.csv`; those files no longer exist, rosters now live in `RUT_*` BiomeDefs and `UtinniPatches/Patches/WildAnimals_*.xml`). Keep the `MayRequire` guard handling, then record the old-to-new name in `infrastructure/state/facts/mlie_creature_defname_map_wave_{a,b,c}.json`.
6. Validate with `validate_patch.py` using both `--live` and `--defs`; deploy via `deploy_custom_mods.py --mod SWBestiary --apply`. Final proof is a cold load with the donor disabled (never done; donor still active).
Output lives in `src/RimStarWars/SWBestiary/Defs/...`.

**Art licensing.** The code and art are MIT (verified against the donor's own `LICENSE.md` in the item, and again here), so copying is legal. But the owner ruling "no donor art kept" (2026-10-05, memory `no-donor-art-kept`): extracted donor art is a stand-in only, and every ported species still needs at least one render of ours on its review sheet, with donor art shown as a "past art" provenance column. So `texPath` re-pointing is mechanical, but the 59 (and 101 existing twins) all still owe regenerated art under that ruling.

## Method and limits
- Scripts: `/home/mandrake/.seat-tmp/FOUNDRY/s/*.py` (scratch, not committed). Donor counts via `xml.etree` over `1.6/Defs`; roster rows via `ET` over all 2753 `.xml` under `src/`, 0 parse failures; sanity probes: bare-donor-row count (0) cross-checked by the guarded count finding 86; `ModsConfig.xml` parsed, not grepped.
- Offline def dump not consulted: the donor's source XML is on disk and is the authority; the dump would add nothing and may be stale.
- Twin matching is by normalised defName (prefix stripped) and requires `<race>` on our ThingDef; label-only matching found 0 extra. "Wired" means a roster `<wildAnimals>` child naming the twin; twins used elsewhere (factions, other spawn paths) are not counted.
