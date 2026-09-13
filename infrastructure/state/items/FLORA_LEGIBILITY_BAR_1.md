# FLORA_LEGIBILITY_BAR_1 — flora gets its own legibility bar, canvas sizes, and NO stroke

Filed by BENCH, 2026-09-13. MEASURED convention (vanilla core, outline
coverage at 96px→32px): grass 0.00→0.00, bush 0.18→0.01, agave 0.02, trees
soft-edged 1.00→0.32-0.43 (shading, not a keyline), versus fauna/pawns at
1.00→1.00 everywhere. Sheet: `Transient/legibility_final_review_2026-09-13/class_convention.png`.
So the creature-fitted gate and the outside stroke DO NOT APPLY to flora —
artpiped now skips both for class=flora (never silently: legibility reads
"skipped (flora)").

## Owner feedback already in hand (verbatim, from the 2026-09-13 final sheet)

- alientree_v1, flagged: "Why is a tree being generated at low resolution?
  It needs t[…]" — tree canvases must scale with plant size the same way
  creature canvases scale with drawSize; the flora register's curated
  sizeBins (small/medium/large/huge) are the size source
  (`drawsize_backfill.json` maps them 0.8/1.0/1.6/2.2 — a first guess to
  re-rule here).
- ambrosia_v1, flagged: "What the heck is this? Ambrosia is supposed to have
  big gol[…]" — identity misses are a generation-prompt problem the flora
  bar's grading pass should catch alongside legibility.

## spec

1. A flora-specific grading sheet: our flora backlog (129 files exempted at
   the 2026-09-13 regate) beside vanilla flora probes (grass/bush/tree
   classes), graded by the owner like the creature pass.
2. Fit a flora model from those grades (expect: value/shape contrast and
   silhouette coherence matter; hard keyline does NOT).
3. Canvas law for flora: size class → canvas (sizeBin×128 → next pow2), and
   regenerate undersized trees (the alientree flag).
4. Whatever processing (if any) flora borderlines get, it is NOT the black
   stroke — A/B anything proposed to the owner's eye first.

## verify

Flora gate verdicts reproduce the owner's flora grades at ≥ the creature
model's LOO ρ (0.81); vanilla grass/bush/tree probes pass their own bar;
no flora sprite ever routes through the creature stroke (selftest).

## Watch out

- The daemon currently marks flora "skipped, not a pass" — the wave items'
  flora art still reaches review sheets ungated until this closes.
- The flora register decisions file is FROZEN — read sizeBins from it, never
  write.
