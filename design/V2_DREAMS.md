<!-- status: aspirational -->
# V2 — dreams and hopes

> 🔴 **STANDING OWNER RULING — 2026-08-15. THERE IS NO WORLDGEN FEATURE, IN ANY VERSION.**
>
> Verbatim: *"There is no auto worldgen we are building. The world will be user-made and
> frozen. We are NOT enabling worldgen, we will provide players a savegame with a fixed
> world, period. That's it. True worldgen is OUT of any version, even v2."*
> Clarified moments later: *"(but designing worldgen by hand and design documents to
> guide that are in)"*
>
> **OUT, permanently — this is not a deferral:**
> - Any automated or programmatic worldgen we build. No tool, script, DLL or bridge verb
>   that generates a world as a product.
> - Worldgen as a player-facing capability. **Players never generate anything.** They
>   receive a savegame containing the fixed world.
> - Any v2 worldgen item. ⛔ **v2 is NOT a parking space for this** — mark such work
>   dead, do not move it to `design/V2_DREAMS.md`.
>
> **IN, unchanged and still wanted:**
> - The owner building the world **by hand, once**. That is how the fixed world exists.
> - **Design documents that guide him doing it** — `WORLDGEN_FACTION_CHECKLIST.md`,
>   `SCENARIO_SETTINGS_SPEC.md`, the faction, biome and terrain specs. Keep writing them.
>
> 🔑 **The consequence, and it got stronger rather than weaker:** one hand-made world,
> frozen, then shipped to every player. **A faction, ideoligion or setting absent when he
> builds it is absent from every player's game forever, with no regenerate to fall back
> on.** That is why the faction roster and the faith text stay v1.


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
resolve. 🔴 **New appends do NOT get one** — owner, 2026-08-20: name them
`THREE_DESCRIPTIVE_WORDS_#` (three UPPER_SNAKE words plus a number), because nobody can
remember what `D55` was. See `CLAUDE.md`. The no-format rule above still holds for
everything after the heading. The `row:` and `state:` fields were queue plumbing and were dropped on the
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
spec:     `src/Jawa/Jawa_Armoury/Patches/Armoury_MeleePower.xml` and `Armoury_RangedDamage.xml`. Swept into `81939e1` (subject: genome tooling), never reviewed, no provenance banner. Re-run the generator; generators anchor provenance and print a banner via `src/RimMandrake/Utils/patch_provenance.py`. Also carries 8 double-match `Replace`s.
verify:   provenance banner shows no `unknown` anchors — `unknown` means STOP. Scoped `validate_patch.py --defs` clean; the 8 double-match `Replace`s resolved.
criteria: EMPTY

## B5 MegafaunaYield.xml — 3 double-match Replaces
spec:     3 `PatchOperationReplace` ops each match two nodes (same value written to both). Cosmetic; a player cannot see it.
verify:   scoped `validate_patch.py --defs` sweep reports 0 double-match `Replace` in `MegafaunaYield.xml`.
criteria: EMPTY

## B7 Repair the approved ideoligion .rid
spec:     `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Ideos\The Salvation (built).rid`. Two defects: `AM_Fertility` was dropped while two precepts still require it; `VME_Nomad` is IN and must come out — its own description says non-vanilla movement systems will not register and it inflicts −50 mood at 60 days. `Nomadic_Preferred` is a PRECEPT (`requiredMemes` empty), zero slot cost, already in the file, and does the job: `GravshipUtility::ArriveNewMap` unconditionally stamps `IdeoManager.lastResettledTick`, the only field its ThoughtWorker reads. (`ArriveExistingMap` does NOT write it.) Rebuild with `python3 src/RimMandrake/Utils/build_salvation_rid.py --check|--write`; it never rewrites the source. Do not delete the owner's original `The Salvation.rid` beside it. Do not "fix" `AM_Structure_Scavenger`'s `deityCount 0` by swapping the structure — no installed structure meme allows more than 4, which is why the nine gods live in the description.
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
spec:     `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`. Pattern is the Horax cult, `Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml`: `fixedIdeo` · `ideoName` · `ideoDescription` · `forcedMemes` (structure first, complete set) · `requiredPreceptsOnly` · `deityPresets` · `disallowedPrecepts` · `styles` — NOT the Empire's `requiredMemes` + `structureMemeWeights`. Entry 1 (Galactic Empire — The Rising Order) lands on vanilla `Empire`, replacing that family. Entries 1 (two deities), 2 (one) and 3 (one) need `deityPresets`; the corrected `deityCount` table is at the foot of the spec. Take `ideoName`, `ideoDescription` and every `deityPresets` name/type VERBATIM — they are the only text the engine renders. Never set `hiddenIdeo`. Section 12 (Jawa) is a deliberate empty slot — the owner is building it. Legal vocabulary: `design\Jawa\worldbuilding\data\ideology_palette.md` (136 memes, 685 precepts, 41 styles, 92 ritual patterns). Three engine constraints: charity has no negative precept · `PreferredXenotypes` cannot be aimed at a xenotype from XML · `Apostasy_Abhorrent` hard-conflicts with the `Guilty` meme. Meme ceiling is a COUNT (`MemeCountRangeAbsolute` 1–4 normal memes), not an impact budget — never pass `--impact-budget`.
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

## ~~B19 `design/Jawa/droid_ruling.md` states a mechanism that is not in the defs~~ — ✅ **CLOSED 2026-08-20**
spec:     JDS droids do not explode — they are force-killed on downing and their wrecks are repairable. The ruling holds; the stated reason is wrong. Rewrite the mechanism.
verify:   the stated mechanism matches the defs.
criteria: MET. `droid_ruling.md` §"JDS droids are never taken alive" now states the measured mechanism (`fleshType Mechanoid` → `deathOnDownedChance = 1.0`), records that the mod ships no `deathAction`/`CompExplosive`/DLL, names the one droid in the stack that does self-destruct (`guy762_DroidRace_KX12APD`, a KotOR def), and warns that §6's explosion tier is our design rather than the mod's behaviour. The old heading is gone. **Do not action from this row.**

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
spec:     `src/Jawa/Jawa_Patches/About/About.xml:36` records that the shipped def has `permanentEnemy false` while the faction dossier says permanent enemy YES — that single field plausibly explains `goodwill 0` AND `canFireNow:false`. Already checked: the live faction list (`hostile:false`, `goodwill:0`, name "the Galactic Empire") and the About.xml note. NOT checked: the shipped `FactionDef` itself — a workshop-tree grep timed out at 120 s twice, so scope it.
verify:   quote `permanentEnemy` and the hostility fields from the shipped `FactionDef` file, with path and line.
criteria: EMPTY

## B33 Malformed closing tag in an active workshop mod loses two precepts
spec:     `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2896845138\Defs\Precepts.xml` line 210 reads `<defName>GarryFlowers_Slave_Relation_Vanilla<defName>` — no slash. The live dump shows `GarryFlowers_Slave_Relations` carrying 2 positions where the XML defines 4; `_Equality` and `_Vanilla` are lost with no error. Checked clean: nothing in the religions spec or the Unearned spec depends on them, and the campaign's slave-romance love-gate uses `GarryFlowers_Slave_attendance`, which is unaffected.
verify:   after the fix the live dump shows 4 positions.
criteria: EMPTY

## B38 Attribution rule: a loose slag chunk on a quicktest map is ours
spec:     Across the 585-mod set as measured 2026-08-14 (the list is 575 since 2026-08-15 — re-run this census against the fresh dump before relying on the ONLY) `Jawa_ScatterScrapfields` is the ONLY GenStepDef that scatters `ChunkSlagSteel`, and it plus `Jawa_StampGroundHulk` are the only non-shipped steps in `Base_Player`'s 46-step list. Every other def-level route to a loose chunk lands on a site/quest/orbital map, NOT an ordinary colony map: `OpportunitySite_Satellite` is an Odyssey orbital platform (`terrainDef OrbitalPlatform`, `LayoutWorker_OrbitalPlatform`); the 42 KCSG `StructureLayoutDef`s carrying slag (Ancient mining industry 4, VQE Cryptoforge 18, VQE The Generator 16, Alpha Genes 1, Vanilla Genetics Expanded 3) are reached only through `SitePartDef`s — `AbandonedPlasteelMineSite_Site`, `VQE_Quest1Site`, `AG_AbandonedBiotechLab`, `GR_AbandonedLab`; `CustomMapDataDef` `AM_Bunker_C`/`AM_Street_A` only through `AM_StreetSite`; `SymbolDef ChunkSlagSteel` is a KCSG auto-generated symbol with no trigger of its own. ONE exception, missed by a string census because it is indirect: `AB_DerelictBioLab` (Alpha Biomes `TileMutatorDef`, worker `VEF.Maps.TileMutatorWorker_GenericKCSGSpawner`) spawns one of thirteen `AG_AbandonedBiotechLab*` layouts, of which `Delta` carries slag — `chanceOnNonLandmarkTile 0.005`, `maxHilliness Flat`, no biome and no temperature gate, so it CAN fire on a plain desert colony tile. RULE: a `ChunkSlagSteel` on a quicktest map whose tile mutators contain none of `AncientGarrison`, `AncientWarehouse`, `AB_DerelictBioLab` is OURS. Residual, stated not hidden: vanilla `Assembly-CSharp` contains the string `ChunkSlagSteel` (the `ThingDefOf` field), so a C#-side genstep cannot be enumerated offline — the density criterion below is what covers it.
verify:   offline, over `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs`: `GenStepDef.json` contains exactly one def whose JSON holds `ChunkSlagSteel` and it is `Jawa_ScatterScrapfields`; and the only `TileMutatorDef`s reaching slag — directly or through `modExtensions/KCSGStructuresToSpawn` — are `AncientGarrison`, `AncientWarehouse`, `AB_DerelictBioLab`. Re-run both after any change to the active mod list.
criteria: on a desert quicktest, `jawa/list_things` for `ChunkSlagSteel` on a 250x250 map. PASS = ~440-560 chunks in ~44-56 clusters of 10 with `Filth_MachineBits` under them (`countPer10kCellsRange 7-9`, `clusterSize 10`, 6.25 units of 10k cells). FAIL = under ~30 chunks, or every chunk inside one walled structure — that is the Alpha Biomes lab, so read the tile's mutator list before blaming our step.

---

**CHECK** — deferred observations and measurements, drained from `infrastructure/state/queue/CHECK.md`

## C2 L3 — the Galactic Empire raid, and read the faction back
spec:     Chain: game DOWN -> deploy BUILD B1 (`--gm`, 30 tools) -> up -> `jawa/set_faction_relation` make `OuterRim_GalacticEmpire` hostile -> `jawa/fire_incident incidentDef=RaidEnemy faction=OuterRim_GalacticEmpire dryRun=true` (abort on `canFireNow:false`) -> fire for real -> screenshot. PASS `points` EXPLICITLY: `points<=0` takes the storyteller default, which on a fresh quicktest is tens of points — one trivial attacker cannot answer whether the Empire reads as an antagonist.
verify:   EMPTY
criteria: read the `faction` field in the REPLY, never the one you sent — `IncidentWorker_RaidEnemy::TryResolveRaidFaction` keeps the passed faction only if non-null AND `HostileTo(Faction.OfPlayer)` AND (`!deactivated` OR `parms.forced`); otherwise IL_0059 passes `ldflda IncidentParms::faction` BY REFERENCE into `TryGetRandomFactionForCombatPawnGroupWeighted`, which overwrites it with a random weighted faction and still reports `success:true`. The tool reports `parms.faction` after the worker ran (`JawaBenchTerrainTools.cs:3588`). Then: does the antagonist read as the antagonist on screen.

