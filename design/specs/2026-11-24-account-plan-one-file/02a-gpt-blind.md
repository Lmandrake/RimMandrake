ACCOUNT PLAN ONE FILE

Pick: **replace the plan representation, decision function and command interface; retain the existing meter and the account-end actuator behind a small adapter.** Do not rewrite the switcher, drain, save orders or emergency pause.

This is worth switching to if replay confirms the safety boundary. Today, changing policy still requires JSON edits, code changes or prose; the census records all three. The replacement makes policy changes transactions against one file.

The commands below are proposed interfaces, not implemented commands. No live readings were supplied, so I do not claim which account is currently eligible.

**A. Questions, answered**

| Question | Answer |
|---|---|
| 1. What is the smallest useful replacement? | One validated plan file, one pure evaluator, one transactional CLI, and an adapter supplying decisions to the existing actuator. Remove eligibility markers, add the missing policy fields, and require ends and reasons for temporary instructions. |
| 2. Replace the actuator too? | No. Preserve `armed_call`, draining, save/emergency delivery, pause sizing and recovery integration. `_check` needs refactoring because it currently mixes these with decisions and markers. It cannot simply consume the new decision unchanged. |
| 3. What does “instant” mean? | A command commits policy and computes its cached-data answer without polling, network access or a model call. Target: well under one second on this machine. Actual switching remains asynchronous: live work, arming and the switcher can take longer. Filesystem failure can prevent the latency target. |
| 4. Is the order a permanent, advancing cursor? | No. It is an ordered, named, conditional priority program, reconsidered every pass. Earlier steps can become eligible after a measured reset/refill. This preserves today’s fixed-priority behavior rather than inventing irreversible progression. |
| 5. How does a hand switch stop fighting the plan? | `switch` commits a named temporary step before requesting execution. `pin` adopts an account already selected by hand. Both end at a measured condition or explicit time. Raw switches remain respected through an explicit policy in the plan, using attribution in the switcher’s log. |
| 6. Can a line be relative? | Yes: `entry_left - 50pp`, or `entry_left * 0.5`. These are deliberately different. Row 6 is interpreted as **50 percentage points**; the wording alone does not prove that interpretation. |
| 7. What is “entry left”? | The identified measured observation used for a successful switch-in, recorded by reference in the switcher’s log. Its age and whole-percent uncertainty remain visible. It is not an invented instantaneous measurement. |
| 8. How does an allowance end at reset? | At the first reset boundary after its stated anchor, established from recorded meter observations. Never keep rolling that end forward to the newest “next reset.” Unknown boundary means no exceptional spending permission. |
| 9. How do overnight rules work? | A timezone, weekday set and half-open local-time interval in plan data. Explicit instants use offsets. Repeated DST hours both belong to the same local interval; nonexistent local times occur zero times. |
| 10. What happens on the last account? | A named terminal `wait` step: warn/save, drain/stop through the existing actuator, then wait for **measured** eligible headroom. A predicted reset never supplies an actual 100% reading. |
| 11. What does an unreadable meter mean? | `UNKNOWN`, with a typed cause. Never 0%, never an empty account collection. The old “blind meter = 0%” conversion is removed; an explicit exhaustion-risk decision can still brake work without fabricating a level. |
| 12. How is flapping prevented without markers? | Every nonlive target must be above its maximum applicable warning line. Accounts just left at that line cannot immediately be selected again. A lower authorized line or a measured refill can make them eligible immediately. |
| 13. Does `switch now` authorize killing live work? | No. It creates a pending request whose execution condition is a positively measured empty live-run set. Existing account-emergency policy remains independently applicable and must be identified separately in the decision. |
| 14. Who owns pacing? | The allocator. This tool publishes spendable pool parts, deadlines and suggested pace; it does not set concurrency. |
| 15. How are missing provenance flags handled? | Record whichever of owner words, card answer and ruling ID are supplied, plus authenticated local identity. Never demand an additional authority flag when the owner’s words are present. If those words supply the reason, use them as `why`. |
| 16. Can Codex and GenAI participate? | They appear in the same status and policy file, but are separate spending lanes, never Claude switch targets. Codex admission uses its leave policy. GenAI is informational until its consumer integration is verified. |
| 17. Can every historical instruction be reconstructed exactly? | No. Some times, meanings and supporting files are missing. Represent those uncertainties explicitly; do not turn them into new defaults. |

Today’s priority, manual-switch behavior, drain and account-end behavior are described in `switching_plan.py:7`, `switching_plan.py:20`, `switching_plan.py:26` and `switching_plan.py:31`.

**B. Three different solutions**

| Approach | How it works and file shape | Build cost | Buys | Risks; best when |
|---|---|---|---|---|
| **Extend today’s engine and file** | Keep schema 1, priority picker and markers. Add CLI transactions, relative lines, schedules, bounded holds and requests alongside `order`, `accounts` and `exceptions`. | Lowest initial cost; medium ongoing cost. | Fastest access to common commands; smallest immediate migration. | Every new feature crosses existing marker, exception, forecast and pool logic. Named steps remain awkward. Best if requirements stop at a few extra fields and marker elimination is waived. |
| **Named conditional program; retain actuator — pick** | One JSON document containing named ordered steps, data templates, lane policies, actuator parameters and provenance. A pure evaluator emits a typed decision. | Medium; actuator extraction, reader error reporting and replay are substantial. | Direct expression of all census policy changes; shared decision/forecast semantics; no eligibility markers. | More explicit semantics to specify and test. Best for this recurring mix of conditional instructions and live-fleet safety. |
| **Event-sourced policy interpreter** | The one file is an append-only sequence of commands: grant, revoke, pin, reorder, hold. Every read folds the events into an effective program and evaluates it. | Highest. | Excellent provenance, reconstruction and command-oriented history. | Current policy becomes a fold rather than an immediately inspectable document; compaction and event-version migration become critical. Derived episodes can become disguised cursors. Best when forensic reconstruction dominates operational simplicity. |

**C. Why the middle option**

The repeated failures concern **policy representation and stale eligibility state**, not the meter or the account-end mechanisms. The census explicitly identifies those boundaries as components to retain.

The middle option removes those faults without rebuilding the dangerous switching machinery. I would change my pick if:

