# DEEPFIRE_PAINT_STATUS_CUISINE_1

## CLOSED PARTIAL — what actually shipped

Built and validated (`src/RimMandrake/LuminousPigment/`, `mandrake.rm.luminouspigment`):

- **Cuisine (§6), in full**: 14 `HediffDef` glow families with 3 severity tiers each
  (`Defs/HediffDefs/RM_DeepfireGlowHediffs.xml`), 15 `RecipeDef`s on any stove
  (`Defs/RecipeDefs/RM_RecipeDeepfireMeals.xml` + `Patches/DeepfireMealsOnStoves.xml`, since
  `RecipeDef` has no `recipeUsers` field — RimSage-verified), the generic chef-skill-steered
  comp/doer pair (`CompSkillSteeredOutcome.cs` + `IngestionOutcomeDoer_SteeredFamily.cs` +
  `GenRecipePatch.cs`'s postfix on `GenRecipe.MakeRecipeProducts`), the vermilion's
  steered-only/never-random/Cooking-14 gate, the 3-family cap, and mood-linked ThoughtDefs.
  Two named-UNMEASURED cells shipped with their own named XML-only fallback (eye-glow's
  darkness exemption, gut-glow III's diet); several purely cosmetic sub-details were trimmed
  (filth reskin, breath flecks, rest-cap/lit-dreams) — see the file header comment in
  `RM_DeepfireGlowHediffs.xml` for the exact list. All offline-verifiable; no live test needed
  for any of it (RimSage confirmed every stat/class/field referenced against the decompiled
  1.6 source, and `validate_patch.py --defs` against the live 628-mod active list found 0
  errors).
- **Ninefold god reactions (§5), partial**: `NinefoldDeltaBridge.cs` (the reusable
  reflection-bound `ApplyDelta` wrapper) and `DeepfireGodExtension` (the statue hook, unused
  but ready) ship. Only the two §5.2 event rows wireable without `CompDeepfire` are wired: "a
  Deepfire dish eaten" (Zizzik/Ozzik +Small) and the vermilion's "cannot be hidden — Ishko
  −Medium on reaching III". The coat/worn/sold/statue-coat deltas need `CompDeepfire`
  (piece 1, deferred).
- **The purple engine / sumptuary status (§4), partial**: `RM_SumptuaryEngine`'s generic
  machinery ships (`SumptuaryEngine.cs`'s `StatusGoodExtension` + `SumptuaryUtility`, rank via
  Royalty title / Ideology role, degrading gracefully with neither DLC) plus three of its five
  ThoughtDefs (`RM_WearingDeepfireTitled/Common`, `RM_WearsAboveStation`,
  `RM_SawCommonerInDeepfire`) — all real and testable, currently inert because nothing is yet
  tagged with `RM_StatusGoodExtension` (exactly the standing Mod Settings rule's "all-off
  degrades gracefully", not a stub). `RM_DeepfireBedroom` and `RM_ImpressedByDeepfire` need a
  room-stat hook over painted furniture, deferred with painting.
- Real Mod Settings for everything above (Cuisine/Gods/Status groups in
  `LuminousPigmentMod.cs`), including a genuine recipe-visibility gate (`cuisineEnabled`
  removes/restores the 15 recipes from `ElectricStove`/`FueledStove` at startup, since a
  `RecipeDef` has no hide flag of its own) and live skill-requirement sync
  (`steerMinSkill`/`vermilionMinSkill`).

**Deferred to `DEEPFIRE_PAINT_LIVE_VERIFY_1`** (filed, `needs: bridge`): painting (§3) and
worn-item glow + the darkness-targeting combat tradeoff (§3.4) — both explicitly gated by the
spec's own live proxy-glower quicktest (§10 step 1) and, for the combat tradeoff, a live
`ShotReport.HitReportFor` comparison (§10 step 8). Building `HediffCompProperties_
DeepfireGlow`'s soft `DeepfireLightsBridge` and `SumptuaryUtility`'s extension point in THIS
pass means that follow-on's light/status work slots in without redesigning either.

Build: `"%USERPROFILE%\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\
LuminousPigment\Source\RM_LuminousPigment.csproj -c Release` — 0 warnings, 0 errors.
`validate_patch.py --defs` against the live 627-active-mod install (Data + Mods + Workshop
content) — 0 errors, advisory warnings only (vanilla-asset texPath, unbuilt-DLL class-not-
found info lines matching the mod's own already-shipped defs' pattern).

---

## Original prose

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
