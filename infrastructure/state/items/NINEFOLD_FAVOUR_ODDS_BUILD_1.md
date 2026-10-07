# NINEFOLD_FAVOUR_ODDS_BUILD_1: Nine Faults, the Left Behind, and god favour as odds

Spec (ruled by the owner 2026-10-01): `design/Jawa/nine_faults_permanent_rite_2026-10-01.md`, top section.
Build list: §5 there ("What Ninefold needs").

- Nine Faults rite (`mandrake.rut.rites`): break a fresh find; it burns out; Rekko -> Zizzik by value.
- The Left Behind at departure: a working machine left off the ship; Ohm -> Ta'Baa by value, whatever the machine.
- `RM_GodFavourTiltDef` + postfixes on `StorytellerComp.IncidentChanceFinal` and `WeatherDecider.CurrentWeatherCommonality`; the §4 table.
- Fresh-find mark (taken on this map, never run, cleared on first use or departure).
- Mod Settings: master toggle and strength slider.

Done when: each piece works offline-testable per the spec, nothing in the world labels a god as the cause, and no hediff or stat blessing exists.

## Built offline (2026-10-06, FOUNDRY helper; uncommitted, not deployed)

- `src/RimMandrake/Ninefold/Source/GodFavourTilt.cs` — `RM_GodFavourTiltDef {god, incident|weather, direction}`; postfixes on `StorytellerComp.IncidentChanceFinal` and `WeatherDecider.CurrentWeatherCommonality` (player-home maps only). `Less` rows take the reciprocal of the band factor.
- `src/RimMandrake/Ninefold/Defs/RM_GodFavourTilts.xml` — the §4 table, 20 rows (Ishko's "sandstorm and fog" = Sandstorm, Fog, FoggyRain). Every defName measured in the def dump.
- `src/RimMandrake/Ninefold/Source/Offerings.cs` — `MapComponent_NinefoldOfferings` (fresh-find mark + one Leave-behind mark). Taken = `Designator_Claim.DesignateThing`, or `Blueprint_Install` of an inner thing not already the player's. Used = `CompPowerTrader.PowerOn` set true, `Building_WorkTable.UsedThisTick`, or found already powered. Departed = `InitiateTakeoff` commit. "Leave behind" toggle gizmo; `GravshipUtility.AbandonMap` prefix moves Ohm → Ta'Baa by market value and sends the glint letter. An anchored map is never abandoned, so nothing moves there.
- `src/RimMandrake/Ninefold/Source/NineFaults.cs` — fresh-find target worker and outcome worker (destroy, slag hulk, fire on Poor, Rekko → Zizzik × quality, art tale on Excellent).
- `src/RimUtinni/Rites/Defs/RUT_NineFaults.xml` — precept, pattern (always anytime), target filter, behaviour, outcome, the memory thought and the TaleDef.
- Mod Settings (`RM_NinefoldMod.cs`): favour toggle + strength slider, offerings toggle.

Still owed: a live check of every piece; adding `RUT_Ritual_NineFaults` to The Salvation's ideo (.rid/save); the value ramp 200..3000 silver is UNTUNED; the §⑦ satiation-bank payment and the `CompBreakdownable.DoBreakdown` hook are not built (the bank does not exist in `GameComponent_Ninefold`).
