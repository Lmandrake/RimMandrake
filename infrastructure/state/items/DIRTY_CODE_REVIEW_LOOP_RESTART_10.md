# DIRTY_CODE_REVIEW_LOOP_RESTART_10

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor to
`DIRTY_CODE_REVIEW_LOOP_RESTART_9` — read that file (and its own chain) for the fuller
history. This file is the short version: what this session did, current numbers, and
what to do first.

## Where things stand

`infrastructure/state/CODE_REVIEW_STATUS.json`: unchanged this session at **618 clean
entries / 635 in-scope (97.3%)** — this session's FOUNDRY pulls were all queue items
already filed by the prior sweep, not new full-file reviews, so the ledger itself
didn't move. (A `code_review_status.py list` was kicked off to refresh the live count
but ran long on this shared mount — re-run it fresh before trusting a number here,
per `[[shared-worktree-remeasure-before-acting]]`.)

## What this session actually did, in order

Pulled `rimflow next --seat FOUNDRY` cold and cleared everything RESTART_9 had queued:

1. **`VALIDATE_PATCH_BLIND_SPOTS_1`** — closed. Re-verified all three findings still
   live in `validate_patch.py` (MayRequire zero hits; `check_dict_keyed_fields()`
   unreachable on the `Defs` root-tag branch, which returns before line 2264 runs).
   Per its own criteria, the item's job was leaving source-verified findings for a
   skill curation session, not fixing ad hoc — that job was done, so it closed as-is.
2. **`VALIDATE_QUEST_FALSE_NEGATIVES_1`** — closed, same pattern. Re-verified
   `main()`'s `ET.ParseError` report is gated on `f in args.paths`, which only holds
   bare positional-arg files — `--dir`-discovered files never reach it.
3. **`IMAGE_SKILL_SCRIPT_NITS_1`** — closed, same pattern. Re-verified
   `compare_images.py`'s `subject_stats()` sets `visible=True` unconditionally when
   `has_alpha` is False (drift checks never fire on non-alpha pairs), and
   `selftest.py`'s `squash()` is dead (CASES calls `_squash()` directly).
4. **`KARRASK_ART_MISSING_1`** — closed, actually built this time (not just filed).
   Generated `Textures/Things/Pawn/Animal/Karrask/Karrask.png` (256x256) via the
   `generating-rimworld-sprites` skill: chroma-keyed the owner's already-picked
   mockup directly (`art/mockups/karrask_opt2.png`, clean key, 0% fringe), conformed
   onto a transparent canvas matching this mod's Skarnix/Cindermare Graphic_Single
   convention. Confirmed live that the other two texPaths named in the item
   (`RSW_KarraskShedRaw`/`Plate`'s `Things/Item/Resource/Leather`) were the
   vanilla-packed-asset false positive from finding #2 above, not actually missing.
   Fixed two now-stale "PLACEHOLDER / no file exists yet" header comments in
   `ThingDefs_Karrask.xml`/`PawnKindDefs_Karrask.xml`. **Not deployed or
   load-tested** — that's a separate load-round item.

All four commits pushed individually (`908fdc8a`, `a37b8ce5`, `1931db8e`,
`9adfd29c`).

## Recommended next steps, in order

1. **`KARRASK_ART_MISSING_1`'s follow-on**: deploy the new sprite and confirm it
   in-game on a load round (`rimworld-load-round`) — the sprite itself is unverified
   against the actual engine, only against the offline validator/describe checks.
2. **Re-verify then resume RESTART_7/8's still-open list** — decays fast, re-check
   before acting, per `[[queue-items-decay-verify-first]]`:
   - the bridgetools `--gm` deploy debt
   - the 49 deprioritized files across 11 inactive mods
   - `rimflow/` itself — deliberately deferred pending an owner ask; the two fixes
     RESTART_9 found in `rimflow/render.py` came from re-reviewing a diff that had
     already landed, not from opening the module cold — that distinction still holds.
3. **Re-run `code_review_status.py list`** for a fresh in-scope/clean count before the
   next full-file review pass — this session didn't get a clean read (see above).
4. Otherwise: keep pulling `rimflow next --seat FOUNDRY`. When it returns nothing
   but a thin continuity marker like this one, that means the filed backlog is
   drained and the next move is either (a) fan out a fresh sweep of un-reviewed
   in-scope files (this is `AFK batches` territory — subagents, output budgets,
   grade the diff not the summary) or (b) stop and let the queue refill from other
   seats' work.
