# The Forge: what the rewrite chose, what it lost, and why

Companion to `design/concepts/TheForge/design.md`, written 2026-11-18 by the same pass. Its job is to let the older
files be deleted without fear: every distinct idea found in any source has a row saying what became of it. Nothing
has been deleted. The older files this design replaces are listed at the end.

**How the choices were made.** The owner's words of 2026-11-18: the biomes *"are going to be visited by a huge ship
on the run"*, crewed by Jawa *"way in over their head"*; *"anything that takes seasons to observe will simply be
missed"*; for 0.1.0 and 0.2.0 the *"OMG did you see that?"* of Jawa meeting alien creatures at close range is *"the
overriding priority"*.

The Forge needed the least bending of my five. Its signature is a cycle that turns in five to seven days (measured
from `RM_ForgePulse.xml`: still 48 to 72 hours, gas 2 to 3, rain 6 to 9, freeze 10 to 14, growth 54 to 66, cracks 6
to 8, melt about 2), so a crew on a stop sees the whole of it more than once, and its payoff is cargo: a light
stone, cut on borrowed ground and carried off. The cleanse proposal of 2026-11-17 chose that cycle as the signature
and I kept its choice whole. What changes is who is standing there (a crew, not settlers), which creature extras
come back (those a week can show), and three things his rulings of 2026-11-18 ask every design to state.

Those four rulings (3:10 PM PST) are applied, not asked: the stop length as an outer edge (about six weeks); cover
from orbit (steam and ash, one step); fuel (emergency only in play, with the campaign's volcanic-gas line noted and
the struck heat exchanger asked about); and the wear on the hull from the sources (fire and boiling rain each turn;
the melt under anything on crust; floatstone as the armour).

**Words used in "what happened".** *kept*; *kept, reshaped* (changed as stated); *moved* (scope bucket changed, from
and to given; the cleanse used "first version", "next version, switched off" and "recommend retiring", and this
design uses 0.1.0, 0.2.0, later, dropped; a cleanse "next version" item that lands in "later" is not a move);
*folded into shared machinery*; *lost*.

## The ones I would look at

1. **The ship drinks the mountain.** *"The Forge is the best refuel stop on Ash'karr and the most uncomfortable
   one; landing here is a bargain the player prices."* A rig on a vent charging the ship's engine, and every burst
   of rain scouring the parked hull. It answered the review's finding that nothing here touched the ship. He struck
   it. It is the single idea in the Forge's sources that is about the ship, about fuel and about hull wear at once,
   which are three of the things he ruled on 2026-11-18. Lost; asked as `NEEDS HIM`.
2. **The fireweed economy.** *"A place hot enough to kill grows the thing that lets you endure everywhere else."*
   Fireweed fibre as the planet's heat gear. Struck earlier, and the one-sun ruling has since removed most of what
   the gear was for. Lost. The sentence is the best in the sheet.
3. **The Empire's gas station.** *"Watching their ammunition slowly run out with a smart grin."* It is the only
   biome on the planet where the pursuer already lives. I left all of it in the campaign layer, as every earlier
   pass did, and asked one question about the search. Under the lens this mountain is where the chase and the
   planet's politics meet, and a first version that does not show the station at all leaves that out.
4. **Two faiths, one mountain.** *"Pilgrims climb to see it once. Two churches, each certain, quietly disagreeing
   forever."* And for this crew it is their own god's forge. Map mechanics for it were struck; content for it is
   "later". One sentence survives in the design.
5. **The kettugal.** One of three creatures offered for the slow-ground slot: *"a low ceramic bowl on six
   basalt-disc legs, carrying a level pool of glowing slag"*, and *"the first thing to walk off the crust when the
   cracks begin to glow."* The ummisk was built instead. A living warning that walks off borrowed ground is exactly
   what a crew of newcomers would learn to watch. Lost (not chosen).
6. **The ummisk's glass trail.** As pitched, *"its wet underside quenches lava-edge cells into a short-lived glass
   trail you can walk on. Follow an ummisk across the flows."* As built, by the cleanse's reading, it *"makes no
   glass trail."* Kept as built. The trail was the creature.
7. **The foundry tower as a dungeon.** *"Floor after floor of forge-works over open melt, heat as the wall, the
   tenders as the garrison."* Salvage that has to be fought for, on a week's clock, is very Jawa. Campaign layer,
   0.2.0 here; the census could not find its implementation.
8. **Bulloos that explode.** The cleanse recommends retiring them as a copy of the game's own explosive livestock.
   I kept the recommendation. A floating animal that bursts when a Jawa annoys it is, I admit, on the lens.

