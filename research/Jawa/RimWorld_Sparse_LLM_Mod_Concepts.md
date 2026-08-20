# Sparse-LLM Mod Concepts for a Star Wars RimWorld Scenario

## Core Design Goal

Use LLMs **sparingly but at high leverage**.

The LLM should not continuously run the simulation, micromanage pawns, perform pathfinding, or make constant tactical decisions. Instead:

> **RimWorld computes facts; the LLM interprets them; C# validates a small structured response; deterministic RimWorld systems enact the result.**

This keeps:
- API/query requirements low
- latency largely irrelevant
- behavior predictable and debuggable
- implementation practical in Claude Code
- the apparent intelligence of the game high

A useful architecture is:

```text
Game State
    ↓
Compact Context
    ↓
LLM
    ↓
Validated JSON
    ↓
RimWorld Mechanics
```

Example compressed colony state:

```text
Colony:
7 Jawa, 3 droids
food 4.2 days
water critical
components 11
ship launch deadline 5.8 days
gravengine damaged
research: moisture vaporator 63%
combat readiness: poor
Junkers hostile, recent raid 1.3 days ago
Tusken relations improving
current threats: heatwave
construction bottleneck: steel
idle capability: 2 hauling droids
```

Example output:

```json
{
  "urgent": [
    "Finish moisture vaporator",
    "Cancel nonessential steel construction",
    "Send R4-K9 to haul components indoors"
  ],
  "nearTerm": [
    "Repair gravengine",
    "Acquire 120 steel",
    "Improve south perimeter"
  ],
  "strategic": [
    "Prepare for departure",
    "Develop Tusken trade relationship"
  ]
}
```

One call can remain valid until something significant changes.

---

# 1. Jawa Foreman's Board

**Value:** ★★★★★  
**Ease:** ★★★★★

A ship-console or colony UI panel that continuously shows AI-generated strategic advice.

Possible names:
- Foreman's Board
- Salvage Master's Console
- Shipmind Advisory Terminal
- Clan Planning Terminal

It presents three planning horizons.

## Do This Now

Examples:

- Stop making Jawa beer; water reserves are nearly exhausted.
- Finish the moisture vaporator.
- Treat Dathcha's infection.
- Move the loose droid cores indoors before the sandstorm.

## Next

- Strip the crashed shuttle for components.
- Replace the eastern turret.
- Get the factory line producing repair plates.

## Long Game

- The gravengine must be repaired before launch.
- There is no competent backup doctor.
- The Hutt Cartel is currently the easiest source of advanced components.

The LLM does not issue orders. It interprets colony state.

### Suggested Call Frequency

- roughly once every 1–2 game days
- after unusually important events
- when the player manually presses **Refresh Advice**

This could easily result in only a few calls during an evening of play.

---

# 2. "What the Hell Is Wrong?"

**Value:** ★★★★★  
**Ease:** ★★★★★

A manual diagnostic interface.

Button:

**ASK THE SHIP COMPUTER**

Fixed questions could include:

- Why are we starving?
- What is our biggest vulnerability?
- What is wasting our time?
- Why isn't production working?
- Who needs attention?
- What should I build next?
- Are we ready to launch?
- What resource should I acquire?
- What am I overlooking?

Because the player explicitly invokes it, it costs nothing unless requested.

This is particularly suitable for enormous modlists where the underlying systems can become difficult to reason about manually.

---

# 3. The Episode Director

**Value:** ★★★★★  
**Ease:** ★★★★☆

Do not ask the LLM to invent arbitrary RimWorld events.

Instead provide a bounded library of legal story beats.

Example event vocabulary:

```text
minorRaid
majorRaid
tradeCaravan
distressSignal
missingPawn
ruinDiscovery
animalMigration
sandstorm
burrowingAttack
theftAttempt
droidMalfunction
imperialInspection
bountyHunter
factionDemand
prisonerEscape
disease
valuableWreck
falseBeacon
```

Modifiers:

```text
targetFaction
targetPawn
targetResource
entryMethod
objective
betrayal
misdirection
reward
followup
```

Every several game days, ask:

> What would make an interesting next episode given what has happened recently?

Example output:

```json
{
  "beat": "theftAttempt",
  "faction": "Junkers",
  "target": "droidCores",
  "entryMethod": "burrow",
  "twist": "falseDistressSignal",
  "severity": 0.55
}
```

The LLM chooses the combination.

Ordinary C# executes it.

This makes the LLM a narrative director rather than a runtime simulation engine.

---

