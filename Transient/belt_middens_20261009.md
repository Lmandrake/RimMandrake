# Long Shade middens build 2026-10-09

## status
- started
- item LONGSHADE_MIDDENS_SPENT_BUILD_1 filed+claimed
- finding: heap/vrekka/search/2 toggles already built (2a704a08e, regrow model). Rework to spent-once; add GenStep seeding + clean-patch marker.
- art: artpipe find vrekka midden -> only Wasteland middenshell; queue decision below
- code written: spent flag, RM_LongShadeMiddenMapgen.cs (2 gensteps+tell comp), 2 settings, defs; art queued 2 jobs; next build+validation
- built OK (winbuild LongShade 0 err); validation.py STATIC PASS (midden chain extended: spent, gensteps, tell)
- art queued: RM_LongShadeMidden, RM_LongShadeCleanPatch (2 jobs, install_to LongShade/Textures/Things/Building/). Vrekka art already exists.
- OWED live: GenStep placement at rock lee, clean patch, search-once (no bridge this pass)
