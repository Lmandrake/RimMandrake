# RIMMANDRAKE_FIX_SLOT_SET_WORDS_KEEP_OWN_SEAT_TIME

## spec
Split from `RIMMANDRAKE_FIX_SLOT_ALLOCATOR_OVERRIDE_AND_BURN_PICK` (findings 3, 4, 5), each red on 85888f7897.
`slot_allocator.py set`: (3) `set --n 6` then `set --seat RELENTLESS --n 1` copies only the prior `seats`, so the unseated
count (BENCH's) is lost: BENCH read 0, not 6; (4) seats kept from the prior word take the new word's `until`, so BENCH's
1 h word lasted the RELENTLESS word's 4 h; (5) `if a.hours:` read `--hours 0` as omitted, so it lasted to the weekly
reset. Fix: a seat word folds the prior unseated n in as BENCH; each kept seat keeps its own until (`seat_until`),
which `_override_live` honours (the file's until is the latest of them); `--hours 0` is now.

## refs
file: src/RimMandrake/Utils/slot_allocator.py
file: src/RimMandrake/Utils/selftest_slot_allocator_v3.py

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_slot_allocator_v3.py` exits 0, its F3, F4 and F5 lines PASS. Watched red on base 85888f7897 (F3, F4, F5 FAIL).

## criteria
- F3: BENCH keeps 6 after a later RELENTLESS seat word; F4: BENCH's word ends at its own hour, RELENTLESS's holds;
- F5: `--hours 0` is not live a second later.

## review
Codex full-file review of the fix (`D:\ClaudeWork\rimmandrake\scratch\slot_allocator_override_review_20261118\codex_review.md`) found two more, each tested red and fixed in the same sha: a legacy `CONDUCTOR` seat key survived beside a new BENCH word and revived when it lapsed (keys now fold to their seat); a lapsed seat left its newer `set_at` on the override, so a kept older word beat a switching notice (each seat keeps `seat_set_at`, and `_override_live` resets `set_at` to the kept words').
