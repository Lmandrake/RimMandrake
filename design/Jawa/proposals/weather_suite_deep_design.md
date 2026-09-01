<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# The sky as terrain — a weather vocabulary for a world that never turns

Grounding docs: `research/Jawa/rimworld_weather_mod_concepts.md` (§7–§9, §19–§22,
§25–§26 — the tidally-locked material this doc expands), `design/Jawa/worldbuilding/
tidally_locked_world.md` (the planet physics: arc from the substellar point, not
latitude — x=1.0 is the terminator at −37 °C on the mod's own curve, the painted
Ash'karr curve runs `[70, 58, 38, 14, −22, −58, −80]` at arc 0/30/60/90/120/150/180),
`design/Jawa/worldbuilding/hydrology_and_fire_ecology.md` (R-H1 rain-only-on-peaks,
R-H7 the ocular forests), `design/Jawa/ownership_settlement_spec.md` (the perception
fabric §4 rides on).

**FIRE is another writer's lane** — `design/Jawa/proposals/fire_ecology_deep_design.md`
owns dry-thunderstorm ignition, Pyroconvective Cells, Pyrocumulus Storms, ember/ash
propagation and the fire-emergent creature roster in full. **Nothing below reignites
that ground**; where a system here would naturally touch fire (glass storms near the
Pyrelands, static charge near a burn), the note says so and stops.

**House rules honoured throughout.** No worldgen — every system is a `WeatherDef` /
`GameConditionDef` / world-map overlay placed on the frozen Ash'karr map, driven by
the fixed geometry the planet already has (substellar point, terminator, poles),
never a generator that could roll a different planet. Anti-exponential — nothing
below is a bigger storm number; each entry is a new *place the sky puts you* and a
new *decision the player makes because of it*, priced in real cost. "Jawa" stays
lore text; no defNames invented, only described in the register a def would carry.

---

## 1. Terminator storms — the permanent front you fly through, not around

**The physics.** Ash'karr's dayside runs to +70 °C at the substellar point and its
nightside falls to −80 °C at the antistellar point, with the terminator sitting at
roughly −37 °C on a curve that is fixed geometry, not a season. Where two air masses
that extreme meet, they do not blend gradually — they meet as a **standing front**,
because nothing on this planet ever moves the boundary that creates it. Vanilla's
Thermal Shock Fronts concept (research §19) becomes, here, not a passing weather
event but **the planet's one permanent weather feature**, present on every map that
straddles the terminator band, every day, forever.

**`GameConditionDef` sketch — `TerminatorFront`.** A world-map-anchored linear
feature that tracks the terminator's own fixed arc-90° line (it does not move,
because the terminator does not move — this is the one weather system in this doc
that needs no simulated motion at all, only a fixed geometric test against a map's
tile position). On any local map whose tile sits within the front's band width:
- a visible standing wall — dust/cloud/haze rendered as a fixed-bearing curtain
  across part of the map, dayside-hot on one face, nightside-cold on the other
- crossing it on foot or by caravan applies an immediate temperature-band swap
  (the "ahead of front / behind front" jump from research §19, except here it is
  not transient — walking back re-crosses it)
- lightning generation along the boundary line, well above ambient — this is
  where fog and electrical build-up (§3) breed

**Gameplay rule change — flying THROUGH it, not around it.** A caravan on foot
detours around a local front segment; **a gravship cannot** — the terminator is a
planetary ring, so any dayside-to-nightside flight plan crosses it exactly once,
by definition. This makes the front a mandatory gravship encounter rather than an
avoidable hazard: launch/landing windows (research §23) get a `TerminatorFront`
modifier — navigation penalty, mishap-probability bump, and (tying §3) an
electronics risk while inside the band. **Opportunity:** the front is also where
`ThermalShockFog` forms (moisture condensing at the boundary), which is the
cheapest source of fresh water on a dayside caravan route — a reason to route
*toward* the front rather than only fearing it.

**Cost:** exposed pawns crossing on foot without weatherproofing take the
temperature-band jump directly — RimWorld's existing hypothermia/heatstroke math
does the rest, no new health system needed. **What needs C#:** the fixed-geometry
band test (arc distance from tile to the terminator line — a small, one-time
`WorldComponent` query, not a per-tick simulation) and the gravship flight-plan
hook that guarantees exactly one crossing per dayside↔nightside trip. Everything
else — the visual wall, the temperature swap, the lightning rate — is `WeatherDef`
tuning once that hook exists.

