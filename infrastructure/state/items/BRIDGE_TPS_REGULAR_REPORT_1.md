# BRIDGE_TPS_REGULAR_REPORT_1 — TPS is gathered and reported all the time

## spec
Owner, 2026-10-10: the bridge should regularly report TPS during use. He regularly sees very slow
(and fast) TPS; agents asked to investigate say they cannot reproduce it. TPS is central to player
experience, so it is a standing measurement, not an investigation.

Outcome: while the game runs with the bridge (JawaBench companion) loaded, TPS is sampled on a fixed
cadence (ticks per real second from the game clock, plus game speed setting and paused flag so a
speed-1 vs speed-4 reading is not mistaken for slowness), written to a rolling on-disk record
(JSONL, size-capped, outside git), and surfaced as one line in `belt_watchdog.py` and in a
`[Tool]` the bridge can call. Must not itself cost TPS (sample on the main thread cheaply).

## criteria
- C1 (L0) selftest: the sampler maths (window, paused/speed normalisation, rolling cap) passes offline.
- C2 (L1) on the minimal list the record file grows at the stated cadence and the tool returns last-N.
- C3 (L0) belt_watchdog prints a TPS line and flags sustained low/high TPS against the speed setting.
- C4 (L0) a doc `design/RimMandrake/tps_record.md` says where the record lives and how to read it.

## verify
Read the record file after a live minute; the median TPS at speed 1 is near 60.
