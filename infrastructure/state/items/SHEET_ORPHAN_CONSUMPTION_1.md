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
