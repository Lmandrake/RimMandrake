---
name: rimflow-operations
description: Operate the multi-account Claude quota system - check each account's level (weekly vs 5-hour cap, percent left, reset time, MEASURED/ESTIMATE/UNMEASURED), apply the standard switching plan (owner's fixed priority steven > system > lukas, 0%/2% floors, soft line then hard stop, Steven's 52% leave line, pool pacing), switch or recover accounts with claude-account, and stand windows down and up. Use whenever anyone asks how much quota/usage is left, which account is live, when an account resets, whether to switch accounts, why the fleet stopped or went DARK, how to recover a stuck switch, or touches account_usage.py, switching_plan.py, account_failover.py, slot_allocator set/clear, account-plan.timer, or timers_guard pause - even if they just say "are we about to run out".
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

## 2. The standard switching plan (rulings and provenance)

| Rule | Source |
|---|---|
| **Fixed priority** `order` = steven, system, lukas: burn the FIRST account in that list that is measured, fresh, inside its window and above its line. When system resets the machine goes to system even if lukas still has budget (a lower account's budget that expires first is given up) | owner's 10:15 words; the 10:58 soonest-expiry rule was reverted on his 15:20 review ("awkward") |
| Steven: use only inside 48 h after his reset, **leave at 52% left** (his "50%" plus a 2-point overshoot margin) | owner words 2026-10-27 "up to 50% after a fresh reset only"; 52 by card 10:20; 48 h is our reading (delegated) |
| Floors: **0%** when switching away, **2%** when waiting on an account (owner can still talk to a seat while idle) | card 2026-10-28 15:33 "Drain to 0%"; 2% delegated |
| **Soft line** (line + 2%: allocator gives 0 new helpers, running seats publish and finish) then **hard stop** (fleet-stop) | by card 10:20 |
| **Blind meter = 0%**: once the last MEASURED reading is <= 1%, a blind one (failed /usage, limit error, ESTIMATE, stale) counts as 0% and switches | relayed rule 11:2x |
| **Pool pacing**: pace the whole pool "BECAUSE it spreads out the human review time cleanly to inform the process in a timely manner" | by card 10:20 |

The engine (`switching_plan.py check`, `account-plan.timer`, every 5 min) polls the meter itself near a line or
when a reading is old and acts once per transition (markers). Its ONLY brake is a `HOLD` file in its output dir
(`D:\ClaudeWork\rimmandrake\switching_plan\HOLD`): while it exists every pass logs `passive` and acts on nothing.
(The old account_failover gate was removed 2026-10-28; that script and its timer are retired.)
**Owner pause, 2026-10-28 14:14 PDT:** "disable any script that will auto log me out for awhile and stay on this
account" - HOLD is set and `account-plan.timer` is stopped and disabled. Remove HOLD or re-enable the timer only on
his word. Full state machine, markers and the review history: `references/plan.md`.

**Why switching at 0% is safe.** The switch is local: `claude-account` renames a credential file,
spends no model tokens and uses no network or Tailscale. Hitting 0% locks nobody out of the
switcher. What breaks at 0%: every window and helper on that account errors, and the owner cannot
talk to a seat until the switch lands. Hence waiting accounts keep 2%, leaving accounts burn to 0.

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

## 5. Stand-down / stand-up costs (why switches are not free)

- Every window and helper on the machine is killed; unpublished work dies. **Publish at every green
  point** and write the handoff BEFORE a switch (the soft line exists to give time for this).
- Remote Control sessions are likely dropped and need re-attaching (UNMEASURED; see skill
  `claude-remote-control`).
- Vault freshness: a stale vault cannot be probed or switched to. `account_usage.py` warms an expired DORMANT login
  itself (at most once per hour per account, under claude-account's own lock, refused if that login is live here or on
  any remote); `claude-account-warm.timer` (daily) is separate and still warms every account (WARMTIMER_HARDEN_SPARE_LIVE).
- The relaunched Fleet comes up on the new account; check `slot_allocator now` before assuming capacity.

## 6. Throttles and timers

- Allocator override: `slot_allocator.py set --mode DARK` (every seat 0) / `set --n N --hours H`, `clear`.
  `--n 0` does NOT stop the FOUNDRY seat; use DARK. A DARK left behind after a reset strands the fresh
  week: lift it when the escape condition changes.
- Pausing timers: only `timers_guard.py pause --hours H --all|TIMER` (it arms the restart first,
  then stops). A bare `systemctl stop` of rm-*/testq-* timers on 2026-10-28 05:04 killed every no-LLM lane
  and the watchdogs until 09:41. `account-plan` is deliberately outside that glob.

## 7. Traps

- Never parse a tail-truncated command output: `claude-account --json status` is ~2000 chars and a
  `[-2000:]` tail lost the opening brace, so the live account read as None forever. Parse the whole stdout.
- The dormant-account tie: two accounts read the same newest time; do not take the first dict key.
  `pick_burn_account` prefers the "live login" method, and `claude-account status` is the authority.
- A DARK soft line is right while there is nowhere to go and wrong once a fresh account exists.
- `use` timing out at 600 s mid-switch leaves the journal: recover (section 4).
- Selftests stub the CLI; the real call needs probing once. More: `references/traps.md`.
