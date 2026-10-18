# Big creatures against slots, thin walls and roofs (DESIGN PASS, 2026-10-18)

Item: `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS` (filed by the owner, 2026-10-18). A design pass, no code: nothing in code,
defs, the bridge or the game was touched. Code claims are from a read-only look at `src/RimMandrake/HugeThings` at
`ae88df220`; vanilla numbers are from RimSage (MEASURED where marked). Numbers marked PROVISIONAL are ours, for his word.

The owner, 2026-10-18 (ledger, filing the item): *"A very large creature (say 10 cell) may see a narrow slot in a wall
as 'something way down there, I don't care' and simply walk over a wall, damaging the wall as though it were an
object. This would not be true of a thin passage through a mountain. If a large creature is trapped by thin wooden
walls around it, it walks through them effortlessly; if the walls were as thick as it is, no longer. I like squeezing
through logic if at least half its width: slowing, not a stop. Do a design pass for the options so we can have
different ideas for maximum game fun. Do a GPT review of your idea. Likely also involves whether the building is roofed
or not: a free-standing thin unroofed wall is easier to smash than a roofed one."*

---

## 0. What already exists (search before designing)

This project keeps having already built it, so first the inventory. **Huge Things** (`src/RimMandrake/HugeThings`,
merged with Titanic Creatures 2026-10-07) already has, MEASURED by reading the source:

| piece | what it does today | file |
|---|---|---|
| size tiers | T1 body size ≥ 4, T2 ≥ 8, T3 ≥ 20 (BENCH draft, not owner-ruled) | `Defs/TitanicTierDefs/RM_TitanicTierDef.xml` |
| the wake | once per cell entered, crushes what the curated table names under the whole footprint: plants from T1, walls and buildings from T2; light 20 / heavy 60 crush damage a step (PROVISIONAL); **T3 destroys a crushable building outright** | `Source/Titanic/Wake/TitanicWakeProcessor.cs`, `Defs/CrushRuleDefs/RM_CrushRules.xml` |
| roofs | thin (built, thin-rock) roofs are holed under the footprint from T2; thick (mountain) roofs are never touched and are avoided in route choice | `TitanicWakeProcessor.ProcessRoof`, `Footprint/Patch_ThickRoofAvoidance.cs` |
| breakthrough clearing | a titan whose path is sealed, or 2.5× longer round than through, walks to the first blocking wall (vanilla sapper route, `PawnPath.FirstBlockingBuilding`) and strikes it once a second, up to 40 strikes, then repaths | `Source/Titanic/Clearing/*`, `Kernel/RM_TitanClearingKernel.cs` |
| footprint | Large Pawns (neku.largepawns) gives 2×2 from body size 2.5, 3×3 from 4.5, 4×4 from 10; **4×4 is its ceiling**; a footprint needs an opening as wide as itself: **a 1-cell gap blocks a 2×2, never squeezed** | `Footprint/LargePawnsBridge.cs`; `design/Jawa/worldbuilding/research/large_pawns_decompile_2026-09-09.md` §2-3 |
| pit width | a pit holds a creature only if it is at least W wide, **W = max(1, round(√BodySize))** (his: *"The pit has to be as wide as the creature to hold it. Otherwise it gets out."*, 2026-10-02) | `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` §3.1 |

So this pass is **not** "give titans wall-smashing". They have it. It is: replace the tier gates (which see only the
creature) with **ratios** (which see the creature *and* the wall), add the squeeze, and make roofs and mountains count.

Two facts that shape every option:

1. **There are already two width ladders**: the pit's √BodySize and Large Pawns' 2.5 / 4.5 / 10 thresholds. They
   disagree (body size 4: pit width 2, footprint 2×2; body size 9: pit 3, footprint 3×3; body size 40: pit 6,
   footprint 4×4). The owner's "10-cell creature" cannot be a 10×10 footprint in this engine. **Every option below
   uses one rules number, the creature's BREADTH B, separate from its collision footprint.** (§3)
2. Vanilla walls (MEASURED, RimSage): `Wall` MaxHitPoints 300 × stuff factor: wood 0.65 → **195 HP**, granite blocks 1.7
   → **510 HP**. Thump and Bomb damage do 2× to walls. Steel and plasteel factors were not looked up (UNMEASURED here).

## 1. The words, made precise