## C3 v1 row 4 — the scrapfields count
spec:     After BUILD B3 deploys, generate a fresh map (a 90 s quicktest counts; `Jawa_ScatterScrapfields` is a `GenStepDef` at order 960 hooking `Base_Player` genSteps, so it is not biome-gated), then take a FULL-MAP `listerThings` count of `ChunkSlagSteel` — no sampling — plus `TileInfo.Mutators` and the map size. NAME THE MAP. A GenStep runs at map generation and never again, so a map's count dates the def that BUILT it. The old "11 measured" was never a measurement: 9 rects of 30x30 = 8,100 cells (~13% of the map) holding 1 chunk each on two maps, extrapolated by /0.13; where the 9 rects sat is recorded nowhere.
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

## C10 The art-observation batch — ~~Cerean and~~ Saurid
⛔ **THE CEREAN HALF IS CLOSED, 2026-08-21, owner's ruling: "completely close all
Cerean hair items right now. If they reoccur, we can reinvestigate."** Measured the
same day: `Neronix17.OuterRim.GalacticDiversity`, which owns HairDef
`OuterRim_CereanMane`, is installed but is NOT in `ModsConfig` — so the hair never
loads, no def anywhere in the 578-mod dump references `OuterRim/Hairs/Cerean`, and
`CereanManeFix` is inert. There is nothing to observe. ✅ **The SauridFrillFix half
below stands unchanged** and is still worth running.
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

## C14 The sealed-room thruster test (a retired seat's L8)
spec:     Sealed roofed room with a thruster inside -> predict INACTIVE. Thruster in the wall line with open sky aft -> predict ACTIVE.
verify:   EMPTY
criteria: send BUILD the RAW `jawa/inspect_string` lines, not a verdict — the whole roof derivation hangs off which sentence fires.

## C19 Live terrain edit — put the salt back in the dry lake bed
spec:     Geological Landforms hard-codes `SoftSand` on its dry-lake landform and the mod-side fix means editing a serialised NodeCanvas, so fix it LIVE on arrival. Target defName, verified: `Jawa_SaltCrust`, `src/Jawa/Jawa_Patches/Defs/TerrainDefs/JawaSaltCrust.xml:100`. Bound by BOTH a rect AND a source-terrain match, never terrain alone — a map-wide SoftSand->salt repaint erases the desert. Same session as worldgen, after rows 2 and 7. Not a blocker.
verify:   EMPTY
criteria: the deliverable is the CAPABILITY, not the pan — (a) can the bridge detect or be told a landform footprint, (b) set terrain over that region, (c) does it survive save/reload. First live evidence for tile-augmentation-on-approach, which has none (`design/Jawa/worldbuilding/tile_augmentation_catalogue.md`).

## C20 Re-shoot the twelve art screenshots
spec:     The 12 `NEEDS EYES` rows are NON-EVIDENCE: the Debug log window covers the CENTRE of the screen, which is exactly where `look()` puts the subject, and in `p5_004.png` and `p13_012.png` the subject is not in frame at all. `jawa/clear_ui` fixes it forward — closes every `Window_Dev`, drops the selection — and `rimbench.core.look()`/`.frame()` call it automatically. Closing the log by hand does not hold: auto-open-on-error.
verify:   EMPTY
criteria: twelve screenshots with the subject in frame and no dev window over it.

## C22 The ten art-fix mods — one spawn, one look each
spec:     Eight deployed and enabled; the two newest are `mandrake.phytokinbarkheadfix` @562 (donor @388) and `mandrake.kotorbandoliernorthfix` @**579** — deliberately outside the 556–563 art-fix slot because its donor `guy762.mm.kotorcore` sits at 572 and ships loose art. A loose PNG beats an AssetBundle regardless of order, but between two LOOSE files order decides, so a loose-art donor must be in `loadAfter` or the fix is invisible with no log line. Routes and click paths: `infrastructure/state/TEST_PLAN.md`.
verify:   EMPTY
criteria: each fix renders in the facing it targets. Judge at DISPLAY size and render the tint — art can be correct at source and broken at render. Observation only.

