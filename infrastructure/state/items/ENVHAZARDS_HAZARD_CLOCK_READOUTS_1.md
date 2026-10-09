# ENVHAZARDS_HAZARD_CLOCK_READOUTS_1 — EH-4: EnvironmentalHazards: show the hazard clocks (venomvine contact and next scratch, wet-bulb ramp, warm ground, tar-beast wake) on hover or as a near-source alert

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row EH-4 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Same idea as HAZARD_CLOCK_INSPECT_LINES_1 (TerminalBiomes) but in EnvironmentalHazards: the map components (MapComponent_ContactVenom, RM_GameCondition_WetBulb, RM_MapComponent_WarmGround) show nothing and EH has no Alert subclass. Text and one alert only; numbers already exist. Mod Settings toggle; PatchApplier for any Harmony.

The row:

| EH-4 | **Show the player the hazard clock.** The map-wide hazards keep timers the player never sees: venomvine contact and the next scratch, the wet-bulb ramp, warm ground, how close the tar beast is to waking. Show them on hover over the source, or as a small alert while one is close. This turns "is this even on?" into something the player can read. | inspect text and alert classes | M | low | EnvironmentalHazards | 12 EH files already carry inspect text, all on comps (`RM_CompWorkedLottery`, `RM_CompFloodIgniter`, …); the map components (`MapComponent_ContactVenom`, `RM_GameCondition_WetBulb`, `RM_MapComponent_WarmGround`) show nothing; there is no `Alert` subclass in EH |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: EnvironmentalHazards builds; inspect text added on the sources; one Alert class gated by a toggle; toggle in Mod Settings.
