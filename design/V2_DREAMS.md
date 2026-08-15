# V2 — dreams and hopes

**An append-only register of deferred work. It is not a queue.** Nothing in here is
scheduled, assigned, or owed. No seat picks work from this file, and no board derives
a state from it.

**Append freely. Every seat — DECIDE, BUILD, CHECK, REP — and the owner may append
here at any time, without permission, without routing it through DECIDE, and without
writing a queue item asking for it.** No format, no approval, no field contract: a
heading and whatever you were thinking is enough. New entries go at the END.

If something is a good idea and it is not v1, it belongs here and nowhere else — not
in `infrastructure/state/queue/`, not in a TODO box, not tagged `[v2]` in a working
doc. The point is to offload it: write it down, let it go, get back to the v1 work.

**It is drained only when v1 has shipped and someone opens it deliberately.**

Items keep their original queue IDs (`B*`, `C*`, `D*`) so older citations still
resolve. The `row:` and `state:` fields were queue plumbing and were dropped on the
way in; everything else is verbatim.

_Created 2026-08-14 by draining `queue/BUILD.md`, `queue/CHECK.md`, `queue/DECIDE.md`
and the whole of `infrastructure/state/TODO_v2.md` (which was deleted)._

---

**BUILD** — deferred build work, drained from `infrastructure/state/queue/BUILD.md`

## B3 S9 — scrapfields `minSpacing` 4 -> 1
spec:     `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches --apply`. Ships `Jawa_Patches/Defs/MapGeneration/JawaScrapfields.xml` with `minSpacing` 4 -> 1 (`8a7a5ee`), plus `JawaGroundHulk.xml`. Root cause: `minSpacing` equalled the engine's hardcoded `ClusterRadius` of 4, so each cluster self-exhausted after ~4 chunks, `TryFindScatterCell` returned an invalid cell and `GenStep_Scatterer::Generate` `ret`s inside its loop, discarding ~46 of 50 chunks. Both are map-generation defs: they need a cold load AND a map generated after it. Never run `--apply` bare.
verify:   `-> VERIFIED in sync`; deployed `JawaScrapfields.xml` carries `minSpacing 1`. `--mod Jawa_Patches` also re-verifies every other file in that mod.
criteria: see CHECK C3 — 44–56 chunks in 4–6 clumps on a map generated after this deploy.

## B4 Armoury patches — HELD on provenance
spec:     `src/Jawa/Jawa_Armoury/Patches/Armoury_MeleePower.xml` and `Armoury_RangedDamage.xml`. Swept into `81939e1` (subject: genome tooling), never reviewed, no provenance banner. Re-run the generator; generators anchor through `observed/2026-08-13/inventory/patch_ledger.json` and print a banner via `src/RimMandrake/Utils/patch_provenance.py`. Also carries 8 double-match `Replace`s.
verify:   provenance banner shows no `unknown` anchors — `unknown` means STOP. Scoped `validate_patch.py --defs` clean; the 8 double-match `Replace`s resolved.
criteria: EMPTY

## B5 MegafaunaYield.xml — 3 double-match Replaces
spec:     3 `PatchOperationReplace` ops each match two nodes (same value written to both). Cosmetic; a player cannot see it.
verify:   scoped `validate_patch.py --defs` sweep reports 0 double-match `Replace` in `MegafaunaYield.xml`.
criteria: EMPTY

## B7 Repair the approved ideoligion .rid
spec:     `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Ideos\The Salvation (CREATE).rid`. Two defects: `AM_Fertility` was dropped while two precepts still require it; `VME_Nomad` is IN and must come out — its own description says non-vanilla movement systems will not register and it inflicts −50 mood at 60 days. `Nomadic_Preferred` is a PRECEPT (`requiredMemes` empty), zero slot cost, already in the file, and does the job: `GravshipUtility::ArriveNewMap` unconditionally stamps `IdeoManager.lastResettledTick`, the only field its ThoughtWorker reads. (`ArriveExistingMap` does NOT write it.) Rebuild with `python3 src/RimMandrake/Utils/build_salvation_rid.py --check|--write`; it never rewrites the source. Do not delete the owner's original `The Salvation.rid` beside it. Do not "fix" `AM_Structure_Scavenger`'s `deityCount 0` by swapping the structure — no installed structure meme allows more than 4, which is why the nine gods live in the description.
verify:   `--check` passes: IDs unique, no dangling `Precept_<ID>`, re-run byte-identical; no `VME_Nomad`; `AM_Fertility` present or its two dependent precepts dropped.
criteria: the ideo browser loads it with 0 rejected precepts; the description renders as scripture, not a wall; the six added precepts show a position (barracks · lighting · combat in darkness · combat prowess · weapons noble *Ranged* / despised *Melee* · apparel desire); one relic, "The Founding Ion Blaster".

## B9 Junkers lose `permanentEnemy` — owner ruling
spec:     `faction_roster_v2.md:1992` (`Permanent enemy | Yes`) and `:2309` (permanently hostile to everyone) -> hostile-but-bribable scavengers. Pillar 5 at `:105` stands as written: the Galactic Empire alone is the permanent enemy.
verify:   no `Permanent enemy | Yes` row survives outside the Galactic Empire.
criteria: EMPTY

## B10 Delete the Imperial Droid Army; the Galactic Empire is the pursuer
spec:     Amend `faction_roster_v2.md` and `gravship_pursuer_mechanism.md`. Two Empire factions only — the planetside aristocratic Empire and the Galactic Empire — and it is the Galactic Empire that pursues the ship: stormtroopers, combat droids, lightsaber-bearing Sith. There is no independent Imperial Droid Army.
verify:   no Imperial Droid Army reference survives in either file.
criteria: EMPTY

## B11 Homestead ideology structure -> `Structure_TheistAbstract`
spec:     `faction_roster_v2.md` :712 / :726 read "Abstract theist or ideological" — literally both. Decided: `Structure_TheistAbstract`, deity *the Withdrawn*, gender `None`. Reason: the covenant is addressed to something, and the ideological structure has `deityCount 0`.
verify:   the either/or line is gone and `deityPresets` is authorable.
criteria: EMPTY

## B12 Homestead raid frequency — state the refusal as doctrine
spec:     `faction_roster_v2.md:300` says "Homestead / Aquifer / Wookiee never raid (Rw 0)"; `:675` says "Raid frequency | Very low". Fix: put `VME_Raiding_Abhorrent` (Vanilla Ideology Expanded, active) on the Homestead and the Deepwater Compact, set the raid curve low, and let the precept carry the reason.
verify:   `python3 src/RimMandrake/Utils/validate_ideoligion.py <xml>` VALID; the two roster lines agree.
criteria: EMPTY

## B13 `VME_SecularSpirituality` renders nothing
spec:     The Deepwater Compact's only style category is `VME_SecularSpirituality`, which has `thingDefStyles: []` — invisible by construction. Swap for a `StyleCategoryDef` that actually ships styles. Read the resolved DUMP, never the vanilla XML: Anomaly writes `<li>Horaxian</li>` but the dump says `AM_Horaxian` because Alpha Memes `PatchOperationReplace`s the whole list.
verify:   the chosen category has non-empty `thingDefStyles` in the live dump; `validate_ideoligion.py` VALID.
criteria: EMPTY

## B14 Build the eleven `FactionDef` ideoligion blocks — entries 1 and 2 first
spec:     `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`. Pattern is the Horax cult, `Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml`: `fixedIdeo` · `ideoName` · `ideoDescription` · `forcedMemes` (structure first, complete set) · `requiredPreceptsOnly` · `deityPresets` · `disallowedPrecepts` · `styles` — NOT the Empire's `requiredMemes` + `structureMemeWeights`. Entry 1 (Galactic Empire — The Rising Order) lands on vanilla `Empire` per `V1_SCOPE.md:84`, replacing that family. Entries 1 (two deities), 2 (one) and 3 (one) need `deityPresets`; the corrected `deityCount` table is at the foot of the spec. Take `ideoName`, `ideoDescription` and every `deityPresets` name/type VERBATIM — they are the only text the engine renders. Never set `hiddenIdeo`. Section 12 (Jawa) is a deliberate empty slot — the owner is building it. Legal vocabulary: `design\Jawa\worldbuilding\data\ideology_palette.md` (136 memes, 685 precepts, 41 styles, 92 ritual patterns). Three engine constraints: charity has no negative precept · `PreferredXenotypes` cannot be aimed at a xenotype from XML · `Apostasy_Abhorrent` hard-conflicts with the `Guilty` meme. Meme ceiling is a COUNT (`MemeCountRangeAbsolute` 1–4 normal memes), not an impact budget — never pass `--impact-budget`.
verify:   `python3 src/RimMandrake/Utils/validate_ideoligion.py <xml>` VALID, then eyeball EVERY `<li>` for its `MayRequire` by hand — the validator does NOT check `MayRequire` (`def/needs-mayrequire` is only an INFO), and an unwrapped defName from a disabled mod is a silent no-op. packageIds: `VME_`/`VFEA_` -> `vanillaexpanded.vmemese`, `AM_` -> `sarg.alphamemes`, plus `VQE_`, `GR_`, `llunak.moreprecepts`, the Ludeon DLC ids. VALID is not GOOD — 4 inert precepts still WARN across the set.
criteria: read the eleven back with `jawa/ideo_of` and diff against the spec.