## Scope moves

Each line is one feature whose bucket changed against the cleanse proposal of 2026-11-17. Revert by moving the line
in the design's Scope section.

- **Dhokkur wake show (groan, dust, pouring water):** next version → 0.1.0. Built; it is what makes the rock
  standing up a moment and not a state change.
- **Dhoggur swell:** next version → 0.2.0. His ruling of 2026-10-16; slapstick.
- **Metal diet:** next version → 0.2.0. It eats the thing this crew values most.
- **Jossur stoop and column hunting:** next version → 0.2.0.
- **Dhokkur roads and shoves:** next version → 0.2.0. The cleanse's runner-up signature.
- **Moving steam fronts; floods:** next version → 0.2.0. His answer about walls is already on file.
- **Extra dhuvvox swarm and countdown:** next version → 0.2.0.
- **Phase voices:** next version → 0.2.0.
- **Bulloo gel and fission:** next version → 0.2.0.
- **Garden study, floatstone hull and door:** next version → 0.2.0. The hull is the Forge's armour under his
  ruling.
- **Scanner readings:** next version → 0.2.0.
- **Campaign gas tap, testing ring, one tower floor:** next version → 0.2.0, campaign layer.
- **Stayed "later" from the cleanse's "next version":** fungus study. Not a move.
- **Kept as the cleanse recommended (retire):** fungus cooling, bulloo detonation, inert knobs, world scoring.
- **Settling the mountain; forty colonists; the full-season trace:** first version → later.
- **New, not in any source:** the Empire's troops as newcomers to the cycle (a reading of built behaviour: the
  phases do not ask who is standing where); fire and rain on the parked ship's apron as the hull's wear; "never
  park on crust"; the reading of the mountain as the crew's own god's ground, from the sheet's line on Jawa sacred
  geography.

## Every idea, row by row

Source names: *sheet* = `biomes/the_forge.md`; *review* = `biomes/forge_bedazzle_review_2026-09-28.md`; *cast bible*
= `biomes/forge_bedazzle_cast_2026-09-29.md`; *kit* = `biomes/kits/forge_kit_spec.md`; *roster json* =
`biomes/rosters/the_forge.json` (all under `design/Jawa/worldbuilding/`); *embargo spec* =
`design/Jawa/tibanna_embargo_plot_spec.md`; *slow-ground* = `design/RimMandrake/forge_slowground_concepts_2026-10-20.md`
and its `.json`; *cleanse* = `design/concepts/TheForge/cleanse/`; *walk* =
`design/validation_walks/RimMandrake/TheForge.md`; *owner answers* =
`design/RimMandrake/designer_codex_2026-11-09/TheForge/ANSWERS_OWNER.md`; *experiences* =
`design/RimMandrake/biome_experiences_2026-10-20.md`; *campaign lore* = `design/Jawa/reconciled_lore/01_campaign.md`;
*pulse def* = `src/RimMandrake/TheForge/Defs/GameConditionDefs/RM_ForgePulse.xml`.

