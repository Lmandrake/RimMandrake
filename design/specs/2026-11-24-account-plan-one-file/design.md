# DESIGN: the account plan as one file, commanded in one line, Design Version 0.1.0

Item: `RIMMANDRAKE_DESIGN_ACCOUNT_PLAN_ONE_FILE_COMMANDED_IN_ONE_LINE`. Written 2026-11-24 by the run that owns the
item (Fable). Inputs: `census.md` (21 rows), `01-design.md` (the first position, four solutions) and `02a-gpt-blind.md`
(a blind design by GPT). No design and no code went to GPT after the owner's order of about 2:15 PM PST. The promises
are in `boundary.md`. Code: `src/RimMandrake/Utils/account_plan.py`, command `./acct`.

## The owner's orders that this design answers

- About 1:20 PM PST: the plan is "a single file that everyone knows to read", changed by "instantaneous Python
  deterministic scripts that take command line arguments". The template: "use this account until (condition is true)
  then warn for (this much leeway) until we switch to (next plan) ... and so on."
- About 2:15 PM PST: "build something that behaves as a human might make their own decisions... such as to stay on an
  account and drain it without incurring additional switches because of alphabetical order or arbitrary list order".
- About 2:19 PM PST: Burn Mode, and the measures in his order: allowance wasted; work wasted by switching; then the
  speed of a decision (Python, no model); then the clarity of "what will happen now, next, and if I say this?".

## The pick

A step list in one machine-local file, one pure decision that a forecast also uses, one-line commands, and the old
meter reader and account-end actuator kept. This is solution 2 of `01-design.md` and the middle option of
`02a-gpt-blind.md`, with a new decision rule (below) that neither of them had.

What changed against both inputs: the old engine and both first designs pick "the first eligible account in the
order" at every pass. That rule is the cause of three of today's faults (a preference switch, the refused starts, the
hand-written hold to stop a wrong switch). This design replaces the rule.

## The decision rule: what a sensible person does

1. **Stay.** The live account stays live until its own step is finished: its level reaches its warning line, or the
   step's `until` condition is true, or no step uses the account now. The order of the steps is never a reason to
   leave a live account.
2. **Next.** When the live account is finished, the next account is chosen among the accounts that can take over
   (measured, fresh, a step uses it now, above its entry line). The choice is the one with the best week ahead (rule 4).
   With an unknown burn rate, or with equal weeks ahead, the choice is the first one in the step order.
3. **No refused start for a preference.** The notice that refuses new runs is written when the live account is at
   its own warning line (the account-end sequence of 2026-11-24, kept as it is), in a switcher call, and for a rescue
   that is worth it (rule 5). The step order, a reset that is near, and a small rescue refuse nothing.
4. **Resets are planned for.** The tool runs the week ahead for each choice that it has now: stay, or switch to each
   account that can take over. One run of the week ahead is `forecast()`: the same step rules, the measured burn rate,
   each account refilled at its reset. It counts two things:
   - **erased**: the points of each account above its leave line at the moment of its reset;
   - **switches**: each change of the live account.
   The cost of a choice is `erased + switch_cost_pts x switches + idle points` (idle: burn that found no account).
   The lowest cost wins. A tie goes to fewer switches, then to stay, then to the step order.
5. **A rescue is weighed.** A rescue is to leave a live account that is not finished, because the week ahead of that
   switch is better. It is taken only when it betters the week ahead by at least `switch_cost_pts`.
   - With no run live, the switch goes at once.
   - With a run live, the switch must also pay for the wait: `switch_cost_pts` plus the burn rate times
     `rescue.drain_h` hours (the work that the wait delays). Then no new run starts while the live runs finish, for at
     most `rescue.drain_h` hours, and the switch goes. The reason line says all three numbers.
   - A smaller rescue refuses nothing and waits for a pass with no live run. The status line says how many points are
     at risk and names the command that goes at once (`./acct switch <account> --now`).
   - Why not "never refuse a start": measured 2026-11-18 to 11-24, the fleet had a run live for 50.8 h without a
     break; the model of 2026-11-10 to 11-24 with no idle moment erases 43 points of Steve's account under that rule
     and none under this one. `./acct set numbers.rescue.drain_h=null` gives the strict rule.
6. **A hand switch is respected.** When the last switch in the switcher's log was not made by this tool, no rescue
   switch leaves that account. It stays until it is finished. `./acct pin` does the same on purpose, with an end.