| term | meaning | measured how |
|---|---|---|
| **B, breadth** | how wide the creature is, in cells, for rules | §3: max(1, round(√BodySize)), per-def override |
| **S, slot** | the clear width of a gap the creature's route uses | cells of open ground across the gap, perpendicular to travel |
| **T, thickness** | how much wall the creature must cross | wall cells (any material, air not counted) inside the densest B-deep stretch of one complete crossing, followed by the body's swept area from first contact until it is clear. So layers with gaps add up within the creature's own length (exploit X1), and a deep wall of anything reaches B. The crossing's **summed HP** counts every wall cell in it |
| **built vs mountain** | a cell is "mountain" if it is natural rock or under a thick roof | `RoofDef.isThickRoof`, rock edifice (same test the roof code uses) |
| **P, passage width** | the width a gap must have to be walked normally | max(B, the Large Pawns footprint edge): breadth for rules, but never narrower than the body that collides |
| **roofed** | a wall that really holds up a roof: at least half of the cells within 2 of it on one side are roofed (one roofed corner cell is not a load path) | roof grid, read **when the creature decides**, before its own wake holes the roof |

---

## 2. Candidate rule sets

Six, each genuinely different in what it treats as the deciding quantity. Build cost is in the epic's agent-day
currency, an ESTIMATE.

### Option A. "Ratio ladder" (geometry decides everything)

Two ratios, three bands each, material only through a thickness factor.

- **Slots**: S ≥ B walks normally. **0.5 B ≤ S < B: squeezes**, slowed (curve in §4). S < 0.5 B: the slot does not
  exist for it.
- **Walls** (T_eff = T × material factor, +1 if roofed): T_eff ≤ B/4 **walks through** it, barely slowed. B/4 < T_eff
  < B **smashes** it (the existing clearing job). **T_eff ≥ B holds**: it does not try.
- **Mountain** never yields: rock is never damaged; a rock slot is squeezed or not, nothing else.

| | |
|---|---|
| fun | Very legible: *"my wall is as thick as it is wide, so it stops."* Players build to a number they can see; a krayt in a wooden pen is a disaster, the same krayt behind four granite cells is a zoo. Mountains become the safe place, which RimWorld players already feel. |
| exploit risk | Thick walls are a perfect answer (by design, his words). Stacked thin walls with gaps (fixed by the window). Players fishing for the exact band edge (harmless). |
| build cost | Low-moderate: the clearing kernel already finds the blocker; add a thickness/slot probe and replace tier gates with ratios. Squeeze needs a Large Pawns walkability exception (§6). **2 to 4 days.** |

### Option B. "Momentum against strength" (physics decides)

Impact = mass (body size) × speed over the last few cells. Resistance = wall HP × thickness × roof brace. A charging
titan that has run 8 straight cells hits much harder than one that starts touching the wall.

| | |
|---|---|
| fun | Spectacle: a krayt charging across open sand and exploding through a gate. Players learn to build **zig-zag approaches** (bleed its speed) and **run-out zones** (put the wall where it cannot build speed). A real terrain-reading game. |
| exploit risk | **High.** A one-cell kink in front of every wall makes every titan harmless; AI never charges intelligently; speed jitters with terrain and slow hediffs, so outcomes look random to the player. |
| build cost | High: per-pawn velocity history, a charge behaviour, tuning against every wall material. **5 to 8 days**, mostly tuning. |

### Option C. "Under its belly" (height decides: it steps over)

Each creature has a **step-over height**: walls and gaps it treats as ground. A built wall cell up to B/4 thick is
**walkable to it** and takes trample damage each time a footprint cell crosses it; the wall **survives** if it has HP
left (his literal words: *"walk over a wall, damaging the wall as though it were an object"*). The same applies to
**trenches**: a gap up to B/4 wide is stepped over, a slot S < 0.5 B is "something way down there".

| | |
|---|---|
| fun | The most faithful to his image. A krayt strolling across your fence line leaves a row of cracked walls, not a hole; the wall still keeps your colonists' animals in afterwards, until it is crossed a few times. Narrow defensive trenches stop people and not titans (a real reason to dig wide). |
| exploit risk | Players may be confused why a wall "held" after the titan crossed it. Small trenches stop being titan defence (a nerf of existing pit play, needs his word). |
| build cost | **High**: walls must be passable per creature. 1.6's path grid is map-wide per pathing context; this needs a per-request mask swap like the climb design's cliff masks (`relative_depth_climb_design_2026-10-12.md` §4, risk 2 of the rebuild plan), plus Large Pawns' footprint walkability check patched. **5 to 7 days**, and it shares the multithreaded-pathing risk P2 is proving. |

