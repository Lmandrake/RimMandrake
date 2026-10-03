# The Chill (the Propane Lake) — floor-pass sitting agenda (draft, 2026-10-02)

Track (b) of `BEDAZZLE_TOP_SHAPE_PROGRAM_1` ("finish the two seas' floor passes"), the
Propane Lake's half. The owner renamed the biome **the Chill** on 2026-09-27 (*"Let's call it
the Chill"*); the free-tier defs are `RM_TheChill*`, the frozen campaign twin is still
`RUT_PropaneLake`. The item this sitting serves is `PROPANELAKE_FLOOR_PASS_1` (proposed, needs
owner, filed 2026-09-25, no prose yet). Shape copied from the Grey Sea pass
(`GREYSEA_FLOOR_PASS_1`, `grey_deep_sitting_agenda_2026-09-27.md`).

**Draft for a sitting: nothing is filed, no code is touched.** Read from the bench clone at
`e7490dd79`. Rosters parsed as XML elements (node name = animal, text = commonality); the cast
was judged from descriptions, not defNames. No tile counts consulted.

Sources: the frozen sheet `the_propane_lakes.md`; `the_propane_lake_flora_pass_2026-09-27.md`
(incl. its §Rulings); `terminal_seas_cast_proposal_2026-09-25.md`;
`the_chill_warlab_routes_spec_2026-09-27.md`; items `PROPANELAKE_FLOOR_PASS_1`,
`PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1`, `SEA_FLOOR_AND_CATCH_PASS_1`,
`CHILL_SURFACE_SITTING_1`, the closed `CHILL_*` family, `PROPANELAKE_ANIMALDENSITY_ZERO_1`,
`RUT_PROPANELAKE_FROZEN_DENSITY_1`; defs under `src/RimMandrake/TerminalBiomes/`,
`src/RimMandrake/DivingInteraction/`, `src/RimUtinni/UtinniPatches/`,
`src/RimUtinni/PropaneLakeMechanics/`.

## 0. The headline: most of this floor pass already happened

The Grey Sea agenda found its sea "mostly a ruling and ratification sitting". The Chill is
further along than that. **A Chill floor sitting was held on 2026-09-27** (two rounds, decisions
taken by question card, recorded across the flora item's ledger and thirteen `CHILL_*` items
filed that evening), and **every one of those items is closed as built** by 2026-10-01:

| What the 2026-09-27 sitting ruled | Item (all `done`) |
|---|---|
| Full rename to the Chill | `CHILL_RENAME_FULL_1` |
| Brutal uniform cold (−110 °C pocket map) + boil-shroud flecks around warm hulls | `CHILL_THERMAL_ENGINE_1` |
| Total fire ban on the floor (no oxygen); fire only with pumped air; fuselight exempt | `CHILL_FIRE_BAN_1` |
| Heated EVA suit with one charge clock; empty = fast hypothermia | `CHILL_HEATED_SUIT_1` |
| Garden immune system: iliss arcs warn, tarnn colonies wake | `CHILL_GARDEN_DEFENSE_1` |
| Warmth leaves refrozen glossy trails the defence can read | `CHILL_THERMAL_FOOTPRINTS_1` |
| Layered floor light: drowned aurora over bioluminescent points | `CHILL_FLOOR_LIGHT_1` |
| Aurora surge storms: harvestable floor weather with shock risk | `CHILL_AURORA_SURGE_1` |
| Ice bedrock + krellik rime-terrace districts | `CHILL_RIME_TERRACES_1` |
| Ten flora + hydrocarbon-flesh fuel chain at the refinery | `CHILL_FLORA_BUILD_1` |
| War-lab access: three blast tiers + two drill routes (spec) | `CHILL_WARLAB_ROUTES_1` |
| Crater biome + world-tile swap when the lab route fires | `CHILL_WORLD_CRATER_1` |
| V-wake pump agitation verified end to end | `CHILL_VWAKE_WIRING_VERIFY_1` |
| Enclosed cryoponics grower + a floor-only growing bed (2026-09-30) | `CHILL_CRYOPONICS_GROWER_1`, `CHILL_FLOOR_GROWING_BED_1` |

