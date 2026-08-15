# BUILD inbox.

## B0 Deploy the 30-tool companion at the next down game
row:      7
spec:     `src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`,
          md5 `d7e7c6c1`, 30 `jawa/` tools. **`--gm` REQUIRED** or `fire_incident`
          and `send_letter` are stripped off the game copy. Game must be DOWN.
          Deploy `JawaSeaShaper.dll` SOLO in the same window — repo `b7730027`
          vs deployed `82b48e53` — it cannot be written while RimWorld runs.
verify:   md5 of the deployed DLL equals `d7e7c6c1`, and `fire_incident` +
          `send_letter` are present in the deployed bytes (`strings -a -el`).
criteria: `rimbridge/list_tools` counts 30 `jawa/` names.
state:    ready


## B1 BridgeTools 30-tool build and deploy — `--gm` is REQUIRED
row:      7
spec:     `cd /mnt/d/Luke/dev/Rimworld; python.exe src/RimMandrake/bridgetools/build.py --gm --apply`. Game must be DOWN — the DLL is locked while it runs and the write fails `OSError 22` (the refusal is safe, it cannot truncate). Without `--gm` the build STRIPS `jawa/fire_incident` and `jawa/send_letter` off the game copy (30 tools -> 28). One-command form: `./src/RimMandrake/Utils/shutdown_deploy.sh [--yes]` runs S8 -> S1 -> S9 in order and refuses while RimWorld is running.
verify:   `D="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/BridgeTools/JawaBench/JawaBench.BridgeTools.dll"`; `md5sum "$D"` expect `d7e7c6c1...`; `strings -a "$D" | grep -oE 'jawa/[a-z_]+' | sort -u | wc -l` expect **30**; both `--gm` canaries `jawa/fire_incident` and `jawa/send_letter` present. `--apply` REBUILDS before deploying, so a rebuild legitimately produces different bytes — gate on the canaries and the count, not on the md5. Census expectation derives from `.cs` ONLY: `grep -rhoE '"jawa/[a-z_]+"' --include='*.cs' src/RimMandrake/bridgetools/` (without the include it returns one too many — `prove_new_tools.py:112` has `[Tool("jawa/x")]` inside a comment). `strings -a` proves a NAME only; use `strings -a -el` to prove a method-body message shipped (UTF-16LE in the `#US` heap).
criteria: five tools respond live — `jawa/set_faction_relation` (unblocks v1 L3), `jawa/inspect_string` (reads `Thing.GetInspectString()`: `WarningThrusterInside`, `ThrusterBlockedBy`, power, breakdown), `jawa/world_stats` unit fix (`perimeterTiles`, `raggedness` from tiles, `centroidLatNorm`), `jawa/ideo_of`, `jawa/biome_probe`. `TicksGameSafe()` rides along: def reads must work at `programState: Entry` instead of throwing a bare NRE on every tool at the main menu.
state:    ready

## B2 JawaSeaShaper.dll deploy — SOLO, its own load
row:      7
spec:     `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaSeaShaper --apply`. Repo md5 `b7730027a639`; deployed/loaded md5 `82b48e53e668`, mtime 08-13 23:57:29. Game DOWN (loaded and locked). A MOD assembly poisons attribution for anything loaded beside it — do not batch it with a load meant to prove something else.
verify:   deployed md5 == `b7730027a639`.
criteria: the arc-distance and elongation work committed in `c3ee8e7` is present in the running game. S1 is rescoped: it PARTITIONS, it does not write the sea — vanilla already produces 1–2 huge masses with no puddles (`bodiesTotal == bodiesOverMinSize`, n=4) and never 3 bodies; a cut adds boundary tiles without adding area.
state:    ready

## B3 S9 — scrapfields `minSpacing` 4 -> 1
row:      4
spec:     `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches --apply`. Ships `Jawa_Patches/Defs/MapGeneration/JawaScrapfields.xml` with `minSpacing` 4 -> 1 (`8a7a5ee`), plus `JawaGroundHulk.xml`. Root cause: `minSpacing` equalled the engine's hardcoded `ClusterRadius` of 4, so each cluster self-exhausted after ~4 chunks, `TryFindScatterCell` returned an invalid cell and `GenStep_Scatterer::Generate` `ret`s inside its loop, discarding ~46 of 50 chunks. Both are map-generation defs: they need a cold load AND a map generated after it. Never run `--apply` bare.
verify:   `-> VERIFIED in sync`; deployed `JawaScrapfields.xml` carries `minSpacing 1`. `--mod Jawa_Patches` also re-verifies every other file in that mod.
criteria: see CHECK C3 — 44–56 chunks in 4–6 clumps on a map generated after this deploy.
state:    ready

