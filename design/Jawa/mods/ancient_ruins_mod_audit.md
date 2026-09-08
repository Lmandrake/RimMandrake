# Ancient Urban Ruins — deep audit (ANCIENT_RUINS_MOD_AUDIT_1)

Owner's brief, verbatim: "the ancient ruins mod... filled with strange mall
maps and other nonsense that really isn't very star wars at all... a huge
number of thingdefs... or maybe we can learn from it how they generate so
many interesting maps and items."

## 1. Identification — evidence, not guess

**Target: `XMB.AncientUrbanrUins.MO`** ("Ancient urban ruins" by author "MO",
workshop id `3316062206`), plus its two active addon patches:

| packageId (ModsConfig.xml) | workshop id | name | role |
|---|---|---|---|
| `xmb.ancienturbanruins.mo` | 3316062206 | Ancient urban ruins | **main content mod** — 1005 defs |
| `meteores.ancienturbanruinsalldeconstructible.aurad` | 3361061429 | Ancient Ruins All Deconstructible | patch-only (`Patches/Patches_ARAD.xml`), 0 new defs |
| `meteores.ancienturbanruinsvanillaloot.aurvl` | 3446989523 | now titled "Ancient Urban Ruins Hit Point" (author renamed the mod but kept the old packageId) | patch-only (`Patches/Patches_AURVL.xml`), 0 new defs, gives ruin walls/objects real HP |

Method: `ModsConfig.xml` was grepped for `ancient|ruin|urban|mall|metro`,
turning up six candidate packageIds. `About.xml` name/packageId scans over
every `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/*/About/About.xml`
folder confirmed exact folder → packageId mapping for each (packageId
capitalization in the About.xml, `XMB.AncientUrbanrUins.MO`, differs from
ModsConfig's lowercased copy — RimWorld packageIds are case-insensitive, same
mod). The mod's own description confirms the target: *"a variety of urban
exploration experiences and maps... system for importing floor plans and
generating quest maps."* Its `SitePartDef`s literally include
`AM_MALL_S_Site` / `AM_MALL_L_Site` ("A Mall") — the mall-maps identity is
confirmed by content, not name alone.

**What else it could have been, and why each was ruled out:**
- `xmb.ancientminingindustry.mo` ("Ancient Mining Industry", same author XMB)
  — a *different* mod, mining/industry themed, not urban/mall maps.
- `mosi.rebalancedancientjunk` — a rebalance patch for vanilla ancient-ruins
  loot tables, adds no maps or defs of its own.
- `vanillaquestsexpanded.ancients` (Vanilla Quests Expanded - Ancients) — a
  separate VQE quest module, unrelated content mod.
- Vanilla `Scarlands` biome / `AncientRuins_Scarlands` layouts, craters, junk
  gen-steps — **Odyssey vanilla** (`Defs/Odyssey/`), explicitly excluded by
  the item spec as a false lead.

## 2. Def inventory — full triage

Offline dump (`defs.sqlite`, mods=596/`cec112bad2152f47`, captured
2026-09-05T14:41:26Z) measured via
`~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py`:
**1005 total resolved defs** carry `package_id = xmb.ancienturbanruins.mo`
(post-inheritance). The two addon patches contribute **0** new defs (pure
`PatchOperation` files) — confirmed by both dump query and by their on-disk
`Patches/` folders holding nothing else.

Breakdown by def type (top): **ThingDef 735**, RecipeDef 79,
CustomMapDataDef 42, ThingSetMakerDef 20, PawnKindDef 14, SoundDef 13,
BackstoryDef 10, HediffDef 8, JobDef 7, LayoutRoomDef 6, SketchResolverDef 6,
ThingCategoryDef 6, QuestScriptDef 5, RuleDef 5, SitePartDef 5, GenStepDef 4,
TerrainDef 4, PawnColumnDef 3, TraitDef 3, FactionDef 2, ScenarioDef 2,
SpecialThingFilterDef 2, ThinkTreeDef 2, ThoughtDef 2, WorkGiverDef 2,
WorldObjectDef 2, plus 13 more types at 1 each (BiomeDef, LayoutDef,
MapGeneratorDef, ResearchProjectDef, WeatherDef, etc.). Raw XML source
(438 `<ThingDef>` nodes pre-inheritance across 27 files) confirms this is not
a dump artifact — it really is a large, mostly self-authored content pack.

