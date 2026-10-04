# Layout fix notes 2026-10-04

## Before

## Changes

## Verification
- desert: 89 rows; rows up to 52 columns (RM_Shadespire: 49 artpipe renders, single facing); letters run A..z (52) so 52 options x group-bulk.
- Options are global (maxl over sheet) -> template renders all-letter bulk + per-row buttons.
- Decisions files all untouched prefill (no writeCount) -> safe to regenerate.
- Scope add (coordinator): canon lookup strips variant words (alpha/juv/feral...), labels "base species"; empty-state wording.
- Layout rewrite done (facings side by side, per-row pick buttons, template hooks bulk:false/itemOptions/decidedAt counter).
- Found: winner from 9-mod live ModsConfig -> every column "shadowed"; load_order now falls back to FULL.LATEST.
- Found: build_row alias word "Plant" joined 49 plant renders to every plant row (B0).
- Census --refresh drops the 19 RSW_ twin rows (cc4111e83 producer never committed) -> adding to biome_census.py.
- Coordinator §5.4 fixes in progress; canon 3-state via design/RimStarWars/canon_references/NO_SOURCE.json.
- 15:36 a foreign 'git pull --rebase --autostash' in this clone reverted art_sheet.py (left in stash@{0}); recovered by git show. stash@{1} held the uncommitted twin-row census code from cc4111e83; re-applied to biome_census.py. 23 art ledger events from my backfill also stranded in stash@{0}; re-run backfill restores. KotORBandolierNorthFix/Source/build_north.py differs from stash@{0} (not mine).

## Result
- desert page 81,223 px -> 23,338 px at 1600 (median row 651 -> 206 px); 27,858 px / median 237 at 1280. No horizontal overflow; 0 console errors.
- resolution_audit before -> after: A1 12->5 (rest are texture-sharing, B3), A2 NO ART 157->111 (census self-contradiction 73->0), B1 name-joined cols 5,619->374, B2 141->63, B4 793->0, B5 259->131 cols.
- check_sheet 0 FAIL 0 WARN on all three; selftest_art ALL PASS (3 unrelated selftests fail: bridgetools metadata, starwarspatches semantics, utinnipatches dump).
