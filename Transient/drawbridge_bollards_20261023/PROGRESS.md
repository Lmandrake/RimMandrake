# ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY — progress

- 08:25 start: reading context
- 08:27 plan: one upright bollard per look x {Timber,Steel} (8, codex), composited into 24 styled facings (S/E/N) with existing rope strips; per-facing rope table in code (attach differs by facing in true perspective). Base singles (Graphic_Single, rotated) out of scope -> follow-up item.
- 08:32 candidates built (24), before/ (cur_*) and after/ renders done; next: look, art-eval, code table
- 08:33 code: per-facing rope table (RM_DrawbridgeMath.cs Art/RopesFor, RM_DrawbridgeArt.cs, DrawbridgeChecks.cs Grade key); art-eval run anchor_bollards_20261023 starting
- 08:39 r1 eval: REGEN both Scrapper (DESC_MISS: no rope wrap). Added wrap; remeasured, table updated, rerendered; r2 eval next
- 08:45 r2 eval: REGEN (wrap not joined to outgoing rope; raised N/S slack J-loops = cables-fix math, out of scope). Added wrap->ground strand; r3 eval all 8 next
- 08:50 r3 Scrapper: only raised N/S slack-loop shape findings left (cables math, not art) -> install + file follow-up; evaluating other looks in r3
- 09:03 r3 all looks: no bollard-art blocker beyond slack-loop shape (cables math) + polish (legibility, Modern gloss). Installing 24 via art.py
- 09:08 installed 24 (art.py, by-card); measure --check OK; selftest_flowworks_stock 897/897 incl Drawbridge_Cables x4; shadow sheet built for run anchor_bollards_20261023_r3; next: commit/publish/ledger
- 09:10 published 8a7d4b78b7c2; implemented (A1/A2 live owed); filed SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE, ANCHOR_BASE_REDRAW_STILL_LYING_FLAT; committing ledger
