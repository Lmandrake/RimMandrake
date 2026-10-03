# WeepingStones / Contagion livefix2, 2026-10-03

Edited: `src/RimMandrake/WeepingStones/validation.py`, `src/RimMandrake/Contagion/validation.py` only.

| item | disposition |
|---|---|
| WS (a) water_truce_extension_present | HARNESS. get_defs flattens a modExtension to its fields (`[{"radius":10.0}]`, class absent). Source `RM_WeepingStones_Biome.xml` has RM_WaterTruceExtension. Check now accepts the name or the `radius` field. |
| WS (b) slider round-trips | HARNESS (Utils/modcheck/suite.py `set_setting` compares '3' to '3.0'; not edited, out of scope). Sliders now set via mod_settings_field and compare numerically. Other `set_setting` uses with bools unaffected. |
| WS (c) designator_hidden_when_off | UNRESOLVED, stays FAIL (message now names the contradiction). Source is correct (`Visible => stockedPoolsEnabled`; setting read back False) but the bridge row says visible=true. Suspect stale deployed DLL or bridge listing cache; not provable offline. Not EnvironmentalHazards. Mod not changed. |
| WS (d) job timeouts | HARNESS. runner client has a fixed 30 s reply timeout; ordered_job alone took 17 s. Jobs now run order+wait inside `_patient` (240 s). |
| WS (e) site_ready_stock/harvest | HARNESS. `destroy_batch` leaves pawns alone ("2 pawn(s) left alone"); `_reset_pad` and `_teardown` now also `destroy_bulk filter=nonColonists`. |
| Contagion biome_table_and_roster | HARNESS. Extension present in repo XML; live read is flat fields (meanDaysBetweenBurns, burnDurationTicks, tellLeadTicks...). Check accepts those fields. Downstream UNMEASUREDs there were upstream cascade. |
| Contagion genome/extraction_surgery | HARNESS. do_bill_now (2500 ticks) and the 1500-tick wait wrapped in `_patient`. |
| Contagion burn/coalescence/repulsor UNMEASURED | Not asked: surprise aborts (RM_Slimification on colonists), left as is. |

Selftests: both pass. No live run done.
