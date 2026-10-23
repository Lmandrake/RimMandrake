# FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN — a simple FlowWorks fountain that closes the whole flow cycle

Owner, 2026-10-23: *"In the meantime, we can do a small simple version in FlowWorks itself: simple fountains that
allow their water to fall out and flow over the ground. The water can be captured in a surrounding ditch then pumped
back to the fountain as a proof-of-principle of the entire flow cycle as well as a neat artistic piece. Please
commission that as art and as a review sheet item to watch work."*

v2 (sculpture family): `design/RimMandrake/fountain_sculptures_v2_2026-10-23.md`, item
`FOUNTAIN_SCULPTURES_DESIGN_WATER_MEETS_ART`.

## spec

**What exists (2026-10-23), so the build is mostly wiring:**
- Overspill: `Source/Sheet/RM_MapComponent_Sheet.cs` (Stage 1 of `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED`).
  `SpillLeg(map, outlet, fluid, Source)` is an `RM_TransferLeg` destination (exact `Probe` before anything moves);
  `Offer`/`Probe` return accepted dL. Water on undug ground flows, levels (D8), returns into dug cells (ledger
  `Returned`), soaks/evaporates (D6, disclosed), freezes keeping volume (D10). Ledger read: `ProofSheetLedger`.
- Net draw: `RM_LiquidNet.DrawPlan(head, liquid, units)` + `RM_TransferLeg.Split` + `RM_LiquidTransfer.Move` +
  `RM_LiquidNet.Credit(...)` — exactly the sprinkler's draw (`Source/Sprinklers/RM_Sprinkle.cs` ~l.98–114).
- Return: `RM_LiquidPump` (looks Scrapper/Industrial/Modern/Futuristic) lifts from an excavated cell in its own
  reach into the tanks on its net. Ditch: `RM_DigCanal` designation. Spray picture: `RM_Mote_SprinklerSpray` via
  `RM_Sprinkle.ThrowSpray(thing, liquid, radius)`.

**The building — `RM_Fountain` (FlowWorks, `Defs/Fountains/RM_Fountain.xml`):**
- 1×1, impassable, `fillPercent` 0.45, not rotatable, `Graphic_Single`, `drawSize (1,1.5)`, `drawOffset (0,0,0.25)`
  (height extends north, camera rule). Stuff: Stony/Metallic, `useIngredientsForColor` — art is pale neutral stone so
  the stuff tint reads (one design, no FlowWorks looks: it is an art piece, not a pipe fixture). Beauty 30, no CompArt
  quality in v1 (that is v2). Architect menu: the FlowWorks pipe-networks category, beside the sprinkler.
- Placed on/adjacent to a universal pipe (PlaceWorker like the sprinkler's `PlaceWorker_RM_OnPipe`, or "touches a
  pipe" — builder decides from the sprinkler's PlaceWorker); `CompFlickable` on/off; no power.
- Every flow pulse (`RM_SprinklerKernel.PulseTicks`-style map component, or ride the sprinkler map component): want =
  `flowLitresPerHour` × pulse fraction in dL; `DrawPlan` from tanks on its net; destination `SpillLeg` at the
  fountain's rim (origin = the fountain cell's first open orthogonal neighbour, Source **Pump**: the water is
  pressurised from a tank, D2 ruled pumps spill); `Move` atomic. Refused (sheet full, setting off, no water) →
  nothing moves, state reads *Dry* / *Backed up* / *No water*. Never destroys, never creates.
- Picture: the static sprite (basin water painted) plus, while *Playing*, the jet overlay frames cycling
  (`Graphic_Flicker`-style, 3 frames, like `RM_FireFrames`) and an occasional `ThrowSpray` at the spout; *Dry* draws
  the dry base only.
