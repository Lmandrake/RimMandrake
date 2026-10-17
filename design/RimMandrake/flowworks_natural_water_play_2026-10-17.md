# Natural water as our own water: play, world coherence and rules (RULED 2026-10-17)

Helper B of a double review (lens: **what the player experiences, whether the world stays coherent, and what the
owner's rulings already say**). Helper A covers the vanilla engine hooks; this file does not repeat that work and
names helper A's questions where they decide something. **Written as a proposal; RULED 2026-10-17 (section below).** No code, defs, bridge or game was
touched to write this, and no existing doc was changed. Claims are labelled **MEASURED** (read from a file or the 1.6
decompiled source via RimSage, cited), **COMPUTED** (arithmetic from ruled constants, shown) or **INFERRED**. One
outside read (GPT, `gpt_consult.py`, gpt-6.1-sol) is kept verbatim beside this file as
`flowworks_natural_water_play_2026-10-17.gpt_read.md`. It was given the problem with no recommendation. It is evidence,
not authority; §7 says what was taken.

The owner, 2026-10-17: *"Worth thinking back on natural bodies of water now too... should we just replace them on maps
with our own pits right away, and enable swimming, fishing, and other water interactions within our own scope? It is a
bit odd that there will be 'two kinds of surface water' one that is flattened depth and one that is articulated depth.
Please look into this deeply. I certainly wouldn't want to turn off aquatic farming, swimming, fishing, or other water
interactions."*


## RULED 2026-10-17 (owner; ledger notes on `WATER_NATURAL_DECIDE_ONE_SURFACE`)

The analysis below is kept as written; where it recommends or asks something these rulings settle, the rulings win.
Build packages and estimates: `design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md` (P11-P14).

| # | ruling | authority |
|---|---|---|
| R10 | **One kind of water (engine doc Option B2).** Every pond, lake, canal and pit is one kind; wet squares write the main (base) terrain layer from one ladder of vanilla water terrains chosen by water depth; natural lakes get their floors recorded when the map is made and nothing on a natural lake changes on screen; rivers and oceans stay vanilla, limitless and never run dry (not converted). | card |
| R11 | **Lake depth varies by lake and by biome:** *"Vary it. Some lakes will be shallow and silted up. Others will be deep and chasm-like. Depends on the biome. The more mountainous, the deeper in general. The more plains-like, the smoother/shallower. They should also have some variation down there, not just a radial crater."* Replaces the 0.5 m-per-4-squares slope and the 20 m default / 50 m large-lake numbers as fixed rules. The settable ceiling (to 125 m) stays; 50 m is an upper bound reachable only by mountainous/deep biomes. | owner said |
| R12 | **Pawns may swim in water 2 m or deeper** (vanilla: impassable). Needs swim rules, speed, drowning/exhaustion, apparel/weight, animals. Non-water fluids keep the no-swim refusal. Deep water stops being a barrier for trenches and prisoner pits: flagged as a risk on the pit items. | card |
| R13 | **Limitless bodies are marked:** *"Any natural body of water that is supposed to be 'clearly limitless' should be so marked, so players aren't shocked."* Narrows ruling 35 (card 2026-09-17, *"Stock replaced it — cut the idea."*): limited bodies still show no indicator. | owner said |

**Defaulted, veto-able (not asked; the docs' recommendations):** fish in dug water by the game's size rule (engine Q2a,
follows R10); the same fish return when a dried pond refills (engine Q5a); reeds survive short pump cycles (engine Q6a);
fish live in lakes as well as seas, caught not seen (play Q7a); a 0.5 m beach ring so a drained lake stays reachable
for small animals (play Q4a); a river below a dam keeps flowing from the edge (play Q6b, R10 keeps rivers vanilla).
The steeper-lake question (play Q2) is superseded by R11; play Q1 and engine Q4 by R10 (floors at map creation);
engine Q1 by R10; engine Q3 and play Q2 by R12; play Q1b by R13.

---

## Summary (one page)

**The premise is half right.** Under the designs ruled this month, the "two kinds of surface water" already differ
far less than it sounds:

- A natural pond is **already** articulated the moment a canal or pump touches it. It gets a real floor (shore 1 m or
  2 m, then 0.5 m deeper every 4 squares, capped at 20 m by default). It holds exact litres and has one level surface.
  It draws down into a pond-shaped hollow and refills to the same shape (`pond_depth_design_2026-10-16.md` §0;
  `natural_bodies_as_canals_design_2026-10-11.md` rulings 2026-10-12).
- While a pond is full it **keeps its own vanilla terrain**. That is why fishing, swimming, reeds, ice and drinking
  all still work on it. Only drawn-down squares change look, and they change by water depth in metres, the same as a
  canal (`flowworks_unified_depth_2026-10-17.md` §4.1).

**So the real seams are not "flat lake vs deep canal". There are four smaller ones, and each has a fix (§2):**

1. **The readout and the deep-lake tints exist only for touched ponds.** An untouched lake reads "shallow water" or
   "deep water". A touched one reads "Water 6 m deep". Fix: **give every lake its real floor when the map is made.**
   Record its floor only and change no terrain ("convert the books, not the ground").
2. **Dug water lacks what natural water has.** A colonist's 8 m reservoir may not be fishable, swimmable, plantable or
   freezable unless its water terrain carries the same tags (helper A measures which). To the player this is the
   **real** "two kinds of water". Fix: dug water earns natural water's interactions, rather than natural water losing
   them.
3. **Natural lakes are shallower than colonist digs.** COMPUTED from the ruled slope: a lake 40 squares across bottoms
   out at **4 m**, and one 120 across at **9 m**. The player's default dig is **8 m**. So in practice "natural water
   goes MUCH deeper" (owner, 2026-10-17) is false on almost every map. This needs an owner card (§5, Q2).
4. **Draining a lake strands small animals.** A drained shore is a 1 m or 2 m step. Small creatures cannot climb it
   (`flowworks_elevation_play_2026-10-17.md` §1.1 D). Animals drink only at terrain edges (thirst OQ-5, card
   2026-10-16). So drawing a lake down 1 m cuts every chicken, cat and wild rat on the map off from that water. This is
   a new finding, and it needs a card (Q4).

**Recommendation:** do **not** replace natural water with pit or canal terrain. That throws away Odyssey's fishing,
swimming, water plants and ice, for no gain the player can see. That option was already weighed and rejected as
"Option C" on 2026-10-11. Instead:

- **Stage 1:** dug water gets every water interaction natural water has.
- **Stage 2:** every limited lake gets its floor recorded at map creation, with vanilla terrain unchanged.
- **Stage 3:** drawdown ecology (fish crowding, a beach for animals, silt fields).
- **Stage 4:** rivers and dams.

Oceans and edge rivers stay limitless: their depth is a picture and a readout only. Non-water liquids (the propane
lake, the boiling Scald, brine) keep their own hazard rules. The seabed stays ship-only.

**Owner decisions:** seven plain-language cards in §5.6.

---

## 1. What a player should experience at natural water, once it is our water

All numbers use the ruled constants: a square is 2 m², so 1 m of water in one square is 2,000 L. Shallow-shore floor
1 m, deep-shore floor 2 m, then +0.5 m every 4 squares beyond 3 from shore. Cap 20 m by default (to 125 m), 50 m for
very large lakes and oceans (`flowworks_unified_depth_2026-10-17.md` §5.2, D2).

### 1.1 What natural lakes actually look like under the ruled slope (COMPUTED)

Round lakes, outer two squares shallow (a typical vanilla fringe), floors by the ruled rule. Python, this sitting:

| lake across | squares | water held | deepest floor | squares ≤ 1 m / 2 m / 2.5–4 m / over 4 m | top 1 m of water |
|---|---|---|---|---|---|
| 12 | 113 | 0.36 ML | 2.5 m | 44 / 68 / 1 / 0 | 226 kL |
| 20 | 317 | 1.18 ML | 3 m | 68 / 200 / 49 / 0 | 634 kL |
| 40 | 1,257 | 5.8 ML | 4 m | 132 / 512 / 613 / 0 | 2.5 ML |
| 80 | 5,025 | 31.7 ML | 6.5 m | 260 / 1,140 / 2,616 / 1,009 | 10 ML |
| 120 | 11,289 | 90 ML | 9 m | 380 / 1,764 / 4,632 / 4,513 | 22.6 ML |

- **Most lakes a player ever sees are 2 to 4 m deep in the middle.** A 20 m floor needs about 150 squares to the
  nearest shore, which is a lake wider than a 250-square map (also stated in `flowworks_elevation_play_2026-10-17.md`
  §1.1 D).
- **The world is dry.** Ash'karr is about 5% liquid tiles (`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md`
  §hydrology: Ocean 823 + Lake 312 of the planet). Rivers die as they go, and the seas are terminal. A settled map
  with a 40-square lake is rare and precious. **Every rule below should make that lake feel like a treasure that
  can be spent, not a texture.**

### 1.2 Depth bands: wading, swimming, standing

Pictures follow water depth in metres, everywhere (ruled 2026-10-17). The movement rules below are the **provisional**
bands of `flowworks_elevation_play_2026-10-17.md` §2.4, applied to lakes unchanged (one rule for all water):

| water | look | person (1.75 m) | vanilla today (MEASURED, `design/RimStarWars/aquatic_water_breathing_design.md` §1) |
|---|---|---|---|
| under 25 cm | new very-shallow look (R2, he sees it first) | walks, splashes | n/a |
| 0.5 m | knee-deep (`RM_WaterThin`) | wades, about 1.5× slower | n/a |
| 1 m | vanilla shallow | wades, about 3× slower | `WaterShallow` walkable, path 30 |
| 1.5 m | chest-deep | wades, about 5× slower | chest-deep walkable, path 42 |
| 2 m and deeper | vanilla deep, darker at 5 m and 10 m (tints ruled yes, he sees them first) | **swim or nothing** (play Q2, unasked) | `WaterDeep` **impassable** to anything that does not fly |

The player-facing promise is **"1 m of water behaves the same in a lake, a canal and a pit."** Because a lake square's
look is chosen from the same band table, it inherits the same path cost. The one open rule is whether people may
swim across water deeper than their heads (play doc Q2). It must be answered once, for lakes and canals together.
Vanilla's answer today is "nobody crosses deep water".

### 1.3 Fishing by depth (a proposal that fits the engine and the sea rulings)

MEASURED (RimSage, `Verse/WaterBody.cs`, `RimWorld/Designator_ZoneAdd_Fishing.cs:65`):

- Odyssey fishing works per **water body**, a connected set of cells with a fresh or salt type.
- A body's maximum fish population grows with its **cell count** (`FishPopulationFactorPerBodySizeCurve`).
- Whether it has fish at all, and an uncommon species, are rolled from size (`ChanceFor…FromWaterBodySizeCurve`).
- An uncommon fish is 5% of catches (`FishingUtility.ChanceToCatchUncommonFish`).
- A fishing zone may only sit on **passable** water. Nobody fishes from deep-water squares; you fish *into* the body
  from its shallows or shore.

Proposed play rules (each a card or a default, §5):

- **Fish live by water, not area.** A lake's population cap follows its **volume** in the deep part, not its cell
  count. The 40-square lake (5.8 ML) holds far more fish than a 12-square pond (0.36 ML). Drawing a lake down
  therefore crowds the fish: when the cap falls below the population, the excess is lost.
- **What you catch depends on how deep the body gets.** Common fish in any fishable body at least 1 m deep (elevation
  play §1.1 I). The uncommon/rare roll rises with the body's **deepest floor**. Proposal: today's 5% at up to 2 m,
  doubling at 4 m and again at 8 m. "The big one lives in the deep middle" then holds true, and a player who digs an
  8 m reservoir and connects it gets a deep-water catch.
- **Seas are different and already ruled.** On a land map beside one of our seas, the shore catch is that sea's
  `fishTypes`, laid by the `RM_SeaCoast` mutator (`design/RimMandrake/sea_shore_mutator_spec.md` §0). Every one of
  those fish is **also alive on the sea floor**, which is reached by ship (rulings in §4). The sea's depth on the land
  map is a picture and a readout only: no depth band changes a sea's catch, because the floor is a separate place.
- **Inland lakes are not seas.** The "every fishable is alive in the depths" ruling names **seas** (*"this is true for
  ALL seas"*, 2026-09-26). Read as written, it does not require visible fish swimming in an inland lake. Stated so a
  later pass does not over-apply it, and offered as a card (Q7) in case he meant all water.

### 1.4 Aquatic plants and farming at shallow depths

MEASURED (RimSage, `Defs/Odyssey/ThingDefs_Plants/Plants_Water.xml`):

- Vanilla plus all DLCs has **wild** water plants only: reeds (edible), lily pad, bulrush and lotus.
- They are placed by **terrain tags** (`WaterFreshShallow`, `WaterFreshShallowStill`, `WaterMarshy`, `Mud`), weighted
  by distance to shore. They ignore fertility.
- No sowable aquatic crop appeared in this search. Any "aquatic farming" in the owner's list comes from a mod
  (UNMEASURED which; helper A or a live census should name it). Rice paddies (crops standing in water) are deferred
  in `flowworks_elevation_play_2026-10-17.md` §1.1 G.

Play rules this implies:

- **A plant's band is a depth band.** Reeds grow at 0 to 1 m of water, and lilies, bulrush and lotus in still water up
  to 1 m. If our 0.5 m and under-25 cm looks carry the same tags as vanilla shallow water, these plants grow in canal
  shallows and on drawn-down shelves with no new mechanic. (Whether the tags are carried is helper A's question.)
- **Drawdown moves the reed line.** Lower a lake 1 m. Its old shallow ring goes to mud, and those reeds stand on dry
  ground and die back. The new shallows (the old 2 m shelf, now 1 m) can grow new reeds. That is visible, slow and
  readable: the lake's green ring walks inward as it falls. **This is a delight, if the plant check runs on band
  change.**
- **Rice-paddy terraces (ruling 21, *"YES if we can have this map into farming easily"*) are the player-built
  version.** A 0.5 m terrace held behind a sluice is a paddy. A sowable water crop is new content and stays deferred.

### 1.5 Drawing a lake down: what it exposes (worked scenario)

**Scenario W1: the 40-square oasis lake** (1,257 squares, 5.8 ML, 4 m middle).

- **Pump one basic pump into tanks.** `RM_PumpMath.CycleTicks = 250` and at least one notch (1,000 L) a cycle
  (MEASURED, `Source/RM_PumpMath.cs:9, :22-26`; PROVISIONAL constants) is ESTIMATED about 240,000 L a game day at
  full duty. The top 1 m of the lake (2.5 ML) is about **10 days** of one pump. Draining the whole lake is about
  **24 days**, and needs 360 2×2 tanks (16 kL each) or a dug reservoir to put it in.
- **After 1 m down:** the 132 shallow-shore squares (1 m floor) are dry mud, then cracked lakebed. The water line
  steps back about 2 squares. The shore is now a **1 m sheer step** all round (2 m where the shore was deep water).
- **After 2 m down:** the 512 two-metre squares are dry as well. The water is a 613-square pool, at most 2 m deep, sitting
  in a gradual bowl. Every step inside the bowl is 0 or 0.5 m, so every creature walks the bowl floor (elevation play
  §1.1 D).
- **What the player gains:** fresh lakebed that becomes fertile soil, under the reclaim idiom of §18 of
  `flowworks_mod_definition.md` (filled-in lakebed becomes `SoilRich`; whether a *drained* bed does too is the T3 card,
  not in this rebuild). Also a sunken, sheltered bowl, and 5.8 ML of water in storage.
- **What the player loses:** the reeds, most of the fish (§1.3), and the shore access for small animals (§1.7).
- **Refill:** seepage and rain, at the ruled pace (`RefillPerDay`, size-independent by ruling 30). Or pump it back:
  the return leg (Option A of the 2026-10-11 design) puts water back into the bed. Ruling 5 (card, 2026-10-12): *water
  waits for people and buildings; items wash ashore.*

### 1.6 Dams and floods

- **We dig down, we never build up** (LAW 1, 2026-09-16), and raised ground is dead (R8, card 2026-10-17). So a
  "dam" is a strip of ground left undug with a sluice in it. A flood can only fill holes below the ground surface.
  Water never rises above the land.
- **Damming a lake.** Dig a canal from the lake to a lower dry trench and put a sluice in it. Opening the sluice
  levels the trench with the lake at the mouth's pace (ruled). This is **the flood weapon** (elevation play §1.1 F:
  20 trench squares to 1.7 m take 68,000 L). The 40-square lake can do that about **37 times** (2.5 ML ÷ 68,000 L) before it drops 1 m.
  That is the right feel: a natural lake is a big battery.
- **Damming an edge river.** A river touching the map edge is limitless (ruling 16). If a dug cut or a fill-in
  severs a stretch, the stretch becomes a limited pond with a floor (`flowworks_unified_depth_2026-10-17.md` §5.3).
  Moving water is exempt from the level solve (`pond_depth_design_2026-10-16.md` §0). So a dry riverbed downstream
  of a dam is **not designed today**. It is the most striking thing a player could do to a river ("I stopped the
  river"), and the hardest to do honestly. Stage 4 (§5), card Q6.
- **Vanilla floods** (Odyssey's torrential-rain flood, `RimWorld/TorrentialRainFlood.cs`, MEASURED that it exists)
  and the FloodedCanyon flood driver write temporary water. Helper A owns whether they collide with recorded floors.
  The play rule should be: **a flood never changes a lake's floor, and its water drains back to where it came
  from or vanishes as the flood says. It never becomes lake stock.**

### 1.7 Wildlife: drinking, birds, aquatic creatures

- **Drinking (MEASURED, `src/RimMandrake/FlowWorks/Source/Thirst/`):**
  - Every animal has thirst (OQ-5, card 2026-10-16) and drinks **only at a terrain edge**, never from a tank or a
    trough (`RM_ThirstJobs.cs:79-80`).
  - A drink is debited from the pond behind the cell (`:153-154`).
  - The ocean is not a drink (`RM_ThirstUtility.cs:50-63`: `IsRiver`, or `IsWater` and not `IsOcean`).
- **The stranding problem (INFERRED from the climb rules, not run live).** Once a lake is drawn down past its shore
  floor, the water's edge is inside the bowl, behind a 1 m or 2 m sheer step. Small creatures cannot climb that
  (elevation play §1.1 D: *"small creatures never enter a drained lake on their own, and one thrown in cannot
  leave"*). So, on a desert map whose only water is that lake:
  - **Wild small animals** stop drinking. They die of thirst or leave the map: the wildlife thins visibly.
  - **The colony's chickens, cats and dogs** die of thirst unless the player builds a ramp into the bowl. They cannot
    use the colony's tanks.
  - **Large animals and people** climb 1 m slowly and are fine. A 2 m deep-water shore needs a ramp even for them.
  - This is either a great consequence ("we drained the lake and the desert came back") or a nasty trap the player
    never saw coming. **Card Q4.** The cheapest gentle fix is a natural **beach**: the outermost shore square's floor is
    0.5 m, not 1 m. Draining then always leaves a walkable slope, and the cost is a slightly smaller lake. This is a
    floor-shape rule, so it costs no new art.
- **Birds** fly over all of it. A flying drinker needs only an edge cell, and real flight is a stat (CLAUDE.md
  flight rule). Nothing new.
- **Aquatic creatures:**
  - Odyssey's otters and seals set `waterCellCost` (MEASURED in the aquatic design §1). Water is cheap ground for
    them, and they keep it in any water that keeps a water terrain.
  - Our aquatic xenotypes (Mon Calamari, Selkath and others) are `AQUATIC_WATER_BREATHING_GENE_1`. If they ever
    breathe under water, a 10 m lake becomes **their** terrain, a place others cannot follow. That is a strong
    reason to settle the swim rule once for all water (Q2 of the play doc).

### 1.8 Ice winters

- Ash'karr is tidally locked. The night side is frozen (the Nightside Ice biome; `RM_BlueDesert`'s native liquid is
  icy water, liquid matrix row 7). Propane liquefies below −42 °C (matrix).
- MEASURED (`Verse/WaterBody.cs` `RecacheState`): vanilla freezing lays `ThinIce` as temporary terrain over water whose
  **base** terrain `canFreeze`. A fishing zone keeps working through ice (`Zone_Fishing.cs:65`, ice holes).
- Play rules:
  - **Ice is a lid on the water, never water itself.** Draining under ice leaves the ice standing over a hollow until
    it thaws. It must never become a walkable floor over a 4 m drop that collapses with no sign. The no-vanishing rule
    (*"no animal or pawn ever vanishes without a readable sign"*, 2026-09-29/30) applies: ice over a drained bed
    shows cracks, or melts when the water under it is gone.
  - **Thaw never adds water.** The litres were always in the body; ice is a picture over them.
  - A frozen lake is a **crossing**: walkable ice over deep water, as vanilla allows. That makes winter a raid season
    on lake-moated bases. This is free drama, and worth keeping.

### 1.9 Boats

- No boat appears in vanilla or any DLC (INFERRED, not searched exhaustively). The gravship is the only vehicle, and
  it is the only way to the seabed (ruled).
- If a mod in the live list adds boats, it will key on vanilla water terrain and its passability. Converting books
  but not terrain (§5) keeps any such mod working. Converting terrain would break it.

### 1.10 Oceans at the map edge: limitless

A player can pump the ocean forever. That matches ruling 16, and ruling 4's *"limitless means a stock large enough
that it never matters"* (in summary form; his words are in the session record). What the player sees of an ocean's
depth is the tint and the readout only. A 50 m ocean (D2) shows as a dark, very-deep tint far from shore. **It
must never suggest a way down:** the seabed is a separate planet layer, reached by flying the ship (rulings in §4).

---

## 2. The "two kinds of surface water" problem

### 2.1 What the player actually notices, most jarring first

| # | seam | when they see it | jarring? | fix |
|---|---|---|---|---|
| S1 | **A thing they did at natural water does not work at dug water** (fish, swim, reeds, ice, drink) | building a reservoir and expecting a fishing pond | **high**: it reads as a bug | Stage 1: dug water gets the same interactions (helper A says how) |
| S2 | **Their 8 m dig is deeper than the lake** | digging a reservoir beside a 4 m lake | **high** for this owner, who ruled the opposite | Q2: steepen natural floors by lake size |
| S3 | **Drawing a lake down kills the small animals** | a season after the first big pump | high, and late | Q4: a beach, or accept it |
| S4 | **Two readouts for the same lake** ("deep water" vs "Water 6 m deep") | hovering an untouched lake, then a touched one | medium | Stage 2: floors recorded at map creation; one readout |
| S5 | **Deep-lake tints appear when a pump arrives** | the first canal that touches a lake | medium: the lake "changes colour" when touched | Stage 2: tints from the recorded floor, from arrival |
| S6 | **The ocean never drops; a lake does** | pumping both | **low**: it is what anyone expects of a sea | none; this is coherent |
| S7 | **A river never drops; a severed river stretch does** | dams | low, and rare | Stage 4 |
| S8 | **A full lake shows only shallow and deep, a drawn one shows five bands** | draining | low: the band art *is* the depth being revealed | tints (S5) narrow it |

**Read this table:** the seams that hurt are S1 to S3. **None of them is fixed by replacing lakes with pit terrain.**
S1 is fixed by making dug water *more* like natural water. S2 and S3 are floor-shape rules. S4 and S5 are fixed by
recording floors early and changing no terrain.

### 2.2 The case for ONE representation (every lake converted into our terrain at map creation)

- Literally one kind of water. One code path. A lake is a big canal.
- Every lake has a real floor, a level, a readout and tints from the first frame.
- Draining, refilling and joining canals behave the same everywhere.

### 2.3 The case for TWO representations (vanilla terrain on full lakes, our bands on drawn-down water)

- **Odyssey's fishing, swimming, water plants and ice are keyed on the water terrain itself:** its water body type,
  its tags, `IsWater`, and `canFreeze` on the base terrain (MEASURED above). Keeping the terrain keeps them for free,
  with no re-implementation. "Every DLC is assumed" (owner, 2026-09-19/25/26) makes them **mandatory** features, not
  optional ones.
- Other mods (drinking, boats, wells, hygiene) read `IsWater`. Replacing terrain silently breaks every one of them.
  Converting books does not.
- Lakes keep their vanilla art at full, which is the art players know. Changing it is a cosmetic change and needs his
  permission (CLAUDE.md, 2026-09-15).
- The cost of a terrain conversion falls on every lake on every map, including the ones the player never touches.
  It also needs a save migration that cannot be undone (2026-10-11 design §4, Option C).

### 2.4 The resolution: one model, two drawings

**The "two kinds" the owner fears is a difference in storage, and storage is invisible.** What the player sees is
pictures, readouts and behaviour. Make those one kind:

- **One floor:** every limited lake gets its floor recorded at map creation (Stage 2), and every dug square has its
  dug depth.
- **One surface:** exactly level water per body (R1), lakes and canals alike, joined when connected.
- **One readout:** "Hole · Water (litres)" (R4) on every square that has a floor, lake or canal.
- **One band table** for pictures and movement (§1.2). A full lake square shows its vanilla look, which **is** the
  band picture for its depth (1 m shallow, 2 m+ deep), plus the deep tint where the floor is deeper.
- **One interaction set:** fish, swim, plants, ice and drink work in all water by the same depth rules (Stage 1).

Seen this way, the owner's instinct is right about the **goal** (one kind of water), and *"replace them with our own
pits"* is one **means** to it. It is the expensive means, and it loses features. The cheap means is "record their
floors and teach dug water the same tricks".

---

## 3. Interaction checklist: what is inherited and what must be built

"Natural, full" = a lake square at its own vanilla terrain. "Band" = a square showing one of our depth-band looks
(drawn-down lake, or dug water). **Inherited** = works because the terrain is vanilla water. **Re-implement** = our
code or defs must provide it. Rows marked *(A)* depend on helper A's engine reading.

| interaction | natural, full | band squares (drawn lake, canal, pit) | must keep | must build or decide |
|---|---|---|---|---|
| **Swim (joy)** | inherited. Odyssey `JoyGiver_GoSwimming`: standable `IsWater`, no toxic buildup, at least 10 °C outdoors or in a warm room (MEASURED) | works iff the band terrain is `IsWater` and standable *(A)* | swimming in lakes | band terrains carry the `Water` tag; an indoor dug pool becomes a swimming pool (a delight, free if the tag is right) |
| **Swim (crossing deep water)** | vanilla: nobody crosses `WaterDeep` | same terrain at 2 m+, same answer | consistency | play Q2 (unasked): swim over head or not, for all water at once |
| **Fish** | inherited: Odyssey water bodies by terrain type | iff the band terrain resolves to the body's water type *(A)*; dug water is likely unfishable today | fishing in every lake, river and sea | Stage 1: dug and drawn-down water keep the body type; Q3 (do dug ponds get fish), Q5 (fish when drained); depth-banded rare catch (§1.3) |
| **Wild water plants** | inherited: terrain tags | iff the band terrains carry `WaterFreshShallow(Still)`/`WaterMarshy` *(A)* | reeds and lilies | tags on the 0.5 m and under-25 cm looks; a plant check when a square changes band |
| **Aquatic crops** | none in vanilla+DLC (MEASURED); the mod is UNMEASURED | same | whatever mod provides it | name the mod, then copy its terrain test onto the band terrains; true paddies deferred |
| **Drink (people and animals)** | inherited by our thirst: `IsRiver` or `IsWater` not ocean | inherited iff `IsWater` | drinking at every fresh shore | **reachability**: the beach rule (Q4); a drink debits the body (built) |
| **Wade speed** | vanilla path costs | by band (§1.2) | yes | one table for all water (ruled direction) |
| **Fire** | water never burns | water bands never burn; burning liquids burn at 0.5 m a day per square (D3, defaulted) | yes | the propane lake is a burning natural body: its own row, never "water" |
| **Ice** | inherited: `ThinIce` over `canFreeze` base terrain | iff the base under a band keeps `canFreeze` *(A)* | winter crossings, ice fishing | ice over a drained hollow (§1.8); thaw adds nothing |
| **Drowning** | none in vanilla (MEASURED, aquatic design §1) | ours: by water against height (V2, defaulted) | n/a | one rule for lakes and pits; refill waits for people (ruling 5) |
| **Boats** | none found (INFERRED) | n/a | any mod's boats | do not change the terrain of full lakes |
| **Caravans** | world-level; local water only shapes the paths to the edge | a drained bowl opens new paths | yes | nothing; note that draining a moat lake opens the base |
| **Raids and moats** | deep water is a wall today | 2 m+ bands keep the same terrain | ruling 26 (*"a water moat alone stops nobody"*) strains, play Q2 | settle Q2 once |
| **Quests and landmarks** | Odyssey lake landmarks are generated with the map | unaffected unless a lake is drained | landmarks stay readable | a drained landmark lake should keep its name on the bowl (INFERRED cheap: a map label) |
| **Pollution and toxfish** | inherited: Biotech toxfish by polluted cell share | iff the band keeps the body membership *(A)* | yes | nothing new |
| **Sea catch beside our seas** | the `RM_SeaCoast` mutator lays sea water and the catch | n/a (limitless) | the ruled two-def rule | never let a drained inland lake roll sea fish |

---

## 4. The owner's rulings: what this confirms and what it strains

| ruling (date, words) | verdict | note |
|---|---|---|
| *"a large body shouldn't be able to 'flap between' because it can't be reduced, it's limitless once and for all."* (ruling 16, 2026-09-16) | **confirms** | Oceans and edge rivers stay limitless, so their depth is a picture and a readout only. |
| Ruling 35 (card, 2026-09-17): *"Stock replaced it — cut the idea."*: limited vs limitless is **never shown** | **CONFLICT, between two ruled docs** | `flowworks_unified_depth_2026-10-17.md` §4.3 (ruled the same day as R4) prints *"Open water, never runs dry"* on oceans and edge rivers. That is a limitless indicator. GPT independently suggests "Ocean, replenishing". One of the two must give. **Card Q1b.** |
| *"The biomes should be describing the sea floors (what you encounter as an animal there) as well as what you can FISH out of the oceans on the shore."* (2026-09-21) | **confirms** | The land-map shore catch comes from the sea's `fishTypes`; nothing here moves it. A depth-banded rare catch (§1.3) applies to inland bodies; the sea's catch stays its own. |
| *"All the fishables should also be alive and moving around in the depths (this is true for ALL seas)."* (2026-09-26) | **confirms, scoped** | It names seas. Inland lakes do not owe living fish on screen unless he says so (Q7). |
| *"You can't 'dive' as an individual pawn nor return as one. It's ship or nothing."* (2026-09-26); *"Now the ship just flies to a new planetary layer called sea floor."* (2026-10-01) | **confirms; a guard** | A 50 m ocean tint or readout must never suggest a way down. A drained coastal lagoon touching the sea is impossible (the sea is limitless), so no walk to the seabed can arise. |
| *"As for natural sources, yes they should be able to go MUCH deeper than level 4 canals."* (2026-10-17) | **STRAINED by the later R5** | He said it when the deepest dig was 2 m. Under R5 (dig 8 m by default) and the ruled slope, most lakes (4 m at 40 squares across) are **shallower** than a colonist's dig (§1.1). **Card Q2.** |
| *"but very large lakes and oceans can absolutely go 50m"* (2026-10-17) | **unreachable on a lake** | With 0.5 m per 4 squares, 50 m needs about 390 squares to shore. Only an ocean (a picture) can show it. Q2 fixes that if he wants it. |
| D2: lakes 20 m by default, to 125 m (card, 2026-10-17) | **unreachable as the slope stands** | The same arithmetic: the cap almost never binds. |
| Tints and new water art: *yes, but he sees it before it ships* (card, 2026-10-17); cosmetic changes need his permission (2026-09-15) | **confirms; binds Stage 2** | Showing tints on untouched lakes from arrival changes how every lake looks. That is his look first. |
| *"what's left after the pond is drained? It kind of should be a lowered area of ground"* (2026-10-11) | **confirms** | Already ruled and designed (hollow beds). |
| *"There's nothing wrong with saying the center of ponds or especially large rivers and lakes and oceans might go down way past 4."* (2026-10-12) | **confirms** | The floor exists; Q2 is about how steep it is. |
| Refill: water waits for people and buildings; items wash ashore (card, 2026-10-12) | **confirms** | Applies to every lake the same way. |
| Thirst OQ-5: all animals drink, terrain only (card, 2026-10-16) | **strained by draining** | §1.7 stranding. Q4. |
| LAW 1, *"We dig down. We never build up."* (2026-09-16); R8, real elevation dead (card, 2026-10-17) | **confirms** | Dams are undug ground plus sluices; floods fill holes only. |
| Ruling 26: *"a full 1.5 m canal is a tax, never a barrier ... a water moat alone stops nobody"* (2026-09-16) | **strained** (already noted by the play doc) | A lake is a moat today because vanilla deep water is impassable. Converting books changes nothing; Q2 of the play doc decides it for all water. |
| No worldgen (owner, 2026-08-15); the planet is frozen | **confirms** | Recording floors when a **local** map is made reads only that map's own terrain. That is map generation, not worldgen, as argued in `natural_bodies_as_canals_design_2026-10-11.md` §9.4. Nothing touches the planet. |
| Every DLC is assumed (2026-09-19/25/26) | **confirms; raises the stakes** | Odyssey fishing, swimming and water plants are core. "Turn them off for converted lakes" is not available. |
| Native liquid per biome (2026-09-24); the four seas: Scald boiling, Grey Sea brine, Twilight Sea salt, Propane Lake propane (liquid matrix) | **confirms; a guard** | A natural body of a non-water liquid gets a floor and a level like any body, and **its own** interaction rules: no swimming in propane or boiling water, no drinking brine, and catch only where the sea has one. |
| Biome mechanics promised inside our biomes only (2026-10-15) | **shapes Stage 2** | The planet's lake and ocean tiles carry vanilla `Lake` and `Ocean` biomes (world definition §hydrology). The floor recording should key on the **water**, not the biome, or vanilla-biome lakes keep the old seam. Q1 says which. |

---

## 5. Recommended staged path

### 5.1 Stage 1: dug water earns natural water's interactions (first, because it removes the worst seam)

- Every band look (under 25 cm, 0.5 m, 1 m, 1.5 m, 2 m+) behaves like vanilla water of that depth for swimming,
  fishing, plants, ice and drinking. **Helper A says how.**
- A dug, filled pond of fishable size can be zoned for fishing. It starts **empty** of fish unless it is joined to a
  natural body (Q3).
- An indoor dug pool at 0.5 to 1.5 m is a swimming pool (free, if the tags hold).
- **Proof:** one staged savegame. A 6×6 reservoir dug to 4 m and filled beside a natural pond, then joined. The
  owner swims, fishes and watches reeds in both.

### 5.2 Stage 2: every limited lake gets its floor at map creation (books only)

- When a local map is made (settling, a quest site, a gravship landing), every limited body of a natural liquid gets
  its floor recorded. This is the same rule as today, run early. **No terrain changes.** Full lakes keep their
  vanilla look.
- Deep tints and the readout then work from arrival. Seams S4 and S5 are gone.
- Old saves: the lazy path stays as the fallback. A lake not yet recorded is recorded on first touch, as today.
- **Not converted:** oceans and edge rivers (limitless), and moving water.
- Cost: one distance-to-shore walk per lake per map, and small grids (ESTIMATED KB-scale, per the 2026-10-11 §9.1
  measurements). Helper A owns the real figure.

### 5.3 Stage 3: drawdown ecology

- Fish crowd as the water falls (Q5). Reeds follow the shallows (§1.4). Fresh lakebed becomes silt or fertile ground
  (the T3 card, already owed). The beach rule, if chosen (Q4). A landmark keeps its name on the bowl.

### 5.4 Stage 4: rivers and dams

- What a severed river stretch does downstream (Q6). This needs a moving-water design. Not before Stages 1 to 3.

### 5.5 Leave vanilla, and never touch

- **Leave vanilla:** the ocean (limitless: picture and readout only), the river's current and its edge supply,
  Odyssey's fishing machinery, wild water plants spawning at map creation, the ice machinery, and the look of a full
  lake (until he approves tints).
- **Never:**
  - replace natural water terrain with pit or canal terrain (it loses DLC features and breaks other mods);
  - turn a non-water natural liquid into water, or give it water's interactions;
  - let any depth picture or readout imply a way to the seabed;
  - touch the planet (the world is frozen);
  - show a limited/limitless indicator on a LIMITED body (ruling 35, narrowed by R13: limitless bodies are marked).

### 5.6 Owner decisions (question-card ready; plain language, both sides)

**Q1. When should a lake learn how deep it really is?**
- (a) **When the map is made.** Every lake gets its real floor on arrival; it looks the same as now, but hovering shows
  its true depth, and deep middles can be shaded darker. *Recommended:* one kind of lake from the first day. Cost: a
  small one-time cost per map, and darker shading changes how lakes look (you see it first).
- (b) **Only when a colonist first pumps or digs into it** (today). Cheapest. But a lake reads "deep water" until
  touched, and then suddenly "6 m deep", and may change colour.
- (c) Also apply it to lakes in vanilla-biome tiles (the planet's plain Lake and Ocean tiles), not just ours. Wider
  coverage, outside the "our biomes only" promise of 2026-10-15.

**Q1b. Should the sea say it never runs dry?** Today two rulings disagree.
- (a) **No.** Keep 2026-09-17's "never show limited vs limitless"; the sea's readout shows only its depth. A player
  learns by pumping.
- (b) **Yes, on the sea and edge rivers only.** One word ("open water") on hover. It is honest, saves wasted labour,
  and reverses part of 2026-09-17.

**Q2. Should natural lakes be deeper than what colonists can dig?** Today a 40-square lake is 4 m deep in the middle,
and colonists dig to 8 m.
- (a) **Yes: lakes get steeper the bigger they are**, so a 40-square lake reaches about 10 m and a big one 20 m or
  more. *Recommended:* matches "MUCH deeper" and makes a lake the deepest thing on the map. Cost: drained lakes get
  steeper steps (ramps needed), and lakes hold several times more water.
- (b) **Keep the gentle slope.** Lakes are wide and shallow and walkable when drained. A colonist's deep reservoir
  outdoes nature.

**Q3. Should a pond your colonists dig and fill get fish?**
- (a) **Yes, once joined to a natural lake or river:** fish swim in. A dug pond on its own stays empty. *Recommended:*
  readable, no new item.
- (b) **Yes, always**, slowly, as if from nowhere. Simple, but unexplained.
- (c) **No, only natural water has fish.** Simplest, but it is exactly the "two kinds of water" he dislikes.

**Q4. When a lake is drained past its shore, small animals cannot climb down to drink. What should happen?**
- (a) **Natural lakes get a gentle beach**, so there is always a walkable slope to the water. *Recommended:* nothing
  dies by surprise. Cost: lakes hold a little less, and a drained lake is not a pen.
- (b) **Leave it: draining a lake is a real cost.** Small animals go thirsty unless you build a ramp. Dramatic, but
  late and easy to miss.
- (c) **Let animals drink from troughs and tanks too.** Fixes it everywhere, but reverses the 2026-10-16 thirst ruling.

**Q5. What happens to the fish when you drain a lake?**
- (a) **They crowd into the water that is left; the ones that do not fit are left on the mud as a one-time catch.**
  *Recommended:* a visible reward and cost.
- (b) **They quietly disappear.** Simple; the player may never notice.
- (c) **Fish follow the water's volume, not its area**, so even a half-drained lake keeps a good catch. Forgiving;
  makes draining nearly free.

**Q6. If you dam a river at the map edge, should the river below the dam run dry?**
- (a) **Yes**, the riverbed empties and can be crossed and farmed. Spectacular. Needs its own design for moving water.
- (b) **No**, the river keeps flowing from the edge whatever you do. Simple. "I stopped the river" never happens.

**Q7. The "fish alive in the depths" ruling names seas. Does it apply to inland lakes too?**
- (a) **Seas only, as written.** Lake fish are caught, not seen.
- (b) **All water**: a deep lake shows fish shadows or swimming fish. More art and more creatures to author.

---

## 6. What this file does not cover

- How the engine keeps fishing, plants, ice and swimming working on band terrains: **helper A**.
- The swim-over-head rule, raiders against trenches, and creature width: the unasked cards Q2, Q6 and Q7 of
  `flowworks_elevation_play_2026-10-17.md`. They are referenced here, not repeated.
- Draining a lake into a fertile field: the T3 card (plants on dug and drained ground), already owed.

## 7. Dispositions of the GPT read (`flowworks_natural_water_play_2026-10-17.gpt_read.md`)

| point | disposition |
|---|---|
| "Convert finite lakes at map creation" | **Taken, narrowed**: convert the floor record only, never the terrain (§2.4). GPT's own list of interactions to keep is the argument for not touching terrain. |
| Players notice contradictory rules, not representations | **Taken.** It is the thesis of §2. |
| Seam 1 "activities disappear when a canal touches a lake" | **Taken as a test:** under today's pond design a touched full lake keeps its terrain, so this holds only for drawn-down squares. Their band terrains must carry the tags (helper A). |
| First-contact colour change | **Taken** (S5). |
| Readout: say the litres are this square's | **Taken.** The ruled R4 format already does ("Water 2.37 m (4,740 L)" of one square). |
| Ocean labelled "replenishing" | **Not taken as a recommendation; turned into Q1b.** It collides with ruling 35. |
| Fishing promise: openings in frozen lakes, overfishing | **Taken** (§1.8, Q5). Its Steam link was not opened; ice fishing is MEASURED here independently (`Zone_Fishing.cs:65`). |
| Refilling must not regenerate harvested fish | **Taken** into Q5: fish follow the population rules, never the litres. |
| Ice is a surface; thaw must not refill | **Taken** (§1.8). |
| Never make hazardous seas into water | **Taken** (§4 native-liquid row; §5.5). |
| Draining must not promise access to the seabed | **Taken** (§4). |
| Scenarios (100 squares lowered 0.5 m = 100,000 L, and so on) | **Checked**: 100 squares × 2 m² × 0.5 m = 100 m³ = 100,000 L. Correct. §1.5 uses a bigger lake. |
| "Beds: credible depths beyond the 8 m dig" | **Taken** as Q2. GPT reached it independently from the 8 m figure. |
| Swimming as recreation versus traversal | **Already owed** as play Q2; referenced. |
