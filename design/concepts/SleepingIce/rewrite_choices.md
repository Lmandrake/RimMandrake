# The Sleeping Ice: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A different agent from the one that wrote this page and the design read the sources again, starting with the ones
the first pass read in part or not at all, and checked each idea in them against the rows below.

**Rows added: 84**, in the table "Added by the second reader" at the end of "Every idea, row by row". Two of the
first pass's rows were corrected in place and say so (the tellurox hexplate; the kesshet).

**The three most valuable things the first read missed.**

1. **The hull answer was already his, and already built.** The first design said *"No shared system for hull wear
   was found in `src/`"*. `src/RimUtinni/ShipShields/` wears a landed ship in extreme cold, and his ruling of
   2026-09-02 gives this hemisphere its own shield: the cryo envelope, *"thermal absorptivity. Pulls in heat in both
   directions and allows the shields to start glowing with red-orange black body radiation, holding severe cold at
   bay. But slowly decreases the temperature within the ship... still better than the extreme cold of the night-side
   atmosphere."* A shield that glows red-orange and pulls heat, on the one biome where warmth is what finds you, is
   the best unasked question the Sleeping Ice has. With it came a real doubt: the built tracker calls a map cold at
   forty below, and the sheet measured this biome's median at −33 °C.
2. **The biome's gift to the ship, which the first design recommended dropping.** His instruction of 2026-09-24:
   *"how can this biome uniquely add something to the ship?"* The answer on record, and built, is the tellurox
   hexplate, a deck floor of the pack beast's shell plates, *"the one floor both sterile and beautiful"*. The
   cleanse of 2026-11-17 recommended retiring it and the first read kept that. His earlier word wins.
3. **Who sells fuel on the night side, in his own words.** The first design left it unsettled. On 2026-08-30 he
   said the nightside droids *"generate fuel they sell to the Junkers via long-distance pipes"*, and a closed item
   had already found which two settlements he meant.

Close behind: the hessarn, the ice's own watcher (*"turns a heat-pit face toward warm bodies and draws down into
the crack"*), pitched under his 2026-10-08 ruling that every biome gets one and never given a row; the ice-kept dead
as *"a party roped together"*; the tauntaun *"radiating heat they cannot afford"*; and the cleanse's best line, *"The
next warning is a knock without an arrow."*

**What changed in the design, and why.**

- *Hull:* rewritten onto the built shield frame and the cryo envelope; the false sentence that no hull system
  exists is deleted; the temperature doubt is flagged `UNMEASURED`; the glow is asked (`NEEDS HIM` 3). Nothing
  here is the second reader's invention: every hull wear in the section has a source, named beside it.
- *The two ship ideas he passed here* (the kesshet and the Keel-Press, 2026-10-01) are both listed under
  `NEEDS HIM` 2 with his words. The first read asked about one. Neither is revived.
- *Fuel:* "where fuel is bought" now quotes him. The class is unchanged: emergency route only.
- *Scope:* the tellurox hexplate is in 0.1.0 (built) and out of "recommended for dropping". The hessarn is in
  0.2.0 as a proposal, flagged as never admitted at a sitting.
- *Creatures and lines:* the zhissa's shock now says what it does as built (it can stop a heart); two "did you see
  that" moments added (the roped party; faces in the cracks); six dropped lines carried in.
- *Flags added:* the floored apron may end cracks for good as built (`UNSETTLED`); whether a zhissa or tellurox
  survives being carried to the day side (`UNSETTLED`, against R-H10).
- *Whose word wins:* each cleanse line was checked against his dated answers. Two cleanse calls fall to earlier
  words of his (the hexplate, above; and the zhissa's shock, which his roster note asked for and the first read
  had already moved back). No locked Designer sheet or tree exists for this biome, so nothing is held for a
  Designer run to reconcile.

**Measured counts** (script: `design/RimMandrake/biome_recheck_row_check_2026-11-18.py`, and the reader's own
source list checked against disk): **226 rows** (142 from the first read, 84 added); **32 lost**, **19 moved** and
2 more that record a move in part, 9 kept and reshaped, 1 folded into shared machinery, 164 kept, 1 the script
could not class (a first-read row that begins "sohl moved"). **Sources: 28 read to the end, 25 read in part, 5 not
opened.** Read to the end: all four files this page lists for deletion; the validation walk; the five readable
files of the rehearsal folder; the cleanse's owner pages, next-version list and definition; the titan calls; the
experiences table; the wreck and hexplate defs; the ship-gifts item; and ten ledger items of this biome. Read in
part: the judgment (every verdict, answer and flag; not the judge's brief, which restates the sources); the
rehearsal `record.json` (inventory, scope, decisions, contradictions, failure modes, neighbours; its scene audit
and file list skimmed); the cleanse's ambiguities (all twenty-four, each cut at about 400 characters), models and
tickets (headings, and searched for ship, hull, fuel and owner) and review (searched); the nine organism build
items (spec heads and amendments); and nine shared documents read at this biome's sections. Not opened: the
cleanse's `census.json`, `bars.json` and `converge.json`; `NIGHTSIDEICE_RM_MOD_BUILD_1` and
`HELIX_TELLUROX_BUILD_1` (build logs). Every file not read to the end is one that stays.

DELETE-READY: yes

That line covers the four files listed at the end of this page and nothing else. Two things to do first are
already stated there and still stand: point the nine organism build items at the design, and keep the life draft's
four art briefs somewhere, since the pictures made from them are gone.

Companion to `design/concepts/SleepingIce/design.md`, written 2026-11-18 by the same pass. Its job is to let the
older files be deleted without fear: every distinct idea found in any source has a row saying what became of it.
Nothing has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the
overriding priority"*. The Sleeping Ice bent easily. Its own line already says nobody stays, its law (your warmth is
what finds you) acts in hours and days, and a review had already noticed that *"a landed ship is the hottest thing
on the hemisphere, and that is unclaimed."* The one large change is the same as the Greentide's: the cleanse
proposal of 2026-11-17 built 0.1.0 around a supplied refuge of forty colonists, and this design keeps the same
struggle and makes the refuge the landed ship. The second change runs the other way from the cleanse: it kept only
the tunnelers and pushed every other strange animal out of sight; this design brings the ones a crew can meet in a
week into 0.2.0, because under the lens the creatures are the point.

