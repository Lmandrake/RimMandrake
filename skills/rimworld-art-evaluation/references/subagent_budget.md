# Subagent budget for art review and live proof (owner, 2026-10-23: "I am very upset")

Why: on 2026-10-23 helpers on this stream hit the account's Opus session limit by mid-morning. Measured from
the transcripts on disk (`scripts/helper_cost.py`, deduped by message id; a first version double-counted streamed
records and overstated everything ~2x): the worst earlier Opus helper ran **452 messages and re-read ~227M cached
tokens**; the three art helpers of that afternoon ran ~85-111 messages and 15-19M cache reads each; the pipeline's
own `claude -p` judge calls (not in any helper's total) were **90 runs, 64 of them one prompt comparison** (4-5
variants x the same set), and are the likeliest single biggest Opus spend, unmeasured. Cost ~ messages x context
(~500k per message), so long helpers and polling turns dominate, then image judge calls.

## Rules for whoever spawns (the orchestrator)

1. **Every brief carries a hard budget:** `max_turns` (default **30**, extend to 60 only by a named reason; mean context was ~488k tokens per turn, so 60 turns is ~29M cache reads per helper) and `max_judge_calls` (**no default: state the planned count**; incumbent+2 variants x 12 items is already 36 calls before retries or GPT escalation),
   and "stop and report with a resume file when either is spent". No budget in the brief, no spawn.
2. **Fresh helper per batch, never one long-lived helper.** Every turn re-reads its whole context on
   every turn; end it with a one-line resume pointer and start a new one. Never SendMessage-resume a helper that
   has already run past budget.
3. **At most ONE Opus helper at a time, three helpers total.** Sonnet drives; Opus only judges or designs, and a
   judge call is a script step, not an agent turn.
4. **A loop is a script, not an agent.** Per-subject judging, regen filing, install and digest writing run as one
   foreground driver (`art_eval.py` plus a driver file) the helper launches once and reads the result of. A helper
   that issues one Bash call per picture is the defect.
5. **No polling turns.** Waiting is `Monitor` / `waitfor.py` or a final report; never a turn per check. Watchdog
   (`belt_watchdog.py --watch`) goes into a Monitor, not a turn loop.
6. **After each helper reports, the orchestrator measures its cost** (`python3 skills/rimworld-art-evaluation/scripts/helper_cost.py <task.output>`) and writes one line to the day's note: turns, output tokens, cache-read tokens. The ~100M cache-read / ~150k output daily figures are EMERGENCY ceilings, not budgets; plan prospectively from rule 1.
7. **Quota first.** Before launching judge-heavy work, run one tiny `claude -p` probe; a 429 / session-limit means
   do not start. A session-limit error is NEVER recorded as a verdict (the runner must not write it as a final
   decision); the run is left resumable.

## Rules for the judging itself

8. **Judge each picture once per (image hash, model, prompt/template version, card facts).** Cache the verdict; a re-run skips it. Re-judge only
   when the prompt version changes or the owner overrides.
9. **One subject per picture**, with a pool-count line on the card (a whole pool as one card let one bad variant sink
   the kept good one, then had to be redone).
10. **Batch pictures into fewer judge calls** where the template allows (several same-class pictures per call, each
    returning its own verdict), and Sonnet pre-screens only to *skip obviously fine art*; "Opus scores first" is the
    owner's rule and is not relaxed here without him.
11. **Prompt comparison budget: incumbent + at most 2 variants, regression set <= 12 known verdicts, ONE round per
    order.** A second round happens only after the first adopted or rejected something and a new batch has landed.
    Adopt only on fewer false accepts, never on a rising agreement score alone.
12. **Don't spend judge calls on art that is not in play:** check reachability and `artpipe_state.py find` before
    judging; skip KEPT art unless a walk or the owner flagged it.

## Brief footer to paste into every art / proof helper

> BUDGET: max_turns=<N>, max_judge_calls=<M>. Run loops as ONE driver script, never a turn per item. Wait with
> Monitor, never polling turns. At budget (or on any 429/session limit) stop, write a resume file naming the exact
> command to continue, push, and report in <=12 lines. Do not record limit errors as verdicts.

## Known gaps (GPT review 2026-10-23; filed as HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY)

These rules are instructions, not enforcement. Owed: one launcher for helpers AND `claude -p` judges that validates
the budget fields, reserves allowance before each call from a shared account/stream ledger (so parallel judge
processes count, not just helpers), and refuses at zero. `helper_cost.py` measures after the fact only, counts usage
records not true turns, omits plain input tokens and external judge calls, and cache reads are not the quota.
Interrupted live observations are UNMEASURED; valid earlier rows stay.
