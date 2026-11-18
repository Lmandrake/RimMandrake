# The Sump: what the rewrite chose, what it lost, and why

Companion to `design/concepts/TheSump/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the
overriding priority"*. And his later test: *"you should always look for solutions that make you say Very Jawa"*.
The Sump needed the opposite bending from most biomes. The cleanse proposal of 2026-11-17 built 0.1.0 around a
forty-colonist settlement paying a toll in tar and solvent, and switched off the dig, the traps, the beast, the
kethrel, the mice as an instrument and the belch. Those are the things a crew of scavengers would land here *for*,
and all of them can be met inside a week. This design keeps the cleanse's toll (tar on everything, solvent, routes)
as the floor and puts the scavenging and the creatures back on top of it.

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The Sinking.** One thing of value thrown into the tar *"pushes the next Imperial probe or raid away x5"* and
   wipes other people's ownership claims off what the crew keeps. It is the best single answer in any biome to his
   question "is there anything here that helps them stay longer and hide", it is a Jawa laundering stolen goods by
   sacrifice, and he ruled every detail of it. It is in "later" only because he tabled all rites on 2026-10-03.
   Asked as `NEEDS HIM`.
2. **The tar beast in 0.1.0.** The cleanse deferred it. I moved it in, because a slow unstoppable thing walking at
   the ship while the crew chooses what to carry aboard is the campaign's loop, and because his three answers of
   2026-11-10 (what the routine is, how long a trap gives, what an evacuation saves) were given for exactly this
   and are unused without it. It is the largest test surface in the version, and its day-ahead warning is not
   built. If 0.1.0 has to shrink, this is the first thing to move back to 0.2.0.
3. **The kethrel in 0.1.0.** The mechanics review asked whether 630 lines for one creature *"not in the line"* was
   worth keeping. Under the lens it is the biome's signature meeting: an animal that hoards scrap and wears it,
   met by a crew that hoards scrap. Moved in.
4. **The wick-plant.** *"The biome's only living light is farmed fire-in-waiting."* The sheet's signature crop, with
   shipped art, cut at a later review sheet according to the biome's own source comments. I did not find his words
   for that cut in the files I read; I have recorded it as lost on the strength of the cleanse's census. If the cut
   was an agent's reading, this is the row to check.
5. **The dusk as cover: one step, not a pause.** His ruling says full dark still pauses the search from orbit. The
   Sump's sun is about ten degrees under the horizon, which is deep twilight. I gave it one step. If he reads the
   Sump as dark, it becomes one of the best hides on the planet and the lit moat becomes a much dearer choice.
6. **The moat in 0.2.0, not 0.1.0.** The sheet says *"from that one fact flows the biome's whole economy"*. For a
   colony, yes. For a stop, the first week has no Empire in it and the moat is a thing for when the Empire comes;
   and what would make it a wall (the smoke, the column, fire along connected tar) is not built or has never run.
7. **Excavation's real prizes.** The table that pays the dig is mostly placeholder salvage today. The sheet's
   *"bones and hides of ages the bestiary never named, sunken machines, sealed casings"* are the reason to dig and
   nobody has authored them. The promise in 0.1.0 is honest only if they are.
8. **The soundscape.** *"Derrick-creak and pump-thud carrying miles in cold air; mouse-skitter on glass tar;
   underfoot, rarely, a bubble the size of a room, rising slowly."* Written, never built, never ticketed. Kept in
   "later", but the bubble is also the beast's warning, so that one sound is owed in 0.1.0.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **The dig shaft, the stratum lottery, the click and the disarm:** next version → 0.1.0. Scavenging treasure out of
  tar is why Jawa would land here. This also answers the cleanse's own flagged conflict (it deferred what the frozen
  sheet calls *"core gameplay"* and what the owner's line calls *"hides all"*).
- **The dormant bulge and the station-eating beast:** next version → 0.1.0. What forces the crew out before the
  Empire does.
- **The pre-wake warning (bubble and ring):** next version → 0.1.0. A beast with no sign would break the rule that
  nothing happens without a readable sign.
- **Mouse tracks and the mice as an instrument:** next version → 0.1.0. Built, and the first thing the player sees.
- **The pallick's false floor and the mice's avoidance of it:** next version → 0.1.0. Small, ruled, and the lens in
  one pratfall. Not built.
- **Tolleth and soffeth placed where they tell the truth:** next version → 0.1.0. A grave-bloom on the wrong cell
  is a lie the design never intended.
- **The kethrel's shell, pickup and molt:** next version → 0.1.0.
- **The belch:** next version → 0.1.0 as the built splash; the real flood stays 0.2.0.
- **The poured moat, fuse post, capstan (combat and rescue), draw-joint learning, salvage winch, solvent weapon,
  vault (seal and extract), gaslight chemistry and lamp, natural flame discovery, acoustic readings, the thrummel
  mound and dredgel ecology:** next version → 0.2.0.
- **Stayed "later" from the cleanse's "next version":** the two rites, tar-aged food, the living map, the inhabited
  additions. Not moves.
- **Glasswalk slips:** next version → later. A harmless pratfall on a deck is funny, and it is the owner's by card;
  it waits because a random stun on a five-person crew during an evacuation reads as the game cheating.
- **Dorvel as a farmed crop:** first version → later. His own ruling makes it slow; a stop never sees a harvest.
  Wild dorvel stays as a plant.
- **The drinking-water problem:** the cleanse asked for it to be modelled as a supply to budget across a whole
  colony run. Here it is simply the stop's clock: the crew drinks what the ship carried.
- **New, not in any source:** dusk as cover from the Empire's watchers (a reading of built pursuit code, not a new
  mechanic); one step of cover from orbit; tar rendered to ship fuel (the research text names fuel, nothing builds
  it); tar fouling of the ship (a reading of the nastiness ruling applied to the hull); the beast walking at the
  ship because the ship is the densest cluster of buildings (a reading of its built target rule); troopers' dropped
  gear ending up on the kethrel.

## Every idea, row by row

Source names: *sheet* = `biomes/the_sump.md`; *fauna roster* = `biomes/sump_fauna_roster_2026-09-24.md`; *flora
roster* = `biomes/sump_flora_roster_2026-09-24.md`; *bedazzle review* = `biomes/sump_bedazzle_review_2026-10-01.md`;
*lanneth note* = `biomes/sump_noothelm_b_plant_2026-10-10.md`; *kit spec* = `biomes/kits/sump_kit_spec.md`; *roster
json* = `biomes/rosters/the_sump.json` (all under `design/Jawa/worldbuilding/`); *cleanse* =
`design/concepts/TheSump/cleanse/`; *walk* = `design/validation_walks/RimMandrake/TheSump.md`; *owner answers* =
`design/RimMandrake/designer_codex_2026-11-09/TheSump/ANSWERS_OWNER.md`; *mechanics review* =
`design/RimMandrake/special_mechanics_review_2026-10-22.md`; *experiences* =
`design/RimMandrake/biome_experiences_2026-10-20.md`; *fluff cuts* = `design/RimMandrake/fluff_cuts_2026-10-23.md`;
*items* = the Sump's ledger items under `infrastructure/state/items/` (named in the row); *ship gifts* =
`infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`; *pursuit code* = `src/RimUtinni/EmpirePursuit/`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "The trap that remembers"; "black glass under a sun that never rises, holding a million years of the unlucky, perfectly" | sheet header | kept, quoted | | |
| "Sticky, stinking, slow to move or burn or surrender. The sump hides all and makes you fight it for every action." | walk, experiences, mechanics review | kept, quoted | His typed line. | |
| The tar's origin: the Pyrelands make it, drainage carries it nightward, the cold is the lid | sheet header, §2, §3; flora roster | kept, reshaped: one clause ("filled by every slow black flow") | World history; a crew at one stop does not see it. | A paragraph of lore in a world document; free. |
| The margin-interspersal seam with the Pyrelands ruling | sheet header | lost | A reconciliation note about the painted map, settled by the sheet itself. | |
| Measured tiles, sun angle, temperatures, regions (Nightspill, Glass Reach) | sheet §0 | lost, except the sun angle (used for the cover reading) and "cold, dry" | A tile count is never evidence; the planet is painted at the end. | |
| Donor inventory and corrections (cold tar not sun-baked mud, sparse-but-strange) | sheet §0, roster json | kept as build facts; "sparse-but-strange" kept as the cast's shape | | |
| The planet's oil sump, lowest basin, flat black pools and cooled sheets under dusk | sheet §1 | kept | | |
| "Mice run the tar without a thought. Nothing else touches it" | sheet §1 | kept | | |
| The hydrocarbon ladder (Sump, Blue Desert, Propane Lakes) | sheet §2 | lost from this design | Cross-biome lore; belongs in the shared-machinery consolidation. | One line there; free. |
| The tar arrives and never leaves; the tar preserves; the tar defends; the tar is partly alive | sheet §3 | kept (the four drive the dig, the dusk and moat, the beast) | | |
| "It can be lit into a terrible smoky horror nothing can cross" | sheet §3 | kept, quoted | | |
| The six "always true" lines | sheet §5 | kept; three quoted | | |
| "The stations reek for miles, and their lamps are the only lights" | sheet §5 | kept, reshaped: the lamps are also what gives a crew away | The pursuit code makes darkness cover. | |
| Ban: no whole Assailant or Rakatan; partial remains; traps more likely than either | sheet §6, kit spec | kept | | |
| Ban: no tar beast as a fightable spawn | sheet §6 | kept (with his later solvent-wake exception) | | |
| Ban: no sun-driven flora; ban: nothing glows | sheet §6, flora roster | kept | | |
| Ban: no rain, no surface water | sheet §6 | kept, reshaped: it is now the stop's water clock | A crew that cannot refill is a crew on a timer. | A water source by trade only; changes nothing built. |
| Ban: no warm-climate donor flavour; no vanilla-Earth life | sheet §6 | kept | | |
| Art theme: light, palette, silhouettes, motion ("the pools, never. Until.") | sheet §9 | kept as art direction; the motion line used | | |
| Sound: derrick-creak, pump-thud, mouse-skitter, the room-sized bubble | sheet §9, bedazzle review | kept in "later"; the bubble owed in 0.1.0 as the beast's sign | | Build the whole bed now: small to medium, reuses the Long Shade's sound extension. |
| The Sump as a place for the dirty and idiosyncratic, frustrating the tidy | items (`SUMP_INHABITED_NOTES_1`, `SUMP_TAR_NASTINESS_1`) | kept, quoted | It names Jawa among those who belong. | |
| Junker stations: derricks, holding ponds, barrel yards, stilt bunkhouses, "everyone knows which ponds you don't pump deep" | sheet §7b, §8 | kept in the campaign layer; used as where the crew trades and buys fuel | The biome places no settlement. | |
| The dig fields, old losses, "the station that pumped the wrong pond" | sheet §8 | kept in the campaign layer | | |
| The glass reaches | sheet §8 | kept | | |
| Factions that belong: junkers, Jawa, deep tribes, Black Star; expedition ruins, failed refineries, miserable moisture farmers | items (`SUMP_INHABITED_NOTES_1`) | kept in "later" (the inhabited pass) | His own scoping: "notes for Inhabited injection later". | |
| Moat-tar as the export "of being left alone"; droid enclaves ring themselves in it | sheet §7 | lost from this design | A world trade fact; the crew sells what it digs, not solitude. | |
| Asphalt for the Ashfall Road; re-paving as a player project | sheet §7; items (`SUMP_WALKWAYS_1`) | lost (his ruling: "this one is about the ship") | | |
| The free mod is the bare biome and the ruled content sat in the campaign patch; "move it all into the free mod" | bedazzle review §1, §4 | kept as a build fact (the move is done or ticketed) | | |
| "Evil sun god" struck from descriptive text | bedazzle review | kept as a build fact | | |

### Tar on everything, and getting it off

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Sticky tar onto any terrain; the tarred condition; tar-ruined goods | items (`SUMP_TAR_NASTINESS_1`), mechanics review | kept | *"The line, literally."* | |
| "The colony stays dirty": automatic scrubbing, the player spends solvent and plans routes | owner answers, cleanse | kept, quoted | | |
| Weak solvent from seepwax, generous; strong solvent only by trade from the Poison Forest | items (`SUMP_GASLIGHT_1`, `SUMP_TAR_NASTINESS_1`) | kept; strong solvent is a trade hook only | | |
| One acid, three uses (cleaning, vault extraction, the lamp) | items (`SUMP_GASLIGHT_1`) | kept; the second and third uses are 0.2.0 | | |
| A scrub must clear carried tar, not only the label | cleanse | kept as a promise's control | A live run found the defect. | |
| The tar's own reward ("annoying materials pay") | items (`SUMP_TAR_NASTINESS_1`) | kept: the dig, bitumen, fuel | | |
| Duckboards: cheap, foul, flammable | items (`SUMP_WALKWAYS_1`), cleanse | kept in "later" as the cleanse recommends (ordinary wood floor does the job) | Brindeth no longer yields wood. | Keep them as their own floor: one more def to test. |
| Glasswalk: never fouls, never full speed | items (`SUMP_WALKWAYS_1`) | kept, quoted | | |
| Glasswalk pratfalls | items (`SUMP_WALKWAYS_1`), cleanse | moved (cleanse next version → later) | See scope moves. | 0.1.0: his card, slapstick, and a random stun during an evacuation. |
| "Cheap-and-tidy is a treadmill; the real answer is to stop fighting the tar and glaze it" | items (`SUMP_WALKWAYS_1`) | kept as the reason for glasswalk | | |
| Glasswalk as ship decking | ship gifts; items | kept (0.1.0, as the answer to tar on the decks) | His named gift. | |
| Tar as a liquid with grades, channels, gates, cooling to glass | items (`SUMP_TAR_FIRE_NETWORK_1`), cleanse | folded into shared machinery (`FlowWorks`) | | |
| Colonists drink carried fresh water; non-native livestock cannot drink here | cleanse owner pages, definition | kept, reshaped: the stop's clock | | |
| Natives drink tar | cleanse | kept (binding owed) | | |
| The forty-colonist routine, route and solvent-queue models, a whole-season run | cleanse definition, models | lost | Colony scale. The situation walk (contact, dirty boots, recovery, death, reload) is kept. | |

### Digging

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Every dig is treasure or a click"; "the tar preserves everything, including intentions" | sheet §7 | moved (→ 0.1.0), quoted | | Leave it in the next version as the cleanse did: 0.1.0 is then a toll with no prize. |
| The stratum table: junk and bitumen, old bones and hides, machines and casings, partial remains, traps | kit spec S2 | moved (→ 0.1.0) | Mostly placeholder loot today. | |
| Traps outweigh remains in every stratum; deeper is richer and clicks more | kit spec S2 | kept as a build rule | A weight is tuning; the promise is "traps come up more often than their makers". | |
| The click, the fuse, the disarm by a qualified miner | kit spec S2, cleanse | moved (→ 0.1.0) | | |
| "Nearby miner can make it" | owner answers | kept, quoted | | |
| Deep digging rolls a beast-wake | kit spec S2, cleanse | moved (→ 0.1.0) | | |
| Dig-woken things are ancient machines or assailants only; the deleted swarm of preserved biters | fauna roster ruling 2 | kept (the ruling); the swarm stays lost | Not authored in the table yet. | |
| Tolleth, the grave-bloom, marks what the tar is holding | flora roster | moved (placement → 0.1.0), quoted | | |
| Dredgel, the archive's janitor, parks on dug ground | fauna roster | kept as an animal; its attraction to digs is 0.2.0 | | |
| The flagged strips "where something clicked once"; mapped claims | sheet §8 | kept in the campaign layer | | |
| Preserved draw-joints from the strata teach the capstan | bedazzle review §5, cleanse | moved (→ 0.2.0) | | |
| The salvage winch | cleanse, mechanics review | moved (→ 0.2.0) | Dragging wrecks along the ground is very Jawa. | 0.1.0, if the capstan family is wanted early. |
| Capstan and traction lance share one pull; "merge, keep one" | mechanics review, fluff cuts | kept as two (the fluff-cut review found the merge is a redesign) | | |

### The beast

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The tar beasts: slow, huge, oozing, feeding on the unfortunate; the Patient family with the sarlacc and the Fever Wood's deep thing | sheet §4 | kept, quoted in shared machinery | | |
| "A slow, unstoppable, station-eating catastrophe you evacuate ahead of, not fight" | sheet §4, bedazzle review | moved (→ 0.1.0), with the ship as the station | | 0.2.0: a smaller first version with nothing that forces a launch. |
| The body: about nine times a person, a glossy mound with no clear head | bedazzle review §3 | kept | | |
| It goes for the densest cluster of buildings, tars every cell it crosses, swallows what it reaches, leaves a mound and a letter, sinks back at a new address | bedazzle review §3 | kept | | |
| Wake causes: explosion, construction near it, deep dig, pumping | sheet §4, bedazzle review | kept | | |
| Signs: the bulge, bent mouse-lines, the bubble and a ring of filth a day ahead | bedazzle review §3 | kept; the day-ahead sign is owed | | |
| "People and chosen goods: everyone escapes and he picks which valuable stores to carry; buildings are lost" | owner answers | kept, quoted; the escape is the launch | | |
| The Thrumbo placeholder | bedazzle review | lost (replaced by the real body) | | |
| Solvent in the pit wakes it manhunter, a deliberate weapon serving two gods | bedazzle review §9 | moved (→ 0.2.0), quoted | Reads under the lens as the parting shot at a siege camp. | |
| "The beast turns over" and the other three second-round offerings | bedazzle review §6 | lost (the offerings card was built from a later redo, not these) | | |
| A visiting giant or passage candidate | cleanse | lost (the beast is not a passage creature) | | |

### Animals

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Sump-mouse: the prey base, the charm and the instrument; lines; tameable, cheap | sheet §4, fauna roster | kept, quoted; the cage of mice is a takeaway | | |
| "Junkers read mouse-lines the way sailors read water" | sheet §4 | kept in spirit; not quoted | | |
| Gulveth, the tar's own grazer | fauna roster | kept | | |
| The thrummel family and the mound; chitin and seepwax; "the jackpot raid and the moral of it" | fauna roster | kept as animals; the defending mound moved (→ 0.2.0) | Not built. | |
| The donor bumbledrones and tar guzzler beside ours | roster json, bedazzle review | kept where they are (evictions are stopped) | | |
| Brommet, the wool-backed margin grazer | fauna roster | lost (cut at a later review sheet, per the cleanse census) | | Restore: a def and art that already existed. |
| Skarrid, the still hunter that mimics the bulge | fauna roster | kept, quoted | | |
| Skellarn, the stilt-flier | fauna roster ruling 1 | kept, quoted | His typed idea. | |
| A skellarn circling low tells you something is moving on that pool | fauna roster | lost as a promise | No scene could tell it from ordinary wandering. | Build it as a real behaviour: small. |
| Kethrel: scrap shell in four stages, molt, charge, nothing vanishes | bedazzle review §3 | moved (→ 0.1.0) | | |
| The hssiss, a canon animal, in the campaign patch | bedazzle review, roster json | kept where the campaign patch puts it | | |
| The 57 evictions and homeless reserves | roster json | lost from this design | Bookkeeping of the fauna assignment pass; it lives in the register. | |
| One home each; nothing migrates | fauna roster | kept | | |
| The silhouette brief and legibility matrix | fauna roster, flora roster | kept as art direction | | |
| No pursuit predator | fauna roster, roster json | kept | | |

### Plants

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Every plant is a chemotroph; the ring at the pit margins | sheet §4, flora roster | kept | | |
| Wick-plant, "a garden of unlit candles" | sheet §4, flora roster, kit spec S5 | lost (cut at a later review sheet, per the cleanse census) | See "the ones I would look at". | Restore: it has shipped art. |
| Dorvel, the slow food crop | flora roster ruling 3 | moved (first version → later for farming); the wild plant stays | | |
| Skelver, the forage staple | flora roster | kept | | |
| Korveth, "a plant growing its own coal" | flora roster | kept, quoted | | |
| Brindeth, "the biome's tree-line joke" | flora roster | kept as scrub; it no longer yields wood | A later size ruling. | |
| Soffeth, the breather's tell (gas below) | flora roster | moved (placement → 0.1.0) | | |
| Velloch, the living sheen; mirrelin, the mice's pasture | flora roster | kept | | |
| Pallick, the false floor; "the mice always tell the truth about it" | flora roster ruling 5 | moved (→ 0.1.0) | | |
| Lanneth, "the Sump's one sweet thing", made from the art he kept | lanneth note | kept | | |
| Lanneth in fruit skewers | lanneth note | kept in the campaign layer | | |
| Tar-loam and tar-pan terrains, tar-beds | flora roster §5 | kept as build facts | | |
| Naming: his plain names for what he named, invented words for the rest | fauna roster ruling 6 | kept | | |

### Fire, light, storage and fighting

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The poured moat, re-poured after burning; "burnt tar is spent tar" | sheet §7b, kit spec S1 | moved (→ 0.2.0) | | |
| The fuse post and command ignition | kit spec S1 | moved (→ 0.2.0) | | |
| The smoke wall that blocks sight and passage; the column "visible for a day's travel" | sheet §7b, kit spec S1 | moved (→ 0.2.0); the column is also what ends the hide | Not built. | |
| A lit moat catches adjacent natural pools | kit spec (ruled 2026-09-12) | kept in 0.2.0 | | |
| Network fire with gate firebreaks; "a belch during a moat-burn is a genuine catastrophe" | items (`SUMP_TAR_FIRE_NETWORK_1`) | kept in 0.2.0 | | |
| "Slow to burn" read as long burning once lit | cleanse | kept | | |
| The belch | fauna roster ruling 1 | moved (→ 0.1.0 as a splash) | His typed event. | |
| Tar rain | bedazzle review, cleanse | lost (ruled out 2026-10-18) | | |
| The capstan turret | bedazzle review §5 | moved (→ 0.2.0), quoted | | |
| Lassos removed from the game | bedazzle review §5 | kept (dropped list) | | |
| Gaslight: tar and acid make green gas; the warbling light; "dancing, pulsing, beautifully warm" | items (`SUMP_GASLIGHT_1`) | moved (→ 0.2.0) | A lamp in the dusk is beautiful and is a beacon; that tension is new and good. | |
| Natural seep flames that teach it; a technology on first meeting tar | items (`SUMP_GASLIGHT_1`) | moved (→ 0.2.0) | Not built. | |
| Flame statues; the holy act | items (`SUMP_GASLIGHT_1`), bedazzle review | kept where they live (`FlameStatues`, the campaign's precept) | | |
| The gas named Sumpgas in the campaign | items | kept in the campaign layer | | |
| The tar vault; "extraction is a solvent based economic need ... Never seen that mechanic before" | items (`SUMP_TAR_VAULT_1`) | moved (→ 0.2.0) | A larder matters to a ship more than to a stop. | 0.1.0: his own invention, built; one more system to prove. |
| Tar-aged food | cleanse | kept in "later" | | |
| The dusk lock and dry weather | kit spec S6, bedazzle review | kept | | |
| Darkness hides a target from a watcher beyond six cells | pursuit code | kept, new to this biome's design | | |

### Rites, the ship, and the pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The Sinking (Ishko): the next probe or raid pushed five times further, ownership erased, a raid lull | bedazzle review §6, §9 | kept in "later"; `NEEDS HIM` | Tabled by him. | See above. |
| "I like Vault forgets, but it should be true about almost anything you own" | bedazzle review §9 | kept with the Sinking | | |
| Mob'Unloo's Price: a good thing and a hated effigy; the Empire held off five times; a faction arrives tarred | bedazzle review §6 | kept in "later" | | |
| The beast sleeps a season; the ancient traps fizzle | bedazzle review §9 | kept in "later" | | |
| Ship gifts: glasswalk, gaslight lamps, the tar vault | ship gifts | kept: glasswalk 0.1.0, the others 0.2.0 | | |
| The arrival letter "The Ship Remembers the Sump" | bedazzle review, cleanse | lost (recommended for dropping; his to confirm) | It tells what the mice should show. | Rewrite it as one line of dread: free. |
| Acoustic scanner readings | cleanse | moved (→ 0.2.0) | | |
| Biome scoring, rarity slider, tar-lake world mutators | cleanse | lost (no worldgen) | | |
| The cleanse's signature (exposure, routes, solvent) | cleanse owner pages, definition | kept as the floor of 0.1.0 | | |
| Its deferral of "hides all" | cleanse owner pages | lost (reversed: the dig is in) | | |
| Its seven proposed bars | cleanse | kept as history; the twelve promises in the design are the proposal to argue from | | |
| Tickets and switch-offs | cleanse tickets | kept as they stand, except where a feature moved | | |
| The must-be-true list | walk | kept | | |
| The mechanics review's dispositions (keep, ask, merge, simplify) | mechanics review | kept as history; each row above carries the outcome | | |

## Sources read, and the count

Measured after writing: a script counted the table rows and the first words of the "what happened" column; the
file count is the files named below as opened, counted by hand (the pursuit code counts as one).

Read whole: the sheet; the bedazzle review; the lanneth note; the cleanse's owner pages; the owner answers; the
walk; the mechanics review's Sump table; the ship-gifts row. Read in large part: the fauna roster (rows one to nine
and the eight rulings; not its legibility matrix, donor dispositions or campaign section); the flora roster (all
ten rows with each row cut off at about 600 characters, and the mechanism inventory; not its later sections); the
cleanse definition (its first two-thirds, long lines cut at 1,500 characters); the cleanse next-version list (every
entry's "what" line; not every "why"). Read by heading or by search: the kit spec (S1, S2 and the headings and
first lines of S3 to S6, and the first ruled card; not the full engine routes); the roster json (its structure, its
five fauna rows, one flora row and the first forty of 57 evictions); the cleanse ambiguities (headings only),
tickets (searched for fuel), census (not opened beyond its shape); the experiences table; fluff cuts (searched);
the items `SUMP_DESIGN_SITTING_1`, `SUMP_TAR_NASTINESS_1`, `SUMP_GASLIGHT_1`, `SUMP_TAR_VAULT_1`,
`SUMP_WALKWAYS_1`, `SUMP_INHABITED_NOTES_1`, `SUMP_TAR_FIRE_NETWORK_1` (the first 3,000 characters of each).
Not read: the cleanse's bars, models, review, converge and fixes files; the Designer's `NOTES.md`, `QUESTIONS.md`
and `record.json` for the Sump; the items `SUMP_TAR_LIVING_SYSTEMS_1`, `SUMP_TAR_HYDROLOGY_1`,
`SUMP_UTINNI_LAYER_1`, `SUMP_MECHANICS_1` and the build items; `design/Jawa/proposals/tar_pits_deep_design.md`
(named by the gaslight item and not opened: a second reader should check it for ideas with no row here).

**27 source files opened, 128 rows**, of which **17 lost**, **25 record a move** (whole or in part), **4 kept, reshaped** and 1 folded into shared machinery.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_sump.md`, `sump_fauna_roster_2026-09-24.md`,
`sump_flora_roster_2026-09-24.md`, `sump_bedazzle_review_2026-10-01.md`, `sump_noothelm_b_plant_2026-10-10.md`,
`kits/sump_kit_spec.md`, `rosters/the_sump.json`.

Hold until the rites are designed for their later version, because the bedazzle review's sections 6 and 9 are their
only specification: copy those two sections out before deleting `sump_bedazzle_review_2026-10-01.md`.

Not for deletion: `design/concepts/TheSump/cleanse/` (superseded by this design, never applied; it should be re-run
from this file, not applied); the validation walk; the ledger items; the Designer's November question and answer
files; `design/Jawa/proposals/tar_pits_deep_design.md` (not read by this pass).

Before deleting: the frozen sheet is cited by section number in both rosters and the kit spec, and by path in the
Blue Desert and Propane Lakes sheets (the hydrocarbon ladder). The two rosters are the art pipeline's silhouette
briefs; their rows should move into the design folder or the art ledger first, whichever the art seat reads.
