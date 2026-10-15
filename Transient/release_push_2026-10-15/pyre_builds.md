# Pyrelands BENCH builds — 2026-10-15

Owner, 2026-10-15: "No withheld functionality. Build it all, test it all, get it all working."
Offline only (no deploy, no bridge). One section per item; updated as each lands.

## 1. STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY
state: BUILT offline (companion built with --gm, NOT deployed - no deploy this session)
- `jawa/static_call` now coerces any Thing/Pawn parameter from an exact ThingID (`Human123`) or a bare
  thingIDNumber, current map first then every map; refused with up to 12 candidate ThingIDs when absent or
  of the wrong type; reply carries `thingArgs[]` (how each was resolved).
  `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCompanionProbeTools.cs`
- Pyrelands `furnace_warmth` row: a second colonist 11 cells off as the control; bar = `OffsetFor(beside) > 0`
  and `OffsetFor(away) == 0` via `jawa/static_call RimMandrake.Pyrelands.FurnaceWarmthField.OffsetFor <ThingID>`;
  `jawa/thing_ambient_temp` delta recorded beside it (not graded: three other mods postfix the same getter).
  UNMEASURED (not PASS) if the companion is not the widened one.
- live proof (game down for the deploy): `python3 src/RimMandrake/bridgetools/build.py --gm --apply`, then
  `python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\northstar_driver\cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains furnace_warmth --no-record`

## 2. ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE
state: pending

## 3. TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED / TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL
state: pending
