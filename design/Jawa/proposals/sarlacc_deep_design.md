<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# The Sarlacc, deep design — a landmark that digests centuries

Grounding: `research/Jawa/rimworld_sarlacc_encounter_current_design.md`
(the existing engineering direction — encounter controller, pit/maw/tentacle
architecture, variable scale, ancient-intelligence-as-narrative-layer) plus
`infrastructure/state/canon.yml` key `anomaly_content.boundary_ruled` — the
owner's verbatim ruling: *"Mostly the assailant exception but may also be
some possibilities with the sarlacc too."* That makes the sarlacc one of
exactly two places in the whole campaign allowed to draw on Anomaly's
fleshmass/entity toolbox. This doc is the design sitting that ruling
promised. `dungeons_arc_spec.md` §1 confirms the sarlacc is tracked as "a
separate item," not authored inside the Assailant/Forsaken-vault arc — this
is that item.

**No worldgen.** The pit is a fixed, hand-placed landmark site on the one
frozen Ash'karr map — the same discipline as every vault, cavern entrance,
and set-piece in `the_one_map.md`. It does not roll, does not vary by seed,
and every player who ever plays this campaign finds it in the same place,
already old, already fed.

---

## 🔴 RULED — owner sitting, saved 2026-09-02 (review sheet, 9 rows, 2 cut)

Verdicts and the owner's notes, verbatim (frozen source: `design/Jawa/worldbuilding/review/proposal_suite_review.decisions.json`; untouched rows keep their prefill — cut is the only destructive verdict):

| row | ruling | owner's note (verbatim) |
|---|---|---|
| landmark-site | v1 | Nope. There should be many Sarlacc's, but they should be semi-permanent when they're really huge. But there are smaller, more mobile ones... |
| ~~compile-digestion~~ | ⛔ **CUT** (was dream) | This is actually Star Wars lore, but it's bizarre and unsettling. I don't like it. But yes, within it, there are dungeons and trapped living things. But not like this. |
| evidence-feeding | v2→**v1** | Seems more like a religious ceremony. A rite of offering and forgetting. I like it for that. |
| tremor-disturbance | v1 | ABSOLUTELY. It must work like this, or else no one would go to the map. You can definitely sneak up on the Sarlacc. |
| anomaly-draws | v2→**v1** | I like it! Might also re-occur for the Assailtant dungeon near the end and their massive bioweapon stuff. |
| escape-quest | dream→**v1** | This must simply be true. Returning from "that place" leaves you permanently changed. Come up with many such explanations as to how, all disturbing and interesting. |
| ~~sky-seeding-myth~~ | ⛔ **CUT** (was dream) | — |
| castings-economy | v2→**v1** | I think maybe you're talking about Sarlacc pearls? |
| root-system-crosslink | dream→**v1** | Yes, I think that's right. |

## 1. The pit as a permanent authored map feature

The sarlacc is not a spawn. It is a **site**, in the same category as the
six Forsaken vaults and the cavern entrances — placed once, in a specific
tile, before any player ever lands. The existing encounter design already
gets this right architecturally (the creature is "already beneath the map");
this section makes it right *canonically* too.

- **One sarlacc. Not a spawn table entry, not a biome-eligible creature —
  a landmark**, the way a specific named ruin or a specific vault is a
  landmark. Its tile is chosen for what surrounds it (§5, §9), not rolled.
- **The pit is legible before it's dangerous.** Long before a player can
  trigger the encounter proper, the site reads as *wrong* at a glance:
  a perfect, ancient depression in the dune line that never quite fills
  back in no matter how the sandstorms move dunes elsewhere (a deliberate
  exception to `DUST_STORMS_DESTRUCTIVE_1`'s dune migration — the pit
  resists being buried, which is itself a tell that something under it is
  keeping it clear), a bone-and-wreckage apron ringing the rim at a
  consistent radius, and a silence — the existing design's "animals
  becoming agitated or fleeing" early-warning stage, but authored as the
  site's *permanent* ambient state at range, not just an escalation cue.
