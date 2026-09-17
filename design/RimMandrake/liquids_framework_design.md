# Liquids Framework — one substance, many faces

**Status: RULED (owner, 2026-09-13, bench session).** Core registry + client mods,
campaign-first. Supersedes and absorbs `design/Jawa/proposals/water_economy_deep_design.md`
(deleted this change; its detox chain survives here as the `thirstQuality` ladder).
Naming per `design/NAMING_SCHEME_PLAN.md` — core and clients are RimMandrake tier;
Ash'karr wiring lives in RimUtinni; cuisine consumers live in RimStarWars.

🔴 **CORRECTED 2026-09-16 — `RimMandrake: Liquid Logistics` will never ship as a
separate mod.** Ruling 11 of `design/RimMandrake/flowworks_mod_definition.md`
supersedes this: the hoses, portable pumps, universal cargo tank, universal pump and
per-net adapters described below (§4's "Tanker raid"/"Universal tank interop", §5's
client-mod row, §7 phase ⑨) are `FlowWorks`' own hardware, absorbed into the single
liquid-domain mod along with the occupancy engine, the registry and the canal/pit
family (rulings 11, 14, 18 of the same document). `LIQUID_LOGISTICS_MOD_1` is stale
in the ledger and needs closing by whoever owns it next — see
`FLOWWORKS_BUILD_PROGRAM_1`.

The dream this scopes: every liquid in the game interchangeable across every place
liquids appear — terrain (rivers/lakes/oceans), bottles and buckets, pipes, worldmap
bodies, rain, canal flooding, and fluid-to-fluid transformation.

## 1. Design pillars

1. **One substance, many faces** — a liquid is defined once; terrain, bottle, canal,
   pipe, weather, worldmap and recipes are optional *form slots* on that definition.
2. **Pulsed spread only** — all map motion is event-shaped (flood, drip, spill,
   seasonal) via the **FlowWorks** engine (named by his ruling of 2026-09-16;
   the rename is ordinary owed work under `FLOWWORKS_BUILD_PROGRAM_1`, no gate). No
   per-tick fluid sim, ever. (Owner ruling.) 🔑 As of 2026-09-16 the engine's motion is a **sort plus an overflow** over the depth
   grid — deepest cells fill first, a full cell overflows to neighbours with room — which is what
   keeps this pillar satisfiable at all.
3. **TerrainDef stays the engine face** — the registry points *at* terrain suites
   (including adopted vanilla/DLC/third-party terrains); it never replaces them.
4. **Industry is found, not built** — crude conversions always buildable; household
   tier by research; industrial scale only as pre-placed set-pieces. (Campaign law;
   the public wave may allow building industrial via a settings switch.)
5. 🔴 **SUPERSEDED 2026-09-16 — "every client ships alone" no longer describes this family.** It
   read: *"the core is data + glue; each client mod is independently playable and degrades gracefully
   when a sibling is absent."* His consolidation ruling makes the core, the roster, the engine and the
   hardware **one mod**, so there are no siblings left to ship apart. What survives of the pillar, and
   still binds: **graceful degradation.** FlowWorks must work with any optional third party absent —
   Alpha Biomes, Dubs Bad Hygiene, VE PipeSystem, VGE — which for the absorbed ManyWaters rows means a
   tinted-vanilla fallback per row, so a liquid never *vanishes*, only its look degrades. The remaining
   true siblings (`GelatinousSlime` registering rows, `WreckedMachines` owning conversion,
   `FloodedCanyon` as a flood driver) each depend on FlowWorks one-way and must degrade to nothing
   without it.
6. **Superb Mod Settings** — every feature a toggle, defaults = shipped behavior,
   all-off is a working game (per the 2026-09-12 standing rule).

## 2. Core: `RimMandrake: Liquids` (grows out of LiquidTypes)

New top-level def type `RimMandrake.LiquidTypes.LiquidDef`, defNames `RM_Liquid_<Name>`
(top-level custom def — avoids the `<li>` custom-loader trap). The existing
`RM_LiquidProperties` DefModExtension stays as the *terrain-side* carrier, emitted by
the generator from registry rows, so third-party terrains remain patchable without a
LiquidDef.

**Property block** (source of truth per liquid): `viscosityClass`
(Thin/Water/Thick/Heavy — drives canal `ticksPerTile` defaults, later wade speed),
`pH`, `damageOnContact/Immersion`, `corrodesApparel`, `flammable`, `igniteTemp`,
`color` (tint for generated art, flecks, bottle fill).

**Form slots** — each nullable (null = the liquid does not take that form; ConfigErrors
requires at least one):

