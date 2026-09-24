# Weeping Stones — "Make It Shine" Option Portfolio (2026-09-24)

Status: ⚖️ RULED 2026-09-24, owner typed verdicts on all five. This head is the record; the option bodies below are the drafts those verdicts judged.

## ⚖️ Verdicts (owner, typed, 2026-09-24)

1. **THE STOCKED POOL — GREENLIT, expanded.** Verbatim: *"love it. Moisture
   farmers specializing in fish. Ripe possibilities for rimcuisine stuff too.
   Make the fish nasty and way too active. And some shouldn't be fish but
   alien beasts you really wonder if we should be eating."* → item
   `WEEPING_STONES_FISH_HUSBANDRY_1`.
2. **THE BORN AND THE DYING WATER — DEAD.** Verbatim: *"nah too much."* Not
   deferred; do not revive.
3. **THE MACHINES THAT WEEP — REDIRECTED** into oasis-maker machines.
   Verbatim: *"let's try for machines that create oases slowly when placed
   near shaded terrain near rocks. Placement is key. We should guide it with
   green red area selections. Like placing water based generators. I know
   there was a mod that used to grow terraforming slowly so we could base it
   on that. Makes obtaining the ancient machines a treasure type.
   Unfortunately it's not very important for the Jawa utinni scenario but
   it's a nice mod component. We would need to weave it into some quests to
   obtain or sabotage them."* (Base identified — CORRECTED same sitting: the
   slow-terraforming mod on disk is **Fertile Fields 1.6**,
   `jamaicancastle.RF.fertilefields`, workshop 3225843229; its stepwise
   terrain-ladder pattern is the study base, license unstated so pattern
   only. `TerramorphArtOverride` is our own art override for the Alpha
   Animals creature `AA_Terramorph` and has nothing to do with terraforming.)
   → item `OASIS_MAKER_MACHINES_1`. The four-state restorable-vane draft below is
   superseded by this redirect.
4. **WIND-HOUR — DEAD.** Verbatim: *"nah."*
5. **THE ONE LAW — REDIRECTED to animal retribution.** Verbatim: *"I like
   that anyone fighting including raiders attacking you near the water get
   animal retribution. That's cool. Like the existing animal mind control
   architect but baked into the biome. Don't fight back and the creatures
   will fight for you. Unless rimworld can tell 'who started it?' If they can
   then it doesn't even need to be 'don't fight back'. We should check that."*
   ✅ CHECKED same sitting (RimSage, decompiled source): the engine CAN tell —
   `DamageInfo.Instigator` + `InstigatorGuilty` per hit (undrafted
   self-defense is not-guilty: `Bullet.cs:22`, `Verb_MeleeAttackDamage.cs:50`),
   `Trigger_PawnHarmed` filters by instigator faction, `Faction.cs` detects
   mutual crossfire, `Hediff_Shambler.cs:239` shows targeted retaliation. So
   "don't fight back" is NOT needed — retribution keys on the first guilty
   hit inside the truce radius. → item `WATER_TRUCE_RETRIBUTION_1`. The
   neutral-ground/diplomacy draft below is superseded by this redirect.
Companion to: `weeping_stones.md` (frozen sheet), `weeping_stones_flora_roster_2026-09-24.md`, `weeping_stones_fauna_roster_2026-09-24.md`.

## 1. Comparative assessment — where Weeping Stones stands

| biome | flagship identity (what a player retells) |
|---|---|
| Sump | tar industry + tar-beast set-pieces, dig-lottery, vermin telegraphy |
| Fever Wood | the Tenant — a map-spanning hidden aquifer entity; mirror pools |
| Rust Cathedral | hum-mood system, living bolts, eel-fishing, wall-tier mining |
| Webwork | shokkweave monopoly economy, web structures, egg blackmarket |
| Miasma | the moving salt-line/surge axis; fever-forged boons |
| Forge | boiling-rain weather, beldon herds + tibanna harvest, vapor-column flight |
| Scald | steam-catch industry, margin fishing, geysers, bubble-sailors |
| Cracked Lands | the witnessed flood event + explosive growth |
| Lantern Deeps | the darkness pocket-map layer |
| Deserts | the moving dunes engine |
| Greentide / Pyrelands | living regrowth / fire ecology |
| **Weeping Stones** | **a superb frozen FICTION (truce, succession ladder, sacred ambiguity, wind-hour, 186 hand-placed landmark oases) and two freshly ruled rosters — but no flagship MECHANISM of its own yet** |

