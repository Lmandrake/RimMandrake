# PROPANE_LAKE_HYDROCARBON_TENTACLER_1

Owner, Blue Desert sheet 2026-10-04, row Vapaad (verbatim): "Option B is a FANTASTIC creature to move to the Propane Lakes biome, but it's simply not a vapaad (canon creature)... keep Option B in the Propane Lakes."

- KEEP the render `bluedesert_Vapaad_v2` (artpipe `done/bluedesert_Vapaad_v2_{east,south,north}`; find with `artpipe_state.py find vapaad`). Currently installed as `Things/Pawn/Animal/RUT_Vapaad/RUT_Vapaad` and stays there until the canon regen (`vapaad_canon_v1`) is picked.
- NEXT: give it its OWN new invented RM_ name and def (not canon Vaapad, not the donor `Vapaad`) in `RM_PropaneLake` (design a short description, hydrocarbon tentacle predator), copy the art to its own texPath, wire it into the Propane Lake roster (and `fishTypes`/floor rules per the sea-biome ruling if it is a lake resident). `animalDensity` on the lake is still 0 (`PROPANELAKE_ANIMALDENSITY_ZERO_1`).
- Do not delete the v2 art when the canon regen is installed over RUT_Vapaad: copy first.
