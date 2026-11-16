# ExplosiveKnockback 0.1.0 — the walk's frame row on the smallest list (Test Pilot during visit 3; this folder was visit_4/ until 2026-11-16 ~12:23 PM PST, moved: only the Stage 6 driver opens a visit)

Detached Test Pilot, seat BENCH, item RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES, 2026-11-16 05:53-09:45 PST.
Scope, the owner's words (5:43 AM PST, OWNER:1794836946186553250): "The game pause has been a consistent issue well beyond
this mod. While it's laudable to try and figure it out, it really is different than getting this mod to pass. And the
smallest list to observe it is the best idea." His card rule is unchanged: mod-on p99 within 10% of the same colony's
mod-off run. The game's own freezes are RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD, not this visit.

## What changed

- Harness 1dd790af20: `--frames-only` runs only the interleaved frame pairs and FRAME_BUDGET, refused on the full list;
  the full-list walk keeps its behaviour rows, runs one unjudged mod-on arm for the tick cost, and reads FRAME_BUDGET from
  `--frame-evidence <frames-only json>` (UNMEASURED unless that file is a frames-only run below --full-min active mods on
  the same deployed DLL). Selftest W31-W34 new, W0/W19-W30 moved to the small list; red on 3606c33e12, green after.
  tree.json walk_storeroom_raid and scenes.json sc_walk_raid reworded, tree re-certified on his 5:43 words, stages 3 and 5
  re-pinned (8ff90a7006).
- Mod 7c6cb7412a (release DLL 51eaadc060): a pawn our knockback throws lands without vanilla's job search
  (RM_Patch_JobTracker_KnockbackLandingNoSearch). Selftest landing_job_search red on 2aa1fac3dc, green. Proof build only:
  RM_FrameProbe's CSV gains flush / takeoff / landing / resume ms per frame.

## Where it ran, and why there

Archmagi's game was held all sitting (Gimme Some Slack visit and the owner's looks), so SteveDesktop (bridge taken, never
forced): the Explosive Knockback tier, visit 3's 34-mod env_minimal2, every DLC (env_small_steve.json). The full-list walk
save cannot load on 34 mods ("Error while loading a map", World.ExposeData: 286 of its mods are absent) [measured], so the
storeroom was rebuilt cell for cell from that save on an AridShrubland quicktest: granite walls, the LWM weapons locker,
both shelves, the 11 stacks, the 5 colonists, and 3 colonists elsewhere as in the original (save
EK_WALK_SMALL_COLONY_20261116 on SteveDesktop).

## The row's numbers (FRAME_BUDGET, small list; evidence/*.json)

| run | build | pairs | on p99 (median) | off p99 (median) | verdict |
|---|---|---|---|---|---|
| 1 | cca4f0d4 (visit 3) | 3, cold | 44.2 | 38.9 | FAIL +13.6% |
| 2 | cca4f0d4 | 3, warm | 38.3 | 39.7 | PASS -3.5% |
| 4 | cca4f0d4 | 3, cold | 46.4 | 45.7 | PASS +1.5% |
| 5 | cca4f0d4 | 9, cold | 43.2 | 36.8 | FAIL +17.4% |
| 6 | cca4f0d4, the 5 colonists removed | 5 | 33.8 | 33.4 | PASS +1.2% |
| 7 | timers | 3, cold | 41.6 | 36.3 | FAIL +14.6% |
| 8 | 011a6a37 (fix + timers) | 3, cold | 45.3 | 45.6 | PASS -0.7% |
| 9 | 011a6a37 | 9, cold | 37.8 (8 read) | 37.3 | UNMEASURED (one reload stuck at Entry) |
| 10 | 011a6a37 | 9, cold | 53.6 | 45.1 | FAIL +18.8% |
| 11, 12 | vanilla-path timers (diagnosis) | 3, cold | 38.1 / 45.4 | 46.8 / 46.2 | PASS -18.6% / -1.7% |
| DECISIVE | 011a6a37 | 21, cold | 46.3 | 44.9 | **PASS +3.1%** |

