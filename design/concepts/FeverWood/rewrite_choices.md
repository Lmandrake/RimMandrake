# The Fever Wood: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A second agent, which did not write the design, read the sources again before anything is deleted. It added rows,
corrected five, and changed the design in the places listed here. Nothing was deleted.

**Rows added: 94.** They are in "Rows added by the second reader", at the end of the row tables.

**The three most valuable things the first read missed.**

1. **The fever.** His freeze ruling R15 of 2026-09-07 says what the Fever Wood's fever is: *"the fever is fungal —
   the wood's own spore load, which is also what Sporefall is named for and what the Wildsteam harvest there. The
   hazard and the resource are the same thing, so living there is a bargain rather than an accident."* It never
   reached the sheet and no source after it mentions a disease, so the biome's own name had no row. It is now a
   question for him, not a feature.
2. **A young one can only be tamed where there are no pools.** His ruling of 2026-09-23: near pools a released
   young *"plops down into them and installs itself as a new tentacled horror"*; *"on a map without such pools,
   it will escape and simply wander wild"*, and only then can it be trained. *"It remembers the tank..."* A
   colony in the Fever Wood can never do it. A ship that carries the tank to another stop can. It was in a closed
   ledger item, which the first read did not open.
3. **What the crew gets out of the two-front war, and out of the ransom.** The sheet's *"Chitin and salvage — the
   two-front war's leavings: stand back, let them, mop up"* had no row, and it is the most Jawa line in the sheet.
   And the "one great gift from the bottom" is built with a gravcore in its table.

Also recovered: his line *"It is not an unknown mystery, but a mystery still for most of the game"*; the sheet's
*"Nothing goes in the water here. Everything remembers why."*; and the lure's bait rule, which the first read
called unset and which was decided and built on 2026-11-03.

**What changed in the design, and why.**

1. *The Mooring in full came out of 0.2.0 and became a question.* It was offered by name on his card of
   2026-10-02 and not chosen. A ship idea he passed over is not revived without him.
2. *The no-fight charge moved from 0.2.0 to 0.1.0, still a question.* His ladder of 2026-09-23 names it, his
   answer of 2026-11-10 names it again, the bar validated on 2026-11-16 says "treatment", and it is built. The
   cleanse of 2026-11-17 proposed deferring it; his dated words outrank the cleanse.
3. *The mirror list moved from "recommended for dropping" to 0.2.0, campaign layer.* The locked Designer sheet
   keeps it, and a locked sheet outranks the cleanse.
4. *Hull wear now says what the built frame sees here:* its heat case starts at 58 °C and this biome tops out at
   51.5, so both of the Fever Wood's wears are kinds the frame has to learn. Nothing was invented; both wears
   still come from the review of 2026-10-02.
5. *Fuel now cites the sheet's stills* (*"stills running nectar-liquor and seep-oil"*) for fuel made and sold at
   Sporefall.
6. *Two moments were added* ("Mopping up", "The gift from the bottom"), *one 0.1.0 line* (limbs that sink back by
   themselves, built) *and one "later" paragraph* (taming a young one somewhere without pools).
7. *The status header now says the locked Designer tree is a colony that stays and is not edited,* and names the
   two north-star bars validated from it.
8. *A new question 3* asks him about the fever. `NEEDS HIM` went from one question to three.

One thing found that this run may not fix: `design/RimMandrake/biome_shared_machinery_2026-11-18.md` still lists
the Fever Wood's *"snare and torn-off section 0.2.0"* in its hull table. That file is not this run's to edit.

**Measured counts** (by script, with a probe; recorded in
`design/RimMandrake/biome_recheck_feverwood_greentide_abyss_row_check_2026-11-18.txt`): 261 rows, of which 42 lost,
18 moved, 23 kept and reshaped, 2 folded into shared machinery, 176 kept. **49 source files read in full**, each
opened and read to its end: the nine older biome files below and the shared names doc; ten files of
`design/concepts/FeverWood/` (the Designer sheet, journal, log and plan; the cleanse's definition, next-version
list, owner pages, ambiguities, models and tickets); the shared-machinery file, the shield rulings and the shield
hazard source; and twenty-six ledger items.

Read in part, and counted as not read: the cleanse census and the Designer record (ids, summaries, decisions,
asks and contradictions, by script); the Fever Wood section of the 2026-10-22 mechanics review (whole) and the
walk's north star; the freeze rulings and review, the tenant digest, the rising note, the Designer-codex notes and
the fluff cuts (by search for his words and for this biome). Not opened: `FEVER_WOOD_MECHANICS_1` and
`FEVERWOOD_RM_MOD_BUILD_1` (build logs), the seven open build items and six small closed ones, the GPT review of
2026-10-08, and the pipeline's `tree.json`, `scenes.json`, `exam.json`, `bars.json` and run folders. None of the
files in this paragraph is on the delete list.

DELETE-READY: yes

That line covers the nine files listed at the end of this page: each was read to its end by the second reader, and every idea found in them has a row. Three questions for him are open
(`NEEDS HIM` in the design); none of them turns on a file being kept.

