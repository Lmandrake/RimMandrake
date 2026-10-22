# Deeper digging: play, rules and coherence (PROPOSAL, 2026-10-17)

Item: `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` (the owner ordered this double review there, 2026-10-17 ledger note).
**RULED in part 2026-10-17 (by card, after this review):** Q1 (c) 8 m by default (a setting from 2 to 20 m); the four
quietly absolute rules of §5 (drowning, falls, spikes, shooting) become relative to the height difference, built in one
rebuild with level water; real elevation is dead. Q2, Q6, Q7, Q9, Q11 and Q12 are still unasked; Q3, Q4, Q5, Q8 and Q10
are veto-able defaults in the build plan, `design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`. The rest of this file was a proposal. This is helper B of a double review: the **play, rules and coherence** lens. Engine cost is
helper A's file; it is not repeated here. Nothing in code, defs, docs, the bridge or the game was touched. Code claims
are from a read-only look at `src/RimMandrake/FlowWorks` at `664f8dd1a`. One outside read (GPT, `gpt_consult.py`,
gpt-6.1-sol) is kept verbatim beside this file as `flowworks_elevation_play_2026-10-17.gpt_read.md`; it is evidence,
not authority, and §7 says what was taken from it. Numbers marked PROVISIONAL are ours, for his word.

The owner, 2026-10-17 (ledger, `WATER_SURFACE_REPAIR_LEVEL_OR_BUST`): *"how should we determine the right number of
quantized levels to support? The same goes for max pit depth. I'm starting to think we shouldn't limit the player to
just four levels of canal. Please evaluate ... allow them to make say a square of 4 4 4 4 / 4 7 7 4 / 4 7 7 4 / 4 4 4 4
(metres depth) if they wish. ... rules like 'ladders/ramps are required to go down delta elevation, not just enter a pit
of some depth in an absolute sense.' This would allow drained lakes to really look like large stretches of depressed
terrain should they get drained. ... feasibility in the game engine, dev time required, and the fascinating play
experience it could bring to players ... natural breaks in complexity ... our two primary use-cases are water
storage/movement and prisoner containment. ... plants growing on those squares if left for a while."*

---

## Summary (one screen)

