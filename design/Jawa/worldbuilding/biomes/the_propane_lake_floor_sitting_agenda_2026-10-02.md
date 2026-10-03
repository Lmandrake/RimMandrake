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

**The required step** (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`, owner ruling 2026-10-01): five ideas, different
from each other and from every other biome, after deep research on RimWorld, its mods and other
games. Run 2026-10-02 via `src/RimMandrake/Utils/gpt_consult.py`, model `gpt-6.1-sol`, effort high
(first attempt timed out at 580 s mid-research; the second completed). Inlined: this agenda,
`the_propane_lakes.md`, the Chill flora pass, `the_scald.md`, `the_twilight_deep.md`, the Grey Deep
agenda, and a digest of every bedazzle review's signature-mechanic rows. **Caveat GPT itself
raised:** it reported that the agenda and flora pass did not reach it (the bundle was ~185k
characters, so they were probably truncated); it checked against the prompt's summary of them
instead. BENCH re-checked each idea against the flora pass and the `CHILL_*` builds below. The
answer is reproduced verbatim in **Appendix A**; precedents it cited include Odyssey, Vanilla
Gravship Expanded, Rimefeller, Oxygen Not Included, Factorio's Aquilo, Subnautica, Barotrauma,
Outer Wilds and Dwarf Fortress.

| # | Idea | What the player does | Rides | Cost | BENCH check |
|---|---|---|---|---|---|
| 1 | **The Wax Procession** | A file of enormous wax colonies crosses the floor eating fuel snow; at pauses they shed dead filter sheets your crew must follow, collect and haul back before the procession walks too far. Killing one spoils the sheet. | a race + lord job, map component for pauses, a collect job | M | Distinct from every built mechanic. **Also answers Q1's hole**: the floor's missing giant becomes a slow herd rather than a hunter. |
| 2 | **Solvent Dissection** | Sealed ancient cartridges: peel them carefully for an intact part, or let the sea's solvent wash them for more metal but a ruined part. You see both outcomes before choosing. | salvage items + a two-recipe comp | S–M | Distinct from the Grey's jacketed salvage (chipping) and the Chill's flesh-to-fuel chain. Smallest build. |
| 3 | **Cold Hold, Warm Heart** | You recover ancient pattern masters pressed in frozen carbon dioxide; they deform if warmed, so your heated ship needs a cold hold and a cold copying bench — warm people, cold knowledge. | item comp reading room temperature, a work table | M | Uses vanilla temperature only (one-heat law respected). Overlaps in spirit with the ship-under-pressure ideas of the Grey; GPT ranks it last for handling burden. |
| 4 | **The Return Comb** | A vast horseshoe of ice-rock cut by black busbars — the exposed return junction of the unfinished planetary dynamo. Its studs answer the aurora in sequences; crews probe pairs and bridge sockets to trace a buried circuit to a service vault. Right reasoning yields a surge-protection design and finite salvage. | a landmark genstep, stud comps, a small circuit-graph map component, study jobs | M–L | **The landmark the floor lacks (Q4)**, and it is the sheet's own "machine under everything" made walkable. Distinct from the electrojet tap and the aurora-surge collector (those harvest; this diagnoses). Risk: an opaque wiring puzzle — GPT caps it at 5–7 nodes with a visible overlay. |
| 5 | **The Dissolved Grudge** (a rite) | Two colonists who have truly fought write accusations on soluble strips, read them, swap them, wash them away in the sea, and promise a quadrum without reprisal. | the rites register's inscription → study → ritual route | M | Fills a found-rite slot without sacrifice; distinct from the register's existing rites (snuffing, anvil gift, effigies, the cold ledger). Must be checked against `salvation_rites_2026-10-01.md` at the sitting. |

**GPT's ranking for the Chill:** Return Comb, Dissolved Grudge, Wax Procession, Solvent
Dissection, Cold Hold. Its one-line verdict: *"The Return Comb would most make the Chill
memorable as a place: an immense black electrical instrument embedded in ice-rock, answering
the aurora beneath a sea of fuel."*

**BENCH's read:** agree on the Comb as the landmark. The Wax Procession is the strongest *living*
idea and solves Q1's empty top of the food chain. One caution from precedent: at the Grey sitting
the owner chose **story only** over a carve-the-waymarks job (Grey Q1) — he has declined a
mechanic that could read as busywork before, so the Comb's puzzle half should be offered
separately from its landmark half (Q4 below).

## 5. Decisions for the owner

Ranked by how much each changes what a player meets. Plain-language choices; the
recommendation is BENCH's, the call is his. In one line each:

1. **Q1** — move the two surface animals and the two borrowed donor animals off the floor (rec: yes).
2. **Q4** — give the floor a landmark: the Return Comb, with or without its puzzle; and the Wax
   Procession as the floor's giant (rec: Comb yes; Procession yes).
3. **Q2** — let the free mod catch all nine species, as the Grey Sea's does (rec: yes).
4. **Q3** — give the zhiil a living floor body (rec: yes).
5. **Q6** — how many animals a dive meets (rec: decide on the live walk, leaning "a few, by weight").
6. **Q5** — natives comfortable below the floor's −110 °C (rec: yes; really a bug fix).

### Q1 — Who actually lives on the floor? (four animals that may belong upstairs)

The floor and the lake's surface share one biome, so its animal list is the floor's cast.
Four animals on it are, by their own descriptions, not floor creatures: the **hoolen** (a
skimmer that runs on the frozen sheets between pools), the **vaunoom** (the V-wake hunter of
the lake's *surface*), and two borrowed creatures from another mod, a floating **aurora sylph**
and a **sky eel**. The surface already has its own sitting coming.

- **(a) Move all four off the floor now; the surface sitting gives them a home.** *For:* the
  floor becomes the strange solvent-world the flora pass designed, entirely our own; the free
  mod stops leaning on another mod's animals. *Against:* until the surface sitting, the hoolen
  and the vaunoom spawn nowhere — measured: no other biome in `src/` lists any of the four.
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
- **(c) Yes, and pick the Return Comb as landmark only** — the dynamo junction stands on the
  floor as scenery and lore, without the circuit-tracing puzzle. *For:* the place gets its
  memory at the lowest cost; the puzzle can be added later without waste. *Against:* the
  Comb's best part is that it answers you.

**Recommendation: (a) with the Return Comb, offered as a pair of choices — landmark only (c),
or landmark plus the five-to-seven-stud tracing puzzle.** And as a separate yes/no: does the
**Wax Procession** become the floor's giant (it fills the hole Q1 (a) leaves)?

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

## Appendix A — GPT consult output, verbatim (2026-10-02, gpt-6.1-sol, effort high)

### Research verdict

**The strongest direction is a submerged industrial landscape whose workings players learn to read.** Cold survival is already built; the remaining opportunities are movement, material handling, spatial investigation and belief.

One limitation: the inline bundle contains the frozen Propane Lakes sheet, but **not the Chill floor agenda or its flora pass**. I checked against your summary of those systems and all supplied biome/rite text; exact flora-level duplication remains unverified. I used six search queries plus primary-source reads.

#### Concrete precedents—and what to take or avoid

- **RimWorld / Odyssey / Anomaly:** Odyssey already supplies the travelling colony, hostile orbital destinations, airtight interiors, oxygen pumps, airlocks and suits. Its alpha-thrumbo quest also follows a herd. Borrow the expedition structure; distinguish any herd proposal from tracking a trophy animal. Anomaly supplies *study something dangerous in place, then acquire knowledge*; avoid another containment-and-exposure loop. [Odyssey](https://store.steampowered.com/app/3022790/RimWorld__Odyssey/), [Anomaly](https://store.steampowered.com/app/2380740/RimWorld__Anomaly/)
- **Vanilla Expanded:** VE Fishing explicitly feeds its fish into **Odyssey’s fishing system** when Odyssey is installed. VE Outposts abstracts unattended production and delivers resources by animals—unsuitable for a ship-only floor. **Vanilla Gravship Expanded Chapter 1** already introduces oxygen networks and structural heat management; Chapter 2 adds orbital threat detection and bombardment. Extend their ship through adapters, without introducing competing heat or attention meters. [Fishing](https://steamcommunity.com/sharedfiles/filedetails/?id=1914064942), [Outposts](https://steamcommunity.com/sharedfiles/filedetails/?id=2688941031), [Chapter 1 source](https://raw.githubusercontent.com/Vanilla-Expanded/VanillaGravshipExpanded/main/About/About.xml), [Chapter 2 source](https://raw.githubusercontent.com/Vanilla-Expanded/VanillaGravshipExpanded2/main/About/About.xml)
- **Alpha Biomes / Alpha Animals / Biomes!:** Alpha’s Propane Lakes is the direct donor, already spent here; Alpha Animals’ useful principle is *each creature contributes a mechanic*. Biomes! Islands demonstrates living aquatic ecosystems and transport-dependent isolation, although it permits swimming visitors. Borrow ecological completeness; reject that ingress rule and the portable animal-resource farm. For **Caverns**, your Lantern Deeps account supplies the concrete luminous flora and specialised cave fauna comparison; its current internals were not independently verified. [Alpha Biomes](https://steamcommunity.com/sharedfiles/filedetails/?id=1841354677), [Alpha Animals source](https://raw.githubusercontent.com/juanosarg/AlphaAnimals/master/About/About.xml), [Islands](https://steamcommunity.com/sharedfiles/filedetails/?id=2038001322)
- **Rimefeller / Dubs Bad Hygiene / SOS2:** Rimefeller supplies extraction, refining and manufactured hydrocarbon products; DBH supplies thermostatically controlled heating infrastructure; SOS2 supplies a habitable ship visiting salvage destinations. Take material processing and compartment planning. Avoid a refinery settlement, another boiler network or a replacement spaceship framework. [Rimefeller](https://github.com/Dubwise56/Rimefeller), [DBH hot water](https://github.com/Dubwise56/Dubs-Bad-Hygiene/wiki/Hot-Water), [SOS2](https://github.com/KentHaeger/SaveOurShip2)
- **Oxygen Not Included / Factorio Aquilo:** ONI makes temperature, gas and liquid plumbing interdependent. Aquilo makes an ammonia ocean into restricted building space and requires heat connections to most machinery. Borrow *material state changes the task*; avoid simulating every fluid cell or making players heat every floor appliance. Aquilo’s developers also describe abandoning actual foundation melting because it was annoying. [ONI](https://store.steampowered.com/app/457140/Oxygen_Not_Included/), [Aquilo developer account](https://factorio.com/blog/post/fff-432)
- **Subnautica / Below Zero / Barotrauma / Dredge:** take the mobile refuge, memorable geological silhouettes, research-station archaeology and expedition commitment. Below Zero’s cold suit and warming refuges duplicate your suit clock. Barotrauma’s active sonar attracts creatures: mechanically attractive, but too close to Grey’s lamp discipline. Dredge contributes boat preparation and regional discoveries; its fog and night threat are wrong for the Chill’s visibility law. [Below Zero](https://store.steampowered.com/app/848450/Subnautica_Below_Zero/), [Barotrauma sonar](https://barotraumagame.com/wiki/Sonar), [Dredge](https://store.steampowered.com/app/1562430/DREDGE/)
- **Dwarf Fortress / Frostpunk 1&2 / Stellaris / Surviving Mars / Outer Wilds / Kenshi / Valheim:** relevant comparisons are DF’s material-dependent engineering and consequential social history; Frostpunk’s generator/heat allocation and later faction bargaining; Stellaris’s science-ship anomalies; Mars’s investigated mysteries; Outer Wilds’s knowledge gained through hazardous geography; Kenshi’s squad recovery expeditions; and Valheim’s biome preparation and maritime logistics. Take readable causes, preparation and discoveries tied to locations. Avoid generic “investigate → research points,” another cold meter, or another permanent planetary transformation. [DF development account](https://www.bay12games.com/dwarves/dev_2019.html), [Frostpunk 2](https://store.steampowered.com/app/1601580/Frostpunk_2/), [Stellaris](https://store.steampowered.com/app/281990/Stellaris/), [Mars](https://store.steampowered.com/app/464920/Surviving_Mars/), [Outer Wilds](https://store.steampowered.com/app/753640/Outer_Wilds/), [Kenshi](https://store.steampowered.com/app/233860/Kenshi/), [Valheim](https://store.steampowered.com/app/892970/Valheim/)

**Physics guardrails:** Titan supplies the hydrocarbon-solvent analogy, not evidence for the fictional biology. Propane remains liquid at −110 °C under suitable pressure. Water ice is structural rock; freezing must be species-specific—nitrogen and oxygen do not become snow merely at −110 °C. Aurora-induced currents should travel through buried conductors, not through propane treated as salty water. [NASA’s Titan account](https://science.nasa.gov/mission/cassini/science/titan/)

### 1. The Wax Procession — work beside a moving giant

A file of enormous articulated wax colonies crosses the floor, collecting settled fuel snow in comb-like undersides. At predictable pauses they extrude exhausted, **dead** filter sheets; crews must follow, collect and haul them back before the procession travels beyond a practical return distance. Killing one ruins the useful sheet into ordinary hydrocarbon flesh. The experience is organising a moving worksite: assigning collectors, establishing temporary stockpiles, and deciding when distance has made another stop unaffordable.

**System:** `Pawn` race with a `ThingComp`, waypoint `LordJob`, `MapComponent` coordinating pauses, and a collection `WorkGiver`/`JobDriver`. Ordinary hauling handles the return. Export only processed inert filter material; the colonies remain untameable floor natives and are not fishable.

**Overlap checked:** Pyrelands’ furnace herd, Scald’s grazing walkers, Sump’s informative mouse trails, and Chill thermal footprints. This herd provides **moving production appointments**; it neither reveals safe ground nor reacts to player heat.

**Precedents:** Odyssey’s herd tracking and Alpha Animals’ behavioural resource creatures; deliberately replace hunting and permanent husbandry with following.

**Cost: M. Risk:** repetitive chasing or path failures. Use several long pauses and automatic job cancellation when the return journey exceeds a player-set limit.

### 2. Solvent Dissection — choose what survives recovery

Ancient sealed cartridges contain metal assemblies embedded in hydrocarbon-soluble potting. Once opened, the sea becomes the dismantling tool. A careful mechanical peel preserves a usable component; a faster solvent wash exposes valuable metal but destroys the assembly’s insulation and alignment. The cartridge’s cutaway preview shows both outcomes before work begins. Players choose which scarce intact parts deserve suit time and which wreckage deserves bulk recovery.

**System:** XML salvage `ThingDef`s; `ThingComp` exposing two recipes; `WorkGiver`/`JobDriver` for field disassembly; fixed ingredient/output accounting. The intact wrapper explains why cartridges survived centuries in solvent.

**Overlap checked:** Grey’s jacketed salvage, Sump’s dig lottery and tar seals, Scald’s wreck stripping, and Chill’s flesh-to-fuel chain. This is **selective material separation with mutually exclusive products**, not uncovering random loot, chipping a mineral case or harvesting more fuel.

**Precedents:** Rimefeller’s hydrocarbon manufacturing and ONI’s material processing; avoid their full fluid networks.

**Cost: S–M. Risk:** “always choose components.” Make intact parts useful for different repairs, and let the wash recover substantially more scarce metal.

### 3. Cold Hold, Warm Heart — organise the ship around incompatible cargo

An ancient archive holds sealed **gasstone relief masters**: mechanical patterns impressed into solid CO₂. They survive the floor but lose their geometry when warmed. Your heated habitat therefore threatens the discovery you just recovered. Maintain an isolated cold hold, send suited readers to a cold copying bench, and return with ordinary durable plans—or sacrifice reading time to collect another master. The ship becomes two adjacent worlds: warm people and cold knowledge.

**System:** an item `ThingComp` reads vanilla cell/room temperature; `CompTempControl`, doors and ordinary rooms provide zoning; a `Building_WorkTable` and custom recipe worker copy masters. Item-holder and gravship-transfer handling must preserve temperature state. VGE compatibility reads its temperature system through an adapter.

**Overlap checked:** Nightside Ice’s preservation and inclusions, Grey’s hull accretion, and Chill’s cold engine/suit clock. The decision is **cargo placement and workflow across room temperatures**. It adds no pawn exposure meter, hull crust, predator attraction or launch gate.

**Precedents:** ONI’s temperature-sensitive logistics, Odyssey’s heated interiors and VGE’s ship management. Avoid Aquilo’s mandatory heating network.

**Cost: M. Risk:** hauling exploits and accidental loss. Give a clear temperature tooltip and gradual deformation; reserve campaign-critical information for durable sources.

### 4. The Return Comb — trace the machine beneath the sea

A vast horseshoe of water-ice bedrock is cut by black busbars: the exposed return junction of the unfinished planetary dynamo. Under drowned aurora, its isolated inspection studs answer in different sequences. Crews measure pairs, mark branches and bridge selected test sockets to trace a buried circuit toward an abandoned service vault. Wrong connections trip local instruments; correct reasoning yields a surge-protection design and finite salvage. The **Comb itself** is the landmark: unmistakable geometry, a low transmitted hum, and machinery continuing beyond both map edges.

**System:** a `GenStep` lays one readable junction; `ThingComp`s represent studs and switches; a `MapComponent` stores a small graph and propagates test pulses. Inspection jobs ride `WorkGiver`/`JobDriver` and `CompStudiable`. Existing aurora `GameCondition` supplies the signal variation.

**Overlap checked:** Rust Cathedral’s attitude/hum and watched bolts; Umbra’s electrojet tap; Blue Desert’s charged reed; war-lab keys. This is **spatial circuit diagnosis**, with deterministic electrical behaviour rather than a sentient response, power harvest or new dungeon key. It never controls the dynamo or changes the world.

**Precedents:** Outer Wilds’s hazardous, physical investigation; Stellaris/Mars anomalies translated into actions on the map. Conductors carry the currents; the propane does not.

**Cost: M–L. Risk:** becoming an opaque wiring minigame. Limit the graph to five–seven nodes and show every measured connection on a persistent map overlay.

### 5. The Dissolved Grudge — relinquish a feud

At an old wax tablet beside the sea, the clan finds a practice for **Sh’kaar’s remaining found-rite slot**. Two colonists who have actually fought write their accusations on separate soluble strips, read them aloud, exchange them, and wash the words away. They then promise a quadrum without reprisal. Lights remain burning, weapons remain owned, and suits remain heated: the thing denied to Sh’kaar is the continuation of a fight. Success lays down one reciprocal fight memory; renewed violence breaks the promise and provokes his displeasure.

**System:** the supplied inscription → `CompStudiable` → rubbing → rites research → `Ideo.AddPrecept` route. `RitualPatternDef`, participant filter, custom outcome worker, and a `GameComponent` track the named pair and promise. Ninefold receives `ApplyDelta`; no new divine arithmetic.

**Overlap checked:** Snuffing denies light; Anvil Gift destroys a weapon; Sump effigies purchase another party’s misfortune; Cold Ledger settles a dead person’s debt. This rite **ends reciprocal retaliation between living participants**, without sacrificing wealth or changing faction goodwill.

**Precedents:** DF’s enduring grudges and religious practice; Frostpunk’s social settlement under environmental pressure. The solvent gives the promise a physical act unique to this sea.

**Cost: M. Risk:** manufacturing social fights for repeat rewards. Require a genuine prior incident and allow each pair/incident to be settled once.

### Ranking for the Chill

1. **Return Comb:** strongest landmark, campaign fit and place-specific discovery.
2. **Dissolved Grudge:** gives the hostile expedition a belief worth bringing home.
3. **Wax Procession:** adds large-scale life and a distinctive moving labour problem.
4. **Solvent Dissection:** economical implementation; makes the solvent matter directly.
5. **Cold Hold, Warm Heart:** excellent ship interaction, but highest compatibility and handling burden.

All five use the existing ship-only `PlanetLayer` route, ordinary temperature and the existing suit/fire rules; finite claims need a tile-keyed ledger so regenerated floors cannot duplicate rewards.

**The Return Comb would most make the Chill memorable as a place: an immense black electrical instrument embedded in ice-rock, answering the aurora beneath a sea of fuel.**

## Rulings — 2026-10-02 sitting (decision taken by question card, 19:30–19:40 PDT)

| Q | Ruling | Item (FOUNDRY) |
|---|---|---|
| Q1 | Move all four non-floor animals off the floor (hoolen, vaunoom, both Alpha Animals borrowings); they wait for a surface home | `CHILL_FLOOR_CAST_TRIM_1` |
| Q2 | Move all seven campaign-only catch species into the free mod, as the Grey Sea did; settle the duplicate rare-catch table; amend `rosters/the_propane_lakes.json` | `CHILL_FREE_TIER_CATCH_1` |
| Q3 | The zhiil gets its own small floor body | `CHILL_ZHIIL_FLOOR_BODY_1` |
| Q4 | The Return Comb, as scenery and lore only (no tracing puzzle) | `CHILL_RETURN_COMB_LANDMARK_1` |
| Q4b | The Wax Procession becomes the floor's giant | `CHILL_WAX_PROCESSION_GIANT_1` |
| Q5 | Natives comfortable to −150 °C; the floor stays −110 °C | `CHILL_NATIVE_COLD_TOLERANCE_1` |
| Q6 | Make density actually govern a dive's spawns; the number is set on a live walk with the owner, leaning 2–4 per dive | `CHILL_DIVE_DENSITY_SAMPLER_1` |
