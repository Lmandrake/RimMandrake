# WARSCAR_RAINBOW_POOLS_1 — the rainbow pools: colour is a lie you learn to read; glower crust as catalyst

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.9. Ruled turn 2: built
**after** `WARSCAR_HOSPICE_DESERTERS_1`. Turn 4, owner typed *"1+2"*: glower crust is **both** a pool
phase catalyst (here) and radiation/toxic shielding (`WARSCAR_AEROSOL_SCREEN_1` §9).
Hard dependency: FlowWorks (`mandrake.rm.flowworks`).

## spec

1. **The registry row** `RM_Liquid_ReactionLiquor` (pH 2, acid `damageOnImmersion`, `corrodesApparel`,
   terrain suite → the existing `RM_ReactionLiquorShallow` / `…Deep`). **Generator-table work:** edit
   `generate_liquid_suite.py`'s table and regenerate; never hand-edit the XML.
2. **Placement:** a genstep puts 1–3 pools in crater bowls (Odyssey's crater gensteps give the bowls).
3. **The cycle:** `RM_MapComponent_ReactionPools`, 4 phases over 24 h, offset per pool; a tint section
   layer **and a surface icon per phase** (colour-blind safe).
4. **The reagents:** amber → **`RM_DielectricGel`** (the screen's membranes); violet → **`RM_Etchant`**
   (cradle limbs stage; turret refit); pale green → **`RM_MedicalCoagulant`** (a herbal-tier bandage that
   stops bleeding fast); the bloom → **`RM_BloomLiquor`** (high-value trade good; drawing it burns the
   drawer: acid burn plus toxic buildup, the injury named after the phase).
5. **`RM_ReactionTap`** at the rim: a "draw reagent" job whose product follows the phase. A
   `GameComponent` journal records each phase drawn as **known**; until then *"unknown colour"*. The
   **phase reader** (old tongue phase reading) names the phase and lets the tap skip the bloom.
6. **Glower crust as catalyst** (ruled, half 1): loading `RM_GlowerCrust` into a tap (a small
   `CompRefuelable`-style hopper) **holds the pool's current phase** for 6 h per unit and **doubles draw
   yield** while held, so a player can farm one reagent on purpose. Balanced by crust consumption.
7. **Readable signs:** the phase tint and icon; the slow boil (choir); corpses in a pool dissolve to a
   **bone filth** over a day, never to nothing.
8. **Mod Settings:** pools on/off · pools per map · cycle length · bloom danger · catalyst on/off.

## criteria

- The liquid-suite generator emits the registry row; a quicktest Warscar map holds 1–3 pools.
- Each phase's draw yields its reagent; drawing the bloom injures the drawer.
- With glower crust loaded the phase holds and yield doubles; without it, it cycles.
- Dielectric gel refuels `RM_AerosolScreen`; etchant is accepted by the cradle's limbs stage.
