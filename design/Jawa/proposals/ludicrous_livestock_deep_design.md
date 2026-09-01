<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# Ludicrous livestock, deep design — a workbench with a heartbeat

The owner's framing question, verbatim: *"What kinds of absolutely ludicrous
livestock can we imagine?"* Answered here as fourteen new creatures across four
families, each pushed past the joke into a working game-design entry: role
band, diet, product and rate, the valve that stops it printing, temperament, a
story hook, and an art direction line. All names are lore text, per house
rule — no defNames are coined here; a build pass runs these through
`design/NAMING_SCHEME_PLAN.md`'s three-tier grammar before anything ships.

Canon anchor: `design/Jawa/worldbuilding/Livestock_Trade_Utility_Pets_v1.md`
§1 ("Living machinery"), the existing four resource-excreters —
**urrak**/radyak (uranium), **vokka**/tetraslug (battery recharge),
**hessa**/aerofleet (power-gel), **hellik**/helixien (gas) — and its §1
guardrail box, which is the load-bearing precedent this whole document
extends rather than reinvents. Beast sizing follows the spirit of
`design/Jawa/worldbuilding/beast_normalization_spec.md` (bodySize tracks
visual size, mass rides bodySize at the engine's 60 kg/bs scale, danger
scales with size) without needing its letter — these are proposals, not
patched defNames, so role bands below are stated as comparisons ("ox-sized,"
"cat-sized") for a future author to convert.

---

## 0. Prior art — what the workshop already proves, and where we go past it

Surveyed against the adopted stack (full detail in `Livestock_Trade_Utility_Pets_v1.md`):

- **Alpha Animals** is the existing donor for "a creature that eats and
  breeds instead of a machine" — the slurrypede (garbage → paste), tetraslug
  (battery recharge), aerofleet (gas → power-gel), radyak (uranium
  crystals), shock goat (static discharge), drainer (eats batteries). Every
  one of these is a **single-input, single-output passive generator** — feed
  X, wait, collect Y. That is the ceiling of the genre as shipped: no def in
  Alpha Animals sorts its output by TYPE, requires a skilled JOB to trigger
  production, or fails informatively when mis-fed.
- **Vanilla Animals Expanded** and **Vanilla Genetics Expanded / Genetic
  Rim** prove the *hybrid* half of the ecosystem — splice a boomalope with a
  muffalo and get a randomized offspring with blended stats — but genetics
  is a randomizer over existing animals, not a new metabolism. Nothing in
  the VE family gives an animal a **process** (a kiln cycle, a smelting
  batch, a molt schedule) the player has to manage in real time.
- **What nothing ships:** an animal whose product depends on a *pawn job*
  performed ON it (not just feeding — tending, narrating, bathing), an
  animal whose "resource" is a stored LIABILITY that comes due, an animal
  that sorts its own output by material class, or a herd whose stampede is
  a directable weapon. Every one of those is open ground, and every one
  below claims a piece of it.

⇒ The move this document makes on Alpha Animals' template: **turn the
single-input/single-output printer into a multi-step process with a
failure mode**, and add a second axis nothing in the genre has —
**creatures whose product is a service or a debt, not a substance.**

### 0-bis. Reconciled against the newly surfaced xenohusbandry corpus

Two research documents surfaced after this doc's first draft —
`research/Jawa/star_wars_rimworld_xenohusbandry_aquaculture_event_design.md`
(800 lines) and `research/Jawa/star_wars_rimworld_xenohusbandry_buildings_art_costs.md`
(468 lines) — cataloguing husbandry facilities, breeding/feed/comfort
mechanics, and a rare-event library for REAL canon SW creatures (bantha,
mynock, droidbreaker, rikknit, mudhorn, kod'yok, colo claw fish, acklay,
and more). **Scope boundary:** that corpus is about creatures already
canon-named and already placed in `Livestock_Trade_Utility_Pets_v1.md`
§10–14; this document's fourteen entries stay original inventions and do
not re-catalog bantha or mynock husbandry. The full reconciliation — what's
borrowed, what overlaps in concept only (mynock/`voltling`,
droidbreaker/`drassik`, rikknit/`karrask`), the art-cost sequencing
discipline, and the explicit scope-cession of aquaculture to the cuisine
doc — is worked through in full in **§7**, added below, rather than
duplicated here.

