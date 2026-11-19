# The Rot: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A different agent from the one that wrote this page and the design read the sources again, starting with the ones
the first pass read by heading or not at all, and checked each idea in them against the rows below.

**Rows added: 93**, in the table "Added by the second reader" at the end of "Every idea, row by row". Two of the
first pass's rows were corrected in place and say so (blastpod to chemfuel; the portable mat).

**The three most valuable things the first read missed.**

1. **The Rot's named fuel cannot grow on the Rot.** The first design made wild blastpods the biome's richer fuel
   source and moved them into 0.1.0. The built plant has a growth floor of 50 °C (measured in its def); the sheet
   gives the Rot a maximum of +24 °C. The roster file said so on 2026-09-09 (*"it can only live in hot caves"*),
   purged the donor plant for it, and records with his ruling of 2026-09-20 on its stand-in: *"I don't want new
   versions of these silly plants."* The first read took that file's keys and counts only. The fuel answer is now
   the emergency route, the blastpod is back in the cleanse's bucket, the finding is filed
   (`RIMMANDRAKE_DECIDE_ROT_BLASTPOD_GROWS_ONLY_ABOVE_FIFTY_DEGREES`), and it is asked (`NEEDS HIM` 3).
2. **A ship's crew already wrote down what this place does to a ship.** The dead ship's log is eight written
   entries in a built def, and the first read kept "the log" without opening it. *"Engineer took the drive coil
   out to clean the spores off it. Left it on the mat for one hour. One hour."* *"It ate the cargo netting, the
   tarps, the galley."* *"Cover what you keep."* That is the hull section's source. His shield rulings of
   2026-09-02 give the answer (he cut a special spore shield, *"spores aren't magical, just particulates"*, and
   gave spores to the light screen), and the frame is built; it cannot see Sheen yet. The log's last entry leads
   to the living mat root, which he ruled a ship part on 2026-10-22 and the first read left in "later". It is in
   0.2.0 with the log now.
3. **The crew can dig up the floor and sell it.** The fungal-soil trade is built in the campaign tier: *"Dig fungal
   soil, sell it to moisture farms by ship; digging sends distress through the fungus and brings its creatures."*
   No row. For a crew that must buy its fuel, it is the Rot's answer to what they pay with.

Close behind: the kit's opening, *"You land warm. That is the first wrong thing"*; the Unjoining rite, written
around the launch (*"We cut it out of her and stayed anyway"*); a hook pitched with the giant and never ruled on,
*"Imperial salvage crews have started following it too"*; the yssomar, the giant he did not choose, whose scars
*"are not its own"*; and a flag the roster raised and nobody closed: every kept fungus had a growth floor of 0 °C
on a biome whose median is −18.8 °C.

**What changed in the design, and why.**

- *Fuel:* rewritten. No richer source is claimed. "Where fuel is bought" now says what the crew has to sell.
- *Hull:* rewritten onto the built shield frame: the Sheen as fouling the light screen stops (ruled; the frame
  build is named), loose things on the mat, stores, the cold room, and the frame's cold wear with its doubt. The
  false sentence that no hull system exists is deleted. Nothing in the section is the second reader's invention.