## C23 Run `TEST_PLAN.md` with its nine pre-flight corrections
spec:     `D:\Luke\dev\Rimworld\infrastructure\state\TEST_PLAN.md` — eight art-fix mods, v1 row 3's `Jawa_ClaimRumour`, row 4's terrain plus the 619-cell ground hulk. Part 3 needs a FRESHLY GENERATED Desert / ExtremeDesert / AridShrubland map; a quicktest counts. The nine pre-flight corrections are now **inside that file**, in its PRE-FLIGHT table — read them before typing at a live console. The terrain part is closed and art is observation-only; check `V1_CHAIN.md` before spending a load on any of it.
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
spec:     ~2 min. The refusal hook is legal and measured: `CharityRefused_Beggars` fires when beggars leave empty-handed, and arresting them raises `CharityRefused_Beggars_Betrayed` (IL: `AnySignal(beggars.Killed, beggars.Arrested)`). No spec doc exists — "The Unearned" precept was never written up, so this item carries its own design. A `FactionDef` has no precept field; only a meme's `requireOne` forces one.
verify:   EMPTY
criteria: does the event record at all for a colony holding NO `Charity_*` precept. Blocks BUILD.

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
spec:     `src/Jawa/Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets `isOrganic=false` on the KotOR flesh type `ABF_FleshType_Synstruct_Base` => `IsFlesh` false => no `Pawn_RelationsTracker` => HAR NREs on the 2nd and later same-race droid. Worldgen is unaffected on four independent grounds; `guy762_KotORFaction_RogueDroids` RAIDS are broken, and that faction is the KotOR distress call's antagonist and a **v1 KEEP**. Routes: **(1)** drop the KotOR flesh type from our patch — one xpath, no assembly; restores tending on droids; loses vanilla EMP behaviour on them; does NOT affect our ion weapon (its guard moved to `IsMechanoid` on 08-13). **(2)** ~5 lines of Harmony in an assembly we already ship — a build, a deploy and a load; gives Humanlike pawns a relations tracker regardless of `IsFlesh`; keeps both the machine framing and working raids; it is the only route that also covers `current`, the previously-spawned droid, which is where the throw actually happens. **(3)** accept broken droid raids — free; the quest antagonist cannot raid past its first pawn. EXCLUDED: retargeting to vanilla `Mechanoid` — it would make our own ion weapon block them.
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

_Split out of `TODO.md` 2026-08-13 when the v1 line was drawn. Rewritten from 1,172
lines of argument into a register 2026-08-14._

**This is a REGISTER, not a workspace.** One compact entry per open v2 item: what it
is, who would own it, what it depends on, and whether v1 closing unblocks it. The
reasoning that produced an entry lives in the commit; the *spec* that came out of one
lives in `design/`, a skill, or the mod it belongs to — never here.

⚠️ **Do not work these while v1 is open.** If one blocks a v1 row, say so and it
moves back. **v2 starts the day v1's gate passes.**

---

## The register

| § | item | owner | blocked by | v1 close unblocks? |
|---|---|---|---|---|
| **0b** | Do enemies actually USE vehicles in raids? Three mods live or die on it | DECIDE | owner must identify "mother (HK Tank)" | no — offline-answerable today |
| **0c** | Alpha Neolithic reskin — the **4 vehicles after the sled** | BUILD | nothing | yes (BUILD is v1-committed) |
| **1** | Everything detonates — energy-density explosion model | unowned | nothing | yes |
| **3a** | Traps entry for the `-main`-branch `supportedVersions` trap | DECIDE/BUILD | nothing | no — 15 minutes, do it anytime |
| **3b** | W3 — re-scope `outer_rim_cherrypick_list.md` against the 1.6-native module | DECIDE | nothing | yes |
| **3c** | W4 — can Royalty noble pawnkinds take varied alien races? | DECIDE | nothing | no — offline from the def dump |
| **3d** | Four `INSPIRATION ONLY (1.4/1.5)` bullets the retraction missed | BUILD | nothing | no |
| **4a** | W7 — re-cast rebel gear onto the scavenger factions | DECIDE | "Junker Scrap-Warrens" has no defName | **no — needs the game up** |
| **4b** | U2 — balance-audit the live JDS droid weapons | DECIDE | nothing | yes |
| **4c** | U3 — build the **Free Droid Enclaves** `FactionDef` | BUILD | worldgen (faction #5 in the spec) | yes — and it unblocks C-v3 |
| **4d** | U4 — the rare Homestead Jedi `pawnGroupMaker` | DECIDE+BUILD | joint Sith/Jedi build (a retired seat's V-new) | yes |
| **5** | V2 Ideology lines — does the Jawaese actually reach Suppress/ReduceWill? | DECIDE | 🛑 owner STOP WORK | yes — and it needs the game up |

---

## 0b. [DECIDE] Do enemies actually USE vehicles against us?

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

## 0c. [BUILD] Alpha Neolithic reskin — the four vehicles after the sled

`sarg.alphavehiclesneolithic`. **The dog sled shipped** (eopie pair, `ad3e3c7`
`2a9a004`). **Four vehicles remain**, each 6 files = **24 PNGs**:
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
deferred to v2 — *"the energy-density explosion model — large,
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
orbital. The *the Galactic Empire*, the *Fallen Dominion*, the
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

### 3a. [DECIDE/BUILD] File the branch trap — it has caught two independent passes

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

### 3b. [DECIDE] W3 — re-scope the cherry-pick list

`design/Jawa/mods/outer_rim_cherrypick_list.md` (91 lines) is a hand-port plan whose
stated top priority is *"Empire trooper ladder + blasters + apparel + training hediffs"*.
That plan exists **only because we believed the module was unloadable**. It is
1.6-native and active, so most of §1 is dead work. **Keep §3** — Old Republic Sith as
the Empire's Sith-elite donor; that lift is still wanted.

⭐ **The defNames did not change between 1.5 and 1.6, only the filenames** — so the
SRC-verified defName list in that doc is still accurate. Nothing has gone stale; the
question is only *port vs load*.

### 3c. [DECIDE] W4 — the feasibility check the docs already owe

`cherry_picker_killlist.md:82` and `required_mods.md:687` both flag it unanswered: can
Royalty noble pawnkinds be given varied alien races, or do their generation rules block
it? **Answerable offline from the live def dump.** Fallback already written down — let
varied races appear naturally rather than guaranteeing them.

### 3d. [BUILD] Four stale `INSPIRATION ONLY (1.4/1.5)` bullets the retraction missed

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

### 4a. [DECIDE] W7 — re-cast the rebel gear onto the scavenger factions

**This is what converts a suppressed faction into a salvage layer.** Without it the
gear exists but nobody wears it. Duplicated as a retired seat's **V13** `[v2]`.

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

### 4b. [DECIDE] U2 — balance-audit the live JDS droid weapons

Two smell wrong on sight and need checking against `setting_physics.md`:
`JDSA_E-5S_Sniper_Rifle` fires a **4-round burst** (snipers should not burst) and
`JDSA_E-5_Blaster_Rifle` has **range 20** — shorter than a vanilla assault rifle, which
makes Separatist droids feel limp at exactly the range the fiction wants them dangerous.
Both are one-line `PatchOperationReplace` fixes in a mod we already load, on content the
player will actually meet.

### 4c. [BUILD] U3 — the droid faction we DO want is not in either mod

`faction_world_spec.md` §6 lists **Free Droid Enclaves** as faction 5 —
100% droid chassis, 0% biological — a *territorial* threat holding specific tiles,
hostile to the Empire because the founders were abandoned after the Clone Wars. That is
not "CIS battle droids still fighting a dead war", and **neither Outer Rim module
supplies it**.

Both candidate mods are pure XML with zero C#, and every droid race we need is installed
twice over (Droid Depot + JDS TSDA), so authoring our own `FactionDef` + thin
`PawnKindDef`s is **~200 lines and no assets**. Build it; do not adopt a substitute.

⭐ **This unblocks C-v3** — the restraining-bolt spec explicitly lands
with the Free Droid Enclaves *"whose `FactionDef` is unbuilt"*.

### 4d. [DECIDE+BUILD] U4 — the rare Homestead Jedi

`required_mods.md:596` permits it and `desert_world_design.md` §3B(7) supplies the why.
Unbuilt: the low-weight `pawnGroupMaker` entry on the Moisture-Farmer / Homestead faction
with the curated light + telekinesis VPE loadout. `OuterRim_MoistureFarmers` is live in
Outer Rim Core, so the vessel exists.

**Spec exists:** `design/Jawa/force_users_build_spec.md`. Owner has flagged Jedi-for-
Homestead and Sith-for-Empire as **one joint build** (a retired seat's V-new), so U4
should not be built alone.

⚠️ `force_users_build_spec.md` cites this item as `TODO_v2.md:1081`. **That line number
is dead as of this rewrite** — the item is §4d/U4. Three citations to repair, at `:8`,
`:1067` and `:1072`. Not my file.

---

## 5. [DECIDE] V2 Ideology lines — do the Jawaese lines reach Suppress/ReduceWill?

> 🛑 **STOP WORK.** Owner, 2026-08-13: *"Deepening this is a v2 item. Let's get stuff
> working that's a blocker to play first."*

**State: NOT failing — unverified.** SpeakUp is confirmed producing glossed Jawaese on
screen; `Suppress` is confirmed firing twice with Jawa initiators onto slaves. **The
text of a Suppress entry has never been seen** — every hovered line came back
`Chitchat`. The prisoner half cannot fire at all.

**Mechanism half is CLOSED** (2026-08-12): 14/14 Ideology defs carry our
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


## Retired from v1 — worldgen is manual (owner, 2026-08-14)
🔴 **DEAD, NOT PARKED — OWNER RULING 2026-08-15.** *"True worldgen is OUT of any
version, even v2."* Players receive a savegame holding one fixed, hand-made world;
they never generate anything. **v2 is not a parking space for worldgen** — the
entries below are recorded as history, not as future work. What survives is the
owner building that world by hand, once, and the design documents guiding him.


The owner makes a world by hand and saves it; we ship it as a fixed
resource. Everything below existed to shape the sea automatically.

⚠️ **Carried down from D-CRIT when that item closed, because it is a measurement and
not a plan:** `waterPct 25.0` was ONE seed; seed `sickle` read 16.74. If the sea is
ever measured again it is a **mode, not a constant** — never accept a world on a
single reading.

## ~~B2 Install the ocean-shaping mod~~ · ~~C15 Finish measuring the ocean (seed sweep)~~ · ~~C16 Score the ocean against its spec~~ · ~~D2 May we generate throwaway worlds to measure?~~ · ~~D4 Half ocean against a quarter — pick a fix~~

⛔ DEAD — owner ruled 2026-08-19, all in-game worldgen hooks stripped; the route is the live bridge, see ASHKARR_WORLD_DEFINITION.md §12. The `JawaSeaShaper` mod,
`sea_seed_sweep.py` and `worldgen_sea_spec.md` are deleted from the repo, the game's
Mods folder and `ModsConfig.xml`; do not rebuild any of them.


## C24 Retire `mandrake.missingartfixes` — has an order and one dependency
row:      —
spec:     Its seven texture pairs are md5-identical to the donors', so it was never a rendering hazard, and it is already inactive. 🔴 **Do not delete it blind: the blast-door brief still lives inside its `Source/`.** Move that out first, then retire the mod. Art fixing is parked, so this is housekeeping, not a fix.
verify:   the blast-door brief exists at its new home before the mod folder goes.
criteria: `mandrake.missingartfixes` gone from disk and from `ModsConfig.xml`, with the brief findable somewhere under `design/`.
state:    ready

## The Tusken water raid, as a behaviour

The Deep Desert Tribes' signature is a raid that targets water containers and
disengages once loaded. v1 ships the COMPOSITION only — a light, fast, chiefless
party. The behaviour needs a custom `RaidStrategyDef` with a C# worker class:
measured 2026-08-14, all 18 live `RaidStrategyDef`s are attack, breach, siege or
mod-specific, and none steals and leaves. Vanilla's `LordJob` layer is where the
steal-and-withdraw behaviour would have to be built.

## A salvage-built weapon tier, as blasters

The VWE-Makeshift weapons (5 guns, plus Makeshift: Re-Examined's revolver) were
cut for v1 on 2026-08-15 — not for balance, which they passed trivially, but
because they are bullet guns and this campaign's weapons are blasters. The idea
underneath them is still good: a Jawa clan that cobbles a working weapon out of
a wrecked speeder is exactly the fiction. v2 route is a reskin, not a re-adopt —
crude scrap-built *blasters* keeping Makeshift's unreliable random-burst verb,
which is what made the tier feel scavenged rather than merely weak. Art for it
already exists: the cut mods' own frames plus the pipe-and-tape VWE silhouettes
noted in `design/Jawa/mods/repurposed_graphics.md`.

---

## The Cantina Kitchen — Star Wars food is ANIMAL food

**Owner, 2026-08-15.** A whole mod of its own, and one of the better ideas on
this list.

**The observation it rests on:** Star Wars food is never abstract. It is a tank
of live things behind the bar. Somebody is always harvesting eggs out of an
aquarium full of semi-sentient trapped creatures and shaking them into a
cocktail, or tipping a squealing lizard down their throat whole. The cantina
scene sells the galaxy as *inhabited* precisely because its menu is made of other
inhabitants. That queasiness is the flavour, and it is completely absent from
RimWorld's food, which is nutrient paste and "fine meal".

**The build:** take the gourmet cooking mods already in the stack and repoint
their RECIPES — swap generic ingredients for animal products from real Star Wars
species. The mechanics are already written; only the inputs and the names change.

```
vanillaexpanded.vcooke        Vanilla Cooking Expanded
vanillaexpanded.vcookestews   Vanilla Cooking Expanded - Stews
vanillaexpanded.vbrewe        Vanilla Brewing Expanded
```

⭐ **The art problem is already solved.** `Star Wars Animal Collection` ships
**160 creatures with textures** — bantha, dewback, blurrg, gorg, kwi, peko-peko,
scavrats, pufferpig, aiwha, beldon, blixus, bogwing. That is a menu, an
ingredient list and a bestiary of things to keep in a tank, all drawn already.
Nothing here needs new art to prototype; it needs new `RecipeDef`s and new
`ThingDef` products.

**Threads worth pulling when this gets built:**

- **Live storage as a building.** An aquarium or holding tank that keeps the
  ingredient alive until use — the fiction is that freshness means *still
  moving*. RimWorld has no live-food container; this is the mechanically novel
  part and probably the mod's spine.
- **Eggs as the cocktail base.** Gorg eggs, kwi eggs, whatever lays. Brewing
  Expanded already has the drink chain to hang them on.
- **Whole-creature dishes** you eat live, with a mood consequence that depends
  on the ideoligion — reverent, indifferent, or horrified. The same dish reading
  three different ways by faith is the sort of thing Ideology does well and
  almost nobody uses.
- **The Jawa angle.** A scavenger clan does not keep aquariums; it eats what it
  finds. So the cantina kitchen is something the player ENCOUNTERS in Hutt and
  Deepwater settlements and has to decide about, rather than something they
  start with. That makes it a trade good and a moral texture rather than a tech
  tree.
- **The Deepwater Compact are the obvious supplier** — they already hold every
  oasis, marsh, river and coast on the map, and they already sell to everyone.

⚠️ Squarely `[v2]`. v1's food is Sekki Vosh and a cook stove, and that is
enough. Recorded now because the art audit made the ingredient list visible and
it would be a shame to rediscover it later.

---

## "They!" — giant ant colonies in the deep desert

**Owner, 2026-08-15.** Giant ants get colonies out in the sand, and they are
**very dangerous** — a hazard of the deep desert rather than a raid that comes to
you. You go out there and something is already living in it.

The fiction is free: `They! (Giant Ants)` is a 1954 monster-movie reference, and
giant ants in a desert is exactly where that film put them. On a thirst world
they read as a natural hazard, not a mod import.

**What ships today:** `sapiently.theyatomicmonsters` — 7 ThingDefs, 2 PawnKindDefs,
1 FactionDef (`GiantAnt_Faction`). Small, so the v2 work is mostly tuning and
placement rather than authoring.

**Threads worth pulling:**
- Settlement density and placement — deep desert and extreme desert only, away
  from the habitable ring, so they are something you travel INTO.
- Raid pressure tuned DOWN and defence tuned UP. The design is a nest you
  regret poking, not an enemy that visits.
- They are the natural counterpart to the Geonosian Foundry Hive: one insectoid
  power that is civilised and industrial, one that is simply fauna with numbers.
- Their tunnels are a reason to own the ion weapons and the vibroblades.

🔴 **THIS IS NOT A FREE v2 DECISION — IT HAS A v1 DEADLINE.**
`GiantAnt_Faction` sits on `WORLDGEN_FACTION_CHECKLIST.md` **Section 2**, marked
untick / drive to 0. **A faction absent at world creation can never be added
later.** If it is unticked at v1's worldgen, this dream needs a NEW WORLD to
happen at all.

⇒ **Decide it at the world screen, not in v2:** leave `GiantAnt_Faction` at 1 if
this idea is wanted, and accept that ants exist in v1 as unbuilt background;
or untick it and accept that v2 giant ants mean a fresh campaign.

---

## ⭐ THE SARLACC — rebrand Anomaly's pit gate. `[v2]`, and it is CONFIRMED buildable

**Owner, 2026-08-15.** The suspicion was right, and the defs are better than the
memory of them. 🔴 **v1 does NOT attempt this** — not the rebrand, not the
enabling. Recorded now because it is critical for v2 and because the evidence is
in hand today.

**What was measured, from the def dump:**

| def | type | what it says |
|---|---|---|
| `PitGate` | ThingDef + IncidentDef (Anomaly) | *"A massive, foreboding hole that connects the surface with a dark network of underground caves. It is possible to climb down into the caverns below."* |
| `PitGateExit` | ThingDef | the way back up |
| `Undercave` | **MapGeneratorDef and BiomeDef** | the place you arrive |
| `FleshmassHeart` | ThingDef + IncidentDef | *"It will keep growing until it consumes everything. The heart grows fleshmass spitters."* |

**And the Undercave's own generation steps settle it** — `Fleshbulbs`,
**`Fleshmass`**, `FleshSacks`, `Dreadmeld`. **The fleshy walls are not flavour
text; they are a gen step.**

⇒ **A pit that opens in the desert, that you climb down into, whose walls are
living flesh, with something at the bottom that grows until it consumes
everything.** That is the Great Pit of Carkoon with the serial numbers still on.
The rebrand is `label` and `description` work over art that already exists and a
mechanic that already ships — the cheapest large win in the register.

**The mapping, for whoever picks this up:**

- `PitGate` → **the sarlacc pit**. The desert opening.
- `Undercave` → **the gullet**. Descending is being swallowed.
- `Fleshmass` / `FleshSacks` / `Fleshbulbs` → the creature's interior.
- `FleshmassHeart` or `Dreadmeld` → **the sarlacc itself**. The heart's shipped
  description — grows until it consumes everything — is already the myth.

⚠️ **Two things NOT established, and they must be checked before building:**

1. **Whether `FleshmassHeart` actually spawns inside the Undercave.** It is a
   separate IncidentDef and the Undercave's gen steps list `Dreadmeld`, not the
   heart. The heart may be surface content. **Do not design around the heart
   being at the bottom of the pit until someone has looked.**
2. **How a pit gate is triggered**, and whether it can be sited deliberately —
   a sarlacc that appears at random is a monster, a sarlacc that lives in a known
   place is a *landmark*, and the landmark is worth far more.

🔴 **The blocker is a standing owner ruling, not a technical one.** Anomaly's
content is set to **ZERO** (owner, 2026-08-13) with the DLC left enabled so its
assets remain available. A sarlacc needs pit gates actually occurring, so v2 must
either raise Anomaly activity narrowly for this one incident, or author the
encounter itself.

⭐ **A possible route that avoids reopening Anomaly:** `CQF_Undercave` — **Custom
Quest Framework ships its own Undercave BiomeDef.** If CQF can place a map of its
own, the sarlacc could be an authored quest destination rather than a random
anomaly event, which also solves (2) above by making it a *place*.

**Why it is worth the trouble:** the campaign is set on a desert world of Jawa
scavengers, and the sarlacc is the single most recognisable thing that lives in
Tatooine's sand. It is also thematically exact — a pit that swallows and digests
slowly is the perfect opposite of a clan whose whole identity is *finding things
and taking them away*.

### 🔴 Addendum — the sarlacc REGIONS and the pearls (owner, 2026-08-15)

**The fiction is now canon; the implementation is still `[v2]`.** Stated plainly
because the two halves arrived in the same session and must not be conflated:

- ✅ **CANON FOR v1's WORLD.** There are **regions of the desert known for
  gigantic sarlacc pits.** Not a random event — *places*, known by reputation, the
  way a real desert has a named quarter nobody crosses. The owner is building the
  world by hand, so these regions can simply exist on the map from day one, and
  naming them costs nothing.
- ⛔ **STILL v2.** The rebrand of `PitGate` / `Undercave` / the fleshmass content,
  and the mechanical encounter. v1 attempts none of it, and Anomaly stays at zero.

⇒ **So v1 can ship the geography and the reputation without the monster.** A
region everyone warns you about, that does nothing yet, is not a broken promise —
it is foreshadowing, and it costs one label.

⭐ **THE PEARLS.** Sarlacc pits yield **wondrous pearls**, and they are a **major
quest reward** — the top of the reward table, not a trade good.

**Why this is the best idea in the whole sarlacc entry:** it converts the pit from
a hazard into an *economy*, and it gives the campaign a reward that is
- **sited** — it comes from a known place the player must travel to,
- **earned by risk rather than by grind**, which is the campaign's whole thesis,
- and **perfectly Jawa** — the clan's identity is finding things and taking them
  away, and a pearl pulled out of a thing that swallows is the purest possible
  expression of that.

**Owed before building:** what a pearl *is* mechanically (a quest reward item, a
crafting input, or a faction-tier trade good), and whether the pits regenerate
them. ⚠️ Do not make them farmable — a wondrous thing you can grind is not
wondrous.

---

### Anomaly playstyle — measured, 2026-08-15

**The question.** The campaign ruled Anomaly content to ZERO with the DLC left
enabled, so its assets stay available. Two v2 designs (the sarlacc built from
`PitGate`/`Undercave`/fleshmass, and the flesh vaults of
`design/Jawa/worldbuilding/the_forgotten_war.md` R-W2/R-W3) need Anomaly
*mechanics*, not just its art. Does the game have a "present but dormant" mode —
content real and reachable on purpose, nothing spawning by itself?

**Yes. It is `AmbientHorror` with the threat-frequency slider at 0%.**

**The def type is `AnomalyPlaystyleDef`** (`RimWorld.AnomalyPlaystyleDef`,
`ludeon.rimworld.anomaly`). There are exactly **three** defs, all in
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Anomaly\Defs\AnomalyPlaystyles\AnomalyPlaystyles.xml`:

