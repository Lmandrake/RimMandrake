# FIREHAWK_FLIGHT_BEHAVIOR_1 — donor-style wing flap → real flight animation

## history
v1 (below, superseded): a `PawnRenderNodeProperties_Spastic` wing-split render
tree was identified as riding a vanilla engine class (zero new C#) and later
actually built (`RUT_FireHawkRenderTree.xml`: custom `RUT_FireHawkBody` +
`PawnRenderTreeDef` wing overlay). Owner's own live test found it broken:
standing still sideways with no visible flap, and north missing one wing
entirely with the other misaligned. Root cause is architectural, not a bug to
patch — Spastic drives a small idle wiggle on ONE static texture per node; it
was never a per-facing, per-frame flying animation, and nothing keeps a single
wing texture aligned across four facings. `CLAUDE.md` and
`skills/generating-rimworld-sprites/SKILL.md` were corrected 2026-09-19 with
the real mechanism: `PawnKindDef.flyingAnimationFramePathPrefix`, a whole-body
directional flip-book, MEASURED against Core's Chicken via `resources.assets`
extraction (UnityPy) and frame-diffed to confirm real pose change.

## done this pass — retired the broken mechanism
- `RUT_PyrelandsFauna.xml`: `RUT_FireHawk`'s `<race><body>` reverted
  `RUT_FireHawkBody` → vanilla `Bird`; `<renderTree>RUT_FireHawk</renderTree>`
  removed entirely.
- `RUT_FireHawkRenderTree.xml` deleted (the custom BodyDef + BodyPartGroupDef +
  Spastic PawnRenderTreeDef).
- PawnKindDef texPath reverted `FireHawk_Body` → `FireHawk` (the original
  complete flattened sprite, body+wings baked in — the wing-cropped
  `FireHawk_Body_*` split art existed only to pair with the Spastic overlay).
- Deleted the 6 now-orphaned PNGs: `FireHawk_Body_{north,east,south}.png`,
  `FireHawk_Wing_{north,east,south}.png`.
- `validate_patch.py --live`: 0 errors, 0 warnings. `deploy_custom_mods.py
  --prune --apply` on UtinniPatches: 8 files, VERIFIED in sync.
- **The flight STAT is untouched and was already correct**: `MaxFlightTime 30`,
  `FlightCooldown 5`, `flightStartChanceOnJobStart 0.15`, `flightSpeedFactor
  2.5`, `canFlyIntoMap`/`canLeaveMapFlying` all still on `RUT_FireHawk`'s
  `<race>` block, landed by an earlier pass ("Flyers fly" standing rule,
  `3785aac81`). FireHawk still flies; it just draws its correct static sprite
  instead of a broken wing overlay while doing so.
- Needs a restart to take effect (defs parse at startup only) — not yet taken,
  batching with other pending def changes rather than restarting for this
  alone.

## owed — the real flip-book animation
Not attempted this pass (art-generation-heavy, scoped separately):
1. Author `frameCount x {north,east,south}` whole-body directional flip-book
   frames (`FireHawk_Flying_<N>_<direction>.png`) via the
   `generating-rimworld-sprites` skill, style-matched to the existing
   `FireHawk_{north,east,south}.png` grounded art. Core's own retrofits ship
   8 frames (Chicken/Duck/Goose/Sparrow); a smaller frameCount (e.g. 4-6) is
   an acceptable v1 per CLAUDE.md ("never block flight waiting on frames" —
   the mechanism already flies with zero frames, animation is additive).
2. Wire `flyingAnimationFramePathPrefix`, `flyingAnimationFrameCount`,
   `flyingAnimationTicksPerFrame`, `flyingAnimationDrawSize` (+
   `flyingAnimationDrawSizeIsMultiplier`) onto `RUT_FireHawk`'s PawnKindDef —
   shape and defaults in `CLAUDE.md`'s "If it flies in the fiction" section.
3. Re-verify live: step ticks to an actual takeoff (not a standing
   screenshot) and confirm the flip-book plays and lands cleanly back on the
   grounded graphic.

## sweep — other flying Pyrelands roster kinds
`RUT_FireWasp` also carries `MaxFlightTime`/flight race fields (from the same
"Flyers fly" pass) and has no render-tree/Spastic wiring to retire — it never
got one. It is in the same "flies, no animation frames yet" state as FireHawk
now is, and is an equally in-scope target for the flip-book work above when
picked up. `RUT_FurnaceBeast` is a quadruped, not a flier. Ash'karr's biome
`wildAnimals` lists reference donor birds (not our art to rewire here) — not
re-swept this pass, see the v1 sweep note above for the original scope.