### Option D. "Squeeze and scrape" (the slot is the whole game)

Built slots are a material, not a hole: a creature squeezing through a built slot **scrapes** its sides, and each
pass widens it. Squeezing near the bottom of the band can **wedge** the creature for a while (a cork in the gap).

- 0.5 B ≤ S < B: squeeze, slowed; every step damages each flanking built cell (20 crush, the wake's light blow).
- 0.5 B ≤ S < 0.6 B: a wedge chance per pass (PROVISIONAL 25%); wedged = stopped 10 to 30 s, then pops through or
  backs out. Rock slots never widen.
- S < 0.5 B: blocked, falls back to the existing clearing behaviour.

| | |
|---|---|
| fun | Slots **evolve**: the gap you left for your muffalo herd becomes a krayt door after three visits, and you see it coming (cracked walls). A wedged titan in your gate is a killing ground and a disaster at once (it is now a wall). Mountain passes stay exactly as narrow forever, which makes them precious. |
| exploit risk | Wedging is a stun the player can farm (a slot at 0.55 B, then shoot). Cap: a creature that wedged once in a slot goes around next time (memory 1 day). |
| build cost | Moderate: squeeze is shared with A; scraping is the wake on flanking cells; wedge is a stance. **3 to 4 days** with A's squeeze. |

### Option E. "Load path" (structures share strength)

A wall is as strong as the building it belongs to. Walls connected to each other under one roof form a **structure**;
its resistance is the sum over the structure (or over the roof's supports within 6 cells, vanilla's roof support
radius). A free-standing unroofed wall stands alone and is weak. Breaking a roofed wall can **drop the roof** it held
(vanilla collapse falls on whoever is under it).

| | |
|---|---|
| fun | Strong match to his roof sentence. A lone sandbag line is paper; a proper roofed bunker is a fortress. The roof collapse is the drama: a titan breaching the barracks wall brings the ceiling down on the beds. |
| exploit risk | Players weld every wall into one giant roofed structure to pool strength (needs a cap: pool only within B cells). Collapse killing colonists may feel unfair if unreadable. |
| build cost | High: a structure graph kept current under building/destruction; collapse is vanilla. **4 to 6 days.** |

### Option F. "Temperament" (the creature's mood decides when, not whether)

Orthogonal to the physics: a **calm** grazer never smashes, only squeezes or goes round; a **frightened** one bolts
through anything thin (stampede); a **manhunting or hungry** one smashes what it can and attacks what it can't for a
while. Trapped (no route at all) counts as frightened after a delay.

| | |
|---|---|
| fun | A wild krayt wandering past your base is a *tension*, not an automatic siege; a gunshot that panics it is a choice with consequences. Taming and penning titans becomes possible: calm penned titans keep to their pens if the pen is not too small. |
| exploit risk | Players keep titans calm (never shoot) and ignore them; fine. Panic chains (one shot, whole herd stampedes) can be brutal; it is the fun. |
| build cost | Low on its own (a behaviour gate in the clearing start). **1 to 2 days**, needs a physics option underneath. |

---

## 3. The breadth ladder (concrete numbers)

**B = max(1, round(√BodySize))**, halves rounding up, the pit's width rule (already his), with a per-def override
`breadthCells` on `RM_TitanicExtension` for creatures whose shape is not a square (a serpent, a whale). Large Pawns'
footprint F stays the **collision** square, capped at 4×4 by that mod. Gaps are judged against **P = max(B, F)**, so a
B 3 creature on a 4×4 footprint is never "normal" in a gap its body cannot fit. The inspect string shows both B and P.

Three rules per crossing, after the GPT review (§9):

- **Holds: T ≥ B physical cells, any material.** His words: *"if the walls were as thick as it is, no longer."*
  Material and roof never change this line.
- **Breaks through without stopping: the crossing's summed wall HP ≤ trample budget 100 × B** (roofed wall HP counted
  ×1.5). The walls break; the step costs ×1.5. His *"walks through them effortlessly"* (thin wood).
