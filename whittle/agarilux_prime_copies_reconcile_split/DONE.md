# Done claim

- true: **One owner is decided and recorded.** Which mod owns RM_AgariluxPrime's def and texture is stated on the item with | evidence: `whittle/agarilux_prime_copies_reconcile_split/evidence/resolved_texpath_before.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/resolved_texpath_after.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/broaden_checks.txt`
- true: **Exactly one copy of the texture ships.** The losing copy is deleted from `src/`; nothing in `src/`, the art ledger | evidence: `whittle/agarilux_prime_copies_reconcile_split/evidence/search_after.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/resolved_texpath_after.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/art_ledger_status_after.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/broaden_checks.txt`
- true: **Every inbound reference is fixed.** Defs, patches, art ledger/artpipe rows, deploy manifests and any doc naming the | evidence: `whittle/agarilux_prime_copies_reconcile_split/evidence/search_after.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/validate_patch.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/validate_def.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/selftests.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/selftest_alpha_plants_renders.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/deploy_plan_biomes.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/deploy_plan_UtinniPatches.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/bulk_accept_plan_agarilux.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/unproven_adjudicate_check.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/sheet_resolution_after.txt`
- true: **The surviving copy's judgement stands, or it is re-judged.** If the survivor is the TheRot (ACCEPT) copy, no re-judge | evidence: `whittle/agarilux_prime_copies_reconcile_split/evidence/judgement_record.txt` `whittle/agarilux_prime_copies_reconcile_split/evidence/three_copies_before.png`

## What I found that the item did not say
There were THREE copies, not two, and the game drew neither copy that gptredo_03 judged. `RM_AgariluxPrime` draws
`RotSpecies/AgariluxPrime` (TheRot, 4096 px v3, owner-approved 2026-09-20). Both judged copies sat at the old Alpha Biomes slot
`Things/Plants/AB_AgariluxPrime`, which a TheRot patch overrode. The TheRot copy there was a 256 px donor-regen render (ACCEPT), the
UtinniPatches copy a 384 px render (REGEN). So TheRot owns the def and the texture. Both slot copies are retired through the art ledger
(`src/RimMandrake/Utils/art/agarilux_prime_retire_copies.py`). The base def now names `RotSpecies/AgariluxPrime` directly and the
repoint is deleted, so the src-reading art tools agree with the game (published 45408f140e). The decision and the correction are recorded in
`infrastructure/state/items/AGARILUX_PRIME_COPIES_RECONCILE_SPLIT.md` (Decision section) and in two ledger notes.

Filed, not fixed (outside this split's scope):
- `RIMMANDRAKE_RETIRE_ROT_DONOR_SLOT_COPIES_ELEVEN_SHADOWED`: 11 sibling Rot ports have the same never-drawn donor-slot copies.
- `RIMMANDRAKE_FIX_SLOT_SCAN_BLIND_TO_TEXPATH_PATCHES`: the root cause. `artledger.scan_def_slots` ignores texPath patches, so
  art_sheet labelled the 256 px copy "IN GAME" on four sheets (2026-10-24 to 2026-11-05) and art-eval judged two pictures nobody sees.

## What I'm least sure about
- The deployed Steam Mods folder still holds both retired PNGs until the next deploy of `mandrake.rm.biomes` and UtinniPatches. I may
  not deploy. Both dry-run plans say `--apply` prunes them, and no def reads that slot in the meantime, so the player's picture does not change.
- The "only one PNG" proof for the drawn path is offline: the resolver, the full-stack file walk and the evaluation of all 69,187 patch
  xpaths. The live dump that shows `RotSpecies/AgariluxPrime` predates the change. The change keeps that path but moves it from a patch
  to the base def, so a live dump after the next load should read the same. That is not yet measured.
- In the repo-wide search, the classification of hits as dated records or append-only ledgers is by path rule plus my reading.
  The five other-def hits each carry a reason in `evidence/search_after.txt`.

## What I did not test
- No running game (offline lane): no in-game render, no fresh def dump after the change, no deploy.
- No new art-eval run on the survivor: under the item's own rule none is owed, and his 2026-09-20 approval covers these exact bytes.
- The 4096 px, 27 MB size of the survivor (a memory question) is outside this item. I did not touch it.
