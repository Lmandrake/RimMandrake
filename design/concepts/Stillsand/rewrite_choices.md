# The Stillsand: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A different agent from the one that wrote this page and the design read the sources again, starting with the ones
the first pass read in part or not at all, and checked each idea in them against the rows below.

**Rows added: 86**, in the table "Added by the second reader" at the end of "Every idea, row by row". Three of
the first pass's rows were corrected in place and say so (the sun lance, the solar still, the roads ban).

**The three most valuable things the first read missed.**

1. **The hull wear was in the sources, and the frame is built.** The first design said *"No shared system for
   hull wear was found in `src/`"* and gave drift no source. `src/RimUtinni/ShipShields/` wears a landed ship in
   extreme heat and in blown sand, with his thermal veil and light screen as the answers (2026-09-02). The frozen
   sheet says of anything that stands here: *"a structure is buried on its windward face and undercut on its
   lee"*, and, as if for this crew, *"crawler-scale machines are the only settlements that make sense in a
   landscape that buries fixed ones."* A kept idea already names the ship as a drum: the krayt attack is
   *"weighted up by... vibration (drilling, a landing ship, the thumper)"*. With these came two doubts, both
   flagged: the built heat line is 58 °C and much of this biome is measured cooler, and the dune gale carries no
   falling sand, so the frame cannot see the biome's own storm.
2. **Two of his own card picks were on the "recommended for dropping" list, and one is half the ship's gift.**
   The cleanse of 2026-11-17 recommended retiring the sun lance and the mirage. He took both by card on
   2026-09-30. The lance and the solar still are also the Stillsand's answer on record to his question of
   2026-09-24, *"how can this biome uniquely add something to the ship?"*
3. **What a firefight and a gale do here.** *"Fighting here starts a clock. Kill, loot fast, leave. A battle left
   standing becomes a zuurrik bloom"*, and *"The gale blinds the swimmers... A player who learns this crosses the
   Stillsand in the gale."* Both are built, both were ruled in, and neither was in the section on the Empire.

Close behind: his word of 2026-10-20 that put roads back across the Stillsand (*"For now just replicate where we
had roads before."*), which the first design's premise quoted the old ban against; the piinnok, the watcher whose
lenses *"turn to follow"* and all sink when something large passes; the dead sandcrawler's note, *"We ran her
until the sand had her. If you find her, start her once before you take her apart. She will know you."*; fine
sand as *"a trade commodity"* by his card, which is what a crew pays for fuel with; and *"move in the shadow of
your own landed ship."*

**What changed in the design, and why.**

- *Hull:* rewritten onto the built shield frame; the false sentence that no hull system exists is deleted; heat,
  blown sand, drift and large animals each carry their source; one proposal of the second reader's own (ollim
  cladding) is flagged as such. The two cut wears (*the dunes take the ship*, card of 2026-09-30; gale abrasion,
  cut 2026-10-23) stay cut and are `NEEDS HIM` 2. No typed words of his exist for either cut; the question says so.
- *Scope:* the lens kit (solar still and sun lance) is in 0.2.0 as the ship's gift; the sun lance is off the
  dropping list; the piinnok is named in 0.1.0; the two found rites of the Jawa's own faith are in "later".
- *Roads:* the premise sentence now gives the sheet's ban and his later word together.
- *Cover and the Empire:* the gale keeps swimmers down; the zuurrik clock; raids that *"pick the side without a
  wall"*.
- *Fuel:* who sells (caravans exist because the vaalok was built) and what the crew pays with (sand).
- *Power:* the ship's solar is no longer "unmeasured": an older pass read the code. It is still unwatched in play.
- *Lines carried in:* nine, among them *"The light is a fixed condition, like the pressure at the bottom of a
  sea"* and the gaanok's *"patient, visible, and correct."*
- *Whose word wins:* the cleanse's lines were checked against his dated cards; the lance and the mirage fall to
  earlier picks of his. **The locked tree is not edited.** Its root describes a colony that stays and names the
  workshop; the design's status header says so, for a later Designer run to reconcile.

**Third run, 2026-11-18: the roster file read to its end.** The second reader's reading of
`rosters/dune_sea_deep_desert.json` had each eviction's reason cut at about 95 characters. A third run read the
file whole (943 lines: 110 evictions, 26 animals, 7 plants, 11 purged plants, 11 owed new things, 6 confidence
notes). The reading reached each file's last line; the longest line in the file is 690 characters and the reading tool shows 2,000 characters of a line, so no entry was cut. **Rows added: 28**, in the table "Added by
the second reader: the roster file read to its end"; two of the second reader's rows corrected in place.
Recovered: his *"I meant pick one arid home."* (2026-09-22), which is where the one-home rule was first written
and which the cut had hidden; his four sheet notes of 2026-10-04 in full, and the second half of the vozzik's
move (*"This should be moved to the Rust Cathedral Biome."*); his eye on the giant mushroom (2026-09-20); the
measure behind the size law and the predator law (*"nothing charges out of a bush; there is no bush"*); and
three flags nobody closed (two eye tests left to him; the ban on night habits never checked; a dunealisk the
file both refuses and lists). One false statement on this page came from the cut and is corrected: the korrum
is not on this roster. The design did not need a repair: it names neither the korrum nor the dunealisk.

**Measured counts** (script: `design/RimMandrake/biome_recheck_row_check_2026-11-18.py`, and the readers' own
source lists checked against disk): **299 rows** (185 from the first read, 86 added by the second reader, 28 by
the third run); **31 lost**, **19 moved** and 5 more that record a move in part, 11 kept and reshaped, 1 folded
into shared machinery, 237 kept. **Sources: 15
read to the end, 9 read in part, 18 not opened.** Read to the end: all seven files this page lists for deletion
(the roster json by the third run, with nothing cut) and the cast bible it says to
hold; the tree's `root.md`, `sheet.md` and `journal.md`; the cleanse's owner pages; his answers and the questions
he was shown; the ship-gifts item. Read in part, at this biome's sections: the rites pass and register, the
mechanics review, the fluff cuts, the watcher pitch, the shield rulings, the dunes design, the gale's weather def,
the lens-chain item. **Not opened by the second reader:** the tree's `tree.json`, `scenes.json`, `record.json`,
`plan.md`, `log.md`, `coverage_verdict.json` and stage-two and stage-three reviews; the cleanse's next-version
list, definition, tickets, ambiguities and models; the validation walk; the rehearsal's notes, questions and
record; and the Stillsand's forty-odd build items other than the one named. Every one of those stays on disk; an
idea that lives only in them has not been checked by this pass.

DELETE-READY: yes

Restated 2026-11-18 after the roster was read to its end. The line covers seven files in
`design/Jawa/worldbuilding/biomes/` and nothing else: `dune_sea.md`, `deep_desert.md`,
`stillsand_bedazzle_2026-09-27.md`, `stillsand_bedazzle_review_2026-09-29.md`,
`stillsand_turn3_development_2026-09-30.md` and `stillsand_roster_fillout_2026-09-27.md` (read to the end by the
second reader, on that reader's statement above) and `rosters/dune_sea_deep_desert.json` (read to the end by the
third run, nothing cut; every idea, ruling and owner word in it has a row). The roster is cited by path in
comments in `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Stillsand.xml` and
`src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Siidda.xml`; those lines should point at this page before the
file goes. The cast bible
stays held as that list says. What the same list says to do first still stands: move the sarlacc carve-out
paragraph of `deep_desert.md` to the sarlacc's design, and repoint the tree's `sheet.md` and the build items that
cite the two sheets by section.