7. **The reason is one line that a person can check.** Every decision prints: the live account, its level and line,
   the next account and about when, and the two counts (erased, switches) of the choice taken and of the best other
   choice.

Rule 1 removes the need for markers. An account that was left at its line is under its entry line, so it is no
target. After its reset it reads above the entry line, so it is a target again at once (census rows 9 and 19). A
hand switch is only a different live account, and rule 1 keeps it (row 7).

The 2026-10-28 ruling (the machine goes to system at its reset although lukas still has budget, "awkward") was a rule
of fixed priority. His words of 2026-11-24 replace it: order answers only "which account is next". The replay lists
each such case as a wanted difference.

## The one file

- Path: `~/.local/state/rimmandrake/account_plan/plan.json` (ext4, outside every clone, beside the control store).
  `RM_ACCOUNT_PLAN_DIR` names another folder for tests; a test never reaches the live file.
- A change binds at the next read by any program in any clone. No commit, publish or pull.
- Beside it, written only by the tool:
  - `history.jsonl`: one line per change, with the whole plan before and after, who, why, and the command. Undo reads it.
  - `log.jsonl`: one line per timed pass: the decision, its reason, the readings it used.
  - `burn_mode.json` and `decision.json`: the published state for other programs (rewritten each pass).
  - `frame.json`: the slow readings of the last pass (Codex, JPL GenAI), with their time.
- No file here keeps an account in or out. `history.jsonl` and `log.jsonl` record acts. A lost log makes the tool
  treat the last switch as a hand switch, which only makes it stay.

### Shape of `plan.json`

```json
{
  "schema": 1, "rev": 3,
  "accounts": {"system": {"kind": "claude"}, "lukas": {"kind": "claude"}, "steven": {"kind": "claude"},
               "codex": {"kind": "meter", "leave": 25}, "jpl-genai": {"kind": "meter"}},
  "steps": [
    {"name": "steven", "use": "steven", "leave": 52, "when": "hours_since_reset <= 48", "why": "..."},
    {"name": "system", "use": "system", "leave": 1, "why": "..."},
    {"name": "lukas",  "use": "lukas",  "leave": 1, "why": "..."}
  ],
  "holds": [], "pins": [], "requests": [],
  "numbers": {"...": "every number, each with its danger in boundary.md LIMITS"},
  "ledger_item": "..."
}
```

- **A step** is the owner's template: use `use`, until its level is at `leave` (or `until` is true), warn `warn` points
  before that, then the next step. Fields: `name` (its identity), `use`, `leave` (a number, or `entry-N`: N points under
  the level at switch-in), `warn` (leeway in points; default from the numbers), `until` and `when` (conditions), and a
  life: `from`, `ends`, `ends_at_reset_of` (the first reset of that account after `from`, read from the meter).
- **The rule of an account** is its first step, in list order, that is alive (inside its life, `when` true). A
  temporary step stands before the standing step of the same account and shadows it until it ends. The order in which
  accounts first appear among the live steps is the step order.
- **A condition** is a line of a small fixed grammar, parsed at each write and refused when wrong:
  `term op number`, joined by `and`, `or`, `not`, brackets. Terms: `left`, `hours_to_reset`, `hours_since_reset`,
  `age_min`, `burn` (points an hour), each of the step's account or of another with `:account`; `runs` (live runs);
  `clock` (local `HH:MM`), `weekday` (`mon`..`sun`). A condition is true, false or unknown. Unknown never gives
  permission: a `when` that is unknown is not alive; an `until` that is unknown is not finished.
- **A meter account** (Codex, JPL GenAI) is never a switch target. It has a leave line, the reset-day rule and Burn
  Mode, and `./acct can-use codex` answers whether our work may send it a job.
- **The reset-day rule** is data: `numbers.reset_day = {"hours": 24, "accounts": ["codex", "system", "lukas"],
  "line": {"meter": 0, "claude": "floor"}}`. Inside that many hours before an account's reset, its leave line is the
  reset-day line. Steve's account is not in the list (the ruling's reading).
- **A hold** has an id, a why, who, and an end (`--for 2h` or `--until`). A hold with no end is refused; the refusal
  names `--for`. While a hold stands, a timed pass acts on nothing.
- **A pin** keeps rescue switches off the live account until its line or its end.
- **A request** is `switch <account>`: it goes when no run is live (`--now`: at once). It is done when the switcher's
  log shows a switch to that account after the request was written. It carries an end (default 24 h).

