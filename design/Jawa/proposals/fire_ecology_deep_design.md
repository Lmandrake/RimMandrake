<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
<!-- v1 SLICE GREEN-LIT by the owner 2026-09-01 (items FIRE_ECOLOGY_LOOP_1 / WEATHER_SUITE_SLICE_1 / LIVESTOCK_STARTER_TRIO_1); the remainder of this doc still awaits PROPOSAL_SUITE_REVIEW_1. -->
# The Pyrelands, made mechanical — fire as a place to be, not a place to flee

Grounding docs: `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md` (R-H3–R-H5,
the dry-thunderstorm loop, "the single best mechanical idea in this document"),
`infrastructure/state/canon.yml` → `deep_desert_tribes.fire_identity_src` (the
reap-ritual theology), `design/Jawa/ownership_settlement_spec.md` (perception and
claims), `design/Jawa/worldbuilding/setting_physics.md` (L12 environment as
participant, L13 explosives). Weather mechanics in §3 also draw on the
fire-adjacent sections of `research/Jawa/rimworld_weather_mod_concepts.md`
(§10 Firestorms, §11 Regional Fire/Smoke/Ash, §12 Ash Accumulation, §24
Weather-Sensitive Wildlife) — only the fire/ash/ember material is ingested
here; that sheet's general atmospheric-layer, forecasting and non-fire desert
weather concepts belong to a different writer's lane.

**The owner's spark, verbatim:** *"could there be creatures that emerge IN the
fire? Special weather events that only occur during the fire? Unique reasons to
BE in that hazardous place?"* Everything below is an answer to those three
questions, in that order.

**House rules honoured throughout:** no worldgen — every feature below is a
`WeatherDef`/`GameConditionDef`/`IncidentDef`/creature placed on the frozen
Ash'karr map, never a generator. Anti-exponential — nothing here is a bigger
number; each feature is a new *place to be* or a new *thing that can happen*,
priced in real danger. "Jawa" stays lore text; no defNames are invented, only
described in the register the eventual def would carry.

---

## 1. The loop, spelled out as numbers a weather table could hold

> 🔴 **RULED v1 — owner, 2026-09-01 (review sheet), verbatim:** "Brief violent
> rain should be possible (to allow the grass to explosively regrow) but as you
> say always with lightning." ⇒ the loop's weather table gains a rare
> short-lived violent-rain state, never without lightning. (Only this row of
> the fire sheet is ruled so far; the sitting continues.)

R-H4 already names the mechanism: fire generates its own convection, the
convection is dry, dry lightning strikes pre-heated ground surrounded by
grass that regrows freakishly fast (R-H3), and the new fire generates the
next storm. RimWorld ships every primitive this needs — `FireWidespread`,
`WeatherDef.lightningMtb`, fire spread off `Plant.flammability` — so this
section is mostly **table values**, not new code.

**Stage 0 — the Pyrelands' resting weather mix.** `BiomeDef.baseWeatherCommonalities`
for the Pyrelands strips ordinary rain entirely (R-H1's global rule already
requires this) and carries three weathers at roughly:

| weather | commonality (relative) | role |
|---|---|---|
| Clear | 55 | the fuel accumulates |
| **Dry Thunderstorm** (existing `DryThunderstorm`-class weather, retuned) | 35 | the ignition source, cranked hard above vanilla's ~5–10% share |
| Hot / heat wave overlay | 10 | pre-heats standing grass toward its ignition point, per L12 |

35% is deliberately far above any vanilla biome's thunderstorm share — the
Pyrelands should feel like it is *always* one bad roll from lighting up,
because that is the physical claim R-H4 makes.

**Stage 1 — ignition.** Standard `Fire` incident off a lightning strike on a
`flammability`-scaled plant. Nothing new; R-H3's growth multiplier means the
fuel bed regenerates to full flammability in a fraction of a temperate
biome's time, so a scar that burned last season is primed again quickly —
the lever that makes "a standing burn that migrates across itself forever"
real rather than a slogan.

**Stage 2 — self-sustained convection (the new `GameConditionDef`).** Once a
fire's contiguous burning-cell count crosses a threshold (RimWorld already
tracks this for `FireWidespread` escalation), spawn a **Pyroconvective Cell**
map condition centered on the fire's burning-cell centroid:
- Raises local `lightningMtb` (mean-time-between) to near-vanilla-thunderstorm
  levels **inside a radius that follows the fire**, independent of the
  ambient weather roll.
