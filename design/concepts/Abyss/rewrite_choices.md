# The Abyss: what the rewrite chose, what it lost, and why

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
| The hull wears only while the engine is cold | first pass's own offered answer, no source | lost | A second rule on top of the weather; he called hull wear *"easy"*. | Take it: the cover itself becomes what costs, at the price of a rule the player has to be told. |
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
| The dusk rat: named for its behaviour, never its look | sheet §4, cast bible §4F, names doc | kept as a roster row and an art debt | Not in the census by name. | |
| The donor cast kept under invented labels | cast bible §4F, roster json, names doc | kept | | |
| The frostling joins this roster | sheet "Owed" | lost | No later source carries it. | A roster row at the Abyss's sitting. |
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
| Four rites taught by the deep dark, performable anywhere dark | review §13, §14 (his words), cast bible §6D | kept in 0.2.0, campaign layer | | |
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

## Sources read, and the count

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**19 source files, 138 rows**, of which **15 lost**, **5 record a move** (three are the hidden ship, seen from
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
