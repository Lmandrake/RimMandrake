# Oversized test scenes: one page

Work of 2026-11-24. Pyrelands has its own run. Every claim is tagged. The full table is `table.md` beside this page.

**Your three questions.** What is tested? Should a script test it? What is the minimum test?

**Short answer.**
- The same fault is in eleven of eleven other mods that have scenes. [measured]
- The long scenes mostly repeat claims that a small scene or an offline test decides already. [measured for the three in-game mods]
- In the in-game mods, the eleven scenes below ran 143 times and did not pass 77 times. [measured]
- Nine of them carry times, and those add to 16,034 s. [measured]
- A long scene mostly failed for a reason outside the mod. [guess ~75%: the causes were read for four scenes]
- The six held mods that are not locked are fixed now, as text. Nothing of them was run. [measured]
- The three in-game mods wait, because a live run or a Codex run holds each one now. [measured 1:30 AM PST]

| mod | scene | runs / not passed | why it is oversized | what replaces it | state |
|---|---|---|---|---|---|
| FlowWorks | `sc_hung_bridge` | 27 / 10 | nine sections for two paths | the first section only | waits: FlowWorks trace run |
| FlowWorks | `sc_source_pays` | 13 / 10 | eight claims, two lists | three small scenes, one offline test | waits: same |
| FlowWorks | `sc_garden` | 15 / 9 | a day, seven machines, no bar | two small supports | waits: same |
| FlowWorks | `sc_walk` | 11 / 3 | full list, eight claims | three small scenes | waits: same |
| FlowWorks | `sc_pawn_height` | 11 / 5 | 46 orders | one walk over five depths | waits: same |
| FlowWorks | `sc_hole_prison` | 14 / 2 | a full day | one meal, 5,000 ticks | waits: same |
| FlowWorks | `OL_OWNER_LOOK_READS` | 9 / 8 | many reads, no bar | your look | waits: same |
| Explosive Knockback | `sc_walk_blasts` | 14 / 12 | 18 rows, 17 decided elsewhere [guess ~80%] | one save with a thing in the air | waits: visit 6 |
| Explosive Knockback | `sc_storeroom_bomb_pit` | 14 / 11 | eight claims, no bar | your walk | waits: visit 6 |
| Explosive Knockback | `sc_pit_fetch` | 12 / 6 | a hauler free for a day | two ordered hauls | waits: visit 6 |
| Gimme Some Slack | `sc_walk` | 3 / 1 | the text says a week; the code plays none | the four save rows | waits: Codex run |
| Gimme Some Slack | `sc_tap_theft`, `sc_gravship` | in the proof | two days; a new ship each flight | one daily call; one ship | waits: Codex run |
| Contagion | 8 scenes | 0 | two weeks, 30 days, full list | 8 rewritten, 7 added | done as text, UNRUN |
| PyrelandsMechanics | 4 scenes | 0 | a season, a raid | 4 rewritten, 4 added | done as text, UNRUN |
| FeverWood | 5 scenes | 0 | two raiding factions, several days | 5 rewritten, 5 added | done as text, UNRUN |
| Cauldron, GelatinousSlime, Stillsand | 5 scenes | 0 | forty colonists | 5 rewritten, 6 added | done as text, UNRUN |
| Graffiti | 7 scenes | 0 | three weeks, six raids | design in `table.md` | waits: your hold, and the lock |
| LeaningScrub | 2 scenes | 0 | forty colonists, 30 cycles | design in `table.md` | waits: your hold, and the lock |

**What leaves the scripts.** A played week, a season and a colony at work go to your walk. How often a chance event comes is felt there too.

**One bar clause needs the Conductor.** On 2026-11-16 your card set a frame row in Explosive Knockback's walk.
The small save scene does not read frames. `sc_barrage_perf` reads frames with the mod on and off. [measured, read]
The ticket names your card, and the builder does not drop that clause silently.

**What was kept.** Ten short bundles on a small list stay whole. Splitting them would repeat the staging. [guess ~80%]

**How a fix is shown.** One program checks each mod's ticket. It was red for all eleven mods tonight. [measured]
It caught eight of eight planted faults, and it passed a good table. [measured]

**UNRUN.** No game ran. No new scene has code yet. Each ticket builds its scenes with offline tests first.
