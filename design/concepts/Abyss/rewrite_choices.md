# The Abyss: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A different agent from the writer re-read the Abyss's sources before any old file is deleted, starting with the
ledger items and with what the first read had named as unread.

DELETE-READY: no, because one source file is not yet read to its end: `design/RimMandrake/special_mechanics_review_2026-10-22.md` from line 221 on (the other biomes' tables; its whole Abyss table is read). The continuation of 2026-11-18 read the other fifteen part-read files to their end and added 100 rows (the last five tables under "Every idea, row by row"); this section's counts below are the earlier ones until that file is finished.

Every file on the delete list was read to its end by the second reader (`abyss.md`, the cast bible, the cryptid
spec, the review, `rosters/abyss.json`), and so was every file in `design/concepts/Abyss/` but one, and every
ledger item with the Abyss in its name. The "no" is for these, read in part: `cleanse/census.json` (all 97 rows'
id, fate, what and why; the evidence and caller path fields for the first twelve rows only); the codex run's
`record.json` (root draft, scope, decisions, contradictions, neighbours and all 76 inventory texts; not its
reviewed-file list, scene audit or proof notes) and `QUESTIONS.md` (all nine questions; the tail of its root
paragraph cut); `BIOME_SHIP_CONTRIBUTIONS_1` (every table row; long paragraphs cut at 1,500 characters);
`_freeze_rulings_2026-09-07.md` (R1, R4, R5, R10, R17, R24 and a search); the escalation ladder (its Abyss lines);
the names document (its Abyss batch); the mechanics review (its Abyss section, the last cells of rows 14 to 16
cut); `v2_nine_rituals.md`, `fluff_cuts_2026-10-23.md` and `biome_experiences_2026-10-20.md` (their Abyss lines).
Not opened: `designer_brief.md` in the codex folder, `SALVATION_RITES_UNIFICATION_1`,
`CONDITION_GATED_RITUALS_MOD_1`, `salvation_rites_2026-10-01.md`, `biome_rites_pass_2026-10-01.md`, and the other
files in `design/` that only mention the Abyss. A run that reads those eleven to the end can change this line.

**Measured** (by `rowcheck.py`; its line is in
`design/RimMandrake/biome_recheck_feverwood_greentide_abyss_row_check_2026-11-18.txt`): **264 rows, 126 of them
added by the second reader.** By the first word of "what happened": 215 kept, 34 lost, 7 kept and reshaped, 6
moved, 2 folded into shared machinery. 32 source names, each used in at least one row. **50 source files read to
their end** (the first read counted 19, most in part).

**The three most valuable things the first read missed**

1. **His three card answers of 2026-11-10 on what the hide is for** (`designer_codex_2026-11-09/Abyss/ANSWERS_OWNER.md`,
   never opened by the first read). *"Searches interrupt work: ordinary work is safe between searches, but exposed
   activity becomes dangerous while a search probe passes."* *"Wonder draws you out... then leaves you exposed when
   darkness returns."* *"Danger becomes more frequent... giving a practical reason to depart at the cost of
   breathing room."* The second is the best evidence there is for the first read's one scope move (the hidden ship
   into 0.1.0); the third is a clock on the hide that nothing builds yet.
2. **The grain on the hull has a source, and it was a ship idea put to him.** The review's "The Abyss etches the
   hull" (wear on hull fittings, a lasting *"I was in the Abyss"* scar, *"sweeping the tholin off pays for some of
   the repair"*) was offered on his card of 2026-10-01 for the free tier; he chose no free-tier ship touch. The
   first read believed no source had it. The wear stays in 0.1.0 by his ruling of 2026-11-18; the scar is asked.
3. **His sheet of 2026-10-05**, which lives on a ledger item and in the roster file: the black, four-eyed kin and
   what their descriptions say (*"less evolved than made, as if some old and patient cruelty once had the shaping
   of it"*), and six animals he cut, two of which the first read still carried (the dusk rat as an art debt, the
   frostling as lost for want of a source).

Close behind: the rites belong to "later", not 0.2.0 (his ruling of 2026-10-23 deferred every biome rite); his
first idea of this biome was the sea floor (2026-08-13), which is why the pilot's brief called it a sea; and, read
from the source, the ship's cover counts built lamps and not living light, so the design's "farm against cover"
bargain was the wrong way round.

**What changed in the design, and why** (each is also a row below)

1. His three card answers are quoted in "What this place is" and used: the probe rule, the Unveiling as a
   temptation, and "the longer the stay, the fewer the quiet stretches" as what ends a hide.
2. The cover bargain is corrected to the source: built lamps cost cover, living light does not, and the cover
   wears thin by itself. The lamp-tree farm no longer costs cover.
3. What is built of the hidden ship is stated: the meter and the probes are; the engine breaking cover and the
   pursuit reading the cover are not; the probe sees by distance through walls and reads no heat.
4. The hull wear cites its source and the hiding rule it must not break (*"not hit points"*); the wreck's four
   repair fittings are named as the Abyss's own repair (0.2.0); the rough way in cites his wind ruling R4
   (*"the ship damage"*).
5. Fuel: his two rulings on tholin are both stated, and the later one (his card of 2026-10-01) is followed.
6. The kin, the two fish by name, the sorter's filth-eating, and the ishvarith answering light (not heat).
7. Scope: the rites to "later"; the great bone as the recorded ship gift; the ship's four accepted and three
   refused parts and its refusal line; a new dropped list (six cut animals, four ideas not chosen on 2026-10-01,
   the sea-floor idea, eclipses).
8. `NEEDS HIM` went from three to eight, each with its default: scope 2, hull 2, cover 1, other 3. Fuel: none.
   Locked-tree: none, the Abyss has no locked sheet or tree.

**Four first-read rows corrected in place** (each says so in its cell): the dusk rat, the frostling, the four
rites, and the hull-wear row.

