# MODLIST_COMPLEXITY_AUDIT_1 — ranked keep-or-cut shortlist (2026-09-13)

Background analysis for the owner's cards. **Nothing here executes without a card.**

- **Excluded by design:** Giddy-Up / Run and Gun — ruled under `GIDDYUP_KEEP_OR_CUT_1`.
- **Live list measured:** 594 active packageIds in
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`
  (6 unmatched folders are all `ludeon.rimworld*` core/DLC — not broken).
- **Cherry Picker cut list:** 2,286 entries in
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`,
  attributed to source mods via `DefDump\defs.sqlite` capture `2026-09-12T22-49-15Z`
  (594 mods = live count; fingerprint-matched). 1,308 attributed to mods, 250 vanilla/DLC,
  728 UNMEASURED (defNames no longer in any active mod — stale entries).
- **Contribution authority:** `design/Jawa/fauna/cast_assignment.csv` (369 rows, `mod` column)
  and `design/Jawa/mods/required_mods.md`.
- **Confirmed NOT active** (so not candidates): Combat Extended, RimThreaded, Performance Fish.
- **Two census numbers corrected:** a first sweep reported Tech Level Enforcement at 15 MB and
  Standalone Hot Spring at 7.5 MB of DLL — those were `Source/lib` reference assemblies. Measured
  under `/Assemblies/`: 22 KB and 15 KB. Both dropped from the list.

Ranking = breakage/complexity risk ÷ what the Jawa scenario actually uses.

---

## 1. Ancient Urban Ruins family — `xmb.ancienturbanruins.mo` (+ `meteores.ancienturbanruinsalldeconstructible.aurad`, `meteores.ancienturbanruinsvanillaloot.aurvl`) and its dependency Custom Quest Framework `hailuan.customquestframework` (+ `hailuan.customquestframeworkai`)

- **Gives us:** nothing any more. The owner ruled the family CUT on 2026-09-09
  (`infrastructure/state/items/ANCIENT_RUINS_FAMILY_CUT_1.md:3-6`; audit
  `ANCIENT_RUINS_MOD_AUDIT_1.md:3-5` — "strange mall maps ... isn't very star wars").
- **Risks/costs:** the cut was executed as Cherry Picker def-cuts (559 of 1,005 defs,
  `ANCIENT_RUINS_FAMILY_CUT_1.md:10-12`; 466 attributed cuts in the live XML = 51% hollow) — but
  **all three packageIds are still in `activeMods`** (positions 413 and neighbours), so the mod's
  6 DLLs (`ACM_RandomBuildings.dll`, `AncientMarket_Libraray.dll`, `BuildingExtraRenderer.dll`,
  `手电筒.dll`, …, workshop `3316062206`), its custom map-generation system and its CQF
  dependency (`QuestEditor_Library.dll` 565 KB, workshop `2978572782`) still load and still
  Harmony-patch. `required_mods.md:412` already flagged it and CQF as "the heaviest additions"
  (73.7 MB). `aurad` is a DO-NOT-COMBINE partner per `required_mods.md:411` — and it is active.
- **Disposition:** **finish the cut** — deactivate `xmb.ancienturbanruins.mo`, `aurad`, `aurvl`,
  `hailuan.customquestframeworkai`. CQF itself stays **only** because Dungeon Pack
  (`mlie.dungeonpack`, adopted `required_mods.md:424-426`) declares it as a dependency
  (`3765496911/About/About.xml`) — card that separately if Dungeon Pack goes.
- **Trade, plainly:** nothing is lost that the owner hasn't already given up; ~7 DLLs and the
  largest content download leave the load. Save-compat: any placed AUR buildings in the start
  save become `Could not load reference` — check `CANONICAL_ASHKARR_START_2026-09-12.rws` first.

## 2. Big and Small – Races — `redmattis.bigsmall` (workshop `2894397737`)

- **Gives us:** nothing. "Norse-themed races" (About.xml). **62 of 62 defs cut** in Cherry Picker
  (100% hollow). Zero active mods declare it as a dependency.
- **Risks/costs:** low per-mod (XML only, no DLL), but it is pure dead weight: 62 defs parsed,
  inherited, then blanked every load. The rest of the family
  (`required_mods.md:1511` "Big and Small ×6 ... deliberate experiment") — `redmattis.optional`,
  `redmattis.bigweapons`, `redmattis.biggergravship`, `redmattis.bigsmall.core` — is UNKNOWN on
  contribution (none reach the ≥10-cuts table, none named in design/Jawa).
