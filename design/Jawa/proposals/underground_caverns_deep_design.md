<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# Underground caverns deep design — the desert's dungeon vocabulary

Companion to `design/Jawa/proposals/water_economy_deep_design.md` (Doc 1),
which this doc cross-cites directly — a drained aquifer from Doc 1's water
heist is one of this doc's cavern entrances, not a separate invention. Reads
against `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md` R-H7 (the
poison headwaters, the ocular forests, and the fact that a river's drinkable
reach and its toxic source are the same water at different points) and
`design/Jawa/worldbuilding/water_doctrine.md` (the League/Deepwater Compact
holds the deep aquifers — meaning the deep aquifer layer this doc proposes is
literally their territory, underground).

**No worldgen.** Every map below is either (a) a generated visit-map spawned
at an authored world site, the way `ownership_settlement_spec.md` §8 already
generates settlement districts, or (b) a genstepped layer under an existing
authored map. Nothing produces an alternative planet, a seed variant, or a
reroll knob — cavern *sites* are hand-placed on the one frozen map, same
discipline as every other landmark in `the_one_map.md`.

---

## 0. Why caverns, and why they matter more here than on a normal Rim world

A tidally-locked desert world has almost nothing to hide behind on the
surface — flat sightlines, no forest canopy, punishing heat, and (per Doc 1)
water sources that are already the most contested, most watched tiles on the
map. **Underground is the only place on Ash'karr where secrecy is free.** It
is also, mechanically, the *only* place the player's single greatest asset —
the Utinni gravship, with its guns, its shields, its mobility — cannot follow.
That's not a limitation to work around, it's the entire design's reason to
exist (§1).

---

## 1. THE SHIP STAYS ON THE SURFACE — the design's soul

This is the rule everything else here is downstream of, and it needs to be
load-bearing, not a flavor note:

- **No gravship in a cavern map, ever.** Not "the ship can't fit" as a
  physical excuse — the ship is categorically surface-only equipment,
  structurally the same restriction as "you can't bring your starfighter into
  a cantina," and it should be enforced the same blunt way: cavern maps are
  not gravship-landable sites, full stop, the way a settlement's inner
  district already isn't.
- **No shields, no ship guns, no home-turf advantage.** Every fight
  underground is fought with what the away team is actually carrying — the
  single biggest tonal shift the campaign has available. Everywhere else the
  Utinni is the answer to "we're in trouble." Underground, it isn't in the
  building.
- **What the player carries down is everything** — this is the *expedition
  loadout* as its own decision layer, distinct from general colony
  equipping. Light sources (§6), water and food for a trip with no
  resupply, breathing gear for bad-air pockets, rope/climbing kit for
  collapse terrain (§7), and whatever the mission actually needs (mining
  tools for a vault, combat loadout for a hostile enclave). **This is a
  genre RimWorld barely has** — vanilla caravans are the closest analogue,
  and they're built for travel, not for a return-trip dungeon crawl with a
  hard "no reinforcements are coming" constraint.

**Prior-art divergence:** DeepRim's mining-shaft layers let you freely shuttle
"pawns, animals, items and power between the surface and underground layers"
— power included. DeepRim treats the underground as an extension of the
base's logistics network. **We want it to be a place that network cannot
reach.** Every trip down is a commitment, not a supply run — a deliberate,
named divergence from the most direct piece of prior art, not an oversight.

---

## 2. Cavern entrances — how you get down there

Entrances are authored world/map features, each with its own in-fiction
logic, matching the owner's list and extending it:

| entrance | in-fiction cause | what it signals to the player |
|---|---|---|
| **sinkholes** | ground collapse over an old void — could be natural karst, could be an ancient vault's roof | usually unmarked, discovered by walking near one and having it *become* an entrance (a triggerable hazard as much as a door) |
| **tar-drained voids** | pockets left by a resource fully extracted long ago (parallel to Doc 1's drained aquifer — anything that USED to be full and is now empty leaves a void) | "someone was here before, and took everything" — a looted-vault tell |
| **dry cistern shafts** | ⭐ **the direct Doc 1 cross-reference**: a settlement's water source, drained past `depleted` (Doc 1 §2's aquifer-depletion consequence), stops being a water feature and becomes a cavern entrance. A settlement the player heisted dry doesn't just get poorer — it gets a hole in the ground where its well used to be, and that hole leads somewhere. | the clearest possible statement that the two docs are one world: theft has a *geological* consequence, not just an economic one |
| **Rakatan bore-tunnels** | deliberate ancient construction — ties into the ruled vault-item canon (§5) as the entrance vocabulary for the deepest, most designed sites | unmistakably built, not found — geometry too regular to be natural, a hostile-scored tell before the player is even inside |

