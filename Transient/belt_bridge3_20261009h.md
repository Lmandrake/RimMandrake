# Belt bridge3 20261009h

Scope: predecessor's open rows (cord handoff, superdeep target, seeded glow tank, POND_RECESSION_STRANDS_CHANNEL_1),
CRUST_NEVER_STRANDS_1 A2, BAROQUE_LOAD_RESIDUE_ERRORS_1. L0-L3 only.

## Milestones
- started (bridge held by FOUNDRY for this helper)

## Left for the next sitting
- 19:05 CRUST_NEVER_STRANDS_1 already done (A2 verified pass 22:50Z, acc_biomes) - skipping (2)
- 19:15 POND_RECESSION mechanism read: Recede() neighbour-first order drops the channel INLET cell second (its pond-side neighbour recedes first, so it falls to fewest-neighbours). Fix in src: outflow cells (dug cardinal neighbour) recede last, setting recedeSparesOutflow (PROVISIONAL), oracle+census 38+selftest updated. Building.
- 19:30 POND fix published 5789216de (selftest 139/139, v2 offline+mock green); control FAIL on old DLL recorded; regression live_probes/fw_pond_outflow_regression.py; implemented, A2 L2 owed after FlowWorks DLL deploy (batched for one reboot)
- 19:45 CORD: added strands: probe command (GimmeSomeSlackProbe) + PrintedStatic record in SectionLayer; GSS DLL built, deploy batched
- 20:00 built JawaBench jawa/attack_target_probe + jawa/thing_refuel (plan-only, deploy batched)
- 20:15 scripts written: FlowWorks live_probes/fw_superdeep_target.py (rewritten on attack_target_probe, rule-off control), LuminousPigment/live_probes/lp_glowtank_seed_sow.py, GimmeSomeSlack/live_probes/gss_cord_static_dynamic_handoff.py. Now BAROQUE offline before the one reboot.
- 20:35 published 1d08588a5 (tools+scripts) and baroque residue fixes; rebooting to deploy FlowWorks+GSS DLLs, JawaBench, composed Biomes
- 20:45 relaunched (37s). L1: salvage cache / chitin leather / sweetline / yearning fruit errors GONE. New residue: Sump dusk-lock FindMod gated on own mod name (fixed in src, regated on UtinniPatches, deploy pending); donor-texture misses RM_MuttavaqUttaqar(RockTroll), LongShade TruffleMole, RM_Radyak, RM_RipperHound (art-owed, not fixed).
- 20:50 POND A2 PASS live: drained 7.8/15.8/23.8/29.8 of 30 (D1-4), channels full, inlet stays source (pre-fix control 5.76 every depth). verified.
- 20:53 SUPERDEEP A1 PASS (state read via jawa/attack_target_probe): rule ON picks open-ground enemy (x80) over nearer pit enemy; control rule OFF picks pit (x62); only-pit -> null. verified.
- 21:00 GLOW_TANK seeded probe: fuel 1->0 + established=True on sow (spawned-crop route; colonist did not sow in 6000 ticks), control unseeded stays False, BUT the tank goes DARK once established (CompRefuelable IThingGlower lit only with fuel). Fixed in src: postfix lights an established tank + UpdateLit on establish/blackout; LP built, selftest ALL OK; deploy pending
- 21:05 CORD A1 PASS: lifted strand owner section 153 / pin section 170; open=dynamic only, pin roofed=static only, pref off (roofed & open)=static only badPaths 0, pref on=dynamic only. verified.
- 21:15 GLOW_TANK A1 PASS after fix 6c35cfa42 (established tank lit; control unseeded False). A2 (colonist sow) owed: no colonist sowed within 6000 ticks on the quicktest - crop was spawned. Sump FindMod error gone from log.
- 21:40 GLOW_TANK A2 (colonist sow) left UNMEASURED: research + Plants 12 + forced power, no sow in 6000 ticks (tank still reads 'Not connected to power'; colonist left the room). Noted on the item with NEXT.
- BAROQUE_LOAD_RESIDUE_ERRORS_1 done (L1 log clean of its 4 rows + the Sump patch). Donor-texture misses (Radyak, RipperHound, RockTroll, TruffleMole) are tracked by DONOR_CODE_PLAIN_PORTS_1 / DONOR_DEFS_PORT_TO_OURS_1.

## Results
- POND_RECESSION_STRANDS_CHANNEL_1 done (5789216de): outflow cells recede last; live D1-4 drains 7.8/15.8/23.8/29.8 of 30 (was 5.76).
- CORD_STATIC_DYNAMIC_HANDOFF_1 done: new GSS probe `strands:`; 5-step roof/pref handoff single-path.
- SUPERDEEP_TARGET_VALIDATOR_1 done: new jawa/attack_target_probe; rule picks open-ground enemy, rule-off control picks pit.
- GLOW_TANK_SEED_LIVE_SOW_1 A1 pass after a real fix (6c35cfa42: established tank went dark); A2 owed.
- CRUST_NEVER_STRANDS_1 was already done before this sitting.

## Left for the next sitting
- GLOW_TANK_SEED_LIVE_SOW_1 A2: wire the tank to a real generator + conduit, re-run lp_glowtank_seed_sow.py, route must read colonist.