Companion to `design/concepts/FeverWood/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, the crew are Jawa *"way in over their head"*, *"anything that takes seasons to observe will simply be
missed"*, and for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is
*"the overriding priority"*. So: a thing a crew meets inside a stop of days went early; a thing only a settled
colony would see went later, however good; nothing he had ruled was reversed, and where the lens argues against one
of his earlier picks the row says so and the design marks it `NEEDS HIM`.

**Words used in "what happened".** *kept*: in the design with its meaning intact. *kept, reshaped*: in the design,
changed as stated. *moved*: its scope bucket changed, from and to given. The older cleanse proposal
(`cleanse/definition.md`, 2026-11-17) used three buckets, "first version", "next version, switched off" and
"recommend retiring"; this design uses 0.1.0, 0.2.0, later, dropped. A cleanse "next version" item that lands in
"later" is counted as *kept in its bucket*, not as a move. *folded into shared machinery*: it is a shared engine's
job. *lost*: not in the design.

## Changed after his rulings of 2026-11-18

His card of 2026-11-18, 3:10 PM PST answered three of the four questions the first pass left for him here, and
ruled on stop length and on a test for every solution. This revision changed the design and this page as follows
and nothing else.

1. **Stop length is stated, as an outer edge.** The "UNSETTLED: how long a visit really lasts" paragraph is gone.
   The design now says about six weeks at the outside, from the pursuit's own arithmetic and the crown's cover, on
   his words *"The numbers you're generating are likely the outer edge allowable for each biome, and that's just
   fine. Go with that."*
2. **The crown is partial cover from orbit.** The question "Does the crown hide the ship from orbit?" is removed
   and answered by his card (*"Canopy, steam and fog slow the search by one step; full dark still pauses it"*).
   **My reading, to check:** "one step" is written as one band on the pursuit's built visibility scale (hidden,
   discreet, noticed, marked, exposed), because those are the only steps the search has. Going from noticed to
   discreet multiplies each wait by 1.4 in today's provisional numbers. If he meant one rung of the ladder, or a
   flat delay, the "clock" section and one promise row change and nothing else does.
3. **The place wears the hull, in 0.1.0.** The question "Does the water touch the ship?" is removed. The wear is
   taken from the one source that names it, the Mooring row of the 2026-10-02 review: the marsh (*"a ship on mud
   lists and mires a few hull cells a day"*) and the water (limbs in reach of a hull edge). Both are in 0.1.0 with
   a sign and an answer.
4. **The Mooring in full moved from lost to 0.2.0.** The snare, the torn-off section and the crew's own plate set
   out as bait were "lost as pitched" in the first pass because he had not chosen them on 2026-10-02. His ruling
   that biomes wear the hull is the reason to bring the Fever Wood's own version back; it is not in 0.1.0 because
   he called hull wear *"easy"* and the tear-off is a new system. Listed under Scope moves; one line to revert.
5. **Seep-oil is the Fever Wood's richer fuel source.** The question "Is seep-oil ship fuel?" is removed. The
   sheet says fuel twice. The slow biomass route is stated as the emergency route; the oil-to-chemfuel recipe and
   fuel on sale at Sporefall are 0.2.0 (nothing builds either, and his words give no version); the Fever Wood is
   not called replete.
6. **A new section in the design, "The ship while it sits here"**, holds cover, hull and fuel together. Two
   promises were added to the 0.1.0 table (hull wear; the crown's step), two on-screen moments (the sinking
   corner; paying for fuel with bait), three scope lines in 0.1.0 and two in 0.2.0.
7. **"Very Jawa" applied where a choice was open:** footings jacked under the hull from salvage instead of a
   purpose-built pad; fuel paid for with the water's bait; the oil skimmed in pairs from inside a pool's reach.
8. **A finding for the shared-machinery file:** the hull-wear frame already exists in the campaign
   (`src/RimUtinni/ShipShields/`, with his eight shield rulings of 2026-09-02 in
   `design/Jawa/proposals/ship_shields_deep_design.md`). The first pass did not find it. Two of his lines there
   decide what answers the Fever Wood's wear: nothing *"holds out water"*, and the heavy field resists *"large
   animal assault"*.

Read for this revision, in part: `ship_shields_deep_design.md` (the ruled table only), `ShieldHazardExposureTracker.cs`
and `ShieldHazardUtility.cs` (header comments and the hazard tests), `EmpireLadderMath.cs` (first eighty lines),
`ScenParts_EmpirePursuit.xml` (whole), `reconciled_lore/01_campaign.md` (the fuel section), and the Mooring row
and the hull, ship and fuel lines of the review and the sheet, found by search.

## The ones I would look at

1. **The Mooring** (the water wraps the ship's hull; launching tears a section off). He did not choose it on
   2026-10-02, before he had stated the ship lens. Under that lens it is the most direct answer anyone has written
   to *"What happens RIGHT AWAY when the ship arrives from the sky?"* After his ruling of 2026-11-18 its plain half
   (the marsh and the lash wear the hull) is in 0.1.0 and its dramatic half (the snare and the torn-off section) is
   in 0.2.0. Moving the dramatic half was my call, not his words.
2. **The Lost Crawler** (the bait turns out to be pieces of one old Jawa sandcrawler, the clan's own). Not chosen
   2026-10-02. It is the only idea in any source that makes the bait personal to *this* crew. Lost; it also needs a
   long stay to collect the pieces, which is the honest reason it stays lost.
3. **The thieving bird.** The cleanse recommended retiring the promise. I moved it back in, to 0.2.0: a bird that
   robs a crew of professional scavengers is exactly the slapstick he asked for.
4. **The sap-drinkers' refusals.** The cleanse moved all three to "next version" as extras. I moved the seal and
   the swelling to 0.1.0 (built, deterministic, funny within minutes) and the scream to 0.2.0.
5. **The prison tank and everything that follows from it** (products, escape, the escapee growing into the real
   thing). *"That's why they're not farmed, they're imprisoned."* Beautiful, his, built, and a colony's story: it
   needs weeks of upkeep. Later. The one piece a travelling ship can use, returning a young for a great gift, is
   kept at 0.2.0.
6. **The reactive ant-hive dungeon.** His 2026-09-22 ruling made hives *"dungeons in their own right"*. Later,
   because a stop of days already has the pools competing for the same hours. If he wants one expedition per stop,
   this is the candidate to bring forward.
7. **The cistrel cup**, *"the only safe water in the Fever Wood"*. It should be early (water is what a stop is
   worth) and is at 0.2.0 only because the thirst service it needs is not in this checkout.
8. **Sink-mud.** *"The floor is the wall."* Unbuilt. It is the Fever Wood's real answer to an Imperial strike and
   to why small light Jawa do better here than armoured troopers. 0.2.0, and the first thing I would build there.
9. **Bog-timber.** The sheet's *"bog-timber and potter's clay"* lost its first half to the 2026-10-17 tree ruling
   (only true trees give wood). The tree stays as scenery. Nobody chose this loss for the Fever Wood in particular.

## Scope moves

One line per feature whose bucket changed against the cleanse proposal of 2026-11-17 (or against his earlier card,
where said). Each can be reverted by moving the line in the design's Scope section.

- **Vaulm seal and drommath swelling:** next version → 0.1.0. A crew sees them the first time it handles one.
- **Ollareth alarm:** next version → 0.2.0. Same reason, but what answers the scream is undefined (the old gap the
  coverage judge named), so it waits for that definition.
- **Thieving bird:** recommend retiring → 0.2.0. Slapstick against scavengers; costs one gated behaviour.
- **Lure stake and the two fronts:** next version → 0.2.0. "Who else attacks here" is one of his lens questions,
  and the staggered arrival can be pointed at an Imperial strike.
- **Oil boil:** next version → 0.2.0. His card of 2026-10-02; a weather event shows itself inside a stop.
- **Radioactive charge:** next version (question pending) → 0.1.0, by the second reader, question carried over
  (`NEEDS HIM` 1). The first pass had 0.2.0.
- **Mirror list:** recommend retiring → 0.2.0, campaign layer, by the second reader (the locked sheet keeps it).
- **Chitin and salvage from the two fronts:** no bucket → 0.2.0, with the lure.
- **Limbs sinking back by themselves:** no bucket → 0.1.0 (built).
- **Ransom of the young (release and gift):** next version → 0.2.0. It rewards arriving with cargo, which only a
  ship does.
- **Summoning the eye:** next version → 0.2.0. A short stay needs a way to choose the moment.
- **Broken hives at the mirrors; the corvath spike as a placed tell:** next version → 0.2.0. Day-one evidence.
  (Corvath *appearing* after a feeding stays later.)
- **Wreck field; acoustic sounder readings:** next version → 0.2.0. Salvage is the crew's trade and the sounder is
  a ship part.
- **Sink-mud and the skimmel skin:** next version → 0.2.0.
- **Cistrel cup:** next version → 0.2.0.
- **Stayed "later" from the cleanse's "next version":** tank industry, escape and maturation, world-held-young
  pressure, the hive (all five parts), borer galleries, regrowth and sealant, moving routes, plennith soil, mirror
  break, arrival letter, grolth trail, the Sporefall display. Not moves.
- **Hull wear by marsh and by reach:** asked of him → 0.1.0, by his ruling of 2026-11-18. Revert is his.
- **The Mooring in full (snare, torn-off section, own plate as bait):** lost → asked of him. The first pass moved it
  to 0.2.0; the second reader took it out again, because he passed over it by card on 2026-10-02 (`NEEDS HIM` 2).
- **The crown as partial cover from orbit:** asked of him → 0.1.0, campaign layer, by his card.
- **Seep-oil to chemfuel; fuel on sale at Sporefall:** asked of him → 0.2.0. The source is his ruling; the version
  is my choice. 0.1.0 instead costs one recipe and a trader stock line, and makes the first version a fuel stop.
- **New, not in any source:** stilt footings under a hull (stilts are built for buildings; this is a new use); the
  bait as what the crew pays for fuel with (a reading, no mechanism).
- **New, not in any source:** the ship's landing as a noise the water hears (0.1.0); troopers seized like anyone
  else and trunks breaking the Empire's sightlines, stated as promises with scenes (0.1.0). Both are consequences
  of built behaviour; drop either by deleting its line.

## Every idea, row by row

Source names: *sheet* = `biomes/the_fever_wood.md`; *deep-and-mud* = `biomes/fever_wood_deep_and_mud_2026-09-23.md`;
*fauna roster*, *flora roster*, *cast proposal*, *syllable pass*, *bedazzle review* = the dated files of those names
in `design/Jawa/worldbuilding/biomes/`; *kit spec* = `biomes/kits/fever_wood_kit_spec.md`; *roster json* =
`biomes/rosters/the_fever_wood.json`; *names doc* = `biomes/noncanon_beast_names_propane_arid_forge_pyre_fever_greentide_rust_lantern_blue.md`;
*Designer sheet*, *plan*, *log*, *journal* = files in `design/concepts/FeverWood/`; *cleanse* = `design/concepts/FeverWood/cleanse/`
(definition, next_version, owner_pages, ambiguities, tickets, models, census); *walk* =
`design/validation_walks/RimMandrake/FeverWood.md`; *owner answers* = `design/RimMandrake/designer_codex_2026-11-09/FeverWood/ANSWERS_OWNER.md`;
*tenant digest* = `design/Jawa/campaign/fever_wood_tenant_digest_2026-10-10.md`; *rising* =
`design/Jawa/worldbuilding/sekkulaath_rising_crater_event_2026-11-01.md`; *fluff cuts* =
`design/RimMandrake/fluff_cuts_2026-10-23.md`; *experiences* = `design/RimMandrake/biome_experiences_2026-10-20.md`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Wood-roads through a living crown above black mirror pools | sheet header, §1 | kept | It is the picture the ship descends into. | |
| "The place where trees finally won" | sheet §1 | kept | Carried over word for word. | |
| The giant stillness; one wetland with the Miasma, which is everything in motion | sheet header | kept, reshaped: the stillness survives as the silence; the Miasma comparison is not restated | A crew at one stop does not compare two biomes. | Restate the pairing in a campaign-level document; free. |
| The thirsty-flora family (Greentide and Webwork drank a river; here the trees drank the chaos) | sheet header, §3 | lost from this design | World lore, not something seen at a stop. It belongs in a world document. | Keep one sentence here; harmless. |
| Measured tiles, sun, temperature, no rivers, no rain | sheet §0 | kept, reshaped: no rain and no flowing water kept as bans; tile counts dropped | A tile count is never evidence (standing ruling); the planet is painted once at the end. | |
| Donor inventory kept: marsh too soft for heavy structures | sheet §0, §6 ban 4 | kept | The land's first rule. | |
| Low ground animal density, the crown teeming | sheet §0, deep-and-mud §6p | lost as a mechanism (owner: *"Don't worry about this"*) | Declined 2026-09-23. | |
| Trunks much more than one tile wide, mineable, never falling | sheet §1, deep-and-mud §6a | kept | *"So you can just mine right through one."* Also why the ship's landing topples nothing. | |
| The trunk's two built defs (the mineable body and the one-cell marker) and their bark-edge art defect | deep-and-mud §6a, flora roster §2 | kept as a build fact, not design | Art debt, owned elsewhere. | |
| Byways that *"seem fixed and are not"*, slowly varying | sheet §1, §5; kit spec; Designer sheet "later" | kept in "later" | Nobody sees a road move in a week. | Bring forward: needs the encroachment engine. |
| Water from below, life from above; deep mud as the nutrient bank | sheet §3, deep-and-mud §6e | kept as the reason the animal does not need the crew | It is what makes the baiting chilling. | |
| The oils boiling gently to the surface | sheet §3 | kept, reshaped: a plant you harvest (seepril), per the 2026-09-23 card | His card. | Ground that weeps oil: declined then. |
| Verticality is paint, walk on and off, no climbing | deep-and-mud §6h | kept | His card; zero new mechanism. | |
| Bough-soil, a fertile terrain so the crown can grow | deep-and-mud §6b | kept | Built. | |
| Stilts for building on marsh | sheet §7b, kit spec | kept, reshaped: stated once, not promised as how the crew lives | The crew lives aboard; stilts matter to a colony. | |
| Base-building in trees and bore-cave rooms | sheet §7, §7b | kept, reshaped: rooms can be mined; living in them is not promised | Same. | |
| "A lamplit crown over black glass — giant stillness, twice inhabited" (art theme, palette, light, sound) | sheet §9 | kept as art direction; one line quoted | The Wildsteam's lamps are campaign-layer; the two registers stacked (loud crown, silent floor) are kept. | |
| Experience line: *"A world in the treetops above a black mirror nobody touches. You live on the branches, and the water remembers."* | experiences | kept, reshaped: "you live on the branches" becomes "you visit" | It was picked by card for a settled colony. *"The water remembers"* is kept exactly (the angered pool). | Keep the colony reading for a later version; free. |
| The owner's November answer: routes shape the day, *"and a little 3 when tentacles emerge from the water"* | owner answers; Designer sheet | kept, reshaped: under the ship lens the water moves from "a little" to the centre | He gave that answer to a question about making a home. The lens he stated on 2026-11-18 changes the question. | Hold the old weighting: the stop becomes about walking routes, which a crew of days barely uses. This is the reshaping he is most entitled to reverse. |

### The thing below

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The sekkulaath: ours, invented, one species; the dianoga mapped over it in the campaign | deep-and-mud §1, §1a | kept | His naming. | |
| Never enters the screen; only tentacles are drawn | deep-and-mud §1 | kept | *"so big it can't even enter the screen"*. | |
| The horror is scale, not mystery; *"shocking even to those who know them"* | deep-and-mud §1 | kept, quoted | | |
| The old ban on naming or showing it in ordinary play | sheet §6 ban 1 | lost (superseded by him, 2026-09-23) | | |
| *"Never killable, only driven off"* | deep-and-mud §1 | lost (superseded by his own ladder the same day: the eye can be killed for the map) | | |
| Canon facts that do mechanical work (colour change, hum that scares prey, hearing, water-bound, regrows limbs, strips victims, eyestalk) | deep-and-mud §1 table | kept, reshaped: hearing, water-bound, regrowing limbs and the eye are in the design; colour change and the hum are not promised | The free tier must be whole without canon; the two dropped facts have no scene. | Promise a pool that *looks* empty and is not: needs art and a test. |
| The pools are windows onto one water table | deep-and-mud §6e | kept | Why one kill clears a map. | |
| It farms on purpose; intent without communication | deep-and-mud §6e | kept, quoted | The whole joke with Jawa. | |
| Treasure as bait, a slow renewing trickle | deep-and-mud §2 | kept | | A depleting hoard: declined by card. |
| The rare visible deposit | deep-and-mud §2 | kept, reshaped: must be seeable within a stop by a crew that watches | *"If you live there, you might even see"* was written for residents. | Leave it rare: most crews never see the best image in the biome. |
| Six limb types as a pseudo-bestiary | deep-and-mud §2 | kept (five ordinary, and the opening one with the eye) | Built. | |
| The feeler, blind, searching after noise | deep-and-mud §2 | kept | | |
| The snare, the killer, with the rescue window | deep-and-mud §2, kit spec card 2 | kept | | |
| The lash at maximum reach | deep-and-mud §2 | kept | | |
| The porter, *"more slender and delicate than the others"* | deep-and-mud §2a | kept, quoted | | |
| Attacking the porter angers the pool and ends its gifts | deep-and-mud §2a | kept | | |
| The sentinel, motionless, and the silence | deep-and-mud §2, §4 | kept; also the first thing the ship meets | | |
| The bloom that exposes the eye | deep-and-mud §2 | kept as the set-piece | | |
| Drive-off ladder: hours, a day with a severed limb, a day map-wide for the eye, permanent kill | deep-and-mud §2b | kept; durations described, not pinned | A bar is an experience, not a number. | |
| Severed tentacle as the only renewable source of the animal's meat | deep-and-mud §2b | kept | A take-away. | |
| Canon product line (pie, spleen tea, cream) | deep-and-mud §2b, §6j | kept in the campaign layer only | Canon names route through the campaign tier. | |
| "Permanently on the map" is per map | deep-and-mud §2b | kept | | |
| The set-piece must actually arrive | deep-and-mud §2b | kept, reshaped: must arrive within a stop for a crew that works a great pool | The lens. | |
| Four triggers: base roll, provocation, accumulated pressure, deliberate summon | deep-and-mud §6d | kept; the summon moved (cleanse next version → 0.2.0) | Provocation and pressure are built and fit a greedy crew. | All four in 0.1.0: the summon is unbuilt. |
| No protection for an early colony | deep-and-mud §6i | kept | His card. The ship is the way out. | |
| Legibility instead: pool size, the silence, corvath, the town's pool list | deep-and-mud §6i | kept, reshaped: size, silence and a new reach overlay in 0.1.0; corvath and the list in 0.2.0 | The overlay (from the cleanse) teaches before the first grab. | |
| Reach scales with the pool | deep-and-mud §3 | kept | | |
| Mud only kills near water; mud and water one mechanic | deep-and-mud §3 | moved (cleanse next version → 0.2.0) | Unbuilt. | |
| Three-state ground: silt, sink-mud, mirror | deep-and-mud §3 | moved with it | | |
| Stick chance scales with weight; *"the floor is the wall"* | deep-and-mud §3, §6h | moved with it; *"do not weaken the weight-scaling"* is kept as written | Under the lens it is what the biome does to troopers. | 0.1.0: adds an unbuilt state machine to the first version. |
| Radioactive suppression; campaign salvage only; free tier from Uranium | deep-and-mud §2b, §6f | moved (cleanse next version → 0.1.0, by the second reader), `NEEDS HIM` 1 | His ladder of 2026-09-23 names it, his answer of 2026-11-10 names it again and the validated water bar says "treatment"; his words outrank the cleanse. The first read left it at 0.2.0. | 0.2.0: the cleanse's smaller first version; his to say. |
| Seep-oil and the Greentide sealant are not the suppressant | deep-and-mud §6f | kept as a ban | | |
| The tank teaches, produces, and can get out | deep-and-mud §6j | kept in "later" | A colony's industry. | 0.2.0: then a crew carries a live tank aboard, which is a good joke and a large test surface. |
| The tank is a prison; the escapee is tough, makes for water, establishes, matures | deep-and-mud §6m | kept in "later" | Stage 3 takes days to weeks by his November answer. | |
| Several days to maturity; only poison at that pool intervenes | owner answers | kept in "later" with the tank | | |
| "More generic creatures" in tanks, plural reading left open | deep-and-mud §1a | lost (still open, not this design's) | Do not invent a second species. | |
| The ransom of its young: world-held young embolden the pools; a returned young earns one great gift; Sporefall's display tank | bedazzle review §3, §8 (his card) | kept, reshaped, moved: release-and-gift at 0.2.0; world tally and the Sporefall bargain later | The gift suits a ship that arrives with cargo. The tally is a planet-wide system. | All later: loses the best reason to come *back* to the Fever Wood. |
| Varruth's Catalogue (a salvage house feeding debtors to the pools) | bedazzle review §5 | lost (not chosen 2026-10-02) | | A quest for a later campaign pass. |
| The Lost Crawler | bedazzle review §3 | lost (not chosen) | See "the ones I would look at". | Reopen it: a long-stay story; cost L. |
| The Wildsteam Drum (calls the whole animal once) | bedazzle review §3 | lost (held off the card; spends the plot reserve) | | |
| The whole animal rising | sheet §4, deep-and-mud §0, rising, tenant digest | kept outside the biome's versions | The campaign spends it once in the crater event. | |
| After the rising the region's pools stay savage for good | rising | kept outside the biome's versions | Campaign state. | |
| "The Tenant" as the kit's word for it | kit spec, tenant digest | lost as a name in prose | An internal label; the animal has a name. | |
| The terribly lost: big animals drink and are subtracted | sheet §4 | kept, reshaped: any non-native animal, the crew's own pets included, with a readable sign | Its dedicated creature was cut; the standing rule is that nothing vanishes without a sign. | |
| The mirror list sold by the town | sheet §8, kit spec, cleanse | moved (cleanse: recommend retiring → 0.2.0, campaign layer; changed by the second reader) | The locked Designer sheet keeps it (*"Obtainable mirror intelligence reports an independent dated snapshot"*), and a locked sheet outranks the cleanse. The first read took the cleanse's side. | Retire it: his word only. |
| Mirror-break incident | kit spec, cleanse | kept in "later" | The sentinel already carries the moment. | |

### The crown's animals and plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Thornbugs and the nectar deal; never yield under fear | sheet §4, ban 6 | kept, quoted | | |
| Fear radius: a far raid does not dry a sheltered herd | kit spec card 3 | kept, no number | | |
| Worked by Wookiees and Ewoks (the arboreal canton) | sheet §4, §8 | kept in the campaign layer only | Canon peoples. | |
| The guild of four; one rule, four refusals | deep-and-mud §6, §6g; fauna roster | kept | | |
| Vaulm seals in sap; lacquer | fauna roster | moved (cleanse next version → 0.1.0) | Built; an instant "did you see that". | Leave it out: 0.1.0's creature moments are then all the sekkulaath. |
| Drommath swells; burst for a one-time payout | fauna roster | moved (→ 0.1.0) | Same. | |
| Ollareth screams and the crown comes | fauna roster | moved (→ 0.2.0) | What comes is undefined. | |
| All four herdable; taming does not disarm them | deep-and-mud §6n | kept in "later" | Ranching is a colony's work. | |
| Refusals legible and avoidable, never random | fauna roster §7 | kept (it is the scene's control) | | |
| "Drops into the pool" as a defence | deep-and-mud §6 | lost (declined) | | |
| The guild as a perimeter decision against ant theft | fauna roster §2 | lost | The theft was cut 2026-10-23. | |
| Brathek, the grub that eats wood | fauna roster §3 | kept as an ordinary animal | | |
| Brathek's galleries advancing through a lived-in trunk | deep-and-mud §6q | kept in "later" | *"Slow and visible"* by ruling: slower than a stop. | |
| Brathek as a living excavation tool | deep-and-mud §6q | lost (unsettled then, unbuilt, a colony tool) | | |
| Kasselith (the renamed donor borer) | fauna roster rulings, roster json, names doc | kept as a roster row | Evictions are stopped. | |
| Silloch, the bark that waits | fauna roster §4 | kept, with its bounded strike | An "OMG" on a pet. | |
| Lommerel, the upside-down grazer | fauna roster §4 | lost (cut by him 2026-10-08) | | Art exists; restoring is a roster row. |
| Thavrik, the furred nest bird | fauna roster §5 | lost (cut 2026-10-08) | | Same. Note the validation walk still lists it as wired. |
| Nests worth raiding | deep-and-mud §6c | lost with the thavrik | | |
| Nemmel, the mud-shoed grazer | cast proposal | lost (cut 2026-10-08) | | |
| Gorrameth, the great placid wanderer, and its doomed-herd incident | cast proposal | lost (cut 2026-10-08); the incident with it | The most beautiful of the cut animals: *"built to look like it is about to kneel at the wrong pool"*. | Restore one row at trace rarity: a crew would likely never see it in a week, which is why it stays cut. |
| Grolth, the carrion mound | cast proposal | kept as an ordinary animal | | |
| Grolth's acid trail | cleanse | kept in "later" | Unbuilt. | |
| Chellow, tameable, *"a lamp with a bellows"* | fauna roster §5 | kept; also a take-away | | |
| Murrelith, ribbon plumes worth money; selling feathers shoots your alarm | fauna roster §5 | kept | The temptation works in a week. | |
| Skellick the thief | fauna roster §5; cleanse | moved (recommend retiring → 0.2.0) | See above. | |
| Birds must be alien, never parrots; all really fly | deep-and-mud §6c, fauna roster | kept | Standing rule on flight. | |
| The chorus is each animal's own noise added together | deep-and-mud §6k | kept, quoted | | |
| The crown is the loudest place on the planet, against the Webwork's silence | deep-and-mud §4 | kept | | |
| The crown goes quiet only for the water | deep-and-mud §4 | kept; the landing hush respects it (the water stirred) | | |
| Killing birds quiets the map; a tamed flock is a private alarm | deep-and-mud §6k | kept | Free consequences. | |
| Homeless canon fliers as injection candidates | deep-and-mud §4, fauna roster | kept in the campaign layer, unassigned | Not this design's to place. | |
| Canon and donor roster rows (urusai, gelagrub, nuna, longtail gorg, convor, whisperbird, fambaa, butterflies) | roster json, cast proposal | kept where the campaign patch puts them; not in the free design | Tier rule. | |
| Three Biomes! ports judged out of this campaign roster | bedazzle review §8 | kept | His card. | |
| Fauna names and the three renames | syllable pass, names doc, cast proposal | kept | | |
| One planet, one language; wetter and slower | deep-and-mud §6o | kept | | |
| Legibility matrices (every silhouette nameable) | fauna roster §6, flora roster §7 | kept as art direction; three lines quoted | | |
| Thulvane, the fused tower | flora roster | kept | | |
| Skethral, the tree that grows the roads | flora roster | lost (cut 2026-10-08) | | |
| Varnoth, standing in the water, *"a pier you must not walk to"* | flora roster | kept as scenery; its timber lost | Tree ruling of 2026-10-17. | |
| Plennith makes the crown's soil | flora roster | kept in "later"; the plant stays | Soil-making takes seasons. | |
| Ossagrel, the weeping cane; sap host of the guild | flora roster | kept as a harvest; the host dependency lost | The cleanse found no need for it. | |
| Cistrel, the only safe water | flora roster | moved (cleanse next version → 0.2.0) | See above. | |
| Maulith, *"a room with walls"*; concealment | flora roster | kept as a plant; concealment not promised | No scene shows it hiding anything yet. | Promise that it blocks sight: a real gain against the Empire's probe, and an engine check first. |
| Verrow gourds, the crown's fruit | flora roster | kept | | |
| Nubrith, the only light, never fungal | flora roster | kept | | |
| Halquin, the medicine | flora roster | kept | | |
| Ammeth, the roof panels | flora roster | kept as a plant; the building material lost | Tree ruling. | |
| Claithe and potter's clay | flora roster, sheet §7 | kept | | |
| Corvath, grows only where it has fed; *"a grave marker"* | flora roster | moved: placed tell at 0.2.0; appearing after a feed later | | |
| Sodderel and bog-timber | flora roster, sheet §7 | kept as scenery; the timber lost | Tree ruling. | |
| Seepril and the honest rainbow | flora roster, deep-and-mud §6s | kept | | |
| Seep-oil as fuel | sheet §3, §7 | kept, reshaped: the Fever Wood's richer fuel source; the recipe is 0.2.0 | His fuel ruling of 2026-11-18; the sheet says fuel twice. | Recipe in 0.1.0: small, and makes the first version a fuel stop. |
| Sporefall and Wildsteam traders stocking goods | kit spec | kept in the campaign layer; named as where fuel is bought | *"You can also buy it"* (his ruling). | |
| Skimmel, *"firm ground — which is the lie"* | flora roster | moved with sink-mud (→ 0.2.0) | | |
| Wanlith, the pale one | flora roster | kept | | |
| Tullick, the tuber | flora roster | kept | | |
| The ground layer is thin on purpose | flora roster §5 | kept | | |
| Dianoga's Kiss and the three canon plants | flora roster §6 | kept in the campaign layer | | |
| Giant leaf | roster json, walk | kept | | |
| Fast jungle growth | cleanse (engine) | folded into shared machinery | `ExplosiveGrowth`. | |

### Raiders, weather, the ship, the gods

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Two raiders from opposite directions who hate each other | sheet §4 | kept | | |
| The ants are a wild swarm, never a faction (hidden plumbing factions are fine) | sheet ban 2, kit spec card 1 | kept | | |
| Kurreth and skreth; the skreth as the free face of the Webwork brood | cast proposal | kept | | |
| Ants steal thornbugs alive; track the column, raid it back | sheet §4, bedazzle review §8 | lost (cut 2026-10-23) | | `git` restore is written in fluff cuts. |
| "Open the gates between them and stand back" | sheet §7b | kept, reshaped: the Empire can be one of the two | The lens. | |
| The lure: living bait, a gamble, staggered arrival | deep-and-mud §5, §6l | moved (→ 0.2.0) | | |
| No crafted decoy, ever | deep-and-mud §6l | kept as a ban | | |
| Whether the lure cares about the prey's quality | deep-and-mud §6l | kept (it does; see the second reader's rows) | Decided and built 2026-11-03. The first read said "lost (still unset)". | |
| The reactive hive dungeon | deep-and-mud §6r, cleanse, fluff cuts | kept in "later" | See above. | |
| Hive farm, guards, sealing corridors | cleanse, fluff cuts | kept in "later" with it | | |
| Hive parasite | fluff cuts | lost (cut) | | |
| Broken hives by the mirrors | deep-and-mud §6r | moved (→ 0.2.0) | | |
| No native chase predators | sheet ban 3 | kept | | |
| No fungal miracle, no flowing water, no rain, no Earth life | sheet bans 5, 7 | kept | | |
| The oil boil | bedazzle review §8 (his card) | moved (→ 0.2.0) | | |
| The closing crown (weather that shuts routes) | bedazzle review §5 | lost (held off the card) | | |
| The Mooring | bedazzle review §4 | kept, reshaped: the marsh and the lash wear the hull in 0.1.0; the snare and the torn-off section are `NEEDS HIM` 2 (changed by the second reader) | His ruling of 2026-11-18 that biomes wear the hull, *"Yes in 0.1.0"*. The mooring was offered by name on 2026-10-02 and not chosen, so its dramatic half is not revived without him. | Bring it back at 0.2.0: his word. |
| "A ship on mud lists and mires a few hull cells a day" | bedazzle review §4 | kept, quoted (0.1.0) | The source's own words for the wear. | |
| Sporefall's toll to land on a trunk-top pad, out of reach and rented | bedazzle review §4 | lost | Campaign layer, and a purpose-built pad is less Jawa than a jack and salvage. | A rented pad as a campaign service: one more reason to trade. |
| Drive the deep off first, then land safely | bedazzle review §4 | kept (hurting or severing a limb buys quiet for a ship in reach) | | |
| The berth that costs a road | bedazzle review §5 | lost (folded into the Mooring, which was not chosen) | | |
| The pressure wedge; bough-grafting | bedazzle review §4, §5 | lost (not chosen) | | |
| Rites: the Gate Between, Cutting the Stilts, the Last Customer | bedazzle review §6 | lost (*"none, move on"*) | | |
| A Fever Wood heat kind, "ambient" | bedazzle review §1, §8 | lost | One sun from geometry, 2026-10-19. | |
| Sporefall, the treetop town; herd-groves; the wood-roads as infrastructure; the war's edges | sheet §8 | kept in the campaign layer | The biome mod places no settlement. | |
| The Wildsteam prefer it here; it is their home canton and it is quiet | sheet §5 | kept in the campaign layer | Whether they fight the Empire is unsettled. | |
| Wreck field and sounder readings | cleanse, Designer sheet | moved (→ 0.2.0) | | |
| Natural placement scorer | fluff cuts | lost (cut; no worldgen) | | |
| Natives drink their own water | Designer sheet (his words 2026-11-01) | kept | | |
| Arrival letter | cleanse | kept in "later" | The landing teaches. | |
| Mod Settings per feature | cleanse, walk | kept | Standing rule. | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature: shore temptation, rescue, remembered consequences | cleanse definition, owner_pages | kept as the core of 0.1.0; reframed for a visiting crew | It was the right centre, stated for a home. | |
| The cleanse's rescue rules (carrying is rescue; touching is not; reload keeps the clock; victims do not reset each other) | cleanse definition | kept (the scene's controls) | | |
| "Show water reach" overlay | cleanse definition | kept | | |
| Forty-colonist holding, season's turn, day one hundred | cleanse definition | lost | Colony-scale stories. The crew is five to seven. | Keep as a later-version check. |
| Four offline models (situations, geometry, timing, season) | cleanse models | kept, reshaped: the first three still serve; the season model is later | | |
| Forty-seven tickets, mostly switch-offs | cleanse tickets | kept as they stand, except those whose feature moved (listed under scope moves) | This design files nothing. | |
| Twenty-three old bars and eight new ones | Designer sheet, cleanse bars | kept as history; the ten promises in the design are the proposal to re-argue from | | |
| The judge's six coverage gaps | coverage verdict | kept as lessons: each promise in the design names its scene and its control | | |
| Stage argument, plan, journal | log, plan, journal | kept as history | | |
| The must-be-true list | walk | kept | It describes the build. | |

### Rows added by the second reader, 2026-11-18

More source names: *freeze rulings* and *freeze review* = `biomes/_freeze_rulings_2026-09-07.md` and
`_freeze_review_2026-09-07.md`; *grammar* = `biomes/README_BIOME_GRAMMAR.md`; *shields ruling* =
`design/Jawa/proposals/ship_shields_deep_design.md` and `src/RimUtinni/ShipShields/Source/ShieldHazardUtility.cs`;
*mechanics review* = `design/RimMandrake/special_mechanics_review_2026-10-22.md`; *census* = `cleanse/census.json`;
*tickets* = `cleanse/tickets.md`; *ambiguities* = `cleanse/ambiguities.md`; an *item* is a file of that name under
`infrastructure/state/items/` or `items/closed/`.

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The fever itself: *"the fever is fungal — the wood's own spore load, which is also what Sporefall is named for and what the Wildsteam harvest there. The hazard and the resource are the same thing, so living there is a bargain rather than an accident."* | freeze rulings R15 (owner, 2026-09-07); roster json notes | lost from every later source; now `NEEDS HIM` 3 in the design | The ruling was never written into the sheet, whose ban 5 forbids a fungal miracle, and no sitting after it mentions a disease. The first read did not find it. | Yes: a crew-scale sickness within days and a Wildsteam trade good; one new disease, and three fungal registers (here, the Miasma, the Rot) to keep apart. |
| The fever was undefined at the freeze: the first round's "stagnation-fever" *"was lost in the crown revision"* | freeze review 33 | lost (the question R15 answered) | History of the row above. | |
| Spores on a ship: *"spores aren't magical, just particulates"*; the light screen *"handle[s] wind, ash, vapor, bio contamination, spores, smoke, sand, and rain damage completely as well as repels small animals"* | shields ruling (owner, 2026-09-02) | kept as the answer that already exists if the fever comes back | It is the only place his shield rulings touch this biome's air. | |
| The built hull frame's heat case starts at 58 °C or a heat wave; the Fever Wood tops out at 51.5 °C | shields ruling; sheet §0 | kept, stated in the design | It shows the frame sees nothing here today, so both hull wears are new kinds. | |
| *"It is not an unknown mystery, but a mystery still for most of the game."* | kit spec F1 (owner, 2026-10-10, story card 19); item SEKKULAATH_RISING_DESIGN_CRATER_EVENT | kept, quoted | His own line for how much the player knows. | |
| *"Below: the black mirrors, unrippled. Nothing goes in the water here. Everything remembers why."* and the rule *"never explained to newcomers because the pools explain it themselves"* | sheet §1, §7b | kept, quoted (carried in by the second reader) | The best two sentences in the sheet were not in the design. | |
| *"a brief moment of giant stillness, giant tree parasites sharing the space with the other races in ambivalent harmony"* | sheet §1 (owner) | kept in the campaign layer | The other races are Wookiees, Ewoks and the Wildsteam. The harmony among the crown's animals is kept. | |
| *"nothing here is at war with the trees, because the trees are the only reason anything is dry"* | sheet §4 | kept as lore | Nothing in play contradicts it. | |
| *"The stillness is real — and it is enforced"* | sheet §3 | kept, reshaped: the landing hush says it | | |
| Where it sits: the freshwater back half of the delta wetland, groundwater *"inches down"*, *"water table × the trees that tamed it"* | sheet §2 | lost from this design | World geography; the planet is painted once at the end. | A world document keeps it for free. |
| "An aquatic equivalent of a sarlacc"; the sarlacc spec as the family register for the art | sheet §4; kit spec F4 | kept outside the biome's versions | It governs the whole animal's art, which the campaign owns. | |
| *"Nothing native drinks at them"* | sheet §5; roster json | lost (superseded by him, 2026-11-01: *"natives should drink their own environmental water"*) | His later word wins. | |
| No fish, ever: *"their emptiness is the biome's central evidence"* | roster json fish ruling; review §1 | kept | A black pool with nothing in it is the picture. | |
| You do not bridge the mirrors | kit spec F5; cleanse definition | kept | Built: pool water takes no foundation. | |
| Heavy building needs real crown support or finished stilts; a blueprint or a half-built platform holds nothing | cleanse definition; ambiguities | kept | It matters to stilt footings under a hull too. | |
| Boughways carry platforms, not bunkers | kit spec F6 | kept as a build fact | | |
| The ground causeway under the roads: *"the free, wet, watched alternative"*, inside reach, *"the price IS the mechanic"* | sheet §7; kit spec F6 | kept | It is the firm landing ground the hull section names. | |
| *"The ground is for the brave and the poor"*, *"always within arm's reach of a mirror"* | sheet §7b; grammar | kept, reshaped: the crew are both | | |
| *"hauled up from the mirrors' edges by people with excellent nerves"* | sheet §7 | kept, quoted (carried in) | | |
| Chitin and salvage: *"the two-front war's leavings: stand back, let them, mop up"* | sheet §7 | moved (not in the cleanse → 0.2.0, with the lure) | The most Jawa line in the sheet had no row: the crew's reward for the two fronts is picking the field. | 0.1.0 without the lure: ordinary raids leave ordinary corpses, nothing to build. |
| *"walls help less than quiet"*; reading *"which direction this month's raid comes from"*; a fixed raid side per map that watch-perches read | sheet §7b, §8; kit spec F9 | kept, reshaped: the two raiders keep opposite edges; watch-perches are campaign | | |
| Nectar-liquor; Sporefall's *"stills running nectar-liquor and seep-oil"*; the oil as *"the still-burners' second source"*; ossagrel as the stills' sugar | sheet §7, §8; flora roster | kept in the campaign layer; now cited for fuel | It is the source line for fuel being made and sold at Sporefall. | |
| Sporefall as *"the beloved second city... a jewel, not the seat"*; the Greentide holds the Wildsteam capital | freeze rulings R10 | kept in the campaign layer | | |
| Seep-oil and the Miasma's attar are sibling goods, never one item: *"scent, slick, and flame"* against *"beauty restored from silt"* | sheet §7 | kept as a ban | | |
| The pools "moved lately": a pool's agitation as the thing a map marks | sheet §8; kit spec F2, F3 | kept with the mirror list | | |
| Wild losses leave a find: *"a dropped pack saddle at the pool edge"*; *"the clean splash remains the wild rule"*; big drinkers go first | kit spec F1, F2, card 2 (2026-09-12) | kept, reshaped: the readable sign is required, the saddle is one way to give it | Standing rule that nothing vanishes without a sign. | |
| *"One story per victim"*: colonists and tame animals are dragged under on a clock, never simply deleted | kit spec card 2 (2026-09-12) | kept | The first grab. | |
| "The herd has gone dry." as an alert that can come before the raid letter | kit spec F8 | kept | Free with the calm meter. | |
| A wasted gathering trip teaches the nectar deal | kit spec F8 | kept | | |
| Wild bore-caves: pre-cut rooms, part sealed, something living in them | kit spec F7 | kept in "later" | A room to move into is a colony's find. | 0.2.0 as a place to loot: unbuilt. |
| The owner's method: *"invent our own complete roster... THEN look for Star Wars specific injection opportunistically"* | flora roster (owner, 2026-09-23) | kept | It is why the free tier is whole. | |
| Twenty-three donor animals and eleven Earth plants evicted from the donor biome, each with its reason | roster json | kept as history | Evictions are stopped; these were done before the stop. | |
| Seven donor plant rows as placeholders; the five alien fillers cut; the canon tree demoted | flora roster §6; item FEVERWOOD_FLORA_ROSTER_1 | kept | | |
| Five plants *"exist to carry a ruling, not to fill a slot"* (plennith, ossagrel, cistrel, corvath, skimmel) | item FEVERWOOD_FLORA_ROSTER_1 | kept as a warning; their mechanics are where the rows above put them | | |
| Corvath must stay worthless: *"its whole worth is as information"* | flora roster | kept | | |
| Two plants deceive on purpose (skimmel reads as safe ground, sodderel as dead): *"an art pass that 'fixes' either has broken the design"* | flora roster §7 | kept as art direction | | |
| Digging a tullick *"churns the mud around it, which is an honest small cost"* | flora roster | lost | No mud state in 0.1.0 to churn. | Comes back free with sink-mud. |
| *"Together they make the crown an ecology rather than a larder"* (fruit draws the grazer, the grazer draws the ambusher) | fauna roster §4 | kept, reshaped: the grazer was cut, so the ambusher waits for pets and small natives | | |
| The bark ambusher goes still *"sometimes for days, then strikes once and holds on"*; the ribbon curtains are where it hides; a tame one strikes only hostiles | fauna roster; cleanse definition | kept | | |
| His art rulings of 2026-10-08: the grub is *"a wood-boring larva that rasps into trees … not a drill head"*; the chellow has no beak; *"This creature is a thief."*; the borer renamed kasselith | fauna roster rulings; roster json | kept | The cast proposal's "a drill bit" brief is overruled by the first of these. | |
| Current art *"accepted as-is, with later review"* | Designer sheet floor (owner event 1792374240816575285) | kept | | |
| The murrelith ships six coats and no flight frames yet | item MURRELITH_FLIGHT_DECIDE_SIX_COATS_ONE_WING | kept as open build work | Flight is never tested live without him. | |
| The ant queen and the spider matron (*"egg-clutch sheen"*); ants *"always drawn mid-haul"* | cast proposal | kept as art direction | | |
| The ants were to come from the They! ant mod if it passed | sheet §4; roster json | lost | The kurreth was invented instead. | |
| Three names drafted for donor rows (narrith, quollith, jemmock) | names doc 5e | lost | Their rows were renamed by him or judged out. | |
| *"Too many two syllable names sound all the same."* | syllable pass (owner, 2026-09-24) | kept | The reason for the three renames. | |
| Letting the peoples who live there name things | deep-and-mud §6o | lost (declined 2026-09-23) | | |
| Three bird voices: *"swoop, shrill, and warble"* to make *"the typical 'swamp cacaphony'"* | deep-and-mud §4 (owner) | kept, quoted here | | |
| A working-crown sound under the birds (taps, herds, steps, steam) that the hush also cuts | sheet §9; review §1; item FEVERWOOD_CROWN_SOUND_HEAT_1; Designer log | kept | Built as one sustained sound; the birds' own calls are the unbuilt half. | |
| The scream is a rise in noise, never a hush: a silence would *"collide with the deep thing's exclusive tell"* | item FEVERWOOD_SAP_SUCKER_GUILD_1 | kept as a ban, with the ollareth at 0.2.0 | | |
| *"Taming buys access, never obedience"*; *"The whole guild works on consent, and fear is the universal failure mode."* | deep-and-mud §6n | kept, quoted here | The rule behind the sac that will not come off. | |
| The lure's three living baits: your own tame animal, a prisoner, a nectar-beast | deep-and-mud §6l | kept | | |
| Bait must be worth eating; the wager locks once a raid is drawn | item FEVERWOOD_TWO_FRONT_LURE_TUNING_1 (decided and built 2026-11-03, delegated) | kept | Corrects the first read's row "whether the lure cares about the prey's quality: lost (still unset)". | |
| *"you are hoping the second column shows up, which is a genuinely novel thing to want during a raid"* | deep-and-mud §5 | kept, quoted (carried in) | | |
| Summoning as *"a raid against the biome"* | deep-and-mud §6d | kept with the summon, 0.2.0 | | |
| *"the whole biome one antagonist instead of a set of hazards"* | deep-and-mud §6e | kept | | |
| The pool breathes: limbs nobody hurts sink back; a cap on standing limbs | item FEVERWOOD_LIMB_LINGER_CAP_1 | kept in 0.1.0 (added by the second reader) | Built. Without it a quiet pool fills and the crown stays silent for good. His look at the two numbers is still owed. | |
| A pawn is held by a stun, not by zeroing its movement (which downs it and wipes its jobs) | item FEVERWOOD_TENTACLE_BESTIARY_1 (measured 2026-09-23) | kept as an engine fact | It answers the open engine question in deep-and-mud §3. | |
| The eye's built form is a lone bloom on a small roll; the "many limbs and the eye" event as its own thing | item FEVERWOOD_TENTACLE_SETPIECE_TUNING_1; ambiguities | kept, reshaped: all limbs of the big one stay in the one great pool | | |
| Whether quieting a pool with the charge also stops its gifts | deep-and-mud §6f | kept: quiet stops gifts too | The cleanse settled it; no risk-free farming. | |
| The campaign's charge is made from irradiated wreck salvage | plan (a Designer choice, 2026-11-16) | kept in the campaign layer | Scavenged poison for a scavenger crew. | |
| The young can be tamed only where there are no pools: *"If there are still pools, it plops down into them and installs itself as a new tentacled horror (small one), so it's no longer trainable. But if it gets out on a map without such pools, it will escape and simply wander wild."* | item FEVERWOOD_DIANOGA_PRISON_1 (owner, 2026-09-23) | kept in "later", now written into the design | A colony here can never do it; a ship that carries the tank away can. The first read had no row. | 0.2.0: it makes the tank cargo; needs the tank and the taming numbers he has not given. |
| *"It remembers the tank..."*: a grudge, not a difficulty number | item FEVERWOOD_DIANOGA_PRISON_1; item FEVERWOOD_DIANOGA_TANK_TUNING_1 | kept in "later", quoted | Only a marker is built; what the grudge does is his to say. | |
| The tank as *"a high-prize item with many uses"* and the model for other prisons for living ingredients | item FEVERWOOD_DIANOGA_PRISON_1 (owner note, 2026-09-23) | folded into shared machinery | A generic capture pod is built. | |
| Build the prison away from the pools; an escape is *"a bad afternoon, not a colony-ender"*; never write it as husbandry | deep-and-mud §6j, §6m | kept in "later" with the tank | | |
| The dianoga replaces the sekkulaath when the Star Wars tier is present, never beside it; its colour is purple | item FEVERWOOD_DIANOGA_PRISON_1 (owner, 2026-09-23) | kept in the campaign layer | | |
| *"It's a mistake to have dianoga in the GreenTime. It belongs only in tank prisons and the Fever Wood."* | item FEVERWOOD_DIANOGA_PRISON_1 (owner, 2026-09-23) | kept | | |
| His wish for *"tentacle pulling capabilities like the lasso power"* in the Miasma | item FEVERWOOD_DIANOGA_PRISON_1 | kept, reshaped: the snare here delivers it | | |
| Canon tank precedent (a display-tank juvenile; refinery tanks) and the product line's home in the cuisine mod | deep-and-mud §6j | kept in the campaign layer | | |
| What the great gift is: a ship chunk, a sealed ancient crate, an archite capsule, a persona core or a gravcore | review §3; item FEVERWOOD_BROOD_RANSOM_1 | kept, now named in the design | A gravcore from the bottom is a ship reason to come back. | |
| The young cask as a trade good; *"the Narrator says what the deep thinks of traders in its children"*; "the pools have been restless since…" | item FEVERWOOD_BROOD_RANSOM_1 | kept with the ransom at 0.2.0; the world tally later | | |
| Sporefall's biggest young: a doubled gift, and the town's peace broken | item FEVERWOOD_BROOD_RANSOM_1 | kept in the campaign layer, later | | |
| *"Their hives should be dungeons in their own right (procedural are fine, not plot based) with all sorts of gross insect symbiotic relationships in there."* | item FEVERWOOD_ANT_HIVE_DUNGEON_1 (owner, 2026-09-22) | kept in "later", quoted here | | |
| *"You decide how deep to go, and then you decide too late."* | item FEVERWOOD_ANT_HIVE_DUNGEON_1 | kept, quoted (carried in) | | |
| The hive parasite as an ally: *"whatever eats ants is not your enemy"*; its creature, the glomvar | item FEVERWOOD_HIVE_PARASITE_CHAMBER_1; census | lost (cut 2026-10-23); the animal ships dormant with its art | | |
| The hive guard, the bostrach | census; tickets | kept in "later" with the hive | | |
| The corridor sealed behind you, *"so retreat costs a dig"* | item FEVERWOOD_HIVE_SEALED_PASSAGES_1 | kept in "later" with the hive | | |
| Dead hives by the water are the exception, never the norm | deep-and-mud §6r | kept with the broken hives | | |
| The oil haze lies on the ground only; a blow never lights it; a letter names the spark; it starts only on the hottest days | item FEVERWOOD_OIL_BOIL_WEATHER_1 | kept with the oil boil | | |
| *"A harvest window you work in silence and without guns."* | review §4 | kept, quoted (carried in) | | |
| The Fever Wood's sky: clear, fog, overcast and dry thunder, all vanilla; no rain | review §2; ambiguities | kept | Dry lightning is one of the oil boil's sparks. | |
| The gravship as *"the heaviest, loudest thing that ever came to the Fever Wood"* | review §4 | kept, quoted (carried in) | | |
| A steel saddle across two trunks as a dear landing berth; *"a stump and an abandoned toll sign remain"* | review §5 | lost; named in `NEEDS HIM` 2 | Not chosen 2026-10-02. | |
| Rites found on the map: a gate-pin scratched *"we were not here"*, a knot-sign meaning *"gone on"* | review §6 | lost with the rites | *"none, move on"*. | |
| The nine-mark scorecard: no ship touch, no sky of its own, no god, *"nothing learned here travels"* | review §2 | kept as history | The ship and sky marks are now filled by hull wear and the oil boil. | |
| The pressure wedge as *"open the vault, keep the loot"* | review §5 | lost (not chosen 2026-10-02) | A row existed; this adds the line. It is the most Jawa tool anyone pitched here. | His to reopen. |
| Canon lines in the free limbs' text; ten campaign-prefixed defs in the free mod; ancient dangers refused; the art for the cask, the display tank and the haze | review §1, §8; item FEVERWOOD_DIANOGA_GIANT_MAP_1 | kept as build facts | | |
| The whole animal's rising: *"appears rageful and dangerous, harms local Wildsteam sites, makes certain world sites no longer accessible"*; reach *"Its region only, permanently"* | kit spec F4 (owner, 2026-10-10 and card 2026-10-12) | kept outside the biome's versions | A row existed; this adds his words. | |
| Campaign text for the thing: *"The clan does not name the thing. Traders who do, name it differently each time"*; *"Somewhere under the Fever Wood, something counts one more"* | tenant digest (read by search) | kept in the campaign layer | | |
| The colony root: *"Make a home on the branches, whose routes shape daily work and travel, above black water that remembers what you do and sometimes reaches up to change your plans."*; two bars validated 2026-11-16 | Designer sheet; plan; walk | kept, not edited; named in the design's status header | A locked tree for a colony that stays is a later Designer run's to reconcile. | |
| Seven showcases, forty-five scenes, seven filed build items | plan | kept as history | | |
| Next-version switches, and what switching the water off does to someone already seized | tickets; cleanse definition | kept | | |
| Growth-top extras read out of the growth engine's comments (a nectar glut, a reroute) | tickets T_MOVING | lost | Nobody ruled them. | |
| A natural-placement scorer and an anima tree | mechanics review 17; cleanse definition | lost | No worldgen; not restored. | |

## Sources read, and the count

*(The paragraph below is the first read's count. The recount after the second read is at the top of this page.)*

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**28 source files, 167 rows**, of which **30 lost**, **19 moved**, **17 kept, reshaped** and 1 folded into shared
machinery (recounted after the revision of 2026-11-18, which added five rows and changed one). Every one of the 28 files is named in at least one row's source column (checked by the same script).
Three further rows keep a plant and lose only its timber; they are counted as kept.

Read whole: the sheet; deep-and-mud; both rosters; the cast proposal; the Designer sheet and journal; the cleanse's
owner pages, definition and next-version list; the owner answers. Read in part (the sections named in the rows):
the bedazzle review; the syllable pass; the validation walk's must-be-true list; the rising note. Read by heading,
or parsed: the kit spec; the roster json; the names doc (Fever Wood lines); plan; log; the cleanse's ambiguities,
tickets, models and census; the coverage verdict; the tenant digest; fluff cuts and the experiences table (Fever
Wood lines). Not read: `record.json`, `tree.json`, `scenes.json`, `exam.json` and the exam run folders (pipeline
records of the older design; they hold no idea the sheet does not), and the Designer-codex notes and questions
beyond their headings.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_fever_wood.md`, `fever_wood_deep_and_mud_2026-09-23.md`,
`fever_wood_fauna_roster_2026-09-23.md`, `fever_wood_flora_roster_2026-09-23.md`,
`fever_wood_rm_cast_proposal_2026-09-24.md`, `fever_wood_syllable_variety_pass_2026-09-24.md`,
`feverwood_bedazzle_review_2026-10-02.md`, `kits/fever_wood_kit_spec.md`, `rosters/the_fever_wood.json`.

Not for deletion: the shared names doc (other biomes use it); `design/concepts/FeverWood/` (pipeline records; the
`cleanse/` proposal there is superseded by this design and should be re-run from it, not applied); the validation
walk (it describes the build); the campaign's tenant digest and rising note.

Before deleting: `the_fever_wood.md` is cited by path from `src/` comments and from the Designer sheet's pruning
lines; `CAMPAIGN_ARC_GATHER.md` cites deep-and-mud. Those references need repointing in the same change.