Also already ruled, and not to be re-asked: the **surface** gets its own separate sitting
(`CHILL_SURFACE_SITTING_1`, open) — the Burner Ascendant guards one authored rim location; the
vaunoom → zhiil → V-wake life cycle is **flavour only** (no fishing-thins-the-wakes loop).
Flora rulings: plantDensity 0.18, fuel-from-flora allowed very late game, stonewater is cooking
+ a powered water source, fuselight explodes for real, eldspar regrows in 60 days, the
tarnn/eldspar boundary is deliberately unsettled, AuroraGlass grows from eldspar hearts.

**So this sitting is a closing sitting**: ratify what is built, settle the handful of
seams the build left (§2), and decide whether the Chill earns one more signature idea (§4).

## 1. What is built (measured)

### 1.1 Getting there and the place

- **Ship-only**, per the standing law. The floor is a pocket map,
  `RM_SeaDiveGenerator_TheChill` (`DivingInteraction/Defs/MapGeneration/RM_SeaDiveGenerators.xml`),
  biome `RM_TheChill`, **temperature −110 °C** (a single uniform float — the engine's own
  pocket-map OutdoorTemp; "an underpowered ship freezes room by room" is vanilla room
  equalisation), `destroyOnParentMapAbandoned=false`, tile mutator `RM_SeaFloorHabitat`.
- **Terrain**: base `RM_ChillIceBedrock` (sparkling water-ice bedrock) with noise bands —
  5% liquid-propane pools `RM_TheChillDeep` (impassable) ringed by 15% standable crust
  `RM_SolidPropane`; `RM_ChillRimeTerraces` genstep paints krellik rime-terrace districts.
  Gensteps: terrain, dive exit, `RM_SeaFloorFauna`, Animals, Plants, rock chunks, fog.
- **No signature landmark genstep.** The Grey has `GenStep_GreySeaFloorDressing` (pillars,
  domes, chimneys, the carved pool, four great crystals). The Chill floor's set-pieces are the
  pools and the terraces; the war lab is a separate site part
  (`StructureInjectionsRUT/Defs/WarLab/SitePartDefs_WarLab.xml`), not floor dressing.

### 1.2 The BiomeDef — `RM_TheChill` (free tier, `mandrake.rm.terminalbiomes`)

| field | value |
|---|---|
| `animalDensity` | **0.08** (sparsest of the four seas; the zero-density defect is fixed here) |
| `plantDensity` | 0.18 (ruled) |
| `wildAnimals` | **12** rows (below) |
| `wildPlants` | **10** rows: slackwax .9, skyharp .8, ghostpane .7, pitchpearl .7, keelgrass .6, tarspool .6, stonewater .4, stillbloom (`RM_ChillStillbloom`) .35, fuselight .3, eldspar .25 |
| `fishTypes` | 5 common + 4 uncommon + rare table `RUT_RarePropaneCatches`; `maxFishPopulation` 60 |
| shore terrains | FlowWorks' propane suite via `RM_SeaShoreExtension` (`RM_PropaneDeep`/`RM_PropaneShallow`) |
| weather | base Clear/Fog only; aurora surge storms ride `CHILL_AURORA_SURGE_1` |

`wildAnimals`: `AA_AuroraSylph` .5 and `AA_Skyeel` .5 (both `MayRequire="sarg.alphaanimals"`,
donor defs, not in our src), `RM_Vaunoom` .04, `RM_Heemin` .7, `RM_Oovanam` .3, `RM_Hoolen` .4,
`RM_Fessu` .55, `RM_Krellik` .5, `RM_Oddu` .45, `RM_Oovu` .4, `RM_Iliss` .3, `RM_Tarnn` .2.