---

## 1. The valve, restated for this document

`Livestock_Trade_Utility_Pets_v1.md` §1 already carries the campaign's
anti-exponential answer for resource-excreting animals: **the gravship
cargo cap and the itinerary's forage-hostile/heat-hostile tiles do the
enforcement automatically.** You cannot ranch what cannot board, and what
boards cannot graze on half the tiles you're forced to visit. That
guardrail is inherited wholesale — nothing below needs its own hard cap
rule, because the ship already is one. Each entry still names its OWN
additional valve, because a few of these are dangerous or labor-costly in
ways cargo space alone doesn't cover (a stampede weapon is dangerous
regardless of herd size; a grief-eater is a liability regardless of how few
you keep).

---

## 2. INDUSTRIAL GUTS — a metabolism that is a workbench

The direct heirs of urrak/vokka/hessa/hellik: feed the animal raw material,
its body performs a real industrial process, and it excretes the finished
good. What's new versus the existing four: a **multi-step or sortable**
process instead of one input → one output, and a **failure state** when
mis-fed rather than a flat rate.

### Onnik — the kiln-belly

| | |
|---|---|
| Role band | Ox-sized, squat and thick-walled — think a barrel with legs |
| Diet | Clay-rich sand and raw silica, in measured feeds |
| Product | Fired ceramic vessels and brick, one small batch per feed cycle (~4 days) |
| Rate & process | Its gut runs hot from a slow internal mineral-oxidation reaction — a real kiln, just biological. Feed it cold (a single dump) and it fires cracked, worthless ceramic. Feed it in three spaced doses over a day (a job, not an event) and the batch comes out glazed and sellable. |
| Valve | The "kiln" cools if underfed for more than a day and must be reheated from scratch (another full slow-feed cycle) — you cannot batch-produce by stockpiling clay and dumping it all in. Heavy-bodied: expensive cargo per unit of output. |
| Temperament | Placid, slow, faintly warm to the touch always — colonists like leaning on it in the cold |
| Story hook | A trader offers an "already-fired" onnik, guaranteed hot — it's stone cold, and the seller knew; the mark is whoever buys it without checking |
| Art direction | A tortoise-shell silhouette with visible seams like kiln brick, a faint heat-shimmer overlay above its back |
| Canon note | Original — extends the §1 "living machinery" template, no SW-canon parallel |

### Drassik — the smelter-ox

| | |
|---|---|
| Role band | Large draft-ox, heavier-set than a Bantha |
| Diet | Scrap metal and slag, sorted by the FEEDER before feeding — it will not sort for you |
| Product | Ingots, sorted by alloy class through three distinct glands (ferrous / light-alloy / unsmeltable residue) |
| Rate & process | One ingot of the correct class per two days, per gland — but feed it MIXED scrap unsorted and it "chokes": a vet-attention event, days of no output, and a chance of a bad ingot (an alloy nobody wants) |
| Valve | Requires a pawn with real sorting discipline (a Crafting-skill-gated job) to keep it fed correctly — a lazy or overworked colony gets choke events, which is the natural brake on running more than one or two |
| Temperament | Bad-tempered when its glands ache from a bad feed; otherwise indifferent to handling |
| Story hook | A clan whose drassik has choked twice this season and won't take feed at all — a live animal-husbandry crisis, not a stat problem |
| Art direction | Visible vent-slits along the flank glowing dull orange when digesting, cooling to grey between cycles |
| Canon note | Original — sibling in concept to `urrak`, explicit cousin naming recommended at build time |

### Ghurr — the cold-lung

