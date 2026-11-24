---
name: rimflow-operations
description: Operate the multi-account Claude quota system - check each account's level (weekly vs 5-hour cap, percent left, reset time, MEASURED/ESTIMATE/UNMEASURED), apply the standard switching plan (owner's fixed priority steven > system > lukas, 1%/2% floors (never 0%), the save warning at 2% or 3%, the emergency order and sized pause at 1%, Steven's 52% leave line, pool pacing), switch or recover accounts with claude-account, and stand windows down and up. Use whenever anyone asks how much quota/usage is left, which account is live, when an account resets, whether to switch accounts, why the fleet stopped or went DARK, how to recover a stuck switch, or touches account_usage.py, account_live.py, switching_plan.py, slot_allocator set/clear, account-plan.timer, or timers_guard pause - even if they just say "are we about to run out".
---

# rimflow-operations: accounts, levels and the standard switching plan

One machine (Archmagi) uses ONE Claude account at a time. A switch closes every Claude window and relaunches the Fleet.
The Fleet is the set of Claude windows that `~/.claude-accounts/machine.json` names. Three accounts are in play:
`system`, `lukas` and `steven`. Steven's account is lent (§2 and `references/accounts.md`).

The plan decides which account burns. The meter says how much each account has. The rules are data, each with its
provenance: `src/RimMandrake/Utils/switching_plan.json`. Reset times are never written down. Always read a reset time
from the meter. Old lines and incident records: `references/history.md`.

## 1. Check an account's level (read-only, safe anywhere)

```
python3 src/RimMandrake/Utils/account_usage.py now          # one line per account
python3 src/RimMandrake/Utils/account_usage.py now --json   # + pct_left, hours_to_reset, age, stale
python3 src/RimMandrake/Utils/switching_plan.py status      # what the next plan pass would do, pool, notice
~/.local/bin/claude-account --json status                   # which account is LIVE (parse the whole output)
```

How to read each line of `account_usage.py now`:

- **week**: the percent left of the week, and the week's reset. The week is the binding cap. At the reset, what is left
  expires and the cap refills.
- **session**: the 5-hour cap. The session resets within hours and is rarely the limit.
- The label says where the figure comes from:
  - MEASURED: the first-party `/usage` command read the account. `/usage` makes no model call.
  - ESTIMATE: the last MEASURED figure, carried forward. The figure is a lower bound on usage. An ESTIMATE is blind: it
    does not see what was spent since.
  - UNMEASURED: there is no figure to carry, or the account's window reset since the last one.
- A figure is only as good as the age of its `measured` time. `stale` means: do not act on the figure.

A dormant account is an account that is not live. A dormant account is read from its vault, the folder that holds its
saved login. The probe reads the vault only while the token has 15+ min left. So a probe never refreshes a token. When
the token has less time left, `account_usage.py` warms the login first (§5). The vault copy of a live account is never run.
Details, the properties of each account, and Steven's window: `references/accounts.md`.

More traps for this section: [references/traps.md](references/traps.md) § 1. Check an account's level (read-only, safe anywhere).

## 2. The standard switching plan (rulings and provenance)

- An account's **line** is the percent left at which the machine leaves the account. Steven's line is his leave line.
  The line of `system` or `lukas` is a floor.
- The **warning line** is the percent left at which the account starts to end. The warning line is max(line, 2%), and
  one point more when the burn is fast or cannot be read.
- The **emergency line** is 1%. Only an account with a line of 10% or less has an emergency step.
- A live run is an active detached run (an `rm-detached-*` unit). If the live runs cannot be read, they count as live.
- A dated exception in `switching_plan.json` can replace the order, an account's line or its window, for at most 7 days.
  `switching_plan.py status` names the exception in force. While an exception stands, obey the values that it sets.
  The rest of the table stands.

