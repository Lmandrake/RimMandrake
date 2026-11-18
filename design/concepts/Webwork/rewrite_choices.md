# The Webwork: what the rewrite chose, what it lost, and why

Companion to `design/concepts/Webwork/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the overriding
priority"*; and *"always look for solutions that make you say Very Jawa"*. The Webwork needed the least bending of
my five. Its sources already describe an expedition and not a home: the cleanse proposal of 2026-11-17 chose
"touching or robbing the web brings hunters; maintaining sunlit ground breaks their approach" as its signature and
his own November answers are about a prepared escape route and a windfall. And he had already answered the lens's
first question for this biome a month earlier: *"Landing a ship into a webwork will surely get a response."* What
this design changes is the base (the ship in its clearing, not a walled compound), the things the lens asks every
biome to state (cover, fuel, wear on the hull, the Empire), and the scope of a few creature moments.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, off" and "recommend retiring", and this design uses
0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move); *folded into
shared machinery*; *lost*. Where a *moved* row's last two cells are empty, its reason and its other choice are the line
for that feature under "Scope moves": the other choice is to move it back, and the cost is the scenes and checks
that come with it. Where a *lost* row's last two cells are empty, the reason is in the outcome cell itself (a ban,
a card, his word) and the other choice is to reopen that ruling.

## The ones I would look at

1. **The hull trellis.** *"On a landed ship a pale root comes through an inside doorframe, thickens, forces the
   door, splits the frame. Cut it out, or take off: the supply is severed but the damage flies with you."* Not
   chosen on 2026-10-02. It is the only idea in any Webwork source written about the ship, it is the plantation
   *"occupying structures"* in its own voice, and he reversed the same kind of decision for the Greentide
   today. I used silk and wrapped doors as the wear on the hull because those parts are built. Asked as
   `NEEDS HIM`.
2. **The probe droid and the droid-haters.** I did not find this connection made anywhere in the sources. The
   owners *"HATE droids and preferentially destroy them"*; the Empire's first step is a probe droid; each step of
   the search *"comes only if the one before it succeeded"*. If the preference covers the probe, the Webwork
   breaks the Empire's ladder at its first rung. I wrote it as a question and not a promise.
3. **The siege as 0.2.0, on the next tile.** The mechanics review calls it *"the one thing that makes the biome
   come to you"*. It was built for a colony that lives beside the Webwork. A ship that robbed a nest and then
   landed one tile away is the same case, and better. It stays 0.2.0 because nothing of it has run live and it is
   over a thousand lines.
4. **The dead giant.** *"They Ate the Colossus"*: a wrapped skeleton *"bigger than a colony building"*, read bone
   by bone until the last wrapping shows what killed it. His pick, by card. It is quiet, forensic and takes days,
   and I put it in 0.2.0 behind the heist. A crew of scavengers climbing a wrapped skeleton for the silk on it is
   a strong picture and could argue its way into 0.1.0.
5. **The pale flowers as a map.** The sheet: *"Fresh blooms mean an active line; withered lines mean abandoned web
   and the safe path. The biome's palette is also its map, for anyone brave enough to read it."* His later words
   (2026-10-07) redid the flower and ended the mechanic: *"Small graveyard-like flowers meant to be a sober
   ceremony to the death of this biome. No need for new state machine building."* I kept his redo, and I listed
   "showing which lines are live" under 0.2.0 as unbuilt. On his own words that line should probably be in
   "dropped". It is the row I am least sure I placed correctly.
6. **The plantation's churn.** *"Gaps open and close, paths are temporary."* The explosive-growth engine in
   self-consuming mode is in the sheet and was never built as such. What survives is regrowth closing a clearing.
7. **The still-burner.** *"Tap the jungle's trees to burn the jungle's owner."* One item that is drink, trade good
   and flamethrower fuel. The fuel half is in 0.2.0 because his ruling asks for a fuel source; the weapon is in
   "later" with the Wildsteam's kit.
8. **Bound bait.** His ruling of 2026-09-11 accepted *"feeding a bound colonist out as convergence bait"* as
   legitimate player cunning, with nothing built to support it. In the design the crew baits with a broken droid
   instead. Both stay possible; neither is promised.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **The vennick running toward clutches:** next version → 0.1.0. *"A living treasure map to a nest"* is the heist's
  first clue and costs little.
- **Silk spun at a target and doors wrapped** (parts of the siege): next version → 0.1.0, on the home map, aimed
  at the landed ship. This is the wear on the hull his ruling of 2026-11-18 asks for.
- **The neighbour siege (incident, lord, spinning jobs, persistent silk, cocoon rescue):** next version → 0.2.0.
- **The traction lance, its fabric loop and its discovery:** next version → 0.2.0.
- **The giant's remains (site, chapters, collapse):** next version → 0.2.0.
- **Webfall's accuracy penalty; passive web stickiness; directed beetle herding; scanner clues:** next version →
  0.2.0.
- **Tapping the still-tree (the cleanse's "weapon fuel"):** next version → 0.2.0 for the fuel; the weapon stays
  later.
- **Plant traps, needle attacks, lure plants:** recommended retirement → 0.2.0. Asked as `NEEDS HIM`.
- **Flower freshness as a readable state:** recommended retirement → 0.2.0, unbuilt. See "the ones I would look
  at": this may belong in "dropped".
- **Stayed "later" from the cleanse's "next version":** the campaign markets and weavers, the assassination
  quests, the egg and mandible bounties, the broker quest, the Felled Noon, the titan battle, fluid irrigation,
  the long arrival letter, the shade-cloth lesson, special prey and kill trails, victim-gear salvage in nests,
  flier radar. Not moves.
- **The whole-season bar:** the cleanse's eighth bar is a complete occupied season. Here the unit is one stop: a
  landing, a clearing kept for days, one raid and a launch.
- **New, not in any source:** the ship's clearing as the fortress (the sheet's is a walled compound); the canopy
  as cover from orbit set against the canopy as the owners' shade; an Imperial probe as a droid the owners hate;
  the crew's own droids kept aboard, and a broken one used as bait; troopers bound and collected.

## Every idea, row by row

Source names: *sheet* = `biomes/the_webwork.md`; *sitting record* =
`biomes/webwork_owner_and_nest_2026-09-23.md`; *egg market draft* = `biomes/webwork_egg_blackmarket_2026-09-24.md`;
*fauna roster* = `biomes/webwork_fauna_roster_2026-09-23.md`; *flora roster* =
`biomes/webwork_flora_roster_2026-09-23.md`; *review* = `biomes/webwork_bedazzle_review_2026-10-02.md`; *kit spec* =
`biomes/kits/webwork_kit_spec.md`; *roster json* = `biomes/rosters/the_webwork.json` (all under
`design/Jawa/worldbuilding/`); *cleanse* = `design/concepts/Webwork/cleanse/`; *open questions* =
`design/RimMandrake/webworks_open_questions_2026-10-22.md`; *owner answers* =
`design/RimMandrake/designer_codex_2026-11-09/Webwork/ANSWERS_OWNER.md`; *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *owner cards* =
`design/RimMandrake/biome_owner_cards_2026-10-22.md`; *experiences* =
`design/RimMandrake/biome_experiences_2026-10-20.md`; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*ship gifts* = `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The loom"; "a green and white hellscape, silent, owned, and growing" | sheet header, §9 | kept, quoted | | |
| "So quiet that you know you're in terrible danger. It makes treasure, it eats all, and it's coming for you." | experiences, mechanics review | kept, quoted | His typed line. | |
| "Landing a ship into a webwork will surely get a response it's only quiet if you walk into it. Mostly about soundscape." | open questions | kept, quoted; made the first minutes | It answers the lens's first question in his own words. | |
| No attack-free days on foot | open questions, cleanse | kept (dropped list) | | |
| Read against the Greentide: loud lawless plenty against silent ownership; a fourth water-law, "occupied" | sheet header | kept as one sentence | | |
| The plants drank the river; "the water is inside" | sheet §1, §5 | kept, quoted | | |
| Measured tiles, sun, temperature, relief, the bimodal rain | sheet §0 | lost | A tile count is never evidence; the planet is painted at the end. | |
| Storm-fed highs as the reservoir, irrigated lowlands as the reach | sheet §0, §3 | lost as geography; "water held inside the plants" kept | A stop is on one map. | |
| Donor inventory; the donor's own advice ("build a walled compound, leave it seldom, and USE the spiders") | sheet §0, §7b | kept, reshaped: the compound is the ship in a clearing | A ship is the walled compound the crew already owns. | |
| Infested jungles are bombarded from orbit with atomics; that is how the homeworld died | sheet §0, §4 | lost from this design | Campaign lore about the canon species. It is a fine reason for the Empire to bombard, and I did not use it. | One line in the campaign layer; free. |
| "The entire biome is a single organism of shadow" | sheet §3 | kept, quoted | | |
| "It is a plantation, and every living thing in it is stock in the owner's ledger" | sheet §3 | kept, quoted | | |
| UV keeps the highest peaks clear; the dry sun cages it on every side | sheet §2, §3 | lost as geography | | |
| The seven "always true" lines | sheet §5 | kept; four quoted | | |
| "Only fire provides the kind of protection and offense needed to drive them back" | sheet §5 | kept, quoted | | |
| "The territory is growing at its margins"; the creep visible between visits | sheet §5, §8 | lost | *"Webs don't creep they are made by spiders."* | |
| Bans: no tamed owner, no truce language, no silk from an abdomen, no safe canopy cell, no other source of the silk | sheet §6 | kept | | |
| Art theme: green gloom, white blades of sun, "safety rendered as glare", catenary lines, almost no motion | sheet §9 | kept as art direction | | |
| Sound: "the quietest green place on the planet"; drip, silk-creak, the listener's own steps | sheet §9 | kept, quoted; owed as sound | | |
| The roster file: five fauna rows, seven flora, four owed bodies, "eaten" as the eviction default | roster json | lost from this design | Superseded by the sitting's rulings and the two rosters. | |