- the actuator cannot be separated from eligibility markers without effectively rewriting it;
- real switch logs cannot support reliable attribution and entry-observation references;
- replay shows that measured admission rules produce unacceptable lost budget or repeated switches;
- the required program turns out to need durable workflow progression rather than recurring measured priority.

In the last case, use an explicit event-sourced workflow, not a hidden cursor.

**D. Complete design**

**One authority and the old rule homes**

Keep the established path: `src/RimMandrake/Utils/switching_plan.json`. Upgrade its schema in place at deployment. Every consumer reads it through the same loader.

| Existing rule home | Disposition |
|---|---|
| Skill’s policy table and numeric description | Replace with a pointer and command examples containing no policy values. |
| `slot_rules.json.lent_accounts` | Remove account-policy fields. Allocator reads the plan’s effective allowance. |
| `slot_rules.json.ops.codex_*`, `codex_advice.py` policy defaults | Remove policy copies; retain measurement/advice functions that consume the plan. |
| Standing rulings prose | Historical evidence only; prominent pointer to the executable plan. Never consulted for live decisions. |
| `HOLD` file | Import deliberately as an attributed, ending hold during migration; remove its enforcement path after cut-over. |
| `account_handover.py` timers | Retire plan-changing timers; import outstanding intentions as named steps/requests. |
| Codex leave line | Plan data, consumed by Codex admission/advice. |
| Marker files | No input to the new decision function. Archive for replay evidence only. |
| Actuator state and notices | Delivery/execution facts only; no account eligibility or policy authority. |

The current duplicated and prose-only homes are documented in census rows 1, 4, 5, 17 and 20.

**Schema**

This is the complete set of record types. Unknown keys, duplicate names and invalid references are errors.

| Record | Required fields and meaning |
|---|---|
| Document | `schema`, `revision`, `parent_hash`, `change`, `timezone`, `control`, `accounts`, `templates`, `scopes`, `steps`, `lanes`, `parameters`, `evidence`. |
| `change` | Unique change ID, timestamp, OS identity, `why`, supplied provenance fields, audit-record hash. |
| Account | Registry label, lane, presence source. No login details or credentials. |
| Template | Named, typed parameters and declarative step body. Expansion is deterministic; no Python or executable strings. |
| Scope | Name, measured condition, optional start instant, required end for temporary permission/restriction. End can be an instant or anchored reset; multiple ends mean the earliest. |
| Step | Unique stable name, kind, template reference/arguments or full body, optional scope and provenance reference. Position supplies order, never identity. |
| `use` body | Account; activation condition; leave expression; warning/leeway reference; until condition; transition mode. |
| `wait` body | Activation condition, until condition, actuator behavior reference. Exactly one terminal wait is required. |
| Lane policy | Admission/leave rules for a nonswitching lane; ordered conditional overrides; fallback. |
| Hold | Named restriction, start, end, reason and provenance. Stored under `control.holds`. |
| Switch request | Named target step, creation/end, positively measured execution condition. No mutable “pending/done” flag. |
| Parameters | All operational policy numbers, including actuator scheduling and freshness settings. |
| Evidence | For every limit/cut: affected field, danger, evidence, provenance and known uncertainty. |

Expressions are typed ASTs in canonical storage. The readable notation below is accepted by the CLI and deterministically parsed into those ASTs.

Names are immutable identity: renaming means inserting a new step and removing the old one in one transaction.

**Today’s plan in the schema**

The following is the authored representation. Template expansion adds no policy defaults from code.