## B15 Tile augmentation catalogue `[v2]`
spec:     `design/Jawa/worldbuilding/tile_augmentation_catalogue.md` — 31 rows, 19 v1-capable. Pure XML: `LandmarkDef` + `TileMutatorDef`. Cheapest first: F1 (zero XML), then C3, then B1. §5: never cull a spawned def.
verify:   `validate_patch.py --defs` 0 errors on the new defs.
criteria: the augmentation appears on the intended tile at worldgen.

## B16 Restraining bolts `[v2]`
spec:     `design/Jawa/worldbuilding/restraining_bolt_technical.md` (`8353622`). Verdict: CAP the goodwill ceiling — one XML def plus ~40 lines of C#, no Harmony. Lands with the Free Droid Enclaves, whose `FactionDef` is unbuilt.
verify:   assembly builds; the def validates.
criteria: the droid faction's goodwill cannot exceed the cap in play.

## B17 Re-cast the rebel gear `[v2]`
spec:     The Rebel Alliance faction is suppressed and confirmed absent, but its gear survives and circulates — `OuterRim_A280Blaster` appears 5x in the world and nobody wears it. Add the gear to Junkers / Homestead `pawnGroupMakers`.
verify:   `validate_patch.py --defs`; the xpath matches the intended `pawnGroupMakers`.
criteria: a Junker or Homestead raider spawns carrying `OuterRim_A280Blaster`.

## B18 Merge water rulings W3–W7 into the twelve dossiers `[v2]`
spec:     W3–W7 live only in `water_doctrine.md`. Junker doctrine still assumes universal thirst.
verify:   no dossier contradicts `water_doctrine.md`.
criteria: EMPTY

## B19 `design/Jawa/droid_ruling.md` states a mechanism that is not in the defs
spec:     JDS droids do not explode — they are force-killed on downing and their wrecks are repairable. The ruling holds; the stated reason is wrong. Rewrite the mechanism.
verify:   the stated mechanism matches the defs.
criteria: EMPTY

## B20 Faction roster Stages 3 and 4 `[v2]`
spec:     The other 11 dossiers, `pawnGroupMakers`, memes, ideoligions, the relations matrix, and the licensing gate. Stages 1 and 2 are closed.
verify:   EMPTY
criteria: EMPTY

## B24 Armoury mid-tier reference `[v2]`
spec:     Echani Foil (AP **1.33**) vs Excellent durasteel heavy armour (Sharp **1.05**) -> effective armour **zero**; the lightsaber got only **27.5** through the same suit. Add a Yautja blade (AP **0.60**) to land a tier between them. If the Yautja mod is cut, re-anchor on another mid-tier weapon.
verify:   the three AP values read out of the live def dump.
criteria: EMPTY

## B28 `jawa/import_gravship` `[v2]`
spec:     Mid-game layout import. `ShipSketchBuilder.BuildFromLayout` is `public static` and pure (no `Find.`/`Current.`/`Map`), and a `Sketch` spawns onto a live map => one method call, not a mod fork; the licence permits it. Floors will NOT come with it — terrain is re-applied by a Harmony patch that does not run for a mid-game Sketch spawn; replay the cells through `jawa/set_terrain_batch` (`src/RimMandrake/Utils/gravship_layout.py` emits them). Build needs the game DOWN.
verify:   builds with `--gm`; the tool name appears in the census.
criteria: a layout XML imports onto a live map and the terrain replay lands. Closes the design loop: author XML -> import -> look -> iterate, with no worldgen and no 25-min load per turn.

## B29 Space Tower `[v2]` — enable and wire the retaliation
spec:     `hailuan.spacetower` is the only absent piece: `hailuan.customquestframework` is already active at 108 of 575 and `hailuan.customquestframeworkai` at 431. Owner's frame: the towers are Imperial infrastructure, the Hutts pay you to cut them, the Empire's retaliation is the cost. Take the Empire-goodwill patch (`ensureHostile: false`, cumulative not one-shot) as PRE-WIRING, not as the cost — the real cost is raid pressure. Design: `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\orbital_towers_and_the_sky_ladder.md`. Two riders: the mod ships NO licence file (default all-rights-reserved — we may subscribe and patch, we may not ship its maps); `rootSelectionWeight` is declared TWICE in `ST_Quest_SpaceTower.xml` (`0.25` then `0.1`), last wins, effective **0.1**, and that is the dial to tune.
verify:   patch validates; `rootSelectionWeight` declared once.
criteria: the quest offers to a gravship colony — `autoAccept=True` on `ST_Quest_SpaceTower` suppresses the space gate entirely and its `everAcceptableInSpace=False` is inert.

## B30 Swap the species-named hood in the ideoligion
spec:     The apparel-desire precept names `guy762_JawaHood`, which is literally species-named. Swap for `OuterRim_DesertHood`. One word.
verify:   `validate_ideoligion.py` VALID; `OuterRim_DesertHood` resolves in the live dump.
criteria: EMPTY

## B31 `factionlessGenerationWeight` patch `[v2]`
spec:     The three Star Wars packs are a STACK, not alternatives: BTD REMIX defines ZERO genes of its own — 196 of its gene refs point at SW Xenotypes, 41 at Outer Rim GD, so uninstalling either breaks it. All three generate, so a wanderer can arrive as the wrong Twi'lek. Fix is a `factionlessGenerationWeight` patch, not an uninstall.
verify:   `validate_patch.py --defs`; the xpath matches the intended xenotypes.
criteria: no wanderer arrives as a non-campaign Twi'lek xenotype.

## B32 Read the shipped `OuterRim_GalacticEmpire` FactionDef
spec:     `src/Jawa/Jawa_Patches/About/About.xml:36` records that the shipped def has `permanentEnemy false` while the faction dossier says permanent enemy YES — that single field plausibly explains `goodwill 0` AND `canFireNow:false`. Already checked: the live faction list (`hostile:false`, `goodwill:0`, name "Imperial Desert Directorate") and the About.xml note. NOT checked: the shipped `FactionDef` itself — a workshop-tree grep timed out at 120 s twice, so scope it.
verify:   quote `permanentEnemy` and the hostility fields from the shipped `FactionDef` file, with path and line.
criteria: EMPTY

## B33 Malformed closing tag in an active workshop mod loses two precepts
spec:     `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2896845138\Defs\Precepts.xml` line 210 reads `<defName>GarryFlowers_Slave_Relation_Vanilla<defName>` — no slash. The live dump shows `GarryFlowers_Slave_Relations` carrying 2 positions where the XML defines 4; `_Equality` and `_Vanilla` are lost with no error. Checked clean: nothing in the religions spec or the Unearned spec depends on them, and the campaign's slave-romance love-gate uses `GarryFlowers_Slave_attendance`, which is unaffected.
verify:   after the fix the live dump shows 4 positions.
criteria: EMPTY

