# Local mod stack — dungeon-relevant findings (disk thread)

Written 2026-09-11. Scope: what is actually installed/vendored/authored **on
this Mac's checkout of RimMaster**, for dungeon-like content (site maps,
sealed structures, ruins, room-layout systems, quest/loot machinery, keys,
puzzles, multi-level traversal). Every line is marked **CONFIRMED** (I read
the file/def/source myself) or **UNCERTAIN** (inferred, secondhand, or a
description string I did not verify against a def). Nothing here is invented;
where a lead went nowhere I say "not found."

## 0. The machine-access fact, first

**This Mac cannot reach the live game at all.** CONFIRMED:
- `game_paths.py` (`src/RimMandrake/Utils/game_paths.py`) resolves every
  RimWorld path (`ModsConfig.xml`, `DefDump`, Steam Workshop, local Mods, game
  Data) to a Windows literal (`C:\Users\Mandrake\...`, `C:\Program Files
  (x86)\Steam\...`) with a `/mnt/c/...` WSL fallback. Neither exists on this
  Mac — no `/mnt`, no mounted Windows share, no local Steam install (`mount`,
  `/Volumes`, and a disk-wide `find -iname "*steam*"` all came back empty
  except an unrelated log filename).
- `infrastructure/state/dumps/` (the offline def-dump root) holds only
  `README.md` and `REGISTRY.jsonl` on this Mac — the actual captures
  (`defs/`, `manifest.json`, `defs.sqlite`) are **not present here**; they live
  only on the owner's Windows machine. `REGISTRY.jsonl` records 4 frozen
  `official` captures (578–584 mods, 2026-08-20 through 2026-08-29) but I could
  not read their contents from this machine.
- `vendor/mod_sources/` — the 430MB tree of 62 gitignored third-party source
  checkouts described in `vendor/mod_sources/SOURCES.md` — **is not on this
  Mac either**; only the (tracked) `SOURCES.md` provenance doc survived the
  checkout. Confirmed empty via `ls`/`find`: the directory holds nothing but
  that one file.
- Every finding below therefore comes from **repo-committed documents that a
  previous session wrote from the Windows/WSL machine**, or from **source
  files this repo authors itself and ships in git** (which I did read
  directly, byte for byte, on this Mac). I mark the provenance on each line.

## 1. The one piece of direct, currently-live evidence: a cached ModsConfig.xml

