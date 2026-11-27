# Creature size verdicts: the animals drawn off vanilla's size curve

Item `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE`. Judge: run `rm-detached-bench-creature-sizes-judge-thirty-nine-off-cur-1795766883`
(a fresh judge; it made none of the work it judges), 2026-11-27. The machine-readable verdict is
`creature_size_verdicts_2026-11-27.json` beside this file; `python3 src/RimMandrake/Utils/size_verdict_check.py
design/RimMandrake/creature_size_verdicts_2026-11-27.json` says whether the fixer changes are in the defs.

## The question and how it was judged

The question: `art_size_audit.py` lists each animal REVIEW that draws under about 0.5x or over about 2.1x of what
vanilla draws for its body size. Is each one MEANT to read that tiny or that huge? Two more rows were added:
RSW_CrimsonOpee (two owner marks disagree) and RM_Summ (an owner order for its donor).

- The audit was run again on 2026-11-27 over the full load set. It lists 36 REVIEW animals.
  One SWBestiary beetle larva has left the list since 2026-11-03 (`art_size_audit_2026-11-03.md` names it).
- Each animal was drawn at its true size on the cell grid, beside a vanilla colonist and a vanilla rat, with the
  project's renderer (`src/RimMandrake/Utils/art/scale_panel.py`).
- Each draw was compared with the size words in the animal's own description, its biome design and the owner's
  orders. Body size is a tuning number, so it decides nothing here. The test is what the player sees.
- The level that is enough: an animal whose look contradicts what its fiction says about its size, or an owner
  size order that is not kept.

## KEEP (35)

The fiction of each of these names a small size, or says nothing that the draw contradicts. Vanilla draws small
animals far larger than life (a rat is about one cell), so a creature that is meant to be smaller than a rat must
draw under the curve. The owner has himself ordered animals at 0.2 and 0.3 cells (RM_ElectricTick, RM_Dustflutter,
RSW_Faa, RSW_Mee).

