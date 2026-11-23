# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only records and lines that are no longer true. Git holds the rest.
Each line below is a record, not a rule.

## The plan (§2)

- Until 2026-11-23 the table held this row: Steven's account, late in his week, "may be drawn down toward **10% left,
  never below**"; "the 50% use is done early in the week, then left alone". Its source was the owner, 2026-10-26: *"As we
  get near his reset you may consider drawing it down towards 10%, but never beyond that. We don't ever want to crowd him
  out."* His words of 2026-10-27, "Dispatcher can use Steve up to 50% after a fresh reset only.", narrowed that rule
  (`src/RimMandrake/Utils/slot_rules.json`, `lent_accounts`). The engine never used the 10% rule. `slot_allocator.py plan`
  still checks a draw against a 10% safety floor, which is an agent proposal.
- Until 2026-11-23 the soft line row said that the allocator gives 0 new helpers and that `detached_helper.launch` refuses
  a new run. Token pacing became advisory on 2026-11-02, so the allocator only reports that 0. The launch refuses only
  during a drain.
- The owner's pause of 2026-10-28 (HOLD set, timer stopped) was lifted (`HOLD.lifted-2026-11-05`,
  `HOLD.lifted-2026-11-06` in the output dir). The timer runs.
- The rule "Blind meter = 0%" has the source "relayed rule 11:2x": the coordinator of 2026-10-28.

## Recovery (§4)

- Until 2026-11-23 the text quoted the refusal as "interrupted switch; run recover".

## Vaults (§5)

- Until 2026-11-23 the text said that a stale vault cannot be probed or switched to. Of the vault checks,
  `claude-account use` refuses a missing login, a login past its sign-in deadline, and a wrong email. `use` does not check
  the age of the access token.
