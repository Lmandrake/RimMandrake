# MIASMA_MOTHERS_PRICE_1 — the giant's choice: a stranded young is worth a fortune; carry it home or sell it

**Free machinery** (`mandrake.rm.miasma`), **campaign buyer** (Utinni). Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §3 (*The Mother's Price*), §4 row 1. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 2, *The giant*): the mother's price. The grounded mother was not chosen.

## The ruling
A stranded young is worth a fortune. Carry it home to her (the built befriending) or sell it. Sell one and her crèche remembers: she
never tolerates the colony again, and her young never become yours (no succession).

## What exists (reuse first)
`RM_CompCrecheYoungLedger` (counts the young she is owed), the tolerance state and `RM_HediffComp_SelfTameOnRecord`, the succession
code, `RM_StrandingPoolsExtension`, vanilla trader arrivals.

## spec (numbers `// INVENTED`)
1. A held stranded young (in a pen or carried) is a high-value trade good; a trader caravan arrives for one the colony holds.
2. Selling it writes a betrayal to that mother's ledger: tolerance revoked permanently, succession void for that crèche.
3. Readable: the young's cry keeps going while held (`MIASMA_YOUNG_CALL_1`); the buyer's letter; her ledger in the inspect pane.
4. **Free:** a generic buyer. **Campaign:** the buyers named (the Deepwater vigil for the sea, margin traders for the pens) via Utinni patch.
5. Settings: on/off.

## Depends on
`MIASMA_YOUNG_CALL_1`, `MIASMA_WARDEN_MOTHER_ART_1` (she must be seen to read the outcome).

## criteria
- Quicktest: sell a stranded young; the mother's tolerance reads revoked and succession is void; return one instead and befriending fires.