| defName | label | `generateMonolith` | `enableAnomalyContent` | `overrideThreatFraction` | `displayThreatFractionSliders` | `displayStudyFactorSlider` | `alwaysShowCodex` |
|---|---|---|---|---|---|---|---|
| `Standard` | standard with monolith | **true** | true | false | true | true | false |
| `AmbientHorror` | ambient horror | **false** | **true** | **true** | false | true | **true** |
| `Disabled` | anomaly incidents disabled | false | **false** | false | false | false | false |

**Why `AmbientHorror` is the one.**

- **Nothing auto-spawns.** `GameComponent_Anomaly.AnomalyThreatFractionNow`
  returns `difficulty.overrideAnomalyThreatsFraction` outright when
  `overrideThreatFraction` is set. That feeds `Storyteller.AnomalyIncidentChanceNow`,
  which `StorytellerComp` uses as a plain `Rand.Chance` before it will draw from the
  anomaly incident pool at all. **At 0 the storyteller never looks at that pool.**
  The slider runs 0–1 and the game's own label for 0 is **"No major threats"**
  (keyed `AnomalyFrequency_None`). Default when you pick the playstyle is 0.15.
- **No monolith, ever.** `generateMonolith:false` makes `GenStep_Monolith.GenerateMonolith`
  and `ScenPart_MonolithGeneration.PostMapGenerate` both early-return, and
  `QuestNode_Root_MonolithMigration.TestRunInt` returns false — so the "Strange
  signal" quest that would otherwise deliver a replacement monolith cannot fire either.
- **The content stays fully alive.** `enableAnomalyContent` stays true, so
  `AnomalyStudyEnabled` is true (it returns true *because* there is no monolith),
  `ResearchManager.Notify_MonolithLevelChanged` force-reveals the anomaly research tab
  at game start, the entity codex is shown from turn one (`alwaysShowCodex`), and
  traders still stock tomes. Bioferrite, containment and the fleshmass tech line are
  all researchable.
- **And the gate our designs would trip on is off.** `IncidentWorker.CanFireNow`
  applies `minAnomalyThreatLevel` **only** `&& Find.Anomaly.GenerateMonolith`. With no
  monolith that check is skipped entirely, so `PitGate` and `FleshmassHeart` (both
  `minAnomalyThreatLevel 2`) can be fired deliberately — dev mode, a forced incident, or
  an authored quest — with no monolith progression to unlock first. **This is what
  unblocks the sarlacc and the flesh vaults.**

**The other two are wrong, and for different reasons.**

- `Disabled` zeroes the threat fraction *and* kills the mechanics: study, the anomaly
  research tab, the codex and tome trading all switch off with `enableAnomalyContent`.
  The art survives; nothing you could build a sarlacc out of does.
- `Standard` with both fractions dragged to 0 is the closest runner-up and still worse:
  the void monolith physically spawns on the starting map, and the `minAnomalyThreatLevel`
  gates stay live at tier 0, so an authored pit gate would need the monolith advanced first.

**Residual auto-spawn under `AmbientHorror`: one, and it is off on our world.**
`GameComponent_Anomaly.TrySpawnHarbingerTrees` queues `HarbingerTreeSpawn` directly on a
timer, bypassing the fraction. It is pollution-gated —
`GenStep_HarbingerTrees` sets `pollutionNone 0` and `pollutionLight 0` — so on an
unpolluted desert map the desired count is 0 and `IncidentWorker_SpecialTreeSpawn.CanFireNowSub`
refuses. Worth one grep after the first load, not worth a redesign.

**🔴 Locked at world creation — this is a decision with a deadline.**
`Dialog_AnomalySettings` is the only vanilla UI that writes `difficulty.AnomalyPlaystyleDef`,
and `StorytellerUI.DrawStorytellerSelectionInterface` only draws the "Anomaly settings..."
button that opens it inside `if (Current.ProgramState == ProgramState.Entry)`. The mid-game
page (`Page_SelectStorytellerInGame`) calls the same method, so the button is simply absent
once a game exists. **Pick the playstyle on the storyteller page or do not get it.**

What *is* changeable afterwards is the **threat-frequency slider**
(`overrideAnomalyThreatsFraction`) — but `StorytellerUI` draws the anomaly slider block only
when `difficulty.isCustom`. **So choose `AmbientHorror` AND Custom difficulty at creation**;
Custom is what keeps the dial adjustable later, and it lets us start at 0 and open the tap by
hand if v2 ever wants ambient dread. The value is serialised as `<anomalyPlaystyleDef>` in the
save, so a save edit or a Harmony poke could change it after the fact — that is a repair, not a plan.

⚠️ **One scenario trap:** `Scenario.standardAnomalyPlaystyleOnly` greys out everything but
`Standard`. Only the Anomaly DLC's own scenario sets it
(`...\Data\Anomaly\Defs\Scenarios\Scenarios.xml`). Our scenario must not.

📌 **Correction to an older note.** `infrastructure/state/EXPECTED_FAILURES_next_load.md`
S5 records `AnomalyFrequency_None` / `_VeryRare` / `_Rare` / `_Balanced` / `_Intense` /
`_Overwhelming` as the playstyle **defNames**. They are not. They are translation keys for
the slider's six frequency labels (`Dialog_AnomalySettings.FrequencyLabels`, thresholds
0 / 0.05 / 0.2 / 0.5 / 0.75 / 1). The save will read `AmbientHorror`, never `AnomalyFrequency_None`.

*Evidence: live def dump `AnomalyPlaystyleDef.json`, the shipped Anomaly XML, and a full
decompile of `Assembly-CSharp.dll` (`AnomalyPlaystyleDef`, `GameComponent_Anomaly`,
`Difficulty`, `StorytellerComp`, `StorytellerUI`, `Dialog_AnomalySettings`,
`IncidentWorker`, `QuestNode_Root_MonolithMigration`).*

### 🔴 The ship's NINE VOICES — `[v2]`, gated on in-game LLM generation

**Owner, 2026-08-15: all in-game LLM generation is v2.** This entry exists so the
v1 lore ruling does not quietly imply v1 dialogue work.

`the_forgotten_war.md` **R-W6** rules that the Jawa pantheon runs as nine
competing personas inside the ship, with **no integrating self** — no "and yet I
am me". `llm_voice_preauthoring.md` currently assumes a single Cradle-Mind
character. **Re-scoping it from one character to a CAST is the v2 job.**

**What v2 inherits, already decided and not to be re-litigated:**

- **No narrator.** A conversation with the ship is a conversation with **whoever
  answered**. Ask twice, a different god may take it, and neither will remember —
  or accept — that the other spoke.
- **No fragment says "my other selves."** They speak as rivals, or do not
  acknowledge each other at all.
- **The ship never describes itself.** Only the crew describe it.
- **The tenth strand — the Cradle's own initiator purpose — may not be a
  character at all.** Whether it can be addressed is open, and "no" is the more
  frightening answer.
- **The Rakatan kinship is below the tenants**, so no fragment can explain it.

⚠️ **v1 must not ship a unified ship-voice**, or this becomes a retcon rather than
a revelation. v1 expresses the nine through the satiation engine only — felt, not
heard.

## Programmatic worldgen — ⛔ DEAD, 2026-08-15 (was: parked in full)
🔴 **DEAD, NOT PARKED — OWNER RULING 2026-08-15.** *"True worldgen is OUT of any
version, even v2."* Players receive a savegame holding one fixed, hand-made world;
they never generate anything. **v2 is not a parking space for worldgen** — the
entries below are recorded as history, not as future work. What survives is the
owner building that world by hand, once, and the design documents guiding him.


Owner: *"WE WILL NOT PROGRAMMATICALLY generate the world, the user will do that
himself. Stand down all development of tuning the worldgen to function by itself
correctly for now. That's all v2."*

Everything aimed at making worldgen run correctly on its own goes here: the
tuning work, the automated-generation harness, and anything downstream of them.
The owner builds a world by hand and we ship it as a fixed resource.

## The four genes we stripped out of the xenotypes — what were they for?

Owner, 2026-08-15: *"Remove any genes from our implementation of the xenotypes that
aren't supported in our mod at this time. We will investigate what to do later."*
This is that "later". Nothing here is scheduled.

`mandrake.starwarsraces` ships six species with a gene removed, because the gene
resolves in **neither** the live def dump **nor** any of the three donors' XML on disk.
Stripping was measured safe — no species empties, none loses its head-forcing gene —
but each lost something the donor thought was part of that species.

