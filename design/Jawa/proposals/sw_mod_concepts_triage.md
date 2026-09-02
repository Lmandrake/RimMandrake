<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# Star Wars mod concepts — full triage, and 7 taken deep

Source: `research/Jawa/Star_Wars_RimWorld_Mod_Concepts.md` (2026-08-18, 27
numbered sections + a §28 "standalone candidates" list). Method: every
section checked against (a) this sitting's sibling proposals —
`tar_pits_deep_design.md`, `propane_gas_deep_design.md`,
`fire_ecology_deep_design.md`, `ship_shields_deep_design.md`,
`water_economy_deep_design.md`, `underground_caverns_deep_design.md`,
`god_modes_deep_design.md`, `skyhook_deep_design.md`,
`ludicrous_livestock_deep_design.md`, `high_cuisine_deep_design.md`,
`llm_driven_mods_deep_design.md` (the last five landed mid-sitting, checked
at start as assigned-but-not-yet-written and named here now that they
exist) — and (b) existing campaign canon (`droid_system_spec.md`, `droid_ruling.md`,
`restraining_bolt_technical.md`, `cantina_kitchen_spec.md`,
`desert_world_design.md`, `dungeons_arc_spec.md`,
`reconciled_lore/FUTURE_VECTORS.md` — which independently re-triaged this
exact concept sheet on 2026-08-29 and is cited throughout below).
`FORCE_SYSTEM_OWNERSHIP_1` (open queue item) also matters for §22.

Nothing below invents a defName. Nothing below is worldgen — every mechanic
proposed is map-level content, authored sites, or systems that run on the
one frozen Ash'karr map.

---

## 🔴 RULED — owner sitting, saved 2026-09-02 (review sheet, 7 rows)

Verdicts and the owner's notes, verbatim (frozen source: `design/Jawa/worldbuilding/review/proposal_suite_review.decisions.json`; untouched rows keep their prefill — cut is the only destructive verdict):

| row | ruling | owner's note (verbatim) |
|---|---|---|
| junk-provenance | v1 | The more unique an item is, the more it can be remembered. Ownership should fade for all things, and the more generic the items the faster it decays. As you say, players only know of other ownership when they steal. Finding something in the desert carries the unknown threat that someone else thinks it's theirs... unless you're within their territory. Then they probably do. If they saw you. Did they see you? Who knows. |
| krayt-leviathans | dream→**v1** | Keep the giant Krayt dragon just as it is, but create a NEW massive dune-style sandworm with its own mythos. Plenty of room for both. But Krayt dragons deserve their own treatment. Feel free to borrow from the giant worm mod to build another version for the Krayt. |
| underworld-reputation | v2→**v1** | This is required for the Hutt dealings, so no reason you can't enter into this state with others. The hutt's just aim at it aggressively, offer it. |
| cantina-social | v2→**v1** | Yet the bad leads can't just be disappointments. Something has to come of it. Maybe it allows you to righteously return and embarass the perpetrator, or flip the tables on them, or sell the false rumor to another later. The fun must continue! |
| holo-deception | v2→**v1** | I super like this when the Jawa turn their newfound technological prowess to their normal pursuits. Deceptive holograms aboard the ship to evade boarders. |
| imperial-bureaucracy | v2→**v1** | Wait, this is GREAT! The Jawa don't enter the settlements with their massive ship, they walk in from afar... so yes! There can be Imperial guards standing by monitoring the situation, and all of the verbs you just offered should be possible interactions. The locals might even cheer your resistance if you do, or just laugh. No such thing as binary "angry/content" town moods, make it interesting! |
| droid-repair-shop | dream→**v1** | Gotta do this. And people bringing their broken droids for repair is so fun, there has to be a way to incorporate this somehow... |

## Full triage, section by section

