# LIGHTFALL_CHASM_AUTHORING_1 — author the Lightfall chasm landmark

Spec source: `design/Jawa/worldbuilding/biomes/forsaken_crags.md` §3 (owner-ratified
2026-09-06). Bridge work; needs game-up.

## spec

- **Site (MEASURED, ruled):** the Damp chain — 32 `AB_RockyCrags` tiles straddling arc 90,
  lat −37→−64, lon 86–97. Center the feature on the arc-90.0 spine (tiles 12253, 15934,
  107, 7924, 1445, 15951); deepest point **tile 9023** (hilliness 5, elev 919 m).
- **Name:** Lightfall (owner's pick — where light falls in; the one place the Dark always
  dies).
- Author as a worldmap landmark/named feature via the `jawa/world_*` tools; remember
  `world_commit` or nothing is visible (rimworld-world-editing skill).
- 🔴 Anti-bullseye caveat rides this work: no regularizing the crag/wasteland interleave
  into rings while editing.

## verify

Read the landmark back from the live world after commit (world read tools, not the write's
return value); confirm name and tile anchor.
