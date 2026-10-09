# Belt: LIGHT_LEDGER_ONE_1 + DEEPFIRE_WORLD_LIGHT_1 (2026-10-08)

Progress log, appended per stage.

## Stage 0 — census of light writers
Done: 10 runtime writers in 5 mods (table in design doc). Vanilla never Scribes glowRadiusOverride. SetLidDarkDimming has no caller. Deepfire proxies are Ethereal, so the Dark skipped them only by accident.
## Stage 1 — design doc
Done: design/RimMandrake/light_ledger_design.md
## Stage 2 — helper + first writer + selftests
(pending)
## Stage 3 — migrate remaining writers
(pending)
## Stage 4 — deepfire world-light changes
(pending)

### Stage 2 done
Helper `src/RimMandrake/_Shared/LightLedger/` (ledger + kernel), kernel selftest + write lint `src/RimMandrake/Utils/selftest_lightledger.py` (PASS), TerminalBiomes sun-sphere base + Scribed graze (`RM_MapComponent_GlowGraze`). TB built, TB fuzz OK.