## B38 Attribution rule: a loose slag chunk on a quicktest map is ours
spec:     Across the live 585-mod set `Jawa_ScatterScrapfields` is the ONLY GenStepDef that scatters `ChunkSlagSteel`, and it plus `Jawa_StampGroundHulk` are the only non-shipped steps in `Base_Player`'s 46-step list. Every other def-level route to a loose chunk lands on a site/quest/orbital map, NOT an ordinary colony map: `OpportunitySite_Satellite` is an Odyssey orbital platform (`terrainDef OrbitalPlatform`, `LayoutWorker_OrbitalPlatform`); the 42 KCSG `StructureLayoutDef`s carrying slag (Ancient mining industry 4, VQE Cryptoforge 18, VQE The Generator 16, Alpha Genes 1, Vanilla Genetics Expanded 3) are reached only through `SitePartDef`s — `AbandonedPlasteelMineSite_Site`, `VQE_Quest1Site`, `AG_AbandonedBiotechLab`, `GR_AbandonedLab`; `CustomMapDataDef` `AM_Bunker_C`/`AM_Street_A` only through `AM_StreetSite`; `SymbolDef ChunkSlagSteel` is a KCSG auto-generated symbol with no trigger of its own. ONE exception, missed by a string census because it is indirect: `AB_DerelictBioLab` (Alpha Biomes `TileMutatorDef`, worker `VEF.Maps.TileMutatorWorker_GenericKCSGSpawner`) spawns one of thirteen `AG_AbandonedBiotechLab*` layouts, of which `Delta` carries slag — `chanceOnNonLandmarkTile 0.005`, `maxHilliness Flat`, no biome and no temperature gate, so it CAN fire on a plain desert colony tile. RULE: a `ChunkSlagSteel` on a quicktest map whose tile mutators contain none of `AncientGarrison`, `AncientWarehouse`, `AB_DerelictBioLab` is OURS. Residual, stated not hidden: vanilla `Assembly-CSharp` contains the string `ChunkSlagSteel` (the `ThingDefOf` field), so a C#-side genstep cannot be enumerated offline — the density criterion below is what covers it.
verify:   offline, over `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs`: `GenStepDef.json` contains exactly one def whose JSON holds `ChunkSlagSteel` and it is `Jawa_ScatterScrapfields`; and the only `TileMutatorDef`s reaching slag — directly or through `modExtensions/KCSGStructuresToSpawn` — are `AncientGarrison`, `AncientWarehouse`, `AB_DerelictBioLab`. Re-run both after any change to the active mod list.
criteria: on a desert quicktest, `jawa/list_things` for `ChunkSlagSteel` on a 250x250 map. PASS = ~440-560 chunks in ~44-56 clusters of 10 with `Filth_MachineBits` under them (`countPer10kCellsRange 7-9`, `clusterSize 10`, 6.25 units of 10k cells). FAIL = under ~30 chunks, or every chunk inside one walled structure — that is the Alpha Biomes lab, so read the tile's mutator list before blaming our step.

---

**CHECK** — deferred observations and measurements, drained from `infrastructure/state/queue/CHECK.md`

## C2 L3 — the Galactic Empire raid, and read the faction back
spec:     Chain: game DOWN -> deploy BUILD B1 (`--gm`, 30 tools) -> up -> `jawa/set_faction_relation` make `OuterRim_GalacticEmpire` hostile -> `jawa/fire_incident incidentDef=RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true` (abort on `canFireNow:false`) -> fire for real -> screenshot. PASS `points` EXPLICITLY: `points<=0` takes the storyteller default, which on a fresh quicktest is tens of points — one trivial attacker cannot answer whether the Empire reads as an antagonist.
verify:   EMPTY
criteria: read the `faction` field in the REPLY, never the one you sent — `IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps the passed faction only if non-null AND `HostileTo(Faction.OfPlayer)` AND (`!deactivated` OR `parms.forced`); otherwise IL_0059 passes `ldflda IncidentParms::faction` BY REFERENCE into `TryGetRandomFactionForCombatPawnGroupWeighted`, which overwrites it with a random weighted faction and still reports `success:true`. The tool reports `parms.faction` after the worker ran (`JawaBenchTerrainTools.cs:3588`). Then: does the antagonist read as the antagonist on screen.

## C3 v1 row 4 — the scrapfields count
spec:     After BUILD B3 deploys, generate a fresh map (a 90 s quicktest counts; `Jawa_ScatterScrapfields` is a `GenStepDef` at order 960 hooking `Base_Player` genSteps, so it is not biome-gated), then take a FULL-MAP `listerThings` count of `ChunkSlagSteel` — no sampling — plus `TileInfo.Mutators` and the map size. NAME THE MAP. A GenStep runs at map generation and never again, so a map's count dates the def that BUILT it. The old "11 measured" was never a measurement: 9 rects of 30x30 = 8,100 cells (~13% of the map) holding 1 chunk each on two maps, extrapolated by /0.13; where the 9 rects sat is recorded nowhere. Full audits: `observed/2026-08-14_O15_scrapfields_offline.md`, `observed/2026-08-14_row4_live.md:97-101`.
verify:   EMPTY
criteria: **44–56 chunks in 4–6 clumps** on a map generated after B3. The 75–125 band was never measured — it omitted `GetPlacementFactor`, the product of `junkDensityFactor` over the tile's mutators, and `Dunes` is one of five live mutators whose factor is **ZERO**. On any older save the verdict is "not measurable here", NEVER "44–56 missed". Look before any destroy — the last map's evidence died in a 43,288-thing wipe.

## C4 Are those chunks ours — attribute the `GenStep_ScatterThings` NRE
spec:     `Player.log:9022` (2026-08-14 ~15:00): `Error in GenStep: NullReferenceException at Verse.GenStep_ScatterThings.ScatterAt [0x0013f]`, called from `GenStep_ScatterThings.Generate [0x0010d]`, with a `BiomesCore.Patches.IslandGeysers` prefix on the same method. Exactly ONE occurrence in four generated worlds, and NOT on the 13:54 quicktest map where 4 chunks were counted (that map's generation sits before log line 6830; this throw is between lines 7975 and 9040). `Error in GenStep` names no defName and both `Jawa_ScatterScrapfields` and Biomes Core's scatterers are `GenStep_ScatterThings`; it is caught per-step, so generation continued — not a hang.
verify:   EMPTY
criteria: grep the log of the C3 quicktests. Vanishes with the `minSpacing` fix => it was ours. Recurs on a map where scrapfields now places ~50 => it is Biomes Core's. Free attribution riding already-scheduled work.

## C5 The two xenotype picker icons
spec:     Two unresolvable `iconPath`s: `Jawa_Head_Plain` -> `UI/Icons/Genes/Gene_Hair`, and `Jawa_Xeno_Gamorrean` -> `UI/Icons/Xenotypes/Pigskin`. Not settleable offline — vanilla textures live in asset bundles. Open the xenotype picker and look at both.
verify:   EMPTY
criteria: a pink or blank square is the defect; both drawing closes this permanently.

## C6 O12 — the 30-second droid NRE confirmation
spec:     Spawn `KotORDroidGood_3C` twice on any map. Chain under test: `Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets `isOrganic=false` on `ABF_FleshType_Synstruct_Base` -> `RaceProperties.IsFlesh => FleshType.isOrganic` -> `PawnComponentsUtility.CreateInitialComponents` builds `Pawn_RelationsTracker` only `if (pawn.RaceProps.IsFlesh)` -> HAR derefs it unguarded.
verify:   EMPTY
criteria: the SECOND same-def droid must NRE (`AlienRace.HarmonyPatches.GenerationChanceGenderless`, `HarmonyPatches.cs:2669`) — the throw is inside the weight selector iterating pawns that ALREADY EXIST, so the pawn with the missing tracker is `current`, the previously-spawned droid. If it does NOT throw, the chain is wrong and all three fix routes are moot.

