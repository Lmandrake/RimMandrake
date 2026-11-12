# BROADEN — HARNESS_REPAIR_CAUSE_8135787B (2026-11-11, CLAUDE_STEVEDESKTOP_OFFLINE6)

Asked GPT (gpt_consult.py --codex wsl) with the statement, the three fixes' diffs and what I had tested.

## The question

You are reviewing a harness repair in a RimWorld mod test harness. Statement the work must satisfy:
- the class is recorded on the item (note) with its evidence before the fix;
- `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_8135787B` exits 0 on a job run at the fix's sha (job DONE, rows carry PASS/FAIL/SKIP, none carries this cause);
- the negative control `retest.py passed J20261106T011656Z-15b610 HARNESS_REPAIR_CAUSE_8135787B` exits 1.

The sighting: a full FlowWorks sweep (modcheck run --drivers on) on SteveDesktop. Driver sprinkler_live.py ran on the run's own long-used map after thirst_live.py had advanced ~15 game-minutes of ticks; it died rc=1 in 57 s with clockgate.GovernorStop "safe_advance stopped after 60 of 125 tick(s): starving: food category Starving" (a colonist at Food 0). So two thirst rows T21/T22 read "no sprinkler_live.py result at the current mod hash" = cause driver_undelivered, and the thirst chain had no verdict. Three other chains (flow_map_controls_six, pit_access_gear_ladders, suspension_bridges_and_covers) were also held under thirst's cause because retest.split_rows' UPSTREAM regex matched "an UNMEASURED component ended this chain earlier", which suite.py writes for the chain's OWN earlier row (here a genuine 'live check owed' GAP).

Fixes (diffs attached): (1) validation_core.site_calm, the calming step every standalone driver calls, now tops up Food of any colonist under 0.25 (the suite's own bland_world.feed_colonists rule; thirst left alone) in its own try block. (2) retest.UPSTREAM matches only cross-chain "upstream failed". (3) testq.py submit run off the dispatcher host (Archmagi) used to write into a local queue no dispatcher reads and print "pending"; it now forwards over ssh to the dispatcher's clone, sha checked locally.

What I tested: offline selftests with fake bridges (site_calm feeds only the starving colonist, Food only, even when another calm piece throws; mutation of the feed makes it red); retest selftests (own-GAP chain not held under another's cause; own undelivered row still held; mutation red); the negative control on the real sighting still exits 1 and now only thirst is held; testq forward selftest with a fake ssh. The live re-run is queued on Archmagi but the lane is paused by the owner until 2026-11-19, so the 'exits 0' criterion cannot be shown yet.

Question: what would a real user of this harness (someone new, someone experienced, someone trying to break it, a messy real case) try that I have not? Which failure modes of these three fixes are most likely to show up in the actual re-run or in ordinary use (e.g. hunger arriving mid-driver rather than at calm time, other drivers sharing the map, forwarded submit edge cases)? Name the one or two most revealing checks I could run OFFLINE now. Be concrete and brief.

## The answer (verbatim)

The biggest remaining risks are:

- **Hunger after calming.** A pawn just above Food 0.25 stays untouched and may starve during a long driver. Another driver, or a newly introduced pawn, can also invalidate the calm-time state.
- **Forwarding the wrong revision.** If `submit` accepts `HEAD`, branches, or abbreviated SHAs, the local check can approve commit A while the dispatcher resolves the forwarded argument differently. Appending `--no-sha-check` removes the remote check.
- **Ambiguous submission failure.** SSH can disconnect after the remote job is queued. A retry may create a duplicate. Also, dispatch-clone paths beginning with `~/` bypass quoting, so spaces or shell metacharacters break command construction.

The two most revealing offline checks:

1. **Stateful thirst → sprinkler replay.** Have the fake bridge consume Food during advances and enforce the real governor starvation rule. Start pawns at `0`, `0.249`, `0.25`, and `0.251`; run consecutive drivers without resetting the map, using their actual tick budgets. Preserve nontrivial thirst values. This distinguishes “clears existing starvation” from “survives the driver sequence.” Use realistic consumption rates so a failure is meaningful.

2. **Two-clone forwarding test that executes the remote command.** Give the local and simulated dispatcher clones different HEADs. Exercise every accepted revision form and assert that the queued job records the exact full commit approved locally—or refuses if unavailable. Include a clone path containing spaces, then simulate “enqueue succeeded, SSH reply lost” followed by retry. A fake SSH that merely returns success misses all three problems.

The regex change looks well targeted from the supplied evidence. Neither these checks nor the existing selftests establishes the required live rerun pass; that acceptance condition remains pending.
## What I tried and found

1. **Hunger after calm time (its point 1): real, and fixed.** RimSage `Need_Food.cs:218`: Food falls `2.6666667E-05` per tick × multipliers. The suite's per-chunk floor 0.25, applied ONCE by site_calm before a whole driver run, leaves ~9,400 ticks (~6,250 at a ×1.5 hunger trait), and sprinkler_live runs up to 22×125-tick loops per row over ~9 rows plus pulses, so a colonist at 0.3 could still starve mid-driver. site_calm now tops up Food below `CALM_FOOD_FLOOR = 0.9` (≥ ~22,000 ticks of headroom). The selftest gained a colonist at 0.3 (above the old floor), and it must be fed; one at 0.95 and a hostile must not. A per-chunk feed inside `_BridgeBase.ticks` was rejected: it adds a list_pawns plus need calls to every chunk of every driver, and the thirst drivers measure needs.
2. **Forwarded revision (its point 2): real, and fixed.** `--sha HEAD`/`origin/main`/an abbreviation was checked here but forwarded raw, so it would re-resolve in the dispatcher's clone. forward_submit now resolves it to the full commit locally and forwards that. A clone path with a space is quoted after `~/`. Selftest: a symbolic `--sha origin/main` arrives as the full sha, and `~/rm/dispatch dir` arrives as `cd ~/'rm/dispatch dir'`.
3. **SSH reply lost after enqueue, then a retry: not built.** A retry would queue a second identical job. I left it: that is the same exposure as any submit today, and a duplicate sweep costs lane time, not correctness.
4. **Found while testing:** the mutation test of forward_submit (forward disabled) submitted a real job into SteveDesktop's local queue, J20261112T060011Z-48833d. That is the trap this fix removes. I cancelled it.
