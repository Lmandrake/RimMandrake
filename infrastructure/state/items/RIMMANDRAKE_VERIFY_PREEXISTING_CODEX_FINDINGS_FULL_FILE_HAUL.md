## spec
The ten FULL-FILE Codex reviews of the 2026-11-17 offline landings (D:\ClaudeWork\rimmandrake\conductor\remote_landings_20261118\codex) reported pre-existing flaws in the files they
read, outside each commit's promise. This audit verified only what bore on the commits; these were NOT run and are not
yet believed: coverage_judge.entry_hashes collapsing None/""/"{"/"null" to one hash, and a recorded round hiding an
unmeasured charge (dbd5c89339 review); ExplosiveKnockback validation: a failed final census reading "nothing moved",
an unchecked Settings(enabled=False), an incomplete settings snapshot, an unchecked final load(base), missing inAir
read as an empty window (9a437178d8 review, 2-6); wrapup.check_clone on a failed git call and an unreadable
BRIDGE_SHARED.json read as free (cf4a8a4d02 review, 3-4); maturation journal read catching every OSError as absence
(13db68e8ed review, 3); seat_sync landed_twin on empty union shards and failed blob reads, _check_displaced on a failed
rev-parse (84ca416f3a review, 3-5); designer_stage stage 5 rejecting a package closed from another clone
(895f0834c3 review, 3); GraffitiFuzz cumulative Cases (unreachable: Program.cs calls Run once per process).

## verify
Acceptance test: none, a verification census: each finding is reproduced by running it, then filed with its own failing case or dropped with the probe.

## criteria
- Every listed finding is either filed with a watched-failing acceptance test or recorded as not reproduced.
