# The Miasma: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A second reader, who did not write the design or this page, read the Miasma's sheet, review, both rosters, kit
spec and roster file to their ends, the cleanse's prose files, the Codex dry run, his ship-gift register, his
shield rulings and the built shield code, the biome's own definition and its ledger items, and checked the
design against them (item `RIMMANDRAKE_RECHECK_LANTERNDEEPS_TO_RUSTCATHEDRAL_CHOICES`).

**Rows added: 209**, in the section "Added by the second reader" below. The page now has 342 rows. Eight of the
first read's rows were wrong, stale or marked "not read" and are corrected in place; each says so.

**The three most valuable things the first read missed**

1. **His own shield rulings already answer what this biome does to a ship, and the first read invented an answer
   instead.** On 2026-09-02 he wrote that the particulate screen handles *"vapor, bio contamination, spores"* and
   *"repels small animals"*: that is the Miasma's haze, and a screened ship here stands in a ring of mud with no
   scuttlers on it. He also wrote that *"nothing 'holds out water'"*, so no shield answers the surge. The built
   code sees heat, cold and particulates; it does not see the haze (one flag short), and it does already wear an
   unveiled ship on this biome's hottest days. Where the first read said the surge was *"the sources' own
   statement"* of hull wear, the October review says in plain words that the biome *"does nothing to your ship."*
   Brine on the hull is now flagged as this rewrite's proposal.
2. **Three things he said that the design needed and did not have.** *"The game isn't that long to watch it
   grow"* (2026-09-23, cutting the young that grows into a leviathan): the ship lens in one sentence, said about
   this biome two months early. The roster's reading of his *"when it spawns, so do some stranded young
   (sometimes)"*: *"the offer arrives with her"*, so a stop too short to see a surge still gets the choice. And
   the register he started on 2026-09-24 (*"how can this biome uniquely add something to the ship?"*), on which
   the Miasma's gift is the decay cell.
3. **"Built" was hiding four gaps that change promises.** The decay cell takes raw food, not rot. The warden
   mother is not held to water on every step (the one constraint the whole friendship stands on). The fever swarm
   causes no fever. The living canopy does not sort along the salt line. And the cast on disk is not the September
   cast: his sheet sitting of 2026-10-08, recorded only in the roster file the first read did not open, renamed
   nine creatures (lastvine, sharpshrimp, siezer, duskfire, fermatalis, hell's lantern, liliana, ondrukka,
   gillclamper), each with a description worth quoting.

Also found: the parking trade (the kit sorts the air's load along the line, worst in the middle, and exposure
clears under a roof, which a ship is); that her protection is a place (*"a colony with its back to open water is
nearly unraidable from that side"*); the declined salt gates; the flotsam yard's plant and its best line; the
braskeen wave; the named buyers (the vigil *"for the sea"*, margin traders *"for the pens"*); his typed sentence
about corpses, skulls and bones; that Bitterleaf is a roadless island; the cleanse's 30-to-60-day target for her
death, which a long stop reaches; and a second brine-proof thing in the sources (ommolyn cordage).

**What the second reader changed in the design, and why**

- *Hull wear rewritten* on his rulings and the built frame, in three numbered parts by how well each is sourced.
  The two promises that depend on his answer are marked so in the promise table.
- *The decay cell* is named as the register's ship gift, and described as built wherever the design had it
  eating waste.
- *The first minutes and first day* gained the two gauge trees, the three-way parking trade, the thrannock, the
  aphreen, the roof, and the first-day offer.
- *The first week* gained the surge's warning, the karrimeth mass, the bozzuga eating orphans, her age said
  outright, the as-built note on her water lock, and where to park for her protection.
- *Moments:* the braskeen wave, the mass, and (conditional on his answer) the clean ring round a screened hull;
  the swarm and the compost scenes say what is built. The 0.2.0 list uses his creature names and lines.
- *Scope:* as-built notes on four lines; the dropped list gained the leviathan (his cut), salt gates (his
  decline), the taming grind, and his words on the Tide-reader; the site-memory line cites his card.
- *`NEEDS HIM` grew from three to eight,* each tagged with a theme.

**What the second reader could not settle.** Whether he ever answered the card that showed him the ship gifts.
What the other three of the "five proposals" of 2026-09-23 were (not on disk). Whether a Miasma map's outdoor
temperature really reaches the frame's 58 C (the sheet says the tiles run to 59; no map was read). Whether the
built weather lock ever clears. Whether any brine-proof cordage is built.

**Ship ideas he declined or cut (not revived; both listed under `NEEDS HIM`):** the grounded mother's hull plate
and the last dry deck, both not chosen by card on 2026-10-02. The Recall rite, which he did choose that day,
dismantles the ship; rites were tabled the next day and are second-version.

**Measured (by script, after writing):** 342 rows, of which 209 added by the second reader; 38 lost (whole or in
part, counted where the outcome begins "lost"), 19 record a move, 2 reshaped, 2 folded into shared machinery; 21
named sources, every one in some row's source column; an invented source name is reported missing (the check can
see absence); 44 source files read to the end. Record:
`design/RimMandrake/biome_recheck_lanterndeeps_to_rustcathedral_row_check_2026-11-18.txt`.

**Read to the end by the second reader:** the sheet; the review of 2026-10-02; the fauna and flora rosters of
2026-09-23; the kit spec; `rosters/the_miasma.json`; the cleanse's owner pages, definition, next version,
ambiguities, models, tickets and its three small records; the Codex dry run's owner answers, owner questions,
brief, notes and question bank; the walk; the ship register; 21 Miasma ledger items; `ShieldHazardUtility.cs`.
**Read in part, with what was skipped:** the cleanse's `census.json` (every row's description, state, fate and
reason; not the evidence and caller fields), `bars.json` (every bar's statement, every check and rule; not the
pictures under each bar), `review.json` and `converge.json` (refusal heads only); the Codex `record.json` (its
outline; its inventory is the census's parent); `MIASMA_MECHANICS_1` (87 KB of build log: its head, and every line
naming the owner, a ruling, a waiver or the ship); six mid-size closed items and the four warden-mother items (the
same search); the mechanics review (the Miasma table, whole); the fluff-cut digest (the Miasma entries); the shield
design (his rulings table and the particulate section); `ShieldHazardExposureTracker.cs` (its header); the biome
definition (header, extensions, diseases, weather; the animal and plant lists from the roster file and census);
the freeze rulings, the campaign arc and the Grey Deep sheet (their Miasma lines). A search of the cleanse's three
large records for a ship, hull, Empire or landing line returned only the gravship-foundation rule (the same
search returns lines in the review, so it can see one). **Not read:** the pipeline's judge prompts and art queues
that mention the Miasma in passing; `design/Jawa/worldbuilding/review/` registers.

