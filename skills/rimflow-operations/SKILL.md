---
name: rimflow-operations
description: Operate the multi-account Claude quota system - check each account's level (weekly vs 5-hour cap, percent left, reset time, MEASURED/ESTIMATE/UNMEASURED), apply the standard switching plan (owner's fixed priority steven > system > lukas, 1%/2% floors (never 0%), soft line then drain then hard stop, Steven's 52% leave line, pool pacing), switch or recover accounts with claude-account, and stand windows down and up. Use whenever anyone asks how much quota/usage is left, which account is live, when an account resets, whether to switch accounts, why the fleet stopped or went DARK, how to recover a stuck switch, or touches account_usage.py, account_live.py, switching_plan.py, slot_allocator set/clear, account-plan.timer, or timers_guard pause - even if they just say "are we about to run out".
---

# rimflow-operations: accounts, levels and the standard switching plan

One machine (Archmagi) uses ONE Claude account at a time; a switch closes every Claude window and
relaunches the Fleet. Three accounts are in play: `system`, `lukas`, `steven` (Steven's is lent: see
below). The plan decides which one burns; the meter says how much each has. Rules are data
(`src/RimMandrake/Utils/switching_plan.json`, each with provenance); reset times are never
written down, always read from the meter.

## 1. Check an account's level (read-only, safe anywhere)

```
python3 src/RimMandrake/Utils/account_usage.py now          # one line per account
python3 src/RimMandrake/Utils/account_usage.py now --json   # + pct_left, hours_to_reset, age, stale
python3 src/RimMandrake/Utils/switching_plan.py status      # what the next plan pass would do, pool, notice
~/.local/bin/claude-account --json status                   # which account is LIVE (parse the whole output)
```
Read each line as: **week** % left and its reset (the binding cap: it expires and refills at the
reset), **session** = the 5-hour cap (resets within hours, rarely the limit), and the label:
MEASURED (first-party `/usage`, no model call), ESTIMATE (last MEASURED carried forward; a lower
bound on usage, and blind), UNMEASURED (nothing to carry, or its window reset). A figure is only
as good as its `measured` age: `stale` means do not act on it. Dormant accounts are read from their
vault only while the token has 15+ min left (probing never refreshes a token); a live account's
vault copy is never run. Details, properties per account, Steven's window: `references/accounts.md`.

More traps for this section: [references/traps.md](references/traps.md) § 1. Check an account's level (read-only, safe anywhere).

## 2. The standard switching plan (rulings and provenance)

