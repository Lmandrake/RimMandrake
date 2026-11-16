# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 3

Detached helper, seat BENCH, item RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED (live_driver run-1794824768), started 2026-11-16 02:27 PST.

## Progress
- 02:40 skeleton written; bridge taken (BENCH); game down. First: the frame-probe bridge read (my item) so one proof build serves the visit.
- 02:50 frame-probe bridge read landed 0459550b0c; proof DLL md5 04c70301 deployed (+FlowWorks, Biomes); 34-mod list = visit 2's env_minimal4 (env_minimal.json); quicktest AridShrubland tile 45875 via live_site.py.
- 03:05 first pass of the 53 minimal checks (pit_fetch apart): 52 PASS, sc_storeroom_bomb_pit FAIL; sc_no_careless_fall PASS but site_checked false (a hostile Human left by an earlier scene). Next: diagnose storeroom_bomb_pit, rerun no_careless_fall on a clean site, pit_fetch.
- 03:15 sc_pit_fetch FAIL 2 of 2 on the 53-scene map (the stack or the corpse "not out"; PitProbe: earlier scenes' corpses and steel hauled into this scene's stockpiles, the stack merged, the corpse moved), PASS 2 of 2 on a fresh quicktest: SITE. sc_storeroom_bomb_pit: goods half = HARNESS (four 2.83-cell shelf stacks skip too_weak, counted unmoved), cover half = the open MOD finding RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY. Fixes 6ab864cf7e (guards G6 and W red then green); proof DLL cca4f0d4 deployed, game relaunched for a clean second pass of every minimal row.
- 03:25 second pass on cca4f0d4 (env_minimal2.json, fresh AridShrubland tile 17404): 53 minimal checks + pit_fetch last on the dirtied map: 54 of 55 PASS. sc_storeroom_bomb_pit FAIL on the cover half only (MOD, open finding). sc_closed_containers INVALID once (heavy locker staged 74.9 kg, band 76-249), PASS on rerun. sc_pit_fetch PASS 2 of 2 on the 53-scene map (the fix holds). Next: full list for sc_barrage_perf and sc_walk_raid, the labelled save.
