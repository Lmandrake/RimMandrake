# DEEPFIRE_GOD_BRIDGE_DELTAS_1: report

Spec §10 step 10 (`design/RimMandrake/deepfire_luminous_pigment_spec.md`), which covers the Ninefold
god deltas, the statue extension and the LightsOut check. Built, compiled clean, and **NOT live-run**.
Nothing was deployed.

## What was built

All code is in `src/RimMandrake/LuminousPigment/Source/`.

- **`DeepfireGodDeltas.cs`** (new). This implements the §5.2 rows:
  - **First coat on a building, floor or item** (`deepfire.coat`): every god gets +3. The trio (Mob'Unloo, Rekko, Zizzik) get +8 instead, and Ishko gets −3.
  - **First coat on apparel or a weapon** (`deepfire.worn`): the same, except Ishko gets −8.
  - **First coat on a thing whose def carries `DeepfireGodExtension`** (`deepfire.statue`): that god gets +15 (for Ishko's own idol, Ishko gets −15). Every other god gets +3, and Ishko keeps his −3 when the idol is another god's. An unknown god name counts as untagged.
  - **Sold or gifted** (`deepfire.sold`): Mob'Unloo gets +8, once per deal. This comes from a Harmony prefix and postfix on `TradeDeal.TryExecute`. The prefix reads the deal before `ResolveTrade`/`Reset` empty it, and walks `thingsColony` in the same order that `TransferNoSplit` hands things over. The postfix pays out only when `__result && actuallyTraded`, which is Ninefold's own gate. A "deepfire good" is either the `RM_Deepfire` jar or any thing (minified or not) with at least one coat.
  - **Anti-pinning (§5.2)**: once a def (a ThingDef, or a floor's TerrainDef) has had `godDeltaDiminishAfter` first-coat events in a game, every later delta for that def shrinks to ±1. The count is stored per game in `GameComponent_Deepfire` and saved with it.
- **Hooks.** In `CompDeepfire.AddCoat`, the call sits on the same first-coat latch as the quality bump (`coats == 0 && !bonusApplied`), so stripping and re-coating cannot farm gods. `MapComponent_DeepfireLights.AddFloorCoat` fires when a cell goes from 0 to 1 coats.
- **`NinefoldDeltaBridge.cs`** now also exposes `GodNames` (read from the live `God` enum), `IsGod`, `TryGetSatiation`, `MagnitudeMultiplier` and `EngineEnabled`, all by reflection. Its stale header was corrected: it said only two rows were wired.
- **Settings.** Added `godDeltaIshko` (3), `godDeltaStatue` (15) and `godDeltaDiminishAfter` (10), each with a slider. The labels were reworded to match what each number now drives.
- **`DeepfireLightsOutCompat.cs`** (new). See below.
- **`DeepfireGodDeltaDebugActions.cs`** (new). These are the proof actions, which show up as `T: GodDeltas: ...` and `T: LightsOut: ...`.
- **Not built:** the "coated god-statue destroyed" row from §5.2. It is not in this item's Build list.

## Engine/API facts confirmed

- The following come from RimSage: `TradeDeal.TryExecute(out bool actuallyTraded)` (both the gift path and the trade path), `Tradeable.ActionToDo`, `thingsColony`, `ForceToDestination`/`ForceToSource`, the order used by `TransferableUtility.TransferNoSplit`, `CompGlower.Glows`/`UpdateLit`, and `ListerThings.EverListable`.
- The following come from our own source (Ninefold): `GetSatiation(God)`, `ApplyDelta` multiplying by `RM_NinefoldSettings.eventMagnitudeMultiplier`, and satiation being clamped to ±100.

## LightsOut check

**Finding: LightsOut WOULD have switched our proxies off.** Spec §8 assumed they were exempt because they have "no `CompFlickable`, no power". They are not exempt. This comes from the installed LightsOut DLL (workshop 2584269293; its root `Assemblies/LightsOut.dll` is the 1.6 load folder), decompiled with ilspycmd:

- `Lights.CanBeLight(ThingWithComps)` accepts any thing that meets three conditions:
  - it has a `CompGlower`;
  - it has none of CompPowerPlant, HeatPusher, Schedule, TempControl or ShipLandingBeacon;
  - its lowercased defName contains `light`, `lamp` or `illuminated`.

  Both `rm_deepfirelightproxy` and `rm_deepfirewornlightproxy` contain `light`, so both qualify.
- `Lights.DisableAllLights(room)` walks `room.ContainedAndAdjacentThings`. Ethereal things are region-listed: `ListerThings.EverListable` excludes only Motes and Projectiles (RimSage). It calls `DisableLight`, which sets `Resources.BuildingStatus[thing] = false`.
- Its `CompGlower` postfix (`DisableLightGlowPatch`) then forces the glow to `false` whenever `Resources.CanConsumeResources(parent) == false`.

As a result, an empty room going dark, or a pawn falling asleep, would have turned off the glow of every coated wall, floor cluster and item in it.

**Fix (`DeepfireLightsOutCompat.cs`).** This is applied by reflection only when LightsOut is loaded, using its own Harmony id. A prefix makes `Lights.CanBeLight` return false for our two proxy defs. As a second guard, a postfix makes `Resources.CanConsumeResources(ThingWithComps)` return null for them. The patches bind by position (`__0`), because the parameter names come from the decompiler rather than from a stable contract. If either method has changed shape, it logs a warning once.

## Proof harness

The harness is `src/RimMandrake/bridgetools/prove_deepfire_god_deltas.py`. **It has not been run.** It needs a tier with LuminousPigment (this build), Ninefold and LightsOut:

    python.exe src\RimMandrake\bridgetools\prove_deepfire_god_deltas.py --start

Each god action snapshots the satiation of all nine gods immediately before and after one real call, and reports both the start value and the change. The script checks each change against the spec number × `eventMagnitudeMultiplier`, clamped to ±100 from that start value. It covers the wall, a second coat, a parka, a Rekko idol and an Ishko idol, a floor cell, the diminish rule and the sold case. The LightsOut step uses a StandingLamp as a control: it must be switched off, while the proxy must keep glowing. If Ninefold or LightsOut is absent, the script reports UNMEASURED and exits 2 rather than passing.

Two parts are proven by a stand-in rather than the real path:

- **Idol:** SculptureSmall is tagged at runtime for the one coat and untagged afterwards, because the Utinni statue mod is not built yet.
- **Sold:** Harmony's `GetPatchInfo` shows the patch is registered, and the action calls the patch's own `DealSellsDeepfire` on real `Tradeable`s. A quicktest has no trader, so the full trade path is not exercised.

## Verification

- `dotnet build` is clean (0 warnings, 0 errors). The DLL and `.srchash` were rebuilt.
- All 24 LuminousPigment XML/csproj files parse, and `py_compile` of the harness passes.
- `run_selftests.py`: 77 of 79 passed, with 1 unmeasured (`selftest_tool_metadata.py`) and 1 failure. The failure is `selftest_deployed_biome_refs.py`: 19 dangling biome refs in the deployed Mods folder. It is unrelated to this change and comes from the game-folder state, not this repo diff.
