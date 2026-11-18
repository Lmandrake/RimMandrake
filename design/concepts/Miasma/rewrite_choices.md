# The Miasma: what the rewrite chose, what it lost, and why

Companion to `design/concepts/Miasma/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* is *"the overriding priority"*. And his later test:
*"you should always look for solutions that make you say Very Jawa."*

Two things shaped this rewrite more than the lens did.

First, **the cleanse proposal of 2026-11-17 was built on a centre he had already refused.** Its signature is
*"recession creating nursery rescues whose treatment determines maternal tolerance and the chance of juvenile
inheritance."* A week earlier, on 2026-11-10, he had written: *"no every map should not have a great mother and
babies everywhere, only sometimes... the colony doesn't HAVE to rescue them, this was supposed to just be an event,
not the center of the whole biome"*, and his answer to what holds the place together was *"Abundance forces
difficult choices: there are competing worthwhile opportunities."* The cleanse softened the mother to "sometimes"
and kept the nursery as the signature anyway. This design takes his answer as the centre: the surge is the event,
and what it leaves (flotsam, dead crops, a moved salt line, sometimes orphans, sometimes a mother) is more than a
small crew can pick up.

Second, **the sheet already put Jawa here.** *"The Jawa — flotsam-combing crews working the root-lines after every
surge; the delta is a harvest that restocks itself."* The flotsam yard is built, and the cleanse switched it off.
It comes back as the reason the ship lands. So does the decay cell, which the cleanse deferred although his own
one-line experience of the biome says *"Rot is power."*

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **She dies of age, and the young inherit her.** *"The succession IS the payoff, and it is what makes the death
   clock bearable."* Ruled by him on 2026-09-23, built, and the fluff-cut review of 2026-10-23 kept it on purpose:
   *"her young succeeding her is that nursery's long game."* A long game is what a ship on the run does not
   play. I moved it from the cleanse's first version to "later". It is the largest loss in this batch.
2. **"Now what when they love you but can only survive in the water?"** His own question. For a colony the answer
   was inheritance. For a ship it has no answer yet, and the unanswered version (something in the channel
   watching the ship lift) may be the best moment the biome has. Asked as `NEEDS HIM`.
3. **Canals that bring her inland.** *"You can build her a road... buy her protection with labour instead of
   location."* His remark started it; it is clever and it is a settler's project. Later.
4. **The grounded mother.** Her dead body as a reef of *"ship-grade hull plate"*, guarded by the young the crew
   inherited: *"scavenger against loyalty."* Not chosen on 2026-10-02. Since then he has ruled that every biome
   wears on the hull and has an answer; this is the only armour answer to brine anywhere. Asked as `NEEDS HIM`.
5. **The last dry deck.** A flotsam crew retreating up the roots to the landed ship as the surge comes in, asking
   passage. Not chosen on 2026-10-02, when it was one ship idea among five. Asked as `NEEDS HIM`.
6. **Fever-forging.** *"Survive and grow stronger — very wild nature."* *"The worst place to get sick is the only
   place getting sick can pay."* It is his, it is partly built, and a fever can run its course inside a stop. I
   put it at 0.2.0, not 0.1.0, because a reward for illness needs its odds proven fair before it ships. If one
   thing moves up, I would move this.
7. **The Working.** *"The diseases ARE the failed experiments — and occasionally not failing."* The idea under
   the whole biome. Kept as the reason for the sickness and quoted; nothing in play shows the muck working toward
   anything.
8. **The Wildsteam pilgrimage.** *"Come here when all hope is lost, and you either die or return with hope
   found."* Campaign layer, untouched, and the best line any faction has about any biome.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **Recurring root-line flotsam after each recession:** next version → 0.1.0. Built. It is the Jawa's stated trade
  in this biome and the reason to land. The one-time seeding of loose goods at map start comes with it, so the
  yard is not empty before the first surge.
- **The found meter and the decay cell:** next version → 0.1.0. Built. *"Rot is power"* is in his experience line;
  his later answer made it *"opportunistic extra power, using waste already on hand"*, which is what a ship has.
- **The mother dying of age, succession, the heir's guard, juvenile inheritance:** first version → later. See
  above.
- **Young that tame themselves, and their guard and attack work:** first version → 0.2.0. A crew can meet it in a
  stop; it is not needed to make the first version's choices.
- **The maternal-tolerance signature as the biome's centre:** first version's signature → one event among several
  in 0.1.0. His answer of 2026-11-10.
- **Fever-forging and the strange boons; attar, its still and the glaze; the spent cell's bed and its
  ingredients; corpse disposal; the creatures' special attacks and habits; custom buyers; fever by swarm contact:**
  next version → 0.2.0.
- **Stayed "later" from the cleanse's "next version":** water-only hauling, host and castings gates, fed-plant
  displays, the Recall rite. Not moves.
- **New in 0.1.0, by his card of 2026-11-18:** brine on the hull with its answers; canopy and haze as one step of
  cover. Both are new, small work.
- **New, not in any source:** triage after a surge as what a stop is made of; the Empire's troopers inside a
  mother's reach; a siege camp in the next surge's path; decay cells as what spares the ship's fuel. All are
  readings of built behaviour and none adds a mechanic. Cleaning salt off a hull by hand is new and is flagged in
  the design.

## Every idea, row by row

Source names: *sheet* = `biomes/the_miasma.md`; *flora roster* = `biomes/miasma_flora_roster_2026-09-23.md`;
*fauna roster* = `biomes/miasma_fauna_roster_2026-09-23.md`; *kit spec* = `biomes/kits/miasma_kit_spec.md`;
*review* = `biomes/miasma_bedazzle_review_2026-10-02.md`; *roster json* = `biomes/rosters/the_miasma.json` (all
under `design/Jawa/worldbuilding/`); *cleanse* = `design/concepts/Miasma/cleanse/`; *owner answers* =
`design/RimMandrake/designer_codex_2026-11-09/Miasma/ANSWERS_OWNER.md`; *walk* =
`design/validation_walks/RimMandrake/Miasma.md`; *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*ladder* = `design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Experience line: "A stinking, beautiful nursery where the sea dumps everything. Rot is power, and every surge brings orphans." | walk, mechanics review | kept, quoted | His card of 2026-10-20. | |
| "Out of darkness, possibility. Out of muck and stink, rebirth... maybe. It's being worked out." | sheet header | kept, quoted | | |
| The name is the Miasma; the place is named for its own breath | sheet header | kept | | |
| Thematic handle: the lifeboat at the drain | sheet header, §2 | kept as lore | | |
| Read against the Slime and the Rot: the same pressure before the breakthrough | sheet header | lost from this design | A comparison among three biomes; one stop shows one. | A line in a world document; free. |
| The gene-reactor reserved to the Slime; no gene machine here | sheet header, ban 1 | kept (dropped list) | | |
| Tile counts, elevation, temperatures, regions | sheet §0 | lost | A tile count is never evidence; the planet is painted at the end. | |
| It has never rained here; no rain | sheet §0, ban 5 | kept, quoted | | |
| Bitterleaf, the Wildsteam's coastal seat | sheet §0, §8 | kept in the campaign layer; named as where fuel might be bought | The fuel ruling of 2026-11-18. | |
| Three donor figures kept and explained (animal density, movement difficulty, disease clock) | sheet §0 | kept as build facts; the explanations quoted | A number is not a bar. | |
| "Bio-engineered viruses" made part of the watershed story; whose is never said | sheet §0, ban 6 | kept (dropped list for authorship) | | |
| "Everything ends up here: the water, the sins it carries, and the life running from the salt" | sheet §1 | kept, quoted | | |
| Density is refugee crowding, not plenty | sheet §2, §5 | kept, quoted | | |
| The drain: the Contagion's mulch, the Greentide's fertility, the war's leftovers | sheet §2 | kept as lore | | |
| The breath-tide: storm-driven, never scheduled | sheet §3, ban 4 | kept, quoted | | |
| The salt line "moves miles per surge"; nothing reaches equilibrium | sheet §3 | kept, quoted | | |
| The gradient as geography; the surge redraws it around what is built | sheet §3, kit spec M1 | kept | | |
| The Working: the planet's compost heap at fever heat | sheet §3 | kept, quoted | See "the ones I would look at". | |
| The trees run the plumbing: drink river and sea, sweat salt | sheet §3 | kept as lore | | |
| "The roots are the only ground" | sheet §5 | kept, quoted | | |
| The place is on the verge of something; it is not ready | sheet §5 | kept as tone | | |
| "The young are everywhere, and the young are hope" | sheet §5 | kept | | |
| Art theme: "Rainbow blooms in green-gold haze — hope, composting"; light, palette, silhouettes, motion, sound | sheet §9 | kept as art direction; the sound line quoted | | |
| A surge announces itself as "a long exhale from seaward" | sheet §9 | kept, quoted | | |
| The plain-words summary written for his card | review §0 | kept; three phrases quoted | | |
| The biome made no sound, did nothing to the ship, and had no god | review §0, §2 | kept as history: the cry is built since; the ship now has brine; no god is added | | |
| The free mod named campaign terrain and carried campaign-prefixed defs | review §1 | kept as history; its fix items are done or owed outside design | | |
| World scoring and a rarity slider | cleanse | lost (recommended for dropping; there is no worldgen) | | |