## C7 Gravship radius — `get_def GravFieldExtender`
spec:     Read the live `GravFieldExtender` (and the engine radius) with `jawa/get_def`. Bigger Gravships is set to 34 in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3522759531_GravshipSizeSettings.xml`, and `GravshipSize.dll` stamps radii during implied-def generation, AFTER all XML patching. On disk the def reads 16.9/12.9 and is MEANT to disagree. Live state: `BG_gravEngineSupport` is **4500** (was 632.79541; compiled default 500.0) — any capacity reading starts from 4500. Setting it live needs `rimworld/update_mod_settings` PLUS the mod's own "Apply Settings Now!" button; the write alone does not reach the defs.
verify:   EMPTY
criteria: the live def carries the expanded radii. Until it does, DO NOT BUILD A SHIP — one built now will not lift and nothing logs why. Confirmatory, not load-bearing: do not spend a session's first call on it.

## C8 v1 row 4 — dune seas
spec:     Read the live `BiomeDef`. Do NOT eyeball it: a density change 0.65 -> 0.55 is unjudgeable without a control.
verify:   EMPTY
criteria: `terrainPatchMakers` read **0.55 / 0.50** on the live def.

## C9 The ground hulk and a casket bank
spec:     `00a1398` — one wide shot plus one casket bank. 619 of 1,200 cells; 0 overlaps, 0 out-of-bounds, 0 props off-deck.
verify:   EMPTY
criteria: does the broken deck read as a wreck, and do three banks read as a hold. Nobody has ever seen an `AncientCryptosleepCasket` — vanilla and DLC art is in AssetBundles, so 297 wreck defs cannot be rendered offline; defs, sizes and yields are proven, the look is not. `ShipChunk_Mech` needs `Light`, not `Heavy`; `BrokenSubstructure` has no `Inherit="False"` so it APPENDS to `FloorBase` — either layer satisfies the deck. Missing props means prefab placement, blocked cells or `spotMustBeStandable`; do not report "deck present, props absent".

## C10 The art-observation batch — Cerean and Saurid
spec:     Runnable on ANY live map; no fresh map, no new capability. **CereanManeFix**: spawn pawnkind `OuterRim_Cerean` (forces the xenotype, weight 999), then SET hair `OuterRim_CereanMane` (a fresh Cerean rolls it ~1 in 5 — set it, do not hope), face **SOUTH**. **SauridFrillFix**: spawn pawnkind `VRESaurids_Villager_Saurid`, then SET hair `VRESaurids_Littlefoot` (`texPath Pawn/CenterFrill/CenterFrill8`), face **NORTH** — the donor ships `CenterFrill8_north-.png` with a trailing hyphen while `CenterFrill7_north.png` beside it is named correctly, and north is the ONLY broken rotation. Tools: `jawa/spawn_pawn`, `jawa/set_pawn_style`, `jawa/set_pawn_rotation`. A pawnkind spawn ALONE tests neither — both are HairDef `texPath`s, not pawnkind art, so the style has to be SET or you photograph a default and call it passed.
verify:   EMPTY
criteria: the hair renders correctly in the named facing. OBSERVATION ONLY — the owner's stop on art fixing stands; looking is not fixing.

## C11 ToolBeltFix
spec:     `VAEA_Apparel_ToolBelt` is spawned by NO PawnKindDef — zero hits across the workshop tree, `Mods/` and `Data/` in `apparelRequired`, `specificApparelRequirements` or any fixed list, and its only tag `VAEA_Utility_Industrial` appears in no pawnkind, so there is no random path either. Every other reference is loot. Needs dev-spawn plus a FORCE-EQUIP tool, which does not exist yet. Hold for that tool, not for a load.
verify:   EMPTY
criteria: face **WEST** (`ToolBelt_west.png` is 753 bytes against `ToolBelt_east.png` at 16,945). `renderUtilityAsPack` is true so it draws in the pack layer — check from behind as well as straight west.

## C12 `NoPathToPilotConsole` — launch gate
spec:     The export holds ZERO `PilotConsole`, so there is nothing to path to: PLACE a console first (defName `PilotConsole`, `Odyssey/Defs/ThingDefs_Buildings/Buildings_Gravship.xml`; `load_session.py` looks it up itself). Then `jawa/order_pawn pawnId=colonists targetId=<consoleThingId> waitTicks=0 unpause=false`; `jawa/list_things` produces the ThingID for a non-pawn. `pathEndMode` must be `interactioncell` (the default when `targetId` is set). Needs no movement.
verify:   EMPTY
criteria: the vanilla gate is `PawnCanFillRole` -> `ReachabilityUtility.CanReach(pawn, console, PathEndMode.InteractionCell, ...)` — a pawn can reach the cell BESIDE a console and still fail, so TARGET THE THING. Doors are in the export; a door is not a path.

## C13 Thruster placement — a confirmation with a committed prediction
spec:     Remove hull at (45,132) and place a `SmallThruster` at (45,131) rot 2; control at (45,129) with the hull intact. Nine candidate sites at x41–49, z131/132; the aft strip (x,133) is off-deck.
verify:   EMPTY
criteria: (45,131) reads ACTIVE with no warning; the control reads `WarningThrusterInside`. Read it with `jawa/inspect_string` (`Thing.GetInspectString()`) — `get_cell_info` returns a className and stops.

## C14 The sealed-room thruster test (CREATE's L8)
spec:     Sealed roofed room with a thruster inside -> predict INACTIVE. Thruster in the wall line with open sky aft -> predict ACTIVE.
verify:   EMPTY
criteria: send CREATE the RAW `jawa/inspect_string` lines, not a verdict — the whole roof derivation hangs off which sentence fires.

## C19 Live terrain edit — put the salt back in the dry lake bed
spec:     Geological Landforms hard-codes `SoftSand` on its dry-lake landform and the mod-side fix means editing a serialised NodeCanvas, so fix it LIVE on arrival. Target defName, verified: `Jawa_SaltCrust`, `src/Jawa/Jawa_Patches/Defs/TerrainDefs/JawaSaltCrust.xml:100`. Bound by BOTH a rect AND a source-terrain match, never terrain alone — a map-wide SoftSand->salt repaint erases the desert. Same session as worldgen, after rows 2 and 7. Not a blocker.
verify:   EMPTY
criteria: the deliverable is the CAPABILITY, not the pan — (a) can the bridge detect or be told a landform footprint, (b) set terrain over that region, (c) does it survive save/reload. First live evidence for tile-augmentation-on-approach, which has none (`design/Jawa/worldbuilding/tile_augmentation_catalogue.md`).

## C20 Re-shoot the twelve art screenshots
spec:     The 12 `NEEDS EYES` rows in `observed/2026-08-14_load_session.md` are NON-EVIDENCE: the Debug log window covers the CENTRE of the screen, which is exactly where `look()` puts the subject, and in `p5_004.png` and `p13_012.png` the subject is not in frame at all. `jawa/clear_ui` fixes it forward — closes every `Window_Dev`, drops the selection — and `rimbench.core.look()`/`.frame()` call it automatically. Closing the log by hand does not hold: auto-open-on-error.
verify:   EMPTY
criteria: twelve screenshots with the subject in frame and no dev window over it.

## C22 The ten art-fix mods — one spawn, one look each
spec:     Eight deployed and enabled; the two newest are `mandrake.phytokinbarkheadfix` @562 (donor @388) and `mandrake.kotorbandoliernorthfix` @**579** — deliberately outside the 556–563 art-fix slot because its donor `guy762.mm.kotorcore` sits at 572 and ships loose art. A loose PNG beats an AssetBundle regardless of order, but between two LOOSE files order decides, so a loose-art donor must be in `loadAfter` or the fix is invisible with no log line. Routes and click paths: `infrastructure/state/CREATE_TEST_PLAN.md`.
verify:   EMPTY
criteria: each fix renders in the facing it targets. Judge at DISPLAY size and render the tint — art can be correct at source and broken at render. Observation only.

## C23 Run `CREATE_TEST_PLAN.md` with its nine pre-flight corrections
spec:     `D:\Luke\dev\Rimworld\infrastructure\state\CREATE_TEST_PLAN.md` — eight art-fix mods, v1 row 3's `Jawa_ClaimRumour`, row 4's terrain plus the 619-cell ground hulk. Part 3 needs a FRESHLY GENERATED Desert / ExtremeDesert / AridShrubland map; a quicktest counts. Nine pre-flight corrections live in `infrastructure/state/AGENT_BRIDGE_state.md`, DELETED in `edaa1bb` — recover with `git show edaa1bb^:infrastructure/state/AGENT_BRIDGE_state.md` and read them before typing at a live console: two are wrong parameters, one is a diagnostic string with no basis, and `ToolBelt` does not exist under that name. Also: `jawa/spawn_thing` DOES NOT EXIST — the call is vanilla `rimworld/spawn_thing`, or `jawa/spawn_batch` for more than one.
verify:   EMPTY
criteria: a screenshot is the evidence, a def query is not — every failure mode in the plan is silent.

## C24 Does Faction Customizer's settings dialog persist across worlds
spec:     One minute at the keyboard.
verify:   EMPTY
criteria: persists or does not — the roster's goodwill-cap mechanism depends on the answer.

## C25 `jawa/ideo_of` — verify the eleven, and measure whether NPC religion surfaces
spec:     `jawa/ideo_of` reads `Find.IdeoManager.IdeosListForReading` — an Ideo is a RUNTIME object, not a Def, so no def read can reach it. Believer counts split **colonists / otherOnMap / worldPawns**; it also exposes `PreceptDef.enabledForNPCFactions`. `ideologyActive:false` is a loud failure, never a count of zero.
verify:   EMPTY
criteria: diff the eleven built ideoligions against `faction_religions_spec.md`. Separately, `otherOnMap` measures how often NPC religion surfaces in play — the whole eleven-religion design is disciplined around "it rarely surfaces", which has NEVER been measured. A total alone would let the claim survive on the player colony's own believers. If it returns ~0, say so in the doc and stop treating the eleven as load-bearing.

## C26 `jawa/biome_probe` — the 29 biome removals
spec:     `jawa/biome_probe find=<defName>` audits a removal across every biome in one call and needs NO map (`AllWildAnimals`/`AllWildPlants` build their own cache lazily, IL_0006). 28 of the 29 removals are UNEVIDENCED: `Scalars()` (`JawaBenchTerrainTools.cs:4111`) reads public instance FIELDS only, while `BiomeDef` keeps `wildAnimals`, `coastalWildAnimals`, `pollutionWildAnimals`, `diseases` and `allowedPackAnimals` PRIVATE and exposes `AllWildAnimals`/`AllWildPlants` as PROPERTIES — every other tool on this bridge is blind to them. The one removal ever looked at (Coastal dunes) was confirmed in two seconds. Record results at `design\Jawa\worldbuilding\cherrypick_inbox.md`.
verify:   EMPTY
criteria: each removal must report `spawning` / `zeroed` / `absent` against the DECLARED records — present-at-commonality-0 and absent are DIFFERENT defects, and the engine's own resolved lists drop a zeroed record exactly like a deleted one (`get_AllWildAnimals` yields a kind only if `CommonalityOfAnimal` or `…PollutionAnimal` or `…CoastalAnimal` > 0, IL_0055/0063/0071; `get_AllWildPlants` filters `CommonalityOfPlant > 0`, IL_0038).

## C27 A coastal forsaken-crags tile
spec:     Roll one. It can roll Archipelago today, giving a permanently dark mostly-ocean map with zero new code.
verify:   EMPTY
criteria: does it read — this decides the deep.

## C28 Photograph the 25 vanilla mechs whose art is bundle-locked
spec:     Art is on disk for 55 of 80 (`data/mech_inventory.json`); the remaining 25 vanilla mechs are inside AssetBundles and cannot be rendered offline.
verify:   EMPTY
criteria: images for all 25 — unblocks the owner's mech review sheet, which is otherwise complete (axes committed in `data/mech_control_axes.md`).

## C29 Does `CharityRefused_Beggars` record without a `Charity_*` precept
spec:     ~2 min. The refusal hook is legal and measured: `CharityRefused_Beggars` fires when beggars leave empty-handed, and arresting them raises `CharityRefused_Beggars_Betrayed` (IL: `AnySignal(beggars.Killed, beggars.Arrested)`). Spec: `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\precept_the_unearned.md`. A `FactionDef` has no precept field; only a meme's `requireOne` forces one.
verify:   EMPTY
criteria: does the event record at all for a colony holding NO `Charity_*` precept. Blocks CREATE.

## C30 RimTunes tagging session `[v2]`
spec:     RimTunes has replaced the vanilla music system, dynamic mode is on (`enableDMS: True`), and `Config/RimTunes/` is EMPTY — it is scoring the game right now with nothing of ours in it. Answer two questions FIRST, both of which change how everything gets tagged: (1) what are the `Events` tags — the category exists in the language keys but the names are in neither the files nor the assembly; icons include `explosion.png` and `dove.png`; (2) do time-range tags mean clock time or position within a song — the dialog says "Play only during this part of the song" while the tag description says "Plays between {range}". Then confirm `SW_Sandstorm` and `SW_DrySandstorm` appear as weather tags (the assembly has `CreateBiomeTags` and `CreateWeatherTags`) — if they do we can score our own weather with no XML at all. Then tag: 102 songs auto-discovered; vanilla's 6 desert-appropriate relax tracks -> Require the desert biomes; the ~6 usable `Tense` tracks -> Require `Tense` (only 11 of 102 are tense and 5 of those are Caverns tracks locked to the fungal forest, so the real combat pool on a desert map is about six). Then back up `Config/RimTunes/` and `Config/Mod_3399705740_RimTunesMod.xml` to `deployed/config/` — hand tagging is otherwise unrecoverable. Context: `design/RimMandrake/music_protocol.md`.
verify:   EMPTY
criteria: both questions answered from the live dialog; the two weather tags present or absent.

## C32 Scrapfields `minSpacing 1` is deployed
spec:     From BUILD B3. Deployed `JawaScrapfields.xml` carries `minSpacing 1`;
          `Jawa_Patches` reports `-> VERIFIED in sync` (46 files). Both are map-generation
          defs: they need a cold load AND a map generated after it.
criteria: folded into C3 — 44–56 chunks in 4–6 clumps on a map generated after this deploy.

---

**DECIDE** — deferred decisions, drained from `infrastructure/state/queue/DECIDE.md`

## D-R4 Row 4 — scrapfields, and it may not be a content bug at all
spec:     2 of 3 terrain overrides are SEEN (dune seas, salt pans at 144 cells).
          Scrapfields is the open one: a full-map count returned 4 `ChunkSlagSteel`
          on the 13:54 quicktest against a band of 44-56 in 4-6 clumps.
          🔴 THE PREREQUISITE NOBODY HAS MET: it is not established that those 4
          chunks are OURS. Vanilla and other mods scatter `ChunkSlagSteel` too. If
          they are foreign, our genStep placed ZERO and every hypothesis so far is
          aimed at the wrong target. Settle that FIRST — it is offline work.
          Then, in order: `warnOnFail=true` on the scatter defs so a failed
          placement is logged at all; `minSpacing 4 -> 1`; one fresh quicktest per
          iteration at ~90 s.
          ⚠️ A GenStep runs at MAP GENERATION and never again. A count only means
          anything on a map generated AFTER the def it is testing. Naming the map
          is part of the result.
verify:   —
criteria: —

## D17 The droid relations NRE — which of three routes (owner decision #12)
spec:     `src/Jawa/Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets `isOrganic=false` on the KotOR flesh type `ABF_FleshType_Synstruct_Base` => `IsFlesh` false => no `Pawn_RelationsTracker` => HAR NREs on the 2nd and later same-race droid. Worldgen is unaffected on four independent grounds; `guy762_KotORFaction_RogueDroids` RAIDS are broken, and that faction is the KotOR distress call's antagonist and a **v1 KEEP**. Routes: **(1)** drop the KotOR flesh type from our patch — one xpath, no assembly; restores tending on droids; loses vanilla EMP behaviour on them; does NOT affect our ion weapon (its guard moved to `IsMechanoid` on 08-13). **(2)** ~5 lines of Harmony in an assembly we already ship — a build, a deploy and a load; gives Humanlike pawns a relations tracker regardless of `IsFlesh`; keeps both the machine framing and working raids; it is the only route that also covers `current`, the previously-spawned droid, which is where the throw actually happens. **(3)** accept broken droid raids — free; the quest antagonist cannot raid past its first pawn. EXCLUDED: retargeting to vanilla `Mechanoid` — it would make our own ion weapon block them. Full write-up: `observed/2026-08-14_O12_har_pawngen_nre.md`.
verify:   EMPTY
criteria: EMPTY

