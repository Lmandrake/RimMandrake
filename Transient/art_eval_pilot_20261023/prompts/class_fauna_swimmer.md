# Class prompt — fauna: SWIMMERS and AMPHIBIANS (pool fish, eels, water creatures)

Read `00_preamble.md` first. Swimmers live in water but are still drawn as body sprites with south, east and
north facings; amphibians may add a **swimming lane** (`swim_<facing>`) drawn at the water surface.

Look for:
1. Everything in `class_fauna_walker.md`: facings (a fish's south shows its face head-on, its north its tail end;
   no overhead view), alien design, scale, style, donor stand-ins.
2. **A water animal drawn as a water animal** (`DESC_MISS`, `PLACEHOLDER`): a land reptile, tortoise or snake
   standing in for a fish or eel is a placeholder → delete.
3. **Realistic and specific, not cute** (`STYLE_CARTOON`): fins, gills, skin texture readable; the description's
   signature feature present.
4. **Swimming lane** (`SWIM_WATERLINE`): reads as the animal at the surface (submerged parts subdued or cut by the
   waterline), same palette and size as the body facings; no painted water rectangle (`ALPHA_HALO`).
5. **Scale** from the description ("hand-length", "forearm-length", "cat-sized"): small fish must still read at
   32 px/cell (`LEGIB_32`).
6. Canon `Must show` for Star Wars amphibians, including how it sits in water (e.g. floats flat vs submerged).