### The place

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| "Dark foundry towers rising defiantly against the sun, over herds grazing the smoke" | sheet header | kept, quoted | | |
| "The only unstolen fire"; vulcanism owes nothing to the sun | sheet header, §2 | kept, quoted | | |
| Three donor defs as one place, zoned by height | sheet header, §0 | kept as a build fact (done) | | |
| Measured tiles, sun heights, temperatures, the disputed older geography | sheet §0 | lost | The planet is painted at the end. | |
| The epicentre of the geyser law | sheet §0, §5 | lost | A rule about the whole planet. | |
| One mountain, three zones, the only vertical skyline in the Dune Sea | sheet §1 | kept, quoted | | |
| Towers "visible for a hundred kilometers" | sheet §1 | kept, quoted | | |
| Native fire: the Forge outshines the sky from below | sheet §3 | kept as mood | | |
| The closed rain: the same water cycling forever, boiling, flashing off | sheet §3 | kept | | |
| The vapor columns as pasture | sheet §3 | kept | | |
| Nothing lives in the lava, but there is movement there | sheet §3, §6 | kept, quoted | | |
| What the lava machines are doing is never revealed | sheet §6 | kept | | |
| The admission test: lives in the flash-interval, or in the sky | sheet §4 | kept as the roster's rule | | |
| Flash-interval flora; "mosses drink in the seconds between fall and flash" | sheet §1, §4 | kept, quoted | | |
| Fireweed as the planet's heat-gear fibre | sheet §4, §7; review slate D | lost (struck earlier); flagged above | | |
| The sky herds: fumeriders, beldons, fleet fliers | sheet §4 | kept, reshaped: bulloos and fleet fliers in the free tier; beldons in the campaign layer | The built roster. | |
| Beldons produce tibanna | sheet §4, §7 | kept in the campaign layer | | |
| The Contagion's corpse-ring: "always testing" | sheet §4, §5 | moved (cleanse next version → 0.2.0, campaign layer), quoted | A ring that forms and dies in hours can be seen in a stop. | |
| Always true: the towers stand whole; the quotas are still being run for no one | sheet §5 | kept | | |
| The hard bans | sheet §6 | kept as rules | | |
| No taking of Forge fire in Tribes canon | sheet §6, §8 | kept, quoted | | |
| No tibanna source but the beldons | sheet §6; embargo spec | kept, quoted | | |
| Free heat: smelting, kilns, power with no fuel bill | sheet §7; kit F6 | kept in "later"; quoted for the fuel answer | Vent machines beyond the game's own were struck. | |
| Obsidian and volcanic glass as materials | sheet §7 | lost | Never built; no source makes them more than a line. | A material def: small. |
| The vents as taps | sheet §7 | kept, quoted for the fuel answer | | |
| The towers as forge-tech salvage over an open melt | sheet §7, §8 | kept: surface works in 0.1.0; the interior moved (→ 0.2.0, campaign) | | |
| The towers as the smeltery of the god-project | sheet §8 | lost | Plot, partitioned by the sheet itself. | |
| The Imperial gas operation | sheet §8; embargo spec | kept in the campaign layer, quoted; flagged above | | |
| The embargo as a campaign clock | sheet §8; embargo spec | kept in "later" (campaign) | | |
| Two faiths, one mountain | sheet §8; review slate F | kept in "later"; one line quoted | Map mechanics struck earlier. | |
| "Jawa sacred geography sees Sh'kaar's forge" | sheet §8 | kept, quoted: it is the crew's own god's ground | | |
| The Tribes' witness-trail; obsidian quarries | sheet §8 | kept in the campaign layer | | |
| "Dark towers against the sun, herds grazing the smoke"; palette, light, silhouettes | sheet §9 | kept as art direction | | |
| Sound: vent-roar, the rain's hiss-and-flash, tower harmonics, machines under the melt | sheet §9; review slate C | hiss kept in 0.1.0; the rest moved (→ 0.2.0, phase voices) | | |
| Experience line: "Where the gods came to forge a world is now the ruins that seek to unmake you. Even the beasts challenge your presence." | experiences; walk | kept, quoted | His words. | |
| "Ruins that seek to unmake you" read as returning lava changing routes past the works | cleanse owner_pages, definition | kept | | Hostile tenders: the 0.2.0 tower. |
| "Even the beasts challenge" read as real predation and retaliation | cleanse definition | kept as a promise | | |
| His answers: old works shape ordinary journeys; recall before gas, orderly retreat before melting; walls stop a steam front | owner answers | kept, quoted | | |

### The cycle

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The grand cycle: still, gas, rain, freeze, growth, cracks, melt | cleanse; cast bible; slow-ground | kept as the centre of 0.1.0 | | |
| Phase lengths | pulse def | kept as description, never as a bar | A bar is an experience. | |
| A hiss before the gas | cleanse definition; pulse def | kept | | |
| Gas ignites exposed vegetation; a bare map invents no fuel | cleanse definition | kept | | |
| Boiling rain scalds the unroofed; scald uses heat armour | review; kit F1 | kept | | |
| "Boiling rain is survivable once": never instant death from one burst | kit, owner card 2026-09-12 | kept | | |
| The flash window: growth multiplied after a burst | review; kit F1 | kept | | |
| Wire the Flash: a harvest economy on the window | review slate A | kept, reshaped: the floatstone gardens became the harvest | The later cycle design. | |
| Crust: temporary basalt and pumice over lava | cleanse; cast bible §5 | kept | | |
| Floatstone gardens, lace-walled globes | cast bible §4 | kept | | |
| Floatstone: light, strong, nonflammable, beautiful | cast bible §4; cleanse | kept | | |
| Lightness means carried weight, not lighter walls or a fuel saving | cleanse definition | kept | | |
| Gardens depart at cracks with dust and a count | cleanse | kept | | |
| Cracks warn; melt takes what is left, with an account | cleanse | kept | | |
| "Ground that belongs to it and ground it is borrowing" | cleanse definition | kept, quoted | | |
| The arrival note | cleanse; review mark 6 | kept | | |
| Shutting the cycle off never drops a survivor into lava | cleanse definition | kept as a promise's control | | |
| Floods in the rain | cleanse | moved (→ 0.2.0) | | |
| Moving steam fronts | cleanse | moved (→ 0.2.0) | | |
| Four phase voices | cleanse | moved (→ 0.2.0) | | |
| The Mountain's Breath, Heard: the burst audible before it arrives | review slate C | kept (the hiss) | | |
| The Columns Made Visible | review slate H | kept (column haze); spirals and highlights later | | |

