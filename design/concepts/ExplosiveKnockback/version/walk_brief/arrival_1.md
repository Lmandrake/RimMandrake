# ExplosiveKnockback 0.2.0: walk brief, arrival 1
written_by: rm-detached-bench-rimmandrake-steward-explosiveknockback-p-1795703710

Written 2026-11-26, 6:45 AM PST, by a fresh reader. This reader made none of this version's evidence writes (no stage move,
no in-game row). Sources: `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\stage_record.json`, the
summary, rows, strange things, scripts and screenshots of visit 3
(`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\in_game\visit_3\`), `build_match.py check`,
`look_changed_labels.py show`, `look_notes.py`, `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\journal.md`,
`git log` on `D:\Luke\dev\RimMandrake\src\RimMandrake\ExplosiveKnockback` since your 0.1.0 walk, the open items, and the
0.1.0 walk brief (`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\previous\0.1.0\walk_brief\arrival_2.md`).

## What to open

- **Savegame:** `EK_V020_WALK_NEW_THROWS_20261126.rws`, on **ArchBig only**:
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_V020_WALK_NEW_THROWS_20261126.rws`
  (10.0 MB, saved 7:37 AM PST 2026-11-26) [measured]. ArchSmall does not have it [measured]. It holds the 16 stations
  below and 4 new stations (17 to 20) that show the throws new in 0.2.0. The earlier save of this version,
  `EK_V020_VISIT3_WALK_20261126.rws` (the 16 stations only), is still in the same folder.
- **Mod list:** the mod's small list, 26 mods (tier `explosiveknockback_visit`), with all five expansions, Simple Camera
  Setting (zoom) and Character Editor. ArchBig's `ModsConfig.xml` holds exactly these 26 now [measured 6:40 AM]. Extra
  Explosion Effects, Better Explosions and Dynamic Effects Forge are not on it, so every blast look you see is ours.
- **Build:** the mod at `9931b028e1`. ArchBig's deployed Explosive Knockback DLL is byte-identical to the committed one
  [measured, same md5]. The save was staged on the proof build and then loaded on this release build with no error line
  in `Player.log` [measured, 7:38 AM].
- **Build match:** 65 of 65 in-game checks count on this build, 0 to run [measured 6:38 AM].
- **Where to look:** it is noon and the game is paused. Stations 1 to 16 have the layout you walked for 0.1.0. Each
  station is one column of two sites. **START** (z 42, above) is the scene before the blast, its explosion removed before
  any tick. **AFTER** (z 12, below) is the same scene after the blast. Signs stand 3 cells below each site. Columns run
  left to right, 15 cells apart. Stations 17 to 20 are a second band, north of the first: AFTER at z 72, START at z 102,
  at x 12, 27, 42 and 57. `walk_twins.py check`: ok, 40 signs, 20 AFTER sites, each with its START twin [measured].
- Nothing is armed. **To see the blast show itself** (the flash, fireball, screen shake, air ripple and smoke), set off a
  blast yourself: development mode's explosion tool, or a grenade. The save shows only what a blast leaves behind
  (crater scars, and soot where a blast stood near walls or people).
- Explosive Knockback adds no creature, so the save has no creature pens.

| station | x | what it shows |
|---|---|---|
| 1 calibration | 12 | a colonist thrown 3 cells |
| 2 over sandbags | 27 | a colonist thrown over a sandbag line |
| 3 wall stop | 42 | a colonist stopped at a wall |
| 4 door stop | 57 | a colonist stopped at a door |
| 5 pawn hits pawn | 72 | thrown colonists stopped by standing ones (now both are bruised, by each other's size) |
| 6 goods fly wild | 87 | one component that bounced back off a wall |
| 7 open storage | 102 | goods blown off open shelves; a steel control on bare ground 5 cells south |
| 8 closed containers | 117 | lockers, a safe and crates that kept their goods; the light ones flew whole |
| 9 heavy knock | 132 | a heavy steel stack that struck a colonist |
| 10 gas chain | 147 | a gas cloud before (by hand, unlit) and after it burned; the yellow haze is its toxic smoke |
| 11 cover breaks | 162 | pit covers broken by a blast |
| 12 pit colonist | 177 | colonists and stacks thrown into pits |
| 13 killed by blast | 192 | corpses thrown by the blast that killed them; the big scorched crater is that deliberately lethal blast |
| 14 storeroom, bomb, pit | 207 | **the flagship** |
| 15 shield | 222 | a shielded colonist who stayed put |
| 16 goods at obstacles | 237 | goods thrown at a door, sandbags and deep water |
| 17 carried thing (new) | 12 | START: a colonist holds 20 steel that she was ordered to haul east. AFTER: she landed 3 cells out, empty-handed, and the stack flew on its own arc to 3 cells beyond her |
| 18 bruise by size (new) | 27 | a colonist thrown into a standing squirrel (lower lane) and into a standing elephant (upper lane): the colonist took 1.3 and the squirrel 6.7; the colonist took 6.4 and the elephant 1.6. Both animals lived in this save |
| 19 sandbag, no contact (new) | 42 | lower lane: the sandbag stopped the throw, and nobody was bruised. Upper lane, no sandbag: the thrown colonist hit the standing one, 4 each |
| 20 gas shoves a pawn on a pit cover (new) | 57 | the Cauldron's vent gas burned beside a colonist who stood on an intact reinforced pit cover; it shoved her one cell east, impact 0, and the cover still stands (the brown square to her west; its art is close to bare soil) |

The new stations' blasts are small (damage 1, "Bigger blasts throw harder" off, as in their 0.2.0 scenes), so that the
throw is not hidden by a downed colonist. Captures of each START and AFTER:
`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\in_game\visit_3\walk_stations\`.

## What changed since his last look

Your last look: your walk of 0.1.0 on 2026-11-24 (passed 3:44 PM PST, "very fun", save `EK_VISIT6_WALK_20261124_C`).
Version 0.2.0 opened at 4:34 PM that day on your words. What it changed, each with its commit:

- **Our own blast show** (`12d6c0feab`; smoke and soot art `d420ae2e45`, 32 renders that the art judge kept): a fiery
  flash and fireball with sparks and thrown dirt, a screen shake (a Mod Settings slider sets how hard, down to none), a
  ring of bent air, rolling smoke, a crater scar on open ground, black soot on walls, doors, furniture and floors, and
  soot on people and animals. A bigger blast is a bigger show in every part. Each part has its own on/off switch, all on.
  Your words: *"Let's drop all those mods and replace them with SO MUCH BETTER stuff."* (2026-11-24)
- **A carried thing flies on its own arc** (`07a4bca605`): the thing leaves the colonist's hands at the blast and lands
  where its own flight ends. Your words: *"Next version it should go flying independently of the person holding it.
  Different trajectories."* (2026-11-14)
- **A thrown pawn that meets a pawn bruises both, by size** (`07a4bca605`): by landing on it or being stopped by it. Your
  words: *"the bruising should be proportional to the size of the thing that hit you (BIG creature on small creature
  really hurts small creature, big creature relatively unaffected, tune to common sense elephant/rat, person on dog or dog
  on person, etc.)"* (2026-11-24)
- **A sandbag that stops a throw before it reaches a pawn means no hit on that pawn** (`07a4bca605`).
- **Burning gas shoves a person who stands on an intact pit cover** one cell, unhurt, as on any ground (`07a4bca605`).
- **A rebounding good carries on for only part of the way it still had** (`380aa4ee6d`, the bar reworded by the
  Conductor on 2026-11-25). Lost: the promise that each rebound is shorter than the leg before it. Near a wall a rebound
  can fly farther than the short leg before it. Undo: revert `380aa4ee6d`.
- **The scar defs were renamed** to end without a digit (`d62ff67597`), to clear a config error. Saves with the old
  names still load.

In-game acceptance, visit 3 (2026-11-26): 16 of 16 checks that the change since visit 2 touches pass on this build; the
other 49 keep their visit-2 PASS. The walk frame time at the 99th percentile is 21.9 ms with the mod on and 22.5 ms with
it off (21 samples each, small list).

`look_changed_labels.py show --mod ExplosiveKnockback --save EK_V020_WALK_NEW_THROWS_20261126` (exit 0):

```
save EK_V020_WALK_NEW_THROWS_20261126 against his last look, save EK_VISIT6_WALK_20261124_C
calibration calibration: changed since your last look
closed_containers closed_containers: changed since your last look
cover_breaks cover_breaks: changed since your last look
door_stop door_stop: changed since your last look
gas_chain gas_chain: changed since your last look
goods_fly_wild goods_fly_wild: changed since your last look
goods_obstacles goods_obstacles: changed since your last look
heavy_knock heavy_knock: changed since your last look
killed_by_blast killed_by_blast: changed since your last look
open_storage open_storage: changed since your last look
over_sandbags over_sandbags: changed since your last look
pawn_hits_pawn pawn_hits_pawn: changed since your last look
pit_colonist pit_colonist: changed since your last look
sc_gas_chain_pawn_on_cover sc_gas_chain_pawn_on_cover: new since your last look
sc_pawn_arc_bruise_sizes sc_pawn_arc_bruise_sizes: new since your last look
sc_pawn_arc_carried_thing sc_pawn_arc_carried_thing: new since your last look
sc_pawn_arc_sandbag_no_contact sc_pawn_arc_sandbag_no_contact: new since your last look
shield_counter shield_counter: changed since your last look
storeroom_bomb_pit storeroom_bomb_pit: changed since your last look
wall_stop wall_stop: changed since your last look
```

So signs 1 to 16 read "[CHANGED SINCE YOUR LAST LOOK]" (every station reads the mod's whole Source and Defs, and both
changed since your 0.1.0 walk), and signs 17 to 20 read "[NEW SINCE YOUR LAST LOOK]". The record of your 0.1.0 look was
missing: the 0.1.0 save's builder wrote no look-cells file, and the label tool did not read where a passed version's stage
record is kept. Both are repaired (`look_cells\EK_VISIT6_WALK_20261124_C.json`, rebuilt from the 0.1.0 walk build
`e089dc2573`).

`look_notes.py ExplosiveKnockback`: *"no pass of his is pinned (version/pins.json holds none): nothing to list."*

## Known, not fixed: you need not report these

Current version (0.2.0), open:
- **In long test batches a good once stayed unthrown or vanished** (3 sightings in visit 1; two of them were later classed
  as staging faults: a hauler picked the good up). `RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS`,
  an open hunt.
- **On the SteveDesktop test lane two checks fail that pass on ArchBig** (pit fetch, re-haul after a throw).
  `RIMMANDRAKE_SORT_KNOCKBACK_LANE_FAILS_ARCHBIG_PASSES_SAME_CHECKS`.
- **Lit chemfuel burns but does not explode, so it throws nobody**: FlowWorks' side.
  `RIMMANDRAKE_PROVE_LIT_CHEMFUEL_BLAST_THROWS_WITH_KNOCKBACK`.
- **A whole-game freeze of 50 to 100 ms now and then**, mod on or off.
  `RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD`. You: *"a consistent issue well beyond this mod."*

Open raid bars (`paused_raids`): none. No scene of this version stages a raid. The bar `walk_storeroom_raid` is decided
by your walk with the frames-only run and the save-in-the-air scene (both PASS); you may play a raid.

Bars moved to the next version (`bars_moved_to_next_version` of `VERSION.json`): none.

Out of this version by design (`D:\Luke\dev\RimMandrake\design\specs\2026-11-24-knockback-blast-show\design.md` §4): the
later set of the blast show (water, snow and steam; roof dust; sound; stagger, thoughts and noise; heat shimmer; sand and
ash; the looks of Stun, EMP, Smoke and Extinguish blasts; soot on goods; lights; the shell's warning). A big "whoosh" for
a blast wider than one cell is a design for a later version
(`RIMMANDRAKE_DESIGN_KNOCKBACK_WHOOSH_FOR_BLASTS_OVER_ONE_CELL`).

Recorded and left (`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\polish.md`), no ticket: the art
judge's nits on the scars (glowing specks baked into the crater art, a pale dusty rim on one scorch); the fire switch
misses another mod's fire type with no Flame parent; a factor-0 throw saved in mid-flight bruises at full factor after a
reload.

## What I noticed first

- **Stations 1 to 16 are the ones you walked two days ago.** What is new in them is the blast show's aftermath. The new
  throws are stations 17 to 20. The captures of stations 1 to 4 and 13 to 16 (from the earlier save of this version, the
  same staging) show a crater scar at each blast, inside the storeroom of station 14 too
  (`D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\in_game\visit_3\screenshots\walk_g1_after.jpg`,
  `walk_g4_after.jpg` beside it). I could not tell soot on the walls from those captures; look for it at station 14.
- **Station 13's crater is several times as wide as the others**: the deliberately lethal blast, scaled to its damage.
  Whether that size reads right is yours to judge.
- **The bruise can kill a small creature.** In visit 3's first bruise run a 12 kg squirrel took 6.7 from the thrown
  colonist and died. That follows your words ("really hurts small creature"); whether killing it is too much is yours to
  judge.
- **On a Rot map, crater scars go within minutes.** The Rot's living ground thins outdoor filth, and a scar is filth: 8 of
  24 scars were gone 300 ticks after their blasts (2026-11-25 probe,
  `D:\Luke\dev\RimMandrake\design\concepts\ExplosiveKnockback\version\evidence\ied_scar_2026-11-25\README.md`). It was
  ruled a physical condition of that biome (a delegated call), so neither mod changed. The bar says a scar is "still there
  days later". This save is on arid shrubland, so you will not see it here.
- **Sign 13 may still overstate the deaths.** It says three colonists are killed. At your 0.1.0 walk two died and one
  lived, and the sign's text has not changed. In this save the count was not read.
- **The START sites carry no scar.** A START site's blast never happened. The staging removes scars that the show laid
  there anyway and reads back zero on each START site.
- **Keep the game paused while you compare.** As at 0.1.0: unpaused, the gas at station 10 thins, its fire burns on, and
  the colonists in the pits of 11 and 12 get ladder blueprints.
