# Design & Creative Census: 2026-09-18 to 2026-09-25

Read-only census of creative/design work on the Ash'karr campaign (RimWorld Star Wars
Jawa scavenger clan). Sources: `git log --since=2026-09-18 -- design/` (246 commits, 234
unique files touched), ledger shards (`infrastructure/state/ledger/events/*.jsonl`, 683
events in window, 23 explicit `owner_said` quotes), and `infrastructure/state/items/closed/`
(224 items closed/mtime'd in window — mostly engineering execution of the week's rulings,
noted but not detailed here).

Written for a guest who has never seen this project.

## The premise, one paragraph

Ash'karr is a single, hand-authored desert planet — never regenerated, painted once at the
end. The player is a Jawa scavenger clan. Every biome is being rebuilt as its own
standalone mod (`RM_` = franchise-free, usable in any RimWorld game; `RSW_` = genuine Star
Wars canon; `RUT_` = this specific campaign's patch layer on top). The week's big-picture
ruling, repeated across many sittings: **invent a complete, rich creature/plant roster
first — then look for Star Wars injection only where it earns its place.** An invented
exotic-sounding name is NOT Star Wars IP; only genuine canon is.

## Biomes touched this week, and what makes each distinct

- **The Fever Wood** (jungle water-world, crown vs. the water below) — a ban on its
  central mystery was *lifted*: the deep tentacled thing (owner: "we should just make up
  our own tentacled eldritch horror down there and map it to the Dianoga when Utinni is
  active") now gets ambient tentacle strikes, scattered loot, a captive specimen on
  display, and a name — **the Sekkulaath** (dianoga under the Star Wars layer). 11 new
  creatures and 18 new plants were rostered, organized around a "sap-drinker guild" of
  four creatures that all cling to bark and refuse to be bothered, each by a different
  defence.
- **The Miasma** (dying delta mangrove, "the lifeboat at the drain") — got its first real
  fauna roster: carnivorous plants that eat floor-dwelling scuttlers (never a colonist), a
  loam-composting scuttler clade, and its "stranded" reconceived — not a species at all, but
  a *condition* that happens to a sea-nursery's failed young.
- **The Webwork** (spider jungle) — got its owner species named: **Ollathrix**, one
  race/one kind (no castes), mapping to the Wyyyschokk under the Star Wars layer, plus a
  thin 5-row supporting cast (anchor-beetle, egg-mite, a trace flier) and — the standout —
  a whole black-market economy: eggs as smuggler contraband, and **assassination quests
  where you plant an egg in a target's room to hatch overnight** (owner's own words,
  verbatim, are the seed of the whole design doc).
- **The Sump** (tar-pit dusk biome) — 9 invented residents, "sparse but strange" by
  design; a tar beast that is never fought, only fled from and evacuated ahead of; and a
  flier, **Skellarn**, added by a live typed reversal — "let's make it have really long
  spikey legs so when it lands it can still move through the tar" — plus a standing order
  for a **random tar-belch event** that dumps tar across the local terrain.
- **The Weeping Stones** (hand-placed sacred oases on high cold stone) — a "Make It Shine"
  option portfolio the owner graded live: a stocked-pool fish husbandry loop was greenlit
  and made memorably strange ("some shouldn't be fish but alien beasts you really wonder if
  we should be eating"); a "born and dying water" mechanic was killed outright ("nah too
  much"); a mechanic idea redirected into standalone **Oasis-Maker Machines** — buildings
  that slowly grow real water out of shaded rock over time, sold at high (moisture-farming
  tech tier) price, usable as scenario starting gear; and a "the water enforces peace"
  concept became **animal retribution**: fight near the pools and the wildlife turns on
  whoever struck first (verified against the decompiled engine that RimWorld really can
  tell who started it).
- **The Rot** and **Greentide** — cast migrations from Star Wars-flavoured donor names to
  invented `RM_` names (recoined where a name collided with real canon, e.g. avoiding
  "zillok" for clashing with the canon Zillo Beast), plus the Greentide's own risk/reward
  redesign: an intimidating jungle of danger (plants, beasts, disease, insects) countered by
  abundance, medicine and Star Wars cuisine ingredients.
- **The Terminal Seas** (the Scald / Grey Sea / Twilight Sea / Propane Lake) — the week's
  biggest single push. All four now get named floor residents and fishable catches. The
  owner personally named the new sea creatures live: the bottom-walkers are **the Mighty
  Vu'uul** (who lay down the glowing pigment as they pass), the glowing swirl is
  **Ullium**, the guardians are **Askirath**, the scalding swarm is **Feen**. A full **Sea
  Dive Maps** design lets a colonist dive from shore into a persistent underwater map per
  sea — dark, roofed by the water itself, no raids, a rope-lit exit line, an exposure clock
  that only heals under an air-bell or back on land. The owner asked for **a crashed,
  mineral-encrusted ancient Rakatan vessel with dormant droids sitting on the sea floor
  (not inside the ship)** as a dive discovery.
- **The Weeping Stones / Arid Shrubland's tree guardian** — the sweetline tree's
  guardian species was finally named: the **bark-warden** (`RM_Barkwarden`), a
  knuckle-walking climber that drops on anyone within 9 cells of its home tree and
  backs off once they retreat past 18 — "a valuable hanging harvest, in a dangerous
  place."
- **The Greentide's greatbole** — a threshold-ladder harvest economy was built this week:
  mine the giant tree past 40% removed and it shakes down fruit and grubs; past 60% it
  seals and violently regrows to full; past 70% it's reachable only by explosives (a pick
  physically cannot out-mine its regrowth rate) and the tree dies for good, permanently
  altering the map. The owner's inadvertent design gift: "the mechanic makes the method
  compulsory without a rule saying so."

## Standout inventions with a line of flavour each

- **Deepfire / crowncarpet** — a luminous pigment mixed into ordinary dye to make any
  colour glow. It comes from a rainbow bacterial mat that dies within a day (instantly if
  chilled), so the whole economy is a race from shore to press; laid down by the sea's
  giant bottom-walkers (the Vu'uul) as they cross the boiling Scald.
- **The exposure gear matrix** — the owner distilled every survival-gear question on the
  planet into two axes (no-air: liquid vs. vacuum; temperature: extreme heat vs. cold) and
  three tiers (cheap improvised, moderate, deluxe-reaching-space), a single clean frame that
  now organizes dive suits, boil-suits and future spacer gear.
- **The Sekkulaath / Ollathrix pattern** — a recurring, elegant trick this week: invent a
  franchise-free creature for the base mod, then have it *map onto* a genuine Star Wars
  creature only when the campaign layer is active (dianoga, Wyyyschokk). The free mod is
  never a cut-down version of the campaign one.
- **The Ollathrix egg economy** — a spider's stolen eggs become both a black-market
  commodity (Hutt/bounty-hunter buyers) and a murder weapon in an optional-immorality quest
  line.
- **The tar-belch event** and **Skellarn's spiky stilt-legs** — both owner improvisations
  landed live, on the spot, mid-review.
- **Oasis-Maker Machines** — slow terraforming as a treasure: buy an ancient machine at
  high moisture-farming-tier price, place it by shaded rock, and watch a real, permanent
  oasis grow.
- **Animal retribution at sacred water** — start a fight near a tended pool and the local
  wildlife turns on the aggressor, verified against actual engine combat-instigator logic
  rather than invented as a "don't fight back" rule.
- **The Titanoslime** — a titanic green slime that grows through five visible life
  stages by swallowing pawns whole (up to forty times human mass), built on vanilla's own
  life-stage system with the stage index locked by a comp — no Harmony patch required.
- **The Bazaar** — a full trade-window redesign built on the thesis "the deal is the
  gameplay": haggling as a real information-and-skill loop rather than a spreadsheet
  checkout, with a droid-carried "information is loot" mechanic.

## Owner rulings that shaped the week's direction

- *"we should just invent our own complete roster of fauna, flora, etc. that make it a
  rich place THEN look for Star Wars specific injection opportunistically"* — the week's
  guiding principle, cited verbatim in nearly every new roster.
- *"I don't think it's important to use actual Star Wars trees... get wild with them"* —
  killed canon-tree research for the Greentide in favour of pure invention (no conifers;
  large-leafed, tentacle-leaved, willow-canopied forms).
- Q11a, formalized this window: **"star wars style" naming is not Star Wars IP** — the
  tier line is provenance, not flavour, and a `RM_` biome must never ship as a thin
  fallback next to a richer campaign one.
- *"Let's stop evictions right now"* (carried into this week) — biome rosters are reviewed
  one sitting at a time, never swept; a species multi-homed across biomes stays until its
  own biome's sitting judges it.
- Rapid-fire, same-day verdicts across the Weeping Stones options: greenlight nasty stocked
  fish, kill "born and dying water," redirect "machines that weep" into Oasis-Makers,
  redirect "the one law" into animal retribution.
- *"Stop this live testing. It's wasting time... handled my northstar-type validations and
  screenshots"* — a standing correction on method, not fiction, but shaping how the rest of
  the week's claims get proven.

## Thematic through-line

The week reads as a planet-wide changeover from *donor filler* to *authored voice*. Nearly
every biome touched follows the same arc: read what's shipping today (often generic vanilla
or Alpha-Biomes placeholder wildlife), name what the frozen design sheet already promised
but never cast, and invent a small, ecologically-linked cast rather than padding a list.
Recurring design moves: creatures that *contest* a resource rather than just guard it
(bark-warden, greatbole grubs, the Sump's tar beast); an invented/canon mapping pair that
keeps the free mod whole (Sekkulaath/dianoga, Ollathrix/Wyyyschokk); and mechanisms the
owner keeps redirecting live, in-session, toward the stranger and more specific option
(nasty fish you're not sure you should eat; egg-laying assassination; tar that literally
belches).
