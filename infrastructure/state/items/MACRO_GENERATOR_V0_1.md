# MACRO_GENERATOR_V0_1 — the map-maker, first version: ONE idea per map

Spec source: `design/RimMandrake/map_content_injection_research.md` §9.2-9.3 step 4
(owner ruled "yes, go" 2026-09-06; corpus statistics allowed as calibration and
regression, never acceptance). Terrain route decided: GL graphs (§5.8).

## spec

- Input: a biome sheet paragraph (`design/Jawa/worldbuilding/biomes/*.md`, start
  with the deep desert / wasteland sheets) + a seed. Output: a **PLAN** (readable
  JSON: `premise`, `landform`, `hydrology` with its cause, `anchor` cell + what sits
  there, `history` one line, `deletions` — what the premise forbids) and a
  **terrain grid** (defName per cell, the `render_terrain.py` text format) for
  offline rendering, plus — once `GL_GRAPH_EMITTER_1` lands — a GL graph.
- The **chooser** is the item. It picks exactly ONE landform class from the
  vocabulary (the GL landforms that fit dryland: DesertPlateau, Badlands, Canyon,
  Crater, Rift, Gorge, Sinkhole, Caldera, Cirque, LoneMountain, SecludedValley;
  plus vanilla mutators), ONE anchor by the compositional-anchor rule (§5.5 #2),
  ONE history line, and then SUBTRACTS everything the premise contradicts (§5.5
  #10). No map may carry two premises.
- Meso texture from `rimbench/scatter.py` primitives (`fbm`, `walk`, `blob`,
  `ring`, `zones`), parameters read from `research/RimMandrake/reference/
  corpus_map_stats.md` ranges (calibration), never hand-tuned to a single map.
- Gates before anything is rendered: connectivity and buildable-area (P12's
  flood-fill, computed offline on the grid), rule 8 vetoes.
- Deliverable for the owner: ONE comparator sheet (`render_terrain.py --sheet`):
  8 generated maps at 250² beside the 5 arid corpus maps at 250² crops
  (InMemoryOfRain, DesertedTrader, LushRiver, PointSea, BloodGulch), captions
  naming each map's premise. He keeps/cuts on the review sheet. First grading
  question, before any other: **can you see the one idea at thumbnail size?**
- Regression: `corpus_stats.py` over the 8 generated grids; report which features
  fall outside the corpus range. Outside is information, not failure.

## verify

```
PROVE   the comparator sheet exists and the owner has marked keep/cut on it
EXPECT  ≥3 of 8 generated maps read as one premise at thumbnail size (owner's call); every generated map passes the connectivity gate
LIES    a map that matches every statistic and reads as nothing; a chooser that always picks the same landform (check the 8 premises are ≥4 distinct)
```

## not chasing

Structures, residents, dressing (steps 7-9), the micro synthesis (step 5), the
LLM plan author (step 8). Terrain and one idea, nothing else.
