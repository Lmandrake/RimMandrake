<!-- status: DRAFT v3 — expansions adopted, pending owner sign-off -->
# Mod Consolidation Plan — domain × tier cells, one big-bang merge

Executes the owner's 2026-09-08 rulings (MOD_NAMING_CONSOLIDATION_AUDIT_1
§Rulings + §Map review rulings R1–R15, e310909b): system = domain × tier
matrix, a mod is a cell; big-bang merge with all judgment pre-baked into a
map; parked content splits fold in; mechanics stay their own mods; fix mods
get a fate column; donor absorption is a separate track; brand = RimMandrake;
Inhabited keeps its name; Ninefold = RM engine + RUT Salvation pack; names
RimProperty / RimPursuit / RimChronicle final (R15).

**R6 doctrine (ratified): the engine + data-pack pattern.** An RM engine
holds real machinery PLUS generic vanilla-style default content, so it is
playable alone; scenario packs patch in from RUT. The guard: only where
real machinery exists — **never invent an empty RM shell where vanilla is
the engine.** Applied throughout: Graffiti gets generic default marks (new
small authoring task, R7); RimChronicle, RimPursuit, RimProperty,
Pyrelands, WeatherSuite and ManyWaters all follow the pattern; no shell
was created for domains where vanilla already is the engine (food, plants,
races have no RM cell).

**The game-down window is purely MECHANICAL.** Authoring tasks the rulings
created — Graffiti's generic default marks (R7), Pyrelands' de-campaigning
text, the Chronicle event-spine spec — are gated precursor/follow-on items,
never in-window work. In particular **CHRONICLE_EVENT_SPINE_1** (ba1f167f):
the one-page event-spine spec (soft MayRequire hooks; Property, Pursuit,
Ninefold and ChronicleRites as producers/consumers) must EXIST before the
sprint's Chronicle/Property/Pursuit merges land.

**The executable map**: `infrastructure/state/mod_consolidation_map.csv`
(every one of the 77 mods appears; 10 VERIFY rows). **The Jawa_Patches
3-way split ALREADY EXECUTED** (2385af29, 2026-09-04: 95 Patches/Defs +
70 assets into the three tier patches mods, no defNames renamed);
`src/SPLIT_Phase3/Jawa_Patches` is a 0-XML tombstone whose map row is a
retire. What still rides this sprint from that item: the straddle
extractions and tombstone removal (JAWA_PATCHES_SPLIT_1, bottom section);
cold-load proof of the successors rides COLD_LOAD_RUN_SHEET_3, not this
sprint.

