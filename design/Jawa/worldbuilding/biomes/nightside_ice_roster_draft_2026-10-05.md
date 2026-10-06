# Nightside Ice: the strange life (roster draft, 2026-10-05)

Item: `NIGHTSIDE_ICE_NEW_LIFE_1`. The owner chose by question card (a click, recorded as a decision
taken by card, not a quote): **"Design the strange life."** This is BENCH's draft of the designed
organisms for him to judge on a later sheet. **Every row is DRAFT.** Nothing here is ruled until he
rules it at the sitting.

Authority: `design/Jawa/worldbuilding/biomes/nightside_ice.md` (frozen; this adds detail and changes
no ruling). Read with it: §4 (catalysts on seams, sessile and enormous, the one-move animal, thermal
sensing only, clonal reproduction, nothing warm), §4c (the tunneler slate and the cast closed
2026-09-24), §5/§6 (always and never true), "Roster consequences", and
`nightsideice_bedazzle_review_2026-10-01.md` §8 (turn-1 rulings).

## 0. What already existed (searched first, reused)

The project had already done most of the naming and the first art. This draft builds on it and
re-proposes nothing the owner passed.

| thing | where it already is | state |
|---|---|---|
| **shivven** (tunnelers) | `src/RimMandrake/NightsideIce/Defs/Fauna/RM_Shivven.xml`, `Source/RM_Shivven.cs`, textures installed | **BUILT** (`NIGHTSIDEICE_SHIVVEN_BUILD_1`, closed) |
| **heat dial** | `Source/RM_HeatDial.cs` (`RM_HeatDial.For(map).Dial`, 0..1, heaters/fires/power/rooms) | **BUILT** |
| **breach crack** | `Defs/ThingDefs_Buildings/RM_BreachCrack.xml`, `Source/RM_BreachCracks.cs` | **BUILT** |
| **sohl, frissim, dhorrumak, wyrmlet** | names ruled at `NIGHTSIDE_ICE_DESIGN_SITTING_1` (sheet §4c, "the cast, closed") | no def; **art done** 2026-10-01 |
| **hessarund** (living ridge) | named and ruled "only a landform, mineable, yields catalyst crust, no behaviour" (bedazzle §8 Q2) | no def; **art done** |
| **hoarfrost forms** (4) | ruled terrain features, never plants (§4c.7) | no def; **art done** (`RM_Hoarfrost_{BladeGrowth,CrystalGarden,DepthHoarColumn,FrostFlower}`) |
| **shivven tell** graphic | `Textures/RM_NightsideIce/Effects/RM_ShivvenTell.png` | **installed** |
| **kesshet** (hull crust) | bedazzle §3 | 🔴 **PASSED by the owner** (*"I don't like any of these. We should likely just pass this."*). Not re-pitched here. |

