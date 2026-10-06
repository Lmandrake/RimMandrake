# FlowWorks size table (MEASURED 2026-10-06 from the bench clone, bytes)

- C# total: 843,412 in 106 files; of which debug/selftest/proof-named C#: 121,521 in 10 files
- Defs+Patches XML: 346,695 in 68 files
- Python (validation, northstar harness, review map, selftests): 794,258 in 24 files
- northstar result JSON files on disk: 39

## Python files by size
-  197,724  src/RimMandrake/FlowWorks/northstar/validation_v2.py
-  116,724  src/RimMandrake/FlowWorks/human_review.py
-  105,697  src/RimMandrake/FlowWorks/northstar/extensions.py
-   77,398  src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py
-   64,119  src/RimMandrake/FlowWorks/review_map.py
-   36,318  src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py
-   26,496  src/RimMandrake/FlowWorks/northstar/site_spec.py
-   22,810  src/RimMandrake/FlowWorks/northstar/selftest_flowworks_northstar.py
-   19,993  src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/make_mockups.py
-   18,585  src/RimMandrake/FlowWorks/northstar/prep_site.py
-   16,903  src/RimMandrake/FlowWorks/northstar/fakegame.py
-   12,665  src/RimMandrake/FlowWorks/validation.py
-   10,857  src/RimMandrake/FlowWorks/northstar/selftest_human_review.py
-    9,106  src/RimMandrake/FlowWorks/northstar/extensions_rivers.py
-    8,831  src/RimMandrake/FlowWorks/review_map_visuals.py
-    7,767  src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/make_sheet.py
-    7,558  src/RimMandrake/FlowWorks/northstar/river_site.py
-    6,647  src/RimMandrake/FlowWorks/selftest_flowworks_rivers.py
-    5,691  src/RimMandrake/FlowWorks/northstar/selftest_extensions.py
-    5,102  src/RimMandrake/FlowWorks/selftest_flowworks_swale.py
-    4,774  src/RimMandrake/FlowWorks/Tools/selftest_liquid_looks.py
-    4,597  src/RimMandrake/FlowWorks/northstar/extension_proof.py
-    4,586  src/RimMandrake/FlowWorks/northstar/runsheet.py
-    3,310  src/RimMandrake/FlowWorks/selftest_review_map.py

## Commit split since 2026-09-20 (path heuristic)
- 87 FlowWorks commits touched harness/validation/review tooling; 74 touched mod C#/XML/art (a commit can do both).