### The owner species

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| An invented spider of ours, the ollathrix; mapped to the canon Wyyyschokk under the campaign | sitting record §0, §1 | kept | | |
| One race, one kind; no castes, no guild | sitting record §0 | kept | | |
| Not native; a sterilised homeworld; "this is one world they cannot consume" | sheet §4 | lost from the free design; campaign lore | The free biome names no canon. | |
| Frame: as large as an elephant, mostly sharp legs | sheet §4 | kept | | |
| The mouth-loom; the binding that "does not wear off for days unless attended medically"; "The spider comes back." | sheet §4 | kept, quoted | | |
| Adhesive commandable: unreleasable or slick as ice | sheet §4, cleanse | lost (the cleanse retires the legacy adhesion command) | | |
| Mandibles that "crush a human head in a single bite" | sheet §4 | kept, quoted | | |
| Legs that cut through a Stormtrooper's leg armour | sheet §4 | kept, quoted as the Empire's benchmark | | |
| Venom: paralysis and heart attack in large prey | sheet §4 | kept | | |
| The web-sense; vibration; summoning support; tracking for over a kilometre | sheet §4, kit spec | kept as contact and convergence; "over a kilometre" lost | A map is not a kilometre. | |
| Ambushers bursting from underbrush, underground or above, with a visible tell | sheet §4, cleanse | kept | | |
| Fecund and self-limiting; their own main predator; "erratic, psychotic intelligence" | sheet §4, §4b | kept, quoted | | |
| Legends of them talking, flavour only | sheet §4 | lost | The sheet itself says it is never a mechanic, and the free biome's spider has no galaxy to have legends in. | One line of campaign flavour; free. |
| Helpless in direct sunlight | sheet §4 | kept | | |
| "Cripple, never down" | kit spec ruling 1 | kept | | |
| "There is no night here, and no light a player can make has the effect of this planet's terrible sun." | kit spec ruling 2 | kept, quoted | | |
| Overcast is the only moat-off | kit spec ruling 2 | kept | | |
| Bound bait accepted as emergent story | kit spec ruling 3 | kept as possible, not promised | | |
| They hate droids | sheet §4 | kept, quoted; extended to the crew's droids and asked about the probe | | |
| Droid preference only among equally reachable prey | cleanse | kept | | |
| Untameable; enemy of all, ally to none | sheet §4 | kept, quoted | | |
| "The existing ollathrix are enough ... coordination must be convincing" | owner answers | kept, quoted | | |
| Sun-scald counts real tree shade | review ruling 1, mechanics review | folded into shared machinery | | |
| Mechanisms in the free tier; the canon skin as a separate patch | sitting record §6, kit spec ruling 6 | kept as a build fact | | |