## D3 The Galactic Empire is not the antagonist the design says it is
spec:     Four independent layers say the same thing. (1) Pillar 5 (`faction_roster_v2.md:105`) promises one permanent enemy: the Galactic Empire. (2) The shipped flags are `hostile: false`, `goodwill: 0`, `permanentEnemy: false`, and a SECOND empire outranks it — "The Fallen Dominion" holds 4 settlements to the Galactic Empire's 1. (3) `jawa/fire_incident RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true` returns `canFireNow: false`, because `TryResolveRaidFaction` keeps the passed faction only if `HostileTo(Faction.OfPlayer)` => the flagship antagonist is MECHANICALLY INCAPABLE of raiding the player. (4) The religion rubric scores it **0 on the decision axis**: no refusal comp, no High-impact precept anywhere in its eight. ⚠ At least two of these layers may be the SAME FACT — `permanentEnemy false` plausibly explains `goodwill 0` and `canFireNow:false` together; BUILD B32 reads the shipped `FactionDef` to settle whether this is a one-field authoring fix or a design crisis.
verify:   EMPTY
criteria: EMPTY

## D5 The Homestead — cut it or differentiate it
spec:     It fails the name-blind test against the Deepwater Compact at **24% Jaccard**, the roster's worst pair, and the Homestead is the decoration half. Do not polish it. This gates the D2 structure ruling (`Structure_TheistAbstract`, deity *the Withdrawn*), which stands only if the faction survives.
verify:   EMPTY
criteria: EMPTY

## D6 Geonosian — retarget the defect or close it
spec:     `faction_roster_v2.md:1403` sets "Preferred xenotypes: Geonosian" while Global system 3 (`:183`) sources Geonosian from the separate race inventory — different objects, and the roster never picks. The named route DOES NOT EXIST: `PreferredXenotypes` has exactly one precept (`PreferredXenotype`, Biotech) and its xenotype is chosen at ideo-GENERATION time, not in XML; there is no `FactionDef` path to it. Retarget at `PawnKindDef` xenotype chances — which is where faction 8's composition already lives — or close it. Group E is not blocked on a roster decision; it is blocked on a wrong one. Pattern to follow: Free Droid (`:1009`) flags the engine question AND rules a fallback.
verify:   EMPTY
criteria: EMPTY

