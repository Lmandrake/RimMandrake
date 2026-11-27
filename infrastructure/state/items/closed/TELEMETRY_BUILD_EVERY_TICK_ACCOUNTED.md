# TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED

Design: `Transient/weekly_cleaning_2026-10-11/08_telemetry_deep_design.md`. Owner picks (00_SUMMARY.md): hybrid
VictoriaMetrics + SQLite + Grafana + RimPulse alerts, data on E:, 1 s test tier + flight recorder.
Skill: `skills/telemetry/SKILL.md`. Code: `src/RimMandrake/Utils/telemetry/`, JawaBench `JawaBenchTpsTier*.cs`.

## owner rulings 2026-10-11 (by card, after the build)
Full text: design doc §12. Minimal by his word: *"Minimal is good, add functionality as needed by debugging."*
Streams tagged with mod set + versions; no per-deploy ceremony; no image-slack alert; low-TPS alarm at normal speed,
tolerant of bridge spikes, every firing logged for tp/fp tuning; health observer off until the overhead test.

## criteria
- C1 L0: offline selftest `selftest_telemetry.py` green (51/51) and `selftest_tps_record.py` green (37 C# units, 68/68 parity)
- C2 L0: Windows stack up and windowless: `selftest_telemetry.py --live` 55/55 (heartbeat, VM + Grafana HTTP 200, no telemetry process owns a window)
- C3 L1: deploy the P2 companion with the game down (`build.py --gm --apply`); `telemetry tier test --ttl 10` arms it; 1 s sample rows carry tier/hist/exc/br; disarm writes a flight dump that `telemetry flight --show` reads
- C4 L2: MUST 17-style overhead A/B with the tier armed on the full list; the P2 cost is measured, not estimated (P2's gate in design §9)
- C5 L1: live-check the three P2 fixes with no offline test (Once used-keys read, disarm-dump rate-limit exemption, mapcomp counted as bulk)