### The web, the clearing and the silk

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Cables, strands, carpet at spider sites | cleanse, mechanics review | kept | | |
| Old anchor lines, sheet webs and irrigation gutters as objects | sheet §8, cleanse | lost (recommended for dropping; his to confirm) | Nothing places them since the front was deleted. | |
| The web front that creeps | review ruling 1, open questions | lost (deleted by his card) | | |
| Silk gutters as irrigation, moving water | sheet §1, §3, cleanse | kept in "later" | | |
| The light-moat: "a clearing is the fortress"; "fire is architecture" | sheet §7b | kept, quoted | | |
| Threats to it: regrowth, overcast, an untrimmed margin | sheet §7b | kept, quoted | | |
| "A prepared escape route is essential..." | owner answers | kept, quoted | | |
| "A major windfall..." | owner answers | kept, quoted | | |
| The successful expedition must fund what ordinary work over the same days could not | cleanse | kept as the measure of "windfall", not as a bar | It pins a ratio. | |
| The plantation's churn: gaps open and close | sheet §4c | kept, reshaped: regrowth closes clearings | | See above. |
| Thrixweave: hyperweave renamed, sole source; cut, butchered, raided | sheet §7, sitting record §2 | kept, quoted | | |
| Cutting rings the line; burn, combat and beetles yield nothing | sheet §7, cleanse | kept | | |
| Rare traders resell it at a steep price | open questions | kept, quoted | | |
| Stuff-rolled gear made rare | sheet, Owed | kept as a build fact | | |
| Shokkweave as the campaign's name | sitting record §2 | kept in the campaign layer | | |
| Webfall | mechanics review, fluff cuts | kept, with his words; its penalty moved (→ 0.2.0) | | |
| Sheetfall: torn web settling across the moat as a roof | review §5 | lost (not chosen) | | A weather that attacks the clearing: large, and exactly on theme. |
| The hull trellis | review §5 | lost (not chosen); `NEEDS HIM` | | See above. |
| The traction lance; "Lasso relative"; one pull shared with the capstan | review ruling 3 | moved (→ 0.2.0), quoted | | |
| Lance rigging in three fabrics; wear; snapped lines | cleanse | moved (→ 0.2.0) | | |
| The gutter junction as the lance's lesson | review §5, cleanse | moved (→ 0.2.0) | | |
| The siege: spiders arrive, spin, wrap doors, cocoon the downed, leave after days | mechanics review, cleanse | moved (→ 0.2.0); the spinning and door-wrap moved (→ 0.1.0) for the ship | | |
| Persistent siege silk and its capped payout | cleanse | moved (→ 0.2.0) | | |
| The ship gift: the traction lance | ship gifts | kept (0.2.0) | | |