| | |
|---|---|
| Role band | Medium, lean and long-necked — built for airflow, not bulk |
| Diet | Water, primarily — it needs to stay hydrated to keep its breath cold |
| Product | Ambient refrigeration — no discrete item, a standing cooling aura in the room it's stabled in, like a swamp cooler run backwards |
| Rate & process | Passive as long as watered; skip its water for a day and its breath warms to ambient, killing the effect until re-hydrated |
| Valve | It trades the desert's scarcest resource (water) for cooling, which is a genuine trade-off rather than a free good — a caravan that waters its ghurr generously is a caravan short on drinking water |
| Temperament | Skittish in heat, calm in any cool space — visibly happier the colder the room |
| Story hook | Caravans without a functioning cooler unit bid absurdly for a healthy ghurr before a hot-tile crossing |
| Art direction | Pale, vented nostrils and a faint visible cold-breath mist even at rest |
| Canon note | Original |

### Vashik — the sand-filter worm

| | |
|---|---|
| Role band | Long and sinuous, low bodyweight for its length — the spindly exemption applies |
| Diet | Raw ore-bearing desert sand, ingested continuously while grazing/burrowing |
| Product | Purified silica sand and glass-grade beads, passively excreted as it moves |
| Rate & process | Yield scales with how MUCH ground it's allowed to work — a fenced worm in a small pen produces little; one allowed a long burrow run produces steadily but is harder to keep contained |
| Valve | Containment is the cost, not feed — a vashik allowed to roam widens its own paddock by digging, so keeping one productive means constant fence maintenance labor |
| Temperament | Utterly harmless, mildly startling (it surfaces without warning) |
| Story hook | A vashik that burrowed under a wall foundation and nobody noticed until the wall settled |
| Art direction | Segmented, sand-toned, near-invisible against dune texture until it moves |
| Canon note | Original |

### Chiffik — the circuit-eater

| | |
|---|---|
| Role band | Small, ferret-sized, quick |
| Diet | Dead electronics — burned boards, fried components, anything with recoverable rare-earth flecks |
| Product | "Glitter dust" — a slow trickle of rare-earth material used in advanced electronics crafting |
| Rate & process | Tiny yield per feed, but it will eat things nothing else in the economy wants (e-waste with no scrap value) — its value is turning garbage into a slow trickle rather than a fast stream |
| Valve | The yield is intentionally too small to matter at scale; it exists to make one specific waste stream non-worthless, not to become a supply chain |
| Temperament | Curious, grabby, will investigate any unattended tool bench |
| Story hook | A colony's chiffik develops a habit of "stealing" unattended electronics before they're dead — a running low-stakes theft gag |
| Art direction | Small, glinting, magpie-like posture even though it has no wings |
| Canon note | Original |

---

## 3. UTILITY SYMBIOTES — the colony lives alongside it, not off it

These aren't feed-in/product-out printers. They're creatures whose presence
or upkeep IS the mechanic — armor you harvest without killing, a debt you
didn't know you were accruing, a herd you sleep inside, a pet with a mind
of its own.

### Karrask — the molt-plate

| | |
|---|---|
| Role band | Medium, armadillo-to-pangolin scaled, low and armored |
| Diet | Mineral-rich rock lichen — a slow forager, not demanding |
| Product | A full shed carapace every molt cycle (~15 days), curable into light plate armor |
| Rate & process | The plate must be CURED (a crafting job, days-long) before it's wearable — a raw shed is brittle and useless. Gentle handling during the molt (don't disturb the molting site) yields a cleaner, higher-quality shed than a rushed or interrupted one — a soft reward for patience. |
| Valve | Territorial specifically about its molting site; disturb a molting karrask and it turns aggressive and the shed is ruined — you cannot force the schedule |
| Temperament | Placid grazer, briefly dangerous once a molt cycle |
| Story hook | A prized "clean-shed" karrask whose molting corner has become an unofficial shrine — nobody builds near it |
| Art direction | Overlapping plate segments in muted desert tones, a visible seam line where the next shed will split |
| Canon note | Concept-adjacent to Geonosian chitin-armor culture; original creature |

### Moornak — the grief-eater

