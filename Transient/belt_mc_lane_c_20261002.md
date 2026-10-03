# BELT MC lane C — art styles + selector (Fri Oct  2 17:28:21 PDT 2026)

## Steps
- [ ] 0 read
- [ ] 1 wire art
- [ ] 2 selector
- [ ] 3 validation
- [ ] 4 live

## Log

- 17:31:15 step0 read done; plan: Styles/<Family>/ folder per family, Jawa stays at root
- 17:36:21 step1 art: 42/42 pieces wired (wire_style_art.py), compare sheet written; aerial def adapted (attachZ, spread, lamp top). step2 code: CordMaterials rebuildable per style, per-net variants, settings UI+swatches, AerialMaterials.EnsureCurrent, StyleProbe
- 17:38:15 step3 validation.py: O5 style art (52 PNG, can-fail probe) + ST1-ST5 live rows + settingsroundtrip probe; offline 5/6 (O1 FAIL = lane D Hose/HoseMath.cs not in csproj yet, not lane C)
- 17:38:43 step4 live: lock acquired; game was up (PID 37036), closing
- 17:49:46 tier messyconduit, deployed, game up (PID 26892) bridge 15s
- 17:53:09 validation --live: 40 PASS (32 prior + ST1x4, ST2-5), 0 FAIL
- 17:55:45 save-load A=MC_LaneC_A_1753 PASS 3/3; aerial live 18/18
- 17:57:18 style shots 8/8 ST PASS; 9 PNGs style_* written
- 18:01:23 aerial save-load 3/3, removal M9 + M9b PASS on flowworks tier; game left UP on flowworks; live lock released; round-trip settings file (did not exist before) removed
- 18:01:49 DONE: README + LEARNED updated; offline 6/6
