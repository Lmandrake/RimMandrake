# The Wastes: what the rewrite chose, what it lost, and why

Companion to `design/concepts/Wastes/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the overriding
priority"*; and *"always look for solutions that make you say Very Jawa"*. The Wastes is an awkward fit for that
priority on its face, because its frozen sheet bans the wildlife from being the threat and its whole danger is
slow. The cleanse proposal of 2026-11-17 leaned into the slow: its 0.1.0 is a settlement keeping a refuge clean
across an occupied season. This design keeps the refuge (it is his own November answer) and makes it the ship;
keeps the ash storm as the signature; and brings forward the three things in the switched-off list that are
funny, fast and already working: the beetle that trades up, the animals that turn poison into goods, and the
twenty-cell giant that walks through the yard.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, default off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The waste run.** *"Drop it on the Empire — an act of war dressed as sanitation. Does the planet really want
   to declare WAR on the Empire?"* Five destinations, each *"a moral verdict"*, and the only place in any of
   these five biomes where the ship itself is the instrument of the story. It is campaign content in its own mod
   and I left it in "later". Under his lens question "who else hates the Empire and might fight them", this is the
   crew's own answer, and it deserves a look before 0.2.0 is fixed.
2. **The Middenshell in 0.1.0.** The cleanse called it *"the strongest spectacle"* and deferred it because *"it
   does not make the quiet day consequential"*. Under the lens the spectacle is the point. I moved the arrival,
   the crawl, the crushing and the trail in, and left its lure, its tentacle and its corpse-quarry out. It is a
   large test surface and one of its live checks (the dose beside it) failed and was never re-run.
3. **The top-down healing.** *"The Wasteland heals top-down — a walkable crust over a deep that grows hotter.
   Cleaning means making the poison stop moving. An old 'recovered' wasteland is a clean crust over a lethal
   root-vault, and digging where the land looks healed is precisely the mistake."* The best idea in the sheet,
   and it runs on a scale of ages. What a stop can see of it is one loaded root being destroyed and the ground
   getting worse at once; the design keeps that and loses the rest to "later".
4. **Plant-vault ore, "the cursed prize".** A fuel deposit that reopens the wound when mined. His fuel ruling
   makes fuel a reason to stop, and this is the most characterful fuel on the planet. I left it unbuilt and
   cursed, and gave the fuel role to soot bricks and wartshrub, which exist. If the Wastes should tempt a crew
   into doing harm for fuel, this is the row.
5. **The smolderback.** *"A tamed one is a living furnace that heats a shelter all winter and irradiates it the
   entire time."* The cleanse's runner-up. A crew parked in the dark scour to hide is exactly who would bring one
   aboard. 0.2.0 because nothing about it has ever been measured.
6. **The Stenchlands.** *"An unholy glow now rises from it, and the ground sometimes trembles as though it were
   moving or groaning ... It is not alive and not undead, despite the rumors."* A single place, the campaign's
   doomsday clock, and no part of an ordinary stop. Kept in the campaign layer; not in this design's visit at
   all.
7. **The dark scour on the orbital pause list.** I applied his 2026-08-05 dark-tile ruling to it from the sheet's
   own line about light past the terminator. Nothing builds that today. If the scour pauses the search, a cold,
   poisoned, lightless flat becomes one of the planet's real hides, and the Wastes' three families become a
   genuine landing choice. If he did not mean it to, the scour is one step, like the Sump.
8. **"Victims."** His picked experience line and his typed register ruling disagree on the creatures. Asked as
   `NEEDS HIM`.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **The gripper's junk, theft and drops:** next version → 0.1.0. Proven live (7 of 7), and the lens in one beetle.
- **Sloghog bezoars and sootgrazer soot bricks:** next version → 0.1.0. They are the takeaway and the fuel.
- **The Middenshell's body, omen and arrival, crawl and crushing, proximity dose, trail:** next version → 0.1.0.
- **The Middenshell's lure and tentacle:** next version → 0.2.0.
- **The Middenshell's corpse quarry:** next version → later. Nobody kills it in a week.
- **The Deadlight Halo, the Cinderwire and its terminator-only eligibility; the smolderback's heat and the
  ambient-dose aura; the processors cleaning cells; casks, the bay, herd processing of casks, the launch refusal,
  reburial; the Rite of Tipping, evidence requests, containment grant, reburial discovery; brine beds, brine
  shock, plate cracking; the grimewing circling exhumations:** next version → 0.2.0.
- **The timed excretor's sheared bezoars; the isi isi's defensive discharge; a real sealed Junker corpse in a
  sarcophagus; vault-root ore; a native titan pawn:** stayed "later" from the cleanse's "next version". Not moves.
- **A finite hoard of salvage buried before arrival:** next version → 0.1.0. The cleanse kept burial and reveal of
  what is already on the map and deferred seeding old finds as *"a prospecting system beyond the selected
  signature"*. For a scavenger crew the prospecting is the stop; without a seeded hoard a storm can only reveal
  what an earlier storm buried.
- **The occupied-season bar:** the cleanse required *"a complete occupied season"*. Here the visit is the unit: a
  stop that sees two natural storms.
- **New, not in any source:** the ship as the refuge of his November answer; the three families as three
  different stops with different cover and different stop lengths; ash as one step of cover while it blows; the
  dark scour on the orbital pause list; soot bricks rendered to ship fuel; the Middenshell steered at a siege
  camp by stacking waste (a reading of its built lure); the Empire's camp dosed by the ground it chose.

## Every idea, row by row

Source names: *sheet* = `biomes/wastes.md`; *cast bible* = `biomes/wasteland_survivor_cast_2026-09-28.md`; *roster
json* = `biomes/rosters/wastes.json` (all under `design/Jawa/worldbuilding/`); *cleanse* =
`design/concepts/Wastes/cleanse/`; *walk* = `design/validation_walks/RimMandrake/Wastes.md`; *owner answers* =
`design/RimMandrake/designer_codex_2026-11-09/Wasteland/ANSWERS_OWNER.md`; *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *experiences* =
`design/RimMandrake/biome_experiences_2026-10-20.md`; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*ship gifts* = `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`; *Warscar turn three* =
`biomes/warscar_turn3_development_2026-09-30.md` (for the screen's reach); *flora defs* =
`src/RimMandrake/Wastes/Defs/ThingDefs_Plants/RM_WastesFlora.xml`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "No outlet"; "a just-lost sunset, flickering with wrathful lightning" | sheet header, §9 | kept, quoted | | |
| "Where rivers come to die and nothing ever leaves ... The land is the monster, and the creatures are its victims." | walk, experiences, mechanics review | kept, quoted; its last clause is `NEEDS HIM` | | |
| "The land itself is the only danger ... You can sleep here without a watch. The ground will still be killing you while you do." | sheet header | kept, quoted | It is the answer to both "what forces them out" and "what lets them stay". | |
| Read against the Abyss: crag is the relief, wasteland the drained flat between | sheet header | lost from this design | A map-painting rule for the end paint. | |
| Read against the arid shrubland (the opposite inversion) | sheet header | lost from this design | Cross-biome framing; belongs in the consolidation. | |
| Measured tiles, arcs, the three families' climate table, the stale-region amendment | sheet §0 | kept, reshaped: the three families are kept as three kinds of stop; every count is lost | A tile count is never evidence; the planet is painted at the end. | |
| One biome, varied only by mutators and inhabited injections | sheet §0 | kept | | |
| The salt plains are dead river ends | sheet §0 | kept as one clause | | |
| The war-legacy split: this is the poisoned legacy; anomaly entities never here | sheet §0, ban 1 | kept | | |
| Where the old war's weapons were used and left; the place you throw what nobody wants | sheet §1 | kept, quoted, without naming who fought | The Warscar's partition rule is a good habit here too. | |
| "It is not they who did this" | sheet §1 | kept in spirit | | |
| Three drains: hydrological, atmospheric, historical | sheet §2 | kept, compressed to one sentence | | |
| Concentration without circulation; the crags kill the wind | sheet §3 | lost | Planetary physics a stop never sees. | |
| The seven "always true" lines | sheet §5 | kept; three quoted | | |
| "Past arc ~100 the only light is the stormwall's glow ... Navigation trivial; morale not." | sheet §5 | kept, quoted; used as the basis for the scour's dark | | |
| Ban: wildlife is never the headline threat | sheet §6 | kept, quoted | | |
| Ban: no unmarked wildlife | sheet §6 | kept | | |
| Ban: no rain; ban: nothing spoilage-dependent | sheet §6 | kept | | |
| Ban: plasma storms only in the terminator pockets | sheet §6, §4b | kept | | |
| Art theme: glow on one horizon; salt-white basins; "horizons of nothing, then one enormous thing" | sheet §9 | kept, quoted | | |
| Sound: wind over crust, Geiger-like clicks, the tremor near the Stenchlands | sheet §9 | kept as art direction | | |
| The 1,126-tile roster file: fifteen fauna rows, nine flora, five owed bodies, 49 evictions | roster json | lost from this design | Superseded by the cast bible's full replacement. | |

### Dose, storms and the ground

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The danger is priced in dose: ground, air, water | sheet §5 | kept | | |
| Radiation and pollution, ridden mostly on the Biotech pollution mechanism | sheet amendment (5) | folded into shared machinery | | |
| "Keeping a habitable refuge leads..." | owner answers | kept, quoted; the refuge is the ship | A landed ship is a refuge by construction, and its upkeep is the stop's daily work. | Hold the colony reading: 0.1.0 is then a settlement nobody in the campaign founds. |
| "Reliable rough comparison: landscape observation distinguishes safer from worse exposure..." | owner answers | kept, quoted | | |
| A waste contract ends with its term; physical pollution persists | owner answers | kept (with the tipping trade, 0.2.0) | | |
| "The vegetation is the dosimeter"; the lushest ground is the deadliest; locals camp where nothing grows | sheet §4 | kept, quoted; made the landing's first lesson | The inversion a desert crew gets exactly wrong. | |
| Radmoss follows the dose that actually harms; hidden stock cannot invent a difference | cleanse | kept as a promise's control | | |
| "Plants clean; animals only refine" | sheet §4 | kept | | |
| Healing by sequestration, top-down; the clean crust over a lethal vault | sheet §4 | kept in "later", quoted in the list above | Ages, not weeks. | |
| Destroying a loaded root releases what it bound, once | cleanse | kept | The part of sequestration a stop can see. | |
| Ash storms: "blinding, abrasive, conductive — and radiologically live" | sheet §4b | kept, quoted | Also the source for how the place wears on the ship. | |
| "The storm redraws the danger map"; re-survey after every storm | sheet §4b | kept, quoted | | |
| Storms exhume and bury; the exhumation lottery | sheet §4b, §7 | kept, quoted | | |
| The Wastes as the one place the fixed map is allowed to regenerate | sheet §4b | kept, quoted | | |
| Ash exhumation reuses the moving-dunes mechanism | sheet amendment (5) | folded into shared machinery | | |
| Ash moves old contamination as well as adding fallout | cleanse | kept | | |
| Cinderfelt, the fresh-fall marker | cast bible §6 | kept | | |
| The Deadlight Halo: a glow, ambient dose raised | sheet §4b, Owed | moved (→ 0.2.0) | A second storm; the first has to work first (its dose check failed live). | |
| The Cinderwire: "EMP, burn, dose and burial in one weather event" | sheet §4b, Owed | moved (→ 0.2.0) | | |
| Storm names picked by card | sheet, Owed | kept | | |
| Preservation: nothing rots; "you may not want what you left here too long" | sheet §5, §7 | kept, quoted | | |
| Caches soak up the ground they sit in; radiotrophs colonise them | sheet §5 | lost as a mechanic | Not built; a week is too short for it. | A slow taint on outdoor stockpiles: small, and one more thing dosing the crew. |
| Native contamination laid once, with cleaner ground left to build on | cleanse | kept | | |
| The pollution account: every outside write enters once; cleanup is not undone | cleanse | kept as a build rule | | |
| Wastepack storage by climate family; freezers | cleanse | lost | A colony's waste logistics. The ship flies its waste away or does not make much. | |
| The occupied-season whole-map model | cleanse | lost | Colony scale. | |
| The other models (situations, exposure geometry, food and rot) | cleanse | kept | | |

### Animals

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Survivors, not sufferers: "ugly warty life that was already tough enough..." | sheet amendment (1), cast bible | kept, quoted | | |
| English ugly-tough names, never invented-exotic, never Star Wars | sheet amendment (1) | kept | | |
| The whole donor cast replaced outright | sheet amendment (2), cast bible | kept as a build fact | | |
| Scumrat, slagmole, scabspinner, boilhide, middenbeetle, gristleswarm, soot gristleswarm, gravelgut | cast bible §2 | kept | | |
| The gravelgut's sorted pebbles, kicked apart to read what is buried | cast bible §2 | kept, quoted, as flavour | No mechanic was ever owed. | |
| The middenbeetle's caravan lines; "it never comes back empty-handed" | cast bible §2; mechanics review | kept (it is the gripper) | | |
| Gripper theft: arrives with junk, swaps up, drops when hurt, never steals once tamed | mechanics review, cleanse | moved (→ 0.1.0) | | 0.2.0: the cleanse's view, that a thief is not in "the land is the monster". |
| The excretors: "a kept herd is a slow refinery" | sheet §4 | kept, quoted | | |
| Sloghog and its bezoars | sheet amendment (3), cast bible §3 | moved (→ 0.1.0) | | |
| Sootgrazer and its soot bricks | cast bible §3 | moved (→ 0.1.0); used as the fuel source | | |
| Processors un-pollute the cell they graze | cast bible §3, cleanse | moved (→ 0.2.0) | A second sink on the pollution account; prove the account first. | |
| The timed excretor that is sheared for bezoars | cleanse | kept in "later" | A third bezoar route. | |
| Smolderback, the living furnace | sheet §4, cast bible §3 | moved (→ 0.2.0), quoted | | |
| "A warm boulder in the black country means one passed" | sheet §4 | kept as a moment (0.1.0, scenery) | The sign is free; the animal's effect waits. | |
| Solitary spacing by heat | sheet §4, cast bible | kept (spawn alone, wander alone) | | |
| The brine batteries: "the pool you want to mine has an owner, and the owner is a capacitor" | sheet §4 | moved (beds → 0.2.0); the isi isi's discharge is later | | |
| Brineleech and sparkcrab, label-only renames | sheet amendment (3), cast bible §5 | kept as a build fact | | |
| The Middenshell: twenty cells wide, never hostile, proximity-dosed | sheet amendment (3), cast bible §4 | moved (→ 0.1.0), quoted | | |
| "Its walk is the danger"; the destruction wake | cast bible §4 | moved (→ 0.1.0) | | |
| The omen: tremor, dust, loose metal pointing at an edge | mechanics review, cleanse | moved (→ 0.1.0) | | |
| It avoids gravship parts; its tentacle excludes gravship objects | cleanse | kept; `NEEDS HIM` | | |
| Its route bends to waste stockpiles | cleanse | moved (→ 0.2.0) | | |
| Its corpse as a permanent bezoar quarry; vitrified bezoars | sheet amendment (3), cast bible §4 | kept in "later" | | |
| The width is a ruling; an engine ceiling below twenty is an escalation, never a silent shrink | cast bible §4 | kept as a build rule (it was built as a building that crawls) | | |
| Grimewing: a real flyer; circles fresh exhumations | cast bible §9 | kept; the circling moved (→ 0.2.0) | Not built. | |
| Kroffa milk, frethik eggs, scumslider | mechanics review, roster json | kept as plain animals | | |
| Raw kroffa-milk mood bonus | cleanse | lost (recommended for dropping; his to confirm) | | |
| The unadapted dead: rib-vaults, "the traditional ash-storm shelter (with the traditional price...)" | sheet §4 | kept, quoted | Whether a rib-vault is a real roof is `UNMEASURED`. | |
| Dead sarlacc throats | sheet §4, §8 | kept in the campaign layer | | |

### Plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Radmoss (the dosimeter lawn) | cast bible, flora defs | kept | | |
| Vault-root trees | cast bible, flora defs | kept | | |
| Plant-vault ore, "the cursed prize" | sheet §7, cleanse | kept in "later", quoted | See "the ones I would look at". | A fuel economy that reopens the wound: medium, and the most Junker thing a Jawa could do. |
| Scumgrass and tall scumgrass | cast bible §6 | kept | | |
| Pusberry; special harm from eating it raw | cast bible §6, cleanse | kept; the special harm lost (recommended for dropping) | | |
| Boilbulb | cast bible §6 | kept | | |
| Wartshrub, whose harvest is chemfuel | cast bible §6, flora defs, mechanics review | kept; named as a fuel source | | |
| Scorched stars; the vanilla grey grass, polux tree and toxipotato | cast bible §1 | kept | | |

### Salvage, waste and people

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "War salvage priced in dose"; "ground nobody can live on is ground nobody has stripped"; "the prize compounds" | sheet §7 | kept, quoted | | |
| The dive structure: suits, scrubbing drugs, the dose budget as timer | sheet §7 | kept in "later" | Not built as a system; the dose is the timer already. | |
| Warcasket sarcophagi | sheet §7, mechanics review | kept, quoted; a real sealed corpse inside is owed | | |
| Warcaskets as a suit class for every hostile terrain; "a primitive tank around a person" | sheet amendment (6) | folded into shared machinery (`Warcasket`) | | |
| The wreck set | mechanics review, fluff cuts | kept (it is the shared wreck scatter) | | |
| A finite hoard buried before arrival | cleanse | moved (→ 0.1.0) | Not built. | Next version: storms then only re-bury and reveal the wreck scatter. |
| Salt, glass, brine minerals | sheet §7 | kept; the beds are 0.2.0 | | |
| Radiothermal heating | sheet §7 | moved with the smolderback (→ 0.2.0) | | |
| The tipping fee: "the one biome with an income stream attached to its awfulness" | sheet §7, §8 | moved (→ 0.2.0), quoted in spirit; `NEEDS HIM` on its shape for a ship | | |
| The Rite of Tipping, evidence, grant, illegal reburial | mechanics review, cleanse | moved (→ 0.2.0) | | |
| Waste casks, the cask bay, the launch refusal | sheet amendment (6), ship gifts, mechanics review | moved (→ 0.2.0) | The bay is the named ship gift. | 0.1.0: the gift arrives a version sooner and brings a cargo system with it. |
| Cargo-bay waste ecology allowed emergently | sheet amendment (6), ship gifts | kept (0.2.0) | | |
| The waste run and its five destinations | sheet §10, mechanics review | kept in the campaign layer | See above. | |
| The throat cask | mechanics review, fluff cuts | kept in the campaign layer | | |
| The Stenchlands (the Glowing Throat, the Pit): not alive, not undead; the doomsday clock | sheet §8, §10, amendments | kept in the campaign layer | | |
| The Junkers: crude sovereigns, the toll, digging up the very plants that seal the poison, institutional denial | sheet §8 | kept in the campaign layer; quoted | | |
| "Junker corpses are more common than anyone else's" | sheet §5 | kept, quoted | | |
| Wildsteam and Deepwater; "the players are the only hands all three can use" | sheet §10 | kept in the campaign layer; quoted | | |
| Roads of shame, toll gates, buried crimes | sheet §8 | kept in the campaign layer | | |
| The mutator and injection palette by family | sheet §8 | kept in the campaign layer and the end paint | | |
| The ship gift: the waste cask bay | ship gifts | kept (0.2.0) | | |
| The aerosol screen works on the ash fall | Warscar turn three | kept | | |
| The dead brine-deposits toggle | fluff cuts | lost (deleted) | | |
| Acoustic scanner payload | cleanse | moved (→ 0.2.0) | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (ash moves contamination; read changed ground; keep a refuge) | cleanse owner pages | kept as the core of 0.1.0, with the ship as the refuge | | |
| Its eight bars | cleanse | kept as history; the twelve promises in the design are the proposal to argue from | | |
| Its defaults ("nothing leaves" means no natural outlet; bare ground is not a safety certificate; "off" stops callbacks) | cleanse owner pages | kept | | |
| Regime tests on scratch tiles at each family's arc | cleanse | kept | | |
| Tickets and switch-offs | cleanse | kept as they stand, except where a feature moved | | |
| The mechanics review's dispositions | mechanics review | kept as history | | |
| The must-be-true list | walk | kept | | |

## Sources read, and the count

Measured after writing: a script counted the table rows and the first words of the "what happened" column; the file
count is the files named below as opened, counted by hand.

Read whole: the sheet; the cleanse's owner pages; the owner answers; the walk's north star; the ship-gifts row.
Read in large part: the cast bible (sections 1 to 6 with stat sketches, def notes and art notes skipped; the
opening of section 9; not sections 7 and 8); the cleanse next-version list (every entry, long lines cut at about 350
characters); the mechanics review's
Wasteland table (long cells cut at about 560 characters). Read by heading or by search: the roster json (its
structure and row names); the flora defs (def names and the chemfuel harvest only); fluff cuts (searched);
the experiences table; Warscar turn three (for the screen's reach, two lines). Not read: the cleanse's definition,
tickets, ambiguities, bars, models, census, review, converge and fixes files; the Designer's `NOTES.md`,
`QUESTIONS.md` and `record.json` for the Wasteland; `src/RimUtinni/WasteRun/` and its design
(`dungeons_arc_spec.md` §2.6, cited by the sheet); the items for the Wasteland's sittings
(`WASTELAND_BEDAZZLE_SITTING_1`, `WASTELAND_GPT_ENRICHMENT_1`, `WASTELAND_MECHANICS_BUILD_1`), which hold his
typed rulings at their source and which I quote only through the sheet and the cast bible.

**12 source files opened, 117 rows**, of which **9 lost**, **20 record a move** (whole or in part), **1 kept, reshaped** and 3 folded into shared machinery.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `wastes.md`, `rosters/wastes.json`.

Hold until its art is all installed, because it is the art commission and the accepted name map:
`wasteland_survivor_cast_2026-09-28.md`.

Before deleting `wastes.md`: its sections 8 and 10 (the Junkers, the Stenchlands, the faction triangle, the five
destinations of the waste run) are the campaign's only statement of those ideas outside the waste-run mod. Move
them to wherever the campaign layer reads first.

Not for deletion: `design/concepts/Wastes/cleanse/` (superseded by this design, never applied; it should be re-run
from this file, not applied); the validation walk; the Designer's November question and answer files.

Before deleting: the sheet is cited by path from the Abyss and arid shrubland sheets ("read against") and by
section from the cast bible.
