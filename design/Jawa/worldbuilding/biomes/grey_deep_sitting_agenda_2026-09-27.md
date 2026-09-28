# The Grey Deep — sitting agenda, 2026-09-27

> ✅ **THE SITTING HAPPENED AND ALL 17 QUESTIONS ARE RULED** — 2026-09-27, five card
> rounds, recorded on `GREYSEA_FLOOR_PASS_1`. Each question below carries its ruling
> inline; nothing in §2 is open any more. This document is now a record, not an agenda.

Prepared for the `GREYSEA_FLOOR_PASS_1` owner sitting. Two halves: **§1 is the merged
proposal** — everything the sheet, the content drop, the flora pass and the danger pass
add up to, read as one place; **§2 is the card agenda** — every decision that was still
open going in, numbered Q1–Q17, each with options and trade-offs, now each carrying its
ruling. **§3 is the list of what was already ruled beforehand**, so the sitting never
re-litigated.

## 0. Provenance and how to use this document

Synthesized 2026-09-27 by a DESIGN subagent for BENCH from: the frozen sheet
`the_grey_deep.md` (including its 2026-09-26 additive merge — the owner's own ruling:
*"Merge them into the sheet. It doesn't overwrite it, it adds to it"*), the verbatim
content drop `the_grey_deep_content_2026-09-26.md`, the flora pass
`the_grey_deep_flora_pass_2026-09-27.md`, the danger/floor pass
`the_grey_deep_danger_floor_pass_2026-09-27.md`, the `GREYSEA_FLOOR_PASS_1` /
`GREYSEA_SHIP_CRYSTALLISATION_1` / `DARKSEA_LIGHT_ATTRACTION_1` ledger histories, and
the live defs under `src/RimMandrake/TerminalBiomes/` and `src/RimMandrake/DivingInteraction/`.

**Nothing here re-designs anything.** Where a source already answers a question, the
answer is repeated and cited; where sources disagree with the disk, the disk was read
and wins. Two corrections of stale framing, measured against `src/` today:

- **The pillars are BUILT.** The item prose still calls the formations "the biggest
  hole — currently NO def of any kind." That was true 2026-09-26 and is not true now:
  `GREYSEA_FLOOR_FORMATIONS_1` is **done** (`RM_GreySeaFormations.xml`,
  `RM_GreySeaFloorScatter.xml`, `RM_GreySeaTerrains.xml`,
  `GenStep_GreySeaFloorDressing.cs` — pillars, domes, chimneys, jacket mineral, four
  great crystals, brine channels, the carved pool). What is still open is the
  **navigation** half of the pillar law, not the pillars (Q1).
- **Nearly every child item is done.** `GREYSEA_CRYSTAL_FLORA_1`,
  `GREYSEA_SALT_SNOW_WEATHER_1`, `GREYSEA_BRINE_POOL_DEFENCE_1`,
  `GREYSEA_BRINE_ELDERS_1`, `GREYSEA_SALT_CUISINE_1`, `GREYSEA_SESSILE_LAYER_1`,
  `GREYSEA_SHORE_MUTATOR_SPECIFICS_1` and `GREYSEA_FLOOR_FORMATIONS_1` all read
  **done** in the ledger; the Grey slice of `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` is built
  (all seven catch species have living floor bodies) and `GREYSEA_CATCH_TIER_RENAME_1`
  landed (the catch is `RM_*Catch` throughout). This sitting is therefore mostly a
  **ruling and ratification sitting**, not a commissioning one.

## 1. The merged proposal — the Grey Sea floor as a place

What a player actually meets, start to finish, with every piece traced to its source.

### 1.1 Getting there

