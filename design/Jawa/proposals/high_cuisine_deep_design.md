<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# High cuisine, deep design — meals are statements

The owner's framing question, verbatim: *"Did we ever spec out the high cuisine
mod star wars style?"* Answer: no — `design/V2_DREAMS.md` ("The Cantina
Kitchen," 2026-08-15) records the observation and the mod-repointing strategy
but explicitly defers everything past a cook stove and Sekki Vosh to v2. This
is that spec. All dish, creature, and preparation names below are lore text,
per house rule — no defNames are coined here; a build pass runs anything
that ships through `design/NAMING_SCHEME_PLAN.md`'s three-tier grammar.

Ingested for this pass: `design/V2_DREAMS.md` ("The Cantina Kitchen," lines
812–864), `research/Jawa/star_wars_rimworld_cuisine_brewing_overcomplete_design.md`
(819 lines, a prior *intentionally over-scoped* catalog — mined and reconciled
in §1), `research/Jawa/star_wars_culinary_research_rimworld.md` (canon
compendium), `design/Jawa/ownership_settlement_spec.md` (the provenance/claim
fabric that makes stolen ingredients mean something), `design/Jawa/divine_satiation_engine.md`
(the nine-god pantheon this doc's capstone ritual serves), `design/Jawa/reconciled_lore/05_the_clan.md`
(the `NutrientPasteEating_Disgusting` precept — Jawas prize delicacies and
merely tolerate paste), and the world-hazard docs cited inline in §3.

---

## 🔴 RULED — owner sitting, saved 2026-09-02 (review sheet, 9 rows)

Verdicts and the owner's notes, verbatim (frozen source: `design/Jawa/worldbuilding/review/proposal_suite_review.decisions.json`; untouched rows keep their prefill — cut is the only destructive verdict):

| row | ruling | owner's note (verbatim) |
|---|---|---|
| hazard-pantry | v1 | YES! I really want there to be many strange pens, pits, aquariums, large bottles, cages, floating tethers... the bestiary for a star wars food culturing area should look absolutely amazing and bizarre. Need to think about how to animate it to look even more amazing. Cuisine should all have mild to major effects too, not necessarily intended to be "farmed" regularly so much as opportunistically prepared and enjoyed and rolled with. Good, bad, strange, and wonderful effects. Somewhat unreliable as well, to prevent min/maxing. |
| vce-repoint | v1 | Absolutely, let's leverage what they have and reskin it to us. |
| diplomacy-claim | v2→**v1** | This should be mostly a VERY big boon or VERY big bane, or else it's a weak "isn't this food nice." Menu should help you recognize what would do best here, not make the player remember a bunch of arcane lore. Likely requires a special "diplomatic meal" event or something to make this easier to remember. |
| ninefold-feast | dream→**v1** | Should earn valuable information, communion with the gods, calming of wild diefic relations, and a general ce-centering on Jawaness for all. Should have many kinds of meals/ingredients that serve each god, not just one specific thing, or it won't ever happen. Could easily unlock another layer of ship trust, sharing of old technology, and other plot elements. (Helps calm the ship too, essentially, feel better about it's inherent new Jawaness). |
| terroir-brewing | v2→**v1** | LOVE the idea that some of the cuisine manufacturing "works better" in different biomes or latitudes. The others should slowly tick along still, but some "supercharge" in the right conditions and really crank out or produce higher quality output. that's gold. |
| chef-performance | v2→**v1** | The Feastboss. Cool role. Explore with me how we might do this. There is a feasting ideologion concept currently in play, but I don't remember being particularly impressed by it. But studying it might be useful. *(✅ DESIGNED with owner 2026-09-02 — see §5.5 The Feastboss; replaces the existing feast ideoligion)* |
| recipe-discovery | dream→**v1** | That is SO Jawa!!! Absolutely. Start with basic stuff, and progress up the tree. Ingest the "stuff on a stick" mod into our own version and jettison that mod eventually... it's rather silly anyway (I think there are two of them). Let's take what we need and release them. |
| preservation-vocab | v2→**v1** | SO GOOD! Canning is terrestrial. This is awesome. Different food will need different preservation methods. And now we know why we want to go to the salt flats, or the tar pits, or sand dunes. Let's make everything salvageable commodoties! The ship should be absolutely full of weird stuff. I love the idea of piles of sand in a box, or a barrel of tar. So good. More than one method should work for each food type, maybe some work for all, just think about each one. Sand-oven should be sand-drying. |
| live-ingredient-tank | dream→**v1** | YES! And a lot more like this. This is deep Star Wars cannon. Grabbing a squealing creature from a fish bowl and eating it live should get a big mood buff and honor especially the Hutt. Gotta be animated somehow. |

## 1. Reconciliation — what survives the overcomplete catalog, and what doesn't

`star_wars_rimworld_cuisine_brewing_overcomplete_design.md` is explicitly
"far more content than should ever ship" (its own line 7) — a 144-dish, 50-
intermediate-ingredient, 16-research-node catalog built to expose the design
space before cutting. It's a genuinely strong survey and this document is
built *on* it, not beside it. Explicit accounting, because the coordinator
asked for one:

### Keep