- Inspect: state, L/h drawn this hour, total spilled; a dev gizmo to set state for staging.
- **Settings** (`RM_FountainSettings`, FlowWorks Mod Settings, searchable): fountains enabled (default on; off =
  fountains stay built and inert, no water moves); flow L/h (default 200, range 20–2000); spray picture on/off.
  Labels note it needs the sheet layer ("Overflow spills onto ground") on, else it reads *Overspill off*.

**The loop (the proof-of-principle layout, 9×9):** fountain at centre; a dug ring ditch at Chebyshev distance 3
(24 cells, 1 notch deep is enough); undug ground between (the sheet runs 2 cells to the ditch); one
`RM_LiquidPump` on the ring's east side with the ditch in reach; one `RM_LiquidTank` beside it; a universal pipe
from tank to fountain crossing the ditch on a pipe pole/span. Prime: tank Fill with 2,000 L water. The cycle:
tank → pipe → fountain → sheet → ditch (Returned) → pump → tank.

**Code needed (do NOT write until the FlowWorks C# holder releases):** `Building_RM_Fountain` or a
`CompRM_Fountain` (+ props), `RM_FountainSettings` (+ search index entry), a pulse driver (reuse the sprinkler map
component's clock), 3 proof methods on a `RM_FountainProofs` static class (below), Defs XML, the selftest for the
want/draw arithmetic (Verse-free `RM_FountainMath`), and a review-map station. Everything hydraulic already exists.

## verify

Offline (SelfTest): `RM_FountainMath` — want dL per pulse from L/h is exact over a day (no drift, integer carry);
refused spill moves 0; settings off moves 0.

Live — `src/RimMandrake/FlowWorks/northstar/fountain_loop_proof.py` (new; same harness shape as
`sheet_overflow_proof.py`), proof surface `ProofFountain` (`state=… drawnDl=… spilledDl=…`) beside the existing
`ProofSheetLedger`:
- **F1 plays:** primed loop, 1 in-game hour → fountain state Playing, `spilledDl` > 0, sheet standing > 0 on the
  ring between fountain and ditch.
- **F2 returns:** ledger `Returned` rises within 2 pulses of the sheet reaching the ditch; the pump moves water
  ditch → tank (tank stock dips then recovers).
- **F3 conserves (the headline):** 3 in-game days at 200 L/h: `tank + ditch + standing + inflight` at end ==
  start − (Soaked + Evaporated) to the dL. Any other gap is a MOD finding.
- **F4 back-pressure:** pump flicked off → ditch fills, sheet backs up, fountain reads *Backed up* and draws 0; total
  water unchanged (no destroy).
- **F5 dry:** tank emptied → *No water*, nothing moves, no error in the log.
- **F6 settings off:** fountains disabled → 0 dL moved over 1 hour; on again resumes.
- **F7 cold:** temperature forced −10 °C → sheet freezes (ice tier, volume kept, D10); fountain behaviour recorded
  (v1 keeps drawing until the sheet refuses; that is a finding for the v2 freeze question, not a fail).
- **F8 log:** zero red errors over the run (log budget row).

**Review scene to WATCH (owner):** a new station `fountain_loop` in `src/RimMandrake/FlowWorks/review_map.py`
`extras()` (the FlowWorks review map's free area F, 11×11 clear soil pad, Clear weather, noon), built as the 9×9
loop above, primed, running unpaused for the owner; sign card: *"Fountain loop: tank → fountain → ground → ditch
→ pump → tank. Watch the sheet reach the ditch, the pump lift it back. Weak spot: water lost on the soil pad (soak
is a disclosed exit, not a leak)."* Keeper save `RM_fw_review_fountain_<date>`. The art review sheet (static
candidates, true scale) is `Transient/fountain_20261023/` (pinned); the game scene follows install.

## NEXT
`FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN` — spec + verify written 2026-10-23, art candidates on a pre-reviewed sheet in
`Transient/fountain_20261023/`; NEXT: when the FlowWorks C# holder releases, build `RM_Fountain` per ## spec, then run
`fountain_loop_proof.py` F1–F8.
