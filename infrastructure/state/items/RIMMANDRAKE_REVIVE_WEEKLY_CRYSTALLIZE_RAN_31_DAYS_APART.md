# RIMMANDRAKE_REVIVE_WEEKLY_CRYSTALLIZE_RAN_31_DAYS_APART

## spec
By his card of 2026-11-23 ("Stop it, weekly does it" and "Weekly, in one report") the weekly Crystallize pass took two
jobs: it improves role files and skills, and it carries the skill and tool proposals
(`design/RimMandrake/standing_rulings.md` §The weekly Crystallize pass improves the agents). Measured 2026-11-23:
- It runs and applies edits. The run of 2026-11-19 (`D:\ClaudeWork\rimmandrake\conductor\crystallize_2026W47\CYCLE_REPORT.md`)
  edited CLAUDE.md and standing_rulings.md (`3b90ed9505`), merged 50 lessons into 10 (`eeb532cee4`) and culled 38
  handoffs. A run of 2026-11-21 edited 21 role files (`2ef5cf2273`).
- It is not weekly. The run before it was 2026-10-19 (W43): 31 days.
- Nothing schedules it. His words, 2026-11-10: "Let's just turn this into a nag at the top of every Lodestar managed
  project client start the same way it shows Burning items, rather than a scheduled job with demands."
- The nag comes at 14 days, and on Archmagi it can never show: `~/dev/Lodestar/bin/crystallize_due.py --json` reads
  `known: false` (no private store here), so it prints nothing.

The Conductor decides the shape: a weekly run for this project, or a reminder that reads the reports in
`D:\ClaudeWork\rimmandrake\conductor\crystallize_*` and shows at 7 days. The words of 2026-11-10 bind the Lodestar nag.

## verify
`python3 ~/dev/Lodestar/bin/crystallize_due.py --json | python3 -c "import json,sys; sys.exit(0 if json.load(sys.stdin)['known'] else 1)"`
Seen failing on Archmagi 2026-11-23 (exit 1). A weekly run needs a live promise on its report instead.

## criteria
On Archmagi, a Crystallize pass more than 7 days old is seen by a session without anybody remembering it.