Companion to `design/concepts/Stillsand/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head, adapted only to their parent desert biomes along roads
trading scrap"*; *"anything that takes seasons to observe will simply be missed"*; for 0.1.0 and 0.2.0 the *"OMG did
you see that?"* of Jawa meeting alien creatures at close range is *"the overriding priority"*.

The Stillsand is the odd one under that lens, because it *is* desert. I read the difference from the sources
themselves: the Jawa's desert is the roads, and this is *"the distance between places"* with *"no roads through the
deep dune"*. So the crew arrives confident and is wrong, which is a different joke from every other biome's and I
think the right one.

Almost everything in the Stillsand is built (the census marks only the one-sun rule and four cut features absent).
So the choices here are not what to build but what a first version has to prove. The cleanse proposal of 2026-11-17
proved a quiet loop (cross, secure a cave, resupply) and switched off nearly every creature event and the whole
workshop. This design keeps its loop and its workshop deferral, and differs in one direction: the events a crew
can meet in a week come back, the sand busters into 0.1.0 and the rest into 0.2.0, because under the lens they are
the biome.

His four rulings of 2026-11-18 (3:10 PM PST) are applied, not asked: the stop length is stated as an outer edge
(about a month, the plainest on the planet); cover from orbit is stated (none, except inside a dune gale); fuel is
stated (emergency only; salvaged cylinders; bought from other Jawa); and the wear on the hull is stated from the
sources (the sun, and drift).

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The adopted root's last sentence.** The pipeline holds, as this mod's validated root, *"Learning to live here
   uses sunlight and desert resources to make glass and lenses, cook food and recover water."* His own words asked
   for it (2026-09-30: *"the very fine sand of this region is extremely high quality and can be smelted into a fine
   glass fit for lenses. The lenses can be made into high performance solar stills and ovens."*). It is all built.
   The cleanse deferred it and so do I, to "later", because a furnace, a bench and a still are what a crew builds
   when it is staying. This is the largest thing the lens takes out of the Stillsand's first two versions. If he
   wants one piece forward, the solar still is the one a ship's crew would carry aboard.
2. **The dunes take the ship.** *"A landed gravship is the largest windward obstacle in a thousand kilometres...
   Parked long enough, the ship starts becoming part of the buried record."* And the landing thump as *"the loudest
   drum on the map."* He put it out by card on 2026-09-30. On 2026-11-18 he ruled that every biome wears on the hull
   and that the answer is in the sources. This is the source's answer. Lost; asked as `NEEDS HIM`.
3. **The Return.** *"Believers carry water out to it in eggs, skins and still-flasks and pour it into the sand in a
   line toward the star. Within hours the sand answers: a ring of pale rose-and-bone hourbloom opens around the
   stone."* He said *"I like your religious implication of a ritual here."* Built. It is in "later" with the whole
   water ledger because it belongs to people who live here and keep faith here. The bloom itself takes hours, not
   seasons, and could be seen in a stop.
4. **The mirage.** *"A heat-struck pawn can break into chasing the water: it walks toward the mirage until rescued
   or collapsed."* The cleanse recommended retiring it as a second heatstroke. I moved it to 0.2.0 instead: it is
   built, he took it by card on 2026-09-30, and a passenger wandering off after water that is not there is exactly
   the slapstick he asked for.
5. **Travel thirsty** (swimmers choosing the wettest body). *"Water cools you, and water makes you prey. It is the
   biome's cruellest arithmetic."* Out by his card; the pipeline's own reconciliation records it as a "does not".
   Lost, rightly, and the line deserved a mention.
6. **The gaanok, the follower.** *"It simply appears on the horizon behind a caravan and walks, at exactly the
   caravan's pace, for days. It is doing arithmetic."* Kept in 0.1.0, and the census says what is built is an
   ordinary slow predator. The following is the animal. I have written it as owed.
7. **The giant's shade as the road.** *"A caravan that stays in the shade of a walking mountain travels; a caravan
   that does not, does not."* His second-ranked marquee. On the map the moving shade is in 0.1.0; crossing the
   *world* in it is "later", and for a crew with a ship it may never matter.
8. **"A machined ochre surface under a star that has not moved since the world began."** The physics of why (the
   wind that never turns, the transverse dunes, the hard green line where the tract ends) is world lore and mostly
   lost from this design. The compass survives in one sentence.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **Sand-buster eruption:** next version → 0.1.0. His first-ranked marquee (2026-09-27), built, and set off by
  exactly what a salvage crew does.
- **Bone harps on the skeletons:** next version → 0.1.0. Built sound on a landmark that is already in; his poster
  image.
- **Gale, carry and return, and what the gale uncovers:** next version → 0.2.0.
- **Muurrok visit and mirror beam:** next version → 0.2.0. His typed yes.
- **Thumper; krayt horn:** next version → 0.2.0. The thumper is how a small crew turns the sand on a larger enemy.
- **Brood mound; zuurrik:** next version → 0.2.0.
- **Geophone; the swimmer drawn by fishing; singing dunes:** next version → 0.2.0.
- **Glare-blind and goggles:** next version → 0.2.0. The Jawa are exempt by his ruling, which is half the joke.
- **Mirage:** recommended retirement → 0.2.0. See above.
- **Scanner readings:** next version → 0.2.0. A ship part.
- **Stayed "later" from the cleanse's "next version":** the whole glass, lens, oven, still and brine workshop; the
  Debt, the Return, the pour, the wet line, the hourbloom and the wringing still; corpse history; the campaign's
  den quest, sarlacc seep and three cave kinds; loomma dung seeding. Not moves.
- **Kept as the cleanse recommended (retire):** sun lance, delayed horizon arrivals, extra fossil scatter, cooling
  draught, the legacy heat regime.
- **Forty-colonist harbour:** first version → later. **The full-season walk:** play testing, no part of any version's passing.
- **New, not in any source:** the Jawa's confidence as the joke; the Empire's probe as a droid the sand ignores
  and its troopers as water the sand wants (a reading of the built rule that swimmers skip bodies with no water);
  the thumper used against a siege; a gale as the biome's only cover from orbit (a reading of his partial-cover
  ruling against the gale's own dim sky); buying fuel from Trade Moot crawlers.

## Every idea, row by row

Source names: *dune sheet* = `biomes/dune_sea.md`; *deep sheet* = `biomes/deep_desert.md`; *bedazzle* =
`biomes/stillsand_bedazzle_2026-09-27.md`; *review* = `biomes/stillsand_bedazzle_review_2026-09-29.md`; *turn
three* = `biomes/stillsand_turn3_development_2026-09-30.md`; *cast bible* =
`biomes/stillsand_bedazzle_cast_2026-09-30.md`; *fill-out* = `biomes/stillsand_roster_fillout_2026-09-27.md`;
*roster json* = `biomes/rosters/dune_sea_deep_desert.json` (all under `design/Jawa/worldbuilding/`); *tree* =
`root.md`, `sheet.md`, `journal.md` and `stage2_edges.md` in `design/concepts/Stillsand/`; *cleanse* =
`design/concepts/Stillsand/cleanse/`; *walk* = `design/validation_walks/RimMandrake/Stillsand.md`; *owner answers* =
`design/RimMandrake/designer_codex_2026-11-09/Stillsand/ANSWERS_OWNER.md`; *fluff cuts* =
`design/RimMandrake/fluff_cuts_2026-10-23.md`; *experiences* = `design/RimMandrake/biome_experiences_2026-10-20.md`;
*campaign lore* = `design/Jawa/reconciled_lore/01_campaign.md`. Added by the second reader: *shield rulings* = `design/Jawa/proposals/ship_shields_deep_design.md` and `src/RimUtinni/ShipShields/`; *ship gifts* = `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`; *rites pass* = `design/Jawa/biome_rites_pass_2026-10-01.md` and `design/Jawa/salvation_rites_2026-10-01.md`; *watcher pitch* = `design/RimMandrake/watcher_creatures_pitch.md`; *mechanics review* = `design/RimMandrake/special_mechanics_review_2026-10-22.md`; *biome def* = `src/RimMandrake/Stillsand/Defs/BiomeDefs/` and `Defs/WeatherDefs/RM_DuneGale.xml`; *owner ledger* = his recorded words and cards, read with `src/RimMandrake/rimflow/owner_rulings.py`; *dunes design* = `design/MOVING_DUNES_DESIGN.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "A corrugated ochre plain that goes on past every horizon, under a star that has not moved in the history of the world" | dune sheet §1 | kept, quoted | | |
| The Dune Sea and the deep desert are regions of one biome | dune sheet header; deep sheet header; bedazzle rulings | kept, quoted | | |
| Emptiness is a texture; the absence has to carry the weight | dune sheet intro | kept | | |
| "Time does not pass": no night, dawn, season or moving shadow | dune sheet intro, §1 | kept | | |
| Your shadow never changes length | dune sheet §1 | kept as the fixed sun | | |
| "The standing crop of this biome would fit in a bucket" | dune sheet §1 | kept, quoted | | |
| The sand dotted with glass nubs | dune sheet §1, §4 | kept | | |
| A shape on the horizon large enough to be mistaken for terrain | dune sheet §1 | kept (the oommok) | | |
| It ends at a hard green line with no gradient | dune sheet §1, §2, §9 | lost | World painting; one map does not show it. | One sentence in a world document. |
| Why the wind never turns; pure transverse dunes; no star dunes or barchans | dune sheet §2 | kept, reshaped: one sentence (the landscape is a compass); the mechanism lost | World physics. | |
| The dune grain as a compass; how the tribes navigate | dune sheet §2 | kept | | |
| Dayside lush is a line, never a region | dune sheet §2 | lost | Another biome's rule. | |
| Unlimited light, no water, no night, a wind that never changes | dune sheet §3 | kept | | |
| Flora is buried; only its optics show; nothing green, nothing leafy | dune sheet §4, §6 | kept | | |
| Bright white is the dayside's pigment | dune sheet §4 | kept as art direction | | |
| Every organism has a sun-face and a shade-face | dune sheet §4 | kept as art direction | | |
| No circadian clock; life is event-driven and dormant by default | dune sheet §4 | kept: "the player is the detonator", quoted | | |
| Bodies are enormous or grain-scale; depth passes at any size | dune sheet §4, §6 amendment | kept | His card of 2026-09-27. | |
| Giants carry the only moving shadows, with an ecology in them | dune sheet §4 | kept | | |
| Following a giant is how you cross | dune sheet §4; bedazzle §4.2 | kept on the map; world-map crossing later | A ship does its own crossing. | |
| No ambush from cover; subsurface or attritional hunting only | dune sheet §4 | kept (swimmers; the gaanok) | | |
| Always true: no water of any kind; anything buried is preserved; density absurdly low | dune sheet §5 | kept | | |
| "A reviewer's instinct to add one more thing is the defect" | dune sheet §5; bedazzle §1 | kept as the first promise's control | | |
| The hard bans of the dune sheet | dune sheet §6 | kept as rules | | |
| No fire: there is no fuel | dune sheet §6; deep sheet §6 | kept, quoted as the fuel answer | | |
| No corroded ruins: wreckage is scoured bright | dune sheet §6 | kept, quoted | | |
| No roads through the deep dune | dune sheet §6 | kept, reshaped (corrected by the second reader): quoted as the sheet's ban, with his later word that put the roads back | Owner, 2026-10-20: *"For now just replicate where we had roads before."* | |
| Solar power at full uptime forever; "infinite power in exchange for infinite logistics" | dune sheet §7; bedazzle §4.5 | kept as a consequence of the pinned sky; the power-station colony lost | Colony fantasy. | A landed-ship power bonus: small, needs the ship's power read. |
| Optical-grade biosilica | dune sheet §7 | kept as a thing to take away | | |
| Giant mass: hide, plate, tallow, bone | dune sheet §7 | kept; tallow cited for fuel | | |
| Perfect preservation; pristine buried ruins | dune sheet §7; deep sheet §7 | kept (caches, wrecks); cave keeping kept | | |
| "Sightlines. You can see anything coming from an hour away. So can it." | dune sheet §7 | kept, quoted as the answer on cover | | |
| "The deep dune kills by absence" | dune sheet §7 | kept, quoted | | |
| A hull, mast or wall emerging from a dune face | dune sheet §8 | kept (wreck field; gale uncovering in 0.2.0) | | |
| Sandcrawler tracks and wallows; the Jawa Trade Moot's circuit | dune sheet §8 | kept in the campaign layer; cited for where fuel is bought | | |
| Deep Desert Tribe holdings with no roads | dune sheet §8; deep sheet §8 | kept in the campaign layer | | |
| Buried finds, found when the dune moves off them | dune sheet §8; bedazzle §4.3 | kept (sealed caches; the gale's uncovering) | | |
| Toward the centre: the Rust Cathedral at the bottom of a planet-sized drain | dune sheet §8 | lost | Another biome. | |
| "A machined ochre surface under a star that has not moved since the world began" | dune sheet §9 | lost as a quotation; flagged above | The opening line carries the same picture. | |
| Palette, one hard light, long horizontals and one vertical | dune sheet §9 | kept as art direction | | |
| "It is not a place you visit. It is the distance between places." | dune sheet §9 | kept, quoted | | |
| Wanted and barred roster lists; "sparse to the point of discomfort" | dune sheet, roster consequences | kept as the roster's rule | | |
| The deep desert as the conjugate of the Abyss: "here it is that you will run out" | deep sheet intro | kept as the reason the crew leaves | | |
| Region table, from-water measurements, the Anvil is not this biome | deep sheet §0 | lost | Tile measurements are never evidence. | |
| "The ground past the last thing that burns... what died here is still lying where it fell" | deep sheet §1 | kept | | |
| "Energy is free and water is money" | deep sheet §3 | kept | | |
| Shade is permanent geography; three sources only | deep sheet §3, §5 | kept, with skeletons added as turn three added them | | |
| The sand is a medium; things swim beneath it | deep sheet §4 | kept, quoted | | |
| The appraisal: attack as a water decision | deep sheet §4; turn three §4 | lost as targeting by water held (his card); kept as "no water, no strike" for droids | | Water-ranked prey: rejected twice. |
| "A droid is invisible to the food web" | deep sheet §4; cast bible ruling 6 | kept, quoted; built | | |
| Predators do not chase, and often do not move once seen | deep sheet §4 | kept (the gaanok); not promised for every predator | | |
| Nothing rots; bodies desiccate; a kill is drunk where it falls | deep sheet §4, §6 | kept, reshaped: keeping is promised only inside a held cave | His words of 2026-11-03: titan resources "shouldn't rot any faster than meat normally does". | |
| The head is a still; mass is the water balance sheet | deep sheet §4 | kept as art direction | | |
| Anhydrobiosis: a sandstorm is an aerosol of sleeping organisms; the bloom after water | deep sheet §4 | kept in "later" (hourbloom, gale seeding) | | |
| "The ground lies to you": prey that drums dry, predators that drum juicy | deep sheet §4 | kept, quoted | | |
| Fliers nest here because nothing can reach the nest | deep sheet §4 | kept (the soorrak) | | |
| Eggs are canteens, and some are traps | deep sheet §4; bedazzle §4.4 | kept, quoted | | |
| The ollim: a tree whose product is shadow, among the bones, rented shade | deep sheet §4b | kept | | |
| Ollim wood: heat and flame immune, weak to sharp and blunt | deep sheet §4b, §7 | kept, quoted | | |
| Creatures must not look mineralised; powder glaze, never shiny | deep sheet §6 | kept as art direction (the two sheets differ on mirror surfaces; the roster already lives with both) | | |
| No fast growth here | deep sheet §6 | kept | | |
| The sarlacc carve-out for held water | deep sheet §6 | kept in the campaign layer | Its own build. | |
| Brine and mineral salts from cavern seeps | deep sheet §7 | kept as the seep cave; extraction later | | |
| Ground a droid can cross that a person cannot | deep sheet §7 | kept | | |
| Yardang stone; the map has a grain | deep sheet §7, §9 | kept on the rock; whole-map grain later | | |
| Wreckage-shelters: a wreck makes shade and a small living place | deep sheet §8 | kept | | |
| Caverns as the real ecosystems; "strike out of the water like traps"; the cave-beast and its eggs | deep sheet §8 | kept (seep cave, guzzka lair); full cavern authoring later | | |
| Mummified fields | deep sheet §8 | kept, reshaped: the veessa and the mummified caravan carry it | | |
| "Fire is the tribes' weapon": it routs and there is no fuel for it | deep sheet §8 | kept, quoted | | |
| Sandstorms that break walls, tear roofs, carry pawns away permanently | deep sheet §8 | kept, reshaped: the gale carries and returns, with signs | Nothing vanishes without a sign. | |
| "Everything that ever died here is still here, and most of it is only asleep" | deep sheet §9 | kept as the place's mood | | |
| Experience line: "An ocean of nothing under a sun that never sets, crossed by giants. Rock islands are your harbours, and their caves are your fortune." | experiences; walk | kept, quoted | His card of 2026-10-20. | |
| His answers: fortunes scattered through emptiness; only a prepared harbour is dependable; a fortune is the next expedition | owner answers; tree | kept, quoted; "the next expedition" read as the ship's next leg | | Hold the colony reading: the first version is then proved on an outpost nobody in the campaign builds. |
| The adopted root | tree | kept, reshaped: its first three sentences are 0.1.0, its last is later | See above. | |
| "THE poster biome of the old tattoine. Huge skeletons on the sand. Barren tracks of apparent nothingness." | turn three §0 | kept, quoted | | |
| "The place Jawas were made for, and the place that made the krayt" | turn three §1 | kept, quoted | | |
| Thesis: "the biome that is not there"; you transit, you detonate, you dig, you leave | bedazzle §1 | kept | It was already a visitor's biome. | |
| Admission test: buried, dormant, giant, or a line | bedazzle §1 | kept | | |

### Under the sand, and what comes up

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The sand-swim kit: submerge, wake, rumble, breach, signs | turn three §2.0, §5; cleanse | folded into shared machinery; featured here | | |
| "The sand swimmer mod is. Major player here." | turn three §0 | kept | | |
| Vekka and qorrax | bedazzle rulings; cleanse | kept | | |
| Deep sand is walkable, very slowly, a terrain of its own | bedazzle ruling 5 | kept | | |
| Drag marks, funnels, letters naming a loss | turn three; cleanse | kept | | |
| The Listening: hiss, saltation, singing dunes, bone harps, rumble, breach, the liars | turn three §2.1; review §8 | kept: hiss, saltation, rumble and bone harps in 0.1.0; singing dunes moved (→ 0.2.0) | "Focus on wind and sand noises and then ominous rumbling" (his words). | |
| The geophone | review §8; cast bible | moved (cleanse next version → 0.2.0) | | |
| "It cannot tell a true drum from a drazzik's lie" | review §8 | kept with it | | |
| Drazzik drum lure and trap clutch | bedazzle §5; cleanse | kept | | |
| Duumma, the prey that drums dry; its water sac | fill-out §2.4; cleanse | kept | | |
| Sand busters: the planet's only infestation, erupting from dry ground | dune sheet amendment; bedazzle §4.1 | moved (cleanse next version → 0.1.0) | | Leave it off: 0.1.0 has no mass threat. |
| The vanilla infestation banned everywhere else by the campaign layer | dune sheet amendment | kept in the campaign layer | | |
| Ruukka and oorrik castes; the mound | bedazzle; cast bible | kept; spreading brood moved (→ 0.2.0) | | |
| Zuurrik, the swarm blood on sand wakes | cast bible §5; walk | moved (→ 0.2.0) | | |
| Sand fishing: dune crawlers and glass pearls | turn three §5; cleanse | kept | | |
| Fishing calls a swimmer | cleanse | moved (→ 0.2.0) | | |
| The thumper, wet | turn three §4; cast bible ruling 6 | moved (→ 0.2.0), quoted | | |
| The krayt horn | turn three §4; cast bible | moved (→ 0.2.0, Star Wars layer) | | |
| Krayts stay wild; attack events on top | cast bible ruling 1 | kept in the Star Wars layer | His card. | |
| Krayts as events only | turn three §2.5 | lost (declined) | | |
| The krayt attack, beat by beat | turn three §2.5 | kept in the Star Wars layer | | |
| The muurrok, the free tier's leviathan, with a reflected-sun beam | turn three §2.5; cast bible ruling 3 | moved (→ 0.2.0) | | 0.1.0: asked as `NEEDS HIM`. |
| The sarlacc swimmer comes to root at the seep | turn three §2.5 | kept in "later" (campaign) | | |
| The greater krayt den quest | turn three §2.5 | kept in "later" (campaign) | | |
| The Long Hunger and its Groundcaller | turn three §2.5 | kept in the campaign layer | | |
| Travel thirsty: the wettest body is chosen | turn three §4; cast bible ruling 7; tree | lost (out by card) | | |
| Sinkhole caves | turn three §4; cast bible ruling 7 | lost (out by card) | | |
| The dunes take the ship | review §8; turn three §4; cast bible ruling 7 | lost (out by card); `NEEDS HIM` | | See above. |
| Ollim-wood sand anchors | review §8 | lost with it | | |
| The buried record: caches, the dig-out loop | bedazzle §4.3 | kept as sealed caches and wrecks | | |
| The mummified caravan | turn three §4; cast bible ruling 10 | moved (→ 0.2.0, with the gale) | | |

### Giants, small life and plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Oommok, the mirror giant | bedazzle rulings; cleanse | kept | | |
| Eemmok shade commensals | bedazzle; cleanse | kept | | |
| Aurrok grazer; karrask and its plate; vaalok pack carrier; murrowbulb crop | cleanse | kept | | |
| Soorrak, the flier that owns the sky | fill-out §2.1 | kept; real flight | | |
| Gaanok, the follower | fill-out §2.2 | kept; its following is owed | See above. | |
| Liikka, the light-eater | fill-out §2.3 | kept | | |
| Veessa, the miller of the mummified dead | fill-out §2.5 | kept | | |
| "A field with no veessa in it has something worse in it" | turn three §3.1 | kept as flavour | | |
| Loomma, the ollim's tenant | fill-out §2.6 | kept; dung seeding later | | |
| Ikee shrunk to grain; spined-gow grown to giant | bedazzle ruling 8 | kept | | |
| Siidda, the dust husk, dormant | bedazzle ruling 11 | kept | | |
| Kudda and truffle mole cut here; kreetle and gizka stay | bedazzle rulings 2 to 4 | kept as ruled | | |
| Guzzka in its cave on its eggs | turn three §2.6; cleanse | kept | | |
| Piinnok, the watcher that sinks when a threat nears | cast bible ruling 4 | kept where its own mod puts it (the watcher creatures) | | |
| Rehomed Long Shade animals and the ultriss pad | cleanse | kept | No evictions. | |
| Light-pipe nubs; glasscrust; tracks through glasscrust last for years | fill-out §3.3; dune sheet | kept | | |
| Hourbloom | fill-out §3.1 | kept in "later" | It needs water poured or a gale's seeding. | 0.2.0 with the gale: small. |
| Kneel ollim | fill-out §3.2 | kept | | |
| The roster json's fauna, flora and 110 evictions | roster json | kept as the record of the cast | | |
| Canon rows stay in the Utinni patch; invented names in the free tier | bedazzle §2 | kept | | |
| Names: vekka kept, oommok and siidda ratified | bedazzle rulings | kept | | |

### Sun, weather, rock and bone

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The biome takes its sun angle from its latitude" | turn three §0, §2.7 | kept | | |
| Pinned sky; no day and night | turn three §2.7; cleanse | kept | | |
| Cover rules that switch at a sun angle; a biome heat offset; a glare floor | turn three §2.7; cast bible ruling 2 | lost | One sun from geometry (2026-10-19): roofs and parasols at every angle, no biome heat. | |
| "Overheating here should be trivial and difficult to avoid" | turn three §0 | kept, reshaped: the high fixed sun does it by geometry, with no biome number | | |
| Glare-blind, goggles, the Jawa exempt | turn three §4; cast bible ruling 8 | moved (→ 0.2.0), quoted | | |
| The mirage | turn three §4; cleanse | moved (recommended retirement → 0.2.0) | | Retire it as the cleanse says. |
| The cooling draught | turn three §5; cleanse | lost (recommended for dropping) | | |
| The dune gale: herald, marching dunes, aftermath | turn three §2.2; review §8 | moved (→ 0.2.0) | | 0.1.0: asked as `NEEDS HIM`. |
| "Call it a dune gale" | turn three §0 | kept | | |
| The gale takes the sun off you; the best time to move | turn three §2.2 | kept with it; read also as the only cover from orbit | | |
| Carry-off with a drag trail, and return | review §8; cleanse | moved (→ 0.2.0) | | |
| One emergence when it clears; seeding | turn three §2.2 | moved (→ 0.2.0) | | |
| Gale abrasion and static | turn three §4; fluff cuts | lost (cut 2026-10-23); abrasion asked as `NEEDS HIM` | | |
| Dust devils; fulgurites | turn three §4; fluff cuts | lost (cut) | | |
| Moving dunes, drift, drift shovelled to glass sand at full yield | bedazzle ruling 12; cast bible ruling 5 | kept | | |
| "The rare rock should be celebrated and almost always featuring a precious cave" | turn three §0, §2.6 | kept | | |
| The arrival letter naming the rock and its bearing | turn three §2.6; cleanse | kept, quoted | | |
| The mouth on the shade face; cool, dark, water | turn three §2.6 | kept, quoted | | |
| The precious table: seep, guzzka lair, lens grotto, krayt den, debt cave | turn three §2.6 | kept, reshaped: the built five (seep, guzzka, grotto, sealed cache, taken before) in 0.1.0; den, sarlacc and debt-shrine kinds later | | |
| Cave drip; tribal mark on a taken cave | fluff cuts | lost (cut) | | |
| "Cool cave" means out of the sun, not cooler air | cleanse owner_pages | kept | | |
| Giant skeletons: landmark, striped shade, a skull as a room, loot | turn three §3.1 | kept | | |
| Bone harps | turn three §2.1, §3.1 | moved (cleanse next version → 0.1.0) | | |
| A skeleton's species as a warning of what hunts here | turn three §3.1 | kept as flavour | | |
| Your kills become skeletons over a season | turn three §3.1 | kept in "later" | A season. | |
| Dunes burying and uncovering skeletons | turn three §3.1; fluff cuts | lost (cut) | | |
| The krayt graveyard mutator; the extra fossil scatter | turn three §3.1; cleanse | lost (recommended for dropping) | | |
| Tracks: boots, treads, wakes, drags, oommok prints, eruption scars | turn three §3.2 | kept | | |
| The dunes as the eraser | turn three §3.2; fluff cuts | kept | | |
| Arrivals announced hours early by a dust plume | turn three §3.3; cleanse | lost (recommended for dropping) | A second queue that can strand a raid; the Empire's ladder brings its own warnings. | Keep it for the look of a strike team's dust. |
| The glass sea landmark | turn three §4; cast bible ruling 10 | lost (out by card) | | |
| Wreck field: sand-sealed hull, cylinder, tread | cleanse | kept; the cylinder cited for fuel | | |

### Glass, water, faith and the ship

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Sand to glass to lens; sun furnace, lens bench | turn three §2.4; cast bible | kept in "later" | See above. | |
| Solar still and solar oven | turn three §0, §2.4 | kept in "later" (the oven); the still moved (later → 0.2.0; corrected by the second reader) | The still is half of the ship's gift. | |
| Sieve; pearl and krayt lenses; crest-plate oven; brine dipping and salt | turn three; cleanse | kept in "later" | | |
| The sun lance | turn three §4; cleanse | moved (recommended for dropping → 0.2.0; corrected by the second reader) | His card pick of 2026-09-30 and half of the ship's gift; see the added rows. | |
| The wringing still | turn three §4; cast bible ruling 10 | kept in "later" | | |
| The Sun-Debt as a counted ledger | turn three §2.3 | kept in "later" (campaign) | | |
| The Return at a debt stone | turn three §2.3; review §8 | kept in "later"; flagged above | | |
| Pour, wet line, bloom on pour | cleanse | kept in "later" | | |
| "ALL game wetness should now migrate to a thin film" | tree | kept in "later", as the tree already has it | | |
| Eggs as water with real volume | bedazzle §4.4; cleanse | kept | | |
| Ship contribution: biosilica lens array, egg cistern, solar catch-yard | bedazzle §6 | kept in "later" | | |
| "Makes the emptiest biome the refuelling stop" | bedazzle §6 | lost | It meant power, not fuel; the fuel ruling of 2026-11-18 is applied instead. | |
| "Many paths to fuel": helixien gas on deep-desert tiles | campaign lore | lost from this biome as unsupported; `UNSETTLED` in the design | No Stillsand source places a deposit. | A gas seep in the cave table: small, and it makes this a richer fuel stop. |
| Scanner readings | cleanse | moved (→ 0.2.0) | | |
| Mod Settings | cleanse; walk | kept | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The tree's eleven leaves and its "does not" list | tree | kept as the pipeline holds them; not edited | A later Designer run reconciles them with this design. | |
| The cleanse's signature (cross, secure a cave, resupply) | cleanse owner_pages | kept as the spine of 0.1.0 | | |
| Forty-colonist harbour | cleanse; tree | moved (first version → later) | Colony scale. | |
| The full-season walk with reload | cleanse; tree | out of every version | Season-long play is play testing (`design/RimMandrake/standing_rulings.md` §Season-long play is play testing). The reload stays a short scene. | |
| The four offline models | cleanse owner_pages | kept | | |
| Tickets and switch-offs | cleanse next_version | kept as they stand, except where a feature moved | | |
| Eight proposed bars | cleanse owner_pages | kept as history; the fourteen promises in the design are the proposal to argue from | | |
| The walk's anti-guessing notes | walk | kept; they are test knowledge, not design | | |
| Admission to the pipeline on Codex; held by the owner | tree | kept as a fact | | |

### Added by the second reader

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The ship's exposure tracker, its landing advisory and the thermal veil: *"reflect all external heat outward with a mild mirror sheen... so the temperature slowly climbs anyway"* (owner, 2026-09-02) | shield rulings | kept, quoted: now the design's hull answer for heat | The first read wrote that no hull system exists. | |
| The light screen handles *"wind, ash, vapor... sand... completely"*; the stock sandstorm is in this biome's weather table | shield rulings; review §2; biome def | kept, cited | | |
| The dune gale is written to carry no falling sand, so the shield frame cannot see it | biome def | kept as a build gap in the hull section | | Give the gale a sand rate: the dunes engine already moves the field. |
| The tracker's heat line is 58 °C; the sheets give 52 to 70 °C in the dune sea and 26 to 43 °C in the far ring | shield rulings; dune sheet §2; deep sheet §0 | kept as an `UNMEASURED` flag | The built heat wear may not fire on much of this biome. | |
| The heavy field *"resists impactors, blaster fire, and large animal assault"* | shield rulings | kept, quoted against krayt, muurrok and busters | | |
| The krayt attack is *"weighted up by... vibration (drilling, a landing ship, the thumper)"* and goes *"toward whatever is making the most noise"* | turn three §2.5 | kept, quoted as wear on the hull (0.2.0, campaign layer) | A kept idea that names the ship; the cut one did not need reviving. | |
| *"A structure is buried on its windward face and undercut on its lee"*; no *"permanent structure not either buried or actively dug out"* | dune sheet §6, §8 | kept, quoted: it is the source for drift on the hull | The first read gave drift no source. | |
| *"Crawler-scale machines are the only settlements that make sense in a landscape that buries fixed ones"* | dune sheet §8 | kept, quoted | It is written about a ship. | |
| *"Move in the shadow of your own landed ship"* | turn three §2.7 | kept, quoted: the ship as the fourth shade | | |
| *"Where debris falls it makes shade, and shade makes a small living biome right beside it"*; a wreck's shade is *"a hard-edged permanent shape, and the player can see why that shape is worth owning"* | deep sheet §8, §9 | kept, quoted; read as the ship's own lee | | |
| Ollim wood as hull cladding against heat | none (deep sheet §4b gives the wood) | kept as the second reader's proposal, flagged | His ruling names armour; no source puts ollim on a hull. | Leave it out: free. |
| The lens kit as the biome's gift to the ship: *"the lens-glass solar still and sun lance, fuel-free on an open deck"* | ship gifts | moved (still: later → 0.2.0; lance: recommended for dropping → 0.2.0) | His every-biome ship question of 2026-09-24 outranks the cleanse; both are built. | Leave both where the first read had them: the Stillsand gives the ship nothing in two versions. |
| The sun lance was his own card pick (slate IN, 2026-09-30), with gale static, dust devils, the mirage, glare and goggles, singing dunes, droids and the thumper | cast bible ruling 6 | kept, corrected: the lance is off the "recommended for dropping" list | The cleanse's retirement list is checked against his earlier cards. | |
| Roads: *"For now just replicate where we had roads before."* (owner, 2026-10-20); 196 road links cross the Stillsand on the record | owner ledger; biome def | kept, corrected in the design | The sheet's *"No roads through the deep dune"* was the first design's premise; his later word replaced the ban. | |
| Fine sand is *"a trade commodity"* (card, 2026-09-30); glass sand is the ingredient of the Pyrelands' Struck Glass rite (card, 2026-10-16) | cast bible §7; owner ledger | kept: named as what the crew pays for fuel with | | |
| The free tier has no trader caravans without its own pack giant, the vaalok | bedazzle §2d; review §5; roster json | kept (built); cited for who sells | | |
| *"The gale blinds the swimmers... swimmers stay down and strike rates collapse"*; *"A player who learns this crosses the Stillsand in the gale"* | turn three §2.2 | kept, quoted (0.2.0, with the gale) | It changes what the gale is for, for the crew and the Empire both. | |
| The gale drowns the rumble; the oommok hunkers and *"its shadow stops moving"* | turn three §2.2; review §8 | kept with the gale | | |
| A pawn carried off the map *"comes back: the next gale or dune pass drops the body, or the living pawn as a wanderer"* | turn three §2.2 | kept with the carry and return | | |
| What a gale can uncover: a caravan, a hull, a sealed Jawa cache, a giant skeleton or a cave mouth | turn three §2.2 | moved with the gale (→ 0.2.0) | | |
| The zuurrik's rule: *"fighting here starts a clock. Kill, loot fast, leave. A battle left standing becomes a zuurrik bloom"*; it never attacks the unwounded | review §6, §8 | kept, quoted in the Empire section and as a moment (0.2.0) | The first read listed the animal and not what it does to a firefight. | |
| *"The veessa mills the dry dead, the zuurrik the wet"* | review §6 | kept | | |
| The piinnok: *"the one thing that tracks anything: you"*; *"living geophones"*; better biosilica when butchered | review §6; watcher pitch | kept, quoted, with its moment; in 0.1.0 (built in the watcher kit) | Admitted by card 2026-09-30; the first read left it to "its own mod". | |
| The two gaps the review named: nothing wakes to blood; *"the glass is only ever a plant"* | review §6 | kept (zuurrik and piinnok fill them) | | |
| The Last Track: a dead crawler at the end of a tread, the drive turned over once: *"We ran her until the sand had her... She will know you."* | rites pass §9.1 | kept, reshaped: the crawler and its note are in the first day; the rite is in "later" | Ruled-kept 2026-10-02; rites since put under review. | The rite in 0.2.0: campaign layer, small. |
| The Unspilled March: full water carried toward a mirage and none drunk: *"He is the pool that walks away."* | rites pass §9.2 | kept in "later", quoted | The Return's opposite, for the Jawa's own faith. | |
| The Return is the Tribes' own; a Salvation colony cannot learn it (ruled 2026-10-01) | rites pass §9 | kept, stated | | |
| Rites under review: *"Many of them are somewhat fluff"* (owner, 2026-10-23); the review's opinion on the Stillsand rites was "cut" | owner ledger; mechanics review | kept as the reason the rites stay in "later" | | |
| *"The light is a fixed condition, like the pressure at the bottom of a sea"*; a stone's shadow *"will be exactly that shadow when your great-grandchildren find it"* | dune sheet §1 | kept, the first quoted | Dropped lines worth carrying. | |
| *"The limiting danger is the light itself"*; shade shelters *"against merciless radiation, not merely heat. An animal caught in the open is being sterilised, not just cooked"* | dune sheet §2; deep sheet §3 | lost | One sun from geometry: no second kind of harm from the sky. | |
| What ends dormancy: *"free water, a vibration, a temperature anomaly, blood"*; *"It wakes up because something did something"* | dune sheet §4 | kept (the landing is three of the four) | | |
| *"Nothing is dormant-looking; everything is actually dormant. Absence of visible activity... proves nothing"* | dune sheet §5 | kept as the place's rule | | |
| Buried finds are found *"when the dune moves off it or a giant's foot breaks the crust"* | dune sheet §8 | kept (caches); the giant's foot is not built | | |
| Giants *"cannot be ambushed and cannot be outrun, only outlasted"* | dune sheet §7 | kept as flavour | | |
| *"Pristine and buried"* here against *"corroded and standing"* elsewhere: *"Two utterly different salvage games, and a Jawa clan wants both"* | dune sheet §7 | kept | | |
| *"Draw the desert so the line lands like a shout"*; giants *"drawn at a scale that breaks the composition on purpose"* | dune sheet §9 | kept as art direction | | |
| *"If the dune sea's roster looks healthy, it is wrong"*, against his *"but we need to fill out that roster. That's silly. More!"* | dune sheet; owner ledger 2026-09-28 | kept: his later word made the fill-out, and every row of it is sparse | | |
| Sand busters *"do not glide through the dune, they ERUPT from it"*; the ground must be dry; *"an eruption scar is the only mark it leaves"* | dune sheet amendment | kept | | |
| The busters' carcass: giant chitin plate in the mirror palette | bedazzle §4.1 | kept as a thing to take away | | |
| *"Digging is drumming"*; *"vibration is the dinner bell for everything subsurface"* | bedazzle §4.3 | kept | | |
| *"A creature that watches you walk past is doing arithmetic, and this reads as far more alien than aggression"* | deep sheet §4 | kept (the gaanok) | | |
| *"The prize is a full animal, and a dried one is worthless"*; nobody caches | deep sheet §4 | kept as flavour | | |
| The fliers' guano, dropped prey and dead chicks are the only organic import; a nesting crag is *"the richest square kilometre of surface in the biome"* | deep sheet §4; fill-out §2.1 | kept with the soorrak | | |
| The ollim *"nursing the very source of water that might sustain it"*; *"The bones and the tree are one system"*; a stand *"older than any ruin"* | deep sheet §4b | kept | | |
| The cave beast: *"a huge shaggy thing deep in a cavern, with massive eggs a Jawa would cross a desert for"* | deep sheet §8 | kept (the guzzka) | | |
| *"The weapon that wins is the one you can barely afford to use"*; fire-keeping sacred beside the Sun-Debt | deep sheet §8 | kept with the tribes (campaign layer) | | |
| *"What is destroyed here stays destroyed"*; *"a predator that watches you go by without bothering to rise"* | deep sheet §1, §9 | kept as mood | | |
| The sarlacc's three stages, dew ring and breach flood; *"The water in your cave becomes a mouth"* | deep sheet §6; turn three §2.5 | kept in the campaign layer, later | | |
| The canon cast by name: war wyrm (ruled a burrower by card, 2026-09-09), krayt, greater krayt, kreetle, granite slug, scurrier, gizka; the bloddle plant; five canon pack beasts | bedazzle §2a; roster json | kept in the Star Wars layer | | |
| *"That emptiness is the intended outcome… what you meet there should be something that arrived"* | bedazzle §4.6 | kept, as the admission test's second half | | |
| *"Deep sand pools are NOT unwalkable, just very slowly. And they should be an entire terrain type... Muchly in the Stillsand."* (owner, typed) | bedazzle rulings | kept, his words now on the row | | |
| The solar offer: the sun as *"the campaign's energy anchor"*, the gravship's appetite sited here on purpose; solar read from the code as following sky brightness | bedazzle §4.5; turn three §2.4 | kept, reshaped: stated as a reason a ship can stay, with the code reading | The first read marked it unmeasured; turn three had read the code. | |
| The egg cistern and the solar catch-yard as ship parts | bedazzle §6 | lost | Never carded; the gift on record is the lens kit. | A hold rack for canteen eggs: small. |
| The ikee's label *"drageye"*, the builder's word after he ruled the Stillsand's eye gets *"a new distinct label"* | review §1 | kept as an open naming row | | |
| The nizzek, the drazzik clutch's hatchling, *"hostile from the shell"* | review §2; cast bible | kept (the wrong egg) | | |
| The vozzik, a barely moving slug giant | bedazzle; roster json | lost from this biome | He moved it out on 2026-10-04, in two notes: the free-tier animal (*"This should go into the Warscar."*) and the campaign-tier one (*"This should be moved to the Rust Cathedral Biome."*). The second note was cut off in the earlier reading; added after the roster was read to its end. | |
| Ulgga, vosska and the ultriss pad moved in by his sheet notes of 2026-10-04; the kudda cut (*"It's dumb."*) | roster json | kept as ruled | | |
| Dead trees purged (*"dead standing wood is imported treasure, never scenery"*) | roster json | kept as the record of the cast | Corrected after the roster was read to its end: this row also said the dunealisk and the korrum are on the roster. The korrum was removed from it (its one home is the Scarlands), and the dunealisk is both refused and listed; see the rows added from the full reading. | |
| The Sun-Debt's words: *"The sun lends and the sand collects… We take back what was drawn"* | review §2; turn three §2.3 | kept in "later", quoted here | | |
| The Debt as a valve: *"the krayt is the debt collector, and the storyteller agrees"*; a bad Return is *"a debt refused"* | turn three §2.3 | kept in "later" (campaign) | | |
| *"The sand remembers water"*: wet sand draws swimmers, *"the rumble comes to the pour"* | turn three §2.3 | kept (the wet thumper is its use) | | |
| Hourbloom's triggers include *"a breached cistern, a spilled tank"*; *"dead land proving it was never dead"* | fill-out §3.1 | kept in "later"; a ship's spill is a trigger | | 0.2.0: a bloom from the crew's own accident. |
| The sand stalker under a fishing pool, waiting for *"a dune crawler, or a boot"*; the glass pearl, *"a lens that grew a skin"* | turn three §2.0 | kept with fishing | | |
| The third-party sandworm as a reference only; the Long Hunger *"erupts, pulses tremor damage, submerges dropping salvage"* | turn three §2.0 | kept in the campaign layer | | |
| The krayt's goods: skull, pearl *"in the gizzard stones"*, the graveyard scatter | turn three §2.0, §3.1 | kept in the Star Wars layer | | |
| The dunes engine's own figures and limits: it cannot bury pawns, corpses or turrets; its wind wanders where the sheet's never turns | turn three §2.0; dunes design | kept as build notes | | |
| The wake as *"a low travelling ridge with a spray of grains off its crest"*; *"Hard ground is therefore a moat"* | turn three §2.1 | kept | | |
| *"A quiet map is not a safe map, and a loud one is not a warning"* | turn three §2.1 | kept as the sound bed's rule | | |
| *"We can't have animals 'disappear spontaneously.' There needs to be SOME kind of indication of what happened to them."* (owner) | turn three §0 | kept: his words behind "nothing vanishes" | | |
| The muurrok seen cruising: *"a line of glare moving across the dunes, a blade of light cutting the corrugation"*; *"one take, and is gone"*; its crest-plate | turn three §2.5 | kept with the muurrok (0.2.0) | | |
| *"Yes and use the beam attack style from mechanics due to reflections"* (owner, typed) | cast bible ruling 3 | kept, his words now on the row | | |
| The den quest as *"the Mandalorian beat"*: bait, drum, charges; the krayt *"spits acid"* | turn three §2.5 | kept in "later" (campaign) | | |
| The cave: *"The hiss drops away at the mouth... Deeper, sometimes, is something breathing"*; *"To settle it, you must take it from whatever already lives in it"* | turn three §2.6 | kept | | |
| A taken cave's *"cold hearth"*: *"the empty one is a sign too"*; a rockless map may seat one small tor | turn three §2.6 | kept (taken before); the mark itself was cut | | |
| The lens chain's parts: a furnace that *"needs no fuel"*, pearl and krayt lenses, the still fed by brine, wet kills or the dead; an oven that is *"a stove for a biome with nothing to burn"* | turn three §2.4 | kept in "later", except the still, moved with the kit | | |
| Lost with the one-sun ruling: the sand glare floor, the paved *"shade yard"*, cover that switches at 55° | turn three §2.7; cast bible | lost | 2026-10-19: roofs and parasols at every angle, no biome number. | |
| *"The colony is a power plant keeping itself alive"*; *"Every counter feeds a danger"* | turn three §2.7 | lost as colony talk; the second kept as the biome's shape | | |
| Skeletons: *"Luke passed one in the first film"*; *"you can find a skeleton with your eyes shut"*; a funnel in the ribs means it *"was taken from below"*; *"The biome keeps score"* | turn three §3.1 | kept | | |
| The track table: crawler treads lead to *"a dead crawler at the end"*; oommok prints *"a day apart"*; a glasscrust scar is *"the oldest route on the map"*; *"The map is a page"* | turn three §3.2 | kept | | |
| Raids *"arrive knowing your layout and pick the side without a wall"* | turn three §3.3 | kept, quoted in the Empire section | | |
| The thumper as *"the drazzik's lie, made by hand"*; the wringing still: *"It is how the desert has always drunk"* | turn three §4 | kept with each | | |
| The fill-out's lines: the gaanok *"patient, visible, and correct"*; the liikka's glints that *"have moved"*; the duumma's quiet sand; the loomma that *"cannot survive twenty minutes"* outside its shade | fill-out §2 | kept, the first two quoted | | |
| *"Your color palette is too uniform per biome. Needs more variety."* (owner) | cast bible §2 | kept as art direction | | |
| His answer on fortune names lens production (*"potentially including useful lens production"*, 2026-11-10) | owner answers | kept as support for bringing the kit forward | | |
| The wetting technique *"the Stillsand is already developing for spilled water on the sand"* (owner, 2026-11-04) | owner ledger | kept in "later" with the thin film | | |
| The Listening's limits: the geophone is taught by *"studying a ruukka corpse or a spent mound"*; *"the readout must stay coarse... or the biome's dread dies"* | review §8 | kept with the geophone (0.2.0) | | |

### Added by the second reader: the roster file read to its end

A third run, 2026-11-18, read `rosters/dune_sea_deep_desert.json` from its first line to its last (943 lines, 110
evictions, 26 animals, 7 plants, 11 purged plants, 11 owed new things, 6 confidence notes), with no line or reason
cut. The rows below are what that reading found without a row. Two of the second reader's rows were corrected in
place and say so (the korrum; the vozzik).

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| *"I meant pick one arid home."* (owner, 2026-09-22, correcting a row added here the same day): the arid biomes he had listed were *"the CANDIDATE set, not an assignment"*, and *"a shared habitat class is NOT an in-game reason to multi-home an animal"*. The bokka's one home is the Long Shade; the korrum's wiring here was removed too, *"its one home is the Scarlands"* | roster json | kept as a rule; neither animal is on the Stillsand | His words, in the longest reason in the file; the earlier reading had its first 95 characters. It is where the one-home rule was first written down. | |
| The size law the evictions measure against: a body size from 0.3 to 3.0 is banned on the surface (freeze ruling R22, *"one merged roster, strict intersection"*); 81 of the 110 rows cite it, each with its measured size | roster json | kept as the roster's rule, never as a bar | The first read's row has "enormous or grain-scale"; this is the measure behind it. A number here is the record of a sorting, not a promise. | |
| The predator law: a hunter here strikes from under the sand or does not live here; pursuit hunters are refused (*"nothing charges out of a bush; there is no bush"*); one that ambushes from water is refused too | roster json | kept as the roster's rule, the line quoted | | |
| No large herds on the surface (the deep sheet's seventh ban): the ronto and the skalder go to the Desert, *"where a herd is infrastructure"*; the beldon and the thranta are refused | roster json | kept as a rule; the animals kept elsewhere | | |
| Animals this roster sent to the Desert (today the Long Shade's roster): eopie, falumpaset, the gorg and frilled gorg, jamel, reek, varactyl, uvak, worrt, shyrack, sketto, desert ave, sand prowler; and by his card *"adjust-and-keep in Desert"*, slowed to fit, the gutkurr and the wraid (the wraid *"as burst predator"*) | roster json | kept elsewhere | Where each landed after the Long Shade's later sittings was not checked by this reader. | |
| Sent elsewhere: to the arid shrubland the longtail gorg, the urusai and (by his card) the massiff; to the Fall Line the mynock (*"parasite needs hosts/hulls"*), the scavrat (*"scurrying between wrecks is correct"*), the fuelmite (*"eats fuel"*) and the womp rat (*"Fall Line ship vermin"*); to the poison forest the crystal mit and the neebray; to the Wasteland the fission mouse; the two hornet queens through the Wasteland to the fungal jungle, their *"current final home"* | roster json | kept elsewhere | These are the "where an animal was sent from" notes. The Fall Line four are ship vermin by the roster's own words. | |
| Refused on sight: the two crabs (*"recognizability, doubly strict here: a crab is a crab"*); the crystal fox (*"mineralized/shiny on sight"*); five animals of three retired donor mods (*"0% survival, mod retirement ruled"*) | roster json | lost (cut or refused) | | |
| *"giants limited to the ruled five"*, under the sheet's *"sparse to the point of discomfort"*; two animals refused on that count | roster json | kept as the record | This roster itself lists more than five giants since his fill-out commission (*"More!"*); his later word wins, as the second reader's row on the fill-out says. | |
| The dunealisk is in this file twice: refused (*"strict intersection evicts it despite the subsurface-donor pattern"*) and listed as an import (*"subsurface strike only — the one legal predator archetype"*, *"review-flagged"*) | roster json | kept as a flag (`UNSETTLED`) | The file disagrees with itself. A search of the built biome def and the campaign patch finds no dunealisk row in either. The second reader's row said it is on the roster; that row is corrected. | |
| Two eye tests left to him and never recorded as done: whether the granite slug and the boulder mit pass the ban on a mineralised or shiny look (*"eye test is the owner's; stone-named but matte-dusty reads plausible"*) | roster json | kept as an open flag | The boulder mit is on this roster as a kept giant and has no other row on this page. | |
| The bloddle measured: no green pixel on any of its three pictures, *"a bulbous rounded body with no leaf shapes"*, so it passes *"no green, no leaves"*; that it is not glassy or white is *"a separate stylistic note"* | roster json | kept (the canon plant, campaign layer) | | |
| The ban on night habits (the dune sheet's first ban) was never checked on any animal: *"no register field covers activity cycles; def-level lint owed"* | roster json | kept as a flag (`UNMEASURED`) | Under a sun that never sets, an animal with a night habit would sleep or hunt on a clock this place does not have. | |
| Every claim that an animal flies was unmeasured when the roster was made (*"register flies special is broken"*); the two leviathans were left out of every measure as *"not wild-roster material anyway"* | roster json | kept as the record | The soorrak's flight was built later and is real. | |
| The gizka has two homes, the Pyrelands and the Stillsand (*"ruled 2026-09-14, reaffirmed at the 2026-09-27 sittings"*), as a protected icon; the kreetle has one, here; the scurrier was thinned to a tenth by his card of 2026-09-09 | roster json | kept as ruled | The first read's row says the two stay; this is the ruling behind each. No evictions. | |
| The ikee *"had quietly tripled the roster's approved"* size when it was ported, which is why he shrank it; the spined gow's donor body was *"a mid-band SURFACE body, illegal on both arms"*, which is why it was grown | roster json | kept (the first read's row), reasons carried here | | |
| The name offered in place of vekka: *"the shakkir swap is dead"* (his call, 2026-09-27) | roster json | lost | | |
| The qorrax's picture is a donor's: *"our own recreated art owed"* | roster json | kept as a build fact (owed) | | |
| The gaanok as the roster has it: a *"never-attacking follower; takes only the downed"* | roster json | kept, with the first read's note that the following is owed | The census calls the built animal an ordinary slow predator; by this line it should never attack at all. | |
| The zuurrik is *"NOT a wildAnimals row"*: blood on sand wakes it, it *"strips the stain and the bodies beside it, then re-buries"*, and it *"keys to blood, never to a clock of day"* | roster json | kept (0.2.0, the second reader's row), detail carried here | | |
| Build facts the roster records: the zuurrik and the vaalok wear placeholder pictures; the hourbloom's plant exists but *"the incident that names it is not wired"*; the light-eater is spelled two ways in this one file | roster json | kept as build facts | The hourbloom is in "later"; whoever brings it forward builds the incident first. | |
| No fish: *"there is no water of any kind: no standing water, no ice, no fog, no condensate"*; *"the only brine is cavern seeps metres wide"* | roster json | kept as a rule | Sand fishing takes dune crawlers and pearls, not fish. | |
| His four sheet notes of 2026-10-04, whole: the ulgga, *"Good, but make it twice as big. Move to our custom extreme desert biome. RimMandrake level."*; the vosska, *"Move this to RimMandrake, then move to our custom extreme desert biome to swim in the sand"*; the ultriss pad, *"This is supposed to be in the most extreme desert ... Rename this to Ultriss Pad. RimMandrake tier."*; the truffle mole, *"Move this to the biome with all the Fuzz (Leaning?), Rim Mandrake level."* | roster json | kept as ruled, his words now on the row | The second reader's row names the moves and quotes only the kudda's. The vosska is one more sand swimmer by his word. | |
| The ultriss pad is wired as the commonest plant on this roster by a wide margin | roster json | kept as ruled, with a flag | Read in the roster and in the built biome def. The sheet says the standing crop *"would fit in a bucket"*; nobody has looked at a map to see which wins. A weight is tuning, never a bar. | |
| Plants purged: seven with Earth names or Earth houseplant bodies, under his card of 2026-09-09 (a planet-wide purge); and the giant mushroom, removed on his eye on 2026-09-20 (*"The giant mushroom seems misplaced"*), which lives in the Abyss | roster json | lost (purged); the mushroom kept elsewhere | | |
| The ollim's first name: *"silverbole (owner to name; silver required)"* | roster json | kept, reshaped: named the ollim; whether its picture is silver was not checked | | A look at the tree's art: one glance. |
| The plan before the siidda was built: dormant dune animals as reskins, because 107 donor rows already carried a dormancy mechanic | roster json | lost (the siidda was built on the game's own dormancy) | | |
| The sand busters' bodies, by the amendment he ruled on 2026-09-24: *"giant or grain-scale only, sun-axis polarised, no nameable insect/spider silhouette"*; *"sand BUSTERS, they erupt, they do not swim"*; the mound is a structure; banned everywhere else by the campaign layer | roster json | kept (the first read's rows), the body rule carried here | | |
| The roster's law sources: the dune sheet's section 6 and roster section, the deep sheet's section 6, freeze ruling R22, the assignment prep's sections 1 and 9, his cards of 2026-09-09 | roster json | kept as the record | The freeze rulings, the prep and the sitting item were not opened by this reader; none is on this page's delete list. | |

## Sources read, and the count

*(The first read's own account follows. The second reader's reading and recount are at the top of this page.)*

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**21 source files, 185 rows**, of which **23 lost**, **18 record a move** (whole or in part), **7 kept, reshaped** and 1 folded into shared machinery. Every source named above is in at least one row's source column (checked by the same script).

Read whole: the dune sheet; the tree's `root.md`, `sheet.md` and `journal.md`; the cleanse's owner pages; the owner
answers; the experiences table. Read in large part: the deep sheet (every paragraph, each cut at 1,500 characters);
the bedazzle proposal (thesis, the whole marquee section, feasibility table, ship row, the fourteen rulings); turn
three (the owner's words, the one-paragraph picture, the opening of each developed idea, all of skeletons, tracks,
"more ideas" and the ranked package); the cleanse next-version list (every entry, each cut at 520 characters). Read
by heading or by search: the review (headings, and the first three and a half entries of its mechanics slate); the
cast bible (rulings, build items, held art); the fill-out (the first lines of each species and plant); the roster
json (its keys and the names in each list); the walk (north star and anti-guessing notes); `stage2_edges.md`
(headings and the water-ranking reconciliation); the cleanse census (every row's name, fate and built state) and
definition (searched for droids and the ship); the fluff cuts (the Stillsand section); the campaign lore (pressures
and fuel). Not read: the review's sections 1 to 7 and the rest of its slate; turn three's sections 2.4 and 2.7 past
their openings and its scorecard; the fill-out's review notes; the cast bible's cast entries and art queue; the
tree's `tree.json`, `scenes.json`, `plan.md`, `log.md`, `coverage_verdict.json`, exam files and stage-two and
stage-three reviews; the cleanse's `tickets.md`, `bars.json`, `models.md`, `ambiguities.md`, `review.json`; the
Designer rehearsal's notes and questions; the Stillsand table of `special_mechanics_review_2026-10-22.md`;
`design/MOVING_DUNES_DESIGN.md`; the shared names docs.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `dune_sea.md`, `deep_desert.md`, `stillsand_bedazzle_2026-09-27.md`,
`stillsand_bedazzle_review_2026-09-29.md`, `stillsand_turn3_development_2026-09-30.md`,
`stillsand_roster_fillout_2026-09-27.md`, `rosters/dune_sea_deep_desert.json`.

Hold until the art is wired or the art ledger has the same rows: `stillsand_bedazzle_cast_2026-09-30.md` (it is the
commission record for 61 art jobs).

Not for deletion: everything else in `design/concepts/Stillsand/` (the tree, the root and the cleanse are the
pipeline's own records; the cleanse is superseded by this design and was never applied); the validation walk; the
shared names docs.

Before deleting: both sheets are frozen by `BIOME_FREEZE_FABLE_REVIEW_1` and are cited by section number from the
tree's `sheet.md`, from the build items of 2026-09-30 and from other biomes' sheets (the Long Shade's reads against
them). `deep_desert.md` holds the only statement of the sarlacc carve-out for held water, which the sarlacc's own
build cites; that paragraph should move to the sarlacc's design first.
