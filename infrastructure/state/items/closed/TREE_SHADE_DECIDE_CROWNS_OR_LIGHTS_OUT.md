# TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT: owner picks the tree shade model before the build

Design: `design/RimMandrake/tree_shade_model_2026-10-19.md` §7. **Needs:** owner, by question card.

Owner, 2026-10-19: *"If we have an excellent tree shade model working, then YES direct sun works the
same everywhere on the day side. If we do not go that route, we may choose to turn it off on
tree-heavy maps (this would be an inferior option)."*

## Questions

- **Q1. The model.**
  - Projected crown (recommended): about 4.5 agent-days. Forests are mostly shade and clearings are
    sunlit, from geometry alone.
  - Direct Sun off on tree-heavy maps: about 0.5 days. It is all-or-nothing and brings back an
    exception. If chosen, key it on the map's measured canopy fraction, never on the biome.
- **Q2. Crown shade.**
  - Full (recommended).
  - Dappled, with an opacity per species to tune.
- **Q3. How shade shows.**
  - Overlay toggle plus mouseover (recommended).
  - Also a subtle ground tint, about +1 day.
  - Also rendered crown shadows, which is art and shader work.
- **Q4. What counts as a tree.**
  - Anything drawn 1.5 cells or larger (today's rule).
  - Only woody trees by the vanilla test. This leaves the Fever Wood and the Webwork shadeless,
    because their canopy trees are not tagged `Wood`.
  - A per-def list.

Still owed from the parent design, unchanged: the D5/D6 confirm
(`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md` §8).