# 4. Multi-Episode Story Arcs

**Value:** ★★★★★  
**Ease:** ★★★★☆

A single LLM call can generate several hours of gameplay.

Ask it to construct a 3–5 beat story arc using only implemented event types.

Example:

## The Water Thieves

1. Moisture equipment begins disappearing.
2. Jawa find evidence implicating Tusken raiders.
3. A Tusken delegation arrives indignantly claiming innocence.
4. Junker tunneling crews attack during negotiations.
5. A captured Junker reveals who paid them.

The arc is stored.

No additional LLM call is required until the arc concludes or needs revision.

Each beat triggers according to ordinary game conditions.

This provides narrative intentionality with very little model use.

---

# 5. Faction Agenda System

**Value:** ★★★★★  
**Ease:** ★★★★☆

Every quadrum, or after major geopolitical changes, the LLM assigns one or more current motivations to each faction.

## Example: Hutt Cartel

Allowed agendas:

- PROFIT
- EXTORT
- ACQUIRE_ASSET
- PUNISH
- RECRUIT
- SMUGGLE

## Example: Galactic Empire

- INVESTIGATE
- CONTROL
- CONFISCATE
- SUPPRESS
- RECRUIT
- EXTERMINATE

## Example: Jawa Trade Clans

- TRADE
- SCAVENGE
- COMPETE
- ASSIST
- STEAL
- GOSSIP

Possible generated state:

```text
Gorga the Immense:
Wants the player's factory ship.
Prefers coercion over destruction.
Interested in purchasing R-41 Rell.
```

For the next several days, deterministic systems alter event weights accordingly:

- suspicious merchants
- purchase offers
- bounty hunters
- intimidation
- favorable trade deals
- escalating demands

One LLM decision produces an extended faction personality.

---

# 6. Recurring Villains with Memory

**Value:** ★★★★★  
**Ease:** ★★★★☆

Create a lightweight **Nemesis Memory** system.

After a major encounter involving an important surviving enemy, make one small call:

> What does this character now want?

Example:

```json
{
  "attitude": "humiliated",
  "goal": "capture_Tikkay",
  "tactic": "avoid_direct_assault",
  "signature": "droid_decoys"
}
```

Store it.

The character can later behave consistently with that memory.

Update only after important events:

- defeats
- escapes
- negotiations
- betrayals
- injuries
- deaths of allies
- humiliation
- successful revenge

This can create strong apparent character intelligence without persistent simulation.

---

# 7. Droid Firmware Personalities

**Value:** ★★★★★  
**Ease:** ★★★★★

This is particularly well suited to Star Wars droids.

Invoke the LLM only when a notable droid is:

- created
- repaired
- memory-wiped
- substantially rebuilt
- upgraded in a major way

Example output:

```json
{
  "helpfulness": 0.91,
  "bravery": 0.32,
  "curiosity": 0.78,
  "literalism": 0.94,
  "selfPreservation": 0.16,
  "obsession": "doors",
  "competence": ["medical", "electronics"],
  "absurdLimitation": "will_not_cross_running_water",
  "heroicTrigger": "child_in_danger"
}
```

The LLM does **not** determine moment-to-moment behavior.

Ordinary C# interprets those parameters.

The result is a very Star Wars combination:

> Astoundingly capable machine + glaringly stupid limitation + inexplicable loyalty + slapstick behavior.

Each memorable droid becomes genuinely distinct.

---

# 8. Emergent Droid Quirks

Droids can gain new quirks based on accumulated history.

Example history:

- struck by lightning twice
- hauled 1,300 meals
- rescued Bibble
- fled five firefights
- had one leg replaced

One LLM query interprets that history.

Example result:

## New Quirk: Protective Food-Service Protocol

Behavioral consequences:

- prioritizes feeding injured Jawa
- becomes distressed by empty food storage
- occasionally delivers meals where nobody requested them
- becomes unusually brave when a starving pawn is threatened

The LLM determines **what the history means**.

Code determines what happens mechanically.

---

# 9. Adaptive Jawa Nicknames and Epithets

**Value:** ★★★★☆  
**Ease:** ★★★★★

After important events, occasionally generate:

- pawn epithets
- droid nicknames
- ship-room names
- historical incident names
- clan sayings

Examples:

**Tikkay "Three Suns"**  
Survived heatstroke three times.

**R4-K9 "Doorbane"**  
Destroyed multiple doors during firefights.

**The Soup Incident**  
The colony's remembered name for some ridiculous catastrophe.

One query can generate many candidate names at once.