### Nest, eggs and trade

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The nest: young trees and rotting hides, silk in the walls, the mother above | sheet §8, sitting record §3 | kept, quoted | | |
| A nest is a cluster, not one object; raid routes and what rings | sitting record §3 | kept | | |
| A nest on every map | sitting record §6 | kept | | |
| A living nest re-lays every twenty to thirty days | sitting record §6 | kept; a second raid needs a long stop | | |
| Finite guardians; the wall does not replace the fallen | cleanse | kept | | |
| Victim gear salvaged from a nest | cleanse | kept in "later" | | A nest that pays in other people's kit: small, and very Jawa. |
| The egg: valuable, inert, perishable, no hatcher, never farmed | sitting record §4, §6 | kept | | |
| The carried-eggs mark; shelves do not broadcast | sheet §7, sitting record §4, cleanse | kept | | |
| The offworld sale route | sitting record §4 | kept in the campaign layer | | |
| "Totally add the black market trader ... planting an egg in their room to hatch in the night" | sitting record §6 | kept in the campaign layer, quoted | | |
| The Hutt Cartel fronts it; a caravan and a broker; prices; the Wildsteam are blind to it | egg market draft §1, §5 | kept in the campaign layer | | |
| The Reckoning and its family; planting; discovery; total deniability; a juvenile hatches as a staged event | egg market draft §2, §3, §5 | kept in the campaign layer | The mechanics review asks him whether it earns its size. | |
| The egg as a free-form weapon | egg market draft §5 | kept in "later" | | |
| The Wildsteam pay to destroy eggs | sitting record §6, mechanics review | kept in the campaign layer | | |
| The mandible bounty | sheet §7 | kept in the campaign layer; mandibles are a takeaway | Not located in source. | |
| The egg broker as a Bazaar tab; its successor, a deadline quest | open questions, fluff cuts | tab lost (cut); quest kept in "later" | | |
| Egg market and caravan ported into the campaign patch; the old economy mod cut | owner cards | kept as a build fact | | |

