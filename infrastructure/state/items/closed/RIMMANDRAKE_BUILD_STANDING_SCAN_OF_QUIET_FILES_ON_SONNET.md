# RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET

## What the card said

<!-- answered 2026-11-20T02:03:02Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Thu Nov 19, 5:54 PM PST. Four choices finish the review method. Two rows I will add without asking, because you already stated them: a finding is significant when it is measured, or predicted with a concrete case (this input, this wrong result), to break a promise or cause a failure; and a ticket must cite a broken promise or a failure, one ticket per source event. First choice: today's rule text says a separate builder fixes what a reviewer finds. In the old loop the reviewer fixed it, with the whole file in context. (Hard to read? Type STE, Binding or Both for a rewrite.) Who fixes a significant finding?
**Picked:** The reviewer, on the spot (Recommended)
**Its description:** Why: the finder holds the whole file and its own reasoning, as in the old loop you found fast and good. The reviewer writes a new test, sees it fail, fixes, sees it pass. Costs: the same agent finds and fixes, so the test is the only independent check. Recommended: it removes the ticket handoff that loses context.
**Other options:** A separate builder · Reviewer if small, builder if large

**Question:** After a significant finding is fixed, the old loop left the file dirty until a fresh blind reader passed it. Your rule today says one round. Measured: on quiet mod files the reread found 0 new bugs; on fast-changing pipeline files 8 of 11 and 9 of 15 later claims pointed at lines the last fix had just written, mostly polish. Under today's rule polish is noted and not fixed. What checks a fix?
**Picked:** One blind reread of the fix
**Its description:** Why: the old way, which caught fixes that broke something else. A fresh reader reads the fixed file once; significant findings are fixed, minor ones noted, then it ends with no third read. Buys: a second mind. Costs: a second run per fixed file, and fresh fix lines draw the most claims.
**His words:** (2) Precisely one, yes. If it too finds a significant change and fixes it, the file is flagged but left alone. Flagged files are examined to see if we need to change the definition of significant or there is a real instability, but this is done infrequently, say weekly or so.
**Other options:** The new test only (Recommended) · Blind reread for mod content only

**Question:** The old standing scan read files nobody was working on and found real bugs: about 0 or 1 per mod file on first read. It worked on quiet files (median 0.75 commits in the week before a review) and failed on files being rewritten (11.3 commits in that week). Today 3,580 code files have never been reviewed and no scan job exists. Should a standing scan run again?
**Picked:** Quiet files only, when idle (Recommended)
**Its description:** Why: that is the measured condition under which the old scan converged and found bugs. A helper reads files unchanged for 7 days or more, mod content first, when no mod step needs the machine. Costs: tokens whenever it runs, and a 7-day line to defend. Recommended: it brings back the bug-finding without the endless rounds.
**His words:** (1) yes, on Sonnet 5.5, and the Python to visualize the clean/dirty codebase is ressurrected and included on the standard suite of Desktop visualizations to track. (perhaps this should become tabs in a standing browser actually, along with FLEET_NOW and MATURATION_NOW in their own windows).
**Other options:** No scan for now · Scan a mod once, before it ships · Scan everything, as before

**Question:** Minor findings now go on a polish list beside each page and are not fixed. You asked how such a list is ever used without becoming the same endless loop. Who may take a line from a polish list?
**Picked:** Nobody; it is a record
**Its description:** Why: the list exists so a finding has somewhere to go that is not a ticket. Buys: zero polish work, ever. Costs: real small improvements are never made, and a list nobody reads may stop being written carefully.
**His words:** (3) for now. We will later do experiments on Polish if we can/must. We're not close to polishing anything right now
**Other options:** Three doors only (Recommended) · You only, after a pass

**Owed by this card** (the close names where each was done or filed): needs the machine
