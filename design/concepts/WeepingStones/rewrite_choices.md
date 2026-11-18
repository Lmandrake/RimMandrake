# The Weeping Stones: what the rewrite chose, what it lost, and why

Companion to `design/concepts/WeepingStones/design.md`, written 2026-11-18 by the same pass. Its job is to let the
older files be deleted without fear: every distinct idea found in any source has a row saying what became of it.
Nothing has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the overriding
priority"*; and *"always look for solutions that make you say Very Jawa"*. The Weeping Stones is the hardest of my
five to read through that lens honestly, because it is the planet's sanctuary and the Jawa already belong at its
edge. Two things made it work without bending the place. First, the truce: his own redirect of 2026-09-24 makes
every animal at the water turn on whoever strikes first, *"including raiders attacking you"*, and a nervous crew
with blasters standing inside the densest crowd of big animals on the planet is the lens. Second, the cleanse
proposal of 2026-11-17 chose seasons of fish husbandry as the signature; this design keeps the pen but sizes it to
a stop, and lets the truce carry the visit.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, off by default" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The pen sized to a stop.** His experience line and his greenlight (*"love it. Moisture farmers specializing
   in fish"*) are about a farm. The stocked-pool design's own picture runs *"three seasons later their own water
   is alive."* I kept the pen in 0.1.0 as something a crew runs for weeks and lost the seasons to "later". If the
   husbandry cannot produce anything worth having inside a month, 0.1.0's pen is a chore with no harvest, and the
   honest version is the truce alone. Asked as `NEEDS HIM`.
2. **The ship weeps.** I proposed the wear on the hull myself, from the sheet's physics (*"every cold shaded face
   of it weeps"*) and its palette (*"verdigris where metal meets moss"*), because the review says the place
   *"does nothing to your ship"* and his ruling of today says every biome states one. It is deliberately mild and
   half a benefit. It is the only thing in this design that is not in a source, and it is the first thing to cut
   if he would rather the Weeping Stones were simply the place that leaves the hull alone.
3. **The pilgrim passage.** *"The landing shelf blocks the pilgrim approach; launch, or grant a permanent public
   passage, rebuilding a corridor through your ship where pilgrims and distrusted factions pass; closing it later
   is a recorded breach."* One of four ideas he called *"close misses"* on 2026-10-02, before the lens. It is the
   claim law turned on the crew's own ship. Kept as a close miss; asked as `NEEDS HIM`.
4. **The last caravan.** The oldest crab carrying a whole lost merchant caravan's freight, whose *"handlers were a
   lost Jawa clan."* The review itself called it *"the most Jawa of the five"*. Not chosen: he chose the walking
   condenser instead. Lost.
5. **The fish that lies.** A loomu taught a vane chord that is a vault's credential; *"one try at a silent vault; a
   slipped keeper's name arms the sentries forever."* The review: *"a scavenger's break-in."* A close miss by his
   word. I used the loomu's built line (it repeats what it hears) as a moment and promised nothing more.
6. **The sound.** *"Each array is its own chord, so each oasis has a name in sound before it has one in words;
   pilgrims navigate the last miles by ear ... A dead oasis is silent — the first thing a traveler notices, and
   the worst."* Never ratified, never built, and the cheapest beauty in the biome. 0.2.0.
7. **The oasis-maker.** His own redirect, built, 1,400 lines, and by his own words *"not very important for the
   Jawa utinni scenario."* Later. A machine that grows water where a fleeing ship lands is not nothing, and I
   left it where he put it.
8. **The recapture ladder.** *"Shields → overhangs → full enclosure ... servo-driven vents that open to accept
   water when the wind brings it and seal the moisture in otherwise."* The sheet's endgame for a settlement, and a
   settlement is what the crew is not. Later.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **The unique condenser crab, its moving pool, guiding it, selling where it settles, cutting the machine out, the
  machine as a ship water plant:** next version → 0.2.0.
