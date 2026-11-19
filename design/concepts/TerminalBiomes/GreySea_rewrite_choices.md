# The Grey Sea: what the rewrite chose, what it lost, and why

Companion to `design/concepts/TerminalBiomes/GreySea_design.md`, written 2026-11-18 by the same pass. Its job is to
let the older Grey Sea files be deleted without fear: every distinct idea found in any source has a row saying what
became of it. None of the Grey Sea's older source files has been deleted. The files this design could replace, and
the ones it must not, are listed at the end.

**Why this page exists.** Earlier the same day one pass wrote all four seas as one design and one choices page
("the four-seas design"; retired on 2026-11-18 and kept only in git history, commit `b2530669e5`) and said of
itself that it read thirteen of its source files by heading only. This pass read the Grey Sea's own sources to their ends (the list and the count are at the bottom) and
searched the rest of `design/` and the ledger for the Grey by name.

## What the fuller read changed against the four-seas design

The four-seas design is retired; this list is the record of what was wrong or missing in it for the Grey Sea.

1. **The catch is four kinds and a rare table, not thirteen, and the cast is nine animals.** The four-seas design
   quoted the card of 2026-09-27 (*"keep all 13, rebalanced rare"*). His card of 2026-10-12 replaced it: *"Sallik in
   the Grey Sea → Remove from the Grey Sea only"*. Seven catch creatures and their living bodies left the Grey that
   day; the pillar-snail had been deleted by card on 2026-10-08. The source (`RM_GreySea.xml`) agrees: nine animals,
   four catch rows.
2. **A crusted ship can always tear free.** His card of 2026-10-08, recorded on the ledger: *"forced (tear-free)
   launch always available, costly, damages hull; no blocker-naming required."* Built the next day. The four-seas
   design did not mention it. It is the Grey's answer to the day the Empire arrives.
3. **The Brine Crown's retraction is a picture only** (card, 2026-10-19: *"brine crown retraction → picture only"*).
4. **The lamp's three steps are in 0.1.0 here** (the four-seas design put them in 0.2.0). Reasons under "Scope
   moves".
5. **Three ship ideas were declined on this sea,** and are listed under `NEEDS HIM` in the design with their dates,
   as the brief for this run asks.
6. **The statuary is built as blocks of salt, not as figures.** The sheet's *"crystal-encased soldier... furniture,
   relic, and museum in one object"* is not a def. Said plainly in the design, and put in 0.2.0.
7. **He asked for a second watching creature here** (typed card, 2026-10-08), designed and unbuilt. The four-seas
   page did not find it.
8. **The Twilight's salt blade was moved to the Grey by his word** (2026-10-07, in the def's own comment: *"This
   sounds like something from the Grey sea, not twilight. Move it there"*).
9. **The first dependency is sharper:** the ship's descent is built to its offline level and blocked on a live
   read; sea tiles on the older campaign-tier biome get the generic empty floor until the repaint.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the
overriding priority"*. The Grey was already written for a ship (his rulings made the ship the only door on
2026-09-26), so the lens changed little about what the sea is and a good deal about what its first version shows.

**Whose word won where sources disagreed.** His latest dated words first; then card answers; then the cleanse
proposal of 2026-11-17. The cleanse was checked line by line against earlier owner answers. It deferred the hull
crust, which he had typed himself on 2026-09-26 and whose every detail he had ruled; his ruling of 2026-11-18 (hull
wear in 0.1.0) settles that the other way. It deferred the lamp response, which exists because he sent it here. It
kept the roster exactly as his card of 2026-10-12 left it, and it kept no idea he had rejected.

His four rulings of 2026-11-18 (3:10 PM PST) are applied, not asked: stop length as an outer edge (about six weeks
on the floor, a month on the open beach); cover from orbit (the floor one step, the beach none); fuel (emergency
only, bought on the shore with salt); and wear on the hull from the sources (crystallisation, already designed,
ruled and built).

**Words used in "what happened".** *kept* (a bucket in brackets where it is not 0.1.0); *kept, reshaped* (changed as
stated); *moved* (scope bucket changed against the cleanse proposal of 2026-11-17, from and to given; the cleanse
used "first version" and "next version, switched off"; a cleanse "next version" item that lands in "later" is not
counted as a move); *folded into shared machinery*; *lost*.

## The ones I would look at

1. **The seven that left.** His card of 2026-10-12 cut the sallik family from the Grey, and this design obeys it.
   But their catch texts are the best small writing in the sea, and the roster records their *"defs kept, cast nowhere"*. The haarn:
   *"Divers who find one do not report it, on the grounds that it seems to have been minding its own business."*
   The immu, *"the most timid thing in the Grey and the only one with any colour, a faint sick pink"*. The sallik
   that *"becomes a pebble"*. They need a home somewhere or they are lost in fact.
2. **The lamp in 0.1.0.** My least certain move. It is built, it is his own redirect, it all happens inside a day,
   and without it the first version's two great animals are almost never seen (the giant and the fessk are the
   rarest rows on the roster; the lamp is what brings them). Against it: one more system to prove before the mod
   can pass.
3. **The Brine Elders.** His own paragraph, entire. 0.2.0 here and asked under `NEEDS HIM`. *"Their trade therefore
   feels less like commerce than negotiating with a geological intelligence that has spent tens of thousands of
   years quietly collecting one specimen of anything genuinely new."*