Where it is honestly thin: it is the only mature biome in the set with **no kit
spec** — `design/Jawa/worldbuilding/biomes/kits/` holds twelve sister specs and
nothing for the Weeping Stones — and correspondingly **no C# it owns**: every
comp cited in today's rosters is borrowed from CreatureBehaviors,
EnvironmentalHazards or FlowWorks, built for other biomes. Its fishing is one
candidate row (`RM_Murrin`) explicitly carried away to `FISH_BY_BIOME_1`; its
signature weather (fog at wind-hour, §10b) and its sound register (aeolian
chords, the silent dead oasis) exist only as sheet prose with no weather/ambient
defs; and the landmark loadouts are placed but their in-map payoffs (the dead
ring, the fog-wild array) are undesigned. The rosters gave it a cast; nothing
yet gives it the *thing you do here that you can do nowhere else* — which is
exactly what the sheet's own §5/§8 material is sitting on.

## 2. The five options

### Option 1 — THE STOCKED POOL (aquaculture / tended fishing)

**Question it answers:** what is fishing HERE, that is neither the Scald's
stand-at-the-margin catch nor the Cathedral's industrial line? Answer: fishing
as *gardening* — the only place on the planet where the fish are something you
raised.

**(a) The fantasy.** A pool is a working thing (§1), and the murrin are part of
the works. A wild pool holds a thin wild stock; a *tended* pool is stocked,
fed, and read — the comb-fins cutting rings at wind-hour are the pool telling
you it is well. A colonist who nets a murrin from a strange oasis carries it
home in a wet skin, and three seasons later their own water is alive. And a
pool gone silent — no rings — is the first word of trouble, before the green
ring even starts to brown.

**(b) What the player does.**
- Nets breeding stock at wild oases and *stocks* their own pool (a carry-job to a pool cell).
- Feeds the stock — mirrik cocoon waste / bladder-fruit scrap thrown to the water on a schedule.
- Reads pool health at a glance: ring density on the water IS the stock gauge (art states, no inspector-diving).
- Harvests sustainably or overdraws: fish above the replacement rate and the stock crashes for a year.
- Guards the stock — pilgrims' herds drink, but a kirruk or a visiting Ollopom crowd will skim an untended pool.