---

# 10. Holonet News

**Value:** ★★★★★  
**Ease:** ★★★★★

Every 5–10 game days, generate a short Holonet bulletin.

Most stories have no direct mechanical consequence.

Examples:

> IMPERIAL CUSTOMS DESTROY SMUGGLER DEPOT AT KESSEL WAYSTATION

> GORGA THE IMMENSE DENIES INVOLVEMENT IN DISAPPEARANCE OF THREE TRADE ENVOYS

> DROID RIGHTS AGITATION REPORTED IN NORTHERN SETTLEMENTS

Occasionally, however, a story sets a small world-state flag:

```text
spicePrice +30%
Empire/Hutt goodwill -15
Droid refugees enabled
```

This creates the illusion of a large galaxy without simulating one in detail.

---

# 11. Rumor Generator

Visitors, merchants, captives, and travelers can provide rumors.

One call produces three claims:

- one true
- one distorted
- one false

Example:

> "There's an Imperial vault beneath the eastern salt flats."

> "The vault is protected by assassin droids."

> "A Jedi is imprisoned inside."

Internal truth state:

```text
vault = true
assassinDroids = partly true
jedi = false
```

This supports exploration and uncertainty without requiring complex procedural storytelling.

---

# 12. Procedural Bounty Board

**Value:** ★★★★★  
**Ease:** ★★★★☆

Every few days, generate several contracts from legal quest templates.

Input:

- nearby factions
- known pawns
- nearby sites
- player strength
- resource scarcity
- recent events

Possible outputs:

**CAPTURE:** Vex Noro, Junker slicer  
**RECOVER:** stolen astromech memory core  
**SALVAGE:** crashed customs skiff  
**ESCORT:** Hutt accountant across Tusken country

Quest mechanics remain deterministic.

The LLM provides context, flavor, targeting, and combinations.

---

# 13. Adaptive Quest Consequences

The LLM does not need to generate a quest.

It can instead decide what should follow from what the player did.

Example history:

- saved a Tusken child
- stole the reward
- killed an Imperial patrol
- abandoned the quest giver

One post-quest query could select:

```text
Tusken gratitude
Imperial suspicion
questgiver resentment
rumor spread: player dishonorable
```

Those become faction modifiers, future story flags, or event weights.

This provides moral and narrative memory without creating a large reputation algorithm.

---

# 14. Salvage with History

**Value:** ★★★★★  
**Ease:** ★★★★★

Rare salvage receives one LLM query when discovered.

Instead of:

> Excellent Blaster Rifle

the player finds:

## DT-19 "Last Argument"

> An obsolete Imperial carbine whose receiver carries three different unit inventory stamps.

The LLM selects from bounded traits such as:

- Imperial provenance
- unreliable cooling
- exceptional accuracy
- valuable to collectors
- Blackstar Company connection

Stats still come from deterministic point-budget systems.

The model chooses an interesting combination and history.

---

# 15. Archaeological Storytelling

**Value:** ★★★★★  
**Ease:** ★★★★☆

When a ruin or special site generates, make one call determining:

- who built it
- why it was abandoned
- what happened here
- what clue remains
- what unusual hazard fits
- what valuable thing may remain

Example:

> **Abandoned Jawa refinery.**  
> Workers accidentally awakened a buried tunneling organism. Survivors barricaded the south processing wing. One maintenance droid remains active.

Map generation then selects from existing modules:

- refinery tileset
- breached floors
- south barricades
- burrowing monsters
- maintenance droid
- industrial loot

The LLM does not generate map geometry.

It gives the map generator a coherent scenario.

---

# 16. Sarlacc Stomach Storyteller

Each Sarlacc could receive one generated **digestive history**.

Determine:

- whom it swallowed
- what wreckage remains inside
- what creatures remain alive
- what internal ecosystem has formed
- whether unusual mutations occurred
- what legendary treasure is rumored

The dungeon generator maps these concepts onto predefined encounter and room modules.

One query can create an entire Sarlacc dungeon identity.

---

# 17. Encounter Twist Selector

Take ordinary generated incidents and occasionally ask:

> Is there a contextually appropriate twist?

Allowed answers:

```text
NONE
SECOND_FACTION
TRAITOR
WRONG_TARGET
HIDDEN_CARGO
DISTRESS_TRAP
CREATURE_ATTACK
WEATHER_CHANGE
PRISONER_RECOGNITION
REINFORCEMENTS
SECRET_OBJECTIVE
```

A small system like this could make familiar RimWorld incidents dramatically less predictable.

