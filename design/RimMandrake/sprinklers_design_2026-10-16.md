# Sprinklers: native pipe heads + VFE automation (SPRINKLERS_DESIGN_PIPES_THEN_PANACHE, 2026-10-16)

**Authority.** Owner, 2026-10-16 round 4 (SP1, `explosive_growth_rulings_2026-10-16.md`): *"Let's define what sprinklers
should do first, then adapt VFE and our own together. VFE should incorporate some kind of bold automation and
enhancement, whereas the native one should be pretty rudimentary (just sprinklers set on pipes)"*. The water rule this
plugs into is `explosive_growth_ruled_spec_2026-10-16.md` (§2 cell states, §3 sources, where the sprinkler row reads
"deferred to this item"). Rulings that bind the design, verbatim: C3 *"Nobody "irrigates" a field on this world, that's
a huge amount of water loss. You share some water, they grow, you leave it there."* · W3 *"It always counts as fresh as
long as it's there. It's continuous."* · GM1 *"Nothing stays wet for long without an obvious reason."* · T2 card
**Only for adapted plants** · EC3 *"A full harvest but the water gets used up. That's the cost."* · H1 card **Watered,
normal vanilla speed**.

Tags: **MEASURED (file:line)** against bench `7556ab5190`; **PROPOSED** for every number not in a ruling; **UNMEASURED**
where nothing was read. Paths are relative to `/home/mandrake/rm/bench` (`D:\Luke\dev\RimMandrake` mirror). Offline
design only: nothing here was built, deployed or run live.

---

## 0. What exists today (searched first)

- **Ours: no sprinkler.** No def, comp or class in `src/` matches sprinkl/irrigat as a watering building; the one
  "irrigation gutter" (`RM_Webwork_Gutter`) has no watering behaviour (bench design pass §2, re-confirmed by grep today).
- **VFE: `VFE_Sprinkler`** — MEASURED `workshop/content/294100/1957158779/1.6/Defs/Buildings/Buildings_Misc.xml:56-122`
  (mod *Vanilla Furniture Expanded - Farming*, packageId `VanillaExpanded.VFEFarming`). `thingClass Building`,
  `CompPowerTrader` 250 W, `CompFlickable`, comp `VFEF.CompProperties_Sprinkler` (`effectRadius 5.8`,
  `sprinkleDurationTicks 500`, mote `VFEF_Mote_SprinklerWater`), cost 40 steel + 1 component, research
  `VFE_Res_Sprinkler` (500, after Machining). Behaviour (decompiled `VFEF.dll`, MEASURED in
  `explosive_growth_bench_design_pass_2026-10-16.md` §2): `VFEF.VFEF_SprinklersManager.MapComponentTick` fires at local
  hour 7, at most once per 57,500 ticks, while powered; `BoostPlantAt` adds **`plant.Growth += 0.04`** to each non-tree
  plant in radius (cells claimed by an earlier sprinkler skipped; planter boxes let through). **It draws no water.**
- Also on disk: Dubs Bad Hygiene's irrigation sprinkler (`2570319432/1.6/Defs/ThingDefs_Buildings/BuildingsF_Irrigation.xml`).
  It needs DBH plumbing, which was rejected 2026-08-04 (`design/Jawa/mods/required_mods.md:576`). Out of scope.
- **The pipe net we hang heads on** (MEASURED `FlowWorks/Source/Machinery/RM_LiquidNet.cs:26-33`): a machine reaches
  every tank touching a universal-pipe run that touches it; `RM_UniversalPipe` is a non-edifice, so machines stand over
  it (`Defs/Machinery/RM_LiquidLogistics.xml:22-75`). Draws go through `DrawPlan` (`RM_LiquidNet.cs:384-393`) and the
  conserving `RM_LiquidTransfer.Move` with a `Sink` world leg (`RM_LiquidTransfer.cs:54,152`); two consumers of one
  liquid take turns (`RM_ConsumerRotation`, used at `CompLiquidConverter.cs:211-300`). Units are decilitres
  (`liquid_litres_2026-10-16.md`: 1 level = 1 kL, a deep square = 4 kL).
