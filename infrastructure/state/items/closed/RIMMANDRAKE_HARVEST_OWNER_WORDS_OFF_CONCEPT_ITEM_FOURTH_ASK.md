## spec
Found 2026-11-16 by RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK. The owner asked for the position-and-slope rule on Gimme Some Slack on
2026-11-09 ("You're not matching both position and slope. That's what it takes.", OWNER:1794242437721637229) and four more times on 2026-11-16;
it never became a bar of 0.1.0 (locked 2026-11-13). Cause in the pipeline's machinery: `designer_stage.owner_uncited()` (the Designer's "his words
not yet taken in" feed, which also freezes and staleness-checks its stages) reads only OWNER events whose text names the concept's OWN item
(`stage.json` item `GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS`). His words recorded on the mod's other items (build items, fix items, sittings:
here `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN`, `RIMMANDRAKE_FIX_SLACK_CORD_ENDS_OWNER_CAUGHT_TWO`) are invisible to it. Measured 2026-11-16: the
GSS feed holds 1 tsn and not his 2026-11-16 "hard wired" ruling (OWNER:1794839121624014370).

Not fixed in the run that found it: the fix is not yet known to be safe. Widening the feed changes `owner_feed()`'s sha for every concept, which
marks accepted Designer stages stale and can relaunch Designer runs (spend) on every mod; and mapping an item to its mod has no field today (a
title or id heuristic would pull in unrelated items). Needs a design call: a `mod` field on items, or a per-concept list of sibling items, and
whether a sibling's words should feed staleness or only a non-freezing "owner words elsewhere" list the Designer and the lock read.

## verify
Acceptance test (watched FAIL on base 9472c5cbdf, 2026-11-16: exit 1):
`python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import designer_stage as D; u=D.owner_uncited('.', 'GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS', 'design/concepts/GimmeSomeSlack') or []; sys.exit(0 if '1794839121624014370' in u else 1)"`
exits 0 (or the same assertion against the new mod-wide harvest function, if the fix adds one instead of widening owner_uncited). It stays valid
only while record.json and tree.json do not cite OWNER:1794839121624014370; a fixture ledger is better once the fix exists.

## criteria
Every OWNER said/card event on any item of a mod that its concept's record.json and tree.json do not cite is listed to the Designer and to the
lock check; no feed change relaunches a Designer run without a recorded decision.

## refs
file: src/RimMandrake/rimflow/designer_stage.py