The gravship is the only way down and the only way back (owner, verbatim: *"It's ship
or nothing"*). The ship lands on the Grey floor — a generated pocket map,
`RM_SeaDiveGenerator_GreySea`, temperature 12, murk-fogged — and everything below
happens on foot from the parked hull, which is itself in play from the moment it
touches down (§1.6).

### 1.2 The floor you walk

Grey-green murk, sight measured in meters, floored with strange mineralogy and death.
The dressing genstep carves the tile's **deepest brine pool**, rings it with **jacket
mineral** (the salt twin of Odyssey's SolidIce — everything the sea has kept, standing
in crystal), paints **chimney seep aprons** and runs **brine channels** downhill from
the chimney fields into the pool — so the floor's gradient always points at the danger.
Between them: the **pillar wonderland** (banded white mineral columns, the mason's
work, the only landmarks in the murk), squat **salt domes** like mushrooms, venting
**salt chimneys** whose plumes crystallise at short range (the visible teacher of what
the pools do invisibly), and four kinds of **great salt crystal** — the treasury,
harvestable and rather valuable. Salt falls like snow (`RM_GreySaltSnow`), the floor's
one weather. All of this is built.

### 1.3 What grows

Two flora layers, deliberately distinct:

- **The monuments** (built, the owner's own seven, verbatim specs): cubic sculptures,
  sphere plants with spine weaponry, Glass Veil Kelp curtained over the channels,
  Brine Crown anemoflora that retracts to a mineral porcupine, Mosaic Fan Palms, Salt
  Chimney Vines on the vents, Crucible Pods. Pink, violet and amber — the floor's only
  colour, mineral not glow, every form marred and never perfect.
- **The understorey** (designed, this sitting rules it — Q3–Q9): ten small soft grey
  things between the monuments, each a different answer to hypersaline cold water —
  the mason's mat skirting the pillar feet, salt-sweating beards on the formations,
  filament nets that sort food from salt by touch, a sponge that freshens the water
  around it, a soft coral turning itself to stone on a schedule, a plant that is
  usually a puddle, a bone-white lily riding the pools' surface, gradient-eating combs
  stitched along the channels, the sprig salt cannot take, and a cushion that only has
  colour while a player's lamp burns. The monuments are crystal; the understorey is
  flesh and felt.

### 1.4 What lives

A floor of small solitary things under one enormity — the sheet's silhouette law in
numbers. Anchors: **the crusted giant** (`RM_Reefback`, bodySize 32, indistinguishable
from a pillar until it moves, its saturated mate-mark the only glow the biome has ever
contained) and **the ossuary shrimp** (`RM_Fessk`, man-sized, shy, intelligent — it saw
you first). Around them: the pillar-snail, the statuary-grazer, the ribbon-swimmer on
the density interfaces; the sessile three (small shrimp, clam, mussel — all new, all
solitary placements, never swarms); and the seven fish-bodies derived from their own
catch descriptions — the pebble-crab, the flat plate-fish, the sealed bivalve, the
blind brine-eel, the half-stone jelly, the lamp-pink shell-lodger, and the haarn, whose
rare scrape-line is a deliberate false positive against the giant's tell. Every catch
species also swims the floor; every floor species that is catchable has its `*Catch`
twin. `animalDensity` is 0.1 — the roster is live, not dead content.

### 1.5 The danger, in layers

- **The pools** (the owner: *"the center of the weird mechanisms"*): touch one and you
  are crystallised where you stand — encased as an object, mined out by your friends,
  never a hediff (ruled). Their loot is ultra-protected; the chimneys teach the
  mechanism in the open, the pools never warn.
- **The light economy** (redirected here from the Twilight by his ruling — on this
  floor a player lamp is the brightest thing the sea has ever contained): lit cells
  yield more (ruled — the bribe is mechanical), the small sighted things drift in, the
  fessk arrives at the rim of the lamplight and watches (ruled — the layer-2 tell),
  and a strong steady light burning for hours reads, to the one creature wired for
  glow, as a rival's mate-mark — the giant comes to break the lamp, not the ship, not
  the pawns (ruled). Light discipline is the Grey's survival craft.
- **The ship being filed** (ruled: *"The grey sea should crystallize the hull, freeze
  doors shut"*): a parked hull accretes the same jacket mineral as the statuary — rime,
  then salted doors, then a launch gate counting chipping work. Doors salt from the
  outside and always force open from the inside (ruled: never a tomb); chipped crust
  pays out salt crystal (ruled: the sea pays you); the counters are chipping and
  leaving, not heat (ruled). A wreck nobody chipped, generations on, is
  indistinguishable from the statuary — the sea's museum acquiring its newest exhibit.
- **The Elders** (one per Grey tile, ruled): from each tile's deepest pool a colossal
  branching salt-crystal organism, older than every faction, discharging when its pool
  is disturbed and rarely on its own — with a visible charge build-up as the tell. It
  trades in novelty: first specimen of anything is precious, every later one worthless,
  and each tile's Elder keeps its own seen-set — the Grey's tiles are a distributed
  market. It pays in matter no craftsman can make and in one-of-each treasures (three
  canon, patched; three invented, `RM_`).

### 1.6 The economy

Salt in four colours for the cuisine mod (built: white, pink, violet, amber — Q16
ratifies the palette); the great crystals and the jacket's yield; the jacketed salvage
— half the value IS the case; pillar stone; the giant's shed crust; a rich and bizarre
catch (Q2 settles its breadth); the pools' locked treasury with two keys (chisel, or an
Elder's exchange); and the Elders' novelty trade, where a colonist of a new xenotype is
an offering.

### 1.7 What the sitting settled — all of it

Everything this section once listed as unsettled was ruled 2026-09-27: pillars story
only (Q1), the catch kept-all rebalanced rare (Q2), the whole understorey shipping at
0.22 (Q3–Q9), the crust ladder with weather+berth multipliers and nothing purchasable
(Q10–Q11), the giant deterministic and forgiving (Q12), the orruhmu (Q13), the Elder's
motion-only tell (Q14), the useless artifact's plot hook filed (Q15), the salt palette
ratified (Q16), and the other seas' ship-touch voices left to their own passes (Q17).
The per-question rulings stand inline in §2.

## 2. The card agenda — open decisions

Each question: one paragraph of framing (only what changes the answer), 2–4 genuinely
different options with the trade-offs both ways, and a one-line recommendation. Plain
language throughout; def names appear only as citations, never as the choice itself.

---

### Q1 — The pillars are built; is getting lost a mechanic or a story?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): story only — no waymark job, no murk penalty, navigation stays perfect (overrides the (b) recommendation); the pillar forest is layout and prose.

The sheet's law is that all travel below is pillar-to-pillar, divers carve waymarks,
and a lost diver is someone who missed one pillar. The pillars themselves now stand on
every Grey floor (mineable, impassable, landmark-sized), and their descriptions carry
the waymark fiction — but nothing in play makes navigation matter: a pawn pathfinds
perfectly through the murk, so "lost" cannot currently happen. What changes the answer:
how much the biome's signature idea deserves to cost, and whether frustrating a pawn's
pathfinding ever feels good in this engine.

- **(a) Story only.** The pillar forest is layout and prose; navigation stays perfect.
  *For:* zero cost, zero frustration, ships now. *Against:* the biome's single most
  distinctive law — the thing the sheet calls "this world's lane-travel pattern taken
  underwater" — never touches play; the wonderland is scenery.
- **(b) Carveable waymarks, gentle benefit.** A small job on a pillar cuts a waymark;
  marked pillars give nearby pawns a modest move/work bonus (a known route) and a mood
  touch, and old waymarks from dead divers spawn pre-carved. *For:* the law becomes a
  ritual the player performs, cheap to build, no pathfinding surgery. *Against:* a
  bonus for clicking every pillar risks reading as busywork if tuned wrong.
- **(c) Real murk navigation.** Away from pillars and lit ground, pawns slow down and
  work worse (a "blind ground" penalty the pillar-adjacent cells are exempt from) — the
  floor is genuinely navigated pillar-to-pillar. *For:* the murk becomes a mechanic and
  the pillar routes are real. *Against:* the heaviest option; global slow-downs punish
  every haul job forever, and it fights the lit-cells-yield-more ruling (light already
  prices visibility).
- **(d) b + a lost-wanderer beat.** Waymarks as in (b), plus a rare arrival: a lost
  diver-wanderer event on the floor, found encased or saveable near an unmarked run.
  *For:* the proverb becomes an event a player remembers. *Against:* event work for a
  map most colonies visit briefly.

**Recommendation: (b)** — it makes the law playable at the price of one job and one
small bonus, and (c)/(d) can layer on later without waste.

---

### Q2 — The catch table is rich; the sea's law is sparse. Coexist or thin?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (c) — KEEP ALL 13, REBALANCED RARE: lower fish population, push species into the uncommon/rare bands, sparseness felt at the dock (overrides the (a) recommendation).

Carried to this sitting by name (from `TERMINALBIOMES_RM_MOD_BUILD_1`, 2026-09-25).
You ruled fish YES, and bizarre — that stands. The question left is breadth: the live
def offers **13 catch species** (8 common, 4 uncommon, 1 rare table) at a healthy fish
population, while the sheet's register is "solitary everything," and the original
roster verdict this table predates was sparser. The floor side is already reconciled —
every catch species now also lives on the floor as a solitary body, so nothing schools.
What changes the answer: whether "sparse" is a law about the water or about the
fishing line — the catch is the shore-camp's economy and the free mod's whole fishing
game here.

- **(a) Coexist, annotated.** Keep all 13; write one sentence into the sheet: the
  murk hides plenty, the line finds what the eye never will — sparse is what you SEE,
  not what the sea holds. *For:* nothing built is wasted; fishing stays varied and
  strange; the floor's visible sparseness is untouched (it is governed by animal
  density, which stays low). *Against:* 13 species is a generous larder for the
  planet's bleakest sea; the Twilight (the rich sea) has 12, so the Grey out-catching
  it reads slightly wrong at the register level.
- **(b) Thin to the seven-plus-anchors.** Cut the catch to the seven derived species
  plus the two anchor catches; the sessile three become floor-only. *For:* the catch
  reads as sparse as the sea. *Against:* deletes shipped, owner-derived content and
  their floor pairings for a register nuance nobody will count in play.
- **(c) Rebalance, don't cut.** Keep all 13 but lower the fish population and push
  more species into the uncommon/rare bands — every catch stays possible, most days
  yield little. *For:* sparseness becomes something the player feels at the dock
  without losing variety. *Against:* hungrier colonies just fish longer; it tunes
  tedium, not tone.

**Recommendation: (a)** — the solitary law was always about what moves in the water,
not the fishing line, and one annotating sentence keeps a later reviewer from
"fixing" the count.

---

### Q3 — How thick does the floor grow? (one number)

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (b) — plantDensity 0.22 ratified.

The flora pass adds a ten-species understorey beneath your seven crystal monuments,
and the whole thing hangs on one knob: plant density. Shipped today: 0.14, set when
the seven monuments were the only flora. The pass proposes 0.22 so the small new layer
actually appears between the monuments instead of losing the roll to them. What
changes the answer: the Grey must never read lush — it is the stiller, bleaker sea —
but a floor that is all mineral and no felt undersells the drop's "strange shapes
everywhere."

- **(a) Stay at 0.14.** *For:* bleakest read, no risk of lushness. *Against:* the
  understorey will be mostly invisible — ten designs paid for and rarely seen.
- **(b) 0.22 as proposed.** *For:* the understorey shows without crowding; still well
  under the Scald's proposed 0.30 (right: the Grey is the stiller sea). *Against:*
  more green-grey underfoot than the sheet's original barren image.
- **(c) Another number you name** (the roster works unchanged anywhere 0.14–0.30).

**Recommendation: (b)** — the sparseness law lives in the palette and the solitude,
not in bare sediment.

---

### Q4 — Does the whole understorey ship, and does anything on it get cut?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — all ten understorey flora SHIP, subject to Q5–Q8 (all four subsequently ratified).

Ten small flora, each with a different survival trick, none duplicating your seven or
any other sea's tricks, all names invented and collision-checked. Six are
uncontroversial dressing-with-ecology (the beard, the net, the sponge, the stone
coral, the puddle-plant, the channel combs). Four carry their own questions and get
their own cards (Q5–Q8). This card is the roster as a whole. What changes the answer:
each plant exists to make an already-ruled thing legible — the mason's presence, the
salt snow's aftermath, the pools' danger, the channels' gradient — so cuts remove
signage, not just decoration.

- **(a) All ten ship** (subject to Q5–Q8 on the four contested ones).
- **(b) Ship the six plain ones now**, hold the four contested until their cards rule.
- **(c) Cut the understorey to a handful** — name keeps and cuts row by row at the
  sitting; the pass's table makes that a five-minute read.

**Recommendation: (a)** — the layer was commissioned by your own card (every sea floor
gets its strange-flora pass, nothing barren), and it is the floor's food chain, not
garnish.

---

### Q5 — The cushion that is only colourful under your lamp: tribute to the
no-glow law, or violation?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — the murkblush SHIPS: structural colour, emits nothing, ban 4's tribute.

One understorey plant is deliberately special: a grey cushion, invisible among
everything else grey, that returns a player's lamplight as deep oil-sheen iridescence
— structural colour, like a beetle's shell. It emits nothing, ever; no lamp, no
colour. The murk law (ban 4: no light-source flora, the only glow is the giant's mark)
is untouched by the letter. What changes the answer: whether the Grey's greyness is a
fact about the sea (things HAVE no colour) or about the dark (colour exists and no
light ever reaches it). The plant argues the second — and it quietly deepens the light
economy, since a floor of blushing cushions is a map of which cells your dangerous
lamp is paying for.

- **(a) Ship it.** *For:* the biome's one reward for the risk the lamp already
  carries; the lamp-pink shell-lodger already uses this exact grammar, so the biome
  speaks it once already. *Against:* deliberate beauty in the bleak sea, even if
  honestly earned.
- **(b) Cut it.** *For:* the Grey stays absolutely grey under any light; nothing else
  references it, so it cuts clean. *Against:* loses the one flora that makes the
  lit-cells ruling visible on the ground.

**Recommendation: (a)** — it is ban 4's tribute, not its exception: every photon is
the player's, and the sea keeps none of it.

---

### Q6 — May a piece of the pillar-mason become a plant?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — the mason's skirt IS a plant (RM_Masonmat); the mason itself stays def-less fiction.

The mason — the Grey's monoculture, the builder of the pillars — has always been
fiction: no def, no pawn, per your anchor-creatures ruling. The flora pass proposes
its floor-level skirt as a plant: a pale banded mat where the film spills off a
column's base, graze for the pillar-snail (whose shipped description already claims to
graze exactly this film). What changes the answer: it makes the biome's architect
partly touchable — and destructible — as "a plant" in a menu.

- **(a) Yes — the skirt is a plant; the mason stays fiction.** *For:* the snail's
  shipped sentence finally points at something real; the commonest living thing on the
  floor is the architect's skin, which is a lovely fact to walk on. *Against:* players
  can clear-cut the mason's edges without consequence, which slightly cheapens the
  untouchable builder.
- **(b) No — the mason stays entirely def-less.** *For:* the monoculture keeps its
  mystery whole. *Against:* the understorey loses its base mat, and the snail's
  description keeps pointing at nothing.
- **(c) Yes, but unharvestable and slow to destroy** — present, walkable, effectively
  permanent. *For:* touchable but not consumable. *Against:* an indestructible plant
  is engine-awkward and reads as scenery pretending to be flora.

**Recommendation: (a)** — the mason as a whole was never at risk; a grazed skirt makes
it MORE real, not less.

---

### Q7 — The sprig that salt cannot take: does it become an item with a use?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — PURE DRESSING, no harvest, no item; the rescue-item variant (b) noted as the only acceptable later opening.

One understorey plant survives by refusing crystallisation outright — brine cannot
seed a crystal on it, so it grows precisely where everything else is jacketed: the
pool shores, among the statuary, at the chimneys' reach. A cut sprig could plausibly
be the Grey's one plant product: an anti-crystallising agent. But you have already
ruled the crystallisation counters closed once — "no fuel-for-time trade; crust pace
is time alone; the counters are chipping and leaving" — and an anticrystallant paint
walks right up to that ruling's spirit. What changes the answer: whether that ruling
was about HEAT specifically or about any purchasable slowdown.

- **(a) Pure dressing.** The plant ships, nothing is harvested; its meaning is where
  it grows. *For:* the ruled counter set (chip, leave) stays exactly two entries;
  nothing to balance. *Against:* a flagrantly useful-sounding organism the player can
  never use — some will file it as a missing feature.
- **(b) A rescue item, not a prevention.** The sprig speeds mining OUT an encased pawn
  (or a salted door) but never slows accretion. *For:* it touches only the recovery
  half, which your rulings left open; a native first-aid for the biome's signature
  harm is good fiction. *Against:* a second knob on a mechanism that was ruled simple.
- **(c) A full anticrystallant** — applied to hull cells, slows the ladder. *For:* the
  obvious use. *Against:* this is exactly the trade your ruling refused, with plants
  in place of fuel.

**Recommendation: (a)** now, with (b) noted as the only acceptable later opening —
the ruling's spirit is "the sea is not negotiated with," and the sprig should obey it.

---

### Q8 — A flower on the killing pools: accept the one plant the player can never
reach?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — the pool lily rides THE SURFACE engine permitting; lip fallback silently.

The pools' surfaces get a resident: a bone-white lily riding the density interface
itself, root-threads down in the brine that kills everything. It is the biome's
warning made beautiful — a white flower seen through murk means a pool is there before
the pool's stillness can be read. It is deliberately, structurally out of reach:
no harvest, no entry, ban 1 whole. What changes the answer: engine reality — if a
plant cannot legally stand on the pool terrain, the fallback is the pool's lip, which
keeps the signage but loses the image of a flower on the deadliest skin in the biome.

- **(a) Yes, on the surface, engine permitting** (lip as the documented fallback).
  *For:* the biome's best small image; free danger signage. *Against:* a plant on
  water terrain may need a placement workaround that is pure fiddliness.
- **(b) Lip only, by design.** *For:* engine-trivial, signage intact. *Against:* a
  ring of flowers at the shore reads as garden edging, not a thing resting on death.
- **(c) Cut it.** *For:* the pools stay utterly unadorned. *Against:* loses the
  cheapest warning the murk can give a first-time visitor.

**Recommendation: (a)** — and if the engine refuses, (b) silently, since the
difference is invisible in a screenshot taken three cells away.

---

### Q9 — The sponge that makes gentle water: story only, or a small yield spot?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — PROSE ONLY; the ecology-clustering version (c) noted as the good later door.

One understorey sponge freshens the water around itself all its slow life — its halo
is where the soft-bodied things shelter, and when it dies it becomes a white cast of
itself and joins the statuary. The design question: does the halo DO anything? The
cheap mechanical read is a modest forage/fishing bonus on adjacent cells. But you
already ruled the biome's yield bonus: LIT cells yield more, bought at the lamp's
standing price. A free yield spot that needs no dangerous lamp competes with the
priced one. What changes the answer: whether the Grey should have any unpriced
generosity at all.

- **(a) Prose only.** The halo is description and creature placement flavour. *For:*
  the light economy stays the only yield dial; nothing competes with the lamp's
  price. *Against:* a mechanic-shaped sentence ships as a sentence.
- **(b) A small yield bonus in the halo.** *For:* rewards reading the floor; an
  old sponge ringed by its yard becomes a real prize worth siting a camp near.
  *Against:* undercuts the ruled bargain — why light a risky lamp when the sponge
  pays for free?
- **(c) The halo attracts the sessile catch instead** — no yield modifier, but the
  small creatures spawn/cluster preferentially in the yards, so fishing NEAR one is
  better because the fish are simply there. *For:* the same reward routed through
  ecology rather than a bonus number; doesn't compete with the lamp (the lamp still
  yields more anywhere). *Against:* subtler to build than a flat bonus.

**Recommendation: (a)** for this sitting — (c) is the good version if a later pass
wants it, and it costs nothing to leave the door open.

### Q10 — How fast does the sea file your ship?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — the proposed ladder: rime ~1 day · first salted door ~2–3 days · full jacket ~a quadrum.

The crystallising hull is ruled (it happens; doors freeze shut; never a tomb; the sea
pays you for chipping; no heat trade). The one thing no ruling touched is the clock.
The danger pass proposes a ladder — cosmetic rime from about a day parked, the first
salted door at two to three days, whole-footprint jacketing only after something like
a quadrum of neglect — so an attended colony meets stages one and two as texture and
never suffers stage three. What changes the answer: whether the Grey's touch should be
something a weekend visit feels, or something only a parked base fights.

- **(a) The proposed ladder** (rime ~1 day · first salted door ~2–3 days · full
  jacketing ~a quadrum). *For:* short visits see the beauty and one cheap chipping
  job; only neglect escalates. *Against:* a colony doing a two-day harvest dive barely
  meets the mechanism.
- **(b) Faster** (first door within the first day). *For:* every landing pays the
  toll; the sea feels aggressive. *Against:* chipping becomes a chore tax on every
  single dive, and the "rent, not raid" grammar tips toward raid.
- **(c) Slower** (doors at a week-plus). *For:* purely a base-builder's problem.
  *Against:* most players never see the biome's signature touch at all.

**Recommendation: (a)** — the first salted door inside a normal stay is the tutorial;
the quadrum-scale jacket is the story.

---

### Q11 — "Crust pace is time alone": does weather and parking spot count as time?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (b) — WEATHER and BERTH modify the pace; nothing the player buys ever does ('time alone' killed trades, not terrain).

Your ruling closed the heat trade: crust pace is time alone, the counters are chipping
and leaving. The danger pass, written before that card landed, also proposed two
environmental multipliers: accretion roughly doubles during salt-snow weather, and a
berth near a chimney field or brine channel accretes faster (the super-brine gradient
pricing parking spots). Strictly read, "time alone" may rule those out too. What
changes the answer: multipliers the player cannot buy off are not a trade — but they
do make the pace something other than time.

- **(a) Flat rate — time alone, literally.** *For:* the ruling's plainest reading;
  trivially predictable. *Against:* salt snow becomes pure scenery for the hull, and
  every parking spot is equal, which wastes the floor's own gradient.
- **(b) Weather and berth modify the pace; nothing the player buys does.** *For:*
  "where you park" and "what the sky is doing" are reading-the-floor skills, not
  purchases — the ruling's target (fuel-for-time) stays dead. *Against:* it is,
  plainly, no longer "time alone."
- **(c) Weather only.** Salt snow accelerates; location is flat. *For:* one visible,
  legible modifier tied to the biome's one weather. *Against:* half-uses the gradient.

**Recommendation: (b)** — the ruling killed trades, not terrain; a sea whose danger
gradient prices parking spots is the same sea whose gradient "always points at the
danger."

---

### Q12 — How forgiving is the giant about your lamps?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — DETERMINISTIC AND FORGIVING: worklight-class only, hours of burn, telegraphed, dowsing always resets.

Ruled: a strong steady player light reads as a rival's mate-mark, and the crusted
giant comes to break the lamp — not the ship, not the pawns. The open knob is the
threshold and the mercy. The danger pass proposes: only worklight-class light (never
a torch), only after hours of steady burn, telegraphed by the watcher at the rim and
by fresh scrape-sign, and fully preventable — dowse the lamps and the giant never
comes. What changes the answer: whether light discipline should be a craft the player
can execute perfectly, or a pressure that always carries some residual risk.

- **(a) Deterministic and forgiving** (bright + hours + telegraphed; dowsing always
  resets). *For:* a learnable craft; deaths are always the player's own read of the
  tells. *Against:* solved once, it never threatens again.
- **(b) Probabilistic pressure** (bright light rolls a growing chance; dowsing shrinks
  but never zeroes it while parked). *For:* the murk never becomes fully safe;
  long stays stay tense. *Against:* a giant that sometimes comes despite perfect play
  feels like weather wearing a creature suit.
- **(c) Deterministic, but the threshold tightens with repetition** — each broken lamp
  makes the giant read that hull's light sooner (it remembers the rival). *For:* the
  craft stays learnable but escalates, which suits an ill-tempered solitary with a
  memory. *Against:* per-giant memory is extra state for one behaviour.

**Recommendation: (a)** — the sheet's own principle is "the tell that lets the
observant survive," and that promise is only kept if reading the tells actually works.

---

### Q13 — Who else squirts? (the pool creatures your sentence left unnamed)

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (b) — ONE new pool-sentinel species designed fresh: the ORRUHMU (RM_Orruhmu, grey_deep_pool_sentinel_2026-09-27.md).

Your drop: *"Brine pools and the creatures near them have a unique defence: they
squirt out a protein shower causing ultra-rapid crystallisation."* Plural, and no
creature was ever named; the sheet records it as open and forbids inventing until you
rule. Today the crystallising set is: the pools themselves, the chimneys (ruled), and
the Elders. What changes the answer: whether the pools need a mobile guardian at all,
now that touching them, mining near them and disturbing an Elder all already punish.

- **(a) Nobody new — the set is pools, chimneys, Elders.** *For:* the mechanism
  already has three carriers and the fauna stays harmless-but-one, which is the
  Grey's danger philosophy (the place kills, the animals mostly don't). *Against:*
  your sentence says creatures, plural, and ships nothing for it.