- **The read pattern to copy**: `_Shared/FlowWorksIrrigation/FlowWorksIrrigationRead.cs` — ExplosiveGrowth reads
  FlowWorks reflection-soft, FlowWorks never a dependency.

## 1. What a sprinkler DOES under the water rule (shared by both)

1. **It is a pipe consumer that turns litres into WET cells.** Every pulse it draws its water from the liquid net it
   touches. If the whole draw commits, every covered cell is WET (`sprinkled`) until the next pulse is due plus a short
   grace. If the draw cannot be met in full, nothing is drawn and the cells go DRY at their expiry (all-or-nothing, so
   the ledger stays exact; `Move` already refuses whole).
2. **Wet only while it runs** (W3 + GM1). While the head keeps getting water, its cells are fresh continuously; the
   spray mote is the "obvious reason". Water stops, the cells are dry within one pulse. No lingering, no overlay.
3. **Pulse:** every 2,500 ticks (1 game hour); grace 250 ticks. PROPOSED.
4. **Water cost:** `litresPerCellHour` × covered cells. **RULED (OQ-S1) 0.5 L per cell-hour** (12 L per cell-day), so a
   native head (29 cells) spends ~350 L a day: a deep pond square lasts ~11 days. This is deliberately dear (C3): a
   sprinkler is an expensive way to share water, not free irrigation.
5. **Shape:** cells within a radius (`GenRadial`), in line of sight of the head (walls stop spray; LOS cached per net
   revision). Under a roof works (it is not rain). SEALED cells (basins, pots: H1) are skipped and never charged.
6. **Light:** the head sprays dark cells too (it is dumb); the water rule already gives a dark cell nothing (spec §2.3).
   Skipping them is one of VFE's smart features (§3).
7. **Crop cost (EC3):** a crop that self-fruits on a sprinkled cell **spends** that cell: it is DRY until the head's
   next successful pulse re-wets it. No extra litres; the pulse already paid.