| | |
|---|---|
| Role band | Small-medium, unsettling — too many eyes for its size, moves in slow deliberate steps |
| Diet | Nothing conventional — it is drawn to a grieving pawn and, kept near, visibly absorbs the mood debuff, easing it faster than time alone would |
| Product | Mood-recovery utility — NOT a substance |
| Rate & process | It doesn't destroy grief. It STORES it. Every debuff it absorbs accrues as a hidden liability on the animal itself. |
| Valve | **The terrible secret, and the entire design:** if a moornak dies — old age, slaughter, an accident — every debuff it has ever absorbed releases back onto the colony at once, scaled by however long it's been fed. Keeping one is a slow-growing bomb you have chosen to defuse later, never now. The only clean resolution is a deliberate, prepared "unburdening" ritual-adjacent event (a controlled release, braced for) rather than an accidental one. |
| Temperament | Eerily calm, never flinches, colonists report it "watching" |
| Story hook | An old moornak that's outlived three owners, never once released — and everyone in the colony quietly hopes it dies on someone else's watch |
| Art direction | Matte-black, faintly damp-looking hide, too many small dark eyes set asymmetrically |
| Canon note | Original — pairs thematically with Rekko (the debt you owe the discarded) and Mob'Unloo (the ledger always comes due) |

### Duskhide — the night-heater herd

| | |
|---|---|
| Role band | Large, bison-scaled, herding |
| Diet | Tough scrub forage, a genuine grazer |
| Product | Living warmth — the colony sleeps among the herd on cold nightside-adjacent tiles, a real temperature/comfort buff to nearby sleepers |
| Rate & process | Passive, ambient, herd-size-scaled — a bigger herd warms a bigger radius |
| Valve | Overheats badly on hot dayside tiles — the same forage-hostile/heat-hostile guardrail that already caps the resource beasts applies here by nature, not by rule: a duskhide herd simply cannot survive the itinerary's hot legs, so it self-culls to "useful on the cold legs only" |
| Temperament | Herd-bonded, calm, mildly claustrophobic if penned too tight |
| Story hook | The one caravan leg every season where the duskhide herd is the only reason nobody froze |
| Art direction | Shaggy, heat-shimmer visible off the flanks even in cold air, herd-clustering body language |
| Canon note | Original — the terminator-cold complement to the existing hot-desert roster |

### Voltling — the wandering battery

| | |
|---|---|
| Role band | Small, cat-sized, low to the ground |
| Diet | Ambient charge — recharges itself from sun exposure or a nearby active conduit |
| Product | Autonomous power donation — left unpenned, it will actually seek out and touch the LEAST-charged battery or conduit in the base and donate a trickle of its own stored charge |
| Rate & process | Modest passive trickle per donation; it re-charges itself afterward and repeats on its own schedule — the charm is that it manages itself, no feeding job required |
| Valve | If it can't find sun or an active conduit for too long it goes dormant (harmless, just inert) until recharged — it cannot be forced to produce on demand, only encouraged to stay topped up |
| Temperament | Twitchy, drawn to warmth and light, genuinely affectionate once bonded |
| Story hook | A voltling that's learned to sit on top of the ONE thing that must never lose power, and nobody has the heart to relocate it |
| Art direction | Small, rounded, faint bioluminescent seams that dim visibly as it discharges |
| Canon note | Original — the small-scale, autonomous cousin to `vokka` |

---

## 4. ABSURD ECONOMY — the pampering, or the con, IS the cost

Creatures whose product only exists because of a deliberately absurd
labor cost, or because the "value" is a fiction the buyer hasn't checked.
The self-limiting valve here isn't cargo or danger — it's labor, spoilage,
or reputation.

### Coo'la — the story-milk doe