- **(b) One new pool-sentinel species.** A single new solitary creature that haunts
  pool shores and squirts when crowded — designed fresh (we have surplus cast, and a
  hole is filled with a NEW creature, never a neighbour's). *For:* the sentence
  becomes a creature; pool shores get a guard that makes harvest runs tense.
  *Against:* one more def in a biome whose law is "do we already have one?".
- **(c) Retrofit the squirt onto an existing resident** — the helmet-sized jacket
  creature (the one animal already allowed to hurt you) gains it near pools. *For:*
  no new species; deepens an existing rumour-tier creature. *Against:* bends a
  built, reviewed creature's whole design after the fact.

**Recommendation: (b)** — the sentence promised creatures, and a single named
sentinel keeps the promise without a menagerie.

---

### Q14 — The Elder's warning light in a biome where nothing may glow

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — MOTION, CRACKLE and SOUND only; light exists only at the discharge instant.

Ruled: the discharge is both a defence and a rare event, with a visible charge
build-up on the limbs as the tell. Ban 4 stands: the only glow in the Grey Deep is
the giant's mark. The sheet leaves open how the tell RENDERS: your own word for the
discharge is "blinding," which is an event, not dressing — but a build-up that
players must notice in time has to be visible somehow. What changes the answer:
whether a seconds-long emergency exception to the no-glow law reads as a violation
or as the law's most dramatic proof.

- **(a) Motion, crackle and sound only — never light.** Arcing animation along the
  limbs, an audible charge-whine, a screen-shake cue; the flash exists only at the
  discharge instant. *For:* ban 4 keeps a perfect record until the one blinding
  moment. *Against:* in murk, motion-only tells are easy to miss at exactly the
  range that matters.
- **(b) A faint local flicker during build-up** — the lattice glimmers for the final
  seconds, then the flash. *For:* readable at range, still nothing standing.
  *Against:* it is, for those seconds, a second glow in the Grey.
- **(c) The tell is on the WATER, not the Elder** — nearby pool surfaces shiver and
  the salt snow around it hangs charged (particle behaviour, no light). *For:*
  wholly ban-clean and very alien. *Against:* the subtlest option and the most
  bespoke effect work.

**Recommendation: (a)** — with the discharge flash itself doing the teaching the
first time; the sheet already says the observant survive on motion and crackle.

---

### Q15 — The "beautifully useless artifact" needs a home before it becomes a thing

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — the plot hook is FILED (GREYSEA_USELESS_ARTIFACT_PLOT_1); the artifact is built when a plot names it.

Among the Elders' one-of-each treasures, five are buildable now (three canon,
patched; two invented besides this one). The sixth — *"some beautifully useless
artifact whose significance only becomes apparent much later"* — is a plot hook
wearing an item's clothes: built today, with no plot to pay it off, it ships as a
mislabelled trinket and the promise in its description becomes a lie. What changes
the answer: whether a plot thread exists (or is worth opening now) for the
significance to land in.

