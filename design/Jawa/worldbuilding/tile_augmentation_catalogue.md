<!-- status: live -->
# tile_augmentation_catalogue.md — the concrete augmentation catalogue

_The **content** layer of map authoring: what gets **placed on** a tile, biome by biome._

**This is the catalogue the two Phase-C agents in `design/Jawa/worldbuilding/enrichment_agents.md` §4 draw
from** — **Opportunity-structure seeding** and **Landmark-narrative**. Those name the *intent*;
this file is the *parts list*, and neither is restated here. Sibling: `design/RimMandrake/beautiful_tilemap.md`
beautifies **terrain**, this file places **content on** it; terrain vocabulary lives in
`design/Jawa/worldbuilding/biome_terrain_palette.md`.

**Every defName below is verified against the live def dump** (`…\RimWorld by Ludeon
Studios\DefDump\defs\`, **573 mods as of 2026-08-13**, 25,734 `ThingDef`s) — not guessed.
⚠️ A mod count with no date reads as current forever. The owner's list is **578 mods as of
2026-08-20**; a dated 573 is a fact, an undated one is a landmine.

---

## 0. THE OWNER'S CONCEPT (his framing, recorded before analysis)

> Beyond generic map beautification, **every tile deserves something special**, and some
> tiles could be **downright replete** with improvements before the player arrives. These
> tie into the existing **landmarks** to make them map-detectable. Example: green-gas
> geysers should be common in one biome, and on SOME of that biome — as indicated by
> landmarks — the geysers **already have functional refineries on them**, producing power
> or chemfuel, inside reasonable structures, **with defenders**. The defenders could be
> pawns from the **local faction that owns that territory**.

Everything from §1 down is **analysis**, not the owner's words.

**The prior ruling this extends** (`context.md:758`, owner) is two-tier: **every tile gets an
authored piece**, but most are small — "ancient mystery, a small unique resource, a place of
natural abundance" — while **plot-moving** discoveries come "perhaps every 2–3 tiles". This
file's `rarity` column is that ruling made numeric.

### ⚠️ Correction to an existing cross-reference

`enrichment_agents.md:159` cites *"the 14 set-pieces (see `context.md`)"*. **Both halves are
wrong.** `context.md` holds only the two-tier *model* (`:750-763`). The catalogue is **15**, not
14, and lives in `design/Jawa/worldbuilding/desert_world_design.md` — §3E (`:547-582`, terrain-keyed) and
§3E-bis (`:584-622`, named locations). The bad pointer entered whole in `62bd2f2`.

Rows already covered there are marked `↩3E-bis#n` / `↩3E §3E-XX` below. This file **extends**
that set with the repeatable, biome-keyed, low-drama tier §3E-bis does not cover. **The 3
arc-critical nodes (§3E-bis 8, 10, 14) stay out of scope** — authored one-offs, not generation.

---

## 1. ⭐ THE MECHANISM IS ALREADY IN THE STACK — and it is pure XML

The headline finding. The owner's example is not a thing to invent; **Odyssey already ships
its exact shape** and the stack already extends it.

| layer | def type | evidence from the live dump |
|---|---|---|
| map-detectable anchor | `LandmarkDef` | **113 live.** Vanilla `AncientChemfuelRefinery`, `AncientGarrison`, `AncientWarehouse`, `AncientQuarry`, `AncientLaunchSite`, `HotSprings`. Fields: `commonality`, `mutatorChances`, `comboLandmarkMutators`, `category` |
| per-biome rarity | `TileMutatorDef` | **337 live.** Fields: `biomeWhitelist` / `biomeBlacklist`, `chanceOnNonLandmarkTile`, `extraGenSteps`, `geyserCountFactor`, `junkDensityFactor` |
| the content itself | `GenStepDef` | **301 live.** `GenStep_ScatterThings`, `GenStep_ScatterGroup`, `GenStep_ScatterLayout`, `GenStep_Outpost`, `GenStep_ScatterAncientTurret/UtilityBuilding/Mechs`, `GenStep_ScatterGroupPrefabs` |
| authored footprints | `StructureLayoutDef` / `PrefabDef` | **301 / 209 live** (KCSG via Vanilla Expanded Framework, + Odyssey prefabs) |

**Three mods already add their own `LandmarkDef`s** — Vanilla Landmarks Expanded (`VEE_*`, ~60),
Alpha Biomes (`AB_TarLakes`, `AB_HealingSprings`…), Star Wars Animal Collection (`sw_Sarlacc`,
`sw_DeadSarlacc`). **A modded landmark is a solved, shipped pattern here, not a research
question**, and `AncientChemfuelRefinery` proves the owner's example is a vanilla idiom.

**So rarity, biome gating and landmark anchoring are XML fields needing no C#. What is *not*
free is defenders from the owning faction** — §6.1.

### What the bridge can and cannot do (`skills/rimbridge/`)

| proven | not proven / absent |
|---|---|
| `jawa/set_terrain_batch` — 421 cells, 14 ms, `failedVerify=0` | **No faction, world or settlement read tool exists** (as per the trap file) |
| `jawa/spawn_batch`, `spawn_thing` + `Set Stuff` / `Set Quality` | `spawn_thing` cannot set stuff in one call |
| `jawa/spawn_pawn` **into a named FactionDef** — `{"kindDef":…,"faction":"OuterRim_BinaryStarRaiders"}` ✅ | ⚠️ never pass `"hostile"` — resolves to Insect/Hive and throws on humanlikes |
| `apply_architect_designator` — 13×11 furnished room built | Terrain restore ≠ undo; destroyed plants do not return |

> **Placement is a solved mechanism. Verification of placement is not the gap; *reading
> world/faction state* is.** That read is `jawa/list_factions`, which already
> is already ranked #1 / V1-CRITICAL in a retired seat's queue and gates on a **shutdown** window.

---

## 2. THE CATALOGUE

`rarity` = target `commonality` / `chanceOnNonLandmarkTile`. `anchor`: **LM** landmark-anchored ·
**FP** free-placed mutator. Biome defNames per `biome_terrain_palette.md`.

| # | augmentation | biome(s) | rarity | defs needed — all ✅ verified live unless noted | defenders | anchor | v1/v2 — why |
|---|---|---|---|---|---|---|---|
| A1 | **Lone worked geyser** — one `SteamGeyser` with a running `GeothermalGenerator`, no walls | `Desert`, `ExtremeDesert`, `AridShrubland` | common 0.15 | `SteamGeyser`, `GeothermalGenerator`, `Filth_MachineBits` | none | FP | **v1** — 2 defs, `GenStep_ScatterThings` only |
| A2 | **Derelict geothermal tap** — dead generator, `AncientPipelineSection` run, slag | as A1 | common 0.12 | + `AncientPipelineSection`, `ChunkSlagSteel` | none | FP | **v1** — same shape as A1 |
| A3 | ⭐ **Green-gas geyser field** — the owner's example, half of it | `Desert`, `ExtremeDesert`, `Wasteland`, `Scarlands` | biome-common 0.25 | `VHGE_GasGeyser` (Vanilla Helixien Gas Expanded) | none | FP | **v1** — one `geyserCountFactor`-style mutator |
| A4 | ⭐ **Working helixien tap** — gas geyser + `VHGE_HelixienGenerator` + pipe, unwalled | as A3 | 0.08 | + `VHGE_HelixienGenerator`, `VHGE_HelixienPipe`, `VHGE_GasTank` | none | LM | **v1** — defs exist; power just works |
| A5 | ⭐⭐ **Functional refinery on gas, in a structure** — the owner's example, full | as A3 | 0.04 | + `VHGE_GasPoweredRefinery` **or** `VGE_CompactRefinery` / `BiofuelRefinery`; walls | none | LM | **v2** — needs a `StructureLayoutDef` authored |
| A6 | ⭐⭐⭐ **…with a garrison** — A5 plus faction defenders | as A3 | 0.02 | A5 + `PawnKindDef`s of the owning faction | ✅ **local faction** | LM | **v2** — blocked on §5 |
| A7 | **Derelict refinery** — A5 with everything broken, no defenders `↩3E-bis#1` | `Desert`, `Wasteland`, `AB_TarPits` | 0.05 | `VFEPD_RuinedLabBarrel`, `VFEPD_RuinedBarrelDouble`, `VFEPD_AncientFuelTank`, `VFEPD_PipelineJunction` | none | LM | **v1** — pure scatter, no structure needed |
| A8 | **Ancient chemfuel refinery** — the vanilla landmark, retuned for desert | vanilla `biomeWhitelist` already lists both deserts | 0.20 → retune | **ships already** — `LandmarkDef AncientChemfuelRefinery` | ancient mechs | LM | **v1** — a `commonality` patch, nothing more |
| A9 | **Automated biofuel plant, still running** | `Desert`, `AridShrubland` | 0.03 | `VFEFactory_AutomatedBiofuelRefinery`, `Chemfuel` | none | LM | **v2** — VFE-Factory is the player's own tree; pillar check owed |
| B1 | **Abandoned moisture-farm homestead** `↩3E §3E-AR` | `Desert`, `ExtremeDesert`, `ZBiome_DesertOasis` | common 0.15 | `KotOR_MoistureVaporator_big`, `KotOR_watertank`, walls | none | FP | **v1** — the single most on-theme cheap row |
| B2 | **Poisoned well** — well + toxic terrain patch + corpses | `Desert`, `AridShrubland`, `Wasteland` | 0.06 | `PrimitiveWell`, `NuclearWaste`/`PoisonMud` terrain | none | FP | **v1** — terrain paint + 1 thing |
| B3 | **Shrine-well tended by absent hands** `↩3E §3E-OA` | `ZBiome_DesertOasis`, ~~`BMT_ChromaticOasis`~~ (**LOST 2026-08-20** — Biomes! Oasis is not in the mod list; see `biome_terrain_palette.md` §A4. What carries the oasis role is an open question) | 0.05 | `PrimitiveWell` + `VIE` relic/altar defs | none | LM | **v2** — wants authored ideoligion dressing |
| B4 | **Ancient aquifer pumping station** `↩3E-bis#4` | `Desert`, `ExtremeDesert` | 0.03 | `MoisturePump`, `AncientPipelineSection` | guardian mechs | LM | **v2** — SACRED-SCRAP repair-only rules owed |
| C1 | **Crashed hauler** — a truck on its side, debris field, scorch | any desert | common 0.12 | `AncientIndustrialTruck`, `AncientMetalCrate`, `Filth_MachineBits` | none | FP | **v1** — `GenStep_ScatterGroup`, pattern copied from `ScarlandsJunkClusters` |
| C2 | **Downed gravship section** | `Desert`, `ExtremeDesert`, `ZBiome_Badlands` | 0.05 | `VFEPD_DestroyedLargeThruster`, `VFEPD_DestroyedGravExtender`, `VFEPD_DestroyedSmallHeatsink`, `VGE_DamagedSubstructure` terrain | none | LM | **v1** — every def ships; terrain paint proven |
| C3 | **Junkyard drift** — 15× junk density | `Desert`, `Scarlands`, `Wasteland` | 0.02 non-landmark | **ships already** — `TileMutatorDef Junkyard` | none | FP | **v1** — retune `biomeWhitelist`, zero new defs |
| C4 | **Droid battlefield, re-exposed** `↩3E-bis#3` | `Desert`, `ExtremeDesert` | 0.04 | `GenStep_ScatterAncientMechs`, JDS Separatist droid kinds | dormant | LM | **v2** — droid-brain economy gate is unresolved |
| C5 | **Meteoric metal field** `↩3E-bis#9` | `ExtremeDesert`, `ZBiome_Badlands` | 0.06 | `ChunkSlagSteel` + `MineralRich` mutator | none | FP | **v1** — mutator + scatter |
| D1 | **Wired chokepoint** — sandbag line + live ancient turret in a pass | `Desert`, `ZBiome_Badlands`, `GL_Canyon` | 0.05 | `Sandbags`, `Barricade`, `GenStep AncientTurret` | ancient turret | FP | **v1** — turret hostility needs no faction |
| D2 | **Fortified toll post** — palisade + bunker across a road | `Desert`, `AridShrubland` | 0.03 | `AM_Palisade`, ~~`AM_Palisade_Embrasures`~~ → `FT_Palisade_Embrasures`, `AM_Entrance_Bunker`, ~~`AM_PalisadeGate`~~ → `FT_PalisadeGate` (Fortifications – Industrial; two prefixes corrected 2026-08-20 — `AM_Palisade` and `AM_Entrance_Bunker` are live as written) | ✅ **local faction** | LM | **v2** — blocked on §5 |
| D3 | **Faction outpost with garrison** | `Desert`, `AridShrubland`, `Savanna` | 0.02 | `GenStepDef Outpost` (`GenStep_Outpost`, `defaultPawnGroupPointsRange` 1150–1600) | ✅ **local faction** | LM | **v2** — ⚠️ `GenStep_Outpost` reads `map.ParentFaction`, which on a player-settled tile **is the player**. See §5 |
| D4 | **Vassal outpost** | any owned territory | tied to territory | `FactionTerritories_VassalOutpost` (Faction Territories and Vassalage) | ✅ by design | LM | **v2** — mod-owned generation; audit before adopting |
| E1 | **Ancient quarry** — retune existing landmark for desert | vanilla whitelist covers deserts | 0.20 → retune | **ships already** — `LandmarkDef AncientQuarry` | none | LM | **v1** — `commonality` patch |
| E2 | **Ancient warehouse / stockpile** | as E1 | 0.20 → retune | **ships already** — `AncientWarehouse`, `GenStep AncientStockpile` | none | LM | **v1** — `commonality` patch |
| E3 | **Ancient garrison** — vanilla, mech-defended | as E1 | 0.20 → retune | **ships already** — `LandmarkDef AncientGarrison` | ancient mechs | LM | **v1** — ⚠️ **already generating today, unaudited** |
| E4 | **Ancient launch site** `↩3E-bis#10-adjacent` | as E1 | 0.10 | **ships already** — `AncientLaunchSite` | none | LM | **v2** — arc-critical dressing; DECIDE owns the hook |
| F1 | **Sarlacc pit** | `Sandy`/`DryGround`/`Dunes` | 0.10 | **ships already** — `sw_Sarlacc`, `sw_SarlaccLair` | the sarlacc | LM | **v1** — ✅ already live; verify it and tick the gate |
| F2 | **Dead sarlacc** — a carcass to strip | as F1 | 0.05 | **ships already** — `sw_DeadSarlacc`, `sw_DeadSarlaccCave` | none | LM | **v1** — as F1 |
| F3 | **Tar-seep pumping rig** `↩3E §3E-TP` | `AB_TarPits` | 0.08 | `AB_Tar` terrain + `AncientDrillPlatform`, `AncientExcavator` | none | LM | **v1** — defs ship; `AncientDrillPlatform` wants `NaturalRock` (`terrainValidationAllowed`) |
| F4 | **Rimefeller derrick field** | `Desert`, `Wasteland` | 0.04 | `OilWell`, `DeepOilWell`, `RefineryLoadingBay` | none | LM | **v2** — ⛔ **blocked**: the buildability strip `required_mods.md:517` prescribes has never been applied |
| F5 | **Geonosian resin mine** `↩3E-bis#5` | `Desert`, `AB_RockyCrags` | 0.03 | VFE-Insectoids 2 hive defs | ✅ **hive faction** | LM | **v2** — blocked on §5 |

**Blocked rows: F4 only** (a config prerequisite, not a missing def). **Every other def in the
table exists in the live dump.** That is the catalogue's strongest single result.

---

## 3. V1 FEASIBILITY PASS

Judged on four gates: **only existing defs · bridge can place it today · verifiable by the
"seen in game once" bar · no new C# and no new mod.**

| verdict | count | rows |
|---|---|---|
| ✅ **v1-capable** | **19** | A1 A2 A3 A4 A7 A8 B1 B2 C1 C2 C3 C5 D1 E1 E2 E3 F1 F2 F3 |
| 🔶 v2 — needs an authored `StructureLayoutDef` | 3 | A5 A9 B3 |
| ⛔ v2 — blocked on faction ownership (§6.1) | 5 | A6 D2 D3 D4 F5 |
| ⛔ v2 — blocked on an unresolved design gate | 4 | B4 C4 E4 F4 |

**19 rows clear all four gates — but the number flatters the work.** Eleven are new XML; **eight
are already generating in the live game right now** (A8, C3, E1, E2, E3, F1, F2, `HotSprings`)
and need only a `commonality` retune, or in F1/F2's case *nothing but a sighting*. **The v1
contribution here is mostly retuning and verifying content already present, not authoring new
content.** That is the useful answer.

### ⭐ The cheapest three — and one costs nothing

1. **F1 — Sarlacc pit.** Zero XML. `sw_Sarlacc` is a live `LandmarkDef`, `commonality 0.1` on
   `Sandy`/`DryGround`/`Dunes` — **already on the desert world**. Cost = find one, screenshot it.
   **A v1 gate pass for the price of a bridge call.**
2. **C3 — Junkyard drift.** ⛔ **PREMISE CORRECTED, a retired seat 2026-08-14 — read the def before
   patching it.** `TileMutatorDef Junkyard` (`Data/Odyssey/Defs/TileMutators/TileMutators_Modifiers.xml:153-163`)
   has **NO `biomeWhitelist` and NO `biomeBlacklist` at all.** There is nothing to add desert
   biomes to: it **already fires on every biome**, deserts included, at
   `chanceOnNonLandmarkTile 0.01`. `junkDensityFactor 15` and the two `extraGenSteps` are as
   described.
   ⇒ **The only lever is the 1% chance**, and that is now a design call rather than a mechanical
   patch, because the field is global:
     * **raise `chanceOnNonLandmarkTile`** — more junkyards everywhere. On a mostly-desert planet
       that is nearly the same thing as "more in the desert", and it is a one-value patch.
     * **add a `biomeWhitelist` AND raise it** — scopes junkyards to our deserts, but that
       *removes* them from every other biome, which is a bigger change than the row asks for.
   🔴 **Worldgen-gated either way:** mutator selection happens at `WorldGenStep_Mutators`
   (order 700), so a chance patch that misses a worldgen never applies to that world.
3. **B1 — Abandoned moisture-farm homestead.** One `GenStep_ScatterGroup` over
   `KotOR_MoistureVaporator_big` + `KotOR_watertank`. Three live defs, and it closes
   `desert_world_design.md` §3E's **AR** row — most on-theme content per line of XML in the file.

⚠️ **A8/E1/E2/E3 generate on the desert world today at vanilla `commonality 0.2` and nobody has
audited what that produces. Look at what the map already makes before authoring anything new** —
free information that may cover "every tile deserves something" further than expected.

---

## 4. THE "LOADED BUT UNUSED" EVALUATION

Mods whose content is invisible because the player cannot build it. **Earns its slot** is judged
*only* on the counterfactual: **does this augmentation system exist?** "Undocumented" = zero
mentions in `design/Jawa/mods/required_mods.md`, i.e. installed without a design entry.

| mod (packageId) | ships | bridge-placeable | earns its slot IF this system exists? |
|---|---|---|---|
| **VFE – Props and Decor** (`vanillaexpanded.vfepropsanddecor`) | ⭐ **1,828 `VFEPD_` defs** — the largest single block in the stack. Includes a whole *destroyed* family (`DestroyedLargeThruster`, `DestroyedGravExtender`, `RuinedLabBarrel`, `AncientCratePile`, `AncientFuelTank`) | ✅ `spawn_thing` | ⭐⭐ **YES, decisively.** Props are map furniture by definition; a props pack with no map-authoring system is *pure* dead weight. Carries C1, C2, A7 alone. **Undocumented in `required_mods.md`** |
| **Fortifications – Industrial** (`aoba.fortress.industrial`) | `AM_Palisade`, ~~`AM_Palisade_Embrasures`~~ → `FT_Palisade_Embrasures`, ~~`AM_PalisadeGate`~~ → `FT_PalisadeGate`, `AM_Entrance_Bunker` (~588 defs; the mod uses **both** an `AM_` and an `FT_` prefix — corrected 2026-08-20) | ✅ | ⭐ **YES** — the only source of a *defensible NPC compound* silhouette. Carries D2. **Undocumented** |
| **Vanilla Helixien Gas Expanded** (`vanillaexpanded.helixiengas`) | `VHGE_GasGeyser`, 2 generators, `VHGE_GasPoweredRefinery`, pipes, tanks | ✅ | ⭐⭐ **YES** — it *is* the owner's example. `required_mods.md:489-492` already mandates stripping the pump so gas is **found, never manufactured**; this system is what "found" then means. Without it the mod is a stripped shell |
| **Rimefeller** (`dubwise.rimefeller`) | `OilWell`, `DeepOilWell`, `RefineryLoadingBay`, pipe net | ✅ | **YES** — `required_mods.md:517` already says *"place pre-built + strip buildability"*. That sentence describes this system and nothing else has ever consumed it |
| **Ancient Mining Industry** (`xmb.ancientminingindustry.mo`) | 12+ mine maps + a mining→screening line ruled **"do NOT build it"** (`required_mods.md:389`) | ✅ | **YES** — the explicit self-limit makes it 100% map furniture. Currently loaded on the strength of its mission maps alone |
| **VFE – Production** (`vanillaexpanded.vfeproduction`) | a second production-bench tree | ✅ | ⚠️ **NO — and it is a live pillar risk.** An unaudited second industrial tree, the exact shape that got Ancient Mining Industry self-limited. **Undocumented.** Audit or drop; do not launder it as furniture |
| **Quarry** (`ogliss.thewhitecrayon.quarry`) | a player-buildable **infinite resource faucet** | ✅ | ⚠️ **NO.** Named-forbidden shape (`required_mods.md:489`, `:515`). **Zero doc mentions.** Belongs in a drop/strip decision, not this catalogue |
| **Outer Rim – Furniture & Decor** (`neronix17.outerrim.furnitureanddecor`) | SW furniture + decorative buildings | ✅ | **YES, conditionally** — the only SW-native furniture. `required_mods.md:611` says only *"cosmetic, pillar-neutral"*; **no buildability call was ever made** |
| **Torment Master** (`vlvop.tormentmaster.expansion`) | 6 cruelty buildings | ✅ | **YES** — already scoped *"Hutt cruelty flavour + fodder for authored tile maps"* (`required_mods.md:1477`). This system is the consumer that ruling assumed |
| **Effigys – Terror Spikes** (`yourname.effigys.mod`) | effigy building, fear aura | ✅ | **YES** — already ruled *"map decor within Hutt territories"* (`required_mods.md:1470`) |
| **Gerrymon's Dungeon Props** (`gmmp.dungeon`) · **Space Base Furniture** · **Tabletop Decorations** · **More Sculpture** · **Medieval Signs** · **Shavius's Medieval Flavour** | prop/decor packs | ✅ | **MARGINAL.** All **undocumented**, redundant against 1,828 `VFEPD_` defs, two are off-theme. **Drop candidates even with this system** |
| **Functional Vanilla Expanded Props** (`mlie.functionalvanillaexpandedprops`) | makes VFEPD props *functional* | n/a — adjuster | ⭐ **YES** — this is what makes a placed refinery **actually produce**, i.e. the owner's word "functional". **Undocumented.** Verify it covers the VFEPD refinery/tank props before relying on A5 |

**The argument, stated once:** ~2,500 loaded defs across these mods are reachable only through a
build menu Cherry Picker is meant to close. **This system is the only mechanism that converts
them from load-order weight into content.** Two are *not* rescued by it — **VFE – Production**
and **Quarry** are unaudited player-power trees, and calling them furniture would be laundering.

---

## 5. THE CHERRY PICKER AUDIT SPEC

If these items appear on maps but must never be player-buildable, the **recipe** goes and the
**def stays**.

> # ⚠️ THE WHOLE POINT OF THIS AUDIT
> **Culling a def that a map spawner references BREAKS THE SPAWN.**
> Cherry Picker deletes a def **from generation AND from every menu** — `cherry_picker_killlist.md:40`,
> bucket **B**, ⛔ **irreversible, cannot be changed mid-save**. A `GenStep_ScatterThings` whose
> `thingDef` no longer exists does not place a broken refinery; **it places nothing, silently**,
> and the tile reads as unaugmented. **Every def in §2 is bucket-B-forbidden.**

### The three outcomes the audit must assign per def

| outcome | mechanism | reversible | use when |
|---|---|---|---|
| **KEEP + UNBUILDABLE** ⭐ the default | `PatchOperation` clearing `<designationCategory>` | ✅ delete one file, redeploy | the def must still **spawn**. **Every §2 def.** Precedent: `Jawa_Doctrine/Patches/NoDroidManufacture.xml` |
| **KEEP + UNCRAFTABLE** | remove the `RecipeDef`, not the `ThingDef` | ✅ | the thing is crafted at a bench rather than placed |
| **CULL** | Cherry Picker | ⛔ **never** | **only** defs with **zero** map-spawn references. Requires proof, not assumption |

### What the audit checks, per def in §2

1. **Referenced by any `GenStepDef`, `ScatterableDef`, `PrefabDef`, `StructureLayoutDef` or
   `TileMutatorDef.extraGenSteps`?** If yes → **CULL is forbidden**, no exceptions.
2. **Carries a `<designationCategory>`?** If no, it is already unbuildable — **record the clean
   bill and move on.** Precedent for that as a valid result: `required_mods.md:433`.
3. **Carries a `RecipeDef` or `ResearchProjectDef` gate?** Strip the recipe, keep the def.
4. **Clearing a field cannot orphan a cross-reference; deleting the def can.** Hence outcome 1.
5. **Re-validate:** `python skills\rimworld-modding\scripts\validate_patch.py <file> --live`.

### Named prerequisites already prescribed and never executed

| target | prescribed at | state |
|---|---|---|
| Helixien pump/extractor — strip buildability | `required_mods.md:489-492` | ⛔ **not done — "the infinite starting pocket is live"** (`:494`). Blocks A3–A5 from being coherent |
| Rimefeller `OilWell`/`DeepOilWell`/`RefineryLoadingBay` — place pre-built, strip buildability | `required_mods.md:517-519` | ⛔ not done. Blocks F4 |
| Quarry (`ogliss.thewhitecrayon.quarry`) | — | ⛔ **no entry at all.** Infinite faucet, undocumented |

⚠️ **Timing.** Cherry Picker applies **at generation** and the kill-list freezes at campaign start
(`cherry_picker_killlist.md:163`), so **the audit runs BEFORE the world is rolled.** A
`designationCategory` strip has no such constraint — another reason it is the default.

---

## 6. OPEN QUESTIONS

### 6.1 ⭐ Can a mod read the worldmap and faction ownership of the tile it is generating?

**The owner flagged this himself. It gates 5 catalogue rows (A6, D2, D3, D4, F5) — every row with
faction defenders.** Split into three questions that have been conflated:

| # | question | state |
|---|---|---|
| a | **Does a tile→faction ownership source exist at all?** | ✅ **YES.** `Faction Territories and Vassalage` (`jaeger972.factionterritories`, load 434, 1.6) is **already loaded** and draws *"deterministic faction territory regions around settlements"* — a Voronoi over settlements. Assembly exposes `GetFactionTerritoryColor`, `IsValidTerritorySource`, `ExecuteCedeToFactionAtTile`. **Deterministic** ⇒ also derivable independently from `Find.WorldObjects.Settlements`, without depending on the mod |
| b | **Readable at *map-gen* time?** | 🔎 **Almost certainly yes — this is reasoning, not measurement.** Map gen runs when the player enters a tile, long after worldgen, so `Find.World` / `Find.FactionManager` / `Find.WorldObjects` are populated and a `GenStep` has `map.Tile`. **Nothing has been measured.** |
| c | **Reachable from XML alone?** | ⛔ **NO — the real blocker.** No `LandmarkDef`/`TileMutatorDef`/`GenStepDef` has a "faction of this tile" field. ⚠️ `GenStep_Outpost` takes its faction from **`map.ParentFaction`**, which on a **player-settled tile is the player** — the vanilla step would generate the garrison *as the player's own pawns* |

**What would settle it:** a ~40-line `GenStep` subclass resolving the nearest settlement's faction
from `map.Tile` and handing it to `PawnGenerator`. **A build, not an experiment** — and the *only*
new C# the entire catalogue needs.

**Who owns finding out.** **CHECK** owns the *live* half and holds the blocking tool:
`jawa/list_factions`, V1-CRITICAL and **shutdown-gated**; as per the trap file,
**no faction, world or settlement tool** exists among the current 139, so faction data comes from
`save_game` + a `.rws` grep meanwhile. ⚠️ **Worldgen-time access is a separate question and nobody
owns it** — it is *not* CHECK's, since the bridge drives a running game and cannot observe a
`GenStep`. Assign it explicitly.

### 6.2 Secondary

| # | question | owner |
|---|---|---|
| a | What do `AncientGarrison` / `AncientQuarry` / `AncientWarehouse` / `AncientChemfuelRefinery` **already produce** on the desert world at vanilla `commonality 0.2`? Free information; may satisfy "every tile deserves something" unaided | CHECK — one live sighting |
| b | Does `Functional Vanilla Expanded Props` actually make the VFEPD refinery/tank props *produce*? A5's word "functional" rests on it | BUILD — offline read |
| c | Does placing running industry violate the anti-exponential pillar? A *found, working* refinery is closer to a faucet than a ruin is | DECIDE — `enrichment_agents.md:33-39` |
| d | 60+ `VEE_*` landmarks from Vanilla Landmarks Expanded are live and unaudited against the desert palette | `[?]` |

---

# 7. THE SECOND AUGMENTABLE SURFACE — authored interior maps

_Added 2026-08-13 by a retired seat, from the owner's observation that the Space Tower
"dungeon" is itself a tile we could augment on approach. **It is, and it is a
better one than the world tile.** Measured from the mod on disk, not inferred._

## 7.1 What these are actually called

RimWorld has **no noun for "dungeon"**. Four different things get called "the
map" in conversation and they are not interchangeable — this is the vocabulary,
so specs stop drifting:

| what the player sees | the engine's noun | when it exists |
|---|---|---|
| a hex on the planet | **world tile** (1.6: on a planet **layer** — Surface, Orbit) | at worldgen, forever |
| the thing sitting on that hex | a **world object** / `MapParent`; the quest kind is a **Site**, built of `SitePartDef`s | when the quest fires |
| the playable grid you land on | a **Map**, produced by a `MapGeneratorDef` running `GenStep`s | **on arrival** |
| an interior level you descend into | 1.5+ **pocket map** | on entering |

**So "map tile" is two things and the difference is the whole point.** A world
tile is *persistent* — you augment it once and it stays augmented. A site Map is
*generated on arrival and discarded on leaving*.

## 7.2 Why the discarded one is the better target — the design finding

**Augmenting a world tile costs save weight forever and can only be done once.
Augmenting a site map costs nothing and can be done differently every visit.**

That inverts the usual assumption. It means authored interior content is
**cheap, repeatable, and safe to be lavish with** — the exact opposite of the
world-tile catalogue above, where §0's "downright replete" tiles have to be
rationed because every one of them is permanent.

⭐ **And it is the one place in RimWorld where authored detail survives the
player.** A colony map gets bulldozed — anything we hand-place is gone by year
two. **A site map is experienced as a place and then left behind intact.** Art
and detail spent here is the only map art the player never demolishes.

## 7.3 The mechanism is already installed and nobody has used it

**`HaiLuan.CustomQuestFramework` is ACTIVE at load 108 of 575** — as of 2026-08-13; the
owner's list is 578 as of 2026-08-20. Space Tower is
not one dungeon mod; **it is one dungeon built on an authoring format we already
have and are paying for.** Measured in
`…\workshop\content\294100\3527936083\1.6\Defs\QuestEditor_Library.CustomMapDataDef\`
— six files, 922 lines total, the whole tower:

- The def type is **`QuestEditor_Library.CustomMapDataDef`** — a hand-authored map.
- Fields observed: `size` (`(31,1,31)`), `terrainsRect`, `roofRects`, `thingDatas`,
  `pawns` (`kindDef` / `faction` / `count` / `spawnType`), `tags`, `commonality`.
- **Levels link by TAG, not by name.** `CustomThingData_CustomMapEntrance` carries
  an `exitName` and a `tagWithChance` list — the tower's entrance rolls against
  tag `ST_TowerLevel`, so **which level you get is drawn from a pool.** Author
  five levels, get a different tower every run, for free.
- `CustomThingData_InteractableThing` carries an `operations` list — scripted
  interactables, i.e. a lever that does something, not just scenery.

**A 31×31 authored map is ~100–240 lines of XML.** That is the actual price of a
dungeon here.

## 7.4 What this is for in THIS campaign, and what it must not become

**A dungeon in a Jawa campaign is a wreck.** Not a tomb, not a vault, not a
fantasy dungeon in space — **a machine that stopped, with the crew still in it
and something in the hold.** The player's verb is *strip*, not *delve*, and the
reward is parts. Anything authored here that does not end with the clan dragging
something home is off-brand however good it looks.

⛔ **The discipline, because this format makes overproduction easy:** the
tag-pool draw means **variation is cheaper than volume**. Five levels in one pool
beat five separate dungeons, and the player cannot tell the difference from the
inside. **Author few pools, deep.** A campaign with thirty hand-made dungeons is
a campaign nobody finished building.

## 7.5 Consequences for other seats — filed, not assigned

- **CHECK's augmentation surface is bigger than the world map.** A site Map is
  an ordinary `Map` once generated, so the live bridge can dress it on arrival.
  ⚠️ **The hook is different**: world tiles are edited whenever; a site map does
  not exist until the player lands, so the trigger is map-generation/arrival.
  **Nobody owns that hook.** Assign it.
- **BUILD:** this raises the value of the Space Tower read (V11), because the
  answer covers the *format*, not just the one mod.
- ⚠️ **Not v1.** v1 ships one quest and three terrain overrides. This
  is a **v2 content pillar** and is recorded here so it is not re-derived.

⭐ **The storyline half of this is now written** — the towers are the Empire's
surface access and the Hutts pay to have them cut:
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\orbital_towers_and_the_sky_ladder.md`
Skyhook and elevator variants are on the register there, `[v2]`.

---

# 8. NEW HAZARD PALETTE — owner, 2026-08-13

_Four concepts recorded the hour they were raised. **The first three are for the
wild jungles and marshes of the Three Waters; the fourth is a general map
augmentation.**_

## 8.1 Wildpods — *the jungle and the marsh*

⚠️ **CORRECTED. I first read "pods" as seed pods and wrote a paragraph about
botany. Wrong. Wildpods are GIANT ANIMALS that move in pods.**

> **Megafauna, in groups, living where the water is.**

⭐ **This is a better version of the thing I credited to briar — a presence that
shapes the route, except it MOVES.** A pod of giant animals is not a raid and not
a hazard. It is a fact occupying part of the map, and the player plans around it
the way you plan around weather that has legs.

### Why they matter more than their meat

⭐ **They explain the jungle.** The obvious question about a desert world with
three green regions is *why has nobody taken them?* **Because something enormous
already has.** The pods are simultaneously the reason the jungles are worth having
and the reason they are still empty — one fact answering two questions, which is
the cheapest kind of worldbuilding there is.

⭐ **And they are the Wildsteam Clan's whole claim to existence.** Wookiees, Ewoks
and every other badly desert-adapted settler live in exactly the jungles the pods
occupy. **They are the only people who came to terms with them** — herding,
avoiding, or hunting on terms the pods tolerate. That is why a faction of
cold-adapted forest species survives on a thirst world at all, and it is far more
interesting than "they live where it is cooler."

### What they must be, mechanically

- **Thrumbo-class, in groups.** Passive until provoked, catastrophic when
  provoked. ⛔ **Not a manhunter pack** — a pack of giants that decides to attack
  a starting colony is not a hazard, it is a save-deleting event.
- **Enormous yield.** On a world where food is pressured, one wildpod is a
  season. **Killing one is a project, not a fight** — and that is the point: it is
  the largest deliberate undertaking available early.
- **They should move between the three water regions**, so a pod is news rather
  than scenery. A herd that arrives is an event; a herd that is always there is
  terrain.

⚠️ **Feasibility looks good and I have not checked it properly:** **Megafauna is
already active** in the stack and was noted as contributing nothing to the crags.
**It is the obvious donor** — BUILD surveys what it ships before anything is
authored.

## 8.2 Poison briar and thorn fields — *the jungle*

**Static, dense, passable at a cost. Area denial by terrain rather than by
threat.**

⭐ **This is a register the campaign does not have yet.** Everything hostile on
this planet currently either *chases you* (raids, the pursuit) or *punishes
lingering* (the Agarilux spore bubble at radius 8). **Briar does neither — it
shapes the route.** You do not fight it and you do not flee it; you go around, or
you pay to go through.

**And that is exactly what a jungle should do to a caravan.** It is also the
cheapest way to make the Three Waters feel defended without adding a single
warrior.

## 8.3 Quicksand and sink-silt — *the marsh, and the deep*

**Terrain that traps, and can kill.**

⭐ **It defends the water for free.** The Deepwater Compact's power rests on
holding the only water worth having, and a marsh that swallows caravans enforces
that **without them fielding anyone.** A faction whose power is geography is far
more convincing than one whose power is a goodwill number.

⭐ **And "sink-silt" has an obvious second home: the seafloor.** The same
mechanic, in the deep, is the thing that makes walking the bottom frightening —
and `AA_SandProwler` already *burrows through loose substrate and ambushes from
beneath it.* **Sink-silt is where a sand prowler lives.**

## 8.4 Tar pits and resin flats — *anywhere*

**A general map augmentation, not tied to the jungles.**

⭐ **The best thing about tar is that things die in it and STAY.** A tar pit is
not just a hazard and a chemfuel source — **it is a salvage site with bodies in
it**, preserved for however long the fiction wants. **For a clan whose economy is
stripping what other people left behind, that is a gift.**

- **hazard:** movement, entrapment, fire
- **resource:** chemfuel and industrial feedstock
- ⭐ **content:** whatever went in and did not come out

**Resin flats** read as the drier, brittler cousin — a sheet rather than a pool.
Same family, different silhouette, and a better fit for the deep desert where a
liquid pool would not survive the heat.

## 8.5 Feasibility — what exists, and what does not

⚠️ **Recorded as design, not as buildable. BUILD owns the survey.**

| concept | what may already exist |
|---|---|
| **tar pits** | ⭐ **Alpha Biomes ships `AB_TarPits` as a BIOME.** The owner wants it as a *patch on other maps* — so the question is whether its terrain and props can be scattered by a `GenStep` outside their own biome |
| **quicksand / sink-silt** | unknown. Swamp and marsh mods are the place to look; Biomes! Islands and the Greater Swamps family are candidates |
| **poison briar** | the existing hostile-flora audit found **only one** damaging plant in the whole stack — Alpha Biomes' `AB_AgariluxPrime`, a radius-8 gas emitter. **Briar is a different mechanic and probably does not exist yet** |
| **wildpods** | ⭐ **Megafauna is ACTIVE** and is the obvious donor — giant animals already exist, the work is herd behaviour, placement and yield. **Likely the cheapest of the four** |

🔴 **The honest read: wildpods and tar are likely cheap — both have donors in the
stack. Briar is probably new work**, since the hostile-flora audit found exactly
one damaging plant in the whole install and it is a gas emitter, not terrain. All four are `[v2]`, and none of them should be authored before the sea
step and the biome mix land.