| gene | species | what it plausibly did | where it might come from |
|---|---|---|---|
| `Force_Gene_LatentForceUser` | Ithorian · KelDor · Mirialan | Force sensitivity | Not in BTD, SWX or Outer Rim — walked all three. Belongs to a Force mod we do not run |
| `OuterRim_ForceAdept` | SithMassassi | Force sensitivity, stronger | same |
| `OuterRim_ForceInsensitive` | Rakata | explicit Force *immunity* — arguably the Rakata's defining trait in canon | same |
| `guy762_AbilityGene_cloak` | Defel | active cloaking, the Defel's whole identity | **On disk**: `SWX/1.5/AdditionalMods/KotORWeapons/Defs/AbilityDefs_defelcloaking.xml` |

**Two different problems wearing one label.**
- **The three Force genes are a CONTENT question, and the current answer is no.** This is
  a Jawa scavenger campaign on a desert world; adding a Force mod to satisfy a gene
  reference is a dependency the campaign never asked for. Reopening this means deciding
  the Force is in the setting at all — that is a big call, not a gene fix.
- **`guy762_AbilityGene_cloak` is a TOOLING question and is cheap.** The gene exists; the
  generator cannot see it because `donor_xml_files` skips `AdditionalMods` and `1.5`.
  Widening it to **index** those folders (never to copy them — the skip list protects the
  copier for good reason) would recover it. `Common` and `Common_Old` are worth the same
  look; D-CHK2 proved they hold real art the migration needed.

⚠️ **Do not fold these two together again.** One needs an owner ruling about the setting;
the other is twenty lines in a path filter.

## Regenerate the races from scratch — all genes, text and art, authored as ours

Owner, 2026-08-15, filed to v2 explicitly. **Not v1. Nothing here is scheduled.**

Today `mandrake.starwarsraces` is a **migration**: the generator composes each species
from the three donors' XML and copies their PNGs. Every species is therefore only as
good as the donor it was lifted from, and the whole of today's trouble is downstream of
that — genes that resolve nowhere, head-type genes one donor carried and another did
not, art the copier never fetched because a path field was not on its rewrite list,
and a catalogue that shrinks when the donors are switched off.

**This item is the other option: stop migrating and author the set.** A full
regeneration of the races **based on what is already there** — the current roster and
its species as the design input, not a blank page.

In scope when it is taken:
- **Genes** — authored per species rather than unioned from donors, so a species owns
  its traits and nothing is inherited by accident. The 4 stripped genes come back as a
  deliberate yes or no.
- **Text** — labels, descriptions and the 48 RulePackDefs / name word-lists, written for
  this campaign's voice rather than inherited from three unrelated mods.
- **Graphics** — heads, head attachments, gene icons and backgrounds generated as one
  consistent set, which is the only real fix for the magenta boxes and the
  generic-reptile-head class of defect rather than patching paths one at a time.

⇒ **The prize is ending the donor dependency completely.** `gen_races_mod.py` exists to
free us from BTD, SWX and Outer Rim, but it still reads them every run — so the mod
cannot be rebuilt without them installed. An authored set can.

⚠️ **This is large.** 69 species, 114 genes, 104 head types, 713 textures at today's
count. It is a v2 project, not a v2 chore, and it should not be started as a fix for any
single v1 defect. See also the stripped-genes item above, which it would subsume.

## ~~⭐ The Ortolan~~ — ✅ ORTOLAN IS BACK IN v1, CONFIRMED IN GAME 2026-08-15. Five others still deferred.

Owner, 2026-08-15: *"Herglic is now v2. So are Anzati, Muun, Sithz, Togorian. **The
Ortolan we sorely want them**, but for now they are also in v2. Mark the Ortolan as a
high priority for v2."*

🔴 **SUPERSEDED FOR THE ORTOLAN, 2026-08-15.** Owner, live, looking at the 70-race grid
on the scratch map: *"We have a working Ortolan! Make that as done for now and confirmed,
not v2 after all."* ⇒ **`RimMandrakeOrtolan` is v1, DONE and CONFIRMED.** It spawned in
the 70/70 grid and the owner examined it on screen. Do not restore it — it is already
here. Strike it from any v2 species list.

**The other five below remain deferred**, and among them the ordering note no longer
applies since its subject has left the list.

| species | xenotype defName | pawn kind |
|---|---|---|
| ⭐ **Ortolan** | `RimMandrakeOrtolan` | `RimMandrakeOrtolan_Kind` |
| Herglic | `RimMandrakeHerglic` | `RimMandrakeHerglic_Kind` |
| Anzati | `RimMandrakeAnzati` | `RimMandrakeAnzati_Kind` |
| Muun | `RimMandrakeMuun` | `RimMandrakeMuun_Kind` |
| Sithz | `RimMandrakeSithZ` | `RimMandrakeSithZ_Kind` |
| Togorian | `RimMandrakeTogorian` | `RimMandrakeTogorian_Kind` |

⚠️ **`Sithz` is `SithZ` in the def — capital Z**, and it is NOT
`RimMandrakeSithMassassi` or `RimMandrakeSithKissaiPureblood`. Those two are different
species and they stayed in v1.

**What restoring them will need, so the next reader does not re-derive it:** only
Herglic sits in the generator's 65-species roster; the other five ship from a different
write path, so they were never a single mechanism to begin with. Herglic additionally
failed its own build with *"source carries no genes"* — a cause nobody has measured, and
it is still unmeasured today. Restoring Herglic means diagnosing that first.

This is also the item the full-regeneration entry below would subsume: if the races are
ever authored rather than migrated, these six come back as authored species and none of
the above matters.

### Restoring the Defel cloak needs four defs, not one

Measured 2026-08-15 while re-testing the strip ruling.
`guy762_AbilityGene_cloak` does not travel alone — its donor file
`SWX/1.5/AdditionalMods/KotORWeapons/Defs/AbilityDefs_defelcloaking.xml` declares **four**
defs that work as a set:

| def type | defName |
|---|---|
| `GeneDef` | `guy762_AbilityGene_cloak` |
| `AbilityDef` | `guy762_StealthDeactivate_defel` |
| `hediffDef` | `guy762_GeneAbility_defelcloak` |
| `HediffDef` | `guy762_StealthField_defel` |

⇒ Migrating the gene alone would produce a gene that grants an ability that does not
exist. Take the set or leave it.

⚠️ Note the donor's own typo: one is `<hediffDef>` lowercase, one is `<HediffDef>`. Def
type names are case-sensitive in RimWorld XML, so the lowercase one is very likely dead
in the donor too — check before assuming the cloak ever worked as shipped.

## Desert creatures for the other four animal-drawn vehicles (was B62)

Deferred out of v1 by the owner, 2026-08-15: *"defer adding any additional art to
B62 for v2. Leave it just as is and keep deployed."* The eopie sled (`4f3afc7`)
shipped and stays; these four did not.

**Scope is exactly four vehicles**, and the test is a def tag, not a look at the
art: Alpha Vehicles - Neolithic ships 12 vehicles and exactly five carry the stat
`AV_TractionAnimal` — Chariot, WarChariot, CoveredCarriage, OxCart, DogSled. Those
five are exactly the five with an animal drawn into the texture. DogSled is done.
⛔ Do not re-derive the list from "the mask has a black region" — seven of twelve
have one and five of those have no animal in them.

| vehicle | donor shows | assign | why it is cheap or dear |
|---|---|---|---|
| `AV_OxCart` | 2 oxen, yoked abreast | **bantha ×2** | cheapest — horns, hump and broad muzzle are already the silhouette. Repose and recolour, not a redraw |
| `AV_Chariot` | 1 horse | **dewback ×1** | smallest animal share of the canvas (~28%) |
| `AV_WarChariot` | 2 horses | **dewback ×2** | reuses the Chariot's body at two instances, darker palette — the two chariots amortise one build |
| `AV_CoveredCarriage` | 2 horses abreast | **ronto ×2** | dearest — reptilian slab body, long neck, small head is a real body swap |

Donor sprites are all live PawnKindDefs in `Mlie.StarWarsAnimalCollection`
(ws `3497316713`), but ⚠️ **its art is in an AssetBundle, not loose PNGs** —
`AssetBundles/Mlie_StarWarsAnimalCollection`, assets `swanimals/<Name>/<Name>_south`.
There is no `Textures/swanimals/` directory. Extract with
`skills/reading-rimworld-graphics` before anything can be composited.

**Two facts worth keeping, because both were bought the hard way:**

- 🔴 **THREE defs share each texPath, not two.** The `Vehicles.VehicleBuildDef`
  blueprint carries its own `<label>` and `<description>` and the sled pass missed
  it. 13 defs across the five vehicles need label and description.
- 🔴 **Art reaches every def naming a path; `<color>` is per-def.** If a vehicle's
  `<color>` changes, its `VFEPD_*` twin must change in the same file or the sled
  bug reproduces exactly. Default here is to leave all four colour triples alone —
  the donors are already tan/brown and the art pass alone answers the brief.

⇒ **CHECK C41 rides this, and is therefore v2 too.** It needs 24 PNGs; the mod has
12, all of them the sled.

## Yoder the Force Gremlin has hair — v2 fix

Owner, 2026-08-15, live off the 70-race grid: *"Oops. Yoder has hair... that's a v2 fix."*

`RimMandrakeYoderForceGremlin` renders with hair it should not have. Owner classed it v2
himself in the same breath, so it is **not** a v1 defect and no v1 item should be opened
for it. The species spawns and is otherwise fine — this is cosmetic only.

## Race art polish — the whole remainder, parked as one v2 item

Owner, 2026-08-15, after examining all 70 races side by side on the scratch map:
*"I think we can mark all the races as visually good enough for v1, with the remaining
missing art for v2 improvement. Let's close out race appearance issues for now."*

**v1 is settled: all 70 races are visually good enough.** Everything below is polish and
none of it is a v1 defect. Do not open a v1 item for any of it.

| species | what |
|---|---|
| `RimMandrakeGand` | missing art |
| `RimMandrakeSelkath` | missing art |
| `RimMandrakeChagrian` | missing art |
| `RimMandrakeYoderForceGremlin` | has hair it should not |
| the four known magenta species | magenta boxes, recorded at `9d10aec` |

✅ **The missing-art three are CONFIRMED and CONSISTENT** — owner, 2026-08-15:
*"The missing art races are consistent: Gand, Selkath, and Chagrian are the ones with
missing art."* An earlier note here wondered whether one of them was a misread, because
the two grids named different second species. It was not: **all three are real, and the
list is complete.** Take the three at face value; no re-survey is needed.
⛔ The log will not find these: the harvest's texture-path check reads 0 and fires only
when EVERY direction is missing, so a partial set is silent. This is an eyes-on job.

## Lightsabre position during melee — v2

Owner, 2026-08-15: *"move the lightsabre position bug to v2"*.

Lightsabres sit significantly displaced from where they should be **during an attack** —
not merely on draft. The owner's report is firsthand and it is why
`com.yayo.yayoani.continued` is switched off. ⛔ Do not propose re-enabling Yayo.

**Nothing is missing from the build.** 14 lightsaber `ThingDef`s are live, and one was
equipped and rendered correctly in game on 2026-08-15. This is purely how the weapon is
positioned mid-swing.

⚠️ What v2 should know before trying to see it again, so the attempt is not repeated
blind:
* **No Yayo-ON comparison shot exists.** "More reasonable" is comparative and the only
  arm we can currently produce is Yayo-OFF. Either accept a baseline or capture the
  other arm deliberately.
* **The bridge cannot order an attack**, so the swing frame cannot be staged
  unattended — drafted pawns hold at `Wait_Combat`, `jawa/order_pawn` issues a GOTO,
  spawned hostiles have no lord, and a real raid plus 5,600 stepped ticks produced no
  engagement. Filed as `bridge-cannot-order-a-melee-attack-3f8c21`. Ten seconds of a
  human right-clicking an enemy would do it.
