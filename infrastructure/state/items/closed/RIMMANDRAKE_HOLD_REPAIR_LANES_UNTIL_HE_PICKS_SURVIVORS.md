# RIMMANDRAKE_HOLD_REPAIR_LANES_UNTIL_HE_PICKS_SURVIVORS

## What the card said

<!-- answered 2026-11-19T13:27:48Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Nine repair runs were stopped at 8:24 PM yesterday when you stopped the review cycle. One of them repairs the launch permit. A launch permit is the record that lets a run start. Two faults are still in the code: the all-on switch does not update the permit, and a launch with no permit reports success and leaves a ghost run. A failing test for both is ready. Which stopped runs restart?
**Picked:** I read all nine first
**Its description:** Why: you choose with full facts. A helper writes one line per run: what it fixed, what is left, and whether a real fault remains. You pick from that. Cost: about 15 minutes before anything restarts.
**Other options:** Only the permit repair (Recommended) · None restart

## What the card said

<!-- answered 2026-11-19T13:48:06Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** [owner-asked] You chose to read the nine stopped repair runs before any restart. Six already finished last night. Three are left. Run A repairs the launch permit, the record that lets a run start. One fault is proven: the permit stays removed after a timed all-off ends, so nothing can launch. Run B writes random-input tests for the coverage judge; 6 of 8 are unwritten. The coverage judge decides if a mod's tests cover its design. Run C guards publishing against two rare timing failures, and has one built patch that is not landed. Which of the three restart?
**Picked:** All three restart
**Its description:** Why: nothing is left half done. Cost: three helper runs, and C's timing guards are the rare-failure fixes you ruled against this morning.
**Other options:** A only; close B and C (Recommended) · A and B · A, and land C's patch
