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

## done (FOUNDRY, 2026-09-12)

Tile 9023 already carried a `Chasm`-def landmark, auto-named "Clam Chasm" — the feature
itself needed no authoring, only the name. `jawa/world_landmark_rename` (tile 9023 →
"Lightfall"), then independently re-read via `jawa/world_mutators_get` (not the rename's
own return value): `landmark: "Chasm", landmarkName: "Lightfall"`. No `world_commit`
needed — landmark names redraw per frame, unlike a landmark add.

Correction to the item's own MEASURED line: live `world_tile_get` on 9023 reads
`hillinessInt: 4` (Mountainous), not 5 (Impassable) as filed — still clears
`TileMutatorDef Chasm`'s `minHilliness: Mountainous` gate either way.
