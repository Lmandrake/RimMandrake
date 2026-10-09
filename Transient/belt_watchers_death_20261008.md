# WATCHER_CREATURES_MOD_1 — death/fragility/ripple pass, 2026-10-08 (FOUNDRY helper)

Owner rulings 2026-10-08 (card, typed): DEATH + ALARM RIPPLE. Offline only.

## Steps
- [x] 0 recorded rulings on item
- [x] 1 flush removed
- [x] 2 fragility + hidden-pawn damage path
- [x] 3 death transition + remains + sign repair
- [x] 4 alarm ripple
- [x] 5 pitch fixes
- [x] 6 build / selftests / publish / implemented

## Log
- 18:42 kernel/flush-removal/death/alarm code written; running fuzz
- 19:11 steps 1-5 written (flush gone, fragility+death+remains+sign repair, ripple, pitch fixes); fuzz 7 families OK, mutations 68/68, DLL built
- 19:11 steps 1-5 written (flush gone, fragility+death+remains+sign repair, ripple, pitch fixes); fuzz 7 families OK, mutations 68/68, DLL built
- 19:12 published 5de62aeab; rimflow implemented -> built, 8 live criteria owed (D1-D8 incl. piinnok full lifecycle)