| § | Concept | Disposition | Note |
|---|---|---|---|
| 1a | Species-relative personhood / food morality | **COVERED** | `high_cuisine_deep_design.md` (this sitting — "meals as statements"); named "Galactic Palates" in both the source sheet §28 and `FUTURE_VECTORS.md`, tied to `cantina_kitchen_spec.md`'s live-tank mechanic |
| 1b | Alien etiquette / bad translation / "technically correct" protocol droid | **LIVE → expanded** | folded into §Droid Behavior below (protocol-droid etiquette is a droid-flavor problem, not a separate system) |
| 2 | Droidbrain — chassis psychology, restraining bolt, unruly combat droids | **COVERED (core) + LIVE (tail) → expanded** | five states, capture, ion, and the restraining-bolt *ceiling* are RULED (`droid_system_spec.md`, `droid_ruling.md`, `restraining_bolt_technical.md` — the last is explicit: "CAP the ceiling... not a project"). `FUTURE_VECTORS.md` names the uncovered tail itself: personality drift, module-personality layer, wild-droid seek-a-master, Repair Shop quest pack. That tail is what gets expanded. |
| 3 | Droid repair/customization economy | **LIVE (tail) → expanded** | same tail as §2; "Repair Shop quest pack... ruled a pack on top, not platform" per `FUTURE_VECTORS.md` |
| 4 | The Living Desert (burrowing, sand-swimming, thumpers, leviathans, krayt pearls, night desert, weather-with-teeth, glasslands) | **PARTIAL COVERED + LIVE → expanded** | "weather-with-teeth" mechanism is already in build (`DUST_STORMS_DESTRUCTIVE_1`, a Tornado-derived `RM_DustDevil`). The rest — burrowing ecology, sand-swimming, krayt leviathans and pearls, night desert — is confirmed still open in `FUTURE_VECTORS.md` ("pairs with the VAST-tier precedent already in-stack: the Leviathans sandworm, a world object with weather and music attached, not a spawn"). Expanded below, scoped narrowly around that gap. |
| 5 | The Desert Below (buried cities, bunkers, starships, sarlacc roots, smugglers' tunnels) | **COVERED** | `underground_caverns_deep_design.md` (this sitting) + `dungeons_arc_spec.md`'s six Forsaken vaults. Sarlacc-root cross-link lands in Doc 2 (`sarlacc_deep_design.md`, this sitting) |
| 6 | Sarlacc: Living Dungeon (entire section) | **COVERED** | Doc 2, this sitting: `sarlacc_deep_design.md`, plus the existing `research/Jawa/rimworld_sarlacc_encounter_current_design.md` and the `anomaly_content.boundary_ruled` canon exception |
| 7 | Junk Is Civilization (salvage ontology, scavenger instinct, junkyard ecology, ownership-negotiable, Jawas steal) | **PARTIAL COVERED + LIVE → expanded** | "much of its spirit already ships (the economy, Rekko)"; the named-open v2 piece is provenance and the salvage-built weapon tier (`FUTURE_VECTORS.md`) — that's what's expanded below |
| 8 | Sandcrawler Life (mobile settlement) | **DEAD as player mechanic, LIVE as flavor (one-liner only)** | `desert_world_design.md` §4B already assigns player vehicles to land skimmers + Bantha caravans; the house rule fixes the player's one home vessel as the gravship Utinni. A sandcrawler survives only as an NPC trader/rival-clan site visual — too thin to earn a full expansion here, noted for a future sitting |
| 9 | Moisture, Water, and Desert Politics | **COVERED** | `water_economy_deep_design.md` (this sitting) + `water_doctrine.md` |
| 10 | Galactic Underworld Reputation (debts, favors, Hutt contracts, bounty hunters, capture-alive) | **LIVE → expanded** | confirmed open in `FUTURE_VECTORS.md`: "the natural deepening of the ledger pressure" |
| 11 | Cantina Simulation (info/econ hub, music) | **PARTIAL COVERED + LIVE → expanded** | `cantina_kitchen_spec.md` owns the food/live-tank half ("the Jawa meet it in Hutt and Deepwater settlements rather than owning it"); the social/information/economy layer is untouched — expanded below |
| 12 | Rumors, Information, and Maps | **LIVE → folded into §11 expansion** | becomes that expansion's information-economy engine, not a separate doc |
| 13 | Biological contraband / xenobiological farming | **COVERED + one-liner** | husbandry half is `ludicrous_livestock_deep_design.md` (this sitting — "a workbench with a heartbeat"); contraband-cargo half folds as flavor into the Underworld Reputation expansion (§10) |
| 14 | Rancor Keeping and Arena Economy | **COVERED + one-liner** | rancor-as-pet is `ludicrous_livestock_deep_design.md`'s territory; arena economy folds as a one-liner into the Cantina/Underworld expansions as a spectacle circuit, not its own doc |
| 15 | Ancient Machinery and Lost Functions | **LIVE → folded into §7 expansion** | the "you shouldn't have turned that on" beat belongs inside Junk Is Civilization's salvage-mystery loop |
| 16 | Imperial Bureaucracy (licenses, transponders, inspections, forgery) | **LIVE → expanded** | no existing doc claims this; distinct non-combat pressure against the already-reskinned-vanilla Empire faction |
| 17 | Holo-Deception and False Reality (fake structures, capture pit-traps, tactical misdirection) | **LIVE → expanded** | confirmed open in `FUTURE_VECTORS.md`: "ties to the ghost layer the ship already carries" |
| 18 | Slicing as Adventure | **LIVE → folded into §17 expansion** | the breaking-in counterpart to holo-deception's faking-out |
| 19 | Shipwreck Archaeology | **COVERED-adjacent, one-liner** | same dungeon-chain machinery as `underground_caverns_deep_design.md` and `dungeons_arc_spec.md` wearing a wreck skin — no new system needed, just a new site dressing when one of those docs authors a wreck entrance |
| 20 | Hyperdrive Weirdness | **LIVE, one-liner only** | good as a rare scripted quest/event-table entry (arrival-mishap flavor on an already-authored transit); "arrive in the wrong biome" as a *system* would need worldgen-shaped randomness the house rules forbid, so this stays a one-off, never a mechanic |
| 21 | Starship Ghost Stories | **LIVE, one-liner only** | flavor content for whichever doc ends up owning the ship's existing memory layer (`FUTURE_VECTORS.md`'s "ghost layer") — not a new system |
| 22 | Rare Force Phenomena | **COVERED/PARKED** | `FORCE_SYSTEM_OWNERSHIP_1` (open item, lightsaber DLL) has an explicit open question about whether the Force-*powers* sibling mod is even wanted; `FUTURE_VECTORS.md` separately parks "Force powers in their entirety (VPE returns in v2)." Not mine to invent ahead of that ruling. |
| 23 | Legend Generation | **LIVE, one-liner only** | `FUTURE_VECTORS.md`: "the Inhabited mod's memory layer is the substrate these want" — a future consumer of `BRIDGE_STORY_ALERT_TALE_TOOLS_1`'s tale-data exposure, not a fresh design surface today |
| 24 | Heroic Idiocy (desperation actions) | **LIVE, one-liner only** | small flavor mechanic, best raised at a future sitting once it's clear whether it rides an existing mental-state hook or needs new C# |
| 25 | Cinematic Failure | **LIVE, one-liner only** | same disposition and substrate as §23 |
| 26 | Recurring Galactic Characters | **LIVE → folded into §10 expansion** | becomes Underworld Reputation's "a debt outlives the fight that created it" throughline |
| 27 | Jawa Cultural Flavor (Utinni! vocal/emote layer) | **COVERED-adjacent, one-liner** | `PAWN_FLAVOR_STARWARS_1` (open item) owns backstories/traits/text flavor; the *audio* emote layer specifically is unclaimed but needs actual sound design, not a design doc — flagged, not expanded |
| 28 | (meta-list: "standalone mod candidates") | **n/a** | this is `FUTURE_VECTORS.md`'s own source list; the 7 picks below track it closely and cite it throughout |