### 1.3 The frozen twin — `RUT_PropaneLake` (what today's save actually paints)

`animalDensity` **still unset** (= 0: its 3-row roster — the two Alpha Animals and
`RUT_VWake` — can never spawn). Deliberately left: the file's 2026-09-25 freeze header routes
every content fix to the RM tier until the planet repaint (`RUT_PROPANELAKE_FROZEN_DENSITY_1`,
closed on that basis). No `wildPlants`. Catch: the seven `RUT_` species + the same rare table.
Per the standing "paint once at the end" ruling this is **expected, not a defect** — listed so
nobody re-files it.

### 1.4 The catch items

- Seven campaign-tier items in `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_PropaneLakeCatch_Items.xml`
  (fessu, krellik, oddu, oovu, iliss, tarnn, zhiil) and two free-tier items in
  `TerminalBiomes/Defs/ThingDefs_Items/RM_TheChillCatch.xml` (heemin, oovanam).
- `RM_TheChill`'s catch rows for the seven `RUT_` items carry `MayRequire="mandrake.rut.patches"`
  — **so in the free mod alone the Chill's catch is two species** (heemin, oovanam) plus the
  rare table.
- **Every catch item draws a stand-in houseplant sprite** (sweetheart plant, pincushion, jade,
  aloe, schlumbergera, echeveria, snake plant). The two `RM_` items point at echeveria textures
  that exist only in the *campaign* mod's Textures folder. (Grey's catch also uses one shared
  placeholder, so this is the sea-wide state, not a Chill-only lapse.)
- `RUT_RarePropaneCatches` is defined **twice** — once in TerminalBiomes (AuroraGlass removed,
  per the garden ruling: chemfuel ×10–20 at weight 4, oddu ×4–6 at weight 1) and once in
  UtinniPatches (frozen, unedited). Same defName in two mods: whichever loads later wins.

### 1.5 The living cast (from descriptions)

All ten `RM_` cast defs have their own pawn art in `TerminalBiomes/Textures/Things/Pawn/Animal/`.
The six "floor life" bodies (`RM_TheChillFloorLife.xml`) were authored 2026-09-26 from their
catch items' own descriptions (`SEA_FISHABLES_ALIVE_IN_DEPTHS_1`).

### 1.6 Surface-side mechanics (not this sitting, listed for completeness)

`src/RimUtinni/PropaneLakeMechanics/`: pipe network, pumps, valves, rupture, gas vent,
saturation tracker + deflagration, the saturation heist raid, V-wake pump agitation
(`CompVWakeAgitation`, hediff `RUT_PropaneAgitation`). Its first north-star script
(`PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1`) is open, needs the bridge, and is FOUNDRY work —
not a sitting question.

## 2. Gaps against the Grey Sea checklist

`GREYSEA_FLOOR_PASS_1`'s closing spec, line by line, against the Chill:

