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
- **Exact `/usage` with no model call.** `claude -p /usage --output-format json --no-session-persistence` (num_turns 0, cost 0) puts the session/week % used and reset lines of the interactive `/usage` in `.result`, for whatever login `CLAUDE_CONFIG_DIR` points at. Pair it with `claude auth status` in the same env to prove which login answered. Never run it against a dormant vault login whose access token is near expiry: Claude Code refreshes and rotates the credential under `claude-account`.
- **`switching_plan.py status` 'The week ahead at R %/h' is the POOL PACING rate** (budget left / hours to deadline: what the plan would like to spend), not the measured burn. Do not quote its times as a forecast. For a switch time, divide pct-to-line by the slope of `week_pct_used` in `/mnt/d/ClaudeWork/rimmandrake/account_usage/series.jsonl` (measured ~2.8%/h when the pacing said 6-7).

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
- **A switch plan that changes WHICH account the owner sits on must cite his words for each leg.** An agent revision ('use it or lose it', no owner quote) kept the fleet on lukas past a planned switch back to system, which refilled to 100% while lukas burned nothing; and every relaunch must start the seats, or the windows open idle.

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
- **The Tailscale-SSH-from-the-Mac route can be unavailable** (the laptop had no Tailscale CLI, no 100.x interface, and `archmagi`/`archmagi-wsl` did not resolve). The browser route works: console.tailscale.com > Machines > archmagi-wsl > "SSH to machine" > username Other: `mandrake` (Google re-auth popup) opens a shell as mandrake on Archmagi. Drive it with uiclick plus System Events keystrokes; the cdp extension loses the tab once the SSH popup opens.

## 5. Stand-down / stand-up costs (why switches are not free)

- Every window and helper on the machine is killed; unpublished work dies. **Publish at every green
  point** and write the handoff BEFORE a switch (the soft line exists to give time for this).
- Remote Control sessions are likely dropped and need re-attaching (UNMEASURED; see skill
  `claude-remote-control`).
- Vault freshness: a stale vault cannot be probed or switched to. `account_usage.py` warms an expired DORMANT login
  itself (at most once per hour per account, under claude-account's own lock, refused if that login is live here or on
  any remote); `claude-account-warm.timer` (daily) is separate and still warms every account (WARMTIMER_HARDEN_SPARE_LIVE).