- Ends when the burning-cell count in its radius drops below the threshold
  for N ticks (the fire ran out of fuel or was contained).
- **This is the loop made visible**: the player watching the map sees a
  localized storm cell tracking their own wildfire, and can read the tactical
  fact "the fire is making its own weather" directly off the map rather than
  from a tooltip.

**Stage 3 — regional escalation.** If a Pyroconvective Cell's burn radius
crosses a large-fire threshold (tunable, keep it rare), it seeds a full
**Pyrocumulus Storm** (§3) — a map-wide `GameConditionDef` that raises
ambient `DryThunderstorm` commonality for its duration, i.e. the big fire
doesn't just make its own storm, it makes the whole savanna more likely to
catch. Rare enough that when it happens, the player remembers it.

**No C# required** for Stages 0–1. Stage 2 wants a small `GameConditionDef` +
`GameCondition` subclass to scope the lightning-rate boost to a tracked region
(vanilla `GameCondition`s are map-wide) — precedented by how `Flashstorm`-class
conditions already localize their strikes. Stage 3 is pure XML on top of
Stage 2's detection.

---

## 2. Fire-emergent creatures — lifecycles that NEED the burn

The owner's question was specific: not "creatures that live in a hot biome"
but creatures whose **life cycle requires ignition**. Four, sized and roled
so they read as an ecosystem rather than four unrelated monsters.

### 2a. Cinderclutch — eggs that hatch at ignition temperature

**Size: small (rabbit-to-cat).** **Aggression: none — it's a hatch event, not
a predator.** A ground-nesting creature (a Pyrelands adaptation, not a new
species from nothing — reskin/repurpose an existing small-fauna template) lays
a clutch of eggs each season in the standing grass. The eggs are inert,
fire-resistant shells that **do nothing until the fire front reaches them** —
then the heat itself is the hatching trigger, and a clutch of juveniles boils
out of the ash *during* the burn, already mobile, feeding on the flash of
insect life the fire is flushing out of the grass ahead of it.

- **Mechanically:** a `ThingDef` (inert egg-cluster prop, like a fungus patch)
  seeded on burn-scar terrain during the growing season; a light trigger
  converts a burning egg-cluster tile into 2–4 juvenile Cinderclutch pawns —
  vanilla fire-and-plant interaction partially supports "burns → spawns"
  already. **Needs C#** only if that pathway can't be hooked to spawn a pawn
  rather than just destroy the prop — worth a spike before committing.
- **What it drops:** nothing on the juvenile. Adult survivors found away from
  fire drop a **fire-resistant hide** — the tanning hook for §4/§6 gear.
- **Why it matters:** proof, on first sight, that *something wants this fire
  to happen* — the Pyrelands reads as an ecosystem with its own agenda, not
  just a hazard.

### 2b. Silhouette-hunter — a predator that reads flame-light, not scent