- **(a) File the plot item now, build the artifact when the plot names it.** *For:*
  the artifact arrives already meaning something. *Against:* the Elder ships with
  five treasures and an IOU.
- **(b) Ship the Elder with five treasures; add the sixth when a plot pass claims
  it.** Same as (a) but without filing anything today. *For:* zero speculative work.
  *Against:* unfiled intentions decay — the standing lesson is that "owed" lists
  nobody filed go stale.
- **(c) Build it now as a genuinely useless beautiful thing** and let a future plot
  retrofit significance. *For:* the treasure list is complete on day one. *Against:*
  the capture's own warning — it WILL be built as a trinket, and retrofitting
  meaning onto a shipped item is the harder surgery.

**Recommendation: (a)** — file the hook with one sentence of intent; it costs a
ledger row and keeps the promise honest.

---

### Q16 — The salt colours shipped on our guess — ratify or repaint

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (a) — RATIFIED: white, pink, violet, amber — one mineralogy with the flora.

The coloured cooking salts are built: white, pink, violet, amber — the same palette
as your crystal flora, on the explicit inference (recorded in the sheet as a BENCH
inference, not a ruling) that ingredient and plant should read as one mineralogy.
This card closes that loop. What changes the answer: only whether you want the
kitchen's salts to rhyme with the floor's monuments or to be their own thing.

