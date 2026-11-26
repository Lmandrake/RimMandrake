# OILGAS_BUILDABILITY_EXCISE_FOUND_NOT_FORGED

Oil and helixien are found, never built. Owner adoption rulings in `design/Jawa/mods/required_mods.md`: Rimefeller
(2026-08-04, "place pre-built + strip buildability") and Vanilla Helixien Gas Expanded (2026-08-10, "not as an
infinite source"; the mandatory strip of the infinite pocket, and of the pump's buildability).

## spec
- Rimefeller's OilWell, DeepOilWell, OilStorage, CrudeCracker and RefineryLoadingBay, and VHGE_HelixienPump, are out
  of the build menu (empty designationCategory; all five Rimefeller works inherit it from an abstract parent).
- VHGE's infinite deposits (HelixienGasHandler.InitDeposits, 2 lumps per surface map plus mutators) are removed when a
  map is generated; finite deposits and geysers stay.
- Both in Jawa Doctrine (`mandrake.rut.doctrine`), each behind a Mod Setting, default on.

## verify
- `python3 src/RimUtinni/Doctrine/selftest_found_not_forged.py` (offline, the outcome check).
- `python.exe src/RimUtinni/Doctrine/live_found_not_forged.py ArchBig` on tier
  `mods__dubwise_rimefeller__vanillaexpanded_helixiengas__mandrake_rut_doctrine` (live, kind A).

## criteria
- The shaped part `found-not-forged offline` on the ledger.

## refs
file: src/RimUtinni/Doctrine/Patches/FoundNotForged.xml
file: src/RimUtinni/Doctrine/Source/DoctrineCore/DoctrineSettings.cs
def: ThingDef/VHGE_HelixienPump
def: ThingDef/OilWell