CONFIRMED, read directly: `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
(tracked in git, mtime today) is a **snapshot of the real live mod list**,
last refreshed today — **590 active mods**. It is not the canonical source
(that's the Windows file), but it is the freshest copy actually reachable from
this Mac, and `infrastructure/state/modlists/` contains ~90 more dated
snapshots (a full history of every swap this project has made) if a specific
date's list is ever needed.

Filtering those 590 packageIds for dungeon/ruin/quest/structure relevance
(CONFIRMED — I parsed the XML myself) surfaces:

| packageId | likely identity (cross-referenced against design docs, UNCERTAIN unless noted) |
|---|---|
| `oskarpotocki.vanillafactionsexpanded.core` | Vanilla Expanded Framework — **ships KCSG inside it** (see §3) |
| `xmb.ancienturbanruins.mo` + `meteores.ancienturbanruinsalldeconstructible.aurad` + `meteores.ancienturbanruinsvanillaloot.aurvl` | Ancient Urban Ruins family — **still in ModsConfig**, but its *content* was cut via Cherry Picker exclusion, not uninstall (see §2) |
| `hailuan.customquestframework` + `hailuan.customquestframeworkai` | Custom Quest Framework (+ AI companion) — AUR's quest-map dependency |
| `vanillaquestsexpanded.ancients`, `vanillaquestsexpanded.cryptoforge`, `vanillaquestsexpanded.generator` | Vanilla Quests Expanded modules — Cryptoforge is a KCSG `StructureLayoutDef` donor (see §3) |
| `xmb.ancientminingindustry.mo` | Ancient Mining Industry — exploration/combat missions into abandoned mines |
| `mlie.dungeonpack` | Dungeon Pack — hand-authored quest-location structures |
| `gmmp.dungeon` | "Gerrymon's Dungeon Props" — decor/prop pack, not a generator (per `tile_augmentation_catalogue.md:195`, UNCERTAIN, marked MARGINAL/drop-candidate there) |
| `jaeger972.factionterritories` | Faction Territories and Vassalage — deterministic tile→faction ownership (Voronoi over settlements); relevant to who "owns" a dungeon site |
| `mandrake.rut.ashkarrlandmarkart`, `mandrake.rut.ishkolandmarks` | **our own** landmark-art mods |
| `mandrake.rm.strandedquest` | **our own** custom quest mod |
| `sk.gravshipraids`, `arcjc007.gravshipcrashes`, `arcjc007.gravshipexporter`, `redmattis.biggergravship`, `sbz.gravshipstorage`, `btd.remix.gravshipblueprints`, `imagitama.rimworldgravshiprangeonmap` | Odyssey-gravship-adjacent site/raid mods (not deeply audited this pass — flagged as leads, not findings) |
| `mlie.rimquest`, `jaeger972.nomadfreindlyquests` | generic quest-variety mods |

## 2. Ancient Urban Ruins — the deepest audit on disk, and its outcome

CONFIRMED, read in full: `design/Jawa/mods/ancient_ruins_mod_audit.md`
(`ANCIENT_RUINS_MOD_AUDIT_1`, landed 2026-09-08) is a genuinely thorough,
def-by-def audit of `xmb.ancienturbanruins.mo` (workshop `3316062206`, author
"MO") plus its two patch-only addons (`aurad` 0 new defs, `aurvl` 0 new defs).
It reports **1005 resolved defs**, top types **ThingDef 735, RecipeDef 79,
CustomMapDataDef 42, ThingSetMakerDef 20, PawnKindDef 14, LayoutRoomDef 6,
SketchResolverDef 6, QuestScriptDef 5, SitePartDef 5, GenStepDef 4**, plus a
`LayoutDef` and `MapGeneratorDef` at 1 each. Two real map-generation
mechanisms, both confirmed by decompile (not guessed):

- **Prefab floor-plan playback** (`AncientMarket_Libraray.dll`): 42
  `CustomMapDataDef`s are literal per-cell coordinate dumps (one runs 233KB for
  a single 50×50 map). `SitePartDef`s like `AM_MALL_S_Site` carry a
  `ModExtension_Map` naming which prefab to paint, via
  `workerClass = SitePartWorker_CustomMap`. Bespoke "paste a saved building"
  system, not reusable outside this mod.
- **True procedural dungeons riding vanilla's Complex system**
  (`ACM_RandomBuildings.dll`): `ACM_AncientRandomComplex` (`SitePartDef` +
  `GenStepDef GenStep_RandomAncientComplex` + `ComplexLayoutDef
  ACM_AncientRandomComplex_Loot`) reuses vanilla's own
  `LayoutRoomDef`/`SketchResolverDef` weighted-room machinery — the same
  system behind vanilla Ancient Complexes / Sanguophage vaults — with a
  weighted room pool (`ACM_HoboRoomLayout:3, ACM_StoreRoomLayout:3,
  ACM_BuildingRoomLayout:3, ACM_BuildingRoomWithNoForkliftLayout:3,
  ACM_ResturantLayout:2, ACM_UnderRoomLayout:1`) and a custom
  `ComplexThreatDef` (`HangingPirates`).

**Verdict, executed:** content cut (modern firearms/loot/mall dressing is
off-theme), technique kept as a worked reference. CONFIRMED via
`infrastructure/state/items/ANCIENT_RUINS_FAMILY_CUT_1.md`: the family stays
**installed** in ModsConfig (confirmed still present in §1's live snapshot)
but had **559 of its 1,005 defs cut via Cherry Picker** (the other 446 types
Cherry Picker never registers and fall dead once the family's 5
`QuestScriptDef`s are gone) — this project's standing doctrine is
"Cherry Picker, not uninstall." The decompiled mechanism is preserved,
CONFIRMED, at `design/Jawa/worldbuilding/complexlayoutdef_acm_reference.md`:
a full method-by-method writeup of `GenStep_RandomAncientComplex`,
`LayoutWorkerComplex`, threat budgeting (`ComplexThreat.chancePerComplex` /
`selectionWeight` / `maxPerComplex` / `maxPerRoom` against a ~200-point
budget), and room painting via `SketchResolverDef`s. Its stated conclusion:
this data-driven weighted-room-pool pattern is "a genuinely different axis of
reuse" from this project's own KCSG fixed-template route (§3) — re-rolls a
fresh layout each visit rather than placing one hand-authored template.

## 3. KCSG — the authoring backbone, and the answer to "most leverage"

**This is the highest-value finding.** CONFIRMED by reading the actual C#
source shipped in this repo: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchKcsgTools.cs`
implements a live bridge tool, `jawa/kcsg_place`, against **KCSG** (Kv's
Custom Structure Generator), which "ships bundled INSIDE
`VanillaExpandedFramework-main`" (packageId `oskarpotocki.vanillafactionsexpanded.core`,
confirmed active in §1's live snapshot) at
`vendor/mod_sources/VanillaExpandedFramework-main/Source/KCSG/` (that source
tree is not present on this Mac — see §0 — but the bridge tool's own header
comment cites the exact files it read there: `Defs/StructureLayoutDef.cs`,
`Utils/LayoutUtils.cs`, `Utils/GenOption.cs`, `Utils/SymbolUtils.cs`,
`Utils/SettlementGenUtils.cs`, `Utils/TileUtils.cs`).