---

# 18. Adaptive Trade Offers

Do not let the LLM invent prices.

Instead, let it interpret player needs and choose among valid trade mechanisms.

Example situation:

- colony desperately needs components
- enormous surplus of fermented bantha secretion

A Jawa caravan might offer:

> 18 components for 200 fermented glands.

Or the Hutts recognize the desperation and charge aggressively.

Economics remain deterministic.

The LLM generates **intent**.

---

# 19. Dynamic Faction Negotiations

Instead of goodwill being only a number, periodically turn history into a concrete proposition.

Example:

> The Deepwater Compact remembers that you rescued Neris Cal's nephew and wants permanent salvage rights to coastal wrecks.

The player receives several legal responses:

- accept
- reject
- demand payment
- counteroffer
- betray

The LLM chooses a contextually meaningful proposal.

The game handles the mechanics.

---

# 20. AI Scene Casting

Before certain social or narrative events, ask:

> Which existing pawn relationships would make this scene interesting?

Rather than randomly selecting pawns, the system might choose:

- estranged siblings
- coward and veteran
- Hutt-hater and Hutt envoy
- droid-rights sympathizer and Imperial captive
- two pawns with unresolved rivalry
- rescuer and rescued pawn

The model chooses **who should be in the scene**, not what every pawn does.

---

# 21. Rare, High-Importance Social Dialogue

Existing LLM mods often focus heavily on frequent pawn chatter.

For this scenario, it may be more effective to use LLM conversation only for significant moments:

- reunion
- breakup
- marriage proposal
- deathbed interaction
- major argument
- rescue
- betrayal
- first encounter with a strange species
- witnessing something extraordinary
- confrontation with a recurring enemy

Routine chatter stays deterministic.

LLM dialogue becomes rare enough that it feels important.

---

# 22. Memory Compression

Every 10–20 days, or only for important pawns, compress their recent event history into a short semantic memory.

Example:

```text
Tikkay:
- distrusts Empire after imprisonment
- feels indebted to R4
- proud of killing krayt juvenile
- increasingly frustrated with Chief
- considers factory ship his home
```

Future rare interactions use this summary rather than sending hundreds of raw events.

This reduces token usage while improving continuity.

---

# 23. Colony Culture Emerging Organically

Every year or after several major milestones, ask:

> What traditions appear to have emerged from what these people actually do?

The model selects from implemented ritual mechanics and writes their meaning.

Examples:

## First Scrap

Whenever the ship lands, the first recovered mechanical component is placed beside the gravengine until departure.

## The Quiet Minute

After losing a droid, colonists briefly shut down nonessential machines.

## Red Hood Day

A ridiculous annual holiday created from some early-game accident.

The colony's culture becomes biographical rather than purely designed at game start.

---

# 24. Storyteller Commentary That Matters

The storyteller can occasionally point out a narrative or strategic motif:

> "You're depending rather heavily on that single vaporator."

That observation is then stored.

Later, the storyteller can preferentially select incidents related to the vaporator.

The commentary therefore reveals what the director considers narratively important.

It is not merely flavor text.

---

# 25. "Previously on RimWorld..."

**Value:** ★★★★★  
**Ease:** ★★★★★

One call when loading a save.

Example:

> **Previously aboard the Utinni's Fortune...**
>
> The clan escaped Mos Vara with the Empire close behind, but not before losing its primary condenser. R4-K9 saved Tik-Tik during the raid. The ship has six days before its next forced departure, and Gorga's promised payment has still not arrived.

Then:

## Open Threads

- Repair condenser
- Gorga owes payment
- R4-K9 damaged
- Empire searching region

Very cheap and disproportionately useful for long-running campaigns.

---

# 26. Automatic Session Goals

Immediately after the recap, generate:

## Tonight's Likely Goals

### Immediate

1. Restore water production.
2. Treat R4-K9.
3. Secure exposed salvage.

### Before Launch

1. Obtain 36 components.
2. Finish starboard engine repairs.
3. Decide whether to answer Gorga.

### Optional Adventures

- Investigate strange transmission.
- Trade with nearby Tusken camp.

This turns the strategic advisor into campaign UX.

---

# 27. Player-Attention Model

**Value:** ★★★★★  
**Ease:** ★★★★☆

The game already knows:

- what UI elements the player rarely opens
- which pawns are seldom selected
- ignored quests
- untouched systems
- unused buildings
- resources accumulating with no use
- technologies researched but never exploited
- animals or droids with no assigned purpose

Periodically ask:

