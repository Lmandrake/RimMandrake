1. **Deep ash rejects buildings that require Medium terrain support**
   - **Where:** `src/RimMandrake/Pyrelands/Defs/TerrainDefs/AshField.xml:29–32`; `src/RimMandrake/Pyrelands/Defs/TerrainDefs/ScorchableGround.xml:27–30`.
   - **Mechanism:** Both terrain bases declare Light and Heavy, but omit Medium. Terrain affordances are independent requirements; Heavy does not implicitly grant Medium. Consequently, the biome’s ordinary ground rejects construction whose `terrainAffordanceNeeded` is Medium.
   - **Repro:** Attempt to place a building requiring Medium support on deep ash, then on ordinary soil.
   - **Severity:** gameplay-visible.
   - **Check:** Enumerate loaded buildable defs requiring Medium and run vanilla’s terrain placement check against deep ash. Confirm its affordance list lacks Medium.
   - **Confidence:** high.

2. **The allowlist can leave mixed-biome patches permanently without grass candidates**
   - **Where:** `src/RimMandrake/Pyrelands/Source/WildPlantAllowlist.cs:19–26,98–112`.
   - **Mechanism:** The documented candidate source is the cell’s biome, which can be a secondary biome. The postfix checks the map’s primary biome at line 104 and removes foreign candidates at lines 106–111, but never supplies either native grass. Where the original candidate list contains only secondary-biome plants, the result is empty. Blocking foreign plants therefore does not establish the required grass carpet.
   - **Repro:** Generate a primary-Pyrelands map with a secondary-biome patch whose roster contains neither native grass. Let wild spawning attempt that patch.
   - **Severity:** gameplay-visible.
   - **Check:** Capture `outPlants` immediately before and after this postfix at one such cell. A nonempty foreign list becoming empty confirms the mechanism without waiting for regrowth.
   - **Confidence:** high.

3. **Reloading erases the promised day of residual watering**
   - **Where:** `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs:47–49,86,89–114,214–243,262–266`.
   - **Mechanism:** Natural water and irrigation record a one-day expiry in `wateredUntil` (lines 214,229,242), but that array is unsaved. After loading, it starts empty. If the source was drained or removed before saving, the sweep cannot reconstruct its remaining watering duration. Persistent sources also temporarily read dry until their slice runs; a complete sweep takes 2,000 ticks.
   - **Repro:** Water ash from a channel, drain the channel, confirm the ash remains watered, then save and reload immediately.
   - **Severity:** gameplay-visible.
   - **Check:** Compare `ProbeCell` before saving and immediately after reloading. With no Black Rain involved, `watered=True` should become `False` despite almost no elapsed game time.
   - **Confidence:** high.

4. **Density and the accelerated regrowth override continue with mechanics disabled**
   - **Where:** `src/RimMandrake/Pyrelands/Source/RM_PyrelandsDensityEnforcer.cs:48–70,73–87`.
   - **Mechanism:** Startup, game initialization and the recurring tick all call `Enforce()` without consulting `PyrelandsMechanicsGate.On`. Lines 85–86 continue imposing density 16 and `EffectiveRegrowDays`, including a nonzero test override. This bypasses the stated master/shell-toggle contract for live mechanics.
   - **Repro:** Set the regrowth override to 0.1 days, disable the master or composed Pyrelands toggle, and advance past a 250-tick boundary.
   - **Severity:** gameplay-visible.
   - **Check:** Read the gate and `RM_Pyrelands.wildPlantRegrowDays` together. The gate can be false while the enforcer continues imposing 0.1.
   - **Confidence:** high.

5. **Changing ambient ash heaviness does not update an existing weather worker**
   - **Where:** `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs:480–482,520–527`.
   - **Mechanism:** The setting changes `drift.overlayClasses`, but does not rebuild the instantiated overlays. The class comment explicitly acknowledges that the overlay is fixed once its weather worker has been built. Thus the setting’s stored value and def list can change while the running visual remains unchanged.
   - **Repro:** Enter ash-drift weather, toggle `ambientAshHeavy`, then return to ash drift.
   - **Severity:** gameplay-visible.
   - **Check:** Compare the def’s overlay-class list with the existing worker’s instantiated overlay types before and after the toggle. No visual hunt is necessary.
   - **Confidence:** high.

