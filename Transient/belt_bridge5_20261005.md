# BELT bridge5 — FlowWorks live run, 2026-10-05

## Milestones
- [16:15] committed stray result 20261005T143030 (precedent: results tracked). offline preflight: P-O2 pitDepthDrawOffsetEnabled uncovered; P-O3 deploy drift; P-O4 FULL.LATEST diff; P-O5 golden stale (DLL + viscosityEnabled)
- [16:2x] P-O2 fixed: toggle_pit_depth_draw chain (pushed 138c04e30). deployed FlowWorks DLL+srchash, ResearchRetag patch. bridge TAKEN
- [16:18] tier flowworks (10) applied, ModsConfig backup Transient/ModsConfig_before_bridge5.xml (50); launched via Steam; quicktest 250x250 AridShrubland up. watchdog 16:16 HEALTHY. running prep_site
- [16:2x] golden rebuilt (prep_site --rebuild rc0). preflight LIVE CLEAN 17/17 (after jawa/prefs autosave=14; RESTORE 0.25 at release). offline: P-O1/2/3/5/6 PASS, P-O4 FAIL = env: pre-swap 50-mod list != FULL.LATEST (restore is exact-bytes backup, not restore_full) -- not a FlowWorks defect. starting v2 --live --fresh-map
- [16:24] v2 LIVE GREEN 74P/0F/0 UNBUILT (validation_v2_result_20261005T162414.json, 9484 ticks, 207 s). All 10 promoted rows PASS first live run (X1-X9, X7n, P4b). watchdog HEALTHY x3
- [16:27] recorded: modcheck FlowWorks PENDING-OWNER-REVIEW (pushed cf92c1716). next: review savegame + sheet
- [16:3x] review shots Transient/belt_bridge5_review/ (7 scene groups) + review save NS_FlowWorks_Review_20261005.rws (new file, no other save changed). autosave pref 0.25 restored; game killed; ModsConfig restored exact bytes (50); bridge RELEASED. GREEN_FULL skipped: gated on GREEN_MINIMAL (owner review pending) + 639 full list not saved anywhere
- [16:4x] owner sheet built: Transient/belt_bridge5_review/FlowWorks_owner_review.html (43 bars, 10 prefilled contested, check_sheet 0 FAIL/1 WARN prefill-rate). NOT served/click-tested (chrome MCP down; subagent sidecar would die). ledger notes on GREEN_MINIMAL_1 + TRIAL_1. DONE
