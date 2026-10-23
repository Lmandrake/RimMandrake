# Fountain sculptures — v2 brainstorm (2026-10-23)

Item `FOUNTAIN_SCULPTURES_DESIGN_WATER_MEETS_ART` (v2). The v1 proof-of-principle is a separate item,
`FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN` (one simple FlowWorks fountain, ring ditch, pump return).

Owner, 2026-10-23: *"Now that we're building the ability for water to flow over the ground (overspill), We can do
some really neat stuff fairly cheaply! We can make fountains! Beautiful artistic sculptures with water spewing out of
them, the counterpart to the fire sculptures we had already invented or the glow sculptures. That's pretty
spectacular! Please document this brainstorm idea for v2 development."*

## 1. What already exists (searched 2026-10-23)

| piece | where | what it gives a fountain |
|---|---|---|
| **Overspill (sheet water)** | FlowWorks `Source/Sheet/RM_MapComponent_Sheet.cs` + kernel `Source/RM_SheetMath.cs`; spec `canal_overflow_flooding_2026-10-21.md` | Stage 1 is wired: `Offer(origin, dL, fluid, Source)` → accepted dL, the caller debits exactly that; `SpillLeg(...)` as a transfer destination. dL-exact ledger: In = Standing + Returned + JoinedLake + Soaked + Evaporated + Burned + Purged. Sheets level (D8), freeze into an ice tier below 0 °C keeping volume (D10), run back into dug cells (Returned). Overlay renderer, no temp terrain. |
| **Fire sculptures** | `src/RimMandrake/FlameStatues` (`RM_FlameStatue_Ember/Dancer/Colossus`, spec `statue_mods_spec.md` §2) | The template: `ParentName="SculptureBase"`, stuff-tinted Stony/Metallic, CompArt quality, Beauty 50/100/400, `MapMeshAndRealTime`, a **set of measured emit points** (`RM_CompFlamePoints`, offsets measured from the PNG), quality-scaled flecks, CompRefuelable. A fountain is the same shape with water points instead of flame points. |
| **Glow sculptures** | `src/RimMandrake/LuminousPigment` deepfire lacquer (`CompInjector_Deepfire`, `DeepfireFirstCoatBonus`) | Any CompArt thing takes deepfire coats and glows (+1 quality step on the first coat). A fountain sculpture is CompArt, so **night-lit fountains come free**. |
| **Spray picture** | FlowWorks `RM_Mote_SprinklerSpray` (`Source/Sprinklers/RM_Sprinkle.ThrowSpray`, tinted by the liquid's colour) | A jet/plume mote already exists; fountains reuse it per emit point. |
| **Net draw** | `RM_LiquidNet.DrawPlan` + `RM_TransferLeg.Split` + `RM_LiquidTransfer.Move` (as the sprinkler does) | Draw N units from the tanks on the fountain's pipe run into the sheet leg, atomically. |
| **Pump return** | `Building_LiquidPump` (own reach + Intake hose ends) | Lifts water out of a dug ditch back into tanks — closes the loop. |
| **Timer switch** | FlowWorks `MapControls/RM_TimerSwitch.cs` (already cites "fountain at dawn") | Scheduled fountains with no new code. |

Nothing named fountain is built (src/ grep, RimSage). `rimplace/plan.py` has a `FOUNTAIN` furniture slot and the
Jawa furniture register keeps a "Fountain" row — both just name the concept.

## 2. The vision

A **third art-sculpture family** beside fire and glow: crafted at a sculptor's table (Artistic skill, CompArt
quality, stuff-tinted), placed, fed from a pipe, and it *plays*: jets, cascades and a sheet of real water that runs
over the ground and is either caught (a basin, a ditch, a pond) or wanders off. Because the water is real
FlowWorks water, everything downstream is already true: it waters crops (D3), wets the ground, puddles, freezes,
drains into channels, and is lost only through disclosed exits.