```json
{
  "schema": 2,
  "revision": "migration",
  "parent_hash": null,
  "change": {
    "id": "migration",
    "at": "<installation time>",
    "by": "<local identity>",
    "why": "Import the supplied plan and identified rulings",
    "provenance": ["supplied-plan", "census"],
    "audit_hash": "<computed>"
  },
  "timezone": "America/Los_Angeles",
  "control": {
    "driver": "legacy",
    "holds": [],
    "requests": [],
    "foreign_switch": {
      "effect": "respect_live_account",
      "until": "leave_due(live) or window_closed(live) or next_changed_switch"
    }
  },
  "accounts": {
    "system": {"lane": "claude", "presence": "switcher_registry"},
    "lukas": {"lane": "claude", "presence": "switcher_registry"},
    "steven": {"lane": "claude", "presence": "switcher_registry"},
    "codex": {"lane": "codex", "presence": "existing_codex_reader"},
    "jpl-genai": {"lane": "genai", "presence": "existing_genai_reader"}
  },
  "templates": {
    "weekly_use": {
      "parameters": ["account", "scope", "leave", "window"],
      "body": {
        "kind": "use",
        "account": "$account",
        "when": "scope($scope) and window($window)",
        "leave": "$leave",
        "warn": "account_end",
        "notice": "leave + soft_margin_pct",
        "until": "left($account) <= warning_line(this) or not window($window)",
        "transition": "retained_actuator"
      }
    }
  },
  "scopes": {
    "SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20": {
      "from": "2026-11-20T16:45:00-08:00",
      "ends": [
        {"at": "2026-11-27T16:00:00-08:00"},
        {
          "first_reset_after": {
            "account": "steven",
            "anchor": "2026-11-20T16:45:00-08:00"
          }
        }
      ],
      "provenance": "supplied-plan-exception"
    },
    "standing": {
      "when": "not scope(SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20)"
    }
  },
  "steps": [
    {
      "name": "SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20/system",
      "template": "weekly_use",
      "args": {
        "account": "system",
        "scope": "SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20",
        "leave": "3pp",
        "window": "always"
      }
    },
    {
      "name": "SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20/steven",
      "template": "weekly_use",
      "args": {
        "account": "steven",
        "scope": "SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20",
        "leave": "5pp",
        "window": "always"
      }
    },
    {
      "name": "SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20/lukas",
      "template": "weekly_use",
      "args": {
        "account": "lukas",
        "scope": "SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20",
        "leave": "floor(this)",
        "window": "always"
      }
    },
    {
      "name": "standing/steven",
      "template": "weekly_use",
      "args": {
        "account": "steven",
        "scope": "standing",
        "leave": "52pp",
        "window": "within 48h after measured_reset(steven)"
      }
    },
    {
      "name": "standing/system",
      "template": "weekly_use",
      "args": {
        "account": "system",
        "scope": "standing",
        "leave": "floor(this)",
        "window": "always"
      }
    },
    {
      "name": "standing/lukas",
      "template": "weekly_use",
      "args": {
        "account": "lukas",
        "scope": "standing",
        "leave": "floor(this)",
        "window": "always"
      }
    },
    {
      "name": "last-account",
      "kind": "wait",
      "when": "no measured eligible use step",
      "until": "some measured eligible use step",
      "actuator": "warn_drain_stop_then_wait"
    }
  ],
  "lanes": {
    "claude": {
      "selection": "first_eligible_named_step",
      "nonlive_admission": "left(account) > max(leave, warn_pct) + (warn_fast_pct - warn_pct)",
      "evening_reserve": "none",
      "unknown_level": "unknown",
      "blind_near_empty": "exhaustion_risk_without_numeric_substitution"
    },
    "codex": {
      "leave": "25pp",
      "overrides": [
        {
          "name": "use-before-reset-today-2026-11-24",
          "when": "now >= 2026-11-24T12:41:00-08:00 and now < first_reset_after(codex, 2026-11-24T00:00:00-08:00) and local_date(first_reset_after(codex, 2026-11-24T00:00:00-08:00)) == 2026-11-24",
          "ends": [
            {"at": "2026-11-25T00:00:00-08:00"},
            {
              "first_reset_after": {
                "account": "codex",
                "anchor": "2026-11-24T00:00:00-08:00"
              }
            }
          ],
          "leave": "0pp",
          "provenance": "census-row-20"
        }
      ],
      "recurring_pre_reset_release": {
        "lead": null,
        "unresolved": "Owner has not specified how long just before reset means"
      }
    },
    "genai": {"mode": "observe"}
  },
  "parameters": {
    "floors": {
      "switch_away_pct_left": 1,
      "wait_pct_left": 2,
      "blind_exhaustion_evidence_pct": 1
    },
    "account_end": {
      "warn_pct": 2,
      "warn_fast_pct": 3,
      "emergency_pct": 1,
      "emergency_max_line": 10,
      "save_need_min": 10,
      "burn_window_min": 45,
      "burn_min_span_min": 10,
      "stale_min": 20,
      "poll_min": 0.5,
      "pause_share": 0.2,
      "pause_from_pct": 0.5,
      "pause_max_s": 180,
      "pause_min_s": 20,
      "clear_pct": 5
    },
    "soft_margin_pct": 2,
    "pull_drain_max_s": 7200,
    "switch_lead_min": 20,
    "fresh": {"near_pct": 3, "max_age_min": 6},
    "window_margin_min": 10,
    "pool_pacing": true,
    "execution": {
      "beat_s": 300,
      "ending_repeat_s": 60,
      "notice_fresh_s": 1200,
      "switcher_call_timeout_s": 600,
      "meter_poll_timeout_s": 420
    }
  },
  "evidence": "<the field-indexed records specified below>"
}
```

The exception’s presence does **not** prove it is active on November 24. Its reset end must be evaluated from historical observations. Its dates/order/lines come from `switching_plan.json:62`.

The Codex recurring release remains unresolved, rather than inventing a “just before” duration. The dated release expresses the supplied “before the reset today” instruction only when that reset can be established. Otherwise the 25% fallback stands.

The imported 48-hour interpretation remains explicitly delegated, not attributed to the owner: `switching_plan.json:16`.

**Conditions and unknowns**

Readable grammar:

```text
condition := comparison | condition and condition | condition or condition
           | not condition | (condition)
comparison := term comparator term
comparator := < | <= | == | != | >= | >
term       := literal | measured_term | term + term | term - term
           | term * dimensionless_literal | min(term,term) | max(term,term)

measured_term :=
    left(account[,model])
  | burn(account)
  | reset_time(account)
  | time_to_reset(account)
  | reading_age(account)
  | live_run_count
  | now
  | local_date(now) | local_time(now) | local_weekday(now)
  | entry_left(step)
  | first_reset_after(account,anchor)
```

`scope`, `window`, `floor`, `warning_line` and eligibility predicates are typed, acyclic macros over those terms and plan data. No Python, arbitrary function invocation, shell evaluation or model evaluation.

- A condition returns `TRUE`, `FALSE` or `UNKNOWN(causes)`.
- Comparisons involving an unavailable operand return `UNKNOWN`.
- `not UNKNOWN` remains unknown.
- `FALSE and UNKNOWN = FALSE`; `TRUE or UNKNOWN = TRUE`; otherwise unknown propagates.
- A positive spending permission requires `TRUE`.
- A known expired temporary permission is false. An unresolved permission is unknown and grants nothing.
- A safety-relevant unknown blocks new starts and requests refresh; it does not manufacture an emergency percentage.
- Historical low readings can establish **exhaustion risk**, with age and reset qualification. The resulting brake is labeled risk-based, never “0% left.”

`floor(this)` uses 1% only when another account has confirmed admission headroom above its own wait/leave threshold; otherwise 2%. Compute that initial headroom set without using `floor(this)`, avoiding circular eligibility.

For the standing plan, `until` means “warning/leave transition is due.” The actuator then supplies the warning, drain and any emergency sequence. Earlier eligible steps can still cause a priority pull.

**Re-entry without markers**

For every nonlive target:

```text
left > max(leave, warn_pct) + (warn_fast_pct - warn_pct)
```

Thus a floor account needs more than 3% left; Steven with a 52% line needs more than 53%. The strict comparison avoids immediately returning to an account left at a possible warning line.

This differs from today’s target admission for preserved-space accounts. It is an **intentional replay difference**, not something to hide as agreement. It introduces no new margin number: it uses the existing warning parameters.

**Current step and retained facts**

At each evaluation:

1. Read one coherent input frame: plan revision, cached meter observations, clock, live account, live runs and switch-log prefix.
2. Resolve scopes and expand templates.
3. Derive entry observations from successful, correlated switch-log events.
4. Apply active holds, explicit requests/pins and the plan’s foreign-switch policy.
5. Evaluate steps in order, using current measurements and nonlive admission.
6. Return current named step, desired target, transition phase, reasons and unresolved inputs.

