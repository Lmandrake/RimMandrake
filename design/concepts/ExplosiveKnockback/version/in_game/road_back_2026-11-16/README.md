# ExplosiveKnockback road back after visit 2 — live holder run run-1794816087 (2026-11-16 PST)

Archmagi, RimWorld 1.6.4871, ExplosiveKnockback PROOF build from source 6624908423 (deployed DLL md5 8753d17373e353be5878f971edb04644),
FlowWorks deployed from the same main.

## sc_barrage_perf (RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO)
Full list (316 mods, ModsConfig = FULL), quicktest AridShrubland 250x250 (live_site.py --biome AridShrubland, 3 colonists, site_checked).
Command: `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes frame_probe_selfcheck,barrage_perf_off,barrage_perf --ticks 0 --real-seconds 25`
| run | control windowP99Ms | barrage windowP99Ms | verdict |
|---|---|---|---|
| 1 | 30.9 | 32.1 | PASS |
| 2 | 21.1 | 20.3 | PASS |
| 3 | 20.0 | 20.4 | PASS |
Evidence: sc_barrage_perf_run{1,2,3}.txt and the runner's run_*.jsonl beside this file.
