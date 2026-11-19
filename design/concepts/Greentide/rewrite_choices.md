# The Greentide: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A different agent from the writer re-read the Greentide's sources before any old file is deleted, starting with
what the first read had named as unread and with the ledger items, which the first read had not used at all.

DELETE-READY: yes

That line covers the eight files listed for deletion at the end of this page, each read to its end by the second
reader. Two conditions travel with it, both already on this page: the flora roster's 22 rows are the art
pipeline's silhouette brief and should move before the file goes; and `rosters/the_greentide.json` is the only
file holding his Greentide sheet of 2026-10-08, whose words are now carried in rows here. The two greatbole files
stay held, as the first read said.

**Measured** (by `rowcheck.py`, the same script the Fever Wood used; its line is in
`design/RimMandrake/biome_recheck_feverwood_greentide_abyss_row_check_2026-11-18.txt`): **327 rows, 163 of them
added by the second reader.** By the first word of "what happened": 258 kept, 34 lost, 18 moved (and one more row
that records a move in part), 15 kept and reshaped, 1 folded into shared machinery. 49 source names, each used in
at least one row. **59 source files read to their end** by the second reader (the first read counted 23, most of
them in part).

**The three most valuable things the first read missed**

1. **His two freeze rulings on this biome's fuel, R5 and R24 of 2026-09-07.** Sap-chemfuel is *"not
   player-tappable — a settlement-level investment"*, and *"green wood does not burn; seasoned wood does"*, with
   drying *"never a supply a passing player taps."* The design had the crew rendering resin to fuel and carrying
   off burnable wood. Both are his words about exactly these two goods, and they fit his ruling of 2026-11-18
   better than the first draft did: the Greentide's fuel is bought.