| | |
|---|---|
| Role band | Medium, doe-proportioned, gentle |
| Diet | Standard grazer forage |
| Product | A rare luxury dairy, usable in high-tier cuisine and as a trade good in its own right |
| Rate & process | It will not let down milk for a bucket alone. It requires a dedicated pawn performing an actual **Tend & Narrate** job — sitting with it and telling it a story, gated on a Social check — for the full milking session. Rushed, silent, or interrupted sessions yield thin, bitter product worth a fraction. |
| Valve | The labor cost is real and ongoing: a full-time (or near-full-time) storyteller job, and the milk spoils fast, forcing quick consumption or quick sale rather than stockpiling |
| Temperament | Attentive, visibly listening, distressed by silence |
| Story hook | The clan's best storyteller quietly resents that their finest work is performed for an audience of one animal |
| Art direction | Large, expressive ears angled forward, a soft attentive posture unlike any other grazer |
| Canon note | Original |

### Grubbin — the silver-eater

| | |
|---|---|
| Role band | Small, rodent-scaled, unremarkable to look at |
| Diet | Raw silver coin |
| Product | Excreted "silver" — assays close enough to pass a quick check, but the con is real: over a month it returns roughly 80% of what it was fed, in a slow trickle of alloyed, slightly-under-pure metal |
| Rate & process | A genuine NET LOSS to whoever keeps it — the entire point |
| Valve | Its only value is as a CON ITEM sold to a mark who does the surface-level math ("it makes silver!") and not the assay — a Jawa clan sells the grubbin, never keeps one; the buyer eats the loss. Mechanically self-limiting because it is bad economics to actually own one. |
| Temperament | Placid, faintly smug in animation only |
| Story hook | A Cartel underboss who's been quietly feeding his grubbin for a year and hasn't done the arithmetic yet |
| Art direction | Dull, coin-toned fur with a faint metallic sheen, disproportionately content expression |
| Canon note | Original — the mechanical embodiment of Mob'Unloo's "successful theft is the perfect deal" |

### Plumaq — the beauty-pampered plume bird

| | |
|---|---|
| Role band | Small-medium, peacock-scaled |
| Diet | Standard omnivorous forage |
| Product | Iridescent plumage, harvested at molt, used in high-fashion apparel and luxury trade goods |
| Rate & process | Plumage quality is gated on the Beauty stat of the room it's kept in at molt time — a plain pen yields drab, low-value feathers; an enriched, deliberately beautiful pen yields the prized iridescent grade |
| Valve | The cost is opportunity cost: building and maintaining a genuinely beautiful pen (art, clean flooring, no clutter) is real labor and real space that competes with every other use of a beautiful room |
| Temperament | Vain in the literal mechanical sense — visibly displays more in nicer surroundings |
| Story hook | A settlement's single most beautiful room turns out to be a bird pen, and everyone has opinions about that |
| Art direction | Bright plumage that visibly dulls in a shabby setting — the animal itself is a mood-o-meter |
| Canon note | Original |

---

## 5. HERDING DRAMA — the herd as instrument

### Gorrath — the aimed stampede

| | |
|---|---|
| Role band | Huge, heavier than a Bantha, built for mass |
| Diet | Bulk grazer forage, herd-scale |
| Product | None directly — this is a combat tool, not a resource animal |
| Mechanic | A trained herd's stampede can be triggered ON COMMAND and aimed at a target direction — enemies, a weak wall, a chokepoint. One trigger, then a real cooldown while the herd re-forms and calms. |
| Valve | Owning and cargo-hauling a full herd is expensive by the standing gravship-cap guardrail already, and a badly aimed trigger stampedes THROUGH your own base as easily as an enemy's — the training investment and the misfire risk are the brakes, on top of the cargo cost |
| Temperament | Calm until triggered, briefly uncontrollable once moving, slow to re-settle |
| Story hook | A raid broken by a stampede nobody quite meant to fire that early |
| Art direction | Low, wide, horn-heavy silhouette; visual weight communicates "do not stand here" |
| Canon note | Original — the weaponized cousin of Bantha-caravan culture |

### Hollowfoot — the undermining grazer