`DELETE-READY: yes` for `the_miasma.md`, `miasma_bedazzle_review_2026-10-02.md`, `kits/miasma_kit_spec.md` and
`miasma_fauna_roster_2026-09-23.md` (all four read to the end, every idea rowed, their best lines carried into the
design or quoted here). Two files stay, for reasons that are not about reading: `miasma_flora_roster_2026-09-23.md`
is held as the only art brief for nineteen plants (his six reference images were never saved; its descriptions and
its legibility matrix are what art is graded against), and `rosters/the_miasma.json` is the only record of his
sheet sitting of 2026-10-08 and of thirty-eight evictions.

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
| Decay cells: power from ordinary rot, learned from a dead meter still reading current | review §5, §8 | moved (next version → 0.1.0) | See scope moves. *Second reader:* as built the cell takes raw food, not rot; and it is the Miasma's row on his ship-gift register. | |
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
| A manhunter wave across the map when a mother dies at her site | cleanse, kit spec M6 | lost (recommended for dropping; his to confirm) | It punishes a natural death. *Second reader:* this is the kit's despoiled-site memory, built, and his card of 2026-09-12 ruled its scope ("marked sites only"); see the added rows. | |
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
| The fever-swarm: the disease vector and the only pollinator | sheet §4, fauna roster §3, fluff cuts | kept as an animal; the pollination gate is lost | Fluff cuts. *Second reader, corrected:* the gate was removed by a delegated decision under his veto card (digest of 2026-10-23, removal 2026-11-02), not by his words; and as built the swarm is not the vector either (the fevers come from the biome's own clock). | |
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
| The legibility matrix for the flora | flora roster §8 | kept as art direction | Read by the second reader; its best phrases are in the added rows. | |
| Bozzuga, the ambush frog remade as ours | review §8, cleanse | kept | | |
| Liliana the silk moth; ondrukka the grub | cleanse | kept | | |
| Lastvine rearing and acid spit; duskfire's burning spit; sharpshrimp regeneration; siezer lockjaw; the fermatalis (the decay drake, renamed by him 2026-10-08) fermenting | cleanse, roster json | moved (next version → 0.2.0); the plain animals stay | Creature moments a crew can meet in a week. | |
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
| Roster rows and their notes | roster json | kept as build facts | Read by the second reader: it holds his sheet sitting of 2026-10-08 (nine renames and cuts), which no other file has; see the added rows. | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (nursery rescues decide tolerance and inheritance) | cleanse owner_pages | kept, reshaped: one event in 0.1.0, not the centre; inheritance later | His answer of 2026-11-10. | Keep it as the centre: against his words. |
| Its runner-up, rot electricity | cleanse owner_pages | moved (deferred → 0.1.0 for the cell) | | |
| Its fifteen consequential defaults (sea connection, bridges, custody, consent, expiry and the rest) | cleanse owner_pages | kept where the feature is kept | | |
| Its four models and six unsettled meetings | cleanse owner_pages | kept as build-first work | | |
| Its tickets, bars and switch-offs | cleanse | kept as they stand, except where a feature moved | Tickets read by the second reader; the bars' statements, checks and rules read, their pictures not. | |
| The kit spec's six mechanics and build order | kit spec | kept as build history (all six have landed) | Read to its end by the second reader; M1's disease sorting, M4's roof and M6's site memory are in the added rows. | |
| The nine-mark scorecard | review §2 | lost | A scoring frame from an earlier programme. | |
| Probe sight and the visibility dial | ladder | kept as what haze and roots act on | | |

### Added by the second reader, 2026-11-18

More source names: *ship register* = `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`; *shield rulings* = the owner's sitting saved 2026-09-02, quoted in `design/Jawa/proposals/ship_shields_deep_design.md`; *shield frame* = `src/RimUtinni/ShipShields/Source/` (`ShieldHazardUtility.cs`, `ShieldHazardExposureTracker.cs`); *biome def* = `src/RimMandrake/Miasma/Defs/BiomeDefs/RM_Miasma.xml` and the two weather definitions beside it; *items* = the Miasma's and the warden mother's ledger items under `infrastructure/state/items/` and `items/closed/`; *sitting notes* = the ledger notes on `MIASMA_SCORING_SITTING_1` and `WARDEN_MOTHER_BEFRIENDING_1`; *Codex notes* = `NOTES.md`, `QUESTIONS.md` and `QUESTIONS_OWNER.md` in `design/RimMandrake/designer_codex_2026-11-09/Miasma/`; *freeze rulings* = `design/Jawa/worldbuilding/biomes/_freeze_rulings_2026-09-07.md`; *census* = `design/concepts/Miasma/cleanse/census.json`.

**The ship, the hull and the clock**

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| His question to every biome, 2026-09-24: "how can this biome uniquely add something to the ship?... What can they take and improve their ships environment with?" | ship register | kept, quoted in the design (carried in by the second reader) | The first read never opened the register. It is the lens, in his words, seven weeks early. | |
| The Miasma's ship gift on that register: the decay cell, "power from rot, in a bed of delta loam, silt and salt", checked by script to stand on a gravship deck | ship register | kept; the design now names the cell as the ship's gift and says the pick is an agent's (delegated, carded to him, answer not found) | The first read had it only as knowledge carried away. | |
| "Landing in a biome changes your ship, not just your stores — the gravship becomes a scrapbook of everywhere it has been" | ship register | kept, quoted | The register's own test for every gift. | |
| The particulate screen: "Light kinetic deflectors handle wind, ash, vapor, bio contamination, spores, smoke, sand, and rain damage completely as well as repels small animals." | shield rulings | kept, quoted; the haze is vapor and bio contamination, so the answer to the air is a screen he already ruled. `NEEDS HIM` (hull) | The first read invented cleaning salt by hand and missed that his own screen ruling names this biome's air. | Leave the haze off the frame: the Miasma then does nothing to a ship from the air, as the review said in October. |
| A screened hull "repels small animals": in a biome whose floor is scuttlers and whose plague is a swarm | shield rulings | kept, as a consequence the design states | A screened ship stands in a ring of clean mud. It is also on screen. | |
| "Slow pressing things move through all shields... This is why nothing 'holds out water,' it just doesn't work that way." | shield rulings | kept, quoted; no shield answers the surge | His words settle what the first read left open: brine at the footing has no shield answer, only position, armour or hands. | |
| "The environment is hostile and immediately goes to work on the ship... Its hull is thick and can take a lot of damage in most situations, so no environment is immediately lethal." | shield rulings | kept, quoted | The frame's ruling: advice and wear, never a refusal to land. | |
| The built frame sees three hazards on a map: outdoor heat at or above 58 C or a heat wave, deep cold, and particulates (pollution, or a weather with a sand rate) | shield frame | kept as the frame the design cites; nothing new is designed | The rule for every biome run. | |
| An unshielded hull in a hazard takes deterioration on things near the ship, and the rate doubles after a long unshielded stretch; a second, harsher letter fires then | shield frame | kept as built fact | It is how any Miasma wear would arrive. | |
| Neither Miasma weather carries a sand rate, and the haze is not pollution: as built the frame does not see this biome's air | biome def, shield frame | kept, stated in the design as the gap | Read from the two weather definitions, not seen live. | One flag on the haze weather would do it; a sand rate would not (it breaks the no-rain ban's linter and draws sand). |
| The sheet's temperatures run to 59 C: on the hottest ground, or in a heat wave, the built frame already wears an unveiled ship here | sheet §0, shield frame | kept, in the design as the one wear that needs no new work, tagged a guess (no map temperature was read) | Sourced and built, where brine is neither. | |
| The October review's plain statement: the biome "does nothing to your ship" | review §0, §2 | kept as history; the design no longer says the surge is "the sources' own statement" of hull wear | The first read overstated it. One unchosen pitch implies brine harms plate; no source says a hull wears here. Brine on the hull is this rewrite's proposal and is flagged so. | |
| The floor-safe repaint leaves bare gravship foundations alone when brine repaints the ground | cleanse (rules), items | kept as built fact | A surge salts the mud around the ship, not the deck. | |
| The Recall rite's reclaimers "dismantle powered structures (the gravship included) until the colony drives them off" | items, review §5 | kept in "later" with the rite, the ship clause now stated | It is the one Miasma idea that attacks the ship directly; rites are tabled (2026-10-03) and second-version. | |
| "He has rejected 'ship-centric gimmicks with no biome voice'" | review §5 | kept, quoted beside the last dry deck | His standing objection to ship ideas; any revived one has to pass it. | |
| The last dry deck's cost and refusal: "taking them costs deck space or freight as the approach floods; refusing leaves them visibly trying worse" | review §5 | lost with the pitch (not chosen by card 2026-10-02); stays a `NEEDS HIM` | The first read had the pitch, not its price. | |
| Odyssey's carried occupants as the machinery for passengers | review §4 | lost with the last dry deck | | |
| A stop's outer edge (about six weeks) against the cleanse's target for the mother's death (30 to 60 days after meeting an already-old mother) | cleanse (ambiguities, models) | kept; the design's "later" bucket now says a long stop could see her die. `NEEDS HIM` (scope) | The first read moved her death to "later" as a long game. On the cleanse's own number it fits inside a long stay. The number is a Designer default, unbuilt. | |
| Haze cuts shooting accuracy a little; surge weather more, and slows walking | biome def, kit spec M4 | kept as a build fact under "When the Empire arrives" | It applies to both sides. | |
| The surge's warning lets nearby workers be recalled; a badly sited farm cannot be saved | cleanse (definition), Codex notes | kept, in the first week | For a ship: the crew gets back aboard; the footing was chosen at landing. | |

