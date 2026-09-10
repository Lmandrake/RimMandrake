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

## Round 3 verdict, absorbed 2026-09-10

Round 3's comparator sheet (`Transient/mapgen_v3/comparator_sheet.png`) went to
the owner and came back **FAIL — 0 of 8 premises readable**, against this
item's own ≥3 bar. Full grade and disposition:
`infrastructure/state/items/MAPGEN_ROUND3_VERDICT_LANDING_1.md`.

Three things this item's next round must fix, not the corpus-stats regression:

1. **Passing every measured statistic is not the acceptance test.** A map can
   sit in-band on `corpus_stats.py` and still read as nothing beside the real
   corpus at thumbnail size — the owner's eye is the acceptance gate, the
   stats page above is calibration/regression only, and round 3 confirms the
   spec's own LIES row rather than contradicting it.
2. **A premise must be visible, not just present in the plan JSON.** The
   choke-point premises ("only way through is at the narrows/head/lip/ring
   centre") produced nothing the owner could locate on the rendered map. If a
   passage doesn't read as a passage at thumbnail size, the premise did not
   ship.
3. **The chooser's one-idea-per-map rule is failing at differentiation, not
   just rendering.** Four canyon maps (two sharing a premise sentence) all
   read as the same map. Distinct premises must produce visibly distinct
   maps, or the ≥4-distinct-premises check in this item's own LIES row is not
   actually being tested by the sheet.

Disposition (BENCH's sequencing via the verdict item, owner may veto): **hold
painter round 4.** `MAPGEN_GL_SHEET_1` is now the lead — it settles whether
the gestalt gap is in the content/chooser or in the offline painter's
rendering, before another painter iteration spends effort on the wrong side of
that question. Do not tune the next round toward `corpus_stats.py` — it is
measuring the wrong thing per the verdict; treat it as a regression check
only, never the pass/fail bar.