4. **The statuary as things to carry off.** *"Half the value IS the case."* Built as blocks that yield salt. I put
   the figures in 0.2.0; a scavenger crew would call them the whole point of the stop, and a case can be made for
   0.1.0.
5. **The pillar law.** *"All travel below is pillar-to-pillar... a lost diver is someone who missed one pillar."*
   He ruled it story only on 2026-09-27. Lost as a mechanic, rightly by his word, and the best idea the sheet had.
6. **"One day this will all stand in open air (the sea is dying), and someone will walk the statuary dry-shod."**
   Nothing a visit can show. Lost from the design; the sheet calls it *"plot soil"*.
7. **A clock for being outside the hull.** The dive specification designed one (deep exposure, healed under any
   roof). It was not found in source, and this design does not ask for it: the Grey already has a clock, on the
   hull. That leaves Jawa in robes walking about on a sea bed with nothing said about air.
8. **The beach.** The shore's own sheet (`terminator_sea.md`) is a whole design of its own: fog nets, cisterns,
   *"one black sail on a white pan"*. Almost none of it is in a design about a ship on the floor, and the beach
   section here is thin. Nobody should delete that sheet on the strength of this page.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section. Where the four-seas design of 2026-11-18 chose differently, that is said.

- **Hull rime, salted doors, crust and the waiting launch:** next version → 0.1.0. His typed words; built; his
  ruling of 2026-11-18. (Same as the four-seas design.)
- **Tear-free launch:** next version → 0.1.0. It is the never-trapped half of the same system, by his card.
- **The lamp: light-seekers, the watcher at the rim, scrape-marks, the giant that breaks the lamp:** next version →
  0.1.0. (The four-seas design: 0.2.0.) See "The ones I would look at", 2.
- **The orruhmu's squirt:** next version → 0.2.0. Its body stays in 0.1.0 as ordinary life.
- **Contact damage from the sphere plant and the Brine Crown:** next version → 0.2.0.
- **The Brine Crown's retracted picture:** next version → 0.2.0. (The four-seas design: later.) It is a picture
  only, by his card, and it is the visible sign that salt snow has started.
- **The Brine Elder's trade, discharge and treasures:** next version → 0.2.0; asked.
- **Lit ground yielding more:** not a line in the cleanse → 0.2.0. Ruled by card 2026-09-26; not found in source.
- **Figures in the statuary, and this visit's dead joining it:** not in the cleanse → 0.2.0.
- **The watcher that hides in place:** not in the cleanse → 0.2.0.
- **Forty colonists on a floor and the whole-sea season model:** first version → later. Colony scale.
- **Stated for the first time, in no source:** the floor as one step of cover and the beach as none; lamps and
  loudness as one mistake; salt as what the crew pays the shore with; the Elder as a customer for junk; the crusted
  deck as the Grey's whole part in the Empire's arrival.

## Every idea, row by row

Source names. In `design/Jawa/worldbuilding/biomes/`: *sheet* = `the_grey_deep.md`; *drop* =
`the_grey_deep_content_2026-09-26.md`; *danger pass* = `the_grey_deep_danger_floor_pass_2026-09-27.md`; *flora
pass* = `the_grey_deep_flora_pass_2026-09-27.md`; *sentinel* = `grey_deep_pool_sentinel_2026-09-27.md`; *agenda* =
`grey_deep_sitting_agenda_2026-09-27.md`; *shore sheet* = `terminator_sea.md`; *cast proposal* =
`terminal_seas_cast_proposal_2026-09-25.md`; *roster* = `rosters/the_grey_sea.json`; *Twilight danger* =
`the_twilight_deep_danger_pass_2026-09-27.md`; *Miasma sheet* = `the_miasma.md`; *freeze rulings* =
`_freeze_rulings_2026-09-07.md`. Elsewhere in `design/`: *catch rosters* =
`Jawa/worldbuilding/sea_catch_rosters_2026-09-24.md`; *landmarks* = `Jawa/worldbuilding/enrichment/grey_sea.csv`;
*world definition* = `Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md`; *legacy index* =
`Jawa/worldbuilding/rakatan_legacy_index.md`; *mechanoid draft* =
`Jawa/worldbuilding/mechanoid_biome_presence_draft.md`; *Deepwater cast* = `Jawa/bridge/INHABITED_CAST_DEEPWATER.md`;
*shields* = `Jawa/proposals/ship_shields_deep_design.md`; *dive spec* = `RimMandrake/sea_dive_maps_spec.md`;
*surface removal* = `RimMandrake/sea_surface_removal_2026-11-01.md`; *floor census* =
`RimMandrake/sea_floor_census_2026-10-29.md`; *mechanics review* =
`RimMandrake/special_mechanics_review_2026-10-22.md`; *code review* = `RimMandrake/gpt_reviews/TerminalBiomes.md`;
*design pass* = `RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`; *watcher pitch* =
`RimMandrake/watcher_creatures_pitch.md`; *wreckage design* =
`RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md`; *minerals design* =
`RimMandrake/minerals_where_they_belong_design_2026-10-02.md`; *gear matrix* =
`RimMandrake/exposure_gear_matrix_spec.md`; *scope cuts* = `RimMandrake/world_remake_2026-10-19/04_scope_cuts.md`;
*experiences* = `RimMandrake/biome_experiences_2026-10-20.md`; *walk* =
`validation_walks/RimMandrake/TerminalBiomes.md`; *four-seas design* and *four-seas choices* = the
retired combined design and its choices page (git history, commit `b2530669e5`). The cleanse folder
(`concepts/TerminalBiomes/cleanse/`): *cleanse definition*, *cleanse pages* (`owner_pages.md`), *cleanse
ambiguities*, *cleanse next version*, *cleanse models*, *cleanse tickets*, *cleanse census*, *cleanse bars*,
*cleanse review*, *cleanse converge*, *cleanse fixes*, *cleanse result*, *cleanse run*. Ledger items
(`infrastructure/state/items/`, `closed/` for the finished ones), each named by what it is about: *floor pass item*
= `GREYSEA_FLOOR_PASS_1`; *ruled content item* = `GREYSEA_RULED_CONTENT_1`; *anchors item* =
`GREYSEA_ANCHOR_CREATURES_1`; *hull crust item* = `GREYSEA_HULL_CRUST_BUILD_1`; *never-strands item* =
`CRUST_NEVER_STRANDS_1`; *lamp item* = `GREYSEA_LAMP_RESPONSE_BUILD_1`; *shore item* =
`GREYSEA_SHORE_MUTATOR_SPECIFICS_1`; *walk check item* = `GREYSEA_FLOOR_WALKABLE_CHECK_1`; *dome scatter item* =
`GREYSEA_SALTDOME_SCATTER_OOB_1`; *roster probe item* = `RIMMANDRAKE_FIX_GREY_ROSTER_PROBE_SALLIK_CUT_LEFT_NINE`;
*weapon config item* = `ELDER_UNKNOWN_WEAPON_CONFIG_1`; *novelty alias item* = `ELDER_NOVELTY_KEY_ALIAS_1`;
*treasure hook item* = `ELDER_TREASURE_PROOF_HOOK_1`; *fishables item* = `SEA_FISHABLES_ALIVE_IN_DEPTHS_1`; *floor
dressing item* = `TERMINAL_SEAS_FLOOR_DRESSING_1`; *generators item* = `SEABED_FLOOR_GENERATORS_1`; *hatch item* =
`SEA_DIVE_HATCH_REMOVE_1`; *descent item* = `SEABED_DESCENT_ASCENT_1`; *sea beasts item* =
`SEA_BEASTS_TIER_RULING_1`. *ledger* = the dated owner rulings in `infrastructure/state/ledger/events/`, read with
`src/RimMandrake/rimflow/owner_rulings.py`.