> Are there useful or interesting parts of the game the player appears to be neglecting?

Possible result:

> **Ship computer:** "We have had a perfectly serviceable probe droid sitting in storage for nineteen days."

This is not optimization.

It is **attention management for a huge modlist**.

That could be unusually valuable in this scenario.

---

# 28. Mod-Aware "What Can I Do with This?"

**Value:** ★★★★★  
**Ease:** ★★★★☆

Select an:

- item
- creature
- building
- gene
- resource
- component

Press:

**ASK DATABANK**

The mod gathers its RimWorld definitions:

- recipes
- comps
- stats
- ThingCategories
- research requirements
- related buildings
- ingredients
- production chains
- known Def references

Then the LLM explains:

> "This gland is mainly used for X. You currently have Y unlocked. The easiest useful application is Z."

This could convert enormous-modlist interoperability confusion into an in-world feature.

---

# 29. A Planner That Does Not Execute

**Value:** ★★★★★  
**Ease:** ★★★★☆

Avoid giving the model direct unrestricted colony control.

Instead, let it propose actions.

Example:

> "I recommend expanding this freezer."

RimWorld displays a translucent suggested area.

Buttons:

**ACCEPT**  
**IGNORE**

Likewise:

> "Raise R4's hauling priority to 2."

The player clicks to apply it.

This gives AI assistance without allowing model mistakes to destroy the colony.

---

# 30. One Director Call Powering Multiple Systems

Rather than making separate model calls for every system, use one bundled **Director Call** after major checkpoints.

Example output:

```json
{
  "advisor": {
    "urgent": [],
    "nearTerm": [],
    "strategic": []
  },
  "story": {
    "currentTheme": "",
    "suggestedNextBeat": ""
  },
  "factions": {
    "mostRelevantFaction": "",
    "intent": ""
  },
  "characters": {
    "pawnToWatch": "",
    "reason": ""
  },
  "opportunities": []
}
```

One invocation can update:

- Foreman's Board
- storyteller priorities
- faction behavior
- narrative focus
- quest hooks
- pawn spotlighting
- optional adventure suggestions

Then the mod waits until something significant invalidates the analysis.

This is probably the best overall optimization.

---

# Recommended Priority for This Playthrough

| Priority | Mod | Approximate Calls | Implementation |
|---|---|---:|---|
| 1 | Jawa Foreman's Board / Strategic Advisor | ~1/day + manual | Easy |
| 2 | Episode Director with legal event grammar | ~1 per 3–7 days | Moderate |
| 3 | Faction Agendas | ~1/faction/quadrum | Easy–Moderate |
| 4 | Droid Firmware Personalities | Once per notable droid | Easy |
| 5 | Nemesis Memory | Once per major encounter | Easy–Moderate |
| 6 | Previously On + Session Goals | Once per load/session | Very Easy |
| 7 | Ruins / Sarlacc Backstory → Modular Dungeon Selection | Once per site | Moderate |
| 8 | Holonet World Simulation | ~1 per 5–10 days | Very Easy |
| 9 | Adaptive Bounty / Rumor Board | ~1 per refresh | Moderate |
| 10 | Rare-Item Provenance | Once per notable item | Very Easy |

---

# Strong Architectural Rule

Use the LLM for:

- semantics
- interpretation
- intentions
- priorities
- combinations
- narrative coherence
- memory compression
- choosing among legal possibilities
- explaining complex mod interactions

Do **not** use it for:

- pathfinding
- tick-by-tick combat tactics
- geometry generation
- minute-to-minute job scheduling
- exact economic balancing
- arbitrary runtime C# generation
- unrestricted autonomous colony control
- high-frequency pawn chatter

---

# Recommended First Combined Mod

The most promising initial system is probably a combined:

## Jawa Director Core

with two visible features:

### Foreman's Board

The LLM interprets the colony as a strategic problem.

Example:

> Fix the vaporator immediately.

### Episode Director

The same analysis interprets the colony as a story.

Example:

> The next interesting complication is a Junker attempt to steal the replacement condenser.

The same sparse model call can know that:

- water is critical
- Junkers recently attacked
- Tusken relations are improving
- the gravship must leave in six days
- the colony badly needs a condenser

It can therefore simultaneously recommend:

> **Repair the water system.**

and choose:

> **A contextually meaningful attempt to steal the replacement part.**

That begins to feel much less like "ChatGPT bolted onto RimWorld" and much more like an intelligent Star Wars game master operating within bounded, deterministic RimWorld mechanics.
