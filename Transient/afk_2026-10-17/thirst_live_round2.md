# Thirst live round 2 — 2026-10-17 (BENCH live driver)

## 0. Offline: settings registry
- 4c87fbef17: 8 thirst settings registered in site_spec.SETTINGS; mock dig-cap text; selftests green.

## 1. Bridge, deploy, load
- `rimflow bridge take` REFUSED: FOUNDRY holds it since 20:17:11Z for "FlowWorks P3/P4 live proofs + walks" (idle 2 min, holder pid alive). Stopped per order; nothing live run, no deploy. Coordinator then reported FOUNDRY released 20:52Z and BENCH took it (20:53:01Z) for this round.
- 20:56Z game closed (Stop-Process; log copied to `live_r2/Player.before_r2.log`); deployed FlowWorks (DLL + srchash + OrdersPatch) and compose biomes (LeaningScrub DLL). ModsConfig had become an 11-mod list (FOUNDRY's); rewrote the 20-mod walk list with walk_modlist.py --apply (backup PRE_WALK_20261017T135630.xml). Launched via Steam; bridge token at ~2 min; log 312 lines, no Exception line, provider Own.

## 2. T15R / T15
- T15R PASS on the new DLL: B got A's ID (Human36705), B's search at tick 92 inside A's window [2, 602), drank red in 30 ticks. The stale-mark fix holds.
- T15 PASS: all four colours exact, the 0.05 pawn drank nothing.

## 3. Undriven rows T14 T16 T18 T20 T23 T25 T26 T29
(pending)

## 4. Full reruns (credit at current mod hash) + modcheck
(pending)

## 5. Mod bugs fixed
(pending)

## 6. End state
(pending)