- The relaunched Fleet comes up on the new account; check `slot_allocator now` before assuming capacity.
- **`claude-account warm <acct>` is NOT safe on the live login.** `warm_one` only observes a LIVE account while Claude processes run; with none running it runs `claude` on the live login (a refresh of the live credential). A dormant-only warm must first prove the account is live nowhere: `account_usage.poll` checks the switcher's own status and every remote's status and skips any live label.
- **A relaunched Claude window is not a working seat until it gets a first prompt.** The WT seat profiles (`install_wt_seat_profiles.py`) launched `claude` with none, so every boot or account-switch relaunch opened BENCH and FOUNDRY idle until someone typed wake; the fix is `WAKE_PROMPT` as a positional after `--remote-control '<label>'` (measured 2.1.308: not swallowed as the RC name). The live Artist profile had drifted from the installer, so a bare `--apply` rewrites tiles you did not mean to touch: use `--only SEAT,SEAT` and diff live vs `build()` first. A seat restart relaunches in the SAME tile (`seat_loop.sh` execs the killed record's argv) because `launch_fleet` opens a new tab and orphans the old tile; `launch_fleet -Seats <SEAT>` is only the fallback (its path from the systemd-run Dispatcher through WSL interop is UNMEASURED and gets no first prompt). A `/clear`'d idle window reads 'not quiet' and holds.
- **A Dispatcher-started restart over the hard context limit stays held** ('no boundary yet, last record assistant_tool') for as long as the window sits on an unanswered AskUserQuestion card, and `restart_reconcile` then alarms `OPS_RESTART_UNSTICK_*` after `restart_reconcile_held_s`. Read the tail of the seat transcript first: a pending card means it waits on the owner and nothing is broken.

## 6. Throttles and timers

- Allocator override: `slot_allocator.py set --mode DARK` (every seat 0) / `set --n N --hours H`, `clear`.
  `--n 0` does NOT stop the FOUNDRY seat; use DARK. A DARK left behind after a reset strands the fresh
  week: lift it when the escape condition changes.
- Pausing timers: only `timers_guard.py pause --hours H --all|TIMER` (it arms the restart first,
  then stops). A bare `systemctl stop` of rm-*/testq-* timers on 2026-10-28 05:04 killed every no-LLM lane
  and the watchdogs until 09:41. `account-plan` is deliberately outside that glob.

- Test spend is throttled by policy, not by hand: `design/RimMandrake/testing_policy_2026-10-28.md` (tunables
  `src/RimMandrake/rimflow/testing_policy.json`, reader `testing_policy.py`). Mutation runs (`run_mutation.py`,
  mutmut on SteveDesktop; gate enforced in code): testing_policy_2026-10-28.md §2.6. Nightly sweep: §2.3. testq
  lanes and filler hours: §2.7. Which test for which code: §4. Only D/A tunables may be moved by an agent: §0.
- **`slot_allocator`'s message-count rate fallback counts only THIS machine's assistant messages;** another machine on the same account (SteveDesktop on system) is invisible to it, so the measured %/h reads low until the `account_usage` series has >=4 points over >=1.5 h and the slope takes over.
- **Never stop timers for a cutover without a resume armed in the same command** (`systemd-run --user --on-active=6h systemctl --user start $(cat list)`, or `timers_guard.py pause --hours H --all`): a mass stop of every `rm-*`/`testq-*` timer killed the no-LLM lanes for hours, and every watchdog was inside the stopped glob; it also stops `timer-guard`, so the guard cannot see it. To find who stopped a unit: the system journal's tailscaled 'starting non-pty command' lines carry the full remote command, `journalctl -g 'audit: SSH login'` names the peer, and `Unit now frozen` or a same-second mass 'Stopped rm-*.timer' in the user journal means a hand-run pause; search that day's transcripts for `systemctl --user (stop|freeze)` before suspecting systemd or a WSL boot drop.

## 7. Traps

- Never parse a tail-truncated command output: `claude-account --json status` is ~2000 chars and a
  `[-2000:]` tail lost the opening brace, so the live account read as None forever. Parse the whole stdout.
- The dormant-account tie: two accounts read the same newest time; do not take the first dict key.
  `pick_burn_account` prefers the "live login" method, and `claude-account status` is the authority.
- A DARK soft line is right while there is nowhere to go and wrong once a fresh account exists.
- `use` timing out at 600 s mid-switch leaves the journal: recover (section 4).
- Selftests stub the CLI; the real call needs probing once. More: `references/traps.md`.
- **Account handover links (`account_handover.py`) are armed one transient systemd link at a time and are allowances that must end.** After a link fires, check the now-live account has its own onward link (`systemctl --user list-units 'rm-account-handover*'`) or it drains to 0% while the next account in order sits full. A one-time link writes `<from>_to_<to>.done` and then ticks forever as a spent timer, and an armed link with no end outlives the grant it carried: arm with `--until <reset ISO with offset>`, end with `account_handover.py retire --why` (stops `rm-account-handover-<from>.timer`). Its `--dry-run` still appends to the real `log.jsonl`, so a proof grepping that log must require dry_run false.
- **Relentless reach repair.** An UNMEASURED blind check no longer re-checks on a clock and is not cleared by `unhold --offbox` (`relentless_reachfix.py`, rule `reach_repair`): the first blind check blocks the item (wait kind `reach`), the Judge's `--propose` (adapter name or read path) is probed from inside a throwaway Marker wall and applied as a store overlay, then the same sha is checked once. One item per gap class owns the repair and the rest wait on it; a ticket (`reach_classes[].ticket`) is filed only when the probe fails. Do not unhold a reach-blocked item: fix the probe's gap or close its ticket, which triggers one re-probe. Store book: `<store>/reach_gaps.json`.
