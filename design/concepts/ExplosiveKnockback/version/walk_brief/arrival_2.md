# ExplosiveKnockback 0.1.0: walk brief, arrival 2
written_by: rm-detached-bench-rimmandrake-steward-explosiveknockback-p-1795560743

Written 2026-11-24, 3 PM PST, by a fresh reader. This reader made none of this version's evidence writes (no stage move,
no in-game row). Sources: `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\stage_record.json`, the
summary, rows, strange things and screenshots of visit 6
(`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\in_game\visit_6\`), `build_match.py check`,
`walk_twins.py check`, `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\journal.md`, `git log` on
`src\RimMandrake\ExplosiveKnockback`, the open items, and the walk save file itself. This brief replaces arrival 1.

## What to open

- **Savegame:** `EK_VISIT6_WALK_20261124_C.rws`. Both games have the same file [measured, same md5]:
  - ArchBig: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT6_WALK_20261124_C.rws`
  - ArchSmall: `D:\ClaudeWork\rimmandrake\instances\b\Saves\EK_VISIT6_WALK_20261124_C.rws`
- **Mod list:** the mod's small list, 24 mods (tier `explosiveknockback_visit`). It has all five expansions and the
  advanced-zoom mod (Simple Camera Setting) [measured, read from the save]. This is not your full list.
- **Before you sit down, the seat that stages the walk does two things.** Neither game's `ModsConfig.xml` is on this list
  now (ArchBig has 10 mods and ArchSmall has 18, both without Explosive Knockback). And the other mods of the list need a
  deploy: ArchBig has an older FlowWorks, ArchSmall an older Gimme Some Slack [measured 2:57 PM]. FlowWorks owns the pits
  and their covers.
- **Build:** the mod's code is at `e089dc2573`. **Both games have exactly that build of Explosive Knockback**, its DLL,
  Defs and Patches [measured 2:57 PM].
- **Build match:** 56 of 56 in-game checks count on that build, 0 to run [measured 2:54 PM].
- **Where to look:** it is noon, and the game is paused. Each station is one column of two sites. **START** (z 42, above)
  is the scene as it stood before the blast. **AFTER** (z 12, below) is the same scene after it. All 16 AFTER sites have a
  START site [measured]. The columns go left to right, 15 cells apart.
- The people in a START site and in its AFTER site are different colonists: compare the places, not the names.
- Nothing is armed. To see a throw happen, make a blast yourself: development mode has an explosion tool
  [guess ~85% on its menu name], or give a colonist a grenade. The START site of station 14 is a good place.

| station | x | what it shows |
|---|---|---|
| 1 calibration | 12 | a colonist thrown 3 cells |
| 2 over sandbags | 27 | a colonist thrown over a sandbag line |
| 3 wall stop | 42 | a colonist stopped at a wall |
| 4 door stop | 57 | a colonist stopped at a door |
| 5 pawn hits pawn | 72 | thrown colonists stopped by standing ones, one of them on a pit cover |
| 6 goods fly wild | 87 | one component that bounced back off a wall |
| 7 open storage | 102 | steel blown off shelves, a hopper and a table |
| 8 closed containers | 117 | lockers, a safe and crates that kept their goods; the light ones flew whole |
| 9 heavy knock | 132 | a heavy steel stack that struck a colonist |
| 10 gas chain | 147 | a gas cloud before and after it burned, and the steel and colonist it shoved |
| 11 cover breaks | 162 | pit covers broken by a blast |
| 12 pit colonist | 177 | colonists and stacks thrown into pits |
| 13 killed by blast | 192 | corpses thrown by the blast that killed them |
| 14 storeroom, bomb, pit | 207 | **the flagship** |
| 15 shield | 222 | a shielded colonist who stayed put |
| 16 goods at obstacles | 237 | goods thrown at a door, sandbags and deep water |

## What changed since his last look

Your last look was on 2026-11-23, about 12:35 PM PST, at the visit 4 save, on `2590111487`. (The record also has a
`his_walk` move of 7:31 PM that day. The mod went back to the in-game stage 6 seconds later and you did not walk it.)
The mod's code changed four times since that look:

- **Goods thrown at a taken pit cell settle anywhere on that pit's floor, and bounce out only when the floor is full**
  (`d61b1e2b31`). Your card of 2026-11-22: *"Always into the pit somewhere, THEN bounced out of the pit if totally full."*
- **Thrown corpses spin in the air** (`1acc05e0ed`). They did not before, and the bar says that they do.
- **Gas stays gentle** (`1acc05e0ed`, `e089dc2573`): a burst moves nothing farther than its cap of 2 cells, also over
  sandbags and beside a full cell, and a heavy stack that gas throws hurts nobody. A thrown good whose diagonal flight
  crosses an open pit falls in.
- **A burning gas clump no longer shoves a thing in another room, past a wall corner** (`db80fab783`). Gas now uses the
  sight line of an explosion.

In-game acceptance, visit 6 (2026-11-24): 56 of 56 checks pass on this build, and the game and the map model agree in 125
of 125 cases. The barrage frame time at the 99th percentile is 21.4 ms (limit 50; mod off 22.2). The storeroom walk check
passes 18 of 18 rows; its frame row (your card "Compare to mod-off") reads +0.0% (limit +10%). Both frame readings are on
the 24-mod list. Nobody measured them on the full list with this build.

### Answers to what you asked at your look on 2026-11-23

- **"I can't see their initial states" / "replicate their frozen initial states beside them".** Done: the START sites. A
  check now refuses a walk save that lacks one
  (`RIMMANDRAKE_SHOW_START_STATE_BESIDE_EACH_AFTERMATH_HE_COULD_NOT_JUDGE`, closed).
- **"You ruled to keep the guns safe within the locker [confirm this]."** Confirmed: every locker at station 8 has the
  same guns in both sites, the safe its 50 silver [measured, read from the save]. **On this list the lockers do not draw
  their guns.** Only your full list draws them, so a mod of the full list does that (which one: unknown). The Conductor
  ruled on 2026-11-24 that this waits for the integration phase (see "Known").
- **"Station ten generated Tox Gas."** The scene burns the Cauldron's vent gas, and vent gas that burns leaves vanilla
  tox gas as its smoke. The yellow haze at the AFTER site is that smoke. The START site shows the unlit cloud.
- **"Station 14 ... I see lots of items still on shelves."** Four shelf stacks stay because the blast is too weak for
  their mass at that distance. The START site now shows what stood where. Whether it reads right is yours to judge.

## Known, not fixed: you need not report these

Current version (0.1.0), open:
- **Gun lockers draw their guns but keep them, on the full list only**:
  `RIMMANDRAKE_SETTLE_GUN_LOCKER_DRAWS_ITS_GUNS_BUT_KEEPS_THEM`, parked until the integration phase. You will not see it
  on this list.
- **The jolt of a container that cannot move may read as a ghost** (a second outline in a paused frame). Nobody has judged
  it in motion. `RIMMANDRAKE_MEASURE_KNOCKBACK_JOLT_PER_CONTAINER_NOT_GHOST`. Its measuring part is done: each jolted
  container now reads its own movement, 0.12 cell.
- **One gas check failed once in four walks on 2026-11-23** (the order in which clumps go off, one late cell) and nobody
  has classed that run. The same check passed in the final walk of visit 6.
  `RIMMANDRAKE_CLASS_KNOCKBACK_GAS_CLUMP_RED_ONCE_IN_FOUR_WALKS`.
- **No check throws with an Outer Rim weapon.** "Other mods' explosions included" is proven with untuned test blasts only.
  Its ticket, `RIMMANDRAKE_RUN_KNOCKBACK_ROWS_TIER_LIST_CANNOT_DECIDE`, was dropped, and a steward read the bar as decided
  without those weapons. The Outer Rim core mod is on this list, so you may try one.
- **A whole-game freeze of 50 to 100 ms now and then**, with the mod on or off.
  `RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD`. You: *"a consistent issue well beyond this mod."*
- **No test stages a raid** (raid tests are paused). `walk_storeroom_raid`: its check now throws the same shells and
  grenade with no raiders (`sc_walk_blasts`, PASS). You may play a raid.

Next version (next version, by your words or cards):
- The carried thing flies on its own arc: `RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC`.
- A thrown pawn that lands on a pawn bruises both: `RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN`.
- Our own soot, smoke and crater: `RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS`.

Recorded and left (`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\polish.md`), no ticket open: a
rebound keeps 70 percent of the cells left, while its bar speaks of speed; a thrown hauler whose storage cell was taken
gives the haul up; a gas burst does not shove a person who stands on an unbroken pit cover; a hit across a sandbag can
register without contact; the fire switch misses another mod's fire type that has no Flame parent.

Not seen again, cause unknown: two error storms of the 2026-11-16 raid walk on the full list
(`D:\Luke\dev\RimMandrake\design\RimMandrake\integration_phase_list.md`).

## What I noticed first

- **The save does what you asked for.** Most pairs read at a glance: 1, 2, 7, 8, 9, 15 and 16 above all.
- **The signs cover their own subjects.** A sign stands 3 cells below its station, and its label hides what lies there:
  above all the pit of station 14, the colonist of station 10, the smaller pit of station 11 and the south stack of
  station 12. Zoom in until the label shrinks away from the pit, or look from the south edge. Zoomed out, the labels of
  neighbouring stations overlap.
- **Sign 13 is wrong.** It says that three colonists are killed. Two died and were thrown 5 and 6 cells; the third (Toni,
  x 188) lost body parts, was thrown 3 cells and lies down alive. The check asks for what happened (2 dead, 2 corpses
  thrown, both spun) [measured].
- **In station 14, one of the four people goes into the pit** (Vas). One is thrown against the east wall. The other
  two stay where they stood; the flying steel strikes one of them (x 210, z 15). Your words were *"some people as well"*. Whether one is enough is yours to judge.
- **You cannot see the covers in the START sites of 11 and 12.** They are there [measured]. A concealed pit looks like
  plain ground while its whole pit is covered; that is FlowWorks by design. Click the ground beside the colonist.
- **The START site of station 10 is hand-built and lacks one thing**: the covered pit cell east of the cloud (x 150),
  which the AFTER site has, with a steel stack and a small fire on it. The cloud, the three stacks and the colonist
  match. The START cloud is faint on screen.
- **Keep the game paused while you compare.** Unpaused, the START gas thins out, the fire at station 10 burns on, its
  colonist breathes the tox gas, and colonists in the pits of 11 and 12 have ladder blueprints waiting beside them.
- **Station 6 is thin**: one component moved two cells, off one wall. Stations 14 and 16 show scattered goods better.
