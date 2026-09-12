# Explosive plant growth — design draft

**Queue item:** `EXPLOSIVE_PLANT_GROWTH_1` · **Status:** DRAFT — nothing here is ruled.
**Sources:** `design/Jawa/worldbuilding/biomes/the_cracked_lands.md` §10b (the mechanic's
birthplace and the owner's verbatim ruling), `infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md`
(the two open questions and engine notes), `infrastructure/state/items/FLOOD_WITNESS_EVENT_1.md`
(the guaranteed showcase). Naming follows `design/NAMING_SCHEME_PLAN.md` tier grammar;
all names below are placeholders (`<RUT_...>`, `<RM_...>`), none coined.

**The ruling this draft serves** (owner, 2026-09-06, world-wide): water-soaked plants
grow VISIBLY — the player watches them get bigger on screen, not animal-motion but
growth — and it should feel intimidating anywhere water soaks a plant. *"'OMG, what's
going to happen?' should be the feeling near any water-soaked plant."* It cannot grow
forever; the top of the curve is a designed moment meant to recur — *"a great moment
again and again."* The jungles should visibly grow.

---

## 1. The shared spine (common to every terminal-moment option)

Whichever terminal moment the owner rules, the run-up is the same, because the run-up
IS the ruling: visible growth plus dread.

1. **Soak.** A plant on soaked ground (flood water, rain pooling, deliberate
   irrigation) enters the surge state. Visibly wet-dark at the base — the player can
   tell a primed plant from a normal one at a glance.
2. **Surge.** The plant grows on screen — smoothly scaling up over minutes of real
   play, not vanilla's invisible tick-crawl. Stages of silhouette change (sprout →
   swollen → looming) so the growth reads even in peripheral vision.
3. **The tell.** Near the top, an unmistakable warning phase: the plant's final
   silhouette (per-option below), a color shift, a sound. The player always gets a
   window to act — harvest it, cut it, run.
4. **The terminal moment.** One of the options in §2. Then the cycle can begin again
   wherever water still soaks the ground — recurrence is a design requirement, not a
   nice-to-have.

The Cracked Lands flood (`FLOOD_WITNESS_EVENT_1`) is the guaranteed full-cycle
showcase: the wall of water, then a canyon floor of surging plants, then the terminal
moment en masse, witnessed from a refuge ledge. Whatever is ruled here must look
magnificent at that scale.

---

## 2. Question 1 — THE TERMINAL MOMENT (owner rules; cards at the end)

Four genuinely different answers. Each is designed to recur, each states what the
player sees, what it drops/spawns/destroys, its danger, per-biome flavor, and its
trade against the others. They are not all-or-one: the owner may rule one world-wide,
or split them per-biome (Option E on the scope card).

### Option A — THE BURST (seed-storm detonation)

- **What the player sees:** the plant swells past its silhouette, visibly straining —
  bulging, trembling — then detonates: a shower of seeds and pulp in a radius, a
  wet green explosion. In a flood-week canyon, hundreds go off like popcorn across
  the floor.
- **Drops / spawns / destroys:** scatters viable seeds onto every soaked tile in
  radius (each starts a new surge — the recurrence engine is the burst itself);
  drops harvestable pulp/pods at the burst site; deals modest damage and a stagger
  to anything adjacent (numbers are tuning, not stated here). Speculation: seeds
  landing on structures/roofs could accumulate as cleanable filth rather than damage.
- **Danger:** HIGH up close, zero at range. Chain-reaction risk: one burst soaking or
  seeding neighbors can ripple a whole grove. A pawn caught mid-field during a mass
  burst is in real trouble.
- **Per-biome flavor:** yes, cheaply — seed/pulp color and burst sound per biome;
  the Cracked Lands bloom-crop is "the pod you cut BEFORE it bursts" (boom-bust
  economy per §10b); jungle bursts feed the jungle, which is why the jungle grows.
- **Trade:** the most intimidating single moment and the cleanest recurrence loop,
  but the least controllable — bursts re-seed where THEY want, and a colony's
  irrigated field bursting is a mess the player did not order. Weaponizes easiest.

### Option B — THE GREAT BLOOM (crown, hold, rot)

- **What the player sees:** the surge ends in a crown — a huge flower or fruiting
  body opening in real time, far out of scale with the plant that bore it. It holds,
  glorious, for a limited window. Then it rots where it stands: color drains,
  the crown slumps, and the rot phase brings its own trouble.
