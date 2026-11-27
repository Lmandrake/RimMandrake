# RIMMANDRAKE_TIME_SLOW_ACTIONS_DEPLOY_CHECK_TOOK_TWO_MINUTES

## What the card said

<!-- answered 2026-11-27T02:15:26Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** I measured the Windows drive from WSL at 6:09 PM. Listing folders is fast: one deployed mod, 1,457 files, in 0.09 s. Reading file contents is slow: 300 small files took 1.0 to 1.7 s on the Windows drive and 0.007 s on the Linux drive, about 150 times slower. So a tool that reads many files there is slow; today's known case is the deploy check, 107 to 148 s, which reads every mod. Common status commands took 0.1 to 3.7 s, so they are not the problem. The game itself can only read the Windows copy. (Hard to read? Type STE, Binding or Both for a rewrite.) How should we stop slow reads of the Windows drive?
**Picked:** Time everything, fix by cause (Recommended)
**Its description:** Why: only one slow reader is measured so far; the rest are guesses. A worker times every common action for a day and names each cause. The deploy check gets an index now (next option). Cost: one study run plus small fixes; slower than copying today. Recommended: it finds the slow actions we have not guessed.
**Other options:** Index only, one copy · Mirror the mods into WSL · Run readers on the Windows side
