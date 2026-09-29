## Spec row (verbatim, deepfire_luminous_pigment_spec.md §10 step 8)

| # | build | proof |
|---|---|---|
| 8 | Worn items: `Notify_Equipped` path, per-pawn proxy, gizmo + `RM_JobDriver_LacquerWornItem`; the Ideology styling-station checkbox; combat hooks | quicktest at night on an unlit map: pawn in a coated parka walks 30 cells — `GroundGlowAt(pawn.Position)` > 0.3 every 15 ticks along the path (bridge poll, not screenshots); hit-chance readout on a shooter targeting the pawn shows the *glowing in the dark* line and a larger chance than against an uncoated twin (`spawn-many-for-bridge-tests`: 20 pairs, compare `HitReportFor` numbers directly, no live shooting needed); melee dodge stat card shows the offset; with Ideology, a styling job with the box ticked consumes 3 Deepfire and the worn item reads `coats 1` |

## What already exists to build on

- `CompDeepfire` (step 5, closed) already gets injected into apparel/weapon
  defs and tracks coats; `WorkGiver_ApplyDeepfireCrafting` already lets a
  player Deepfire a loose apparel/weapon item on the ground or in storage —
  this item is specifically the WORN case (spec §3.4): a pawn's own gizmo, a
  press job, the styling station, and the darkness-targeting combat tradeoff.
- `MapComponent_DeepfireLights.RegisterHediffGlow`/`DeregisterHediffGlow`
  (step 5's own build, satisfying the contract `HediffComp_DeepfireGlow.cs`
  already soft-binds to for Cuisine) is a PAWN-KEYED registration that
  re-anchors to `pawn.Position` on every call — but it is driven by that
  hediff comp's own 250-tick `CompPostTick`, NOT a continuous per-tick
  tracker. Spec §3.4 wants worn-item movement tracked every 15 ticks
  (`CompTickInterval`), tighter than the 250-tick hediff cadence — this item
  needs to add that tighter polling for worn items specifically (its own comp
  ticking `pawn.Position` into the same `RegisterHediffGlow`-shaped call, or
  a parallel `RegisterWornGlow`/`DeregisterWornGlow` pair on
  `MapComponent_DeepfireLights` — the underlying proxy machinery
  (`SetLight`/`RemoveLight`) is already generic over any key and needs no
  change).
- `RM_DeepfirePress` ships (`DEEPFIRE_PIGMENT_MOD_1`, closed) — the "lacquer
  worn item" job's destination bench already exists.

## Build (spec §3.4)

1. Per-pawn proxy: one light per glowing pawn (not per item) — colour =
   brightest coat's colour blended across the pawn's glowing items, radius =
   pawn's highest coat, moved every `CompTickInterval` 15 ticks by comparing
   `pawn.Position` to the proxy's cell. Skipped while unspawned (caravan,
   carried, in a pod). No off switch (ruling: the trade is real, a pawn who
   does not want to glow takes the robe off).
2. Gizmo *"lacquer worn item…"* listing worn apparel/equipped weapons with
   `coats < 3` → `RM_JobDriver_LacquerWornItem` (fetch Deepfire, walk to a
   powered `RM_DeepfirePress`, 1000 ticks, `AddCoat`).
3. Ideology styling station: per-item Deepfire checkbox beside each apparel
   row's colour picker in `Dialog_StylingStation`, `MayRequire`-guarded/
   reflection-resolved so Ideology-absent installs reference nothing.
4. Combat: Harmony postfix on `ShotReport.HitReportFor` (×`glowTargetFactor`,
   default 1.25, clamped 0.5–2, only when target is glowing AND the
   surroundings are dark without OUR light's own contribution) +
   `RM_StatPart_GlowingTarget` on `MeleeDodgeChance` (offset
   `−glowDodgePenalty`, default −0.08). Both read a labelled *"glowing in the
   dark"* explanation line.

## Needs

`bridge` — both proof halves above need a live game (spec's own words, §10).