### The surge, the yard and the power

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The surge as an irregular incident with forced weather | kit spec M2, cleanse | kept | | |
| The surge must actually wet and withdraw from ground | cleanse owner_pages | kept, in the promise table | The cleanse found the built surge only repaints. | |
| The salt-line gauge: ilbareen dies standing where brine reaches | cleanse, fauna roster | kept | It is how a crew reads where to park. | |
| Crops in newly reached brine fail; floors survive | cleanse | kept | | |
| Natural ground repainted under floors and bridges without harming them | cleanse | kept as a build duty | | |
| Stranding pools on recession | sheet §4, kit spec M3 | kept | | |
| "Every surge brings orphans" read as recurring, not every time | cleanse owner_pages | kept | And his "only sometimes". | |
| The flotsam yard: "the planet's driftwood-and-salvage beach" | sheet §7, review | moved (next version → 0.1.0) | See scope moves. | |
| "The Jawa — flotsam-combing crews working the root-lines after every surge" | sheet §8 | kept, quoted; made the crew's reason to land | The lens, written in September. | |
| One-time seeding of loose goods at map start | cleanse | moved (next version → 0.1.0) | So the yard is not empty before the first surge. | Leave it off: the first days have nothing to comb. |
| Brined wreck frames and tanks | cleanse, mechanics review | kept | | |
| The scuttler appraisal: bidding on unopened lots by listening to what feeds in them | review §5 | lost (not chosen 2026-10-02) | | It is the most Jawa idea in the file; a small build on the yard. |
| Decay cells: power from ordinary rot, learned from a dead meter still reading current | review §5, §8 | moved (next version → 0.1.0) | See scope moves. | |
| "Opportunistic extra power, using waste already on hand" | owner answers 3 | kept, quoted | | |
| "Decay cells, but they become a rotting bed that is part of Star Wars Cuisine ingredients" | review §8 (his words) | moved (next version → 0.2.0) | The cell is the stop; the kitchen is company. | |
| A bed that takes corpses and leaves bone and a named skull | mechanics review, cleanse | moved (next version → 0.2.0) | | |
| The haze: permanent, green-gold, no rain, softened light | sheet §1, kit spec M4 | kept; given one step of cover from orbit with the canopy | His card of 2026-11-18. | |
| The mangals' visible thriving in the haze | sheet Owed, kit spec M4 | kept as art direction | | |
| Canals carry water, and brine if dug from the wrong end | fauna roster §6b | kept as merely active shared machinery | | |
| Liquid grades for brackish, brine and muck | sheet Owed | folded into shared machinery (`FlowWorks`) | | |