**Rules applied.** Hull wear cites the existing frame (`src/RimUtinni/ShipShields/`) and now cites its source;
nothing new was invented for it. Ship ideas he declined are listed and not revived (the etch scar, moths on the
ship's lamps, the stealth lamp). His latest dated words won where sources disagreed: his cuts of 2026-10-05 over
the sheet, his fish mark over the roster's no-fish ruling, his card of 2026-10-01 over his fuel table of
2026-09-07, his rites deferral over the cleanse's "next version". Each cleanse deferral was checked against his
answers dated before it: the hidden ship's deferral was a delegated call made a week after his card on probes,
and he then approved the cleanse's scope, so the move stays a question for him. The clock's arithmetic was not
touched.

**Findings for other pages.** `BIOME_SHIP_CONTRIBUTIONS_1` says the great bone lets the ship *"raise the Abyss's
flyers"*; the summ is a six-limbed grazer and does not fly. The older lore files that tie the cryptid to the
Rakata are listed in the cryptid spec §8 and still owe their fix.

Companion to `design/concepts/Abyss/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**Two things to know first.**

1. **The Abyss is not a sea.** The brief for this pass picked it as "a sea biome: the ship is the only way down and
   back". Every source describes a dark highland past the terminator. So this pilot covered two wet jungles and a
   dark refuge, not two jungles and a sea, and no sea biome has yet been through the lens.
2. **He approved a scope for the Abyss the day before.** On 2026-11-17 he walked the cleanse proposal and wrote: *"I
   saw how much you put into 0.2.0 Impressive, and the right call. It's still a daunting mod even with that you
   chose to keep in 0.1.0. I approve. I changed two items only to move them into 0.1.0, small impact."* This rewrite
   treats that as the starting point, keeps his marks, and moves one thing.

**How the choices were made.** His words of 2026-11-18: the biomes *"are going to be visited by a huge ship on the
run"*; the crew are *"Empire-pursued by scenario design"*; and one of his lens questions is *"Is there anything here
that helps them stay longer and hide/resist the Empire?"* For the Abyss the answer to that question is the whole
biome. His own earlier words say so: *"'Hiding' your gravship from pursuit is a big deal in this campaign"*
(2026-08-13), and on the hidden ship here, *"Yes but probe droids will still come that must be avoided"*
(2026-09-30). So the lens does not shorten the Abyss the way it shortens the jungles. It changes what the first
version is *about*: from surviving in the dark to hiding in it.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given, against the scope he approved on 2026-11-17); *folded into shared machinery*; *lost*.

## Changed after his rulings of 2026-11-18

His card of 2026-11-18, 3:10 PM PST ruled on stop length, cover from orbit, fuel and hull wear, and gave a test for
every solution. This revision changed the design and this page as follows and nothing else. **The hidden-ship move
is untouched: still in 0.1.0 as the first pass made it, still the first question under `NEEDS HIM`, still one line
to revert.**

1. **Stay length is stated, as an outer edge.** The "UNSETTLED: how long a stay lasts" paragraph is gone. The
   design says about two months before the Empire's first contact at the outside (the pursuit's fourfold delay on
   a hidden crew), on his words *"The numbers you're generating are likely the outer edge allowable for each biome,
   and that's just fine. Go with that."* A ship that holds its cover is past that arithmetic, and the design says
   the place then sets the edge.
2. **Cover from orbit is stated as the full kind.** His card: *"full dark still pauses it."* Nothing changed in
   what the Abyss does; the design now says in one place that it is the only biome with full cover, and that the
   jungles' partial cover is a weaker entry beside it.
3. **The grain wears the hull, in 0.1.0.** The question "Does the grain eat the ship?" is removed and answered by
   his ruling (*"Yes in 0.1.0. It's easy, and most of the biome already talk about this."*). Of the three answers
   the first pass offered, the design takes the plain one: the hull wears in any etchfall, whatever the engine is
   doing. The variant where it wears only while the engine is cold is not taken; it would be a second rule on top
   of the weather.
4. **What answers the wear** is taken from the fluff-cut review's *"roof everything"* and his shield ruling of 2026-09-02: a
   roofed lean-to against the hull, patching by hand, the ship's light screen. **New in this revision, not in any
   source:** that a hull face with roofed building against it counts as out of the weather. It is an ordinary
   reading of the built rule that roofed things are spared, and it is what makes the answer hands-on and made of
   scrap.
5. **The rough way in is written as the Abyss's second wear, at 0.2.0.** His ruling names *"rough weather
   turbulence in the approach"* and the sheet describes exactly that here. I put it a version later because a
   knock on arrival has no answer but a shield; that placing is mine.
6. **Tholin is the Abyss's richer fuel source; there is nobody to buy from.** Both were already in the sources
   and the build; the design now says so in the terms of his fuel ruling, and says the Abyss is not replete,
   because the hide burns what it sweeps.
7. **A new section in the design, "The ship while it sits here"**, holds cover, hull and fuel together. One promise
   was added to the 0.1.0 table (the hull in an etchfall), two on-screen moments (sweeping the ship; the shed left
   behind), one scope line in 0.1.0 and one in 0.2.0. `NEEDS HIM` went from four questions to three.
8. **"Very Jawa" applied where a choice was open:** the hull is sheltered with a lean-to of wreck-field scrap
   instead of a fitted cover; the dust that eats the ship is swept into sacks and burned as fuel.
9. **A finding for the shared-machinery file:** the hull-wear frame already exists in the campaign
   (`src/RimUtinni/ShipShields/`). Its cold test is far below the temperatures the Abyss's sheet records, so cold
   is not a hull wear here.

Read for this revision, in part: `abyss.md` §3 (wind and power), §7 and its weather list, by search;
`hiding_the_gravship.md` lines 36 to 58; the first lines of the ship item; and the shield and pursuit files listed
on the Fever Wood's choices page.

## The ones I would look at

1. **The hidden ship, moved into 0.1.0.** This is the one place in the pilot where I moved something against an
   approval he gave a day earlier. I did it because the card said to move and list, and because a first version of
   the hiding biome with no hiding in it reads, under his lens, as the wrong first version. It is one line to
   revert.
2. **The dread of staying.** *"You fear staying here too long will find the source of the nightmares themselves."*
   The cryptid's signs, the whisper that the Nhaleth *"are whoever stays"*, and the dream *"Dreamt I didn't need the
   light"* are all built and all 0.2.0 by his approval. Under the lens they are the natural clock on a hide. I left
   them where he put them.
3. **The Snuffing.** One of four rite inscriptions drafted for him: *"He sees by what you light. Put it out, one and
   then the next, until he forgets where you are."* It was written about a god. It is also the hidden ship's whole
   mechanic in one sentence. The rites are campaign-layer and 0.2.0; the line deserves to be found near a probe.
4. **Sharp-edged clear pockets.** The frozen sheet's most striking image, *"nothing but a thermometer can tell the
   clear pocket from the wall of Dark beside it"*, is not in 0.1.0 outdoors, because the built Dark follows one
   shared outdoor temperature. The cleanse asked him; unanswered; carried.
5. **Fugitive holds.** *"Smuggler caches and bolt-holes of everyone the Empire ever chased into the sensor shadow;
   some still occupied."* The only people in any of the three biomes who are written as hating the Empire. Unbuilt.
   In "later".
6. **Gust power and the repair culture.** *"A working turbine is tended like an animal."* Cut by his card on
   2026-10-01. What survives is the wreck field: the turbines are here only as storm-torn salvage, which suits a
   scavenger crew better than a wind farm would.
7. **The summing that never stops growing.** His, typed, and the best joke in the Abyss for a crew that lives on a
   ship with finite decks. 0.2.0 with the rest of Lightfall, by his approval.
8. **The Ship in the Wall.** *"You can't have two ships but you can cannibalize that one to improve yours... their
   ship only wants certain parts. It likes what it is."* In a campaign whose spine is getting the ship flying, this
   is the richest take-away in any biome. 0.2.0 by his approval, and I agree: it is one site, and it needs the
   brood beside it.

## Scope moves

Against the scope he approved on 2026-11-17 (cleanse proposal plus his four marks).

- **The hidden ship (cover on a quiet, dark, landed ship; probes that still come; the report that ends the cover and
  restores the ordinary search):** 0.2.0 → 0.1.0. Reason above. Revert by moving its line in the design's Scope
  section and deleting the last two rows of the promises table. Trade isolation under cover stays 0.2.0.
- **Second reader, 2026-11-18. The four darkness rites:** 0.2.0 → later, on his ruling of 2026-10-23 that every biome
  rite waits for a second version.
- **Nothing else moved.** His marks stand as he wrote them: the fold lamp, the turning vine, the glowberry as a
  carried light and the fishery are in 0.1.0; heat observation stays 0.2.0.
- **The grain wearing the hull:** asked of him → 0.1.0, by his ruling of 2026-11-18. Revert is his.
- **Gust shear knocking the arriving ship:** not in the first pass → 0.2.0. From the sheet's wind section and his
  ruling's *"rough weather turbulence in the approach"*; the version is my choice. Revert by deleting its line.
- **New, not in any source, and not in a version:** an Unveiling exposing the ship (asked as `NEEDS HIM`, default
  no).
- **New, not in any source:** a roofed lean-to against the hull as shelter from the grain (0.1.0, with the wear).
- **Stated as consequences of built behaviour, with scenes owed:** the Empire's lamps are eaten like anyone's; a
  fold lamp is the only clean firing lane; the crew's own dark vision does not pierce the Dark (from the sheet's
  ban on clean sensing).

## Every idea, row by row

Source names: *sheet* = `biomes/abyss.md`; *cast bible* = `biomes/abyss_cast_bible_2026-10-01.md`; *cryptid spec* =
`biomes/abyss_free_cryptid_2026-10-01.md`; *review* = `biomes/blackcrags_bedazzle_review_2026-09-30.md`; *roster
json* = `biomes/rosters/abyss.json`; *names doc* = `biomes/noncanon_beast_names_crags_nightside_contagion_slime.md`
(all under `design/Jawa/worldbuilding/`); *hiding note* = `design/Jawa/worldbuilding/hiding_the_gravship.md`;
*pursuit note* = `design/Jawa/mods/ruthless_faction_pursuit.md`; *ladder* =
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md`; *ship item* =
`infrastructure/state/items/ABYSS_HIDDEN_SHIP_PROBES_1.md`; *cleanse* = `design/concepts/Abyss/cleanse/` (owner
pages, owner marks, definition, next-version list, ambiguities, census); *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *fluff cuts* =
`design/RimMandrake/fluff_cuts_2026-10-23.md`; *experiences* = `design/RimMandrake/biome_experiences_2026-10-20.md`.

### The place and the Dark

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Obsidian teeth in a fog that light cannot cross, lit only by what grows" | sheet header, §9 | kept, quoted | | |
| The Dark as a substance; light eaten in transit | sheet §1 | kept, quoted | | |
| His experience line (the tide that protects and conceals; beauty that twists; the fear of staying) | experiences, mechanics review | kept, quoted in full | It reads as if written for a ship in hiding. | |
| Measured tiles, arc, temperatures, hilliness | sheet §0 | lost | A tile count is never evidence; painting is at the end. | |
| Crag and wasteland interleave; no border drawn; never a bullseye | sheet §0 | lost from this design | A world-painting rule; it belongs with the paint list. | |
| Wholesale donor content, then bent to this world | sheet header, §4 | kept, reshaped: the donor cast is now owned, renamed and redrawn | His *"No donor dependencies tolerable. Free us."* | |
| Past the terminator; relief and the Dark as two anomalies | sheet §2 | kept | | |
| Where the Dark is made: aurora-ash, tholin rime, daysmoke | sheet §3 | kept as lore, not restated | Nothing at a stop shows it. | A line of description text; free. |
| The Dark folds up in warmth and stays airborne | sheet §3 | kept (warm rooms clear) | | |
| Nothing but a thermometer can tell a clear pocket from the wall beside it | sheet §3, §5 | moved by the cleanse and approved (0.2.0); `NEEDS HIM` carried | The engine's one outdoor temperature. | See the design. |
| The collapse is the erosion: the rock is the trail of where the Dark has cleared | sheet §3 | kept as etchfall and the etched land | | |
| Lightfall, the great chasm where the Dark always dies | sheet §3, §7 | kept; its contents are 0.2.0, its landmark is world authoring | | |
| No steady wind; gusts and stillness | sheet §3, ban 2 | kept | | |
| Wind shattering into vortices among the crags; gust shear that snaps what stands in it | sheet §3, §5 | kept, reshaped, moved: the rough way in for an arriving ship (not in the first pass → 0.2.0) | His ruling names approach turbulence as a wear. | 0.1.0: a hit on arrival with no hands-on answer. |
| "Refuge priced in darkness, breakage and cold" | sheet §7 | kept, quoted; breakage now includes the ship's own plate | | |
| "Roof everything" | fluff cuts (Abyss, etchfall) | kept, quoted; turned on the ship as a lean-to against the hull | | |
| Power in pulses; chemistry seeps | sheet §3, §8 | lost as power (turbines cut); seeps kept in "later" | His card. | |
| No geothermal | sheet ban 1 | kept | | |
| No water rain; etchfall is grain | sheet ban 3, §4b | kept | | |
| No permanent clear weather | sheet ban 4 | kept | | |
| No clean sensing | sheet ban 5 | kept, and applied to the crew's own dark vision | | |
| No sun-dependent resident life | sheet ban 6 | kept | | |
| The Dark weather: near-black sky, ranged accuracy cut, glow below crop threshold | sheet §4b | kept, no number | | |
| The Unveiling | sheet §4b (his), review | kept, quoted | | |
| Etchfall, with a strength slider | sheet §4b, review §8 | kept | | |
| Witchfire storms | sheet §4b | kept as weather; the summ's answer is 0.2.0 | His approval. | |
| Sensors and long sight degrade; the biome slows Imperial pursuit | sheet §5 | kept, quoted | | |
| Wind technology breaks often; repair as a way of life | sheet §5, §7, §8 | lost | Turbines cut 2026-10-01. | |
| Black rock, dark sand, dark mud | sheet §5 | kept | | |
| Art theme: two-toned bioluminescence, etched verticals, rhythm of stillness and violence | sheet §9 | kept as art direction | | |
| Every sprite reads in near-darkness; no baked shadow; palette variety is law | cast bible §2 | kept as art direction | His *"Your color palette is too uniform per biome."* | |
| The rename to the Abyss | review §7 | kept | | |
| "Forsaken" belongs to the Rakata, not here | review §10 | kept | | |
| Dark dims terrain, buildings and non-crew creatures with outlines kept | cleanse | kept | | |
| Intervening Dark spoils a shot even from clear air | cleanse, review (consult) | kept | | |
| Lamps shrink; living lamps resist | cleanse, review | kept | | |
| Sound muffled by the Dark; the gust soundscape | review §12, mechanics review | kept | | |
| One shared gust reading for creatures, sound and anything later | review (consult) | folded into shared machinery | | |
| A shared ledger of who dims which light | cleanse census | folded into shared machinery | | |
| "Tide" is opening and closing air, not a wave system | cleanse | kept | | |
| Forty-colonist rules; whole-map season model | cleanse definition, owner pages | kept, reshaped: the long hide is the one stop where a season model earns its keep; the forty colonists are lost | The crew is five to seven. | |

### The ship, the Empire and the hide

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Hiding as the third verb, after run and fight | hiding note (his concept) | kept, quoted | | |
| "The hiding place must be poor" | hiding note | kept, quoted | | |
| "It must not be permanent"; something must erode | hiding note | kept, quoted; what erodes is the hull, in etchfall (0.1.0) | His ruling of 2026-11-18 on hull wear. | The hull exempt: then only stores and mood erode, and the hide has no clock of its own. |
| "No salvage. No sun. No trade." | hiding note | kept, quoted, as the reason no fuel is bought here | His fuel ruling: *"You can also buy it"*; here nobody sells. | |
| The hull wears only while the engine is cold | first pass's own offered answer, no source | lost | A second rule on top of the weather; he called hull wear *"easy"*. (The plain wear does have a source, which the first read missed: the review's etch scars, in the second reader's rows.) | Take it: the cover itself becomes what costs, at the price of a rule the player has to be told. |
| Raid, get hot, go dark and cold, wait, come back up | hiding note | kept as the Abyss's place in the campaign's rhythm | | |
| Hiding under water; the drowned cavern under polar night; the Deepwater Compact as gatekeeper | hiding note | lost from this design | Not the Abyss; it belongs to the seas. | Carry it into the first sea biome's rewrite. |
| Underwater as vacuum for breathing | hiding note | lost from this design | Same. | Same. |
| The whole hiding loop was second-version in August | hiding note | lost (overtaken by his 2026-09-30 ruling and the build) | | |
| The sensor shadow: the place to run to | sheet §7 | kept, quoted | | |
| Refuges at twenty to thirty days | pursuit note | kept | | |
| The fourfold pursuit delay on a list of biomes | pursuit note, review slate 5 | kept (built) | | |
| Forty to sixty-four days between rungs for a hidden crew here | ladder | kept, quoted | | |
| A refuge is a slower ladder, never a frozen one | ladder | kept | | |
| A landed ship here is hidden; trade and pursuit scans fail; the engine breaks cover | review slate 5, ship item | moved (0.2.0 → 0.1.0), except trade | See above. | |
| "Yes but probe droids will still come that must be avoided" | review §7 (his words) | moved with it, quoted | | |
| How to beat a probe: still, cold, dark, or shoot it first | ship item | kept | | |
| A reported probe collapses the cover | ship item | kept; the search returning to ordinary pace is stated and unverified | | |
| Cover builds with few lit lamps | cleanse census | kept as the central bargain | | |
| The free tier gets no ship touch | review §12 | kept | His card. | |
| A free-tier "raids take longer to find you" or "hunted by light-eaters" ship | review §11.2 | lost (declined) | | |
| Starting the engine tears the mask away | review (consult) | kept | | |
| Probes are existing droid content, no new art | cast bible §4G | kept | | |

### Creatures and plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The admission test: live by the Dark, or trade in light | cast bible §2 | kept | | |
| One transplanted nocturnal family, suspiciously well placed | sheet §4 | kept | The cryptid's shared line. | |
| The soft sibilant names are for the Abyss's black, many-eyed creatures only; pitch black with yellow eyes | cast bible rulings 18, 19 | kept | His words. | |
| Gharrek: opens on every gust, map-wide | cast bible, review §4 | kept; also the landing's first sight | | |
| Gill-ash as a second fuel | cast bible | lost (recommended for dropping; his to confirm) | Tholin does the job. | |
| Durrgak, the sorter: arranges things; tamed, it tidies | cast bible | kept for tidying; rings, dens and caches stay 0.2.0 | His approval. | Rings in 0.1.0: the first "someone was here" on day one. |
| Krizzak, the moth that eats light | cast bible | kept | | |
| Etchcap, only in etch-hollows; a delicacy | cast bible | kept | | |
| Tholin: swept residue that refines to fuel | cast bible, review §8 | kept; named as the Abyss's richer fuel source, spent by the hide's own heaters | His fuel ruling of 2026-11-18. | |
| "Chemfuel-adjacent industry from air" | sheet §7 | kept, quoted | | |
| Tholin collects in rings at the edges of warm clearings | review (consult), cast bible | lost | Not found built; the cleanse does not carry it. | A pretty tell that ties heat to harvest. |
| Cindermare (now saevitha): mouthless, kills by grip, draining warmth | cast bible §4B | kept | | |
| Skarnix (now ishvarith): will not cross firelight | cast bible §4B | kept | | |
| Summ, the storm giant: the thunder is its voice | cast bible §4C, §6A | kept as an ordinary great beast; the storm call is 0.2.0 | His approval. | |
| "A storm does not bring the summ; the summ brings the storm" | cast bible §6A (draft lore) | kept, quoted, marked as draft | | |
| Summ regenerates; hurt by daylight; sees in the Dark | cast bible ruling 12 | kept in 0.2.0 | His approval. | |
| The summing that never stops growing | cast bible §4C, review §16 (his words) | kept in 0.2.0 | | |
| Drokattak (now ombrathia): the quill hackle before the lunge | cast bible §4C | kept | | |
| It does not throw quills | cast bible | kept | | |
| Alien megafauna, never a fantasy dragon | cast bible ruling 9 | kept as a ban | | |
| The brood-mother, landscape-sized, unkillable once woken | cast bible §4D | kept in 0.2.0 | | |
| Greed wakes her: one meter fed by light, noise, theft and salvage | cast bible §4D | kept in 0.2.0 | | |
| The egg; it bonds only with a great bone aboard | cast bible §4D | kept in 0.2.0 | | |
| The storms follow a stolen egg home | review §9 | kept in 0.2.0 | A consequence that travels with the ship. | |
| The bone field; bone as stuff | cast bible §4D | kept in 0.2.0 | | |
| The tamed beast as bane and boon, killing wildlife | cast bible §4D | kept in 0.2.0 | | |
| The Ship in the Wall; the ship takes only some parts and says so | review §9 (his words), cast bible §4D, §6B, §6C | kept in 0.2.0, quoted | | |
| The four Lightfall options not picked | review §9 | lost (not chosen) | | |
| The darkbeast (nevarithia): wears a halo of Dark | sheet §4 | kept as an animal; the halo and its release are 0.2.0 | Unbuilt; his approval. | |
| The dusk rat: named for its behaviour, never its look | sheet §4, cast bible §4F, names doc | lost (corrected by the second reader: he cut it on his sheet of 2026-10-05, *"No longer needed, cut."*) | The first read had it as an art debt. | |
| The donor cast kept under invented labels | cast bible §4F, roster json, names doc | kept | | |
| The frostling joins this roster | sheet "Owed" | lost (corrected by the second reader: it was admitted, then cut by him on 2026-10-05, *"cut. no longer needed."*) | | |
| The herd, pack and milk animals; the scavenger; the fast egg-eater; the toxic predator | cleanse census | kept as ordinary life | | |
| Their bespoke behaviours not yet built | cleanse | kept in 0.2.0 | | |
| Chemotrophy on the mixing boundary; life keeps the gust rhythm | sheet §4 | kept as the gharrek | | |
| The light-makers as the farmers' infrastructure | sheet §4, §7 | kept, reshaped: for a hiding crew the farm's light is also its exposure | | |
| The lamp crop (wickwood) | cast bible §4E, review §8 | kept | | |
| Giant glow globe as a found sunlamp; glow globes; glowing grass | sheet §4, cleanse | kept | | |
| Glowberries; a picked berry as a carried light | sheet §4, cleanse owner marks | kept (his mark) | | |
| Vines that turn to light | cleanse owner marks | kept (his mark) | | |
| The fishery of weird dark creatures, alive in the pools | cleanse owner marks | kept (his mark) | | |
| Glow-globe poison; fungus spores | cleanse | kept in 0.2.0 | | |
| Ultima fibres | sheet §7 | kept, reshaped: ordinary cloth from the vine, no premium fibre | The cleanse's reading of the built plant. | |
| The gourmet line as named cuisine | sheet §7 | kept as etchcap; a named cuisine is campaign | | |
| Grown light deferred as an echo of other biomes | review (consult) | lost (he kept lamp crops) | | |
| The taozin as a rare campaign animal | cleanse census | kept in the campaign layer | | |
| Real flight for the moths; never live-tested without him | cast bible | kept | Standing rule. | |

### The cryptid, the rites, the people

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The Nhaleth come for the Dark and are never seen | sheet §8, cryptid spec | kept; never on screen in any version | | |
| The campaign's whisper: the Sith, never the Rakata | cryptid spec (his correction) | kept in the campaign layer | | |
| The free whisper: they are whoever stays | cryptid spec §3 | kept in 0.2.0, quoted | | |
| Signs that can always be explained away | cryptid spec §4 | kept in 0.2.0 | | |
| The unwatched exchange | cryptid spec §4 | kept in 0.2.0 | | |
| A clear pocket around nothing | cryptid spec §4 | kept in 0.2.0 | | |
| The dream after a long stay | cryptid spec §4 | kept in 0.2.0, quoted | | |
| Tales and art that show them unseen | cryptid spec §4 | kept in 0.2.0 | | |
| The name lives in one rule pack; defNames stay neutral | cryptid spec §5 | kept as a build fact | | |
| Four rites taught by the deep dark, performable anywhere dark | review §13, §14 (his words), cast bible §6D | kept in "later", campaign layer (corrected by the second reader: he deferred every biome rite to a second version on 2026-10-23) | | |
| "Biomes teach rites as well as tech" | review §14 (his words) | kept as a programme principle; not this design's | | |
| The Veil Vigil at a cairn during an Unveiling | review (consult) | lost (superseded by the four) | | |
| Fugitive holds | sheet §8 | kept in "later" | See above. | |
| Wind farms, working and wrecked; spare-part shrines | sheet §8 | kept, reshaped: wrecked only, as the salvage field | | |
| Seep-works | sheet §8 | kept in "later" | | |
| Rumour sites | sheet §8 | kept in 0.2.0 with the cryptid | | |
| Learning heat-folding by watching warm air | review §12, cleanse | kept in 0.2.0 (his *"determination later"*) | | |
| The fold lamp | review §12 | kept (his mark) | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (Dark, living light, warmth, light-feeders, grain as fuel) | cleanse definition, owner pages | kept as the body of 0.1.0; the hidden ship added as what it is all for | | |
| The cleanse's runner-up: the hidden ship and probes | cleanse definition | moved (0.2.0 → 0.1.0) | | |
| His four marks | cleanse owner marks | kept exactly | | |
| The cleanse's one question (outdoor pockets) | cleanse owner pages | kept, carried | | |
| Its defaults on what the Dark hides, what recovers in warmth, what an Unveiling clears | cleanse owner pages, ambiguities | kept | | |
| Three retirement recommendations | cleanse owner pages | kept as recommendations | | |
| Fifty-one tickets, four models | cleanse | kept as they stand; the ship's switch-off ticket no longer applies if the move stands | | |
| Etchfall is the "staying too long wears at you" half of his line | fluff cuts | kept, quoted in spirit | | |
| What has and has not run live | mechanics review | kept as build facts | | |

### Rows added by the second reader

More source names: *owner answers* = `design/RimMandrake/designer_codex_2026-11-09/Abyss/ANSWERS_OWNER.md`; *codex notes* = `NOTES.md` and `QUESTIONS_OWNER.md` in the same folder; *owner plan* = `design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.md`; *freeze rulings* = `design/Jawa/worldbuilding/biomes/_freeze_rulings_2026-09-07.md`; *rites file* = `design/RimMandrake/v2_nine_rituals.md`; *lightfall item* = `ABYSS_LIGHTFALL_BROOD_WRECK_1`; *sheet port item* = `ABYSS_SHEET_DONOR_PORT_1`; *dark item* = `ABYSS_DARK_BUILD_1`; *muffle item* = `ABYSS_DARK_MUFFLE_ALL_SOUNDS_1`; *beasts item* = `ABYSS_DONOR_BEASTS_FREED_1`; *cryptid item* = `ABYSS_FREE_CRYPTID_1`; *rename item* = `ABYSS_FULL_RENAME_1`; *body item* = `ABYSS_FREE_TIER_BODY_1`; *sitting item* = `BLACKCRAGS_BEDAZZLE_SITTING_1`; *marks item* = `RIMMANDRAKE_FOLD_OWNER_MARKS_INTO_ABYSS_AND_ROT_PROPOSALS`; *flora items* = `DARK_FLORA_FIX_WILTS_WITHOUT_A_SUN` and its verify sibling; *face item* = `WORLD_FACES_REDRAW_ABYSS_ROT_RUST`; *contributions item* = `BIOME_SHIP_CONTRIBUTIONS_1`; *creature items* = the closed build items for the gharrek, durrgak, krizzak, etchcap, etchfall, fold lamp, lamp crops and soundscape. Items are under `infrastructure/state/items/` or its `closed/` folder.

#### His words that had no row

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| *"Searches interrupt work: ordinary work is safe between searches, but exposed activity becomes dangerous while a search probe passes."* | owner answers (card, 2026-11-10) | kept, quoted: it is the rule of the hide | His own answer on "keeping a hidden colony working", a week before the cleanse deferred probes by a delegated call. The first read never opened this file. | Leave probes at 0.2.0: his card of 2026-11-10 then has nothing in the first version. |
| *"Wonder draws you out: beauty offers something worth approaching, then leaves you exposed when darkness returns. Shelter remains worth choosing, while wonder tempts the crew beyond it."* | owner answers (card, 2026-11-10) | kept, quoted, in the Unveiling | The design had the Unveiling as a view. He ruled it a temptation. | |
| *"Danger becomes more frequent: close threats and frightening reversals gradually leave fewer peaceful stretches, giving a practical reason to depart at the cost of breathing room."* | owner answers (card, 2026-11-10) | kept, quoted, as what ends a long hide; its version is a question for him | Nothing built makes danger more frequent with time, and no source says how. It is his answer to "why staying becomes frightening" and the design had only the dream. | Treat the cryptid's signs as this: they are 0.2.0 and are signs, not threats. |
| *"Please take these now as THE PLAN going forward."* | owner plan (2026-11-17) | kept as the starting scope | | |
| *"It's not that big of a deal to make some creepy dark critters to fish for."* | cleanse owner marks; marks item | kept, quoted | | |
| The creepy fish, as the cleanse drew them: veiljaws (black ribbon swimmers with pale hinged jaws and blind pits) and suturefins (flat bottom swimmers with a pale stitch-like seam), in mineral-fed pools | cleanse definition | kept, now named in the design | Delegated designs under his mark. | |
| His first idea of this biome was the sea floor: *"a pitch black Alpha Biomes biome already that is very alien and strange and almost perfect to pretend is at the bottom of the ocean... 'go to that biome' when we try to land on water instead."* | hiding note (owner, 2026-08-13) | lost (superseded) | The sheet of 2026-09-06 made it a highland and the seas got their own seabed. It is why this pilot's brief called the Abyss a sea. | |
| *"...allowing them to under the (admittedly very small) bodies of water or into the permanently dark terrain is pretty cool! In fact, maybe we should combine both of those concepts…"* | hiding note (owner, 2026-08-13) | kept for the dark half; the water half is the seas' | | |
| "They are small and overlooked, and being overlooked is the thing they are actually good at." | hiding note | kept, quoted in "What this place is" | The best sentence anywhere on why Jawa hide. | |
| "Hiding must cost the thing the campaign is about — salvage and progress — not hit points." | hiding note | kept, quoted beside the hull wear | The hull wear he ruled on 2026-11-18 costs plate. The design keeps both: the wear is slow, answerable by hand, and never the main price. | |
| "The player should sit there watching the heat bleed off and feel the weeks they are not earning." | hiding note | kept, quoted | | |
| What may erode in a hide: *"stores, mood, the water itself, or the Empire narrowing its search"* | hiding note | kept; the design uses stores, the hull and (by his card) rising danger | | |
| "You are unfound, which is different" | hiding note | kept, quoted | | |
| Permanent dark is *"worthless ground"* that nobody owns; its cost is isolation | hiding note | kept | | |
| Hide and stay poor, or cut the Empire's towers and grow hotter: two opposite answers to pursuit | hiding note | lost from this design | The sky ladder is campaign structure. | A line in the campaign document. |
| Hiding as the way Imperial Heat decays | hiding note | lost | The Heat gauge is unbuilt; the visibility dial took its place. | |
| The under-water depth table (unreachable costs trade, quests and contact) | hiding note | lost from this design (the seas') | | |
| *"I had thought around every 5-8 days, keep 'em running"*; refuges *"and possibly some others, and even in distant v2 maybe on the ocean floor for a sealed ship"* at 20 to 30 days | pursuit note (owner, 2026-08-28) | kept, quoted | | |
| The Empire also raids as an ordinary storyteller enemy, on top of the pursuit | pursuit note (owner, 2026-08-28) | kept as `UNMEASURED`: whether the shadow slows those raids | The built delay is on the pursuit's own timers. | |
| The pursuit arrives by orbital drop; a second wave twelve hours after the first, then waves every three hours | pursuit note | kept as build facts | It is what "a probe that got its report out" eventually costs. | |
| *"Actually I want to call it the Abyss. And do the full rename in content, code, def, mod, and put it all in the consolidated biome mod now."* | rename item; review §7 | kept, quoted | | |
| *"I chose Forsaken and Forgotten myself, independent of the mod... So we keep those for the Rakatan."* | review §10 (owner, 2026-10-01) | kept as a campaign naming rule | | |
| *"For the Star Wars part we had already written rumors... For the free version we would make our own. Do so."* | cryptid spec §1; cryptid item | kept | | |
| The whisper in full: *everyone who lived in the Dark long enough stopped needing light, stopped coming home, and now comes back only to tend the places they left* | cryptid spec §3 | kept in 0.2.0, quoted | | |
| The name: the opening *nh-* is a hush, *the sound someone makes when they don't want to say a word out loud*; spares Ommerai, Sennoth, Thessuin | cryptid spec §2 | kept | | |
| Why no invented race with a history: *the player's own colonists are the one subject every player already cares about* | cryptid spec §3 | kept as the reason | | |
| The exchange never happens while anyone can see the circle; its letter says *something took it and something was left* | cryptid spec §4; cleanse | kept in 0.2.0 | | |
| Never owed: a body, a raid, a quest giver, a reveal | cryptid spec §4 | kept as a ban | | |
| The fear that they are the Nightbrothers: *"merely whispered, to ensure they do not come to pass"* | sheet §8 | kept in the campaign layer | | |
| The Nhaleth as *"this planet's Loch Ness monster, its Bigfoot"* | sheet §8 | kept, quoted | | |
| The droid who told the story of the Forsakens tells of the Nhaleth | review §10; cryptid spec §8 | kept (done; a deploy owed) | | |
| Older lore files that tie the cryptid to the Rakata | cryptid spec §8 | lost (wrong by his correction; listed there for fixing) | | |
| *"Fully regenerate art and names for those two beasts. No donor dependencies tolerable. Free us."* | beasts item; review §8 | kept, quoted | | |
| *"Summ the All-Render, with the lesser forms of it other Summ creatures."*; *"Drokattak"* | review §15 | kept | | |
| *"Summing for the little one. (Not so little ) the brood mother must be landscape sized. And the little one should be constantly growing problemmatically."* | review §16; lightfall item | kept in 0.2.0, quoted | | |
| *"We must be careful with those dragons to make sure they don't turn into fantasy dragons. They must remain starwars-esque beasts from an alien world... get too greedy to steal from the crashed ship, and you wake an essentially unkillable thing."* | lightfall item (owner, 2026-10-01) | kept in 0.2.0, quoted | | |
| *"It's ok to require load/save to learn the boundry, that's pretty normal in these games."* | lightfall item | kept in 0.2.0 | A waiver; never re-asked. | |
| *"Perhaps you MUST have one of those great bones on your ship in order for the beast egg to bond with you?... a bane and a boon... UV sensitive but able to see in darkness."* | lightfall item | kept in 0.2.0, quoted | | |
| The ship quote's last lines: *"This is a chance to restore much of its glory. While the sleeping dragons threaten to pummel you."* | lightfall item; review §9 | kept in 0.2.0 | | |
| *"You draft three items. Then ask gpt to make three unrelated ideas. Make them spectacular."* | review §8 | kept as how Lightfall's bottom was written | | |
| Read the summ like a krayt, a rancor or a zillo: a biology, not a heraldry | lightfall item; cast bible §2 | kept as art direction | | |
| *"Those new smooth names are for Abyss creatures of the black style with multiple eyes uniquely. The 'possibly of Sith origin' type."* His examples: Assith, Seratha, Manolithia | sheet port item; cast bible ruling 18 | kept, quoted | Never used for another biome. | |
| *"Make hide pitch black with four glowing yellow eyes"* | sheet port item; cast bible ruling 19 | kept | | |
| The made lineage: each of the black kin reads *"less evolved than made, as if some old and patient cruelty once had the shaping of it"* | sheet port item | kept, quoted in the design | The first read named the family and not what its descriptions say. | |
| The eight ported kin by name and nature: sesserith, olumetha, aveluthia, lirrith, moravatha, ossumatha, ysvaltha, nevarithia | sheet port item | kept | The first read listed them by role only. | |
| The aveluthia *"still bows its head to a hard voice"*; the moravatha hauls *"as if it remembered whose it was"* | sheet port item | kept, quoted | | |
| The ossumatha's rage: *"a weapon someone once made and then lost"*; the ysvaltha: *"few who see one see it twice"* | sheet port item | kept, quoted | | |
| A lirrith pack strips a camp's stores *"in the time it takes to light a lamp"* | sheet port item | kept as description; ordinary scavenging only | | |
| His plant notes: glow globe *"great idea. Make twice as big."*; the paddle vine's first art *"looked like bad computer art"*; glowing grass *"More realistic, more variations."* | sheet port item | kept as art rulings | | |
| The plants he named plainly: glow globe, giant glow globe, sickly glow mushroom, paddle vine, giant fibre stalk, tree mushroom, glowberry bush | sheet port item | kept | | |
| The paddle vine's *fine faceted photoreceptors, like the eye of a fly* | sheet port item | kept, quoted: it is why the vine turns | | |
| The tree mushroom is *"the nearest thing the Abyss has to a forest"*; glowberries *"glow like embers held in the hand"* | sheet port item | kept, quoted | | |
| "Nobody eats one twice" (the glow globe's flesh) | sheet port item | kept as description; the poison itself is 0.2.0 | | |
| Cut by him on his sheet of 2026-10-05: the dusk rat (*"No longer needed, cut."*), the frostling, the night ave, the sand prowler (*"doesn't belong here"*), the shadow charger, the thunderox | roster json; sheet port item | lost (cut by him) | The first read had the dusk rat as an art debt and the frostling as lost for want of a source. | |
| The tellurox is livestock, not wildlife here; the Earth rat goes; twenty-three other animals turned away | roster json | lost (ruled or evicted, each with its reason) | | |
| The roster's old ruling of no fish (acid in the water, nothing sun-fed) | roster json; review §4 | lost (overtaken by his mark of 2026-11-17) | The new fish live on mineral film, not on sky light. | |
| *"There are no eclipses on this planet."* | review §13 (owner, 2026-10-01) | kept: the nevarithia's death looses its knot of Dark, never an eclipse | The donor animal's death darkened the sky. | |
| His rites rulings: rites that *can be done in absolute darkness*; *"you don't just discover tech in the biomes you discover new rites"*; part of the Salvation suite | review §12 to §14 | kept in "later" | | |
| *"All 'rituals' to interact with the Nine that are based on unique Baroque Biome content are hereby documented and deferred to v2."* The four Abyss rites are in that register | rites file (owner, 2026-10-23) | moved (0.2.0 → later) | The first read put the rites at 0.2.0. He deferred every biome rite to a second version. | |
| The other three inscriptions: the Dark Vigil (*"Do not speak until the dark speaks first."*), the Blind Offering (*"What is taken is paid."*), the Lightless Burial (*"We were more once. Bury that with them, in the dark"*) | cast bible §6D | kept in "later", quoted | | |
| If the dark breaks mid-rite it fails and the hungry god answers; a rite can be held in any sealed, unlit room | review §13 | kept in "later" | | |
| The Veil Vigil's belief, *"the Dark is a veil"*; a lifelong memory of having seen an Unveiling | review §11.2 | lost (not chosen 2026-10-01) | | |
| *"Abyss I had envisioned as far darker still with eerie swirling within it."* | face item (owner, 2026-10-20) | kept as art direction for the world map | | |
| *"You know all the biomes are being moved into a single Baroque Biome mod that WILL take harmony, right?"* | muffle item (owner, 2026-10-09) | kept as a build fact | | |
| *"how can this biome uniquely add something to the ship?"* The Abyss's recorded answer is the great bone | contributions item (owner, 2026-09-24; the row is delegated) | kept in 0.2.0 | "The gravship becomes a scrapbook of everywhere it has been." | The fold lamp as the gift: a judge dropped it because three biomes gave a heater. |

#### The ship, the hull and the hide

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Etch scars: etchfall wears the ship's hull fittings and leaves a visible scar that stays, *"I was in the Abyss"*; *sweeping the tholin off pays for some of the repair* | review §11.2 (mark 6, option b) | kept, reshaped: the wear and the sweeping are in 0.1.0 by his ruling of 2026-11-18; the lasting scar is a question for him | It was put to him on 2026-10-01 for the free tier and he chose no free-tier ship touch. The first read believed no source had the grain on the hull. | Add the scar: one overlay and a tag that travels. |
| A scar that means something, *a small stealth bonus at night anywhere* | review §11.2 | lost (never offered on the card) | | |
| Moths drawn to the ship's own lamps, each smothered lamp lifting the mask | review §11.2 (mark 6, option a) | lost (not chosen 2026-10-01) | It was the free tier's hide. Listed under NEEDS HIM, not revived. | |
| Cold-burn cells: a heatless lamp from gill-ash and tholin, *the stealth light... it pairs with hiding the ship* | review §11.2 (mark 2, option c) | lost (not chosen 2026-10-01) | Listed under NEEDS HIM, not revived. | |
| Light-grafting glow onto any tree | review §11.2 (mark 2, option b) | lost (not chosen 2026-10-01) | | |
| The terminator's weather makes *"the ship damage"* | freeze rulings R4 (owner, 2026-09-07) | kept: it is his own source for the rough way in | The first read sourced the approach wear from the sheet's wind alone. | |
| The planet's winds close at the Stormwall; *"ends at the crags"* is wrong | freeze rulings R4 | kept as a correction to the sheet's line that the great cycles end here | The crags shatter the local surface wind; the circulation does not end in them. | |
| Tholins as *"unharvestable — a similar keyword, not a fuel"* | freeze rulings R5 (2026-09-07) | lost (overtaken by his card of 2026-10-01: etchfall leaves tholin that refines to fuel; built) | His later decision wins. | |
| The wreck's fittings repair worn ship structure: hull plating, conduit loom, thruster liner, seal gaskets | lightfall item (built 2026-10-07) | kept in 0.2.0, and named in the design as the Abyss's own repair for an etched hull | | |
| The ship refuses three parts in plain words: the bridge console, the foreign lattice, the rescue berth | lightfall item | kept in 0.2.0 | | |
| The ship's refusals: *"The ship will not take this. It does not want to be something else."* *"It knows its own shape."* *"Something in the old frame settles, as if it remembered."* | cast bible §6B | kept in 0.2.0, quoted | Drafts in use; his edit pending. | |
| The wreck's story: *"It came down into Lightfall after someone, and it is still here. Whatever it came for, nobody climbed out with it."* | cast bible §6C | kept in 0.2.0, quoted | | |
| The wake meter as built: cuts, the egg and each lit lamp near her; a stir, then a rumble, always before the wake; quiet days bleed it off | lightfall item | kept in 0.2.0 | | |
| The egg can be put back at the lip | lightfall item; cleanse ambiguities | kept in 0.2.0 (built as "near her coils"; the lip is owed) | | |
| A stolen egg at home calls a storm every few days and a hunting summ after it | lightfall item | kept in 0.2.0 | | |
| The biology draft: *"an egg must lie a year in perfect dark to hatch. Sunlight burns them. They see by the faint glow of their own throats."* | cast bible §6A | kept in 0.2.0, quoted | | |
| The draft says the Dark at Lightfall's bottom *"has never once lifted"*; the sheet says Lightfall is *"the one place the Dark always dies"* | cast bible §6A; sheet §3; cleanse ambiguities | kept as a question for him | Two of his approved texts disagree. | |
| Three probe kinds exist to draw on; *"hidden is not safe"* | ship item | kept | | |
| The cover as built: few lit lamps anywhere on the map build it, noise wears it, a report or its expiry starts a cooldown | cleanse census; codex notes | kept, stated in the design | | |
| The cover counts only built lamps that are lit; light that grows is not counted | codex notes; `RM_MapComponentShipCover.cs` (read by the second reader) | kept, and the design's central bargain is corrected to it | The first read wrote the lamp-tree farm as what costs cover. As built, living light is the hide's free light. | Count living light too: the farm-against-cover bargain the first read described, and a poorer hide. |
| The cover wears thin by itself and can be rebuilt after a few days | `RM_MapComponentShipCover.cs`; cleanse census | kept, stated | *"It must not be permanent."* | |
| The engine starting does not yet break the cover; only the engine's absence resets it | cleanse census; codex notes | kept as a known gap | The design said this was built. | |
| Nothing outside the Abyss reads the cover: the pursuit looks only at the biome | cleanse ambiguities; codex notes | kept as a known gap | *An internal covered meter cannot prove dynamic protection.* | |
| The built probe finds lamps and moving crew by distance alone, through walls, and does not read heat | codex notes; cleanse census | kept as a known gap; "cold" comes out of the design's list of what beats a probe | | |
| A free-tier stand-in probe exists (a mechanoid scout) | codex notes | kept as a build fact | | |
| "No orbital eyes" means nobody can see the ship; a radio call to a trader is not seeing | cleanse ambiguities | kept | | |
| The cleanse's reason for deferring the hide: *a separate stealth game* | cleanse owner pages | lost as a reason (his card of 2026-11-10 names the probes; the question stays his) | | |

#### The place, the Dark and what lives in it

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The Dark is *not unique to this world, only rare in the galaxy* | sheet §2 | kept, quoted | It is why visitors would come. | |
| The Dark is aurora-ash, made over the night pole and *combed out here* | sheet §3 | kept as lore | | |
| "The Dark does not leave — it folds up." | sheet §3 | kept, quoted | | |
| Lightfall, named by him: *where light falls in* | sheet §3 | kept | | |
| *"Whatever generations of the desperate have lowered into it"* | sheet §8 | kept in 0.2.0, quoted | | |
| "A gust is a meal, a stillness is a fast." | sheet §3 | kept, quoted with the gharrek | | |
| "Light is the currency." | sheet §5 | kept, quoted | | |
| *"Lit like a harbor at night, by its own lamps"* | sheet §1 | kept | | |
| "A warm base is a seeing base, and a cold one is blind"; in this cold *that ties vision to fuel* | review §5; dark item | kept, quoted | | |
| "The best single idea on the planet, light as a thing the air eats" | review §3 | kept, quoted | | |
| "Every other biome's rare weather is a hazard. This one is a gift." | review §5 | kept, quoted in the Unveiling | | |
| Grain falls harder during an Unveiling | cleanse census | kept (built) | The beautiful hours cost plate. | |
| An Unveiling does not show unexplored ground and is not sunlight | cleanse definition | kept | | |
| Etchfall *falls where the Dark dies*, so heat brings it down on you | review §5 | lost | Built as weather over the whole map. | Tie grain to warm clearings: the hide's heaters would wear the hide. |
| Destroyed rock leaves an etch-hollow, the only ground etchcap takes | cleanse census; creature items | kept (the fungus's ground rule is owed: it grows on plain sand today) | | |
| The gharrek: dinner-plate sized, prey for the hunters in a gust, dormant and slowed in the still | cast bible §4A; creature items | kept | | |
| The sorter tidies by hauling and by eating filth; the Jawa *"say it learned it from someone"* | review §4; cleanse census | kept | | |
| The moth *holds a faint stolen glow*; it takes light, never power or hull | cast bible §4A; creature items | kept | | |
| The ishvarith answers light only; the old line about heated space is not built | cleanse ambiguities | kept, reshaped: the design says light, not heat | | |
| The quill rattle fires when the hunt begins, perhaps out of earshot | cleanse ambiguities | kept as a known gap (the close tell is owed) | | |
| Glowing grass does not yet give light; the glow globe still needs some sky | cleanse census; flora items | kept as known gaps | | |
| Night-side plants need no light at all to grow | flora items | kept (fixed in source) | | |
| No renderer of the Dark exists yet, only a sky colour; no black etched rock was found built | cleanse tickets | kept as known gaps | The first minutes describe what is owed, not what runs. | |
| The summ feeds on the charge the Dark carries; its throat-sacs glow storm-violet | cast bible §4C | kept in 0.2.0 | | |
| The darkbeast's halo was never put on a card | cast bible §1 | kept in 0.2.0 as the cleanse placed it | | |
| The soundscape: *silence by default, each gust an impact; gill-fans rustle, grain ticks, dying lamps clatter* | creature items; review §12 | kept, quoted | | |
| Sound is judged only with him present; muffling ships on by his card | muffle item; cleanse bars | kept as rules for whoever builds | | |
| A canon predator and its nest join in the campaign | cleanse census | kept in the campaign layer | | |
| His card that the Abyss is the crags he meant for that canon predator and its nest | codex notes (its record, owner card of 2026-10) | kept in the campaign layer | | |
| The first crag names, *said in a gust*: vrakk, dhukk, hulggarok, kessik, gruzz, shekkur, ulkhorr and the rest | names doc | lost (overtaken by his smooth names of 2026-10-05; the art drawn under them is superseded too) | The first read's row says the donor cast was kept under invented labels; these are not those labels any more. | |
| The lirrith also lives in the Cracked Lands | cleanse definition | kept (two homes recorded, no eviction) | | |
| The body the free tier was owed: its own labels, its own weather names, its own flora | body item | kept (done or carried by the port) | | |
| The old tile gate, the scorecards and the nine marks | review §2, §3, §11; sitting item | lost | A scoring programme and a rename check. | |
| The cleanse's four instruments and fifty-one tickets, read to the end | cleanse | kept as they stand | | |

#### Rows added when the part-read files were read to their end (second reader, continued 2026-11-18)

More source names: *rites register* = `design/Jawa/salvation_rites_2026-10-01.md`; *rites pass* = `design/Jawa/biome_rites_pass_2026-10-01.md`; *salvation item* = `SALVATION_RITES_UNIFICATION_1`; *gated item* = `CONDITION_GATED_RITUALS_MOD_1` (closed); *codex record* = `record.json`, *codex questions* = `QUESTIONS.md` and *codex brief* = `designer_brief.md`, all three in `design/RimMandrake/designer_codex_2026-11-09/Abyss/`; *crags items* = the closed items filed under the biome's older names, `FORSAKENCRAGS_RM_MOD_BUILD_1`, `FORSAKEN_CRAGS_FAUNA_1`, `FORSAKEN_CRAGS_PREDATORS_BUILD_1` and `LIGHTFALL_CHASM_AUTHORING_1`. The census is `design/concepts/Abyss/cleanse/census.json`, cited as before under "cleanse census".

##### The rites the deep dark teaches (all "later", by his ruling of 2026-10-23)

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| *"This mod is going to be specific to the utinni scenario. Just make a discoverable rite here in the deep dark that they can perform later. That's the discoverable tech, or one of them anyway."* | gated item (owner, typed, 2026-10-01) | kept in "later", quoted in the design | His own word that a rite is one of the things a crew carries away from the Abyss. The first read had the rites and not this sentence. | |
| Where each rite is found: the Dark Vigil at *the inscription where no light has reached*; the Blind Offering at the Nhaleth circle; the Snuffing at the ring of dead lamps; the Lightless Burial at the rescue ship in Lightfall | rites register B2 | kept in "later", named in the design | Four places a crew in hiding would walk past. | |
| Which god each rite moves, and how: the Vigil feeds Ishko by stillness; the Blind Offering settles a debt with Mob'Unloo; the Snuffing starves Sh'kaar; the Lightless Burial consoles Ozzik (*for now*, to be re-balanced) | salvation item; rites register §c | kept in "later" | | |
| Sh'kaar is *fed by light cast into darkness* and starved by *"staying dark, hidden, and unfought"*. "The only appeasement a hungry god accepts is to be denied." | rites register §c3 | kept in "later", quoted in the design | It is the hidden ship said in the campaign's own religion. The design had the Snuffing's inscription and not the reason behind it. | |
| The Snuffing makes the dark the other three rites need, *"so it is a colony's way in"*. Done well, *"the clan has hidden from him; fewer and later brute attacks"*. Failed, it is *"the clan lighting a night-rite in front of the god it was hiding from"*. | rites register §c3 | kept in "later", quoted | | |
| Ta'Baa, the god of flight, and Ishko, the god of concealment, *"reconcile in exactly one posture, hidden and watching for the instant to flee"* | rites pass §8.2 | kept, quoted in "What this place is" | The best single sentence on what a hidden ship is doing, and it sat in another biome's rite. | Leave it there: it goes when that file goes. |
| The dark itself always moves Ishko up and Sh'kaar down: *"together the two make darkness doubly sacred"* | rites register §c | kept in "later" | | |
| The Dark Vigil in detail: an organiser and three still watchers, two hours, no light carried; a poor one is *"a long cold sit"*; a good one leaves Ishko's mark on the wall and lifts the dark's mood penalty for a season; repeated fine vigils count toward *"terraform the dark itself into a home"* | rites register §c1 | kept in "later", quoted | Ishko *alone does not punish a skipped rite*. | |
| The Blind Offering in detail: name a debt, lay an item on a ring in the dark, everyone leaves; by morning *"it was not taken"*, or it is gone, or gone and replaced by *something small and strange*, never silver. *In the Abyss this is the Nhaleth exchange, never confirmed.* | rites register §c2 | kept in "later", quoted | The built unwatched exchange (0.2.0) is this rite's body. | |
| The Lightless Burial in detail: *"the grave is the deepest dark"*; Ozzik under his pride is grief, *"we were once great, and we cannot bear the memory"*; a grave cut into rock and closed before any light returns; the dead *"went unseen"* | rites register §c4 | kept in "later", quoted | | |
| The Unlit Wedding: the wedding held in absolute darkness, the canon *"mate only in total darkness"* made pious; the memory *"married in the dark"*; unlocked by learning any darkness rite | rites register §c5; rites file | kept in "later" | The first read had four rites. There is a fifth thing, a variant, deferred with them and with no queue item of its own. | |
| Dark variants of the wedding and the funeral take no ritual slot (his card of 2026-10-01); the old claim of six ritual slots was false | gated item; rites register §a | kept in "later" | | |
| How a rite is found: an inscription studied in place and in the dark (*a lamp brought to read it spoils the study and is a lit night-rite*); the study yields a rubbing; the letter reads *"The stone said what to do. It did not say who carved it."* | rites register §d | kept in "later", quoted | | |
| The reason shown while a spot is lit, *"The spot is not dark: 34% light"*; a setting to count the Abyss's Dark as absolute darkness; the greyed row *"A rite the dark keeps."* | rites register §d | kept in "later" | | |
| A Dark Vigil held at the rare wrong ring moves the lore toward the Sith whisper: *"a voice that is not one of the nine"*; it never becomes a visitor | rites register §f | kept in "later", campaign layer | | |
| A darkness rite at the ship's shrine-heart puts the ship's lamps out first, so the gods' council *speaks out of the black* | rites register §f | kept in "later" | A ship idea nobody has ruled on; it needs the unbuilt voice layer. Not a promise of any version here. | |
| The rites' home is the Salvation Rites mod; a Salvation crew cannot learn another faith's rites; five found rites a god at most, and with the Abyss's rites Mob'Unloo and Ozzik are at that limit | salvation item; rites register B11, B15 | kept in "later" | | |
| The name "the Unveiling" collides with the campaign's "nine unveilings"; neither is renamed | rites register ("Still open") | kept as a known open naming question | Nobody has asked him. It is listed in the design beside the Unveiling. | |
| His deferral also ordered every built rite removed, *"including art"*. Nothing of the Abyss's rites was ever built, so nothing was removed; they were first tabled on 2026-10-03 (*"table the rites until the biome mod is fully complete and checked out"*) | rites file | kept as the record | | |
| Ishko's wall-mark outcome, built for the Dark Vigil, stays in the game with nothing calling it | rites file; rites register §a | kept as a build fact | | |
| Ordinary night-side dark is not the Abyss's gate (another biome's rite *never reads the Abyss's absolute-darkness gate*); the Vigil *sits still in a dark nobody can see into* | rites pass §3.2, §7.2 | kept in "later" | | |
| Laws on every rite: no rite grants a power, no god appears, nothing vanishes without a readable sign; his *"Rites are allowed everywhere"* (2026-10-01) | rites pass §0 and its rulings | kept in "later" | | |
| At that pass Ishko was only ever fed, and Mob'Unloo had the fewest rites of any god | rites pass §11 | lost | A balance note for whoever re-balances the rites when they come back. | |

##### The Empire's ladder, read to its end

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| *"Escallation isn't just 'more troopers' it's more kinds of raids that rapidly escalate until you move. Always start with probes that can be evaded."* | ladder (owner, 2026-09-27) | kept, quoted in the design | It is his rule that a probe comes first and can be evaded, three days before his Abyss words on probes. | |
| *Dark/covered tiles PAUSE the orbital clock* (his rulings of 2026-08-05 and 06, as the ladder records them); the quiet rung *pauses under roof/dark* | ladder §1, §3 | kept: the earliest source for his card's *"full dark still pauses it"* | The first read had the pause from the 2026-11-18 card alone. | |
| The same file says a refuge is *a slower ladder, never a frozen one*, and what is built is a fourfold slowing | ladder §4; pursuit note | kept as a question for him (pause, or four times slower) | His word, twice, is "pause". The built thing slows. | See `NEEDS HIM`. |
| The file's header says "design only"; rung definitions now exist in `src/RimUtinni/EmpirePursuit/` (measured by the second reader, 2026-11-18) | ladder; `RUT_EmpireRungs.xml` | kept as a correction to a stale header | Whether each rung behaves as designed nobody has run. | |
| The probe as the ladder designs it: one or two droids set down well away from the ship; a sighting is line of sight to the ship or a crew member for about two hours in all; it leaves after a day | ladder §3 | kept as the campaign's probe; the Abyss's own built probe differs (distance, through walls) and the difference is a known gap | | |
| Three ways to beat a probe: shoot it before the sighting completes, stay out of sight (*"indoors, dark, under the hull"*), or *let it leave blind* | ladder §3 | kept; the design's two ways gain the third | | |
| A shot probe destroys itself with a small blast: *"a kill is never free loot"* | ladder §3 | kept, quoted in the design | A scavenger crew that cannot scavenge the thing hunting it. | |
| What each ending does: destroyed before it reports, the crew is quieter and the search does not advance; leaves blind, the next probe comes later; leaves with a sighting, the search advances | ladder §2 | kept | | |
| The letter *"Probe landed"* with a bar showing how much it has seen; the quiet alert *"The sky is empty. For now."* | ladder §2, §3 | kept, quoted in the design | | |
| The five visibility bands and their multipliers; an exposed crew on open sand gets two and a half to four days | ladder §2 | kept by reference; not re-derived | The clock's arithmetic is the shared file's. | |
| The tile remembers how far the search got, fading a step a season: *"the desert remembers, decaying"*; landing back on it starts there | ladder §4 | kept as a campaign fact the design now states | A crew cannot use the same dark valley twice in a row for nothing. | |
| The later steps: spotters who call it in, a strike, an ion cordon that stalls the ship for hours and never traps it, a breach, and *"Star Destroyer in orbit"* | ladder §3 | kept as the campaign's; the design lists them and does not restate them | | |
| Ishko's boon, the Unseen Berth, takes one step off the search on this map | ladder §5 | kept in "later" (the gods' layer) | | |
| The storyteller's own Empire raids never advance the search and are kept two days apart from it | ladder §5 | kept | It answers half of the design's `UNMEASURED` on those raids; whether the shadow slows them is still unread. | |
| Four questions the ladder put to him (what the Empire knows after a move; may a step touch the ship; does the bombardment destroy buildings; one heat meter or two) | ladder §8 | kept as the campaign's open questions, not this biome's | | |
| An arrival mode exists that walks raiders in through dark cells; the canon probe droid has no def and a stand-in kind is used | ladder §1 | kept as build facts | | |

##### His planet rulings of 2026-09-07, read to the end

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The growth law: fast growth only where *water AND light are both present*; where either is missing, growth is normal to dormant | freeze rulings R3 | kept: it is why the Abyss's larder is slow | The design said "slow fungus" without the rule behind it. The edge cases where "lit" is arguable were owed and never ruled. | |
| Vents and geysers are a likelihood that *drops to zero on the terminator for sure* | freeze rulings R12 | kept: his source for the sheet's ban on geothermal | | |
| *"We don't need to go around crowning things for the planet."* Say what a place does, never rank it | freeze rulings R9 | kept as a writing rule | The design's "only biome with full cover" states the pursuit's built list, which is a fact. The review's "best single idea on the planet" is a quoted opinion. | |
| *"there will certainly be fliers that visit multiple biomes"* | freeze rulings R17 | kept: a krizzak met outside the Abyss is not a finding | | |
| On the night side the wind runs along the ground toward the terminator and rises in the storm wall; at ground level local relief can dominate, *the most extreme of which are the high mountain ranges* | freeze rulings R4 | kept as lore: the crags' gusts are that local rule | | |
| The night side's dirty ice is dust shed by the returning high wind, settling out, never weather | freeze rulings R27 | kept as lore beside the Dark's aurora-ash | | |
| *"The player may INFER it; the player is never TOLD it"* (ruled for the war-made biomes) | freeze rulings R25 | kept as the manner of the kin's descriptions | Applying it to the Abyss's made lineage is the second reader's reading, not his ruling. | |
| *"the fact that people have found SO MANY ways to get fuel is still evidence of its scarcity."* | freeze rulings R5 | kept, quoted beside tholin | | |
| Eight tiles of a dissolved fungal forest go to the Abyss's old donor def: *a merged tile must be continuous with its new biome* | freeze rulings R29 | lost | Tile paint; the planet is painted once at the end. | |

##### The first names, read to the end

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| *"Please change some of them to one syllable and some to theee syllable. Too many two syllable names sound all the same."* | names doc rule 7 (owner, typed, 2026-09-24) | kept as a naming rule for any later Abyss name | | |
| Each first name's sound: *vrakk*, the quills leaving the back; *gruzz*, the rooting grunt itself; *ulkhorr*, *a word said into darkness*; *bhoruk*, *the bray farmers listen for before the gust-storm* | names doc batch 3a | lost | His smooth names of 2026-10-05 replaced the whole set. | Keep one as a Jawa nickname in a description. |
| The first name for one of the kin was coined as *"Something made, not born"* | names doc batch 3a | kept, reshaped: the idea survives as the made lineage in every kin description | The lineage was in the cast before his sheet said so. | |
| A real canon title, "Dark Beast", sat on a creature that was not that creature; the rename removed the false read | names doc flag 3 | kept (done by the rename to nevarithia) | | |
| The donor's natures: a black bird *ridden into battle*; a *thief of the night* whose snout organs hum to its pack; an ox that *brays at the dawn of thunderstorms*; a boar-thing that digs for truffles | names doc batch 3a | lost | Donor text. Two of these animals he cut; the ported kin carry new descriptions. | |
| The storm giant's donor form: *the Forsaken "dragon"*, fire breath, sixteen squares | names doc batch 3a | lost | It became the summ; fire breath is banned by his words. | |
| A mutated cousin of the quill-hunter lives in the Contagion | names doc batch 3c | lost from this design | The Contagion's, under that biome's own naming rule. | |
| One accent a biome: the crags hard and stopped, the night side hushed and sibilant | names doc rule 5 | lost for the Abyss | His smooth names sit nearer the night-side accent; the crag accent has no creature left. | |
| A creature in several biomes has one name everywhere; a label and its description change together | names doc rule 6, "On acceptance" | kept as naming rules | | |
| Art had been redrawn for two animals he then cut (the shadow charger and the thunderox) | names doc appendix B | lost | Superseded with the animals. | |

##### What is built, from the census and the dry-run record read to their ends

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| An Unveiling announces the nearby rings: the sorter's cairns stand revealed | cleanse census; mechanics review row 2 | kept in 0.2.0 with the rings (built) | | |
| The Unveiling as *a window to travel, hunt and see* | mechanics review row 2 | kept | | |
| The gharrek has facings and no picture of its fans opening | cleanse census; codex record | kept as a known gap: the design's first moment is owed its art | | |
| A tamed krizzak does not steal light; a wild one's feeding has no line-of-sight check | cleanse census | kept as a known gap (the promise "does not feed through a wall" is not built) | | |
| Lamps of one neighbour mod's "deepfire" kind are spared by the Dark | cleanse census; codex record | kept as a build fact | | |
| The grain's sampler wears natural rock and things built of steel, and nothing else | cleanse census | kept as a build fact, stated beside the hull wear | What a hull is made of decides whether the built grain would touch it. | |
| The grain wears things and never skin; it is not clean water for the growth rules | cleanse census (hazard and growth engine rows) | kept, stated in the design | | |
| The cover's code sits in the free biome mod, though his card of 2026-10-01 makes every ship touch campaign-only | cleanse census; codex record | kept as a known contradiction for whoever builds | *Not grounds to remove built cover.* | |
| The cover calls the map quiet at four lit lamps or fewer anywhere on it: *"a small outlying workshop decide the fate of the whole ship"* | codex questions 04 | kept as `UNSETTLED` in the design (the ship's surroundings, or the whole map) | His card answer of 2026-11-10 says what work is safe, not where the count is taken. | |
| The long-stay dream waits on the map's age, not on how long that crew member has lived there | codex questions 08; cleanse census | kept as a known gap (0.2.0) | | |
| The sleeping mother fills seven cells square and is drawn fifteen across; awake she hunts for good, shrugs off nearly all harm and feels no pain; several workers cutting at once can wake her with no grace after the rumble | cleanse census; codex questions 06 | kept in 0.2.0 | *A warning can exist in code yet leave no useful action.* | |
| Summ bone is a light, woody building stuff; a great bone can only be set on ship structure, and a script checks it can stand on a deck | cleanse census; contributions item | kept in 0.2.0 | | |
| The wreck yields seven kinds of part from a finite stock; the three the ship refuses stay loot to sell or smelt; a fitting spends a repair budget on damaged things standing on ship structure | cleanse census; codex questions 07 | kept in 0.2.0 | *Restoring generic hit points may be less than the payoff* his words describe. | |
| A summ sunburns readably under open sky and cools in shade or Dark; any summ the crew owns grows hungry and kills animals by itself, with a warning for tame victims; the built life stages stop growing | cleanse census; codex questions 09 | kept in 0.2.0 as built facts and one known gap (it must never stop growing) | | |
| A Witchfire storm's rumble and flash can bring a hunting summ, with a letter | cleanse census; mechanics review row 3 | kept in 0.2.0 (built) | | |
| Whose idea the nevarithia's knot of Dark is: the sheet calls it his ruling, the cast bible says that slate was never put to him | codex record ("halo authority") | kept in 0.2.0, flagged | Nobody has resolved it. | |
| A tamed sorter's cairn gives a crew member a small memory on sight; the rings are *the wonder and the cryptid's cover story* | cleanse census; mechanics review row 9 | kept in 0.2.0 | | |
| The cryptid's clear pocket is forgotten on save and load; the exchange returns at most one stack of each thing | cleanse census | kept as known gaps (0.2.0) | | |
| The sounder's banded echoes must *harmonise with no clean sensing* | codex record ("sensor boundary") | kept as a rule for whoever builds | | |
| The world face's swirl is drawn by the biomes' shell mod; the soundscape plays only for the map on screen | cleanse census | kept as build facts | | |
| Nothing of the Abyss has been watched working: every existing check reads a definition, and the one recorded run (2026-10-07) covers loading, sign placement, flight eligibility and four cryptid checks | codex record (scene audit); mechanics review | kept as build facts in the design's status | | |
| Three ways this biome fails: the Dark is *a numerical penalty and palette*; beauty and terror *never turn into each other*; a long stay is *arbitrary attrition* and not mounting dread | codex record (failure modes) | kept as tests the design is read against | Agent-written, never his. | |
| *"The Dark is valuable enough to stay in and frightening enough to make that choice costly."* | codex questions (an agent's proposed root) | kept, quoted as an agent's line | | |
| Nine questions were drafted for him and three reached him. Unasked: which demonstration first; what sends people out in an Unveiling; a lamp-thief's cost in work; the last sensible haul; what restores the ship's glory; what a season changes; what makes the summ worth it | codex questions; owner answers | kept as questions a Designer run may still ask | | |
| *"Let's use more codex to do initial designer runs to the question stage on more mods such as all the rest of the baroque biomes"* | codex brief (owner, 2026-11-09) | kept as where the dry run came from | | |
| The review's opinions on the Abyss: the lair, *"ask: largest single piece, rare... never run live"*; the Ship in the Wall, decide with the lair; the hidden ship, *keep*; gusts, *"gust thresholds invented"*. None of the Abyss was among its ten likeliest cuts | mechanics review rows 7, 14 to 16 | kept as opinions; his approval of 2026-11-17 is what placed each | | |
| *"We need to re-examine the rites and special items within each map. Many of them are somewhat fluff"*; *"We need to review all of these special mechanics."* | mechanics review (owner, 2026-10-22) | kept, as why the review exists | | |
| Etchfall was put on trial and kept by an agent under his card *"I cut, you veto"* | fluff cuts (2026-11-02) | kept | Nothing of the Abyss was cut in that pass. | |
| The experiences file is the only home of the Abyss's experience line: the biome has no validation walk | experiences (header) | kept as a fact for whoever deletes files | That file must outlive any cleanup. | |
| *"this one is about the ship"* | contributions item (owner, 2026-09-24) | kept, quoted | | |

##### The ledger items filed under the biome's older names

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| *"Others get promoted to other crag creatures. The forsaken crags are the dark biomes on the night side."* | crags items (owner, 2026-09-01) | kept, quoted | It is the first thing he ever said about what lives here. | |
| The saevitha and the ishvarith began as two pictures drawn for a livestock animal and passed over: *three pictures exist before their creatures do*. One had seven uneven eyes, a damp black hide and no mouth; the other was cat-large with eyes clustered on one side and a violet undertone | crags items (the fauna item) | kept, stated in the design | The saevitha kills by grip because the picture had no mouth. The first read had the mechanic and not where it came from. | |
| *"The forsaken review sheet is reviewed and approved."* | crags items (owner, 2026-09-02) | kept: his approval of both predators | | |
| The ishvarith's valve as he approved it: it *will not cross firelight or a heated space, so a lit camp neutralizes it without requiring fight stats* | crags items (the predators item) | kept, reshaped: light only is built; heated space is the older line that is not built | A crew weak in a brawl was given a predator that a lamp answers. | |
| The third picture became the tellurox, livestock *"genetically modified by the Helix faction"*, and never a crag animal | crags items (the fauna item) | lost from this design | Another biome's animal by his correction. | |
| The cold-drain grip was seen working in the live game on 2026-09-02 (on an older build of the animal) | crags items (the predators item) | kept as a build fact | It is the only Abyss predator mechanic ever watched working. | |
| A crash the first build hit: a redeclared list of life stages is appended to the parent's, not replaced, unless marked to replace | crags items (the predators item) | lost from this design | An engine lesson; it lives in the modding skill. | |
| Lightfall on the world: the chasm already existed under a generated name, "Clam Chasm", and only the name was authored | crags items (the Lightfall item) | lost | World authoring; the planet is repainted once at the end. | |
| The crags' named regions: Gray Crags, Rimewall, Twilight Crags, Sunreach, Nightspill, Coldstone, The Verge | crags items (the mod build item) | kept in "later" with the world's painting | Place names that exist nowhere else in the Abyss's own files. | Lose them at the repaint. |
| The six Forsaken vaults of the campaign's plot stand in other regions; none is in the crags | crags items (the mod build item) | kept as a campaign fact | | |
| The donor's body before it was owned: fourteen donor animals, eight donor plants, donor sand and donor night weathers, vanilla diseases | crags items (the mod build item) | lost | All of it was replaced by the owned port; the animal list is in the roster rows above. | |
| Colder and warmer variants of the biome, never ratified | crags items (the mod build item) | lost | Listed as owed in 2026-09 and never taken up. | |

## Sources read, and the count

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**19 source files, 138 rows** (the first read's count; the second reader's count is at the top of this page), of which **15 lost**, **5 record a move** (three are the hidden ship, seen from
three sources; one is the outdoor pockets, which the cleanse moved and he approved; one is the rough way in, added
by the revision of 2026-11-18, which added six rows and changed two), **6 kept, reshaped** and
2 folded into shared machinery. Every source is named in at least one row's source column (checked by the same script; the six
cleanse files count under the one name "cleanse").

Read whole: the sheet; the cleanse's owner pages and owner marks; the ship item. Read in large part: the cast bible
(rulings, shared law, every cast entry, the lore drafts and rites); the cryptid spec (ruling, who they are, signs,
tiers); the review (all ten ruling sections, the slate's headings and its ship item, the roster fills, the
consult's additions); the cleanse definition (its first two-thirds); the hiding note (the Abyss-relevant half). Read
by heading, by search or parsed: the roster json; the names doc; the pursuit note; the ladder; the cleanse's
next-version list, ambiguities and census; the mechanics review (Abyss table); fluff cuts; the experiences table.
Not read: the review's first six sections on the rename and scorecard, the cast bible's art list and handoff notes,
the cleanse's tickets, bars and models.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `abyss.md`, `abyss_cast_bible_2026-10-01.md`,
`abyss_free_cryptid_2026-10-01.md`, `blackcrags_bedazzle_review_2026-09-30.md`, `rosters/abyss.json`.

Hold until 0.2.0 is designed, because they are the only specification of Lightfall and the cryptid: the cast
bible's sections on the brood and the wreck and its lore drafts, and the cryptid spec. The simplest safe course is
to delete the sheet, the review and the roster json now and keep those two files until then.

Not for deletion: `hiding_the_gravship.md` (it also covers the seas); the shared names doc; the pursuit note and
the ladder; `design/concepts/Abyss/cleanse/` (his approval and marks are recorded there; the proposal should be
re-run from this design rather than applied as it stands, because it switches the hidden ship off).

Before deleting: `abyss.md` is cited by section from the cryptid spec, the cast bible, the names doc and the
cleanse's first question.
