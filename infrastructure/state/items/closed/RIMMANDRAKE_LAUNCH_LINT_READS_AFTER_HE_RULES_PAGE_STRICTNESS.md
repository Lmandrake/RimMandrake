# RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS

## What the card said

<!-- answered 2026-11-19T13:27:48Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Each piece of pipeline code now has a one-page list of promises. A promise says what the code always does. A blind reader and Codex each say 21 of 35 old review complaints break a promise. The earlier analyst said 4. Most of the 21 are rare failures, such as a crash during a crash. What do we do with a rare failure that breaks a promise?
**Picked:** Page says 'not handled' (Recommended)
**Its description:** Why: keep the code small and stop the review cycle. The page lists each rare failure it does not survive. No fix is built. Cost: those failures stay possible, and you must trust the list. Recommended: fixing all 21 is the review cycle again by another door.
**Other options:** Fix every one · Fix only what happened