- **Keep regardless:** the Framework `redmattis.betterprerequisites` (2,144 KB `0Harmony.dll`
  bundled + `BetterPrerequisites.dll` 711 KB) — our own `mandrake.rsw.starwarsraces` declares it
  as a dependency.
- **Disposition:** **cut** the Races mod; card the four siblings as one "keep or trim" question.
- **Trade:** zero gameplay loss; one fewer race pack for HAR/B&S to render.

## 3. RimAI Framework + Core — `kilokio.rimai.framework` (workshop `3529263357`), `kilokio.rimai.core` (`3560404184`)

- **Gives us:** the "talking ship" persona object, adopted 2026-08-07
  (`design/Jawa/mods/required_mods.md:1127-1131`, voice-only plan).
- **Risks/costs:** its transport is HTTP to an OpenAI-style endpoint (bundled
  `000_Newtonsoft.Json.dll` 695 KB + `RimAI.Framework.dll`), which the owner's 2026-09-05 ruling
  forbids for every LLM consumer (`CLAUDE.md:50-52` — "shelling out to `claude -p` ... not by
  making an HTTP call"). Both mods are unlicensed DLL-only, so nothing can be absorbed
  (`design/RimMandrake/llm_ingame_wiring_spec.md:115-125` — "We build the same shape as our own
  thin module ... the Oracle needs a fraction of RimAI's surface"). Core can *call tools that act
  on the colony* — an anti-exponential watch item (`required_mods.md:1131`). A live network client
  inside the game process that the shipped policy says must not exist.
- **Disposition:** **cut** (re-subscribing is one click if the Oracle track dies).
- **Trade:** the ship has no voice until our Oracle ships its own object; nothing in the current
  start save uses it (UNKNOWN — see below).

## 4. Jurassic Rimworld – Dinosaurs Only — `mlie.jurassicrimworlddinosaursonly` (workshop `3541510004`)

- **Gives us:** by the cast authority, nothing — 0 of 369 `cast_assignment.csv` rows name it.
  Four prehistoric creatures were absorbed as standalone copies into our SWBestiary
  (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Absorbed_Diplocaulus.xml:16-21` and 3
  siblings) — no live XML cross-reference to any `JRW*` def survives in `src/` (grep of
  tag-enclosed `JRW…` values: 0).
- **Risks/costs:** 912 defs, **311 already cut** (34% hollow); three Harmony DLLs
  (`ManhuntingDinos.dll`, `DinoShoo.dll`, `ExtraButcheringProducts.dll`) patching animal AI and
  butchery for creatures the Star Wars world does not field. `required_mods.md:477,488` adopted it
  on 2026-08-04 as "the dino layer" — before the fauna cast existed.
- **Conflict to resolve first:** `design/Jawa/fauna/CREATURE_RESIZE_LIST.md:31-47` still places
  JRW dinos in our biomes (Desert, `ZBiome_Badlands`, …) and `biome_fit.csv` marks 476 JRW rows
  "ours" — whether any live BiomeDef wildAnimals list still carries a `JRW*` kind is UNMEASURED.
- **Disposition:** **cut**, after one dump join (biome→wildAnimals) proves no live spawn.
- **Trade:** ~600 dinosaurs nobody cast leave; the four absorbed ones stay.

## 5. CAI 5000 – Advanced AI + Fog of War — `krkr.rule56` (workshop `3673768803`, position 10)

- **Gives us:** smart raid AI (the whole enemy-symmetry design, `desert_world_design.md:208`) and,
  via `FogOfWar_DisableOnPlayerMap.15=True`, the thing that keeps NWN's fog OFF colony maps
  (`FOG_REVIEW_SITTING_WITH_OWNER_1.md:4-12` — "Dropping CAI would cost the whole combat AI and
  remove no fog at all").
- **Risks/costs:** the single heaviest mechanism on the list — per-pawn sight buckets ticked for
  every faction class (`Mod_3673768803_CombatAIMod.xml` SightSettings blocks), a Prepatcher hook
  (`0PrepatcherAPI.dll`) and `CombatAI.dll` 448 KB — and it is an **unofficial 1.6 port**
  (About.xml: "This is an unofficial 1.6 port"). Named as the compat heavy-hitter in
  `GIDDYUP_KEEP_OR_CUT_1.md:23`. If a RimWorld point release breaks it, nobody upstream owns it.
- **Disposition:** **keep** — but it is the one mod whose failure would take the whole combat
  layer with it; a card for "what we do if the port dies" is worth having now, not then.
- **Trade:** keep the smart raids, carry an orphan binary at position 10.

## 6. (NWN) Real Fog of War — `mlie.nwnrealfogofwar` (workshop `3391128917`, position 11)

- **Gives us:** the "you only see it when you see it" threat axis on **expedition maps only** —
  `onlyOutsideColony=True` in `Config\Mod_3391128917_RealFoWModStarter.xml`, and CAI strips it
  on player maps anyway. Design wanted exactly this (`desert_world_design.md:200-213`).
- **Risks/costs:** no global off switch — 27 tuning fields only
  (`FOG_REVIEW_SITTING_WITH_OWNER_1.md:16-21`); per-cell field-of-view recompute is what wedged
  the game for ~4 min when fought with `unfogAll`; two DLL generations shipped side by side. The
  blind-landing scare (`GRAVSHIP_LANDING_FOG_REVEAL_1.md:3-5,16-19`) was closed by our own reveal —
  owner 2026-09-12: "it worked" (ledger note on that item).
- **Disposition:** **keep** (owner's card: is the expedition-map fog worth the second fog engine?).
  `desert_world_design.md:213` "don't run two fog mods at once" is satisfied only because CAI's
  own fog is off — record that as a locked setting pair.
- **Trade:** keep the unexplored-map feel; carry a mod that cannot be switched off if it misbehaves.

## 7. Star Wars KotOR Resources and Materials — `guy762.mm.kotorcore` (workshop `3254370945`, position 555)

- **Gives us:** donor materials our Armoury still declares as a hard dependency
  (`src/RimStarWars/Armoury/About/About.xml:44`); 335 files in `src/` reference kotor/guy762.
- **Risks/costs:** ~6 micro-DLLs (`AbilityDropdown`, `AddGeneForPK_v15`, `AthenaPort`,
  `BodyTypeForPawnKind`, `CrystalFormations`, …) each a Harmony patch of its own; 13
  missing-texture ERRORs found in absorbed content (`KOTORCORE_ABSORPTION_MISSING_TEXTURES_1.md:1-10`,
  closed 09-07). Already scheduled to die: `design/MOD_CONSOLIDATION_PLAN.md:125`
  "dies-with-donor — WEAPONS_DONOR_RETIREMENT_1" (state doing, BLOCKED on game-up).
- **Disposition:** **keep until the retirement item closes** — no new card; the ruling exists.
  The only ask: no new `src/` dependency on it while it is on death row.
- **Trade:** none new — this is a countdown already running.

## 8. Research Reinvented — `petetimessix.researchreinvented` (workshop `2868392160`)

- **Gives us:** v1 progression ("v1 progression rides Research Reinvented + VFE-Factory",
  `design/Jawa/build_plan.md:53,61`).
- **Risks/costs:** shipped a self-referencing prerequisite that hard-crashed
  `start_debug_game_ready` after auto-research; an XML strip was not enough, the real fix is
  **our own Harmony guard** (`QUICKTEST_POSTSETUP_CRASH_1.md:94-107,113,150-157`, closed 09-12).
  Four DLL generations in the folder (175–347 KB); patches research progress paths.
- **Disposition:** **keep** — the guard is ours to maintain; log it as a standing dependency of
  every quicktest.
- **Trade:** scavenger-flavoured research stays; we own a patch on someone else's bug.

## 9. Character Editor + Rim Control — `void.charactereditor` (`1874644848`), `lordfelix.rimcontrol` (`3774299554`)

- **Gives us:** authoring convenience only — both are explicitly "setup/authoring convenience,
  NOT a live gameplay power ... NOT the shipping mechanism" (`required_mods.md:373-374,1323`).
- **Risks/costs:** Character Editor is a 1,143 KB DLL (six versions shipped) that patches pawn
  generation at every spawn; Rim Control is a second live editor over items/buildings/genes.
  Two editors is redundancy with a patch surface. Players get the mod list with the savegame,
  so both ship.
- **Disposition:** **trim** — keep one (Character Editor is the one the workflow cites) for the
  authoring machine; card whether either belongs on the *player* list at all.
- **Trade:** lose a second editor nobody plays with; keep the one we author with.

## 10. GravTide — `gravtide.mod` (workshop `3779600989`, position 164)

- **Gives us:** diving on the four seas — owner asked 2026-09-07 ("make those biomes look like
  ocean yet allow you to land", `UNDERWATER_BIOME_SUPPORT_1.md:3`); diving confirmed working on
  all four (`BENCH_REBOOT_HANDOFF_202609072200.md:81`); loaded clean, 0 dead mods, no new
  baseline errors (`WORLDMAP_REDO_RUN_SHEET_2026-09-07.md:174-177`).
- **Risks/costs:** the newest large binary on the list — `GravTide.dll` 1,470 KB, 32 patch files,
  unlicensed (`underwater_donor_scan_2026-08-31.md:17`), on the list for ~6 days, not yet in
  `required_mods.md` at all (0 hits). Pressure/O2 hediffs and world-map boats are a whole new
  system riding a mod we cannot read.
- **Disposition:** **keep**, eyes open — add it to `required_mods.md` with the sea-mechanic
  rationale so the next audit doesn't re-ask.
- **Trade:** keep the sea-floor game; accept a fresh, closed-source system in the stack.

## 11. Alpha Genes — `sarg.alphagenes` (workshop `2891845502`)

- **Gives us:** `AG_InnatePsylink` for the force-user build
  (`design/Jawa/force_users_build_spec.md:433`) and the 250-gene pool; only 1 `AG_` GeneDef cut.
- **Risks/costs:** its implied-gene sweep NREs on any PawnKindDef whose `race` is null and takes
  the whole load down — bisect-proven, RimWorld's recovery reset fired
  (`NURSERY_JUVENILES_CRASH_1.md:1-8`). Root cause was **our** `Name=` collision (item lines
  20-30), so Alpha Genes is the tripwire, not the culprit — but it is a tripwire on every future
  race def we author.
- **Disposition:** **keep**; note in the SWBestiary authoring checklist that a null-race kind
  crashes the load via this mod.
- **Trade:** keep the genes; carry a hard crash for a class of authoring mistake.

## 12. Beasts of the Rim — `mlie.beastsoftherim` (workshop `2194018641`)

- **Gives us:** nothing cast — 0 of 369 cast rows; 29 of 102 defs already cut (28%).
- **Risks/costs:** near zero (no DLL); cost is 73 leftover animal defs in the pool and in
  `animal_live_diff.py` runs. Whether any still spawn wild in our biomes: UNMEASURED.
- **Disposition:** **cut** at the next Cherry Picker/ModsConfig pass — lowest stakes on this list.
- **Trade:** a few generic beasts leave; nothing the design named.

---

## Considered and left off (keep, no card needed)

- **Vehicle Framework** (`smashphil.vehicleframework`, 1,824 KB DLL): design depends on it
  (`required_mods.md:1040-1047`); no defect on record.
- **Primordial Geysers** (`ironscruff.primordialgeysers`): 10/29 cut but "a mod nobody is
  retiring" — R-H0 volcanism needs its biome (`RETIREMENT_CHECKLIST.md:181`,
  `biome_review_comments.md:32`).
- **Vanilla Expanded Framework / VGE / VIE-Memes / Alpha Memes / HAR / ReGrowth / Biomes! Core**:
  heaviest patch counts on the list (128–308 patch files each) but each carries named cast or
  biome content (`cast_assignment.csv` tallies; `desert_world_design.md:35,73-76,130`); no defect
  on record.
- **Dubs suite / Layered Apparel / VRE-Genie identical 2,167 KB DLLs**: one bundled Harmony copy
  each, not independent code — not a signal.

## UNKNOWN

- Whether the start save (`CANONICAL_ASHKARR_START_2026-09-12.rws`) holds placed things from
  AUR, RimAI Core or JRW — a cut would then surface as `Could not load reference`. Not grepped.
- Whether any live BiomeDef `wildAnimals` list still carries a `JRW*` or Beasts-of-the-Rim kind
  (dump join not run; `biome_animal_conflicts.py` is the instrument).
- What the four Big and Small siblings (`optional`, `bigweapons`, `biggergravship`,
  `bigsmall.core`) contribute — no design mention, no cut evidence either way.
- The 728 Cherry Picker entries naming defs that no active mod defines — stale, but not
  attributed to which retired mods.
- Whether `hailuan.iwbb` ("I will be back", 2 DLLs) is a CQF-family passenger or independently
  wanted — not named anywhere in design/Jawa.
