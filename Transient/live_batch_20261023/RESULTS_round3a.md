# BENCH live round 3a — 2026-10-23

Save: RM_fw_walkthrough_20261022d (fw_gss_sitting tier). Bridge: BENCH.

## 1. PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN
Verdict: PASS for every proof that can run on a review save; one HARNESS hole found and fixed (WALK_KEEP_FIX_SNAPSHOT_STAYED_HOME, 3d06a6028672).
Zoo before (r3a/zoo_r3a_before.json): map C (0) 9 non-colonists (Chicken, Husky, 3 Muffalo, 2 TribeRoughNeanderthal prisoners, Thrumbo, WildBoar 39,23); map R (48) 1 Muffalo.

| proof | run | zoo | verdict |
|---|---|---|---|
| raid_trench_proof --direct --ticks 5000 (map C, current) | sweep_start route none-needed, kept 9; RAID_island_sealed PASS; outcome SHOT_ACROSS (1 colonist down); 6 PirateYttakin raiders vanished after (tools/killids.py) | C 9 -> 9 (+ a wandering Vulture); R 1 -> 1 (+6 wild horses, a herd arrival on R while the raid ticked) | PASS (r3a/raid_trench_saved_C.json, r3a/zoo_r3a_after_raid.json) |
| water_scenes_walk prep, then go S1 --no-shots, then restore (map C) | prep: opening sweep none-needed, kept 10; S1 ran (site not pristine: S1.a DIFFERS, S1.d UNMEASURED - SITE, review map, not scored) | C: WildBoar1864604 (39,23) GONE, no corpse | FAIL/HARNESS -> fixed |
| repro + fix | the keep snapshot is per PROCESS: only `prep` took it, so a separate `stage/go S1` had KEEP_PAWNS empty and prepare_site's remove_intruders (S1 rect 0,28,28,15 + 30 margin) vanished the boar. Repro: wild boar spawned at 40,22 (faction none) vanished on `stage S1` pre-fix; fix = every stage/run/go/all verb on a current map calls sweep_at_start(made_map=False) first; post-fix two boars at 40,22 survived two `stage S1` runs (trace r3a/trace_stage_S1.log); test boars removed after; selftest_water_walks 0 failures | | PASS after fix |
| validation_v2 --current-map | not runnable on a review save by design: L1 aborts 'site not pristine' (map C excavated 2578, superdeep 937) BEFORE any phase sweep, so it cannot eat a review save's zoo; its keep snapshot (line ~4748) is taken before L1 | - | UNMEASURED/by design (no zoo risk) |
| prep_site | builds the golden site save from a fresh map; never runs on a review save | - | out of scope |
| liquid_checks | PASS in round 2 (9 -> 9) | | PASS |

Zoo after (r3a/zoo_r3a_after_water.json): C 8 of the original 9 (the boar lost to the pre-fix walk) + Vulture; R Muffalo kept.
Side lessons filed: jawa/spawn_pawn of an animal with no faction spawns it as Mechanoid (hostile) - pass faction "none"; a truncated bridge print grepped for an id reads a live pawn as absent (my call.py, caught by the full-list zoo read).


## 2. C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING
Verdict: A2 PASS (cord over land); 'no power' = NOT A DEFECT (vanilla PowerOn lag on a just-built consumer, game paused); the loop = GSS canned slack loop placed over the pipe -> MOD (GSS) filed CORD_LOOP_UNTANGLE_LASSOED_A_PIPE.
- Rebuilt C1 on in-memory map R: scenarios_map.py --river --build (map R current first; map_r_placed.json backed up and restored, unchanged in git). C1 at origin 15,34: Battery 34,69-70, PowerConduit 34,71/34,72/34,73, RM_LiquidPump 35,73, pipe 35..38,72 (r3a/rebuild_mapR.log).
- Power: GSS probe rect:32,68,8,8 -> 1 net, netLive true, nodes battery 34,71 + consumer 34,73 both netLive. HoseProbe pump:35,73 right after build (paused): powered false; after safe_advance 400 ticks: powered true, moved 10000 units at tick 138938. Save d's own C1 pump (116,74) reads powered true, moved 19. The judge's bolt was a capture taken paused right after a --build (soak skipped); builder could step ~400 ticks before shooting (note on the item, builder file not touched: other helper's).
- Cord: ONE strand, edge consumer:34,73|battery:34,71, 186 pts, length 9.44 vs chord 3.64, one self-crossing (pts 53/114) = the closed loop centred ~36.7,72.5 (radius ~0.48) round pipe cell 36,72. Drawn by _Shared/SlackGeometry/CordLayer.AddLoops (canned loop/figure-8, LoopsPerCell 0.35, design 8.10): AllClear tests only walkability, so a pipe cell is 'clear'. By-design mess, wrong placement. (r3a/c1_cord_probe.txt, r3a/C1_cord_powered_after400.png)


## 3. MAST_PIPE_MEND_STOPS_SHY
Verdict: (a) mast join = MOD (FlowWorks join draw), stays open with a precise spec; (b) blue->copper elbow = NOT A DEFECT (scene design).
(a) Rebuilt C1 (origin 15,34): RM_UniversalPipe 44..46,72 | RM_PipePole 47,72 ... RM_PipePole 52,72 | RM_UniversalPipe 53..55,72 (r3a/c1_mast_cells.txt). RM_PipePole has no linkFlags; the pipe links to it only through Patch_Pipe_LinksIntoMachines (RM_LiquidJoins.PipePoleAt, D5 2026-10-22), which makes the linked atlas run the arm to the SHARED CELL EDGE (x=47.0). The mast art (AerialMast 2x4, drawOffset z 1.5) stands its trunk base at ~x 47.18 and its grey riser pipe at ~x 47.5 up the trunk, so the ground pipe ends ~0.18 cell short of the trunk with nothing joining it to the riser (r3a/C1_mast_join_west.png at 114 px/cell: pipe end 228 px = 47.00, trunk 248 px). Fix (FlowWorks C#, after the hose helpers' deploy): give a pole the tank treatment - an inset/riser like RM_LiquidJoins.RiserInto + SectionLayer_RM_PipeCentreStubs so the arm runs into the pole cell to the trunk and a clamp/flange or a short bend joins it to the riser; offline-selftestable via LiquidJoinRule.
(b) Elbow 61,46 (r2/C1_rebuilt_no_tail_61_44.png): jawa/thing_graphic reads pipes 59,46 and 60,46 resolvedPath Pipe/Futuristic (blue), 61,46 (the corner) and 61,47 Pipe/Scrapper (copper). c01_thirsty_terraces styles each sprinkler row x 38..45 (abs 53..60) in its row's look (ROWS: z12 = Futuristic) and leaves the trunk x 46 (abs 61, z 46..71) at the default Scrapper look; the corner belongs to the trunk. Two looks meeting at the row/trunk boundary is the scene's 'four looks side by side' design, not a style-map gap.


## Watchdog log
- 03:15 belt_watchdog: WEDGED on save-d SaveableFromNode abstract MapComponent load errors (known absent-tier noise); bridge answering, game paused.
- 03:27 belt_watchdog after reload of save d: 03:28:00 WEDGED -- player_log: updated 25s ago; repeating every frame: 42x (93% of tail errors) "SaveableFromNode except

## End state
Game UP, save RM_fw_walkthrough_20261022d reloaded (tick 130096, map C current, paused); all in-memory changes of this round (raid site, map R C1 rebuild) discarded; saves b/c/d untouched (no save written). Bridge still held by BENCH for the deploy + re-check round.
