# FLOWWORKS_SETTINGS_SCOPE_RESET_1 — FL-5: FlowWorks settings say when each takes effect plus per-section reset

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row FL-5 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| FL-5 | The settings screen says when each setting takes effect: "now", "next pulse", "new ponds only" or "new maps only". Each section gets its own reset-to-default button. Some text already does this ("decided ONCE", "Set when the map first finds something"), but the source budget and drill-odds sliders do not, and players will think the slider is broken. | Text only, plus a reset button per section. The reset pattern already exists in EnvironmentalHazards, SolarMirrors and KineticArms. | S | low | FlowWorks | RimMandrakeFlowWorksMod.cs:530-545 (the budget slider has no scope note) and :959 (drill odds). There is no reset button in the FlowWorks settings (grep). Body capacity is fixed at formation (RM_LiquidStock.cs:154). MOD_OPTIONS_RETROFIT_1 does not mention reset buttons. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: FlowWorks builds clean; budget and drill-odds sliders carry scope notes; each section has a reset-to-default button.