### Animals and plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| A very thin cast; "silence is doctrine"; every row carries a war or a use | sitting record §0, fauna roster | kept | | |
| The three wars: beetles, mites, themselves | sheet §4b | kept | | |
| Quarrok, the anchor beetle; cut corridors are blind | sheet §4b, fauna roster | kept | | |
| Beetles herded along a route to cut a corridor | sheet §4b, cleanse | moved (→ 0.2.0) | Not built. | |
| Vennick, the egg-mite; "a living treasure map" | sheet §4b, fauna roster | moved (clutch-seeking → 0.1.0), quoted | | |
| Skennet and cravvet, the trace prey | fauna roster | kept | | |
| Sivvern, the trace flier; circling low means mites, means eggs | fauna roster | kept as a real flyer; the "aerial tell" lost as a promise | No scene could tell it from ordinary hunting. | |
| The three donor animals cut here | sitting record §6 | kept (dropped list) | | |
| The living colossus (the morravell) | review §3 | lost (not chosen) | | |
| "They Ate the Colossus": the urraveth's remains | review §5, ruling 2 | moved (→ 0.2.0) | | See above. |
| The titanic battle | open questions | kept in "later", quoted | | |
| Sixteen invented plants in a silhouette brief | flora roster | kept as the roster and as art direction | | |
| Kollavane, the braided canopy tree; vessark, the strangler | flora roster | kept | | |
| Tavrosk, the still-tree | flora roster, sheet §7 | kept; its tapping moved (→ 0.2.0) as the fuel source | | |
| Dulloth, the canopy sealer | flora roster | kept | It is the cover from orbit and the owners' shade in one plant. | |
| Brimlock, "the drunk river, held in flesh" | flora roster | kept, quoted | | |
| Threllick, the root mat; sellith, the gutter weed; varrisk, the reach | flora roster | kept as plants | | |
| Kessaroth, norrveth, sorrivel: the trap, the needle-wand, the bait | flora roster, cleanse | moved (recommended retirement → 0.2.0); `NEEDS HIM` | | |
| The canon trap plant kept low by a campaign patch | sitting record §6 | kept in the campaign layer | | |
| Pellareth, the pale flowers: "a sober ceremony to the death of this biome. No need for new state machine building." | flora roster (his words, 2026-10-07) | kept, quoted | | |
| Fresh and withered blooms as a map of live and abandoned web | sheet §4c | moved (recommended retirement → 0.2.0, unbuilt) | See "the ones I would look at". | Drop it, on his own words. |
| Ruddreth, the nest-bloom on hide-rot | flora roster | kept | The nest's sign at a distance. | |
| Fellome, the plantation's gleanings | flora roster | kept | | |
| Grennick, the creep made visible | flora roster | lost as a mechanic (the creep was deleted); the plant stays | | |
| Brennoth, the margin's tinder | flora roster | kept, quoted | | |
| The six generic donor plants cut here | sitting record §6 | kept (dropped list) | | |

