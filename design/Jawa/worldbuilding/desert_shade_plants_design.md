# DESERT_SHADE_PLANTS_DESIGN_1 — the two plants that defend the desert's shade

_Fable design pass, 2026-09-20. DECIDED — a build pass executes this without
re-deriving the trigger, damage-shape or tier questions. Nothing here is built.
Sources: `infrastructure/state/items/DESERT_SHADE_PLANTS_DESIGN_1.md`;
`biomes/desert.md` §4b/§6/§9/§10 (FROZEN); `biomes/arid_shrubland.md` §Venomvine
(FROZEN); `PLANT_GROWTH_SPEC.md`; the round-2 flora review
(`review/round2/flora_decisions_propagated.json`, owner ruled
`ledger:desert:defending-shade-plants-thorn-venom-patch-flora` **in**); and the
installed 1.6 engine, read through RimSage on 2026-09-20 (every line marked
MEASURED below)._

**Every rule this document invents is marked 🄸 INVENTED.** Everything unmarked
traces to a frozen sheet, a ruling, the item file, or a MEASURED engine fact.
Numbers marked 🄸 are defaults for the build, all of them exposed in Mod Settings
(owner, 2026-09-12: every mod ships superb Mod Settings).

---

## 0. How many plants: TWO, not three

desert.md §4b "The shade plants, which defend" has exactly two bullets:

1. "Strange vines and thorny venom writhing around some areas — plants that hold
   territory by injury."
2. "Mossy growth leaching nutrients as fast as it can — fast, shallow,
   opportunistic."

