# BELT watchers kit 2026-10-08 (WATCHER_CREATURES_MOD_1)

## Steps
- [x] 1 pitch revised
- [x] 2 cue set implemented + selftests
- [x] 3 build + publish
- [x] 4 rimflow implemented

## Log
- 10:37 step2: cue kernel (CueKind/CueIn/Cues/ShadeReading/CueConfigErrors/MediumAudit), RM_WatcherCues.cs, 7 settings toggles, driver+extension wired, startup water audit, keyed strings. Selftests next.
- 10:38 step2 selftests: new cues family + cue bit in step table; fuzz OK 109212 cases; mutations (gas >=, cue emerge) caught. Static validation PASS.
- 10:39 step3: winbuild Watchers OK (0 errors); DLL carries RM_WatcherCueUtility/CueKind/MediumAudit.
- 10:41 step1: pitch revised (rulings folded, Q1/Q2/Q3/Q5 removed, cues + water §1.3/§1.4, clekk for Rust Cathedral under Q7); item prose gains 2026-10-08 rulings.
- 10:46 step3: PUBLISHED d50fcb6b7 (selftests 340/340). step4: rimflow implemented, 5 L2 criteria owed (bridge).
