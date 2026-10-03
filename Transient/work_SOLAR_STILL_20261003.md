# SOLAR_STILL work 2026-10-03
- claimed+started. Plan: RM_SolarStill.cs (building comp: sun-gated, fed by contents), defs, settings, validation, art search.
- DONE offline: Source/RM_SolarStill.cs (+csproj Compile), RM_SunTableKind.still, settings solarStillEnabled/wringingStillEnabled/stillRateMultiplier (RM_GlassChainMod.cs), Defs/ThingDefs_Buildings/RM_SolarStill.xml (RM_SolarStill, RM_WringingStill), Defs/ThingDefs_Items/RM_StilledWater.xml (+RM_Brine), Defs/ThoughtDefs/RM_Thought_DeadDistilled.xml, validation.py (solar_still_defs, settings, ThoughtDef parsed), art RM_SolarStill copied from artpipe done/ to Textures/Things/Building/Production.
- Choices where spec ambiguous:
  * Sun gate: reused RM_CompSunPowered (kind still) + RM_SunPower.FactorAt; gale blocks via noSunWeathers. Rate = sunFactor x slider x (2 if RM_PearlLens lying in the still; lens not consumed). Cycle 6000 ticks at full sun.
  * Still is a Building_Storage; the feedstock is hauled into it (no bills/UI). Feeds: RM_Brine 1->3 L, eggs 1->2 L, raw meat 5->2 L; wringing still adds corpses: bodySize x4 L.
  * No brine item existed: added RM_Brine (nothing yet produces it; cave seep source is a later item).
  * Output: DBH_WaterBottle if live, else RM_StilledWater (1 L, carries RM_CompProperties_WaterVolume). FlowWorks liquid stock NOT used (hand-fed item machine).
  * Ledger: every cycle calls RM_WaterLedger.Notify_Drawn. Corpse witness thought is RM-tier RM_Thought_DeadDistilled (-4, 1.5d, all free colonists); Sun-Debt "drawing" stage is for the RUT layer to patch in.
  * Wringing still has no art job: reuses RM_SolarStill tinted. Water/brine items reuse the sun-glass icon tinted (no art job).
- Build OK (stage_build + extra_dirs). selftest 74/74. validate_patch: 0 errors in new files (remaining errors are other pending-art defs).