### Life

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Dhokkur: the giant on the clock, terrain until the rain | review fills, slate G; cast bible §3 | kept | | |
| Dhokkur's wake show | cleanse | moved (→ 0.1.0) | | |
| Dhokkur's remembered roads and shoves | review slate G; cleanse | moved (→ 0.2.0) | | |
| Dhokkur seeking vents | cleanse | kept in "later" | | |
| Dhokkur hide as heat shielding | review | kept as a thing to take away | | |
| Julmox: the plate-footed herd that sits sealed between rains | review fills; cast bible §3 | kept | | |
| Jossur: the sky apex | review fills; cast bible §3 | kept; stoop and prey scoring moved (→ 0.2.0) | | |
| Dhuvvox: the flash swarm, sealed nodules that wake | review fills; cast bible §3 | kept as residents; the extra swarm and countdown moved (→ 0.2.0) | | |
| Fleet flier | sheet §4; review | kept; real flight | | |
| Bulloos small and great, floating, fed by vapor | cleanse | kept | | |
| Bulloo gel; fission | cleanse | moved (→ 0.2.0) | | |
| Bulloo detonation | cleanse | lost (recommended for dropping; his to confirm); flagged above | | |
| Metallovore: the metal-eating slug | review; cleanse | kept; the metal diet moved (→ 0.2.0) | | |
| Dhoggur: placid ash-forager | walk; cleanse | kept | | |
| Dhoggur's swell and fire-spit | walk; cleanse | moved (→ 0.2.0) | | |
| Ummisk: tube colony on a cushion of steam along the lava's lip | slow-ground; cleanse | kept | | |
| Ummisk's glass trail across the flows | slow-ground | lost (not built; the cleanse confirms none); flagged above | | A terrain-swap on the freeze machinery: medium to high. |
| Kettugal, the walking crucible | slow-ground | lost (not chosen); flagged above | | |
| Brazzok, the chimney-walker | slow-ground | lost (not chosen) | | |
| The lava snail's old slot | slow-ground | lost (cut) | | |
| Fire lavender, cinder crust, heatsink fungus; firevine | review; cleanse | kept | | |
| Heatsink fungus cools a room | cleanse | lost (recommended for dropping) | | |
| Fungus as a study source | cleanse | kept in "later" | | |
| Donor plants and animals; lava flea, maguana, tibidee, colossal aerofleet | review; roster json | kept where the campaign patch puts them | | |
| Eighty-four evictions | roster json | kept as the record | | |
| Beldon taming "brutal-but-possible" | kit, owner card 2026-09-12 | kept in the campaign layer | | |
| Names and the heat accent; palette diversity is law | cast bible §0, §1 | kept as art and naming direction | | |
| Art done, art owed, deploy holds | review; cast bible §2, §6, §7 | kept as build facts | | |
| The nine-mark scorecard | review | lost | A measure of the old programme. Its finding that nothing touched the ship is kept. | |