- **Drops / spawns / destroys:** the crown is the harvest — cut it during the window
  for the full prize (the Cracked Lands' flood-week market crop, verbatim §10b's
  boom-bust). Miss the window and the rot drops a lesser salvage and spawns the
  penalty: speculation — spore cloud (toxic buildup zone), or a wave of vermin/
  Spender-fauna drawn to the rot, per-biome. The plant itself dies back to a stump
  that can re-surge on the next soak.
- **Danger:** LOW during bloom, MODERATE after — the danger is the deadline, not the
  plant. Intimidation comes from scale and from knowing what the rot brings.
- **Per-biome flavor:** the strongest per-biome canvas of the four — each biome's
  crown is its signature image (canyon bloom, jungle canopy-flower, Fever Wood's
  fever-bloom), and each biome picks its own rot penalty.
- **Trade:** the most farmable and the most beautiful, but the least intimidating —
  it is a harvest deadline wearing a monster's silhouette. If the owner wants dread
  first, this is the weakest at it; if he wants the economy §10b names, it is the
  strongest.

### Option C — THE DEADFALL (grow tall, then fall)

- **What the player sees:** the plant grows UP — a tower of green climbing in real
  time, visibly leaning further and further as it overreaches. The lean is the tell
  and it is directional: the player can read WHERE it will land. Then it falls, one
  crashing arc, and lies where it fell.
- **Drops / spawns / destroys:** crushes what it lands on — plants, items, walls at
  the impact line, pawns who ignored the lean (damage tuning open). The fallen trunk
  is a windfall: a large one-spot haul of wood/biomass plus a per-biome prize in the
  crown. The trunk itself is terrain-scale cover/obstacle until hauled. The root
  re-surges on the next soak — same spot, new tower.
- **Danger:** HIGH but positional and readable — it kills the inattentive, spares
  anyone watching. Uniquely, it threatens STRUCTURES: build beside soaked ground and
  the flood may drop a tree on your roof. (Rhymes with the Cracked Lands' law:
  never build the bottom.)
- **Per-biome flavor:** moderate — trunk species and crown-prize vary; reads best in
  biomes with trees, weakest where flora is groundcover. Likely needs a groundcover
  variant (a collapsing mat rather than a falling tower) or a per-biome pairing.
- **Trade:** the most physical and most legible danger, and the only option that
  redraws the map (fallen trunks as new cover/obstacles). But it is the worst at
  mass spectacle — a hundred simultaneous falls is chaos to read — and the least
  suited to small groundcover plants, so it cannot be the whole answer alone.

### Option D — THE OVERGROWTH SURGE (the plant does not die — it RUNS)

- **What the player sees:** at the top of the curve the plant stops growing up and
  starts growing OUT — runners visibly racing across every adjacent soaked tile,
  each runner surging in turn. A green wall advancing while you watch. The jungle
  does not just grow; it comes toward you. The surge halts only where the water
  ends — dry ground is the firebreak — then the whole overgrowth mass slumps into
  harvestable matter as the water is spent.
- **Drops / spawns / destroys:** entombs what it overruns — items and structures
  wrapped in overgrowth (disabled/blocked until cut free, not destroyed; destruction
  is a tuning question to rule later). The receding surge leaves a carpet of
  harvestable biomass and re-fertilized soil — the flood's "death, then soil, then
  the bloom" in one mechanic. Speculation: overrun corpses/ruins could yield the
  Jawa salvage-strike beat from §12.
- **Danger:** SUSTAINED and territorial rather than instantaneous — it will not
  one-shot a pawn, but it will take the map away from a player who does nothing.
  The intimidation is exactly the owner's sentence: OMG, what is going to happen —
  and the answer is *it is coming here.*
- **Per-biome flavor:** yes — runner speed, look, and what the receding mass leaves
  behind; jungles get the standing version (the overgrowth doesn't fully recede —
  which IS "the jungles visibly grow").
- **Trade:** the biggest fantasy and the only option where the terminal moment is
  itself a spreading growth spectacle — but the heaviest build (many tiles animating
  at once; the perf gate in §4 bites hardest here), the hardest to tune fair, and
  the least point-harvestable: it pays in territory and bulk biomass, not a prize
  you snatch at the peak.

### How they recur (all options)

Recurrence is water-driven in every case: the plant, stump, or root re-enters the
surge whenever soaked again. Natural recurrence rides floods and rain; designed
recurrence rides the player actions in §3 (irrigation makes it a crop cycle,
deliberate flooding makes it a weapon). No option ends in a dead one-shot.

---

## 3. Question 2 — CUSTOM MOD ACTIONS (experience it, play with it, replay it)

