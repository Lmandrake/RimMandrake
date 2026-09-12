# SUMP_MECHANICS_1 — C# mechanics kit spec (engine mapping)

Drafted 2026-09-11 against the FROZEN lore sheet
`design/Jawa/worldbuilding/biomes/the_sump.md` (§0, §3, §4, §5, §6 hard bans,
§7, §7b, Owed) and the RULED comp kit in
`design/Jawa/worldbuilding/alpha_family_source_review.md` §4 (owner,
2026-09-11: all six RM_ comps IN; build item `ALPHA_MECHANICS_KIT_1`). This
spec maps the sheet's mechanics onto the engine — it invents no lore.
**INVENTED** marks a tuning parameter this spec picked a starting value for;
❓ marks an engine claim not verified against source, to be checked at build.

**Source verification basis**: claims marked *(verified)* were read from the
RimSage source index this session (`mcp__rimsage__search_source` /
`read_csharp_symbol`). ⚠️ Same caveat as `greentide_kit_spec.md` /
`miasma_kit_spec.md`: the index is consistent with a 1.5-era decompile, so
every "vanilla has no X" claim is "no X **in the indexed source**" with an
implicit ❓ against the live 1.6 assembly. Anchors marked *(verified,
greentide)* / *(verified, miasma)* were verified at those specs' drafting.

**Naming**: generic mechanisms are `RM_` (`RimMandrake.*` namespaces); Sump
content defs exposing them are `RUT_` (`RimMandrake.Utinni.*`), per
`design/NAMING_SCHEME_PLAN.md`. One C# implementation per mechanic, tuned
per-biome by XML (ruled §4 resolution). RM_ classes live in the ruled kit's
home (`src/RimMandrake/EnvironmentalHazards/`, packageId
`mandrake.rm.environmentalhazards`) or a sibling RM_ mod if FOUNDRY splits by
weight. Biome: `AB_TarPits` (Alpha Biomes donor, per the sheet header).

**Hard-ban compliance (sheet §6, linter-checkable)** — how each ban binds this kit:

| Ban | Where it binds |
|---|---|
| 1. No whole Assailant/Rakatan in the tar | S2's loot tables contain **partial remains and §GM-tier finds only** — no whole-body defs of either era may appear in any `RUT_TarDig*` table; **trap rows outweigh both remains rows in every stratum** (the ruling's "MORE likely", checkable as a weight inequality). |
| 2. No tar beast as fightable spawn | S3's kinds carry **zero wild-spawn commonality and no faction/raid entry**; the GenStep is their only route in. Woken behavior is station-eating + re-submerge, never a huntable reward (no killReward, no butcher yield worth the fight — priced to evacuate). |
| 3. No sun-driven flora | Every native PlantDef ships `growMinGlow 0` *(field verified, `Source/RimWorld/PlantProperties.cs:75`, default 0.51)* — chemotrophy is structural, not flavor text. |
| 4. No rain, no surface water defs | `RUT_SumpWeather` and every weather the biome can roll carry zero rain/snow rates; the standing weather lock (S6) makes vanilla rain unreachable. No vanilla water TerrainDef appears in any Sump terrain mapping — tar grades only (`LIQUID_TYPES_MOD_1` owns them). |
| 5. No warm-climate donor flavor | Donor strings/graphics are stripped at the content pass; nothing in this kit references AB warm-mud defs. |
| 6. No vanilla-Earth flora/fauna | Standard eviction; S4's mice and S5's wick-plants are `RUT_` kinds the roster pass owns. |

Scoreboard: **6 mechanics** · **2 ruled-comp reuses** (EnvironmentalWeather,
BiomeGlowMultiplier) · **1 cross-kit shared class** (`RM_GenStep_PlacedSetPieces`,
with Miasma M6) · **5 new RM_ classes** (1 L, 3 M, 1 S) · S5 is XML-only.

---

## S1. The poured moat + command ignition (§3 "the tar defends", §7b)

**Player experience.** You lay a tar perimeter like flooring; raiders path
around it or mire in it. On command, it lights: a long-burning wall of flame
and smoke nothing crosses or shoots through, its column visible for a day's
travel. Burnt tar is spent tar — the moat is a consumable, and demand never
ends (§5).

