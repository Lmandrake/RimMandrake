# GL_EMITTER_OBJECT_GAP_1 — 14 of 44 shipped landforms rebuild one `<Object>` short

Found 2026-09-06 while fixing `gl_emit.py`'s List<MapSide>→List<String> defect (GL refused the emitted Canyon; fixed in 33e2e681). A rebuild-all-44 check then showed 30/44 census-identical and 14 emitted with exactly one fewer `<Object>` than the source: CoastalIsland, Cove, CoveWithIsland, Fjord, Glacier, Gorge, River, RiverConfluence, RiverDelta, RiverIsland, RiverSource, SecludedCove, Tombolo, Valley — the coast/river family plus Gorge and Valley (Gorge and Valley are dryland-relevant).

## spec
- Diff one small case (`LandformValley.xml`: 3 objects vs 2 emitted) — find which `<Object refID>` the parser drops: likely a `<Variable>` inside a dynamic Port's sub-block or a NodeSide, or an Object referenced by a node child the parser treats as scalar. Fix `_parse_source`/`_read_objects` so every refID in the source is carried.
- Make the selftest iterate ALL files in `Landforms-v1/` (census-identical nodes/fields/ports/connections AND Objects type list), not DesertPlateau alone — that single-source selftest is what let the MapSide bug through. Print per-file OK; `SELFTEST PASS 44/44`.
- Live proof for one of the 14 (Gorge — dryland): emitted `RUT_Gorge_probe` on a quicktest, Player.log `Landforms: RUT_Gorge_probe`.

## verify
```
PROVE   rebuild-all shows 44/44; GL log names the emitted Gorge on a quicktest
EXPECT  0 object-count mismatches; no 'Caught exception while loading landform' line
LIES    a rebuild that matches counts but drops a refID and re-numbers — compare the SET of Object type strings and each Variable's refID→type binding, not counts
```
