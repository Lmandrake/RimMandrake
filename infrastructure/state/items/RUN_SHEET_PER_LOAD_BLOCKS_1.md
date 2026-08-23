## spec
Filed by REP 2026-08-23: *"The run sheet needs per-load blocks and an index, or it rots after
every single load."*

🔑 **The diagnosis, from doing the surgery an hour earlier: `NEXT_RELOAD.md` was TWO documents
wearing one name**, and that is the whole mechanism of the rot.

| | changes | what it is |
|---|---|---|
| **standing procedure** | rarely | the down window, the startup harvest, the tool census, the gates, the unlock, the after-load refresh |
| **this load's payload** | every load | which batches to run, which items to score, which strings decide them, which baselines to write down |

**The payload half goes stale the moment a load is scored — but nobody deletes it, because the
procedure half around it is still live.** So the spent payload stays, and it does not merely
take space: on 2026-08-22 a spent header sat at the top announcing 🔴 *"F1 is the gate:
`Exception loading def from file Biomes_` must be 0"* when the live capture already held **80
BiomeDefs**. It was sending the next launcher to stop at a green light. That is the cost, and
it is a correctness cost, not a tidiness one. The file had been cleared twice, both times late.

**Done, 2026-08-23:**
1. **Split.** Standing procedure → `infrastructure/state/LOAD_PROCEDURE.md` (§1 §2 §3 §7 §8
   §9). Payload stays in `NEXT_RELOAD.md` (§4 §5 §6 §10 + the deployed-and-unproven blocks).
2. ⭐ **Section numbers deliberately NOT renumbered.** Other docs cite *"§5 of NEXT_RELOAD"*
   and *"§3–§6"*; renumbering breaks every one of them silently. The numbers are one sequence
   across two files, and each file's header says which numbers live where.
3. **An INDEX at the top of `NEXT_RELOAD.md`**, one row per block with a ⏳ PENDING / ✅ status,
   and the rule beside it: **when a load is scored, move its block whole to
   `NEXT_RELOAD_ARCHIVE.md` and delete its index row.** ⛔ Not "mark it ✅ and leave it" — that
   is the same rot one step slower.

`NEXT_RELOAD.md` **460 → 222** lines (budget 400). `LOAD_PROCEDURE.md` 259.

## verify

    python3 src/RimMandrake/Utils/doc_budget.py | grep -E "NEXT_RELOAD.md|LOAD_PROCEDURE"

**PASS =** `NEXT_RELOAD.md` under budget, and every block in it has an index row. The real test
is the next load: after it is scored, does the block leave? If a scored block is still here a
week later, this item did not work and the index is decoration.

## criteria
- [x] Standing procedure separated from per-load payload.
- [x] An index that names every block and its status.
- [x] Cross-references preserved — no section renumbered.
- [ ] ⏳ **Proven by the next load actually being archived out of it.**

## Watch out
🔴 **The index is discipline, not a generator, so expect decay.** `CLAUDE.md` is explicit:
single-source only what a generator can enforce. A real fix is a script that reads the blocks,
compares against the ledger's `game UP` events, and reports any block older than the last load
that is still ⏳ — **that is the thing that would make this stick**, and it is not written.
Filed as `RUN_SHEET_STALE_BLOCK_CHECK_1`.
⚠️ **`LOAD_PROCEDURE.md` is 259 against a default 250** and there is nothing left to cut — its
provenance density is **2.7**, the lowest in the repo; the remainder is rules and paste-able
commands, which the budget guard itself says never to cut. It needs its own budget entry in
`src/RimMandrake/Utils/doc_budget.py`. **Not done here on purpose: a peer had that exact file
uncommitted in the working tree** (raising `BUILDABLE.md` to 800 and exempting `facts/`), and
editing it would have clobbered them. Filed as `LOAD_PROCEDURE_NEEDS_BUDGET_1`.
