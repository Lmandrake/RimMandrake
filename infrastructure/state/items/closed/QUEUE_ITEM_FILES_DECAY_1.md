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

## 2026-09-02 (FOUNDRY) — built option (b): `rimflow show` checks for itself

Wired into `cmd_show` (`rimflow show <ID>`, the "let me look at this before I
claim/pick it" command — the one both near-misses were actually caught
through, by hand) rather than `close`: the real failure mode wasn't a close
event missing a check, it was a commit that finished real work and never
called `close` OR touched the item file at all, leaving the item correctly
`doing` with a stale prose file. A `close`-time check would never have fired
for either historical case.

`_undocumented_work_warning(item_id)` (`cli.py`): searches `git log -F
--grep="<ID>:"` (this repo's near-universal commit-subject convention,
confirmed against every commit cited this session) for commits citing the
ID, and warns — once, right after the header, before the prose dump — only
when NONE of them touched `items/<ID>.md`. No structured item→source-path
map exists or is needed; option (a)'s "same diff" framing was reconsidered
in favor of "any commit since, ever," which is what actually would have
caught `3dfea85e` (2026-09-01) days before this session even started.
Advisory only — never blocks, matches every other soft-warning `rimflow`
already has (THIN ITEM, dead evidence). Skipped entirely once
`it.closed_sha` is set (a closed item already carries its own commit tie).

**Verified against the deliberately-reproduced failure**, per this item's
own `## verify`: `selftest_undocumented_work.py` builds a real throwaway git
repo (`model.ROOT`/`model.ITEMS` monkeypatched, restored after — the real
repo's own history is never touched) and reproduces the exact
`BUILDING_THEFT_HAULER_1` shape byte for byte — a commit citing an ID that
never touches the item file, confirms the warning fires, confirms a LATER
citing commit that does touch the file clears it, confirms a colon-anchored
prefix collision (`FAKE_ITEM_1` vs `FAKE_ITEM_10`) doesn't false-positive,
and documents the one accepted false-positive shape (a body-line mention,
not a subject-line citation) rather than silently living with it unstated.
5/5 passed. Smoke-tested against 5 real, currently-clean items
(`DROID_KOTORDROIDS_PORT_WAVE1_1`, `SANDWORM_MYTHOS_BUILD_1`,
`RIVER_STEAM_ANIMATION_1`, `NINEFOLD_ENGINE_M0_1`,
`GRAFFITI_FRAMEWORK_BUILD_1`) — zero false positives, and re-ran against
`BUILDING_THEFT_HAULER_1`/`SETTLEMENT_VERBS_WAVE_1` themselves, both
correctly silent now that their own item files carry the correction.

**Not built**: option (a) (a commit/pre-commit-time check) — reconsidered
and dropped, not merely deferred; see above for why `show`-time is the
actual leverage point. `next`'s own single-item offer path and the
`_offer_claimable`/`_nothing` bucket listings were NOT wired to this check —
`show` is the point every real workflow already routes through before
claiming or reporting on an item, and adding it everywhere else risked
noise on the common "the item is just correctly in progress" path.

Closed at the commit that lands this note.
