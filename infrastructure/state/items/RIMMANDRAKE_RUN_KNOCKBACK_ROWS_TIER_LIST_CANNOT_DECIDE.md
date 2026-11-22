## spec
Explosive Knockback, Design Version 0.1.0 (current version; a Problem class: these bars stay undecided without it).
Filed by the ticket sweep RIMMANDRAKE_SWEEP_KNOCKBACK_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE (2026-11-22), which
merged four older tickets into this one. Each one is a live row that the mod's 34-mod tier list cannot decide. The
2026-11-17 rescue ran 66 scenes on that list (`design/concepts/ExplosiveKnockback/version/rescue_2026-11-17/live/all_scenes_300_ticks.txt`);
these are the rows it left open.

1. **sc_barrage_perf on the owner's full list** (from RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF, bar barrage_frame_budget:
   the p99 frame in the 0.9-8.25 s window at most 50 ms). The rescue's wall bounce puts more stacks in the air, so the
   2026-11-12 13-mod reading does not decide it. Today it reads INVALID ("not the owner's full list: 34 active mods").
   Command: `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes frame_probe_selfcheck,barrage_perf_off,barrage_perf --ticks 0 --real`
   (the whole line is in `design/concepts/ExplosiveKnockback/version/in_game/unrun.jsonl`).
2. **sc_walk_raid on the owner's full list** (also from ALL_FLY_PERF, which owned the walk scene). Its frame row
   compares mod on against mod off in the same run (his card, OWNER:1794834159094900561). Command:
   `python.exe src\RimMandrake\ExplosiveKnockback\validation.py --live walk_storeroom_raid --storeroom x,z,w,h --cover x,z --gas x,z [--save NAME]`.
3. **Two NRE storms on that walk** (from RIMMANDRAKE_FIX_KNOCKBACK_RAID_NULL_PAWN_STORM_780_TICKS, 2026-11-16, full list):
   780x 'Exception ticking Levin' in vanilla Pawn.Tick+0x60 at (246,0,36) and 447x root Update NRE in
   PawnTweener.TweenedPosRoot via Pawn_DrawTracker.DrawPos. The rescue read the log: both start right after a game
   LOAD, on a pawn at the map edge; that a knockback caused them is a guess. It did not reproduce on the 34-mod list (a
   pawn saved mid-flight and reloaded lands and logs 0 such lines, `proof/pawn_flight_saveload.py`, 5 of 5). Next step:
   read Player.log for those two lines after run 2. If they come back, bisect knockback on or off with the same save.
4. **spared_states' sleeper on the full list** (from RIMMANDRAKE_KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST, Stage 6 visit 1,
   2026-11-15): on the full list the staged sleeper is not in its bed at the blast (row INVALID), though the scene passes
   on the tier list (`sleeper in_bed`, 2026-11-17). The bar is decided on the tier list. This matters for the walk save
   staging only: the walk station must not be labelled INVALID when he walks it.
5. **sc_blast_kinds' Outer Rim lanes** (from RIMMANDRAKE_PROVE_KNOCKBACK_OUTERRIM_BLAST_LANES, 2026-11-13): the modded
   damaging lane is OuterRim_SonicGrenadeProj (damage OuterRim_Sonic, neronix17.outerrim.core), and the modded Flame lane
   is OuterRim_PlasmaGrenadeProj (`design/RimMandrake/explosion_mods_characterized_2026-11-12.md`, "The three unnamed lanes").
   The blast_kinds scene exists and passes on the tier list, but no proof file names Outer Rim, so bar
   every_harmful_blast_throws' "other mods' explosions included" has no modded lane yet. Build the lanes in the proof
   build, then run them on a list that loads Outer Rim. The full list does; a tier list plus Outer Rim also does.

Rows 1 to 4 need the owner's full list: ArchBig, or another game that can hold the full list. Row 5 needs Outer Rim
loaded. ExplosiveKnockback is switched OFF in the pipeline (pipe act ct_000026, 2026-11-18). This ticket runs when the
Conductor switches it on and Stage 6 is reached. It does not run the mod forward by itself.

## His words carried from the merged tickets
- 2026-11-12 about 00:0x PST, card write-in for the flagship scene (OWNER:1794470697182934051, on
  RIMMANDRAKE_DESIGN_KNOCKBACK_FIRST_TOUCH; staged by ALL_FLY_PERF): "Just put a bomb into a storeroom with people in it
  beside a pit. Shows some items falling into the pit and some people as well." The flagship sc_storeroom_bomb_pit and
  its control passed live on the tier list on 2026-11-17. His look at it is part of his walk.
- 2026-11-12 (note on ALL_FLY_PERF, his look at the 13-mod barrage): "No noticable delay during the explosion. Tuning looks good. I approve 1-7."
- ALL_FLY_PERF was filed under standing ruling OWNER.jsonl:1794468864684141079 (the Designer pass's plan).

## verify
Acceptance test (row 5 offline, today red): `grep -l OuterRim src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof*.cs`
prints nothing on today's tree (watched 2026-11-22). It must name the proof file that holds the two Outer Rim lanes.
Rows 1 to 4 have no offline test: they are live runs on the full list. On today's tree, row 1 reads INVALID and rows 2 to 4
are UNRUN (`version/in_game/unrun.jsonl`, the rescue's all_scenes file).

## criteria
- sc_barrage_perf on the full list: PASS by its p99 rule, or a measured FAIL filed against the mod.
- sc_walk_raid on the full list: every row PASS or UNMEASURED with its cause. Player.log after that run holds neither NRE storm, or
  the storm is bisected to knockback on or off.
- The walk save's spared_states station is not labelled INVALID.
- sc_blast_kinds runs the Outer Rim sonic and plasma lanes. Each one throws as the bar says.