* Equipping is solved: `rimworld/select_pawn`, then
  `Actions\Equip primary (selected)...\Force_Lightsaber_Custom`.

## Five CHECK items deferred to v2 — owner's close-out, 2026-08-15

The owner walked the whole CHECK queue and ruled item by item. These five leave v1.
None is abandoned; none is scheduled.

| item | what it is | why it can wait |
|---|---|---|
| **C42 (.rid half)** | Does `The Salvation.rid` load with all **101 precepts**? | ⚠️ **This one bakes at world creation** — the generated world keeps whatever the file loads with, and dropped precepts are silent. The owner deferred it knowing that. The `.xtp` half is separate and still tracked in DECIDE. |
| **C21** | Follow The Claim quest from rumour to actual **resolution** | Registration already works; only end-to-end resolution is unproven, and that needs real playtime rather than a bridge test. |
| **C35** | Do the six factions' `xenotypeSet`s read back as Star Wars species, not the vanilla ones inherited from the abstract parent? | The fix is deployed and C37 forced 70/70 xenotypes correctly (70 = the BTD roster; we now define **71** under `src/`, and 139 XenotypeDefs are live at 578 mods — `canon.yml > species`), so this is confirmation, not discovery. If it HAS failed, faction members spawn as vanilla xenotypes. |
| **C41** | Four more animal-drawn transports | Nothing to test — **B62 is unbuilt**: 12 PNGs on disk against 24 needed, and its 13 defs are absent. Pure content addition. |
| **C31** | Four Jawa pawn kinds (`Jawa_Colonist`, `Jawa_Tribal_Scavenger`, `_Slinger`, `_Elder`) | They are **silently discarded at load** on a bad `ParentName`, so those four types do not exist in game. Blocked on BUILD's fix and deferred with it. |

**What stayed in v1**, for contrast: C17 (untick the fiction-breaking factions at worldgen
— seen once, unfixable after), C40 (three deployed Jawa fixes, incl. the
`canGenerateAsCombatant` flag without which a Jawa faction cannot field a fighter), and
C38 (fast plant growth, which the owner is ruling on directly).

## Boiling water and boiling rain as our own content (was B64)
Owner, 2026-08-15: we are not using the boiling biome. Building our own boiling
water/rain and dropping ReGrowth: Boiling would reopen chain step 8, which is
ratified. Spec survives at `design/Jawa/mods/REGROWTH_BOILING_LIFT_SPEC.md`.

## Our own XenotypeDef set (was D23)
Owner, 2026-08-15: *"We are shipping with the ones we have right now, unchanged."*
v1 ships on the donor packs as they load today. The v2 ambition is unchanged —
own `XenotypeDef`s assembled from donor genes, donors stood down by zeroed
generation weight, so BTD Remix's load-time dedup stops deciding which version of
a species survives. `FACTION_SPEC.md` R27's 31 `BTD_*` names are the scope.

## Second pass on the xenotypes (was D28)
Gated on the above. Nothing to do until v1's set is replaced.

## Moons and moonlight
Owner, 2026-08-15, parked on arrival — *"Decide on Moons and moonlight in the game,
though that might make it hard for tidal locking."* Unresolved tension: the campaign
planet is tidally locked (`7f.alienworlds.tidallylocked`), and a moon's light cycle
may not compose with a fixed day/night hemisphere. Not v1, not scheduled.

## The 2026-08-15 v2 triage — nine items moved out of v1 in one pass

Owner's ruling, walking the BUILD queue item by item. **The test applied was "does
worldgen close the door on this?"** — everything below is read live from defs on
every load, so it can be added to an existing campaign later and will simply start
working. Nothing here is refused; it is sequenced.

| item | what it is | why it was safe to move |
|---|---|---|
| ~~**B61**~~ | ~~The frozen Ancients look Rakatan~~ | ⛔ **RETURNED TO v1 — owner, 2026-08-20:** *"let's go all out for v1 here."* The Rakata are named as the ancient enemy and the sleepers are Rakatan. Spec: `design/Jawa/worldbuilding/ANCIENTS_AS_RAKATA_SPEC.md`. **Do not action from this row** |
| **B64** | Author our own boiling water and rain, drop ReGrowth: Boiling | The boiling biome is already ruled out of the campaign, so nothing in v1 consumes it |
| **B57** | The lasso becomes a strength gene, not a pickup weapon | Balance, reversible at any time |
| **B39** | Every place a design doc disagrees with the frozen mod list | Doc hygiene, zero world effect |
| **B37** | Two docs cite evidence files that no longer exist | Doc hygiene, zero world effect |
| **nomatch-add…-7b1e4c** | Validator: flag an add-if-missing `<nomatch>` whose container is only INHERITED | Would catch this class prospectively; the one instance we had is already fixed |
| **B35** | Move the repo to the agreed folder layout | Housekeeping, disruptive mid-flight |
| **B36** | Rename the mods and tool namespace, 35 files | ⚠️ Touches LOAD ORDER — not worth disturbing before a once-only worldgen |
| **B44** | Rename vanilla mechanoid and insect factions | Owner: *"Keep mechanoid and insect for now, looking into changing them is v2."* |

**Also v2, ruled the same day:**

- **B67(b)** — teach `cherrypick_build.py` to validate the 1,308 live Cherry Picker
  keys against a def dump. 🔴 **Carry this risk knowingly:** a misspelled cut key is
  silently inert, and the dump cannot detect it — *a cut that worked is absent from
  the dump, so absence proves nothing.* Cherrypicking is frozen so no new bad keys
  can appear; an existing one just means that thing was never really cut.
- **The four companion-DLL bridge tools** — `jawa/inspect_string`,
  `jawa/gravship_status`, `jawa/set_thing_rotation`, `jawa/can_place`. Deferred, not
  refused; each is a measured gap. No shutdown window is held for them.
- **`bridge-cannot-order-a-melee-attack-3f8c21`** — nothing on the bridge can order an
  attack, so any "what does it look like DURING an attack" item is uncollectable
  unattended. C43 left v1, so nothing waits on it.

⭐ **Stayed in v1: B53**, the 48 pawn kinds. It is technically deferrable — pawn kinds
resolve at raid time, not at worldgen — but flat, samey raids are most of what a first
session shows. **Sequenced AFTER worldgen**, since `FACTION_SPEC.md` names zero
`Jawa_<Faction>_<Role>` kinds and nothing bakes.

## v2 concept: Star Wars domestic animals as map mutators

Owner, 2026-08-16: *"Create map mutators that feature Star Wars domestic animals rather
than cows, chickens, rats."*

The gap is already measured. `VEE_DomesticatedEscapees` and `VEE_NobleSteeds` occur **75
times each** in a generated world and put chickens, pigs and horses on an Outer Rim
planet. They were the closest calls in the whitelist review — the *beat* is excellent
(feral stock gone wild around dead moisture farms) and only the species are wrong.

⇒ Author our own `TileMutatorDef`s on the same shape, with `additionalWildPlants`'
animal equivalent pointed at **eopie, bantha, dewback, ronto, happabore**. We already
ship the eopie (`AV_DogSled` reskin, C39) and `mlie.starwarsanimalcollection` is active
with 11 mutators of its own, 4 of which already occur — so the species exist; what is
missing is the mutator that PLACES them as domestic escapees.

Worth pairing with a landmark: an abandoned moisture farm with its herd still on the
tile. That is a Jawa salvage hook, a food source and a story in one map.

## v2 concept: iteratable map generation against validator criteria

Owner, 2026-08-16: *"Iteratable mapgen to satisfy validator-style criteria as specified
in all of these mutators and world defs... or just more manual curation of course."*

The criteria already exist and are machine-readable. Every `TileMutatorDef` carries
`minHilliness`/`maxHilliness`, `averageTemperatureRange`, `pollutionRange`,
`coastSidesRange`, `canSpawnOnRiver`/`OnRoad`/`OnLandmark`, plus density factors and
`preventGenSteps`. That is a constraint system nobody is checking against.

The loop: **generate → score the result against the constraints we care about →
adjust → repeat**, the same shape as the validators already in this repo
(`validate_patch.py`, `validate_ideoligion.py`, `validate_save_artifact.py`). Scoring
is cheap offline: `worldmap.py` reads every tile's biome, elevation, temperature,
rainfall and hilliness, so "does this planet actually have a habitable ring 40-57° from
the substellar point" is a function, not an opinion.

🔴 **RULED BY THE OWNER, 2026-08-21: the habitable ring is 40–57° of arc.** ✅ **SETTLED — this paragraph is dead.**
~~40–57 is not settled, and neither is 34–57.~~ It is 40–57, at
`canon.yml > world.habitable_ring_arc`, and `HABITABLE_RING_ARC_RULING_1` is closed.
⛔ **34–57 lost.** It was provisional on the strength of `ashkarr_paint.py:76-77`, the code
that sited the player's home — a siting decision, not a measurement. A scorer built against
40–57 is now legitimate.

🔴 **Scope note, and it needs the owner's word before anyone builds it.** Automated
**WORLDgen** is OUT of every version by his own standing ruling, and v2 is explicitly not
a parking space for it. Two readings survive that:
- **LOCAL map generation** (the 250x250 colony map) is not covered by the worldgen ban at
  all, and is where mutators actually express themselves. Safe.
- **A validator with no generator** — score the hand-built world, report what fails, and
  let the owner fix it by hand. That is "more manual curation", his own alternative, and
  it contradicts nothing.
⇒ Record both. Build neither until he picks.

## v2 concept: no rain on this planet, except something violent in the high mountains

Owner, 2026-08-16: *"banning rainfall on any biome except those that occur in high
mountain areas where instead it is torrential, boiling, red, or otherwise violent and
bizarre, otherwise we have to add mutators everywhere to enact this (v1 approach)."*

Rain should not exist on a Tatooine-grade world. The one exception is altitude, and what
falls there should not read as weather — **torrential, boiling, red, bizarre**. Rare,
altitude-locked, and frightening.

**Why this cannot be done with mutators.** v1's only tool is hanging a mutator on every
dry tile and another on every violent one — thousands of placements to state one
planetary rule, and all of it lost on regeneration. The rule belongs in the biome and
weather defs.

**What is already established**, so the eventual spec starts from fact: rainfall is a
per-tile array of raw **mm/year**, writable offline and verified (`worldmap.py`; a test
world spanned 233–2584 mm). **Biome selection keys off rainfall**, so zeroing it changes
which biomes can exist — the real lever and the real risk. Altitude is computable from
`tileElevation` and `tileHilliness`, so "high mountain" needs no hand-drawing. The
tidally-locked mod rewrites temperature but **not** rainfall, so there is no conflict.
`VEE_FertileRains` already occurs 124 times and would have to be out-ranked.

Open questions the spec must answer: zero or a low floor (zero may make biomes
ungenerable); WeatherDef vs GameCondition vs biome property (a mutator is the shape we
are rejecting); what "boiling" and "red" do mechanically rather than cosmetically;
whether the Jawa economy still gets its plant cover; and whether the wet band is
**visible from orbit**, or the rule never reaches the player.

Queue pointer: `infrastructure/state/queue/DECIDE.md` → `D-V2-RAIN`.


---

## Parked out of BUILD's queue, 2026-08-19

Five items the 2026-08-15 triage marked v2 or withdrew, moved here verbatim when
the queue was stripped of everything closed. Nothing here is scheduled.


