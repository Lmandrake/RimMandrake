# ExplosiveKnockback 0.1.0: walk brief, arrival 1
written_by: rm-detached-bench-rimmandrake-steward-explosiveknockback-p-1795487378

Written 2026-11-23, 7:30 PM PST, by a fresh reader. This reader made none of this version's evidence writes (no stage
move, no in-game row). Sources: `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\stage_record.json`,
the summaries, rows and strange things of visits 4 and 5
(`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\in_game\visit_4\` and `visit_5\`),
`build_match.py check --mod ExplosiveKnockback`, `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\journal.md`,
`git log` on `src\RimMandrake\ExplosiveKnockback`, the open items, and the walk save file itself.

## What to open

- **Savegame:**
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT5_WALK_20261123_CLEAR.rws`
  (18,538,100 bytes, saved 2026-11-23 5:06 PM PST) [measured]. It has the same 16 stations as the visit 4 save that you
  looked at on 2026-11-23 about 12:35 PM PST. The one improvement: station 13 is no longer under fog.
- **Mod list:** your full list, 314 mods in the save, Camera+ and Explosive Knockback among them [measured]. **The live
  `ModsConfig.xml` is now a smaller list without Explosive Knockback** (ArchBig is held for your drawbridge look)
  [measured 6:35 PM]. The seat that stages the walk restores the full list before the load.
- **Build:** the mod's code is at `db80fab783` (the gas fix, 2026-11-23 6:53 PM PST). **ArchBig still has the build before
  that fix**: deploy first [measured 7:26 PM].
- **Build match:** 54 of the 56 in-game checks count on that build. The two full-list checks (`sc_barrage_perf`,
  `sc_walk_raid`) must run again on it, on ArchBig [measured 7:26 PM]. So the mod goes back to the in-game stage for these
  two before you walk: `RIMMANDRAKE_RUN_KNOCKBACK_FULL_LIST_CHECKS_AFTER_GAS_CORNER_FIX`. The next brief (arrival 2)
  replaces this one.
- **Where to look:** the stations are in one row, left to right, 15 cells apart, at z = 12 (signs at z = 9). The map is
  at night and paused at tick 301.

| station | x | what it shows |
|---|---|---|
| 1 calibration | 12 | a colonist thrown 3 cells |
| 2 over sandbags | 27 | a colonist thrown over a sandbag line |
| 3 wall stop | 42 | a colonist stopped at a wall |
| 4 door stop | 57 | a colonist stopped at a door |
| 5 pawn hits pawn | 72 | a thrown colonist stopped by a standing one |
| 6 goods fly wild | 87 | scattered goods (weak: about one component is left to see) |
| 7 open storage | 102 | goods blown off open shelves |
| 8 closed containers | 117 | lockers, a safe and a crate that kept their goods |
| 9 heavy knock | 132 | a heavy steel stack that struck a colonist |
| 10 gas chain | 147 | a burned gas cloud, and the steel and colonist it shoved |
| 11 cover breaks | 162 | pit covers broken by a blast |
| 12 pit colonist | 177 | a colonist and a stack thrown into a pit |
| 13 killed by blast | 192 | corpses thrown by the blast that killed them |
| 14 storeroom, bomb, pit | 207 | **the flagship** |
| 15 shield | 222 | a shielded colonist who stayed put |
| 16 goods at obstacles | 237 | goods thrown at a door, sandbags and deep water |

- **Every station shows an aftermath.** Nothing on the map is armed. To see a throw happen, make a blast yourself:
  development mode has a bomb explosion tool [guess ~85% on its menu name], or give a colonist a grenade or a mortar. A
  good place is the flagship room at station 14: shelves, goods and a pit are there already.

## What changed since his last look

The record has no `his_walk` move, so the start point is the version's first move (2026-11-14 9:28 PM PST). Your informal
look on 2026-11-23 about 12:35 PM PST was at the visit 4 save, on `2590111487`. **The mod's code has changed once since
that look**: the first entry below. Changes to the mod since 2026-11-14:

- **A burning gas clump no longer shoves a thing in another room, past a wall corner** (`db80fab783`). The Conductor ruled
  on 2026-11-23 that this is a Problem of 0.1.0 to fix before you walk. Gas now uses the sight line of an explosion. Live:
  the game and the map model disagreed on the corner case before, and agree in 123 of 123 cases after.
- **Goods fly wild**: thrown goods go 1.6 times as far as the plain rule (`81392aea38`).
- **A thrown colonist who was hauling goes back to the haul** (`ef266bbdf9`). What a thrown colonist carries stays in the
  hands. You: *"For today have them hold it."*
- **Goods bounce off walls also from a cell right beside the wall, and hop over sandbags; goods over a pit go to the pit
  floor before the rim** (`ffc3937ee7`).
- **A good that has no way to fly tumbles along the freest line**, so that every good moves (`fa2de6ee4b`).
- **Pit covers break under what lands on them**: under a landing stack (`a9eedde493`), under a blast-thrown person
  (`610b127ba8`). A thrown person stops at a person who stands on a cover (`42225e0686`). Melee never throws.
- **A person thrown onto a cover falls once.** Before, the person fell twice and was hurt twice (`2590111487`).
- **A landing costs no job search** (19 to 25 ms less for each landing) (`7aa050b610`).
- **The fire switch also covers electrical burns** (`bace1c29cc`).
- **The closed container is thrown whole, as built**, by your card; a container that cannot move jolts (`587529cee1`).

In-game acceptance, visits 4 and 5 (2026-11-23): 56 of 56 checks passed, on the build before the gas fix. On the gas fix,
54 of 54 small-list checks pass. The frame bar on your full list reads 22.1 ms at
the 99th percentile (limit 50; with the mod off, 21.7). The storeroom raid walk passes 18 of 18 rows. Its frame
row reads -1.0% against mod off (limit +10%, your card "Compare to mod-off"), measured on a 24-mod list as ruled on
2026-11-16.

### Answers to what you asked at your look on 2026-11-23

- **"You ruled to keep the guns safe within the locker [confirm this]."** Confirmed: each of the 5 lockers at station 8
  still holds its gun, and the safe its silver [measured, read from the save]. They are LWM's Deep Storage weapons
  lockers. The mod reads them as closed because Deep Storage declares that they hide their contents (`showContents`).
  On your screen they draw the guns all the same. So the declaration and the picture disagree. Nobody has fixed this
  (see "Known").
- **"Station ten generated Tox Gas."** The scene seeds and lights the Cauldron's flammable vent gas, and a burst can come
  only from vent gas that burns [measured, read from the code]. Vent gas that burns turns into vanilla tox gas: that is
  the Cauldron's toxic smoke (`ToxFromBurn`, needs Biotech). What you saw is the smoke after the burn, so the station
  does decide the flammable-gas bars.
- **"Station 14 ... I see lots of items still on shelves."** The check on that scene reads 7 goods flown and 4 shelf
  stacks "too weak": the blast was too weak at their distance to move their mass, so they stayed [measured, visit 4
  row]. Whether that reads right is yours to judge.
- **"I can't see their initial states."** Not done in this save (see "Known").

## Known, not fixed: you need not report these

Current version (0.1.0), open:
- **Gun lockers draw their guns but keep them** (station 8).
  `RIMMANDRAKE_SETTLE_GUN_LOCKER_DRAWS_ITS_GUNS_BUT_KEEPS_THEM`. Your proposal: patch them so that they do not draw.
- **No station has its start state beside it.** `RIMMANDRAKE_SHOW_START_STATE_BESIDE_EACH_AFTERMATH_HE_COULD_NOT_JUDGE`.
  The visit 5 save was built after your words and does not have them.
- **Goods thrown at a pit cell that already holds goods** land on the floor beside that cell, or back on the near side
  when the floor is full. Your card (2026-11-22): "Always into the pit somewhere, THEN bounced out of the pit if totally
  full." Not built. `RIMMANDRAKE_LAND_KNOCKBACK_GOODS_IN_PIT_FIRST_BOUNCE_ONLY_WHEN_FULL`.
- **The jolt of a blocked container may read as a ghost** (a second outline), and its check does not read the drawn
  offset. `RIMMANDRAKE_MEASURE_KNOCKBACK_JOLT_PER_CONTAINER_NOT_GHOST`.
- **No check throws with an Outer Rim weapon.** "Other mods' explosions included" is proven with unpatched test blasts
  only. `RIMMANDRAKE_RUN_KNOCKBACK_ROWS_TIER_LIST_CANNOT_DECIDE` (its row 5; rows 1 and 2 passed in visit 5).
- **A whole-game freeze of 50 to 100 ms now and then**, with the mod on or off.
  `RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD`. You: *"a consistent issue well beyond this mod."*

Next version, by your words or cards:
- The carried thing flies on its own arc: `RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC`.
- A thrown pawn that lands on a pawn bruises both: `RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN`.
- Our own soot, smoke and crater in place of Extra Explosion Effects' (the dark blots at every station are explosion
  smoke and that mod's soot): `RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS`.

Recorded and left (`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\polish.md`), no ticket open: a
thrown hauler whose storage cell was taken in the meantime gives the haul up; a gas burst does not shove a person who
stands on an unbroken pit cover; a hit across a sandbag can register without contact; the fire switch misses another
mod's fire type that has no Flame parent.

Not seen again: the two error storms of the 2026-11-16 raid walk. The archived log of the visit 5 full-list walk
(`Player_20261124T010730Z_d7e6c333_b4e48aade92e.log`, 18 raid-save loads) has 0 "Exception ticking" lines and 0
"TweenedPosRoot" lines [measured].

## What I noticed first

- **This save repeats the problem that you named at your look.** The same 16 aftermaths, no start states. A rebuild of
  the save with start-state twins would make the walk easier to judge. Ticket
  `RIMMANDRAKE_SHOW_START_STATE_BESIDE_EACH_AFTERMATH_HE_COULD_NOT_JUDGE`.
- **Some signs are wrong.** Do not trust the text of signs 2, 4, 6, 10 and 14. Sign 14 says "known: it stays" about the
  pit cover; that is old text: the cover now breaks and the stack falls through (check `sc_storeroom_bomb_pit`, PASS).
  Sign 2 promises two colonists and one is there. Sign 4 promises a second colonist at deep water and none is there.
  The rebuild in the same ticket carries the sign repair.
- **It is night on the map.** The stations are hard to see. Set the time to day before you look.
- **Station 6 shows almost nothing** for what its sign promises. Stations 14 and 16 show scattered goods better.
- **The signs overlap when you zoom out.**
