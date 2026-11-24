# A design position, written before the blind answer was read

Written by the run that owns the item, from `census.md` and today's files, while the blind design ran. It is one of the
two independent samples of the deep-design shape. The merged design is `design.md`.

## The problem in one paragraph

The plan says which account the machine burns, in what order, down to what line, and what changes for a time. Today the
plan is spread over a JSON file in the repo (a change needs a commit, a publish and a pull by the clone that the timer
runs from), code (`switching_plan.py` holds the rule kinds), prose (the skill's table) and stored state (markers, a
`HOLD` file, a transient timer). Three classes of fault came from that spread (`census.md`).

## Four solutions

### 1. Extend today's engine and file

Keep `switching_plan.json` and `switching_plan.py`. Add a command tool that edits the JSON under a lock, with
validation, a history and an undo. Add fields for the missing rule kinds as new exception keys.

- Cost: small. Risk to the fleet: lowest; the decision code does not change.
- Buys: no more hand edits of JSON. One command per change of a kind that exists today.
- Does not buy: the markers stay, so the stale-marker class stays. The file stays in the repo, so a change is not
  instant: it binds when the dispatch clone pulls it. The plan stays "an order plus exceptions", not steps with
  conditions, so each new kind of rule is again a code change.
- Best when: the fleet cannot bear any change to the decision this month.

### 2. A step list in one machine-local file, a new pure decision, the old actuator kept

- One file, machine-local (beside the control store, not in the repo), so a change binds at the next read by every
  clone. An append-only history beside it. Each owner-authority change also goes to the ledger, after the write, and a
  ledger failure never undoes the plan change.
- The plan is an ordered list of named steps. A step: use this account; until these conditions; warn with this leeway;
  an optional life (`from`, `until`, `ends_at_reset_of`), after which the step is inert.
- A new pure function: (plan, readings, the switcher's log, the live account, the live runs, now) gives the decision:
  the current step, the target account, each account's line, why, the next event and its estimated time.
- No marker. The anti-flap rule that the markers carry becomes hysteresis, read from the readings alone: the live
  account stays the target while it is above its leave line; another account is a target only when it is above its
  leave line plus an entry margin. A refilled account is above the margin and is a target at once (row 19). A lowered
  line opens the account at once (row 9).
- A hand switch is a plan command (`switch-now`, `pin`), so the plan and the hand cannot fight (row 7). A switch made
  outside the tool is seen in the switcher's log with no act of the actuator beside it; the decision treats it as a pin
  until that account reaches its line, and `status` says so.
- The actuator stays: arm, use, disarm, the drain, the save and emergency orders, the notice. At cut-over it asks the
  new decision for the target and the lines. Its own episode state (who was ordered, the pause's start) stays, because
  that state records acts that happened, and it ends with the episode.
- Cost: medium. Risk: a wrong decision moves the fleet to the wrong account; shadow and replay measure that first.
- Best when: the fault classes of the census must go and the actuator must not be rebuilt. This is today.

### 3. The plan as rows in the pipeline's control store

Put the plan in `control.db` (SQLite) and command it with `./pipe account ...`.

- Buys: one store that every launch reads already; atomic writes; a history table.
- Costs: a database is not "a single file that everyone knows to read": a person or an agent cannot read it without a
  tool. The account plan then fails when the pipeline's store is locked or broken, and the reverse.
- Best when: the plan must gate each launch inside the same transaction as the launch.

### 4. The plan as an append-only log of commands

The file is a list of commands; the plan in force is the fold of the list.

- Buys: history and undo are the same file; appends by two writers do not tear.
- Costs: no one can read the plan without a tool; one bad line needs a rule; the fold must be the same code everywhere.
- Best when: audit is the first need. Here it is the second: solution 2 keeps the log beside a plain plan file.

## The pick

Solution 2. The reason: it is the smallest design that removes all three fault classes, and it leaves alone the two
parts that the census shows did not fail (the reader and the actuator).

What would change the pick:
- if replay shows that hysteresis flaps where the markers did not, the pick falls back to solution 1 plus the commands;
- if the actuator cannot take its target from outside without a rewrite, the cut-over cost rises to a rebuild.

## Claims the pick rests on

| claim | status |
|---|---|
| * The timer runs the engine from a clone, so a plan change in the repo binds only after a publish and a pull | read: `skills/rimflow-operations/SKILL.md` (the timer), `account-plan.service`; to re-measure |
| * The markers exist only to stop a flap back to an account that was left at its line, and to tell the plan's switch from a hand switch | read: `switching_plan.py` `_decide` (the `kept_out` loop), `manual_switch` |
| * The meter reads whole percents, so an entry margin of a few points is the smallest hysteresis that the meter can see | read: `switching_plan.json` `floors._doc` (8,749 readings, none fractional) |
| The series file holds at least two weeks of readings for a replay | assumed; to measure |
| * `decide` is separable from `_check`: the actuator reads only `do`, `to`, `under`, `line`, `pct_left`, `warn_line`, `key` and the drain flags | read: `switching_plan.py` `_check`; to confirm by building the shadow |
| The switcher's log names every switch with its time | read: `switching_plan.py` `switches()` |
