# VEHICLE_FRAMEWORK_AERIAL_DEBUG_1 — Ground All Aerial Vehicles / Spawn Airdrop

Filed 2026-08-29, FOUNDRY, at session end (context restart imminent). Two Vehicle
Framework debug actions surveyed but explicitly NOT built in `BRIDGE_KCSG_VGE_TOOLS_1`
because their bodies reach into unread internal state:
- **"Ground All Aerial Vehicles"** — `Find.World.GetComponent<VehicleWorldObjectsHolder>()
  .AerialVehicles`, then a private `DebugLandAerialVehicle(aerialVehicle)` per vehicle
  whose body was never read, plus a second pass over `Find.Maps` for `VehicleSkyfaller`
  things mid-flight.
- **"Spawn Airdrop"** — `AirdropSkyfaller.cs:172`, body not read this pass.

Owner ruling, asked directly: **"Yes, worth it"** — Vehicles are a real, active part
of this campaign, not incidental.

## Spec
1. Read `DebugLandAerialVehicle`'s full body (referenced but not opened this
   session) in `vendor/mod_sources/VehicleFramework_src/.../Harmony/Patches/Patch_Debug.cs`.
2. Read the full `AirdropSkyfaller` spawn path for "Spawn Airdrop".
3. Both routes need reflection (Vehicle Framework's assembly isn't referenced by
   this project, matching `JawaBenchVehicleTools.cs`'s own established pattern) —
   `VehicleWorldObjectsHolder`, `AerialVehicleInFlight`, `VehicleSkyfaller` are all
   VF-internal types.
4. Build only once the exact call sequence is read, not inferred from the debug
   action's one-line dispatch — same rule that caught the KCSG extension-method
   trap in the sibling item.

## Verify
Builds clean, signatures read from vendored source (already present at
`vendor/mod_sources/VehicleFramework_src/`), no duplicate alias, deployed and
proven live against a real aerial vehicle / airdrop on the live mod list.

## criteria
- [ ] `DebugLandAerialVehicle` and the airdrop spawn path read in full.
- [ ] Built via reflection, matching the established no-hard-reference pattern.
- [ ] Builds clean, no duplicate alias.
- [ ] Deployed and proven live.

--- history ---