**The surge, the pools and the yard**

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The physics itself is 'being worked out.'" | sheet §3 | kept as lore | | |
| "The 15-day clock and the hope are the same process." | sheet §3 | kept, quoted | A dropped line; it is the fever in one sentence. | |
| The recede never quite returns to the old line, "so no two maps age alike" | kit spec M2, biome def | kept as build fact | | |
| The salt line drawn as a fleck line on the ground while a surge runs | kit spec M2, census | kept (built: "sparse pale flecks mark the moving salt line") | The player watches it move. | |
| Storm wind multiplies the chance of a surge; no period field may exist on the definition | kit spec M2, biome def | kept as build fact | The no-clockwork ban, made checkable. | |
| Pools roll empty, one or two young, or "something bigger"; they dry in days | kit spec M3, biome def | kept as build fact | A number is not a bar. | |
| The next surge erases the ledger: re-covered pools deregister and their occupants rejoin the wild | kit spec M3 | kept | | |
| A young in a shrinking pool heads for the channel on its own when it can | kit spec M3, census | kept (built for the undeformed; the deformed cannot) | It is why only some need carrying. | |
| The tell of a stranded animal: "an animal trying to reach water it can no longer use" | fauna roster §5 | kept as a readable sign | | |
| A stranded animal "occasionally survives into something that works" | fauna roster §5 | lost (never built; the forging comp was not put on animals) | | A small build on a built comp. |
| "The population differs every game": the stranded as content the surge generates | fauna roster §5, §8 | kept as the reason for his ruling | | |
| Unfloored crops in the band die: "Physics, not mercy — floors/bridges are the engineering answer" (his card, 2026-09-12) | kit spec owner cards | kept, the card now cited | The first read had the consequence without his card. The census could not find it in source (unknown). | |
| Disease and exposure load sorts along the line: worst mid-gradient, where "the Working ferments hardest where everything settles" | kit spec M1, census | kept, carried into the design as the parking trade (the brine end has the cleaner air and the salt) | Built in part: the exposure carrier reads salinity. It makes where the ship lands a three-way choice. | |
| Haze exposure builds outdoors and recovers under a roof | cleanse (definition), kit spec M4, census | kept; the design now says the ship is the roof | Built. The first read's "the air is a wager" had no answer in it. | |
| Exposure is deliberately not wired to disease chance (two systems would double-charge) | kit spec M4 | kept as build fact | | |
| "Its absence is the strange day": rare clear spells | kit spec M4 | kept as lore; whether the built lock ever clears is `UNMEASURED` | The definition lists clear weather but the lock forces the haze. | |
| The mangals grow faster while the haze runs; a clear spell "visibly stalls the green" | kit spec M4, census | kept as art and build fact | | |
| Light softened to 0.85 through the haze, "seen through breath", "not the Lantern's dark" | kit spec M4, biome def | kept as build fact; it is why cover here is one step and never a pause | Agrees with the design's "a dim place, not a dark one". | |
| "The war's leavings" as the only allowed name for the plagues' origin | kit spec ban table | kept (dropped list already bars authorship) | | |
| The flotsam yard is a plant: thrannock, "a net someone left", hung with "rags, shell, splintered wood, salt-bleached plastic" | flora roster §6, §8 | kept, carried into the first day | The first read had the yard without its object. | |
| "A freshly loaded thrannock means the water came up recently" | flora roster §6 | kept, quoted | It makes the surge legible to a crew that slept through it. | |
| The flotsam table: scrap, wood, cloth, the odd component; restock has a cap | items (flotsam yard), census | kept as build fact | | |
| Near root-lines hold a little wood and cloth; farther out are metal, a brined wreck and a crying young: "why go back into the roots" | Codex notes (question 06) | kept as the shape of a salvage trip; the question was never served to him | It is triage drawn as a map. | |
| "Add no auction, appraisal minigame or new quest from the old unchosen pitches" | Codex notes (question 06) | kept (dropped list) | | |
| The scuttler appraisal's two sounds: chatter means rotting goods, taps on broad surfaces mean metal | review §5 | lost with the pitch (not chosen 2026-10-02) | The first read had the pitch without the one detail that makes it work. | |
| The wreck field and its brined frames are their own definitions (`RM_MiasmaWreckField`) | mechanics review M15 | kept | | |
| Flotsam is "the line's literal words" (the sea dumps everything): keep | mechanics review M10 | kept; supports the first read's move of the yard into 0.1.0 | An agent's opinion of 2026-10-22, against the cleanse's switch-off. | |
| His card of 2026-11-17 ("Land, life, one signature") against the first read's 0.1.0, which holds the surge, the yard, the orphans, the mother and the cell | cleanse (definition), owner answers | kept as the open question it is. `NEEDS HIM` (scope) | The first read moved two built features in on the lens and on his "Rot is power". The cleanse read the same card the other way. | |