**(c) Reuses already built.** The whole biome-side fishing surface exists:
`src/RimMandrake/SeaShores/Source/RM_SeaShoreExtension.cs` (opt-in DefModExtension — a
biome carrying one IS fishable, no whitelist) and the Scald's `fishTypes
MayRequire Odyssey` precedent. The population model is
`src/RimMandrake/CreatureBehaviors/Source/RM_CompVerminBreeder.cs` +
`RM_MapComponent_VerminPopulation.cs` — a per-map stock that breeds, caps, and
crashes, built for the Fever Wood grubs; a pool stock is the same math wearing
fins. `RM_MapComponent_SilenceCue.cs` (CreatureBehaviors) is the built "the
absence is the signal" register for the silent pool.

**(d) New build: M.** A `RM_MapComponent_PoolStock` keyed to contiguous
pool-water bodies, the stocking/feeding jobs, and ring-density art states. The
honest hard part: **defining "a pool" as a discrete entity** — contiguous
water-terrain regions must be identified, tracked across terrain edits, and
scribed; nothing built does per-body bookkeeping on map water (RM_LiquidBody
does it for excavations, not natural terrain — its region logic is the pattern
to steal, not the object to reuse).

**(e) Unique contribution.** The only fishing on the planet where the yield is
a function of the player's husbandry rather than of what nature put there —
fishing as agriculture, and the pool's health made readable at a glance.

**(f) Validity floor.** No rain (stock feeds on thrown scrap and the pool
itself); no ambush-at-water (predation on stock is skimming by drinkers, never
a margin hunter); truce v1 untouched; murrin *species* selection stays owed to
`FISH_BY_BIOME_1` as ruled — this option is the mechanism around whatever that
lane casts; no worldgen, no painting.

### Option 2 — THE BORN AND THE DYING WATER (oasis life-and-death stewardship)

**Question it answers:** §8's succession ladder is prose — can the map's heart
actually be CREATED and KILLED by the player? No other biome lets the player
make the biome's own centerpiece.

**(a) The fantasy.** Every oasis is tended (§5), and tending runs both ways. A
burrak's abandoned dig holds a skin of wet; a colonist who cuts it deeper,
stands a condenser fin over it and keeps the crowd from fouling it will watch
a green ring assemble itself over seasons — a new oasis, theirs, that pilgrim
lines begin to bend toward. And the same ledger runs backward: draw harder than
the wind delivers and the rings recede from the outside in — sand, then scrub,
then the browning green, then the silent water — until the map holds a dead
ring with your settlement in the middle of it.

**(b) What the player does.**
- Starts water: digs a catch-basin (or claims a burrak dig — the animal is the biome's own contractor).
- Grows it up the ladder: fin → shield → shade-lid → enclosure, each rung cutting the loss side of the budget.
- Reads the budget: the concentric rings ARE the gauge — the ring edge creeping in or out is the ledger made terrain.
- Overdraws at a price: heavy irrigation of dewgourd fields, big tame herds, and generous visitors all debit the same stock.
- Kills or rescues: a fouled or overdrawn pool dies by visible stages, and each stage is still reversible at rising cost — until the truce-break scuffle at the last of it (§4's one sanctioned violence, as an event).

**(c) Reuses already built.** This is the option FlowWorks was accidentally
built for: `src/RimMandrake/FlowWorks/Source/RM_LiquidStock.cs` is a stock model with
"sticky-limitless classification, **recession from the outside in**, and refill
from seepage, rain and season" — recession-from-the-outside-in is the
concentric rings dying, verbatim; `RM_MapComponent_Excavation.cs` +
`Designator_DigCanal.cs` are the digging; `RM_MapComponent_SubsurfaceLiquid.cs`
(FlowWorks/Drilling) is the seep-oasis feed from below. Ring die-back/regrowth
is `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_LivingRegrowth.cs`
(terrain-gated regrowth, Greentide) run against a moving gate. The burrak dig
is `RM_CompDungSeeder.cs`'s leave-something-behind pattern.

**(d) New build: L.** The wind-income source term (condensation credit keyed to
weather/wind-hour instead of rain), the ring-state terrain/plant cascade, the
death-and-rebirth staging, the truce-break event. The honest hard part:
**pacing the death so it is a story, not a gotcha** — the budget must fail in
legible, reversible stages over seasons, with the murrin rings (Option 1) and
the browning ring edge as early warnings, or the first dead oasis reads as a
bug and the feature is hated.

**(e) Unique contribution.** The only biome where the player can create and
destroy the biome's own centerpiece — the map's sacred object is a savings
account with terrain for a balance sheet.

**(f) Validity floor.** 🔴 R21 names the one config trap: `RM_LiquidStock`'s
**rain refill term must be ZERO here** — income is seepage + wind-condensation
only; a default-carried rain credit would violate the sheet silently. Truce v1
untouched (the scarcity scuffle is the sheet's own §4 carve-out, an event, not
a behavior rewrite); creating an oasis is map-scale terrain work — no landmark,
no worldgen, no planet edit; §6 toll ban unaffected (settling your own water is
the legal claim, per §4).

### Option 3 — THE MACHINES THAT WEEP (the ancient vane arrays)

**Question it answers:** §9's sacred ambiguity — is the machine alive? — as a
mechanical register: restorable ancient water infrastructure, distinct from the
Cathedral's hum (which is attitude/mood about a place; this is *water income*
plus reverence about an *act*).

**(a) The fantasy.** The ancients found the best traps and built on them, and
ages sorted their works into four fates: one still runs cold and true; one
leaks and made a hanging marsh; one runs half-wild and floods its canyon with
fog; one died, and its oasis is a dry ring around a silent machine (§8, rung
2). Each array sings its own aeolian chord, so you hear its state before you
see it — and when a colonist fits the last comb-vane segment and a machine
that was silent for an age starts to weep again, everything on the map that
drinks knows something changed.

**(b) What the player does.**
- Finds arrays by EAR: each state has its chord; the dead one's silence is the tell.
- Salvages OR restores — strip a dead array for comb-vane segments (§11, component-tier), or spend segments + components to walk one back up its states: dead → fog-wild → leaking → true-running.
- Owns the consequence: a true-running array is standing water income to the local budget (Option 2's ledger, if taken; a straight item-water yield if not).
- Chooses the fog-wild middle state deliberately — canyon ground-fog is concealment and dew both.
- Answers who notices: pilgrims arrive at a re-woken array, the Deep Desert Tribes leave chimes, Ascendant Helix comes asking (§12) — restoring one is a planet-legible act.

**(c) Reuses already built.**
`src/RimMandrake/EnvironmentalHazards/Source/RM_CompResourceCondenser.cs` is the
exact machine — a cycle-yield condenser ThingComp ("25 water units/day"
framing, a must-sit-on anchor def field) built for the Scald's vents; the vane
array is this comp on a ruin building with a state ladder in front of it.
`RM_MapComponent_ProximitySoundscape.cs` and `RM_MapComponent_SilenceCue.cs`
(CreatureBehaviors) are the built proximity-audio and meaningful-silence
registers — the aeolian chords ride them. Fog-wild's ground fog has the
`RM_MapComponent_VaporColumns.cs` (Forge) column-emission pattern to copy.
`RM_Verdimoss` (flora roster row 3) is already specified as the relic-dresser.

**(d) New build: M.** The array as a multi-cell ruin ThingDef with four scribed
states, the restore job chain, the state-transition events, four ambient
chords. The honest hard part: **making the four states READ** — fog-wild must
visibly fog, the hanging marsh must be wet terrain, the dead ring must be a
dead ring at map-gen — which is per-state map-side work (a GenStep dressing
pass per state, `RM_GenStep_PlacedSetPieces.cs` in EnvironmentalHazards is the
placed-set-piece precedent), not just a def field.

**(e) Unique contribution.** The only content anywhere that turns a RUIN into
a working piece of the biome's own engine — reverence attached to
infrastructure repair, with the map's water budget as the reward.

**(f) Validity floor.** Arrays comb wind, never rain (R21 native); restoring
one is map-scale (the 186 world-map landmark placements are CLOSED and
untouched — this designs what a landmark's *map* contains, adding nothing to
the planet); no toll mechanics (§6 — the array waters its OWN oasis); sacred
ambiguity stays ambiguous: no ruling is forced on whether the machine is
alive, the events only ever say what visitors believe.

### Option 4 — WIND-HOUR (the daily communal ritual)

**Question it answers:** every sister biome's signature weather is a stochastic
storm or an event; can a biome run on a CLOCK — a daily, watchable, joinable
choreography that the whole map keeps together?

**(a) The fantasy.** Once a day the damp flow peaks and the high country goes
into cloud at ground level (§10b). The weep-faces darken first — the wet black
streaks spreading on pale stone — then the mirrik come up off the pools like
smoke flowing the wrong way, the sillik stipple the wet faces, the vellak
lines crest the rim with sail-combs fanned, every animal walks its drinking
rotation, and for one hour the biome does its actual living. Then the wind
dries, the combs are licked clean, and the country goes back to glare and
stillness. Travelers plan around it. Colonists step outside for it.

**(b) What the player does.**
- Plans work around the clock: condenser fins and vane arrays pay out AT wind-hour — the water economy has a payday.
- Attends: a pawn at a pool or truce-stone during wind-hour takes a real mood/recreation payoff — the ritual is joinable, not just scenery.
- Harvests the hour: mirrik cocoon gathering, salvecomb cutting and murrin netting are wind-hour-windowed jobs — the biome's gathering day.
- Fights the hour or hides in it: ground fog cuts sight lines for everyone; a raid that arrives at wind-hour is a different fight.
- Reads the biome's health by it: a weak wind-hour (thin fog, no rings, silent faces) is the drought klaxon for Options 1/2.

**(c) Reuses already built.** The scheduled-cycle skeleton exists twice:
`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_FlashCycle.cs` (the
Cracked Lands' clocked event cycle) and `RM_MapComponent_GradientAxis.cs` +
`RM_GameCondition_GradientSurge` (the Miasma's map-state axis + condition);
`RM_GameCondition_WeatherPulse` is a built weather-pulse condition to model
the fog hour on. `RM_MapComponent_ShadeGrid.cs` (CreatureBehaviors) already
knows the cold faces — the darken-first pass reads it. Swarm timing is an
activity window on `RM_MapComponent_VerminPopulation.cs`; the soundscape rides
`RM_MapComponent_ProximitySoundscape.cs`.

**(d) New build: M.** One `RM_MapComponent_WindHour` clock owning the
choreography, a fog-at-ground WeatherDef + daily forced transition, the
attend-the-hour joy/mood hook, job-window gating on 3–4 defs. The honest hard
part: **RimWorld's weather is built to be random** — a daily deterministic
weather seizure has to coexist with the vanilla WeatherDecider (force,
restore, don't fight storms from other sources), and the hour must not become
a tick-cost pileup when six systems all key one clock.

**(e) Unique contribution.** The only daily RHYTHM on the planet — every other
biome's signature sky is something that happens TO you; wind-hour is a
standing appointment the player can build an economy and a social life around.

**(f) Validity floor.** The fog is condensation at ground level, not rain —
R21 is the premise, not a risk; no snow weather touched (§6); drinking
rotation is spawn/flavor choreography on top of truce v1, not a new behavior
adjudication; purely map-scale — no worldgen, no painting, no landmark edits.

### Option 5 — THE ONE LAW EVEN ENEMIES KEEP (the sacred-water social contract)

**Question it answers:** the truce is ruled for animals (v1 accepted
2026-09-24); does it bind PEOPLE — neutral ground on the player's own map,
with teeth when the player breaks it?

**(a) The fantasy.** Eventually all cultures respect it here, even those from
far away with very different ideas of morality (§4). So a raid crossing your
map walks WIDE of your pool; a hostile party and your own haulers water thirty
paces apart in silence; pilgrim caravans bend their route to your oasis and
leave Oomo tokens at the truce-stone, asking nothing. And the day a colonist
opens fire across full water, everything changes: the animals stop turning
their backs, the tribes' chimes disappear, and the desert knows your water is
the kind where the one law doesn't hold.

**(b) What the player does.**
- Holds neutral ground: hostile and neutral parties water unmolested inside the truce radius — and so, there, does the player.
- Profits from sanctuary: pilgrim visits at a well-kept pool bring tokens, trade, goodwill drips, and recruitment-flavored social events — the water is a diplomatic engine.
- Chooses to break it: violence on pool ground WORKS (no invisible wall) and costs — faction goodwill across every local faction, a lasting "oathbreaker water" map-state that thins pilgrim traffic and hardens taming/bonding at the pools, Deep Desert Tribes retribution.
- Earns it back slowly: seasons of unbroken truce (and Oomo tokens laid) walk the state back.
- Reads visitors correctly: a Blackstar team watering quietly, a Geonosian column NOT stopping — §12's omens become live tells the player learns.

**(c) Reuses already built.** The radius machinery is
`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_DreadField.cs` + the
avoid-field JobGiver pattern (the Sump), which truce v1 already plans to
invert for predators — people ride the same field.
`RM_TenantTruceExtension.cs` (EnvironmentalHazards) is the built
truce-marker DefModExtension pattern. Goodwill, visitor lords and gift events
are vanilla Lord/Faction API; the truce-stone and Oomo token are already
sheet-specified items (§11).

**(d) New build: L — and honestly the riskiest.** Raid-AI carve-outs are the
hard part named plainly: **hostile LordToil pathing must respect pool ground
without the pool becoming an exploitable pan-map panic room** — raiders must
route around, wait at the margin, or besiege, never stand down because a
colonist kited them to water; every duty type (sapper, breacher, drop pod on
the pool) is an edge case. The reputation/map-state side is cheap; the raider
dance is where the size lives.

**(e) Unique contribution.** The only neutral-ground gameplay on the planet —
every other biome's flagship is between the player and nature; this one puts a
LAW on the map that binds every faction including the player, and makes
keeping or breaking it the story.

**(f) Validity floor.** Builds ON truce v1 (animals, ruled 2026-09-24) without
reopening it — this is the human layer the sheet's §4 already asserts in
fiction; §6's toll ban is actively enforced by it (the oathbreaker state IS
the barbarism made costly); no ambush-at-water content; violence at scarcity
stays the one sanctioned break (§4); map-scale only.

## 3. Recommendation

**Take Option 2 first and Option 3 with it** — they share one spine
(the water budget: FlowWorks' `RM_LiquidStock` already implements
recession-from-the-outside-in, and the vane array is the built
`RM_CompResourceCondenser` given a soul), and together they turn the sheet's
two most-loved sections (§8 ladder, §9 ambiguity) into the planet's only
create-and-kill-the-centerpiece play. The trades, one line each: **Opt 1**
buys a unique fishing answer for a new pool-entity bookkeeping cost;
**Opt 2** buys the biome's whole identity for the largest build and a pacing
risk (death must be a story, not a gotcha); **Opt 3** buys ruin-into-engine
magic cheaply but needs per-state map dressing to land; **Opt 4** buys the
planet's only daily rhythm at the cost of fighting the vanilla weather
randomizer; **Opt 5** buys the strongest fiction (neutral ground) at the
highest AI-fragility risk — best taken LAST, on top of a biome already worth
being neutral in. If only one cheap winner is wanted, Option 4 is the most
spectacle per unit build.

---

_No slot was swapped: the five briefed questions survived contact with the
code census — each found real distinct machinery to stand on, and no stronger
distinct question emerged. Compiled read-only; nothing filed, nothing
committed. Comp/mapcomponent names verified against
`src/RimMandrake/*/Source/*.cs` on 2026-09-24; the absence of a Weeping Stones
kit spec verified against `design/Jawa/worldbuilding/biomes/kits/` (twelve
sister specs, none for this biome)._