**Size: medium (large dog-to-boar).** **Aggression: ambush, ranged-shy,
melee-committed.** Nocturnal-adjacent but not literally nocturnal — it hunts
by the light of an active burn, because a fire-lit map is the one time
everything else on it is backlit and easy to silhouette. It does not hunt in
daylight or in the dark; it hunts **against the fire**, using the burn as its
own light source to spot prey (including the player's colonists) moving
between it and the flame front.

- **Mechanically:** a hunting-behavior tweak so detection radius and
  manhunter-trigger sensitivity scale with **nearby fire cell count** rather
  than light level — the one creature that gets *more* dangerous the bigger
  the fire gets, taxing the "burn it for the reward" strategy (§4) with real
  risk. A small Harmony patch on its predator-hunt job weighting toward
  fire-adjacent tiles; cheaper v1 fallback is a flat `aggroRadius` bonus keyed
  off a per-tile "near fire" check.
- **What it drops:** a **flame-adapted pelt** and a rare **ember-gland**
  trophy — a specific, ownable hunt rather than generic meat.
- **Beast-role thinking:** the roster's answer to "what makes farming the fire
  dangerous rather than merely inconvenient" — it punishes staying near your
  own burn.

### 2c. Ember-swarm — a weather-linked insect bloom, not a pawn kind

**Size: swarm/VAST-adjacent (per `setting_physics.md` Part 5 — a weather-linked
world object, not an animal on the bestiary).** Not aggressive in the raid
sense; hazardous by presence. A rising column of actual burning particulate
and disturbed insect matter that a big fire throws into its own convection
column (Stage 2's Pyroconvective Cell) — visually and mechanically an ember
cloud that drifts downwind of an active large burn and **ignites anything
flammable it passes over**, extending the fire's reach beyond the contiguous
burn line.

- **Mechanically:** modeled the sandworm way — no `<race>`, a `ThingDef`/world
  object riding the Pyroconvective Cell condition, with drift AI (wind
  direction + convection center) and a flammability check each tick it passes
  over a cell. Intentionally *not* a creature the player fights — you cannot
  kill weather, only evacuate its path.
- **What it "drops":** nothing directly; its payoff is a wider, richer burn
  scar (§4) than the fire alone would have made, at the cost of the fire
  spreading somewhere the player didn't plan for.
- **Why it matters:** the owner's "special weather event" and "creature that
  emerges in the fire" answered by the same object — the ember-swarm *is*
  weather that behaves like a beast, the VAST-tier precedent Part 5 already
  establishes.

### 2d. Slagback — a slow armored grazer that IS a walking hearth

**Size: large (megafauna tier, per R-H2's gigantism).** **Aggression: passive
unless cornered; territorial around its own smolder.** The signature creature
of the proposal. A slow, heavily armored grazer (ablative hide, per L11 —
desert megafauna are naturally thermal-resistant) that doesn't merely tolerate
fire, it **carries a bed of slow-burning material in a dorsal hump or shell
cavity**, permanently smoldering at low intensity, which it uses to pre-cook
and soften the tough, ash-fertilized grass (R-H5) it grazes — a literal walking
compost-and-hearth.

- **Mechanically:** needs a small C# comp (`CompFirebearer`-style) giving a
  permanent, non-damaging fire-graphic + light/heat emission, and periodically
  igniting standing grass under its resting spot without the creature ever
  taking fire damage itself — vanilla renders burning pawns already, but never
  as a survivable, permanent state. Resting spots become small, deliberate
  ignition points: the Slagback is a *slow, mobile fire-starter*, which gives
  the Deep Desert Tribes (§5) something to escort and follow, not just hunt.
- **What it drops:** the best payoff on the roster — armor-grade ablative
  hide, a rendered tallow product, and its ember-organ as a **portable coal
  source** (quest-flavor, not craftable — a walking heat source stays rare).
- **Beast-role thinking:** the megafauna anchor — big, slow, high-value, and
  dangerous through what happens *around* it (its rest site is a live
  ignition hazard) rather than its own attack. A literal totem animal for the
  reap-ritual: a beast that reaps nothing and burns nothing but *is* the
  fire, walking.

---

## 3. Fire-only weather — the loop made visible

All of these are `WeatherDef`/`GameConditionDef` entries gated to fire
presence or the Pyrelands biome; none change combat balance, all change what
the map is doing around the player.

**Fire whirls (localized tornado, XML-only).** Prior art: *Disasters: Tornado*
already models tornado-from-conditions. Gate a **Fire Whirl** — small, fast,
short-lived — to spawn as a rare sub-event of a Stage-2 Pyroconvective Cell
above a wind-speed threshold: it picks up burning debris and redeposits it
downwind, extending the fire's reach unpredictably. Short duration, small
radius, high telegraph (visible funnel, wind-roar cue) — per
`setting_physics.md` guardrail 6, it must be outrunnable.

**Downwind zonation — one fire, three bands.** Adapted from
`rimworld_weather_mod_concepts.md` §11, rescoped to a single map (no
world-tile propagation, per house rules): a large active burn projects three
concentric, wind-skewed bands rather than one uniform hazard. **Near** (the
Ember-swarm's territory, §2c): burning debris, high ignition risk. **Mid**:
Heavy Smoke — reduced sight range and a breathing-irritant debuff, no
ignition risk of its own. **Far downwind**: Ashfall, which is where §3's
Black Rain and Ember Snow (below) actually land. This turns "a fire is
burning somewhere on the map" into a readable wind-shadow the player can plan
a harvest run around, rather than a flat radius.

**Ash accumulation — trace/light/heavy/deep, per §12 of the same sheet.**
Ashfall is not cosmetic-or-not; it accumulates in the same register as snow,
and the state should be legible: **trace** (cosmetic only) → **light** (minor
plant-growth penalty) → **heavy** (movement slowed, solar-panel output
dented) → **deep** (plants smothered, paths need clearing). This gives Ember
Snow (below) a mechanical spine instead of being pure atmosphere, and it
means a burn scar's aftermath is a real, walkable terrain state the player
manages, not a texture swap.

**Black rain — the ash storm, and the one time it "rains."** R-H1 forbids
ordinary rain almost everywhere; the exception is **after**, not during, a
large burn: a Pyroconvective Cell or Pyrocumulus Storm (below) can resolve
into **Black Rain** — a short, filthy, non-hydrating downpour of ash-laden
condensate that blackens everything, cuts visibility, and (the mechanical
hook) is what actually **extinguishes** the fire. It also does the ash
sheet's §12 slurry step: heavy/deep ash caught in Black Rain turns to
fast-clearing slurry rather than staying a lasting movement penalty, so the
punctuation mark is legible top to bottom: ignition → storm → burn → black
rain → slurry → clear ground. `WeatherDef` with a heavy particulate overlay
(reuse `AB_VolcanicAsh`'s visual language, already in the modstack per
R-H0's volcanism).

**Ember snow.** The Ashfall band's quiet aftermath at the Pyrelands' cooler
margins (tidally-locked world, so "cooler" reads as arc-distance, not time of
day — R-H10): fine, still-glowing particulate drifts down like snow once a
burn has mostly died, settling per the ash-accumulation ladder above.
Mechanically light beyond that — a low, ongoing fire-restart chance wherever
it settles on unburned fuel, keeping a "finished" scar honest: it can
restart, quietly, days later. Pure `WeatherDef`, no C#.

**The tell before the burn.** Per `rimworld_weather_mod_concepts.md` §24: big
wildlife move before a firestorm the way real animals move before real ones.
A visible pre-burn migration of Pyrelands megafauna (Slagback herds included,
§2d) reads as a free, diegetic warning shot — the player who watches the game
for it gets advance notice of a Stage-3 escalation without a UI element.

**Pyrocumulus storm — the loop's top gear.** The Stage-3 regional escalation
from §1: a full-map `GameConditionDef` triggered only by a large enough
contiguous burn, raising ambient dry-thunderstorm commonality planet-wide (or
biome-wide) for its duration and visibly building a towering cloud-column
graphic over the fire's location, visible from anywhere on the map. This is
the "special weather event that only occurs during the fire" stated as
plainly as possible: **the storm is the fire's own exhaust**, and it seeds
more of itself. Rare by threshold-gating, not by dice — the player should be
able to see it coming by watching how big their own fire has gotten.

---

## 4. Reasons to be there — harvest windows and drop-ins

**Scorch-fruit — opens only in flame.** A plant/pod that is inert and
worthless unburned; its casing requires ignition heat to crack. The harvest
window is **during the burn or in the minutes after**, on the scar, before
Ember Snow or Black Rain seals it back into ordinary soil — the best yield on
the map, time-locked to the single most dangerous window on the map. `Plant`
with a fire-triggered yield swap, precedented by vanilla's existing
scorched-ground harvest hooks; the new part is gating harvest to "`Fire`
active on this cell, or within N ticks of it."

**Fire-glass fulgurites — where lightning struck.** Every dry-lightning
strike on sand-adjacent ground (the Pyrelands margin toward true desert,
R-H9's tar-pit interspersion) has a chance to drop a small, fused-glass
fulgurite prop — hooked straight off the lightning-strike event: check the
underlying terrain, roll to spawn a mineable node. Low value individually,
satisfying to collect, and it turns "a storm just passed through" into "go
see what it left" — a pure exploration reward for having survived being
nearby, no combat attached.

**The reap-ritual's yield, made literal.** Per `canon.yml`
`deep_desert_tribes.fire_identity_src`, the Deep Desert Tribes light fires to
"burn away the life and reveal the food: take the scorched fruits and seeds
that remain and move on." Scorch-fruit IS that yield, mechanically — a player
who understands the loop can run the Tribes' own play: light a controlled
burn on a scar they intend to return to, then harvest scorch-fruit and
fulgurites off the aftermath.

**Creatures only present mid-burn.** Cinderclutch juveniles (§2a) and the
Silhouette-hunter's active hunting behavior (§2b) only exist/activate during
a live fire — the fire itself is a spawn condition, the same way a raid or a
caravan is. "Avoid the fire" becomes "time your visit to the fire."

**An incident that drops cargo into the burn zone.** A cargo pod, crashed
vehicle or fleeing NPC caravan whose landing site is weighted toward active
or recent Pyrelands scars (reusing the existing ship-part-crash/transport-
pod-crash incident family, retargeted). Something valuable just landed
somewhere you don't want to walk into right now, on a timer, while
scavengers converge on it too — the classic risk-window incident shape,
reskinned onto this loop with no new incident category, just biome-weighted
site selection on an existing one.

---

## 5. The Deep Desert Tribes as observable fire-farmers

`hydrology_and_fire_ecology.md`'s "Who survives a savanna" table names
strategy ③ — burn it first, farm the fire — as "the one to build," and
`canon.yml`'s reap-ritual entry gives it theology: fire is the warrior/hunter
side that reaps, distinct from the water-priest side that reveres. This
proposal treats that faction behavior as **observable**, not just described:

- **Controlled burn fronts as a visible faction action.** The Tribes should be
  seen, periodically, setting deliberate fire lines on their own territory —
  a caravan-adjacent `LordJob` where a Tribe party walks a line and ignites it
  with the same primitive the player's own firestarter tools would use. The
  player who watches this happen learns the loop by example before ever
  lighting a fire themselves.
- **An unplanned burn reads as an act of war.** Per `ownership_settlement_spec.md`'s
  claim/perception fabric: a fire the player starts that crosses into Tribes
  territory, witnessed by Tribe pawns or their ambient surveillance, is a
  `TakingEvent`-shaped violation — not theft of an object, but theft of
  *their reap*. It propagates through the same faction-record pipe as a
  stolen good — cooling relations, a confrontation party, potentially a raid,
  read from the record, never a UI meter (that spec's ruling 6) — applying
  the already-ruled fabric to fire instead of goods, no new mechanism.
- **Why the sand-camps make sense.** Canon's addendum — *"it doesn't burn.
  That's safety"* — is free scenery once the scar/standing-grass distinction
  exists: Tribe camps on bare sand are provably outside every fire hazard
  here, a detail the player notices without being told.

---

## 6. What the player gets — firefighting and firebreak tools

Prior art (Fire Extinguisher, Firefoam Things — launcher/sprayer/grenades that
douse and lay temporary firebreaks) is directly portable, reflavored as
**salvaged, improvised** Jawa kit rather than clean Imperial gear — contrast
strategy ④'s ceramite firebreaks, the expensive industrial answer.

- **A handheld foam/retardant sprayer** — reflavor of the existing firefoam
  primitive, craftable early and cheaply so the scorch-fruit window (§4) is
  reachable without losing a colonist to it.
- **A layable firebreak line** — a temporary, consumable foam-sprayed strip
  rather than a permanent structure, matching the Tribes' own burn-line
  practice and letting the player stage a controlled burn on their own
  schedule, the way strategy ③ does.
- **No permanent sterile-scar firebreak for the player** — that stays
  strategy ④'s signature; giving it to the player would flatten the
  four-faction answer table into one answer.

---

## Build ladder

**v1 slice.** Strip rain from the Pyrelands table, crank `DryThunderstorm`
(pure XML, §1 Stage 0). Ship Black Rain to follow and extinguish any
sufficiently large fire, plus the ash-accumulation ladder (§3). Ship
scorch-fruit's fire-triggered harvest window and fulgurites off lightning
strikes (§4, mostly XML). Ship the firefoam sprayer + layable firebreak line
(§6). Proves the loop and gives the player a reason to walk into it — no new
creatures, no C# beyond a light lightning-strike-spawns-prop hook.

**v2.** Add the Pyroconvective Cell localized-lightning condition (§1 Stage 2,
small `GameCondition` C#), downwind zonation (§3), and Cinderclutch (§2a,
burn-spawns-pawn hook). Add the Tribes' observable controlled-burn behavior
and unplanned-burn-as-violation event, wired into the already-ruled
ownership/perception fabric (§5) — mostly data once
`PROPERTY_FABRIC_BUILD_1` lands. Add Fire Whirls as a rare Stage-2 sub-event.

**Dream.** Pyrocumulus Storm regional escalation (§1 Stage 3), Ember-swarm as
a weather-linked world object (§2c, sandworm-precedent C#), Silhouette-hunter
with fire-proximity-scaled hunting AI (§2b), and Slagback as the megafauna
centerpiece with its permanent-ember body comp and pre-burn migration tell
(§2d, §3) — the full roster that makes the Pyrelands read, on sight, as an
ecosystem built around fire rather than a grassland that occasionally
catches.