---

## 2. Glass-sand storms — beautiful, lethal, and worth harvesting afterward

**The physics.** Extreme electrical build-up (§3) over silica-rich desert can fuse
airborne sand mid-storm — vanilla-adjacent to research §18's "glass storms," pushed
to full lethality rather than cosmetic wear, because a desert planet's signature
storm should be able to kill, and killing-by-beauty is the right register for this
world (mirrors the Pyrelands' fire-glass fulgurites in the other doc, but this is
the DRY analog — no fire required, pure electrical + windborne silica).

**`WeatherDef` sketch — `GlassStorm`.** Rare, high commonality-weight only where
static-season conditions (§3) are already active (glass storms are static seasons'
signature payoff weather, not an independent roll):
- severe ranged accuracy and sight-range penalties (dust-wall shape, research §16)
- **shrapnel ticks** — periodic, sparse, meaningful hits on exposed pawns/animals
  (per research §27's damage philosophy: a handful of real incidents over the
  storm's duration, never continuous chip damage) — lacerations from lofted glass
  shards, armor-value-sensitive so the right gear genuinely protects
- solar-panel fouling and severe wind-power surge simultaneously — the storm
  attacks one power source and gifts the other, a real trade-off during it

**Opportunity — fulgurite harvest, after.** Where lightning strikes fused sand
during the storm, it leaves **glass-fused mineral nodes** on the ground once the
storm passes — a harvestable resource node (visually and mechanically parallel to
the Pyrelands' fire-glass, but generated by electrical-storm lightning strikes on
bare silica terrain rather than by fire), richer the more violent the storm was.
This gives the storm a memory: the map looks different afterward, and walking the
strike-line the morning after is its own small expedition.

**What needs C#:** none for the storm itself (weather effects, accuracy/sight
modifiers, and shrapnel-tick incidents are all vanilla-shaped `IncidentDef`/stat
offset work). The fulgurite-node spawn wants a light hook on lightning-strike
resolution (already precedented by the Pyrelands' own fire-glass hook in the
sibling doc) to check terrain type and drop a harvestable prop instead of nothing.

---

## 3. Static seasons — weeks where everything metal bites

**The concept.** Rather than a single storm type, a **recurring atmospheric
regime**: weeks-long stretches where planetary electrical potential builds toward
a release, driven by the same terminator-front charge separation that makes glass
storms possible (§1's front is where the charge accumulates; §2's storm is when it
discharges). This gives the desert a *mood*, not just an event.

**`GameConditionDef` sketch — `StaticBuildup`.** Map-wide (or regional, tracking
distance from an active terminator-front segment), escalating over its duration:
- early: minor shock incidents on metal-touching pawns, crackling ambient audio/
  visual cue, a soft accuracy penalty on electrically-conductive weapons
- mid: **battery drain rate increases**, wireless/comms range shortens, and
  (the requested Droidworks tie) droid-race pawns running on the `ArtificialBeings`
  need-comp framework already active in this modlist take periodic **coherence-
  need disruption ticks** — a droid whose need bar the static season is actively
  destabilizing, mechanically distinct from ordinary need decay, reads as the
  world itself getting under a droid's skin the way heat gets under a human's
- late (rare, capped): the regime resolves into a Glass Storm (§2) or simply fades
  — the buildup does not guarantee a payoff storm every time, which is what makes
  the payoff, when it comes, feel earned rather than scheduled

**Opportunity + cost.** Grounding masts and Faraday-shelter rooms (research §17)
become a real desert-clan build item, not a gimmick — a static season is the
reason to have built one before it arrives, which forecasting (§8) exists to give
warning of. The cost is real economic pressure on a droid-heavy clan specifically:
this is a season where the Jawa's OWN workforce — their droids — needs the
protection most, which is a nicely on-genre inversion (the humans shrug, the
machines suffer).

**What needs C#:** a `GameCondition` subclass for the escalating-tier state
machine (vanilla conditions are largely single-intensity; this wants a tracked
tier that ratchets over its lifetime) and, if the Droidworks coherence-need tie is
taken, a small hook into `ArtificialBeings.CompCoherenceNeed` (already confirmed
present and ungated in the live droid mod chain per `design/Jawa/
droidworks_assumptions.md`) to apply a disruption modifier during the condition —
worth a spike to confirm the comp exposes a clean external hook before committing.