| animal | draws (cells) | why it is meant to read so |
|---|---|---|
| RM_Aluun | 0.35 | a fan shell grown on a kelp stem; "a column of small windows" |
| RM_Grusk | 0.34 | a wedge of shell cemented to a pillar; "a thumb of dark meat" |
| RM_Haarn | 0.56 | "the size of a helmet" (the audit's FICTION 'giant' hit is the word "the giant's", which names another animal) |
| RM_Hessal | 0.38 | two crystal shells; "a patch of frost lying on the floor" |
| RM_Immu | 0.30 | "finger-long"; hides inside a dead hessal shell |
| RM_Karrud | 0.44 | "palm-wide" |
| RM_Nissik | 0.30 | "hand-sized"; "forty in a stride" |
| RM_Oomal | 0.50 | "arm-long brine-eel" |
| RM_Sallik | 0.33 | "thumb-sized crab-thing" that becomes a pebble |
| RM_Thollim | 0.40 | a pair of valves half down in the sediment |
| RM_Otheska | 0.45 | a flat oval shell, a slow detritivore |
| RM_Lunoowa | 0.45 | a shed pane of waveglass, settling |
| RM_Weloon | 0.45 | a felt-textured shell at the edge of a shed pane |
| RM_Noohm | 0.45 | "a little solar sail" |
| RM_Oovanam | 0.45 | a flattened crawler that sifts ash |
| RM_Chittik | 0.50 | "finger-long vermin", always a swarm |
| RM_ContagionIkee | 0.45 | an eye on a knot of tendrils that hides in crevices; the plain RM_Ikee draws 0.50 |
| RM_Gripper | 0.45 | "a fist-sized beetle" |
| RM_Gristleswarm | 0.50 | "a knee-high scuttler"; it draws to a colonist's knee |
| RM_SootGristleswarm | 0.50 | "the same animal run through the chimney" |
| RM_Vennick | 0.35 | "a fist-sized silk-runner"; "read as a current, not as animals" |
| RM_Sparkleech | 0.50 | "a wet-winged flap of tissue" |
| RM_SparkleechGrub | 0.32 | the same, a grub at the roots |
| RM_Scorchpod | 0.55 | a seed-case on too few legs |
| RM_Gawpsack | 0.70 | a drifting bag of eyes |
| RM_Scabspinner | 0.75 | "hunts the small cast of the flats and flees anything larger" |
| RM_Peeper | 0.90 | the Contagion design names it in "the small/browser/picker cast" |
| RM_Blisterfloat | 1.00 | a hanging cluster of blisters under a gas bladder; nothing says big |
| RM_Sloghog | 1.00 | a barrel-bodied hog, about a pig's length beside a colonist |
| RM_Scaldhide | 1.15 | "a low armoured slab"; it draws low and as long as a colonist is tall, which "low slab" allows |
| RM_ShaleGorgerJuv | 1.11 | a juvenile: 0.41 of its adult (2.69), the ratio that all three invented sea-beast juveniles share |
| RM_ThornbackColoJuv | 1.26 | a juvenile: 0.41 of its adult (3.06) |
| RM_Titanoslime | 9.00 | "a hill of green jelly"; it reads as a hill |
| RSW_Taozin | 10.00 | "a giant armoured annelid many times a man's length"; coiled, it reads so |
| RM_MycoidColossus | 15.00 | named in the item's title only; "a colossal ... beast"; it reads colossal (it is not on the REVIEW list; its ORDER_MATCHED row matched an owner note about its graphic, not about its size) |

## New drawSize (6 kinds)

Every stage of a kind is scaled by one factor, as the Opee Sea Killer was when the owner ordered it to 10 cells on
2026-10-17 ("younger stages in proportion", its def comment). The new values are in the JSON file.

| kind | drawSize now (by stage) | verdict (by stage) | reason |
|---|---|---|---|
| RSW_CrimsonOpee | 1.36 · 1.98 · 2.48 | 4.94 · 7.19 · 9.0 | His note "Twilight Sea 9 squares long" (2026-09-10, fauna_assignment_register) is a number. The size bin "medium" that he set on the same row is a coarse class. The audit's own rule ranks a numeric order above a bin. The opee family later went big by his word: the Opee Sea Killer, first ordered at "5 squares long" on the same day, became "10 cells wide. SEE CANON." on 2026-10-17. A crimson opee at 9 sits just under the sea killer at 10. |
| RM_CrimsonOpee | 1.36 · 1.98 · 2.48 | 4.94 · 7.19 · 9.0 | The franchise-free twin of RSW_CrimsonOpee (same art, SEA_BEASTS_TIER_RULING_1). It is the same animal, so it takes the same order. |
| RM_CrimsonOpeeJuv | 0.68 · 1.02 | 2.47 · 3.70 | The young keep the 0.41 young-to-adult ratio of the other two invented juveniles. At 1.02 beside a 9-cell adult, a crimson opee juvenile would read as a different species. |
| RM_Summ | 2.2 · 3.6 · 6 · 7.2 · 8.6 | 4.09 · 6.70 · 11.16 · 13.40 · 16.0 | His order "crag, 16 squares" (2026-09-10) is on AA_Behemoth. RM_Summ replaced AA_Behemoth (the header of `RM_Summ.xml`). The largest stage (ancient) takes his number, so no summ outgrows it. The brood mother, which he wants "landscape sized" (2026-10-01), stays the only bigger one. |
| RM_Summing | same as RM_Summ | same as RM_Summ | The young-only kind on the same race. It must draw the same stage sizes as RM_Summ. |
| RM_Eyestinger | 1.0 · 1.2 · 1.3 | 1.54 · 1.85 · 2.0 | Its description says "a big segmented thing ... A heavy ambusher". The Contagion design casts it as predator risk. At 1.3 it draws no taller than a colonist; at 2.0 it reads big. Contagion is on the owner's hold (2026-11-16), so this change is a line on `design/concepts/Contagion/version/polish.md` for the next run that changes the def. It is not fixer work now. |

## For the fixer

- Set the five `route: fixer` kinds in the JSON. Change every `drawSize` of a stage (bodyGraphicData and
  swimmingGraphicData alike). Change no body size and no other number.
- Then delete the `RSW_CrimsonOpee` entry from `src/RimMandrake/Utils/art_size_audit_waivers.json`. With the adult at
  9 cells, the owner order matches.
- Done when `python3 src/RimMandrake/Utils/size_verdict_check.py design/RimMandrake/creature_size_verdicts_2026-11-27.json`
  exits 0.
- Mods touched: SWBestiary, TerminalBiomes and Abyss. None of them is on the owner's hold today. Read
  `src/RimMandrake/rimflow/mod_owner_hold.json` again before the edit.
