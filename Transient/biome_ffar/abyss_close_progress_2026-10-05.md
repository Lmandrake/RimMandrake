# Abyss sheet close — progress 2026-10-05 (BENCH helper)

## 1. Commit raw decisions — DONE 818a1f616
## 2. Stamp ruled + ingest — DONE 26df94528
- reviewStatus stamped ruled (by owner (Lukas); evidence = sidecar writeCount 96, BENCH relay). `art.py ingest`: 37 rulings, 3 AA_NightAve pictures purged (owner purge list), 1 untouched (RM_Gharrek).

## 3. Mechanical def edits — DONE 11a821c18
- RM_Abyss roster: AA_DuskRat, AA_Frostling, AA_NightAve, RM_Vosska rows removed (RM_Abyss only; abyss.json rows -> evictions cut:).
- RM_Durrgak: label "sorter", description says tame + trainable + cleans; RM_EatCleanableExtension (filth only) from CreatureBehaviors. Already Advanced-trainable and tamable (wildness 0.75). defName kept.
- RM_Skarnix: label "gekkrith", new description, eyes ring the head. defName kept (RUT_Abyss casts it).
- RM_Wickwood: visualSizeRange 1.3~1.8 -> 2.6~3.6, shadow x2.
- RM_Cindermare: "fourteen eyes, seven to a side".
- RM_Drokattak: description colours -> black hide, purple sheen, black-violet quills, many eyes (rest kept).
- Abyss validation.py static: all PASS. run_selftests 178/180 (2 pre-existing failures, not ours).

## 4. Authored names + art queue — DONE
- 17 donor rows given new names/descriptions (table in infrastructure/state/items/ABYSS_SHEET_DONOR_PORT_1.md); names checked: 0 repo hits, 0 Wookieepedia titles.
- 53 artpipe jobs filed from Transient/biome_ffar/abyss_redo_jobs_2026-10-05.json (27 rows: 10 ported fauna + gekkrith + drokattak v2 + cindermare facings faced x3; 7 ported flora; glowing grass a/b/c; etchcap b/c; wickwood b/c). owner_note verbatim on every row. Existing art checked first: the old giantgamma/stikehr/septimum/radagast/glowinggrass v1 redraws and the crags_* sets predate this ruling and are superseded by it.

## 5. Filed items — DONE
- ABYSS_SHEET_DONOR_PORT_1 (FOUNDRY): port the 17 donor rows to owned RM_ defs, wire ruled art, etchcap Graphic_Random defect, Krizzak/Summ keeps install, durrgak/skarnix C# strings, RUT_Abyss twin question.
- Note on BIOME_FLORAFAUNA_ART_REVIEW_1.
