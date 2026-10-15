# Fuel-moat independent review (BENCH reviewer, 2026-10-15)

Scope: every file changed by b0ec1721ff 1a5a2ceee7 6238e06206 b7392d3d39 538e17abf9. RM_LiquidFire.cs, RM_FuelFireMath.cs and FuelBlastInvestigation.cs (builder-CLEAN) re-read in full for the focus areas.

Focus areas: no hard-freeze path found (blasts <=4/tick, cells <=400/tick, one body <=20000 cells and <=240 blasts, <=8 new bodies a check; explosion->ignition only ever writes the pending dict, never the det lists being iterated; Fire/explosion hooks re-enter TryQueue only and planned cells are skipped). Chemfuel: front step >=1 tick, burning cells never re-queued, BurnOffLevel cannot go below 0, every level counted. Save/load: det schedule, burning, carried and pending saved; `detonating` rebuilt in PostLoadInit; blastHops (thing-id keyed) is per instance, not static, and unsaved, so a blast in flight across a reload lights at hops 0 (benign). Utinni hook: static event bound by reflection, a no-op when either mod is absent; one raid per map per day via the saved lastFuelBlastTick. Settings mid-fire: fire off clears everything; detonation off now drops the schedule (D1).

Selftests after fixes: fuel_moat, call_sites, flowworks_stock (the C# SelfTest incl. FuelFireChecks), empire_ladder, empirepursuit_fuzz, settings_screens: 6/6 GREEN. DLLs: FlowWorks + EmpirePursuit b78028dd4a (from c3498ecfd0), EmpirePursuit again from d518b2b296.

| file | state | review | notes | fix sha |
|---|---|---|---|---|
| `src/RimMandrake/FlowWorks/Defs/Canals/FluidDefs/FlowWorks_PitFluids.xml` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/Defs/Canals/ThingDefs/FlowWorks_LiquidFire.xml` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml` | DIRTY | generated | byte-identical on regeneration; cleans with the generator |  |
| `src/RimMandrake/FlowWorks/Patches/LiquidTypes/RM_LiquidDef_AstrofuelAdoption.xml` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/Source/FluidDef.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/Source/RM_FuelFireMath.cs` | CLEAN | builder CLEAN, re-read in full | no finding |  |
| `src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs` | CLEAN | fixed | D1: detonation schedule kept firing Bomb blasts after astrofuelDetonationEnabled was switched off mid-chain (now dropped, like fire-off); D2: static shoveScratch kept Pawn refs past the call / into the next game (cleared) | c3498ecfd0 |
| `src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs` | DIRTY | not full-read | fields, ExposeData, masters (lines 1-640) and the Burning-liquid screen read, no finding; the rest of 1585 lines not read |  |
| `src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorks_DefOf.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/Source/SelfTest/FuelFireChecks.cs` | CLEAN | builder CLEAN | not re-read |  |
| `src/RimMandrake/FlowWorks/Source/SelfTest/GptFixesAChecks.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs` | DIRTY | not full-read | 1-line change reviewed; 1871 lines not read |  |
| `src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj` | CLEAN | full-file read | no significant finding |  |
| `src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py` | DIRTY | not full-read | regenerated: every output byte-identical; the changed row reviewed; 1666 lines not full-read |  |
| `src/RimMandrake/FlowWorks/northstar/extensions.py` | DIRTY | fixed, not full-read | D5: fuel_moat_astrofuel FAILed on a rerun within a day (raid cooldown); now UNMEASURED. Fuel chains + diff reviewed; 2860 lines not full-read | d518b2b296 |
| `src/RimMandrake/FlowWorks/northstar/selftest_flowworks_northstar.py` | DIRTY | not full-read | count 123->125 matches the two new bools |  |
| `src/RimMandrake/FlowWorks/northstar/site_spec.py` | DIRTY | not full-read | 2-line change reviewed |  |
| `src/RimMandrake/FlowWorks/review_map.py` | DIRTY | not full-read | the two fuel stations reviewed (light mark adjacent to the moat, frozen unlit); 1662 lines not read |  |
| `src/RimMandrake/FlowWorks/review_map_coverage.py` | DIRTY | not full-read | 3 new rows reviewed |  |
| `src/RimMandrake/FlowWorks/selftest_flowworks_call_sites.py` | DIRTY | not full-read | regex change reviewed; passes |  |
| `src/RimMandrake/FlowWorks/selftest_flowworks_fuel_moat.py` | CLEAN | builder CLEAN | not re-read; passes |  |
| `src/RimMandrake/Utils/selftest_settings_screens.py` | CLEAN | CLEAN before this review | not re-read; passes |  |
| `src/RimUtinni/EmpirePursuit/Languages/English/Keyed/EmpireLadder.xml` | CLEAN | fixed | desc follows D3 | c3498ecfd0 |
| `src/RimUtinni/EmpirePursuit/Source/EmpireLadder.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/EmpireLadderMath.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/EmpirePursuit.csproj` | CLEAN | fixed | D4: header claimed AssemblyName RimMandrake.Utinni.EmpirePursuit (it is RuthlessPursuingMechanoids) and building from the read-only mirror | d518b2b296 |
| `src/RimUtinni/EmpirePursuit/Source/FuelBlastInvestigation.cs` | CLEAN | fixed | D3: raid QUEUED hours ahead on any map; vanilla IncidentQueue/Storyteller.TryFire never re-check the target, so a blast on a temporary map left before the drop fires a raid at a removed map. Now home maps only (Visibility still rises) | c3498ecfd0 |
| `src/RimUtinni/EmpirePursuit/Source/SelfTest/Program.cs` | CLEAN | full-file read | no significant finding |  |
| `src/RimUtinni/EmpirePursuit/Source/Settings.cs` | CLEAN | full-file read | no significant finding |  |
