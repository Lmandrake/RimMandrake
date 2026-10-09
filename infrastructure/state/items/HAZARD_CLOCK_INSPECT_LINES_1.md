# HAZARD_CLOCK_INSPECT_LINES_1 — TB-4: Inspect lines for Grey lamp burn time, twilight well phase, grav engine crust count

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row TB-4 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| TB-4 | Readable hazard clocks on things the player already looks at: a Grey lamp says how long it has burned steadily (not the threshold — the watcher at the rim stays the warning), a twilight well says it is opening/waning, and the grav engine says how many crust cells still hold the deck. All three numbers already exist. | nothing | S | low | TerminalBiomes | No inspect override on lamps, wells or engine (`grep GetInspectString` hits only ScaldKit, CryoGrower, SunSphere, door patch `RM_GreyHullCrust.cs:353`); burn book `RM_GreyLampResponse.cs:34`, crust count `CountCrust` `:~320`. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: Inspect strings added on the three things; toggle in Mod Settings; numbers read from existing state.