No stored cursor, `done`, “spent this week” or marker exclusion participates.

Necessary stored facts:

| Fact | Why retained; why it cannot become stale policy |
|---|---|
| Plan revision and attributed instructions | These **are** policy. Ends are reevaluated against the clock and measurements. |
| Switch-log operation ID, step name, revision and entry-observation ID | Immutable evidence of an actual transition. Never asserts current eligibility. |
| Relative-line anchor | Its meaning is historical by definition. Scope ends at its specified reset/time; a later entry uses a later event. Missing evidence gives unknown. |
| Order IDs and delivery receipts | Prevent duplicate save/emergency delivery; keyed to account, entry event and applicable policy fingerprint. Reconcile/withdraw on reset, refill, line change or account change. |
| Emergency start and selected pause | An execution fact needed after a crash, not a percentage or eligibility marker. Before further action, reevaluate current measurements and policy. |
| Stop outcome | Reconcile with actual switcher/fleet status; never assume a recorded stop means the fleet remains stopped. |
| Indexes/caches | Disposable; identified by source hash/prefix and revision. Invalid input identity invalidates them. |

The switcher log needs an additive, nonsecret operation/decision ID. Existing timestamp-window attribution is insufficient for an unconditional promise of correct ownership.

**Reader and status contract**

Keep `account_usage.py` as the only level reader. Use `read_now()`, `week_left_for()` and the existing Codex/GenAI readers. Its documented shared read interface is `account_usage.py:41`.

Required additive changes **inside that reader**:

- expose typed load/collection outcomes instead of collapsing unreadable and empty;
- publish cached structured Codex and GenAI observations through the existing collection path;
- let `account_lines` format that snapshot without calling a slow external tool;
- preserve the actual measurement timestamp, source, reset and failure cause;
- distinguish GenAI absent locally from an unsuccessful remote lookup.

The new CLI never invokes polling. Existing collection can continue independently; its credential-handling internals are not duplicated.

Every status includes these labels, even if a source is empty:

```text
system LEFT=… reset=… age=…; lukas LEFT=… reset=… age=…; steven LEFT=… reset=… age=…
codex LEFT=… reset=… age=…; jpl-genai LEFT=… reset=… age=…
```

Unknown reset/age prints explicitly. Absent GenAI prints `EMPTY(not installed here); reset=NA age=NA`, not 0%.

**Return values and exits**

Every result has a tagged outcome:

```text
VALUE(value, unit, observation_id, measured_at, reset_at)
ZERO(unit, observation_id, measured_at, reset_at)
EMPTY(reason)
COULD_NOT_LOOK(component, reason)
FAILED(component, operation, reason)
```

`UNKNOWN` conditions retain these underlying causes. “No live runs” is `EMPTY(live_runs)`, not `ZERO(account_level)`.

Exit status is a bitset, preserving mixed answers:

| Bit | Meaning |
|---:|---|
| 0 | Successful operation, with none of the following flags |
| 1 | At least one requested result is an explicit numeric zero |
| 2 | At least one requested result is an established empty set/absent resource |
| 4 | Could not look |
| 8 | Attempted operation failed |
| 16 | Validation refused; nothing written |
| 32 | Concurrent writer or revision conflict; nothing written |
| 64 | Durability/commit uncertainty; inspect printed committed revision |
| 128 | Shadow/replay acceptance failed |

A successful mutation followed by a partly unreadable status can therefore exit `4`; stdout still says `committed=true`. Consumers must inspect the commit result separately from observation flags.

All return records and printed lines preserve the tags. No truthiness-based conversion of `0`, `[]` or `None`.

**Forecast**

Use the **same evaluator**, driven forward through events:

- threshold crossings under measured burn;
- scope starts/ends, clock windows and known reset times;
- requested switches and terminal waits.

Reuse `account_end.burn_of` for burn. Forecast all-model levels and any relevant model-specific level through `week_left_for`.

For each event, print:

- estimated time to warning;
- estimated time to a requested transition;
- execution time as `after drain; duration unknown` unless runs are already empty;
- source age, burn span and limiting unknown.

Whole-percent meters imply interval uncertainty. Without a verified rounding contract, treat a reported percentage as uncertain by up to one point. Run forecasts across those level intervals and the range of comparable observed burn slopes. Report the resulting interval as a **scenario range**, not a confidence interval.

Zero measured burn gives no burn-crossing ETA. Unavailable burn gives `UNKNOWN`; any actuator fallback estimate is labeled a fallback. Reset-to-100 is a forecast assumption only. No arbitrary simulation tick, iteration cap or forecast horizon is required: stop at the requested named event/reset, or report an unbounded wait/cycle.

Pool parts expire at the earlier of their usable window, reset or exceptional permission’s end. The allocator still controls pace.

**Commands**

`ap` denotes the proposed Python entry point. Every invocation accepts `--why`, `--owner-said`, `--by-card` and `--per-ruling`. Mutations share one validator and transaction path.

For compactness, the output column uses `M` for **one printed line containing all five account tuples above**. Examples use symbolic IDs/ETAs because no readings were supplied. Each output is at most three lines.