The decisive run was declared before it ran (ledger note "PRE-REGISTERED"): one cold run of 21 pairs on the deploy
candidate decides the row whatever it reads; no reruns for a better number. It took four launches to get one reading: the first
crashed natively at game start (RimBridge's socket bind), the second right after the colony load (Mono, Task
continuations), both before any arm; the third ran every arm at ~10 fps (about 100 window frames an arm against ~480 in
every other run; cause unknown; iCloudHome was holding one full core on SteveDesktop throughout) and read UNMEASURED by the
like-for-like gate (evidence/ek_frames_small_DECISIVE_21_attempt3_10fps.json). The fourth is the reading
(evidence/ek_frames_small_DECISIVE_21.json): on p99s 41.7-63.7, off 41.8-58.5, frame counts 474/479. A blind instrument is
not a number, so the reruns chose nothing.

## Cause, with evidence

1. The extra cost is thrown pawns. Without the 5 colonists the arms read +1.2%, each on arm with one ~53 ms frame at launch,
   the size of the vanilla blast frame (run 6). With them, every on arm had a 48-105 ms frame 0.07-0.18 s after takeoff.
2. Proof timers (run 7): each pawn landing spent 19-25 ms inside vanilla PawnFlyer.RespawnPawn, whose CheckForJobOverride is
   a full think-tree search; our postfix then starts the job suspended at takeoff anyway. The mod's resume itself: 0.03 ms.
3. After the fix (runs 8-10): a landing costs 0.6-4 ms. Per-blast excess frame time (sum over the blast second above the
   arm's own baseline), on minus off: +32 ms on cca4f0d4 (run 5), 0 to +16 ms on the fixed build (runs 8-10, 12); +14 ms in the decisive run, where a landing cost 0.8 ms (median of 25, max 2.2).

Ruled out (proof timers): the request flush (1-3 ms warm; 8-18 ms on the session's first throw only, cold JIT), the
in-memory journal, flyer drawing (0.1-3.6 ms), the map mesh rebuild (0.0-0.1 ms), and job searches as a mod cost (25-28 ms
each on this host, but the same three far colonists search at the blast in both arms; per-arm totals equal: on 236-359 ms,
off 275-415 ms).

## What the instrument can and cannot say

A p99 over ~480 window frames is the 5th-slowest frame. On SteveDesktop the mod-off arms alone spread 35-57 ms there, so
3 pairs flip and 9 pairs read +1% to +19% on one build. The 10% bar is about 4 ms, inside that spread. The 21-pair median
is the decision; the per-blast excess above is the better reading of what the mod costs.

## The acceptance (rows.jsonl)

Full-list leg, Archmagi (bridge taken when free, ModsConfig backed up to
`D:\ClaudeWork\backups\ModsConfig.pre_ek_walk_fullleg_20261116T091447.xml`, 316 mods, the same DLL 011a6a37, cold load
09:15-09:28 PST): `--save EK_WALK_RAID_BASE_20261115T173148 --frame-evidence evidence/ek_frames_small_DECISIVE_21.json`
exits 0, 18 of 18 rows PASS (evidence/sc_walk_raid_fulllist.json). CARRIER_TICK_COST is recorded, not judged, and its
read found 0 carriers in the air (5.73 ms at rest, 5.57 ms after the shells): it measured nothing about carriers this time.

## Left

- The first throw of a session still costs 8-18 ms in the request flush (cold JIT); one frame, once. Not filed: it did not
  decide the row (the first on arm is the highest in every cold run, and the median absorbs it).
- SteveDesktop crashed natively three times and ran one run at ~10 fps; noted on
  RIMMANDRAKE_FIX_JAWABENCH_AWARENESS_INSTALL_CRASHES_START. Its force stop failed once:
  RIMMANDRAKE_STOP_STEVE_GAME_FORCE_KILL_LEFT_IT_RUNNING.
- SteveDesktop was left on the 34-mod list with the proof DLL 011a6a37 and Archmagi's FlowWorks, StructureInjections,
  StructureInjectionsRUT (its old folders are in `~/rm/backups/ek_pilot_*` on SteveDesktop's WSL); the runner's next
  deploy replaces them. Archmagi was left on the 316-mod list with the same proof DLL, the walk colony loaded.
