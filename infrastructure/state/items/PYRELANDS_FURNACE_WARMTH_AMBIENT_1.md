# PYRELANDS_FURNACE_WARMTH_AMBIENT_1

Split from `PYRELANDS_HEAT_KIND_BUILD_1` (steps 2-3; step 1, the `RM_SunHeatExtension` on `RM_Pyrelands`, shipped).

## spec
1. Retire `RM_FurnaceWarmth` (`Pyrelands/Defs/HediffDefs/RM_PyrelandsHediffs.xml`) and `CompFurnaceWarmthAura`'s hediff stamping (`Pyrelands/Source/CompFurnaceWarmthAura.cs`, `Patches/RM_PyrelandsIgniters_Comps.xml`). One kind of heat: no comfort-range hediff.
2. The furnace-beast's warmth becomes a local felt-temperature offset (+C within a radius, falling off with distance, radius scaled by thermal charge as today) applied through a `Thing.AmbientTemperature` postfix beside `RM_SunHeatPatches` (CreatureBehaviors). Keep the vanilla heat pusher for rooms.
3. Mod Settings: a furnace-warmth strength slider.
4. Rewrite the `Pyrelands/validation.py` furnace-warmth check (~line 1041-1083) to read AmbientTemperature instead of the hediff.

## verify
- Selftest: a pawn beside a furnace-beast reads a higher `AmbientTemperature`; no comfort-range hediff exists.

## done
Built: `CompFurnaceWarmthAura` + `FurnaceWarmthField` (AmbientTemperature postfix, per-map registry, in the Pyrelands DLL), `FurnaceWarmthMath` + offline selftest (`selftest_furnace_warmth.py`), `furnaceWarmthStrength` slider, `RM_FurnaceWarmth` deleted. Live felt-temperature read is UNMEASURED: needs a debug [Tool] reading `Thing.AmbientTemperature` on a pawn.