## B4 Armoury patches — HELD on provenance
row:      v2
spec:     `src/Jawa/Jawa_Armoury/Patches/Armoury_MeleePower.xml` and `Armoury_RangedDamage.xml`. Swept into `81939e1` (subject: genome tooling), never reviewed, no provenance banner. Re-run the generator; generators anchor through `observed/2026-08-13/inventory/patch_ledger.json` and print a banner via `src/RimMandrake/Utils/patch_provenance.py`. Also carries 8 double-match `Replace`s.
verify:   provenance banner shows no `unknown` anchors — `unknown` means STOP. Scoped `validate_patch.py --defs` clean; the 8 double-match `Replace`s resolved.
criteria: EMPTY
state:    ready

## B5 MegafaunaYield.xml — 3 double-match Replaces
row:      v2
spec:     3 `PatchOperationReplace` ops each match two nodes (same value written to both). Cosmetic; a player cannot see it.
verify:   scoped `validate_patch.py --defs` sweep reports 0 double-match `Replace` in `MegafaunaYield.xml`.
criteria: EMPTY
state:    ready

## B7 Repair the approved ideoligion .rid
row:      v2
spec:     `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Ideos\The Salvation (CREATE).rid`. Two defects: `AM_Fertility` was dropped while two precepts still require it; `VME_Nomad` is IN and must come out — its own description says non-vanilla movement systems will not register and it inflicts −50 mood at 60 days. `Nomadic_Preferred` is a PRECEPT (`requiredMemes` empty), zero slot cost, already in the file, and does the job: `GravshipUtility::ArriveNewMap` unconditionally stamps `IdeoManager.lastResettledTick`, the only field its ThoughtWorker reads. (`ArriveExistingMap` does NOT write it.) Rebuild with `python3 src/RimMandrake/Utils/build_salvation_rid.py --check|--write`; it never rewrites the source. Do not delete the owner's original `The Salvation.rid` beside it. Do not "fix" `AM_Structure_Scavenger`'s `deityCount 0` by swapping the structure — no installed structure meme allows more than 4, which is why the nine gods live in the description.
verify:   `--check` passes: IDs unique, no dangling `Precept_<ID>`, re-run byte-identical; no `VME_Nomad`; `AM_Fertility` present or its two dependent precepts dropped.
criteria: the ideo browser loads it with 0 rejected precepts; the description renders as scripture, not a wall; the six added precepts show a position (barracks · lighting · combat in darkness · combat prowess · weapons noble *Ranged* / despised *Melee* · apparel desire); one relic, "The Founding Ion Blaster".
state:    ready