### Rites, the campaign and the pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The Felled Noon | review ruling 4, open questions | kept in "later" (rites tabled; held for the shade model by his card) | | |
| The Cut Cocoon; the testimony rite | review §5, §6 | lost (not chosen) | | |
| The Wildsteam war front, still-burner patrols, bounty boards | sheet §8 | kept in the campaign layer | | |
| The still-burner weapon | sheet §7 | kept in "later" | | |
| No droid enclaves near the web; the convoy story | sheet §8 | kept in the campaign layer | | |
| The old campaign copy of the biome retired at the end paint | open questions | kept as a build fact | | |
| The placement worker kept as it is | open questions, cleanse | kept | | |
| The mutator that seeds owners on other maps | cleanse | lost (recommended for dropping; his to confirm) | | |
| The long arrival letter; the shade-cloth lesson | cleanse | kept in "later" | | |
| Acoustic scanner clues | cleanse | moved (→ 0.2.0) | | |
| The cleanse's signature | cleanse owner pages | kept as the core of 0.1.0 | | |
| Its readings (quiet is sound; sun cripples; refuge is conditional; eggs in hands; water-inside is land) | cleanse owner pages | kept; each is a promise or a control in the design | | |
| Its eight bars | cleanse | kept as history; the twelve promises in the design are the proposal to argue from | | |
| Its four models | cleanse | kept, with the stop as the whole-map unit | | |
| Tickets and switch-offs | cleanse | kept as they stand, except where a feature moved | | |
| The mechanics review's dispositions | mechanics review | kept as history | | |

## Sources read, and the count

Measured after writing: a script counted the table rows and the first words of the "what happened" column; the file
count is the files named below as opened, counted by hand.

Read whole: the sheet; the cleanse's owner pages; the owner answers; the mechanics review's Webwork table (long
cells cut at about 640 characters); the ship-gifts row. Read in large part: the cleanse next-version list (the
"what" of its first twenty-four entries; the rest by the summary on the owner pages); the sitting record (both
rulings tables, sections 0 and 6; not sections 1 to 5 in full, only their headings). Read by heading or by search:
the egg market draft (headings and the seven rulings); the fauna roster (section titles, the sivvern row, the
trace-prey opening); the flora roster (the sixteen rows, each cut at about 430 characters, and the pale-flower
ruling; not its wiring sections); the review (the five outside ideas, the turn-one rulings and ticket table, the
"ruled, unbuilt" list; not its scorecard, roster fill or slate in full); the kit spec (the seven ruled cards; not
the seven mechanics); the roster json (structure and row names); the cleanse definition and ambiguities (searched
for the ship landing and droids), tickets (searched for droids); the open-questions file (its eight "answered"
lines; not the briefings above them); owner cards (the economy-mod card); fluff cuts (searched); the experiences
table. Not read: the cleanse's bars, models, census, review, converge and fixes files; the Designer's `NOTES.md`,
`QUESTIONS.md` and `record.json`; `kits/shokkweave_sole_source_spec.md` (the economy spec the sheet cites as
build-ready: a second reader should check it for ideas with no row here); the campaign mods `EggReckoning` and
`WildsteamEggBounty`.

**20 source files opened, 127 rows**, of which **17 lost**, **14 record a move** (whole or in part), **2 kept, reshaped** and 1 folded into shared machinery.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_webwork.md`, `webwork_fauna_roster_2026-09-23.md`,
`webwork_flora_roster_2026-09-23.md`, `webwork_bedazzle_review_2026-10-02.md`, `kits/webwork_kit_spec.md`,
`rosters/the_webwork.json`.

Hold until the campaign's egg trade and quests are designed for their version, because they are its only
specification: `webwork_egg_blackmarket_2026-09-24.md` and sections 3 and 4 of
`webwork_owner_and_nest_2026-09-23.md` (the nest as a place, the egg and the mark; the rest of that file is
replaced).

Not for deletion: `kits/shokkweave_sole_source_spec.md` (not read by this pass); `design/concepts/Webwork/cleanse/`
(superseded by this design, never applied; it should be re-run from this file, not applied);
`design/RimMandrake/webworks_open_questions_2026-10-22.md` (it holds his card answers at their source); the
validation walk; the Designer's November question and answer files.

Before deleting: the sheet is cited by path from the Greentide's sheet ("read against") and by section from both
rosters, the sitting record and the kit spec. The flora roster is the art pipeline's silhouette brief; its rows
should move into the design folder or the art ledger first, whichever the art seat reads.