## D7 The mech review sheet — accept name+role for the 25 vanilla mechs
spec:     Axes are known and committed (`data/mech_control_axes.md`): raids · ancient dangers + clusters (one flag, not separable) · bossgroups · gestation · sellable · purchasable (a separate axis, a 3-line patch) · decoration. Art is on disk for 55 of 80. The sheet is otherwise complete and waits only on whether the owner accepts name+role for the 25 whose art is bundle-locked.
verify:   EMPTY
criteria: EMPTY

## D8 Two mod adoptions
spec:     **GravTide** `3779600989` — recommended ADOPT `[v2]`; the ocean objection is dead. **`[KR] Star Wars: Droids`** `3248936254` — Biotech-only, covers 5 of 6 real chassis gaps; take the chassis, REFUSE its faction wrappers.
verify:   EMPTY
criteria: EMPTY

## D9 Does the restraint bolt work on PEOPLE
spec:     Ruled KEEP, weighted ~10x a droid, plus a mood hit. Not confirmed by the owner.
verify:   EMPTY
criteria: EMPTY

## D11 The art directive — resume, or stay parked
spec:     Standing directive (owner, 2026-08-13): stop fixing art until the owner can verify the art doesn't work; the gate is the owner's own eyes, not a clean log, not a blank alpha channel, not an md5, and the PREMISE is what is suspect. Parked by it and awaiting a ruling: **C7 rows 4–6** (fully triaged with per-file canvases and verdicts, `design/Jawa/art/c7_directional_triage.md`) · **C-t2** (`SWDoorBlast{B,D}Door_Frame_east_m.png` carry an underscore before the `m`; the convention is `...eastm.png` — exactly the class the directive suspects, nothing errors and nobody has looked in game) · **C3a Eopie**, two proposals never ruled on: the species-inconsistent head shapes and north's featureless rear (salmon-pink is a playtest question, do not re-raise). Do not read silence as approval. Already-deployed work stays in place.
verify:   EMPTY
criteria: EMPTY

## D12 The Jawa faith — name, and Nomad vs Tunneler
spec:     The name contradicts itself in its own file: "The Salvation" vs "The Articles of Passage". Nomad-vs-Tunneler is still a coin. Owner's, not any seat's — flag both if he opens it. Section 12 of `faction_religions_spec.md` is a deliberate empty slot because the owner is building it.
verify:   EMPTY
criteria: EMPTY

## D13 Two lore contradictions inside the approved ideoligion
spec:     (1) Lore sanctifies ration paste, but the ideo sets `NutrientPasteEating_Disgusting`. (2) Sh'kaar is written as "the sun that never sets"; the older doc says twin suns, and the tidally-locked world postdates it.
verify:   EMPTY
criteria: EMPTY

## D14 Broken-infrastructure mod — repairable workbenches, turrets, engines `[v2]`
spec:     For the ship. Survey what exists BEFORE designing — `design/Jawa/art/graphics_overhaul_protocol.md` §6.
verify:   EMPTY
criteria: EMPTY

## D15 The canon droid lineage catalogue — re-request or drop
spec:     Agent `abe113a7` delivered the non-CIS additions only; the main lineage table never arrived. Re-request it if the visual comparison sheet is wanted.
verify:   EMPTY
criteria: EMPTY

---

**TODO_v2.md** — absorbed whole, 2026-08-14. The file it came from is deleted;
citations of the form `TODO_v2.md §N` resolve to the numbered sections below.

_Split out of `TODO.md` 2026-08-13 when the v1 line was drawn
(`D:\Luke\dev\Rimworld\infrastructure\state\V1_SCOPE.md`). Rewritten from 1,172
lines of argument into a register 2026-08-14._

**This is a REGISTER, not a workspace.** One compact entry per open v2 item: what it
is, who would own it, what it depends on, and whether v1 closing unblocks it. The
reasoning that produced an entry lives in the commit; the *spec* that came out of one
lives in `design/`, a skill, or the mod it belongs to — never here.

⚠️ **Do not work these while v1 is open.** If one blocks a v1 row, say so and it
moves back. **v2 starts the day v1's gate passes.**

**Closed items are one line in `infrastructure/state/CLOSED.md`, not a struck-through
block here.** Check there before re-filing anything.

---

## The register