| Grey checklist line | Chill state | gap? |
|---|---|---|
| Anchor creatures (one enormity + one signature small thing) | The vaunoom is the named giant, but it is **bodySize 1.1** (a large dog) with a 0.9–1.3 draw size, and its description is a *surface* wake. No floor anchor is designed. | **yes — Q1 (cast) and Q4** |
| Floor formations / landmarks (the place, not a cast list) | Ice bedrock, pools, rime terraces. No landmark object a player navigates by or remembers. | **yes — Q4, §4 ideas** |
| Crystal/strange flora, ruled and wired with real plantDensity | Ten species wired at 0.18, art present. | no |
| Own weather | Aurora surge storms built; base weather is generic Clear/Fog. | no |
| The pool defence / the danger mechanism | Fire ban, −110 cold, heated suit clock, garden defence, thermal footprints. | no |
| Elders / a trade or novelty economy | none; the fuel chain and stonewater are the economy | judgement — §4 |
| Cuisine / economy items | hydrocarbon flesh → refinery; stonewater; rime euphoric; AuroraGlass | no |
| Sessile layer | oddu (never moves), tarnn (colony), fessu (drifts) | no |
| Shore mutator specifics | FlowWorks propane suite on shore maps | no (surface sitting) |
| Catch reconciliation (tier) | Grey renamed its catch to `RM_*Catch` (`GREYSEA_CATCH_TIER_RENAME_1`). The Chill's seven are still `RUT_`, so the **free mod's Chill catches two species**; rare table duplicated across tiers. | **yes — Q2** |
| Every catch species also alive on the floor | 8 of 9: zhiil has **no** floor body (its comment pairs it with the adult vaunoom by life stage). | **yes — Q3** |
| Every floor species owes a catch | vaunoom, hoolen, and the two Alpha Animals have none — but see Q1 for whether they belong on the floor at all. | via Q1 |
| Roster JSON amended | `rosters/the_propane_lakes.json` (2026-09-09) still says *"ruled no-fish … CREATURES owed as new defs, not fishTypes"* — overturned by the 2026-09-25 cast sitting. | **yes — housekeeping** |
| Live review sitting: owner walks the floor | not held | **yes — closes the item** |

One more seam, measured: **the floor map uses the same BiomeDef as the surface tile**, so
`RM_TheChill`'s `wildAnimals` IS the floor roster. Four of its twelve rows are not floor
animals by their own descriptions — hoolen *"runs the frozen sheets between the Chill's
pools"*, the vaunoom's *"V-shaped ripple … across the black mirror of the lake"*, and the
two Alpha Animals, donor fliers/floaters. That is Q1.

### 2.1 Two measured seams in how the floor actually populates

These are source readings, not sitting questions — they change what the owner will see on a
walk, so they belong in front of him before it.

- **The natives are tuned 10 °C too warm for their own floor.** All ten `RM_` cast defs carry
  `ComfyTemperatureMin` **−100**; the floor map was set to a uniform **−110** two days after they
  were authored (`CHILL_THERMAL_ENGINE_1`, 2026-09-28). By vanilla's hypothermia rule, every
  native should slowly freeze on its own sea floor — the opposite of the sheet's law that the
  nightside's creatures *"genuinely enjoy the cold"*. Not live-verified; a one-field fix per def
  whichever way it is resolved. (A bug, not a choice — listed so the walk does not discover it.)
- **The 0.08 density does not make the Chill sparse.** The floor is seeded by
  `GenStep_SeaFloorFauna` (`DivingInteraction/Source/GenStep_SeaFloorFauna.cs`), not by the
  vanilla spawner: it computes a total of round(20 × 0.08) = 2, then spawns
  round(2 × commonality) of *each* species. With commonalities 0.3–0.7 that rounds to **one of
  nearly every species** — about eight natives per dive (plus the two Alpha Animals when that
  mod is loaded; the tarnn and the vaunoom roll by chance). So every dive meets a sampler
  of the whole cast, one each, and the sparseness the 0.08 was chosen for never shows. The
  genstep's own comment says the number is a placeholder owed to a live walk with the owner.
  That is Q6.

## 3. Per-species floor + catch table

Description-led; "floor def" = a living pawn on the floor map; "catch def" = an item in
`fishTypes`.