| slot | meaning |
|---|---|
| `terrainSuite` | shallow/deep/chest-deep TerrainDef refs; may ADOPT existing terrains |
| `canalFluid` | FlowWorks `FluidDef` ref (soft, MayRequire-style) — pulsed spread row |
| `bottled` + `unitsPerBottle` | the item form |
| `bottleBehavior` | `revertsTo`+`revertTicks` (boiling/icy → fresh); `rotsTo`+`rotTicks` (blood) |
| `pipeResource` | VE PipeSystem net (patched in only when VE Framework loads) |
| `weather` | WeatherDef for "rain of X" events (v2 for new ones) |
| `worldTag` | typed worldmap bodies (authored onto the frozen map) |
| `conversions` | list of {tier: Crude/Household/Industrial, product, recipe/building} |
| `trade` | marketValue/unit + tradeTags |
| `cuisineTags` | ingredient categories the RSW cuisine mod cooks against |
| `thirstQuality` | Distilled/Potable/Fouled/Toxic (absorbed detox chain) |

`Tools/generate_liquid_suite.py` grows to emit terrain suites, bottle ThingDefs and a
compat index from rows.

## 3. v1 roster (ruled)

| Liquid | Notes |
|---|---|
| Fresh water | adopts vanilla waters; the product of most conversions |
| Salt water | adopts vanilla ocean; → fresh at household still / found desal |
| Boiling water | `RM_WaterBoiling`; bottled form reverts to fresh |
| Icy water | `RM_WaterFrigid`; bottled form reverts to fresh |
| Toxic water | `RM_WaterPoisoned` + adopted Odyssey toxic suites; → fresh (crude drip-filter slow / found detox) |
| Acid water | `RM_AcidWater` (the wired corrosion liquid); → fresh (industrial only) |
| Tar | `RM_Tar`; Heavy viscosity; → chemfuel at found refineries |
| Slime RED / GREEN / WHITE | **distinct rows** (distinct hazards + cuisine tags) — the REALLY-want trio; viscous streams and pools via Heavy-viscosity canal fluids |
| Slime YELLOW | actual human snot — kept as the documented **example row** others follow for disgusting uses in other scenarios |
| Blood | **item-only in v1** — bottled, rots (CompRottable), household recipe → hemopack before spoil; map pooling is v2 |
| Chemfuel | **adopts the vanilla item**; VE pipes carry it; tar cracks into it |
| Astrofuel | **adopts Vanilla Gravship Expanded** — the `VGE_Astrofuel*` net (pipe/tap/valve/drain/giant tank/synthesizer) already exists in the campaign dump; optional-checked, supported when present |
| Brine | **minimal row** (terrain + worldTag + canal only) — forced back into v1 by ruling 5: `LIQUID_BIOMES_MAP_1` already authored TWO brine seas onto the frozen world, and typed tiles must have rows. `RM_WaterBrine` terrain exists |
| Propane | **minimal row** (terrain + worldTag + canal only) — same forcing: the frozen world holds a propane lake under Umbra. `RM_Propane` terrain exists |

The frozen world's authored liquid bodies (boiling ocean, two brine seas, propane
lake — `LIQUID_BIOMES_MAP_1`, done) are the floor of the roster: every authored body
gets at least a minimal row, or ruling 5 cannot hold.

**Dropped/cut**: purple slime (dropped, owner 2026-09-13). **v2+/deferred**: machine
oil and cooking oil as distinct rows (chemfuel + cuisine tags cover the fantasy),
nuclear wastewater, ammonia/coolant/brackish/mineral waters (the LiquidTypes terrains
stay shipped, no registry rows yet), lava (STUDY Lava Must Flow first),
hemogen/beer/milk adoption rows, basic (alkaline) water, kolto/bacta healing rows
(see §8).

## 4. Mechanics

**Pulsed spread — REWRITTEN 2026-09-16.** This paragraph described `Flood_FlowWorks` +
`CompFluidReservoir` generalising with an auto-prime path for natural sources. Both halves of that
are now dead: the vanilla `Flood` subclass is **dropped** for a `MapComponent`-owned walk, and
`CompFluidReservoir` is **deleted** (ruling 24) because a source is no longer a building.

What replaces it: every excavated cell carries `depth` D (shallow/mid/deep/SUPERDEEP) and `fill` F,
with `0 ≤ F ≤ D`. Each pulse, over the connected excavated set — sort deepest-first, pour to `F = D`,
and a full cell **overflows** into neighbours with room. A natural source is simply a SUPERDEEP cell
that is already full, so it spills into any channel dug at its edge and needs no priming path at all.
Spills are one-shot releases; viscosity maps to `ticksPerTile` bands (Heavy = slow oozing — the slime
look). Detail: `design/RimMandrake/flowworks_mod_definition.md` §21.

