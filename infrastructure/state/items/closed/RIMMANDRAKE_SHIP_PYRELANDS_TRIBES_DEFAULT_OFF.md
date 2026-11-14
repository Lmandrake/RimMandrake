# RIMMANDRAKE_SHIP_PYRELANDS_TRIBES_DEFAULT_OFF

## spec
Owner, by card 2026-11-13 (~3:50 PM PST), "One mod, Tribes next version": Pyrelands is one mod with one Design Version.
Pyrelands 0.1.0 is the biome alone; the Deep Desert Tribes (rite, visit, fruit defence; design
`design/concepts/PyrelandsMechanics`) are Pyrelands 0.2.0. The card's stated cost: "Tribes code already in the mod must
switch off cleanly for 0.1.0". Recorded on `RIMMANDRAKE_ADOPT_MOD_DESIGN_VERSIONS_SO_JUDGE_CAN_PASS`.

Measured at 01b0e4f07b (2026-11-13): the Tribes code is NOT in `mandrake.rm.pyrelands`. It ships in the separate package
`mandrake.rut.pyrelandsmechanics` (`src/RimUtinni/PyrelandsMechanics`). Its three switches all default ON:
`PyrelandsMechanicsSettings.fireRiteEnabled`, `flameHarvestEnabled` (the visit), `arsonJusticeEnabled` (the fire raid),
initialisers at `Source/PyrelandsMechanicsMod.cs:22-28` and Scribe defaults at lines 42-44. `mandrake.rm.pyrelands`
reaches the rite only through `PyrelandsFireRiteHook` (null when the Utinni mod is absent).
`PyrelandsMechanicsGate.cs` is the whole-mod gate (Pyrelands "Mod enabled" and the Baroque Biomes roster toggle), not a
Tribes switch. No separate fruit-defence switch or code was found (grep for warn/defence in that Source: nothing).

Do: ship those three switches OFF (initialiser and Scribe default), update any shipped-defaults table or selftest that
pins them (MOD_OPTIONS_RETROFIT_1 reads the initialisers; `src/RimMandrake/Utils/selftest_settings_screens.py`), and keep
each switch's off path clean (no incident, no rite, no log noise). Do NOT use `RM_PyrelandsSettings.fireClockEnabled` for
this: it also gates the biome's own scheduled fronts and the opening "yesterday fire" (`PyrelandsFireFront.cs:101,215`),
which are 0.1.0 bars. Related finding: that setting's label "Fire clock (flame harvest / fire raid / fire rite)" and
tooltip "Off: those incidents never fire" (`RM_PyrelandsMod.cs:508`) undersell that it stops the biome's own fire; the
label should be fixed in the same pass (Pyrelands 0.1.0, a Problem: a player turning off the Tribes would lose the burn).

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/pyrelands_tribes_default_off_accept.py` exits 0 with
`PASS: 3 Tribes switches ship off`. Watched failing at 01b0e4f07b: exit 1, six rows (each switch: initialiser ['true'],
Scribe default ['true']); evidence `D:\ClaudeWork\rimmandrake\helpers\maturation_rulings_20261113\tribes_test_base.txt`.
Passability: a copy with the six literals set to false gave PASS, exit 0.
Not covered by the test (builder owes it): the label fix above, and an offline check that with all three off no
Tribes incident or rite can fire (`RM_BurnKernel.TribesIncidentSwitchesOn` / `RiteRoll` already take the switch).