Concrete verbs, each with a rough mechanism sketch. Register: design; C#-vs-def
notes are sketches, not commitments.

### Trigger it

- **SOAK (irrigate):** a buildable irrigation channel / sprinkler head
  (`<RUT_...>` building) that soaks its footprint on demand — turns the mechanic
  into deliberate agriculture: prime a field, stand back, take the terminal moment
  on your own schedule. *Mechanism:* building def + C# comp that applies a "soaked"
  state to plant comps in range (vanilla has no soak state to patch — this is comp
  territory).
- **FLOOD (breach):** open a cistern/water store onto the ground — a one-shot area
  soak, the big red button. Cracked Lands flavor: you are doing on purpose what the
  canyon does to you. *Mechanism:* building/ability + the same soak-application comp,
  larger radius, destroys the stored water.
- **PRIME (throw):** a throwable/mortar water charge (`<RUT_...>` shell) that soaks
  a distant area — the ranged trigger, and the honest half of weaponization.
  *Mechanism:* projectile def + explosion class or comp that applies soak instead of
  damage; likely def-mostly with one small C# damage-worker.

### Harvest it

- **TAP (harvest at the tell):** cutting the plant during the warning phase yields
  the premium product (the §10b bloom crop); earlier yields less, later costs you the
  terminal moment on your head. Risk-priced harvesting — the closer to the top, the
  better the prize. *Mechanism:* C# comp exposing yield-by-stage to the harvest job;
  the designation itself stays vanilla.
- **GLEAN (harvest the aftermath):** every option leaves a post-terminal drop (pulp,
  rotting crown, fallen trunk, receded biomass). Free of risk, lesser value. Keeps
  the flood's "disaster and fertilizer, both faces" promise from
  `FLOOD_WITNESS_EVENT_1`. *Mechanism:* item defs + spawn logic in the terminal-moment
  comp; def-heavy.

### Survive it

- **READ (the tell is teachable):** every terminal moment has a visible, learnable
  warning — the strain-wobble, the crown, the lean, the runner-front. First
  encounters teach by scaring; a letter/alert fires the first time a colony's own
  plant reaches the tell. *Mechanism:* comp state + one alert class; small C#.
- **CUT (break the chain):** cutting a surging plant before the top defuses it —
  and clearing a dry firebreak stops Option D's spread cold. Makes plant-cutting a
  defensive verb, not a chore. *Mechanism:* already vanilla (cut designations);
  the comp just has to die gracefully when cut.
- **REFUGE (elevation/distance):** terminal effects respect cover and distance
  rules so ledges, walls, and open ground are real answers — the refuge-ledge
  lesson from the flood event generalized. *Mechanism:* falls out of using standard
  explosion/spawn machinery; design constraint, not code.

### Weaponize it

- **BAIT (prime the killbox):** soak the ground where raiders will walk; time the
  terminal moment onto their heads (bursts and deadfalls excel; the surge walls
  them in). Skill ceiling: reading raid timing against growth timing. *Mechanism:*
  no new code beyond the triggers above — weaponization IS trigger + timing, which
  is the elegant version.
- **LOOSE (carried seed-bomb):** speculation, further out — a harvested seed/pod as
  a thrown weapon that starts a surge where it lands (needs water there to matter,
  which keeps it honest). *Mechanism:* item + projectile def, reusing the soak comp.
  Flag: could trivialize the dread if too available; propose it as a late-game
  unlock, owner to rule at build time.

### Replayability spine

Trigger verbs make it schedulable, harvest verbs make it profitable, survive verbs
make it fair, weaponize verbs make it clever — the same terminal moment recurs in
four registers. The natural version (flood, rain) stays the intimidating one because
it happens at scale and not on your schedule.

---

## 4. Engine notes and build gates (from the item; not design decisions)

- **Visible growth is the hard part:** vanilla growth is tick-slow and visually
  stepped. Real-time visible growth needs per-tick (or short-interval) graphic
  scaling, or many staged graphic swaps, via a C# comp — there is no def-only route
  to the on-screen effect. Staged swaps are cheaper but chunkier; smooth scaling is
  the fantasy but the cost is unmeasured.