| Command example | Output: three lines maximum |
|---|---|
| `ap plan show --why "Inspect policy"` | `VALUE(plan=<complete canonical JSON on one line>)`<br>`M`<br>`undo: none; read-only` |
| `ap status --why "What happens next?"` | `VALUE(step=standing/system next=save-warning ETA=<range> drain=<known/unknown> pool=<parts,pace>)`<br>`M`<br>`undo: none; read-only` |
| `ap readings --why "Check measurement ages"` | `VALUE(observations=<sources, ages, burn ages and causes>)`<br>`M`<br>`undo: none; read-only` |
| `ap plan apply --template weekly-priority --order steven,system,lukas --why "Restore standard order"` | `VALUE(committed=true change=C1 standing-order=steven,system,lukas)`<br>`M`<br>`undo: ap undo C1 --why "Undo standard order"` |
| `ap step insert reserve --after standing/system --account lukas --leave 2pp --why "Add reserve step"` | `VALUE(committed=true change=C2 inserted=reserve)`<br>`M`<br>`undo: ap undo C2 --why "Remove added reserve"` |
| `ap step change reserve --until 'left(lukas)<=3pp' --why "End reserve earlier"` | `VALUE(committed=true change=C3 changed=reserve)`<br>`M`<br>`undo: ap undo C3 --why "Restore reserve condition"` |
| `ap step remove reserve --why "Remove reserve step"` | `VALUE(committed=true change=C4 removed=reserve)`<br>`M`<br>`undo: ap undo C4 --why "Restore reserve step"` |
| `ap step move standing/lukas --before standing/system --why "Change priority"` | `VALUE(committed=true change=C5 moved=standing/lukas)`<br>`M`<br>`undo: ap undo C5 --why "Restore priority"` |
| `ap line set standing/steven 35pp --until 'first_reset_after(steven,command_time)' --owner-said "Leave space for Steven too" --why "Temporary allowance"` | `VALUE(committed=true change=C6 leave=35pp end=<reset/UNKNOWN>)`<br>`M`<br>`undo: ap undo C6 --why "Withdraw allowance"` |
| `ap hold set maintenance --until 2026-11-24T15:00:00-08:00 --owner-said "Pause the engine" --why "Maintenance"` | `VALUE(committed=true change=C7 hold=maintenance end=2026-11-24T15:00:00-08:00)`<br>`M`<br>`undo: ap undo C7 --why "Release maintenance hold"` |
| `ap hold release maintenance --why "Maintenance finished"` | `VALUE(committed=true change=C8 ended=maintenance)`<br>`M`<br>`undo: ap undo C8 --why "Restore unexpired hold"` |
| `ap pin lukas --until 'leave_due(lukas) or first_reset_after(lukas,command_time)' --owner-said "That's how it should be" --why "Respect current selection"` | `VALUE(committed=true change=C9 pin=lukas)`<br>`M`<br>`undo: ap undo C9 --why "Release Lukas pin"` |
| `ap switch steven --when no-live-run --until 'first_reset_after(steven,command_time)' --owner-said "Switch when we can do so without losing anything" --why "Switch as soon as safe"` | `VALUE(committed=true change=C10 request=<id> execution=<ready/waiting/UNKNOWN>)`<br>`M`<br>`undo: ap undo C10 --why "Cancel request; completed switches are not reversed"` |
| `ap policy set account_end.warn_pct=2 account_end.warn_fast_pct=3 account_end.emergency_pct=1 --by-card "Pause? -> Sized from burn" --why "Set account-end policy"` | `VALUE(committed=true change=C11 policy=account_end)`<br>`M`<br>`undo: ap undo C11 --why "Restore account-end policy"` |
| `ap whatif --why "Compare Steven allowance" -- line set standing/steven 35pp --until 'first_reset_after(steven,command_time)'` | `VALUE(committed=false forecast=<changed pick, next event and range>)`<br>`M`<br>`undo: none; hypothetical copy discarded` |
| `ap undo C11 --why "Restore previous account-end policy"` | `VALUE(committed=true change=C12 reverses=C11)`<br>`M`<br>`undo: ap undo C12 --why "Reapply account-end change"` |

`step insert/change` also accepts window, scope, relative leave, warning-leeway and transition fields. `plan apply` can create one named temporary sequence atomically. `line set codex …` targets the Codex lane.

A removed/renamed referenced step, malformed condition or missing temporary end is refused before writing:

```text
FAILED(validation): standing/system is referenced by request R; retarget or remove R in the same transaction.
VALUE(committed=false revision=<unchanged>)
undo: none; nothing changed
```

No command waits for a live run to end. A switch command commits its request and wakes the executor. Undo cancels future policy effects; it cannot resurrect killed processes, recover spent quota or reverse an already completed switch.

**Validation, concurrency, history and undo**

Validation checks types/units, account and step references, acyclic macros, allowed lane targets, explicit temporary ends, unambiguous scopes, numeric domains and required terminal wait. It prints the exact repair.

Transactions:

1. Acquire a stable sibling lock file with nonblocking `flock`; never lock the replaceable plan inode.
2. Read current revision; apply mutation to a copy; validate the entire result.
3. Append and fsync an audit `PREPARE` containing actor, provenance, reason, old/new hashes, complete patch and inverse.
4. Write a uniquely named temporary file in the plan directory; fsync it.
5. Atomically replace the plan; fsync the directory.
6. Append audit `COMMIT`. Print the committed revision and undo command.

The journal stores historical facts, **not live rules**. Recovery matches the authoritative plan hash to prepared transactions. Failure after replacement reports the actual committed revision or explicit uncertainty; it never claims the old plan survived.

Two writers either serialize or receive an immediate conflict. Optional expected-revision arguments prevent unnoticed rebasing.

Undo applies an inverse as another validated transaction. It checks affected-field preconditions, preserving unrelated later changes. Conflicting later edits cause a refusal naming the conflict. No revision counter is decremented.

**Limits, dangers and evidence**

Every row below becomes field-indexed `evidence` data. No new policy number is supplied by Python.

