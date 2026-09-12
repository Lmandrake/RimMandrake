# SHEET_ORPHAN_CONSUMPTION_1 — the sheet verdicts nothing ever consumed

The owner graded both assignment sheets on 2026-09-10 (fauna 828 rows / 291
overrides; flora 288 rows / 19 overrides — `ASSIGNMENT_SHEETS_VERDICT_SITTING_1`).
A channel-level provenance audit (BENCH subagent, 2026-09-12) found five verdict
channels that were graded and never landed anywhere. Sidecars:
`design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json` and
`flora_assignment_register.decisions.json`; consumer:
`design/Jawa/worldbuilding/review/apply_assignment_verdicts.py`.

## the orphans (MEASURED by the audit — re-verify each before acting)

| channel | rows | evidence |
|---|---|---|
| fauna `decision=out` (cut for real) | 6 | BMT_CaveSpider, BMT_ChemSnail, BMT_GiantSlug, BMT_GiantSnail, BMT_Pillbug still in `the_rot.json`; AA_FissionMouse still in `wasteland.json`; no cut-list sidecar ever written |
| flora `decision=move` | 15 | `ROSTER_MOVE_APPLY_1` says "Flora is NOT in scope"; 6/6 spot-checked (AB_GiantGamma, AG_Gamma, AG_Septimum, AB_CrystalFlower, AB_CrystalHorn, BMT_Nogtyl) unresolved despite `flora_move_mapping.md`'s claim |
| flora `decision=out` (purge) | 4 | AB_DessertTree, AB_EyeGrass, Boomshroom, PoisonPlantBush all still present, no `flora_purged` record |
| NEW-ART/DEF commission ledger (`decision=in`) | 118 | the sitting item says these verdicts "CREATE the art queue"; no ART_REGEN_WAVE item, commission item or artpipe registry entry references any of the 118 concept slugs |
| flora `art:improve` | 148 | WAVE3 examined only flora's single `redo` row; waves 4–9 draw exclusively from the fauna improve pool |

UNKNOWN: the sizeBin rescale worklist (~29 fauna rows where sizeBin differs from
prefill) — `apply_assignment_verdicts.py`'s `size_rescale_worklist` sidecar is
never written anywhere and no item references it. Not measured whether any
bodySize actually changed. Resolve it first: measured orphan, or consumed by the
Law-3 size scaling under `FAUNA_TOLERANCE_NORMALIZATION_1`?

## 🔴 the trap — the sheet is a superseded snapshot
Every orphaned verdict is checked against the rulings landed AFTER 2026-09-10
before it is consumed. Later sittings (09-11, 09-12: homeless dispositions,
bat cull, lisk cull, Hssiss, Wave-2 rulings, the card sittings) legitimately
overrode sheet rows. **The sheet never overwrites a newer decision.** Where a
sheet row and a later ruling disagree, the later ruling stands and the row is
recorded as superseded, not applied. Grep the roster json's history
(`git log -p --since=2026-09-10 -- design/Jawa/worldbuilding/biomes/rosters/`)
and the item files named above per row before writing.

