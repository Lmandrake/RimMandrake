<!-- status: DRAFT — pending owner map review (MOD_NAMING_CONSOLIDATION_AUDIT_1) -->
# Mod Consolidation Plan — domain × tier cells, one big-bang merge

Executes the owner's 2026-09-08 rulings (MOD_NAMING_CONSOLIDATION_AUDIT_1
§Rulings): system = domain × tier matrix, a mod is a cell; big-bang merge
with all judgment pre-baked into a map; parked content splits fold in;
mechanics stay their own mods; fix mods get a fate column; donor absorption
is a separate track; brand = RimMandrake; Inhabited keeps its name; Ninefold
= RM engine + RUT Salvation pack.

**The executable map**: `infrastructure/state/mod_consolidation_map.csv`
(every one of the 77 mods appears; 11 VERIFY rows). **The Jawa_Patches
3-way split ALREADY EXECUTED** (2385af29, 2026-09-04: 95 Patches/Defs +
70 assets into the three tier patches mods, no defNames renamed);
`src/SPLIT_Phase3/Jawa_Patches` is a 0-XML tombstone whose map row is a
retire. What still rides this sprint from that item: the straddle
extractions and tombstone removal (JAWA_PATCHES_SPLIT_1, bottom section);
cold-load proof of the successors rides COLD_LOAD_RUN_SHEET_3, not this
sprint.

**Headline: 77 mods → 52 at sprint end** (50 steady-state once the two
donor-tied fix mods die with their donors on the absorption track). Nothing
here executes until the owner reviews the map.

## 1. The target roster (domain × tier)

Every cell below is one mod. packageIds follow `mandrake.<tier>.<modname>`.
"←" lists what merges in. Mods not listed in a cell are mechanics or
tooling and stay as-is (§1b).

