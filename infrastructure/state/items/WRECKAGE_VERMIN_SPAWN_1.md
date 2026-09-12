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