## What becomes of each old home of a rule

| home | after the cut-over |
|---|---|
| `switching_plan.json` | read once by `./acct import-legacy`; it carries a tombstone that points at the plan file, and is read again only while the old engine decides (`./acct driver old`, or a refused plan file) |
| rule kinds in `switching_plan.py` (`_decide`, exceptions, markers, pool) | not called; `tick` gives the actuator part of that file its decision |
| `markers/*.json` | read only as the record of a switcher call in flight (`pending`, under 40 min) or failed; never as "this account is out" |
| the `HOLD` file | a hand-made one is still obeyed and shown; `./acct hold` is the door |
| the skill's rule table | the commands, with no number (done: `skills/rimflow-operations/SKILL.md` §2) |
| `slot_rules.json` `ops.codex_*` | a pointer (`_codex`); the allocator's advice line and Codex's door read `./acct can-use codex` |
| `slot_rules.json` `lent_accounts` | kept: the allocator's own draw check (`slot_allocator.py plan`); a temporary line comes from the plan file (`temporary_line`) |
| `standing_rulings.md` prose (leave lines, reset day, "run to the line") | history; each rule is a field of the plan |
| `account_handover.py` timers | deleted 2026-11-24; `./acct switch <account>` and `./acct step add ... --ends-at-reset` are the doors |

## Commands (each one line; a write prints at most 3 lines, the last is its undo)

```
./acct status                  now, next and about when, every account as LEFT with age, Burn Mode, holds
./acct next                    one line: what happens now and next
./acct plan                    the whole plan: steps in order, lines, holds, pins, requests, numbers
./acct readings                each account: left, reset (Pacific), age, source
./acct forecast [--rate R]     the week ahead: each switch and reset, points erased, switches
./acct measures [--weeks N]    per past week: points erased per account, switches, refused-start minutes
./acct whatif -- <a write>     the write on a copy: now, next and the week ahead, before and after; writes nothing
./acct order A B C             the step order
./acct line A N [--until-reset [B] | --for D | --until T]     a leave line, standing or temporary
./acct step add|set|rm|move    a step, with --use --leave --warn --until --when --first/--before/--after --ends...
./acct switch A [--now]        go to A when no run is live (or at once)
./acct pin [--for D]  ·  ./acct unpin        ./acct hold --for D  ·  ./acct release
./acct set numbers.K=V         one or more numbers
./acct undo [REV]              the plan as it was before that change
./acct can-use A               exit 0 yes, 1 no, 2 could not look
./acct burn-mode               the Burn Mode state now
./acct driver [old|new]        which engine the timer's pass runs (the cut-over and its undo)
./acct pass                    what the timer runs: the old engine with a shadow, or this plan
./acct tick [--shadow]         one pass of this plan (or only its pick, logged)
./acct replay --from T --to T  both engines over the recorded readings
./acct import-legacy           the plan file from switching_plan.json
```

- Every write takes `--why`, `--owner-said`, `--by-card`, `--per-ruling`. None is demanded: a write with none of them
  is done, and its history line says `no reason given`.
- A write: lock (`flock` on a sibling lock file), read, change a copy, validate the whole plan, write a temp file,
  `os.replace`, append the history line. A plan that fails validation is not written; the refusal names the repair.
- An owner-authority write (`--owner-said`, `--by-card`) is also owed to the rimflow ledger. The timed pass sends it.
  A ledger failure never undoes the plan change.

## Answers and exit codes

| answer | printed | exit |
|---|---|---|
| done, or a value (a measured zero is a value) | the value | 0 |
| no (`can-use`), or the shadow disagrees | `NO: ...` | 1 |
| could not look (a reading that the answer needs is missing) | `COULD NOT LOOK: <which, why>` | 2 |
| refused (validation; nothing written) | `REFUSED: <fault>; repair: <command>` | 3 |
| failed (the write or the act broke) | `FAILED: <what>` | 4 |
| empty (nothing to undo, no step, no hold) | `NONE: <what was looked for>` | 5 |

A level that could not be read prints `UNMEASURED: <cause>`, never 0. An account that is not on this machine prints
`not on this machine`.

## Burn Mode

- **What it is:** a state per account, computed each pass from fresh readings, for the live Claude account and for
  each meter account.
