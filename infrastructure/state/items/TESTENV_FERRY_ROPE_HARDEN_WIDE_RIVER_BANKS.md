# TESTENV_FERRY_ROPE_HARDEN_WIDE_RIVER_BANKS

Filed by BENCH 2026-10-15 (after live round 8, ratchet_pilot tier, HEAD 22b596181b). Evidence:
`Transient/bench_live_20261015_r8/live/river/ext_river_{1,2}.json` / `.log`, `river_site_3.log` (tile 1474, grid
`current=8152 fast=3943 edge=4209 size=2.50`, moving water on west 32 / east 35 edge cells).

What happened: `extension_proof --live --site river`, chain rivers works, component `works/ferry_rope` read
`UNMEASURED could not find two banks across the current` both runs, and every later row of that chain was skipped
(incl. `ferry_rope_undrafted`).

Class: SITE/HARNESS (the probe's site finder), not MOD. `RM_RiverWorksProofWorks.SpawnFerry` tried exactly ONE line:
the first weir site's first adjacent water cell, walked across the flow (FlowDirAt+2) both ways; either walk failing
(out of bounds, > 60 water cells, or a far-bank cell that is not Standable / holds an edifice -- a tree is PassThroughOnly,
so any tree on that one bank cell refused it) was the whole answer. The river is ~33 moving cells wide at the edges, under
`ferryMaxSpan` 40, so a rope is possible on that map.

## guard (to build)

The probe searches every bank-adjacent moving-water cell for a straight crossing across its flow whose two bank cells
are standable with no edifice and at most `ferryMaxSpan` apart (shortest wins), and only then spawns the two posts.
What it MEASURES is unchanged (paired, rope count, rope exemption of the crossing's water cell). When no crossing exists
it reads UNMEASURED with the counts of why (blocked bank / too wide / no far bank), so a genuinely unbridgeable river is
told apart from a narrow finder.

## verify

`river_site.py` then `extension_proof --live --site river` on a wide (size 2.5) river: `works/ferry_rope` is not
UNMEASURED "two banks" (PASS, or a FAIL that is the mod's), and `ferry_rope_undrafted` runs.
