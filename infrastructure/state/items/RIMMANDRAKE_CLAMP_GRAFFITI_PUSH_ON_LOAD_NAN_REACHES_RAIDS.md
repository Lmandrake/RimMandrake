## spec
Found by the Graffiti 0.1.0 blind challenge, cycle 2 (RIMMANDRAKE_JUDGE_GRAFFITI_BLIND_CYCLE_TWO_TESTS_FIRST), 2026-11-17. Class: **Polish**, bar `raider_pressure`.

**Criterion:** a standing mark makes the faction's next raid larger by the setting's factor

**Evidence:**
- lane1 row L1_PRESSURE_EDITED_FILE_PUSH: PressureFactor(true, 1, NaN) = NaN; RM_GraffitiSettings.ExposeData loads raiderPressurePush unclamped, and RaiderPressureMod.Postfix writes PressurePoints into AdjustedRaidPoints' result
- only a hand-edited settings file reaches it: the slider is 1.1..3

**Smallest fix:** in PressureFactor treat a non-finite push as PushDefault (or clamp in ExposeData on PostLoadInit), with a kernel case for NaN and infinities

Record: `design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/faults.json`.

## criteria
any loaded push gives a factor in [1, 3]

## verify
Acceptance test: lane 1 row L1_PRESSURE_EDITED_FILE_PUSH reports every probe in [1, 3] (`python3 design/concepts/Graffiti/version/blind_challenge/cycle_2/lane1/run_lane1.py --out /tmp/l1.jsonl`, then that row's detail starts "every out-of-range push"); today it names NaN.