The "2-3" in the filing item was a hedge over whether bullet 1 is one plant or
two. The arid shrubland sheet settles it: its **venomvine** ("a scratch carries
venom with serious results", "nearly impossible to cut down", "resist fire
greatly") is explicitly **"Desert lineage"** (arid_shrubland.md §Venomvine). The
desert's "strange vines and thorny venom" is that plant's ancestral, sparser
form — one plant, one mechanism, shared with the shrubland's thicket form.

| # | plant | working name | tier | mechanism |
|---|---|---|---|---|
| 1 | the vine that holds territory by injury | **venomvine** (the shrubland sheet's own name — stands) | **c** (new C#) | contact venom: a scratch on contact, then one per hour of lingering, carrying a venom hediff |
| 2 | the moss that leaches nutrients | **leachmoss** 🄸 INVENTED working name | **b** (pure XML) | a spawn-roll competitor that owns the fertile patch ground |

The two are split. The moss was never a pawn-damage mechanic and must not wait on
the C#. Names: desert.md's Owed list reserves owner's-pick names for the cycle
plant, the prepared seed dish and the glitter-birds only — not for these two — so
the working names ship unless he renames them (the ultracactus precedent). No card
filed.

---

## 1. Venomvine — the desert form (tier c)

### 1a. The engine has no thorn — MEASURED 2026-09-20

- `grep -rln "CompProperties_Thorn\|CompProperties_Contact.*Damage" "$RW/Data"`
  → nothing (re-run this pass; the item's finding holds).
- Every comp in `Data/` whose name touches damage, trap, toxic, gas, enter or
  proximity: `ReactOnDamage`, `ReleaseGas`, `PlantDamager`, `EnterCooldown`,
  `ProximityLetter`, `ProximityFuse`, `GasOnDamage`, `DamageOnInterval`,
  `SeverityFromGas*`. None damages a pawn for standing on a cell.
- `CompPlantDamager` (Ideology archonexus) damages **plants** in a radius with
  `Rotting`, from `CompTick`, no own-def exclusion. Wrong target and, on a plant,
  never ticks — see next line.
- **Plants tick Long** (`Plants_Bases.xml` `tickerType Long` = every 2000 ticks,
  ~33 s). A `ThingComp` on the plant cannot see a pawn crossing its cell: a
  crossing takes ~10–20 ticks.
- `CompProperties_ReleaseGas` is a one-shot burst (`cellsToFill`,
  `durationSeconds`) that then diffuses on the gas grid. A drifting cloud is not
  a territory, and Biotech tox resistance would switch it off.
- The exact shape we want already exists on a **Building**: `Building_Trap.Tick`
  scans its own cell every tick, keeps a `touchingPawns` list so a pawn springs it
  once per entry, and skips `Pawn.Flying`. A plant cannot be a `Building_Trap`
  (no growth, no `wildPlants`, no cutting job), so the shape is copied, not reused.
- The venom-on-a-cut shape already exists as data: Core's `ScratchToxic` is
  `DamageDef ParentName="Scratch"` + `additionalHediffs` (hediff,
  `severityPerDamageDealt`, `victimSeverityScalingByInvBodySize`). No C# is needed
  to make a scratch carry a hediff.
- `JobDriver_PlantWork` goes to the plant with `PathEndMode.Touch` — a cutter
  stands **adjacent**, not on the cell.
- `DamageInfo.SetBodyRegion(BodyPartHeight, BodyPartDepth)` exists — a thorn can
  be aimed low.

### 1b. Decisions

| question | decision |
|---|---|
| **trigger** | **Both, unified as one per-pawn contact clock.** A pawn standing in any venomvine cell takes one venom scratch on first contact, then one more for every 🄸 **2500 ticks (one in-game hour)** it remains in contact with the stand. Moving between two vine cells is lingering, not re-entry; leaving and re-entering inside the hour does not re-trigger. This is the `Building_Trap` on-enter model plus a linger timer, and it is what "holds territory" means in a biome where shade is used by *resting*: crossing costs one scratch, staying costs one an hour, lying down in it is fatal by the end of the day. |
| **detection** | A `MapComponent` (one per map) holding a `HashSet<IntVec3>` of venomvine cells, maintained by the plant's comp on `PostSpawnSetup`/`PostDeSpawn`. It samples every 🄸 **15 ticks**: for each of `map.mapPawns.AllPawnsSpawned`, test `Position` against the set. O(pawns) per sample, independent of stand size and of the plant's Long ticker. Per-pawn state: last-contact tick and next-scratch tick, in a dictionary, pruned when a pawn leaves for longer than the clock. |
| **damage shape** | **A new `DamageDef`, `RM_VenomvineScratch`, `ParentName="Scratch"`**, carrying `additionalHediffs` → **a new `HediffDef`, `RM_VenomvineVenom`** — the `ScratchToxic` shape, pure XML. Not `ToxicBuildup`: the shrubland sheet says "serious results" from *a scratch*, and ToxicBuildup is shared planetary toxin accounting that Biotech genes and gas masks already zero. 🄸 Scratch 3 damage, armour penetration 0.05, `SetBodyRegion(Bottom, Outside)` — thorns take the legs. 🄸 `severityPerDamageDealt 0.04` (one full scratch = 0.12 venom), `victimSeverityScalingByInvBodySize true` (a Jawa gets a serious dose, a giant shrugs), **no** `ToxicResistance` scaling — armour is the counter, not a gas mask. |
| **the venom** | 🄸 `RM_VenomvineVenom`: `severityPerDay -0.5` (one scratch clears in ~6 h), stages at 0.05 minor (pain), 0.30 serious (pain, moving −20%, consciousness −10%, vomiting), 0.60 grave (consciousness −30%, blood-filtration −20%), `lethalSeverity 1.0`. Arithmetic: lingering nets +0.10/h, so serious after ~3 h in the vines, lethal after ~9 h. A crossing pawn gets minor-stage pain for six hours and nothing else. Lethality is a Mod Settings toggle (default on — desert.md §6.7: "there is no safety anywhere"). |
| **avoidable?** | **Avoidable by route and by armour, a flat tax only where the stand walls the patch.** Route: the plant def carries 🄸 `pathCost 60` (a tree is 42), so the pathfinder threads gaps and detours a band when the detour is cheaper — sparse stands ("around some areas") are threadable, solid bands cost a scratch. Armour: Sharp armour reduces the 3-damage scratch and a scratch reduced to 0 delivers no venom, so leg armour is protective gear without a new stat. Flyers are immune (`Pawn.Flying`, same as vanilla traps — "if it flies in the fiction, it flies in the game"). Race immunity: a `DefModExtension`, `RimMandrake.EnvironmentalHazards.ContactVenomImmunity`, on the **race** ThingDef, so any mod's creature opts out without touching the vine (the shrubland's "residents move through the walls to their advantage"; the desert's glitter-birds). |
| **cutting it** | Safe from the adjacent cell (MEASURED `PathEndMode.Touch`), so the player verb is **clear a stand from the edge inward**; a colonist ordered to cut a vine whose only adjacent cells are vine cells will stand in one and be scratched hourly. 🄸 `MaxHitPoints 300`, `harvestWork 900` ("nearly impossible to cut down"). No harvest product in the desert form (dead-venomvine fuel is the shrubland's industry — that sheet's later work). |
| **who it hurts** | Every non-flying, non-immune pawn: colonists, animals, raiders, caravans. No instigator pawn on the `DamageInfo`, so no manhunter response, no faction relation hit; the `DamageInfo.Instigator` is the vine Thing so the health tab names it. Wild animals that rest in a stand are the biome's own casualties — a steady tax, not a boom-and-bust (§6.4). |
| **class shape** | `CompProperties_ContactVenom` / `CompContactVenom` (a generalized "this thing scratches whoever stands on it" comp — fields: `damageDef`, `damageAmount`, `armorPenetration`, `contactIntervalTicks`, `bodyHeight`) + `MapComponent_ContactVenom` + `ContactVenomImmunity` extension. Generic on purpose: the shrubland thicket form and any later thorn plant reuse it with different numbers. |
| **NOT this mechanism** | The shrubland thicket's **"small creatures pass through easily; larger ones simply cannot"** is a body-size passability rule (per-pawn impassability, a pathing patch) and is a separate owed commission slug (`venomvine-fortress-flora-passability-by-body-size`, tracked by `COMMISSION_LEDGER_CLEANUP_1`). The comp must not preclude it; it does not attempt it. |

### 1c. Rejected routes, one line each

- **Harmony on `Pawn_PathFollower` for on-enter** — hot pathing code, misses a
  stationary pawn entirely, and lingering is the case that matters.
- **`tickerType Normal` on the plant** — makes every vine in a stand tick every
  frame and breaks `Plant.TickLong` growth.
- **A gas** — drifts, is not territorial, and Biotech tox resistance switches it
  off.
- **`Building_TrapDamager` dressed as a plant** — no growth, no wild spawning,
  no cutting, and colonists know their own faction's traps.
- **Reusing `ToxicBuildup`** — see 1b; also lethal at the same 1.0 as fallout
  exposure, which would make a scratch and a toxic-fallout day the same disease.

### 1d. The plant def (tier b half of the build) — 🄸 defaults

`RM_Venomvine`: `PlantBase`; `pathCost 60`; `MaxHitPoints 300`;
`Flammability 0.1` (shrubland: "resist fire greatly and burn only grudgingly";
desert §6.5 bans local fire ecology); `Nutrition 0` (nothing grazes it);
`Beauty -4`; `fertilityMin 0.5` (patch ground — Gravel 0.7 / Soil 1.0; MEASURED
`Terrain_Natural.xml`: Sand is 0.10, SoftSand 0 — so it can never reach the
ultracactus's sand, realising §4b's partition); `fertilitySensitivity 0.3`;
`growDays 8`; `lifespanDaysPerGrowDays 0` (does not die of age — a stand is
permanent until cut); `wildClusterRadius 4`, `wildClusterWeight 6` (stands, not
lawn); `wildOrder 2`; `maxMeshCount 1`; `visualSizeRange 0.8~1.2`;
`topWindExposure 0.1`; `purpose Misc`; `allowAutoCut false` (a stand is a hazard
the player clears on purpose, never by an auto-cut sweep). RUT_Desert
`wildPlants` weight 🄸 0.25 (MEASURED current list: ultracactus 0.8 … dommo 0.06).
Colour: dark rust-umber, thorn tips lighter — **no green** (§9: "the only greens
are the pale ultracactus and the dew-line halo"; §6.8 no lush).

Art: **none exists** — `infrastructure/artpipe/{done,_artsrc,registry.jsonl,
art_status.json}` searched for vine/thorn/venom on 2026-09-20; the hits
(`ripthorn_v1`, `tropicalchokevine_v1`, `firevine*`) are donor plants rendered for
other biomes' rosters. The build files the job, after searching again.

---

## 2. Leachmoss — the nutrient racer (tier b)

### 2a. What "competition" is in this engine — MEASURED 2026-09-20

- **1.6 `PlantProperties` has no reproduction fields at all** — no
  `reproduceMtbDays`, no `reproduces`, no per-plant seeding. A plant never
  damages, displaces or slows a neighbour. All wild spread is `WildPlantSpawner`:
  it picks a plant per empty cell by **biome commonality share**, filtered by
  `fertilityMin`/`wildTerrainTags`/`terrainBlacklist`, shaped by
  `wildClusterRadius`/`wildClusterWeight`/`wildOrder`, and it steers local
  proportions back toward each plant's commonality share
  (`LocalPlantProportionsWeightFactor`). Regrowth after a cell empties is
  weighted by `plantRespawningCommonalityFactor`.
- There is no per-cell fertility to leach: fertility is a `TerrainDef` constant.

⇒ **"Leaching nutrients as fast as it can" is, in engine terms, owning the spawn
rolls on the fertile ground and re-taking any fertile cell that empties.** That is
buildable in XML alone; the fiction's outcome — the fertile patch ground fills with
moss before anything slower can have it, and the ultracactus is pushed to the sand
— falls out of `fertilityMin` partitioning plus commonality. The item's instinct
was right: this is a fertility/growth-rate competitor, not a damage mechanic, and
it is **split out** from the vine.

### 2b. Decisions — 🄸 defaults

`RM_Leachmoss`: `PlantBase`; `fertilityMin 0.5` (Gravel/Soil only — the same
partition as the vine, never the ultracactus's Sand); `fertilitySensitivity 1.0`
(the leacher: thrives only on rich ground, starves on poor); `growDays 1.5` (the
planetary ×4 baseline of `PLANT_GROWTH_SPEC.md` applies on top — fast enough to
watch); `lifespanDaysPerGrowDays 4` (short-lived: "fast, shallow"); RUT_Desert
`wildPlants` weight **1.5** — the highest in the list, so on ground it can take it
wins most rolls; `plantRespawningCommonalityFactor 2.0` (after a cut, an ash-pulse
or a megafauna dung stop, the empty fertile cell goes to the moss first — "racing
everything else to whatever the wind just delivered"); `wildClusterRadius 5`,
`wildClusterWeight 10`; `wildOrder 1`; `maxMeshCount 9`; `visualSizeRange
0.4~0.7`; `topWindExposure 0`; `Nutrition 0.3` (grazable — the herbivores' steady
patch forage, §5 "populations small and steady"); `MaxHitPoints 60`;
`harvestWork 60`; no harvest product; `purpose Misc`; `Flammability 0.2`;
`pathCost 0`. Colour: dull olive-umber, darker and duller than the ultracactus —
never a bright green (§6.8). It is permitted a muted green only because §9 allows
the dew-line's densest growth one, and this is the plant that will *be* that halo
once placement can follow the shade grid.

Rejected: `CompPlantDamager` (plant-only `Rotting` over a 32-cell radius from
`CompTick`, which on a Long-ticking plant never fires — and it would rot its own
stand); any terrain-swap hack to fake fertility depletion.

⚠️ UNMEASURED and deliberately left to the build's verify: the commonality weight
that makes the moss *visibly* own patch ground at `plantDensity 0.05` against the
full roster. Tune by LOOKING (quicktest map, walk a gravel/soil pocket), not by
arithmetic.

---

## 3. Where it lands — tier and naming

Everything from this design ships in **`mandrake.rm.environmentalhazards`**
(`src/RimMandrake/EnvironmentalHazards`, "generalized, XML-configurable
environmental hazards", `RimMandrake.EnvironmentalHazards.dll` already built):
the comp, the MapComponent, the immunity extension, `RM_VenomvineScratch`,
`RM_VenomvineVenom`, and both plant ThingDefs, all `RM_`-prefixed (they are
generic RimWorld content, not Star Wars content — tier grammar,
`NAMING_SCHEME_PLAN.md`; `naming_lint.py` checks prefix against mod tier, which
is why the plant defs do not go beside `RSW_Ultracactus.xml`). `RUT_Desert`
wires them into `wildPlants` with `MayRequire="mandrake.rm.environmentalhazards"`,
exactly as it already does for the SWBestiary plants. When
`BIOME_MOD_SPLIT_EXECUTION_1` names the desert's own RimMandrake mod, the plant
defs may move there by `git mv` — no rename.

Mod Settings (both plants live behind the kit's settings screen): contact venom
on/off (default on); scratch damage multiplier; venom lethal on/off (default on);
leachmoss on/off (default on — removes it from `wildPlants` via the kit's
existing pattern).

---

## 4. What the shade grid changes later — nothing here

`DESERT_SHADE_GRID_KEYSTONE_1` (the `ShadeAt(IntVec3)` MapComponent) is **done**
in the ledger (checked 2026-09-20). Placing both plants *on shade cells* rather
than on fertile terrain as a proxy is a later spawner-placement pass against that
grid, not a change to either mechanism: the contact-venom comp keys on the
plant's own cell, and the moss keys on terrain fertility. Neither build waits on
it, and neither build does it.

---

## 5. Verification the build owes (quicktest map, five DLC, minimal list)

1. Spawn a stand; walk a colonist through: exactly one `RM_VenomvineScratch`
   injury on a leg, `RM_VenomvineVenom` at ~0.12, decaying to 0 in ~6 h.
2. Park a colonist inside for 3 in-game hours: one scratch per hour, venom
   passes 0.30 (serious stage visible). Downed pawn left inside reaches
   `lethalSeverity` in ~9 h with lethality on; never with it off.
3. Cut a vine from an adjacent non-vine cell: no scratch. Cut one whose only
   adjacent cells are vine: scratch on the hour.
4. A flying creature (any Core bird) crosses the stand: nothing.
5. A race carrying `ContactVenomImmunity` crosses: nothing.
6. Full Sharp leg armour: scratch reduced; when reduced to 0, no venom.
7. Leachmoss on a fresh desert map: present on Gravel/Soil pockets, absent from
   Sand; cut a moss cell and confirm the regrowth is moss more often than not.
8. Save/load mid-contact: the per-pawn clock survives (`ExposeData`) — no double
   scratch on load.

---

## 6. Successors filed by this pass

- `VENOMVINE_CONTACT_VENOM_BUILD_1` — tier c: the comp, MapComponent, extension,
  DamageDef, HediffDef, the `RM_Venomvine` def, RUT_Desert wiring, settings, art
  job, verify list above. Needs offline (compile + XML), then a quicktest.
- `DESERT_LEACHMOSS_BUILD_1` — tier b: the `RM_Leachmoss` def, RUT_Desert wiring,
  settings toggle, art job, verify step 7. Independent of the C# item.

No owner card: the sheet answered the plant count, the shrubland sheet answered
the name and the venom's seriousness, and every remaining number is a Mod
Settings default the owner tunes by playing, not a ruling he has to give blind.