- **(a) Ratify** — pink/violet/amber/white stands. *For:* one mineralogy, already
  built. *Against:* none of substance.
- **(b) Repaint** — name a different set (art regen on a handful of small items).

**Recommendation: (a)** — the inference was drawn from your own flora palette.

---

### Q17 — Do the other two seas get their ship-touch voices named today?

> ✅ **RULED 2026-09-27** (decision taken by question card, recorded on `GREYSEA_FLOOR_PASS_1`): option (b) — the Scald's and the Propane Lake's ship-touch voices wait for THEIR OWN passes.

The cross-sea grammar is ruled and half-filled: every sea touches a parked ship in
its own voice — the Twilight drops panes, the Grey crystallises. The Scald and the
Propane Lake have no ruled voice yet. This is the one agenda row that is about
scheduling, not the Grey. What changes the answer: whether naming two sentences now
is cheaper than re-opening the grammar twice later.

- **(a) Name both now, one sentence each** (e.g. the boiling sea furs the hull like
  a kettle; the cold lake sheathes it in condensate ice) — design lands at their own
  passes. *For:* the grammar table completes today; both later passes start ruled.
  *Against:* ruling on seas this sitting is not about, with their sheets not open in
  front of you.
- **(b) Leave both to their own passes.** *For:* each sea's voice is ruled with its
  whole register in view — the way the Grey's was. *Against:* two future cards that
  could have been one line today.