## B25 Mod-list chores to do in one pass while the game is closed
row:      0
spec:     (a) Pin the 6 `loadBottom`+`loadAfter` userRules — order is correct today but rides a tie-break, not a constraint; `loadBottom` outranks `loadAfter`, keep it only on `rimdefdump`. (b) Run `src/RimMandrake/Utils/refresh.py` (wants the game down). (c) ⛔ **DEPRECATED — owner's ruling 2026-08-15: "We are keeping the mechanoids. Deprecate any action about turning mechanoids off."** Do not run it, do not revive it, do not re-derive it from the O-v2 line in any other doc. The former spec (Cherry Picker removal of the mechanoid defs and the `Mechanoid` faction) is dead; the guards it carried are now moot but were: keep Alpha Mechs `sarg.alphamechs`, and `matathias.ruthlessmechanoids` is the gravship pursuer redirect, not a mech mod. Per-mech ART curation against `design/Jawa/worldbuilding/review/mech_register.html` is a SEPARATE question and is still the owner's to make — this ruling kills the wholesale cut, not that review. (d) **O-v3** — enable `vanillaexpanded.vwel` (ws `1989352844`, installed and inactive) and dump its weapon `ThingDef`s in TWO SEPARATE tiers: `salvaged` (pistol/rifle/shotgun/sniper + `unstable` projectile variants) and `ultratech` (incl. a laser sword and a tesla gun). The split is load-bearing for the design (`design/Jawa/worldbuilding/ship_legacy_armoury.md`).
verify:   ~~read `ModsConfig.xml`'s mtime before writing~~ — RETIRED by the owner
          2026-08-15 (`0460ee4`, now in CLAUDE.md): *"You NEVER have to ask if
          RimSort is open. It does not autosave, and I will never save without
          asking. Nobody blocks on RimSort or game close for config files of any
          kind."* Write it, game up or down. Assemblies are the only thing that
          needs the game down, because the OS locks them.
          Real verify: `ModsConfig.xml` parses, the activeMods count moves by
          exactly the intended delta, and zero listed-but-missing
          (`src/RimMandrake/Utils/check_load.py`).
criteria: the game reaches the main menu with the new list; the two weapon tiers exist as separate dumps.
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

## mod-list-shows-descoped-removals-9c4e12
row:      10
spec:     Owner broadcast, 2026-08-15: *"Game is down, offline work may begin. Stage
          the next game load and prepare additional content. Ensure the mod list shows
          the many removed mods correctly (BUILD)."* Relayed by REP with the state
          measured at relay time, so you do not re-measure the settled half:

          ALREADY CORRECT — live `ModsConfig.xml` (mtime 2026-08-15 11:58:30, 575
          active) and `deployed/config/v1_freeze/ModsConfig.xml` are IDENTICAL,
          including order, and 0 listed packageIds are missing from disk. All six
          Descoped rows of `design/Jawa/mods/CHERRYPICK_AGENDA.md` are absent from
          both: `VanillaExpanded.VanillaAnimalsExpanded`, `zal.giantsnake`,
          `regrowth.botr.boilingforest`, `guppyfacesarecute.skunks`,
          `abrolo.grimstone.beasts`, `redmattis.sapientanimals`.

          WHAT IS NOT DONE, and is this item:
          1. ✅ **ANSWERED — OWNER 2026-08-15: they stay INACTIVE BUT SUBSCRIBED, and
             this half is CLOSED.** Do not unsubscribe them and do not file an item to.
             ⚠️ The hazard the line below described is real and is now ACCEPTED, not
             fixed: a RimSort re-sort or a Steam action can re-add them with no warning.
             ⇒ The mitigation is the freeze copy, not unsubscribing — `ModsConfig.xml`
             and the freeze must stay identical, which item 2's verify already checks.
          2. Their defs are gone but references to them are not. Pre-record the
             `Could not resolve cross-reference` signatures the next load will throw
             into `infrastructure/state/EXPECTED_FAILURES_next_load.md` BEFORE launch —
             a missed one costs a load, a duplicate costs nothing.
          3. `RG_BoilingForest` and the six `BoilingWater*` terrains are named by
             B64 as replaced by our own authoring; confirm nothing still points at
             the dead defNames.
          🔴 Game is DOWN and confirmed down (`tasklist.exe`, no `RimWorldWin64.exe`),
          so this is the window. But `ModsConfig.xml` was written at 11:58 today and
          REP has asked the owner whether RimSort is open — read its mtime again
          immediately before any write, per NEXT_RELOAD §1b.
verify:   `ModsConfig.xml` live and freeze still identical after your pass; the six
          packageIds absent from both; every signature you expect from the removals
          present in `EXPECTED_FAILURES_next_load.md` before the load is called.
criteria: the next load throws no unexpected `Could not resolve cross-reference` that
          traces to one of the six removed mods.
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