| creature (as described) | floor def | catch def | tier of catch | free-mod catch? | note |
|---|---|---|---|---|---|
| **fessu** — paper-thin crystal plate drifting edge-on where snow falls | `RM_Fessu` .55 | `RUT_Fessu` common 1.2 | campaign | **no** | pair OK; catch tier |
| **krellik** — crab plated in nightly-regrown frost crystal; rime terraces are its work | `RM_Krellik` .5 | `RUT_Krellik` common 1.0 | campaign | **no** | pair OK; catch tier |
| **oddu** — fist-sized shell drawing propane into a euphoric jelly sac; never moves | `RM_Oddu` .45 | `RUT_Oddu` common .8 (+ rare ×4–6) | campaign | **no** | pair OK; catch tier |
| **oovu** — floating jelly bell catching snow; kept for the lamp | `RM_Oovu` .4 | `RUT_Oovu` common .6 | campaign | **no** | pair OK; a "surface" rider, but lives in the fuel column — fine on the floor |
| **iliss** — wire eel on the electrojet currents; shocks | `RM_Iliss` .3 | `RUT_Iliss` uncommon 1.0 | campaign | **no** | pair OK; garden-defence role built |
| **tarnn** — half-crystal colony; boundary with eldspar unsettled on purpose | `RM_Tarnn` .2 | `RUT_Tarnn` uncommon .6 | campaign | **no** | pair OK |
| **heemin** — near-transparent sliver in the top layer, kin of the giant | `RM_Heemin` .7 | `RM_HeeminCatch` common .9 | free | yes | pair OK; catch sprite lives in campaign mod |
| **oovanam** — soot-dark crawler sifting aurora-ash on the floor | `RM_Oovanam` .3 | `RM_OovanamCatch` uncommon .4 | free | yes | pair OK; same sprite caveat |
| **zhiil** — the V-wake's young; thrashes until it freezes | **none** | `RUT_Zhiil` uncommon .4 | campaign | no | **Q3** — the one fishable not alive on the floor |
| **vaunoom** — the V-wake giant, hunts what disturbs the surface | `RM_Vaunoom` .04 (bodySize 1.1) | none | — | — | **Q1** — surface beast on a floor roster; not giant |
| **hoolen** — long-legged skimmer licking fuel frost off the crust between pools | `RM_Hoolen` .4 | none | — | — | **Q1** — a surface animal by its own words |
| **aurora sylph** (Alpha Animals donor) | `AA_AuroraSylph` .5 | none | — | — | **Q1** — donor flier; free mod should stand alone |
| **skyeel** (Alpha Animals donor) | `AA_Skyeel` .5 | none | — | — | **Q1** — same |

Tally: 9 catch species, 8 paired with a living floor body; free mod alone: 2 catch species.

## 4. Five ideas (GPT consult)

_pending — consult running_

## 5. Decisions for the owner

Ranked by how much each changes what a player meets. Plain-language choices; the
recommendation is BENCH's, the call is his.

### Q1 — Who actually lives on the floor? (four animals that may belong upstairs)