- **Culinary geography (its §2), wholesale.** Dayside/nightside/terminator
  as three distinct processing environments — solar drying and salt harvest
  on the scorchside, cryo-aging and freeze-drying on the nightside,
  fermentation and dairying in the terminator's narrow temperate band — maps
  exactly onto Ash'karr's real, already-authored geography
  (`ASHKARR_WORLD_DEFINITION.md`'s substellar/terminator/nightside bands) and
  needs no new worldgen to use. This is the load-bearing idea of the whole
  document and §3–§4 below are built as its direct extension into hazard
  terrain.
- **The intermediate-ingredient production-chain shape** (raw → processed
  intermediate → finished dish, its §3) as a PATTERN, not its specific
  50-row table — see "Drop" below for why the table itself doesn't survive.
- **The pairing system** (§6.1) — a meal and drink consumed in a short
  window forming a named, flavored bonus. Cheap to build, encourages running
  a kitchen AND a bar, and reads as genuinely Star Wars (cantina culture is
  drink-and-food together, never one alone).
- **"Chef as artist"** (§6.9) — quality-bearing haute meals, a generated
  description crediting the cook, a **Culinary Triumph** thought, a
  legendary dish briefly displayed before being eaten. This is §5 below.
- **The anti-bloat rule** (§9) — "common base meal defs... not one unique
  ThingDef for every recipe" — restated here as a hard constraint on this
  document's own build ladder (§8), and consistent with the campaign's
  standing files-must-shrink discipline.
- **The workstation vocabulary** (§7) — solar dryer, salt pan, smoker,
  pickling crock, fermentation crock, cheese vat, aging rack/cellar, cryo
  rack, brewery, still, carbonator, cantina bar. Reused directly in §4 and §6.
- **Faction taste profiles** (§6.11) as a STRUCTURE — cross-reference
  `Livestock_Trade_Utility_Pets_v1.md` §14's faction ownership table
  directly rather than re-deriving faction identity from scratch; a
  faction's livestock trade and its cuisine should read as the same
  worldview (the Cartel's spectacle pets and its "Hutt Excess Table" are one
  culture, not two).
- **"A sane first implementation slice" as a METHOD** (§10) — rank by lore
  flavor, unique gameplay, art cost, code cost, dependency complexity,
  whether it's a new decision or another button. §8 below applies the same
  method to this document's own build ladder.

### Drop, and why

- **The 144-dish catalog itself.** It's the intentional bloat the source
  document names as bloat. Repointing VCE/VCE-Stews recipe-by-recipe onto
  new ingredients (per `V2_DREAMS.md`'s original plan — "only the inputs
  and the names change") is v1-cheap; authoring 144 bespoke finished goods
  up front is the opposite of the anti-bloat rule the same source document
  states two sections later. Keep it as a design bank to draw FROM during
  build, never as a target list to clear.
- **The 50-row intermediate-ingredient table**, specifically. Most of its
  raw inputs (ronto, shaak, nerf, bantha, tip-yip, gorg, mynock meat/milk)
  are products of animals already covered by
  `Livestock_Trade_Utility_Pets_v1.md` and the adopted Star Wars Animal
  Collection roster — RimWorld already grants meat/milk/wool/eggs from a
  tamed or hunted animal without a bespoke ingredient def. Re-deriving a
  parallel ingredient matrix here would duplicate that roster instead of
  repointing recipes onto it, which is the actual v1 mechanism.
- **Palate progression / acquired alien-palate tolerance** (§6.2–6.4) as a
  persistent stacking stat. Flavorful, but a permanent, ever-rising buff
  from repeated luxury eating is exactly the unbounded-creep shape the
  campaign's anti-exponential house rule exists to catch — it would need
  its own hard-cap or decay design before it's safe, which makes it a
  separate systemic proposal, not a line item here. Parked to Dream-tier
  (§8) pending that pass.
- **Food scent as stealth/predator-detection penalty** (§6.5). Genuinely
  interesting, but it cross-cuts into Ishko's hiding/ambush theology
  (`05_the_clan.md`) hard enough that it deserves its own design pass
  alongside whatever owns Ishko's mechanics, not a bolt-on here.
- **The 16-node research tree** (§8 of the source). This document's own
  recipe-gating answer is §6 below (recipes as loot/rumor/quest reward,
  not a tech ladder) — a linear research tree would compete with that
  mechanism rather than support it, and duplicates whatever the base
  game/VCE already research-gate.
- **The 13-entry random micro-event catalog** (§6.12). Cute individually,
  but this campaign already has a live, deep ritual/event framework — the
  Council of Voices (`divine_satiation_engine.md` §5c) narrates exactly this
  kind of "something happened during the feast" beat, in-theology, with
  build-up and consequence. A parallel unthemed event table would compete
  with it. The two or three best beats (a live ingredient escaping
  mid-service; a legendary vintage a pawn refuses to open) should be
  authored as INPUTS to the existing ritual system, not a second one.
- **The full nine-faction banquet roster** (§5.15's Kaminoan/Mon
  Cala/Geonosian/Droid-Enclave entries etc.) as a build target. Keep the
  STRUCTURE (§7 below cites it), author only the banquets matching this
  campaign's actual roster (`faction_roster_v2.md`) when building, not all
  nine speculatively.

---

## 1-bis. Canon anchors confirmed against the compendium (ingested 2026-08-31)

`star_wars_culinary_research_rimworld.md` (976 lines) was mined specifically
to check this document's inventions against real Star Wars culinary canon
rather than let them float free. Findings that change or strengthen §3–§6:

- **Mudhorn egg yolk is on-screen Jawa canon, not extrapolation** — Jawas
  eagerly eat it straight from the shell in *The Mandalorian*. This is the
  single strongest anchor available for a Tier 2 "repointed VCE" dish (§5)
  and should be the one that ships first when this design is built.
- **Salt-crust is canon-supported, not original coinage** — Crait-crusted
  cod (fish prepared under Crait's own salt crust) is a documented dish tied
  to the salt-flat planet Crait. §9's salt-crust term upgrades from "a
  working term tied to an existing hazard" to a directly attested technique.
- **The diplomacy mechanic in §3 is this document's own extrapolation, and
  that needs to stay visible.** The compendium does NOT contain a
  documented "serve the correct/humiliating delicacy to an envoy" scene —
  the closest supporting material is krayt eggs "appearing at state
  dinners" [L] and a documented status-food category (Hutt live-food
  excess, proscribed aristocratic dishes) rather than a specific ritual.
  §3 is built on that category, honestly [T]-tagged, not on a sourced
  precedent.
- **Orpali dragon young, served on glazed chuba eyes** [L] — explicitly
  tagged "proscribed aristocratic cuisine" in the compendium (illegal,
  captive-bred young killed in infancy). This is the concrete canon dish
  §5's course ⑨ (Ozzik — the showiest, riskiest course) was gesturing at in
  the abstract; cite it directly when this ships.
- **Roasted Acklay Claws** [C culinary] is a named, documented dish — a
  dangerous-hunt trophy course that cross-references directly to the
  Acklay already placed in `Livestock_Trade_Utility_Pets_v1.md` §10.2
  (Cartel arena tier). Use it as the anchor for a §5 Tier 3 haute course
  built from a hunted-not-farmed ingredient.
- **Named canon drinks exist and should replace invented signatures in
  §6.3** rather than sit beside them: **Tsiraki** [C] (fermented
  salakberries), **Jogan brandy** [C culinary], **Pallie wine** [L, carries
  its own vintage/producer prestige — a natural fit for the aging-quality
  mechanic in §1's "chef as artist" keep], **Tarine tea** [C], **Cassius
  tea** [C, documented as strongly Mandalorian-associated — a ready-made
  Blackstar Company / Mandalorian faction-taste tie per §7]. §6.3's "author
  two or three named signatures at build time" should draw from this list
  first, not invent from scratch.
- **No tidally-locked-world food ecology exists anywhere in canon.** This
  confirms §4's four hazard ingredients (scorch-fruit, tar-preserved meat,
  nightside cryo-delicacies, pool-guardian roe) are correctly this
  document's own invention, not something to reconcile against a source
  that doesn't cover it — the terminator/dayside/nightside framing stays
  sourced to Ash'karr's own world doc, not to Star Wars canon.

---

## 2. Prior art — what the workshop already gives, and where this design
extends past it

Verified this session (§ live web search, cross-checked against the
overcomplete catalog's own §1):

| Mod | What it actually does | Adopt as-is | Where this design extends it |
|---|---|---|---|
| **Vanilla Cooking Expanded** | Meals differentiated by function (desserts, grills, soups, bakes, frying, condiments), a condiment system with 12h effects that stacks by ingredient list, a cheese press that gains quality/value the longer milk sits in it | The condiment system and cheese press wholesale | Repoint the recipes onto hazard-sourced and Star Wars animal ingredients (§3–§4) rather than generic ones |
| **Vanilla Cooking Expanded — Stews** | Time-on-stove as a real processing cost; stews mask objectionable ingredients and are more nutrition-efficient | Wholesale — the masking mechanic is the mechanical answer to "eating something you found," useful for hazard-sourced ingredients that read as gross | — |
| **Vanilla Brewing Expanded** | Distinct production chains, advantages/disadvantages and cocktail traits per alcohol type, not interchangeable recreation drugs | Wholesale — see §5 | Desert-specific fermentation chains (§5.1) and the terminator-belt terroir angle |
| **Gastronomy** | Restaurant-style table service: guests/colonists sit, order from a waiter, price and the waiter's opinion/traits/skill/mood shape the guest's reaction | The waiter-job pattern, reskinned | Extend price/service quality into the diplomacy layer (§3) — a Hutt envoy's opinion of the SERVICE is part of what a banquet is negotiating |
| **Variety Matters Dinner Time** | Poorly prepared meals (too small/large, under/overcooked, burnt, wrong seasoning) generate graded bad thoughts | The precedent that presentation quality reads as a real, graded mood signal, not a binary | Extend from per-eater mood to a ROOM-radius ambient effect for a properly staged banquet (§6) |
| **Table Purity** | Eating without a table has real social consequences, not just a mild mood ding | The precedent | Feeds directly into §3 — a Hutt envoy eating standing up IS an incident |

Nothing here needs new C#. The whole design is XML recipes, ThingDefs, and
one new job type (§6's Tend & Narrate-adjacent waiter/chef roles, which the
livestock companion doc already establishes a precedent for with `coo'la`'s
Tend & Narrate job).

---

## 3. Meals are statements — cuisine as a diplomacy instrument

**The mechanic.** A dish served to a guest is not merely food; it is a
CLAIM about the relationship. Two axes decide what that claim says:

1. **Is it the RIGHT dish for the guest?** Per §7's faction taste profiles —
   serving a Hutt envoy a live-food course from the Hutt Excess Table
   register is a compliment (you know and honor their palate); serving them
   a plain paste-vat meal is either an insult or an accidental confession of
   poverty, and the game should let both readings be possible depending on
   context (a poor clan honestly has nothing else vs. a clan that could have
   done better and didn't bother).
2. **Where did the ingredients come from, and does the guest know?** This is
   where `ownership_settlement_spec.md`'s claim fabric does real work.
   Every ingredient in a served dish carries whatever claim history it had
   at harvest — battle loot keeps its origin claim at ~1.0, decaying by
   recognizability (spec §5); a stolen Hutt delicacy served back to a Hutt
   guest is a HIGH-recognizability item by definition (named, distinctive,
   exactly the kind of thing the spec singles out as slow to decay).

**The event, mapped onto the existing spine** (`ownership_settlement_spec.md`'s
"act → TakingEvent → claim resolution → perception roll → propagation →
faction record"), specialized for a served meal:

```
serve (a dish built from a claimed ingredient)
  → claim resolution: whose ingredient was it, how strong is the claim now
  → the CHOICE: does the clan disclose the origin, or let it pass unremarked?
      disclosed  → a FLEX. Per Mob'Unloo's doctrine ("successful theft is
                   the perfect deal; being CAUGHT is the sin"), a chosen
                   reveal is not a crime — it's a boast, and a savvy guest
                   reads it as one. Goodwill can move EITHER way depending
                   on the guest's own culture (a Hutt may respect the nerve;
                   an Imperial officer will not).
      undisclosed → a perception roll per the spec's witness mechanic. A
                   guest (or their retinue) with a plausible reason to
                   recognize the item may catch it unassisted. Caught this
                   way, it is an INCIDENT — propagation follows the guest's
                   OWN faction's security-profile rate (spec §6), same as
                   any other undisclosed theft, and consequences read the
                   faction record exactly as they would for a burglary: a
                   guard shadows the clan's next visit, a price cools, a
                   grudge is logged. Nobody at the table says anything in
                   the moment — the dread is entirely in what happens after.
```

**Why this belongs in the cuisine doc and not just the ownership doc:** a
banquet is the highest-density, highest-stakes venue for a claim to surface,
because it puts the claimant's own faction directly across the table from
the evidence. Building the hook here means every future banquet quest or
diplomacy scene gets this tension for free, rather than needing a bespoke
check.

**The clean-provenance course, inverted.** The same mechanic gives Mob'Unloo
(trade/debt, `divine_satiation_engine.md` §2④) a positive-valence course of
his own: a dish built entirely from FAIRLY bought ingredients — a real,
costed transaction, no claims outstanding — reads as devotional in exactly
the way a stolen one reads as a gamble. See §7's Ninefold Feast course ④.

---

## 4. Ingredient rarity tied to world hazards — every dangerous biome is a pantry

The same logic that makes half the hazard content worth visiting in
`fire_ecology_deep_design.md`, `tar_pits_deep_design.md` and
`water_economy_deep_design.md` (concurrent proposals in this same directory)
applies to food: an ingredient that can ONLY be sourced from a genuinely
dangerous place is worth more than one grown in a planter, and it's a
standing reason to send a caravan somewhere it would otherwise have no
reason to go.

| Ingredient | Source hazard | Canon anchor | Why it's dangerous to get |
|---|---|---|---|
| **Scorch-fruit** | Fire-ecology margins, the Pyrelands' burning-savanna cycle | `hydrology_and_fire_ecology.md` R-H9/R-H10 (ash-water-ash-water compression, the scorched-day/frozen-night reconciliation) | Grows fastest in soil that burns on a cycle — harvesting it means timing a trip between burns, not just walking in |
| **Tar-preserved aged meat** | The tar pits past the Pyrelands' margin | `hydrology_and_fire_ecology.md` R-H9 ("tar preserves... a receipt of what this world has been"); `desert_world_design.md` line 576's tar-preserved battlefield | The tar keeps whatever it catches — sometimes that's a delicacy decades old and perfectly sealed, sometimes it's the thing that died trying to reach the same delicacy. Excavating it is the tar-pits proposal's own dig-site stratigraphy, repurposed as a pantry raid. |
| **Nightside cryo-delicacies** | The permanent nightside, past the terminator | `ASHKARR_WORLD_DEFINITION.md` (rain never condenses on the nightside; water there is locked as ice) | Requires a cold-chain the whole way home — the same forage-hostile/heat-hostile guardrail that caps livestock (`Livestock_Trade_Utility_Pets_v1.md` §1) caps how much of this a caravan can bring back before it spoils or the crossing kills the crew |
| **Pool-guardian roe** | Oasis/river water holes with a resident apex defender | `Livestock_Trade_Utility_Pets_v1.md` §13 (the overgrowth layer — wet tiles are the densest wild-capture ground AND the most dangerous, an emergent pairing, not scripted) | The roe is only reachable by getting past whatever the water hole's density of predators has concentrated there — the ecology doc's own "reward gated behind a crowded, ambush-friendly shoreline" |

**The pantry-as-reason-to-visit design payoff:** none of these four need a
new biome, a new hazard mechanic, or new worldgen — every one of them rides
an existing, already-authored hazard. The only new content is the
ThingDef/RecipeDef layer sitting on top, which is exactly the "only the
inputs and the names change" promise `V2_DREAMS.md` made for this whole mod.

---

## 5. Dish tiers — from paste-vat humility to the Nine-Course Ninefold Feast

**Tier 0 — the paste vat.** `NutrientPasteEating_Disgusting` is already
canon (`05_the_clan.md`) — Jawas tolerate paste, they don't enjoy it. This
tier needs no new content; it's the floor everything else is measured
against, and its presence is what makes Tier 1+ mean something.

**Tier 1 — Sekki Vosh and the cook stove.** Already-shipped v1 scope per
`V2_DREAMS.md` line 862. The baseline "we cook, we don't just paste" meal.

**Tier 2 — the repointed VCE tier.** Grills, wraps, stews, condiments —
mechanically identical to Vanilla Cooking Expanded's existing recipe types,
repointed onto Star Wars animal products and, where available, a §4 hazard
ingredient. This is where most of the overcomplete catalog's §5.1–5.4
material (Ronto Wrap, jerky variants, pickled preserves) belongs when built.

**Tier 3 — the haute course.** Quality-bearing, chef-credited, generated
description, per §1's "chef as artist" keep. Requires a §4 hazard ingredient
or a genuinely rare animal product (a §17-priced creature from the livestock
doc). This is the tier a banquet in §3 is actually built from.

**Tier 4 — the Nine-Course Ninefold Feast.** The capstone: one course per
god, each course built to please that god's OWN satiation channel (per
`divine_satiation_engine.md` §3's a/b/c framework), served as a single
ritual meal. This is a religious instrument, not a stat pipeline — per the
engine's own §19.5 pillar, no course grants material reward; the payoff is
mood, narrative, and ritual-participation eligibility exactly like any other
rite.

| Course | God | What pleases him, mechanically | Why |
|---|---|---|---|
| ① | **Ishko** (hiding, ambush, stillness) | Served and eaten in total darkness — the room's lights are OFF for this course specifically, by design, not by accident | Open exposure offends him; a course you cannot see is the one dish that is structurally pious |
| ② | **Ohm** (the living machine) | Prepared and served by a droid, zero organic hand-touch from ingredient to table | His lever is bold tech-handling; a fully machine-tended course is the boldest possible reading of that |
| ③ | **Oomo** (the body's waters, family increase) | Built around the rarest water-linked ingredient on hand — pool-guardian roe (§4) is the ideal, or an egg dish — with a small tableside libation poured, not drunk, as an offering | His domain is explicitly "the body's waters" and eggs; a poured-not-drunk libation mirrors his "waters offered" framing |
| ④ | **Mob'Unloo** (trade, debt, the sacred exchange) | Built ENTIRELY from fairly, verifiably purchased ingredients — the clean-provenance course from §3, inverted from every stolen-ingredient flex elsewhere on the table | Transactional to his core — this is the one course where an HONEST deal is the devotion, not a clever theft |
| ⑤ | **Rekko** (salvage, repair) | Served in mended, salvaged cookware with its own repair history — never anything newly forged | Scrapping the repairable is tragedy to him; the VESSEL matters as much as the food |
| ⑥ | **Ta'Baa** (flight, hope) | A handheld course, eaten standing, timed to finish right as the ship prepares to lift | The launch is his holiest rite; a course built to be devoured mid-departure is devotion in motion |
| ⑦ | **Zizzik** (malfunction, betrayal, breaks) | Deliberately includes one genuinely risky preparation step — a dangerous ingredient handled live, a technique that can fail (the overcomplete catalog's "dangerous food preparation," §6.8, repurposed as devotion rather than a hazard to avoid) | He is fed by chaos; a controlled offering of risk is the only pious way to approach a god you cannot otherwise serve |
| ⑧ | **Sh'kaar** (the killing light, inevitability) | Not a food course at all — a controlled, violent destruction performed tableside (something flambéed or burned outright), framed as a death that costs the clan nothing of its own | Comfort and abundance anger him; per his own calming lever ("a death that isn't yours"), the ninth seat is a sacrifice, not a meal |
| ⑨ | **Ozzik** (ambition, pride, grief) | The chef's single most technically ambitious dish on the table — the one most likely to fail, the one that risks the most to attempt | THE TRAP, mechanically: courting him is necessary and dangerous at once; the showiest course is the one that draws the most story-risk, exactly as his own doctrine demands |

**Staging note:** the Feast is performed at the same sacred center the
Council of Voices already convenes at (`divine_satiation_engine.md` §5c) —
this is not a separate venue, it's a ritual TYPE that venue already
supports, triggered per §5b's event-driven contract (most naturally: after a
major trade, a landing, or a formation of an outpost — anywhere a feast
would already be diegetically owed). The Council's participation-bias rules
apply unchanged: a pleased god's course is loud and blessed; a wrathful
god's course (most likely Sh'kaar's or Zizzik's) is rare-but-possible to go
wrong, which is the entire point of offering them anything at all.

---

## 5.5 The Feastboss — the impresario the Ninefold Feast runs on

Designed with the owner in a bench session, 2026-09-02. His framing: *"The
Feastboss. Cool role. Explore with me how we might do this."* Every ruling
below is his, verbatim where quoted.

**The problem it solves.** Vanilla's feast ritual is a passive gathering —
everyone eats, everyone gets a mood buff, nothing is at stake. ✅ **RULED:
that existing feasting ideoligion is REPLACED entirely** — stripped, not kept
alongside. The Feastboss makes the feast a *performance with a skilled pawn's
judgment at its center*, where the same Nine-Course meal (§5, Tier 4) can
bless the clan or offend a god depending on who runs it and how they play the
room.

**What it is.** A permanent, titled ideoligion role — one Feastboss at a time,
like the Moral Guide — but the title is **earned by cooking, never appointed**.
✅ **RULED: won by a triumph, lost by a disaster.** A pawn who lands a
genuinely ambitious feast claims the title; a public catastrophic failure (or
death) loses it. The title tracks live reputation, not a menu assignment — the
clan has a named impresario it rallies around, and watches fall.

**The three-in-one binding — the counterweight, and the best part.** ✅
**RULED: the Feastboss must personally be all three of these people at once,**
skill-gated, with *"special dishes that open the role"* as the gate:

1. **The exotic-animal tender.** The hazard-pantry and live-ingredient
   creatures (§4, and the ruled live-ingredient tanks) are tended by the
   Feastboss's own hand — the squirming, dangerous, wondrous bestiary is
   *their* husbandry burden, not a separate animal-hauler's.
2. **The cook.** They prepare the courses themselves — no delegating the
   knife.
3. **The impresario.** They read the room, reach for the dangerous gods, and
   perform.

⇒ This is a genuine opportunity cost: the Feastboss braids **animal husbandry
+ cooking + social/ritual performance** into one colonist across three skill
trees. You give up a great generalist to have a great Feastboss, and the role
is a bottleneck by design — there is exactly one throat through which the
whole divine-cuisine system passes.

**The core verbs — ✅ RULED all three, gated behind the role:**

- **Read the gods.** The Feastboss surfaces which gods are hungry or wrathful
  tonight and advises the menu. ⚠️ **Skill-gated and fallible** — a mediocre
  Feastboss *misreads* which gods are angry, so reaching for a wrathful course
  on bad intel is a live way disasters happen. Good intel is the reward for a
  skilled impresario; a bad one flies blind and thinks they can see.
- **Unlock the wrathful courses.** Anyone with the ingredients can cook the
  *safe* god-courses (Ishko's darkness, Mob'Unloo's honest provenance). Only a
  Feastboss can attempt the ones that can fail catastrophically — Ozzik's
  most-ambitious dish, Zizzik's live-risk step, Sh'kaar's tableside
  destruction (§5, Tier 4). A feast without a Feastboss is safe and small; a
  feast with one can reach for the wrathful gods at all.
- **Perform to rescue failures.** Their performance skill can convert a failed
  course from a divine catastrophe into mere story. ⚠️ **The rescue burns
  them** — a stacking exhaustion/strain hediff — so a feast that keeps going
  wrong can break the impresario mid-service. The safety net has a floor.

**Skin in the game.** The Feastboss bears the god's reaction in their own
name: land a wrathful course and they gain standing (a "Feast-Crowned"
reputation/mood); botch it and *they* take the scar — a hediff, a
broken-reign ledger entry (`divine_satiation_engine.md`, the Reign-Scars
pattern) written against them, the clan watching their impresario fail a god
in public. The title has skin in the game, which is exactly what vanilla's
feast lacks.

**Where it plugs in.** The Feast is performed at the sacred center the Council
of Voices already convenes at (§5's staging note); the Feastboss is the
officiant role that ritual type has been missing. The wrathful-course
risk/reward is the same `divine_satiation_engine.md` §5b event contract, now
with a named pawn staking their standing on each attempt.

**Build ladder for the role specifically:** (1) the titled role + the
triumph-wins/disaster-loses tracking + the three-skill gate and the
qualifying "opening dishes"; (2) read-the-gods advice surfaced through the
menu, skill-gated fallible; (3) the wrathful-course unlock and the
performance-rescue hediff. Tier 1 is the role existing; the feast itself
(§5 Tier 4) is its own build.

---

## 6. Brewing — the drink half of the same culture

Per the coordinator's flag: brewing gets its own section because the
overcomplete catalog's depth here (§5.10–5.13, §7's still/fermenter/
carbonator/cantina-bar line) is genuinely strong and this campaign's
cantina-culture framing (`V2_DREAMS.md`'s "Cantina Kitchen") is explicitly
about food AND drink together.

### 6.1 Fermentation — the terminator's one clear advantage

Adopting the overcomplete catalog's terroir claim directly: **fermentation
quality peaks in a narrow temperature band that only the terminator holds
reliably.** Dayside heat stalls or spoils a ferment; nightside cold slows it
to a crawl without a heated room. This makes the terminator belt genuinely
valuable territory for a reason that has nothing to do with farmland — a
scavenger clan that wants real drink has to hold or trade for terminator
access, which ties brewing directly into the same territorial pressure that
already shapes the Homestead Defense League's terminator holdings
(`ASHKARR_WORLD_DEFINITION.md`). Base chain: fruit/grain must → Fermenter →
low-alcohol drink (wine, beer, cider, fermented dairy — the overcomplete
catalog's §5.11 has a clean template list to draw individual names from at
build time, none of which need to ship as a block).

### 6.2 Distillation — the fire-risk tier

Still-based spirits are the second tier: higher value, real fire risk (per
the overcomplete catalog's own workstation note), and thematically adjacent
to the tar-pits proposal's flammable-hydrocarbon vocabulary — a Jawa still
run too close to a tar seep is a story, not just flavor text. Distillation
gates on the fermentation tier already existing (you distill a wine or
wash, you don't distill straight from must), which keeps the tier real
rather than a flat unlock.

### 6.3 Cantina culture — cocktails as the social layer, not a longer list

The overcomplete catalog's cocktail section (§5.12–5.13) is where its bloat
risk is highest — a dozen named signature drinks with near-identical
mechanical shapes. Keep the PAIRING mechanic (§1) as the actual gameplay;
author two or three named signatures at build time (one Jawa-flavored
scavenger's draft, one Hutt-court cocktail, one honest Compact field drink)
rather than the full catalog, and let the Cantina Bar building (§7's
workstation list) generate flavor text for the rest the way VCE's Haute
module already generates dish descriptions from ingredients.

### 6.4 Non-alcoholic — caf and tea as the working drink

Caf (roasted, solar-roasted for a stronger dayside profile) and tea
(tarine-style, cold-steeped nightside) round out the non-alcoholic tier and
exist mainly to give the Second Wind / Cold Furnace-style functional-drink
niche somewhere to live without needing an alcohol chain — a caravan's
morning drink, not its evening one.

### 6.5 Drinking as devotion, not just recreation

The same theological hook that makes food a statement (§3, §5) makes a
SHARED drink one too: Mob'Unloo's domain already extends to "accepted
romantic advances, marriages, and conversions" as contracts struck
(`divine_satiation_engine.md` §3④) — a toast shared over a fair trade is the
same shape of devotional act at a smaller scale, and costs nothing new to
implement once the pairing mechanic (§6.1 above) exists. A poured-and-shared
drink is the natural low-stakes version of the Ninefold Feast's Mob'Unloo
course (§5), available every session rather than only at the capstone rite.

---

## 7. Cooking as performance

- **The chef pawn role.** Not a new work type — an emergent identity for
  whichever pawn consistently produces Tier 3+ dishes, formalized the way
  `05_the_clan.md` already flags "the cook matters" against the paste
  precept. A named chef role earns the Culinary Triumph thought (§1) and
  becomes a recognizable NPC-facing identity when the clan hosts (§3).
- **Table service.** Gastronomy's waiter-job pattern (§2), reskinned: a
  served meal's quality reads as partly the DISH and partly the SERVICE —
  the waiter's social skill, opinion of the guest, and presentation choices
  modulate the same mood outcome a raw meal-quality stat would give alone.
  This is what makes a banquet (§3) a performance the clan can succeed or
  fail at independent of the food itself.
- **Presentation quality and mood radius.** Variety Matters Dinner Time
  proves graded presentation-quality mood effects are workable per-eater
  (§2). Extend the same grading to a ROOM-radius ambient effect for a
  properly staged banquet table — everyone seated at a well-presented feast
  gets a smaller version of the eater's mood bonus, which is what turns
  "cook a good meal" into "throw a good banquet" as a distinct, biggerstakes
  action.
- **Faction-flavored service, cross-referenced.** `Livestock_Trade_Utility_Pets_v1.md`
  §14's per-faction ownership table already establishes who trades what;
  the overcomplete catalog's §6.11 faction-taste-profile structure (kept,
  §1) should be authored against THAT table specifically, not invented in
  parallel, so a settlement's cuisine and its livestock trade read as one
  culture.

---

## 8. Recipe discovery — recipes as loot, rumor, and quest reward

Per the owner's brief, recipes are not unlocked by research (§1's drop
list) — they're found, same as any other piece of intel in the settlement
fabric `ownership_settlement_spec.md` already builds:

- **A stolen cookbook is a physical quest item**, not an abstraction — a
  ThingDef that, read/used, unlocks a specific Tier 3+ RecipeDef. A stolen
  Hutt cookbook is the obvious flagship (and pairs naturally with §3's
  stolen-ingredient mechanic: cooking FROM a stolen recipe on top of stolen
  ingredients is a double flex, or a double incident, depending entirely on
  whether the clan chooses to disclose either half).
- **Rumors as intel objects** (`ownership_settlement_spec.md` §9's "v1 verb
  families," social fabric bullet) point at recipes the same way they point
  at anything else worth knowing in a settlement — a rumor that names WHERE
  a recipe lives is the discovery hook, and the recipe itself is the payoff,
  same shape as a salvage-law wreck-rights lead.
- **Settlement-visit districts as recipe sources**, per the spec's district
  library (§8 of that doc) — a cantina-block district visit is the natural
  place a recipe changes hands, bought, overheard, or lifted, tying recipe
  discovery into the same walkable-commerce verbs the ownership fabric
  already ships rather than inventing a separate discovery system.

---

## 9. Food preservation vocabulary for a desert

Three working terms, each tied to an existing hazard rather than invented
whole:

- **Salt-crust** — evaporative salt harvest (the overcomplete catalog's
  §2 scorchside strength; `biome_terrain_palette.md`'s Salt Flat terrain
  code, SF, already exists as a biome). A crust-sealed dish is the desert's
  answer to canning: cheap, dayside-native, long shelf life, unglamorous.
- **Tar-seal** — literally what the tar pits already do to anything that
  falls in (`hydrology_and_fire_ecology.md` R-H9, "tar preserves"). A
  deliberately tar-sealed food product is the SAME preservation process the
  §4 tar-preserved-meat delicacy uses by accident, now performed on purpose
  — a controlled, cheaper version of a hazard-sourced luxury, which gives
  the dangerous version (§4) a mundane sibling worth contrasting it against.
- **Sand-oven** — desert cooking by radiant/retained heat rather than an
  open flame. **Direct cross-doc synergy:** the livestock companion proposal
  (`ludicrous_livestock_deep_design.md` §2) invents `onnik`, a "kiln-belly"
  creature whose fed-and-cured product is literally fired ceramic vessels —
  onnik-fired cookware is the sand-oven's natural hardware, authored once
  and shared between both documents rather than duplicated.

---

## 10. What Vanilla Cooking/Brewing Expanded already gives, restated as a table

| Already given (adopt) | This design adds |
|---|---|
| Condiment system, cheese press, grilled/frozen/baked/soup meal types | Hazard-sourced and Star Wars animal ingredients repointed onto the same recipe shapes (§4) |
| Distinct alcohol production chains and cocktail traits (VBE) | Desert terroir gating — terminator-only fermentation, still fire-risk tied to tar-pit proximity (§6) |
| Generated haute-meal descriptions, quality, personal/social memories (VCE-Haute precedent, cited via the overcomplete catalog §1) | Chef pawn role formalized against the existing `NutrientPasteEating_Disgusting` precept; Culinary Triumph as a named thought (§7) |
| Table-adjacency mood mechanics (base game + Table Purity) | Banquet-as-diplomacy stakes layered on top — the ownership claim fabric turns a served dish into a discoverable social event (§3) |
| Waiter/restaurant service (Gastronomy) | Room-radius presentation effect for a staged banquet, not just a per-guest one (§7) |

---

## Build ladder

- **v1 slice:** repoint ONE existing VCE recipe chain onto a §4 hazard
  ingredient (scorch-fruit is the cheapest — no new creature dependency,
  reuses an existing dessert/preserve RecipeDef shape) and ship the
  salt-crust preservation building. This proves the "only the inputs and
  the names change" promise before anything harder is attempted, and needs
  zero new job types.
- **v2:** the diplomacy layer (§3, riding `ownership_settlement_spec.md`'s
  already-scheduled `PROPERTY_FABRIC_BUILD_1`/`SETTLEMENT_VERBS_WAVE_1`
  work — this doc adds no new execution item, it rides theirs), the chef
  role and table-service reskin (§7), tar-seal and sand-oven preservation
  (§9, the latter gated on the livestock doc's `onnik` shipping first), and
  the fermentation/distillation brewing chain (§6.1–6.2).
- **Dream:** the full Nine-Course Ninefold Feast ritual (§5, staged through
  the Council of Voices, LLM-narrated per-god course reactions), the
  recipe-discovery quest chain including the stolen Hutt cookbook (§8), and
  the live-ingredient tank building `V2_DREAMS.md` already flagged as "the
  mechanically novel part" of the original Cantina Kitchen pitch — correctly
  last, since it's the one piece here that needs real new C#. **Aquaculture
  is explicitly this document's ground to develop, not the livestock
  proposal's** — `ludicrous_livestock_deep_design.md` §7.4 cedes the whole
  water-dwelling husbandry layer here on exactly this basis. When that pass
  happens, `research/Jawa/star_wars_rimworld_xenohusbandry_aquaculture_event_design.md`'s
  live-tank species (a Yobshrimp-style "eaten alive, still moving" delicacy
  is the strongest single candidate) are the natural first stock for the
  live-ingredient tank, and its own event library (escape gags, brood
  crises) should feed the Council of Voices as ritual-interrupting beats
  per §1's "drop the parallel micro-event table" ruling, not as a second
  event system.
