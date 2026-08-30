# RimMandrake Spikes — compile-only risk proofs (FABLE_HANDOFF_SPRINT_1, 2026-08-30)

**Never deployed, never loaded.** These skeletons exist so the builder of
`RimMandrake Pits` and the Salvation engine inherits verified API shape instead
of guesses. All three **COMPILE CLEAN (0 warnings, 0 errors)** against the live
1.6 `Assembly-CSharp` + Harmony with:

```
"%USERPROFILE%\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\Spikes\Spikes.csproj -c Release
```

`bin/`/`obj/` are build artifacts — never commit them. One compile fix already
eaten for you: there is no `this.TrueCenter()` extension visible here; use
`DrawPos`.

## Spike 1 — terrain-mimic pit cover (`Spike1_TerrainMimic.cs`)

- **VERIFIED-IN-SOURCE:** `BuildableDef.graphic` (public, BuildableDef.cs:122) ·
  `DrawMatSingle => graphic?.MatSingle` (:146) · TerrainDef *is* a BuildableDef,
  so `Position.GetTerrain(Map).graphic.MatSingle` is the very material the
  terrain layer renders · `Thing.Print(SectionLayer)` (Thing.cs:1333) ·
  `Printer_Plane.PrintPlane(MapDrawLayer, …)` (Printer_Plane.cs:50 — 1.6 takes
  `MapDrawLayer`; `SectionLayer` derives from it, so passing the layer works).
- **The trick:** override `Print()` and print a plane with the terrain's own
  material — no texture copying; terrain shaders UV by world position, so the
  cover should tile seamlessly into the ground around it.
- **Runtime questions (FOUNDRY quicktest):** ① altitude layer choice so the
  cover prints above terrain, below pawns, without z-fighting (try
  `FloorCoverings`); ② does the seam actually vanish (the whole point — LOOK at
  it); ③ dirty the section (`Map.mapDrawer`) when terrain under the cover
  changes, or accept staleness.

## Spike 2 — pit cell holding (`Spike2_PitCellHolding.cs`)

- **VERIFIED-IN-SOURCE:** `Building_HoldingPlatform : Building,
  IThingHolderWithDrawnPawn, IThingHolder, IRoofCollapseAlert,
  ISearchableContents` (Building_HoldingPlatform.cs:10); one pawn in a
  `ThingOwner innerContainer`; the building draws its captive via
  `HeldPawnDrawPos_Y / HeldPawnBodyAngle / HeldPawnPosture`.
  `CompHoldingPlatformTarget.Notify_HeldOnPlatform` (CompHoldingPlatformTarget.cs:228)
  is the transfer-in choreography (clears lord, refreshes dynamic components).
- **The trick:** implement the same interfaces on `Building_PitCell` and let the
  engine's existing holder plumbing (rendering, Scribe via ThingOwner) work for
  us; depth is just a negative draw offset where the platform lifts +0.15.
- **Runtime questions:** ① prisoner intake job (model on
  `JobDriver_CarryToEntityHolder`) — entities flow via CompHoldingPlatformTarget,
  prisoners will need our own JobDef; ② feeding through the gate (captives in a
  ThingOwner are not room-prisoners — custom feed job); ③ negative-offset drawing
  may clip under the terrain mesh — fallback is a masked upper-body render;
  ④ escape struggle ticker is sketched inert in `Tick()` — the odds curve lands
  with the build.

## Spike 3 — threat-point replace (`Spike3_ThreatPointReplace.cs`)

- **VERIFIED-IN-SOURCE:** `StorytellerUtility.DefaultThreatPointsNow(IIncidentTarget)`
  — public static float, StorytellerUtility.cs:131, and it IS the single choke
  point: ~50 call sites including `IncidentWorker_RaidEnemy.cs:88`,
  `IncidentWorker_RaidFriendly.cs:69`, quest sizing, site gen, Anomaly spawners.
- **The trick:** one Harmony Postfix scaling `__result` modulates every threat
  consumer at once — the F12 replace-don't-stack ruling in five lines. The F18
  Visibility dial plugs in at `VisibilityStub.VisibilityFactorFor`.
- **Runtime questions:** ① non-raid consumers read the same number (thrumbo herd
  size, quest rewards, Anomaly curves) — probably gate on
  `target is Map map && map.IsPlayerHome`, then decide the rest per-consumer;
  ② mod-conflict ordering via `[HarmonyPriority]` only if a real collision shows.