---

## 4. The great pressure tides — wind you can set a calendar by

**The physics.** A tidally-locked atmosphere with a permanent hot pole and a
permanent cold pole does not stay still: dayside air perpetually rises and flows
toward the nightside aloft, nightside air sinks and flows back along the surface
— a standing circulation cell, not a season-driven one, because nothing here
changes with a year. Layer onto that the world's **rotation-free geometry**
(no day/night cycle to break the pattern up) and the honest physical prediction
is a **slow, planet-scale sloshing** — pressure building on one hemisphere,
releasing toward the other, on a cycle set by the atmosphere's own thermal mass
rather than by any calendar humans invented. Call it what it is: **the pressure
tide**, and give it a real, learnable period.

**World-map system, not a local `WeatherDef`.** A `WorldComponent` tracks a single
slow oscillating value — planetary pressure differential, dayside-high to
nightside-high and back — on a period long enough to be a strategic fact (weeks,
not hours). Every map's local wind strength and prevailing direction derives from
where the current tide phase puts it relative to the terminator wind belt
(research §9) already described for this world.

**Gameplay rule change — wind becomes a resource with a timetable.** During a
dayside-releasing phase, terminator wind power spikes (real generation bonus for
wind-power infrastructure) and dayside-to-nightside gravship flights gain a speed/
fuel bonus (tailwind); during the reverse phase, the return trip does. **Sail-
craft implications**, taken literally: a Jawa scavenger clan hauling bulk salvage
over land across the near-desert could run wind-assisted ground rigs (a light,
cheap, wind-dependent hauling method) that are only worth building once a player
has learned the tide's rhythm — which is the entire point of forecasting (§8)
existing as a tech ladder rather than a single gauge.

**Opportunity + cost.** A player who tracks the tide can time a launch for the
tailwind phase and save real fuel/time; a player who doesn't gets ordinary
numbers. Extreme tide peaks (rare, at the tail of the oscillation) could briefly
exceed safe wind-power tolerances — a genuine "too much of a good thing" moment
for a nightside colony that over-invested in wind. **What needs C#:** the
`WorldComponent` oscillator itself (one slow-updating float, negligible cost —
updates on the order of once per in-game hour per research's own scope-friendly
guidance) and a read-hook wherever wind-power generation and gravship travel time
are computed. No per-tile simulation.

---

## 5. Dark-side auroras — the one beauty the night side owns

**The physics.** The nightside has no sun, but it is not without light: a planet
this electrically active (§3's static seasons, the terminator's own storm
lightning) plausibly drives a genuine magnetospheric aurora over the deep night,
independent of any local weather — the sky itself lit from above, the one thing
worth looking up for in a hemisphere the tidal-lock doctrine (`tidally_locked_
world.md`) already rules is otherwise "somewhere nothing belongs."

**`GameConditionDef` sketch — `DarkAurora`.** Nightside-only, rare, silent (no
mechanical hazard at all — the design intent is that this is the ONE nightside
weather event with zero cost, a deliberate contrast to everything else the
nightside doctrine costs the player):
- a genuine morale/mood buff for pawns who witness it outdoors — the doctrine
  already establishes the nightside as "somewhere you go when you cannot be
  found," cold and hungry and running on borrowed fuel; one free good thing that
  costs nothing is the right amount of mercy for a refuge this harsh
- a navigation aid: aurora-lit terrain grants a partial sight-range restoration
  on an otherwise near-zero-visibility hemisphere, which is a real, learnable
  reason to plan nightside travel around it rather than pure luck

**Opportunity, no cost.** This is deliberately the one entry in this whole doc
with no downside attached — every other weather system here prices its beauty in
danger; this one doesn't, because the nightside's baseline cost (cold, dark,
hungry, per the tidal-lock doctrine) is already the price, and stacking a second
tax onto the hemisphere's one moment of grace would just be cruelty without a
design purpose. **What needs C#:** essentially none — a rare `GameConditionDef`
restricted to nightside-tagged tiles, vanilla mood-buff and sight-radius
modifiers.

---

## 6. Spore blooms off the ocular forests — beauty that is also the R-H7 poison, airborne