## B66 🔴 Two generator defects, one regenerate — RIDE THIS WINDOW or lose a load
row:      9
spec:     🔴 **OWNER RULING 2026-08-15, AND IT IS PART (c) OF THIS ITEM — do it FIRST,
          because it changes what a correct run produces:**
          *"Remove any genes from our implementation of the xenotypes that aren't
          supported in our mod at this time. We will investigate what to do later."*

          ⇒ **STRIP the unresolvable gene; BUILD the species.** `pick_species` currently
          SKIPS a species when any gene fails `_gene_exists` — that is the behaviour being
          overturned. **No species is ever dropped for a gene again.** Filter `glist`
          instead of `continue`-ing, and keep `skipped` for causes that are not genes.

          **The complete set, measured by DECIDE at `e4d6040` — 4 genes, 6 species, one
          bad gene each. Enumerated in full; the skip message's `missing[:3]` truncation
          is hiding nothing.**

          | gene to strip | species |
          |---|---|
          | `Force_Gene_LatentForceUser` | Ithorian · KelDor · Mirialan |
          | `OuterRim_ForceAdept` | SithMassassi |
          | `OuterRim_ForceInsensitive` | Rakata |
          | `guy762_AbilityGene_cloak` | Defel |

          ✅ Measured safe — no species empties and **none loses its head-forcing gene**:
          Defel 18→17, Ithorian 16→15, KelDor 15→14, Mirialan 11→10, Rakata 7→6,
          SithMassassi 14→13. (Mirialan and SithMassassi have no head-forcer before OR
          after — pre-existing, D-CHK2's finding, not caused by this.)
          ⇒ Roster **57 → 63** of 64 buildable. ⚠️ **Herglic stays out** — "source carries
          no genes", a different cause, still unmeasured. Do not let the recovery hide it.

          📌 **Emit the strip list as generator OUTPUT** — one printed line per stripped
          gene per species — so the record is produced by the run and cannot drift from
          what shipped. That print IS the input to the later investigation.
          ⛔ **Do NOT widen `donor_xml_files` to index `AdditionalMods` in this item.** I
          directed that earlier to rescue Defel's cloak gene; the owner's ruling strips it
          instead, so the widening moved to the later investigation. Real finding, wrong
          moment.
          ⛔ **`_guard_species_regression` stays and is not weakened.** This ruling makes
          the catalogue GROW, so the guard should never fire — if it does, stop.

          ─────────────────────────────────────────────────────────────────────────────
          (a) and (b) below were routed 2026-08-15 from CHECK's D-CHK2 and D-CHK3.
          ⚠️ **"One file, one re-run, one redeploy" was DECIDE's framing and it was
          WRONG** — that premise is what sent a partial run at a mod live in `ModsConfig`.
          BUILD was right to stop and escalate. Treat (a), (b) and (c) as three changes
          to one file that share a single redeploy, not as one trivial regenerate.
          do not split them and pay the deploy twice.
          File: `src/RimMandrake/Utils/gen_races_mod.py`.
          Mod:  `src/Jawa/RimMandrake_StarWarsRaces` (`mandrake.starwarsraces`).
          ⏱️ **Pure XML + loose PNGs, no assembly.** It needs no shutdown window of
          its own, but it MUST be regenerated and redeployed before the game relaunches
          or `NEXT_RELOAD.md` §5 L0 photographs four species that are magenta for a
          reason we already know, and the next load re-asks a question answered today.

          (a) **THE PATH-REWRITE LIST IS INCOMPLETE — 19 defs, 27 dead paths.**
          `TEXFIELDS` at `gen_races_mod.py:148` and `TEXCONTAINERS` at `:151` are the
          whole list, and four families are missing from it:
            · `texPathFemale`                    — add to `TEXFIELDS`
            · `backgroundPathEndogenes`          — add to `TEXFIELDS`
            · `backgroundPathXenogenes`          — add to `TEXFIELDS`
            · `<Male>` / `<Female>` **inside** a `BigAndSmall.PawnExtension` `headPaths`
              — NOT a flat field; `TEXCONTAINERS` handles `<li>` children only, so this
              needs the container walk to descend into named children too
          Plus one hand path outside the generator:
            · `Pawn/HeadAttachments/gand/mask_yuun` in
              `src/Jawa/RimMandrake_StarWarsRaces/Defs/Misc/SW_Support.xml`
          🔑 **The texture copier is driven from the SAME list** (`copy_textures`,
          `:597`, fed by `texhits` from `rewrite`, `:478`). A field it does not rewrite
          is a texture it never copied — so three of these need the ART copied as well,
          not just the path fixed:
          | path | art state | action |
          |---|---|---|
          | `Pawn/HeadType/gand/gand`, selkath heads | 6 files PRESENT | rewrite path only |
          | `OuterRim/Genes/Headbone/ChagrianF` | NOT copied | rewrite **and** copy |
          | `Pawn/HeadAttachments/gand/mask_yuun` | NOT copied | rewrite **and** copy |
          | `YellowEyes_Female` | NOT copied | rewrite **and** copy |
          | `OuterRim/GeneIcons/*BG` | NOT copied | rewrite **and** copy |
          The donors still hold every file — e.g.
          `2980427615/Common_Old/Textures/OuterRim/Genes/Headbone/ChagrianF_east.png`,
          `2915192253/Textures/Pawn/HeadAttachments/gand/mask_yuun_east.png`. Nothing
          is lost, only unmigrated.

          (b) **69 PawnKindDefs are missing `initialResistanceRange`.**
          `write_pawnkinds` (`:821`) emits each kind with `ParentName="BasePlayerPawnKind"`,
          which does not supply it, so every load throws
          `Config error in RimMandrake<Species>_Kind: initial resistance range is
          undefined for humanlike pawn kind.` — **69 lines, three quarters of the whole
          stack's 93 config errors.** Not only noise: it is what a prisoner's recruitment
          resistance rolls from, so the capture path is unset for all 70 species (70 = the BTD roster the generator emits; 71 XenotypeDefs are now defined under `src/` — `canon.yml > species.ours_on_disk`).
          Fix: one `ET.SubElement(e, "initialResistanceRange").text = "10~20"` beside the
          existing `apparelMoney` line at `:831`. `10~20` is vanilla's humanlike value —
          use it; this is not a balance decision and must not become one.
          ⚠️ **Check `write_rescued_kinds` (`:769`) too.** It emits the 16 Galactic
          Diversity `RimMandrake_<Species>` kinds. The error text names `_Kind`, so those
          16 are probably clean — confirm rather than assume, and fix if not.
verify:   OFFLINE, all three before deploying:
          1. `python3 src/RimMandrake/Utils/gen_races_mod.py` re-derives the mod and
             prints `references that die 0` / `dangling texture paths 0`.
          2. No def field in the regenerated mod holds a path beginning `Pawn/`,
             `OuterRim/`, `UI/` or `Genes/` **without** the `RimMandrakeSW/` prefix:
             `grep -rhoE '>(Pawn|OuterRim|UI|Genes)/[^<]*<' src/Jawa/RimMandrake_StarWarsRaces/Defs/`
             returns nothing.
          3. Every path the generator now rewrites has a PNG behind it in
             `src/Jawa/RimMandrake_StarWarsRaces/Textures/` — the file count rises from
             713. A rewritten path with no art is the SAME magenta box wearing a new name.
          Then bare `deploy_custom_mods.py --mod RimMandrake_StarWarsRaces`, read the
          plan, then `--apply`.
          🔴 **STOP — the "one re-run" this item is built on is not possible today.
          See the state line. Do not run the generator expecting output.**
criteria: LIVE, on the load this window precedes — folded into `NEXT_RELOAD.md` §5 L0:
          · `grep -c "Failed to find any textures at" Player.log` returns **0**.
            🔴 That is the string. `Could not load UnityEngine.Texture2D` returns zero
            hits and is the wrong grep.
          · `grep -c "initial resistance range is undefined" Player.log` returns **0**.
          · A **female** `RimMandrakeChagrian`, a `RimMandrakeGand`, a `RimMandrakeSelkath`
            and the Gand's `mask_yuun` all render a head rather than a magenta box.
            ⚠️ **Gendered fields make this look intermittent** — male Chagrians already
            render because their `texPaths` WERE rewritten. **Do not test one sex and
            call a species clean.**
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

          DONE in `e4d6040`, all three code fixes, none deployed:
          · (a) `texPathFemale`, `backgroundPathEndogenes`, `backgroundPathXenogenes`
            added to `TEXFIELDS`; `headPaths` and `texturePaths` to `TEXCONTAINERS`.
            The spec said `mask_yuun` needed a HAND edit "outside the generator" —
            it does not: `SW_Support.xml` IS generated (`gen_races_mod.py:899` is
            its default target), so `texturePaths` covers it. The spec also warned
            `TEXCONTAINERS` handles `<li>` only; it does not — the walk takes every
            child, which is exactly why `headPaths`' `<Male>`/`<Female>` work.
          · (b) `initialResistanceRange` `10~20` added to `write_pawnkinds`.
            `write_rescued_kinds` NOT changed — unverified, because the run that
            would confirm it cannot complete.
          · (c) NOT IN THE SPEC: `_is_donor_gene` fixes a `KeyError: 'GS_Primitive'`
            that stopped the generator DEAD. `main` looked genes up in the dump with
            a bare `g[n]`; the donors' genes left the dump when the donors left the
            list.

          🔴 WHY IT IS BLOCKED, and this is the finding: `pick_species` reads its
          species from the DUMP and — unlike `_gene_exists`, whose docstring
          anticipates exactly this — has **no on-disk fallback**. With the donors
          switched off it builds **57 species where the mod ships 69**, losing
          Herglic, Defel, Ithorian, KelDor, Mirialan, Rakata, SithMassassi and
          others. **The `KeyError` was the only thing preventing that from being
          written and deployed over a mod live at slot 562.** Fixing the crash
          removed the accident, so `_guard_species_regression` now refuses to write
          a smaller catalogue. A partial run DID overwrite six def files at 57
          species before the guard existed; reverted, and HEAD is 69.

          TO UNBLOCK, pick one — both are DECIDE's call, not mine:
          1. Give `pick_species` the disk fallback `_gene_exists` already has.
             Offline, no load, and it removes the donor dependency permanently —
             which is the whole point of this mod. **Recommended.**
          2. Re-enable `guy762.starwarsxenotypes` + `neronix17.outerrim.galacticdiversity`,
             take a dump with them active, regenerate, switch them off again.
             Costs a load and restores the dependency this mod exists to break.

          ⚠️ Until then the four magenta species STAY magenta. That is now a known,
          explained state — CHECK should record it, not re-investigate it.

          ═══════════════════════════════════════════════════════════════════════
          🔴 **CLOSED FOR v1 BY THE OWNER, 2026-08-15 (`36debc4`), broadcast:**
          *"I think we can mark all the races as visually good enough for v1, with
          the remaining missing art for v2 improvement. Let's close out race
          appearance issues for now."*
          ⇒ **The magenta species are ACCEPTED AS SHIPPED. This item is DEAD
          for v1** — not blocked, not waiting on a load, not waiting on option 1.
          📌 **The list is THREE SPECIES and it is complete** — owner, 2026-08-15
          (`7661925`): *"Gand, Selkath, and Chagrian are the ones with missing art."*
          `RimMandrakeGand` · `RimMandrakeSelkath` · `RimMandrakeChagrian`.
          ⚠️ This item's own text says "four magenta species" — that count folds in
          the Gand's `mask_yuun`, which is an asset on one of the three, not a
          fourth species. **Nobody should go looking for a fourth.** A caveat that
          the pair differed between two grids was retracted by CHECK and
          contradicted by the owner: **no re-survey.**
          **Do not build the `pick_species` disk fallback for this reason**, and do
          not re-enable the two donor mods for a dump. The art moved to
          `design/V2_DREAMS.md` under "Race art polish".
          ⛔ Race appearance is CLOSED for v1. Do not open, action or escalate a v1
          item for any race's looks. `gand-and-chagrian-missing-artwork-5d2a09` is
          WITHDRAWN (struck in place below, deliberately left visible).
          ✅ Related and going the OTHER way: **`RimMandrakeOrtolan` is v1, done and
          confirmed** — the owner pulled it out of the deferred list on the 70-race
          grid. Herglic, Anzati, Muun, SithZ and Togorian stay deferred.
          📌 The three code fixes in `e4d6040` are still correct and still undeployed;
          they are a v2 carry-in, not a v1 defect.
          ═══════════════════════════════════════════════════════════════════════

## nomatch-add-assumes-a-container-that-may-be-inherited-7b1e4c
row:      tooling
spec:     The sequel to B22, and a different case from it. B22 catches a `<nomatch>`
          whose xpath is IDENTICAL to the test — provably dead, no `--defs` needed.
          This is the case where the `<nomatch>` `PatchOperationAdd` targets the
          **parent container** of the test xpath, which is the legitimate
          add-if-missing idiom and therefore only a WARN today:
            test:  /Defs/ThingDef[defName="X"]/statBases/MeatAmount
            inner: /Defs/ThingDef[defName="X"]/statBases
          🔴 It is fatal exactly when the def **inherits** that container instead of
          declaring it. Patches run on RAW XML, so the Add matches nothing, returns
          false, and `PatchOperationSequence` stops — every op after it in the block
          silently never runs. Cost us `DA_Taraal` + `DA_SnowTaraal` and one load's
          worth of wrong diagnosis (B59).
          THE CHECK: with defs loaded from RAW XML (not a resolved dump, which
          cannot tell inherited from owned), resolve the inner xpath's container
          against the def's OWN node. Absent ⇒ ERROR, not WARN.
          ⚠️ **This warning currently fires 1,145 times on one file.** A warning that
          fires a thousand times is not a warning — whatever shape the fix takes, it
          has to end with the fatal cases distinguishable from the safe ones, or the
          signal stays buried exactly where it was buried this time.
verify:   a synthetic def that inherits `<statBases>` is flagged ERROR with raw-XML
          defs; a def that declares its own stays at WARN or better; the count on
          `Jawa_Doctrine/Patches/MegafaunaYield.xml` drops from 1,145.
criteria: `validate_patch.py` on `src/Jawa/Jawa_Doctrine` names any def whose
          add-if-missing container is inherited, and names no def whose is owned.
state:    ⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
          reach the frozen world. Parked, not lost.

## ~~gand-and-chagrian-missing-artwork-5d2a09~~ — ⛔ WITHDRAWN, IT IS v2
🔴 CLOSED 2026-08-15, hours after filing, by the owner's ruling that all 70 races are
visually good enough for v1 and the remaining art is v2 improvement. **Do not action
this.** Moved to `design/V2_DREAMS.md` under "Race art polish". Left here struck rather
than deleted so a reader who saw it filed knows where it went. Original text follows.

raised:   2026-08-15 CHECK, from the owner examining the 70-race grid live on the
          scratch quicktest map.
finding:  THREE species named across two separate looks, and the pair is NOT the same
          both times — record all three, do not collapse them:
            `RimMandrakeGand`      — named BOTH times. The solid one.
            `RimMandrakeChagrian`  — named on the owner's OWN earlier grid (the one he
                                     saved as `racetest`), NOT on mine.
            `RimMandrakeSelkath`   — named on MY 70-race grid, NOT on his.
          Owner's words, in order: *"Gand and Chagrian have missing artwork, but most now
          look good."* then, on the new grid: *"Gand and Selkath show missing art in your
          new grid."*
          ⚠️ Two grids, two different second names. Either the fault is not deterministic
          per species, or one of the two was a misread at a glance — **check all three**,
          and do not assume Chagrian is clean because the second look did not name it.
          All SPAWN fine — 70/70 xenotypes spawned (70 = the BTD roster, not the 71 now under `src/`), so this is art only, not defs or genes.
scope:    ⛔ Not triaged and not diagnosed by me — the owner looked, I am recording it.
          Whether it is a texPath that does not resolve, a missing PNG, or a head/body
          type with no graphic is BUILD's to find.
⚠️ do not assume the log will show it:
          `texture path failures` read **0 = baseline 0** in this load's harvest, and
          that check fires ONLY when ALL directions are missing — a partial set is
          silent. A clean log is not evidence against this finding.
note:     Owner's verdict on the rest of the grid was positive — *"most now look good"* —
          so this is two exceptions in 70, not a systemic art problem.

## IMPERIAL_IMPLANT_LEGALITY_1 `royalImplantRules` is a free extension point nobody uses

`FactionDef.royalImplantRules` exists in C# and is **absent from every shipped FactionDef** —
a grep of all of `Data/` returns zero. Vanilla enforces nothing with it. If the Galactic
Empire should ever forbid its own troops certain bionics, or make an implant grounds for the
Empire turning on a pawn, the field is already there and costs one patch.

Found while auditing the Empire, 2026-08-21 (`EMPIRE_GAP_AUDIT.md` §4 gap 9). Recorded
because the *absence* is the surprising part — a reader who greps for examples finds none
and concludes the field is dead. It is not; it is unused.

## MOUNTAIN_RAIN_VIOLENT_1 The one place it still rains, and it is red

🔴 **Owner, 2026-08-21: `[v2]`.** The rain BAN ships in v1 (`RAIN_DRY_THE_LOWLANDS_1`); this
half — *"torrential, boiling, red, or otherwise violent and bizarre"* rain in the high
country — does not.

⭐ **It is cheap when it comes back, and the pieces already exist**, which is why it is worth
recording rather than re-deriving:

- **`SW_RedFoggyRain` is already ours and already ships** —
  `src/Jawa/Jawa_Patches/Defs/WeatherDefs/SWDesertWeather.xml:186`, `rainRate 1`, label
  *"red foggy rain"* — and it is already attached to `Volcano` at commonality 5.
- **The whole build is one curve plus one patch.** Its `commonalityRainfallFactor` is
  `(0,0) (1300,1)`, the same as vanilla `Rain`, so it is not altitude-locked. Steepen it to
  `(0,0) (800,0) (1200,1)` and it becomes **physically incapable of occurring anywhere but
  the wet high country** — because that factor is evaluated **per tile** on
  `Tile.rainfall`, while a `baseWeatherCommonalities` patch is per BIOME and those biomes
  also exist at sea level. Then attach it, dictionary-keyed, to the high-country biomes.
- ⛔ **`AB_VolcanicAshRain` is not a candidate.** It has no `rainRate` node at all, so it is
  ash with rain *art* and does not rain.
- ⛔ **`baseWeatherCommonalities` is DICTIONARY-KEYED.** An `<li>` there once discarded
  seven whole BiomeDefs on this project. See `SWDesertWeather_Attach.xml`'s header.

⚠️ **One thing to re-check before building it:** after `RAIN_DRY_THE_LOWLANDS_1`, the tiles
that keep rain are 359 river-jungle and 276 non-volcanic mountain — median elevation ~606 m,
max 2101 m. **The volcanic province is deliberately dry**, so red rain on a volcano is no
longer available and the high country it would fall on is badlands and desert ridge.
