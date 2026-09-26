# DEEPFIRE_PAINT_STATUS_CUISINE_1

Deferred out of `DEEPFIRE_PIGMENT_MOD_1` (the LuminousPigment mod's Phase 1 build,
`src/RimMandrake/LuminousPigment/`, ships the chain: crowncarpet, its one-day
clock, the Deepfire press + hidden research, Deepfire itself, and the GlowTank).
Full authority: `design/RimMandrake/deepfire_luminous_pigment_spec.md` — every
question in it is already RULED (§11: "None. Q1–Q12 are all ruled"). This item is
not blocked on the owner; it is blocked on size. Five separate mechanisms, each
real, separately buildable work:

## 1. Painting (spec §3)
`CompDeepfire` injected at startup into every paintable/colourable/art/apparel/
weapon def; `RM_Designator_Deepfire`/`RM_Designator_RemoveDeepfire` +
`RM_WorkGiver_ApplyDeepfire` + `RM_JobDriver_ApplyDeepfire`; up to three coats,
radius/intensity per coat; the floor grid (`floorCoats[]`, postfixes on
`TerrainGrid.SetTerrainColor`/`DoTerrainChangedEffects`); contiguous-cell
clustering into one proxy light per 3x3 block (`RM_MapComponent_DeepfireLights`);
the first-coat quality bump (art) / `RM_StatPart_Deepfire` beauty bonus
(everything else) with the two floor-only bonuses (per-cell `CellBeauty`
postfix, per-room `RoomStatWorker_Beauty` postfix). Needs: a Harmony postfix
into `BeautyUtility.CellBeauty` whose signature the spec itself flags
UNMEASURED (fallback named: postfix `AverageBeautyPerceptible` instead), and
the build plan's own step 1 (a proxy-glower quicktest deciding unspawned vs.
spawned-invisible-Thing shape) gates everything else in this list — it must
run and pass BEFORE any of steps 5-9 below are built on top of it.

## 2. Worn-item glow + the darkness-targeting tradeoff (spec §3.4)
The per-pawn proxy light (`RM_MapComponent_DeepfireLights`, one light per
glowing pawn, moved every `wornLightTickInterval` ticks); the press's "lacquer
worn item" gizmo + `RM_JobDriver_LacquerWornItem`; the Ideology styling-station
checkbox (needs the same mod's `Dialog_StylingStation`/`JobDriver_UseStylingStation`
patch pattern other Ideology-touching mods here use — FOUNDRY to find the
precedent). The combat tradeoff: a Harmony postfix on `ShotReport.HitReportFor`
(ranged) and `RM_StatPart_GlowingTarget` on `MeleeDodgeChance` (melee), both
gated on "dark, and not lit by our own glow" — needs a live bridge quicktest
(spec §10 step 8: compare `HitReportFor` numbers on 20 paired coated/uncoated
test pawns, no live shooting needed, `spawn-many-for-bridge-tests` pattern).

## 3. The purple engine — sumptuary status (spec §4)
No such engine exists yet (MEASURED 2026-09-25: `sumptuary`/`tyrian` match
nothing under `src/`, `design/` or the live items) — "the purple engine" is the
owner's own name for this mechanism (named for Tyrian purple), not a system
already in the repo. Ships here as a reusable, generic
`RM_SumptuaryEngine` (namespace `RimMandrake.LuminousPigment.Status`): display
score per pawn/room, rank via Royalty title / Ideology role (degrades to a
plain "nice clothes" thought with neither DLC), five ThoughtDefs (reactions
only — no law, no confiscation, per the 15:42 card ruling). A future
Tyrian-purple-like good hooks it with one `DefModExtension`, not a second
engine.

## 4. Ninefold god reactions (spec §5)
Soft reflection bridge to `mandrake.rm.ninefold`'s `GameComponent_Ninefold`
(copy the `NinefoldBandBridge.cs` pattern from `src/RimMandrake/Aftermath/Source/`)
— nine deltas keyed to coat/wear/sale/eat/statue events, rate-limited by
Ninefold's own band ladder plus a per-def diminishing-returns cap.
`RM_DeepfireGodExtension` is the hook the (not-yet-built) Utinni statue mod
tags its idols with. Inert with Ninefold absent — no-op by construction.

## 5. Cuisine glow-hediff families (spec §6)
Ships in `mandrake.rm.luminouspigment` itself (RM-tier, must not depend on the
RSW-tier `mandrake.rsw.cuisine`): 15 recipes, 14 permanent `HediffDef` families
with 3 severity tiers each (the table in spec §6.3 is complete, including the
two UNMEASURED cells with named XML-only fallbacks — eye-glow's darkness
exemption, gut-glow III's diet), the chef-skill-steering comp/doer pair
(`RM_CompSkillSteeredOutcome` + `RM_IngestionOutcomeDoer_SteeredFamily`,
written generic so Cuisine's own later dishes can reuse it — "a general theme
for Cuisine" per the ruling), max 3 families per pawn, the vermilion
(family 14) steered-only at Cooking 14, never rolled at random.

## Build order and gating
Follow spec §10's own step list (steps 1-12; steps 2-4 are DEEPFIRE_PIGMENT_MOD_1's
chain, already built). Step 1 (the proxy-glower quicktest) is the one hard
prerequisite: it decides the light-proxy shape every one of §1/§2/§3's lights use,
and the spec is explicit that nothing downstream should be built on a guess here.
Steps 9-11 (status, gods, cuisine) do not depend on the proxy-glower decision and
could be built and quicktested independently/in parallel if that is useful.

## What NOT to do
Do not guess "god reactions" beyond what §5 already specifies (it is fully
ruled, not vague — the phrase in the original one-line item title just compresses
a fully-specified table). Do not build the FlowWorks ocean-water requirement for
the GlowTank here either — that gap is noted in `RM_GlowTank.xml`'s own header,
filed as a sub-note of this item rather than a sixth top-level mechanism, since
it is a small addition to an already-shipped building, not a new mechanism.