🔴 **Scarcity is STOCK, not rate — owner, 2026-09-16, a FULL REVERSAL of this
document's original line.** Every source carries a real volume and conservation of mass
holds everywhere; "limitless" means only that a source's stock is large enough never to
matter (a map-edge body). A source is debited by canal fill and by pumping, strains
visibly as it is drawn down, recedes cell by cell, and — if it is a limited source, one
fully inside the map — refills slowly from rain, season and ground seepage, slowest for
a small body. ⚠️ **This does not weaken pillar 2**: the volume is debited at each pulse,
never simulated per tick. A stock model and "no per-tick fluid sim, ever" are
compatible, and the reversal is not licence for a sim. `CompFluidReservoir` is a rate
today and must gain volume accounting; the design is drafted in
`design/RimMandrake/flowworks_mod_definition.md` (DRAFT — the owner has ruled the
reversal, not the mechanism).

⚠️ **Engine status — CORRECTED 2026-09-16 (this document was stale).** All three
`FLUID_CANAL_FLOOD_TUNING_GAPS_1` defects were fixed **2026-09-02**, eleven days before
this document first described them as open, and the item is **closed at `747b0025`**.
Verified by reading the source this date: `SpreadFlood` writes `SetTempTerrain` +
`QueueRemoveTerrain` so a release is recoverable and the floor returns (and the flood
terrains deliberately carry no `tempTerrain.destroysFloors`); a boxed-in flood
self-destroys at `ExpiryTick = spawnedTick + 2 * FloodingTicks`; and `ticksPerTile` is a
real per-fluid field with `MaxFloodDurationTicks` derived from it, so it is a duration
again. `FLUID_CANAL_FLOOD_LIVE_CHECK_1` is closed too. **There is no flood-correction
pass owed** — the deleted claim that "nothing builds on the engine until those
corrections land" was blocking work that had already landed.

🔴 **The real engine gap, MEASURED 2026-09-16: spread is not channel-constrained.**
`Flood_FlowWorks` inherits vanilla `Flood`'s gating and spreads from its seed across
any open, non-water, non-edifice ground — it does not follow the dug channel. Every
canal fantasy in this document assumes a channel *contains* its liquid. This, not the
fixed tuning defects, is what the engine owes.

**Bottles are real items** (scavenger law): `RM_BottleEmpty` → fill (at terrain edge or
tank) → `RM_Bottle<Liquid>` (generator-emitted per row) → use produces `RM_BottleDirty`
→ wash job (consumes water) → empty again. Buckets = bigger bottle, same chain.
Dirty-bottle stage is a Mod Settings toggle; **default ON in the campaign** (it is the
shipped behavior); off = use returns a clean empty. Bottles are loot, not free.

**Special behaviors** — all data, no per-liquid C#: revert timer (boiling/icy → fresh
bottle), rot (blood; convert to hemopack at household tier to stabilize), viscosity
classes (data-only in v1 beyond canal speed).

**Thirst chain.** Thirst is live in the campaign: `DBHThirst` NeedDef is in the frozen
dump (MEASURED, capture 2026-08-29) via the "Dubs Bad Hygiene – Thirst" add-on riding
DBH Lite. Chain: crude (solar still, drip filter — slow, free) → household (fueled
still/boiling — research) → industrial (found desal/detox set-pieces — fast, powered).
We register bottles as DBH drinkables and patch the water tag onto adopted terrains;
with DBH absent (public), bottles are plain ingestibles with a hydration thought.
Aquifer-remembers (draining degrades quality) deferred to v2.

