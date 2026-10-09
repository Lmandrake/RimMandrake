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
- Stage 3a: twilight wells migrated (base = waning radius, Scribed lid-dark cap, re-asserted on FinalizeInit). Waning-step/frozen rulings in TWILIGHT_WELL_LIGHT_STATE_1 untouched.
- Stage 3b: EnvironmentalHazards warbling glow → `eh.warble` multiplier (cleared when the setting is off).
- Stage 3c: LanternDeeps aurora → `ld.aurora` mul; sippers → `ld.sipper` proportional mul (SipperLedger tolerance-guessing deleted). Fuzz first caught a subtraction blacking a lamp out when the aurora ended → share made proportional; floor now holds at every step. Shared kernel gained ScaledExcept → TB/EH rebuilt in the same commit.
- Stage 3d: Abyss Dark → `abyss.dark` mul, krizzak → `abyss.krizzak` mul; they compose (the Dark no longer skips krizzak lamps). Kernel arithmetic unchanged (run in the ledger view), so abyss fuzz + mutation strings stand. New setting `darkSparesDeepfire` (on) + explicit deepfire skip. moddefs_lint/lanterndeeps_lint taught linked `..\..\_Shared` sources.
- Stage 3e: LuminousPigment proxies → ledger base; proxies + glow tank tagged `deepfire`; hediff/worn proxies carry their pawn. Write lint now has no allowlist: 0 direct GlowRadius writes outside the ledger.

## Stage 4 — DEEPFIRE_WORLD_LIGHT_1 (all four rulings)
- (a) TerminalBiomes `RM_JobGiver_SeekGlow`: lit deepfire-tagged lights of any owner count; seekers BASK at them, never graze. Toggle `seekGlowDrawnToDeepfire` (on).
- (b) Abyss: shipped in stage 3d (`darkSparesDeepfire`, on).
- (c) LuminousPigment: hourly, dark sky (<0.3 PROVISIONAL) on a home map, +0.05 visibility per lit deepfire light (PROVISIONAL), max 2/hour, via soft lookup of `GameComponent_ColonyVisibility.Adjust`. Toggle `deepfireNightVisibility` + slider.
- (d) Scarlands lacquer cloak: denied while `LightLedger.CarriesLitLight(wearer)`. Toggle `lacquerDeniedWhileGlowing` (on).
Full selftest suite: 254 pass, 1 fail (art placeholder lint, passes alone — not this work).
- Ledger: both items `implemented` (owe L1 live criteria, bridge); notes on SUN_SPHERE_GRAZE_PERSIST_1 and TWILIGHT_WELL_LIGHT_STATE_1.