- **The pit has a history the player can read, not just a threat they
  discover.** Wreck fragments in the apron carry provenance the same way
  `sw_mod_concepts_triage.md` §A's salvage system tags an item's origin —
  a downed speeder here, a fragment of Old Republic-era plating there, an
  Imperial transponder half-buried near the rim. None of it is loot yet
  (§10 covers what actually comes out). It's a **timeline made of debris**,
  readable by anyone who stops and looks instead of walking straight to
  the edge.

---

## 2. The multi-decade digestion fiction

The existing design already frames age as an ecological category (Juvenile
/ Mature / Ancient-Leviathan). This section gives that age a *felt* texture
— what decades of digestion actually mean to something still alive down
there.

- **Digestion here is not "dissolve," it's "compile."** The sarlacc's gut
  doesn't erase what it eats so much as slowly disassemble and *reuse* it —
  organic matter becomes tissue, minerals become casting material (§10),
  and — per the existing design's ancient-intelligence framing — fragments
  of *mind* become part of the creature's own accumulating awareness. This
  is the throughline that makes every other section in this doc cohere:
  everything the sarlacc has ever taken is still in there, in some form,
  including the people.
- **A visible age ring, like a tree.** The pit's rim tissue can carry a
  faint visual banding — not a mechanic on its own, but authored art
  direction that gives an "ancient" specimen a read of genuine deep time,
  distinct from just "bigger pit, more tentacles."
- **Nothing that goes in fully "returns."** Even a rescued survivor (§8)
  comes back changed — the fiction is explicit that the pit keeps
  something, always. This is the honesty tax on the escape quest: winning
  doesn't mean it didn't happen to you.

---

## 3. Feeding the pit — disposal, tribute, and the ownership fabric

This is the section that turns the sarlacc from "monster on the map" into
"an institution the surrounding factions have built a relationship with,"
and it's where this doc earns its place next to `water_economy_deep_design.md`
and `underground_caverns_deep_design.md` rather than standing apart from
them.

- **Disposal.** The oldest and simplest use: things you want to be
  genuinely, permanently gone go into the pit. A body nobody should find.
  A weapon that would incriminate someone. A droid with memories someone
  paid to erase the hard way. This is disposal with teeth, because —
  per §2 — the pit doesn't erase, it *compiles*. Nothing thrown in is
  actually safe forever; it's safe from casual discovery, which is a
  different and more interesting promise.
- **Tribute.** Factions and settlements near the pit (§5) have their own
  standing relationship with it — a scheduled offering, a first-kill
  tithe, a "the pit gets a share before we eat" custom. This gives the
  sarlacc the same texture `water_economy_deep_design.md` gives water: not
  a hazard to route around, but **infrastructure with a social contract
  attached**, one that predates the player and that the player can honor,
  ignore, or exploit.
