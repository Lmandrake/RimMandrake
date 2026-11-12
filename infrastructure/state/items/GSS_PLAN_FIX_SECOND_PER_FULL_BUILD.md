---
state: built
needs: bridge
---

# GSS_PLAN_FIX_SECOND_PER_FULL_BUILD

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

GSS build that plans cords (not reused) now takes ~1 s on the 325-map lattice (E=248): lattice placed 1026 ms, 84 lamps placed 1009 ms, bEdges 997 ms of it. The same scene under the pre-round-2 DLL (wave 3, 06:40) built in 13.6 ms, so round 2 (b60a1526a4) regressed full planning ~70x while making the all-reused path fast (1.7 ms). Profile bEdges on a planned build and restore the old cost.

Built at `903ba19f5d7c` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-11-07: FROZEN STOP 2026-11-07: was game/prove, gen 3, returns 1, checks 2, candidate 903ba19f5d7c; held no clone; bundle /home/mandrake/rm/relentless/store/items/GSS_PLAN_FIX_SECOND_PER_FULL_BUILD/bundles/20261107T020552Z-GSS_PLAN_FIX_SECOND_PER_FULL_BUILD (from an earlier release); hold refused by design for game items (it waits for the verdict/phase), item left as game. NEXT: lift PAUSE and let the game phase prove run on at candidate 903ba19f5d7c; its bundle restores on the next lease.
- 2026-11-09: testq J20261107T155813Z-f2ff09.a1 quarantined: ran inside Steve SIMD fault window F20261107T174953Z (last clean 2026-11-08T00:52:39Z, first bad 2026-11-08T00:57:39Z); no verdict recorded; re-queued as J20261109T230403Z-af96fa
- 2026-11-09: testq J20261109T230403Z-af96fa.a1 quarantined: ran inside Steve SIMD fault window F20261107T174953Z (last clean 2026-11-08T00:52:39Z, first bad 2026-11-08T00:57:39Z); no verdict recorded

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GSS_PLAN_FIX_SECOND_PER_FULL_BUILD --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GSS_PLAN_FIX_SECOND_PER_FULL_BUILD` first: another commit may already do it.