**Roster (RM_ generic, mirroring the flame sizes):**
- *Spout* — 1×1 small (Beauty ~50): a single bowl or urn, one jet. (v1's fountain is this tier, made plain.)
- *Cascade* — 2×2 large (Beauty ~100): stacked basins, water drops tier to tier, 3–4 emit points.
- *Grand fountain* — 3×3 grand (Beauty ~400): figure plus ring basin, 6–8 jets; a centrepiece.
- *Wall spout* — a wall-mounted mask/lion-head (Beauty ~30), facing-aware, fills a trough.

**RSW tier (franchise flavour, routed per the naming ruling):** only genuine canon gets RSW_/RUT_ — a Naboo
Theed-style cascade (canon architecture), a moisture-farm vaporator "weeping" condensate, a Jedi-temple reflecting
pool. Invented exotic designs stay RM_.

## 3. Mechanics (proposal)

- **Feed:** a pipe port (universal pipe, like the sprinkler) or an adjacent tank. Flow is a setting per building
  (gizmo: off / trickle / play / full), litres per hour drawn through `DrawPlan`, spilled through `SpillLeg` at the
  fountain's rim cells. Back-pressure: if the sheet refuses (ground already brim-full), the fountain *stops drawing*
  — nothing is destroyed, the picture shows a still basin.
- **Recirculating basin (v2 option):** a fountain with its own basin holds a small internal stock and returns its
  own overflow; only the excess spills. This is the "indoor" fountain that does not flood a room.
- **Emit points:** `RM_CompWaterPoints` — the flame-points comp pattern with offsets measured from the PNG, each
  point throwing the sprinkler spray mote (tinted by liquid; quality scales jet height like flame size).
- **Beauty/mood:** CompArt beauty as vanilla sculptures; while playing, + a small *Beauty* bonus and a
  "pleasant sound" ambience (one sustainer, vanilla `SoundDef`); recreation: *meditate/watch* via a `JoyGiverDef`
  like vanilla's sculpture viewing.
- **Cold:** below 0 °C the sheet already freezes (D10). The fountain itself shows a frozen-jet graphic and stops
  drawing (pipe would freeze) — or, with a heater nearby, keeps playing: a winter spectacle.
- **Night:** deepfire lacquer gives glowing stone; an optional *lit basin* variant (CompGlower, power) colours the
  water at night.
- **Any FlowWorks liquid:** a fountain of tar, slime or glowing pigment liquid — the sheet already carries each
  fluid's rules (fuel spills spread and burn, D5). A burning-fuel fountain is the bridge to the fire family.

## 4. Dependencies

1. The sheet layer at 1.0 quality (`CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` live acceptance rows) — a fountain is
   its first *permanent* source; any sheet leak shows up as a slow flood.
2. v1 `FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN` proving the closed loop conserves over a long run.
3. A measured emit-points comp (copy of `RM_CompFlamePoints`), and art per design through the art judge.

## 5. Risks

- **Perf:** a fountain keeps the sheet awake forever around it. The kernel sleeps dry areas; a permanent wet patch is
  a standing cost per pulse. Measure with `ProofSheetPerf` beside 10 fountains.
- **Room flooding:** an indoor fountain with no drain floods the room; that is the honest physics but players will
  call it a bug. Mitigation: the recirculating basin, and an inspect line "spilling X L/h; nowhere to drain".
- **Mote spam:** one mote per jet per few ticks at grand tier; budget it like flame flecks (quality-scaled interval).
- **Art camera:** water in its true plane (C3, C6): jets rise vertically, basin water is an ellipse at 0.56.

## 6. Open questions (for the owner, when v2 opens)

1. Crafted like sculptures (art bench, quality) or built from the architect menu like furniture? *(Proposal: art
   bench for the sculpture tiers; the v1 plain fountain stays an architect build.)*
2. Recirculating basin: in v2, or only open spill? 3. Mood: beauty only, or a "lovely fountain" thought?
4. Which RSW canon designs, if any. 5. Freezing: stop, or keep playing with a frozen-jet picture?