| Rule | Source |
|---|---|
| **Fixed priority** `order` = steven, system, lukas: burn the FIRST account in that list that is measured, fresh, inside its window and above its line. When system resets the machine goes to system even if lukas still has budget (a lower account's budget that expires first is given up) | owner's 10:15 words; the 10:58 soonest-expiry rule was reverted on his 15:20 review ("awkward") |
| Steven: use only inside 48 h after his reset, **leave at 52% left** (his "50%" plus a 2-point overshoot margin) | owner words 2026-10-27 "up to 50% after a fresh reset only"; 52 by card 10:20; 48 h is our reading (delegated) |
| Steven's account, late in his week: may be drawn down toward **10% left, never below**; the 50% use is done early in the week, then left alone | owner, 2026-10-26: *"As we get near his reset you may consider drawing it down towards 10%, but never beyond that. We don't ever want to crowd him out."* |
| Floors: **1%** when switching away, **2%** when waiting on an account (owner can still talk to a seat while idle). No account is driven to 0%. The meter reads whole percents (8,749 readings, none fractional), so 1% is the lowest line it can see | owner 2026-11-20: *"Actually 0.1% is even ok kept. We just don't want to crash to zero and get stuck."*, then *"Agreed for 1% at the moment"*; 2% delegated |
| **Soft line** (line + 2%): no new start (allocator gives 0 new helpers; `detached_helper.launch` refuses a new run). **Live runs finish**: at the line the switch or stop waits while a detached run is live, and goes when they end or at the **hard line** = max(1%, line - 2%) (steven: 50%) | card 10:20 "Soft line, then hard stop"; owner 2026-11-20: *"And yes for live runs finish past, absolutely."* |
| A switch the priority pulls (above the line) also waits for live runs, at most `pull_drain_max_s` (2 h) | owner 2026-11-20, as above; page `design/specs/2026-11-20-account-drain/boundary.md` |
| **Do not stop runs or switch by hand at the soft line.** The 2026-11-18 6:43 PM hand stop and 6:59 PM hand switch (steven at 55%) killed 9 runs, and their resumes missed the cache: 4.73M weighted | the 2026-11-20 scan, `design/specs/2026-11-20-context-kept-not-reloaded/report.md` §1 row 3 |
| **Blind meter = 0%**: once the last MEASURED reading is <= 1%, a blind one (failed /usage, limit error, ESTIMATE, stale) counts as 0% and switches | relayed rule 11:2x |
| **Pool pacing**: pace the whole pool "BECAUSE it spreads out the human review time cleanly to inform the process in a timely manner" | by card 10:20 |

The engine (`switching_plan.py check`, `account-plan.timer`, every 5 min) polls the meter itself near a line or
when a reading is old and acts once per transition (markers). Its ONLY brake is a `HOLD` file in its output dir
(`D:\ClaudeWork\rimmandrake\switching_plan\HOLD`): while it exists every pass logs `passive` and acts on nothing.
His 2026-10-28 pause (HOLD set, timer stopped) was lifted (`HOLD.lifted-2026-11-05`, `HOLD.lifted-2026-11-06` in that
dir); the timer runs. Full state machine, markers and the review history: `references/plan.md`.

**Why the switch must wait for live runs.** The switch is local: `claude-account` renames a credential file,
spends no model tokens and uses no network or Tailscale. But it stops every Claude process on the machine, so a run
cannot go on with the old account after it; a killed run resumed on the next account loses its prompt cache. At 0%
every window and helper on that account errors and the owner cannot talk to a seat, so no account goes under 1%.

More traps for this section: [references/traps.md](references/traps.md) § 2. The standard switching plan (rulings and provenance).

## 3. Switching by hand

```
claude-account arm --confirm archmagi
claude-account use <acct> --confirm archmagi     # --dry-run refuses while DISARMED
claude-account disarm
claude-account fleet-stop | fleet-start          # the two halves, e.g. a hard stop
```
It refuses to run inside a Claude window (the switch kills them) and refuses while DISARMED;
the engine arms, switches, disarms in one pass. Prefer `systemd-run` from a script, never a
shell a window owns. Nothing else should call `use`; if the plan owns the machine, change the plan
or write a `HOLD`, do not fight it.

## 4. Recovery when a switch sticks (needs no Claude)

A switch killed mid-way (timeout, SIGKILL) leaves `~/.claude-accounts/journal.json`; every later
`use` refuses with "interrupted switch; run recover". From the **Mac laptop**, over Tailscale SSH to Archmagi:
```
claude-account recover
claude-account arm --confirm archmagi
claude-account use <acct> --confirm archmagi      # then disarm
```
Check `claude-account --json status` for the live account first. No Claude session is needed
anywhere in this path.

More traps for this section: [references/traps.md](references/traps.md) § 4. Recovery when a switch sticks (needs no Claude).

## 5. Stand-down / stand-up costs (why switches are not free)

- Every window and helper on the machine is killed; unpublished work dies. **Publish at every green
  point** and write the handoff BEFORE a switch. The plan waits for detached runs to end (the drain), but a hard
  line, a failed switch or a hand switch still kills them.
- Remote Control sessions are likely dropped and need re-attaching (UNMEASURED; see skill
  `claude-remote-control`).
- Vault freshness: a stale vault cannot be probed or switched to. `account_usage.py` warms an expired DORMANT login
  itself (at most once per hour per account, under claude-account's own lock, refused if that login is live here or on
  any remote). `claude-account-warm.timer` is retired on Archmagi (`selftest_timer_prune.py` RETIRED).
- A warm or a refresh never extends a login. Each sign-in has a fixed deadline (`refreshTokenExpiresAt`, about 30 days),
  and the CLI keeps the earlier deadline on every refresh. Only a new sign-in moves it. login_watch warns 3 days before
  (`login:deadline:<account>:<epoch>`, page `design/specs/2026-11-22-login-deadline-forewarning/boundary.md`).
- The relaunched Fleet comes up on the new account; check `slot_allocator now` before assuming capacity.

More traps for this section: [references/traps.md](references/traps.md) § 5. Stand-down / stand-up costs (why switches are not free).

## 6. Throttles and timers

- Allocator override: `slot_allocator.py set --mode DARK` (every seat 0) / `set --n N --hours H`, `clear`.
  `--n 0` did not stop the retired FOUNDRY seat; DARK stops every seat. A DARK left behind after a reset strands the fresh
  week: lift it when the escape condition changes.
- Pausing timers: only `timers_guard.py pause --hours H --all|TIMER` (it arms the restart first,
  then stops). A bare `systemctl stop` of rm-*/testq-* timers on 2026-10-28 05:04 killed every no-LLM lane
  and the watchdogs until 09:41. `account-plan` is deliberately outside that glob.

- Test spend is throttled by policy, not by hand: `design/RimMandrake/testing_policy_2026-10-28.md` (tunables
  `src/RimMandrake/rimflow/testing_policy.json`, reader `testing_policy.py`). Mutation runs (`run_mutation.py`,
  mutmut on SteveDesktop; gate enforced in code): testing_policy_2026-10-28.md §2.6. Nightly sweep: §2.3. testq
  lanes and filler hours: §2.7. Which test for which code: §4. Only D/A tunables may be moved by an agent: §0.

More traps for this section: [references/traps.md](references/traps.md) § 6. Throttles and timers.

## 7. Traps

- Never parse a tail-truncated command output: `claude-account --json status` is ~2000 chars and a
  `[-2000:]` tail lost the opening brace, so the live account read as None forever. Parse the whole stdout.
- The dormant-account tie: two accounts read the same newest time; do not take the first dict key.
  `pick_burn_account` prefers the "live login" method, and `claude-account status` is the authority.
- A DARK soft line is right while there is nowhere to go and wrong once a fresh account exists.
- `use` timing out at 600 s mid-switch leaves the journal: recover (section 4).
- Selftests stub the CLI; the real call needs probing once. More: `references/traps.md`.

More traps for this section: [references/traps.md](references/traps.md) § 7. Traps.