KCSG exposes **four XML-authorable def types**, each a plain `Verse.Def`
subclass (confirmed by the tool's own comment: "ALL FOUR ... CLASSES DERIVE
FROM Verse.Def"):
- `KCSG.StructureLayoutDef` — a named, fixed-size cell-grid structure, placed
  via `LayoutUtils.Generate(StructureLayoutDef, CellRect, Map, Faction, bool)`.
- `KCSG.SettlementLayoutDef` — a full base layout (buildings + defenses +
  stockpile) via `SettlementGenUtils.Generate`.
- `KCSG.TiledStructureDef` — a multi-tile complex via `TileUtils.Generate`.
- `KCSG.SymbolDef` — a single placeable symbol (building/item/pawn spawner)
  via `SymbolUtils.Generate`; can carry a `<pawnKindDef>` to spawn a pawn.

This project already **uses KCSG as its own dungeon-authoring tool**,
CONFIRMED by reading the def files directly:
`src/RimUtinni/StructureInjectionsRUT/Defs/VaultDungeons/` ships
`StructureLayoutDefs_Vaults.xml` with three hand-authored
`KCSG.StructureLayoutDef`s (`RUT_VaultType1_MechanoidGarrison`,
`RUT_VaultType2_FleshWeaponLoose`, `RUT_VaultType3_FrozenRakata`), each wired
to its own `SitePartDef`/`GenStepDef` pair
(`RUT_VaultSite_Type{1,2,3}`/`RUT_GenStep_VaultSite_Type{1,2,3}` in
`SitePartDefs_Vaults.xml`) plus `SymbolDefs_Vaults.xml`,
`IncidentDefs_Vaults.xml`, and a `QuestScriptDef`
(`Source/Defs/QuestScriptDefs/RUT_VaultThaw.xml`). A sibling structure,
`Defs/DarkTower/`, does the same for a `RUT_DarkTowerControlConsole` +
`StructureLayoutDefs_DarkTower.xml` + `SymbolDefs_DarkTower.xml`. Both live
under the mod `mandrake.rut.injections` (`About/About.xml`, packageId
confirmed by direct read). This mod is the concrete, on-disk, currently-built
template for "hand-made dungeon, authored in KCSG XML."

The bridge tool itself is the live authoring surface: `jawa/kcsg_place` can
place any `StructureLayoutDef`/`SettlementLayoutDef`/`TiledStructureDef`/
`SymbolDef` by name onto a running map (`layoutType=structure|settlement|
tiled|symbol`), replicating KCSG's own debug-menu call sequence
(`GetAllMineableIn` → `CleanRect` → `Generate`), with a documented gotcha: the
placement rect is silently re-centered to the layout's own fixed size (KCSG
cannot render a `StructureLayoutDef` into any other rect). A second tool,
`jawa/vge_spawn_structure_skyfaller`, wraps the same KCSG structure as an
Odyssey-style skyfaller delivery via Vanilla Gravship Expanded's
`VGE_LandingStructure` (set its `layoutDef` field, spawn) — a mechanism for
dropping a KCSG dungeon in as a landing event rather than instant-placing it.

**Answer to "which mod gives the most authoring leverage for hand-made
content": KCSG, bundled inside Vanilla Expanded Framework
(`oskarpotocki.vanillafactionsexpanded.core`), confirmed active, confirmed
already the backbone of this project's own two dungeon-content mods
(VaultDungeons, DarkTower), with a working bridge tool already built against
it.** `vanillaquestsexpanded.cryptoforge` (confirmed active in §1) is a
second live KCSG *content donor*: CONFIRMED via
`design/Jawa/worldbuilding/donor_harvest/cryptoforge_kcsg/README.md`, this
project harvested 38 of Cryptoforge's own `KCSG.StructureLayoutDef` entries
(11 `CryptoforgeMaps_*.xml` files) as a **grammar reference** (room shapes,
prop density, wall thickness) before that mod's *content* is retired —
explicitly not shippable verbatim, since every cell names Cryptoforge's own
third-party `SymbolDef`s.

