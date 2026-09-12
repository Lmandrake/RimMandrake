# WRECKAGE_VERMIN_SPAWN_1 — vermin spawn from the wreckage itself

Owner, 2026-09-12 (verbatim on the filing event): "Yes vermin should be able
to spawn from wreckage." Confirms the frozen fall_line.md design line ("Ship
vermin nests under the larger hulls, living on what falls") as a build
requirement, not just flavor.

## What already exists (checked 2026-09-12, BENCH)
- Biome-level wandering: the ship-vermin band (Scavrat, WompRat, Mynock,
  VFEI2_Fuelmite; vanilla Rat is biome-native) is in `wildAnimals` of the five
  biomes the Fall Line crosses via `BiomeCast_Ashkarr.xml`, deployed
  byte-identical (Mynock weights 0.3/0.3/0.3/0.2/0.5).
- ShipVermin mod (`src/RimMandrake/ShipVermin`, SHIP_VERMIN_MOD_1 closed
  2026-09-11): About + `RSW_Mynock_ShipVermin.xml` comp patch + alert DLL. No
  wreck-anchored spawner exists anywhere.

## spec
- A spawn mechanism anchored to wreckage things/structures (Fall Line hulks,
  wreck salvage sites, grounded ruins): nests under/inside the wrecks emit
  vermin over time — a comp on wreck defs or a MapComponent keyed to wreck
  presence, whichever survives contact with how the hulks are actually built
  (verify the wreck defs' identity first; do not guess defNames).
- Species drawn from the ship-vermin band; respect the ruled pressure curve
  ("Nuisance unless there are many").
- Mod Settings per MOD_OPTIONS_RETROFIT_1: wreck-spawning on/off, rate, which
  species.
- Home: the ShipVermin mod (RimMandrake tier — mechanism is generic
  "vermin from wrecks"; any campaign-specific wreck-def wiring goes in the
  Utinni layer).

## verify
On a quicktest map with a wreck structure placed: vermin appear attributable
to the wreck (not biome wander) at the configured rate; toggling the setting
off stops it; no spawns on wreckless maps from this mechanism.

## built 2026-09-12, FOUNDRY — offline complete, live verify OWED

Mechanism: `RM_CompProperties_VerminNest` / `RM_CompVerminNest`
(`src/RimMandrake/ShipVermin/Source/`) — a generic ThingComp, attached via a
comps-list patch to any wreckage ThingDef, that periodically spawns one wild
pawn of a settings-enabled species nearby. Reuses
`RM_MapComponent_VerminPopulation`'s existing group-tag pressure pool
(default tag `ShipVermin`, hard cap 12 — the SAME pool RSW_Mynock's breeder
already presses against), so a nest and a breeding population share one
ceiling. Home is the ShipVermin mod per the spec; the mechanism decides
nothing about which ThingDef is "wreckage".

Wiring (campaign-specific, RimUtinni layer):
`src/RimUtinni/UtinniPatches/Patches/WreckVerminNest_ShipChunk.xml` attaches
the comp to `ShipChunk_Mech` (Odyssey's "mechanoid ship chunk" — the exact
prop scattered six-per-hulk in `RUT_Jawa_GroundHulk`, and the only real
Thing the ground-hulk PrefabDef actually places that is debris rather than
a generic Ancient-Danger casket). Verified via `validate_patch.py --live
--defs` (592-mod live load set): 0 errors, ShipChunk_Mech resolves, the
outer conditional matches.

Mod Settings added to ShipVermin's own `ShipVerminSettings`
(`RM_ShipVerminMod.cs`): wreck-spawning on/off, a 0.25x-3x rate multiplier,
and a per-species checkbox roster (Mynock, Scavrat, Womp rat, VFEI2_Fuelmite
gated by GetNamedSilentFail, Rat).

Both `RM_CreatureBehaviors.csproj` and `RM_ShipVermin.csproj` build clean
(0 warnings, 0 errors) via the Windows-native dotnet toolchain.

**Not done — no bridge/game session this run** (`./game` reported DOWN,
bridge FREE, no live RimWorld process): the item's own `## verify` — vermin
appearing attributable to a placed wreck at the configured rate, the
setting stopping it, no spawns on a wreckless map — has NOT been run live.
Blocked rather than closed; the next session with the game up should drive
a quicktest with a `ShipChunk_Mech` placed (or a real ground-hulk map) and
run that verify before closing.
