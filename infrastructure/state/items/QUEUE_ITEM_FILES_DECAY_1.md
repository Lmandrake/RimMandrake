# QUEUE_ITEM_FILES_DECAY_1 — a closing commit doesn't have to touch items/<ID>.md, so the record silently rots

## What happened, 2026-09-02 (FOUNDRY)
`BUILDING_THEFT_HAULER_1` was fully built and committed 2026-09-01
(`3dfea85e`) — full mod, compiled DLL, MayRequire-gated patch, all offline
work done. That commit never touched `infrastructure/state/items/
BUILDING_THEFT_HAULER_1.md`, which still read as pure spec/verify/criteria,
zero progress notes. Both `rimflow next --seat FOUNDRY` and a dedicated
fork's triage of the whole offline backlog read it as unstarted and ranked
it "READY" — a git-log check (`git log --oneline -- src/RimMandrake/
TheftHauler`) is what caught it, not the queue tooling or the item file.

## spec
`rimflow` has no hook forcing a `close`, or even a plain code commit that
finishes an item's work, to also append to that item's own `items/<ID>.md`.
Nothing stops a future commit from doing exactly what `3dfea85e` did again.
Two shapes worth considering, either or both: (a) a pre-commit or `rimflow
close` check that warns (not blocks — plenty of commits legitimately touch
code without finishing an item) when a commit's message cites a queue ID but
`items/<ID>.md` isn't in the same diff; (b) teaching `next`/triage-style
reads to check `git log --oneline -- <item's known source paths>` before
trusting an item file's silence as "nothing happened here."

## verify
Whatever's built should be checked against a deliberately-reproduced case of
this exact failure (an item with real, committed, working code and a stale
item file) and confirm it now surfaces the mismatch instead of silence.

## criteria
A FOUNDRY or BENCH session pulling `next` (or triaging the backlog) no
longer has to independently think to run `git log` against guessed folder
names to catch a done-but-undocumented item.