### Triage table (category level — 735 ThingDefs are too many to itemize
individually; grouped by source file, each with a keep/cut/maybe call)

| Category (file) | raw count | verdict | reason |
|---|---|---|---|
| `ThingDef_Ruins.xml`, `ThingDef_SalvagePoint.xml` (ruin wall/floor/rubble pieces) | 43 + 43 | **CUT** | generic modern concrete/rebar debris art, no Star Wars register; only exist to dress the prefab maps below |
| `ThingDef_NonfunctionalBuilding.xml` (decorative dead-tech shells: vending machines, ATMs, arcade cabinets, escalators) | 83 | **CUT** | pure contemporary-urban set dressing, the "mall" identity itself |
| `ThingDef_EmptyShelves.xml`, `ThingDef_EmptyPackage.xml`, `ThingDef_Trash.xml` | 16+10+6 | **CUT** | mall-shelf/retail-packaging flavor objects |
| `ThingDef_Appearances.xml`, `ThingDef_Building.xml`, `ThingDef_Staircase.xml`, `ThingDef_StreetPlate.xml`, `ThingDef_ConstructableElevators.xml`, `ThingDef_UndergroundGarage.xml`, `ThingDef_FloorLabeling.xml`, `ThingDef_comp.xml` | 13+11+11+20+9+3+18+1 | **CUT** | building shells, elevators, parking-garage/street signage — bespoke for the prefab urban maps, not reusable outside them |
| `RangedIndustrial.xml` (Tarkov-style modern firearms + ammo, e.g. `.338LM`, `SS190`, `6.8 spear rifle`) | 48 | **CUT** | real-world modern-military weapon register, directly clashes with the campaign's Star Wars/scavenger arsenal |
| `Armor.xml`, `Helmet.xml`, `BossArmor.xml` (`AM_CompFlakSuit`, `AM_NightVisionHelmet`, `AM_CataphractHelmet…`) | 4+2+6 | **CUT** | modern tactical-gear reskins, off-theme |
| `ThingDef_HighValueItem.xml` (CPU/GPU/SSD/HDD, credit cards, game consoles, LEGO sets, golden statues, briefcases) | 48 | **CUT** | explicitly contemporary loot ("game console", "LEGO", "credit card") — the clearest evidence for the owner's "isn't very Star Wars" complaint |
| `ThingDef_Useable.xml`, `ThingDef_Special comp.xml` | 14+7 | **MAYBE** | a few generic consumables/tools worth a closer look case-by-case if repurposed with new art/names, but low value |
| `Items_Food.xml`, `Thoughts.xml` | 22+0 | **CUT** | modern packaged-food flavor items |
| PawnKindDef (`AncientMallGuards`/"Fashion guy", `AncientSlaughter`/"parasitic failed product", `AM_Elite`) + HediffDef (`AM_RampageParasite`, `AM_IntegratedTorsoArmor`) | 14 + 8 | **CUT** | body-horror "mall zombie" faction concept, no hook into Jawa/Empire/scavenger lore |
| FactionDef `AM_PlayerColony` ("Safe House"), ScenarioDef `SafeHouse` | 2 + 2 | **CUT** | a whole alternate start scenario nobody plays in this campaign |
| CustomMapDataDef (the 42 hand-authored floor plans) | 42 | **CUT (content) / redeemable (technique)** | see §3 — the prefab-map *format* is worth studying even though the specific malls/bunkers are cut |
| GenStepDef, MapGeneratorDef, SitePartDef, LayoutRoomDef, SketchResolverDef, ComplexLayoutDef, ComplexThreatDef (mechanism defs) | ~30 | **STUDY, then CUT with the mod** | the mechanism is the redeemable part, not these specific instances — see §3 |
| RecipeDef (79), ThingSetMakerDef (20), JobDef (7), ThinkTreeDef (2), WorkGiverDef (2) | 110 | **CUT** | machinery in service of the above content (crafting/AI for the modern loot and NPC factions) |
| SoundDef (13), Dialog, PawnColumnDef, KeyBindingDef, MainButtonDef, DesignationCategoryDef | ~20 | **CUT** | UI/audio support for the same content |