| § | item | owner | blocked by | v1 close unblocks? |
|---|---|---|---|---|
| **0b** | Do enemies actually USE vehicles in raids? Three mods live or die on it | PROJECT | owner must identify "mother (HK Tank)" | no — offline-answerable today |
| **0c** | Alpha Neolithic reskin — the **4 vehicles after the sled** | CREATE | nothing | yes (CREATE is v1-committed) |
| **1** | Everything detonates — energy-density explosion model | unowned | nothing | yes |
| **3a** | Traps entry for the `-main`-branch `supportedVersions` trap | WORLD/OPS | nothing | no — 15 minutes, do it anytime |
| **3b** | W3 — re-scope `outer_rim_cherrypick_list.md` against the 1.6-native module | WORLD | nothing | yes |
| **3c** | W4 — can Royalty noble pawnkinds take varied alien races? | WORLD | nothing | no — offline from the def dump |
| **3d** | Four `INSPIRATION ONLY (1.4/1.5)` bullets the retraction missed | OPS | nothing | no |
| **4a** | W7 — re-cast rebel gear onto the scavenger factions | WORLD | "Junker Scrap-Warrens" has no defName | **no — needs the game up** |
| **4b** | U2 — balance-audit the live JDS droid weapons | WORLD | nothing | yes |
| **4c** | U3 — build the **Free Droid Enclaves** `FactionDef` | CREATE | worldgen (faction #5 in the spec) | yes — and it unblocks C-v3 |
| **4d** | U4 — the rare Homestead Jedi `pawnGroupMaker` | VISION+CREATE | joint Sith/Jedi build (VISION V-new) | yes |
| **5** | V2 Ideology lines — does the Jawaese actually reach Suppress/ReduceWill? | VISION | 🛑 owner STOP WORK | yes — and it needs the game up |

---

## 0b. [PROJECT] Do enemies actually USE vehicles against us?

**Owner's ask, 2026-08-12:** _"The point here is to be able to have enemies use these
against us in raids. If they can't or won't, then these three mods should be
dropped."_ **The test is binary and the owner has pre-committed to the answer.** No
partial credit — the player-facing half is not the justification.

**The three:** `smashphil.vehicleframework` · `gabrieel1482.raidvehicleframework` ·
**"mother (HK Tank)" — ⚠️ NOT IDENTIFIED. Owner: which mod is this?** No `HK`-prefixed
defName in any def type and nothing named "mother"/"HK"/"tank" in the manifest. The
other two can be assessed without it.

**Already found, and not encouraging:** `VRF_SettlementVehicleDef` has **zero defs**
in the live dump — VehicleRaid Framework's own registry of which settlements field
which vehicles, empty. ⚠️ **Do not close on that alone.** Faction Control's whole
capability lived in settings with zero defs; same trap, same day. "The def type is
empty" and "raiders never use vehicles" are different claims.

**Check offline, in order:** (1) `strings` both assemblies for `PawnsArrivalModeDef`,
`RaidStrategyDef`, `IncidentWorker_RaidEnemy`, Harmony targets; (2) look for
`Config/Mod_*_*.xml` settings; (3) does any live `PawnKindDef` or faction
`pawnGroupMaker` reference a vehicle at all — if not, settled; (4) only then put a
named log string in `NEXT_RELOAD.md`.

**Rides the same decision:** `farxmai2.vanilladeconstructablevehicles` (a VVE add-on)
— if VVE survives but the frameworks go, check whether it still has a job.

---

## 0c. [CREATE] Alpha Neolithic reskin — the four vehicles after the sled

`sarg.alphavehiclesneolithic`. **The dog sled shipped** (eopie pair, `ad3e3c7`
`2a9a004`; see `CLOSED.md` C3a). **Four vehicles remain**, each 6 files = **24 PNGs**:
**Chariot** (1 horse) · **War chariot** (2 horses) · **Covered carriage** (2 horses) ·
**Ox cart** (2 oxen).

The other seven have no draught animal — Rickshaw, Palanquin, Wheelbarrow and Hwacha
are human-powered; Balloon is `Air`; Row boat and Outrigger Canoe are `Sea`. Nothing
to reskin.

📏 **The measurement is already done and committed:**
`D:\Luke\dev\Rimworld\src\Jawa\DesertVehicleReskin\Source\GEOMETRY.md` — per-vehicle
animal bounding boxes, hitch bands, the dilate-by-8px mask rule and the 512×512
canvas facts. **Do not re-measure.**

Three numbers that live only here, kept so they are not re-derived:
- **Mask suffix is `AV_DogSled_southm.png` — `m` on the facing, NOT `_south_m.png`.**
  Applies to all 24 remaining files.
- Every facing has a paired `_m` mask for the Vehicle Framework's colour system.
  **Edit the mask in step with the art or the new animal will not tint.**
- Aspect ratios that decided the eopie: dog slot **0.57**, Eopie **0.618**, Massiff
  **0.720**. `bodySize` is a *mass* stat and does not predict sprite proportions —
  that is what made the Massiff argument wrong.

⚠️ **Reference only — do not composite.** The creature art belongs to Star Wars Animal
Collection (Continued), and lives inside a 33 MB Unity AssetBundle (`extract_bundle.py`,
needs the venv; recipe in `design/Jawa/art/graphics_overhaul_protocol.md` §2.2). Draw
from it, never paste it.

**Load `skills/generating-rimworld-sprites/` before making any PNG.**

---

## 1. Everything detonates — explosions scaled by energy density

**Owner's ask 2026-08-12; accepted, not started, no files written.** Explicitly
deferred to v2 by `V1_SCOPE.md` — *"the energy-density explosion model — large,
self-contained, pure v2."*

📄 **The spec now lives at `D:\Luke\dev\Rimworld\design\Jawa\explosion_energy_model.md`**
— the vanilla turret ladder, the shield-belt stat findings, the `PostDestroy` IL read,
the `DestroyMode` table (⚠️ `explodeOnKilled`, **never** `explodeOnDestroyed`), the
`tickerType` ConfigError, the `Turret_FoamTurret` template, the corpse/salvage IL
trace, the three tiers, the `E` curve and its proxy table, and the six pre-decisions.

**The droid half is not in that doc** — it is `design/Jawa/droid_ruling.md` §6.

**State:** the destroy-and-detonate half is **pure XML** and batches into any load.
**Shield-break venting still needs Harmony** and is the only piece that rides a load
alone. Ship the XML first.

---

## 3. The Empire

🔴 **The two-Empire fusion is STRUCK.** Owner ruled one Empire, one Emperor
(`a8768c7`, `78a0967`): vanilla `Empire` (Royalty) reskinned as the Galactic Empire,
Palpatine, the one permanent enemy, ~3 surface seats near the spaceport with the rest
orbital. The *Imperial Desert Directorate*, the *Fallen Dominion*, the
disgraced-local-aristocracy reading and any office called *Sector Director* must not
return in any doc. Canon: `design/Jawa/worldbuilding/faction_world_spec.md` §5.

⚠️ **One consequence still unpriced:** a permanently hostile Empire deletes Royalty's
progression — titles, permits, honour, imperial favour all run through this faction
being talkable-to. Almost certainly correct for a Jawa clan, but it is a whole DLC
subsystem and should be a decision, not a side effect. Owner's call; not a v2 job.

**The Outer Rim module is live and is a GEAR donor, not the faction.**
`Neronix17.OuterRim.GalacticEmpire`, WS `2919248699`, active in the 580 stack, 1.6
verified on disk. It ships the stormtrooper wardrobe (`Imp_StormtrooperCuirass` /
`Helmet` / `Pauldrons` / `Kama`), **`Imp_OfficerUniform_Black`** — the black officer
uniform the owner asked for — ISB, Death/Scout/Range/Snowtroopers, 19 Imperial
`PawnKindDef`s including `OuterRim_ImpStormtrooper_Desert`, and a 10.7 KB Harmony
assembly (solo-load waived by the owner). Full entry: `required_mods.md:604`.

⚠️ **Do NOT also load "Star Wars – Factions (Continued)" (WS 3544900066)** — it ships
its own Galactic Empire and would collide.

### 3a. [WORLD/OPS] File the branch trap — it has caught two independent passes

**The lesson is not written down anywhere.** `skills/rimworld-modding/references/`
has no entry for it, and it cost six days plus a re-derivation by a second census.

> **Never read `supportedVersions` off a GitHub `main` branch or a `*-main` zip.**
> Multi-version RimWorld mods branch per game version and this author keeps `main`
> stale. Check the **Workshop copy on disk**, or the branch matching your version.
> The control case: Outer Rim **Core** reads 1.4/1.5 on GitHub `main` and
> **1.4/1.5/1.6** in the Workshop copy we actually run.

**Generalises to:** a local, complete, file-backed artifact is more convincing than
the truth. All nine `vendor/mod_sources/Outer-Rim-*-main` extracts are stale-branch
pulls — **delete or clearly mark them**, or a third pass reaches the same wrong answer.

### 3b. [WORLD] W3 — re-scope the cherry-pick list

`design/Jawa/mods/outer_rim_cherrypick_list.md` (91 lines) is a hand-port plan whose
stated top priority is *"Empire trooper ladder + blasters + apparel + training hediffs"*.
That plan exists **only because we believed the module was unloadable**. It is
1.6-native and active, so most of §1 is dead work. **Keep §3** — Old Republic Sith as
the Empire's Sith-elite donor; that lift is still wanted.

⭐ **The defNames did not change between 1.5 and 1.6, only the filenames** — so the
SRC-verified defName list in that doc is still accurate. Nothing has gone stale; the
question is only *port vs load*.

### 3c. [WORLD] W4 — the feasibility check the docs already owe

`cherry_picker_killlist.md:82` and `required_mods.md:687` both flag it unanswered: can
Royalty noble pawnkinds be given varied alien races, or do their generation rules block
it? **Answerable offline from the live def dump.** Fallback already written down — let
varied races appear naturally rather than guaranteeing them.

### 3d. [OPS] Four stale `INSPIRATION ONLY (1.4/1.5)` bullets the retraction missed

The 2026-08-12 retraction in `required_mods.md` fixed the table, the Galactic Empire
bullet and (later) Rebel Alliance. **It did not fix `:605`–`:608`** — Galactic
Republic, Separatists, Mandalore and Old Republic all still carry
*"⚠️ INSPIRATION ONLY (1.4/1.5, SRC-AUDITED)"*, which the retraction directly
contradicts. `research/Jawa/sw_ingredients_inventory.md` still carries the old
*"DO NOT LOAD, not 1.6"* framing too. **Verify each by branch before rewriting** — the
verdict may be right for a different reason.

### 3e. Not in scope, deliberately

Player-side anything. Royalty stays non-progression (`forbidden_mods.md:86`), no player
psycasting (`:62`), and Imperial gear that out-classes vanilla rides the §19.5 balance
pass in the same lift — the enemy gets better *coordination*, never a better *curve*.

---

## 4. Ingredient verdicts — the 2026-08-12 subscription batch

**Owner subscribed six mods for evaluation and ratified these verdicts the same day.**
Kept as a register row each; the arguments are in the commits.

| mod | WS | verdict |
|---|---|---|
| Outer Rim – Galactic Empire | `2919248699` | ✅ **ADOPT** — 1.6-native, active. See §3 |
| Outer Rim – Rebel Alliance | `2919249903` | ✅ **ADOPT FOR GEAR, FACTION SUPPRESSED** — done, `5f68a9e` |
| LK Mineable Resources OR | `3565716659` | ✅ **ADOPT** — filed as `desert_world_design.md` §3B(6) |
| Outer Rim – Separatists | `3097604003` | ⚠️ **KEEP DOWNLOADED, NEVER ENABLE** — live JDS TSDA already ships `JDSCIS_CIS_Faction` with 8 `pawnGroupMakers` vs 4 and 16 droid kinds vs 9, and adds zero new droid races. Enabling it puts a second "Confederacy of Independent Systems" on the map |
| Outer Rim – Chiss Ascendancy | `2919962538` | ❌ **REJECTED, unsubscribed** — defines **zero** `GeneDef`s; the xenotype is live three times over (Galactic Diversity's `LoadFolders.xml` stands its copy down only `IfModNotActive` Csilla); 2 of 3 weapons are stat-clones and `OuterRim_CharricRifle` is a §19.5 violation (27 dmg × 2-burst at range 38 on the *rifle* cooldown base) |
| Mines 2.0 | `2503894706` | ❌ **REJECT** — filed as `desert_world_design.md` §3B(6) |
| LK Mines 2.0 compat | `3558833789` | ❌ **REJECT** — falls with Mines 2.0; also unguarded |

⛔ **The Separatist weapon lift is REDUNDANT — do not author it.** All four already
exist live in `[JDS] StarWars - Armory`: `OuterRim_E5Blaster`→`JDSA_E-5_Blaster_Rifle`,
`OuterRim_E5sSniperRifle`→`JDSA_E-5S_Sniper_Rifle`, `OuterRim_RG4DBlaster`→
`JDSA_SE-14_Light_Blaster_Pistol`, `OuterRim_BXVibroblade`→`JDSA_Vibroblade`. The
player would see two E-5 blasters in a stack already carrying 674 weapons. **U2 below
is the work that is actually owed instead, and it is the same effort.**

### 4a. [WORLD] W7 — re-cast the rebel gear onto the scavenger factions

**This is what converts a suppressed faction into a salvage layer.** Without it the
gear exists but nobody wears it. Duplicated at `queue/VISION.md` **V13** `[v2]`.

⚠️ **Three of the four premises in the original filing were wrong. Checked from disk:**
1. **The named tool is NOT installed.** WS `3635005747` (Faction Weapons and Apparel
   Set) was never subscribed — *"already adopted"* meant *chosen on paper* from a
   Workshop page in 2026-08-07.
2. **Not blocked — the documented fallback IS live.** `co.uk.epicguru.factionloadout`
   (Rimsential – Total Control: Continued), active now. `ship_deck_plan.md:201` warns
   plan B is *"more powerful but heavier"*; that trade is now the default.
3. 🔴 **Not offline-authorable through either tool** — both configure through an
   **in-game mod-settings UI**. W7 needs the game *up* and cannot be prepared as a
   patch. `Config/` holds no Total Control file, so nothing has been started.
4. **Half the target does not exist as a def.** `OuterRim_MoistureFarmers` is real.
   **"Junker Scrap-Warrens" has no defName anywhere** — it is a design-doc faction
   (`faction_roster_v2.md` §12) with no implementation vessel. Decide what it maps to
   first; `OuterRim_BinaryStarRaiders` is the only plausible candidate and **nothing
   on file says it is the Junkers**.

⭐ **Prefer the offline XML path for a small change:** `weaponTags` / `apparelTags` on
the PawnKindDef, matched against ThingDef tags and wealth-gated by the engine. Patchable
in `Jawa_Patches` today, no tool and no UI session — appropriate if W7 only ever meant
*"Homestead pawns can carry an A280"*.

### 4b. [WORLD] U2 — balance-audit the live JDS droid weapons

Two smell wrong on sight and need checking against `setting_physics.md`:
`JDSA_E-5S_Sniper_Rifle` fires a **4-round burst** (snipers should not burst) and
`JDSA_E-5_Blaster_Rifle` has **range 20** — shorter than a vanilla assault rifle, which
makes Separatist droids feel limp at exactly the range the fiction wants them dangerous.
Both are one-line `PatchOperationReplace` fixes in a mod we already load, on content the
player will actually meet.

### 4c. [CREATE] U3 — the droid faction we DO want is not in either mod

`faction_world_spec.md` §6 lists **Free Droid Enclaves** as faction 5 —
100% droid chassis, 0% biological — a *territorial* threat holding specific tiles,
hostile to the Empire because the founders were abandoned after the Clone Wars. That is
not "CIS battle droids still fighting a dead war", and **neither Outer Rim module
supplies it**.

Both candidate mods are pure XML with zero C#, and every droid race we need is installed
twice over (Droid Depot + JDS TSDA), so authoring our own `FactionDef` + thin
`PawnKindDef`s is **~200 lines and no assets**. Build it; do not adopt a substitute.

⭐ **This unblocks `queue/CREATE.md` C-v3** — the restraining-bolt spec explicitly lands
with the Free Droid Enclaves *"whose `FactionDef` is unbuilt"*.

### 4d. [VISION+CREATE] U4 — the rare Homestead Jedi

`required_mods.md:596` permits it and `desert_world_design.md` §3B(7) supplies the why.
Unbuilt: the low-weight `pawnGroupMaker` entry on the Moisture-Farmer / Homestead faction
with the curated light + telekinesis VPE loadout. `OuterRim_MoistureFarmers` is live in
Outer Rim Core, so the vessel exists.

**Spec exists:** `design/Jawa/force_users_build_spec.md`. Owner has flagged Jedi-for-
Homestead and Sith-for-Empire as **one joint build** (`queue/VISION.md` V-new), so U4
should not be built alone.

⚠️ `force_users_build_spec.md` cites this item as `TODO_v2.md:1081`. **That line number
is dead as of this rewrite** — the item is §4d/U4. Three citations to repair, at `:8`,
`:1067` and `:1072`. Not my file.

---

## 5. [VISION] V2 Ideology lines — do the Jawaese lines reach Suppress/ReduceWill?

> 🛑 **STOP WORK.** Owner, 2026-08-13: *"Deepening this is a v2 item. Let's get stuff
> working that's a blocker to play first."*

**State: NOT failing — unverified.** SpeakUp is confirmed producing glossed Jawaese on
screen; `Suppress` is confirmed firing twice with Jawa initiators onto slaves. **The
text of a Suppress entry has never been seen** — every hovered line came back
`Chitchat`. The prisoner half cannot fire at all.

**Mechanism half is CLOSED** (`CLOSED.md`, 2026-08-12): 14/14 Ideology defs carry our
rules, `Suppress` sits in `logRulesInitiator` gated `INITIATOR_kind==OuterRim_Jawa` /
`OuterRim_JawaTribal` at `priority=250`, and the `ReduceWill` InteractionDef/
PrisonerInteractionModeDef disambiguation is clean (24 rules vs 0). Source:
`D:\Luke\dev\Rimworld\src\Jawa\JawaVoice\Patches\JawaVoice_Ideology.xml`

### 🔴 The gloss is NOT a discriminator — disproven on screen

Hovering `Keetkeeh tub tub tohti te bataa. (At least the sunlight helps a little.)`
gave the tooltip **"Chitchat"**. The gloss separates JawaVoice from **vanilla**, which
was never in question, and says **nothing** about which InteractionDef sourced it.
V1 insults, V3 Chitchat and V2 Ideology lines all render in the same shape. **Scoring
V2 on the gloss produces a false pass.** RimWorld does not store the rendered line —
`PlayLogEntry_Interaction` holds `intDef` + participants and the text is generated at
*draw* time by the same rule engine for every interaction.

### ✅ The correct test — find the entry first, THEN read its text

| tooltip says | text is | verdict |
|---|---|---|
| `Suppress` / `ReduceWill` / `EnslaveAttempt` / `ConvertIdeoAttempt` | Jawaese + gloss | ✅ PASS for that half |
| same | plain English narration | ❌ real failure — `priority=250` lost its pool |
| `Chitchat` / `ChattedAboutSomeone` / `SpreadRumors` | either | ⬜ NO INFORMATION — do not score |

**Both halves must be seen; they are different interactions.** PRISONER = `ReduceWill`
(6 lines) / `EnslaveAttempt` (4) / `ConvertIdeoAttempt` (3). SLAVE = `Suppress` (4) /
`SparkSlaveRebellion` (4). 14 defs, 49 lines total.

### 🔴 Four preconditions whose absence looks exactly like failure

1. **A prisoner does NOT generate warden interactions by default.** Prisoners default to
   `<interactionMode>MaintainOnly</interactionMode>`, so `ReduceWill` /
   `EnslaveAttempt` / `ConvertIdeoAttempt` **can never fire** and their absence proves
   nothing. Set the mode per prisoner, give a colonist **Warden** work, and check there
   is at least one prisoner bed.
2. **The two halves fail for different reasons** — the slave half is a *text* question,
   the prisoner half a *setup* question. Do not report them together.
3. **The initiator must be a Jawa.** A non-Jawa suppressing a slave **correctly** gives
   a vanilla line — a pass for the gate, not a V2 failure.
4. **The game must be UNPAUSED.** SpeakUp fires on ticks; a paused game produces silence
   indistinguishable from a broken patch.

### ⛔ The save can never answer the text — do not try again

`PlayLogEntry_Interaction` serialises **no `<text>` node** — zero across 56 blocks. It
stores `initiator`, `initiatorFaction`, `initiatorIdeo`, `intDef`, `logID`, `recipient`,
`ticksAbs`. **Jawaese is never in the `.rws`**, so grepping for it returns 0 whether the
patch works or not. A save answers *whether an interaction fired and who initiated it*,
never *what it said*. Only the on-screen social log answers the text.

⚠️ `priority=250` **outbids** Core's pool, it does not replace it — vanilla lines
coexisting is expected and is evidence neither way.
