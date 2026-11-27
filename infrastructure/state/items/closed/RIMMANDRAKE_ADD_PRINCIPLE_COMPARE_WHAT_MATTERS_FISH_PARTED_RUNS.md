# RIMMANDRAKE_ADD_PRINCIPLE_COMPARE_WHAT_MATTERS_FISH_PARTED_RUNS

## What the card said

<!-- answered 2026-11-27T18:35:27Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** You ruled that a "did it come back the same" test must not demand exact identity: fish-shadow timing and the exact curve a Gimme Some Slack line takes do not matter. One fact for the wording: the test that tripped was not a picture comparison. It compared the game's random-number draws and state between runs from one save, and the fish shadows broke it. So the principle should cover any comparison: pictures, saved state, random draws, files. I would add two guards. Exact identity stays right where identity itself is the promise (a copied file, a build hash). And a looser test must say what may differ, or "it does not matter" can hide a real regression. It will live at the top of the CHARTER beside the Principle of Impactful Evidence, with a pointer in the root rules file, as you chose for that principle on Nov 23. (Hard to read? Type STE, Binding or Both for a rewrite.) Which sentence should the principle be?
**Picked:** As strict as the harm it guards (Recommended)
**Its description:** Why: one rule for every test, game or tool. "A test is as strict as the harm it guards, and no stricter: it names what must match and ignores a difference that costs nothing." Buys: covers pictures, saves, random draws and pipeline checks. Costs: "harm" is a judgement per test. Recommended: it generalizes and is still one sentence.
**Other options:** Fail only on what the player notices · Every test says what "same" means