**Engine route.**

- **The moat terrain**: `RUT_TarMoat` — a player-buildable TerrainDef (floor
  grammar; cost paid in barreled tar, the §7 export consuming itself). High
  `pathCost` + movement penalty is the unlit deterrent (raiders path around
  or mire — vanilla pathfinding prices pathCost natively, no C#).
  Flammability demands a burn target: `TerrainDef.burnedDef` *(verified,
  `Source/Verse/TerrainDef.cs:180`; ConfigErrors enforces "flammable but
  burnedDef is null" at :542)* → `RUT_TarSpent` (dark, cheap, walkable —
  re-pour to re-arm). Terrain burn conversion is stock: `TerrainGrid` swaps
  to `burnedDef` on burn notify *(verified, `Source/Verse/TerrainGrid.cs:609`)*.
- **Command ignition**: `RM_CompFloodIgniter : ThingComp` on a small buildable
  fuse-post (`RUT_MoatFusePost`). Gizmo → flood-fill across contiguous
  `RUT_TarMoat` cells from the post, staggered ignition front (**INVENTED**:
  ~10 cells/sec) via `FireUtility.TryStartFireIn` *(verified — call sites
  across `PowerBeam`, `Explosion.cs:334`, etc.)*. Generic: props name which
  TerrainDefs conduct — any future flammable-line content reuses it.
- **The burning wall**: each lit cell spawns `RUT_TarBlaze` (a short-lived
  Thing): fire graphic + stock **`CompReleaseGas`** *(verified,
  `Source/RimWorld/CompReleaseGas.cs`)* emitting **`GasType.BlindSmoke`**.
  BlindSmoke already blocks shooting — accuracy factor in `ShotReport`
  *(verified, `Source/Verse/ShotReport.cs:106`)* — and AI target acquisition
  — LOS validator in `AttackTargetFinder` *(verified,
  `Source/Verse/AttackTargetFinder.cs:49`)*. Sight-blocking is therefore
  stock; **passage-blocking is the flame itself** (crossing a burning cell
  takes fire damage; ❓ verify raider pathfinding actually prices fire cells
  high enough to refuse crossing — if not, `RUT_TarBlaze` gets `pathCost`/
  impassable while alive). Burn duration **INVENTED**: 12–24 in-game hours;
  on expiry the blaze destroys itself and the terrain has burned to
  `RUT_TarSpent`.
- **The distant column**: cosmetic — a tall smoke mote/overlay while ≥N
  blaze cells live (**INVENTED**: N=20). No world-map mechanic in v1.

*Why not a ruled comp*: nothing ruled owns terrain flood-ignition; gas and
fire pieces are deliberately stock.

**Effort**: **M** (igniter S + blaze lifecycle S + pathing verification).
**v1: ships** — §7b calls it the biome's whole economy in one build.

## S2. The dig lottery (§7 "what the tar keeps", ban #1)

**Player experience.** Stake a dig, put work into it, and the tar sells back
deep time: bones of unnamed ages, sunken machines, sealed casings — or a
click. Traps of the Assailant era come up MORE often than anything of their
makers. Digging deeper raises both the prize and the price.

**Engine route.** `RM_CompWorkedLottery : ThingComp` on a buildable
`RUT_DigShaft` — work-accumulation shape cribbed from `CompDeepDrill`
*(verified, `Source/RimWorld/CompDeepDrill.cs` — work float, TryProducePortion
seam)*, but yielding from a stratum table, not resources:

- **The table**: `RUT_DigStratum` rows in a `RM_LotteryTableDef` (new lightweight
  Def class; ❓ at build, check whether vanilla `ThingSetMakerDef` composes
  weighted-outcome-with-side-effects cleanly enough to replace it — prefer
  stock if it does). Row kinds: junk/bitumen (common) · preserved fauna
  remains, hides, bones of un-bestiaried ages (uncommon) · sunken machines,
  sealed §GM-tier casings, **partial** era remains (rare) · **trap** (see
  below). **Ban #1 as arithmetic: in every stratum, weight(trap) >
  weight(era remains) > 0, and no whole-body row exists.**
- **The click**: a trap row telegraphs — click sound + pause letter
  (**INVENTED**: 15-second fuse) — then detonates via stock `CompExplosive`
  *(verified, `Source/RimWorld/CompExplosive.cs`)*; crib
  `Building_TrapExplosive` *(class verified)* for the armed-thing variant
  that surfaces intact for card 2's disarm question.
- **Depth**: each completed portion increments the shaft's stratum
  (Scribe-saved). Deeper strata: better rare rows, heavier trap weight
  (**INVENTED**: trap weight ×1.3/stratum), and past a threshold
  (**INVENTED**: stratum 4+) each portion rolls a beast-wake signal (S3).
  "Never dig past the click you were warned about" becomes a real gradient.
- **Placement**: shafts are player-placed on tar terrain; mapgen also
  scatters pre-dug abandoned shafts + flagged strips (§8) as ruins flavor
  via S3's shared scatterer — no separate system.

**Effort**: **M**. **v1: ships** — §7 names excavation "core gameplay".

## S3. The tar beast set-pieces (§4, §5 "something under the deepest black", ban #2)

**Player experience.** Somewhere under the deepest black is a smooth bulge
you learn not to trust. Deep digs, explosions, or greedy pumping wake it —
and a woken tar beast is a slow, unstoppable, station-eating catastrophe you
evacuate ahead of, not fight. Then the black goes still again.

**Engine route.**

- **Placement**: **`RM_GenStep_PlacedSetPieces`** — the SAME generic def-list
  scatterer specced for Miasma M6 (`GenStep_Scatterer` subclass; base
  *(verified, miasma)*). One implementation, two customers; whichever kit
  builds first ships it. Per map, N dormant beasts (**INVENTED**: 1–2) in
  deep-tar regions, far from map edge. Never random (ban #2): zero
  commonality, no faction, GenStep-only entry.
- **Dormancy + wake**: stock **`CompCanBeDormant`** + **`CompWakeUpDormant`**
  *(both verified; `CompWakeUpDormant` read in full)* carry the wake causes
  natively: explosions → `wakeUpOnDamage` (external violence); building
  derricks/stations too close → `wakeUpOnThingConstructedRadius`
  (**INVENTED**: 20 cells); deep digs and greedy pumping → S2/S6b send
  `Activate()` via the comp's signal seam. Dormant form is a Building
  (`RUT_BeastBulge`, "one wrong smooth bulge in the black", §9) swapped for
  the beast pawn on wake — crib the `TunnelHiveSpawner : GroundSpawner`
  emergence shape *(class verified)*.
- **Station-eating**: `RM_CompStationEater` driving a dedicated ThinkTree:
  the woken beast paths slowly toward the nearest player-built structure
  cluster and consumes/destroys buildings (accreting tar as it goes, per
  §4); it does not hunt pawns (they can always outwalk it — **evacuate, not
  fight** is priced by speed **INVENTED**: 0.9 c/s, massive health, high
  blunt/sharp resist, and no meaningful kill yield). ❓ cleanest breach seam:
  crib the breach-raid JobGiver vs a custom eat-building job — read at build.
- **Satiation**: after eating N structures or M days awake (**INVENTED**:
  8 structures / 3 days), it re-submerges (despawns into a fresh bulge at a
  new deep-tar cell). No corpse economy, no trophy (ban #2's spirit). Card 3
  owns the end-state question.
- **Patient-family register**: art/dread/mechanics rhyme with
  `sarlacc_spec.md` (type specimen) and the Fever Wood's deep thing — this
  kit's dormant-bulge + cause-driven wake + never-a-raid-entry trio is the
  family's mechanical signature; the roster pass owns the shared register.

**Effort**: **L** (eater ThinkTree + lifecycle; dormancy/wake are stock).
**v1: ships** placement + wake + a minimal eater; satiation polish may land
one build later — flag, not silent.

## S4. Mouse-line telegraphy (§4 "sump-mice", §5 "where they won't, you don't")

**Player experience.** Mice run the black everywhere, leaving faint tracery
— except across one stretch they always detour around. Nobody tells you why.
The absence of tracks IS the warning; Junkers read mouse-lines the way
sailors read water.

**Engine route.** `RM_MapComponent_DreadField` — a per-map avoid-cell set
built from registered dread sources (dormant `RUT_BeastBulge` positions,
radius **INVENTED**: 8 cells; generic — any Patient-family map presence can
register):

- **Mouse avoidance**: sump-mouse kinds (roster owns the PawnKindDef) get a
  wander JobGiver whose cell validator consults the field — mice never path
  into dread cells. ❓ cheapest seam: ThinkTree wander-node validator vs
  pathfinder cost injection — read the wander JobGiver family at build and
  crib the smaller.
- **The tracery**: mice deposit `RUT_Filth_MouseTrack` (low-alpha filth,
  slow dissipation) on tar cells they cross (**INVENTED**: 1 per ~40 cells
  walked). Track filth accumulates map-wide over days — except inside dread
  radii. **The telegraph is emergent and diegetic: no overlay, no alert, no
  UI** — the player who looks sees the gap in the tracery, and the player
  who doesn't learns like the Junkers did. Filth deposit is a ~20-line
  comp/JobDriver hook; ❓ verify filth-per-cell caps don't erase the pattern
  at low mouse counts (tune spawn density in biome XML if so).

*Why not a ruled comp*: nothing ruled owns spatial fear-fields or
species-read telegraphy.

**Effort**: **M** (field S + wander validator + filth hook). **v1: ships** —
it is the sheet's charm and its survival instrument in one system.

## S5. The wick-garden crop (§4 "edge-flora", §7 "light as a crop")

**Player experience.** The only living light is farmed fire-in-waiting:
wick-plants grown in station gardens under no sun at all, harvested as
candles and lamp-stock.

**Engine route. XML-only — no C#.**

- `RUT_Plant_Wick` PlantDef: **`growMinGlow 0`** *(verified field — 0 makes
  darkness-growth stock engine behavior; ban #3 satisfied structurally)*,
  sowable, restricted by terrain affordance to tar-margin terrain grades
  (`LIQUID_TYPES_MOD_1` names them); `growMinTemp` lowered for the cold
  (**INVENTED**: −8 °C; sheet §0 temps straddle freezing). Harvest:
  `RUT_WickStem` — torch/lamp fuel via `CompRefuelable` fuel filters and a
  tradeable candle good (items pass owns pricing).
- Wild edge-flora variants (chemotroph ring at pit margins, faint glow near
  stations) are roster/art content on the same `growMinGlow 0` pattern.
- ❓ one live check owed: that a `growMinGlow 0` plant actually grows under
  the S6 glow regime on a quicktest map (plant growth also gates on resting
  hours — confirm the night-edge light level isn't double-penalized).

**Effort**: **XML only.** **v1: ships.**

## S6. Permanent dusk + the weather lock (§0, §9, bans #4/#5)

**Player experience.** Deep twilight forever: sun a glow below the horizon,
horizon amber over every black. It never rains; the cold is the trap's lid.

**Engine route.** Reuse-heavy, per the ruled kit:

- **The lock**: ruled **`RM_GameCondition_EnvironmentalWeather`** as a
  permanent `biomeMapConditions` entry *(both hooks verified, greentide)* —
  forced `RUT_SumpWeather` (cold, dry, still; zero rain/snow rates — ban #4
  structural), rare cold-fog variants via the condition's config, never
  vanilla's rain-capable rotation.
- **The light**: ruled **`RM_HarmonyPatch_BiomeGlowMultiplier`** with the
  extension on the Sump BiomeDef (**INVENTED**: multiplier 0.55 — deep
  dusk, darker than Miasma's 0.85, lighter than a cave). ❓ **verify on a
  quicktest map how much darkness the engine already gives a night-edge
  tile** (map sun angle derives from world position; the frozen map puts all
  tiles at arc 85–105) — the multiplier tunes the RESIDUAL, so calibrate
  live, don't stack blind.
- **6b. Derrick pumping** (§7b stations): the pump/derrick building is items
  and content-pass XML (production building grammar); the ONLY C# seam it
  owes this kit is: pumping volume past a threshold on a deep pond registers
  as "greedy" and calls S3's wake signal (**INVENTED**: threshold; a props
  field on `RM_CompWorkedLottery` reused for pump-shape work — same comp,
  different yield table, so derricks and dig shafts share one class).
- Biome figures (movementDifficulty 4, animalDensity 3.5, plantDensity 0.25,
  forageability 0.8, `diseaseMtbDays` conservative) — BiomeDef XML per §0.

**Effort**: **S** (glow calibration + wake threshold; heavy pieces ruled).
**v1: ships.**

---

## XML-only ledger (no C#, listed so nothing gets re-invented)

- Tar terrain grades (natural pools, glass reaches, moat, spent) —
  `LIQUID_TYPES_MOD_1` owns what the liquids ARE; this kit consumes the defs.
- Bitumen, asphalt (Ashfall Road re-paving supply chain), barreled tar,
  candles — §7 economy, rides the **items pass**.
- Sump-mice, tar beasts, edge chemotrophs, bumbledrone verdict — **roster
  pass** (sheet Owed; Patient-family register with `sarlacc_spec.md`).
  Bumbledrone hives: stock Hive/`TunnelHiveSpawner` grammar, no new C#.
- Station/dig-field ruins flavor (§8) — def-list content for the shared
  scatterer, no new class.

## New-C# roster (beyond the two ruled-comp reuses)

| Class | For | Effort |
|---|---|---|
| `RM_CompFloodIgniter` + `RUT_TarBlaze` lifecycle | S1 | M |
| `RM_CompWorkedLottery` + `RM_LotteryTableDef` (shafts AND derricks) | S2, S6b | M |
| `RM_GenStep_PlacedSetPieces` | S3 | shared w/ Miasma M6 |
| `RM_CompStationEater` (+ ThinkTree) | S3 | L |
| `RM_MapComponent_DreadField` (+ wander validator, track filth hook) | S4 | M |

Total: 1 L, 3 M, 1 shared; S5 XML-only; two ruled-comp reuses ride
`ALPHA_MECHANICS_KIT_1`'s build.

## Build order

1. **`ALPHA_MECHANICS_KIT_1` lands first** (external dependency): the S6
   weather lock + glow patch — the biome instantly looks right, and every
   later live test happens under the dusk.
2. **S6 calibration + biome XML** — including the live glow check.
3. **S5 wick crop** — XML; proves the chemotroph pattern for the roster pass.
4. **S1 poured moat** — needs `LIQUID_TYPES_MOD_1` grade names (defs can
   stub as recolors first); the pathing-refusal check is its gate.
5. **S2 dig lottery** — independent of S1; trap-weight inequality is its
   linter check.
6. **S3 tar beast** — after S2 (wake signal source) and the shared scatterer
   (build here if Miasma hasn't).
7. **S4 mouse-lines** — strictly after S3 (dread sources must exist);
   roster's mouse kind can stub as a recolored placeholder for the filth test.

Cross-item dependencies restated: `ALPHA_MECHANICS_KIT_1` (S6),
`LIQUID_TYPES_MOD_1` (terrain grades), roster pass (mice, beasts, flora,
bumbledrones; Patient-family register), items pass (§7 economy — deliberately
NOT in this kit), `sarlacc_spec.md` (family type specimen).

## Open owner cards (unruled — rides `MECHANICS_CARDS_SITTING_1`)

1. **RULED 2026-09-12 — the lit moat DOES catch adjacent natural tar
   pools.** The owner overrode the drafted poured-cells-only default: a
   defensive burn can cascade into a map-scale fire. Physics is true and
   spectacular and punishing; players learn where they pour. (Build note:
   the cascade must still be survivable-by-foresight — telegraphy per the
   mouse-line doctrine, no silent map-wipe.)
2. **RULED 2026-09-12 — era traps are disarmable: high skill gate, failure
   detonates.** As drafted; the click is a decision and a skill-priced
   §GM-tier find.
3. **RULED 2026-09-12 — sated → re-submerges at a new spot.** As drafted:
   the map heals, the mouse-lines redraw, no player is ever taught to farm
   it.
