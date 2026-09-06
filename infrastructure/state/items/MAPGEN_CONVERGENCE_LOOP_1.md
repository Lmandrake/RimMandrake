# MAPGEN_CONVERGENCE_LOOP_1 — the standing iteration: painter and GL side by side until they agree, and both are great

Owner 2026-09-06 (research doc §8 #9): *"Do both, accept they differ at first, but then go back and improve the painter until they converge. Keep iterating until we get great results."*

## spec

Each round:
1. Same 8 plans → painter renders (offline, seconds) AND GL screenshots (`MAPGEN_GL_SHEET_1`'s procedure, ~16 min bridge).
2. One sheet, three rows per plan: painter · GL · the nearest corpus map by landform class. Captions = premise.
3. Two gradings, kept apart: (a) **convergence** — does the painter's render predict the GL render (same landform footprint, same edge character, same terrain families)? Measured by `corpus_stats.py` features on both grids (GL's grid read back through the bridge terrain batch read) plus the owner's eye; (b) **quality** — is the GL map great? Owner keeps/cuts.
4. Feed back: painter fixes to `MAPGEN_PAINTER_V1_1`'s successor; emitter knob mappings to `gl_emit.py`; chooser rules to the spec. Log each round's gap in this item file (a table: round, feature, painter, GL, corpus band).
5. Stop when the owner says the sheet is great, not when the numbers converge.

## verify

```
PROVE   round table in this file grows by one row set per round; the last round's sheet has the owner's keep/cut marks
EXPECT  convergence features move toward each other round over round; quality keeps rise
LIES    tuning the painter to the GL grid's statistics while both still read as diagrams — the corpus row on the sheet is the control against that
```