### Works, industry, the ship and the campaign

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| Whole towers: permanent, impassable, never mined or salvaged; broken works salvageable | cleanse definition | kept | | |
| Tower shadow is shade and not a roof | cleanse definition | kept as a promise's control | | |
| The tower dungeon: one large floor per tower | kit F4, owner card 2026-09-12; review | moved (→ 0.2.0, campaign layer); flagged above | | |
| Tender-Craft: learning the towers' trick and carrying it to any geyser | review slate E | kept in "later" | | |
| Geothermal vent benches | kit F6; review | kept in "later" | | |
| The beldon tibanna tap | kit F2; review | moved (→ 0.2.0, campaign layer) | | |
| The Ship Drinks the Mountain | review slate B | lost (struck); `NEEDS HIM` | | See above. |
| "Every burst scours the parked ship" | review slate B | kept, reshaped: ordinary fire and rain on the ship's outside in 0.1.0 | His ruling of 2026-11-18. | |
| Fuel-saving keel brace | cleanse next_version | lost (waived) | | |
| Garden study; floatstone door | cleanse | moved (→ 0.2.0) | | |
| Floatstone airtight ship hull | cleanse | moved (→ 0.2.0); it is the armour | | 0.1.0: the hull answer is in the first version, with a research step to prove. |
| Scanner readings | cleanse | moved (→ 0.2.0) | | |
| "Many paths to fuel": helixien gas on volcanic tiles | campaign lore | kept as a noted source line; nothing built; `NEEDS HIM` | | |
| The embargo: goods, enforcement, heat and interest, quest beats | embargo spec | kept in "later" (campaign) | Read by heading only. | |
| Inert settings knobs; world scoring of hot tiles | cleanse | lost (recommended for dropping; worldgen is forbidden regardless) | | |
| Mod Settings | cleanse; review | kept | | |

### The pipeline's own material

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The cleanse's signature (warned fire and rain, a crust, a harvest, a retreat) | cleanse definition, owner_pages | kept whole | | |
| "You settle among dark foundry towers" | cleanse definition | kept, reshaped: a crew on a stop | | |
| Forty colonists; the whole-season trace | cleanse definition | moved (first version → later) | Colony scale. | |
| The feeding contract for bulloos | cleanse definition | kept as a promise | | |
| Four offline models | cleanse owner_pages | kept | | |
| Tickets and switch-offs | cleanse next_version | kept as they stand, except where a feature moved | | |
| Eight proposed bars | cleanse owner_pages | kept as history; the thirteen promises in the design are the proposal to argue from | | |
| The walk's intended-function lines | walk | kept; only the north star and three creature lines were read | | |

## Sources read, and the count

Measured after writing (a script counted the table rows and the first words of the "what happened" column):
**17 source files, 113 rows**, of which **15 lost**, **19 record a move** (whole or in part), **4 kept, reshaped** and 0 folded into shared machinery. Every source named above is in at least one row's source column (checked by the same script).

Read whole, or every paragraph with long lines cut: the sheet; the review; the cleanse definition, owner pages and
next-version list; the owner answers; the experiences table. Read in large part: the slow-ground concepts (the
markdown's opening and its three-way table; the json's first entry). Read by heading or by search: the cast bible
(headings, shared law, name sweep and art dedup; not the cast entries); the kit (headings and the three owner cards
of 2026-09-12); the embargo spec (the law and headings); the roster json (its keys and the names in each list); the
walk (north star, and a search for three creatures); the cleanse census (every row's name, fate and built state);
the pulse def (phase lengths); the campaign lore (pressures and fuel). Not read: the cast bible's cast entries, set
pieces and art queue; the kit's six mechanic sections; the embargo spec's body; the Designer rehearsal's `NOTES.md`,
`QUESTIONS.md` and `record.json` in `design/RimMandrake/designer_codex_2026-11-09/TheForge/`; the cleanse's
`tickets.md`, `bars.json`, `models.md`, `ambiguities.md`, `review.json`, `converge.json`; the Forge table of
`special_mechanics_review_2026-10-22.md`; the two tickets the cast bible feeds (`FORGE_RULED_CONTENT_1`,
`FORGE_CYCLE_MECHANICS_1`), where the owner's rulings from the bedazzle volley are recorded and which I did not
open: the struck list in this page comes from the cleanse's summary of them, not from his words.

## The older files this design replaces, ready to delete on his word

In `design/Jawa/worldbuilding/biomes/`: `the_forge.md`, `forge_bedazzle_review_2026-09-28.md`,
`rosters/the_forge.json`.

Hold: `forge_bedazzle_cast_2026-09-29.md` (the art commission's only brief for the four natives and the floatstone
family); `kits/forge_kit_spec.md` (the engine mapping for six built mechanics, three of which the campaign layer
still owes surfaces for); `design/Jawa/tibanna_embargo_plot_spec.md` (the campaign's, not this biome's);
`design/RimMandrake/forge_slowground_concepts_2026-10-20.md` and `.json` (two unchosen creatures he may want).

Not for deletion: `design/concepts/TheForge/cleanse/` (superseded by this design, never applied; it should be re-run
from this file, not applied); the validation walk.

Before deleting: `the_forge.md` is frozen by `BIOME_FREEZE_FABLE_REVIEW_1`, is cited as the verbatim law by the
embargo spec, and is quoted in the BiomeDef's own description, which the slow-ground concepts were written from.
