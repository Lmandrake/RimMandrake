# PYRELANDS_ULLAI_GIANT_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md` §3 (ruled, owner turn 1 by card: both). Free `RM_` tier, one home each.

1. **The ullai** (`RM_Ullai`, new): long-legged ash-grazer, bs about 1.8, herds of 8 to 20, meat and hide, tameable herd animal. A herd drifts to the freshest burned ground (`RM_SeekTargetExtension` aimed at ash/scorched terrain, informed by `MapComponent_BurnLine`), so where it grazes is where it burned two days ago. Wired inline in `RM_Pyrelands`. Static art only, no new animation.
2. **The furnace-beast grown into a giant:** `RM_FurnaceBeast` bs 3.2 → about 6, commonality about 0.04 (from 0.08), drawn huge on an ordinary pawn footprint. Its warmth radius, bed-down smoulder and fire hazard scale with it; it stays tameable (ruled). New art at giant draw size (art list job `RM_FurnaceBeast_Giant`).
3. Mod Settings: ullai on/off and herd size; giant furnace-beast size toggle.

Depends on `PYRELANDS_FAUNA_TIER_PORT_BUILD_1` and `PYRELANDS_HEAT_KIND_BUILD_1` (warmth radius). Art: `infrastructure/artpipe/art_lists/pyrelands_bedazzle_cast.csv`.

🔴 **North-star re-measure:** `PYRELANDS_NORTHSTAR_TRIAL_1` must re-measure after row 0 (the animal move) lands: it changes the cast the trial's census reads. Sequence with `PYRELANDS_SHIP_READINESS_1`.

## verify
- A Pyrelands map spawns ullai herds that move to fresh ash after a front; a giant furnace-beast reads huge and warms a wider ring.
