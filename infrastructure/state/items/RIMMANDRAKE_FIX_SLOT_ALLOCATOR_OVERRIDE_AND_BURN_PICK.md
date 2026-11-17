# RIMMANDRAKE_FIX_SLOT_ALLOCATOR_OVERRIDE_AND_BURN_PICK

## spec
Codex full-file review 2026-11-17 of `src/RimMandrake/Utils/slot_allocator.py` (two halves, lines 1-759 and 760-1519;
raw `/mnt/d/ClaudeWork/rimmandrake/conductor/cr/r2a.txt`, `r2b.txt`). Each read by Opus against the code: real as stated
unless marked. Not fixed at filing.
1. (med) `pick_burn_account` ~l.421-427: when `live_login_name()` names an account with no MEASURED reading on this
   machine yet, falls to the newest other reading, so the allocator paces on the previous account's quota. The code
   comment calls it deliberate; decide whether to return "unknown" for a positively named but unmeasured login.
2. (med) `mean_helpers` l.216-229: counts first-record to last-write, so a resumed transcript's idle gap counts as
   running time (one helper writing a minute at each end of a 6 h window reads ~1.0, not ~0.006). `helper_spans`
   (l.232) already cuts at gaps; `gather` l.708 still uses `mean_helpers` for `inp["mean_helpers"]`.
3. (med) `set` ~l.1503: `set --n 6` (no --seat) stores `ov["n"]`; a later `set --seat X --n k` copies only
   `prior["seats"]`, so the unseated BENCH count is lost (BENCH drops to its base).
4. (med) `set` ~l.1499: seats kept from the prior override inherit the new override's `until`, so a lapsing word is
   extended by an unrelated later `set` (4 helpers until 12:00, set at 11:00 with --hours 4 -> BENCH keeps 4 until 15:00).
5. (low) `set` ~l.1485 `if a.hours:` treats `--hours 0` as omitted (validation allows 0), so it lasts to the weekly
   reset instead of expiring immediately.
Acceptance: a selftest case per finding in selftest_slot_allocator_v3.py that fails on base before the fix.

## refs
file: src/RimMandrake/Utils/slot_allocator.py

## criteria
- Each finding has a selftest case that failed on base and passes after (finding 1 may be ruled intended and closed with the reason).

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_slot_allocator selftest_slot_allocator_v3