- **Smashes: everything in between.** The existing clearing job, one blow a second, **final damage 20 × B a blow**
  (after every multiplier; a roofed wall takes ⅔ of it). A short, visible struggle.

Vanilla HP (MEASURED): wood wall 195, granite wall 510. Budget and blows (ARITHMETIC on PROVISIONAL constants):

| body size | B | example (from the tier item's roster) | trample budget | lone wood (195) | roofed wood (195, counts 293) | lone granite (510) | roofed granite (510, counts 765) | holds at T ≥ |
|---|---|---|---|---|---|---|---|---|
| < 2.25 | 1 | person, muffalo | — | vanilla | vanilla | vanilla | vanilla | — |
| 2.25 to 6.24 | 2 | thrumbo, elephant (bs 4) | 200 | through (if B 2 breaking is on, §5.8) | smash, 8 blows | smash, 13 | smash, 20 | 2 |
| 6.25 to 12.24 | 3 | Krayt (bs 12) | 300 | **through** | **through** | smash, 9 | smash, 13 | 3 |
| 12.25 to 20.24 | 4 | Greater Krayt, Summit Crab (15), Paraceramuffalo (16), Elder Sando (20) | 400 | through | through (double wood 390 too) | smash, 7 | smash, 10 | 4 |
| 20.25 to 30.24 | 5 | — | 500 | through | through | smash, 6 | smash, 8 | 5 |
| 30.25 to 42.24 | 6 | Reefback (32), Lanternwhale (40) | 600 | through | through | **through** | smash, 7 | 6 |
| ~100 (override) | 10 | his "10-cell creature" | 1,000 | through | through | through | through (one cell) | 10 |

Blows per cell; a thicker crossing is the sum over its cells. What that means in a sentence: a Krayt (B 3) strolls out
of any wooden pen, struggles nine seconds per granite cell, and three cells of anything stop it. A Lanternwhale walks
through a lone granite wall and stops at six cells. A ten-cell creature stops only at ten.

## 4. Squeeze curve (concrete numbers)

For 0.5 P ≤ S < P (PROVISIONAL, softened after the GPT review): **cost × (1 + 2 × (1 − S/P))**, i.e. **×2 at half
width**, ×1.5 at three-quarters, ×1 at full width. A squeeze is never a stop.

| P | S | S/P | cost |
|---|---|---|---|
| 2 | 1 | 0.5 | ×2 |
| 3 | 2 | 0.67 | ×1.67 |
| 4 | 2 | 0.5 | ×2 |
| 4 | 3 | 0.75 | ×1.5 |
| 6 | 3 | 0.5 | ×2 |
| 6 | 5 | 0.83 | ×1.33 |

**Geometry of a squeeze:** inside a gap narrower than P the creature moves straight only (no turns, no diagonal corner
cuts); it needs a P × P clear square to enter and to leave; a squeeze interrupted mid-way (job change, save) finishes
or backs out the way it came. The same narrowed area is used for wake damage, collision and reach while squeezing.

**Doors:** a door the creature can open (its own faction, tamed) is a gap of the door's width. A wild animal cannot
open doors, so to it a door is a wall cell with the door's HP.

---

## 5. Recommended combination

**A's squeeze and hold line, materials through HP (the GPT revision), D's scrape (no wedge), F's temperament as a
confinement meter, the roof as resistance; C's true step-over as phase 2.**

1. **Breadth B and passage width P** by §3; one ladder for pits, gaps and walls; Large Pawns stays collision only.
2. **Gaps** (built or rock): S ≥ P walk; **0.5 P ≤ S < P squeeze** at §4's cost with §4's geometry; **S < 0.5 P:
   "something way down there"**: the gap is ignored and the wall around it is judged as a wall.
3. **Built walls**, per crossing: **T ≥ B holds** (any material); summed HP ≤ 100 × B **breaks through** without
   stopping (×1.5 step); otherwise **smashes** at 20 × B final damage a blow, one a second.
4. **Mountain**: natural rock is never damaged, ever. Only the cells actually crossed count: a crossing that contains a
   rock cell cannot be broken there, but a wooden plug between two outcrops is wood. An open-sky gap through rock (a
   canyon slot) is squeezed or not; anything under thick roof stays avoided (his card #1, *"a titan never paths under
   rock"*, already built).
5. **Roof** (his: *"a free-standing thin unroofed wall is easier to smash than a roofed one"*): a wall that really holds a
   roof (§1) counts its HP ×1.5 against the trample budget and takes ⅔ damage from blows. Read at the decision, so the
   creature's own roof-holing cannot weaken the wall first. Breaking it leaves roof collapse to vanilla.
6. **Scrape**: squeezing through a built gap deals 20 final damage to each flanking built cell, **at most once per
   creature step and once per second per cell**: wood gives way on the 10th, granite on the 26th. Gaps widen over
   visits; rock gaps never do.
7. **Temperament, as a restlessness meter**: a wandering or grazing creature prefers routes that break nothing and
   breaks through only when the detour is over the existing ×6 cap. Restlessness rises while its reachable area is under
   6 × P² cells or a need (food, water) is unmet, falls slowly otherwise, is saved, and shows on its inspect string
   ("Restless 40%"). At 100%, or when fleeing, manhunting or hunting, the full rule applies. Opening a door now and then
   does not reset it.
8. **Replaces** the tier gates on walls and buildings (T2 crush, T3 destroy-outright) with this rule. Plants and the
   giant-plant smash keep their tier gates. The B 2 band (thrumbo class) gets **squeeze only** by default; breaking
   and smashing from B 3, a setting.
9. **Reading**: the creature's inspect string: *"Breadth 4 (needs 4-wide gaps) · squeezes gaps of 2+ · breaks walls up
   to 400 HP · smashes up to 3 thick · stopped by 4"*. A wall's inspect string: *"Stops creatures up to breadth N"*
   (from the run of wall it belongs to, not counting roof). Neither is a ground marker (his 2026-10-12 Q4 is about
   markers). A text mote when it squeezes, breaks through, smashes or gives up. Never a silent vanish.
10. **Settings** (every mod ships superb settings): master switch; squeeze on/off and slowdown at half width (default
    ×2); trample budget per breadth (100); blow per breadth (20); hold line (1.0 B); roof factors (×1.5 HP, ⅔ damage);
    temperament on/off; B 2 breaking on/off. Defaults = this list.

**Why this one:** the three lines are his own sentences turned into numbers (half its width; as thick as it is;
effortless through thin wood). Materials matter once, through HP, so granite buys time and only thickness buys a cage.
The scrape and the restlessness meter make it a story. Momentum (B) has the worst exploit and the highest cost; a
full structure graph (E) costs a lot for what the roof factor delivers; true step-over (C) is the most faithful but
needs per-creature walkability, which shares P2's open pathing risk, so it waits. When phase 2 lands, "breaks through"
becomes "walks over, leaving the wall damaged" for the same budget.

**ESTIMATE**: 6 to 9 agent-days for phase 1 (crossing probe and route agreement 2.5 to 3.5, squeeze with the Large Pawns
exception and its geometry 2 to 3, scrape and restlessness 1, settings and strings 0.5 to 1), plus 1 to 1.5 live.

### Exploits and their fixes (recommended set)

| id | exploit | fix |
|---|---|---|
| X1 | wall, air gap, wall, air gap: each layer thin | the crossing is judged whole: its summed HP decides break-through, and wall cells within any B-deep stretch count toward the hold line. Gapped layers are half as good as solid wall at holding, and never free |
| X2 | a deep wall with a gap just under 0.5 P: titan neither passes nor smashes | intended (*"as thick as it is, no longer"*); a held titan paces, grows restless and leaves or rages at the thinnest point |
| X3 | doors as cheap holes in a holding wall | a door is a gap only to a creature that can open it; to a wild one it is wall with door HP |
| X4 | one roofed cell beside a wall to buy the roof bonus | "roofed" needs half the cells within 2 on one side roofed, read at the decision |
| X5 | a rock squeeze as a permanent shooting gallery | softened to ×2; rock gaps are rare map features, and a long rock squeeze is a real fortress (accepted) |
| X6 | a tiny escapable pen, or a door opened now and then, to keep a titan "not trapped" | restlessness reads reachable area and unmet needs, and is not reset by a door |
| X7 | a wooden plug between rock outcrops borrowing rock's immunity | only crossed cells count; the plug is wood |
| X8 | zig-zag or diagonal approach resetting the thickness probe | the probe follows the body's swept area along the chosen route, not a centre line |

---

## 6. Engine notes (why the costs are what they are)

- **Large Pawns blocks every cell narrower than the footprint** (`GenGrid_WalkableBy_LargePawnPatch` fails the cell if
  any footprint cell is unwalkable, decompile §3). Squeezing needs our own exception that, for a creature with P and a
  gap S ≥ 0.5 P, tests a narrowed footprint, straight-line only. Door/portal connectivity is Large Pawns' least settled
  area (its bug PAWN-048); the squeeze must be proven live on 2×2 and 3×3 through 1- and 2-wide gaps.
- **A walkability exception is not enough on its own**: reachability can reject a job target before cell pathing runs,
  and the region graph can accept passages a body cannot fit. Reachability, the region grid and the path search must
  share one "may this creature cross here" answer, and caches must be cleared when a wall breaks or a roof changes
  (event-driven, not only the 600-tick detour cadence).
- **Route, execution and breach must agree.** Today's clearing takes the first blocker of a `PassAllDestroyableThings`
  path. Under the new rule that path may run through a wall this creature holds at; the titan would keep choosing an
  impossible shortcut. The crossing probe must rank breaches the rule allows and skip those it forbids, and must see
  walls touching the footprint's flank, not only its centre line.
- **Breaking through (phase 1) needs no new pathing**: a clearing with no pause and the budget as the strike.
- **Step-over (phase 2)** needs per-creature walkability of walls: request-owned, immutable data handed to 1.6's
  threaded path jobs (a swap-and-restore can restore before the job runs), with a main-thread recheck of each crossing.

## 7. Test ideas via the bridge (minimal list, all five DLCs, no flyers)

Never live-test a flyer's flight; every test creature here is a walker. Results are state reads; one joint look with
him at the end, since a state read cannot show a body drawn through rock.

1. **The canyon lanes (pure squeeze)**: open-sky gaps of 1 to 6 cells cut through natural rock; a B 2, B 3, B 4 and B 6
   creature each sent by a goto job to a goal behind. Read: ticks to cross, lane used, rock HP. Bar: S ≥ P at ×1 ±
   10%; 0.5 P ≤ S < P at §4's cost ± 15%; S < 0.5 P never used; rock HP unchanged.
2. **The thickness ladder**: walls of thickness 1 to 6, wood and granite, roofed and unroofed (24 lanes), no gaps.
   Read per creature and lane: broke through / smashed (blow count) / held. Bar: §3's table cell for cell.
3. **The sandwich** (X1, X8): wood, air, wood, air, wood, approached straight and diagonally by a B 4 creature. Bar:
   T = 2 (densest 4-deep stretch), summed HP 585 > 400: smashed, never broken through layer by layer; five solid
   wood cells instead: held.
4. **The plug** (X7): one wood wall between two rock outcrops. Bar: broken like wood; the rock untouched.
5. **The pen**: a B 3 creature, calm, inside a ring of single wood walls of 6 × P² cells with food; then the food
   removed; then shot. Bar: calm and fed, it stays; restlessness climbs without food and it breaks out at 100%; shot,
   it breaks out within 30 s. Inside a 3-thick granite ring it never breaks out and no wall dies.
6. **The scrape**: a B 4 creature crossing a 2-wide built gap ten times. Bar: each flanking cell loses 20 per step, at
   most once a second; the gap widens when a flank dies.
7. **The roof**: a roofed barracks wall (half the near cells roofed) and a free-standing one, same material, B 4. Bar:
   blow counts differ by §5.5's factors; roof state read before the approach equals the one used; collapse after the
   breach is vanilla's (roof grid before and after).
8. **The door**: a wild B 3 at a granite wall with a wooden door; a tamed B 3 at the same door. Bar: the wild one
   treats the door as wall (door HP); the tamed one squeezes through it.
9. **Concurrency and saves**: two creatures of different B requesting paths in the same tick past the same wall; a save
   and reload mid-squeeze and mid-smash; a wall destroyed by a colonist while a titan is on its way. Bar: no creature
   crosses where its rule forbids; caches update the same tick.
10. **Kernel fuzz offline first** (no bridge): the decisions in a Verse-free kernel beside `RM_TitanClearingKernel.cs`,
    fuzzed like `ClearingFuzz.cs`: monotone in B (bigger never weaker), monotone in T (thicker never easier), rock never
    damaged, roof never makes a wall weaker.

These belong in Huge Things' `validation.py` (its north-star script, `TITANIC_CREATURES_FIRST_SCRIPT_1`) as one new
chain, `walls_and_slots`.

## 8. Questions for him (question-card wording)

1. The recommended combination (§5)? Or a different mix of A to F.
2. **Walk over** (C: the wall survives, damaged) or **break through** (phase 1: the wall breaks)? Break through first,
   walk over later, is recommended.
3. Do thin trenches stop titans? (C says a trench up to B/4 wide is stepped over; today they hold if wide enough.)
4. Does the thrumbo class (B 2) only squeeze, or also break thin walls?
5. Roof: ×1.5 HP and ⅔ damage (recommended), or the full structure strength of E?
6. Squeeze slowdown at half width: ×2 (recommended), ×3 (harsher, a stronger kill zone), or a setting only?

## 9. GPT review

One outside read (`gpt_consult.py`, default model, effort high) of the first draft of this file. It is evidence, not
authority. The draft's §3 to §7 were rewritten in place to take what was accepted; the rejected points are below.

| # | GPT point | disposition |
|---|---|---|
| 1 | Material factor inside a B-cell window means deep wood never holds | **accepted**: the hold line is physical thickness, any material |
| 2 | A centre-line probe is reset by diagonals, corners, zig-zags | **accepted**: swept-area probe over the whole crossing (X8) |
| 3 | "A wall against rock counts as rock" makes wooden plugs immortal | **accepted**: only crossed cells count (X7) |
| 4 | Test 4 contradicted thick-roof avoidance | **accepted**: open-sky rock gaps are legal; under thick roof stays avoided (his card #1) |
| 5 | Doors need an explicit rule | **accepted**: a gap only to a creature that can open it |
| 6 | One roofed neighbour is roof spam; own roof-holing removes the brace before contact | **accepted**: half the near cells roofed, read at the decision |
| 7 | Temperament's "trapped" timer is gamed by tiny pens and doors | **accepted**: restlessness meter on reachable area and needs, saved, visible |
| 8 | Breadth and footprint disagree; a gap can be "normal" by B and blocked by the body | **accepted**: passage width P = max(B, footprint) |
| 9 | ×3 squeeze makes a permanent shooting gallery; the "450 ticks" claim compared unlike things | **accepted**: ×2 at half width; the 450-tick sentence deleted (it was wrong) |
| 10, 11 | Draft blows were really 40 × B after the Thump doubling; the B/4 walk-through deleted granite on contact for B 4 | **accepted**: blows are stated as final damage; walk-through is now an HP budget, so B 4 smashes granite (7 blows) |
| 12 | Materials were rewarded twice (HP and thickness) | **accepted**: materials through HP only |
| 13 | Roof +1 thickness flips double granite from smash to hold at B 3 | **accepted**: roof is resistance (×1.5 HP, ⅔ damage), never a hold-line change |
| 14 | Scrape needs a damage contract; draft test 1 said no HP change on built lanes | **accepted**: once per step and per second per cell; test 1 moved to rock lanes |
| 15 | Stronger combination: half-width squeeze, scrape, temperament, physical thickness hold, HP materials, roof resistance | **accepted**: this is now §5 |
| 16 | Do not call deletion "effortless step-over" | **accepted**: phase 1 is named "break through"; step-over is phase 2 and card 2 |
| 17 | `PassAllDestroyableThings` may propose breaches the rule forbids; flank walls are missed | **accepted** into §6 and the estimate |
| 18 | Reachability and regions, not just walkability, must agree; caches must invalidate | **accepted** into §6 and test 9 |
| 19 | Squeezing needs transition geometry | **accepted**: straight-only, P × P entry and exit, interrupted squeezes finish or back out |
| 20 | Threaded pathing: swap-and-restore races; estimates optimistic; inspect visuals | **accepted** for the threading (§6) and the estimate (raised from 4 to 6 to 6 to 9 days); visuals **partly**: one joint look with him at the end rather than agent screenshots, per the standing joint-review practice |
| — | Momentum and random wedging do not improve the core | **agreed** (both were already left out of §5) |
| 18-20 links | Cited a public decompile, the Large Pawns page, a Ludeon blog post and a multiplayer issue | **not verified here**; recorded as GPT's citations, not as facts |