## 4. Other named dungeon/quest mods on the live list, briefly

- **Custom Quest Framework** (`hailuan.customquestframework` +
  `hailuan.customquestframeworkai`) — CONFIRMED active. Per
  `design/RimMandrake/map_content_injection_research.md:263` and
  `design/Jawa/worldbuilding/tile_augmentation_catalogue.md:324` ("ACTIVE at
  load 108 of 575" as of 2026-08-13), this is Ancient Urban Ruins' own
  quest-map-generation dependency and doubles as this project's general
  quest-scripting layer. I did not read its C# source myself on this Mac (not
  present — see §0); this is UNCERTAIN beyond "active + load position."
- **Ancient Mining Industry** (`xmb.ancientminingindustry.mo`) — CONFIRMED
  active. Per `design/Jawa/mods/required_mods.md:442`: 12+ ancient-mine
  exploration/combat missions; the mod also ships a player-buildable
  mining→screening production line that this project deliberately leaves
  unbuilt (self-limit against the sole-industrial-tree rule) — UNCERTAIN
  (that self-limit is a design ruling, not something I verified against defs).
- **Dungeon Pack** (`mlie.dungeonpack`) — CONFIRMED active. Per
  `required_mods.md:424`: 10 hand-authored quest locations, each a unique
  structure + reward (e.g. a pirate ship with cannons) — described as
  filling the "authored sci-fi dungeon" gap vanilla lacks. Not independently
  verified against its own defs from this Mac (source not present).
- **Dungeon Core** (workshop `3064597982`) — per `required_mods.md:430-435`,
  evaluated and explicitly **dropped** (redundant with Dungeon Pack + Ancient
  Urban Ruins; tonally off — skeleton/treasure-chest fantasy art). Not in the
  live §1 snapshot under any packageId I could match — consistent with "not
  adopted."
- **Vanilla Quests Expanded – Drone Factory** — NOT found in the §1 live
  packageId list under any recognizable name (`vanillaquestsexpanded.*`
  entries present are `ancients`, `cryptoforge`, `generator` only — no
  `dronefactory`). `required_mods.md:446` records it as "ADOPTED w/ HARD
  SELF-LIMIT" on 2026-08-02, but the live mod list does not currently show
  it active — flagging this discrepancy rather than asserting either way;
  resolve against the real `ModsConfig.xml` before relying on it.
- **Gerrymon's Dungeon Props** (`gmmp.dungeon`) — CONFIRMED active, but per
  `design/Jawa/worldbuilding/tile_augmentation_catalogue.md:195` this is a
  **decor/prop pack**, not a map generator, and is flagged there as
  "MARGINAL... drop candidate."

## 5. What is NOT here (say-so, not silence)

- **No ModsConfig.xml, DefDump, or Steam Workshop folder reachable on this
  Mac** — see §0. Any "ACTIVE" claim above rests on the §1 cached snapshot,
  not a live read of the canonical file.
- **`vendor/mod_sources/`'s 62 third-party trees are not on disk here** —
  only their provenance doc (`SOURCES.md`) survived. I could not read
  `VanillaExpandedFramework-main/Source/KCSG/*.cs`, `CustomQuestFramework-Old-src/`,
  or any other vendored mod source directly; every KCSG/CQF claim above is
  sourced from what a prior session already wrote down after reading them on
  a different machine, or from this project's own shipped `.cs`/`.xml` (which
  I did read directly).
- **Real Ruins** (workshop `1552146295`) — explicitly cut, stability risk
  (save bloat/load hangs from server-fetched player-base structures);
  confirmed absent from the §1 live snapshot.
- I did not find any mod on this list implementing a genuine multi-Z-level
  or sub-map traversal system (elevators/basements as a *traversal mechanic*
  rather than set dressing) — Ancient Urban Ruins' `ConstructableElevators`/
  `UndergroundGarage` ThingDefs are cut content (§2), and nothing else
  surfaced this search term. Treat as **not found**, not "confirmed absent."