## spec
1. Resolve the sizeBin UNKNOWN (measure, don't infer).
2. Per channel: diff the sheet verdict against post-09-10 state; produce a
   per-row table `defName -> APPLY | SUPERSEDED-BY <commit/item> | ALREADY-DONE`
   in `Transient/` for the owner to skim.
3. Apply via `apply_assignment_verdicts.py` (report first, `--apply` writes),
   or by hand where the applier has no channel for it (flora purge/move), then
   `_validate.py --cross`, then the regeneration commands it prints.
4. The 118-row ledger becomes a real art-queue filing (an ART_REGEN_WAVE item or
   the artpipe registry) — commission / defer / drop as graded.
5. Freeze both decisions files when done (`frozen-artifacts` skill).

## verify
- Each of the 6 fauna cuts and 4 flora purges is absent from every roster json
  (or explicitly SUPERSEDED with the ruling cited).
- The 15 flora moves resolve to a target roster each.
- 118 ledger slugs each appear in exactly one art-queue artifact.
- `serve_sheet.py --decisions <file> --status` shows `frozen: true` on both.

## criteria
Zero verdict channels of the 2026-09-10 sheets without a recorded consumer, and
zero later rulings overwritten by an older sheet row.

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — audit table built, NO writes made, needs owner calls before any apply

Read-only audit only (spec steps 1-2), deliberately stopped before any
`--apply`/roster write per this pass's own brief — the trap this item warns
about ("the sheet never overwrites a newer decision") is real enough that
the actual apply step needs a human decision on several rows, not a blind
run. Full per-row table: `Transient/sheet_orphan_audit_2026-09-12.md`.

**sizeBin UNKNOWN resolved: genuine unconsumed orphan**, not covered by
`FAUNA_TOLERANCE_NORMALIZATION_1` (its own RULED §4 says verbatim "Does NOT
change: bodySize itself, per the ceiling-fields lesson"). 29 fauna + 3 flora
rows, `size_rescale_worklist` sidecar has never once been written by
`apply_assignment_verdicts.py` in this repo's history.

**Channel counts** (APPLY / SUPERSEDED / ALREADY-DONE / UNRESOLVED):
sizeBin 32/0/0/0 · fauna out 6/0/0/0 · flora move 14/0/1/0 · flora out
4/0/0/0 · art/def ledger ~91/~20/7/0 (of 118) · flora improve 145/3/0/0.

🔴 **Five findings need an owner or BENCH call before any apply runs, not a
FOUNDRY judgment call**:
1. `flora_move_mapping.md` rows 12-13 (AG_Gamma, AG_Septimum) claim a target
   roster ("already in forsaken_crags") that is MEASURED FALSE — both plants
   only exist in `the_forge.json`. Applying as written would misfile or
   effectively delete them from the world. Needs a real target roster named.
2. The two flora decision files disagree with each other (14/288 rows) —
   `ART_REGEN_WAVE3_QUEUE_1` asserted they were byte-identical and was
   wrong; commit `1caff3664` silently demoted `AB_SlimyPholiota` from `redo`
   to `improve`, which is why WAVE3 only ever saw one redo row.
3. If `DUMP_DRAWSIZE_CAPTURE_1` unblocks and a naive Law-1 rescale runs from
   current drawSize, it will silently overwrite all 29 owner sizeBin
   rulings from this sheet. Flagging now so whoever builds that item reads
   this first.
4. The 118-row "NEW-ART/DEF commission ledger" is not a clean commission
   list — **at least 9 of the 118 slugs** are ALREADY BUILT live defs
   (`RSW_Cindermare`, `RSW_Skarnix`, `RUT_FireHawk`, `RUT_FurnaceBeast`,
   `RM_FE_Plant_Quickgrass`, `RM_FE_Plant_ScorchFruit`, `RUT_LivingBolt`,
   `RUT_SweetlineTree`, `RSW_Reefback`; a 10th, a lanternwhale slug, matches
   the same pattern) — the sheet re-surfaced already-shipped concepts as
   new commissions. `RUT_SweetlineTree` (commit `0d42dd16a`) **predates the
   register's own 2026-09-10 grading date**, meaning this isn't only "a
   later ruling superseded an old row" — the register contains duplicate
   entries that were already stale on the day it was graded. Only ~130
   keyword hits across two passes were individually checked, not all 118;
   the true error rate is likely higher. Full addendum in the Transient
   audit file.
5. A third instrument (`cast_assignment.csv`) still contradicts the 6 fauna
   `decision=out` cuts (carries all 5 BMT stragglers + AA_FissionMouse as
   `import`/`keep`), and the 2026-09-11 card ruling (`cf0632c39`) actually
   WIDENS the cut list (adds `BMT_ChemSnail`@`the_cracked_lands`,
   `BMT_GlowBat`) — but that ruling's home item (`BMT_FAUNA_ABSORPTION_1`)
   is itself ledger-BLOCKED, so which list is authoritative right now is
   not this pass's call.

**Not attempted this pass, deliberately**: steps 3-5 of the spec (the
actual `apply_assignment_verdicts.py --apply` run, the flora hand-edits,
the 118-slug art-queue filing, freezing the decisions files). All of them
are gated on the 5 calls above landing first — applying blind now risks
exactly the kind of silent data loss this item exists to prevent.
`needs=owner`.