| | |
|---|---|
| Role band | Large, low-profile, thick-limbed for digging rather than speed |
| Diet | Root-fiber, found under structures and packed ground — it eats the thing holding foundations together |
| Product | None directly — a siege tool and a hazard in one |
| Mechanic | Directed at an enemy wall, it burrows and undermines the foundation over time — a slow, quiet siege option. Left unsupervised near your OWN structures, it does the same thing to you. |
| Valve | Requires active fencing/zoning discipline at all times, not just during an attack — an unmanaged hollowfoot is a standing structural threat to its own keepers, which is what stops every colony from just owning one for free |
| Temperament | Placid, easily startled into fleeing (which is when it digs fastest, panicked) |
| Story hook | A grain silo that settled six inches overnight and no alarm ever went off |
| Art direction | Squat, powerful forelimbs, dust-caked, almost never fully visible above ground |
| Canon note | Original |

---

## 6. Cross-family notes

- **Onnik's fired ceramic and vashik's purified sand are a matched pair** —
  a colony that keeps both effectively has an in-house pottery/glass supply
  chain running on two animals instead of a building. Worth authoring as a
  deliberate combo at build time (§8.4 crossover with the tar-pits proposal
  is a further natural link, since tar-preserved goods want durable
  ceramic storage).
- **Moornak is the one entry in this document that argues against itself**
  — a genuinely useful mood tool that becomes more dangerous the longer it
  works. That tension is the whole pitch; do not soften it by adding an
  easy safe-release button at build time.
- **Beast-normalization compliance:** none of these are unusually large or
  dangerous for their stated role band except gorrath (deliberately huge,
  deliberately dangerous-when-triggered) and hollowfoot (large, structural
  danger rather than combat danger) — both should get an explicit
  exemption note rather than a silent oversized stat block when patched.

---

## 7. Grounding against the xenohusbandry research corpus (ingested 2026-08-31)

The owner surfaced a deep buildings/art-cost/event-mechanics research pair
after this document's first draft:
`research/Jawa/star_wars_rimworld_xenohusbandry_buildings_art_costs.md` (468
lines) and `research/Jawa/star_wars_rimworld_xenohusbandry_aquaculture_event_design.md`
(800 lines). Both are pitched broader than this document — full ranch/pit/
aquaculture/aviary/hive/vacuum/bioculture facility catalogues for the whole
campaign, not just these 14 — but three findings land directly on this doc
and revise it below rather than sitting as a separate citation.

**1. Every creature here maps onto an existing facility TEMPLATE, not a
blank page.** The buildings corpus already worked out the placement-rule
grammar (hard restrictions players can *see the reason for*: terrain,
temperature, power, clearance — soft penalties for everything cosmetic:
odor, mood radius, escape-on-damage). Applying it to this roster's harder
valves:

| Creature | Nearest corpus template | What it borrows |
|---|---|---|
| Onnik | Dung Fuel Press × Trufflite Bed hybrid | squat, ugly, dry-boosts-speed placement logic |
| Drassik | Mineral Paddock | scrap/ore feed trough; "never overlap valuable resource stockpiles" |
| Ghurr | Cryo Nursery | "exploit natural frostside cold to reduce power" — ghurr should get the same siting bonus |
| Vashik | Sandmaggot Dune Bed | sand/soil-only, outdoors, uncontained-perimeter logic |
| Chiffik | Hull-Scrap Feeder | "accepts scrap/slag; reduces chance animals attack useful equipment," scaled down |
| Karrask | Bantha Grooming Frame | "animals voluntarily use it when comfortable" — gates the gentle-handling quality bonus |
| Moornak | *(no template exists — genuinely novel against this corpus)* | a bespoke Symbiont-Monitor-style console reading its accrued liability is the natural building hook |
| Duskhide | Kod'yok Snow Paddock Shelter | inverted: a warmth-*emitting* herd shelter instead of a cold-*resisting* one |
| Voltling | Sacrificial Power Bus / Mynock system | the autonomous, self-directing feed pattern already exists for a different creature |
| Gorrath | Deep-Beast Pit's containment logic | scaled to a herd rather than a single dangerous predator |
| Hollowfoot | Terrafin Rock Yard | "anti-dig mesh… no adjacent unreinforced walls" — direct precedent for the undermining valve |

