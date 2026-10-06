# VEXXITH_CLOSED_LOOP_BUILD_1 — FOUNDRY build log 2026-10-06 (offline, uncommitted)

## Rulings (2026-10-03, BENCH notes on the item)
Harmony acid patch goes in Cauldron; vexxith stays strong (HP x1.6, "poor walls/weapons" deleted);
vexxith-only items: filter vessels, vent-cap liners, ship scab-scrapers; plus an acid-proof vexxith door.

## Sweep
No acid-immunity, vexxith door, liner, vessel or scab-scraper existed anywhere in src/. AcidBurn (Core) is the
acid DamageDef; Warscar (src Scarlands) ships RM_BloomAcid. Filter-Works and gas-tap scaffold are unbuilt
(CAULDRON_MECHANICS_BUILD_1 parts 3/4, BLOCKED); ship-scab mechanic (slate E / GPT "Scabweight") was declined.

## Built (src/RimMandrake/Cauldron)
- Source/RM_VexxithAcidImmunity.cs: RM_AcidDamageExtension, RM_AcidImmuneExtension, Harmony prefix on
  Thing.TakeDamage, door architect gate. csproj: Harmony ref + Compile line. About.xml: brrainz.harmony dep.
- Patches/RM_Cauldron_AcidDamage.xml: AcidBurn + (guarded) RM_BloomAcid marked acid.
- Defs/StuffCategoryDefs/RM_VexxithPlate.xml; RM_Vexxith now Metallic + RM_VexxithPlate + immune extension.
- Defs/ThingDefs_Buildings/RM_VexxithDoor.xml: plate-only door. PROVISIONAL: cost 25, work 1200, HP 200.
- Settings: vexxithAcidImmunityEnabled, vexxithDoorEnabled (restart); screen now scrolls (maxOneColumn).
- validation.py: load.acid_wiring_shape, acid chain (vexxith_acid_proof w/ steel control, toggle_off),
  vexxithDoorEnabled roundtrip; selftest fake + 3 breaks; walk lines added.

## Deferred
- Filter vessels: need the Filter-Works (unbuilt; FlowWorks LiquidDef lane, BENCH rework).
- Vent-cap liners: need the gas-tap scaffold (unbuilt).
- Scab-scrapers: no ship-scab mechanic exists or is ruled (Scabweight declined) — owner question.

## Validation
winbuild OK (0 warn); validate_patch 0 errors (texPath warns = vanilla bundle paths); selftest 59/59, 54 breaks;
modcheck lint 0 FAIL. Live acid chain never run (UNPROVEN until a bridge pass).

## Art owed
RM_VexxithDoor mover + menu icon (placeholder: vanilla DoorSimple tinted). Only RM_Vexxith item art exists.
