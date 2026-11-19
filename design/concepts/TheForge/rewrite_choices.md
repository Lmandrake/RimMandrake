# The Forge: what the rewrite chose, what it lost, and why

## Second reader, 2026-11-18

A different agent from the one that wrote this page and the design read the sources again, starting with the ones
the first pass read by heading or not at all, and checked each idea in them against the rows below.

**Rows added: 102**, in the table "Added by the second reader" at the end of "Every idea, row by row". Four of the
first pass's rows were corrected in place and say so (the scour; the keel brace; the garden study and door; the
floatstone hull).

**The three most valuable things the first read missed.**

1. **The hull rulings are his, they are built, and one of them names this ground.** The first design said *"No
   shared system for hull wear was found in `src/`"*. `src/RimUtinni/ShipShields/` holds his eight shield rulings
   of 2026-09-02, and one is about lava: *"Landing on lava should be the worst case causing immediate severe damage
   (don't do that)."* The thermal veil is his answer to heat, *"not nearly as badly as it would in an active
   fire/volcano"*, and it runs on power, which this mountain gives free by his own word of 2026-09-29. Reading the
   built frame turned up a real doubt: its lava check looks at the whole map, and every Forge map has lava, so as
   written every landing here would take the worst case. That is filed
   (`RIMMANDRAKE_NARROW_LAVA_LANDING_BURST_WHOLE_MAP_SCAN`) and flagged in the design.
2. **The Forge's gift to the ship, by his card, was parked in 0.2.0.** His question of 2026-09-24: *"how can this
   biome uniquely add something to the ship?"* The answer on record (his card of 2026-10-03) is the spunstone hull
   and the floatstone door, both built. A stone that will not burn, grown on the ground the gas wash burns, is the
   armour; it is in 0.1.0 now.
3. **Zersium.** By his cards of 2026-10-09 the ore that makes durasteel on the ship's alloy forge has one home
   biome, and it is this one: *"I like the forge makes that mineral."* The first read has no row for it. It is the
   one thing on this mountain the ship's own machinery needs.

Close behind: his own typed words for the cycle (*"This is a biome of fire and water..."*) and for floatstone
(*"swirled stone spun sugar made into blocks. Very beautiful."*), which the first read knew only through the
cleanse's summary; the Anvil Gift, a rite he kept on 2026-10-02 in which a Jawa throws its own weapon into the lava
for its own god (*"Give him a blade and he will not come for yours. For a while."*); the cast bible's lines, never
opened by the first read (*"Half the outcrops on the skirts are stone. The other half are waiting for rain."* *"A
block of floatstone weighs what a lie weighs."*); and the embargo's second card, which had already ruled how the
clock ends.

**What changed in the design, and why.**

- *Hull:* rewritten onto the built shield frame: the lava landing, heat and the thermal veil, with their flags.
  The false sentence that no hull system exists is deleted. Ordinary fire stays. Nothing in the section is the
  second reader's invention: every wear has a source, named beside it.
- *The first design's own hull wear was a struck idea.* It put *"fire and rain on the parked ship's apron"* in
  0.1.0 and listed it as new. Rain on the ship is the scour, which he struck on 2026-09-29 with the heat exchanger.
  The rain half is taken out of 0.1.0 and asked (`NEEDS HIM` 3). By the kit's specification the rain scalds
  people, not buildings, so the promise now says that.
- *Three ship ideas he struck or cut here* are listed with dates and his words and not revived: the heat exchanger
  (`NEEDS HIM` 1, as before), the scour and the keel brace (`NEEDS HIM` 3, new). The first read called the brace
  "waived"; it was picked by card, built, and cut on 2026-10-23 under his *"I cut, you veto"* card.
- *Scope:* the garden study, spunstone hull and floatstone door moved from 0.2.0 to 0.1.0. Zersium, the Anvil Gift,
  the two wired-in giants and the zhaskel (a proposal, never admitted) are named in 0.2.0. The embargo's two ends
  and the second rite are named in "later". The dropped list gains the creatures and enrichments that were offered
  and not chosen.
- *Fuel:* the class is unchanged (emergency only). Two sourced sentences added: tibanna is not fuel, by the
  embargo's own law; and vent power is free, by his word.
- *Promises:* two added (the hull and door; the lava landing with its control). One corrected: the sleeping dhokkur
  has one quiet tell, by the cast bible.
- *Lines carried in:* his two typed passages; nine lines from the cast bible, the kit and the rites.
- *Whose word wins:* each cleanse line was checked against his dated words. The cleanse's "next version" for the
  hull and door falls to his card of 2026-10-03 and his hull ruling of 2026-11-18. The cleanse's "waived" for the
  brace is his cut of 2026-10-23, which stands. No locked Designer sheet or tree exists for this biome, so nothing
  is held for a Designer run to reconcile.

**Third run, 2026-11-18: the roster file read to its end.** The second reader's reading of
`rosters/the_forge.json` had five of its eighty-four eviction reasons cut at about 520 characters. A third run read
the file whole (634 lines: 84 evictions, 9 animals, 9 plants, 4 purged plants, 3 owed new things, 6 confidence
notes). The reading reached each file's last line; the longest line in the file is 574 characters and the reading tool shows 2,000 characters of a line, so no entry was cut. **Rows added: 24**, in the table "Added by the
second reader: the roster file read to its end". Recovered: his rulings that sent the gamma plants to the Abyss
(2026-09-20) and the dewback to the oasis (2026-09-06); his card of 2026-09-09 behind eight cuts and two moves;
the roster's own test, *"no heat story"*; an open flag that nobody measured whether the kept ground animals can
live at Forge heat; and the pointers the evictions leave for other biomes' rosters. The design changed in two
facts: the tibidee is wired in the campaign patch, and the lava snail's cut is dated 2026-10-19, Pacific.

**Measured counts** (script: `design/RimMandrake/biome_recheck_row_check_2026-11-18.py`, and the readers' own
source lists): **239 rows** (113 from the first read, 102 added by the second reader, 24 by the third run); **30 lost**, **17 moved** and 6 more that record a move in part, 5 kept and reshaped, 1 folded into shared machinery, 185 kept, 1 the script could not class (a first-read row that begins "hiss kept"). **Sources: 32 read to the end,
12 read in part, 12 not opened.** Read to the end: the three files this page lists for deletion (the roster file
by the third run, with nothing cut); the cast bible; the kit; the
embargo spec; both slow-ground files; nineteen ledger items (the cycle, the ruled content, the enrichment and its
seven splits and remainders, the sitting, the roster reconcile, the slot card, the voices audio, the first script,
zersium, the ship's alloy forge, the ship gifts); his answers and the questions he was shown; the rehearsal's
notes; the cleanse's owner pages and next-version list. Read in part: the rehearsal's questions (all six, each
paragraph cut at about 800 characters); the walk (every line, each cut at 500 characters); the shield design (his
rulings table and the thermal veil section) and two of the frame's source files; the rites pass (the Forge section
and the summary rows); the watcher pitch (the Forge row); the mechanics review (the Forge table, whole); the
2026-10-23 cut digest (the brace's entry); the built spunstone parts (labels and descriptions); and two long build
logs, `FORGE_MECHANICS_1` and `THEFORGE_RM_MOD_BUILD_1` (headings and every line naming the owner). Not opened by
this reader: the rehearsal's `record.json` and `designer_brief.md`; the cleanse's definition (the first read read
it whole), `ambiguities.md`, `models.md`, `tickets.md`, `bars.json`, `census.json`, `review.json` and
`converge.json`; the experiences table, the campaign lore and the pulse def (the first read read the parts that
bear on this biome). Every file not read to the end is one that stays.

DELETE-READY: yes

Restated 2026-11-18 after the roster was read to its end. The line covers three files in
`design/Jawa/worldbuilding/biomes/` and nothing else: `the_forge.md` and `forge_bedazzle_review_2026-09-28.md`
(read to the end by the second reader, on that reader's statement above) and `rosters/the_forge.json` (read to the
end by the third run, nothing cut; every idea, ruling and owner word in it has a row). What the first read says to
do before deleting still stands. Two more. The roster file is the only place the eighty-four evictions and their
reasons are written whole; the rows added from it carry his rulings and the pointers to other biomes, and if
another biome's roster work wants the full table it should be copied out first. And the roster is cited by path in
comments in `src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheForge.xml` and
`src/RimMandrake/TheForge/Defs/BiomeDefs/RM_TheForge_Biome.xml`, in the kit, and in the open item
`FORGE_MECHANICS_1`; those lines should point at this page before the file goes.

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
- **Garden study, floatstone hull and door:** next version → 0.1.0 (the first read had 0.2.0; moved by the second
  reader). The hull is the Forge's armour under his ruling, and with the door it is the Forge's gift to the ship by
  his card of 2026-10-03.
- **Named in 0.2.0 by the second reader, not moves against the cleanse:** zersium and the Anvil Gift (campaign
  layer); the tibidee and the greater bulloo; the zhaskel (a proposal); ash and rain on the shield frame (asked).
- **Scanner readings:** next version → 0.2.0.
- **Campaign gas tap, testing ring, one tower floor:** next version → 0.2.0, campaign layer.
- **Stayed "later" from the cleanse's "next version":** fungus study. Not a move.
- **Kept as the cleanse recommended (retire):** fungus cooling, bulloo detonation, inert knobs, world scoring.
- **Settling the mountain; forty colonists; the full-season trace:** first version → later.
- **New, not in any source:** the Empire's troops as newcomers to the cycle (a reading of built behaviour: the
  phases do not ask who is standing where); fire on the parked ship's apron (the first read also listed rain
  here; rain on the ship is the struck scour, see the second reader's section); "never park on crust"; the reading of the mountain as the crew's own god's ground, from the sheet's line on Jawa sacred
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
*pulse def* = `src/RimMandrake/TheForge/Defs/GameConditionDefs/RM_ForgePulse.xml`. Added by the second reader:
*shield rulings* = `design/Jawa/proposals/ship_shields_deep_design.md` and `src/RimUtinni/ShipShields/`; *ship gifts*
= `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md` and
`src/RimMandrake/TheForge/Defs/ThingDefs_Buildings/RM_SpunstoneParts.xml`; *cycle item* =
`infrastructure/state/items/FORGE_CYCLE_MECHANICS_1.md`; *ruled content* =
`infrastructure/state/items/closed/FORGE_RULED_CONTENT_1.md`; *enrichment* =
`infrastructure/state/items/closed/FORGE_GPT_ENRICHMENT_1.md` and the items split from it; *slot card* =
`infrastructure/state/items/closed/FORGE_SLOT_DECIDE_NEEDS_A_DESCRIPTION.md`; *zersium items* =
`ZERSIUM_FORGE_BIOME_1.md` and `SHIP_ALLOY_FORGE_1.md` in `infrastructure/state/items/`; *rites pass* =
`design/Jawa/biome_rites_pass_2026-10-01.md`; *watcher pitch* = `design/RimMandrake/watcher_creatures_pitch.md`;
*rehearsal* = `NOTES.md` and `QUESTIONS.md` in `design/RimMandrake/designer_codex_2026-11-09/TheForge/`; *mechanics review*
= `design/RimMandrake/special_mechanics_review_2026-10-22.md`; *fluff cuts* =
`design/RimMandrake/fluff_cuts_2026-10-23.md`.

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
| "Every burst scours the parked ship" | review slate B | lost (struck 2026-09-29 with the heat exchanger); `NEEDS HIM` 3 | Corrected by the second reader: the first read kept it reshaped as fire and rain on the ship's outside. Ordinary fire stays in 0.1.0 and is no part of the struck idea; rain on the ship is the struck idea. | |
| Fuel-saving keel brace | cleanse next_version | lost (cut 2026-10-23 under his "I cut, you veto" card); `NEEDS HIM` 3 | Corrected by the second reader: the first read called it waived. | Revert one commit. |
| Garden study; floatstone door | cleanse | moved (cleanse next version → 0.1.0) | Corrected by the second reader: the first read had 0.2.0. His card of 2026-10-03 makes these the Forge's gift to the ship. | |
| Floatstone airtight ship hull | cleanse | moved (cleanse next version → 0.1.0); it is the armour | Corrected by the second reader: the first read had 0.2.0 and named 0.1.0 as the other choice. | 0.2.0: the first stop has wear and no local answer. |
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

### Added by the second reader

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| His own words for the cycle: *"This is a biome of fire and water. The open lava is horrible, hot, deadly..."* through *"the whole thing melts back into lava again, destroying them."* | cycle item | kept, quoted in the design | The first read took the cycle from the cleanse's summary and never quoted the man who typed it. | |
| His own words for floatstone: *"Ultra-light pumice made of what looks like spun glass whirled into tangles... the walls it makes look like swirled stone spun sugar made into blocks. Very beautiful."* | ruled content; cast bible §4 | kept, quoted in the design | | |
| The spunstone hull and the floatstone door as the Forge's gift to the ship, by his card of 2026-10-03 | ship gifts | moved (first read 0.2.0 → 0.1.0), by the second reader | Hull is in 0.1.0 by his ruling of 2026-11-18, and this is the only armour the sources give the Forge. Both parts are built. | Leave it in 0.2.0: the first stop on the Forge then has wear and no local answer to it. |
| His question to every biome, 2026-09-24: *"how can this biome uniquely add something to the ship?"*; and the item's own line, *"the gravship becomes a scrapbook of everywhere it has been"* | ship gifts | kept, quoted in the design | | |
| *"Landing on lava should be the worst case causing immediate severe damage (don't do that)."* | shield rulings | kept in 0.1.0 (built in the campaign tier), quoted | The one hull ruling that names this biome's ground. The first read did not open the shield frame and wrote that no hull system exists. | |
| The built lava check looks at the whole map, so every Forge landing would take the burst | shield rulings | kept as a flag (`UNSETTLED`), and filed as `RIMMANDRAKE_NARROW_LAVA_LANDING_BURST_WHOLE_MAP_SCAN` | Read from source, not run. His words describe a mistake a pilot can avoid. | Leave it: the Forge becomes the one biome that damages every ship on arrival, which nobody ruled. |
| The thermal veil: *"reflect all external heat outward with a mild mirror sheen... but not nearly as badly as it would in an active fire/volcano. Just use power for fuel"* | shield rulings | kept in 0.1.0 (built), quoted | | |
| The heat tracker's threshold (58 °C outdoors, a heat wave, or the game's lava-flow condition) against the sheet's 42 to 56 °C | shield rulings; sheet §0 | kept as a flag (`UNMEASURED`) | On some Forge maps the built heat wear would never fire. | |
| The light screen: *"handle wind, ash, vapor, bio contamination, spores, smoke, sand, and rain damage completely as well as repels small animals"* | shield rulings | kept in 0.2.0 as a build the frame owes, and asked (`NEEDS HIM` 3) | The built frame sees particulate only as pollution or sand-carrying weather; nothing the Forge mod ships sets that. | 0.1.0: a small build, but the only source that put rain on the hull was struck. |
| No hard landing gate: *"The environment is hostile and immediately goes to work on the ship. The ship will know what's visibly dangerous and will advise course of action, but no more than that."* | shield rulings | kept | The advisory letter and never a refused landing. | |
| *"Slow pressing things move through all shields... This is why nothing 'holds out water'"* | shield rulings | folded into shared machinery | True of every biome's shield. | |
| The scour: *"every burst scours the parked ship (minor exterior damage/ash filth on unroofed ship tiles during boiling rain)"*, to stay *"annoyance-grade, not hull-loss-grade"* | review slate B; ruled content | lost (struck 2026-09-29 with the heat exchanger); `NEEDS HIM` 3 | A ship idea he struck is listed, not revived. The first read's row above kept it reshaped; that row is corrected. | |
| The floatstone keel brace: braces *"threaded through a gravship"* that cut launch fuel and *"ring glassily at launch"* | enrichment §1; fluff cuts | lost (picked by card from the 2026-09-30 consult, built, then cut 2026-10-23 under his *"I cut, you veto"* card); `NEEDS HIM` 3 | The cut's stated reason: *"simplify or cut: small effect; the only ship hook"*. The first read called it waived. | Revert commit `061f5d693`. |
| The brace's open question: should it also raise how much substructure a ship can hold, since the game has no payload | enrichment (keelwork remainder) | lost with the brace | | |
| Zersium: a rare local ore with one home biome, and that biome is the Forge; *"I like the forge makes that mineral."* Steel and zersium make durasteel on the ship's alloy forge | zersium items | kept in 0.2.0, campaign layer; now in the design under what the crew takes away | Canon material, so campaign tier. It is the one ore on the planet the ship's own forge needs from one place. The first read has no row for it. | |
| Zersium placement as read live 2026-10-09: four new Forge maps carried 24, 0, 0 and 0 ore cells | zersium items | kept as a build flag | Placement owed a retune. | |
| The alloy forge aboard: *"Durasteel earlier, plasteel later"*; exotic metals never forged | zersium items | kept as a fact of the ship, not of this biome | | |
| Asteroids as a second zersium source: *"It's ok if it's both"* | zersium items | kept elsewhere (the asteroid item) | | |
| Three enrichments offered on 2026-09-30 and not picked: The Last Lift, Quench Crossings, The Anvil Answer | enrichment | lost (not picked by card) | Only the three names are in any source; what they were is not on disk in the files read. | |
| Spunstone bonding: *"material science, not a vent machine"*; a study of ripe gardens, a hidden research project, a letter naming who studied the samples | enrichment §2 | moved (first read 0.2.0 → 0.1.0), with the hull and door it unlocks | | |
| Foundry salvage as the second thing to study | enrichment (spunstone sources); rehearsal | kept in 0.2.0, campaign layer | The patch exists by the rehearsal's reading. | |
| *"High-speed doors and advanced structural parts"*, which became the floatstone door and the spunstone hull | enrichment (spunstone sources) | moved (first read 0.2.0 → 0.1.0) | | |
| The door's own text: *"so light that a push swings it wide and it falls shut on its own weight a breath later. Nobody slows for it."* | ship gifts | kept, quoted in the design | | |
| The four voices as written: a *"subterranean, turbine-like throb"*; vents coughing; *"a deafening hiss"*; basalt that *"ticks and sings like glass"*; and before the melt *"the harmony drops out and a deep cracking pulse begins"* | enrichment §3 | kept in 0.2.0 (the first read's row), lines carried here | | |
| *"Just use vanilla until we get around to sound work."* (2026-10-03) | enrichment (voices audio) | kept | | |
| Steam fronts as built: the game's blind smoke, puddles, and added heat through ordinary heatstroke; vapour animals unharmed; four builder choices still owed his review | enrichment (plume fronts) | kept in 0.2.0, with the owed review noted | | |
| By source reading, the built front's heat crosses walls and roofs | rehearsal | kept as a build flag | It contradicts his answer of 2026-11-10 (*"Walls stop the immediate front"*); the build owes the fix before 0.2.0. | |
| Dhokkur ways as built: a polished trail it keeps; a wall in its way is moved whole, then packed up, then damaged; two questions to him still open (what shoving means; whether tracks fade) | enrichment (dhokkur ways) | kept in 0.2.0, open questions noted | | |
| By source reading, the dhokkur goes to the nearest vent and never revisits its saved tracks | rehearsal | kept as a build flag | "The giant has a road" (moment 10) is not true of the build as read. | |
| The dhuvvox clock in full: a click and sparks as each nodule opens; a countdown; slowing in the last quarter-hour; *"every survivor visibly curls back into a persistent nodule; none vanishes"*; a scuttle that slows | enrichment §7 | kept in 0.2.0 | The pawn stays its own nodule, by his card of 2026-10-08. | |
| The dhoggur in his words, by card 2026-10-16: *"a bizarre creature that constantly snuffles and digs at the ashy minerals freshly deposited by volcanic sputter. Very tough heat resistant hide."* | slot card | kept, quoted in the design | | |
| The jobbosh, offered for the same slot and dropped: *"insufficiently alien"* | slot card | lost (dropped by card 2026-10-16) | | |
| The dhoggur's swell as he settled it 2026-10-16: only attacks set it off; death on shrinking kept, *"it is the price of the swell"* | rehearsal; walk | kept in 0.2.0 with both rulings | | |
| The crescendo anole, the small ground slot the dhoggur took | review; roster json | lost (replaced by card 2026-10-16) | | |
| *"Wire in all waiting"* (2026-09-29): the tibidee and the great aerofleet into the rosters, the fleet flier's finished art, the flash-growth class onto the plants, three held art debts | ruled content | kept; the two giants are now named in the design's 0.2.0 | The first read left the giants to "where the campaign patch puts them". The great aerofleet is the built greater bulloo; the tibidee's state was not checked. | |
| Fumeriders: the sheet's name for the drifting jelly-fleets | sheet §4; roster json | kept, reshaped: the built free tier calls them bulloo and greater bulloo; the name fumerider is lost | The built roster's names. | Rename them back: labels only. |
| The scald-armour stat left *"granted-by-nothing ON PURPOSE"* after the gear economy was struck | ruled content | kept as a build fact | | |
| The re-score at the cycle's close: the Forge's two remaining gaps (touching the ship; discoverable technology) to be recorded as *"owner-accepted misses, not silent drops"* | cycle item | kept as history | The ship lens reopened the first; it is `NEEDS HIM` 1 and 3. Spunstone answered the second. | |
| *"lets just keep vent-based power as an option (already present in game)"* (2026-09-29) | ruled content | kept, quoted in the design | It is why the thermal veil's power is free here. | |
| Vent smelter, kiln and forge: no fuel, no power, on a geyser; reported shipped as defs 2026-09-28, then struck the next day | kit F6; review; ruled content | lost (struck), with a flag | `UNSETTLED`: whether the three defs are still in the campaign tier. The Flawed Masterwork rite needs one. | |
| The Anvil Gift: a weapon *"thrown into the melt by its last user"* at a lava lake; a line hammered into an obsidian slab *"among the twisted remains of older weapons fused to the rock"*; readable only in still heat | rites pass | kept in 0.2.0, campaign layer; now moment 11 in the design | Kept by him 2026-10-02. A Jawa giving up a weapon to its own god on that god's mountain is the lens. The first read has no row for either rite. | |
| *"This is where the sun hammers. Give him a blade and he will not come for yours. For a while."* | rites pass | kept, quoted in the design | | |
| *"an explosion burning your own stuff pleases him; he's fed, then lenient a while"* | rites pass | kept in the campaign layer | The gods' engine. | |
| The Flawed Masterwork: a masterwork finished at a vent forge, and its maker scratching one flaw into it *"so the crown never quite fits"*; found on *"a tower tender's tool rack... where every tool bears the same small scratch"* | rites pass | kept in "later" | Kept by him pending an engine check. It needs a masterwork, a vent forge and the inside of a tower: not a stop. | |
| The zhaskel: *"an ember-dark plated sitter in cooled-crust fissures"*, never in lava | watcher pitch | kept in 0.2.0 as a proposal | Pitched under his 2026-10-08 ruling that every biome gets a watcher; never admitted at a sitting. | |
| *"Tibanna is not propane."* No route from one to the other | embargo spec §0 | kept, quoted in the design's fuel answer | It settles that a hold of tibanna is not fuel. | |
| The game has no ammunition, so the embargo bites through the price of making blasters and through trader stock | embargo spec §1 | kept in "later" (campaign) | | |
| Metered and unmetered gas; unmetered gas is contraband and hums | embargo spec §2, §4 | kept in "later" (campaign) | | |
| Buying the Empire's gas draws no attention: *"the Empire wants you dependent"*; poaching the herds draws it every time | embargo spec §4 | kept in "later" (campaign), with a flag | `UNSETTLED`: no source ties a poached beldon to the search clock a stop runs on. | |
| The fixer who buys kyber sells tibanna: one Hutt contact, both trades | embargo spec §4 | kept in "later" (campaign) | | |
| The clock is never a gauge; it shows as traders' shelves thinning and prices climbing; the crew's own smuggling speeds it: *"Getting armed makes everyone else's drought worse"* | embargo spec §5 | kept in "later" (campaign) | | |
| Seven beats: the Meter, the Ration, the Hutt lane, the Poach, the Shipment, the Gun-Runner, the Resolution | embargo spec §6 | kept in "later" (campaign) | | |
| Arming the resistance *"buys them time, never victory — no uprising, no Rebellion, no liberation event"* | embargo spec §6 | kept as a rule | | |
| Card T1, 2026-09-12: every other tibanna source in the mod stack is cut | embargo spec | kept as a built rule | | |
| Card T2, 2026-09-12: break the meter (the garrison *"must be beatable"*), or the Empire wins the clock | embargo spec | kept in "later"; now stated in the design | The first read's row called the resolution unruled in shape; it is ruled. | |
| *"They don't need the Forge; they need everyone else not to have it."* | sheet §8; embargo spec | kept, line carried here | | |
| *"The Empire holds the gas, and everyone's ammunition knows it."* | sheet §5 | kept, line carried here | | |
| The dhokkur's text: *"Half the outcrops on the skirts are stone. The other half are waiting for rain."* ... *"It is not angry. It has never needed to be. Its hide turns the boiling rain, and the boiling rain is the worst thing this mountain knows how to say."* | cast bible §3 | kept, quoted in the design | The first read did not open the cast entries. | |
| The dhokkur's tell: *"the gutter-lines converge too regularly for stone. The tooltip lies; the sprite may only whisper."* | cast bible §3; enrichment §6 | kept; the design's promise is corrected to allow the one quiet tell | The first read's promise said it cannot be told from an outcrop at all. | |
| The dhokkur's body: *"more cistern than face"*; rain gutters running to a drinking maw; *"the one cast member painted by the water, not the fire"* | cast bible §3 | kept as art direction | | |
| The julmox's text: *"a row of dull kettles on the skirts"*; *"they turn stone-film into meat. Pasture is wherever it last rained."* | cast bible §3 | kept, quoted in the design | | |
| The jossur's text: *"The columns are pasture, and every pasture gets its wolf"*; grounded, *"folded weapon"*, not walking bird; *"the reason the herds keep their young in the middle of the smoke"* | cast bible §3 | kept, quoted in the design | | |
| The dhuvvox's text: *"think them slag... and the slag hatches"*; *"The old hands tell time by them. When the dhuvvox run, you reap; when they still, you are already late for shelter."* | cast bible §3 | kept, quoted in the design | | |
| The garden's text: *"light enough that a grown one strains at its own root"*; *"the most beautiful quarry on the planet"*; *"the one form the lava never gets back"* | cast bible §4 | kept, quoted in part in the design | | |
| The stone's text: *"A block of floatstone weighs what a lie weighs."* *"The Farmers sell it by the promise instead of the weight. Nobody has ever asked for the weight back."* | cast bible §4 | kept, quoted in part in the design | | |
| A built floatstone wall is a tinted ordinary wall; the spun-sugar swirl needs its own wall art, *"only if the owner asks"* | cast bible §4, §7 | kept as a build fact, flagged | `UNSETTLED`: his words say the walls *look* like spun sugar, and today they do not. | |
| The crust's three grounds: basalt shingle (*"the treasure floor"*), pumice chunk, glowing crack | cast bible §5; cycle item | kept | | |
| Flight frames for the jossur are not drawn; it flies without a wing-beat | cast bible §3, §7 | kept as a build fact | | |
| The tower floor as written: a pocket map at furnace heat, melt channels, a salvage cache; *"You leave the way you came, richer or cooked."* | kit F4; review | kept in 0.2.0, campaign layer; line carried into the design | | |
| The tower's garrison was never cast: no tender creature exists | review | kept as a build fact | The 0.2.0 tower owes it. | |
| Floor after floor by chained doorways | kit F4 | lost (one floor ruled 2026-09-12) | *"untested engine territory"*; more floors only *"if a quicktest proves the seam clean"*. | |
| The Contagion's probe as an event: a tongue of red pushed up the slope that blackens and dies within hours. *"You can watch it lose."* | kit F5 | kept in 0.2.0, campaign layer; line carried into the design | | |
| The dying creep is in no biome's plant list, so it can never take hold | kit F5 | kept as a rule | | |
| Lava by the game's own fields: shallow lava can be walked and burns and ignites; deep lava cannot be entered | kit (header) | kept as "lava is lava" | | |
| The rain is *"brutal to stand in, survivable to sprint through"* | kit F1 | kept, line carried here | | |
| *"Farming here means learning the mountain's breathing"*; growth in the window many times normal and near nothing outside it: *"the RHYTHM is the mechanic"* | kit F1 | kept as description; farming itself is "later" | A crew on a stop does not farm. | |
| Sky animals *"never wander off across the ash like ground animals; the columns are their pasture, and hunting them means going where the columns are"* | kit F3 | kept | | |
| Drifters are not scalded: *"they live in the steam"* | kit F3 | kept as a build fact | | |
| Fleet fliers *"race in, eat fireweed, and retreat before they perish"* | sheet §4; kit F3 | kept | | |
| The beldon as shipped by its donor hunts and bursts when it dies; the hunting was stripped to match *"placid"* | roster json | kept as a build fact (campaign layer) | | |
| The lava flea: *"the one ground herd"*, a hopper that carries cargo | roster json | kept in the campaign layer | A pack animal is a Jawa thing; no source builds on it. | |
| No fish: *"no persistent liquid water"* | roster json | kept as a rule | | |
| Purged plants; *"the Forge is clean heat, not contamination"* | roster json | kept as the record | | |
| Fireweed and fire lavender are Earth plant names, flagged for his eye and never ruled | roster json | kept as an open flag | | |
| Magma cactus, tinkle grass, the geyser grasses and bindweed | review; roster json | kept where the built roster has them | | |
| Cinder crust has no picture and no written identity | review; cast bible §8 | kept as a build fact (owed) | | |
| The brazzok's lore: herds standing in lines *"reading as towers on the skyline"*; *"Rumour says the ancients grew the first towers from brazzok shells."* | slow-ground | lost (not chosen 2026-10-20), line carried here | | |
| The kettugal's detail: *"slow because the bowl must stay level"*; hit, *"its bowl spills burning slag"*; sheared for slag beads | slow-ground | lost (not chosen 2026-10-20) | | |
| The ummisk as pitched: *"it is the moss that drinks between fall and flash: a walking colony"*; no head and no face | slow-ground | kept as its description | | |
| His order for the slot: *"Create something truly alien and interesting based on the Forge description. Be impressive."* | slow-ground | kept as the record | | |
| The sheet's light and shape: *"the herds' soft enormous rounds against hard geometry"*; *"in the melt, slow deliberate movement that is not alive"*; beldon amber over everything | sheet §9 | kept as art direction, lines carried here | | |
| Foundries *"sunk deep into the magma below and yet remaining whole"* | sheet §8 | kept as the towers' lore | | |
| Sh'kaar's lava lakes and craters; the ancient vent as *"the right kind of joke"* | sheet §8 | kept in the campaign layer | The Anvil Gift stands on the lake. | |
| *"The fire that owes nothing may not be taken."* *"the one flame older than the theft"* | sheet §8 | kept, lines carried here | | |
| An older document puts this massif on the Scald rim beside two other biomes; the measured map does not: *"Sh'kaar's ownership stands; the geography updates"* | sheet §0 | lost | The planet is painted once, at the end. | |
| Three things owed to a canon sitting: the witnessed-fire precept into the faiths document, the smeltery into the planet's history, the Empire's operation into the faction roster | sheet (Owed) | kept in "later" (campaign) | | |
| The rehearsal's finding that on the free tier the ruined works are *"largely a description"* | rehearsal | kept: it produced his first answer, and promise 1 | | |
| Three drafted questions he was never shown: which scene is shown first; what a successful trip onto the crust should buy; what a crew can do about the jossur | rehearsal | kept as open | The second is flagged in the hull section. | |
| Five risks found by reading source, among them a survivor left on returning lava when no safe cell is near, and crust left behind if the cycle is ended early | rehearsal | kept as build notes for the next Designer run | The first breaks the design's promise that no pawn vanishes. | |
| Blue gel has no built use; the greater bulloo is not bound to the columns | rehearsal; cleanse | kept as build facts | "Blue gel" under what the crew takes away is, today, a thing to sell. | |
| The 2026-10-22 review's calls: the tower, *"decide whether the Foundry tower is real"*; the ummisk, *"keep as scenery"*; the brace, *"simplify or cut"* | mechanics review | kept as history | The tower call was never put to him; the first read placed the tower in 0.2.0, campaign layer. | |
| The walk's list of theories already ruled out | walk | kept in the walk, which stays | | |

### Added by the second reader: the roster file read to its end

A third run, 2026-11-18, read `rosters/the_forge.json` from its first line to its last (634 lines, 84 evictions,
9 animals, 9 plants, 4 purged plants, 3 owed new things, 6 confidence notes), with no line or reason cut. The rows
below are what that reading found without a row.

| idea | source | what happened | why | the other choice, and its cost |
|---|---|---|---|---|
| The roster's admission test as it was applied animal by animal: *"no heat story"*; *"nothing unadapted admits to the massif"*; *"few means few"* (said of a slow producer that passed on speed and still went) | roster json | kept as the roster's rule | It is the sheet's test (the flash-interval, or the sky) turned into a reason on each of the eighty-four rows. | |
| The gamma and septimum plants sent to the Abyss: *"owner ruling 2026-09-20, flora move approved; owner review 2026-09-11 (move)"*; the move mapping's claim that two of them were already there was *"MEASURED FALSE (audit 2026-09-12)"*, so they were added to the Abyss roster and not dropped | roster json | kept elsewhere (the Abyss) | His ruling, as the roster records it. These are three of the five reasons the earlier reading cut at 520 characters. | |
| The dewback sent to the oasis: *"RULED move (owner 2026-09-06...)"*, *"the dew-drinking lizard was mis-cast to LavaField"* | roster json | kept elsewhere (the Weeping Stones' roster) | | |
| His card of 2026-09-09 on Earth-nameable animals, planet-wide: the catfish (*"a catfish on a lava massif"*), brown bat, mole, axolotl, land octopus and night mule cut here; and under the ban on retextured Earth animals, the sonar rabbit and the tox sheep | roster json | lost (cut) | His card and the ban it made. | |
| His card of 2026-09-09, ruling 3: the mudhorn *"kept as the shrubland's ONE huge-predator icon exception"*, and the massiff to the shrubland's medium band | roster json | kept elsewhere (the arid shrubland's roster) | | |
| The cinderlisk: cut with the whole "-lisk" clade on 2026-09-10; *"the defName does not load"*; this roster still listed it as an import until 2026-09-21 | roster json | lost (cut) | The fourth of the five reasons cut short before. | |
| Animals this roster sent to a named home: the shyrack to the Desert (*"slow cave-mouth ambusher"*), the iriaz to the grasslands (*"belongs with the Pyrelands ash-grazers"*), the scavrat to the Fall Line (*"the name is the job"*) | roster json | kept elsewhere | Where each landed after the later sittings was not checked by this reader. | |
| Pointers the evictions leave for other rosters without moving the animal: the ray hound (*"Rust Cathedral lane if anywhere"*), the thunderbeast (*"Stormwall/wasteland lane, not vulcanism"*), the bloodletter petrel (the Wasteland's), the skalder and the uvak (*"that roster's call, not the Forge's"*), the crystal mantis (caverns or poison forest) | roster json | kept as the record | These are the "where an animal was sent from" notes the paragraph under DELETE-READY says to copy out first. | |
| The other reasons an animal was refused: no standing water for fish, tadpoles and toads; the pollution register (*"the Forge's air is steam and ash, not smog-lure country"*); the lush register (the jungle rancor, the marsh haunt, the kaadu); a Gauranlen creature that *"does not function wild"*; a Final Fantasy animal; hive queens, because *"infestation axis is not wild-roster business"* | roster json | kept as the record | | |
| Six chimeras judged by the sheet's heat law and not by their name prefix: `GRim*=Grindterra homeless; GR_*=VGE chimeras judged per sheet law` (the roster's words, correction pass of 2026-09-09) | roster json | kept as the record | All six were refused for no heat adaptation. | |
| *"ONE roster for all three defs"*: the zones differ by height, and *"the sheet names no per-def fauna split"* | roster json | kept as a build fact | The first read's row covers the three defs as one place; this is the cast's side of it. | |
| *"kept ground fauna tolerate 42-56 °C"*: marked UNMEASURED; the animals were picked by their descriptions because the register carries no heat-comfort figure | roster json | kept as a flag (`UNMEASURED`) | Nothing in this file closes it. Whether the kept ground animals live through Forge heat is a live read. | |
| The lava snail as the roster cast it: *"lives between the rain-flashes by being too slow to care"*; the Grindterra retexture of it *"never gets a home (owner card)"* | roster json; slow-ground | lost (cut by his card of 2026-10-19 with seven other vanilla rows; the ummisk took the slot the next day) | The roster file was never updated after the cut and still lists the snail as an import. The first read's row "the lava snail's old slot" is the same loss. | |
| The maguana: a *"magma-patterned camouflage lizard"*, *"moved from the Pyrelands cast where it had no story"*; the roster's weight for it and the wired weight differ, *"a pre-existing tuning drift... flagged for whoever owns fauna density tuning"* | roster json | kept in the campaign layer, with the flag | The fifth reason cut short before. A weight is tuning and never a bar. | |
| His review of 2026-09 (the round-two move mapping) on the two giants: the great aerofleet is a *"rare creature wherever normal aerofleets end up"*; the tibidee belongs in *"volcanic areas"* | roster json | kept; the tibidee is wired in the campaign patch (read in `WildAnimals_TheForge.xml`) | The second reader left the tibidee's state unchecked; the design now says it is wired. | |
| The aerofleet kept past the planet-wide trim of animals that live in too many biomes, because the sheet names the Forge its home: *"flagged for owner review"* | roster json | kept as an open flag | Never ruled in this file. | |
| The lava flea's origin: *"SW canon lava-country herd hopper (Mustafar)"*, refused by the dune sea for its size and given a home here; it *"grazes the flash-flora at the skirts"* | roster json | kept in the campaign layer (the second reader's row), detail carried here | | |
| Fireweed is the roster's commonest plant and its *"SIGNATURE"*, on a borrowed body: *"fiber yield needs the FORGE_MECHANICS_1 reconcile"* | roster json | kept as a plant; the fibre economy is lost (the first read's row) | | |
| Fire lavender is *"the one donor plant that literally lives at Forge temperatures"*; the heatsink fungus is the sheet's *"even trees of shocking tolerance"*; both were ported from the retired caverns donor on 2026-09-20 | roster json | kept as build facts | | |
| The crust as the roster names it: the sheet's *"beautiful heat-resistant mosses"*, a *"crust form on the rock between flashes"*, on a def shared with the Rot's spore kit | roster json | kept, reshaped: the built Forge has its own plant in that place, cinder crust | The review says cinder crust has no written identity; this line is the nearest thing to one. | |
| The geyser grasses and bindweed are here by freeze ruling R12: *"the Forge is the geothermal field's densest point; geyser flora is its ground truth"* | roster json | kept (the second reader's row), reason carried here | | |
| The three things the roster said were still owed: fleet fliers, because *"no small donor flier passes heat-adapted"*; the tibanna gland on the beldon, with a herd harvest system; the corpse-ring as an *"event, not roster"* | roster json | kept; each has its own row above | | |
| The beldon's change is his *"adjust-and-keep pattern (owner card 2026-09-09), same treatment the Scald gave the sandos"*; its weight is held near zero | roster json | kept as a build fact (campaign layer) | | |
| The roster's law sources: the sheet's sections 4 and 6, freeze ruling R12, the assignment prep's section 9, his cards of 2026-09-09 | roster json | kept as the record | The three files other than the sheet were not opened by this reader; none is on this page's delete list. | |

## Sources read, and the count

The second reader's counts and source list are at the top of this page; what follows is the first read's.

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