**The physics.** R-H7 already establishes the ocular forests as the one large
organism on this planet with unlimited water, "excreting red-flowing water loaded
with reproductive spores and alien toxins" that volatilize out of the stream
before it reaches the lowlands — the rivers arrive clean because the poison
leaves the water as **vapor**. That vapor has to go somewhere. This system is
where it goes: airborne, occasionally, as a genuine weather event downwind of the
high valleys.

**`WeatherDef` sketch — `SporeBloom`.** Rare, triggered off proximity to ocular-
forest terrain (mirrors the fire doc's regional-plume propagation shape — a
source biome, a wind-carried plume, tiered effects by distance):
- near-source: visible red-tinged haze, moderate toxicity buildup on exposed
  pawns (R-H8 already establishes this planet's biology runs "genetically wrong
  on purpose" — spore exposure is squarely that register, not a generic toxic-
  gas reskin)
- downwind: thinner haze, largely cosmetic, but a visible tell that the ocular
  forests are close and upwind — a navigational fact a player can read off the
  sky before ever finding the biome on foot
- **opportunity:** spore-exposed terrain, after the bloom passes, briefly
  supports abnormal plant growth (R-H3's freakish-regrowth mechanic, borrowed
  for one bloom-adjacent tile flush rather than owned here) — a short window
  where a forageable bonus appears in a place that was ordinary desert a day
  before, rewarding a player who tracks bloom paths rather than ignoring them

**Cost.** Real toxicity risk near-source, scaling with the same "genuinely
alien biology" register R-H8 sets for anything touching this bioweapon-legacy
ecosystem — this should feel a rung more dangerous than ordinary toxic fallout,
because R-H8 already rules that everything in this cluster of biomes is not
ordinary. **What needs C#:** a wind-carried plume system, precedented directly by
the sibling fire doc's smoke/ash propagation (same mechanism, different source
biome and different payload) — if that plume-transport code ships for fire
first, this is close to pure data reuse rather than a second implementation.

---

## 7. Mirage events — did you SEE that?

**The concept.** Extreme thermal gradients (a dayside desert running toward
+70 °C at the subsolar point, per the doctrine) produce genuine optical mirages —
false water, false structures, false movement — and this world has a second,
better reason to want them: **the perception fabric already tracked in
`ownership_settlement_spec.md`** (witnesses, suspect-confidence, propagation)
gives a mirage event somewhere real to land. A caravan or a lone pawn who
"sees" something during a mirage event can generate a genuine, low-confidence
knowledge fragment in exactly the same shape the fabric already uses for a
witnessed `TakingEvent` — except the fragment is FALSE, or unconfirmed, and
propagates as a rumor the same way real knowledge does.

**`WeatherDef`/incident sketch — `MirageEvent`.** Rare, dayside/near-desert only,
triggered on extreme heat + clear sky:
- a **false oasis** rendering — a visual-only feature on the map's horizon that
  is not really there; a pawn who paths toward it (or the player who orders one
  to) discovers nothing, at the cost of the wasted travel time and — on a bad
  roll — real heat exposure for the detour
- a **phantom caravan** sighting — a distant moving shape that resolves to
  nothing on approach, but which (per the perception-fabric tie) can seed a
  low-confidence rumor fragment exactly like a real witnessed event: "someone
  saw travelers near the old wash." The fabric doesn't know it's false any more
  than the witnessing pawn does — which is the honest version of the survey's
  original Rumor Generator concept (true/distorted/false trio), except here the
  falsehood is generated by the WORLD, not narrated by an LLM, and costs zero
  Oracle calls
- **opportunity:** a player who learns to read mirage conditions (extreme heat +
  clear = high mirage chance) can discount reports made during one, which is a
  real skill the forecasting ladder (§8) can eventually name explicitly

**Cost.** Wasted movement, wasted caravan time, occasional real heat exposure
from chasing a false lead — never damage from the mirage itself, since a mirage
that could kill you directly stops being a mirage and starts being a lie the
design is telling.

**What needs C#:** a lightweight visual-only world-object/map-decal spawn (no
new pathing target — critically, the false oasis/caravan must never be a real
destination a vanilla job can path to, only a rendered feature) and, if the
perception-fabric tie is taken, a hook that lets a mirage-witnessing pawn emit a
`TakingEvent`-shaped-but-fabricated knowledge fragment into the existing
propagation pipeline — worth scoping against `PROPERTY_FABRIC_BUILD_1`'s actual
event schema once that lands, rather than guessing its shape here.