| Fields | Danger guarded; evidence |
|---|---|
| Floors 1/2%; exhaustion evidence 1% | Zero strands the fleet; preserve an idle conversational margin. Existing rationale: `switching_plan.json:25`. Exhaustion evidence no longer becomes a numeric level. |
| Steven 52%, 48h | Lent-account crowding; owner/card and delegated interpretation: `switching_plan.json:14`, `switching_plan.json:16`. |
| Warning 2/3%, emergency 1% | Give saves time before exhaustion: owner/card, `switching_plan.json:42`, `switching_plan.json:43`. |
| Emergency eligibility 10% | Avoid destructive emergency behavior on substantially preserved accounts. Imported delegated cutoff; supporting boundary evidence is not inlined. |
| Save need 10 min | Size fast-burn warning for save completion. Imported delegated estimate; empirical support unavailable. |
| Burn window 45 min; minimum span 10 min | Balance recent load against whole-percent noise. Imported delegated choices; empirical support unavailable. |
| Burn staleness 20 min; ending poll 0.5 min | Avoid using an old slope near exhaustion. Imported delegated settings; empirical support unavailable. |
| Pause share .2; reserve .5%; bounds 20–180s | Allow state recording while limiting exhaustion exposure. Owner/card supports the policy; it does **not** establish a calibrated “under 10%” probability. |
| Episode clear 5 points | Avoid retaining obsolete save orders after refill. Imported delegated margin; empirical support unavailable. |
| Soft margin 2 points | Early publish notice: `switching_plan.json:49`. |
| Pull drain 7200s | Balance cache-preserving completion against a run holding the machine indefinitely. Supplied evidence: 724 runs, p95 122 min: `switching_plan.json:48`. Preserve initially; owner may set unlimited wait. |
| Reset lead 20 min | Advance publish notice before reset pull. Agent proposal: `switching_plan.json:51`; no stronger evidence supplied. |
| Near line 3 points; age 6 min | Demand fresher observations near a boundary: `switching_plan.json:55`; empirical support unavailable. |
| Window margin 10 min | Avoid landing after a lent window closes during a slow switch: `switching_plan.json:58`. No demonstrated latency bound supplied. |
| Beat 300s; ending repeat 60s | Ordinary monitoring overhead versus near-end responsiveness; existing engine documentation, `switching_plan.py:37`, `switching_plan.py:43`. |
| Notice freshness 1200s | Avoid permanent admission restrictions from a dead publisher. Existing `NOTICE_FRESH_S`; retain only as actuator-output freshness, never as policy expiry. |
| Switcher timeout 600s; poll timeout 420s | Bound blocked subprocess calls. Existing `run`/`meter_poll` settings; these timeouts do not prove the underlying operation stopped. Reconcile switcher journal/status before retry. |
| Dated ends | End delegated permission when the instruction says it ends; exception dates and reset end: `switching_plan.json:62`. |
| Codex 25%; dated release | Preserve personal allocation except the supplied release: census row 20. |
| Percentage domain 0–100 | Physical meter domain supplied in the task; percentages outside it are invalid observations. |

Remove the old seven-day exception cap: explicit ends already express duration. Remove marker-age, fixed pool-iteration and simulation-tick limits from the new evaluator. Reader-internal credential/probe limits remain with the reader and its existing configuration; they are not duplicated as plan rules.

**All 21 census rows**

Each row below is one invocation. Mutation commands use the common transaction/provenance path. Test names remain those in the census.

| # | One command, or retained component |
|---:|---|
| 1 | `ap step change standing/steven --leave 52pp --window 'within 48h after measured_reset(steven)' --owner-said "Up to 50% after a fresh reset only" --why "Import lent-account terms; 48h is delegated"` |
| 2 | `ap plan apply --template weekly-priority --name standard-2026-10-28 --order steven,system,lukas --initial 'lukas,system to 2pp; wait until 2026-10-28T13:00:00-07:00; system' --why "Owner's first standard plan"` |
| 3 | `ap policy set floors.switch_away_pct_left=0 floors.wait_pct_left=2 soft_margin_pct=2 standing/steven.leave=52pp --by-card "Floor -> Drain to 0%" --why "Historical card choice"` |
| 4 | `ap hold set owner-pause --until '<chosen end>' --owner-said "Pause the engine" --why "Owner pause"` |
| 5 | `ap plan apply --template allowance --name steven-extra-week --after-account system --trigger 'left(system)<=1pp' --account steven --leave 20pp --until 'first_reset_after(steven,command_time)' --owner-said "He has authorized using another 20%" --why "Historical leave-at-20 allowance; ends this week"` |
| 6 | `ap plan apply --template allowance --name steven-relative --after-account system --trigger 'left(system)<=1pp' --account steven --leave 'max(floor(this),entry_left(this)-50pp)' --until 'first_reset_after(steven,command_time)' --why "Use 50 points below entry; interpretation recorded"` |
| 7 | `ap pin lukas --until 'leave_due(lukas) or first_reset_after(lukas,command_time)' --owner-said "That's how it should be" --why "Adopt owner's hand selection"` |
| 8 | `ap hold set stop-switching --until '<chosen end>' --owner-said "STOP KILLING THESE WINDOWS NOW" --why "Brake unwanted switching"` |
| 9 | `ap plan apply --template temporary-priority --name system-then-steven-35 --order system,steven,lukas --leave steven=35pp --until 'first_reset_after(steven,command_time)' --owner-said "Current rule until the reset" --why "Open temporary budget and order"` |
| 10 | `ap step change standing/steven --leave-schedule 'America/Los_Angeles: overnight=25pp; Wednesday daytime=floor(this)' --hours '<explicit overnight and daytime intervals>' --why "Encode time-of-day line"` |
| 11 | `ap switch steven --when no-live-run --until '<explicit end>' --owner-said "Switch when we can do so without losing anything" --why "Safe immediate request"` |
| 12 | `ap switch system --when no-live-run --until '<explicit end>' --owner-said "Don't lose work. When you can" --why "Leave Steven safely"` |
| 13 | `ap plan apply --template handover --name system-to-lukas --from system --until-condition 'left(system)<=1pp' --next lukas --why "Switch to Lukas at system's line"` |
| 14 | **Not a plan command: stays with the drain/actuator.** Its tuning remains editable through `policy set`; the plan tool does not stop runs itself. |
| 15 | `ap plan apply --template temporary-priority --name SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20 --from 2026-11-20T16:45:00-08:00 --order system,steven,lukas --leave system=3pp,steven=3pp --window steven=always --until 2026-11-27T16:00:00-08:00 --end-at-reset steven --owner-said "Use up this account first" --why "Authorized next account and temporary lines"` |
| 16 | `ap switch lukas --when no-live-run --until '<explicit end>' --owner-said "Wind down that switch and get it done" --why "Execute pending handover without moving the leave line"` |
| 17 | `ap policy set claude.evening_reserve=none --by-card "Keep share for evenings? -> No, run to the line" --why "Make ruling executable"` |
| 18 | `ap policy set account_end.warn_pct=2 account_end.warn_fast_pct=3 account_end.emergency_pct=1 account_end.pause_share=0.2 account_end.pause_from_pct=0.5 account_end.pause_min_s=20 account_end.pause_max_s=180 --owner-said "Scale based on load" --why "Set warning and burn-sized pause"` |
| 19 | `ap status --why "Reevaluate Steven's measured refill"` — no unlock/edit command. Eligibility follows the new reading. |
| 20 | `ap line set codex 25pp --release-before-reset-on 2026-11-24 --owner-said "ALL should be used before the reset today. Otherwise preserve 25%" --why "Codex policy in the shared plan"` |
| 21 | **Not a plan command: stays with `slot_allocator.py set`.** `ap status --why "Show pool and pace"` displays its inputs and reported pace. |

