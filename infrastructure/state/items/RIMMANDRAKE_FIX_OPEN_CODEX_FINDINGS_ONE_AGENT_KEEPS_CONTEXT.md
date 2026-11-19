# RIMMANDRAKE_FIX_OPEN_CODEX_FINDINGS_ONE_AGENT_KEEPS_CONTEXT

## What the card said

<!-- answered 2026-11-19T03:55:25Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Wed Nov 18, 7:47 PM PST. Today's Codex reviews produced 96 tickets: 3 dangerous (all fixed, none ever fired), 49 minor, 41 polish. Every dangerous one came from a file's FIRST review; later rounds were 70 to 90 percent polish, yet each finding was filed as a repair ticket and fixed tonight. 'Problem' here means a defect an ordinary day here can reach, that gets a record, a gate, a commit or spend wrong. 'Polish' means it needs something this estate does not produce: a failure during a failure, a malformed file we never write, a split-second race, or a stricter test. How should a Codex review finding be sorted when it is filed?
**His words:** Give it two more rounds of this. If it's staying constant in # but higher and higher in polish, we put in the filter
**Other options:** Problem needs a named input (Recommended) · A second agent sorts each one · Only work-losing ones are problems · Keep filing all as problems

**Question:** Wed Nov 18, 7:47 PM PST. Separate from how findings are sorted: how many times is a repair reviewed? Today each repair gets a whole-file Codex review, its fixes get another whole-file review, and so on until one comes back clean. The analyst found the first review of a file is where the real problems were, and that two fixes made in later rounds introduced small new bugs of their own. A 'recheck' below means Codex reads only whether the fixes for its own findings landed correctly, not the whole file again. How many review rounds should a pipeline repair get?
**His words:** I already answered this
**Other options:** One review, one recheck (Recommended) · Review until no problems remain · One review only, no recheck · Keep going until clean

**Question:** Wed Nov 18, 7:47 PM PST. Of the 96 Codex-review tickets, 24 are still open: 11 minor problems, 12 polish, and 1 unverified list. Two of the open ones are not polish and are handled either way: the uncounted mod-advance refusals (a fixer is running now) and publish checks that may read another helper's unsaved edits (no builder yet). 30 of the 49 'minor' verdicts are the analyst's guess from ticket text, not a code reading. What should happen tonight to the open tickets?
**Picked:** Fix all 24
**Its description:** Why: they are already filed with tests, so finishing them leaves nothing behind. Costs: the 12 polish fixes each trigger their own review, which is how the list kept growing tonight.
**His words:** (3) fix them all with a single agent that keeps context so it can pound them all out and hopefully introduce fewer mistakes as it does.
**Other options:** Fix minor now, park polish (Recommended) · Park everything but the two · Re-read the 30 guesses first
