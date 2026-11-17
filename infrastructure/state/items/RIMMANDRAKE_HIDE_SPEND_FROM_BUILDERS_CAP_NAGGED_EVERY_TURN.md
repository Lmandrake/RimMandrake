# RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN

Owner, 2026-11-16 ~6:25 PM PST, watching a live builder: *"I don't like how you're telling the agent how much it's spent. This has been shown to reduce their creativity and obsess on cost savings..."* · *"You're telling it constantly"*

## spec

Every claude run launched with `--max-budget-usd` gets a harness reminder on every turn (`USD budget: $used/$total; $remaining remaining`, transcript attachment type `budget_usd`; MEASURED 143 in the Gimme Some Slack certificate fixer's transcript, 2026-11-16). No agent we launch is told its spend, its cap or what remains: not by the harness flag, brief text, footers, hooks or resume prompts. The hard per-run spend stop stays (owner 2026-11-12), enforced from outside the agent by a no-token watchdog that reads the run's transcript usage and stops the run resumably at the cap. People still see spend, in weighted tokens, on run records and the status page.

## refs

file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/role_launch.py

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_spend_blind_agents` (written first by the builder, watched failing on the base). Live: one tiny real detached run after the change has 0 `budget_usd` attachments in its transcript and its run record still carries the cap.

## criteria

- Every launcher's command line and prompt/footer carries no spend, cap or remainder figure, and nothing that makes the harness inject `budget_usd`.
- The outside watchdog stops an over-cap run, leaves an under-cap run alone, and never stops a healthy run on an empty, missing or malformed transcript.
- A mutant that re-adds the flag is caught by the selftest.
- The watch window no longer labels harness reminders "AGENT SAYS".
- The ruling is in `design/RimMandrake/standing_rulings.md` with his words and date.
