# ASH_LADDER_FIX_ONE_FIRE_GOES_DEEP (MOD, Pyrelands)

**Bar:** `pyre_ground_ash_ladder`: "repeated burns visibly darken it through trace, light, heavy and deep ash stages."

**Measured live 2026-10-12c** (23-mod ratchet_pilot+patches tier, site anima0 tile 5, FireEcologyHook 0f867dd1):
`Transient/bench_live_20261012c/ash_timeline.log`. A 20x20 cohort of RM_FE_Ground_Soil, grassed, one `map_fire`,
terrain read every 500 ticks: Soil 400 until t=7000; t=7500 Soil 374 + Ash_Trace 26; **t=8000 RM_FE_Ash_Deep 400**, fires 0.
ONE fire walks soil to deep ash inside ~500 ticks; burn 2 then cannot happen (EmberGrass rejected on deep ash: 400/400,
`Pyrelands_ashladder_20261012c.json` evidenceFull), so ground_ash_ladder FAILs every run.

**Mechanism (traced, RimSage):** `Fire.TickInterval` calls `TryBurnFloor()` on EVERY interval once
`ticksSinceSpawn >= 7500`, and `TryBurnFloor` only checks `TerrainFlammableNow`. `AshLadder.xml` makes every rung
except Deep flammable with `burnedDef` = the next rung (the comment's "a scar that burns AGAIN escalates"), so a single
long-lived fire keeps re-burning the floor on consecutive intervals until it reaches non-flammable Deep. The
"burnedDef is flammable" config warning that file documents as advisory is exactly this cascade. The mod has no
TryBurnFloor/Notify_TerrainBurned hook (grep Source/), so nothing gates one rung per burn.

**Consequence for a player:** any Pyrelands fire that lives 7500 ticks on a cell leaves deep ash (fertility 0, no
regrowth), never the trace/light/heavy stages; the 2026-10-01 run already saw 45,343 deep-ash cells on a burned map.

**Fix options (design, owner's call on behaviour):** (a) a Harmony prefix on `Fire.TryBurnFloor` that allows one rung
per Fire lifetime (or per N ticks) on RM_FE ash rungs; (b) make the rungs non-flammable so a burn is one step and the
NEXT fire (fuelled by regrown grass) escalates it; (c) re-rule the bar. Harness rows that would read the fix:
ground_ash_ladder (3 cycles) and this timeline probe (`ash_timeline.py` beside the evidence).

NEXT: pick (a)/(b) with the owner or by the fire-ecology design doc, build it with a selftest, then rerun
`--chains ground_ash_ladder`.