**Tanker raid** (pillar; ~~lives in Liquid Logistics~~ — **FlowWorks'**, since 2026-09-16, §6): fly to a typed liquid body →
deploy `RM_HoseSpool` (fast-build, cheap, fragile conduit-thing hose with a length cap
— NOT terrain, NOT a VE pipe) from shore to ship tank → `RM_PumpPortable` (found or
stolen, heavy) pulses N units per interval from any cell whose terrain belongs to a
LiquidDef into `RM_ShipTank` → undeploy, fly away rich. Raid pressure = time on the
ground while pumping. A "tanker ship" build is a first-class, highly viable player goal.

**Universal tank interop** (owner ruling): the ecosystem's existing tank families are
ADOPTED, never duplicated — VE PipeSystem (`PS_ChemfuelTank`, `PS_DeepchemTank`), VGE
astrofuel, KotOR water/kolto, Rhydonium/Tibanna. We ship exactly ONE new storage
building: the **universal cargo tank** — minifiable, holds any (LiquidDef, amount) —
plus a **universal pump**, and per-net ADAPTERS so every supported pipe network can
feed from and draw into our tank, and existing pumps can pump from it.

**Liquid trade** (owner-ruled 2026-09-13: BOTH routes — "it's that important").
Nothing in vanilla or the mod list trades bulk liquid; this is new mechanism.
Two routes, both v1:
- **Barrels** — a real item family (~25 units, the bottle chain's big sibling:
  fill/empty bills at the tank, dirty barrels pile up like dirty bottles, barrels
  are loot). Trade stays 100% vanilla — every trader buys and sells barrels today,
  zero patches. Owner: "barrels are also a thing to keep in the game. Very
  scavenger."
- **Bulk broker interface** — pump-to-sell AND pay-to-fill, both directions,
  price = row marketValue × amount, weighted by the settlement's world tag
  (desert pays more for water). **Ruled later the same day: the broker lives as
  the Broker TAB of The Bazaar** (`design/RimMandrake/bazaar_trade_window_design.md`
  §2), our own Dialog_Trade replacement — which also supersedes the "no
  trade-window Harmony" caveat that applied when we only had a small rider
  patch in mind. **FlowWorks** owns the tank/pump/hose hardware (was Liquid Logistics, absorbed
  2026-09-16); the Bazaar still owns the Broker tab.
Bottles trade natively as ThingDefs either way (tradeTags per row).

**Typed worldmap → mapgen.** One authoring pass writes `worldTag` values onto the
frozen Ash'karr map's water tiles/named bodies (WorldComponent keyed by tile ID,
authored through the bridge — no worldgen, no re-render, per the no-worldgen law). On
map generation, a GenStep reads the landing tile's tag and *repaints* the generated
shores/lakes to that liquid's suite. Untyped tiles = vanilla, untouched. This is what
makes "fly to that tar lake" true for the tanker raid.

**Found industry.** `RM_GenStep_PlacedSetPieces` (exists) scatters authored set-pieces:
desal plant on brine coasts, detox works near toxic bodies, tar-cracking refinery,
pumping station — each WreckedMachines-tier (Wrecked→Kludged→Repaired), found broken,
repaired into the industrial conversion tier, **never buildable from the menu** in the
campaign. Set-pieces stock stealable pumps and tanks feeding the tanker pillar.
**WreckedMachines gains a Distillation module** on the players' ship: clean water from
appropriate sources (not oil).

**Star Wars cuisine hook.** Core ships `cuisineTags` + ThingCategories on bottled rows;
the RSW cuisine mod writes recipes against tags, never against defNames — new liquids
auto-join the pantry.

## 5. Client-mod map

🔴 **SUPERSEDED IN PART — owner, 2026-09-16: the many-clients shape is replaced by ONE mod,
named `FlowWorks` by ruling 20 the same day** (he called it "Fluidity" in the consolidation
ruling below, earlier the same session; that name did not ship). *"I do want to absorb Many
Waters and Canals together into a single Fluidity mod. All of
it. Universal containers, flexible tubing, pumps, surface transient flow, canals, sources & sinks."*
He answered this document's own cadence argument: *"I understand your argument about constant updates.
I don't think that's actually going to happen. We're going to include a big set of options. Others can
extend later via our framework."*

**Certain**: `FlowWorks` + `ManyWaters` + the planned `RimMandrake: Liquid Logistics` + the surface
flood driver all become **`FlowWorks`**. Liquid Logistics therefore never ships as its own mod, and
pillar 5 ("every client ships alone") no longer describes this family — one mod cannot ship alone
*from itself*. The rows/hardware/engine boundaries survive as INTERNAL structure, which is still worth
keeping: it is what stops the hardware writing stock bookkeeping directly.

**Not yet ruled** — whether `LiquidTypes`/`RimMandrake: Liquids` (the registry), `GelatinousSlime` and
`WreckedMachines`' distillation also dissolve into FlowWorks, or stay as siblings extending it. Until
he rules, treat the rows below for those three as live. Design detail:
`design/RimMandrake/flowworks_mod_definition.md` §16.

| Mod | Becomes |
|---|---|
| **LiquidTypes** → `RimMandrake: Liquids` | the core registry + generator; keeps `RM_LiquidProperties` for foreign terrains — ⚠️ FlowWorks boundary unruled |
| **FlowWorks** | the whole domain: occupancy engine, canals, sources, sinks, sluice gates, surface transient flow, roster, hardware. Named by ruling 20 (2026-09-16); the rename itself is `FLOWWORKS_BUILD_PROGRAM_1` Phase 1 work, not gated on anything |
| ~~**ManyWaters**~~ | **absorbed into FlowWorks** — its coloured waters and slimes become FlowWorks' rows, with a tinted-vanilla fallback per row so no liquid vanishes without Alpha Biomes |
| **GelatinousSlime** | slime-mechanics client: hediffs/genes stay; its terrains adopted — ⚠️ FlowWorks boundary unruled |
| **WreckedMachines** | + Distillation module; wreck-tier grammar for found industry — ⚠️ FlowWorks boundary unruled |
| **UtinniPatches (RUT)** | Ash'karr worldTag authoring pass; campaign settings defaults |
| ~~**NEW `RimMandrake: Liquid Logistics`**~~ | **never ships as a mod** — hoses, portable pumps, universal cargo tank, universal pump, per-net adapters and trade-from-tank are FlowWorks' |
| **FloodedCanyon** | 🔴 was missing from this map entirely. Becomes the **flood-driver client**: keeps its biome and phase clock, depends on FlowWorks for motion (ruling 8, 2026-09-16) |

**v1 third-party seams**: VE PipeSystem (pipe slot + tank adapters), DBH Lite + Thirst
add-on (drinkables), VGE (astrofuel net adoption), Odyssey (Flood subclass, toxic-water
adoption), Vanilla Fishing Expanded (`waterBodyType` per suite so typed waters fish
sensibly), Alpha Biomes (slime/tar terrain adoption).
**Deferred, seams documented only**: Rimefeller, No Water No Life, hemogen-pipe mods
(none in the campaign list). STUDY: Lava Must Flow before any lava row.

## 6. Fun expansions (accepted as candidates, not commitments)

v1-cheap: weaponized canal gates (flood the raider approach with tar/boiling water);
thrown flasks (bottled acid/boiling water as crude grenades); typed fishing exotics;
spa/bathing thoughts. v2: slip hazards on slime/oil; blood/slime rain; spill-scent
predator incidents; tank-mixing accidents (cross-connected tanks brew
`RM_ReactionLiquor`, with a bang).

## 7. Build phasing (each slice lands + quicktests alone)

① ~~**Flood-engine corrections**~~ — **DONE 2026-09-02, item closed at `747b0025`**
(see §4's corrected engine status; the defects this phase existed for were already
fixed). What the engine actually owes in its place is **channel-constrained spread** and
the **stock model** of the 2026-09-16 reversal. Their position in this order is the
owner's call, not this correction's: both are drafted in
`flowworks_mod_definition.md` and neither is ruled. → ② registry skeleton adopting
existing terrains (def-load test only) →
③ natural-source auto-prime + spills → ④ slime streams (Heavy FluidDefs, R/G/W/yellow
rows) → ⑤ bottles + Mod Settings → ⑥ revert/rot specials → ⑦ thirst chain +
WreckedMachines Distillation → ⑧ worldmap tags (bridge authoring) + landing paint
GenStep → ⑨ the hardware, in FlowWorks (tank → pump → hose → tanker loop → trade, in that
order — the tank alone is already useful) → ⑩ found-industry set-pieces.

## 8. Measured facts this design leans on (frozen dump, capture 2026-08-29)

- `DBHThirst` NeedDef present — thirst is live in the campaign.
- The frozen world already holds four authored liquid bodies as worldmap tiles:
  boiling ocean, two brine seas, propane lake (`LIQUID_BIOMES_MAP_1`, done) — the
  worldTag authoring pass (§4) builds on them, and they force the brine/propane
  minimal rows in §3.
- `VGE_Astrofuel*` full pipe net present — astrofuel row adopts, builds nothing.
- Tank families present: `PS_ChemfuelTank`/`PS_DeepchemTank`, VGE astrofuel, KotOR
  water + `KoltoTank` (buildable; healing function UNMEASURED — KotOR C#, needs a live
  look), Rhydonium/Tibanna, misc fuel/oxygen.
- Bacta: NO tank exists — only `OuterRim_BactaSpray` + `OuterRim_ApplyBacta`. A
  found/repairable bacta tank is a natural future healing-liquid set-piece; kolto and
  bacta are future rows.
- Workshop landscape: DBH and No Water No Life are incompatible incumbents each
  hardcoding their liquids; VE PipeSystem is the one generic pipe library; Lava Must
  Flow is the best liquid-as-terrain prior art; blood piping does not exist on the
  Workshop; nobody types worldmap bodies. The gap this framework fills is the shared
  substance model across terrain/worldmap/pipes/bottles/weather/transform.