| Rule | Source |
|---|---|
| **Fixed priority** `order` = steven, system, lukas. Burn the FIRST account in that list that is measured, fresh, inside its window and above its line. When system resets, the machine goes to system even if lukas still has budget. A lower account's budget that expires first is given up. | the owner's 10:15 words of 2026-10-28. The soonest-expiry rule of 10:58 was reverted on his 15:20 review ("awkward"). |
| Steven: use his account only inside 48 h after his reset. **Leave at 52% left** (his "50%" plus a 2-point overshoot margin) | owner words 2026-10-27 "up to 50% after a fresh reset only". The 52 is by card 10:20. The 48 h is our reading (delegated). |
| Steven, outside those 48 h: leave his account alone. Never crowd him out. | owner 2026-10-27, the row above. It narrows his 2026-10-26 words about 10% left late in the week (`references/history.md`). |
| Floors: **1%** when the machine switches away, **2%** when the machine waits on an account. With 2% left, the owner can still talk to a seat while the machine is idle. No account is driven to 0%. The meter reads whole percents (8,749 readings, none fractional). So 1% is the lowest line that the meter can see. | owner 2026-11-20: *"Actually 0.1% is even ok kept. We just don't want to crash to zero and get stuck."*, then *"Agreed for 1% at the moment"*. The 2% is delegated. |
| **No share is kept for his evenings.** Each account runs to its line, at any hour. | owner, card 2026-11-23 8:57 AM PST: *"No, run to the line"* (`standing_rulings.md` §Account and capacity budget) |
| **Soft line** (line + 2%): a notice. Land your commits with `./publish`, and start no new subagent inside an interactive window. A new detached run still starts. | card 10:20 "Soft line, then hard stop" |
| **Save warning**, at the warning line (2%; 3% when the burn is over 0.1% a minute, stale or unread): no new work starts on the account: a new run, a continuation and a resume are refused. Each live run gets a stop order: wrap it up cleanly and safely save your work. The order says the percent left, the burn rate and the minutes left. | owner 2026-11-24: *"At 2% no new work is started and "wrap it up cleanly and safely save your work" is sent to everyone."* Card: *"up at 3% as well if the burn is going crazy fast ... TELL THE PROCESSES these numbers."* |
| **Switch when the work has ended**: after the warning the switch goes as soon as the last live run has ended. The switch does not wait for 1%. | owner 2026-11-24: *"I agree with your switch when the last live run has ended when <2% remains."* |
| **Emergency**, at 1% with a run live: each live run gets the order to record its state at once. The order says the seconds of the pause. Then the machine pauses: a fifth of the time from 0.5% to zero at the burn rate, 20 s to 180 s (20 s when the reading is stale). Then the switch goes and stops every Claude process. Nothing is killed by hand. | owner 2026-11-24: *"Give it a beat... don't just kill at 1%."* Card "Sized from the burn rate" |
| **An account kept well above zero** (Steven at 52%) gets the warning and the switch at the end of the last run. It gets no emergency. | owner 2026-11-24: *"does not need the emergency kill at all"* |
| **The last account** gets the same two orders. Then the machine stops at the account's line, and a reset starts it again. | owner 2026-11-24: *"wait for a reset if it's the last account"* |
| A priority switch is a switch to an account that comes earlier in `order`, made above the live account's line. A priority switch also waits for live runs, at most `pull_drain_max_s` (2 h). | owner 2026-11-20, the same words as the soft line row; page `design/specs/2026-11-20-account-drain/boundary.md` |
| **Do not stop runs or switch by hand at the soft line or at the warning.** The hand stop of 2026-11-18 6:43 PM and the hand switch of 6:59 PM (steven at 55%) killed 9 runs. Their resumes missed the prompt cache: 4.73M weighted. | the 2026-11-20 scan, `design/specs/2026-11-20-context-kept-not-reloaded/report.md` §1 row 3 |
| **Blind meter = 0%**: the last MEASURED reading is <= 1%, and the meter is now blind (a failed /usage, a limit error, an ESTIMATE or a stale reading). Then the account counts as 0%, and the machine switches. | the rule relayed on 2026-10-28 at 11:2x |
| **Pool pacing**: pace the whole pool "BECAUSE it spreads out the human review time cleanly to inform the process in a timely manner". | by card 10:20 |

What enforces the soft line and the save warning today:

- `switching_plan.py status` shows when the plan is soft. Either the `do` of `next_pass` is `soft`, or the `notice` has
  `state` `soft` and an `at` time under 20 min old. Then land your commits with `./publish`, and start no
  new subagent inside an interactive window (a switch kills it and does not wait for it). The plan is also soft in the 20 min before a reset that will pull the machine to another account.
- `status` also shows `account_end`: the burn, the warning line, the pause and the episode (who was ordered, and when).
  `account_end.py burn [ACCOUNT]` shows the sizes of one account.
- While the plan drains (its notice reads `soft` with `drain` true), `detached_helper.launch` refuses a new run. With
  `account_end` true it refuses a continuation and a resume too. A continuation that waited starts after the switch
  (`left_open_continue.kick_waiting`). A notice that is unreadable or over 20 min old refuses nothing.
- The orders are stop orders of the control store, for the detached and role runs. A run hears an order after its tool
  call in hand ends. The orders write no OFF switch and void no run. A run that ends on an order writes a note that
  starts `LEFT OPEN:`, and that note carries its work on.
- A window has no stop hook. Its signs are the notice, the Conductor log lines `ACCOUNT END` and the ledger notes on
  `RIMMANDRAKE_BUILD_ACCOUNT_END_WARN_SAVE_PAUSE_SWITCH_SIZED_BY_BURN`.
- No program refuses a new helper inside a window. The allocator reports 0 new helpers, but does not apply that count
  while `advisory.enabled` is true in `slot_rules.json`.
- While an account ends, the pass reads the meter and repeats each minute inside its 5-min beat.

The engine is `switching_plan.py check`. The timer `account-plan.timer` runs the engine every 5 min.

- Near a line, or when a reading is old, the engine polls the meter itself.
- The engine acts once per transition. A marker file records each transition.
- The engine does not undo a switch that the plan did not make. That account stays live until it is spent or until the next switch.
- The engine's ONLY brake is a `HOLD` file in its output dir (`D:\ClaudeWork\rimmandrake\switching_plan\HOLD`). While
  that file exists, every pass logs `passive` and acts on nothing.

Full state machine, markers and the review history: `references/plan.md`.

**Why the switch must wait for live runs.** The switch is local. `claude-account` renames a credential file. The rename
spends no model tokens and uses no network or Tailscale. But the switch stops every Claude process on the machine. So a
run cannot go on with the old account after the switch. A killed run that is resumed on the next account loses its
prompt cache. At 0%, every window and helper on that account errors, and the owner cannot talk to a seat. So no account
goes under 1%.

More traps for this section: [references/traps.md](references/traps.md) § 2. The standard switching plan (rulings and provenance).

## 3. Switching by hand

```
claude-account arm --confirm archmagi
claude-account use <acct> --confirm archmagi     # --dry-run refuses while DISARMED
claude-account disarm
claude-account fleet-stop | fleet-start          # the two halves, e.g. a hard stop
```

- `claude-account use` refuses to run inside a Claude window, because the switch kills that window. `use` also refuses
  while the machine is DISARMED. `fleet-stop` and `fleet-start` refuse in the same two cases.
- The engine arms, switches and disarms in one pass. If the machine was armed before the pass, the engine leaves it armed.
- From a script, prefer `systemd-run`. Never use a shell that a window owns.
- Let nothing else call `use`. The two exceptions are `login_watch.py`, when a login dies, and `account_handover.py`,
  for one change-over at a named line.
- If the plan owns the machine, change the plan or write a `HOLD` file. Do not fight the plan.

## 4. Recovery when a switch sticks (needs no Claude)

A switch that is killed mid-way (timeout, SIGKILL) leaves `~/.claude-accounts/journal.json`. Every later `use` then
refuses: "an earlier switch was interrupted; run `claude-account recover` first".

1. Work from the **Mac laptop**, over Tailscale SSH to Archmagi.
2. Read `claude-account --json status` first, to see which account is live.
3. Run:

```
claude-account recover
claude-account arm --confirm archmagi
claude-account use <acct> --confirm archmagi      # then disarm
```

No Claude session is needed anywhere in this path.

More traps for this section: [references/traps.md](references/traps.md) § 4. Recovery when a switch sticks (needs no Claude).