| Domain | RimMandrake | RimStarWars | RimUtinni |
|---|---|---|---|
| **structures** | StructureInjections `mandrake.rm.injections` (engine, exemplar) | StructureInjectionsSW `mandrake.rsw.injections` ← BeastLairs | StructureInjectionsRUT `mandrake.rut.injections` ← DesertFixtures, VaultDungeons |
| **fauna** | — | SWBestiary `mandrake.rsw.swbestiary` ← SeaBeasts, Livestock, HelixTellurox, JawaIkee, BeastNorm (+ future Mlie absorption lands here) | LongHunger `mandrake.rut.longhunger` (stays; the RUT fauna cell) |
| **weapons** | — | Armoury `mandrake.rsw.armoury` ← JawaIonWeapons; − SovSith genes/headtypes (→ StarWarsRaces), − droid namer rulepacks (→ Droidworks, VERIFY) | — (doctrine already lives in Doctrine/UtinniPatches) |
| **races** | — | StarWarsRaces `mandrake.rsw.starwarsraces` ← Armoury's Absorbed_SovSith genes+headtypes | — |
| **droids** | — | Droidworks `mandrake.rsw.droidworks` (stays; campaign layer already externalized by design) | campaign droid roster rows ride UtinniPatches (from Jawa_Patches' JawaFactionRoster.xml) |
| **food** | — | Cuisine `mandrake.rsw.cuisine` | — |
| **plants** | — | — | AshkarrFlora `mandrake.rut.ashkarrflora` |
| **faith / pantheon** | Ninefold `mandrake.rm.ninefold` (engine, ruled) + Graffiti `mandrake.rm.graffiti` ← SacredGraffiti's worker C# | — | **Salvation `mandrake.rut.salvation` (NEW)** ← SacredGraffiti's mark defs, IshkoDarkLandmarks, Rites (decision 4) |
| **art / UI** | RustChrome `mandrake.rm.rustchrome` | — | MenuShell `mandrake.rut.menushell` ← UtinniShell · AshkarrLandmarkArt stays separate (world art, decision 6) |
| **patches** | MandrakePatches `mandrake.rm.patches` ← 6 RM fix mods (Jawa_Patches' 8 RM files already landed, 2385af29) | StarWarsPatches `mandrake.rsw.patches` ← 2 RSW fix mods (28 RSW files already landed) | UtinniPatches `mandrake.rut.patches` ← FactionSlate (VERIFY) (57 RUT files already landed) |
| **terrain / weather** | — | FireEcology + WeatherSuite (engines; RM-promotion candidates, decision 5) | PyrelandsFireEcology, AshkarrWeatherSuite (wiring cells, stay) |

### 1b. Mechanics that stay their own mods (ruling 4)

RM: Aftermath, FluidCanals, Inhabited, Oracle, Pits, Property (← SalvageClaim,
TheftHauler — decision 1), RaidRedesigner, Visibility, WreckedMachines,
StrandedQuest (VERIFY tier). RSW: JawaRules, JawaVoice — **per-file triage
done (11 patch files, sixth straddle): the naming plan's "6 files carry
god/ship/campaign refs" does NOT reproduce** — no Ishko/Nine/ship/clan
vocabulary greppable in any file; "Utinni!"/"Thrumb-bros" are canon Jawaese,
not campaign names. Whole mod stays RSW; only JawaVoice_Ideology.xml keeps
a VERIFY (full line-read in sprint). RUT: AftermathRites, Antiquities, AshkarrInhabited,
AshkarrWeatherSuite, Doctrine, EmpirePursuit, LanternDeeps, PlantGrowth,
PyrelandsFireEcology, ResearchRetag, RestrainingBolts, RiverSteam, ShipMemory.
Dev-only mods stay: LoadTracer, PlanetPresetPrime, RimDefDump. Retire:
SeasWaterline (0 defs, program lane — VERIFY), BirthHatchDemo (dev demo —
VERIFY), SPLIT_Phase3/Jawa_Patches (after split).

### 1c. The Ninefold / Property / Visibility / Doctrine cluster — KEEP SEPARATE

The audit suspected one system in pieces. Examined: they are four distinct
systems that share only history. Ninefold = divine-satiation mood engine (0
defs, own C#). Property = ownership/theft/perception fabric with three
dependents. Visibility = a 0–100 stat dial; its census "dep" on
`mandrake.rut.doctrine` is NOT in its About.xml modDependencies (checked —
loadAfter at most; the safe-core merely originated inside Doctrine). Doctrine
= the campaign's surgical patch layer. Merging them would weld a faith
engine to a crime engine to a stat dial for no shared consumer.

The one genuine one-system-in-pieces inside the cluster's orbit: **SalvageClaim
+ TheftHauler**, both ~0-def C# verbs hard-depending on Property, both
"crime-suite slices". Recommend merging both into Property; RaidRedesigner
stays out (different concern: persistent NPC roster). TheftHauler's About
also names `mandrake.rsw.droidworks` — a RM→RSW tier inversion to verify
before the merge (if hard, the heist verb may belong in a lower cell).

## 2. Fix-mod fates (all 10)

| Fix mod | Donor (packageId, verified in About.xml) | Fate |
|---|---|---|
| DesertVehicleReskin | sarg.alphavehiclesneolithic (stays) | folds-into-patches → MandrakePatches (MEDIUM: 30-tex full reskin; owner may prefer stays) |
| GravshipAstronautFix | vanillaexpanded.gravship (stays) | folds-into-patches → MandrakePatches |
| PhytokinBarkHeadFix | vanillaracesexpanded.phytokin (stays) | folds-into-patches → MandrakePatches |
| ResearchKitEastFix | PeteTimesSix.ResearchReinvented (stays) | folds-into-patches → MandrakePatches |
| SauridFrillFix | vanillaracesexpanded.saurid (stays) | folds-into-patches → MandrakePatches |
| ToolBeltFix | VanillaExpanded.VAEAccessories (stays) | folds-into-patches → MandrakePatches |
| BlastDoorFrameAsyncFix | Lumi.doorsexpanded (SW ed., no retirement item) | folds-into-patches → StarWarsPatches |
| CereanManeFix | Neronix17.OuterRim.GalacticDiversity (NOT on the sunset list) | folds-into-patches → StarWarsPatches |
| KotORBandolierNorthFix | guy762.MM.KotORCore | **dies-with-donor** — WEAPONS_DONOR_RETIREMENT_1 / ARMOURY_SWMODS_DONOR_GAP_1 |
| MSEDroidFix | Neronix17.OuterRim.DroidDepot | **dies-with-donor** — STARWARS_DONOR_SUNSET_1 wave 3 / DROID_SYSTEM_BUILD_1 (Depot rides OuterRim Core) |

A folded fix keeps its PatchOperationFindMod guard inside the tier patches
mod, so it stays inert when its donor is absent — same behavior, one fewer
mod. The two dies-with-donor rows are recorded here so the absorption items
retire them (ruling 6); they are NOT this sprint's work.

## 3. The defName-prefix question (owner decision)

When content moves tier at extraction (e.g. `RM_SacredMark_*` defs moving to
the RUT Salvation pack, or an `RSW_` def going RUT), does it re-prefix?

**Recommendation: YES, re-prefix now — this is the last cheap moment.**
Phase 2 built the whole machinery (`Utils/migrate_names.py` off a map,
staged commits, ModsConfig swap, `.naming-vendored` exemptions) and proved
it at 4,904 defName hits; the affected surface here is tiny by comparison
(~20 defs: SacredMarks, ritual outcome defs, anything JawaVoice sheds).
Costs: the sed sweep rides the same sprint; world-draft .rws artifacts are
already declared sacrificial pre-freeze; .rid/.xtp regenerate afterward
anyway. After the world freeze the rename becomes effectively impossible
(shortHashes), so "leave the old prefix" is a permanent lie in the one
namespace players see in dev mode. Exception unchanged: vendored/absorbed
donor defNames stay under `.naming-vendored` exemptions. **Flagged as
decision 3** because the owner has twice chosen prefix pragmatism
(`Inhabited_`, `DW_` stems) — he may prefer no-rename here too.

## 4. Migration mechanics (one game-down sprint, Phase-2 pattern)

Ordering law unchanged: **map → migration → regenerate .rid/.xtp → freeze.**

1. **Write-freeze with a mechanism** (Phase-2 precedent): rimflow blocking
   item + temporary PreToolUse hook refusing `src/` writes lacking the
   sprint tag. Sweep includes queue/spec files citing old packageIds.
2. **Baseline**: `refresh.py` current? fingerprint-check the dump; record
   per-source def counts via `measure` (never grep) — this is the
   reconciliation ledger.
3. **File moves**: `git mv` per map row (history preserved); split rows move
   file contents, never whole-folder copies.
4. **About merges**: destination About.xml takes the UNION of source
   modDependencies/loadAfter (dedup; drop deps on mods being merged away,
   e.g. StructureInjectionsRUT's dep on DesertFixtures dies); source About
   deleted with its folder.
5. **packageId consolidation**: map-driven sed — case-sensitive on
   namespaces (Phase 2's case-insensitive replace bit two camel-case
   namespaces).
6. **MayRequire rewrite** from the map + the zero-tolerance checker (a
   wrong MayRequire is a silent no-op; 167 sites last time; known hot rows:
   ResearchRetag → ionweapons/armoury, Graffiti ↔ sacredgraffiti/rut.marks,
   IshkoDarkLandmarks → ashkarrlandmarkart).
7. **defName re-prefix** if decision 3 = yes, via migrate_names.py rows.
7b. **Fully-qualified C# class-reference sweep** (lesson from
   INHABITED_CHARACTERDEF_NAMESPACE_GAP_1, where 269 authored characters
   silently vanished): any merge that relocates or renames a C# namespace
   (SacredGraffiti.cs → Graffiti; Livestock/JawaIkee/IonWeapons/SalvageClaim/
   TheftHauler assemblies folding into their destinations) must sweep EVERY
   fully-qualified class reference in XML — modExtensions `Class=`, comps,
   workerClass, thingClass, custom def root elements — through the map.
   Default rule: keep merged assemblies' namespaces UNCHANGED (ship the old
   DLL namespace inside the new mod) unless a rename row exists; then grep
   the new dump for the old namespace strings and require zero orphans.
8. **Game DOWN**: ModsConfig.xml swap from the map (retired/merged ids out,
   `mandrake.rut.salvation` in, load order: engines before content cells,
   patches cells last); redeploy via `deploy_custom_mods.py` (unique
   folder-name check — the FireEcology tier-collision trap).
9. **`refresh.py`** + re-fingerprint; every downstream census is stale
   until this runs.
10. **Gates**: `naming_lint.py` zero violations (the SPLIT marker row
    finally clears) · MayRequire checker zero · `validate_patch.py --live`
    AND `--defs` on all three patches cells + Armoury + Doctrine · magenta
    sweep (texPath moves bind silently) · grep live log for
    `^Config error in` (invisible to validate_patch).
11. **Def-count reconciliation — the "lost nothing" proof**: for every
    destination, `measure` def count == Σ(source counts from step 2), and
    the old dump's defName SET maps 1:1 through the rename map onto the new
    dump's set — zero unmapped, zero vanished. Per-def counts alone lie
    (verify-what-you-displaced); the set diff is the real check. Art:
    texture file counts per destination reconcile the same way.
12. **Loads**: 22-second minimal-list load + quicktest first; full-list
    cold load (~15 min) at the next natural window. Regenerate
    `The Salvation.rid` / `MandrakeJawa.xtp` after renames, validate with
    `validate_save_artifact.py`. Release the write-freeze.

## 5. Per-domain manifest spec

One manifest per domain SYSTEM (not per cell), living beside the system's
highest-tier cell: `src/<Tier>/<EngineOrPrimaryCellMod>/MANIFEST.csv`
(e.g. `src/RimStarWars/SWBestiary/MANIFEST.csv` for fauna). Committed,
generator-owned where a pipeline exists, frozen-artifact rules where
hand-curated. Columns:

| column | values |
|---|---|
| def | defName (post-consolidation) |
| defType | e.g. ThingDef, PawnKindDef |
| cell | which tier-cell mod carries it (RM/RSW/RUT folder) |
| source_mod | provenance: donor packageId or our origin mod |
| art_status | donor / placeholder / ours / reviewed |
| name_status | donor / ours / reviewed |
| text_status | donor / ours / reviewed |
| numbers_status | default / tuned / reviewed |
| biome_assignment | biome defName(s), or `-` (fauna/flora/structures rows) |
| note | ≤15 words |

"reviewed" means the OWNER looked (review-sheet or in-world savegame per
the 2026-09-02 ruling), never an agent's self-grade. The existing frozen
manifests (ResearchRetag's, beast-norm's) migrate into this format rather
than persisting as parallel truths.

## 6. Relationship diagram — current mods → target roster

Arrows are real merges; dependency lines (`..>`) are real About.xml/MayRequire
facts only. Fix mods and mechanics with no relationships are listed flat.

```
DOMAIN            RimMandrake                RimStarWars                     RimUtinni
────────────────  ─────────────────────────  ──────────────────────────────  ─────────────────────────────
structures        StructureInjections ◄──engine──┐                               ┌─◄ DesertFixtures
                   (exemplar engine)        StructureInjectionsSW ..> engine  StructureInjectionsRUT ◄─┤
                                             ▲                                 ▲                        └─◄ VaultDungeons
                                             └── BeastLairs ──merge──┘         │..> rm.inhabited
fauna                                        SWBestiary ◄── SeaBeasts          LongHunger (stays)
                                              ▲  ▲  ▲  ◄── Livestock
                                              │  │  └── HelixTellurox
                                              │  └── JawaIkee ..> StarWarsRaces
                                              └── BeastNorm (donor-gated)
                                              (Mlie absorption lands here)
weapons                                      Armoury ◄── JawaIonWeapons
                                              │ ─extract→ StarWarsRaces (SovSith genes/heads)
                                              │ ─extract→ Droidworks (droid namers, VERIFY)
races                                        StarWarsRaces
droids                                       Droidworks ─(roster rows stay out)→ UtinniPatches
faith             Ninefold (engine, ruled)                                    Salvation (NEW) ◄── SacredGraffiti defs
                  Graffiti ◄── SacredGraffiti C#                               ▲ ◄── IshkoDarkLandmarks ..> AshkarrLandmarkArt
                                                                               └─◄── Rites ..> Antiquities
crime             Property ◄── SalvageClaim
                   ▲       ◄── TheftHauler (VERIFY droidworks dep)
                   └..RaidRedesigner (stays separate)
weather/fire                                 WeatherSuite ──engine──►         AshkarrWeatherSuite
                                             FireEcology ──engine──►          PyrelandsFireEcology
aftermath         Aftermath ──engine──────────────────────────────────────►   AftermathRites
inhabited         Inhabited ──engine──────────────────────────────────────►   AshkarrInhabited
art/UI            RustChrome                                                  MenuShell ◄── UtinniShell
                                                                              AshkarrLandmarkArt · RiverSteam
patches           MandrakePatches ◄─┐        StarWarsPatches ◄─┐              UtinniPatches ◄── FactionSlate (VERIFY)
                    6 RM fix mods ──┘          2 RSW fix mods ─┘
                  (Jawa_Patches' 95 files already landed in these three, 2385af29 — tombstone dies)
solo mechanics    FluidCanals Oracle Pits    JawaRules JawaVoice(VERIFY)      Antiquities Doctrine EmpirePursuit
                  Visibility WreckedMachines Cuisine                          LanternDeeps PlantGrowth ResearchRetag
                  StrandedQuest(VERIFY tier)                                  RestrainingBolts ShipMemory AshkarrFlora
dev-only (stay)   LoadTracer PlanetPresetPrime RimDefDump
retire            —                          SeasWaterline(VERIFY)            BirthHatchDemo(VERIFY)
dies-with-donor                              KotORBandolierNorthFix · MSEDroidFix
```

## 7. Open decisions for the owner

1. **Crime suite**: merge SalvageClaim + TheftHauler into Property?
   Recommend YES (0-def C# verbs on one fabric); RaidRedesigner stays out.
2. **The Ninefold/Property/Visibility/Doctrine cluster**: recommend
   KEEP SEPARATE (§1c) — the census's suspicion is history, not
   architecture; the cluster's real merge is decision 1.
3. **defName re-prefix on tier moves**: recommend YES now, pre-freeze (§3);
   never after.
4. **Salvation pack contents**: recommend SacredMarks + ritual defs +
   IshkoDarkLandmarks + Rites; AftermathRites stays out (Aftermath's cell,
   not god content).
5. **Promote FireEcology and WeatherSuite engines RSW → RM?** The census
   itself calls both generic. Recommend YES — same sprint, two packageId
   moves; their RUT wiring cells are untouched.
6. **RUT art granularity**: recommend MenuShell absorbs UtinniShell only;
   AshkarrLandmarkArt (world art) and RiverSteam (C# effect) stay separate
   rather than one catch-all art pack.
7. **DesertVehicleReskin**: fold into MandrakePatches with the other five
   RM art fixes, or keep as a named reskin mod? Recommend fold; it is the
   only fix big enough (30 textures) to argue.
8. **Retirements**: SeasWaterline (0-def program lane) and BirthHatchDemo
   (dev demo) — recommend retire both at this sprint; neither ships
   content.
9. **Fauna cell name**: keep the SWBestiary folder/id as the RSW fauna
   destination (recommend — least churn, already the absorption home) or
   rename the merged mod "Fauna".
10. **JawaVoice**: the naming plan's claimed 6-file RUT extraction does not
   reproduce under triage (§1b). Recommend: whole mod stays RSW; one full
   line-read of JawaVoice_Ideology.xml during the sprint closes it either
   way.

## 8. Adjacent item NOT riding this sprint

**BIOME_LABEL_CAMPAIGN_NAMES_1** (proposed — relabel 26 donor biomes to
campaign names) is label-text work, not restructure. **Recommend it stays
STANDALONE**: it touches donor-biome label fields none of this map's merge
rows touch, and welding text passes into a big-bang structural sprint
widens the game-down window for no shared verification. If its files turn
out to overlap a patches-cell move mid-sprint, fold it in then — by
decision on the event, not by default.
