# DEEPFIRE_PAINT_LIVE_VERIFY_1

Caused by `DEEPFIRE_PAINT_STATUS_CUISINE_1` (closed, partial): the two of its five mechanisms
that mod's own spec explicitly gates on a live game, not a def dump. Full authority:
`design/RimMandrake/deepfire_luminous_pigment_spec.md`.

## Which NEW mechanism has never once been observed running

The proxy-glower light shape itself — an unspawned `ThingWithComps` vs. a spawned
invisible 1x1 Thing registering a `CompGlower` and lighting `map.glowGrid.GroundGlowAt`.
Neither shape has been built or run here. Spec §10 step 1 is explicit that this decision
gates everything built on top of it (walls, floors, worn items) and must be decided by a
bridge quicktest reading `GroundGlowAt` before/after moving the proxy — not guessed from
source, because the question is runtime behaviour (does an unspawned proxy actually light
the grid), which reading the decompiled engine cannot answer. This is the mechanism; every
later state (a coated wall glowing, a worn robe's moving light) is the SAME untested
mechanism reused, not a new one.

## Scope (spec §1/§2 mechanism list)

1. **Painting (spec §3).** `CompDeepfire` injected into every paintable/colourable/art/
   apparel/weapon def; `RM_Designator_Deepfire`/`RM_Designator_RemoveDeepfire` +
   `RM_WorkGiver_ApplyDeepfire` + `RM_JobDriver_ApplyDeepfire`; up to three coats; the floor
   grid (`floorCoats[]`, postfixes on `TerrainGrid.SetTerrainColor`/`DoTerrainChangedEffects`);
   contiguous-cell clustering into one proxy light per 3x3 block
   (`RM_MapComponent_DeepfireLights` — the type `HediffComp_DeepfireGlow.DeepfireLightsBridge`
   in `mandrake.rm.luminouspigment` already reserves this name and soft-binds to it by
   reflection, so Cuisine's glow-hediffs light up for free the moment this ships); the
   first-coat quality bump (art) / `RM_StatPart_Deepfire` beauty bonus with the two floor-only
   bonuses (`BeautyUtility.CellBeauty` postfix — UNMEASURED signature in the spec, RE-CHECK via
   RimSage before building, it may already be resolvable offline even though the light
   mechanism is not).
2. **Worn-item glow + the darkness-targeting tradeoff (spec §3.4).** The per-pawn proxy light;
   the press's "lacquer worn item" gizmo + `RM_JobDriver_LacquerWornItem`; the Ideology
   styling-station checkbox. The combat tradeoff (Harmony postfix on `ShotReport.HitReportFor`
   + `RM_StatPart_GlowingTarget` on `MeleeDodgeChance`) needs spec §10 step 8's own live bridge
   quicktest: compare `HitReportFor` numbers on 20 paired coated/uncoated test pawns
   (`spawn-many-for-bridge-tests` pattern) — no live shooting needed, but a live game is.

## What already exists to build on (do not re-invent)

- `RM_Deepfire`, `RM_CrowncarpetFresh/Dead`, the press and the GlowTank ship
  (`DEEPFIRE_PIGMENT_MOD_1`, closed).
- Cuisine's 14 glow-hediff families, 15 recipes, the chef-steering comp/doer pair, the
  Ninefold god bridge (`NinefoldDeltaBridge.cs`), and the sumptuary status engine's
  worn-goods thoughts all ship (`DEEPFIRE_PAINT_STATUS_CUISINE_1`, closed, partial) —
  `src/RimMandrake/LuminousPigment/`.
- `HediffComp_DeepfireGlow.cs`'s `DeepfireLightsBridge` already defines the CONTRACT this
  item's `RM_MapComponent_DeepfireLights` must satisfy: static `RegisterHediffGlow(Pawn,
  HediffDef, Color, float)` / `DeregisterHediffGlow(Pawn, HediffDef)`. Match that shape (or
  update the bridge in the same commit if a different shape proves necessary) so Cuisine's
  glow-hediffs light up without a second change.
- `StatusGoodExtension`/`SumptuaryUtility` (in `SumptuaryEngine.cs`) already compute a pawn's
  display score generically from any def carrying the extension. Once `CompDeepfire` exists,
  add a branch there reading `CompDeepfire.coats` directly (spec §4.1: "Deepfire is detected
  by comp, not by extension") — a small addition, not a redesign.
- `RM_WearsAboveStation`/`RM_WearingDeepfireTitled`/`RM_WearingDeepfireCommon`/
  `RM_SawCommonerInDeepfire` ship; `RM_DeepfireBedroom` and `RM_ImpressedByDeepfire` (spec
  §4.1) still need a room-stat hook over painted furniture — build those here alongside the
  floor/room beauty bonuses, not as a separate item.
- `NinefoldDeltaBridge.ApplyDelta` ships and is proven working (dish-eaten delta, vermilion
  Ishko penalty). The remaining §5.2 event rows (first coat, worn coat, sold, statue-coat) are
  one `ApplyDelta` call each from wherever `CompDeepfire` raises the event — wire them here,
  not a new bridge.
- `DeepfireGodExtension` (statue hook) ships, unused; the Utinni statue mod can already tag
  idols with it today.

## Build order

Spec §10 steps 1, 5-10 (2-4 done; 11 done; 12 partial — Mod Settings for painting/worn-glow/the
remaining god deltas/the two room-stat thoughts ship here too, per the standing Mod Settings
rule: a toggle for a mechanism that doesn't exist is a stub). Step 1 (the proxy-glower
quicktest) is the one hard prerequisite for steps 5-8; it does not gate 9-10 (already partially
done) further than they already are.

## Needs

`bridge` — step 1's quicktest and step 8's `HitReportFor` comparison both need a live game, per
the spec's own words, not a def-dump guess.