- **🔴 BUILD GATE — perf:** measure the cost on a jungle map at density BEFORE
  promising density anywhere. No perf number exists yet and none is claimed here;
  Option D and the flood-week mass showcase are the stress cases. If the measurement
  fails, the fallback is fewer simultaneous surges (a cap with priority to
  player-visible plants), not abandoning visibility. (Speculation as to fallback;
  the measurement itself is the item's own instruction.)
- **Soak detection:** "water-soaked" needs a definition — flood terrain, rain +
  soil type, adjacency to water tiles, or an explicit comp state set by events and
  player triggers. Sketch: an explicit comp state applied by (a) flood/rain events,
  (b) the §3 trigger verbs — cleanest to test and the only version that can't
  misfire off unrelated water tiles. To be verified against engine reality at build.
- **Consumers already waiting** (from the item): Cracked Lands flood-weeks (§10b),
  the jungles (AB_MycoticJungle, BiomeCypreJungle sheets when they come), any biome
  with soaking events. `FLOOD_WITNESS_EVENT_1` is the guaranteed showcase and its
  timing rides the plot, not weather RNG.
- **Naming:** the mechanic is world-any-Rim (nothing Star Wars in it) — tier
  suggests `<RM_...>` for the core comp/mod, `<RUT_...>` for campaign-specific
  flavor defs (the bloom crop, the water chimes tie-ins). Per
  `design/NAMING_SCHEME_PLAN.md`; names themselves left to the naming item.

## UNKNOWN (could not be grounded in the docs read)

- Whether the engine can smoothly scale a plant's draw size per tick at acceptable
  cost — asserted possible in the item's engine notes, unmeasured (build gate).
- What "water-soaked" is mechanically in the current mod stack (no soak/wetness
  system found in the design docs read; sketch above is speculation).
- All numeric tuning: growth duration, radii, damage, yields, windows — no source
  states any; every number-shaped statement above is marked as tuning.
- The jungle biomes' own sheets (not yet written per the item) — jungle flavoring
  above is inferred from "the jungles should visibly grow," nothing more.

---

## Owner cards

### CARD 1 — Terminal moment: THE BURST
The plant swells, strains, and explodes — seeds and pulp everywhere, each seed
starting the next round. Loud, scary, self-spreading.
**Trade:** the scariest single moment and it spreads itself — but you can't fully
control where it re-seeds, and your own field going off is a mess you didn't order.

### CARD 2 — Terminal moment: THE GREAT BLOOM
The plant crowns into a giant flower that holds for a while, then rots. Cut it
during the window for the prize; miss it and the rot brings trouble instead.
**Trade:** the prettiest and the best money-maker (the flood-week crop) — but the
least scary of the four; it's a harvest deadline more than a monster.

### CARD 3 — Terminal moment: THE DEADFALL
The plant grows into a leaning tower and comes crashing down where it leaned.
Watch the lean and you're safe; ignore it and it lands on you — or your roof.
**Trade:** the most physical danger and it leaves fallen trunks that change the
map — but it only works for tree-sized plants and reads badly in a mass event, so
it can't be the whole answer by itself.

### CARD 4 — Terminal moment: THE OVERGROWTH SURGE
The plant doesn't die at the top — it spreads: green runners race across every wet
tile toward you, swallowing what they reach, stopping only at dry ground. When the
water's spent it all slumps into harvest.
**Trade:** the biggest "OMG what is happening" and the only one where jungles
literally advance — but the heaviest on performance (must pass the jungle-map
measurement first), and it pays in territory and bulk, never a single snatchable
prize.

### CARD 5 — Terminal moment: SPLIT IT PER-BIOME
No single world answer: jungles get the Surge, the Cracked Lands get the Bloom
(its crop economy is already ruled), tree country gets the Deadfall, groundcover
gets the Burst — one shared growth spine, four regional tops.
**Trade:** every biome gets its best-fitting moment — but it's the most build (all
four mechanisms) and the mechanic loses one instantly-recognizable signature.

### CARD 6 — Action set: HOW MUCH DO PLAYERS GET TO DRIVE IT?
- **(a) Watch-and-survive only:** floods and rain trigger it; players harvest the
  aftermath and learn to stay clear. *Trade: cheapest to build, keeps the dread
  pure — but players can't farm it or weaponize it, so it stays a spectacle.*
- **(b) Farm it too:** add irrigation/flood triggers and peak-harvesting (SOAK,
  FLOOD, TAP). *Trade: the boom-bust economy becomes playable — but a scheduled
  terror is less terrifying; the wild version must stay bigger than the farmed one.*
- **(c) Full toolkit:** (b) plus ranged priming and seed-bombs (PRIME, LOOSE) —
  players weaponize it against raids. *Trade: the most replay value and the
  cleverest stories — but the most build, and the dread survives only if
  weaponizing stays expensive and conditional (needs water where it lands).*