Placeholders mark information the historical record does not supply. They are **not** accepted literal arguments. Commands with those placeholders must be concretized before execution. Row 5 reproduces the recorded leave-at-20 setup; the quoted “another 20%” alone does not establish that arithmetic. Row 3 is a historical test case, not today’s recommended floor.

**Boundary promises and planted faults**

The boundary page must say it accepts validated schema-2 data, existing-reader observations, switcher events, clock input and positively identified live-run observations.

It does not survive arbitrary disk corruption, malicious writers bypassing locks, lying meter timestamps, unlogged credential switches, a broken switcher, or uncooperative launch paths that bypass admission. It detects/refuses what it can; it cannot promise no lost work during emergencies, nor a measured probability of avoiding zero.

| Promise | One test name | Planted fault that must turn it red |
|---|---|---|
| Every active policy value comes from the shared document. | `one_policy_authority` | Change a skill/allocator constant and make it affect the decision. |
| Conditions preserve unknown under negation. | `unknown_is_not_false` | Implement `not unknown` as true. |
| Zero, empty, inability to look and failed operations remain distinct through output and exit. | `outcome_tags_survive_cli` | Collapse zero and unreadable to `None`. |
| Existing meter functions are the only level source. | `only_existing_meter_reads_levels` | Open a credential or probe a provider from `ap`. |
| Every status names every required account, left/reset/age. | `status_lists_all_left_reset_age` | Omit absent GenAI or print Codex used percent. |
| Invalid edits preserve the old document and name a repair. | `invalid_edit_preserves_plan` | Replace the file before validation. |
| Concurrent edits cannot lose a committed change. | `concurrent_edits_are_serialized` | Lock the replaceable inode instead of the stable lock file. |
| Crash recovery identifies committed revision and audit record. | `crash_commit_is_reconcilable` | Crash after rename and falsely report old revision. |
| Undo preserves unrelated later edits. | `undo_checks_field_preconditions` | Restore an entire old snapshot over later changes. |
| Warning exits cannot immediately flap back. | `nonlive_admission_prevents_flap` | Admit a target at its possible warning line. |
| Named identity survives reordering. | `step_identity_is_not_position` | Bind relative entry to array index. |
| Safe requests cannot race a new launch. | `safe_switch_interlocks_launch` | Release launch exclusion between final empty check and switch start. |
| A revision/hold change during arming cancels an obsolete act. | `act_rechecks_revision_after_arm` | Execute the pre-arm decision unconditionally. |
| Timed-out switches are reconciled before retry. | `timeout_does_not_imply_no_switch` | Retry immediately after timeout. |
| Forecast and live selection use the same evaluator. | `forecast_uses_live_evaluator` | Give the forecast its own priority implementation. |
| Unknown/reset predictions never become real quota. | `forecast_refill_is_not_measurement` | Feed predicted 100% into live admission. |
| Shadow cannot actuate. | `shadow_has_no_actuator_capability` | Give the shadow process a callable switcher. |
| Cut-over has one active executor generation. | `cutover_has_one_driver` | Let both drivers act after the revision change. |

The census test names are also boundary promises:

| Promise/test name | Planted fault |
|---|---|
| `census_lent_account_window_and_leave_line` | Read Steven’s window from `slot_rules.json`. |
| `census_fixed_priority_order` | Select soonest-expiring eligible account. |
| `census_set_floor_and_leave_line` | Apply only one field of the atomic command. |
| `census_hold_with_why_and_end` | Allow an ending hold to remain active indefinitely. |
| `census_one_week_allowance_ends_at_reset` | Reanchor the allowance to the next week. |
| `census_leave_line_relative_to_entry_level` | Anchor to command-time level instead of entry observation. |
| `census_pin_account_now_plan_does_not_fight` | Permit a priority pull through an active pin. |
| `census_temporary_order_and_line_until_reset` | Count exceptional budget after its end. |
| `census_line_by_time_of_day` | Evaluate Pacific hours as UTC. |
| `census_switch_now_when_no_run_is_live` | Treat unreadable runs as an empty set. |
| `census_use_until_pct_then_next` | Use `<` where the specified condition is `<=`. |
| `shadow_drain_is_not_the_plan_tools` | Have the planner call a process-kill operation. |
| `census_reorder_and_lower_line_until_reset` | Commit the new order without its new lines. |
| `census_no_rule_lives_in_prose` | Require an agent-read evening-reserve ruling. |
| `census_set_warn_and_emergency_numbers` | Keep a warning number in Python. |
| `census_refill_is_seen_from_the_meter_no_marker` | Reintroduce an old spent-account marker. |
| `census_codex_leave_line_in_the_same_plan` | Read an older Codex floor from allocator rules. |
| `status_shows_pool_pace_not_sets_it` | Have status change allocator concurrency. |

**Shadow, replay and cut-over**

Before shadowing, add a compatibility loader to the old engine. Both engines must consume the same authoritative plan and the same frozen observation frame. For the imported plan, the loader produces schema-1-shaped data **in memory**, without another rules file.

While the legacy driver acts, unsupported new policy features are available through `whatif`; they must not silently alter only the shadow interpretation.

Exact proposed commands:

```text
ap rollout shadow-start --why "Compare new decisions without acts"
ap replay --series /mnt/d/ClaudeWork/rimmandrake/account_usage/series.jsonl --from 2026-11-10T00:00:00-08:00 --until 2026-11-24T00:00:00-08:00 --legacy-context recorded --why "Replay two complete weeks"
ap rollout compare --shadow live --replay latest --why "Review picks, safety decisions and expected differences"
ap rollout cutover --report latest --why "Enable reviewed new driver"
```

Every command prints its result, `M`, and an undo/no-op line. Cut-over prints:

