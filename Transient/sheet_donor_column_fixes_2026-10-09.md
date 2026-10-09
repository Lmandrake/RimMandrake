# Sheet donor column fixes 2026-10-09

## SHEET_DONOR_COLUMN_FALSE_PASS_1
Already fixed at 98b0bac5f (ours key + label fallback, donorPurged, donorAbsent note counted by req 4; selftest covers all four).
Sweep over 27 sheets in Transient/biome_ffar: req 4 fails on none; 0 donor-sourced rows lack a real donor column, a purged flag or an absent-note. Gate before = after (sheets not rebuilt):
PASS: blue_desert contagion feverwood gelatinousslime greysea lanterndeeps leaningscrub miasma nightsideice rustcathedral thechill thescald thesump warscar webwork
FAIL (none on req 4): abyss(6) cauldron(7,14) deep_desert(6) desert(6) floodedcanyon(14) greentide(6) pyrelands(7,14) theforge(7,14) therot(7,14) twilightsea(6) wasteland(14) weepingstones(14)
(All pre-existing, unrelated to donor columns.)

## ART_SHEET_DONOR_JOIN_GAPS_1
Donor-prefixed names (RG_/AB_/Plant_) and mandrake.* mislabel were already fixed (subject.TIER_RE, name_render_cols, ours). Probed all 12 rows named in gapfill_blindspots_progress: all join now; Swarmling renders are owner-purged (correctly hidden).
Real remaining gap found by diffing joins over 839 census rows: trailing `_Wild` plants (RSW_Plant_Nysyllin_Wild -> nysyllin_v1, Plant_TookeTrap_Wild -> webwork_tooketrap_redo_*). Fixed via subject.join_stems (Wild only; Queen/Alpha/Feral deliberately not shared: different life stage). Selftest in selftest_subject.py.
Sheets need a rebuild to show the new joins (not done here).
