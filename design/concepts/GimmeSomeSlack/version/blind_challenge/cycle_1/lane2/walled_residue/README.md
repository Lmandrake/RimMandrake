# Walled residue over 2000 seeded scenes (RIMMANDRAKE_SWEEP_GSS_WALLED_RESIDUE_TWO_THOUSAND_SCENES, 2026-11-15)

The instrument is `../judge_the_judge/diag.py all 1000 --base`: lane 1's scene maker, open and walled, the bars' own oracles.
`residue.py` stages the same harness plus `Residue.cs` (modes `r_stages`, `r_why`, `r_heapground`, `r_heapone`).

## Residue, before (3f9fbc811) and after the fix

| bar | group (cause) | before | after |
|---|---|---|---|
| no_unforced_sharp_turn | cut leads: bend already in the first sprawl; SmoothBends refuses every window (turn cap, cut-keep guard) | 68 bends / 47 strands | 0 |
| no_unforced_sharp_turn | routed leads (junction-junction, self-loop junctions, device leads): the same | 19 / 13 | 0 |
| no_unforced_sharp_turn | heap cables: a tight plug hook at a pile port (HeapEscape takes it before any gentle way or coil) | 28 / 23 | 0 |
| cords_lie_slack (1.4x) | cut-lead bundle (walled 53623), a hop, a routed lead | 5 | 0 |
| cords_lie_slack (1.4x) | 'fell' strands: the floor rule's centreline fallback, never slackened | 2 | 0 |
| cords_lie_slack (stray) | edges over four cells that never leave their conduit line by a cell | 7 | 0 |
| cords_never_repeat | equal short leads drawn alike (L3-L5), each from its own stream | 6 pairs | 6 pairs (open) |

`sweep_base_3f9fbc811.txt` and `sweep_fix.txt` are the raw lines. `stages_base_3f9fbc811.txt` charges each bend to a lay stage: 87 of 115 were already
there after `unfold` (the first sprawl), and no later stage removed them.

## Rulings per group
- **Cut and routed leads: solver defect.** Another draw of the same edge lies clean: `LayEdge` now draws a faulted piece again, from fresh streams of its key
  (`LayRedraws` 8), and keeps the draw with the fewest `LayFaults` (unforced bends, strands under 1.4x, a first strand with no full-cell stray). A clean
  piece is laid exactly as before, so it is unchanged.
- **Heap ports: solver defect.** Bounded search (`heap_escape_search.py`, `heap_search_first_pass.txt`) over each failing port's own heap ground: 21 of 21
  have a local way out with no counted bend (7 by gentle arcs, 14 need a coil, the instrument's own loop). This witness is looser than the kernel: it starts
  at the tip, not after the plug's 0.22 lead. Started after the lead, a coil fits at only 7 of 16, so the kernel also tries the next port. A redrawn cable
  (`HeapRedraws` 12) escapes by a gentle way, then a coil of 330-570 degrees at radius 0.5-0.65 (300 reads 291-297 after its joins), then the plug bend.
  Its later redraws take the next port for the far end, then the near end. The spline fallback is redrawn too.
- **'fell' slack: solver defect.** A FellBack strand now takes CordSlacken's lobe on clear ground, and nothing else (no unbend, no vary).
- **Twins: solver defect, not fixed.** The bar is satisfiable (`feasibility_sweep.py`: every chord-3+ cell has two shapes 0.1 apart). Independent per-piece
  draws collide at a rate that no per-piece change can drive to zero. The fix is a cross-piece pass, which risks the cache invariant (cold = incremental)
  and game-side mesh reuse. Filed: RIMMANDRAKE_PART_GSS_TWIN_LEADS_EACH_DRAWN_ALONE, with its acceptance test.
- No group is unsatisfiable, and no bar was ruled wrong. No bar or check was edited.

## Cost and side effects [measured]
- Live lattice scene: a fresh Build takes 670 ms, against about 690 before (`live_build_fix.txt`).
- CordShape.Kinks over the bends scenes: 3272 -> 3290. This is not a bar.
- T_CORE 4507/4508 and --geometry 4518/4519. Each run failed one timing check: the graph-worker convergence check, then the 30 ms slice check at 30.1 ms.
  The convergence check is red on the base too, in 2 of 2 `--perdig-only` runs; with the fix it was red in 1 of 2. Filed:
  RIMMANDRAKE_STEADY_GSS_FAULTED_GRAPH_JOB_NEVER_SETTLES.
- T_GATE (proof_all --offline-gate), no_hose, end-heap budget, short-twins, settings sweep, strip and junction art: all green.