**Headline: 77 mods → 53 at sprint end** (51 steady-state once the two
donor-tied fix mods die with their donors on the absorption track).
RM 21 · RSW 12 · RUT 20. Map carries 10 VERIFY rows. Nothing here executes
until the owner signs off this revision.

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
| **faith / pantheon** | Ninefold `mandrake.rm.ninefold` (engine, R2) + Graffiti `mandrake.rm.graffiti` ← SacredGraffiti's worker C# + NEW generic default marks (R7) | — | **Salvation `mandrake.rut.salvation` (NEW, R8)** ← SacredGraffiti's nine mark-styles, IshkoDarkLandmarks, Rites (AftermathRites NOT in it) |
| **crime / property** | **RimProperty `mandrake.rm.property` (R1)** = Property ← SalvageClaim, TheftHauler (droid-loader wiring stays a MayRequire patch; RIMPROPERTY_ANIMAL_THEFT_1 filed) | — | — |
| **pursuit / visibility** | **RimPursuit `mandrake.rm.pursuit` (R3, NEW)** = Visibility ← EmpirePursuit's pursuit engine (promoted RUT→RM) | — | EmpirePursuit `mandrake.rut.empirepursuit` stays as the Empire-triggers data pack |
| **chronicle / events** | **RimChronicle `mandrake.rm.chronicle` (R5)** = Aftermath, reframed: hookable game-event evidence engine (battle-scoped v1; Ninefold consumes the same events) | — | ChronicleRites `mandrake.rut.chroniclerites` = AftermathRites renamed (proposed grammar name) |
| **water** | **ManyWaters `mandrake.rm.manywaters` (R10, NEW)** — all water effects/types (steaming, boiling, …) ← RiverSteam's fleck effect | — | RiverSteam's Ashkarr wiring → UtinniPatches (judgment call — see §7.11) |
| **art / UI** | RustChrome `mandrake.rm.rustchrome` | — | MenuShell `mandrake.rut.menushell` ← UtinniShell (R10) · AshkarrLandmarkArt stays separate (R10) |
| **patches** | MandrakePatches `mandrake.rm.patches` ← 5 RM fix mods (Jawa_Patches' 8 RM files already landed, 2385af29) | StarWarsPatches `mandrake.rsw.patches` ← 2 RSW fix mods + DesertVehicleReskin (R11) (28 RSW files already landed) | UtinniPatches `mandrake.rut.patches` ← FactionSlate (VERIFY) (57 RUT files already landed) |
| **terrain / weather** | **Pyrelands `mandrake.rm.pyrelands` (R9, NEW)** = FireEcology engine + generic biome content (self-contained) · **WeatherSuite `mandrake.rm.weathersuite` (R9)** promoted whole to RM | — | AshkarrWeatherSuite stays (uniquely-Ashkarr wiring); PyrelandsFireEcology's Ashkarr residue → UtinniPatches, folder dies |

### 1b. Mechanics that stay their own mods (ruling 4)

RM: RimChronicle (né Aftermath), FluidCanals, Inhabited, Oracle, Pits,
RimProperty (né Property, ← SalvageClaim, TheftHauler — R1), RaidRedesigner,
RimPursuit (né Visibility, ← pursuit engine — R3), WreckedMachines,
StrandedQuest (VERIFY tier). RSW: JawaRules, JawaVoice — **per-file triage
done (11 patch files, sixth straddle): the naming plan's "6 files carry
god/ship/campaign refs" does NOT reproduce** — no Ishko/Nine/ship/clan
vocabulary greppable in any file; "Utinni!"/"Thrumb-bros" are canon Jawaese,
not campaign names. Whole mod stays RSW; only JawaVoice_Ideology.xml keeps
a VERIFY (full line-read in sprint). RUT: ChronicleRites (né AftermathRites),
Antiquities, AshkarrInhabited, AshkarrWeatherSuite, Doctrine, EmpirePursuit
(data-pack half, R3), LanternDeeps, PlantGrowth, ResearchRetag,
RestrainingBolts, ShipMemory. Dev-only mods stay: LoadTracer,
PlanetPresetPrime, RimDefDump. R14 — NO retirements approved: SeasWaterline
stays pending (VERIFY); BirthHatchDemo stays, gated on
EGG_PROXIMITY_HATCH_TRIGGER_1 (VERIFY). Only the SPLIT_Phase3/Jawa_Patches
tombstone is removed. Folders that die by merge: PyrelandsFireEcology and
RiverSteam (their Ashkarr residues fold into UtinniPatches — §7.11).

### 1c. The Ninefold / Property / Visibility / Doctrine cluster — RULED (R1/R2/R3)

The audit suspected one system in pieces. Examined: they are four distinct
systems that share only history. Ninefold = divine-satiation mood engine (0
defs, own C#). Property = ownership/theft/perception fabric with three
dependents. Visibility = a 0–100 stat dial; its census "dep" on
`mandrake.rut.doctrine` is NOT in its About.xml modDependencies (checked —
loadAfter at most; the safe-core merely originated inside Doctrine). Doctrine
= the campaign's surgical patch layer. Merging them would weld a faith
engine to a crime engine to a stat dial for no shared consumer.

Ruled outcomes: **R2** — Ninefold and Doctrine stay separate, the RM-engine
+ RUT-content split stands. **R1** — Property + SalvageClaim + TheftHauler
merge as **RimProperty**; the droid-loader wiring stays a MayRequire patch,
which resolves the RM→RSW tier-inversion worry; RaidRedesigner stays out;
new scope filed as RIMPROPERTY_ANIMAL_THEFT_1. **R3** — Visibility does NOT
stay solo: it merges with EmpirePursuit's pursuit engine (promoted RUT→RM)
as **RimPursuit** ("hiding helps when pursued"); the Empire-specific
triggers stay behind in RimUtinni/EmpirePursuit as the RUT data pack.
packageId picks (noted per R1's "grammar-closest — you pick"):
`mandrake.rm.property` and `mandrake.rm.pursuit` — the modname segment
drops the Rim- stem to avoid the `mandrake.rm.rimproperty` stutter, and
keeping `mandrake.rm.property` unchanged saves every existing MayRequire.

## 2. Fix-mod fates (all 10)

| Fix mod | Donor (packageId, verified in About.xml) | Fate |
|---|---|---|
| DesertVehicleReskin | sarg.alphavehiclesneolithic (stays) | folds-into-patches → **StarWarsPatches (R11; per NAMING_SCHEME_PLAN's tie-break amendment — aesthetic reskins take the tier of the aesthetic)** |
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

## 3. The defName-prefix question — RULED (R4): YES, re-prefix now

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
(shortHashes) — R4's own words: pre-freeze is the only exit. Exception
unchanged: vendored/absorbed donor defNames stay under `.naming-vendored`
exemptions. Surface now includes the R3/R5/R9/R10 tier moves (pursuit
engine defs, ChronicleRites' RM_AftermathRuleDef/RM_AlliancePairDef family,
anything Pyrelands/WeatherSuite/ManyWaters pull up from RSW/RUT).

## 4. Migration mechanics (one game-down sprint, Phase-2 pattern)

Ordering law unchanged: **map → migration → regenerate .rid/.xtp → freeze.**
Pre-gate: CHRONICLE_EVENT_SPINE_1's spec exists before the
Chronicle/Property/Pursuit merges execute (adopted by card, 2026-09-08).

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
7. **defName re-prefix** (RULED yes, R4) via migrate_names.py rows.
7b. **Fully-qualified C# class-reference sweep** (lesson from
   INHABITED_CHARACTERDEF_NAMESPACE_GAP_1, where 269 authored characters
   silently vanished): any merge that relocates or renames a C# namespace
   (SacredGraffiti.cs → Graffiti; Livestock/JawaIkee/IonWeapons/SalvageClaim/
   TheftHauler assemblies folding in; EmpirePursuit's engine → RimPursuit;
   RiverSteam's fleck classes → ManyWaters; FireEcology/WeatherSuite
   namespaces moving `.StarWars.` → root) must sweep EVERY
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

**Per-RM-engine release-readiness columns** (adopted by card, 2026-09-08 —
the manifests serve BOTH art-regen tracking and the release burn-down):
each RM engine's manifest additionally carries, at mod level,
`standalone_loads` / `generic_defaults_present` / `zero_cross_tier_refs` /
`workshop_page_drafted` (yes/no/n-a), one row per RM engine mod
(RimChronicle, RimProperty, RimPursuit, Graffiti, Ninefold, Pyrelands,
WeatherSuite, ManyWaters, StructureInjections, Inhabited, Pits, …).

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
faith             Ninefold (engine, R2) ..consumes.. RimChronicle events      Salvation (NEW, R8) ◄── SacredGraffiti defs
                  Graffiti ◄── SacredGraffiti C#                               ▲ ◄── IshkoDarkLandmarks ..> AshkarrLandmarkArt
                   + NEW generic marks (R7)                                    └─◄── Rites ..> Antiquities
crime             RimProperty (R1) ◄── SalvageClaim
                   ▲              ◄── TheftHauler (droid wiring = MayRequire patch)
                   └..RaidRedesigner (stays separate)
pursuit           RimPursuit (R3, NEW) = Visibility ◄── EmpirePursuit engine ──promoted from──►  EmpirePursuit (RUT data pack, stays)
chronicle         RimChronicle (R5) = Aftermath ──engine──────────────────►   ChronicleRites (né AftermathRites)
weather/fire      WeatherSuite (R9, promoted) ◄──── WeatherSuite (RSW, dies)  AshkarrWeatherSuite (stays, wiring)
                  Pyrelands (R9, NEW) ◄──── FireEcology (RSW, dies)           PyrelandsFireEcology (dies: generic→Pyrelands,
                                                                                Ashkarr residue→UtinniPatches)
water             ManyWaters (R10, NEW) ◄── RiverSteam effect                 RiverSteam wiring → UtinniPatches (folder dies)
inhabited         Inhabited ──engine──────────────────────────────────────►   AshkarrInhabited
art/UI            RustChrome                                                  MenuShell ◄── UtinniShell (R10)
                                                                              AshkarrLandmarkArt (stays, R10)
patches           MandrakePatches ◄─┐        StarWarsPatches ◄─┐              UtinniPatches ◄── FactionSlate (VERIFY)
                    5 RM fix mods ──┘          2 RSW fix mods ─┤
                                               DesertVehicleReskin (R11) ─┘
                  (Jawa_Patches' 95 files already landed in these three, 2385af29 — tombstone dies)
solo mechanics    FluidCanals Oracle Pits    JawaRules JawaVoice (R13)        Antiquities Doctrine LanternDeeps
                  WreckedMachines            Cuisine                          PlantGrowth ResearchRetag AshkarrFlora
                  StrandedQuest(VERIFY tier)                                  RestrainingBolts ShipMemory
dev-only (stay)   LoadTracer PlanetPresetPrime RimDefDump
stay pending(R14)                            SeasWaterline                    BirthHatchDemo (gate: EGG_PROXIMITY_HATCH_TRIGGER_1)
dies-with-donor                              KotORBandolierNorthFix · MSEDroidFix
```

## 7. Decisions — ALL RULED (owner sitting 2026-09-08, R1–R15)

1. **Crime suite** — RULED (R1): merged as **RimProperty**; droid-loader
   wiring stays a MayRequire patch; RIMPROPERTY_ANIMAL_THEFT_1 filed.
2. **Ninefold/Property/Visibility/Doctrine cluster** — RULED (R2/R3):
   Ninefold and Doctrine stay separate; Visibility merges into the NEW
   **RimPursuit** with EmpirePursuit's promoted engine (R3).
3. **defName re-prefix on tier moves** — RULED (R4): YES, now; pre-freeze
   is the only exit.
4. **Salvation pack contents** — RULED (R8): nine campaign mark-styles +
   IshkoDarkLandmarks + Rites; AftermathRites (now ChronicleRites) NOT in it.
5. **Engine promotions** — RULED (R9), and further than proposed:
   **Pyrelands** ships as a self-contained generic RM biome (FireEcology
   engine + biome content together); WeatherSuite likewise promotes whole
   to RM. Uniquely-Ashkarr content stays RUT.
6. **RUT art granularity** — RULED (R10): MenuShell absorbs UtinniShell,
   stays RUT; AshkarrLandmarkArt stays RUT separate; RiverSteam's effect
   generalizes into the NEW RM **ManyWaters** (all water effects/types).
7. **DesertVehicleReskin** — RULED (R11), overriding the draft: folds into
   **StarWarsPatches** — "the reskins were Star Wars"; re-tiers RSW.
8. **Retirements** — RULED (R14): NOT approved. SeasWaterline and
   BirthHatchDemo both stay; BirthHatchDemo gated on
   EGG_PROXIMITY_HATCH_TRIGGER_1.
9. **Fauna cell name** — RULED (R12): SWBestiary keeps its name; merge
   list stands.
10. **JawaVoice** — RULED (R13): stays whole at RSW; one
   JawaVoice_Ideology.xml line-read during the sprint closes its VERIFY.
11. **Judgment calls — RATIFIED by BENCH (2026-09-08)** except one:
   ✅ packageIds drop the Rim stem (`mandrake.rm.property` /
   `mandrake.rm.pursuit` / `mandrake.rm.chronicle`) — now written into
   NAMING_SCHEME_PLAN §7.4's display amendment, with the display-name
   rule: RimProperty displays as "RimProperty", never
   "RimMandrake: RimProperty". ✅ ChronicleRites name stands.
   ✅ PyrelandsFireEcology's and RiverSteam's Ashkarr residues fold into
   UtinniPatches; both folders die. ✅ DesertVehicleReskin's fold rides
   the R4 rename machinery. ⚠️ STILL VERIFY: Pyrelands BiomeDef donor
   ownership (own the def vs keep the zylle.morevanillabiomes dep) —
   resolve before calling the RM biome self-contained.

## 8. Adjacent item NOT riding this sprint

**BIOME_LABEL_CAMPAIGN_NAMES_1** (proposed — relabel 26 donor biomes to
campaign names) is label-text work, not restructure. **Recommend it stays
STANDALONE**: it touches donor-biome label fields none of this map's merge
rows touch, and welding text passes into a big-bang structural sprint
widens the game-down window for no shared verification. If its files turn
out to overlap a patches-cell move mid-sprint, fold it in then — by
decision on the event, not by default.
