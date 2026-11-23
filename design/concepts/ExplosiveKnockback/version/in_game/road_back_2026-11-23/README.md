# ExplosiveKnockback road back after visit 4 (holder run-1795464425, ArchSmall, 2026-11-23 PST)

Game: ArchSmall, RimWorld 1.6, tier `explosiveknockback_visit` (24 mods, all five DLC), AridShrubland quicktest. Proof DLL of the deciding
readings: md5 107deb57 (`D:\ClaudeWork\rimmandrake\ek_run_20261123\proof_cap2.dll`, the sources of this commit). Only the frame row and the
full-list walk need that exact file.

| what | real build | fault |
|---|---|---|
| FRAME_BUDGET (walk_storeroom_raid --frames-only, 21 cold pairs, pre-registered) | PASS, mod on 7.3% under mod off (51.8 vs 55.9 ms; window frames 499-557) `ek_frames_small_DECISIVE_21_capped_20261123.json` | `plant_slow_flight.patch` (45 ms a frame while a good flies): FAIL +14.5%; at 90 ms UNMEASURED by the like-for-like gate, never PASS |
| sc_spared (RIMMANDRAKE_HOLD_SPARED_CARRIER_IN_BLAST_IT_WALKED_AWAY) | PASS 10 of 10 (f74ea550), 5 of 5 (107deb57) | held only from +55: INVALID 3 of 30, the carrier off its staged cell (the walk-off, measured); PF_CALLER_PIT_NEVER_READ: FAIL 3 of 3 |
| A_RELOAD_NO_DUP_LOST (a step cut short by the load's pause) | PASS 4 of 4 | offline W35: cut step plus a twin FAIL, dead clock UNMEASURED |
| COVER rows (a rider killed by the grenade is thrown again) | PASS 8 of 8, two of them on the second throw | offline W37: living rider, no descent, FAIL |

The first 21-pair run (f74ea550) is UNMEASURED: 517 to 2678 window frames, because vsync does not hold a covered window; no verdict was read
from it. The probe now holds 60 fps. A run on c197f043 was stopped about 2 minutes in, unread, to move the cap's restore into OnDestroy.
Small-list only, seen in the behaviour runs and not touched: C_OFF_IMPACTS_NO_THROWS FAIL 4 of 4 (one silver stack dropped by its own
destroyed vanilla shelf, 0 throw lines; 0 of 11 on every full-list run) and A_GAS_CLUMP_BY_CLUMP FAIL 1 of 8 (one straggler cell; 0 of 18
orders on the full list).

A second 21-pair cold run on the landed proof build (77296ea4, src_id 51f9663608541267), made so the file carries the source id the
full-list walk now matches on: PASS, mod on 1.0% under mod off (50.0 vs 50.5 ms) `ek_frames_small_SRCID_21_20261123.json`. Use this file.

Left: the full-list walk on ArchBig with --frame-evidence, and sc_barrage_perf (both in `unrun.jsonl`, for visit 5).