- **The two condenser quests and their faction slots; sale delivery:** next version → 0.2.0.
- **Dewsilk; rare loot from the pools; the burrak's digs; species catch methods; the mirrik swarm's special
  behaviour; the aeolian chords; scanner readings:** next version → 0.2.0.
- **The pen across seasons** (retained breeders over repeated cycles, the crash year): first version → later. In
  0.1.0 the pen lasts a stop.
- **The whole-map husbandry season as the bar's unit:** replaced by one stop.
- **Stayed "later" from the cleanse's "next version":** the recapture ladder, pilgrim routes, courtship, the
  sillik's face-feeding, giant collision geometry, the cooperative cull, doubt extensions, the ssurr's aura, huldu
  fat, the shade study lesson, the Refused Toll. Not moves.
- **New, not in any source:** the ship's shaded side weeping; the truce read as the crew's defence against the
  Empire (his ruling names raiders; the Empire is my reading of "anyone"); the crew's own nervous first shot as
  the stop's worst case; buying fuel at the water as the answer to his fuel ruling; a crowded oasis possibly
  counting as loud to the search (asked as unsettled, not asserted).

## Every idea, row by row

Source names: *sheet* = `biomes/weeping_stones.md`; *fauna roster* =
`biomes/weeping_stones_fauna_roster_2026-09-24.md`; *flora roster* =
`biomes/weeping_stones_flora_roster_2026-09-24.md`; *shine options* =
`biomes/weeping_stones_shine_options_2026-09-24.md`; *stocked pool* =
`biomes/weeping_stones_stocked_pool_2026-09-24.md`; *review* = `biomes/weepingstones_bedazzle_review_2026-10-02.md`;
*roster json* = `biomes/rosters/weeping_stones.json` (all under `design/Jawa/worldbuilding/`); *cleanse* =
`design/concepts/WeepingStones/cleanse/`; *walk* = `design/validation_walks/RimMandrake/WeepingStones.md`; *owner
answers* = `design/RimMandrake/designer_codex_2026-11-09/WeepingStones/ANSWERS_OWNER.md`; *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *experiences* =
`design/RimMandrake/biome_experiences_2026-10-20.md`; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*ship gifts* = `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Tended water"; "stone that sweats on its cold faces, and everything alive or built crowding around to drink the wind" | sheet header | kept, quoted | | |
| "Bright dry stone and secret weeping shade, where every pool is a gathering. Keep the oasis healthy, or it breeds something wrong." | walk, experiences, mechanics review | kept, quoted | His card. | |
| Read against the Cracked Lands: fugitive water against tended water | sheet header | lost from this design | Cross-biome framing; belongs in the consolidation. | |
| The oasis as the water god's ground; "Oomo's lesson in the hearts of the Jawa" | sheet header, §4 | kept in the campaign layer | The free biome names no god. | |
| Biome plus hand-placed, hand-named oasis landmarks with companion loadouts; 186 pools placed | sheet header, Owed | kept in the campaign layer (world state) | | |
| Measured tiles, sun, temperature, elevation, regions | sheet §0 | lost, except "high stone, high sun on most tiles" | A tile count is never evidence; the planet is painted at the end. | |
| An anomaly biome: wherever high stone stands in the moisture corridor | sheet §0, §2 | kept as one sentence | | |
| The seep oases: fed from below, "a green eye in open nothing"; "the stones are beneath the oasis now" | sheet §2b | kept as the stated exception | | |
| "Water is combed from moving air, never rained" | sheet §3 | kept, quoted | | |
| The convergence: one right shape, a thin upright surface held into the airflow | sheet §4, §9 | kept, quoted | | |
| "At a distance you cannot tell the relics from the living" | sheet §9 | kept, quoted | | |
| Life follows the shade, not the soil | sheet §4 | kept | | |
| Pilgrimage density: every big animal on the hot half of the world must come | sheet §4 | kept, quoted; made the first minutes | | |
| The truce passage ("strangely sacred ... Even the Jawa ... feel it. If there is enough for all, you take what you need and you leave.") | sheet §4 | kept, quoted | | |
| The truce breaks only if the water is drying up | sheet §4 | lost | The born-and-dying water is dead by his word; nothing dries a pool in these versions except the crab leaving. | |
| Among animals the truce is mutual assured destruction | sheet §4 | kept as the reason the retribution works | | |
| Pools as places of romance, play, bonding and breeding | sheet §4, §7 | kept as the fan-dancer's display; choreography later | | |
| The claim law: settling is valid; a toll on unsettled water is "barbaric" | sheet §4, §6 | kept, quoted; turned on the crew as an unsettled question | | |
| The six "always true" lines | sheet §5 | kept; the weep streak and the comb rule carried | | |
| Every oasis is tended and individually different | sheet §5 | kept in the campaign layer | | |
| Bans: no vanilla life, no snow, no rain-fed ecology, no native without the comb, no ambush at water, no toll on unsettled water | sheet §6 | kept | | |
| "A place a colonist can stand beside every dayside animal in peace: good taming, bonding, and observation ground" | sheet §7 | kept, reshaped: a small crew standing in it is the first moment | | |
| The map-scale read: concentric rings, "the most legible tile on the world" | sheet §9 | kept, quoted | | |
| Palette: bone-white stone, black weep-streaks, green in blue shade, verdigris where metal meets moss | sheet §9 | kept; also the source of the hull's wear | | |
| Weather: clear and windy; no rain, never storms, never snow | sheet §10b | kept (the review records ordinary fog and the odd sandstorm) | | |
| Fog at wind-hour | sheet §10b, shine options | lost (dead by his word: "nah.") | | |
| Sound: aeolian chords, drip-echo, the crowd; "a dead oasis is silent" | sheet §10b | moved (cleanse next version → 0.2.0), quoted | Never ratified, never built. | 0.1.0: cheap, and the stop's first impression. |
| The 2026-09 roster file: nineteen fauna rows in rings, fourteen flora, nine owed bodies, 24 evictions | roster json | lost from this design | Superseded by the two rosters' rulings. | |

### The truce and the water

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Anyone fighting including raiders attacking you near the water get animal retribution ... Don't fight back and the creatures will fight for you." | shine options verdict 5 | kept, quoted; extended to the Empire | | |
| The engine can tell who started it; self-defence is not guilty | shine options | kept | | |
| Predators never start a hunt at full water, tamed ones included | review ruling 1 | kept | | |
| The truce as neutral ground and diplomacy | shine options, option 5 | lost (redirected by him) | | |
| The truce ruled cheap for the first version; the honest behaviour later | sheet, Owed | kept (it has since been built both ways) | | |
| Pen cells sit outside the truce | stocked pool §1, §3; cleanse | kept | *"The pen is not the truce."* | |
| Reliable standing fresh water | sheet §7 | kept; the ship fills its tanks | | |
| The born and the dying water | shine options, option 2 | lost (dead by his word: "nah too much.") | | |
| The heat kind by sun height from the tile's latitude; overhang shade | review, ruling 1 | folded into shared machinery (the one sun) | | |
| Local heat fields and arrival advice that contradict the roof-and-parasol ruling | cleanse | lost (to be corrected) | | |

### The pool stock

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "love it. Moisture farmers specializing in fish ... Make the fish nasty and way too active. And some shouldn't be fish but alien beasts you really wonder if we should be eating." | shine options verdict 1 | kept, quoted | | |
| The fantasy: "the water has a crop of its own"; "the stock does not want to be farmed"; "husbandry here is a contact sport" | stocked pool §1 | kept, quoted in part | | |
| "Three seasons later their own water is alive" | stocked pool §1 | moved (first version → later) | Seasons. | Hold it: the cleanse's reading. |
| Murrin, the baseline pool fish; catchable; the net can start a pool from it | fauna roster, review ruling 1 | kept | | |
| Skarrin, the ring-breaker; karrek, the flenser; vizhik, the walker | stocked pool §2 | kept, quoted | | |
| The vizhik's escape by a visible route | stocked pool, cleanse | kept | | |
| Vhorrin, the cull: the same stock grown past what the pen can hold | stocked pool §2d | kept, quoted | *"This is the line."* | |
| Loomu, the caller; huldu, the warm one; ivvol, the tally | stocked pool §2e–g | kept, quoted | | |
| "They are the best eating in the biome. Everyone says so. Nobody says it comfortably." | stocked pool §1 | kept, quoted | | |
| Ivvol immune to the vhorrin | stocked pool, cleanse | lost (recommended for dropping; his to confirm) | | |
| Ivvol in neighbouring pools surface at the same moment | stocked pool §2g | kept as flavour | | |
| The husbandry loop: stock, feed, net, harvest, overdraw, cull, recapture | stocked pool §3 | kept | | |
| "Care automatically; harvest only on orders ... do not invent new UI" | owner answers | kept, quoted | | |
| The gauge: healthy, thin, silent, vhorrin; readable before a loss | mechanics review, cleanse | kept | | |
| Net capture of wild stock | mechanics review | kept (owed a repair: the fish outruns the net) | | |
| The cuisine hooks; the doubt in eater and cook | stocked pool §4, cleanse | kept as the memory; recipes are the campaign's | | |
| Rare catches | mechanics review, cleanse | moved (→ 0.2.0) | | |
| Huldu fur and rendered fat | mechanics review, cleanse | kept in "later" | An open follow-up of his. | |
| Species-specific catch methods; the cooperative cull; the crash year; doubt extensions | cleanse | kept in "later" | | |
| The fish walk (the stock crossing wet stone in weather) | review ruling 3 | lost (a close miss by his word) | | |

### Animals and plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Three rings of fauna: residents, pilgrims, the margin | sheet §10 | kept as the roster's shape | | |
| The 29 animals cast here before the sheet; keeps and violations | sheet §10 | lost | Reconciled by the roster's rulings. | |
| The dewback reassigned here | sheet §10, Owed | kept in the campaign layer (a canon animal) | | |
| The fanback, "the comb convergence was waiting for us" | sheet §10 | kept in the campaign layer | | |
| Tirbak, the walking cistern | sheet §10, fauna roster | kept, quoted; a takeaway | | |
| Burrak, the well-digger (one def, by ruling); the elder form | sheet §10, fauna roster | kept as an animal; its digs becoming pools moved (→ 0.2.0) | | |
| Sillik, the weep-mouse | sheet §10, fauna roster | kept | | |
| Mirrik, the dew-smoke, a flyer | sheet §10, fauna roster | kept | | |
| Ssurr, the fan-dancer | sheet §10, fauna roster | kept, quoted | | |
| Vhakk, the warden: never hunts at water, owns the approaches | sheet §10, fauna roster | kept, quoted | | |
| Vellak, the pilgrim herd of tall sail-comb striders; kirruk, the ridge-flier (both by card, 2026-09-24) | fauna roster | kept | | |
| The ten kept canon and donor rows (dewback, fanback, colossus toad, ollopom, boma, dactillion, the ikee, bantha, jamel, eopie), patched in by the campaign; pilgrims are multi-homed by design | fauna roster §3 | kept in the campaign layer | The in-game reason for a second home is the pilgrimage itself. | |
| The side effect that the player's tamed predators also refuse to hunt near the pools | fauna roster ruling 3 | kept (accepted by card) | | |
| The ikee as an omen | sheet §10 | kept in the campaign layer | | |
| The gorrask, a stone-crab bigger than a canyon | review, fauna | kept as an animal; as a landform later | | |
| The walking condenser: "I love (1) ..." | review ruling 2 | moved (→ 0.2.0), quoted in the list above | | 0.1.0: the ship's gift a version early, on a once-per-world event. |
| "Buildings and built floors only" are spared by the walking oasis | owner answers | kept (0.2.0) | | |
| "A usable exit and the promised access to water fulfil the promise" | owner answers | kept (0.2.0) | | |
| The Hutts' Arena capture, or keeping it free against hunters | review ruling 2 | moved (→ 0.2.0) | | |
| The last caravan; the crab on the hatch | review §5, ruling 2 | lost (not chosen) | | See above. |
| The ancient condenser plant as the ship's water machine | ship gifts, review ruling 2 | moved (→ 0.2.0); `NEEDS HIM` | | |
| Plants as blades; mats ridged square to the wind | sheet §4 | kept | | |
| Dewblade, weep-mat, verdimoss, shadefern, dripfringe | flora roster | kept | | |
| Bladderquill and bladder-fruit, "food and drink in one object" | sheet §11, flora roster | kept, quoted | | |
| Salvecomb, the medicine plant | flora roster | kept, quoted | | |
| Rockfinger: "long terrible shadows from the rims of tall rocks… very scraggly and hardy" | flora roster (his words) | kept, quoted | | |
| Steamfrond at the seep vents | flora roster | kept | | |
| Dewgourd: "a large melon like gourd that takes a long time to grow..." | flora roster (his words) | kept, quoted; a crew eats one somebody else grew | It takes long to grow by his own spec. | |
| The silhouette briefs | fauna roster, flora roster | kept as art direction | | |
| Earth palms out of our oases; native plants on oasis tiles | review ruling 1, mechanics review | kept | | |
| Scarce timber | cleanse | kept | | |

### Machines, goods, people and rites

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The succession ladder: natural weep, ancient vane arrays in four states, shields and overhangs, full enclosure | sheet §5, §8 | kept in "later", quoted in part | | See above. |
| The machines that weep: restorable vane arrays | shine options, option 3 | lost (redirected by him into the oasis-maker) | | |
| The oasis-maker: "machines that create oases slowly when placed near shaded terrain near rocks ... Unfortunately it's not very important for the Jawa utinni scenario" | shine options verdict 3 | kept in "later", quoted | | |
| Its quests (obtain, sabotage) | shine options, review | kept in "later" | | |
| Relic condenser tech; comb-vane segments; cistern shafts | sheet §7, §11 | kept in "later" (never ratified) | | |
| The condenser fin as the player's entry rung; shade-lids; servo-vents | sheet §11 | kept in "later" | | |
| Dewsilk | sheet §11, review ruling 1 | moved (→ 0.2.0) | *"The biome's signature trade good."* | |
| Seep-salt | sheet §11 | kept in "later" | Not located in source. | |
| Oomo tokens and truce-stones | sheet §11 | kept in the campaign layer | | |
| Cairns, dry cisterns, camp rings between oases | sheet §8 | kept in the campaign layer | | |
| The Jawa at the water: pay-and-go, the crawler at the margin, comb-sails, market-day | sheet §12 | kept, quoted; it is the crew's history with this place | | |
| The other faces: Hutt palaces, Deepwater stewards, Wildsteam seeps, Homestead farmers, Deep Desert Tribes, Geonosians who do not stop, droid enclaves on poisoned water, the Helix at a dead ring, Blackstar's rendezvous | sheet §12 | kept in the campaign layer; three quoted as who is at the water | Never ratified as a block. | |
| The Empire meters the water, "despised past politics" | sheet §12 | kept, quoted; made the Empire section's opening | | |
| The Refused Toll: "This is pretty cool (2). Gotta do it." | review ruling 4 | kept in "later", quoted | Tabled with all rites; blocked on a new kind of site. | |
| The Open Water rite | review §6 | lost (not chosen) | | |
| The pilgrim passage through the ship | review §5, ruling 3 | lost (a close miss by his word); `NEEDS HIM` | | See above. |
| The dewsilk casket | review §5, ruling 3 | lost (a close miss by his word) | | A portable stasis casket: large, and a rescue a ship could finish. |
| The fish that lies | review §5, ruling 3 | lost (a close miss by his word) | | See above. |
| The stone lets go; weeping masonry | review §5, ruling 3 | lost (held off the card, unticketed) | | |
| "It does nothing to your ship" | review §0 | kept, quoted; answered with the mildest wear I could ground | | |
| The ship gift: the ancient condenser plant | ship gifts | kept (0.2.0) | | |
| Mod Settings sliders (truce radius, vhorrin odds, vizhik escape) | review ruling 1 | kept | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (tending stocked pools; mismanagement breeds a vhorrin; cull and recover) | cleanse owner pages | kept, reshaped: sized to a stop, with the truce carrying the visit | | See above. |
| Its readings ("a pool", "sustainable", "harvest is a choice", "feed", "read", "eats the farm", "it escapes", "truce", "shade", "weeping", "doubt", "scarce timber") | cleanse owner pages | kept, except "sustainable" across seasons | | |
| Its nine bars | cleanse | kept as history; the twelve promises in the design are the proposal to argue from | | |
| Its three models | cleanse | kept, with the stop as the husbandry model's unit | | |
| Tickets and switch-offs | cleanse | kept as they stand, except where a feature moved | | |
| The mechanics review's dispositions | mechanics review | kept as history | | |
| The must-be-true list | walk | kept | | |
| The dewsilk row among the kept ones | fluff cuts | kept (he keeps dewsilk as the signature trade good) | | |

## Sources read, and the count

Measured after writing: a script counted the table rows and the first words of the "what happened" column; the file
count is the files named below as opened, counted by hand.

Read whole: the sheet (its first twenty lines by preview, the rest in full); the cleanse's owner pages; the owner
answers; the mechanics review's Weeping Stones table (long cells cut at about 600 characters); the ship-gifts row.
Read in large part: the shine options (the five verdicts in full; the options themselves by heading only); the
stocked pool (the fantasy in full, the eight bestiary rows by their "look" lines; not the husbandry loop, the
cuisine hooks or the questions); the review (the plain-words paragraph, the heat note, the built and unbuilt list,
the five outside ideas with long cells cut, and the turn-one rulings; not the scorecard, roster fill, slate or
rites sections); the fauna roster (its rulings block and its kept-and-ruled rows in full; the ten invented rows by
title only). Read by heading or by search: the flora roster (ten rows,
each cut at about 330 characters); the roster json (structure and row names); the cleanse next-version list
(entry titles only, plus the summary on the owner pages); the experiences table; fluff cuts (searched). Not read:
the cleanse's definition, tickets, ambiguities, bars, models, census, review, converge and fixes files; the
Designer's `NOTES.md`, `QUESTIONS.md` and `record.json`; `design/RimMandrake/` material on the oasis-maker;
`sacred_sites_pass_1.md` (cited by the sheet). The fauna roster's ten invented rows were read by title only: a
second reader should check their detail for ideas with no row here.

**15 source files opened, 119 rows**, of which **18 lost**, **9 record a move** (whole or in part), **2 kept, reshaped** and 1 folded into shared machinery.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `weeping_stones.md`, `weeping_stones_shine_options_2026-09-24.md`,
`weepingstones_bedazzle_review_2026-10-02.md`, `rosters/weeping_stones.json`, and
`weeping_stones_fauna_roster_2026-09-24.md` once its rows have moved to wherever the art seat reads (it and the
flora roster are the silhouette briefs).

Hold until the pen is built out and the cuisine is designed, because it is their only specification:
`weeping_stones_stocked_pool_2026-09-24.md` (the husbandry loop and the cuisine hooks).

Before deleting `weeping_stones.md`: its section 12 (the thirteen faction faces at the water) and its claim law are
the campaign's only statement of those ideas, and were never ratified as a block. Move them to wherever the
campaign layer reads first.

Not for deletion: `weeping_stones_flora_roster_2026-09-24.md` until its rows have moved to wherever the art seat
reads (it is the silhouette brief); `design/concepts/WeepingStones/cleanse/` (superseded by this design, never
applied; it should be re-run from this file, not applied); the validation walk; the Designer's November question
and answer files.

Before deleting: the sheet is cited by path from the Cracked Lands sheet ("read against") and by section from both
rosters, the stocked-pool design and the review.
