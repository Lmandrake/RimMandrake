# The Blue Desert: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A second agent, which did not write the design or this page, read the sources again, starting with the ones the
first read named as read in part or not at all. Item: `RIMMANDRAKE_RECHECK_BLUEDESERT_TO_SLIME_CHOICES`.

**Rows added: 112**, in the table "Found by the second reader" below the first read's rows.

**The three most valuable things the first read missed**

1. **The hull wear is already built, twice.** The first read wrote the hull section without the shield frame. The
   frame in `src/RimUtinni/ShipShields/` counts outdoor cold of forty below as a hazard to an unshielded ship (the
   Blue Desert's median is −42.6 °C) and counts any weather that carries sand (the ice-sand drift rides that same
   field). His own words give the answer to the first, the cryo envelope, and it glows *"red-orange"*, on the one
   biome whose cover is darkness. That last point is a new question for him.
2. **The Horrors raid the night side whether or not anyone mines.** `assailant_weapon_remnants.md` was not opened
   by the first read. It holds the ruling (*"Players who land on the night side encounter them: the weapon on
   patrol comes out of the cold"*), his own sentence about them, and the line about the BroodLord still collecting
   *"samples for a master who no longer exists."* The design had the Horrors only as something a quarry might
   release.
3. **The life brief, read by headings only the first time, holds most of the crew's-eye writing.** The salvager
   names (cask, torch, linewalker); *"The crews call them linewalkers and follow them to the good salvage"*; the
   pet that eats the field, *"dies of it and takes the barn with it"*; a native brought indoors, where *"the room
   does the rest"*; and *"a crew that clears a firebreak with knives is doing the right thing."* The cast bible
   adds that a wounded vhaulk always turns on its attacker, which changes the "right way" scene from patient work
   to a fight.

Also recovered, and worth his eye: his own words of 2026-11-10, *"We likely need to revisit this biome and do a
full redesign pass"*, which the first read did not quote. They are now in the design's status header.

**What I changed in the design, and why**

- *What the place does to the ship* is rewritten to cite the shield frame and his shield rulings, as the rule for
  these rewrites requires. Every wear in it comes from a source; none is this page's proposal. The drift against
  the hull is stated as a walking cost that cannot trap the ship, because that is what the engine does.
- *Who else attacks* now states the Horrors as the night side's raiders (campaign layer), with the quarry link
  still 0.2.0.
- *"OMG did you see that?"*: the vhaulk kill is a fight with an enraged giant; the sick pet can go off; krissek come
  in packs; two scenes added ("Tea", flagged as a reading of built behaviour, and "The live one", from the brief).
- *The first day* and *first week* took the firebreak line, the fuse line, the wax's overheating gauge, melting ice
  over a fire, mining wrecks free, following the linewalkers, the crew's slang and the ossivel line.
- *The clock* now gives the open-ground figures for a stop whose dark pause is lost, taken from the Greentide
  design and not re-derived.
- *Scope*: the kuvvel and the dovvik-as-defuser join 0.2.0; the rites cite his ruling of 2026-10-23; the boomalope
  joins the dropped list.
- *NEEDS HIM* grew from three to six: full dark or one step (cover); the cryo envelope's glow (hull); the deck part
  now the rack is gone (other). Question 3 now says that taking the vapaad off this biome would undo his own
  placement.
- Checked and left alone: whose word wins. No cleanse line was found that keeps something he had rejected before
  2026-11-17; the cleanse already follows his answers of 2026-11-10 and his cuts of 2026-10-23. There is no locked
  Designer sheet or tree for this biome. No ship idea of his was found declined; the rack and its drip were
  already on the dropped list.

**What I read, and what I did not**

Read whole by the second reader (the script counts this list and checks each path exists):

<!-- second-reader-read-whole -->
`design/concepts/BlueDesert/design.md` · `design/concepts/BlueDesert/rewrite_choices.md` ·
`design/concepts/BlueDesert/cleanse/owner_pages.md` · `design/concepts/BlueDesert/cleanse/next_version.md` ·
`design/concepts/BlueDesert/cleanse/ambiguities.md` · `design/concepts/BlueDesert/cleanse/definition.md` ·
`design/concepts/BlueDesert/cleanse/tickets.md` · `design/concepts/BlueDesert/cleanse/run.json` ·
`design/concepts/BlueDesert/cleanse/result.json` · `design/Jawa/worldbuilding/biomes/the_blue_desert.md` ·
`design/Jawa/worldbuilding/creatures/blue_desert_hydrocarbon_life.md` ·
`design/Jawa/worldbuilding/biomes/bluedesert_bedazzle_cast_2026-09-28.md` ·
`design/Jawa/worldbuilding/biomes/bluedesert_bedazzle_review_2026-09-28.md` ·
`design/Jawa/worldbuilding/biomes/bluedesert_flora_expansion_pitch_2026-10-02.md` ·
`design/Jawa/worldbuilding/biomes/bluedesert_carbon_garden_2026-09-30.md` ·
`design/Jawa/worldbuilding/biomes/rosters/the_blue_desert.json` ·
`design/Jawa/worldbuilding/biomes/assailant_weapon_remnants.md` ·
`design/validation_walks/RimMandrake/BlueDesert.md` ·
`design/RimMandrake/designer_codex_2026-11-09/BlueDesert/ANSWERS_OWNER.md` ·
`design/RimMandrake/designer_codex_2026-11-09/BlueDesert/QUESTIONS_OWNER.md` ·
`design/RimMandrake/designer_codex_2026-11-09/BlueDesert/designer_brief.md` ·
`design/RimMandrake/designer_codex_2026-11-09/BlueDesert/NOTES.md` ·
`infrastructure/state/items/BLUEDESERT_MECHANICS_BUILD_1.md` ·
`infrastructure/state/items/closed/BLUEDESERT_DESIGN_SITTING_1.md` ·
`infrastructure/state/items/closed/BLUEDESERT_RULED_CONTENT_1.md` ·
`infrastructure/state/items/closed/BLUEDESERT_FLORA_EXPANSION_BUILD_1.md` ·
`infrastructure/state/items/closed/BLUEDESERT_GPT_ENRICHMENT_1.md` ·
`infrastructure/state/items/closed/NIGHTSIDE_BLUE_DESERT_1.md` ·
`infrastructure/state/items/closed/BLUE_PROPANE_RING_RULING_1.md` ·
`infrastructure/state/items/closed/BLUEDESERT_ORPHAN_LOAD_CRASH_1.md` ·
`infrastructure/state/items/closed/RIMMANDRAKE_REWRITE_BLUEDESERT_TO_SLIME_UTINNI_LENS.md`
<!-- /second-reader-read-whole -->

Read in part (the part is named): the cleanse's `census.json` (every row's description, fate and built state; not
each row's argument); `bars.json` (the ten checks and eleven rules; not the eight bars' bodies); `fixes.json` (the
first two); `models.md` (headings); the rehearsal's `QUESTIONS.md` (the root, questions 1 to 4, and the picture and
question of 5 to 9); the mechanics review (its header and the whole Blue Desert table, uncut); fluff cuts (the Blue
Desert section); the experiences table (this row); the rites pass (§3 whole); the hydrocarbon commission (§6 and
§14g); the beast-names page (the Blue Desert batch); `ship_shields_deep_design.md` (the rulings table and the cryo
section); the shield source (the hazard checks, by search); `BIOME_SHIP_CONTRIBUTIONS_1` (this biome's row);
`BLUE_DESERT_FIRST_SCRIPT_1` (its spec); the watcher pitch and the salvage design (this biome's rows).

Not read: the rehearsal's `record.json` (334 KB of inventory); the cleanse's `review.json` and `converge.json`;
`BLUEDESERT_RM_MOD_BUILD_1` and `BLUE_DESERT_LIFE_AUTHORING_1` (build records; searched for his words only); and
about 185 other files under `design/` that mention the Blue Desert, which were searched for lines about the ship,
fuel, cover, the Empire and cuts, not read. None of these is on the deletion list.

**Measured counts** (script, after writing; the check with its probe is recorded in
`design/RimMandrake/biome_recheck_bluedesert_to_slime_row_check_2026-11-18.txt`): **250 rows** (138 from the first read, 112 added), of which **34 lost**, **15 record a move**, 8 kept and reshaped, 2 folded into shared machinery and 191 kept; all 16 named sources have a row; **31 source files read whole** by the second reader.

**DELETE-READY: yes**, for the seven files named at the end of this page (the six in the deletion list and
`blue_desert_hydrocarbon_life.md`, which the first read held back and which has now been read whole against the
design). The first read's three conditions still stand before anything is deleted: move the art briefs to the art
ledger; fix the two files that cite `the_blue_desert.md` by path; and, added by this read, move the life brief's
§1 engine facts (why plants here must ignore fertility, why the vanilla explosive comp cannot sit on a plant or a
pawn, why "hard to ignite" is authored) into the mod's own notes, because the brief is the only place they are
written.


Companion to `design/concepts/BlueDesert/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the
overriding priority"*. The cleanse proposal of 2026-11-17 had already done the hard cut here: it took his November
answers (*"it's just ice"*; loose ice cools the room; prepare containment) and reduced the biome to cold-stable fuel
that punishes heat. This design keeps that cut almost whole and changes who is making the heat: a warm ship full of
desert people with ion guns, not a forty-colonist cold-storage operation. Four things he ruled on today's card are
stated per biome: the stop's outer edge, cover from orbit, fuel, and what the place does to the hull.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The choir.** *"When the singing stops all at once, you have until the echo dies to be somewhere else."* The
   ossivel's silence alarm and the virr reed whose *"pitch rises as the plant's charge ripens"* were cut by him on
   2026-10-23 as *"pure audio at 361 lines"*. Under the lens, a hush before the big thing arrives is exactly an
   "OMG" beat, and the Fever Wood and the Greentide feature the same cue from shared code. I left it dropped
   because the cut is his and recent. If one cut is worth reopening, it is this one, and it could ride the shared
   silence cue instead of its own 361 lines.
2. **Reading the warnings.** *"Nobody who can read the warnings mines; everybody who mines learns what they
   said."* Five epochs of failed quarries under a script nobody can read, ending in the player as epoch five. It is
   the half of his experience line that says *"ancient secrets from the depths of time"*, and 0.1.0 keeps only the
   physical site. A study ladder is colony work, so it is "later". The ship gives it a shorter road nobody has
   written: the hull is Rakatan and so is the script.
3. **The ice hands up the weapon.** The sheet calls the Blue Desert *"the Horrors' host"*, and *"Mining is
   warming"* was its original loop. The cleanse put the link to the Night Horrors in "next version"; I put it at
   0.2.0 because "who else here attacks" is one of his lens questions and the siege forms are *"hardened for...
   vehicle attack"*. It depends on another mod and may not belong that early.
4. **The Returned.** A freeze-dried body the ice gave back, sealed in a sarcophagus aboard *"so that it leaves with
   the clan on the next launch"*; inscription *"I went higher than any of us. The ice brought me back. Take me with
   you when you go."* Ruled kept by card on 2026-10-01, and the only rite in any biome written around the ship
   leaving. It is "later" because rites live in their own mod, not because it does not fit.
5. **Tapping the living vhaulk**, *"the mad-brave harvest"*. Unbuilt. Six Jawa siphoning fuel from a walking bomb
   is the lens and the "very Jawa" test in one image; I moved it to 0.2.0 from the cleanse's next version and would
   not argue with 0.1.0 if it were built.
6. **The cold rack.** Built, 243 lines, with a tint and a groan that tell the player how much cold is left. His
   November write-in replaced it (*"no rack needed"*). Dropped as the cleanse recommended. What is lost with it is
   the readable gauge; loose ice will need its own sign of how long it will last.
7. **The murrek in the drift.** *"The crews walk the swept ice after a storm and probe the leaning sand with poles,
   and the poles are not long enough."* Built, 507 lines, never proven live. The cleanse deferred it; I moved it to
   0.2.0, since a drift against the ship's own hull that turns out to be an animal is a close-range moment.
8. **Uzhmek, the tar-snarl** (slow ground where pawns walk most, so *"a pawn stuck in a mat is a pawn standing in
   a blast radius"*). Pitched 2026-10-02, never built, never ruled, and not in the cleanse at all. Lost from this
   design; it is the one pitched plant with no row in the mod.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **Murrek burial, flushing and storm re-arming:** next version → 0.2.0. A creature moment a crew meets in a week,
  at its own hull.
- **The ablation line giving something up (incident and payloads):** next version → 0.2.0. Salvage surfacing while
  the crew watches is what a Jawa came for.
- **The quarry that releases a siege form:** next version → 0.2.0. "Who else here attacks." Depends on the Night
  Horrors.
- **A passing giant exposing buried ground:** next version → 0.2.0. His answer of 2026-11-10, and a reason to run
  after something enormous.
- **Tame dovvik minesweeping:** next version → 0.2.0. Approved by him 2026-09-28.
- **Living vhaulk valve tap:** next version → 0.2.0.
- **Hazebell bloom; char-lace:** next version → 0.2.0. Both built; both show inside a stop.
- **Acoustic sounder readings here:** recommended for retiring → 0.2.0. It is a ship part; the pilot kept the same
  feature at 0.2.0 for the Greentide.
- **Drift against the grounded ship, dug out by hand:** the cleanse kept ordinary drift and deferred a
  ship-specific burial; today's ruling puts what the biome does to the hull in 0.1.0. The promise is the ordinary
  drift, proven deep, beside the hull. What an undug hull costs at launch is left to the shared rules.
- **Oskelloth, the salvage-sign crust:** not in the cleanse → 0.2.0. *"A Jawa signpost plant."* Unbuilt.
- **Stayed "later" from the cleanse's "next version":** the study ladder and epochs, rites, the Haze illness, the
  fog's shuttle veto, the thunderbeast's toolkit, roe as human food. Not moves.
- **Dropped as the cleanse recommended:** the cold rack and its readability, the cold-cutting technique, the
  block-counter loot, the krissek's duplicate blast, milelace reseeding. The last three still wait for his word.
- **New, not in any source:** the crew as the heat source (ramp air, heaters, ion guns, hauling corpses aboard);
  the Empire's own weapons and stoves setting off the field; the Empire's ion cordon and the vhaulk; a blast ending
  the dark pause (asked as `NEEDS HIM`); the Rakatan ship reading Rakatan warnings (parked in "later"). The first
  three are readings of built or ruled behaviour.

## Every idea, row by row

Source names: *sheet* = `biomes/the_blue_desert.md`; *life brief* = `creatures/blue_desert_hydrocarbon_life.md`;
*cast bible* = `biomes/bluedesert_bedazzle_cast_2026-09-28.md`; *bedazzle review* =
`biomes/bluedesert_bedazzle_review_2026-09-28.md`; *carbon garden* = `biomes/bluedesert_carbon_garden_2026-09-30.md`;
*flora pitch* = `biomes/bluedesert_flora_expansion_pitch_2026-10-02.md`; *roster json* =
`biomes/rosters/the_blue_desert.json` (all under `design/Jawa/worldbuilding/`); *cleanse* =
`design/concepts/BlueDesert/cleanse/`; *walk* = `design/validation_walks/RimMandrake/BlueDesert.md`; *owner answers*
= `design/RimMandrake/designer_codex_2026-11-09/BlueDesert/ANSWERS_OWNER.md` and its `QUESTIONS_OWNER.md`;
*mechanics review* = `design/RimMandrake/special_mechanics_review_2026-10-22.md`; *rites pass* =
`design/Jawa/biome_rites_pass_2026-10-01.md` §3; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*experiences* = `design/RimMandrake/biome_experiences_2026-10-20.md`; *pursuit* = the escalation ladder and
`reconciled_lore/01_campaign.md`; *clan lore* = `reconciled_lore/05_the_clan.md` and `07_physics_and_arms.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Experience line: "An alien expanse of beautiful blue locking ancient secrets... risk your own passion's heat turning everything into a bomb" | experiences, walk, mechanics review | kept, quoted | His words. | |
| "From orbit it is the bluest thing on the planet; underfoot it is colorless" | sheet §1, §9 | kept, quoted | What the ship sees on approach. | |
| The phase boundary as the thematic handle; the median temperature is propane's condensation point | sheet header, §3 | lost from this design | Chemistry lore a crew never sees; the rule the player meets is "warm it and it goes". | One sentence of flavour text on the biome card; free. |
| "The ablation line gives something up... and the beauty has a price tag on it" | sheet §1 | kept, quoted | | |
| Deep nightside, eternal dark, −42.6 °C, zero water | sheet §0, §2 | kept as the kind of place | It decides cover from orbit. | |
| Measured tiles, regions, the nightside temperature ladder | sheet §0 | lost | A tile count is never evidence; the planet is painted at the end. | |
| The ring, the lobe mosaic, the sector table, the clean-circle amendment, "no bullseye" ban | sheet §0, ban 4 | lost | World painting, done once at the end; not a biome design matter. | Keep in the paint list; free. |
| No second highland biome (Bluefire not used) | sheet ban 5 | lost | Same. | |
| Donor inventory (density, movement, disease clock, weather table) | sheet §0 | kept as build facts, not design | | |
| The Earth desert zoo and grimpepper evicted | sheet §0, roster json | kept (dropped list) | | |
| Nothing is blue up close; the colour is scattering | sheet §5, §1 | kept | | |
| The ground is ancient water ice; the sand is ice; the snow is sand | sheet §5 | kept, quoted in part | | |
| "Hydrocarbon ice": the ground does not explode, the life does | cleanse ambiguities 1 | kept | His "it's just ice". | |
| Hydrocarbon biology: no water life; transparent fractal plants; plants stay small | sheet §3 | kept, quoted | | |
| "It is not a fire, it is an explosive chain reaction" | sheet §3 | kept, quoted | The signature. | |
| Every native organic is a fuel charge stable only in the cold | sheet §5 | kept | | |
| The quarries have been tried before, and it is all still here | sheet §5, §8 | kept as a physical site | | |
| No cultivation of the native flora | sheet ban 2 | kept (dropped list) | | |
| No warm-safe hydrocarbon organics; "you never bring one indoors" | sheet ban 3 | kept, quoted | It is the joke: Jawa bring everything indoors. | |
| No Horrors settlement; the ground stays clean of horror | sheet header, ban 6 | kept | | |
| No rain | sheet ban 7 | kept | | |
| Recognizability rule; icon carve-out for mynock and neebray | sheet ban 8, roster json | kept as an art and roster constraint | | |
| Art theme: starlit clear, halos the only warm light, fractal silhouettes | sheet §9 | kept, quoted in part | | |
| Sound line: "wind over ice; the hiss of drift; the crack of a thaw; then the boom" | sheet §9 | kept, reshaped: the crack survives as a warning cue; the ambient set is cut | His cut of 2026-10-23. | |
| Ice fog as cover; "the sensor-shadow theme's second home" | sheet §4b, §7 | kept, reshaped: ground-level cover against a probe; cover from orbit is the dark | Today's ruling asks each biome to state its cover. | Count fog as a second step of cover: the Blue Desert becomes better hidden than the Abyss. |
| Careful means prepare containment and secure escape | owner answers 1 | kept, quoted | | |
| Root proposal: choosing how far to pursue a discovery that pursuit can destroy | owner answers (questions page) | kept as the feeling of the old workings | An agent's proposal, not his words. | |
| Forty-colonist cold-storage operation; whole-season ecology | cleanse definition | lost from 0.1.0 | Colony scale; a season of predation and regrowth is not seen in a stop. | Keep as "later"; it is listed there. |
| The cleanse's signature (cold preserves fuel; warming spreads a blast into cargo) | cleanse owner pages, definition | kept as the core of 0.1.0 | | |
| The cleanse's five offline models | cleanse owner pages | kept | Build instruments; the containment and thermal ones matter most to a ship. | |
| The cleanse's eight bars and thirty-one tickets | cleanse | kept as history; the promises table in the design is the proposal to argue from | | |
| Draft north star; anti-guessing notes | walk | kept | | |
| Jawa as heat-adapted, dark-sighted, ion-armed | clan lore | kept, used as the crew's relation to the place | New framing; the facts are sourced. | |
| The dark pauses the orbital clock | pursuit; card of 2026-11-18 | kept; stated as owed work | Only the Abyss is on the built list. | |

### Weather, ice and the old workings

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Usually clear; less shelter than the crags | sheet §3, §4b | kept, quoted | | |
| Ice-sand drift on Odyssey's sand grid; "we need to do testing to make sure it goes deep" | sheet §4b amendment | kept, quoted | Now also what the place does to the hull. | |
| Blue-white tint patch for drift | sheet §4b | kept as build detail | | |
| Deep drift means thick buildup beside walls, doors and hulls | cleanse owner pages, ambiguities 22 | kept | | |
| Ice fog: accuracy halved, range capped, movement slowed | sheet §4b amendment | kept; the numbers are tuning, not promises | A bar is an experience. | |
| Ice fog forbids shuttle launch | cleanse next version | kept in "later" | A veto on leaving is close to a trap, and the ladder says never trap. | 0.1.0: fog becomes a reason to launch before it closes in; needs a warning. |
| The Haze as hydrocarbon precipitation | sheet §3, §4b | kept as a veil | | |
| The Haze's exposure film on unroofed pawns | sheet §4b amendment, mechanics review | kept in "later" | A second meter; the cleanse deferred it. | 0.2.0: a reason to stay under the hull. |
| Blue ice: mineable, distilled purity, "golden" | sheet §7 | kept, quoted | | |
| Blue ice as the one true blue up close; its look | cast bible §5 | kept as art direction | | |
| Mined like an ordinary mineral | owner answers | kept, quoted | | |
| The thaw roll every third block (push your luck) | bedazzle review slate B, mechanics review | lost (recommended for dropping; his to confirm) | His answer removes the premise; pace changes nothing. | Keep as an optional setting; costs a false lesson about care. |
| Quarry → warmth → thaw → siege form; "Mining is warming" | sheet §3, §7 | moved (next version → 0.2.0) | See "the ones I would look at". | Later: the biome has no outside attacker in either early version. |
| The cold-cutting technique | bedazzle review slate A | lost | His answer: "it's just ice". | |
| The Warnings study ladder; hazard sense; the full reading | bedazzle review slate A, sheet amendment 6 | kept in "later" | Study is colony work. | 0.2.0 with the ship's mind as the reader: new design. |
| Five epochs: Rakata, the war era, Czerka, the Empire, the player | sheet §8 amendment | kept in "later"; the Empire's cut is quoted | | |
| "Nobody who can read the warnings mines; everybody who mines learns what they said" | sheet §8 | kept in "later", quoted above | | |
| "Do not still the mountain" among the warnings | sheet amendment 4, cast bible | kept, quoted | It is the ion joke. | |
| A physical abandoned extraction face with ice and salvage, no study needed | cleanse definition, ambiguities 25 | kept | | |
| The fallen: meteoritic metal, wreckage, freeze-dried dead; the Empire as unwitting supplier | sheet §7 | kept, quoted | Salvage is why a Jawa is here. | |
| Static ice-locked wreck field | cleanse census, shared machinery draft | kept | | |
| Ablation-line salvage incident: crack, shape under the ice, payload, letter | bedazzle review slate J, mechanics review | moved (next version → 0.2.0) | | |
| Scavengers converging on a surfacing as the tell | bedazzle review slate J | moved with it | | |
| Drift-buried ruins, eroded windward, entombed on the lee | sheet §8 | kept, reshaped: part of the static workings | Not found as its own built thing. | |
| Fall debris fields | sheet §8 | kept (the wreck field) | | |
| The weapon layer: crysalises, sinkholes, nests | sheet §8 | kept in the campaign layer (Night Horrors) | | |
| A passing giant exposes buried ground; "risk following it" | owner answers 3 | moved (next version → 0.2.0) | | |
| The vhaulk's pressed rime road | mechanics review, fluff cuts | lost (cut 2026-10-23) | | |
| Acoustic sounder readings for this biome | cleanse next version | moved (retire → 0.2.0) | | Retire as the cleanse said. |

### Plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The charge on every plant: cutting and grazing safe, a damage kill chains | life brief §2, bedazzle review mark 1 | kept | | |
| Warm air above the threshold sets plants off after a short countdown | life brief, walk | kept as a warning then a crack | | |
| The crack cue before a chain propagates, "a beat to run" | bedazzle review slate E | kept, reshaped: a locatable warning state, with sound as reinforcement | The cleanse: audio alone fails offscreen cargo. | |
| A warning that survives a reload | cleanse ambiguities 9 | kept | | |
| Cooling before the crack stops it; after, nothing does | cleanse ambiguities 8 | kept | | |
| The chain number (one blast kills the next plant) | life brief §2d | kept as tuning, not a promise | | |
| Palefloss, glassfern, chimeglobe; names reaffirmed | sheet §4 amendment, life brief §6 | kept | | |
| Virr, the whistle-reed, as a plant | cast bible §4 | kept | | |
| Virr's pitch rising with its charge | cast bible §4 | lost (cut with the soundscape) | | See "the ones I would look at". |
| Milelace, the creeping mat | carbon garden | kept | | |
| Milelace reseeding into fresh drifts | carbon garden §2 | lost (never built; recommended for dropping) | | |
| Frost-fibre from milelace | carbon garden | lost (would be a warm-safe organic) | Decided 2026-11-03. | |
| Hazebell (renamed from Ninefold Censer) | carbon garden | kept | | |
| Hazebell opening after the Haze and breathing vapour | carbon garden | moved (next version → 0.2.0) | Built; a visible change within days. | |
| Longglass, leaning with the wind in its art | carbon garden | kept | | |
| Qeshra, the scarlet bead cushion; native feed that draws herds, and herds draw the krissek | flora pitch 1 | kept | "The one red thing on the plateau." | |
| Qeshra roe preserved as human food | cleanse next version | kept in "later" | It would give the crew food here and remove the larder as the stop's limit. | 0.2.0: the Blue Desert becomes livable; a large change to its clock. |
| Uzhmek, the tar-snarl | flora pitch 2 | lost | Never built or ruled. | Build at 0.2.0: slow ground in a blast radius is a real moment; new plant and art. |
| Rimetangle | cleanse census, source | kept | Built; no design text found beyond its def. | |
| Kethevar, the golden coil | flora pitch 3 | kept | | |
| Char-lace from a burned kethevar, the one warm-safe product | flora pitch 3 | moved (next version → 0.2.0) | "Rewards setting fires deliberately": a very Jawa bad idea. | |
| Lisqueth, the violet rosette, the nightside's one natural lamp | flora pitch 4 | kept | | |
| Oskelloth, the oil-sheen crust beside the fallen | flora pitch 5 | moved (unbuilt → 0.2.0) | | Later, with the incident. |
| Vashpuk, the amber fuel bladder that regrows after tapping | flora pitch 6 | kept, quoted | A named fuel source. | |
| Colour on the flora against the "glass-clear" palette | flora pitch §8 | kept as art direction (his palette law of 2026-09-29) | | |
| The three donor water plants | bedazzle review §5, roster json | lost (cut by him 2026-09-28) | | |
| Only hydrocarbon plants | carbon garden, flora pitch | kept, his words | | |
| Cold wax: the product of every harvest and carcass; ruins then wicks when warm | life brief §7, bedazzle review mark 3 | kept | | |
| Wax refined to chemfuel in a cold room; "it is ordinary fuel" | life brief §7, cleanse | kept; it is the biome's fuel answer | Today's ruling. | |
| Burner glands and Swallower gut-oil as fuel products | sheet §7 | kept, reshaped: all carcasses give wax | Not found as separate built items. | |

### Animals

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Admission test: hydrocarbon, cold-stable, warm-reactive | sheet §4 | kept | | |
| Swallowers: tear plants up whole, sealed gut | sheet §4, life brief §3 | kept | | |
| Dorrak: shoot the hump and it takes you with it | life brief §3b | kept | | |
| Burners: a halo of blue fire at speed; explode if gravely wounded | sheet §4, life brief §4 | kept, quoted in part | | |
| Krissek's second death blast | cleanse next version | lost (recommended for dropping) | One death, one blast. | |
| Pickers: the vekkit, harmless herd scavenger | sheet §4, life brief §5 | kept | | |
| Zhaaz, the living propane-slush lobe, engulf-feeder | sheet §4 amendment, roster json | kept as an ordinary animal | Built; its engulfing is not promised in 0.1.0. | Promise the engulf at 0.2.0: needs its own scene. |
| Vrisk, the kite-thin flier, real flight | sheet §4 amendment | kept | Flyers fly. | |
| Dovvik, the proboscis defuser | sheet §4 amendment | kept as a grazer | | |
| Dovvik safe trails and the tame minesweeper | bedazzle review slate I | moved (next version → 0.2.0) | | |
| Utikka, fist-sized cropper, the krissek's staple prey | sheet §4 amendment | kept | | |
| Vhaulk, the walking cistern: "a hill that was not there last season" | cast bible §1 | kept, quoted | | |
| Vhaulk dies quiet by cold or kinetic, loud by heat; ion on a living one detonates it | sheet amendment 2 | kept, quoted | His ruling, and the best joke available to an ion-armed crew. | |
| Lure a vhaulk to a siege camp | cast bible §1, bedazzle review slate C | kept, quoted | It answers "what does this biome do to the Empire's fight". | |
| Tap it alive at the valve | cast bible §1 | moved (next version → 0.2.0) | | |
| The vhaulk walks off with a sign; never vanishes | cleanse definition | kept | Standing rule. | |
| Vhaulk stats, rarity, art notes | cast bible §1 | kept as build and art facts | | |
| Murrek as a visible flat predator | cast bible §2 | kept | | |
| Murrek buried in drifts, re-armed by storms, flushed by digging | cast bible §2, bedazzle review slate G | moved (next version → 0.2.0) | | |
| "The poles are not long enough" | cast bible §2 | kept, quoted above | | |
| Ossivel as a herd animal, tameable | cast bible §3 | kept | | |
| The choir and its silence alarm | cast bible §3, mechanics review | lost (cut 2026-10-23) | | See "the ones I would look at". |
| Tameability relaxed; a native pet needs the cold | sheet amendment 5, cast bible §0 | kept; the cold room it needs aboard is drawn out | Natives overheat above freezing. | |
| The butane gut for foreign grazers | life brief §2f | kept; shown on a crew pet | | |
| Native corpses stay dangerous | cleanse ambiguities 10, life brief §2e | kept (owed work) | | |
| Thunderbeast as a trace animal | bedazzle review §2, roster json | kept where the campaign patch puts it | | |
| Thunderbeast's electrical attacks and flashstorm | cleanse next version | kept in "later" | Lightning is flame to a charge; a storm-summoner here is a second system. | |
| Vapaad on the campaign patch; multi-homed | roster json, cleanse | kept; its ordinary body is `NEEDS HIM` | No evictions. | |
| Sparse by doctrine: richness is role variety | bedazzle review §2 | kept | | |
| Art queue notes and commissions | cast bible §7, bedazzle review | kept as art-ledger history | | |

### The ship, the hold and the gods

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The Cold Hold: blue ice as water stock, wax and glands as a windfall safe only refrigerated; "one cooling failure aboard and the pantry is a bomb" | sheet §7 | kept, quoted | Already written about the ship. | |
| "The phase-line physics travels with you" | sheet §7 | kept, quoted | | |
| Loose ice cools a room with no rack, for a very long time | owner answers 2 | kept, quoted | | |
| The cold rack: powerless cooling, tint, groan, hours-left readout | mechanics review, cleanse | lost (superseded by his answer) | | See "the ones I would look at". |
| Meltwater drip from the rack | mechanics review, fluff cuts | lost (cut 2026-10-23) | | |
| Blue ice into the water system | cleanse definition (FlowWorks) | folded into shared machinery | | |
| Drift burial of the landed ship, a dig-out on departure | bedazzle review slate F, sheet amendment 6 | moved (next version → 0.1.0, as ordinary drift at the hull) | Today's ruling on hull wear. | |
| "Tuning so it reads as weather, not tax" | bedazzle review slate F | kept as the test of the dig-out | | |
| The Returned | rites pass 3.1 | kept in "later" | | See "the ones I would look at". |
| The Charged Reed: cut one reed from a live field carrying nothing that sparks | rites pass 3.2 | kept in "later" | | |
| The Field of the Returned as a precept package | bedazzle review slate H | kept in "later" (the rites carry it) | | |
| Rites allowed in every biome | sheet amendment 4 | kept | | |
| The nine-mark scorecard | bedazzle review §1 | lost | A review instrument of its day; its findings are in the rows above. | |
| Mod Settings, and the vhaulk gate that makes things worse when off | cleanse definition | kept; the defect is named in the design | | |
| Fuel paths that differ in access cost, never viability | pursuit (campaign lore) | kept as the frame for the fuel answer | | |

### Found by the second reader, 2026-11-18

Rows the first read had no row for. Same columns. Where the "source" cell names a source by the short names above,
the file actually read is in the "why" cell if it is not one of those.

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The horror emerges from beauty and emptiness, never from a landscape that already looks like horror" | sheet header | kept, quoted in the design | The rule for how the Horrors may ever show here; the first read kept the ban and dropped the sentence. | |
| "Everything alive here lives two degrees on the warm side of a phase line. Two degrees the other way, and the propane pools" | sheet §3 | kept, quoted in the design | It is why the propane lakes are the next stop down and the replete one; a crew reads it as a route, not as chemistry. | |
| Methane as the exchange metabolite; metal-organic membranes; "some fast creatures toying with the extreme energy of oxidation" | sheet §3 | lost | Chemistry lore; the Burner line carries what the player sees. | Flavour text on the krissek's card; free. |
| "A crysalis is a butane charge with a program"; release "at proximity using stored energy reserves" | sheet §3 | kept in the campaign layer (Night Horrors), quoted | It says the Horrors' release is the same charge family, which matters to whoever builds the 0.2.0 quarry link. | |
| "The Horrors are not residents; they are delivered — by thaw, or by trigger" | sheet §5 | kept, quoted | | |
| The fallen are "free for the finding, guarded by whatever thawed beside it" | sheet §7 | kept, quoted | Salvage with a tax, in his sheet's own words. | |
| "Waves of different civilizations trying to mine the ice, drink the propane" | sheet §8 | kept, quoted | | |
| "A cocoon face in a cut ice wall"; "the alien script's unknown color"; "drifts leaning on ruined quarry gear" | sheet §9 | kept as art direction for the old workings | | |
| "Knife-and-sensor country by different physics than the crags" | sheet §7 | kept, quoted | Says what a fog fight is. | |
| No cultivation is also "the infinite-generator guardrail" | sheet ban 2 | kept (the reason joins the dropped list) | A sowable fuel plant aboard is unlimited fuel; it would break the fuel leash. | |
| Blue ice is the top row of the water taxonomy | sheet §7 | folded into shared machinery (FlowWorks water kinds) | | |
| Receiving ground for the dissolved Horror Wastes; its 29 legacy cast rows; region names | sheet header, §0, Owed | lost | World painting and roster history. | |
| Donor silhouettes (Blareebian tree, cactus) "as shape references only" | sheet §0 | lost | Superseded by the fractal register. | |
| "Hard to ignite" is authored, not free: the engine's fire knows nothing of cold, so every native carries a very low flammability | life brief §1c | kept as a build fact | The one sheet sentence the brief found engine-false. | |
| Engine facts the build must not rediscover: plants on ice must ignore fertility; the growth band written below freezing; no cave-plant flag; a charge comp cannot be the vanilla explosive on a plant or a pawn | life brief §1a, §1b, §1e | kept as build facts; the brief stays the only place they are written | Not design, but the brief must not be deleted before they move to the mod's own notes. | |
| The plant-growth multiplier would quadruple these plants unless exempted | life brief §6a | kept as a build fact | | |
| Tier: these are free-tier defs, not campaign | life brief §0c | kept | | |
| Forageability zero: "nothing a human can forage that will not detonate in a pack" | life brief §6c | kept, quoted | It is the larder limit, said by the source. | |
| Six settings: native detonations, flora chains, warm-reactive products, butane gut, halo effect, warm threshold slider | life brief §9 | kept, reshaped: the threshold slider is tuning, the rest stand | | |
| "The sheet's bans are NOT toggles": no setting may add sowing | life brief §9 | kept | | |
| The warm threshold is "a warm room, not a warm breath": two readings in a row, so one gust from a nearby blast does not chain the field | life brief §2b, §6a | kept as the meaning of the warning | It is what makes "take the heat away in time" true. | |
| "The field is a fuse laid by the spawner": palefloss carries, glassfern steps it up, a chimeglobe "restarts the whole thing" | life brief §6b | kept, quoted | Gives the three first plants different jobs in a chain the player can read. | |
| "A crew that clears a firebreak with knives is doing the right thing; a crew that clears it with a flamethrower is the sound in" the sheet's last line | life brief §6b | kept, quoted | | |
| Plants are the only beauty on the plateau (beauty stat on glassfern and chimeglobe) | life brief §6b | kept as a build fact | | |
| Slow growth: "without the polar water molecule, transport and chemistry are simply less efficient" | life brief §6a, sheet §3 | kept | A cleared apron stays cleared for the length of a stop. | |
| A blast indoors heats the room, which pushes every other native thing in it over the line: "the chain reaction indoors, for free" | life brief §1h | kept | It is why one pop in the hold is the whole hold. | |
| Wax shows an "Overheating" percentage for a little over an hour before it wicks | life brief §2c | kept | The readable gauge for cargo that the first read said was lost with the rack. | |
| Five wax to ten chemfuel; no gate in the recipe: "a fact about rooms, not a rule in a recipe" | life brief §7 | kept, quoted; the ratio is tuning | | |
| Wax pricing left to the trade sweep | life brief §7, §10 | lost | Never set. | |
| Salvager nicknames: the dorrak is a "cask", the krissek a "torch", the vekkit a "linewalker" | life brief §3–§5 | kept, quoted | Crew slang is how a Jawa would name them. | |
| "The crews call them casks and give them the road. Nobody who has shot one in the belly has described it afterwards" | life brief §3 | kept, quoted | | |
| The dorrak's hump is one shot in ten; "a hunter who reads the health tab can avoid it" | life brief §3b | kept | The counterplay. | |
| "They do not live long and they do not seem to mind"; "never, ever go for the body shot" | life brief §4 | kept, quoted | | |
| A pack of krissek: "a pack of torches is the biome's set-piece" | life brief §4a | kept, quoted | An OMG beat the first read had as one animal. | |
| The krissek never hunts a dorrak (it would go up with it) | life brief §4a | kept as a build fact | | |
| The krissek's halo shows only when it runs, flees or fights; grey on grey at rest | life brief §4b, §8 | kept | The tell: colour means it has seen you. | |
| No real light on the krissek (painted halo, cost unmeasured) | life brief §4b, §10 | kept as an open build call | | |
| The vekkit "walks like a folding chair"; "not interested in you unless you are lying down"; the crews "follow them to the good salvage" | life brief §5 | kept, quoted | Following pickers to salvage is the most Jawa line in the brief. | |
| The vekkit's charge is "the one you can survive standing next to"; a pack butchered warm is the hazard | life brief §5b | kept | | |
| Pickers digging up buried salvage | life brief §5b, §10 | lost (default no; never ruled) | Their gathering is placement, not behaviour. | 0.2.0 with the ablation incident: the tell is already "scavengers converging". |
| A live native brought into the warm dies of heatstroke and goes off: "Bring one indoors and the room does the rest" | life brief §1f | kept, quoted | Free from the engine; it is the souvenir beat with a live animal. | |
| A foreign grazer that keeps eating the field "dies of it and takes the barn with it": the butane gut itself goes off at death | life brief §2f | kept, quoted | The first read kept the illness and lost the blast. | |
| Juveniles go off at the adult radius | life brief §1d, §10 | kept as an open build call | | |
| The krissek is frail on purpose, "droppable from range before it closes" | life brief §4a, §10 | kept as tuning | | |
| "A tamed dorrak is a walking bomb in a barn, and a krissek pet is a torch in the kitchen"; "the barn temperature [is] the whole game" | life brief §10 | kept, quoted | | |
| Desiccated corpse art for dorrak and krissek; a six-legged boiler with a lid, haunch-and-jaw with no ears and no tail | life brief §8 | kept as art direction | | |
| The blue accent "owned by the krissek halo only" | life brief §8 | kept, reshaped: his palette law of 2026-09-29 later gave the flora colour | | |
| A wounded vhaulk turns on its attacker every time: "neutral until wounded; then the mountain notices you, slowly" | cast bible §1 | kept, quoted; the design's "right way" scene now says so | The first read had the kinetic kill as patient work; the source makes it a fight with an enraged giant, which is the better scene. | |
| "Kill it near your base and you have detonated a district"; a blast inside chains "can glass a quarter map — that is the point" | cast bible §1 | kept, quoted | Scale of the mistake, in the source's words. | |
| "The read from a distance is terrain; the read up close is a mistake"; "it eats a floss field the way weather eats a footprint"; "the crews who thought that was poetry are the reason the crews steer wide" | cast bible §1 | kept, quoted | | |
| Never a second vhaulk on a map; most maps never see one | cast bible §1 | kept | | |
| Lightning sets a vhaulk off for nothing (its strike is flame) | sheet amendment 2, cast bible §1 | kept | Matters to the thunderbeast row: a storm-caller beside a vhaulk. | |
| The vhaulk's own grazing never chains; its bite is weak on purpose: "the danger must never be its teeth" | cast bible §1 | kept as build facts | | |
| The warning about the mountain is carried "obliquely... never as a tooltip spoiler" | cast bible §1 | kept | The ion joke only works if the game does not say it first. | |
| The vhaulk as "the anti-siege weapon the quarry epochs learned to fear"; older than the later epochs | bedazzle review §3, cast bible §1 | kept, quoted | Ties the mountain to the old workings. | |
| The frost on its flanks ("the cistern is colder than the animal") and the sludge window, "the one hint of what it is full of" | cast bible §1 | kept as art direction | | |
| "A drift leaning against your wall might be a drift"; "In the open it is unimpressive; the drift IS the animal"; "flat as a dropped tarp" | cast bible §2 | kept, quoted (0.2.0) | | |
| Flushing a murrek with fire "re-arms the field a different way" | cast bible §2 | kept (0.2.0) | | |
| Ossivel: "the only proof for a hundred kilometres that anything is glad to be here"; "The crews like them" | cast bible §3 | kept, quoted | The line survives the audio cut: it is about the animal. | |
| "Butchering the choir is a choice the colony hears"; a startled choir dying together in a floss field | cast bible §3 | lost with the soundscape, in part; the herd blast stays | | |
| A tamed choir as "a living perimeter alarm" | cast bible §3 | lost (the alarm was cut 2026-10-23); the animal stays tameable | | If the choir is reopened, this is its use aboard a ship. |
| The choir falls silent for big bodies only: "a colonist in armour does not qualify; predators and the mountain do" | cast bible §3 | lost (cut 2026-10-23) | | |
| Virr as "the only plant on Ash'karr that tells you its own state"; its scream and the crack cue "one system heard two ways" | cast bible §4 | lost (cut 2026-10-23), noted: the crack cue that was kept reads the same countdown | | |
| Names restyled for variety at the sitting (sivvet became ossivel, virrell became virr); rejected names from three sweeps | bedazzle review §3, §5; flora pitch §7 | kept (final names); the rejects are lost | | |
| The Field of the Returned: "where the sky gives back its dead — the one place on Ash'karr where what is lost returns, incorruptible"; the script as "sacred text nobody may read aloud"; "the ones who dug are still here" | bedazzle review slate H, §1 mark 9 | kept in "later", quoted | The gods layer's own lines; the first read kept only the heading. | |
| Vapaad placed here by him: "This goes in the blue desert... why couldn't I see that in the dropdown?" | roster json | kept, quoted; the NEEDS HIM question on the outsiders now says taking it off contradicts this | His own placement. | |
| Mynock and neebray are not rostered here; fliers may cross | roster json | kept | | |
| No fish: "zero water, zero rivers" | roster json | kept | | |
| Boomalope cut: "Absolutely no boomalopes" (his card, 2026-09-14) | roster json | kept (dropped list) | The one existing bomb animal, and he cut it everywhere. | |
| Never audit this roster from a live dump (the padder shows every animal at zero) | roster json | kept as a build fact | | |
| Vashpuk refills in about ten days; "a fuel well that is also a bomb you must never let warm"; "the scavengers' fuel tap" | flora pitch 6 | kept, quoted | Ten days fits inside a stop: two or three taps. | |
| Kethevar: "the player earns it by deliberately detonating a field"; "the quarries' 'it is all still here' economy, made from the plants" | flora pitch 3 | kept, quoted (0.2.0) | | |
| Lisqueth: "a field of them is a postcard"; "killing the light is the cost"; never warm in colour, so the krissek keeps the only warm light | flora pitch 4 | kept, quoted | | |
| Qeshra roe is feed for tamed natives, kept cold, and goes off warm like wax | flora pitch 1 | kept | What a cold-blooded pet eats aboard. | |
| Uzhmek is tholin, "literally what the Haze leaves behind" | flora pitch 2 | lost with the plant | | |
| Longglass's frost is the Haze's own rime, on new growth only; it cannot turn, so it leans | carbon garden §2 | kept as art direction | | |
| Frost-fibre could ship as a cold-store packing that is never brought indoors | carbon garden §2 | lost | Decided against, 2026-11-03 (delegated). | |
| The Carbon Garden came from a GPT consult, advice only | carbon garden | kept as history | | |
| His words on the whole biome: "We likely need to revisit this biome and do a full redesign pass"; "The mod may be making more to-do about making ice blocks than is warranted" | owner answers | kept, quoted in the design's status header | The first read quoted the answers and left out that he asked for a redesign. This rewrite is an agent's attempt at it, not his approval. | |
| What the ice reserve buys: "Time to restore cooling: reduce traffic and repair powered cooling"; ice cools "until the ice gets dangerously warm" | owner answers 2 | kept | The cold hold promise already tests exactly this. | |
| The passing giant is a second animal, "separate from the existing vhaulk" (an owner-filed item asks for one) | owner answers (questions page) | kept in the 0.2.0 row for the passing giant | | |
| Warming does not reset in a container, in hands or off the map: no "free refrigeration" by loading or leaving | cleanse definition (Edges) | kept, added to the design's hull section | A ship in flight is exactly this case. | |
| A death off the map cannot blast an unrelated map | cleanse definition | kept as a build fact | | |
| Blue ice melts to water at a campfire or stove (built); the bucket and melter routes give different yields for the same ice | cleanse census, walk | kept, added to the first day; the yields are folded into shared machinery (FlowWorks) | A fire on this ice is a Jawa decision. | |
| The drift's blue-white tint is unbuilt | cleanse census | kept (owed) | | |
| Wrecks here are ice-locked and "must mine free first"; the ice jacket is a named gap | walk, cleanse census | kept, added to the first day (owed) | From the salvage design's row for this biome (`design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md`). | |
| A deep drift is a walking cost, never a wall, and no sand lies under a building | cleanse ambiguities 22 | kept, added to the hull section | It means the drift cannot trap the ship. | |
| The ablation "crack" is a text message since the audio cut; vekkit and vrisk circle the spot | walk | moved with the ablation incident (0.2.0) | | |
| Newborn natives miss the charge; an old all-on settings file must not switch on deferred features | cleanse tickets | kept as owed build work | | |
| "The easiest false success": a blue icon, plain ice, spawned blocks, separate blast demos and a rack proof | cleanse ambiguities (second attack) | kept: the promises table's "what rules out a fake" column carries it | | |
| A small avoidable disaster "should be more interesting than repeated arbitrary instant losses" | cleanse definition | kept | The test of the whole stop. | |
| Cleared growth regrows and "must be inspected before each expedition" | cleanse definition | kept, added to the first day | | |
| Rites of the Nine found in a biome, these two by name, are for the second release (his ruling, 2026-10-23) | mechanics review | kept in "later", with the ruling now cited | The first read placed them right without the ruling. | |
| The Returned is found as "a line scratched on the inside of a returned hull's hatch, in the clan's own trade script, by someone who fell"; "the sky gave back someone who went farther than anyone alive, and the clan takes him farther still"; the body "rides in the hold until the player chooses to bury it" | rites pass 3.1 | kept in "later", quoted | The fallen one was a Jawa: the only place the sources say so. | |
| The Charged Reed: "No fire, ion weapon or powered light may be carried"; the reed whistle "will sing before the ground does"; studied only in the Haze | rites pass 3.2 | kept in "later", quoted | A rite that disarms the clan of its ion is the same joke as the mountain. | |
| The Warnings were ruled biome-local at the sitting: no ideology defs, the gods layer "delivered as prose" | bedazzle review §5 | kept in "later" | From the build item `BLUEDESERT_MECHANICS_BUILD_1` §2; rites were allowed in every biome three days later. | |
| The Horrors are the night side's raiders whether or not anyone mines: "the weapon on patrol comes out of the cold" | sheet header | kept, reshaped: the design's "who else attacks" now says so | From `assailant_weapon_remnants.md`, which the first read did not open. The design had them only as a mining consequence. | |
| "Degraded LESS than anywhere else"; the BroodLord "still takes victims alive — samples for a master who no longer exists"; his words: "A semi-live version of the weapon slowly operating on the frozen darkside" | sheet header | kept in the campaign layer, quoted in the design | Same file. | |
| Six Horror kinds, hives, dens, sinkholes and crysalises as injected dungeons; reach "nightside-only" still awaiting his confirmation | sheet §8 | kept in the campaign layer | Same file. | |
| Hull wear, cold: the shield frame already counts forty below as a hazard ("exposed systems will cold-seize over time") | pursuit | kept, added: the design's hull section now leads with it | Found in `src/RimUtinni/ShipShields/` and `ship_shields_deep_design.md`; the first read cited neither. | |
| Hull wear, sand: the frame counts any weather carrying sand, and the ice-sand drift rides that field | pursuit | kept, added (unmeasured live) | Same. | |
| The cryo envelope, his words: "Pulls in heat in both directions and allows the shields to start glowing with red-orange black body radiation"; a cold trip is "expedition-shaped: fuel committed up front" | pursuit | kept, quoted; the glow against the dark is a new NEEDS HIM | Same. | |
| "Slow pressing things move through all shields": no field answers the drift | pursuit | kept, quoted | From his shield rulings as recorded in the shared machinery file. | |
| The ship contribution by his card of 2026-09-24 named the rack "the deck part" | sheet §7 | lost (the rack went with his answer of 2026-11-10); asked as NEEDS HIM | From `BIOME_SHIP_CONTRIBUTIONS_1`. | Name a new part. |
| Kuvvel, the Watchers animal for this biome: "a drift whose kuvvel all sink holds one" | cast bible §2 | moved (unlisted to 0.2.0, with the buried murrek) | From `design/RimMandrake/watcher_creatures_pitch.md`; no Blue Desert source mentions it. | |
| The dovvik as first written, the "defuser": "a dovvik-cleared field is safe to walk warm"; it leaves "drained glass, inert"; "dead glassfern just lies there, a live charge forever" | life brief §0b | moved with the safe trails (0.2.0), quoted | From `RUT_hydrocarbon_ecology_commission.md` §6, where the cast began. | |
| Chimeglobe "named for the sound a field makes in wind"; it sheds seed-lattices on the drift | life brief §0b | lost (sound cut); the shedding is art direction | Same commission. | |
| "The Blue Desert's dead arrive here and are eaten": the propane lakes' crawlers sift what this plateau sheds | life brief §0b | kept as the neighbour's lore | From the propane lakes' names page. | |
| Thunderbeast's drafted name "yuddra", "the one y- word on the planet" | roster json | lost (a draft, never applied) | | Apply it when the animal's body is settled. |
| "Blue Desert People" is an existing Star Wars Legends phrase (the Kwi) | experiences | lost: no source ties this biome to it | Found in the canon library; noted so a later reader does not think it was missed. | |
| GPT's eight unpicked enrichment ideas of 2026-09-30 | carbon garden | lost, and unreadable: the consult lived in Transient and is gone | "The owner picked these four... GPT's eight other ideas were not picked, so they are out." | |
| A snapshot of weather mix, thresholds and radii (tuning readings) | cleanse | kept as build facts, never promises | | |

## Sources read, and the count

Measured after writing: a script counted the table rows and the first words of the "what happened" column; its
figures are the last paragraph of this section.

Read whole: the sheet; the cast bible; the bedazzle review; the carbon garden; the cleanse's owner pages,
definition and next-version list; the owner answers and the questions page; rites pass §3. Read in large part: the
cleanse's ambiguities (all thirty-four entries, most cut off after their first few sentences); the flora pitch (the
first lines of each of six cards, the owner questions and the card draft, not the full cards or the collision
sweep). Read by heading or by search only: the life brief (`blue_desert_hydrocarbon_life.md`, 47 KB: headings and
what the other files quote from it); the cleanse's tickets (titles and the first five) and census (searched for
plant names); the walk (north star and the first anti-guessing notes); the mechanics review (the Blue Desert
table, rows cut off at 600 characters); fluff cuts; the experiences table; the roster json (keys and names).
Not read: `assailant_weapon_remnants.md` (the Horrors' own sheet); the designer rehearsal's `NOTES.md`,
`QUESTIONS.md`, `designer_brief.md` and `record.json`; the cleanse's `bars.json`, `models.md`, `review.json`,
`converge.json` and `fixes.json`; and the forty-odd other files under `design/RimMandrake/` that mention the Blue
Desert in passing.

*(First read's count, kept as written; the count after the second read is at the top of this page.)*
**25 source files, 138 rows**, of which **18 lost**, **12 record a move** (whole or in part), **5 kept, reshaped** and 1 folded into shared machinery. Every source name is in at least one row's source column (checked by the same script; files read under one name, such as the cleanse's, count under that name).

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_blue_desert.md`, `bluedesert_bedazzle_cast_2026-09-28.md`,
`bluedesert_bedazzle_review_2026-09-28.md`, `bluedesert_carbon_garden_2026-09-30.md`,
`bluedesert_flora_expansion_pitch_2026-10-02.md`, `rosters/the_blue_desert.json`.

Also ready, since the second reader read it whole against this design on 2026-11-18:
`design/Jawa/worldbuilding/creatures/blue_desert_hydrocarbon_life.md`. It is the only place the charge family's
engine reasoning is written down, so its §1 moves to the mod's own notes before it goes.

Not for deletion: `design/concepts/BlueDesert/cleanse/` (superseded by this design, never applied; it should be
re-run from this file, not applied); the validation walk; the rites pass; the designer rehearsal folder.

Before deleting: the cast bible is the art commission's brief for five subjects, and the flora pitch and carbon
garden hold the art briefs for nine plants; those lines should move to the art ledger first. `the_blue_desert.md`
is cited by path in the rites pass and in `sleeping_ice.md`.