**Nothing above silently vanishes.** Every DEAD-as-mechanic and one-liner
disposition names where the concept still lives, or names the sitting where
it should be raised next.

---

## The 7 taken to deep-design level

### A. Junk Is Civilization — provenance and the scrap-built weapon tier

*The gap, precisely:* the salvage economy already ships. What's missing is
the layer that makes junk feel like **history** rather than inventory —
where an item came from, who it belonged to, and whether picking it up was
theft.

- **Provenance as a hidden stat, not a tooltip essay.** Every salvaged item
  above a rarity floor carries a provenance tag (`legitimate` /
  `battlefield` / `disputed` / `Imperial` / `Hutt-collateral` /
  `ancestral`). Most of the time this sits inert. It activates when the item
  crosses paths with someone who cares: an Imperial inspection reading a
  serial number (ties to §Imperial Bureaucracy below), a former owner's
  faction recognizing their own gear on a trader's counter, a Hutt
  collections agent noticing collateral being worn openly.
- **"Salvage" is a negotiable category, mechanically.** Taking an item from
  an unattended, unowned source (wreck, ruin, corpse with no living claimant)
  is free. Taking it from something *watched* — a caravan's cargo, a
  droid still nominally in someone's service — is a theft roll: if unseen,
  no hostility; if seen, it's whatever theft already does, just dressed as
  "salvage" in the flavor text. This reuses existing theft/ownership
  plumbing; the new part is that Jawas get a bonus on the unseen roll
  (Scavenger Instinct, §7 of the source sheet), which is the one new number
  this needs.