- **Enters when** all are measured: the reset is within `burn_mode.window_h`; `usable` (left less the leave line in
  force, the reset-day line included) over the hours to the reset is more than the measured burn; and the points at
  risk (`usable - burn x hours`) are at least `burn_mode.min_at_risk_pts`.
- **Publishes** `burn_mode.json`: per account `state` (`on`, `off`, `unmeasured`), `target_burn_pct_h` (usable over the
  hours left), `measured_burn_pct_h`, `at_risk_pts`, `ends` (the reset), and one `why` line; and `raise_ok` with the
  machine load.
- **Changes, through the programs that own them** (the wiring ticket, after the cut-over): the helper allocator raises
  its pace to the target while `raise_ok`; the pipelines put first the work that loads the account and is wanted
  anyway; Codex's door prefers a Codex job while Codex is `on`.
- **Ends when** the reset passes, or the points at risk fall under the minimum, or the level is at the line.
- **Never:** starts work (it publishes two files); counts allowance under a leave line that is not lifted (the target
  is computed above the line in force); raises load on a loaded machine (`raise_ok` false over
  `burn_mode.max_load_per_core`); reads `on` from an unknown burn (that state is `unmeasured`).

## The measures

1. **Allowance wasted:** per account and week, the points above the leave line at the reset (`measures`, from the
   reader's series; `forecast`, for the plan now).
2. **Work wasted by switching:** switches per week (the switcher's log), runs live at each switch (the tool's log from
   the cut-over on), and the minutes in which new runs were refused for a switch that the level did not force (the old
   engine's log has these as `drain`).
3. **Speed:** a decision is one Python process and no model call; `status` reads only cached readings.
4. **Clarity:** `status` and `next` say now and next; `whatif` says "if I say this".

## The actuator, and the cut-over

- The account-end actuator stays: arm, `use`, disarm, the save and emergency orders, the pause, the notice, the fleet
  stop and start (`switching_plan._check`, `account_end.py`). `./acct tick` runs that same code and gives it this
  design's decision in place of `switching_plan.decide`, and the numbers of the plan file in place of
  `switching_plan.json`. No line of `switching_plan.py` changes.
- The cut-over has two steps, both the Conductor's act.
  1. The timer's unit runs `account_plan.py pass` in place of `switching_plan.py check`. With `driver` old (the value
     of a new plan file) that pass runs the old engine as it is, and logs this tool's pick beside it: this step changes
     no decision, and it is the shadow.
  2. `./acct driver new --why "..."` makes the plan decide. `./acct driver old` (or the undo that the command prints)
     gives the old engine back at the next pass. Each is one line and binds at once.
- With a plan file that is missing or refused, `pass` runs the old engine and says why.

## What the tool never does

Log in, read or print a credential, poll the meter from a status command, start work, stop one run by hand, write a
marker that decides eligibility, or refuse the owner's or the Conductor's write for a missing provenance flag.

## Taken from GPT's blind design, and rejected

- Taken: unknown is a third truth value and never gives permission; a request is done by evidence in the switcher's
  log, not by a flag; a hold needs an end; relative lines read the level at switch-in; the forecast and the pick share
  one function; shadow has no actuator; replay separates wanted differences from unexplained ones.
- Rejected: the plan file kept in the repo (a change would still need a publish and a pull); templates, scopes and a
  typed AST (three more record kinds than the census needs); a bitset exit code (a caller cannot test it with `$?`
  alone); a full audit journal with PREPARE and COMMIT (the history line after the replace is enough for undo, and a
  crash between the two leaves a valid plan); changes inside `account_usage.py` and the switcher's log (both stay as
  they are); first-eligible-in-order as the pick (the cause of today's faults).

## Claims the pick rests on

| claim | status |
|---|---|
| `switching_plan._check` takes its decision from the module name `decide`, so `tick` can hand it one | read, then tested: `tick_drives_the_old_actuator` |
| The readings reader answers in about 15 ms and the live account in about 0.1 s; Codex's reader takes about 1.8 s | measured 2026-11-24; so `status` reads Codex from `frame.json` |
| The series holds the readings of 2026-10-26 on (9,030 lines) | measured 2026-11-24 |
| One point of a week is the same amount of work on each Claude account | assumed; the replay says so beside its scores |
| The fleet has moments with no live run often enough for a rescue switch | measured false, 2026-11-18 to 11-24 (control store, 783 detached runs): 11.5% of passes idle, longest busy stretch 50.8 h. So rule 5 has the weighed drain |