**Recommendation: (b)** — this sitting's discipline is one sea at a time; the
grammar table already reserves their rows.

---

### Sitting housekeeping (not cards — carried out on your word, no design in them)

- **Roster JSON amendment**: `rosters/the_grey_sea.json` still says `"flora": []`
  and lacks rows for the formations, pool grade, Elders and sessile layer — amend to
  match the sheet at this sitting (the sheet already records this as owed).
- **`GREYSEA_ANCHOR_CREATURES_1` disposition**: still `proposed` in the ledger while
  its substance shipped elsewhere (pillars built as formations, the ossuary shrimp
  lives as the built anchor cast, the aerofleet replacement ships in the shore-life
  file). Close or re-scope with a note.
- **Rare-catch tier leftovers**: the rare-catch table and the salt cameo still carry
  the campaign-layer prefix while every named catch moved to the free tier — a small
  owed migration already noted in the danger pass.
- **The Rakata eyewitness row**: `rakatan_legacy_index.md` owes the ruled row (the
  Elders' memory of the Reshapers' arrival — the planet's only eyewitness).
- **The live review sitting**: the item closes only when you walk the floor
  (`rimworld-live-review`); schedule it once the flora ruling from this agenda is
  wired.

## 3. Ruled inputs already settled — do not re-ask

Everything below is ruled and recorded; the sitting spends no time on it.

**The frame**
- The gravship is the ONLY way onto and off a sea floor — *"It's ship or nothing"*
  (2026-09-26). The pawn-dive mechanism is retired and deleted.
- The content drop MERGES INTO the frozen sheet as additions — *"Merge them into the
  sheet. It doesn't overwrite it, it adds to it"* (2026-09-26). Done; the sheet
  carries §4a–§4e.
- Grey Sea fish: YES — *"There should be fish"*, *"But bizarre creatures of course"*
  (2026-09-26). The catch is bizarre invented creatures, never reskinned vanilla fish.
- All five DLCs are assumed present, for us and for players.
- The sheet's six hard bans all stand (no pool entry · no schools/swarms · the shrimp
  never attacks, never tamed · no light-source flora · no decay of the encased · no
  vanilla-Earth organisms).