**The mother, the young and the nursery**

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The sea's memory dying in its lifeboat" | sheet §4 | kept, quoted in the design (carried in) | The best line about her, dropped by the first read. | |
| "You can." "One sentence of fiction sitting on one hard movement constraint" | fauna roster §6 | kept | | |
| "The offer arrives with her": she sometimes spawns with a stranded young, so the choice exists on the first day and does not wait on a storm | fauna roster §6, cleanse (fixes R1) | kept, carried into the first day | For a ship this is the most important sentence in the roster: a short stop cannot wait for an unscheduled surge. | |
| Her protection is geographic: "A colony with its back to open water is nearly unraidable from that side. A colony four tiles inland gets nothing." | fauna roster §6 | kept, carried in as where the ship parks | It turns "the water is not theirs" into a landing decision. | |
| Rescue by engineering: cut a channel so the water reaches the young, "the gentler of the two rescue routes, and the more expensive" | fauna roster §6b, cleanse (definition) | kept as merely active shared machinery (`FlowWorks`) | A crew with days can dig a short ditch. | |
| She is never commanded, "fed on demand, moved, bonded, hauled, healed, ridden, or safely crowded" | fauna roster §6 | kept | | |
| The wardens' life cycle: born in these nurseries, adults in the Grey Sea, elders come back to die as warden mothers | freeze rulings, roster json | kept as lore | It is why she is old. | |
| The crusted giant of the Grey Deep "bred at the Miasma's crèches, returned here for its solitary centuries" | items (nursery kinds) | kept in the sea's design, where it lives | | |
| Juvenile-only wild spawns (his rulings of 2026-09-10); "On-map aging into adulthood is ACCEPTED fiction (the one that stayed too long)" | items (nursery kinds) | kept | | |
| The retier of eleven invented sea beasts to the free tier, so the free mod has a nursery (his card, 2026-09-23) | fauna roster §4, items (sea beasts tier) | kept as build history (done) | | |
| "The top mod without star wars will look precisely the same as the star wars enhanced one save for any star wars beasts we populate it with." (2026-09-22) | fauna roster §4 | kept, as the rule the free nursery answers | | |
| The free nursery: rust nipper, gillclamper, crimson opee, thornback colo, shale gorger and reefback young | review §3, biome def | kept | | |
| The gillclamper: his rename of the silt lamprey's young (2026-10-08), which "latches on, clamps tight, and lets its host do the travelling" | roster json | kept, named in the design | The first read used no creature names from his October sheet. | |
| Reefback young are nursery prey; "killing a calf does not acquire a new remote retaliation mechanism" | fauna roster §4 (2026-11-11) | kept | Agrees with his card: open-water hunting is not remembered. | |
| Despoiling is remembered at marked sites only: "Open-water juvenile hunting is not remembered; the fear stays player-learned, not a mechanical fence." (his card, 2026-09-12) | kit spec owner cards | kept, quoted | It is the rule behind "the small are cheap". | |
| The despoiled-site memory: killing a warden or clearing a crèche raises wild aggression across the map for days, "a factor, not an event" | kit spec M6, census | kept as "recommended for dropping, not yet his", with his card of 2026-09-12 now beside it | The first read's row called it a cleanse idea. It is built, and his card ruled its scope. The cleanse's objection (it fires on her natural death) is fair. | Drop it: against a card of his, so it is his to confirm. |
| "Harming a crèche is not sacrilege in the oasis sense, but everything living remembers it" | sheet §8 | kept, quoted | | |
| A young's nursery is fixed at spawn; the wrong mother refuses; two nurseries on one map keep separate records | cleanse (ambiguities) | kept as owed work (as built the nearest mother takes the credit) | | |
| The worst day: "The colony sells a young from one nursery and returns another from a different site" | cleanse (definition, stories) | kept as a scene | | |
| Accidental harm by a crew member or a turret counts against the nursery; wildlife and disease do not | cleanse (definition) | kept where the feature is kept | | |
| The named buyers: the Deepwater vigil "for the sea", margin traders "for the pens" | review §3, items (mother's price) | kept in the campaign layer, named in the design | The first read said "named buyers" without naming them. A vigil that buys orphans back for the sea is a different sale from a pen. | |
| Sell one and "the succession never comes"; her ledger shows in the inspect pane | review §3 | kept | | |
| "The clearest decision in the biome" (the mother's price) | mechanics review M4, fluff cuts | kept, quoted | | |
| Succession kept on purpose: cutting it "would hollow" the mother's price | fluff cuts | kept as the reason "later" is a bucket and not a cut | | |
| OWNER CUT, 2026-09-23: the "raise it into a leviathan" arc. "The game isn't that long to watch it grow." | fauna roster §6a | kept, in the dropped list with his words (carried in) | The first read missed a cut of his that is the ship lens in miniature. | |
| No maturation, no "it leaves for the sea", no later meeting with the grown adult | fauna roster §6a | kept (dropped list) | | |
| The successor is a child: "a juvenile that loves you and is nowhere near her size"; "the gift is continuity, not a replacement" | fauna roster §6a | kept in "later", quoted | | |
| Succession must not be guaranteed: rescue nothing and "the crèche is just a place, and the scavengers come" | fauna roster §6a | kept in "later" | | |
| A never-rescued sibling can inherit on the colony's rescue record at that nursery | cleanse (ambiguities) | kept in "later" | | |
| "Animals in this project are not conquered, they agree" (three sittings converged on consent) | fauna roster §6a | kept, quoted; a conventional taming grind here is barred | A house pattern worth carrying to every biome design. | |
| Self-taming is barred or reset "the moment you harvest, kill, or butcher one" | fauna roster §6a | kept with the self-taming young (0.2.0) | | |
| The ache: a tame young "stops at the waterline and watches you walk inland. It is there when you come back." | fauna roster §6a | kept, quoted in the design's `NEEDS HIM` on a young coming aboard | The first read asked the question without the roster's answer. | |
| "Do not solve it. No land-walking upgrade, no tank, no carrying it around." | fauna roster §6a, cleanse (ambiguities) | kept: the design's default (they stay) now cites it, and the other option says plainly that it breaks this line | The line is an agent's, written under his ruling; the cleanse kept it ("no carry-home upgrade"). | |
| Water-scoped work: guard the channel; haul from the water only; release and attack in water; never rescue or general haul | fauna roster §6a | kept (guard and attack with the young in 0.2.0; hauling later) | | |
| A trained young working the root-lines is "the single best fit between a creature and an existing economy in this biome" | fauna roster §6a | kept in "later" with water-only hauling (unbuilt) | For a salvage crew it is the most Jawa use of an orphan. | 0.2.0: a new job to build. |
| Foreshadowing is a requirement: an inspect line that "says it outright", she slows as she ages, "and somebody tells you" (the vigil; a pilgrim "would say it differently") | fauna roster §6b | kept; the inspect line and the elder art are 0.1.0, the tellers are campaign | "A player who is surprised by her death means this was built wrong." | |
| Built: an elder life stage and aged art; no death date, no slowing | census, Codex notes | kept as build fact | | |
| The dark use of canals: "you have weaponised a tolerant giant without ever commanding her... it should feel like using a friend" | fauna roster §6b | kept in "later" with canals | | |
| Strand her in a pond: "The mother suffers her children's fate, by your doing" | fauna roster §6b | kept in "later" (the first read had the trapped state, not the line) | | |
| "A canal is water, never a bridge." A canal adds no reach beyond her anchor | fauna roster §6b, cleanse (definition) | kept in "later" | | |
| His swim rule, 2026-09-23: "FlowWorks. Yes, it needs to allow the critter to swim for sure as long as it connects to the sea" | fauna roster §6b | kept, quoted | The first read had canals without his rule. | |
| Connection means the seaward edge, not any map edge; a river mouth is not the sea | fauna roster §6b, cleanse (ambiguities) | kept as owed work | | |
| As built she is not held to water: destinations are checked and a recovery walk brings her back | census, Codex notes | kept, stated in the design's scope line | The first read marked the mother "(built)". The one thing that makes her tragic is not enforced. | |
| As built the heir is a saved name and a message; no guard duty transfers | census, Codex notes | kept in "later" as owed work | | |
| DECLINED, 2026-09-23: salt gates and contested brine. Of five proposals he chose the warden mother "only, all the way"; "That is not licence to build salt gates" | fauna roster §6b, items (befriending) | lost (declined by him); in the dropped list | Not a ship idea. The other three proposals are not on disk. | |
| The retraction: two documents said she shipped when only a comment named her | fauna roster §6, items | kept as history | | |
| The duty trap (a plain animal ignores its guard duty) and its fix | fauna roster §6, sitting notes | kept as build history (fixed at the build) | | |
| The sando aqua monster adult, "bottom-walker adult — the submerged herds": held, "Ask the owner before building it" | roster json, review §1, items (round-2 imports) | kept as held; `NEEDS HIM` (other) | It breaks "no second giant" and "only the young side". Nobody asked him. | |
| The evicted overgrown colossus: "a random giant dilutes them" | roster json | kept (no second giant) | | |

**Animals**

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Four scuttlers because one silhouette cannot do four jobs; each shape follows its job: "a disc, a digger, a mass, and a single big one" | fauna roster §2 | kept | | |
| The karravel: in numbers "the ground appears to be *sliding*" | fauna roster §2 | kept, quoted in the first minutes (carried in) | It is what "the floor moves" looks like. | |
| The karrimeth: only ever a clicking carpet, thousands strong; a mass crossing a camp "strips forage and fills the traps"; "the surge's aftermath made visible" | fauna roster §2 | kept, carried in as a moment after a surge | A nuisance event a week can hold. | |
| The karrolun: hand-sized, iridescent blue-green that "fades to chalk when it dies", "the only one worth picking up individually" | fauna roster §2 | kept | It gives the harvest a target and leaves the rest ambient. | |
| The karrobel: mostly seen half-buried in "a churned ring of castings"; pallasheen is "this animal's visible receipt" | fauna roster §2, flora roster §6 | kept (the castings-only germination is "later") | | |
| One population, four draws on it (the shared vermin pool) | fauna roster §2 | folded into shared machinery (`CreatureBehaviors`) | | |
| The fever swarm seen close: a gold-dusted haze, "the green-gold breath the biome is named for, seen close up" | fauna roster §3 | kept, quoted | | |
| "A player who fumigates their holding gets a clean colony and a dying canopy" | fauna roster §3 | lost with the pollination gate | The gate was removed by a delegated decision (digest of 2026-10-23, removal 2026-11-02), under his veto card, not by his words. | Rebuild it: it was cut as "invisible to the player". |
| Never a second pollinator; the swarm "must not become a mere pest" | fauna roster §3, §7 | lost with the gate | With no gate the swarm is, mechanically, a pest. | |
| "Half a bargain": the swarm carries no disease; the fevers come from the biome's own clock, so killing it cleans nothing | review §1, census | kept as a build fact the design now states; contact transmission stays 0.2.0, unbuilt | The design's swarm moment (a cloud, then a sick Jawa) is not caused by the swarm as built. Flagged in the design. | |
| His sheet sitting of 2026-10-08: nine creatures renamed, re-tiered or cut, each with a new description | roster json | kept; the names are now used in the design (the first read had four of them from the cleanse and not the sitting) | The September rosters are not the cast. | |
| The lastvine: "It is not a plant." | roster json | kept, quoted | | |
| The sharpshrimp: "People who lose companions in the Miasma's reeds rarely see what took them." | roster json | kept, quoted | | |
| The siezer, a mud-whale: "nothing it has seized has ever been pulled free" | roster json | kept | | |
| The duskfire: "Never fight one near anything you want to keep — wooden walls, stores and fields burn first." | roster json | kept, quoted (its fire is 0.2.0) | Beside a parked ship and a yard of salvage this is advice for the crew. | |
| The fermatalis (his name for the decay drake): "usually drunk on it — four separate livers"; cooks count it "among the most valuable beasts in the Miasma"; it takes to you "especially if you bring a drink" | roster json | kept, named and quoted (its fermenting is 0.2.0); the first read called it "the drake" | A beast that ferments anything in hours, tamed with liquor, is very Jawa. | |
| The hell's lantern (his name for the pod worm): muffalo-sized, pods that "glow a sickly orange", milked "for a luminous goo" | roster json | kept, carried into the design (campaign cast, by the patch) | The first read never met it. A lamp that walks, in a dim biome. | |
| The liliana: "RimMandrake tier, not SW"; a wingless moth that "never stops" spinning; silk gathered every few days | roster json, census | kept, carried into "what the crew takes away" | Built: silk and eggs. | |
| The ondrukka: grubs that are "the young of something larger... What matters is how many there are, and how long they have been left." | roster json, census | kept as an ordinary animal; the metamorphosis in his description is lost (the port has none) | A promise in his text that the build does not keep. | Build the cocoon: unscoped. |
| The slurrypede: "cut from this biome" (2026-10-08) | roster json | lost (his cut, this biome only) | | |
| The ommok, moved here from the Long Shade and shrunk by half (2026-10-04) | roster json, cleanse (definition) | kept (its definition still sits in the Long Shade's folder) | | |
| The bozzuga: a root-maze ambusher of the fresh end that eats scuttlers and stranded young | items (ambush frog), review §3 | kept; the first read did not say it eats the orphans | A reason a pool's young do not wait. | |
| The round-2 imports (his review, 2026-09-10): bogwing ("miasma flyer"), blarth, blixus, marsh haunt | roster json, review §1, items (round-2 imports) | kept where the campaign patch puts them; the bogwing flies | | |
| Wild blarth read "as escaped/feral stock" of Hutt pets | roster json | kept in the campaign layer | | |
| The canon cast kept at the roster: shiro, runyip ("Naboo swamp icon"), whisperbird, anooba, grank, vornskyr, zakkeg | roster json, review §1 | kept where the patch puts them | | |
| Three "genuine Star Wars" rows that are team ports, not canon | review §1 | kept as tier history (two since renamed by him to our tier) | | |
| Thirty-eight evictions with reasons (the womp rat, "Tatooine-dry icon in a delta"; the glow bat to the Rot; the hive queen to the incident axis) | roster json | lost from this design; the roster file is the record | Do not delete `rosters/the_miasma.json`. | |
| Fish are the nursery itself, "thinning to nothing on the brine side" | roster json | kept | | |
| A sheet's cut is scoped to that sheet's biome (his ruling, 2026-09-21) | roster json | kept as the rule | | |
| A free install without the donors or the campaign had five animal rows: three scuttlers and two juveniles | review §1 | kept as history (the ports and the four new young are done) | | |
| "Parents' desperate gamble": "send them into the muck, and they die or come back stronger" | sheet §4 | kept, quoted | The same wager as the pilgrimage and the fever; the first read had it as lore without the line. | |
| The composters as "the hopeful mirror of the Scarlands' mortuary guild" | sheet §4 | lost from this design | A cross-biome comparison. | |
| `RM_Stranded` is an unrelated quest about a stranded traveller | fauna roster, items | kept as a naming warning | | |

**Plants**

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The mangals "sweat salt from their leaves": a white rime, "the biome's best texture idea" | flora roster §1, §3 | kept as art direction, quoted | | |
| The thessamor: "the trunk never touches the water"; "the nursery's cage is a plant" | flora roster §3 | kept | | |
| The brelloch: "the last living thing before the salt wins", so a stand of it marks where the gradient ends; its crust is "the cheapest good in the biome, and the one the stills need" | flora roster §3 | kept, carried in as the second gauge tree | With the ilbareen it brackets the line: where brine has been and where it always is. | |
| The quennath: "it never touches the brine at all, it just takes from something that did" | flora roster §3 | kept, quoted | | |
| The ilbareen dead "stay standing for years": "a flagpole, and a graveyard of them"; "the map's only readable history of the one process that governs it" | flora roster §3, §8 | kept, quoted | | |
| As built the canopy does not sort along the line (no recruitment by band) | census | kept, stated in the design's scope line | The first promise in the table depends on it. | |
| The ollamane: "held-up hands", the signature silhouette; its fans "cut for roofing" | flora roster §4, census | kept as art; the roofing is lost (no such product is built) | | A roofing fan would be a material answer to the air: unbuilt. |
| The vellamine: colour that travels along the veins, "something circulating" | flora roster §4 | kept as art direction | | |
| The ismerrow: "the only plant on the planet whose individuals differ"; cut it if it cannot be colour-randomised | flora roster §4, §10 | kept (built with variants) | | |
| The aphreen: "it looks diseased and it is perfectly healthy, and a player who learns that about aphreen has learned how to read this biome" | flora roster §4 | kept, quoted in the design (carried in) | The whole biome's lesson in one common plant. | |
| The nyssolet: "a growth, or a cluster of eggs, and it is stunning"; it "looks least harmless of anything here — which is the ban working as designed" | flora roster §4 | kept | | |
| The sarrash: "a flame, or a fever chart"; plume fibre is "the delta's cheap textile" | flora roster §4, census | kept (built: cloth) | | |
| The rainbow flora as "the deliberate inversion of the Scarlands' rainbow pools" | sheet ban 2 | lost from this design | A cross-biome comparison. | |
| Blooms are not immune to salt, fire or ordinary damage; benign means no attack, toxin or deceit | cleanse (definition) | kept | | |
| The ullavess: a fed vessel is cloudy, "a readout of how thick the scuttler floor is nearby" | flora roster §5 | kept in "later" with the fed displays | | |
| The nemreth: "the most beautiful thing in the biome that is also a killer"; "frost that glitters in the heat" | flora roster §5, §8 | kept, quoted | | |
| The velluric: the water over a bed is "very slightly clearer"; "safe water — and the water is the trap" | flora roster §5, §8 | kept as art direction | | |
| The braskeen: "A channel of braskeen snapping shut one after another as scuttlers cross is the biome's best ambient moment" | flora roster §5 | kept, carried into the "OMG" list | The first read's "the flower eats" had one plant; this is the same idea as a wave. Open and closed art exists; a fed state per plant is "later". | |
| The ommolyn: bare mud round a modest flower; its tube-fibre is "the only cordage that survives the brine" | flora roster §5 | kept as lore; whether any cordage is built is `UNMEASURED` | The first read wrote that the mother's shell is the only brine-proof thing in any source. This is a second, and it is rope. | |
| Three predators work out of sight and each needs a visible consequence | flora roster §5 | kept as a design duty; only a feeding mote is built | | |
| Concealed is not lying: velluric and ommolyn "hide from *scuttlers*, not from people" | flora roster §8 | kept | | |
| A plant as built kills the nearest wild scuttler in range, through walls | census, cleanse (tickets) | kept as owed work | | |
| The immarel: reeds "all leaning downstream", mud that "smells extraordinary"; the attar given a plant, on an agent's call, where the sheet says silt | flora roster §6, §10 | kept (0.2.0 with the attar); the call was flagged to him and never answered | | |
| The wessaline must not read as a trap (the Fever Wood's skimmel owns that) | flora roster §6 | kept | | |
| The only rainbow plant the biome had was a donor's, purged 2026-09-18; the reason cites an item that does not exist | flora roster header, §10 | kept as history | | |
| "Invent a complete rich roster first, then look for Star Wars injection opportunistically" | flora roster header | kept as the rule | | |
| No canon plant is proposed; the nogtyl stays by his review of 2026-09-20 | flora roster §7 | kept | | |
| The donor mangals kept as legacy definitions; one still yields herbal medicine | cleanse (next version), census | lost for the medicine (recommended for dropping; ban 3) | | |

**Sickness, power and goods**

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "A brush with it doesn't forge": only a fever that went deep can leave something | kit spec M5 | kept with fever-forging (0.2.0) | | |
| Mostly nothing; "the fever broke, and left something"; "the table stays illegible, wild-nature, undirected"; the player never picks | kit spec M5 | kept (0.2.0), quoted | | |
| The minor boons: toughskin, painworn, saltblood; a hardened immunity per disease | kit spec M5 | kept (0.2.0) | | |
| The five strange ones by name: swarm-marked, salt-blooded, loam-lunged, mother-dreamed, fever-tempered; "none healing"; never the Force's register | kit spec owner cards | kept (0.2.0); built as stand-ins | The first read counted them without naming one. | |
| Fever-tempered "pays game-wide on a planet whose geography is temperature" | kit spec owner cards | kept, quoted in the design's 0.2.0 line | For a ship that crosses the terminator it is the boon worth getting sick for. | |
| "The tide aware would be useless for most of the game... strip that one"; "Replace it with another similarly themed" | kit spec owner cards | kept: his words are now on the Tide-reader's cut | A boon useless away from this biome was cut for the reason the lens gives. | |
| Loam-lunged must never trigger, surge or scale (the line against the Greentide's growth) | kit spec owner cards | kept (0.2.0) | | |
| "Endure for power": fever-forging kept by the October review | mechanics review M11 | kept; supports moving it up if one thing moves | | |
| Seven diseases forge; the biome adds gangrene, an abasia and gut parasites to the ordinary list | census, biome def | kept as build fact | | |
| The decay cell as built: a 2 by 2 generator that needs the electricity research and takes raw food; "Built raw-food feeding falls short of the promised rot stream" | census, Codex notes, items (decay cells) | kept; the design now says so and no longer promises that spoiled food goes in. `NEEDS HIM` (fuel) | The first read's scene (shovelling spoiled rations) is the item's spec, not the build. Feeding a generator good food is a bad trade on a hungry ship. | |
| The cell's bed: "delta loam, silt ceramic and delta salt"; "spoiled freight becomes power" | review §4, §5 | kept, quoted | It is what gives delta salt and silt a use. | |
| Learned from a dead meter in "a Bitterleaf compost bed"; built as a meter seeded on new maps | review §5, census | kept (built on the map, not at Bitterleaf) | | |
| The name "vorrsalt" failed the stem rule; "evrith" is a surname already in use | review §5 | lost (rejected names) | | |
| His typed words, 2026-10-02: "That rotting bed could also be used to corpse dispose as well... and produce skulls and bones!" | items (decay cells, rotting bed corpses) | kept, quoted (0.2.0) | The first read had the feature from the mechanics review without his sentence. | |
| The skull records whose it was; bones follow body size | items (rotting bed corpses), walk | kept (0.2.0) | | |
| His write-in, 2026-11-10: "and also be useful for Star Wars Cruisine for bizarre ingredients" | owner answers | kept, quoted | | |
| The bed's yield as built is marsh fungus; the cuisine design's "many strange pens, pits, aquariums, large bottles…" | census, items (rotting bed cuisine) | kept (0.2.0) | | |
| Attar's parts: nyssolet beads the fixative, nemreth glue the binder, ullavess fluid and brelloch salt for the stills | flora roster §3 to §5 | lost in part: the built recipe is silt and salt | A whole-biome recipe in the roster; two inputs in the build. | |
| The glaze adds beauty once per artwork; the balm lowers an old injury | census, walk | kept for the glaze (0.2.0); the balm stays recommended for dropping | | |
| The arthropod harvest's trap and one dish: not in the batch he picked on 2026-10-02 | review §8 | kept in "later" | | |
| Delta loam "sits in the same economy as the Rot's fungal-soil trade" | sheet §7 | kept in "later" with the loam trade | | |
| Forage stays generous; the vanilla-Earth cast is evicted | sheet §0, ban 7 | kept as build facts | | |
| Heat kind "owed": the biome reads as ambient under a permanent haze | review §1 | lost (superseded by his One Direct Sun ruling of 2026-10-19: no biome heat kind) | | |
| The shrine denial reaches only the donor biome, not ours | review §1 | kept as a build defect outside design | | |

**Places, people and gods**

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "A Wildsteam pilgrim in the muck is on the worst day of their life, on purpose." | sheet §8 | kept, quoted in the design (carried in) | Dropped by the first read; it is who the crew meets out there. | |
| Bitterleaf: "stilt-and-steam architecture over the channels"; the Wildsteam's "cool-weather retreat and first coastal foothold" | sheet §8, freeze rulings | kept in the campaign layer | | |
| Bitterleaf is a sea-facing, deliberately roadless island; the world's basins are not joined; "river mouth" is read as local delta ecology | cleanse (definition, ambiguities) | kept; the design's fuel line now says Bitterleaf is reached by ship | It changes "a coast where fuel can be bought" into a flight. | |
| The Deepwater vigil's posts "measure the brine year by year, and whatever they know about the shrinking, they knew it here first" | sheet §8 | kept, quoted | | |
| "The Greentide's river graves are the rivers that DIDN'T make it here" | sheet Owed | kept as lore | | |
| "Owed: a stated route between the Miasma delta and the Grey Deep" | freeze rulings | kept as owed lore | | |
| "Steam threads off the stills"; light "as if seen through breath"; the weather "mutes and thickens everything — the biome breathing" | sheet §9 | kept as art direction, the last quoted | | |
| No god is the Miasma's; the Wildsteam's worship is another faith | review §6 | kept | | |
| The rite rules: no god is evil; a rite gives cohesion, never a power; five found rites a god | review §6 | kept in "later" with the rite; rites are second-version by his word | | |
| The second-hand young: a ring of hand-dug wet hollows and a stake scratched "it walked a little" | review §6 | lost (not chosen 2026-10-02); the found site is quoted here so it survives | The saddest object in the file. | |
| The mother's blind side: a counted coup in "the one place on the dayside where the bright hours hide you" | review §6 | lost (not chosen 2026-10-02) | The line about daylight haze is kept: it is the cover this biome gives. | |
| Seven rite ideas considered and not taken (a funeral for the dead warden, a fever-exposure rite, a brine offering and others) | review §6 | lost | | |
| The seed of a rite for Oomo, "the nursed stranger" at the crèche | review §2, §6 | lost (closed when the slot went elsewhere) | | |
| The Recall is found "at a river-mouth disposal depot": "an inscription under condemnation stamps"; it "calls the salvager on yourself" | items (recall rite), review §5 | kept in "later" | | |
| The first egg's two bidders: a collector for the founders, a pilgrim begging the nest be guarded | review §5 | lost with the pitch | | |
| The grounded mother's reef: scuttlers swarm it and "the surge cannot move" it; "the choice comes once, late" | review §3, §7 | lost with the pitch; `NEEDS HIM` | "Once, late" is why it lost: a ship is gone by then. | |

**The pipeline's own material**

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| His card of 2026-10-02, item 1: "Land it and add the giant's choice together" (the free mod stands alone) | review §8, sitting notes | kept as build history (fourteen items, done) | | |
| The cleanse's four instruments (shore sweep, nursery generator, whole-map season, food and rescue budget) | cleanse (models) | kept as build-first work; none is built | | |
| Its thirty-five tickets: twenty-four switch-offs, the surge and route contracts, settings migration, a recorder | cleanse (tickets) | kept as they stand, except where this design moved a feature | Read by the second reader. | |
| Its nine bars and twelve rules | cleanse (bars) | kept as a proposal; a re-run should start from this design | Statements, checks and rules read; the pictures under each bar were not. | |
| Its review rounds: tolerance does not cover harvesting inside her reach; the first-day offer restored | cleanse (fixes, review) | kept (both corrections are in this design) | | |
| "Enjoyment itself is no passing bar." | cleanse (definition) | kept | | |
| The Codex dry run's five code risks and eight draft questions; three were served and answered | Codex notes, owner answers | kept as build facts and open questions | | |
| "What the sea discards becomes both a responsibility and a resource" | Codex notes | kept as a reading (an agent's, not his) | | |
| The walk's bars are a draft; most live checks have never run | walk, Codex notes | kept as status | | |
| World scoring and the rarity slider are built | census, walk | lost (already a row above; built, to be made inert) | | |
| The six mechanics as built, with their gaps | items (mechanics), kit spec | kept as build history | The mechanics item (87 KB) was read at its head and searched, not to its end. | |

## Sources read, and the count

*First read (as it reported itself):* 12 source files, 133 rows, of which 18 lost (whole or in part), 18 record a
move, 2 kept, reshaped and 1 folded into shared machinery. It read whole: the sheet (each line cut at 1,000
characters), the owner answers, the cleanse's owner pages. It read in part: the review, the fauna roster, the flora
roster, the kit spec, the cleanse census, the mechanics review, the walk, fluff cuts and the ladder. It did not
open: `rosters/the_miasma.json`; the cleanse's `definition.md`, `next_version.md`, `ambiguities.md`, `tickets.md`,
`bars.json`, `models.md`, `review.json`, `converge.json`; the Designer record and notes.

*Second read:* the counts, the files read to the end and the files read in part are at the top of this page.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_miasma.md`, `miasma_bedazzle_review_2026-10-02.md`,
`kits/miasma_kit_spec.md` (its six mechanics have landed) and, since the second read,
`miasma_fauna_roster_2026-09-23.md` (its §6, §6a and §6b are now rowed line by line and its rulings quoted).

Hold: `miasma_flora_roster_2026-09-23.md`, because its six reference descriptions, its silhouette forms and its
legibility matrix are the only art brief for the plants (the images were never saved; the words are the brief).

Not for deletion: `rosters/the_miasma.json` (the only record of his sheet sitting of 2026-10-08 and of the
evictions with their reasons); `design/concepts/Miasma/cleanse/` (superseded by this design, never applied; it
should be re-run from this file, not applied, and its signature should not be reused); the validation walk.

Before deleting: `the_miasma.md` is the frozen sheet the Slime's and the Rot's sheets are read against, and the
Grey Sea's design depends on its nursery pairing (the young here, the adults in the terminator waters).