```text
VALUE(committed=true change=CUT driver=new; prior driver quiescent)
M
undo: ap undo CUT --why "Restore legacy driver"
```

Shadow mechanism:

- The authoritative legacy pass captures a frame after each read/poll and final recheck: observation IDs, time, plan revision, live account, live runs, burn input, switch-log prefix and legacy execution context.
- Both pure evaluators receive that frame. Shadow receives no actuator capability and writes comparison records only.
- Compare desired account, named policy reason, stop/start decision, admission restriction, warning/emergency phase and unknown causes.
- Compare **desired picks separately from actuator-deferred picks**; a live drain must not masquerade as disagreement in priority.
- Record expected differences explicitly: no fabricated blind zero, marker removal, stricter preserved-account re-entry, and newly executable Codex policy.

Replay mechanism:

- Reconstruct readings through the existing reader’s derivation functions, at recorded times.
- Run an **observed-trajectory replay**: use historical switches and live-run observations; do not pretend decisions changed history.
- Reconstruct the policy revision applicable then from archived revisions/change history.
- Feed historical marker/state facts only to the legacy evaluator.
- Missing live-run, state, policy or switch-log history marks affected comparisons `COULD_NOT_LOOK`; a quota-only replay is not a complete safety replay.
- Separately run synthetic census fixtures and planted-fault boundary tests. Those test counterfactual behavior; they are not historical evidence.

“Agree” means equal normalized decisions on frames unaffected by a documented intentional difference. An intentional difference passes only if its exact trigger and expected result are recorded in the report and its boundary test passes. No percentage threshold hides unexplained differences.

Cut-over requires complete required evidence, all boundary tests passing, no unexplained divergence, compatible rollback data, and verified launch interlocking.

Cut-over is one transaction changing `control.driver`. Both drivers share an execution lock and reread driver generation, revision, holds, live account and live runs after arming and immediately before acting. A running switch causes immediate conflict rather than a competing transition.

The launch gate must share exclusion with the final no-live check and switch start. The supplied files do not establish that integration; it is a cut-over prerequisite.

Undo changes the driver back using current compatible policy and freshly reconciled execution facts. It does not restore old markers or an old live-account assumption. Later incompatible policy changes must first be undone; the refusal prints that repair.

**E. Claims the pick rests on**

Paths below use `Utils/` for `src/RimMandrake/Utils/`. `★` means the pick would change materially if wrong.

| Claim | Evidence classification |
|---|---|
| ★ The existing reader and drain/account-end components have no recorded plan-side failure in this census. | **Read in the files:** `census.md`, final paragraph under “What the census says.” This is recorded history, not proof of correctness. |
| ★ Existing switching stops Claude processes, making actuator preservation valuable. | **Read in the files:** `Utils/switching_plan.py:26`; `skills/rimflow-operations/SKILL.md:8`. |
| Today selects the first eligible account in a fixed order. | **Read in the files:** `Utils/switching_plan.py:7`; `Utils/switching_plan.json:10`. |
| Standing order is Steven, system, Lukas. | **Read in the files:** `Utils/switching_plan.json:5`. |
| Steven’s standing line/window are 52% and 48h; the latter is delegated interpretation. | **Read in the files:** `Utils/switching_plan.json:13`, `Utils/switching_plan.json:16`. |
| Floors are 1%/2%; old blind policy converts an unavailable near-empty reading to zero. | **Read in the files:** `Utils/switching_plan.json:22`, `Utils/switching_plan.json:25`. |
| Account-end’s fourteen numbers are already data. | **Read in the files:** `Utils/switching_plan.json:27`. |
| The dated exception declares system, Steven, Lukas with system 3% and Steven 5%. | **Read in the files:** `Utils/switching_plan.json:62`. |
| Pool policy is intended for allocator pacing. | **Read in the files:** `Utils/switching_plan.json:60`. |
| Existing manual-switch respect depends on transition attribution. | **Read in the files:** `Utils/switching_plan.py:20`. |
| Existing brake is a bare HOLD file. | **Read in the files:** `Utils/switching_plan.py:39`. |
| ★ The meter offers a shared cached reader and recorded series. | **Read in the files:** `Utils/account_usage.py:38`, `Utils/account_usage.py:41`. |
| Existing sources include live/remote/vault and carried/unknown observations. | **Read in the files:** `Utils/account_usage.py:15`. |
| ★ All consumers can be migrated to the shared loader/admission decision. | **Assumed.** Allocator, launcher and Codex admission implementations are not supplied. |
| ★ Switcher logs can be extended with reliable operation IDs and entry references. | **Assumed.** Switcher implementation is not supplied. |
| ★ The Linux filesystem used for the plan supports the required lock, replace and durability behavior. | **Assumed.** Must verify on the actual plan filesystem. |
| Two full weeks of usable readings exist. | **Assumed from the task’s statement.** Series contents were not supplied. |
| Full historical policy/run/state context exists for replay. | **Assumed and unverified.** Missing context blocks full acceptance. |
| Common-plan evaluation and bounded local transactions meet subsecond latency. | **Assumed performance target.** Benchmark on the machine; no unconditional I/O latency guarantee. |
| A relative 50% instruction means a 50-point drop. | **Assumed interpretation**, explicitly recorded in that command. |
| “Just before Codex reset” has no supplied recurring duration. | **Read in the files:** census row 20 supplies changing instructions but no duration. |

## Outside this slice

- Actual readings, series contents, switcher logs and historical plan revisions.
- `claude-account`, its lock/journal contracts and support for correlated decision IDs.
- Launcher/admission paths needed to make “no live run” race-free.
- `slot_allocator.py`, `slot_rules.json`, Codex admission/advice consumers and their exact interfaces.
- `account_handover.py`, outstanding timers, current HOLD contents and login-watch failover behavior.
- The referenced account-end/drain boundary evidence, including support for delegated numeric choices.
- Exact historical pause ends, overnight/daytime hours and the meaning/arithmetic of the extra allowance.
- Codex’s recurring pre-reset release interval.
- Remote GenAI discovery and measurement timestamps.

These gaps do not prevent choosing the design. They prevent claiming a completed replay or authorizing live cut-over.