**Mechanically**, each entrance type is a map-transition building/feature
(same category as any existing enter-a-sub-map trigger RimWorld or its mods
use) that spawns a **new, generated cavern map** authored at that world site.
This is identical in kind to how DeepRim's mining shaft or Z-Levels' stairs
create a new map layer — the divergence from that prior art is entirely in
§1 (what you can bring) and §3 (how the maps chain), not in the basic
transition mechanism, which is well-trodden ground worth reusing rather than
reinventing.

---

## 3. Verticality within a flat-map engine — the map-chain approach

RimWorld's engine has no real Z-axis. Every existing "underground" mod solves
this the same fundamental way — a second flat map, connected by a
transition point — and differs only in how many layers, how persistent, and
what crosses between them:

- **Z-Levels / MultiFloors**: true multi-floor stacking, stairs per floor,
  synced weather between floors, raiders can pathfind up and down stairs.
  Ambitious, and explicitly flagged by its own community as save-breaking
  and unstable across versions — a real cost for a feature this doc doesn't
  need in that form (we don't want "one map with floors," we want discrete
  dungeon maps).
- **Z Pocket Dimension**: cavern-style generation with tunnels, cave plants
  and cavern animals, one pocket per map tile — closer in spirit to a
  cavern *biome* than a dungeon *chain*, and worth mining for cave-flora/fauna
  set-dressing ideas even though its structure (one static pocket per tile)
  is not the shape this doc wants.
- **DeepRim**: mining shafts drilling down into successive new map layers,
  each layer named and persistent, ore density tunable, with **free
  pawn/item/power transfer between layers** — the single most relevant prior
  art for "how do you technically spawn a chain of connected maps and let a
  player descend through them," and the piece this design deliberately
  diverges from on §1's ship-stays-surface rule and on power/logistics
  transfer.
- **CaveBiome / Biomes! Caverns**: not a descent mechanic at all — these are
  cave *biomes* you settle into directly (a cave replaces the biome a normal
  map generates in), useful purely as a reference for cave-appropriate
  flora/fauna/lighting art, not for the chain structure.

**Our approach, stated plainly: a dungeon is a CHAIN of generated maps, each
one an authored "layer" reached by a shaft/hole/tunnel exit, with the
surface map as the chain's permanent, unremovable anchor.** Concretely:

1. The surface entrance point is a fixed map feature, always returns to the
   same surface location (no drift, no re-roll — same discipline as the rest
   of the frozen world).
2. Each cavern layer is a generated map (composed via the same rimplace/Lua
   template machinery the settlement districts already use —
   `ownership_settlement_spec.md` §8's composition step is architecture we
   should reuse here almost unchanged: cavern *rooms* instead of city
   *districts*, same manifest-driven adjacency composition).
3. **A layer's only two exits are up (back toward the surface anchor,
   possibly through intermediate layers) and down (deeper).** No lateral
   jumps between unrelated dungeon chains — this keeps the chain legible and
   avoids the engine ever needing to represent more than one map "loaded
   adjacent" to another, sidestepping the exact stability class of bug that
   makes Z-Levels risky.
4. **Depth is persistent per site, not per player action.** A layer, once
   generated, keeps its state (looted rooms stay looted, a collapse stays
   collapsed) for the life of the campaign, matching the frozen-world
   discipline everywhere else in this project — this is a generated map that
   then behaves like any other authored one once it exists, not a
   regenerate-on-visit roguelike.

