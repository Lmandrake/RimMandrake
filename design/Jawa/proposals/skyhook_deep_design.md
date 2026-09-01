<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->

# The Skyhook — an Imperial tether on a world that never turns

> *"What elements could be put into the skyhooks to make them feel truly
> immersive and exotic?"* — owner's spark, 2026-08-31

Source lore: `worldbuilding/orbital_towers_and_the_sky_ladder.md` (owner,
2026-08-13, content since ABSORBED into `reconciled_lore/01_campaign.md` +
`04_factions.md` — Empire reach is orbital-first, the pursuit clock lives
there). That doc's own comparison table held the skyhook back on purpose:
*"take the towers now, and hold the skyhook as the one set-piece... one of
those is worth more than three more dungeons"* (`tile_augmentation_catalogue.md`
§7.4, few pools, deep). This is that set-piece, designed to the depth its own
restraint earned it.

**Grounding fact that makes it exotic for free:** Ash'karr is tidally locked
(the sun never moves in the sky — canon.yml, `01_campaign.md`). On a normal
world a skyhook's ground anchor sweeps under a moving sky; here it doesn't
need to sweep at all, and neither does its shadow. **The cable's shadow is not
a line that crosses the map once a day. It is a place.** Every other feature
below follows from taking that one fact seriously.

⛔ **House-rule compliance, stated once:** nothing below generates world tiles
at runtime. The anchor site, the debris field The Cut leaves behind, and every
named location are **hand-authored, fixed content** on Ash'karr's frozen map —
activated by scripted quest state, never rolled or placed programmatically.
"There is no worldgen feature, in any version" (CLAUDE.md) is respected
throughout; where a section below reads like generation, it is a pre-built
alternate state of an already-existing tile, swapped in once.

## 1. The anchor site as a visitable map

