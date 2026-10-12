# THEFT_ROW_REPAIR_WITNESS_WALKS_OFF (HARNESS, FlowWorks live checks)

`Transient/bench_live_20261011/fw_live_checks.py` block L6 spawns two lordless neutral villagers 5 cells NE of the foreign tank, then
watches 1,000 ticks. They walk off before the first theft check (TicksGame % 250 == 7), so `L6_theft_spotted_letter` FAILs with
caught 0 -> 0 whatever the mod does: BENCH 2026-10-12 rerun with the footprint-aim fix (DLL e8860a76) still read 0 -> 0, while
`Transient/bench_live_20261012/fw_theft_los_probe2.py` (witness spawned 3 ticks before the check, still at (81,185) at it) read
caught 0 -> 1 and the letter. The 2026-10-11 probe had the same confound (its NE witness was read at (73,200)). The `--theft-day`
loop also lets colonists idle: a Tantrum (tick 126,799) smashed our Fill tank before a day of touched ticks accrued.

Fix (harness only): spawn each witness at tick % 250 == 4 and read caught after the check; draft every colonist before the day loop;
refill/empty every 2,000 ticks so every cycle is touched. Move the row into src/RimMandrake/FlowWorks/northstar/ when fixed (the
Transient script has a 14-day shelf life).

NEXT: port fw_live_checks L6 into src/RimMandrake/FlowWorks/northstar/ with the timed-spawn witness, drafted colonists and 2,000-tick refills, and rerun it once.
