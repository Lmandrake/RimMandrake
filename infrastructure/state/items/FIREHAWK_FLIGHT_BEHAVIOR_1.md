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
### attempt 1, 2026-09-19 (background subagent) — blocked on art-gen quota, wiring deferred
Filed 15 artpipe jobs (`FireHawk_Flying_<1-5>_<north|east|south>.png`, 5 frames
— tucked/upstroke-peak/full-spread/downstroke-power/recovery). **All 15
failed immediately**: the codex channel is quota-exhausted account-wide until
**2026-09-21 09:32** (confirmed from `worker_stderr_tail` on each
`infrastructure/artpipe/failed/rut_firehawk_flying_*.manifest.json`). No
local codex/gemini CLI fallback exists in this environment; gemini is
policy-disabled for this daemon ($0 budget). **No PNGs were fabricated** —
correctly refused rather than faking placeholder art.

The subagent also wired `flyingAnimation*` fields onto the PawnKindDef
pointing at those not-yet-existing frames, reasoning from CLAUDE.md's "never
block flight waiting on frames." **That wiring was reverted before commit**:
the CLAUDE.md guidance covers fields being *absent* (no animation defined at
all, definitely safe); it says nothing about fields *present* pointing at
missing texture files, and the subagent's own report flagged this exact gap
as unverified (RimSage/engine access unavailable on this machine). Given
`flightStartChanceOnJobStart 0.15` means FireHawk will actually attempt to
fly in the live, actively-played campaign, shipping an unverified "what
happens when GetBestFlyAnimation's texture lookup misses" is the same class
of mistake this item already cost once (a visibly broken flying animal the
owner had to catch live). Reverting costs nothing — the block is preserved
below, ready to re-apply once art exists.

**Re-do once art lands**: run
`python3 src/RimMandrake/Utils/artpipe/requeue_quota_failures.py` after
2026-09-21 09:32 to regenerate the 15 filed jobs (already sitting in
`infrastructure/artpipe/failed/rut_firehawk_flying_*.json`, committed this
pass), then re-add this exact block as a sibling of `<lifeStages>` on
`RUT_FireHawk`'s PawnKindDef, deploy, and **verify live — step ticks to an
actual takeoff, not a standing screenshot** — before considering the missing-
texture-fallback question settled one way or the other:

```xml
<flyingAnimationFramePathPrefix>Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_</flyingAnimationFramePathPrefix>
<flyingAnimationFrameCount>5</flyingAnimationFrameCount>
<flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
<flyingAnimationDrawSize>1.35</flyingAnimationDrawSize>
<flyingAnimationDrawSizeIsMultiplier>false</flyingAnimationDrawSizeIsMultiplier>
<flyingAnimationInheritColors>true</flyingAnimationInheritColors>
```

Frame count (5, Locust's) and `ticksPerFrame` (2) are defaults, not gates —
adjust freely once real art is in hand. **One measured finding worth
keeping**: read live against all 5 vanilla flyers in the
`2026-09-19T18-15-44Z` def dump rather than trusting CLAUDE.md's single
Chicken example — Chicken is the ONLY one of the five using
`flyingAnimationDrawSizeIsMultiplier=true` (2.4); Duck (1.7), Goose (1.35),
Sparrow (2) and Locust (1) all use `false` with an absolute cell size. The
block above follows the 4-of-5 majority (`false`, absolute `1.35` against
this creature's 1.1 grounded adult drawSize) rather than copying Chicken's
outlier pattern — if a future pass copies CLAUDE.md's Chicken example
verbatim without re-checking this, it's copying the minority case.

## sweep — other flying Pyrelands roster kinds
`RUT_FireWasp` also carries `MaxFlightTime`/flight race fields (from the same
"Flyers fly" pass) and has no render-tree/Spastic wiring to retire — it never
got one. It is in the same "flies, no animation frames yet" state as FireHawk
now is, and is an equally in-scope target for the flip-book work above when
picked up. `RUT_FurnaceBeast` is a quadruped, not a flier. Ash'karr's biome
`wildAnimals` lists reference donor birds (not our art to rewire here) — not
re-swept this pass, see the v1 sweep note above for the original scope.