The tether is not a backdrop sprite. It is a **vertical presence rendered on a
flat map** — RimWorld has no Z-axis, so the cable is represented the way the
game already represents things bigger than a tile: a linear cluster of
`Building` pieces (base collar, tension towers, the line itself as a tall
thin blocking structure running off the map's north edge) plus a permanent
**light/sound signature** that does the actual work of making it feel
40,000 km tall.

- **The eternal shadow line.** Because the sun never moves, the cable casts
  one fixed shadow, forever, at the same map cells. That shadow band is
  **cooler, some degrees darker, and cheaper to build in** (a standing terrain
  overlay, not a mechanic) — and it is *inhabited*: the anchor-town's climber
  yards and customs sheds cluster inside it on purpose, the one strip of shade
  on a sun-fixed world that didn't cost anyone a mountain. Mechanically: a
  static `TerrainAffordance`/glow-curve override painted once at map-build
  time on the pre-authored tile, zero runtime cost.
- **Cargo climber arrivals as scheduled thunder.** Ascending/descending
  cargo pods are not random incidents — they run a **published schedule**
  (posted, in-fiction, on the customs board), and their arrival is a sensory
  event before it's a gameplay one: a deep bass tremor through the ground two
  minutes out, then the pod itself screaming down the last kilometer on
  brakes, throwing sand. `GameConditionDef`-adjacent: a lightweight scheduled
  `WorldComponent` timer, not a condition (it's punctual, not sustained), that
  fires a sound cue + camera-shake-equivalent (screen-shake is fine per
  vanilla precedent) and spawns the cargo `Thing` stack at a fixed cell.
- **Static discharge weather.** A tether 40,000 km long dragging through a
  planet's ionosphere is, physically, a standing lightning-rod. Author a new
  `WeatherDef`, **Tether Static**, that occurs *only* within a fixed radius of
  the anchor: crawling blue arcs up the cable at intervals, a real (rare,
  telegraphed) chance to strike an exposed metal structure or pawn near the
  base — RimWorld already has the lightning-strike primitive from vanilla
  weather; this reskins and geofences it.
- **The deep hum.** A permanent ambient sound layer, always audible within
  the anchor map, that pitches up almost imperceptibly during a climber
  arrival and audibly *changes* — a wrongness, not a warning — in the hours
  before The Cut's tension-failure stage (§5). Players who've spent time here
  learn to hear the mode change before the letter arrives, same diegetic
  grammar as the Ninefold's F9 signature tells.

## 2. What rides the tether

**Scheduled cargo drops, interceptable per the ownership fabric.** Every pod
descending the line carries goods with a real **claim** the moment it's
manifested — Imperial requisition stock, consigned to a named garrison, at
claim strength ~1.0 (`ownership_settlement_spec.md` §2–3: claims are a
decaying vector by recognizability). This is the hook that makes stealing
from the sky *mean* something instead of being a free loot pinata:

- **Intercept the pod in flight (map-side).** A descending pod that takes
  fire or sabotage mid-drop scatters its cargo across the anchor map in a
  **falling-cargo scatter event** — crates landing hot, some breached, some
  intact, spread over a real footprint rather than neatly stacked, with a
  short window before Imperial customs response arrives to secure the site.
  This reuses the existing scatter-on-destruction pattern RimWorld already
  has for crashed ships/pods; the new part is that the scattered goods carry
  the pod's *manifest claim* forward, unbroken by the fall — hot Imperial
  stock is still hot Imperial stock lying in the sand.
- **Steal it at rest (customs-side).** Pods that land clean sit in a customs
  yard under real security (per `ownership_settlement_spec.md`'s per-faction
  security profile — Empire reads "high"), so lifting cargo here is a proper
  heist: witnesses, propagation, faction-record consequence, not a raid.
- **Recognizability makes the choice interesting.** Bulk requisition steel
  decays to "just steel" in days: safe, low-value, no heat. A **named**
  shipment (a numbered Imperial part, a court gift, a droid crate with a
  serial) never fully decays — high value, and it *travels* with a live
  claim wherever the clan takes it, exactly the fence-risk the property spec
  already models for battle loot.

## 3. The vertical society

The people who work the tether are not garrison flavor — they're a **caste
the Empire depends on and half-resents**, riveted directly into the district
grammar `ownership_settlement_spec.md` already specs (a Lua district library
composed per settlement, security props placed per profile). Anchor-town gets
its own district set, distinct from any other Imperial settlement on Ash'karr:

- **Climber yards** — the working core: cable-tension winches, pod cradles,
  a rigger crew (contracted labor, often non-Imperial — Homestead or
  Deepwater hands who took Imperial pay because the alternative is a
  vaporator) whose culture is built entirely around **trusting a fall that
  never happens** — riggers who go up the line on tethers of their own for
  maintenance, a job vanilla RimWorld has no analog for and which reads as
  genuinely alien the first time the player sees a pawn-scale figure climb
  *up*, off the map's visible ceiling, and not come back down for hours.
- **Tension-monitoring shrines** — not Imperial architecture: a folk
  practice the riggers built themselves, small shrines at the base of every
  tension tower where a rigger leaves a token before a climb (a bolt, a
  coin, a name written and burned) — official Imperial doctrine tolerates it
  because morale among riggers who don't have a ritual is worse. This is a
  direct echo of F1's folk-depth logic from the Ninefold review, deliberately
  placed in *Imperial* space to make the point that the Jawa aren't the only
  people improvising faith against a machine that could kill them.
- **Imperial customs** — the actual garrison presence, thin and procedural
  (per `orbital_towers_and_the_sky_ladder.md`'s "not hateful, procedural"
  Empire framing): manifest checks, a bored quota of searches, ion
  emplacements (`04_factions.md`: "ion emplacements are Imperial anti-ship
  tech") ringing the collar as the anchor's actual air-defense, not
  decoration.
- **The caste line matters mechanically.** Riggers are recruitable/
  bribeable in a way stormtroopers aren't — they have grievances (hazard pay,
  the fall that hasn't happened *yet*), which is the social-fabric verb
  family `ownership_settlement_spec.md` already specs (rumors, bribes, hired
  placeless) landed on a specific, sympathetic population instead of a
  generic settlement crowd.

## 4. THE CUT — the campaign set-piece

**Stage 1 — the choice of method.** Sabotage (quiet, deniable, slow — rig a
tension failure over several in-game days, riggers may notice, customs may
not) versus assault (loud, fast, unmistakably the clan's doing, and the only
route if the Hutt commission wants it done *before* a deadline). Both routes
are quest-scripted (`QuestScriptDef`, per `rimworld-quests`), not a single
button — sabotage needs the rigger relationships from §3 to have somewhere to
land; assault needs the ion emplacements suppressed first.

**Stage 2 — the physics of the fall, played straight.** Ash'karr's tidal lock
cuts both ways here: the planet barely spins relative to the stars (rotation
period ≈ orbital year), which means the counterweight riding out past
geostationary sits **absurdly far out** compared to a normally-spinning
world's elevator — the Empire's own engineers are on record (flavor text,
customs-board grumbling) hating this world for exactly that reason: the cable
is longer, the tension math is worse, and it was never supposed to be built
here at all, only that the Hutts' shipping lanes made it worth the expense.
When it's cut near the anchor, a barely-rotating world doesn't get the
dramatic globe-girdling whip a fast-spinning one would — **the cable falls
close to straight down**, but 40,000 km of straight-down is still a
catastrophe: the lower atmosphere-grazing kilometers shred and burn on entry
long before they land, and what *does* land is a **debris corridor**, not a
point.

- **On the local (anchor) map:** the debris corridor is authored as a
  post-Cut alternate map state for the anchor tile itself — collapsed
  tension towers, a kilometer-scale trench of buried cable segment cutting
  straight through what used to be the customs yard, live power conduits
  still discharging for days (Tether Static weather, now *un*-geofenced and
  dangerous everywhere nearby). This is the same "hand-authored alternate
  state, swapped in once" pattern as the shadow-line overlay in §1 — no
  runtime generation.
- **On the frozen world map:** a **pre-authored chain of debris-corridor
  tiles**, already reserved in Ash'karr's map alongside the anchor tile
  exactly the way its other authored features are (roads, mines, the three
  seas), sits inert and unreachable until The Cut fires, at which point a
  scripted world-state flip reveals them as a new salvage-rich, hazardous
  region — cable segment as a resource (absurd quantities of high-grade
  cable — genuinely useful, genuinely a landmark), buried munitions from the
  collar's ion batteries, and a permanent scar on the world map every player
  who finishes this arc will have in the same place, because the world is
  frozen and this is authored, not rolled.

**Stage 3 — the moral weight.** The riggers from §3 were on shift. Sabotage
gives the clan a window to warn them (at a cost — warning risks the whole
plan); assault doesn't. Either way, the Hutts profit and the Jawa did the
dying-adjacent work, restating `orbital_towers_and_the_sky_ladder.md`'s own
thesis: *"the small party everyone uses... the player should be able to feel
that and take the job anyway, because the pay is real."*

**Stage 4 — Imperial response tiers.** Not a goodwill-tick, per the source
doc's original complaint about "Imperial Heat" being a fictional gauge — the
response is **structural and regional**, reusing the backbone-tower shape
that doc already ruled: Imperial reach in the region drops (fewer patrols,
slower response elsewhere), *and* a dedicated punitive tier stands up
specifically for this act — a named Imperial task force that hunts the tower/
tether backbone arc as a set, cross-referencing whichever backbone site falls
next. The ending is announced, not implied: a letter, a visible regional
raid-pressure change, the Hutts paying out and going quiet — the same "a
finite arc that ends without ceremony reads as content running out" law the
source doc already laid down for the towers.

## 5. Smaller exotica

- **Cable-jumper daredevils.** A rare wandering NPC or recruitable specialist
  who base-jumps the tether for sport/smuggling — a living demonstration that
  the "impossible" climb is survivable with the right gear, and a quest hook
  (retrieve their gear, recruit them, or watch them die spectacularly and
  become the reason a shrine gets built).
- **Harmonic resonance events.** A tether under enough sustained stress
  (weather, a failed maintenance cycle, deliberate tampering) hits a
  resonant frequency and rings — a `GameConditionDef`-scale short event (not
  sustained, an incident) that shatters glass and fine ceramics across the
  *entire* anchor map simultaneously, a genuinely strange, low-cost, highly
  memorable "the whole world just went 'BONG'" beat.
- **A cult that reads the cable's vibrations as prophecy.** Riggers who spend
  years with a hand on the tension line start hearing patterns in the hum
  (§1's deep-hum layer, again) — an unauthorized, tolerated-because-morale
  folk sect distinct from both the Ninefold and Imperial doctrine, offering
  quest-giving "prophecy" that's mechanically just an early-warning system
  for scheduled climbers and weather dressed as divination. A clean seam if
  the owner ever wants a non-Jawa faith to contrast against the Ninefold's
  depth without borrowing its gods.

## Build ladder

**v1 slice** — the anchor map as a static, visitable site: the shadow-line
overlay, the deep hum, one scheduled cargo-climber arrival type, and the
falling-cargo scatter event on interception. Ships with the Space Tower
dungeon content already installed (`HaiLuan.SpaceTower`, load 108) reskinned
as this specific tether rather than a generic derelict — the cheapest
possible route to "a place the player can go stand under."

**v2** — the vertical society (riggers, shrines, customs, the recruitable/
bribeable caste line), Tether Static weather, and THE CUT's Stage 1–3
(sabotage vs. assault, the moral-weight framing) as a full `QuestScriptDef`
arc riding the already-ruled backbone/side-tower shape.

**Dream** — Stage 4 in full: the pre-authored debris-corridor world-map
tiles, the named punitive Imperial task force, and the harmonic-resonance/
cult exotica as standing, always-on texture rather than one-off flavor —
the tether as a second campaign clock running alongside the Ninefold's own,
the two systems never touching mechanically but both teaching the player to
read a world that talks back.
