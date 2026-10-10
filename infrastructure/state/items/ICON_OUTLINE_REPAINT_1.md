# ICON_OUTLINE_REPAINT_1

Owner card 2026-10-10: item icons with black outlines are redrawn painted, no outline (rot_*_v3 look).

## spec
- Census and full outlined list (165 icons, share of near-black edge pixels >= 0.90): Transient/icon_outline_20261010.md
- 24 jobs already in the artpipe pending dir (Transient/icon_outline_jobs_20261010.json), including rot_tollukcap_v4.
- Batch 1 rendered: 21/24 under 0.10 edge-black; contact sheet Transient/icon_renders_contact_20261010.png; 3 re-queued as v4. Batch 2 (27 jobs) queued: Transient/icon_batch2_20261010.md.
- Batch 2 + v4 rendered (27 + rot_tollukcap_v4), measured, none visibly outlined; 9 flagged by metric are genuinely black materials. Review: Transient/icon_batch2_review_20261010.md, sheet Transient/icon_renders_contact_batch2_20261010.png.
- NEXT: owner looks at both contact sheets; on OK install via art ledger `art install` only. Gap-art jobs (10) still pending/active: build gap sheet when done.
- NEXT: queue the remainder (fish catches, meal skewers, eggs, research kits, no-job-record items) in later passes.

## verify
- Re-run the census on installed PNGs: share < 0.3 for each repainted icon.