Existing art, all in the artpipe state dir `D:\Luke\dev\_artpipe\done\` (filed 2026-10-01 under
`NIGHTSIDEICE_BEDAZZLE_SITTING_1`): `RM_Sohl_Dormant`, `RM_Sohl_{east,north,south}`,
`RM_Shivven_*`, `RM_ShivvenTell`, `RM_Frissim_*`, `RM_Wyrmlet_*`, `RM_Dhorrumak_*`,
`RM_Hessarund`, the four `RM_Hoarfrost_*`. **No review sheet has ruled on any of them** (no
`decisions.json` names them). So no new art is queued for the ruled cast; it goes to the sheet as
it stands. New art is queued only for the four new organisms in §2.

**Names.** The ruled nightside accent (shivven, frissim, sohl, dhorrumak, hessarund): hushed, long
vowels, doubled consonants, endings on *-n/-m/-l/-k/-d*. The smooth *-ith/-tha/-ia* sound is the
Abyss's black many-eyed family (owner, 2026-10-05) and is avoided. Each new name was grepped across
`design/` and `src/` and returned 0 hits (`vosh` was dropped: it is a founder's surname).

---

## 1. The ruled cast, carried forward

These six are named and admitted already. What they lacked was a def-ready design: description,
scale, play, and build cost. **DRAFT** applies to everything below the name.

### 1.1 sohl (`RM_Sohl`): the one-move animal: DRAFT

- **Kind:** a building-like dormant body (`RM_Sohl_Dormant`, mineable-looking, `Building` with a
  comp) that becomes a pawn for exactly one move, then a permanent inert body.
- **Scale:** 4×3 cells dormant; the move covers 8–20 cells in a few seconds; the spent body lies
  4×3 where it stops, forever.
- **In play:** placed by map generation as 0–2 per map, on open ice, never on a floor. It reads
  the heat dial. When a strong heat source (a fire, a heater, a warm pawn lying downed) stays within
  its reach for long enough, it **commits**: one sudden lunge onto the source's cell, crushing what
  is there (big blunt damage, no second strike). Then it is spent: a 4×3 body that never moves
  again, can be cut apart for a large yield of catalyst crust (shared resource with the hessarund)
  and dense hide-plate. Insulate, and it never moves. There is no fleeing it and no fighting it
  twice. A sohl that commits at a seam rather than a pawn leaves a fragment behind (the clonal rule,
  §4: it moved to reproduce); see the oolm, §2.2.
- **Reads in-game:** dormant, a low too-even mound of dirty ice with faint plate seams under the
  frost; the hover label says only "ice mound" until a pawn with Animals ≥ 8 has looked at it (then
  "sohl, dormant"). Spent, limbs splayed out of the mound.
- **Description:** *"What you took for a mound of old ice has been eating the frost under it since
  before your people had writing. It has been saving for two hundred years to move exactly once:
  to a new seam, to a new place to be, or onto something warm. When it moves it is sudden and total,
  and afterwards it lies where it stopped, still alive, never to move again."*
- **Art:** done (`RM_Sohl_Dormant`, `RM_Sohl_*`). ⚠️ The facing set shows a pawn mid-lunge; a
  sessile spent body may need only one top-down graphic. Sheet question.
- **Build cost:** **C#.** A dormant-building comp with a heat-trigger (reads `RM_HeatDial` and the
  nearest source), the one-move jump (a short forced move or a spawn-pawn-and-path), and the conversion
  to a spent building. Medium. Reuses `RM_HeatDial`; the "dormancy comps" noted in the roster
  `new_defs` are prior art.

### 1.2 shivven (`RM_Shivven`): the tunnelers: BUILT, carried for the sheet

- **Kind:** pawn that travels inside the ice (`RM_CompSandSwim` retune), with the rumble-tell.
- **Scale:** dog-sized pawn; tell 1 cell, travelling; breach cracks at the base edge.
- **In play:** built: heat-seeking, rumble-tell, surfaces at breach cracks only in open ice (hull
  rule), escalated by the heat dial. Still owed from §4c: the larder (dragging downed pawns under),
  and the clonal warren (one warren per pan margin).
- **Description:** as shipped in `RM_Shivven.xml`; no change proposed.
- ⚠️ **Sheet question, not a change:** the shipped art and description are pink-grey, hairless,
  wrinkled, with ivory incisors: a naked mole-rat. §6 bars *"anything instantly nameable"* and
  *"ordinary animal silhouettes"*, and pink reads warm. The §4 ruling calls them a mole-rat *analog*,
  so the owner may be content; the sheet should ask.
- **Build cost:** done; the larder is `NIGHTSIDEICE_BEDAZZLE_SITTING_1` backlog row 5.

### 1.3 frissim (`RM_Frissim`): the icy insects of the inclusions: DRAFT

- **Kind:** tiny pawn swarm, dormant inside the ice; appears only as an incident-borne release.
- **Scale:** bs 0.05 each; a release is a 3×3 to 5×5 cell cloud of 10–30 on the ground, never in
  the air.
- **In play:** they live in the bubbles of dirty ice and never appear on their own. A thaw pulse, a
  slab-fall, a calving delivery or an insect-fall releases a patch. Harmless one at a time (a nip,
  no disease); they crawl toward warmth, and die off as the ice re-freezes (a few hours). Their
  presence draws wyrmlets (§1.4) and stirs the warren. Whether their bodies may be gathered as a
  tiny food item is a sitting question: §7 says the biome is *"not food"*.
- **Reads in-game:** a pale crawling scatter on the ice around a fresh crack; hover "frissim".
- **Description:** *"Insects the size of a fingernail that live inside the ice, in its bubbles and
  its veins of mineral dust, asleep for years at a time. A thaw wakes them. They crawl toward warmth,
  slowly, and when the ice closes again they stop."*
- **Art:** done (`RM_Frissim_*`). ⚠️ The prompt gave them *"folded transparent wing-cases"*. They
  must never fly (§6). Wing-cases that stay folded are fine; the sheet should check they read as
  flightless.
- **Build cost:** **XML + small C#.** The pawn is XML (a vanilla insect body, no flight stat); the
  release is a spawn hook on whatever thaw/calving event lands (backlog row 2), and a die-off when
  the local temperature falls back (a hediff or comp). Small.

### 1.4 wyrmlet (`RM_Wyrmlet`): the apex's young: DRAFT

- **Kind:** pawn; surfaces only where frissim are stirring.
- **Scale:** forearm-long, bs 0.3.
- **In play:** the foreshadow rung (§4c.6): when frissim are released, 1–3 wyrmlets surface beside
  them within an hour, eat them, and go back under. They bite only if cornered. Seeing them is the
  letter-free warning that the map is dhorrumak country. Killable, and their bodies are a rare
  scale-plate yield.
- **Reads in-game:** a pale finned worm on the ice beside a crawling patch; gone again soon.
- **Description:** *"A young ice wyrm, no longer than a forearm, blind and clumsy, with a horned
  drilling snout. It comes up where the ice-insects wake and goes back down when they are gone.
  Wherever these surface, something very much larger made them."*
- **Art:** done (`RM_Wyrmlet_*`).
- **Build cost:** **XML + small C#.** Body, stats and the CompSandSwim-style submerged state reuse
  the shivven's code; the surface trigger is one hook on the frissim release. Small once the frissim
  exist.

### 1.5 dhorrumak (`RM_Dhorrumak`): the apex ice wyrm: DRAFT

- **Kind:** pawn, an incident-borne set-piece; never on the wild roster.
- **Scale:** surfaces through a 5×5 burst; the body occupies 3×3 on the surface, the rest is under.
- **In play:** the top of the ladder (frissim → wyrmlets → nest → dhorrumak). It comes only under
  **sustained** high heat dial (days above a threshold) or when its nest's eggs are taken or broken.
  It breaches at the base's edge in open ice (hull rule), strikes, and goes under again; it does not
  chase across floors. Killing it is a colony-scale fight; driving it off means cooling the base.
  Canon anchor: the ice wyrm (blind snow-driller), routed via the Utinni layer if canon text or name
  is used; `dhorrumak` itself is an invented `RM_` name (Q11a).
- **Reads in-game:** the rumble-tell scaled up, then a 5×5 crater of burst slabs with a vast plated
  length reared out of it.
- **Description:** *"Most of it is always under the ice. What comes up is a ringed, toothed mouth
  and a length of body plated in old blue-black scale, rearing out of a crater of broken slabs. It is
  blind. It came because you were warm for too long."*
- **Art:** done (`RM_Dhorrumak_*`).
- **Build cost:** **C#, large.** A sustained-heat trigger on `RM_HeatDial`, a breach incident
  reusing `RM_BreachCracks`, a big-body submerged pawn. The nest eruption is a separate calving
  set-piece. Backlog row 6.

### 1.6 hessarund (`RM_Hessarund`): the living ridge: DRAFT

- **Kind:** mineable building plates laid in a line (ruled: only a landform, no behaviour).
- **Scale:** a ridge 1–2 cells wide and 20–60 cells long, one per map at most.
- **In play:** placed by map generation along a crevasse line. Mined, each plate yields **catalyst
  crust** (new resource: a stuff-less material for advanced components and a cold-rejection
  research input; never food, never fuel). It has no behaviour, by ruling. The only tell that it is
  alive is in the inspect text and the yield.
- **Reads in-game:** a ridge, faintly too regular, with a darker seam line along its spine; hover
  "ridge (hessarund)".
- **Description:** *"A ridge, by every measure you can take of it. It is also one living thing,
  lying on a seam where two frosts ought to react and cannot, taking a share of the reaction the cold
  forbids. It has been here for longer than anything has been anywhere. Cut into it and the crust
  comes away chalky and rose-tinted, and it does not grow back in your lifetime."*
- **Art:** done (`RM_Hessarund`).
- **Build cost:** **XML + small C#.** The plate is a mineable `ThingDef` with leavings (XML); the
  catalyst crust item is XML. Laying a line needs a small `GenStep` (vanilla scatter does blobs, not
  lines). Small.

---

## 2. New organisms

Four fills, one per wanted category the ruled cast left empty. All `RM_` tier, invented names, one
home (the Nightside Ice). All **DRAFT**.

| wanted category (sheet) | covered by |
|---|---|
| sessile catalytic sheets, crusts and lobes at landform scale | hessarund (ridge) + **saallen** (crust sheet) + **oolm** (lobes) |
| organisms indistinguishable from terrain | sohl, hessarund, saallen, oolm |
| the one-move animal | sohl |
| clonal colonial forms | **oolm** (and the shivven warren) |
| thermal-sensing tunnelers within the ice | shivven, wyrmlet, dhorrumak |
| icy insects of the inclusions | frissim |
| chemical-frost formations ambiguously alive | **neshkoll** (the hoarfrost forms are ruled not alive) |
| corpses and the lost | **the ice-kept dead** |

### 2.1 saallen (`RM_Saallen`): the seam crust: DRAFT

- **Kind:** sessile building-like crust (a flat, walkable-over `Building`, like vanilla's
  `Filth`-height but persistent), in patches.
- **Scale:** patches of 6–30 cells, laid where the ice is thinnest over a seam; 2–5 patches a map.
- **In play:** a catalytic sheet pressed onto a frost interface. Cold, it is inert and walkable.
  **Warmed** (any cell above about −30 °C, i.e. the colony's waste-heat ring, or a thaw pulse), its
  reaction runs away: the crust blisters and darkens over a day, and the ice under it softens. A
  blistered saallen is the **map-readable sign of the breach ring** (§4c hull rule: the colony's
  heat softens the ice around it): breach cracks prefer blistered saallen cells. Scrape it (a
  short work job) to remove that risk and collect a little catalyst crust; scraped ice stays bare.
  The heat dial bites here with a visible map tell, not only an alert.
- **Reads in-game:** cold: a dull grey-white skin a shade off the ice, with fine polygon cracks.
  Warmed: the same patch blistered, rose-grey, pitted. Hover "saallen (cold)" / "saallen
  (blistering)".
- **Description:** *"A skin on the ice, thin as paper and as wide as a field, lying on a seam where
  two frosts meet. It lives on a reaction the cold has stopped. Warm it and the reaction runs: the
  skin blisters, and the ice under it goes soft."*
- **Art brief:** top-down terrain-scale patch, tiling-friendly. Dull grey-white crust on dirty white
  ice, a fine net of polygonal hairline cracks, faint chalk-rose mineral in the cracks; reads as ice
  skin, not lichen. A second state (blistered, pitted, darker rose-grey) is owed after the first is
  ruled. No green, no glow, no plant forms.
- **Build cost:** **XML + small C#.** The patch is an XML building with two graphics; a comp reads
  cell temperature (vanilla) to flip state; one line in `RM_BreachCracks.cs` to weight placement
  toward blistered cells. Small to medium.

### 2.2 oolm (`RM_Oolm`): the clonal lobes: DRAFT

- **Kind:** mineable building lobes (rock-like), clonal colony.
- **Scale:** each lobe 2×2; a colony is 4–15 lobes in a loose cluster along a pan margin, 0–1
  colonies a map.
- **In play:** every lobe on a map is **one individual** (the clonal rule, §4: one lineage per pan
  for a geological age). Mined, a lobe yields **oolm block**, a stony, very low-conductivity material
  (cold as a resource, §7): an excellent insulating stuff for walls, which is what bermed,
  cold-outside buildings (§8) need. The colony notices: each lobe cut makes the rest harder to cut
  (work to mine rises per lobe taken), because it is one body closing up. A colony never regrows in
  a game's span. Link to the sohl: a sohl that commits without a warm target leaves a single oolm
  lobe where it stops: the fragment that reached a new seam.
- **Reads in-game:** a cluster of smooth, rounded grey-white lobes like frozen dough or river-worn
  boulders, all of them the same faint banding, so the cluster looks like one thing broken up.
  Hover "oolm".
- **Description:** *"A cluster of smooth rounded lobes along the edge of the pan, all of them the
  same banded grey. They are one creature, and they have been one creature since the pan formed:
  every lobe a piece of the same body, pressed to the same seam. It does not like being cut. Each
  piece you take, the rest grow harder."*
- **Art brief:** top-down, one 2×2 lobe as a sessile sprite: a smooth, rounded, slightly flattened
  grey-white lobe with fine concentric banding and a dark seam where it presses to the ice; frost in
  the creases. Reads as stone or ice first, alive only on study. No face, no limbs, no eyes, no
  green, no glow, nothing plant-like.
- **Build cost:** **XML + small C#.** The lobe and the oolm block stuff are XML (mineable building,
  `StuffProperties` with low insulation conductance via vanilla stats). The rising work cost needs a
  tiny comp (count lobes left on the map). The sohl fragment is one line in the sohl's C#. Small.

### 2.3 neshkoll (`RM_Neshkoll`): the frost that leans toward heat: DRAFT

- **Kind:** scatter formation (a small walk-over building, short-lived), spawned on the cold
  side of heat.
- **Scale:** single 1×1 growths in fans of 3–12 on open ice, 4–10 cells out from a heat source.
- **In play:** the chemical-frost formation that may or may not be alive. On any map with a heat
  dial above zero, neshkoll grows on open ice near the colony's hottest leaks, and **every growth
  points its plumes at the source that fed it.** It is the one native thing that tells the player
  which of their buildings is the loud one: the same thing the shivven read. Break it and it is gone
  (a little catalyst crust); leave it and it marks the leak until the heat drops, then sublimes in a
  day. Nobody, in game or out, can say whether it is alive; the inspect text says so.
- **Reads in-game:** fans of tall, feathered, comb-like frost plumes, all leaning one way across the
  ice toward a wall. Hover "neshkoll", inspect *"leaning toward: <building>"*.
- **Description:** *"Frost that grows in combs and plumes on the cold side of anything warm, and leans
  toward it. It might be a crystal doing what crystals do in still air. It might be something feeding on
  the edge between your heat and the cold. Either way, it points straight at whatever is warmest."*
- **Art brief:** top-down, one growth: a cluster of tall feathery comb-like frost plumes, all bent
  hard to one side as if leaning into a wind that is not there; translucent white with grey-violet
  shadow in the feathers, chalky mineral at the root. Must read as frost, not a plant: no stems, no
  leaves, no green, no glow. One direction of lean (the game rotates it).
- **Build cost:** **C#, small to medium.** A spawner on `RM_HeatDial`'s measurement pass (it already
  finds the sources) placing a rotatable 1×1 building facing the source, plus a decay timer. The
  graphic is one `Graphic_Single` rotated by `Rot4` or a `Graphic_Multi` built from one image.

### 2.4 the ice-kept dead (`RM_IceKeptDead`): corpses and the lost: DRAFT

- **Kind:** incident-borne and map-generated building: a body held in clear ice, cut out by a work
  job. Not a creature; plain English name on purpose.
- **Scale:** 2×1 (one body) or 3×3 (a party roped together); 1–4 per map from generation, more from
  calving deliveries.
- **In play:** the sheet's real population (§4 second pass). A dark shape under a pane of clearer
  ice: a lost traveller, a Junker crystal expedition member, someone from orbit. Cutting it out (a
  mining-like job, slow) yields the **perfectly preserved corpse with its gear** (`ThingSetMaker`
  of period kit and a chance at a ledger tablet for the ruled Cold Ledger rite, bedazzle §6 R1).
  Warming it is the catch: an exposed or thawing body is a warm signal; the shivven come for it to
  stock the larder. Cut it out cold, or lose it to them.
- **Reads in-game:** a pale rectangular pane of clearer ice set in the dirty white, with a dark
  human-shaped silhouette inside, arms at odd angles. Hover "body in the ice".
- **Description:** *"Someone is in the ice. They lay down here, or fell here, a very long time ago,
  and the ice took them and kept them exactly as they were: clothes, pack, the look on their face.
  Cut them out and you can have whatever they carried. Cut them out warm and something else will want
  them too."*
- **Art brief:** top-down, 2×1: a slab of clearer, slightly blue-grey ice set flush in dirty white
  ice, and inside it, blurred by the ice, the dark silhouette of a person in heavy cold-weather gear
  lying twisted, one arm out. The figure is only a shape through the ice, never sharp, no face
  detail, no blood. No glow, no green.
- **Build cost:** **XML + small C#.** The held body is a mineable XML building; leavings need a
  small C# spawner to make a pawn corpse with gear (vanilla `PawnGenerator` then kill, the ancient-
  casket shape). The shivven hook (warm body → larder target) rides the larder build (backlog row 5).

### Pointer: the hoarfrost forms (not an organism)

Ruled terrain features, never plants, never alive (§4c.7). Art done, four kinds. They are the
plateau's scenery and the neshkoll's foil: hoarfrost stands straight up in still air; neshkoll leans.

---

## 3. Questions for the sitting

1. Admit each of the four new organisms (saallen, oolm, neshkoll, the ice-kept dead)? Each can be
   cut alone.
2. Names: saallen, oolm, neshkoll; alternates offered at the sheet if he dislikes any.
3. Shivven art: content with the pink, hairless mole-rat read, or push it stranger and colder?
4. Frissim: confirm flightless; and may frissim be harvested as food, given §7's *"not food"*?
5. Sohl: is one top-down spent-body graphic wanted beside the lunge facings?
6. Catalyst crust: one shared resource from hessarund, sohl, saallen and neshkoll, or only the
   ridge?

## 4. Build order and cost

| organism | needs | size | rides |
|---|---|---|---|
| hessarund | XML + line GenStep | S | ice forms row (7) |
| oolm | XML + tiny comp | S | new |
| ice-kept dead | XML + corpse spawner | S–M | thaw/calving row (2) |
| saallen | XML + temp comp + breach weighting | S–M | heat-dial follow-on |
| neshkoll | C# spawner on the heat dial | M | heat-dial follow-on |
| frissim | XML + release hook | S | thaw/calving row (2) |
| wyrmlet | XML + reuse shivven code | S | apex ladder row (6) |
| sohl | C# dormant → one move → spent | M | row (4) |
| dhorrumak | C# sustained-heat breach set-piece | L | row (6) |

Order follows the owner's ruled backlog (bedazzle §8): rows 2 → 3 → 4 → 5 → 6 → 7. The new four slot
in after the ruling; none jumps the queue.

Art queued 2026-10-05 for the four new organisms:
`Transient/biome_ffar/nightsideice_newlife_jobs_2026-10-05.json`.
