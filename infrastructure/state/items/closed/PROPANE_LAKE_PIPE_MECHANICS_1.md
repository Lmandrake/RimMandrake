# PROPANE_LAKE_PIPE_MECHANICS_1 — the propane lake's pipe/vent/saturation build ladder

## what

`design/Jawa/proposals/propane_gas_deep_design.md` §9, "Build ladder — RULED
(owner, 2026-09-01): six rows v1, two cut." Four of the six rows are still
entirely unbuilt (checked this pass — zero hits anywhere in the repo for
`CompPipeNetwork`, `CompPipeRupture`, `RUT_GasVent`, `GasSaturationTracker`):

1. `RUT_GasVent` (§3): self-igniting puffs, no depletion until actively
   pumped; pump-removal triggers a violent map-wide flammable release that
   clears by wind.
2. `GasSaturationTracker` (§5): transient during release events, perpetual in
   authored caverns and dead-sarlacc dungeons (with rotstink).
3. `CompPipeNetwork`/`CompPipeRupture` (§4): ruled on-map manual shutoff
   valves, plus the faction-relations consequence for leaving a rupture
   running.
6. Saturation heist (§5): ruled enemy loadout — strictly non-flammable/
   non-thermal/non-explosive (Geonosian sonic, javelins, catapults,
   vibro-weaponry).

Rows 4 (nightside propane lake, refueled in place) and 5 (lake-margin
creature) are DONE — `RUT_PropaneLake` BiomeDef (`LIQUID_BIOMES_MAP_1`) and
`RUT_VWake` (`COMMISSION_LEDGER_CLEANUP_1`, 2026-09-25).

## why filed

`RUT_VWake`'s own ruled behaviour is "propane-native, agitated by pumping,
attacking pawns and pipe on sight" (`the_propane_lakes.md` §4) — the
pump-agitation half of that needs row 3's `CompPipeNetwork` to exist at all.
`RUT_VWake` currently ships with plain elevated aggression
(`manhunterOnDamageChance 1.0`) standing in for the ruled trigger; this item
is what closes that gap, and the other three rows besides.

Too large for an inline commission (real new comp classes, a map-wide event
system, a heist encounter) — see `COMMISSION_LEDGER_CLEANUP_1`'s own
`## work owed` section for the general rule this follows.

## work owed (not done by this item's filing)

Nothing built yet. A build pass needs to: read `propane_gas_deep_design.md`
§3-§5 and §9 in full (the ruled model is spelled out there, not re-derived
here); author `RUT_GasVent` (ThingDef + ignition/depletion comp);
`GasSaturationTracker` (a MapComponent, transient vs. perpetual per §5);
`CompPipeNetwork`/`CompPipeRupture` with manual shutoff valves; the
saturation-heist incident with the ruled non-thermal enemy loadout; and,
last, wire `RUT_VWake`'s aggression to read the pipe network's agitation
state instead of its current flat `manhunterOnDamageChance`.

## caused by

`COMMISSION_LEDGER_CLEANUP_1` — the_propane_lakes sheet's
`v-wake-propane-sea-exotic-kin-propane-native-agitated-by-pum` slug named
this gap while building the creature itself.