### The nursery and the mother

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The nursery: the sea's roster breeds here | sheet §4 | kept | | |
| "Don't kill what's small here; its mother is why nobody goes out onto the open water" | sheet §4 | kept, quoted | | |
| "The reason ships sink" | sheet §4 correction | lost (he corrected it: there are no nautical ships in this world) | | |
| The parents' gamble with their young as the biome's soul | sheet §4 | kept as lore | | |
| The warden mothers: brine-broken elders ending their centuries guarding nurseries | sheet §4 | kept | | |
| "A not-so-gentle giant who can be befriended when its young call out for it and get stuck" | fauna roster §6 (his words) | kept, quoted | | |
| She lumbers in water and cannot reach dry land; "A colony can." | sheet §4, fauna roster §6 | kept, quoted | | |
| Befriended, never tamed; tolerance means only leaving her target set | sheet §4 | kept | | |
| Harvesting inside her reach ends tolerance at once | sheet §4, cleanse | kept | | |
| "When it spawns, so do some stranded young (sometimes)" | fauna roster §6 (his words) | kept | | |
| A mother only sometimes; young may come without her | owner answers 1 | kept, quoted | | |
| The mother-centred root | owner answers 1 | lost (he rejected it) | | |
| Rescue is optional: "just an event, not the center of the whole biome" | owner answers 2 | kept, quoted | | |
| Triage: choose the reachable pools; losses despite preparation | owner answers 2 | kept; widened to everything a surge leaves | | |
| The stranded as a condition, not species: gills going leathery, fins into feet | sheet §4, fauna roster §5 | kept, quoted | | |
| "Evolution auditioning... in the pools behind the player's base" | sheet §4 | kept as tone; nothing evolves in play | | |
| The first egg above water: one species makes it onto land in the crew's care | review §5 | lost (not chosen 2026-10-02) | | |
| The young's cry, audible and locatable; she moves toward it | review §1, mechanics review | kept | | |
| A cry that continues while the young is carried | cleanse | kept as owed work | | |
| Carrying a young to water near her earns tolerance | cleanse, mechanics review | kept | | |
| The mother's price: sell one and her nursery never forgives | review §3, §8 | kept | His card. Selling the baby is very Jawa, and the cost is on screen. | |
| Only a completed paid sale is betrayal; holding is not | cleanse owner_pages | kept | | |
| Ordinary traders supply the sale; named buyers are campaign | cleanse, review §8 | kept; custom buyers moved (next version → 0.2.0) | | |
| The nursery trade: eggs and young "priced in the mothers' memory" | sheet §7 | kept (it is the mother's price) | | |
| Her nursery as a placed, mapped, named site | sheet §4, §8 | kept, reshaped: she spawns; names are campaign layer | His amendment of 2026-09-23. | |
| The young are trainable and "frequently self-tame if there are no hostilities against them" | fauna roster §6a (his words) | moved (first version → 0.2.0) | | |
| "They love you but can only survive in the water" | fauna roster §6a (his words) | kept, quoted; `NEEDS HIM` | See above. | |
| She dies of age, foreshadowed from the first day | fauna roster §6a | moved (first version → later) | See above. | Keep it: the first version then needs a campaign's length to show. |
| One of the young takes the nursery; not guaranteed | fauna roster §6a | moved (first version → later) | | |
| Her ageing shown in her art | review §1, cleanse | kept as art | Seeing that she is old costs nothing. | |
| The heir's weaker watch; a never-rescued sibling's weaker still | cleanse owner_pages | moved (first version → later) | | |
| Canals extend her reach; she becomes something the player authors | fauna roster §6b | kept in "later" | See above. | |
| A severed canal traps her visibly | cleanse owner_pages | kept in "later" with canals | | |
| A manhunter wave across the map when a mother dies at her site | cleanse | lost (recommended for dropping; his to confirm) | It punishes a natural death. | |
| The grounded mother | review §3 | lost (not chosen 2026-10-02); `NEEDS HIM` | See above. | |
| The giant lane is hers alone; no second giant | sheet §4 | kept | | |
| Water-only hauling by tame young | cleanse | kept in "later" | | |
| The retraction of an earlier stationary mother | fauna roster §6 | lost (superseded by his ruling) | | |

### Animals, plants, sickness and goods

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The crusty arthropods: eaten by everything, faintly comic | sheet §4 | kept, quoted | | |
| Four scuttler species; the loam producer is one of them | fauna roster §2, rulings | kept | | |
| The composters; delta loam | sheet §4, §7 | kept | | |
| The fever-swarm: the disease vector and the only pollinator | sheet §4, fauna roster §3, fluff cuts | kept as vector; the pollination gate is lost (cut 2026-10-23) | Fluff cuts. | |
| "You cannot have the trees without the fever" | sheet §4 | lost with the gate | | Rebuild the gate: he cut it. |
| Fever passed by the swarm's touch | cleanse | moved (next version → 0.2.0) | | |
| Fever-forged: "survive and grow stronger — very wild nature" | sheet §4b | moved (next version → 0.2.0) | See above. | |
| Five strange boons he selected; the Tide-reader cut | kit spec owner cards | moved (next version → 0.2.0); Tide-reader lost | | |
| All four faces in scope: floor, stranded, composters, economies | fauna roster rulings | kept, by bucket | | |
| "Strangely beautiful but also a little sick looking" | flora roster §0 (his words) | kept, quoted | | |
| "Especially add things inspired by real-world cannibal plants" | flora roster §0 (his words) | kept | | |
| The predators eat scuttlers, never a colonist or a tame animal | flora roster §0, fauna roster | kept | | |
| Two families: honest blooms and honest predators | flora roster §0 | kept | | |
| "Don't be so upset by modifying a frozen document. It's no big deal." | flora roster §0 (his words) | kept, as licence for this whole rewrite | | |
| Six blooms from his six reference images | flora roster §0, §4 | kept as the roster and the art brief | The images were never saved; the words are the brief. | |
| Four mangals that are the terrain; thessamor wood, brelloch salt | flora roster §3, cleanse | kept | | |
| Five predator plants on five real mechanisms | flora roster §5 | kept | | |
| Four muck plants and three economies; immarel's silt; thrannock anchoring flotsam; wessaline's crust that crunches underfoot | flora roster §6 | kept | | |
| The salt gradient, not height, organises the flora | flora roster §1 | kept | | |
| Trees bound to hosts and castings; plants that show when fed | cleanse | kept in "later" | | |
| Star Wars plant injections where they earn a slot | flora roster §7 | kept where the campaign patch puts them | | |
| The legibility matrix for the flora | flora roster §8 | kept as art direction | Not read. | |
| Bozzuga, the ambush frog remade as ours | review §8, cleanse | kept | | |
| Liliana the silk moth; ondrukka the grub | cleanse | kept | | |
| Lastvine rearing and acid spit; duskfire's burning spit; sharpshrimp regeneration; siezer lockjaw; the drake's fermenting | cleanse | moved (next version → 0.2.0); the plain animals stay | Creature moments a crew can meet in a week. | |
| Neighbour animals and the canon cast added by the campaign | cleanse, review | kept where the patch puts them | | |
| The attar: "the planet's loveliest luxury, pressed from its ugliest mud" | sheet §7 | moved (next version → 0.2.0) | His own pick of resource; a still is a week's work. | 0.1.0: one more chain to prove. |
| Attar as a glaze on artwork | sheet §7, cleanse | moved (next version → 0.2.0) | | |
| Attar as a balm that fades scars | sheet §7, cleanse | lost (recommended for dropping; his to confirm) | It changes injuries, against the medicine ban. | Cosmetic only: a different build. |
| No medicine economy; the old medicinal mangrove harvest | sheet ban 3, cleanse | lost (ban; and recommended for dropping) | | |
| The arthropod harvest as a food industry | sheet §7 | kept as plain hunting; the industry is "later" | | |
| Delta loam as an export | sheet §7 | kept as a good; the trade is "later" | | |
| The Wildsteam pilgrimage and shrine-stills | sheet §8 | kept in the campaign layer, quoted | | |
| The Deepwater vigil | sheet §8 | kept in the campaign layer | | |
| The last dry deck | review §5 | lost (not chosen 2026-10-02); `NEEDS HIM` | See above. | |
| The Recall of the Written-Off rite | review §8, mechanics review | kept in "later" | Rites are tabled; it dismantles powered structures, the ship included. | |
| The two rites not chosen (the second-hand young; the mother's blind side) | review §6 | lost (not chosen) | | |
| The scanner's readings | cleanse | kept | | |
| Roster rows and their notes | roster json | kept as build facts | Not read. | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (nursery rescues decide tolerance and inheritance) | cleanse owner_pages | kept, reshaped: one event in 0.1.0, not the centre; inheritance later | His answer of 2026-11-10. | Keep it as the centre: against his words. |
| Its runner-up, rot electricity | cleanse owner_pages | moved (deferred → 0.1.0 for the cell) | | |
| Its fifteen consequential defaults (sea connection, bridges, custody, consent, expiry and the rest) | cleanse owner_pages | kept where the feature is kept | | |
| Its four models and six unsettled meetings | cleanse owner_pages | kept as build-first work | | |
| Its tickets, bars and switch-offs | cleanse | kept as they stand, except where a feature moved | Not read. | |
| The kit spec's six mechanics and build order | kit spec | kept as build history (all six have landed) | Only its opening and owner cards were read. | |
| The nine-mark scorecard | review §2 | lost | A scoring frame from an earlier programme. | |
| Probe sight and the visibility dial | ladder | kept as what haze and roots act on | | |

## Sources read, and the count

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**12 source files, 133 rows**, of which **18 lost** (whole or in part), **18 record a move**, **2 kept,
reshaped** and 1 folded into shared machinery. Every source is named in at least one row's source column
(checked by the same script; the cleanse files count under the one name "cleanse").

Read whole: the sheet (`the_miasma.md`, each line cut at 1,000 characters); the owner answers; the cleanse's owner
pages. Read in part, with what was skipped: **the review** (`miasma_bedazzle_review_2026-10-02.md`, 56 KB: read
§0, "ruled mechanics, built and unbuilt", the giant's two options, the GPT consult table and §8's rulings, each
line cut at 640 characters; not read: the defect findings of §1, the fauna census, the scorecard, the roster fill,
the slate, the two pitched rites, the draft card); **the fauna roster** (`miasma_fauna_roster_2026-09-23.md`: read
the rulings table, his verbatim ruling in §6, the opening of §6a and of §6b, and lines found by search; not read:
§1 to §5 in detail, the rest of §6, §7, §8); **the flora roster** (`miasma_flora_roster_2026-09-23.md`: read §0
with the six references and the headings; not read: the plant rows of §3 to §6, §7 to §10); **the kit spec**
(`kits/miasma_kit_spec.md`: read the opening and the first owner card; not read: M1 to M6, the ledgers, the build
order, the other owner cards); **the cleanse census** (every row's name, built and fate); **the mechanics review**
(the Miasma table, rows cut at 230 characters); the walk (north star only); fluff cuts by search; the ladder
(sections 1 to 4). **Not read at all:** `rosters/the_miasma.json`; the cleanse's `definition.md`,
`next_version.md`, `ambiguities.md`, `tickets.md`, `bars.json`, `models.md`, `review.json`, `converge.json`; the
Designer record and notes in `design/RimMandrake/designer_codex_2026-11-09/Miasma/` other than the owner answers.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_miasma.md`, `miasma_bedazzle_review_2026-10-02.md`,
`kits/miasma_kit_spec.md` (its six mechanics have landed).

Hold these: `miasma_flora_roster_2026-09-23.md`, because its six reference descriptions are the only art brief
for the blooms (the images were never saved); `miasma_fauna_roster_2026-09-23.md`, because its §6, §6a and §6b are
the only full statement of the mother, the succession and the canals, most of which this design leaves in "later"
and this pass read only in part.

Not for deletion: `rosters/the_miasma.json` (not read); `design/concepts/Miasma/cleanse/` (superseded by this
design, never applied; it should be re-run from this file, not applied, and its signature should not be reused);
the validation walk.

Before deleting: `the_miasma.md` is the frozen sheet the Slime's and the Rot's sheets are read against, and the
Grey Sea's design depends on its nursery pairing (the young here, the adults in the terminator waters).
