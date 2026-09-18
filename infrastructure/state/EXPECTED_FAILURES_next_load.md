# Decision strings — CAVERNS_PARITY_BUILD_1 shutdown window, 2026-09-18

Written BEFORE the game closes (rimworld-load-round §2/§3). Bridge held by BENCH
on the owner's word ("You have the bridge.").

## Load A — minimal list + LanternDeeps chain (22 s), quicktest the Deeps pocket map

Riding: ONE new assembly (`RimMandrake.Utinni.LanternDeeps.dll`, rebuilt after the
`RUT_Deep*` rename) + its XML. Solo per §3 — nothing else with a DLL rides this load.

| item | decision string in Player.log / bridge | baseline | means |
|---|---|---|---|
| DLL attaches | NO `TypeLoadException` / `ReflectionTypeLoadException` naming `RimMandrake.Utinni.LanternDeeps` | 0 | present ⇒ assembly broken, stop |
| GenSteps resolve | NO `Could not find a type named RimMandrake.Utinni.LanternDeeps.GenStep_ScatterLanternstone` (nor `GenStep_DeepFloraGate`) | 0 | present ⇒ XML/DLL class-name mismatch |
| biome loads | `jawa/get_defs BiomeDef RUT_LanternDeeps` returns a def with `isCavern` and weather `RUT_DeepCalm` | n/a | absent ⇒ def discarded, read config errors |
| rename landed | `RUT_DeepNuitae`, `RUT_DeepArpeau`, `RUT_DeepGreyLady`, `RUT_DeepDulcisPlant`, `RUT_DeepRawDulcis` all resolve via `jawa/get_defs`; `Config error` count naming any of the five = 0 | 0 | a dangling old name ⇒ a reference I missed |
| no BMT_ coupling left | NO `Could not resolve cross-reference` line naming `BMT_` inside a LanternDeeps def context (on the minimal list the donor is ABSENT, so any surviving BMT_ ref MUST log here) | 0 | present ⇒ parity build incomplete — name the def |
| pocket map generates | quicktest → build/spawn the emergence entrance → enter → a map with biome `RUT_LanternDeeps` exists (`jawa/list_maps`) | n/a | generation exception in log ⇒ GenStep defect |
| crystals scatter | `jawa/list_things` on the pocket map counts `RUT_LanternstoneSmall/Medium/Large/Huge` > 0 total | n/a | 0 ⇒ GenStep ran but placed nothing (order 320 / density setting) |
| flora gate | at least one `RUT_Deep*` plant on the pocket map | n/a | 0 with crystals present ⇒ DeepFloraGate misconfigured |
| magenta is EXPECTED | pink textures on crystals/flora are NOT a finding (art in pipeline) | — | do not file |

Expected-failure signature for the one assembly: a `TypeLoadException` mentioning
`RimMandrake.Utinni.LanternDeeps` — anything else in the log is NOT this DLL.

## Load B — full list (632, ~15 min), fresh def dump

| item | string | baseline | means |
|---|---|---|---|
| dump lands | `[RimDefDump]` in Player.log; a new `DefDump/captures/<ts>` dir; fingerprint ≠ `2026-09-18T17-31-09Z` | — | absent ⇒ marker not armed / not at main menu |
| precept resolves | `validate_save_artifact.py "src/Jawa/ideoligion/The Salvation.rid"` against the NEW dump: 0 dangling (was 1: `RUT_FungusEating_DontCare`) | 1 | still 1 ⇒ UtinniPatches deploy did not land |
| harvest baseline | `harvest_log.py` exit 0, or every above-baseline class explained | prior run | — |
| RSW_ kinds present | dump contains `RSW_Kreetle`, `RSW_Scavrat`, `RSW_Runyip`, `RSW_Scurrier` (missing from the stale capture) | absent | still absent ⇒ real mod-list regression, NOT a capture artefact |
| WeatherSuite + Injections | both packageIds in the loaded list per the log's mod roster | — | — |

## Not riding this window
- No Cherry Picker cut, no ModsConfig removal of the Biomes! family — the cut waits on
  quicktest parity + BiomeCast regen (scoping doc §4 step 3).
