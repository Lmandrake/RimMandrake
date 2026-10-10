# ICON_OUTLINE_REPAINT_1

Owner card 2026-10-10: item icons with black outlines are redrawn painted, no outline (rot_*_v3 look).

## spec
- Census and full outlined list (165 icons, share of near-black edge pixels >= 0.90): Transient/icon_outline_20261010.md
- 24 jobs already in the artpipe pending dir (Transient/icon_outline_jobs_20261010.json), including rot_tollukcap_v4.
- NEXT: after renders finish, owner looks at them; on OK install via art ledger `art install` only.
- NEXT: queue the remainder (fish catches, meal skewers, eggs, research kits, no-job-record items) in later passes.

## verify
- Re-run the census on installed PNGs: share < 0.3 for each repainted icon.