8. **Liquids.** It sprays whatever single liquid its draw takes (the head picks one, §2/§3), by `LiquidDef` fields
   (MEASURED `FlowWorks/Source/LiquidTypes/LiquidDef.cs:31-58`, enum `RM_LiquidProperties.cs:75-81`):
   - `viscosityClass` Thin or Water: sprays. **Thick or Heavy** (tar, pitch, heavy slimes): the head **clogs** and reads
     "clogged: <liquid> too thick to spray"; it draws nothing.
   - Clean water (`RM_Fluid_Water`'s liquid) wets every archetype; any other liquid wets **only plants adapted to it**
     (T2; acceptance on the (cell liquid, plant) pair, spec §2.4).
   - `damageOnContact` liquids (acid, scalding `hot`) apply that contact effect to pawns standing in the spray, once per
     pulse; `flammable` liquids lay their `spillFilth` at the normal spill rate (fire risk you can see). RULED (OQ-S5).
9. **Power and pressure (RULED OQ-S2):** no electrical power for the native head, **but a pump must be on its network**: the pump is the pressure. A head on a net with no working pump reads "No pressure: no pump on this network" and draws nothing (cells dry at expiry, as §1.1). VFE's head keeps its own 250 W for its automation and, because it is a pipe consumer under this section, needs the same pump (inferred from the shared path; owner to confirm).
10. **Scope:** the WET effect is read only where the water rule is in scope (our biomes; spec §6). Elsewhere a native head
    still draws and wets; growth reads it only under setting B "same rule". VFE's waterless boost is removed everywhere while the adapter is on (§3, OQ-S3).

## 2. Native FlowWorks head: `RM_SprinklerHead` (rudimentary)

- **What:** a 1×1 nozzle set **on a universal pipe cell** (PlaceWorker: a pipe must be under it; it stands over the
  pipe like the tanks do). It joins that pipe's component as a machine (never conducts). It needs a working pump on that component (OQ-S2).
- **Radius 2.9** (29 cells incl. its own). PROPOSED. No electrical power (pump on the net required). Cost 5 steel; WorkToBuild 200; research: none beyond
  FlowWorks' pipes. PROPOSED.
- **UI, minimal:** `CompFlickable` on/off; inspect line "Spraying water · 14.5 L/h · 29 cells" / "Dry: net has 3 L of
  water, needs 14.5 L" / "Clogged: tar too thick". **No liquid picker:** it sprays the liquid its net holds most of
  (ties by liquid defName); a mixed net is the player's problem, as with every other FlowWorks consumer.
- **Art:** a nozzle in the four pipe looks (Scrapper/Industrial/Modern/Futuristic, `PipeLook`) so it matches the pipe it
  sits on, plus a small spray mote. RULED (OQ-S6): the art commission is approved, all four looks plus the spray mote.
- **Class:** `RimMandrake.FlowWorks.Machinery.CompRM_SprinklerHead` calling the shared pulse (§4).

## 3. VFE `VFE_Sprinkler` adaptation: bold automation and enhancement

Base change (all bold ideas sit on it): the VFE head becomes **a pipe consumer under §1**. It must touch a universal
pipe run (8-way, the net's existing machine rule). Its radius stays VFE's 5.8 (~105 cells, ~1,260 L a day at full
coverage: a serious commitment of water). Its 250 W powers the brains; unpowered it acts as a dumb native head.

**Bold ideas, ranked:**

1. **Thirst valve (moisture-sensing, budgeted) — RECOMMENDED FIRST.** Each pulse it charges only cells where water
   *changes growth*: a plant stands there, it is not SEALED, not already WET by another source (river, channel,
   flood, a spill), lit, not exempt, not a wood plant at rest. It shows "watering 41 of 105 cells, 20.5 L/h, saved
   32 L today". Gizmos: **daily budget** (L/day cap; it trims the farthest cells first) and **reserve floor** (stop when
   the net's water falls below N kL, so the farm never drinks the colony's thirst supply — DBH Thirst is adopted,
   `required_mods.md:580`). Directly serves C3: water is the cost, and this is the tool that spends it wisely.
2. **Bloom conductor (harvest hold).** Modes on the head: *Grow* (default), *Hold at ripe* (cut water to a dry
   native's cell when it reaches 0.95 growth, so the 1-in-3 rupture/fruit roll waits until you choose), *Release*
   (re-wet the whole field at once: the field cycles together, pawns harvest one wave). Turns the churn rulings into a
   player-run event. Bold, but it touches the cycle code (spec §4.1), so it waits for that.
3. **Dual-line fertigation.** A second pipe input: the head can carry water and one adapted liquid (a slime, red water)
   and sprays each cell with the liquid **its plant is adapted to**, water otherwise (T2 made into a feature). Option:
   dose a fertility liquid that the plant economy item defines. Highest cost (two-liquid draw, per-cell liquid tag), and
   it depends on per-biome adaptation columns not yet filled. Last.

**VFE's own +0.04 a day (§0). RULED 2026-10-16 (by card, OQ-S3): removed everywhere while our adapter is on.** A Harmony
prefix on `VFEF.VFEF_SprinklersManager.BoostPlantAt` skips the boost on every map and biome, not only in water-rule
scope; the sprinkler then does only what our pipe-fed pulse does. With `vfeSprinklerAdapterEnabled` off VFE runs exactly as shipped.
Reason: a waterless boost would stack on the ruled rates (the 2026-08-04 rejection reason).

⚠️ **FLAG FOR THE OWNER (not resolved here):** this changes VFE behaviour outside our biomes, which sits against the
2026-10-15 ruling that biome mechanics are promised inside OUR biomes only (*"We can't guarantee they will work in
other biomes beyond our framework"*). The card answer was explicit, so the design follows it; the owner should say
whether the 10-15 rule yields here or the removal should be scoped to our biomes after all.

**3.4 Mechanics of the adapter (no dependency on VFE):**
- XML: `FlowWorks/Patches/Compat/RM_VFEFarming_Sprinkler.xml`, a `PatchOperationFindMod`
  (`<li>Vanilla Furniture Expanded - Farming</li>`) adding `CompProperties_RM_SmartSprinkler` to `VFE_Sprinkler` and an
  inspect/description line. Never a top-level `MayRequire` (ignored).
- C#: patches applied only when `AccessTools.TypeByName("VFEF.VFEF_SprinklersManager")` resolves; signatures checked at
  startup with one warning on mismatch. The FlowWorks DLL never references `VFEF.dll`.
- VFE's mote/rotation animation is left alone; our comp only decides whether a pulse paid.

## 4. One code path for both

```
CompRM_SprinklerHead (native) ─┐
CompRM_SmartSprinkler (VFE) ───┴─► RM_Sprinkle.Pulse(head, cells, liquid, litresPerCell)      [FlowWorks]
                                     ├─ RM_SprinklerKernel (Verse-free): cell plan, litres, all-or-nothing, expiry, spend
                                     ├─ RM_LiquidNet.DrawPlan + RM_LiquidTransfer.Move(Store → Sink)  (conserving, rotation)
                                     └─ RM_MapComponent_Sprinklers: per-cell wetUntilTick + liquid key  (saved, sparse)
_Shared/FlowWorksSprinklerRead.cs  (reflection-soft, like FlowWorksIrrigationRead)
   └─► ExplosiveGrowth §3 source row "sprinkled": WET while now < wetUntil and the plant accepts the cell's liquid;
       crop self-fruit calls Spend(cell) through the same read.
```

- The smart features only **choose `cells`** before calling `Pulse`; the water rule sees one source kind either way.
- ExplosiveGrowth never knows a sprinkler exists; FlowWorks never knows the water rule's rates. The hook is the
  `wetUntil` grid, read at `GrowthRate` time (no per-cell ticking, spec §2.1).
- The ExplosiveGrowth hook is built **after** the water-rule rewrite lands (spec §8 deltas), per this item's own
  "design sprinklers BEFORE any water-rule hook".

## 5. Mod Settings (defaults = shipped behaviour)

| mod | setting | default |
|---|---|---|
| FlowWorks | `sprinklersEnabled` (native heads buildable and running) | on |
| FlowWorks | `sprinklerLitresPerCellHour` (slider 0.1–5) | 0.5 |
| FlowWorks | `sprinklerNativeRadius` (1.9 / 2.9 / 3.9) | 2.9 |
| FlowWorks | `sprinklerNonWaterEffects` (contact damage, flammable filth in spray) | on |
| FlowWorks | `vfeSprinklerAdapterEnabled` (off = VFE exactly as shipped everywhere; on = VFE's waterless boost removed everywhere) | on |
| FlowWorks | `vfeThirstValve` · `vfeBloomConductor` · `vfeFertigation` (each feature on/off) | on · on · on (as each ships) |
| ExplosiveGrowth | source toggle `sprinklers` (spec §6 "one toggle per source") | on |

All off: no native head, VFE vanilla, growth ignores sprinkled cells: the game is whole. VFE settings are labelled
"needs Vanilla Furniture Expanded - Farming" and hidden when it is absent.

## 6. Build plan (ordered) and the first functional script

1. **Kernel** `FlowWorks/Source/Machinery/RM_SprinklerKernel.cs` (Verse-free) + selftest cases in
   `selftest_flowworks_stock.py`: `Sprinkler_pulse_all_or_nothing`, `Sprinkler_expiry_one_pulse_plus_grace`,
   `Sprinkler_spend_dries_until_next_pulse`, `Sprinkler_thick_liquid_clogs`, `Sprinkler_sealed_cells_never_charged`,
   `Sprinkler_conserves_litres` (Move refusal on either leg changes nothing).
2. **FlowWorks plumbing:** `RM_Sprinkle.Pulse`, `RM_MapComponent_Sprinklers` (save/load), settings, a probe verb
   `sprinkler:` (head state, litres last pulse, cells, wetUntil sample) on the existing FlowWorks probe.
3. **Native head** def `RM_SprinklerHead` + `CompRM_SprinklerHead` + on-pipe PlaceWorker; placeholder graphic until the
   owner rules on art.
4. **Shared read + ExplosiveGrowth source row** (after the water-rule rewrite): `_Shared/FlowWorksSprinklerRead.cs`,
   the §3 row, `Spend` on crop self-fruit, the source toggle.
5. **VFE base adapter** (§3 base + §3.4) with the `BoostPlantAt` scope prefix.
6. **Thirst valve** (bold #1). 7. **Bloom conductor** (#2, after spec §4.1 cycle code). 8. **Fertigation** (#3, after
   per-biome adaptation columns exist).

**First functional script (ships with step 3, per `debug_process.md` §2):**
- Walk lines added under `## must be true` in `design/validation_walks/RimMandrake/FlowWorks.md`, each ending `→ <chain>`:
  - a native head on a pipe to a tank of 1 kL water draws `cells × 0.5 L` each hour and its cells read sprinkled →
    `sprinkler.draws_and_wets`;
  - with the tank emptied, the cells read dry within 2,750 ticks and the head reads "Dry" → `sprinkler.dries_when_starved`;
  - a tar tank: the head reads clogged and the tank is unchanged → `sprinkler.thick_clogs`;
  - a slime tank: cells read sprinkled with liquid key = that slime → `sprinkler.liquid_key`;
  - `sprinklersEnabled` off: the head draws nothing → `sprinkler_switch_flips.flip_sprinklersEnabled`.
- Chains in `FlowWorks/validation.py` (a quicktest map, ~90 s; spawn tank + 3 pipes + head through the bridge, advance
  ticks, read the probe verb and tank litres). Runs clean under `--mock` before any live run.
- Step 4 adds to `design/validation_walks/RimMandrake/ExplosiveGrowth.md`: a dry native on a sprinkled, lit cell reads
  ×10; a vanilla crop in coverage reads "water nearby" (setting A); a self-fruited crop's cell reads dry until the next
  pulse.

## 7. Rulings (owner, question cards, 2026-10-16)

- **RULED 2026-10-16 (by card), OQ-S1:** 0.5 L per cell per hour, about 350 L/day for a native head (§1.4).
- **RULED 2026-10-16 (by card), OQ-S2:** no electrical power, but a pump must be on the head's network (§1.9, §2).
- **RULED 2026-10-16 (by card), OQ-S3:** remove VFE's waterless boost everywhere when our adapter is on (§3). Against the recommendation; flagged for the owner against the 10-15 inside-our-biomes rule.
- **RULED 2026-10-16 (by card), OQ-S4:** the first VFE upgrade is the moisture valve (Thirst valve, bold #1).
- **RULED 2026-10-16 (by card), OQ-S5:** acid or boiling liquids hurt pawns in the spray; fuels leave flammable filth (§1.8).
- **RULED 2026-10-16 (by card), OQ-S6:** a nozzle in each of the four pipe looks plus spray; art commission approved (§2).
- **RULED 2026-10-16 (by card), OQ-S7:** walls stop the spray; line of sight from the head (§1.5).

## 8. Build consequences

1. The head draws only when a working pump is on its network; add the "No pressure" state, a probe field, and a validation line (head on a pump-less net reads No pressure and draws nothing; adding a pump flips it).
2. Native head cost stays 5 steel, no power comp; the pump requirement makes the pump a prerequisite in the tutorial/research text.
3. `BoostPlantAt` prefix is unconditional while the adapter is on; the setting `vfeKeepFlatBoostInOurBiomes` is deleted. Anything reading "VFE unchanged outside our biomes" is wrong.
4. Art commission for the nozzle in four pipe looks plus spray mote may be filed now.
5. Step 6 (Thirst valve) is the first VFE feature to build.
6. Non-water spray effects and LOS are ON (not optional-by-default); keep the `sprinklerNonWaterEffects` setting only as a toggle.
