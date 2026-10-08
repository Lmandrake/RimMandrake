# Live harness re-run 2026-10-07 (acc_harness-27), 11:48-12:00 PDT
Method: `python.exe Transient/l2sweep_run.py <Mod>` on one dev quicktest map (started with l2p3_start.py). Raw JSON: `Transient/l2sweep_<Mod>.json` (pre-rerun copies of the old sweeps in `Transient/l2sweep_prev_20261007/`). Settings: suite context managers restore after each arm; LuminousPigment Config xml md5 unchanged; FallLine onlyOnFallLine probe restored to False. Nothing committed, no ledger verify recorded (no L2 acceptance criterion matches a component wording).

| Mod | Previously failing component | Now | Evidence | Class |
|---|---|---|---|---|
| LuminousPigment | settings_apply.apply_reaches_defs / glowtank_toggle | PASS / PASS | get_defs designationCategory: Production by default, absent after glowTankEnabled=False + apply | - |
| LuminousPigment | build menu really refreshes | UNMEASURED | no tool reads Production's cached designator list; check is def-level only. No "could not refresh the build menu" / "ResolveDesignators not found" warning in Player.log (literal scan, MEASURE_ALLOW_SCAN=1) | HARNESS gap |
| WreckedMachines | spawns_and_inspects_clean (wrecked, kludged, repaired tiers) | PASS x3 | no config errors | - |
| WreckedMachines | researchCost/materialCost/skipRestoration/refurbished/kludged *_rewrites_its_def | PASS (deep=True works) | | - |
| WreckedMachines | allowDonorSmelter / allowFullRestoration _rewrites_its_def | UNMEASURED | get_defs returns `fields: {}` for a NULL designationCategory (same quirk LuminousPigment `_designation` already handles), so `before` reads None | HARNESS |
| WreckedMachines | wreckedRatio_rewrites_its_def | FAIL | check reads CompProperties_Power `idlePowerDraw` (-1.0, a vanilla default constant; VanometricPowerCell itself reads -1.0). The scaled field is private `basePowerConsumption`, never serialised | HARNESS |
| Droidworks | protocol_droid_shifts_prices | FAIL | fire_incident(TraderCaravanArrival) canFireNow=True fired=False. No exception; Player.log: "Faction Thiraora of def OutlanderCivil has no usable PawnGroupMakers for parms groupKind=Trader ... Caravan_Outlander_CombatSupplier" (and Iracan League likewise) | LIST ARTIFACT (no trader-capable faction in the 27-mod list); harness could pick another incident/faction |
| FallLineArrivals | off_fall_line_refused | FAIL | `static_call ProofGate args=""` -> "No public static ProofGate with 0 params" (signature is ProofGate(string args)). Probe with args="x": setting ON -> "REFUSED: setting ON and map is not on the Fall Line"; OFF -> "ALLOWED" | HARNESS (pass a non-empty args, or make ProofGate parameterless); mod behaves correctly |
| FallLineArrivals | anywhere_allows (+ wrecks_toggle_off_refuses) | UNMEASURED | upstream of the above; probe shows ALLOWED with setting OFF | HARNESS |
| UnfinishedLine | volunteer_offered | UNMEASURED | world.line_stands fails upstream first: defs missing FactionDef/RUT_Jawa_FreeDroidEnclaves and RUT_Jawa_GeonosianFoundryHive (live in `src/RimUtinni/UtinniPatches`, `mandrake.rut.patches` not in acc_harness want list). The new ally-the-Enclaves fixture cannot be exercised | LIST ARTIFACT |

## Other failures seen (not in scope, not classified in depth)
- LuminousPigment (8 FAIL / 17 UNMEASURED): patches_applied (Orders designators read as 'RuntimeType'), mat_alive_control, research_gate (Crowncarpet cannot plant on this map), press_is_a_powered_bench (same private basePowerConsumption read, -0.0025 vs -2.5), first_coat (thing id gone), worn_glow (roofStrip not dark), styling_lacquer (no job queued), gods idol; gods chain needs mandrake.rm.ninefold (LIST ARTIFACT). settings_apply.press_buildable_finishes_research UNMEASURED (research_availability has no finished flag).
- Droidworks: nimbus_charges_in_range, full_charge_detonates_on_death, mood_penalty_nearby, ion_overload (RSW_JawaIon_Stun absent: LIST ARTIFACT).
- UnfinishedLine: all chain/truce/cores/tithe failures trace to the same missing factions/settlements.