- **Scrap blaster tier.** Named directly in `FUTURE_VECTORS.md`: reskin
  Makeshift's unreliable-burst verb as the visible signature of a
  jury-rigged weapon assembled from mismatched components. Stats sit below
  a proper blaster on accuracy/reliability, above nothing on damage — a
  real early-game weapon with a personality (occasional misfire, described
  in flavor as "the regulator's from a landspeeder"), not a strictly worse
  clone.
- **"You shouldn't have turned that on"** (source §15, folded in here):
  rare salvage items carry a hidden capability flag revealed only through
  use/disassembly/slicing (never a research-tree line) — a cargo droid with
  military encryption, a medical scanner with restricted genetic tools. This
  is the payoff structure Junk Is Civilization has been missing: most junk
  is just junk, but the player can never be *certain* which piece isn't.

**Defs/C#:** a provenance ThingComp (enum field + optional faction-of-origin
reference) on salvageable ThingDefs; a small Harmony hook on existing
theft-detection to read Jawa Scavenger Instinct as a roll modifier; the
scrap blaster as one new ThingDef pointing at Makeshift's existing verb
class (no new C#); the hidden-capability flag as a ThingComp with a
reveal-condition enum (`onUse` / `onDisassemble` / `onSlice`).

**Story hook:** a trader recognizes his own stolen speeder part in a Jawa's
hands — not as a raid trigger, but as a haggling opener ("I'll pretend I
didn't see that, for a price").

**Mini build ladder:** v1 — provenance tag + Jawa unseen-roll bonus. v2 —
scrap blaster tier + faction recognition events. dream — hidden-capability
salvage as a recurring, non-scripted discovery loop across the whole
campaign.

---

### B. Krayt Leviathans — sand as an ocean, pearls as its pearl

*The gap, precisely:* `DUST_STORMS_DESTRUCTIVE_1` already makes weather bite.
What's still open is the *creature* register of the Living Desert — the
thing that makes "under the sand" feel occupied, mirroring the
already-in-stack sea Leviathan (a world object carrying weather and music,
never a spawn) but built for dunes instead of water.

- **The krayt leviathan is a regional event, not a pawn kind.** Same
  register as the sea Leviathan: it doesn't spawn on a map, it *is* a
  standing world-object with a migration route, weather effects (a
  moving dust-wake visible for tiles around it), and its own ambient
  music sting when a caravan crosses its path. Encountering one is closer
  to a weather event than a monster fight.
- **Vibration as the shared signal.** Thumpers (in-fiction: repurposed
  mining or seismic gear) generate a tunable vibration signature. Heavy
  machinery running nearby generates it as an unwanted side effect. Both
  read against the SAME creature-AI trigger the underground caverns
  doc already proposes for its darkness-draws-things mechanic (§8 of that
  doc) — one shared "disturbance level" signal, two consumers, no
  duplicate system.
- **Krayt pearls, and the kill-vs-take-alive tension.** Pearls form inside
  a leviathan over a lifetime — mineral ingestion, age, diet, biome
  chemistry. A dead leviathan is a one-time extraction site (meat, hide,
  bone, glands, pearls, all as a temporary harvestable ruin, same shape as
  a normal animal's corpse-harvest but map-sized). Sand-swimming and
  "riding" a live leviathan's wake safely is the higher-skill, higher-value
  alternative — pearls extracted without killing the source are worth
  more, mirroring the sarlacc's own pearl economy in Doc 2 for a
  deliberate cross-campaign echo (two very different creatures, same
  "the treasure gets worse if you're crude" lesson).
- **Night desert as the leviathan's active window.** Reuses whatever
  day/night gameplay toggle other proposals in this sitting (fire ecology,
  propane) already lean on — leviathan activity, burrowing-creature
  emergence, and flower-opening/moisture-collection all key off the same
  daylight flag, so "operate at night" becomes one coherent strategy
  rather than three unrelated toggles.

**Defs/C#:** the leviathan as a WorldObjectDef (not a PawnKindDef) with a
route/GenStep-adjacent movement tick and an attached GameCondition for its
dust-wake weather; a shared "disturbance level" trigger (small C#, the same
one underground_caverns already needs — build once, two consumers); pearl
extraction as a corpse-harvest-shaped ThingComp keyed to kill-vs-live
capture state.

**Story hook:** a Jawa clan elder can read leviathan tracks the way a sailor
reads weather — a caravan route recommendation that's really a leviathan
migration forecast in disguise.

**Mini build ladder:** v1 — one leviathan route, dust-wake weather effect,
dead-leviathan harvest. v2 — vibration/thumper mechanic, shared disturbance
signal wired to both this and underground caverns. dream — live pearl
extraction as its own skill-gated minigame, night desert as a distinct
playstyle window.

---

### C. Galactic Underworld Reputation — debts outlive the fight

*The gap, precisely:* the campaign already has faction relations and a Hutt
identity; what's missing is the layer where **owing someone** is a distinct
state from **being at war with them** — the source sheet's central insight
that a Hutt doesn't attack because you offended them, they decide you owe
them, and an associate collects months later.

- **A ledger, not a relations meter.** Alongside the existing faction
  goodwill number, a per-faction (or per-notable-NPC) debt/favor ledger:
  positive (they owe the colony), negative (the colony owes them), decaying
  slowly, never zeroing out on its own. This is the mechanical spine
  `FUTURE_VECTORS.md` calls "the natural deepening of the ledger pressure"
  — it already expects this to exist somewhere.
- **Hutt contracts with built-in ambiguity.** Quest-shaped offers whose
  plain-text framing ("retrieve my property," "collect a debt," "transport
  cargo") can resolve as something the player didn't sign up for
  (capturing a *person*, seizing a moisture farm, running biological
  contraband) — discovered mid-quest, not hidden as a gotcha at accept
  time. Refusing creates ledger consequence, not instant war.
- **Bounty hunter ecosystem, scaled to bounty value.** A pawn's individual
  bounty (crime, debt, faction grudge) is tracked independently of faction
  hostility. Cheap bounties draw cheap hunters (they just attack). Expensive
  ones draw hunters who use the toolkit the source sheet names — trackers,
  disguise, informants, ambush, kidnap-not-kill — which is also where
  Holo-Deception's capture-pit-trap mechanic (§E below) gets a *user*, not
  just a builder: a hunter working a high-value bounty is exactly who
  deploys a fake floor.
- **Recurring characters as the ledger's memory** (source §26, folded in
  here): every named ledger entry can spawn a return visit — the trader who
  remembers being cheated, the bounty hunter who got away wounded, the
  rescued refugee who comes back as someone else's problem or asset. This
  doesn't need a new system, just the ledger keeping names instead of
  numbers for its top entries.

**Defs/C#:** a ledger ThingComp/WorldComponent keyed to faction+optional
named-pawn, decaying on a slow tick; contract quests as QuestScriptDefs with
a delayed-reveal node (the "actually means" twist surfaces via existing
quest-node branching, no new node type needed); bounty value as a stat on
the existing wanted/criminal-record plumbing if RimWorld already tracks one,
otherwise a small new comp.

**Story hook:** the colony's oldest debt is to someone who's dead — does the
obligation pass to their faction, their heir, or die with them? A quest
generator, not a one-off.

**Mini build ladder:** v1 — the ledger itself, one Hutt contract chain with
a mid-quest twist. v2 — bounty-value-scaled hunter roster, recurring-visitor
hook on top ledger entries. dream — a fully generative "who's owed what"
system that produces its own quest content without hand-authoring each one.

---

### D. The Cantina, socially — rumors, gambling, and a stage

*The gap, precisely:* `cantina_kitchen_spec.md` built the kitchen (the live
tank, the recipes, the three-faiths-one-dish mechanic). It explicitly hands
the Jawa a *destination*, not ownership. What's missing is what happens at
the tables once the food's served.

- **Rumor economy.** Tradeable information — wreck coordinates, bounty
  targets, patrol schedules, hidden water (a direct hook into
  `water_economy_deep_design.md`'s scarcity framing), suspected leviathan
  pearls (a hook into §B above). Rumors carry a reliability rating and can
  simply be wrong — the interesting failure mode is a caravan chasing a
  bad map, not a binary refund.
- **Maps that lie**, same mechanic in item form: a purchased map is
  outdated, incomplete, or fraudulent, and Jawa/scout characters get better
  at telling which before committing resources to it.
- **Music as a mood/economy lever, not decoration.** A cantina musician
  (droid or organic) affects customer dwell time and violence probability
  — reusing whatever mood-radius mechanic vanilla joy buildings already
  have, retuned rather than reinvented. Species-specific musical taste (and
  the bad-music-provokes-a-fight failure mode) is flavor content riding the
  same trigger.
- **A stage for reputation to walk onto.** This is the room where
  Underworld Reputation (§C) actually gets *seen* — bounty ID happens here,
  informants gossip here, a rescued recurring character reappears here
  first. The cantina isn't a separate economy; it's the front-of-house for
  the ledger.

**Defs/C#:** a rumor as a tradeable ThingDef-or-quest-item with a hidden
accuracy roll, resolved on use/travel-to-target; a musician joy-building
retune (existing comp, new tuning values) with a species-preference lookup
table; no new subsystem beyond what §C's ledger and §water_economy already
need to expose to a shared "cantina board" UI surface.

**Story hook:** a rumor about a Sarlacc pearl cache turns out to describe
Doc 2's very real pit — the cantina becomes the place that *sends* the
player toward this sitting's other proposals, not a side room.

**Mini build ladder:** v1 — rumor items with accuracy rolls, tied to one
other proposal's content (water or leviathans). v2 — musician mood mechanic,
species preference table. dream — the cantina as a living index of every
other system's current rumor-worthy state, self-updating.

---

### E. Holo-Deception — projection as a weapon, a wall, and a lie

*The gap, precisely:* nothing else in this campaign's canon touches
holography as a system; `FUTURE_VECTORS.md` flags only that it "ties to the
ghost layer the ship already carries," meaning the *mechanism* is unclaimed.

- **Holographic pit traps** (the source sheet's strongest single image):
  a fake floor over a real hazard — a capture trench, a droid
  immobilization bay, a restraint cage — with a detection tier per pawn
  type: organics trust vision, animals smell the void beneath, droids read
  projection artifacts, sensor-equipped or sufficiently alert pawns can
  notice. This gives Jawas, Hutts, bounty hunters (§C) and defensive
  colonies alike a distinctly non-lethal capture tool that isn't a stun
  weapon reskin.
- **Tactical misdirection at colony-defense scale.** Fake walls, decoy
  colonists, false command posts, spoofed vehicle silhouettes — a
  slicer/technician-gated defensive tool that reads as a genuine
  alternative to turret spam, not a strictly-better version of it (it
  fails against anything that doesn't trust vision, same detection-tier
  logic as the pit traps).
- **Slicing as its counterpart** (source §18, folded in here): where
  holography is deception aimed outward, slicing is the break-in aimed
  inward — small procedural "dungeons" inside a single computer/terminal,
  reusing whatever puzzle/skill-check plumbing an existing colonist skill
  already has, with failure states (alarms, lockouts, waking something
  that shouldn't wake) that are narratively cheap to author and mechanically
  small.

**Defs/C#:** a projector building/apparel ThingDef with a `HologramComp`
carrying a detection-tier enum per pawn category; a terrain-overlay hologram
(visual-only floor swap) tied to a real hidden hazard building underneath —
architecturally a thin C# layer (render override + trigger-on-approach), not
a new pathing system; slicing as a skill-check minigame reusing existing
research/analyze UI patterns rather than inventing new ones.

**Story hook:** the player's own colony gets caught by someone else's
holographic trap first — the lesson taught by being on the receiving end,
before the player ever builds one.

**Mini build ladder:** v1 — one holographic pit trap type (capture-not-kill),
one detection tier (organic-trusts-vision only). v2 — full detection-tier
table across pawn types, defensive misdirection toolkit. dream — slicing as
a fully procedural terminal-dungeon generator, holograms indistinguishable
from reality until a specific counter is used.

---

### F. Imperial Bureaucracy — the Empire that doesn't have to fight you

*The gap, precisely:* the campaign already has the Empire as a reskinned
vanilla faction with combat-shaped pressure. This adds the pressure vanilla
factions never apply: paperwork.

- **Inspections as an event, not a raid.** A patrol arrives peacefully,
  looking for something specific and narrow (one unregistered droid, one
  unlicensed weapon class, one undeclared cargo manifest) — and the colony
  almost never has *only* that one thing clean. This is the source sheet's
  best single joke made mechanical: "twenty-three unregistered droids."
- **Compliance is a real choice with real cost**, not a skip-button: comply
  (lose/pay/register something), forge documentation (a slicing-adjacent
  check, §E), bribe (a ledger-adjacent transaction, §C), conceal (a
  detection-tier problem, reusing §E's hologram detection logic for
  "hidden from an inspection" rather than "hidden from an enemy"), or
  refuse outright (which is the one branch that *does* turn into combat
  pressure, deliberately rare).
- **Imperial equipment carries its own provenance flag** — the same field
  §A's Junk Is Civilization already needs (serial numbers, transponder IDs,
  ownership records), so using captured Imperial gear openly is a detection
  risk that reuses that system rather than inventing a parallel one.

**Defs/C#:** an inspection event (existing raid/visitor-event plumbing,
retuned goal: check-not-fight) with a checklist against colony inventory
tags; reuses §A's provenance flag for the "is this gear traceable" check;
no new detection system — reuses §E's tier logic.

**Story hook:** the inspector who keeps finding reasons to overlook things,
until the day a promotion changes his incentives.

**Mini build ladder:** v1 — one inspection event type (droid registration),
comply/conceal/bribe branches. v2 — full checklist variety (weapons,
cargo, licenses), forgery via slicing. dream — a reputation-with-the-Empire
track that changes inspection frequency and thoroughness over a campaign.

---

### G. Droid Behavior & the Repair Shop — the tail Droidworks left open

*The gap, precisely, restated from the triage table:* Droidworks owns the
platform (five states, capture, ion, restraining-bolt ceiling). This is
explicitly the "personality drift, module-personality layer, wild-droid
seek-a-master, Repair Shop quest pack" named as still-open in
`FUTURE_VECTORS.md` — plus the source sheet's chassis-archetype flavor and
protocol-droid etiquette content (§1b, folded in here), which Droidworks'
mechanical docs never claimed either.

- **Chassis archetypes as starting personality bias, not destiny.**
  Astromech (clever, territorial about machinery), protocol (risk-averse,
  pedantic, prone to interrupting), B1-style battle droid (obedient,
  literal, comically bad at threat assessment), assassin (competent,
  disturbingly literal about mission scope), gonk (simple, occasionally
  heroic) — implemented as a starting-trait weighting per chassis
  PawnKindDef, not a hard-coded behavior, so individual droids still
  diverge (the emergent-personality layer already named as open).
- **The protocol droid is technically correct** (source §1's sharpest
  bit): a diplomacy-support droid that can worsen a negotiation through
  perfect, pedantic honesty — implemented as a modifier on existing
  social/negotiation rolls that's sometimes negative, keyed to the
  protocol chassis bias above.
- **Repair Shop as its own quest pack**, exactly as `FUTURE_VECTORS.md`
  scopes it: visitors arrive with broken droids, diagnosis reveals
  something (routine job, or the "broken agricultural droid" that's
  actually a wiped assassin unit), reputation affects customer quality —
  built as a quest-pack layer on top of Droidworks' existing repair
  primitives, not a new droid state.
- **Jury-rigging as flavor+stats, tied to §A's provenance system**: a
  landspeeder regulator standing in for a motivator isn't just a stat
  penalty, it's a provenance-tagged component the same way a salvaged
  weapon part is — one shared data shape across both docs.
- **Mouse droid / gonk logistics comedy**: small, low-stakes, autonomous
  routing behavior (a power droid wandering off to service a jukebox
  instead of the freezer) — cheap, funny, and a genuinely useful
  emergent-failure signal for the player to debug their own base layout.

**Defs/C#:** a chassis-personality-bias field on existing droid PawnKindDefs
(data, not new C#) feeding into whatever trait-roll system Droidworks
already has; a protocol-droid social-roll modifier (small Harmony patch);
the Repair Shop quest pack as QuestScriptDefs against existing repair
primitives; jury-rigging as a shared component-provenance data shape with
§A (no separate system).

**Story hook:** a Jawa clan's oldest astromech has been rebuilt from six
different droids' salvaged parts so many times nobody remembers its
original chassis — and its personality is entirely its own by now.

**Mini build ladder:** v1 — chassis personality bias as starting-trait
weighting, protocol-droid social modifier. v2 — Repair Shop quest pack,
jury-rigging tied to §A's provenance shape. dream — full emergent
personality drift across a droid's whole service life, mouse-droid routing
comedy as a visible, tunable base-logistics stress test.

---

## Build ladder (whole doc)

**v1 slice** — pick ONE of the 7 to prototype first. Recommendation: **§A
Junk Is Civilization's provenance tag**, because it's the cheapest (one
ThingComp, one roll modifier) and every other expansion above (§C bounty
gear, §F Imperial inspections, §G jury-rigging) reuses the exact same data
shape — building it first de-risks four other docs at once.

**v2** — the four expansions that explicitly need each other landed
together: §C Underworld Reputation's ledger, §D Cantina's rumor board
(which needs something to have rumors *about*), §E Holo-Deception's capture
traps (which needs §C's bounty hunters to be the ones using them), and §F
Imperial Bureaucracy (which needs §A's provenance flag and §E's detection
tiers already built). Sequencing them together avoids building the same
detection/reputation logic three separate times.

**dream** — §B Krayt Leviathans as a full living-desert ecology layer, and
§G's full emergent droid-personality drift — both are the two items on this
list closest to "a simulation that writes its own stories," and both are
explicitly named that way in `FUTURE_VECTORS.md` already. Everything else
above is scoped to land well before either of these.