## 5. Stand-down / stand-up costs (why switches are not free)

- A switch kills every window and helper on the machine. Unpublished work dies. **Publish at every green point**: each
  time the checks of your work pass. Write the handoff file (the `handoff` skill) BEFORE a switch. The plan waits for
  detached runs to end (the drain). But the switch after the pause at 1%, a failed switch or a hand switch still kills
  them.
- A switch likely drops the Remote Control sessions, and they need a new attach (UNMEASURED; see the skill
  `claude-remote-control`).
- Vault freshness: a vault whose token has under 15 min left cannot be probed. `account_usage.py` warms such a DORMANT
  login itself, at most once per hour per account, under claude-account's own lock. The warm is refused if that login is
  live here or on any remote.
- `claude-account-warm.timer` is retired on Archmagi (`selftest_timer_prune.py` RETIRED).
- A warm or a refresh never extends a login. Each sign-in has a fixed deadline (`refreshTokenExpiresAt`, about 30 days).
  The CLI keeps the earlier deadline on every refresh. Only a new sign-in moves the deadline. After the deadline, `use`
  refuses that account.
- login_watch warns 3 days before the deadline (`login:deadline:<account>:<epoch>`, page
  `design/specs/2026-11-22-login-deadline-forewarning/boundary.md`).
- The relaunched Fleet comes up on the new account. Check `slot_allocator now` before you assume capacity.

More traps for this section: [references/traps.md](references/traps.md) § 5. Stand-down / stand-up costs (why switches are not free).

## 6. Throttles and timers

- Allocator override: `slot_allocator.py set --mode DARK` sets every seat to 0 helpers. `set --n N --hours H` sets a
  count, and `clear` ends the override.
  - `set` needs `--owner-said` with his exact words, or a Conductor instruction (`--per-ruling
    CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` with `--why`).
  - `--n` without `--seat` sets only the Conductor's seat. So `--n 0` did not stop the retired FOUNDRY seat. DARK stops
    every seat.
  - A DARK that is left behind after a reset strands the fresh week. Lift DARK when its reason ends, for example when a
    fresh account exists.
- To pause timers, use only `timers_guard.py pause --hours H --all|TIMER`. The pause arms the restart first, then stops
  the timers.
- Never stop the timers with a bare `systemctl stop`. A bare stop of rm-*/testq-* timers on 2026-10-28 05:04 killed
  every no-LLM lane and the watchdogs until 09:41. `account-plan` is deliberately outside that glob.
- Policy throttles test spend, not a hand: `design/RimMandrake/testing_policy_2026-10-28.md`. Its tunables are in
  `src/RimMandrake/rimflow/testing_policy.json`, and `testing_policy.py` reads them. In that policy:
  - mutation runs (`run_mutation.py`, mutmut on SteveDesktop; the gate is enforced in code): testing_policy_2026-10-28.md §2.6;
  - the nightly sweep: §2.3;
  - testq lanes and filler hours: §2.7;
  - which test for which code: §4;
  - which tunables an agent may move: §0. An agent may move only a tunable with the mark D or the mark A. Mark D is a code
    default that nobody ruled on. Mark A is an agent proposal.

More traps for this section: [references/traps.md](references/traps.md) § 6. Throttles and timers.

## 7. Traps

- Never parse a tail-truncated command output. `claude-account --json status` is ~2000 chars. A `[-2000:]` tail lost the
  opening brace, so the live account read as None forever. Parse the whole stdout.
- The dormant-account tie: two accounts can read the same newest time. Do not take the first dict key.
  `claude-account status` is the authority on which account is live. Without its answer, `pick_burn_account` prefers the
  "live login" method.
- A DARK soft line is right while there is nowhere to go. A DARK soft line is wrong once a fresh account exists. Since
  2026-11-24 the switch goes when the last run ends, so a drain that stops all work cannot strand the account.
- If `use` times out at 600 s mid-switch, the journal stays. Recover (§4).
- Selftests stub the CLI. So probe the real call once. More: `references/traps.md`.

More traps for this section: [references/traps.md](references/traps.md) § 7. Traps.