2. **His card of 2026-10-03 on the bank ambusher**, which exists only on a closed ledger item. The design
   described the design draft of the day before (a moment's warning, a marked cell to step off). He ruled the
   opposite: it bites on contact, bites anything heavy enough, and the game pauses the first time one is revealed,
   with the letter *"The bank moved."*
3. **Limb regrowth is not the Greentide's.** On 2026-09-22 he moved it to the Contagion and named grenades as the
   jungle's reward. The first read kept it "in later" and counted it among the jungle's unruled rewards.

Close behind: the rooted ambusher he approved on 2026-09-22 (*"one of its leaves occasionally twitches if you
watch carefully"*), which the first read had filed as shared machinery; his own sentences for the wasps and the
Frenzy; and five one-line tests written on the ledger items, now quoted in the design ("You kill the first six
without thinking, and then you look at the screen.").

**What changed in the design, and why** (fourteen repairs; each is also a row below)

1. *Fuel.* Rewritten on R5 and R24: settlements make sap-chemfuel, the crew buys it with green wood, and the
   crew-run resin recipe left 0.2.0 and became a question for him.
2. *The bank ambusher.* Written as he ruled it on 2026-10-03, pause and letter included.
3. *The shoal.* Its blast-only hide moved from 0.2.0 to 0.1.0, with a promise row. His typed words define the
   creature by it and it is built; the deferral was a delegated cleanse call.
4. *The wasps.* His sentence and the item's test line are in the moment; leaving is named as the answer.
5. *The Frenzy.* It kills untreated and is treated in the coma (his words); no milder sickness lives here.
6. *"Darkness brings roots."* Kept as his image, marked as not a mechanic (the built growth needs light). The
   blower's three prerequisites are stated.
7. *When the Empire arrives.* His fire ruling; the built sight rule (thicket between, shots and witnessing
   blocked); and the kit's own line that dropped battle gear goes under, which the first read had listed as new.
8. *Who else.* The Wildsteam capital (R10) and their taboo on cutting a living tree; the sytheclaw is not here
   (his sheet of 2026-10-08).
9. *The rooted ambusher* is named in 0.2.0 beside the plants that act.
10. *Dropped list.* Limb regrowth, the sytheclaw, the carry-nothing Frenzy route, Jawa plant names, the insect
    nest. The "nine further reward ideas" line is corrected to the seven that remain.
11. *The Ceded Room.* Both of his sentences are quoted: the one that wrote it around the ship, and the one that
    deferred every such rite.
12. *What the crew takes away.* Greenwood leaves green; resin is for sealing; the stench grenade is named at 0.2.0.
13. *Names.* The lunger is the dhollollo in game; the three that divide the water are stated together.
14. *NEEDS HIM* went from none to nine, each with its default: fuel 2, hull 1, cover 1, scope 2, other 3.
    Locked-tree: none, the Greentide has no locked sheet or tree.

**Five first-read rows corrected in place** (each says so in its cell): limb regrowth, brunnock, the second gear
tree, sap rendered to chemfuel, the Illisk.

**Rules applied.** Hull wear cites the existing frame (`src/RimUtinni/ShipShields/`) and comes from a source (the
rasp, the review of 2026-10-02); nothing invented was added to it, and whether his "Yes in 0.1.0" chose the rasp is
asked. Ship ideas he declined or deferred are listed and not revived: the rasp (asked), the Ceded Room (his
deferral of 2026-10-23, quoted). Where sources disagreed his latest dated words won, and each cleanse deferral
was checked against them: the cleanse's scope calls are all marked "Designer decision (delegated)", so the
shoal's hide followed his words. The clock's arithmetic was not touched.

**Not read to the end by the second reader** (none is on the delete list): the item `GREENTIDE_MECHANICS_2` (its
head and owner lines only) and `GREENTIDE_HUMMING_GROVE_1` (its rulings only); the cleanse's `bars.json` and
`census.json` (every bar, rule, check, meeting and census row heading, not every field); the freeze rulings (R1,
R5, R10, R17, R24 and the header); the mechanics review, owner cards, fluff cuts and experiences (their Greentide
passages). **Not opened:** the cleanse's `review.json` and `converge.json`; the codex run's `QUESTIONS.md` and
`record.json`; the items `GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1`, `GREATBOLE_HARVEST_LADDER_1`,
`THEY_MOD_REPLICATION_1`, `EXPLOSIVE_PLANT_GROWTH_1`, `WETBULB_FOLD_INTO_HEAT_1`, `BLOWER_ROOM_COOLER_1`; the
growth roster; the rites register and `v2_nine_rituals.md`; the Wildsteam cast file. The shared names doc was
read to its end by the Fever Wood's second read.

**Two findings for other pages** (this run may not edit the shared-machinery file): its fuel table lists the
Greentide as "richer" with resin as the crew's source, against R5; and R5's table also speaks to the Fever Wood
(*"seep oils: slow seeps, hard to gather"*) and the Sump (*"tar: not fuel — must be processed"*).

Companion to `design/concepts/Greentide/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the
overriding priority"*. The Greentide needed less bending than the Fever Wood: its own pressure runs in hours and
days, and one of its older design passes had already concluded *"The Greentide is a destination, not a home."* The
one large change is whose home is being defended. The cleanse proposal of 2026-11-17 built 0.1.0 around a colony
holding a jungle home; this design keeps the same struggle and makes the home the landed ship.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## Changed after his rulings of 2026-11-18

His card of 2026-11-18, 3:10 PM PST answered all three questions the first pass left for him here, and ruled on
stop length and on a test for every solution. This revision changed the design and this page as follows and
nothing else.

1. **Stop length is stated, as an outer edge.** The "UNSETTLED: how long a visit lasts" paragraph is gone. The
   design says about six weeks at the outside, from the pursuit's own arithmetic and the Greentide's cover, on his
   words *"The numbers you're generating are likely the outer edge allowable for each biome, and that's just fine.
   Go with that."*
2. **Canopy and steam are partial cover from orbit**, and together they are one step, not two. The question is
   removed and answered by his card. **My reading, to check:** "one step" is written as one band on the pursuit's
   built visibility scale (hidden, discreet, noticed, marked, exposed); noticed to discreet multiplies each wait
   by 1.4 in today's provisional numbers. Whether a clearing costs the step while the steam is up is marked
   `UNSETTLED`, assumed not.
3. **The hull rasp is back, in 0.1.0.** It was "lost (not chosen 2026-10-02)". His card of 2026-11-18 asked about
   hull wear naming *"the Greentide hull rasp you did not choose on 2026-10-02"* and he answered *"Yes in 0.1.0."*
   I read that as choosing it now. The brief said not to invent a wear where a source names one, and this is the
   one the Greentide's sources name. If he meant hull wear in general and still not the rasp, the fallback is that
   falling trees are the Greentide's only wear and the rasp's lines come out (one section paragraph, one promise
   row, one scope line, one on-screen moment).
4. **Resin is the Greentide's richer fuel source.** The question "Is resin ship fuel?" is removed. The slow
   biomass route is stated (with greenwood as its feedstock); the resin recipe and fuel on sale are 0.2.0 (nothing
   builds either, and his words give no version). The Greentide is written as richer, not replete; the sheet's
   *"the dayside's fuel economy"* could carry replete, and that is his word to give.
5. **A new section in the design, "The ship while it sits here"**, holds cover, hull and fuel together. Two
   promises were added to the 0.1.0 table (the rasp; the step of cover), two on-screen moments (scraping the ship;
   wood for fuel), three scope lines in 0.1.0 and one in 0.2.0, and the rasp left the dropped list.
6. **"Very Jawa" applied where a choice was open:** fuel is bought from the crew's own cousins at the band's edge
   and paid for in greenwood; the hull is scraped by hand with whatever is in the hold; the blower that keeps the
   rasp off burns the fuel the crew came to buy.
7. **A finding for the shared-machinery file:** the hull-wear frame already exists in the campaign
   (`src/RimUtinni/ShipShields/`, with his shield rulings of 2026-09-02 in
   `design/Jawa/proposals/ship_shields_deep_design.md`). His line there decides the shield answer to the rasp: the
   light screen handles *"bio contamination"*.

Read for this revision, in part: the review's three rasp passages and its ruling row (found by search);
`the_greentide.md` §7 and §8 (the goods and the Jawa lines); `RM_DryAirBlower.xml` (its fuel lines); and the
shield and pursuit files listed on the Fever Wood's choices page.

## The ones I would look at

1. **The living greatbole tower.** *"Squatting inside an organism that is actively trying to heal you out of it."*
   It is the most original thing in the biome, his, built, and the cleanse's runner-up. It stays in "later" because
   mining a home into a tree is what a colony does over weeks. Two parts of it fit a ship on the run and I did not
   pull them forward on my own authority: rooms *"invisible from outside"* as a place to hide people and cargo from
   an Imperial probe, and the catastrophe (explosives bring the whole tower down across fifty cells) as a parting
   shot at a siege camp.
2. **The hull rasp** (a colony organism that rasps the landed ship's metal, scraped off by hand, dying when the ship
   flies). He did not choose it on 2026-10-02, before he stated the ship lens. It is the only idea in any Greentide
   source written about the ship itself. It was lost in the first pass and is back in 0.1.0 after his ruling of
   2026-11-18 (see the change list above for the reading that rests on).
3. **Concealment biology** (scent-masking, a resin that kills a working camp's noise, coatings that read as
   vegetation). One of ten reward ideas of 2026-09-22, never ruled, unbuilt. Under the lens it is the direct answer
   to "is there anything here that helps them hide from the Empire". Kept in "later".
4. **The bottled growth extract**, *"the explosive-growth mechanic in a jar. Force a crop, rush a treeline, sabotage
   a doorway."* The sheet calls it the biome's killer export, and it is exactly what a ship carries away. Unbuilt;
   "later".
5. **Wet-bulb heat and the second survival kit.** *"The desert kills you dry; the Greentide kills you wet; the same
   planet demands two opposite kits, and a Jawa trader sells both."* Lost to the one-sun ruling of 2026-10-19, and
   rightly; the sentence is the best line in the sheet and I kept the first half of it.
6. **The vurrak.** The cleanse deferred it. I moved it into 0.1.0: it is built, it passed three live checks on
   2026-10-08, and *"the ground itself stands up"* under a Jawa is the lens in one image.
7. **Plants that act.** His 2026-09-22 direction names *plants* first among the dangers. 0.1.0 has falling trees,
   sight-blocking growth and the green at the doors, and no plant that grabs anyone, because none is built. They
   are 0.2.0. If 0.1.0 reads to him as a jungle whose plants are scenery, this is the row to change.
8. **The ruled first payoff.** By card on 2026-09-25 he chose *"survivors become specialists"* as the first new
   reward to build. The cleanse moved it to "next version". I put it at 0.2.0, not 0.1.0: it pays on the *second*
   jungle stop, which a ship reaches and a first version does not need.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **Vurrak, the bank ambusher:** next version → 0.1.0. Built and live-checked; the lens in one image.
- **Yearning fruit's tax (early hunger, filth, the waddle):** next version → 0.1.0. Built; slapstick within the
  first hour. Its seed passage goes to 0.2.0.
- **Plants that act (maddrick, gorbeleth, phorrik, zhorrel):** next version → 0.2.0. This also answers the
  cleanse's first question to him (can falls alone carry the plant danger): for one version, yes.
- **Thurrock shouldering walls; illisk immune to all but blast; steam devils; the zrrik:** next version → 0.2.0.
  Creature moments a crew can meet in a week.
- **Giant ant raids:** next version → 0.2.0. "Who else here attacks" is one of his lens questions.
- **Fever mark and deliberate dose:** next version → 0.2.0. His card; and a dose taken on purpose before a deadline
  is a ship-crew decision.
- **Lace found by studying a branch:** next version → 0.2.0.
- **Stench grenade:** next version → 0.2.0. The fluff-cut review of 2026-10-23 called it the ruled one tool for the
  biome's animals.
- **Acoustic sounder readings:** next version → 0.2.0. A ship part.
- **Cuisine:** the cleanse's second question, answered by scope: ordinary cooking in 0.1.0, the combining system
  later.
- **Entrance care after paving:** the cleanse's third question, answered: paving ends regrowth on its cells; a
  visiting crew's care is on the unpaved ground it uses.
- **Stayed "later" from the cleanse's "next version":** the living greatbole package, moving roads, salinity, the
  habitable band, canopy drip, growth extract, ant materials, weapons beyond the stench grenade, branch travel, the
  rite. Not moves.
- **The hull rasp:** dropped (not chosen 2026-10-02) → 0.1.0, on his ruling of 2026-11-18. Revert by restoring it
  to the design's dropped list and deleting its promise row.
- **Canopy and steam as partial cover from orbit:** asked of him → 0.1.0, campaign layer, by his card.
- **Resin to chemfuel; fuel bought at the band's edge:** asked of him → 0.2.0. The source is his ruling; the
  version is my choice. 0.1.0 instead costs one recipe and a trader stock line.
- **New, not in any source:** greenwood as what the crew pays the crawlers with for fuel (a reading of two sheet
  lines, no mechanism); the blower's fuel draw named as a cost of holding the hull.
- **New, not in any source:** the ship as the foothold being defended; the Empire's troopers mired; sight-blocking
  growth as what the probe and spotter cannot see through. These are readings of built behaviour. (Dropped gear
  going under the mud is in a source after all: the kit spec's *"battlefield drops vanish but hauling is safe"*.)
- **Second reader, 2026-11-18. Illisk blast-only hide:** 0.2.0 → 0.1.0. His typed words define the creature by it
  and it is built. Revert by moving the line back in the design's Scope section.
- **Second reader. Resin to chemfuel made by the crew:** 0.2.0 → a question for him. His ruling R5 says a
  settlement makes it; buying it stays at 0.2.0.
- **Second reader. The rooted ambusher (a plant that is an animal):** shared machinery → named in 0.2.0 with the
  plants that act. His words of 2026-09-22 approve it; its home biome is a question for him.

## Every idea, row by row

Source names: *sheet* = `biomes/the_greentide.md`; *flora roster* = `biomes/greentide_tree_roster_2026-09-22.md`;
*risk-reward* = `biomes/greentide_risk_reward_2026-09-22.md`; *bedazzle review* = `biomes/greentide_bedazzle_review_2026-10-02.md`;
*terror design* and *terror consult* = `biomes/greentide_terror_replacement_design_2026-10-02.md` and its
`_gpt_consult_` sibling; *crossovers* = `biomes/greatbole_atmosphere_crossovers_design_2026-10-02.md`; *kit spec* =
`biomes/kits/greentide_kit_spec.md`; *harvest spec* = `biomes/kits/greatbole_harvest_spec.md`; *roster json* =
`biomes/rosters/the_greentide.json`; *names doc* = the shared non-canon names file (all under
`design/Jawa/worldbuilding/`); *cleanse* = `design/concepts/Greentide/cleanse/`; *walk* =
`design/validation_walks/RimMandrake/Greentide.md`; *owner answers* = `design/RimMandrake/designer_codex_2026-11-09/Greentide/ANSWERS_OWNER.md`;
*mechanics review* = `design/RimMandrake/special_mechanics_review_2026-10-22.md`; *owner cards* =
`design/RimMandrake/biome_owner_cards_2026-10-22.md`; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*experiences* = `design/RimMandrake/biome_experiences_2026-10-20.md`; *growth roster* =
`design/RimUtinni/explosive_plant_growth_roster.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "A green ribbon of total war, steaming, growing while you watch" | sheet §9 | kept, quoted | | |
| Water is the only argument; the three water-laws of the dayside (oasis, canyon, Greentide) | sheet header, §2 | lost from this design | World lore; a crew at one stop does not compare three biomes. | One sentence in a world document; free. |
| No truce, ever | sheet header, ban 1 | kept, quoted | It is also the answer to "who hates the Empire": everything, impartially. | |
| Measured tiles, river share, gorge country, temperatures | sheet §0 | lost | A tile count is never evidence; the planet is painted at the end. | |
| Donor inventory (animal density, disease load, terrain family) | sheet §0 | kept as build facts, not design | | |
| A gallery jungle a few tiles wide, visible from the dunes as a line of steam | sheet §1 | kept, quoted: it is what the ship sees on approach | | |
| "You don't sweat, the air sweats you" | sheet §1 | kept, quoted | | |
| Tree crashes as the background percussion | sheet §1, §5 | kept, quoted | | |
| Maximum sun times permanent water | sheet §3 | kept as the reason growth is fast | | |
| The inversion lid: steam that cannot rise | sheet §3 | kept as the Roil | | |
| The dying river: saltier every mile, ending in a salt grave | sheet §3, §5 | kept in "later" | A property of the river's whole course; one stop sees one reach. | Per-map salinity: a mapgen system, cost L. |
| Droid enclaves at the river graves | sheet §3, §8 | kept in the campaign layer | The biome places no settlement. | |
| The habitable band: too close cooks, too far desiccates | sheet §4b, §5 | kept in "later" | The cleanse found no built distance law; the ship lands where it lands. | |
| Homes made by going down; windowless mud domes; no windowed native architecture | sheet §4b, ban 4 | kept in the campaign layer (a constraint on templates) | | |
| No dry ground pockets; no safe standing water | sheet bans 5, 6 | kept | The water triad carries the second. | |
| No high-flammability native flora; fire is not the tool | sheet §4b, ban 3; flora roster §5 | kept | | |
| Experience line: "Abundance with teeth: everything grows, and everything sinks. Fight the jungle every day or lose your base to it." | experiences, walk, mechanics review | kept, quoted; "your base" read as the ship | His card of 2026-10-20. | |
| His November answers: defend an inhabited foothold; recovery first, then abandonment; rescue ends on firm ground | owner answers | kept, quoted; the foothold is the ship | The answers fit a landed ship better than a colony: "evacuation with supplies left behind" is the campaign's own loop. | Hold the colony reading: 0.1.0 is then a settlement sim nobody in the campaign plays. |
| "The Greentide is a destination, not a home" | risk-reward §3a | kept, quoted | | |
| "You look at the map when you land and decide to go around" | risk-reward §3a | kept, quoted as the landing's test | | |
| Choked with foliage, virtually no square uncovered | flora roster §1 | kept, quoted | | |
| Jawa presence: trade, not settlement; crawlers at the band's edge; both kits sold | sheet §8, §4b | kept, reshaped: used as the crew's backstory with this place | It is the textual basis for "never THIS close". The kits half is lost with wet-bulb. | |
| The elevated-thirst races come home; the densest crowd of big wet aliens | sheet §4b, §8 | kept in the campaign layer | | |
| The Wildsteam's two seats, safe harbour, bathhouses | sheet §0, §8 | kept in the campaign layer | Whether they fight the Empire is unsettled. | |
| Greentide as its own free-tier mod | kit spec ruling 4 | kept (done) | | |
| Art theme: light, palette, silhouettes, motion | sheet §9 | kept as art direction | | |

### Weather, ground and growth

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The Roil: low hot fog hiding the floor, not the world | sheet §4c, kit spec | kept | | |
| Breaklight: "clarity as the disaster" | sheet §4c | kept, quoted | Rare, but hours long and unmistakable when it comes. | |
| Seek-shade scramble in a clearing | kit spec ruling 3 | kept | He rejected deferring it. | |
| Steam devils and scald damage | sheet §4c | moved (cleanse next version → 0.2.0) | | |
| Underlight rain, dripping forever under the canopy | sheet §4c | kept in "later" | Unbuilt, cosmetic. | |
| Wet-bulb heat as an ambient kind; shade and roofs do nothing | sheet §4b, kit spec | lost | One sun from geometry; no biome heat (2026-10-19). | |
| The second gear tree (wicking, sealed, dry-air) | sheet §4b | kept, reshaped (corrected by the second reader): ordinary heat clothing | The heat kind is lost; the clothes are not. | |
| The dry-air blower: repels growth, repels animals, cools the room behind | sheet §4b | kept, reshaped: repels growth and cools; "repels animals" is not promised | The cleanse says it is no guarantee against an animal already attacking. | Promise the animal effect: needs its own scene. |
| "When it fails the green notices within hours" | sheet §4b | kept as the blower scene's control | | |
| Visible growth; plants grow into and block your doors | sheet §5 | kept, quoted; the doors are the ship's | The signature. | |
| Darkness brings roots, light brings leaves, only dry heat repels | sheet §4 | kept, quoted | | |
| Grazing suppresses encroachment; a penned herd is a living defence | sheet §4, kit spec | kept | Real eating only. | |
| Paving ends regrowth on its cells | cleanse | kept | | |
| Upkeep rises with the size of the presence | risk-reward §3a | kept as a consequence, not a promise | | |
| Churnmud: slow, swallows dropped items, mires the unlucky | sheet §8b | kept | "Everything sinks." | |
| No exemption for stockpiles | kit spec ruling 1 | kept | *"The biome makes you engineer."* | |
| Under the Roil you cannot see which mud is the hungry kind | sheet §8b | kept, quoted | | |
| Dug-out things come back as they went in | cleanse | kept (a known defect today: detail is lost) | | |
| Root causeways as the roads, contested by everything | sheet §8b | kept | | |
| The roads slowly move between visits | sheet §8b | kept in "later" | | |
| Churnmud on other biomes | mechanics review, fluff cuts | lost (off, unsupported, by ruling) | | |
| Sealing mud with resin | kit spec, cleanse | kept as ordinary engineering | | |
| Movement difficulty as a world-map stat only | risk-reward §1 | kept as a build fact | | |
| Density and movement sliders | mechanics review | kept (settings) | | |
| Three phases: trespass, foothold, expedition economy | risk-reward §3 | kept, reshaped: a stop is the first phase and the start of the second; the third is later | Thirty visits is not a stop. | |
| Two hazards never softened: the swarm chain and the tree fall | risk-reward §3c | kept for the fall; the swarm chain belongs to the shared hostile-plant engine | | |
| Danger stays flat | risk-reward Q4 | kept, quoted | | |

### Plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Our own invented roster, no canon tree; "get wild with them" | flora roster | kept | | |
| Fifteen trees in four strata, seven understory plants | flora roster §3 | kept as the roster | | |
| The silhouette brief and legibility matrix | flora roster §3e | kept as art direction | | |
| Veluthar, the umbrella; the Swingers' road | flora roster | kept | | |
| Mourvel, the weeping curtain, a room with walls | flora roster | kept as a plant; concealment not promised | | |
| Kaddrath, roots first; the causeway generator | flora roster | kept | | |
| Sarnstilt, a tripod in the river; falls across the channel | flora roster | kept | | |
| Brunnock, slow and heavy | flora roster | kept; it pays greenwood, not hardwood (corrected by the second reader) | Hardwood became the fellable giant's alone. | |
| Ghemmel, the commons, bleeds red | flora roster | kept | | |
| Nemmer, fruit too big for the branch; gall host | flora roster | kept; periodic fruit drops later | | |
| Vurmeloth, the crimson export | flora roster | kept as timber | | |
| Mirrelbole, split and bleeding; tapping it is the risk | flora roster | kept as a tree; sap-tapping later | The cleanse deferred tapping. | |
| Zhorrel, the strangler | flora roster | moved (→ 0.2.0) | | |
| Quathis, the flat fan; roofing | flora roster | kept | | |
| Thalquith, the aquamarine lattice that hums | flora roster; cleanse | lost from the Greentide (it lives in the Chill now) | Already rehomed. | |
| Cundral, acid pods over a forageable root | flora roster | kept as forage; the pods later | | |
| Gorbeleth, the throat that spits | flora roster | moved (→ 0.2.0) | | |
| Brakkel, the forage staple | flora roster | kept | | |
| Tumbel, gourds and containers | flora roster | kept as food; containers not promised | Not found built. | |
| Sarquin, the sugar drip; primary gall host | flora roster | kept | | |
| Phorrik, bursting spore bladders; medicinal | flora roster | moved (→ 0.2.0) for the cloud; harvest kept | | |
| Wollick, the tuber | flora roster | kept | | |
| Maddrick, the static trap; a free perimeter | flora roster | moved (→ 0.2.0) | | |
| Illurin, the only light under the canopy | flora roster | kept | | |
| All seven understory plants block sight | flora roster §3d | kept, quoted | Built in the shared sight engine. | |
| Hostile mobile plants hiding on the covered floor | flora roster, risk-reward §1a | folded into shared machinery | `HostileFlora`; not found wired to this biome. | Wire one in at 0.2.0. |
| The fellable greatbole; the largest fall on the map; true hardwood | flora roster §3a0, sheet §7 | kept | A week-sized project and a real prize. | |
| Two giants by life stage (fellable tree, mineable landmark) | flora roster §4 | kept; the landmark is "later" | | |
| Greenwood, abundant beyond counting; hardwood only from giants | sheet §7 | kept, quoted | | |
| The fruit yearns to be eaten: accelerants, hunger, filth, the waddle | sheet §4 | moved (→ 0.1.0) | | |
| Seed passed in filth and sprouting | sheet §4, mechanics review | moved (→ 0.2.0) | Couples to the growth signature. | |
| Sap and resin: glue, lacquer, waterproofing | sheet §7 | kept as resin | | |
| Sap rendered to chemfuel, the dayside's fuel economy | sheet §7 | kept, reshaped (corrected by the second reader): a settlement makes it and the crew buys it | His freeze ruling R5 of 2026-09-07 calls sap-chemfuel *"not player-tappable — a settlement-level investment"*; his fuel ruling of 2026-11-18 says fuel can be bought. | A crew recipe at 0.2.0, as the first read had it: asked under NEEDS HIM. |
| The slow route: greenwood rendered to chemfuel | his ruling of 2026-11-18; sheet §7 for the wood | kept (the emergency route; the base game's refining) | *"Every biome has a fuel source."* | |
| Crawlers at the band's edge, and the Wildsteam's seats, as where fuel is bought | sheet §8 | kept, reshaped: named as the sellers; campaign layer, 0.2.0 | *"You can also buy it... very Jawa."* | |
| Greentide extract | sheet §7 | kept in "later" | Unbuilt. | See above. |
| Eggs, chitin, medicine, fresh water upstream | sheet §7 | kept, reshaped: the lace is the medicine; eggs, chitin and hauled water are not promised | Not found built as Greentide goods. | |
| Toxin sealant from resin | kit spec ruling 2 | kept in "later" with the living tower | | |
| Canon and donor plant rows; what their growth class is | roster json, growth roster | kept where the campaign patch puts them | | |
| Sugar-famewort | roster json, cleanse | lost (recommended for dropping; his to confirm) | | |

### Animals, insects and sickness

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The six sorts: Gnawers, Shatterers, Brakes, Lungers, Swingers, Fliers | sheet §4 | kept as the roster's shape | | |
| Three fellers, one fall | sheet §4 | kept | | |
| Krannock, the gnawer | bedazzle review §3, cleanse | kept | | |
| Thurrock, the tree-felling herd; "a weather event" | bedazzle review §3, §8 | kept, quoted | His card. | |
| Thurrock shoulders walls when provoked | bedazzle review §3 | moved (→ 0.2.0) | | |
| The moulting giant | bedazzle review §5 | lost (not chosen) | | |
| Sulleth, the grazer, always eating | bedazzle review §3 | kept | | |
| Dhollock, the deep-water lunger | bedazzle review §3 | kept | | |
| Yammeth, the screaming flock, and the one that stops | bedazzle review §3 | kept | | |
| The silence before the predator | sheet §9, kit spec ruling 3 | kept, quoted | | |
| Working between the crashes (noise as cover) | bedazzle review §5 | lost (not chosen) | | |
| Canopy swinger; branch travel | bedazzle review §3, cleanse | kept in "later" | | |
| Vurrak, the bank that stands up; its fairness rules | terror design | moved (→ 0.1.0) | | |
| Four other bank-ambusher candidates | terror design §2, terror consult | lost (not recommended) | | |
| Illisk, the toothy shoal | terror design (his words) | kept; blast-only resistance back in 0.1.0 (second reader; the first read had it at 0.2.0) | It is his typed definition of the creature. | |
| The dianoga's old slot here | terror design | lost (removed by his ruling) | | |
| Skerrel wasps in galls on sarquin and nemmer | flora roster, mechanics review | kept; natural gall placement owed | | |
| Insects as their own canopy layer | risk-reward Q3 | kept (the krannock) | | |
| Zrrik | cleanse | moved (→ 0.2.0) | | |
| Giant ants as raiders, ours and franchise-free | owner cards, mechanics review | moved (→ 0.2.0) | | |
| Ant carapace as building stock | cleanse | kept in "later" | | |
| Gristle hunting underground | cleanse, roster json | kept in "later" | | |
| The vanilla seven and the placeholders | bedazzle review | lost | | |
| Canon and donor animals | roster json, risk-reward §1b | kept where the campaign patch puts them | | |
| Exotic catch; no underwater beasts for the fish | risk-reward §2a | kept | | |
| Seven vanilla diseases | risk-reward §1c | kept, reshaped: flu and malaria out, the Frenzy in | His ruling. | |
| The Frenzy | risk-reward Q2 | kept | | |
| The Frenzy as a dose taken on purpose | mechanics review | moved (→ 0.2.0) | | |
| Survivors become specialists | risk-reward Q1 | moved (→ 0.2.0) | | |
| Stellock lace | bedazzle review §8 | kept | | |
| Finding it by studying a branch | bedazzle review §5 | moved (→ 0.2.0) | | |
| Stench grenade; seeding and toxin weapons | mechanics review, cleanse | grenade moved (→ 0.2.0); the others later | | |
| Names for donor rows | names doc | kept | | |

### The living tower, rewards, rites and the ship

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The living greatbole: mine rooms in, it heals shut, sealant holds | sheet §7b | kept in "later" | See "the ones I would look at". | 0.2.0 for hiding rooms only: a large test surface. |
| Wild greatboles as dungeons | sheet §7b | kept in "later" | | |
| The harvest ladder: shaking, violent healing, catastrophe | harvest spec | kept in "later" | | |
| "A pick cannot reach 70%"; only explosives can | harvest spec | kept in "later", quoted in the list above | | |
| Fruitfall, fruit steaks, Royal Rind and its coat, seeds, grubs | harvest spec | kept in "later" | | |
| The song as a progress bar | harvest spec §5, crossovers §2 | kept in "later" | | |
| The cool sanctuary inside | crossovers §3 | kept in "later" | | |
| Pilgrims who come to hear it | crossovers §4 | kept in "later" | | |
| Anima and servant crossovers | crossovers §5 | kept in "later" | | |
| Fire cannot excavate it | harvest spec §6 | kept in "later" | | |
| Immunological capital | risk-reward R1 | kept (the fever mark, 0.2.0) | | |
| Medicines priced in hours | risk-reward R2 | kept in "later" | Never ruled. | |
| Cuisine as a combining system | risk-reward R3 | kept in "later" | | |
| Regrowing a lost limb | risk-reward R4 | lost from the Greentide (corrected by the second reader: he moved it to the Contagion on 2026-09-22) | The first read had it "kept in later". | |
| Live bloodstock | risk-reward R5 | kept, reshaped: ordinary taming covers it | | |
| Domestication as a desert cultivar | risk-reward R6 | kept in "later" | | |
| The living laboratory | risk-reward R7 | kept in "later" | | |
| Concealment biology | risk-reward R8 | kept in "later" | See above. | |
| Grown construction | risk-reward R9 | kept in "later" | | |
| Reputation as sole supplier | risk-reward R10 | kept in "later" | | |
| The Ceded Room rite: *"Build it outside the ship and let it be taken"* | bedazzle review §8 | kept in "later" | His later ruling put it in a second version. | |
| The Open Boast | bedazzle review §8 | lost from the Greentide (it is the Warscar's) | | |
| The Uprooting | bedazzle review §6 | lost (not chosen) | | |
| The hull rasp | bedazzle review §5 | moved (dropped → 0.1.0) | His ruling of 2026-11-18 on hull wear, asked with the rasp named. | Keep it dropped: the Greentide's only wear is then the falling tree. |
| The rasp is on every metal building alike, no ship special case | bedazzle review §5 | kept, quoted | | |
| The blower as the rasp's natural counter; scraping by hand in the heat | bedazzle review §5 | kept, quoted | | |
| The damage flies home; the rasp dies away from the jungle | bedazzle review §5 | kept | It is what keeps the wear a reason to leave and never a trap. | |
| Painting exposed plate with resin lacquer to keep the rasp off | not in any source (the sheet lists resin as lacquer and waterproofing; the rasp eats *wet* metal) | lost: not written into the design | A new idea and a good one for this crew; left out because no source ties resin to the rasp. | Add it as a third hands-on answer: one more job and one more scene. |
| Acoustic sounder readings | cleanse | moved (→ 0.2.0) | | |
| Natural-placement scoring | cleanse, fluff cuts | lost (no worldgen) | | |
| Mod Settings | cleanse, mechanics review | kept | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (growth feeds and reclaims; clearing, blower, grazing, paving) | cleanse definition, owner_pages | kept as the core of 0.1.0, with the ship as the home | | |
| Its three questions to him | cleanse owner_pages | kept, reshaped: answered by scope (see scope moves) | The card of 2026-11-18 said move it and list the move. | |
| Forty-colonist home, season model | cleanse definition, models | lost | Colony scale. | |
| The other offline models (situations, footing geometry, clearing and heat timing) | cleanse models | kept | | |
| Tickets and switch-offs | cleanse tickets | kept as they stand, except where a feature moved | | |
| Eight proposed bars | cleanse bars | kept as history; the twelve promises in the design are the proposal to argue from | | |
| The must-be-true list and draft north star | walk | kept | | |

### Rows added by the second reader

More source names: *freeze rulings* = `biomes/_freeze_rulings_2026-09-07.md`; *density item* = `GREENTIDE_BIOME_DENSITY_1` and `GREENTIDE_DENSITY_SETTINGS_1`; *tree item* = `GREENTIDE_JUNGLE_TREE_ROSTER_1`; *understory item* = `GREENTIDE_UNDERSTORY_PLANT_ROSTER_1`; *sight item* = `GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1`; *fish item* = `GREENTIDE_EXOTIC_JUNGLE_FISH_1`; *terror item* = `GREENTIDE_TERROR_REPLACEMENT_1`; *vurrak item* = `GREENTIDE_VURRAK_BUILD_1`; *illisk item* = `GREENTIDE_ILLISK_BUILD_1`; *wasp item* = `GREENTIDE_WASP_SWARM_1`; *swarm item* = `GREENTIDE_CANOPY_SWARM_1`; *specialists item* = `GREENTIDE_FEVER_SPECIALISTS_1`; *frenzy item* = `GREENTIDE_FRENZY_DISEASE_1`; *grenade item* = `GREENTIDE_GRENADE_WEAPONS_1`; *exchange item* = `GREENTIDE_RISK_REWARD_EXCHANGE_1`; *cast item* = `GREENTIDE_FREE_ROSTER_OWNED_1`; *mod build item* = `GREENTIDE_RM_MOD_BUILD_1`; *fruit item* = `GREENTIDE_YEARNING_FRUIT_1` and its `_FILTH_` sibling; *contagion item* = `CONTAGION_GENOME_ORGAN_GROWING_1`; *ambusher item* = `HOSTILE_MOBILE_PLANTS_1`; *ant item* = `GREENTIDE_ANTS_MIGRATE_NO_ANT_LEFT_BEHIND`; *rite item* = `GREENTIDE_CEDED_ROOM_RITE_1`; *lace item* = `GREENTIDE_STELLOCK_LACE_BUILD_1`; *thurrock item* = `GREENTIDE_THURROCK_HERD_BUILD_1`; *port item* = `GREENTIDE_BASE_PORT_BUILD_1`; *donor item* = `MIASMA_FEVERWOOD_GREENTIDE_BMT_1`; *grove item* = `GREENTIDE_HUMMING_GROVE_1`; *bark item* = `GREATBOLE_BARK_EDGE_ART_1`; *owner ledger* = `infrastructure/state/ledger/events/OWNER.jsonl`; *codex notes* = `design/RimMandrake/designer_codex_2026-11-09/Greentide/NOTES.md`. Items are under `infrastructure/state/items/` or its `closed/` folder.

#### His words that had no row

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Fuel is scarce: *"the fact that people have found SO MANY ways to get fuel is still evidence of its scarcity"*; sap-chemfuel is *"not player-tappable — a settlement-level investment"* | freeze rulings R5 (owner, 2026-09-07) | kept, reshaped: the design's fuel section now says sap-chemfuel is made by settlements and bought by the crew | The first read took the sheet's "rendered chemfuel" as a crew recipe; his own ruling on that line says a settlement makes it. It agrees with his words of 2026-11-18, *"You can also buy it"*. | A crew-run resin recipe at 0.2.0, as the first read had it: against R5 unless he says the newer ruling replaces it. Asked under NEEDS HIM. |
| *"Green wood does not burn; seasoned wood does."* The export is dried greenwood; drying is *"long, space-hungry and settlement-scale"*, *"never a supply a passing player taps"* | freeze rulings R24 (owner, 2026-09-07) | kept, quoted: the crew cuts and sells it green; it is feedstock for the slow render, not firewood | The design called a hold of greenwood burnable. A ship on the run is the passing player. | Let the crew burn it wet: against R24. |
| The Greentide holds the Wildsteam capital; Sporefall is the second city | freeze rulings R10 | kept in the campaign layer, stated in "Who else attacks" | | |
| Fliers cross biomes: *"there will certainly be fliers that visit multiple biomes"* | freeze rulings R17 | kept as a standing rule | A flier seen here from another roster is not a defect. | |
| The Scald is a perched ocean that spills the world's rivers; all five Scald rivers flow out | freeze rulings R1, R31 | kept as world lore; the design says "storm peaks" and takes no side | The cleanse says the Scald is terminal, citing a corrected world definition. R1 is his; which is newer was not settled by this read. | Settle it in the world document, not here. |
| *"2+3, most are useful, many are dangerous."* Reward and hazard are often the same plant | density item (owner, 2026-09-22) | kept, quoted | Six roster rows are literally both. | |
| Density at the top of what the base game allows (the plant-choked swamp's own numbers); "movement extremely difficult" is the world-map stat | density item | kept as build facts | A tuning number is never a bar. | |
| Sliders that soften density and travel cost, never below ordinary rainforest | density item | kept (settings) | *"This is a jungle, not a plain."* | |
| *"I would like to review the plants and their sizes before you generate art. I really want these to be huge, and want to make sure you were sufficiently bold."* | tree item (owner, 2026-09-22) | kept, quoted | Boldness went above the range (the sixteen-cell giant); the middle was not inflated, by his ruling. | |
| Plant names stay *alien and organic*, not Jawa | tree item (ruling 3) | kept | The crew does not name these plants; nobody does. Do not rename them into a Jawa register for the ship lens. | |
| *"We should just put the flammability as very low, don't stress about it."* | tree item (ruling 4) | kept, quoted; the question is closed | | |
| *"Fire will harm and burn things, but no they do not catch fire themselves, just take damage."* An incendiary leaves a scorched hole, not a burning jungle | flora roster §5; tree item | kept, quoted in "When the Empire arrives" | It tells the player what a flame weapon does here, on either side. | |
| *"The top mod without star wars will look precisely the same as the star wars enhanced one save for any star wars beasts"* | tree item | kept as the tier rule | | |
| *"We work on drafting the replacements for everything right now. No reason to wait! Let's do this!"* All ten borrowed plant rows replaced | tree item; flora roster appendix C | kept (done) | | |
| *"Absolutely not. We should have wild jungle trees with bizarre Starwars names... a diversity of perhaps ten types of trees at least. Plus the signature huge tree."* | tree item; flora roster §1 | kept (the roster is the answer) | | |
| No coniferous forms; large leaves, hanging tentacle leaves, willow canopies | flora roster (owner, 2026-09-22) | kept as art direction | | |
| The landmark is *"a blob of wood on the map, representing a trunk so vast that you can't even see the tree in the game"*; its edge reads as bark; *"How this became a Deep Drill I have no idea."* | bark item (owner, 2026-09-23) | kept in "later" with the living tower | | |
| *"Create exotic new jungle fish to catch, not base game fish. Weird aquatic worms, eels, parasitic moving plants, toothy tadpoles, spiked eels... get wild"* | fish item (owner, 2026-09-22) | kept, quoted | Eight invented river fish are built. | |
| The parasitic moving plant is *"a very strange kind of fish to catch"* | fish item | kept as a catch | | |
| *"But yes we should ALSO make some 'animals' that are hostile mobile plants too, that's cool."* It *waits, rooted and still*; *"one of its leaves occasionally twitches if you watch carefully"*; it wakes *"if others of its own kind activate nearby: swarm"* | ambusher item (owner, 2026-09-22) | moved (folded into shared machinery → named in 0.2.0 with the plants that act) | His approved creature and the binding ruling's home for plant danger. The first read left it as machinery. Which biome it lives in was never ruled. | Leave it out of the Greentide until a sitting names its home. |
| "Something you walked past twice turns out to have been waiting for you." | ambusher item (criteria) | kept, quoted | | |
| *"Let's do some very small, numerous wasps that boil out of hives attached to plants. They are easy to kill and sting you for a very small irritating HEDIFF, but multiple stings add up quickly and overwhelm."* | wasp item (owner, 2026-09-22) | kept, quoted | The design had the wasps and not his words. | |
| "You kill the first six without thinking, and then you look at the screen." | wasp item (criteria) | kept, quoted in the wrong-fruit moment | | |
| The swarm must be survivable by leaving; a gall must be visible before it is disturbed; hives are never a free farm | wasp item | kept | *"A swarm you cannot escape is not tension, it is a death notice."* | |
| The stench repels the wasps too: *"one tool, all the biome's animals"* | grenade item; wasp item | kept with the grenade (0.2.0) | So its cost is the thing to price. | |
| *"Special smoke that makes beasts flee from the stench, or that plant jungle plants in the ground near a water source... or powerful toxins that can fuel blow darts or taint water sources and anyone wading in them."* | grenade item (owner, 2026-09-22) | kept: stench at 0.2.0, the other two later | He ruled stench first; the others are *queued behind the proof, not dropped*. | Tainted water against troopers wading a reach is a ship-crew trick; it stays later. |
| "A colonist packs jungle in their bag before leaving for somewhere that has none." | grenade item (criteria) | kept, quoted in "What the crew takes away" | It is the ship lens stated before the lens existed. | |
| The Frenzy, in his words: *"It will kill you if not treated, but you can treat it in the coma stage after benefiting from the rapid work."* *"Can purposely infect someone."* | frenzy item (owner, 2026-09-22) | kept, quoted; the design now says it kills untreated | The design had the speed and the coma and not the death. | |
| The dose is an item, harvested and carried; the plant-interaction route is declined, not deferred | frenzy item | kept (0.2.0) | Built from gorbeleth toxin. | |
| Flu and malaria are out; what is left is all severe: *no warning shots* | frenzy item | kept | He accepted the cost. | |
| "A player looks at a colonist, looks at the deadline, and does something they know is a bad idea." | frenzy item (criteria) | kept, quoted beside the dose | | |
| Whether the crew reacts to one of its own being dosed on purpose | frenzy item | kept as a question (NEEDS HIM, other) | Marked unruled in the item: *flag it, do not decide it*. | |
| The fever mark is a job qualification: lead a deep trip, hold a forward camp, handle fresh medicine | specialists item | kept, reshaped: built as immunity to the Frenzy only (0.2.0) | No work gate is built. | The gate itself: later. |
| "A colony's veteran jungle-hands are visibly different from its rookies, and everyone can tell why." | specialists item (criteria) | kept, quoted in spirit | | |
| The exchange: *both sides must be extreme*; he bound danger and reward together by card | exchange item | kept | | |
| "A player who has been to the Greentide twice goes back a third time, knowing exactly what it costs." | exchange item (criteria) | kept, quoted | A second stop is the campaign's version. | |
| He ruled farming camps allowed and organ decay in as a seventh disease | mod build item (card, 2026-09-22) | kept as build facts | | |
| *"This is a really cool mechanic and suggests making the Biome Greentide its own RimMandrake level mod too."* | kit spec ruling 4 (owner, 2026-09-11) | kept (done) | | |
| The blower: *"Just add this as a special kind of room cooler. No one wants a room heater in that biome..."* | kit spec M2 (owner, 2026-10-08) | kept, quoted | | |
| Wet heat is *"hotter air on the thermometer"* | kit spec M1; cleanse | kept | | |
| The sytheclaw: *"This should not be in this biome"* | roster json (owner sheet, 2026-10-08) | lost from the Greentide (cut by him; it stays in the Pyrelands) | The review had it listed as two-homed. | |
| *"Rename the Gristle, make it realistic"*; the swarmling renamed saluksis with stranger art; the swinger named ookala | roster json (owner sheet, 2026-10-08) | kept | The roster json is the only file that still holds this sheet's words. | |
| The lunger's label in game is the dhollollo (def `RM_Dhollock`) | cleanse; `RM_Dhollock.xml` | kept: the design gives both names | | |
| The vurrak, as he ruled it on 2026-10-03: the weighted crown; bites anything that steps on it; almost no warning; the game pauses the first time one is ever revealed | vurrak item; walk | kept, reshaped: the design's moment is corrected to this | The design described the draft of 2026-10-02 (a warning, a marked cell). His card came a day later. | |
| The letter "The bank moved" | vurrak item; walk | kept, quoted | | |
| The Illisk *changes the map, not a fight*: water you route around until you spend explosives | terror item | moved (0.2.0 → 0.1.0) with the blast-only hide | *"Nearly unkillable except with explosives"* is his typed definition and is built. The deferral was a delegated cleanse call, not his. | Leave it at 0.2.0: 0.1.0 then has a shoal that dies to rifles. |
| The word for the shoal's shape never reaches a def or label | terror item | kept | Ban 2 allows the shape and bans the Earth name. | |
| *"We have plenty of creatures left to fill rosters if there are holes."* | terror item (owner, 2026-09-21) | kept | | |
| His Miasma wish for tentacle pulling, delivered by the Fever Wood's snare | terror item | lost from the Greentide (it is the Fever Wood's) | | |
| An effectively walled river and the base game's water content | terror item; illisk item | kept as UNMEASURED | | |
| *"Only the raiding events in the greentide jungles and surrounding area"* (the ants) | roster json | kept (0.2.0) | | |
| The ants moved into the free mod under our own name | ant item; owner cards card 8 | kept (done; name, art and two sounds owed) | | |
| *"Use first and third. First can be here. Build it outside the ship and let it be taken. Works better the better the room."* | rite item (owner, typed 2026-10-02) | kept in "later", quoted | It is the one rite he wrote with the ship in it. | |
| *"All 'rituals' to interact with the Nine that are based on unique Baroque Biome content are hereby documented and deferred to v2."* | owner ledger (2026-10-23) | kept: this is the "later ruling" the first read cited without quoting | Not revived. | |
| A review sheet's cut is scoped to that sheet's biome | donor item (owner, 2026-09-21) | kept as a standing rule | | |
| *"Would it be mechanically possible... to have different trees hum at slightly different frequencies... that's pretty magical..."*; *"It's ok if it were attached to the camera."* | grove item (owner, 2026-09-22) | lost from the Greentide (the humming tree lives in the Chill now) | | |
| *"An ultra-violent catastrophe, with huge logs smashing down destroying everything in its wake."* | harvest spec §2c (owner, 2026-09-23) | kept in "later", quoted | | |
| *"The sealant only seals SOME areas, while the rest of the tree heals and remains alive and harvestable. Once dead, it's dead."* | harvest spec §2c | kept in "later" | | |
| Royal Rind, named by him; *"It's all three"*: gear against the killing biomes, a vacuum garment, a luxury | harvest spec §3b | kept in "later" | *"Makes the jungle the gateway to the rest of the planet."* For a ship that must visit those biomes this is the tower's strongest pull. | |
| *"Those grubs are NASTY to deal with."* | harvest spec §3b | kept in "later" | | |
| *"For Utinni, both will be switched off of course"* (anima focus, tree servants) | harvest spec §8b | kept in "later", off | | |
| Limb regrowth: *"(2) is a really interesting idea that could be adapted for the Contagion"* | contagion item (owner, 2026-09-22) | lost from the Greentide (moved by him to the Contagion) | *"The Greentide keeps no limb-regrowth content."* The first read had it "kept in later". | |

#### The place, the ground and the weather

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| *"Not fog: STEAM"*; the steam deflects part of the sun | sheet §3; kit spec M4 | kept as light only (a bright overcast); no heat discount | One sun from geometry. The dimmer light is on the frozen twin only today. | |
| The rivers enter sterilized and clean from the Contagion's country | sheet §2 | kept as lore | | |
| The admission test: grows or eats at Greentide speed, carries no truce, is not a terrestrial animal | sheet §4; roster json | kept | | |
| "Everything is eating or being eaten, mating or laying eggs, growing visibly or dying trying." | sheet header | kept, quoted | | |
| "Food is enormously abundant, and every export has a tooth in it somewhere." | sheet §5 | kept, quoted | | |
| Bridges are precious; crossing water is the scariest routine act | sheet §4; kit spec M7 | kept | *"A bridge protects footing, not the whole bank approach."* | |
| Downstream: milky water, crusted margins, brine-adapted horrors | sheet §3 | kept in "later" with salinity | | |
| *"The water dies before the fish law does"*: no fish in the brine reaches or the graves | roster json | kept in "later", quoted | | |
| The riverless tiles are the dying river and its graves | sheet §0 (owner, 2026-09-08) | kept as lore; no tile is counted | | |
| The sibling jungle with no rivers must say why it is not the Greentide | sheet, Owed | lost from this design | A note for another biome's page. | |
| The loud, lawless opposite of its silent neighbour the Webwork | bedazzle review §0 | kept as a line for the campaign | | |
| "Darkness brings roots" as a second, night-time growth engine | sheet §4; cleanse | lost: kept as his image only | Growth in the built engine needs light (the tree-burst rules of 2026-10-17). | A night root engine: a second system. |
| The blower needs fuel and power and its switch, and says which one failed | cleanse | kept | It is *not a tree-clearing weapon, mud drainage device or guarantee against an animal already attacking*. | |
| The blower makes wild animals in its arc shy off for a moment | kit spec M2 | kept as built, not promised | | |
| The clearing warms the air; grazers head for a roof | kit spec M5; cleanse | kept | | |
| A dropped thing sinks after about an hour on mud: *"battlefield drops vanish but hauling is safe"* | kit spec M8 | kept: it is the source for the Empire's gear going under | The first read listed that as new. It is in the kit. | |
| Carried things, corpses and minified furniture never sink; buried time is frozen | cleanse | kept | | |
| Natives are not mired; nothing flying touches the mud | cleanse; kit spec M8 | kept (the flying gate is a known gap) | | |
| The fights happen on the causeways | sheet §8; kit spec M9 | kept | | |
| Steam vents on the banks, as scenery | kit spec, reuse note | kept in "later" | | |
| The Roil hiding the floor as a true height layer | kit spec M4 | lost | *"Deferred, likely never"*; the look and a flat penalty carry it. | |
| Plants cannot block sight in the base game; ours do through a shared grid | understory item; sight item | kept (built) | | |
| What hides a thing is thicket between, never the cell it stands in; shooting is blocked too; witnessing is blocked | sight item | kept, stated in "When the Empire arrives" | | |
| The player's own view and pathing are untouched | sight item | kept | *"A biome the player cannot read is a different failure from a biome that is dangerous."* | |
| A look-at-it save with every plant on one map and a grid key | flora roster §3e; density item | kept as owed work | | |
| The worst day: *"The blower loses fuel while a fever patient collapses and a hauler mires on a neglected shortcut."* | cleanse definition | kept, reshaped: a ship crew's worst day is the same sentence | | |
| The lazy build to refuse: *"an attractive swamp with fast growth, inactive gall defs, suppression counters and a rescue that merely clears Mired"* | cleanse definition | kept | | |
| The cleanse's first call: a home, *superseding "destination, never home"* | cleanse ambiguities 1 | lost (his ship lens of 2026-11-18 is newer) | | |
| Known defects: burial keeps only kind and count; the rescue frees in place; the old biome heat offset is still live; the test site locks clear weather | cleanse tickets; codex notes | kept as build facts for whoever builds | | |

#### Plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Brunnock as the hardwood | flora roster §4a | lost: the first read's row was out of date | After the fellable giant was ruled in, brunnock pays bulk greenwood at the highest hit points; hardwood is the greatbole's alone. | |
| The two giants share bark, never a silhouette; no growth from one to the other is simulated | flora roster §3a0, §3f; tree item | kept | The relationship is fiction, by his accepted cost. | |
| The free mod has the fellable giant and, after the port, the landmark too | port item; flora roster §3a0 | kept (the tier gap is closed in source) | | |
| Mourvel: a room with walls; its leaf cords are cordage | flora roster | kept as a plant | | |
| Kaddrath: the root arcade survives the fall; its gaps are the best hiding place on the map | flora roster | kept | | |
| Sarnstilt: the lungers wait in its shade; salt-cured, it is the good boat wood | flora roster | kept as a plant; boat wood not promised | | |
| Ghemmel's red dye and lacquer; vurmeloth's crimson heart, in small pure stands, carried out at a markup | flora roster | kept as timber and goods | | |
| Mirrelbole: the tree you tap is the one most likely to fall on the tapper | flora roster | kept in "later" with tapping | | |
| Zhorrel's leaves move against the wind; thalquith's hum stopping is the tell; you can see the acid moving in a cundral pod | flora roster | kept as art direction | | |
| Gorbeleth's toxin: the Frenzy dose and the sealant's reagent both come from it | harvest spec §11; cleanse tickets | kept (0.2.0 and later) | *"Going close to something that shoots at you."* | |
| Phorrik gives the stench extract | understory item | kept (0.2.0 with the grenade) | Every tool traces to a named plant. | |
| Brakkel is the foraged food, in place of a berry; four raw foods are built | understory item; tree item | kept | | |
| Tumbel as the waypoint plant; illurin really gives light; wollick's digging slumps the mud | flora roster; understory item | kept | | |
| What each form reads as: *a building that is alive*, *a chandelier*, *eggs at head height*, *a lamp on a post*, *a trap, and it looks like one* | flora roster §3e | kept, quoted as art direction | | |
| Only three plants are not green | flora roster §3e | kept as art direction | | |
| Starting weights for the roster | flora roster §6b | kept as tuning | | |
| The canon trees that inspired rows; the one rejected because *Jedi has no place in a Jawa scavenger jungle* | flora roster appendix A | lost (inspiration notes; nothing ships) | | |
| Other biomes' tree art is not free; four pictures transfer and are under-sized | flora roster §3f, appendix B | kept as an art fact | | |
| Spare cleared names: tarrowan, calloch, bhorrun, vessquith | flora roster §3g | kept as spares | | |
| The giant leaf, ours since before the roster | roster json; flora roster appendix C | kept where the campaign patch puts it | | |
| Twelve retextured Earth plants purged, the donor's cypre tree among them | roster json | lost (purged) | | |
| The fruit's tax works on any eater, wild grazers included | fruit item | kept | *"The ground is carpeted"* means the animals too. | |
| The branch drops at the stump of a felled tree and rots in days: *studied while in the jungle or carried home quickly*; the letter names who studied it | lace item | kept (0.2.0) | Learn-here, use-anywhere; *balanced by cost, not scope*. | |

#### Animals

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The krannock is the canopy swarm he ruled: *"You hear trees falling in the canopy before you ever see what is doing it."* | swarm item; walk | kept, quoted | The first read's row said "the krannock" and no more. | |
| A nest you can find, rob and regret | risk-reward Q3, option C | lost (not chosen 2026-09-25) | | |
| The thurrock: copper-teal, in herds of three to six, never a mount; in season they fight; *"the reason the canopy has holes"* | bedazzle review §3; thurrock item | kept | The rut brawl is dropped if the base game cannot carry it. | |
| "The jungle's crashes stop when a herd stops, which is its own sign." | thurrock item | kept, quoted | | |
| The sulleth: violet with lime bars, *always eating*, tameable | bedazzle review §3; cast item | kept | | |
| The yammeth is *the one that stops*: the flock that falls silent is the tell | bedazzle review §3; cast item | kept | No calls are authored yet; the hush is on the biome's ambience. | |
| The three divide the water: deep reach, open reach, bank. *"No river crossing in the Greentide is free."* | terror design §3; bedazzle review §3 | kept, quoted | | |
| The vurrak's look: a keel *like an overturned hull*, three unequal legs, petrol-violet, chalk-pink teeth | terror design §4 | kept as art direction | | |
| "Terror comes from not being able to trust ordinary scenery, and fairness comes from a tell between the trigger and the bite." | terror design §2 | kept, quoted; his later card chose almost no tell and a pause instead | | |
| The ookala *lets go, trusting the river below* | bedazzle review §1; roster json | kept (branch travel later) | | |
| The zrrik heals itself by what it stabs; it has no roster row here | cleanse tickets | kept (0.2.0), with that caveat | | |
| The canon cast by name (gizka, worrt, clodhopper, whisperbird, fambaa and the rest) | bedazzle review §1; roster json | kept where the campaign patch puts them | *"A busy roster is correct here."* | |
| The gelagrub, *an insect that pays rent* | risk-reward §1d | kept in the campaign cast | | |
| Animals moved out: the fire wasp, the land octopus, the sonar rabbit, the boomcat and ten more | roster json; terror item | lost (evicted or rehomed, each with its reason) | | |
| Butterflies and the wildpawn placed here by his notes; unwired | roster json; donor item | kept as owed wiring | | |
| The river fish from the old scalefish art (scaa lumsigh, vashuu) | roster json | kept | | |
| A net must name the catch item, never the animal | fish item | kept as a build fact | | |
| The free tier owns its whole animal list; the campaign only adds canon | cast item; bedazzle review findings 1 to 4 | kept (done) | His card of 2026-10-02: base fixes and the giant together. | |
| The bedazzle scorecard and its nine marks | bedazzle review §2 | lost | A scoring programme, not design. | |
| Rites considered and not offered (blessing fever survivors, mending what the mud took, anything with fire) | bedazzle review §6 | lost | | |
| The Ceded Room's found site: a grown-through dome and, on the lintel, *we were proud of this* | bedazzle review §6; rite item | kept in "later", quoted | | |

#### Rewards and the living tower

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "You stop surviving the Greentide and start scheduling it." | risk-reward §3 | kept, quoted | | |
| On a dead planet the scarce thing is a living process: biology *used as machinery* | risk-reward §4 | kept as the frame for the later rewards | | |
| No bulk recipe, ever: *"would have quietly turned a pilgrimage into a production line"* | risk-reward §2c | kept as the rule for every later reward | | |
| The reward ranking, and *"R4 is the one to protect"* | risk-reward §4b | lost | Overtaken: he moved that reward to the Contagion and named grenades instead. | |
| Seven defences against the jungle becoming home: *"eats magnificently and cannot build anything"* | risk-reward §4c | kept, quoted | It is the ship lens again: a destination. | |
| Medicines in three grades (used on the spot, sealed for travel, a living culture) | risk-reward R2 | kept in "later" | | |
| Cuisine: three tags per ingredient and a palate that remembers | risk-reward R3 | kept in "later" | | |
| Open cards on cuisine and on how hard the clock bites | risk-reward Q5, Q6 | kept as unasked questions for whoever builds those | Never put to him. | |
| The card on how far regrowth goes | risk-reward Q7 | lost (moot; the reward moved) | | |
| Being findable is the price of being the only supplier | risk-reward R10 | kept in "later" | A known route is a route a raid can use; for this crew, the Empire. | |
| Twelve engine questions the rewards rest on | risk-reward §6 | kept as UNMEASURED | | |
| "Below the line you mine faster than it heals; above it, it heals faster than you mine." | harvest spec §1 | kept in "later", quoted | | |
| The violent healing runs back to whole: *the bole is not lost, it is reclaimed* | harvest spec §2b | kept in "later" | | |
| What the catastrophe leaves: a crater, a field of trunks, a dead husk to build in | harvest spec §2c | kept in "later" | | |
| Fruitfall: *patience or sacrilege* | harvest spec §2d | kept in "later" | | |
| The grub dilemma: *"Take the fruit and you starve them into a manhunter swarm. Leave the fruit and you breed them into an army."* | harvest spec §4b | kept in "later", quoted | | |
| Purple grubs on purple fruit; a slow hauler walking up to the pile *is the ambush* | harvest spec §4c | kept in "later" | | |
| The seed needs water beside it and grows fast; the species becomes a loop the player can run | harvest spec §3c | kept in "later" | | |
| "The finest shelter on Ash'karr is alive and slowly trying to close on you." | harvest spec §7 | kept in "later", quoted | | |
| The chamber's cool fades as the tree is hollowed: *greed costs comfort before it costs lives* | crossovers §3 | kept in "later" | | |
| The Wildsteam's Green Oath: the taboo is *"cutting a living tree"*; they are *"the only faction that plants"* | harvest spec §8 | kept in the campaign layer, stated in "Who else attacks" | A crew that fells a giant in their sight is new ground: asked under NEEDS HIM. | |
| The seed is the atonement: *"one fruit therefore contains both the atrocity and the apology"* | harvest spec §8 | kept in "later" | | |
| Pilgrims come to listen; sealed rooms are forgiven, open wounds are not; *"time launders sin"*; the worst thing is to be *caught mid-harvest* | harvest spec §8a; crossovers §4 | kept in "later" | | |
| A readable line for how hollow the tree is, for a player with the sound off | crossovers §6 | kept in "later" | | |
| The song in bands, with a resolve when the tree heals: *a player who backs off hears forgiveness* | harvest spec §5; crossovers §2 | kept in "later" | | |
| Many plants on this world hum | harvest spec §5 | kept as world lore | | |
| Open draft questions on the tower (where free-mod pilgrims go, how big the pilgrims' rage is, pull or pin, whose servants) | crossovers §8 | kept as questions for the tower's own version | Their later answers are on an item this read did not open. | |
| The wet-heat clothes (a wrap, a sealed suit, a hood) | kit spec M1 | kept, reshaped: ordinary heat clothing, sold at the band's edge | The first read's row said lost with wet-bulb. The heat kind was lost; the clothes answer hot air by ordinary insulation, and the wrap is built. | |

## Sources read, and the count

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**23 source files, 164 rows** (the first read's count; the second reader's count is at the top of this page), of which **17 lost**, **21 record a move** (whole or in part), **9 kept, reshaped**
and 1 folded into shared machinery (recounted after the revision of 2026-11-18, which added six rows and changed
two). Every source is named in at least one row's source column (checked by the same
script; the five cleanse files it read count under the one name "cleanse").

Read whole: the sheet; the cleanse's owner pages; the owner answers. Read in large part: the flora roster (rulings,
the 22 rows, the giant); risk-reward (the audit, the phases, the reward list, the four ruled cards); the bedazzle
review (plain words, mechanics, roster fill, slate, consult, rulings); the terror design; the cleanse definition (its
first two-thirds). Read by heading or by search: the terror consult; crossovers; both kit files; the roster json;
the names doc; the cleanse's next-version list, ambiguities and census; the walk's north star; the mechanics review
(Greentide table); owner cards (card 8); fluff cuts; the experiences table; the growth roster. Not read: the flora
roster's appendices and wiring sections, risk-reward's sections on reward ranking and its open questions five to
seven, the cleanse's tickets, bars, models and review files.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_greentide.md`, `greentide_tree_roster_2026-09-22.md`,
`greentide_risk_reward_2026-09-22.md`, `greentide_bedazzle_review_2026-10-02.md`,
`greentide_terror_replacement_design_2026-10-02.md`, `greentide_terror_replacement_gpt_consult_2026-10-02.md`,
`kits/greentide_kit_spec.md`, `rosters/the_greentide.json`.

Hold these two until the living tower is designed for its later version, because they are its only specification:
`greatbole_atmosphere_crossovers_design_2026-10-02.md` and `kits/greatbole_harvest_spec.md`.

Not for deletion: the freeze rulings; the ledger items; the shared names doc; `design/concepts/Greentide/cleanse/` (superseded by this design, never
applied; it should be re-run from this file, not applied); the validation walk.

Before deleting: `the_greentide.md` is cited by line number in the flora roster and by path in other biomes' sheets
(the Fever Wood's and the Webwork's say "read against" it), and the roster is the art pipeline's silhouette brief.
The roster's rows should move into the design folder or the art ledger first, whichever the art seat reads.
`rosters/the_greentide.json` is the only file that still holds the words of his Greentide sheet of 2026-10-08
(the sytheclaw cut, the gristle and saluksis renames, the ookala's name); they are carried in the second reader's
rows above, with the eviction list.