### The frame

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Ship or nothing: no pawn dives or returns alone | dive spec; agenda; ledger | kept, quoted | | |
| The ship flies to the floor as a planet layer; the hatch is a leftover | dive spec; hatch item; descent item | kept; the descent's unproven state is the design's first dependency | | |
| Each sea's floor content generates on the layer | generators item | kept | | |
| Floor or beach; no place on the surface | surface removal; shore sheet; ledger | kept, quoted | | |
| Seven of the seventeen open wording calls touch the Grey | surface removal | kept where they are; not settled here | They are his to word. | |
| A sea describes both its floor and its catch; every fishable is alive below | fishables item; cast proposal; floor census | kept as a promise | | |
| A floor stays generated between visits; floors are 100 by 100 | dive spec | kept as build facts | Ruled by card 2026-09-25 for the pocket-map route; unmeasured on the layer. | |
| No raids on a pocket map; what happens to a party if the ship leaves is owed | dive spec | kept, reshaped: both now sit under the first `NEEDS HIM` question | The floor is a layer tile now, so the pocket-map fact no longer answers it. | |
| A clock for being outside the hull (deep exposure), air-bells, a floor temperature | dive spec; gear matrix | lost | Not found in source; the Grey's clock is on the hull. Flagged above. | Build it: every errand is timed and the stop has two clocks. Medium build, and it competes with the hull for the player's attention. |
| His experience line | walk; experiences; mechanics review | kept, quoted | Typed 2026-10-20. | |
| "The Grey grows salt"; a sea visit has an arrival, a safe edge, temptation, a bad choice, a recovery | cleanse definition; cleanse pages | kept | The Grey's version: the ramp, the pool, the reach, the rescue. | |
| One signature for the whole mod (the Twilight's current); the Grey is land and ordinary life only | cleanse pages; cleanse definition; cleanse ambiguities | kept, reshaped: the Grey gets its hull wear and its lamp in 0.1.0 | His ruling of 2026-11-18 and his typed words of 2026-09-26. | One signature: the Grey's first version is scenery with a deadly pool. |
| A legal landing keeps hull and working route clear of the hazard | cleanse definition; cleanse models | kept as a build rule | Here: a berth clear of pools and plumes, and a walkable floor. | |
| Forty colonists on a floor; the whole-sea season model | cleanse definition; cleanse models; cleanse bars | moved (first version → later) | Colony scale. | |
| Five offline models and the instrument tickets | cleanse models; cleanse tickets | kept as they stand | Pipeline instruments, not Grey design. | |
| The proposed bars' Grey clauses: mineral shapes readable through murk; a caught clam has a living counterpart; Grey fauna solitary | cleanse bars; cleanse review; cleanse converge; cleanse fixes | kept, reshaped: carried into the design's promises table | The reviewer's point that *"disappear into Grey murk"* reads as a failure is kept as a control. | |
| The cleanse run's counts and records | cleanse result; cleanse run | kept as history | | |
| Next-version settings shipped off | cleanse tickets; cleanse next version | kept, reshaped: hull and lamp settings ship on | They moved into 0.1.0. | |
| Inert cross-biome switches | cleanse next version; cleanse tickets | lost | Not the Grey's; the cleanse's recommendation to drop them stands on its own page. | |
| The four-seas design's Grey section and rows | four-seas design; four-seas choices | kept, reshaped: replaced for this sea, with the nine differences listed above | A fuller read. | Not open: the four-seas page was retired on 2026-11-18. |
| The floor pass's closing condition: he walks the floor live | floor pass item | kept as a stated dependency | | |
| Per-question build list of the 2026-09-27 rulings | ruled content item | kept, reshaped: its catch row is superseded by the card of 2026-10-12 | His later card wins. | |

### The floor itself

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Pillars in grey murk, a lake with shores at the bottom of a sea, and the dead standing in crystal where they sank" | sheet | kept, quoted | | |
| The statuary: everything not eaten is jacketed forever; "everything that dies there keeps" | sheet | kept, quoted | | |
| The planet's three ways of preserving (tar, scar, brine): "the brine keeps the shape" | sheet | lost | Lore across three biomes. | A world document. |
| The murk: sight in meters, "navigated, not seen" | sheet | kept, reshaped: it is how the floor looks, never a penalty | Card, 2026-09-27. | |
| The pillar-mason, pillar-to-pillar travel, waymarks, the lost diver | sheet; anchors item; agenda; floor dressing item | lost as a mechanic; kept as story on the built pillars | Card, 2026-09-27: story only. Flagged above. | Carved waymarks with a small benefit (the agenda's own recommendation): one job, one bonus, and a ruling reversed. |
| "The masons never stop; charts age" | sheet | lost | Seasons. | |
| Pillars as mineable formations | agenda; roster; minerals design | kept | | |
| Salt domes "like mushrooms growing, strange shapes everywhere" | drop; sheet | kept, quoted | | |
| Salt chimneys venting white super-brine; the plume crystallises at short range | drop; sheet | kept, quoted | Ruled 2026-09-26: the visible teacher. | |
| Brine channels from chimney field to pool; the gradient points at the danger | drop; sheet | kept, quoted | | |
| Huge salt crystals, "harvestable and rather valuable", in four colours, well apart | drop; sheet; minerals design | kept, quoted | | |
| Coloured salts as cooking ingredients; the palette ratified | drop; agenda | kept | They are what the crew pays the shore with. | |
| Salt falling like snow; rain removed from the sea | drop; sheet; cleanse census | kept | | |
| "Marred slightly, don't make them too perfect or they look manufactured" | drop; sheet; flora pass | kept, quoted | His one art rule. | |
| The four reference images | drop; sheet | kept as art direction | The paths are in the sheet. | |
| Brine below brine: pools with their own surfaces and shores | sheet | kept, quoted | | |
| The deepest pool carved and ringed with jacket | flora pass; agenda | kept | | |
| A floor that stays walkable after decoration | walk check item; design pass | kept | | |
| A scatter step that read off the map on other biomes | dome scatter item | kept as history | A closed defect. | |
| Position, tile counts, measured temperatures | sheet; roster | lost | The planet is painted at the end. | |
| "One day this will all stand in open air... walk the statuary dry-shod" | sheet | lost | Nothing a visit shows. Flagged above. | A plot thread, later. |
| "Everything soluble concentrates downward" | sheet | kept | It is why salt is the prize here and nowhere else. | |
| World-map landmarks for the sea's tiles | landmarks | lost | The planet is painted once. | |
| The sea's colour on the world map ("lighter and clearer") | ledger | lost | World-map art, not a stop. | |

### The pools and the crystal

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The crystallisation defence: one mechanism, three triggers | drop; sheet | kept: pool and plume in 0.1.0, the creature's squirt in 0.2.0 | | |
| A crystallised pawn is encased as an object and mined out | drop; sheet | kept, quoted | Ruled 2026-09-26. | |
| Smothering as a timer on the jacket; a wide rescue window; an alert | sentinel; mechanics review | kept | | |
| The jacket mineral, one substance for statuary, loot, pawn and hull | drop; sheet; danger pass | kept | | |
| "Loot within the pools is ultra-protected until the player figures out how to get at it" | drop; sheet | kept (later) | A puzzle for a crew that stays; the keys are a chisel and an Elder. | 0.2.0 with the Elder: the pool gives something up on screen. |
| No survivable entry to a pool | sheet | kept | Ban 1. | |
| No decay of the encased | sheet | kept | Ban 5. | |
| A corpse left on the floor joins the statuary | dive spec | moved (not in the cleanse → 0.2.0) | Not found in source; a visit's dead becoming exhibits is on the lens. | Leave it out: no cost. |
| The statuary as encased soldiers and vehicles worth carrying off | sheet; wreckage design | moved (not in the cleanse → 0.2.0) | Built as blocks of jacket. Flagged above. | 0.1.0: the scavenger's prize is there from the first stop; new defs and art. |
| A crystal-jacketed wreck field on the floor | wreckage design; generators item | kept | | |
| The heavier pool liquid as its own grade | sheet | kept as a build debt | | |
| Minerals dip-harvested at the pool shores | sheet; dive spec | kept (later) | Industry. | |
| The launch warns when someone is still held | mechanics review | kept | | |

### The hull

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The grey sea should crystallize the hull, freeze doors shut" | danger pass; Twilight danger; ledger | moved (next version → 0.1.0), quoted | His typed words; his ruling of 2026-11-18. | Next version, as the cleanse had it: the Grey's first version does nothing to the ship. |
| "Each sea claims a parked hull in its own register"; one launch-gate pattern, one never-strand bar, one rule that removal pays | danger pass; Twilight danger | folded into shared machinery | The Grey is the worked example. | |
| "The ship is not being attacked. It is being filed" | danger pass | kept, quoted | | |
| Doors first; salted from outside, forced from inside; never a tomb | danger pass; agenda | kept, quoted | Card, 2026-09-26. | |
| The sea pays you | danger pass; agenda | kept, quoted | Card, 2026-09-26. | |
| No heat or fuel traded for time | danger pass; agenda | kept as a ban; listed under `NEEDS HIM` | Card, 2026-09-26. | |
| The ladder: rime, then doors, then crust; its day counts | agenda; hull crust item; walk | kept, reshaped: the order is promised, the days are tuning | A passing bar is an experience. | |
| Weather and berth change the pace; nothing purchasable ever | agenda; sheet; hull crust item | kept, quoted | Card, 2026-09-27. | |
| A launch that waits for chipping and says why; never against a launch in progress | danger pass; hull crust item | kept | | |
| The tear-free launch | never-strands item; design pass; ledger | moved (next version → 0.1.0) | Card, 2026-10-08. | |
| The fully jacketed hull as a thing shown, not suffered; the wreck nobody chipped | danger pass | kept (later) | A season of neglect. | |
| Crust state rides with the ship | danger pass | kept | | |
| The crust clock belongs to the berth; salt could be lost from a door in flight | code review; design pass | kept as build debts | Listed in the design under "Found while reading". | |
| Switching the mechanic off left doors locked | code review | kept as a build debt | "Off" has to mean off. | |
| The review's verdict: "the biome's one real clock" | mechanics review | kept | It agrees with the move. | |
| No field holds out water | shields | kept, quoted | His ruling of 2026-09-02. It is why no shield answers the crust. | |

### The lamp

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Actually attacking light makes more sense in the Grey and Scald (dark on the bottom)" | danger pass; Twilight danger; ledger | moved (next version → 0.1.0), quoted | Built; his redirect; seen inside a day. Flagged above. | 0.2.0, as the four-seas design had it: the first version's giant and watcher are rarely seen. |
| The small sighted things drift into the light | danger pass; lamp item | kept, reshaped: two of the three named animals were cut on 2026-10-12 | Whether the clam still comes is unmeasured. | |
| The fessk at the rim, never entering | danger pass; agenda | moved (next version → 0.1.0), quoted | With the lamp, above. | 0.1.0 alone, without the giant: the cheapest dread in the sea, and a warning of nothing. |
| The giant reads a steady light as a rival's mark and breaks the lamp, not the ship, not the pawns | danger pass; agenda | moved (next version → 0.1.0), quoted | With the lamp, above. | |
| Deterministic and forgiving: never a torch, hours of burn, dowsing resets | agenda; lamp item; walk | kept | Card, 2026-09-27. | |
| Lit cells yield more | danger pass; agenda | moved (not in the cleanse → 0.2.0) | Ruled; not found in source. | 0.1.0: the lamp has a bribe as well as a price; small build. |
| Fresh scrape-sign means the giant is near | sheet; cleanse census | kept, quoted | | |
| Light discipline as the Grey's survival craft | danger pass | kept, reshaped: tied to cover from orbit | New reading, flagged in the design. | |
| The same mechanism is owed to the Scald | danger pass | kept as a pointer | Another sea's. | |
| One setting per lamp step | danger pass; lamp item | kept | | |
| A lamp that shows how long it has burned | design pass | kept | Whether it is built for the lamp is unmeasured. | |

### The animals

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Solitary everything; one endemic giant; "do we already have one?" | sheet; shore sheet | kept | | |
| The cap of three released; nothing schools in the Grey | sheet; catch rosters | kept | | |
| The crusted giant: ill-tempered, armoured in its own mineral, a pillar until it moves, one saturated mark | sheet; anchors item; roster | kept, quoted | | |
| The giant ships as the reefback, one of the eighteen sea beasts ("Don't get rid of any of them") | anchors item; sea beasts item | kept | Its shipped description reads against the no-glow ban; noted in the design. | |
| The giant's adults come from the Miasma's nursery; a route between the two is owed | sheet; roster; freeze rulings; Miasma sheet | kept (later) | A life longer than any visit. | |
| The ossuary shrimp, the fessk: man-sized, shy, never attacks, never tamed; "the shrimp saw you first" | sheet; cast proposal; anchors item | kept, quoted | | |
| The ribbon-swimmer above the pools; the statuary-grazer | cast proposal; roster | kept | | |
| The pillar-snail | cast proposal; roster | lost | Deleted from the game by card, 2026-10-08. | |
| The donor drifter cut; a drifter of ours in its place | anchors item; roster; ledger | kept | Card, 2026-09-26. | |
| The sessile layer: a clam, a mussel and a small shrimp, all new; abundance as placement, never a group | drop; sheet; roster; cleanse ambiguities | kept | Ruled 2026-09-26; reaffirmed by card 2026-10-12. | |
| Seven living bodies for the seven catch creatures | danger pass; fishables item; catch rosters | lost | Card, 2026-10-12: removed from the Grey only; defs kept, cast nowhere. Flagged above. | None here; they need a home in another water. |
| Four small behaviours built for them (scrape-line, pebble-freeze, sealing, shell-lodging); the shell-fish and its lodger travelling together; the small scrape as a false sign of the giant | danger pass | lost | They left with their animals. The scrape-mark itself stays as the giant's sign. | |
| The orruhmu: a salt dome that breathes; the owner's name for it | sentinel; agenda; roster | kept | Ruled 2026-09-27. | |
| Its squirt: two or more in reach, one swell of warning, the nearest encased, a long rest | sentinel; cleanse tickets; cleanse next version | moved (next version → 0.2.0), quoted | "Two are a crowd" was written for Jawa. | 0.1.0: the best joke in the sea is in the first version; one more trigger to prove. |
| It is never caught, never tamed, and its squirt is never harvested | sentinel | kept | | |
| Its stats, art brief and wiring notes | sentinel | kept as build and art direction | | |
| The review's question whether the sentinel "was ever designed" | mechanics review | kept, reshaped: answered | Designed 2026-09-27 and built. | |
| "That is not a watcher, that's its own creepy thing. Add an independent watcher that hides in place." | watcher pitch | moved (not in the cleanse → 0.2.0), quoted | His typed card of 2026-10-08; designed, unbuilt. | Later: one creature fewer to draw and build. |
| Campaign-tier animals a review sheet sent to the Grey (a lamprey, an elder giant, and others) | roster | kept where they are | Rows on a review sheet; evictions are stopped; this design touches no roster. | |
| No ancient machine wakes on this floor | mechanoid draft | kept, quoted | A draft; it suits the stillness. | |
| The roster reads as nine | roster probe item; floor census; cleanse census | kept as a measured fact | | |
| His brief for the Grey's creatures: "timorous, sickly, extremophile, or alien saline creatures often with crusty bits and shell" | catch rosters | kept | The register for anything added later. | |

### The catch

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "There should be fish" / "But bizarre creatures of course" | floor pass item; roster; ledger | kept | Typed 2026-09-26. | |
| The older no-fish ruling | catch rosters; cast proposal; roster | kept as history | Superseded twice. | |
| Thirteen catch kinds, all kept, rebalanced rare | agenda; ruled content item | lost | Replaced by the card of 2026-10-12. | |
| The catch as it stands: four kinds and a rare table, a smaller fish population | roster; floor census | kept | | |
| The rare table: a creature in crystal, a ring in its jacket | catch rosters; roster | kept, reshaped: the "bed of the sealed" option left with its animal | Card, 2026-10-12. | |
| Catch names moved to the free tier | danger pass; catch rosters | kept | Done. | |
| The seven catch texts | catch rosters | lost | Their animals are cast nowhere. Flagged above. | |

### The plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The crystalline idea: green tissue inside salt armour; pink, violet, amber | drop; sheet | kept, quoted | | |
| The seven forms, his specifications verbatim | drop; sheet; roster | kept, part quoted | The drop stays the authority for any def. | |
| The sphere plant and the Brine Crown hurt to touch | drop; sheet; cleanse tickets | moved (next version → 0.2.0) | Ruled 2026-09-26: low damage. | |
| The Brine Crown pulls its membranes in when the salinity shifts | drop; ledger; cleanse tickets | moved (next version → 0.2.0) | Card, 2026-10-19: picture only. | Later: no cost in play. |
| The Brine Crown feeds on the small things it traps | drop | kept as lore | | |
| Five places the drop seemed to cross the frozen sheet, all ruled additive | drop; sheet; agenda; ledger | kept | Reaffirmed by card 2026-10-12. | |
| No plant or creature that glows | sheet; flora pass | kept | Ban 4. | |
| Ten small grey plants between the monuments, all shipping; the density ruled | flora pass; agenda; ruled content item | kept | Cards, 2026-09-27. | |
| The mason's skirt as a plant | flora pass; agenda | kept | | |
| The salt-sweating beard; young beard on a scrape means an old scrape | flora pass | kept | | |
| The net that sorts food from salt, bowed white after a salt fall | flora pass | kept | Description on a still picture. | |
| The sponge that makes gentle water: "a well running upward, a spring at the bottom of a sea" | flora pass; agenda | kept; its halo is prose only | Card, 2026-09-27. | Later: small creatures gather in its water (the card's "good later door"). |
| The coral that turns itself to stone on a schedule | flora pass | kept | | |
| The plant that is usually a puddle | flora pass | kept, quoted | | |
| The pool lily, out of reach on the pool's skin | flora pass; agenda | kept, quoted | Card, 2026-09-27. | |
| The combs along the channel beds | flora pass | kept | | |
| The sprig salt cannot take: pure dressing | flora pass; agenda | kept; any product from it is dropped | Card, 2026-09-27. Listed under `NEEDS HIM`. | Later: a sprig that speeds cutting someone out (the card's only acceptable opening). |
| The cushion with colour only under a lamp | flora pass; agenda | kept, quoted | Card, 2026-09-27. | |
| Plants and animals wired as one system | flora pass | kept, reshaped: the snail's pasture and the pebble-crab's shelter lost their animals | Cards, 2026-10-08 and 2026-10-12. | |
| The tall salt-rimed blades, the Grey's and the one moved here from the Twilight | roster; shore sheet; floor dressing item | kept | His word of 2026-10-07. They are shore plants on a floor list; noted as unsettled. | |
| How the plants are placed (by density, and beside formations and pools) | flora pass | kept as build notes | | |

### The Brine Elders

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| His paragraph, entire | drop; sheet | moved (next version → 0.2.0); asked under `NEEDS HIM` | Flagged above. | 0.1.0: the first version has its mind; about eleven hundred untested lines to prove. |
| "ONLY grey sea, but there's one per grey sea tile"; each keeps its own set, so the tiles are a spread-out market | drop; sheet; ledger | kept (0.2.0), quoted | A reason to move the ship. | |
| The discharge: a defence and a rare event; the warning is motion, crackle and sound only | drop; agenda | kept (0.2.0), quoted | Ruled 2026-09-26 and 2026-09-27. | |
| "Cripple nearby ships" as its own engine check | drop; sheet | kept (0.2.0) as an open check | Not built. The crew's ship is a nearby ship. | |
| "The Reshapers" are the Rakata, in the Elders' own word | drop; legacy index | kept, quoted | Ruled 2026-09-26. | |
| The trade in novelty: precious once, worthless after; a colonist of a new kind is an offering | drop; sheet | kept (0.2.0) | | |
| The resonant storage crystal | drop | kept (0.2.0), quoted | | |
| Six treasures, one of each; three are canon and belong to the campaign layer | drop; design pass; treasure hook item | kept (0.2.0) | The three canon ones cannot yet be added there. | |
| The sixth treasure waits for a plot | agenda; ledger | kept (later) | Card, 2026-09-27. | |
| A treasure that could be crafted for nothing | weapon config item | kept as history | A closed defect. | |
| A renamed creature is not new to an Elder twice | novelty alias item | kept | Built. | |
| The Elder's voice: what changed in the water, never who or why | drop | kept (0.2.0) | | |
| A second colossal organism beside the one giant | drop; sheet | kept | Ruled additive. | |
| The specimen cabinet | mechanics review | kept (later) | Colony furniture. | |
| "Is it a found rite worth keeping or a fluff trade window?"; a proposal to cut sea depth to a minimum | mechanics review; scope cuts | kept as the evidence against, under `NEEDS HIM` | Neither is decided. | |

### The shore

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The crusty whiteness that should be on every Grey Sea shoreline"; crust and domes; no shore salt | drop; sheet; shore item | kept, quoted | Ruled 2026-09-26. | |
| "Make sure the shore mutator respects the specifics of the grey sea" | shore item | kept | Typed 2026-09-26; closed as built. | |
| "A white salt pan under a permanent horizontal wind"; shadows a kilometre long | shore sheet | kept, quoted | It is why the beach has no cover. | |
| The lush rule in three parts; why the seas are dying; the one-way wind | shore sheet | lost | The whole planet's lore. | A world document. |
| The sea is not drink; fog is; fog nets, cisterns | shore sheet | kept, reshaped: only "not potable" is carried | The rest is the shore's land. Flagged above. | A beach design of its own. |
| The black blade and its shadow lane as the only habitat | shore sheet | kept, reshaped: the blades are kept as plants, the lane as a habitat is not | The lane is the shore's land. | A beach design of its own. |
| Giants because bigger keeps its water; a player who kills the last one has killed the last one | shore sheet | kept as lore | | |
| The shore's weather bans | shore sheet; surface removal | kept for the beach | One of the open wording calls. | |
| Salt works stranded inland; holdings in the lee of a blade; salt-buried ruins | shore sheet | lost | The campaign layer's shore. | |
| The boundary with the poison forest | shore sheet | lost | A map rule. | |
| Who lives round the Grey: Homestead, Trade Moot, Junkers, Free Droids, thinned by his order of 2026-08-24 | world definition | kept | They are who sells. | |
| Tidewatch: "The Compact holds it anyway" | Deepwater cast | kept, quoted | | |
| Deepwater's sounding lines over the sea | sheet | kept (later) | Scenery for a sea that is being measured as it dies. | |

### Look and sound

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Grey murk, pale pillars, and the dead standing at attention"; light, palette, silhouettes, motion, sound | sheet | kept as art direction, part quoted | | |
| The 2026-09-26 additions to the theme | sheet | kept | | |
| "The sea precipitates itself onto you; stillness is death" | Twilight danger | kept, quoted | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's split of the Grey into land, life and extras | cleanse census; cleanse definition | kept, reshaped: with the moves listed above | The lens, and his ruling on hull wear. | |
| Its six switched-off Grey extras | cleanse next version; cleanse tickets | kept, reshaped: two come into 0.1.0, four into 0.2.0 | See "Scope moves". | Leave all six off, as the cleanse had it. |
| "Sparse" means solitary animals, not bare ground; a rooted animal is still alive; a species' extra is not its body | cleanse ambiguities | kept | | |
| Mineral ground and salt fall never become cold snow or rain | cleanse definition; cleanse census | kept | | |

## New in this design, in no source

Not rows, because nothing was chosen away. Each is flagged in the design where it stands: the floor as one step of
cover and the beach as none; lamps and loudness as one mistake; salt as what the crew pays the shore with; the Elder
as a customer for junk and its discharge as a hazard to both sides; the crusted deck as the Grey's whole part in the
Empire's arrival; a dead trooper joining the statuary.

## Sources read, and the count

Measured after writing, by a script that reads this page (it counts table rows, the first words of each "what
happened" cell, and checks that every source name defined above appears in at least one row; it was first run with a
made-up source name added, and failed on it as it should):

**44 source files read to the end; 171 rows**, of which **17 lost**, **14 record a move**, **17 kept, reshaped**, 1 folded into shared machinery and 122 kept. Sixty-seven source names are defined above and every one is in at least one row's source column; every file and ledger item they name was found on disk.

**Read to the end (44 files).** In `design/Jawa/worldbuilding/biomes/`: the sheet, the drop, the danger pass, the
flora pass, the sentinel, the agenda, the shore sheet, the cast proposal, the roster. In
`design/concepts/TerminalBiomes/`: the four-seas design and choices (since retired); and in `cleanse/`: definition, owner pages,
ambiguities, next version, models, tickets, census, bars, converge, fixes, result, run (the four large JSON files
were flattened to text by a script and read as text). In `design/RimMandrake/`: the surface removal record, the
floor census. The validation walk. Eighteen ledger items: the floor pass, ruled content, anchors, hull crust,
never-strands, lamp, shore, walk check, dome scatter, roster probe, weapon config, novelty alias, treasure hook,
fishables, floor dressing, generators, hatch, sea beasts.

**Read in part, and which part.** The cleanse `review.json`: both rounds' refusals and the first round's picture
sort; the second round's repeated picture lines were collapsed. `sea_dive_maps_spec.md`: lines 1 to 494 (everything
shared and everything about the Grey); the rest is the Scald's worked design and was searched for the Grey only.
`sea_catch_rosters_2026-09-24.md`: the owner's brief, the reading rules, the Grey section, the rare tables, the
superseded rulings, what is owed and the answered questions; the other three seas' tables were not read.
`special_mechanics_review_2026-10-22.md`: its header, the Grey Sea table and the shared sea-floor table.
`ship_shields_deep_design.md`: the table of his eight rulings. `SEABED_DESCENT_ASCENT_1`: its specification and
reshaping note. `ASHKARR_WORLD_DEFINITION.md`: the section on thinning the Grey Sea's settlements.

**Read by search for the Grey only** (lines found, not files read): `biome_rulings.md`, the code review, the design
pass of 2026-10-08, the Twilight danger pass, the freeze rulings, the Miasma sheet, the Deepwater cast, the legacy
index, the mechanoid draft, the wreckage design, the minerals design, the watcher pitch, the gear matrix, the scope
cuts, the experiences table, the landmarks sheet (its header), `TERMINALBIOMES_RM_MOD_BUILD_1`,
`SEA_FLOOR_AND_CATCH_PASS_1`, `SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR`, and the ledger's dated owner rulings.

**Not read.** A search of `design/` and the ledger's items for the Grey Sea by name returned 277 files. Most are
registers, art job lists, review decks, data tables and other biomes' documents that mention the sea in passing. The
ones not named above were not opened. Among them, the ones a second reader might want: `sea_shore_mutator_spec.md`,
`LIQUID_BIOMES_MAP_1_RECONCILIATION.md`, `fish_bestiary_commission_2026-09-10.md`, `sea_beasts_roster.md`, the
Designer rehearsal folders under `design/RimMandrake/designer_codex_2026-11-09/` (none is named for the Grey), and
`biomes/_assignment_prep.md`.

**Source facts checked in `src/` on 2026-11-18** (by search and by reading the lines found, not by reading whole
files): the Grey's roster, densities, weather and catch rows in `RM_GreySea.xml`; the layer generator's step list;
the Grey's settings; that the lamp response spawns its animals; that no lit-yield code, no corpse-jacketing code, no
second watcher and no Grey breath system were found; that the Elder's source says the ship clause is not
implemented; the hazards the shield tracker knows.

## The older files this design replaces, ready to delete on his word

**For the Grey Sea, two files are fully carried here and hold nothing else:**
`design/Jawa/worldbuilding/biomes/the_grey_deep_danger_floor_pass_2026-09-27.md` and
`design/Jawa/worldbuilding/biomes/grey_deep_sitting_agenda_2026-09-27.md`. Every ruling in them is in a row above
with its date. (Closed ledger items cite both by path; deleting them leaves those citations dangling, which is
ordinary for closed items.)

**Hold, because each is the only specification of something built or still owed:**
- `the_grey_deep.md`: the frozen sheet. Its six bans are checkable law, defs cite it by section, the reference
  image paths live in it, and seven of the open wording calls of 2026-11-01 point at its lines.
- `the_grey_deep_content_2026-09-26.md`: his verbatim drop, which the sheet names as *"the authority for any def"*,
  and the only home of the Brine Elder paragraph.
- `the_grey_deep_flora_pass_2026-09-27.md` and `grey_deep_pool_sentinel_2026-09-27.md`: def and art specifications
  for eleven built things.
- `terminator_sea.md`: the shore's own law, shared with the Twilight, and the beach's only design.
- `rosters/the_grey_sea.json`: the record of the roster cards.
- `terminal_seas_cast_proposal_2026-09-25.md`, `sea_catch_rosters_2026-09-24.md`, `sea_dive_maps_spec.md`: shared
  with the other three seas; this page speaks only for their Grey parts.

**Not for deletion:** `design/concepts/TerminalBiomes/cleanse/` (never applied; superseded for the Grey by this
design, and it should be re-run from the new designs, not applied); the validation walk; the surface removal record.
