---
name: rimflow-operations
description: Operate the multi-account Claude quota system - check each account's level (weekly vs 5-hour cap, percent left, reset time, MEASURED/ESTIMATE/UNMEASURED), read and command the account plan with ./acct (status, next, forecast, can-use, hold, switch, line, pin, order, undo), run an account end, handle a second machine on the same account, switch or recover accounts with claude-account, and stand windows down and up. Use whenever anyone asks how much quota/usage is left, which account is live, when an account resets, whether to switch accounts, why a launch was refused by the ACCOUNT GATE, why the fleet stopped or went DARK, how to recover a stuck switch, or touches ./acct, account_plan.py, account_usage.py, account_live.py, slot_allocator set/clear, account-plan.timer, or timers_guard pause - even if they just say "are we about to run out".
---

# rimflow-operations: accounts, levels and the account plan

One machine uses ONE Claude account at a time. A switch closes every Claude window on that machine and relaunches the
Fleet. The Fleet is the set of Claude windows that `~/.claude-accounts/machine.json` names. The accounts are in the
plan (`./acct plan`). One of them is lent (`references/accounts.md`).

The plan decides which account burns. The meter (`account_usage.py`, which reads each account's `/usage` figures)
says how much each account has. Every rule is a field of ONE file,
`~/.local/state/rimmandrake/account_plan/plan.json`, which only `./acct` writes. A write binds at the next read, with no
commit, publish or pull. No rule is in this skill: a line, a floor, an order or a percent that you read here would be
a copy, and the copy would be wrong after the next command. Reset times are never written down. Read a reset time from
the meter. Incident records: `references/history.md`.

## 1. Check an account's level (read-only, safe anywhere)

```
./acct status                                               # now and next, the end of the live account, every account as LEFT
./acct readings                                             # each account: left, reset in Pacific time, age, source
python3 src/RimMandrake/Utils/account_usage.py now          # the meter itself, one line per account
python3 src/RimMandrake/Utils/account_usage.py now --json   # + pct_left, hours_to_reset, age, stale
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
  - UNMEASURED: there is no figure to carry, or the account's week (or its 5-hour session) reset since the last
    MEASURED figure.
- A figure is only as good as the age of its `measured` time. `stale` means: do not act on the figure.

A dormant account is an account that is not live. A dormant account is read from its vault, the folder that holds its
saved login. The probe reads the vault only while the token has 15+ min left. So a probe never refreshes a token. When
the token has less time left, `account_usage.py` warms the login first (§5). The vault copy of a live account is never run.
Details and the properties of each account: `references/accounts.md`.

More traps for this section: [references/traps.md](references/traps.md) § 1. Check an account's level (read-only, safe anywhere).

## 2. The account plan: `./acct`

**`./acct --help` is the operator's page, and `./acct status` prints the end of the live account with the numbers and
the names in force. Those two are enough to run an account end.** This section says only what they cannot.

| You want | Command |
|---|---|
| what happens now, next, and at the end of the live account | `./acct status` |
| one line for the next pass | `./acct next` |
| the week ahead: each switch, each reset, the points a reset erases | `./acct forecast` |
| may a new run start here now | `./acct can-use` (exit 0 yes, 1 no, 2 could not look) |
| may a Codex job be sent | `./acct can-use codex` |
| the rules themselves | `./acct plan` |
| stop every automatic act for a time | `./acct hold --for 2h` (`./acct release`) |
| go to an account | `./acct switch <account>` (`--now`: at the next pass) |
| another leave line until a reset | `./acct line <account> <percent> --until-reset` |
| keep the live account | `./acct pin --for 6h` |
| which account is next | `./acct order <a> <b> <c>` |
| try a change before you make it | `./acct whatif -- <a write>` |
| take a change back | `./acct undo [REV]` (each write prints its undo) |
| what the last weeks cost | `./acct measures` |

How the plan decides (the page of promises: `design/specs/2026-11-24-account-plan-one-file/boundary.md`):

- The live account stays live until its own line. The order of the steps answers one question: which account is next.
- A switch that rescues allowance from a reset must be worth a switch. The reason line of `./acct next` gives the count.
- Between the warning line and the line the runs are warned and keep working, and new runs start. At the line no new
  run starts, each live run is told to save and end, and the switch goes when the last one ends.
- A switch that a person made (by hand, or with `./acct switch`) is kept until that account is finished.
- Unknown never gives permission. A level that is not measured makes no account a target.

What reads the plan:

- **The timed pass** (`account-plan.timer`, each 5 min, `account_plan.py pass`). The timed pass makes the switch through the
  account-end actuator (`switching_plan._check`, `account_end.py`): the warning, the save order, the pause, the switch.
  Its log is `~/.local/state/rimmandrake/account_plan/log.jsonl`; `journalctl --user -u account-plan.service` has each pass.
- **Every launcher** of a detached run (`detached_helper.drain_refusal`). A refusal starts `refused: ACCOUNT GATE`. The
  pipeline reads it as a wait, not a fault, and launches the same thing again after the switch.
- **Codex's door** (`codex_advice.gate`, which `gpt_consult.py` passes). At Codex's line every job is refused, exit 4.
- **The helper allocator** (`slot_allocator.py`): Burn Mode (`./acct burn-mode`), the pool and its Codex advice line.
- **Another machine on the same account** (`./acct plan` lists the machines). Each timed pass writes that machine
  its notice. That machine starts no new run at the line. That machine also starts no new run when its last notice is
  over 20 min old (COULD NOT LOOK). The tool never switches another machine: the switch of another machine is a hand
  act, and `./acct status` prints the command.

An interactive Claude window (a seat's terminal session) has no stop hook. The signs for such a window are the notice (`./acct can-use`), the Conductor log lines `ACCOUNT END` and the
ledger notes on `RIMMANDRAKE_BUILD_ACCOUNT_END_WARN_SAVE_PAUSE_SWITCH_SIZED_BY_BURN`. No program refuses a new helper
inside an interactive Claude window.

**Do not stop runs or switch by hand at the warning.** The hand stop and the hand switch of 2026-11-18 killed 9 runs,
and their resumes missed the prompt cache (`design/specs/2026-11-20-context-kept-not-reloaded/report.md` §1 row 3).

**Why the switch waits for live runs.** The switch is local. `claude-account` renames a credential file. The rename
spends no model tokens and uses no network. But the switch stops every Claude process on the machine. A killed run
that is resumed on the next account loses its prompt cache. At 0%, every window and helper on that account errors, and
the owner cannot talk to a seat. So no Claude account's line is under the plan's floor (`numbers.floor_pct`, which `./acct plan` prints).

The old engine is the decision half of the `switching_plan` module, with its rule file `switching_plan.json`. The old
engine decides only when `./acct driver` reads `old`, or while the plan file is refused; the timed pass then says so.
The other half of the `switching_plan` module is the account-end actuator, which the timed pass drives.

More traps for this section: [references/traps.md](references/traps.md) § 2. The account plan.

## 3. Switching by hand

```
claude-account arm --confirm archmagi
claude-account use <acct> --confirm archmagi     # --dry-run refuses while DISARMED
claude-account disarm
claude-account fleet-stop | fleet-start          # the two halves, e.g. a hard stop
```

- `claude-account use` refuses to run inside a Claude window, because the switch kills that window. `use` also refuses
  while the machine is DISARMED. `fleet-stop` and `fleet-start` refuse in the same two cases.
- The timed pass arms, switches and disarms in one pass. If the machine was armed before the pass, it stays armed.
- From a script, prefer `systemd-run`. Never use a shell that a window owns.
- Let nothing else call `use`. The one exception is `login_watch.py`, when a login dies.
- The plan owns the machine. To go to an account, ask the plan: `./acct switch <account> --now`. To stop it:
  `./acct hold --for 2h`. A switch made with `claude-account use` is a hand switch: the plan keeps that account until
  it is finished.
- Another machine is switched by hand: `ssh -t <its ssh name> claude-account-switch <machine> <account>`.

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
- An allocator override of DARK (`slot_allocator.py set --mode DARK`: every seat at 0 helpers) is right while no
  account can take over, and wrong once a fresh account exists. A drain at the line ends when the last run has ended,
  so a drain that stops all work cannot strand the account.
- If `use` times out at 600 s mid-switch, the journal stays. Recover (§4).
- Selftests stub the CLI. So probe the real call once. More: `references/traps.md`.

More traps for this section: [references/traps.md](references/traps.md) § 7. Traps.