His four rulings of 2026-11-18 (3:10 PM PST) are applied, not asked: the stop length is stated as an outer edge;
the biome's cover from orbit is stated (none overhead; cold); its fuel class is stated (emergency only, plus
salvaged cylinders); and how it wears on the hull is stated from the sources (cold, and the bitten edge).

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The dhorrumak.** *"Most of it is always under the ice. What comes up is a ringed, toothed mouth and a length of
   body plated in old blue-black scale, rearing out of a crater of broken slabs. It is blind. It came because you
   were warm for too long."* It is the biome's own answer to his question *"is there anything here that forces the
   players to leave before the Empire does?"*, and a warm ship sitting for days is exactly its trigger. I left it in
   "later" because it is the largest build in the biome and its ladder (insects, young, nest, parent) needs the thaw
   first; its foreshadowing young are in 0.2.0. If one thing here should come forward, it is this.
2. **The larder.** *"Tunnelers drag downed and dead pawns under the ice — stored, not eaten."* A crew member taken
   under the ice and fetched back from a pocket below is a whole evening's story, and he has already answered how the
   rescue works (2026-11-10: *"pocket map style"*). It is a second system on top of the first; "later".
3. **The kesshet** (a crust that grows on the warm hull, raises the ship's signature, must be scraped before launch,
   and scrapes to a superconducting film). He passed it on 2026-10-01 with three other ideas in one sentence. It is
   the only idea in any source written about the ship on this ice, and on 2026-11-18 he ruled that every biome wears
   on the hull and that the answer is in the sources. Lost; asked as `NEEDS HIM`.
4. **The Cold Hearth** (a rite, not taken 2026-10-01): *"for one night every heater, fire and powered heat source is
   put out, and every colonist lies still, wrapped."* As a rite it stays dropped. As a plain thing a crew can do, it
   is in the design as the dark ship, with no rite attached and the search above slowing one step.
5. **The sohl.** The cleanse held it back as its runner-up. I moved it to 0.2.0: a mound that has been in view since
   landing lunging once onto the campfire and never moving again is the lens in one image, and it can happen inside
   a stop because its trigger is steady heat within reach.
6. **The zhissa's shock.** Built, and switched off by the cleanse as a separate combat hazard. I moved it back into
   0.1.0. A six-eyed goat that reads by heat and drops a Jawa with static is what the owner asked for in the roster
   (*"make pale blue aura around it"*) and it costs nothing.
7. **The lasting refuge.** His answer of 2026-11-10 allows it: *"Crossing leads; settlement is exceptional."* The
   cleanse made it the measure of the first version. Here it is "later", and the forty-colonist season model goes
   with it.
8. **"A chemistry set the size of a hemisphere, switched off, under the aurora."** The art theme's line. The world
   physics behind it (the distillation column, sorting by basin) is lost from this design as world lore; the line is
   too good to lose and should live in a world document.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **Zhissa electrical defence:** next version → 0.1.0. Built; slapstick in the first day.
- **Sohl:** next version → 0.2.0. The strongest single creature moment a visit can hold.
- **Ice-kept dead:** next version → 0.2.0, as cutting a body out with its gear. Looting the perfectly kept dead is
  very Jawa. The theft of a warm body by the tunnelers waits for the larder.
- **Thaw and calving delivery:** next version → 0.2.0. It is also how the ice wears on a warm ship's footing.
- **Frissim and wyrmlets:** next version → 0.2.0. Small, cheap once the thaw exists, and they announce the parent.
- **Neshkoll and saallen:** next version → 0.2.0. Both make the ship's own heat visible on the map.
- **Heat-drawn assailants:** next version → 0.2.0. *"Who else here attacks and raids?"* is one of his lens
  questions and this is the sheet's ruled answer.
- **Lost soul:** next version → 0.2.0. A rescue with a deadline of hours.
- **Insect-fall:** next version → 0.2.0. Food falling out of the sky onto a plateau with none.
- **Fires, warm rooms and downed living bodies as targets:** the cleanse proposed these as first-version
  completions; kept in 0.1.0 and stated as owner-blind, so that the Empire's warmth counts.
- **Lasting refuge at forty colonists:** first version → later.
- **Stayed "later" from the cleanse's "next version":** dhorrumak and nest, larder and pocket rescue, oolm,
  reconnection storm, margin rime-fall and ablation, drifting Dark, active crevasses, the Cold Ledger. Not moves.