This is more robust than Z-Levels' approach specifically because it never
asks the engine to hold multiple maps in a live vertical relationship at
once — it's caravan-style map-to-map travel (which RimWorld already does
constantly and reliably) wearing a dungeon's clothes, rather than a
same-tile Z-stack (which is the part of Z-Levels/MultiFloors that's fragile).

---

## 4. Subterranean ecology, by depth

Layered so each descent is legibly *worse and stranger* than the last —
matching the owner's "bizarre ecology" spark, and giving the player a reason
to feel every additional layer as a real cost, not a reskin:

| depth band | ecology | economy |
|---|---|---|
| **shallow (layer 1)** | fungal pastures — bioluminescent-adjacent but mostly just alive: mold gardens, blind insects, the first cave fauna. Survivable air, tolerable temperature. | scavengeable biomass, maybe the first sign of an inhabited layer above (§5) |
| **mid (layer 2–3)** | blind fauna proper — predators and grazers with no eyes, echolocation or vibration-sense instead; bioluminescent economies where light itself becomes currency (a lit passage draws things, a glowing fungus is both hazard-marker and harvestable resource) | this is where "darkness as a real mechanic" (§6) starts mattering — safe zones are the ones you can see, not the ones that are empty |
| **deep — the aquifer layer** | ⭐ **the water actually lives here.** This is where Doc 1's whole potable/non-potable model has its source geography made literal and walkable: a cavern layer that IS an aquifer, water underfoot instead of underground-and-abstract. **A drained settlement aquifer (Doc 1 §2) becomes exactly this kind of layer once emptied** — the heist doesn't just create a surface consequence, it opens a new place to go. | the deepest legitimate "why would anyone come down here" answer that isn't combat or loot: water security, for whoever controls this layer |
| **deepest — the vault layer** | Rakatan-built, not evolved — see §5 | the campaign's dungeon endgame |

**Bioluminescence as economy, not just atmosphere**: a light-producing
organism or mineral that's simultaneously (a) the only safe light source that
doesn't attract the things §6 describes, and (b) itself a resource worth
extracting, so the player is constantly trading "light now" against "light
later, sold." This gives the mid-depth ecology a gameplay verb, not just set
dressing.

---

## 5. Underground settlements — who lives down there, and why

Three answers, each with a distinct silhouette so the player can read "who
built/lives in this layer" at a glance before a single dialogue box opens:

- **Heat refugees.** The most mundane, most humane answer, and the one that
  most directly earns its place on a world this hot: people who couldn't
  survive the surface anymore and went down instead of dying. Low security
  profile (echoes the ownership fabric's Junkers-tier forgiving posture —
  this could literally BE a Junkers-adjacent enclave, reusing that pilot
  faction's tuning), scavenger economy, more interested in trade than
  combat. The layer they occupy looks *adapted*, not built — patched walls,
  reused surface junk, jury-rigged light.
- **Droid enclaves.** A direct thematic tie to the Free Droid Enclaves
  faction and to `water_doctrine.md`'s droid-thirst-none ruling — droids are
  the one population type for whom "no water down here" isn't a problem at
  all, which makes underground the single most defensible, most
  economically rational place for a droid population to be. This is a
  free, already-canon-supported reason for a specific underground faction to
  exist rather than an invented one.
- **Something older.** Pre-human (pre-any-current-faction), non-explaining —
  the layer that doesn't answer "who lived here," it just shows evidence
  that something did, and that it isn't entirely gone. This is the tonal
  bridge into the vault layer (§5 continues below) and should stay
  genuinely unresolved rather than lore-dumped; a dungeon's best rooms are
  the ones that raise more questions than they answer.

---

## 6. Deep vault bases — new archetypes beyond the existing item

The existing vault-item canon (Rakatan vaults, referenced elsewhere in the
campaign as a specific placed item/site type) stays the campaign's dungeon
*endgame*, but this doc's job is to give the underground layers **new
archetypes distinct from that vault**, so "underground" doesn't collapse into
"one reused vault template repeated":

- **Seed vaults.** A dry, sealed, deliberately preserved archive — biotech
  or agricultural, not weapons — that rewards patience and careful handling
  over combat. The payoff is strategic (new crops, new genetic material) not
  a loot pile, giving the underground game a non-violent high-value target.
- **Flooded galleries.** A layer partially claimed by the aquifer layer
  above/adjacent (§4) — half-submerged rooms, current, the risk profile
  shifts from "things in the dark" to "things in the water," and the
  expedition-loadout tension (§1) gets a new axis: do you bring the gear for
  a swim, knowing it trades off against combat loadout weight.
- **A cavern that is one organism.** The strangest and most purely "bizarre
  ecology" entry on the list: a layer where the walls, the fungus, the
  fauna, and the light are all one distributed creature, and disturbing one
  room has consequences in a room the player hasn't found yet. Mechanically
  this can be as simple as a shared "irritation" meter across a layer's
  rooms that changes hazard spawn rates as it rises — expensive to build
  well, but it's the single most distinctive image on this whole list and
  worth flagging as the dream-tier centerpiece (see Build ladder).

---

## 7. Collapse and cave-in — hazard AND tool

Two-sided by design, matching how a smart expedition should be able to use
the same mechanic offensively and defensively:

- **As hazard**: unstable ceiling in old or damaged layers (especially
  anything near a Doc-1-style drained aquifer, where the rock has lost
  whatever the water was holding up) — a real risk to weigh against speed,
  and a reason "rope/climbing kit" belongs in the expedition loadout (§1)
  alongside light and air.
- **As tool**: a deliberate collapse (an explosive charge, or a mined
  support beam) can seal a pursuing enemy behind the player, cut off a
  layer's connection entirely (permanently, per the persistent-state rule in
  §3 — a collapsed passage stays collapsed), or open a shortcut between two
  otherwise-distant rooms. This gives the player agency over the very map
  topology the chain-of-maps structure (§3) is built from, without needing
  the engine to do anything more exotic than swap which transition points on
  a generated layer are currently active.

---

## 8. Darkness as a real mechanic

Underground is the one place on Ash'karr where **light is not free and not
default** — everywhere else on this desert world, the problem is too much
light and heat; down here it inverts completely, and that inversion should be
felt, not stated:

- **Light discipline** is a real expedition decision (§1): carrying enough
  light to work and see hazards, without carrying so much that you're a
  beacon (see next point). This turns "how much light-source fuel/charge did
  you bring" into a resource-management question with the same shape as
  water on the surface — pleasingly recursive with Doc 1's whole framing of
  scarcity-as-the-game.
- **Things are drawn to light.** The mid-depth bioluminescent-economy fauna
  (§4) and the deep-layer predators both key off light level, meaning a
  bright, safe-feeling torch is sometimes the wrong tool — the player who
  always over-lights an expedition should occasionally pay for it, and the
  player who masters using dim/no light in the right rooms should be
  visibly rewarded (quieter passage, fewer encounters). This is a single
  shared "ambient light level" trigger read by multiple creature AI
  behaviors, not a bespoke system per creature.

---

## Mechanics summary — what's a def, what needs C#

| feature | defs only? | needs C# | why |
|---|---|---|---|
| entrance features (sinkhole, drained cistern, bore-tunnel) | yes, as map-transition buildings | a shared "spawn/link generated cavern map" transition (reference: DeepRim's shaft mechanism, reimplemented rather than depended-on since our chain semantics differ) | new mechanism, but a well-precedented one |
| ship-excluded cavern maps | data (map tags: not gravship-landable) | possibly a small check where landing sites are validated | mostly a flag, reusing whatever already stops a ship from landing at, e.g., a settlement's inner district |
| expedition loadout tension | defs (light/air/rope items) + tuning | no — reuses existing inventory/equip systems | it's a design constraint expressed through item weight/need defs, not a new subsystem |
| map-chain generation (up/down only, persistent per layer) | manifest schema (Lua templates, adjacency) reusing `ownership_settlement_spec.md` §8's composer | a chain-state tracker per site (which layers exist, their persistent state) | biggest net-new C# in this doc, but architecturally a sibling of the district-composition system already being built for settlements |
| depth-banded ecology (fungal/blind-fauna/bioluminescent/aquifer/vault) | defs (PawnKind/plant/terrain per band) | shared "ambient light level" trigger for creature AI (§8) | mostly authored content; one shared signal is the only new mechanism |
| aquifer-layer ↔ Doc 1 drained-well cross-link | data (a manifest-state → cavern-site trigger) | small hook: Doc 1's manifest-depletion event also unlocks/spawns a cavern entrance | the payoff cross-reference; cheap once both fabrics exist |
| underground settlements (refugees/droids/older) | defs + manifests, reusing settlement-visit machinery (§5's factions can literally be existing faction data) | none beyond what settlement-visit already needs | almost entirely authored content on existing rails |
| new vault archetypes (seed/flooded/organism) | defs + Lua templates for the first two | the "organism cavern" shared-irritation meter is bespoke, small | flagged explicitly as the ambitious one — see Build ladder |
| collapse/cave-in (hazard + tool) | defs (a triggerable terrain-collapse feature) | a job/verb for deliberate collapse, toggling which chain-transitions are active | small, reuses §3's transition-active flag |
| darkness/light-draws-things | tuning data | the shared ambient-light trigger from the ecology row above | one signal, multiple consumers |

**The throughline**: the map-chain mechanism (§3) is the one genuinely new
piece of infrastructure this doc needs, and it's deliberately built as a
sibling to the district-composition system `ownership_settlement_spec.md` is
already committed to building — cavern "rooms" instead of city "districts,"
same manifest-driven Lua composition, same team of tools. Everything else is
authored content, shared trigger signals, or small hooks into systems already
being built for other reasons.

---

## Build ladder

**v1 slice** — one entrance type (sinkholes, cheapest to author, no
dependency on Doc 1's aquifer-depletion feature existing yet), a two-layer
chain (shallow fungal-pasture layer, one deeper layer), ship-exclusion
enforced, basic expedition-loadout light/air needs, darkness-draws-things on
one creature type. Proves the map-chain mechanism end to end before anything
else is built on top of it.

**v2** — full entrance vocabulary including the dry-cistern-shaft link to
Doc 1's aquifer depletion (requires that feature to have landed first);
full depth-banded ecology through the aquifer layer; underground settlements
(heat refugees and droid enclaves, reusing existing faction data); collapse
as both hazard and player tool; seed vaults and flooded galleries as the
first two new vault archetypes.

**dream** — the organism-cavern archetype (§5's shared-irritation-meter
layer) as a fully realized, one-of-a-kind dungeon; deep bioluminescent
economies with their own micro-trade loop; the "something older" layer
paid off with content that still refuses to fully explain itself. Explicitly
NOT a dream-tier item: anything that turns cavern generation into a
player-facing world-shaping tool — that stays permanently out of scope under
house rules, no matter how tempting a "let players configure their own
dungeon" feature becomes later.