**The five "contradiction" flags — ALL RULED ADDITIVE, 2026-09-26** (the Elders beside
the one giant lineage · "abundant" sessiles as individual placements, never groups ·
chemically-cued retraction and pane-rotation are not the banned open-and-close ·
floor salt-snow is not the banned surface weather · warm mineral seeps are not the
banned cold gas vents). The sheet states each non-contradiction in place.

**The content drop's ten questions — ALL RULED at the bench, 2026-09-26**
1. A crystallised pawn is ENCASED AS AN OBJECT, mined out — never a hediff.
2. Salt chimneys also crystallise, at shorter range — the visible teacher.
3. Brine rivers = brine channel terrain strips, chimney field downhill to pool.
4. The shore is crust terrain PLUS scattered domes; NO harvestable shore salt.
5. The sessile layer is ALL THREE NEW — small shrimp, clam, mussel (this overrode the
   capture's position that the ossuary shrimp covers "shrimp").
6. The sphere plant does LOW contact damage.
7. The Elder's discharge is BOTH defence and rare event, with a visible build-up tell.
8. "Cripple nearby ships" is its own filed engine check; it blocks nothing else.
9. "The Reshapers" ARE the Rakata — the Elders' own exonym; not a new faction.
10. Elders are Grey Sea ONLY — *"ONLY grey sea, but there's one per grey sea tile"* —
    and each tile's Elder keeps its own seen-set (the distributed novelty market).

**Ship crystallisation cards, 2026-09-26**
- NEVER A TOMB — doors salt shut from outside only; inside always forces open; the
  danger is ship readiness, never crew air.
- NO heat-for-time trade — the counters are chipping and leaving (Q11 asks only
  whether weather/berth location modify pace; the heat ruling itself is closed).
- THE SEA PAYS YOU — hull chips yield the same salt-crystal item as floor mining.

**Light attraction cards, 2026-09-26**
- The crusted giant reads strong steady player light as a rival mate-mark and comes to
  BREAK THE LAMP — not the ship, not the pawns.
- Lit cells DO yield more — the bribe made mechanical.
- The fessk watcher is IN — stands at the lamplight's edge, never enters, never
  attacks.
- (BENCH engineering decision, standing unless vetoed: the light-attraction settings
  gate generalises to a per-sea toggle when the Grey wiring lands.)

**Fish-bodies and catch**
- Every fishable lives on the floor too, in every sea (owner, 2026-09-26) — the Grey's
  seven are BUILT and wired, verified sentence-against-field in the danger pass.
- The catch tier rename is DONE (`GREYSEA_CATCH_TIER_RENAME_1`, 2026-09-27) — all
  seven invented-name catch items live in the free tier with `*Catch` pairing.
- All four description-promised behaviours BUILD with the fish-body wave (scrape-line,
  pebble-freeze, sealing, shell-lodging) — the descriptions are the spec.
- (Note for the record: the niim/noolim two-species disentangling is a TWILIGHT
  ruling and belongs to that sea's pass, not this sitting.)

**Standing laws that bound this agenda's shape**
- One biome per animal unless an in-game mechanism reasons otherwise; holes are
  filled with NEW creatures, never a neighbour's (Q13's options honour this).
- Invented exotic names ship in the free `RM_` tier; only genuine canon routes
  through the campaign patch layer (the Elder's three canon treasures are patched).
- The floor's animal density is set (0.1 — the roster is live); the biome is
  impassable-surface with a walkable pocket floor, which is the intended shape.
- His one aesthetic rule, on every art brief for this biome: *"marred slightly,
  don't make them too perfect or they look manufactured."*