- **New, not in any source:** the ship as the warm thing the plateau notices; a cold ship searched for more slowly
  (a reading of the sheet's *"thermal camouflage"* under his partial-cover ruling); the Empire's fires and downed
  troopers as warmth the tunnelers go to (a reading of the sheet's thermal law); frost-locked cylinders named as a
  fuel find (the salvage table already lists chemfuel).

## Every idea, row by row

Source names: *sheet* = `biomes/sleeping_ice.md`; *life draft* = `biomes/nightside_ice_roster_draft_2026-10-05.md`;
*bedazzle review* = `biomes/nightsideice_bedazzle_review_2026-10-01.md`; *scores* =
`biomes/grandfathered_bedazzle_scores_2026-10-01.md`; *roster json* = `biomes/rosters/sleeping_ice.json`; *names
doc* = `biomes/noncanon_beast_names_crags_nightside_contagion_slime.md` (all under `design/Jawa/worldbuilding/`);
*cleanse* = `design/concepts/SleepingIce/cleanse/`; *walk* = `design/validation_walks/RimMandrake/SleepingIce.md`;
*owner answers* and *rehearsal* = `ANSWERS_OWNER.md`, `QUESTIONS_OWNER.md` and `NOTES.md` in
`design/RimMandrake/designer_codex_2026-11-09/NightsideIce/`; *judgment* =
`infrastructure/state/delegated/2026-11-03/NIGHTSIDE_ICE_NEW_LIFE_1.json`; *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *titan calls* =
`design/RimMandrake/titan_passage_dark_side_calls_2026-11-05.md`; *experiences* =
`design/RimMandrake/biome_experiences_2026-10-20.md`; *wreck defs* =
`src/RimMandrake/SleepingIce/Defs/ThingDefs_Buildings/RM_NightsideWrecks.xml`. Added by the second reader:
*shield rulings* = `design/Jawa/proposals/ship_shields_deep_design.md` and `src/RimUtinni/ShipShields/`;
*ship gifts* = `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md` and
`src/RimMandrake/SleepingIce/Defs/TerrainDefs/RM_TelluroxHexplate.xml`; *watcher pitch* =
`design/RimMandrake/watcher_creatures_pitch.md`; *droid item* = `infrastructure/state/items/closed/FDE_NIGHTSIDE_VERIFY_1.md`;
*world rules* = `design/Jawa/reconciled_lore/02_world.md`; *cleanse review* = `design/concepts/SleepingIce/cleanse/review.json`;
*record* = `design/RimMandrake/designer_codex_2026-11-09/NightsideIce/record.json`; *build items* = the nine organism items
and the closed sitting items under `infrastructure/state/items/`; *wreck design* =
`design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md`; *name candidates* =
`design/Jawa/worldbuilding/biome_name_candidates_2026-09-26.md`; *fluff digest* = `design/RimMandrake/fluff_cuts_2026-10-23.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Dirty white ice on the highest ground of the night, under the aurora, with something moving inside it" | sheet header | kept, quoted | | |
| The drain of the atmosphere; the antistellar point as a distillation column the size of a hemisphere | sheet header, §2, §3 | lost | World physics; a crew at one stop sees ice, not the column. | One paragraph in a world document; free. |
| Measured tiles, regions, bearing sectors, temperatures | sheet §0 | lost, except "far below freezing all year" | A tile count is never evidence; the planet is painted at the end. | |
| Own def, not a patch of vanilla's ice sheet; no arctic zoo | sheet §0; roster json | kept as a build fact (done) | | |
| "The only animals here are migrating to somewhere else — or badly lost" | sheet §0 | kept, quoted | | |
| Ice as hard as quartzite; rings when struck; fractures in slabs | sheet §1 | kept, quoted | | |
| White, not blue: young, impure, geologically active ice | sheet §1, §6 | kept | | |
| No wind at its heart, no snow, no weather | sheet §1, §3, §6; walk | kept | | |
| The basins below belong to other sheets; "you are the only source of ignition on the hemisphere" | sheet §1 | lost from this design (it is the propane country's line) | | |
| "The hills have metabolisms"; the boulder saving for two hundred years to move once | sheet §1 | kept (the hessarund, the sohl) | | |
| Why it is not a ring and cannot be moved | sheet §2 | lost | World layout; no worldgen. | |
| No vents, no geothermal, no volcanism | sheet §2, §6 | kept | | |
| The six reconciliations (wind source, aurora, glow ban, chemistry partition, no falling weather, the occupied door) | sheet §3 | kept where a visitor can see it (aurora, stillness, no glow); the rest lost as cross-sheet bookkeeping | | |
| The ice sheet is the source of the katabatic wind that strips the Blue Desert | sheet §3 | lost | A fact about another biome. | |
| Crevassing: frost-sift, rime-fall at a lip, the grumble | sheet §3 | kept in "later" as active crevasses; the grumble kept as the shivven's tell | Static fracture lines are scenery now. | Collapse hazard in 0.2.0: joins the thaw; cost M. |
| Things burst out of flowing ice | sheet §3 | moved (cleanse next version → 0.2.0, with calving) | | |
| "The thaw pulse is the disaster"; your own base softens the ice | sheet §3 | moved (→ 0.2.0) | It is the ship's footing. | Hold it for later: the hull then wears only by cold in every version. |
| Experience line: "A frozen highway that nobody stays on. You cross it, dig into it, or go under it." | experiences, walk | kept, quoted | His card of 2026-10-20. | |
| "Highway" as open crossing ground, not a paved line | cleanse owner_pages | kept | | |
| "Dig into it": ordinary mining and salvage | cleanse | kept | | |
| "Go under it": hosting a Lantern Deeps entrance with a real round trip | cleanse; mechanics review | kept in 0.1.0 as a dependency | | |
| His answers: crossing leads, settlement is exceptional; reachable warmth wins; rescue is a pocket map with a way home | owner answers | kept, quoted; the first read as the ship | | Hold the colony reading: 0.1.0 is then measured on a refuge nobody in the campaign builds. |
| The rehearsal's proposed root paragraph | rehearsal | kept, reshaped: the same stop-and-leave bargain, told from the ship | | |
| Always true: the sky is bright and cold; no warm light exists but yours | sheet §5, §9 | kept | | |
| "The player's own lamp is the most emotionally loaded object in the biome" | sheet §9 | kept as art direction | | |
| Anything left here is preserved perfectly and indefinitely | sheet §5, §7 | kept; it is why the salvage is mint and the larder keeps | | |
| "Fire is possible and catastrophic below; warmth is catastrophic here" | sheet §5 | kept as the law | | |
| The fourteen hard bans | sheet §6 | kept as rules; none is a promise | | |
| No farming, no soil, ever | sheet §6 | kept | | |
| No ordinary animal silhouettes: "if a player can tell it is a creature before it acts, it is wrong" | sheet §6 | kept as the art test | The shivven's mole-rat look strains it; the life draft already flags that for a sheet. | |
| Dirty ice melted and filtered for water | sheet §7 | kept in "later" | Belongs to the water machinery. | |
| "What the ice gives up": prospecting is waiting for the ice to move, or making it | sheet §7 | moved (→ 0.2.0, calving) | | |
| A hiding place besides; four Free Droid Enclave seats, cold on purpose | sheet §7, §8 | kept in the campaign layer; quoted under "who hates the Empire" | | |
| Cold as a resource: superconduction, refrigeration, heat rejection | sheet §7 | kept, reshaped: free refrigeration is 0.1.0 (stores do not rot); the rest later | | |
| The electrojet tap | sheet §7; bedazzle review | kept in "later" | | |
| "Not food, not water you can drink unfiltered, not fuel, not safety" | sheet §7 | kept, quoted as the fuel answer | | |
| Thermal camouflage: buried and bermed structures, exteriors at ambient | sheet §8 | kept, reshaped: read as the biome's cover from orbit (a cold ship) | His partial-cover ruling asks each biome for its own. | No cover: the signature matters only to the tunnelers. |
| "Stay light, because a warm building softens its own foundation" | sheet §8 | kept, quoted as hull wear (0.2.0) | | |
| Cracking and tap plant on the pan margins | sheet §8 | kept in the campaign layer; cited for where fuel might be bought | | |
| The failed Junker crystal expeditions, preserved as they died | sheet §8; wreck defs | kept (the expedition rig wreck; the dead in 0.2.0) | | |
| "Untouched": the fourth ruin-language | sheet §8 | kept, quoted | It is the Jawa's reason to land. | |
| "A chemistry set the size of a hemisphere, switched off, under the aurora" | sheet §9 | lost from the design; flagged above | | A world document. |
| Palette, light from above, low horizontal silhouettes | sheet §9 | kept as art direction | | |
| The door, occupied (the Rot and the Ammonia Flats) | sheet §10 | lost | Pointers to other sheets. | |
| The admission test: wanted and barred lists | sheet, roster consequences | kept as the roster's rule | | |
| Owed list and cross-flow ledger | sheet, Owed | lost | Build bookkeeping, mostly done or superseded. | |

### The law of heat, and the tunnelers

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Sensing is thermal; "the player is the loudest thing on the hemisphere" | sheet §4 | kept, quoted | | |
| "Your heating is your threat generator. Insulate, run cold, and nothing comes." | sheet §4 | kept, quoted | | |
| No light-warding: "ward with cold, never with lamps" | sheet §4c | kept, quoted | | |
| The heat dial and its alert | life draft §0; mechanics review; cleanse | kept (built), named the thermal signature | | |
| Insulation must actually lower the reading | cleanse owner_pages, definition; rehearsal | kept as a promise with its control scene | The rehearsal found the built dial does not measure insulation. | |
| The cleanse's exterior-transmission formula and weights | cleanse definition | lost from the design | A bar is an experience, never a tuning number; the formula stays in the cleanse folder as a build proposal. | |
| The rumble-tell: a travelling grumble and ice-twitch | sheet §4c.1 | kept | | |
| The standing audio: the warren's tunnels make the still air sing | sheet §4c.1 | kept in "later" | Unbuilt; no source rules it as sound. | |
| The breach loop: a visible attackable crack; first one timed and taught, later ones vague | sheet §4c.4 | kept, quoted | | |
| Heat output escalates breach frequency, continuously | sheet §4c.4 | kept | | |
| The hull rule: never through floor or hull | sheet §4c | kept, quoted | | |
| The ring feeds back: a warren fed at a warm edge grows | sheet §4c | kept, reshaped: surviving shivven wait and do not leave | The cleanse's capacity rule says only a death frees a place. | |
| Shivven: blind, colonial, within the ice | sheet §4, §4c; life draft §1.2 | kept (built) | | |
| The pink, hairless mole-rat look | life draft §1.2 | kept; the art question stays open for a sheet | | |
| One warren per pan margin, clonal | sheet §4; life draft | kept in "later" with the larder | | |
| Reachable warmth beats stronger protected warmth | owner answers | kept, quoted | | |
| A protected heater as a dependable decoy | rehearsal (agent's guess) | lost | He answered the other way. | |
| Fires, warm rooms and downed living bodies as targets | cleanse definition, census | kept in 0.1.0, owner-blind | | Player-owned only: the Empire's camp is then invisible to the ice. |
| Healthy walkers are not hunted | cleanse definition | kept | | |
| Flooring a pending crack seals it visibly | cleanse owner_pages | kept as a promise's control | | |
| Shivven capacity of 24 and reservations | cleanse definition | lost as a number; kept as "they wait and are accounted" | Tuning. | |
| First warning 24 hours, later 8 to 16 | cleanse definition | lost as numbers; kept as "taught, then vague" | Tuning. | |
| Five code defects found by reading | rehearsal | kept where they are (the rehearsal notes and the cleanse tickets) | Not design. | |
| The larder: dragged under, stored, not eaten; cut down to fetch them | sheet §4c.5; bedazzle review | kept in "later" | See above. | 0.2.0: abduction and a pocket rescue inside a stop; cost L. |
| The apex: one ice wyrm, surfacing under sustained heat | sheet §4c.6; life draft §1.5 | kept in "later" | See above. | 0.2.0 with the whole ladder; cost L. |
| The nest is the eruption; the eggs bring the parent | sheet §4c.6 | kept in "later" | | |
| Wyrmlets foreshadow it | sheet §4c.6; life draft §1.4 | moved (→ 0.2.0) | | |
| Frissim, the insects of the inclusions | sheet §4; life draft §1.3; judgment | moved (→ 0.2.0); flightless and not food, as judged | | |
| The insect-fall | sheet §4c.2 | moved (→ 0.2.0) | | |
| Heat-drawn assailant raid and pack | sheet §4c.3 | moved (→ 0.2.0) | | |
| Reuse of the sand-swim kit, keeping the shivven's own voice | bedazzle review §1 | folded into shared machinery | | |
| Reuse of the Chill's aurora surge and the Blue Desert's buried-pawn work | bedazzle review §1 | kept as build notes for later | | |

### Life that does not look alive

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Life here does not grow. It catalyses, and it waits." | sheet §4 | kept, quoted | | |
| A nightside organism is a catalyst living on a seam | sheet §4 | kept as the reason for the hessarund's inspect text | | |
| Sessile, laminar, enormous; "none of them looks alive" | sheet §4 | kept | | |
| The one-move animal | sheet §4 | moved (→ 0.2.0), quoted | | |
| Sohl: mound, lunge, spent body cut for crust and hide-plate | life draft §1.1; judgment | moved (→ 0.2.0) | | |
| Sohl named only "ice mound" until someone skilled has looked | life draft §1.1 | kept with it | | |
| A sohl that commits at a seam leaves an oolm lobe | life draft §1.1, §2.2 | kept in "later" with the oolm | | |
| Reproduction by fragment; populations clonal and local | sheet §4 | kept in "later" (oolm) | | |
| Nothing warm-blooded, nothing fast; "anything warm on the nightside is a visitor, a machine, or dying" | sheet §4 | kept, quoted about the crew | | |
| "The population is mostly corpses and dying lost souls" | sheet §4 second pass | kept (wrecks in 0.1.0; the dead and the lost soul in 0.2.0) | | |
| Hessarund: the ridge organism, only a landform | bedazzle review §3, §8; life draft §1.6 | kept in 0.1.0 | His card. | |
| The ridge that bargains (Vhal); the ridge that creeps toward heat | bedazzle review §5, §7 | lost (not chosen) | | |
| Catalyst crust as a resource | life draft; judgment; cleanse | kept as a building stock; no research promised | | |
| Saallen, the seam crust that blisters | life draft §2.1 | moved (→ 0.2.0) | | |
| Oolm, the clonal lobes; oolm block as insulation | life draft §2.2 | kept in "later" | Mining a colony organism for wall stock is colony work. | 0.2.0 as scenery that hardens: small, but little to see in a week. |
| Neshkoll, the frost that leans toward heat | life draft §2.3 | moved (→ 0.2.0) | | |
| The ice-kept dead | life draft §2.4; judgment | moved (→ 0.2.0) | | |
| Warm the body and the shivven come for it | life draft §2.4 | kept in "later" with the larder | The cleanse: no theft ships before the recovery exists. | |
| Hoarfrost forms: crystal gardens, frost flowers, depth-hoar columns, blade growth | sheet §4c.7; life draft | kept in 0.1.0 as scenery | Art exists. | |
| Chemical frosts ambiguously alive | sheet, roster consequences | kept (the neshkoll) | | |
| Kesshet, the hull crust | bedazzle review §3 | lost (passed); `NEEDS HIM` 2, now with the Keel-Press and his words | | See above. |
| Zhissa: six-eyed, thermal-reading, milk | bedazzle review §3; names doc; cleanse | kept | | |
| Zhissa's shock | cleanse next_version | moved (next version → 0.1.0) | | Leave it off: one less hazard and one less joke. |
| Tellurox as an owned pack beast; shell stuff | cleanse; rehearsal | kept | | |
| Tellurox hexplate floor | cleanse | kept in 0.1.0 (corrected by the second reader: the first read kept the cleanse's "recommend retiring") | It is the biome's gift to the ship, on his instruction of 2026-09-24; see the added rows. | |
| Mahllik (cave lemming), tauntaun, wampa as visitors | bedazzle review §1; roster json; titan calls | kept where the campaign patch puts them | | |
| Six donor residents; the wider eviction list | roster json; names doc | lost (evicted 2026-09-24) | | |
| Summit crab moves to the Weeping Stones | roster json | lost from here (another biome's business) | | |
| No giant can live here; no titan passage | titan calls | kept | | |
| Names and the nightside accent | names doc; life draft | kept | | |
| Art done and art owed for the cast | life draft §0; bedazzle review | kept as a build fact | | |

### Weather, events, rites and the ship

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The equivalence table: what replaces each vanilla ice-sheet incident | sheet §4b | kept, reshaped: each replacement is in a bucket of its own below | | |
| Thaw pulse instead of cold snap | sheet §4b | moved (→ 0.2.0) | | |
| Rime-fall and ablation at the margins | sheet §4b | kept in "later" | Margin geometry; a ship lands on the interior. | |
| Reconnection storm: radiation, surging circuits, the tunnelers stir | sheet §4b | kept in "later" | | 0.2.0: a storm that surges the ship's own circuits; cost M. |
| Calving delivery: chunks, pods, a cocoon, a machine part | sheet §4b | moved (→ 0.2.0) | | |
| The lost soul | sheet §4b | moved (→ 0.2.0) | | |
| The one-move animal commits; Junker expeditions crossing and failing | sheet §4b | sohl moved (→ 0.2.0); crossings later | | |
| The Abyss's Dark drifting over | sheet §4b | kept in "later" | | |
| No psychic drone or mech cluster by default | sheet §4b | kept | | |
| Standing weather: aurora-clear | sheet §4b; walk | kept | | |
| Scorecard of nine marks | bedazzle review §2; scores | lost | A measure of the old programme, not design. Its one live finding (the ship is unclaimed) is kept. | |
| "A landed ship is the hottest thing on the hemisphere, and that is unclaimed" | scores; bedazzle review | kept, quoted: it is this design's centre | | |
| Build order: heat and tunnelers, thaw, sky, sohl, larder, apex, forms, art | bedazzle review §4, §8 | kept, reshaped: sky and larder fall behind sohl and thaw | The lens ranks what a visit can show. | His order: the sky comes before the sohl. |
| The Breath-Choir | bedazzle review §5 | lost (passed) | | |
| The Keel-Press | bedazzle review §5 | lost (passed) | | |
| The Witness Method | bedazzle review §5 | lost (passed) | | |
| Mob'Unloo's Ninth Account (the ledger tablet) | bedazzle review §5 | kept in "later" as the Cold Ledger's tablet | | |
| The Cold Ledger rite | bedazzle review §6, §8; mechanics review | kept in "later" | Ruled-kept; campaign layer; needs calving first. | |
| The Exchange at the Crack | bedazzle review §6 | lost (not taken) | | |
| The Cold Hearth | bedazzle review §6 | lost as a rite; the act survives as running the ship cold | | See above. |
| A burial in the ice for Rekko | bedazzle review §6 | lost (not taken) | | |
| Frozen wreck field: hull section, cylinder, expedition rig | mechanics review; wreck defs; cleanse | kept | | |
| "Whatever was bolted inside is still bolted inside" | wreck defs | kept, quoted | | |
| Acoustic scanner readings: cracks, wrecks, voids | mechanics review; cleanse | kept in 0.1.0 | A ship part, built, and it finds the vague cracks. | |
| Mod Settings: master and per-feature switches | walk; cleanse; mechanics review | kept | | |
| Master off cancels cracks visibly and deletes no animal | cleanse definition | kept as a promise's control | | |
| The walk's must-be-true list | walk | kept; the mechanics review notes it is stale | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (exposed warmth, warned breaches, cold and floors as answers) | cleanse definition, owner_pages | kept as the core of 0.1.0, with the ship as the warm thing | | |
| Forty-colonist refuge and the whole-plateau season model | cleanse definition, owner_pages | moved (first version → later) | Colony scale. | |
| The other offline models (situations, ice-boundary geometry, exterior heat) | cleanse owner_pages | kept | | |
| Tickets and switch-offs | cleanse tickets, next_version | kept as they stand, except where a feature moved | | |
| Eight proposed bars | cleanse bars | kept as history; the twelve promises in the design are the proposal to argue from | | |
| Eight draft questions for him | rehearsal | lost, except the three he answered | | |

### Added by the second reader

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cryo envelope: *"thermal absorptivity. Pulls in heat in both directions and allows the shields to start glowing with red-orange black body radiation, holding severe cold at bay"* (owner, 2026-09-02) | shield rulings | kept, quoted: it is now the design's hull answer | The first read wrote that no hull system exists. This one is built, and he ruled it for this hemisphere. | |
| The ship's exposure tracker and one-letter landing advisory; *"no environment is immediately lethal"* | shield rulings | kept, cited as the frame | His rule for these rewrites: cite the frame, design no new one. | |
| A cold landing is *"expedition-shaped"*: the envelope is *"mandatory"*, with a fuel spike at each start | shield rulings §2b, §3 | kept, quoted | | |
| The tracker's cold line is forty below; the sheet measured a median of −33 °C | shield rulings; sheet §0 | kept as an `UNMEASURED` flag in the hull section | The built cold wear may never fire on most of this biome. | Lower the line or cool the biome: a build call, no bar. |
| A red-orange glowing shield on the one hemisphere with no warm light | shield rulings; sheet §9 | kept as `NEEDS HIM` 3 | Two of his rulings meet here and neither settles it. | |
| *"The ship must be excellently heated to reach the propane that keeps it warm"* (R-H10) | world rules | kept, quoted | | |
| Nightside creatures *"die crossing the terminator"*; nightside biology is *"untransportable, which makes it valuable"* (R-H10) | world rules | kept as an `UNSETTLED` note on carrying zhissa and tellurox away | The design promises tame zhissa as a takeaway. | Rule that both travel: they were refashioned for the night, not born to it. |
| The tellurox hexplate as the biome's gift to the ship: *"the one floor both sterile and beautiful, for a ship's infirmary or galley"* | ship gifts | moved (the cleanse's "recommend retiring" → 0.1.0) | His words of 2026-09-24 ask every biome what it adds to the ship; they outrank the cleanse of 2026-11-17. It is built. | Retire it: the Sleeping Ice is then the only biome that gives the ship nothing. |
| *"How can this biome uniquely add something to the ship?"* and *"the gravship becomes a scrapbook of everywhere it has been"* | ship gifts | kept, quoted | | |
| The hessarn, the ice's watcher: *"a seam-grazer in ice cracks that turns a heat-pit face toward warm bodies and draws down into the crack"*; it never flees | watcher pitch | kept, reshaped: in 0.2.0 as a proposal, with its "did you see that" | He ruled watchers *"All biomes. It's a new fixture."* (2026-10-08); this member was never admitted at a sitting and is not in `src/`. | Leave it out: the plateau has no small life a crew meets on day one. |
| The nightside droids *"generate fuel they sell to the Junkers via long-distance pipes"* (owner, 2026-08-30) | droid item | kept, quoted as where fuel is bought | The first read left "who sells" unsettled; he had said. | |
| The droids *"fled deep into the cold dark"*, *"suffer from very low power"*, *"burn the strange materials around them for dirty power"*, *"so cold that it can freeze their servo's"* | droid item | kept, quoted | | |
| Two of the four seats (Cracking Station, Coldfire) are the fuel refugees, on the propane lakes; Trade Socket and Vent Nine are out here for neutrality | droid item | kept | | |
| Tauntaun: *"margin herds straying in at LOW commonality, radiating heat they cannot afford"*; the wampa *"follows the straying herds in"* (his visitor law, 2026-09-10) | roster json | kept, quoted | | |
| Every nightside visitor owes a thermal-only sensing line in its text | roster json | kept as a build note | | |
| The mahllik's size deliberately breaks the small-animal pyramid; he was shown the cost: *"not a defect, do not lower or remove it"* (2026-09-21) | roster json | kept | | |
| *"Near-empty is correct"*: about nine in ten of the candidate animals evicted, accepted by card 2026-09-09 | roster json | kept as the roster's rule | | |
| A thaw's named triggers: *"a reconnection storm dumping energy, a machine venting, your own base"* | sheet §3 | kept, reshaped: the landing is named as one in the hull section | | |
| *"Inside the dirty ice, unseen, something is tunneling toward the warmth of whatever just lay down to die"* | sheet §1 | kept, quoted | A dropped line worth carrying. | |
| The owner's *"truly huge creatures everywhere"* is *"most defensible right here"*: size is the only way the arithmetic works | sheet §4 | kept (the hessarund; the dhorrumak later) | | |
| The plateau is *"the gap in both ranges"*: too hot for the propane country's beings, too cold for the terminator's | sheet §4 second pass | lost | World ecology; nothing a visit shows. | |
| Frissim are *"harmless individually; a slumping slab full of them is not"* | sheet §4 | kept with the frissim (0.2.0) | | |
| The canon anchors: the ice wyrm, the sapphire ice worm whose tunnels make the wind sing, the wampa that stores prey | sheet §4c | kept as provenance; anything canon routes through the campaign layer | | |
| *"No game has ever tracked a moving underground threat with a live surface tell, and none scales danger continuously off the player's heat output"* | sheet §4c | lost as a claim | The cleanse declined to repeat it as fact; it is a survey's conclusion, not a promise. | |
| The first-pass seam striker, folded into the dhorrumak: *"one set-piece, not two"* | sheet §4c; roster json | kept (later, as the dhorrumak) | | |
| The apex's eggs: *"preserved perfectly, enormously valuable"* | sheet §4c.6 | kept in "later" with the nest | The most Jawa temptation in the biome; it waits for the ladder. | 0.2.0 with the nest alone: the parent then needs building too. |
| What calving gives up, by name: pieces of the terramanufacture's collapsing machine, the war's cocoons, the well-provisioned dead | sheet §3, §7 | moved with calving (→ 0.2.0) | | |
| *"Any warm directional light in a nightside shot is artificial and belongs to someone"* | sheet §9 | kept as art direction | | |
| The name: "the Nightside Ice" with a name owed; candidates *the Ringing Ice*, *the Dirty Ice*; now the Sleeping Ice | sheet; name candidates | kept (the name in use) | | |
| Roads are allowed: *"All of our biomes should allow roads."* (owner, 2026-09-07) | `RM_SleepingIce.xml`; cleanse ambiguities | kept as a build fact | The sheet says "no roads"; his later word wins. | |
| Engine precedents for the breach: a siege-burrow staging object, pit-gate warning tiers, an open-ground placement rule | sheet, Owed; bedazzle review | kept as build notes | | |
| Mechanoid clusters and psychic drones denied; calving is how war debris arrives | sheet §4b; `mechanoid_biome_presence_draft.md` | kept | | |
| The ice-kept dead as *"a party roped together"*, with *"clothes, pack, the look on their face"* | life draft §2.4 | kept, quoted (0.2.0) | A dropped image worth carrying. | |
| *"Cut them out warm and something else will want them too"*; the judge: a cold corpse gives off no heat, the warmth must have a real source | life draft §2.4; judgment | kept in "later" with the larder | | |
| Neshkoll's foil: hoarfrost stands straight up in still air, neshkoll leans; *"nobody, in game or out, can say whether it is alive"* | life draft §2.3 | kept, quoted | | |
| Neshkoll's lean is approximate (four facings) | judgment | kept as a build note | | |
| Wyrmlets bite only if cornered; their bodies give a rare scale-plate | life draft §1.4 | kept with the wyrmlets (0.2.0) | | |
| The dhorrumak does not chase across floors; *"driving it off means cooling the base"* | life draft §1.5 | kept in "later" | | |
| The sohl's triggers include *"a warm pawn lying downed"*; none to two a map, never on a floor | life draft §1.1 | kept with the sohl (0.2.0) | | |
| The sohl's move to a fresh seam needs a trigger of its own | judgment, flags | kept as a build note | | |
| Hessarund's tells: frost that sublimates off it in slow patterns, a seam *"faintly warmer than the ice"*; one a map; *"it does not grow back in your lifetime"* | bedazzle review §3; life draft §1.6 | kept | | |
| Alternate names for the ridge: thessul, olvesh, ossuvel | bedazzle review §3 | lost | The name is ruled. | |
| The six questions the life draft left for a sitting, and their delegated answers | life draft §3; judgment | kept as answered (shipped shivven art stays; frissim flightless, not food; one spent-body graphic; one shared catalyst crust) | | |
| Frissim go dormant again when the ice refreezes; any that die leave remains | judgment, flags | kept with the frissim | The draft killed them silently. | |
| The insect-fall is a dayside swarm, not frissim; only the fall is food | judgment, flags | kept | | |
| Saallen is *"not a revival of the passed hull-crust kesshet"*; scraping lowers a crack's preference only | judgment | kept with the saallen (0.2.0) | | |
| Softened ice is never a melt pool | judgment, flags; cleanse | kept as a rule | No liquid water, ever. | |
| The renders for the four new organisms are gone from disk and were never judged; each build re-queues its art | judgment; build items | kept as a build fact | This page's closing note is corrected below: the briefs survive in the life draft, the pictures do not. | |
| His art notes of 2026-10-05 on the cast sheet: redo zhissa, mahllik and tauntaun; the mahllik rewritten *"small, silky, tasselled"* | `NIGHTSIDEICE_SHEET_ART_REDO_1` | kept as a build fact | | |
| The tellurox's sideways body is his own reported defect, already filed | rehearsal `NOTES.md`; record | kept where it is filed | | |
| The larder's sign: *"a visible drag trail into the crack, a letter naming who"* | bedazzle review §4 | kept in "later" with the larder | | |
| The Cold Hearth was to be found in *"the one shelter on the ice whose people lived"* | bedazzle review §6 | lost with the rite | The image is kept here. | A bermed refuge as a 0.2.0 site with nobody home. |
| The Exchange was to be found where *"a Junker expedition traded its dead for its living"* | bedazzle review §6 | lost with the rite | | |
| The Cold Ledger's details: *"the ice keeps it, in sight, forever"*; the tablet names the next find *"and it calves where it said"* | bedazzle review §6; `salvation_rites_2026-10-01.md` | kept in "later" | | |
| Rites are under review: *"Many of them are somewhat fluff"* (owner, 2026-10-23); the Cold Ledger was left untouched as already second-version | owner ruling on `BIOME_MECHANICS_JUDGE_FLUFF_ON_TRIAL`; fluff digest | kept in "later" | | |
| The Breath-Choir's line: *"Making this dead place sing means announcing yourself to it"* | bedazzle review §5 | lost with the idea (passed) | | |
| The Keel-Press is a ship idea too, passed in the same sentence as the kesshet | bedazzle review §5, §8 | lost (passed); now named with the kesshet in `NEEDS HIM` 2 | The first read asked about one of the two. | |
| The record of his pass: *"passed, not gaps to re-pitch"* | bedazzle review §8 | kept, quoted in `NEEDS HIM` 2 | It is the evidence for the default. | |
| Shrines are prevented on this biome | bedazzle review §1; scores | kept as a build fact | | |
| *"The tell graphic matters more than the body"* | bedazzle review §4; `NIGHTSIDEICE_SHIVVEN_BUILD_1` | kept as art direction | | |
| *"It is the best-designed and least-built of the twelve"*; *"the thermal law hands it a ship touch for free"* | scores | lost as scoring; the second is the design's centre | | |
| The zhissa's shock, as built: consciousness falls and repeated shocks risk a stopped heart | record; cleanse next_version | kept, stated in the design | The first read called it slapstick that costs nothing. | Leave it switched off, as the cleanse proposed. |
| The zhissa's static is *"a visitor's trait, not resident glow"* | bedazzle review §3 | kept | | |
| Shivven give no meat or leather and need no food or rest | record | kept as a build fact | | |
| The rehearsal's three ways the biome could fail: *"the highway has no journey"*, *"warmth is an arbitrary punishment"*, *"the ice breaks its own truth"* | record | kept as the test of this design's first week | | |
| The rehearsal's unasked question: *"What should the party bring away from a successful day's stop that makes you glad they took the risk?"* | rehearsal `QUESTIONS.md` 07 | kept, answered by the design's "What the crew takes away" | | |
| The rehearsal's unasked question on the first countdown: recall the exposed and make *"one deliberate response"* | rehearsal `QUESTIONS.md` 04 | kept as the first crack's intent | | |
| The proof script tolerates a little prefab water, against the sheet's ban | rehearsal `NOTES.md`; cleanse ambiguities | kept as a defect for the build | | |
| *"The next warning is a knock without an arrow"* | cleanse definition | kept, quoted | | |
| *"The pale grazer is not a promise of pasture"* | cleanse definition | kept, quoted | | |
| A departure leaves *"still ice, worked sites and whatever ordinary living animals or corpses remain, not a reset world or an ever-growing hidden army"* | cleanse definition | kept as the rule behind "nothing vanishes" | | |
| Hydroponics and carried supplies are not banned | cleanse owner_pages, ambiguities | kept, stated in the first day | A ship carries its own garden. | |
| A crack with no legal cell at its deadline resolves as blocked, says so, and releases nothing | cleanse definition | kept as a promise's control | | |
| Ground changed under a waiting shivven surfaces it in view; it is never moved | cleanse definition | kept as part of "nothing vanishes" | A ship that re-lands is the case. | |
| The thermal signature is *"a sensor of exposure, not a second temperature, damage type or sun"* | cleanse definition | kept | One sun, from geometry. | |
| The first crack is not a staged arrival event; a cold camp may never see one | cleanse definition | kept | | |
| Shivven never leave, breed or despawn | cleanse definition | kept | | |
| One wide floored apron could end cracks for good, against his *"ongoing costs"* | cleanse review | kept as an `UNSETTLED` note on the apron | The design leans on the apron. | |
| Whether hunting the dying visitors can feed a camp | cleanse review | kept, reshaped: the design says the only meat is what else is lost here | | |
| Wrecks here are the densest class on the planet, *"riddled"*; frozen weathering adds no corrosion; shared with the Lantern Deeps | wreck design; wreck defs | kept | | |
| *"Their tools went with them or under the ice"* | wreck defs | kept, quoted | | |
| The wrecks *"dress the highway"*: *"dead travellers' leftovers"* | mechanics review | kept | | |
| Blue ice blocks cut on the night side can go in the melter (owner, 2026-10-25) | owner ruling on `ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN` | kept in "later" with dirty ice melted and filtered | Blue ice is the Blue Desert's; dirty ice is this biome's. | |
| The scanner's readings were ruled for every biome by card on 2026-10-06 | mechanics review; cleanse definition | kept | | |

## Sources read, and the count

*(The first read's own account follows. The second reader's reading and recount are at the top of this page.)*

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**21 source files, 142 rows**, of which **25 lost**, **18 record a move** (whole or in part), **6 kept, reshaped** and 1 folded into shared machinery. Every source named above is in at least one row's source column (checked by the same script).

Read whole: the sheet; the life draft; the bedazzle review; the cleanse's owner pages and next-version list; the
walk; the owner answers and the questions he was shown; the experiences table. Read in large part: the cleanse
definition (every paragraph, each cut at about 900 characters). Read by heading or by search: the scores doc (the
Nightside Ice section's first rows); the roster json (its first third: the confidence notes and eviction list); the
names doc (Nightside rows); the rehearsal `NOTES.md` (each paragraph's opening); the judgment (the brief and the
first three verdicts); the mechanics review (the Nightside Ice table, each row cut short); the titan calls; the
cleanse census (every row's name and built state), ambiguities and tickets (searched for the ship, the hull and the
hexplate); the wreck defs (labels and descriptions). Not read: the rehearsal's `QUESTIONS.md`, `record.json` and
`designer_brief.md`; the cleanse's `bars.json`, `models.md`, `review.json`, `converge.json` and the body of
`tickets.md`; the judgment's verdicts on the last seven organisms and its factual flags; the roster json's later
sections; `design/Jawa/salvation_rites_2026-10-01.md` (the Cold Ledger's register entry).

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `sleeping_ice.md`, `nightside_ice_roster_draft_2026-10-05.md`,
`nightsideice_bedazzle_review_2026-10-01.md`, `rosters/sleeping_ice.json`.

Not for deletion: the two shared names docs and the grandfathered scores doc (they cover other biomes);
`design/concepts/SleepingIce/cleanse/` (superseded by this design, never applied; it should be re-run from this
file, not applied); the validation walk (stale, by the mechanics review's own note, and owed a rewrite);
`design/RimMandrake/designer_codex_2026-11-09/NightsideIce/` (it holds his three answers).

Before deleting: `sleeping_ice.md` is frozen by `BIOME_FREEZE_FABLE_REVIEW_1` (*"amendments add detail; they never
change a ruling"*) and is the authority the life draft, the judgment and the build items for the nine organisms cite
by section number. Those items should be pointed at this design first. The life draft's art briefs for saallen,
oolm, neshkoll and the ice-kept dead are the art pipeline's only briefs for them and should move to the art ledger
or stay until that art is ruled. (Second reader: the briefs are also the only trace of that art. The renders made
from them on 2026-10-05 are gone from disk and were never judged, by the closed item `NIGHTSIDE_ICE_NEW_LIFE_1`.)
