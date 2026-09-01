<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# Water economy deep design — the heist, the siege, and the thing in the pool

Reads against `design/Jawa/worldbuilding/water_doctrine.md` (differential thirst,
defended natural sources, purification tech, v2 bottle-currency) and wires
directly into the just-ruled `design/Jawa/ownership_settlement_spec.md` fabric
(claims, recognizability, perception, faction record, district manifests). Also
reads `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md` R-H7 (poison
headwaters that detoxify in transit — the reason a river is drinkable but its
source is not).

Nothing here is a worldgen feature. Every mechanic below runs on the existing
frozen map (`the_one_map.md`) and on generated settlement/visit maps composed
per `ownership_settlement_spec.md` §8. No seed sweeps, no alternate planets.

---

## 0. The two-tier water model

| tier | what it is | who can drink it as-is | value |
|---|---|---|---|
| **potable** | aquifer, spring, oasis, a river reach past its toxin-volatilisation point (R-H7) | desert-natives (low need), off-worlders (normal need), everyone | **wealth** — currency-adjacent per water_doctrine.md ruling 4 |
| **non-potable** | sulfurous vents, spore-fouled pools directly below an ocular-forest stream (R-H7's poisoned reach), brine seeps, the hypersaline sea margin | nobody, raw | **worthless until processed**, then **cheap and abundant** |

The two tiers are not a slider, they're a **fork**: a pool is one or the other,
legible at a glance (color, smell-vfx, a "Contaminated" inspect string), never a
percentage — Dubs Bad Hygiene's `Filth_Toxic`-style hazard tiles prove a
boolean-ish state reads clearly with no HUD element, and the same no-meter
taste `water_doctrine.md` rule 6 sets for perception applies here: the map
tells you, the tooltip confirms it.

### The detox chain (turns non-potable into potable, at a price)

Three tiers of tech, matching `water_doctrine.md` W5's "cheap for those who
have it, expensive to build":

1. **Crude still** (salvage-grade, matches Jawa Trade Moot canon) — slow,
   fuel-hungry, converts brine/sulfur water at a lousy ratio. Feeds a
   colonist, doesn't feed a caravan. This is the tier the player clan starts
   with if they build anything at all.
2. **Membrane filtration** (mid-game unlock, steel + component cost, a real
   research node) — the ratio gets good enough to matter. This is the
   Deepwater Compact's monopoly tech (W5), so acquiring it is either theft,
   trade, or defection of a League tech.
3. **Spore-detox chain** (late, R-H7-specific) — a dedicated process for
   ocular-forest runoff, because raw poison-headwater water isn't just salty,
   it's carrying live reproductive spores. This tier requires either
   biotech-adjacent research or literally distance (letting it sit downstream
   long enough to volatilise naturally, i.e. "the planet's own detox chain" —
   a colonist can choose to wait instead of build).

None of this needs new hediffs beyond what a `ThirstDrug`-style toxicity
mechanic already covers — Dubs Bad Hygiene's `Hediff_Dehydration` plus its
water-quality gate (dirty water risks disease before treatment) is the
precedent shape: drink non-potable raw, take a toxin hediff scaled by dose;
process it first, don't.

---

## 1. Settlements are built AROUND their water — wiring into the ownership fabric

**The core image:** the well or cistern is not decoration at the map's center,
it is *the* object the district manifest (`ownership_settlement_spec.md` §8)
generates every other district in relation to. A settlement's shape is a
territorial gradient radiating out from one tile.

### Concretely, in the manifest schema

Add a required field to every settlement manifest that has a water feature:
`waterSource: {tile, kind: potable|processed, districtAdjacency: [...]}`. The
district template library composes market row, dwelling cluster, workshop
yard etc. **outward from that tile**, the way real desert settlements are
concentric around a well — a placement rule for the Lua composition step, not
new code. `DISTRICT_TEMPLATE_LIBRARY_1` already owns "districts, sizes,
adjacency" (spec §8/#3); this is one more adjacency constraint, proved first
on the Junkers pilot manifest (spec ruling #10) before a Hutt town.

### Claim strength maxes at the waterline

This is the direct hook into the ruled claim math (spec ruling #2: claims are
`(claimant, strength 0–1, basis, timestamp)` decaying by recognizability).
**The water source itself is the single highest-recognizability territorial
claim on the whole settlement map** — it doesn't decay in any human timescale,
because everyone who lives there recognizes it permanently, every day, by
using it. Mechanically: the water tile's territorial claim strength is
authored at 1.0 and given a near-zero decay rate (or none — it's a *natural*
source, exempt from the manufactured-store carve-out in water_doctrine.md
W4), so it is always the most CLAIMED object on the map, exactly matching the
owner's spark. Every other claim on the map (a market stall's goods, a
dwelling's furniture) decays on the normal curve; the well does not, because
its basis is never a transaction, it's a birthright.

This gives district art a design target for free: **defenders cluster where
claim strength is highest**, i.e. at the water. `water_doctrine.md` ruling 2
("potable water always has significant defenders, explained by the water")
and the settlement-visit security-profile system (spec module boundary table:
"security profiles... claim-fee tables" owned by RimUtinni data) are the same
number now — the security prop density in the district template for the
water district reads directly off the same claim-strength field the fabric
already computes.

---

## 2. THE WATER HEIST — the headline capability

This is the owner's spark, built out as a full verb-family entry inside
`SETTLEMENT_VERBS_WAVE_1` (spec §"v1 verb families" — it fits the
"salvage-law gray zone" / crime suite boundary, arguably straddles both:
stealing from an unguarded pool is salvage-law-adjacent; stealing from a
DEFENDED settlement well is straight crime).

### The gizmo

A **deployable hose** — an item in the Utinni's cargo hold, or built at the
ship, that a colonist walks out and drops on a water tile within hose-length
of the landed ship (or within range of a portable pump-sled for
sources too far from a landing site). Two ends: intake pinned at the water
tile, outflow piped to storage. This is a direct structural echo of Dubs Bad
Hygiene's pipe network — **what DBH already carries**: a connected-grid pipe
system, pump throughput rates, and tank/butt storage nodes that draw down a
finite source. **What DBH does NOT carry, because it has no concept of it**:
an *unauthorized, opposed, timed extraction from someone else's claimed
resource*, with witnesses, an escape window, and a persistent world
consequence. DBH's water is either yours or infinite (a well tile with no
owner). Ours has an owner, and the owner notices.

### The mechanics, three dials

| dial | what it controls | tension it creates |
|---|---|---|
| **pump rate** | volume/tick drawn from the source into ship tanks | fast pumping = louder, more conspicuous, drains visibly faster (a claim-fabric readable "pool level" the district's own inhabitants can also see dropping) |
| **time-on-map** | how long the hose stays deployed before someone notices, patrols return, or the raid timer expires | every tick past first witness compounds perception (spec's TakingEvent → witness → propagation chain, verbatim) |
| **tank capacity** | how much the ship (or a hauled tanker vehicle) can carry away | **the greed dial** — small skim vs draining the aquifer dry is a player choice with an authored consequence gradient, not a hard cap |

**Pumps are loud.** Running pumps raise the ambient-surveillance and
witness-roll chance for the whole district, every tick they run, not just at
hose-drop and pickup — mechanically a `sustainedActPerceptionMultiplier` on
the existing TakingEvent pipeline (spec's event spine: "act → TakingEvent →
claim resolution → perception roll → propagation → faction record"), feeding
its witness-roll step a louder input for the whole duration instead of one
instant. A wandering guard patrol near the water district (which already
clusters at claim-strength-1.0 tiles per §1) is drawn toward the sound —
the spec's "fixed cameras, ambient per-faction surveillance" language already
budgets for exactly this; pumps are just a very good trigger, authored once.

### Persistent consequence: the aquifer remembers

**This is the line that makes the heist matter after the ship leaves orbit.**
Draining a settlement's water source doesn't just cost the settlement a
resource, it **rewrites the district manifest itself**, because the manifest
is data (spec §8), not a one-time layout:

- Below some drawn-down threshold, the settlement's water tile flips state:
  `potable, abundant` → `potable, rationed` → in extreme draining,
  `depleted` (a dry cistern, matching the "dry cistern shafts" entrance
  vocabulary Doc 2 uses for cavern access — a drained aquifer IS a cavern
  entrance now, cross-referenced explicitly below).
- **Rationing changes the settlement's population and posture** the way any
  resource crash would: NPC pawns can migrate out (a scripted departure event
  reading the new manifest state, not a new colonist-simulation system),
  prices for water import spike, and the settlement's security profile can
  escalate (guards get desperate, tighter gate searches per spec's gate-search
  hook: "a faction searches leavers only if its profile says so" — a drained
  settlement's profile should now say so, even if it didn't before).
- **A bounty is a faction-record entry, not a scripted quest.** Whether it
  fires is entirely governed by the spec's existing perception chain: if
  nobody witnessed the theft, or witnesses never propagated it up to the
  faction record (Junkers-tier low propagation, per spec ruling #6's example
  table), the settlement just... goes dry, confused, and the player is never
  named. If a Hutt-tier settlement (excellent propagation) got a good look at
  the ship's hull marks during the heist, the faction record carries a
  `waterTheft` provenance entry the same way a stolen rifle's serial carries
  one (spec ruling #5, "battle loot keeps its origin claim"), and *that*
  entry is what a later bounty quest, a recovery invoice, or a raid reads.
  **We do not invent a new consequence system for this. We feed the existing
  one a new event type.**

This is the single biggest reason to build the heist as data flowing through
`RM_Property`'s existing event spine rather than a bespoke feature: the
"do they know it was you" question the owner asked for is *already answered*
by the fabric, for free, the moment TakingEvent fires from a hose gizmo
instead of a pickpocket job.

---

## 3. Pool guardians — why every pool survives

**The owner's second spark, and it's a worldbuilding answer disguised as a
monster closet.** If water in the desert is this valuable, an unguarded,
un-warred-over pool needs an in-fiction reason to still exist at all — why
hasn't every faction on the planet already drained every puddle dry?

**Answer: something lives in even the smallest pools, and it responds to
disturbance.** Not a settlement's worth of humanoid guards — a creature,
often small, sometimes ancient, that:

- **Stays dormant and invisible under normal conditions** — a colonist can
  hand-draw water from a small unguarded pool without incident, the way a
  single bucket doesn't provoke a river.
- **Triggers on sustained or large-volume disturbance** — the same hook that
  makes the hose gizmo the trigger: a bucket doesn't wake it, a pump running
  for minutes does. This gives small "safe-looking" pools their own version
  of the settlement defender rule (water_doctrine.md ruling 2) *without* a
  garrison — the guardian creature IS the defender for sources too small or
  remote to justify posting people.
- **Explains its own existence in-fiction**: the pool persists *because*
  something keeps casual takers away — the in-world logic that stops every
  faction from strip-mining every puddle. Narratively, **the water is there
  partly because the creature is** (a filter-feeder or symbiote keeping a
  seep from evaporating or fouling), the same way Alpha Biomes' Ocular
  Forest — independently convergent with this campaign's own R-H7
  ocular-forest lore — ties a creature to a water feature rather than
  treating them as unrelated dressing.

**Mechanically**: a lightweight ambush/guardian creature class, spawned as a
district or wild-tile prop tied to any water feature below settlement scale
(so it doesn't compete with, or duplicate, the settlement-defender garrison
rule — it's the answer for the tiles that AREN'T settlements). Trigger
condition reads off the same "sustained act" signal the pump-noise mechanic
above already needs (§2), so this is one shared trigger definition serving
two features, not two separate systems. Difficulty scales with pool size —
tiny seep, a nuisance critter; a real oasis pool, something the player needs
a plan for.

---

## 4. Water diplomacy

Once water is trackable as a resource with a source, a level, and an owner
(all of which the fabric above already computes), the social layer is mostly
*reading* that state rather than building new systems:

- **Selling water back in a drought.** If a settlement's manifest state is
  `rationed` (from natural scarcity OR from a player heist, deliberately not
  distinguished at the mechanical layer — narratively it can matter who
  caused it, but the trade UI doesn't need to know), the player selling
  potable water there should price far above baseline. This is a straight
  supply-state modifier on an existing trade-goods price curve, no new
  system — the manifest's water-state field is the input.
- **Water tribute.** A settlement under threat, or one that's realized the
  player *could* drain them, pays periodic water tribute to be left alone —
  a recurring caravan/quest reward flow the quest system (`rimworld-quests`
  skill) already supports; the water-economy layer only supplies the flavor
  and the trigger (manifest state + faction record entry, both already
  existing). No new data type: a QuestScriptDef reading state §1–§2 produce.
- **Hutt water-debt bondage.** The bleakest version of tribute: a settlement
  or individual who can't pay for water goes into debt-bondage to whoever
  controls the supply, which is a direct mechanical use of the v2 "water
  bottles as currency" ruling in water_doctrine.md (ruling 4) — debt
  denominated in bottles rather than silver is *more* frightening precisely
  because it's denominated in the thing that keeps you alive, matching the
  water_doctrine.md line almost verbatim ("why the Hutts are frightening
  rather than merely rich"). This is the payoff feature for that ruling, and
  it should be filed as depending on it explicitly — do not build Hutt
  water-debt before bottle-currency v2 lands, or it has no unit to be
  denominated in.

---

## 5. Rain as an event — once a year, everyone stops

Per `hydrology_and_fire_ecology.md`, rain on this world falls almost only on
the unlandable peaks (R-H1) — meaning **anywhere a player or NPC settlement
actually stands, rain is not weather, it's an EVENT.** This is a
once-a-year-scale incident, not a weather-pattern change (which would risk
reading as a worldgen knob — it isn't one; it's a scripted incident firing on
the existing frozen map, same category as any other authored incident).

- **Collection frenzy.** Every settlement (player's and NPC alike) drops
  whatever it's doing to deploy every catch-basin, tarp, and open vessel it
  owns. Mechanically this is an incident that (a) spawns a temporary
  "rainfall" weather state scoped to the event's duration and geography
  (peaks-adjacent + a wide splash radius, not global), and (b) flags every
  open water-storage building on affected maps to fill at an accelerated
  rate for the duration. No new storage object type needed — reuse
  whatever containers the water-economy build already ships (tanks, butts,
  cisterns per §0–§2).
- **Truces.** The in-fiction logic is the same one that makes real desert
  cultures suspend feuds for a rain: when water stops being scarce for a few
  hours, the thing everyone was fighting over is temporarily off the table.
  Mechanically, the cheapest true version is a temporary faction-record
  modifier — hostility checks and ambient-surveillance triggers (the same
  ones §2 uses for pump noise) are suppressed or reduced for the event's
  duration on any map currently receiving the rain. This lets a player
  colony and a hostile settlement's caravan both be catching water in the
  open without an automatic fight — genuinely rare, genuinely memorable,
  and built entirely out of dials the fabric already exposes.
- **Frequency discipline**: authored as a rare, campaign-year-scale incident,
  not a chance-per-day weather roll — an EVENT the player anticipates and
  plans for (stockpiling vessels, timing a heist to the chaos), not
  background noise.

---

## Mechanics summary — what's a def, what needs C#

| feature | defs only? | needs C# | why |
|---|---|---|---|
| potable/non-potable tile tagging | yes | — | a terrain/building tag + a couple of ThingDefs |
| detox chain buildings (still/membrane/spore-chain) | yes | — | standard production-building defs with a recipe |
| toxin hediff on raw drinking | yes | — | HediffDef + a job/recipe gate, DBH-style precedent |
| water-source claim-strength (max, ~no decay) | data (RimUtinni tuning) | **hooks into `RM_Property`'s existing claim engine (already C#)** | one authored constant per source, not new code |
| district composition anchored on water tile | Lua template + manifest schema field | possibly a small composition-step hook | adjacency constraint for the existing composer |
| hose gizmo + pump rate/tank capacity | defs (Thing + comp) | **yes — a Comp driving a timed extraction job, tied into TakingEvent** | new player-facing verb; DBH's pipe-grid C# is a reference architecture, not reusable code (different assembly, different event model) |
| sustained-act perception multiplier (pump noise) | tuning data | **small hook in `RM_Property`'s perception roll** | one multiplier input on an existing roll |
| aquifer depletion → manifest rewrite | data (thresholds) + a scripted incident/quest | **a manifest-mutation call, likely already needed for other manifest-state changes (drought, raids)** | reuses whatever "manifest state changes" mechanism the visit-loop mod needs generally |
| pool guardian creatures | defs (PawnKind/creature) | trigger hook shared with pump-noise | one shared "sustained disturbance" signal |
| water diplomacy (price, tribute, debt-bondage) | defs + QuestScriptDefs | — | reads existing state, no new mechanism |
| rain-as-event | one IncidentDef | small scoped weather-state + suppression hook | rare by design, not a weather-system rewrite |

**The throughline**: almost nothing here is a new system. It's the
`RM_Property` claim/perception/faction-record spine (already ruled, already
scoped for `PROPERTY_FABRIC_BUILD_1`) fed a handful of new event types and
authored data. The hose gizmo and the pool guardian trigger are the only
genuinely new mechanisms, and both are small.

---

## Build ladder

**v1 slice** — potable/non-potable tile tagging + crude still; settlement
manifests carry a `waterSource` field and district composition anchors on it
(Junkers pilot, per spec ruling #10); the hose gizmo exists with pump
rate/tank capacity and feeds the *existing* TakingEvent pipeline with a
sustained-act multiplier; pool guardians exist as one creature class gated on
the same sustained-disturbance signal. No aquifer-depletion manifest rewrite
yet — a heist just steals a fixed haul and leaves.

**v2** — membrane filtration + spore-detox chain tiers; aquifer depletion
persistently rewrites district manifests (rationed/depleted states, NPC
migration, security-profile escalation); water diplomacy (drought pricing,
tribute quests); rain-as-event with collection frenzy and truce suppression;
bottle-currency integration for tribute/debt-bondage once
water_doctrine.md's ruling 4 lands.

**dream** — a settlement's entire posture (garrison size, gate-search
strictness, even which districts exist) generated *live* off its current
water state rather than an authored manifest baseline, so two players who
each heist a different settlement leave behind two visibly different, fully
consistent worlds — with the caveat that this stays within composing
pre-authored district templates differently, never generating new terrain or
a new world.
