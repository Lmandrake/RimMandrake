# TREE_SHADE_BUILD_CROWNS_ON_STILTS: tree crowns cast Direct Sun shade by sun geometry

Design: `design/RimMandrake/tree_shade_model_2026-10-19.md` (§4 is the model, §5 the cost, §6 the
adopt-or-fall-back test). The estimate behind §2.2 is
`design/RimMandrake/tree_shade_model_2026-10-19_estimate.py`. Nothing here is built.

Owner, 2026-10-19: *"If we have an excellent tree shade model working, then YES direct sun works the
same everywhere on the day side. If we do not go that route, we may choose to turn it off on
tree-heavy maps (this would be an inferior option)."*

**Model: opus.** Tier RimMandrake (`CreatureBehaviors`). **Needs:** offline.

**Blocked on:**
- `TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT` (Q1, the model; Q2–Q4 set its defaults).
- `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`: this item uses its one E and one cover rule. Build it on
  top of that item, or in the same pass.

## spec

1. **A tree is a parasol on a pole.**
   - Every plant with `visualSizeRange.max ≥ 1.5` (or the set Q4 rules) has a crown.
   - Drawn size `s = Graphic.drawSize.x × visualSizeRange.LerpThroughRange(growth)`. This is
     growth-aware: today's code uses `.max`, so a seedling casts a giant's shadow.
   - Crown radius `r = 0.8 × s / 2` and crown height `hc = 0.5 × s`. Both are INVENTED defaults and
     belong in settings or constants.
   - Opacity is 1.0 (Q2). While `Plant.LeaflessNow`, it is × 0.3.
2. **The projection.** The disc is offset down-sun by `min(16, hc × cot E)`, along the same sun vector
   and cap (`MaxCastCells`) as every other caster. The trunk keeps today's strip. Rasterise both into
   `castShade` by max in `RM_MapComponent_ShadeGrid.Recompute`.
   - The pure footprint goes in `RM_SunHeatMath.CrownFootprint`, so the selftest can call it.
   - Reuse `RM_MovingShadeMath.CastBody`'s overhead-plus-strip shape.
   - The non-directional ring path gets the disc with zero offset.
3. **`RM_TreeCrownExtension`** (a DefModExtension on the plant ThingDef, never on a BiomeDef). It
   carries optional `crownRadiusFactor`, `crownHeightFactor` and `opacity`. Give overrides to the
   giants whose sprite misleads: `RM_Greatbole`, `RM_Nogtyl`, `RSW_Plant_HydenockTree_Wild`,
   `RM_CorriskTree`, `RM_Veluthar`, `RM_Kaddrath`. The numbers are INVENTED and the owner tunes them.
4. **Responsiveness.** A caster plant despawning (felled, burned, eaten, crushed) calls
   `RequestRecompute`. Growth is picked up by the 2000-tick recompute.
5. **Readable sign.**
   - A shade overlay toggle in the play-settings row (`CellBoolDrawer`), drawn from the same array
     `ExposureAt` reads.
   - A mouseover cell readout that names the cause: roof, canopy (species), lee, or parasol.
   - The cause word on the `RM_Gizmo_SunLoad` line.
   - The ground tint, only if Q3 says so.
6. **Settings,** in the Direct Sun group (design §4.6): tree canopy shade on/off, canopy shade
   strength, and the overlay button. No per-biome switch.
7. Nothing new is saved. The grid stays derived.

## criteria

- `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE` passes T1, T2 (offline half), T4, T5 and T6 (design §6).
- T3 is shown to the owner in the `DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME` sitting.
- No BiomeDef carries any crown or canopy field (XML parsed as elements).