## B8 `gravship_flight_invariants.md` §11 is WRONG ON BOTH BRANCHES
row:      infra
spec:     Correct §11 of `gravship_flight_invariants.md` to the measured facts. The export holds **zero thrusters, zero tanks, zero consoles**. The format has **no roof field**, but roofs are derivable: GravshipExport regenerates them at import by flood-fill (`Patch_Sketch_GetSuggestedRoofCells_Postfix.cs:45-85`) => **4,049 of 4,057 substructure cells roofed, every standable cell indoors**. There is **no stern re-lay**: the cost is ONE `GravshipHull` cell per small thruster (two per large), because `ThrusterBase` is `holdsRoof true` + `fillPercent 1` and seals the room exactly as the wall it replaces. Nine sites at x41–49, z131/132; the aft strip (x,133) is off-deck.
verify:   §11 states those measurements and marks the roof map as DERIVED (the mod's own algorithm re-run), not observed.
criteria: EMPTY
state:    ready

## B9 Junkers lose `permanentEnemy` — owner ruling
row:      v2
spec:     `faction_roster_v2.md:1992` (`Permanent enemy | Yes`) and `:2309` (permanently hostile to everyone) -> hostile-but-bribable scavengers. Pillar 5 at `:105` stands as written: the Galactic Empire alone is the permanent enemy.
verify:   no `Permanent enemy | Yes` row survives outside the Galactic Empire.
criteria: EMPTY
state:    ready

## B10 Delete the Imperial Droid Army; the Galactic Empire is the pursuer
row:      v2
spec:     Amend `faction_roster_v2.md` and `gravship_pursuer_mechanism.md`. Two Empire factions only — the planetside aristocratic Empire and the Galactic Empire — and it is the Galactic Empire that pursues the ship: stormtroopers, combat droids, lightsaber-bearing Sith. There is no independent Imperial Droid Army.
verify:   no Imperial Droid Army reference survives in either file.
criteria: EMPTY
state:    ready

## B11 Homestead ideology structure -> `Structure_TheistAbstract`
row:      v2
spec:     `faction_roster_v2.md` :712 / :726 read "Abstract theist or ideological" — literally both. Decided: `Structure_TheistAbstract`, deity *the Withdrawn*, gender `None`. Reason: the covenant is addressed to something, and the ideological structure has `deityCount 0`.
verify:   the either/or line is gone and `deityPresets` is authorable.
state:    blocked
criteria: EMPTY

## B12 Homestead raid frequency — state the refusal as doctrine
row:      v2
spec:     `faction_roster_v2.md:300` says "Homestead / Aquifer / Wookiee never raid (Rw 0)"; `:675` says "Raid frequency | Very low". Fix: put `VME_Raiding_Abhorrent` (Vanilla Ideology Expanded, active) on the Homestead and the Deepwater Compact, set the raid curve low, and let the precept carry the reason.
verify:   `python3 src/RimMandrake/Utils/validate_ideoligion.py <xml>` VALID; the two roster lines agree.
criteria: EMPTY
state:    ready

## B13 `VME_SecularSpirituality` renders nothing
row:      v2
spec:     The Deepwater Compact's only style category is `VME_SecularSpirituality`, which has `thingDefStyles: []` — invisible by construction. Swap for a `StyleCategoryDef` that actually ships styles. Read the resolved DUMP, never the vanilla XML: Anomaly writes `<li>Horaxian</li>` but the dump says `AM_Horaxian` because Alpha Memes `PatchOperationReplace`s the whole list.
verify:   the chosen category has non-empty `thingDefStyles` in the live dump; `validate_ideoligion.py` VALID.
criteria: EMPTY
state:    ready

## B14 Build the eleven `FactionDef` ideoligion blocks — entries 1 and 2 first
row:      v2
spec:     `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_religions_spec.md`. Pattern is the Horax cult, `Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml`: `fixedIdeo` · `ideoName` · `ideoDescription` · `forcedMemes` (structure first, complete set) · `requiredPreceptsOnly` · `deityPresets` · `disallowedPrecepts` · `styles` — NOT the Empire's `requiredMemes` + `structureMemeWeights`. Entry 1 (Galactic Empire — The Rising Order) lands on vanilla `Empire` per `V1_SCOPE.md:84`, replacing that family. Entries 1 (two deities), 2 (one) and 3 (one) need `deityPresets`; the corrected `deityCount` table is at the foot of the spec. Take `ideoName`, `ideoDescription` and every `deityPresets` name/type VERBATIM — they are the only text the engine renders. Never set `hiddenIdeo`. Section 12 (Jawa) is a deliberate empty slot — the owner is building it. Legal vocabulary: `design\Jawa\worldbuilding\data\ideology_palette.md` (136 memes, 685 precepts, 41 styles, 92 ritual patterns). Three engine constraints: charity has no negative precept · `PreferredXenotypes` cannot be aimed at a xenotype from XML · `Apostasy_Abhorrent` hard-conflicts with the `Guilty` meme. Meme ceiling is a COUNT (`MemeCountRangeAbsolute` 1–4 normal memes), not an impact budget — never pass `--impact-budget`.
verify:   `python3 src/RimMandrake/Utils/validate_ideoligion.py <xml>` VALID, then eyeball EVERY `<li>` for its `MayRequire` by hand — the validator does NOT check `MayRequire` (`def/needs-mayrequire` is only an INFO), and an unwrapped defName from a disabled mod is a silent no-op. packageIds: `VME_`/`VFEA_` -> `vanillaexpanded.vmemese`, `AM_` -> `sarg.alphamemes`, plus `VQE_`, `GR_`, `llunak.moreprecepts`, the Ludeon DLC ids. VALID is not GOOD — 4 inert precepts still WARN across the set.
criteria: read the eleven back with `jawa/ideo_of` and diff against the spec.
state:    ready

## B15 Tile augmentation catalogue `[v2]`
row:      v2
spec:     `design/Jawa/worldbuilding/tile_augmentation_catalogue.md` — 31 rows, 19 v1-capable. Pure XML: `LandmarkDef` + `TileMutatorDef`. Cheapest first: F1 (zero XML), then C3, then B1. §5: never cull a spawned def.
verify:   `validate_patch.py --defs` 0 errors on the new defs.
criteria: the augmentation appears on the intended tile at worldgen.
state:    ready

## B16 Restraining bolts `[v2]`
row:      v2
spec:     `design/Jawa/worldbuilding/restraining_bolt_technical.md` (`8353622`). Verdict: CAP the goodwill ceiling — one XML def plus ~40 lines of C#, no Harmony. Lands with the Free Droid Enclaves, whose `FactionDef` is unbuilt.
verify:   assembly builds; the def validates.
criteria: the droid faction's goodwill cannot exceed the cap in play.
state:    blocked

## B17 Re-cast the rebel gear `[v2]`
row:      v2
spec:     The Rebel Alliance faction is suppressed and confirmed absent, but its gear survives and circulates — `OuterRim_A280Blaster` appears 5x in the world and nobody wears it. Add the gear to Junkers / Homestead `pawnGroupMakers`.
verify:   `validate_patch.py --defs`; the xpath matches the intended `pawnGroupMakers`.
criteria: a Junker or Homestead raider spawns carrying `OuterRim_A280Blaster`.
state:    ready

## B18 Merge water rulings W3–W7 into the twelve dossiers `[v2]`
row:      v2
spec:     W3–W7 live only in `water_doctrine.md`. Junker doctrine still assumes universal thirst.
verify:   no dossier contradicts `water_doctrine.md`.
criteria: EMPTY
state:    ready

## B19 `design/Jawa/droid_ruling.md` states a mechanism that is not in the defs
row:      v2
spec:     JDS droids do not explode — they are force-killed on downing and their wrecks are repairable. The ruling holds; the stated reason is wrong. Rewrite the mechanism.
verify:   the stated mechanism matches the defs.
criteria: EMPTY
state:    ready

## B20 Faction roster Stages 3 and 4 `[v2]`
row:      v2
spec:     The other 11 dossiers, `pawnGroupMakers`, memes, ideoligions, the relations matrix, and the licensing gate. Stages 1 and 2 are closed.
verify:   EMPTY
criteria: EMPTY
state:    blocked

## B21 `loadset_fingerprint()` must compare listed against exists
row:      infra
spec:     The `ModsConfig.xml` listed-but-missing trap in code form: `loadset_fingerprint()` compares *listed* against *exists*.
verify:   a synthetic `ModsConfig.xml` listing a packageId that is not on disk is reported, not silently passed.
criteria: EMPTY
state:    ready

## B22 `validate_patch.py` — an op in `<nomatch>` with the test's own xpath is statically dead
row:      infra
spec:     The mirror of O8 and the opposite verdict: reaching `<nomatch>` proves the test matched NOTHING, so an identical-xpath op there can never do anything. Provable WITHOUT `--defs`; today it is only caught as a 0-match ERROR when defs are loaded. `<nomatch>` must stay an ERROR — unlike the `<match>` branch, which `_guarded_by_identical_test()` correctly downgrades to info.
verify:   a synthetic `<nomatch>` case is flagged with no `--defs`; `DroidsAreMachines.xml` still reports OK (0 errors, 2 warnings).
criteria: EMPTY
state:    ready

## B23 Write the three expected-failure signatures before the worldgen session
row:      7
spec:     Write the expected-failure signatures into `EXPECTED_FAILURES` BEFORE the worldgen load. A duplicate costs nothing; a missed one costs a load.
verify:   the signatures exist in `EXPECTED_FAILURES` before launch.
criteria: EMPTY
state:    ready

## B24 Armoury mid-tier reference `[v2]`
row:      v2
spec:     Echani Foil (AP **1.33**) vs Excellent durasteel heavy armour (Sharp **1.05**) -> effective armour **zero**; the lightsaber got only **27.5** through the same suit. Add a Yautja blade (AP **0.60**) to land a tier between them. If the Yautja mod is cut, re-anchor on another mid-tier weapon.
verify:   the three AP values read out of the live def dump.
criteria: EMPTY
state:    ready

## B25 The game-down mod-list batch — one pass before the next launch
row:      infra
spec:     (a) Pin the 6 `loadBottom`+`loadAfter` userRules — order is correct today but rides a tie-break, not a constraint; `loadBottom` outranks `loadAfter`, keep it only on `rimdefdump`. (b) Run `src/RimMandrake/Utils/refresh.py` (wants the game down). (c) **O-v2 Cherry Picker** — remove mechanoid defs AND the `Mechanoid` faction; answer three things: does the game still load · does `Samael.NPCMechsAndAnimals` survive and keep its ANIMALS half (`Patches/NPC_Mechs.xml`, 13 ops into `Empire`/`Outlander*`/`Pirate*`/`TradersGuild`) · is that mod configurable. Do NOT remove Alpha Mechs (`sarg.alphamechs`). `matathias.ruthlessmechanoids` is NOT a mech mod (it is the gravship pursuer redirect) — leave it on. REPORT, do not resolve: Alpha Mechs hangs off `FactionDef[defName="Mechanoid"]/pawnGroupMakers`, so cutting that faction takes its raids too. (d) **O-v3** — enable `vanillaexpanded.vwel` (ws `1989352844`, installed and inactive) and dump its weapon `ThingDef`s in TWO SEPARATE tiers: `salvaged` (pistol/rifle/shotgun/sniper + `unstable` projectile variants) and `ultratech` (incl. a laser sword and a tesla gun). The split is load-bearing for the design (`design/Jawa/worldbuilding/ship_legacy_armoury.md`).
verify:   read `ModsConfig.xml`'s mtime before writing — RimSort writes it too, and it moved twice in twenty minutes with the game down.
criteria: the game reaches the main menu with the new list; the two weapon tiers exist as separate dumps.
state:    ready

## B26 Remove `mandrake.missingartfixes`
row:      infra
spec:     Already dropped from `ModsConfig.xml`; all 7 textures are md5-identical to the per-donor successors and the blocking dependency is cleared. Remove the deployed copy under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\` and the repo folder.
verify:   neither path exists.
criteria: EMPTY
state:    ready

## B27 Rebuild the skill zips at hand-off
row:      infra
spec:     `python3 src/RimMandrake/Utils/package_skill.py --all`. Editing `skills/<name>/` is not shipping it — Claude Code installs from a `.skill` zip and those are gitignored, so a fresh clone has none. `skills/rimworld-quests.skill` (65 KB) is one that exists only on disk.
verify:   read the EXIT CODE and the named failure list, never the directory listing — a failure leaves its own zip stale beside fresh ones.
criteria: EMPTY
state:    ready

## B28 `jawa/import_gravship` `[v2]`
row:      v2
spec:     Mid-game layout import. `ShipSketchBuilder.BuildFromLayout` is `public static` and pure (no `Find.`/`Current.`/`Map`), and a `Sketch` spawns onto a live map => one method call, not a mod fork; the licence permits it. Floors will NOT come with it — terrain is re-applied by a Harmony patch that does not run for a mid-game Sketch spawn; replay the cells through `jawa/set_terrain_batch` (`src/RimMandrake/Utils/gravship_layout.py` emits them). Build needs the game DOWN.
verify:   builds with `--gm`; the tool name appears in the census.
criteria: a layout XML imports onto a live map and the terrain replay lands. Closes the design loop: author XML -> import -> look -> iterate, with no worldgen and no 25-min load per turn.
state:    ready

## B29 Space Tower `[v2]` — enable and wire the retaliation
row:      v2
spec:     `hailuan.spacetower` is the only absent piece: `hailuan.customquestframework` is already active at 108 of 575 and `hailuan.customquestframeworkai` at 431. Owner's frame: the towers are Imperial infrastructure, the Hutts pay you to cut them, the Empire's retaliation is the cost. Take the Empire-goodwill patch (`ensureHostile: false`, cumulative not one-shot) as PRE-WIRING, not as the cost — the real cost is raid pressure. Design: `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\orbital_towers_and_the_sky_ladder.md`. Two riders: the mod ships NO licence file (default all-rights-reserved — we may subscribe and patch, we may not ship its maps); `rootSelectionWeight` is declared TWICE in `ST_Quest_SpaceTower.xml` (`0.25` then `0.1`), last wins, effective **0.1**, and that is the dial to tune.
verify:   patch validates; `rootSelectionWeight` declared once.
criteria: the quest offers to a gravship colony — `autoAccept=True` on `ST_Quest_SpaceTower` suppresses the space gate entirely and its `everAcceptableInSpace=False` is inert.
state:    ready

## B30 Swap the species-named hood in the ideoligion
row:      v2
spec:     The apparel-desire precept names `guy762_JawaHood`, which is literally species-named. Swap for `OuterRim_DesertHood`. One word.
verify:   `validate_ideoligion.py` VALID; `OuterRim_DesertHood` resolves in the live dump.
criteria: EMPTY
state:    ready

## B31 `factionlessGenerationWeight` patch `[v2]`
row:      v2
spec:     The three Star Wars packs are a STACK, not alternatives: BTD REMIX defines ZERO genes of its own — 196 of its gene refs point at SW Xenotypes, 41 at Outer Rim GD, so uninstalling either breaks it. All three generate, so a wanderer can arrive as the wrong Twi'lek. Fix is a `factionlessGenerationWeight` patch, not an uninstall.
verify:   `validate_patch.py --defs`; the xpath matches the intended xenotypes.
criteria: no wanderer arrives as a non-campaign Twi'lek xenotype.
state:    ready

## B32 Read the shipped `OuterRim_GalacticEmpire` FactionDef
row:      v2
spec:     `src/Jawa/Jawa_Patches/About/About.xml:36` records that the shipped def has `permanentEnemy false` while the faction dossier says permanent enemy YES — that single field plausibly explains `goodwill 0` AND `canFireNow:false`. Already checked: the live faction list (`hostile:false`, `goodwill:0`, name "Imperial Desert Directorate") and the About.xml note. NOT checked: the shipped `FactionDef` itself — a workshop-tree grep timed out at 120 s twice, so scope it.
verify:   quote `permanentEnemy` and the hostility fields from the shipped `FactionDef` file, with path and line.
criteria: EMPTY
state:    ready

## B33 Malformed closing tag in an active workshop mod loses two precepts
row:      v2
spec:     `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2896845138\Defs\Precepts.xml` line 210 reads `<defName>GarryFlowers_Slave_Relation_Vanilla<defName>` — no slash. The live dump shows `GarryFlowers_Slave_Relations` carrying 2 positions where the XML defines 4; `_Equality` and `_Vanilla` are lost with no error. Checked clean: nothing in the religions spec or the Unearned spec depends on them, and the campaign's slave-romance love-gate uses `GarryFlowers_Slave_attendance`, which is unaffected.
verify:   after the fix the live dump shows 4 positions.
criteria: EMPTY
state:    ready

## B34 Correct the "More Slavery Stuff (Continued)" workshop ID in the design docs
row:      infra
spec:     WS `3530586159` is cited as adopted in several design docs but is NOT installed — a grep of all 1246 workshop `About.xml` files matches only the original `2896845138`, which is active and supplies every `GarryFlowers_` def in use.
verify:   grep of the design docs returns no `3530586159`.
criteria: EMPTY
state:    ready

## B35 Execute the restructure to option B
row:      infra
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` — ten stages, ONE commit each, lowest-risk first. Stage 9 (`skills/`) is owner-gated and may never run. §3's seven unplaced items need a ruling before stage 4.
verify:   run `src/RimMandrake/Utils/check_refs.py` and `src/RimMandrake/Utils/doc_budget.py` after EVERY stage; §8 names the check that proves a stage landed whole.
criteria: EMPTY
state:    blocked

## B36 Deferred renames
row:      infra
spec:     `infrastructure/disposing/RESTRUCTURE_PLAN.md` §7. `JawaBench.BridgeTools` -> `RimMandrake.Bridge` (14 tracked files, 4 identities including the deploy folder). The `jawa/<tool>` namespace: 35 tracked files at once, canonically 17 `[Tool]` attributes in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs`, 3 of the 35 being generated JSON. The five `Jawa*` mod folders. All five packageIds ARE active in `ModsConfig.xml` (lines 560–571 of 575) => a load-order edit at a specific slot plus a RimSort rules edit, not a `sed`.
verify:   `check_refs.py` clean; `ModsConfig.xml` slots preserved.
criteria: the game loads with the renamed mods at the same load positions.
state:    blocked

## B37 Two save-citation sweeps
row:      infra
spec:     (1) The prisoner `interactionMode` finding in `TODO_v2.md` — the save it rested on is gone (`acc3261`) and the file was compacted from 1,144+ lines to 350, so its line citation points at nothing. Find it BY TEXT, mark it measured-and-unreproducible, do not delete it. (2) `save_authoring_pipeline.md:141` and `rimworld_file_lore.md` anchor the whole `.rws` teardown to `~/GDrive/Personal/Rimworld/observed/2026-08-13_pre-restructure/savegame/03_Gravtasm__starting_save.rws`; `~/GDrive` does not exist in this WSL at all — the directory is absent, not the file. Establish whether that path is Windows-side, another machine, or dead, then correct it or mark the teardown as a record whose source artifact is unavailable. Do not delete the lore.
verify:   neither file cites a path that does not resolve.
criteria: EMPTY
state:    ready
