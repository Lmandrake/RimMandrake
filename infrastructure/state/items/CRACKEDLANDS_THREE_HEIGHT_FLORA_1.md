# CRACKEDLANDS_THREE_HEIGHT_FLORA_1 — qirra mats and talus clasps

Split from `CRACKEDLANDS_GPT_ENRICHMENT_1` §4. Coordinate with `BEDAZZLE_FLORA_EXPANSION_1` (BENCH),
which also owes this biome flora. The spec says: **art to an owner review sheet before any def
ships.**

## spec (as picked)

Red-brown **qirra mats** open only on recently wetted open clay. The Veqma (existing, `RM_Veqma`)
maps hidden water in the blue shade. Pale **talus clasps** root beside fossil-bearing rock and slowly
pry cracks wider. Only the Veqma shows green, and only inside the shade line. PlantDefs with
terrain/glow limits; the flood component wakes the qirra; a placement worker keeps talus clasps on
natural walls; minor harvests only.

## done in the parent

- **Collision sweep, both names clean (2026-10-01):** `qirra`, `talus clasp` and `talusclasp` return
  0 hits in `src/`, `design/` and `infrastructure/artpipe/`, and none in any installed workshop
  `About.xml`. A sanity probe on `veqma` found 5 hits in `src/`.
- No existing art was found in artpipe for either name.

## hooks that exist

- `RM_MapComponent_RecedeAftermath.OnRecede(wetted)` receives the wetted cells at every recede. Wake
  the qirra there.
- `RM_FossilStrata` places the fossil seam things, which are what talus clasps root beside.

## open questions (owner)

1. **What does "pry cracks wider" do in game?** Options: a slow chance to turn the adjacent wall
   cell into a fossil seam or rubble; purely flavour; or a mining-yield bonus next to it.
2. **The harvests**: what each yields, and how much ("minor").
3. **The Veqma shade-line law**: enforce it with a glow limit on the def, or with roster placement.
   This is also open on `CRACKEDLANDS_RULED_CONTENT_1`.

## criteria

Art is reviewed on a sheet before the defs ship. Quicktest: qirra mats appear only on cells wetted by
a recent flood, and talus clasps only touch natural walls (state reads).