- **Feeding it EVIDENCE — the sharpest version of this idea.** The
  ownership fabric this campaign already runs on (`ownership_settlement_
  spec.md`'s claim-strength model, echoed in `underground_caverns_deep_
  design.md` and `sw_mod_concepts_triage.md` §A/§C's provenance and ledger
  systems) is built on things being *provable* — who owned it, who stole
  it, who has a claim. **The pit is the one place on the map where a claim
  goes to die.** Feed it the stolen deed, the murder weapon, the forged
  contract, and the evidence is gone — but per §2, not actually gone,
  just buried in something that occasionally, decades later, casts a
  fragment of it back out as a mineralized curiosity (§10) for someone
  else entirely to find and misread. **A crime disposed of here doesn't
  disappear from the story. It becomes a delayed-fuse plot hook with the
  serial numbers filed off by geology instead of a person.** This is the
  single strongest cross-system idea in this doc: the sarlacc as the
  ownership fabric's one true dead-end that isn't actually dead-ended.

---

## 4. What it wants

The existing encounter design treats the ancient intelligence as "an
encounter-personality layer... not a complex simulated intelligence
system." This section stays inside that constraint and gives it wants that
are legible through behavior, never through dialogue the creature itself
speaks.

- **It wants to keep eating**, obviously — but *selectively* once mature.
  A young pit strikes at anything in reach. An old one, carrying fragments
  of many minds (§2), develops something closer to preference: it goes
  quiet for ordinary traffic and stirs hard for specific triggers — a
  particular faction's transponder signature, a particular kind of cargo,
  anything that resembles what fed it something memorable once. This reads
  to the player as "it recognizes patterns," not "it thinks," matching the
  existing design's targeting-modifier framing exactly.
- **It wants to not be found out.** The pit's whole existence depends on
  being either avoided or fed on purpose — a colony that starts actively
  hunting *into* it (rather than feeding it or leaving it alone) should see
  escalating structural aggression (per the existing design's escalation
  stages), because the one thing worse for the creature than staying
  hidden is a settlement deciding it's a target instead of a neighbor.
- **It (rarely, and only in the oldest specimens) wants something specific
  returned.** The ancient-intelligence layer's best possible payoff: a
  years-old event where the pit's behavior around one particular pawn,
  item, or location is subtly different — not explained, never fully
  explained — because some fragment inside it remembers that thing
  specifically. This is the seed for the escape quest (§8) and for one
  entry in the sky-seeding myth (§9), not a system on its own.

---

## 5. Symbiosis — who lives around the pit, and why

- **Scavenger-cultists, not worshippers.** A small local population (Jawa
  clan splinter, or an independent enclave — never a new faction, reusing
  existing faction data per house-rule discipline) that has built a
  low-key economic relationship with the pit: they know the tribute
  schedule (§3), they know the tremor discipline (§6) better than anyone,
  and they harvest the apron debris (§1) and occasional castings (§10)
  that wash up at the rim without ever provoking a full stir. They are not
  a cult in the "worship" sense — they're the people who figured out how
  to run a business next to a natural disaster that occasionally pays out.
- **Apron scavenger fauna** — small, quick animals that live specifically
  off what the pit's feeding activity displaces (loose debris, fleeing
  prey, the edge of the disturbed sand), the same ecological-opportunist
  niche `tar_pits_deep_design.md` gives its own pit fauna, deliberately
  parallel rather than reinvented per pit.
- **A rival predator, kept honest by the pit's presence.** The area
  immediately around the sarlacc is otherwise *safer* than equivalent open
  desert, because nothing large wants to compete near something that big —
  giving the site a genuine risk/reward shape (dangerous at the rim,
  unusually undisturbed a short walk out) instead of being uniformly
  lethal in every direction.

---

## 6. Tremor-sense — walk softly

The vibration-as-signal idea `sw_mod_concepts_triage.md` §B already proposes
sharing between krayt leviathans and the underground caverns' darkness-draws-
things trigger extends naturally here as the *third* consumer of the same
shared "disturbance level" signal — one system, three payoffs across three
docs, never three separate implementations.

- **Movement discipline as the core tension near the pit.** Running,
  heavy equipment, gunfire, and vehicle engines all raise the local
  disturbance reading; walking, sneaking, and quiet tools keep it low. This
  is legible to the player as a literal choice between speed and safety
  every time they're within the pit's rim radius — not a hidden roll, a
  visible discipline.
- **The tell escalates before the strike.** Per the existing design's
  staged-escalation model: a rising disturbance reading produces
  increasingly obvious surface tells (trembling objects, sand shifting,
  the apron fauna of §5 scattering) before a tentacle actually surfaces —
  giving an attentive player a genuine chance to freeze, retreat, or drop
  whatever's making noise, rather than the strike feeling like a coin
  flip.
- **Thumpers work here too, on purpose.** A vibration lure built for
  krayt-leviathan hunting (§B of the triage doc) is *also* a viable — if
  reckless — tool for deliberately drawing the sarlacc's attention toward
  a chosen point (luring it away from an expedition route, or luring it
  toward an enemy). One item, two very different creatures, two very
  different reasons to own one.

---

## 7. Anomaly-toolbox draws — used, not laundered

This is the section the `boundary_ruled` canon key exists for. The rule is
narrow on purpose: **only fleshmass/entity mechanisms, only inside this
site's own encounter logic, nothing ambient, nothing that leaks Anomaly
flavor onto any other creature or building in the campaign.** Every draw
below needs its exact defName confirmed via RimSage before any build item
touches it — nothing here is a defName claim, only a mechanism claim.

- **Tentacle-grab-and-drag** — Anomaly ships creatures whose core verb is
  exactly this: seize a target, apply a pull/constrain state, drag toward
  a point. That verb shape is the direct mechanical ancestor of the
  existing sarlacc design's "grapple and dragging states for living
  targets." Reusing the verb architecture (not the flavor, not the
  creature) is the cheap, correct draw here.
- **A below-map presence that's never fully seen** — Anomaly's toolbox
  includes creatures and structures designed around partial visibility and
  off-map/adjacent-cell threat presence (things that act on a map without
  a fully rendered, fully pathfinding body occupying it conventionally).
  That's structurally identical to what the existing sarlacc design already
  wants ("the visible footprint can be dramatically larger than the actual
  logical footprint") — the Anomaly precedent is evidence this is a solved
  problem in this exact engine, not a novel risk.
- **Fleshmass-style terrain corruption, used sparingly, only at the rim.**
  A creeping, organic terrain-overlay effect (visually — not mechanically —
  adjacent to Anomaly's fleshmass growth) confined strictly to the pit's
  own apron, never spreading, never persisting past the encounter's
  immediate radius. This is flavor reuse only: the sarlacc's rim should
  look like it's *becoming* part of the creature the closer you get to it,
  and Anomaly already has the rendering vocabulary for "ground that isn't
  quite ground anymore."
- **What does NOT get drawn**: Anomaly's progression content, its research
  unlocks, its player-facing ability/power systems, its metahorror/cult
  framing as a *faction*, or anything that would read as "Anomaly is active
  in this campaign" to a player who hasn't found the pit yet. The exception
  is a single site's encounter logic, not a genre bleed.

---

## 8. The escape quest — someone climbs out

The Boba-Fett-shaped hook, played straight: being taken by the sarlacc is
not automatically death (the existing design already establishes this —
"the pawn transitions into the creature"), and the campaign should have
exactly one, rare, extremely hard-won thread where that transition runs in
reverse.

- **The rescue, not the reappearance.** The strongest version of this is
  NOT "an NPC randomly climbs out and joins you" — it's a quest the player
  has to *choose to pursue*, built on a rumor (a direct consumer of
  `sw_mod_concepts_triage.md` §D's Cantina rumor economy: "someone's still
  alive in there, if the pit hasn't finished with them") that may or may
  not be true, may or may not still be current by the time the player acts
  on it, and requires actually going *into* the encounter with rescue as
  the objective instead of loot or a kill.
- **What survivors are, mechanically**: the existing design's own list —
  long-term trapped victims, hermits, malfunctioning droids that adapted,
  tiny survivor scavenger camps inside air-pocket chambers. The escape
  quest's target is drawn from that list, never invented fresh, and per
  §2's "nothing fully returns" rule, a rescued survivor carries something
  — a trait, a scar, a fragment of borrowed memory that isn't originally
  theirs (the ancient-intelligence layer's most human-facing payoff) —
  that marks the rescue as a genuine cost, not a free recruit.
- **The climb itself is the encounter's internal-map content** — the
  existing design's stomach cavities, digestive canals, fibrous tissue
  tunnels, and scar-tissue chambers become the literal level geometry for
  this one quest's resolution, reusing content that already needs to exist
  for the loot-focused version of "entering the sarlacc" rather than
  building a second internal map just for rescue.

---

## 9. Spawn and lifecycle horror — the sky-seeding myth

The existing design is right that sarlaccs "can occur on multiple worlds
because their lifecycle allows them to establish themselves far from their
point of origin" — canon leaves the actual mechanism vague on purpose (the
films never explain it), which is exactly the right amount of unexplained
for this campaign to keep.

- **The myth, as Jawa folklore, never as confirmed fact.** Something in
  the old stories says the pit came from the sky — that before there was
  a pit, there was a night when something fell, small enough to go
  unnoticed, patient enough to wait decades before it was big enough to
  matter. This should exist ONLY as spoken folklore (an elder's story, a
  cantina rumor per §D of the triage doc, a half-legible fragment in old
  Rakatan-adjacent text) — never as a confirmed cutscene, never as
  something the player can definitively verify, because the horror is in
  not knowing whether the next "shooting star" event on this world is
  scenery or a hundred-year countdown.
- **This deliberately does NOT create a second sarlacc, ever.** The house
  rule against worldgen and against anything that "produces ALTERNATIVE
  planets" extends here by the same logic that keeps this a landmark and
  not a spawn table: **one sarlacc, authored once, and the sky-seeding myth
  stays myth for the entire life of this campaign.** If it were ever
  confirmed true and a second pit opened somewhere, that would be new-content
  worldgen-adjacent behavior on a frozen map, and the house rules kill that
  outright. The myth's whole job is to be scary specifically *because* it's
  unresolvable, not because it's a mechanic waiting to fire.
- **The apron's oldest wreckage (§1) is where this myth gets its
  evidence** — a scorched depression pattern in the debris timeline that
  predates every other layer, consistent with "something arrived here
  before anything else did." Never stated outright. Just there, for a
  player who reads the site closely enough to notice the oldest thing in
  the apron isn't wreckage at all.

---

## 10. Economy — castings as a unique material

- **Castings, not "pearls" as a reskinned gem.** Per §2's compile-not-
  dissolve digestion fiction, an indigestible core (metal, bone, ceramic,
  a fragment of something that used to be a person's tool) accumulates
  biomineral layers over years. The resulting object should read
  mechanically and narratively as **evidence with a shell on it** — cutting
  one open is archaeology, not just a resource-extraction action, and what's
  at the core (per §3's evidence-disposal hook) is sometimes recognizably
  something specific: a weapon's serial plate, a signet, a name.
- **Quality scales with how it was obtained**, directly mirroring
  `research/Jawa/Star_Wars_RimWorld_Mod_Concepts.md`'s original framing and
  echoed by this sitting's krayt-pearl economy (§B of the triage doc, for a
  deliberate cross-campaign rhyme): killing the sarlacc for its castings
  damages them; harvesting the apron's naturally-shed castings (a slow,
  patient, tremor-disciplined activity per §6) yields the best material.
  **The treasure gets worse if you're crude — twice on this map, once for
  each apex creature, on purpose.**
- **Uses**: a distinctive craft-material tier (armor/weapon components with
  a unique flavor profile — resilience, a faint organic give under impact —
  never a strict numeric upgrade over existing top-tier materials, per
  anti-exponential discipline), and a pure-flavor/prestige good for
  factions who value provenance over utility (the scavenger-cultists of
  §5 trade almost exclusively in these), giving the material two audiences
  instead of one.

---

## 11. Cross-cite — the sarlacc's roots, underground

`underground_caverns_deep_design.md` §5 already lists "Sarlacc root systems"
among the campaign's underground-entrance vocabulary. This doc doesn't
re-author that cavern content — it hands that doc exactly what it needs to
make the cross-link real:

- **The root system is the digestive plumbing, not a second creature.**
  What a cavern-layer visitor finds under/around the pit is the
  sarlacc's own subterranean tissue — fibrous tunnels, calcified passages,
  the same vocabulary the existing surface-encounter design already lists
  for the creature's *internal* map (§8 above), just reached from
  underground instead of from the mouth. One creature, two entrances,
  already-consistent art/mechanic vocabulary.
- **This is where the underground-caverns "cavern that is one organism"
  archetype (that doc's §6, its own flagged dream-tier centerpiece) and
  this doc's creature can, if the owner wants it, become literally the
  same thing** — a root-system cavern layer that IS sarlacc tissue, with
  that doc's proposed shared-irritation-meter mechanic reading directly off
  this doc's disturbance signal (§6). Flagged here as a possibility, not
  claimed as decided — the two docs' authors should reconcile this
  specific overlap before either builds it.
- **What crosses the boundary**: light, air, and structural collapse rules
  stay `underground_caverns_deep_design.md`'s (§1, §7 of that doc — the
  ship-stays-surface and expedition-loadout rules apply here without
  exception, root-system access included); tremor/disturbance behavior
  and casting/evidence content (§6, §10 above) stay this doc's.

---

## Mechanics summary — what's a def, what needs C#

| feature | defs only? | needs C# | why |
|---|---|---|---|
| pit as fixed landmark site, apron debris timeline | yes (site/building defs, provenance-tagged debris items reusing §A's ThingComp shape) | none new | authored content on an existing data shape |
| dune-resistant pit terrain | tuning (exclude from dune-migration effect) | small hook into `DUST_STORMS_DESTRUCTIVE_1`'s dune system | one flag read by an existing system |
| encounter controller, tentacles, grab/drag, escalation stages | — | the existing design's own architecture (encounter controller + independent tentacle objects) | this doc changes none of that engineering, only the fiction wrapped around it |
| tribute/disposal/evidence-feeding | data (a feed-the-pit interaction + provenance-consuming effect) | small: on evidence-feed, clear the item's ownership-fabric claim and schedule a delayed casting-spawn | the one genuinely new mechanism this doc needs |
| ancient-intelligence targeting bias | tuning (per-specimen memory tags) | the existing design's "targeting modifiers," not a new system | already scoped as encounter-personality layer, not simulated intelligence |
| tremor/disturbance signal | — | the shared trigger `sw_mod_concepts_triage.md` §B and `underground_caverns_deep_design.md` §8 already need; this is its third consumer | build once, three payoffs |
| Anomaly-toolbox draws (§7) | — | Harmony/verb reuse from existing Anomaly creature classes, confirmed via RimSage before build, scoped to this encounter only | the one place this campaign is allowed to touch it |
| escape quest | QuestScriptDef + a rumor item (reuses §D's rumor-accuracy shape) | none beyond existing quest-node branching | authored content on existing rails |
| castings economy | defs (craft-material ThingDef, harvest-quality tiers) | none | mirrors krayt-pearl material design already proposed elsewhere this sitting |
| root-system cross-link | manifest-level site link only | shared disturbance signal (already counted above) | the payoff cross-reference; cheap once both docs' foundations exist |

---

## Build ladder

**v1 slice** — the pit as a placed landmark with its apron debris timeline;
the existing encounter design's core (controller, maw, tentacles, one age
tier — Mature) built as already scoped; basic tremor/disturbance signal
gating tentacle-strike frequency; one feed-the-pit interaction (disposal
only, no evidence-provenance hook yet). Proves the site reads as a landmark
and plays as the existing engineering doc intends before any of this doc's
new fiction layers ride on top.

**v2** — the evidence-feeding/ownership-fabric hook (§3) with its delayed
casting payoff; tribute relationship with the scavenger-cultist population
(§5); the shared tremor/disturbance signal wired to all three consumers
(this doc, krayt leviathans, underground caverns); the castings economy
(§10) as a real craft-material tier; the Anomaly-toolbox tentacle-grab and
below-map-presence draws (§7), RimSage-verified before implementation.

**dream** — the full escape quest (§8) with its internal-map content and
its "nothing fully returns" character-marking payoff; the sky-seeding myth
(§9) authored purely as unverifiable folklore across multiple NPC and
cantina-rumor touchpoints, never resolved; the root-system reconciliation
with `underground_caverns_deep_design.md`'s "cavern that is one organism"
archetype (§11), if the owner rules the two should merge into a single
authored dungeon. Explicitly NOT dream-tier: a second sarlacc anywhere on
the map, ever, under any justification — the myth stays myth.
