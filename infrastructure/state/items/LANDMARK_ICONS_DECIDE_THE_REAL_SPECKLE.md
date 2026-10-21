# LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE

`LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE` — measured, owner decision owed; NEXT: show the owner `D:\ClaudeWork\rimmandrake\scratch\hilldecals\PHONE_hills_Rust_Cathedral_before_after.png` and ask by question card: keep the landmark icons as they are, draw them faded/smaller (a look-only RM_WorldLook option), or fewer landmarks on the Rust Cathedral (a world edit).

## Finding (2026-10-20)

The white and grey speckle in the Rust Cathedral on the live map is not hill decals. It is Odyssey **landmark icons**.

- `WorldDrawLayer_Landmarks` prints one quad per Standard landmark. A landmark that draws above roads is lifted +0.025, so it sits over rivers and roads too.
- The icons in this region are `World/Landmarks/Ruins`, a 2x2 atlas of grey building clusters, and `AncientVents`, the spirals.
- On `world/ASHKARR_DEV_START_2026-10-20.rws`, **155 of the 236 Rust Cathedral tiles carry a landmark**:
  - Ruins 68
  - AncientHeatVent 28
  - RUT_ComplexStructures 18
  - TerraformingScar 18
  - AncientGarrison 7
  - others
- The planet has 3,008 landmarks.
- A tile with a landmark draws no hill. That is why softening the hills (`HILL_DECALS_VERIFY_NO_MORE_COOKIE_CUTTERS`) does not change this region.
- An offline render with the landmark icons drawn matches the live screenshot `D:\ClaudeWork\rimmandrake\scratch\live5\V_rust_stipple.png`.

## Options (not built)

1. Keep the icons as they are. Landmarks are gameplay information.
2. Look-only: an RM_WorldLook setting that tints or fades the landmark materials, or draws them smaller. It would be global and reversible.
3. World edit: thin the Rust Cathedral's landmarks. This changes the frozen world, so it needs his word.