- *The ship ideas he passed over* are both under `NEEDS HIM` 1 now, with dates and his words: the sheened hull
  (with the consult's harder version) and the launch siege. The first read asked about one. Neither is revived.
- *Scope:* blastpod fuel moved from 0.1.0 back to 0.2.0 (asked). The last camp and the living mat root moved from
  "later" to 0.2.0. Named in 0.2.0: the fungal-soil trade (campaign layer), the mollugh (a proposal, never
  admitted). The dropped list gains the two giants and two ideas that were offered and not chosen.
- *Promises:* the blastpod promise is removed; two added (Sheen fouling with its screened control; a ship part on
  open mat is eaten like anything else).
- *Lines carried in:* six from the dead ship's log, two from the kit, three from the sheet, his card-5 reason.
- *Whose word wins:* each cleanse line was checked against his dated words. His mark of 2026-11-17 (the pleasure
  brew) is kept. The first read's largest reversal of the rows he let stand (the giant into 0.1.0) is unchanged
  and still asked (`NEEDS HIM` 2); the second reader undid one of its reversals (blastpod) on evidence. One
  delegated list fell to his word: the 2026-11-11 pass that struck the mat root from the ship gifts. No locked
  Designer sheet or tree exists for this biome, so nothing is held for a Designer run to reconcile.

**Measured counts** (script: `design/RimMandrake/biome_recheck_row_check_2026-11-18.py`, and the reader's own
source list): **218 rows** (125 from the first read, 93 added); **35 lost**, **24 moved** and 6 more that record a move in part, 1 kept and reshaped, 1 folded into shared machinery, 154 kept, 3 the script could not class (first-read rows that begin "pleasure cup kept", "ping moved" and "weapon and helmet moved"). **Sources: 28 read to the end,
12 read in part, 30 not opened.** Read to the end: four of the six files this page lists for deletion (the sheet,
the review, the redo, the cast proposal); the mat spec; the open questions; his answers and his marks; nineteen
ledger items of this biome (the giant, the swallow, the navigator and its two splits, the vat, the draught, the
rite, the kin table, the wound wiring and its fix, the allergy port, the tier leaks, the sitting, the marks fold
and four small ones); and the ship-gifts item. Read in part: the other two files listed for deletion, the roster
file (every section and every row; the sixty-three eviction reasons cut at about 150 characters) and the bars
draft (every bar; a few long lines cut at 900 characters); the rehearsal's notes (every paragraph, each cut at
1,300 characters) and questions (titles); the kit (the player-experience section and the six cards); the log def
(the eight entries and both quest texts); the mechanics review (the Rot table, each row cut at about 500
characters); the watcher pitch (the Rot row); the shield design and two of the frame's source files; the Sheen
weather def and the blastpod's def (the fields cited). Not opened by this reader: `rot_flora_fauna_names.md` and
`rot_regen_briefs.json` (both on this page's hold list); the rehearsal's `record.json`, brief and the questions he
was shown; the cleanse folder apart from his marks and a search for the blastpod (eight files; the first read read
its definition, owner pages and next-version list); the walk and the experiences table (the first read read the
parts that bear on this biome); the Fungal Forest merge plan; the rites register; and thirteen closed items of art,
naming and build-log work (among them `THEROT_RM_MOD_BUILD_1`, `ROT_FLORA_FAUNA_VERDICTS_1` and
`ROT_RM_CAST_MIGRATION_1`). Every file not read to the end is one that stays, except the roster file and the bars
draft as stated.

DELETE-READY: yes

That line covers the six files listed at the end of this page and nothing else. What the first read says to do
before deleting still stands. Two more: the roster file is the only place the sixty-three evictions and their
reasons are written, and its note on the fungi's growth floor is an open flag this page now carries; the eight
log entries live in `src/RimMandrake/TheRot/Defs/Misc/RM_NavigatorLog.xml`, which is source and is not on any
delete list.

Companion to `design/concepts/TheRot/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the
overriding priority"*.

The Rot is the biome where this pass disagrees most with the cleanse proposal of 2026-11-17, and where that matters
most, because the owner had read that proposal and marked it. The cleanse chose a quiet signature (the floor warms
you, the open ground spoils your food, the harvest heats your freezer) and switched off forty-six other things. He
changed one cell (the pleasure brew, back to 0.1.0) and let the rest stand. That was the day before he stated the
lens. Among the things switched off were the giant he himself chose and described on 2026-10-02, the ship it
swallowed, the sound of a person knocking from inside it, and the vat that gets implants back from the dead, which
the pitch he approved called *"the most Jawa idea of the lot."* Read through the lens, those are the Rot. So this
design keeps the cleanse's metabolism as the ground everything stands on and brings the giant's eating, swallowing,
rescue, castings and ping into 0.1.0, with the rest of the creature and grove encounters at 0.2.0. Because that
reverses rows he let stand, it is the second question under `NEEDS HIM`, and every move is listed below so each can
be put back.

His four rulings of 2026-11-18 (3:10 PM PST) are applied, not asked: the stop length as an outer edge (about six
weeks); cover from orbit (canopy and fog, one step); fuel (a richer source, named: wild blastpods, by his ruling of
2026-09-06); and the wear on the hull from the sources (the Rot spares metal; it wears on stores, on the cold room,
and later on the crew). (Second reader: the fuel and hull answers changed; see the top of this page.)

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The portable living mat.** His ruling of 2026-10-22: *"Can be installed on the gravship to help with heating in
   cold places as a reward. Needs food. Would grow in other biomes if tended with food."* And of the mat itself on
   2026-09-17: *"Very Star Wars."* It is a ship part, won at the end of the dead ship's log, built. I left it in
   "later" because it pays on other landings and needs feeding and budding proved off the Rot. It is the reward
   most plainly made for a ship and the one I was least sure about holding back.
2. **The sheened hull.** *"The biome marks the ship by using it to travel."* Turned down with two other ideas on
   2026-10-02. It is the only idea in the Rot's sources about what the Sheen does to the ship, and the Sheen is, by
   the sheet, *"a reproductive sleet flung outward to colonize."* Lost; asked as `NEEDS HIM`.
3. **The Rot will not let them go.** A launch siege: *"the warm mat grows up over the landing struts and holds the
   ship down for a few hours. Every hybrid on the map that shares wounds turns toward the hull."* Pitched 2026-10-02
   and not chosen. It answers his lens question about what happens when the ship tries to leave, and it is the
   strongest image in the file. Lost.
4. **The Unjoining.** The rite he chose: *"a colonist who let the jungle into their body is purged until the
   symbiont dies, just before the clan leaves."* It is a leaving ritual for a ship's crew, written before the lens.
   Rites are a second version by his ruling of 2026-10-23, so the rite is "later" and only its draught is 0.2.0.
5. **The teas.** *"Biosculpting in a cup, EARNED... Getting a tea is an expedition, not a harvest."* Five years of
   age given back, once a year, behind armed mushrooms. For a ship this is the reason to come: *"You want some of
   this, you come to the biome and prepare it in your vessel, right now."* Only the pleasure cup is 0.1.0, by his
   mark; the two great cups and their groves are 0.2.0.
6. **Shared wounds.** *"Your herd bleeds as one."* The cleanse's runner-up signature; 0.2.0 here. If he reads
   0.1.0 and finds the animals ordinary, this is the row to move.
7. **The joined ear.** A colonist carrying a symbiont hears the forest from inside, *"and a sharp wrong note
   wherever something is hiding."* Not chosen. Lost, and lovely.
8. **"The dayside is the planet's leaf, the stormwall is its throat, and The Rot is its gut."** World lore, kept in
   one clause. The fuller chain (the fallout, the Hadley cell) is lost from a design about a stop.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17, which he marked. Revert
by moving the line in the design's Scope section.

- **Hwelgrue open-ground grazing and first-sighting letter:** next version → 0.1.0.
- **Hwelgrue castings (metal returned whole):** next version → 0.1.0.
- **Swallowing and rescue:** next version → 0.1.0. His answer of 2026-11-10 is about exactly this rescue.
- **Knocking and the core's ping:** next version → 0.1.0.
- **Wild blastpod sac and chemfuel:** next version → 0.2.0 (the first read had 0.1.0; moved back by the second
  reader, and asked: the built plant cannot grow at the Rot's temperatures).
- **The log's last camp and the living mat root:** next version → 0.2.0 (the first read had "later"; moved by the
  second reader on his ruling of 2026-10-22).
- **Drive core: uniqueness, damage, range:** next version → 0.2.0.
- **Navigator log and salvage sites:** next version → 0.2.0.
- **Sheen exposure ladder; chitin helmet:** next version → 0.2.0.
- **Kin wounds; kin mending; chittik implantation:** next version → 0.2.0.
- **Guardian gas, alarm, false fruit, crown ring; brewing vessel; ageless and regenerant cups:** next version →
  0.2.0.
- **Three symbionts; unjoining draught:** next version → 0.2.0.
- **Gut-mother: analysis, recovery, starters:** next version → 0.2.0.
- **Thrown spore weapon; ambrosyx:** next version → 0.2.0.
- **Stayed "later" from the cleanse's "next version":** pale tree; grown
  furnace; furnace-blood and the heat gene; gourmet line; Slime exports; treasure conscience; industrial medicine;
  regional spore cloud; outdoor compost; ritual groves and set pieces; the giant's warm trail; local genepacks; the
  wayward Prime. Not moves.
- **Kept as the cleanse recommended (retire):** spore allergy, the giant's rot aura, mould mood, fungiponics, spider
  trophy, air collector, world scoring and mutator chances.
- **Kept as he marked:** the pleasure brew, 0.1.0.
- **A colony of forty and the whole-map season:** first version → later.
- **New, not in any source:** the Jawa feeding the giant their rusty scrap on purpose (a reading of the built
  casting rule: items come back at full condition); the Empire's fallen and their gear going through the same gut;
  the cold room as the part of the ship this biome wears on; canopy and fog as the Rot's cover from orbit.

## Every idea, row by row

Source names: *sheet* = `biomes/the_rot.md`; *review* = `biomes/rot_bedazzle_review_2026-10-02.md`; *redo* =
`biomes/rot_new_marks_redo_2026-10-02.md`; *cast proposal* = `biomes/rot_rm_cast_proposal_2026-09-24.md`; *names
doc* = `biomes/rot_flora_fauna_names.md`; *kit* = `biomes/kits/rot_kit_spec.md`; *roster json* =
`biomes/rosters/the_rot.json` (all under `design/Jawa/worldbuilding/`); *mat spec* =
`design/RimMandrake/rot_warm_mat_portable_2026-10-22.md`; *open questions* =
`design/RimMandrake/rot_open_questions_2026-10-22.md`; *bars draft* =
`design/RimMandrake/rot_northstar_bars_draft_2026-10-22.md`; *cleanse* = `design/concepts/TheRot/cleanse/`; *marks*
= `design/concepts/TheRot/cleanse/owner_marks.md`; *walk* = `design/validation_walks/RimMandrake/TheRot.md`; *owner
answers* = `design/RimMandrake/designer_codex_2026-11-09/TheRot/ANSWERS_OWNER.md`; *experiences* =
`design/RimMandrake/biome_experiences_2026-10-20.md`. Added by the second reader: *log def* =
`src/RimMandrake/TheRot/Defs/Misc/RM_NavigatorLog.xml`; *shield rulings* =
`design/Jawa/proposals/ship_shields_deep_design.md` and `src/RimUtinni/ShipShields/`; *ship gifts* =
`infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`; *blastpod def* =
`src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml`; *build items* = the closed items
`ROT_HWELGRUE_GIANT_BUILD_1`, `ROT_STILL_ALIVE_SWALLOW_1`, `ROT_SWALLOWED_NAVIGATOR_1`, `ROT_GUT_MOTHER_VAT_1` and
`ROT_UNJOINING_DRAUGHT_1` in `infrastructure/state/items/closed/`; *rite item* =
`infrastructure/state/items/ROT_UNJOINING_RITE_1.md`; *kin table* =
`infrastructure/state/items/closed/ROT_HEALTH_SHARING_1.md`; *watcher pitch* =
`design/RimMandrake/watcher_creatures_pitch.md`; *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *rehearsal* = `NOTES.md` and `QUESTIONS.md` in
`design/RimMandrake/designer_codex_2026-11-09/TheRot/`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "A pale fungal continent on the night shoulder of the stormwall..." | sheet §1 | kept, quoted entire | | |
| "Nothing here is a plant. Nothing here is quite an animal... still alive." | sheet §1 | kept, quoted | | |
| The planet's gut: leaf, throat, gut | sheet header, §2 | kept in one clause; flagged above | | |
| "A pale forest with a heartbeat of rot" | sheet header, §9 | kept as art direction | | |
| Measured tiles, regions, temperatures; the cold tail repainted to ice | sheet §0 | lost | The planet is painted at the end. | |
| The nightside's lush: "a thick pale sprawl" | sheet §2 | kept ("dense beyond anything dayside", quoted for cover) | | |
| Bioweapon-adjacent and disarmed: "Nature won here" | sheet §3 | kept, quoted | | |
| Genepacks carry only locally useful genes; the gene reactor is the Slime's | sheet §3, §6 | kept as a rule; local genepacks later | | |
| Thermogenesis: the mat is a heated floor; Frostcaps is where the heat fails | sheet §3 | kept | | |
| Warm mat free forever inside the Rot; "it just helps a lot" | kit, owner card 3; mat spec | kept, quoted | | |
| The Sheen: emitted, not received; "the biome's border is enforced by its own breath" | sheet §3 | kept as weather in 0.1.0; the border by breath moved (→ 0.2.0), quoted | | |
| The milk: ponds and streams of not-water | sheet §3 | kept | | |
| The rot clock: raw meat gone within a day | sheet §3, §5 | kept, quoted | | |
| Only walled and roofed rooms are exempt; a lean-to will not save your meat | kit, owner card 2 | kept | | |
| Digestion pauses for frozen stock | cleanse owner_pages | kept as the default; the cleanse's question to him stands | | Frozen meat digested too: the sheet's "for certain", and a harsher larder. |
| All-fungus flora; no conventional plants | sheet §4, §6 | kept | | |
| The Agarilux Prime, "celebrated"; it feeds on what it kills | sheet §4 | kept, quoted | | |
| A generic defender-plant pattern for the planet | sheet §4 | folded into shared machinery | | |
| Hybrid-or-out fauna | sheet §4, §6 | kept | | |
| Health-sharing in two variants; works on tame creatures | sheet §4; kit M7 | moved (cleanse next version → 0.2.0) | | |
| Guardianship as a law of potency; no undefended prizes | sheet §4, §6 | kept (the cup's spores in 0.1.0; the groves 0.2.0) | | |
| Sheen-fall, spore events, no water rain | sheet §4b | kept | | |
| Always true: "what you harvest is still alive"; it will wreck a freezer not overbuilt | sheet §5 | kept, quoted | | |
| Live preparations cannot be stored: "you come to the biome and prepare it in your vessel, right now" | sheet §5, §6 | kept, quoted | | |
| All useful light is biological | sheet §5 | kept, quoted | | |
| The nine hard bans | sheet §6 | kept as rules | | |
| Instant composting as a service | sheet §7 | kept as a consequence | | |
| Wildsteam sacred groves; pilgrim paths | sheet §8 | kept in the campaign layer, quoted | | |
| Brewing stations kept by whoever came last | sheet §8 | kept in "later" (set pieces) | | |
| Digestion sites, "quietly warm" | sheet §8 | kept in "later", quoted | | |
| Guardian thickets as marked danger and marked treasure | sheet §8 | moved (→ 0.2.0) | | |
| Light, palette, silhouettes; "the longer you stay, the more you shine" | sheet §9 | kept as art direction; the last quoted | | |
| Sound: insect hum, wet settling, the hiss of the fall | sheet §9 | kept as art direction | | |
| Experience line: "A cathedral of mushrooms in the dark, generous and hungry. The Rot shares everything, including you." | experiences; walk | kept, quoted | His card of 2026-10-20. | |
| His answers: comfort and danger from the same life; quiet between outings; a prompt rescue can succeed | owner answers | kept, quoted | | |
| The Rot in plain words | review §0 | kept; the design's opening follows it | | |
| "It has no voice of its own, nothing to do with the ship" | review §0 | lost | No longer true after 2026-10-02. | |

### The metabolism

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature: the floor warms shelter, the open ground spoils stores, the harvest heats storage | cleanse definition, owner_pages | kept as the ground of 0.1.0 | | |
| Flooring over the mat ends its warmth | cleanse definition | kept as a promise's control | | |
| Exposed corpses desiccate faster | cleanse owner_pages | kept | | |
| Produce heat follows the native fungal diet | cleanse owner_pages | kept; no produce carries it yet | | |
| Probabilistic thinning of outdoor filth | cleanse next_version | kept in "later" | | |
| The giant's own rot aura | cleanse next_version | lost (recommended for dropping) | | |
| The giant's warm trail | cleanse next_version | kept in "later" | | |
| Grown heaters: palpably warm mushrooms, cultivated | sheet §3, §7; kit M3 | kept in "later" | | |
| The heat-generating gene; furnace-blood | sheet §3; cleanse | kept in "later" | | |
| The portable mat: works anywhere, fed off the Rot, buds, rides the ship | mat spec; open questions | moved (cleanse next version → 0.2.0), with the log's last camp | Corrected by the second reader: the first read kept it in "later" and named this as the other choice. His ruling of 2026-10-22 makes it a ship part. | "Later": needs no off-Rot proof in either version. |
| The starving-mat variant inside the Rot | kit, owner card 3 | lost (ruled out) | | |
| "The mat keeps you" as a bar | bars draft | kept as a promise in other words | | |

### Life

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The donor fungal suite, renamed and resized (grath elder twenty cells wide) | names doc | kept as the flora | Read by heading and the first rows only. | |
| Thirty wild plants, all fungal | cast proposal; roster json | kept | | |
| Marsh fungi in the milk; mushroom bridges; goo lights | sheet §7b | kept | | |
| Mushroom leather, logs, floors, carpet | sheet §7b; cleanse | kept | | |
| The Skulltop defender | sheet §7b | kept, quoted | | |
| Ten Biomes-team creatures migrate to the free tier; names coined | cast proposal; review ruling 1 | kept (done) | | |
| Thozzik, the hornet colony and its queens | cast proposal | kept | | |
| Illoth, the moth; dustveil, the silk moth that flies | cast proposal; cleanse; open questions | kept; real flight | | |
| Brullith, without its laboratory origin | cast proposal; review | kept | | |
| Brogg, the milker | cast proposal | kept | | |
| Grellik; skerrith, the mantis that passes for a cap | cast proposal; redo | kept | | |
| Thozzik, illoth and brogg redrawn as hybrids of our own creatures | review follow-up 3 | kept | His typed words. | |
| Rennok, gromma, durrok, mullgoth, chittik, the colossi | review census | kept where they are; durrok and mullgoth's shared homes left alone | No evictions. | |
| Vorrugath: "a walking piece of the pale forest" | review census | kept, quoted | | |
| Snoruuk and the shiro trap stay campaign-side | cast proposal | kept | | |
| The nameable donor animals evicted; the vanilla zoo | sheet §0, §7b; roster json | lost (evicted) | | |
| Bovine beetle milk, cricket eggs, dulcis | sheet §7b | kept where built as ordinary products | | |
| Chittik implanting bite | cleanse next_version | moved (→ 0.2.0) | | |
| Spore allergy diseases | sheet §0; cleanse | lost (recommended for dropping here; the Contagion keeps its own) | | |
| Spore-flesh as a Sheen infection | sheet §7b | moved (→ 0.2.0, with the Sheen) | | |
| Thozzik faction affiliation | cleanse census | kept as a build fact | | |
| "The grove tends its own" as a bar | bars draft | moved (→ 0.2.0) | | |

### The giant and the ship

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The gut that walks: "a huge maggot slow maggot covered in small wriggling tentacles and eye spots" | review ruling 2; redo | kept, quoted | His typed words. | |
| "The old ship that's pinging from within begging the players to figure out how to kill it" | review ruling 2 | kept, quoted | | |
| It eats whatever lies down, digests all but metal, passes polished salvage | review ruling 2 | moved (cleanse next version → 0.1.0), quoted | | |
| Castings return items whole and mended | cleanse next_version | moved (→ 0.1.0) | | |
| Something Is Still Alive In There: the knocking, the name, the time | redo O1; review ticket-out | moved (→ 0.1.0), quoted | | |
| "Sometimes the knocking is a stranger" | redo O1 | kept with it, quoted | | |
| "The gut takes the fallen" as a bar | bars draft | moved (→ 0.1.0) | | |
| The Swallowed Navigator: the console answers the ping; the log writes itself | redo S1; review ruling 3 | ping moved (→ 0.1.0); log and sites moved (→ 0.2.0) | | |
| The core is "a significant upgrade to your ship if extracted" and ship weapons harm it | review ruling 3 | moved (→ 0.2.0) | | |
| The core is unique in the world; a quarter more range | review follow-up 1 | moved (→ 0.2.0) | | |
| The core's campaign tiles | open questions Q3 | kept in the campaign layer | | |
| "A treasure map that is still writing itself" | redo S1 | kept with the log | | |
| The Gut-Mother: implants back from the dead; starters to sell | redo T1; review ticket-out | moved (→ 0.2.0); "the most Jawa idea of the lot", quoted in this page | | 0.1.0: the stop's best trade good in the first version; three systems to prove. |
| The Unjoining Draught | redo T2; review ticket-out | moved (→ 0.2.0) | | |
| The Rot Will Not Let Them Go | redo S2 | lost (not chosen); flagged above | | |
| The Joined Ear | redo O2 | lost (not chosen); flagged above | | |
| The sheened hull | review §4, §5, §7 | lost (turned down); `NEEDS HIM` | | See above. |
| The ground's heartbeat; a grove's audible breath | review §4, §5 | lost (turned down) | | |
| Unseaming | review §4, §5 | lost (turned down) | | |
| The wound-tie as learned technology | review §4 | lost (not taken) | | |
| Scanner readings | cleanse | kept | | |
| Digested wreck field | cleanse | kept | | |

### Cups, groves, symbionts and the rest

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The teas: "biosculpting in a cup, EARNED" | sheet §7 | pleasure cup kept in 0.1.0; the others moved (→ 0.2.0); flagged above | | |
| The pleasure brew in 0.1.0 | marks | kept | His mark of 2026-11-17. | |
| Tea potency: five years, once a year, "darned hard to obtain" | kit, owner card 1 | kept with the ageless cup | | |
| The guardian repertoire: spore clouds, summoned defenders, the grasping mat, false fruit | sheet §7; kit M6 | moved (→ 0.2.0) | | |
| Symbionts: "luciferium pulled apart", three bargains | sheet §7; kit M4 | moved (→ 0.2.0) | | |
| Sheen gear only slows the clock; the symbiont is the only true immunity | kit, owner card 5 | moved (→ 0.2.0, with the Sheen) | | |
| The new conscience: a mood cost for selling the Rot's treasures | kit, owner card 6 | kept in "later" | | |
| "The Sheen marks you" as a bar | bars draft | moved (→ 0.2.0) | | |
| Exports for the Slime | sheet §7 | kept in "later" | | |
| The gourmet line | sheet §7 | kept in "later" | | |
| The pale tree: "a door ajar"; cap two | sheet §7; kit M8, owner card 4 | kept in "later" | | |
| The spore-warfare kit: thrown thrumbungus, mantis scythe, chitin helmet | sheet §7b | weapon and helmet moved (→ 0.2.0); the scythe not found built | | |
| Blastpod to chemfuel, wild only | sheet §7b | moved (cleanse next version → 0.2.0), quoted; asked | Corrected by the second reader: the first read had 0.1.0. The built plant cannot grow at the Rot's temperatures. | |
| The fungal power generator | sheet §7b | lost (cut: "that's stupid") | | |
| Ambrosyx | sheet §7b; cleanse | moved (→ 0.2.0) | | |
| Fungiponics basin | sheet §7b; cleanse | lost (recommended for dropping) | | |
| The spider-head trophy; the airborne-food collector; the mould mood | cleanse | lost (recommended for dropping) | | |
| The regional spore cloud | sheet §7b; kit M9; cleanse | kept in "later" | It never falls on the Rot itself. | |
| Industrial medicine | cleanse | kept in "later" | | |
| The Gut's Due; Standing in the Sheen; the Bought Quarrel | review §5, §6 | lost (not chosen) | | |
| The Unjoining, for Ta'Baa | review ruling 4; open questions Q4 | kept in "later"; flagged above | Rites are a second version. | |
| A wayward Prime elsewhere | cleanse | kept in "later" | | |
| World scoring and mutator chances | cleanse | lost (worldgen is forbidden) | | |
| Mod Settings | kit; cleanse | kept | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Settling here means arranging shelter, harvest and refrigeration around the same metabolism" | cleanse definition | kept, reshaped: a crew on a stop arranges its ship | | |
| A colony of forty; the whole-map season | cleanse definition | moved (first version → later) | Colony scale. | |
| The four offline models | cleanse owner_pages | kept | | |
| Tickets and switch-offs | cleanse next_version | kept as they stand, except where a feature moved | | |
| Seven proposed bars | cleanse owner_pages | kept as history; the thirteen promises in the design are the proposal to argue from | | |
| The seven open questions of 2026-10-22 | open questions | kept as answered there; only two were opened | | |
| The scorecard of nine marks | review §2 | lost | A measure of the old programme. | |
| Art briefs for regeneration | review ticket-out | kept as a build fact | The briefs file itself was not read. | |

### Added by the second reader

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The dead ship's log, eight entries, written and built: *"Day nine. Something big came through camp in the night. Slow. Pale. It ate the cargo netting, the tarps, the galley. It did not touch us. It left the cutlery in a glossy lump by the ramp, clean as new."* | log def | kept in 0.2.0, quoted in the design | The first read kept "the log" and never opened it. It is the story of a ship's crew on this ground, in their words. | |
| *"Day fifteen. Engineer took the drive coil out to clean the spores off it. Left it on the mat for one hour. One hour. It is gone, and the pale thing is lying where it was, and we can hear the coil humming inside it."* | log def | kept, quoted in the design; it is the hull section's source | The only place in the sources where the Sheen and the giant are shown acting on a ship. | |
| *"The fog does not clear; it sticks."* *"Note for whoever reads this: cover what you keep."* *"We did not shoot it. Shoot it and the coil goes with it."* *"The captain wants it back. I want to go home."* | log def | kept, quoted in part in the design | | |
| The last entry: *"Cut the beast open gently. It never meant us harm. It just keeps"* | log def | kept, quoted in the design | | |
| The last camp, *"past the third ridge"*: *"The warm mat took them in the way it takes everything, gently and completely, and where they lay a root of it has knotted itself, its heart still beating."* | log def; mat spec | moved (first read "later" → 0.2.0), by the second reader, with the root it holds | It is the log's eighth entry and the log is 0.2.0; the first read split them. | |
| The living mat root as a ship part: *"Can be installed on the gravship to help with heating in cold places as a reward. Needs food."* | mat spec; ship gifts | moved (first read "later" → 0.2.0), by the second reader | His ruling of 2026-10-22, built. The first read named 0.2.0 as its other choice. At the built defaults the eighth entry comes sixteen days after the first ping, inside a stop. | "Later": the reward most plainly made for a ship stays out of both versions. |
| The root was struck from the list of ship gifts on 2026-11-11 because two other biomes also gave a heater | ship gifts | kept as a flag; his ruling wins | A delegated judging pass, not his word. | |
| The trade between the two prizes: *"Cutting the drive core out early ends the log, and the root with it."* | mat spec | kept, stated in the design | | |
| The root's rules: eats raw food off the Rot and nothing on it (*"Joined to the Rot's network: the living ground feeds it"*); starves visibly and never dies; buds a second *"now and then"*; *"It is a floor tile. A living floor tile."* | mat spec | kept with the root (0.2.0) | His second card of 2026-10-22. | |
| Whether a mat floor laid on a ship's deck survives a launch | mat spec | kept as a flag (`UNMEASURED`) | | |
| The swallowed drive core as the Rot's gift to the ship | ship gifts | kept in 0.2.0 | An agent's pick on the gifts list, matching his own typed ruling on the core. | |
| His shield rulings: a spore shield cut (*"spores aren't magical, just particulates"*); the light screen *"handle[s]... bio contamination, spores... completely"* | shield rulings | kept in 0.1.0 as the Rot's hull wear and its answer | The first read wrote that no hull system exists and did not open the frame. | |
| The built frame cannot see Sheen: it knows particulate hazard as pollution or sand in the weather, and the Sheen weathers carry none | shield rulings | kept as a flag; the small build is named in the design | Measured in the weather def. | |
| The frame's cold wear and the cryo envelope against the Rot's temperatures (median −18.8 °C, floor −42 °C; the tracker fires at forty below) | shield rulings; sheet §0 | kept as a flag (`UNMEASURED`) | On most Rot ground it would not fire. | |
| The consult's harder sheened hull: *"scrape early, replace infected deck later, abandon a compartment, or launch carrying a declared discharge of Sheen inside the ship after the next landing"* | review §5 | lost (merged into the sheened hull, turned down 2026-10-02); `NEEDS HIM` 1 | | |
| The wild blastpod's growth floor is 50 °C; the Rot's maximum is +24 °C | blastpod def; sheet §0 | kept as a flag; filed as `RIMMANDRAKE_DECIDE_ROT_BLASTPOD_GROWS_ONLY_ABOVE_FIFTY_DEGREES`; `NEEDS HIM` 3 | Measured in the def. The first read made this plant the Rot's richer fuel. | |
| *"it can only live in hot caves; the wild-only ruling stands but its wild presence is cavern-gated, not surface"* (2026-09-09) | roster json | kept, quoted in the design | The first read took the roster's keys and counts only. | |
| The donor blastpod purged for that reason; its stand-in purged; *"I don't want new versions of these silly plants"* (with his ruling of 2026-09-20) | roster json | kept, quoted in the design | Later than the 2026-09-06 ruling the first read stood on. | |
| Blastpod to chemfuel in 0.1.0 as the Rot's richer fuel | sheet §7b; cleanse | moved (first read 0.1.0 → 0.2.0, the cleanse's bucket), by the second reader; asked | The three findings above, and his letting the cleanse row stand on 2026-11-17. | 0.1.0: a promise the built plant cannot keep. |
| The fungal-soil trade: *"Dig fungal soil, sell it to moisture farms by ship; digging sends distress through the fungus and brings its creatures."* | mechanics review; review §1 | kept in 0.2.0, campaign layer; now moment 13 in the design | Built. A thing dug up and sold by ship is the crew's own trade; the first read has no row for it. | |
| The trade was dead for a time: gated on the retired donor biome, so *"the knots never scatter and the distress never fires"*; fixed by the tier-leak item | review §1 | kept as history | | |
| *"You land warm. That is the first wrong thing — the tile said −19 °C and the glow-moss under your boots is damp and body-warm, while the air a meter up frosts your breath."* | kit (player experience) | kept, quoted in the design | The first read took the kit's headings and cards. | |
| *"Your first economy is the freezer war."* *"brew in your vessel at the shrine some earlier party left, and drink it while it lives."* *"It is generous, warm, and always, patiently, digesting you."* | kit (player experience) | kept, lines carried here | | |
| His reason the mat is free: *"likely the only way to tolerate the night side at all without spending all your power on heating"* | kit, owner card 3 | kept, line carried here | | |
| His reason gear only slows the Sheen: *"incidental exposure every time you go in and out — you just can't totally sterilize everything"* | kit, owner card 5 | kept, quoted in the design | It is why the Sheen comes aboard. | |
| His reason for the tea's limits: *"a pilgrimage industry, rate-limited so it never becomes routine"* | kit, owner card 1 | kept with the ageless cup (0.2.0) | | |
| The rot scope's precedent: *"the biome makes you engineer"* | kit, owner card 2 | kept, line carried here | | |
| The conscience as he framed it: *"selling a part of yourself"* | kit, owner card 6 | kept in "later" (the first read's row), line carried here | | |
| The pale tree at cap two: *"a real minor kit, not just a door ajar"*; and its feeling *"that you really should find someone to train you"* | kit, owner card 4; sheet §7 | kept in "later" | | |
| The Force named in the free pale tree's text; taken out, and patched back in the campaign | review §1 | kept as a build fact (done) | | |
| The yssomar, the wound-bearer: *"a hill of grey-lilac caps over a long body like coral grown over a beached whale... its hide a patchwork of healed scars that are not its own"*; *"the one giant whose danger is your own violence"* | review §3 | lost (not chosen 2026-10-02; *"no yssomar is built"*) | He chose the gut that walks. | |
| Its hook: old blaster burns *"the ship's Narrator recognises as the pattern of its own guns"* | review §3 | lost with it | A ship idea, and not his pick. Listed, not revived. | |
| The brullith that cannot lie down: a cargo yoke grown through its chest; *"a giant met as a patient, not a fight"* | review §5, §7 | lost (not chosen 2026-10-02) | | |
| The hwelgrue's body as built: *"bone-white with a lilac underside"*, a dredge mouth rimmed with hyphae; hide that halves blows; *"fire does full damage (the Rot's fungal weakness)"*; hurt, it *"turns and crushes whatever hurt it"* | build items | kept | Fire as the weakness matters to a fight on a week's clock. | |
| Scavengers follow it *"as crows follow a plough, and its trail is a salvage line"* | review §3 | kept, quoted in the design | | |
| Its unpicked hooks: *"Imperial salvage crews have started following it too; a trail shared with rivals"*; *"one day a casting holds a sealed data core"* | review §3 | lost (not picked, never built); the first is flagged in the design as `UNSETTLED` | It is the only line in the Rot's sources that puts the Empire on this ground. | |
| The swallowed thing was first written as *"a piece of a Rakatan ship"* | review §3 | kept as campaign lore; the built core says only an older ship | | |
| Its readable signs: *"Digesting. Something metal rattles inside."* *"The console is answering something. It is inside that animal."* *"The ping falters when the ship's guns hit it."* | build items | kept | | |
| A casting is cracked open by hand; a smashed one still drops its metal; contents come out at death | build items | kept | | |
| The stranger inside: a chance a newly met hwelgrue already holds *"a trader's pack animal still wearing its packs, or a wounded wanderer"* | build items; redo O1 | kept (the first read's row), detail carried here | | |
| An animal inside *"makes scrabbling instead of a voice"*; *"Mara was swallowed by the hwelgrue."* | build items | kept | | |
| The knocking's audio is borrowed and pitched down; no knocking or voice was ever recorded | build items | kept as a build fact (owed) | The moment the design leans on is, today, a punch on wood. | |
| Where the giant rests, things rot three times faster and the mat spreads warm | review §3; build items | lost (the rot aura: recommended for dropping; the warm trail was never built) | The first read's rows cover both; this one adds that the warm half was not built. | |
| The core as built: one per world, the first wild giant to settle claims it; integrity; ruined below a quarter | build items | kept in 0.2.0 | | |
| The core's range is a share of the ship's whole range, not a fixed number | review §8 (follow-up 1); build items | kept as description, never a bar | A bar is an experience. | |
| Gut-mother starters are the one living thing that may leave the Rot: a *"ruled exception to ban 4"* | review §8; build items | kept in 0.2.0; now stated in the design | | |
| The vat needs feeding or goes dormant; a letter the first time an implant comes back | build items | kept | | |
| The draught forces a hidden Anomaly horror out of a body: *"The draught found something that was not a parasite."* | build items; redo T2 | kept in 0.2.0 | | |
| The Unjoining is keyed to the launch: fly within days and the god of flight is pleased; stay, and the memory sours: *"We cut it out of her and stayed anyway."* | rite item | kept in "later" | Tabled by him 2026-10-03, kept tabled 2026-10-22. It is the one rite on the planet written around a ship leaving. | 0.2.0 for the Rot alone: it reopens rites before he said to. |
| The rite's found sign: *"an empty brewing vessel overturned at a grove's edge, a rag stiff with dried Sheen, and footprints that stop shining halfway down the path"* | review §6; rite item | kept in "later", line carried here | | |
| The draught is *"the only tech on the planet that comes out of a rite"*; today it is plain research, because there is no rite | redo T2; open questions Q4 | kept as built | | |
| The Gut's Due: lay goods of equal value on the warm mat and guard them while the rot eats them; found beside *"a trader's pack frame grown through by the mat"* | review §6 | lost (not chosen 2026-10-02) | The first read's row names it only. A trader's rite; his to bring back. | |
| Standing in the Sheen: faces up in the fall, no gear; found at stones with *"the faint shapes of people pressed into the gloss"* | review §6 | lost (held off the card) | | |
| The Bought Quarrel: the clan guarantees a stranger's unpaid debt and both sides come armed to collect | review §5 | lost (not chosen 2026-10-02) | | |
| The wound-tie: a surgery that ties two colonists so each takes half of the other's injuries for a season | review §4 | lost (held off the card) | | |
| The grove's audible breath: *"a long wet in-breath... cap clicks... a hiss, then quiet"*, the timer for a brewing trip | review §5 | lost (offered with the heartbeat, turned down 2026-10-02) | | |
| Unseaming in full: learned from a fungus that *"strips organic binders off machinery and leaves the metal assemblies intact"*; taking a damaged machine apart into working parts | review §5 | lost (turned down 2026-10-02) | The review called it *"the best fit with the clan."* Listed, not revived. | |
| The kin table he ruled 2026-09-18: wound-link and mending by named clique, *"never biome-wide"*; mending in proportion to body size | kin table | kept in 0.2.0 with shared wounds | | |
| Who answers a grove's alarm: the vorrugath (*"the forest walks over, when it's near"*), the skerrith (*"the trap you never saw answers"*), the chittik | kin table | kept in 0.2.0 with the groves | | |
| A grove alarm that rings into empty forest: accepted by him as it is | kin table | kept | | |
| The chittik: *"a single body with a hundred mouths that shares every wound it takes"* | review §1; kin table | kept, line carried here | | |
| The durrok and mullgoth live in three biomes: *"Like needs to move. Wait until biome reviews. But you are right they should not be like this."* | open questions Q1 | kept as it stands | No evictions. | |
| The dustveil: made to fly, fungus-grown, its laboratory origin dropped | open questions Q5 | kept (done) | | |
| The core's campaign tiles wait for the remade planet; until then *"no hwelgrue anywhere ever carries the core, silently"* is the risk named | open questions Q3 | kept in the campaign layer | | |
| The four drafted bars pin numbers (21 °C, 3 a day, a day and a half) | bars draft | lost as bars; the experiences are kept as promises | His ruling of 2026-11-16: a bar is an experience, never a tuning number. | |
| The first bar was asked for as *"hurt one, the grove comes"* and drafted as a mending rate | bars draft; open questions Q7 | kept as a note; the design's 0.2.0 moment 9 is the one he asked for | | |
| Thozzik, illoth and brogg redrawn *"NOT terrain animals hybridized. Our own custom creatures from other biomes"*: from the kurreth, the vrisk and the dorrak | review §8 (follow-up 3) | kept (the first read's row), parents named here | | |
| The Contagion takes the Rot's spore allergy too | review §8 (follow-up 2) | kept elsewhere (the Contagion's design) | | |
| Names tried and dropped: zillok (a canon beast's stem), yurrok (one letter off a Rot shelf fungus), yooka | cast proposal | lost | | |
| The angel moth and the anima colossus, named mollith and kerrugoth | cast proposal | kept in the roster | | |
| No new creature was needed in 2026-09: *"18 rows already exceeds every neighbouring biome's fauna count"* | cast proposal | kept as history | | |
| No fish: *"the milk ponds are not-water"*; what lives in them is fungal | roster json | kept as a rule | | |
| The six cavern creatures cut 2026-09-20; the glow bats cut 2026-09-10; nogtyl moved to the Miasma and rust puff to the Contagion | roster json | lost (cut) or kept elsewhere (moved) | His rulings, as the roster records them. | |
| Every kept fungus had a growth floor of 0 °C on a biome with a median of −18.8 °C | roster json | kept as a flag (`UNMEASURED`) | The roster raised it on 2026-09-09; the rehearsal found the dark-growth repair but no temperature proof. If it is still true, the forest does not regrow. | |
| Inkcap and the silk moths were named by the sheet and never found as defs | roster json | kept as a note | | |
| The mollugh, the Rot's watcher: *"a fungus/animal that pulls itself under its own cap"* | watcher pitch | kept in 0.2.0 as a proposal | Pitched under his 2026-10-08 ruling; never admitted at a sitting. | |
| *"Fungi are the one metabolism that never noticed the sun is gone."* | sheet §2 | kept, line carried here | | |
| *"the dayside's lush is a thin green line; the nightside's is a thick pale sprawl"* | sheet §2 | kept, line carried here | | |
| *"Warm ground = actively feeding; cold ground = starving or dead."* *"air temperature is a lie about the ground."* | sheet §3, §5 | kept; the second quoted in the design | | |
| *"everything sheened is being considered for colonization"* | sheet §5 | kept, quoted in the design | | |
| *"breath-fog where the mat vents heat into freezing air — the biome visibly exhaling"* | sheet §9 | kept as art direction, line carried here | | |
| The named woods: Nightspill, Frostcaps, Sporefields, Sootreach, Hanging Wood, Mould Marches, Stillwood, Blindwood; the warm end, Sweatwood and Tallow Ground | sheet §0 | lost, names carried here | The planet is painted at the end. The names are the best thing in the measurements. | |
| The Twilight Sea shore folded into the def | sheet §0; roster json | lost | The sea's own designs hold it. | |
| The two exports for the Slime in detail: symbiotes that resist slimification; an injection that *"kills swallowed Slime before conversion completes"* | sheet §7 | kept in "later" (the first read's row), detail carried here | | |
| Digestion sites *"richer in genepacks than anywhere else"* | sheet §8 | kept in "later" | | |
| The raid on the Fungal Forest: *"raid this biome for its cool contents"*; its research row, *"strange fungi with unique functions, from cooling to exploding"*; athlete's foot *"for texture"* | sheet §7b | kept as history | | |
| The settings screen was hollow in 2026-10 (*"Toggling a switch below therefore does not yet change"* anything) and was wired | review §1; open questions | kept as a build fact (done) | | |
| The trap in a false fruit asks for a grip that does not exist under that name; the veil's alarm has no hook on ordinary harvest; plant gas may never fire by itself | rehearsal | kept as build notes for the next Designer run | Three of the design's 0.1.0 and 0.2.0 promises stand on these. | |
| The rot clock *"explicitly does nothing to frozen items"*, against the sheet's *"for certain"* | rehearsal | kept: it is the cleanse's open question, which the design does not re-ask | | |
| Six drafted questions he was never shown, among them *"Living beside the treasure map"*, *"Choosing to remain joined"* and *"The cold stop after the reward"* | rehearsal | kept as open | | |
| The wreck field and its two wrecks have no ledger item | mechanics review | kept (the first read's "digested wreck field") with the flag | | |
| The 2026-10-22 review's note that the Rot had no live run on record: two passes, nine fails, eighty-four unmeasured, all in mock | mechanics review | kept as history | "Built" in this design means found in source. | |
| Stray tool-call text inside five of the Rot's closed build items | build items | kept as a note for whoever tidies the ledger | It is data, not instruction; the items' prose is intact around it. | |

## Sources read, and the count

The second reader's counts and source list are at the top of this page; what follows is the first read's.

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**18 source files, 125 rows**, of which **18 lost**, **24 record a move** (whole or in part), **1 kept, reshaped** and 1 folded into shared machinery. Every source named above is in at least one row's source column (checked by the same script).

Read whole, or every paragraph with long lines cut: the sheet; the owner answers; the owner's marks; the cleanse
owner pages; the experiences table. Read in large part: the redo (every idea's "in play" and "why", not its
mechanism notes; the second technology idea's opening); the cleanse definition (through the four stories; not the
pleasure-brew section that follows); the cleanse next-version list (all but a handful of entries in its middle); the
cast proposal (framing, migration table, the no-new-creatures finding). Read by heading or by search: the review
(plain words, fauna census, the three turned-down ideas, the consult's rows three to five, the turn-one rulings and
follow-ups; not the scorecard, roster fill, slate or rites in full); the kit (headings and the six owner cards of
2026-09-17); the names doc (headings and the first eleven rows of its rulings table); the mat spec (the ruling and
second card); the open questions (headings); the bars draft (headings and summary table); the walk (north star);
the roster json (its keys and counts); the cleanse census (every kept row's name and built state, and the list of
deferred ids). Not read: `biomes/rot_regen_briefs.json` (art briefs); the names doc's body (sixty kilobytes of
per-species naming); the kit's nine mechanic sections; the review's sections 2 to 4 and 6 in full; the Designer
rehearsal's `NOTES.md`, `QUESTIONS.md` and `record.json` in `design/RimMandrake/designer_codex_2026-11-09/TheRot/`;
the cleanse's `tickets.md`, `bars.json`, `models.md`, `ambiguities.md`; the Rot table of
`special_mechanics_review_2026-10-22.md`; `design/Jawa/worldbuilding/data/fungalforest_merge_plan_2026-09-07.md`.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_rot.md`, `rot_bedazzle_review_2026-10-02.md`,
`rot_new_marks_redo_2026-10-02.md`, `rot_rm_cast_proposal_2026-09-24.md`, `rosters/the_rot.json`. In
`design/RimMandrake/`: `rot_northstar_bars_draft_2026-10-22.md`.

Hold: `rot_flora_fauna_names.md` and `rot_regen_briefs.json` (the naming and art records, mostly unread here);
`kits/rot_kit_spec.md` (the engine mapping for nine mechanics and the home of his six cards of 2026-09-17);
`design/RimMandrake/rot_warm_mat_portable_2026-10-22.md` (the only specification of the portable mat, which this
design defers); `design/RimMandrake/rot_open_questions_2026-10-22.md` (his answers on shared animals, the core's
tiles and the dustveil).

Not for deletion: `design/concepts/TheRot/cleanse/` including `owner_marks.md` (superseded by this design, never
applied; it should be re-run from this file, not applied); the validation walk.

Before deleting: `the_rot.md` is frozen by `BIOME_FREEZE_FABLE_REVIEW_1` and is cited by section number throughout
the kit, the cleanse and the Slime's sheet (for the two exports). Its section 7b is the only record of what was
taken from the dissolved Fungal Forest and what he ruled about each piece.