The floor and the lake's surface share one biome, so its animal list is the floor's cast.
Four animals on it are, by their own descriptions, not floor creatures: the **hoolen** (a
skimmer that runs on the frozen sheets between pools), the **vaunoom** (the V-wake hunter of
the lake's *surface*), and two borrowed creatures from another mod, a floating **aurora sylph**
and a **sky eel**. The surface already has its own sitting coming.

- **(a) Move all four off the floor now; the surface sitting gives them a home.** *For:* the
  floor becomes the strange solvent-world the flora pass designed, entirely our own; the free
  mod stops leaning on another mod's animals. *Against:* until the surface sitting, the hoolen
  and the vaunoom spawn nowhere (the lake surface has no walkable map of its own).
- **(b) Keep the two borrowed floaters as aurora drifters in the fuel column, move the hoolen
  and vaunoom.** *For:* the floor keeps something large and luminous overhead. *Against:* the
  free mod still depends on a donor, and nobody has checked those two can survive −110 °C.
- **(c) Keep all four.** *For:* no work. *Against:* a surface skimmer licking frost off a
  crust that is not there; the floor's one "giant" is a dog-sized surface hunter.

**Recommendation: (a).** This is a decision at this biome's own sitting, the review machinery
he asked for, not a sweep.

### Q2 — The free mod's Chill catches two species; the campaign catches nine

Seven of the nine catch species (fessu, krellik, oddu, oovu, iliss, tarnn, zhiil) live in the
campaign mod, so a player with only the free mod pulls just heemin and oovanam out of the lake.
All seven names are invented, not Star Wars canon, so the free tier is allowed to own them —
and the ruling is that the free mod must look *the same* as the campaign one. The Grey Sea
fixed the identical situation by moving its catch into the free tier.

- **(a) Move the seven into the free tier, as the Grey did.** *For:* the free Chill fishes the
  same as the campaign; consistent with the other seas. *Against:* one more rename pass;
  the campaign's frozen twin keeps its own copies until the repaint.
- **(b) Leave it.** *For:* zero work. *Against:* the free mod's Chill is a two-fish pond, which
  the "rich enough to stand alone" rule forbids.

**Recommendation: (a)** — and the same pass should give the two free-tier catch items sprites
that live in the free mod (today they borrow a houseplant image from the campaign mod).

### Q3 — The zhiil is caught but never seen alive

The zhiil, the V-wake's young, is the one catch species with no living body on the floor. The
build waved it through as "the young of the vaunoom", but the vaunoom is not a floor animal
(Q1), and the life cycle was ruled flavour only.

- **(a) Give the zhiil its own small floor body**, like the other six got. *For:* satisfies
  "every fishable is also alive on the floor" literally; cheap; a thrashing black juvenile is
  a good thing to meet. *Against:* one more def and sprite.
- **(b) Cut the zhiil from the catch.** *For:* tidy. *Against:* loses the best line in the
  catch table (*"scrapers who have fished up a zhiil pull the line and leave"*).
- **(c) Keep it as a written exception.** *Against:* the rule has no such carve-out.

**Recommendation: (a).**

### Q4 — The floor has no landmark

The Grey floor is a forest of pillars you remember. The Chill floor is ice bedrock, pools and
rime terraces — handsome, but nothing on it is a *place*. The five GPT ideas in §4 are mostly
answers to this. The question is whether the Chill gets one signature set-piece at all, and
which one.

- **(a) Yes, one** (pick from §4).
- **(b) No — the war lab is the Chill's landmark, and the floor is the approach.** *For:* the
  lab is already the biggest set-piece in the campaign. *Against:* most visits never reach it.

**Recommendation:** pending the consult — see §4's ranking.

### Q5 — Ratify the cold-tolerance fix direction

Not really a choice, but it needs his nod because it is a feel number: the natives are
comfortable only down to −100 °C on a −110 °C floor (§2.1).

- **(a) Make the natives comfortable well below the floor** (to −150 °C), so they thrive and
  only the visitors suffer. *For:* matches the sheet's law. **Recommendation.**
- **(b) Warm the floor to −100.** *Against:* softens the brutal cold he ruled.

### Q6 — How many animals should a dive meet?

Today every dive meets roughly one of each species (§2.1), about eight animals, regardless of
the "sparsest sea" number. The Grey (0.1) and the Chill (0.08) therefore feel about the same.

- **(a) Make density mean something:** a dive meets two to four animals drawn by weight, so
  each visit shows a different few and the giant stays rare. *For:* the Chill reads as the
  emptiest sea, as intended; repeat dives differ. *Against:* a player may never meet half
  the cast without many dives.
- **(b) Keep the one-of-each sampler.** *For:* every dive shows off the whole cast. *Against:*
  the sea's emptiness, its whole register, never shows.
- **(c) Decide on the live walk.** The genstep's own comment already defers it to this.

**Recommendation: (c), leaning (a)** — the number is for his eyes on a real dive.

### Housekeeping the sitting can wave through (no options needed)

- Amend `rosters/the_propane_lakes.json` — its fish ruling ("ruled no-fish") was overturned
  2026-09-25.
- The rare-catch table is defined twice under one name (free and campaign mods); settle it
  in the Q2 pass.
- Ratify `animalDensity` 0.08 (FOUNDRY chose it under the zero-density fix; the item said the
  floor pass owns the number) — moot if Q6 replaces the spawning rule.
- The frozen twin's unset density is expected until the repaint — not a finding.
- `PROPANELAKE_FLOOR_PASS_1` has no prose file; this agenda is its first.