1. **The "delta, not absolute" rule is already his, and already built.** He ruled it on 2026-10-12 (*"it should be
   relative height (the depth of the pit relative to its N, S, E, W, neighbors) so that gradual slopes never trap
   anyone"*), and `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` built it offline (live proof owed). Ramps span 1.5 m, a
   ladder any depth. So deeper digging needs **no new climbing idea**. What it needs is the rest of that work landed
   (the pathing masks and the ramp, items 2 and 3 of that design) **before** holes get deeper, or the AI will walk
   down 7 m walls like stairs.
2. **The right step is still 0.5 m, because every climbing threshold is a multiple of 0.5 m** (small creatures 0.5 m,
   people 1 m, large 1.5 m, huge 2 m). A finer dig step adds clicks and no decisions; a coarser one erases the
   small/person line. Water is already continuous (ruled today: *exactly level*). So there are **three different
   quantities, quantised three different ways**: dig depth (0.5 m steps), water (continuous), pictures (bands chosen
   by what a pawn's body meets, §2.3).
3. **The natural breaks in rules come early and then stop.** 2 m (today) traps everything but huge creatures. **2.5 m
   traps every walking creature in vanilla** (3 m with our provisional climber and leaper bonus). Past that, depth adds storage, drama, fall height and labour, but **no
   new kind of rule**. The breaks after 2.5 m are about scale (falls that maim, rescue time, AI and art), not about
   holding.
4. **Labour already gives a natural cap.** Digging cost rises with each notch (`RM_ExcavationDepth.WorkToDeepen` =
   3,200 × the notch being cut, MEASURED), so one cell costs about half a game-day of work to 2 m, 2 days to 4 m, 5.6
   days to 7 m and 44 days to 20 m (continuous work at speed 1, ARITHMETIC). His 4/7 square is about **45 work-days**.
   That is an endgame project, which is the right feel for a reservoir.
5. **Deeper digging exposes four rules that were quietly absolute and now misfire** (§5): drowning is "any liquid in a
   2 m pit"; fall damage is "drop ÷ the deepest dig", so raising the cap would make a 2 m fall *safer*; spikes are
   "the deepest cells", which moves with the cap; and the "only shoot your neighbours from a pit" rule is "anyone 2 m
   down", so a firefight on the floor of a big basin would be locked to arm's length.
6. **Recommended first tier: colonists dig to 8 m** (16 notches), lakes keep their ruled 20/50/125 m floors, and the
   four absolute rules above are restated by height and metres. Defer anything that makes depth *do* something new
   (shade, darkness, gas pooling, cave-ins, groundwater, rice paddies). Twelve plain-language cards in §6.

---

## 1. What players could do, tier by tier

**Units.** 1 notch = 0.5 m. A square is 2 m², so 1 m of water in one square is 2,000 L. A person is about 1.7 m tall
(the pit draw treats a person as 1 cell from feet to crown and sinks 0.3 cells per notch, `RM_PitDrawMath`; 1 cell ≈
3.3 notches ≈ 1.7 m). Climb limit K (ruled 2026-10-12, bands PROVISIONAL): small 0.5 m, person 1 m (slow), large
1.5 m, huge 2 m; climbers and leapers +0.5 m; flyers never trapped. Dig work per cell to depth n notches =
1,600 × n × (n + 1) work units (MEASURED formula; days = ÷ 60,000 ticks at speed 1).

| tier | deepest dig | one cell's dig work | what it adds in play |
|---|---|---|---|
| **0 (today)** | 2 m | 0.5 day | person pits, fire and flood traps, shallow irrigation canals. Huge creatures (thrumbo, elephant) can never be held. |
| **1** | 2.5 to 3 m | 0.8 to 1.1 days | **every walking creature can be held** (a 2×2, 2.5 m pit holds a thrumbo: body size 4 needs width 2). The last *holding* threshold. |
| **2** | 4 to 8 m | 1.9 to 7.3 days | his 4/7 square; two-stage prisons; real reservoirs with dead storage below the outlet; terraces; switchback ramps; falls that maim. Rules: none new beyond §5. |
| **3** | 20 m (lake parity) | 44 days | dug lakes. Nothing new to hold or climb; pure scale, and labour makes it rare. |
| **4** | 50 to 125 m | 6 months to 2 years a cell | spectacle only. Natural lakes and oceans already reach this (ruled D2); there is no play reason for a colonist to dig it. |

### 1.1 Scenarios, with numbers

**A. His square: a desert reserve (tier 2).** 4×4: twelve cells at 4 m, a 2×2 sump at 7 m.
- Holds **152,000 L** brim-full (12 × 4 m + 4 × 7 m = 76 m of column × 2 m²). A flat 2 m 4×4 holds 64,000 L. A
  2×2 tank holds 16,000 L. So the reserve is about **9½ 2×2 tanks in 16 squares**.
- Cost: about **45 work-days** (12 × 1.9 + 4 × 5.6). A flat 2 m 4×4 is about 8.5.
- **Where the water goes.** Thirst is 3 L a colonist a day (ruled, thirst design): ten colonists drink 152 kL in about
  5,000 days (over 80 game years). Drinking is not the drain. A sprinkler field of 100 cells uses 1,200 L a day (ruled
  0.5 L per cell-hour): about 127 days, two game years. An irrigation canal burning 0.5 m a day per square (D3,
  defaulted) uses 1,000 L a square a day: a 10-square canal empties it in about 15 days. **Depth stores; canals spend.**
- **Dead storage (the interesting part).** Water is level (ruled today), and a canal takes only water above its own
  floor. A 1 m outlet canal at the rim draws the top 1 m: 16 × 1 m × 2 m² = **32,000 L by gravity; the other 120,000 L
  needs a pump.** The player decides how deep to cut the outlet: a deep outlet drains more by gravity but needs its own
  deep channel all the way to the fields. That is real reservoir engineering, and the rules already produce it.
- As it drains, the 4 m ring shows as a dry terrace while the sump keeps the last 24,000 L. With §3's plants, the ring
  greens over in a dry season (fresh water leaves silt).
- **Getting in.** Surface to ring is a sheer 4 m: no creature climbs it. Ring to sump is 3 m: same. A colonist needs
  a ladder, or a switchback of ramps (a ramp spans 1.5 m, so 4 m needs three ramp steps). His ring is one cell wide,
  so a switchback cannot fit on it: he needs a ladder, or a wider ring. That is a design choice the player sees.

**B. The two-stage oubliette (tier 2).** The same square, dry. A prisoner in the sump faces two sheer walls (3 m, then
4 m). One lowered ladder is not an escape; a prison break needs both. A raider knocked in from the rim falls 7 m.

**C. The thrumbo pit (tier 1).** A 2×2 pit at 2.5 m, covered. Today no depth holds a thrumbo. At 2.5 m, a thrumbo
that falls through the cover is held, takes a big fall (§2.5) and can be shot from the lip or tamed down. This is the
smallest change that makes megafauna hunting a pit game.

**D. The drained lake (any tier; lakes already go deep).** A 20 m lake slopes 0.5 m every 4 squares from its shore
(ruled), so every step on its floor is 0 or 0.5 m: **every creature walks the whole bowl**, as he wanted. The one step
that matters is the **shore**: 1 m where the shore was shallow water, 2 m where it was deep water.
- People climb the 1 m shore slowly; a 2 m deep-water shore is a wall to people (they find the shallow part).
- Small creatures (K 0.5 m) **cannot climb the 1 m shore at all**, and nobody walks *down* a step taller than they can
  climb. So small creatures never enter a drained lake on their own, and one thrown in cannot leave. It is not a trap
  for people; it is a ha-ha (a sunken fence) for rats, cats, dogs, chickens and toddlers.
- A 20 m middle sits about 150 squares from shore, so only very large lakes get there; a 30-square pond bottoms out
  at its 2 m shore depth. The "large stretches of depressed terrain" he wants are big lakes, and they are the ones that read
  as landscape.

**E. The ha-ha pen (tier 0, already possible).** A 1 m sheer pocket holds small animals with no fence; colonists walk
in and out slowly. Note: vanilla's pen system does not know it is a pen (INFERRED), so roping and pen markers do not
apply; the animals simply cannot leave.

**F. The dam break (tier 2).** A dry 2.5 m trench across the approach, a covered stretch to drop raiders in, and the
reserve upstream behind a sluice. Open the sluice: water levels into the trench at the mouth's pace (ruled). Filling
20 trench cells to 1.7 m (over a person's head) takes 68,000 L, so the reserve can do it twice. This is ruling 26's
*"trap-then-flood pipeline"*, with a reservoir big enough to matter.

**G. Terraces (tier 2).** Steps of 0.5 m walk for every creature. Each terrace is its own level water body behind a
sluice at the step, so water cascades terrace to terrace. With §3's fertility they farm; irrigation counts plants by a
filled canal as watered (existing FlowWorks mechanism). True rice paddies (crops standing in shallow water) are a new
crop mechanic: deferred.

**H. The sunken court (tier 2).** A 3 m deep, 10×10 court reached by a ramp switchback. It is outdoors, lit and hot,
and holds no rule of its own. Its value is defence (one controlled way in) and look. Shade from a low sun, shelter from
the dune gale, and "cooler down there" are all new rules: deferred, and each would need his word.

**I. Fish ponds.** Whether a dug, filled pond counts as fishing water is an engine question (helper A). The play rule
is simple if it does: fish need water deeper than 1 m, and a deeper pond holds more fish because it holds more water.

### 1.2 Most delightful

1. **The reserve with dead storage** (A): one dig makes a visible drought clock, a terrace that greens as it drains,
   and an engineering choice about outlet depth. It serves irrigation, his second goal.
2. **Holding anything that walks** (B, C): two-stage prisons and megafauna pits. Defence, his first goal.
3. **The drained lake as landscape** (D): a bowl people walk, a ha-ha for small animals, silt fields after (§3). This
   is terraforming, his fourth goal, from rules that already exist.

### 1.3 Most griefing or exploit-prone (and the cheapest rule that kills each)

| problem | what goes wrong | cheapest fix |
|---|---|---|
| **AI walking cliffs** | Until the per-band pathing masks land, vanilla's pathfinder sees a dug cell as costly ground, not a wall (MEASURED gap, `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` "gaps"). At 7 m that is pawns walking down a sheer wall. | **Order, not a rule:** no deeper digging until the masks and ramps (climb design §8.7 items 2 and 3) are built and proven live. |
| **The perfect moat** | A closed sheer trench with the ladder raised stops every walking raid forever. True today at 2 m for people; deeper makes it true for mechs and megafauna too. Drop pods, flyers and sappers' targets (walls) still exist, but a ground raid has no answer. | Card Q7: organised raiders bring **scaling ladders** (a destructible ladder from a reachable lip, about 10 s + 1 s a metre, PROVISIONAL). Or he rules the perfect moat is a feature: defence is his first goal. |
| **Jobs that never arrive** | A doctor takes a rescue at the bottom of a 7 m pocket, cannot get there, takes it again. Reachability for our own colonists is not yet tied to the climb rule (MEASURED gap: captured pawns and pawnless queries only). | Job reachability uses the same climb permissions as walking, including the way back while carrying someone. Already the plan (climb design §8.5 step 6), needed before any deeper dig. |
| **Death by a puddle** | Drowning today is "any liquid in a 2 m pit, non-swimmer" (`RM_PitFillEffects`, MEASURED). With level water, 4 cm drowns. | Drown by water against height (§2.4). |
| **Giants walking up cliffs** | His width rule (*"The pit has to be as wide as the creature to hold it. Otherwise it gets out."*) means a thrumbo in a 1-wide, 20 m slot walks out up 20 m. | Card Q6: bracing gets a creature out only within reach (about twice its climb); deeper, it stays down. |
| **Remote everything** | "From the lip, warden adjacent" scales to tending a wound 20 m below. | Card Q11: capture, convert and feeding stay from the lip at any depth (his words); hands-on care (tend, rescue, strip, haul) needs a lowered ladder. |
| **Arm's-length firefights in basins** | Ruling 23 lets a pit occupant trade fire only with its 8 neighbours, keyed to "dug 2 m or more" (MEASURED key). Two pawns on the floor of a 4 m basin could not shoot each other. | Card Q8: the restriction applies across a cliff edge, not to everyone deep. |
| **Fire and gas in pits** | Fire on an oil pit, smoke and toxic gas. | **No depth rule.** A deep oil pit holds more litres, so it burns longer if fire eats a fixed amount per square per hour; that is all. No gas pooling, no depth immunity, no depth damage bonus. |
| **Stranded colonists** | A colonist who jumped in, ladder raised, starves quietly. | Card Q12: a top-right alert when our own colonist cannot reach food or bed because of a pit. Not a marker on the ground (he ruled no ground markers, 2026-10-12 Q4). |

## 2. The rules that keep it coherent

### 2.1 One sentence

**How deep a cell is decides what it holds (water, a fall, a bonus to nothing else). The step between two
neighbours decides who can cross. The water above the floor decides who can wade.** Never one for the other.

### 2.2 Climbing, ramps, stairs and ladders by delta (ruled 2026-10-12; numbers PROVISIONAL as ruled)

| step between neighbours | small | person | large | huge | ramp | ladder |
|---|---|---|---|---|---|---|
| 0.5 m | climbs | climbs | climbs | climbs | not needed | — |
| 1 m | **wall** | climbs slowly | climbs | climbs | one ramp, walking speed, everyone | yes |
| 1.5 m | wall | **wall** | climbs slowly | climbs | one ramp | yes |
| 2 m | wall | wall | **wall** | climbs slowly | two ramps (1.5 + 0.5) | yes |
| 2.5 m and more | wall | wall | wall | **wall** | a chain: one ramp per 1.5 m, each needs its landing | yes, any height |

- **A stair is a ramp.** One rule: one cell bridges at most 1.5 m, both ways, at walking speed. A 7 m wall needs five.
  That takes room, which is the point: a ramp chain is a road, a ladder is a door.
- **A ladder spans any height** (his: *"A ladder can go down arbitrarily deep but still goes somewhat slow"*). Speed
  PROVISIONAL at 1 s a metre, doubled while carrying a pawn. It keeps the prison-door rule (his, 2026-10-02 Q1).
- **Nobody walks down a step they cannot climb back up** (climb design §8.1). Going in that way is a fall, and only
  force (a cover, knockback, the jump button) does it.
- **Diagonals** never cut a cliff corner (§8.1).

### 2.3 Pictures: what is quantised and why

| quantity | step | why that step |
|---|---|---|
| dig depth | **0.5 m** | every climbing threshold is a multiple of 0.5 m; nothing a player decides changes at 0.25 m |
| water | **continuous** (ruled 2026-10-17, *exactly level*) | water's one trait is a level surface |
| water picture | **by what the water reaches on a person**: under 25 cm (very shallow, ruled today, new art he sees first), knee 0.5 m, waist 1 m, chest 1.5 m, over the head 2 m and deeper; darker tints at 5 m and 10 m for lakes (ruled, he sees them first) | those bands are where wading changes (§2.4). The four existing water looks already line up with a person's knee, waist, chest and head: a happy accident worth keeping. |
| wall picture | **by the step to each neighbour, not the cell's depth**: a lip (0.5 m), 1 m, 1.5 m, 2 m, and one tall dark "cliff" look for anything over 2 m | the climb rule is per edge, so the picture should be per edge (his, 2026-10-12 Q4: *"If you can't even see your pawn's body because of a cliff, it's no surprise when they can't walk through it"*). **Five wall looks, whatever the deepest dig.** Art cost stops growing with depth. |
| pawn sink | lowers with the cell, **capped at "below the lip"** (today: 2 m) | a pawn 7 m down cannot be drawn 7 m lower on screen; it reads as "down there" by the cliff faces round it and a darker floor shade |
| absolute depth | **the readout** ("floor 7 m down") and a floor shade | a number is the only honest way to tell 7 m from 8 m |

### 2.4 Wading, swimming and drowning by height (PROVISIONAL bands; H = the creature's height)

| water above the floor | effect |
|---|---|
| up to 0.3 H (knee on a person, 0.5 m) | wade, about 1.5× slower |
| 0.3 H to 0.6 H (waist, 1 m) | wade, about 3× slower |
| 0.6 H to 0.9 H (chest, 1.5 m) | wade, about 5× slower |
| over 0.9 H (2 m and deeper on a person) | **swim or nothing**: a non-swimmer will not go in on purpose; a swimmer crosses slowly |
| over H standing, or over 0.2 H downed | drowning, unless it can reach shallower water it can climb to |

- **"One litre in a 7 m pit cannot drown its occupant."** (GPT, adopted.) Drowning follows the water, not the hole.
- **Swimming never climbs a wall.** A swimmer in a flooded sheer pit floats up only as the water rises: a flooded pit
  becomes escapable exactly when the water reaches within the creature's climb of the rim. That is a lovely
  consequence of exact level water, and it means **flooding a pit to the brim frees its swimmers.**
- For a rat, 0.5 m is already over its head. Card Q2 and Q3 (this strains ruling 26, §4).

### 2.5 Falls (PROVISIONAL)

- Damage is **by metres fallen**, never "drop ÷ the deepest dig" (today `RM_PitTrapMath.FallDropScale` divides by the
  dig cap, MEASURED: raising the cap would make a 2 m fall weaker).
- Keep today's damage up to 2 m. Past 2 m it grows (PROVISIONAL: +50% a metre), capped at 4× at 8 m. Blunt damage
  through the normal pipeline, scaled by body size as he ruled for spikes (*"Don't use instant death, use regular
  damage"*, 2026-09-17). A heavily armoured pawn can survive a 7 m fall; most will not walk away.
- Spikes add their own damage on a fall into their cell (ruled), at any depth where spikes are allowed (card Q5).

### 2.6 What makes a pit a real cell

A pocket holds a given creature when **all** of these hold:
1. no chain of steps it can climb reaches the surface (its climb band, ruled 2026-10-12);
2. the pocket is at least as wide as the creature (his width rule), within card Q6's reach limit;
3. every exit is a controlled one: a ladder (prison door), a sluice or a grate door. **A ramp to the surface breaks it,
   for everyone, both ways** (ruled: ramps are structural);
4. with a prisoner bed, it is a prison room (his, 2026-09-17).

**Deeper is not a stronger prison.** Holding is yes or no. Deeper adds three things only: it holds bigger creatures, a
prison break needs more ladders, and a push in hurts more. No recruitment bonus for depth, no security rating. The
softening is temperature on an open pit (ruled), the same at 2.5 m and 20 m; no depth multiplier.

### 2.7 AI, animals, mood and needs

- **Raiders and animals** path only by steps they can climb (masks). They never walk into a hole; they fall in only by
  force. Wild animals never graze a drained lake they cannot climb back out of. Fleeing pawns pick exits they can
  climb.
- **Sapper and breach raids** have no terrain to breach; card Q7 decides whether they bring ladders.
- **Mood:** no new thought for depth. The ruled "Exposed Prisoner" thought (copying vanilla's beggar-rejection
  structure) covers cruelty. Our own colonists stranded get the alert (Q12), not a mood.
- **Light, roof, temperature:** an open pit is outdoors at every depth: lit by the sun, no free roof, coupled hard to
  outdoor temperature (ruled). A roof over a pit uses vanilla's rules. Shade at low sun angles ties into his "one kind
  of heat" ruling and is deferred to its own design.

## 3. Plants and terrain on dug and drained ground (a design, not a build)

Today every dug and lakebed terrain has fertility 0 (MEASURED, `FlowWorks_Terrain.xml`), so nothing ever grows there.

**Rule: what grows depends on what the ground is made of, and water is what makes good ground.**

| ground | how it arises | fertility (PROVISIONAL) | what grows |
|---|---|---|---|
| **silt** | a fresh-water pond or canal floor left dry: mud for `pondMudDays` (2 days, built), then silt | **1.0**, rich soil | the biome's wild plants come back at their own pace; sow anything |
| **salt crust** | a salt-water floor left dry | 0 | nothing (a real desert playa) |
| **tar, oil, slime floors** | those liquids' floors left dry | 0 (tar may already turn to glass at its edge, built) | nothing |
| **dug floor** | a dry dig | the cell's original fertility × 0.5 for each metre dug (0.5 m: 0.7×; 1 m: 0.5×; 2 m: 0.25×; 4 m: about 0) | the same plants as the ground around, thinner and slower, then none |
| **rock** | dug into rock | 0 | nothing |

- **Speed is the biome's own.** Vanilla spreads wild plants onto cells with fertility above zero at the biome's rate
  (INFERRED: the wild plant spawner reads fertility and biome commonality). On a desert world that is slow, which is
  right. **No timer of ours.** Expect a drained fresh pond to show sparse grass within a few weeks and brush within a
  season (INFERRED, biome-dependent).
- **Water back kills them.** Refilling turns the cell back to water (fertility 0); vanilla removes plants that fail
  their new terrain (MEASURED in the natural-bodies design, G4). A pond that refills drowns its fields; a player who
  wants fields keeps a dam shut.
- **Irrigation already helps.** A field beside a filled canal counts as watered (FlowWorks mechanism), so terraces of
  silt beside their canals are the best farmland on the map.
- **No dig-for-soil exploit.** Digging never makes ground better; only fresh water leaves silt, and silt costs a pond.
  This keeps the 2026-09-16 design note's *"Reclaimed lakebed is the best farmland there is"* true without making
  shovels into fertiliser. (GPT proposed 0.7 for lake sediment and a 10-day colonisation delay; we prefer vanilla's
  own pace and the rich-soil value the design already named. His call: card Q9.)
- **Not in this design:** crops standing in water (paddies), wet-tolerant pit plants, moss in shade. Each is a new
  mechanic.

## 4. His rulings and bars: confirm, strain, contradict

| ruling or bar (date) | verdict | why |
|---|---|---|
| *"it should be relative height ... so that gradual slopes never trap anyone"*; ramps 1.5 m, ladders any depth (2026-10-12, Q1-Q3) | **confirms** | His new sentence restates it. Built offline; deeper digging rides on it. |
| D5 *"the deepest pit stays 2 m"* (by card, 2026-10-17 morning) | **reversed** | He reopened it the same day and ruled Q1: 8 m by default, a setting from 2 to 20 m. |
| D2 lake floors 20 m, to 125 m; *"very large lakes and oceans can absolutely go 50m"* (2026-10-17) | **confirms** | Drained lakes are already deep; the dig cap is a separate number. |
| Exactly level water; a very-shallow look under 25 cm (by card, 2026-10-17) | **confirms** | Continuous water frees the dig step from the water step. |
| Ruling 19, *"Four depths: shallow 0.5 m, mid 1 m, deep 1.5 m, SUPERDEEP 2 m"* (2026-09-16) | **strains** | It is about digging. A deeper cap replaces it. |
| *"All depths must be visually legible and differentiable graphically. The pawn should visibly rise up and lower down as they move over the depths."* (2026-09-17) | **strains** | 16 depths cannot each have a picture and a pawn height. Proposal §2.3: per-edge wall looks, capped sink, readout for absolute depth. |
| North-star bars `pit_depth_ladder_legible` ("depth one, two, three and four") and `pawn_height_ladder_legible` ("each of the four depths ... at every deeper step") | **strains** | Both name four depths. Restate as "every step between neighbours of 0.5, 1, 1.5, 2 and over 2 m is distinguishable" and "a pawn sits lower at every deeper step down to the lip, and reads as below the lip beyond it". Hash-bound: his to re-validate (the section reads DRAFT today). |
| *"walls are higher than their head by 20%"* (2026-09-17; a visual rule only, by card 2026-10-17) | **confirms** | Any pocket a person cannot climb satisfies it. |
| Spikes *"Only in the deepest (D=4) pits"* (by card, 2026-10-02) | **strains** | "Deepest" would move with the cap. Card Q5: any cell 2 m or deeper. |
| *"The pit has to be as wide as the creature to hold it. Otherwise it gets out."* (2026-10-02) | **strains** | Fine at 2 m; silly at 20 m. Card Q6. |
| Capture and convert *"down"* from the lip, warden adjacent (2026-09-17) | **confirms**, with one line added | Card Q11: hands-on care needs floor access. |
| Temperature softening: *"brutal high-temp sun should raise the temperature in the pit quickly"* (2026-09-17) | **confirms** | No depth multiplier proposed. |
| Spikes *"isn't instantly lethal ... Don't use instant death, use regular damage"* (2026-09-17) | **confirms** | Extended in spirit to falls (§2.5). |
| LAW 1 *"We dig down. We never build up."* (design law, 2026-09-16) | **confirms** | Deeper is still down. A dam is ground left undug plus a sluice. |
| LAW 2 *"Depth affects MOVEMENT and LIQUID. It never affects sight or shooting."* (design law, 2026-09-16; **replaced 2026-10-18**: depth now also gives cover, `flowworks_mod_definition.md`) | **strains (again)** | Ruling 23 is its first exception, and keyed to absolute depth it misfires in basins. Card Q8 narrows it to cliff edges. |
| Ruling 26, *"a full 1.5 m canal is a tax, never a barrier ... a water moat alone stops nobody"* (2026-09-16) | **strains** | Water over a person's head in a 4 m canal is either swimmable or a barrier. Card Q2. |
| Pond shore 1 m (shallow) or 2 m (deep) (2026-10-12) | **confirms, with a note** | Drained lakes never trap people. Small creatures cannot climb the 1 m shore, so a drained lake fences them out (§1.1 D). |
| No evaporation: *"only people and plants use water up"* (by card, 2026-10-16) | **strains the storage value** | With nothing lost to the sky, deep stores beat wide stores only on footprint and look. Not a contradiction; a reason the reserve's appeal is mostly visual and spatial. |
| No ground markers for traps: *"Let's try it without such indicators at first."* (2026-10-12 Q4) | **confirms** | The Q12 alert is about our own colonists, not the ground. |
| *"Ladders should be able to be raised and lowered ... No need to have the colonists automatically move them"* (2026-10-06) | **confirms** | Unchanged at any depth. |
| Defence first, then irrigation, then industry, then terraforming (2026-09-16) | **confirms** | Tiers 1-2 feed defence and irrigation directly; drained lakes feed terraforming. |
| Art is delegated to a judge agent (owner, 2026-10-22, `delegation_policy.md`) | **applies** | The five wall looks, the floor shade and silt art pass the art judge, then reach him in the curated review before shipping. |

## 5. Rules that were quietly absolute (fix whatever tier ships)

1. **Drowning** keyed to "any liquid at 2 m" → water against height (§2.4).
2. **Fall damage** divided by the dig cap → metres fallen (§2.5).
3. **Spikes** on "the deepest" cells → a fixed minimum depth (Q5).
4. **Shooting from a pit** keyed to "2 m or deeper" → across a cliff edge (Q8).
5. **Rooms**: a pit room is "dug 2 m and a person-band pocket" today (MEASURED in helper A's brief and the pocket item).
   Keep the person-band pocket; drop the 2 m clause, so a sheer 1.5 m pocket is a prison room too (his own words on
   2026-10-12 imply it: *"a 3-deep trench can trap a normal person"*).

## 6. Decisions for the owner (question-card wording; plain language)

**Q1. How deep may colonists dig?**
- (a) Keep 2 m. Nothing new to build; thrumbos and elephants can never be held.
- (b) 3 m. Every walking creature can be held. Small change; no square like 4/7.
- (c) **8 m. Your 4/7 square fits; real reservoirs; two-stage prisons. Lakes keep their own deeper floors.**
  *Recommended: it covers both of your main uses, and past about 3 m depth adds scale, not new rules.* Digging deeper
  already costs more work per half-metre, so 7 m takes about 5½ days a square.
- (d) As deep as lakes (20 m). Same rules as (c), much more art and testing at scale, and 44 work-days a square.

**Q2. Water deeper than a creature is tall (over a person's head):**
- (a) **It must swim. A creature that cannot swim will not walk in, so a deep, full canal stops it.** *Recommended:
  it matches how water looks, and it gives deep canals a reason to exist.* This changes your 2026-09-16 ruling that a
  water moat alone stops nobody.
- (b) Keep it as now: water slows, it never stops anyone.

**Q3. When does water drown someone in a pit?**
- (a) **When it covers their head (for someone lying down, much sooner).** *Recommended: a puddle should not drown
  anyone.* Bonus: filling a pit to near the rim lets swimmers float out.
- (b) Keep today's rule: any liquid in a deep pit drowns a non-swimmer.

**Q4. Falls:**
- (a) **Damage grows with the metres fallen, never instant death, with a ceiling.** *Recommended.*
- (b) One fall size for every depth.

**Q5. Where may spikes go?**
- (a) **Any cell at least 2 m deep.** *Recommended: spikes stay a pit thing and do not move if the dig limit changes.*
- (b) Only the deepest cells the dig limit allows.

**Q6. A big creature in a slot narrower than itself:**
- (a) It braces and climbs out, at any depth (your 2026-10-02 rule, as written).
- (b) **It braces out only from a slot up to about twice what it could climb; deeper than that, it stays down.**
  *Recommended: a thrumbo climbing out of a 20 m crack reads as a bug.*

**Q7. Raiders facing a trench they cannot cross:**
- (a) **Organised raiders bring scaling ladders (they can be shot down).** *Recommended: keeps trenches strong but
  not perfect.*
- (b) A closed trench is a perfect wall. Defence is your first goal; this makes it absolute.
- (c) They give up and leave.

**Q8. "From a pit you can only shoot your neighbours":**
- (a) **Applies only when a cliff edge is between the shooters.** *Recommended: two people on the floor of a big basin
  can fight normally.*
- (b) Keep it for anyone 2 m down.

**Q9. Plants on dug and drained ground:**
- (a) **A dried fresh-water floor becomes rich silt; dug floors get poorer with each metre; wild plants come back at
  the biome's own pace; salt and oil floors stay barren.** *Recommended.*
- (b) Keep dug and drained ground barren.

**Q10. Digging cost by depth:** today each half-metre costs more than the last (7 m ≈ 5½ work-days a square).
- (a) **Keep it.** *Recommended: deep pits feel like projects.*
- (b) Make it cheaper below 2 m.

**Q11. Who must go down?**
- (a) **Capture, convert and feeding from the lip at any depth (as you ruled). Tending wounds, rescue, stripping and
  hauling need a lowered ladder.** *Recommended.*
- (b) Everything from the lip.

**Q12. Your own colonist stuck in a pit:**
- (a) **An alert in the corner when one of yours cannot reach food or a bed because of a pit.** *Recommended: it is
  not a marker on the ground, which you asked to leave out.*
- (b) No alert.

**Deferred (each would be a new rule, so each is a later card):** shade from low sun in deep pits; darkness; cooler
air down a shaft; gas pooling; cave-ins and wall collapse; groundwater seeping into deep holes; crops standing in
water; dug fishing ponds beyond what the engine already allows; digging below a lake's natural floor.

**Order of work this implies** (play lens; costs are helper A's): (1) the climb rules' live proof, pathing masks and
ramps; (2) the four absolute rules of §5; (3) the deeper cap with the five wall looks and the readout; (4) plants.

## 7. The outside read: what we took

| GPT point | disposition |
|---|---|
| 8 m first cap; 0.5 m step; 2.5 m is the last holding threshold | **taken** (independently reached the same breaks) |
| 152,000 L for the square | **taken** (same arithmetic) |
| Scaling ladders for organised raids, 10 s + 1 s/m | **taken** as card Q7's recommended option |
| Hands-on services need floor access | **taken** as Q11, but capture, convert and feeding stay from the lip (his ruling) |
| Width bracing must not waive every cliff | **taken** as Q6 |
| Fall damage by metres, not ÷ cap | **taken**, and confirmed against `FallDropScale` |
| Shooting restriction breaks basins | **taken** as Q8 |
| Drowning by water against height; wade bands 0.3 H / 0.6 H | **taken**, with a third wade band to 0.9 H so a person still wades chest-deep water as vanilla allows |
| Lake sediment 0.7, a 10-day delay before plants | **not taken**: we keep the existing design's rich-soil value and vanilla's own pace; salt and oil floors added |
| Forbid prison designation without a service route, or accept starvation oubliettes | **not taken**: his capture-down and lip feeding already give every pit a service route |
| No depth multipliers for temperature, gas, fire | **taken** |