Coo'la, grubbin, and plumaq have no facility precedent because their valve
is *labor*, not *containment* — correctly so; nothing in the corpus's
building catalogue models a story-time job either.

**2. Art-cost realism forces a shared-sprite-family build order, not 14
bespoke creatures.** The buildings corpus's own larger catalogue (40+
proposed buildings) explicitly compresses to "roughly 20–25 genuinely
distinct art assets plus overlays and recolors" via shared silhouette
families — and its own recommended first wave is 12 items, not the full
set. Applied here: **do not plan full bespoke art for all 14 creatures.**
Group by body-family before any art is commissioned:
- *Thick-hided industrial* (onnik, drassik) — one heavy-set base body, a
  kiln-vent head/back overlay vs. a gland-and-vent overlay.
- *Small scavenger* (chiffik, grubbin, voltling) — one small quadruped
  base, differentiated by texture/colour and a held prop (chiffik's
  glinting salvage, grubbin's dull coin-sheen, voltling's bioluminescent
  seams).
- *Armored grazer* (karrask, hollowfoot) — shared low-slung plated base.
- *Herd bison-scaled* (duskhide, gorrath) — shared large-herd body,
  different horn/heat-shimmer overlays.
This revises §6's cross-family note about art scope from a soft aside into
a hard sequencing rule (below).

**3. The event-mechanics half (rare breeding/escape/disease events, feed-
quality-affects-product, mating-season states) makes every valve above
mechanically real instead of narrative-only, and belongs to whichever
creature already has a schedule to disrupt:** moornak's stored-liability
release is exactly the corpus's "brood rejection" event shape (§7.8 of the
aquaculture doc) applied to mood instead of a physical symbiont; drassik's
choke-on-mixed-feed is the corpus's "feed affects product" mechanic (§6.2)
with a failure branch added; gorrath's stampede misfire and duskhide's
heat-stress cull are both direct reskins of the corpus's mating-season and
environmental-failure event families (§7.5, §7.7) rather than anything
novel to invent.

**4. Aquaculture is the corpus's largest adjacent family and this document
deliberately does not annex it.** The aquaculture/event doc catalogues an
entire water-dwelling husbandry layer (raceways, roe incubation, live-tank
species) that overlaps far more with the Cantina Kitchen live-food fiction
(`design/V2_DREAMS.md` §"The Cantina Kitchen") and the high-cuisine
proposal's ingredient-rarity pantries than with land livestock. Rather than
force a fifth family in here to cover it, that ground is ceded explicitly
to `design/Jawa/proposals/high_cuisine_deep_design.md`, which cites the
same corpus for its own live-ingredient and roe sections. If a future pass
wants a dedicated aquaculture livestock family, the corpus's §12
"first-wave" ten systems are the correct starting menu, not a fresh
brainstorm.

---

## Build ladder

- **v1 slice:** two entries only, chosen for zero new job types AND a
  shared art base — **onnik** (kiln-belly, straightforward feed-cycle) and
  **karrask** (molt-plate, straightforward harvest-on-schedule). Both slot
  into the existing animal-husbandry loop with no new pawn-job code, and
  onnik doubles as the first half of the "thick-hided industrial" shared
  body once drassik follows in v2 — proving the family reads as intended
  before anything harder ships.
- **v2:** the rest of INDUSTRIAL GUTS and UTILITY SYMBIOTES (drassik,
  ghurr, vashik, chiffik, moornak, duskhide, voltling), built in shared-art
  batches per §7.2 rather than one at a time, plus a first pass at ABSURD
  ECONOMY's labor-gated products (coo'la's Tend & Narrate job is the hard
  one — needs the new job type built once, then reusable).
- **Dream:** the full ABSURD ECONOMY set including grubbin as a working
  buyer-facing con in the trade UI (an assay check the AI trader can fail),
  and HERDING DRAMA's two weaponized herds with full misfire/friendly-fire
  simulation — the riskiest entries, correctly last. A dedicated
  aquaculture livestock family (§7.4) is dream-tier and out of this
  document's scope entirely.
