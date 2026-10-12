# BENCH live sitting 2026-10-11 (20:15-23:25 PDT): GSS / FlowWorks / telemetry / ratchet pilot

Harness: every live script ran from a `git archive` export of **c4bd7af75a** at `D:\Luke\dev\_rmscratch\bench_live_20261011`.

## Deploy (game down, md5 repo == game)
| artifact | md5 |
|---|---|
| RimMandrakeGimmeSomeSlack.dll | 22508fb5bbc60994bf225ab98b2a1c69 |
| RimMandrakeFlowWorks.dll | addf7fd7723bfc795bca03adfa4ac6fc |
| JawaBench.BridgeTools.dll (--gm, the telemetry P2 companion) | f586119842088b2694011abff0e6ef4e |
| composed biomes, UtinniPatches, SWBestiary | deployed before the pilot load (logs deploy_apply_*.txt) |

## Results
**GimmeSomeSlack tier (10 mods)**: proof_all 106/106 (M11 diveThrough PASS; O8 is in the 9/9 offline rows). Tap clamp v3 seen on
an E-W and a N-S foreign run (shots/tapclamp_*_crop.png): the jaws sit on THEIR stub into the tap; handles east on the N-S stub,
upright on the E-W stub. Power theft A2 + A3 PASS (A3 rerun: the first 60,500-tick step stopped at the 120 s timeout after
~7,200 ticks, HARNESS). Chemfuel ignition PASS. cstyles A1 PASS. Telemetry C3 PASS.

**FlowWorks tier (11 mods)**: validation_v2 GREEN 61/61. hose_bend + hose_carry PASS (first runs INVALID: no clean 34x34
site, SITE). fw_live_checks: L1 canal from lake PASS, L2a Dump drain PASS, **L2b pump Pour no faster FAIL (MOD)**, L3 intake
PASS, L4 Fill/Empty PASS (stand-in tank), L5 spill PASS / clean UNMEASURED, **L6 theft never caught FAIL (MOD)**, D1 sluice +
frames PASS, R1 four looks survive blueprint/frame/save PASS (menu not driven), T1 worst FlowWorks component 0.009 ms/tick,
P1 pit coupling patch REDUNDANT (pit 22.87 = open 22.87 with and without it), P1 hot/cold/narrowing rows not settled
(no temperature setter; the pit pawn's exposure marker vanished mid-run, presumed the pawn left the cell), W1 and B1
UNMEASURED (HARNESS). extension_proof dry 90/7/32 (triage ext_dry_triage.md); river half got no site (every river tile
had a steam geyser in the plot grid).
**flowworks_vepipe tier (13 mods)**: pipe-networks tab A2 PASS (one tab, 23 designators, no duplicate-def line).

**Ratchet pilot (22 mods)**: clean load; GSS 106/106; FlowWorks v2 61/61; Pyrelands NOT GREEN 9/11/13 on a gate-B-refused site.

## Filed
LIQUID_THEFT_FIX_TANK_HIDES_ITSELF (MOD) · PUMP_POUR_TUNE_NO_FASTER_THAN_GRAVITY (MOD) ·
CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY (MOD, presumed) · RIVER_SITE_FIX_GEYSER_ON_EVERY_TILE (HARNESS).

## Not run
LAUNCH_HELD_COLONIST_WARNING_1 A3/A4 (needs a gravship plus a held colonist; not scripted). FALLEN_WIRE_SHOCK_1 A5
canal-oil half. Telemetry C4 full-list overhead and C5.

## State left
The game is DOWN. ModsConfig is the owner's 550 list (md5 ee01dae9, from ModsConfig.owner_before.xml). Prefs autosave is back
to 0.25 days. The JawaBench test profile was renewed to 2026-10-12T12:00Z and lapses on its own. The bridge is released.