---

## 8. Forecasting as wealth — a tech ladder for a world that punishes ignorance

**The frame.** On most RimWorld deserts, weather is an inconvenience. On this
one — where a mistimed dayside crossing meets +70 °C and a mistimed nightside
exposure meets −80 °C, where the pressure tide (§4) determines whether a gravship
launch spends or saves fuel, and where the terminator front (§1) is a mandatory
crossing rather than an avoidable one — **knowing the sky in advance is a
resource as real as water**, which is exactly the frame `rimworld_weather_mod_
concepts.md` §4 already argues in the abstract. Here it is made specific to this
planet's own systems rather than a generic hurricane-tracking ladder.

| tier | building | what it reads | this world's specific payoff |
|---|---|---|---|
| 0 — folk signs | none — observation only | animal behavior, sky color, static crackle | "the crackle means a static season is starting" — free, always available, imprecise |
| 1 — instruments | thermometer, barometer, anemometer, a grounding-mast tap | local temperature, pressure trend, wind | crude static-season and terminator-proximity warning; the FIRST thing worth building on a terminator-band settlement |
| 2 — weather station | powered building | short-term local forecast, tide-phase reading | **this is the tier that reads the pressure tide (§4) directly** — the first building that turns "wind you can set a calendar by" into an actual calendar the player can consult |
| 3 — radar-analog (a grounding-mast array, tuned to the terminator's own electrical activity rather than rainfall) | regional storm/front detection | tracks the terminator front's (§1) local bulge/recession and gives real arrival windows for glass storms (§2) | the building that makes gravship launch timing (§1, §4) a planned decision instead of a gamble |
| 4 — orbital/high-altitude meteorology | full-world weather layer (gravship-borne, since there is no satellite infrastructure to inherit) | pressure-tide phase across the whole planet, static-season buildup regionally, aurora prediction (§5) | the tier that turns weather from a local nuisance into the strategic layer the research doc's §1 always wanted — and on this planet, the payoff is bigger, because the whole economy (fuel timing, wind power, static protection) reads off it |

**Design discipline:** forecasts stay imperfect at every tier below 4, per
research §4's own rule — a Tier-1 reading might say "static building, glass storm
possible in the next few days" where Tier-4 says "static discharge in
11.5 ± 2 hours." **The imprecision is content, not a bug to fix with a bigger
number** — it's what keeps Tier 0's free folk-sign reading relevant even after
Tier 4 exists (a player caught away from the weather station still has the
animals and the crackle).

---

## Build ladder

**v1 slice.** Terminator storms (§1) as the fixed geometric band-crossing feature
— this is nearly free once the arc-distance test exists, and it is the single
system that makes the tidally-locked geometry a felt mechanic rather than a
worldbuilding fact. Dark-side auroras (§5) — zero-cost, high-charm, almost no C#.
Tier 0–1 forecasting (§8) — folk signs plus the instrument building, which every
other v1/v2 system needs a reader for anyway.

**v2.** Glass storms + fulgurite harvest (§2), reusing the fire doc's lightning-
strike-spawns-prop hook once it exists for either lane. Static seasons (§3),
without the Droidworks coherence-need tie initially — ship the human-facing
shock/battery-drain layer first, add the droid disruption once the
`ArtificialBeings` hook is spiked and confirmed clean. Spore blooms (§6), reusing
the fire doc's wind-plume transport mechanism wholesale rather than writing a
second one. Tier 2–3 forecasting (§8) — the weather station and the terminator-
tuned radar-analog, which turn §1/§2/§3/§4 from things that happen TO the player
into things the player plans around.

**Dream.** The great pressure tides (§4) as a full world-scale oscillator with
wind-assisted ground rigs and gravship tailwind timing built on top of it. Mirage
events (§7) wired into the mature perception fabric once `PROPERTY_FABRIC_BUILD_1`
and the Inhabited rumor pipeline (see the sibling `llm_driven_mods_deep_design.md`
§4) are both live, so a phantom-caravan sighting can genuinely propagate through
the same knowledge-and-gossip machinery a real witnessed event uses. Tier 4
orbital-analog forecasting (§8), gravship-borne, closing the loop on every system
above with a single strategic weather layer.