**Net:** effectively all 735 ThingDefs and the ~270 supporting defs are
**CUT** as *content*. Nothing found registers into vanilla or another active
mod's tag pools — the mod ships its own `FactionDef`, `PawnKindDef`s, and
weapon/apparel tags, all self-referential. No other active mod lists it as a
hard `modDependencies` entry (only soft `loadAfter` mentions from "More Prop
Categories" and "FrozenSnowFox Tweaks", plus the two official addon patches
and a fan cosmetic patch `Charlie.Muzzle.Flash.for.ancientruins` — all of
which are cut candidates alongside it). Removal breaks nothing else that was
found; this needs re-verification against the *live* mod list at cut time
per doctrine, since the dump is 596/599 mods and may be a few mods stale.

## 3. Generation mechanism — HOW it makes the maps (studied before any
removal call, per the item's explicit requirement)

Two genuinely different systems, both worth understanding:

**(a) Prefab floor-plan playback (`AncientMarket_Libraray.dll`).** The 42
`CustomMapDataDef`s are literal hand-drawn blueprints — a `(x,y,z)` size plus
per-cell terrain/roof/thing/rotation lists (one file runs 233KB of raw
coordinate data for a single 50×50 bunker). A `SitePartDef` (e.g.
`AM_MALL_S_Site`) carries a `ModExtension_Map` naming which prefab(s) it may
draw from, and its `workerClass = SitePartWorker_CustomMap` paints the chosen
prefab wholesale onto the generated map when the player visits. A dedicated
`AM_CustomMap_Editor_Generator` `MapGeneratorDef` (pocket-map biome, no
shadows) exists purely as the *author's own level-editor tool* for building
and exporting these prefabs — not something a player ever loads. This is
essentially a bespoke "paste a saved building" system, closer to a savegame
snippet importer than procedural generation.

**(b) True procedural dungeons riding vanilla's own Complex system
(`ACM_RandomBuildings.dll`).** `ACM_AncientRandomComplex` is a `SitePartDef`
+ `GenStepDef` (`GenStep_RandomAncientComplex`) + `ComplexLayoutDef`
(`ACM_AncientRandomComplex_Loot`) that reuses vanilla's own
`LayoutRoomDef`/`SketchResolverDef` machinery (the same system behind vanilla
Ancient Complexes / Sanguophage vaults) with a weighted room-type pool
(`ACM_HoboRoomLayout:3, ACM_StoreRoomLayout:3, ACM_BuildingRoomLayout:3,
ACM_BuildingRoomWithNoForkliftLayout:3, ACM_ResturantLayout:2,
ACM_UnderRoomLayout:1`) and a custom `ComplexThreatDef`
(`HangingPirates`) ambush. This is genuinely well-built, idiomatic vanilla
extension — not a black box.

**Redeemability verdict: the CONTENT is not redeemable (confirms the
owner's read — modern firearms, LEGO loot, credit cards, mall guards); the
TECHNIQUE in (b) is directly redeemable as a pattern.** It is a working,
in-mod-list example of extending vanilla's `ComplexLayoutDef`/`LayoutRoomDef`
weighted-room system with custom `LayoutRoomDef`s and a `ComplexThreatDef` —
exactly the kind of mechanism `structure_injection_roster` /
`MOISTURE_FARM_TEMPLATES` want, and it can be studied (read-only, from the
workshop folder, before the mod is cut) without keeping the mod installed.
Technique (a), the prefab floor-plan importer, is lower value to imitate — it
is bespoke coordinate-dump XML wired to a private author-only editor
GenStepDef, not a reusable authoring surface.

## Recommendation

**Cut the whole mod family** (`xmb.ancienturbanruins.mo` +
`meteores.ancienturbanruinsalldeconstructible.aurad` +
`meteores.ancienturbanruinsvanillaloot.aurvl`, and drop the now-orphaned
`Charlie.Muzzle.Flash.for.ancientruins` patch) via Cherry Picker, not
uninstall, per doctrine — nothing else in the active list hard-depends on
it. Before the cut: re-run the tag→surviving-item cross-check against the
*live* dump (this one is 3 mods stale) to be safe, since removal itself is a
separate ticket per the item's own scope note. Optionally spend an hour
reading `AncientMarket_Libraray.dll`'s `GenStep_RandomAncientComplex` /
`ACM_AncientRandomComplex_Loot` classes (decompile) as a worked reference for
our own `ComplexLayoutDef` authoring before the mod leaves the list — that is
the one piece worth lifting.