6. **Setting Black Rain watering to zero leaves existing blanket watering active**
   - **Where:** `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs:188–191,262–266`.
   - **Mechanism:** A positive `blackRainWaterHours` controls extending the timer, but `IsWatered()` never checks that setting. Changing it to zero stops future extensions while retaining the previous map-wide expiry, potentially leaving another day of watering despite selecting “Black Rain does not water.”
   - **Repro:** Let Black Rain establish watering, change its watering duration to zero, then inspect outdoor ash away from water sources.
   - **Severity:** gameplay-visible.
   - **Check:** Read `ProbeCell` after applying the setting: `watered=True` and a future `blackRainWateredUntil` confirm that disabling the route did not remove its live effect.
   - **Confidence:** high.

7. **The fertility overlay is not invalidated for most ash-field changes**
   - **Where:** `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs:187–194,228–249,253–258,269–275`.
   - **Mechanism:** The only explicit drawer invalidation occurs when a sweep marks a previously dry cell watered (lines 246–248). Burn stamping, bonus aging, rain washing, Black Rain watering and watering expiry do not invalidate it. Cached overlay colours can therefore disagree with the fertility used by growth and the mouseover.
   - **Repro:** Keep the fertility overlay open over source-free ash, stamp a burn or begin Black Rain, then let the effect expire without rebuilding the overlay.
   - **Severity:** cosmetic/perf.
   - **Check:** Compare `FertilityAt` with the displayed overlay before and after closing/reopening it. Alternatively, instrument `Drawer.SetDirty` during those state transitions.
   - **Confidence:** high.

8. **The ash-field static cache retains a removed map**
   - **Where:** `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs:60–71,117–122`.
   - **Mechanism:** `lastMap` and `lastComp` hold strong static references. `MapRemoved()` clears the furnace registry but leaves this separate cache intact. The most recently queried map remains reachable after removal or returning to the menu until another qualifying fertility query replaces it. This retention is bounded to one map, but includes that map’s contents.
   - **Repro:** Query ash fertility on a temporary map, remove that map, and continue somewhere without ash-field queries.
   - **Severity:** cosmetic/perf.
   - **Check:** Read the two static fields after removal, or use a weak-reference collection check. Both still identify the removed map/component.
   - **Confidence:** high.

9. **A map that gains ash after initialization can remain permanently inactive**
   - **Where:** `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs:124–132,163–180,253–259,425–437`.
   - **Mechanism:** `active` is calculated only during initialization or set by `StampBurn()`. An initially ash-free, non-Pyrelands map that later receives opted-in terrain is served by the fertility postfix, but its component still returns before performing watering sweeps or recording rain. Merely querying that terrain does not activate it.
   - **Repro:** On an initialized non-Pyrelands map without ash, introduce deep ash beside water without issuing a burn stamp. Advance beyond a complete sweep, then reload.
   - **Severity:** latent.
   - **Check:** `ProbeCell` should show `active=False` and dry fertility before reload, then `active=True` and watered fertility after initialization and a sweep.
   - **Confidence:** high.

10. **Legacy conversion misses retired ash beneath constructed floors**
    - **Where:** `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs:135–150`; `src/RimMandrake/Pyrelands/Defs/TerrainDefs/AshField.xml:47–51,54–77`.
    - **Mechanism:** Migration examines only `TerrainAt(c)`, the exposed terrain. Retired ash stored beneath a constructed floor is not converted. Removing that floor later exposes a legacy alias without the ash-field extension, so it receives neither watered fertility nor the fresh-burn bonus until another reload converts it. This is an incomplete part of the recorded legacy-save fix.
    - **Repro:** Load a keeper/review save containing a floor over a retired ash rung, then remove the floor.
    - **Severity:** latent.
    - **Check:** Read the exposed terrain and `ProbeCell`: a legacy def with `ashField=False` confirms it. Reloading should convert it to deep ash.
    - **Confidence:** high.

No additional finding established for plant TickLong rules (5), animal jobs (6), heat (7), or Harmony target signatures (8). Standing-fire performance, earlier-save burn-line/scorchfruit-ID state, direct plant spawning and map generation (11) cannot be assessed from these excerpts: their implementing files were not supplied. The loose-ash XML does contain the documented vanilla rain-washing flag.